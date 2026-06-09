/**
 * board/serial_irq.h - Forwarding header → arduino/serial.h
 *
 * The original Kalico serial_irq.h declares:
 *   void serial_enable_tx_irq(void);
 *   void serial_rx_byte(uint_fast8_t data);
 *   int serial_get_tx_byte(uint8_t *pdata);
 *
 * Our arduino/serial.h provides serial_enable_tx_irq.
 * serial_rx_byte/serial_get_tx_byte are in arduino/serial.c.
 */
#include "arduino/serial.h"

// These are declared globally from arduino/serial.c
void serial_rx_byte(uint_fast8_t data);
int serial_get_tx_byte(uint8_t *pdata);
