# Modbus RTU protocol implementation for RS485 servo drives
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import struct
import time

from .protocol import RS485Protocol, RS485ProtocolError


# Modbus function codes
FC_READ_HOLDING_REGISTERS = 0x03
FC_WRITE_SINGLE_REGISTER = 0x06
FC_WRITE_MULTIPLE_REGISTERS = 0x10

# Modbus exception codes
MODBUS_EXCEPTION_CODES = {
    0x01: "Illegal Function",
    0x02: "Illegal Data Address",
    0x03: "Illegal Data Value",
    0x04: "Slave Device Failure",
    0x05: "Acknowledge",
    0x06: "Slave Device Busy",
    0x08: "Memory Parity Error",
    0x0A: "Gateway Path Unavailable",
    0x0B: "Gateway Target Device Failed to Respond",
}

# Default CiA 402-compatible register mapping
# Many industrial servo drives use these register addresses
DEFAULT_REGISTER_MAP = {
    "control_word": 0x6040,
    "status_word": 0x6041,
    "mode_of_operation": 0x6060,
    "mode_of_operation_display": 0x6061,
    "target_position": 0x607A,
    "actual_position": 0x6064,
    "target_velocity": 0x60FF,
    "actual_velocity": 0x606C,
    "error_code": 0x603F,
}


