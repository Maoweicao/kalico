/**
 * arduino/wifi_config.cpp - Configuration portal for ESP32 WiFi settings
 *
 * On boot this module:
 *   1. Reads saved configuration from NVS (Preferences).
 *   2. Starts a permanent WiFi AP ("Kalico-Config") with a hardcoded
 *      password so the user can always connect to change settings.
 *   3. Starts a tiny web server at http://192.168.4.1/ that displays
 *      the current status and a form to set the target WiFi credentials,
 *      transport mode (TCP / UDP), and Kalico port.
 *
 * The AP NEVER turns off, even after the STA connects to the target
 * WiFi.  Closing the browser keeps the AP alive so the user can
 * reconnect at any time.
 *
 * Copyright (C) 2024 Arduino port contributors.
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#include <Arduino.h>
#include "autoconf.h"

#if CONFIG_WANT_WIFI && defined(ESP32)

#include <WiFi.h>
#include <WebServer.h>
#include <Preferences.h>

#include "wifi_config.h"

// ============================================================================
// NVS keys
// ============================================================================

#define NVS_KEY_SSID        "ssid"
#define NVS_KEY_PASS        "pass"
#define NVS_KEY_TRANSPORT   "transport"
#define NVS_KEY_PORT        "port"

// ============================================================================
// State
// ============================================================================

static WebServer   _web(80);
static Preferences _prefs;
static bool        _ap_started = false;

// Cached NVS values (populated at init time)
static String _saved_ssid;
static String _saved_pass;
static int    _saved_transport = 0;
static int    _saved_port      = 5500;

// ============================================================================
// NVS helpers
// ============================================================================

static void _nvs_load(void)
{
    _prefs.begin(CONFIG_NVS_NAMESPACE, false);
    _saved_ssid      = _prefs.getString(NVS_KEY_SSID, "");
    _saved_pass      = _prefs.getString(NVS_KEY_PASS, "");
    _saved_transport = _prefs.getInt(NVS_KEY_TRANSPORT, CONFIG_WIFI_TRANSPORT);
    _saved_port      = _prefs.getInt(NVS_KEY_PORT, CONFIG_WIFI_PORT);
    _prefs.end();
}

static void _nvs_save(const char *ssid, const char *pass,
                      int transport, int port)
{
    _prefs.begin(CONFIG_NVS_NAMESPACE, false);
    _prefs.putString(NVS_KEY_SSID, ssid);
    _prefs.putString(NVS_KEY_PASS, pass);
    _prefs.putInt(NVS_KEY_TRANSPORT, transport);
    _prefs.putInt(NVS_KEY_PORT, port);
    _prefs.end();

    // Update the cached values
    _saved_ssid      = ssid;
    _saved_pass      = pass;
    _saved_transport = transport;
    _saved_port      = port;
}

// ============================================================================
// Public accessors
// ============================================================================

String wifi_config_get_ssid(void)       { return _saved_ssid; }
String wifi_config_get_password(void)   { return _saved_pass; }
int    wifi_config_get_transport(void)  { return _saved_transport; }
int    wifi_config_get_port(void)       { return _saved_port; }
bool   wifi_config_is_saved(void)       { return _saved_ssid.length() > 0; }

/**
 * Reconnect the STA to the saved WiFi credentials.
 * Called after the user saves new configuration via the web page.
 */
void
wifi_config_reconnect_sta(void)
{
    if (_saved_ssid.length() == 0)
        return;

    // Disconnect from any current AP
    WiFi.disconnect(true);
    delay(200);

    WiFi.begin(_saved_ssid.c_str(), _saved_pass.c_str());
    // Connection will be picked up by wifi_serial_poll_rx() which
    // monitors WiFi.status() on each polling cycle.
}

// ============================================================================
// HTML page (single, self-contained, mobile-friendly)
// ============================================================================

