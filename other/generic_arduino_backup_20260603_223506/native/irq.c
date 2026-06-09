// native/irq.c — interrupt management stubs for host-native build
//
// SPDX-License-Identifier: GPL-3.0-or-later

#include "board/irq.h"

// On host, interrupts are simulated — we just toggle a flag
static int irq_disabled_flag = 0;

void irq_disable(void) {
    irq_disabled_flag = 1;
}

void irq_enable(void) {
    irq_disabled_flag = 0;
}

irqstatus_t irq_save(void) {
    irqstatus_t old = irq_disabled_flag;
    irq_disabled_flag = 1;
    return old;
}

void irq_restore(irqstatus_t flag) {
    irq_disabled_flag = (int)flag;
}

void irq_wait(void) {
    // No-op on host
}

void irq_poll(void) {
    // Poll serial for incoming data (implemented in serial_native.c)
    extern void native_serial_poll_rx(void);
    native_serial_poll_rx();
}
