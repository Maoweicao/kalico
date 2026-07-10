# External Pulse Generator Support

This document describes Kalico's support for external pulse generator
modules. These are devices that accept position/velocity commands via
RS485/SPI/UART and generate their own high-speed differential step/dir
pulses internally.

## Overview

External pulse generator modules are useful when:
- You need higher pulse rates than MCU GPIO can provide (10MHz+)
- You need differential signaling (RS-422/LVDS) for long cable runs
- You want the pulse generator to handle acceleration/deceleration
- Your drive only accepts step/dir but you want bus-based control

Kalico supports three command modes:
- **Absolute position** — Send absolute position setpoints (like CSP)
- **Relative displacement** — Send relative pulse counts
- **Velocity** — Send velocity commands

Communication uses the RS485 transport and protocol layers (Modbus RTU,
UART passthrough, or custom protocols).

## Hardware Requirements

### Pulse Generator Module

Any external module that accepts position/velocity commands and outputs
step/dir pulses. Examples:
- Leadshine DMC series (Digital Motion Controller)
- External motion controllers with RS485/UART interface
- Custom pulse generator boards

### Communication Interface

USB-to-RS485 adapter (same as RS485 servo drives). See the
[RS485 guide](RS485.md) for adapter recommendations.

## Configuration

### Absolute Position Mode

```ini
[pulse_gen_stepper x]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 1
pulse_gen_mode: absolute
register_target_position: 0x607A
register_actual_position: 0x6064
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### Relative Displacement Mode

```ini
[pulse_gen_stepper y]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 2
pulse_gen_mode: relative
register_relative_position: 0x0020
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200
```

### Velocity Mode

```ini
[pulse_gen_stepper z]
serial_port: /dev/ttyUSB0
baud_rate: 9600
pulse_gen_protocol: modbus_rtu
pulse_gen_slave_id: 3
pulse_gen_mode: velocity
register_velocity: 0x0030
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

## Configuration Reference

### [pulse_gen_stepper]

```
[pulse_gen_stepper x]
serial_port:
#   Serial port path. Required.
#baud_rate: 9600
#   Baud rate. Range: 1200 to 115200. Default is 9600.
#pulse_gen_protocol: modbus_rtu
#   Protocol type. Options: modbus_rtu, uart_passthrough, custom.
#   Default is modbus_rtu.
#pulse_gen_slave_id: 1
#   Slave address (1-247). Default is 1.
#pulse_gen_mode: absolute
#   Command mode. Options: absolute, relative, velocity.
#   Default is absolute.
#register_target_position: 0x607A
#   Register address for target position (absolute mode).
#   Default is 0x607A.
#register_actual_position: 0x6064
#   Register address for actual position feedback.
#   Set to 0 for open-loop operation (no encoder).
#   Default is 0x6064.
#register_relative_position: 0x0020
#   Register address for relative displacement (relative mode).
#   Default is 0x0020.
#register_velocity: 0x0030
#   Register address for velocity command (velocity mode).
#   Default is 0x0030.
#rs485_parity: N
#   Parity. Options: N, E, O. Default is N.
#rs485_stopbits: 1
#   Stop bits. Default is 1.
#rs485_bytesize: 8
#   Data bits. Default is 8.
#rs485_direction_pin: rts
#   DE/RE control method. Default is "rts".
#protocol_class:
#   Python class path for custom protocol (when pulse_gen_protocol
#   is "custom"). Format: module.ClassName
rotation_distance:
#   Distance (mm) per full rotation. Required.
microsteps:
#   Set to 1 for pulse generators (required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation. Default is 200.
#endstop_pin:
#   Endstop pin for homing. Required for homing.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum position in mm. Default is 0.
#position_max:
#   Maximum position in mm. Required if endstop_pin is set.
```

## Command Mode Details

### Absolute Mode

Each `generate_steps` call sends the absolute target position to the
pulse generator. The generator's internal trajectory planner handles
acceleration, deceleration, and pulse generation.

```
itersolve → target_pos → protocol.set_target_position(target)
                              │
                              └─ Generator internally:
                                   ├─ Trajectory planning
                                   ├─ Acceleration/deceleration
                                   └─ Differential pulse output
```

### Relative Mode

Each `generate_steps` call sends the delta (displacement) since the
last call. Suitable for open-loop pulse generators without encoders.

```
itersolve → target_pos → delta = target - last_target
                              │
                              ├─ if delta != 0:
                              │    protocol.write_register(RELATIVE, delta)
                              │
                              └─ last_target = target
```

### Velocity Mode

Each `generate_steps` call calculates the velocity from position
change over time and sends it to the generator.

```
itersolve → target_pos → velocity = (target - last) / dt
                              │
                              └─ protocol.write_register(VELOCITY, velocity)
```

## Open-Loop vs Closed-Loop

If the pulse generator has an encoder, set `register_actual_position`
to the encoder feedback register address. The position tracker will
use the actual encoder position.

If there's no encoder (open-loop), set `register_actual_position: 0`.
The position tracker will use the commanded position, which is less
accurate but sufficient for most applications.

## Writing Custom Protocols

See the [RS485 guide](RS485.md#writing-custom-protocols) for
instructions on writing custom protocol adapters. The same
`RS485Protocol` base class is used.

## Troubleshooting

### No response from pulse generator

1. Check wiring and serial port
2. Verify baud rate and slave ID match
3. Ensure the protocol type is correct

### Position drift (open-loop)

This is expected with open-loop operation. The commanded position
may differ from the actual mechanical position due to:
- Missed pulses at high speeds
- Mechanical backlash
- Motor stall

For accurate positioning, use a closed-loop drive with encoder.

### Communication delay

RS485/Modbus has inherent latency (2-20ms). At high speeds, this
may cause the position tracking to lag behind. Consider:
- Using a higher baud rate
- Reducing the number of slaves on the bus
- Using absolute mode (the generator handles timing internally)
