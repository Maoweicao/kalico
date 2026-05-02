# Kalico binary message protocol codec
#
# Pure Python implementation of VLQ encoding/decoding, CRC16-CCITT,
# and message block framing used in Kalico's host-MCU protocol.
#
# Derived from klippy/msgproto.py (GPLv3)
# Copyright (C) 2016-2024  Kevin O'Connor <kevin@koconnor.net>
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Kalico Binary Protocol Codec
============================

Message Block Format::

    Offset  Size  Field
    ─────────────────────────
     0       1    Length (total block size, min=5, max=64)
     1       1    Sequence (lower 4 bits seq | upper 4 bits 0x10)
     2       n    Content (VLQ-encoded command/response)
     2+n     2    CRC-16 CCITT checksum
     2+n+2   1    Sync byte (0x7E)

VLQ (Variable Length Quantity) Encoding:

    Integer ranges and encoded byte count:

    -32 .. 95        : 1 byte
    -4096 .. 12287   : 2 bytes
    -524288 .. 1572863 : 3 bytes
    -67108864 .. 201326591 : 4 bytes
    -2147483648 .. 4294967295 : 5 bytes
"""

import struct
from typing import List, Optional, Tuple, Union

# Protocol constants (match klippy/msgproto.py exactly)
MESSAGE_MIN = 5
MESSAGE_MAX = 64
MESSAGE_HEADER_SIZE = 2
MESSAGE_TRAILER_SIZE = 3
MESSAGE_POS_LEN = 0
MESSAGE_POS_SEQ = 1
MESSAGE_TRAILER_CRC = 3
MESSAGE_TRAILER_SYNC = 1
MESSAGE_PAYLOAD_MAX = MESSAGE_MAX - MESSAGE_MIN
MESSAGE_SEQ_MASK = 0x0F
MESSAGE_DEST = 0x10
MESSAGE_SYNC = 0x7E


# ─── CRC16-CCITT ─────────────────────────────────────────────────────────


def crc16_ccitt(buf: Union[bytes, bytearray, List[int]]) -> List[int]:
    """Compute CRC-16 CCITT checksum (MSB first, poly=0x1021).

    Returns [crc_high, crc_low] as used in the Kalico protocol trailer.
    """
    crc = 0xFFFF
    for data in buf:
        data ^= crc & 0xFF
        data ^= (data & 0x0F) << 4
        crc = ((data << 8) | (crc >> 8)) ^ (data >> 4) ^ (data << 3)
    return [crc >> 8, crc & 0xFF]


def crc16_ccitt_int(buf: Union[bytes, bytearray, List[int]]) -> int:
    """Compute CRC-16 CCITT and return as 16-bit integer."""
    hi, lo = crc16_ccitt(buf)
    return (hi << 8) | lo


# ─── VLQ (Variable Length Quantity) Encoding Types ─────────────────────


class VLQEncoder:
    """VLQ encoding for Kalico protocol integers."""

    @staticmethod
    def encode_uint32(v: int) -> List[int]:
        """Encode a (potentially signed) 32-bit integer as VLQ bytes."""
        out: List[int] = []
        if v >= 0xC000000 or v < -0x4000000:
            out.append((v >> 28) & 0x7F | 0x80)
        if v >= 0x180000 or v < -0x80000:
            out.append((v >> 21) & 0x7F | 0x80)
        if v >= 0x3000 or v < -0x1000:
            out.append((v >> 14) & 0x7F | 0x80)
        if v >= 0x60 or v < -0x20:
            out.append((v >> 7) & 0x7F | 0x80)
        out.append(v & 0x7F)
        return out

    @staticmethod
    def encode_uint16(v: int) -> List[int]:
        """Encode a 16-bit integer as VLQ bytes."""
        return VLQEncoder.encode_uint32(v)

    @staticmethod
    def encode_byte(v: int) -> List[int]:
        """Encode a byte-sized integer as VLQ bytes."""
        out: List[int] = []
        if v >= 0x60 or v < -0x20:
            out.append((v >> 7) & 0x7F | 0x80)
        out.append(v & 0x7F)
        return out

    @staticmethod
    def encode_int32(v: int) -> List[int]:
        """Encode a signed 32-bit integer (same as uint32 for this VLQ)."""
        return VLQEncoder.encode_uint32(v)

    @staticmethod
    def encode_int16(v: int) -> List[int]:
        """Encode a signed 16-bit integer."""
        return VLQEncoder.encode_uint32(v)

    @staticmethod
    def encode_string(v: Union[str, bytes]) -> List[int]:
        """Encode a string/buffer with prepended length byte."""
        if isinstance(v, str):
            v = v.encode("utf-8")
        out = [len(v)]
        out.extend(v)
        return out


class VLQDecoder:
    """VLQ decoding for Kalico protocol integers."""

    @staticmethod
    def decode_int(data: Union[bytes, bytearray, List[int]], pos: int
                   ) -> Tuple[int, int]:
        """Decode a single VLQ integer from data at position pos.

        Returns (value, new_position).
        Handles both signed and unsigned ranges.
        """
        c = data[pos]
        pos += 1
        v = c & 0x7F
        if (c & 0x60) == 0x60:
            v |= -0x20
        while c & 0x80:
            c = data[pos]
            pos += 1
            v = (v << 7) | (c & 0x7F)
        return v, pos

    @staticmethod
    def decode_uint32(data: Union[bytes, bytearray, List[int]], pos: int
                      ) -> Tuple[int, int]:
        """Decode an unsigned 32-bit VLQ integer."""
        v, pos = VLQDecoder.decode_int(data, pos)
        return int(v & 0xFFFFFFFF), pos

    @staticmethod
    def decode_int32(data: Union[bytes, bytearray, List[int]], pos: int
                     ) -> Tuple[int, int]:
        """Decode a signed 32-bit VLQ integer."""
        v, pos = VLQDecoder.decode_int(data, pos)
        # Sign extension for 32-bit
        if v >= 0x80000000:
            v -= 0x100000000
        return v, pos

    @staticmethod
    def decode_string(data: Union[bytes, bytearray, List[int]], pos: int
                      ) -> Tuple[bytes, int]:
        """Decode a length-prefixed string/buffer.

        Returns (bytes_value, new_position).
        """
        l = data[pos]
        pos += 1
        result = bytes(bytearray(data[pos:pos + l]))
        return result, pos + l


# ─── Message Block Framing ──────────────────────────────────────────────


class MessageBlock:
    """Represents a single framed Kalico protocol message block.

    Handles encoding/decoding of the complete wire format:
        [Length][Seq][Content...][CRC16_hi][CRC16_lo][Sync]
    """

    __slots__ = ("seq", "content", "raw_bytes")

    def __init__(self, seq: int, content: Union[bytes, bytearray, List[int]],
                 raw_bytes: Optional[bytes] = None):
        self.seq = seq
        self.content = bytes(bytearray(content))
        self.raw_bytes = raw_bytes

    @property
    def length(self) -> int:
        return MESSAGE_HEADER_SIZE + len(self.content) + MESSAGE_TRAILER_SIZE

    def is_valid(self) -> bool:
        return self.length <= MESSAGE_MAX and self.length >= MESSAGE_MIN

    def encode(self) -> bytes:
        """Encode this message block into wire-format bytes."""
        if not self.is_valid():
            raise ValueError(
                f"Invalid message length: {self.length} "
                f"(max={MESSAGE_MAX}, min={MESSAGE_MIN})"
            )
        header = bytes([
            self.length,
            (self.seq & MESSAGE_SEQ_MASK) | MESSAGE_DEST,
        ])
        payload = bytes(bytearray(self.content))
        body = header + payload
        crc = bytes(crc16_ccitt(body))
        sync = bytes([MESSAGE_SYNC])
        result = body + crc + sync
        self.raw_bytes = result
        return result

    @classmethod
    def decode(cls, data: Union[bytes, bytearray]) -> "MessageBlock":
        """Decode wire-format bytes into a MessageBlock.

        Raises ValueError if CRC or sync byte is invalid.
        """
        buf = bytearray(data) if isinstance(data, bytes) else data
        if len(buf) < MESSAGE_MIN:
            raise ValueError(
                f"Data too short: {len(buf)} < {MESSAGE_MIN}"
            )
        msglen = buf[MESSAGE_POS_LEN]
        if msglen < MESSAGE_MIN or msglen > MESSAGE_MAX:
            raise ValueError(f"Invalid message length: {msglen}")
        if len(buf) < msglen:
            raise ValueError(
                f"Data too short for declared length: {len(buf)} < {msglen}"
            )
        # Verify sync byte
        sync_pos = msglen - MESSAGE_TRAILER_SYNC
        if buf[sync_pos] != MESSAGE_SYNC:
            raise ValueError(
                f"Invalid sync byte: 0x{buf[sync_pos]:02X} "
                f"(expected 0x{MESSAGE_SYNC:02X})"
            )
        # Verify CRC
        body_end = msglen - MESSAGE_TRAILER_SIZE
        body = buf[:body_end]
        expected_crc = list(buf[body_end:body_end + 2])
        actual_crc = crc16_ccitt(body)
        if expected_crc != actual_crc:
            raise ValueError(
                f"CRC mismatch: expected {expected_crc}, got {actual_crc}"
            )
        seq = buf[MESSAGE_POS_SEQ] & MESSAGE_SEQ_MASK
        content = bytes(buf[MESSAGE_HEADER_SIZE:body_end])
        return cls(seq=seq, content=content, raw_bytes=bytes(buf[:msglen]))

    @classmethod
    def find_and_decode(cls, data: Union[bytes, bytearray]
                        ) -> Tuple[Optional["MessageBlock"], int]:
        """Find the first valid message block in a byte stream.

        Returns (MessageBlock or None, bytes_consumed).
        Positive consumed = valid message found.
        Negative consumed = need more data (abs = bytes to keep).
        """
        buf = bytearray(data) if isinstance(data, bytes) else data
        if len(buf) < MESSAGE_MIN:
            return None, -len(buf)
        msglen = buf[MESSAGE_POS_LEN]
        if msglen < MESSAGE_MIN or msglen > MESSAGE_MAX:
            # Bad length, skip this byte
            return None, -MESSAGE_MIN
        if len(buf) < msglen:
            return None, -msglen
        try:
            block = cls.decode(buf[:msglen])
            return block, msglen
        except ValueError:
            # Bad message, skip to find next sync candidate
            return None, -(msglen - 1)

    def __repr__(self) -> str:
        content_hex = self.content.hex()
        return (
            f"MessageBlock(seq={self.seq}, len={self.length}, "
            f"content={content_hex})"
        )


# ─── Message Content (VLQ-encoded command/response) ─────────────────────


def encode_message_content(msgid_bytes: bytes,
                           params: List[int]) -> bytes:
    """Encode message content: message ID (VLQ int) + parameter values.

    msgid_bytes: the pre-encoded message ID bytes (1-5 bytes VLQ)
    params: list of integer parameter values (already encoded per-type)
    """
    return msgid_bytes + bytes(params)


def decode_message_content(data: Union[bytes, bytearray], start_pos: int = 0
                           ) -> Tuple[int, bytes, int]:
    """Decode message content into (msgid, remaining_params_bytes, pos).

    Returns (msgid_value, param_bytes, position_after_msgid).
    """
    msgid, pos = VLQDecoder.decode_int(data, start_pos)
    param_bytes = bytes(data[pos:])
    return msgid, param_bytes, pos


# ─── Utility Functions ──────────────────────────────────────────────────


def bytes_to_hex(data: Union[bytes, bytearray],
                 sep: str = " ", uppercase: bool = True) -> str:
    """Convert bytes to hex dump string."""
    fmt = "%02X" if uppercase else "%02x"
    return sep.join(fmt % b for b in data)


def hex_to_bytes(hex_str: str) -> bytes:
    """Convert hex string (with or without spaces) to bytes."""
    return bytes.fromhex(hex_str.replace(" ", "").replace("\n", ""))


def format_hex_dump(data: Union[bytes, bytearray],
                    bytes_per_line: int = 16) -> str:
    """Format bytes as a traditional hex dump with ASCII side panel."""
    lines = []
    addr = 0
    buf = bytearray(data) if isinstance(data, bytes) else data
    while addr < len(buf):
        chunk = buf[addr:addr + bytes_per_line]
        hex_part = " ".join(f"{b:02X}" for b in chunk)
        hex_part = hex_part.ljust(bytes_per_line * 3 - 1)
        ascii_part = "".join(
            chr(b) if 0x20 <= b < 0x7F else "." for b in chunk
        )
        lines.append(f"{addr:08X}  {hex_part}  |{ascii_part}|")
        addr += bytes_per_line
    return "\n".join(lines)


# ─── Packet Construction Helpers ────────────────────────────────────────


def build_message_packet(seq: int, msgid_vlq: List[int],
                         param_values: Optional[List[int]] = None
                         ) -> bytes:
    """Build a complete wire-format message packet.

    Args:
        seq: Sequence number (0-15)
        msgid_vlq: Pre-encoded message ID as VLQ bytes (list of ints)
        param_values: List of pre-encoded parameter value bytes

    Returns:
        Complete wire-format bytes including header, CRC, and sync
    """
    content = list(msgid_vlq)
    if param_values:
        content.extend(param_values)
    block = MessageBlock(seq=seq, content=content)
    return block.encode()
