# 前沿功能配置参考

本文档是 Kalico 配置文件中可用的前沿功能选项的参考。
有关特定功能的详细信息，请参阅 [前沿文档](Bleeding_Edge.md)。

本文档中的描述的格式使其可以将其剪切并粘贴到打印机配置文件中。
有关设置 Kalico 和选择初始配置文件的信息，
请参阅 [安装文档](Installation.md)。

## 高精度步进和新的 stepcompress 协议

此功能在 Kalico 固件编译期间通过在 menuconfig 中选择
"高精度步进支持"选项来启用。然后需要将固件刷入所有使用此功能的 MCU。

![make_menuconfig](img/high-precision-menu-makeconfig.jpg)

以下配置行应添加到 **printer.cfg** 中的每个步进器。
例如，在 CoreXY 系统中，配置行将添加到 [stepper_x] 和 [stepper_y]
中，使其在控制工具头 X-Y 运动的两个步进器中启用。

```
[stepper_... ]
high_precision_step_compress: True
```

请注意，在配置中启用此功能而不重新编译和刷入固件将给出错误。

## 输入整形器

### [input_shaper]

**挤出机 PA 与输入整形同步**

```
[input_shaper]
enabled_extruders: extruder
```

**光滑输入整形器**

```
[input_shaper]
shaper_type:
#   要为 X 和 Y 轴使用的输入整形器类型。支持的
#   整形器为 smooth_zv、smooth_mzv、smooth_ei、smooth_2hump_ei、smooth_zvd_ei、
#   smooth_si、mzv、ei、2hump_ei。
#shaper_type_x:
#shaper_type_y:
#   如果未设置 shaper_type，这两个参数可用于
#   为 X 和 Y 轴配置不同的输入整形器。支持与
#   shaper_type 参数相同的值。
smoother_freq_x: 0
#  X 轴光滑输入整形器的频率（Hz）。
smoother_freq_y: 0
#  Y 轴光滑输入整形器的频率（Hz）。
#damping_ratio_x: 0.1
#damping_ratio_y: 0.1
#   X 和 Y 轴振动的阻尼比，用于输入整形器
#   以改进振动抑制。默认值为 0.1，
#   这是大多数打印机的良好全面值。在大多数情况下，
#   此参数不需要调谐，不应更改。
#   注意：输入光滑器目前不支持阻尼比。
```

## 测试打印实用程序

### [ringing_test]

铃声塔测试打印实用程序，一次隔离一个轴的振动。

```
[ringing_test]
size: 100
#   塔足迹的 X-Y 尺寸（mm）
height: 60
#   塔的高度（mm）
band: 5
#   每个铃声步骤的高度（mm）
perimeters: 2
#   要为塔打印的周长数
velocity: 80
#   是在计算共振频率时作为公式 V * N / D 中的 V 使用的速度
#   其中 N 和 D 是振荡数和它们之间的距离（照常）：
brim_velocity: 30
#   边框打印速度（mm/s）
accel_start: 1500
#   测试开始的加速度
accel_step: 500
#   每个 `band` 加速度的增量 (mm/s^2)
layer_height: 0.2
first_layer_height: 0.2
filament_diameter: 1.75

#   自动计算的参数，但必要时可能调整

#center_x:
#   默认床的中心（如果检测正确）
#center_y:
#   默认床的中心（如果检测正确）
#brim_width:
#   根据模型大小计算，但可能增加

#   最好保持其默认值的参数

#notch: 1
#   mm 中的槽口尺寸
#notch_offset:
#   默认 0.275 * 大小
#deceleration_points: 100
```

### [pa_test]

压力提前塔测试打印实用程序

```
[pa_test]
size_x: 100
#    塔 X 尺寸（mm）
size_y: 50
#    塔 Y 尺寸（mm）
height: 50
#   塔的高度（mm）
origin_x:
#   x 中床的中心
origin_y:
#   y 中床的中心
layer_height: 0.2
first_layer_height: 0.3
perimeters: 2
#   要为塔打印的周长数
brim_width: 10
#   边框宽度（mm）
slow_velocity: 20
#   PA 测试段的启动速度（mm/s）
medium_velocity: 50
#   PA 测试段的中等速度（mm/s）
fast_velocity: 80
#   PA 测试段的结束速度（mm/s）
filament_diameter: 1.75