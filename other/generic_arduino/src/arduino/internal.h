/**
 * arduino/internal.h - Internal declarations for the Arduino Kalico port
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_INTERNAL_H
#define __ARDUINO_INTERNAL_H

#include <stdint.h>
#include <stdbool.h>

#ifdef __cplusplus
extern "C" {
#endif

// ---- Timer (timer.c) ------------------------------------------------------

/** Initialize the hardware timer used for Kalico scheduling. */
void arduino_timer_init(void);

/** Check if the timer ISR has fired and needs handling. */
bool arduino_timer_irq_pending(void);

/** Clear the timer IRQ pending flag. */
void arduino_timer_irq_clear(void);

/** Forward declaration from timer_irq.c */
uint32_t timer_dispatch_many(void);

// ---- Serial (serial.c) ----------------------------------------------------

/** Initialize the serial port. */
void arduino_serial_init(void);

/** Check if there is pending received serial data. */
bool arduino_serial_rx_pending(void);

/** Drain all pending received serial bytes into the Kalico rx buffer. */
void arduino_serial_drain_rx(void);

/** Enable the TX interrupt / start sending buffered data. */
void arduino_serial_enable_tx(void);

// ---- GPIO (gpio.c) --------------------------------------------------------

/** Forward-declare the GPIO types used by base Kalico. */
struct gpio_out {
    uint8_t pin;        // Arduino digital pin number
    uint8_t invert;     // Invert output (1 = active-low)
    uint8_t is_static;  // Static (non-PWM) output flag
    void*   pwm_ptr;    // Opaque pointer to PWM hardware (platform-specific)
};

struct gpio_in {
    uint8_t pin;        // Arduino digital pin number
    uint8_t invert;     // Invert input (1 = active-low)
};

struct gpio_adc {
    uint8_t pin;        // Arduino analog pin number (A0→0, A1→1, ...)
};

struct gpio_pwm {
    uint8_t pin;        // Arduino digital pin number
    uint8_t channel;    // PWM channel (platform-specific)
    void*   hw;         // Opaque pointer to PWM hardware
};

// GPIO function declarations that must be provided by gpio.c
struct gpio_out gpio_out_setup(uint8_t pin, uint8_t val);
void gpio_out_reset(struct gpio_out g, uint8_t val);
void gpio_out_toggle_noirq(struct gpio_out g);
void gpio_out_toggle(struct gpio_out g);
void gpio_out_write(struct gpio_out g, uint8_t val);
uint8_t gpio_out_valid(struct gpio_out g, uint8_t val);

struct gpio_in gpio_in_setup(uint8_t pin, int8_t pull_up);
void gpio_in_reset(struct gpio_in g, int8_t pull_up);
uint8_t gpio_in_read(struct gpio_in g);

struct gpio_adc gpio_adc_setup(uint8_t pin);
void gpio_adc_reset(struct gpio_adc g);
uint32_t gpio_adc_sample(struct gpio_adc g);
uint16_t gpio_adc_read(struct gpio_adc g);
void gpio_adc_cancel_sample(struct gpio_adc g);

struct gpio_pwm gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val);
void gpio_pwm_write(struct gpio_pwm g, uint8_t val);

// ---- CRC-16 CCITT (provided by generic/crc16_ccitt.c or local) ------------
uint16_t crc16_ccitt(uint8_t *buf, uint_fast8_t len);

#ifdef __cplusplus
}
#endif

#endif // __ARDUINO_INTERNAL_H
