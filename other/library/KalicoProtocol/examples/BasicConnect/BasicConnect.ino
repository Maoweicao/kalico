/**
 * BasicConnect - Arduino example for KalicoProtocol library
 *
 * This example demonstrates how to:
 * 1. Establish a connection to a Kalico/Klipper MCU over Serial
 * 2. Perform the "identify" handshake to download the data dictionary
 * 3. Parse and print identify_response data
 *
 * Hardware setup:
 *   - Connect Arduino TX → MCU RX
 *   - Connect Arduino RX → MCU TX
 *   - Connect GND → GND
 *   - For 5V Arduino with 3.3V MCU, use a level shifter
 *
 * Baud rate: 250000 (typical Kalico default)
 */

#include <KalicoProtocol.h>

// ============================================================================
// Configuration
// ============================================================================

// Use Serial1 (hardware UART) for MCU communication
#define MCU_SERIAL  Serial1
#define MCU_BAUD    250000

// Use Serial (USB) for debug output
#define DEBUG_SERIAL Serial

// ============================================================================
// Kalico protocol objects
// ============================================================================

Kalico::MessageParser parser;
uint8_t identifyBuffer[Kalico::MESSAGE_MAX];

// ============================================================================
// Callbacks
// ============================================================================

/**
 * Called for each identify_response chunk from the MCU.
 * The identify data is zlib-compressed JSON describing available
 * commands, responses, enumerations, and constants.
 */
void onIdentifyData(uint32_t offset, const uint8_t* data, uint8_t dataLen,
                    void* userData) {
    DEBUG_SERIAL.print(F("[IDENTIFY] offset="));
    DEBUG_SERIAL.print(offset);
    DEBUG_SERIAL.print(F(" len="));
    DEBUG_SERIAL.println(dataLen);

    // In a full implementation, you would accumulate these chunks,
    // decompress with zlib, and parse the JSON data dictionary.
    // For this basic example, we just print the raw bytes.
    DEBUG_SERIAL.print(F("  Data (hex): "));
    for (uint8_t i = 0; i < dataLen && i < 32; i++) {
        if (data[i] < 0x10) DEBUG_SERIAL.print('0');
        DEBUG_SERIAL.print(data[i], HEX);
        DEBUG_SERIAL.print(' ');
    }
    if (dataLen > 32) DEBUG_SERIAL.print(F("..."));
    DEBUG_SERIAL.println();
}

/**
 * Called for general response messages from the MCU.
 */
void onResponse(uint16_t msgId, const uint8_t* payload, uint8_t payloadLen,
                void* userData) {
    DEBUG_SERIAL.print(F("[RESPONSE] msgId="));
    DEBUG_SERIAL.print(msgId);
    DEBUG_SERIAL.print(F(" payloadLen="));
    DEBUG_SERIAL.println(payloadLen);
}

// ============================================================================
// Helper: send a framed command block to the MCU
// ============================================================================

uint8_t g_seq = 0;

void sendBlock(const uint8_t* content, uint8_t contentLen) {
    uint8_t blockBuf[Kalico::MESSAGE_MAX];
    uint8_t blockLen = Kalico::MessageBlock::frame(
        blockBuf, content, contentLen,
        g_seq & Kalico::MESSAGE_SEQ_MASK
    );
    g_seq++;

    MCU_SERIAL.write(blockBuf, blockLen);

    DEBUG_SERIAL.print(F("[SEND] seq="));
    DEBUG_SERIAL.print((g_seq - 1) & Kalico::MESSAGE_SEQ_MASK);
    DEBUG_SERIAL.print(F(" len="));
    DEBUG_SERIAL.println(blockLen);
}

/**
 * Send the "identify" command to request a chunk of the data dictionary.
 */
void sendIdentify(uint32_t offset, uint8_t count) {
    uint8_t payload[Kalico::MESSAGE_PAYLOAD_MAX];
    uint8_t payloadLen = Kalico::MessageEncoder::encodeIdentify(
        payload, offset, count
    );
    sendBlock(payload, payloadLen);
}

// ============================================================================
// Arduino setup / loop
// ============================================================================

void setup() {
    DEBUG_SERIAL.begin(115200);
    while (!DEBUG_SERIAL); // Wait for USB serial on native USB boards

    DEBUG_SERIAL.println(F("\n=== KalicoProtocol BasicConnect Example ==="));
    DEBUG_SERIAL.println(F("Connecting to MCU..."));

    MCU_SERIAL.begin(MCU_BAUD);

    // Configure parser callbacks
    parser.setHandler(onResponse);
    parser.setIdentifyHandler(onIdentifyData);

    // Send initial identify request (offset=0, count=40 = full block)
    DEBUG_SERIAL.println(F("Sending identify request..."));
    sendIdentify(0, 40);

    DEBUG_SERIAL.println(F("Ready. Waiting for MCU responses..."));
}

void loop() {
    // Read all available bytes from MCU serial and feed to parser
    while (MCU_SERIAL.available() > 0) {
        uint8_t buf[64];
        uint16_t toRead = MCU_SERIAL.available();
        if (toRead > sizeof(buf)) toRead = sizeof(buf);

        uint16_t n = MCU_SERIAL.readBytes(buf, toRead);

        // Feed bytes to parser
        uint16_t consumed = parser.feed(buf, n);

        // Any unconsumed bytes remain in buf for next iteration.
        // In a robust implementation, you'd use a ring buffer.
        if (consumed < n) {
            DEBUG_SERIAL.print(F("[WARN] Parser consumed only "));
            DEBUG_SERIAL.print(consumed);
            DEBUG_SERIAL.print(F(" of "));
            DEBUG_SERIAL.println(n);
        }
    }

    // Periodically request more identify data
    // (In a complete implementation, you'd track progress and request
    //  additional chunks until the full data dictionary is received.)
    static unsigned long lastIdentify = 0;
    if (millis() - lastIdentify > 5000) {
        lastIdentify = millis();
        DEBUG_SERIAL.println(F("Re-sending identify request..."));
        sendIdentify(0, 40);
    }
}
