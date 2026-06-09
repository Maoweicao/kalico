#!/bin/bash
# run_simavr.sh - Start simavr with PTY for UART communication
# Uses run_avr (simavr built-in) + socat for UART1 bridging
FIRMWARE="${1:-../.pio/build/mega2560/firmware.hex}"
SIMAVR_HOME="${SIMAVR_HOME:-$HOME/simavr}"
RUN_AVR="$SIMAVR_HOME/simavr/run_avr"
SOCAT=$(which socat)

echo "=== Kalico SimAVR Launcher ==="
echo "Firmware: $FIRMWARE"

# Create PTY pair for UART1 MCU communication
UART1_PTY=$($SOCAT -d -d PTY,raw,echo=0 PTY,raw,echo=0 2>&1 | grep 'PTY is' | head -2 | awk '{print $NF}')
UART1_MASTER=$(echo "$UART1_PTY" | head -1)
UART1_SLAVE=$(echo "$UART1_PTY" | tail -1)

echo "UART1 Master: $UART1_MASTER"
echo "UART1 Slave:  $UART1_SLAVE"
echo ""

# Run simavr with UART1 connected via socat
# (socat bridges UART1 slave to TCP or just expose the slave path)
echo "Starting simavr..."
echo "UART1 path (for Klipper/host): $UART1_SLAVE"
echo ""
echo "Press Ctrl+C to stop."
echo ""

# Run in background
LD_LIBRARY_PATH="$SIMAVR_HOME/simavr/obj-x86_64-linux-gnu:$SIMAVR_HOME/examples/parts/obj-x86_64-linux-gnu" \
    timeout 300 "$RUN_AVR" -m atmega2560 -f 16000000 "$FIRMWARE" 2>&1

kill %1 2>/dev/null
