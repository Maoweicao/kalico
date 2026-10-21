# Monitor endstop switches during printing
#
# Endstop switches are only sampled while homing/probing (see
# src/endstop.c: command_endstop_home() disables sampling when
# sample_count=0).  This module re-arms the endstop sampling
# (command_endstop_monitor) so that a switch hit during a print is
# reported to the host instead of being silently ignored.
#
# Multiple sections may be defined, each with its own action and its own
# set of monitored endstops:
#
#   [endstop_monitor axis]
#   action: shutdown
#   monitored: x, y, z
#
#   [endstop_monitor probe_guard]
#   action: pause
#   monitored: probe
#
# The "monitored" option accepts:
#   - axis names (x, y, z)
#   - the full name of a stepper that owns an endstop (stepper_x)
#   - the config section name of any other endstop provider
#     (probe, bltouch, dockable_probe my_probe, ...)
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging


class _MonitorState:
    """State shared by every [endstop_monitor ...] section of a printer.

    The state is kept on the printer object so that it does not survive a
    config reload.  A config reload creates a new printer and the endstop
    oids of the new printer may collide with the oids of the old one - a
    leftover claim would make the new section skip the endstop.
    """

    def __init__(self):
        self.instances = []
        self.claims = {}
        self.query_cmd_registered = False


def _get_state(printer):
    state = printer.lookup_object("endstop_monitor_state", None)
    if state is None:
        state = _MonitorState()
        printer.add_object("endstop_monitor_state", state)
    return state


