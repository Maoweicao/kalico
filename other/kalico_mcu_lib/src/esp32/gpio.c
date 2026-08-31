/**
 * esp32/gpio.c - GPIO operations for ESP32
 *
 * Configuration paths (setup/reset) use Arduino pin functions.
 * The stepper/digital-out ISR hot path (toggle_noirq / write / in_read) uses
 * direct GPIO register writes with IRAM_ATTR so no flash cache stall delays
 * step pulses.
 * Pin numbering: Arduino convention; on the standard ESP32 variants the
 * Arduino pin number equals the GPIO number (identity mapping).
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "internal.h"
#include "irq.h"
#include "command.h"

/* IRAM-resident GPIO registers for IRQ-safe fast toggling */
#include "esp_attr.h"
#include "soc/gpio_reg.h"

/* ---- GPIO register helpers ------------------------------------------------
 * On ESP32 the Arduino "pin" number equals the GPIO number (identity
 * mapping for the standard variants), so g.pin can be used directly as a
 * GPIO bit index.  The *_W1TS / *_W1TC registers are single-1-write set /
 * clear so they are atomic and safe to poke from an ISR.
 * ------------------------------------------------------------------------- */

static inline void IRAM_ATTR
esp32_gpio_set(uint8_t gpio, uint8_t val)
{
    if (gpio >= 32) {
        volatile uint32_t *reg = val
            ? (volatile uint32_t *)GPIO_OUT1_W1TS_REG
            : (volatile uint32_t *)GPIO_OUT1_W1TC_REG;
        *reg = (1u << (gpio - 32));
    } else {
        volatile uint32_t *reg = val
            ? (volatile uint32_t *)GPIO_OUT_W1TS_REG
            : (volatile uint32_t *)GPIO_OUT_W1TC_REG;
        *reg = (1u << gpio);
    }
}

static inline uint8_t IRAM_ATTR
esp32_gpio_out_state(uint8_t gpio)
{
    if (gpio >= 32)
        return !!((*(volatile uint32_t *)GPIO_OUT1_REG) & (1u << (gpio - 32)));
    return !!((*(volatile uint32_t *)GPIO_OUT_REG) & (1u << gpio));
}

static inline uint8_t IRAM_ATTR
esp32_gpio_in(uint8_t gpio)
{
    if (gpio >= 32)
        return !!((*(volatile uint32_t *)GPIO_IN1_REG) & (1u << (gpio - 32)));
    return !!((*(volatile uint32_t *)GPIO_IN_REG) & (1u << gpio));
}

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

/* Fast IRQ-safe toggle/write paths - called from timer dispatch in ISR
 * context, so they must live in IRAM and touch hardware registers directly. */

void IRAM_ATTR
gpio_out_toggle_noirq(struct gpio_out g)
{
    esp32_gpio_set(g.pin, !esp32_gpio_out_state(g.pin));
}

void
gpio_out_toggle(struct gpio_out g)
{
    irqstatus_t flag = irq_save();
    gpio_out_toggle_noirq(g);
    irq_restore(flag);
}

void IRAM_ATTR
gpio_out_write(struct gpio_out g, uint8_t val)
{
    if (g.invert)
        val = !val;
    esp32_gpio_set(g.pin, val);
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

uint8_t IRAM_ATTR
gpio_in_read(struct gpio_in g)
{
    return esp32_gpio_in(g.pin) ^ g.invert;
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
