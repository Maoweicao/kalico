# Tests for the closed loop position controller
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pathlib
import subprocess
import sys

import pytest
from klippy_testing import PrinterShim

from klippy.extras.closed_loop import (
    RATE_WINDOW,
    SUPPORTED_KINEMATICS,
    ClosedLoop,
)

CHELPER_DIR = pathlib.Path(__file__).parent.parent / "klippy" / "chelper"
TEST_DIR = pathlib.Path(__file__).parent / "closed_loop"

AXIS_INDEX = {"x": 0, "y": 1, "z": 2}


######################################################################
# Firmware level test of the re-anchor mechanism
######################################################################


def _build_and_run(tmp_path):
    src = TEST_DIR / "test_reanchor.c"
    exe = tmp_path / (
        "test_reanchor.exe" if sys.platform == "win32" else "test_reanchor"
    )
    cmd = [
        "gcc",
        "-Wall",
        "-O1",
        "-I",
        str(CHELPER_DIR),
        "-o",
        str(exe),
        str(src),
        # The step compressor uses sqrt() - the link fails without libm
        "-lm",
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        # No compiler on this machine - the python level tests still cover
        # the controller logic
        pytest.skip("no C compiler available")
    except subprocess.CalledProcessError as e:
        # A broken build is a real failure - it must not be hidden behind a
        # skip, that is how a broken harness went unnoticed
        pytest.fail(
            "unable to build the reanchor test:\n%s\n%s"
            % (e.stdout or "", e.stderr or "")
        )
    return subprocess.run([str(exe)], capture_output=True, text=True)


def test_reanchor_mechanism(tmp_path):
    # Verify that lowering a stepper reference makes the stepper travel an
    # additional distance and that the step compressor is able to deliver
    # the correction.  This is the mechanism the closed loop controller
    # uses to correct a position error.
    res = _build_and_run(tmp_path)
    print(res.stdout)
    assert res.returncode == 0, res.stdout


def test_reanchor_mechanism_is_actually_executed(tmp_path):
    # Guard against the harness silently skipping itself - the re-anchor
    # limit of the closed loop controller depends on this test really
    # running.
    res = _build_and_run(tmp_path)
    assert "PASSED" in res.stdout, res.stdout
    assert "FAIL" not in res.stdout, res.stdout


######################################################################
# Test doubles
######################################################################


class _FakeMCU:
    def __init__(self, print_time=10.0):
        self._print_time = print_time

    def estimated_print_time(self, systime):
        return self._print_time


class _FakeStepper:
    """A cartesian stepper stand-in."""

    def __init__(self, name="stepper_x", step_dist=0.0125):
        self._name = name
        self._step_dist = step_dist
        self.commanded_pos = 0.0
        self.mcu_pos = 0

    def get_name(self):
        return self._name

    def get_step_dist(self):
        return self._step_dist

    def get_commanded_position(self):
        return self.commanded_pos

    def set_commanded_pos(self, pos):
        self.commanded_pos = pos

    def calc_position_from_coord(self, coord):
        return coord[AXIS_INDEX[self._name.rsplit("_", 1)[-1]]]

    def get_past_mcu_position(self, print_time):
        return self.mcu_pos

    def mcu_to_commanded_position(self, mcu_pos):
        return mcu_pos * self._step_dist


class _FakeKinematics:
    def __init__(self, steppers):
        self._steppers = steppers

    def get_steppers(self):
        return self._steppers

    def calc_position(self, stepper_positions):
        return [stepper_positions[s.get_name()] for s in self._steppers]


class _FakeToolhead:
    def __init__(self, kinematics, position=(0.0, 0.0, 0.0)):
        self._kinematics = kinematics
        self._position = list(position)
        self.pre_step_gen_callbacks = []

    def get_kinematics(self):
        return self._kinematics

    def get_position(self):
        return list(self._position)

    def register_pre_step_gen_callback(self, handler):
        if handler not in self.pre_step_gen_callbacks:
            self.pre_step_gen_callbacks.append(handler)

    def unregister_pre_step_gen_callback(self, handler):
        if handler in self.pre_step_gen_callbacks:
            self.pre_step_gen_callbacks.remove(handler)


class _FakeEncoder:
    """An encoder stand-in reporting a (print_time, raw_position) sample."""

    def __init__(
        self,
        name="enc_x",
        axis="x",
        sample=None,
        stepper=None,
        scale=40.0,
        mcu=None,
    ):
        self.name = name
        self.scale = scale
        self.mcu = mcu or _FakeMCU()
        self._axis = axis
        self._sample = sample
        self._stepper = stepper

    def get_latest_sample(self):
        return self._sample

    def get_sample_mm(self, sample):
        return sample[1] * self.scale / 65536.0

    def get_axis_index(self):
        if self._axis is None:
            return None
        return AXIS_INDEX[self._axis]

    def get_stepper(self):
        return self._stepper

    def get_status(self, eventtime=None):
        return {"position": self._sample[1] if self._sample else 0}


######################################################################
# Controller construction
######################################################################


def _write_config(tmp_path, options, kinematics="cartesian"):
    cfg = tmp_path / "printer.cfg"
    lines = [
        "[printer]",
        "kinematics: %s" % kinematics,
        "",
        "[danger_options]",
        "",
        "[closed_loop]",
    ]
    for option, value in options.items():
        lines.append("%s: %s" % (option, value))
    cfg.write_text("\n".join(lines) + "\n")
    return cfg


def _make_controller(tmp_path, **options):
    """Build a controller from a real config file.

    The config file is generated so the real option names and the real
    defaults of the module are always used.  A renamed option is caught
    here instead of silently falling back to a default.
    """
    cfg = _write_config(tmp_path, options)
    printer = PrinterShim({"config_file": str(cfg)})
    config = printer.load_config()
    cl = ClosedLoop(config.getsection("closed_loop"))
    return printer, cl


def _make_machine(printer, position=(0.0, 0.0, 0.0)):
    """Attach a three axis cartesian machine to the printer."""
    steppers = [
        _FakeStepper("stepper_x"),
        _FakeStepper("stepper_y"),
        _FakeStepper("stepper_z"),
    ]
    toolhead = _FakeToolhead(_FakeKinematics(steppers), position)
    printer.add_object("toolhead", toolhead)
    return steppers, toolhead


def _make_encoder(
    name="enc_x", axis="x", stepper=None, ptime=10.0, mm=10.0, scale=40.0
):
    """An encoder whose sample reports "mm" of axis travel."""
    raw = None if mm is None else int(round(mm * 65536.0 / scale))
    return _FakeEncoder(
        name=name,
        axis=axis,
        sample=None if ptime is None else (ptime, raw),
        stepper=stepper,
        scale=scale,
    )


######################################################################
# PID controller
######################################################################


def test_pid_output_is_clamped(tmp_path):
    printer, cl = _make_controller(tmp_path)
    # A large error must not produce an unbounded correction
    corr = cl._calc_pid("x", 10.0, 0.020)
    assert abs(corr) <= cl.max_correction


def test_pid_integral_is_clamped(tmp_path):
    printer, cl = _make_controller(tmp_path, pid_ki=1.0)
    for _ in range(100):
        corr = cl._calc_pid("x", 1.0, 0.020)
    # The integral must not wind up beyond the correction limit
    assert abs(cl._integral["x"]) <= cl.max_correction / cl.ki
    assert abs(corr) <= cl.max_correction


def test_pid_proportional_response(tmp_path):
    printer, cl = _make_controller(tmp_path, pid_kp=0.5)
    assert cl._calc_pid("x", 0.02, 0.020) == pytest.approx(0.01)


def test_pid_derivative_is_zero_on_the_first_sample(tmp_path):
    printer, cl = _make_controller(
        tmp_path, pid_kp=0.5, pid_kd=1.0, max_correction=100.0
    )
    # The first sample has no derivative - only the proportional part
    assert cl._calc_pid("x", 1.0, 0.020) == pytest.approx(0.5)
    # The second sample adds the derivative of the error
    assert cl._calc_pid("x", 2.0, 0.020) == pytest.approx(0.5 * 2.0 + 50.0)


def test_pid_keeps_per_axis_state(tmp_path):
    printer, cl = _make_controller(tmp_path, pid_kp=0.5, pid_ki=1.0)
    cl._calc_pid("x", 1.0, 0.020)
    cl._calc_pid("y", 1.0, 0.020)
    assert cl._integral["x"] == pytest.approx(cl._integral["y"])
    cl._calc_pid("y", 5.0, 0.020)
    assert cl._integral["x"] != pytest.approx(cl._integral["y"])


def test_pid_without_integral_gain_ignores_the_integral(tmp_path):
    printer, cl = _make_controller(
        tmp_path, pid_kp=0.5, pid_ki=0.0, max_correction=100.0
    )
    first = cl._calc_pid("x", 1.0, 0.020)
    for _ in range(50):
        corr = cl._calc_pid("x", 1.0, 0.020)
    # Without an integral gain the correction stays purely proportional
    assert corr == pytest.approx(first)


def test_pid_integral_limit_scales_with_the_gain(tmp_path):
    printer, cl = _make_controller(tmp_path, pid_ki=2.0, max_correction=0.1)
    for _ in range(1000):
        cl._calc_pid("x", 1.0, 0.020)
    assert abs(cl._integral["x"]) <= cl.max_correction / cl.ki + 1e-12


######################################################################
# Correction limits
######################################################################


def test_correction_limited_to_reanchor_steps(tmp_path):
    printer, cl = _make_controller(tmp_path)
    stepper = _FakeStepper(step_dist=0.0125)
    # The step compressor can only deliver two steps at a time
    corr = cl._limit_correction("x", 0.5, stepper)
    assert abs(corr) <= 2 * 0.0125 + 1e-9
    # A small correction is passed through unchanged
    corr = cl._limit_correction("x", 0.01, stepper)
    assert abs(corr - 0.01) < 1e-9


def test_correction_limited_by_max_correction(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction=0.005)
    stepper = _FakeStepper(step_dist=0.0125)
    corr = cl._limit_correction("x", 0.5, stepper)
    assert abs(corr) <= 0.005 + 1e-9


def test_correction_rate_limit(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction_rate=1.0)
    stepper = _FakeStepper(step_dist=0.0125)
    total = 0.0
    for _ in range(200):
        corr = cl._limit_correction("x", 0.02, stepper)
        total += abs(corr)
    # The rate limit allows at most one second worth of correction
    assert total <= 1.0 + 1e-6


def test_correction_preserves_the_sign(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction=0.05)
    stepper = _FakeStepper(step_dist=0.0125)
    corr = cl._limit_correction("x", -0.5, stepper)
    assert corr < 0.0
    assert abs(corr) <= 2 * 0.0125 + 1e-9


def test_correction_rate_limit_returns_zero_when_exhausted(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction_rate=1.0)
    stepper = _FakeStepper(step_dist=0.0125)
    total = 0.0
    for _ in range(500):
        total += abs(cl._limit_correction("x", 0.02, stepper))
    # Once the budget of the window is used up nothing more is applied
    assert cl._limit_correction("x", 0.02, stepper) == 0.0
    assert total <= 1.0 + 1e-6


def test_correction_rate_window_slides(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction_rate=1.0)
    stepper = _FakeStepper(step_dist=0.0125)
    reactor = printer.get_reactor()
    for _ in range(100):
        cl._limit_correction("x", 0.02, stepper)
    assert cl._limit_correction("x", 0.02, stepper) == 0.0
    # Once the window has passed the budget is available again
    reactor.advance(RATE_WINDOW + 0.1)
    assert cl._limit_correction("x", 0.02, stepper) == pytest.approx(0.02)


def test_correction_rate_limit_is_per_axis(tmp_path):
    printer, cl = _make_controller(tmp_path, max_correction_rate=1.0)
    stepper = _FakeStepper(step_dist=0.0125)
    for _ in range(100):
        cl._limit_correction("x", 0.02, stepper)
    # The "y" axis has its own budget
    assert cl._limit_correction("y", 0.02, stepper) == pytest.approx(0.02)


######################################################################
# Error evaluation
######################################################################


def test_calc_error_uses_the_commanded_position(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    # 8000 steps of 0.0125mm is a commanded position of 100mm
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder

    error, ptime, age = cl._calc_error(encoder, 10.0)
    # expected (100mm) - actual (10mm)
    assert error == pytest.approx(90.0)
    assert ptime == 10.0
    assert age == pytest.approx(0.0)


def test_calc_error_rejects_a_missing_sample(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(ptime=None, stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    assert cl._calc_error(encoder, 10.0) is None


def test_calc_error_rejects_a_sample_from_the_future(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(ptime=11.0, stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    # A negative age means the sample was taken in a different time base
    assert cl._calc_error(encoder, 10.0) is None


def test_calc_error_rejects_a_stale_sample(tmp_path):
    printer, cl = _make_controller(tmp_path, max_sample_age=0.25)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(ptime=9.0, stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    assert cl._calc_error(encoder, 10.0) is None


def test_calc_error_accepts_a_sample_at_the_age_limit(tmp_path):
    printer, cl = _make_controller(tmp_path, max_sample_age=0.25)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(ptime=9.75, stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    assert cl._calc_error(encoder, 10.0) is not None


def test_calc_error_rejects_an_encoder_without_an_axis(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(axis=None, stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    assert cl._calc_error(encoder, 10.0) is None


def test_calc_error_subtracts_the_accumulated_lead(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._lead["enc_x"] = 5.0
    # The commanded position of the machine includes the extra steps that
    # the correction injected - they have to be removed
    error, _, _ = cl._calc_error(encoder, 10.0)
    assert error == pytest.approx(85.0)


def test_calc_error_applies_the_zero_offset(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._zero_offset["enc_x"] = 90.0
    # The offset cancels the difference between the two positions
    error, _, _ = cl._calc_error(encoder, 10.0)
    assert error == pytest.approx(0.0)


######################################################################
# Update loop
######################################################################


def test_update_corrections_is_a_noop_when_disabled(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=0)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    assert "enc_x" not in cl._last_error


def test_update_corrections_skips_an_encoder_without_a_stepper(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1)
    encoder = _make_encoder(stepper=None)
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    assert "enc_x" not in cl._last_error


def test_update_corrections_records_the_error(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    assert cl._last_error["enc_x"] == pytest.approx(90.0)
    assert cl._sample_time["enc_x"] == pytest.approx(10.0)


def test_update_corrections_does_not_correct_an_uncalibrated_axis(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=1)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    # Without a calibration the measured position is not comparable
    assert "enc_x" not in cl._last_correction
    assert cl._pending == {}


def test_update_corrections_does_not_correct_without_calibration_support(
    tmp_path,
):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=1)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._zero_offset["enc_x"] = 0.0
    cl._kinematics_supported = False
    cl._update_corrections(10.0)
    assert "enc_x" not in cl._last_correction


def test_update_corrections_applies_a_correction(tmp_path):
    printer, cl = _make_controller(
        tmp_path, enable=1, enable_correction=1, pid_kp=0.5
    )
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._zero_offset["enc_x"] = 0.0
    cl._kinematics_supported = True
    cl._update_corrections(10.0)
    # The error is 90mm but the correction is limited to the number of
    # steps that the step compressor is able to deliver in one re-anchor
    assert cl._last_correction["enc_x"] == pytest.approx(
        cl.max_reanchor_steps * steppers[0].get_step_dist()
    )
    assert cl._pending["enc_x"][0] == pytest.approx(
        cl.max_reanchor_steps * steppers[0].get_step_dist()
    )


######################################################################
# Error handling
######################################################################


def test_handle_error_shuts_down(tmp_path):
    printer, cl = _make_controller(tmp_path, action="shutdown")
    cl._handle_error("enc_x", 1.0)
    assert len(printer.shutdowns) == 1
    assert "enc_x" in printer.shutdowns[0]


def test_handle_error_only_triggers_once(tmp_path):
    printer, cl = _make_controller(tmp_path, action="shutdown")
    cl._handle_error("enc_x", 1.0)
    cl._handle_error("enc_x", 1.0)
    assert len(printer.shutdowns) == 1


def test_handle_error_logs_only(tmp_path):
    printer, cl = _make_controller(tmp_path, action="log")
    cl._handle_error("enc_x", 1.0)
    assert printer.shutdowns == []


def test_handle_error_pause_without_a_pause_resume_object(tmp_path):
    printer, cl = _make_controller(tmp_path, action="pause")
    cl._handle_error("enc_x", 1.0)
    assert printer.shutdowns == []


def test_update_corrections_trips_on_the_error_threshold(tmp_path):
    printer, cl = _make_controller(
        tmp_path, enable=1, error_threshold=0.05, action="shutdown"
    )
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    assert len(printer.shutdowns) == 1


def test_update_corrections_does_not_trip_below_the_threshold(tmp_path):
    printer, cl = _make_controller(
        tmp_path, enable=1, error_threshold=1000.0, action="shutdown"
    )
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._update_corrections(10.0)
    assert printer.shutdowns == []


######################################################################
# State handling
######################################################################


def test_set_position_resets_the_controller_state(tmp_path):
    printer, cl = _make_controller(tmp_path)
    cl._integral["enc_x"] = 1.0
    cl._last_error["enc_x"] = 1.0
    cl._prev_error["enc_x"] = 1.0
    cl._lead["enc_x"] = 1.0
    cl._pending["enc_x"] = (1.0, 0.0, 0.0)
    # A homing move re-bases the stepper references
    cl._handle_set_position()
    assert cl._integral == {}
    assert cl._last_error == {}
    assert cl._prev_error == {}
    assert cl._lead == {}
    assert cl._pending == {}


def test_check_kinematics_rejects_unsupported_kinematics(tmp_path):
    cfg = _write_config(tmp_path, {}, kinematics="delta")
    printer = PrinterShim({"config_file": str(cfg)})
    config = printer.load_config()
    cl = ClosedLoop(config.getsection("closed_loop"))
    assert cl._check_kinematics() is False


def test_check_kinematics_accepts_cartesian(tmp_path):
    printer, cl = _make_controller(tmp_path)
    assert cl._check_kinematics() is True
    assert "cartesian" in SUPPORTED_KINEMATICS


######################################################################
# Correction application
######################################################################


def test_pre_step_gen_applies_a_pending_correction(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=1)
    steppers, toolhead = _make_machine(printer)
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    cl._kinematics_supported = True
    cl._pending["enc_x"] = (0.1, 0.0, 0.0)
    cl._pre_step_gen_callback(10.0)
    # The reference of the x stepper is lowered so that the stepper
    # travels an additional 0.1mm
    assert steppers[0].commanded_pos == pytest.approx(-0.1)
    assert steppers[1].commanded_pos == pytest.approx(0.0)
    assert cl._lead["enc_x"] == pytest.approx(0.1)
    assert cl._pending == {}


def test_pre_step_gen_handles_two_axes(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=1)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_y"] = _make_encoder("enc_y", "y", stepper=steppers[1])
    cl._kinematics_supported = True
    cl._pending["enc_x"] = (0.1, 0.0, 0.0)
    cl._pending["enc_y"] = (0.0, 0.2, 0.0)
    cl._pre_step_gen_callback(10.0)
    assert steppers[0].commanded_pos == pytest.approx(-0.1)
    assert steppers[1].commanded_pos == pytest.approx(-0.2)
    assert steppers[2].commanded_pos == pytest.approx(0.0)
    assert cl._lead["enc_x"] == pytest.approx(0.1)
    assert cl._lead["enc_y"] == pytest.approx(0.2)


def test_pre_step_gen_drops_the_correction_when_disabled(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=0)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=steppers[0])
    cl._kinematics_supported = True
    cl._pending["enc_x"] = (0.1, 0.0, 0.0)
    cl._pre_step_gen_callback(10.0)
    assert steppers[0].commanded_pos == pytest.approx(0.0)
    assert cl._lead == {}


def test_pre_step_gen_drops_the_correction_on_unsupported_kinematics(
    tmp_path,
):
    printer, cl = _make_controller(tmp_path, enable=1, enable_correction=1)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=steppers[0])
    cl._kinematics_supported = False
    cl._pending["enc_x"] = (0.1, 0.0, 0.0)
    cl._pre_step_gen_callback(10.0)
    assert steppers[0].commanded_pos == pytest.approx(0.0)


def test_ready_registers_the_pre_step_gen_callback(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=1)
    steppers, toolhead = _make_machine(printer)
    # The callback has to run before the steppers of a flush generate their
    # steps - that ordering is what makes the correction work
    printer.send_event("klippy:ready")
    assert cl._pre_step_gen_cb in toolhead.pre_step_gen_callbacks


######################################################################
# Calibration
######################################################################


def test_calibrate_requires_an_axis(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    printer.call("CLOSED_LOOP_CALIBRATE")
    assert any("Usage" in r for r in printer.lookup_object("gcode").responses)


def test_calibrate_rejects_an_unknown_encoder(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    printer.call("CLOSED_LOOP_CALIBRATE AXIS=nope")
    assert any(
        "Unknown encoder" in r for r in printer.lookup_object("gcode").responses
    )


def test_calibrate_rejects_an_encoder_without_a_stepper(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=None)
    printer.call("CLOSED_LOOP_CALIBRATE AXIS=enc_x")
    assert any(
        "no associated stepper" in r
        for r in printer.lookup_object("gcode").responses
    )


def test_calibrate_rejects_an_encoder_without_a_sample(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(ptime=None, stepper=steppers[0])
    printer.call("CLOSED_LOOP_CALIBRATE AXIS=enc_x")
    assert any(
        "no measurement available" in r
        for r in printer.lookup_object("gcode").responses
    )


def test_calibrate_sets_the_zero_offset(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    printer.call("CLOSED_LOOP_CALIBRATE AXIS=enc_x")
    # The encoder reports 10mm while the machine is at 100mm
    assert cl._zero_offset["enc_x"] == pytest.approx(90.0)
    assert cl._last_error["enc_x"] == pytest.approx(0.0)


def test_calibrate_zeroes_the_error(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    steppers[0].mcu_pos = 8000
    encoder = _make_encoder(stepper=steppers[0])
    cl.encoders["enc_x"] = encoder
    printer.call("CLOSED_LOOP_CALIBRATE AXIS=enc_x")
    error, _, _ = cl._calc_error(encoder, 10.0)
    assert error == pytest.approx(0.0)


######################################################################
# Commands and status
######################################################################


def test_enable_and_disable_commands(tmp_path):
    printer, cl = _make_controller(tmp_path, enable=0)
    printer.call("CLOSED_LOOP_ENABLE")
    assert cl.enabled is True
    printer.call("CLOSED_LOOP_DISABLE")
    assert cl.enabled is False


def test_status_command_reports_the_axis(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=steppers[0])
    printer.call("CLOSED_LOOP_STATUS")
    responses = printer.lookup_object("gcode").responses
    assert any("enc_x" in r for r in responses)


def test_status_command_without_an_encoder(tmp_path):
    printer, cl = _make_controller(tmp_path)
    printer.call("CLOSED_LOOP_STATUS")
    responses = printer.lookup_object("gcode").responses
    assert any("No encoders registered" in r for r in responses)


def test_get_status_reports_the_encoder_fields(tmp_path):
    printer, cl = _make_controller(tmp_path)
    steppers, toolhead = _make_machine(printer)
    cl.encoders["enc_x"] = _make_encoder(stepper=steppers[0])
    cl._zero_offset["enc_x"] = 1.5
    cl._last_error["enc_x"] = 0.25
    cl._last_correction["enc_x"] = 0.1
    cl._sample_age["enc_x"] = 0.01
    cl._lead["enc_x"] = 0.2
    st = cl.get_status()
    assert st["enc_x"]["zero_offset"] == pytest.approx(1.5)
    assert st["enc_x"]["error"] == pytest.approx(0.25)
    assert st["enc_x"]["correction"] == pytest.approx(0.1)
    assert st["enc_x"]["sample_age"] == pytest.approx(0.01)
    assert st["enc_x"]["lead"] == pytest.approx(0.2)
