/**
 * esp32/pgm.h - Program memory abstraction for ESP32
 *
 * ESP32 has unified address space, no PROGMEM needed.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ESP32_PGM_H
#define __ESP32_PGM_H

#include <string.h>

#define NEED_PROGMEM 0
#define READP(VAR)    (VAR)
#define PROGMEM
#define memcpy_P(dest, src, n) memcpy((dest), (src), (n))

#define pgm_read_byte(addr)   (*(const uint8_t*)(addr))
#define pgm_read_word(addr)   (*(const uint16_t*)(addr))
#define pgm_read_dword(addr)  (*(const uint32_t*)(addr))

#endif /* __ESP32_PGM_H */
