# Nozzle & Filament Diameter Commands

## Overview

Allows runtime adjustment of nozzle diameter and filament diameter without modifying `printer.cfg`. Changes are persistent across restarts (saved via `SAVE_CONFIG`).

## G-code Commands

### SET_NOZZLE_DIAMETER

Set the nozzle diameter for the active extruder.

```
SET_NOZZLE_DIAMETER DIAMETER=<mm>
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `DIAMETER` | float | Nozzle diameter in mm (must be > 0) |

**Example:**
```
SET_NOZZLE_DIAMETER DIAMETER=0.4
```

### SET_FILAMENT_DIAMETER

Set the filament diameter for the active extruder.

```
SET_FILAMENT_DIAMETER DIAMETER=<mm>
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `DIAMETER` | float | Filament diameter in mm (must be > nozzle diameter) |

**Example:**
```
SET_FILAMENT_DIAMETER DIAMETER=1.75
```

## Effects

These commands adjust:

- `nozzle_diameter` — affects volumetric flow calculations and collision detection
- `filament_area` — calculated as `π × (diameter/2)²`
- `max_extrude_ratio` — recalculated based on the new values: `4 × nozzle_diameter² / filament_area`

## Safety

- Filament diameter must be **greater than** nozzle diameter (otherwise you get an error).
- If filament diameter equals nozzle diameter, the max extrude ratio becomes exactly 4, meaning the extruder can push at most an amount of filament equal to the nozzle area. This is physically unrealistic for most printers, so the extruder will refuse large moves.

## Persistent Storage

After using either command, `SAVE_CONFIG` must be called to persist the change to `printer.cfg`. The printer will restart with the new values.