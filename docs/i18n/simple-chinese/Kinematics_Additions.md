# 附加运动学

本文档描述了在标准 Klipper 运动学基础上添加到 Kalico 的附加运动学模块。

## 支持的运动学

| 运动学 | 配置名称 | 描述 |
|--------|----------|------|
| SCARA | `scara` | 选择性顺应装配机器人臂 |
| TPARA | `tpara` | 三平行轴旋转臂 |
| Polargraph | `polargraph` | 绳索驱动的墙面绘图仪 |
| Belt Printer | `belt` | 无限Z轴传送带打印机 |
| Robot Arm | `robot_arm` | 多关节铰接臂 |
| Foam Cutter | `foam_cutter` | XYUV热丝切割机 |
| CoreYX | `coreyx` | 反向CoreXY |
| CoreYZ | `coreyz` | YZ轴耦合 |
| CoreZX | `corezx` | ZX轴耦合 |
| CoreZY | `corezy` | ZY轴耦合 |

## SCARA 运动学

SCARA（选择性顺应装配机器人臂）是一种常见的工业机器人臂配置。

### 配置

```
[printer]
kinematics: scara

[scara]
linkage_1: 150
#   内臂长度，单位为毫米。此参数必须提供。
linkage_2: 150
#   外臂长度，单位为毫米。此参数必须提供。
offset_x: 100
#   塔架相对于床中心的X偏移量，单位为毫米。默认值为0。
offset_y: -56
#   塔架相对于床中心的Y偏移量，单位为毫米。默认值为0。
segments_per_second: 200
#   曲线运动的每秒段数。默认值为200。
variant: morgan
#   SCARA变体："morgan"或"mp"。默认值为"morgan"。
print_radius: 250
#   最大打印半径，单位为毫米。默认值为linkage_1 + linkage_2。
home_x: 100
#   归位X位置，单位为毫米。默认值为0。
home_y: 100
#   归位Y位置，单位为毫米。默认值为0。
home_z: 0
#   归位Z位置，单位为毫米。默认值为0。
max_z: 300
#   最大Z高度，单位为毫米。默认值为300。
```

### 步进电机配置

```
[stepper_a]
# 肩部电机（旋转）
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
#   每完整旋转360度
microsteps: 16

[stepper_b]
# 肘部电机（旋转）
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_z]
# Z轴（线性）
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 300
microsteps: 16
```

### 变体

- **Morgan SCARA**：使用笛卡尔XY归位位置
- **MP SCARA**：使用臂角度进行AB归位

## TPARA 运动学

TPARA（三平行轴旋转臂）是一种具有三个平行旋转轴的3轴机器人臂。

### 配置

```
[printer]
kinematics: tpara

[tpara]
linkage_1: 120
#   内臂长度，单位为毫米。此参数必须提供。
linkage_2: 120
#   外臂长度，单位为毫米。此参数必须提供。
offset_x: 0
#   X偏移量，单位为毫米。默认值为0。
offset_y: 0
#   Y偏移量，单位为毫米。默认值为0。
offset_z: 0
#   Z偏移量，单位为毫米。默认值为0。
segments_per_second: 200
#   每秒段数。默认值为200。
print_radius: 200
#   最大打印半径，单位为毫米。默认值为linkage_1 + linkage_2。
max_z: 300
#   最大Z高度，单位为毫米。默认值为300。
```

### 步进电机配置

```
[stepper_a]
# 底座旋转
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
microsteps: 16

[stepper_b]
# 肩部旋转
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_c]
# 肘部旋转
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
rotation_distance: 360
microsteps: 16
```

## Polargraph 运动学

Polargraph（也称为墙面绘图仪或绳索驱动绘图仪）使用安装在顶部角落的两个电机通过绳索/电缆控制笔/夹持器。

### 配置

