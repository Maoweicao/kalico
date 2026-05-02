# Virtual MCU simulator for offline Kalico protocol debugging
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Virtual MCU Simulator
=====================

Simulates a minimal Kalico MCU firmware for offline protocol debugging.
Can be used without any physical hardware to:
  - Test protocol parsing and encoding
  - Debug communication logic
  - Simulate command/response flows
  - Verify host-side code behavior

The virtual MCU:
  - Maintains a virtual clock (derived from host time)
  - Responds to identify requests with a data dictionary
  - Handles config and status commands
  - Supports custom command handler registration
"""

import json
import logging
import threading
import time
import zlib
from typing import Any, Callable, Dict, List, Optional, Union

from ..protocol.codec import (
    MESSAGE_DEST,
    MESSAGE_SEQ_MASK,
    MESSAGE_SYNC,
    MessageBlock,
    VLQDecoder,
    VLQEncoder,
    crc16_ccitt,
)
from ..protocol.dictionary import MessageDictionary
from ..protocol.parser import Parser, ParsedMessage
from .command_handler import CommandRegistry
from .responder import Responder


class VirtualMCU:
    """Simulates a Kalico MCU device.

    Provides the same binary protocol interface as a real MCU,
    allowing host-side debugging without hardware.
    """

    STATE_INIT = "init"
    STATE_READY = "ready"
    STATE_SHUTDOWN = "shutdown"
    STATE_ERROR = "error"

    def __init__(self, name: str = "virtual-mcu"):
        self.name = name
        self.state = self.STATE_INIT
        self._clock_freq: float = 1000000.0  # 1 MHz virtual clock
        self._clock_offset: float = 0.0
        self._virtual_time: float = 0.0
        self._start_time: float = 0.0
        self._lock = threading.Lock()
        self._rx_buffer = bytearray()

        # Message handling
        self.parser = Parser()
        self.responder = Responder(self.parser.get_dictionary())
        self.registry = CommandRegistry()

        # Register default handlers
        self._register_default_handlers()

        # Callbacks
        self.on_message: Optional[Callable[[ParsedMessage], None]] = None
        self.on_response: Optional[Callable[[bytes], None]] = None
        self.on_state_change: Optional[Callable[[str], None]] = None

        # Statistics
        self.commands_received = 0
        self.responses_sent = 0

        # Add default messages to dictionary
        self._setup_default_dictionary()

    def _setup_default_dictionary(self) -> None:
        """Set up a minimal default message dictionary."""
        dict_obj = self.parser.get_dictionary()
        dict_obj.add_default_messages()
        # Add some common MCU messages
        self._add_common_messages(dict_obj)

    def _add_common_messages(self, dict_obj: MessageDictionary) -> None:
        """Add common MCU command/response message formats."""
        common_messages = {
            # Config messages
            2: "config oid=%c",
            3: "config_key oid=%c key=%.*s",
            4: "config_key_value oid=%c key=%.*s value=%.*s",
            5: "finalize_config crc=%u",
            6: "get_config",
            # Digital output
            10: "update_digital_out oid=%c value=%c",
            11: "set_digital_out_pwm oid=%c value=%hu",
            # Stepper motor
            20: "queue_step oid=%c interval=%u count=%hu add=%hi",
            21: "set_next_step_dir oid=%c dir=%c",
            22: "reset_step_clock oid=%c clock=%u",
            23: "stepper_get_position oid=%c",
            24: "stepper_stop_on_timeout oid=%c",
            # ADC
            30: "query_analog oid=%c clock=%u rest_ticks=%u",
            # Status responses
            100: "identify_response offset=%u data=%.*s",
            101: "status clock=%u status=%c",
            102: "shutdown clock=%u flags=%c",
            103: "config_crc oid=%c crc=%u",
            104: "stepper_position oid=%c pos=%i",
            105: "analog_state oid=%c value=%hu",
            106: "gpio_output oid=%c value=%c",
        }
        for msgid, msgformat in common_messages.items():
            dict_obj.add_message(msgid, msgformat)

    def _register_default_handlers(self) -> None:
        """Register default command handlers."""
        self.registry.register("identify", self._handle_identify)
        self.registry.register("config", self._handle_config)
        self.registry.register("config_key", self._handle_config_key)
        self.registry.register("finalize_config", self._handle_finalize_config)
        self.registry.register("get_config", self._handle_get_config)

    def _handle_identify(self, params: Dict[str, Any],
                         mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Handle identify command - respond with data dictionary."""
        offset = params.get("offset", 0)
        count = params.get("count", 40)

        # Build dictionary payload
        dict_config = {
            "version": f"virtual-{self.name}",
            "build_versions": "virtual",
            "config": {
                "MCU": self.name,
                "CLOCK_FREQ": self._clock_freq,
                "STATUS_BITS": 0,
                "RECEIVE_WINDOW": 64,
            },
        }

        # Get compressed dictionary
        dict_obj = self.parser.get_dictionary()
        raw_dict = self._build_raw_dictionary(dict_obj, dict_config)
        compressed = zlib.compress(raw_dict)

        chunk = compressed[offset:offset + count]
        return {"offset": offset, "data": chunk}

    def _build_raw_dictionary(self, dict_obj: MessageDictionary,
                              dict_config: dict) -> bytes:
        """Build raw dictionary bytes as the firmware would."""
        config_json = json.dumps(dict_config).encode("utf-8")
        result = bytearray()
        length_bytes = bytes(VLQEncoder.encode_uint32(len(config_json)))
        result.extend(length_bytes)
        result.extend(config_json)
        for mf in dict_obj.messages:
            encoded_name = mf.msgformat.encode("utf-8")
            result.extend(bytes(VLQEncoder.encode_uint32(mf.msgid)))
            result.extend(bytes(VLQEncoder.encode_uint32(len(encoded_name))))
            result.extend(encoded_name)
        return bytes(result)

    def _handle_config(self, params: Dict[str, Any],
                       mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Handle config command."""
        return {"oid": params.get("oid", 0)}

    def _handle_config_key(self, params: Dict[str, Any],
                           mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Handle config_key command."""
        return {"oid": params.get("oid", 0)}

    def _handle_finalize_config(self, params: Dict[str, Any],
                                mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Handle finalize_config command."""
        self.state = self.STATE_READY
        #config_crc response with oid and crc
        return {"oid": 0, "crc": params.get("crc", 0)}

    def _handle_get_config(self, params: Dict[str, Any],
                           mcu: "VirtualMCU") -> Optional[Dict[str, Any]]:
        """Handle get_config command - respond with status."""
        return {
            "clock": self.get_virtual_clock(),
            "status": 0,  # STATUS_READY
        }

    # ─── Public API ─────────────────────────────────────────────────

    def start(self) -> None:
        """Start the virtual MCU."""
        with self._lock:
            self._start_time = time.time()
            self.state = self.STATE_READY
            self._rx_buffer = bytearray()
        if self.on_state_change:
            self.on_state_change(self.state)
        logging.info(f"Virtual MCU '{self.name}' started")

    def stop(self) -> None:
        """Stop the virtual MCU."""
        with self._lock:
            self.state = self.STATE_INIT
        if self.on_state_change:
            self.on_state_change(self.state)
        logging.info(f"Virtual MCU '{self.name}' stopped")

    def reset(self) -> None:
        """Reset the virtual MCU to initial state."""
        self.stop()
        self.start()

    def feed_data(self, data: Union[bytes, bytearray]) -> List[ParsedMessage]:
        """Feed raw host-to-MCU data for processing.

        Processes incoming bytes, finds message blocks, dispatches
        commands, and generates responses.

        Args:
            data: Raw bytes (wire format) from host

        Returns:
            List of parsed messages from the data
        """
        responses: List[bytes] = []
        parsed_messages: List[ParsedMessage] = []

        with self._lock:
            self._rx_buffer.extend(data)
            buf = self._rx_buffer

            while True:
                # Try to find a valid message block
                try:
                    block, consumed = MessageBlock.find_and_decode(buf)
                except Exception:
                    consumed = -MESSAGE_MIN

                if block is None:
                    if consumed < 0:
                        # Need more data; keep recent bytes
                        keep = min(-consumed, len(buf))
                        self._rx_buffer = buf[-keep:] if keep > 0 else bytearray()
                    break

                # Remove consumed bytes
                buf = buf[consumed:]
                self.commands_received += 1

                # Parse and dispatch
                parsed = self.parser.parse_block(block, direction="Rx")
                parsed_messages.append(parsed)

                # Dispatch command
                try:
                    response = self._dispatch_command(parsed)
                    if response is not None:
                        responses.append(response)
                except Exception as e:
                    logging.error(f"Command dispatch error: {e}")

            self._rx_buffer = buf

        # Deliver responses
        for resp_bytes in responses:
            if self.on_response:
                self.on_response(resp_bytes)

        return parsed_messages

    def _dispatch_command(self, parsed: ParsedMessage) -> Optional[bytes]:
        """Dispatch a parsed command and return response bytes if any."""
        cmd_name = parsed.msg_name
        params = parsed.params

        # Check registry
        response_params = self.registry.dispatch(cmd_name, params, self)
        if response_params is not None:
            self.responses_sent += 1
            return self.responder.generate_response(cmd_name, response_params)

        return None

    def register_command(self, cmd_name: str,
                         handler) -> None:
        """Register a custom command handler."""
        self.registry.register(cmd_name, handler)

    def register_response(self, cmd_name: str,
                          response_bytes: bytes) -> None:
        """Register a pre-encoded response for a command."""
        self.responder.register_custom(cmd_name, response_bytes)

    def get_virtual_clock(self) -> int:
        """Get the current virtual clock value."""
        now = time.time()
        elapsed = now - self._start_time
        return int(elapsed * self._clock_freq)

    def get_stats(self) -> dict:
        """Get simulator statistics."""
        return {
            "name": self.name,
            "state": self.state,
            "uptime": round(time.time() - self._start_time, 1) if self._start_time else 0,
            "commands_received": self.commands_received,
            "responses_sent": self.responses_sent,
            "virtual_clock": self.get_virtual_clock(),
            "clock_freq": self._clock_freq,
            "registered_commands": self.registry.list_commands(),
        }

    def __repr__(self) -> str:
        return f"VirtualMCU(name={self.name!r}, state={self.state})"
