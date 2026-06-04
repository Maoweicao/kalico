/**
 * stm32/serial.c - UART serial for STM32H723 using USART3
 *
 * Interrupt-driven UART using direct register access.
 * Uses the generic/serial_irq.c protocol layer (same as AVR).
 *
 * Default: USART3 on PD8 (TX) / PD9 (RX) — ST-Link VCP on Nucleo H723ZG.
 * Alternate: USART1 on PA9 (TX) / PA10 (RX).
 *
 * Derived from Klipper src/stm32/serial.c
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"
#include "internal.h"
#include "irq.h"
#include "misc.h"
#include "serial.h"             /* serial_enable_tx_irq declaration */
#include "command.h"            /* DECL_CONSTANT_STR, DECL_CONSTANT */
#include "sched.h"
#include "generic/serial_irq.h" /* serial_rx_byte, serial_get_tx_byte */
#include "compiler.h"           /* DIV_ROUND_CLOSEST */

/* ---- Serial port selection --------------------------------------------- */
/*
 * Set CONFIG_STM32_SERIAL_USART3 or CONFIG_STM32_SERIAL_USART1 in
 * platformio.ini build_flags (e.g. -DCONFIG_STM32_SERIAL_USART3=1).
 * Default is USART3.
 */

#ifndef CONFIG_STM32_SERIAL_USART1
#define CONFIG_STM32_SERIAL_USART1 0
#endif
#ifndef CONFIG_STM32_SERIAL_USART3
#define CONFIG_STM32_SERIAL_USART3 1
#endif

#if CONFIG_STM32_SERIAL_USART3
  /* USART3: PD8=TX, PD9=RX, AF7 */
  #define GPIO_Rx     GPIO('D', 9)
  #define GPIO_Tx     GPIO('D', 8)
  #define GPIO_AF     7
  #define USARTx      USART3
  #define USARTx_IRQn USART3_IRQn
#elif CONFIG_STM32_SERIAL_USART1
  /* USART1: PA9=TX, PA10=RX, AF7 */
  #define GPIO_Rx     GPIO('A', 10)
  #define GPIO_Tx     GPIO('A', 9)
  #define GPIO_AF     7
  #define USARTx      USART1
  #define USARTx_IRQn USART1_IRQn
#endif

/* CR1 flags: enable UE (USART), RE (receiver), TE (transmitter), RXNEIE (RX interrupt) */
#define CR1_FLAGS   (USART_CR1_UE | USART_CR1_RE | USART_CR1_TE | USART_CR1_RXNEIE)

/* ---- USART IRQ handler ------------------------------------------------- */

void
USARTx_IRQHandler(void)
{
    uint32_t isr = USARTx->ISR;

    /* RX: read data register (also clears ORE, NE, FE flags) */
    if (isr & (USART_ISR_RXNE_RXFNE | USART_ISR_ORE)) {
        serial_rx_byte(USARTx->RDR);
    }

    /* TX: transmit next byte if TXE interrupt is enabled */
    if ((isr & USART_ISR_TXE_TXFNF) && (USARTx->CR1 & USART_CR1_TXEIE)) {
        uint8_t data;
        int ret = serial_get_tx_byte(&data);
        if (ret) {
            /* No more data — disable TX interrupt */
            USARTx->CR1 = CR1_FLAGS;
        } else {
            USARTx->TDR = data;
        }
    }
}

/* ---- serial_enable_tx_irq ---------------------------------------------- */
/* Called by generic/serial_irq.c when data is ready in the TX buffer. */

void
serial_enable_tx_irq(void)
{
    USARTx->CR1 = CR1_FLAGS | USART_CR1_TXEIE;
}

/* ---- Initialization ---------------------------------------------------- */

void
stm32_serial_init(void)
{
    static int initialized = 0;
    if (initialized)
        return;
    initialized = 1;

    /* Enable USART peripheral clock */
    enable_pclock((uint32_t)USARTx);

    /* Configure baud rate:
     * BRR = peripheral_clock / baud_rate
     * H7 USART uses oversampling by 16 (default).
     * BRR = mantissa | fraction (4 bits).
     */
    uint32_t pclk = get_pclock_frequency((uint32_t)USARTx);
    uint32_t brr = DIV_ROUND_CLOSEST(pclk, CONFIG_SERIAL_BAUD);
    USARTx->BRR = brr;

    /* Configure USART: 8N1, enable TX/RX, RX interrupt */
    USARTx->CR1 = CR1_FLAGS;
    USARTx->CR2 = 0;  /* 1 stop bit */
    USARTx->CR3 = 0;  /* No flow control */

    /* Configure GPIO pins for USART alternate function */
    gpio_peripheral(GPIO_Rx, GPIO_FUNCTION(GPIO_AF), 1);  /* RX with pull-up */
    gpio_peripheral(GPIO_Tx, GPIO_FUNCTION(GPIO_AF), 0);  /* TX no pull */

    /* Enable USART interrupt in NVIC */
    NVIC_SetPriority(USARTx_IRQn, 1);  /* Priority 1 (lower than TIM2's 0) */
    NVIC_EnableIRQ(USARTx_IRQn);
}
