/**
 * board/irq.h - Platform-conditional forwarding header
 *
 * For STM32: → stm32/irq.h (CMSIS __get_PRIMASK / __set_PRIMASK)
 * For ESP32: → esp32/irq.h (portDISABLE_INTERRUPTS / portSET_INTERRUPT_MASK_FROM_ISR)
 * For Arduino: → arduino/irq.h (cli() / sei() or __disable_irq / __enable_irq)
 */
#if CONFIG_MACH_STM32
  #include "stm32/irq.h"
#elif CONFIG_MACH_ESP32
  #include "esp32/irq.h"
#else
  #include "arduino/irq.h"
#endif
