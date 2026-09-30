# 伺服安全监控

Kalico 支持工业级伺服驱动器安全监控功能，包括 ALM（报警）引脚检测和故障管理。

## 功能特性

- **ALM 引脚监控**：实时监控伺服驱动器报警输出引脚
- **可配置动作**：报警时可选择紧急停止、暂停、自定义 G-code 或仅记录
- **故障检测**：通过通信协议检测 CiA 402 故障状态
- **G-code 命令**：交互式查询和复位伺服故障
- **状态报告**：通过 API 获取驱动器状态、错误码和报警状态

## 快速开始

### 方式一：集成配置

在伺服步进电机配置中直接添加 ALM 引脚：

```ini
[canopen_stepper stepper_x]
canopen_bus: mybus
node_id: 1
eds_file: ~/servo.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1

# ALM 报警引脚
alm_pin: PB7
alarm_action: shutdown
alm_invert: false
```

### 方式二：独立模块

使用 `[servo_alarm]` 实现灵活的多轴监控：

```ini
[servo_alarm x_axis]
alm_pin: PB7
action: shutdown
invert: false
debounce: 0.01
```

## 配置参考

### 集成选项

在 `[canopen_stepper]`、`[ethercat_stepper]` 或 `[rs485_stepper]` 中添加以下选项：

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `alm_pin` | 无 | 连接到伺服 ALM 输出的 GPIO 引脚 |
| `alarm_action` | `shutdown` | 报警动作：`shutdown`、`pause`、`gcode`、`none` |
| `alm_invert` | `false` | 反转引脚逻辑（高电平报警时设为 `true`） |

### `[servo_alarm]` 配置节

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `alm_pin` | 必填 | 报警输入的 GPIO 引脚 |
| `action` | `shutdown` | 报警动作：`shutdown`、`pause`、`gcode`、`none` |
| `invert` | `false` | 反转引脚逻辑 |
| `debounce` | `0.01` | 防抖时间（秒） |
| `alarm_gcode` | 无 | 当 `action: gcode` 时执行的 G-code |

### 动作类型

| 动作 | 说明 |
|------|------|
| `shutdown` | 紧急停止 - 立即停止所有运动 |
| `pause` | 暂停当前打印（如果正在打印） |
| `gcode` | 执行 `alarm_gcode` 中的自定义 G-code |
| `none` | 仅记录日志，不执行自动动作 |

## G-code 命令

### `QUERY_SERVO [STEPPER=<名称>]`

查询伺服驱动器状态。不带 `STEPPER` 参数时，查询所有伺服。

```
QUERY_SERVO                        # 查询所有伺服
QUERY_SERVO STEPPER=stepper_x      # 查询指定伺服
```

输出示例：
```
stepper_x:
  state=OPERATION_ENABLED
  mode=CSP
  error_code=0x0000
  is_fault=False
  alarm_active=False
```

### `RESET_SERVO_FAULT STEPPER=<名称>`

通过 CiA 402 故障复位命令复位伺服驱动器故障。

```
RESET_SERVO_FAULT STEPPER=stepper_x
```

### `QUERY_SERVO_ALARM`

查询所有 `[servo_alarm]` 模块的状态。

```
QUERY_SERVO_ALARM
```

### `QUERY_ALARM_<名称>` / `CLEAR_ALARM_<名称>`

查询或清除指定 `[servo_alarm]` 的状态。名称为配置节名称的最后一部分。

```ini
[servo_alarm x_axis]
```
```
QUERY_ALARM_X_AXIS
CLEAR_ALARM_X_AXIS
```

### `QUERY_SERVO_ALARM STEPPER=<名称>`

查询指定步进电机的报警状态（当配置了 `alm_pin` 时）。

### `RESET_SERVO_ALARM STEPPER=<名称>`

复位指定步进电机的报警和故障状态。

## 状态字段

### 伺服步进电机状态

| 字段 | 类型 | 说明 |
|------|------|------|
| `state` | 字符串 | CiA 402 状态名（如 "OPERATION_ENABLED"、"FAULT"） |
| `actual_position` | 整数 | 当前编码器位置 |
| `error_code` | 整数 | 驱动器错误码（来自 0x603F 寄存器） |
| `mode` | 字符串 | 运行模式（CSP、CSV、PP 等） |
| `is_fault` | 布尔 | 驱动器是否处于故障状态 |
| `statusword` | 整数 | 原始 CiA 402 状态字（0x6041） |
| `alarm_active` | 布尔 | ALM 引脚是否激活 |
| `alarm_count` | 整数 | 启动后的报警事件次数 |

### ServoAlarm 状态

| 字段 | 类型 | 说明 |
|------|------|------|
| `alarm_active` | 布尔 | 报警是否当前激活 |
| `alarm_count` | 整数 | 启动后的报警触发次数 |
| `last_alarm_time` | 浮点 | 上次报警事件的时间戳 |
| `pin` | 字符串 | 配置的 ALM 引脚 |
| `action` | 字符串 | 配置的报警动作 |

