#!/bin/bash
set -e
pkill -9 simavr_runner 2>/dev/null || true
rm -f /tmp/simavr-uart*
rm -f /tmp/klippy_test.log
export LD_LIBRARY_PATH=/usr/local/lib

echo "Starting simavr..."
/mnt/f/kalico/other/generic_arduino/simavr/simavr_runner \
  /mnt/f/kalico/other/generic_arduino/.pio/build/mega2560/firmware.hex &
MCPU=$!
sleep 2

PTY=$(readlink /tmp/simavr-uart1)
echo "UART1 PTY: $PTY"

sed "s|REPLACE_WITH_PTY_PATH|$PTY|" \
  /mnt/f/kalico/other/generic_arduino/simavr/klippy_test.cfg \
  > /tmp/klippy_test.cfg

echo "Starting klippy..."
cd /mnt/f/kalico
python3 ./klippy/klippy.py /tmp/klippy_test.cfg -l /tmp/klippy_test.log 2>&1 &
KPID=$!

sleep 15
kill $KPID 2>/dev/null || true
kill $MCPU 2>/dev/null || true
wait 2>/dev/null || true

echo ""
echo "=== KLIPPY LOG ==="
cat /tmp/klippy_test.log 2>/dev/null | tail -80
