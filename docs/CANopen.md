# CANopen Servo Support

This document describes Kalico's support for CANopen CiA 402 servo
drives. CANopen allows using industrial servo motors with position
feedback directly over a CAN bus, without step/dir pulse signaling.

## Overview

CANopen is a higher-level protocol built on top of CAN bus (CiA 301).
Unlike Kalico's native CAN protocol (which uses CAN as a transport for
MCU step/dir commands), CANopen sends position setpoints directly to
intelligent servo drives. The drives handle their own trajectory
generation, current control, and encoder feedback.

Key features:
- **Cyclic Synchronous Position (CSP)** mode for real-time position control
- **Cyclic Synchronous Velocity (CSV)** mode for speed control
- **Profile Position (PP)** mode for point-to-point moves
- **CiA 402 homing** with 11 homing methods (limit switch, home switch, index)
- **EDS/DCF device description** file support (INI format per CiA 306)
- **SYNC groups** for synchronized multi-axis motion

## Hardware Requirements

### CAN Bus Interface

You need a CAN bus adapter connected to your host computer. See the
[CANBUS](CANBUS.md) document for information on host-side CAN
hardware and OS configuration.

### Servo Drive

Any CANopen CiA 402 compliant servo drive should work. Common drives:
- **EtherCAT/CANopen dual-mode drives** (e.g., Leadshine, Estun, Delta)
- **CANopen servo drives** from various manufacturers
- **BLDC/PMSM drives** with CiA 402 support

The drive must support at least one of these operating modes:
- **CSP (Cyclic Synchronous Position)** — Recommended for CNC/3D printing
- **CSV (Cyclic Synchronous Velocity)** — Alternative for speed control
- **PP (Profile Position)** — Uses drive's internal trajectory generator

### EDS/DCF File

Each drive needs an EDS (Electronic Data Sheet) or DCF (Device
Configuration File) in INI format. This file describes the drive's
object dictionary, supported modes, and default parameters. The file
is typically provided by the drive manufacturer.

Supported file formats:
- `.eds` — Standard Electronic Data Sheet (CiA 306 INI format)
- `.dcf` — Device Configuration File (same format, with device-specific values)

## Configuration

### Basic Single-Axis Setup

```ini
[canopen_stepper x]
can_interface: socketcan
can_channel: can0
can_bitrate: 1000000
node_id: 1
eds_file: ~/servo_configs/servo_x.eds
canopen_mode: CSP
sync_group: default
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### Multi-Axis with Shared Bus

When multiple servos share the same CAN bus, use a `[canopen_bus]`
section to avoid repeating bus parameters:

```ini
[canopen_bus main]
interface: socketcan
channel: can0
bitrate: 1000000

[canopen_stepper x]
canopen_bus: main
node_id: 1
eds_file: ~/configs/servo_x.eds
canopen_mode: CSP
sync_group: xy_group
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200

[canopen_stepper y]
canopen_bus: main
node_id: 2
eds_file: ~/configs/servo_y.eds
canopen_mode: CSP
sync_group: xy_group
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200

[canopen_stepper z]
canopen_bus: main
node_id: 3
eds_file: ~/configs/servo_z.eds
canopen_mode: CSP
sync_group: z_group
sync_period: 0.002
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

### CiA 402 Homing (Servo Internal Homing)

Instead of using a physical endstop connected to an MCU GPIO pin, you
can use the servo drive's built-in CiA 402 homing mode:

```ini
[canopen_stepper z]
canopen_bus: main
node_id: 3
eds_file: ~/configs/servo_z.eds
canopen_mode: CSP
sync_group: z_group
sync_period: 0.001
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: canopen
canopen_homing_method: negative_limit
canopen_homing_speed_switch: 1000
canopen_homing_speed_zero: 500
canopen_homing_accel: 5000
canopen_homing_offset: 100
homing_speed: 5.0
position_min: 0
position_max: 300
```

## Configuration Reference

### [canopen_bus]

Shared CAN bus parameters for multiple CANopen steppers.

```
[canopen_bus my_bus]
interface: socketcan
#   CAN interface type. Required. Typical values: "socketcan" (Linux),
#   "slcan" (serial-line CAN), "pcan" (PEAK).
channel: can0
#   CAN channel name. Required. For socketcan this is the network
#   interface name (e.g., "can0"). For slcan this is the serial port
#   (e.g., "/dev/ttyACM0").
#bitrate: 1000000
#   CAN bus bitrate in bps. Default is 1000000 (1 Mbit/s).
```

### [canopen_stepper]

CANopen servo stepper motor configuration.

