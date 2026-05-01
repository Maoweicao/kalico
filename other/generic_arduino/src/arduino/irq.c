/**
 * arduino/irq.c - Interrupt management implementation for Arduino
 *
 * Maps Kalico's irq_* API to Arduino's noInterrupts()/interrupts()
 * and Architecture-specific interrupt primitives.
 *
 * Derived from src/avr/irq.h and src/linux/timer.c
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "irq.h"
#include "internal.h"

// Arduino core provides noInterrupts()/interrupts() macros
// which map to cli()/sei() on AVR or __disable_irq()/__enable_irq() on ARM

void
irq_disable(void)
{
    noInterrupts();
}

void
irq_enable(void)
{
    interrupts();
}

irqstatus_t
irq_save(void)
{
    // On Arduino, we use the SREG (AVR) or PRIMASK (ARM) as status
    // For simplicity, we use a flag-based approach
    uint8_t primask;
#if defined(__AVR__)
    primask = SREG & 0x80;  // Global Interrupt Enable flag
    noInterrupts();
#elif defined(__arm__) || defined(__ARM_ARCH)
    // Read PRIMASK
    __asm__ __volatile__("mrs %0, primask" : "=r"(primask));
    __disable_irq();
#else
    primask = 0;
    noInterrupts();
#endif
    return primask;
}

void
irq_restore(irqstatus_t flag)
{
#if defined(__AVR__)
    if (flag)
        interrupts();
#elif defined(__arm__) || defined(__ARM_ARCH)
    if (!flag)
        __enable_irq();
#else
    if (flag)
        interrupts();
#endif
}

// Wait for an interrupt (sleep until next IRQ)
void
irq_wait(void)
{
    // On AVR: sleep_cpu() with interrupts enabled will wake on next IRQ
    // On ARM: __WFI() does the same
#if defined(__AVR__)
    interrupts();
    // AVR sleep modes: idle mode wakes on any interrupt
    SMCR = (SMCR & ~(_BV(SM0) | _BV(SM1) | _BV(SM2))) | (0 << SM0); // Idle
    sleep_cpu();
#elif defined(__arm__) || defined(__ARM_ARCH)
    __enable_irq();
    __WFI();
    __disable_irq();
#else
    // Fallback: brief yield via delay
    interrupts();
    delayMicroseconds(10);
    noInterrupts();
#endif
}

// Poll for pending work (called from main loop)
void
irq_poll(void)
{
    // Check if we need to handle serial data
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }

    // Check if timer ISR needs attention
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        timer_dispatch_many();
    }
}
