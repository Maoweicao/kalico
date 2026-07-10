# EtherCAT stepper configuration for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

from klippy import stepper

from .ethercat_backend import EtherCATBackend, EtherCATSlaveAdapter
from .ethercat_master import EtherCATMaster

# Global registry of EtherCAT masters (one per interface)
_global_masters = {}


def _get_or_create_master(config, interface, cycle_time):
    """Get or create an EtherCAT master for an interface."""
    key = (interface, cycle_time)
    if key not in _global_masters:
        master = EtherCATMaster(interface, cycle_time)
        _global_masters[key] = master
    return _global_masters[key]


class EtherCATStepper:
    """EtherCAT servo stepper motor configuration handler."""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.name = config.get_name()

        # EtherCAT configuration
        interface = config.get("ethercat_interface")
        slave_pos = config.getint("ethercat_slave", 0, minval=0)
        cycle_time = config.getfloat("ethercat_cycle_time", 0.001,
                                      minval=0.000250, maxval=0.020)

        # Operating mode
        mode_name = config.get("canopen_mode", "CSP").upper()
        from ..canopen.cia402 import MODE_CSP, MODE_CSV, MODE_HOMING, MODE_PP
        mode_map = {
            "PP": MODE_PP, "PV": 3, "CSP": MODE_CSP,
            "CSV": MODE_CSV, "CST": 10, "HOMING": MODE_HOMING,
        }
        mode = mode_map.get(mode_name)
        if mode is None:
            raise config.error(
                "Unknown EtherCAT mode '%s'. "
                "Supported: PP, PV, CSP, CSV, HOMING" % mode_name
            )

        # Create or get master (shared per interface)
        self._master = _get_or_create_master(config, interface, cycle_time)
        self._slave_pos = slave_pos
        self._mode = mode
        self._mode_name = mode_name

        # Stepper geometry
        rotation_dist, steps_per_rotation = stepper.parse_step_distance(config)
        self._rotation_dist = rotation_dist
        self._steps_per_rotation = steps_per_rotation
        self._step_dist = rotation_dist / steps_per_rotation

        # Slave, adapter, device, backend - created on connect
        self._slave = None
        self._adapter = None
        self._device = None
        self.backend = None
        self.stepper = None

        # Endstop
        self._endstop = None

        # ALM alarm pin support
        self._alm_pin = config.get("alm_pin", None)
        self._alm_action = config.get("alarm_action", "shutdown")
        self._alm_invert = config.getboolean("alm_invert", False)
        self._alarm_active = False
        self._alarm_count = 0

        if self._alm_pin:
            valid_actions = ("shutdown", "pause", "gcode", "none")
            if self._alm_action not in valid_actions:
                raise config.error(
                    "Invalid alarm_action '%s' in [%s]. Options: %s"
                    % (self._alm_action, self.name, ", ".join(valid_actions))
                )
            buttons = self.printer.load_object(config, "buttons")
            buttons.register_debounce_button(
                self._alm_pin, self._handle_alarm, config
            )
            # Register alarm query command
            gcode = self.printer.lookup_object("gcode")
            gcode.register_mux_command(
                "QUERY_SERVO_ALARM", "STEPPER", self.name,
                self.cmd_QUERY_SERVO_ALARM,
                desc="Query servo alarm state for %s" % self.name,
            )
            gcode.register_mux_command(
                "RESET_SERVO_ALARM", "STEPPER", self.name,
                self.cmd_RESET_SERVO_ALARM,
                desc="Reset servo alarm for %s" % self.name,
            )

        # Register connect handler
        self.printer.register_event_handler(
            "klippy:connect", self._handle_connect
        )
        self.printer.register_event_handler(
            "klippy:shutdown", self._handle_shutdown
        )

        logging.info(
            "EtherCAT stepper '%s': interface=%s, slave=%d, mode=%s, "
            "cycle_time=%.1fms",
            self.name, interface, slave_pos, mode_name, cycle_time * 1000,
        )

    def _handle_connect(self):
        """Called after all modules are loaded."""
        from ..canopen.cia402 import CiA402Device

        # Open master if not already started
        if not self._master.is_started():
            try:
                self._master.open()
            except Exception as e:
                logging.error(
                    "EtherCAT master open failed for '%s': %s",
                    self.name, e,
                )
                return

        # Get slave
        try:
            self._slave = self._master.get_slave(self._slave_pos)
        except Exception as e:
            logging.error(
                "EtherCAT slave %d not found for '%s': %s",
                self._slave_pos, self.name, e,
            )
            return

        # Create CiA 402 adapter and device
        self._adapter = EtherCATSlaveAdapter(self._slave)
        self._device = CiA402Device(self._adapter, self._mode)

        # Create backend
        cycle_time = self._master.get_cycle_time()
        self.backend = EtherCATBackend(
            self._slave, self._device, self._step_dist, cycle_time
        )

        # Create MCU_stepper with EtherCAT backend
        mcu = self._get_or_create_mcu()
        fake_pin = {"chip": mcu, "pin": "ethercat_none", "invert": False}
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
            m = self.printer.load_object(self.config, mname)
            m.register_stepper(self.config, self.stepper)

        # Handle endstop
        endstop_pin = self.config.get("endstop_pin", None)
        if endstop_pin:
            ppins = self.printer.lookup_object("pins")
            mcu_endstop = ppins.setup_pin("endstop", endstop_pin)
            mcu_endstop.add_stepper(self.stepper)
            self._endstop = mcu_endstop

            query_endstops = self.printer.load_object(
                self.config, "query_endstops"
            )
            endstop_name = " ".join(self.name.split()[1:])
            query_endstops.register_endstop(mcu_endstop, endstop_name)

        # Transition slaves to OP (done once for all slaves on this interface)
        if self._master.is_started():
            try:
                self._master.transition_to_op()
            except Exception as e:
                logging.error(
                    "EtherCAT OP transition failed for '%s': %s",
                    self.name, e,
                )
                return

        # Enable drive
        try:
            self._device.enable()
            logging.info(
                "EtherCAT stepper '%s': drive enabled (slave %d)",
                self.name, self._slave_pos,
            )
        except Exception as e:
            logging.error(
                "EtherCAT: failed to enable slave %d for '%s': %s",
                self._slave_pos, self.name, e,
            )

    def _get_or_create_mcu(self):
        printer = self.printer
        mcu_name = self.config.get("ethercat_mcu", "mcu")
        try:
            return printer.lookup_object("mcu %s" % mcu_name)
        except Exception:
            return printer.lookup_object("mcu")

    def _handle_shutdown(self):
        if self._device is not None:
            try:
                self._device.disable()
            except Exception:
                pass

    def _handle_alarm(self, eventtime, state):
        """Called when ALM pin state changes."""
        alarmed = bool(state) != self._alm_invert
        if alarmed == self._alarm_active:
            return
        self._alarm_active = alarmed
        if alarmed:
            self._alarm_count += 1
            logging.error(
                "EtherCAT stepper '%s': ALARM TRIGGERED (count=%d)",
                self.name, self._alarm_count,
            )
            self._execute_alarm_action(eventtime)
        else:
            logging.info(
                "EtherCAT stepper '%s': alarm cleared", self.name
            )

    def _execute_alarm_action(self, eventtime):
        """Execute the configured alarm action."""
        if self._alm_action == "shutdown":
            self.printer.invoke_shutdown(
                "Servo ALM alarm on %s" % self.name
            )
        elif self._alm_action == "pause":
            try:
                print_stats = self.printer.lookup_object("print_stats")
                if print_stats.get_status()["state"] == "printing":
                    gcode = self.printer.lookup_object("gcode")
                    gcode.run_script_from_command("PAUSE")
            except Exception as e:
                logging.error(
                    "EtherCAT stepper '%s': pause failed: %s",
                    self.name, e,
                )
                self.printer.invoke_shutdown(
                    "Servo ALM alarm on %s (pause failed)" % self.name
                )

    def cmd_QUERY_SERVO_ALARM(self, gcmd):
        """Query alarm state."""
        if self._alarm_active:
            msg = "Servo %s: ALARM ACTIVE (count=%d)" % (
                self.name, self._alarm_count
            )
        else:
            msg = "Servo %s: OK" % self.name
        gcmd.respond_info(msg)

    def cmd_RESET_SERVO_ALARM(self, gcmd):
        """Reset alarm state and try to reset drive fault."""
        self._alarm_active = False
        if self._device is not None:
            try:
                if self._device.is_fault():
                    self._device.fault_reset()
                    gcmd.respond_info(
                        "Servo %s: fault reset OK" % self.name
                    )
                else:
                    gcmd.respond_info(
                        "Servo %s: alarm cleared (no drive fault)" % self.name
                    )
            except Exception as e:
                gcmd.respond_info(
                    "Servo %s: fault reset failed: %s" % (self.name, e)
                )
        else:
            gcmd.respond_info(
                "Servo %s: alarm cleared (device not initialized)" % self.name
            )

    def get_stepper(self):
        return self.stepper

    def get_status(self, eventtime=None):
        if self.backend is not None:
            status = self.backend.get_status()
        else:
            status = {"state": "not_initialized"}
        status["alarm_active"] = self._alarm_active
        status["alarm_count"] = self._alarm_count
        return status


def load_config_prefix(config):
    """Load an [ethercat_stepper] config section."""
    return EtherCATStepper(config)
