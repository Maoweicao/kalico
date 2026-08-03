# Shared Modbus RTU frame helpers
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Pure Modbus RTU primitives shared by the host-side RS485 subsystem
# (modbus_rtu.py) and the MCU bit-bang transport (mcu_modbus.py and the
# LYX stepper driver host layer).

import struct

# Modbus function codes
FC_READ_HOLDING_REGISTERS = 0x03
FC_WRITE_SINGLE_REGISTER = 0x06
FC_WRITE_MULTIPLE_REGISTERS = 0x10

# Bit set in the function code of an exception response
EXCEPTION_MASK = 0x80

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


def calc_crc16(data):
    """Calculate the Modbus RTU CRC16 (polynomial 0xA001)."""
    crc = 0xFFFF
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 0x0001:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xFFFF


def check_crc(data):
    """Return True if the trailing CRC16 of a received frame is valid."""
    if len(data) < 2:
        return False
    return calc_crc16(data[:-2]) == int.from_bytes(data[-2:], "little")


def is_exception(func_code):
    """Return True if the response function code signals an exception."""
    return bool(func_code & EXCEPTION_MASK)


def exception_message(exception_code):
    """Return a human-readable message for a Modbus exception code."""
    return MODBUS_EXCEPTION_CODES.get(
        exception_code, "Unknown (0x%02X)" % exception_code
    )


def build_read_request(slave_id, start_addr, count):
    """Build an FC03 Read Holding Registers request."""
    request = struct.pack(
        ">B B H H", slave_id, FC_READ_HOLDING_REGISTERS, start_addr, count
    )
    return request + struct.pack("<H", calc_crc16(request))


def build_write_single_request(slave_id, register, value):
    """Build an FC06 Write Single Register request."""
    request = struct.pack(
        ">B B H H", slave_id, FC_WRITE_SINGLE_REGISTER, register, value & 0xFFFF
    )
    return request + struct.pack("<H", calc_crc16(request))


def build_write_multiple_request(slave_id, start_addr, values):
    """Build an FC16 Write Multiple Registers request."""
    count = len(values)
    request = struct.pack(
        ">B B H H B",
        slave_id,
        FC_WRITE_MULTIPLE_REGISTERS,
        start_addr,
        count,
        count * 2,
    )
    for val in values:
        request += struct.pack(">H", val & 0xFFFF)
    return request + struct.pack("<H", calc_crc16(request))


def decode_read_response(data, slave_id, count=1):
    """Validate and decode an FC03 response.

    Returns a list of register values, or None if the frame is invalid
    (wrong slave, exception, bad CRC or short frame).
    """
    expected = 5 + 2 * count
    if len(data) != expected:
        return None
    if data[0] != slave_id:
        return None
    if is_exception(data[1]):
        return None
    if data[2] != 2 * count:
        return None
    if not check_crc(data):
        return None
    values = []
    for i in range(count):
        values.append(int.from_bytes(data[3 + i * 2 : 5 + i * 2], "big"))
    return values
