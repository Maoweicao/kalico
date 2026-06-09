# MCU Connection Methods

This document describes all the ways a micro-controller (MCU) can
connect to the Kalico host (`klippy`), including their internal
architecture, configuration, and trade-offs.

---

## Overview

Kalico supports **six distinct transport methods** for MCU-to-host
communication. Each method ultimately provides a file descriptor (fd)
to the C-level `serialqueue.c` transport layer, which handles message
framing, command queuing, retransmission, and clock synchronization.

| # | Method | Config Key | Transport | Topology |
|---|--------|-----------|-----------|----------|
| 1 | **UART/Serial** | `serial` + `baud` | USB CDC ACM / physical UART | Point-to-point |
| 2 | **CAN Bus** | `canbus_uuid` | SocketCAN | Multi-drop bus |
| 3 | **Pipe / PTY** | `serial` (no baud) | Named pipe / PTY | Local IPC |
| 4 | **TCP** | `tcp_host` + `tcp_port` | TCP/IP stream | Network (wired/WiFi) |
| 5 | **UDP** | `udp_host` + `udp_port` | UDP/IP datagram | Network (wired/WiFi) |
| 6 | **Debug File** | CLI arguments | File replay | Offline debugging |

---

## Internal Architecture

The communication stack has three layers:

```
klippy/mcu.py          ── Configuration, connect/disconnect logic
klippy/serialhdl.py    ── Transport adapters (UART, CAN, TCP, UDP, Pipe, File)
klippy/chelper/serialqueue.c ── Low-level I/O, retransmit, clock tracking
```

The C transport layer (`serialqueue.c`) defines four internal fd types:

| Constant | Value | Description |
|----------|-------|-------------|
| `SQT_UART` | `'u'` | Byte stream over serial device |
| `SQT_CAN` | `'c'` | CAN frames via SocketCAN |
| `SQT_DEBUGFILE` | `'f'` | File-based replay |
| `SQT_TCP` | `'t'` | Byte stream over TCP socket |
| `SQT_UDP` | `'d'` | Datagram over UDP socket |

The transport layer uses Linux epoll (or poll on other platforms) for
asynchronous I/O with a dedicated background thread running at real-time
priority (`SCHED_FIFO`).

---

## 1. UART / Serial (USB)

The most common connection method. The MCU enumerates as a USB CDC ACM
device or communicates over a physical UART.

### Configuration

```ini
[mcu]
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_12345-if00
baud: 250000
restart_method: arduino
```

### How It Works

- **Host**: Opens the serial port via Python `pyserial`, passes the fd
  to `serialqueue_alloc(fd, 'u', 0)`.
- **C layer**: Reads raw bytes, processes message framing via
  `msgblock_check()`. Writes raw bytes via `write()`. On retransmit,
  calls `tcflush(TCOFLUSH)` to flush the UART output buffer.
- **Firmware**: `src/generic/serial_irq.c` handles interrupt-driven
  RX/TX per byte. Platform-specific `serial.c` provides the hardware
  interface.

### Restart Methods

| Method | Description |
|--------|-------------|
| `arduino` | Toggle DTR line (common for Arduino/STM32 boards) |
| `cheetah` | Special sequence for Fysetc Cheetah boards |
| `command` | Send Klipper protocol reset command |
| `rpi_usb` | Toggle USB port power via `hub-ctrl` |

---

## 2. CAN Bus

A multi-drop bus using SocketCAN on Linux. Supports multiple devices
on a single interface, each identified by a UUID.

### Configuration

```ini
[mcu]
canbus_uuid: 0a1b2c3d4e5f
canbus_interface: can0
```

### How It Works

- **Host**: Uses Python `python-can` library with `bustype=socketcan`.
  Sends `CMD_SET_NODEID` admin frame (CAN ID `0x3F0`) to assign a node
  ID. Passes the CAN socket fd as `serialqueue_alloc(fd, 'c', txid)`.
- **C layer**: Reads `struct can_frame` (8 bytes max) from the socket.
  Splits output into 8-byte CAN frames for write.
- **Firmware**: `src/generic/canserial.c` implements the CAN serial
  protocol. `src/generic/canbus.c` wraps platform CAN hardware.

