# Closed-loop position control using encoder feedback
#
# Copyright (C) 2024-2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import math

# Kinematics where each stepper drives exactly one cartesian axis.  For
# those the position error reported by an encoder maps directly onto a
# single cartesian axis and the correction can be applied unambiguously.
# Other kinematics are monitored only.
SUPPORTED_KINEMATICS = ["cartesian"]

# Sliding window used to rate limit the applied corrections (seconds)
RATE_WINDOW = 1.0

# The step time solver emits the additional steps of a corrected segment
# all at the start of that segment.  The step compressor is not able to
# deliver steps that are closer together than its timing error tolerance,
# so the re-anchor of a stepper reference must stay small.  Two steps is
# the largest value that the Klipper step compressor accepts - see
# test/closed_loop/test_reanchor.c
DEFAULT_MAX_REANCHOR_STEPS = 2


class ClosedLoop:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.enabled = config.getboolean("enable", False)
        self.enable_correction = config.getboolean("enable_correction", False)
        self.action = config.getchoice(
            "action", ["log", "pause", "shutdown"], "shutdown")
        # PID gains.  "pid_kp" is dimensionless, "pid_ki" has units of
        # 1/second and "pid_kd" has units of seconds.  The controller
        # output is a position correction in millimeters.
        self.kp = config.getfloat("pid_kp", 0.5, above=0.0)
        self.ki = config.getfloat("pid_ki", 0.0, minval=0.0)
        self.kd = config.getfloat("pid_kd", 0.0, minval=0.0)
        # Maximum correction applied on a single update (mm)
        self.max_correction = config.getfloat("max_correction", 0.05,
                                              above=0.0)
        # Maximum total correction applied per second (mm/s), 0 disables
        self.max_correction_rate = config.getfloat("max_correction_rate", 2.0,
                                                   minval=0.0)
        # Maximum re-anchor of a stepper reference (in steps).  This is a
        # hard limit imposed by the step compressor - see the comment on
        # DEFAULT_MAX_REANCHOR_STEPS
        self.max_reanchor_steps = config.getint(
            "max_reanchor_steps", DEFAULT_MAX_REANCHOR_STEPS, minval=1,
            maxval=64)
        # Update interval of the controller (seconds)
        self.correction_interval = config.getfloat("correction_interval",
                                                   0.020, above=0.0)
        # Position error below this value is considered in tolerance (mm)
        self.error_threshold = config.getfloat("error_threshold", 0.05,
                                               above=0.0)
        # Maximum age of an encoder sample that is still used (seconds)
        self.max_sample_age = config.getfloat("max_sample_age", 0.250,
                                              above=0.0)
        self.encoders = {}
        self._zero_offset = {}
        self._integral = {}
        self._last_error = {}
        self._prev_error = {}
        self._last_correction = {}
        self._pending = {}
        self._sample_time = {}
        self._sample_age = {}
        self._rate_window = {}
        self._tripped = {}
        # Accumulated re-anchor of each axis.  The step count of a stepper
        # includes the extra steps that were injected by a correction, so
        # the accumulated lead has to be subtracted to recover the
        # position that the machine was commanded to.
        self._lead = {}
        self._correction_timer = None
        self._pre_step_gen_cb = None
        self._kinematics_supported = None
        self._last_update_time = 0.0

        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("CLOSED_LOOP_ENABLE",
                               self.cmd_CLOSED_LOOP_ENABLE,
                               desc=self.cmd_CLOSED_LOOP_ENABLE_help)
        gcode.register_command("CLOSED_LOOP_DISABLE",
                               self.cmd_CLOSED_LOOP_DISABLE,
                               desc=self.cmd_CLOSED_LOOP_DISABLE_help)
        gcode.register_command("CLOSED_LOOP_STATUS",
                               self.cmd_CLOSED_LOOP_STATUS,
                               desc=self.cmd_CLOSED_LOOP_STATUS_help)
        gcode.register_command("CLOSED_LOOP_CALIBRATE",
                               self.cmd_CLOSED_LOOP_CALIBRATE,
                               desc=self.cmd_CLOSED_LOOP_CALIBRATE_help)

        self.printer.register_event_handler("klippy:ready",
                                            self._handle_ready)
        # A homing move resets the stepper references and therefore
        # invalidates the encoder zero offsets, the accumulated lead and
        # the PID state
        self.printer.register_event_handler("toolhead:set_position",
                                            self._handle_set_position)

    cmd_CLOSED_LOOP_ENABLE_help = "Enable closed-loop control"
    cmd_CLOSED_LOOP_DISABLE_help = "Disable closed-loop control"
    cmd_CLOSED_LOOP_STATUS_help = "Report closed-loop status"
    cmd_CLOSED_LOOP_CALIBRATE_help = ("Calibrate encoder zero position to "
                                      "stepper position")

    def register_encoder(self, encoder):
        self.encoders[encoder.name] = encoder
        # The encoder may register itself before or after the "klippy:ready"
        # event is dispatched - make sure the controller is set up either way
        self._setup()

    def _setup(self):
        # Register the step generation callback and start the controller
        if self._pre_step_gen_cb is None:
            toolhead = self.printer.lookup_object("toolhead")
            self._pre_step_gen_cb = self._pre_step_gen_callback
            toolhead.register_pre_step_gen_callback(self._pre_step_gen_cb)
        if self.encoders and self.enabled:
            self._start_correction_timer()

    def _handle_ready(self):
        self._kinematics_supported = self._check_kinematics()
        self._setup()

    def _handle_set_position(self):
        # The stepper references have been re-based - drop any pending
        # correction and reset the controller state
        self._pending = {}
        self._integral = {}
        self._last_error = {}
        self._prev_error = {}
        self._lead = {}

    def _check_kinematics(self):
        try:
            scfg = self.printer.lookup_object("configfile")
            psection = scfg.getsection("printer")
            kin_name = psection.get("kinematics")
        except Exception:
            return False
        if kin_name in SUPPORTED_KINEMATICS:
            return True
        logging.warning(
            "Closed-loop: kinematics '%s' is not supported for position"
            " correction - monitoring only", kin_name)
        return False

    def _start_correction_timer(self):
        if self._correction_timer is None:
            self._correction_timer = self.reactor.register_timer(
                self._correction_callback)
            self.reactor.update_timer(
                self._correction_timer,
                self.reactor.monotonic() + self.correction_interval)

    def _stop_correction_timer(self):
        if self._correction_timer is not None:
            self.reactor.unregister_timer(self._correction_timer)
            self._correction_timer = None

    def _correction_callback(self, eventtime):
        try:
            self._update_corrections(eventtime)
        except self.printer.command_error:
            logging.exception("Closed-loop correction error")
        except Exception:
            logging.exception("Unexpected closed-loop error")
        return eventtime + self.correction_interval

    # Error evaluation
    def _get_print_time(self, encoder):
        # The "current" print time in the same time base as the encoder
        # samples.  The encoder timestamps are derived from its own mcu
        # clock, so use that mcu to avoid mixing time bases.
        systime = self.reactor.monotonic()
        return encoder.mcu.estimated_print_time(systime)

    def _calc_commanded_position(self, ptime):
        # Return the commanded cartesian position at the given print time.
        # The stepper positions are recovered from the step time history so
        # that the measurement is compared against the position the machine
        # was actually commanded to be at when the sample was taken.
        toolhead = self.printer.lookup_object("toolhead")
        kin = toolhead.get_kinematics()
        kin_spos = {}
        for s in kin.get_steppers():
            mcu_pos = s.get_past_mcu_position(ptime)
            kin_spos[s.get_name()] = s.mcu_to_commanded_position(mcu_pos)
        return kin.calc_position(kin_spos)

    def _calc_error(self, encoder, now_ptime):
        sample = encoder.get_latest_sample()
        if sample is None:
            return None
        ptime, raw_pos = sample
        age = now_ptime - ptime
        if age < 0. or age > self.max_sample_age:
            return None
        axis_idx = encoder.get_axis_index()
        if axis_idx is None:
            return None
        cpos = self._calc_commanded_position(ptime)
        if cpos is None:
            return None
        # The step count includes the extra steps that a correction
        # injected - remove them to obtain the commanded position
        lead = self._lead.get(encoder.name, 0.0)
        expected = cpos[axis_idx] - lead
        actual = encoder.get_sample_mm(sample) + self._zero_offset.get(
            encoder.name, 0.0)
        return expected - actual, ptime, age

    def _update_corrections(self, eventtime):
        if not self.enabled:
            return
        dt = self.correction_interval
        now_ptime = 0.0
        for name, encoder in self.encoders.items():
            stepper = encoder.get_stepper()
            if stepper is None:
                continue
            now_ptime = self._get_print_time(encoder)
            if self._last_update_time:
                dt = max(1e-3, now_ptime - self._last_update_time)
            res = self._calc_error(encoder, now_ptime)
            if res is None:
                continue
            error, ptime, age = res
            self._last_error[name] = error
            self._sample_time[name] = ptime
            self._sample_age[name] = age
            if abs(error) > self.error_threshold:
                self._handle_error(name, error)
            else:
                self._tripped.pop(name, None)
            if not self.enable_correction:
                continue
            if name not in self._zero_offset:
                # Not calibrated yet - the error would be meaningless
                continue
            if not self._kinematics_supported:
                continue
            corr = self._calc_pid(name, error, dt)
            corr = self._limit_correction(name, corr, stepper)
            if abs(corr) < 1e-6:
                continue
            self._last_correction[name] = corr
            axis_idx = encoder.get_axis_index()
            delta = [0.0, 0.0, 0.0]
            delta[axis_idx] = corr
            self._pending[name] = delta
        if now_ptime:
            self._last_update_time = now_ptime

    def _calc_pid(self, name, error, dt):
        prev_error = self._prev_error.get(name)
        if prev_error is None:
            deriv = 0.0
        else:
            deriv = (error - prev_error) / dt
        self._prev_error[name] = error
        integral = self._integral.get(name, 0.0) + error * dt
        if self.ki:
            # Clamp the integral to avoid windup
            ilimit = self.max_correction / self.ki
            integral = max(-ilimit, min(ilimit, integral))
        self._integral[name] = integral
        corr = self.kp * error + self.ki * integral + self.kd * deriv
        return max(-self.max_correction, min(self.max_correction, corr))

    def _limit_correction(self, name, corr, stepper):
        # The correction is limited by the user setting, by the rate limit
        # and by the number of steps that the step compressor is able to
        # deliver in a single re-anchor
        if abs(corr) > self.max_correction:
            corr = math.copysign(self.max_correction, corr)
        max_delta = self.max_reanchor_steps * stepper.get_step_dist()
        if abs(corr) > max_delta:
            corr = math.copysign(max_delta, corr)
        if self.max_correction_rate:
            window = self._rate_window.setdefault(name, [])
            now = self.reactor.monotonic()
            window[:] = [w for w in window if now - w[0] < RATE_WINDOW]
            used = sum(abs(w[1]) for w in window)
            room = self.max_correction_rate * RATE_WINDOW - used
            if room <= 0.:
                return 0.0
            if abs(corr) > room:
                corr = math.copysign(room, corr)
            window.append((now, corr))
        return corr

    # Correction application
    def _pre_step_gen_callback(self, flush_time):
        # Apply any pending corrections before the steppers generate their
        # steps.  The step time solver reads the stepper reference once at
        # the start of a segment, so lowering the reference here makes the
        # stepper travel an additional distance without disturbing the
        # planned trajectory or the lookahead queue.
        if not self._pending:
            return
        pending = self._pending
        self._pending = {}
        if not self.enable_correction or not self._kinematics_supported:
            return
        toolhead = self.printer.lookup_object("toolhead")
        kin = toolhead.get_kinematics()
        cur = toolhead.get_position()
        for name, delta in pending.items():
            encoder = self.encoders.get(name)
            if encoder is None or encoder.get_stepper() is None:
                continue
            axis_idx = encoder.get_axis_index()
            newpos = [cur[0] + delta[0], cur[1] + delta[1], cur[2] + delta[2]]
            for s in kin.get_steppers():
                d_new = s.calc_position_from_coord(newpos)
                d_old = s.calc_position_from_coord(cur)
                ds = d_new - d_old
                if not ds:
                    continue
                s.set_commanded_pos(s.get_commanded_position() - ds)
            # Remember how much the axis was advanced so that the
            # commanded position can be recovered from the step count
            self._lead[name] = self._lead.get(name, 0.0) + delta[axis_idx]

    # Error handling
    def _handle_error(self, name, error):
        if self._tripped.get(name):
            return
        self._tripped[name] = True
        msg = ("Closed-loop position error on '%s': %.4fmm" % (name, error))
        if self.action == "shutdown":
            logging.error(msg)
            self.printer.invoke_shutdown(msg)
        elif self.action == "pause":
            logging.error(msg)
            pr = self.printer.lookup_object("pause_resume", None)
            if pr is not None:
                pr.send_pause_command()
            else:
                logging.error("Closed-loop: unable to pause")
        else:
            logging.error(msg)

    # Commands
    def cmd_CLOSED_LOOP_ENABLE(self, gcmd):
        self.enabled = True
        if self.encoders:
            self._start_correction_timer()
        gcmd.respond_info("Closed-loop control enabled")

    def cmd_CLOSED_LOOP_DISABLE(self, gcmd):
        self.enabled = False
        self._stop_correction_timer()
        self._pending = {}
        gcmd.respond_info("Closed-loop control disabled")

    def cmd_CLOSED_LOOP_STATUS(self, gcmd):
        if not self.encoders:
            gcmd.respond_info("No encoders registered for closed-loop")
            return
        status_lines = ["Closed-loop status:"]
        for name, encoder in self.encoders.items():
            stepper = encoder.get_stepper()
            if stepper is None:
                status_lines.append("  %s: (no stepper)" % (name,))
                continue
            error = self._last_error.get(name)
            corr = self._last_correction.get(name)
            age = self._sample_age.get(name)
            status_lines.append(
                "  %s: error=%s correction=%s sample_age=%s"
                % (name,
                   "%.4fmm" % (error,) if error is not None else "n/a",
                   "%.4fmm" % (corr,) if corr is not None else "n/a",
                   "%.3fs" % (age,) if age is not None else "n/a"))
            status_lines.append(
                "    lead=%.4fmm calibrated=%s"
                % (self._lead.get(name, 0.0),
                   name in self._zero_offset))
        status_lines.append("  enabled: %s" % (self.enabled,))
        status_lines.append("  correction_active: %s"
                            % (self.enable_correction,))
        status_lines.append("  correction_supported: %s"
                            % (self._kinematics_supported,))
        status_lines.append("  action: %s" % (self.action,))
        status_lines.append("  kp=%.4f ki=%.4f kd=%.4f"
                            % (self.kp, self.ki, self.kd))
        status_lines.append("  max_correction=%.4f max_rate=%.4f"
                            % (self.max_correction, self.max_correction_rate))
        status_lines.append("  max_reanchor_steps=%d" % (self.max_reanchor_steps,))
        gcmd.respond_info("\n".join(status_lines))

    def cmd_CLOSED_LOOP_CALIBRATE(self, gcmd):
        axis = gcmd.get("AXIS", None)
        if axis is None:
            gcmd.respond_info(
                "Usage: CLOSED_LOOP_CALIBRATE AXIS=<encoder_name>")
            return
        if axis not in self.encoders:
            gcmd.respond_info("Unknown encoder '%s'" % (axis,))
            return
        encoder = self.encoders[axis]
        stepper = encoder.get_stepper()
        if stepper is None:
            gcmd.respond_info(
                "Encoder '%s' has no associated stepper" % (axis,))
            return
        sample = encoder.get_latest_sample()
        if sample is None:
            gcmd.respond_info(
                "Encoder '%s' has no measurement available yet" % (axis,))
            return
        try:
            ptime = sample[0]
            cpos = self._calc_commanded_position(ptime)
            axis_idx = encoder.get_axis_index()
            if cpos is None or axis_idx is None:
                raise gcmd.error("Unable to determine the expected position")
            lead = self._lead.get(axis, 0.0)
            travel = encoder.get_sample_mm(sample)
            self._zero_offset[axis] = (cpos[axis_idx] - lead) - travel
            self._last_error[axis] = 0.0
            self._integral[axis] = 0.0
            self._tripped.pop(axis, None)
            gcmd.respond_info(
                "Encoder '%s' calibrated: offset=%.4fmm"
                % (axis, self._zero_offset[axis]))
        except Exception:
            logging.exception("Calibration failed for '%s'", axis)
            raise gcmd.error("Calibration failed")

    def get_status(self, eventtime=None):
        st = {"enabled": self.enabled,
              "correction_active": self.enable_correction,
              "correction_supported": bool(self._kinematics_supported),
              "action": self.action}
        for name, encoder in self.encoders.items():
            st[name] = encoder.get_status(eventtime)
            if name in self._zero_offset:
                st[name]["zero_offset"] = self._zero_offset[name]
            if name in self._last_error:
                st[name]["error"] = self._last_error[name]
            if name in self._last_correction:
                st[name]["correction"] = self._last_correction[name]
            if name in self._sample_age:
                st[name]["sample_age"] = self._sample_age[name]
            if name in self._lead:
                st[name]["lead"] = self._lead[name]
        return st


def load_config(config):
    return ClosedLoop(config)
