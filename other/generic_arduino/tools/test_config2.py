#!/usr/bin/env python3
"""Test script v2: Use real python reactor thread to test get_config"""
import sys, time, threading
sys.path.insert(0, '/home/armbian/klipper')

from klippy import serialhdl, reactor as reactor_mod
import serial

# Create real reactor
re = reactor_mod.Reactor()
def run_reactor():
    re.run()
t = threading.Thread(target=run_reactor, daemon=True)
t.start()
time.sleep(0.5)

# Create SerialReader with real reactor
sr = serialhdl.SerialReader(re)

# Connect via UART
sr.connect_uart('/dev/ttyUSB0', 250000)

# Now send get_config
try:
    params = sr.send_with_response("get_config", "config")
    print(f"get_config OK: {params}")
except Exception as e:
    print(f"get_config ERROR: {e}")

# Try get_uptime for comparison
try:
    params = sr.send_with_response("get_uptime", "uptime")
    print(f"get_uptime OK: {params}")
except Exception as e:
    print(f"get_uptime ERROR: {e}")

sr.disconnect()
print("Done")
