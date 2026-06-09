/**
 * esp32/irq.h - Interrupt management for ESP32
 *
 * ESP32 uses Arduino noInterrupts()/interrupts() for global interrupt control.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ESP32_IRQ_H
#define __ESP32_IRQ_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef unsigned long irqstatus_t;

void irq_disable(void);
void irq_enable(void);
irqstatus_t irq_save(void);
void irq_restore(irqstatus_t flag);
void irq_wait(void);
void irq_poll(void);

#ifdef __cplusplus
}
#endif

#endif /* __ESP32_IRQ_H */
