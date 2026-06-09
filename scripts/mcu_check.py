#!/usr/bin/env python3
# MCU Configuration Checker and Device Discovery Tool
#
# Scans for serial, CAN, TCP, and UDP devices, validates printer.cfg
# configuration, and provides interactive configuration assistance.
#
# Copyright (C) 2026  Kalico contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import argparse
import configparser
import ipaddress
import json
import logging
import os
import platform
import socket
import struct
import sys
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Constants
CANBUS_ID_ADMIN = 0x3F0
CMD_QUERY_UNASSIGNED = 0x00
CMD_QUERY_UNASSIGNED_EXTENDED = 0x01
RESP_NEED_NODEID = 0x20
RESP_HAVE_NODEID = 0x21
RESP_KALICO_NODEID = 0x07
CMD_SET_KLIPPER_NODEID = 0x01
CMD_SET_CANBOOT_NODEID = 0x11

MESSAGE_SYNC = 0x7E
MESSAGE_MIN = 5
MESSAGE_MAX = 64

# Identify command packet (pre-computed)
IDENTIFY_PACKET = bytes([0x05, 0x01, 0x00, 0x7e, 0x00])

DEFAULT_TCP_PORTS = [5500, 7125, 8000]
DEFAULT_UDP_PORTS = [5500]

AppNames = {
    CMD_SET_KLIPPER_NODEID: "Klipper",
    RESP_KALICO_NODEID: "Kalico",
    CMD_SET_CANBOOT_NODEID: "Katapult",
}

BUS_STATE_NAMES = {
    0: "ACTIVE",
    1: "WARNING",
    2: "PASSIVE",
    3: "OFF",
}

# Known MCU USB VID:PID pairs
KNOWN_MCU_DEVICES = {
    # STM32
    (0x1D50, 0x6177): "Katapult/Canboot STM32 Bootloader",
    (0x0483, 0x5740): "STM32 USB-Serial",
    (0x0483, 0xDF11): "STM32 DFU Bootloader",
    # RP2040/RP2350
    (0x2E8A, 0x000A): "Raspberry Pi Pico/RP2040",
    (0x2E8A, 0x0009): "Raspberry Pi Pico (CDC)",
    (0x2E8A, 0x000F): "Raspberry Pi RP2350",
    (0x1D50, 0x6177): "Katapult RP2040/RP2350",
    # ATSAM
    (0x1D50, 0x6177): "Katapult ATSAM Bootloader",
    (0x03EB, 0x6124): "AT91SAM3U (Arduino Due)",
    # CH340/CH341 USB-Serial
    (0x1A86, 0x7523): "CH340 USB-Serial",
    (0x1A86, 0x5523): "CH341 USB-Serial",
    # FTDI
    (0x0403, 0x6001): "FTDI USB-Serial",
    (0x0403, 0x6015): "FTDI FT230X",
    # CP210x
    (0x10C4, 0xEA60): "CP2102/CP2104 USB-Serial",
    # Prolific
    (0x067B, 0x2303): "PL2303 USB-Serial",
}


@dataclass
class DeviceInfo:
    """Information about a discovered device."""
    device_type: str  # serial, can, tcp, udp
    path: str  # Device path or address
    description: str = ""
    vid: Optional[int] = None
    pid: Optional[int] = None
    serial_number: Optional[str] = None
    manufacturer: Optional[str] = None
    product: Optional[str] = None
    is_kalico: bool = False
    firmware_info: Optional[str] = None
    baudrate: Optional[int] = None
    extra_info: Dict = field(default_factory=dict)

    @property
    def identity(self) -> str:
        """Return a unique identity string for this device."""
        if self.device_type == "serial":
            return f"serial:{self.path}"
        elif self.device_type == "can":
            return f"can:{self.path}"
        elif self.device_type in ("tcp", "udp"):
            return f"{self.device_type}:{self.path}"
        return self.path

    @property
    def display_type(self) -> str:
        """Return a human-readable type string."""
        if self.vid and self.pid:
            known = KNOWN_MCU_DEVICES.get((self.vid, self.pid))
            if known:
                return known
            return f"USB Device ({self.vid:04X}:{self.pid:04X})"
        return self.device_type.upper()


