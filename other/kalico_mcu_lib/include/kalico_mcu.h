/**
 * kalico_mcu.h - Public API for the kalico_mcu_lib library.
 *
 * Usage (Arduino / ESP32-S3):
 *
 *   #include <Arduino.h>
 *   #include <kalico_mcu.h>
 *
 *   void setup()
 *   {
 *       klipper_init();
 *   }
 *
 *   void loop()
 *   {
 *       klipper_loop();
 *   }
 *
 * After flashing, attach a Klipper/Kalico host to the UART used by the board
 * (on ESP32-S3 default UART0: TX=GPIO43, RX=GPIO44, 250000 baud) and run
 * firmware flashing / identify as you would for an official MCU.  This is a
 * bare UART transport with no WiFi - suitable for handshake / identify /
 * command loopback, and (with stepper outputs wired) real stepping.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */
#ifndef __KALICO_MCU_H
#define __KALICO_MCU_H

#ifdef __cplusplus
extern "C" {
#endif

// Initialize the MCU core (serial, timer, command processing).  Call exactly
// once from setup().  Safe to call before the main loop starts running.
void klipper_init(void);

// Run a single non-blocking pass of the scheduler.  Call repeatedly from
// loop().  Returns immediately when idle so the surrounding loop stays
// responsive (LEDs, WiFi, etc).  Shutdowns requested from timer ISR context
// are serviced here, in task context.
void klipper_loop(void);

#ifdef __cplusplus
} // extern "C"
#endif

#endif // __KALICO_MCU_H