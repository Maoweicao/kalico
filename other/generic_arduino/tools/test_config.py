#!/usr/bin/env python3
"""Test script: connect to MCU and send get_config, get_uptime"""
import sys, time
sys.path.insert(0, '/home/armbian/klipper')

from klippy import serialhdl, msgproto, chelper
import serial

# Connect
ser = serial.Serial('/dev/ttyUSB0', 250000, timeout=0, exclusive=True)
ser.close()
ser.open()

# Create SerialReader
class FakeReactor:
    def __init__(self):
        self._completions = {}
        self._next_id = 1
    def register_callback(self, cb):
        return self
    def completion(self):
        return self
    def async_complete(self, c, params):
        pass
    def pause(self, t):
        time.sleep(t)
    def monotonic(self):
        return time.monotonic()

reactor = FakeReactor()
sr = serialhdl.SerialReader(reactor)

# Start session
sr._start_session(ser)

# Now send get_config
try:
    params = sr.send_with_response("get_config", "config")
    print(f"get_config response: {params}")
except Exception as e:
    print(f"get_config error: {e}")

# Try get_uptime
try:
    params = sr.send_with_response("get_uptime", "uptime")
    print(f"get_uptime response: {params}")
except Exception as e:
    print(f"get_uptime error: {e}")

sr.disconnect()
