# Tests for the LYX9231 Modbus RTU host layer
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from sim.modbus_slave import ModbusSlave
from sim.transport import FakeBitbangModbus

from klippy.extras.lyx9231 import Fields, ReadRegisters, Registers, SignedFields
from klippy.extras.lyx_uart import MCU_LYX_uart, _reg_read, _reg_write


def _make_slave():
    return ModbusSlave(1, {addr: 0 for addr in Registers.values()})


class _FakePrinter:
    def get_start_args(self):
        return {}


def _make_uart(slave=None):
    uart = object.__new__(MCU_LYX_uart)
    uart.printer = _FakePrinter()
    uart.name = "my_lyx"
    uart.name_to_reg = Registers
    uart.fields = None
    uart.addr = 1
    uart.bus_pin = {"pin": "PA1"}
    uart.mcu_uart = FakeBitbangModbus(
        slave if slave is not None else _make_slave()
    )
    uart.mutex = uart.mcu_uart.mutex
    return uart


######################################################################
# Register map
######################################################################


def test_the_register_addresses_are_unique():
    assert len(set(Registers.values())) == len(Registers)


def test_the_register_addresses_fit_in_a_byte():
    for name, address in Registers.items():
        assert 0 <= address <= 0xFF, name


def test_every_register_has_a_field():
    for name in Registers:
        assert name in Fields
        assert Fields[name][name.lower()] == 0xFFFF


def test_the_signed_fields_exist():
    for name in SignedFields:
        assert name in [reg.lower() for reg in Registers]


def test_the_readback_registers_exist():
    for name in ReadRegisters:
        assert name in Registers


######################################################################
# Low level register access
######################################################################


def test_reg_read_returns_the_value():
    slave = _make_slave()
    slave.set_register(0x08, 0x1234)
    uart = _make_uart(slave)
    assert _reg_read(uart.mcu_uart, 1, 0x08) == 0x1234


def test_reg_read_sends_a_read_request():
    slave = _make_slave()
    uart = _make_uart(slave)
    _reg_read(uart.mcu_uart, 1, 0x08)
    frame = uart.mcu_uart.sent_frames[0]
    assert frame[0] == 1
    assert frame[1] == 0x03
    assert frame[2:4] == b"\x00\x08"


def test_reg_read_of_a_missing_register_returns_none():
    slave = ModbusSlave(1, {})
    uart = _make_uart(slave)
    assert _reg_read(uart.mcu_uart, 1, 0x08) is None


def test_reg_read_of_a_silent_slave_returns_none():
    slave = _make_slave()
    slave.silent = True
    uart = _make_uart(slave)
    assert _reg_read(uart.mcu_uart, 1, 0x08) is None


def test_reg_write_returns_the_echo():
    slave = _make_slave()
    uart = _make_uart(slave)
    echo = _reg_write(uart.mcu_uart, 1, 0x08, 0x1234)
    assert echo[0] == 1
    assert echo[1] == 0x06
    assert len(echo) == 8


def test_reg_write_updates_the_register():
    slave = _make_slave()
    uart = _make_uart(slave)
    _reg_write(uart.mcu_uart, 1, 0x08, 0x1234)
    assert slave.get_register(0x08) == 0x1234


######################################################################
# The driver layer
######################################################################


def test_get_register():
    slave = _make_slave()
    slave.set_register(0x08, 0x0005)
    uart = _make_uart(slave)
    assert uart.get_register("ALARM_CODE") == 0x0005


def test_set_register_writes_the_value():
    slave = _make_slave()
    uart = _make_uart(slave)
    uart.set_register("ALARM_CODE", 0x0003)
    assert slave.get_register(0x08) == 0x0003


def test_set_register_masks_the_value():
    slave = _make_slave()
    uart = _make_uart(slave)
    uart.set_register("ALARM_CODE", 0x1FFFF)
    assert slave.get_register(0x08) == 0xFFFF


def test_set_register_retries_until_the_echo_is_valid():
    # The first write is answered with a broken frame - the driver has to
    # fall back to a readback
    slave = _make_slave()
    uart = _make_uart(slave)
    original_handle = slave.handle
    state = {"calls": 0}

    def flaky_handle(request):
        state["calls"] += 1
        if state["calls"] == 1:
            return b""
        return original_handle(request)

    slave.handle = flaky_handle
    uart.set_register("ALARM_CODE", 0x0007)
    assert slave.get_register(0x08) == 0x0007


def test_set_register_in_debug_output_does_nothing():
    class _DebugPrinter:
        def get_start_args(self):
            return {"debugoutput": "/tmp/out"}

    slave = _make_slave()
    uart = _make_uart(slave)
    uart.printer = _DebugPrinter()
    uart.set_register("ALARM_CODE", 0x0007)
    assert slave.get_register(0x08) == 0x0000
