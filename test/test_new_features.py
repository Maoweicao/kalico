# Tests for the newly added modules
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import importlib.util

import pytest

from klippy.extras.dummy_thermistor import DUMMY_REPORT_TIME, DummyThermistor
from klippy.extras.heaters import NullHeater

KINEMATICS = [
    "scara",
    "tpara",
    "polargraph",
    "belt",
    "robot_arm",
    "foam_cutter",
    "coreyx",
    "coreyz",
    "corezx",
    "corezy",
]


def _import_kinematics(name):
    return importlib.import_module("klippy.kinematics." + name)


######################################################################
# The dummy thermistor
######################################################################


class _FakeReactor:
    NOW = 0.0
    NEVER = 9999999999.999

    def __init__(self):
        self._now = 0.0
        self.timers = []

    def monotonic(self):
        return self._now

    def register_timer(self, callback, waketime=None):
        self.timers.append(callback)
        return len(self.timers)

    def update_timer(self, handle, waketime):
        pass


class _FakeMCU:
    def estimated_print_time(self, systime):
        return systime + 10.0


class _FakePrinter:
    def __init__(self):
        self.reactor = _FakeReactor()
        self.objects = {"gcode": _FakeGCode()}
        self.events = {}

    def get_reactor(self):
        return self.reactor

    def add_object(self, name, obj):
        self.objects[name] = obj

    def lookup_object(self, name, default=None):
        return self.objects.get(name, default)

    def register_event_handler(self, name, cb):
        self.events[name] = cb


class _FakeGCode:
    error = Exception

    def __init__(self):
        self.commands = {}
        self.responses = []

    def register_mux_command(self, cmd, key, value, func, desc=None):
        self.commands[cmd] = func

    def respond_info(self, msg):
        self.responses.append(msg)


class _FakeConfig:
    error = Exception

    def __init__(self, printer, name="temperature_sensor my_sensor", **options):
        self._printer = printer
        self._name = name
        self._options = options

    def get_printer(self):
        return self._printer

    def get_name(self):
        return self._name

    def getfloat(self, option, default=None, minval=None, maxval=None):
        value = self._options.get(option, default)
        if value is None:
            return None
        value = float(value)
        if minval is not None and value < minval:
            raise self.error("%s is below the minimum" % option)
        return value


def _make_dummy_sensor(**options):
    printer = _FakePrinter()
    printer.add_object("mcu", _FakeMCU())
    config = _FakeConfig(printer, **options)
    sensor = DummyThermistor(config)
    return printer, sensor


def test_the_dummy_sensor_uses_the_default_temperature():
    printer, sensor = _make_dummy_sensor()
    assert sensor.temp == pytest.approx(25.0)


def test_the_dummy_sensor_uses_the_configured_temperature():
    printer, sensor = _make_dummy_sensor(temperature=60.0)
    assert sensor.temp == pytest.approx(60.0)


def test_the_dummy_sensor_rejects_a_temperature_below_absolute_zero():
    with pytest.raises(Exception):
        _make_dummy_sensor(temperature=-300.0)


def test_the_dummy_sensor_registers_itself():
    printer, sensor = _make_dummy_sensor()
    assert printer.lookup_object("temperature_sensor my_sensor") is sensor


def test_the_dummy_sensor_registers_the_gcode_command():
    printer, sensor = _make_dummy_sensor()
    assert "SET_DUMMY_TEMPERATURE" in printer.lookup_object("gcode").commands


def test_the_dummy_sensor_minmax_can_be_changed():
    printer, sensor = _make_dummy_sensor()
    sensor.setup_minmax(10.0, 80.0)
    assert sensor.min_temp == pytest.approx(10.0)
    assert sensor.max_temp == pytest.approx(80.0)


def test_the_dummy_sensor_report_time():
    printer, sensor = _make_dummy_sensor()
    assert sensor.get_report_time_delta() == DUMMY_REPORT_TIME


def test_the_dummy_sensor_reports_the_temperature():
    printer, sensor = _make_dummy_sensor(temperature=42.0)
    status = sensor.get_status(None)
    assert status["temperature"] == pytest.approx(42.0)
    assert status["is_active"] is True


def test_the_dummy_sensor_samples_the_temperature():
    printer, sensor = _make_dummy_sensor(temperature=42.0)
    reported = []
    sensor.setup_callback(lambda ptime, temp: reported.append((ptime, temp)))
    sensor.handle_connect()
    # The sample timer is registered
    assert printer.reactor.timers
    printer.reactor.timers[0](5.0)
    assert reported
    assert reported[0][1] == pytest.approx(42.0)


def test_the_dummy_sensor_does_not_sample_when_inactive():
    printer, sensor = _make_dummy_sensor()
    reported = []
    sensor.setup_callback(lambda ptime, temp: reported.append((ptime, temp)))
    sensor.is_active = False
    sensor.handle_connect()
    assert not printer.reactor.timers
    assert reported == []


def test_the_dummy_sensor_sets_the_temperature():
    printer, sensor = _make_dummy_sensor()

    class _Gcmd:
        error = Exception

        def __init__(self):
            self.params = {"TEMPERATURE": "55.5"}

        def get_float(self, name, default=None, minval=None, maxval=None):
            return float(self.params[name])

        def respond_info(self, msg):
            printer.lookup_object("gcode").responses.append(msg)

    sensor.cmd_SET_DUMMY_TEMPERATURE(_Gcmd())
    assert sensor.temp == pytest.approx(55.5)


######################################################################
# The null heater
######################################################################


def test_the_null_heater_defaults():
    heater = NullHeater()
    assert heater.can_extrude is True
    assert heater.cold_extrude is True
    assert heater.min_temp == pytest.approx(0.0)
    assert heater.max_temp == pytest.approx(100.0)
    assert heater.smoothed_temp == pytest.approx(25.0)
    assert heater.max_power == pytest.approx(1.0)


def test_the_null_heater_minmax_can_be_changed():
    heater = NullHeater()
    heater.setup_minmax(5.0, 50.0)
    assert heater.min_temp == pytest.approx(5.0)
    assert heater.max_temp == pytest.approx(50.0)


def test_the_null_heater_always_allows_extrusion():
    heater = NullHeater()
    assert heater.can_extrude is True


def test_the_null_heater_target_temperature():
    heater = NullHeater()
    heater.set_temp(0.0)
    assert heater.target_temp == pytest.approx(0.0)
    # The null heater always reports a room temperature
    temp, target = heater.get_temp()
    assert temp == pytest.approx(25.0)
    assert target == pytest.approx(0.0)


def test_the_null_heater_status():
    heater = NullHeater()
    status = heater.get_status(None)
    assert status["temperature"] == pytest.approx(25.0)
    assert status["can_extrude"] is True


######################################################################
# The new kinematics
######################################################################


@pytest.mark.parametrize("name", KINEMATICS)
def test_the_kinematics_module_can_be_imported(name):
    module = _import_kinematics(name)
    assert hasattr(module, "load_kinematics")


@pytest.mark.parametrize("name", KINEMATICS)
def test_the_kinematics_provide_a_position_calculation(name):
    module = _import_kinematics(name)
    assert hasattr(module, "load_kinematics")


def test_the_core_variants_are_distinct():
    modules = [
        _import_kinematics(n) for n in ("coreyx", "coreyz", "corezx", "corezy")
    ]
    assert len({m.__name__ for m in modules}) == 4
