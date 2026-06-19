# TSL1401CL 耗材宽度传感器

本文档介绍耗材宽度传感器主机模块。用于开发此主机模块的硬件基于 TSL1401CL 线性传感器阵列，但它可以与任何具有模拟输出的传感器阵列配合使用。你可以在 [Thingiverse](https://www.thingiverse.com/search?q=filament%20width%20sensor) 上找到设计图纸。

要将传感器阵列用作耗材宽度传感器，请阅读[配置参考](Config_Reference.md#tsl1401cl_filament_width_sensor)和 [G-Code 文档](G-Codes.md#hall_filament_width_sensor)。

## 工作原理

传感器根据计算的耗材宽度生成模拟输出。输出电压始终等于检测到的耗材宽度（例如 1.65v、1.70v、3.0v）。主机模块监控电压变化并调整挤出倍率。

## 注意：

默认情况下，传感器读数以 10 mm 间隔进行。如有需要，你可以通过编辑 **filament_width_sensor.py** 文件中的 ***MEASUREMENT_INTERVAL_MM*** 参数来自由更改此设置。
