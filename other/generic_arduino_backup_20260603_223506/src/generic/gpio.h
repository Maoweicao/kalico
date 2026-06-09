/**
 * generic/gpio.h - GPIO API declarations for generic (Arduino) implementation
 *
 * These struct definitions MUST match arduino/internal.h exactly.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __GENERIC_GPIO_H
#define __GENERIC_GPIO_H

#include <stdint.h>

struct gpio_out {
    uint8_t pin;
    uint8_t invert;
    uint8_t is_static;
    void*   pwm_ptr;
};
struct gpio_out gpio_out_setup(uint8_t pin, uint8_t val);
void gpio_out_reset(struct gpio_out g, uint8_t val);
void gpio_out_toggle_noirq(struct gpio_out g);
void gpio_out_toggle(struct gpio_out g);
void gpio_out_write(struct gpio_out g, uint8_t val);
uint8_t gpio_out_valid(struct gpio_out g, uint8_t val);

struct gpio_in {
    uint8_t pin;
    uint8_t invert;
};
struct gpio_in gpio_in_setup(uint8_t pin, int8_t pull_up);
void gpio_in_reset(struct gpio_in g, int8_t pull_up);
uint8_t gpio_in_read(struct gpio_in g);

struct gpio_adc {
    uint8_t pin;
};
struct gpio_adc gpio_adc_setup(uint8_t pin);
void gpio_adc_reset(struct gpio_adc g);
uint32_t gpio_adc_sample(struct gpio_adc g);
uint16_t gpio_adc_read(struct gpio_adc g);
void gpio_adc_cancel_sample(struct gpio_adc g);

struct gpio_pwm {
    uint8_t pin;
    uint8_t channel;
    void*   hw;
};
struct gpio_pwm gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val);
void gpio_pwm_write(struct gpio_pwm g, uint8_t val);

#endif // __GENERIC_GPIO_H
