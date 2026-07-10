# RS485 stepper configuration for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import importlib
import logging
import os

from klippy import stepper

from .rs485_backend import RS485Backend
from .transport import HostRS485Transport


class RS485Stepper:
    """RS485 servo stepper motor configuration handler."""

    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.name = config.get_name()

        # Transport configuration
        transport_type = config.get("rs485_transport", "host")
        serial_port = config.get("serial_port")
        baud_rate = config.getint("baud_rate", 9600,
                                   minval=1200, maxval=115200)
        parity = config.get("rs485_parity", "N")
        stopbits = config.getfloat("rs485_stopbits", 1)
        bytesize = config.getint("rs485_bytesize", 8)
        direction_pin = config.get("rs485_direction_pin", "rts")
        inter_byte_delay = config.getfloat("rs485_inter_byte_delay", 0)

        if transport_type == "host":
            self._transport = HostRS485Transport(
                port=serial_port,
                baudrate=baud_rate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                direction_pin=direction_pin,
                inter_byte_delay=inter_byte_delay,
            )
        elif transport_type == "mcu":
            from .transport import McuRS485Transport
            raise config.error(
                "MCU-side RS485 transport not yet implemented. "
                "Use rs485_transport: host."
            )
        else:
            raise config.error(
                "Unknown rs485_transport '%s'. Options: host, mcu"
                % transport_type
            )

        # Protocol configuration
        protocol_type = config.get("rs485_protocol", "modbus_rtu")
        slave_id = config.getint("rs485_slave_id", 1, minval=1, maxval=247)

        if protocol_type == "modbus_rtu":
            from .modbus_rtu import ModbusRtuProtocol
            register_map = self._parse_register_map(config)
            response_delay = config.getfloat("rs485_response_delay", None)
            inter_frame_delay = config.getfloat("rs485_inter_frame_delay", None)
            self._protocol = ModbusRtuProtocol(
                transport=self._transport,
                slave_id=slave_id,
                register_map=register_map,
                response_delay=response_delay,
                inter_frame_delay=inter_frame_delay,
            )
        elif protocol_type == "uart_passthrough":
            from .uart_passthrough import UartPassthroughProtocol
            response_length = config.getint("rs485_response_length", 0)
            self._protocol = UartPassthroughProtocol(
                transport=self._transport,
                slave_id=slave_id,
                response_length=response_length,
            )
        elif protocol_type == "custom":
            self._protocol = self._load_custom_protocol(config, slave_id)
        else:
            raise config.error(
                "Unknown rs485_protocol '%s'. Options: modbus_rtu, "
                "uart_passthrough, custom" % protocol_type
            )

        # Stepper geometry
        rotation_dist, steps_per_rotation = stepper.parse_step_distance(config)
        self._rotation_dist = rotation_dist
        self._steps_per_rotation = steps_per_rotation
        self._step_dist = rotation_dist / steps_per_rotation

        # Create RS485 backend
        self.backend = RS485Backend(self._protocol, self._step_dist)

        # Create MCU_stepper with RS485 backend
        self._mcu = self._get_or_create_mcu()
        fake_pin = {"chip": self._mcu, "pin": "rs485_none", "invert": False}
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
        endstop_pin = config.get("endstop_pin", None)
        if endstop_pin:
            ppins = self.printer.lookup_object("pins")
            mcu_endstop = ppins.setup_pin("endstop", endstop_pin)
            mcu_endstop.add_stepper(self.stepper)
            self._endstop = mcu_endstop

            query_endstops = self.printer.load_object(config, "query_endstops")
            endstop_name = " ".join(self.name.split()[1:])
            query_endstops.register_endstop(mcu_endstop, endstop_name)

        # Register shutdown handler
        self.printer.register_event_handler(
            "klippy:shutdown", self._handle_shutdown
        )

        logging.info(
            "RS485 stepper '%s': slave=%d, protocol=%s, transport=%s",
            self.name, slave_id, protocol_type, transport_type,
        )

    def _get_or_create_mcu(self):
        printer = self.printer
        mcu_name = self.config.get("rs485_mcu", "mcu")
        try:
            return printer.lookup_object("mcu %s" % mcu_name)
        except Exception:
            return printer.lookup_object("mcu")

    def _parse_register_map(self, config):
        """Parse optional custom register map from config."""
        register_map = {}
        for key in ("control_word", "status_word", "target_position",
                     "actual_position", "error_code", "mode_of_operation",
                     "mode_of_operation_display"):
            full_key = "register_" + key
            val = config.getint(full_key, None)
            if val is not None:
                register_map[key] = val
        return register_map if register_map else None

    def _load_custom_protocol(self, config, slave_id):
        """Load a custom protocol class from config."""
        class_path = config.get("protocol_class")
        if not class_path:
            raise config.error(
                "rs485_protocol: custom requires protocol_class"
            )

        # Try loading as module.ClassName
        if '.' in class_path:
            module_name, class_name = class_path.rsplit('.', 1)
        else:
            # Look in klippy.extras namespace
            module_name = "klippy.extras." + class_path
            class_name = class_path.split('.')[-1]

        try:
            mod = importlib.import_module(module_name)
            cls = getattr(mod, class_name)
        except (ImportError, AttributeError) as e:
            raise config.error(
                "Failed to load custom protocol '%s': %s" % (class_path, e)
            )

        return cls(self._transport, slave_id)

    def _handle_shutdown(self):
        try:
            self.backend.close()
        except Exception:
            pass

    def get_stepper(self):
        return self.stepper

    def get_status(self, eventtime=None):
        return self.backend.get_status()


def load_config_prefix(config):
    """Load a [rs485_stepper] config section."""
    return RS485Stepper(config)
