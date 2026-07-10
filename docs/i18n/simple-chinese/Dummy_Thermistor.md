# 假热敏传感器

假热敏传感器是一种虚拟温度传感器，无需物理传感器即可提供固定的温度读数。主要用于：

- 无需硬件的测试和开发
- 不需要温度监控的陶泥/混凝土挤出机
- 调试打印机配置

## 配置

### 基本用法

```
[temperature_sensor my_dummy_sensor]
sensor_type: dummy_thermistor
temperature: 25.0
#   报告的固定温度（摄氏度）。默认值为 25.0。
#min_temp:
#max_temp:
#   上述参数的定义请参阅"extruder"部分。
```

### 示例：用于陶泥的冷挤出机

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
sensor_type: dummy_thermistor
temperature: 25.0
min_extrude_temp: 0
#   设置为 0 以允许冷挤出
```

### 示例：无硬件测试

```
[extruder]
sensor_type: dummy_thermistor
temperature: 200.0
#   模拟 200°C 的热端

[heated_bed]
sensor_type: dummy_thermistor
temperature: 60.0
#   模拟 60°C 的热床
```

## G-code 命令

### SET_DUMMY_TEMPERATURE

在运行时设置假热敏传感器报告的温度。

```
SET_DUMMY_TEMPERATURE SENSOR=<名称> [TEMPERATURE=<值>]
```

参数：
- `SENSOR`：假热敏传感器的名称（必填）
- `TEMPERATURE`：新的温度值，单位为摄氏度（可选）

示例：
```
# 将腔室传感器设置为 40°C
SET_DUMMY_TEMPERATURE SENSOR=chamber TEMPERATURE=40.0

# 查询 mcu_temp 传感器的当前温度
SET_DUMMY_TEMPERATURE SENSOR=mcu_temp
```

## 使用场景

### 1. 开发和测试

在没有物理硬件的情况下开发或测试打印机配置时，假热敏传感器允许您：

- 测试检查温度的 G-code 脚本
- 验证加热器控制逻辑
- 运行模拟而不会出现温度错误

### 2. 冷挤出

对于不需要加热的材料（陶泥、混凝土、食品酱），使用假热敏传感器可以：

- 避免"加热器未配置"错误
- 保持与期望温度读数的切片软件兼容性
- 允许 M104/M109 命令成功执行而不采取行动

### 3. 温度监控点

创建虚拟温度监控点，用于：

- 室温跟踪
- 腔室温度模拟
- 调试温度相关逻辑

## 技术细节

假热敏传感器传感器：

- 报告固定温度值（可配置）
- 更新频率为 1Hz（每秒 1 次）
- 默认忽略 min_temp/max_temp 限制
- 可通过 G-code 动态更新
- 注册为标准温度传感器

## 与 Marlin 的比较

此实现类似于 Marlin 的假热敏表：

| 特性 | Marlin | Kalico |
|------|--------|--------|
| 传感器类型 | 表 998 (25°C) / 表 999 (100°C) | `dummy_thermistor` |
| 固定温度 | 是（通过 `DUMMY_THERMISTOR_*_VALUE`） | 是（通过 `temperature` 配置） |
| 动态更新 | 否 | 是（通过 `SET_DUMMY_TEMPERATURE`） |
| 适用插槽 | 所有 TEMP_SENSOR_* | 任何 sensor_type 字段 |

## 另请参阅

- [温度传感器](Config_Reference.md#温度传感器)
- [挤出机配置](Config_Reference.md#挤出机)
- [G-code 命令](G-Codes.md)
