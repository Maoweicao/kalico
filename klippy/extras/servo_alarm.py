# Servo alarm (ALM) pin monitoring for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class ServoAlarm:
    """Independent servo alarm pin monitor.

    Monitors a GPIO pin connected to a servo drive's ALM output.
    When triggered, can execute shutdown, pause, or custom G-code.

    Config format:
        [servo_alarm my_servo]
        alm_pin: PB6
        action: shutdown
        invert: false
        debounce: 0.01
        alarm_gcode:
          M118 Servo alarm!
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        self.reactor = self.printer.get_reactor()

        # Configuration
        self.alm_pin = config.get("alm_pin")
        self.action = config.get("action", "shutdown")
        self.invert = config.getboolean("invert", False)
        self.debounce = config.getfloat("debounce", 0.01, minval=0.0)

        # Validate action
        valid_actions = ("shutdown", "pause", "gcode", "none")
        if self.action not in valid_actions:
            raise config.error(
                "Invalid alarm_action '%s' in [%s]. Options: %s"
                % (self.action, self.name, ", ".join(valid_actions))
            )

        # Load alarm G-code template if action is "gcode"
        self._alarm_gcode = None
        if self.action == "gcode":
            gcode_macro = self.printer.load_object(config, "gcode_macro")
            self._alarm_gcode = gcode_macro.load_template(
                config, "alarm_gcode"
            )

        # State tracking
        self._alarm_active = False
        self._alarm_count = 0
        self._last_alarm_time = 0.0

        # Register GPIO button
        buttons = self.printer.load_object(config, "buttons")
        buttons.register_debounce_button(
            self.alm_pin, self._handle_pin_change, config
        )

        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        cmd_name = "QUERY_ALARM_" + self.name.split()[-1].upper()
        gcode.register_command(
            cmd_name, self.cmd_QUERY_ALARM,
            desc="Query servo alarm state for %s" % self.name
        )
        cmd_name = "CLEAR_ALARM_" + self.name.split()[-1].upper()
        gcode.register_command(
            cmd_name, self.cmd_CLEAR_ALARM,
            desc="Clear servo alarm for %s" % self.name
        )

        # Register event handlers
        self.printer.register_event_handler(
            "klippy:ready", self._handle_ready
        )

        logging.info(
            "ServoAlarm '%s': pin=%s, action=%s, invert=%s",
            self.name, self.alm_pin, self.action, self.invert,
        )

    def _handle_ready(self):
        """Called when printer is ready."""
        # Query initial pin state
        pass

    def _handle_pin_change(self, eventtime, state):
        """Called when ALM pin state changes."""
        # Apply inversion: state=1 means pin is HIGH
        # For most servo drives, ALM is active-low (LOW = alarm)
        alarmed = bool(state) != self.invert

        if alarmed == self._alarm_active:
            return  # No change

        self._alarm_active = alarmed

        if alarmed:
            self._alarm_count += 1
            self._last_alarm_time = eventtime
            logging.error(
                "ServoAlarm '%s': ALARM TRIGGERED (count=%d)",
                self.name, self._alarm_count,
            )
            # Fire event for alarm_history
            try:
                self.printer.send_event(
                    "servo_alarm:triggered",
                    self.name,
                    "alm_pin",
                    {
                        "pin": self.alm_pin,
                        "count": self._alarm_count,
                        "action": self.action,
                    },
                )
            except Exception:
                pass
            self._execute_alarm_action(eventtime)
        else:
            logging.info(
                "ServoAlarm '%s': alarm cleared", self.name
            )

    def _execute_alarm_action(self, eventtime):
        """Execute the configured alarm action."""
        if self.action == "shutdown":
            self.printer.invoke_shutdown(
                "Servo ALM alarm on %s" % self.name
            )
        elif self.action == "pause":
            self._pause_print()
        elif self.action == "gcode" and self._alarm_gcode:
            try:
                gcode = self.printer.lookup_object("gcode")
                gcode.run_script(
                    self._alarm_gcode.render()
                )
            except Exception as e:
                logging.error(
                    "ServoAlarm '%s': alarm gcode error: %s",
                    self.name, e,
                )
                # Fallback to shutdown on gcode error
                self.printer.invoke_shutdown(
                    "Servo ALM alarm on %s (gcode error)" % self.name
                )

    def _pause_print(self):
        """Pause the current print."""
        try:
            print_stats = self.printer.lookup_object("print_stats")
            if print_stats.get_status()["state"] == "printing":
                gcode = self.printer.lookup_object("gcode")
                gcode.run_script_from_command("PAUSE")
                logging.info(
                    "ServoAlarm '%s': print paused", self.name
                )
        except Exception as e:
            logging.error(
                "ServoAlarm '%s': pause failed: %s", self.name, e
            )
            # Fallback to shutdown
            self.printer.invoke_shutdown(
                "Servo ALM alarm on %s (pause failed)" % self.name
            )

    def is_alarm_active(self):
        """Return True if alarm is currently active."""
        return self._alarm_active

    def get_alarm_count(self):
        """Return number of alarm events since startup."""
        return self._alarm_count

    def clear_alarm(self):
        """Clear the alarm state (does not reset hardware)."""
        self._alarm_active = False
        logging.info("ServoAlarm '%s': alarm state cleared", self.name)

    def get_status(self, eventtime=None):
        """Return alarm status for API/Moonraker."""
        return {
            "alarm_active": self._alarm_active,
            "alarm_count": self._alarm_count,
            "last_alarm_time": self._last_alarm_time,
            "pin": self.alm_pin,
            "action": self.action,
        }

    def cmd_QUERY_ALARM(self, gcmd):
        """Query alarm state."""
        if self._alarm_active:
            msg = "Servo %s: ALARM ACTIVE (count=%d)" % (
                self.name, self._alarm_count
            )
        else:
            msg = "Servo %s: OK" % self.name
        gcmd.respond_info(msg)

    def cmd_CLEAR_ALARM(self, gcmd):
        """Clear alarm state."""
        self.clear_alarm()
        gcmd.respond_info("Servo %s: alarm cleared" % self.name)


def load_config_prefix(config):
    """Load a [servo_alarm xxx] config section."""
    return ServoAlarm(config)
