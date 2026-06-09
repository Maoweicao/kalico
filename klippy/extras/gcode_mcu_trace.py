# G-code to MCU command tracing and recording module
#
# Provides one-to-one tracing of gcode commands and their corresponding
# MCU指令, with support for recording and replay.
#
# Copyright (C) 2024 Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.
import json
import logging
import os
import re
import threading
import time

from .. import queuelogger

TRACER = None
_replay_mode = False
_replay_state = {"recording": False, "replaying": False}
_replay_lock = threading.Lock()


def get_tracer():
    return TRACER


def is_replaying():
    with _replay_lock:
        return _replay_state["replaying"]


class GCodeMCUTacer:
    def __init__(self, config):
        global TRACER
        TRACER = self
        self.printer = config.get_printer()
        self._enabled = False
        self._log_dir = None
        self._danger_opts = None
        self._gcode_cb = None
        self._mcu_cmd_cb = None
        self._mcu_resp_cb = None
        self._mcu_ack_cb = None
        self._virtual_sd = None
        self._print_stats = None
        self._reactor = self.printer.get_reactor()
        self._pending_mcu_cmds = []
        self._cmd_lock = threading.Lock()
        try:
            self._danger_opts = self.printer.lookup_object("danger_options")
            danger_opts = self._danger_opts
            self._log_gcode = danger_opts.log_gcode_mcu_trace
            self._log_mcu_commands = danger_opts.log_mcu_commands
            self._log_mcu_responses = danger_opts.log_mcu_responses
            self._log_mcu_execution = danger_opts.log_mcu_execution_status
        except:
            self._log_gcode = False
            self._log_mcu_commands = False
            self._log_mcu_responses = False
            self._log_mcu_execution = False
        self.printer.register_event_handler(
            "virtual_sdcard:load_file", self._on_load_file
        )
        self.printer.register_event_handler(
            "print_stats:start_printing", self._on_print_start
        )
        self.printer.register_event_handler(
            "print_stats:complete_printing", self._on_print_end
        )
        self.printer.register_event_handler(
            "print_stats:error_printing", self._on_print_end
        )
        self.printer.register_event_handler(
            "print_stats:cancelled_printing", self._on_print_end
        )
        self.printer.register_event_handler(
            "print_stats:paused_printing", self._on_print_pause
        )
        self.printer.register_event_handler(
            "klippy:shutdown", self._on_shutdown
        )
        self._register_gcode_handlers()
        self._apply_hooks()

    def _register_gcode_handlers(self):
        self.gcode = self.printer.lookup_object("gcode")
        self.gcode.register_command(
            "MCU_RECORD_START", self.cmd_MCU_RECORD_START,
            desc=self.cmd_MCU_RECORD_START_help
        )
        self.gcode.register_command(
            "MCU_RECORD_STOP", self.cmd_MCU_RECORD_STOP,
            desc=self.cmd_MCU_RECORD_STOP_help
        )
        self.gcode.register_command(
            "MCU_REPLAY", self.cmd_MCU_REPLAY,
            desc=self.cmd_MCU_REPLAY_help
        )
        self.gcode.register_command(
            "MCU_TRACE_STATUS", self.cmd_MCU_TRACE_STATUS,
            desc=self.cmd_MCU_TRACE_STATUS_help
        )

    cmd_MCU_RECORD_START_help = (
        "Start recording MCU commands for later replay. "
        "Usage: MCU_RECORD_START [DURATION=seconds]"
    )

    def cmd_MCU_RECORD_START(self, gcmd):
        duration = gcmd.get_float("DURATION", 0.0, minval=0.0)
        with _replay_lock:
            if _replay_state["recording"]:
                gcmd.respond_raw("Already recording")
                return
            _replay_state["recording"] = True
        queuelogger.start_trace_session("_manual_record")
        gcmd.respond_raw(
            "MCU command recording started (duration=%.1fs)" % (
                duration if duration > 0 else float('inf')
            )
        )
        if duration > 0:
            self.printer.get_reactor().register_callback(
                lambda e: self._stop_recording()
            )

    def _stop_recording(self):
        with _replay_lock:
            if not _replay_state["recording"]:
                return
            _replay_state["recording"] = False
        queuelogger.end_trace_session()

    cmd_MCU_RECORD_STOP_help = "Stop recording MCU commands"

    def cmd_MCU_RECORD_STOP(self, gcmd):
        with _replay_lock:
            if not _replay_state["recording"]:
                gcmd.respond_raw("Not currently recording")
                return
            _replay_state["recording"] = False
        queuelogger.end_trace_session()
        gcmd.respond_raw("MCU command recording stopped")

    cmd_MCU_REPLAY_help = (
        "Replay previously recorded MCU commands from a trace file. "
        "Usage: MCU_REPLAY FILE= [SEND=0] [SPEED=1.0] [FILTER=<msg_name_pattern>]"
    )

    def cmd_MCU_REPLAY(self, gcmd):
        filename = gcmd.get("FILE")
        if not filename:
            raise gcmd.error("FILE parameter is required")
        send = gcmd.get_int("SEND", 0, minval=0, maxval=1)
        speed = gcmd.get_float("SPEED", 1.0, minval=0.01, maxval=1000.0)
        filter_pat = gcmd.get("FILTER", None)
        try:
            with open(filename, "r", encoding="utf-8") as f:
                events = [json.loads(line) for line in f if line.strip()]
        except Exception as e:
            raise gcmd.error("Failed to read file: %s" % (str(e),))
        self._do_replay(gcmd, events, send, speed, filter_pat)

    def _do_replay(self, gcmd, events, send, speed, filter_pat):
        if send:
            vsd = None
            try:
                vsd = self.printer.lookup_object("virtual_sdcard")
            except:
                pass
            if vsd and vsd.is_active():
                raise gcmd.error("Cannot replay with SEND=1 while printing")
        with _replay_lock:
            if _replay_state["replaying"]:
                raise gcmd.error("Already replaying")
            _replay_state["replaying"] = True
        try:
            mcu_cmds = [e for e in events
                        if e.get("type") == "mcu_command"]
            if filter_pat:
                pat = re.compile(filter_pat, re.IGNORECASE)
                mcu_cmds = [e for e in mcu_cmds
                            if pat.search(e.get("cmd_name", ""))]
            total = len(mcu_cmds)
            sent = 0
            if send:
                serial = self._get_serial()
                if not serial:
                    raise gcmd.error("MCU serial interface not available")
                for ev in mcu_cmds:
                    if not _replay_state["replaying"]:
                        break
                    if speed != 1.0:
                        time.sleep(0.001 / speed)
                    try:
                        cmd_data = ev.get("encoded_data", [])
                        if cmd_data:
                            serial.raw_send(
                                list(cmd_data),
                                ev.get("minclock", 0),
                                ev.get("reqclock", 0),
                                serial.get_default_command_queue()
                            )
                        sent += 1
                        if sent % 100 == 0:
                            gcmd.respond_raw(
                                "Replay progress: %d/%d" % (sent, total)
                            )
                    except Exception as e:
                        logging.exception("mcu_replay send error")
            else:
                for i, ev in enumerate(mcu_cmds):
                    if i % 1000 == 0:
                        gcmd.respond_raw(
                            "Replay (read-only): %d/%d - cmd=%s params=%s" % (
                                i, total,
                                ev.get("cmd_name", "?"),
                                str(ev.get("params", {}))[:80]
                            )
                        )
            gcmd.respond_raw(
                "Replay complete: %d commands processed" % (total,)
            )
        finally:
            with _replay_lock:
                _replay_state["replaying"] = False

    cmd_MCU_TRACE_STATUS_help = "Report current trace/recording status"

    def cmd_MCU_TRACE_STATUS(self, gcmd):
        with _replay_lock:
            rec = _replay_state["recording"]
            repl = _replay_state["replaying"]
        gcmd.respond_raw(
            "Trace status: recording=%s replaying=%s" % (rec, repl)
        )

    def _get_serial(self):
        try:
            mcu = self.printer.lookup_object("mcu")
            return mcu._serial
        except:
            return None

    def _on_load_file(self):
        pass

    def _on_print_start(self):
        if not self._log_gcode and not self._log_mcu_commands:
            return
        try:
            ps = self.printer.lookup_object("print_stats")
            vsd = self.printer.lookup_object("virtual_sdcard")
            filename = ps.filename
            if not filename:
                filename = vsd.file_path() or "unknown"
            queuelogger.start_trace_session(filename)
        except Exception as e:
            logging.exception("gcode_mcu_trace start session")

    def _on_print_pause(self):
        pass

    def _on_print_end(self):
        queuelogger.end_trace_session()

    def _on_shutdown(self):
        queuelogger.end_trace_session()

    def _apply_hooks(self):
        pass

    def register_gcode_callback(self, cb):
        self._gcode_cb = cb

    def register_mcu_command_callback(self, cb):
        self._mcu_cmd_cb = cb

    def register_mcu_response_callback(self, cb):
        self._mcu_resp_cb = cb

    def register_mcu_ack_callback(self, cb):
        self._mcu_ack_cb = cb

    def log_gcode(self, event):
        if self._log_gcode and self._gcode_cb:
            self._gcode_cb(event)
        elif self._log_gcode:
            queuelogger.log_trace("gcode", event)

    def log_mcu_command(self, event):
        if _replay_state.get("recording") or self._log_mcu_commands:
            if self._mcu_cmd_cb:
                self._mcu_cmd_cb(event)
            else:
                queuelogger.log_trace("mcu_commands", event)

    def log_mcu_response(self, event):
        if _replay_state.get("recording") or self._log_mcu_responses:
            if self._mcu_resp_cb:
                self._mcu_resp_cb(event)
            else:
                queuelogger.log_trace("mcu_responses", event)

    def log_mcu_ack(self, event):
        if _replay_state.get("recording") or self._log_mcu_execution:
            if self._mcu_ack_cb:
                self._mcu_ack_cb(event)
            else:
                queuelogger.log_trace("mcu_execution", event)


def load_config(config):
    return GCodeMCUTacer(config)