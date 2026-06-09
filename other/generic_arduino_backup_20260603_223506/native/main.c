// native/main.c — entry point for host-native Kalico MCU build
//
// Compiles the Kalico MCU protocol layer as a native executable.
// Uses TCP sockets for serial communication — kalico_debug_tool
// can connect via `tcp:127.0.0.1:<port>`.
//
// SPDX-License-Identifier: GPL-3.0-or-later

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include "autoconf.h"
#include "serial_native.h"

// Kalico core entry point (defined in src/sched.c)
extern void sched_main(void);

// Exit flag (set by signal handler)
static volatile int g_running = 1;

static void signal_handler(int sig) {
    (void)sig;
    g_running = 0;
}

int main(int argc, char *argv[]) {
    int port = 0;  // 0 = auto-assign

    // Parse --port argument
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "--port") == 0 && i + 1 < argc) {
            port = atoi(argv[i + 1]);
            i++;
        } else if (strcmp(argv[i], "--help") == 0 || strcmp(argv[i], "-h") == 0) {
            printf("Usage: %s [--port PORT]\n", argv[0]);
            printf("\n");
            printf("  --port PORT  TCP port to listen on (default: 0 = auto-assign)\n");
            printf("\n");
            printf("Kalico MCU protocol native build.\n");
            printf("Connect with: kalico_debug_tool connect tcp:127.0.0.1:<port>\n");
            return 0;
        }
    }

    // Setup signal handlers for graceful shutdown
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    printf("=== Kalico native MCU firmware ===\n");
    printf("Clock: %lu Hz\n", (unsigned long)CONFIG_CLOCK_FREQ);

    // Initialize TCP serial server
    int actual_port = native_serial_init(port);
    if (actual_port < 0) {
        fprintf(stderr, "FATAL: Failed to initialize serial server\n");
        return 1;
    }

    printf("[INIT] Platform initialized (port=%d).\n", actual_port);
    printf("[INIT] Entering Kalico scheduler loop...\n");
    printf("Connect with: kalico_debug_tool connect tcp:127.0.0.1:%d\n", actual_port);

    // Run the Kalico cooperative scheduler
    // sched_main() contains its own infinite loop but calls
    // irq_poll() → native_serial_poll_rx() periodically
    sched_main();

    // Should never reach here
    printf("[FATAL] sched_main returned!\n");
    native_serial_shutdown();
    return 1;
}
