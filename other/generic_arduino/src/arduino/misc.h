/**
 * arduino/misc.h - Board-level API declarations for Arduino
 *
 * Derived from src/generic/misc.h
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_MISC_H
#define __ARDUINO_MISC_H

#include <stdarg.h> // va_list
#include <stdint.h> // uint8_t

#ifdef __cplusplus
extern "C" {
#endif

struct command_encoder;
void console_sendf(const struct command_encoder *ce, va_list args);
void *console_receive_buffer(void);

uint32_t timer_from_us(uint32_t us);
uint8_t timer_is_before(uint32_t time1, uint32_t time2);
uint32_t timer_read_time(void);
void timer_kick(void);

void *dynmem_start(void);
void *dynmem_end(void);

uint16_t crc16_ccitt(uint8_t *buf, uint_fast8_t len);

void bootloader_request(void);

#ifdef __cplusplus
}
#endif

#endif // __ARDUINO_MISC_H
