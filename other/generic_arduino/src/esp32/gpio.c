/**
 * esp32/gpio.c - GPIO operations for ESP32
 *
 * Uses Arduino digital pin functions for simplicity.
 * Pin numbering follows Arduino convention (GPIO0-GPIO48).
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "internal.h"
#include "irq.h"
#include "command.h"

/* ---- GPIO Output -------------------------------------------------------- */

struct gpio_out
gpio_out_setup(uint8_t pin, uint8_t val)
{
    struct gpio_out g;
    g.pin = pin;
    g.invert = 0;
    g.is_static = 1;
    g.pwm_ptr = NULL;
    pinMode(pin, OUTPUT);
    digitalWrite(pin, val);
    return g;
}

void
gpio_out_reset(struct gpio_out g, uint8_t val)
{
    pinMode(g.pin, OUTPUT);
    digitalWrite(g.pin, val);
}

void
gpio_out_toggle_noirq(struct gpio_out g)
{
    digitalWrite(g.pin, !digitalRead(g.pin));
}

void
gpio_out_toggle(struct gpio_out g)
{
    irqstatus_t flag = irq_save();
    gpio_out_toggle_noirq(g);
    irq_restore(flag);
}

void
gpio_out_write(struct gpio_out g, uint8_t val)
{
    digitalWrite(g.pin, val);
}

uint8_t
gpio_out_valid(struct gpio_out g, uint8_t val)
{
    return 1;
}

/* ---- GPIO Input --------------------------------------------------------- */

struct gpio_in
gpio_in_setup(uint8_t pin, int8_t pull_up)
{
    struct gpio_in g;
    g.pin = pin;
    g.invert = 0;
    if (pull_up > 0)
        pinMode(pin, INPUT_PULLUP);
    else if (pull_up < 0)
        pinMode(pin, INPUT_PULLDOWN);
    else
        pinMode(pin, INPUT);
    return g;
}

void
gpio_in_reset(struct gpio_in g, int8_t pull_up)
{
    if (pull_up > 0)
        pinMode(g.pin, INPUT_PULLUP);
    else if (pull_up < 0)
        pinMode(g.pin, INPUT_PULLDOWN);
    else
        pinMode(g.pin, INPUT);
}

uint8_t
gpio_in_read(struct gpio_in g)
{
    return !!digitalRead(g.pin);
}

/* ---- GPIO ADC (stubs for now) ------------------------------------------- */

struct gpio_adc
gpio_adc_setup(uint8_t pin)
{
    struct gpio_adc g;
    g.pin = pin;
    return g;
}

void
gpio_adc_reset(struct gpio_adc g)
{
}

uint32_t
gpio_adc_sample(struct gpio_adc g)
{
    return 0;
}

uint16_t
gpio_adc_read(struct gpio_adc g)
{
    return 0;
}

void
gpio_adc_cancel_sample(struct gpio_adc g)
{
}

/* ---- GPIO PWM (stubs for now) ------------------------------------------- */

struct gpio_pwm
gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val)
{
    struct gpio_pwm g;
    g.pin = pin;
    g.channel = 0;
    g.hw = NULL;
    return g;
}

void
gpio_pwm_write(struct gpio_pwm g, uint8_t val)
{
}

/* ---- Bootloader request ------------------------------------------------- */

void
bootloader_request(void)
{
    /* ESP32: could implement as restart to bootloader */
}
