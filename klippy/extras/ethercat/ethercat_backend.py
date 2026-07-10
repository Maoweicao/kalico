# EtherCAT stepper backend for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import collections
import logging
import struct

from klippy import chelper, stepper


class PositionTracker:
    """Track commanded and actual positions over time."""

    def __init__(self, history_size=2000):
        self._history = collections.deque(maxlen=history_size)
        self._commanded_pos = 0
        self._actual_pos = 0
        self._step_dist = 1.0

    def set_step_dist(self, step_dist):
        self._step_dist = step_dist

    def update(self, clock, commanded_pos, actual_pos):
        self._commanded_pos = commanded_pos
        self._actual_pos = actual_pos
        self._history.append((clock, commanded_pos, actual_pos))

    def get_position_at(self, clock):
        if not self._history:
            return self._actual_pos
        for entry_clock, cmd, actual in reversed(self._history):
            if entry_clock <= clock:
                return actual
        return self._history[0][2] if self._history else self._actual_pos

    def get_actual_position(self):
        return self._actual_pos

    def get_commanded_position(self):
        return self._commanded_pos


class EtherCATSlaveAdapter:
    """Adapt pysoem slave to CiA402Device interface.

    CiA402Device expects:
      - node.sdo_read(index, subindex) -> int
      - node.sdo_write(index, subindex, value)
      - node.node_id
    """

    def __init__(self, slave):
        self._slave = slave
        self.node_id = slave.position

    def sdo_read(self, index, subindex=0, timeout=None):
        return self._slave.sdo_read(index, subindex)

    def sdo_write(self, index, subindex, value, timeout=None, size=None):
        self._slave.sdo_write(index, subindex, value, size or 4)


class EtherCATBackend(stepper.StepperBackend):
    """StepperBackend implementation for EtherCAT servo drives.

    Bridges the motion planner to an EtherCAT servo via pysoem.

    CL3B ESI PDO mapping (CSP mode default):
      RxPDO 1 (0x1600, Sm=2):
        - 0x6040:00 Controlword      (UINT, 16-bit)
        - 0x607A:00 Target Position  (DINT, 32-bit)
        Total: 6 bytes
      TxPDO 1 (0x1A00, Sm=3):
        - 0x603F:00 Error Code       (UINT, 16-bit)
        - 0x6041:00 Statusword       (UINT, 16-bit)
        - 0x6061:00 Mode Display     (SINT, 8-bit)
        - 0x6064:00 Actual Position  (DINT, 32-bit)
        - ... (more fields)
        First 6 bytes used: Error(2) + Status(2) + Mode(1) + ActualPos(4)

    Args:
        slave: EtherCATSlave instance
        device: CiA402Device instance (reused from canopen)
        step_dist: Distance per encoder count (mm)
        cycle_time: DC sync cycle time (seconds)
    """

    def __init__(self, slave, device, step_dist, cycle_time):
        self._slave = slave
        self._device = device
        self._step_dist = step_dist
        self._cycle_time = cycle_time
        self._stepper_kinematics = None
        self._mcu = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._last_commanded = 0
        # PDO buffers
        self._rpdo_buf = bytearray(6)   # CW(2) + TargetPos(4)
        self._tpdo_size = 6             # We read first 6 bytes of TxPDO

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)

    def set_trapq(self, trapq):
        pass  # EtherCAT doesn't use trapq

    def generate_steps(self, flush_time):
        """Get commanded position from itersolve and write to RPDO."""
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        sk = self._stepper_kinematics

        # Get commanded position from itersolve
        cmd_pos = ffi_lib.itersolve_get_commanded_pos(sk)

        # Convert to integer encoder counts
        mcu_pos = cmd_pos / self._step_dist
        if mcu_pos >= 0.0:
            target = int(mcu_pos + 0.5)
        else:
            target = int(mcu_pos - 0.5)

        # Build RPDO: [Controlword(2)] [TargetPosition(4)]
        controlword = 0x000F  # Enable operation
        struct.pack_into('<Hi', self._rpdo_buf, 0,
                         controlword, target & 0xFFFFFFFF)
        self._slave.write_output(bytes(self._rpdo_buf))

        # Read TPDO: [Error(2)] [Statusword(2)] [Mode(1)] [ActualPos(4)]
        tpdo = self._slave.read_input()
        if len(tpdo) >= self._tpdo_size:
            error_code = struct.unpack_from('<H', tpdo, 0)[0]
            statusword = struct.unpack_from('<H', tpdo, 2)[0]
            # Skip mode display (1 byte at offset 4)
            actual = struct.unpack_from('<i', tpdo, 5)[0]
            self._position_tracker.update(
                0, cmd_pos, actual * self._step_dist
            )

        self._last_commanded = target

    def set_dir_inverted(self, invert_dir):
        pass  # EtherCAT handles direction internally

    def note_homing_end(self):
        # Re-enable drive after homing
        try:
            self._device.enable()
        except Exception:
            logging.exception("EtherCAT: failed to re-enable after homing")

    def set_last_position(self, clock, position):
        """Sync itersolve position with actual encoder position."""
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        ffi_lib.itersolve_set_position(
            self._stepper_kinematics, position, 0.0, 0.0
        )

    def get_past_position(self, clock):
        return self._position_tracker.get_position_at(clock)

    def dump_steps(self, count, start_clock, end_clock):
        return None, 0  # No step/dir history for EtherCAT

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        """Return actual position from TPDO cache."""
        return self._position_tracker.get_actual_position()

    def get_status(self):
        """Return drive status for diagnostics."""
        try:
            state = self._device.get_state_name()
            actual = self._position_tracker.get_actual_position()
            error = self._device.get_error_code()
            mode = self._device.get_mode_name()
            return {
                "state": state,
                "actual_position": actual,
                "error_code": error,
                "mode": mode,
            }
        except Exception:
            return {"state": "unknown"}
