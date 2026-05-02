# Protocol log viewer panel
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Protocol Log Panel
==================

Displays parsed protocol events in a scrollable table view with:
  - Columns: #, Time, Dir, Seq, Message Name, Parameters, Raw
  - Color-coded: Tx=blue, Rx=green, Error=red
  - Real-time updates via callback from LogEngine
  - Right-click context menu (copy, export)
  - Filter toolbar
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Optional

from ...log.logger import LogEngine, ProtocolEvent
from ...log.filter import EventFilter


# Tag colors
COLOR_TX = "#1a73e8"     # Blue for transmitted
COLOR_RX = "#0d652d"     # Green for received
COLOR_ERROR = "#d93025"  # Red for errors
COLOR_BG = "#ffffff"
COLOR_ALT_ROW = "#f5f5f5"


class LogPanel(ttk.Frame):
    """Table view of protocol events with filtering."""

    def __init__(self, parent, log_engine: LogEngine):
        super().__init__(parent)
        self.log_engine = log_engine
        self.filter = EventFilter()
        self._events: List[ProtocolEvent] = []
        self._auto_scroll = True

        self._build_ui()
        self.refresh()

    def _build_ui(self) -> None:
        """Build the log panel UI."""
        # ─── Filter toolbar ──────────────────────────────────────────
        filter_frame = ttk.Frame(self, padding=5)
        filter_frame.pack(fill=tk.X)

        ttk.Label(filter_frame, text="过滤:").pack(side=tk.LEFT)

        self.filter_var = tk.StringVar()
        self.filter_var.trace("w", lambda *a: self._apply_filter())
        ttk.Entry(filter_frame, textvariable=self.filter_var,
                  width=20).pack(side=tk.LEFT, padx=5)

        self.dir_filter_var = tk.StringVar(value="全部")
        dir_combo = ttk.Combobox(
            filter_frame, textvariable=self.dir_filter_var,
            values=["全部", "Tx", "Rx", "错误"],
            width=6, state="readonly"
        )
        dir_combo.pack(side=tk.LEFT, padx=5)
        dir_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_filter())

        ttk.Button(filter_frame, text="清除过滤", width=8,
                   command=self._clear_filter).pack(side=tk.LEFT, padx=5)

        self.auto_scroll_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(filter_frame, text="自动滚动",
                        variable=self.auto_scroll_var).pack(side=tk.RIGHT)

        # Count label
        self.count_label = ttk.Label(filter_frame, text="事件: 0")
        self.count_label.pack(side=tk.RIGHT, padx=10)

        # ─── Treeview ────────────────────────────────────────────────
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "time", "dir", "seq", "name", "params", "raw")
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings",
            selectmode="extended"
        )

        # Define headings
        self.tree.heading("id", text="#")
        self.tree.heading("time", text="时间")
        self.tree.heading("dir", text="方向")
        self.tree.heading("seq", text="SEQ")
        self.tree.heading("name", text="消息名称")
        self.tree.heading("params", text="参数")
        self.tree.heading("raw", text="原始数据(Hex)")

        # Column widths
        self.tree.column("id", width=50, minwidth=40)
        self.tree.column("time", width=100, minwidth=80)
        self.tree.column("dir", width=50, minwidth=40)
        self.tree.column("seq", width=50, minwidth=40)
        self.tree.column("name", width=180, minwidth=120)
        self.tree.column("params", width=300, minwidth=150)
        self.tree.column("raw", width=200, minwidth=100)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal",
                            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
                            xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Bind right-click
        self.tree.bind("<Button-3>", self._show_context_menu)
        self.tree.bind("<Button-2>", self._show_context_menu)  # macOS

        # Double-click to show raw hex
        self.tree.bind("<Double-1>", self._on_double_click)

    def on_event(self, event: ProtocolEvent) -> None:
        """Callback from LogEngine when a new event is logged.

        Called from background thread - use root.after() for GUI update.
        """
        root = self.winfo_toplevel()
        root.after(0, self._insert_event, event)

    def _insert_event(self, event: ProtocolEvent) -> None:
        """Insert a single event into the treeview."""
        # Format time
        time_str = f"{event.timestamp:.6f}"

        # Format params
        params_str = ""
        if event.params:
            param_parts = []
            for k, v in event.params.items():
                if k.startswith("#"):
                    continue
                if isinstance(v, bytes):
                    param_parts.append(f"{k}={v.hex()}")
                else:
                    param_parts.append(f"{k}={v}")
            params_str = ", ".join(param_parts)

        # Truncate raw hex for display
        raw_str = event.raw_hex
        if len(raw_str) > 40:
            raw_str = raw_str[:38] + "..."

        values = (
            str(event.id),
            time_str,
            event.direction,
            f"{event.seq:02X}",
            event.msg_name,
            params_str,
            raw_str,
        )

        # Insert with tags for coloring
        tags = ()
        if event.error:
            tags = ("error",)
        elif event.direction == "Tx":
            tags = ("tx",)
        else:
            tags = ("rx",)

        item_id = self.tree.insert("", tk.END, values=values, tags=tags)

        # Auto-scroll
        if self.auto_scroll_var.get():
            self.tree.see(item_id)

        # Update count
        self._update_count()

    def _update_count(self) -> None:
        """Update the event count display."""
        count = len(self.tree.get_children())
        self.count_label.config(text=f"事件: {count}")

    def refresh(self) -> None:
        """Refresh the treeview from the log engine."""
        self.tree.delete(*self.tree.get_children())
        for event in self.log_engine.get_all_events():
            self._insert_event(event)

    def _apply_filter(self) -> None:
        """Apply current filter settings."""
        text = self.filter_var.get().strip()
        dir_val = self.dir_filter_var.get()

        self.filter.reset()

        if text:
            self.filter.set_text_search(text, case_sensitive=False)

        if dir_val == "Tx":
            self.filter.set_direction("Tx")
        elif dir_val == "Rx":
            self.filter.set_direction("Rx")
        elif dir_val == "错误":
            self.filter.set_only_errors(True)

        # Re-populate
        self.tree.delete(*self.tree.get_children())
        all_events = self.log_engine.get_all_events()
        filtered = self.filter.apply(all_events)
        for event in filtered:
            self._insert_event(event)

    def _clear_filter(self) -> None:
        """Clear all filters and show all events."""
        self.filter_var.set("")
        self.dir_filter_var.set("全部")
        self.filter.reset()
        self.refresh()

    def _show_context_menu(self, event) -> None:
        """Right-click context menu."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="复制选中行", command=self._copy_selected)
        menu.add_command(label="复制全部", command=self._copy_all)
        menu.add_separator()
        menu.add_command(label="清除显示", command=self._clear_display)
        menu.add_command(label="导出为 CSV...", command=self._export_csv)
        menu.add_command(label="导出为文本...", command=self._export_text)
        menu.tk_popup(event.x_root, event.y_root)

    def _copy_selected(self) -> None:
        """Copy selected rows to clipboard."""
        selected = self.tree.selection()
        if not selected:
            return
        lines = []
        for item_id in selected:
            values = self.tree.item(item_id, "values")
            lines.append("\t".join(str(v) for v in values))
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)

    def _copy_all(self) -> None:
        """Copy all rows to clipboard."""
        lines = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            lines.append("\t".join(str(v) for v in values))
        text = "\n".join(lines)
        self.clipboard_clear()
        self.clipboard_append(text)

    def _clear_display(self) -> None:
        """Clear the treeview display (not the log engine buffer)."""
        self.tree.delete(*self.tree.get_children())
        self._update_count()

    def _export_csv(self) -> None:
        """Export visible events as CSV."""
        from ...log.export import Exporter
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if path:
            all_events = self.log_engine.get_all_events()
            Exporter.to_csv(all_events, path)

    def _export_text(self) -> None:
        """Export visible events as text."""
        from ...log.export import Exporter
        from tkinter import filedialog
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if path:
            all_events = self.log_engine.get_all_events()
            Exporter.to_text(all_events, path)

    def _on_double_click(self, event) -> None:
        """Handle double-click to show details."""
        item_id = self.tree.focus()
        if not item_id:
            return
        values = self.tree.item(item_id, "values")
        if not values:
            return
        # Show details in a popup
        detail_win = tk.Toplevel(self)
        detail_win.title(f"消息详情 #{values[0]}")
        detail_win.geometry("600x300")
        detail_win.transient(self)

        text = tk.Text(detail_win, wrap=tk.WORD, font=("Consolas", 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        text.insert(tk.END, f"事件 ID: {values[0]}\n")
        text.insert(tk.END, f"时间戳: {values[1]}\n")
        text.insert(tk.END, f"方向: {values[2]}\n")
        text.insert(tk.END, f"序列号: {values[3]}\n")
        text.insert(tk.END, f"消息名称: {values[4]}\n")
        text.insert(tk.END, f"参数: {values[5]}\n")
        text.insert(tk.END, f"原始 Hex: {values[6]}\n")
        text.config(state="disabled")
