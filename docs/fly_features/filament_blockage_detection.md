# Filament Blockage Detection / 耗材堵塞检测

## Overview / 概述

Detects three types of filament feed problems: runout (no filament), slip (motor turns but filament doesn't move), and blockage (encoder reports movement but extruder doesn't). This is a firmware-level (MCU) implementation for low-latency detection.

检测三种类型的耗材送丝问题：断料（无耗材）、打滑（电机转动但耗材未移动）、堵塞（编码器报告移动但挤出机未移动）。这是固件级（MCU）实现，具有低延迟特性。

## Configuration / 配置

### MCU Sensor / MCU 传感器

```ini
[filament_blockage_sensor my_sensor]
encoder_pin: ^PA7           # Encoder GPIO pin (required)
#event_delay: 0.003         # Minimum time between events (default: 0.003)
#pause_delay: 0.5           # Time from event to pause (default: 0.5)
#extruder: extruder         # Extruder to monitor (default: extruder)
```

### Calibration / 校准

```ini
[filament_blockage_calibration my_sensor]
#min_threshold: 150         # Minimum edge count for detection (default: 150)
```

Calibration is performed automatically on startup or manually via `CALIBRATE_FILAMENT_BLOCKAGE`.

校准在启动时自动执行，也可通过 `CALIBRATE_FILAMENT_BLOCKAGE` 手动执行。

## G-code Commands / G-code 命令

| Command | Description | 说明 |
|---------|-------------|------|
| `ENABLE_FILAMENT_BLOCKAGE` | Enable sensor | 启用传感器 |
| `DISABLE_FILAMENT_BLOCKAGE` | Disable sensor | 禁用传感器 |
| `CALIBRATE_FILAMENT_BLOCKAGE` | Run calibration | 运行校准 |
| `STATUS_FILAMENT_BLOCKAGE` | Print status | 打印状态 |
| `SET_FILAMENT_BLOCKAGE_MIN_THRESHOLD THRESHOLD=<n>` | Set minimum edge count threshold | 设置最小边缘计数阈值 |

## Event Types / 事件类型

| Event | Meaning | 触发条件 |
|-------|---------|----------|
| `RUNOUT` | No filament detected | 编码器无脉冲 |
| `SLIP` | Motor turns but filament doesn't | 挤出机请求转动但编码器未检测到运动 |
| `BLOCKAGE` | Encoder moves but extruder doesn't | 编码器检测到运动但挤出机未请求转动 |

## Status Variables / 状态变量

Access via `printer["filament_blockage_sensor my_sensor"]`:

| Variable | Type | Description | 说明 |
|----------|------|-------------|------|
| `enabled` | bool | Whether sensor is active | 传感器是否启用 |
| `is_blockage` | bool | Whether blockage is detected | 是否检测到堵塞 |
| `is_paused` | bool | Whether print is paused due to event | 是否因事件暂停打印 |
| `edge_count` | int | Current encoder edge count | 当前编码器边缘计数 |
| `min_threshold` | int | Minimum edge count threshold | 最小边缘计数阈值 |
| `total_runout` | int | Total runout events | 总断料事件数 |
| `total_slip` | int | Total slip events | 总打滑事件数 |
| `total_blockage` | int | Total blockage events | 总堵塞事件数 |
| `blockage_threshold` | float | Max encoder edges before blockage (default: 80) | 堵塞前最大编码器边缘数 |
| `slip_threshold` | float | Min encoder edges to confirm slip (default: 8) | 确认打滑的最小编码器边缘数 |
| `total_distance` | float | Total distance pushed (mm) | 总推送距离(mm) |
| `calibration_edge_count` | float | Calibrated edge count per mm | 校准的每毫米边缘计数 |

## How It Works / 工作原理

The MCU firmware polls the encoder GPIO at high frequency. It tracks three signals:
1. `is_extrude_request`: Whether Klipper is commanding the extruder motor
2. `is_pushing`: Whether the encoder detects filament movement
3. `is_rotate`: Whether the extruder motor driver reports rotation

By comparing these signals over time windows, the firmware detects runout, slip, and blockage conditions and generates corresponding events.

MCU固件以高频率轮询编码器GPIO。它跟踪三个信号：
1. `is_extrude_request`：Klipper是否正在命令挤出机电机
2. `is_pushing`：编码器是否检测到耗材移动
3. `is_rotate`：挤出机电机驱动器是否报告转动

通过在时间窗口内比较这些信号，固件检测断料、打滑和堵塞条件并生成相应事件。