### Tools

- `scripts/canbus_query.py` - Discover CAN bus devices and their UUIDs
- `klippy/extras/canbus_ids.py` - Track CAN node ID assignments
- `klippy/extras/canbus_stats.py` - Report CAN bus status/errors

### CAN Bus Bridge

`src/generic/usb_canbus.c` implements a USB-to-CAN bridge using the
Linux `gs_usb` protocol. This allows an MCU to act as a USB CAN adapter
for other CAN devices.

---

## 3. Pipe / PTY (Linux Process MCU)

Used for the "host MCU" (Linux process) or PRU-based devices
(BeagleBone). Data passes through a local pipe or pseudo-terminal
without hardware serial overhead.

### Configuration

```ini
[mcu host]
serial: /tmp/klipper_host_mcu
```

### How It Works

- **Host**: Opens the file with `os.open(path, O_RDWR | O_NOCTTY)`.
  Passes fd as `serialqueue_alloc(fd, 'u', 0)`. Skips baud rate
  configuration.
- **Firmware**: `src/linux/console.c` creates a PTY via `openpty()`.
  `src/linux/main.c` uses `/tmp/klipper_host_mcu` by default.

### Detection

Paths starting with `/dev/rpmsg_` or `/tmp/klipper_host_` are
automatically treated as pipe connections (no baud required).

---

## 4. TCP (Network Stream)

Connects to an MCU over a TCP/IP network. Suitable for wired Ethernet
or WiFi connections. The MCU must run a TCP server (either natively
or via a bridge device).

### Configuration

```ini
[mcu]
tcp_host: 192.168.1.100
tcp_port: 5500
```

### How It Works

