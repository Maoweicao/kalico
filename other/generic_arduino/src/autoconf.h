/**
 * autoconf.h - Static configuration for the generic_arduino Kalico port.
 *
 * This replaces the Kconfig/menuconfig flow for Arduino environments.
 * Adjust these values to match your target board and wiring.
 */

#ifndef __AUTOCONF_H
#define __AUTOCONF_H

// ---- Machine selection ----------------------------------------------------
#define CONFIG_MACH_ARDUINO       1
#define CONFIG_BOARD_DIRECTORY    "arduino"

// ---- Clock ----------------------------------------------------------------
// Arduino Uno/Nano:   16000000  (16 MHz)
// Arduino Mega:       16000000  (16 MHz)
// Arduino Due:        84000000  (84 MHz)
// Teensy 4.0:         600000000 (600 MHz)
// ESP32:              240000000 (240 MHz)
#define CONFIG_CLOCK_FREQ         16000000UL

// ---- Serial ---------------------------------------------------------------
// Baud rate for communication with the host (e.g. Raspberry Pi)
#define CONFIG_SERIAL_BAUD         250000

// Use double-speed mode on AVR (U2X)
#ifdef ARDUINO_AVR_UNO
  #define CONFIG_SERIAL_BAUD_U2X   1
#else
  #define CONFIG_SERIAL_BAUD_U2X   0
#endif

// ---- Memory management ----------------------------------------------------
// Dynamic memory pool size (bytes). Start of heap to end of free RAM.
// For AVR this is small; for ARM/ESP32 it can be much larger.
#ifndef CONFIG_AVR_STACK_SIZE
  #define CONFIG_AVR_STACK_SIZE    256
#endif

// ---- Feature flags --------------------------------------------------------
#define CONFIG_HAVE_GPIO           1
#define CONFIG_HAVE_GPIO_ADC       1
#define CONFIG_HAVE_GPIO_SPI       0
#define CONFIG_HAVE_GPIO_I2C       0
#define CONFIG_HAVE_GPIO_HARD_PWM  1
#define CONFIG_WANT_GPIO_BITBANGING 1
#define CONFIG_WANT_SOFTWARE_SPI   0
#define CONFIG_WANT_SOFTWARE_I2C   0
#define CONFIG_WANT_ADC            0
#define CONFIG_WANT_SPI            0
#define CONFIG_WANT_I2C            0
#define CONFIG_WANT_HARD_PWM       0
#define CONFIG_WANT_BUTTONS        0

// ---- Stepper configuration (set to 0 if not using steppers) ---------------
#define CONFIG_WANT_STEPPER        0
#define CONFIG_WANT_ENDSTOPS       0

// Inline stepper dispatch (disabled for generic build)
#define CONFIG_INLINE_STEPPER_HACK 0

// Bootloader request support
#define CONFIG_HAVE_BOOTLOADER_REQUEST 0

// ---- MCU identification ---------------------------------------------------
#define CONFIG_MCU_NAME            "arduino"

#endif // __AUTOCONF_H
