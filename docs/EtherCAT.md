# EtherCAT Servo Support

This document describes Kalico's support for EtherCAT servo drives using
the CoE (CANopen over EtherCAT) protocol with CiA 402 drive profile.
This enables using industrial EtherCAT servo motors with real-time
position control over an Ethernet network.

## Overview

EtherCAT is a high-performance industrial Ethernet protocol. Unlike
CANopen or RS485, EtherCAT frames pass through all slaves in a single
trip, achieving sub-microsecond synchronization across all axes.

Kalico uses **pysoem** (Python wrapper for SOEM - Simple Open EtherCAT
Master) as the EtherCAT master stack. The CiA 402 state machine is
reused from the CANopen module since CoE uses the same object dictionary.

Key features:
- **Cyclic Synchronous Position (CSP)** mode for real-time position control
- **Profile Position (PP)** mode for point-to-point moves
- **Distributed Clocks (DC)** for sub-microsecond multi-axis synchronization
- **Multiple slave support** on a single EtherCAT network
- **Configurable cycle time** (250µs to 20ms, default 1ms)

## Hardware Requirements

### Host Adapter

Any standard Ethernet adapter works. EtherCAT uses raw Ethernet frames,
so no special hardware is needed on the host side. However:

- **Linux**: Requires root privileges or `CAP_NET_RAW` capability
- **Windows**: Requires [Npcap](https://nmap.org/npcap/) installed
  with WinPcap API-compatible mode

### Servo Drive

Any EtherCAT servo drive that supports CoE (CANopen over EtherCAT)
with CiA 402 drive profile. Tested with:

- **Leadshine CL3B-EC series** — Closed-loop stepper drive with EtherCAT
- Other CiA 402 compliant EtherCAT drives should also work

### Network Wiring

```
Host NIC ─── CAT5/6 cable ─── Slave 0 (IN) ─── (OUT) ─── Slave 1 (IN) ─── ...
```

EtherCAT uses standard Ethernet cables (RJ45). Each slave has an IN
and OUT port. Connect the host to the first slave's IN port, then
daisy-chain from OUT to the next slave's IN.

### ESI File

Each EtherCAT slave needs an ESI (EtherCAT Slave Information) XML file.
For Leadshine CL3B drives, download from the Leadshine website. The ESI
file should be placed where SOEM can find it (typically auto-detected
from the slave's EEPROM).

## Installation

```bash
pip install pysoem
```

On Linux, ensure you run with root privileges or set capabilities:
```bash
sudo setcap cap_net_raw+ep $(which python3)
```

## Configuration

### Single Drive (CSP Mode)

```ini
[ethercat_stepper x]
ethercat_interface: eth0
ethercat_slave: 0
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### Multi-Axis Cascade

```ini
[ethercat_stepper x]
ethercat_interface: eth0
ethercat_slave: 0
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200

[ethercat_stepper y]
ethercat_interface: eth0
ethercat_slave: 1
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200

[ethercat_stepper z]
ethercat_interface: eth0
ethercat_slave: 2
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

## Configuration Reference

### [ethercat_stepper]

```
[ethercat_stepper x]
ethercat_interface:
#   Network interface name. Linux: eth0, enp3s0, etc.
#   Windows: Npcap device name. Required.
ethercat_slave: 0
#   Slave position index (0 = first slave). Default is 0.
#canopen_mode: CSP
#   Operating mode. Options: CSP (Cyclic Synchronous Position),
#   PP (Profile Position), CSV (Cyclic Synchronous Velocity),
#   HOMING. Default is CSP.
#ethercat_cycle_time: 0.001
#   DC sync cycle time in seconds. Range: 0.000250 to 0.020.
#   Default is 0.001 (1ms).
rotation_distance:
#   Distance (mm) per full rotation. Required.
microsteps:
#   Set to 1 for EtherCAT servos (required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation. Default is 200.
#endstop_pin:
#   Endstop pin for traditional homing. Required for homing.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum position in mm. Default is 0.
#position_max:
#   Maximum position in mm. Required if endstop_pin is set.
```

## CL3B EtherCAT Register Map

Leadshine CL3B-EC series default PDO mapping for CSP mode:

### RxPDO 1 (Master → Slave, 6 bytes)

| Object | SubIndex | Type | Bits | Description |
|--------|----------|------|------|-------------|
| 0x6040 | 0x00 | UINT | 16 | Controlword |
| 0x607A | 0x00 | DINT | 32 | Target Position |

### TxPDO 1 (Slave → Master, ~15 bytes)

| Object | SubIndex | Type | Bits | Description |
|--------|----------|------|------|-------------|
| 0x603F | 0x00 | UINT | 16 | Error Code |
| 0x6041 | 0x00 | UINT | 16 | Statusword |
| 0x6061 | 0x00 | SINT | 8 | Mode of Operation Display |
| 0x6064 | 0x00 | DINT | 32 | Position Actual Value |
| 0x60B9 | 0x00 | UINT | 16 | Touch Probe Status |
| 0x60BA | 0x00 | DINT | 32 | Touch Probe 1 Positive Value |
| 0x60FD | 0x00 | UDINT | 32 | Digital Inputs |

### CiA 402 Controlword (0x6040) Transitions

| Transition | Controlword | Statusword | Description |
|------------|-------------|------------|-------------|
| Power On → Ready | Auto | 0x0250 | Automatic |
| Ready → Switch On Disabled | 0x0000 | 0x0250 | Shutdown |
| Switch On Disabled → Ready | 0x0006 | 0x0231 | Shutdown |
| Ready → Waiting Enable | 0x0007 | 0x0233 | Switch On |
| Waiting Enable → Enabled | 0x000F | 0x0237 | Enable Operation |
| Fault → Ready | 0x0080 | 0x0250 | Fault Reset |

### Supported Operating Modes (0x6060)

| Value | Mode | Description |
|-------|------|-------------|
| 1 | PP | Profile Position |
| 3 | PV | Profile Velocity |
| 6 | HM | Homing Mode |
| 8 | CSP | Cyclic Synchronous Position |

## Distributed Clocks (DC)

EtherCAT DC provides sub-microsecond synchronization across all slaves.
The CL3B supports DC with the following configuration:

- AssignActivate: `#x0300`
- CycleTimeSync0: Configurable (default 1ms)
- ShiftTimeSync0: 0

DC is automatically enabled when `ethercat_cycle_time` is set. All
slaves on the same network share the same DC reference clock.

## Data Flow

```
Toolhead → generate_steps() → itersolve_get_commanded_pos()
  → EtherCATBackend
      ├─ Build RPDO: [Controlword(2)] [TargetPosition(4)]
      ├─ slave.write_output(rpdo_data)
      ├─ slave.read_input() → TPDO
      └─ Parse TPDO: [Error(2)] [Statusword(2)] [Mode(1)] [ActualPos(4)]
          → PositionTracker
```

The PDO exchange happens via `master.exchange_processdata()` which is
called by the DC sync timer at the configured cycle time.

## Troubleshooting

### No slaves found

1. Check network cable connection
2. Verify the interface name is correct (`ip addr` on Linux)
3. Ensure you have root privileges (Linux) or Npcap installed (Windows)
4. Check that slaves are powered on

### Slave fails to reach OP state

1. Check the ESI file matches your drive model
2. Verify the drive is not in fault state
3. Check DC sync configuration
4. Look at the RUN and ERR LEDs on the drive

### Position drift

1. Verify encoder is working correctly
2. Check that `rotation_distance` matches your mechanics
3. Ensure the drive is in CSP mode (0x6060 = 8)

### Communication timeout

1. Check cable quality and length (max 100m per segment)
2. Reduce cycle time if too many slaves on the bus
3. Check for network interference
