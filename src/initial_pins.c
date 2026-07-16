// Support setting gpio pins at mcu start
//
// Copyright (C) 2019  Kevin O'Connor <kevin@koconnor.net>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "autoconf.h" // CONFIG_INITIAL_PINS
#include "board/gpio.h" // gpio_in_setup, gpio_out_setup
#include "board/pgm.h" // READP
#include "ctr.h" // DECL_CTR
#include "initial_pins.h" // initial_pins
#include "sched.h" // DECL_INIT

DECL_CTR("DECL_INITIAL_PINS " __stringify(CONFIG_INITIAL_PINS));
DECL_CTR("DECL_STARTUP_PIN_STATE " __stringify(CONFIG_STARTUP_PIN_STATE));

void
initial_pins_setup(void)
{
    int i;
    if (CONFIG_STARTUP_PIN_STATE) {
        for (i=0; i<startup_state_pins_size; i++) {
            int pin = READP(startup_state_pins[i]);
            if (CONFIG_STARTUP_PIN_STATE == 1
                || CONFIG_STARTUP_PIN_STATE == -1)
                gpio_in_setup(pin, CONFIG_STARTUP_PIN_STATE);
            else
                gpio_out_setup(pin, CONFIG_STARTUP_PIN_STATE > 0);
        }
    }
    for (i=0; i<initial_pins_size; i++) {
        const struct initial_pin_s *ip = &initial_pins[i];
        gpio_out_setup(READP(ip->pin), READP(ip->flags) & IP_OUT_HIGH);
    }
}
DECL_INIT(initial_pins_setup);
