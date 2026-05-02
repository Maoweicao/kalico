# Serial I/O abstraction for Kalico MCU communication
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Serial I/O Module
=================

Provides low-level serial port communication with Kalico MCU devices.
Supports regular serial (UART/USB CDC ACM) and optionally CAN bus.

Features:
  - Auto-detect available serial ports
  - Connect/disconnect with configurable baud rate
  - Raw byte send/receive with timeouts
  - Background read thread with callback on received data
"""

import logging
import platform
import select
import socket
import threading
import time
from enum import Enum
from typing import Callable, List, Optional, Tuple, Union

from ..protocol.codec import (
    MESSAGE_MIN, MESSAGE_MAX, MESSAGE_SYNC, MESSAGE_DEST,
    MessageBlock, VLQEncoder, crc16_ccitt,
)

# TCP scheme prefix for virtual serial connections (e.g. mcu_sim)
_TCP_PREFIX = "tcp:"


# Identify command bytes: msgid=1, offset=0, count=40
_IDENTIFY_PACKET = bytes(
    MessageBlock(seq=0, content=bytes(
        VLQEncoder.encode_uint32(1)  # msgid=1 (identify)
        + VLQEncoder.encode_uint32(0)  # offset=0
        + VLQEncoder.encode_byte(40)   # count=40
    )).encode()
)


class SerialProbeResult:
    """Result of a single serial probe attempt."""
    __slots__ = ("port", "baudrate", "success", "error")

    def __init__(self, port: str, baudrate: int,
                 success: bool = False, error: str = ""):
        self.port = port
        self.baudrate = baudrate
        self.success = success
        self.error = error

    def __repr__(self) -> str:
        return (f"SerialProbe(port={self.port!r}, baud={self.baudrate}, "
                f"ok={self.success})")


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class SerialIO:
    """Abstraction layer for serial port communication.

    Provides a callback-based receive model suitable for
    integration with the protocol parser and GUI.
    """

    def __init__(self, on_data: Optional[Callable[[bytes], None]] = None,
                 on_error: Optional[Callable[[Exception], None]] = None):
        self._serial: Optional["serial.Serial"] = None  # type: ignore
        self._socket: Optional[socket.socket] = None    # TCP mode
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._buffer = bytearray()
        self._port = ""
        self._baudrate = 250000
        self._is_tcp = False
        self.state = ConnectionState.DISCONNECTED

        # Callbacks
        self.on_data = on_data       # received raw bytes
        self.on_error = on_error     # error occurred
        self.on_connect = None       # connected callback
        self.on_disconnect = None    # disconnected callback

        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.connect_time: Optional[float] = None

    @staticmethod
    def list_ports() -> List[str]:
        """List available serial ports.

        Returns a list of port device names/paths.
        TCP endpoints are listed as ``tcp:host:port``.
        """
        result: List[str] = []
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            for p in ports:
                desc = f"{p.device}"
                if p.description and p.description != p.device:
                    desc += f" ({p.description})"
                result.append(desc)
        except ImportError:
            pass
        return result

    @staticmethod
    def get_port_name(port_desc: str) -> str:
        """Extract the actual device name from a port description string."""
        return port_desc.split(" ")[0]

    def connect(self, port: str, baudrate: int = 250000,
                timeout: float = 2.0) -> bool:
        """Connect to a serial port or TCP endpoint.

        Args:
            port: Serial port device name/path, or ``tcp:host:port``
                  for virtual serial (e.g. ``tcp:127.0.0.1:12345``).
            baudrate: Baud rate (default 250000 for Kalico).
                      Ignored for TCP connections.
            timeout: Read timeout in seconds.

        Returns:
            True if connection successful
        """
        # Detect TCP mode
        if port.startswith(_TCP_PREFIX):
            return self._connect_tcp(port, timeout)
        if port.startswith("socket://"):
            return self._connect_tcp(port.replace("socket://", _TCP_PREFIX), timeout)

        return self._connect_serial(port, baudrate, timeout)

    def _connect_tcp(self, port: str, timeout: float) -> bool:
        """Connect via TCP socket (virtual serial bridge)."""
        # Parse tcp:host:port
        addr = port[len(_TCP_PREFIX):]
        if ":" in addr:
            host, port_str = addr.rsplit(":", 1)
            try:
                tcp_port = int(port_str)
            except ValueError:
                logging.error(f"Invalid TCP port: {port_str}")
                return False
        else:
            host = addr
            tcp_port = 25000  # default

        with self._lock:
            if self.state == ConnectionState.CONNECTED:
                logging.warning(f"Already connected to {self._port}")
                return False
            self.state = ConnectionState.CONNECTING
            self._port = port
            self._is_tcp = True
            self._buffer = bytearray()

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((host, tcp_port))
            sock.settimeout(0.1)  # short timeout for read loop
            sock.setblocking(True)

            with self._lock:
                self._socket = sock
                self.state = ConnectionState.CONNECTED
                self.connect_time = time.time()
                self.bytes_sent = 0
                self.bytes_received = 0
                self.packets_sent = 0
                self.packets_received = 0

            # Start background read thread
            self._running = True
            self._read_thread = threading.Thread(
                target=self._read_loop, daemon=True,
                name=f"serial-read-{host}:{tcp_port}"
            )
            self._read_thread.start()

            logging.info(f"Connected to TCP {host}:{tcp_port}")
            if self.on_connect:
                self.on_connect()
            return True

        except (ConnectionRefusedError, socket.timeout, OSError) as e:
            with self._lock:
                self.state = ConnectionState.ERROR
                self._socket = None
                self._is_tcp = False
            logging.error(f"Failed to connect to {port}: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def _connect_serial(self, port: str, baudrate: int,
                        timeout: float) -> bool:
        """Connect via physical serial port."""
        import serial

        with self._lock:
            if self.state == ConnectionState.CONNECTED:
                logging.warning(f"Already connected to {self._port}")
                return False
            self.state = ConnectionState.CONNECTING
            self._port = port
            self._baudrate = baudrate
            self._is_tcp = False
            self._buffer = bytearray()

        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout,
            )
            with self._lock:
                self._serial = ser
                self.state = ConnectionState.CONNECTED
                self.connect_time = time.time()
                self.bytes_sent = 0
                self.bytes_received = 0
                self.packets_sent = 0
                self.packets_received = 0

            # Start background read thread
            self._running = True
            self._read_thread = threading.Thread(
                target=self._read_loop, daemon=True,
                name=f"serial-read-{port}"
            )
            self._read_thread.start()

            logging.info(f"Connected to {port} at {baudrate} baud")
            if self.on_connect:
                self.on_connect()
            return True

        except Exception as e:
            with self._lock:
                self.state = ConnectionState.ERROR
                self._serial = None
            logging.error(f"Failed to connect to {port}: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def disconnect(self) -> None:
        """Disconnect from the serial port or TCP socket."""
        self._running = False

        with self._lock:
            ser = self._serial
            sock = self._socket
            self._serial = None
            self._socket = None
            self.state = ConnectionState.DISCONNECTED
            self._is_tcp = False

        if sock:
            try:
                sock.shutdown(socket.SHUT_RDWR)
                sock.close()
            except OSError:
                pass
        if ser and ser.is_open:
            try:
                ser.close()
            except Exception as e:
                logging.debug(f"Error closing serial port: {e}")

        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=2.0)
            self._read_thread = None

        logging.info(f"Disconnected from {self._port}")
        if self.on_disconnect:
            self.on_disconnect()

    def send(self, data: Union[bytes, bytearray]) -> bool:
        """Send raw bytes to the serial port or TCP socket.

        Args:
            data: bytes to send

        Returns:
            True if successful
        """
        import serial

        with self._lock:
            sock = self._socket
            ser = self._serial

            if sock is not None:
                try:
                    sock.sendall(data)
                    self.bytes_sent += len(data)
                    self.packets_sent += 1
                    return True
                except OSError as e:
                    logging.error(f"TCP send error: {e}")
                    if self.on_error:
                        self.on_error(e)
                    return False

            if ser is None or not ser.is_open:
                return False
            try:
                written = ser.write(data)
                self.bytes_sent += written
                self.packets_sent += 1
                return True
            except serial.SerialTimeoutException:
                logging.warning("Serial write timeout")
                return False
            except Exception as e:
                logging.error(f"Serial write error: {e}")
                if self.on_error:
                    self.on_error(e)
                return False

    def send_block(self, block: MessageBlock) -> bool:
        """Send a MessageBlock to the serial port."""
        return self.send(block.encode())

    def _read_loop(self) -> None:
        """Background thread: continuously read from serial port or TCP socket."""
        while self._running:
            try:
                with self._lock:
                    sock = self._socket
                    ser = self._serial
                    if sock is None and (ser is None or not ser.is_open):
                        break

                # TCP socket read path
                if sock is not None:
                    try:
                        ready, _, _ = select.select([sock], [], [], 0.2)
                        if ready:
                            data = sock.recv(4096)
                            if not data:
                                break  # connection closed
                        else:
                            continue
                    except (OSError, socket.timeout):
                        continue
                else:
                    # Serial read path
                    import serial
                    if hasattr(ser, 'read') and ser.in_waiting:
                        data = ser.read(ser.in_waiting)
                    else:
                        data = ser.read(1)
                        if data:
                            data += ser.read(ser.in_waiting)

                if data:
                    with self._lock:
                        self.bytes_received += len(data)
                        self.packets_received += 1
                    if self.on_data:
                        try:
                            self.on_data(bytes(data))
                        except Exception as e:
                            logging.error(f"on_data callback error: {e}")

            except serial.SerialException as e:
                if self._running:
                    logging.error(f"Serial read error: {e}")
                    if self.on_error:
                        self.on_error(e)
                break
            except Exception as e:
                logging.error(f"Serial read thread error: {e}")
                break

        # Thread ending - mark state (don't call disconnect() — would deadlock)
        with self._lock:
            self._running = False
            self.state = ConnectionState.DISCONNECTED

    def get_stats(self) -> dict:
        """Get connection statistics."""
        with self._lock:
            duration = 0.0
            if self.connect_time:
                duration = time.time() - self.connect_time
            return {
                "port": self._port,
                "baudrate": self._baudrate,
                "state": self.state.value,
                "duration": round(duration, 1),
                "bytes_sent": self.bytes_sent,
                "bytes_received": self.bytes_received,
                "packets_sent": self.packets_sent,
                "packets_received": self.packets_received,
            }

    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED

    @property
    def is_tcp(self) -> bool:
        """True if connected via TCP (virtual serial bridge)."""
        return self._is_tcp

    # ── Auto-detect ──────────────────────────────────────────────────

    @staticmethod
    def _probe(port: str, baudrate: int,
               timeout: float = 0.8) -> SerialProbeResult:
        """Probe a single serial port at a single baud rate.

        Opens the port, sends an identify command, and checks for a
        valid Kalico protocol response (sync byte 0x7E present).

        Returns SerialProbeResult.
        """
        import serial
        try:
            ser = serial.Serial(
                port=port, baudrate=baudrate,
                timeout=timeout, write_timeout=timeout,
                exclusive=True,
            )
        except (OSError, serial.SerialException) as e:
            return SerialProbeResult(port, baudrate, error=str(e))

        try:
            # Flush any stale data
            time.sleep(0.05)
            ser.reset_input_buffer()
            ser.reset_output_buffer()

            # Send identify command
            ser.write(_IDENTIFY_PACKET)

            # Wait for response - a valid Kalico response starts with
            # a length byte (5-64), has 0x7E at end, CRC in between
            data = bytearray()
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                try:
                    chunk = ser.read(max(1, int(remaining * 1000)))
                except serial.SerialException:
                    break
                if not chunk:
                    continue
                data.extend(chunk)
                # Look for a valid message block anywhere in buffer
                while len(data) >= MESSAGE_MIN:
                    # Scan for a message starting with valid length
                    found = False
                    for scan_pos in range(len(data)):
                        blen = data[scan_pos]
                        if blen < MESSAGE_MIN or blen > MESSAGE_MAX:
                            continue
                        end_pos = scan_pos + blen
                        if end_pos > len(data):
                            break  # need more data
                        # Check sync byte
                        sync_pos = end_pos - 1
                        if data[sync_pos] != MESSAGE_SYNC:
                            continue
                        # Check CRC
                        body = data[scan_pos:end_pos - 3]
                        expected_crc = data[end_pos - 3:end_pos - 1]
                        actual_crc = bytes(crc16_ccitt(body))
                        if expected_crc == actual_crc:
                            found = True
                            break
                    if found:
                        return SerialProbeResult(port, baudrate,
                                                 success=True)
                    # No valid message; discard first byte and continue
                    data = data[1:]

            return SerialProbeResult(port, baudrate,
                                     error="No valid response")

        except Exception as e:
            return SerialProbeResult(port, baudrate, error=str(e))
        finally:
            try:
                ser.close()
            except Exception:
                pass

    def auto_detect(self,
                    baudrates: Optional[List[int]] = None,
                    on_progress: Optional[Callable[[str], None]] = None,
                    timeout_per_port: float = 0.8
                    ) -> Optional[Tuple[str, int]]:
        """Auto-detect a Kalico MCU by scanning all serial ports.

        Iterates through all available serial ports at common baud
        rates, sending identify commands and looking for valid
        Kalico protocol responses.

        Args:
            baudrates: List of baud rates to try (default: [250000, 115200,
                       500000, 230400])
            on_progress: Callback for progress updates (receives status str)
            timeout_per_port: Timeout per port/baudrate attempt

        Returns:
            (port_name, baudrate) if found, None otherwise
        """
        if baudrates is None:
            baudrates = [250000, 115200, 500000, 230400]

        ports = self.list_ports()
        if not ports:
            if on_progress:
                on_progress("未检测到串口")
            return None

        for pdesc in ports:
            port = self.get_port_name(pdesc)
            for baud in baudrates:
                msg = f"探测 {port} @ {baud}..."
                if on_progress:
                    on_progress(msg)
                logging.info(msg)
                result = self._probe(port, baud, timeout_per_port)
                if result.success:
                    msg = f"✓ 发现设备: {port} @ {baud}"
                    if on_progress:
                        on_progress(msg)
                    logging.info(msg)
                    return (port, baud)
                if on_progress:
                    on_progress(f"  {port} @ {baud}: {result.error}")

        msg = "未找到 Kalico MCU 设备"
        if on_progress:
            on_progress(msg)
        logging.info(msg)
        return None
