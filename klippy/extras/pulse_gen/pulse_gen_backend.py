# Pulse generator stepper backends for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import collections
import logging
import time

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


class AbsolutePulseGenBackend(stepper.StepperBackend):
    """Absolute position command mode.

    Sends absolute position setpoints to the external pulse generator
    via the configured protocol. Similar to CSP mode in CANopen/EtherCAT.

    The generator's internal trajectory planner handles acceleration
    and pulse generation.

    Args:
        protocol: RS485Protocol instance for communication
        step_dist: Distance per encoder count (mm)
        reg_target: Register address for target position
        reg_actual: Register address for actual position (0 if open-loop)
    """

    def __init__(self, protocol, step_dist, reg_target=0x607A,
                 reg_actual=0x6064):
        self._protocol = protocol
        self._step_dist = step_dist
        self._reg_target = reg_target
        self._reg_actual = reg_actual
        self._stepper_kinematics = None
        self._mcu = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._open_loop = (reg_actual == 0)

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu
        try:
            self._protocol.open()
            logging.info("PulseGen: protocol opened (absolute mode)")
        except Exception as e:
            logging.error("PulseGen: failed to open protocol: %s", e)

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)

    def set_trapq(self, trapq):
        pass

    def generate_steps(self, flush_time):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        cmd_pos = ffi_lib.itersolve_get_commanded_pos(
            self._stepper_kinematics
        )
        target = int(cmd_pos / self._step_dist + 0.5)

        try:
            self._protocol.write_register(self._reg_target, target)
            if self._open_loop:
                self._position_tracker.update(
                    0, cmd_pos, target * self._step_dist
                )
            else:
                actual = self._protocol.read_register(self._reg_actual)
                self._position_tracker.update(
                    0, cmd_pos, actual * self._step_dist
                )
        except Exception as e:
            logging.warning("PulseGen absolute comm error: %s", e)

    def set_dir_inverted(self, invert_dir):
        pass

    def note_homing_end(self):
        pass

    def set_last_position(self, clock, position):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        ffi_lib.itersolve_set_position(
            self._stepper_kinematics, position, 0.0, 0.0
        )

    def get_past_position(self, clock):
        return self._position_tracker.get_position_at(clock)

    def dump_steps(self, count, start_clock, end_clock):
        return None, 0

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        try:
            if not self._open_loop:
                actual = self._protocol.read_register(self._reg_actual)
                return actual
        except Exception:
            pass
        return self._position_tracker.get_actual_position()

    def get_status(self):
        try:
            actual = self._position_tracker.get_actual_position()
            return {"mode": "absolute", "actual_position": actual}
        except Exception:
            return {"mode": "absolute", "state": "unknown"}

    def close(self):
        try:
            self._protocol.close()
        except Exception:
            pass


class RelativePulseGenBackend(stepper.StepperBackend):
    """Relative displacement command mode.

    Sends relative displacement (pulse count) to the external pulse
    generator. Suitable for open-loop pulse modules without encoders.

    Args:
        protocol: RS485Protocol instance
        step_dist: Distance per encoder count (mm)
        reg_relative: Register address for relative displacement
        reg_actual: Register address for actual position (0 if open-loop)
    """

    def __init__(self, protocol, step_dist, reg_relative=0x0020,
                 reg_actual=0):
        self._protocol = protocol
        self._step_dist = step_dist
        self._reg_relative = reg_relative
        self._reg_actual = reg_actual
        self._stepper_kinematics = None
        self._mcu = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._last_target = 0
        self._open_loop = (reg_actual == 0)

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu
        try:
            self._protocol.open()
            logging.info("PulseGen: protocol opened (relative mode)")
        except Exception as e:
            logging.error("PulseGen: failed to open protocol: %s", e)

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)

    def set_trapq(self, trapq):
        pass

    def generate_steps(self, flush_time):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        cmd_pos = ffi_lib.itersolve_get_commanded_pos(
            self._stepper_kinematics
        )
        target = int(cmd_pos / self._step_dist + 0.5)
        delta = target - self._last_target

        if delta != 0:
            try:
                self._protocol.write_register(self._reg_relative, delta)
            except Exception as e:
                logging.warning("PulseGen relative comm error: %s", e)

        self._last_target = target

        if self._open_loop:
            self._position_tracker.update(
                0, cmd_pos, target * self._step_dist
            )
        else:
            try:
                actual = self._protocol.read_register(self._reg_actual)
                self._position_tracker.update(
                    0, cmd_pos, actual * self._step_dist
                )
            except Exception:
                self._position_tracker.update(
                    0, cmd_pos, target * self._step_dist
                )

    def set_dir_inverted(self, invert_dir):
        pass

    def note_homing_end(self):
        self._last_target = 0

    def set_last_position(self, clock, position):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        ffi_lib.itersolve_set_position(
            self._stepper_kinematics, position, 0.0, 0.0
        )
        self._last_target = int(position / self._step_dist + 0.5)

    def get_past_position(self, clock):
        return self._position_tracker.get_position_at(clock)

    def dump_steps(self, count, start_clock, end_clock):
        return None, 0

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        try:
            if not self._open_loop:
                actual = self._protocol.read_register(self._reg_actual)
                return actual
        except Exception:
            pass
        return self._position_tracker.get_actual_position()

    def get_status(self):
        try:
            actual = self._position_tracker.get_actual_position()
            return {"mode": "relative", "actual_position": actual}
        except Exception:
            return {"mode": "relative", "state": "unknown"}

    def close(self):
        try:
            self._protocol.close()
        except Exception:
            pass


