# 工业安全监控

Kalico 为伺服驱动系统提供全面的工业级安全监控功能。

## 功能概览

| 模块 | 功能 | 状态 |
|------|------|------|
| `[safety_monitor]` | 位置偏差、速度、扭矩监控 | ✅ |
| `[emergency_stop]` | 硬件急停按钮 | ✅ |
| `[safety_door]` | 安全门联锁 | ✅ |
| `[servo_alarm]` | 伺服 ALM 引脚监控 | ✅ |
| `[production_counter]` | 生产计数、维护提醒 | ✅ |
| `[alarm_history]` | 报警历史持久化 | ✅ |

## 快速开始

```ini
# 安全监控
[safety_monitor]
deviation_threshold: 1.0
deviation_action: shutdown
max_velocity: 5000
velocity_action: shutdown
max_torque: 300
torque_action: pause
steppers: canopen_stepper stepper_x, canopen_stepper stepper_y

# 急停按钮
[emergency_stop]
estop_pin: ^PA0

# 安全门
[safety_door]
door_pin: ^PA1
door_action: pause

# 伺服 ALM 引脚
[servo_alarm x_axis]
alm_pin: PB7
action: shutdown

# 生产计数
[production_counter]
maintenance_interval: 1000
data_file: ~/production_data.json

# 报警历史
[alarm_history]
history_file: ~/alarm_history.json
max_entries: 1000
log_to_text: true
text_log_file: ~/alarm_log.txt
```

## 模块说明

### [safety_monitor]

监控伺服驱动器的位置偏差、速度和扭矩。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `deviation_threshold` | 0.0 | 位置偏差阈值（编码器计数） |
| `deviation_action` | shutdown | 超限动作：shutdown/pause/gcode/none |
| `deviation_debounce` | 0.05 | 防抖时间（秒） |
| `max_velocity` | 0.0 | 最大速度（编码器计数/秒） |
| `velocity_action` | shutdown | 速度超限动作 |
| `velocity_debounce` | 0.05 | 防抖时间（秒） |
| `max_torque` | 0.0 | 最大扭矩（%额定值） |
| `torque_action` | shutdown | 扭矩超限动作 |
| `torque_debounce` | 0.1 | 防抖时间（秒） |
| `steppers` | | 逗号分隔的步进电机列表 |

### [emergency_stop]

硬件急停按钮支持。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `estop_pin` | 必填 | 急停按钮 GPIO 引脚 |
| `estop_invert` | false | 反转引脚逻辑 |
| `estop_debounce` | 0.01 | 防抖时间（秒） |

### [safety_door]

安全门联锁，支持可配置动作。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `door_pin` | 必填 | 安全门传感器 GPIO 引脚 |
| `door_invert` | false | 反转引脚逻辑 |
| `door_debounce` | 0.01 | 防抖时间（秒） |
| `door_action` | shutdown | 门开动作：shutdown/pause/none |
| `allow_print_with_door_open` | false | 允许门开时打印 |

### [production_counter]

生产计数和维护提醒。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `count_on_complete` | true | 打印完成时计数 |
| `maintenance_interval` | 1000 | 维护间隔（打印次数） |
| `maintenance_hours` | 500 | 维护间隔（小时） |
| `data_file` | ~/production_data.json | 数据持久化文件 |

### [alarm_history]

报警历史持久化，支持 JSON 和文本日志。

| 选项 | 默认值 | 说明 |
|------|--------|------|
| `history_file` | ~/alarm_history.json | JSON 历史文件 |
| `max_entries` | 1000 | 最大记录数 |
| `log_to_text` | true | 同时写入文本日志 |
| `text_log_file` | ~/alarm_log.txt | 文本日志文件 |

## G-code 命令

### 安全监控

| 命令 | 说明 |
|------|------|
| `QUERY_SAFETY_STATUS` | 查询安全监控状态 |
| `SET_SAFETY_LIMIT [DEVIATION=<v>] [VELOCITY=<v>] [TORQUE=<v>]` | 运行时设置阈值 |

### 急停

| 命令 | 说明 |
|------|------|
| `QUERY_EMERGENCY_STOP` | 查询急停状态 |

### 安全门

