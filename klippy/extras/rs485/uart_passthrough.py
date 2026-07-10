# Generic UART passthrough protocol for RS485
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import struct

from .protocol import RS485Protocol, RS485ProtocolError


class UartPassthroughProtocol(RS485Protocol):
    """Generic UART passthrough protocol.

    Sends and receives raw bytes without protocol-specific framing.
    Users provide optional callback functions for encoding, decoding,
    and CRC calculation.

    If no callbacks are provided, data is sent/received as-is.

    Args:
        transport: RS485Transport instance
        slave_id: Slave ID (used by callbacks if needed)
        encode_func: function(slave_id, register, value) -> bytes
            Called to encode a register write into bytes.
        decode_func: function(slave_id, data) -> int
            Called to decode received bytes into a register value.
        crc_func: function(data) -> bytes
            Called to calculate CRC bytes for outgoing data.
        read_request_func: function(slave_id, register) -> bytes
            Called to build a register read request.
        write_request_func: function(slave_id, register, value) -> bytes
            Called to build a register write request.
        response_length: Expected response length in bytes (0 for auto)
        inter_byte_delay: Delay between bytes in seconds (0 for none)
    """

    def __init__(self, transport, slave_id=1, encode_func=None,
                 decode_func=None, crc_func=None,
                 read_request_func=None, write_request_func=None,
                 response_length=0, inter_byte_delay=0):
        super().__init__(transport, slave_id)
        self._encode_func = encode_func
        self._decode_func = decode_func
        self._crc_func = crc_func
        self._read_request_func = read_request_func
        self._write_request_func = write_request_func
        self._response_length = response_length
        self._inter_byte_delay = inter_byte_delay
        self._lock = __import__('threading').Lock()

    def _build_request(self, register, value=None):
        """Build a request frame using callbacks."""
        if value is not None and self._write_request_func:
            data = self._write_request_func(self._slave_id, register, value)
        elif value is None and self._read_request_func:
            data = self._read_request_func(self._slave_id, register)
        else:
            # Default: raw 4-byte frame [slave_id] [register(2)] [value(1)]
            if value is not None:
                data = struct.pack(">B H B", self._slave_id, register, value)
            else:
                data = struct.pack(">B H", self._slave_id, register)

        if self._crc_func:
            crc = self._crc_func(data)
            data = data + crc
        return data

    def _send_and_receive(self, request, expected_len=None):
        """Send request and receive response."""
        with self._lock:
            self._transport.write(request)

            if self._inter_byte_delay > 0:
                import time
                time.sleep(self._inter_byte_delay)

            if expected_len is None:
                expected_len = self._response_length
            if expected_len <= 0:
                expected_len = 64  # Read whatever is available

            response = self._transport.read(expected_len, timeout=1.0)
            return response

    def read_register(self, register):
        """Read a register using the configured callbacks."""
        request = self._build_request(register)
        response = self._send_and_receive(request)

        if not response:
            raise RS485ProtocolError(
                "UART passthrough: no response from slave %d"
                % self._slave_id
            )

        if self._decode_func:
            return self._decode_func(self._slave_id, response)

        # Default: interpret response as [slave_id] [register(2)] [value(2)]
        if len(response) >= 5:
            return struct.unpack(">H", response[3:5])[0]
        elif len(response) >= 2:
            return struct.unpack(">H", response[-2:])[0]
        return response[-1] if response else 0

    def write_register(self, register, value):
        """Write a register using the configured callbacks."""
        request = self._build_request(register, value)
        response = self._send_and_receive(request)

        if self._encode_func:
            return  # Custom encode function handles everything

        # Default: just send, don't wait for response
        if not response:
            logging.debug(
                "UART passthrough: no response to write (may be normal)"
            )

    def set_target_position(self, position):
        """Set target position. Override for custom protocols."""
        pos_u = position & 0xFFFFFFFF
        lo = pos_u & 0xFFFF
        hi = (pos_u >> 16) & 0xFFFF
        self.write_register(0x0010, lo)
        self.write_register(0x0011, hi)

    def get_actual_position(self):
        """Get actual position. Override for custom protocols."""
        lo = self.read_register(0x0012)
        hi = self.read_register(0x0013)
        pos = (hi << 16) | lo
        if pos >= 0x80000000:
            pos -= 0x100000000
        return pos

    def set_control_word(self, value):
        self.write_register(0x0000, value & 0xFFFF)

    def get_status_word(self):
        return self.read_register(0x0001)

    def get_error_code(self):
        try:
            return self.read_register(0x0002)
        except Exception:
            return 0
