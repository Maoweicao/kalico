# LYX 步进驱动

本文档介绍如何在 Kalico 中使用 LYX9231 闭环步进电机驱动器。LYX9231
是一款带编码器反馈的闭环步进驱动器，它接收来自微控制器的普通 STEP/DIR
脉冲，并通过软件位翻转（bit-bang）的 Modbus RTU 总线（运行在单个 GPIO
引脚上）进行参数配置。

Kalico 直接使用微控制器本身来位翻转 Modbus RTU 帧（参见
`src/modbus_uart.c`），因此无需 USB 转 RS485 适配器等额外硬件。

底层 Modbus RTU 组帧与位翻转总线驱动与
[RS485 伺服支持](RS485.md) 共享：`ModbusRtuProtocol` 和
`rs485_transport: mcu` 传输层使用完全相同的核心
（`klippy/extras/rs485/modbus_frame.py` 与
`klippy/extras/rs485/mcu_modbus.py`）。因此 LYX 驱动与 RS485 伺服
驱动可以共享同一条总线引脚。

除了本文档，还请查阅
[LYX 驱动配置参考](Config_Reference.md#lyx-stepper-driver-configuration)。

## 概述

在运动方面，LYX9231 与普通步进驱动一样：打印机像对待其他步进电机一样
发送 STEP 和 DIR 信号。Modbus 链路仅用于配置和诊断：

- 设置运行/保持电流
- 设置细分（微步）
- 配置电机类型与控制模式
- 读取芯片状态（报警、电机转速、位置误差）

这意味着 `[lyx9231]` 配置段是添加到常规的 `[stepper_x]` 配置段旁边，
而**不是**取代它。

## 硬件要求

### 微控制器

任何具有空闲 GPIO 引脚且受 Kalico 支持的 MCU 均可。Modbus 总线由软件
在单个引脚上位翻转实现，波特率为 38400（8N1）。

### 接线

LYX9231 使用半双工单线 Modbus UART，因此只需要一个 GPIO 引脚：

```
MCU GPIO ──── LYX9231 通信引脚
MCU GND  ──── LYX9231 GND
```

- 通信引脚空闲时为高电平，作为推挽输出驱动并启用内部上拉。
- 共用总线的所有驱动器必须使用**相同**的 `uart_pin`，并且每个
  `uart_address` 必须唯一。
- 线缆尽量短（建议 < 50cm），较长时请确保共地。

## 固件要求

位翻转 Modbus UART 需要编译进微控制器固件。运行 `make menuconfig`
时，请启用：

- **Support software Modbus RTU UART communication**（即
  `WANT_MODBUSUART` 选项）

当所选架构支持 GPIO 时，该选项默认开启，但请确认你的构建中已包含此项。

## 配置

### 与步进电机配合使用

```
[stepper_x]
step_pin: PC0
dir_pin: PC1
enable_pin: !PC2
microsteps: 16
rotation_distance: 40
endstop_pin: ^PE0
position_min: 0
position_max: 200
homing_speed: 20

[lyx9231 stepper_x]
uart_pin: PB1
uart_address: 1
microstep: 16
run_current: 1.4
hold_current: 0.7
driver_motor_type: 1
driver_op_mode: 2
```

`[lyx9231 stepper_x]` 段的名字必须与对应的 `[stepper_x]` 段名一致。

启动时，Kalico 会通过 Modbus 总线将所有配置的驱动器寄存器写入芯片。
之后，STEP/DIR 运动完全由常规的步进代码路径处理。

## 配置参考

### [lyx9231]

通过软件位翻转的 Modbus RTU 总线配置 LYX9231 闭环步进电机驱动器。

```
[lyx9231 stepper_x]
uart_pin:
#  用于单线 Modbus RTU 总线的 GPIO 引脚。必填。
uart_address: 1
#  该驱动器的 Modbus 从站地址（1-247）。在共享同一 uart_pin 的驱动
#  中必须唯一。默认 1。
sense_resistor: 0.050
#  用于将寄存器值换算为电流的采样电阻值（欧姆）。默认 0.050。
run_current: 1.4
#  驱动器运行电流（安培）。默认 1.4。
hold_current:
#  驱动器保持电流（安培）。未指定时默认为运行电流的一半。
microstep: 16
#  微步细分（1-256）。默认 16。
driver_motor_type: 1
#  电机相型：1 为 1.8 度，0 为 0.9 度。默认 1。
driver_op_mode: 2
#  控制模式。0=开环，1=普通闭环，2=超级闭环，3=伺服闭环，
#  4=力矩模式。默认 2。
driver_run_current: 896
#  运行电流寄存器的原始值。通常由 run_current 自动计算，无需手动
#  设置。默认 896。
driver_half_cur_en: 0
#  启用半电流功能（1=开，0=关）。默认 0。
driver_half_cur_time: 3000
#  施加半电流之前的延时（毫秒）。默认 3000。
driver_half_cur_ratio: 64
#  半电流比例寄存器值（0-128）。64 对应运行电流的一半。默认 64。
driver_boost_level: 1
#  额外力矩的 boost 档位。默认 1。
driver_noise_en: 0
#  启用降噪功能（1=开，0=关）。默认 0。
```

## G-Code 命令

这些命令按驱动器注册，使用 `STEPPER=<name>` 选择，其中 `<name>`
与 `[lyx9231 <name>]` 段名一致。

#### SET_LYX_CURRENT
`SET_LYX_CURRENT STEPPER=<name> [CURRENT=<安培>] [HOLDCURRENT=<安培>]`：
调整驱动器的运行和/或保持电流（安培）。不带参数时打印当前的
运行/保持电流值。

#### SET_LYX_FIELD
`SET_LYX_FIELD STEPPER=<name> FIELD=<字段> VALUE=<值>`：
向单个驱动器寄存器字段写入原始值。字段名为寄存器映射中的小写寄存器名
（例如运行电流寄存器为 `run_current`）。

#### SET_LYX_MICROSTEP
`SET_LYX_MICROSTEP STEPPER=<name> [MICROSTEP=<值>]`：
修改微步细分（1-256）。不带参数时打印当前细分设置。

#### DUMP_LYX
`DUMP_LYX STEPPER=<name>`：
打印驱动器的写寄存器缓存值与实时读取的寄存器值。

#### LYX_READ_REG
`LYX_READ_REG STEPPER=<name> REGISTER=<名字>`：
读取单个 Modbus 寄存器并打印原始值。寄存器名参照下方寄存器映射表。

#### LYX_WRITE_REG
`LYX_WRITE_REG STEPPER=<name> REGISTER=<名字> VALUE=<值>`：
向 Modbus 寄存器写入原始值并回读验证。若回读不一致会打印警告。

## 寄存器映射

LYX9231 暴露给 Kalico 的寄存器：

| 名称 | 地址 |
|------|------|
| SAVE_PARAM | 0x00 |
| BAUDRATE | 0x01 |
| COMM_ADDR | 0x02 |
| CHIP_MODEL | 0x03 |
| PHASE_B_RESIST | 0x04 |
| PHASE_A_RESIST | 0x05 |
| PHASE_B_INDUCT | 0x06 |
| PHASE_A_INDUCT | 0x07 |
| ALARM_CODE | 0x08 |
| CURRENT_KP | 0x09 |
| CURRENT_KI | 0x0A |
| MOTOR_POS_H | 0x0C |
| MOTOR_POS_L | 0x0D |
| MOTOR_SPEED | 0x0E |
| ERROR_ANGLE | 0x10 |
| MS_PIN_FUNC | 0x11 |
| MOTOR_TYPE | 0x12 |
| RUN_CURRENT | 0x13 |
| HALF_CUR_TIME | 0x14 |
| HALF_CUR_RATIO | 0x15 |
| HALF_CUR_EN | 0x16 |
| DIR_POLARITY | 0x17 |
| ENA_POLARITY | 0x18 |
| MICROSTEP_RATIO | 0x19 |
| DEAD_TIME | 0x1A |
| OCL_THRESHOLD | 0x1B |
| OCL_FILTER | 0x1C |
| CUR_ANTISAT | 0x1D |
| CUR_KP_GAIN | 0x1E |
| CUR_KI_GAIN | 0x1F |
| BOOST_LEVEL | 0x20 |
| OP_MODE | 0x21 |
| STALL_ANGLE | 0x22 |
| STALL_OUT_EN | 0x23 |
| MIN_SPEED | 0x26 |
| NOISE_EN | 0x41 |

`MOTOR_SPEED` 与 `ERROR_ANGLE` 按 16 位有符号数解释。`ALARM_CODE`
取值：0=正常，1=过流，2=电机断开，3=线圈异常，4=跟随误差，
5=堵转。

## 常见问题

### 寄存器写入验证失败

每次寄存器写入都会回读验证。若多次重试后仍无法验证，Kalico 会关机并
报错，例如：

```
Unable to write lyx uart 'stepper_x' register ALARM_CODE due to
transmission delay, try to reboot Klipper Service to retry
```

请检查接线、`uart_address`（必须与芯片地址一致）以及共享总线的拓扑，
然后重启 Klipper。

### Modbus 通信始终无法成功

固件的位时间基于实测的 MCU 时钟频率而非 MCU 上报的频率计算。若时钟
频率不稳定，通信可能始终无法成功。请重新检查接线，并确保 MCU 运行在
其配置频率上。

### 同一总线上多个驱动器

- 所有驱动器必须使用完全相同的 `uart_pin`。
- 每个 `uart_address` 必须唯一。
