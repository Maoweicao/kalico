/**
 * esp32/irq.c - Interrupt management for ESP32 (ISR-native mode)
 *
 * Uses ESP-IDF portSET_INTERRUPT_MASK_FROM_ISR for proper save/restore.
 * In ISR-native mode, timer dispatch happens in the gptimer ISR.
 * irq_wait() and irq_poll() only handle serial data.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "irq.h"
#include "internal.h"

/* ESP-IDF FreeRTOS critical section */
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

/* ---- irq_disable / irq_enable ------------------------------------------ */

void
irq_disable(void)
{
    portDISABLE_INTERRUPTS();
}

void
irq_enable(void)
{
    portENABLE_INTERRUPTS();
}

irqstatus_t
irq_save(void)
{
    /* portSET_INTERRUPT_MASK_FROM_ISR saves current interrupt level
     * and disables interrupts up to configMAX_SYSCALL_INTERRUPT_PRIORITY.
     * Safe to call from both ISR and task context on ESP32. */
    return (irqstatus_t)portSET_INTERRUPT_MASK_FROM_ISR();
}

void
irq_restore(irqstatus_t flag)
{
    portCLEAR_INTERRUPT_MASK_FROM_ISR((UBaseType_t)flag);
}

/* ---- irq_wait ---- */
/* ISR-native mode: timers dispatched in timer ISR.
 * Only drain serial data here. */

void
irq_wait(void)
{
    irq_enable();
    if (arduino_serial_rx_pending())
        arduino_serial_drain_rx();
    else
        __asm__ __volatile__("nop" ::: "memory");
    irq_disable();
}

/* ---- irq_poll ---- */
/* Called from main loop. ISR-native: only handle serial. */

void
irq_poll(void)
{
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
}
