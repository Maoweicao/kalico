#!/bin/bash
PORT=$(readlink -f /dev/serial/by-id/usb-1a86_USB_Serial-if00-port0 2>/dev/null | xargs basename)
echo "PORT=$PORT"
kill -9 $(pgrep -f 'moonraker|klippy.*printer|klippy.*mini' 2>/dev/null) 2>/dev/null || true
sleep 1.5
avrdude -q -c arduino -p m328p -P /dev/$PORT -b 115200 -U flash:w:/tmp/kf.hex:i
echo "FLASHED"
sleep 3
timeout 15 /home/armbian/klippy-env/bin/python /home/armbian/klipper/klippy/klippy.py \
    /tmp/mini.cfg -l /tmp/km.log 2>&1
echo "DONE"
grep -E 'Loaded|Sending|Configured|Printer is ready|Welcome|shutdown|error|config is_' /tmp/km.log
echo "===TAIL==="
tail -3 /tmp/km.log
