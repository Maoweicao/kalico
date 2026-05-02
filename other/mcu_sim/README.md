# mcu_sim — Kalico MCU 固件模拟器

基于 QEMU 的 MCU 固件模拟器，无需真实硬件即可测试 Kalico 二进制协议。
加载 `generic_arduino` 编译产物（`.hex` / `.bin` / `.elf`），以指令级精度
执行固件，暴露虚拟串口 TCP 端口供 `kalico_debug_tool` 连接。

## 支持的 MCU

| MCU | 开发板 | 架构 | QEMU 后端 |
|-----|--------|------|-----------|
| ATmega328P | Arduino Uno | AVR 8-bit | `qemu-system-avr` |
| ATmega2560 | Arduino Mega 2560 | AVR 8-bit | `qemu-system-avr` |
| ATSAM3X8E | Arduino Due | ARM Cortex-M3 | `qemu-system-arm` |
| iMXRT1062 | Teensy 4.0 | ARM Cortex-M7 | `qemu-system-arm` * |
| ESP32 | ESP32 DevKit | Xtensa LX6 | `qemu-system-xtensa` |

> \* iMXRT1062 的 QEMU 支持有限，外设模拟不完整。

## 快速开始

### 1. 安装 QEMU

```bash
# Windows (MSYS2 / Chocolatey / winget)
winget install qemu

# Linux (Debian/Ubuntu)
sudo apt install qemu-system-avr qemu-system-arm

# macOS
brew install qemu
```

### 2. 编译 generic_arduino 固件

```bash
cd other/generic_arduino

# 编译 Arduino Mega (推荐)
pio run -e mega2560

# 或编译 Uno
pio run -e uno

# 固件在 .pio/build/mega2560/firmware.hex
```

### 3. 启动模拟器（推荐：纯 Python 模式）

```bash
cd other/mcu_sim

# 启动 Python MCU 模拟器 — 零依赖，即开即用
python -m mcu_sim serve

# 或指定端口
python -m mcu_sim serve --port 25000 --name my-mcu

# 输出:
# ==================================================
# Python MCU 'my-mcu' started!
#   Clock:  16 MHz
#   Port:   TCP 127.0.0.1:25000
# ==================================================
# Connect: kalico_debug_tool connect tcp:127.0.0.1:25000
```
#   Firmware:  firmware.hex
#   Serial:    TCP 127.0.0.1:12345
# ============================================================
# Connect with: kalico_debug_tool connect tcp:127.0.0.1:12345
```

### 4. 连接 kalico_debug_tool

```bash
# 新终端窗口
cd other
python -m kalico_debug_tool

# 在 kalico_debug_tool 的 CLI 中:
> connect tcp:127.0.0.1:12345
> send_command identify offset=0 count=40
> get_messages
```

### 5. 一键冒烟测试

```bash
python -m mcu_sim test ../generic_arduino/.pio/build/mega2560/firmware.hex --mcu atmega2560
```

## CLI 命令

```
python -m mcu_sim <command> [options]

命令:
  serve     启动纯 Python MCU 模拟器 (推荐, 零依赖)
  run       加载固件并用 QEMU 启动模拟 (需 QEMU)
  test      一键冒烟测试 (identify 协议验证)
  info      查看固件文件元数据
  backends  列出已安装的 QEMU 后端

serve 选项:
  --port, -p     TCP 端口 (0=自动, 默认: 0)
  --name         MCU 名称 (默认: py-mcu)

run 选项:
  firmware       .hex / .bin / .elf 固件路径
  --mcu, -m      MCU 型号
  --port, -p     TCP 端口
  --no-wait      不等待 MCU 就绪
  --oneshot      运行冒烟测试后退出

## 架构

```
                         ┌───────────────────────────────┐
                         │  kalico_debug_tool            │
                         │  (SerialIO → tcp:host:port)   │
                         └──────────────┬────────────────┘
                                        │ TCP
                         ┌──────────────▼────────────────┐
                         │  mcu_sim (Python)             │
                         │  ┌─────────────────────────┐  │
                         │  │  VirtualSerialBridge    │  │
                         │  │  TCP ↔ QEMU stdio       │  │
                         │  └────────┬────────────────┘  │
                         │           │ stdin/stdout       │
                         │  ┌────────▼────────────────┐  │
                         │  │  QEMU Process           │  │
                         │  │  -nographic             │  │
                         │  │  -serial stdio          │  │
                         │  │  -M mega2560            │  │
                         │  │  -bios firmware.hex      │  │
                         │  └─────────────────────────┘  │
                         └───────────────────────────────┘
```

