# Kalico Debug Tool - CLI Command Functions
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
CLI Commands Module
===================

Standalone command functions that can be called programmatically
from scripts or the AI bridge. Each command is a pure function
that takes parameters and returns results as dicts.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from ..log.logger import LogEngine, ProtocolEvent
from ..protocol.codec import (
    MessageBlock, hex_to_bytes, bytes_to_hex, format_hex_dump,
)
from ..protocol.parser import Parser, ParsedMessage
from ..io.serial_io import SerialIO, ConnectionState
from ..io.can_io import CANIO
from ..io.capture import CaptureManager
from ..io.replay import ReplayPlayback
from ..simulator.virtual_mcu import VirtualMCU


class CLICommands:
    """Stateless command implementations for programmatic use."""

    def __init__(self):
        self.log_engine = LogEngine()
        self.parser = Parser()
        self.serial_io = SerialIO(
            on_data=self._on_serial_data,
        )
        self.can_io = CANIO(
            on_data=self._on_serial_data,
        )
        self.capture_mgr = CaptureManager()
        self.virtual_mcu: Optional[VirtualMCU] = None
        self._monitor_buffer: List[dict] = []
        self._active_io: str = "serial"  # "serial" or "can"

    def _on_serial_data(self, data: bytes) -> None:
        """Serial data callback."""
        try:
            block = MessageBlock.decode(data)
            parsed = self.parser.parse_block(block, direction="Rx")
            self.log_engine.log_message(parsed, "Rx")
            self._monitor_buffer.append(parsed.params)
        except ValueError as e:
            self.log_engine.log_raw(data, "Rx", error=str(e))

    def cmd_connect(self, port: str, baudrate: int = 250000,
                    io_type: str = "serial") -> dict:
        """Connect to serial port or CAN bus.

        For CAN: port='slcan:COM3', port='virtual:virtual0', or port='pcan:PCAN_USBBUS1'
        """
        if io_type == "can":
            parts = port.split(":", 1)
            iface = parts[0]
            channel = parts[1] if len(parts) > 1 else ""
            ok = False
            if iface == "slcan":
                ok = self.can_io.connect_slcan(channel, baudrate)
            elif iface == "pcan":
                ok = self.can_io.connect_pcan(channel, baudrate)
            else:
                ok = self.can_io.connect_virtual(channel or iface, baudrate)
            self._active_io = "can"
            return {"ok": ok, "interface": iface, "channel": channel,
                    "bitrate": baudrate}
        result = self.serial_io.connect(port, baudrate)
        self._active_io = "serial"
        return {"ok": result, "port": port, "baudrate": baudrate}

    def cmd_disconnect(self, io_type: str = "") -> dict:
        """Disconnect from serial or CAN."""
        if io_type == "can" or self._active_io == "can":
            self.can_io.disconnect()
            return {"ok": True, "type": "can"}
        self.serial_io.disconnect()
        return {"ok": True, "type": "serial"}

    def cmd_send_raw(self, hex_str: str, io_type: str = "") -> dict:
        """Send raw hex bytes via active I/O."""
        try:
            data = hex_to_bytes(hex_str)
            io = self.can_io if (io_type == "can" or self._active_io == "can") else self.serial_io
            if not io.is_connected():
                return {"ok": False, "error": "Not connected"}
            self.log_engine.log_raw(data, "Tx")
            result = io.send(data)
            return {"ok": result, "bytes": len(data), "hex": data.hex()}
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    def cmd_send_command(self, name: str,
                         params: Optional[dict] = None,
                         io_type: str = "") -> dict:
        """Send a named command via active I/O."""
        params = params or {}
        encoded = self.parser.encode_message(name, **params)
        if encoded is None:
            return {"ok": False, "error": f"Unknown command: {name}"}
        io = self.can_io if (io_type == "can" or self._active_io == "can") else self.serial_io
        if not io.is_connected():
            return {"ok": False, "error": "Not connected"}
        self.log_engine.log_raw(encoded, "Tx")
        result = io.send(encoded)
        return {"ok": result, "command": name, "hex": encoded.hex()}

    def cmd_get_messages(self, count: int = 50) -> dict:
        """Get recent messages."""
        events = self.log_engine.get_all_events()
        recent = events[-count:]
        messages = []
        for ev in recent:
            messages.append(ev.to_dict())
        return {
            "ok": True,
            "count": len(messages),
            "messages": messages,
        }

    def cmd_get_dictionary(self) -> dict:
        """Get data dictionary contents."""
        dict_obj = self.parser.get_dictionary()
        messages = []
        for mf in sorted(dict_obj.messages, key=lambda x: x.msgid):
            messages.append({
                "msgid": mf.msgid,
                "format": mf.msgformat,
                "name": mf.name,
            })
        return {
            "ok": True,
            "version": dict_obj.version,
            "count": len(messages),
            "messages": messages,
        }

    def cmd_get_status(self, io_type: str = "") -> dict:
        """Get connection status and stats."""
        io = self.can_io if (io_type == "can" or self._active_io == "can") else self.serial_io
        stats = io.get_stats()
        result: dict = {
            "ok": True,
            "active_io": self._active_io,
            "connection": stats,
            "log_events": self.log_engine.event_count,
        }
        if self.virtual_mcu:
            result["virtual_mcu"] = self.virtual_mcu.get_stats()
        return result

    def cmd_auto_detect(self,
                        baudrates: Optional[List[int]] = None,
                        timeout: float = 0.6) -> dict:
        """Auto-detect Kalico MCU by scanning all serial ports."""
        results_log: list = []

        def on_progress(msg: str) -> None:
            results_log.append(msg)

        found = self.serial_io.auto_detect(
            baudrates=baudrates,
            on_progress=on_progress,
            timeout_per_port=timeout,
        )
        return {
            "ok": found is not None,
            "found": {
                "port": found[0],
                "baudrate": found[1],
            } if found else None,
            "log": results_log,
        }

    def cmd_can_discover(self, uuid: str = "", timeout: float = 3.0) -> dict:
        """Discover MCU nodes on the CAN bus."""
        uuid_str = uuid.strip() or None
        if not self.can_io.is_connected():
            return {"ok": False, "error": "CAN not connected"}
        nodeid = self.can_io.discover_mcu(uuid=uuid_str, timeout=timeout)
        return {"ok": nodeid is not None, "nodeid": nodeid}

    def cmd_can_assign(self, uuid: str, nodeid: int = 64) -> dict:
        """Assign a NodeID to a CAN MCU."""
        if not self.can_io.is_connected():
            return {"ok": False, "error": "CAN not connected"}
        ok = self.can_io.assign_nodeid(uuid, nodeid)
        if ok:
            self.can_io.connect_node(nodeid)
        return {"ok": ok, "uuid": uuid, "nodeid": nodeid}

    def cmd_sim_start(self, name: str = "ai-mcu") -> dict:
        """Start virtual MCU simulator."""
        self.virtual_mcu = VirtualMCU(name)
        self.virtual_mcu.on_response = self._on_sim_response
        self.virtual_mcu.start()
        return {"ok": True, "name": name}

    def cmd_sim_stop(self) -> dict:
        """Stop virtual MCU simulator."""
        if self.virtual_mcu:
            name = self.virtual_mcu.name
            self.virtual_mcu.stop()
            self.virtual_mcu = None
            return {"ok": True, "name": name}
        return {"ok": False, "error": "Not running"}

    def cmd_sim_send(self, name: str,
                     params: Optional[dict] = None) -> dict:
        """Send a command to the virtual MCU."""
        if not self.virtual_mcu:
            return {"ok": False, "error": "Virtual MCU not running"}
        params = params or {}
        encoded = self.parser.encode_message(name, **params)
        if encoded is None:
            return {"ok": False, "error": f"Unknown command: {name}"}
        self.virtual_mcu.feed_data(encoded)
        return {"ok": True, "command": name, "hex": encoded.hex()}

    def cmd_sim_register(self, cmd_name: str,
                         response_hex: str) -> dict:
        """Register a custom response for a command."""
        if not self.virtual_mcu:
            return {"ok": False, "error": "Virtual MCU not running"}
        try:
            data = hex_to_bytes(response_hex)
            self.virtual_mcu.register_response(cmd_name, data)
            return {"ok": True, "cmd_name": cmd_name}
        except ValueError as e:
            return {"ok": False, "error": str(e)}

    def _on_sim_response(self, resp_bytes: bytes) -> None:
        """Virtual MCU response callback."""
        try:
            block = MessageBlock.decode(resp_bytes)
            parsed = self.parser.parse_block(block, direction="Rx")
            self.log_engine.log_message(parsed, "Rx")
        except ValueError:
            self.log_engine.log_raw(resp_bytes, "Rx")

    def cmd_capture_start(self, name: Optional[str] = None) -> dict:
        """Start data capture."""
        path = self.capture_mgr.start(name)
        return {"ok": True, "path": path}

    def cmd_capture_stop(self) -> dict:
        """Stop data capture."""
        path = self.capture_mgr.stop()
        return {"ok": True, "path": path}

    # ── Benchmark Commands ──────────────────────────────────────────

    def cmd_benchmark(self, btype: str = "full", stepper_oid: int = 0,
                      latency_samples: int = 100,
                      throughput_packets: int = 2000,
                      clock_duration: float = 10.0,
                      target: str = "real") -> dict:
        """Run a MCU benchmark.

        Args:
            btype: 'latency', 'throughput', 'step_rate', 'clock', or 'full'
            stepper_oid: Stepper OID for step rate test
            latency_samples: Number of latency samples
            throughput_packets: Number of throughput test packets
            clock_duration: Clock test duration in seconds
            target: 'real' for real device, 'virtual' for simulator

        Returns:
            Benchmark result dict
        """
        from ..benchmark.engine import (
            BenchmarkEngine, BenchmarkConfig, BenchmarkType,
        )

        io = None
        simulator_mode = False
        if target == "virtual":
            from ..simulator.virtual_mcu import VirtualMCU
            if self.virtual_mcu is None:
                return {"ok": False, "error": "Virtual MCU not running"}
            mcu = self.virtual_mcu
            simulator_mode = True

            def send_fn(data):
                mcu.feed_data(data)
                return True
        else:
            io = self.can_io if self._active_io == "can" else self.serial_io
            if not io.is_connected():
                return {"ok": False, "error": "Not connected"}

            def send_fn(data):
                return io.send(data)

        def recv_fn():
            return self.log_engine.get_all_events()

        results_log = []

        def on_progress(msg):
            results_log.append(msg)

        engine = BenchmarkEngine(
            parser=self.parser, send_fn=send_fn, recv_fn=recv_fn,
            simulator_mode=simulator_mode, on_progress=on_progress,
        )
        engine._running = True

        try:
            cfg = BenchmarkConfig(
                stepper_oid=stepper_oid,
                latency_sample_count=latency_samples,
                throughput_packet_count=throughput_packets,
                clock_duration=clock_duration,
            )

            type_map = {
                "latency": BenchmarkType.LATENCY,
                "throughput": BenchmarkType.THROUGHPUT,
                "step_rate": BenchmarkType.STEP_RATE,
                "clock": BenchmarkType.CLOCK,
            }

            if btype == "full":
                results = engine.run_full(cfg)
                summaries = {}
                for k, v in results.items():
                    summaries[k] = v.summary() if hasattr(v, 'summary') else {}
                return {
                    "ok": True,
                    "type": "full",
                    "results": summaries,
                    "log": results_log,
                    "report": "\n".join(results_log),
                }
            else:
                bt = type_map.get(btype)
                if bt is None:
                    return {"ok": False, "error": f"Unknown benchmark: {btype}"}
                cfg.type = bt
                runner_map = {
                    BenchmarkType.LATENCY: engine.run_latency,
                    BenchmarkType.THROUGHPUT: engine.run_throughput,
                    BenchmarkType.STEP_RATE: engine.run_step_rate,
                    BenchmarkType.CLOCK: engine.run_clock,
                }
                result = runner_map[bt](cfg)
                s = result.summary() if hasattr(result, 'summary') else {}
                return {
                    "ok": s.get("success", False),
                    "type": btype,
                    "result": s,
                    "report": result.text_report() if hasattr(result, 'text_report') else "",
                    "log": results_log,
                }
        except Exception as e:
            return {"ok": False, "error": str(e)}