```
[canopen_stepper x]
#canopen_bus:
#   Reference to a [canopen_bus] section. If not specified, you must
#   provide can_interface, can_channel, and can_bitrate directly.
#can_interface:
#can_channel:
#can_bitrate: 1000000
#   Direct bus configuration (alternative to canopen_bus).
node_id:
#   CANopen node ID (1-127). Required.
eds_file:
#   Path to the EDS/DCF file for this device. Required. Supports ~/
#   for home directory. Relative paths are resolved from the config
#   file directory.
#canopen_mode: CSP
#   Operating mode. Options: CSP (Cyclic Synchronous Position),
#   CSV (Cyclic Synchronous Velocity), PP (Profile Position),
#   PV (Profile Velocity), CST (Cyclic Synchronous Torque).
#   Default is CSP.
#sync_group: default
#   SYNC group name. Steppers with the same sync_group share the same
#   CANopen SYNC signal and are synchronized in their PDO exchange.
#   Default is "default".
#sync_period: 0.001
#   SYNC period in seconds (0.000250 to 0.010). This controls how
#   often position setpoints are sent to the drive. Default is 0.001
#   (1ms, 1kHz).
rotation_distance:
#   Distance (in mm) that the axis travels with one full rotation of
#   the servo motor. This parameter must be provided.
microsteps:
#   Set to 1 for CANopen servos (not used, but required by framework).
full_steps_per_rotation: 200
#   Encoder counts per rotation or motor pole count. Default is 200.
#endstop_pin:
#   Endstop pin. Set to "canopen" to use CiA 402 internal homing, or
#   specify a GPIO pin for traditional endstop. Required for homing.
#canopen_homing_method: negative_limit
#   CiA 402 homing method (only used when endstop_pin is "canopen").
#   Options: current_position, positive_limit, negative_limit,
#   positive_home, negative_home, positive_home_index,
#   negative_home_index, negative_limit_index, positive_limit_index,
#   index_positive, index_negative. Can also be a number (1-35).
#   Default is "negative_limit".
#canopen_homing_speed_switch:
#   Speed for switch search in encoder counts/s. If not specified,
#   uses the drive's default.
#canopen_homing_speed_zero:
#   Speed for zero search in encoder counts/s. If not specified,
#   uses the drive's default.
#canopen_homing_accel:
#   Homing acceleration in encoder counts/s^2. If not specified,
#   uses the drive's default.
#canopen_homing_offset: 0
#   Home offset in encoder counts. Default is 0.
#max_velocity:
#   Maximum velocity in mm/s. Optional, overrides drive limits.
#max_accel:
#   Maximum acceleration in mm/s^2. Optional, overrides drive limits.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum valid position in mm. Default is 0.
#position_max:
#   Maximum valid position in mm. Required if position_endstop is set.
```

## SYNC Groups

SYNC groups control how multiple CANopen nodes are synchronized. All
nodes in the same SYNC group share the same SYNC frame timing, which
means their position setpoints are updated at the same instant.

```
[canopen_stepper x]
sync_group: xy_group    # Same group = synchronized
sync_period: 0.001

[canopen_stepper y]
sync_group: xy_group    # Shares SYNC with x axis
sync_period: 0.001      # Period must match within group

[canopen_stepper z]
sync_group: z_group     # Independent SYNC
sync_period: 0.002      # Can have different period
```

The first stepper registered in a SYNC group becomes the SYNC
producer. All other steppers in the group are consumers.

## CiA 402 Homing Methods

When using `endstop_pin: canopen`, the following homing methods are
available:

| Method | Number | Description |
|--------|--------|-------------|
| `current_position` | 35 | Use current position as home |
| `positive_limit` | 17 | Positive limit switch |
| `negative_limit` | 18 | Negative limit switch |
| `positive_home` | 1 | Positive home switch |
| `negative_home` | 2 | Negative home switch |
| `positive_home_index` | 11 | Positive home switch + index pulse |
| `negative_home_index` | 12 | Negative home switch + index pulse |
| `negative_limit_index` | 23 | Negative limit switch + index pulse |
| `positive_limit_index` | 27 | Positive limit switch + index pulse |
| `index_positive` | 33 | Index pulse, positive direction |
| `index_negative` | 34 | Index pulse, negative direction |

The exact behavior depends on your servo drive's implementation of
CiA 402 homing. Refer to your drive's manual for details on each
method.

## EDS File Format

EDS (Electronic Data Sheet) files use INI format per CiA 306. A
typical EDS file contains:

```ini
[DeviceInfo]
VendorName=MyServo
VendorNumber=0x12345678
ProductName=ServoX
ProductCode=0x00010001

[Objects]
1000=1
1018=4
6040=1
6041=1
6060=1
607A=1
6064=1

[1000]
ParameterName=Device Type
ObjectType=7
DataType=0x0007
AccessType=ro
DefaultValue=0x00020192

[6040]
ParameterName=Controlword
ObjectType=7
DataType=0x0006
AccessType=rw
DefaultValue=0x0000
PDOMapping=1
```

Key objects that must be present:
- `0x1000` — Device Type
- `0x1018` — Identity Object (Vendor ID, Product Code)
- `0x6040` — Controlword
- `0x6041` — Statusword
- `0x6060` — Modes of Operation
- `0x607A` — Target Position (for CSP mode)
- `0x6064` — Position Actual Value
- `0x1600` — RPDO 1 Mapping
- `0x1A00` — TPDO 1 Mapping

## Troubleshooting

### Drive not enabling

Check that:
1. The EDS file matches your drive model
2. The node_id matches the drive's configured ID
3. The CAN bus bitrate matches the drive's configuration
4. The drive is powered and not in fault state

### Homing fails

For CiA 402 homing:
1. Verify `canopen_homing_method` matches your hardware setup
2. Check that homing speeds are within the drive's limits
3. Ensure the drive supports the selected homing method (check EDS)

### Position drift

If the actual position drifts from the commanded position:
1. Check that the drive is in the correct operating mode (CSP)
2. Verify the encoder is working correctly
3. Check for CAN bus errors (retries, lost frames)

### CAN bus errors

If you see CAN bus errors:
1. Check terminating resistors (two 120 ohm resistors at bus ends)
2. Verify bus length is within specification
3. Check for proper grounding
4. Reduce bus speed if using long cables
