#!/bin/bash
# One-shot: kill klippy/moonraker, flash, test
set -e
echo "=== KILLING ==="
kill -9 $(pgrep -f 'moonraker|klippy.*printer' 2>/dev/null) 2>/dev/null || true
sleep 1.5

echo "=== FLASHING ==="
avrdude -q -c arduino -p m328p -P /dev/ttyUSB1 -b 115200 -U flash:w:/tmp/kf.hex:i

echo "=== TESTING ==="
sleep 3
timeout 15 /home/armbian/klippy-env/bin/python /home/armbian/klipper/klippy/klippy.py \
    /home/armbian/printer_data/config/printer.cfg \
    -l /tmp/klippy-onerun.log -v 2>&1

echo "=== RESULT ==="
grep -E 'Loaded|Sending|Configured|Printer is ready|Welcome|shutdown|error' /tmp/klippy-onerun.log | head -10
echo "=== TAIL ==="
tail -3 /tmp/klippy-onerun.log
