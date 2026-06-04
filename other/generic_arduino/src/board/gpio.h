/**
 * board/gpio.h - Platform-conditional forwarding header
 *
 * For STM32: → stm32/internal.h (port+bitmask GPIO structs)
 * For Arduino: → generic/gpio.h (pin-based GPIO structs)
 */
#if CONFIG_MACH_STM32
  #include "stm32/internal.h"
#else
  #include "generic/gpio.h"
#endif
