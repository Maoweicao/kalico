// Native autoconf.h — minimal configuration for host-native build
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifndef __AUTOCONF_H
#define __AUTOCONF_H

#define CONFIG_MCU_NAME             "native"
#define CONFIG_CLOCK_FREQ           1000000UL   // 1 MHz virtual clock
#define CONFIG_SERIAL_BAUD          250000

// Feature flags — minimal for protocol testing
#define CONFIG_HAVE_GPIO            1
#define CONFIG_HAVE_GPIO_ADC        0
#define CONFIG_HAVE_GPIO_SPI        0
#define CONFIG_HAVE_GPIO_I2C        0
#define CONFIG_HAVE_GPIO_HARD_PWM   0
#define CONFIG_HAVE_STEPPER         0
#define CONFIG_HAVE_ENDSTOPS        0

#define CONFIG_WANT_GPIO_BITBANGING 0
#define CONFIG_WANT_STEPPER         0
#define CONFIG_WANT_ENDSTOPS        0
#define CONFIG_WANT_ADC             0
#define CONFIG_WANT_SOFTWARE_SPI    0
#define CONFIG_WANT_SOFTWARE_I2C    0

// Memory sizes (unlimited for native)
#define CONFIG_RECV_WINDOW          256
#define CONFIG_TX_BUFFER_SIZE       128

#endif // __AUTOCONF_H
