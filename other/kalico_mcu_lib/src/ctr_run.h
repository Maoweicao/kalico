/**
 * ctr_run.h - Task/init/shutdown registration macros (Arduino port)
 *
 * In the full Kalico build, these macros use DECL_CTR to place strings
 * in the .compile_time_request section for the build script to process.
 *
 * In generic_arduino, we use explicit registration via registrations.c.
 * The macros below are no-ops that serve only as documentation markers.
 * When you add a new DECL_TASK(func), also add unc to registrations.c.
 */

#ifndef __CTR_RUN_H
#define __CTR_RUN_H

#include <stdint.h>

// === Registration macros (documentation markers) ===

#define DECL_INIT(FUNC)    /* See registrations.c */
#define DECL_TASK(FUNC)    /* See registrations.c */
#define DECL_SHUTDOWN(FUNC) /* See registrations.c */

// === Runner functions (implemented in ctr_run.c) ===

void ctr_run_initfuncs(void);
void ctr_run_taskfuncs(void);
void ctr_run_shutdownfuncs(void);

#endif // __CTR_RUN_H
