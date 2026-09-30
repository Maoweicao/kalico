# Host hardware detection and compute scheduling
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The [hardware] module detects host CPU and GPU capabilities at startup and
# provides helpers that let Python computations (input-shaper calibration,
# coordinate descent, etc.) run on user-selected CPU cores and, when a GPU is
# available, accelerate numeric work on that GPU.
#
# All behaviour is off by default so existing installations are unaffected.
import logging
import os
import subprocess

from . import compute

######################################################################
# CPU detection
######################################################################

def _read_sys_string(path):
    try:
        with open(path, "r") as f:
            return f.read().strip()
    except (IOError, OSError):
        return None


def _read_proc_cpuinfo():
    try:
        with open("/proc/cpuinfo", "r") as f:
            return f.read()
    except (IOError, OSError):
        return None


def _detect_cpu():
    """Return a dict describing the host CPU(s)."""
    info = {"count": 0, "model": "?", "arch": "?", "online": []}
    try:
        info["arch"] = os.uname().machine
    except (AttributeError, OSError):
        pass
    online = _read_sys_string("/sys/devices/system/cpu/online")
    if online:
        info["online"] = _parse_cpu_range(online)
    if info["online"]:
        info["count"] = len(info["online"])
    data = _read_proc_cpuinfo()
    if data:
        lines = [l.split(":", 1) for l in data.split("\n")]
        lines = [(l[0].strip(), l[1].strip()) for l in lines if len(l) == 2]
        model = dict(lines).get("model name")
        if model:
            info["model"] = model
        else:
            # ARM systems usually do not expose 'model name' - fall back to
            # the first 'model' or 'Processor' entry.
            info["model"] = dict(lines).get("model", "?")
        if not info["count"]:
            info["count"] = [k for k, v in lines].count("processor")
            info["online"] = list(range(info["count"]))
    if not info["count"]:
        # Final fallback to the OS query
        info["count"] = os.cpu_count() or 0
        info["online"] = list(range(info["count"]))
    return info


def _parse_cpu_range(spec):
    """Parse a Linux 'cpu online' spec like '0-3' or '0,2-4' into a list."""
    cpus = []
    try:
        parts = spec.split(",")
        for part in parts:
            part = part.strip()
            if "-" in part:
                start, end = part.split("-", 1)
                cpus.extend(range(int(start), int(end) + 1))
            elif part:
                cpus.append(int(part))
    except ValueError:
        return []
    return cpus


def _has_sched_setaffinity():
    return hasattr(os, "sched_setaffinity")


######################################################################
# GPU detection (CuPy / OpenCL)
######################################################################

def _run_cmd(args):
    """Run a command, returning (retcode, stdout, stderr) or None on failure."""
    try:
        proc = subprocess.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        out, err = proc.communicate(timeout=5)
        return (
            proc.returncode,
            out.decode(errors="replace").strip(),
            err.decode(errors="replace").strip(),
        )
    except (OSError, subprocess.SubprocessError):
        return None


def _detect_cuda_nvidia():
    """Detect an NVIDIA GPU via nvidia-smi and/or cupy."""
    gpu = None
    res = _run_cmd(
        [
            "nvidia-smi",
            "--query-gpu=name,memory.total,driver_version",
            "--format=csv,noheader,nounits",
        ]
    )
    if res and res[0] == 0:
        lines = [l.split(",") for l in res[1].split("\n") if l.strip()]
        if lines:
            row = [c.strip() for c in lines[0]]
            gpu = {
                "vendor": "NVIDIA",
                "model": row[0] if row else "?",
                "memory_bytes": int(row[1]) * 1024 * 1024 if len(row) > 1
                and row[1].isdigit() else None,
                "driver": row[2] if len(row) > 2 else "?",
            }
    return gpu


def _detect_opencl():
    """Detect an OpenCL GPU via pyopencl (AMD/Intel etc)."""
    try:
        import pyopencl  # noqa: F401
    except ImportError:
        return None
    try:
        import pyopencl as cl

        platform = None
        gpu_model = None
        for plat in cl.get_platforms():
            for dev in plat.get_devices(device_type=cl.device_type.GPU):
                platform = plat.name
                gpu_model = dev.name.strip()
                break
            if gpu_model:
                break
        if not gpu_model:
            return None
        return {
            "vendor": platform or "OpenCL",
            "model": gpu_model,
        }
    except Exception:
        logging.debug(
            "OpenCL GPU detection failed", exc_info=True
        )
        return None


def _detect_gpu():
    """Return a dict describing the best available GPU, or None."""
    # Prefer NVIDIA/CUDA first, then OpenCL
    gpu = _detect_cuda_nvidia()
    if gpu is not None:
        gpu["api"] = "cuda"
        return gpu
    gpu = _detect_opencl()
    if gpu is not None:
        gpu["api"] = "opencl"
        return gpu
    return None


######################################################################
# The [hardware] module
######################################################################


