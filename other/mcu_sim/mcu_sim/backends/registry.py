# Backend registry — discover and select simulation backends
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Backend Registry
================

Discovers available QEMU binaries on the system and returns the
appropriate backend for a given MCU architecture.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..firmware import McuArch


# ---------------------------------------------------------------------------
# MCU model → backend mapping
# ---------------------------------------------------------------------------

@dataclass
class McuModel:
    """Metadata for a supported MCU model."""
    name: str
    arch: McuArch
    qemu_machine: str
    qemu_binary: str
    description: str
    flash_size: int = 0
    ram_size: int = 0


# Known MCU models
_MCU_MODELS: Dict[str, McuModel] = {
    "atmega328p": McuModel(
        name="atmega328p",
        arch=McuArch.AVR,
        qemu_machine="uno",
        qemu_binary="qemu-system-avr",
        description="Arduino Uno (ATmega328P, 16 MHz)",
        flash_size=32 * 1024,
        ram_size=2 * 1024,
    ),
    "atmega2560": McuModel(
        name="atmega2560",
        arch=McuArch.AVR,
        qemu_machine="mega2560",
        qemu_binary="qemu-system-avr",
        description="Arduino Mega 2560 (ATmega2560, 16 MHz)",
        flash_size=256 * 1024,
        ram_size=8 * 1024,
    ),
    "sam3x8e": McuModel(
        name="sam3x8e",
        arch=McuArch.ARM_CORTEX_M,
        qemu_machine="none",
        qemu_binary="qemu-system-arm",
        description="Arduino Due (ATSAM3X8E, Cortex-M3, 84 MHz)",
        flash_size=512 * 1024,
        ram_size=96 * 1024,
    ),
    "imxrt1062": McuModel(
        name="imxrt1062",
        arch=McuArch.ARM_CORTEX_M,
        qemu_machine="none",
        qemu_binary="qemu-system-arm",
        description="Teensy 4.0 (iMXRT1062, Cortex-M7, 600 MHz)",
        flash_size=1984 * 1024,
        ram_size=1024 * 1024,
    ),
    "esp32": McuModel(
        name="esp32",
        arch=McuArch.XTENSA,
        qemu_machine="esp32",
        qemu_binary="qemu-system-xtensa",
        description="ESP32 DevKit (Xtensa LX6, 240 MHz)",
        flash_size=4 * 1024 * 1024,
        ram_size=520 * 1024,
    ),
}


def list_models() -> List[McuModel]:
    """Return all known MCU models."""
    return list(_MCU_MODELS.values())


def get_model(name: str) -> Optional[McuModel]:
    """Get an MCU model by name, or ``None``."""
    return _MCU_MODELS.get(name.lower())


def find_model_for_arch(arch: McuArch) -> List[McuModel]:
    """Return all models for a given architecture."""
    return [m for m in _MCU_MODELS.values() if m.arch == arch]


# ---------------------------------------------------------------------------
# QEMU binary discovery
# ---------------------------------------------------------------------------

@dataclass
class BackendInfo:
    """Information about an available backend."""
    name: str
    binary: str
    path: str
    available: bool
    version: str = ""


def _find_binary(name: str) -> Optional[str]:
    """Locate a QEMU binary on the system PATH and common install dirs."""
    # 1. Check PATH first
    found = shutil.which(name)
    if found:
        return found

    # 2. Check common Windows install locations
    if sys.platform == "win32":
        exe_name = f"{name}.exe"
        # from PATH
        found = shutil.which(exe_name)
        if found:
            return found
        # Check common directories
        candidates = [
            os.environ.get("ProgramFiles", "C:\\Program Files"),
            os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)"),
        ]
        for base in candidates:
            for subdir in ("qemu", "QEMU"):
                qemu_dir = os.path.join(base, subdir)
                exe_path = os.path.join(qemu_dir, exe_name)
                if os.path.isfile(exe_path):
                    return exe_path

    return None


def _get_version(binary_path: str) -> str:
    """Get QEMU version string."""
    try:
        result = subprocess.run(
            [binary_path, "--version"],
            capture_output=True, text=True, timeout=5,
        )
        return result.stdout.splitlines()[0] if result.stdout else "unknown"
    except Exception:
        return "unknown"


def list_backends() -> List[BackendInfo]:
    """Discover available QEMU backends on the current system."""
    results: List[BackendInfo] = []
    seen = set()

    for model in _MCU_MODELS.values():
        binary = model.qemu_binary
        if binary in seen:
            continue
        seen.add(binary)

        path = _find_binary(binary)
        version = _get_version(path) if path else ""

        results.append(BackendInfo(
            name=f"qemu-{model.arch.value}",
            binary=binary,
            path=path or "(not found)",
            available=path is not None,
            version=version,
        ))

    return results


def get_backend_info(arch: McuArch | str) -> Optional[BackendInfo]:
    """Get backend info for a specific architecture."""
    if isinstance(arch, str):
        try:
            arch = McuArch(arch)
        except ValueError:
            return None
    for model in _MCU_MODELS.values():
        if model.arch == arch:
            path = _find_binary(model.qemu_binary)
            return BackendInfo(
                name=f"qemu-{arch.value}",
                binary=model.qemu_binary,
                path=path or "(not found)",
                available=path is not None,
                version=_get_version(path) if path else "",
            )
    return None
