# Example: Leadshine RS485 servo protocol adapter
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
# This is an example of how to write a custom RS485 protocol adapter
# for Leadshine servo drives. Adapt the register addresses to match
# your specific drive model.
#
# Usage in config:
#   [rs485_stepper x]
#   rs485_protocol: custom
#   protocol_class: leadshine_rs485.LeadshineRS485Protocol
#   ...
import logging
import struct

from klippy.extras.rs485.modbus_rtu import ModbusRtuProtocol
from klippy.extras.rs485.protocol import RS485ProtocolError


# Leadshine ES series register mapping
# These addresses may vary by drive model - check your drive manual
LEADSHINE_REGISTERS = {
    "control_word": 0x0000,
    "status_word": 0x0001,
    "mode_of_operation": 0x0002,
    "error_code": 0x0003,
    "target_position_l": 0x0010,
    "target_position_h": 0x0011,
    "actual_position_l": 0x0012,
    "actual_position_h": 0x0013,
    "target_velocity": 0x0020,
    "actual_velocity": 0x0021,
}


class LeadshineRS485Protocol(ModbusRtuProtocol):
    """Leadshine RS485 servo protocol adapter.

    This extends ModbusRtuProtocol with Leadshine-specific register
    mapping and position encoding. Leadshine servo drives typically use
    Modbus RTU frames but with custom register addresses.

    Register layout (Leadshine ES series):
    - 0x0000: Control word (16-bit)
    - 0x0001: Status word (16-bit)
    - 0x0002: Operating mode (16-bit)
    - 0x0003: Error code (16-bit)
    - 0x0010: Target position low word (16-bit)
    - 0x0011: Target position high word (16-bit)
    - 0x0012: Actual position low word (16-bit)
    - 0x0013: Actual position high word (16-bit)
    - 0x0020: Target velocity (16-bit)
    - 0x0021: Actual velocity (16-bit)

    Control word bits (Leadshine specific):
    - bit 0: Switch on
    - bit 1: Enable voltage
    - bit 2: Quick stop
    - bit 3: Enable operation
    - bit 4: Start homing (in homing mode)
    - bit 7: Fault reset

    Status word bits:
    - bit 0: Ready to switch on
    - bit 1: Switched on
    - bit 2: Operation enabled
    - bit 3: Fault
    - bit 4: Voltage enabled
    - bit 5: Quick stop
    - bit 6: Switch on disabled
    - bit 12: Homing attained
    """

    def __init__(self, transport, slave_id=1, **kwargs):
        # Use Leadshine register mapping
        register_map = {
            "control_word": LEADSHINE_REGISTERS["control_word"],
            "status_word": LEADSHINE_REGISTERS["status_word"],
            "mode_of_operation": LEADSHINE_REGISTERS["mode_of_operation"],
            "error_code": LEADSHINE_REGISTERS["error_code"],
            # For 32-bit positions, we use the low word address
            # The protocol handles splitting into two 16-bit registers
            "target_position": LEADSHINE_REGISTERS["target_position_l"],
            "actual_position": LEADSHINE_REGISTERS["actual_position_l"],
        }
        super().__init__(transport, slave_id, register_map=register_map)
        self._enabled = False

    def set_target_position(self, position):
        """Set 32-bit target position via two 16-bit registers."""
        pos_u = position & 0xFFFFFFFF
        lo = pos_u & 0xFFFF
        hi = (pos_u >> 16) & 0xFFFF
        self.write_register(LEADSHINE_REGISTERS["target_position_l"], lo)
        self.write_register(LEADSHINE_REGISTERS["target_position_h"], hi)

    def get_actual_position(self):
        """Read 32-bit actual position from two 16-bit registers."""
        lo = self.read_register(LEADSHINE_REGISTERS["actual_position_l"])
        hi = self.read_register(LEADSHINE_REGISTERS["actual_position_h"])
        pos = (hi << 16) | lo
        if pos >= 0x80000000:
            pos -= 0x100000000
        return pos

    def enable_drive(self):
        """Enable the drive using Leadshine control word sequence."""
        # Shutdown: CW = 0x0006
        self.set_control_word(0x0006)
        # Switch on: CW = 0x0007
        self.set_control_word(0x0007)
        # Enable operation: CW = 0x000F
        self.set_control_word(0x000F)
        self._enabled = True
        logging.info(
            "Leadshine RS485 slave %d: drive enabled",
            self.get_slave_id(),
        )

    def disable_drive(self):
        """Disable the drive."""
        self.set_control_word(0x0000)
        self._enabled = False

    def fault_reset(self):
        """Reset drive fault."""
        self.set_control_word(0x0080)

    def get_state_name(self):
        """Get state name from Leadshine status word."""
        try:
            sw = self.get_status_word()
            if sw & (1 << 3):
                return "FAULT"
            if sw & (1 << 6):
                return "SWITCH_ON_DISABLED"
            if sw & (1 << 2):
                return "OPERATION_ENABLED"
            if sw & (1 << 1):
                return "SWITCHED_ON"
            if sw & (1 << 0):
                return "READY_TO_SWITCH_ON"
            return "UNKNOWN(0x%04X)" % sw
        except Exception:
            return "unknown"

    def is_homing_done(self):
        """Check if homing is complete (Leadshine specific)."""
        try:
            sw = self.get_status_word()
            return bool(sw & (1 << 12))
        except Exception:
            return False
