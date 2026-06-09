// native/misc_native.c — board-level glue functions for native build
//
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdint.h>
#include <stdlib.h>
#include "board/misc.h"

// console_receive_buffer — used by command.c for pointer<->offset conversion
// We provide a simple static buffer.
static uint8_t _receive_buf[4096];

void *console_receive_buffer(void) {
    return _receive_buf;
}

// timer_kick — no-op on native (timer is polled in irq_poll)
void timer_kick(void) {
}

// dynmem_start — provides a memory region for the dynamic allocator
// (generic/alloc.c). On native we just use malloc.
static uint8_t _dynmem[65536];

void *dynmem_start(void) {
    return _dynmem;
}

void *dynmem_end(void) {
    return _dynmem + sizeof(_dynmem);
}

// console_shutdown — called when MCU shuts down
#include <stdio.h>
#include <stdlib.h>

void console_shutdown(void) {
    fprintf(stderr, "[native] MCU shutdown\n");
    exit(1);
}
