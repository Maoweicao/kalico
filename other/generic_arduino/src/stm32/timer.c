/**
 * stm32/timer.c - ISR-native timer for STM32H723 using TIM2 (32-bit)
 *
 * TIM2 runs at APB1 timer clock (FREQ_PERIPH = CONFIG_CLOCK_FREQ/4 = 132MHz).
 * It counts continuously and fires a compare-match interrupt (CC1) to
 * dispatch software timers.  The dispatch happens entirely inside the ISR,
 * providing deterministic, low-latency step pulse timing (like AVR's
 * Timer1 COMPA ISR but natively 32-bit — no software overflow extension).
 *
 * Derived from Klipper src/avr/timer.c (ISR-native concept)
 * and src/stm32/timer.c (STM32 timer hardware).
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"           /* CONFIG_CLOCK_FREQ */
#include "internal.h"
#include "irq.h"                /* irq_save, irq_enable, irq_disable */
#include "misc.h"               /* timer_from_us (defined in generic/timer_irq.c) */
#include "command.h"            /* DECL_CONSTANT, try_shutdown */
#include "sched.h"              /* sched_timer_dispatch */
#include "compiler.h"           /* likely, unlikely */

/* ---- Timer frequency constant ------------------------------------------ */

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

/* ---- ISR timing constants ---------------------------------------------- */
/* These control how the ISR handles deferred/repeated timer dispatch.
 * At 132MHz, 1 tick ≈ 7.58ns.
 * TIMER_REPEAT_TICKS  = 100µs worth of ticks = ~13200 ticks
 * TIMER_MIN_TRY_TICKS = minimum ticks before we schedule a wakeup
 * TIMER_DEFER_REPEAT_TICKS = defer interval when many repeat timers */
#define TIMER_REPEAT_TICKS      (FREQ_PERIPH / 10)   /* 100µs */
#define TIMER_MIN_TRY_TICKS     (FREQ_PERIPH / 500000) /* ~2µs ≈ 264 */
#define TIMER_DEFER_REPEAT_TICKS (FREQ_PERIPH / 200000) /* ~5µs ≈ 660 */

/* ---- TIM2 hardware helpers --------------------------------------------- */

static inline uint32_t
timer_get(void)
{
    return TIM2->CNT;
}

static inline void
timer_set(uint32_t next)
{
    TIM2->CCR1 = next;
}

static inline void
timer_repeat_set(uint32_t next)
{
    TIM2->CCR2 = next;
    /* Clear CC2 interrupt flag */
    TIM2->SR = ~TIM_SR_CC2IF;
}

/* ---- Timer kick -------------------------------------------------------- */
/* Activate timer dispatch as soon as possible (used at init and by
 * sched code). */

void
timer_kick(void)
{
    timer_set(timer_get() + 500);
    /* Clear any pending CC1 interrupt and re-enable */
    TIM2->SR = ~TIM_SR_CC1IF;
}

/* ---- Timer read -------------------------------------------------------- */
/* Return the current time in absolute 32-bit clock ticks. */

uint32_t
timer_read_time(void)
{
    return TIM2->CNT;
}

/* ---- TIM2 Compare-Match ISR ------------------------------------------- */
/* This is the ISR-native timer dispatch.  It directly calls
 * sched_timer_dispatch() which may invoke stepper_event() and other
 * timer callbacks.  This ensures deterministic, low-latency step pulse
 * timing — identical in concept to AVR's TIMER1_COMPA_vect. */

void
TIM2_IRQHandler(void)
{
    uint32_t next;
    for (;;) {
        /* Run the next software timer (may call stepper_event, etc.) */
        next = sched_timer_dispatch();

        for (;;) {
            int32_t diff = (int32_t)(timer_get() - next);
            if (likely(diff >= 0)) {
                /* Timer has expired — run next one.
                 * Briefly allow nested IRQs to check for defer. */
                irq_enable();
                if (unlikely(TIM2->SR & TIM_SR_CC2IF))
                    goto check_defer;
                irq_disable();
                break;
            }

            if (likely(diff <= -(int32_t)TIMER_MIN_TRY_TICKS))
                /* Timer is far enough in the future — schedule it */
                goto done;

            /* Timer is close — spin-wait */
            irq_enable();
            if (unlikely(TIM2->SR & TIM_SR_CC2IF))
                goto check_defer;
            irq_disable();
            continue;

        check_defer:
            /* Too many repeat timers — defer to main loop */
            irq_disable();
            uint32_t now = timer_get();
            if ((int32_t)(next - now) < (int32_t)(-timer_from_us(1000)))
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
    /* Clear CC1 interrupt flag */
    TIM2->SR = ~TIM_SR_CC1IF;
}

/* ---- Initialization ---------------------------------------------------- */

void
stm32_timer_init(void)
{
    static int initialized = 0;
    if (initialized)
        return;
    initialized = 1;

    irqstatus_t flag = irq_save();

    /* Enable TIM2 peripheral clock */
    enable_pclock((uint32_t)TIM2);

    /* TIM2 configuration:
     * - Up-counting mode (DIR=0)
     * - No prescaler (PSC=0) → timer runs at FREQ_PERIPH (132MHz)
     * - Auto-reload = maximum (32-bit counter, ARR=0xFFFFFFFF)
     * - Enable capture/compare interrupt on CC1
     */
    TIM2->CR1 = 0;             /* Up-counting, no prescaler division */
    TIM2->PSC = 0;             /* No prescaler */
    TIM2->ARR = 0xFFFFFFFF;    /* Max 32-bit auto-reload */
    TIM2->CNT = 0;             /* Reset counter */

    /* Enable CC1 interrupt (for timer scheduling) */
    TIM2->DIER = TIM_DIER_CC1IE;

    /* Set initial compare value so we get an interrupt soon */
    timer_kick();

    /* Set initial repeat timer value */
    timer_repeat_set(timer_get() + 500);

    /* Configure NVIC for TIM2 interrupt at highest priority */
    NVIC_SetPriority(TIM2_IRQn, 0);
    NVIC_EnableIRQ(TIM2_IRQn);

    /* Start the timer */
    TIM2->CR1 |= TIM_CR1_CEN;

    irq_restore(flag);
}
