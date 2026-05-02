# Protocol event export
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Event Export Module
===================

Exports protocol events to various formats:
  - CSV: Spreadsheet-compatible format
  - Plain text: Human-readable log
  - Hex dump: Traditional hex+ASCII dump
"""

import csv
import io
import os
from typing import List, Optional, TextIO

from .logger import ProtocolEvent
from ..protocol.codec import format_hex_dump


class Exporter:
    """Exports protocol events to various output formats."""

    @staticmethod
    def to_csv(events: List[ProtocolEvent],
               filepath: Optional[str] = None) -> Optional[str]:
        """Export events as CSV.

        Args:
            events: List of protocol events
            filepath: Optional output file path

        Returns:
            CSV content as string if filepath is None, else None
        """
        output = io.StringIO() if filepath is None else None
        f: TextIO = open(filepath, "w", newline="", encoding="utf-8") \
            if filepath else output  # type: ignore

        try:
            writer = csv.writer(f)
            writer.writerow([
                "ID", "Timestamp", "Direction", "Name", "Seq",
                "Raw Hex", "Error"
            ])
            for ev in events:
                writer.writerow([
                    ev.id,
                    round(ev.timestamp, 6),
                    ev.direction,
                    ev.msg_name,
                    ev.seq,
                    ev.raw_hex,
                    ev.error,
                ])
        finally:
            if filepath and hasattr(f, "close"):
                f.close()

        if output:
            return output.getvalue()
        return None

    @staticmethod
    def to_text(events: List[ProtocolEvent],
                filepath: Optional[str] = None,
                include_params: bool = True) -> Optional[str]:
        """Export events as human-readable text.

        Args:
            events: List of protocol events
            filepath: Optional output file path
            include_params: Whether to include decoded parameters

        Returns:
            Text content as string if filepath is None, else None
        """
        lines = []
        lines.append(f"# Kalico Protocol Log - {len(events)} events")
        lines.append(f"# Generated: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        for ev in events:
            ts_str = f"[{ev.timestamp:.3f}]"
            line = f"{ts_str} {ev.direction:>2s} [{ev.seq:02X}] {ev.msg_name}"
            lines.append(line)
            if include_params and ev.params:
                # Format params as compact key=value pairs
                param_strs = []
                for k, v in ev.params.items():
                    if k.startswith("#"):
                        continue
                    if isinstance(v, bytes):
                        param_strs.append(f"{k}={v.hex()}")
                    else:
                        param_strs.append(f"{k}={v}")
                if param_strs:
                    lines.append(f"           {', '.join(param_strs)}")
            if ev.error:
                lines.append(f"    ERROR: {ev.error}")
            lines.append("")

        output = "\n".join(lines)

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(output)
            return None
        return output

    @staticmethod
    def to_hex_dump(events: List[ProtocolEvent],
                    filepath: Optional[str] = None) -> Optional[str]:
        """Export events as traditional hex dump.

        Args:
            events: List of protocol events
            filepath: Optional output file path

        Returns:
            Hex dump content as string if filepath is None, else None
        """
        lines = []
        lines.append(f"Kalico Protocol Hex Dump - {len(events)} events")
        lines.append("=" * 60)
        lines.append("")

        for ev in events:
            header = (
                f"--- {ev.direction} [{ev.timestamp:.3f}] "
                f"{ev.msg_name} (seq={ev.seq}) ---"
            )
            lines.append(header)
            lines.append(format_hex_dump(ev.raw_bytes))
            lines.append("")

        output = "\n".join(lines)

        if filepath:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(output)
            return None
        return output
