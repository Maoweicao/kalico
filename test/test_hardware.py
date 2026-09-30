#!/usr/bin/env python3
# Tests for the [hardware] module: host CPU/GPU detection and compute scheduling
#
# These imports require the host Python environment (numpy is a runtime
# dependency); they do not require a GPU or the MCU firmware build.

import os
import sys
import unittest

# Add klippy to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestCPUInfoParsing(unittest.TestCase):
    def test_parse_single_range(self):
        from klippy.extras.hardware import _parse_cpu_range

        self.assertEqual(_parse_cpu_range("0-3"), [0, 1, 2, 3])

    def test_parse_mixed_spec(self):
        from klippy.extras.hardware import _parse_cpu_range

        self.assertEqual(_parse_cpu_range("0,2-4"), [0, 2, 3, 4])

    def test_parse_single_cpu(self):
        from klippy.extras.hardware import _parse_cpu_range

        self.assertEqual(_parse_cpu_range("5"), [5])

    def test_parse_invalid(self):
        from klippy.extras.hardware import _parse_cpu_range

        self.assertEqual(_parse_cpu_range("not-a-range"), [])


class TestComputeBackendSelection(unittest.TestCase):
    """Backend selection must fail safe back to numpy when GPU libs are absent.

    On a plain numpy environment (the typical/CI case) an explicit
    'cuda'/'opencl' request returns numpy when the corresponding library cannot
    be imported.  On machines that do have the GPU libraries installed the
    backend is selected accordingly, so the tests guard for both cases.
    """

    def test_numpy_backend(self):
        from klippy.extras.compute import create_backend

        b = create_backend("numpy")
        self.assertEqual(b.name, "numpy")
        self.assertFalse(b.gpu)
        self.assertEqual(b.get_module().__name__, "numpy")

    def test_cuda_falls_back_without_cupy(self):
        from importlib.util import find_spec

        from klippy.extras.compute import create_backend

        b = create_backend("cuda")
        if find_spec("cupy") is None:
            # No CUDA library installed -> must fall back to numpy.
            self.assertEqual(b.name, "numpy")
        else:
            self.assertIn(b.name, ("cuda", "numpy"))

    def test_opencl_falls_back_without_pyopencl(self):
        from importlib.util import find_spec

        from klippy.extras.compute import create_backend

        b = create_backend("opencl")
        if find_spec("pyopencl") is None:
            # No OpenCL library installed -> must fall back to numpy.
            self.assertEqual(b.name, "numpy")
        else:
            self.assertIn(b.name, ("opencl", "numpy"))

    def test_numpy_backend_does_not_accelerate(self):
        from klippy.extras.compute import create_backend

        b = create_backend("numpy")
        self.assertIsNone(b.accelerated_welch_psd(None, None, 0, 0))


class TestWelchPSD(unittest.TestCase):
    """The shared welch_psd helper must match the classic Welch algorithm."""

    @staticmethod
    def _reference_psd(x, fs, nfft):
        import numpy as np

        window = np.kaiser(nfft, 6.0)
        scale = 1.0 / (window ** 2).sum()
        overlap = nfft // 2
        step = nfft - overlap
        n_windows = (x.shape[-1] - overlap) // step
        shape = (nfft, n_windows)
        strides = (x.strides[-1], step * x.strides[-1])
        wx = np.lib.stride_tricks.as_strided(
            x, shape=shape, strides=strides, writeable=False
        )
        wx = window[:, None] * (wx - np.mean(wx, axis=0))
        result = np.fft.rfft(wx, n=nfft, axis=0)
        result = np.conjugate(result) * result
        result *= scale / fs
        result[1:-1, :] *= 2.0
        return np.fft.rfftfreq(nfft, 1.0 / fs), result.real.mean(axis=-1)

    def test_matches_reference(self):
        import numpy as np

        from klippy.extras.compute import welch_psd

        rng = np.random.default_rng(11)
        for nfft in (64, 256, 1024):
            fs = 2000.0
            x = rng.standard_normal(nfft * 8)
            window = np.kaiser(nfft, 6.0)
            f1, p1 = self._reference_psd(x, fs, nfft)
            f2, p2 = welch_psd(x, window, nfft, fs, np)
            self.assertTrue(np.allclose(f1, f2))
            self.assertTrue(np.allclose(p1, p2))


if __name__ == "__main__":
    unittest.main()
