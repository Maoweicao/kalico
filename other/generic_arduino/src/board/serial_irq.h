/**
 * board/serial_irq.h - Platform-conditional forwarding header
 *
 * Declares serial_enable_tx_irq and serial_rx_byte / serial_get_tx_byte.
 * serial_enable_tx_irq is provided by platform serial code.
 * serial_rx_byte / serial_get_tx_byte are provided by generic/serial_irq.c.
 */
#if CONFIG_MACH_STM32
  #include "stm32/serial.h"
#else
  #include "arduino/serial.h"
#endif

/* These are declared globally from generic/serial_irq.c */
void serial_rx_byte(uint_fast8_t data);
int serial_get_tx_byte(uint8_t *pdata);
