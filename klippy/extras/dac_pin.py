# Analog output (DAC) pin handling via PWM
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

PIN_MIN_TIME = 0.100
MAX_SCHEDULE_TIME = 5.0


class PrinterDACPin:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object("pins")
        self.name = config.get_name().split()[1]
        pin_desc = config.get("pin")
        self.mcu_pin = ppins.setup_pin("pwm", pin_desc)
        cycle_time = config.getfloat(
            "cycle_time", 0.100, above=0.0, maxval=MAX_SCHEDULE_TIME
        )
        hardware_pwm = config.getboolean("hardware_pwm", False)
        self.mcu_pin.setup_cycle_time(cycle_time, hardware_pwm)
        self.scale = config.getfloat("scale", 3.3, above=0.0)
        self.mcu_pin.setup_max_duration(0.0)
        self.last_value = (
            config.getfloat("value", 0.0, minval=0.0, maxval=self.scale)
            / self.scale
        )
        self.shutdown_value = (
            config.getfloat(
                "shutdown_value", 0.0, minval=0.0, maxval=self.scale
            )
            / self.scale
        )
        self.mcu_pin.setup_start_value(self.last_value, self.shutdown_value)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "SET_DAC_PIN",
            "PIN",
            self.name,
            self.cmd_SET_DAC_PIN,
            desc=self.cmd_SET_DAC_PIN_help,
        )

    def get_status(self, eventtime):
        return {"value": self.last_value * self.scale}

    def _set_pin(self, value):
        value = max(0.0, min(1.0, value / self.scale))
        self.last_value = value
        systime = self.printer.get_reactor().monotonic()
        print_time = self.mcu_pin.get_mcu().estimated_print_time(
            systime + PIN_MIN_TIME
        )
        self.mcu_pin.set_pwm(print_time, value)

    cmd_SET_DAC_PIN_help = "Set the value of a DAC output pin"

    def cmd_SET_DAC_PIN(self, gcmd):
        value = gcmd.get_float("VALUE", minval=0.0, maxval=self.scale)
        self._set_pin(value)
        gcmd.respond_info(
            'DAC pin "%s" value: %.3fV' % (self.name, value)
        )


def load_config_prefix(config):
    return PrinterDACPin(config)
