/**
 * stepper.c - Stub stepper implementation for generic_arduino
 *
 * Provides a dummy stepper_event() for builds without stepper support.
 */

#include "stepper.h"
#include "sched.h"

unsigned int
stepper_event(struct timer *t)
{
    // Stepper not configured — should never be called
    shutdown("stepper_event called without stepper support");
    return SF_DONE;
}
