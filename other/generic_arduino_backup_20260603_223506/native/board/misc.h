// Native board/misc.h — timer, console, and utility declarations
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __NATIVE_MISC_H
#define __NATIVE_MISC_H

#include <stdarg.h>
#include <stdint.h>

struct command_encoder;

// Timer API (implemented in timer_native.c)
uint32_t timer_from_us(uint32_t us);
uint8_t timer_is_before(uint32_t time1, uint32_t time2);
uint32_t timer_read_time(void);
void timer_kick(void);

// Console I/O (implemented in misc_native.c)
void console_sendf(const struct command_encoder *ce, va_list args);
void *console_receive_buffer(void);
void console_shutdown(void);

// Dynamic memory (implemented in misc_native.c)
void *dynmem_start(void);
void *dynmem_end(void);

// CRC-16 CCITT (implemented in src/generic/crc16_ccitt.c)
uint16_t crc16_ccitt(const uint8_t *buf, uint_fast8_t len);

#endif // __NATIVE_MISC_H
