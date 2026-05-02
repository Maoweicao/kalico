// Native board/io.h — memory-mapped I/O stubs
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __NATIVE_IO_H
#define __NATIVE_IO_H

#include <stdint.h>

// Simple volatile read/write — translates to regular memory access
static inline void writeb(void *addr, uint8_t val) {
    *(volatile uint8_t *)addr = val;
}
static inline uint8_t readb(const void *addr) {
    return *(const volatile uint8_t *)addr;
}

#endif // __NATIVE_IO_H
