# Tests for the input shaper parameters
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pytest

from klippy.extras.input_shaper import InputShaperParams
from klippy.extras.shaper_defs import DEFAULT_DAMPING_RATIO

pytestmark = pytest.mark.unit


class _FakeConfig:
    """A config section wrapper for the input shaper options."""

    error = Exception

    def __init__(self, **options):
        self._options = options

    def get(self, option, default=None):
        return self._options.get(option, default)

    def getfloat(self, option, default=None, minval=None, maxval=None):
        value = self._options.get(option, default)
        if value is None:
            return None
        value = float(value)
        if minval is not None and value < minval:
            raise self.error("%s is below the minimum" % option)
        if maxval is not None and value > maxval:
            raise self.error("%s is above the maximum" % option)
        return value


class _FakeGCodeCommand:
    error = Exception

    def __init__(self, **params):
        self._params = params

    def get(self, name, default=None):
        return self._params.get(name, default)

    def get_float(self, name, default=None, minval=None, maxval=None):
        value = self._params.get(name, default)
        if value is None:
            return default
        value = float(value)
        if minval is not None and value < minval:
            raise self.error("%s is below the minimum" % name)
        return value


######################################################################
# The parameters
######################################################################


def test_the_default_shaper_type():
    params = InputShaperParams("x", _FakeConfig())
    assert params.shaper_type == "mzv"
    assert params.damping_ratio == pytest.approx(DEFAULT_DAMPING_RATIO)
    assert params.shaper_freq == 0.0


def test_the_axis_specific_options_win():
    config = _FakeConfig(
        shaper_type="zv",
        shaper_type_x="ei",
        damping_ratio_x=0.2,
        shaper_freq_x=50.0,
    )
    params = InputShaperParams("x", config)
    assert params.shaper_type == "ei"
    assert params.damping_ratio == pytest.approx(0.2)
    assert params.shaper_freq == pytest.approx(50.0)


def test_an_unsupported_shaper_type_is_rejected():
    with pytest.raises(Exception) as exc:
        InputShaperParams("x", _FakeConfig(shaper_type_x="nope"))
    assert "Unsupported shaper type" in str(exc.value)


def test_a_damping_ratio_above_the_limit_is_rejected():
    # The EI shaper only supports a damping ratio of up to 0.4
    with pytest.raises(Exception):
        InputShaperParams(
            "x", _FakeConfig(shaper_type_x="ei", damping_ratio_x=0.5)
        )


def test_get_shaper_without_a_frequency():
    params = InputShaperParams("x", _FakeConfig())
    n, A, T = params.get_shaper()
    assert n == 0
    assert A == []
    assert T == []


def test_get_shaper_with_a_frequency():
    params = InputShaperParams("x", _FakeConfig(shaper_freq_x=50.0))
    n, A, T = params.get_shaper()
    assert n == len(A) == len(T)
    assert n > 0


def test_get_status():
    params = InputShaperParams(
        "x", _FakeConfig(shaper_type_x="zv", shaper_freq_x=50.0)
    )
    status = params.get_status()
    assert status["shaper_type"] == "zv"
    assert status["shaper_freq"] == "50.000"
    assert "damping_ratio" in status


######################################################################
# The runtime update
######################################################################


def test_update_changes_the_shaper():
    params = InputShaperParams("x", _FakeConfig(shaper_freq_x=50.0))
    params.update(_FakeGCodeCommand(SHAPER_TYPE_X="zv", SHAPER_FREQ_X=60.0))
    assert params.shaper_type == "zv"
    assert params.shaper_freq == pytest.approx(60.0)


def test_update_uses_the_generic_shaper_type():
    params = InputShaperParams("x", _FakeConfig(shaper_freq_x=50.0))
    params.update(_FakeGCodeCommand(SHAPER_TYPE="mzv"))
    assert params.shaper_type == "mzv"


def test_update_keeps_the_current_values():
    params = InputShaperParams(
        "x", _FakeConfig(shaper_type_x="zv", shaper_freq_x=50.0)
    )
    params.update(_FakeGCodeCommand())
    assert params.shaper_type == "zv"
    assert params.shaper_freq == pytest.approx(50.0)


def test_update_rejects_an_unsupported_shaper_type():
    params = InputShaperParams("x", _FakeConfig(shaper_freq_x=50.0))
    with pytest.raises(Exception) as exc:
        params.update(_FakeGCodeCommand(SHAPER_TYPE_X="nope"))
    assert "Unsupported shaper type" in str(exc.value)


def test_update_rejects_a_damping_ratio_above_the_limit():
    params = InputShaperParams(
        "x", _FakeConfig(shaper_type_x="ei", shaper_freq_x=50.0)
    )
    with pytest.raises(Exception) as exc:
        params.update(_FakeGCodeCommand(DAMPING_RATIO_X=0.5))
    assert "Too high value of damping_ratio" in str(exc.value)


def test_update_rejects_a_negative_damping_ratio():
    params = InputShaperParams("x", _FakeConfig(shaper_freq_x=50.0))
    with pytest.raises(Exception):
        params.update(_FakeGCodeCommand(DAMPING_RATIO_X=-0.1))


def test_update_accepts_a_damping_ratio_below_the_limit():
    params = InputShaperParams(
        "x", _FakeConfig(shaper_type_x="ei", shaper_freq_x=50.0)
    )
    params.update(_FakeGCodeCommand(DAMPING_RATIO_X=0.3))
    assert params.damping_ratio == pytest.approx(0.3)