class VelocityPulseGenBackend(stepper.StepperBackend):
    """Velocity command mode.

    Sends velocity commands to the external pulse generator.
    The generator handles position tracking internally.

    Args:
        protocol: RS485Protocol instance
        step_dist: Distance per encoder count (mm)
        reg_velocity: Register address for velocity command
        reg_actual: Register address for actual position (0 if open-loop)
    """

    def __init__(self, protocol, step_dist, reg_velocity=0x0030,
                 reg_actual=0):
        self._protocol = protocol
        self._step_dist = step_dist
        self._reg_velocity = reg_velocity
        self._reg_actual = reg_actual
        self._stepper_kinematics = None
        self._mcu = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._last_target = 0
        self._last_time = 0.0
        self._open_loop = (reg_actual == 0)

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu
        try:
            self._protocol.open()
            logging.info("PulseGen: protocol opened (velocity mode)")
        except Exception as e:
            logging.error("PulseGen: failed to open protocol: %s", e)

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)

    def set_trapq(self, trapq):
        pass

    def generate_steps(self, flush_time):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        cmd_pos = ffi_lib.itersolve_get_commanded_pos(
            self._stepper_kinematics
        )
        target = int(cmd_pos / self._step_dist + 0.5)
        now = time.monotonic()

        if self._last_time > 0:
            dt = now - self._last_time
            if dt > 0.0001:
                velocity = int((target - self._last_target) / dt)
                try:
                    self._protocol.write_register(
                        self._reg_velocity, velocity
                    )
                except Exception as e:
                    logging.warning("PulseGen velocity comm error: %s", e)

        self._last_target = target
        self._last_time = now

        if self._open_loop:
            self._position_tracker.update(
                0, cmd_pos, target * self._step_dist
            )
        else:
            try:
                actual = self._protocol.read_register(self._reg_actual)
                self._position_tracker.update(
                    0, cmd_pos, actual * self._step_dist
                )
            except Exception:
                self._position_tracker.update(
                    0, cmd_pos, target * self._step_dist
                )

    def set_dir_inverted(self, invert_dir):
        pass

    def note_homing_end(self):
        self._last_target = 0
        self._last_time = 0.0

    def set_last_position(self, clock, position):
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        ffi_lib.itersolve_set_position(
            self._stepper_kinematics, position, 0.0, 0.0
        )
        self._last_target = int(position / self._step_dist + 0.5)

    def get_past_position(self, clock):
        return self._position_tracker.get_position_at(clock)

    def dump_steps(self, count, start_clock, end_clock):
        return None, 0

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        try:
            if not self._open_loop:
                actual = self._protocol.read_register(self._reg_actual)
                return actual
        except Exception:
            pass
        return self._position_tracker.get_actual_position()

    def get_status(self):
        try:
            actual = self._position_tracker.get_actual_position()
            return {"mode": "velocity", "actual_position": actual}
        except Exception:
            return {"mode": "velocity", "state": "unknown"}

    def close(self):
        try:
            self._protocol.close()
        except Exception:
            pass
