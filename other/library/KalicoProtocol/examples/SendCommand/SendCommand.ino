/**
 * SendCommand - Arduino example for KalicoProtocol library
 *
 * This example demonstrates how to:
 * 1. Connect to a Kalico/Klipper MCU
 * 2. Build and send arbitrary commands (e.g., get_clock, get_status)
 * 3. Parse and display the responses
 *
 * This assumes the data dictionary has been previously loaded.
 * For a full implementation, combine with BasicConnect's identify flow.
 *
 * Hardware setup:
 *   - Connect Arduino TX → MCU RX
 *   - Connect Arduino RX → MCU TX
 *   - Connect GND → GND
 */

#include <KalicoProtocol.h>

// ============================================================================
// Configuration
// ============================================================================

#define MCU_SERIAL   Serial1
#define MCU_BAUD     250000
#define DEBUG_SERIAL Serial

// ============================================================================
// Protocol objects
// ============================================================================

Kalico::MessageParser parser;
uint8_t g_seq = 0;

// ============================================================================
// Example: Pre-defined command IDs
//
// In a real application, these would come from the data dictionary
// obtained during the identify phase.  These are illustrative values.
// ============================================================================

// Some common command IDs (will vary by firmware build)
static const uint16_t CMD_GET_CLOCK        = 2;   // "get_clock"
static const uint16_t CMD_GET_STATUS       = 3;   // "status"
static const uint16_t CMD_EMERGENCY_STOP   = 4;   // "emergency_stop"
static const uint16_t CMD_FINALIZE_CONFIG  = 5;   // "finalize_config"

// Response IDs
static const uint16_t RSP_STATUS = 0x100;  // "status clock=%u status=%c"

// ============================================================================
// Callbacks
// ============================================================================

void onResponse(uint16_t msgId, const uint8_t* payload, uint8_t payloadLen,
                void* userData) {
    DEBUG_SERIAL.print(F("[MCU→] msgId=0x"));
    DEBUG_SERIAL.print(msgId, HEX);
    DEBUG_SERIAL.print(F(" len="));
    DEBUG_SERIAL.print(payloadLen);

    // Decode known responses
    if (msgId == RSP_STATUS) {
        // "status clock=%u status=%c"
        const uint8_t* p = payload;
        uint32_t clock = Kalico::VLQ::decode(p);
        uint8_t  status = Kalico::VLQ::decode(p);
        DEBUG_SERIAL.print(F(" clock="));
        DEBUG_SERIAL.print(clock);
        DEBUG_SERIAL.print(F(" status="));
        DEBUG_SERIAL.print(status);
    } else {
        // Unknown — print raw bytes
        DEBUG_SERIAL.print(F(" raw="));
        for (uint8_t i = 0; i < payloadLen && i < 16; i++) {
            if (payload[i] < 0x10) DEBUG_SERIAL.print('0');
            DEBUG_SERIAL.print(payload[i], HEX);
        }
    }
    DEBUG_SERIAL.println();
}

// ============================================================================
// Helper: send a command
// ============================================================================

void sendCommand(uint16_t encodedMsgId, uint8_t paramCount, ...) {
    // Build payload
    uint8_t payload[Kalico::MESSAGE_PAYLOAD_MAX];
    uint8_t* p = Kalico::VLQ::encodeMsgId(payload, encodedMsgId);

    va_list args;
    va_start(args, paramCount);
    for (uint8_t i = 0; i < paramCount; i++) {
        uint32_t typeCode = va_arg(args, uint32_t);
        uint32_t val      = va_arg(args, uint32_t);
        Kalico::ParamType pt = static_cast<Kalico::ParamType>(typeCode);
        p = Kalico::MessageEncoder::encodeParam(p, pt, val);
    }
    va_end(args);

    uint8_t payloadLen = p - payload;

    // Frame and send
    uint8_t block[Kalico::MESSAGE_MAX];
    uint8_t blockLen = Kalico::MessageBlock::frame(
        block, payload, payloadLen,
        g_seq & Kalico::MESSAGE_SEQ_MASK
    );
    g_seq++;

    MCU_SERIAL.write(block, blockLen);

    DEBUG_SERIAL.print(F("[→MCU] seq="));
    DEBUG_SERIAL.print((g_seq - 1) & Kalico::MESSAGE_SEQ_MASK);
    DEBUG_SERIAL.print(F(" len="));
    DEBUG_SERIAL.println(blockLen);
}

// ============================================================================
// Arduino setup / loop
// ============================================================================

void setup() {
    DEBUG_SERIAL.begin(115200);
    while (!DEBUG_SERIAL);

    DEBUG_SERIAL.println(F("\n=== KalicoProtocol SendCommand Example ==="));
    DEBUG_SERIAL.println(F("Connecting to MCU at 250000 baud..."));

    MCU_SERIAL.begin(MCU_BAUD);
    parser.setHandler(onResponse);

    DEBUG_SERIAL.println(F("Ready. Type commands in Serial Monitor:"));
    DEBUG_SERIAL.println(F("  c = get_clock"));
    DEBUG_SERIAL.println(F("  s = get_status"));
    DEBUG_SERIAL.println(F("  e = emergency_stop"));
}

void loop() {
    // ---- Receive from MCU ----
    while (MCU_SERIAL.available() > 0) {
        uint8_t buf[64];
        uint16_t toRead = MCU_SERIAL.available();
        if (toRead > sizeof(buf)) toRead = sizeof(buf);
        uint16_t n = MCU_SERIAL.readBytes(buf, toRead);
        parser.feed(buf, n);
    }

    // ---- Send commands via Serial Monitor ----
    if (DEBUG_SERIAL.available() > 0) {
        char cmd = DEBUG_SERIAL.read();
        switch (cmd) {
        case 'c':
            DEBUG_SERIAL.println(F("→ Sending get_clock"));
            // get_clock has no parameters — just msgid
            sendCommand(CMD_GET_CLOCK, 0);
            break;

        case 's':
            DEBUG_SERIAL.println(F("→ Sending get_status"));
            // get_status has no parameters
            sendCommand(CMD_GET_STATUS, 0);
            break;

        case 'e':
            DEBUG_SERIAL.println(F("→ Sending emergency_stop"));
            sendCommand(CMD_EMERGENCY_STOP, 0);
            break;

        case '\n': case '\r':
            // Ignore
            break;

        default:
            DEBUG_SERIAL.print(F("Unknown command: "));
            DEBUG_SERIAL.println(cmd);
            DEBUG_SERIAL.println(F("  c=get_clock  s=get_status  e=emergency_stop"));
            break;
        }
    }
}
