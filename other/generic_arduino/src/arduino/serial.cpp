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
#include "../generic/serial_irq.h"

// Ensure C linkage for functions called from C code
#ifdef __cplusplus
extern "C" {
#endif

// ---- Serial selection -----------------------------------------------------
//
// Two serial types are supported, controlled by CONFIG_MCU_SERIAL_TYPE:
//   0 = Hardware UART (uses Arduino HardwareSerial, robust and fast)
//   1 = Software Serial (bit-banged on arbitrary GPIO pins via
//       Arduino SoftwareSerial library; slower and less reliable)
//
// Hardware UART port is selected by CONFIG_MCU_SERIAL_HW_PORT:
//   0 = Serial, 1 = Serial1, 2 = Serial2, 3 = Serial3
//
// Software Serial pins are set by:
//   CONFIG_MCU_SERIAL_SW_RX  (receive from host → Arduino pin)
//   CONFIG_MCU_SERIAL_SW_TX  (transmit to host → Arduino pin)

#if CONFIG_MCU_SERIAL_TYPE == 0
  // ── Hardware UART ──────────────────────────────────────────────────────
  #include <HardwareSerial.h>

  #if CONFIG_MCU_SERIAL_HW_PORT == 0
    #define KALICO_SERIAL   Serial
  #elif CONFIG_MCU_SERIAL_HW_PORT == 1
    // Guard: some boards (Uno/Nano) have no Serial1
    #if !defined(HAVE_HWSERIAL1) && !defined(USBCON) && !defined(SERIAL_PORT_HARDWARE1)
      // Assume Arduino Uno-class board — Serial1 not available
      #define KALICO_SERIAL   Serial
      #pragma message "Board has no Serial1; falling back to Serial"
    #else
      #define KALICO_SERIAL   Serial1
    #endif
  #elif CONFIG_MCU_SERIAL_HW_PORT == 2
    #define KALICO_SERIAL   Serial2
  #elif CONFIG_MCU_SERIAL_HW_PORT == 3
    #define KALICO_SERIAL   Serial3
  #else
    #define KALICO_SERIAL   Serial1
  #endif

  #define KALICO_SERIAL_IS_SOFTWARE    0

#elif CONFIG_MCU_SERIAL_TYPE == 1
  // ── Software Serial ────────────────────────────────────────────────────
  #include <SoftwareSerial.h>

  // SoftwareSerial instance (pins: RX=receive from host, TX=transmit to host)
  static SoftwareSerial swSerial(
      CONFIG_MCU_SERIAL_SW_RX,
      CONFIG_MCU_SERIAL_SW_TX
  );

  #define KALICO_SERIAL       swSerial
  #define KALICO_SERIAL_IS_SOFTWARE    1

#else
  #error "CONFIG_MCU_SERIAL_TYPE must be 0 (hardware) or 1 (software)"
#endif

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
    // Flush all buffered bytes via the serial_get_tx_byte() interface
    uint8_t data;
    while (serial_get_tx_byte(&data) == 0) {
        KALICO_SERIAL.write(data);
    }
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
#if CONFIG_MCU_SERIAL_TYPE == 0
    // Hardware UART: report the port name for the host config
    DECL_CONSTANT_STR("RESERVE_PINS_serial", "arduino_uart");
    #if CONFIG_MCU_SERIAL_HW_PORT == 0
      DECL_CONSTANT_STR("MCU_SERIAL_PORT", "Serial");
    #elif CONFIG_MCU_SERIAL_HW_PORT == 1
      DECL_CONSTANT_STR("MCU_SERIAL_PORT", "Serial1");
    #elif CONFIG_MCU_SERIAL_HW_PORT == 2
      DECL_CONSTANT_STR("MCU_SERIAL_PORT", "Serial2");
    #elif CONFIG_MCU_SERIAL_HW_PORT == 3
      DECL_CONSTANT_STR("MCU_SERIAL_PORT", "Serial3");
    #endif
#else
    DECL_CONSTANT_STR("RESERVE_PINS_serial", "arduino_swserial");
    DECL_CONSTANT("MCU_SERIAL_SW_RX", CONFIG_MCU_SERIAL_SW_RX);
    DECL_CONSTANT("MCU_SERIAL_SW_TX", CONFIG_MCU_SERIAL_SW_TX);
#endif
}

#ifdef __cplusplus
}
#endif
