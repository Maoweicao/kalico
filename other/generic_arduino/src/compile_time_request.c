/**
 * compile_time_request.c - Complete command/response registry for Kalico
 *
 * Uses hash-based encoder lookup to avoid AVR linker issues with
 * string literal address resolution.
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include "command.h"
#include "sched.h"
#include "board/pgm.h"
#include "compiler.h"
#include <string.h>
#include <stddef.h>

/* Forward declarations of ALL command handlers */
extern void command_identify(uint32_t *args);
extern void command_clear_shutdown(uint32_t *args);
extern void command_emergency_stop(uint32_t *args);
extern void command_get_uptime(uint32_t *args);
extern void command_get_clock(uint32_t *args);
extern void command_finalize_config(uint32_t *args);
extern void command_get_config(uint32_t *args);
extern void command_allocate_oids(uint32_t *args);
extern void command_debug_nop(uint32_t *args);
extern void command_debug_ping(uint32_t *args);
extern void command_debug_write(uint32_t *args);
extern void command_debug_read(uint32_t *args);
extern void command_set_digital_out(uint32_t *args);
extern void command_update_digital_out(uint32_t *args);
extern void command_queue_digital_out(uint32_t *args);
extern void command_set_digital_out_pwm_cycle(uint32_t *args);
extern void command_config_digital_out(uint32_t *args);
extern void command_buttons_ack(uint32_t *args);
extern void command_buttons_query(uint32_t *args);
extern void command_buttons_add(uint32_t *args);
extern void command_config_buttons(uint32_t *args);

/* ============================================================================
 * Identify data
 * ============================================================================ */

