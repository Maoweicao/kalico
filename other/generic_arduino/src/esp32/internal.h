/**
 * esp32/internal.h - Internal declarations for ESP32 Kalico port
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ESP32_INTERNAL_H
#define __ESP32_INTERNAL_H

#include <stdint.h>
#include <stdbool.h>
#include "autoconf.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ---- GPIO structs (Arduino-style pin numbering) ------------------------- */

struct gpio_out {
    uint8_t pin;
    uint8_t invert;
    uint8_t is_static;
    void*   pwm_ptr;
};

struct gpio_in {
    uint8_t pin;
    uint8_t invert;
};

struct gpio_adc {
    uint8_t pin;
};

struct gpio_pwm {
    uint8_t pin;
    uint8_t channel;
    void*   hw;
};

/* ---- GPIO function declarations ----------------------------------------- */

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

/* ---- Timer (timer.c) ---------------------------------------------------- */

void arduino_timer_init(void);
bool arduino_timer_irq_pending(void);
void arduino_timer_irq_clear(void);
uint32_t timer_dispatch_many(void);
void timer_kick_next(uint32_t next_time);

/* ---- Serial (serial.cpp) ------------------------------------------------ */

void arduino_serial_init(void);
bool arduino_serial_rx_pending(void);
void arduino_serial_drain_rx(void);
void serial_enable_tx_irq(void);

/* ---- CRC-16 CCITT ------------------------------------------------------- */

uint16_t crc16_ccitt(uint8_t *buf, uint_fast8_t len);

#ifdef __cplusplus
}
#endif

#endif /* __ESP32_INTERNAL_H */
