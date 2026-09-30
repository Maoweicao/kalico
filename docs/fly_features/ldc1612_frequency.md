# LDC1612 External Crystal Frequency Configuration

## Overview

Enhances the LDC1612 inductive sensor driver with configurable external crystal frequency and automatic sensor divider calculation. This allows the use of LDC1612-based sensors with non-standard coil frequencies.

## Configuration

In your `[ldc1612]` or `[ldc1612 chip_name]` section:

```ini
[ldc1612]
frequency: 12000000          # External crystal frequency in Hz (default: 12000000)
max_sensor_hz: 5000000       # Maximum sensor frequency in Hz (default: 5000000)
```

## Parameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| `frequency` | 12000000 | 2000000–40000000 | External crystal reference frequency |
| `max_sensor_hz` | 5000000 | 3000000–20000000 | Maximum coil oscillation frequency |

## How the Divider Is Calculated

The sensor divider is computed as:

```
sensor_div = ceil(4 × max_sensor_hz / frequency)
```

This ensures that `4 × max_sensor_hz < frequency × sensor_div`, satisfying the LDC1612's requirement that the coil frequency must be less than 1/4 of the reference clock.

## Calibration Warning

If the LDC1612 calibration data contains frequencies that exceed `max_sensor_hz`, a runtime warning will be displayed:

```
ldc1612 chip_name: Should set 'max_sensor_hz' to at least <frequency>
```

Update your config accordingly and run `SAVE_CONFIG`.

## Common Configurations

| Sensor | frequency | max_sensor_hz |
|--------|-----------|---------------|
| BTT Eddy | 12000000 | 5000000 |
| Custom coil (8MHz) | 8000000 | 3000000 |
| Custom coil (16MHz) | 16000000 | 6000000 |