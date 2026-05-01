/**
 * CRC16.h - CRC-16 CCITT implementation
 *
 * Implements the CRC-16 CCITT algorithm used for message integrity checking
 * in the Kalico binary protocol.
 *
 * Based on crc16_ccitt() from src/generic/crc16_ccitt.c
 * and klippy/msgproto.py.
 */

#ifndef KALICO_CRC16_H
#define KALICO_CRC16_H

#include <stdint.h>

namespace Kalico {

/**
 * @class CRC16CCITT
 * @brief Static CRC-16 CCITT checksum computation.
 *
 * Used by both host and MCU to verify message block integrity.
 * The CRC is calculated over all bytes of the message block
 * EXCLUDING the 3 trailer bytes (CRC high, CRC low, SYNC).
 */
class CRC16CCITT {
public:
    /**
     * @brief Compute CRC-16 CCITT over a buffer.
     * @param buf Pointer to data.
     * @param len Number of bytes.
     * @return 16-bit CRC value.
     */
    static uint16_t compute(const uint8_t* buf, uint_fast8_t len) {
        uint16_t crc = 0xFFFF;
        while (len--) {
            uint8_t data = *buf++;
            data ^= crc & 0xFF;
            data ^= data << 4;
            crc = (((uint16_t)data << 8) | (crc >> 8))
                ^ (uint8_t)(data >> 4)
                ^ ((uint16_t)data << 3);
        }
        return crc;
    }

    /**
     * @brief Compute CRC-16 CCITT over a buffer, returning high/low bytes.
     * @param buf    Pointer to data.
     * @param len    Number of bytes.
     * @param crcHi  Output: high byte of CRC.
     * @param crcLo  Output: low byte of CRC.
     */
    static void computeBytes(const uint8_t* buf, uint_fast8_t len,
                             uint8_t &crcHi, uint8_t &crcLo) {
        uint16_t crc = compute(buf, len);
        crcHi = crc >> 8;
        crcLo = crc & 0xFF;
    }

    /**
     * @brief Verify CRC-16 CCITT of a buffer against expected high/low bytes.
     * @param buf       Pointer to data.
     * @param len       Number of bytes.
     * @param expectedHi Expected CRC high byte.
     * @param expectedLo Expected CRC low byte.
     * @return true if CRC matches, false otherwise.
     */
    static bool verify(const uint8_t* buf, uint_fast8_t len,
                       uint8_t expectedHi, uint8_t expectedLo) {
        uint16_t crc = compute(buf, len);
        return (crc >> 8) == expectedHi && (crc & 0xFF) == expectedLo;
    }
};

} // namespace Kalico

#endif // KALICO_CRC16_H
