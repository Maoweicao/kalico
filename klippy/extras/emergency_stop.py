# Emergency stop and safety door support for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class EmergencyStop:
    """Dedicated emergency stop button support.

    Monitors a hardware E-Stop button connected to a GPIO pin.
    When triggered, immediately halts all motion.

    Config format:
        [emergency_stop]
        estop_pin: ^PA0
        estop_invert: false
        estop_debounce: 0.01
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()

        # Configuration
        self.estop_pin = config.get("estop_pin")
        self.estop_invert = config.getboolean("estop_invert", False)

        # State
        self._triggered = False
        self._trigger_count = 0

        # Register GPIO button
        buttons = self.printer.load_object(config, "buttons")
        buttons.register_debounce_button(
            self.estop_pin, self._handle_estop, config
        )

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_EMERGENCY_STOP",
            self.cmd_QUERY_EMERGENCY_STOP,
            desc="Query emergency stop status",
        )

        logging.info(
            "EmergencyStop '%s': pin=%s, invert=%s",
            self.name,
            self.estop_pin,
            self.estop_invert,
        )

    def _handle_estop(self, eventtime, state):
        """Handle E-Stop button state change."""
        triggered = bool(state) != self.estop_invert
        if triggered == self._triggered:
            return

        self._triggered = triggered
        if triggered:
            self._trigger_count += 1
            logging.error(
                "Emergency stop TRIGGERED (count=%d)", self._trigger_count
            )
            # Fire event for alarm_history
            try:
                self.printer.send_event(
                    "emergency_stop:triggered",
                    self.name,
                    {"count": self._trigger_count},
                )
            except Exception:
                pass
            # Execute emergency stop
            self.printer.invoke_shutdown("Emergency stop button pressed")

    def is_triggered(self):
        """Return True if E-Stop is currently triggered."""
        return self._triggered

    def get_status(self, eventtime=None):
        """Return E-Stop status."""
        return {
            "triggered": self._triggered,
            "trigger_count": self._trigger_count,
            "pin": self.estop_pin,
        }

    def cmd_QUERY_EMERGENCY_STOP(self, gcmd):
        """Query E-Stop status."""
        if self._triggered:
            msg = "Emergency Stop: TRIGGERED (count=%d)" % self._trigger_count
        else:
            msg = "Emergency Stop: OK"
        gcmd.respond_info(msg)


class SafetyDoor:
    """Safety door interlock support.

    Monitors a door sensor connected to a GPIO pin.
    When door opens, can pause print or trigger emergency stop.

    Config format:
        [safety_door]
        door_pin: ^PA1
        door_invert: false
        door_debounce: 0.01
        door_action: shutdown
        allow_print_with_door_open: false
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()

        # Configuration
        self.door_pin = config.get("door_pin")
        self.door_invert = config.getboolean("door_invert", False)
        self.door_action = config.get("door_action", "shutdown")
        self.allow_print_with_door_open = config.getboolean(
            "allow_print_with_door_open", False
        )

        # Validate action
        valid_actions = ("shutdown", "pause", "none")
        if self.door_action not in valid_actions:
            raise config.error(
                "Invalid door_action '%s' in [%s]. Options: %s"
                % (
                    self.door_action,
                    self.name,
                    ", ".join(valid_actions),
                )
            )

        # State
        self._door_open = False
        self._open_count = 0
        self._armed = True

        # Register GPIO button
        buttons = self.printer.load_object(config, "buttons")
        buttons.register_debounce_button(
            self.door_pin, self._handle_door, config
        )

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command(
            "QUERY_SAFETY_DOOR",
            self.cmd_QUERY_SAFETY_DOOR,
            desc="Query safety door status",
        )
        gcode.register_command(
            "ARM_SAFETY_DOOR",
            self.cmd_ARM_SAFETY_DOOR,
            desc="Arm safety door monitoring",
        )
        gcode.register_command(
            "DISARM_SAFETY_DOOR",
            self.cmd_DISARM_SAFETY_DOOR,
            desc="Disarm safety door monitoring",
        )

        # Register event handlers
        self.printer.register_event_handler(
            "print_stats:start_printing", self._on_print_start
        )

        logging.info(
            "SafetyDoor '%s': pin=%s, action=%s",
            self.name,
            self.door_pin,
            self.door_action,
        )

    def _handle_door(self, eventtime, state):
        """Handle door sensor state change."""
        door_open = bool(state) != self.door_invert
        if door_open == self._door_open:
            return

        self._door_open = door_open
        if door_open:
            self._open_count += 1
            logging.warning(
                "Safety door OPENED (count=%d)", self._open_count
            )

            # Fire event for alarm_history
            try:
                self.printer.send_event(
                    "safety_door:opened",
                    self.name,
                    {"count": self._open_count},
                )
            except Exception:
                pass

            if self._armed:
                self._execute_action()
        else:
            logging.info("Safety door CLOSED")

    def _execute_action(self):
        """Execute configured door action."""
        if self.door_action == "shutdown":
            self.printer.invoke_shutdown("Safety door opened")
        elif self.door_action == "pause":
            try:
                print_stats = self.printer.lookup_object("print_stats")
                if print_stats.get_status()["state"] == "printing":
                    gcode = self.printer.lookup_object("gcode")
                    gcode.run_script_from_command("PAUSE")
                    logging.info(
                        "SafetyDoor: print paused due to door open"
                    )
            except Exception as e:
                logging.error("SafetyDoor: pause failed: %s", e)
                self.printer.invoke_shutdown(
                    "Safety door opened (pause failed)"
                )

    def _on_print_start(self):
        """Check if printing is allowed with door open."""
        if self._door_open and not self.allow_print_with_door_open:
            logging.error(
                "SafetyDoor: print blocked - door is open"
            )
            gcode = self.printer.lookup_object("gcode")
            gcode.run_script_from_command("PAUSE")

    def is_door_open(self):
        """Return True if door is currently open."""
        return self._door_open

    def is_armed(self):
        """Return True if safety door monitoring is armed."""
        return self._armed

    def arm(self):
        """Arm safety door monitoring."""
        self._armed = True
        logging.info("SafetyDoor: armed")

    def disarm(self):
        """Disarm safety door monitoring."""
        self._armed = False
        logging.info("SafetyDoor: disarmed")

    def get_status(self, eventtime=None):
        """Return safety door status."""
        return {
            "door_open": self._door_open,
            "open_count": self._open_count,
            "armed": self._armed,
            "pin": self.door_pin,
            "action": self.door_action,
        }

    def cmd_QUERY_SAFETY_DOOR(self, gcmd):
        """Query safety door status."""
        if self._door_open:
            state = "OPEN"
        else:
            state = "CLOSED"
        armed = "ARMED" if self._armed else "DISARMED"
        msg = "Safety Door: %s, %s (count=%d)" % (
            state,
            armed,
            self._open_count,
        )
        gcmd.respond_info(msg)

    def cmd_ARM_SAFETY_DOOR(self, gcmd):
        """Arm safety door monitoring."""
        self.arm()
        gcmd.respond_info("Safety door armed")

    def cmd_DISARM_SAFETY_DOOR(self, gcmd):
        """Disarm safety door monitoring."""
        self.disarm()
        gcmd.respond_info("Safety door disarmed")


def load_config(config):
    """Load [emergency_stop] config section."""
    return EmergencyStop(config)


def load_config_prefix(config):
    """Load [safety_door] config section."""
    return SafetyDoor(config)
