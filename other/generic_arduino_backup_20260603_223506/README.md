# generic_arduino — Kalico MCU Firmware for Arduino

> **🌐 Languages**: English · [简体中文](README_CN.md)

A PlatformIO-based project that ports the Kalico/Klipper 3D printer firmware
MCU code to run on **any Arduino-compatible board** (AVR, ARM Cortex-M,
ESP32, etc.).

## Architecture

```
                         ┌──────────────────────────┐
                         │  Host (Raspberry Pi/PC)  │
                         │  running Klipper Python   │
                         └──────────┬───────────────┘
                                    │ UART/USB (250000 baud)
                                    │ Kalico Binary Protocol
                         ┌──────────▼───────────────┐
                         │     Arduino Board         │
                         │  ┌─────────────────────┐ │
                         │  │   main.cpp           │ │
                         │  │   setup() → sched_main()│
                         │  └─────────┬───────────┘ │
                         │            │              │
                         │  ┌─────────▼───────────┐ │
                         │  │  Kalico Core (C)     │ │
                         │  │  sched.c  command.c  │ │
                         │  │  basecmd.c           │ │
                         │  └─────────┬───────────┘ │
                         │            │              │
                         │  ┌─────────▼───────────┐ │
                         │  │  Arduino HAL (C)     │ │
                         │  │  serial.c timer.c    │ │
                         │  │  gpio.c  irq.c       │ │
                         │  └─────────────────────┘ │
                         └──────────────────────────┘
```

## Directory Structure

```
generic_arduino/
├── platformio.ini              # PlatformIO build configuration
├── README.md                   # This file (English)
├── README_CN.md                # Documentation in Chinese
├── tools/
│   ├── requirements.txt        # TUI config tool dependencies
│   └── configure_autoconf.py   # TUI configuration tool ⭐
├── src/
│   ├── main.cpp                # Arduino entry point (setup/loop)
│   ├── autoconf.h              # Static Kconfig-equivalent configuration
│   ├── stepper.h / stepper.c   # Stepper stub (for builds without steppers)
│   │
│   ├── board/                  # Forwarding headers (board/xxx.h → arduino/)
│   │   ├── io.h                # → arduino/io.h
│   │   ├── irq.h               # → arduino/irq.h
│   │   ├── misc.h              # → arduino/misc.h
│   │   ├── pgm.h               # → arduino/pgm.h
│   │   ├── serial_irq.h        # → arduino/serial.h + declarations
│   │   └── timer_irq.h         # → generic/timer_irq.h
│   │
│   ├── arduino/                # Arduino platform abstraction layer
│   │   ├── io.h                # Volatile read/write (readb/writeb)
│   │   ├── irq.h / irq.c       # noInterrupts()/interrupts() wrappers
│   │   ├── misc.h              # Board API declarations
│   │   ├── pgm.h               # PROGMEM (AVR) or no-op (ARM/ESP32)
│   │   ├── timer.c             # Hardware timer (AVR: Timer1, ARM: SysTick)
│   │   ├── serial.c / serial.h # HardwareSerial wrapper (Serial1)
│   │   ├── gpio.c              # digitalWrite/digitalRead/analogWrite
│   │   └── internal.h          # Internal function declarations
│   │
│   ├── generic/                # Kalico generic layer (copied from src/generic/)
│   │   ├── serial_irq.c / .h   # Generic interrupt-driven serial
│   │   ├── timer_irq.c / .h    # Generic timer dispatch
│   │   ├── crc16_ccitt.c       # CRC-16 CCITT
│   │   └── alloc.c             # Dynamic memory allocator
│   │
│   └── [Kalico core]           # Copied from src/
│       ├── sched.c / sched.h   # Cooperative scheduler
│       ├── command.c / command.h # Binary protocol engine
│       ├── basecmd.c / basecmd.h # Infrastructure commands
│       ├── debugcmds.c         # Debug commands
│       ├── ctr.h               # Compile-time request macros
│       ├── compiler.h          # GCC attribute helpers
│       └── byteorder.h         # Endianness helpers
│
└── ../library/KalicoProtocol/  # C++ library (optional, for host-side code)
```

## Quick Start

### Prerequisites

