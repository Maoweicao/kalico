# Kalico protocol message dictionary
#
# Manages the "data dictionary" that defines message formats
# for encoding/decoding commands and responses between host and MCU.
#
# Derived from klippy/msgproto.py (GPLv3)
# Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Data Dictionary Management
==========================

The data dictionary maps message IDs to message format strings. It is
normally obtained from the MCU's firmware via the 'identify' command
during connection startup.

Dictionary source options:
  1. From real MCU: captured during serial handshake (identify response)
  2. From file: pre-extracted dictionary (JSON or raw binary)
  3. Built-in: minimal default dictionary for simulation/testing
"""

import json
import logging
import zlib
from typing import Any, Dict, List, Optional, Tuple, Union

from .codec import VLQDecoder, VLQEncoder, MESSAGE_MIN

# Default messages that are always available
DEFAULT_MESSAGES: Dict[str, int] = {
    "identify_response offset=%u data=%.*s": 0,
    "identify offset=%u count=%c": 1,
}


class MessageFormat:
    """A parsed message format definition.

    Maps between wire-format (VLQ-encoded) messages and their
    human-readable parameterized form.
    """

    def __init__(self, msgid: int, msgformat: str,
                 enumerations: Optional[Dict[str, Dict[str, int]]] = None):
        self.msgid = msgid
        self.msgid_bytes = bytes(VLQEncoder.encode_uint32(msgid))
        self.msgformat = msgformat
        self.name = msgformat.split()[0] if " " in msgformat else msgformat
        self.enumerations = enumerations or {}
        self._parsed_params: List[Tuple[str, str]] = []
        self._parse_format()

    def _parse_format(self) -> None:
        """Parse the format string into parameter names and types."""
        parts = self.msgformat.split()
        if len(parts) < 2:
            return
        for arg in parts[1:]:
            if "=" in arg:
                name, fmt = arg.split("=", 1)
                self._parsed_params.append((name, fmt))

    @property
    def params(self) -> List[Tuple[str, str]]:
        return list(self._parsed_params)

    def encode(self, **params: Any) -> bytes:
        """Encode named parameters into VLQ-encoded content bytes.

        Returns the content bytes (msgid + encoded params), ready
        to be placed into a MessageBlock.
        """
        content = list(self.msgid_bytes)
        for name, fmt in self._parsed_params:
            value = params.get(name, 0)
            encoded = self._encode_param(fmt, value)
            content.extend(encoded)
        return bytes(content)

    def _encode_param(self, fmt: str, value: Any) -> List[int]:
        """Encode a single parameter value by format type."""
        # Handle enumerations
        for enum_name, enum_map in self.enumerations.items():
            if fmt.endswith(enum_name) or name_match(fmt, enum_name):
                if value in enum_map:
                    value = enum_map[value]
                break

        if fmt in ("%u", "%i"):
            return VLQEncoder.encode_uint32(int(value))
        elif fmt in ("%hu", "%hi"):
            return VLQEncoder.encode_uint16(int(value))
        elif fmt == "%c":
            return VLQEncoder.encode_byte(int(value))
        elif fmt in ("%s", "%.*s", "%*s"):
            if isinstance(value, str):
                return VLQEncoder.encode_string(value)
            return VLQEncoder.encode_string(bytes(value))
        return VLQEncoder.encode_uint32(int(value))

    def decode(self, data: Union[bytes, bytearray], pos: int = 0
               ) -> Tuple[Dict[str, Any], int]:
        """Decode VLQ-encoded parameters from data starting at pos.

        Returns (params_dict, new_position).
        """
        params: Dict[str, Any] = {}
        # Skip msgid bytes
        msgid, pos = VLQDecoder.decode_int(data, pos)
        for name, fmt in self._parsed_params:
            value, pos = self._decode_param(fmt, data, pos)
            params[name] = value
        return params, pos

    def _decode_param(self, fmt: str,
                      data: Union[bytes, bytearray], pos: int
                      ) -> Tuple[Any, int]:
        """Decode a single parameter from data by format type."""
        # Handle enumerations
        for enum_name, enum_map in self.enumerations.items():
            if fmt.endswith(enum_name) or name_match(fmt, enum_name):
                value, pos = VLQDecoder.decode_uint32(data, pos)
                reverse_map = {v: k for k, v in enum_map.items()}
                decoded = reverse_map.get(value, f"?{value}")
                return decoded, pos

        if fmt in ("%u",):
            return VLQDecoder.decode_uint32(data, pos)
        elif fmt in ("%i",):
            return VLQDecoder.decode_int32(data, pos)
        elif fmt in ("%hu",):
            v, pos = VLQDecoder.decode_uint32(data, pos)
            return v & 0xFFFF, pos
        elif fmt in ("%hi",):
            v, pos = VLQDecoder.decode_int32(data, pos)
            return v & 0xFFFF, pos
        elif fmt == "%c":
            return VLQDecoder.decode_int(data, pos)
        elif fmt in ("%s",):
            return VLQDecoder.decode_string(data, pos)
        elif fmt in ("%.*s", "%*s"):
            return VLQDecoder.decode_string(data, pos)
        # Unknown format, treat as uint32
        return VLQDecoder.decode_uint32(data, pos)

    def format_params(self, params: Dict[str, Any]) -> str:
        """Format decoded parameters into a human-readable string."""
        parts = [self.name]
        for name, fmt in self._parsed_params:
            value = params.get(name, "?")
            if isinstance(value, bytes):
                value = repr(value)
            parts.append(f"{name}={value}")
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"MessageFormat(msgid={self.msgid}, name={self.name})"


def name_match(fmt: str, enum_name: str) -> bool:
    """Check if a format string references an enumeration by name."""
    # Pattern: format string like '%c' with enum name as suffix
    return False


class MessageDictionary:
    """Manages the collection of message format definitions.

    Acts as a bidirectional mapping between message IDs and names.
    """

    def __init__(self):
        self._messages_by_id: Dict[int, MessageFormat] = {}
        self._messages_by_name: Dict[str, MessageFormat] = {}
        self._raw_identify_data: Optional[bytes] = None
        self.config: Dict[str, Any] = {}
        self.version: str = ""
        self.build_versions: str = ""

    def add_default_messages(self) -> None:
        """Register the default messages (identify, identify_response)."""
        for fmt, msgid in DEFAULT_MESSAGES.items():
            self.add_message(msgid, fmt)

    def add_message(self, msgid: int, msgformat: str,
                    enumerations: Optional[Dict[str, Dict[str, int]]] = None
                    ) -> MessageFormat:
        """Register a message format."""
        mf = MessageFormat(msgid, msgformat, enumerations)
        self._messages_by_id[msgid] = mf
        self._messages_by_name[mf.name] = mf
        return mf

    def get_by_id(self, msgid: int) -> Optional[MessageFormat]:
        return self._messages_by_id.get(msgid)

    def get_by_name(self, name: str) -> Optional[MessageFormat]:
        return self._messages_by_name.get(name)

    @property
    def messages(self) -> List[MessageFormat]:
        return list(self._messages_by_id.values())

    def process_identify(self, data: bytes, decompress: bool = True
                         ) -> bool:
        """Process raw identify data from firmware.

        Parses the JSON config and message definitions embedded
        in the firmware binary.

        Args:
            data: Raw binary identify response data
            decompress: Whether to decompress (zlib) the data

        Returns:
            True if successful
        """
        self._raw_identify_data = data
        if decompress:
            try:
                data = zlib.decompress(data)
            except zlib.error as e:
                logging.warning(f"Dictionary decompression failed: {e}")
                return False

        # Parse the JSON config from the dictionary
        try:
            config_json, pos = self._parse_dict_config(data)
            self.config = config_json.get("config", {})
            self.version = config_json.get("version", "")
            self.build_versions = config_json.get("build_versions", "")
            # Parse message definitions
            self._parse_dict_messages(data, pos)
            return True
        except Exception as e:
            logging.error(f"Failed to parse identify data: {e}")
            return False

    def _parse_dict_config(self, data: bytes
                           ) -> Tuple[Dict[str, Any], int]:
        """Parse the JSON config section from dictionary data."""
        # The config is a JSON string prefixed by its length (VLQ)
        length, pos = VLQDecoder.decode_int(data, 0)
        raw = data[pos:pos + length]
        config = json.loads(raw.decode("utf-8"))
        return config, pos + length

    def _parse_dict_messages(self, data: bytes, pos: int) -> None:
        """Parse message format definitions from dictionary data."""
        while pos < len(data):
            msgid, pos = VLQDecoder.decode_int(data, pos)
            length, pos = VLQDecoder.decode_int(data, pos)
            raw = data[pos:pos + length]
            msgformat = raw.decode("utf-8")
            self.add_message(msgid, msgformat)
            pos += length

    def save_to_file(self, filepath: str) -> None:
        """Save the dictionary to a JSON file."""
        data = {
            "version": self.version,
            "build_versions": self.build_versions,
            "config": self.config,
            "messages": [
                {"msgid": m.msgid, "format": m.msgformat}
                for m in self._messages_by_id.values()
            ],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_file(cls, filepath: str) -> "MessageDictionary":
        """Load a dictionary from a JSON file."""
        d = cls()
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        d.version = data.get("version", "")
        d.build_versions = data.get("build_versions", "")
        d.config = data.get("config", {})
        for msg in data.get("messages", []):
            d.add_message(msg["msgid"], msg["format"])
        return d

    def __repr__(self) -> str:
        return (
            f"MessageDictionary("
            f"version={self.version!r}, "
            f"messages={len(self._messages_by_id)})"
        )
