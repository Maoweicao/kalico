# Servo status G-code commands for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

SERVO_STEPPER_TYPES = (
    "canopen_stepper",
    "ethercat_stepper",
    "rs485_stepper",
)


class ServoStatus:
    """G-code commands for querying and managing servo drive status.

    Commands:
        QUERY_SERVO [STEPPER=<name>]     - Query servo drive status
        RESET_SERVO_FAULT STEPPER=<name> - Reset servo drive fault
        QUERY_SERVO_ALARM                - Query all alarm states
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_SERVO", self.cmd_QUERY_SERVO,
            desc="Query servo drive status"
        )
        gcode.register_command(
            "RESET_SERVO_FAULT", self.cmd_RESET_SERVO_FAULT,
            desc="Reset servo drive fault"
        )
        gcode.register_command(
            "QUERY_SERVO_ALARM", self.cmd_QUERY_SERVO_ALARM,
            desc="Query all servo alarm states"
        )
        gcode.register_command(
            "QUERY_ALL_SAFETY", self.cmd_QUERY_ALL_SAFETY,
            desc="Query all safety status"
        )

    def _find_servo_steppers(self):
        """Find all servo stepper objects."""
        steppers = []
        for name, obj in self.printer.lookup_objects():
            prefix = name.split()[0] if " " in name else name
            if prefix in SERVO_STEPPER_TYPES:
                steppers.append((name, obj))
        return steppers

    def _find_servo_alarms(self):
        """Find all servo alarm objects."""
        alarms = []
        for name, obj in self.printer.lookup_objects():
            prefix = name.split()[0] if " " in name else name
            if prefix == "servo_alarm":
                alarms.append((name, obj))
        return alarms

    def cmd_QUERY_SERVO(self, gcmd):
        """Query servo drive status.

        Usage:
            QUERY_SERVO                         # Query all servos
            QUERY_SERVO STEPPER=stepper_x       # Query specific servo
        """
        stepper_name = gcmd.get("STEPPER", None)

        if stepper_name:
            # Query specific stepper
            try:
                obj = self.printer.lookup_object(stepper_name)
            except Exception:
                gcmd.respond_info("Unknown stepper: %s" % stepper_name)
                return

            if not hasattr(obj, "get_status"):
                gcmd.respond_info(
                    "Stepper '%s' does not support status queries"
                    % stepper_name
                )
                return

            status = obj.get_status()
            self._respond_stepper_status(gcmd, stepper_name, status)
        else:
            # Query all servo steppers
            steppers = self._find_servo_steppers()
            if not steppers:
                gcmd.respond_info("No servo steppers configured")
                return

            for name, obj in steppers:
                if hasattr(obj, "get_status"):
                    status = obj.get_status()
                    self._respond_stepper_status(gcmd, name, status)

    def _respond_stepper_status(self, gcmd, name, status):
        """Format and respond with stepper status."""
        state = status.get("state", "unknown")
        error = status.get("error_code", 0)
        mode = status.get("mode", "N/A")
        is_fault = status.get("is_fault", False)
        alarm = status.get("alarm_active", False)

        parts = ["%s:" % name]
        parts.append("  state=%s" % state)
        if mode != "N/A":
            parts.append("  mode=%s" % mode)
        if error:
            parts.append("  error_code=0x%04X" % error)
        if is_fault:
            parts.append("  **FAULT**")
        if alarm:
            parts.append("  **ALARM**")

        gcmd.respond_info("\n".join(parts))

    def cmd_RESET_SERVO_FAULT(self, gcmd):
        """Reset servo drive fault.

        Usage:
            RESET_SERVO_FAULT STEPPER=stepper_x
        """
        stepper_name = gcmd.get("STEPPER")
        if not stepper_name:
            gcmd.respond_info("Usage: RESET_SERVO_FAULT STEPPER=<name>")
            return

        try:
            obj = self.printer.lookup_object(stepper_name)
        except Exception:
            gcmd.respond_info("Unknown stepper: %s" % stepper_name)
            return

        # Try different fault reset methods
        reset_done = False

        # Method 1: CiA402Device.fault_reset()
        if hasattr(obj, "backend"):
            backend = obj.backend
            if hasattr(backend, "_device"):
                device = backend._device
                if hasattr(device, "fault_reset"):
                    try:
                        device.fault_reset()
                        gcmd.respond_info(
                            "Fault reset on %s: OK" % stepper_name
                        )
                        reset_done = True
                    except Exception as e:
                        gcmd.respond_info(
                            "Fault reset on %s failed: %s"
                            % (stepper_name, e)
                        )

        # Method 2: Protocol-level fault_reset (RS485/Leadshine)
        if not reset_done and hasattr(obj, "backend"):
            backend = obj.backend
            if hasattr(backend, "_protocol"):
                protocol = backend._protocol
                if hasattr(protocol, "fault_reset"):
                    try:
                        protocol.fault_reset()
                        gcmd.respond_info(
                            "Fault reset on %s: OK" % stepper_name
                        )
                        reset_done = True
                    except Exception as e:
                        gcmd.respond_info(
                            "Fault reset on %s failed: %s"
                            % (stepper_name, e)
                        )

        if not reset_done:
            gcmd.respond_info(
                "Stepper '%s' does not support fault reset"
                % stepper_name
            )

    def cmd_QUERY_SERVO_ALARM(self, gcmd):
        """Query all servo alarm states.

        Usage:
            QUERY_SERVO_ALARM
        """
        alarms = self._find_servo_alarms()
        if not alarms:
            gcmd.respond_info("No servo alarms configured")
            return

        for name, obj in alarms:
            status = obj.get_status()
            active = status.get("alarm_active", False)
            count = status.get("alarm_count", 0)
            pin = status.get("pin", "N/A")

            if active:
                gcmd.respond_info(
                    "%s: ALARM ACTIVE (pin=%s, count=%d)"
                    % (name, pin, count)
                )
            else:
                gcmd.respond_info(
                    "%s: OK (pin=%s, count=%d)" % (name, pin, count)
                )

    def cmd_QUERY_ALL_SAFETY(self, gcmd):
        """Query all safety-related status in one command.

        Usage:
            QUERY_ALL_SAFETY
        """
        lines = ["=== Safety Status Summary ===", ""]

        # Servo steppers
        steppers = self._find_servo_steppers()
        if steppers:
            lines.append("Servo Steppers:")
            for name, obj in steppers:
                if hasattr(obj, "get_status"):
                    status = obj.get_status()
                    state = status.get("state", "unknown")
                    is_fault = status.get("is_fault", False)
                    alarm = status.get("alarm_active", False)
                    deviation = status.get("following_error", 0)
                    flags = []
                    if is_fault:
                        flags.append("FAULT")
                    if alarm:
                        flags.append("ALARM")
                    flag_str = " [%s]" % ",".join(flags) if flags else ""
                    lines.append(
                        "  %s: %s%s (deviation=%.1f)"
                        % (name, state, flag_str, deviation)
                    )
            lines.append("")

        # Safety monitor
        try:
            safety = self.printer.lookup_object("safety_monitor")
            status = safety.get_status()
            lines.append("Safety Monitor:")
            lines.append(
                "  Deviation: %s (threshold=%.1f)"
                % (
                    "ALARM" if status["deviation_alarm"] else "OK",
                    status["deviation_threshold"],
                )
            )
            lines.append(
                "  Velocity: %s (threshold=%.1f)"
                % (
                    "ALARM" if status["velocity_alarm"] else "OK",
                    status["velocity_threshold"],
                )
            )
            lines.append(
                "  Torque: %s (threshold=%.1f)"
                % (
                    "ALARM" if status["torque_alarm"] else "OK",
                    status["torque_threshold"],
                )
            )
            lines.append("")
        except Exception:
            pass

        # Emergency stop
        try:
            estop = self.printer.lookup_object("emergency_stop")
            status = estop.get_status()
            lines.append("Emergency Stop: %s" % (
                "TRIGGERED" if status["triggered"] else "OK"
            ))
            lines.append("")
        except Exception:
            pass

        # Safety door
        try:
            for name, obj in self.printer.lookup_objects():
                if name.startswith("safety_door"):
                    status = obj.get_status()
                    door = "OPEN" if status["door_open"] else "CLOSED"
                    armed = "ARMED" if status["armed"] else "DISARMED"
                    lines.append(
                        "Safety Door %s: %s (%s)" % (name, door, armed)
                    )
            lines.append("")
        except Exception:
            pass

        # Alarm history
        try:
            alarm_hist = self.printer.lookup_object("alarm_history")
            status = alarm_hist.get_status()
            lines.append("Alarm History:")
            lines.append(
                "  Total alarms: %d" % status["total_alarms"]
            )
            lines.append(
                "  Unacknowledged: %d" % status["unacknowledged"]
            )
            lines.append("")
        except Exception:
            pass

        # Production counter
        try:
            prod = self.printer.lookup_object("production_counter")
            status = prod.get_status()
            lines.append("Production Counter:")
            lines.append(
                "  Total prints: %d" % status["total_prints"]
            )
            lines.append(
                "  Runtime: %.1f hours" % status["total_runtime_hours"]
            )
            lines.append(
                "  Maintenance due: %s"
                % ("YES" if status["maintenance_due"] else "No")
            )
        except Exception:
            pass

        gcmd.respond_info("\n".join(lines))


def load_config(config):
    """Load [servo_status] config section."""
    return ServoStatus(config)