const uint8_t command_identify_data[] PROGMEM = {
    0x78, 0xda, 0x75, 0x55, 0xdb, 0x6e, 0xdb, 0x38, 0x14, 0xfc, 0x15, 0x42,
    0x40, 0x80, 0xed, 0x22, 0x31, 0x24, 0xd9, 0x8e, 0x1b, 0x03, 0x79, 0x48,
    0x53, 0x17, 0x08, 0xb6, 0xd9, 0x6c, 0xed, 0xa4, 0x7d, 0x24, 0x18, 0xf1,
    0x58, 0x26, 0x22, 0x53, 0x2a, 0x2f, 0xce, 0x66, 0x8b, 0xfe, 0xfb, 0x0e,
    0xa9, 0x8b, 0xd5, 0x36, 0xf5, 0x8b, 0xcd, 0xc3, 0x73, 0x9f, 0x19, 0xfa,
    0x5b, 0x22, 0x9a, 0x26, 0x59, 0x26, 0x25, 0x69, 0x32, 0xaa, 0xe0, 0xc2,
    0x48, 0xaf, 0x74, 0x9d, 0x9c, 0x26, 0x8f, 0x5e, 0x55, 0x92, 0x1f, 0xc8,
    0x58, 0x55, 0x6b, 0x1b, 0x5c, 0x8a, 0x62, 0xc9, 0xfe, 0xb8, 0xfa, 0xbc,
    0xe6, 0x8b, 0xc9, 0x74, 0x92, 0x72, 0x71, 0x30, 0x67, 0x95, 0x7a, 0x2c,
    0x78, 0x3e, 0x49, 0x27, 0xe9, 0x1b, 0x16, 0xad, 0x08, 0x2c, 0xea, 0xfd,
    0x5e, 0x68, 0x89, 0x90, 0x6f, 0x89, 0xa8, 0xaa, 0xba, 0x10, 0x8e, 0x78,
    0xad, 0xa4, 0x65, 0x45, 0xed, 0xb5, 0xbb, 0x3c, 0x29, 0x92, 0xe5, 0xdb,
    0x90, 0xdf, 0x39, 0x24, 0xe6, 0xa2, 0x78, 0x62, 0xb8, 0x85, 0x79, 0x74,
    0x3f, 0x3b, 0x1f, 0x39, 0x48, 0xd9, 0x3b, 0x34, 0xb5, 0x8d, 0x5f, 0x4a,
    0x5f, 0x9e, 0x78, 0xd6, 0xf8, 0xaa, 0xe2, 0xbe, 0x69, 0x03, 0x46, 0x19,
    0xbf, 0x7a, 0x32, 0x2f, 0x43, 0x4e, 0x34, 0xf0, 0x14, 0xbc, 0x0d, 0x59,
    0xc7, 0x9d, 0x2a, 0x9e, 0x6c, 0x7b, 0x72, 0x46, 0x68, 0xbb, 0x57, 0x8e,
    0xf7, 0x55, 0x99, 0xd2, 0x98, 0xb6, 0xab, 0xbf, 0xc0, 0x1c, 0x15, 0x09,
    0xc3, 0xed, 0xce, 0x3b, 0x59, 0x3f, 0xeb, 0x64, 0x99, 0x87, 0xd1, 0xf4,
    0x56, 0x95, 0xbc, 0x2b, 0xd4, 0x97, 0x68, 0x8f, 0x7c, 0xd4, 0xfd, 0xc5,
    0xe0, 0x2a, 0x55, 0xa9, 0x9c, 0xa8, 0x78, 0xed, 0xdd, 0x30, 0x44, 0xdb,
    0xfd, 0x41, 0x54, 0x9e, 0xc2, 0x59, 0xd2, 0x56, 0xf8, 0xca, 0xf1, 0xc1,
    0xb0, 0x17, 0xff, 0x72, 0xe9, 0x8d, 0x70, 0x58, 0x3c, 0x3c, 0x93, 0x65,
    0x86, 0x6e, 0x24, 0x3d, 0xfa, 0x92, 0xeb, 0x1a, 0x60, 0x5d, 0xf4, 0x27,
    0x64, 0x2a, 0x99, 0x14, 0x4e, 0x5c, 0x9e, 0xfc, 0x89, 0x75, 0x67, 0x69,
    0x7f, 0x61, 0x48, 0x60, 0x67, 0x46, 0x92, 0x09, 0xf9, 0x2a, 0xd2, 0xb1,
    0xad, 0x2c, 0xef, 0xef, 0x9f, 0x8d, 0x72, 0x74, 0x74, 0x40, 0xe5, 0xd0,
    0x91, 0xb2, 0xbc, 0x31, 0xaa, 0x9b, 0x21, 0xcb, 0x4e, 0x13, 0xda, 0x93,
    0x01, 0x31, 0x8a, 0x17, 0x6e, 0x5d, 0x28, 0x3c, 0x3d, 0x4d, 0xb6, 0x4a,
    0x8b, 0x4a, 0xfd, 0x47, 0xbc, 0x9d, 0x8f, 0x15, 0xa6, 0x88, 0x2d, 0x02,
    0xaf, 0x92, 0xb0, 0xcb, 0xb0, 0xed, 0x64, 0x39, 0xef, 0x4e, 0xd1, 0x27,
    0x59, 0x2e, 0xda, 0xa3, 0x6f, 0x9c, 0xda, 0x13, 0xd6, 0x73, 0x9a, 0x28,
    0x49, 0xda, 0xa9, 0x2d, 0x50, 0xda, 0x6e, 0x2d, 0xb9, 0x50, 0xfd, 0xb8,
    0x3e, 0x54, 0x06, 0x84, 0x9e, 0x5e, 0x5b, 0xde, 0x00, 0x27, 0x16, 0xde,
    0x83, 0x89, 0x08, 0x14, 0x44, 0x9a, 0x1f, 0x02, 0x7e, 0x5a, 0x33, 0x9c,
    0xa6, 0xbf, 0x38, 0xf1, 0xe6, 0x79, 0xcf, 0x8b, 0x17, 0x20, 0x3d, 0xe4,
    0x0f, 0x87, 0x71, 0x66, 0x0c, 0xe6, 0x1b, 0x19, 0x28, 0xfc, 0x4a, 0x37,
    0xa3, 0xe4, 0xb3, 0xef, 0x3d, 0xe6, 0x81, 0xf7, 0xd7, 0x1f, 0xef, 0xae,
    0xff, 0xe2, 0x1f, 0xd6, 0xab, 0x4f, 0x10, 0x4e, 0x76, 0x9e, 0xc6, 0x0f,
    0xb4, 0x71, 0x7b, 0xfd, 0xf0, 0xaa, 0xd8, 0xd6, 0xab, 0xeb, 0xd5, 0xcd,
    0xe7, 0x15, 0xff, 0x72, 0xf3, 0xf7, 0xfb, 0xbb, 0x2f, 0x21, 0xe6, 0x22,
    0x87, 0x79, 0xb3, 0x5a, 0xdf, 0x5c, 0x7d, 0xe4, 0xef, 0xae, 0x1e, 0xde,
    0x07, 0x5b, 0x36, 0xcf, 0x63, 0x96, 0xce, 0xfc, 0xcf, 0xdd, 0xfa, 0x1e,
    0xe6, 0x0d, 0x72, 0x89, 0x2a, 0x98, 0xef, 0xaf, 0xee, 0x37, 0x7c, 0xf3,
    0x70, 0xbb, 0xf9, 0x84, 0x90, 0xcd, 0x0a, 0x77, 0xf9, 0xfc, 0x3c, 0x41,
    0x63, 0xa4, 0x3d, 0xa0, 0x8c, 0x84, 0x8a, 0xb2, 0xb4, 0x0e, 0xbf, 0x0b,
    0xa0, 0x0a, 0xb8, 0x4b, 0xae, 0x64, 0x6c, 0xb9, 0x95, 0x2d, 0x6b, 0x84,
    0xb1, 0x64, 0x18, 0x19, 0x53, 0x9b, 0x28, 0xd4, 0x1b, 0x8d, 0x31, 0x95,
    0x64, 0x9d, 0xae, 0x23, 0xff, 0x6e, 0xc9, 0x5a, 0x51, 0x12, 0x03, 0x39,
    0x6a, 0x49, 0xbd, 0x73, 0x20, 0xd8, 0x9a, 0x6c, 0xb1, 0x23, 0xe9, 0x2b,
    0x92, 0x2c, 0xc0, 0x6d, 0x20, 0x2b, 0xe6, 0x76, 0x84, 0xbc, 0xd6, 0x45,
    0x2a, 0x6c, 0x3a, 0x45, 0xb1, 0x28, 0x30, 0xb8, 0x3d, 0xef, 0x48, 0x33,
    0x5d, 0x3b, 0x76, 0xd4, 0x5a, 0xa0, 0xb2, 0x0d, 0x14, 0xd1, 0x54, 0x75,
    0x69, 0x0a, 0xbc, 0x25, 0x24, 0x5b, 0x62, 0xb6, 0x16, 0x57, 0xd7, 0x81,
    0x0f, 0x16, 0x94, 0x3a, 0xff, 0x8e, 0x29, 0xa1, 0xf0, 0x06, 0x03, 0x52,
    0x1c, 0xb1, 0x7f, 0x0c, 0xc2, 0xa8, 0x03, 0xba, 0x78, 0x6b, 0x8e, 0x72,
    0x8f, 0x37, 0xad, 0x72, 0xf2, 0x79, 0x1a, 0xf4, 0x0e, 0x6a, 0x0d, 0x04,
    0x83, 0x71, 0x96, 0xf6, 0x90, 0x06, 0x69, 0xb4, 0xbf, 0x22, 0x47, 0x22,
    0xe7, 0x83, 0xad, 0x6f, 0x38, 0xaa, 0xb6, 0x3e, 0x50, 0x9f, 0x7c, 0x17,
    0xc3, 0xb3, 0xa3, 0x1c, 0x2d, 0x04, 0xde, 0xc9, 0x2c, 0xdc, 0x4c, 0x8f,
    0x0a, 0xe0, 0x7d, 0xd7, 0x23, 0x29, 0xb4, 0x92, 0x9e, 0x84, 0xce, 0xd0,
    0xc2, 0xa8, 0x0e, 0xfb, 0x19, 0xb8, 0xae, 0xd4, 0x14, 0x2c, 0x45, 0x92,
    0xf1, 0x63, 0x90, 0xcf, 0x00, 0x86, 0x3d, 0xae, 0xba, 0x93, 0xcd, 0xef,
    0x12, 0x00, 0x17, 0x5c, 0x19, 0x2c, 0xbc, 0x0c, 0xc7, 0x79, 0x3c, 0xba,
    0xe1, 0xc9, 0x46, 0xa0, 0xdf, 0x77, 0x5f, 0xf6, 0x6b, 0x3b, 0xc5, 0xf4,
    0x6d, 0x90, 0x46, 0x80, 0x82, 0xed, 0x54, 0xb9, 0x8b, 0x1a, 0x3e, 0x2e,
    0x6f, 0x7a, 0x01, 0x44, 0xba, 0x7f, 0x0f, 0x10, 0xf1, 0x90, 0x4e, 0x32,
    0xfc, 0x4f, 0x9c, 0xe5, 0x8b, 0xf4, 0xac, 0x5c, 0x14, 0x8f, 0xd3, 0x74,
    0x3b, 0x03, 0x35, 0xff, 0x07, 0xce, 0xbb, 0x29, 0x5b,
};
const uint32_t command_identify_size PROGMEM = 825;

