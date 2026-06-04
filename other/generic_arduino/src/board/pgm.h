/**
 * board/pgm.h - Platform-conditional forwarding header
 */
#if CONFIG_MACH_STM32
  #include "stm32/pgm.h"
#else
  #include "arduino/pgm.h"
#endif
