/**
 * compile_time_request.c - Stub for Kalico compile-time request system
 *
 * In the full Kalico build system, scripts/buildcommand.py extracts
 * DECL_CTR strings from object files and generates this file automatically.
 *
 * For generic_arduino, we provide a hardcoded version that supports
 * the essential identify handshake. Run `python scripts/generate_ctr.py`
 * to generate a complete version from your source files.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "command.h"
#include "sched.h"
#include "board/pgm.h"
#include <stddef.h>

// ============================================================================
// Forward declarations of command handlers
// ============================================================================

// These are defined in the source files using DECL_COMMAND().
// The DECL_COMMAND macro in command.h places their metadata into the
// .compile_time_request section, which the build script processes.

// For now, we manually register the handlers we know about.
// When you add new commands, add their handler here.
extern void console_task(void);       // from generic/serial_irq.c
extern void timer_task(void);         // from generic/timer_irq.c

// ============================================================================
// identify command — the only hardcoded command
// ============================================================================

// identify_response offset=%u data=%.*s (msgid=0)
// identify offset=%u count=%c              (msgid=1)
//
// These are the two hardcoded message IDs that allow the host to
// discover all other commands.

// NOTE: command_identify() lives in basecmd.c — it reads from
// command_identify_data[].  Do NOT define a duplicate here; the linker
// would pick one arbitrarily and Klipper gets garbage or empty data.

// ============================================================================
// Command index — maps command IDs to handler functions
// ============================================================================

// Handlers declared in other source files:
extern void command_identify(uint32_t *args);     // from basecmd.c
extern void command_clear_shutdown(uint32_t *args); // from basecmd.c

// Parameter types for "identify_response offset=%u data=%.*s" (output only)
static const uint8_t identify_response_param_types[] = {
    PT_uint32,           // offset
    PT_progmem_buffer,   // data
};

// Parameter types for "identify offset=%u count=%c"
static const uint8_t identify_param_types[] = {
    PT_uint32,  // offset
    PT_byte,    // count
};

// Parameter types for "clear_shutdown" (0 params)
static const uint8_t clear_shutdown_param_types[] = {
    // no parameters
};

// Command index: array of all registered command parsers.
// Index 0 = identify_response (output only, not dispatched)
// Index 1 = identify
// Index 2 = clear_shutdown
const struct command_parser command_index[] = {
    [0] = {
        .encoded_msgid = 0,
        .num_args = 0,
        .flags = 0,
        .num_params = 2,
        .param_types = identify_response_param_types,
        .func = NULL,
    },
    [1] = {
        .encoded_msgid = 1,
        .num_args = 2,
        .flags = HF_IN_SHUTDOWN,        // identify works even in shutdown
        .num_params = 2,
        .param_types = identify_param_types,
        .func = command_identify,
    },
    [2] = {
        .encoded_msgid = 2,
        .num_args = 0,
        .flags = HF_IN_SHUTDOWN,
        .num_params = 0,
        .param_types = clear_shutdown_param_types,
        .func = command_clear_shutdown,
    },
};

const uint16_t command_index_size = sizeof(command_index) / sizeof(command_index[0]);

// ============================================================================
// Identify data — zlib-compressed JSON sent to the host
// ============================================================================
//
// Klipper expects this to be zlib-compressed.  Decompressed contents:
// {"commands":{"identify offset=%u count=%c":1,"clear_shutdown":2},
//  "responses":{"identify_response offset=%u data=%.*s":0,"starting":3,
//   "shutdown clock=%u static_string_id=%hu":4,
//   "is_shutdown static_string_id=%hu":5},
//  "config":{"CLOCK_FREQ":16000000,"MCU":"arduino","SERIAL_BAUD":250000,
//   "RECEIVE_WINDOW":192},
//  "constants":{"SERIAL_BAUD":250000,"RECEIVE_WINDOW":192,"CLOCK_FREQ":16000000},
//  "version":"generic_arduino 1.0","build_versions":""}
//
// Generated with: python -c "import zlib,json; d=...; print(zlib.compress(json.dumps(d).encode()))"

const uint8_t command_identify_data[] = {
    0x78, 0xda, 0x8d, 0x90, 0x5b, 0x4b, 0xc3, 0x30, 0x14, 0xc7, 0xbf, 0x4a,
    0x39, 0xd0, 0x17, 0x09, 0xa3, 0x9b, 0x4e, 0x30, 0xd0, 0x87, 0xd9, 0x55,
    0x28, 0x4e, 0x87, 0x95, 0xb9, 0xc7, 0x90, 0x25, 0x69, 0x17, 0xec, 0x12,
    0xc9, 0x45, 0x91, 0xb1, 0xef, 0xee, 0xd9, 0x56, 0x87, 0x82, 0xc2, 0xf2,
    0x94, 0xcb, 0xef, 0xfc, 0x2f, 0xd9, 0x82, 0xb0, 0x9b, 0x0d, 0x37, 0xd2,
    0x03, 0xdd, 0x82, 0x96, 0xca, 0x04, 0xdd, 0x7c, 0x26, 0xb6, 0x69, 0xbc,
    0x0a, 0x79, 0x1a, 0x13, 0x61, 0xa3, 0xc1, 0x8d, 0x00, 0x3a, 0x24, 0x20,
    0x3a, 0xc5, 0x1d, 0xf3, 0xeb, 0x18, 0xa4, 0xfd, 0x30, 0x40, 0x47, 0x3b,
    0x02, 0x4e, 0xf9, 0x37, 0x6b, 0xbc, 0xfa, 0x25, 0xc0, 0xbe, 0x6f, 0x7f,
    0x28, 0x49, 0x1e, 0x78, 0x9e, 0x0e, 0x2e, 0x10, 0xcc, 0x08, 0xf8, 0xc0,
    0x5d, 0xd0, 0xa6, 0x05, 0x7a, 0x89, 0x87, 0x5e, 0x31, 0x11, 0x9d, 0x15,
    0xaf, 0x7b, 0x18, 0x9f, 0x83, 0x16, 0xcc, 0x07, 0x87, 0x0c, 0xd3, 0x32,
    0x4f, 0xd7, 0x11, 0xe8, 0x15, 0x01, 0xed, 0x4f, 0xfe, 0xff, 0x40, 0x63,
    0x0c, 0x25, 0xac, 0x69, 0x74, 0xbb, 0x4f, 0x54, 0xcc, 0xe6, 0xc5, 0x3d,
    0xbb, 0xab, 0xcb, 0x27, 0x6c, 0x70, 0x9d, 0x1d, 0x16, 0x81, 0x87, 0x62,
    0x01, 0x14, 0xb8, 0x93, 0x51, 0x1b, 0x0b, 0x04, 0x9e, 0xcb, 0xba, 0x9a,
    0xcc, 0xd8, 0xed, 0x64, 0x31, 0xc5, 0x56, 0xe3, 0x23, 0x54, 0x97, 0x45,
    0x59, 0xbd, 0x94, 0x6c, 0x59, 0x3d, 0x4e, 0xe7, 0x4b, 0x1c, 0xbf, 0x19,
    0x1d, 0xa5, 0xd1, 0xd7, 0x84, 0x43, 0xdf, 0x73, 0xe7, 0xc8, 0x9f, 0x39,
    0x50, 0xed, 0x5d, 0x39, 0xaf, 0x2d, 0x7e, 0x25, 0xb4, 0xca, 0x28, 0x87,
    0x6d, 0xfa, 0x50, 0xc9, 0x70, 0x90, 0x61, 0xb0, 0x55, 0xd4, 0x9d, 0x64,
    0x3d, 0x85, 0x96, 0x00, 0xbb, 0x2f, 0xdc, 0xe7, 0x8b, 0x3c,
};
const uint32_t command_identify_size = 262;

// ============================================================================
// Encoder lookup stubs (superseded by the full encoder definitions below)
// ============================================================================
// Encoder definitions for all firmware messages
// ============================================================================
//
// Each `sendf()` call in the code needs a matching encoder so the binary
// message framing (msgid, header/trailer, parameter encoding) is correct.
// Without this, `sendf()` reads garbage from the stack and crashes the MCU.
//
// msgid assignments (sequential in order of definition):
//   0 = identify_response      (output, 2 params)
//   1 = identify               (input command, 2 params)
//   2 = starting               (output, 0 params — boot announcement)
//   3 = shutdown               (output, 2 params)
//   4 = is_shutdown             (output, 1 param)
//
// ============================================================================

// ---- "starting" (0 params) -------------------------------------------------
static const uint8_t starting_encoder_types[] = {
    // no parameters
};

static const struct command_encoder __starting_encoder = {
    .encoded_msgid = 2,
    .max_size = MESSAGE_MIN,       // header + trailer only (5 bytes)
    .num_params = 0,
    .param_types = starting_encoder_types,
};

// ---- "identify_response offset=%u data=%.*s" (2 params) --------------------
static const uint8_t identify_response_encoder_types[] = {
    PT_uint32,           // offset
    PT_progmem_buffer,   // data
};

static const struct command_encoder __identify_response_encoder = {
    .encoded_msgid = 0,
    .max_size = 64,
    .num_params = 2,
    .param_types = identify_response_encoder_types,
};

// ---- "shutdown clock=%u static_string_id=%hu" (2 params) -------------------
static const uint8_t shutdown_encoder_types[] = {
    PT_uint32,           // clock
    PT_uint16,           // static_string_id
};

static const struct command_encoder __shutdown_encoder = {
    .encoded_msgid = 3,
    .max_size = 32,
    .num_params = 2,
    .param_types = shutdown_encoder_types,
};

// ---- "is_shutdown static_string_id=%hu" (1 param) --------------------------
static const uint8_t is_shutdown_encoder_types[] = {
    PT_uint16,           // static_string_id
};

static const struct command_encoder __is_shutdown_encoder = {
    .encoded_msgid = 4,
    .max_size = 16,
    .num_params = 1,
    .param_types = is_shutdown_encoder_types,
};

// ---- Encoder lookup --------------------------------------------------------

const struct command_encoder *
ctr_lookup_encoder(const char *str)
{
    // Match the format string and return the correct encoder.
    // WITHOUT this proper matching, sendf() encodes garbage and crashes.
    if (str[0] == 's') {
        if (str[1] == 't')
            return &__starting_encoder;            // "starting"
        if (str[1] == 'h')
            return &__shutdown_encoder;            // "shutdown clock=..."
    }
    if (str[0] == 'i') {
        if (str[1] == 'd')
            return &__identify_response_encoder;   // "identify_response ..."
        if (str[1] == 's')
            return &__is_shutdown_encoder;         // "is_shutdown ..."
    }
    // Fallback: return a minimal encoder (MESSAGE_MIN = ack size = 5 bytes)
    // This prevents crashes but hosts may not recognize the message.
    return &__starting_encoder;
}

const struct command_encoder *
ctr_lookup_output(const char *str)
{
    // No output() messages registered
    return NULL;
}

uint8_t
ctr_lookup_static_string(const char *str)
{
    // Static strings for shutdown() messages
    // Return a dummy ID (0)
    return 0;
}
