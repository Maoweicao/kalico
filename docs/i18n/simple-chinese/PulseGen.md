# 外部脉冲发生器支持

本文档介绍 Kalico 对外部脉冲发生器模块的支持。这些模块通过 RS485/SPI/UART 接收位置/速度指令，内部生成高速差分步进/方向脉冲。

## 概述

外部脉冲发生器模块适用于以下场景：
- 需要比 MCU GPIO 更高的脉冲频率（10MHz+）
- 需要差分信号（RS-422/LVDS）进行长距离传输
- 需要脉冲发生器处理加减速
- 驱动器只接受步进/方向信号，但希望通过总线控制

Kalico 支持三种指令模式：
- **绝对位置** — 发送绝对位置指令（类似 CSP）
- **相对位移** — 发送相对脉冲数
- **速度** — 发送速度指令

通信使用 RS485 传输层和协议层（Modbus RTU、UART 透传或自定义协议）。

## 硬件要求

### 脉冲发生器模块

任何接受位置/速度指令并输出步进/方向脉冲的外部模块。示例：
- 雷赛 DMC 系列（数字运动控制器）
- 带 RS485/UART 接口的外部运动控制器
- 自定义脉冲发生器板

### 通信接口

USB 转 RS485 适配器（与 RS485 伺服驱动器相同）。参见 [RS485 指南](RS485.md) 了解适配器推荐。

## 配置

### 绝对位置模式

```ini
[pulse_gen_stepper x]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 1
pulse_gen_mode: absolute
register_target_position: 0x607A
register_actual_position: 0x6064
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### 相对位移模式

```ini
[pulse_gen_stepper y]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 2
pulse_gen_mode: relative
register_relative_position: 0x0020
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200
```

### 速度模式

```ini
[pulse_gen_stepper z]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 3
pulse_gen_mode: velocity
register_velocity: 0x0030
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

## 配置参考

### [pulse_gen_stepper]

```
[pulse_gen_stepper x]
serial_port:
#   串口路径。必填。
#baud_rate: 9600
#   波特率。范围：1200 至 115200。默认 9600。
#pulse_gen_protocol: modbus_rtu
#   协议类型。可选：modbus_rtu、uart_passthrough、custom。
#   默认 modbus_rtu。
#pulse_gen_slave_id: 1
#   从站地址（1-247）。默认 1。
#pulse_gen_mode: absolute
#   指令模式。可选：absolute（绝对位置）、relative（相对位移）、
#   velocity（速度）。默认 absolute。
#register_target_position: 0x607A
#   目标位置寄存器地址（绝对模式）。默认 0x607A。
#register_actual_position: 0x6064
#   实际位置反馈寄存器地址。
#   设为 0 表示开环运行（无编码器）。默认 0x6064。
#register_relative_position: 0x0020
#   相对位移寄存器地址（相对模式）。默认 0x0020。
#register_velocity: 0x0030
#   速度指令寄存器地址（速度模式）。默认 0x0030。
#rs485_parity: N
#   校验位。可选：N、E、O。默认 N。
#rs485_stopbits: 1
#   停止位。默认 1。
#rs485_bytesize: 8
#   数据位。默认 8。
#rs485_direction_pin: rts
#   DE/RE 控制方式。默认 "rts"。
#protocol_class:
#   自定义协议的 Python 类路径（pulse_gen_protocol 为 "custom" 时）。
#   格式：模块名.类名
rotation_distance:
#   伺服电机旋转一圈的距离（毫米）。必填。
microsteps:
#   脉冲发生器设为 1（框架要求）。
#full_steps_per_rotation: 200
#   编码器每圈计数。默认 200。
#endstop_pin:
#   回原限位引脚。回原必填。
#homing_speed: 5.0
#   回原速度（毫米/秒）。默认 5.0。
#position_min: 0
#   最小位置（毫米）。默认 0。
#position_max:
#   最大位置（毫米）。设置 endstop_pin 时必填。
```

## 指令模式详情

### 绝对模式

每次 `generate_steps` 调用发送绝对目标位置。脉冲发生器的内部轨迹规划器处理加减速和脉冲生成。

```
itersolve → target_pos → protocol.set_target_position(target)
                              │
                              └─ 发生器内部处理：
                                   ├─ 轨迹规划
                                   ├─ 加速/减速
                                   └─ 差分脉冲输出
```

### 相对模式

每次 `generate_steps` 调用发送自上次以来的位移增量。适用于无编码器的开环脉冲发生器。

```
itersolve → target_pos → delta = target - last_target
                              │
                              ├─ 如果 delta != 0：
                              │    protocol.write_register(RELATIVE, delta)
                              │
                              └─ last_target = target
```

### 速度模式

每次 `generate_steps` 调用根据位置变化计算速度并发送。

```
itersolve → target_pos → velocity = (target - last) / dt
                              │
                              └─ protocol.write_register(VELOCITY, velocity)
```

## 开环与闭环

如果脉冲发生器有编码器，将 `register_actual_position` 设为编码器反馈寄存器地址。位置跟踪器将使用实际编码器位置。

如果没有编码器（开环），将 `register_actual_position: 0`。位置跟踪器将使用指令位置，精度较低但对大多数应用足够。

## 编写自定义协议

参见 [RS485 指南](RS485.md#编写自定义协议) 了解自定义协议适配器的编写说明。使用相同的 `RS485Protocol` 基类。

## 故障排除

### 脉冲发生器无响应

1. 检查接线和串口
2. 确认波特率和从站地址匹配
3. 确保协议类型正确

### 位置漂移（开环）

开环运行时这是预期现象。指令位置可能因以下原因与实际机械位置不同：
- 高速时丢失脉冲
- 机械间隙
- 电机失步

要获得精确定位，请使用带编码器的闭环驱动器。

### 通信延迟

RS485/Modbus 有固有延迟（2-20ms）。高速时可能导致位置跟踪滞后。建议：
- 使用更高的波特率
- 减少总线上的从站数量
- 使用绝对模式（发生器内部处理时序）
