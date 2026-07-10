# Industrial Safety Monitoring

Kalico provides comprehensive industrial-grade safety monitoring features for servo drive systems.

## Overview

| Module | Function | Status |
|--------|----------|--------|
| `[safety_monitor]` | Following error, velocity, torque monitoring | ✅ |
| `[emergency_stop]` | Hardware E-Stop button | ✅ |
| `[safety_door]` | Safety door interlock | ✅ |
| `[servo_alarm]` | Servo ALM pin monitoring | ✅ |
| `[production_counter]` | Production counting, maintenance | ✅ |
| `[alarm_history]` | Alarm history persistence | ✅ |

## Quick Start

```ini
# Safety monitoring
[safety_monitor]
deviation_threshold: 1.0
deviation_action: shutdown
max_velocity: 5000
velocity_action: shutdown
max_torque: 300
torque_action: pause
steppers: canopen_stepper stepper_x, canopen_stepper stepper_y

# Emergency stop
[emergency_stop]
estop_pin: ^PA0

# Safety door
[safety_door]
door_pin: ^PA1
door_action: pause

# Servo ALM pins
[servo_alarm x_axis]
alm_pin: PB7
action: shutdown

# Production counter
[production_counter]
maintenance_interval: 1000
data_file: ~/production_data.json

# Alarm history
[alarm_history]
history_file: ~/alarm_history.json
max_entries: 1000
log_to_text: true
text_log_file: ~/alarm_log.txt
```

## Modules

### [safety_monitor]

Monitors following error, velocity, and torque for servo drives.

| Option | Default | Description |
|--------|---------|-------------|
| `deviation_threshold` | 0.0 | Following error threshold (encoder counts) |
| `deviation_action` | shutdown | Action: shutdown/pause/gcode/none |
| `deviation_debounce` | 0.05 | Debounce time (seconds) |
| `max_velocity` | 0.0 | Max velocity (encoder counts/s) |
| `velocity_action` | shutdown | Action on velocity exceeded |
| `velocity_debounce` | 0.05 | Debounce time (seconds) |
| `max_torque` | 0.0 | Max torque (% rated) |
| `torque_action` | shutdown | Action on torque exceeded |
| `torque_debounce` | 0.1 | Debounce time (seconds) |
| `steppers` | | Comma-separated stepper list |

### [emergency_stop]

Hardware emergency stop button support.

| Option | Default | Description |
|--------|---------|-------------|
| `estop_pin` | Required | E-Stop button GPIO pin |
| `estop_invert` | false | Invert pin logic |
| `estop_debounce` | 0.01 | Debounce time (seconds) |

### [safety_door]

Safety door interlock with configurable actions.

| Option | Default | Description |
|--------|---------|-------------|
| `door_pin` | Required | Door sensor GPIO pin |
| `door_invert` | false | Invert pin logic |
| `door_debounce` | 0.01 | Debounce time (seconds) |
| `door_action` | shutdown | Action: shutdown/pause/none |
| `allow_print_with_door_open` | false | Allow printing with door open |

### [production_counter]

Production counting and maintenance reminders.

| Option | Default | Description |
|--------|---------|-------------|
| `count_on_complete` | true | Count on print complete |
| `maintenance_interval` | 1000 | Prints between maintenance |
| `maintenance_hours` | 500 | Hours between maintenance |
| `data_file` | ~/production_data.json | Data persistence file |

### [alarm_history]

Persistent alarm history with JSON and text log support.

| Option | Default | Description |
|--------|---------|-------------|
| `history_file` | ~/alarm_history.json | JSON history file |
| `max_entries` | 1000 | Maximum history entries |
| `log_to_text` | true | Also write text log |
| `text_log_file` | ~/alarm_log.txt | Text log file |

## G-code Commands

### Safety Monitor

| Command | Description |
|---------|-------------|
| `QUERY_SAFETY_STATUS` | Query safety monitor status |
| `SET_SAFETY_LIMIT [DEVIATION=<v>] [VELOCITY=<v>] [TORQUE=<v>]` | Set limits at runtime |