/* ============================================================================
 * Command index (PROGMEM)
 * ============================================================================ */


static const uint8_t pt_identify[] PROGMEM = { PT_uint32, PT_byte };
static const uint8_t pt_finalize_config[] PROGMEM = { PT_uint32 };
static const uint8_t pt_allocate_oids[] PROGMEM = { PT_byte };
static const uint8_t pt_debug_ping[] PROGMEM = { PT_buffer };
static const uint8_t pt_debug_write[] PROGMEM = { PT_byte, PT_uint32, PT_uint32 };
static const uint8_t pt_debug_read[] PROGMEM = { PT_byte, PT_uint32 };
static const uint8_t pt_set_digital_out[] PROGMEM = { PT_uint32, PT_byte };
static const uint8_t pt_update_digital_out[] PROGMEM = { PT_byte, PT_byte };
static const uint8_t pt_queue_digital_out[] PROGMEM = { PT_byte, PT_uint32, PT_uint32 };
static const uint8_t pt_set_digital_out_pwm_cycle[] PROGMEM = { PT_byte, PT_uint32 };
static const uint8_t pt_config_digital_out[] PROGMEM = { PT_byte, PT_uint32, PT_byte, PT_byte, PT_uint32 };
static const uint8_t pt_buttons_ack[] PROGMEM = { PT_byte, PT_byte };
static const uint8_t pt_buttons_query[] PROGMEM = { PT_byte, PT_uint32, PT_uint32, PT_byte, PT_byte };
static const uint8_t pt_buttons_add[] PROGMEM = { PT_byte, PT_byte, PT_uint32, PT_byte };
static const uint8_t pt_config_buttons[] PROGMEM = { PT_byte, PT_byte };
static const uint8_t pt_identify_response[] PROGMEM = { PT_uint32, PT_progmem_buffer };
static const uint8_t pt_empty[] PROGMEM = { };

