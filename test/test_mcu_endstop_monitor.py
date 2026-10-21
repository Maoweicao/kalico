# Tests for the endstop monitoring bridge of MCU_endstop
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from klippy.mcu import MCU_endstop

CLOCK_FREQ = 1000000


class _FakeMCU:
    def __init__(self):
        self.responses = []

    def print_time_to_clock(self, print_time):
        return int(print_time * CLOCK_FREQ)

    def seconds_to_clock(self, seconds):
        return int(seconds * CLOCK_FREQ)

    def register_response(self, cb, msg, oid):
        self.responses.append((cb, msg, oid))


class _FakeCommand:
    def __init__(self):
        self.sent = []

    def send(self, params, minclock=0):
        self.sent.append(params)


def _make_endstop(oid=3, invert=0):
    es = object.__new__(MCU_endstop)
    es._mcu = _FakeMCU()
    es._oid = oid
    es._invert = invert
    es._monitor_cmd = _FakeCommand()
    return es


######################################################################
# monitor_start()
######################################################################


def test_monitor_start_sends_the_expected_parameters():
    es = _make_endstop(oid=3)
    es.monitor_start(10.0, 0.000050, 4, 0.000050)
    params = es._monitor_cmd.sent[0]
    assert params[0] == 3
    assert params[1] == 10000000
    assert params[2] == 50
    assert params[3] == 4
    # The rest time is the distance between the two print times
    assert params[4] == 50
    # The physical pin level that means "triggered"
    assert params[5] == 1


def test_monitor_start_inverts_the_trigger_level():
    es = _make_endstop(oid=3, invert=1)
    es.monitor_start(10.0, 0.000050, 4, 0.000050)
    # The firmware reports the raw pin level - the host inverts it
    assert es._monitor_cmd.sent[0][5] == 0


def test_monitor_start_with_a_triggered_level():
    es = _make_endstop(oid=3)
    es.monitor_start(10.0, 0.000050, 4, 0.000050, triggered=True)
    assert es._monitor_cmd.sent[0][5] == 1


def test_monitor_start_computes_the_rest_ticks_from_the_print_time():
    es = _make_endstop(oid=3)
    es.monitor_start(10.0, 0.000050, 4, 0.002000)
    params = es._monitor_cmd.sent[0]
    # 2ms at 1MHz is 2000 ticks
    assert params[4] == 2000


def test_monitor_start_with_a_zero_rest_time():
    es = _make_endstop(oid=3)
    es.monitor_start(10.0, 0.000050, 4, 0.0)
    # The rest time may not become negative because of the rounding
    assert es._monitor_cmd.sent[0][4] == 0


######################################################################
# monitor_stop()
######################################################################


def test_monitor_stop_disables_the_monitoring():
    es = _make_endstop(oid=3)
    es.monitor_stop()
    # A zero clock disables the monitoring in the firmware
    assert es._monitor_cmd.sent[0] == [3, 0, 0, 0, 0, 0]


######################################################################
# Response callbacks
######################################################################


def test_register_monitor_callback():
    es = _make_endstop(oid=3)

    def cb(params):
        pass

    es.register_monitor_callback(cb)
    assert es._mcu.responses[-1] == (cb, "endstop_monitor_state", 3)


def test_unregister_monitor_callback():
    es = _make_endstop(oid=3)
    es.unregister_monitor_callback()
    assert es._mcu.responses[-1] == (None, "endstop_monitor_state", 3)


def test_get_oid():
    assert _make_endstop(oid=42).get_oid() == 42
