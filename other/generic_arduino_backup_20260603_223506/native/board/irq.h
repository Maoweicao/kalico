// Native board/irq.h — interrupt management stubs
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __NATIVE_IRQ_H
#define __NATIVE_IRQ_H

#include <stdint.h>

typedef unsigned long irqstatus_t;

void irq_disable(void);
void irq_enable(void);
irqstatus_t irq_save(void);
void irq_restore(irqstatus_t flag);
void irq_wait(void);
void irq_poll(void);

#endif // __NATIVE_IRQ_H
