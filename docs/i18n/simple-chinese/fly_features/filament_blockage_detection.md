# 耗材堵塞检测

## 概述

检测三种类型的耗材送丝问题：断料（无耗材）、打滑（电机转动但耗材未移动）、堵塞（编码器报告移动但挤出机未移动）。这是固件级（MCU）实现，具有低延迟检测特性。

## 配置

### MCU 传感器

```ini
[filament_blockage_sensor my_sensor]
encoder_pin: ^PA7           # 编码器GPIO引脚（必填）
#event_delay: 0.003         # 事件之间最小时间间隔（默认：0.003）
#pause_delay: 0.5           # 事件到暂停的时间（默认：0.5）
#extruder: extruder         # 要监控的挤出机（默认：extruder）
```

### 校准

```ini
[filament_blockage_calibration my_sensor]
#min_threshold: 150         # 检测所需的最小边缘计数（默认：150）
```

校准在启动时自动执行，也可通过 `CALIBRATE_FILAMENT_BLOCKAGE` 手动执行。

## G-code 命令

| 命令 | 说明 |
|---------|-------------|
| `ENABLE_FILAMENT_BLOCKAGE` | 启用传感器 |
| `DISABLE_FILAMENT_BLOCKAGE` | 禁用传感器 |
| `CALIBRATE_FILAMENT_BLOCKAGE` | 运行校准 |
| `STATUS_FILAMENT_BLOCKAGE` | 打印状态 |
| `SET_FILAMENT_BLOCKAGE_MIN_THRESHOLD THRESHOLD=<n>` | 设置最小边缘计数阈值 |

## 事件类型

| 事件 | 触发条件 |
|-------|----------|
| `RUNOUT` | 无耗材，编码器无脉冲 |
| `SLIP` | 挤出机请求转动但编码器未检测到运动 |
| `BLOCKAGE` | 编码器检测到运动但挤出机未请求转动 |

## 状态变量

通过 `printer["filament_blockage_sensor my_sensor"]` 访问：

| 变量 | 类型 | 说明 |
|----------|------|------|
| `enabled` | bool | 传感器是否启用 |
| `is_blockage` | bool | 是否检测到堵塞 |
| `is_paused` | bool | 是否因事件暂停打印 |
| `edge_count` | int | 当前编码器边缘计数 |
| `min_threshold` | int | 最小边缘计数阈值 |
| `total_runout` | int | 总断料事件数 |
| `total_slip` | int | 总打滑事件数 |
| `total_blockage` | int | 总堵塞事件数 |
| `blockage_threshold` | float | 堵塞前最大编码器边缘数（默认：80） |
| `slip_threshold` | float | 确认打滑的最小编码器边缘数（默认：8） |
| `total_distance` | float | 总推送距离（mm） |
| `calibration_edge_count` | float | 校准的每毫米边缘计数 |

## 工作原理

MCU固件以高频率轮询编码器GPIO。它跟踪三个信号：
1. `is_extrude_request`：Klipper是否正在命令挤出机电机
2. `is_pushing`：编码器是否检测到耗材移动
3. `is_rotate`：挤出机电机驱动器是否报告转动

通过在时间窗口内比较这些信号，固件检测断料、打滑和堵塞条件并生成相应事件。