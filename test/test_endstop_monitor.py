# Tests for the endstop monitor module
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import pytest
from klippy_testing import PrinterShim

from klippy.extras.endstop_monitor import EndstopMonitor

######################################################################
# Helpers
######################################################################


def _write_config(tmp_path, sections):
    cfg = tmp_path / "printer.cfg"
    lines = []
    for name, options in sections.items():
        lines.append("[%s]" % name)
        for option, value in options.items():
            lines.append("%s: %s" % (option, value))
        lines.append("")
    cfg.write_text("\n".join(lines) + "\n")
    return cfg


class _FakeMCUEndstop:
    """A stand-in for klippy.mcu.MCU_endstop."""

    def __init__(self, oid=1, value=0):
        self._oid = oid
        self._value = value
        self.monitor_calls = []
        self.callbacks = []

    def get_oid(self):
        return self._oid

    def monitor_start(
        self, print_time, sample_time, sample_count, rest_time, triggered=True
    ):
        self.monitor_calls.append(
            (
                "start",
                print_time,
                sample_time,
                sample_count,
                rest_time,
                triggered,
            )
        )

    def monitor_stop(self):
        self.monitor_calls.append(("stop",))

    def register_monitor_callback(self, cb):
        self.callbacks.append(cb)

    def unregister_monitor_callback(self):
        self.callbacks = []

    def query_endstop(self):
        return self._value


class _FakeQueryEndstops:
    def __init__(self, endstops):
        self.endstops = endstops


class _FakeKinematics:
    rails = []


class _FakeToolhead:
    def __init__(self, print_time=100.0):
        self._print_time = print_time

    def get_kinematics(self):
        return _FakeKinematics()

    def get_last_move_time(self):
        return self._print_time


class _FakeEndstopProvider:
    """An object that exposes an endstop the way a probe would."""

    def __init__(self, endstop):
        self.mcu_endstop = endstop


def _setup(
    tmp_path,
    monitor_options=None,
    section="endstop_monitor axis",
    endstops=None,
    objects=None,
    extra_sections=None,
):
    """Build a printer that has an endstop monitor section.

    The config file is generated so that the real option names and the
    real defaults of the module are always used.
    """
    sections = {"printer": {"kinematics": "cartesian"}}
    if extra_sections:
        sections.update(extra_sections)
    sections[section] = monitor_options or {}
    cfg = _write_config(tmp_path, sections)
    printer = PrinterShim({"config_file": str(cfg)})
    printer.load_config()
    if endstops:
        printer.add_object("query_endstops", _FakeQueryEndstops(endstops))
    printer.add_object("toolhead", _FakeToolhead())
    for name, obj in (objects or {}).items():
        printer.add_object(name, obj)
    pconfig = printer.lookup_object("configfile")
    return printer, pconfig.getsection(section)


######################################################################
# Configuration validation
######################################################################


def test_invalid_action_is_rejected(tmp_path):
    with pytest.raises(Exception) as exc:
        printer, section = _setup(tmp_path, {"action": "explode"})
        EndstopMonitor(section)
    assert "Invalid action" in str(exc.value)


def test_gcode_action_requires_a_gcode_option(tmp_path):
    with pytest.raises(Exception) as exc:
        printer, section = _setup(tmp_path, {"action": "gcode"})
        EndstopMonitor(section)
    assert "requires a 'gcode' option" in str(exc.value)


def test_the_defaults_are_applied(tmp_path):
    printer, section = _setup(tmp_path)
    monitor = EndstopMonitor(section)
    assert monitor.enable is True
    assert monitor.action == "shutdown"
    assert monitor.poll_time == pytest.approx(0.000050)
    assert monitor.sample_count == 4
    assert monitor.debounce == pytest.approx(0.05)


######################################################################
# Endstop discovery
######################################################################


