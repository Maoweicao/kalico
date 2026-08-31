/**
 * ctr_run.c - Runtime execution of registered init/task/shutdown functions
 *
 * Uses the explicit lists from registrations.c, since the Arduino
 * build does not support the original compile_time_request system.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

// Type definitions matching registrations.c
typedef void (*init_func_t)(void);
typedef void (*task_func_t)(void);
typedef void (*shutdown_func_t)(void);

// Extern declarations for the registration lists from registrations.c
extern init_func_t ctr_init_list[];
extern const unsigned int ctr_init_count;
extern task_func_t ctr_task_list[];
extern const unsigned int ctr_task_count;
extern shutdown_func_t ctr_shutdown_list[];
extern const unsigned int ctr_shutdown_count;

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
