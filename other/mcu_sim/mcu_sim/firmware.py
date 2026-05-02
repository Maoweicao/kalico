# Firmware file loader — Intel HEX, raw binary, and ELF
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Firmware Loader
===============

Parses and validates firmware image files.  Supports three formats:

* **Intel HEX** (.hex) — text-based, contains address information
* **Raw binary** (.bin) — flat binary blob, needs a load address
* **ELF** (.elf) — full executable with symbol information

Also provides architecture detection from ELF headers and hex address ranges.
"""

from __future__ import annotations

import dataclasses
import enum
import struct
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class McuArch(enum.Enum):
    """Known MCU architectures."""
    AVR = "avr"
    ARM_CORTEX_M = "arm-cortex-m"
    XTENSA = "xtensa"
    UNKNOWN = "unknown"

    @property
    def display_name(self) -> str:
        _names = {
            McuArch.AVR: "AVR (8-bit)",
            McuArch.ARM_CORTEX_M: "ARM Cortex-M (32-bit)",
            McuArch.XTENSA: "Xtensa (ESP32)",
            McuArch.UNKNOWN: "Unknown",
        }
        return _names[self]


# ---------------------------------------------------------------------------
# Intel HEX helpers
# ---------------------------------------------------------------------------

def _parse_hex_line(line: str) -> Optional[Tuple[int, int, bytes]]:
    """Parse a single Intel HEX record line.

    Returns ``(byte_count, address, data)`` or ``None`` for EOF.
    """
    line = line.strip()
    if not line or line[0] != ":":
        return None
    try:
        byte_count = int(line[1:3], 16)
        address = int(line[3:7], 16)
        record_type = int(line[7:9], 16)
    except ValueError:
        return None

    if record_type == 1:          # EOF
        return None
    if record_type != 0:          # skip extended address etc.
        return None

    data_hex = line[9 : 9 + byte_count * 2]
    data = bytes(int(data_hex[i : i + 2], 16) for i in range(0, len(data_hex), 2))
    return byte_count, address, data


# ---------------------------------------------------------------------------
# ELF helpers (minimal — just read machine type and entry point)
# ---------------------------------------------------------------------------

_ELF_MAGIC = b"\x7fELF"
_EM_AVR = 83
_EM_ARM = 40
_EM_XTENSA = 94


def _elf_machine_to_arch(machine: int) -> McuArch:
    if machine == _EM_AVR:
        return McuArch.AVR
    if machine == _EM_ARM:
        return McuArch.ARM_CORTEX_M
    if machine == _EM_XTENSA:
        return McuArch.XTENSA
    return McuArch.UNKNOWN


# ---------------------------------------------------------------------------
# FirmwareFile
# ---------------------------------------------------------------------------

@dataclasses.dataclass
class FirmwareFile:
    """Represents a loaded firmware image ready for simulation.

    Attributes:
        path:              Original file path.
        format:            ``"hex"``, ``"bin"``, or ``"elf"``.
        arch:              Detected architecture.
        data:              Raw binary payload (flat, contiguous bytes).
        load_address:      Base address where data should be loaded in memory.
        entry_point:       Optional entry-point address (from ELF).
        total_size:        Total binary size in bytes.
    """

    path: Path
    format: str
    arch: McuArch
    data: bytes
    load_address: int
    entry_point: Optional[int] = None
    total_size: int = 0

    def __post_init__(self) -> None:
        if self.total_size == 0:
            self.total_size = len(self.data)

    @classmethod
    def from_path(cls, path: str | Path) -> "FirmwareFile":
        """Auto-detect format and load a firmware file."""
        path = Path(path).resolve()
        if not path.is_file():
            raise FileNotFoundError(f"Firmware file not found: {path}")

        suffix = path.suffix.lower()
        if suffix == ".hex":
            return cls._from_hex(path)
        if suffix == ".bin":
            return cls._from_bin(path)
        if suffix in (".elf", ".axf", ".out"):
            return cls._from_elf(path)

        # Try to detect by content
        with open(path, "rb") as fh:
            header = fh.read(16)
        if header[:4] == _ELF_MAGIC:
            return cls._from_elf(path)
        if header[0:1] == b":":
            return cls._from_hex(path)
        # Default to binary
        return cls._from_bin(path)

    # ---- HEX loader ----

    @classmethod
    def _from_hex(cls, path: Path) -> "FirmwareFile":
        segments: Dict[int, bytearray] = {}
        base_addr = 0
        min_addr = 0xFFFFFFFF
        max_addr = 0

        with open(path, "r", encoding="ascii", errors="ignore") as fh:
            for raw_line in fh:
                parsed = _parse_hex_line(raw_line)
                if parsed is None:
                    continue
                _, addr_lo, data = parsed
                addr = base_addr | addr_lo
                if addr not in segments:
                    segments[addr] = bytearray()
                segments[addr].extend(data)
                if addr < min_addr:
                    min_addr = addr
                end = addr + len(data)
                if end > max_addr:
                    max_addr = end

        if not segments:
            raise ValueError(f"No data found in HEX file: {path}")

        # Merge segments into contiguous binary
        load_address = min_addr
        total_len = max_addr - min_addr
        data = bytearray(total_len)

        for seg_addr, seg_data in segments.items():
            offset = seg_addr - load_address
            data[offset : offset + len(seg_data)] = seg_data

        arch = _guess_arch_from_address(load_address, max_addr)

        return cls(
            path=path,
            format="hex",
            arch=arch,
            data=bytes(data),
            load_address=load_address,
        )

    # ---- BIN loader ----

    @classmethod
    def _from_bin(cls, path: Path) -> "FirmwareFile":
        data = path.read_bytes()
        arch = _guess_arch_from_size(len(data))
        return cls(
            path=path,
            format="bin",
            arch=arch,
            data=data,
            load_address=0,
            entry_point=None,
        )

    # ---- ELF loader ----

    @classmethod
    def _from_elf(cls, path: Path) -> "FirmwareFile":
        data_buf = path.read_bytes()

        # Verify ELF magic
        if data_buf[:4] != _ELF_MAGIC:
            raise ValueError(f"Not a valid ELF file: {path}")

        # Read ELF header
        is_64bit = data_buf[4] == 2
        is_le = data_buf[5] == 1

        if is_64bit:
            endian = "<" if is_le else ">"
            hdr = struct.unpack_from(endian + "HHIQQQIHHHHHH", data_buf, 16)
            machine, entry = hdr[0], hdr[2]
        else:
            endian = "<" if is_le else ">"
            hdr = struct.unpack_from(endian + "HHIIIIIHHHHHH", data_buf, 16)
            machine, entry = hdr[0], hdr[3]

        arch = _elf_machine_to_arch(machine)

        # Extract loadable segments — flattened to binary
        # We extract from program headers for simplicity
        if is_64bit:
            phoff = struct.unpack_from(endian + "Q", data_buf, 32)[0]
            phentsize = struct.unpack_from(endian + "H", data_buf, 54)[0]
            phnum = struct.unpack_from(endian + "H", data_buf, 56)[0]
            phdr_fmt = endian + "IIQQQQQQ"
            phdr_size = 56
        else:
            phoff = struct.unpack_from(endian + "I", data_buf, 28)[0]
            phentsize = struct.unpack_from(endian + "H", data_buf, 42)[0]
            phnum = struct.unpack_from(endian + "H", data_buf, 44)[0]
            phdr_fmt = endian + "IIIIIIII"
            phdr_size = 32

        segments: List[Tuple[int, bytes]] = []
        min_addr = 0xFFFFFFFF
        max_addr = 0

        for i in range(phnum):
            offset = phoff + i * phdr_size
            p_type, p_offset, p_vaddr = struct.unpack_from(
                phdr_fmt[:12], data_buf, offset
            )
            if p_type != 1:          # PT_LOAD
                continue
            if is_64bit:
                _, _, p_filesz, p_memsz = struct.unpack_from(
                    endian + "QQQQ", data_buf, offset + 24
                )
            else:
                _, _, p_filesz, p_memsz = struct.unpack_from(
                    endian + "IIII", data_buf, offset + 16
                )

            if p_filesz == 0:
                continue

            seg_data = data_buf[p_offset : p_offset + p_filesz]
            segments.append((p_vaddr, seg_data))
            if p_vaddr < min_addr:
                min_addr = p_vaddr
            end = p_vaddr + max(p_filesz, p_memsz)
            if end > max_addr:
                max_addr = end

        if not segments:
            raise ValueError(f"No loadable segments in ELF: {path}")

        # Flatten to contiguous binary
        load_address = min_addr
        total_len = max_addr - min_addr
        flat = bytearray(total_len)
        for vaddr, sdata in segments:
            offset = vaddr - load_address
            flat[offset : offset + len(sdata)] = sdata

        return cls(
            path=path,
            format="elf",
            arch=arch,
            data=bytes(flat),
            load_address=load_address,
            entry_point=entry,
        )


# ---------------------------------------------------------------------------
# Architecture guessing heuristics (for formats that lack metadata)
# ---------------------------------------------------------------------------

def _guess_arch_from_address(min_addr: int, max_addr: int) -> McuArch:
    """Guess architecture from typical address ranges."""
    # AVR flash typically starts at 0x0000
    # ARM Cortex-M flash typically starts at 0x08000000
    # ESP32 flash typically starts at 0x3F400000 or 0x40000000
    if min_addr >= 0x3F000000:
        return McuArch.XTENSA
    if min_addr >= 0x08000000:
        return McuArch.ARM_CORTEX_M
    if min_addr < 0x40000 and max_addr < 0x100000:
        return McuArch.AVR
    return McuArch.UNKNOWN


def _guess_arch_from_size(size: int) -> McuArch:
    """Guess architecture from typical firmware sizes."""
    if size <= 256 * 1024:         # ≤256KB → likely AVR
        return McuArch.AVR
    return McuArch.UNKNOWN
