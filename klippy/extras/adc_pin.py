# Generic analog input (ADC) pin handling
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.


class PrinterADCPin:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object("pins")
        pin_desc = config.get("pin")
        self.name = config.get_name().split()[1]
        self.mcu_adc = ppins.setup_pin("adc", pin_desc)
        sample_time = config.getfloat("sample_time", 0.001, above=0.0)
        sample_count = config.getint("sample_count", 8, minval=1, maxval=255)
        report_time = config.getfloat("report_time", 0.015, above=0.0)
        min_value = config.getfloat("min_value", 0.0)
        max_value = config.getfloat("max_value", 1.0, above=min_value)
        range_check_count = config.getint("range_check_count", 0, minval=0)
        self.mcu_adc.setup_minmax(
            sample_time,
            sample_count,
            minval=min_value,
            maxval=max_value,
            range_check_count=range_check_count,
        )
        query_adc = self.printer.load_object(config, "query_adc")
        query_adc.register_adc(self.name, self.mcu_adc)
        self._last_value = 0.0
        self._last_read_time = 0.0
        self.mcu_adc.setup_adc_callback(report_time, self._adc_callback)
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "QUERY_ADC_PIN",
            "PIN",
            self.name,
            self.cmd_QUERY_ADC_PIN,
            desc=self.cmd_QUERY_ADC_PIN_help,
        )

    def _adc_callback(self, read_time, read_value):
        self._last_value = read_value
        self._last_read_time = read_time

    def get_status(self, eventtime):
        return {
            "value": self._last_value,
            "read_time": self._last_read_time,
        }

    cmd_QUERY_ADC_PIN_help = "Query the value of an analog input pin"

    def cmd_QUERY_ADC_PIN(self, gcmd):
        value, timestamp = self.mcu_adc.get_last_value()
        gcmd.respond_info(
            'ADC pin "%s" value: %.6f (timestamp %.3f)'
            % (self.name, value, timestamp)
        )


def load_config_prefix(config):
    return PrinterADCPin(config)
