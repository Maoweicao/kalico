// Verify the mechanism used by the closed loop position controller.
//
// The step time solver reads the stepper reference position (the
// "commanded_pos" of the stepper kinematics) once at the start of a
// trapezoid segment.  The number of steps generated for that segment is
// (segment_end_position - reference) / step_dist, so lowering the
// reference makes the stepper travel an additional distance.
//
// The closed loop controller uses this to move a stepper further than the
// planned trajectory so that the load catches up with the commanded
// position.
//
// The additional steps are all emitted at the very start of the segment
// (the position function of the segment starts above the lowered
// reference, so the intermediate step targets are not reachable and the
// solver collapses them onto the segment start).  The step compressor
// cannot deliver steps that are closer together than its timing error
// tolerance, so only a small re-anchor is safe.  This test determines
// that limit.

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>

#include "compiler.h"
#include "pyhelper.h"
#include "msgblock.h"
#include "serialqueue.h"
#include "list.h"
#include "stepcompress.h"
#include "trapq.h"
#include "itersolve.h"

// Minimal stubs - the real pyhelper.c is not needed for this test and it
// is not portable to all host platforms
void
errorf(const char *fmt, ...)
{
}

void
report_errno(char *where, int rc)
{
}

// The serialqueue is not used by this test - the steps are never sent to
// a microcontroller.  Stub out the entry points that stepcompress.c uses.
struct command_queue *
serialqueue_alloc_commandqueue(void)
{
    return NULL;
}

void
serialqueue_free_commandqueue(struct command_queue *cq)
{
}

void
serialqueue_send_batch(struct serialqueue *sq, struct command_queue *cq
                        , struct list_head *msgs)
{
}

#include "msgblock.c"
#include "stepcompress.c"
#include "itersolve.c"
#include "trapq.c"
#include "kin_cartesian.c"

#define STEP_DIST 0.0125
#define TRAVEL 100.0
// Realistic mcu parameters - a 72MHz clock and the 25us step compress
// error tolerance used by Klipper
#define MCU_FREQ 72000000.
#define MAX_ERROR_TICKS 1800

// The largest re-anchor (in steps) that the step compressor is able to
// deliver.  The closed loop controller must not exceed this.
#define MAX_REANCHOR_STEPS 2

// Generate the steps for two consecutive moves and return the number of
// steps generated for the second move.  The second move is the one that
// carries the re-anchored reference - this matches the real situation
// where the machine is already running when a correction is applied.
static int
count_steps(double travel, double reference, int *out_err)
{
    *out_err = 0;
    struct trapq *tq = trapq_alloc();
    struct stepcompress *sc = stepcompress_alloc(0);
    stepcompress_fill(sc, MAX_ERROR_TICKS, 1, 2);
    stepcompress_set_time(sc, 0., MCU_FREQ);
    struct stepper_kinematics *sk = cartesian_stepper_alloc('x');
    itersolve_set_trapq(sk, tq);
    itersolve_set_stepcompress(sk, sc, STEP_DIST);
    itersolve_set_position(sk, 0., 0., 0.);
    // First move - establishes the step clock of a running machine
    trapq_append(tq, 100.0, 0., 1.0, 0.,
                 0., 0., 0., 1., 0., 0., 100., 100., 1000.);
    itersolve_generate_steps(sk, 200.);
    queue_flush(sc, UINT64_MAX);
    int64_t first = stepcompress_find_past_position(sc, UINT64_MAX);
    // Second move - carries the re-anchored reference.  The reference is
    // the position of the end of the first move (TRAVEL) lowered by the
    // requested correction.
    if (reference != 0.)
        itersolve_set_commanded_pos(sk, TRAVEL + reference);
    trapq_append(tq, 200.0, 0., 1.0, 0.,
                 TRAVEL, 0., 0., 1., 0., 0., 100., 100., 1000.);
    itersolve_generate_steps(sk, 300.);
    int ret = queue_flush(sc, UINT64_MAX);
    if (ret)
        *out_err = ret;
    int64_t total = stepcompress_find_past_position(sc, UINT64_MAX);
    itersolve_set_trapq(sk, NULL);
    stepcompress_free(sc);
    trapq_free(tq);
    return (int)(total - first);
}

static int failures = 0;

static void
check(const char *name, int got, int expect, int tol)
{
    int ok = abs(got - expect) <= tol;
    if (!ok)
        failures++;
    printf("%-44s got=%-8d expect=%-8d %s\n", name, got, expect,
           ok ? "OK" : "FAIL");
}

int
main(void)
{
    int err = 0;
    int base = count_steps(TRAVEL, 0., &err);
    check("steps for a 100mm move", base, (int)lround(TRAVEL / STEP_DIST),
          2);
    check("baseline has no compressor error", err, 0, 0);

    // A re-anchor of N steps must produce exactly N additional steps
    printf("\nre-anchor sweep:\n");
    int steps[] = {1, 2, 3, 4, 8, 40};
    for (unsigned i = 0; i < sizeof(steps) / sizeof(steps[0]); i++) {
        double delta = steps[i] * STEP_DIST;
        int e1 = 0;
        int got = count_steps(TRAVEL, -delta, &e1);
        printf("  %4d steps (%7.4fmm) extra=%+6d compressor_err=%d\n",
               steps[i], delta, got - base, e1);
        if (steps[i] <= MAX_REANCHOR_STEPS) {
            check("  re-anchor delivers the extra steps", got - base,
                  steps[i], 1);
            check("  re-anchor has no compressor error", e1, 0, 0);
        }
    }
    if (failures) {
        printf("FAILED (%d)\n", failures);
        return 1;
    }
    printf("PASSED\n");
    return 0;
}
