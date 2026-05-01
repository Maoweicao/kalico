/**
 * MessageParser.h - Parsing and dispatching of Kalico protocol messages
 *
 * Parses incoming binary message blocks and dispatches responses
 * based on the data dictionary obtained during the identify phase.
 *
 * Based on command_dispatch() from src/command.c and
 * MessageParser class from klippy/msgproto.py.
 */

#ifndef KALICO_MESSAGE_PARSER_H
#define KALICO_MESSAGE_PARSER_H

#include "KalicoProtocol.h"
#include "VLQ.h"
#include "MessageBlock.h"
#include <string.h>

namespace Kalico {

// ============================================================================
// Callback types
// ============================================================================

/**
 * @brief Callback for handling parsed responses from the MCU.
 *
 * Called when a complete, validated message has been parsed.
 * The raw payload (excluding msgid) is provided for flexibility.
 *
 * @param msgId        The decoded message ID.
 * @param payload      Pointer to payload data (after msgid).
 * @param payloadLen   Length of payload data.
 * @param userData     Opaque user pointer.
 */
typedef void (*ResponseHandler)(uint16_t msgId,
                                const uint8_t* payload, uint8_t payloadLen,
                                void* userData);

/**
 * @brief Callback for handling raw decoded identify response data chunks.
 *
 * Called as each identify_response segment is received.
 *
 * @param offset       Offset of this chunk in the total identify data.
 * @param data         Pointer to data bytes.
 * @param dataLen      Number of data bytes.
 * @param userData     Opaque user pointer.
 */
typedef void (*IdentifyDataHandler)(uint32_t offset,
                                    const uint8_t* data, uint8_t dataLen,
                                    void* userData);

// ============================================================================
// MessageParser
// ============================================================================

/**
 * @class MessageParser
 * @brief Parses Kalico binary protocol messages from a byte stream.
 *
 * Handles:
 *   - Frame synchronisation (SYNC byte detection)
 *   - Block validation (length, sequence, CRC)
 *   - Multi-command dispatch within a single block
 *   - Identify data reassembly
 *   - Sequence number tracking
 */
class MessageParser {
public:
    MessageParser()
        : _nextSeq(MESSAGE_DEST)
        , _handler(nullptr)
        , _identifyHandler(nullptr)
        , _userData(nullptr)
        , _needSync(false)
        , _needValid(false)
    {}

    // ---- Configuration ----

    /** Set the general response handler. */
    void setHandler(ResponseHandler handler, void* userData = nullptr) {
        _handler = handler;
        _userData = userData;
    }

    /** Set the identify data chunk handler. */
    void setIdentifyHandler(IdentifyDataHandler handler, void* userData = nullptr) {
        _identifyHandler = handler;
    }

    /** Reset parser state (e.g. after reconnection). */
    void reset() {
        _nextSeq   = MESSAGE_DEST;
        _needSync  = false;
        _needValid = false;
    }

    // ---- Core method: feed bytes ----

    /**
     * @brief Feed received bytes into the parser.
     *
     * Call this whenever new data arrives from the serial connection.
     *
     * @param data   Pointer to received bytes.
     * @param len    Number of received bytes.
     * @return       Number of bytes consumed.
     *
     * After this call, the user should remove `consumed` bytes from
     * their receive buffer.
     */
    uint16_t feed(const uint8_t* data, uint16_t len);

    /**
     * @brief Get the next expected sequence number (for ACK tracking).
     */
    uint8_t nextSequence() const { return _nextSeq & MESSAGE_SEQ_MASK; }

    /**
     * @brief Advance to the next sequence number manually
     *        (used after sending a new command).
     */
    void advanceSeq() {
        _nextSeq = ((_nextSeq + 1) & MESSAGE_SEQ_MASK) | MESSAGE_DEST;
    }

    /**
     * @brief Get current sequence byte (for building outbound blocks).
     */
    uint8_t currentSeq() const { return _nextSeq; }

    /** Reset sync state (called when resynchronising). */
    void clearSync() { _needSync = false; _needValid = false; }

private:
    uint8_t  _nextSeq;       // Next expected sequence number with MESSAGE_DEST
    ResponseHandler    _handler;
    IdentifyDataHandler _identifyHandler;
    void*    _userData;