class Hardware:
    def __init__(self, config):
        self.printer = config.get_printer()
        # --- CPU detection --------------------------------
        self.cpu_info = _detect_cpu()
        # --- Affinity configuration (Linux only) ----------
        # List of CPUs to pin background calibration processes to.
        self.background_cpu_affinity = config.getintlist(
            "cpu_affinity_background", None
        )
        # List of CPUs to pin the Klipper main process to (optional).
        self.main_cpu_affinity = config.getintlist(
            "cpu_affinity_main", None
        )
        self._affinity_supported = _has_sched_setaffinity()
        if not self._affinity_supported and (
            self.background_cpu_affinity or self.main_cpu_affinity
        ):
            logging.warning(
                "CPU affinity requested in [hardware] but this platform "
                "does not support os.sched_setaffinity; ignoring affinity "
                "settings"
            )
        # Apply main-process affinity if requested.
        if (
            self._affinity_supported
            and self.main_cpu_affinity
        ):
            self.apply_process_affinity(self.main_cpu_affinity)
        # --- GPU backend configuration --------------------
        backend_choices = {
            "auto": "auto",
            "cuda": "cuda",
            "opencl": "opencl",
            "numpy": "numpy",
            "cpu": "numpy",
            "none": "numpy",
        }
        self.backend_cfg = config.getchoice(
            "gpu_backend", backend_choices, "auto"
        )
        self.gpu_accelerate_calibration = config.getboolean(
            "gpu_accelerate_calibration", True
        )
        # --- GPU detection --------------------------------
        self.gpu = _detect_gpu()
        self.compute_backend = self._select_backend()
        self._log_summary()

    def _select_backend(self):
        """Pick the numerical backend based on config + detection."""
        # 'auto' prefers CUDA, then OpenCL, then numpy.
        if self.backend_cfg == "cuda":
            return compute.create_backend("cuda")
        if self.backend_cfg == "opencl":
            return compute.create_backend("opencl")
        if self.backend_cfg == "numpy":
            return compute.create_backend("numpy")

        # auto path
        if self.gpu is not None and self.gpu["api"] == "cuda":
            return compute.create_backend("cuda")
        if self.gpu is not None and self.gpu["api"] == "opencl":
            return compute.create_backend("opencl")
        return compute.create_backend("numpy")

    def _log_summary(self):
        cpu = self.cpu_info
        summary = [
            "Hardware report: %d CPUs (%s) %s"
            % (cpu["count"], cpu["arch"], cpu["model"]),
        ]
        if self._affinity_supported and self.background_cpu_affinity:
            summary.append(
                "Background calibration pinned to CPU(s): %s"
                % (", ".join(map(str, self.background_cpu_affinity)),)
            )
        if (
            self._affinity_supported
            and self.main_cpu_affinity
        ):
            summary.append(
                "Main process pinned to CPU(s): %s"
                % (", ".join(map(str, self.main_cpu_affinity)),)
            )
        if self.gpu is not None:
            summary.append(
                "GPU detected: %s %s (API: %s)"
                % (self.gpu["vendor"], self.gpu["model"], self.gpu["api"])
            )
        else:
            summary.append("No GPU detected; using numpy backend")
        summary.append(
            "Active compute backend: %s" % (self.compute_backend.name,)
        )
        logging.info("\n".join(summary))

    # --- Affinity helpers (callable from forked workers) -----

    def apply_process_affinity(self, cpu_list=None):
        """Pin the *calling* process to the given CPU(s).

        The background workers (coordinate descent / shaper calibration) are
        forked off this process, so they call this from inside their wrapper
        to move themselves onto the configured cores.
        """
        if not self._affinity_supported:
            return False
        cpus = set(cpu_list) if cpu_list is not None else set()
        if not cpus and self.background_cpu_affinity:
            cpus = set(self.background_cpu_affinity)
        if not cpus:
            return False
        try:
            os.sched_setaffinity(0, cpus)
            return True
        except (OSError, ValueError) as e:
            logging.warning(
                "Failed to set CPU affinity to %s: %s",
                sorted(cpus),
                e,
            )
            return False

    def get_backend(self):
        return self.compute_backend

    def get_status(self, eventtime=None):
        cpu = self.cpu_info
        return {
            "cpu_count": cpu["count"],
            "cpu_model": cpu["model"],
            "cpu_arch": cpu["arch"],
            "cpu_online": list(cpu["online"]),
            "affinity_supported": self._affinity_supported,
            "background_cpu_affinity": (
                list(self.background_cpu_affinity)
                if self.background_cpu_affinity
                else None
            ),
            "main_cpu_affinity": (
                list(self.main_cpu_affinity)
                if self.main_cpu_affinity
                else None
            ),
            "gpu": self.gpu,
            "compute_backend": self.compute_backend.name,
            "gpu_accelerate_calibration": self.gpu_accelerate_calibration,
        }


HARDWARE: Hardware = None


def get_hardware():
    if HARDWARE is None:
        raise Exception("Hardware has not been loaded yet!")
    return HARDWARE


def load_config(config):
    global HARDWARE
    HARDWARE = Hardware(config)
    return HARDWARE
