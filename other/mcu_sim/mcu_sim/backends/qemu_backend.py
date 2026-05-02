# QEMU backend — runs firmware images via QEMU subprocess
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
QEMU Backend
============

Implements :class:`SimBackend` by spawning and controlling a QEMU
system emulator subprocess.  QEMU is used for all target architectures:

* **AVR**:           ``qemu-system-avr``  (ATmega328P, ATmega2560)
* **ARM Cortex-M**:  ``qemu-system-arm``  (Cortex-M3, Cortex-M7)
* **Xtensa/ESP32**:  ``qemu-system-xtensa``

The serial port (UART) is exposed via TCP (``-serial tcp:...``),
which works reliably on both Windows and Unix.  The
:class:`VirtualSerialBridge` connects to this TCP endpoint.
"""

from __future__ import annotations

import logging
import os
import re
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Optional

from . import SimBackend
from .registry import McuModel, get_model, _find_binary

logger = logging.getLogger(__name__)


def _find_free_port(host: str = "127.0.0.1") -> int:
    """Find an available TCP port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return s.getsockname()[1]


class QemuBackend(SimBackend):
    """Run firmware in a QEMU system emulator subprocess.

    Uses ``-serial tcp:host:port,server,nowait,maxc=1`` so the
    simulated UART is exposed as a TCP server.  The bridge connects
    as a TCP client — this works reliably on all platforms.
    """

    def __init__(self, mcu_model: str | McuModel):
        if isinstance(mcu_model, str):
            model = get_model(mcu_model)
            if model is None:
                raise ValueError(f"Unknown MCU model: {mcu_model}")
        else:
            model = mcu_model

        self._model = model
        self._process: Optional[subprocess.Popen] = None
        self._firmware_path: Optional[str] = None
        self._start_time: Optional[float] = None
        self._lock = threading.Lock()
        self._serial_port: int = 0          # QEMU's TCP serial port
        self._error_lines: list[str] = []   # captured stderr lines

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------

    @property
    def serial_port(self) -> int:
        """TCP port QEMU is listening on for serial I/O."""
        return self._serial_port

    # ------------------------------------------------------------------
    # SimBackend interface
    # ------------------------------------------------------------------

    def load_firmware(self, firmware_path: str, mcu: str = "", /) -> None:
        if mcu:
            model = get_model(mcu)
            if model is not None:
                self._model = model
        self._firmware_path = firmware_path

    def start(self) -> None:
        if self._process is not None:
            raise RuntimeError("Simulation is already running")

        if self._firmware_path is None:
            raise RuntimeError("No firmware loaded — call load_firmware() first")

        binary_name = self._model.qemu_binary
        binary = _find_binary(binary_name)
        if binary is None:
            raise RuntimeError(
                f"QEMU binary '{binary_name}' not found. "
                f"Please install QEMU: https://www.qemu.org/download/"
            )
        logger.info("Using QEMU binary: %s", binary)

        machine = self._model.qemu_machine
        self._serial_port = _find_free_port()

        qemu_args = [
            binary,
            "-nographic",
            "-monitor", "none",
        ]

        # Map UARTs:
        # - Mega2560: UART0=debug USB(ignored), UART1=Kalico protocol(TCP)
        # - Uno:      UART0=both debug+Kalico protocol(TCP)
        # We use multiple -serial options; each maps to consecutive USARTs
        if self._model.name in ("atmega2560",):
            # UART0 → null (debug output discarded), UART1 → TCP (Kalico)
            qemu_args.extend(["-serial", "null"])
            qemu_args.extend([
                "-serial", f"tcp:127.0.0.1:{self._serial_port},server,nowait",
            ])
        else:
            # Single UART → TCP (Kalico protocol)
            qemu_args.extend([
                "-serial", f"tcp:127.0.0.1:{self._serial_port},server,nowait",
            ])

        if self._model.arch.value == "avr":
            qemu_args.extend(["-M", machine, "-bios", self._firmware_path])
        elif self._model.arch.value in ("arm-cortex-m",):
            qemu_args.extend([
                "-M", machine,
                "-cpu", "cortex-m3",
                "-device", f"loader,file={self._firmware_path},addr=0x8000000",
            ])
        elif self._model.arch.value == "xtensa":
            qemu_args.extend([
                "-M", machine,
                "-bios", self._firmware_path,
            ])
        else:
            raise RuntimeError(f"Unsupported architecture: {self._model.arch}")

        logger.info("Starting QEMU: %s", " ".join(qemu_args))
        logger.info("Firmware: %s", self._firmware_path)
        logger.info("MCU: %s", self._model.description)
        logger.info("QEMU serial TCP port: %d", self._serial_port)

        self._error_lines = []

        # Launch QEMU — no stdin/stdout pipes needed for serial
        try:
            self._process = subprocess.Popen(
                qemu_args,
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to start QEMU: {exc}")

        self._start_time = time.time()

        # Start thread to read stderr
        self._stderr_thread = threading.Thread(
            target=self._read_stderr, daemon=True, name="qemu-stderr"
        )
        self._stderr_thread.start()

    @property
    def stdin(self):
        """Not used with TCP serial — direct to QEMU TCP socket instead."""
        raise NotImplementedError(
            "Use serial_port to connect to QEMU's TCP serial directly"
        )

    @property
    def stdout(self):
        """Not used with TCP serial."""
        raise NotImplementedError(
            "Use serial_port to connect to QEMU's TCP serial directly"
        )

    def wait_ready(self, timeout: float = 10.0) -> bool:
        """Wait until the QEMU TCP serial port is accepting connections."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.is_running():
                errs = "\n".join(self._error_lines[-5:]) if self._error_lines else "(none)"
                logger.error(
                    "QEMU exited prematurely (rc=%s). Last stderr:\n%s",
                    self._process.returncode if self._process else "?",
                    errs,
                )
                return False

            # Try to connect to QEMU's serial TCP port
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                sock.connect(("127.0.0.1", self._serial_port))
                sock.close()
                logger.info("QEMU serial port %d is ready", self._serial_port)
                return True
            except (ConnectionRefusedError, socket.timeout, OSError):
                pass

            time.sleep(0.2)

        logger.warning("MCU serial port did not become ready within %.1fs", timeout)
        return False

    def get_state(self) -> str:
        if self._process is None:
            return "stopped"
        rc = self._process.poll()
        if rc is not None:
            err_tail = self._error_lines[-3:] if self._error_lines else []
            return f"exited ({rc})" + (f" — {'; '.join(err_tail)}" if err_tail else "")
        if self._start_time is not None:
            elapsed = time.time() - self._start_time
            return f"running ({elapsed:.1f}s)"
        return "running"

    @property
    def backend_name(self) -> str:
        return f"qemu-{self._model.arch.value}"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_stderr(self) -> None:
        """Read QEMU's stderr stream and collect error lines."""
        if self._process is None or self._process.stderr is None:
            return
        try:
            for line_bytes in self._process.stderr:
                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                if line:
                    self._error_lines.append(line)
                    logger.debug("[QEMU] %s", line)
                    if len(self._error_lines) > 50:
                        self._error_lines.pop(0)
        except (ValueError, OSError):
            pass

    def stop(self) -> None:
        if self._process is None:
            return

        logger.info("Stopping QEMU (pid=%d)...", self._process.pid)

        with self._lock:
            proc = self._process
            self._process = None

        # Try graceful shutdown first
        try:
            if sys.platform == "win32":
                proc.terminate()
            else:
                proc.send_signal(signal.SIGTERM)
        except OSError:
            pass

        # Wait a bit, then force kill
        try:
            proc.wait(timeout=3.0)
        except subprocess.TimeoutExpired:
            try:
                proc.kill()
                proc.wait(timeout=2.0)
            except Exception:
                pass

        self._start_time = None
        logger.info("QEMU stopped")

    def is_running(self) -> bool:
        if self._process is None:
            return False
        return self._process.poll() is None

    @property
    def stdin(self):
        if self._process is None:
            raise RuntimeError("Simulation not started")
        return self._process.stdin

    @property
    def stdout(self):
        if self._process is None:
            raise RuntimeError("Simulation not started")
        return self._process.stdout

    def wait_ready(self, timeout: float = 10.0) -> bool:
        """Wait until MCU firmware has initialized and is ready.

        We poll for any output on stdout — the firmware typically
        prints a startup banner via its debug serial.
        """
        deadline = time.time() + timeout
        while time.time() < deadline:
            if not self.is_running():
                logger.error("QEMU exited prematurely (rc=%s)", self._process.returncode if self._process else "?")
                return False

            # Try to read a byte — if we get something, firmware is alive
            if self.stdout is not None:
                try:
                    # Non-blocking check
                    import select
                    r, _, _ = select.select([self.stdout], [], [], 0.2)
                    if r:
                        # peek at data without consuming too much
                        return True
                except (OSError, ValueError):
                    pass

            time.sleep(0.1)

        logger.warning("MCU did not become ready within %.1fs", timeout)
        return False

    def get_state(self) -> str:
        if self._process is None:
            return "stopped"
        rc = self._process.poll()
        if rc is not None:
            return f"exited ({rc})"
        if self._start_time is not None:
            elapsed = time.time() - self._start_time
            return f"running ({elapsed:.1f}s)"
        return "running"

    @property
    def backend_name(self) -> str:
        return f"qemu-{self._model.arch.value}"

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _read_stderr(self) -> None:
        """Read QEMU's stderr stream and log it."""
        if self._process is None or self._process.stderr is None:
            return
        try:
            for line_bytes in self._process.stderr:
                line = line_bytes.decode("utf-8", errors="replace").rstrip()
                if line:
                    logger.debug("[QEMU] %s", line)
        except (ValueError, OSError):
            pass
