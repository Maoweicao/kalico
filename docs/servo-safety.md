# Servo Safety Monitoring

Kalico supports industrial-grade servo drive safety monitoring through ALM (alarm) pin detection and fault management.

## Features

- **ALM Pin Monitoring**: Real-time monitoring of servo drive alarm output pins
- **Configurable Actions**: Shutdown, pause, custom G-code, or none on alarm
- **Fault Detection**: CiA 402 fault state detection via communication protocols
- **G-code Commands**: Query and reset servo faults interactively
- **Status Reporting**: Drive state, error codes, and alarm status via API

## Quick Start

### Option 1: Integrated Configuration

Add ALM pin directly to your servo stepper configuration:

```ini
[canopen_stepper stepper_x]
canopen_bus: mybus
node_id: 1
eds_file: ~/servo.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1

# ALM alarm pin
alm_pin: PB7
alarm_action: shutdown
alm_invert: false
```

### Option 2: Independent Module

Use `[servo_alarm]` for flexible multi-axis monitoring:

```ini
[servo_alarm x_axis]
alm_pin: PB7
action: shutdown
invert: false
debounce: 0.01
```

## Configuration Reference

### Integrated Options

Add these options to `[canopen_stepper]`, `[ethercat_stepper]`, or `[rs485_stepper]`:

| Option | Default | Description |
|--------|---------|-------------|
| `alm_pin` | None | GPIO pin connected to servo ALM output |
| `alarm_action` | `shutdown` | Action on alarm: `shutdown`, `pause`, `gcode`, `none` |
| `alm_invert` | `false` | Invert pin logic (set `true` for active-high ALM) |

### `[servo_alarm]` Section

| Option | Default | Description |
|--------|---------|-------------|
| `alm_pin` | Required | GPIO pin for alarm input |
| `action` | `shutdown` | Alarm action: `shutdown`, `pause`, `gcode`, `none` |
| `invert` | `false` | Invert pin logic |
| `debounce` | `0.01` | Debounce time in seconds |
| `alarm_gcode` | None | G-code to execute (when `action: gcode`) |

### Action Types

| Action | Description |
|--------|-------------|
| `shutdown` | Emergency stop - halts all motion immediately |
| `pause` | Pause current print (if printing) |
| `gcode` | Execute custom G-code from `alarm_gcode` |
| `none` | Log only, no automatic action |

## G-code Commands

### `QUERY_SERVO [STEPPER=<name>]`

Query servo drive status. Without `STEPPER` parameter, queries all servos.

```
QUERY_SERVO                        # Query all servos
QUERY_SERVO STEPPER=stepper_x      # Query specific servo
```

Output:
```
stepper_x:
  state=OPERATION_ENABLED
  mode=CSP
  error_code=0x0000
  is_fault=False
  alarm_active=False
```

### `RESET_SERVO_FAULT STEPPER=<name>`

Reset servo drive fault via CiA 402 fault reset command.

```
RESET_SERVO_FAULT STEPPER=stepper_x
```

### `QUERY_SERVO_ALARM`

Query all `[servo_alarm]` module states.

```
QUERY_SERVO_ALARM
```

### `QUERY_ALARM_<name>` / `CLEAR_ALARM_<name>`

Query or clear specific `[servo_alarm]` state. The name is the last part of the section name.

```ini
[servo_alarm x_axis]
```
```
QUERY_ALARM_X_AXIS
CLEAR_ALARM_X_AXIS
```

### `QUERY_SERVO_ALARM STEPPER=<name>`

Query alarm state for specific stepper (when `alm_pin` is configured).

### `RESET_SERVO_ALARM STEPPER=<name>`

Reset alarm and fault for specific stepper.

## Status Fields

### Servo Stepper Status

| Field | Type | Description |
|-------|------|-------------|
| `state` | string | CiA 402 state (e.g., "OPERATION_ENABLED", "FAULT") |
| `actual_position` | int | Current encoder position |
| `error_code` | int | Drive error code (from 0x603F register) |
| `mode` | string | Operating mode (CSP, CSV, PP, etc.) |
| `is_fault` | bool | True if drive is in fault state |
| `statusword` | int | Raw CiA 402 statusword (0x6041) |
| `alarm_active` | bool | True if ALM pin is active |
| `alarm_count` | int | Number of alarm events since startup |

