/**
 * MessageBlock.h - Message block framing and deframing
 *
 * Handles the low-level framing of Kalico message blocks:
 *
 * | Offset | Size | Field                          |
 * |--------|------|--------------------------------|
 * | 0      | 1    | Length (total block size, 5-64)|
 * | 1      | 1    | Sequence (low 4 bits seq | 0x10)|
 * | 2      | n    | Content (VLQ-encoded commands)  |
 * | 2+n    | 2    | CRC-16 CCITT                    |
 * | 2+n+2  | 1    | Sync byte (0x7E)                |
 *
 * Based on command.c / msgproto.py framing logic.
 */

#ifndef KALICO_MESSAGE_BLOCK_H
#define KALICO_MESSAGE_BLOCK_H

#include "KalicoProtocol.h"
#include "CRC16.h"
#include <string.h>

namespace Kalico {

/**
 * @class MessageBlock
 * @brief Builds and parses message blocks.
 *
 * All methods operate on a pre-allocated buffer of at least MESSAGE_MAX bytes.
 */
class MessageBlock {
public:
    /**
     * @brief Assemble a complete message block with header and trailer.
     *
     * @param buf       Pre-allocated buffer (MESSAGE_MAX bytes).
     * @param content   VLQ-encoded command content bytes.
     * @param contentLen Number of content bytes.
     * @param seq       Sequence number (0-15, will be ORed with MESSAGE_DEST).
     * @return          Total block size (including header + trailer).
     */
    static uint8_t frame(uint8_t* buf,
                         const uint8_t* content, uint8_t contentLen,
                         uint8_t seq) {
        uint8_t msglen = MESSAGE_MIN + contentLen;
        buf[MESSAGE_POS_LEN] = msglen;
        buf[MESSAGE_POS_SEQ] = (seq & MESSAGE_SEQ_MASK) | MESSAGE_DEST;

        // Copy content
        if (contentLen > 0)
            memcpy(&buf[MESSAGE_HEADER_SIZE], content, contentLen);

        // Compute CRC over everything except trailer
        uint16_t crc = CRC16CCITT::compute(buf, msglen - MESSAGE_TRAILER_SIZE);
        buf[msglen - MESSAGE_TRAILER_CRC]     = crc >> 8;
        buf[msglen - MESSAGE_TRAILER_CRC + 1] = crc & 0xFF;
        buf[msglen - MESSAGE_TRAILER_SYNC]    = MESSAGE_SYNC;

        return msglen;
    }

    /**
     * @brief Encode a msgid + parameters and frame into a complete block.
     *
     * @param buf       Pre-allocated buffer (MESSAGE_MAX bytes).
     * @param encodedMsgId The VLQ-encoded message ID (positive, ≤ 2 bytes).
     * @param params    VLQ-encoded parameter bytes.
     * @param paramsLen Number of parameter bytes.
     * @param seq       Sequence number (0-15).
     * @return          Total block size.
     */
    static uint8_t frameWithMsgId(uint8_t* buf,
                                  uint16_t encodedMsgId,
                                  const uint8_t* params, uint8_t paramsLen,
                                  uint8_t seq) {
        // Encode msgid + parameters into content
        uint8_t content[MESSAGE_PAYLOAD_MAX];
        uint8_t* p = VLQ::encodeMsgId(content, encodedMsgId);
        if (paramsLen > 0) {
            memcpy(p, params, paramsLen);
            p += paramsLen;
        }
        return frame(buf, content, p - content, seq);
    }

    /**
     * @brief Validate a received message block.
     *
     * Checks: minimum length, sequence marker, sync byte, CRC.
     *
     * @param buf    Buffer containing a potential block.
     * @param bufLen Number of available bytes.
     * @return       Block length if valid, 0 if more data needed, -1 if invalid.
     */
    static int8_t validate(const uint8_t* buf, uint_fast8_t bufLen) {
        if (bufLen < MESSAGE_MIN)
            return 0;  // Need more data

        uint8_t msglen = buf[MESSAGE_POS_LEN];
        if (msglen < MESSAGE_MIN || msglen > MESSAGE_MAX)
            return -1; // Invalid length

        uint8_t msgseq = buf[MESSAGE_POS_SEQ];
        if ((msgseq & ~MESSAGE_SEQ_MASK) != MESSAGE_DEST)
            return -1; // Invalid sequence marker

        if (bufLen < msglen)
            return 0;  // Need more data

        if (buf[msglen - MESSAGE_TRAILER_SYNC] != MESSAGE_SYNC)
            return -1; // Invalid sync byte

        uint16_t expectedCrc =
            (buf[msglen - MESSAGE_TRAILER_CRC] << 8) |
             buf[msglen - MESSAGE_TRAILER_CRC + 1];
        uint16_t computedCrc = CRC16CCITT::compute(buf, msglen - MESSAGE_TRAILER_SIZE);

        if (computedCrc != expectedCrc)
            return -1; // CRC mismatch

        return static_cast<int8_t>(msglen); // Valid
    }

    /**
     * @brief Extract the sequence number from a valid block.
     * @param buf Validated block buffer.
     * @return   Sequence number (0-15).
     */
    static uint8_t getSequence(const uint8_t* buf) {
        return buf[MESSAGE_POS_SEQ] & MESSAGE_SEQ_MASK;
    }

    /**
     * @brief Get a pointer to the content (payload) within a block.
     * @param buf Block buffer.
     * @return   Pointer to first content byte.
     */
    static const uint8_t* getPayload(const uint8_t* buf) {
        return &buf[MESSAGE_HEADER_SIZE];
    }

    /**
     * @brief Get the length of the payload in a block.
     * @param buf Block buffer.
     * @return   Number of payload bytes.
     */
    static uint8_t getPayloadLength(const uint8_t* buf) {
        return buf[MESSAGE_POS_LEN] - MESSAGE_MIN;
    }
};

} // namespace Kalico

#endif // KALICO_MESSAGE_BLOCK_H
