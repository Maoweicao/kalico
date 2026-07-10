# CANopen stepper backend for Kalico
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
        """Record a position sample."""
        self._commanded_pos = commanded_pos
        self._actual_pos = actual_pos
        self._history.append((clock, commanded_pos, actual_pos))

    def get_position_at(self, clock):
        """Get actual position at a given clock time."""
        if not self._history:
            return self._actual_pos
        # Find closest entry
        best = None
        for entry_clock, cmd, actual in reversed(self._history):
            if entry_clock <= clock:
                return actual
            best = actual
        return self._history[0][2] if self._history else self._actual_pos

    def get_actual_position(self):
        return self._actual_pos

    def get_commanded_position(self):
        return self._commanded_pos


class CANopenBackend(stepper.StepperBackend):
    """StepperBackend implementation for CANopen servo drives."""

    def __init__(self, node, device, sync_group, step_dist):
        self._node = node
        self._device = device
        self._sync_group = sync_group
        self._step_dist = step_dist
        self._stepper_kinematics = None
        self._trapq = None
        self._position_tracker = PositionTracker()
        self._position_tracker.set_step_dist(step_dist)
        self._mcu = None
        self._last_commanded = 0

    def setup(self, mcu, oid, step_pulse_duration, step_both_edge):
        self._mcu = mcu

    def set_kinematics(self, stepper_kinematics, step_dist):
        self._stepper_kinematics = stepper_kinematics
        self._step_dist = step_dist
        self._position_tracker.set_step_dist(step_dist)
        # NOTE: Do NOT call itersolve_set_stepcompress - we don't use it

    def set_trapq(self, trapq):
        self._trapq = trapq

    def generate_steps(self, flush_time):
        """Get commanded position from itersolve and queue for PDO."""
        if self._stepper_kinematics is None:
            return
        ffi_main, ffi_lib = chelper.get_ffi()
        sk = self._stepper_kinematics

        # Get commanded position from itersolve
        cmd_pos = ffi_lib.itersolve_get_commanded_pos(sk)

        # Convert to integer steps
        mcu_pos = cmd_pos / self._step_dist
        if mcu_pos >= 0.0:
            target_steps = int(mcu_pos + 0.5)
        else:
            target_steps = int(mcu_pos - 0.5)

        # Queue RPDO for sync group
        rpdo_data = self._device.build_rpdo1_data(target_steps)
        self._sync_group.queue_rpdo(self._node.node_id, 1, rpdo_data)

        # Read latest TPDO (actual position)
        tpdo_data = self._sync_group.get_tpdo(self._node.node_id, 1)
        if tpdo_data is not None:
            actual_pos, statusword = self._device.parse_tpdo1_data(tpdo_data)
            # Convert actual position back to commanded_pos units
            self._position_tracker.update(
                0, cmd_pos, actual_pos * self._step_dist
            )

        self._last_commanded = target_steps

    def set_dir_inverted(self, invert_dir):
        pass  # CANopen handles direction internally

    def note_homing_end(self):
        # Re-enable drive after homing
        try:
            self._device.enable()
        except Exception:
            logging.exception("CANopen: failed to re-enable after homing")

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
        return None, 0  # No step/dir history for CANopen

    def query_position(self, oid, invert_dir, mcu, get_position_cmd):
        """Return actual position from TPDO cache."""
        tpdo_data = self._sync_group.get_tpdo(self._node.node_id, 1)
        if tpdo_data is not None:
            actual_pos, _ = self._device.parse_tpdo1_data(tpdo_data)
            return actual_pos
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


class CANopenEndstop:
    """Endstop that triggers via CiA 402 homing mode.

    Implements the interface expected by HomingMove:
    - home_start() -> trigger_completion
    - home_wait() -> trigger_time
    - add_stepper() / get_steppers()
    - get_mcu()
    - query_endstop()
    """

    def __init__(self, device, backend, mcu):
        self._device = device
        self._backend = backend
        self._mcu = mcu
        self._steppers = []
        self._homing_method = 0  # Will be set by configure()
        self._homing_speed_switch = None
        self._homing_speed_zero = None
        self._trigger_completion = None

    def configure(self, method, speed_switch=None, speed_zero=None,
                  accel=None, offset=0):
        """Configure CiA 402 homing parameters."""
        from . import cia402
        self._homing_method = method
        self._homing_speed_switch = speed_switch
        self._homing_speed_zero = speed_zero
        self._homing_accel = accel
        self._homing_offset = offset

    def get_mcu(self):
        return self._mcu

    def add_stepper(self, stepper_obj):
        if stepper_obj not in self._steppers:
            self._steppers.append(stepper_obj)

    def get_steppers(self):
        return list(self._steppers)

    def home_start(self, print_time, sample_time, sample_count, rest_time,
                   triggered=True):
        """Start CiA 402 homing sequence."""
        reactor = self._mcu.get_printer().get_reactor()
        self._trigger_completion = reactor.completion()

        try:
            # Configure homing parameters
            self._device.configure_homing(
                method=self._homing_method,
                speed_switch=self._homing_speed_switch,
                speed_zero=self._homing_speed_zero,
                accel=self._homing_accel,
                offset=self._homing_offset,
            )

            # Start homing
            self._device.start_homing()
        except Exception as e:
            logging.error("CANopen homing start error: %s", e)
            self._trigger_completion.complete(False)

        return self._trigger_completion

    def home_wait(self, home_end_time):
        """Wait for CiA 402 homing to complete.

        Returns trigger time on success, 0.0 on failure.
        """
        reactor = self._mcu.get_printer().get_reactor()

        # Poll for homing completion
        while reactor.monotonic() < home_end_time:
            try:
                if self._device.is_homing_done():
                    # Homing attained - read actual position
                    actual_pos = self._device.get_actual_position()
                    logging.info(
                        "CANopen homing done, actual_pos=%d", actual_pos
                    )
                    if self._trigger_completion is not None:
                        self._trigger_completion.complete(True)
                    # Return current time as trigger time
                    # (actual position sync happens in note_homing_end)
                    return reactor.monotonic()
                if self._device.is_fault():
                    sw = self._device.get_status_word()
                    logging.error(
                        "CANopen homing fault, Statusword=0x%04X", sw
                    )
                    if self._trigger_completion is not None:
                        self._trigger_completion.complete(False)
                    return 0.0
            except Exception as e:
                logging.error("CANopen homing wait error: %s", e)
                if self._trigger_completion is not None:
                    self._trigger_completion.complete(False)
                return 0.0
            time.sleep(0.02)

        logging.error("CANopen homing timeout")
        if self._trigger_completion is not None:
            self._trigger_completion.complete(False)
        return 0.0

    def query_endstop(self, print_time):
        """Query endstop state.

        Returns True if homing switch is active.
        """
        try:
            sw = self._device.get_status_word()
            # Bit 12: homing attained (switch found)
            return bool(sw & (1 << 12))
        except Exception:
            return False

    def get_position_endstop(self):
        """Return endstop position (used by PrinterRail)."""
        return 0.0
