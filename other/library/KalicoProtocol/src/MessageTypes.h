/**
 * MessageTypes.h - Kalico protocol message type system
 *
 * Provides C++ classes that mirror the Python type system from
 * klippy/msgproto.py, allowing encoding/decoding of individual
 * parameter values in their VLQ or string forms.
 */

#ifndef KALICO_MESSAGE_TYPES_H
#define KALICO_MESSAGE_TYPES_H

#include "VLQ.h"
#include <string.h>
#include <stdint.h>

namespace Kalico {

// ============================================================================
// Forward declarations
// ============================================================================

class MessageTypeBase;

// ============================================================================
// Concrete parameter type classes
// ============================================================================

/**
 * @class PT_uint32
 * @brief Encodes/decodes an unsigned 32-bit integer as VLQ (up to 5 bytes).
 */
class PT_uint32 {
public:
    static constexpr bool isInt    = true;
    static constexpr bool isString = false;
    static constexpr uint8_t maxLength = 5;
    static constexpr ParamType typeCode = ParamType::PT_uint32;

    /** Encode a value into a byte buffer, return pointer past written data. */
    static uint8_t* encode(uint8_t* out, uint32_t v) {
        return VLQ::encode(out, v);
    }

    /** Decode a value from a byte buffer.  Advances `p` past consumed bytes. */
    static uint32_t decode(const uint8_t* &p) {
        return VLQ::decode(p);
    }
};

/**
 * @class PT_int32
 * @brief Encodes/decodes a signed 32-bit integer as VLQ.
 */
class PT_int32 {
public:
    static constexpr bool isInt    = true;
    static constexpr bool isString = false;
    static constexpr uint8_t maxLength = 5;
    static constexpr ParamType typeCode = ParamType::PT_int32;

    static uint8_t* encode(uint8_t* out, int32_t v) {
        return VLQ::encode(out, static_cast<uint32_t>(v));
    }

    static int32_t decode(const uint8_t* &p) {
        return static_cast<int32_t>(VLQ::decode(p));
    }
};

/**
 * @class PT_uint16
 * @brief Encodes/decodes an unsigned 16-bit integer as VLQ (up to 3 bytes).
 */
class PT_uint16 {
public:
    static constexpr bool isInt    = true;
    static constexpr bool isString = false;
    static constexpr uint8_t maxLength = 3;
    static constexpr ParamType typeCode = ParamType::PT_uint16;

    static uint8_t* encode(uint8_t* out, uint16_t v) {
        return VLQ::encode(out, v);
    }

    static uint16_t decode(const uint8_t* &p) {
        return static_cast<uint16_t>(VLQ::decode(p));
    }
};

/**
 * @class PT_int16
 * @brief Encodes/decodes a signed 16-bit integer as VLQ (up to 3 bytes).
 */
class PT_int16 {
public:
    static constexpr bool isInt    = true;
    static constexpr bool isString = false;
    static constexpr uint8_t maxLength = 3;
    static constexpr ParamType typeCode = ParamType::PT_int16;

    static uint8_t* encode(uint8_t* out, int16_t v) {
        return VLQ::encode(out, static_cast<uint32_t>(v));
    }

    static int16_t decode(const uint8_t* &p) {
        return static_cast<int16_t>(VLQ::decode(p));
    }
};

/**
 * @class PT_byte
 * @brief Encodes/decodes an 8-bit byte as VLQ (up to 2 bytes).
 */
class PT_byte {
public:
    static constexpr bool isInt    = true;
    static constexpr bool isString = false;
    static constexpr uint8_t maxLength = 2;
    static constexpr ParamType typeCode = ParamType::PT_byte;

    static uint8_t* encode(uint8_t* out, uint8_t v) {
        return VLQ::encode(out, v);
    }

    static uint8_t decode(const uint8_t* &p) {
        return static_cast<uint8_t>(VLQ::decode(p));
    }
};

/**
 * @class PT_string
 * @brief Encodes/decodes a dynamic-length string (length byte + data).
 *
 * Wire format: [length_byte][data_bytes...]
 * Maximum length: 64 bytes (limited by MESSAGE_PAYLOAD_MAX).
 */
class PT_string {
public:
    static constexpr bool isInt    = false;
    static constexpr bool isString = true;
    static constexpr uint8_t maxLength = 64;
    static constexpr ParamType typeCode = ParamType::PT_string;

    /**
     * @brief Encode a string.
     * @param out Destination buffer.
     * @param str Pointer to string data.
     * @param len Length of string.
     * @return    Pointer past written data.
     */
    static uint8_t* encode(uint8_t* out, const uint8_t* str, uint8_t len) {
        *out++ = len;
        if (len > 0) {
            memcpy(out, str, len);
            out += len;
        }
        return out;
    }

    /**
     * @brief Encode a null-terminated string.
     */
    static uint8_t* encode(uint8_t* out, const char* str) {
        uint8_t len = static_cast<uint8_t>(strlen(str));
        return encode(out, reinterpret_cast<const uint8_t*>(str), len);
    }

    /**
     * @brief Decode a string. Advances `p` past consumed bytes.
     * @param p     Pointer to pointer to current read position.
     * @param out   Output buffer for the decoded string.
     * @param maxLen Maximum output buffer size.
     * @return      Number of bytes decoded (length of string data).
     */
    static uint8_t decode(const uint8_t* &p, uint8_t* out, uint8_t maxLen) {
        uint8_t len = *p++;
        if (len > maxLen) len = maxLen;
        if (len > 0) {
            memcpy(out, p, len);
            p += len;
        }
        out[len] = '\0';
        return len;
    }
};

/**
 * @class PT_buffer
 * @brief Like PT_string but semantics indicate a raw RAM buffer.
 */
class PT_buffer : public PT_string {
public:
    static constexpr ParamType typeCode = ParamType::PT_buffer;
};

/**
 * @class PT_progmem_buffer
 * @brief Like PT_string but semantics indicate a flash-stored buffer.
 */
class PT_progmem_buffer : public PT_string {
public:
    static constexpr ParamType typeCode = ParamType::PT_progmem_buffer;
};

// ============================================================================
// Message type string → class mapping (compile-time resolution)
// ============================================================================

/**
 * Determine the maximum encoded size of a format string's parameters.
 * Used for compile-time buffer sizing.
 *
 * Format specifiers:
 *   %u  = PT_uint32  (5 bytes)
 *   %i  = PT_int32   (5 bytes)
 *   %hu = PT_uint16  (3 bytes)
 *   %hi = PT_int16   (3 bytes)
 *   %c  = PT_byte    (2 bytes)
 *   %s  = PT_string  (1 + 64 = 65 bytes)
 *   %*s = PT_buffer  (1 + 64 = 65 bytes)
 *   %.*s= PT_progmem_buffer (1 + 64 = 65 bytes)
 */
namespace detail {
    constexpr uint8_t paramMaxSize(const char* fmt) {
        if (fmt[0] == '%') {
            if (fmt[1] == 's' || (fmt[1] == '*' && fmt[2] == 's') ||
                (fmt[1] == '.' && fmt[2] == '*' && fmt[3] == 's'))
                return 65; // string: 1 len byte + up to 64 data bytes
            if (fmt[1] == 'u' || fmt[1] == 'i')
                return 5;  // 32-bit VLQ
            if (fmt[1] == 'h' && (fmt[2] == 'u' || fmt[2] == 'i'))
                return 3;  // 16-bit VLQ
            if (fmt[1] == 'c')
                return 2;  // 8-bit VLQ
        }
        return 0;
    }
}

} // namespace Kalico

#endif // KALICO_MESSAGE_TYPES_H
