# MCU bit-bang Modbus RTU host layer
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# Generic host wrapper for the firmware software bit-bang Modbus UART
# (src/modbus_uart.c). Used by both the LYX stepper driver host layer
# (lyx_uart.py) and the MCU-side RS485 transport (McuRS485Transport).
#
# The bus is a half-duplex single-wire 8N1 UART: tx and rx share one GPIO
# pin. All users of a given pin share a single MCUBitbangModbus instance
# and a per-MCU reactor mutex so frames never collide on the wire.


class PrinterModbusUartMutexes:
    """Store per-MCU mutex objects to prevent concurrent bus access."""

    def __init__(self):
        self.mcu_to_mutex = {}


def lookup_modbus_uart_mutex(mcu):
    """Retrieve or create the reactor mutex guarding an MCU's Modbus bus."""
    printer = mcu.get_printer()
    pmutexes = printer.lookup_object("mcu_modbus_uart", None)
    if pmutexes is None:
        pmutexes = PrinterModbusUartMutexes()
        printer.add_object("mcu_modbus_uart", pmutexes)
    mutex = pmutexes.mcu_to_mutex.get(mcu)
    if mutex is None:
        mutex = printer.get_reactor().mutex()
        pmutexes.mcu_to_mutex[mcu] = mutex
    return mutex


class MCUBitbangModbus:
    """Bind to the MCU modbus_uart commands and manage pin sharing.

    Args:
        rx_pin_params: pin params dict from pins.lookup_pin()
        tx_pin_params: pin params dict (same as rx_pin_params in
            single-wire mode)
        baud: UART baud rate (default 38400)
    """

    # Firmware receive buffer limit (src/modbus_uart.c)
    MAX_RESPONSE_BYTES = 16

    def __init__(self, rx_pin_params, tx_pin_params, baud=38400):
        self.mcu = rx_pin_params["chip"]
        self.mutex = lookup_modbus_uart_mutex(self.mcu)
        self.rx_pin = rx_pin_params["pin"]
        self.tx_pin = tx_pin_params["pin"]
        self.baud = baud
        self.oid = self.mcu.create_oid()
        self.cmd_queue = self.mcu.alloc_command_queue()
        self.instances = {}
        self.send_cmd = None
        self.mcu.register_config_callback(self.build_config)

    def build_config(self):
        """Generate the MCU config_modbus_uart command on startup."""
        reactor = self.mcu.get_printer().get_reactor()
        systime = reactor.monotonic()
        get_clock = self.mcu._clocksync.get_clock
        calc_freq = get_clock(systime + 1) - get_clock(systime)

        # Derive the bit time from the measured MCU clock instead of the
        # frequency reported by the MCU, which may be wrong on some boards.
        bit_ticks = int(1.0 / self.baud * calc_freq)
        self.mcu.add_config_cmd(
            "config_modbus_uart oid=%d rx_pin=%s pull_up=%d tx_pin=%s bit_time=%d"
            % (self.oid, self.rx_pin, 1, self.tx_pin, bit_ticks)
        )
        self.send_cmd = self.mcu.lookup_query_command(
            "modbus_uart_send oid=%c write=%*s read=%c",
            "modbus_uart_response oid=%c read=%*s",
            oid=self.oid,
            cq=self.cmd_queue,
            is_async=True,
        )

    def register_slave(self, rx_pin_params, tx_pin_params, addr):
        """Validate and register a slave address on this bus."""
        if (
            rx_pin_params["pin"] != self.rx_pin
            or tx_pin_params["pin"] != self.tx_pin
        ):
            raise self.mcu.get_printer().config_error(
                "Shared Modbus bit-bang uarts must use identical pins"
            )
        if addr in self.instances:
            raise self.mcu.get_printer().config_error(
                "Modbus slave address %d already in use on this bus" % addr
            )
        self.instances[addr] = True
        return addr

    def send_frame(self, data, read_len=0, minclock=0):
        """Transmit a frame and (optionally) read read_len response bytes.

        Caller must hold self.mutex when the bus is shared. Returns the
        raw response bytes, or b'' if no response was captured.
        """
        if read_len > self.MAX_RESPONSE_BYTES:
            raise self.mcu.get_printer().command_error(
                "modbus read length %d exceeds firmware limit of %d"
                % (read_len, self.MAX_RESPONSE_BYTES)
            )
        params = self.send_cmd.send(
            [self.oid, bytes(data), read_len], minclock=minclock
        )
        raw = params["read"]
        if read_len and raw and raw.count(0xFF) == len(raw):
            # Line stayed idle (slave never responded).
            return b""
        return raw

    def get_mcu(self):
        """Return the bound MCU instance."""
        return self.mcu


def lookup_mcu_bitbang(config):
    """Look up (or create) the shared bit-bang Modbus bus for uart_pin.

    Args:
        config: a config section providing uart_pin and optional baud_rate

    Returns:
        (bus_pin_params, MCUBitbangModbus)
    """
    ppins = config.get_printer().lookup_object("pins")
    bus_pin = ppins.lookup_pin(config.get("uart_pin"), share_type="mcu_modbus")
    baud = config.getfloat("baud_rate", 38400, minval=300, maxval=115200)
    mcu_modbus = bus_pin.get("class")
    if mcu_modbus is None:
        mcu_modbus = MCUBitbangModbus(bus_pin, bus_pin, baud)
        bus_pin["class"] = mcu_modbus
    return bus_pin, mcu_modbus
