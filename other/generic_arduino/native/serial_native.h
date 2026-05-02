// native/serial_native.h — native TCP serial declarations
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __NATIVE_SERIAL_H
#define __NATIVE_SERIAL_H

#include <stdint.h>

// Initialize TCP serial server. Returns port number (>0) on success, -1 on error.
int native_serial_init(int port);

// Shut down serial server
void native_serial_shutdown(void);

// Poll for incoming TCP connections and data.
// Calls serial_rx_byte() (from generic/serial_irq.c) for each received byte.
void native_serial_poll_rx(void);

#endif // __NATIVE_SERIAL_H
