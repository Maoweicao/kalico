# A scriptable Modbus RTU slave simulator
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The simulator answers FC03/FC06/FC10 requests from a register bank.  It
# can also be told to misbehave - that is what makes the error paths of
# the host side (timeouts, exception frames, a broken CRC, a response of
# the wrong slave) testable without any hardware.
import struct

from klippy.extras.rs485.modbus_frame import calc_crc16

FC_READ_HOLDING_REGISTERS = 0x03
FC_WRITE_SINGLE_REGISTER = 0x06
FC_WRITE_MULTIPLE_REGISTERS = 0x10

EXC_ILLEGAL_FUNCTION = 0x01
EXC_ILLEGAL_DATA_ADDRESS = 0x02
EXC_ILLEGAL_DATA_VALUE = 0x03
EXC_SLAVE_DEVICE_FAILURE = 0x04


def _with_crc(body):
    return body + struct.pack("<H", calc_crc16(body))


class ModbusSlave:
    """A Modbus RTU slave that can be driven into every failure mode.

    Args:
        slave_id: the address of the slave
        registers: initial register bank (address -> value)
    """

    def __init__(self, slave_id=1, registers=None):
        self.slave_id = slave_id
        self.registers = dict(registers or {})
        # Log of the frames that the slave received
        self.requests = []
        # Fault injection
        self.exception_code = None
        self.corrupt_crc = False
        self.response_slave_id = None
        self.silent = False
        self.truncate = 0
        self.extra_bytes = 0
        self.wrong_byte_count = None
        self.delay = 0.0

    # -- helpers ---------------------------------------------------------

    def set_register(self, address, value):
        self.registers[address] = value & 0xFFFF

    def get_register(self, address):
        return self.registers.get(address, 0)

    def _exception(self, func_code, code):
        return _with_crc(bytes([self.slave_id, func_code | 0x80, code & 0xFF]))

    # -- request handling ------------------------------------------------

    def handle(self, request):
        """Process a request frame and return the response bytes."""
        request = bytes(request)
        self.requests.append(request)
        if self.silent:
            return b""
        if len(request) < 4:
            return b""
        func_code = request[1]
        try:
            response = self._dispatch(func_code, request)
        except _IllegalAddress:
            response = self._exception(func_code, EXC_ILLEGAL_DATA_ADDRESS)
        except _SlaveFailure:
            response = self._exception(func_code, EXC_SLAVE_DEVICE_FAILURE)
        if response is None:
            response = self._exception(func_code, EXC_ILLEGAL_FUNCTION)
        return self._apply_faults(response)

    def _dispatch(self, func_code, request):
        if func_code == FC_READ_HOLDING_REGISTERS:
            return self._read_holding_registers(request)
        if func_code == FC_WRITE_SINGLE_REGISTER:
            return self._write_single_register(request)
        if func_code == FC_WRITE_MULTIPLE_REGISTERS:
            return self._write_multiple_registers(request)
        return None

    def _read_holding_registers(self, request):
        start_addr, count = struct.unpack(">HH", request[2:6])
        values = []
        for i in range(count):
            address = start_addr + i
            if address not in self.registers:
                raise _IllegalAddress()
            values.append(self.registers[address])
        body = bytearray([self.slave_id, FC_READ_HOLDING_REGISTERS])
        body.append(count * 2)
        for value in values:
            body += struct.pack(">H", value)
        return _with_crc(bytes(body))

    def _write_single_register(self, request):
        address, value = struct.unpack(">HH", request[2:6])
        if address not in self.registers:
            raise _IllegalAddress()
        self.registers[address] = value
        body = bytes([self.slave_id, FC_WRITE_SINGLE_REGISTER]) + request[2:6]
        return _with_crc(body)

    def _write_multiple_registers(self, request):
        start_addr, count = struct.unpack(">HH", request[2:6])
        byte_count = request[6]
        if byte_count != count * 2:
            raise _SlaveFailure()
        values = []
        for i in range(count):
            values.append(
                struct.unpack(">H", request[7 + i * 2 : 9 + i * 2])[0]
            )
        for i, value in enumerate(values):
            address = start_addr + i
            if address not in self.registers:
                raise _IllegalAddress()
            self.registers[address] = value
        body = bytes([self.slave_id, FC_WRITE_MULTIPLE_REGISTERS])
        body += struct.pack(">HH", start_addr, count)
        return _with_crc(body)

    # -- fault injection --------------------------------------------------

    def _apply_faults(self, response):
        if not response:
            return response
        if self.exception_code is not None:
            response = _with_crc(
                bytes(
                    [
                        self.slave_id,
                        (response[1] & 0x7F) | 0x80,
                        self.exception_code & 0xFF,
                    ]
                )
            )
        if self.response_slave_id is not None:
            response = bytes([self.response_slave_id]) + response[1:]
        if self.wrong_byte_count is not None and len(response) > 2:
            response = (
                response[:2] + bytes([self.wrong_byte_count]) + response[3:]
            )
        if self.corrupt_crc and len(response) >= 2:
            response = response[:-1] + bytes([response[-1] ^ 0xFF])
        if self.truncate:
            response = response[: len(response) - self.truncate]
        if self.extra_bytes:
            response = response + bytes(self.extra_bytes)
        return response


class _IllegalAddress(Exception):
    pass


class _SlaveFailure(Exception):
    pass
