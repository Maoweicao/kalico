# Tests for the MCU side RS485 transport
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import pytest
from sim.modbus_slave import ModbusSlave
from sim.transport import FakeBitbangModbus

from klippy.extras.rs485.transport import McuRS485Transport, RS485TransportError

pytestmark = pytest.mark.proto


def _make_transport(slave=None):
    transport = object.__new__(McuRS485Transport)
    transport._config = None
    transport._bus_pin = {"pin": "PA1"}
    transport._mcu_modbus = FakeBitbangModbus(slave)
    transport._rx_buffer = b""
    transport._open = False
    return transport


######################################################################
# Response length inference
######################################################################


def test_expected_response_len_of_a_read_request():
    transport = _make_transport()
    frame = bytes([0x01, 0x03, 0x60, 0x41, 0x00, 0x02])
    assert transport._expected_response_len(frame) == 5 + 2 * 2


def test_expected_response_len_of_a_write_single_request():
    transport = _make_transport()
    frame = bytes([0x01, 0x06, 0x60, 0x40, 0x00, 0x0F])
    assert transport._expected_response_len(frame) == 8


def test_expected_response_len_of_a_write_multiple_request():
    transport = _make_transport()
    frame = bytes([0x01, 0x10, 0x60, 0x7A, 0x00, 0x02])
    assert transport._expected_response_len(frame) == 8


def test_expected_response_len_of_an_unknown_function():
    transport = _make_transport()
    frame = bytes([0x01, 0x42, 0x60, 0x41, 0x00, 0x02])
    assert transport._expected_response_len(frame) == 0


def test_expected_response_len_of_a_short_frame():
    transport = _make_transport()
    assert transport._expected_response_len(b"") == 0
    assert transport._expected_response_len(b"\x01") == 0


######################################################################
# Buffering
######################################################################


def test_open_and_close():
    transport = _make_transport()
    transport.open()
    assert transport._open is True
    transport.close()
    assert transport._open is False
    assert transport._rx_buffer == b""


def test_write_on_a_closed_transport_is_rejected():
    transport = _make_transport()
    with pytest.raises(RS485TransportError):
        transport.write(b"\x01\x03")


def test_write_buffers_the_response():
    slave = ModbusSlave(1, {0x6041: 0x0027})
    transport = _make_transport(slave)
    transport.open()
    transport.write(bytes([0x01, 0x03, 0x60, 0x41, 0x00, 0x01]))
    assert len(transport._rx_buffer) == 7


def test_read_splits_the_buffer():
    transport = _make_transport()
    transport.open()
    transport._rx_buffer = b"abcdefg"
    assert transport.read(3) == b"abc"
    assert transport.read(3) == b"def"
    assert transport.read(3) == b"g"
    assert transport.read(3) == b""


def test_read_returns_the_rest_when_less_is_available():
    transport = _make_transport()
    transport.open()
    transport._rx_buffer = b"ab"
    assert transport.read(5) == b"ab"
    assert transport._rx_buffer == b""


def test_read_until_keeps_the_remainder():
    transport = _make_transport()
    transport.open()
    transport._rx_buffer = b"ab\x00cd"
    assert transport.read_until(b"\x00") == b"ab\x00"
    assert transport._rx_buffer == b"cd"


def test_read_until_without_a_terminator():
    transport = _make_transport()
    transport.open()
    transport._rx_buffer = b"abcd"
    assert transport.read_until(b"") == b"abcd"
    assert transport._rx_buffer == b""


def test_flush_drops_the_buffer():
    transport = _make_transport()
    transport.open()
    transport._rx_buffer = b"abcd"
    transport.flush()
    assert transport._rx_buffer == b""


def test_get_baudrate():
    transport = _make_transport()
    assert transport.get_baudrate() == 38400