static String _html_page(void)
{
    String sta_status;
    String sta_ip;
    String sta_rssi;

    if (WiFi.status() == WL_CONNECTED) {
        sta_status = "Connected";
        sta_ip     = WiFi.localIP().toString();
        sta_rssi  = String(WiFi.RSSI()) + " dBm";
    } else {
        sta_status = "Not connected";
        sta_ip     = "—";
        sta_rssi  = "—";
    }

    String tcp_sel = (_saved_transport == 0) ? "selected" : "";
    String udp_sel = (_saved_transport == 1) ? "selected" : "";

    String html;
    html.reserve(2048);
    html += F(
        "<!DOCTYPE html><html><head>"
        "<meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>Kalico ESP32 Config</title>"
        "<style>"
        "body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
        "max-width:420px;margin:0 auto;padding:24px 16px;background:#0d1117;color:#c9d1d9}"
        "h1{font-size:1.3em;text-align:center;color:#58a6ff;margin-bottom:20px}"
        "h2{font-size:1.0em;color:#8b949e;border-bottom:1px solid #30363d;padding-bottom:4px;margin:20px 0 12px}"
        ".card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:12px 16px;margin-bottom:16px}"
        ".card p{margin:4px 0;font-size:0.9em}"
        ".val{float:right;color:#7ee787}"
        "label{display:block;margin-bottom:10px;font-size:0.9em;color:#c9d1d9}"
        "label span{display:block;margin-bottom:2px}"
        "input,select{box-sizing:border-box;width:100%;padding:8px 10px;"
        "background:#0d1117;border:1px solid #30363d;border-radius:4px;"
        "color:#c9d1d9;font-size:0.9em}"
        "input:focus,select:focus{outline:none;border-color:#58a6ff}"
        "button{width:100%;padding:10px;background:#238636;color:#fff;border:none;"
        "border-radius:4px;font-size:0.95em;font-weight:600;cursor:pointer;margin-top:10px}"
        "button:active{background:#2ea043}"
        ".note{font-size:0.78em;color:#8b949e;text-align:center;margin-top:20px}"
        "input[type=password]{letter-spacing:4px}"
        "</style></head><body>"
        "<h1>Kalico ESP32 Config</h1>"

        // ---- Status ----
        "<h2>Status</h2><div class=\"card\">"
        "<p>STA <span class=\"val\">" + sta_status + "</span></p>"
        "<p>IP <span class=\"val\">" + sta_ip + "</span></p>"
        "<p>RSSI <span class=\"val\">" + sta_rssi + "</span></p>"
        "<p>AP Clients <span class=\"val\">" + String(WiFi.softAPgetStationNum()) + "</span></p>"
        "</div>"

        // ---- Form ----
        "<h2>WiFi Settings</h2>"
        "<form method=\"POST\" action=\"/save\">"
        "<label><span>SSID</span>"
        "<input name=\"ssid\" maxlength=\"32\" value=\"" + _saved_ssid + "\" required></label>"
        "<label><span>Password</span>"
        "<input name=\"pass\" type=\"password\" maxlength=\"63\"></label>"
        "<label><span>Mode</span>"
        "<select name=\"transport\">"
        "<option value=\"0\" " + tcp_sel + ">TCP (reliable)</option>"
        "<option value=\"1\" " + udp_sel + ">UDP (fast)</option>"
        "</select></label>"
        "<label><span>Port</span>"
        "<input name=\"port\" type=\"number\" min=\"1\" max=\"65535\" value=\"" + String(_saved_port) + "\" required></label>"
        "<button type=\"submit\">Save &amp; Reconnect</button>"
        "</form>"

        "<p class=\"note\">AP stays on permanently.</p>"
        "</body></html>"
    );

    return html;
}

// ============================================================================
// Web route handlers
// ============================================================================

static void _handle_root(void)
{
    _web.send(200, "text/html", _html_page());
}

