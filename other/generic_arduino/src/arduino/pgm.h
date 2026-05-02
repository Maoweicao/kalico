/**
 * arduino/pgm.h - Program memory (PROGMEM) abstraction for Arduino
 *
 * On AVR, this provides READP() for reading from flash.
 * On ARM/ESP32, flash is memory-mapped so READP is a no-op.
 *
 * Derived from src/avr/pgm.h
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_PGM_H
#define __ARDUINO_PGM_H

#if defined(__AVR__)
  // AVR uses PROGMEM to store constant data in flash
  #include <avr/pgmspace.h>

  #define NEED_PROGMEM 1

  #define READP(VAR) ({                                                   \
      _Pragma("GCC diagnostic push");                                     \
      _Pragma("GCC diagnostic ignored \"-Wint-to-pointer-cast\"");        \
      typeof(VAR) __val =                                                 \
          __builtin_choose_expr(sizeof(VAR) == 1,                         \
              (typeof(VAR))pgm_read_byte(&(VAR)),                         \
          __builtin_choose_expr(sizeof(VAR) == 2,                         \
              (typeof(VAR))pgm_read_word(&(VAR)),                         \
          __builtin_choose_expr(sizeof(VAR) == 4,                         \
              (typeof(VAR))pgm_read_dword(&(VAR)),                        \
          __force_link_error__unknown_type)));                            \
      _Pragma("GCC diagnostic pop");                                      \
      __val;                                                              \
      })

  extern void __force_link_error__unknown_type(void);

  #ifndef PROGMEM
  #define PROGMEM __attribute__((__progmem__))
  #endif
  #define memcpy_P(dest, src, n) memcpy_P((dest), (src), (n))

#else
  // ARM, ESP32, etc: flash is memory-mapped, PROGMEM is unnecessary
  #define NEED_PROGMEM 0
  #define READP(VAR)    (VAR)
  #define PROGMEM
  #define memcpy_P(dest, src, n) memcpy((dest), (src), (n))

  // Provide a dummy pgm_read_* for compatibility
  #define pgm_read_byte(addr)   (*(const uint8_t*)(addr))
  #define pgm_read_word(addr)   (*(const uint16_t*)(addr))
  #define pgm_read_dword(addr)  (*(const uint32_t*)(addr))

#endif

#endif // __ARDUINO_PGM_H
