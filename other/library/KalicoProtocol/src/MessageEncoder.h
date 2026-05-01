/**
 * MessageEncoder.h - Encoding of Kalico protocol commands
 *
 * Provides facilities to build and encode commands/requests that
 * can be sent to a Kalico/Klipper MCU.
 *
 * Based on command_encodef() from src/command.c and
 * MessageFormat.encode_by_name() from klippy/msgproto.py.
 */

#ifndef KALICO_MESSAGE_ENCODER_H
#define KALICO_MESSAGE_ENCODER_H

#include "KalicoProtocol.h"
#include "VLQ.h"
#include "MessageTypes.h"
#include <stdarg.h>
#include <string.h>

namespace Kalico {

/**
 * @class MessageEncoder
 * @brief Encodes Kalico protocol commands/responses into wire format.
 *
 * Usage:
 * @code
 *   uint8_t buf[Kalico::MESSAGE_MAX];
 *   // Encode "update_digital_out oid=6 value=1" with msgid=5
 *   uint8_t len = Kalico::MessageEncoder::encodePayload(buf, 5,
 *       Kalico::PT_byte::typeCode, 6,
 *       Kalico::PT_byte::typeCode, 1);
 *   // Then frame it:
 *   uint8_t blockLen = Kalico::MessageBlock::frame(outputBuf, buf, len, seq);
 * @endcode
 */
class MessageEncoder {
public:
    /**
     * @brief Encode a command payload (msgid + parameters) into a buffer.
     *
     * Accepts a variable number of type-value pairs. Each pair consists of
     * a ParamType specifying the wire format followed by the value.
     *
     * @param buf        Destination buffer.
     * @param encodedMsgId The VLQ-encoded message ID (positive integer).
     * @param count      Number of type-value pairs (paramCount * 2).
     * @param ...        Alternating (uint32_t typeCode, uint32_t value).
     * @return           Total number of bytes written.
     */
    static uint8_t encodePayload(uint8_t* buf, uint16_t encodedMsgId,
                                 uint8_t count, ...) {
        const uint8_t* start = buf;

        // Write message ID
        buf = VLQ::encodeMsgId(buf, encodedMsgId);

        va_list args;
        va_start(args, count);
        for (uint8_t i = 0; i < count; i++) {
            ParamType pt = static_cast<ParamType>(va_arg(args, uint32_t));
            uint32_t val = va_arg(args, uint32_t);
            buf = encodeParam(buf, pt, val);
        }
        va_end(args);

        return buf - start;
    }

    /**
     * @brief Encode a single parameter.
     * @param buf  Destination buffer.
     * @param pt   Parameter type.
     * @param val  Value to encode.
     * @return     Pointer past written data.
     */
    static uint8_t* encodeParam(uint8_t* buf, ParamType pt, uint32_t val) {
        switch (pt) {
        case ParamType::PT_uint32:
        case ParamType::PT_int32:
        case ParamType::PT_uint16:
        case ParamType::PT_int16:
        case ParamType::PT_byte:
            return VLQ::encode(buf, val);

        case ParamType::PT_string:
        case ParamType::PT_buffer:
        case ParamType::PT_progmem_buffer: {
            // val is treated as a pointer to string data
            const uint8_t* src = reinterpret_cast<const uint8_t*>(val);
            uint8_t len = *src; // first byte = length
            *buf++ = len;
            if (len > 0) {
                memcpy(buf, src + 1, len);
                buf += len;
            }
            return buf;
        }

        default:
            return buf;
        }
    }

    /**
     * @brief Encode a string parameter.
     * @param buf  Destination buffer.
     * @param str  Null-terminated string.
     * @return     Pointer past written data.
     */
    static uint8_t* encodeString(uint8_t* buf, const char* str) {
        uint8_t len = static_cast<uint8_t>(strlen(str));
        *buf++ = len;
        if (len > 0) {
            memcpy(buf, str, len);
            buf += len;
        }
        return buf;
    }

    /**
     * @brief Helper to build the `identify` command payload.
     *
     * `identify offset=%u count=%c` (msgid = MSGID_IDENTIFY = 1)
     *
     * @param buf    Destination buffer.
     * @param offset Byte offset into identify data.
     * @param count  Number of bytes to request (0 = full block).
     * @return       Number of bytes written to buf.
     */
    static uint8_t encodeIdentify(uint8_t* buf, uint32_t offset, uint8_t count) {
        return encodePayload(buf, MSGID_IDENTIFY, 2,
                             static_cast<uint32_t>(ParamType::PT_uint32), offset,
                             static_cast<uint32_t>(ParamType::PT_byte),   count);
    }

private:
    // Prevent instantiation
    MessageEncoder() = delete;
};

} // namespace Kalico

#endif // KALICO_MESSAGE_ENCODER_H
