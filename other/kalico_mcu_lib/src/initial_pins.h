#ifndef __INITIAL_PINS_H
#define __INITIAL_PINS_H

#include <stdint.h>

struct initial_pin_s {
    int pin;
    uint8_t flags;
};

enum { IP_OUT_HIGH = 1 };

// Auto-generated in compile_time_request.c
extern const struct initial_pin_s initial_pins[];
extern const int initial_pins_size;

#endif // initial_pins.h
