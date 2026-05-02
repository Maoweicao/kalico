# MCU Simulator for Kalico firmware protocol testing
#
# Loads compiled .hex/.bin firmware files and simulates MCU execution
# using QEMU as the CPU emulation backend. Exposes a virtual serial port
# for connection by kalico_debug_tool or other host-side tools.
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MCU Simulator (mcu_sim)
=======================

A hardware-less MCU simulator for testing the Kalico binary protocol.
Loads generic_arduino firmware images (.hex/.bin) and executes them
with instruction-level accuracy using QEMU.

Supported architectures:
  - AVR (ATmega328P, ATmega2560) via qemu-system-avr
  - ARM Cortex-M3/M7 (ATSAM3X8E, iMXRT1062) via qemu-system-arm
  - Xtensa (ESP32) via qemu-system-xtensa

Quick start::

    python -m mcu_sim run firmware.hex --mcu atmega2560
    python -m mcu_sim run firmware.hex --baud 250000
"""

__version__ = "0.1.0"
__all__ = ["MCUSimulator", "FirmwareFile", "VirtualSerialBridge",
           "list_backends", "get_backend_info"]

from .core import MCUSimulator
from .firmware import FirmwareFile
from .virtual_serial import VirtualSerialBridge
from .py_mcu import PyMCU
from .backends.registry import list_backends, get_backend_info
