# RS485 stepper backend for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import collections
import logging

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


class RS485Backend(stepper.StepperBackend):
    """StepperBackend implementation for RS485 servo drives.

    Bridges the motion planner to an RS485 servo via a protocol adapter.

    Args:
        protocol: RS485Protocol instance
        step_dist: Distance per encoder count (mm)
    """

    def __init__(self, protocol, step_dist):
        self._protocol = protocol
        self._step_dist = step_dist
        self._stepper_kinematics = None
        self._mcu = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._last_commanded = 0

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu
        try:
            self._protocol.open()
            logging.info(
                "RS485: protocol opened for slave %d",
                self._protocol.get_slave_id(),
            )
        except Exception as e:
            logging.error("RS485: failed to open protocol: %s", e)

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)

    def set_trapq(self, trapq):
        pass  # RS485 doesn't use trapq

    def generate_steps(self, flush_time):
        """Get commanded position from itersolve and send via RS485."""
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

        # Send target position via protocol
        try:
            self._protocol.set_target_position(target)
            actual = self._protocol.get_actual_position()
            self._position_tracker.update(
                0, cmd_pos, actual * self._step_dist
            )
        except Exception as e:
            logging.warning("RS485 communication error: %s", e)

        self._last_commanded = target

    def set_dir_inverted(self, invert_dir):
        pass  # RS485 handles direction internally

    def note_homing_end(self):
        pass  # RS485 doesn't need special homing end handling

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
        return None, 0  # No step/dir history for RS485

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        """Return actual position from RS485 drive."""
        try:
            return self._protocol.get_actual_position()
        except Exception:
            return self._position_tracker.get_actual_position()

    def get_status(self):
        """Return drive status for diagnostics."""
        try:
            state = self._protocol.get_state_name()
            actual = self._position_tracker.get_actual_position()
            commanded = self._position_tracker.get_commanded_position()
            error = self._protocol.get_error_code()
            is_fault = "FAULT" in state.upper()
            following_error = commanded - actual
            # Try to get velocity (may not be available)
            try:
                actual_velocity = self._protocol.get_actual_velocity()
            except Exception:
                actual_velocity = 0
            # Try to get torque (may not be available)
            try:
                actual_torque = self._protocol.get_actual_torque()
            except Exception:
                actual_torque = 0
            return {
                "state": state,
                "actual_position": actual,
                "commanded_position": commanded,
                "following_error": following_error,
                "actual_velocity": actual_velocity,
                "actual_torque": actual_torque,
                "error_code": error,
                "is_fault": is_fault,
            }
        except Exception:
            return {"state": "unknown"}

    def close(self):
        """Close the RS485 connection."""
        try:
            self._protocol.close()
        except Exception:
            pass
