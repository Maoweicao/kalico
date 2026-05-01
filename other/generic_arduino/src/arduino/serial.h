/**
 * arduino/serial.h - Serial port declarations for Arduino
 *
 * Declares the serial functions that the generic serial_irq.c layer uses.
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_SERIAL_H
#define __ARDUINO_SERIAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void serial_enable_tx_irq(void);

#ifdef __cplusplus
}
#endif

#endif // __ARDUINO_SERIAL_H
