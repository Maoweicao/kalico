/**
 * arduino/serial.c - Serial (UART) implementation for Arduino
 *
 * Provides ONLY the board-specific serial functions.
 * The generic serial_irq.c provides the main serial logic
 * (serial_rx_byte, serial_get_tx_byte, console_sendf, console_task).
 *
 * Derived from src/avr/serial.c
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "misc.h"
#include "serial.h"
#include "internal.h"
#include "../command.h"     // DECL_CONSTANT_STR, DECL_INIT
#include "../sched.h"

// ---- HardwareSerial selection --------------------------------------------
// Default: Serial1.  Adjust for your board:
//   Uno/Nano:  Serial  (pins 0/1, conflicts with USB)
//   Mega:      Serial1 (pins 18/19), Serial2 (16/17), Serial3 (14/15)
//   Due:       Serial1 (pins 19/18)
//   Teensy:    Serial1
#define KALICO_SERIAL   Serial1

// ---- TX interrupt callback ------------------------------------------------
// Called by generic/serial_irq.c when it has bytes queued for transmission.
// We flush them to the hardware.

/**
 * Enable TX — called by generic/serial_irq.c when data is ready in the TX buffer.
 *
 * In interrupt-driven UART setups, this would enable the UDRE interrupt.
 * In Arduino's polled environment, we flush the buffer immediately.
 */
void
serial_enable_tx_irq(void)
{
    // The serial_irq.c module manages transmit_buf/transmit_pos/transmit_max.
    // We need access to them to flush.
    extern uint8_t transmit_buf[];
    extern uint8_t transmit_pos;
    extern uint8_t transmit_max;

    while (transmit_pos < transmit_max) {
        KALICO_SERIAL.write(transmit_buf[transmit_pos++]);
    }
    transmit_pos = 0;
    transmit_max = 0;
    KALICO_SERIAL.flush();
}

// ---- Arduino poll wrapper -------------------------------------------------
// Called from irq_poll() in our irq.c → feeds received bytes into the
// generic serial_irq.c receive buffer.

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

// ---- Initialization -------------------------------------------------------

void
arduino_serial_init(void)
{
    KALICO_SERIAL.begin(CONFIG_SERIAL_BAUD);

    DECL_CONSTANT("SERIAL_BAUD", CONFIG_SERIAL_BAUD);
    DECL_CONSTANT_STR("RESERVE_PINS_serial", "arduino_serial1");
}
