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
    """MCU-side RS485 transport via UART + DE/RE GPIO.

    Placeholder for future implementation. Requires MCU firmware support
    for RS485 direction control.
    """

    def __init__(self, mcu, uart_bus, baudrate, de_pin=None):
        self._mcu = mcu
        self._uart_bus = uart_bus
        self._baudrate = baudrate
        self._de_pin = de_pin
        raise RS485TransportError(
            "MCU-side RS485 transport not yet implemented. "
            "Use rs485_transport: host with a USB-to-RS485 adapter."
        )

    def open(self):
        pass

    def close(self):
        pass

    def write(self, data):
        pass

    def read(self, length, timeout=1.0):
        return b''

    def read_until(self, terminator, timeout=1.0):
        return b''

    def flush(self):
        pass