class EndstopMonitor:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name()
        self.short_name = self.name.split()[-1]

        self.enable = config.getboolean("enable", True)
        self.action = config.get("action", "shutdown")
        self.gcode = config.get("gcode", "")
        self.poll_time = config.getfloat("poll_time", 0.000050, minval=0.000010)
        self.sample_count = config.getint(
            "sample_count", 4, minval=1, maxval=255
        )
        self.debounce = config.getfloat("debounce", 0.05, minval=0.0)
        self.monitored = config.get("monitored", "")

        valid_actions = ("shutdown", "pause", "gcode", "none")
        if self.action not in valid_actions:
            raise config.error(
                "Invalid action '%s' in [%s]. Options: %s"
                % (self.action, self.name, ", ".join(valid_actions))
            )
        if self.action == "gcode" and not self.gcode:
            raise config.error(
                "action 'gcode' requires a 'gcode' option in [%s]" % self.name
            )

        # (mcu_endstop, display_name) pairs for this section
        self._endstops = []
        self._oid_to_name = {}
        self._registry = {}
        self._armed = False
        self._last_trigger = {}
        self._triggered = set()
        self._rearm_timer = None

        self._state = _get_state(self.printer)
        self._state.instances.append(self)

        gcode = self.printer.lookup_object("gcode")
        if not self._state.query_cmd_registered:
            self._state.query_cmd_registered = True
            gcode.register_command(
                "QUERY_ENDSTOP_MONITOR",
                self._cmd_query_all,
                desc="Report the status of all endstop monitor sections",
            )

        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler(
            "idle_timeout:printing", self._handle_printing
        )
        self.printer.register_event_handler(
            "idle_timeout:ready", self._handle_not_printing
        )
        self.printer.register_event_handler(
            "idle_timeout:idle", self._handle_not_printing
        )
        # homing calls home_wait() which disables sampling; re-arm if printing
        self.printer.register_event_handler(
            "homing:home_rails_end", self._handle_home_end
        )

        logging.info(
            "EndstopMonitor '%s': enable=%s action=%s poll=%.6f samples=%d",
            self.name,
            self.enable,
            self.action,
            self.poll_time,
            self.sample_count,
        )

    # -- endstop discovery -------------------------------------------------

    def _build_registry(self):
        # Map every name a user may put in "monitored" to its MCU endstop.
        registry = {}

        def add(name, es):
            if name and es is not None and hasattr(es, "monitor_start"):
                registry.setdefault(name, es)

        # Endstops registered with query_endstops (steppers, trad_rack, ...)
        query_endstops = self.printer.lookup_object("query_endstops", None)
        if query_endstops is not None:
            for es, name in query_endstops.endstops:
                add(name, es)

        # Toolhead rails: full stepper name (stepper_x) and short name (x)
        try:
            kin = self.printer.lookup_object("toolhead").get_kinematics()
            for rail in getattr(kin, "rails", []):
                endstops = rail.get_endstops()
                if not endstops:
                    continue
                es = endstops[0][0]
                add(rail.get_name(), es)
                try:
                    add(rail.get_name(short=True), es)
                except TypeError:
                    pass
                for _, name in endstops:
                    add(name, es)
        except Exception:
            pass

        # Other endstop providers expose their endstop either as
        # "mcu_endstop" (probe, bltouch, dockable_probe, ...) or as
        # "mcu_pin" (input_pin, ...).  Register them by section name.
        for name, obj in self.printer.lookup_objects():
            es = getattr(obj, "mcu_endstop", None)
            if es is None:
                es = getattr(obj, "mcu_pin", None)
            add(name, es)

        return registry

    def _handle_ready(self):
        query_endstops = self.printer.lookup_object("query_endstops", None)
        self._registry = self._build_registry()

        if not self.enable:
            logging.info("EndstopMonitor '%s': disabled", self.name)
            return

        if self.monitored:
            names = [x.strip() for x in self.monitored.split(",") if x.strip()]
        elif query_endstops is not None:
            # Default: every endstop registered with query_endstops
            names = [name for _, name in query_endstops.endstops]
        else:
            names = []

        resolved = []
        for name in names:
            es = self._registry.get(name)
            if es is None:
                logging.warning(
                    "EndstopMonitor '%s': unknown endstop name '%s'",
                    self.name,
                    name,
                )
                continue
            oid = es.get_oid()
            prev = self._state.claims.get(oid)
            if prev is not None and prev != self.name:
                logging.warning(
                    "EndstopMonitor '%s': endstop '%s' is already monitored "
                    "by '%s'; ignoring",
                    self.name,
                    name,
                    prev,
                )
                continue
            self._state.claims[oid] = self.name
            resolved.append((es, name))

        self._endstops = resolved
        self._oid_to_name = {es.get_oid(): name for es, name in resolved}
        for es, name in resolved:
            es.register_monitor_callback(self._handle_state)
        logging.info(
            "EndstopMonitor '%s': monitoring %s",
            self.name,
            ", ".join(name for _, name in resolved) or "(none)",
        )

    # -- arming ------------------------------------------------------------

    def _arm(self):
        if not self._endstops or not self.enable:
            return
        print_time = self.printer.lookup_object("toolhead").get_last_move_time()
        for mcu_endstop, name in self._endstops:
            mcu_endstop.monitor_start(
                print_time,
                self.poll_time,
                self.sample_count,
                self.poll_time,
            )
        self._armed = True

    def _disarm(self):
        if self._rearm_timer is not None:
            self.reactor.unregister_timer(self._rearm_timer)
            self._rearm_timer = None
        if not self._endstops:
            return
        for mcu_endstop, name in self._endstops:
            mcu_endstop.monitor_stop()
        self._armed = False

    def _schedule_rearm(self):
        # The MCU monitor is one-shot; re-arm after the debounce window so a
        # still-pressed switch does not flood the serial link with reports.
        if self._rearm_timer is not None:
            return
        self._rearm_timer = self.reactor.register_timer(
            self._rearm_event, self.reactor.monotonic() + self.debounce
        )

    def _rearm_event(self, eventtime):
        self._rearm_timer = None
        if self._armed and self.enable:
            self._arm()
        return self.reactor.NEVER

    def _handle_printing(self, print_time):
        self._arm()

    def _handle_not_printing(self, print_time):
        self._disarm()

    def _handle_home_end(self, homing_state, rails):
        if self._armed and self.enable:
            self._arm()

    # -- trigger handling --------------------------------------------------

    def _handle_state(self, params):
        name = self._oid_to_name.get(params["oid"])
        if name is None:
            return
        now = self.reactor.monotonic()
        last = self._last_trigger.get(name)
        if last is not None and now - last < self.debounce:
            # Debounced duplicate: stay quiet but keep monitoring.
            self._schedule_rearm()
            return
        self._last_trigger[name] = now
        self._triggered.add(name)
        logging.error(
            "EndstopMonitor '%s': endstop '%s' triggered (pin_value=%d)",
            self.name,
            name,
            params["pin_value"],
        )
        try:
            self.printer.send_event(
                "endstop_monitor:triggered",
                self.name,
                name,
                params["pin_value"],
            )
        except Exception:
            pass

        if self.action == "shutdown":
            self.printer.invoke_shutdown(
                "Endstop '%s' triggered during print (%s)" % (name, self.name)
            )
        elif self.action == "pause":
            try:
                print_stats = self.printer.lookup_object("print_stats")
                if print_stats.get_status()["state"] == "printing":
                    self.printer.lookup_object("gcode").run_script_from_command(
                        "PAUSE"
                    )
            except Exception as e:
                logging.error(
                    "EndstopMonitor '%s': pause failed: %s", self.name, e
                )
        elif self.action == "gcode":
            try:
                self.printer.lookup_object("gcode").run_script_from_command(
                    self.gcode
                )
            except Exception as e:
                logging.error(
                    "EndstopMonitor '%s': gcode failed: %s", self.name, e
                )

        # The MCU monitoring is one-shot; re-arm to keep watching.
        self._schedule_rearm()

    # -- reporting ---------------------------------------------------------

    def get_status(self, eventtime=None):
        return {
            "enable": self.enable,
            "action": self.action,
            "armed": self._armed,
            "monitored": [name for _, name in self._endstops],
            "triggered": sorted(self._triggered),
        }

    def _report(self, gcmd):
        lines = []
        for mcu_endstop, name in self._endstops:
            try:
                value = mcu_endstop.query_endstop()
            except Exception:
                value = None
            state = (
                "unknown"
                if value is None
                else ("TRIGGERED" if value else "open")
            )
            lines.append(
                "  %s: %s%s"
                % (name, state, " (latched)" if name in self._triggered else "")
            )
        gcmd.respond_info(
            "Endstop monitor '%s' (armed=%s, action=%s):\n%s"
            % (
                self.name,
                self._armed,
                self.action,
                "\n".join(lines) or "  (none)",
            )
        )

    def _cmd_query_all(self, gcmd):
        if not self._state.instances:
            gcmd.respond_info("Endstop monitor: no sections loaded")
            return
        for inst in self._state.instances:
            inst._report(gcmd)


def load_config(config):
    return EndstopMonitor(config)


def load_config_prefix(config):
    return EndstopMonitor(config)
