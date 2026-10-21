# Tests for the position encoder module
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import pytest
from klippy_testing import PrinterShim

from klippy.extras.encoder import (
    ANGLE_FULL_SCALE,
    AXIS_LIST,
    QUADRATURE_SENSOR_TYPES,
    SPI_SENSOR_TYPES,
    UNSUPPORTED_SENSOR_TYPES,
    Encoder,
)

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


def _make_printer(tmp_path, sections):
    cfg = _write_config(tmp_path, sections)
    printer = PrinterShim({"config_file": str(cfg)})
    printer.load_config()
    return printer


class _FakeConfig:
    """A config section wrapper for the pure logic of the encoder."""

    def __init__(self, printer, name="encoder my_enc"):
        self._printer = printer
        self._name = name

    def get_printer(self):
        return self._printer

    def get_name(self):
        return self._name

    def error(self, msg):
        return Exception(msg)


class _FakeBatchBulk:
    def __init__(self):
        self.clients = []

    def add_client(self, client_cb):
        self.clients.append(client_cb)


def _make_encoder(**attrs):
    # Build an encoder without the SPI setup - only the pure logic is
    # exercised here
    enc = object.__new__(Encoder)
    enc.printer = attrs.pop("printer", None)
    enc.name = attrs.pop("name", "my_enc")
    enc.encoder_type = attrs.pop("encoder_type", "as5047d")
    enc.is_quadrature = attrs.pop("is_quadrature", False)
    enc.stepper_name = attrs.pop("stepper_name", None)
    enc.last_position = attrs.pop("last_position", 0)
    enc.last_sample = attrs.pop("last_sample", None)
    enc.rotation_distance = attrs.pop("rotation_distance", 1.0)
    enc.scale = attrs.pop("scale", None)
    enc.invert = attrs.pop("invert", False)
    enc.axis = attrs.pop("axis", None)
    enc.cpr = attrs.pop("cpr", None)
    enc._sampling_active = attrs.pop("_sampling_active", False)
    enc.batch_bulk = attrs.pop("batch_bulk", None)
    for key, value in attrs.items():
        setattr(enc, key, value)
    return enc


######################################################################
# Configuration validation
######################################################################


def test_quadrature_types_are_rejected(tmp_path):
    # The quadrature firmware module is not part of the build
    assert "quadrature" in QUADRATURE_SENSOR_TYPES
    assert "quadrature" in UNSUPPORTED_SENSOR_TYPES
    printer = _make_printer(
        tmp_path,
        {"encoder my_enc": {"encoder_type": "quadrature"}},
    )
    config = printer.lookup_object("configfile").getsection("encoder my_enc")
    with pytest.raises(Exception) as exc:
        Encoder(config)
    assert "not yet supported by the firmware" in str(exc.value)


def test_invalid_axis_is_rejected(tmp_path):
    printer = _make_printer(
        tmp_path,
        {"encoder my_enc": {"encoder_type": "as5047d", "axis": "q"}},
    )
    config = printer.lookup_object("configfile").getsection("encoder my_enc")
    with pytest.raises(Exception) as exc:
        Encoder(config)
    assert "Invalid axis" in str(exc.value)


def test_supported_sensor_types_are_documented(tmp_path):
    # The removed sensors must not silently reappear
    assert "mt6701" not in SPI_SENSOR_TYPES
    assert "a1333lletr" not in SPI_SENSOR_TYPES
    assert "as5047d" in SPI_SENSOR_TYPES


######################################################################
# Stepper configuration resolution
######################################################################


def test_scale_defaults_to_the_stepper_rotation_distance(tmp_path):
    printer = _make_printer(
        tmp_path,
        {"stepper_x": {"rotation_distance": 40.0}},
    )
    enc = _make_encoder(stepper_name="stepper_x", printer=printer)
    enc._resolve_stepper_config(_FakeConfig(printer))
    assert enc.rotation_distance == pytest.approx(40.0)
    # The scale is the distance of one motor revolution
    assert enc.scale == pytest.approx(40.0)


def test_explicit_scale_wins_over_the_rotation_distance(tmp_path):
    printer = _make_printer(
        tmp_path,
        {"stepper_x": {"rotation_distance": 40.0}},
    )
    enc = _make_encoder(stepper_name="stepper_x", scale=20.0, printer=printer)
    enc._resolve_stepper_config(_FakeConfig(printer))
    assert enc.scale == pytest.approx(20.0)


def test_axis_is_derived_from_the_stepper_name(tmp_path):
    printer = _make_printer(
        tmp_path,
        {
            "stepper_x": {"rotation_distance": 40.0},
            "stepper_y": {"rotation_distance": 40.0},
            "stepper_z": {"rotation_distance": 40.0},
        },
    )
    for stepper, axis in (
        ("stepper_x", "x"),
        ("stepper_y", "y"),
        ("stepper_z", "z"),
    ):
        enc = _make_encoder(stepper_name=stepper, printer=printer)
        enc._resolve_stepper_config(_FakeConfig(printer))
        assert enc.axis == axis


