/**
 * arduino/timer.c - Hardware timer implementation for Arduino
 *
 * Provides platform-specific timer functions:
 *   timer_read_time(), timer_kick(),
 *   arduino_timer_init(), arduino_timer_irq_*()
 *
 * The generic functions (timer_from_us, timer_is_before, timer_dispatch_many)
 * are provided by generic/timer_irq.c.
 *
 * Derived from src/avr/timer.c
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>            // millis, micros, noInterrupts, interrupts
#include "autoconf.h"           // CONFIG_CLOCK_FREQ
#include "irq.h"                // irq_save
#include "misc.h"               // timer_from_us (declared; defined in generic/)
#include "internal.h"           // arduino_timer_*
#include "../command.h"         // DECL_CONSTANT
#include "../sched.h"           // sched_timer_dispatch

// Timer IRQ pending flag (set by timer ISR, cleared by irq_poll)
static volatile bool timer_irq_pending_flag = false;

// ---- Forward: timer_dispatch_many (from generic/timer_irq.c) -------------
extern uint32_t timer_dispatch_many(void);

// ============================================================================
// Platform-specific timer implementation
// ============================================================================

#if defined(__AVR__)

#include <avr/interrupt.h>
#include <avr/io.h>

// ---- AVR Timer1 (16-bit) ----
// Timer1 is used because Timer0 is reserved for millis()/micros()

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

// AVR 32-bit time: extended by counting Timer1 overflows
static volatile uint32_t timer_overflow_count = 0;

// Timer1 overflow ISR — extends the 16-bit counter to 32-bit
ISR(TIMER1_OVF_vect)
{
    timer_overflow_count++;
}

// Timer1 compare match A ISR — signals that a timer dispatch is needed
ISR(TIMER1_COMPA_vect)
{
    timer_irq_pending_flag = true;
}

uint32_t
timer_read_time(void)
{
    uint8_t sreg = SREG;
    noInterrupts();
    uint16_t cnt = TCNT1;
    uint32_t ovf = timer_overflow_count;
    if ((TIFR1 & (1 << TOV1)) && cnt < 32768) {
        ovf++;
    }
    SREG = sreg;
    return (ovf << 16) | cnt;
}

void
timer_kick(void)
{
    OCR1A = TCNT1 + 50;
    TIFR1 = 1 << OCF1A;
}

// Re-arm timer with a 32-bit absolute timer value.
// Extracts the low 16 bits for OCR1A (compare) but also ensures
// the overflow count is consistent.
void
timer_kick_next(uint32_t next_time)
{
    // next_time is (overflow << 16) | compare.  We only write the
    // compare value to OCR1A; the overflow ISR will extend the count
    // transparently.
    uint16_t compare = (uint16_t)(next_time & 0xFFFF);
    // Avoid setting OCR1A too close to TCNT1 (must be > ~10 ticks ahead).
    uint16_t now = TCNT1;
    if ((int16_t)(compare - now) < 10)
        compare = now + 50;
    OCR1A = compare;
    TIFR1 = 1 << OCF1A;
}

bool
arduino_timer_irq_pending(void)
{
    return timer_irq_pending_flag;
}

void
arduino_timer_irq_clear(void)
{
    timer_irq_pending_flag = false;
}

void
arduino_timer_init(void)
{
    irqstatus_t flag = irq_save();

    TCCR1A = 0;                          // Normal mode
    TCCR1B = (1 << CS10);                // Prescaler = 1
    TCCR1C = 0;
    TCNT1 = 0;
    timer_overflow_count = 0;
    TIMSK1 = (1 << TOIE1) | (1 << OCIE1A);
    OCR1A = timer_from_us(100);

    irq_restore(flag);
}

#elif defined(__arm__) || defined(__ARM_ARCH)

// ---- ARM Cortex-M (Arduino Due, Teensy 3.x/4.x, etc.) ----
// Uses the SysTick timer extended to 32-bit via millis()/micros()

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

uint32_t
timer_read_time(void)
{
    uint32_t ms = millis();
    uint32_t us_part = micros() % 1000;
    uint32_t total_us = ms * 1000UL + us_part;
    return timer_from_us(total_us);
}

void
timer_kick(void)
{
    timer_irq_pending_flag = true;
}

bool
arduino_timer_irq_pending(void)
{
    return timer_irq_pending_flag;
}

void
arduino_timer_irq_clear(void)
{
    timer_irq_pending_flag = false;
}

void
arduino_timer_init(void)
{
    // ARM Arduino: SysTick already runs, rely on irq_poll periodic calling
}

void
timer_kick_next(uint32_t next_time)
{
    (void)next_time;
    // ARM: timer dispatch happens synchronously in irq_poll().
    // No hardware timer to re-arm — timer_kick() sets the flag,
    // irq_poll() calls timer_dispatch_many() synchronously.
}

#else

// ---- Generic fallback (ESP32, etc.) ----
DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

uint32_t
timer_read_time(void)
{
    return micros() * (CONFIG_CLOCK_FREQ / 1000000UL);
}

void
timer_kick(void)
{
    timer_irq_pending_flag = true;
}

bool
arduino_timer_irq_pending(void)
{
    return timer_irq_pending_flag;
}

void
arduino_timer_irq_clear(void)
{
    timer_irq_pending_flag = false;
}

void
arduino_timer_init(void)
{
    // Generic: no hardware timer setup needed (poll-based)
}

// Non-AVR fallback for timer_kick_next — not needed because
// timer_dispatch_many() re-arms via the irq_poll loop.
void timer_kick_next(uint32_t next_time)
{
    (void)next_time;
    // On ARM/ESP32, timer dispatch happens synchronously in irq_poll()
    // so no hardware re-arm is needed.
}

#endif
