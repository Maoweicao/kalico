# Kalico protocol message parser
#
# High-level message parser that uses the message dictionary
# to decode/encode command and response messages.
#
# Derived from klippy/msgproto.py and klippy/parsedump.py (GPLv3)
# Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Protocol Message Parser
=======================

Provides a high-level interface for:
  - Parsing raw message block bytes into structured messages
  - Encoding structured messages into wire-format bytes
  - Dumping/debugging message contents
"""

import logging
from typing import Any, Dict, List, Optional, Tuple, Union

from .codec import (
    MESSAGE_HEADER_SIZE,
    MESSAGE_TRAILER_SIZE,
    MessageBlock,
    VLQDecoder,
    crc16_ccitt,
)
from .dictionary import MessageDictionary


class UnknownMessage:
    """Represents an unrecognized/unregistered message."""

    name = "#unknown"

    def __init__(self, msgid: int, raw_content: bytes):
        self.msgid = msgid
        self.raw_content = raw_content

    def format_params(self) -> str:
        return f"#unknown msgid={self.msgid} data={self.raw_content.hex()}"


class OutputMessage:
    """Represents a debug output message (#output)."""

    name = "#output"

    def __init__(self, msg: str):
        self.msg = msg

    def format_params(self) -> str:
        return f"#output {self.msg}"


class ParsedMessage:
    """A fully parsed protocol message with metadata."""

    def __init__(self, block: MessageBlock,
                 msg_format: Optional[Any] = None,
                 params: Optional[Dict[str, Any]] = None,
                 msg_name: str = "#unknown"):
        self.block = block
        self.msg_format = msg_format
        self.params = params or {}
        self.msg_name = msg_name
        self.timestamp: float = 0.0
        self.direction: str = "Rx"  # "Tx" or "Rx"

    @property
    def seq(self) -> int:
        return self.block.seq

    @property
    def raw_hex(self) -> str:
        return self.block.raw_bytes.hex() if self.block.raw_bytes else ""

    def format(self) -> str:
        """Format as human-readable string."""
        if self.msg_format and hasattr(self.msg_format, "format_params"):
            return self.msg_format.format_params(self.params)
        return f"{self.msg_name} {self.params}"

    def __repr__(self) -> str:
        return (
            f"ParsedMessage("
            f"seq={self.seq}, {self.direction}, "
            f"name={self.msg_name})"
        )


class MessageDirection:
    """Direction constants."""
    TX = "Tx"
    RX = "Rx"


class Parser:
    """High-level protocol message parser.

    Wraps MessageDictionary with convenient parse/encode methods.
    """

    def __init__(self, dictionary: Optional[MessageDictionary] = None):
        self.dictionary = dictionary or MessageDictionary()
        self.dictionary.add_default_messages()
        self._unknown_count = 0

    def parse_block(self, block: MessageBlock,
                    direction: str = MessageDirection.RX) -> ParsedMessage:
        """Parse a MessageBlock into a structured ParsedMessage."""
        # Decode msgid from content
        if not block.content:
            return ParsedMessage(
                block=block, msg_name="#empty",
                params={"#raw": block.raw_bytes or b""}
            )
        msgid, param_pos = VLQDecoder.decode_int(block.content, 0)
        mf = self.dictionary.get_by_id(msgid)
        if mf is None:
            # Unknown message
            parsed = ParsedMessage(
                block=block, msg_name=f"#unknown_{msgid}",
                params={"#msgid": msgid, "#raw": block.content}
            )
            parsed.direction = direction
            return parsed
        # Decode parameters
        params, _ = mf.decode(block.content, 0)
        params["#name"] = mf.name
        parsed = ParsedMessage(
            block=block, msg_format=mf, params=params,
            msg_name=mf.name
        )
        parsed.direction = direction
        return parsed

    def parse_raw(self, data: Union[bytes, bytearray],
                  direction: str = MessageDirection.RX
                  ) -> Optional[ParsedMessage]:
        """Parse raw wire-format bytes directly.

        Attempts to find and decode a valid message block.
        Returns None if data is invalid.
        """
        try:
            block = MessageBlock.decode(data)
            return self.parse_block(block, direction)
        except ValueError as e:
            logging.debug(f"parse_raw failed: {e}")
            return None

    def encode_message(self, name: str, seq: int = 0,
                       **params: Any) -> Optional[bytes]:
        """Encode a named message with parameters into wire-format bytes.

        Returns wire-format bytes ready to send, or None if the
        message name is not in the dictionary.
        """
        mf = self.dictionary.get_by_name(name)
        if mf is None:
            return None
        content = mf.encode(**params)
        block = MessageBlock(seq=seq, content=content)
        return block.encode()

    def dump_block(self, block: MessageBlock) -> List[str]:
        """Dump a message block as human-readable debug lines.

        Similar to klippy/msgproto.py's MessageParser.dump().
        """
        seq = block.seq
        out = [f"seq: {seq:02x}"]
        pos = 0  # content start
        while True:
            msgid, param_pos = VLQDecoder.decode_int(block.content, pos)
            mf = self.dictionary.get_by_id(msgid)
            if mf is None:
                out.append(f"#unknown msgid={msgid}")
            else:
                params, _ = mf.decode(block.content, pos)
                out.append(mf.format_params(params))
            if param_pos >= len(block.content):
                break
            pos = param_pos
        return out

    def get_dictionary(self) -> MessageDictionary:
        return self.dictionary

    def __repr__(self) -> str:
        return f"Parser(dictionary={self.dictionary})"
