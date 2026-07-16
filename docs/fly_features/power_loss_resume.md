# Power Loss Resume / 断电续打

## Overview / 概述

When a power outage or M112 emergency stop occurs during a print, this module automatically saves the current print state. Upon power restoration and printer restart, it resumes printing from where it left off.

当打印过程中发生断电或M112紧急停机时，此模块自动保存当前打印状态。电源恢复并重启打印机后，可从中断位置继续打印。

## Configuration / 配置

Add to `printer.cfg`:

```ini
[power_loss_resume]
#resume_gcode: G28 X Y      # G-code to run after resume (optional)
#start_gcode:                # Additional start gcode (optional)
#max_layer_save: 500         # Maximum layers to save progress (default: 500)
#enable_shutdown_save: True  # Save state on M112 shutdown (default: True)
#enable_resume_speed: True   # Apply configured speed on resume (default: True)
#resume_speed: 150           # Speed to apply on resume (default: 150)
```

## G-code Commands / G-code 命令

| Command | Description | 说明 |
|---------|-------------|------|
| `ENABLE_POWER_LOSS_RESUME` | Enable power loss resume | 启用断电续打 |
| `DISABLE_POWER_LOSS_RESUME` | Disable power loss resume | 禁用断电续打 |
| `RESET_POWER_LOSS_RESUME` | Clear saved state and delete file | 清除保存状态并删除文件 |
| `STATUS_POWER_LOSS_RESUME` | Print current status | 打印当前状态 |

## Status Variables / 状态变量

Access via `printer["power_loss_resume"]`:

| Variable | Type | Description | 说明 |
|----------|------|-------------|------|
| `state` | int | 0=off, 1=ready, 2=power lost | 0=关闭, 1=就绪, 2=已断电 |
| `file_path` | string | Path to saved resume data | 保存数据路径 |
| `last_epos` | float | Last known E position | 最后E轴位置 |
| `last_z` | float | Last known Z position | 最后Z轴位置 |
| `last_layer` | int | Last layer number | 最后层数 |
| `is_resume_speed` | bool | Whether speed override is active | 是否启用速度覆盖 |

## How It Works / 工作原理

1. On `M112` shutdown or power loss detection, saves: position, temperature, fan speeds, bed mesh, pressure advance, flow rate, extruder position, layer count.
2. On restart, if resume data exists, `SAVE_RESTART gcode` is automatically issued.
3. Printer performs homing, reheats, and resumes G-code execution from the saved position.

1. 在M112关机或断电检测时，保存：位置、温度、风扇速度、床网、压力提前、流量率、挤出机位置、层数。
2. 重启后，如存在续打数据，自动发出 `SAVE_RESTART gcode`。
3. 打印机执行归位、重新加热，从中断位置继续执行G-code。

## Safety Notes / 安全注意事项

- After resume, the printer executes a full G28 homing sequence. Ensure the bed is clear before resuming.
- The resume file is stored in the same directory as the main G-code file.
- If you manually print a different file, the old resume data is automatically cleared.
