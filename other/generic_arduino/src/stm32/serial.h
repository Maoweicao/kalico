/**
 * stm32/serial.h - Serial port declarations for STM32H723
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __STM32_SERIAL_H
#define __STM32_SERIAL_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

void serial_enable_tx_irq(void);

#ifdef __cplusplus
}
#endif

#endif /* __STM32_SERIAL_H */
