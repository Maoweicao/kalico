/**
 * arduino/timer.c - Hardware timer implementation for Arduino
 *
 * Platform-specific timer functions with ISR-native dispatch on AVR
 * and poll-based dispatch on ARM/ESP32.
 *
 * AVR: Timer1 COMPA ISR directly calls sched_timer_dispatch() —
 *      same as native Klipper src/avr/timer.c, enabling real-time
 *      stepper ISR scheduling.
 *
 * ARM/ESP32: Timer ISR sets a flag; irq_poll() dispatches timers.
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"           // CONFIG_CLOCK_FREQ
#include "irq.h"                // irq_save, irq_enable, irq_disable
#include "misc.h"               // timer_from_us (declared; defined in generic/)
#include "internal.h"           // arduino_timer_*
#include "../command.h"         // DECL_CONSTANT
#include "../sched.h"           // sched_timer_dispatch


// ============================================================================
// AVR: ISR-native timer dispatch (directly from Timer1 COMPA ISR)
// ============================================================================

#if defined(__AVR__)

#include <avr/interrupt.h>
#include <avr/io.h>

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

// ---- 32-bit timer: high 16 bits from overflow counting ----
static uint16_t timer_high;

// Wrap timer: handles 16→32 bit overflow extension
static struct timer wrap_timer;

// Forward declarations
extern void sched_add_timer(struct timer *add);

static uint_fast8_t
timer_event(struct timer *t)
{
    uint16_t *nextwake = (void*)&wrap_timer.waketime;
    if (TIFR1 & (1<<TOV1)) {
        TIFR1 = 1<<TOV1;
        timer_high++;
        // Schedule next overflow check at mid-point of next 16-bit cycle
        uint32_t nw = ((uint32_t)timer_high << 16) | 0x8000;
        *nextwake = (uint16_t)nw;
    } else {
        // Not overflowed yet — check again after wrap
        uint32_t nw = ((uint32_t)(timer_high + 1)) << 16;
        *nextwake = (uint16_t)nw;
    }
    return SF_RESCHEDULE;
}

static struct timer wrap_timer = {
    .func = timer_event,
    .waketime = 0x8000,
};

// ---- ISR timing constants (from native Klipper) ----
#define TIMER_REPEAT_TICKS 3000
#define TIMER_MIN_ENTRY_TICKS 44
#define TIMER_MIN_EXIT_TICKS 47
#define TIMER_MIN_TRY_TICKS (TIMER_MIN_ENTRY_TICKS + TIMER_MIN_EXIT_TICKS)
#define TIMER_DEFER_REPEAT_TICKS 256

static inline uint16_t
timer_get(void)
{
    return TCNT1;
}

static inline void
timer_set(uint16_t next)
{
    OCR1A = next;
}

static inline void
timer_repeat_set(uint16_t next)
{
    OCR1B = next;
    // Clear OCF1B flag — hand-coded for efficiency
    uint8_t dummy;
    asm volatile("ldi %0, %2\n    out %1, %0"
                 : "=d"(dummy) : "i"(&TIFR1 - 0x20), "i"(1<<OCF1B));
}

// Activate timer dispatch as soon as possible
void
timer_kick(void)
{
    timer_set(timer_get() + 50);
    TIFR1 = 1<<OCF1A;
}

void
timer_kick_next(uint32_t next_time)
{
    // Only the low 16 bits matter for OCR1A
    OCR1A = (uint16_t)(next_time & 0xFFFF);
    TIFR1 = 1 << OCF1A;
}

// Return the current time (in absolute clock ticks, 32-bit)
uint32_t
timer_read_time(void)
{
    irqstatus_t flag = irq_save();
    uint16_t cnt = timer_get();
    uint16_t hi = timer_high;
    if (unlikely(TIFR1 & (1<<TOV1))) {
        irq_restore(flag);
        if ((uint8_t)(cnt >> 8) < 0xff)
            hi++;
        return ((uint32_t)hi << 16) | cnt;
    }
    irq_restore(flag);
    return ((uint32_t)hi << 16) | cnt;
}

// ---- Timer1 COMPA ISR: directly dispatches software timers ----
// This is the key change from poll-based to ISR-native mode.
// The stepper_event() function runs directly inside this ISR,
// ensuring deterministic, low-latency step pulse timing.
ISR(TIMER1_COMPA_vect)
{
    uint16_t next;
    for (;;) {
        // Run the next software timer (may call stepper_event)
        next = sched_timer_dispatch();

        for (;;) {
            int16_t diff = timer_get() - next;
            if (likely(diff >= 0)) {
                // Timer has expired — run next one
                // Briefly allow nested irqs to check for defer
                irq_enable();
                if (unlikely(TIFR1 & (1<<OCF1B)))
                    goto check_defer;
                irq_disable();
                break;
            }

            if (likely(diff <= -(int16_t)TIMER_MIN_TRY_TICKS))
                // Timer is far enough in the future — schedule it
                goto done;

            // Timer is close — spin-wait
            irq_enable();
            if (unlikely(TIFR1 & (1<<OCF1B)))
                goto check_defer;
            irq_disable();
            continue;

        check_defer:
            // Too many repeat timers — defer to main loop
            irq_disable();
            uint16_t now = timer_get();
            if ((int16_t)(next - now) < (int16_t)(-timer_from_us(1000)))
                try_shutdown("Rescheduled timer in the past");
            if (sched_check_set_tasks_busy()) {
                timer_repeat_set(now + TIMER_REPEAT_TICKS);
                next = now + TIMER_DEFER_REPEAT_TICKS;
                goto done;
            }
            timer_repeat_set(now + TIMER_REPEAT_TICKS);
            timer_set(now);
        }
    }

done:
    timer_set(next);
}

// ---- Initialization ----
void
arduino_timer_init(void)
{
    static bool initialized = false;
    if (initialized)
        return;
    initialized = true;

    irqstatus_t flag = irq_save();

    TCCR1A = 0;                          // Normal mode
    TCCR1B = (1 << CS10);                // Prescaler = 1 (16 MHz)
    TCCR1C = 0;
    TCNT1 = 0;
    timer_high = 0;

    // Setup for first IRQ
    timer_kick();
    timer_repeat_set(timer_get() + 50);

    // Register wrap_timer for 16→32 bit overflow handling
    sched_add_timer(&wrap_timer);

    // Clear overflow flag and enable COMPA interrupt
    TIFR1 = 1<<TOV1;
    TIMSK1 = (1 << OCIE1A);

    irq_restore(flag);
}

// AVR ISR-native mode: these functions are not used in the main loop
// (timer dispatch happens entirely inside the ISR)
bool
arduino_timer_irq_pending(void)
{
    return false;
}

void
arduino_timer_irq_clear(void)
{
    // No-op: ISR handles everything
}

// ============================================================================
// ARM (Arduino Due, Teensy 3.x/4.x) — Poll-based timer dispatch
// ============================================================================

#elif defined(__arm__) || defined(__ARM_ARCH)

#include <Arduino.h>

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

static volatile bool timer_irq_pending_flag = false;

extern uint32_t timer_dispatch_many(void);

// ARM SysTick-based 32-bit timer
uint32_t
timer_read_time(void)
{
    // Use DWT cycle counter if available, else micros()
#if defined(DWT_BASE) && defined(DWT_CYCCNT)
    return DWT->CYCCNT;
#else
    return micros() * (CONFIG_CLOCK_FREQ / 1000000UL);
#endif
}

void
timer_kick(void)
{
    timer_irq_pending_flag = true;
}

void
timer_kick_next(uint32_t next_time)
{
    (void)next_time;
    // On ARM, timer dispatch happens synchronously in irq_poll()
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
    // ARM: SysTick/DWT already running by Arduino core
}

// ============================================================================
// ESP32 / Generic fallback — Poll-based timer dispatch
// ============================================================================

#else

#include <Arduino.h>

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

static volatile bool timer_irq_pending_flag = false;

extern uint32_t timer_dispatch_many(void);

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

void
timer_kick_next(uint32_t next_time)
{
    (void)next_time;
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
    // ESP32: no hardware timer setup needed (poll-based)
}

#endif
