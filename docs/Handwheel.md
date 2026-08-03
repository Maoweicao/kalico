# Handwheel (Jog Wheel) Support

## Overview

The handwheel module allows using a physical rotary encoder to directly control printer axis movement. By rotating the encoder, users can precisely move the X, Y, Z, or E axis manually, suitable for calibration, debugging, and manual operation scenarios.

## Configuration

Add a `[handwheel]` section to `printer.cfg`:

```ini
[handwheel]
# Rotary encoder A/B phase pins (required)
encoder_pins: ^PA0, ^PA1

# Steps per detent: 2 (half-step) or 4 (full-step) (default: 4)
encoder_steps_per_detent: 4

# Button pin for toggling handwheel mode on/off (optional)
click_pin: ^PA2

# Button debounce delay in seconds (default: 0, no debounce)
# debounce_delay: 0.025

# Default active axis: X, Y, Z, or E (default: X)
axis: X

# Distance per detent in mm (default: 1.0)
step_distance: 1.0

# Normal move speed in mm/s (default: 100.0)
speed: 100.0

# Fast rotation move speed in mm/s (default: 6000.0)
jog_speed: 6000.0

# Fast rotation threshold in seconds (default: 0.030)
# Uses jog_speed when interval between rotations is less than this
fast_rate: 0.030
```

## Pin Description

| Parameter | Description | Example |
|-----------|-------------|---------|
| `encoder_pins` | Rotary encoder A/B phase pins, comma-separated | `^PA0, ^PA1` |
| `click_pin` | Encoder button pin (optional) | `^PA2` |
| `encoder_steps_per_detent` | Steps per detent, 2 or 4 | `4` |

> **Note**: If the `[display]` configuration uses the same `encoder_pins`, both modules share the same physical encoder. When the handwheel is active, menu navigation is automatically disabled; when the handwheel is off, menu navigation resumes.

## G-code Commands

### JOG

Start or stop handwheel jog mode.

```
JOG [AXIS=<axis>] [STEP=<distance>] [SPEED=<speed>] [STOP]
```

**Parameters**:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `AXIS` | Active axis (X/Y/Z/E) | Config value |
| `STEP` | Distance per detent in mm | 1.0 |
| `SPEED` | Move speed in mm/s | 100.0 |
| `STOP` | Stop handwheel mode | - |

**Examples**:

```gcode
JOG                        # Start with defaults
JOG AXIS=Z STEP=0.1        # Control Z axis, 0.1mm per step
JOG SPEED=200               # Set speed to 200mm/s
JOG STOP                    # Stop handwheel mode
```

### SET_JOG

Modify handwheel parameters without changing the active state.

```
SET_JOG [AXIS=<axis>] [STEP=<distance>] [SPEED=<speed>] [JOG_SPEED=<speed>]
```

**Parameters**:

| Parameter | Description |
|-----------|-------------|
| `AXIS` | Active axis (X/Y/Z/E) |
| `STEP` | Distance per detent in mm |
| `SPEED` | Normal move speed in mm/s |
| `JOG_SPEED` | Fast rotation move speed in mm/s |

**Examples**:

```gcode
SET_JOG AXIS=Y              # Switch to Y axis
SET_JOG STEP=0.01           # Set 0.01mm per step
SET_JOG SPEED=200 JOG_SPEED=12000  # Set speeds
```

## Usage

### Method 1: G-code Commands

Activate the handwheel via terminal G-code commands:

```gcode
JOG AXIS=X STEP=1.0
```

Once activated, the rotary encoder controls X axis movement, 1.0mm per detent.

### Method 2: LCD Menu

If an LCD display is configured, operate through the menu:

1. Navigate to **Control** → **Handwheel**
2. Select **Jog: OFF** to toggle to **Jog: ON**
3. Use **Axis** to select the active axis
4. Use **Step** to select the step distance

### Method 3: Physical Button

If `click_pin` is configured, short-press the encoder button to toggle handwheel mode on/off.

## Operating Modes

| Mode | Encoder Rotation | Button Press |
|------|-----------------|--------------|
| Menu Mode (default) | Navigate menu up/down | Confirm selection |
| Handwheel Mode | Control axis movement | Switch back to menu mode |

## Safety Restrictions

- **Homing Protection**: X/Y/Z axes must be homed before handwheel movement
- **E Axis Restriction**: E axis movement requires X axis to be homed
- **Error Handling**: Move failures are logged automatically without interrupting the system

## Status Query

Handwheel status is accessible via `printer.handwheel`:

```gcode
{printer.handwheel.is_active}      # Is active
{printer.handwheel.active_axis}    # Current active axis
{printer.handwheel.step_distance}  # Current step distance
{printer.handwheel.speed}          # Current speed
```

## Wiring Example

Typical rotary encoder module (e.g., KY-040) wiring:

```
Encoder Pin    MCU Pin
──────────────────────
CLK (A)    →   PA0 (pull-up)
DT  (B)    →   PA1 (pull-up)
SW         →   PA2 (pull-up)
VCC        →   3.3V
GND        →   GND
```

Configuration example:

```ini
[handwheel]
encoder_pins: ^PA0, ^PA1
click_pin: ^PA2
encoder_steps_per_detent: 4
axis: X
step_distance: 1.0
speed: 100.0
```

## Troubleshooting

| Problem | Possible Cause | Solution |
|---------|---------------|----------|
| No response to rotation | Handwheel not activated | Send `JOG` command or press button to activate |
| Movement direction reversed | A/B phase wires swapped | Swap the two pins in `encoder_pins` |
| Multiple steps per detent | Wrong `steps_per_detent` setting | Try changing to `2` or `4` |
| Intermittent movement | Encoder quality issue | Increase `debounce_delay` value |
| Menu navigation not working | Handwheel is active | Press button or send `JOG STOP` to deactivate |
