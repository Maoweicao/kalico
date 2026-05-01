/**
 * arduino/gpio.c - GPIO implementation using Arduino digitalWrite/digitalRead
 *
 * Provides the gpio_out, gpio_in, gpio_adc, and gpio_pwm structs
 * and their operations using Arduino core functions.
 *
 * Derived from src/avr/gpio.c and src/linux/gpio.c
 *
 * Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "internal.h"
#include "../command.h"     // DECL_COMMAND, DECL_ENUMERATION_RANGE
#include "../sched.h"       // sched_shutdown
#include "../compiler.h"    // ARRAY_SIZE

// ---- Pin enumeration (for data dictionary) --------------------------------

DECL_ENUMERATION_RANGE("pin", "ar0", 0, 70);
DECL_ENUMERATION_RANGE("pin", "PD0", 0, 70);

#define GPIO_PIN_MAX 70

// ============================================================================
// GPIO Output
// ============================================================================

struct gpio_out
gpio_out_setup(uint8_t pin, uint8_t val)
{
    if (pin >= GPIO_PIN_MAX)
        shutdown("Invalid gpio_out pin");

    struct gpio_out g = {
        .pin = pin,
        .invert = 0,
        .is_static = 1,
        .pwm_ptr = NULL
    };
    gpio_out_reset(g, val);
    return g;
}

void
gpio_out_reset(struct gpio_out g, uint8_t val)
{
    if (g.is_static) {
        pinMode(g.pin, OUTPUT);
    }
    gpio_out_write(g, val);
}

void
gpio_out_toggle_noirq(struct gpio_out g)
{
    digitalWrite(g.pin, !digitalRead(g.pin));
}

void
gpio_out_toggle(struct gpio_out g)
{
    gpio_out_toggle_noirq(g);
}

void
gpio_out_write(struct gpio_out g, uint8_t val)
{
    digitalWrite(g.pin, val ^ g.invert);
}

uint8_t
gpio_out_valid(struct gpio_out g, uint8_t val)
{
    return 1;
}

// ============================================================================
// GPIO Input
// ============================================================================

struct gpio_in
gpio_in_setup(uint8_t pin, int8_t pull_up)
{
    if (pin >= GPIO_PIN_MAX)
        shutdown("Invalid gpio_in pin");

    struct gpio_in g = { .pin = pin, .invert = 0 };
    gpio_in_reset(g, pull_up);
    return g;
}

void
gpio_in_reset(struct gpio_in g, int8_t pull_up)
{
    if (pull_up > 0) {
        pinMode(g.pin, INPUT_PULLUP);
    } else {
        pinMode(g.pin, INPUT);
    }
}

uint8_t
gpio_in_read(struct gpio_in g)
{
    return digitalRead(g.pin) ^ g.invert;
}

// ============================================================================
// GPIO ADC
// ============================================================================

struct gpio_adc
gpio_adc_setup(uint8_t pin)
{
    // Convert Arduino analog pin number to physical pin
    struct gpio_adc g = { .pin = pin };
    return g;
}

void
gpio_adc_reset(struct gpio_adc g)
{
    pinMode(g.pin + A0, INPUT);
}

uint32_t
gpio_adc_sample(struct gpio_adc g)
{
    return analogRead(g.pin + A0);
}

uint16_t
gpio_adc_read(struct gpio_adc g)
{
    return (uint16_t)analogRead(g.pin + A0);
}

void
gpio_adc_cancel_sample(struct gpio_adc g)
{
    // No-op: Arduino analogRead is synchronous
}

// ============================================================================
// GPIO PWM
// ============================================================================

struct gpio_pwm
gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val)
{
    // Note: Arduino analogWrite uses 8-bit resolution (0-255)
    // and the frequency is fixed by the platform (490 Hz or 980 Hz typically)
    struct gpio_pwm g = {
        .pin = pin,
        .channel = 0,
        .hw = NULL
    };
    pinMode(pin, OUTPUT);
    gpio_pwm_write(g, val);
    return g;
}

void
gpio_pwm_write(struct gpio_pwm g, uint8_t val)
{
    analogWrite(g.pin, val);
}

// ============================================================================
// Dynamic memory region
// ============================================================================

// These define the heap region available to Kalico's allocator.
// On Arduino, we use the remaining RAM after globals/stack.

#if defined(__AVR__)
  #include <avr/io.h>
  extern unsigned int __heap_start;
  extern void *__brkval;

  void *
  dynmem_start(void)
  {
      return (void*)&__heap_start;
  }

  void *
  dynmem_end(void)
  {
      if ((int)__brkval == 0)
          return (void*)SP - CONFIG_AVR_STACK_SIZE;
      return (void*)__brkval;
  }
#elif defined(__arm__) || defined(__ARM_ARCH)
  extern char _end;
  extern char _sstack;

  void *
  dynmem_start(void)
  {
      return (void*)&_end;
  }

  void *
  dynmem_end(void)
  {
      return (void*)&_sstack - CONFIG_AVR_STACK_SIZE;
  }
#else
  // Generic fallback: use a static buffer
  #define DYNMEM_SIZE 4096
  static uint8_t dynmem_pool[DYNMEM_SIZE];

  void *
  dynmem_start(void)
  {
      return dynmem_pool;
  }

  void *
  dynmem_end(void)
  {
      return dynmem_pool + DYNMEM_SIZE;
  }
#endif

// ============================================================================
// Bootloader request (no-op on Arduino)
// ============================================================================

void
bootloader_request(void)
{
    // Platform-specific: can be implemented per board
    // Example for AVR: jump to bootloader section
    // For now, no-op
}
