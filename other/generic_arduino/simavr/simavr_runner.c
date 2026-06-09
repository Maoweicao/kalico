/**
 * simavr_runner.c - Kalico generic_arduino simavr simulation runner
 *
 * Loads ATmega2560 firmware and exposes:
 *   - UART0 -> simavr built-in console (stdout)
 *   - UART1 -> PTY (via uart_pty) for Klipper host connection
 *
 * Usage:
 *   ./simavr_runner ../.pio/build/mega2560/firmware.hex
 *
 * The UART1 PTY slave path is printed on startup.  uart_pty_connect()
 * also auto-creates /tmp/simavr-uartN symlink.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <signal.h>

#include "sim/sim_avr.h"
#include "sim/sim_hex.h"
#include "sim/sim_gdb.h"
#include "uart_pty.h"

static avr_t *g_avr = NULL;
static int g_running = 1;
static uart_pty_t uart1_pty;

static void signal_handler(int sig) {
    (void)sig;
    g_running = 0;
}

int main(int argc, char *argv[]) {
    const char *firmware_path = NULL;
    const char *mcu_name = "atmega2560";
    uint32_t freq = 16000000;
    int gdb_port = 0;

    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "--help") || !strcmp(argv[i], "-h")) {
            printf("Usage: %s [options] <firmware.hex>\n", argv[0]);
            printf("Options:\n");
            printf("  --mcu NAME    MCU type (default: atmega2560)\n");
            printf("  --freq HZ     Clock frequency (default: 16000000)\n");
            printf("  --gdb [PORT]  Enable GDB (default port: 1234)\n");
            return 0;
        } else if (!strcmp(argv[i], "--mcu") && i+1 < argc) {
            mcu_name = argv[++i];
        } else if (!strcmp(argv[i], "--freq") && i+1 < argc) {
            freq = (uint32_t)atol(argv[++i]);
        } else if (!strcmp(argv[i], "--gdb")) {
            gdb_port = (i+1 < argc && argv[i+1][0] != '-') ? atoi(argv[++i]) : 1234;
        } else {
            firmware_path = argv[i];
        }
    }

    if (!firmware_path) {
        fprintf(stderr, "ERROR: No firmware specified.\n");
        return 1;
    }

    // Create AVR core
    g_avr = avr_make_mcu_by_name(mcu_name);
    if (!g_avr) {
        fprintf(stderr, "ERROR: Failed to create AVR core '%s'\n", mcu_name);
        return 1;
    }
    avr_init(g_avr);
    g_avr->frequency = freq;
    g_avr->log = 2;

    // Load firmware
    uint32_t boot_size, boot_base;
    uint8_t *boot = read_ihex_file(firmware_path, &boot_size, &boot_base);
    if (!boot) {
        fprintf(stderr, "ERROR: Failed to load firmware\n");
        return 1;
    }
    memcpy(g_avr->flash + boot_base, boot, boot_size);
    free(boot);
    g_avr->pc = boot_base;
    g_avr->codeend = g_avr->flashend;

    // Connect UART1 to PTY for Klipper communication
    uart_pty_init(g_avr, &uart1_pty);
    uart_pty_connect(&uart1_pty, '1');
    /* uart_pty_connect auto-creates /tmp/simavr-uartN symlink
       and disables AVR_UART_FLAG_STDIO on this UART */

    // GDB
    if (gdb_port > 0) {
        g_avr->gdb_port = gdb_port;
        g_avr->state = cpu_Stopped;
        avr_gdb_init(g_avr);
    }

    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    printf("\n");
    printf("============================================================\n");
    printf("  Kalico MCU Simulator (simavr + %s)\n", mcu_name);
    printf("============================================================\n");
    printf("  Firmware  : %s\n", firmware_path);
    printf("  MCU       : %s @ %lu Hz\n", mcu_name, (unsigned long)freq);
    printf("\n");
    printf("  UART0 (debug) -> simavr console (stdout)\n");
    printf("  UART1 (MCU)   -> %s\n", uart1_pty.port[0].slavename);
    printf("    symlink: /tmp/simavr-uart1\n");
    printf("\n");
    printf("  klippy config:\n");
    printf("    [mcu]\n");
    printf("    serial: %s\n", uart1_pty.port[0].slavename);
    printf("    baud: 250000\n");
    printf("    restart_method: none\n");
    printf("\n");
    printf("  Press Ctrl+C to stop.\n");
    printf("============================================================\n");
    fflush(stdout);

    // Run simulation
    while (g_running) {
        int state = avr_run(g_avr);
        if (state == cpu_Done || state == cpu_Crashed) {
            fprintf(stderr, "\n[SIMAVR] CPU state=%d at pc=0x%05x\n",
                    state, g_avr->pc);
            break;
        }
    }

    printf("\n[SIMAVR] Shutting down...\n");
    uart_pty_stop(&uart1_pty);
    return 0;
}