1. Install [PlatformIO](https://platformio.org/) (VS Code extension or CLI)
2. Connect your Arduino board via USB

### Build & Upload

```bash
cd other/generic_arduino

# Build for Arduino Mega (default)
pio run

# Or specify a different board
pio run -e uno
pio run -e due
pio run -e teensy40
pio run -e esp32dev

# Upload to connected board
pio run -t upload

# Monitor serial output (USB debug at 115200 baud)
pio device monitor -b 115200
```

### Wiring

| Arduino Pin | Connect To |
|-------------|-----------|
| Serial1 TX (18 on Mega) | Raspberry Pi RX (GPIO15 / pin 10) |
| Serial1 RX (19 on Mega) | Raspberry Pi TX (GPIO14 / pin 8) |
| GND | Raspberry Pi GND |

> **Note for Arduino Uno**: Use `Serial` (pins 0/1) but this conflicts with USB
> upload. Upload first, then disconnect USB and power externally.

> **Level shifting**: Raspberry Pi GPIO is 3.3V. If using a 5V Arduino, use a
> level shifter or voltage divider on the RX pin.

### Configuration

You can configure the firmware using **two methods**:

#### 🖥️ TUI Configuration Tool (recommended)

A terminal-based visual configuration tool is provided:

```bash
# Install dependency (one-time)
pip install -r tools/requirements.txt

# Launch the TUI configurator
python tools/configure_autoconf.py
```

| Key | Action |
|-----|--------|
| `↑/↓` | Navigate options |
| `Tab` | Switch panel (category ↔ options) |
| `Enter` | Edit selected value |
| `/` | Search |
| `s` | Save changes |
| `q` / `Esc` | Quit |
| `?` | Show help |

The tool parses `autoconf.h` and presents all options organized by category
(Machine, Clock, Serial, Memory, Features, Stepper, etc.). Changes are saved
directly back to the file.

#### ✏️ Manual Editing

Edit `src/autoconf.h` directly:

```c
// Clock frequency (check your board's specs):
//   Uno/Mega: 16000000  (16 MHz)
//   Due:      84000000  (84 MHz)
//   Teensy 4: 600000000 (600 MHz)
//   ESP32:    240000000 (240 MHz)
#define CONFIG_CLOCK_FREQ    16000000UL

// Baud rate for host communication
#define CONFIG_SERIAL_BAUD    250000

// Enable features as needed:
#define CONFIG_HAVE_GPIO      1    // digitalWrite/Read support
#define CONFIG_WANT_ADC       0    // analog input support
#define CONFIG_WANT_SPI       0    // SPI support
#define CONFIG_WANT_I2C       0    // I2C support
```

## 🔨 Build & Flash TUI Tool

In addition to running `pio run` manually, this project provides a **terminal-based
visual build & flash tool** with board selection, device detection, one-click
build/upload, and serial monitor launch.

```bash
# Launch the build & flash TUI (dependencies must be installed first)
python tools/build_flash_tui.py
```

**Layout preview:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 🧩 Board Selection  │ 🎯 Actions       │ 📋 Build/Flash Log    │
│──────────────────────│──────────────────│───────────────────────│
│ ◉ Arduino Mega      │ [📦 Build]       │ 📦 Building Arduino   │
│ ○ Arduino Uno       │ [📤 Upload]      │ Mega...               │
│ ○ Arduino Due       │ [🗑️  Clean]      │ Compiling .pio/...   │
│ ○ Teensy 4.0        │ [🔄 Refresh]     │ ✅ Build successful!  │
│ ○ ESP32 DevKit      │ [📟 Monitor]     │                       │
│──────────────────────│──────────────────│                       │
│ ATmega2560 @ 16MHz  │ 🔌 Serial Devices│                       │
│                      │ • COM3 - Mega    │                       │
└─────────────────────────────────────────────────────────────────┘
```

### Workflow

1. **Select board** — Use `↑/↓` to pick your target, press `Enter` to confirm
2. **Build firmware** — Press `b` to compile with real-time log output
3. **Connect device** — Plug in the board via USB, press `d` to scan serial ports
4. **Flash firmware** — Press `u` to upload the firmware to the board
5. **Serial monitor** — Press `s` to launch an external serial monitor

### Key Bindings

| Key | Action |
|-----|--------|
| `↑/↓` | Navigate lists |
| `Tab` | Switch panel (Board ↔ Actions ↔ Log) |
| `Enter` | Select board / confirm |
| `b` | Build firmware for selected board |
| `u` | Upload / flash firmware |
| `c` | Clean build artifacts |
| `d` | Refresh serial device list |
| `s` | Launch serial monitor |
| `q` / `Esc` | Quit |
| `?` | Show help |

### Supported Boards

| Env Name | Board | Architecture |
|----------|-------|-------------|
| `mega2560` | Arduino Mega 2560 | AVR (ATmega2560) |
| `uno` | Arduino Uno | AVR (ATmega328P) |
| `due` | Arduino Due | ARM Cortex-M3 |
| `teensy40` | Teensy 4.0 | ARM Cortex-M7 |
| `esp32dev` | ESP32 DevKit | Xtensa LX6 |

> **Note**: Ensure PlatformIO CLI (`pio` command) is available and your
> board is connected via USB before building/flashing.

### Klipper Host Configuration

On the Klipper host, configure the MCU serial connection:

```ini
[mcu arduino]
serial: /dev/ttyAMA0    # Raspberry Pi built-in UART
# or
serial: /dev/ttyUSB0    # USB-to-serial adapter
baud: 250000
```

## Protocol Flow

1. Host connects at 250000 baud
2. Host sends `identify` command (msgid=1)
3. Arduino responds with `identify_response` (msgid=0) — data dictionary
4. Host parses the dictionary to discover available commands
5. Normal operation: host sends command blocks, Arduino dispatches + responds

## Limitations

- **No stepper support in default build**: Enable `CONFIG_WANT_STEPPER` to add
  stepper motor control. This requires porting `stepper.c`, `endstop.c`, and
  `trsync.c`.
- **No hardware PWM for servos/heaters**: The `gpio_pwm` implementation is
  basic (uses `analogWrite`). For precise PWM, implement a hardware timer.
- **Polled serial**: Uses polling (`Serial.available()`) instead of interrupt-
  driven serial. This is simpler but may miss bytes at very high baud rates.
- **No CAN bus**: The CAN transport is not implemented.

## License

SPDX-License-Identifier: GPL-3.0-or-later

Based on Kalico firmware code by Kevin O'Connor <kevin@koconnor.net>.
Arduino port contributors.
