# Hex dump viewer panel
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Hex View Panel
==============

Displays raw message bytes as a traditional hex dump with:
  - Upper half: hex dump (address + hex + ASCII)
  - Lower half: protocol field breakdown
  - Clickable bytes with field highlighting
  - Link to log panel for event selection
"""

import tkinter as tk
from tkinter import ttk
from typing import Optional

from ...log.logger import LogEngine
from ...protocol.codec import (
    MESSAGE_HEADER_SIZE, MESSAGE_TRAILER_SIZE,
    MESSAGE_POS_LEN, MESSAGE_POS_SEQ,
    MESSAGE_TRAILER_CRC, MESSAGE_TRAILER_SYNC,
    MESSAGE_DEST, MESSAGE_SYNC,
    format_hex_dump, bytes_to_hex,
)


class HexPanel(ttk.Frame):
    """Hex dump viewer for raw protocol bytes."""

    def __init__(self, parent, log_engine: LogEngine):
        super().__init__(parent)
        self.log_engine = log_engine
        self._current_raw: bytes = b""

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the hex view panel UI."""
        paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ─── Upper: Hex Dump ─────────────────────────────────────────
        upper_frame = ttk.LabelFrame(paned, text="Hex Dump", padding=5)
        paned.add(upper_frame, weight=3)

        self.hex_text = tk.Text(
            upper_frame, font=("Consolas", 10), wrap=tk.NONE,
            state="disabled", bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white"
        )
        self.hex_text.pack(fill=tk.BOTH, expand=True)

        # Scrollbars for hex dump
        h_scroll = ttk.Scrollbar(upper_frame, orient="horizontal",
                                 command=self.hex_text.xview)
        h_scroll.pack(fill=tk.X)
        self.hex_text.config(xscrollcommand=h_scroll.set)

        v_scroll = ttk.Scrollbar(upper_frame, orient="vertical",
                                 command=self.hex_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.hex_text.config(yscrollcommand=v_scroll.set)

        # ─── Lower: Field Breakdown ───────────────────────────────────
        lower_frame = ttk.LabelFrame(paned, text="协议字段解析", padding=5)
        paned.add(lower_frame, weight=2)

        self.field_text = tk.Text(
            lower_frame, font=("Consolas", 10), wrap=tk.WORD,
            state="disabled", height=8
        )
        self.field_text.pack(fill=tk.BOTH, expand=True)

        # ─── Event selector ──────────────────────────────────────────
        selector_frame = ttk.Frame(self, padding=5)
        selector_frame.pack(fill=tk.X)

        ttk.Label(selector_frame, text="选择事件:").pack(side=tk.LEFT)
        self.event_combo = ttk.Combobox(
            selector_frame, width=60, state="readonly"
        )
        self.event_combo.pack(side=tk.LEFT, padx=5)
        self.event_combo.bind("<<ComboboxSelected>>", self._on_event_selected)

        ttk.Button(selector_frame, text="刷新",
                   command=self._refresh_events).pack(side=tk.LEFT, padx=5)

    def _refresh_events(self) -> None:
        """Refresh the event selector combobox."""
        events = self.log_engine.get_all_events()
        items = []
        for ev in events[-100:]:  # Show last 100 events
            ts_str = f"{ev.timestamp:.3f}"
            items.append(
                f"#{ev.id} [{ts_str}] {ev.direction} {ev.msg_name}"
            )
        self.event_combo["values"] = items
        if items:
            self.event_combo.set(items[-1])
            self._on_event_selected(None)

    def _on_event_selected(self, event) -> None:
        """Handle event selection from combobox."""
        selection = self.event_combo.get()
        if not selection:
            return
        # Parse event ID from selection
        try:
            event_id = int(selection.split("#")[1].split("]")[0].split("[")[0])
        except (IndexError, ValueError):
            return

        # Find the event
        events = self.log_engine.get_all_events()
        for ev in events:
            if ev.id == event_id:
                self._display_event(ev)
                break

    def _display_event(self, event) -> None:
        """Display a protocol event in the hex viewer."""
        data = event.raw_bytes
        self._current_raw = data
        self._show_hex_dump(data)
        self._show_field_breakdown(data)

    def _show_hex_dump(self, data: bytes) -> None:
        """Show hex dump of raw data."""
        self.hex_text.config(state="normal")
        self.hex_text.delete("1.0", tk.END)

        if not data:
            self.hex_text.insert(tk.END, "(无数据)")
        else:
            dump = format_hex_dump(data)
            self.hex_text.insert(tk.END, dump)

        self.hex_text.config(state="disabled")

    def _show_field_breakdown(self, data: bytes) -> None:
        """Show protocol field breakdown."""
        self.field_text.config(state="normal")
        self.field_text.delete("1.0", tk.END)

        if len(data) < 5:
            self.field_text.insert(
                tk.END, f"数据太短: {len(data)} 字节 (最小 {5} 字节)"
            )
            self.field_text.config(state="disabled")
            return

        msglen = data[MESSAGE_POS_LEN]
        seq = data[MESSAGE_POS_SEQ] & 0x0F
        dest = data[MESSAGE_POS_SEQ] & 0xF0
        sync_pos = msglen - MESSAGE_TRAILER_SYNC
        crc_start = msglen - MESSAGE_TRAILER_CRC

        self.field_text.insert(tk.END, "┌─ Kalico 协议消息块 ────────────────────────────────┐\n")
        self.field_text.insert(
            tk.END,
            f"│ 偏移 0:  Length    = {msglen} 字节 "
            f"(0x{msglen:02X})"
            f"{'  ✓' if 5 <= msglen <= 64 else '  ✗ 越界'}\n"
        )
        self.field_text.insert(
            tk.END,
            f"│ 偏移 1:  Sequence  = {seq} (0x{seq:X})  "
            f"| Dest=0x{dest>>4:X}"
            f"{'  ✓' if dest == MESSAGE_DEST else '  ✗ 无效'}\n"
        )

        # Content bytes
        content = data[MESSAGE_HEADER_SIZE:crc_start]
        self.field_text.insert(
            tk.END,
            f"│ 偏移 2:  Content   = {len(content)} 字节 "
            f"(VLQ 编码命令/响应)\n"
        )

        # CRC
        crc_bytes = data[crc_start:crc_start + 2]
        self.field_text.insert(
            tk.END,
            f"│ 偏移 {crc_start}: CRC-16    = 0x{crc_bytes[0]:02X}{crc_bytes[1]:02X}\n"
        )

        # Sync
        sync_byte = data[sync_pos]
        sync_ok = sync_byte == MESSAGE_SYNC
        self.field_text.insert(
            tk.END,
            f"│ 偏移 {sync_pos}:  Sync      = 0x{sync_byte:02X}"
            f"{'  ✓' if sync_ok else f'  ✗ 应为 0x{MESSAGE_SYNC:02X}'}\n"
        )

        self.field_text.insert(tk.END, "└────────────────────────────────────────────────────┘\n")

        # Raw hex summary
        self.field_text.insert(tk.END, f"\n完整消息 ({len(data)} 字节): ")
        self.field_text.insert(tk.END, bytes_to_hex(data))

        self.field_text.config(state="disabled")
