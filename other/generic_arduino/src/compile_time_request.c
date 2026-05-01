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
// discover all other commands. We implement a minimal identify
// response containing just enough information for connection.

static void
command_identify(uint32_t *args)
{
    uint32_t offset = args[0];
    uint8_t count = args[1];

    // Send back identify_response with empty data dictionary
    // (host will still connect, just won't know any commands)
    // A minimal JSON identify payload:
    static const char identify_json[] =
        "{"
        "\"commands\": ["
        "  \"identify offset=%u count=%c\""
        "],"
        "\"responses\":["
        "  \"identify_response offset=%u data=%.*s\""
        "],"
        "\"version\":\"generic_arduino 1.0\","
        "\"build_versions\":\"\","
        "\"config\": {"
        "  \"CLOCK_FREQ\": \"16000000\","
        "  \"MCU\": \"arduino\","
        "  \"SERIAL_BAUD\": \"250000\","
        "  \"RECEIVE_WINDOW\": \"192\""
        "}"
        "}";

    const char *data = identify_json;
    uint32_t data_len = sizeof(identify_json) - 1;

    if (offset >= data_len) {
        count = 0; // Nothing to send
    } else if (offset + count > data_len) {
        count = data_len - offset;
    }

    sendf("identify_response offset=%u data=%.*s",
          offset, count, data + offset);
}

// ============================================================================
// Command index — maps command IDs to handler functions
// ============================================================================

// Hardcoded command parsers. In the full build, this array is generated
// by scripts/buildcommand.py from DECL_COMMAND declarations.

// Parameter types for "identify offset=%u count=%c"
static const uint8_t identify_param_types[] = {
    PT_uint32,  // offset
    PT_byte,    // count
};

static const struct command_parser __identify_parser PROGMEM = {
    .encoded_msgid = 1,  // msgid for "identify"
    .num_args = 2,
    .flags = 0,
    .num_params = 2,
    .param_types = identify_param_types,
    .func = command_identify,
};

// Parameter types for "identify_response offset=%u data=%.*s"
static const uint8_t identify_response_param_types[] = {
    PT_uint32,           // offset
    PT_progmem_buffer,   // data
};

// Command index: array of all registered command parsers.
// Index 0 = identify_response (output only)
// Index 1 = identify
const struct command_parser command_index[] PROGMEM = {
    [0] = {  // identify_response — output only, not dispatched
        .encoded_msgid = 0,
        .num_args = 0,
        .flags = 0,
        .num_params = 2,
        .param_types = identify_response_param_types,
        .func = NULL,  // Not called — output encoding only
    },
    [1] = __identify_parser,
};

const uint16_t command_index_size = sizeof(command_index) / sizeof(command_index[0]);

// ============================================================================
// Identify data (zlib-compressed JSON sent to the host)
// ============================================================================

const uint8_t command_identify_data[] = {
    // No additional compressed data needed for the basic identify.
    // In the full build, this is zlib-compressed JSON enumerating all
    // commands, responses, constants, and enumerations.
};
const uint32_t command_identify_size = 0;

// ============================================================================
// Encoder lookup stubs
// ============================================================================

// These are needed for sendf() and output() macros.
// In the full build, these are generated from the command declarations.

static const uint8_t identify_response_encoder_types[] = {
    PT_uint32,           // offset
    PT_progmem_buffer,   // data
};

static const struct command_encoder __identify_response_encoder PROGMEM = {
    .encoded_msgid = 0,
    .max_size = 64,
    .num_params = 2,
    .param_types = identify_response_encoder_types,
};

const struct command_encoder *
ctr_lookup_encoder(const char *str)
{
    // Only "identify_response offset=%u data=%.*s" is supported
    return &__identify_response_encoder;
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
