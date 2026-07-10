# CiA 402 drive profile state machine
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import time


# CiA 402 states (derived from Statusword bits 0-6, 9-10)
STATE_NOT_READY = 0x00
STATE_SWITCH_ON_DISABLED = 0x40
STATE_READY_TO_SWITCH_ON = 0x21
STATE_SWITCHED_ON = 0x23
STATE_OPERATION_ENABLED = 0x27
STATE_QUICK_STOP_ACTIVE = 0x07
STATE_FAULT_REACTION_ACTIVE = 0x0F
STATE_FAULT = 0x08

STATE_MASK = 0x006F  # Bits 0-3, 5-6

STATE_NAMES = {
    STATE_NOT_READY: "NOT_READY",
    STATE_SWITCH_ON_DISABLED: "SWITCH_ON_DISABLED",
    STATE_READY_TO_SWITCH_ON: "READY_TO_SWITCH_ON",
    STATE_SWITCHED_ON: "SWITCHED_ON",
    STATE_OPERATION_ENABLED: "OPERATION_ENABLED",
    STATE_QUICK_STOP_ACTIVE: "QUICK_STOP_ACTIVE",
    STATE_FAULT_REACTION_ACTIVE: "FAULT_REACTION_ACTIVE",
    STATE_FAULT: "FAULT",
}

# Controlword commands
CW_SHUTDOWN = 0x0006
CW_SWITCH_ON = 0x0007
CW_ENABLE_OPERATION = 0x000F
CW_DISABLE_VOLTAGE = 0x0000
CW_QUICK_STOP = 0x0002
CW_DISABLE_OPERATION = 0x0007
CW_FAULT_RESET = 0x0080

# Operating modes (0x6060 values)
MODE_PP = 1      # Profile Position
MODE_PV = 3      # Profile Velocity
MODE_PT = 4      # Profile Torque
MODE_HOMING = 6  # Homing
MODE_IP = 7      # Interpolated Position
MODE_CSP = 8     # Cyclic Synchronous Position
MODE_CSV = 9     # Cyclic Synchronous Velocity
MODE_CST = 10    # Cyclic Synchronous Torque

MODE_NAMES = {
    MODE_PP: "PP",
    MODE_PV: "PV",
    MODE_PT: "PT",
    MODE_HOMING: "HOMING",
    MODE_IP: "IP",
    MODE_CSP: "CSP",
    MODE_CSV: "CSV",
    MODE_CST: "CST",
}

# CiA 402 homing methods (0x6098 values)
HOMING_METHOD_CURRENT_POS = 35   # Current position
HOMING_METHOD_POS_LIMIT = 17     # Positive limit switch
HOMING_METHOD_NEG_LIMIT = 18     # Negative limit switch
HOMING_METHOD_POS_HOME = 1       # Positive home switch
HOMING_METHOD_NEG_HOME = 2       # Negative home switch
HOMING_METHOD_POS_HOME_INDEX = 11  # Positive home + index
HOMING_METHOD_NEG_HOME_INDEX = 12  # Negative home + index
HOMING_METHOD_NEG_LIMIT_INDEX = 23 # Negative limit + index
HOMING_METHOD_POS_LIMIT_INDEX = 27 # Positive limit + index
HOMING_METHOD_INDEX_POS = 33     # Index, positive direction
HOMING_METHOD_INDEX_NEG = 34     # Index, negative direction

HOMING_METHOD_NAMES = {
    HOMING_METHOD_CURRENT_POS: "current_position",
    HOMING_METHOD_POS_LIMIT: "positive_limit",
    HOMING_METHOD_NEG_LIMIT: "negative_limit",
    HOMING_METHOD_POS_HOME: "positive_home",
    HOMING_METHOD_NEG_HOME: "negative_home",
    HOMING_METHOD_POS_HOME_INDEX: "positive_home_index",
    HOMING_METHOD_NEG_HOME_INDEX: "negative_home_index",
    HOMING_METHOD_NEG_LIMIT_INDEX: "negative_limit_index",
    HOMING_METHOD_POS_LIMIT_INDEX: "positive_limit_index",
    HOMING_METHOD_INDEX_POS: "index_positive",
    HOMING_METHOD_INDEX_NEG: "index_negative",
}

# Statusword homing bits
SW_HOMING_ATTAINED = 1 << 12
SW_HOMING_ERROR = 1 << 13

# Controlword homing bits
CW_HOMING_START = 1 << 4


class CiA402Error(Exception):
    pass


