# Tests for the input shaper definitions
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math

import pytest

from klippy.extras.shaper_defs import (
    INPUT_SHAPERS,
    ShaperError,
    get_2hump_ei_shaper,
    get_3hump_ei_shaper,
    get_ei_shaper,
    get_mzv_coeffs,
    get_mzv_shaper,
    get_none_shaper,
    get_shaper_cfg,
    get_zv_shaper,
    get_zvd_shaper,
    init_shaper,
)

pytestmark = pytest.mark.unit
FREQS = [10.0, 25.0, 40.0, 60.0, 100.0]


def _all_shapers():
    return [(cfg.name, cfg.init_func) for cfg in INPUT_SHAPERS]


def _response_magnitude(A, T, freq):
    """The magnitude of the shaper response at the given frequency."""
    w = 2.0 * math.pi * freq
    re = sum(a * math.cos(-w * t) for a, t in zip(A, T))
    im = sum(a * math.sin(-w * t) for a, t in zip(A, T))
    return math.sqrt(re * re + im * im)


######################################################################
# The none shaper
######################################################################


def test_the_none_shaper_is_empty():
    A, T = get_none_shaper()
    assert A == []
    assert T == []


######################################################################
# The invariants of every shaper
######################################################################


@pytest.mark.parametrize("name,init_func", _all_shapers())
@pytest.mark.parametrize("freq", FREQS)
def test_the_taps_are_not_negative(name, init_func, freq):
    A, T = init_func(freq, 0.1)
    assert all(a >= 0.0 for a in A)


@pytest.mark.parametrize("name,init_func", _all_shapers())
@pytest.mark.parametrize("freq", FREQS)
def test_the_times_start_at_zero_and_increase(name, init_func, freq):
    A, T = init_func(freq, 0.1)
    assert len(A) == len(T)
    assert T[0] == 0.0
    assert all(T[i] < T[i + 1] for i in range(len(T) - 1))


@pytest.mark.parametrize("name,init_func", _all_shapers())
@pytest.mark.parametrize("freq", FREQS)
def test_the_number_of_taps(name, init_func, freq):
    A, T = init_func(freq, 0.1)
    expected = {
        "zv": 2,
        "mzv": 3,
        "zvd": 3,
        "ei": 3,
        "2hump_ei": 4,
        "3hump_ei": 5,
    }[name]
    assert len(A) == expected


# The shapers that null the vibration completely at their target frequency
NULLING_SHAPERS = ["zv", "mzv", "zvd", "2hump_ei"]
# The shapers that leave a small residual vibration
TOLERANCE_SHAPERS = ["ei", "3hump_ei"]


@pytest.mark.parametrize("name,init_func", _all_shapers())
@pytest.mark.parametrize("freq", FREQS)
def test_the_vibration_is_attenuated_at_the_target_frequency(
    name, init_func, freq
):
    A, T = init_func(freq, 0.1)
    # The shaper has to reduce the vibration at the frequency it was
    # designed for
    assert _response_magnitude(A, T, freq) < 1.0


@pytest.mark.parametrize(
    "name,init_func",
    [(n, f) for n, f in _all_shapers() if n in NULLING_SHAPERS],
)
@pytest.mark.parametrize("freq", FREQS)
def test_the_target_frequency_is_a_minimum_of_the_response(
    name, init_func, freq
):
    A, T = init_func(freq, 0.1)
    at_target = _response_magnitude(A, T, freq)
    assert at_target < _response_magnitude(A, T, freq * 0.9)
    assert at_target < _response_magnitude(A, T, freq * 1.1)


@pytest.mark.parametrize(
    "name,init_func",
    [(n, f) for n, f in _all_shapers() if n in TOLERANCE_SHAPERS],
)
@pytest.mark.parametrize("freq", FREQS)
def test_the_tolerance_shapers_leave_only_a_small_residual(
    name, init_func, freq
):
    A, T = init_func(freq, 0.1)
    # The EI shapers are designed for a vibration tolerance - they leave a
    # small residual instead of a complete null
    assert _response_magnitude(A, T, freq) < 0.1


@pytest.mark.parametrize("name,init_func", _all_shapers())
@pytest.mark.parametrize("freq", FREQS)
def test_a_higher_damping_leaves_more_vibration(name, init_func, freq):
    A1, T1 = init_func(freq, 0.05)
    A2, T2 = init_func(freq, 0.2)
    assert _response_magnitude(A1, T1, freq) < _response_magnitude(A2, T2, freq)


######################################################################
# The individual shapers
######################################################################


