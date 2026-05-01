# KalicoProtocol Library

A reusable C++ library implementing the **Kalico/Klipper binary communication
protocol** for use with Arduino and other embedded frameworks.

This library allows any C++ application (Arduino, ESP32, STM32duino, etc.) to
communicate with a Kalico/Klipper MCU firmware over a serial (UART/USB)
connection.

## Features

- **VLQ encoding/decoding** — Compact Variable Length Quantity integers (1–5 bytes)
- **CRC-16 CCITT** — Message integrity verification
- **Message block framing** — Header + payload + CRC + SYNC
- **Message types** — PT_uint32, PT_int32, PT_uint16, PT_int16, PT_byte, PT_string, PT_buffer
- **Message parser** — SYNC detection, block validation, multi-command dispatch
- **Message encoder** — Build and send arbitrary commands
- **Identify protocol** — Download the MCU data dictionary
- **No dynamic allocation** — All buffers are user-provided (embedded-friendly)

## Protocol Overview

```
| Offset | Size | Field                          |
|--------|------|--------------------------------|
| 0      | 1    | Length (total block size, 5-64)|
| 1      | 1    | Sequence (low 4 bits seq | 0x10)|
| 2      | n    | Content (VLQ-encoded commands)  |
| 2+n    | 2    | CRC-16 CCITT                    |
| 2+n+2  | 1    | Sync byte (0x7E)                |
```

For full protocol details, see
[docs/i18n/simple-chinese/Communication_Protocol.md](../../docs/i18n/simple-chinese/Communication_Protocol.md).

## Installation

### Arduino IDE

1. Copy the `KalicoProtocol/` folder into your Arduino `libraries/` directory
2. Restart the Arduino IDE
3. Open `File → Examples → KalicoProtocol → BasicConnect`

### PlatformIO

```ini
lib_deps =
    https://github.com/KalicoCrew/kalico/tree/main/other/library/KalicoProtocol
```

### Manual

Add the `src/` folder to your include path:

```cpp
#include <KalicoProtocol.h>
```

## Quick Start

```cpp
#include <KalicoProtocol.h>

// Create a parser
Kalico::MessageParser parser;

// Response callback
void onResponse(uint16_t msgId, const uint8_t* payload,
                uint8_t payloadLen, void* userData) {
    Serial.print("Response msgId=");
    Serial.println(msgId);
}

void setup() {
    Serial1.begin(250000);  // MCU serial
    parser.setHandler(onResponse);

    // Send identify command
    uint8_t payload[Kalico::MESSAGE_PAYLOAD_MAX];
    uint8_t len = Kalico::MessageEncoder::encodeIdentify(payload, 0, 40);

    uint8_t block[Kalico::MESSAGE_MAX];
    uint8_t blockLen = Kalico::MessageBlock::frame(block, payload, len, 0);
    Serial1.write(block, blockLen);
}

void loop() {
    // Feed received bytes to parser
    while (Serial1.available()) {
        uint8_t c = Serial1.read();
        parser.feed(&c, 1);
    }
}
```

## Files

| File | Description |
|------|-------------|
| `KalicoProtocol.h` | Main include header, protocol constants |
| `VLQ.h` | Variable Length Quantity encode/decode |
| `CRC16.h` | CRC-16 CCITT checksum |
| `MessageTypes.h` | Parameter type classes (PT_uint32 etc.) |
| `MessageBlock.h` | Message block framing/deframing |
| `MessageEncoder.h` | Command encoding |
| `MessageParser.h` | Byte-stream parser and dispatcher |

## Examples

### BasicConnect
Demonstrates connecting to an MCU, performing the identify handshake,
and receiving identify response chunks.

### SendCommand
Demonstrates building and sending arbitrary commands (get_clock, get_status,
emergency_stop) and parsing typed responses.

## License

SPDX-License-Identifier: GPL-3.0-or-later

Based on communication protocol code from Kalico
(Copyright (C) 2016-2024 Kevin O'Connor <kevin@koconnor.net>).
