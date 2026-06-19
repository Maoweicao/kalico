# 霍尔耗材宽度传感器

本文档介绍耗材宽度传感器主机模块。用于开发此主机模块的硬件基于两个霍尔线性传感器（例如 ss49e）。传感器位于机体的两侧。工作原理：两个霍尔传感器以差分模式工作，传感器的温度漂移相同。不需要特殊的温度补偿。

你可以在 [Thingiverse](https://www.thingiverse.com/thing:4138933) 上找到设计图纸，组装视频也可在 [Youtube](https://www.youtube.com/watch?v=TDO9tME8vp4) 上找到。

要使用霍尔耗材宽度传感器，请阅读[配置参考](Config_Reference.md#hall_filament_width_sensor)和 [G-Code 文档](G-Codes.md#hall_filament_width_sensor)。

## 工作原理

传感器根据计算的耗材宽度生成两个模拟输出。输出电压之和始终等于检测到的耗材宽度。主机模块监控电压变化并调整挤出倍率。我在类 ramps 板上使用 aux2 连接器的 analog11 和 analog12 引脚。你可以使用不同的引脚和不同的板卡。

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

## 校准步骤

要获取原始传感器值，你可以使用菜单项或在终端中使用 **QUERY_RAW_FILAMENT_WIDTH** 命令。

1. 插入第一个校准棒（1.5 mm 尺寸），获取第一个原始传感器值

2. 插入第二个校准棒（2.0 mm 尺寸），获取第二个原始传感器值

3. 将原始传感器值保存在配置参数 `Raw_dia1` 和 `Raw_dia2` 中

## 如何启用传感器

默认情况下，传感器在上电时处于禁用状态。

要启用传感器，请发出 **ENABLE_FILAMENT_WIDTH_SENSOR** 命令或将 `enable` 参数设置为 `true`。

## 日志记录

默认情况下，直径日志记录在上电时处于禁用状态。

发出 **ENABLE_FILAMENT_WIDTH_LOG** 命令开始记录，发出 **DISABLE_FILAMENT_WIDTH_LOG** 命令停止记录。要在上电时启用日志记录，请将 `logging` 参数设置为 `true`。

耗材直径会在每个测量间隔（默认 10 mm）记录一次。
