/**
 * board/misc.h - Platform-conditional forwarding header
 */
#if CONFIG_MACH_STM32
  #include "stm32/misc.h"
#else
  #include "arduino/misc.h"
#endif
