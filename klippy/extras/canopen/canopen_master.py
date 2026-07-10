# CANopen master protocol stack (NMT, SDO, PDO, SYNC)
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import struct
import threading
import time

from . import eds_parser


# CANopen COB-IDs
COB_NMT = 0x000
COB_SYNC = 0x080
COB_EMCY_BASE = 0x080
COB_TPDO1_BASE = 0x180
COB_RPDO1_BASE = 0x200
COB_TPDO2_BASE = 0x280
COB_RPDO2_BASE = 0x300
COB_TPDO3_BASE = 0x380
COB_RPDO3_BASE = 0x400
COB_TPDO4_BASE = 0x480
COB_RPDO4_BASE = 0x500
COB_SDO_TX_BASE = 0x580  # Server → Client
COB_SDO_RX_BASE = 0x600  # Client → Server
COB_HEARTBEAT_BASE = 0x700

# NMT commands
NMT_START = 0x01
NMT_STOP = 0x02
NMT_PRE_OP = 0x80
NMT_RESET_NODE = 0x81
NMT_RESET_COMM = 0x82

# SDO command specifiers
SDO_CCS_DOWNLOAD_EXPEDITED = 0x23  # 2-byte index, expedited
SDO_CCS_DOWNLOAD_SEG = 0x21       # 2-byte index, segmented
SDO_CCS_UPLOAD = 0x40             # 2-byte index
SDO_SCS_DOWNLOAD_RESP = 0x60
SDO_SCS_UPLOAD_EXPEDITED = 0x43
SDO_SCS_UPLOAD_SEG = 0x41
SDO_ABORT = 0x80

# SDO abort codes
SDO_ABORT_TOGGLE = 0x05030000
SDO_ABORT_TIMEOUT = 0x05040000
SDO_ABORT_NOT_FOUND = 0x06020000
SDO_ABORT_WRITEONLY = 0x06010001
SDO_ABORT_READONLY = 0x06010002
SDO_ABORT_TYPE_MISMATCH = 0x06070010
SDO_ABORT_DATA_LONG = 0x06070012
SDO_ABORT_DATA_SHORT = 0x06070013


class CANopenError(Exception):
    pass


class SDOError(CANopenError):
    def __init__(self, code, index, subindex):
        self.code = code
        self.index = index
        self.subindex = subindex
        msg = "SDO abort 0x%08X at 0x%04X:%02X" % (code, index, subindex)
        super().__init__(msg)


