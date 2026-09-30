# Power Loss Resume

## Overview

When a power outage or M112 emergency stop occurs during a print, this module automatically saves the current print state. Upon power restoration and printer restart, it resumes printing from where it left off.

## Configuration

Add to `printer.cfg`:

```ini
[power_loss_resume]
#resume_gcode: G28 X Y      # G-code to run after resume (optional)
#start_gcode:                # Additional start gcode (optional)
#max_layer_save: 500         # Maximum layers to save progress (default: 500)
#enable_shutdown_save: True  # Save state on M112 shutdown (default: True)
#enable_resume_speed: True   # Apply configured speed on resume (default: True)
#resume_speed: 150           # Speed to apply on resume (default: 150)
```

## G-code Commands

| Command | Description |
|---------|-------------|
| `ENABLE_POWER_LOSS_RESUME` | Enable power loss resume |
| `DISABLE_POWER_LOSS_RESUME` | Disable power loss resume |
| `RESET_POWER_LOSS_RESUME` | Clear saved state and delete file |
| `STATUS_POWER_LOSS_RESUME` | Print current status |

## Status Variables

Access via `printer["power_loss_resume"]`:

| Variable | Type | Description |
|----------|------|-------------|
| `state` | int | 0=off, 1=ready, 2=power lost |
| `file_path` | string | Path to saved resume data |
| `last_epos` | float | Last known E position |
| `last_z` | float | Last known Z position |
| `last_layer` | int | Last layer number |
| `is_resume_speed` | bool | Whether speed override is active |

## How It Works

1. On `M112` shutdown or power loss detection, saves current position, temperatures, fan speeds, bed mesh, pressure advance, flow rate, extruder position, and layer count.
2. On restart, if resume data exists, `SAVE_RESTART gcode` is automatically issued.
3. The printer performs homing, reheats, and resumes G-code execution from the saved position.

## Safety Notes

- After resume, the printer executes a full G28 homing sequence. Ensure the bed is clear before resuming.
- The resume file is stored in the same directory as the main G-code file.
- If you manually print a different file, the old resume data is automatically cleared.