/**
 * arduino/wifi_serial.cpp - WiFi TCP/UDP serial transport for ESP32
 *
 * Provides a network-based serial transport that replaces the standard
 * UART/serial.cpp when CONFIG_WANT_WIFI=1.  The Kalico binary protocol
 * runs transparently over WiFi TCP or UDP instead of a serial port.
 *
 * TCP mode (CONFIG_WIFI_TRANSPORT=0):
 *   ESP32 runs a TCP server on CONFIG_WIFI_PORT.  The host connects as
 *   a TCP client.  Data streams in both directions like a serial port.
 *
 * UDP mode (CONFIG_WIFI_TRANSPORT=1):
 *   ESP32 listens on a UDP port.  Each received datagram is fed into
 *   the Kalico RX buffer.  TX data is sent as individual UDP datagrams
 *   back to the last-known source address.
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"

#if CONFIG_WANT_WIFI
#if defined(ESP32)

#include <WiFi.h>
#include <WiFiUdp.h>

#include "wifi_serial.h"            // our own declarations
#include "wifi_config.h"            // NVS config accessors
#include "../generic/serial_irq.h"  // serial_rx_byte, serial_get_tx_byte

// ============================================================================
// State
// ============================================================================

static bool _wifi_initialized = false;
static bool _wifi_connected   = false;

// Transport mode from NVS (0 = TCP, 1 = UDP)
static int  _transport = 0;
static int  _port      = 5500;

// TCP state
static WiFiServer *_tcp_server = nullptr;
static WiFiClient  _tcp_client;

// UDP state
static WiFiUDP     _udp;
static IPAddress   _remote_ip;
static uint16_t    _remote_port = 0;

// ============================================================================
// Initialization
// ============================================================================

void
wifi_serial_init(void)
{
    // Guard against double-init (called from setup() and ctr_init_list)
    static bool init_done = false;
    if (init_done)
        return;
    init_done = true;

    // Read configuration from NVS (populated by wifi_config_init first)
    _transport = wifi_config_get_transport();
    _port      = wifi_config_get_port();
    String ssid = wifi_config_get_ssid();
    String pass = wifi_config_get_password();

    // ---- Connect to target WiFi AP (if credentials saved) ----
    if (ssid.length() > 0) {
        WiFi.setAutoReconnect(true);
        WiFi.begin(ssid.c_str(), pass.c_str());

        unsigned long start = millis();
        while (WiFi.status() != WL_CONNECTED
               && millis() - start < CONFIG_WIFI_TIMEOUT) {
            delay(100);
        }

        if (WiFi.status() == WL_CONNECTED) {
            _wifi_connected = true;
#if CONFIG_DEBUG_SERIAL_PORT != 2
            Serial.print(F("[WiFi] Connected: "));
            Serial.println(WiFi.localIP());
#endif
        } else {
#if CONFIG_DEBUG_SERIAL_PORT != 2
            Serial.println(F("[WiFi] STA connection failed!"));
#endif
        }
    }

    _wifi_initialized = true;

    // ---- Start Kalico transport server ----
    if (_transport == 0) {
        _tcp_server = new WiFiServer(_port);
        _tcp_server->begin();
        _tcp_server->setNoDelay(true);
#if CONFIG_DEBUG_SERIAL_PORT != 2
        Serial.print(F("[WiFi] TCP server on port "));
        Serial.println(_port);
#endif
    } else {
        _udp.begin(_port);
#if CONFIG_DEBUG_SERIAL_PORT != 2
        Serial.print(F("[WiFi] UDP on port "));
        Serial.println(_port);
#endif
    }

    // ---- Declare constants for host identification ----
    // These appear in the firmware's data dictionary and let klippy
    // verify it connected to the right MCU.
    DECL_CONSTANT("SERIAL_BAUD", CONFIG_SERIAL_BAUD);

    if (_transport == 0) {
        DECL_CONSTANT_STR("MCU_SERIAL_PORT", "WiFi_TCP");
    } else {
        DECL_CONSTANT_STR("MCU_SERIAL_PORT", "WiFi_UDP");
    }
    DECL_CONSTANT("WIFI_PORT", _port);
    DECL_CONSTANT_STR("RESERVE_PINS_serial", "wifi");
}

// ============================================================================
// Polling
// ============================================================================

void
wifi_serial_poll_rx(void)
{
    // Detect late STA connection (e.g. user configured WiFi after boot)
    if (!_wifi_connected && WiFi.status() == WL_CONNECTED) {
        _wifi_connected = true;
#if CONFIG_DEBUG_SERIAL_PORT != 2
        Serial.print(F("[WiFi] Connected: "));
        Serial.println(WiFi.localIP());
#endif
    }

    if (!_wifi_connected)
        return;

    if (_transport == 0) {
        // ── TCP: accept clients, read data ─────────────────────────
        if (!_tcp_client || !_tcp_client.connected()) {
            _tcp_client = _tcp_server->available();
        }
        if (_tcp_client && _tcp_client.connected()) {
            while (_tcp_client.available()) {
                uint8_t c = _tcp_client.read();
                serial_rx_byte(c);
            }
        }
    } else {
        // ── UDP: receive datagrams ───────────────────────────────────
        int packetSize = _udp.parsePacket();
        if (packetSize > 0) {
            _remote_ip   = _udp.remoteIP();
            _remote_port = _udp.remotePort();

            while (_udp.available()) {
                uint8_t c = _udp.read();
                serial_rx_byte(c);
            }
        }
    }

    // Let the ESP32 WiFi/IP stack process background events.
    delay(0);
}

bool
wifi_serial_rx_pending(void)
{
    return _wifi_connected;
}

bool
wifi_serial_is_connected(void)
{
    if (_transport == 0)
        return _wifi_connected && _tcp_client && _tcp_client.connected();
    return _wifi_connected;
}

// ============================================================================
// TX interrupt — shared by TCP and UDP
// ============================================================================

/**
 * Called by generic/serial_irq.c when the Kalico TX buffer has data ready.
 * We flush the buffer to the network socket.
 */
