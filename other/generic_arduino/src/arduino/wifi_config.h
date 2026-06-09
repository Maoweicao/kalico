/**
 * arduino/wifi_config.h - Configuration portal for ESP32 WiFi settings
 *
 * Provides:
 *   - A persistent WiFi Access Point ("Kalico-Config") that stays on
 *     permanently so the user can always reconnect to change settings.
 *   - A lightweight web server at http://192.168.4.1 with an HTML form
 *     for setting the target WiFi SSID, password, transport mode (TCP/UDP),
 *     and Kalico protocol port.
 *   - NVS (non-volatile storage) for saving configuration across reboots.
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#ifndef __ARDUINO_WIFI_CONFIG_H
#define __ARDUINO_WIFI_CONFIG_H

#ifdef __cplusplus
extern "C" {
#endif

void wifi_config_init(void);
void wifi_config_shutdown(void);
void wifi_config_reconnect_sta(void);

#ifdef __cplusplus
}
#endif

#ifdef __cplusplus
// C++-only convenience accessors for the saved NVS config.
// These return String values; call .c_str() for C strings.

#include <WString.h>

String wifi_config_get_ssid(void);
String wifi_config_get_password(void);
int    wifi_config_get_transport(void);
int    wifi_config_get_port(void);
bool   wifi_config_is_saved(void);

#endif // __cplusplus

#endif // __ARDUINO_WIFI_CONFIG_H
