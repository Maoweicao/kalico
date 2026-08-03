# Handwheel (jog wheel) support for manual axis control
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class HandWheel:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        # Config
        self.axis = config.get("axis", "X").upper()
        if self.axis not in ("X", "Y", "Z", "E"):
            raise config.error(
                "Invalid handwheel axis '%s' (must be X, Y, Z, or E)"
                % self.axis
            )
        self.step_distance = config.getfloat("step_distance", 1.0, above=0.0)
        self.speed = config.getfloat("speed", 100.0, above=0.0)
        self.jog_speed = config.getfloat("jog_speed", 6000.0, above=0.0)
        self.fast_rate = config.getfloat("fast_rate", 0.030, above=0.0)
        # State
        self.is_active = False
        self.active_axis = self.axis
        self.last_cw_time = 0.0
        self.last_ccw_time = 0.0
        # Encoder config (deferred registration)
        self.encoder_pins = config.get("encoder_pins", None)
        self.steps_per_detent = config.getchoice(
            "encoder_steps_per_detent", [2, 4], 4
        )
        self.click_pin = config.get("click_pin", None)
        self.debounce_delay = config.getfloat("debounce_delay", 0.0, minval=0.0)
        # Register events
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        # Register G-code commands
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("JOG", self.cmd_JOG, desc=self.cmd_JOG_help)
        gcode.register_command(
            "SET_JOG", self.cmd_SET_JOG, desc=self.cmd_SET_JOG_help
        )

    def _handle_ready(self):
        if self.encoder_pins is None:
            return
        buttons = self.printer.lookup_object("buttons")
        try:
            pin1, pin2 = self.encoder_pins.split(",")
        except:
            raise self.printer.config_error(
                "Unable to parse handwheel encoder_pins"
            )
        buttons.register_rotary_encoder(
            pin1.strip(),
            pin2.strip(),
            self._on_cw,
            self._on_ccw,
            self.steps_per_detent,
        )
        if self.click_pin:
            if self.debounce_delay > 0.0:
                buttons.register_debounce_button(
                    self.click_pin,
                    self._on_click,
                    self._make_debounce_config(),
                )
            else:
                buttons.register_button_push(self.click_pin, self._on_click)
        logging.info(
            "Handwheel: initialized axis=%s step=%.3f speed=%.1f",
            self.active_axis,
            self.step_distance,
            self.speed,
        )

    def _make_debounce_config(self):
        """Create a minimal config object for DebounceButton."""
        printer = self.printer
        delay = self.debounce_delay

        class _Cfg:
            def get_printer(self):
                return printer

            def getfloat(self, key, default=0.0, **kw):
                if key == "debounce_delay":
                    return delay
                return default

        return _Cfg()

    def _on_cw(self, eventtime):
        if not self.is_active:
            return
        fast = (eventtime - self.last_cw_time) <= self.fast_rate
        self.last_cw_time = eventtime
        speed = self.jog_speed if fast else self.speed
        self._jog_move(1, speed)

    def _on_ccw(self, eventtime):
        if not self.is_active:
            return
        fast = (eventtime - self.last_ccw_time) <= self.fast_rate
        self.last_ccw_time = eventtime
        speed = self.jog_speed if fast else self.speed
        self._jog_move(-1, speed)

    def _jog_move(self, direction, speed):
        toolhead = self.printer.lookup_object("toolhead")
        status = toolhead.get_status(None)
        homed = status.get("homed_axes", "")
        axis_map = {"X": 0, "Y": 1, "Z": 2, "E": 3}
        idx = axis_map.get(self.active_axis)
        if idx is None:
            return
        axis_char = self.active_axis.lower()
        if idx < 3 and axis_char not in homed:
            return
        if idx == 3 and "x" not in homed:
            return
        curpos = list(toolhead.get_position())
        curpos[idx] += direction * self.step_distance
        try:
            toolhead.manual_move(curpos, speed)
        except Exception:
            logging.exception("Handwheel: move failed")

    def _on_click(self, eventtime, state=None):
        if state is not None and not state:
            return
        self.is_active = not self.is_active
        self.printer.send_event("handwheel:toggle", self.is_active)
        logging.info("Handwheel: %s", "activated" if self.is_active else "deactivated")

    def set_active_axis(self, axis):
        axis = axis.upper()
        if axis in ("X", "Y", "Z", "E"):
            self.active_axis = axis

    def set_step_distance(self, distance):
        self.step_distance = max(0.001, distance)

    def get_status(self, eventtime=None):
        return {
            "is_active": self.is_active,
            "active_axis": self.active_axis,
            "step_distance": self.step_distance,
            "speed": self.speed,
        }

    cmd_JOG_help = "Start or stop handwheel jog mode"

    def cmd_JOG(self, gcmd):
        if gcmd.get("STOP", None) is not None:
            self.is_active = False
            self.printer.send_event("handwheel:toggle", False)
            gcmd.respond_info("Handwheel jog stopped")
            return
        axis = gcmd.get("AXIS", self.active_axis).upper()
        if axis not in ("X", "Y", "Z", "E"):
            raise gcmd.error("Invalid axis '%s'" % axis)
        step = gcmd.get_float("STEP", self.step_distance, above=0.0)
        speed = gcmd.get_float("SPEED", self.speed, above=0.0)
        self.active_axis = axis
        self.step_distance = step
        self.speed = speed
        self.is_active = True
        self.printer.send_event("handwheel:toggle", True)
        gcmd.respond_info(
            "Handwheel jog active: axis=%s step=%.3f speed=%.1f"
            % (axis, step, speed)
        )

    cmd_SET_JOG_help = "Set handwheel jog parameters without changing state"

    def cmd_SET_JOG(self, gcmd):
        axis = gcmd.get("AXIS", None)
        if axis is not None:
            axis = axis.upper()
            if axis not in ("X", "Y", "Z", "E"):
                raise gcmd.error("Invalid axis '%s'" % axis)
            self.active_axis = axis
        step = gcmd.get_float("STEP", None, above=0.0)
        if step is not None:
            self.step_distance = step
        speed = gcmd.get_float("SPEED", None, above=0.0)
        if speed is not None:
            self.speed = speed
        jog_speed = gcmd.get_float("JOG_SPEED", None, above=0.0)
        if jog_speed is not None:
            self.jog_speed = jog_speed
        gcmd.respond_info(
            "Jog settings: axis=%s step=%.3f speed=%.1f jog_speed=%.1f"
            % (self.active_axis, self.step_distance, self.speed, self.jog_speed)
        )


def load_config(config):
    return HandWheel(config)
