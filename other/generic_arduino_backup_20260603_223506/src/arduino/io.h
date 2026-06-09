/**
 * arduino/io.h - Memory-mapped I/O helpers for Arduino
 *
 * Derived from src/generic/io.h
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_IO_H
#define __ARDUINO_IO_H

#include <stdint.h>
#include "compiler.h"

// Memory barrier for volatile access ordering
#ifndef barrier
  #define barrier() __asm__ __volatile__("": : :"memory")
#endif

static inline void writel(void *addr, uint32_t val) {
    barrier();
    *(volatile uint32_t *)addr = val;
}
static inline void writew(void *addr, uint16_t val) {
    barrier();
    *(volatile uint16_t *)addr = val;
}
static inline void writeb(void *addr, uint8_t val) {
    barrier();
    *(volatile uint8_t *)addr = val;
}
static inline uint32_t readl(const void *addr) {
    uint32_t val = *(volatile const uint32_t *)addr;
    barrier();
    return val;
}
static inline uint16_t readw(const void *addr) {
    uint16_t val = *(volatile const uint16_t *)addr;
    barrier();
    return val;
}
static inline uint8_t readb(const void *addr) {
    uint8_t val = *(volatile const uint8_t *)addr;
    barrier();
    return val;
}

#endif // __ARDUINO_IO_H
