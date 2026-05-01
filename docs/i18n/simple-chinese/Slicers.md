# 切片机

本文档为使用Kalico的"切片机"应用程序配置提供了一些提示。与Kalico一起使用的常见切片机包括Slic3r、Cura、Simplify3D等。

## 将G代码风格设置为Marlin

许多切片机都有一个选项来配置"G代码风格"。大多数现代切片机现在都有一个"Klipper" G代码风格，最适合Kalico。如果"Klipper"风格不可用，"Marlin"也应该与Kalico配合良好。"Smoothieware"设置也适用于Kalico。

## Kalico gcode_macro

切片机通常允许配置"启动G代码"和"结束G代码"序列。在Kalico配置文件中定义自定义宏通常很方便，例如：`[gcode_macro START_PRINT]`和`[gcode_macro END_PRINT]`。然后可以在切片机的配置中只运行START_PRINT和END_PRINT。在Kalico配置中定义这些操作可能会使调整打印机的启动和结束步骤更容易，因为更改不需要重新切片。

请参见[sample-macros.cfg](../config/sample-macros.cfg)了解示例START_PRINT和END_PRINT宏。

请参见[配置参考](Config_Reference.md#gcode_macro)了解有关定义gcode_macro的详细信息。

## 大回抽设置可能需要调整Kalico

回抽移动的最大速度和加速度由Kalico中的`max_extrude_only_velocity`和`max_extrude_only_accel`配置设置控制。这些设置具有默认值，应该在许多打印机上表现良好。但是，如果已在切片机中配置了大回抽（例如5mm或更大），您可能会发现它们限制了所需的回抽速度。

如果使用大回抽，请考虑调整Kalico的[压力前进](Pressure_Advance.md)。或者，如果您发现工具头在回抽和加液期间似乎"暂停"，请考虑在Kalico配置文件中显式定义`max_extrude_only_velocity`和`max_extrude_only_accel`。

## 不要启用"滑行"

"滑行"功能可能会导致Kalico打印质量下降。请考虑改用Kalico的[压力前进](Pressure_Advance.md)。

具体来说，如果切片机在移动之间剧烈改变挤出速率，Kalico将在移动之间执行减速和加速。这可能会使blob变得更糟，而不是更好。

相比之下，使用切片机的"回抽"设置、"擦拭"设置和/或"回抽时擦拭"设置是可以的（通常很有帮助）。

## 不要在Simplify3D上使用"额外重启距离"

此设置会导致挤出速率的剧烈变化，这可能会触发Kalico的最大挤出截面检查。请考虑改用Kalico的[压力前进](Pressure_Advance.md)或常规Simplify3D回抽设置。

## 在KISSlicer上禁用"PreloadVE"

如果使用KISSlicer切片软件，则将"PreloadVE"设置为零。请考虑改用Kalico的[压力前进](Pressure_Advance.md)。

## 禁用任何"高级挤出机压力"设置

某些切片机宣传"高级挤出机压力"功能。建议在使用Kalico时将这些选项保持禁用状态，因为它们可能会导致打印质量下降。请考虑改用Kalico的[压力前进](Pressure_Advance.md)。

具体来说，这些切片机设置可以指示固件对挤出速率进行剧烈改变，希望固件能够近似这些请求，打印机将大致获得所需的挤出机压力。但是，Kalico采用精确的运动学计算和定时。当Kalico被命令对挤出速率进行重大改变时，它将规划相应的速度、加速度和挤出机运动的改变——这不是切片机的意图。切片机甚至可能命令过度的挤出速率，以至于触发Kalico的最大挤出截面检查。

相比之下，使用切片机的"回抽"设置、"擦拭"设置和/或"回抽时擦拭"设置是可以的（通常很有帮助）。

## START_PRINT宏

使用START_PRINT宏或类似的宏时，有时从切片机变量传递参数到宏很有用。

在Cura中，要传递温度，将使用以下启动gcode：

```
START_PRINT BED_TEMP={material_bed_temperature_layer_0} EXTRUDER_TEMP={material_print_temperature_layer_0}
```

在PrusaSlicer和SuperSlicer等slic3r衍生产品中，将使用以下方法：

```
START_PRINT EXTRUDER_TEMP=[first_layer_temperature] BED_TEMP=[first_layer_bed_temperature]
```

另请注意，当不满足某些条件时，这些切片机将插入自己的加热代码。在Cura中，存在`{material_bed_temperature_layer_0}`和`{material_print_temperature_layer_0}`变量就足以缓解这个问题。在slic3r衍生产品中，您将使用：

```
M140 S0
M104 S0
```

在宏调用之前。另请注意，SuperSlicer有一个"仅自定义gcode"按钮选项，可以达到相同的结果。

使用这些参数的START_PRINT宏示例可在config/sample-macros.cfg中找到