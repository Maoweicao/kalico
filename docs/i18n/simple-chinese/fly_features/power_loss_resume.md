# 断电续打

## 概述

当打印过程中发生断电或M112紧急停机时，此模块自动保存当前打印状态。电源恢复并重启打印机后，可从中断位置继续打印。

## 配置

添加到 `printer.cfg`：

```ini
[power_loss_resume]
#resume_gcode: G28 X Y      # 续打后运行的G-code（可选）
#start_gcode:                # 附加的开始gcode（可选）
#max_layer_save: 500         # 最大保存进度层数（默认：500）
#enable_shutdown_save: True  # M112关机时保存状态（默认：True）
#enable_resume_speed: True   # 续打时应用配置的速度（默认：True）
#resume_speed: 150           # 续打时应用的速度（默认：150）
```

## G-code 命令

| 命令 | 说明 |
|---------|-------------|
| `ENABLE_POWER_LOSS_RESUME` | 启用断电续打 |
| `DISABLE_POWER_LOSS_RESUME` | 禁用断电续打 |
| `RESET_POWER_LOSS_RESUME` | 清除保存状态并删除文件 |
| `STATUS_POWER_LOSS_RESUME` | 打印当前状态 |

## 状态变量

通过 `printer["power_loss_resume"]` 访问：

| 变量 | 类型 | 说明 |
|----------|------|------|
| `state` | int | 0=关闭, 1=就绪, 2=已断电 |
| `file_path` | string | 保存数据路径 |
| `last_epos` | float | 最后E轴位置 |
| `last_z` | float | 最后Z轴位置 |
| `last_layer` | int | 最后层数 |
| `is_resume_speed` | bool | 是否启用速度覆盖 |

## 工作原理

1. 在M112关机或断电检测时，保存当前位置、温度、风扇速度、床网、压力提前、流量率、挤出机位置和层数。
2. 重启后，如存在续打数据，自动发出 `SAVE_RESTART gcode`。
3. 打印机执行归位、重新加热，从中断位置继续执行G-code。

## 安全注意事项

- 续打后，打印机执行完整的G28归位序列。确保续打前热床已清空。
- 续打文件保存于主G-code文件的同一目录中。
- 如果手动打印其他文件，旧的续打数据会自动清除。