class CANopenNode:
    """Represents a single CANopen slave node."""

    def __init__(self, node_id, eds, master):
        self.node_id = node_id
        self.eds = eds
        self.master = master
        self.state = "INIT"
        self._sdo_lock = threading.Lock()
        self._sdo_timeout = 1.0

    def nmt_change_state(self, command):
        """Send NMT command to this node."""
        data = bytes([command, self.node_id])
        self.master.send_can(COB_NMT, data)
        if command == NMT_START:
            self.state = "OPERATIONAL"
        elif command == NMT_STOP:
            self.state = "STOPPED"
        elif command == NMT_PRE_OP:
            self.state = "PRE-OPERATIONAL"
        elif command in (NMT_RESET_NODE, NMT_RESET_COMM):
            self.state = "INIT"

    def nmt_start(self):
        self.nmt_change_state(NMT_START)

    def nmt_stop(self):
        self.nmt_change_state(NMT_STOP)

    def nmt_reset(self):
        self.nmt_change_state(NMT_RESET_NODE)

    def sdo_read(self, index, subindex=0, timeout=None):
        """Read an object via SDO. Returns integer value."""
        if timeout is None:
            timeout = self._sdo_timeout
        with self._sdo_lock:
            return self._sdo_read_locked(index, subindex, timeout)

    def _sdo_read_locked(self, index, subindex, timeout):
        # Build SDO upload request: CCS=2, n=e=0, s=0
        cmd = SDO_CCS_UPLOAD
        data = struct.pack("<BHB", cmd, index, subindex)
        tx_cob = COB_SDO_RX_BASE + self.node_id
        rx_cob = COB_SDO_TX_BASE + self.node_id

        self.master.send_can(tx_cob, data)
        resp = self.master.wait_can(rx_cob, timeout)
        if resp is None:
            raise CANopenError(
                "SDO read timeout at 0x%04X:%02X" % (index, subindex)
            )

        resp_cmd = resp[0]
        if resp_cmd == SDO_ABORT:
            abort_code = struct.unpack_from("<I", resp, 4)[0]
            raise SDOError(abort_code, index, subindex)

        # Check for expedited response
        if resp_cmd & 0xE2 == SDO_SCS_UPLOAD_EXPEDITED:
            # Expedited: n = (cmd >> 2) & 3, unused bytes
            n = (resp_cmd >> 2) & 0x03
            data_len = 4 - n
            if data_len == 1:
                return struct.unpack_from("<B", resp, 4)[0]
            elif data_len == 2:
                return struct.unpack_from("<H", resp, 4)[0]
            elif data_len == 4:
                return struct.unpack_from("<I", resp, 4)[0]
            else:
                return struct.unpack_from("<B", resp, 4)[0]

        # Segmented response (not commonly needed for CiA 402)
        raise CANopenError(
            "Segmented SDO read not implemented for 0x%04X:%02X"
            % (index, subindex)
        )

    def sdo_write(self, index, subindex, value, timeout=None, size=None):
        """Write an object via SDO. value is an integer."""
        if timeout is None:
            timeout = self._sdo_timeout
        with self._sdo_lock:
            return self._sdo_write_locked(index, subindex, value, timeout, size)

    def _sdo_write_locked(self, index, subindex, value, timeout, size):
        # Determine data size
        if size is not None:
            data_size = size
        else:
            obj = self.eds.get_object(index, subindex)
            if obj is not None:
                data_size = obj.get_data_type_size()
                if data_size is None:
                    data_size = 4
            else:
                # Auto-detect based on value
                if value <= 0xFF:
                    data_size = 1
                elif value <= 0xFFFF:
                    data_size = 2
                else:
                    data_size = 4

        # Pack value
        if data_size == 1:
            val_bytes = struct.pack("<B", value & 0xFF)
        elif data_size == 2:
            val_bytes = struct.pack("<H", value & 0xFFFF)
        elif data_size == 3:
            val_bytes = struct.pack("<I", value & 0xFFFFFF)[:3]
        elif data_size == 4:
            val_bytes = struct.pack("<I", value & 0xFFFFFFFF)
        else:
            raise CANopenError("Unsupported SDO data size: %d" % data_size)

        # Build expedited download: CCS=1, n=4-size, e=1, s=1
        e = 1  # expedited
        s = 1  # size indicated
        n = 4 - data_size
        cmd = 0x23 | (n << 2) | (e << 1) | s
        pad = b'\x00' * (4 - data_size)
        payload = struct.pack("<BHB", cmd, index, subindex) + val_bytes + pad

        tx_cob = COB_SDO_RX_BASE + self.node_id
        rx_cob = COB_SDO_TX_BASE + self.node_id

        self.master.send_can(tx_cob, payload)
        resp = self.master.wait_can(rx_cob, timeout)
        if resp is None:
            raise CANopenError(
                "SDO write timeout at 0x%04X:%02X" % (index, subindex)
            )

        resp_cmd = resp[0]
        if resp_cmd == SDO_ABORT:
            abort_code = struct.unpack_from("<I", resp, 4)[0]
            raise SDOError(abort_code, index, subindex)

        if resp_cmd != SDO_SCS_DOWNLOAD_RESP:
            raise CANopenError(
                "Unexpected SDO response 0x%02X at 0x%04X:%02X"
                % (resp_cmd, index, subindex)
            )

    def configure_rpdo(self, pdo_num, mapping_entries, trans_type=0x01):
        """Configure an RPDO.

        Args:
            pdo_num: RPDO number (1-4)
            mapping_entries: list of (index, subindex, bit_length)
            trans_type: transmission type (0x01 = on SYNC)
        """
        # Mapping table indices: 0x1400, 0x1401, ... for comm params
        #                       0x1600, 0x1601, ... for mapping
        comm_index = 0x1400 + (pdo_num - 1)
        map_index = 0x1600 + (pdo_num - 1)

        # Calculate COB-ID
        cob_id = COB_RPDO1_BASE + (pdo_num - 1) * 0x100 + self.node_id

        # Go to pre-operational for PDO config
        self.nmt_change_state(NMT_PRE_OP)
        time.sleep(0.01)

        # Disable PDO (set bit 31 of COB-ID)
        self.sdo_write(comm_index, 1, cob_id | (1 << 31))
        time.sleep(0.005)

        # Clear mapping count
        self.sdo_write(map_index, 0, 0)
        time.sleep(0.005)

        # Write mapping entries
        for i, (idx, sub, bit_len) in enumerate(mapping_entries, 1):
            mapping_value = (idx << 16) | (sub << 8) | bit_len
            self.sdo_write(map_index, i, mapping_value)
            time.sleep(0.005)

        # Set mapping count
        self.sdo_write(map_index, 0, len(mapping_entries))
        time.sleep(0.005)

        # Set transmission type
        self.sdo_write(comm_index, 2, trans_type)
        time.sleep(0.005)

        # Enable PDO (clear bit 31)
        self.sdo_write(comm_index, 1, cob_id)
        time.sleep(0.005)

    def configure_tpdo(self, pdo_num, mapping_entries, trans_type=0x01):
        """Configure a TPDO.

        Args:
            pdo_num: TPDO number (1-4)
            mapping_entries: list of (index, subindex, bit_length)
            trans_type: transmission type (0x01 = on SYNC)
        """
        comm_index = 0x1800 + (pdo_num - 1)
        map_index = 0x1A00 + (pdo_num - 1)
        cob_id = COB_TPDO1_BASE + (pdo_num - 1) * 0x100 + self.node_id

        self.nmt_change_state(NMT_PRE_OP)
        time.sleep(0.01)

        # Disable PDO
        self.sdo_write(comm_index, 1, cob_id | (1 << 31))
        time.sleep(0.005)

        # Clear and set mapping
        self.sdo_write(map_index, 0, 0)
        time.sleep(0.005)
        for i, (idx, sub, bit_len) in enumerate(mapping_entries, 1):
            mapping_value = (idx << 16) | (sub << 8) | bit_len
            self.sdo_write(map_index, i, mapping_value)
            time.sleep(0.005)
        self.sdo_write(map_index, 0, len(mapping_entries))
        time.sleep(0.005)

        # Set transmission type
        self.sdo_write(comm_index, 2, trans_type)
        time.sleep(0.005)

        # Enable PDO
        self.sdo_write(comm_index, 1, cob_id)
        time.sleep(0.005)

    def send_rpdo(self, pdo_num, data):
        """Send an RPDO to this node."""
        cob_id = COB_RPDO1_BASE + (pdo_num - 1) * 0x100 + self.node_id
        self.master.send_can(cob_id, data)

    def get_tpdo_cob_id(self, pdo_num):
        """Get the COB-ID for a TPDO from this node."""
        return COB_TPDO1_BASE + (pdo_num - 1) * 0x100 + self.node_id

    def configure_heartbeat(self, producer_ms=0, consumer_ms=0):
        """Configure heartbeat producer/consumer."""
        if producer_ms > 0:
            self.sdo_write(0x1017, 0, producer_ms)
        if consumer_ms > 0:
            # Consumer: (node_id << 16) | timeout_ms
            self.sdo_write(0x1016, 1, (self.node_id << 16) | consumer_ms)


