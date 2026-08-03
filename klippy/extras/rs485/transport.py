# RS485 transport layer abstraction
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import threading
import time


class RS485TransportError(Exception):
    pass


class RS485Transport:
    """Abstract base class for RS485 transport."""

    def open(self):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError

    def write(self, data):
        raise NotImplementedError

    def read(self, length, timeout=1.0):
        raise NotImplementedError

    def read_until(self, terminator, timeout=1.0):
        raise NotImplementedError

    def flush(self):
        raise NotImplementedError

    def set_direction(self, transmitting):
        pass  # No-op for transports that handle direction automatically


class HostRS485Transport(RS485Transport):
    """Host-side RS485 transport via USB-to-RS485 adapter.

    Uses pyserial for communication. Supports:
    - FTDI FT232RL with CBUS0 for automatic DE/RE control
    - CH340/CP2102 with RTS signal for DE/RE control
    - Adapters with hardware auto-direction control

    Args:
        port: Serial port path (e.g., '/dev/ttyUSB0', 'COM3')
        baudrate: Baud rate (default 9600)
        parity: Parity ('N', 'E', 'O') (default 'N')
        stopbits: Stop bits (1, 1.5, 2) (default 1)
        bytesize: Data bits (5, 6, 7, 8) (default 8)
        direction_pin: DE/RE control method ('rts', 'none') (default 'rts')
        inter_byte_delay: Delay between bytes in seconds (default 0)
    """

    def __init__(self, port, baudrate=9600, parity='N', stopbits=1,
                 bytesize=8, direction_pin='rts', inter_byte_delay=0):
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._stopbits = stopbits
        self._bytesize = bytesize
        self._direction_pin = direction_pin
        self._inter_byte_delay = inter_byte_delay
        self._serial = None
        self._lock = threading.Lock()
        self._is_transmitting = False

    def open(self):
        import serial
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                parity=self._parity,
                stopbits=self._stopbits,
                bytesize=self._bytesize,
                timeout=1.0,
                write_timeout=1.0,
            )
            # Set RTS low (receive mode)
            if self._direction_pin == 'rts':
                self._serial.rts = False
            logging.info(
                "RS485: opened %s @ %d baud",
                self._port, self._baudrate,
            )
        except Exception as e:
            raise RS485TransportError(
                "Failed to open RS485 port %s: %s" % (self._port, e)
            )

    def close(self):
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                pass
            self._serial = None

    def set_direction(self, transmitting):
        if self._serial is None:
            return
        if self._direction_pin == 'rts':
            if transmitting and not self._is_transmitting:
                self._serial.rts = True
                time.sleep(0.0001)  # 100us settle time
            elif not transmitting and self._is_transmitting:
                self._serial.rts = False
        self._is_transmitting = transmitting

    def write(self, data):
        if self._serial is None:
            raise RS485TransportError("Port not open")
        with self._lock:
            self.set_direction(True)
            try:
                if self._inter_byte_delay > 0:
                    for b in data:
                        self._serial.write(bytes([b]))
                        time.sleep(self._inter_byte_delay)
                else:
                    self._serial.write(data)
                self._serial.flush()
            finally:
                # Small delay for last byte to shift out
                byte_time = 10.0 / self._baudrate
                time.sleep(byte_time * 2)
                self.set_direction(False)

    def read(self, length, timeout=1.0):
        if self._serial is None:
            raise RS485TransportError("Port not open")
        self._serial.timeout = timeout
        data = self._serial.read(length)
        return data

    def read_until(self, terminator, timeout=1.0):
        if self._serial is None:
            raise RS485TransportError("Port not open")
        self._serial.timeout = timeout
        data = bytearray()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            b = self._serial.read(1)
            if not b:
                break
            data.extend(b)
            if data[-len(terminator):] == terminator:
                break
        return bytes(data)

    def flush(self):
        if self._serial is not None:
            self._serial.flush()

    def get_baudrate(self):
        return self._baudrate

    def get_port(self):
        return self._port


class McuRS485Transport(RS485Transport):
    """MCU-side RS485 transport via the software bit-bang Modbus UART.

    Uses the same firmware bit-bang driver (src/modbus_uart.c) as the LYX
    stepper drivers. The bus is a half-duplex single-wire 8N1 UART driven
    on a single GPIO pin, so no USB-to-RS485 adapter is required.

    The transport buffers the full response of each transaction; the
    Modbus RTU protocol performs its read() calls against that buffer.

    Args:
        config: config section providing uart_pin and optional baud_rate
        slave_id: optional Modbus slave address to reserve on the bus
    """

    def __init__(self, config, slave_id=None):
        from .mcu_modbus import lookup_mcu_bitbang
        self._config = config
        self._bus_pin, self._mcu_modbus = lookup_mcu_bitbang(config)
        if slave_id is not None:
            self._mcu_modbus.register_slave(
                self._bus_pin, self._bus_pin, slave_id)
        self._rx_buffer = b''
        self._open = False

    def open(self):
        self._open = True
        logging.info(
            "RS485: opened MCU bit-bang Modbus on pin %s @ %d baud",
            self._bus_pin['pin'], self._mcu_modbus.baud,
        )

    def close(self):
        self._open = False
        self._rx_buffer = b''

    def _expected_response_len(self, data):
        """Infer the Modbus response length for the outgoing frame.

        Returns 0 (write-only) for frames that are not standard Modbus.
        """
        if len(data) < 2:
            return 0
        func_code = data[1]
        if func_code == 0x03 and len(data) >= 6:
            count = (data[4] << 8) | data[5]
            return 5 + 2 * count
        if func_code in (0x06, 0x10):
            return 8
        return 0

    def write(self, data):
        if not self._open:
            raise RS485TransportError("Port not open")
        with self._mcu_modbus.mutex:
            read_len = self._expected_response_len(data)
            self._rx_buffer = self._mcu_modbus.send_frame(data, read_len)

    def read(self, length, timeout=1.0):
        if len(self._rx_buffer) >= length:
            data, self._rx_buffer = self._rx_buffer[:length], self._rx_buffer[length:]
            return data
        data, self._rx_buffer = self._rx_buffer, b''
        return data

    def read_until(self, terminator, timeout=1.0):
        data = self._rx_buffer
        self._rx_buffer = b''
        if terminator:
            idx = data.find(terminator)
            if idx >= 0:
                keep = data[idx + len(terminator):]
                if keep:
                    self._rx_buffer = keep
                data = data[:idx + len(terminator)]
        return data

    def flush(self):
        self._rx_buffer = b''

    def get_baudrate(self):
        return self._mcu_modbus.baud