@dataclass
class MCUConfig:
    """Parsed MCU configuration from printer.cfg."""
    name: str  # Section name (e.g., "mcu", "mcu extruder")
    transport: str  # serial, can, tcp, udp
    serial: Optional[str] = None
    baud: int = 250000
    canbus_uuid: Optional[str] = None
    canbus_interface: str = "can0"
    tcp_host: Optional[str] = None
    tcp_port: int = 5500
    udp_host: Optional[str] = None
    udp_port: int = 5500
    restart_method: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Return display name without 'mcu ' prefix."""
        if self.name.startswith("mcu "):
            return self.name[4:]
        return self.name


@dataclass
class CheckResult:
    """Result of checking an MCU config against discovered devices."""
    mcu_config: MCUConfig
    matched_device: Optional[DeviceInfo] = None
    is_responsive: bool = False
    firmware_version: Optional[str] = None
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)


class CRC16:
    """CRC-16/CCITT-FALSE calculator."""

    def __init__(self):
        self._table = self._build_table()

    def _build_table(self) -> list:
        table = []
        for i in range(256):
            crc = i << 8
            for _ in range(8):
                if crc & 0x8000:
                    crc = (crc << 1) ^ 0x1021
                else:
                    crc <<= 1
                crc &= 0xFFFF
            table.append(crc)
        return table

    def update(self, data: bytes) -> int:
        crc = 0
        for byte in data:
            crc = ((crc << 8) & 0xFFFF) ^ self._table[((crc >> 8) ^ byte) & 0xFF]
        return crc


crc16 = CRC16()


def get_local_interfaces() -> List[Tuple[str, str, str]]:
    """Get local network interfaces.

    Returns list of (name, ip, netmask) tuples.
    """
    interfaces = []
    if platform.system() == "Windows":
        try:
            import netifaces
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        netmask = addr.get('netmask')
                        if ip and netmask and not ip.startswith('127.'):
                            interfaces.append((iface, ip, netmask))
        except ImportError:
            # Fallback: get hostname IP
            hostname = socket.gethostname()
            try:
                ip = socket.gethostbyname(hostname)
                interfaces.append(("default", ip, "255.255.255.0"))
            except socket.error:
                pass
    else:
        try:
            import netifaces
            for iface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(iface)
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        ip = addr.get('addr')
                        netmask = addr.get('netmask')
                        if ip and netmask and not ip.startswith('127.'):
                            interfaces.append((iface, ip, netmask))
        except ImportError:
            # Fallback for Linux
            try:
                import fcntl
                import struct
                for iface_name in os.listdir('/sys/class/net/'):
                    if iface_name == 'lo':
                        continue
                    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    try:
                        ip_addr = socket.inet_ntoa(fcntl.ioctl(
                            sock.fileno(),
                            0x8915,  # SIOCGIFADDR
                            struct.pack('256s', iface_name[:15].encode())
                        )[20:24])
                        netmask = socket.inet_ntoa(fcntl.ioctl(
                            sock.fileno(),
                            0x891B,  # SIOCGIFNETMASK
                            struct.pack('256s', iface_name[:15].encode())
                        )[20:24])
                        interfaces.append((iface_name, ip_addr, netmask))
                    except (IOError, OSError):
                        pass
                    finally:
                        sock.close()
            except (ImportError, OSError):
                # Final fallback
                hostname = socket.gethostname()
                try:
                    ip = socket.gethostbyname(hostname)
                    interfaces.append(("default", ip, "255.255.255.0"))
                except socket.error:
                    pass
    return interfaces


def get_subnet_hosts(ip: str, netmask: str) -> List[str]:
    """Get all hosts in a subnet."""
    try:
        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
        # Skip network and broadcast addresses, limit to reasonable size
        hosts = [str(h) for h in network.hosts()]
        if len(hosts) > 1024:
            # Too many hosts, just scan nearby
            base = ipaddress.IPv4Address(ip)
            hosts = [str(base + i) for i in range(-50, 51) if base + i in network]
        return hosts
    except (ValueError, ipaddress.AddressValueError):
        return [ip]


class SerialScanner:
    """Scan for serial port devices."""

    @staticmethod
    def list_ports() -> List[DeviceInfo]:
        """List all available serial ports with detailed info."""
        devices = []
        try:
            import serial.tools.list_ports
            for port_info in serial.tools.list_ports.comports():
                device = DeviceInfo(
                    device_type="serial",
                    path=port_info.device,
                    description=port_info.description or "",
                    vid=port_info.vid,
                    pid=port_info.pid,
                    serial_number=port_info.serial_number,
                    manufacturer=port_info.manufacturer,
                    product=port_info.product,
                )
                # Check if it's a known MCU device
                if device.vid and device.pid:
                    known = KNOWN_MCU_DEVICES.get((device.vid, device.pid))
                    if known:
                        device.description = known
                        if "Katapult" in known or "Bootloader" in known:
                            device.is_kalico = True
                devices.append(device)
        except ImportError:
            # Fallback for systems without pyserial
            if platform.system() != "Windows":
                # Linux: scan /dev/ttyUSB* and /dev/ttyACM*
                for pattern in ['/dev/ttyUSB*', '/dev/ttyACM*']:
                    import glob
                    for dev_path in glob.glob(pattern):
                        devices.append(DeviceInfo(
                            device_type="serial",
                            path=dev_path,
                            description="Serial device",
                        ))
                # Also scan /dev/serial/by-id/
                by_id_path = '/dev/serial/by-id/'
                if os.path.exists(by_id_path):
                    for link_name in os.listdir(by_id_path):
                        full_path = os.path.join(by_id_path, link_name)
                        real_path = os.path.realpath(full_path)
                        devices.append(DeviceInfo(
                            device_type="serial",
                            path=real_path,
                            description=link_name,
                        ))
        return devices

    @staticmethod
    def probe_kalico(port: str, baudrate: int = 250000,
                     timeout: float = 0.5) -> bool:
        """Probe a serial port for Kalico protocol response."""
        try:
            import serial
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout,
                exclusive=False,
            )
            time.sleep(0.05)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(IDENTIFY_PACKET)

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
                # Look for valid message
                while len(data) >= MESSAGE_MIN:
                    for scan_pos in range(len(data)):
                        blen = data[scan_pos]
                        if blen < MESSAGE_MIN or blen > MESSAGE_MAX:
                            continue
                        end_pos = scan_pos + blen
                        if end_pos > len(data):
                            break
                        sync_pos = end_pos - 1
                        if data[sync_pos] != MESSAGE_SYNC:
                            continue
                        body = data[scan_pos:end_pos - 3]
                        expected_crc = data[end_pos - 3:end_pos - 1]
                        actual_crc = bytes([crc16.update(body) >> 8,
                                           crc16.update(body) & 0xFF])
                        if expected_crc == actual_crc:
                            ser.close()
                            return True
                    data = data[1:]
            ser.close()
            return False
        except Exception:
            return False

    @staticmethod
    def get_kalico_info(port: str, baudrate: int = 250000,
                        timeout: float = 1.0) -> Optional[Dict]:
        """Get detailed Kalico firmware info from a serial port."""
        try:
            import serial
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                timeout=timeout,
                write_timeout=timeout,
                exclusive=False,
            )
            time.sleep(0.05)
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            ser.write(IDENTIFY_PACKET)

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
                # Try to parse identify response
                if len(data) >= MESSAGE_MIN:
                    try:
                        # Simple parsing - just look for app info
                        text = data.decode('ascii', errors='ignore')
                        if 'kalico' in text.lower() or 'klipper' in text.lower():
                            ser.close()
                            return {"raw": text[:200]}
                    except Exception:
                        pass
            ser.close()
        except Exception:
            pass
        return None


class CANScanner:
    """Scan for CAN bus devices."""

    @staticmethod
    def list_interfaces() -> List[Dict]:
        """List available CAN interfaces."""
        interfaces = []
        if platform.system() == "Linux":
            sys_net = "/sys/class/net"
            if os.path.exists(sys_net):
                for iface_name in os.listdir(sys_net):
                    if not iface_name.startswith("can"):
                        # Also check for other CAN interface names
                        iface_path = os.path.join(sys_net, iface_name)
                        type_path = os.path.join(iface_path, "type")
                        if os.path.exists(type_path):
                            try:
                                with open(type_path) as f:
                                    iface_type = f.read().strip()
                                if iface_type == "280":  # ARPHRD_CAN
                                    interfaces.append({
                                        "name": iface_name,
                                        "type": "can",
                                    })
                                    continue
                            except (IOError, ValueError):
                                pass
                        continue
                    iface_path = os.path.join(sys_net, iface_name)
                    state = "UNKNOWN"
                    bitrate = None
                    try:
                        operstate_path = os.path.join(iface_path, "operstate")
                        if os.path.exists(operstate_path):
                            with open(operstate_path) as f:
                                state = f.read().strip().upper()
                        bitrate_path = os.path.join(iface_path, "can_bittiming/bitrate")
                        if os.path.exists(bitrate_path):
                            with open(bitrate_path) as f:
                                bitrate = int(f.read().strip())
                    except (IOError, ValueError):
                        pass
                    interfaces.append({
                        "name": iface_name,
                        "type": "can",
                        "state": state,
                        "bitrate": bitrate,
                    })
        elif platform.system() == "Windows":
            # Check for common Windows CAN interfaces
            try:
                import can
                # Try to list PCAN channels
                try:
                    from can.interfaces.pcan import PcanBus
                    for i in range(8):
                        channel = f"PCAN_USBBUS{i+1}"
                        try:
                            bus = can.interface.Bus(channel=channel, bustype="pcan")
                            bus.shutdown()
                            interfaces.append({
                                "name": channel,
                                "type": "pcan",
                            })
                        except Exception:
                            pass
                except ImportError:
                    pass
                # Try slcan (serial-line CAN)
                import serial.tools.list_ports
                for port_info in serial.tools.list_ports.comports():
                    if "CAN" in (port_info.description or "").upper():
                        interfaces.append({
                            "name": port_info.device,
                            "type": "slcan",
                        })
            except ImportError:
                pass
        return interfaces

    @staticmethod
    def scan_devices(iface: str, timeout: float = 2.0,
                     iface_type: str = "socketcan") -> List[DeviceInfo]:
        """Scan a CAN interface for devices."""
        devices = []
        try:
            import can
            filters = [
                {"can_id": CANBUS_ID_ADMIN + 1, "can_mask": 0x7FF, "extended": False}
            ]
            try:
                bus = can.interface.Bus(
                    channel=iface,
                    can_filters=filters,
                    bustype=iface_type,
                )
            except Exception as e:
                logging.debug(f"Cannot open CAN interface {iface}: {e}")
                return devices

            msg = can.Message(
                arbitration_id=CANBUS_ID_ADMIN,
                data=[CMD_QUERY_UNASSIGNED, CMD_QUERY_UNASSIGNED_EXTENDED],
                is_extended_id=False,
            )
            try:
                bus.send(msg)
            except Exception:
                bus.shutdown()
                return devices

            found_uuids = set()
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    msg = bus.recv(min(timeout - (time.time() - start_time), 0.5))
                except Exception:
                    break
                if msg is None:
                    continue
                if (
                    msg.arbitration_id != CANBUS_ID_ADMIN + 1
                    or msg.dlc < 7
                    or msg.data[0] not in (RESP_NEED_NODEID, RESP_HAVE_NODEID)
                ):
                    continue

                uuid = sum(v << ((5 - i) * 8) for i, v in enumerate(msg.data[1:7]))
                if uuid in found_uuids:
                    continue
                found_uuids.add(uuid)

                app_id = CMD_SET_KLIPPER_NODEID
                node_id = None
                if msg.dlc > 7:
                    app_id = msg.data[7]
                status = "Unassigned"
                if msg.data[0] == RESP_HAVE_NODEID:
                    node_id = app_id
                    app_id = RESP_KALICO_NODEID
                    status = "Assigned"
                app_name = AppNames.get(app_id, "Unknown")

                device = DeviceInfo(
                    device_type="can",
                    path=f"{uuid:012X}",
                    description=f"{app_name} ({status})",
                    extra_info={
                        "uuid": uuid,
                        "uuid_hex": f"{uuid:012X}",
                        "app_name": app_name,
                        "app_id": app_id,
                        "node_id": node_id,
                        "status": status,
                        "interface": iface,
                    },
                )
                if app_name in ("Kalico", "Klipper"):
                    device.is_kalico = True
                devices.append(device)

            bus.shutdown()
        except ImportError:
            logging.debug("python-can library not installed")
        return devices


class NetworkScanner:
    """Scan for TCP/UDP devices on the local network."""

    @staticmethod
    def scan_udp_broadcast(port: int = 5500, timeout: float = 2.0,
                           broadcast_addr: str = None) -> List[DeviceInfo]:
        """Scan for UDP devices using broadcast."""
        devices = []
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(timeout)

            # Send identify packet via broadcast
            if broadcast_addr:
                target = broadcast_addr
            else:
                target = '<broadcast>'

            try:
                sock.sendto(IDENTIFY_PACKET, (target, port))
            except OSError:
                # Try specific broadcast addresses
                for iface_name, ip, netmask in get_local_interfaces():
                    try:
                        network = ipaddress.IPv4Network(f"{ip}/{netmask}", strict=False)
                        bcast = str(network.broadcast_address)
                        sock.sendto(IDENTIFY_PACKET, (bcast, port))
                    except Exception:
                        pass

            # Collect responses
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    data, addr = sock.recvfrom(1024)
                    if addr not in [(d.path, None) for d in devices]:
                        # Check if it looks like a Kalico response
                        is_kalico = False
                        if len(data) >= MESSAGE_MIN:
                            for scan_pos in range(len(data)):
                                blen = data[scan_pos]
                                if blen < MESSAGE_MIN or blen > MESSAGE_MAX:
                                    continue
                                end_pos = scan_pos + blen
                                if end_pos > len(data):
                                    break
                                if data[end_pos - 1] == MESSAGE_SYNC:
                                    is_kalico = True
                                    break
                        device = DeviceInfo(
                            device_type="udp",
                            path=f"{addr[0]}:{addr[1]}",
                            description="UDP MCU" if is_kalico else "UDP Device",
                            is_kalico=is_kalico,
                            extra_info={"ip": addr[0], "port": addr[1]},
                        )
                        devices.append(device)
                except socket.timeout:
                    break
                except Exception:
                    break
            sock.close()
        except Exception as e:
            logging.debug(f"UDP broadcast scan error: {e}")
        return devices

    @staticmethod
    def scan_tcp_port(host: str, port: int, timeout: float = 1.0) -> Optional[DeviceInfo]:
        """Check if a TCP port is open and probe for Kalico protocol."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((host, port))
            if result != 0:
                sock.close()
                return None

            # Port is open, try to probe for Kalico
            sock.settimeout(timeout)
            try:
                sock.send(IDENTIFY_PACKET)
                data = sock.recv(1024)
                is_kalico = False
                if len(data) >= MESSAGE_MIN:
                    for scan_pos in range(len(data)):
                        blen = data[scan_pos]
                        if blen < MESSAGE_MIN or blen > MESSAGE_MAX:
                            continue
                        end_pos = scan_pos + blen
                        if end_pos > len(data):
                            break
                        if data[end_pos - 1] == MESSAGE_SYNC:
                            is_kalico = True
                            break
            except Exception:
                is_kalico = False

            sock.close()
            return DeviceInfo(
                device_type="tcp",
                path=f"{host}:{port}",
                description="TCP MCU" if is_kalico else "TCP Device (open port)",
                is_kalico=is_kalico,
                extra_info={"ip": host, "port": port},
            )
        except Exception:
            return None

    @staticmethod
    def scan_network(subnet: str = None, ports: List[int] = None,
                     timeout: float = 0.5, max_threads: int = 50,
                     progress_callback=None) -> List[DeviceInfo]:
        """Scan local network for TCP/UDP devices."""
        devices = []
        if ports is None:
            ports = DEFAULT_TCP_PORTS

        # Get hosts to scan
        hosts = []
        if subnet:
            try:
                network = ipaddress.IPv4Network(subnet, strict=False)
                hosts = [str(h) for h in network.hosts()]
                if len(hosts) > 1024:
                    logging.warning(f"Subnet too large ({len(hosts)} hosts), limiting scan")
                    hosts = hosts[:1024]
            except ValueError:
                hosts = [subnet]
        else:
            for iface_name, ip, netmask in get_local_interfaces():
                iface_hosts = get_subnet_hosts(ip, netmask)
                hosts.extend(iface_hosts)
            hosts = list(set(hosts))

        # First try UDP broadcast
        for port in DEFAULT_UDP_PORTS:
            if progress_callback:
                progress_callback(f"Scanning UDP broadcast on port {port}...")
            udp_devices = NetworkScanner.scan_udp_broadcast(port, timeout=timeout * 2)
            devices.extend(udp_devices)

        # Then scan TCP ports
        total_tasks = len(hosts) * len(ports)
        completed = 0
        lock = threading.Lock()

        def scan_task(host, port):
            nonlocal completed
            device = NetworkScanner.scan_tcp_port(host, port, timeout=timeout)
            if device:
                with lock:
                    devices.append(device)
            with lock:
                completed += 1
                if progress_callback and completed % 100 == 0:
                    progress_callback(f"Scanning TCP... {completed}/{total_tasks}")

        # Use thread pool for scanning
        threads = []
        for host in hosts:
            for port in ports:
                while len(threads) >= max_threads:
                    threads = [t for t in threads if t.is_alive()]
                    if len(threads) >= max_threads:
                        time.sleep(0.01)
                t = threading.Thread(target=scan_task, args=(host, port))
                t.daemon = True
                t.start()
                threads.append(t)

        # Wait for all threads
        for t in threads:
            t.join(timeout=timeout * 2)

        if progress_callback:
            progress_callback(f"Network scan complete. Found {len(devices)} device(s).")

        return devices


