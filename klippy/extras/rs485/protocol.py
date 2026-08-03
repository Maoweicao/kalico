# RS485 protocol abstraction layer
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.


class RS485ProtocolError(Exception):
    pass


class RS485Protocol:
    """Abstract base class for RS485 protocols.

    Subclass this to implement custom protocols for specific servo drives.
    See ModbusRtuProtocol for a reference implementation.

    Example custom protocol:

        from klippy.extras.rs485.protocol import RS485Protocol

        class MyServoProtocol(RS485Protocol):
            def __init__(self, transport, slave_id=1):
                super().__init__(transport, slave_id)

            def read_register(self, register):
                # Implement protocol-specific register read
                ...

            def write_register(self, register, value):
                # Implement protocol-specific register write
                ...

            def set_target_position(self, position):
                self.write_register(0x0010, position & 0xFFFF)
                self.write_register(0x0011, (position >> 16) & 0xFFFF)

            def get_actual_position(self):
                lo = self.read_register(0x0012)
                hi = self.read_register(0x0013)
                pos = (hi << 16) | lo
                if pos >= 0x80000000:
                    pos -= 0x100000000
                return pos
    """

    def __init__(self, transport, slave_id=1):
        self._transport = transport
        self._slave_id = slave_id

    def open(self):
        """Open the transport connection."""
        self._transport.open()

    def close(self):
        """Close the transport connection."""
        self._transport.close()

    def read_register(self, register):
        """Read a single register. Returns integer value.

        Args:
            register: Register address (protocol-specific)

        Returns:
            Register value as integer
        """
        raise NotImplementedError

    def write_register(self, register, value):
        """Write a single register.

        Args:
            register: Register address (protocol-specific)
            value: Integer value to write
        """
        raise NotImplementedError

    def read_registers(self, start, count):
        """Read multiple consecutive registers.

        Args:
            start: Start register address
            count: Number of registers to read

        Returns:
            List of integer values
        """
        result = []
        for i in range(count):
            result.append(self.read_register(start + i))
        return result

    def write_registers(self, start, values):
        """Write multiple consecutive registers.

        Args:
            start: Start register address
            values: List of integer values to write
        """
        for i, val in enumerate(values):
            self.write_register(start + i, val)

    # Servo control interface (override for your protocol)
    def set_target_position(self, position):
        """Set target position in encoder counts."""
        raise NotImplementedError

    def get_actual_position(self):
        """Get actual position in encoder counts."""
        raise NotImplementedError

    def set_control_word(self, value):
        """Set the drive control word."""
        raise NotImplementedError

    def get_status_word(self):
        """Get the drive status word."""
        raise NotImplementedError

    def set_mode_of_operation(self, mode):
        """Set operating mode."""
        raise NotImplementedError

    def get_mode_of_operation(self):
        """Get current operating mode."""
        raise NotImplementedError

    def get_error_code(self):
        """Get drive error code."""
        return 0

    def get_state_name(self):
        """Get human-readable drive state name."""
        return "unknown"

    def get_slave_id(self):
        return self._slave_id
