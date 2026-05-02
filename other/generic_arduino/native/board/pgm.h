// Native board/pgm.h — PROGMEM stubs (host has no flash memory)
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __NATIVE_PGM_H
#define __NATIVE_PGM_H

// On host, PROGMEM is just regular RAM — no special access needed
#define PROGMEM
#define PSTR(s) (s)
#define READP(VAR) (VAR)
#define strcmp_P strcmp

#endif // __NATIVE_PGM_H