### 数据流

1. `kalico_debug_tool` 发送 Kalico 二进制协议帧 → TCP
2. `VirtualSerialBridge` 转发 → QEMU stdin
3. QEMU 将字节送入模拟 ATmega2560 的 UART
4. 固件的 `serial_rx_byte()` 中断处理接收字节
5. `command_find_block()` + `command_dispatch()` 处理命令
6. 响应通过 UART TX → QEMU stdout
7. `VirtualSerialBridge` 转发 → TCP → `kalico_debug_tool`

## 目录结构

```
mcu_sim/
├── pyproject.toml
├── README.md
├── requirements.txt
├── mcu_sim/
│   ├── __init__.py           # 包入口, 导出公共 API
│   ├── __main__.py           # python -m mcu_sim
│   ├── core.py               # MCUSimulator 统一核心
│   ├── firmware.py           # HEX/BIN/ELF 加载器
│   ├── virtual_serial.py     # VirtualSerialBridge (TCP ←→ QEMU)
│   ├── py_mcu.py             # PyMCU — 纯 Python MCU 模拟器 ⭐
│   ├── protocol_test.py      # 内建冒烟测试
│   ├── cli.py                # 命令行界面
│   ├── backends/
│   │   ├── __init__.py       # SimBackend 抽象基类
│   │   ├── registry.py       # MCU 型号注册表 + QEMU 发现
│   │   └── qemu_backend.py   # QEMU 子进程后端
│   └── configs/              # MCU 配置文件
│       ├── atmega328p.json
│       ├── atmega2560.json
│       ├── sam3x8e.json
│       ├── imxrt1062.json
│       └── esp32.json
└── examples/
    └── test_with_debug_tool.py  # 集成测试示例
```

## 工作原理

### 推荐方式：纯 Python MCU (`serve`)

```
kalico_debug_tool  ──TCP──>  PyMCU  (纯 Python)
    tcp:127.0.0.1:PORT       ├─ Kalico 协议编解码 (VLQ + CRC16 + 帧)
                             ├─ identify → identify_response 握手
                             ├─ get_clock / get_uptime / emergency_stop
                             └─ config / finalize_config / get_config
```

### QEMU 方式 (`run`)

```
kalico_debug_tool  ──TCP──>  VirtualSerialBridge  ──TCP──>  QEMU serial
    tcp:127.0.0.1:PORT_B          TCP proxy            tcp:127.0.0.1:PORT_A
                                                         └─ 模拟 MCU UART
```

### 协议层级

| 层级 | 实现 | 说明 |
|------|------|------|
| 消息编码 | `kalico_debug_tool/protocol/codec.py` | VLQ 编码, CRC16-CCITT |
| 消息帧 | `generic_arduino/src/generic/serial_irq.c` | MESSAGE_SYNC (0x7E) 帧边界 |
| 命令分发 | `generic_arduino/src/command.c` | `command_find_block()` + `command_dispatch()` |
| 模拟 I/O | `mcu_sim/virtual_serial.py` | TCP ↔ QEMU stdio 桥接 |

### 启动握手

```
1. QEMU 启动, 加载 firmware.hex 到 ATmega2560 模拟 flash
2. 固件执行 setup() → arduino_serial_init() → arduino_timer_init()
3. 固件进入 sched_main() 协作调度循环
4. console_task() 轮询串口, 等待命令
5. 主机发送: identify (msgid=1, offset=0, count=40)
6. 固件响应: identify_response (msgid=0, 数据字典)
```

## 限制

- **QEMU AVR 无 EEPROM 模拟** — 固件若依赖 EEPROM 启动可能失败
- **GPIO/SPI/I2C 未连接** — 当前仅模拟 UART，其他外设未接线
- **定时器精度** — QEMU 定时器为功能级模拟，非周期精确
- **Windows 上的 pty** — 使用 TCP socket 替代 pty，kalico_debug_tool 需通过 `tcp://` 连接
- **iMXRT1062** — QEMU 支持有限，推荐用 Renode 或真实硬件

## 许可协议

SPDX-License-Identifier: GPL-3.0-or-later

基于 Kevin O'Connor <kevin@koconnor.net> 的 Kalico 固件。