```
[printer]
kinematics: polargraph

[polargraph]
motor_distance_x: 1000.0
#   两个电机中心之间的距离，单位为毫米。此参数必须提供。
motor_offset_y: 50.0
#   从电机中心到归位位置的Y偏移量，单位为毫米。默认值为0。
max_belt_length: 1200.0
#   最大皮带/电缆长度，单位为毫米。默认值为motor_distance_x * 1.2。
segments_per_second: 5
#   每秒段数。默认值为5。
```

### 步进电机配置

```
[stepper_left]
# 左电机
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 40
microsteps: 16

[stepper_right]
# 右电机
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 40
microsteps: 16

[stepper_z]
# 可选Z轴用于抬笔
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 100
microsteps: 16
```

## 传送带打印机运动学

传送带打印机具有无限Z轴（传送带床面），通常倾斜45度。

### 配置

```
[printer]
kinematics: belt

[belt]
bed_tilt: 45.0
#   床面倾斜角度，单位为度。默认值为45。
bed_rotation_axis: y
#   床面旋转轴："x"或"y"。默认值为"y"。
segments_per_second: 10
#   每秒段数。默认值为10。
```

### 步进电机配置

```
[stepper_x]
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
position_endstop: 0
position_max: 200

[stepper_y]
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
position_endstop: 0
position_max: 200

[stepper_z]
# 传送带电机
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 200
```

## 机器人臂运动学

具有多个旋转关节的铰接机器人臂。

### 配置

```
[printer]
kinematics: robot_arm

[robot_arm]
d1: 100
#   底座高度，单位为毫米。默认值为100。
a1: 50
#   连杆1长度，单位为毫米。默认值为50。
a2: 200
#   连杆2长度，单位为毫米。默认值为200。
a3: 150
#   连杆3长度，单位为毫米。默认值为150。
segments_per_second: 100
#   每秒段数。默认值为100。
```

### 步进电机配置

```
[stepper_a]
# 底座旋转
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
microsteps: 16

[stepper_b]
# 肩部旋转
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_c]
# 肘部旋转
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
rotation_distance: 360
microsteps: 16
```

## 热丝切割机运动学

热丝切割机使用热丝切割泡沫，通常有4个轴：X、Y（热丝顶部）和U、V（热丝底部）。

### 配置

```
[printer]
kinematics: foam_cutter

[foam_cutter]
wire_length: 500.0
#   热丝长度，单位为毫米。此参数必须提供。
segments_per_second: 10
#   每秒段数。默认值为10。
```

### 步进电机配置

```
[stepper_x]
# 热丝顶部X
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
position_endstop: 0
position_max: 500

[stepper_y]
# 热丝顶部Y
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
position_endstop: 0
position_max: 500

[stepper_u]
# 热丝底部X
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 500

[stepper_v]
# 热丝底部Y
step_pin: PD0
dir_pin: PD1
endstop_pin: PD2
position_endstop: 0
position_max: 500
```

## Core 变体

这些是标准 CoreXY 运动学的不同轴耦合变体。

### CoreYX

反向 CoreXY - Y 独立移动，X 和 Z 耦合。

```
[printer]
kinematics: coreyx
```

### CoreYZ

X 独立移动，Y 和 Z 耦合。

```
[printer]
kinematics: coreyz
```

### CoreZX

Y 独立移动，Z 和 X 耦合。

```
[printer]
kinematics: corezx
```

### CoreZY

Z 独立移动，X 和 Y 耦合。

```
[printer]
kinematics: corezy
```

## 注意事项

- 所有旋转轴使用 `rotation_distance: 360` 表示每完整旋转360度
- SCARA 和 TPARA 需要仔细校准臂长
- Polargraph 需要准确测量电机距离
- 传送带打印机需要正确配置床面倾斜角度
- 热丝切割机必须正确配置热丝长度

## 另请参阅

- [运动学概述](Kinematics.md)
- [配置参考](Config_Reference.md)
- [G-code 命令](G-Codes.md)
