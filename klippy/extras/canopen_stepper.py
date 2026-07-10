# CANopen stepper configuration for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging
import os

from klippy import stepper

from . import cia402, eds_parser
from .canopen_backend import CANopenBackend
from .canopen_master import CANopenMaster

# Global registry of CANopen masters (one per bus)
_global_masters = {}


def _get_or_create_master(config, bus_section):
    """Get or create a CANopen master for a bus configuration."""
    if bus_section:
        # Reference to a [canopen_bus] section
        printer = config.get_printer()
        bus_config = config.getsection(bus_section)
        interface = bus_config.get("interface")
        channel = bus_config.get("channel")
        bitrate = bus_config.getint("bitrate", 1000000)
    else:
        # Direct configuration
        interface = config.get("can_interface")
        channel = config.get("can_channel")
        bitrate = config.getint("can_bitrate", 1000000)

    key = (interface, channel, bitrate)
    if key not in _global_masters:
        master = CANopenMaster(interface, channel, bitrate)
        _global_masters[key] = master
    return _global_masters[key]


class CANopenStepper:
    """CANopen stepper motor configuration handler."""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.name = config.get_name()

        # Parse configuration
        bus_section = config.get("canopen_bus", None)
        node_id = config.getint("node_id", minval=1, maxval=127)
        eds_path = config.get("eds_file")
        mode_name = config.get("canopen_mode", "CSP").upper()
        sync_group_name = config.get("sync_group", "default")
        sync_period = config.getfloat("sync_period", 0.001,
                                       minval=0.000250, maxval=0.010)

        # Resolve EDS path
        if eds_path.startswith("~/"):
            eds_path = os.path.expanduser(eds_path)
        elif not os.path.isabs(eds_path):
            # Relative to config directory
            config_dir = os.path.dirname(config.get_printer().get_start_args().get(
                "config_file", "."
            ))
            eds_path = os.path.join(config_dir, eds_path)

        # Load EDS
        self.eds = eds_parser.EDSFile(eds_path)

        # Get operating mode
        mode_map = {
            "PP": cia402.MODE_PP,
            "PV": cia402.MODE_PV,
            "CSP": cia402.MODE_CSP,
            "CSV": cia402.MODE_CSV,
            "CST": cia402.MODE_CST,
            "HOMING": cia402.MODE_HOMING,
        }
        mode = mode_map.get(mode_name)
        if mode is None:
            raise config.error(
                "Unknown CANopen mode '%s' in %s. "
                "Supported: PP, PV, CSP, CSV, CST, HOMING"
                % (mode_name, self.name)
            )

        # Create CANopen master (shared per bus)
        self.master = _get_or_create_master(config, bus_section)

        # Create node
        self.node = self.master.add_node(node_id, self.eds)

        # Create CiA 402 device
        self.device = cia402.CiA402Device(self.node, mode)

        # Get sync group
        self.sync_group_name = sync_group_name
        self.sync_period = sync_period
        self._sync_group = None  # Created on connect

        # Stepper geometry (required by framework)
        rotation_dist, steps_per_rotation = stepper.parse_step_distance(config)
        self._rotation_dist = rotation_dist
        self._steps_per_rotation = steps_per_rotation
        self._step_dist = rotation_dist / steps_per_rotation

        # Create CANopen backend
        self.backend = CANopenBackend(
            self.node, self.device, None, self._step_dist
        )

        # Create MCU_stepper with CANopen backend
        # Need a fake MCU for the framework
        self._mcu = self._get_or_create_mcu()
        fake_pin = {"chip": self._mcu, "pin": "canopen_none", "invert": False}
        self.stepper = stepper.MCU_stepper(
            self.name,
            fake_pin,
            fake_pin,
            self._rotation_dist,
            self._steps_per_rotation,
            backend=self.backend,
        )

        # Register with helper modules
        for mname in ["stepper_enable", "force_move", "motion_report"]:
            m = self.printer.load_object(config, mname)
            m.register_stepper(config, self.stepper)

        # Handle endstop
        self._endstop = None
        self._canopen_endstop = None
        endstop_pin = config.get("endstop_pin", None)
        if endstop_pin and endstop_pin.lower() == "canopen":
            # CiA 402 homing mode endstop
            from .canopen.canopen_backend import CANopenEndstop
            self._canopen_endstop = CANopenEndstop(
                self.device, self.backend, self._mcu
            )
            # Parse homing configuration
            method_name = config.get("canopen_homing_method", "negative_limit")
            homing_method = self._parse_homing_method(method_name)
            speed_switch = config.getint("canopen_homing_speed_switch", None)
            speed_zero = config.getint("canopen_homing_speed_zero", None)
            homing_accel = config.getint("canopen_homing_accel", None)
            homing_offset = config.getint("canopen_homing_offset", 0)
            self._canopen_endstop.configure(
                method=homing_method,
                speed_switch=speed_switch,
                speed_zero=speed_zero,
                accel=homing_accel,
                offset=homing_offset,
            )
            self._canopen_endstop.add_stepper(self.stepper)
            self._endstop = self._canopen_endstop

            # Register with query_endstops
            query_endstops = self.printer.load_object(config, "query_endstops")
            endstop_name = " ".join(self.name.split()[1:])
            query_endstops.register_endstop(self._canopen_endstop, endstop_name)

        elif endstop_pin:
            # Traditional MCU GPIO endstop
            ppins = self.printer.lookup_object("pins")
            mcu_endstop = ppins.setup_pin("endstop", endstop_pin)
            mcu_endstop.add_stepper(self.stepper)
            self._endstop = mcu_endstop

            # Register with query_endstops
            query_endstops = self.printer.load_object(config, "query_endstops")
            endstop_name = " ".join(self.name.split()[1:])
            query_endstops.register_endstop(mcu_endstop, endstop_name)

        # Register connect handler
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        self.printer.register_event_handler(
            "klippy:shutdown", self._handle_shutdown
        )

        logging.info(
            "CANopen stepper '%s': node=%d, mode=%s, sync_group=%s",
            self.name, node_id, mode_name, sync_group_name,
        )

    def _get_or_create_mcu(self):
        """Get or create a virtual MCU for CANopen steppers."""
        # Use the primary MCU for endstop support
        # The CANopen backend doesn't actually use MCU step generation
        printer = self.printer
        mcu_name = self.config.get("canopen_mcu", "mcu")
        try:
            return printer.lookup_object("mcu %s" % mcu_name)
        except Exception:
            return printer.lookup_object("mcu")

    @staticmethod
    def _parse_homing_method(name):
        """Parse homing method name to CiA 402 method number."""
        from .canopen import cia402
        methods = {
            "current_position": cia402.HOMING_METHOD_CURRENT_POS,
            "positive_limit": cia402.HOMING_METHOD_POS_LIMIT,
            "negative_limit": cia402.HOMING_METHOD_NEG_LIMIT,
            "positive_home": cia402.HOMING_METHOD_POS_HOME,
            "negative_home": cia402.HOMING_METHOD_NEG_HOME,
            "positive_home_index": cia402.HOMING_METHOD_POS_HOME_INDEX,
            "negative_home_index": cia402.HOMING_METHOD_NEG_HOME_INDEX,
            "negative_limit_index": cia402.HOMING_METHOD_NEG_LIMIT_INDEX,
            "positive_limit_index": cia402.HOMING_METHOD_POS_LIMIT_INDEX,
            "index_positive": cia402.HOMING_METHOD_INDEX_POS,
            "index_negative": cia402.HOMING_METHOD_INDEX_NEG,
        }
        method = methods.get(name.lower())
        if method is None:
            # Try as integer
            try:
                method = int(name)
            except ValueError:
                raise ValueError(
                    "Unknown homing method '%s'. "
                    "Supported: %s" % (name, ", ".join(methods.keys()))
                )
        return method

    def _handle_connect(self):
        """Called after all modules are loaded."""
        reactor = self.printer.get_reactor()

        # Start CANopen master if not already started
        if self.master._bus is None:
            try:
                self.master.start()
            except Exception as e:
                logging.error(
                    "CANopen master start failed for '%s': %s",
                    self.name, e,
                )
                return

        # Create/get sync group
        self._sync_group = self.master.get_or_create_sync_group(
            self.sync_group_name, self.sync_period, reactor
        )
        self._sync_group.add_node(self.node)
        self.backend._sync_group = self._sync_group

        # Start node
        self.node.nmt_change_state(0x80)  # PRE-OPERATIONAL
        import time
        time.sleep(0.05)

        # Configure PDO mapping
        self.device.configure_default_pdo_mapping()

        # Enable drive
        try:
            self.device.enable()
        except Exception as e:
            logging.error(
                "CANopen: failed to enable node %d for '%s': %s",
                self.node.node_id, self.name, e,
            )

        # Switch to OPERATIONAL
        self.node.nmt_start()

    def _handle_shutdown(self):
        """Called on printer shutdown."""
        try:
            self.device.disable()
        except Exception:
            pass

    def get_stepper(self):
        return self.stepper

    def get_status(self, eventtime=None):
        return self.backend.get_status()


class CANopenBus:
    """CANopen bus configuration (shared by multiple steppers)."""

    def __init__(self, config):
        self.interface = config.get("interface")
        self.channel = config.get("channel")
        self.bitrate = config.getint("bitrate", 1000000)
        logging.info(
            "CANopen bus '%s': %s/%s @ %d bps",
            config.get_name(), self.interface, self.channel, self.bitrate,
        )


def load_config_prefix(config):
    """Load a [canopen_stepper] config section."""
    return CANopenStepper(config)


def load_config(config):
    """Load a [canopen_bus] config section."""
    return CANopenBus(config)
