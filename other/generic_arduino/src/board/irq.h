/**
 * board/irq.h - Platform-conditional forwarding header
 *
 * For STM32: → stm32/irq.h (CMSIS __get_PRIMASK / __set_PRIMASK)
 * For Arduino: → arduino/irq.h (cli() / sei() or __disable_irq / __enable_irq)
 */
#if CONFIG_MACH_STM32
  #include "stm32/irq.h"
#else
  #include "arduino/irq.h"
#endif
