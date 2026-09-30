# Filament Blockage Detection

## Overview

Detects three types of filament feed problems: runout (no filament), slip (motor turns but filament doesn't move), and blockage (encoder reports movement but extruder doesn't). This is a firmware-level (MCU) implementation for low-latency detection.

## Configuration

### MCU Sensor

```ini
[filament_blockage_sensor my_sensor]
encoder_pin: ^PA7           # Encoder GPIO pin (required)
#event_delay: 0.003         # Minimum time between events (default: 0.003)
#pause_delay: 0.5           # Time from event to pause (default: 0.5)
#extruder: extruder         # Extruder to monitor (default: extruder)
```

### Calibration

```ini
[filament_blockage_calibration my_sensor]
#min_threshold: 150         # Minimum edge count for detection (default: 150)
```

Calibration is performed automatically on startup or manually via `CALIBRATE_FILAMENT_BLOCKAGE`.

## G-code Commands

| Command | Description |
|---------|-------------|
| `ENABLE_FILAMENT_BLOCKAGE` | Enable sensor |
| `DISABLE_FILAMENT_BLOCKAGE` | Disable sensor |
| `CALIBRATE_FILAMENT_BLOCKAGE` | Run calibration |
| `STATUS_FILAMENT_BLOCKAGE` | Print status |
| `SET_FILAMENT_BLOCKAGE_MIN_THRESHOLD THRESHOLD=<n>` | Set minimum edge count threshold |

## Event Types

| Event | Meaning |
|-------|---------|
| `RUNOUT` | No filament detected |
| `SLIP` | Motor turns but filament doesn't |
| `BLOCKAGE` | Encoder moves but extruder doesn't |

## Status Variables

Access via `printer["filament_blockage_sensor my_sensor"]`:

| Variable | Type | Description |
|----------|------|-------------|
| `enabled` | bool | Whether sensor is active |
| `is_blockage` | bool | Whether blockage is detected |
| `is_paused` | bool | Whether print is paused due to event |
| `edge_count` | int | Current encoder edge count |
| `min_threshold` | int | Minimum edge count threshold |
| `total_runout` | int | Total runout events |
| `total_slip` | int | Total slip events |
| `total_blockage` | int | Total blockage events |
| `blockage_threshold` | float | Max encoder edges before blockage (default: 80) |
| `slip_threshold` | float | Min encoder edges to confirm slip (default: 8) |
| `total_distance` | float | Total distance pushed (mm) |
| `calibration_edge_count` | float | Calibrated edge count per mm |

## How It Works

The MCU firmware polls the encoder GPIO at high frequency. It tracks three signals:
1. `is_extrude_request`: Whether Klipper is commanding the extruder motor
2. `is_pushing`: Whether the encoder detects filament movement
3. `is_rotate`: Whether the extruder motor driver reports rotation

By comparing these signals over time windows, the firmware detects runout, slip, and blockage conditions and generates corresponding events.