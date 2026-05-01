/**
 * stepper.h - Stub stepper header for generic_arduino
 *
 * The stepper subsystem is not enabled in this generic build
 * (CONFIG_INLINE_STEPPER_HACK=0, CONFIG_WANT_STEPPER=0).
 *
 * This stub provides the minimum declarations needed for sched.c to compile.
 */

#ifndef __STEPPER_H
#define __STEPPER_H

#include <stdint.h>

struct timer;
unsigned int stepper_event(struct timer *t);

#endif // __STEPPER_H
