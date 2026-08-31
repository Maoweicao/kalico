// esp32s3_uart - minimal Kalico MCU firmware based on kalico_mcu_lib.
//
// Runs the Kalico scheduler cooperatively from Arduino setup()/loop().
// The ESP32-S3 default UART0 (TX=GPIO43 RX=GPIO44) carries the Klipper
// wire protocol at 250000 baud.
//
// For a real handshake test, use other/kalico_debug_tool:
//   cd other && python -m kalico_debug_tool

#include <Arduino.h>
#include <kalico_mcu.h>

void setup()
{
    klipper_init();
}

void loop()
{
    klipper_loop();
}