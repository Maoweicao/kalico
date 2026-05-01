/**
 * KalicoProtocol - A reusable C++ library implementing the Kalico/Klipper
 * binary communication protocol for use with Arduino and other frameworks.
 *
 * Based on the Kalico firmware communication protocol:
 *   - C side: src/command.c, src/command.h
 *   - Python side: klippy/msgproto.py
 *
 * This library allows any C++ application to communicate with a Kalico/Klipper
 * MCU firmware over a serial (UART/USB) connection.
 *
 * Copyright (C) 2024  Kalico Protocol Library Contributors
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef KALICO_PROTOCOL_H
#define KALICO_PROTOCOL_H

#include <stdint.h>
#include <stddef.h>

/**
 * @namespace Kalico
 * @brief All Kalico Protocol types and functions reside in this namespace.
 */
namespace Kalico {

// ============================================================================
// Protocol Constants (matching command.h / msgproto.py)
// ============================================================================

static constexpr uint8_t MESSAGE_MIN          = 5;    // Minimum block size
static constexpr uint8_t MESSAGE_MAX          = 64;   // Maximum block size
static constexpr uint8_t MESSAGE_HEADER_SIZE  = 2;    // len + seq
static constexpr uint8_t MESSAGE_TRAILER_SIZE = 3;    // CRC16(2) + SYNC(1)
static constexpr uint8_t MESSAGE_POS_LEN      = 0;    // Offset of length byte
static constexpr uint8_t MESSAGE_POS_SEQ      = 1;    // Offset of sequence byte
static constexpr uint8_t MESSAGE_TRAILER_CRC  = 3;    // CRC offset from end
static constexpr uint8_t MESSAGE_TRAILER_SYNC = 1;    // SYNC offset from end
static constexpr uint8_t MESSAGE_PAYLOAD_MAX  = MESSAGE_MAX - MESSAGE_MIN;
static constexpr uint8_t MESSAGE_SEQ_MASK     = 0x0F; // Low 4 bits for seq
static constexpr uint8_t MESSAGE_DEST         = 0x10; // High 4 bits fixed
static constexpr uint8_t MESSAGE_SYNC         = 0x7E; // Frame sync byte

// Hard-coded message IDs
static constexpr uint16_t MSGID_IDENTIFY_RESPONSE = 0;
static constexpr uint16_t MSGID_IDENTIFY          = 1;

// Parameter type enum (matching command.h)
enum class ParamType : uint8_t {
    PT_uint32          = 0,
    PT_int32           = 1,
    PT_uint16          = 2,
    PT_int16           = 3,
    PT_byte            = 4,
    PT_string          = 5,
    PT_progmem_buffer  = 6,
    PT_buffer          = 7,
};

} // namespace Kalico

#include "VLQ.h"
#include "CRC16.h"
#include "MessageTypes.h"
#include "MessageBlock.h"
#include "MessageEncoder.h"
#include "MessageParser.h"

#endif // KALICO_PROTOCOL_H
