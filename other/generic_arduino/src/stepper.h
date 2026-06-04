/**
 * stepper.h - Stepper motor driver declarations
 *
 * Copyright (C) 2016-2025  Kevin O'Connor <kevin@koconnor.net>
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __STEPPER_H
#define __STEPPER_H

#include <stdint.h>

struct timer;
uint_fast8_t stepper_event(struct timer *t);
void stepper_shutdown(void);

#endif // __STEPPER_H
