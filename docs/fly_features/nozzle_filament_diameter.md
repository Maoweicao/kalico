# Nozzle & Filament Diameter Commands / 喷嘴与耗材直径命令

## Overview / 概述

Allows runtime adjustment of nozzle diameter and filament diameter without modifying `printer.cfg`. Changes are persistent across restarts (saved via `SAVE_CONFIG`).

允许在运行时调整喷嘴直径和耗材直径，无需修改 `printer.cfg`。更改在重启后持久化（通过 `SAVE_CONFIG` 保存）。

## G-code Commands / G-code 命令

### SET_NOZZLE_DIAMETER

Set the nozzle diameter for the active extruder.

设置活动挤出机的喷嘴直径。

```
SET_NOZZLE_DIAMETER DIAMETER=<mm>
```

| Parameter | Type | Description | 说明 |
|-----------|------|-------------|------|
| `DIAMETER` | float | Nozzle diameter in mm (must be > 0) | 喷嘴直径(mm)，必须>0 |

**Example / 示例:**
```
SET_NOZZLE_DIAMETER DIAMETER=0.4
```

### SET_FILAMENT_DIAMETER

Set the filament diameter for the active extruder.

设置活动挤出机的耗材直径。

```
SET_FILAMENT_DIAMETER DIAMETER=<mm>
```

| Parameter | Type | Description | 说明 |
|-----------|------|-------------|------|
| `DIAMETER` | float | Filament diameter in mm (must be > nozzle diameter) | 耗材直径(mm)，必须>喷嘴直径 |

**Example / 示例:**
```
SET_FILAMENT_DIAMETER DIAMETER=1.75
```

## Effects / 影响

These commands adjust:

- `nozzle_diameter` — affects volumetric flow calculations and collision detection
- `filament_area` — calculated as `π × (diameter/2)²`
- `max_extrude_ratio` — recalculated based on new values: `4 × nozzle_diameter² / filament_area`

这些命令调整：

- `nozzle_diameter` — 影响体积流量计算和碰撞检测
- `filament_area` — 计算为 `π × (直径/2)²`
- `max_extrude_ratio` — 基于新值重新计算：`4 × 喷嘴直径² / 耗材面积`

## Safety / 安全

- Filament diameter must be **greater than** nozzle diameter (otherwise you get an error).
- If filament diameter equals nozzle diameter, the max extrude ratio becomes exactly 4, meaning the extruder can push filament at most equal to nozzle area. This is physically unrealistic for most printers, so the extruder will refuse large moves.

- 耗材直径必须**大于**喷嘴直径（否则报错）。
- 如果耗材直径等于喷嘴直径，最大挤出比恰好为4，这意味着挤出机最多能推动等于喷嘴面积的耗材。这对大多数打印机来说在物理上不现实，因此挤出机会拒绝大的移动。

## Persistent Storage / 持久化存储

After using either command, `SAVE_CONFIG` must be called to persist the change to `printer.cfg`. The printer will restart with the new values.

使用任一命令后，必须调用 `SAVE_CONFIG` 将更改持久化到 `printer.cfg`。打印机将以新值重启。
