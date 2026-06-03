/**
 * board/gpio.h - Forwarding header → generic/gpio.h
 *
 * Our Arduino GPIO implementation uses the generic pin-based structs,
 * not the AVR register-based structs.
 */
#include "generic/gpio.h"