const struct command_parser command_index[] PROGMEM = {
    [0] = { .encoded_msgid = 0, .num_args = 0, .flags = 0, .num_params = 2, .param_types = pt_identify_response, .func = 0 },
    [1] = { .encoded_msgid = 1, .num_args = 2, .flags = HF_IN_SHUTDOWN, .num_params = 2, .param_types = pt_identify, .func = command_identify },
    [2] = { .encoded_msgid = 2, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_clear_shutdown },
    [3] = { .encoded_msgid = 3, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_emergency_stop },
    [4] = { .encoded_msgid = 4, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_get_uptime },
    [5] = { .encoded_msgid = 5, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_get_clock },
    [6] = { .encoded_msgid = 6, .num_args = 1, .flags = HF_IN_SHUTDOWN, .num_params = 1, .param_types = pt_finalize_config, .func = command_finalize_config },
    [7] = { .encoded_msgid = 7, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_get_config },
    [8] = { .encoded_msgid = 8, .num_args = 1, .flags = HF_IN_SHUTDOWN, .num_params = 1, .param_types = pt_allocate_oids, .func = command_allocate_oids },
    [9] = { .encoded_msgid = 9, .num_args = 0, .flags = HF_IN_SHUTDOWN, .num_params = 0, .param_types = pt_empty, .func = command_debug_nop },
    [10] = { .encoded_msgid = 10, .num_args = 2, .flags = HF_IN_SHUTDOWN, .num_params = 1, .param_types = pt_debug_ping, .func = command_debug_ping },
    [11] = { .encoded_msgid = 11, .num_args = 3, .flags = HF_IN_SHUTDOWN, .num_params = 3, .param_types = pt_debug_write, .func = command_debug_write },
    [12] = { .encoded_msgid = 12, .num_args = 2, .flags = HF_IN_SHUTDOWN, .num_params = 2, .param_types = pt_debug_read, .func = command_debug_read },
    [13] = { .encoded_msgid = 13, .num_args = 2, .flags = 0, .num_params = 2, .param_types = pt_set_digital_out, .func = command_set_digital_out },
    [14] = { .encoded_msgid = 14, .num_args = 2, .flags = 0, .num_params = 2, .param_types = pt_update_digital_out, .func = command_update_digital_out },
    [15] = { .encoded_msgid = 15, .num_args = 3, .flags = 0, .num_params = 3, .param_types = pt_queue_digital_out, .func = command_queue_digital_out },
    [16] = { .encoded_msgid = 16, .num_args = 2, .flags = 0, .num_params = 2, .param_types = pt_set_digital_out_pwm_cycle, .func = command_set_digital_out_pwm_cycle },
    [17] = { .encoded_msgid = 17, .num_args = 5, .flags = 0, .num_params = 5, .param_types = pt_config_digital_out, .func = command_config_digital_out },
    [18] = { .func = 0 }, [19] = { .func = 0 }, [20] = { .func = 0 }, [21] = { .func = 0 },
    [22] = { .func = 0 }, [23] = { .func = 0 }, [24] = { .func = 0 }, [25] = { .func = 0 },
    [26] = { .func = 0 }, [27] = { .func = 0 }, [28] = { .func = 0 }, [29] = { .func = 0 },
    [30] = { .func = 0 }, [31] = { .func = 0 }, [32] = { .func = 0 }, [33] = { .func = 0 },
    [34] = { .func = 0 }, [35] = { .func = 0 }, [36] = { .func = 0 }, [37] = { .func = 0 },
    [38] = { .func = 0 }, [39] = { .func = 0 }, [40] = { .func = 0 }, [41] = { .func = 0 },
    [42] = { .func = 0 }, [43] = { .func = 0 }, [44] = { .func = 0 }, [45] = { .func = 0 },
    [46] = { .encoded_msgid = 46, .num_args = 2, .flags = 0, .num_params = 2, .param_types = pt_buttons_ack, .func = command_buttons_ack },
    [47] = { .encoded_msgid = 47, .num_args = 5, .flags = 0, .num_params = 5, .param_types = pt_buttons_query, .func = command_buttons_query },
    [48] = { .encoded_msgid = 48, .num_args = 4, .flags = 0, .num_params = 4, .param_types = pt_buttons_add, .func = command_buttons_add },
    [49] = { .encoded_msgid = 49, .num_args = 2, .flags = 0, .num_params = 2, .param_types = pt_config_buttons, .func = command_config_buttons },
};