    bool _needSync;           // Currently searching for SYNC byte
    bool _needValid;          // Need to validate next possible block

    // Dispatch all commands found in a validated block
    void dispatch(const uint8_t* buf, uint8_t msglen);

    // Parse the identify_response command specifically
    void parseIdentifyResponse(const uint8_t* payload, uint8_t payloadLen);
};

// ============================================================================
// Implementation (inline for header-only library)
// ============================================================================

inline uint16_t MessageParser::feed(const uint8_t* data, uint16_t len) {
    if (len == 0) return 0;

    const uint8_t* buf = data;
    uint16_t remaining = len;

    while (remaining > 0) {
        // ---- State: searching for sync ----
        if (_needSync) {
            const uint8_t* sync = (const uint8_t*)memchr(buf, MESSAGE_SYNC, remaining);
            if (sync) {
                uint16_t skip = sync - buf + 1;
                buf       += skip;
                remaining -= skip;
                _needSync = false;
            } else {
                // No SYNC found; discard all
                return len;
            }
            continue;
        }

        // ---- Need at least minimum block size ----
        if (remaining < MESSAGE_MIN) {
            return buf - data; // Wait for more data
        }

        // ---- Validate block ----
        int8_t result = MessageBlock::validate(buf, remaining);
        if (result > 0) {
            // Valid block received
            uint8_t msglen = static_cast<uint8_t>(result);
            uint8_t seq    = buf[MESSAGE_POS_SEQ] & MESSAGE_SEQ_MASK;

            // Check sequence number
            uint8_t expectedSeq = _nextSeq & MESSAGE_SEQ_MASK;
            if (seq == expectedSeq) {
                // Expected sequence —process
                dispatch(buf, msglen);
                _nextSeq = ((seq + 1) & MESSAGE_SEQ_MASK) | MESSAGE_DEST;
            }
            // If out-of-order, silently drop (wait for retransmit)

            _needValid = false;
            buf       += msglen;
            remaining -= msglen;
        }
        else if (result == 0) {
            // Need more data
            return buf - data;
        }
        else {
            // Invalid block
            if (buf[0] == MESSAGE_SYNC) {
                // Leading SYNC byte — skip it
                buf++;
                remaining--;
                continue;
            }

            // Search for next SYNC
            _needSync  = true;
            _needValid = true;
            continue;
        }
    }

    return len;
}

inline void MessageParser::dispatch(const uint8_t* buf, uint8_t msglen) {
    const uint8_t* p      = &buf[MESSAGE_HEADER_SIZE];
    const uint8_t* msgend = &buf[msglen - MESSAGE_TRAILER_SIZE];

    while (p < msgend) {
        uint16_t msgId = VLQ::parseMsgId(p);

        // Special handling for identify_response (msgid=0)
        if (msgId == MSGID_IDENTIFY_RESPONSE && _identifyHandler) {
            parseIdentifyResponse(p, msgend - p);
            p = msgend; // identify_response consumes the rest
            break;
        }

        // For other messages, dispatch to the general handler
        if (_handler) {
            // Pass the raw payload starting at current position.
            // The handler receives everything after the msgid for this command.
            const uint8_t* cmdStart = p;
            // Advance past parameters to find next msgid (or end)
            // We can't easily know the payload length without the data dictionary.
            // For now, pass the entire remaining payload.
            _handler(msgId, p, msgend - p, _userData);
            break; // Let the handler deal with the rest
        }

        // No handler — skip to end
        p = msgend;
    }
}

inline void MessageParser::parseIdentifyResponse(const uint8_t* payload,
                                                  uint8_t payloadLen) {
    // identify_response offset=%u data=%.*s
    // Parameters: PT_uint32 offset, PT_progmem_buffer data
    const uint8_t* p = payload;
    uint32_t offset = VLQ::decode(p);  // decode offset

    // Decode buffer: length byte + data
    uint8_t dataLen = *p++;
    if (dataLen > payloadLen - (p - payload))
        dataLen = payloadLen - (p - payload);

    _identifyHandler(offset, p, dataLen, _userData);
}

} // namespace Kalico

#endif // KALICO_MESSAGE_PARSER_H
