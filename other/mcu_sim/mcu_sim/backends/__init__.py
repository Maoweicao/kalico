# Abstract backend interface for MCU simulators
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Simulation Backend Interface
============================

Defines the :class:`SimBackend` abstract base class that all MCU
simulation backends must implement.  Currently the primary backend
is QEMU (via subprocess), but the interface is designed to allow
future additions like Unicorn Engine or Renode.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class SimBackend(ABC):
    """Abstract interface for an MCU simulation engine.

    Each backend manages the lifecycle of a single MCU simulation
    instance — loading firmware, starting/stopping execution, and
    providing access to the serial I/O channels.
    """

    @abstractmethod
    def load_firmware(self, firmware_path: str, mcu: str, /) -> None:
        """Load a firmware image into the simulator.

        Args:
            firmware_path: Path to ``.hex``, ``.bin``, or ``.elf`` file.
            mcu:           MCU model identifier (e.g. ``"atmega2560"``).
        """

    @abstractmethod
    def start(self) -> None:
        """Launch the simulation process."""

    @abstractmethod
    def stop(self) -> None:
        """Stop (kill) the simulation process."""

    @abstractmethod
    def is_running(self) -> bool:
        """Return ``True`` if the simulation is currently executing."""

    @property
    @abstractmethod
    def stdin(self):
        """File-like object for writing serial data **into** the simulated MCU."""

    @property
    @abstractmethod
    def stdout(self):
        """File-like object for reading serial data **from** the simulated MCU."""

    @abstractmethod
    def wait_ready(self, timeout: float = 10.0) -> bool:
        """Block until the simulated MCU is ready to communicate.

        Returns:
            ``True`` if ready within timeout, ``False`` otherwise.
        """

    @abstractmethod
    def get_state(self) -> str:
        """Return a human-readable state string (e.g. ``"running"``, ``"stopped"``)."""

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Short identifier for this backend (e.g. ``"qemu-avr"``)."""

    # Optional — for instruction-level stepping
    def step(self, count: int = 1) -> None:
        """Execute *count* instructions (optional — raises by default)."""
        raise NotImplementedError(f"{self.backend_name} does not support stepping")

    def run_until_halt(self, timeout: float = 30.0) -> bool:
        """Run until MCU halts or timeout expires (optional)."""
        raise NotImplementedError(f"{self.backend_name} does not support run-until")
