// native/timer_native.c — host-native timer implementation
//
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdint.h>
#include <time.h>
#include "autoconf.h"

// Convert microseconds to native clock ticks
uint32_t timer_from_us(uint32_t us) {
    return us * (CONFIG_CLOCK_FREQ / 1000000UL);
}

// Compare two timer values with 32-bit wraparound safety
uint8_t timer_is_before(uint32_t time1, uint32_t time2) {
    return (int32_t)(time1 - time2) < 0;
}

// Read current time in clock ticks
uint32_t timer_read_time(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    uint64_t us = (uint64_t)ts.tv_sec * 1000000ULL + ts.tv_nsec / 1000ULL;
    return timer_from_us((uint32_t)(us & 0xFFFFFFFFULL));
}
