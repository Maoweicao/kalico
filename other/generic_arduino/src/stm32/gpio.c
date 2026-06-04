/**
 * stm32/gpio.c - GPIO operations for STM32H723
 *
 * Derived from Klipper src/stm32/stm32h7_gpio.c and src/stm32/gpio.c
 *
 * Uses direct register access to GPIO peripherals. Pin encoding follows
 * the Klipper convention: GPIO('A', 0) = 0, GPIO('B', 0) = 16, etc.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <string.h>     /* ffs */
#include "autoconf.h"
#include "internal.h"
#include "irq.h"        /* irq_save / irq_restore */
#include "misc.h"       /* dynmem_start / dynmem_end */
#include "command.h"    /* DECL_ENUMERATION_RANGE, shutdown */
#include "sched.h"      /* sched_shutdown (used by shutdown() macro) */
#include "compiler.h"   /* ARRAY_SIZE, ALIGN */

/* ---- Pin enumeration for Klipper data dictionary ----------------------- */

DECL_ENUMERATION_RANGE("pin", "PA0", GPIO('A', 0), 16);
DECL_ENUMERATION_RANGE("pin", "PB0", GPIO('B', 0), 16);
DECL_ENUMERATION_RANGE("pin", "PC0", GPIO('C', 0), 16);
DECL_ENUMERATION_RANGE("pin", "PD0", GPIO('D', 0), 16);
DECL_ENUMERATION_RANGE("pin", "PE0", GPIO('E', 0), 16);
#ifdef GPIOF
DECL_ENUMERATION_RANGE("pin", "PF0", GPIO('F', 0), 16);
#endif
#ifdef GPIOG
DECL_ENUMERATION_RANGE("pin", "PG0", GPIO('G', 0), 16);
#endif
#ifdef GPIOH
DECL_ENUMERATION_RANGE("pin", "PH0", GPIO('H', 0), 16);
#endif
#ifdef GPIOI
DECL_ENUMERATION_RANGE("pin", "PI0", GPIO('I', 0), 16);
#endif

/* ---- GPIO port register table ------------------------------------------ */

GPIO_TypeDef * const digital_regs[] = {
    ['A' - 'A'] = GPIOA,
    ['B' - 'A'] = GPIOB,
    ['C' - 'A'] = GPIOC,
    ['D' - 'A'] = GPIOD,
    ['E' - 'A'] = GPIOE,
#ifdef GPIOF
    ['F' - 'A'] = GPIOF,
#endif
#ifdef GPIOG
    ['G' - 'A'] = GPIOG,
#endif
#ifdef GPIOH
    ['H' - 'A'] = GPIOH,
#endif
#ifdef GPIOI
    ['I' - 'A'] = GPIOI,
#endif
};

/* Verify that a pin number maps to a valid GPIO port */
static int
gpio_valid(uint32_t pin)
{
    uint32_t port = GPIO2PORT(pin);
    return port < ARRAY_SIZE(digital_regs) && digital_regs[port];
}

/* ---- GPIO peripheral mode configuration -------------------------------- */
/*
 * Configures a GPIO pin's alternate function / mode via MODER, OTYPER,
 * OSPEEDR, PUPDR, and AFR registers.
 *
 * mode: GPIO_INPUT, GPIO_OUTPUT, GPIO_ANALOG, GPIO_FUNCTION(fn),
 *       optionally OR'd with GPIO_OPEN_DRAIN / GPIO_HIGH_SPEED.
 * pullup: 0 = none, 1 = pull-up, -1 = pull-down.
 */
void
gpio_peripheral(uint32_t gpio, uint32_t mode, int pullup)
{
    GPIO_TypeDef *regs = digital_regs[GPIO2PORT(gpio)];
    uint32_t bit = GPIO2BIT(gpio);
    uint32_t bit_num = __builtin_ffs(bit) - 1;   /* 0-15 */
    uint32_t pos = bit_num * 2;                    /* bit position in 2-bit fields */
    uint32_t func = mode & 0x0F;

    /* MODER: 2 bits per pin */
    regs->MODER = (regs->MODER & ~(3 << pos)) | ((func & 3) << pos);

    /* OTYPER: output type (push-pull vs open-drain) */
    if (mode & GPIO_OPEN_DRAIN)
        regs->OTYPER |= bit;
    else
        regs->OTYPER &= ~bit;

    /* OSPEEDR: output speed */
    if (mode & GPIO_HIGH_SPEED)
        regs->OSPEEDR = (regs->OSPEEDR & ~(3 << pos)) | (3 << pos);
    else
        regs->OSPEEDR = (regs->OSPEEDR & ~(3 << pos)) | (1 << pos);

    /* PUPDR: pull-up/pull-down */
    uint32_t pupdr_val = 0;
    if (pullup > 0)
        pupdr_val = 1;   /* pull-up */
    else if (pullup < 0)
        pupdr_val = 2;   /* pull-down */
    regs->PUPDR = (regs->PUPDR & ~(3 << pos)) | (pupdr_val << pos);

    /* AFR: alternate function (AFRL for pins 0-7, AFRH for pins 8-15) */
    if (func >= 2) {
        uint32_t af = (mode >> 4) & 0x0F;
        if (bit_num < 8) {
            uint32_t af_pos = bit_num * 4;
            regs->AFR[0] = (regs->AFR[0] & ~(0xF << af_pos)) | (af << af_pos);
        } else {
            uint32_t af_pos = (bit_num - 8) * 4;
            regs->AFR[1] = (regs->AFR[1] & ~(0xF << af_pos)) | (af << af_pos);
        }
    }
}