static void _handle_save(void)
{
    if (!_web.hasArg("ssid") || !_web.hasArg("pass")) {
        _web.send(400, "text/html",
                  "<p>Missing SSID or password.</p><a href=\"/\">Back</a>");
        return;
    }

    String ssid  = _web.arg("ssid");
    String pass  = _web.arg("pass");
    int    trans = _web.arg("transport").toInt();
    int    port  = _web.arg("port").toInt();

    if (ssid.length() == 0) {
        _web.send(400, "text/html",
                  "<p>SSID is required.</p><a href=\"/\">Back</a>");
        return;
    }
    if (port < 1 || port > 65535)
        port = CONFIG_WIFI_PORT;
    if (trans < 0 || trans > 1)
        trans = 0;

    // Save to NVS
    _nvs_save(ssid.c_str(), pass.c_str(), trans, port);

    // Response page
    String html;
    html.reserve(512);
    html += F(
        "<!DOCTYPE html><html><head>"
        "<meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<meta http-equiv=\"refresh\" content=\"3;url=/\">"
        "<style>body{font-family:-apple-system,BlinkMacSystemFont,sans-serif;"
        "max-width:420px;margin:40px auto;text-align:center;"
        "background:#0d1117;color:#c9d1d9}"
        ".ok{color:#7ee787;font-size:2em}"
        "</style></head><body>"
        "<p class=\"ok\">&#10004;</p>"
        "<p>Saved. ESP32 will now connect to <strong>" + ssid + "</strong>.</p>"
        "<p>If the WiFi LED stops blinking, check the Klippy host config.<br>"
        "Redirecting in 3 seconds…</p>"
    );

    if (trans == 0)
        html += "<p>Mode: TCP, Port: " + String(port) + "</p>";
    else
        html += "<p>Mode: UDP, Port: " + String(port) + "</p>";

    html += F("</body></html>");

    _web.send(200, "text/html", html);

    // Trigger STA reconnect with the new credentials.
    // The wifi_serial poll loop will detect the new connection.
    wifi_config_reconnect_sta();
}

static void _handle_not_found(void)
{
    _web.send(404, "text/plain", "Not Found");
}

// ============================================================================
// AP startup
// ============================================================================

static void _ap_start(void)
{
    IPAddress ap_ip(CONFIG_AP_IP);
    WiFi.mode(WIFI_AP_STA);
    WiFi.softAPConfig(ap_ip, ap_ip, IPAddress(255, 255, 255, 0));

    bool ok = WiFi.softAP(CONFIG_AP_SSID, CONFIG_AP_PASSWORD);
    _ap_started = ok;

#if CONFIG_DEBUG_SERIAL_PORT != 2
    if (ok) {
        Serial.print(F("[Config] AP started: "));
        Serial.println(CONFIG_AP_SSID);
        Serial.print(F("[Config] Web config: http://"));
        Serial.print(ap_ip);
        Serial.println(F("/"));
    } else {
        Serial.println(F("[Config] AP start failed!"));
    }
#endif
}

// ============================================================================
// Web server
// ============================================================================

static void _web_start(void)
{
    _web.on("/",      HTTP_GET,  _handle_root);
    _web.on("/save",  HTTP_POST, _handle_save);
    _web.onNotFound(_handle_not_found);
    _web.begin();
}

static void _web_stop(void)
{
    _web.stop();
}

// ============================================================================
// Public init / shutdown
// ============================================================================

/**
 * Called once at boot (from sched_main → ctr_init_list).
 * Reads NVS, starts the config AP, and launches the web server.
 */
extern "C" void
wifi_config_init(void)
{
    static bool init_done = false;
    if (init_done)
        return;
    init_done = true;

    _nvs_load();
    _ap_start();
    _web_start();
}

/**
 * Poll the config web server.  Must be called regularly from the
 * Kalico task loop so that HTTP requests are handled.
 */
extern "C" void
wifi_config_poll_task(void)
{
    _web.handleClient();
}

/**
 * Graceful shutdown (from sched_shutdown).
 */
extern "C" void
wifi_config_shutdown(void)
{
    _web_stop();
    WiFi.softAPdisconnect(false);
}

#endif // CONFIG_WANT_WIFI && ESP32
