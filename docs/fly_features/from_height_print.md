# From-Height Print

## Overview

Allows resuming a print from a specific Z height instead of from the beginning. The system parses the G-code file to find the target Z height, extracts the printer state (temperatures, fan speed, extrusion mode) at that point, and resumes printing from there with the correct preamble commands.

## How It Works

1. The Mainsail/Fluidd UI sends a POST request to `virtual_sdcard/from_height_print` with `filename` and `height` parameters.
2. A background thread parses the G-code file to find the target Z height.
3. The parser identifies the slicer type (CURA, OrcaSlicer, Simplify3D) and extracts:
   - Last extruder temperature
   - Last bed temperature
   - Last fan speed
   - Absolute/relative extrusion mode
   - Absolute/relative position mode
   - File byte position at the target Z height
4. Preamble scripts (M109, M190, M106, M82/M83, G90/G91) are injected before the main print loop.
5. The file is seeked to the extracted position and printing continues.

## Webhook API

**Endpoint:** `POST /printerwebhook/virtual_sdcard/from_height_print`

| Parameter | Type | Description |
|-----------|------|-------------|
| `filename` | string | G-code file path (relative to sdcard_dirname) |
| `height` | float | Target Z height to resume from |

**Example:**
```json
{
    "filename": "my_print.gcode",
    "height": 10.5
}
```

## Supported Slicers

| Slicer | Z-Height Detection |
|--------|-------------------|
| Cura | G0/G1 Z commands |
| OrcaSlicer | `;LAYER_CHANGE` comments |
| Simplify3D | `; layer` comments with `=` |

## State Machine

The from-height feature uses a 3-state machine (`_parse_state`):

| State | Meaning |
|-------|---------|
| 0 | Idle |
| 1 | Parsing in progress |
| 2 | Parse failed |
| 3 | Parse complete, ready to print |

The `work_handler` polls `_parse_state` every 0.1s while parsing. On success (state 3), it falls through to the normal print loop with the injected preamble scripts.

## External Parser

The threaded parser (`_thread_parse_gcode`) uses an external `parse_gcode` binary via subprocess. If this binary is not available, the in-process parser (`_parse_gcode`) can be used as a fallback. The in-process parser is less efficient but has no external dependencies.

## Status Variables

Access via `printer["virtual_sdcard"]`:

| Variable | Type | Description |
|----------|------|-------------|
| `is_from_height` | bool | Whether from-height print is active |

## Safety Notes

- The printer will execute homing before resuming. Ensure the bed is clear.
- The preamble scripts restore the printer state that existed at the target Z height.
- If the target Z height is not found (e.g., the slicer is not supported), the parse will fail and the print will be cancelled.
- Canceling the print during parsing properly cleans up the parser thread.