/**
 * main.cpp - Arduino entry point for the Kalico MCU firmware
 *
 * Maps Arduino's setup()/loop() to the Kalico scheduler's sched_main().
 *
 * Setup flow:
 *   1. Initialize serial for debug output
 *   2. Initialize the Arduino serial port for MCU communication
 *   3. Initialize the hardware timer
 *   4. Call sched_main() — enters the Kalico cooperative scheduler loop
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "arduino/internal.h"

// Kalico core entry point (defined in sched.c)
extern "C" void sched_main(void);

// ============================================================================
// Arduino Setup
// ============================================================================

// Macro magic: map CONFIG_DEBUG_SERIAL_PORT to the right Serial object
#if CONFIG_DEBUG_SERIAL_PORT == 0
  #define DEBUG_SERIAL   Serial
#elif CONFIG_DEBUG_SERIAL_PORT == 1
  #define DEBUG_SERIAL   SerialUSB
#elif CONFIG_DEBUG_SERIAL_PORT == 2
  // Debug serial disabled — define as a no-op stream
  #define DEBUG_SERIAL_OFF  1
#else
  #define DEBUG_SERIAL   Serial
#endif

void setup()
{
#if !defined(DEBUG_SERIAL_OFF)
    // ---- Debug serial (USB) ----
    DEBUG_SERIAL.begin(CONFIG_DEBUG_SERIAL_BAUD);
    while (!DEBUG_SERIAL && millis() < 3000) {
        // Wait for USB serial on native USB boards (timeout 3s)
    }
    DEBUG_SERIAL.println();
    DEBUG_SERIAL.println(F("=== Kalico generic_arduino firmware ==="));
    DEBUG_SERIAL.print(F("Clock: "));
    DEBUG_SERIAL.print(CONFIG_CLOCK_FREQ);
    DEBUG_SERIAL.print(F(" Hz, Baud: "));
    DEBUG_SERIAL.println(CONFIG_SERIAL_BAUD);
    DEBUG_SERIAL.print(F("MCU Serial: "));
#if CONFIG_MCU_SERIAL_TYPE == 0
    DEBUG_SERIAL.print(F("Hardware UART"));
    #if CONFIG_MCU_SERIAL_HW_PORT == 0
      DEBUG_SERIAL.println(F(" (Serial)"));
    #elif CONFIG_MCU_SERIAL_HW_PORT == 1
      DEBUG_SERIAL.println(F(" (Serial1)"));
    #elif CONFIG_MCU_SERIAL_HW_PORT == 2
      DEBUG_SERIAL.println(F(" (Serial2)"));
    #elif CONFIG_MCU_SERIAL_HW_PORT == 3
      DEBUG_SERIAL.println(F(" (Serial3)"));
    #endif
#else
    DEBUG_SERIAL.print(F("Software Serial (RX="));
    DEBUG_SERIAL.print(CONFIG_MCU_SERIAL_SW_RX);
    DEBUG_SERIAL.print(F(", TX="));
    DEBUG_SERIAL.print(CONFIG_MCU_SERIAL_SW_TX);
    DEBUG_SERIAL.println(F(")"));
#endif
#endif // !DEBUG_SERIAL_OFF

    // ---- Initialize Arduino platform layer ----
    arduino_serial_init();
    arduino_timer_init();

#if !defined(DEBUG_SERIAL_OFF)
    DEBUG_SERIAL.println(F("[INIT] Platform initialized."));
    DEBUG_SERIAL.println(F("[INIT] Entering Kalico scheduler loop..."));
#endif

    // ---- Enter Kalico main loop ----
    // sched_main() never returns — it runs the cooperative scheduler forever.
    sched_main();

    // Unreachable
#if !defined(DEBUG_SERIAL_OFF)
    DEBUG_SERIAL.println(F("[FATAL] sched_main returned!"));
#endif
    for (;;) { delay(1000); }
}

// ============================================================================
// Arduino Loop (should never be called — sched_main runs forever)
// ============================================================================

void loop()
{
    // sched_main() contains its own infinite loop (run_tasks).
    // If we ever get here, something went wrong.
    delay(1000);
}
