# Bit-bang Modbus RTU host layer for LYX9231
# Raw Modbus frame transport over the MCU software 8N1 UART
# License: GNU GPLv3
#
# The low-level bit-bang bus handling and Modbus frame code are shared
# with the RS485 subsystem (rs485/mcu_modbus.py, rs485/modbus_frame.py),
# so LYX drivers and rs485_stepper drives may share the same bus.

import logging
import time

from .rs485.mcu_modbus import lookup_mcu_bitbang
from .rs485.modbus_frame import (
    build_read_request,
    build_write_single_request,
    decode_read_response,
)


######################################################################
# Low-level Modbus register helpers over the shared bit-bang bus
######################################################################
def _reg_read(mcu_uart, slave_addr, reg_addr):
    """Send a Modbus 0x03 read request and validate the response."""
    msg = build_read_request(slave_addr, reg_addr, 1)
    raw = mcu_uart.send_frame(msg, read_len=7)
    values = decode_read_response(raw, slave_addr, 1)
    if values is None:
        logging.debug(
            "LYX modbus read reg=0x%02X failed: %s",
            reg_addr,
            raw.hex() if raw else "no response",
        )
        return None
    return values[0]


def _reg_write(mcu_uart, slave_addr, reg_addr, value, minclock=0):
    """Send a Modbus 0x06 write request, returning the echo response."""
    msg = build_write_single_request(slave_addr, reg_addr, value)
    return mcu_uart.send_frame(msg, read_len=8, minclock=minclock)


######################################################################
# High-level register read/write API exposed to the driver
######################################################################
class MCU_LYX_uart:
    """Upper layer register access wrapper for the LYX9231 driver"""

    def __init__(self, config, name_to_reg, fields):
        self.printer = config.get_printer()
        self.name = config.get_name().split()[-1]
        self.name_to_reg = name_to_reg
        self.fields = fields
        self.addr = config.getint("uart_address", 1, minval=1, maxval=247)
        self.bus_pin, self.mcu_uart = lookup_mcu_bitbang(config)
        self.mcu_uart.register_slave(self.bus_pin, self.bus_pin, self.addr)
        self.mutex = self.mcu_uart.mutex

    def get_fields(self):
        """Return the field helper instance for the current driver"""
        return self.fields

    def _do_get_register(self, reg_name):
        """Retry read logic with a limited iteration count"""
        reg = self.name_to_reg[reg_name]
        if self.printer.get_start_args().get("debugoutput") is not None:
            return {"data": 0, "#receive_time": 0.0}
        for retry in range(1000):
            logging.debug("R %s retry %d", reg_name, retry)
            value = _reg_read(self.mcu_uart, self.addr, reg)
            if value is not None:
                return {"data": value, "#receive_time": 0.0}
            # Small delay to avoid bus overload during retries
            time.sleep(0.001)
        raise self.printer.command_error(
            "Unable to read lyx uart '%s' register %s" % (self.name, reg_name)
        )

    def get_register_raw(self, reg_name):
        """Thread-safe register read entry with mutex lock"""
        with self.mutex:
            return self._do_get_register(reg_name)

    def get_register(self, reg_name):
        """Simplified read interface returning a raw integer value"""
        return self.get_register_raw(reg_name)["data"]

    def set_register(self, reg_name, val, print_time=None):
        """Write register + readback validation with limited retries"""
        reg = self.name_to_reg[reg_name]
        val = int(val) & 0xFFFF
        if self.printer.get_start_args().get("debugoutput") is not None:
            return
        minclock = 0
        if print_time is not None:
            minclock = self.mcu_uart.mcu.print_time_to_clock(print_time)
        with self.mutex:
            for write_retry in range(100):
                # Transmit the write frame and verify the echoed response
                echo = _reg_write(self.mcu_uart, self.addr, reg, val, minclock)
                if (
                    echo
                    and echo[0] == self.addr
                    and echo[1] == 0x06
                    and len(echo) >= 8
                ):
                    return
                # Delay for the chip register refresh cycle
                time.sleep(0.005)
                # Limited readback retry to verify the write was applied
                for retry in range(100):
                    logging.debug(
                        "W %s val=%d write_retry=%d retry=%d",
                        reg_name,
                        val,
                        write_retry,
                        retry,
                    )
                    readback = _reg_read(self.mcu_uart, self.addr, reg)
                    if readback == val:
                        return
                    time.sleep(0.001)

            self.printer.invoke_shutdown(
                "Unable to write lyx uart '%s' register %s due to "
                "transmission delay, try to reboot Klipper Service to retry"
                % (self.name, reg_name)
            )

    def get_mcu(self):
        """Return the bound MCU reference"""
        return self.mcu_uart.get_mcu()