const uint16_t command_index_size PROGMEM = sizeof(command_index) / sizeof(command_index[0]);

/* ============================================================================
 * Response encoders (all in PROGMEM)
 * ============================================================================ */

static const uint8_t enc_pt_identify_response[] PROGMEM = { PT_uint32, PT_progmem_buffer };
static const uint8_t enc_pt_starting[] PROGMEM = { };
static const uint8_t enc_pt_is_shutdown[] PROGMEM = { PT_uint16 };
static const uint8_t enc_pt_shutdown[] PROGMEM = { PT_uint32, PT_uint16 };
static const uint8_t enc_pt_stats[] PROGMEM = { PT_uint32, PT_uint32, PT_uint32 };
static const uint8_t enc_pt_uptime[] PROGMEM = { PT_uint32, PT_uint32 };
static const uint8_t enc_pt_clock[] PROGMEM = { PT_uint32 };
static const uint8_t enc_pt_config[] PROGMEM = { PT_byte, PT_uint32, PT_byte, PT_uint16 };
static const uint8_t enc_pt_pong[] PROGMEM = { PT_buffer };
static const uint8_t enc_pt_debug_result[] PROGMEM = { PT_uint32 };
static const uint8_t enc_pt_buttons_state[] PROGMEM = { PT_byte, PT_byte, PT_buffer };