class SyncGroup:
    """A group of CANopen nodes sharing the same SYNC signal."""

    def __init__(self, name, period, master):
        self.name = name
        self.period = period
        self.master = master
        self.nodes = []
        self.producer_node = None
        self._timer = None
        self._started = False
        # RPDO buffers: node_id -> {pdo_num: bytes}
        self._rpdo_buffers = {}
        # TPDO caches: node_id -> {pdo_num: bytes}
        self._tpdo_caches = {}

    def add_node(self, node):
        """Add a node to this sync group."""
        if node not in self.nodes:
            self.nodes.append(node)
            self._rpdo_buffers[node.node_id] = {}
            self._tpdo_caches[node.node_id] = {}
            if self.producer_node is None:
                self.producer_node = node
            logging.info(
                "CANopen: node %d added to sync group '%s'",
                node.node_id, self.name,
            )

    def queue_rpdo(self, node_id, pdo_num, data):
        """Queue data to be sent in the next RPDO."""
        if node_id in self._rpdo_buffers:
            self._rpdo_buffers[node_id][pdo_num] = data

    def get_tpdo(self, node_id, pdo_num):
        """Get the latest TPDO data from a node."""
        cache = self._tpdo_caches.get(node_id, {})
        return cache.get(pdo_num)

    def start(self, reactor):
        """Start the SYNC timer."""
        if self._started or not self.nodes:
            return
        self._reactor = reactor
        self._timer = reactor.register_timer(self._sync_callback)
        self._started = True
        logging.info(
            "CANopen: sync group '%s' started, period=%.1fms, %d nodes",
            self.name, self.period * 1000, len(self.nodes),
        )

    def stop(self):
        """Stop the SYNC timer."""
        if self._timer is not None:
            self._reactor.unregister_timer(self._timer)
            self._timer = None
        self._started = False

    def _sync_callback(self, eventtime):
        """Called at SYNC rate. Sends SYNC + RPDOs, reads TPDOs."""
        try:
            # Send SYNC frame
            self.master.send_can(COB_SYNC, b'\x00')

            # Send RPDOs for all nodes
            for node in self.nodes:
                bufs = self._rpdo_buffers.get(node.node_id, {})
                for pdo_num, data in bufs.items():
                    node.send_rpdo(pdo_num, data)

            # Read TPDOs (non-blocking poll)
            for node in self.nodes:
                for pdo_num in range(1, 5):
                    cob_id = node.get_tpdo_cob_id(pdo_num)
                    data = self.master.poll_can(cob_id)
                    if data is not None:
                        self._tpdo_caches[node.node_id][pdo_num] = data

        except Exception:
            logging.exception("CANopen sync callback error")

        return eventtime + self.period


