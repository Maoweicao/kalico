# 切片软件

本文档提供了一些配置"切片软件"应用程序以与 Kalico 一起使用的提示。与 Kalico 一起使用的常见切片软件有 Slic3r、Cura、Simplify3D 等。

## 将 G-Code 风格设置为 Marlin

许多切片软件有一个选项来配置"G-Code 风格"。如今大多数现代切片软件都有一个"Klipper"G-Code 风格，最适合 Kalico。如果"Klipper"风格不可用，"Marlin"也应该可以与 Kalico 良好配合。"Smoothieware"设置也可以与 Kalico 良好配合。

## Kalico gcode_macro

切片软件通常允许配置"起始 G-Code"和"结束 G-Code"序列。通常更方便的是在 Kalico 配置文件中定义自定义宏，例如：`[gcode_macro START_PRINT]` 和 `[gcode_macro END_PRINT]`。然后只需在切片软件配置中运行 START_PRINT 和 END_PRINT。在 Kalico 配置中定义这些操作可能更容易调整打印机的起始和结束步骤，因为更改不需要重新切片。

有关示例 START_PRINT 和 END_PRINT 宏，请参阅 [sample-macros.cfg](../config/sample-macros.cfg)。

有关定义 gcode_macro 的详细信息，请参阅[配置参考](Config_Reference.md#gcode_macro)。

## 大回缩设置可能需要调整 Kalico

回缩移动的最大速度和加速度在 Kalico 中由 `max_extrude_only_velocity` 和 `max_extrude_only_accel` 配置设置控制。这些设置有一个默认值，在许多打印机上应该可以很好地工作。但是，如果在切片软件中配置了大回缩（例如 5mm 或更大），可能会发现它们限制了所需的回缩速度。

如果使用大回缩，考虑调整 Kalico 的[压力提前](Pressure_Advance.md)。否则，如果发现工具头在回缩和填充期间似乎"暂停"，则考虑在 Kalico 配置文件中显式定义 `max_extrude_only_velocity` 和 `max_extrude_only_accel`。

## 不要启用"coasting"

"coasting"功能很可能导致使用 Kalico 时打印质量差。考虑使用 Kalico 的[压力提前](Pressure_Advance.md)。

具体来说，如果切片软件在移动之间显著改变挤出速率，Kalico 将在移动之间执行减速和加速。这可能会使拉丝问题更严重，而不是更好。

相比之下，使用切片软件的"retract"设置、"wipe"设置和/或"wipe on retract"设置是可以的（通常是有帮助的）。

## 不要在 Simplify3D 上使用"extra restart distance"

此设置可能导致挤出速率的剧烈变化，从而触发 Kalico 的最大挤出横截面检查。考虑使用 Kalico 的[压力提前](Pressure_Advance.md)或常规的 Simplify3D 回缩设置。

## 在 KISSlicer 上禁用"PreloadVE"

如果使用 KISSlicer 切片软件，请将"PreloadVE"设置为零。考虑使用 Kalico 的[压力提前](Pressure_Advance.md)。

## 禁用任何"advanced extruder pressure"设置

一些切片软件宣传"advanced extruder pressure"功能。建议在使用 Kalico 时禁用这些选项，因为它们可能导致打印质量差。考虑使用 Kalico 的[压力提前](Pressure_Advance.md)。

具体来说，这些切片软件设置可以指示固件对挤出速率进行剧烈更改，希望固件近似这些请求并且打印机会大致获得所需的挤出机压力。然而，Kalico 利用精确的运动学计算和时序。当 Kalico 被命令对挤出速率进行显著更改时，它将规划相应的速度、加速度和挤出机运动更改——这不是切片软件的意图。切片软件甚至可能命令过量的挤出速率，以至于触发 Kalico 的最大挤出横截面检查。

相比之下，使用切片软件的"retract"设置、"wipe"设置和/或"wipe on retract"设置是可以的（通常是有帮助的）。

## START_PRINT 宏

使用 START_PRINT 宏或类似宏时，有时将切片软件变量中的参数传递给宏是有用的。

在 Cura 中，要传递温度，将使用以下起始 gcode：

```
START_PRINT BED_TEMP={material_bed_temperature_layer_0} EXTRUDER_TEMP={material_print_temperature_layer_0}
```

在 Slic3r 衍生软件（如 PrusaSlicer 和 SuperSlicer）中，将使用：

```
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

还要注意，当某些条件不满足时，这些切片软件将插入自己的加热代码。在 Cura 中，`{material_bed_temperature_layer_0}` 和 `{material_print_temperature_layer_0}` 变量的存在足以缓解此问题。在 Slic3r 衍生软件中，你将使用：

```
M140 S0
M104 S0
```

在宏调用之前。还要注意 SuperSlicer 有一个"custom gcode only"按钮选项，它可以实现相同的结果。

可以在 config/sample-macros.cfg 中找到使用这些参数的 START_PRINT 宏示例。