def test_monitored_names_are_resolved(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path, {"monitored": "x"}, endstops=[(endstop, "x")]
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    assert [name for _, name in monitor._endstops] == ["x"]
    assert monitor._oid_to_name[7] == "x"


def test_all_registered_endstops_are_monitored_by_default(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(tmp_path, endstops=[(endstop, "x")])
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    assert [name for _, name in monitor._endstops] == ["x"]


def test_an_unknown_name_is_skipped(tmp_path):
    printer, section = _setup(tmp_path, {"monitored": "nope"})
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    assert monitor._endstops == []


def test_an_endstop_of_another_provider_is_found(tmp_path):
    endstop = _FakeMCUEndstop(oid=9)
    printer, section = _setup(
        tmp_path,
        {"monitored": "probe"},
        objects={"probe": _FakeEndstopProvider(endstop)},
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    assert [name for _, name in monitor._endstops] == ["probe"]


def test_a_second_section_cannot_claim_the_same_endstop(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path,
        {"monitored": "x"},
        section="endstop_monitor axis",
        endstops=[(endstop, "x")],
        extra_sections={"endstop_monitor other": {"monitored": "x"}},
    )
    first = EndstopMonitor(section)
    first._handle_ready()
    assert len(first._endstops) == 1

    pconfig = printer.lookup_object("configfile")
    second = EndstopMonitor(pconfig.getsection("endstop_monitor other"))
    second._handle_ready()
    # The endstop is already monitored by the first section
    assert second._endstops == []


######################################################################
# Arming
######################################################################


def test_arming_starts_the_mcu_monitor(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path, {"monitored": "x"}, endstops=[(endstop, "x")]
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    monitor._handle_printing(100.0)
    assert endstop.monitor_calls[0][0] == "start"
    assert monitor._armed is True


def test_disarming_stops_the_mcu_monitor(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path, {"monitored": "x"}, endstops=[(endstop, "x")]
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    monitor._handle_printing(100.0)
    monitor._handle_not_printing(100.0)
    assert ("stop",) in endstop.monitor_calls
    assert monitor._armed is False


def test_a_disabled_monitor_does_not_arm(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path, {"enable": 0, "monitored": "x"}, endstops=[(endstop, "x")]
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    monitor._handle_printing(100.0)
    assert endstop.monitor_calls == []


######################################################################
# Trigger handling
######################################################################


def _armed_monitor(tmp_path, **options):
    endstop = _FakeMCUEndstop(oid=7)
    options.setdefault("monitored", "x")
    printer, section = _setup(tmp_path, options, endstops=[(endstop, "x")])
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    monitor._handle_printing(100.0)
    return printer, monitor, endstop


def test_a_trigger_shuts_the_printer_down(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="shutdown")
    monitor._handle_state({"oid": 7, "pin_value": 1})
    assert len(printer.shutdowns) == 1
    assert "x" in printer.shutdowns[0]


def test_a_trigger_is_latched(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="shutdown")
    monitor._handle_state({"oid": 7, "pin_value": 1})
    monitor._handle_state({"oid": 7, "pin_value": 1})
    # The switch is latched so that the status shows it
    assert "x" in monitor._triggered


def test_a_trigger_is_debounced(tmp_path):
    printer, monitor, endstop = _armed_monitor(
        tmp_path, action="shutdown", debounce=10.0
    )
    monitor._handle_state({"oid": 7, "pin_value": 1})
    monitor._handle_state({"oid": 7, "pin_value": 1})
    # The second hit is inside the debounce window
    assert len(printer.shutdowns) == 1


def test_a_trigger_runs_a_gcode_script(tmp_path):
    printer, monitor, endstop = _armed_monitor(
        tmp_path, action="gcode", gcode="M117 triggered"
    )
    monitor._handle_state({"oid": 7, "pin_value": 1})
    assert "M117 triggered" in printer.lookup_object("gcode").scripts


def test_the_none_action_only_logs(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="none")
    monitor._handle_state({"oid": 7, "pin_value": 1})
    assert printer.shutdowns == []
    assert printer.lookup_object("gcode").scripts == []


def test_a_trigger_sends_an_event(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="none")
    events = []
    printer.register_event_handler(
        "endstop_monitor:triggered",
        lambda *args: events.append(args),
    )
    monitor._handle_state({"oid": 7, "pin_value": 1})
    assert events
    assert events[0][1] == "x"


def test_a_trigger_of_an_unknown_endstop_is_ignored(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="shutdown")
    monitor._handle_state({"oid": 999, "pin_value": 1})
    assert printer.shutdowns == []


def test_the_monitor_is_rearmed_after_a_trigger(tmp_path):
    printer, monitor, endstop = _armed_monitor(tmp_path, action="none")
    before = len(endstop.monitor_calls)
    monitor._handle_state({"oid": 7, "pin_value": 1})
    # A rearm timer is scheduled instead of an immediate rearm
    assert monitor._rearm_timer is not None
    assert len(endstop.monitor_calls) == before


######################################################################
# Reporting
######################################################################


def test_the_query_command_reports_every_section(tmp_path):
    endstop = _FakeMCUEndstop(oid=7)
    printer, section = _setup(
        tmp_path, {"monitored": "x"}, endstops=[(endstop, "x")]
    )
    monitor = EndstopMonitor(section)
    monitor._handle_ready()
    printer.call("QUERY_ENDSTOP_MONITOR")
    responses = printer.lookup_object("gcode").responses
    assert any("endstop monitor" in r.lower() for r in responses)
    assert any("x" in r for r in responses)


######################################################################
# State handling across printers
######################################################################


def test_the_state_does_not_leak_into_a_new_printer(tmp_path):
    # A config reload creates a new printer - the shared state of the old
    # one must not survive, otherwise the endstop of the new printer is
    # reported as "already monitored"
    printer, monitor, endstop = _armed_monitor(tmp_path, action="none")
    assert len(monitor._endstops) == 1

    new_endstop = _FakeMCUEndstop(oid=7)
    printer2, section2 = _setup(
        tmp_path, {"monitored": "x"}, endstops=[(new_endstop, "x")]
    )
    new_monitor = EndstopMonitor(section2)
    new_monitor._handle_ready()
    # The new printer has to be able to monitor the endstop
    assert len(new_monitor._endstops) == 1
