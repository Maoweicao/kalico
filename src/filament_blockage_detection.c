// Filament blockage sensor measurement helper
// 耗材堵塞检测传感器
//
// Copyright (C) 2026  Mellow <service@3dmellow.com>
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "basecmd.h" // oid_alloc
#include "board/gpio.h" // gpio_in_read
#include "board/irq.h" // irq_disable
#include "board/misc.h" // timer_is_before
#include "command.h" // DECL_COMMAND
#include "sched.h" // struct timer

enum {
    FBF_PENDING = 1 << 0,
};

struct filament_blockage {
    struct timer time;
    struct gpio_in pin;
    uint32_t poll_ticks, report_ticks, next_report_time;
    uint32_t measured_um, edge_count, distance_per_edge_um;
    uint8_t oid, last_pin_state, flags;
};

static struct task_wake filament_blockage_wake;

static void
filament_blockage_log(uint8_t reason, uint8_t oid, uint32_t measured_um,
                      uint32_t edge_count, uint8_t pin_state,
                      uint32_t poll_ticks, uint32_t report_ticks)
{
    output("filament_blockage_debug reason=%c oid=%c measured_um=%u"
           " edge_count=%u pin_state=%c poll_ticks=%u report_ticks=%u",
           reason, oid, measured_um, edge_count, pin_state,
           poll_ticks, report_ticks);
}

static uint_fast8_t
filament_blockage_event(struct timer *t)
{
    struct filament_blockage *fb = container_of(
        t, struct filament_blockage, time);
    uint8_t pin_state = gpio_in_read(fb->pin);

    if (pin_state != fb->last_pin_state) {
        fb->last_pin_state = pin_state;
        fb->edge_count++;
        fb->measured_um += fb->distance_per_edge_um;
    }

    if (!timer_is_before(fb->time.waketime, fb->next_report_time)) {
        fb->next_report_time = fb->time.waketime + fb->report_ticks;
        fb->flags |= FBF_PENDING;
        sched_wake_task(&filament_blockage_wake);
    }

    fb->time.waketime += fb->poll_ticks;
    return SF_RESCHEDULE;
}

void
command_config_filament_blockage(uint32_t *args)
{
    struct filament_blockage *fb = oid_alloc(
        args[0], command_config_filament_blockage, sizeof(*fb));
    fb->oid = args[0];
    fb->pin = gpio_in_setup(args[1], args[2]);
    fb->time.func = filament_blockage_event;
    filament_blockage_log(1, fb->oid, 0, 0, 0, 0, 0);
}
DECL_COMMAND(command_config_filament_blockage,
             "config_filament_blockage oid=%c pin=%u pull_up=%c");

void
command_filament_blockage_start(uint32_t *args)
{
    struct filament_blockage *fb = oid_lookup(
        args[0], command_config_filament_blockage);
    sched_del_timer(&fb->time);
    fb->time.waketime = args[1];
    fb->poll_ticks = args[2];
    fb->report_ticks = args[3];
    fb->distance_per_edge_um = args[4];
    fb->next_report_time = args[1] + args[3];
    fb->measured_um = 0;
    fb->edge_count = 0;
    fb->flags = 0;
    fb->last_pin_state = gpio_in_read(fb->pin);
    filament_blockage_log(2, fb->oid, fb->measured_um, fb->edge_count,
                          fb->last_pin_state, fb->poll_ticks,
                          fb->report_ticks);
    if (!fb->poll_ticks || !fb->report_ticks)
        return;
    sched_add_timer(&fb->time);
}
DECL_COMMAND(command_filament_blockage_start,
             "filament_blockage_start oid=%c clock=%u poll_ticks=%u"
             " report_ticks=%u distance_per_edge_um=%u");

void
filament_blockage_task(void)
{
    if (!sched_check_wake(&filament_blockage_wake))
        return;

    uint8_t oid;
    struct filament_blockage *fb;
    foreach_oid(oid, fb, command_config_filament_blockage) {
        if (!(fb->flags & FBF_PENDING))
            continue;
        irq_disable();
        if (!(fb->flags & FBF_PENDING)) {
            irq_enable();
            continue;
        }
        fb->flags &= ~FBF_PENDING;
        uint32_t report_clock = fb->time.waketime;
        uint32_t measured_um = fb->measured_um;
        uint32_t edge_count = fb->edge_count;
        uint8_t pin_state = fb->last_pin_state;
        irq_enable();
        sendf("filament_blockage_state oid=%c clock=%u measured_um=%u"
              " edge_count=%u pin_state=%c",
              fb->oid, report_clock, measured_um, edge_count, pin_state);
    }
}
DECL_TASK(filament_blockage_task);
