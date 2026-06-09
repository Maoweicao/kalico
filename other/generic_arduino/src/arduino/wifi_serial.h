/**
 * arduino/wifi_serial.h - WiFi TCP/UDP serial transport for ESP32
 *
 * Replaces the standard UART serial transport with WiFi-based TCP or UDP
 * when CONFIG_WANT_WIFI=1.  The host (klippy) connects to this MCU over
 * the network, and the Kalico binary protocol runs transparently over
 * the socket instead of a serial port.
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_WIFI_SERIAL_H
#define __ARDUINO_WIFI_SERIAL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

void wifi_serial_init(void);
void wifi_serial_poll_rx(void);
bool wifi_serial_rx_pending(void);
bool wifi_serial_is_connected(void);

#ifdef __cplusplus
}
#endif

#endif // __ARDUINO_WIFI_SERIAL_H