### ServoAlarm Status

| Field | Type | Description |
|-------|------|-------------|
| `alarm_active` | bool | True if alarm is currently active |
| `alarm_count` | int | Number of alarm triggers since startup |
| `last_alarm_time` | float | Timestamp of last alarm event |
| `pin` | string | Configured ALM pin |
| `action` | string | Configured alarm action |

## Hardware Wiring

### Typical Servo Drive ALM Output

Most servo drives have an open-collector ALM output:

```
Servo Drive                    MCU (e.g., STM32)
+---------+                    +------------+
| ALM OUT |---[10k pullup]---| GPIO (PBx) |
| GND     |-----------------| GND        |
+---------+                    +------------+
```

- **Normal state**: ALM pin is HIGH (pulled up)
- **Alarm state**: ALM pin is LOW (driven to GND)

For active-high ALM outputs, set `alm_invert: true`.

### Level Shifting

Some servo drives require 24V ALM output. Use one of:

1. **Voltage divider**: 24V -> 3.3V using resistor network
2. **Optocoupler**: Galvanic isolation (recommended for industrial)
3. **Level shifter module**: Bidirectional level conversion

### Example: 24V to 3.3V Voltage Divider

```
24V ALM ---[10k]---+---[5.6k]--- GND
                   |
                   +--- to MCU GPIO
```

## Examples

### Multi-Axis CNC Setup

```ini
# CANopen bus
[canopen_bus mybus]
interface: can0
channel: can0
bitrate: 1000000

# X axis
[canopen_stepper stepper_x]
canopen_bus: mybus
node_id: 1
eds_file: ~/servo_x.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB7
alarm_action: shutdown

# Y axis
[canopen_stepper stepper_y]
canopen_bus: mybus
node_id: 2
eds_file: ~/servo_y.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB8
alarm_action: shutdown

# Z axis
[canopen_stepper stepper_z]
canopen_bus: mybus
node_id: 3
eds_file: ~/servo_z.eds
canopen_mode: CSP
rotation_distance: 360
microsteps: 1
alm_pin: PB9
alarm_action: pause

# Global alarm handler
[gcode_macro ON_SERVO_ALARM]
gcode:
  {% set stepper = params.STEPPER|default("unknown") %}
  M118 ALARM: Servo fault on {stepper}!
  M104 S0  ; Turn off hotend
  M140 S0  ; Turn off bed
  {action_emergency_stop("Servo alarm")}
```

### Industrial Robot Arm

```ini
# Independent alarm monitoring with custom actions
[servo_alarm joint1_alarm]
alm_pin: PA0
action: gcode
invert: false
debounce: 0.01
alarm_gcode:
  M118 CRITICAL: Joint 1 servo alarm!
  {action_emergency_stop("Joint 1 ALM")}

[servo_alarm joint2_alarm]
alm_pin: PA1
action: gcode
invert: false
debounce: 0.01
alarm_gcode:
  M118 CRITICAL: Joint 2 servo alarm!
  {action_emergency_stop("Joint 2 ALM")}
```

## Troubleshooting

### Alarm Not Detected

1. Check wiring: Verify ALM pin is connected to correct GPIO
2. Check pin logic: Try `alm_invert: true` if alarm is active-high
3. Check debounce: Increase `debounce` time if experiencing false triggers
4. Query pin state: Use `QUERY_ALARM_<name>` to check current state

### False Alarms

1. Increase debounce time (e.g., `debounce: 0.02`)
2. Add hardware filtering (RC low-pass on ALM pin)
3. Check for noise on ALM signal wire

### Fault Reset Not Working

1. Verify drive supports CiA 402 fault reset
2. Check drive documentation for specific reset sequence
3. Some drives require power cycle after fault

### Status Shows "unknown"

1. Check communication (CAN/EtherCAT/RS485)
2. Verify EDS file is correct
3. Check drive is powered and not in boot mode
