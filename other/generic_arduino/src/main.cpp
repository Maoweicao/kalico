/**
 * main.cpp - Entry point for the Kalico MCU firmware
 *
 * Maps platform-specific entry points to the Kalico scheduler's sched_main().
 *
 * AVR (Arduino):  setup()/loop() → sched_main()
 * STM32H723:      main() → clock_setup() → sched_main()
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"

// Kalico core entry point (defined in sched.c)
extern "C" void sched_main(void);

// ============================================================================
// STM32 Entry Point
// ============================================================================

#if CONFIG_MACH_STM32

#include "stm32/internal.h"

// Declared in stm32/timer.c
extern "C" void stm32_timer_init(void);

// Declared in stm32/serial.c
extern "C" void stm32_serial_init(void);

// Forward declarations for registration-based init
extern "C" void alloc_init(void);
extern "C" void arduino_serial_init(void);
extern "C" void arduino_timer_init(void);

// Override the registration names so registrations.c links correctly.
// stm32_serial_init() and stm32_timer_init() are the actual implementations.
void arduino_serial_init(void) { stm32_serial_init(); }
void arduino_timer_init(void)  { stm32_timer_init(); }

extern "C"
int main(void)
{
    // ---- Configure system clock to 528MHz via PLL1 ----
    // Must be done before any peripheral access that depends on clock speed.
    stm32_clock_setup();

    // ---- Enter Kalico main loop ----
    // Serial init and timer init are handled by registrations.c → ctr_run_initfuncs().
    // sched_main() never returns.
    sched_main();

    // Should never reach here
    for (;;) ;
}

// ============================================================================
// Arduino Entry Point (AVR / ARM / ESP32)
// ============================================================================

#else // !CONFIG_MACH_STM32

#include <Arduino.h>
#if defined(__AVR__)
#include <avr/interrupt.h>
#endif
#include "arduino/internal.h"

void setup()
{
#if defined(__AVR__)
    // Disable Arduino's Timer0 overflow interrupt (we have our own timer)
    TIMSK0 = 0;
#endif

    // Enter Kalico main loop
    sched_main();
}

void loop()
{
    // sched_main() contains its own infinite loop.
    // If we ever get here, something went wrong.
    delay(1000);
}

#endif // CONFIG_MACH_STM32
