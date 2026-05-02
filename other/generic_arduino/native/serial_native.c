// native/serial_native.c — TCP socket-based serial for host-native build
//
// Kalico protocol runs over a TCP server.  kalico_debug_tool connects
// as a TCP client (via its tcp:// support) directly to this process.
//
// SPDX-License-Identifier: GPL-3.0-or-later

#ifdef _WIN32
  #ifndef _WIN32_WINNT
    #define _WIN32_WINNT 0x0600
  #endif
  #include <winsock2.h>
  #include <ws2tcpip.h>
  typedef SOCKET native_socket_t;
  #define NATIVE_INVALID_SOCKET INVALID_SOCKET
  #define NATIVE_SOCKET_ERROR SOCKET_ERROR
  #define native_close_socket closesocket
  #define native_last_error() WSAGetLastError()
  #define native_would_block() (WSAGetLastError() == WSAEWOULDBLOCK)
#else
  #include <sys/socket.h>
  #include <netinet/in.h>
  #include <arpa/inet.h>
  #include <unistd.h>
  #include <fcntl.h>
  #include <errno.h>
  typedef int native_socket_t;
  #define NATIVE_INVALID_SOCKET (-1)
  #define NATIVE_SOCKET_ERROR (-1)
  #define native_close_socket close
  #define native_last_error() errno
  #define native_would_block() (errno == EAGAIN || errno == EWOULDBLOCK)
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "autoconf.h"
#include "serial_native.h"

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

static native_socket_t _server_sock = NATIVE_INVALID_SOCKET;
static native_socket_t _client_sock = NATIVE_INVALID_SOCKET;
static int _listen_port = 0;
static int _initialized = 0;

// TX buffer (shared with generic/serial_irq.c)
#define TX_BUF_SIZE 128
static uint8_t _tx_buf[TX_BUF_SIZE];
static int _tx_head = 0;
static int _tx_tail = 0;

// RX buffer
#define RX_BUF_SIZE 256
static uint8_t _rx_buf[RX_BUF_SIZE];
static int _rx_head = 0;
static int _rx_tail = 0;

// ---------------------------------------------------------------------------
// Windows socket init
// ---------------------------------------------------------------------------

#ifdef _WIN32
static int _wsa_init_done = 0;
static void _ensure_wsa(void) {
    if (!_wsa_init_done) {
        WSADATA wsa;
        WSAStartup(MAKEWORD(2, 2), &wsa);
        _wsa_init_done = 1;
    }
}
#else
static void _ensure_wsa(void) {}
#endif

// ---------------------------------------------------------------------------
// Non-blocking helper
// ---------------------------------------------------------------------------

static void _set_nonblocking(native_socket_t sock) {
#ifdef _WIN32
    unsigned long mode = 1;
    ioctlsocket(sock, FIONBIO, &mode);
#else
    int flags = fcntl(sock, F_GETFL, 0);
    fcntl(sock, F_SETFL, flags | O_NONBLOCK);
#endif
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

int native_serial_init(int port) {
    _ensure_wsa();

    _server_sock = socket(AF_INET, SOCK_STREAM, 0);
    if (_server_sock == NATIVE_INVALID_SOCKET) {
        fprintf(stderr, "native_serial: failed to create socket\n");
        return -1;
    }

    int opt = 1;
    setsockopt(_server_sock, SOL_SOCKET, SO_REUSEADDR,
               (const char *)&opt, sizeof(opt));

    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    addr.sin_port = htons((unsigned short)port);

    if (bind(_server_sock, (struct sockaddr *)&addr, sizeof(addr)) != 0) {
        fprintf(stderr, "native_serial: bind failed (port %d)\n", port);
        native_close_socket(_server_sock);
        _server_sock = NATIVE_INVALID_SOCKET;
        return -1;
    }

    if (listen(_server_sock, 1) != 0) {
        fprintf(stderr, "native_serial: listen failed\n");
        native_close_socket(_server_sock);
        _server_sock = NATIVE_INVALID_SOCKET;
        return -1;
    }

    _set_nonblocking(_server_sock);

    // Get actual port if using port=0 (auto-assign)
    if (port == 0) {
        socklen_t len = sizeof(addr);
        getsockname(_server_sock, (struct sockaddr *)&addr, &len);
        _listen_port = ntohs(addr.sin_port);
    } else {
        _listen_port = port;
    }

    fprintf(stderr, "[native] Kalico protocol listening on TCP 127.0.0.1:%d (baud=%lu)\n",
            _listen_port, (unsigned long)CONFIG_SERIAL_BAUD);

    _initialized = 1;
    return _listen_port;
}

void native_serial_shutdown(void) {
    if (_client_sock != NATIVE_INVALID_SOCKET) {
        native_close_socket(_client_sock);
        _client_sock = NATIVE_INVALID_SOCKET;
    }
    if (_server_sock != NATIVE_INVALID_SOCKET) {
        native_close_socket(_server_sock);
        _server_sock = NATIVE_INVALID_SOCKET;
    }
    _initialized = 0;
}

void native_serial_poll_rx(void) {
    if (!_initialized) return;

    // Accept new client connections
    if (_client_sock == NATIVE_INVALID_SOCKET && _server_sock != NATIVE_INVALID_SOCKET) {
        struct sockaddr_in client_addr;
        socklen_t len = sizeof(client_addr);
        native_socket_t cs = accept(_server_sock, (struct sockaddr *)&client_addr, &len);
        if (cs != NATIVE_INVALID_SOCKET) {
            _set_nonblocking(cs);
            _client_sock = cs;
            fprintf(stderr, "[native] Client connected\n");
        }
    }

    // Read from client into RX buffer
    if (_client_sock != NATIVE_INVALID_SOCKET) {
        unsigned char buf[256];
        while (1) {
            int n = recv(_client_sock, (char *)buf, sizeof(buf), 0);
            if (n > 0) {
                for (int i = 0; i < n; i++) {
                    serial_rx_byte(buf[i]);
                }
            } else if (n == 0) {
                // Client disconnected
                fprintf(stderr, "[native] Client disconnected\n");
                native_close_socket(_client_sock);
                _client_sock = NATIVE_INVALID_SOCKET;
                break;
            } else {
                if (native_would_block()) break;
                fprintf(stderr, "[native] Client disconnected (error)\n");
                native_close_socket(_client_sock);
                _client_sock = NATIVE_INVALID_SOCKET;
                break;
            }
        }
    }
}

// ---------------------------------------------------------------------------
// Interface consumed by generic/serial_irq.c
// ---------------------------------------------------------------------------

// Declare serial_rx_byte (defined in generic/serial_irq.c)
extern void serial_rx_byte(uint_fast8_t data);
// Declare serial_get_tx_byte (defined in generic/serial_irq.c)
extern int serial_get_tx_byte(uint8_t *pdata);

// serial_enable_tx_irq: called by generic/serial_irq.c when TX buffer has data
void serial_enable_tx_irq(void) {
    // Flush TX buffer to client
    if (_client_sock == NATIVE_INVALID_SOCKET) return;

    uint8_t data;
    while (serial_get_tx_byte(&data) == 0) {
        send(_client_sock, (const char *)&data, 1, 0);
    }
}