extern "C" void
serial_enable_tx_irq(void)
{
    if (!_wifi_connected)
        return;

    if (_transport == 0) {
        // ── TCP: stream write ─────────────────────────────────────────
        if (!_tcp_client || !_tcp_client.connected())
            return;

        uint8_t data;
        while (serial_get_tx_byte(&data) == 0) {
            _tcp_client.write(data);
        }
        _tcp_client.flush();
    } else {
        // ── UDP: datagram write ───────────────────────────────────────
        if (_remote_port == 0)
            return;

        uint8_t buf[128];
        int len = 0;
        uint8_t data;
        while (len < (int)sizeof(buf) && serial_get_tx_byte(&data) == 0) {
            buf[len++] = data;
        }
        if (len > 0) {
            _udp.beginPacket(_remote_ip, _remote_port);
            _udp.write(buf, len);
            _udp.endPacket();
        }
    }
}

// ============================================================================
// Initialization & task — exported for registrations.c
// ============================================================================

// wifi_poll_task is registered in the task list by registrations.c.
// wifi_serial_init is registered in the init list (or called from setup()).

extern "C" void
wifi_poll_task(void)
{
    wifi_serial_poll_rx();
}

// Graceful shutdown: close client and stop server.
extern "C" void
wifi_shutdown(void)
{
    _wifi_initialized = false;
    if (_transport == 0) {
        _tcp_client.stop();
        if (_tcp_server) {
            _tcp_server->end();
            delete _tcp_server;
            _tcp_server = nullptr;
        }
    } else {
        _udp.stop();
    }
}

#else  // !ESP32
// Stub implementations for non-ESP32 platforms (WiFi not available)

void wifi_serial_init(void)          {}
void wifi_serial_poll_rx(void)       {}
bool wifi_serial_rx_pending(void)    { return false; }
bool wifi_serial_is_connected(void)  { return false; }

#endif // ESP32
#endif // CONFIG_WANT_WIFI
