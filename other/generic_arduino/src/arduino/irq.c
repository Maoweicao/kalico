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

#include <Arduino.h>
#if defined(__AVR__)
#include <avr/sleep.h>
#endif
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
//
// IMPORTANT: This port uses polled serial (Arduino's HardwareSerial),
// NOT interrupt-driven UART.  During the 500µs delay below, Arduino's
// UART RX ISR puts bytes into the internal HardwareSerial buffer, BUT
// arduino_serial_drain_rx() / serial_rx_byte() / sched_wake_tasks()
// are the ONLY way those bytes get fed into Kalico's command parser.
//
// If we don't drain them here, run_tasks() sleeps forever because
// sched_wake_tasks() is never called and tasks_status stays TS_IDLE.
//
void
irq_wait(void)
{
#if defined(__AVR__)
    interrupts();
    delayMicroseconds(500);
    noInterrupts();
#elif defined(__arm__) || defined(__ARM_ARCH)
    __enable_irq();
    delayMicroseconds(500);
    __disable_irq();
#else
    interrupts();
    delayMicroseconds(500);
    noInterrupts();
#endif
    // 🔑 Drain serial bytes that arrived during the delay window.
    // Without this, data accumulates in Arduino's HardwareSerial buffer
    // but never reaches Kalico's command parser → system deadlocks.
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
    // Also handle any timer events that fired.
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
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
        uint32_t next = timer_dispatch_many();
        // Re-arm timer hardware so COMPA keeps firing
        timer_kick_next(next);
    }
}
