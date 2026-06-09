# generic_arduino — Kalico MCU 固件 for Arduino

基于 PlatformIO 的项目，将 Kalico/Klipper 3D 打印机固件的 MCU 代码移植到
**任意 Arduino 兼容板**（AVR、ARM Cortex-M、ESP32 等）。

## 目录

- [概述](#概述)
- [架构](#架构)
- [目录结构](#目录结构)
- [快速开始](#快速开始)
- [接线](#接线)
- [配置](#配置)
  - [使用 TUI 配置工具](#使用-tui-配置工具)
  - [手动编辑](#手动编辑)
- [Klipper 主机配置](#klipper-主机配置)
- [协议流程](#协议流程)
- [限制与注意事项](#限制与注意事项)
- [许可协议](#许可协议)

## 概述

本项目的核心目标是将 Kalico 固件的底层 MCU 通信层移植到 Arduino 平台上。
通过串口（UART/USB）与运行 Klipper 的主机（如树莓派）通信，执行 G 代码
解析后的底层硬件控制命令。

## 架构

```
                         ┌──────────────────────────┐
                         │  主机 (树莓派/PC)         │
                         │  运行 Klipper Python      │
                         └──────────┬───────────────┘
                                    │ UART/USB (250000 波特)
                                    │ Kalico 二进制协议
                         ┌──────────▼───────────────┐
                         │     Arduino 开发板        │
                         │  ┌─────────────────────┐ │
                         │  │   main.cpp           │ │
                         │  │   setup() → sched_main()│
                         │  └─────────┬───────────┘ │
                         │            │              │
                         │  ┌─────────▼───────────┐ │
                         │  │  Kalico 核心 (C)     │ │
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

## 目录结构

```
generic_arduino/
├── platformio.ini              # PlatformIO 构建配置
├── README.md                   # 英文说明（本文件）
├── README_CN.md                # 中文说明（就是你正在看的）
├── tools/
│   ├── requirements.txt        # TUI 配置工具依赖
│   └── configure_autoconf.py   # TUI 配置工具 ⭐
├── src/
│   ├── main.cpp                # Arduino 入口 (setup/loop)
│   ├── autoconf.h              # 静态编译配置（相当于 Kconfig）
│   ├── stepper.h / stepper.c   # 步进电机桩代码
│   │
│   ├── board/                  # 转发头文件 (board/xxx.h → arduino/)
│   │   ├── io.h                # → arduino/io.h
│   │   ├── irq.h               # → arduino/irq.h
│   │   ├── misc.h              # → arduino/misc.h
│   │   ├── pgm.h               # → arduino/pgm.h
│   │   ├── serial_irq.h        # → arduino/serial.h + 声明
│   │   └── timer_irq.h         # → generic/timer_irq.h
│   │
│   ├── arduino/                # Arduino 平台抽象层
│   │   ├── io.h                # 易失读写 (readb/writeb)
│   │   ├── irq.h / irq.c       # noInterrupts()/interrupts() 封装
│   │   ├── misc.h              # 板级 API 声明
│   │   ├── pgm.h               # PROGMEM (AVR) 或空操作 (ARM/ESP32)
│   │   ├── timer.c             # 硬件定时器 (AVR: Timer1, ARM: SysTick)
│   │   ├── serial.c / serial.h # HardwareSerial 封装 (Serial1)
│   │   ├── gpio.c              # digitalWrite/digitalRead/analogWrite
│   │   └── internal.h          # 内部函数声明
│   │
│   ├── generic/                # Kalico 通用层 (从 src/generic/ 复制)
│   │   ├── serial_irq.c / .h   # 通用中断驱动串口
│   │   ├── timer_irq.c / .h    # 通用定时器调度
│   │   ├── crc16_ccitt.c       # CRC-16 CCITT
│   │   └── alloc.c             # 动态内存分配器
│   │
│   └── [Kalico 核心]           # 从 src/ 复制
│       ├── sched.c / sched.h   # 协作式调度器
│       ├── command.c / command.h # 二进制协议引擎
│       ├── basecmd.c / basecmd.h # 基础架构命令
│       ├── debugcmds.c         # 调试命令
│       ├── ctr.h               # 编译时请求宏
│       ├── compiler.h          # GCC 属性助手
│       └── byteorder.h         # 字节序助手
│
└── ../library/KalicoProtocol/  # C++ 库（可选，供主机端使用）
```

## 快速开始

### 前置要求

1. 安装 [PlatformIO](https://platformio.org/)（VS Code 扩展或 CLI）
2. 通过 USB 连接你的 Arduino 开发板

### 编译与上传

```bash
cd other/generic_arduino

# 编译 Arduino Mega（默认）
pio run

# 或指定开发板
pio run -e uno
pio run -e due
pio run -e teensy40
pio run -e esp32dev

# 上传到已连接的开发板
pio run -t upload

# 监视串口输出（USB 调试，115200 波特）
pio device monitor -b 115200
```

### 支持的开发板

| 开发板 | 环境名 | 架构 | 时钟频率 |
|--------|--------|------|----------|
| Arduino Mega 2560 | `mega2560` | AVR | 16 MHz |
| Arduino Uno | `uno` | AVR | 16 MHz |
| Arduino Due | `due` | ARM Cortex-M3 | 84 MHz |
| Teensy 4.0 | `teensy40` | ARM Cortex-M7 | 600 MHz |
| ESP32 DevKit | `esp32dev` | Xtensa LX6 | 240 MHz |

## 接线

| Arduino 引脚 | 连接到 |
|-------------|--------|
| Serial1 TX（Mega 上是 18） | 树莓派 RX（GPIO15 / pin 10） |
| Serial1 RX（Mega 上是 19） | 树莓派 TX（GPIO14 / pin 8） |
| GND | 树莓派 GND |

> **Arduino Uno 注意**：使用 `Serial`（引脚 0/1）会与 USB 上传冲突。
> 请先上传固件，然后断开 USB，改用外部供电。

> **电平转换**：树莓派 GPIO 是 3.3V。如果使用 5V 的 Arduino，
> 请在 RX 引脚上使用电平转换器或分压电阻。

## 配置

### 使用 TUI 配置工具

本项目提供了一个强大的 **终端可视化配置工具**，让您无需手动编辑代码即可
轻松调整所有编译选项。

```bash
# 1. 安装依赖（只需一次）
cd other/generic_arduino
pip install -r tools/requirements.txt

# 2. 启动配置工具
python tools/configure_autoconf.py
```

**工具特性：**

![TUI 配置工具](docs/images/tui-preview.png)
*（终端内操作，上图仅为示意图）*

| 快捷键 | 功能 |
|--------|------|
| `↑/↓` | 导航选项列表 |
| `Tab` | 切换面板（分类 ↔ 选项） |
| `Enter` | 编辑选中的配置值 |
| `/` | 搜索过滤 |
| `s` | 保存修改到文件 |
| `q` / `Esc` | 退出 |
| `?` | 显示帮助 |

**配置项分类：**

- **Machine** — 板型选择、时钟频率
- **Clock** — CPU 时钟配置
- **Serial** — 串口通信参数
- **Memory management** — 内存管理设置
- **Feature flags** — GPIO、ADC、SPI、I2C 等功能开关
- **Stepper configuration** — 步进电机相关

> **提示**：修改后记得按 `s` 保存！保存后会立即写入 `autoconf.h`。

### 手动编辑

你也可以直接编辑 `src/autoconf.h`：

```c
// 时钟频率（查看你的开发板规格）：
//   Uno/Mega: 16000000  (16 MHz)
//   Due:      84000000  (84 MHz)
//   Teensy 4: 600000000 (600 MHz)
//   ESP32:    240000000 (240 MHz)
#define CONFIG_CLOCK_FREQ    16000000UL

// 与主机通信的波特率
#define CONFIG_SERIAL_BAUD    250000

// 按需启用功能：
#define CONFIG_HAVE_GPIO      1    // digitalWrite/Read 支持
#define CONFIG_WANT_ADC       0    // 模拟输入支持
#define CONFIG_WANT_SPI       0    // SPI 支持
#define CONFIG_WANT_I2C       0    // I2C 支持
```

## 编译与刷写 TUI 工具

除了手动执行 `pio run` 命令外，本工具还提供了一个 **终端可视化编译刷写工具**，
让您无需记忆命令即可完成开发板选择、编译、上传和监控的全流程。

```bash
# 启动编译刷写工具（确保先安装依赖）
python tools/build_flash_tui.py
```

**工具截图预览：**

```
┌─────────────────────────────────────────────────────────────────┐
│ 🧩 开发板选择    │ 🎯 操作          │ 📋 编译/刷写日志          │
│───────────────────│──────────────────│──────────────────────────│
│ ◉ Arduino Mega   │ [📦 编译]        │ 📦 开始编译 Arduino      │
│ ○ Arduino Uno    │ [📤 上传]        │ Mega...                  │
│ ○ Arduino Due    │ [🗑️ 清理]        │ Compiling .pio/build/... │
│ ○ Teensy 4.0     │ [🔄 刷新设备]    │ Linking .pio/build/...   │
│ ○ ESP32 DevKit   │ [📟 串口监视]    │ ✅ 编译成功！            │
│───────────────────│──────────────────│                          │
│ ATmega2560 @ 16MHz│ 🔌 串口设备     │                          │
│                   │ • COM3 - Mega    │                          │
└─────────────────────────────────────────────────────────────────┘
```

### 使用流程

1. **选择开发板** — 用 `↑/↓` 选择目标板，按 `Enter` 确认
2. **编译固件** — 按 `b` 键开始编译，实时显示编译日志
3. **连接设备** — 通过 USB 连接开发板，按 `d` 键扫描串口设备
4. **刷写固件** — 按 `u` 键上传固件到开发板
5. **串口监视** — 按 `s` 键启动外部串口监视器查看输出

### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `↑/↓` | 导航选项列表 |
| `Tab` | 切换面板（板子 ↔ 操作 ↔ 日志） |
| `Enter` | 选择板子 / 确认操作 |
| `b` | 编译当前选择的固件 |
| `u` | 上传/刷写固件 |
| `c` | 清理构建文件 |
| `d` | 刷新串口设备列表 |
| `s` | 启动串口监视器 |
| `q` / `Esc` | 退出 |
| `?` | 显示帮助 |

### 支持的开发板

| 环境名 | 开发板 | 架构 |
|--------|--------|------|
| `mega2560` | Arduino Mega 2560 | AVR (ATmega2560) |
| `uno` | Arduino Uno | AVR (ATmega328P) |
| `due` | Arduino Due | ARM Cortex-M3 |
| `teensy40` | Teensy 4.0 | ARM Cortex-M7 |
| `esp32dev` | ESP32 DevKit | Xtensa LX6 |

> **提示**：使用前确保已安装 PlatformIO CLI（`pio` 命令可用），
> 并已通过 USB 连接开发板。

## Klipper 主机配置

在 Klipper 主机上配置 MCU 串口连接：

```ini
[mcu arduino]
serial: /dev/ttyAMA0    # 树莓派内置 UART
# 或
serial: /dev/ttyUSB0    # USB 转串口适配器
baud: 250000
```

### 配置验证

在树莓派上运行以下命令验证连接：

```bash
# 检查 MCU 是否响应
~/klippy/scripts/flash_usb.py -c /dev/ttyAMA0

# 或使用 kalico 调试工具
python other/kalico_debug_tool.py
```

## 协议流程

1. 主机以 250000 波特率连接
2. 主机发送 `identify` 命令（msgid=1）
3. Arduino 回复 `identify_response`（msgid=0）— 包含数据字典
4. 主机解析字典，发现可用的命令列表
5. 正常运行：主机发送命令块，Arduino 分发并回复

## 限制与注意事项

- **默认构建不包含步进电机支持**：启用 `CONFIG_WANT_STEPPER` 可添加步进电机
  控制，这需要移植 `stepper.c`、`endstop.c` 和 `trsync.c`
- **无硬件 PWM 用于伺服/加热器**：`gpio_pwm` 实现较基础（使用 `analogWrite`）。
  如需精确 PWM，请实现硬件定时器
- **轮询式串口**：使用轮询（`Serial.available()`）而非中断驱动串口。
  这种方式更简单，但在高波特率下可能丢失字节
- **无 CAN 总线**：未实现 CAN 传输层
- **内存限制**：AVR 系列（Uno/Mega）RAM 极小（2KB/8KB），
  启用过多功能可能导致溢出
- **ESP32 注意**：ESP32 使用 HardwareSerial(2) 而非 Serial1，
  如有需要请调整 `serial.cpp`

## 许可协议

SPDX-License-Identifier: GPL-3.0-or-later

基于 Kevin O'Connor <kevin@koconnor.net> 的 Kalico 固件代码。
Arduino 移植版贡献者。

---

[⬆ 返回顶部](#generic_arduino--kalico-mcu-固件-for-arduino)
