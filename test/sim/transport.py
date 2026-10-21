# Fake RS485 transports
#
# Copyright (C) 2026  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# The transports implement the RS485Transport interface of
# klippy.extras.rs485.transport so that the host side of the protocol can
# be driven against a simulator without any hardware.
import threading


class FakeTransport:
    """A transport that is connected to a Modbus slave simulator."""

    def __init__(self, slave=None, baudrate=9600):
        self.slave = slave
        self._baudrate = baudrate
        self._rx = b""
        self._open = False
        # Log of the frames that were written by the host
        self.sent_frames = []

    def open(self):
        self._open = True

    def close(self):
        self._open = False
        self._rx = b""

    def write(self, data):
        if not self._open:
            raise RuntimeError("Port not open")
        data = bytes(data)
        self.sent_frames.append(data)
        if self.slave is not None:
            self._rx += self.slave.handle(data)

    def read(self, length, timeout=1.0):
        data, self._rx = self._rx[:length], self._rx[length:]
        return data

    def read_until(self, terminator, timeout=1.0):
        if not terminator:
            data, self._rx = self._rx, b""
            return data
        index = self._rx.find(terminator)
        if index < 0:
            data, self._rx = self._rx, b""
            return data
        end = index + len(terminator)
        data, self._rx = self._rx[:end], self._rx[end:]
        return data

    def flush(self):
        self._rx = b""

    def get_baudrate(self):
        return self._baudrate

    def get_port(self):
        return "fake"


class FakeBitbangModbus:
    """A stand-in for klippy.extras.rs485.mcu_modbus.MCUBitbangModbus.

    The firmware bit-bang uart is replaced by a Modbus slave simulator so
    that the host side of the LYX and RS485 stepper drivers can be tested
    without an MCU.
    """

    def __init__(self, slave=None, baud=38400):
        self.slave = slave
        self.baud = baud
        self.mutex = threading.Lock()
        self.instances = {}
        # Log of the frames that were sent to the bus
        self.sent_frames = []

    def register_slave(self, rx_pin_params, tx_pin_params, addr):
        self.instances[addr] = True
        return addr

    def send_frame(self, data, read_len=0, minclock=0):
        data = bytes(data)
        self.sent_frames.append(data)
        if self.slave is None:
            return b""
        response = self.slave.handle(data)
        if read_len:
            response = response[:read_len]
        return response

    def get_mcu(self):
        return None
