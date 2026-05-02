# Kalico Debug Tool - AI Bridge (JSON-RPC Interface)
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
AI Bridge Module
================

Provides a JSON-RPC style interface for AI Agents to interact with
the Kalico protocol debugger. Reads JSON commands from stdin and
writes JSON responses to stdout.

Command Format (stdin, one per line)::

    {"id": "1", "cmd": "get_status", "params": {}}

Response Format (stdout, one per line)::

    {"id": "1", "ok": true, "data": {...}}

Supported commands:
  - connect:       connect to serial port
  - disconnect:    disconnect serial port
  - send_raw:      send raw hex bytes
  - send_command:  send a named command
  - get_messages:  get recent protocol messages
  - get_dictionary: get the data dictionary
  - get_status:    get connection status
  - sim_start:     start virtual MCU
  - sim_stop:      stop virtual MCU
  - sim_send:      send command to virtual MCU
  - sim_register:  register custom response
  - capture_start: start data capture
  - capture_stop:  stop data capture
"""

import json
import logging
import sys
from typing import Any, Dict, Optional

from .commands import CLICommands


class BytesSafeEncoder(json.JSONEncoder):
    """JSON encoder that converts bytes to hex strings."""
    def default(self, obj):
        if isinstance(obj, bytes):
            return obj.hex()
        if isinstance(obj, bytearray):
            return bytes(obj).hex()
        return super().default(obj)


class AIBridge:
    """JSON-RPC style bridge for AI Agent interaction.

    Usage:
        echo '{"id":"1","cmd":"get_status","params":{}}' \\
            | python -m kalico_debug_tool --batch
    """

    def __init__(self):
        self.commands = CLICommands()
        self._command_map = self._build_command_map()

    def _build_command_map(self) -> dict:
        """Build command dispatch table."""
        return {
            "connect": self.commands.cmd_connect,
            "disconnect": self.commands.cmd_disconnect,
            "send_raw": self.commands.cmd_send_raw,
            "send_command": self.commands.cmd_send_command,
            "get_messages": self.commands.cmd_get_messages,
            "get_dictionary": self.commands.cmd_get_dictionary,
            "get_status": self.commands.cmd_get_status,
            "auto_detect": self.commands.cmd_auto_detect,
            "benchmark": self.commands.cmd_benchmark,
            "sim_start": self.commands.cmd_sim_start,
            "sim_stop": self.commands.cmd_sim_stop,
            "sim_send": self.commands.cmd_sim_send,
            "sim_register": self.commands.cmd_sim_register,
            "capture_start": self.commands.cmd_capture_start,
            "capture_stop": self.commands.cmd_capture_stop,
            "can_discover": self.commands.cmd_can_discover,
            "can_assign": self.commands.cmd_can_assign,
        }

    def process_line(self, line: str) -> Optional[str]:
        """Process a single JSON command line and return JSON response.

        Args:
            line: JSON command string

        Returns:
            JSON response string, or None on error
        """
        line = line.strip()
        if not line:
            return None

        try:
            request = json.loads(line)
        except json.JSONDecodeError as e:
            return json.dumps({
                "ok": False,
                "error": f"JSON parse error: {e}",
            })

        cmd_id = request.get("id", "0")
        cmd_name = request.get("cmd", "")
        params = request.get("params", {})

        handler = self._command_map.get(cmd_name)
        if handler is None:
            return json.dumps({
                "id": cmd_id,
                "ok": False,
                "error": f"Unknown command: {cmd_name}",
            })

        try:
            # Call the handler with params
            if isinstance(params, dict):
                result = handler(**params)
            else:
                result = handler(params)
        except TypeError as e:
            return json.dumps({
                "id": cmd_id,
                "ok": False,
                "error": f"Parameter error: {e}",
            })
        except Exception as e:
            return json.dumps({
                "id": cmd_id,
                "ok": False,
                "error": str(e),
            })

        response = {
            "id": cmd_id,
            "ok": True,
            "data": result,
        }
        return json.dumps(response, ensure_ascii=False, cls=BytesSafeEncoder)

    def run_batch(self, input_stream=None, output_stream=None) -> None:
        """Run in batch mode: read JSON commands, write JSON responses.

        Args:
            input_stream: Input stream (default: sys.stdin)
            output_stream: Output stream (default: sys.stdout)
        """
        if input_stream is None:
            input_stream = sys.stdin
        if output_stream is None:
            output_stream = sys.stdout

        for line in input_stream:
            response = self.process_line(line)
            if response:
                output_stream.write(response + "\n")
                output_stream.flush()


def run_batch() -> None:
    """Entry point for --batch mode."""
    bridge = AIBridge()
    bridge.run_batch()
