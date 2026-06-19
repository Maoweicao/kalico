# 前沿功能配置参考

本文档是 Kalico 配置文件中前沿功能可用选项的参考。有关特定功能的详细信息，请参阅[前沿功能文档](Bleeding_Edge.md)。

本文档中的描述格式使得可以直接复制粘贴到打印机配置文件中。有关设置 Kalico 和选择初始配置文件的信息，请参阅[安装文档](Installation.md)。

## 高精度步进和新的 stepcompress 协议

此功能在 Kalico 固件编译期间通过在 menuconfig 中选择"高精度步进支持"选项来启用。然后需要使用此功能将固件刷写到所有 MCU。

![make_menuconfig](/img/high-precision-menu-makeconfig.jpg)

以下配置行应添加到 **printer.cfg** 中的每个步进器。例如，在 CoreXY 系统中，配置行将添加到 [stepper_x] 和 [stepper_y]，以便在控制工具头 X-Y 运动的两个步进器上都启用它。

```
[stepper_... ]
high_precision_step_compress: True
```

请注意，在不重新编译和刷写固件的情况下在配置中启用此功能将导致错误。

## 输入整形

### [input_shaper]

**挤出机 PA 与输入整形同步**

```
[input_shaper]
enabled_extruders: extruder
```

**平滑输入整形器**

```
[input_shaper]
shaper_type:
#   用于 X 和 Y 轴的输入整形器类型。支持的
#   整形器有 smooth_zv、smooth_mzv、smooth_ei、smooth_2hump_ei、smooth_zvd_ei、
#   smooth_si、mzv、ei、2hump_ei。
#shaper_type_x:
#shaper_type_y:
#   如果未设置 shaper_type，可以使用这两个参数来
#   为 X 和 Y 轴配置不同的输入整形器。支持与
#   shaper_type 参数相同的值。
smoother_freq_x: 0
#  X 轴平滑输入整形器的频率（Hz）。
smoother_freq_y: 0
#  Y 轴平滑输入整形器的频率（Hz）。
#damping_ratio_x: 0.1
#damping_ratio_y: 0.1
#   输入整形器用于改善振动抑制的 X 和 Y 轴
#   振动阻尼比。默认值为 0.1，这对大多数打印机
#   来说是一个很好的通用值。在大多数情况下，此
#   参数无需调整，不应更改。
#   注意：输入平滑器目前不支持阻尼比。
```

## 测试打印工具

### [ringing_test]

振铃塔测试打印工具，一次将振动隔离到一个轴。

```
[ringing_test]
size: 100
#   塔占地面积的 X-Y 尺寸（mm）
height: 60
#   塔的高度（mm）
band: 5
#   每个振铃步骤的高度（mm）
perimeters: 2
#   塔要打印的周长数
velocity: 80
#   速度，必须在公式 V * N / D 中用作 V
#   来计算共振频率。N 和 D 分别是振荡次数
#   和它们之间的距离：
brim_velocity: 30
#   打印边缘的速度（mm/s）
accel_start: 1500
#   测试开始时的加速度
accel_step: 500
#   每 `band` 的加速度增量（mm/s^2）
layer_height: 0.2
first_layer_height: 0.2
filament_diameter: 1.75

#   自动计算的参数，但如有必要可以调整

#center_x:
#   默认床面中心（如果正确检测）
#center_y:
#   默认床面中心（if correctly detected）
#brim_width:
#   基于模型尺寸计算，但可以增加

#   最好保持默认值的参数

#notch: 1
#   凹口大小（mm）
#notch_offset:
#   默认 0.275 * size
#deceleration_points: 100
```

### [pa_test]

压力提前塔测试打印工具

```
[pa_test]
size_x: 100
#    X 方向塔尺寸（mm）
size_y: 50
#    Y 方向塔尺寸（mm）
height: 50
#   塔的高度（mm）
origin_x:
#   床面 X 中心
origin_y:
#   床面 Y 中心
layer_height: 0.2
first_layer_height: 0.3
perimeters: 2
#   塔要打印的周长数
brim_width: 10
#   边缘宽度（mm）
slow_velocity: 20
#   PA 测试段的起始速度（mm/s）
medium_velocity: 50
#   PA 测试段的中间速度（mm/s）
fast_velocity: 80
#   PA 测试段的结束速度（mm/s）
filament_diameter: 1.75
```