### Emergency Stop

| Command | Description |
|---------|-------------|
| `QUERY_EMERGENCY_STOP` | Query E-Stop status |

### Safety Door

| Command | Description |
|---------|-------------|
| `QUERY_SAFETY_DOOR` | Query door status |
| `ARM_SAFETY_DOOR` | Arm door monitoring |
| `DISARM_SAFETY_DOOR` | Disarm door monitoring |

### Production Counter

| Command | Description |
|---------|-------------|
| `QUERY_PRODUCTION` | Query production statistics |
| `RESET_PRODUCTION [TOTAL]` | Reset counters |
| `MARK_MAINTENANCE` | Mark maintenance performed |

### Alarm History

| Command | Description |
|---------|-------------|
| `QUERY_ALARM_HISTORY [COUNT=<n>]` | Query alarm history |
| `CLEAR_ALARM_HISTORY` | Clear history |
| `ACKNOWLEDGE_ALARM ID=<n>` | Acknowledge alarm |

### Summary

| Command | Description |
|---------|-------------|
| `QUERY_ALL_SAFETY` | Query all safety status |

## Status Fields

### safety_monitor

| Field | Type | Description |
|-------|------|-------------|
| `deviation_alarm` | bool | Following error alarm active |
| `deviation_value` | float | Current following error |
| `deviation_threshold` | float | Configured threshold |
| `velocity_alarm` | bool | Velocity alarm active |
| `velocity_value` | float | Current velocity |
| `velocity_threshold` | float | Configured threshold |
| `torque_alarm` | bool | Torque alarm active |
| `torque_value` | float | Current torque |
| `torque_threshold` | float | Configured threshold |

### emergency_stop

| Field | Type | Description |
|-------|------|-------------|
| `triggered` | bool | E-Stop currently triggered |
| `trigger_count` | int | Trigger count since startup |
| `pin` | str | Configured pin |

### safety_door

| Field | Type | Description |
|-------|------|-------------|
| `door_open` | bool | Door currently open |
| `open_count` | int | Open count since startup |
| `armed` | bool | Monitoring armed |
| `pin` | str | Configured pin |
| `action` | str | Configured action |

### production_counter

| Field | Type | Description |
|-------|------|-------------|
| `total_prints` | int | Total completed prints |
| `session_prints` | int | Prints this session |
| `total_runtime_hours` | float | Total runtime hours |
| `prints_since_maintenance` | int | Prints since last maintenance |
| `maintenance_due` | bool | Maintenance reminder active |

### alarm_history

| Field | Type | Description |
|-------|------|-------------|
| `total_alarms` | int | Total alarm count |
| `unacknowledged` | int | Unacknowledged alarms |
| `recent_alarms` | list | Last 5 alarms |

## IEC 61800-5-2 Safety Functions

> **Note**: The following safety functions require drive hardware safety modules.
> Pure software cannot achieve compliant safety integrity levels (SIL).

| Function | Description | Requirement |
|----------|-------------|-------------|
| STO | Safe Torque Off | Drive STO input terminal |
| SS1/SS2 | Safe Stop | Drive safety stop function |
| SLS | Safely Limited Speed | Drive safety speed monitoring |
| SBC | Safe Brake Control | Drive safety brake output |
| SDI | Safe Direction | Drive safety direction |
| SLP | Safe Limited Position | Drive safety position limit |

For industrial applications requiring these functions, use external safety PLCs or safety relays.

## Events

The following events are fired for integration:

| Event | Source | Details |
|-------|--------|---------|
| `servo_alarm:triggered` | servo_alarm | Alarm pin triggered |
| `safety_monitor:alarm` | safety_monitor | Safety limit exceeded |
| `emergency_stop:triggered` | emergency_stop | E-Stop pressed |
| `safety_door:opened` | safety_door | Door opened |
| `production_counter:print_completed` | production_counter | Print completed |
| `production_counter:maintenance_due` | production_counter | Maintenance due |
| `alarm_history:recorded` | alarm_history | Alarm recorded |
