# 冷挤出机（无加热器）

冷挤出机配置允许使用没有加热器的挤出机，用于不需要加热的材料，例如：

- 陶泥
- 混凝土
- 食品酱
- 硅胶
- 其他冷挤出材料

## 配置

### 基本用法

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
#   设置为 true 以将此配置为无加热器的冷挤出机。
#   默认值为 false。
sensor_type: dummy_thermistor
#   使用假热敏传感器，因为不需要真实的传感器。
temperature: 25.0
#   室温或任何固定值。
```

### 完整示例：陶泥打印机

```
[printer]
kinematics: cartesian
max_velocity: 100
max_accel: 500

[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 50.0
max_extrude_only_distance: 100.0
max_extrude_only_velocity: 10
max_extrude_only_accel: 50
step_pin: PC1
dir_pin: PC0
rotation_distance: 28.0

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
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 200
```

### 多个冷挤出机

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
step_pin: PC1
dir_pin: PC0
rotation_distance: 28.0

[extruder1]
nozzle_diameter: 3.0
filament_diameter: 15.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
step_pin: PD1
dir_pin: PD0
rotation_distance: 35.0
```

## 配置选项

当设置 `no_heater: true` 时：

- 不需要 `heater_pin`
- 不配置温度控制（PID、bang-bang 等）
- `min_extrude_temp` 自动设置为 0
- 挤出机可以在任何温度下挤出
- 仍然建议使用温度传感器以保持兼容性

### 冷材料的推荐设置

| 参数 | 陶泥 | 混凝土 | 食品酱 |
|------|------|--------|--------|
| nozzle_diameter | 1.0-2.0mm | 3.0-5.0mm | 0.8-1.5mm |
| filament_diameter | 5-15mm | 10-20mm | 3-5mm |
| max_extrude_only_velocity | 5-15 mm/s | 2-5 mm/s | 10-20 mm/s |
| max_extrude_only_accel | 25-100 mm/s² | 10-50 mm/s² | 50-200 mm/s² |

## G-code 兼容性

冷挤出机保持完整的 G-code 兼容性：

- `M104 S0` - 成功执行而不采取行动
- `M109 S0` - 成功执行而不等待
- `M302` - 报告冷挤出已启用
- `G1 E10` - 挤出材料

## 使用场景

### 1. 陶泥打印

陶泥打印机使用大喷嘴（1-3mm）并以慢速挤出。材料通常装入注射器或墨盒中。

```
[extruder]
nozzle_diameter: 2.0
filament_diameter: 20.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 100.0
max_extrude_only_distance: 200.0
max_extrude_only_velocity: 5
max_extrude_only_accel: 25
```

### 2. 食品打印

食品打印机挤出巧克力、面团或其他食品材料。温度控制可能需要单独处理（例如巧克力调温）。

```
[extruder]
nozzle_diameter: 0.8
filament_diameter: 5.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 22.0
max_extrude_cross_section: 20.0
max_extrude_only_velocity: 15
max_extrude_only_accel: 100
```

### 3. 混凝土/建筑打印

大型建筑打印机挤出混凝土混合物。流量控制至关重要。

```
[extruder]
nozzle_diameter: 10.0
filament_diameter: 50.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 500.0
max_extrude_only_distance: 500.0
max_extrude_only_velocity: 2
max_extrude_only_accel: 10
```

## 故障排除

### "挤出温度过低"错误

如果看到此错误，请确保：
1. 在挤出机部分设置了 `no_heater: true`
2. 配置了假热敏传感器（或任何 sensor_type）

### 切片软件温度命令

大多数切片软件会发送 `M104` 和 `M109` 命令。使用冷挤出机时：
- `M104 S200` 将成功执行而不加热
- `M109 S200` 将成功执行而不等待

### 流量控制

对于粘性材料，考虑：
- 增加 `max_extrude_only_distance`
- 减少 `max_extrude_only_velocity`
- 使用更大的 `nozzle_diameter`

## 另请参阅

- [挤出机配置](Config_Reference.md#挤出机)
- [假热敏传感器](Dummy_Thermistor.md)
- [G-code 命令](G-Codes.md)