def test_zv_shaper():
    A, T = get_zv_shaper(50.0, 0.1)
    df = math.sqrt(1.0 - 0.1**2)
    K = math.exp(-0.1 * math.pi / df)
    assert A == pytest.approx([1.0, K])
    assert T[1] == pytest.approx(0.5 / (50.0 * df))


def test_zvd_shaper():
    A, T = get_zvd_shaper(50.0, 0.1)
    df = math.sqrt(1.0 - 0.1**2)
    K = math.exp(-0.1 * math.pi / df)
    assert A == pytest.approx([1.0, 2.0 * K, K**2])
    assert T[2] == pytest.approx(1.0 / (50.0 * df))


def test_ei_shaper():
    A, T = get_ei_shaper(50.0, 0.1)
    assert len(A) == 3
    assert _response_magnitude(A, T, 50.0) < 0.1


def test_ei_shaper_with_a_custom_tolerance():
    A1, _ = get_ei_shaper(50.0, 0.1)
    A2, _ = get_ei_shaper(50.0, 0.1, v_tol=0.1)
    assert A1 != A2


def test_2hump_ei_shaper():
    A, T = get_2hump_ei_shaper(50.0, 0.1)
    assert len(A) == 4
    assert _response_magnitude(A, T, 50.0) < 0.1


def test_3hump_ei_shaper():
    A, T = get_3hump_ei_shaper(50.0, 0.1)
    assert len(A) == 5
    assert _response_magnitude(A, T, 50.0) < 0.1


def test_mzv_shaper():
    A, T = get_mzv_shaper(50.0, 0.1)
    assert len(A) == 3
    assert _response_magnitude(A, T, 50.0) < 0.1


def test_mzv_shaper_with_more_taps():
    A, T = get_mzv_shaper(50.0, 0.1, n=5)
    assert len(A) == 5
    assert _response_magnitude(A, T, 50.0) < 0.1


def test_mzv_shaper_with_a_tau():
    # The tau parameter is the projected shaper duration - it is
    # converted into the t parameter of the coefficient solver
    A1, _ = get_mzv_shaper(50.0, 0.1, n=3, tau=1.5)
    A2, _ = get_mzv_shaper(50.0, 0.1, n=3)
    assert A1 == pytest.approx(A2)


######################################################################
# MZV coefficients
######################################################################


def test_mzv_coeffs():
    A, T = get_mzv_coeffs(3, 0.75)
    assert len(A) == 3
    assert len(T) == 3
    assert sum(A) == pytest.approx(1.0)


def test_mzv_coeffs_of_too_small_n():
    with pytest.raises(ShaperError):
        get_mzv_coeffs(2, 0.75)


def test_mzv_coeffs_of_a_too_large_t():
    with pytest.raises(ShaperError):
        get_mzv_coeffs(3, 5.0)


######################################################################
# Configuration lookup
######################################################################


def test_get_shaper_cfg():
    cfg = get_shaper_cfg("zv")
    assert cfg is not None
    assert cfg.name == "zv"
    assert cfg.min_freq > 0.0


def test_get_shaper_cfg_with_parameters():
    assert get_shaper_cfg("mzv(3, 0.5)").name == "mzv"


def test_get_shaper_cfg_of_an_unknown_name():
    assert get_shaper_cfg("nope") is None


def test_every_shaper_has_a_min_freq():
    for cfg in INPUT_SHAPERS:
        assert cfg.min_freq > 0.0
        assert 0.0 < cfg.max_damping_ratio <= 1.0


######################################################################
# init_shaper
######################################################################


def test_init_shaper():
    A, T = init_shaper("zv", 50.0, 0.1)
    assert len(A) == 2


def test_init_shaper_with_positional_parameters():
    A, T = init_shaper("mzv(3, 0.5)", 50.0, 0.1)
    assert len(A) == 3


def test_init_shaper_with_named_parameters():
    A, T = init_shaper("ei(v_tol=0.1)", 50.0, 0.1)
    assert len(A) == 3


def test_init_shaper_of_an_unknown_name():
    assert init_shaper("nope", 50.0, 0.1) is None


def test_init_shaper_rejects_mixed_parameters():
    with pytest.raises(ShaperError):
        init_shaper("mzv(3, t=0.5)", 50.0, 0.1)


def test_init_shaper_reports_an_error_through_the_callback():
    def error(msg):
        raise RuntimeError(msg)

    with pytest.raises(RuntimeError) as exc:
        init_shaper("mzv(2, 0.5)", 50.0, 0.1, error=error)
    assert "Failed to initialize shaper" in str(exc.value)
