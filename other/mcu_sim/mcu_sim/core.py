# Unified MCU simulator core — orchestrates backend + serial bridge
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
MCU Simulator Core
==================

:class:`MCUSimulator` is the main entry point for running firmware
simulations.  It:

1. Loads and inspects the firmware image
2. Selects the appropriate QEMU backend
3. Starts the virtual serial bridge (TCP server)
4. Manages the simulation lifecycle

Typical usage::

    sim = MCUSimulator()
    sim.load("firmware.hex", mcu="atmega2560")
    port = sim.start()
    # Connect kalico_debug_tool to localhost:{port}
    # ...
    sim.stop()
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Optional

from .backends.qemu_backend import QemuBackend
from .backends.registry import McuModel, get_model, list_models
from .firmware import FirmwareFile, McuArch
from .virtual_serial import VirtualSerialBridge

logger = logging.getLogger(__name__)


class MCUSimulator:
    """High-level simulator that ties together firmware loading,
    QEMU execution, and a virtual serial bridge.

    Parameters:
        on_serial_tx:
            Optional callback for bytes sent from host → MCU.
        on_serial_rx:
            Optional callback for bytes sent from MCU → host.
        host:
            TCP host address for the virtual serial bridge.
        port:
            TCP port (``0`` = auto-assign).
    """

    def __init__(
        self,
        on_serial_tx: Optional[Callable[[bytes], None]] = None,
        on_serial_rx: Optional[Callable[[bytes], None]] = None,
        host: str = "127.0.0.1",
        port: int = 0,
    ):
        self._host = host
        self._port = port
        self._on_serial_tx = on_serial_tx
        self._on_serial_rx = on_serial_rx

        self._firmware: Optional[FirmwareFile] = None
        self._model: Optional[McuModel] = None
        self._backend: Optional[QemuBackend] = None
        self._bridge: Optional[VirtualSerialBridge] = None
        self._started = False

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def firmware(self) -> Optional[FirmwareFile]:
        return self._firmware

    @property
    def mcu_model(self) -> Optional[McuModel]:
        return self._model

    @property
    def serial_port(self) -> int:
        """TCP port the virtual serial bridge is listening on."""
        if self._bridge:
            return self._bridge.listen_port
        return 0

    @property
    def is_running(self) -> bool:
        return self._started and self._backend is not None and self._backend.is_running()

    @property
    def state(self) -> str:
        if not self._started:
            return "idle"
        if self._backend is None:
            return "idle"
        return self._backend.get_state()

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def load(self, firmware_path: str, mcu: Optional[str] = None) -> "MCUSimulator":
        """Load and inspect a firmware image.

        Args:
            firmware_path: Path to ``.hex``, ``.bin``, or ``.elf`` file.
            mcu:           Optional MCU model override (e.g. ``"atmega2560"``).
                           If not provided, auto-detected from firmware.

        Returns:
            ``self`` for method chaining.
        """
        logger.info("Loading firmware: %s", firmware_path)
        self._firmware = FirmwareFile.from_path(firmware_path)

        # Determine MCU model
        if mcu:
            self._model = get_model(mcu)
            if self._model is None:
                raise ValueError(
                    f"Unknown MCU model '{mcu}'. Known: "
                    f"{', '.join(m.name for m in list_models())}"
                )
        else:
            # Auto-detect from firmware architecture
            arch = self._firmware.arch
            if arch == McuArch.UNKNOWN:
                raise ValueError(
                    "Could not auto-detect MCU architecture. "
                    "Use --mcu to specify explicitly."
                )
            models = [m for m in list_models() if m.arch == arch]
            if not models:
                raise ValueError(f"No MCU model available for architecture {arch}")
            # Default to first matching model; user can override
            self._model = models[0]
            logger.info("Auto-detected MCU: %s (%s)", self._model.name, self._model.description)

        logger.info("Firmware: %s, %d bytes, arch=%s",
                     self._firmware.format, self._firmware.total_size,
                     self._firmware.arch.value)
        logger.info("MCU model: %s (%s)", self._model.name, self._model.description)

        return self

    def start(self, wait_ready: bool = True, ready_timeout: float = 15.0) -> int:
        """Start the simulation: launch QEMU and the serial bridge.

        Args:
            wait_ready:    Wait for MCU firmware to initialize.
            ready_timeout: Maximum time to wait for ready state.

        Returns:
            TCP port number the virtual serial bridge is listening on.
        """
        if self._firmware is None:
            raise RuntimeError("No firmware loaded — call load() first")
        if self._model is None:
            raise RuntimeError("No MCU model selected")
        if self._started:
            raise RuntimeError("Simulation is already running")

        # 1. Create and start QEMU backend
        self._backend = QemuBackend(self._model)
        self._backend.load_firmware(str(self._firmware.path), self._model.name)
        self._backend.start()

        if wait_ready:
            logger.info("Waiting for MCU to become ready (timeout=%.1fs)...", ready_timeout)
            if not self._backend.wait_ready(timeout=ready_timeout):
                logger.warning("MCU not ready — continuing anyway")

        # 2. Create and start virtual serial bridge (TCP → QEMU's TCP serial)
        self._bridge = VirtualSerialBridge(
            qemu_host=self._host,
            qemu_port=self._backend.serial_port,
            host=self._host,
            port=self._port,
        )
        # Wire up optional protocol interception hooks
        if self._on_serial_tx:
            self._bridge.on_tx = self._on_serial_tx
        if self._on_serial_rx:
            self._bridge.on_rx = self._on_serial_rx

        actual_port = self._bridge.start()
        self._started = True

        logger.info("=" * 60)
        logger.info("MCU Simulator started successfully!")
        logger.info("  MCU:       %s", self._model.description)
        logger.info("  Firmware:  %s", self._firmware.path.name)
        logger.info("  Serial:    TCP %s:%d", self._host, actual_port)
        logger.info("  State:     %s", self._backend.get_state())
        logger.info("=" * 60)
        logger.info("Connect with: kalico_debug_tool connect tcp:%s:%d", self._host, actual_port)
        logger.info("=" * 60)

        return actual_port

    def stop(self) -> None:
        """Stop the simulation and clean up all resources."""
        logger.info("Stopping MCU simulator...")

        if self._bridge:
            self._bridge.stop()
            self._bridge = None

        if self._backend:
            self._backend.stop()
            self._backend = None

        self._started = False
        logger.info("MCU simulator stopped")

    # ------------------------------------------------------------------
    # Direct serial access (bypass TCP for programmatic use)
    # ------------------------------------------------------------------

    def send(self, data: bytes) -> None:
        """Send raw bytes to the simulated MCU (host → MCU)."""
        if self._bridge is None:
            raise RuntimeError("Simulation not started")
        self._bridge.send_to_qemu(data)

    def recv(self, timeout: float = 1.0) -> bytes:
        """Receive raw bytes from the simulated MCU (MCU → host)."""
        if self._bridge is None:
            raise RuntimeError("Simulation not started")
        return self._bridge.read_from_qemu(timeout=timeout)

    def recv_line(self, timeout: float = 5.0) -> str:
        """Receive a line of text from the MCU's debug serial.

        This reads from the debug serial (115200 baud USB), not the
        Kalico protocol serial (250000 baud UART).  Useful for reading
        the firmware startup banner.
        """
        deadline = time.time() + timeout
        buf = b""
        while time.time() < deadline:
            chunk = self.recv(timeout=0.2)
            if chunk:
                buf += chunk
                if b"\n" in buf:
                    line, _, rest = buf.partition(b"\n")
                    return line.decode("utf-8", errors="replace").strip()
        return buf.decode("utf-8", errors="replace").strip()

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    def __enter__(self) -> "MCUSimulator":
        return self

    def __exit__(self, *args) -> None:
        self.stop()