def test_explicit_axis_wins_over_the_stepper_name(tmp_path):
    printer = _make_printer(
        tmp_path,
        {"stepper_x": {"rotation_distance": 40.0}},
    )
    enc = _make_encoder(stepper_name="stepper_x", axis="y", printer=printer)
    enc._resolve_stepper_config(_FakeConfig(printer))
    assert enc.axis == "y"


def test_undeterminable_axis_is_an_error(tmp_path):
    printer = _make_printer(
        tmp_path,
        {"stepper_x1": {"rotation_distance": 40.0}},
    )
    enc = _make_encoder(stepper_name="stepper_x1", printer=printer)
    with pytest.raises(Exception) as exc:
        enc._resolve_stepper_config(_FakeConfig(printer))
    assert "unable to determine the measured axis" in str(exc.value)


def test_a_missing_stepper_section_keeps_the_default_scale(tmp_path):
    # A stepper that does not exist is reported when the printer is ready
    # - the scale falls back to the default until then
    printer = _make_printer(tmp_path, {"printer": {"kinematics": "cartesian"}})
    enc = _make_encoder(stepper_name="stepper_x", printer=printer)
    enc._resolve_stepper_config(_FakeConfig(printer))
    assert enc.rotation_distance == pytest.approx(1.0)
    assert enc.scale == pytest.approx(1.0)


def test_a_standalone_encoder_keeps_its_scale(tmp_path):
    printer = _make_printer(tmp_path, {"printer": {"kinematics": "cartesian"}})
    enc = _make_encoder(stepper_name=None, scale=25.0, printer=printer)
    enc._resolve_stepper_config(_FakeConfig(printer))
    assert enc.scale == pytest.approx(25.0)
    assert enc.axis is None


######################################################################
# Position conversion
######################################################################


def test_raw_to_mm_converts_the_angle():
    enc = _make_encoder(scale=40.0)
    # A half turn is half of the encoder revolution
    assert enc._raw_to_mm(ANGLE_FULL_SCALE / 2) == pytest.approx(20.0)


def test_raw_to_mm_honours_the_invert_flag():
    enc = _make_encoder(scale=40.0, invert=True)
    assert enc._raw_to_mm(ANGLE_FULL_SCALE / 2) == pytest.approx(-20.0)


def test_raw_to_mm_without_a_scale_is_zero():
    enc = _make_encoder(scale=None)
    assert enc._raw_to_mm(12345) == 0.0


def test_raw_to_mm_for_a_quadrature_sensor():
    enc = _make_encoder(scale=40.0, is_quadrature=True, cpr=1000)
    assert enc._raw_to_mm(500) == pytest.approx(20.0)


def test_get_position_mm_uses_the_last_position():
    enc = _make_encoder(scale=40.0, last_position=ANGLE_FULL_SCALE / 2)
    assert enc.get_position_mm() == pytest.approx(20.0)


def test_get_sample_mm_converts_a_sample():
    enc = _make_encoder(scale=40.0)
    sample = (10.0, ANGLE_FULL_SCALE / 2)
    assert enc.get_sample_mm(sample) == pytest.approx(20.0)


def test_get_axis_index_maps_the_axis():
    assert _make_encoder(axis="x").get_axis_index() == 0
    assert _make_encoder(axis="y").get_axis_index() == 1
    assert _make_encoder(axis="z").get_axis_index() == 2
    assert _make_encoder(axis=None).get_axis_index() is None


def test_axis_list_matches_the_cartesian_axes():
    assert AXIS_LIST == ["x", "y", "z"]


######################################################################
# Sample bookkeeping
######################################################################


def test_note_sample_records_the_print_time():
    enc = _make_encoder()
    enc._note_sample((12.5, 4321))
    assert enc.last_sample == (12.5, 4321)
    assert enc.last_position == 4321


def test_get_latest_sample_returns_none_without_a_sample():
    enc = _make_encoder()
    assert enc.get_latest_sample() is None


######################################################################
# Sampling
######################################################################


def test_ensure_sampling_registers_one_internal_client():
    batch = _FakeBatchBulk()
    enc = _make_encoder(batch_bulk=batch)
    enc._ensure_sampling()
    enc._ensure_sampling()
    # The internal client keeps the measurements running even when no web
    # client is attached - it must be registered only once
    assert len(batch.clients) == 1


def test_ensure_sampling_is_a_noop_when_already_active():
    batch = _FakeBatchBulk()
    enc = _make_encoder(batch_bulk=batch, _sampling_active=True)
    enc._ensure_sampling()
    assert batch.clients == []


######################################################################
# Status
######################################################################


def test_get_status_reports_the_configuration():
    class _FakeSensorHelper:
        last_temperature = 42.0

    enc = _make_encoder(
        scale=40.0,
        invert=True,
        axis="x",
        last_position=1000,
        sensor_helper=_FakeSensorHelper(),
    )
    st = enc.get_status()
    assert st["encoder_type"] == "as5047d"
    assert st["scale"] == pytest.approx(40.0)
    assert st["invert"] is True
    assert st["axis"] == "x"
    assert st["position"] == 1000
