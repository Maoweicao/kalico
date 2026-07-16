# Generic digital input pin handling
#
# Copyright (C) 2024  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import logging

PIN_MIN_TIME = 0.100


class MCU_input_pin:
    def __init__(self, mcu, pin_params):
        self._mcu = mcu
        self._pin = pin_params["pin"]
        self._pullup = pin_params["pullup"]
        self._invert = pin_params["invert"]
        self._oid = self._mcu.create_oid()
        self._query_cmd = None
        self._last_value = None
        self._mcu.register_config_callback(self._build_config)

    def get_mcu(self):
        return self._mcu

    def _build_config(self):
        self._mcu.add_config_cmd(
            "config_endstop oid=%d pin=%s pull_up=%d"
            % (self._oid, self._pin, 1 if self._pullup else 0)
        )
        self._mcu.add_config_cmd(
            "endstop_home oid=%d clock=0 sample_ticks=0 sample_count=0"
            " rest_ticks=0 pin_value=0 trsync_oid=0 trigger_reason=0"
            % (self._oid,),
            on_restart=True,
        )
        cmd_queue = self._mcu.alloc_command_queue()
        self._query_cmd = self._mcu.lookup_query_command(
            "endstop_query_state oid=%c",
            "endstop_state oid=%c homing=%c next_clock=%u pin_value=%c",
            oid=self._oid,
            cq=cmd_queue,
        )

    def query(self, print_time=None):
        if self._mcu.is_fileoutput():
            return 0
        if print_time is not None:
            clock = self._mcu.print_time_to_clock(print_time)
            params = self._query_cmd.send([self._oid], minclock=clock)
        else:
            params = self._query_cmd.send([self._oid])
        self._last_value = params["pin_value"] ^ self._invert
        return self._last_value

    def get_last_value(self):
        return self._last_value


class PrinterInputPin:
    def __init__(self, config):
        self.printer = config.get_printer()
        ppins = self.printer.lookup_object("pins")
        pin_desc = config.get("pin")
        self.mcu_pin = ppins.setup_pin("endstop", pin_desc)
        self.name = config.get_name().split()[1]
        self.poll_interval = config.getfloat(
            "poll_interval", 0.5, minval=0.05, maxval=5.0
        )
        self._poll_timer = None
        self._last_value = None
        gcode = self.printer.lookup_object("gcode")
        gcode.register_mux_command(
            "QUERY_INPUT_PIN",
            "PIN",
            self.name,
            self.cmd_QUERY_INPUT_PIN,
            desc=self.cmd_QUERY_INPUT_PIN_help,
        )
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.printer.register_event_handler(
            "klippy:disconnect", self._handle_disconnect
        )

    def _handle_ready(self):
        self._reactor = self.printer.get_reactor()
        self._start_polling()

    def _handle_disconnect(self):
        self._stop_polling()

    def _start_polling(self):
        if self.poll_interval <= 0 or self._poll_timer is not None:
            return
        self._poll_timer = self._reactor.register_timer(
            self._poll_event, self._reactor.NOW
        )

    def _stop_polling(self):
        if self._poll_timer is not None:
            self._reactor.unregister_timer(self._poll_timer)
            self._poll_timer = None

    def _poll_event(self, eventtime):
        try:
            self._last_value = self.mcu_pin.query()
        except Exception:
            logging.exception("input_pin: query failed")
        return eventtime + self.poll_interval

    def get_status(self, eventtime):
        return {"value": self._last_value}

    cmd_QUERY_INPUT_PIN_help = "Query the state of a digital input pin"

    def cmd_QUERY_INPUT_PIN(self, gcmd):
        value = self.mcu_pin.query()
        self._last_value = value
        state = "HIGH" if value else "LOW"
        gcmd.respond_info(
            'Input pin "%s" value: %s (%d)' % (self.name, state, value)
        )


def load_config_prefix(config):
    return PrinterInputPin(config)
