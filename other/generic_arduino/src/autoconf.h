/**
 * autoconf.h - Static configuration for the generic_arduino Kalico port.
 *
 * This replaces the Kconfig/menuconfig flow for Arduino/STM32 environments.
 * Adjust these values to match your target board and wiring.
 *
 * For STM32 builds: define CONFIG_MACH_STM32=1 in platformio.ini build_flags.
 * For Arduino builds: CONFIG_MACH_ARDUINO is the default.
 */

#ifndef __AUTOCONF_H
#define __AUTOCONF_H

// ---- Machine selection ----------------------------------------------------
// Determine target platform from build flags.
// CONFIG_MACH_STM32 is set via -DCONFIG_MACH_STM32=1 in platformio.ini.
// If not set, default to Arduino.

#if CONFIG_MACH_STM32
  // ── STM32 configuration ─────────────────────────────────────────────────
  #define CONFIG_BOARD_DIRECTORY  "stm32"

  // STM32H723 clock: 528MHz system, 132MHz peripherals
  #ifndef CONFIG_CLOCK_FREQ
    #define CONFIG_CLOCK_FREQ       528000000UL
  #endif

  // Peripheral clock = system clock / 4 (after HPRE/2 and D*PPRE/2)
  #define FREQ_PERIPH  (CONFIG_CLOCK_FREQ / 4)

  #ifndef CONFIG_SERIAL_BAUD
    #define CONFIG_SERIAL_BAUD      250000
  #endif

  // STM32H723 identification
  #define CONFIG_MCU_NAME         "stm32h723"

  // No AVR stack size on STM32
  #define CONFIG_AVR_STACK_SIZE   0

  // Inline stepper dispatch: Cortex-M7 is fast enough for function pointer dispatch
  #define CONFIG_INLINE_STEPPER_HACK  0

#else
  // ── Arduino (default) configuration ──────────────────────────────────────
  #define CONFIG_MACH_ARDUINO     1
  #define CONFIG_BOARD_DIRECTORY  "arduino"

  #ifndef CONFIG_CLOCK_FREQ
    #define CONFIG_CLOCK_FREQ       16000000UL
  #endif

  #ifndef CONFIG_SERIAL_BAUD
    #define CONFIG_SERIAL_BAUD      115200
  #endif

  #define CONFIG_MCU_NAME         "arduino_uno"

  #ifndef CONFIG_AVR_STACK_SIZE
    #define CONFIG_AVR_STACK_SIZE   128
  #endif

  #if defined(__AVR__) && CONFIG_WANT_STEPPER
    #define CONFIG_INLINE_STEPPER_HACK  1
  #else
    #define CONFIG_INLINE_STEPPER_HACK  0
  #endif

#endif // CONFIG_MACH_STM32

// ---- Serial (Arduino-specific) --------------------------------------------
#if CONFIG_MACH_ARDUINO
  #define CONFIG_MCU_SERIAL_TYPE       0

  #ifndef CONFIG_MCU_SERIAL_HW_PORT
    #if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_NANO)
      #define CONFIG_MCU_SERIAL_HW_PORT     0
    #else
      #define CONFIG_MCU_SERIAL_HW_PORT     1
    #endif
  #endif

  #ifdef ARDUINO_AVR_UNO
    #define CONFIG_SERIAL_BAUD_U2X       0
  #else
    #define CONFIG_SERIAL_BAUD_U2X       1
  #endif

  #define CONFIG_MCU_SERIAL_SW_RX       10
  #define CONFIG_MCU_SERIAL_SW_TX       11
#endif // CONFIG_MACH_ARDUINO

// ---- Debug serial (disabled by default) -----------------------------------
#define CONFIG_DEBUG_SERIAL_PORT      2
#define CONFIG_DEBUG_SERIAL_BAUD      250000

// ---- Feature flags --------------------------------------------------------
#define CONFIG_HAVE_GPIO            1
#define CONFIG_HAVE_GPIO_ADC        1
#define CONFIG_HAVE_GPIO_SPI        0
#define CONFIG_HAVE_GPIO_I2C        0
#define CONFIG_HAVE_GPIO_HARD_PWM   0
#define CONFIG_WANT_GPIO_BITBANGING 1
#define CONFIG_WANT_SOFTWARE_SPI    0
#define CONFIG_WANT_SOFTWARE_I2C    0
#define CONFIG_WANT_ADC             0
#define CONFIG_WANT_SPI             0
#define CONFIG_WANT_I2C             0
#define CONFIG_WANT_HARD_PWM        0
#define CONFIG_WANT_BUTTONS         0

// ---- Stepper configuration ------------------------------------------------
#define CONFIG_WANT_STEPPER         1
#define CONFIG_WANT_ENDSTOPS        0

// Bootloader request support
#define CONFIG_HAVE_BOOTLOADER_REQUEST  0

#endif // __AUTOCONF_H
