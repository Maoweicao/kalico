# Additional Kinematics

This document describes the additional kinematics modules added to Kalico beyond the standard Klipper kinematics.

## Supported Kinematics

| Kinematics | Config Name | Description |
|------------|-------------|-------------|
| SCARA | `scara` | Selective Compliance Assembly Robot Arm |
| TPARA | `tpara` | Three Parallel Axis Rotary Arm |
| Polargraph | `polargraph` | Cable-driven wall plotter |
| Belt Printer | `belt` | Infinite Z-axis conveyor belt |
| Robot Arm | `robot_arm` | Multi-joint articulated arm |
| Foam Cutter | `foam_cutter` | XYUV hot wire cutter |
| CoreYX | `coreyx` | Reversed CoreXY |
| CoreYZ | `coreyz` | YZ-axis coupled |
| CoreZX | `corezx` | ZX-axis coupled |
| CoreZY | `corezy` | ZY-axis coupled |

## SCARA Kinematics

SCARA (Selective Compliance Assembly Robot Arm) is a common industrial robot arm configuration.

### Configuration

```
[printer]
kinematics: scara

[scara]
linkage_1: 150
#   Length of inner arm in mm. This parameter must be provided.
linkage_2: 150
#   Length of outer arm in mm. This parameter must be provided.
offset_x: 100
#   X offset of tower from bed center in mm. Default is 0.
offset_y: -56
#   Y offset of tower from bed center in mm. Default is 0.
segments_per_second: 200
#   Number of segments per second for curved moves. Default is 200.
variant: morgan
#   SCARA variant: "morgan" or "mp". Default is "morgan".
print_radius: 250
#   Maximum print radius in mm. Default is linkage_1 + linkage_2.
home_x: 100
#   Home X position in mm. Default is 0.
home_y: 100
#   Home Y position in mm. Default is 0.
home_z: 0
#   Home Z position in mm. Default is 0.
max_z: 300
#   Maximum Z height in mm. Default is 300.
```

### Stepper Configuration

```
[stepper_a]
# Shoulder motor (rotational)
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
#   360 degrees per full rotation
microsteps: 16

[stepper_b]
# Elbow motor (rotational)
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_z]
# Z axis (linear)
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 300
microsteps: 16
```

### Variants

- **Morgan SCARA**: Uses Cartesian XY home position
- **MP SCARA**: Uses arm angles for AB home position

## TPARA Kinematics

TPARA (Three Parallel Axis Rotary Arm) is a 3-axis robotic arm with three parallel rotation axes.

### Configuration

```
[printer]
kinematics: tpara

[tpara]
linkage_1: 120
#   Length of inner arm in mm. This parameter must be provided.
linkage_2: 120
#   Length of outer arm in mm. This parameter must be provided.
offset_x: 0
#   X offset in mm. Default is 0.
offset_y: 0
#   Y offset in mm. Default is 0.
offset_z: 0
#   Z offset in mm. Default is 0.
segments_per_second: 200
#   Number of segments per second. Default is 200.
print_radius: 200
#   Maximum print radius in mm. Default is linkage_1 + linkage_2.
max_z: 300
#   Maximum Z height in mm. Default is 300.
```

### Stepper Configuration

```
[stepper_a]
# Base rotation
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
microsteps: 16

[stepper_b]
# Shoulder rotation
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_c]
# Elbow rotation
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
rotation_distance: 360
microsteps: 16
```

## Polargraph Kinematics

Polargraph (also known as wall plotter or cable-driven plotter) uses two motors mounted at the top corners to control a pen/gripper via strings/cables.

### Configuration

```
[printer]
kinematics: polargraph

[polargraph]
motor_distance_x: 1000.0
#   Distance between the two motor centers in mm. This parameter
#   must be provided.
motor_offset_y: 50.0
#   Y offset from motor center to home position in mm. Default is 0.
max_belt_length: 1200.0
#   Maximum belt/cable length in mm. Default is motor_distance_x * 1.2.
segments_per_second: 5
#   Number of segments per second. Default is 5.
```

### Stepper Configuration

```
[stepper_left]
# Left motor
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 40
microsteps: 16

[stepper_right]
# Right motor
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 40
microsteps: 16

[stepper_z]
# Optional Z axis for pen lift
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 100
microsteps: 16
```

## Belt Printer Kinematics

Belt printers have an infinite Z axis (conveyor belt bed) and are typically tilted at 45 degrees.

### Configuration

```
[printer]
kinematics: belt

[belt]
bed_tilt: 45.0
#   Bed tilt angle in degrees. Default is 45.
bed_rotation_axis: y
#   Bed rotation axis: "x" or "y". Default is "y".
segments_per_second: 10
#   Number of segments per second. Default is 10.
```

### Stepper Configuration

```
[stepper_x]
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
position_endstop: 0
position_max: 200

[stepper_y]
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
position_endstop: 0
position_max: 200

[stepper_z]
# Conveyor belt motor
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 200
```

## Robot Arm Kinematics

Articulated robot arm with multiple rotational joints.

### Configuration

```
[printer]
kinematics: robot_arm

[robot_arm]
d1: 100
#   Base height in mm. Default is 100.
a1: 50
#   Link 1 length in mm. Default is 50.
a2: 200
#   Link 2 length in mm. Default is 200.
a3: 150
#   Link 3 length in mm. Default is 150.
segments_per_second: 100
#   Number of segments per second. Default is 100.
```

### Stepper Configuration

```
[stepper_a]
# Base rotation
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
rotation_distance: 360
microsteps: 16

[stepper_b]
# Shoulder rotation
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
rotation_distance: 360
microsteps: 16

[stepper_c]
# Elbow rotation
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
rotation_distance: 360
microsteps: 16
```

## Foam Cutter Kinematics

Foam cutters use a hot wire to cut foam, typically with 4 axes: X, Y (wire top) and U, V (wire bottom).

### Configuration

```
[printer]
kinematics: foam_cutter

[foam_cutter]
wire_length: 500.0
#   Wire length in mm. This parameter must be provided.
segments_per_second: 10
#   Number of segments per second. Default is 10.
```

### Stepper Configuration

```
[stepper_x]
# Wire top X
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
position_endstop: 0
position_max: 500

[stepper_y]
# Wire top Y
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
position_endstop: 0
position_max: 500

[stepper_u]
# Wire bottom X
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 500

[stepper_v]
# Wire bottom Y
step_pin: PD0
dir_pin: PD1
endstop_pin: PD2
position_endstop: 0
position_max: 500
```

## Core Variants

These are variations of the standard CoreXY kinematics with different axis couplings.

### CoreYX

Reversed CoreXY - Y moves independently, X and Z are coupled.

```
[printer]
kinematics: coreyx
```

### CoreYZ

X moves independently, Y and Z are coupled.

```
[printer]
kinematics: coreyz
```

### CoreZX

Y moves independently, Z and X are coupled.

```
[printer]
kinematics: corezx
```

### CoreZY

Z moves independently, X and Y are coupled.

```
[printer]
kinematics: corezy
```

## Notes

- All rotational axes use `rotation_distance: 360` for 360 degrees per full rotation
- SCARA and TPARA require careful calibration of arm lengths
- Polargraph requires accurate motor distance measurement
- Belt printers need proper bed tilt angle configuration
- Foam cutters must have wire length properly configured

## See Also

- [Kinematics Overview](Kinematics.md)
- [Configuration Reference](Config_Reference.md)
- [G-code Commands](G-Codes.md)
