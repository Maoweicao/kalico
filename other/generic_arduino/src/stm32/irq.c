/**
 * stm32/irq.c - Interrupt management for STM32H723
 *
 * Uses CMSIS __get_PRIMASK / __set_PRIMASK for interrupt control.
 * ISR-native timer dispatch: timer events are handled entirely inside
 * the TIM2 ISR, so irq_poll() only drains serial data.
 *
 * Derived from Klipper src/generic/irq.c and the Arduino irq.c
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"
#include "internal.h"
#include "irq.h"

/* ---- irq_disable / irq_enable ------------------------------------------ */

void
irq_disable(void)
{
    __disable_irq();
}

void
irq_enable(void)
{
    __enable_irq();
}

/* ---- irq_save / irq_restore -------------------------------------------- */
/* Save the current interrupt state and disable interrupts. */
irqstatus_t
irq_save(void)
{
    irqstatus_t flag = __get_PRIMASK();
    __disable_irq();
    return flag;
}

/* Restore a previously saved interrupt state. */
void
irq_restore(irqstatus_t flag)
{
    __set_PRIMASK(flag);
}

/* ---- irq_wait ---------------------------------------------------------- */
/* Sleep until next interrupt.  On STM32 with ISR-native timer dispatch,
 * timers are handled entirely inside the TIM2 ISR.  irq_wait() only
 * needs to briefly allow interrupts and drain any pending serial data. */

void
irq_wait(void)
{
    __enable_irq();
    __asm__ __volatile__("nop" ::: "memory");
    __disable_irq();
}

/* ---- irq_poll ---------------------------------------------------------- */
/* Called from the main loop to handle pending work.
 * With ISR-native mode, timer dispatch happens in the TIM2 ISR.
 * irq_poll() does nothing here — serial RX happens in USART3 ISR. */

void
irq_poll(void)
{
    /* All work is done in ISRs:
     * - TIM2 ISR handles timer dispatch (stepper scheduling)
     * - USART3 ISR handles serial RX/TX
     */
}
