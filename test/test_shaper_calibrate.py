# Tests for the input shaper autotune engine
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import math

import numpy as np
import pytest

from klippy.extras import shaper_defs
from klippy.extras.shaper_calibrate import (
    AUTOTUNE_SHAPERS,
    CalibrationData,
    ShaperCalibrate,
)

pytestmark = pytest.mark.unit

SAMPLE_RATE = 2000.0
DURATION = 4.0


@pytest.fixture(scope="module")
def calibrate():
    # A printer of None makes the calculator run in the current process
    return ShaperCalibrate(None)


def _make_spectrum(peak_freq=50.0, n_bins=512, fs=200.0):
    """A synthetic spectrum with a single peak."""
    freqs = np.linspace(0.0, fs, n_bins)
    psd = np.exp(-((freqs - peak_freq) ** 2) / 4.0)
    return freqs, psd


def _make_calibration_data(peak_freq=50.0, n_bins=512, fs=200.0):
    freqs, psd = _make_spectrum(peak_freq, n_bins, fs)
    data = CalibrationData(freqs, psd, psd, psd, psd)
    data.set_numpy(np)
    return data


def _make_accelerometer_data(freq=50.0, duration=DURATION, fs=SAMPLE_RATE):
    """Synthetic accelerometer samples with a single frequency."""
    count = int(duration * fs)
    times = np.arange(count) / fs
    signal = np.sin(2.0 * math.pi * freq * times)
    data = np.zeros((count, 4))
    data[:, 0] = times
    data[:, 1] = signal
    data[:, 2] = signal
    data[:, 3] = signal
    return data


######################################################################
# CalibrationData
######################################################################


def test_calibration_data_get_psd():
    freqs, psd = _make_spectrum()
    data = CalibrationData(freqs, psd, psd * 2, psd * 3, psd * 4)
    data.set_numpy(np)
    assert data.get_psd("x").max() == pytest.approx((psd * 2).max())
    assert data.get_psd("all").max() == pytest.approx(psd.max())


def test_calibration_data_add_data_averages_the_spectra():
    freqs, psd = _make_spectrum()
    # The four spectra are separate arrays
    first = CalibrationData(
        freqs, psd.copy(), psd.copy(), psd.copy(), psd.copy()
    )
    first.set_numpy(np)
    second = CalibrationData(freqs, psd * 3, psd * 3, psd * 3, psd * 3)
    second.set_numpy(np)
    # The spectra are averaged - the data sets are updated in place
    expected = psd.max() * 2
    first.add_data(second)
    assert first.psd_sum.max() == pytest.approx(expected)
    assert first.data_sets == 2


def test_calibration_data_normalize_to_frequencies():
    freqs, psd = _make_spectrum()
    data = CalibrationData(
        freqs, psd.copy(), psd.copy(), psd.copy(), psd.copy()
    )
    data.set_numpy(np)
    data.normalize_to_frequencies()
    assert np.all(np.isfinite(data.psd_sum))
    # The low frequency noise is removed
    assert data.psd_sum[0] < psd[0]


######################################################################
# The window splitting
######################################################################


def test_split_into_windows(calibrate):
    x = np.arange(100.0)
    windows = calibrate._split_into_windows(x, 10, 5)
    assert windows.shape == (10, 19)
    assert windows[0][0] == 0.0
    assert windows[0][1] == 5.0
    assert windows[1][0] == 1.0


def test_split_into_windows_of_a_short_signal(calibrate):
    # A signal that is shorter than the window cannot be split
    x = np.arange(4.0)
    with pytest.raises(ValueError):
        calibrate._split_into_windows(x, 10, 5)


######################################################################
# The power spectral density
######################################################################


