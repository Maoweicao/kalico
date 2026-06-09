// Support for reading quadrature encoders via GPIO pins
//
// Copyright (C) 2024  Kalico Contributors
//
// This file may be distributed under the terms of the GNU GPLv3 license.

#include "basecmd.h"       // oid_alloc, oid_lookup
#include "board/gpio.h"    // gpio_in_setup, gpio_in_read
#include "board/irq.h"     // irq_disable, irq_enable
#include "command.h"       // DECL_COMMAND
#include "sched.h"         // DECL_TASK, sched_wake_task
#include "sensor_bulk.h"   // sensor_bulk_report, sensor_bulk_reset

enum { QE_STATE_00, QE_STATE_01, QE_STATE_10, QE_STATE_11 };
enum { QE_PENDING = 1<<0 };

#define QE_BYTES_PER_SAMPLE 4

struct quadrature_encoder {
    struct timer timer;
    uint32_t rest_ticks;
    struct gpio_in pin_a, pin_b;
    uint8_t state, flags;
    int32_t position;
    struct sensor_bulk sb;
};

static struct task_wake quad_enc_wake;

// Quadrature transition tables
// From 00 (0): forward->01 (1), reverse->10 (2)
// From 01 (1): forward->11 (3), reverse->00 (0)
// From 10 (2): forward->00 (0), reverse->11 (3)
// From 11 (3): forward->10 (2), reverse->01 (1)
static const uint8_t quad_next_fwd[4] = {
    QE_STATE_01, QE_STATE_11, QE_STATE_00, QE_STATE_10
};
static const uint8_t quad_next_rev[4] = {
    QE_STATE_10, QE_STATE_00, QE_STATE_11, QE_STATE_01
};

static uint_fast8_t
quad_enc_event(struct timer *timer)
{
    struct quadrature_encoder *qe = container_of(
        timer, struct quadrature_encoder, timer);
    qe->flags |= QE_PENDING;
    sched_wake_task(&quad_enc_wake);
    qe->timer.waketime += qe->rest_ticks;
    return SF_RESCHEDULE;
}

void
command_config_quadrature_encoder(uint32_t *args)
{
    struct quadrature_encoder *qe = oid_alloc(
        args[0], command_config_quadrature_encoder, sizeof(*qe));
    qe->timer.func = quad_enc_event;
    qe->pin_a = gpio_in_setup(args[1], 0);
    qe->pin_b = gpio_in_setup(args[2], 0);
    qe->position = 0;
    qe->state = QE_STATE_00;
}
DECL_COMMAND(command_config_quadrature_encoder,
    "config_quadrature_encoder oid=%c pin_a=%u pin_b=%u");

static void
quad_enc_do_report(struct quadrature_encoder *qe, uint8_t oid)
{
    if (qe->sb.data_count + QE_BYTES_PER_SAMPLE > ARRAY_SIZE(qe->sb.data))
        sensor_bulk_report(&qe->sb, oid);
}

void
command_query_quadrature_encoder(uint32_t *args)
{
    struct quadrature_encoder *qe = oid_lookup(
        args[0], command_config_quadrature_encoder);
    if (args[1] == 0) {
        sched_del_timer(&qe->timer);
        sensor_bulk_reset(&qe->sb);
        return;
    }
    qe->timer.waketime = args[1];
    qe->rest_ticks = args[2];
    sensor_bulk_reset(&qe->sb);
    sched_add_timer(&qe->timer);
}
DECL_COMMAND(command_query_quadrature_encoder,
    "query_quadrature_encoder oid=%c clock=%u rest_ticks=%u");

void
quadrature_encoder_task(void)
{
    if (!sched_check_wake(&quad_enc_wake))
        return;
    uint8_t oid;
    struct quadrature_encoder *qe;
    foreach_oid(oid, qe, command_config_quadrature_encoder) {
        if (!(qe->flags & QE_PENDING))
            continue;
        irq_disable();
        qe->flags = 0;
        irq_enable();

        uint8_t a = gpio_in_read(qe->pin_a);
        uint8_t b = gpio_in_read(qe->pin_b);
        uint8_t new_state = (a ? 2 : 0) | (b ? 1 : 0);

        if (new_state != qe->state) {
            if (new_state == quad_next_fwd[qe->state])
                qe->position++;
            else if (new_state == quad_next_rev[qe->state])
                qe->position--;
            qe->state = new_state;
        }

        int32_t pos = qe->position;
        qe->sb.data[qe->sb.data_count] = pos;
        qe->sb.data[qe->sb.data_count + 1] = pos >> 8;
        qe->sb.data[qe->sb.data_count + 2] = pos >> 16;
        qe->sb.data[qe->sb.data_count + 3] = pos >> 24;
        qe->sb.data_count += QE_BYTES_PER_SAMPLE;
        quad_enc_do_report(qe, oid);
    }
}
DECL_TASK(quadrature_encoder_task);