/* ---- GPIO Output ------------------------------------------------------- */

struct gpio_out
gpio_out_setup(uint32_t pin, uint32_t val)
{
    if (!gpio_valid(pin))
        shutdown("Not an output pin");

    GPIO_TypeDef *regs = digital_regs[GPIO2PORT(pin)];
    gpio_clock_enable(regs);

    struct gpio_out g = { .regs = regs, .bit = GPIO2BIT(pin) };
    gpio_out_reset(g, val);
    return g;
}

void
gpio_out_reset(struct gpio_out g, uint32_t val)
{
    irqstatus_t flag = irq_save();
    /* Set or clear via BSRR (atomic) */
    if (val)
        g.regs->BSRR = g.bit;
    else
        g.regs->BSRR = g.bit << 16;
    /* Configure as general-purpose output (MODER=01, push-pull, high-speed) */
    uint32_t bit_num = __builtin_ffs(g.bit) - 1;
    uint32_t pos = bit_num * 2;
    g.regs->MODER = (g.regs->MODER & ~(3 << pos)) | (1 << pos);
    g.regs->OSPEEDR = (g.regs->OSPEEDR & ~(3 << pos)) | (3 << pos);
    irq_restore(flag);
}

void
gpio_out_toggle_noirq(struct gpio_out g)
{
    /* Toggle via XOR on ODR */
    g.regs->ODR ^= g.bit;
}

void
gpio_out_toggle(struct gpio_out g)
{
    irqstatus_t flag = irq_save();
    gpio_out_toggle_noirq(g);
    irq_restore(flag);
}

void
gpio_out_write(struct gpio_out g, uint32_t val)
{
    /* BSRR is atomic: writing to lower 16 bits sets, upper 16 bits clears */
    if (val)
        g.regs->BSRR = g.bit;
    else
        g.regs->BSRR = g.bit << 16;
}

uint8_t
gpio_out_valid(struct gpio_out g, uint32_t val)
{
    return 1;
}

/* ---- GPIO Input -------------------------------------------------------- */

struct gpio_in
gpio_in_setup(uint32_t pin, int32_t pull_up)
{
    if (!gpio_valid(pin))
        shutdown("Not a valid input pin");

    GPIO_TypeDef *regs = digital_regs[GPIO2PORT(pin)];
    gpio_clock_enable(regs);

    struct gpio_in g = { .regs = regs, .bit = GPIO2BIT(pin) };
    gpio_in_reset(g, pull_up);
    return g;
}

void
gpio_in_reset(struct gpio_in g, int32_t pull_up)
{
    irqstatus_t flag = irq_save();
    /* Configure as input (MODER=00) */
    uint32_t bit_num = __builtin_ffs(g.bit) - 1;
    uint32_t pos = bit_num * 2;
    g.regs->MODER &= ~(3 << pos);

    /* Set pull-up / pull-down */
    uint32_t pupdr_val = 0;
    if (pull_up > 0)
        pupdr_val = 1;
    else if (pull_up < 0)
        pupdr_val = 2;
    g.regs->PUPDR = (g.regs->PUPDR & ~(3 << pos)) | (pupdr_val << pos);
    irq_restore(flag);
}

uint8_t
gpio_in_read(struct gpio_in g)
{
    return !!(g.regs->IDR & g.bit);
}

/* ---- GPIO ADC (stubs - ADC not yet implemented) ------------------------ */

struct gpio_adc
gpio_adc_setup(uint32_t pin)
{
    shutdown("STM32 ADC not yet implemented");
    /* Unreachable */
    struct gpio_adc g = { .chan = 0, .adc = NULL };
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

/* ---- GPIO PWM (stubs - PWM not yet implemented) ------------------------ */

struct gpio_pwm
gpio_pwm_setup(uint32_t pin, uint32_t cycle_time, uint8_t val)
{
    shutdown("STM32 PWM not yet implemented");
    /* Unreachable */
    struct gpio_pwm g = { .tim = NULL, .chan = 0 };
    return g;
}

void
gpio_pwm_write(struct gpio_pwm g, uint8_t val)
{
}

/* ---- Dynamic memory (non-AVR: use static pool from alloc.c) ------------ */
/* dynmem_start() and dynmem_end() are provided by generic/alloc.c */

/* ---- Bootloader request ------------------------------------------------ */

void
bootloader_request(void)
{
    /* No-op for now.  Could be implemented as DFU reboot. */
}