class CiA402Device:
    """CiA 402 drive profile state machine manager."""

    def __init__(self, node, mode=MODE_CSP):
        self.node = node
        self._mode = mode
        self._enabled = False

    def get_state(self):
        """Read current state from Statusword (0x6041)."""
        sw = self.node.sdo_read(0x6041, 0)
        return sw & STATE_MASK

    def get_state_name(self):
        state = self.get_state()
        return STATE_NAMES.get(state, "UNKNOWN(0x%02X)" % state)

    def is_enabled(self):
        return self.get_state() == STATE_OPERATION_ENABLED

    def is_fault(self):
        state = self.get_state()
        return state in (STATE_FAULT, STATE_FAULT_REACTION_ACTIVE)

    def fault_reset(self):
        """Reset fault state."""
        if not self.is_fault():
            return
        self.node.sdo_write(0x6040, 0, CW_FAULT_RESET)
        time.sleep(0.05)
        # Wait for state to leave fault
        for _ in range(50):
            state = self.get_state()
            if state != STATE_FAULT:
                break
            time.sleep(0.02)
        else:
            raise CiA402Error("Fault reset timeout")

    def enable(self):
        """Transition through states to reach OPERATION ENABLED."""
        if self.is_enabled():
            return

        # Clear fault if present
        if self.is_fault():
            self.fault_reset()

        state = self.get_state()
        logging.info(
            "CiA402 node %d: current state=%s",
            self.node.node_id, STATE_NAMES.get(state, hex(state)),
        )

        # Transition: SWITCH_ON_DISABLED → READY_TO_SWITCH_ON
        if state == STATE_SWITCH_ON_DISABLED:
            self.node.sdo_write(0x6040, 0, CW_SHUTDOWN)
            state = self._wait_state(
                STATE_READY_TO_SWITCH_ON, timeout=2.0
            )

        # Transition: READY_TO_SWITCH_ON → SWITCHED_ON
        if state == STATE_READY_TO_SWITCH_ON:
            self.node.sdo_write(0x6040, 0, CW_SWITCH_ON)
            state = self._wait_state(STATE_SWITCHED_ON, timeout=2.0)

        # Transition: SWITCHED_ON → OPERATION_ENABLED
        if state == STATE_SWITCHED_ON:
            self.node.sdo_write(0x6040, 0, CW_ENABLE_OPERATION)
            state = self._wait_state(STATE_OPERATION_ENABLED, timeout=2.0)

        if state != STATE_OPERATION_ENABLED:
            raise CiA402Error(
                "Failed to enable node %d: state=%s"
                % (self.node.node_id, STATE_NAMES.get(state, hex(state)))
            )

        self._enabled = True
        logging.info("CiA402 node %d: OPERATION ENABLED", self.node.node_id)

    def disable(self):
        """Disable the drive."""
        self.node.sdo_write(0x6040, 0, CW_DISABLE_VOLTAGE)
        self._enabled = False
        time.sleep(0.05)

    def quick_stop(self):
        """Perform quick stop."""
        self.node.sdo_write(0x6040, 0, CW_QUICK_STOP)
        self._enabled = False
        time.sleep(0.05)

    def set_mode(self, mode):
        """Set operating mode (0x6060)."""
        mode_name = MODE_NAMES.get(mode, "UNKNOWN(%d)" % mode)
        self.node.sdo_write(0x6060, 0, mode)
        time.sleep(0.01)
        # Verify
        actual = self.node.sdo_read(0x6061, 0)
        if actual != mode:
            raise CiA402Error(
                "Mode set failed: requested %s(%d), got %d"
                % (mode_name, mode, actual)
            )
        self._mode = mode
        logging.info("CiA402 node %d: mode=%s", self.node.node_id, mode_name)

    def get_mode(self):
        """Get current operating mode."""
        return self.node.sdo_read(0x6061, 0)

    def get_mode_name(self):
        mode = self.get_mode()
        return MODE_NAMES.get(mode, "UNKNOWN(%d)" % mode)

    def set_target_position(self, position):
        """Set target position (0x607A) for CSP mode."""
        self.node.sdo_write(0x607A, 0, position, size=4)

    def get_actual_position(self):
        """Get actual position (0x6064)."""
        return self._signed32(self.node.sdo_read(0x6064, 0))

    def set_target_velocity(self, velocity):
        """Set target velocity (0x60FF) for CSV mode."""
        self.node.sdo_write(0x60FF, 0, velocity, size=4)

    def get_actual_velocity(self):
        """Get actual velocity (0x606C)."""
        return self._signed32(self.node.sdo_read(0x606C, 0))

    def get_status_word(self):
        """Get raw status word (0x6041)."""
        return self.node.sdo_read(0x6041, 0)

    def get_error_code(self):
        """Get error code (0x603F)."""
        try:
            return self.node.sdo_read(0x603F, 0)
        except Exception:
            return 0

    def configure_default_pdo_mapping(self):
        """Configure default PDO mapping for CSP mode.

        RPDO1: Target Position (0x607A:00, 32-bit) + Controlword (0x6040:00, 16-bit)
        TPDO1: Position Actual (0x6064:00, 32-bit) + Statusword (0x6041:00, 16-bit)
        """
        self.node.configure_rpdo(1, [
            (0x607A, 0x00, 32),  # Target Position
            (0x6040, 0x00, 16),  # Controlword
        ], trans_type=0x01)

        self.node.configure_tpdo(1, [
            (0x6064, 0x00, 32),  # Position Actual Value
            (0x6041, 0x00, 16),  # Statusword
        ], trans_type=0x01)

        logging.info(
            "CiA402 node %d: default PDO mapping configured",
            self.node.node_id,
        )

    def configure_homing(self, method, speed_switch=None, speed_zero=None,
                         accel=None, offset=0):
        """Configure CiA 402 homing mode parameters.

        Args:
            method: Homing method (HOMING_METHOD_* constant or int)
            speed_switch: Speed for switch search (encoder counts/s)
            speed_zero: Speed for zero search (encoder counts/s)
            accel: Homing acceleration (encoder counts/s^2)
            offset: Home offset (encoder counts)
        """
        # Set homing method (0x6098)
        self.node.sdo_write(0x6098, 0, method)
        time.sleep(0.005)

        # Set homing speeds (0x6099)
        if speed_switch is not None:
            self.node.sdo_write(0x6099, 1, speed_switch)
            time.sleep(0.005)
        if speed_zero is not None:
            self.node.sdo_write(0x6099, 2, speed_zero)
            time.sleep(0.005)

        # Set homing acceleration (0x609A)
        if accel is not None:
            self.node.sdo_write(0x609A, 0, accel)
            time.sleep(0.005)

        # Set home offset (0x607C)
        if offset != 0:
            self.node.sdo_write(0x607C, 0, offset)
            time.sleep(0.005)

        method_name = HOMING_METHOD_NAMES.get(method, str(method))
        logging.info(
            "CiA402 node %d: homing configured, method=%s, "
            "speed_switch=%s, speed_zero=%s",
            self.node.node_id, method_name, speed_switch, speed_zero,
        )

    def start_homing(self):
        """Start homing sequence.

        Switches to Homing mode, enables drive, and triggers homing.
        Call is_homing_done() to poll for completion.
        """
        # Set mode to Homing
        self.set_mode(MODE_HOMING)

        # Enable drive
        self.enable()

        # Trigger homing (set bit 4 of Controlword)
        self.node.sdo_write(0x6040, 0, CW_ENABLE_OPERATION | CW_HOMING_START)
        logging.info("CiA402 node %d: homing started", self.node.node_id)

    def is_homing_done(self):
        """Check if homing is complete.

        Returns:
            True if homing attained and target reached,
            False if still in progress.
        """
        sw = self.get_status_word()
        homing_attained = bool(sw & SW_HOMING_ATTAINED)
        homing_error = bool(sw & SW_HOMING_ERROR)
        if homing_error:
            raise CiA402Error(
                "Homing error on node %d (Statusword=0x%04X)"
                % (self.node.node_id, sw)
            )
        return homing_attained

    def get_homing_status(self):
        """Get detailed homing status.

        Returns dict with 'attained', 'error', 'state' keys.
        """
        sw = self.get_status_word()
        return {
            "attained": bool(sw & SW_HOMING_ATTAINED),
            "error": bool(sw & SW_HOMING_ERROR),
            "state": self.get_state_name(),
            "statusword": sw,
        }

    def wait_homing_done(self, timeout=30.0):
        """Wait for homing to complete.

        Returns actual position after homing.
        Raises CiA402Error on timeout or error.
        """
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if self.is_homing_done():
                pos = self.get_actual_position()
                logging.info(
                    "CiA402 node %d: homing done, position=%d",
                    self.node.node_id, pos,
                )
                return pos
            time.sleep(0.02)
        status = self.get_homing_status()
        raise CiA402Error(
            "Homing timeout on node %d: %s"
            % (self.node.node_id, status)
        )

    def build_rpdo1_data(self, target_position, controlword=None):
        """Build RPDO1 data bytes for CSP mode.

        Returns bytes: [target_pos(4 bytes LE), controlword(2 bytes LE)]
        """
        import struct
        if controlword is None:
            controlword = CW_ENABLE_OPERATION
        pos = target_position & 0xFFFFFFFF
        return struct.pack("<IH", pos, controlword)

    def parse_tpdo1_data(self, data):
        """Parse TPDO1 data from CSP mode.

        Returns (actual_position, statusword).
        """
        import struct
        if len(data) < 6:
            return 0, 0
        pos_raw, sw = struct.unpack_from("<IH", data, 0)
        return self._signed32(pos_raw), sw

    def _wait_state(self, expected, timeout=2.0):
        """Wait for drive to reach expected state."""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            state = self.get_state()
            if state == expected:
                return state
            time.sleep(0.02)
        return self.get_state()

    @staticmethod
    def _signed32(val):
        """Convert unsigned 32-bit to signed."""
        if val >= 0x80000000:
            val -= 0x100000000
        return val
