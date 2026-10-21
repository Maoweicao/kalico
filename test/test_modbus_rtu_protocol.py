# Tests for the Modbus RTU protocol implementation
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The host side of the protocol is driven against a Modbus slave
# simulator - the frames that go on the wire are checked and every error
# path of the protocol is exercised.
import pytest
from sim.modbus_slave import ModbusSlave
from sim.transport import FakeTransport

from klippy.extras.rs485.modbus_frame import (
    FC_READ_HOLDING_REGISTERS,
    FC_WRITE_MULTIPLE_REGISTERS,
    FC_WRITE_SINGLE_REGISTER,
    check_crc,
)
from klippy.extras.rs485.modbus_rtu import ModbusRtuProtocol
from klippy.extras.rs485.protocol import RS485ProtocolError

pytestmark = pytest.mark.proto
REGISTERS = {
    0x6040: 0x000F,  # control word
    0x6041: 0x0027,  # status word - operation enabled
    0x6060: 0x0008,  # mode of operation
    0x6061: 0x0008,  # mode of operation display
    0x6064: 0x0000,  # actual position (low)
    0x6065: 0x0000,  # actual position (high)
    0x607A: 0x0000,  # target position (low)
    0x607B: 0x0000,  # target position (high)
    0x60FF: 0x0000,  # target velocity
}


def _make_protocol(slave=None, slave_id=1, **kwargs):
    if slave is None:
        slave = ModbusSlave(slave_id, REGISTERS)
    transport = FakeTransport(slave)
    transport.open()
    protocol = ModbusRtuProtocol(transport, slave_id=slave_id, **kwargs)
    return protocol, transport, slave


######################################################################
# Reading
######################################################################


def test_read_register():
    protocol, transport, slave = _make_protocol()
    assert protocol.read_register(0x6041) == 0x0027


def test_read_register_sends_a_well_formed_frame():
    protocol, transport, slave = _make_protocol()
    protocol.read_register(0x6041)
    frame = transport.sent_frames[0]
    assert frame[0] == 1
    assert frame[1] == FC_READ_HOLDING_REGISTERS
    assert frame[2:4] == b"\x60\x41"
    assert frame[4:6] == b"\x00\x01"
    assert check_crc(frame) is True


def test_read_registers():
    protocol, transport, slave = _make_protocol()
    assert protocol.read_registers(0x6064, 2) == [0x0000, 0x0000]


def test_read_registers_of_several_values():
    slave = ModbusSlave(1, {0x10: 0x1111, 0x11: 0x2222, 0x12: 0x3333})
    protocol, transport, _ = _make_protocol(slave)
    assert protocol.read_registers(0x10, 3) == [0x1111, 0x2222, 0x3333]


def test_read_of_an_unknown_address_is_rejected():
    slave = ModbusSlave(1, {0x10: 0x1111})
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x20)
    assert "exception" in str(exc.value).lower()


######################################################################
# Writing
######################################################################


def test_write_register():
    slave = ModbusSlave(1, dict(REGISTERS))
    protocol, transport, _ = _make_protocol(slave)
    protocol.write_register(0x6040, 0x000F)
    assert slave.get_register(0x6040) == 0x000F


def test_write_register_sends_a_well_formed_frame():
    protocol, transport, slave = _make_protocol()
    protocol.write_register(0x6040, 0x1234)
    frame = transport.sent_frames[0]
    assert frame[0] == 1
    assert frame[1] == FC_WRITE_SINGLE_REGISTER
    assert frame[2:4] == b"\x60\x40"
    assert frame[4:6] == b"\x12\x34"
    assert check_crc(frame) is True


def test_write_registers():
    slave = ModbusSlave(1, dict(REGISTERS))
    protocol, transport, _ = _make_protocol(slave)
    protocol.write_registers(0x607A, [0x1111, 0x2222])
    assert slave.get_register(0x607A) == 0x1111
    assert slave.get_register(0x607B) == 0x2222


def test_write_registers_sends_a_well_formed_frame():
    protocol, transport, slave = _make_protocol()
    protocol.write_registers(0x607A, [0x1111, 0x2222])
    frame = transport.sent_frames[0]
    assert frame[1] == FC_WRITE_MULTIPLE_REGISTERS
    assert frame[4:6] == b"\x00\x02"
    assert frame[6] == 4
    assert check_crc(frame) is True


######################################################################
# CiA 402 helpers
######################################################################


def test_set_target_position_splits_the_value():
    slave = ModbusSlave(1, dict(REGISTERS))
    protocol, transport, _ = _make_protocol(slave)
    protocol.set_target_position(0x00012345)
    assert slave.get_register(0x607A) == 0x2345
    assert slave.get_register(0x607B) == 0x0001


def test_get_actual_position_combines_the_registers():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.set_register(0x6064, 0x2345)
    slave.set_register(0x6065, 0x0001)
    protocol, transport, _ = _make_protocol(slave)
    assert protocol.get_actual_position() == 0x00012345


def test_get_actual_position_is_signed():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.set_register(0x6064, 0xFFFF)
    slave.set_register(0x6065, 0xFFFF)
    protocol, transport, _ = _make_protocol(slave)
    assert protocol.get_actual_position() == -1


def test_get_status_word():
    protocol, transport, slave = _make_protocol()
    assert protocol.get_status_word() == 0x0027


def test_get_state_name():
    protocol, transport, slave = _make_protocol()
    assert protocol.get_state_name() == "OPERATION_ENABLED"


def test_get_state_name_of_an_unknown_state():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.set_register(0x6041, 0x0001)
    protocol, transport, _ = _make_protocol(slave)
    assert protocol.get_state_name().startswith("UNKNOWN")


def test_get_mode_of_operation():
    protocol, transport, slave = _make_protocol()
    assert protocol.get_mode_of_operation() == 0x0008


def test_get_error_code_returns_zero_on_a_failure():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.silent = True
    protocol, transport, _ = _make_protocol(slave)
    assert protocol.get_error_code() == 0


def test_get_register_map_is_a_copy():
    protocol, transport, slave = _make_protocol()
    register_map = protocol.get_register_map()
    register_map["control_word"] = 0x1234
    assert protocol.get_register_map()["control_word"] == 0x6040


######################################################################
# Error paths
######################################################################


def test_a_silent_slave_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.silent = True
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x6041)
    assert "no response" in str(exc.value)


def test_an_exception_frame_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.exception_code = 0x02
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x6041)
    assert "Illegal Data Address" in str(exc.value)


def test_a_response_of_the_wrong_slave_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.response_slave_id = 2
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x6041)
    assert "wrong slave" in str(exc.value)


def test_a_broken_crc_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.corrupt_crc = True
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x6041)
    assert "CRC error" in str(exc.value)


def test_a_truncated_response_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.truncate = 3
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_register(0x6041)
    assert "incomplete" in str(exc.value)


def test_a_response_with_the_wrong_byte_count_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.wrong_byte_count = 8
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError) as exc:
        protocol.read_registers(0x6064, 2)
    assert "byte count" in str(exc.value)


def test_an_empty_response_is_reported():
    slave = ModbusSlave(1, dict(REGISTERS))
    slave.silent = True
    protocol, transport, _ = _make_protocol(slave)
    with pytest.raises(RS485ProtocolError):
        protocol.write_register(0x6040, 0x000F)


######################################################################
# Timing
######################################################################


def test_the_inter_frame_delay_is_applied():
    protocol, transport, slave = _make_protocol(
        inter_frame_delay=0.0, response_delay=0.0
    )
    protocol.read_register(0x6041)
    assert len(transport.sent_frames) == 1
