/**
 * arduino/irq.c - Interrupt management implementation for Arduino
 *
 * Maps Klipper's irq_* API to platform-specific primitives.
 *
 * AVR: ISR-native timer dispatch — irq_poll() only handles serial.
 * ARM/ESP32: Poll-based — irq_poll() handles both serial and timers.
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#if defined(__AVR__)
#include <avr/sleep.h>
#endif
#include "autoconf.h"
#include "irq.h"
#include "internal.h"

// ---- irq_disable / irq_enable ----

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
    uint8_t primask;
#if defined(__AVR__)
    primask = SREG & 0x80;  // Global Interrupt Enable flag
    noInterrupts();
#elif defined(__arm__) || defined(__ARM_ARCH)
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

// ---- irq_wait ----
// Sleep until next interrupt, then drain any pending serial data.
//
// On AVR with ISR-native timer dispatch, timers are handled entirely
// inside the Timer1 COMPA ISR.  irq_wait() only needs to drain serial.
//
// On ARM/ESP32 with poll-based dispatch, irq_wait() also checks for
// pending timer events.

void
irq_wait(void)
{
#if defined(__AVR__)
    // AVR ISR-native: brief interrupt window for pending ISRs.
    // Timer dispatch happens entirely inside the Timer1 COMPA ISR.
    // Arduino HardwareSerial accumulates bytes in its own buffer —
    // we must drain them here so serial_rx_byte() sees MESSAGE_SYNC
    // and calls sched_wake_tasks(), breaking us out of the idle loop.
    irq_enable();
    if (arduino_serial_rx_pending())
        arduino_serial_drain_rx();
    else
        __asm__ __volatile__("nop" ::: "memory");
    irq_disable();
#elif defined(__arm__) || defined(__ARM_ARCH)
    __enable_irq();
    __asm__ __volatile__("nop" ::: "memory");
    __disable_irq();
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
#else
    interrupts();
    __asm__ __volatile__("nop" ::: "memory");
    noInterrupts();
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
#if CONFIG_WANT_WIFI && defined(ESP32)
    delay(0);
#endif
#endif
}

// ---- irq_poll ----
// Called from main loop to handle pending work.
//
// On AVR with ISR-native mode: only drains serial data.
// On ARM/ESP32: drains serial AND dispatches pending timers.

void
irq_poll(void)
{
#if defined(__AVR__)
    // AVR ISR-native: timers dispatched in ISR, only handle serial here
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
#else
    // ARM/ESP32 poll-based: check both serial and timer
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
#if CONFIG_WANT_WIFI && defined(ESP32)
    delay(0);
#endif
#endif
}
