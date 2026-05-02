# CAN bus I/O abstraction for Kalico MCU communication
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
CAN Bus I/O Module
==================

Provides CAN bus communication with Kalico MCU devices on Windows.
Uses python-can with supported interfaces:

  - **slcan**  : Serial-line CAN (Lawicel CANUSB, USB2CAN, etc.) — works on Windows via COM port
  - **pcan**   : PEAK PCAN-USB — requires PCANBasic DLL
  - **virtual**: Virtual CAN bus (for testing without hardware)

Kalico CAN Protocol:
  - Standard 11-bit CAN IDs
  - Admin ID: 0x3F0 (discovery/assignment)
  - Data IDs: txid = nodeid * 2 + 0x100, rxid = txid + 1
  - CAN data payload wraps the standard Kalico binary message block
"""

import logging
import threading
import time
from enum import Enum
from typing import Callable, List, Optional, Union

from ..protocol.codec import MessageBlock, MESSAGE_MIN, MESSAGE_MAX

# CAN protocol constants (matches klippy/serialhdl.py)
CANBUS_ID_ADMIN = 0x3F0
CMD_QUERY_UNASSIGNED = 0x00
CMD_QUERY_UNASSIGNED_EXTENDED = 0x01
CMD_SET_NODEID = 0x01
RESP_NEED_NODEID = 0x20
RESP_HAVE_NODEID = 0x21


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class CANIO:
    """CAN bus communication layer for Kalico MCU.

    Encapsulates python-can bus with Kalico-specific addressing
    and message block extraction.
    """

    def __init__(self, on_data: Optional[Callable[[bytes], None]] = None,
                 on_error: Optional[Callable[[Exception], None]] = None):
        self._bus = None
        self._read_thread: Optional[threading.Thread] = None
        self._running = False
        self._lock = threading.Lock()
        self._can_interface = ""
        self._can_channel = ""
        self._can_bitrate = 500000
        self._nodeid = 0
        self._txid = 0
        self._rxid = 0
        self.state = ConnectionState.DISCONNECTED

        # Callbacks
        self.on_data = on_data
        self.on_error = on_error
        self.on_connect = None
        self.on_disconnect = None

        # Statistics
        self.bytes_sent = 0
        self.bytes_received = 0
        self.packets_sent = 0
        self.packets_received = 0
        self.connect_time: Optional[float] = None

    @staticmethod
    def list_interfaces() -> List[str]:
        """List available CAN interface types.

        Returns interface type identifiers suitable for python-can.
        On Windows, typical usable types: 'slcan', 'pcan', 'virtual'.
        """
        available = ['virtual']  # always available (no hardware needed)
        try:
            import can
            # Detect slcan (serial-based CAN adapters)
            try:
                from can.interfaces.slcan import slcanBus
                available.append('slcan')
            except ImportError:
                pass
            # Detect pcan
            try:
                from can.interfaces.pcan import PcanBus
                available.append('pcan')
            except ImportError:
                pass
            # Detect other common interfaces
            for iface in ['ixxat', 'usb2can', 'neousys', 'seeedstudio']:
                try:
                    mod = __import__(f'can.interfaces.{iface}', fromlist=[''])
                    if hasattr(mod, f'{iface[0].upper()}{iface[1:]}Bus'):
                        available.append(iface)
                except ImportError:
                    pass
        except ImportError:
            pass
        return available

    @staticmethod
    def list_slcan_ports() -> List[str]:
        """List serial ports suitable for slcan adapters."""
        try:
            import serial.tools.list_ports
            return [p.device for p in serial.tools.list_ports.comports()]
        except ImportError:
            return []

    def connect_slcan(self, port: str, bitrate: int = 500000) -> bool:
        """Connect via slcan interface (USB-to-CAN serial bridge).

        Args:
            port: COM port name (e.g., 'COM3')
            bitrate: CAN bitrate (default 500000)

        Returns:
            True if connection successful
        """
        return self._connect(interface='slcan', channel=port,
                             bitrate=bitrate)

    def connect_pcan(self, channel: str = 'PCAN_USBBUS1',
                     bitrate: int = 500000) -> bool:
        """Connect via PEAK PCAN interface.

        Args:
            channel: PCAN channel name (e.g., 'PCAN_USBBUS1')
            bitrate: CAN bitrate

        Returns:
            True if connection successful
        """
        return self._connect(interface='pcan', channel=channel,
                             bitrate=bitrate)

    def connect_virtual(self, channel: str = 'virtual0',
                        bitrate: int = 500000) -> bool:
        """Connect via virtual CAN bus (testing only).

        Args:
            channel: Virtual channel name
            bitrate: CAN bitrate

        Returns:
            True if connection successful
        """
        return self._connect(interface='virtual', channel=channel,
                             bitrate=bitrate)

    def _connect(self, interface: str, channel: str,
                 bitrate: int = 500000) -> bool:
        """Internal: open a python-can bus."""
        import can

        with self._lock:
            if self.state == ConnectionState.CONNECTED:
                logging.warning("Already connected")
                return False
            self.state = ConnectionState.CONNECTING
            self._can_interface = interface
            self._can_channel = channel
            self._can_bitrate = bitrate

        try:
            kwargs = {'interface': interface, 'channel': channel,
                      'bitrate': bitrate}
            # slcan needs additional params
            if interface == 'slcan':
                kwargs['tty'] = channel
                kwargs['sleep_after_open'] = 0.5
            elif interface == 'virtual':
                kwargs['rx_queue_size'] = 1000

            bus = can.Bus(**kwargs)

            with self._lock:
                self._bus = bus
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
                name=f"can-read-{interface}-{channel}"
            )
            self._read_thread.start()

            logging.info(f"CAN connected: {interface}/{channel} @ {bitrate}")
            if self.on_connect:
                self.on_connect()
            return True

        except Exception as e:
            with self._lock:
                self.state = ConnectionState.ERROR
                self._bus = None
            logging.error(f"CAN connect failed: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def disconnect(self) -> None:
        """Disconnect the CAN bus."""
        self._running = False
        with self._lock:
            bus = self._bus
            self._bus = None
            self.state = ConnectionState.DISCONNECTED

        if bus is not None:
            try:
                bus.shutdown()
            except Exception as e:
                logging.debug(f"CAN shutdown error: {e}")

        if self._read_thread and self._read_thread.is_alive():
            self._read_thread.join(timeout=2.0)
            self._read_thread = None

        logging.info("CAN disconnected")
        if self.on_disconnect:
            self.on_disconnect()

    def discover_mcu(self, uuid: Optional[str] = None,
                     timeout: float = 3.0) -> Optional[int]:
        """Discover MCU nodes on the CAN bus.

        Sends a query on the admin channel and waits for responses.

        Args:
            uuid: Optional UUID string to filter for (e.g., 'a1b2c3d4e5f6')
            timeout: Discovery timeout in seconds

        Returns:
            Node ID if found, None otherwise
        """
        import can

        with self._lock:
            bus = self._bus
            if bus is None:
                return None

        try:
            # Send query on admin channel
            msg = can.Message(
                arbitration_id=CANBUS_ID_ADMIN,
                data=[CMD_QUERY_UNASSIGNED, CMD_QUERY_UNASSIGNED_EXTENDED],
                is_extended_id=False,
            )
            bus.send(msg)
            self.packets_sent += 1
            self.bytes_sent += msg.dlc

            # Listen for responses
            start = time.time()
            while time.time() - start < timeout:
                msg = bus.recv(timeout=0.5)
                if msg is None:
                    continue
                if msg.arbitration_id != CANBUS_ID_ADMIN + 1:
                    continue
                if msg.dlc < 7:
                    continue
                resp_type = msg.data[0]
                if resp_type not in (RESP_NEED_NODEID, RESP_HAVE_NODEID):
                    continue
                # Extract UUID from data[1:7]
                found_uuid = sum(
                    v << ((5 - i) * 8)
                    for i, v in enumerate(msg.data[1:7])
                )
                if uuid is not None:
                    target = int(uuid, 16)
                    if found_uuid != target:
                        continue
                # Found a node
                self.packets_received += 1
                self.bytes_received += msg.dlc
                if resp_type == RESP_HAVE_NODEID:
                    # Node already has an ID
                    nodeid = msg.data[7]
                    logging.info(f"Found node {hex(found_uuid)} @ id={nodeid}")
                    return nodeid
                elif resp_type == RESP_NEED_NODEID:
                    # Node needs assignment, return 0 to indicate
                    logging.info(f"Found unassigned node {hex(found_uuid)}")
                    return 0
            return None
        except Exception as e:
            logging.error(f"Discovery error: {e}")
            return None

    def assign_nodeid(self, uuid: str, nodeid: int) -> bool:
        """Assign a node ID to an MCU.

        Sends SET_NODEID command on the admin channel.

        Args:
            uuid: 6-byte UUID hex string (e.g., 'a1b2c3d4e5f6')
            nodeid: Node ID to assign (0-127)

        Returns:
            True if command sent successfully
        """
        import can

        with self._lock:
            bus = self._bus
            if bus is None:
                return False

        try:
            uuid_bytes = [int(uuid[i:i+2], 16) for i in range(0, 12, 2)]
            data = [CMD_SET_NODEID] + uuid_bytes + [nodeid]
            msg = can.Message(
                arbitration_id=CANBUS_ID_ADMIN,
                data=data,
                is_extended_id=False,
            )
            bus.send(msg)
            self.packets_sent += 1
            self.bytes_sent += msg.dlc
            logging.info(f"Assigned nodeid={nodeid} to uuid={uuid}")
            return True
        except Exception as e:
            logging.error(f"SET_NODEID error: {e}")
            return False

    def connect_node(self, nodeid: int) -> bool:
        """Configure the CAN filter for a specific node ID.

        After this, the bus will only receive messages from this node.
        txid = nodeid * 2 + 0x100, rxid = txid + 1

        Args:
            nodeid: Node ID to connect to (0-127)

        Returns:
            True if filters set
        """
        import can

        with self._lock:
            bus = self._bus
            if bus is None:
                return False
            self._nodeid = nodeid
            self._txid = nodeid * 2 + 0x100
            self._rxid = self._txid + 1

        try:
            bus.set_filters([
                {"can_id": self._rxid, "can_mask": 0x7FF,
                 "extended": False},
            ])
            logging.info(f"CAN filter set: rxid=0x{self._rxid:X}")
            return True
        except Exception as e:
            logging.error(f"Set filter error: {e}")
            return False

    def send(self, data: Union[bytes, bytearray]) -> bool:
        """Send raw Kalico message block as a CAN data frame.

        The raw bytes become the CAN data payload.
        If data > 8 bytes, splits into multiple CAN frames.

        Args:
            data: Raw Kalico message block bytes

        Returns:
            True if successful
        """
        import can

        with self._lock:
            bus = self._bus
            if bus is None:
                return False
            txid = self._txid

        try:
            # CAN FD supports up to 64 bytes; standard CAN = 8
            max_dlc = 8
            offset = 0
            while offset < len(data):
                chunk = data[offset:offset + max_dlc]
                msg = can.Message(
                    arbitration_id=txid,
                    data=list(chunk),
                    is_extended_id=False,
                )
                bus.send(msg)
                self.packets_sent += 1
                self.bytes_sent += len(chunk)
                offset += max_dlc
            return True
        except Exception as e:
            logging.error(f"CAN send error: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def send_block(self, block: MessageBlock) -> bool:
        """Send a MessageBlock via CAN."""
        return self.send(block.encode())

    def _read_loop(self) -> None:
        """Background thread: continuously read CAN frames."""
        import can

        while self._running:
            try:
                with self._lock:
                    bus = self._bus
                    if bus is None:
                        break

                msg = bus.recv(timeout=0.1)
                if msg is None:
                    continue

                with self._lock:
                    self.bytes_received += msg.dlc
                    self.packets_received += 1

                data = bytes(msg.data)
                if self.on_data:
                    try:
                        self.on_data(data)
                    except Exception as e:
                        logging.error(f"on_data callback error: {e}")

            except can.CanError as e:
                if self._running:
                    logging.error(f"CAN read error: {e}")
                    if self.on_error:
                        self.on_error(e)
                break
            except Exception as e:
                logging.error(f"CAN read thread error: {e}")
                break

        # Just mark disconnected, don't call self.disconnect() (would deadlock)
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
                "type": "CAN",
                "interface": self._can_interface,
                "channel": self._can_channel,
                "bitrate": self._can_bitrate,
                "nodeid": self._nodeid,
                "state": self.state.value,
                "duration": round(duration, 1),
                "bytes_sent": self.bytes_sent,
                "bytes_received": self.bytes_received,
                "packets_sent": self.packets_sent,
                "packets_received": self.packets_received,
            }

    def is_connected(self) -> bool:
        return self.state == ConnectionState.CONNECTED
