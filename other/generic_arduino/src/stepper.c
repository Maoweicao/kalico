/**
 * stepper.c - Stepper motor driver for generic_arduino
 *
 * Ported from src/stepper.c (Klipper/Kalico).
 * Uses stepper_event_full() path (generic, no edge optimization).
 * On AVR with ISR-native timer, stepper_event runs inside Timer1 COMPA ISR.
 *
 * Copyright (C) 2016-2025  Kevin O'Connor <kevin@koconnor.net>
 * Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "autoconf.h"   // CONFIG_*
#include "basecmd.h"    // oid_alloc, move_alloc, move_free
#include "board/gpio.h" // gpio_out_write, gpio_out_toggle_noirq
#include "board/irq.h"  // irq_disable, irq_enable
#include "board/misc.h" // timer_is_before
#include "command.h"    // DECL_COMMAND, sendf, shutdown
#include "sched.h"      // struct timer, sched_add_timer, sched_del_timer
#include "stepper.h"    // stepper_event


// ============================================================================
// Data structures
// ============================================================================

struct stepper_move {
    struct move_node node;
    uint32_t interval;
    int16_t add;
    uint16_t count;
    uint8_t flags;
};

enum { MF_DIR = 1 << 0 };

struct stepper {
    struct timer time;
    uint32_t interval;
    int16_t add;
    uint32_t count;
    uint32_t next_step_time, step_pulse_ticks;
    struct gpio_out step_pin, dir_pin;
    uint32_t position;
    struct move_queue_head mq;
    uint8_t flags;
};

enum { POSITION_BIAS = 0x40000000 };

enum {
    SF_LAST_DIR     = 1 << 0,
    SF_NEXT_DIR     = 1 << 1,
    SF_INVERT_STEP  = 1 << 2,
    SF_NEED_RESET   = 1 << 3,
    SF_SINGLE_SCHED = 1 << 4,
};


// ============================================================================
// Stepper move loading
// ============================================================================

// Forward declarations
static uint_fast8_t stepper_event_full(struct timer *t);
void command_config_stepper(uint32_t *args);

static uint_fast8_t
stepper_load_next(struct stepper *s)
{
    if (move_queue_empty(&s->mq)) {
        s->count = 0;
        return SF_DONE;
    }

    struct move_node *mn = move_queue_pop(&s->mq);
    struct stepper_move *m = container_of(mn, struct stepper_move, node);
    uint32_t move_interval = m->interval;
    uint_fast16_t move_count = m->count;
    int_fast16_t move_add = m->add;
    uint_fast8_t need_dir_change = m->flags & MF_DIR;
    move_free(m);

    // Update position tracking
    s->position = (need_dir_change ? -s->position : s->position) + move_count;

    // Load move parameters
    s->add = move_add;
    s->interval = move_interval + move_add;

    // Using fully scheduled stepper_event_full() — the scheduler
    // is called twice for each step (once for step, once for unstep)
    uint_fast8_t was_active = !!s->count;
    uint32_t min_next_time = s->time.waketime;
    s->next_step_time += move_interval;
    s->time.waketime = s->next_step_time;
    s->count = (s->flags & SF_SINGLE_SCHED ? move_count
                : (uint32_t)move_count * 2);
    if (was_active && timer_is_before(s->next_step_time, min_next_time)) {
        // Actively stepping and next step event close to the last
        int32_t diff = s->next_step_time - min_next_time;
        if (diff < (int32_t)-timer_from_us(1000))
            shutdown("Stepper too far in past");
        s->time.waketime = min_next_time;
    }
    if (was_active && need_dir_change) {
        if (s->flags & SF_SINGLE_SCHED)
            while (timer_is_before(timer_read_time(), min_next_time))
                ;
        gpio_out_toggle_noirq(s->dir_pin);
        uint32_t curtime = timer_read_time();
        min_next_time = curtime + s->step_pulse_ticks;
        if (timer_is_before(s->time.waketime, min_next_time))
            s->time.waketime = min_next_time;
        return SF_RESCHEDULE;
    }

    // Set new direction if needed
    if (need_dir_change)
        gpio_out_toggle_noirq(s->dir_pin);
    return SF_RESCHEDULE;
}


// ============================================================================
// Stepper event handler (fully scheduled)
// ============================================================================

// This function runs inside the timer ISR on AVR (ISR-native mode)
// or from irq_poll() on ARM/ESP32 (poll-based mode).
static uint_fast8_t
stepper_event_full(struct timer *t)
{
    struct stepper *s = container_of(t, struct stepper, time);

    // Toggle step pin (generates one edge per call)
    gpio_out_toggle_noirq(s->step_pin);

    uint32_t curtime = timer_read_time();
    uint32_t min_next_time = curtime + s->step_pulse_ticks;
    uint32_t count = s->count - 1;

    if (likely(count & 1 && !(s->flags & SF_SINGLE_SCHED)))
        // Schedule unstep event
        goto reschedule_min;

    if (likely(count)) {
        s->next_step_time += s->interval;
        s->interval += s->add;
        if (unlikely(timer_is_before(s->next_step_time, min_next_time)))
            goto reschedule_min;
        s->count = count;
        s->time.waketime = s->next_step_time;
        return SF_RESCHEDULE;
    }

    s->time.waketime = min_next_time;
    return stepper_load_next(s);

reschedule_min:
    s->count = count;
    s->time.waketime = min_next_time;
    return SF_RESCHEDULE;
}

// Entry point — called from sched_timer_dispatch via inline hack or func ptr
uint_fast8_t
stepper_event(struct timer *t)
{
    return stepper_event_full(t);
}


// ============================================================================
// Command handlers
// ============================================================================

static struct stepper *
stepper_oid_lookup(uint8_t oid)
{
    return oid_lookup(oid, command_config_stepper);
}

// Configure a stepper
void
command_config_stepper(uint32_t *args)
{
    struct stepper *s = oid_alloc(args[0], command_config_stepper, sizeof(*s));
    int_fast8_t invert_step = args[3];
    if (invert_step > 0)
        s->flags = SF_INVERT_STEP;
    else if (invert_step < 0)
        s->flags = SF_SINGLE_SCHED;
    s->step_pin = gpio_out_setup(args[1], s->flags & SF_INVERT_STEP);
    s->dir_pin = gpio_out_setup(args[2], 0);
    s->position = -POSITION_BIAS;
    s->step_pulse_ticks = args[4];
    move_queue_setup(&s->mq, sizeof(struct stepper_move));
    // Always use stepper_event_full (generic path)
    if (!CONFIG_INLINE_STEPPER_HACK)
        s->time.func = stepper_event_full;
}

// Queue a set of steps with given timing
void
command_queue_step(uint32_t *args)
{
    struct stepper *s = stepper_oid_lookup(args[0]);
    struct stepper_move *m = move_alloc();
    m->interval = args[1];
    m->count = args[2];
    if (!m->count)
        shutdown("Invalid count parameter");
    m->add = args[3];
    m->flags = 0;

    irq_disable();
    uint8_t flags = s->flags;
    if (!!(flags & SF_LAST_DIR) != !!(flags & SF_NEXT_DIR)) {
        flags ^= SF_LAST_DIR;
        m->flags |= MF_DIR;
    }
    if (s->count) {
        s->flags = flags;
        move_queue_push(&m->node, &s->mq);
    } else if (flags & SF_NEED_RESET) {
        move_free(m);
    } else {
        s->flags = flags;
        move_queue_push(&m->node, &s->mq);
        stepper_load_next(s);
        sched_add_timer(&s->time);
    }
    irq_enable();
}

// Set the direction of the next queued step
void
command_set_next_step_dir(uint32_t *args)
{
    struct stepper *s = stepper_oid_lookup(args[0]);
    uint8_t nextdir = args[1] ? SF_NEXT_DIR : 0;
    irq_disable();
    s->flags = (s->flags & ~SF_NEXT_DIR) | nextdir;
    irq_enable();
}

// Set absolute time for the next step
void
command_reset_step_clock(uint32_t *args)
{
    struct stepper *s = stepper_oid_lookup(args[0]);
    uint32_t waketime = args[1];
    irq_disable();
    if (s->count)
        shutdown("Can't reset time when stepper active");
    s->next_step_time = s->time.waketime = waketime;
    s->flags &= ~SF_NEED_RESET;
    irq_enable();
}

// Return current stepper position
static uint32_t
stepper_get_position(struct stepper *s)
{
    uint32_t position = s->position;
    if (s->flags & SF_SINGLE_SCHED)
        position -= s->count;
    else
        position -= s->count / 2;
    if (position & 0x80000000)
        return -position;
    return position;
}

void
command_stepper_get_position(uint32_t *args)
{
    uint8_t oid = args[0];
    struct stepper *s = stepper_oid_lookup(oid);
    irq_disable();
    uint32_t position = stepper_get_position(s);
    irq_enable();
    sendf("stepper_position oid=%c pos=%i", oid, position - POSITION_BIAS);
}

// Stop all moves for a given stepper
static void
stepper_stop(struct stepper *s)
{
    sched_del_timer(&s->time);
    s->next_step_time = s->time.waketime = 0;
    s->position = -stepper_get_position(s);
    s->count = 0;
    s->flags = (s->flags & (SF_INVERT_STEP | SF_SINGLE_SCHED)) | SF_NEED_RESET;
    gpio_out_write(s->dir_pin, 0);
    if (!(s->flags & SF_SINGLE_SCHED))
        gpio_out_write(s->step_pin, s->flags & SF_INVERT_STEP);
    while (!move_queue_empty(&s->mq)) {
        struct move_node *mn = move_queue_pop(&s->mq);
        struct stepper_move *m = container_of(mn, struct stepper_move, node);
        move_free(m);
    }
}

// Set stepper to stop on trigger (simplified — no trsync)
void
command_stepper_stop_on_trigger(uint32_t *args)
{
    struct stepper *s = stepper_oid_lookup(args[0]);
    // Simplified: just stop the stepper immediately
    irq_disable();
    stepper_stop(s);
    irq_enable();
}

// Shutdown handler
void
stepper_shutdown(void)
{
    uint8_t i;
    struct stepper *s;
    foreach_oid(i, s, command_config_stepper) {
        move_queue_clear(&s->mq);
        stepper_stop(s);
    }
}
