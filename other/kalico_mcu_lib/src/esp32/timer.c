/**
 * esp32/timer.c - ISR-native timer dispatch for ESP32
 *
 * Uses the legacy ESP-IDF timer driver (driver/timer.h) with
 * compare-match interrupt to directly call timer_dispatch_many(),
 * achieving the same ISR-native dispatch as AVR Timer1 COMPA
 * and STM32 TIM2.
 *
 * All ISR-path functions are IRAM_ATTR to avoid flash cache miss delays.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"
#include "irq.h"
#include "misc.h"
#include "internal.h"
#include "../command.h"
#include "../sched.h"

/* ESP-IDF legacy timer driver */
#include "driver/timer.h"
#include "esp_attr.h"

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

/* ---- Hardware constants ---- */
/* ESP32 APB clock = 80MHz. With divider=80, timer runs at 1MHz (1µs tick).
 * CONFIG_CLOCK_FREQ=1000000 matches this. */
#define TIMER_GROUP_NUM   TIMER_GROUP_0
#define TIMER_IDX         TIMER_0
#define TIMER_DIVIDER     80
#define TIMER_SCALE       (TIMER_BASE_CLK / TIMER_DIVIDER)  /* 1MHz = 1µs per tick */

/* ---- ISR timing constants (in timer ticks = µs) ---- */
#define TIMER_MIN_TRY_TICKS      2
#define TIMER_DEFER_REPEAT_TICKS 5
#define TIMER_REPEAT_TICKS       100

/* ---- Hardware timer read ---- */
uint32_t IRAM_ATTR
timer_read_time(void)
{
    uint64_t val = 0;
    timer_get_counter_value(TIMER_GROUP_NUM, TIMER_IDX, &val);
    return (uint32_t)val;
}

/* ---- Timer kick: activate dispatch as soon as possible ---- */
void IRAM_ATTR
timer_kick(void)
{
    uint32_t now = timer_read_time();
    timer_set_alarm_value(TIMER_GROUP_NUM, TIMER_IDX, now + 50);
    timer_set_alarm(TIMER_GROUP_NUM, TIMER_IDX, TIMER_ALARM_EN);
}

/* ---- Timer kick next: schedule interrupt at specific time ---- */
void IRAM_ATTR
timer_kick_next(uint32_t next_time)
{
    timer_set_alarm_value(TIMER_GROUP_NUM, TIMER_IDX, next_time);
    timer_set_alarm(TIMER_GROUP_NUM, TIMER_IDX, TIMER_ALARM_EN);
}

/* ---- Timer ISR: core realtime dispatch ---- */
static bool IRAM_ATTR
timer_group_isr(void *arg)
{
    /* Clear interrupt status */
    timer_group_clr_intr_status_in_isr(TIMER_GROUP_NUM, TIMER_IDX);

    /* Re-enable alarm for next event */
    timer_group_enable_alarm_in_isr(TIMER_GROUP_NUM, TIMER_IDX);

    /* Directly call timer_dispatch_many() — same path as AVR/STM32 */
    uint32_t next = timer_dispatch_many();

    /* Schedule next alarm */
    timer_set_alarm_value(TIMER_GROUP_NUM, TIMER_IDX, next);
    timer_set_alarm(TIMER_GROUP_NUM, TIMER_IDX, TIMER_ALARM_EN);

    return false;  /* No task yield needed */
}

/* ---- Initialization ---- */
void
arduino_timer_init(void)
{
    static bool initialized = false;
    if (initialized)
        return;
    initialized = true;

    /* Configure timer: 80MHz / 80 = 1MHz (1µs resolution), count up */
    timer_config_t config = {
        .alarm_en = TIMER_ALARM_EN,
        .counter_en = TIMER_START,
        .intr_type = TIMER_INTR_LEVEL,
        .counter_dir = TIMER_COUNT_UP,
        .auto_reload = TIMER_AUTORELOAD_DIS,
        .divider = TIMER_DIVIDER,
    };
    timer_init(TIMER_GROUP_NUM, TIMER_IDX, &config);

    /* Set initial alarm */
    timer_set_alarm_value(TIMER_GROUP_NUM, TIMER_IDX, 50);

    /* Register ISR callback */
    timer_isr_callback_add(TIMER_GROUP_NUM, TIMER_IDX,
                           timer_group_isr, NULL,
                           ESP_INTR_FLAG_IRAM);

    /* Start timer */
    timer_start(TIMER_GROUP_NUM, TIMER_IDX);
}

/* ---- ISR-native mode: poll functions not used ---- */

bool IRAM_ATTR
arduino_timer_irq_pending(void)
{
    return false;
}

void IRAM_ATTR
arduino_timer_irq_clear(void)
{
    /* No-op: ISR handles everything */
}