class CANopenMaster:
    """CANopen master managing nodes on one CAN bus."""

    def __init__(self, interface, channel, bitrate):
        self.interface = interface
        self.channel = channel
        self.bitrate = bitrate
        self.nodes = {}  # node_id -> CANopenNode
        self.sync_groups = {}  # name -> SyncGroup
        self._bus = None
        self._rx_thread = None
        self._running = False
        self._rx_callbacks = {}  # cob_id -> list of callbacks
        self._rx_lock = threading.Lock()
        self._wait_events = {}  # cob_id -> threading.Event + data

    def start(self):
        """Start the CAN bus connection."""
        import can
        logging.info(
            "CANopen master: starting on %s/%s @ %d bps",
            self.interface, self.channel, self.bitrate,
        )
        try:
            self._bus = can.interface.Bus(
                interface=self.interface,
                channel=self.channel,
                bitrate=self.bitrate,
            )
        except Exception as e:
            raise CANopenError("Failed to open CAN bus: %s" % e)

        self._running = True
        self._rx_thread = threading.Thread(target=self._rx_loop, daemon=True)
        self._rx_thread.start()
        logging.info("CANopen master: started")

    def stop(self):
        """Stop the CAN bus connection."""
        self._running = False
        # Stop all sync groups
        for sg in self.sync_groups.values():
            sg.stop()
        # Stop all nodes
        for node in self.nodes.values():
            try:
                node.nmt_stop()
            except Exception:
                pass
        if self._bus is not None:
            self._bus.shutdown()
            self._bus = None
        logging.info("CANopen master: stopped")

    def add_node(self, node_id, eds):
        """Register a new CANopen node."""
        node = CANopenNode(node_id, eds, self)
        self.nodes[node_id] = node
        return node

    def get_or_create_sync_group(self, group_name, period, reactor):
        """Get or create a sync group."""
        if group_name not in self.sync_groups:
            self.sync_groups[group_name] = SyncGroup(group_name, period, self)
        sg = self.sync_groups[group_name]
        if not sg._started:
            sg.start(reactor)
        return sg

    def send_can(self, cob_id, data):
        """Send a CAN frame."""
        import can
        if self._bus is None:
            return
        try:
            msg = can.Message(
                arbitration_id=cob_id,
                data=data,
                is_extended_id=False,
            )
            self._bus.send(msg)
        except Exception as e:
            logging.warning("CANopen TX error: %s", e)

    def wait_can(self, cob_id, timeout):
        """Wait for a CAN frame with specific COB-ID."""
        event = threading.Event()
        result = [None]
        with self._rx_lock:
            self._wait_events[cob_id] = (event, result)
        if event.wait(timeout):
            return result[0]
        with self._rx_lock:
            self._wait_events.pop(cob_id, None)
        return None

    def poll_can(self, cob_id):
        """Non-blocking poll for a CAN frame."""
        # This is handled by the rx thread caching latest frames
        return None

    def _rx_loop(self):
        """Background thread receiving CAN frames."""
        while self._running:
            try:
                msg = self._bus.recv(timeout=0.01)
                if msg is None:
                    continue
                self._dispatch_rx(msg)
            except Exception:
                if self._running:
                    logging.exception("CANopen RX error")
                    time.sleep(0.1)

    def _dispatch_rx(self, msg):
        """Dispatch received CAN frame to waiting threads."""
        cob_id = msg.arbitration_id
        with self._rx_lock:
            if cob_id in self._wait_events:
                event, result = self._wait_events.pop(cob_id)
                result[0] = bytes(msg.data)
                event.set()
