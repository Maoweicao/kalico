# Klipper 新手入门教程

> 本教程面向完全零基础用户，从软硬件角度全面介绍 Klipper 固件的使用。

---

## 目录

- [第一部分：Klipper 基础介绍](#第一部分klipper-基础介绍)
- [第二部分：主板连接方式](#第二部分主板连接方式)
- [第三部分：固件编译与烧录](#第三部分固件编译与烧录)
- [第四部分：基础配置](#第四部分基础配置)
- [第五部分：宏编写](#第五部分宏编写)
- [第六部分：基础架构](#第六部分基础架构)

---

# 第一部分：Klipper 基础介绍

## 1.1 什么是 Klipper

Klipper 是一个 3D 打印机固件，它的核心理念是：**将复杂的运动计算交给性能更强的上位机（如树莓派），让打印机主板专注于执行步进脉冲。**

### 传统固件 vs Klipper

| 特性 | 传统固件 (Marlin 等) | Klipper |
|------|---------------------|---------|
| 运算位置 | 打印机主板 | 上位机（树莓派） |
| 计算能力 | 受限于 8/32 位 MCU | 几乎无限（Linux 主机） |
| 配置修改 | 需要重新编译固件 | 只需修改配置文件 |
| 运动精度 | 受限于 MCU 性能 | 高精度（25微秒级） |
| 扩展性 | 有限 | 支持多 MCU、CAN 总线等 |

## 1.2 Klipper 的优势

### 高精度步进运动
Klipper 使用应用处理器（如树莓派）计算打印机运动，将步进事件压缩后发送给 MCU 执行。每个步进事件的精度可达 25 微秒或更好。

### 顶级性能
即使在旧的 8 位 MCU 上，Klipper 也能达到 175K+ 步/秒的步进速率。在较新的 MCU 上，可达到数百万步/秒。

### 多 MCU 支持
Klipper 支持多个 MCU 协同工作，例如：
- 一个 MCU 控制挤出机
- 一个 MCU 控制加热器
- 一个 MCU 控制打印机其他部分

### 配置简单
所有配置都存储在一个简单的配置文件中，无需重新编译固件即可修改设置。

### 高级功能
- **压力提前 (Pressure Advance)**：减少挤出机渗漏，改善打印边角质量
- **输入整形 (Input Shaping)**：减少打印中的振纹（ringing/ghosting）
- **自定义宏**：可以在配置文件中定义新的 G-Code 命令

## 1.3 硬件需求

### 上位机（Host）
运行 Klipper 主机软件（Klippy）的设备，推荐：

| 设备 | 说明 |
|------|------|
| 树莓派 3B/4B/5 | 最常用，社区支持最好 |
| 树莓派 Zero 2 W | 小巧，适合小型打印机 |
| Orange Pi | 性价比高 |
| BeagleBone | 支持 PRU 实时控制 |
| x86 Linux 电脑 | 性能最强 |

### 下位机（MCU）
打印机主板，常见型号：

| 芯片架构 | 常见型号 | 说明 |
|----------|----------|------|
| STM32 | STM32F103, STM32F407, STM32F446, STM32G0B1 | 最常见，性能好 |
| AVR | ATmega2560 | 传统 8 位 MCU |
| RP2040/RP2350 | 树莓派 Pico | 新兴选择 |
| LPC | LPC1768, LPC1769 | 旧款主板 |
| SAM | SAM3X8E, SAM4S8C, SAME70 | Arduino Due 等 |

### 常见打印机主板

| 主板 | MCU | 特点 |
|------|-----|------|
| BTT SKR Mini E3 | STM32F103 | 入门级，性价比高 |
| BTT SKR 1.4 | LPC1768/1769 | 功能丰富 |
| BTT SKR 2 | STM32F407 | 高性能 |
| BTT SKR Pico | RP2040 | 新兴选择 |
| MKS Robin | STM32F103/F407 | 常见选择 |
| Fysetc Cheetah | STM32F103 | 性价比高 |
| RAMPS 1.4 | ATmega2560 | 经典 Arduino 主板 |

---

# 第二部分：主板连接方式

Klipper 支持 6 种不同的 MCU 连接方式，每种方式适用于不同的场景。

## 2.1 连接方式概览

| # | 方式 | 配置项 | 传输介质 | 拓扑结构 |
|---|------|--------|----------|----------|
| 1 | UART/Serial (USB) | `serial` + `baud` | USB CDC ACM / 物理串口 | 点对点 |
| 2 | CAN Bus | `canbus_uuid` | SocketCAN | 多点总线 |
| 3 | Pipe/PTY | `serial` (无 baud) | 命名管道 / PTY | 本地 IPC |
| 4 | TCP | `tcp_host` + `tcp_port` | TCP/IP 流 | 网络 |
| 5 | UDP | `udp_host` + `udp_port` | UDP/IP 数据报 | 网络 |
| 6 | Debug File | 命令行参数 | 文件回放 | 离线调试 |

## 2.2 UART/Serial (USB) - 最常用

这是最常见的连接方式，MCU 通过 USB 虚拟串口或物理 UART 连接到上位机。

### 配置示例

```ini
[mcu]
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_12345-if00
baud: 250000
restart_method: arduino
```

### 如何获取串口 ID

在终端中运行：

```bash
ls /dev/serial/by-id/*
```

输出示例：
```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

### 重启方式 (restart_method)

| 方式 | 说明 |
|------|------|
| `arduino` | 切换 DTR 线（Arduino/STM32 常用） |
| `cheetah` | Fysetc Cheetah 主板专用 |
| `command` | 发送 Klipper 协议复位命令 |
| `rpi_usb` | 通过 hub-ctrl 切换 USB 端口电源 |

### 适用场景
- 单 MCU 打印机
- 入门级配置
- USB 连接的主板

## 2.3 CAN Bus - 多设备总线

CAN 总线是一种多点通信协议，允许多个设备共享同一条总线，每个设备通过 UUID 标识。

### 配置示例

```ini
[mcu]
canbus_uuid: 0a1b2c3d4e5f
canbus_interface: can0
```

### 多 MCU 配置示例

```ini
# 主板通过 USB
[mcu]
serial: /dev/serial/by-id/usb-main_board

# 工具头通过 CAN
[mcu toolhead]
canbus_uuid: 1a2b3c4d5e6f

# 加速度计通过 TCP
[mcu accelerometer]
tcp_host: 192.168.1.200
tcp_port: 5500
is_non_critical: True
```

### 发现 CAN 设备

使用 Klipper 自带工具：

```bash
python3 ~/klipper/scripts/canbus_query.py can0
```

### 适用场景
- 多 MCU 打印机
- 工具头主板
- 需要减少布线的场景

## 2.4 Pipe/PTY - Linux MCU

用于主机 MCU（Linux 进程）或 BeagleBone PRU 设备。

### 配置示例

```ini
[mcu host]
serial: /tmp/klipper_host_mcu
```

### 适用场景
- 使用树莓派 GPIO 的 Linux MCU
- BeagleBone PRU 控制
- 本地进程间通信

## 2.5 TCP - 网络流

通过 TCP/IP 网络连接 MCU，适用于有线以太网或 WiFi 连接。

### 配置示例

```ini
[mcu]
tcp_host: 192.168.1.100
tcp_port: 5500
```

### 使用场景
- 远程 MCU 控制
- 通过 WiFi 连接的打印机
- ESP32 等 WiFi MCU

### 实现方式
1. **桥接设备**：MCU 通过 UART 连接到 ESP32/RPi，ESP32/RPi 通过 TCP 连接到 Klippy
2. **原生 TCP**：MCU 固件直接实现 TCP/IP 协议栈（如 STM32 + W5500）

## 2.6 UDP - 网络数据报

通过 UDP/IP 连接 MCU，适合低延迟场景。

### 配置示例

```ini
[mcu]
udp_host: 192.168.1.100
udp_port: 5500
```

### TCP vs UDP 对比

| 方面 | TCP | UDP |
|------|-----|-----|
| 可靠性 | 保证送达 | 尽力而为 |
| 有序性 | 保证顺序 | 不保证 |
| 连接状态 | 面向连接 | 无连接 |
| 延迟 | 较高 | 较低 |
| 开销 | 连接建立 + 断开 | 最小 |
| 适用场景 | 通用远程 MCU | 低延迟、局域网 |

## 2.7 Debug File - 离线调试

用于离线调试，Klippy 从预录制的串口流量文件读取数据。

### 使用方法

```bash
klippy.py --debugoutput=/tmp/klipper.log --dictionary=/tmp/dict.bin
```

### 适用场景
- 开发调试
- 复现问题
- 无硬件测试

## 2.8 连接方式选择流程

Klippy 按以下顺序检测配置：

1. `tcp_host` 已设置 → **TCP**
2. `udp_host` 已设置 → **UDP**
3. `canbus_uuid` 已设置 → **CAN Bus**
4. `serial` 已设置，路径以 `/dev/rpmsg_` 或 `/tmp/klipper_host_` 开头 → **Pipe/PTY**
5. `serial` 已设置，其他路径 → **UART/Serial**

**注意**：每个 `[mcu]` 部分只能指定一种连接方式，这些选项互斥。

---

# 第三部分：固件编译与烧录

## 3.1 编译环境准备

### 安装依赖

在上位机（树莓派等）上安装编译工具：

```bash
sudo apt-get update
sudo apt-get install git build-essential libncurses-dev
```

### 进入 Klipper 目录

```bash
cd ~/klipper/
```

## 3.2 menuconfig 配置

运行配置工具：

```bash
make menuconfig
```

### 界面说明

```
┌─────────────────────────────────────────────────────┐
│  Klipper Firmware Configuration                    │
├─────────────────────────────────────────────────────┤
│  [*] Micro-controller Architecture (STMicroelectronics STM32) │
│  [ ] Bootloader offset (No bootloader)              │
│  [ ] Communication Interface (Serial (on USB PA10/PA9)) │
│                                                   │
│      <Ok>                <Save>                <Exit> │
└─────────────────────────────────────────────────────┘
```

### 常见配置选项

#### 1. 选择 MCU 架构

| 选项 | 芯片架构 |
|------|----------|
| Atmel AVR | ATmega2560 等 |
| Atmel SAM | SAM3X8E, SAM4S8C 等 |
| STMicroelectronics STM32 | STM32F103, STM32F407 等 |
| RP2040/RP2350 | 树莓派 Pico |
| NXP LPC176x | LPC1768, LPC1769 |
| SAMD21/SAMD51 | ATSAMD21, ATSAMD51 |

#### 2. 选择主板型号（以 STM32 为例）

| 选项 | 说明 |
|------|------|
| STM32F103 | 常见入门级主板 |
| STM32F407 | 高性能主板 |
| STM32F446 | 高性能主板 |
| STM32G0B1 | 新款低成本 MCU |
| STM32H723 | 顶级性能 |

#### 3. 选择通信接口

| 选项 | 说明 |
|------|------|
| Serial (on USB PA10/PA9) | USB 虚拟串口 |
| Serial (UART1) | 物理 UART |
| CAN bus | CAN 总线 |
| TCP (Network) | 网络连接 |

## 3.3 编译固件

配置完成后，按 `Q` 退出，按 `Y` 保存。

编译固件：

```bash
make
```

编译成功后，固件文件位于：
- AVR: `out/klipper.elf.hex`
- ARM: `out/klipper.bin`

## 3.4 烧录固件

### 方法一：USB 串口烧录（AVR 芯片）

适用于 ATmega2560 等 AVR 芯片：

```bash
# 停止 Klipper 服务
sudo service klipper stop

# 烧录固件（替换为实际串口）
make flash FLASH_DEVICE=/dev/serial/by-id/usb-Klipper_stm32f103xe_12345-if00

# 启动 Klipper 服务
sudo service klipper start
```

### 方法二：SD 卡烧录（STM32 芯片）

适用于 STM32F103, STM32F407 等：

1. **断开 USB 连接**（重要！防止供电冲突）
2. 将编译好的 `firmware.bin` 复制到 SD 卡根目录
3. 将 SD 卡插入主板
4. 给主板上电
5. 等待几秒后取出 SD 卡
6. 重新连接 USB

**注意**：某些主板需要将 SD 卡命名为特定名称（如 `firmware.bin`）。

### 方法三：RP2040 烧录

适用于树莓派 Pico 等 RP2040 主板：

1. 按住 BOOTSEL 按钮
2. 连接 USB
3. 板子会作为 USB 存储设备出现
4. 复制 `firmware.uf2` 到存储设备
5. 板子会自动重启

命令行方式：

```bash
sudo service klipper stop
make flash FLASH_DEVICE=first
sudo service klipper start
```

### 方法四：LPC176x 烧录

适用于 LPC1768/LPC1769 主板：

1. 将编译好的 `firmware.bin` 复制到 SD 卡
2. 重命名为 `firmware.bin`（确保名称正确）
3. 插入 SD 卡并重启主板

### 烧录后验证

烧录完成后，验证连接：

```bash
ls /dev/serial/by-id/*
```

如果能看到设备，说明烧录成功。

---

# 第四部分：基础配置

## 4.1 配置文件结构

Klipp 配置文件是 INI 格式的文本文件，存放在 `~/printer.cfg`。

### 基本结构

```ini
# 这是注释

[mcu]
serial: /dev/serial/by-id/usb-Klipper_xxx
baud: 250000

[printer]
kinematics: cartesian
max_velocity: 300
max_accel: 3000

[stepper_x]
step_pin: PC0
dir_pin: PC1
enable_pin: !PC2
...
```

### 配置引用

Klipper 支持配置引用，可以在多个部分之间共享值：

```ini
[constants]
run_current: 1.0

[tmc2209 stepper_x]
run_current: ${constants.run_current}

[tmc2209 stepper_y]
run_current: ${tmc2209 stepper_x.run_current}
```

## 4.2 MCU 配置

### 基本 MCU 配置

```ini
[mcu]
# 串口连接（USB 方式）
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_12345-if00
baud: 250000
restart_method: arduino
```

### CAN 总线 MCU 配置

```ini
[mcu toolhead]
canbus_uuid: 1a2b3c4d5e6f
canbus_interface: can0
```

### 多 MCU 配置

```ini
# 主 MCU
[mcu]
serial: /dev/serial/by-id/usb-main_board

# 工具头 MCU
[mcu toolhead]
serial: /dev/serial/by-id/usb-toolhead_board

# 非关键 MCU（可断开）
[mcu accelerometer]
serial: /dev/serial/by-id/usb-accelerometer
is_non_critical: True
```

### 引脚名称格式

引脚名称使用硬件名称，如 `PA4`、`PC0` 等。

- `!` 前缀：反转极性（低电平有效）
- `^` 前缀：启用内部上拉电阻
- `~` 前缀：启用内部下拉电阻

示例：
- `PC0` - 普通引脚
- `!PC0` - 反转极性
- `^PC0` - 启用上拉
- `!^PC0` - 反转 + 上拉

## 4.3 打印机运动学配置

### [printer] 部分

```ini
[printer]
# 运动学类型（必须）
kinematics: cartesian

# 最大速度（必须）
max_velocity: 300  # mm/s

# 最大加速度（必须）
max_accel: 3000  # mm/s^2

# Z 轴最大速度（可选）
max_z_velocity: 5

# Z 轴最大加速度（可选）
max_z_accel: 100

# 最小巡航比例（可选）
minimum_cruise_ratio: 0.5

# 直角速度（可选）
square_corner_velocity: 5.0
```

### 支持的运动学类型

| 类型 | 说明 | 适用打印机 |
|------|------|-----------|
| `cartesian` | 笛卡尔坐标 | 传统 XYZ 打印机 |
| `corexy` | CoreXY 结构 | 高速打印机 |
| `corexz` | CoreXZ 结构 | 特殊结构 |
| `hybrid_corexy` | 混合 CoreXY | Markforged 类型 |
| `delta` | 三角洲结构 | Delta 打印机 |
| `polar` | 极坐标 | 实验性 |
| `winch` | 绳索牵引 | 实验性 |

## 4.4 步进电机配置

### [stepper_x] 基本配置

```ini
[stepper_x]
# 步进引脚（必须）
step_pin: PC0

# 方向引脚（必须）
dir_pin: PC1

# 使能引脚（可选）
enable_pin: !PC2  # ! 表示低电平有效

# 旋转距离（必须）
# 计算公式：皮带齿距 × 驱动轮齿数 / 电机齿数
rotation_distance: 40  # 例如 2GT 皮带，20 齿驱动轮

# 微步数（必须）
microsteps: 16

# 每圈全步数（可选）
full_steps_per_rotation: 200  # 1.8 度电机

# 齿轮比（可选）
# gear_ratio: 5:1

# 限位开关引脚（必须，X/Y/Z 轴需要）
endstop_pin: ^PC3

# 限位位置（必须）
position_endstop: 0

# 最大位置（必须）
position_max: 220

# 最小位置（可选）
position_min: 0

# 归位速度（可选）
homing_speed: 5  # mm/s

# 第二次归位速度（可选）
second_homing_speed: 2.5

# 归位后回退距离（可选）
homing_retract_dist: 5.0
```

### rotation_distance 计算

**皮带传动**：
```
rotation_distance = 皮带齿距 × 驱动轮齿数
```
- 2GT 皮带：2mm × 20齿 = 40mm
- T2.5 皮带：2.5mm × 20齿 = 50mm

**丝杆传动**：
```
rotation_distance = 丝杆导程
```
- 8mm 丝杆：rotation_distance = 8
- 2mm 丝杆：rotation_distance = 2

**带齿轮箱**：
```
rotation_distance = (输出齿数 / 输入齿数) × 基础距离
```

### 限位开关配置

```ini
# 机械限位开关（上拉）
endstop_pin: ^PC3

# 限位开关（下拉）
endstop_pin: ~PC3

# 无归位（不推荐）
# endstop_pin: virtual_endstop

# 传感器归位
# endstop_pin: tmc2209_stepper_x:virtual_endstop
```

## 4.5 挤出机配置

### [extruder] 配置

```ini
[extruder]
# 步进引脚
step_pin: PB1
dir_pin: PB0
enable_pin: !PA5

# 旋转距离
rotation_distance: 22.6789511  # 根据实际齿轮比计算

# 微步数
microsteps: 16

# 每圈全步数
full_steps_per_rotation: 200

# 齿轮比（如有）
# gear_ratio: 5:1

# 喷嘴直径（必须）
nozzle_diameter: 0.4

# 耗材直径（必须）
filament_diameter: 1.75

# 最大挤出横截面积（可选）
# max_extrude_cross_section: 4.0

# 最大挤出距离（可选）
# max_extrude_only_distance: 50.0

# 压力提前（可选，需要校准）
# pressure_advance: 0.0
# pressure_advance_smooth_time: 0.040

# 加热器引脚（必须）
heater_pin: PC4

# 温度传感器类型（必须）
sensor_type: ATC Semitec 104NT-4-R025H42G

# 温度传感器引脚（必须）
sensor_pin: PA0

# 控制方式（必须）
control: pid

# PID 参数（必须，使用 PID_CALIBRATE 命令获取）
pid_Kp: 21.527
pid_Ki: 1.063
pid_Kd: 108.982

# 或使用 MPC 控制（Kalico 特性）
# control: mpc
# heater_power: 40
# cooling_fan: fan

# 温度范围（必须）
min_temp: 0
max_temp: 270

# 最低挤出温度（可选）
min_extrude_temp: 170
```

### PID 校准

在 Klipper 控制台中运行：

```bash
# 加热喷嘴到目标温度并校准
PID_CALIBRATE HEATER=extruder TARGET=200

# 保存配置
SAVE_CONFIG
```

### MPC 控制（Kalico 特性）

MPC（Model Predictive Control）是 Kalico 的增强功能：

```ini
[extruder]
control: mpc
heater_power: 40  # 加热器功率（瓦特）
cooling_fan: fan  # 关联的冷却风扇
ambient_temp_sensor: temperature_sensor room  # 环境温度传感器

# 耗材参数（可选）
filament_diameter: 1.75
filament_density: 1.2
filament_heat_capacity: 1.8
```

## 4.6 热床配置

### [heater_bed] 配置

```ini
[heater_bed]
# 加热器引脚
heater_pin: PD3

# 温度传感器
sensor_type: EPCOS 100K B57560G104F
sensor_pin: PA1

# 控制方式
control: pid

# PID 参数
pid_Kp: 58.437
pid_Ki: 2.347
pid_Kd: 363.769

# 温度范围
min_temp: 0
max_temp: 120
```

## 4.7 风扇配置

### [fan] - 打印冷却风扇

```ini
[fan]
# 风扇引脚
pin: PB5

# 最大功率（可选）
# max_power: 1.0

# 关机时转速（可选）
# shutdown_speed: 0

# 启动时间（可选）
# kick_start_time: 0.100

# 最小功率（可选）
# min_power: 0.0
```

### [heater_fan] - 加热器冷却风扇

```ini
[heater_fan hotend_fan]
# 风扇引脚
pin: PB6

# 关联的加热器
heater: extruder

# 最低温度（低于此温度风扇关闭）
heater_temp: 50

# 最大功率
# max_power: 1.0
```

### [controller_fan] - 控制器风扇

```ini
[controller_fan controller_fan]
# 风扇引脚
pin: PB7

# 关联的加热器（可选）
heater: heater_bed

# 关联的电机驱动（可选）
# fan_speed: 0.5

# 超时时间（可选）
# idle_timeout: 60
```

### [temperature_fan] - 温控风扇

```ini
[temperature_fan chamber_fan]
# 风扇引脚
pin: PB8

# 温度传感器
sensor: temperature_sensor chamber

# 目标温度
target_temp: 40

# PID 控制（可选）
# pid_kp: 0.2
# pid_ki: 0.1
# pid_kd: 0.5

# 最小温度（可选）
min_temp: 0
max_temp: 60
```

## 4.8 TMC 驱动配置

### TMC2208 (UART)

```ini
[tmc2208 stepper_x]
uart_pin: PC4  # UART 引脚

# 或使用 TX/RX 引脚
# tx_pin: PC4
# rx_pin: PC5

# 串口地址（多驱动时需要）
# uart_address: 0

# 运行电流（必须）
run_current: 0.8

# 保持电流（可选）
# hold_current: 0.4

# 微步插值（可选）
# interpolate: True

# 运行模式（可选）
# driver_SGTHRS: 50  # 传感器归位阈值
```

### TMC2209 (UART)

```ini
[tmc2209 stepper_x]
uart_pin: PC4

# 运行电流
run_current: 0.8

# 传感器归位支持
# driver_SGTHRS: 100
```

### TMC5160 (SPI)

```ini
[tmc5160 stepper_x]
cs_pin: PC4  # 片选引脚

# SPI 引脚（如需要）
# spi_bus: spi1
# spi_software_sclk_pin: PA5
# spi_software_mosi_pin: PA7
# spi_software_miso_pin: PA6

# 运行电流
run_current: 1.0

# 其他参数
# driver_TPWMTHRS: 0
# driver_VACTUAL: 0
# driver_TPOWERDOWN: 128
# driver_EN_PWM_MODE: True
```

### TMC 驱动调试

```bash
# 测试步进电机
STEPPER_BUZZ STEPPER=stepper_x

# 设置驱动电流
SET_TMC_CURRENT STEPPER=stepper_x CURRENT=0.8

# 查看驱动状态
DUMP_TMC STEPPER=stepper_x
```

## 4.9 温度传感器配置

### 常见热敏电阻类型

| 类型 | 说明 |
|------|------|
| EPCOS 100K B57560G104F | 常见 EPCOS 100K |
| ATC Semitec 104GT-2 | 常见 Semitec |
| Generic 3950 | 通用 3950 NTC |
| NTC 100K MGB18-104F39050L32 | NTC 100K |

### [temperature_sensor] 配置

```ini
[temperature_sensor chamber]
# 传感器类型
sensor_type: Generic 3950

# 传感器引脚
sensor_pin: PA2

# 温度偏移（可选）
# temperature_offset: 0

# 最小/最大温度（可选）
min_temp: 0
max_temp: 100
```

### SPI 温度传感器

```ini
[temperature_sensor hotend_temp]
sensor_type: MAX31865
# 使用软件 SPI
spi_bus: spi1
rtd_reference_r: 430
rtd_num_of_wires: 2
cs_pin: PC4
```

## 4.10 其他常用配置

### [bed_mesh] - 热床网格

```ini
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 30, 60
mesh_max: 200, 190
probe_count: 5, 5
algorithm: bicubic
```

### [probe] - 探针

```ini
[probe]
pin: ^PA3
x_offset: -25
y_offset: 0
z_offset: 0
#   点击 "QUERY_PROBE" 查看当前状态
speed: 5
samples: 3
samples_result: average
samples_tolerance: 0.05
```

### [screws_tilt_adjust] - 螺丝校准

```ini
[screws_tilt_adjust]
screw1: 30, 30
screw1_name: front left screw
screw2: 200, 30
screw2_name: front right screw
screw3: 200, 190
screw3_name: rear right screw
screw4: 30, 190
screw4_name: rear left screw
horizontal_move_z: 5
speed: 50
screw_thread: CW-M3
```

### [input_shaper] - 输入整形

```ini
[input_shaper]
shaper_freq_x: 50
shaper_freq_y: 50
shaper_type: mzv
```

---

# 第五部分：宏编写

## 5.1 基本宏结构

### 定义一个简单的宏

```ini
[gcode_macro GREETING]
description: 打印问候语
gcode:
  M117 Hello World!
```

### 宏的命名规则

- 宏名称不区分大小写
- 如果包含数字，数字必须在末尾
- 示例：`MY_MACRO` 和 `my_macro` 等价
- 有效：`TEST_MACRO25`
- 无效：`MACRO25_TEST3`

### 缩进规则

`gcode:` 部分后的每一行都需要缩进（通常 2 个空格）：

```ini
[gcode_macro MY_MACRO]
gcode:
  G28
  G1 Z10 F300
  M117 Done!
```

## 5.2 Jinja2 模板

### 变量设置

```ini
[gcode_macro SET_TEMP]
gcode:
  {% set temp = params.TEMPERATURE|default(200)|float %}
  M104 S{temp}
```

### 条件语句

```ini
[gcode_macro CONDITIONAL]
gcode:
  {% if params.VALUE|default(0)|int > 10 %}
    M117 Value is greater than 10
  {% else %}
    M117 Value is 10 or less
  {% endif %}
```

### 循环

```ini
[gcode_macro MULTI_MOVE]
gcode:
  {% for i in range(5) %}
    G1 X{10 + i * 20} F3000
  {% endfor %}
```

### 访问打印机状态

```ini
[gcode_macro SHOW_TEMP]
gcode:
  {% set bed_temp = printer.heater_bed.temperature %}
  {% set extruder_temp = printer.extruder.temperature %}
  M117 Bed: {bed_temp}C, Extruder: {extruder_temp}C
```

### 访问参数

```ini
[gcode_macro SET_BED_TEMP]
gcode:
  {% set bed_temp = params.TEMPERATURE|default(40)|float %}
  M140 S{bed_temp}
```

调用方式：`SET_BED_TEMP TEMPERATURE=60`

## 5.3 Python 宏（Kalico 特性）

Kalico 支持使用 Python 编写宏，使用 `!` 前缀：

### 基本 Python 宏

```ini
[gcode_macro PYTHON_EXAMPLE]
gcode:
  !temp = printer["extruder"]["temperature"]
  !respond_info(f"Current temperature: {temp}C")
```

### Python 循环

```ini
[gcode_macro PYTHON_LOOP]
gcode:
  !for i in range(5):
  !  emit(f"G1 X{i * 20} F3000")
```

### 从文件包含 Python 宏

```ini
[gcode_macro MY_MACRO]
gcode: !!include my_macros/my_macro.py
```

文件 `my_macros/my_macro.py`：
```python
wipe_count = 8
emit("G90")
emit("G0 Z15 F300")
for wipe in range(wipe_count):
    emit(f"G0 X{275} Y{4 + 0.25 * wipe} Z9.7 F12000")
```

### 可用的 Helper 函数

| 函数 | 说明 |
|------|------|
| `emit(cmd)` | 发送 G-Code 命令 |
| `wait_while(cond)` | 等待条件为假 |
| `wait_until(cond)` | 等待条件为真 |
| `wait_moves()` | 等待移动完成 |
| `sleep(seconds)` | 暂停 |
| `respond_info(msg)` | 发送信息 |
| `raise_error(msg)` | 抛出错误 |
| `action_emergency_stop(msg)` | 紧急停止 |

## 5.4 常用宏示例

### 开始打印宏

```ini
[gcode_macro START_PRINT]
description: 开始打印准备
gcode:
  {% set BED_TEMP = params.BED_TEMP|default(60)|float %}
  {% set EXTRUDER_TEMP = params.EXTRUDER_TEMP|default(200)|float %}

  # 归位
  G28

  # 加热热床
  M140 S{BED_TEMP}
  M190 S{BED_TEMP}

  # 加热喷嘴
  M104 S{EXTRUDER_TEMP}
  M109 S{EXTRUDER_TEMP}

  # 自动调平
  BED_MESH_CALIBRATE

  # 挤出准备
  G92 E0
  G1 E5 F100
  G92 E0

  # 开始打印
  G1 Z5 F3000
```

### 结束打印宏

```ini
[gcode_macro END_PRINT]
description: 打印结束
gcode:
  # 关闭加热器
  M104 S0
  M140 S0

  # 关闭风扇
  M106 S0

  # 回到原点
  G91
  G1 Z10 F3000
  G90
  G28 X Y

  # 关闭电机
  M84
```

### 换料宏

```ini
[gcode_macro CHANGE_FILAMENT]
description: 更换耗材
gcode:
  {% set OLD_TEMP = printer.extruder.target %}
  {% set NEW_TEMP = params.NEW_TEMP|default(200)|float %}

  # 保存当前温度
  SET_GCODE_VARIABLE MACRO=CHANGE_FILAMENT VARIABLE=old_temp VALUE={OLD_TEMP}

  # 加热到换料温度
  M109 S{NEW_TEMP}

  # 退料
  G91
  G1 E-50 F300
  G90

  # 提示用户
  M117 请更换耗材，完成后按继续

  # 等待用户确认
  PAUSE

  # 进料
  G91
  G1 E50 F300
  G90

  # 恢复温度
  M109 S{OLD_TEMP}
```

### 安全归位宏

```ini
[gcode_macro SAFE_HOME]
description: 安全归位
gcode:
  # 抬高喷嘴
  G91
  G1 Z10 F3000
  G90

  # 归位
  G28

  # 移动到中心
  G1 X{printer.toolhead.axis_maximum.x / 2} Y{printer.toolhead.axis_maximum.y / 2} F6000
```

## 5.5 Delayed Gcodes

延迟 G-Code 可以在指定时间后执行：

### 基本用法

```ini
[delayed_gcode clear_display]
description: 清除显示消息
gcode:
  M117

[gcode_macro LOAD_FILAMENT]
description: 加载耗材
gcode:
  G91
  G1 E50 F100
  G90
  M400
  M117 加载完成!
  UPDATE_DELAYED_GCODE ID=clear_display DURATION=10
```

### 启动时执行

```ini
[delayed_gcode welcome]
initial_duration: 5.
gcode:
  M117 欢迎使用 Klipper!
```

### 循环执行

```ini
[delayed_gcode report_temp]
initial_duration: 2.
gcode:
  {action_respond_info("喷嘴温度: %.1f" % (printer.extruder0.temperature))}
  UPDATE_DELAYED_GCODE ID=report_temp DURATION=2
```

取消循环：
```bash
UPDATE_DELAYED_GCODE ID=report_temp DURATION=0
```

## 5.6 变量保存

### 使用 SET_GCODE_VARIABLE

```ini
[gcode_macro PRINT_STATUS]
variable_status: "idle"
gcode:
  M117 Status: {printer["gcode_macro PRINT_STATUS"].status}

[gcode_macro SET_STATUS]
gcode:
  {% set status = params.STATUS|default("unknown") %}
  SET_GCODE_VARIABLE MACRO=PRINT_STATUS VARIABLE=status VALUE='"{status}"'
```

使用：
```bash
SET_STATUS STATUS="printing"
PRINT_STATUS
```

### 使用 SAVE_VARIABLE 持久化

```ini
# 首先启用 save_variables
[save_variables]
filename: ~/printer_data/config/saved_variables.cfg

# 然后在宏中使用
[gcode_macro T1]
gcode:
  ACTIVATE_EXTRUDER extruder=extruder1
  SAVE_VARIABLE VARIABLE=currentextruder VALUE='"extruder1"'

[gcode_macro T0]
gcode:
  ACTIVATE_EXTRUDER extruder=extruder
  SAVE_VARIABLE VARIABLE=currentextruder VALUE='"extruder"'

[gcode_macro START_PRINT]
gcode:
  {% set svv = printer.save_variables.variables %}
  ACTIVATE_EXTRUDER extruder={svv.currentextruder}
```

## 5.7 宏调试

### 查看变量

```bash
# 查看宏的变量
QUERY_GCODE_VARIABLE MACRO=PRINT_STATUS VARIABLE=status
```

### 测试宏

```bash
# 直接调用宏
START_PRINT BED_TEMP=60 EXTRUDER_TEMP=200

# 测试延迟 G-Code
UPDATE_DELAYED_GCODE ID=clear_display DURATION=0
```

### 查看打印机状态

```bash
# 查看工具头位置
STATUS

# 查看温度
M105
```

---

# 第六部分：基础架构

## 6.1 软件架构概览

Klipper 采用分层架构：

```
┌─────────────────────────────────────────┐
│         上位机 (Klippy)                  │
│  ┌─────────────────────────────────────┐ │
│  │  Python 应用层                      │ │
│  │  - G-Code 解析                      │ │
│  │  - 运动学计算                       │ │
│  │  - 温度控制                         │ │
│  │  - 宏系统                           │ │
│  └─────────────────────────────────────┘ │
│  ┌─────────────────────────────────────┐ │
│  │  C 辅助层 (chelper)                 │ │
│  │  - 步进压缩                         │ │
│  │  - 运动学求解                       │ │
│  │  - 串口通信                         │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
                    │
                    │ 串口/CAN/TCP/UDP
                    ▼
┌─────────────────────────────────────────┐
│         下位机 (MCU)                     │
│  ┌─────────────────────────────────────┐ │
│  │  C 固件层                           │ │
│  │  - 步进电机控制                     │ │
│  │  - 温度读取                         │ │
│  │  - 加热器控制                       │ │
│  │  - 限位开关检测                     │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## 6.2 目录结构

```
klipper/
├── src/                    # MCU 源码
│   ├── avr/               # AVR 架构
│   ├── stm32/             # STM32 架构
│   ├── rp2040/            # RP2040 架构
│   ├── lpc176x/           # LPC 架构
│   ├── linux/             # Linux MCU
│   ├── generic/           # 通用代码
│   ├── sched.c            # 调度器
│   ├── command.c          # 命令处理
│   ├── stepper.c          # 步进电机
│   └── ...
├── klippy/                 # 上位机软件
│   ├── klippy.py          # 主入口
│   ├── gcode.py           # G-Code 解析
│   ├── mcu.py             # MCU 通信
│   ├── toolhead.py        # 工具头控制
│   ├── serialhdl.py       # 串口处理
│   ├── chelper/           # C 辅助库
│   │   ├── serialqueue.c  # 串口队列
│   │   ├── stepcompress.c # 步进压缩
│   │   ├── itersolve.c    # 迭代求解
│   │   └── ...
│   ├── kinematics/        # 运动学模块
│   │   ├── cartesian.py
│   │   ├── corexy.py
│   │   ├── delta.py
│   │   └── ...
│   └── extras/            # 扩展模块
│       ├── temperature_sensor.py
│       ├── bed_mesh.py
│       ├── tmc2208.py
│       └── ...
├── config/                 # 示例配置
├── scripts/                # 构建脚本
├── lib/                    # 第三方库
└── test/                   # 测试
```

## 6.3 主机代码流程

### 启动流程

1. **klippy.py** - 主入口
   - 解析命令行参数
   - 打开配置文件
   - 实例化打印机对象
   - 启动串口连接

2. **gcode.py** - G-Code 处理
   - 接收 G-Code 命令
   - 翻译为内部调用
   - 执行相应操作

3. **toolhead.py** - 运动控制
   - LookAheadQueue（前瞻队列）
   - Move 对象创建
   - 梯形速度规划

### 移动命令流程

```
G1 X100 Y100 F3000
        │
        ▼
    gcode.py
        │
        ▼
    gcode_move.py → cmd_G1()
        │
        ▼
    ToolHead.move()
        │
        ▼
    LookAheadQueue.add_move()
        │
        ▼
    LookAheadQueue.flush()
        │
        ▼
    Move.set_junction()  # 梯形生成
        │
        ▼
    ToolHead._process_moves()
        │
        ▼
    trapq_append()  # 加入运动队列
        │
        ▼
    itersolve_generate_steps()  # 迭代求解
        │
        ▼
    stepcompress_append()  # 步进压缩
        │
        ▼
    serialqueue  # 发送到 MCU
```

## 6.4 MCU 代码流程

### 启动流程

1. **架构特定初始化**（如 `src/avr/main.c`）
   - 初始化硬件
   - 调用 `sched_main()`

2. **sched.c** - 调度器
   - 运行所有 `DECL_INIT()` 函数
   - 循环运行所有 `DECL_TASK()` 函数

3. **command.c** - 命令处理
   - 从串口接收命令
   - 调用对应的命令函数

### 步进电机控制

```c
// 伪代码
void stepper_event(uint32_t time) {
    // 产生步进脉冲
    gpio_out_write(step_pin, 1);
    // 短暂延迟
    udelay(2);
    gpio_out_write(step_pin, 0);

    // 计算下一步时间
    interval += add;
    sched_add_timer(time + interval, stepper_event);
}
```

## 6.5 模块系统

### 动态模块加载

Klipp 会根据配置文件自动加载模块：

```ini
# 如果配置中有 [bed_mesh] 部分
[bed_mesh]
...

# Klippy 会自动加载 klippy/extras/bed_mesh.py
```

### 模块结构

```python
# klippy/extras/my_module.py

def load_config(config):
    """加载配置并返回打印机对象"""
    # 读取配置
    pin = config.get('pin')

    # 创建对象
    obj = MyModule(config)

    # 注册事件处理器
    printer = config.get_printer()
    printer.register_event_handler('klippy:connect', obj._handle_connect)

    return obj
```

### 添加新模块

1. 在 `klippy/extras/` 目录创建 Python 文件
2. 实现 `load_config()` 或 `load_config_prefix()` 函数
3. 在配置文件中添加对应的部分

## 6.6 运动学系统

### ToolHead 类

核心运动控制类：

```python
class ToolHead:
    def move(self, newpos, speed):
        """处理移动命令"""
        # 创建 Move 对象
        move = Move(self, newpos, speed)

        # 运动学检查
        self.kin.check_move(move)

        # 添加到前瞻队列
        self.lookahead.add_move(move)
```

### LookAheadQueue

前瞻队列用于优化运动：

```python
class LookAheadQueue:
    def add_move(self, move):
        """添加移动到队列"""
        self.queue.append(move)

    def flush(self):
        """刷新队列，计算速度"""
        # 根据后续移动优化当前移动的速度
        # 实现 "look-ahead" 算法
```

### 迭代求解器

使用迭代算法计算精确的步进时间：

```c
// 伪代码
void itersolve_gen_steps_range(struct stepper *stepper,
                                double x_start, double x_end) {
    while (x_start < x_end) {
        // 猜测时间
        double time = guess_time(stepper, x_start);

        // 计算实际位置
        double actual_x = calc_position(stepper, time);

        // 修正猜测
        x_start = actual_x;

        // 记录步进时间
        stepcompress_append(stepper, time);
    }
}
```

## 6.7 关键组件

### 串口通信 (serialhdl.py)

处理与 MCU 的通信：

```python
class SerialReader:
    def __init__(self, serialport, baud):
        """初始化串口"""
        self.serialport = serialport
        self.baud = baud

    def _readline(self):
        """读取一行数据"""
        # 从 C 层接收数据
        # 解析协议帧
        # 处理响应
```

### 命令调度 (gcode.py)

解析和执行 G-Code：

```python
class GCodeParser:
    def register_command(self, name, func):
        """注册命令"""
        self.commands[name] = func

    def execute(self, gcode):
        """执行 G-Code"""
        # 解析命令名和参数
        # 调用注册的函数
```

### 温度控制

PID/MPC 温度控制算法：

```python
class PrinterHeater:
    def set_temperature(self, temp):
        """设置目标温度"""
        self.target_temp = temp

    def _check_temperature(self):
        """检查温度并调整功率"""
        # PID 或 MPC 算法
        # 输出 PWM 控制加热器
```

## 6.8 通信协议

### 协议帧格式

```
┌─────────┬─────────┬─────────┬─────────┐
│ Sequence│ Command │ Payload │  CRC    │
│ (16bit) │ (16bit) │ (变长)  │ (16bit) │
└─────────┴─────────┴─────────┴─────────┘
```

### 命令类型

| 命令 | 说明 |
|------|------|
| queue_step | 队列步进命令 |
| set_next_step_dir | 设置下一步方向 |
| reset_step_clock | 重置步进时钟 |
| stepper_get_position | 获取步进位置 |
| endstop_query | 查询限位开关 |

### 时钟同步

Klipp 实现 MCU 时钟同步：

1. 主机记录本地时间
2. 发送时间戳到 MCU
3. MCU 返回其时钟值
4. 主机计算时钟偏移
5. 后续命令使用同步后的时间

## 6.9 调试与故障排除

### 日志文件

日志位于 `~/printer_data/logs/klippy.log`

### 常用调试命令

```bash
# 查看状态
STATUS

# 查看温度
M105

# 查看 MCU 状态
DUMP_TMC STEPPER=stepper_x

# 查询限位开关
QUERY_ENDSTOPS

# 查看步进位置
STEPPER_BUZZ STEPPER=stepper_x
```

### 常见问题

1. **串口找不到**
   - 检查 USB 连接
   - 运行 `ls /dev/serial/by-id/`

2. **固件编译失败**
   - 检查依赖安装
   - 确认 make menuconfig 配置正确

3. **电机不转**
   - 检查引脚配置
   - 确认使能引脚极性
   - 测试 `STEPPER_BUZZ`

4. **温度传感器错误**
   - 检查传感器类型
   - 确认引脚连接
   - 查看日志错误信息

---

# 附录

## A. 常见 G-Code 命令

| 命令 | 说明 |
|------|------|
| G28 | 归位 |
| G1 | 直线移动 |
| G28 X Y Z | 归位指定轴 |
| M104 S{temp} | 设置喷嘴温度 |
| M109 S{temp} | 等待喷嘴温度 |
| M140 S{temp} | 设置热床温度 |
| M190 S{temp} | 等待热床温度 |
| M106 S{speed} | 设置风扇速度 |
| M107 | 关闭风扇 |
| M82 | 相对挤出 |
| M83 | 绝对挤出 |
| M117 {msg} | 显示消息 |
| M400 | 等待移动完成 |
| M84 | 关闭电机 |

## B. 常见错误信息

| 错误 | 原因 | 解决方法 |
|------|------|----------|
| MCU 'mcu' shutdown | MCU 通信失败 | 检查串口连接 |
| Timer too close | MCU 负载过高 | 降低速度/加速度 |
| ADC out of range | 温度传感器错误 | 检查传感器连接 |
| Move out of range | 移动超出范围 | 检查位置限制 |
| Unable to read tmc | TMC 驱动通信失败 | 检查 UART/SPI 连接 |

## C. 参考资源

- [Klipper 官方文档](https://www.klipper3d.org/)
- [Kalico 文档](https://docs.kalico.gg/)
- [Klipper 配置参考](Config_Reference.md)
- [G-Code 命令参考](G-Codes.md)
- [宏编写指南](Command_Templates.md)
- [TMC 驱动配置](TMC_Drivers.md)
- [输入整形](Resonance_Compensation.md)
- [压力提前](Pressure_Advance.md)
