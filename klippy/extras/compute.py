# Compute backend abstraction for Kalico
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Several offline, compute-heavy parts of Kalico (input-shaper calibration,
# frequency-response analysis) use NumPy.  When a suitable GPU is present the
# [hardware] module may select a GPU compute backend here:
#
#   * numpy  - the stock CPU backend (always available, default)
#   * cupy   - NVIDIA CUDA; a near drop-in numpy replacement that runs on the
#              GPU.  Requires the optional `cupy` package.
#   * opencl - AMD/Intel GPU via pyopencl; accelerates the shaper Welch-PSD
#              FFT hotspot, falling back to numpy for everything else.
#
# All GPU backends are optional and fail safe (back to numpy) so Kalico always
# runs on a plain numpy environment.
import logging


def welch_psd(x, window, nfft, fs, module):
    """Compute a Welch power spectral density.

    x      : 1D real samples (length N)
    window : 1D window of length nfft
    nfft   : FFT size
    fs     : sampling frequency
    module : a numpy-compatible array module (numpy or cupy)

    Must return numpy arrays.  When `module` is a GPU module (cupy) the caller
    is responsible for transferring the result back to the host first.
    With numpy, returns (freqs, psd) directly.
    """
    import numpy as np

    w = module.asarray(window)
    overlap = nfft // 2
    step = nfft - overlap
    n_windows = (len(x) - overlap) // step
    if n_windows <= 0:
        raise ValueError("Too few samples for the requested FFT size")
    seg_size = n_windows * step + overlap
    segs = module.asarray(x[:seg_size])
    idx = (module.arange(nfft)[:, None]
           + module.arange(n_windows)[None, :] * step)
    windows = segs[idx]
    windows = w[:, None] * (windows - module.mean(windows, axis=0))
    result = module.fft.rfft(windows, n=nfft, axis=0)
    psd = (module.conj(result) * result).real.mean(axis=-1)
    psd *= 1.0 / (w ** 2).sum() / fs
    psd[1:-1] *= 2.0
    freqs = module.fft.rfftfreq(nfft, 1.0 / fs)
    if module is np:
        return np.asarray(freqs), np.asarray(psd)
    return freqs.get(), psd.get()


class Backend:
    """Base numerical backend.

    `module` is a numpy-compatible array module (numpy or cupy).  `name` is a
    short string used for status/reporting.  `gpu` is True when the backend
    actually offloads work to a GPU.
    """
    name = "numpy"
    gpu = False

    def get_module(self):
        return self.module

    def accelerated_welch_psd(self, x, window, nfft, fs):
        """GPU-accelerated Welch PSD, or None to fall back to numpy.

        x      : 1D real samples (shape (N,))
        window : 1D window of length nfft
        nfft   : FFT size (power of two)
        fs     : sampling frequency

        Returns an (freqs, psd) tuple of numpy arrays, or None when the backend
        is CPU-only or the acceleration could not run.
        """
        return None


class NumpyBackend(Backend):
    name = "numpy"
    gpu = False

    def __init__(self):
        import numpy

        self.module = numpy


class CupyBackend(Backend):
    name = "cuda"
    gpu = True

    def __init__(self):
        import cupy  # noqa: F401
        import cupy as np

        self.module = np

    def accelerated_welch_psd(self, x, window, nfft, fs):
        """Welch PSD computed with CuPy (a near drop-in for numpy on GPU)."""
        try:
            return welch_psd(x, window, nfft, fs, self.module)
        except Exception:
            logging.debug(
                "CuPy accelerated Welch PSD failed; using numpy",
                exc_info=True,
            )
            return None


class OpenCLBackend(Backend):
    """AMD/Intel GPU backend via pyopencl.

    NumPy still drives the non-critical parts; only the dominant Welch PSD
    hotspot is offloaded to the GPU with a power-of-two radix-2 FFT.
    """
    name = "opencl"
    gpu = True

    def __init__(self):
        import numpy
        import pyopencl  # noqa: F401  (raise ImportError if unavailable)

        self.module = numpy
        self._program = None
        self._ctx = None
        self._queue = None

    def _ensure_context(self):
        if self._ctx is not None:
            return True
        import pyopencl as cl

        gpu_devices = []
        for plat in cl.get_platforms():
            for dev in plat.get_devices(device_type=cl.device_type.GPU):
                gpu_devices.append(dev)
        if not gpu_devices:
            return False
        self._ctx = cl.Context(gpu_devices)
        self._queue = cl.CommandQueue(self._ctx, gpu_devices[0])
        try:
            self._program = cl.Program(self._ctx, _OPENCL_KERNEL).build()
        except Exception:
            logging.warning(
                "OpenCL kernel build failed; OpenCL acceleration disabled",
                exc_info=True,
            )
            self._program = None
        return self._program is not None

    def accelerated_welch_psd(self, x, window, nfft, fs):
        try:
            import numpy as np
            from pyopencl import array as cl_array

            if not self._ensure_context():
                return None
            if self._program is None:
                return None
            if nfft & (nfft - 1):
                # only power-of-two FFT sizes supported
                return None
            overlap = nfft // 2
            step = nfft - overlap
            n_windows = (len(x) - overlap) // step
            half = nfft // 2
            if n_windows <= 0:
                return None

            x32 = np.ascontiguousarray(x, dtype=np.float32)
            w = np.ascontiguousarray(window, dtype=np.float32)
            offsets = np.arange(n_windows, dtype=np.int32) * step
            # Per-window means over the windowed segment (host reduction), so
            # the fill kernel can detrend each window (matches the numpy path).
            means = np.empty(n_windows, dtype=np.float32)
            for k in range(n_windows):
                means[k] = x32[offsets[k]: offsets[k] + nfft].mean()

            full = cl_array.to_device(self._queue, x32)
            win_buf = cl_array.to_device(self._queue, w)
            off_buf = cl_array.to_device(self._queue, offsets)
            mean_buf = cl_array.to_device(self._queue, means)
            spectrum = cl_array.empty(
                self._queue, (n_windows * nfft * 2,), np.float32
            )

            fill = self._program.fill_windows
            fftk = self._program.fft_power

            wgs = 256 if nfft >= 256 else nfft
            fill(self._queue, (n_windows, nfft), (1, wgs),
                 full, win_buf, off_buf, mean_buf, spectrum,
                 np.int32(nfft))
            fftk(self._queue, (n_windows,), (1,), spectrum, np.int32(nfft))
            self._queue.finish()

            power = spectrum.get().reshape(n_windows, nfft, 2)
            # One-sided power spectrum from a full-size FFT of real input.
            p2 = power[:, : half + 1, 0] ** 2 + power[:, : half + 1, 1] ** 2
            psd = p2.mean(axis=0)
            psd *= 1.0 / (w ** 2).sum() / fs
            if half > 1:
                psd[1:half] *= 2.0
            freqs = np.fft.rfftfreq(nfft, 1.0 / fs)
            return freqs, psd
        except Exception:
            logging.debug(
                "OpenCL accelerated Welch PSD failed; using numpy",
                exc_info=True,
            )
            return None


_OPENCL_KERNEL = r"""
// Window-and-gather: one work-item per (window, sample) pair.  Each window is a
// strided slice of the raw signal, mean-detrended and windowed.  Output is a
// per-window complex buffer (imag part zero) laid out as [n_windows][nfft][2].
__kernel void fill_windows(
    __global const float* x,
    __global const float* window,
    __global const int* offsets,
    __global const float* means,
    __global float2* spectrum,
    const int n)
{
    int nw = get_global_id(0);
    int i  = get_global_id(1);
    float val = x[offsets[nw] + i] - means[nw];
    spectrum[(size_t)nw * n + i] = (float2)(val * window[i], 0.f);
}

// Iterative radix-2 Cooley-Tukey FFT in place, one work-item per window.
// The global work-groups carry a scalar sum reduction for |X|^2 not needed
// here; we instead write the full complex spectrum and let the host average.
__kernel void fft_power(__global float2* spectrum, const int n)
{
    int nw = get_global_id(0);

    // Bit-reversal permutation, in place.
    int bits = 0;
    int t = n;
    while (t > 1) { t >>= 1; bits++; }
    for (int i = 0; i < n; i++) {
        int rev = 0;
        int j = i;
        for (int b = 0; b < bits; b++) { rev = (rev << 1) | (j & 1); j >>= 1; }
        if (rev > i) {
            float2 tmp = spectrum[(size_t)nw * n + i];
            spectrum[(size_t)nw * n + i] = spectrum[(size_t)nw * n + rev];
            spectrum[(size_t)nw * n + rev] = tmp;
        }
    }

    // Butterfly stages.
    for (int s = 2; s <= n; s <<= 1) {
        int half = s >> 1;
        for (int start = 0; start < n; start += s) {
            for (int k = 0; k < half; k++) {
                float ang = -6.28318530718f * (float)k / (float)s;
                float2 w = (float2)(cos(ang), sin(ang));
                int i0 = start + k;
                int i1 = start + k + half;
                float2 u = spectrum[(size_t)nw * n + i0];
                float2 v = spectrum[(size_t)nw * n + i1];
                float2 t = (float2)(v.x * w.x - v.y * w.y,
                                    v.x * w.y + v.y * w.x);
                spectrum[(size_t)nw * n + i0] = (float2)(u.x + t.x, u.y + t.y);
                spectrum[(size_t)nw * n + i1] = (float2)(u.x - t.x, u.y - t.y);
            }
        }
    }
}
"""


def create_backend(name):
    """Instantiate the named backend, falling back to numpy on any failure."""
    try:
        if name == "cuda":
            return CupyBackend()
        if name == "opencl":
            return OpenCLBackend()
    except Exception:
        logging.warning(
            "GPU backend '%s' requested but unavailable; using numpy",
            name,
            exc_info=True,
        )
    return NumpyBackend()
