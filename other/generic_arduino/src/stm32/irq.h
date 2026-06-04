/**
 * stm32/irq.h - Interrupt management for STM32H723
 *
 * Uses CMSIS __get_PRIMASK / __set_PRIMASK.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __STM32_IRQ_H
#define __STM32_IRQ_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef uint32_t irqstatus_t;

void irq_disable(void);
void irq_enable(void);
irqstatus_t irq_save(void);
void irq_restore(irqstatus_t flag);
void irq_wait(void);
void irq_poll(void);

#ifdef __cplusplus
}
#endif

#endif /* __STM32_IRQ_H */
