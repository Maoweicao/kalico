/**
 * ctr_run.c - Runtime execution of registered init/task/shutdown functions
 *
 * Uses the explicit lists from registrations.c, since the Arduino
 * build does not support the original compile_time_request system.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "registrations.c"  // Include the explicit lists

// These functions are called by sched.c (sched_main / run_tasks / run_shutdown)

void
ctr_run_initfuncs(void)
{
    for (unsigned int i = 0; i < ctr_init_count; i++) {
        ctr_init_list[i]();
    }
}

void
ctr_run_taskfuncs(void)
{
    for (unsigned int i = 0; i < ctr_task_count; i++) {
        ctr_task_list[i]();
    }
}

void
ctr_run_shutdownfuncs(void)
{
    for (unsigned int i = 0; i < ctr_shutdown_count; i++) {
        ctr_shutdown_list[i]();
    }
}
