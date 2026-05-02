/**
 * autoconf.h - Static configuration for the generic_arduino Kalico port.
 *
 * This replaces the Kconfig/menuconfig flow for Arduino environments.
 * Adjust these values to match your target board and wiring.
 */

#ifndef __AUTOCONF_H
#define __AUTOCONF_H

// ---- Machine selection ----------------------------------------------------
// Target MCU architecture: Arduino framework (AVR/ARM/ESP32)
#define CONFIG_MACH_ARDUINO       1
// HAL header directory name (maps to src/board/ and src/arduino/)
#define CONFIG_BOARD_DIRECTORY       "arduino"

// ---- Clock ----------------------------------------------------------------
// Arduino Uno/Nano:   16000000  (16 MHz)
// Arduino Mega:       16000000  (16 MHz)
// Arduino Due:        84000000  (84 MHz)
// Teensy 4.0:         600000000 (600 MHz)
// ESP32:              240000000 (240 MHz)
#ifndef CONFIG_CLOCK_FREQ
#define CONFIG_CLOCK_FREQ       16000000UL
#endif

// ---- Serial ---------------------------------------------------------------
// ── MCU Communication (Klipper host ↔ Arduino) ──
//
// Serial type for host communication:
//   0 = Hardware UART  (Serial1 on Mega/Due/Teensy/ESP32, Serial on Uno)
//   1 = Software Serial (bit-banged on arbitrary GPIO pins)
#define CONFIG_MCU_SERIAL_TYPE       0

// Baud rate for communication with the host (e.g. Raspberry Pi)
#define CONFIG_SERIAL_BAUD       250000

// Software Serial pins (only used when CONFIG_MCU_SERIAL_TYPE = 1)
// RX pin = receive from host; TX pin = transmit to host
#define CONFIG_MCU_SERIAL_SW_RX       10
#define CONFIG_MCU_SERIAL_SW_TX       11

// Hardware UART port index (only used when CONFIG_MCU_SERIAL_TYPE = 0)
//   0 = Serial  (Uno/Nano, pins 0/1 — conflicts with USB upload!)
//   1 = Serial1 (Mega 18/19, Due 19/18, Teensy, ESP32)
//   2 = Serial2 (Mega 16/17)
//   3 = Serial3 (Mega 14/15)
//
// Default: Uno/Nano use Serial(0), all others use Serial1(1)
#ifndef CONFIG_MCU_SERIAL_HW_PORT
  #if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_NANO)
    #define CONFIG_MCU_SERIAL_HW_PORT     0
  #else
    #define CONFIG_MCU_SERIAL_HW_PORT     1
  #endif
#endif

// Use double-speed mode on AVR (U2X)
#ifdef ARDUINO_AVR_UNO
  #define CONFIG_SERIAL_BAUD_U2X       1
#else
  #define CONFIG_SERIAL_BAUD_U2X       1
#endif

// ── Debug Serial (USB, for monitoring only) ──
//
// Which serial port to use for debug output:
//   0 = Serial  (USB, always available on boards with USB-to-serial)
//   1 = SerialUSB (native USB on Due/Teensy/ESP32-S2)
//   2 = Disabled (no debug output at all — saves flash & RAM)
#define CONFIG_DEBUG_SERIAL_PORT      0

// Baud rate for debug serial output
// Common values: 9600, 115200, 250000, 500000, 1000000
#define CONFIG_DEBUG_SERIAL_BAUD      250000

// ---- Memory management ----------------------------------------------------
// Dynamic memory pool / stack size (bytes). From heap start to end of free RAM.
// For AVR (Uno/Mega) this is small (128-256); for ARM/ESP32 it can be much larger.
#ifndef CONFIG_AVR_STACK_SIZE
  #define CONFIG_AVR_STACK_SIZE       128
#endif

// ---- Feature flags --------------------------------------------------------
// Enable basic digital GPIO read/write support (digitalWrite/digitalRead)
#define CONFIG_HAVE_GPIO       1
// Enable analog input support (analogRead / ADC)
#define CONFIG_HAVE_GPIO_ADC       1
// Enable hardware SPI peripheral (if available on target MCU)
#define CONFIG_HAVE_GPIO_SPI       0
// Enable hardware I2C peripheral (if available on target MCU)
#define CONFIG_HAVE_GPIO_I2C       0
// Enable hardware PWM support (analogWrite / timer-based PWM)
#define CONFIG_HAVE_GPIO_HARD_PWM       1
// Enable software bit-banging for generic GPIO protocols
#define CONFIG_WANT_GPIO_BITBANGING       1
// Build software (bit-bang) SPI implementation
#define CONFIG_WANT_SOFTWARE_SPI       0
// Build software (bit-bang) I2C implementation
#define CONFIG_WANT_SOFTWARE_I2C       0
// Build ADC sensor reading support (thermistor, etc.)
#define CONFIG_WANT_ADC       0
// Build SPI protocol support for external devices
#define CONFIG_WANT_SPI       0
// Build I2C protocol support for external devices
#define CONFIG_WANT_I2C       0
// Build hardware PWM output support (heaters, fans, servos)
#define CONFIG_WANT_HARD_PWM       0
// Build button/endstop input support (mechanical switches)
#define CONFIG_WANT_BUTTONS       0

// ---- Stepper configuration (set to 0 if not using steppers) ---------------
// Enable stepper motor control (requires timer-based step generation)
#define CONFIG_WANT_STEPPER       0
// Enable endstop switch support (homing and limit sensing)
#define CONFIG_WANT_ENDSTOPS       0

// Inline stepper dispatch (disabled for generic build)
#define CONFIG_INLINE_STEPPER_HACK       0

// Bootloader request support
#define CONFIG_HAVE_BOOTLOADER_REQUEST       0

// ---- MCU identification ---------------------------------------------------
// Human-readable MCU name reported via the identify protocol
#define CONFIG_MCU_NAME       "arduino_uno"

#endif // __AUTOCONF_H
