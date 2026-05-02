# Virtual MCU response generator
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Response Generator
==================

Generates automatic responses for the virtual MCU based on the
data dictionary. Uses message format definitions to construct
properly-encoded response messages.

Supports:
  - Automatic response generation from command definitions
  - Custom response data injection
  - Configurable timing/sequence number control
"""

import json
import logging
import zlib
from typing import Any, Dict, List, Optional

from ..protocol.codec import MessageBlock, VLQEncoder
from ..protocol.dictionary import MessageDictionary, MessageFormat
from ..protocol.parser import Parser


class Responder:
    """Generates virtual MCU responses to simulated commands.

    Uses the message dictionary to construct properly-encoded
    response messages.
    """

    def __init__(self, dictionary: Optional[MessageDictionary] = None):
        self.parser = Parser(dictionary)
        self._custom_responses: Dict[str, bytes] = {}
        self._next_seq = 0
        self._response_delay: float = 0.001  # 1ms simulated latency

    def set_dictionary(self, dictionary: MessageDictionary) -> None:
        """Set the message dictionary for response generation."""
        self.parser.dictionary = dictionary

    def get_dictionary(self) -> MessageDictionary:
        return self.parser.dictionary

    def register_custom(self, cmd_name: str, response_bytes: bytes) -> None:
        """Register a pre-encoded response for a command."""
        self._custom_responses[cmd_name] = response_bytes

    def unregister_custom(self, cmd_name: str) -> None:
        """Remove a custom response."""
        self._custom_responses.pop(cmd_name, None)

    @property
    def response_delay(self) -> float:
        return self._response_delay

    @response_delay.setter
    def response_delay(self, seconds: float) -> None:
        self._response_delay = max(0.0, seconds)

    def next_seq(self) -> int:
        """Get next sequence number and advance."""
        seq = self._next_seq
        self._next_seq = (self._next_seq + 1) & 0x0F
        return seq

    def generate_response(self, cmd_name: str,
                          response_params: Optional[Dict[str, Any]] = None
                          ) -> Optional[bytes]:
        """Generate a response message for a given command.

        Finds the corresponding response message format and encodes it.

        Args:
            cmd_name: The command name (e.g., "identify")
            response_params: Parameters for the response message

        Returns:
            Wire-format response bytes, or None if no response format found
        """
        # Check for custom response first
        if cmd_name in self._custom_responses:
            return self._custom_responses[cmd_name]

        # Try to find standard response format
        # Common Kalico response naming: <cmd>_response or status
        dict_obj = self.parser.get_dictionary()

        # Try various response name patterns
        response_names = [
            f"{cmd_name}_response",
            "status",
        ]
        for rname in response_names:
            mf = dict_obj.get_by_name(rname)
            if mf is not None:
                params = response_params or {}
                content = mf.encode(**params)
                seq = self.next_seq()
                block = MessageBlock(seq=seq, content=content)
                return block.encode()

        return None

    def build_identify_response(self, mcu_config: dict) -> bytes:
        """Build the identify response containing the data dictionary.

        This is the most critical response - it tells the host
        about all available commands.
        """
        # Build dictionary JSON
        dict_data = {
            "config": mcu_config.get("config", {}),
            "version": mcu_config.get("version", "virtual-mcu-0.1"),
            "build_versions": mcu_config.get("build_versions", "virtual"),
        }

        # Build message definitions
        dict_obj = self.parser.get_dictionary()
        msg_defs = bytearray()
        for mf in dict_obj.messages:
            encoded_name = mf.msgformat.encode("utf-8")
            msgid_bytes = bytes(VLQEncoder.encode_uint32(mf.msgid))
            name_bytes = bytes(VLQEncoder.encode_uint32(len(encoded_name)))
            msg_defs.extend(msgid_bytes)
            msg_defs.extend(name_bytes)
            msg_defs.extend(encoded_name)

        # Combine: JSON config + message defs
        config_json = json.dumps(dict_data).encode("utf-8")
        full_dict = bytearray()
        length_bytes = bytes(VLQEncoder.encode_uint32(len(config_json)))
        full_dict.extend(length_bytes)
        full_dict.extend(config_json)
        full_dict.extend(msg_defs)

        # Compress with zlib (as real firmware does)
        compressed = zlib.compress(bytes(full_dict))

        # Split into chunks for identify_response messages
        chunk_size = 40
        seq = self.next_seq()
        first = True

        # For the first response, we need to handle the offset=0 case
        chunks = []
        for offset in range(0, len(compressed), chunk_size):
            chunk = compressed[offset:offset + chunk_size]
            mf = dict_obj.get_by_name("identify_response")
            if mf is None:
                continue
            content = mf.encode(offset=offset, data=chunk)
            block = MessageBlock(seq=seq, content=content)
            chunks.append(block.encode())
            seq = self.next_seq()

        # Return all chunks concatenated (for single-get usage)
        return b"".join(chunks)

    def get_next_seq(self) -> int:
        """Get current sequence number without advancing."""
        return self._next_seq