def _reference_welch(x, fs, nfft):
    """An independent Welch PSD implementation."""
    window = np.kaiser(nfft, 6.0)
    scale = 1.0 / (window**2).sum()
    overlap = nfft // 2
    step = nfft - overlap
    count = (len(x) - overlap) // step
    result = np.zeros((nfft // 2 + 1, count))
    for i in range(count):
        chunk = x[i * step : i * step + nfft]
        chunk = window * (chunk - chunk.mean())
        spec = np.fft.rfft(chunk, n=nfft)
        result[:, i] = (np.conjugate(spec) * spec).real
    result *= scale / fs
    result[1:-1, :] *= 2.0
    psd = result.real.mean(axis=-1)
    freqs = np.fft.rfftfreq(nfft, 1.0 / fs)
    return freqs, psd


@pytest.mark.parametrize("nfft", [64, 256, 1024])
def test_the_psd_matches_an_independent_implementation(calibrate, nfft):
    fs = 1000.0
    times = np.arange(4096) / fs
    signal = np.sin(2.0 * math.pi * 50.0 * times) + 0.3 * np.random.RandomState(
        0
    ).randn(len(times))
    freqs, psd = calibrate._psd(signal, fs, nfft)
    ref_freqs, ref_psd = _reference_welch(signal, fs, nfft)
    assert np.allclose(freqs, ref_freqs)
    assert np.allclose(psd, ref_psd)


def test_the_psd_finds_a_known_frequency(calibrate):
    fs = 1000.0
    times = np.arange(8192) / fs
    signal = np.sin(2.0 * math.pi * 50.0 * times)
    freqs, psd = calibrate._psd(signal, fs, 1024)
    peak = freqs[np.argmax(psd)]
    assert peak == pytest.approx(50.0, abs=2.0)


######################################################################
# The frequency response
######################################################################


def test_calc_freq_response_of_raw_samples(calibrate):
    data = _make_accelerometer_data(freq=50.0)
    res = calibrate.calc_freq_response(data)
    assert res is not None
    freqs, psd = res.freq_bins, res.psd_sum
    peak = freqs[np.argmax(psd)]
    assert peak == pytest.approx(50.0, abs=2.0)


def test_calc_freq_response_of_a_sample_object(calibrate):
    class _FakeSamples:
        def get_samples(self):
            return _make_accelerometer_data(freq=50.0).tolist()

    res = calibrate.calc_freq_response(_FakeSamples())
    assert res is not None


def test_calc_freq_response_of_no_data(calibrate):
    assert calibrate.calc_freq_response(None) is None


def test_calc_freq_response_of_an_empty_sample_set(calibrate):
    class _FakeSamples:
        def get_samples(self):
            return []

    assert calibrate.calc_freq_response(_FakeSamples()) is None


def test_calc_freq_response_of_a_short_sample_set(calibrate):
    data = _make_accelerometer_data(duration=0.01)
    assert calibrate.calc_freq_response(data) is None


######################################################################
# The shaper response
######################################################################


def test_estimate_shaper_of_a_nulling_shaper(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    freqs = np.array([50.0])
    vals = calibrate._estimate_shaper(shaper, 0.1, freqs)
    # The ZV shaper nulls the vibration at its target frequency
    assert vals[0] < 0.5


def test_estimate_shaper_at_another_frequency(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    freqs = np.array([25.0])
    vals = calibrate._estimate_shaper(shaper, 0.1, freqs)
    assert (
        vals[0] > calibrate._estimate_shaper(shaper, 0.1, np.array([50.0]))[0]
    )


def test_estimate_remaining_vibrations(calibrate):
    data = _make_calibration_data(peak_freq=50.0)
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    vibrations, vals = calibrate._estimate_remaining_vibrations(
        shaper, 0.1, data.freq_bins, data.psd_sum
    )
    # Most of the vibration is removed
    assert 0.0 <= vibrations < 0.5
    assert len(vals) == len(data.freq_bins)


def test_the_smoothing_of_a_shaper(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    smoothing = calibrate._get_shaper_smoothing(shaper)
    assert smoothing > 0.0


def test_a_higher_accel_gives_more_smoothing(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    low = calibrate._get_shaper_smoothing(shaper, accel=1000)
    high = calibrate._get_shaper_smoothing(shaper, accel=10000)
    assert high > low


######################################################################
# The bisection
######################################################################


def test_bisect(calibrate):
    # A function that is true below 0.25
    res = calibrate._bisect(lambda x: x < 0.25)
    assert res == pytest.approx(0.25, abs=1e-6)


def test_bisect_of_a_function_that_is_never_true(calibrate):
    assert calibrate._bisect(lambda x: False) == 0.0


######################################################################
# The maximum acceleration
######################################################################


def test_find_shaper_max_accel(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    max_accel = calibrate.find_shaper_max_accel(shaper, 5.0)
    assert max_accel > 0.0


def test_a_lower_max_accel_gives_a_lower_smoothing_limit(calibrate):
    shaper = shaper_defs.get_zv_shaper(50.0, 0.1)
    max_accel = calibrate.find_shaper_max_accel(shaper, 5.0)
    # The smoothing at the returned acceleration is at the target
    smoothing = calibrate._get_shaper_smoothing(shaper, max_accel, 5.0)
    assert smoothing == pytest.approx(0.12, abs=0.02)


######################################################################
# The shaper fit
######################################################################


def test_fit_shaper_finds_the_peak_frequency(calibrate):
    data = _make_calibration_data(peak_freq=50.0)
    cfg = shaper_defs.get_shaper_cfg("mzv")
    res = calibrate.fit_shaper(
        cfg, data, (30.0, 70.0, 1.0), 0.1, 5.0, None, None, 200.0
    )
    # The peak of the spectrum is at 50Hz
    assert res.freq == pytest.approx(50.0, abs=2.0)
    assert res.name == "mzv"


def test_fit_shaper_reports_the_vibrations(calibrate):
    data = _make_calibration_data(peak_freq=50.0)
    cfg = shaper_defs.get_shaper_cfg("zv")
    res = calibrate.fit_shaper(
        cfg, data, (40.0, 60.0, 2.0), 0.1, 5.0, None, None, 200.0
    )
    assert 0.0 <= res.vibrs <= 1.0
    assert res.smoothing > 0.0
    assert res.score > 0.0


def test_fit_shaper_of_a_flat_spectrum(calibrate):
    freqs = np.linspace(0.0, 200.0, 512)
    psd = np.ones_like(freqs)
    data = CalibrationData(freqs, psd, psd, psd, psd)
    data.set_numpy(np)
    cfg = shaper_defs.get_shaper_cfg("zv")
    res = calibrate.fit_shaper(
        cfg, data, (40.0, 60.0, 5.0), 0.1, 5.0, None, None, 200.0
    )
    assert res is not None


def test_find_best_shaper(calibrate):
    data = _make_calibration_data(peak_freq=50.0)
    best, all_shapers = calibrate.find_best_shaper(
        data,
        shapers=["zv", "mzv"],
        damping_ratio=0.1,
        scv=5.0,
        shaper_freqs=(30.0, 70.0, 2.0),
        max_freq=200.0,
    )
    assert best is not None
    assert best.name in ("zv", "mzv")
    assert len(all_shapers) == 2


def test_find_best_shaper_reports_every_shaper(calibrate):
    data = _make_calibration_data(peak_freq=50.0)
    logged = []
    calibrate.find_best_shaper(
        data,
        shapers=["zv", "mzv"],
        damping_ratio=0.1,
        scv=5.0,
        shaper_freqs=(40.0, 60.0, 5.0),
        max_freq=200.0,
        logger=logged.append,
    )
    # Every shaper reports the fitted frequency and the acceleration limit
    assert len(logged) == 4
    assert any("Fitted shaper" in msg for msg in logged)


######################################################################
# The shaper list
######################################################################


def test_the_autotune_shapers_are_known():
    for name in AUTOTUNE_SHAPERS:
        assert shaper_defs.get_shaper_cfg(name) is not None
