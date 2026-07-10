# EtherCAT master protocol wrapper (pysoem)
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import struct
import threading
import time


class EtherCATError(Exception):
    pass


class EtherCATSlave:
    """Wrapper around a pysoem slave object."""

    def __init__(self, pysoem_slave, position):
        self._slave = pysoem_slave
        self.position = position
        self.name = pysoem_slave.name

    def sdo_read(self, index, subindex=0):
        """Read an SDO object. Returns integer value."""
        data = self._slave.sdo_read(index, subindex)
        if len(data) == 1:
            return struct.unpack('<b', data)[0]
        elif len(data) == 2:
            return struct.unpack('<h', data)[0]
        elif len(data) == 4:
            return struct.unpack('<i', data)[0]
        else:
            return int.from_bytes(data, 'little', signed=True)

    def sdo_write(self, index, subindex, value, size=4):
        """Write an SDO object. value is an integer."""
        if size == 1:
            data = struct.pack('<b', value)
        elif size == 2:
            data = struct.pack('<h', value)
        elif size == 4:
            data = struct.pack('<i', value)
        else:
            data = value.to_bytes(size, 'little', signed=True)
        self._slave.sdo_write(index, subindex, data)

    def write_output(self, data):
        """Write output process data (RPDO)."""
        self._slave.output = data

    def read_input(self):
        """Read input process data (TPDO)."""
        return bytes(self._slave.input)

    def get_state(self):
        """Get AL state."""
        return self._slave.state

    def set_state(self, state):
        """Set AL state."""
        self._slave.state = state

    def is_op(self):
        """Check if slave is in OPERATIONAL state."""
        import pysoem
        return self._slave.state == pysoem.OP_STATE


class EtherCATMaster:
    """pysoem wrapper managing EtherCAT bus and slaves.

    Args:
        interface_name: Network interface (e.g., 'eth0', '\\Device\\NPF_{...}')
        cycle_time: DC sync cycle time in seconds (default 0.001 = 1ms)
    """

    def __init__(self, interface_name, cycle_time=0.001):
        self._interface = interface_name
        self._cycle_time = cycle_time
        self._master = None
        self._slaves = []
        self._lock = threading.Lock()
        self._started = False

    def open(self):
        """Open the EtherCAT master and discover slaves."""
        import pysoem
        self._master = pysoem.Master()
        self._master.open(self._interface)

        # Discover slaves
        num_slaves = self._master.config_init()
        if num_slaves <= 0:
            raise EtherCATError(
                "No EtherCAT slaves found on '%s'" % self._interface
            )
        logging.info(
            "EtherCAT: found %d slave(s) on '%s'",
            num_slaves, self._interface,
        )

        # Auto-configure PDO mapping
        self._master.config_map()

        # Enable DC sync if cycle_time is set
        if self._cycle_time > 0:
            self._master.config_dc()

        # Log discovered slaves
        self._slaves = []
        for i, s in enumerate(self._master.slaves):
            slave = EtherCATSlave(s, i)
            self._slaves.append(slave)
            logging.info(
                "EtherCAT slave %d: '%s' (state=0x%04X)",
                i, s.name, s.state,
            )

        self._started = True

    def get_slave(self, position):
        """Get a slave by position index."""
        if position < 0 or position >= len(self._slaves):
            raise EtherCATError(
                "EtherCAT slave %d not found (have %d slaves)"
                % (position, len(self._slaves))
            )
        return self._slaves[position]

    def get_slave_count(self):
        """Get number of discovered slaves."""
        return len(self._slaves)

    def exchange_processdata(self):
        """Send/receive process data for all slaves.

        Returns the AL state of the first slave.
        """
        if self._master is None:
            return 0
        with self._lock:
            self._master.send_overlap_processdata()
            self._master.receive_processdata()
            return self._master.readstate()

    def transition_to_op(self):
        """Transition all slaves to OPERATIONAL state."""
        import pysoem
        if self._master is None:
            raise EtherCATError("Master not open")

        # Request SAFE-OP
        for slave in self._master.slaves:
            slave.state = pysoem.SAFEOP_STATE
        self._master.send_processdata()
        self._master.receive_processdata()
        self._master.state_check(pysoem.SAFEOP_STATE, timeout=5000000)

        # Request OP
        for slave in self._master.slaves:
            slave.state = pysoem.OP_STATE
        self._master.send_processdata()
        self._master.receive_processdata()
        self._master.state_check(pysoem.OP_STATE, timeout=5000000)

        # Verify all slaves are in OP
        for i, slave in enumerate(self._master.slaves):
            if slave.state != pysoem.OP_STATE:
                raise EtherCATError(
                    "EtherCAT slave %d failed to reach OP state (0x%04X)"
                    % (i, slave.state)
                )

        logging.info("EtherCAT: all slaves in OPERATIONAL state")

    def close(self):
        """Transition all slaves to INIT and close."""
        import pysoem
        if self._master is not None:
            try:
                for slave in self._master.slaves:
                    slave.state = pysoem.INIT_STATE
                self._master.send_processdata()
            except Exception:
                pass
            try:
                self._master.close()
            except Exception:
                pass
            self._master = None
        self._slaves = []
        self._started = False

    def is_started(self):
        return self._started

    def get_interface(self):
        return self._interface

    def get_cycle_time(self):
        return self._cycle_time

    @staticmethod
    def find_adapters():
        """List available network adapters for EtherCAT."""
        try:
            import pysoem
            return pysoem.find_adapters()
        except ImportError:
            logging.warning("pysoem not installed, cannot list adapters")
            return []
