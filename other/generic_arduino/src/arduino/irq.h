/**
 * arduino/irq.h - Interrupt management for Arduino
 *
 * Derived from src/generic/irq.h
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_IRQ_H
#define __ARDUINO_IRQ_H

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

#endif // __ARDUINO_IRQ_H
