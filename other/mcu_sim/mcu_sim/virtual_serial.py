# Virtual serial bridge — TCP ↔ TCP proxy for QEMU serial
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Virtual Serial Bridge
=====================

A TCP-to-TCP proxy that bridges a Kalico host tool (e.g.
``kalico_debug_tool``) to QEMU's simulated UART.

Architecture::

    kalico_debug_tool ──TCP──> [VirtualSerialBridge] ──TCP──> QEMU serial
                         :PORT_B                           :PORT_A
"""

from __future__ import annotations

import logging
import select
import socket
import threading
import time
from typing import Callable, List, Optional, Set

logger = logging.getLogger(__name__)


class VirtualSerialBridge:
    """Bidirectional TCP proxy: host ↔ QEMU serial.

    Parameters:
        qemu_host:
            Host where QEMU's serial TCP server is listening.
        qemu_port:
            Port where QEMU's serial TCP server is listening.
        host:
            Host address to bind the proxy server (default ``127.0.0.1``).
        port:
            TCP port for the proxy server.  Use ``0`` for auto-assign.
        on_client_connect:
            Callback when a host client connects.
        on_client_disconnect:
            Callback when a host client disconnects.
    """

    def __init__(
        self,
        qemu_host: str = "127.0.0.1",
        qemu_port: int = 0,
        host: str = "127.0.0.1",
        port: int = 0,
        on_client_connect: Optional[Callable[[str], None]] = None,
        on_client_disconnect: Optional[Callable[[str], None]] = None,
    ):
        self._qemu_host = qemu_host
        self._qemu_port = qemu_port
        self._host = host
        self._port = port

        self._server: Optional[socket.socket] = None
        self._qemu_sock: Optional[socket.socket] = None
        self._clients: Set[socket.socket] = set()
        self._lock = threading.Lock()
        self._running = False
        self._thread: Optional[threading.Thread] = None

        # Hooks
        self.on_client_connect = on_client_connect
        self.on_client_disconnect = on_client_disconnect
        self.on_tx: Optional[Callable[[bytes], None]] = None   # host→mcu
        self.on_rx: Optional[Callable[[bytes], None]] = None   # mcu→host

        # Statistics
        self.bytes_to_mcu = 0
        self.bytes_from_mcu = 0

    @property
    def listen_port(self) -> int:
        """The actual TCP port in use (available after ``start()``)."""
        if self._server:
            return self._server.getsockname()[1]
        return self._port

    @property
    def client_count(self) -> int:
        with self._lock:
            return len(self._clients)

    @property
    def is_running(self) -> bool:
        return self._running

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> int:
        """Start the proxy server and connect to QEMU serial.

        Returns:
            The listening TCP port number.
        """
        if self._running:
            raise RuntimeError("VirtualSerialBridge is already running")

        # 1. Connect to QEMU's serial TCP server
        self._qemu_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._qemu_sock.settimeout(2.0)
        try:
            self._qemu_sock.connect((self._qemu_host, self._qemu_port))
        except (ConnectionRefusedError, socket.timeout, OSError) as exc:
            raise RuntimeError(
                f"Failed to connect to QEMU serial at "
                f"{self._qemu_host}:{self._qemu_port}: {exc}"
            )
        self._qemu_sock.settimeout(0.1)
        logger.info("Connected to QEMU serial at %s:%d",
                     self._qemu_host, self._qemu_port)

        # 2. Start proxy server for host tools
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((self._host, self._port))
        self._server.listen(1)
        self._server.settimeout(0.5)

        self._running = True
        self._thread = threading.Thread(
            target=self._bridge_loop, daemon=True, name="serial-bridge"
        )
        self._thread.start()

        actual_port = self.listen_port
        logger.info("Virtual serial bridge listening on %s:%d",
                     self._host, actual_port)
        return actual_port

    def stop(self) -> None:
        """Shut down the proxy and close all connections."""
        self._running = False
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)

        with self._lock:
            for client in list(self._clients):
                self._close_client(client)

        if self._qemu_sock:
            try:
                self._qemu_sock.close()
            except OSError:
                pass
            self._qemu_sock = None

        if self._server:
            try:
                self._server.close()
            except OSError:
                pass
            self._server = None

        logger.info("Virtual serial bridge stopped")

    # ------------------------------------------------------------------
    # Internal — I/O bridge
    # ------------------------------------------------------------------

    def _bridge_loop(self) -> None:
        """Main loop: forward data between QEMU and host clients."""
        server = self._server
        if server is None:
            return

        while self._running:
            try:
                readers = [server]
                if self._qemu_sock is not None:
                    readers.append(self._qemu_sock)
                with self._lock:
                    readers.extend(self._clients)

                ready, _, _ = select.select(readers, [], [], 0.1)

                for r in ready:
                    if r is server:
                        self._accept_client()
                    elif r is self._qemu_sock:
                        self._forward_qemu_to_clients()
                    else:
                        self._forward_client_to_qemu(r)
            except (OSError, ValueError, select.error) as exc:
                if self._running:
                    logger.debug("Bridge loop error: %s", exc)
                time.sleep(0.05)

    def _accept_client(self) -> None:
        try:
            client, addr = self._server.accept()
        except (socket.timeout, OSError):
            return

        client.settimeout(0.1)
        with self._lock:
            self._clients.add(client)
        logger.info("Host client connected: %s:%d", addr[0], addr[1])
        if self.on_client_connect:
            self.on_client_connect(f"{addr[0]}:{addr[1]}")

    def _forward_qemu_to_clients(self) -> None:
        """Read from QEMU → forward to all host clients."""
        try:
            data = self._qemu_sock.recv(4096)
        except (socket.timeout, OSError):
            return
        if not data:
            logger.warning("QEMU serial connection closed")
            self._qemu_sock = None
            return

        self.bytes_from_mcu += len(data)
        if self.on_rx:
            self.on_rx(data)

        with self._lock:
            dead: List[socket.socket] = []
            for client in self._clients:
                try:
                    client.sendall(data)
                except OSError:
                    dead.append(client)
            for d in dead:
                self._close_client(d)

    def _forward_client_to_qemu(self, client: socket.socket) -> None:
        """Read from host client → forward to QEMU."""
        try:
            data = client.recv(4096)
        except (socket.timeout, OSError):
            return
        if not data:
            self._close_client(client)
            return

        self.bytes_to_mcu += len(data)
        if self.on_tx:
            self.on_tx(data)

        if self._qemu_sock is not None:
            try:
                self._qemu_sock.sendall(data)
            except OSError as exc:
                logger.error("Error writing to QEMU: %s", exc)

    def _close_client(self, client: socket.socket) -> None:
        with self._lock:
            if client in self._clients:
                self._clients.discard(client)
        try:
            addr = client.getpeername()
            logger.info("Host client disconnected: %s:%d", addr[0], addr[1])
            if self.on_client_disconnect:
                self.on_client_disconnect(f"{addr[0]}:{addr[1]}")
        except OSError:
            pass
        try:
            client.close()
        except OSError:
            pass

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def send_to_qemu(self, data: bytes) -> None:
        """Programmatically inject data to QEMU serial (host→mcu)."""
        if self._qemu_sock is not None:
            try:
                self._qemu_sock.sendall(data)
                self.bytes_to_mcu += len(data)
            except OSError as exc:
                logger.error("send_to_qemu error: %s", exc)

    def read_from_qemu(self, timeout: float = 0.5) -> bytes:
        """Read any available data from QEMU serial (mcu→host)."""
        if self._qemu_sock is None:
            return b""
        try:
            self._qemu_sock.settimeout(timeout)
            data = self._qemu_sock.recv(4096)
            self._qemu_sock.settimeout(0.1)
            return data
        except (socket.timeout, OSError):
            self._qemu_sock.settimeout(0.1)
            return b""
