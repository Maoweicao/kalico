# LDC1612 External Crystal Frequency Configuration / LDC1612 外部晶振频率配置

## Overview / 概述

Enhances the LDC1612 inductive sensor driver with configurable external crystal frequency and automatic sensor divider calculation. This allows use of LDC1612-based sensors with non-standard coil frequencies.

增强LDC1612电感传感器驱动器，支持可配置的外部晶振频率和自动传感器分频器计算。这允许使用具有非标准线圈频率的基于LDC1612的传感器。

## Configuration / 配置

In your `[ldc1612]` or `[ldc1612 chip_name]` section:

```ini
[ldc1612]
frequency: 12000000          # External crystal frequency in Hz (default: 12000000)
                             # 外部晶振频率(Hz)，默认12000000
max_sensor_hz: 5000000       # Maximum sensor frequency in Hz (default: 5000000)
                             # 传感器最大频率(Hz)，默认5000000
```

## Parameters / 参数

| Parameter | Default | Range | Description | 说明 |
|-----------|---------|-------|-------------|------|
| `frequency` | 12000000 | 2000000–40000000 | External crystal reference frequency | 外部晶振参考频率 |
| `max_sensor_hz` | 5000000 | 3000000–20000000 | Maximum coil oscillation frequency | 最大线圈振荡频率 |

## How the Divider Is Calculated / 分频器计算原理

The sensor divider is computed as:

```
sensor_div = ceil(4 × max_sensor_hz / frequency)
```

This ensures that `4 × max_sensor_hz < frequency × sensor_div`, satisfying the LDC1612's requirement that the coil frequency must be less than 1/4 of the reference clock.

分频器计算公式：

```
sensor_div = ceil(4 × max_sensor_hz / frequency)
```

这确保 `4 × max_sensor_hz < frequency × sensor_div`，满足LDC1612的线圈频率必须小于参考时钟1/4的要求。

## Calibration Warning / 校准警告

If the LDC1612 calibration data contains frequencies that exceed `max_sensor_hz`, a runtime warning will be displayed:

如果LDC1612校准数据包含超过 `max_sensor_hz` 的频率，将显示运行时警告：

```
ldc1612 chip_name: Should set 'max_sensor_hz' to at least <frequency>
```

Update your config accordingly and run `SAVE_CONFIG`.

请相应更新配置并运行 `SAVE_CONFIG`。

## Common Configurations / 常见配置

| Sensor | frequency | max_sensor_hz | 说明 |
|--------|-----------|---------------|------|
| BTT Eddy | 12000000 | 5000000 | Default, works out of the box |
| Custom coil (8MHz) | 8000000 | 3000000 | Lower frequency coil |
| Custom coil (16MHz) | 16000000 | 6000000 | Higher frequency coil |
