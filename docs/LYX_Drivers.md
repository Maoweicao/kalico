# LYX stepper drivers

This document provides information on using the LYX9231 closed-loop
stepper motor driver on Kalico. The LYX9231 is a closed-loop stepper
driver with integrated encoder feedback. It accepts normal STEP/DIR
pulses from the micro-controller and is configured through a software
bit-banged Modbus RTU bus running over a single GPIO pin.

Kalico uses the micro-controller itself to bit-bang the Modbus RTU
frames (see `src/modbus_uart.c`), so no additional hardware such as a
USB-to-RS485 adapter is required.

The low-level Modbus RTU framing and the bit-bang bus driver are shared
with the [RS485 servo support](RS485.md): the `ModbusRtuProtocol` and
the `rs485_transport: mcu` transport use the exact same core
(`klippy/extras/rs485/modbus_frame.py` and
`klippy/extras/rs485/mcu_modbus.py`). LYX drivers and RS485 servo
drives may therefore share the same bus pin.

In addition to this document, be sure to review the
[LYX driver config reference](Config_Reference.md#lyx-stepper-driver-configuration).

## Overview

The LYX9231 driver behaves like a regular stepper driver for motion:
the printer sends STEP and DIR signals exactly like it would for any
other stepper. The Modbus link is used only for configuration and
diagnostics:

- Set run / hold current
- Set microstep subdivision
- Configure motor type and control mode
- Read chip status (alarm, motor speed, position error)

This means the `[lyx9231]` config section is added alongside the
regular `[stepper_x]` section and does **not** replace it.

## Hardware Requirements

### Micro-controller

Any MCU with a free GPIO pin that Kalico supports. The Modbus bus is
bit-banged in software on a single pin at 38400 baud (8N1).

### Wiring

The LYX9231 uses a half-duplex single-wire Modbus UART, so only one
GPIO pin is required:

```
MCU GPIO ──── LYX9231 communication pin
MCU GND  ──── LYX9231 GND
```

- The communication pin must be idle-high and is driven as a
  push-pull output with internal pull-up enabled.
- All drivers sharing a bus must use the **same** `uart_pin` and a
  unique `uart_address`.
- Keep the wire short (< 50cm recommended) and, for long runs, add a
  common ground wire.

## Firmware Requirements

The bit-bang Modbus UART is compiled into the micro-controller
firmware. When running `make menuconfig`, enable:

- **Support software Modbus RTU UART communication** (the
  `WANT_MODBUSUART` option)

This option is enabled by default when the selected architecture has
GPIO support, but confirm it is present in your build.

## Configuration

### Combining with a stepper

```
[stepper_x]
step_pin: PC0
dir_pin: PC1
enable_pin: !PC2
microsteps: 16
rotation_distance: 40
endstop_pin: ^PE0
position_min: 0
position_max: 200
homing_speed: 20

[lyx9231 stepper_x]
uart_pin: PB1
uart_address: 1
microstep: 16
run_current: 1.4
hold_current: 0.7
driver_motor_type: 1
driver_op_mode: 2
```

The `[lyx9231 stepper_x]` section name must match the name of the
corresponding `[stepper_x]` section.

On startup Kalico writes all configured driver registers to the chip
over the Modbus bus. After that, STEP/DIR motion is entirely handled
by the normal stepper code path.

## Configuration Reference

### [lyx9231]

Configure a LYX9231 closed-loop stepper motor driver over a software
bit-banged Modbus RTU bus.

```
[lyx9231 stepper_x]
uart_pin:
#   The GPIO pin used for the single-wire Modbus RTU bus. Required.
uart_address: 1
#   The Modbus slave address of this driver (1-247). Must be unique
#   among drivers sharing the same uart_pin. Default is 1.
sense_resistor: 0.050
#   The sense resistor value (Ohms) used to convert register values
#   to current. Default is 0.050.
run_current: 1.4
#   The driver run current in Amps. Default is 1.4.
hold_current:
#   The driver hold current in Amps. If not specified, defaults to
#   half of run_current.
microstep: 16
#   Microstep subdivision (1-256). Default is 16.
driver_motor_type: 1
#   Motor phase type: 1 for 1.8deg, 0 for 0.9deg. Default is 1.
driver_op_mode: 2
#   Control mode. 0=OpenLoop, 1=NormalClosed, 2=SuperClosed,
#   3=ServoClosed, 4=TorqueMode. Default is 2.
driver_run_current: 896
#   Raw register value of the run current register. This is normally
#   computed automatically from run_current and does not need to be
#   set. Default is 896.
driver_half_cur_en: 0
#   Enable the half current function (1=on, 0=off). Default is 0.
driver_half_cur_time: 3000
#   Delay (ms) before half current is applied. Default is 3000.
driver_half_cur_ratio: 64
#   Half current ratio register value (0-128). 64 corresponds to half
#   of the run current. Default is 64.
driver_boost_level: 1
#   Boost level for extra torque. Default is 1.
driver_noise_en: 0
#   Enable noise suppression (1=on, 0=off). Default is 0.
```

## G-Code Commands

These commands are registered per driver and are selected with
`STEPPER=<name>`, where `<name>` matches the `[lyx9231 <name>]`
section.

#### SET_LYX_CURRENT
`SET_LYX_CURRENT STEPPER=<name> [CURRENT=<amps>] [HOLDCURRENT=<amps>]`:
Adjust the run and/or hold current of the driver in Amps. With no
parameters, prints the current run/hold values.

#### SET_LYX_FIELD
`SET_LYX_FIELD STEPPER=<name> FIELD=<field> VALUE=<value>`:
Write a raw value to a single driver register field. The field name is
the lower-case register name from the register map (for example
`driver_run_current` is `run_current`).

#### SET_LYX_MICROSTEP
`SET_LYX_MICROSTEP STEPPER=<name> [MICROSTEP=<value>]`:
Change the microstep subdivision (1-256). With no parameter, prints
the current microstep setting.

#### DUMP_LYX
`DUMP_LYX STEPPER=<name>`:
Print the cached write registers and the live read registers of the
driver.

#### LYX_READ_REG
`LYX_READ_REG STEPPER=<name> REGISTER=<name>`:
Read a single Modbus register and print its raw value. Register names
follow the register map below.

#### LYX_WRITE_REG
`LYX_WRITE_REG STEPPER=<name> REGISTER=<name> VALUE=<value>`:
Write a raw value to a Modbus register and read back the value to
verify the write. If the read-back does not match, a warning is
printed.

## Register Map

The LYX9231 registers that are exposed to Kalico:

| Name | Address |
|------|---------|
| SAVE_PARAM | 0x00 |
| BAUDRATE | 0x01 |
| COMM_ADDR | 0x02 |
| CHIP_MODEL | 0x03 |
| PHASE_B_RESIST | 0x04 |
| PHASE_A_RESIST | 0x05 |
| PHASE_B_INDUCT | 0x06 |
| PHASE_A_INDUCT | 0x07 |
| ALARM_CODE | 0x08 |
| CURRENT_KP | 0x09 |
| CURRENT_KI | 0x0A |
| MOTOR_POS_H | 0x0C |
| MOTOR_POS_L | 0x0D |
| MOTOR_SPEED | 0x0E |
| ERROR_ANGLE | 0x10 |
| MS_PIN_FUNC | 0x11 |
| MOTOR_TYPE | 0x12 |
| RUN_CURRENT | 0x13 |
| HALF_CUR_TIME | 0x14 |
| HALF_CUR_RATIO | 0x15 |
| HALF_CUR_EN | 0x16 |
| DIR_POLARITY | 0x17 |
| ENA_POLARITY | 0x18 |
| MICROSTEP_RATIO | 0x19 |
| DEAD_TIME | 0x1A |
| OCL_THRESHOLD | 0x1B |
| OCL_FILTER | 0x1C |
| CUR_ANTISAT | 0x1D |
| CUR_KP_GAIN | 0x1E |
| CUR_KI_GAIN | 0x1F |
| BOOST_LEVEL | 0x20 |
| OP_MODE | 0x21 |
| STALL_ANGLE | 0x22 |
| STALL_OUT_EN | 0x23 |
| MIN_SPEED | 0x26 |
| NOISE_EN | 0x41 |

`MOTOR_SPEED` and `ERROR_ANGLE` are interpreted as signed 16-bit
values. `ALARM_CODE` values: 0=OK, 1=OverCurrent,
2=MotorDisconnected, 3=CoilAbnormal, 4=FollowError, 5=Stall.

## Troubleshooting

### Register write verification fails

Every register write is read back to verify it was applied. If a write
cannot be verified after many retries, Kalico shuts down with an error
message similar to:

```
Unable to write lyx uart 'stepper_x' register ALARM_CODE due to
transmission delay, try to reboot Klipper Service to retry
```

Check the wiring, the `uart_address` (must match the chip's address)
and the shared bus topology. Then restart Klipper.

### Modbus communication never succeeds

The firmware bit time is derived from the measured MCU clock frequency
instead of the value reported by the MCU. If the clock frequency is
not stable, the communication may never succeed. Recheck the wiring
and ensure the MCU is running at its configured frequency.

### Multiple drivers on one bus

- All drivers must use the identical `uart_pin`.
- Each `uart_address` must be unique.
