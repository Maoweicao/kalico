#!/bin/bash
# Flash and test generic_arduino Uno firmware
set -e
sudo fuser -k /dev/ttyUSB1 2>/dev/null || true
sleep 2
avrdude -q -c arduino -p m328p -P /dev/ttyUSB1 -b 115200 -U flash:w:/tmp/kf.hex:i
echo "FLASHED"
sleep 4
timeout 25 /home/armbian/klippy-env/bin/python /home/armbian/klipper/klippy/klippy.py \
    /home/armbian/printer_data/config/printer.cfg \
    -l /tmp/klippy-test.log 2>&1
echo "=== RESULT ==="
grep -E 'Loaded|Sending|Configured|Printer is ready|Welcome|error|Error|shutdown|Klippy done' /tmp/klippy-test.log | head -12
echo "=== TAIL ==="
tail -5 /tmp/klippy-test.log