| 命令 | 说明 |
|------|------|
| `QUERY_SAFETY_DOOR` | 查询安全门状态 |
| `ARM_SAFETY_DOOR` | 启用安全门监控 |
| `DISARM_SAFETY_DOOR` | 禁用安全门监控 |

### 生产计数

| 命令 | 说明 |
|------|------|
| `QUERY_PRODUCTION` | 查询生产统计 |
| `RESET_PRODUCTION [TOTAL]` | 重置计数器 |
| `MARK_MAINTENANCE` | 标记已执行维护 |

### 报警历史

| 命令 | 说明 |
|------|------|
| `QUERY_ALARM_HISTORY [COUNT=<n>]` | 查询报警历史 |
| `CLEAR_ALARM_HISTORY` | 清除历史 |
| `ACKNOWLEDGE_ALARM ID=<n>` | 确认报警 |

### 汇总查询

| 命令 | 说明 |
|------|------|
| `QUERY_ALL_SAFETY` | 查询所有安全状态 |

## 状态字段

### safety_monitor

| 字段 | 类型 | 说明 |
|------|------|------|
| `deviation_alarm` | bool | 位置偏差报警激活 |
| `deviation_value` | float | 当前位置偏差 |
| `deviation_threshold` | float | 配置的阈值 |
| `velocity_alarm` | bool | 速度报警激活 |
| `velocity_value` | float | 当前速度 |
| `velocity_threshold` | float | 配置的阈值 |
| `torque_alarm` | bool | 扭矩报警激活 |
| `torque_value` | float | 当前扭矩 |
| `torque_threshold` | float | 配置的阈值 |

### emergency_stop

| 字段 | 类型 | 说明 |
|------|------|------|
| `triggered` | bool | 急停当前触发 |
| `trigger_count` | int | 启动后触发次数 |
| `pin` | str | 配置的引脚 |

### safety_door

| 字段 | 类型 | 说明 |
|------|------|------|
| `door_open` | bool | 门当前打开 |
| `open_count` | int | 启动后打开次数 |
| `armed` | bool | 监控已启用 |
| `pin` | str | 配置的引脚 |
| `action` | str | 配置的动作 |

### production_counter

| 字段 | 类型 | 说明 |
|------|------|------|
| `total_prints` | int | 总完成打印数 |
| `session_prints` | int | 本次会话打印数 |
| `total_runtime_hours` | float | 总运行时间（小时） |
| `prints_since_maintenance` | int | 上次维护后打印数 |
| `maintenance_due` | bool | 维护提醒激活 |

### alarm_history

| 字段 | 类型 | 说明 |
|------|------|-------------|
| `total_alarms` | int | 总报警次数 |
| `unacknowledged` | int | 未确认报警数 |
| `recent_alarms` | list | 最近 5 条报警 |

## IEC 61800-5-2 安全功能

> **注意**：以下安全功能需要驱动器硬件安全模块支持。
> 纯软件无法实现合规的安全完整性等级（SIL）。

| 功能 | 说明 | 要求 |
|------|------|------|
| STO | 安全扭矩关断 | 驱动器 STO 输入端子 |
| SS1/SS2 | 安全停止 | 驱动器安全停止功能 |
| SLS | 安全限速 | 驱动器安全速度监控 |
| SBC | 安全制动控制 | 驱动器安全制动输出 |
| SDI | 安全方向 | 驱动器安全方向 |
| SLP | 安全限位 | 驱动器安全位置限制 |

对于需要这些功能的工业应用，请使用外部安全 PLC 或安全继电器。

## 事件

以下事件用于集成：

| 事件 | 来源 | 详情 |
|------|------|------|
| `servo_alarm:triggered` | servo_alarm | 报警引脚触发 |
| `safety_monitor:alarm` | safety_monitor | 安全限制超出 |
| `emergency_stop:triggered` | emergency_stop | 急停按下 |
| `safety_door:opened` | safety_door | 门打开 |
| `production_counter:print_completed` | production_counter | 打印完成 |
| `production_counter:maintenance_due` | production_counter | 维护到期 |
| `alarm_history:recorded` | alarm_history | 报警已记录 |

## 相关文档

- [伺服安全监控](servo-safety_CN.md)
- [配置参考](Config_Reference.md)
- [G-code 命令](G-Codes.md)
- [状态参考](Status_Reference.md)