static const struct command_encoder enc_identify_response PROGMEM = { .encoded_msgid = 0, .max_size = 64, .num_params = 2, .param_types = enc_pt_identify_response };
static const struct command_encoder enc_starting PROGMEM = { .encoded_msgid = 235, .max_size = 7, .num_params = 0, .param_types = enc_pt_starting };
static const struct command_encoder enc_is_shutdown PROGMEM = { .encoded_msgid = 236, .max_size = 16, .num_params = 1, .param_types = enc_pt_is_shutdown };
static const struct command_encoder enc_shutdown PROGMEM = { .encoded_msgid = 237, .max_size = 32, .num_params = 2, .param_types = enc_pt_shutdown };
static const struct command_encoder enc_stats PROGMEM = { .encoded_msgid = 238, .max_size = 32, .num_params = 3, .param_types = enc_pt_stats };
static const struct command_encoder enc_uptime PROGMEM = { .encoded_msgid = 239, .max_size = 24, .num_params = 2, .param_types = enc_pt_uptime };
static const struct command_encoder enc_clock PROGMEM = { .encoded_msgid = 240, .max_size = 16, .num_params = 1, .param_types = enc_pt_clock };
static const struct command_encoder enc_config PROGMEM = { .encoded_msgid = 241, .max_size = 32, .num_params = 4, .param_types = enc_pt_config };
static const struct command_encoder enc_pong PROGMEM = { .encoded_msgid = 242, .max_size = 64, .num_params = 1, .param_types = enc_pt_pong };
static const struct command_encoder enc_debug_result PROGMEM = { .encoded_msgid = 243, .max_size = 16, .num_params = 1, .param_types = enc_pt_debug_result };


static const struct command_encoder enc_buttons_state PROGMEM = { .encoded_msgid = 250, .max_size = 64, .num_params = 3, .param_types = enc_pt_buttons_state };


/* ============================================================================

 * Encoder lookup: compile-time hash → switch-case, zero string comparison.
 *
 * _ENCODER_HASH(FMT) = sizeof(FMT)*31 + (FMT)[0] + (FMT)[sizeof(FMT)-2]
 * Computed at compile time by the macro in command.h.
 * NOTE: hash is computed on the FULL format string including params.
 * Verified unique for all 11 response types.
 * ============================================================================ */

const struct command_encoder *
ctr_lookup_encoder(uint16_t hash)
{
    switch (hash) {
    case  497:  return &enc_starting;          /* "starting" */

    case 1398:  return &enc_identify_response; /* "identify_response offset=%u data=%.*s" */
    case 1245:  return &enc_is_shutdown;       /* "is_shutdown static_string_id=%hu" */
    case 1441:  return &enc_shutdown;          /* "shutdown clock=%u static_string_id=%hu" */
    case 1193:  return &enc_stats;             /* "stats count=%u sum=%u sumsq=%u" */
    case  978:  return &enc_uptime;            /* "uptime high=%u clock=%u" */

    case  681:  return &enc_clock;             /* "clock clock=%u" */
    case 1983:  return &enc_config;            /* "config is_config=%c crc=%u is_shutdown=%c move_count=%hu" */
    case  661:  return &enc_pong;              /* "pong data=%*s" */
    case  837:  return &enc_debug_result;      /* "debug_result val=%u" */
    case 1577:  return &enc_buttons_state;     /* "buttons_state oid=%c ack_count=%c state=%*s" */
    default:    return &enc_starting;
    }
}

const struct command_encoder *
ctr_lookup_output(const char *str)
{
    return NULL;
}

uint8_t
ctr_lookup_static_string(const char *str)
{
    return 0;
}





