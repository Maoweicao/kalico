/**
 * stm32/internal.h - Internal declarations for STM32H723 Kalico port
 *
 * Derived from Klipper src/stm32/internal.h
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __STM32_INTERNAL_H
#define __STM32_INTERNAL_H

#include <stdint.h>
#include "autoconf.h"

/* Include STM32H7 device headers (provided by stm32cube framework) */
#include "stm32h7xx.h"

#ifdef __cplusplus
extern "C" {
#endif

/* ---- GPIO encoding (matches Klipper STM32 convention) ------------------ */
/* Pin encoding: GPIO('A', 0) = 0, GPIO('B', 0) = 16, etc. */
#define GPIO(PORT, NUM)     (((PORT) - 'A') * 16 + (NUM))
#define GPIO2PORT(PIN)      ((PIN) / 16)
#define GPIO2BIT(PIN)       (1 << ((PIN) % 16))

/* ---- GPIO direction constants ------------------------------------------ */
#define GPIO_INPUT      0
#define GPIO_OUTPUT     1
#define GPIO_OPEN_DRAIN 0x100
#define GPIO_HIGH_SPEED 0x200
#define GPIO_FUNCTION(fn) (2 | ((fn) << 4))
#define GPIO_ANALOG     3

/* ---- GPIO port register lookup ----------------------------------------- */
extern GPIO_TypeDef * const digital_regs[];

/* ---- GPIO peripheral configuration ------------------------------------- */
void gpio_peripheral(uint32_t gpio, uint32_t mode, int pullup);

/* ---- Clock line -------------------------------------------------------- */
struct cline {
    volatile uint32_t *en, *rst;
    uint32_t bit;
};

struct cline lookup_clock_line(uint32_t periph_base);
uint32_t get_pclock_frequency(uint32_t periph_base);
void gpio_clock_enable(GPIO_TypeDef *regs);
void enable_pclock(uint32_t periph_base);

/* ---- Clock setup ------------------------------------------------------- */
void stm32_clock_setup(void);

/* ---- GPIO structs (port + bitmask pattern) ----------------------------- */
struct gpio_out {
    GPIO_TypeDef *regs;
    uint32_t bit;
};

struct gpio_in {
    GPIO_TypeDef *regs;
    uint32_t bit;
};

struct gpio_adc {
    uint32_t chan;       /* ADC channel number */
    ADC_TypeDef *adc;   /* ADC peripheral */
};

struct gpio_pwm {
    TIM_TypeDef *tim;
    uint32_t chan;       /* TIM channel (1-4) */
};

/* ---- GPIO function declarations ---------------------------------------- */
struct gpio_out gpio_out_setup(uint32_t pin, uint32_t val);
void gpio_out_reset(struct gpio_out g, uint32_t val);
void gpio_out_toggle_noirq(struct gpio_out g);
void gpio_out_toggle(struct gpio_out g);
void gpio_out_write(struct gpio_out g, uint32_t val);
uint8_t gpio_out_valid(struct gpio_out g, uint32_t val);

struct gpio_in gpio_in_setup(uint32_t pin, int32_t pull_up);
void gpio_in_reset(struct gpio_in g, int32_t pull_up);
uint8_t gpio_in_read(struct gpio_in g);

struct gpio_adc gpio_adc_setup(uint32_t pin);
void gpio_adc_reset(struct gpio_adc g);
uint32_t gpio_adc_sample(struct gpio_adc g);
uint16_t gpio_adc_read(struct gpio_adc g);
void gpio_adc_cancel_sample(struct gpio_adc g);

struct gpio_pwm gpio_pwm_setup(uint32_t pin, uint32_t cycle_time, uint8_t val);
void gpio_pwm_write(struct gpio_pwm g, uint8_t val);

/* ---- Timer (timer.c) --------------------------------------------------- */
void stm32_timer_init(void);

/* ---- Serial (serial.c) ------------------------------------------------- */
void stm32_serial_init(void);
void serial_enable_tx_irq(void);

#ifdef __cplusplus
}
#endif

#endif /* __STM32_INTERNAL_H */
