/**
 * board/io.h - Platform-conditional forwarding header
 */
#if CONFIG_MACH_STM32
  #include "stm32/io.h"
#else
  #include "arduino/io.h"
#endif