def _calc_crc16(data):
    """Calculate Modbus CRC16."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc


class ModbusRtuProtocol(RS485Protocol):
    """Modbus RTU protocol implementation.

    Supports:
    - FC03: Read Holding Registers
    - FC06: Write Single Register
    - FC16: Write Multiple Registers

    The register map can be customized for drives that don't use
    standard CiA 402 addresses. Pass a custom register_map dict with
    keys: control_word, status_word, mode_of_operation, target_position,
    actual_position, error_code.

    Args:
        transport: RS485Transport instance
        slave_id: Modbus slave address (1-247)
        register_map: Custom register address mapping (optional)
        response_delay: Delay after write before reading response (seconds)
        inter_frame_delay: Minimum delay between frames (3.5 char times)
    """

    def __init__(self, transport, slave_id=1, register_map=None,
                 response_delay=None, inter_frame_delay=None):
        super().__init__(transport, slave_id)
        self._register_map = register_map or dict(DEFAULT_REGISTER_MAP)
        self._response_delay = response_delay
        self._inter_frame_delay = inter_frame_delay
        self._last_frame_time = 0
        self._lock = __import__('threading').Lock()

    def _ensure_frame_delay(self):
        """Ensure minimum inter-frame delay (3.5 character times)."""
        if self._inter_frame_delay is not None:
            delay = self._inter_frame_delay
        else:
            # 3.5 character times: 11 bits/char * 3.5 / baudrate
            baud = getattr(self._transport, 'get_baudrate', lambda: 9600)()
            delay = 11.0 * 3.5 / baud
        elapsed = time.monotonic() - self._last_frame_time
        if elapsed < delay:
            time.sleep(delay - elapsed)

    def _send_request(self, request):
        """Send a Modbus request and receive response."""
        with self._lock:
            self._ensure_frame_delay()
            self._transport.write(request)
            self._last_frame_time = time.monotonic()

            # Wait for response
            if self._response_delay is not None:
                time.sleep(self._response_delay)
            else:
                baud = getattr(self._transport, 'get_baudrate', lambda: 9600)()
                time.sleep(11.0 / baud)  # ~1 character time

            # Read response header (slave_id + function_code + ...)
            header = self._transport.read(3, timeout=1.0)
            if len(header) < 3:
                raise RS485ProtocolError(
                    "Modbus RTU: no response from slave %d" % self._slave_id
                )

            slave_id = header[0]
            func_code = header[1]

            if slave_id != self._slave_id:
                raise RS485ProtocolError(
                    "Modbus RTU: response from wrong slave %d (expected %d)"
                    % (slave_id, self._slave_id)
                )

            # Check for exception response
            if func_code & 0x80:
                exception_code = header[2]
                exc_msg = MODBUS_EXCEPTION_CODES.get(
                    exception_code, "Unknown (0x%02X)" % exception_code
                )
                raise RS485ProtocolError(
                    "Modbus RTU exception: FC=0x%02X, %s"
                    % (func_code & 0x7F, exc_msg)
                )

            return header, func_code

    def _build_read_request(self, start_addr, count):
        """Build FC03 Read Holding Registers request."""
        request = struct.pack(">B B H H",
                              self._slave_id,
                              FC_READ_HOLDING_REGISTERS,
                              start_addr,
                              count)
        crc = _calc_crc16(request)
        request += struct.pack("<H", crc)
        return request

    def _build_write_single_request(self, register, value):
        """Build FC06 Write Single Register request."""
        request = struct.pack(">B B H H",
                              self._slave_id,
                              FC_WRITE_SINGLE_REGISTER,
                              register,
                              value & 0xFFFF)
        crc = _calc_crc16(request)
        request += struct.pack("<H", crc)
        return request

    def _build_write_multiple_request(self, start_addr, values):
        """Build FC16 Write Multiple Registers request."""
        count = len(values)
        byte_count = count * 2
        request = struct.pack(">B B H H B",
                              self._slave_id,
                              FC_WRITE_MULTIPLE_REGISTERS,
                              start_addr,
                              count,
                              byte_count)
        for val in values:
            request += struct.pack(">H", val & 0xFFFF)
        crc = _calc_crc16(request)
        request += struct.pack("<H", crc)
        return request

    def read_register(self, register):
        """Read a single holding register (FC03)."""
        request = self._build_read_request(register, 1)
        header, func_code = self._send_request(request)

        # Response: [slave_id] [FC=03] [byte_count] [data...] [CRC16]
        byte_count = header[2]
        data = self._transport.read(byte_count + 2, timeout=1.0)
        if len(data) < byte_count + 2:
            raise RS485ProtocolError("Modbus RTU: incomplete response")

        # Verify CRC
        full_response = header + data[:-2]
        expected_crc = _calc_crc16(full_response)
        actual_crc = struct.unpack("<H", data[-2:])[0]
        if expected_crc != actual_crc:
            raise RS485ProtocolError("Modbus RTU: CRC error")

        value = struct.unpack(">H", data[:2])[0]
        return value

    def read_registers(self, start, count):
        """Read multiple holding registers (FC03)."""
        request = self._build_read_request(start, count)
        header, func_code = self._send_request(request)

        byte_count = header[2]
        expected_bytes = count * 2
        if byte_count != expected_bytes:
            raise RS485ProtocolError(
                "Modbus RTU: unexpected byte count %d (expected %d)"
                % (byte_count, expected_bytes)
            )

        data = self._transport.read(byte_count + 2, timeout=1.0)
        if len(data) < byte_count + 2:
            raise RS485ProtocolError("Modbus RTU: incomplete response")

        full_response = header + data[:-2]
        expected_crc = _calc_crc16(full_response)
        actual_crc = struct.unpack("<H", data[-2:])[0]
        if expected_crc != actual_crc:
            raise RS485ProtocolError("Modbus RTU: CRC error")

        values = []
        for i in range(count):
            val = struct.unpack(">H", data[i * 2:i * 2 + 2])[0]
            values.append(val)
        return values

    def write_register(self, register, value):
        """Write a single holding register (FC06)."""
        request = self._build_write_single_request(register, value)
        header, func_code = self._send_request(request)

        # Response echoes the request: [slave_id] [FC=06] [addr(2)] [val(2)] [CRC(2)]
        data = self._transport.read(4 + 2, timeout=1.0)
        if len(data) < 6:
            raise RS485ProtocolError("Modbus RTU: incomplete write response")

        full_response = header + data[:-2]
        expected_crc = _calc_crc16(full_response)
        actual_crc = struct.unpack("<H", data[-2:])[0]
        if expected_crc != actual_crc:
            raise RS485ProtocolError("Modbus RTU: CRC error on write")

    def write_registers(self, start, values):
        """Write multiple holding registers (FC16)."""
        request = self._build_write_multiple_request(start, values)
        header, func_code = self._send_request(request)

        # Response: [slave_id] [FC=10] [start_addr(2)] [count(2)] [CRC(2)]
        data = self._transport.read(4 + 2, timeout=1.0)
        if len(data) < 6:
            raise RS485ProtocolError(
                "Modbus RTU: incomplete write-multiple response"
            )

        full_response = header + data[:-2]
        expected_crc = _calc_crc16(full_response)
        actual_crc = struct.unpack("<H", data[-2:])[0]
        if expected_crc != actual_crc:
            raise RS485ProtocolError("Modbus RTU: CRC error on write-multiple")

    # Servo control interface using CiA 402 register mapping
    def set_target_position(self, position):
        """Set target position via Modbus registers."""
        reg = self._register_map.get("target_position", 0x607A)
        # Write as 32-bit value (two 16-bit registers)
        pos_u = position & 0xFFFFFFFF
        lo = pos_u & 0xFFFF
        hi = (pos_u >> 16) & 0xFFFF
        self.write_registers(reg, [lo, hi])

    def get_actual_position(self):
        """Get actual position via Modbus registers."""
        reg = self._register_map.get("actual_position", 0x6064)
        values = self.read_registers(reg, 2)
        pos = (values[1] << 16) | values[0]
        if pos >= 0x80000000:
            pos -= 0x100000000
        return pos

    def set_control_word(self, value):
        """Set control word via Modbus."""
        reg = self._register_map.get("control_word", 0x6040)
        self.write_register(reg, value & 0xFFFF)

    def get_status_word(self):
        """Get status word via Modbus."""
        reg = self._register_map.get("status_word", 0x6041)
        return self.read_register(reg)

    def set_mode_of_operation(self, mode):
        """Set operating mode via Modbus."""
        reg = self._register_map.get("mode_of_operation", 0x6060)
        self.write_register(reg, mode & 0xFFFF)

    def get_mode_of_operation(self):
        """Get current operating mode via Modbus."""
        reg = self._register_map.get("mode_of_operation_display",
                                     0x6061)
        return self.read_register(reg)

    def get_error_code(self):
        """Get error code via Modbus."""
        reg = self._register_map.get("error_code", 0x603F)
        try:
            return self.read_register(reg)
        except Exception:
            return 0

    def get_state_name(self):
        """Get state name from status word."""
        try:
            sw = self.get_status_word()
            state = sw & 0x006F
            state_names = {
                0x00: "NOT_READY",
                0x40: "SWITCH_ON_DISABLED",
                0x21: "READY_TO_SWITCH_ON",
                0x23: "SWITCHED_ON",
                0x27: "OPERATION_ENABLED",
                0x07: "QUICK_STOP",
                0x0F: "FAULT_REACTION",
                0x08: "FAULT",
            }
            return state_names.get(state, "UNKNOWN(0x%02X)" % state)
        except Exception:
            return "unknown"

    def get_register_map(self):
        return dict(self._register_map)