## 硬件接线

### 典型伺服驱动器 ALM 输出

大多数伺服驱动器具有开集电极 ALM 输出：

```
伺服驱动器                    MCU（如 STM32）
+---------+                    +------------+
| ALM OUT |---[10k 上拉]------| GPIO (PBx) |
| GND     |------------------| GND        |
+---------+                    +------------+
```

- **正常状态**：ALM 引脚为高电平（上拉）
- **报警状态**：ALM 引脚为低电平（被拉到 GND）

对于高电平有效的 ALM 输出，设置 `alm_invert: true`。

### 电平转换

某些伺服驱动器需要 24V ALM 输出。可使用以下方式之一：

1. **分压器**：24V -> 3.3V 电阻网络
2. **光耦**：电气隔离（推荐用于工业环境）
3. **电平转换模块**：双向电平转换

### 示例：24V 到 3.3V 分压器

```
24V ALM ---[10k]---+---[5.6k]--- GND
                   |
                   +--- 连接到 MCU GPIO
```

## 配置示例

### 多轴 CNC 设置

```ini
# CANopen 总线
[canopen_bus mybus]
interface: can0
channel: can0
bitrate: 1000000

# X 轴
[canopen_stepper stepper_x]
canopen_bus: mybus
node_id: 1
eds_file: ~/servo_x.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB7
alarm_action: shutdown

# Y 轴
[canopen_stepper stepper_y]
canopen_bus: mybus
node_id: 2
eds_file: ~/servo_y.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB8
alarm_action: shutdown

# Z 轴
[canopen_stepper stepper_z]
canopen_bus: mybus
node_id: 3
eds_file: ~/servo_z.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB9
alarm_action: pause

# 全局报警处理宏
[gcode_macro ON_SERVO_ALARM]
gcode:
  {% set stepper = params.STEPPER|default("unknown") %}
  M118 警告：{stepper} 伺服故障！
  M104 S0  # 关闭热端
  M140 S0  # 关闭热床
  {action_emergency_stop("伺服报警")}
```

### 工业机器人手臂

```ini
# 独立报警监控，使用自定义动作
[servo_alarm joint1_alarm]
alm_pin: PA0
action: gcode
invert: false
debounce: 0.01
alarm_gcode:
  M118 严重错误：关节 1 伺服报警！
  {action_emergency_stop("关节 1 ALM")}

[servo_alarm joint2_alarm]
alm_pin: PA1
action: gcode
invert: false
debounce: 0.01
alarm_gcode:
  M118 严重错误：关节 2 伺服报警！
  {action_emergency_stop("关节 2 ALM")}
```

### EtherCAT 伺服设置

```ini
# EtherCAT 伺服
[ethercat_stepper stepper_x]
ethercat_interface: eth0
ethercat_slave: 0
ethercat_cycle_time: 0.001
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
endstop_pin: PB6
alm_pin: PB7
alarm_action: shutdown

[ethercat_stepper stepper_y]
ethercat_interface: eth0
ethercat_slave: 1
ethercat_cycle_time: 0.001
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
endstop_pin: PB6
alm_pin: PB8
alarm_action: shutdown
```

### RS485 伺服设置

```ini
# RS485 伺服
[rs485_stepper stepper_x]
serial_port: /dev/ttyUSB0
baud_rate: 9600
rs485_protocol: modbus_rtu
rs485_slave_id: 1
rotation_distance: 360
microsteps: 1
endstop_pin: PB6
alm_pin: PB7
alarm_action: pause
alm_invert: true  # 某些驱动器使用高电平有效 ALM
```

## 故障排除

### 报警未检测到

1. 检查接线：确认 ALM 引脚连接到正确的 GPIO
2. 检查引脚逻辑：如果报警是高电平有效，尝试 `alm_invert: true`
3. 检查防抖：如果出现误触发，增加 `debounce` 时间
4. 查询引脚状态：使用 `QUERY_ALARM_<名称>` 检查当前状态

### 误报警

1. 增加防抖时间（如 `debounce: 0.02`）
2. 添加硬件滤波（ALM 引脚上的 RC 低通滤波器）
3. 检查 ALM 信号线是否有噪声

### 故障复位不工作

1. 确认驱动器支持 CiA 402 故障复位
2. 检查驱动器文档了解特定复位序列
3. 某些驱动器在故障后需要断电重启

### 状态显示 "unknown"

1. 检查通信（CAN/EtherCAT/RS485）
2. 确认 EDS 文件正确
3. 检查驱动器是否已上电且不在引导模式

## 相关文档

- [CANopen 指南](CANopen.md)
- [EtherCAT 指南](EtherCAT.md)
- [RS485 指南](RS485.md)
- [配置参考](Config_Reference.md)
- [G-code 命令](G-Codes.md)
- [状态参考](Status_Reference.md)