- **Host**: Creates a TCP socket with `TCP_NODELAY` enabled (disables
  Nagle's algorithm for low latency). Connects to `host:port`. Passes
  the socket fd as `serialqueue_alloc(fd, 't', 0)`.
- **C layer**: Reads/writes raw bytes over the socket, identical to
  UART stream mode. No `tcflush` (not applicable to sockets).
- **Restart method**: Always `command` (physical reset methods cannot
  work over a network).

### Connection lifecycle

1. Klippy resolves the hostname and attempts TCP connect
2. On success, starts protocol handshake (data dictionary exchange)
3. On failure, retries every 5 seconds for up to 90 seconds
4. If the connection drops, Klippy detects EOF and triggers reconnect

### Firmware Options

**Option A: Bridge device** (zero firmware changes for existing MCUs)

```
MCU (STM32/AVR/...) ──UART──▶ ESP32/RPi (Bridge) ──TCP──▶ Klippy
```

The bridge runs a TCP-to-UART proxy. The MCU firmware is unchanged.
The bridge device handles WiFi/Ethernet connectivity and exposes the
MCU's UART data stream over TCP.

**Option B: Native TCP in firmware**

The MCU firmware implements a TCP/IP stack directly. Examples:
- STM32 + W5500 Ethernet module (SPI-based)
- ESP32 with built-in WiFi
- Linux MCU with built-in TCP stack

### Example: ESP32 TCP-to-UART Bridge (Pseudocode)

```c
void app_main() {
    wifi_connect("SSID", "password");
    int server = tcp_listen(5500);
    int client = tcp_accept(server);
    uart_init(115200);

    while (1) {
        // TCP → UART
        uint8_t buf[256];
        int len = tcp_read(client, buf, sizeof(buf));
        if (len > 0) uart_write(buf, len);

        // UART → TCP
        len = uart_read(buf, sizeof(buf));
        if (len > 0) tcp_write(client, buf, len);
    }
}
```

---

## 5. UDP (Network Datagram)

Connects to an MCU over UDP/IP. Useful for scenarios where TCP's
connection-oriented overhead is undesirable, or where the underlying
link is inherently datagram-based.

### Configuration

```ini
[mcu]
udp_host: 192.168.1.100
udp_port: 5500
```

### How It Works

- **Host**: Creates a connected UDP socket. Passes the socket fd as
  `serialqueue_alloc(fd, 'd', 0)`.
- **C layer**: `read()` on a connected UDP socket returns one
  datagram's worth of data. `write()` sends the buffer as a single
  UDP datagram. Maximum write buffer size is
  `MESSAGE_MAX (64) * MAX_PENDING_BLOCKS (12) = 768 bytes`, well
  within UDP's 65507-byte limit.
- **Reliability**: UDP does not guarantee delivery. The Klipper
  protocol's built-in sequence numbering and retransmission mechanism
  handles lost datagrams at the application layer.
- **Restart method**: Always `command`.

### Connection lifecycle

1. Klippy "connects" the UDP socket (sets default peer address,
   no packets sent)
2. On success, starts protocol handshake
3. On failure, retries every 5 seconds for up to 90 seconds
4. UDP is connectionless, so "disconnect" cannot be detected at the
   transport layer. The protocol's retransmit timeout handles this.

### When to Use UDP vs TCP

| Aspect | TCP | UDP |
|--------|-----|-----|
| Reliability | Guaranteed delivery | Best-effort |
| Ordering | In-order | No ordering guarantee |
| Connection state | Connection-oriented | Connectionless |
| Latency | Higher (retransmit at TCP level) | Lower |
| Overhead | Connection setup + teardown | Minimal |
| Use case | General remote MCU | Low-latency, LAN only |

---

## 6. Debug File (Offline Replay)

For offline debugging. Klippy reads pre-recorded serial traffic from
files instead of connecting to real hardware.

### Usage

```bash
klippy.py --debugoutput=/tmp/klipper.log --dictionary=/tmp/dict.bin
```

### How It Works

- **Host**: Opens debug output and dictionary files. Processes the
  dictionary directly. Creates `serialqueue_alloc(fd, 'f', 0)`.
- **C layer**: Sets `receive_seq = -1` (no message sync needed) and
  `rto = PR_NEVER` (no retransmission). Reads pre-recorded data from
  file.

---

## Connection Selection Flow

The MCU initialization code selects the transport method based on
config file parameters, evaluated in this order:

1. `tcp_host` is set → **TCP**
2. `udp_host` is set → **UDP**
3. `canbus_uuid` is set → **CAN Bus**
4. `serial` is set, starts with `/dev/rpmsg_` or `/tmp/klipper_host_`
   → **Pipe / PTY**
5. `serial` is set, other path → **UART / Serial**

These options are mutually exclusive. Only one connection method may
be specified per `[mcu]` section.

---

## Multi-MCU Setups

Kalico supports multiple MCUs in a single printer. Each MCU section
can use a different transport method:

```ini
# Main board via USB
[mcu]
serial: /dev/serial/by-id/usb-main_board

# Toolhead board via CAN
[mcu toolhead]
canbus_uuid: 1a2b3c4d5e6f

# Accelerometer via TCP (WiFi)
[mcu accelerometer]
tcp_host: 192.168.1.200
tcp_port: 5500
is_non_critical: True
```

The main `[mcu]` section cannot be marked as non-critical. Secondary
MCUs can use `is_non_critical: True` to allow disconnection without
halting the printer.

---

## Code Reference

### Host-side (Python)

| File | Role |
|------|------|
| `klippy/mcu.py` | MCU class, connect/disconnect logic, config parsing |
| `klippy/serialhdl.py` | SerialReader class with all transport adapters |
| `klippy/chelper/serialqueue.c` | C-level I/O, retransmit, threading |
| `klippy/chelper/serialqueue.h` | C API header |
| `klippy/chelper/pollreactor.c` | epoll/poll event loop |

### Firmware-side (C)

| File | Role |
|------|------|
| `src/generic/serial_irq.c` | Interrupt-driven serial for UART transport |
| `src/generic/canserial.c` | CAN bus serial protocol |
| `src/generic/canbus.c` | CAN hardware abstraction |
| `src/generic/usb_canbus.c` | USB-to-CAN bridge |
| `src/linux/console.c` | PTY console for Linux MCU |
| `src/linux/main.c` | Linux MCU entry point |
| `src/*/serial.c` | Platform-specific UART hardware drivers |

### Tools

| File | Role |
|------|------|
| `scripts/canbus_query.py` | CAN bus device scanner |
| `scripts/console.py` | Debug console (supports all transports) |
| `other/mcu_sim/` | MCU simulator with TCP support for testing |