class PrinterConfigParser:
    """Parse printer.cfg to extract MCU configurations."""

    @staticmethod
    def find_config(config_path: str = None) -> Optional[str]:
        """Find printer.cfg file."""
        if config_path:
            if os.path.exists(config_path):
                return config_path
            return None

        # Common locations
        search_paths = [
            os.path.expanduser("~/printer_data/config/printer.cfg"),
            os.path.expanduser("~/klipper_config/printer.cfg"),
            os.path.expanduser("~/.config/klipper/printer.cfg"),
            "/etc/klipper/printer.cfg",
            "printer.cfg",
        ]
        for path in search_paths:
            if os.path.exists(path):
                return path
        return None

    @staticmethod
    def parse_config(config_path: str) -> List[MCUConfig]:
        """Parse printer.cfg and extract MCU configurations."""
        mcus = []
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_path)

        for section in config.sections():
            if section == "mcu" or section.startswith("mcu "):
                mcu = MCUConfig(name=section)

                # Determine transport type
                if config.has_option(section, "tcp_host"):
                    mcu.transport = "tcp"
                    mcu.tcp_host = config.get(section, "tcp_host")
                    mcu.tcp_port = config.getint(section, "tcp_port", fallback=5500)
                elif config.has_option(section, "udp_host"):
                    mcu.transport = "udp"
                    mcu.udp_host = config.get(section, "udp_host")
                    mcu.udp_port = config.getint(section, "udp_port", fallback=5500)
                elif config.has_option(section, "canbus_uuid"):
                    mcu.transport = "can"
                    mcu.canbus_uuid = config.get(section, "canbus_uuid")
                    mcu.canbus_interface = config.get(section, "canbus_interface",
                                                       fallback="can0")
                else:
                    mcu.transport = "serial"
                    mcu.serial = config.get(section, "serial", fallback=None)
                    mcu.baud = config.getint(section, "baud", fallback=250000)

                # Optional settings
                if config.has_option(section, "restart_method"):
                    mcu.restart_method = config.get(section, "restart_method")

                mcus.append(mcu)

        return mcus

    @staticmethod
    def update_config(config_path: str, mcu_name: str,
                      updates: Dict[str, str]) -> bool:
        """Update MCU configuration in printer.cfg."""
        try:
            with open(config_path, 'r') as f:
                lines = f.readlines()

            in_section = False
            section_indent = 0
            updated_keys = set()

            for i, line in enumerate(lines):
                stripped = line.strip()
                if stripped.startswith('['):
                    if in_section:
                        # End of section, add any remaining keys
                        break
                    if stripped == f'[{mcu_name}]':
                        in_section = True
                        section_indent = len(line) - len(line.lstrip())
                        continue
                elif in_section:
                    if stripped and not stripped.startswith('#'):
                        for key, value in updates.items():
                            if stripped.startswith(f'{key}:') or stripped.startswith(f'{key} ='):
                                lines[i] = ' ' * section_indent + f'{key}: {value}\n'
                                updated_keys.add(key)

            # Add any keys that weren't found
            if in_section:
                for key, value in updates.items():
                    if key not in updated_keys:
                        insert_pos = i
                        lines.insert(insert_pos, ' ' * section_indent + f'{key}: {value}\n')

            with open(config_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            logging.error(f"Failed to update config: {e}")
            return False


class MCUChecker:
    """Main MCU configuration checker."""

    def __init__(self, config_path: str = None, verbose: bool = False):
        self.config_path = config_path
        self.verbose = verbose
        self.serial_scanner = SerialScanner()
        self.can_scanner = CANScanner()
        self.network_scanner = NetworkScanner()
        self.config_parser = PrinterConfigParser()

    def check_all(self, scan_network: bool = False,
                  network_subnet: str = None) -> List[CheckResult]:
        """Run all checks and return results."""
        results = []

        # Find and parse config
        config_file = self.config_parser.find_config(self.config_path)
        if not config_file:
            print("ERROR: Could not find printer.cfg")
            print("Searched in:")
            print("  ~/printer_data/config/printer.cfg")
            print("  ~/klipper_config/printer.cfg")
            print("  ~/.config/klipper/printer.cfg")
            print("  /etc/klipper/printer.cfg")
            print("  ./printer.cfg")
            print("\nUse --config to specify the path.")
            return results

        print(f"Reading config: {config_file}")
        mcu_configs = self.config_parser.parse_config(config_file)

        if not mcu_configs:
            print("No MCU configurations found in printer.cfg")
            return results

        print(f"Found {len(mcu_configs)} MCU configuration(s):\n")
        for mcu in mcu_configs:
            self._print_mcu_config(mcu)

        # Scan for devices
        print("\n" + "=" * 60)
        print("Scanning for devices...")
        print("=" * 60 + "\n")

        # Scan serial ports
        print("[Serial Ports]")
        serial_devices = self.serial_scanner.list_ports()
        if serial_devices:
            for dev in serial_devices:
                self._print_device(dev)
        else:
            print("  No serial ports found")

        # Scan CAN interfaces
        print("\n[CAN Interfaces]")
        can_ifaces = self.can_scanner.list_interfaces()
        can_devices = []
        if can_ifaces:
            for iface_info in can_ifaces:
                iface_name = iface_info['name']
                iface_type = iface_info.get('type', 'socketcan')
                state = iface_info.get('state', 'UNKNOWN')
                bitrate = iface_info.get('bitrate')
                print(f"  {iface_name}: {state}", end="")
                if bitrate:
                    print(f", {bitrate // 1000}Kbps", end="")
                print()
                devs = self.can_scanner.scan_devices(iface_name, iface_type=iface_type)
                can_devices.extend(devs)
                for dev in devs:
                    self._print_device(dev, indent=4)
        else:
            print("  No CAN interfaces found")

        # Scan network if requested
        network_devices = []
        if scan_network:
            print("\n[Network Scan]")
            network_devices = self.network_scanner.scan_network(
                subnet=network_subnet,
                progress_callback=lambda msg: print(f"  {msg}")
            )
            for dev in network_devices:
                self._print_device(dev)

        # Match configs to devices
        print("\n" + "=" * 60)
        print("Configuration Validation")
        print("=" * 60 + "\n")

        all_devices = serial_devices + can_devices + network_devices
        for mcu in mcu_configs:
            result = self._check_mcu_config(mcu, all_devices)
            results.append(result)
            self._print_check_result(result)

        return results

    def _print_mcu_config(self, mcu: MCUConfig):
        """Print MCU configuration details."""
        print(f"  [{mcu.display_name}]")
        if mcu.transport == "serial":
            print(f"    Transport: Serial")
            print(f"    Port: {mcu.serial}")
            print(f"    Baud: {mcu.baud}")
        elif mcu.transport == "can":
            print(f"    Transport: CAN")
            print(f"    UUID: {mcu.canbus_uuid}")
            print(f"    Interface: {mcu.canbus_interface}")
        elif mcu.transport == "tcp":
            print(f"    Transport: TCP")
            print(f"    Host: {mcu.tcp_host}:{mcu.tcp_port}")
        elif mcu.transport == "udp":
            print(f"    Transport: UDP")
            print(f"    Host: {mcu.udp_host}:{mcu.udp_port}")
        if mcu.restart_method:
            print(f"    Restart Method: {mcu.restart_method}")
        print()

    def _print_device(self, device: DeviceInfo, indent: int = 2):
        """Print device information."""
        prefix = " " * indent
        type_str = device.display_type
        print(f"{prefix}{device.path} - {type_str}")
        if device.description and device.description != type_str:
            print(f"{prefix}  Description: {device.description}")
        if device.serial_number:
            print(f"{prefix}  Serial: {device.serial_number}")
        if device.manufacturer:
            print(f"{prefix}  Manufacturer: {device.manufacturer}")
        if device.is_kalico:
            print(f"{prefix}  * Kalico/Klipper device detected")
        if device.firmware_info:
            print(f"{prefix}  Firmware: {device.firmware_info}")
        print()

    def _check_mcu_config(self, mcu: MCUConfig,
                          devices: List[DeviceInfo]) -> CheckResult:
        """Check an MCU configuration against discovered devices."""
        result = CheckResult(mcu_config=mcu)

        if mcu.transport == "serial":
            self._check_serial_config(mcu, devices, result)
        elif mcu.transport == "can":
            self._check_can_config(mcu, devices, result)
        elif mcu.transport == "tcp":
            self._check_tcp_config(mcu, devices, result)
        elif mcu.transport == "udp":
            self._check_udp_config(mcu, devices, result)

        return result

    def _check_serial_config(self, mcu: MCUConfig, devices: List[DeviceInfo],
                             result: CheckResult):
        """Check serial MCU configuration."""
        if not mcu.serial:
            result.issues.append("No serial port configured")
            result.suggestions.append("Add 'serial: /dev/ttyUSB0' to printer.cfg")
            return

        # Find matching device
        for dev in devices:
            if dev.device_type == "serial":
                if (dev.path == mcu.serial or
                    os.path.realpath(dev.path) == os.path.realpath(mcu.serial)):
                    result.matched_device = dev
                    break

        if not result.matched_device:
            # Check if path exists at all
            if os.path.exists(mcu.serial):
                result.issues.append(
                    f"Configured port '{mcu.serial}' exists but not detected as serial device"
                )
            else:
                result.issues.append(
                    f"Configured port '{mcu.serial}' does not exist"
                )
            result.suggestions.extend([
                "Check if device is connected",
                "Run 'ls /dev/ttyUSB* /dev/ttyACM* /dev/serial/by-id/' to see available ports",
                "Update 'serial' in printer.cfg to correct port",
            ])
            # Suggest alternative ports
            serial_devs = [d for d in devices if d.device_type == "serial"]
            if serial_devs:
                result.suggestions.append(
                    f"Available ports: {', '.join(d.path for d in serial_devs)}"
                )
            return

        # Device found, check if it's responsive
        dev = result.matched_device
        result.is_responsive = self.serial_scanner.probe_kalico(dev.path, mcu.baud)
        if result.is_responsive:
            result.firmware_version = "Detected (Kalico protocol)"
        else:
            result.issues.append(
                f"Port '{mcu.serial}' exists but not responding to Kalico protocol"
            )
            result.suggestions.extend([
                "Firmware may not be flashed (recompile and flash)",
                "Wrong baud rate (verify firmware baud setting)",
                "Device may be in bootloader mode (try reflash)",
            ])

    def _check_can_config(self, mcu: MCUConfig, devices: List[DeviceInfo],
                          result: CheckResult):
        """Check CAN MCU configuration."""
        if not mcu.canbus_uuid:
            result.issues.append("No CAN UUID configured")
            result.suggestions.append("Add 'canbus_uuid: <uuid>' to printer.cfg")
            return

        uuid_upper = mcu.canbus_uuid.upper()

        # Find matching device
        for dev in devices:
            if dev.device_type == "can":
                dev_uuid = dev.extra_info.get("uuid_hex", "").upper()
                if dev_uuid == uuid_upper:
                    result.matched_device = dev
                    break

        if not result.matched_device:
            result.issues.append(
                f"CAN UUID '{mcu.canbus_uuid}' not found on bus '{mcu.canbus_interface}'"
            )
            result.suggestions.extend([
                f"Run 'python3 scripts/canbus_query.py' to scan for CAN devices",
                f"Check CAN interface is up: 'ip link set {mcu.canbus_interface} up type can bitrate 500000'",
                "Verify UUID in printer.cfg matches device UUID",
                "Check USB-CAN bridge connection",
            ])
            # List found UUIDs
            can_devs = [d for d in devices if d.device_type == "can"]
            if can_devs:
                result.suggestions.append(
                    f"Found CAN devices: {', '.join(d.path for d in can_devs)}"
                )
        else:
            dev = result.matched_device
            result.is_responsive = True
            status = dev.extra_info.get("status", "Unknown")
            app = dev.extra_info.get("app_name", "Unknown")
            result.firmware_version = f"{app} ({status})"

    def _check_tcp_config(self, mcu: MCUConfig, devices: List[DeviceInfo],
                          result: CheckResult):
        """Check TCP MCU configuration."""
        if not mcu.tcp_host:
            result.issues.append("No TCP host configured")
            result.suggestions.append("Add 'tcp_host: <ip>' to printer.cfg")
            return

        target = f"{mcu.tcp_host}:{mcu.tcp_port}"

        # Find matching device
        for dev in devices:
            if dev.device_type == "tcp" and dev.path == target:
                result.matched_device = dev
                break

        if not result.matched_device:
            # Try to connect directly
            device = self.network_scanner.scan_tcp_port(mcu.tcp_host, mcu.tcp_port)
            if device:
                result.matched_device = device
                result.is_responsive = device.is_kalico
            else:
                result.issues.append(
                    f"Cannot connect to TCP {target}"
                )
                result.suggestions.extend([
                    f"Check if remote host '{mcu.tcp_host}' is reachable (ping {mcu.tcp_host})",
                    f"Check if port {mcu.tcp_port} is open on remote host",
                    "Verify firewall rules allow TCP connections",
                    "Check MCU firmware is configured for TCP",
                ])
        else:
            result.is_responsive = result.matched_device.is_kalico

    def _check_udp_config(self, mcu: MCUConfig, devices: List[DeviceInfo],
                          result: CheckResult):
        """Check UDP MCU configuration."""
        if not mcu.udp_host:
            result.issues.append("No UDP host configured")
            result.suggestions.append("Add 'udp_host: <ip>' to printer.cfg")
            return

        target = f"{mcu.udp_host}:{mcu.udp_port}"

        # Find matching device
        for dev in devices:
            if dev.device_type == "udp" and dev.path == target:
                result.matched_device = dev
                break

        if not result.matched_device:
            result.issues.append(
                f"UDP device at {target} not found via broadcast"
            )
            result.suggestions.extend([
                f"Check if remote host '{mcu.udp_host}' is reachable (ping {mcu.udp_host})",
                f"Check if port {mcu.udp_port} is open on remote host",
                "Verify firewall rules allow UDP traffic",
                "Check MCU firmware is configured for UDP",
            ])
        else:
            result.is_responsive = result.matched_device.is_kalico

    def _print_check_result(self, result: CheckResult):
        """Print check result for an MCU."""
        mcu = result.mcu_config
        print(f"[{mcu.display_name}]")

        if result.matched_device:
            dev = result.matched_device
            status = "OK" if result.is_responsive else "WARNING"
            print(f"  Status: {status}")
            print(f"  Device: {dev.path}")
            if result.firmware_version:
                print(f"  Firmware: {result.firmware_version}")
        else:
            print(f"  Status: ERROR - Device not found")

        if result.issues:
            print(f"  Issues:")
            for issue in result.issues:
                print(f"    ! {issue}")

        if result.suggestions:
            print(f"  Suggestions:")
            for suggestion in result.suggestions:
                print(f"    -> {suggestion}")

        print()

    def interactive_fix(self, results: List[CheckResult]):
        """Interactive configuration fix wizard."""
        config_file = self.config_parser.find_config(self.config_path)
        if not config_file:
            print("ERROR: Cannot find printer.cfg for interactive fix")
            return

        # Find problematic configs
        problem_results = [r for r in results if r.issues]
        if not problem_results:
            print("All MCU configurations appear correct. No fixes needed.")
            return

        print("\n" + "=" * 60)
        print("Interactive Configuration Fix")
        print("=" * 60)
        print(f"\nConfig file: {config_file}")
        print(f"Found {len(problem_results)} MCU(s) with issues.\n")

        # List all available devices
        all_serial = self.serial_scanner.list_ports()
        can_devices = []
        for iface in self.can_scanner.list_interfaces():
            can_devices.extend(self.can_scanner.scan_devices(iface['name']))

        for i, result in enumerate(problem_results):
            mcu = result.mcu_config
            print(f"\n--- [{mcu.display_name}] ---")
            print(f"Current config: {mcu.transport}")

            if result.issues:
                for issue in result.issues:
                    print(f"  Issue: {issue}")

            print("\nOptions:")
            print("  1. Update serial port")
            print("  2. Update CAN UUID")
            print("  3. Update TCP host/port")
            print("  4. Update UDP host/port")
            print("  5. Skip this MCU")
            print("  6. Quit")

            try:
                choice = input("\nSelect option (1-6): ").strip()
            except (EOFError, KeyboardInterrupt):
                print("\nAborted.")
                return

            if choice == "1":
                self._fix_serial(mcu, all_serial, config_file)
            elif choice == "2":
                self._fix_can(mcu, can_devices, config_file)
            elif choice == "3":
                self._fix_tcp(mcu, config_file)
            elif choice == "4":
                self._fix_udp(mcu, config_file)
            elif choice == "5":
                continue
            elif choice == "6":
                break

    def _fix_serial(self, mcu: MCUConfig, devices: List[DeviceInfo],
                    config_file: str):
        """Interactive serial port fix."""
        serial_devs = [d for d in devices if d.device_type == "serial"]
        if not serial_devs:
            print("No serial devices found!")
            return

        print("\nAvailable serial ports:")
        for i, dev in enumerate(serial_devs):
            print(f"  {i + 1}. {dev.path} - {dev.display_type}")
            if dev.serial_number:
                print(f"     Serial: {dev.serial_number}")

        try:
            choice = input("\nSelect port number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return
            idx = int(choice) - 1
            if 0 <= idx < len(serial_devs):
                selected = serial_devs[idx]
                updates = {"serial": selected.path}
                if self.config_parser.update_config(config_file, mcu.name, updates):
                    print(f"Updated {mcu.name}: serial = {selected.path}")
                else:
                    print("Failed to update config file")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("Cancelled.")

    def _fix_can(self, mcu: MCUConfig, devices: List[DeviceInfo],
                 config_file: str):
        """Interactive CAN UUID fix."""
        can_devs = [d for d in devices if d.device_type == "can"]
        if not can_devs:
            print("No CAN devices found!")
            return

        print("\nAvailable CAN devices:")
        for i, dev in enumerate(can_devs):
            status = dev.extra_info.get("status", "Unknown")
            app = dev.extra_info.get("app_name", "Unknown")
            print(f"  {i + 1}. UUID: {dev.path} - {app} ({status})")

        try:
            choice = input("\nSelect device number (or 'q' to quit): ").strip()
            if choice.lower() == 'q':
                return
            idx = int(choice) - 1
            if 0 <= idx < len(can_devs):
                selected = can_devs[idx]
                iface = selected.extra_info.get("interface", "can0")
                updates = {
                    "canbus_uuid": selected.path,
                    "canbus_interface": iface,
                }
                if self.config_parser.update_config(config_file, mcu.name, updates):
                    print(f"Updated {mcu.name}:")
                    print(f"  canbus_uuid = {selected.path}")
                    print(f"  canbus_interface = {iface}")
                else:
                    print("Failed to update config file")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("Cancelled.")

    def _fix_tcp(self, mcu: MCUConfig, config_file: str):
        """Interactive TCP host/port fix."""
        try:
            host = input("Enter TCP host IP: ").strip()
            if not host:
                return
            port = input(f"Enter TCP port [{mcu.tcp_port}]: ").strip()
            port = int(port) if port else mcu.tcp_port

            updates = {
                "tcp_host": host,
                "tcp_port": str(port),
            }
            # Remove serial/can settings if present
            for key in ["serial", "baud", "canbus_uuid", "canbus_interface"]:
                if self.config_parser.has_option(config_file, mcu.name, key):
                    updates[key] = ""

            if self.config_parser.update_config(config_file, mcu.name, updates):
                print(f"Updated {mcu.name}: tcp_host = {host}, tcp_port = {port}")
            else:
                print("Failed to update config file")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("Cancelled.")

    def _fix_udp(self, mcu: MCUConfig, config_file: str):
        """Interactive UDP host/port fix."""
        try:
            host = input("Enter UDP host IP: ").strip()
            if not host:
                return
            port = input(f"Enter UDP port [{mcu.udp_port}]: ").strip()
            port = int(port) if port else mcu.udp_port

            updates = {
                "udp_host": host,
                "udp_port": str(port),
            }
            if self.config_parser.update_config(config_file, mcu.name, updates):
                print(f"Updated {mcu.name}: udp_host = {host}, udp_port = {port}")
            else:
                print("Failed to update config file")
        except (ValueError, EOFError, KeyboardInterrupt):
            print("Cancelled.")


def main():
    parser = argparse.ArgumentParser(
        description="MCU Configuration Checker and Device Discovery Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Basic check
  %(prog)s --verbose                # Detailed output
  %(prog)s --network                # Scan local network for TCP/UDP devices
  %(prog)s --network 192.168.1.0/24 # Scan specific subnet
  %(prog)s --fix                    # Interactive configuration fix
  %(prog)s --config ~/my_printer.cfg # Specify config file
        """
    )
    parser.add_argument(
        "--config", "-c",
        help="Path to printer.cfg file"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--network", "-n",
        nargs="?",
        const="auto",
        default=None,
        help="Scan network for TCP/UDP devices (optionally specify subnet)"
    )
    parser.add_argument(
        "--fix", "-f",
        action="store_true",
        help="Interactive configuration fix wizard"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Create checker
    checker = MCUChecker(config_path=args.config, verbose=args.verbose)

    # Determine network scan parameters
    scan_network = args.network is not None
    network_subnet = None
    if args.network and args.network != "auto":
        network_subnet = args.network

    # Run checks
    print("=" * 60)
    print("MCU Configuration Checker")
    print("=" * 60)
    print()

    results = checker.check_all(scan_network=scan_network,
                                network_subnet=network_subnet)

    # Output JSON if requested
    if args.json:
        json_results = []
        for r in results:
            json_results.append({
                "mcu": r.mcu_config.display_name,
                "transport": r.mcu_config.transport,
                "matched": r.matched_device is not None,
                "responsive": r.is_responsive,
                "firmware": r.firmware_version,
                "issues": r.issues,
                "suggestions": r.suggestions,
            })
        print("\nJSON Output:")
        print(json.dumps(json_results, indent=2))

    # Run interactive fix if requested
    if args.fix:
        checker.interactive_fix(results)

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    ok_count = sum(1 for r in results if r.is_responsive)
    warn_count = sum(1 for r in results if r.matched_device and not r.is_responsive)
    error_count = sum(1 for r in results if not r.matched_device)

    print(f"  OK: {ok_count}")
    print(f"  WARNING: {warn_count}")
    print(f"  ERROR: {error_count}")

    if error_count > 0 or warn_count > 0:
        print("\nRun with --fix to interactively update printer.cfg")
        sys.exit(1)
    else:
        print("\nAll MCU configurations appear correct!")
        sys.exit(0)


if __name__ == "__main__":
    main()
