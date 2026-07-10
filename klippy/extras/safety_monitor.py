# Safety monitoring for industrial servo drives
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class SafetyMonitor:
    """Monitor servo drive safety parameters.

    Monitors following error, velocity, and torque for configured
    servo steppers. Triggers configurable actions when limits are exceeded.

    Config format:
        [safety_monitor]
        deviation_threshold: 1.0
        deviation_action: shutdown
        max_velocity: 5000
        velocity_action: shutdown
        max_torque: 300
        torque_action: pause
        steppers: canopen_stepper stepper_x, canopen_stepper stepper_y
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.reactor = self.printer.get_reactor()

        # Following error configuration
        self.deviation_threshold = config.getfloat(
            "deviation_threshold", 0.0, minval=0.0
        )
        self.deviation_action = config.get("deviation_action", "shutdown")
        self.deviation_debounce = config.getfloat(
            "deviation_debounce", 0.05, minval=0.0
        )

        # Velocity configuration
        self.max_velocity = config.getfloat(
            "max_velocity", 0.0, minval=0.0
        )
        self.velocity_action = config.get("velocity_action", "shutdown")
        self.velocity_debounce = config.getfloat(
            "velocity_debounce", 0.05, minval=0.0
        )

        # Torque configuration
        self.max_torque = config.getfloat(
            "max_torque", 0.0, minval=0.0
        )
        self.torque_action = config.get("torque_action", "shutdown")
        self.torque_debounce = config.getfloat(
            "torque_debounce", 0.1, minval=0.0
        )

        # Validate actions
        valid_actions = ("shutdown", "pause", "gcode", "none")
        for action_name, action_val in [
            ("deviation_action", self.deviation_action),
            ("velocity_action", self.velocity_action),
            ("torque_action", self.torque_action),
        ]:
            if action_val not in valid_actions:
                raise config.error(
                    "Invalid %s '%s' in [%s]. Options: %s"
                    % (
                        action_name,
                        action_val,
                        self.name,
                        ", ".join(valid_actions),
                    )
                )

        # Parse steppers list
        stepper_names = config.get("steppers", "")
        self._stepper_names = [
            s.strip() for s in stepper_names.split(",") if s.strip()
        ]
        self._steppers = {}

        # Alarm state tracking
        self._deviation_alarm = False
        self._velocity_alarm = False
        self._torque_alarm = False
        self._deviation_value = 0.0
        self._velocity_value = 0.0
        self._torque_value = 0.0

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_SAFETY_STATUS",
            self.cmd_QUERY_SAFETY_STATUS,
            desc="Query safety monitor status",
        )
        gcode.register_command(
            "SET_SAFETY_LIMIT",
            self.cmd_SET_SAFETY_LIMIT,
            desc="Set safety monitoring limits",
        )

        # Register ready event to lookup steppers
        self.printer.register_event_handler(
            "klippy:ready", self._handle_ready
        )

        logging.info(
            "SafetyMonitor '%s': deviation=%.1f, velocity=%.1f, torque=%.1f",
            self.name,
            self.deviation_threshold,
            self.max_velocity,
            self.max_torque,
        )

    def _handle_ready(self):
        """Lookup stepper objects after all modules are loaded."""
        for name in self._stepper_names:
            try:
                obj = self.printer.lookup_object(name)
                self._steppers[name] = obj
                logging.info(
                    "SafetyMonitor '%s': monitoring stepper '%s'",
                    self.name,
                    name,
                )
            except Exception:
                logging.error(
                    "SafetyMonitor '%s': stepper '%s' not found",
                    self.name,
                    name,
                )

        # Start periodic monitoring if steppers found
        if self._steppers and (
            self.deviation_threshold > 0
            or self.max_velocity > 0
            or self.max_torque > 0
        ):
            self.reactor.register_timer(
                self._check_safety, self.reactor.monotonic() + 1.0
            )

    def _check_safety(self, eventtime):
        """Periodic safety check callback."""
        for stepper_name, stepper_obj in self._steppers.items():
            try:
                status = stepper_obj.get_status()
            except Exception:
                continue

            # Check following error
            if self.deviation_threshold > 0:
                deviation = abs(status.get("following_error", 0))
                self._deviation_value = deviation
                if deviation > self.deviation_threshold:
                    if not self._deviation_alarm:
                        self._deviation_alarm = True
                        logging.error(
                            "SafetyMonitor: Following error exceeded on %s "
                            "(%.1f > %.1f)",
                            stepper_name,
                            deviation,
                            self.deviation_threshold,
                        )
                        self._trigger_alarm(
                            "deviation", stepper_name, deviation
                        )
                else:
                    self._deviation_alarm = False

            # Check velocity
            if self.max_velocity > 0:
                velocity = abs(status.get("actual_velocity", 0))
                self._velocity_value = velocity
                if velocity > self.max_velocity:
                    if not self._velocity_alarm:
                        self._velocity_alarm = True
                        logging.error(
                            "SafetyMonitor: Velocity exceeded on %s "
                            "(%.1f > %.1f)",
                            stepper_name,
                            velocity,
                            self.max_velocity,
                        )
                        self._trigger_alarm(
                            "velocity", stepper_name, velocity
                        )
                else:
                    self._velocity_alarm = False

            # Check torque
            if self.max_torque > 0:
                torque = abs(status.get("actual_torque", 0))
                self._torque_value = torque
                if torque > self.max_torque:
                    if not self._torque_alarm:
                        self._torque_alarm = True
                        logging.error(
                            "SafetyMonitor: Torque exceeded on %s "
                            "(%.1f > %.1f)",
                            stepper_name,
                            torque,
                            self.max_torque,
                        )
                        self._trigger_alarm(
                            "torque", stepper_name, torque
                        )
                else:
                    self._torque_alarm = False

        return eventtime + 0.1  # 100ms check period

    def _trigger_alarm(self, alarm_type, stepper_name, value):
        """Trigger alarm action."""
        # Determine action
        if alarm_type == "deviation":
            action = self.deviation_action
        elif alarm_type == "velocity":
            action = self.velocity_action
        else:
            action = self.torque_action

        # Fire event for alarm_history
        try:
            self.printer.send_event(
                "safety_monitor:alarm",
                self.name,
                alarm_type,
                {
                    "stepper": stepper_name,
                    "value": value,
                    "action": action,
                },
            )
        except Exception:
            pass

        # Execute action
        if action == "shutdown":
            self.printer.invoke_shutdown(
                "Safety limit exceeded: %s on %s (%.1f)"
                % (alarm_type, stepper_name, value)
            )
        elif action == "pause":
            try:
                print_stats = self.printer.lookup_object("print_stats")
                if print_stats.get_status()["state"] == "printing":
                    gcode = self.printer.lookup_object("gcode")
                    gcode.run_script_from_command("PAUSE")
                    logging.info(
                        "SafetyMonitor: print paused due to %s", alarm_type
                    )
            except Exception as e:
                logging.error(
                    "SafetyMonitor: pause failed: %s", e
                )
                self.printer.invoke_shutdown(
                    "Safety limit exceeded: %s on %s (pause failed)"
                    % (alarm_type, stepper_name)
                )

    def get_status(self, eventtime=None):
        """Return safety monitor status."""
        return {
            "deviation_alarm": self._deviation_alarm,
            "deviation_value": self._deviation_value,
            "deviation_threshold": self.deviation_threshold,
            "velocity_alarm": self._velocity_alarm,
            "velocity_value": self._velocity_value,
            "velocity_threshold": self.max_velocity,
            "torque_alarm": self._torque_alarm,
            "torque_value": self._torque_value,
            "torque_threshold": self.max_torque,
            "monitored_steppers": list(self._stepper_names),
        }

    def cmd_QUERY_SAFETY_STATUS(self, gcmd):
        """Query safety monitor status."""
        status = self.get_status()
        lines = [
            "Safety Monitor '%s':" % self.name,
            "  Following Error: %s (threshold=%.1f, current=%.1f)"
            % (
                "ALARM" if status["deviation_alarm"] else "OK",
                status["deviation_threshold"],
                status["deviation_value"],
            ),
            "  Velocity: %s (threshold=%.1f, current=%.1f)"
            % (
                "ALARM" if status["velocity_alarm"] else "OK",
                status["velocity_threshold"],
                status["velocity_value"],
            ),
            "  Torque: %s (threshold=%.1f, current=%.1f)"
            % (
                "ALARM" if status["torque_alarm"] else "OK",
                status["torque_threshold"],
                status["torque_value"],
            ),
            "  Monitored steppers: %s"
            % ", ".join(status["monitored_steppers"]),
        ]
        gcmd.respond_info("\n".join(lines))

    def cmd_SET_SAFETY_LIMIT(self, gcmd):
        """Set safety monitoring limits at runtime."""
        changed = False
        if "DEVIATION" in gcmd.get_command_parameters():
            self.deviation_threshold = gcmd.get_float(
                "DEVIATION", self.deviation_threshold, minval=0.0
            )
            changed = True
        if "VELOCITY" in gcmd.get_command_parameters():
            self.max_velocity = gcmd.get_float(
                "VELOCITY", self.max_velocity, minval=0.0
            )
            changed = True
        if "TORQUE" in gcmd.get_command_parameters():
            self.max_torque = gcmd.get_float(
                "TORQUE", self.max_torque, minval=0.0
            )
            changed = True

        if changed:
            gcmd.respond_info(
                "Safety limits updated: deviation=%.1f, velocity=%.1f, "
                "torque=%.1f"
                % (
                    self.deviation_threshold,
                    self.max_velocity,
                    self.max_torque,
                )
            )
        else:
            gcmd.respond_info(
                "Usage: SET_SAFETY_LIMIT [DEVIATION=<val>] "
                "[VELOCITY=<val>] [TORQUE=<val>]"
            )


def load_config(config):
    """Load [safety_monitor] config section."""
    return SafetyMonitor(config)
