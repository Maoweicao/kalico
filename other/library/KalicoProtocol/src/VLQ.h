/**
 * VLQ.h - Variable Length Quantity encoding and decoding
 *
 * Implements the Kalico VLQ integer encoding scheme that supports
 * both positive and negative integers in a compact variable-length format.
 *
 * Based on encode_int() / parse_int() from src/command.c and
 * PT_uint32.encode() / PT_uint32.parse() from klippy/msgproto.py.
 */

#ifndef KALICO_VLQ_H
#define KALICO_VLQ_H

#include <stdint.h>

namespace Kalico {

/**
 * @class VLQ
 * @brief Static methods for encoding/decoding Variable Length Quantities.
 *
 * The Kalico VLQ scheme encodes integers in 1-5 bytes depending on magnitude:
 *
 * | Integer Range            | Bytes |
 * |--------------------------|-------|
 * | -32 .. 95                | 1     |
 * | -4096 .. 12287           | 2     |
 * | -524288 .. 1572863       | 3     |
 * | -67108864 .. 201326591   | 4     |
 * | -2147483648 .. 4294967295| 5     |
 *
 * Each byte uses the lower 7 bits for data; the MSB indicates
 * whether more bytes follow (1 = continuation, 0 = final).
 */
class VLQ {
public:
    /**
     * @brief Compute the number of bytes required to encode a value.
     * @param v The 32-bit value to encode.
     * @return Number of bytes needed (1..5).
     */
    static uint8_t encodedLength(uint32_t v) {
        int32_t sv = static_cast<int32_t>(v);
        if (sv < (3L << 5)  && sv >= -(1L << 5))  return 1;
        if (sv < (3L << 12) && sv >= -(1L << 12)) return 2;
        if (sv < (3L << 19) && sv >= -(1L << 19)) return 3;
        if (sv < (3L << 26) && sv >= -(1L << 26)) return 4;
        return 5;
    }

    /**
     * @brief Encode a uint32_t as VLQ into a buffer.
     * @param buf Destination buffer (must have sufficient space).
     * @param v   The value to encode.
     * @return    Pointer just past the last byte written.
     */
    static uint8_t* encode(uint8_t* buf, uint32_t v) {
        int32_t sv = static_cast<int32_t>(v);
        if (sv < (3L << 5)  && sv >= -(1L << 5))  goto f4;
        if (sv < (3L << 12) && sv >= -(1L << 12)) goto f3;
        if (sv < (3L << 19) && sv >= -(1L << 19)) goto f2;
        if (sv < (3L << 26) && sv >= -(1L << 26)) goto f1;
        *buf++ = (v >> 28) | 0x80;
    f1: *buf++ = ((v >> 21) & 0x7f) | 0x80;
    f2: *buf++ = ((v >> 14) & 0x7f) | 0x80;
    f3: *buf++ = ((v >> 7)  & 0x7f) | 0x80;
    f4: *buf++ = v & 0x7f;
        return buf;
    }

    /**
     * @brief Encode a uint32_t as VLQ into a buffer with a length limit.
     * @param buf     Destination buffer.
     * @param v       The value to encode.
     * @param maxLen  Maximum bytes to write.
     * @return        Number of bytes written (0 if buffer too small).
     */
    static uint8_t encodeChecked(uint8_t* buf, uint32_t v, uint8_t maxLen) {
        uint8_t len = encodedLength(v);
        if (len > maxLen) return 0;
        encode(buf, v);
        return len;
    }

    /**
     * @brief Decode a VLQ-encoded uint32_t from a buffer.
     * @param p  Pointer to pointer to current read position.
     *           Updated to point past the last byte read.
     * @return   The decoded 32-bit value.
     */
    static uint32_t decode(const uint8_t* &p) {
        uint8_t c = *p++;
        uint32_t v = c & 0x7f;
        if ((c & 0x60) == 0x60)
            v |= -0x20;  // sign-extend if first byte indicates negative
        while (c & 0x80) {
            c = *p++;
            v = (v << 7) | (c & 0x7f);
        }
        return v;
    }

    /**
     * @brief Optimised 2-byte VLQ encode for message IDs.
     *
     * Message IDs in Kalico are always positive and encoded in at most 2 bytes.
     *
     * @param buf          Destination buffer.
     * @param encodedMsgId The message ID to encode.
     * @return             Pointer past the last byte written.
     */
    static uint8_t* encodeMsgId(uint8_t* buf, uint16_t encodedMsgId) {
        if (encodedMsgId >= 0x80)
            *buf++ = (encodedMsgId >> 7) | 0x80;
        *buf++ = encodedMsgId & 0x7f;
        return buf;
    }

    /**
     * @brief Optimised 2-byte parse for message IDs.
     * @param p  Pointer to pointer to current read position. Updated on return.
     * @return   The parsed (positive) message ID.
     */
    static uint16_t parseMsgId(const uint8_t* &p) {
        uint16_t vid = *p++;
        if (vid & 0x80)
            vid = ((vid & 0x7f) << 7) | (*p++);
        return vid;
    }
};

} // namespace Kalico

#endif // KALICO_VLQ_H
