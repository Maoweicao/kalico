# External pulse generator stepper configuration for Kalico
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import logging

from klippy import stepper

from .pulse_gen_backend import (
    AbsolutePulseGenBackend,
    RelativePulseGenBackend,
    VelocityPulseGenBackend,
)
from ..rs485.transport import HostRS485Transport


class PulseGenStepper:
    """External pulse generator stepper motor configuration handler.

    Supports three command modes:
    - absolute: Send absolute position (like CSP)
    - relative: Send relative displacement (pulse count)
    - velocity: Send velocity command

    Communication uses the RS485 transport and protocol layers.
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.config = config
        self.name = config.get_name()

        # Transport configuration (reuse RS485 transport)
        serial_port = config.get("serial_port")
        baud_rate = config.getint("baud_rate", 9600,
                                   minval=1200, maxval=115200)
        parity = config.get("rs485_parity", "N")
        stopbits = config.getfloat("rs485_stopbits", 1)
        bytesize = config.getint("rs485_bytesize", 8)
        direction_pin = config.get("rs485_direction_pin", "rts")
        inter_byte_delay = config.getfloat("rs485_inter_byte_delay", 0)

        self._transport = HostRS485Transport(
            port=serial_port,
            baudrate=baud_rate,
            parity=parity,
            stopbits=stopbits,
            bytesize=bytesize,
            direction_pin=direction_pin,
            inter_byte_delay=inter_byte_delay,
        )

        # Protocol configuration
        protocol_type = config.get("pulse_gen_protocol", "modbus_rtu")
        slave_id = config.getint("pulse_gen_slave_id", 1,
                                  minval=1, maxval=247)

        if protocol_type == "modbus_rtu":
            from ..rs485.modbus_rtu import ModbusRtuProtocol
            self._protocol = ModbusRtuProtocol(
                self._transport, slave_id
            )
        elif protocol_type == "uart_passthrough":
            from ..rs485.uart_passthrough import UartPassthroughProtocol
            response_length = config.getint("pulse_gen_response_length", 0)
            self._protocol = UartPassthroughProtocol(
                self._transport, slave_id,
                response_length=response_length,
            )
        elif protocol_type == "custom":
            self._protocol = self._load_custom_protocol(config, slave_id)
        else:
            raise config.error(
                "Unknown pulse_gen_protocol '%s'. Options: modbus_rtu, "
                "uart_passthrough, custom" % protocol_type
            )

        # Command mode
        mode = config.get("pulse_gen_mode", "absolute").lower()

        # Stepper geometry
        rotation_dist, steps_per_rotation = stepper.parse_step_distance(config)
        self._rotation_dist = rotation_dist
        self._steps_per_rotation = steps_per_rotation
        self._step_dist = rotation_dist / steps_per_rotation

        # Register addresses
        reg_target = config.getint("register_target_position", 0x607A)
        reg_actual = config.getint("register_actual_position", 0x6064)
        reg_relative = config.getint("register_relative_position", 0x0020)
        reg_velocity = config.getint("register_velocity", 0x0030)

        # Create backend based on mode
        if mode == "absolute":
            self.backend = AbsolutePulseGenBackend(
                self._protocol, self._step_dist,
                reg_target=reg_target, reg_actual=reg_actual,
            )
        elif mode == "relative":
            self.backend = RelativePulseGenBackend(
                self._protocol, self._step_dist,
                reg_relative=reg_relative, reg_actual=reg_actual,
            )
        elif mode == "velocity":
            self.backend = VelocityPulseGenBackend(
                self._protocol, self._step_dist,
                reg_velocity=reg_velocity, reg_actual=reg_actual,
            )
        else:
            raise config.error(
                "Unknown pulse_gen_mode '%s'. Options: absolute, "
                "relative, velocity" % mode
            )

        # Create MCU_stepper with pulse gen backend
        self._mcu = self._get_or_create_mcu()
        fake_pin = {"chip": self._mcu, "pin": "pulse_gen_none",
                     "invert": False}
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

        # Shutdown handler
        self.printer.register_event_handler(
            "klippy:shutdown", self._handle_shutdown
        )

        logging.info(
            "PulseGen stepper '%s': slave=%d, protocol=%s, mode=%s",
            self.name, slave_id, protocol_type, mode,
        )

    def _get_or_create_mcu(self):
        printer = self.printer
        mcu_name = self.config.get("pulse_gen_mcu", "mcu")
        try:
            return printer.lookup_object("mcu %s" % mcu_name)
        except Exception:
            return printer.lookup_object("mcu")

    def _load_custom_protocol(self, config, slave_id):
        import importlib
        class_path = config.get("protocol_class")
        if not class_path:
            raise config.error(
                "pulse_gen_protocol: custom requires protocol_class"
            )
        if '.' in class_path:
            module_name, class_name = class_path.rsplit('.', 1)
        else:
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
    """Load a [pulse_gen_stepper] config section."""
    return PulseGenStepper(config)
