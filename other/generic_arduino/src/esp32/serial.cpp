/**
 * esp32/serial.cpp - Serial implementation for ESP32
 *
 * Uses Arduino HardwareSerial (Serial0 = UART0).
 * Provides board-specific serial functions for generic/serial_irq.c.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"

#if !CONFIG_WANT_WIFI

#include "misc.h"
#include "serial.h"
#include "internal.h"
#include "../command.h"
#include "../sched.h"
#include "../generic/serial_irq.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ESP32 Serial0: GPIO1=TX, GPIO3=RX (default UART0) */
#define KALICO_SERIAL   Serial

/* ---- TX interrupt callback ---------------------------------------------- */

void
serial_enable_tx_irq(void)
{
    uint8_t data;
    while (serial_get_tx_byte(&data) == 0) {
        KALICO_SERIAL.write(data);
    }
    KALICO_SERIAL.flush();
}

/* ---- Arduino poll wrapper ----------------------------------------------- */

void
arduino_serial_drain_rx(void)
{
    while (KALICO_SERIAL.available() > 0) {
        uint8_t c = KALICO_SERIAL.read();
        serial_rx_byte(c);
    }
}

bool
arduino_serial_rx_pending(void)
{
    return KALICO_SERIAL.available() > 0;
}

/* ---- Initialization ----------------------------------------------------- */

void
arduino_serial_init(void)
{
    static bool initialized = false;
    if (initialized)
        return;
    initialized = true;

    KALICO_SERIAL.begin(CONFIG_SERIAL_BAUD);

    DECL_CONSTANT("SERIAL_BAUD", CONFIG_SERIAL_BAUD);
    DECL_CONSTANT_STR("RESERVE_PINS_serial", "esp32_uart");
    DECL_CONSTANT_STR("MCU_SERIAL_PORT", "Serial");
}

#ifdef __cplusplus
}
#endif

#endif /* !CONFIG_WANT_WIFI */
