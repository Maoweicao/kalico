# Closed-loop position control using encoder feedback
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class ClosedLoop:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.enabled = config.getboolean("enable", False)
        self.enable_correction = config.getboolean(
            "enable_correction", False)
        self.kp = config.getfloat("pid_kp", 0.5, above=0.0)
        self.ki = config.getfloat("pid_ki", 0.0, minval=0.0)
        self.kd = config.getfloat("pid_kd", 0.0, minval=0.0)
        self.max_correction = config.getfloat(
            "max_correction", 1.0, above=0.0)
        self.correction_interval = config.getfloat(
            "correction_interval", 0.050, above=0.0)
        self.error_threshold = config.getfloat(
            "error_threshold", 0.5, above=0.0)
        self.encoders = {}
        self._correction_timer = None
        self._last_error = {}
        self._integral = {}
        self._zero_offset = {}
        self._correction_history = {}

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

    cmd_CLOSED_LOOP_ENABLE_help = "Enable closed-loop control"
    cmd_CLOSED_LOOP_DISABLE_help = "Disable closed-loop control"
    cmd_CLOSED_LOOP_STATUS_help = "Report closed-loop status"
    cmd_CLOSED_LOOP_CALIBRATE_help = ("Calibrate encoder zero position to "
                                      "stepper position")

    def register_encoder(self, encoder):
        self.encoders[encoder.name] = encoder

    def _handle_ready(self):
        if self.encoders and self.enabled:
            self._start_correction_timer()

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
            self._apply_corrections(eventtime)
        except self.printer.command_error:
            logging.exception("Closed-loop correction error")
        except Exception:
            logging.exception("Unexpected closed-loop error")
        return eventtime + self.correction_interval

    def _apply_corrections(self, eventtime):
        if not self.enabled:
            return
        for name, encoder in self.encoders.items():
            stepper = encoder.get_stepper()
            if stepper is None:
                continue
            encoder_pos = encoder.get_position_mm()
            offset = self._zero_offset.get(name, 0.0)
            actual_pos = encoder_pos + offset
            stepper_pos = stepper.get_commanded_position()
            if stepper_pos is None:
                continue
            error = stepper_pos - actual_pos

            if abs(error) > self.error_threshold:
                self._trigger_error(name, error)

            if name in self._last_error:
                derivative = (error - self._last_error[name]) / max(
                    self.correction_interval, 0.001)
            else:
                derivative = 0.0
            self._last_error[name] = error

            if name in self._integral:
                self._integral[name] += error * self.correction_interval
            else:
                self._integral[name] = 0.0

            correction = (self.kp * error + self.ki * self._integral[name]
                          + self.kd * derivative)
            correction = max(-self.max_correction,
                             min(self.max_correction, correction))

            self._correction_history[name] = {
                "error": error, "correction": correction}

            if self.enable_correction and abs(correction) > 0.0001:
                self._apply_step_correction(name, encoder, stepper,
                                            correction)

    def _apply_step_correction(self, name, encoder, stepper, correction):
        try:
            toolhead = self.printer.lookup_object("toolhead")
            toolhead.flush_step_generation()
            current_pos = stepper.get_commanded_position()
            sname = stepper.get_name()
            coord = [0.0, 0.0, 0.0]
            if "stepper_x" in sname:
                coord[0] = current_pos + correction
            elif "stepper_y" in sname:
                coord[1] = current_pos + correction
            elif "stepper_z" in sname:
                coord[2] = current_pos + correction
            else:
                coord[0] = current_pos + correction
            stepper.set_position(tuple(coord))
        except Exception:
            logging.exception("Failed to apply correction on '%s'", name)

    def _trigger_error(self, axis, error):
        msg = ("Closed-loop position error on '%s': %.4fmm"
               % (axis, error))
        logging.error(msg)

    def cmd_CLOSED_LOOP_ENABLE(self, gcmd):
        self.enabled = True
        if self.encoders:
            self._start_correction_timer()
        gcmd.respond_info("Closed-loop control enabled")

    def cmd_CLOSED_LOOP_DISABLE(self, gcmd):
        self.enabled = False
        self._stop_correction_timer()
        gcmd.respond_info("Closed-loop control disabled")

    def cmd_CLOSED_LOOP_STATUS(self, gcmd):
        if not self.encoders:
            gcmd.respond_info("No encoders registered for closed-loop")
            return
        status_lines = ["Closed-loop status:"]
        for name, encoder in self.encoders.items():
            pos_mm = encoder.get_position_mm()
            offset = self._zero_offset.get(name, 0.0)
            actual_pos = pos_mm + offset
            stepper = encoder.get_stepper()
            if stepper is not None:
                cmd_pos = stepper.get_commanded_position()
                error = cmd_pos - actual_pos
                status_lines.append(
                    "  %s: pos=%.4fmm stepper=%.4fmm error=%.4fmm"
                    % (name, actual_pos, cmd_pos, error))
            else:
                status_lines.append(
                    "  %s: pos=%.4fmm (no stepper)" % (name, actual_pos))
        if self._correction_history:
            for name, hist in self._correction_history.items():
                status_lines.append(
                    "  %s: PID error=%.4f correction=%.4f"
                    % (name, hist["error"], hist["correction"]))
        status_lines.append("  enabled: %s" % (self.enabled,))
        status_lines.append("  correction_active: %s"
                            % (self.enable_correction,))
        status_lines.append("  kp=%.4f ki=%.4f kd=%.4f"
                            % (self.kp, self.ki, self.kd))
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
        try:
            encoder_pos = encoder.get_position_mm()
            stepper_pos = stepper.get_commanded_position()
            self._zero_offset[axis] = stepper_pos - encoder_pos
            self._last_error[axis] = 0.0
            self._integral[axis] = 0.0
            gcmd.respond_info(
                "Encoder '%s' calibrated: offset=%.4fmm"
                % (axis, self._zero_offset[axis]))
        except Exception:
            logging.exception("Calibration failed for '%s'", axis)
            raise gcmd.error("Calibration failed")

    def get_status(self, eventtime=None):
        st = {"enabled": self.enabled,
              "correction_active": self.enable_correction}
        for name, encoder in self.encoders.items():
            st[name] = encoder.get_status(eventtime)
            if name in self._zero_offset:
                st[name]["zero_offset"] = self._zero_offset[name]
            if name in self._correction_history:
                st[name].update(self._correction_history[name])
        return st


def load_config(config):
    return ClosedLoop(config)
