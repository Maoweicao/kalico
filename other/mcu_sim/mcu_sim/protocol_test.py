# Built-in protocol smoke test — Kalico identify + config handshake
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Protocol Smoke Test
===================

A self-contained Kalico protocol test that connects to the simulated
MCU via TCP, sends an ``identify`` command, and verifies the response.

This is used by the ``mcu_sim test`` and ``mcu_sim run --oneshot``
commands — no external ``kalico_debug_tool`` needed.
"""

from __future__ import annotations

import logging
import socket
import time
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)

# Kalico protocol constants
MESSAGE_SYNC = 0x7E
MESSAGE_MIN = 5
MESSAGE_MAX = 64

# CRC16-CCITT (matches klippy/msgproto.py)
def _crc16_ccitt(data: bytes) -> int:
    """CRC-16 CCITT — matches klippy/msgproto.py and Kalico firmware."""
    crc = 0xFFFF
    for b in data:
        b ^= crc & 0xFF
        b ^= (b & 0x0F) << 4
        crc = ((b << 8) | (crc >> 8)) ^ (b >> 4) ^ (b << 3)
    return crc & 0xFFFF


def _vlq_encode(values: List[int]) -> bytes:
    """Encode a list of integers using Kalico VLQ encoding."""
    result = bytearray()
    for v in values:
        v_signed = v
        if v_signed < -32 or v_signed >= 96:
            if v_signed < -4096 or v_signed >= 12288:
                if v_signed < -524288 or v_signed >= 1572864:
                    if v_signed < -67108864 or v_signed >= 201326592:
                        # 5-byte
                        v_u = v_signed & 0xFFFFFFFF
                        result.append(0x80 | 0x40 | 0x20 | 0x10 | ((v_u >> 28) & 0x0F))
                        result.append((v_u >> 21) & 0x7F)
                        result.append((v_u >> 14) & 0x7F)
                        result.append((v_u >> 7) & 0x7F)
                        result.append(v_u & 0x7F)
                        continue
                    # 4-byte
                    v_u = v_signed & 0xFFFFFFFF
                    result.append(0x80 | 0x40 | 0x20 | ((v_u >> 21) & 0x0F))
                    result.append((v_u >> 14) & 0x7F)
                    result.append((v_u >> 7) & 0x7F)
                    result.append(v_u & 0x7F)
                    continue
                # 3-byte
                v_u = v_signed & 0xFFFFFFFF
                result.append(0x80 | 0x40 | ((v_u >> 14) & 0x1F))
                result.append((v_u >> 7) & 0x7F)
                result.append(v_u & 0x7F)
                continue
            # 2-byte
            v_u = v_signed & 0xFFFFFFFF
            result.append(0x80 | ((v_u >> 7) & 0x3F))
            result.append(v_u & 0x7F)
            continue
        # 1-byte (signed range)
        result.append(v_signed & 0x7F)
    return bytes(result)


def _vlq_decode(data: bytes, offset: int = 0) -> Tuple[int, int]:
    """Decode one VLQ value. Returns (value, new_offset)."""
    b0 = data[offset]
    if not (b0 & 0x80):
        # 1 byte: 0xxxxxxx, signed range -32..95
        val = b0
        if val >= 96:
            val -= 128
        return val, offset + 1

    if not (b0 & 0x40):
        # 2 bytes
        b1 = data[offset + 1]
        val = ((b0 & 0x3F) << 7) | b1
        if val >= 4096:
            val -= 8192
        return val, offset + 2

    if not (b0 & 0x20):
        # 3 bytes
        b1 = data[offset + 1]
        b2 = data[offset + 2]
        val = ((b0 & 0x1F) << 14) | (b1 << 7) | b2
        if val >= 524288:
            val -= 1048576
        return val, offset + 3

    if not (b0 & 0x10):
        # 4 bytes
        b1 = data[offset + 1]
        b2 = data[offset + 2]
        b3 = data[offset + 3]
        val = ((b0 & 0x0F) << 21) | (b1 << 14) | (b2 << 7) | b3
        if val >= 67108864:
            val -= 134217728
        return val, offset + 4

    # 5 bytes
    b1 = data[offset + 1]
    b2 = data[offset + 2]
    b3 = data[offset + 3]
    b4 = data[offset + 4]
    val = ((b0 & 0x0F) << 28) | (b1 << 21) | (b2 << 14) | (b3 << 7) | b4
    if val >= 2147483648:
        val -= 4294967296
    return val, offset + 5


def build_message(msgid: int, seq: int = 0) -> bytes:
    """Build a Kalico protocol message block.

    Args:
        msgid: Command message ID.
        seq:   Sequence number (0-15).
    """
    content = _vlq_encode([msgid])
    length = 2 + len(content) + 2 + 1  # len + content + crc + sync
    if length < MESSAGE_MIN:
        length = MESSAGE_MIN
    if length > MESSAGE_MAX:
        raise ValueError(f"Message too long: {length} > {MESSAGE_MAX}")

    seq_byte = (0x10 | (seq & 0x0F)).to_bytes(1, "little")
    header = bytes([length]) + seq_byte
    pre_crc = header + content
    crc = _crc16_ccitt(pre_crc)
    crc_bytes = bytes([(crc >> 8) & 0xFF, crc & 0xFF])

    block = pre_crc + crc_bytes + bytes([MESSAGE_SYNC])
    return block


def parse_response(data: bytes) -> List[Tuple[int, List[int]]]:
    """Parse Kalico response messages. Returns list of (msgid, params)."""
    messages = []
    i = 0
    while i < len(data):
        # Find sync byte
        sync_pos = data.find(MESSAGE_SYNC, i)
        if sync_pos < 0:
            break
        block_start = sync_pos - (data[sync_pos - 1] if sync_pos > 0 else 5) + 1
        block_start = max(0, block_start)
        block = data[block_start : sync_pos + 1]

        if len(block) >= MESSAGE_MIN:
            length = block[0]
            if 2 < len(block):
                # VLQ decode content
                try:
                    msgid, offset = _vlq_decode(block, 2)
                    params: List[int] = []
                    while offset < len(block) - 3:  # before CRC+SYNC
                        val, offset = _vlq_decode(block, offset)
                        params.append(val)
                    messages.append((msgid, params))
                except (IndexError, ValueError):
                    pass
        i = sync_pos + 1
    return messages


def run_smoke_test(host: str = "127.0.0.1", port: int = 0,
                   timeout: float = 10.0) -> int:
    """Run the identify protocol smoke test against a simulated MCU.

    Connects to the TCP virtual serial port, sends an ``identify``
    command, and prints the response.

    Returns:
        Exit code (0 = success, 1 = failure).
    """
    if port == 0:
        logger.error("No port specified for smoke test")
        return 1

    logger.info("Connecting to simulated MCU at %s:%d...", host, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)

    try:
        sock.connect((host, port))
    except (ConnectionRefusedError, socket.timeout) as exc:
        logger.error("Connection failed: %s", exc)
        return 1

    logger.info("Connected. Sending identify command (msgid=1, offset=0, count=40)...")

    # Build identify command: msgid=1, offset=0, count=40
    # Kalico identify:  command_identify offset=%u count=%c
    # VLQ: msgid=1, offset=0, count=40 (byte)
    content = _vlq_encode([1]) + _vlq_encode([0]) + _vlq_encode([40])
    header = bytes([2 + len(content) + 2 + 1]) + bytes([0x10])  # length + seq
    pre_crc = header + content
    crc = _crc16_ccitt(pre_crc)
    crc_bytes = bytes([(crc >> 8) & 0xFF, crc & 0xFF])
    identify_msg = pre_crc + crc_bytes + bytes([MESSAGE_SYNC])

    # Pad to minimum message size
    if len(identify_msg) < MESSAGE_MIN:
        # Pad with a longer content
        identify_msg = build_message(1, seq=0)
    else:
        pass  # Already padded

    logger.debug("Sending %d bytes: %s", len(identify_msg), identify_msg.hex())

    try:
        sock.sendall(identify_msg)
    except OSError as exc:
        logger.error("Send failed: %s", exc)
        sock.close()
        return 1

    # Read response
    logger.info("Waiting for identify_response (msgid=0)...")
    all_data = bytearray()

    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            chunk = sock.recv(4096)
            if not chunk:
                break
            all_data.extend(chunk)

            # Parse any responses
            messages = parse_response(bytes(all_data))
            for msgid, params in messages:
                if msgid == 0:          # identify_response
                    logger.info("✓ Received identify_response!")
                    logger.info("  msgid=%d, params=%s", msgid, params)
                    if len(params) >= 2:
                        offset = params[0]
                        data_len = params[1]
                        logger.info("  offset=%d, data_length=%d", offset, data_len)
                    print("\n" + "=" * 60)
                    print("  SMOKE TEST: PASSED ✓")
                    print("  identify_response received from simulated MCU")
                    print("=" * 60)
                    sock.close()
                    return 0

            if messages:
                logger.debug("Parsed %d messages (no identify_response yet)", len(messages))

        except socket.timeout:
            continue
        except OSError:
            break

    sock.close()

    if all_data:
        logger.warning("Received %d bytes but no identify_response found", len(all_data))
        logger.debug("Raw data: %s", bytes(all_data).hex())
    else:
        logger.error("No response received from MCU")

    print("\n" + "=" * 60)
    print("  SMOKE TEST: FAILED ✗")
    print("  No identify_response from simulated MCU")
    print("=" * 60)
    return 1
