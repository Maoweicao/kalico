# Hall 灯丝宽度传感器

本文档描述灯丝宽度传感器主机模块。用于开发此主机模块的硬件基于两个 Hall 线性传感器（例如 ss49e）。传感器在物体中位于相对两侧。工作原理：
两个 Hall 传感器以差分模式工作，温度漂移对传感器相同。无需特殊的温度补偿。

您可以在 [Thingiverse](https://www.thingiverse.com/thing:4138933) 上找到设计，
[Youtube](https://www.youtube.com/watch?v=TDO9tME8vp4) 上也提供了装配视频

要使用 Hall 灯丝宽度传感器，请阅读
[配置参考](Config_Reference.md#hall_filament_width_sensor) 和
[G-Code 文档](G-Codes.md#hall_filament_width_sensor)。


## 工作原理

传感器根据计算的灯丝宽度生成两个模拟输出。输出电压的总和始终等于检测到的灯丝宽度。主机模块监视电压变化并调整挤出倍数。我在类似 ramps 的主板上使用 aux2 连接器与 analog11 和 analog12 引脚。您可以使用不同的引脚和不同的主板。

## 菜单变量模板

```
[menu __main __filament __width_current]
type: command
enable: {'hall_filament_width_sensor' in printer}
name: Dia: {'%.2F' % printer.hall_filament_width_sensor.Diameter}
index: 0

[menu __main __filament __raw_width_current]
type: command
enable: {'hall_filament_width_sensor' in printer}
name: Raw: {'%4.0F' % printer.hall_filament_width_sensor.Raw}
index: 1
```

## 校准过程

要获得原始传感器值，可以使用菜单项或在终端中使用 **QUERY_RAW_FILAMENT_WIDTH** 命令。

1. 插入第一个校准杆（1.5 毫米尺寸）获取第一个原始传感器值

2. 插入第二个校准杆（2.0 毫米尺寸）获取第二个原始传感器值

3. 将原始传感器值保存在配置参数 `Raw_dia1` 和 `Raw_dia2` 中

## 如何启用传感器

默认情况下，传感器在通电时禁用。

要启用传感器，发出 **ENABLE_FILAMENT_WIDTH_SENSOR** 命令或
设置 `enable` 参数为 `true`。

## 日志记录

默认情况下，直径日志记录在通电时禁用。

发出 **ENABLE_FILAMENT_WIDTH_LOG** 命令开始日志记录，发出
**DISABLE_FILAMENT_WIDTH_LOG** 命令停止日志记录。要在通电时启用日志记录，设置 `logging` 参数为 `true`。

灯丝直径在每个测量间隔（默认为 10 毫米）记录。