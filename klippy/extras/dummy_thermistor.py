# Dummy thermistor sensor for testing and development
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging

DUMMY_REPORT_TIME = 1.0


class DummyThermistor:
    """Fixed-temperature dummy sensor for testing and development.
    
    Similar to Marlin's dummy thermistor tables 998/999, this provides
    a constant temperature reading without requiring a physical sensor.
    Useful for:
    - Testing printer configurations without hardware
    - Clay/cold extruders that don't need temperature monitoring
    - Development and debugging
    """

    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name().split()[-1]
        self.temp = config.getfloat("temperature", 25.0, minval=-273.15)
        self.min_temp = -273.15
        self.max_temp = 9999.0
        self.is_active = True
        
        # Register as printer object
        self.printer.add_object("temperature_sensor " + self.name, self)
        
        # Register for events
        self.printer.register_event_handler(
            "klippy:connect", self.handle_connect
        )
        
        # Register G-code command for dynamic temperature control
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "SET_DUMMY_TEMPERATURE",
            "SENSOR",
            self.name,
            self.cmd_SET_DUMMY_TEMPERATURE,
            desc=self.cmd_SET_DUMMY_TEMPERATURE_help,
        )

    def handle_connect(self):
        if self.is_active:
            self.sample_timer = self.reactor.register_timer(
                self._sample_temperature
            )
            self.reactor.update_timer(self.sample_timer, self.reactor.NOW)

    def setup_minmax(self, min_temp, max_temp):
        self.min_temp = min_temp
        self.max_temp = max_temp

    def setup_callback(self, cb):
        self._callback = cb

    def get_report_time_delta(self):
        return DUMMY_REPORT_TIME

    def _sample_temperature(self, eventtime):
        if not self.is_active:
            return self.reactor.NEVER
            
        mcu = self.printer.lookup_object("mcu")
        measured_time = self.reactor.monotonic()
        self._callback(mcu.estimated_print_time(measured_time), self.temp)
        return measured_time + DUMMY_REPORT_TIME

    def get_status(self, eventtime):
        return {
            "temperature": round(self.temp, 2),
            "is_active": self.is_active,
        }

    cmd_SET_DUMMY_TEMPERATURE_help = "Set dummy sensor temperature"

    def cmd_SET_DUMMY_TEMPERATURE(self, gcmd):
        """Set the temperature reported by this dummy sensor.
        
        Usage: SET_DUMMY_TEMPERATURE SENSOR=<name> [TEMPERATURE=<value>]
        
        If TEMPERATURE is not provided, reports current temperature.
        """
        new_temp = gcmd.get_float("TEMPERATURE", None)
        if new_temp is not None:
            self.temp = new_temp
            gcmd.respond_info(
                "Dummy sensor '%s' temperature set to %.2f°C"
                % (self.name, self.temp)
            )
        else:
            gcmd.respond_info(
                "Dummy sensor '%s' temperature: %.2f°C"
                % (self.name, self.temp)
            )


def load_config(config):
    # Register sensor factory
    pheaters = config.get_printer().load_object(config, "heaters")
    pheaters.add_sensor_factory("dummy_thermistor", DummyThermistor)
