/**
 * arduino/pgm.h - Program memory (PROGMEM) abstraction for Arduino AVR
 *
 * Matches the original Klipper src/avr/pgm.h exactly.
 * On AVR: const data goes to flash (PROGMEM), READP uses pgm_read_*.
 * This saves precious SRAM on ATmega328P (only 2KB!).
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_PGM_H
#define __ARDUINO_PGM_H

#if defined(__AVR__)
  #include <avr/pgmspace.h>

  #define NEED_PROGMEM 1

  // READP reads from flash (PROGMEM) using the appropriate pgm_read_* function
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

#else
  // ARM, ESP32, etc: flash is memory-mapped, PROGMEM is unnecessary
  #define NEED_PROGMEM 0
  #define READP(VAR)    (VAR)
  #define PROGMEM
  #define memcpy_P(dest, src, n) memcpy((dest), (src), (n))

  #define pgm_read_byte(addr)   (*(const uint8_t*)(addr))
  #define pgm_read_word(addr)   (*(const uint16_t*)(addr))
  #define pgm_read_dword(addr)  (*(const uint32_t*)(addr))

#endif

#endif // __ARDUINO_PGM_H
