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

void setup()
{
    // ---- Debug serial (USB) ----
    Serial.begin(115200);
    while (!Serial && millis() < 3000) {
        // Wait for USB serial on native USB boards (timeout 3s)
    }
    Serial.println();
    Serial.println(F("=== Kalico generic_arduino firmware ==="));
    Serial.print(F("Clock: "));
    Serial.print(CONFIG_CLOCK_FREQ);
    Serial.print(F(" Hz, Baud: "));
    Serial.println(CONFIG_SERIAL_BAUD);

    // ---- Initialize Arduino platform layer ----
    arduino_serial_init();
    arduino_timer_init();

    Serial.println(F("[INIT] Platform initialized."));
    Serial.println(F("[INIT] Entering Kalico scheduler loop..."));

    // ---- Enter Kalico main loop ----
    // sched_main() never returns — it runs the cooperative scheduler forever.
    sched_main();

    // Unreachable
    Serial.println(F("[FATAL] sched_main returned!"));
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
