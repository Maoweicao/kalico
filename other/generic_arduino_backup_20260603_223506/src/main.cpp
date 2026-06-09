/**
 * main.cpp - Arduino entry point for the Kalico MCU firmware
 *
 * Maps Arduino's setup()/loop() to the Kalico scheduler's sched_main().
 *
 * Setup flow:
 *   1. Disable Arduino's Timer0 ISR (we have our own timer)
 *   2. Call sched_main() — enters the Kalico cooperative scheduler loop
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include <avr/interrupt.h>
#include "autoconf.h"
#include "arduino/internal.h"

// Kalico core entry point (defined in sched.c)
extern "C" void sched_main(void);

// ============================================================================
// Arduino Setup
// ============================================================================

void setup()
{
    // ---- Disable Arduino's Timer0 overflow interrupt ----
    // Arduino's init() enables TIMER0_OVF for millis()/micros().
    // We don't need it — Klipper has its own timer system.
    // Leaving it active wastes stack space on every ISR (~50 bytes)
    // and can cause stack overflow on AVR with limited RAM.
    TIMSK0 = 0;

    // ---- Enter Kalico main loop ----
    // sched_main() never returns — it runs the cooperative scheduler forever.
    // Serial init and timer init are handled by registrations.c → ctr_run_initfuncs().
    sched_main();
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
