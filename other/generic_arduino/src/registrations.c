/**
 * registrations.c - Explicit list of all DECL_INIT / DECL_TASK / DECL_SHUTDOWN
 *
 * Because generic_arduino does not have the Kalico build script to
 * extract these from object files, we maintain them manually here.
 *
 * When you add a new DECL_INIT(), DECL_TASK(), or DECL_SHUTDOWN()
 * in your source files, add the function to the appropriate list below.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <stddef.h>

// ============================================================================
// Known init functions (called once at startup, in order)
// ============================================================================

extern void alloc_init(void);       // from basecmd.c
extern void arduino_serial_init(void);  // from arduino/serial.c
extern void arduino_timer_init(void);   // from arduino/timer.c

// NOTE: timer_init() from generic/timer_irq.c is NOT included here
// because arduino_timer_init() replaces it on Arduino.

typedef void (*init_func_t)(void);
init_func_t ctr_init_list[] = {
    alloc_init,
    arduino_serial_init,
    arduino_timer_init,
};
const unsigned int ctr_init_count = sizeof(ctr_init_list) / sizeof(ctr_init_list[0]);

// ============================================================================
// Known task functions (called periodically in the main loop)
// ============================================================================

typedef void (*task_func_t)(void);

// From generic/serial_irq.c:
extern void console_task(void);

// From generic/timer_irq.c:
extern void timer_task(void);

task_func_t ctr_task_list[] = {
    console_task,
    timer_task,
};
const unsigned int ctr_task_count = sizeof(ctr_task_list) / sizeof(ctr_task_list[0]);

// ============================================================================
// Known shutdown functions (called on emergency stop)
// ============================================================================

// From command.c:
extern void sendf_shutdown(void);

typedef void (*shutdown_func_t)(void);
shutdown_func_t ctr_shutdown_list[] = {
    sendf_shutdown,
};
const unsigned int ctr_shutdown_count = sizeof(ctr_shutdown_list) / sizeof(ctr_shutdown_list[0]);
