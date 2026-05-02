# Kalico Debug Tool - Main GUI Window
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Main GUI Window
===============

Tkinter-based multi-tab main window with:
  - Notebook (tabbed) layout for all panels
  - Status bar showing connection state, message counts, errors
  - Menu bar with File/View/Help options
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .. import __version__, __app_name__
from ..log.logger import LogEngine, ProtocolEvent
from ..protocol.codec import MessageBlock
from ..protocol.parser import Parser, ParsedMessage
from ..io.serial_io import SerialIO, ConnectionState as SerialState
from ..io.can_io import CANIO
from ..io.capture import CaptureManager
from ..simulator.virtual_mcu import VirtualMCU

from .panels.connection_panel import ConnectionPanel
from .panels.log_panel import LogPanel
from .panels.hex_panel import HexPanel
from .panels.simulator_panel import SimulatorPanel
from .panels.ai_cli_panel import AICliPanel
from .panels.benchmark_panel import BenchmarkPanel


class DebugToolWindow:
    """Main application window for Kalico protocol debugger."""

    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"{__app_name__} v{__version__}")
        root.geometry("1200x800")
        root.minsize(800, 600)

        # Core components
        self.log_engine = LogEngine(max_events=10000)
        self.parser = Parser()
        self.serial_io = SerialIO(
            on_data=self._on_serial_data,
            on_error=self._on_serial_error,
        )
        self.serial_io.on_connect = self._on_serial_connect
        self.serial_io.on_disconnect = self._on_serial_disconnect
        self.can_io = CANIO(
            on_data=self._on_serial_data,
            on_error=self._on_serial_error,
        )
        self.can_io.on_connect = self._on_can_connect
        self.can_io.on_disconnect = self._on_can_disconnect
        self.capture_mgr = CaptureManager()
        self.virtual_mcu: Optional[VirtualMCU] = None

        # Active I/O channel (serial or can) - tracks which has data callbacks
        self._active_io: str = "serial"

        # GUI state
        self._capturing = False
        self._simulator_active = False

        # Build UI
        self._build_menu()
        self._build_main_area()
        self._build_status_bar()

        # Bind close handler
        root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_menu(self) -> None:
        """Build the menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="清除日志", command=self._clear_log,
                              accelerator="Ctrl+L")
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self._on_close,
                              accelerator="Ctrl+Q")

        # View menu
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="视图", menu=view_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self._show_about)

        # Keyboard shortcuts
        self.root.bind("<Control-l>", lambda e: self._clear_log())
        self.root.bind("<Control-q>", lambda e: self._on_close())

    def _build_main_area(self) -> None:
        """Build the main notebook area with tabs."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        # Tab 1: Connection
        self.connection_panel = ConnectionPanel(
            self.notebook, self.serial_io, self.can_io,
            self.log_engine, self.parser
        )
        self.notebook.add(self.connection_panel, text=" 🔌 连接  ")

        # Tab 2: Protocol Log
        self.log_panel = LogPanel(
            self.notebook, self.log_engine
        )
        self.notebook.add(self.log_panel, text=" 📋 协议日志  ")

        # Tab 3: Hex View
        self.hex_panel = HexPanel(self.notebook, self.log_engine)
        self.notebook.add(self.hex_panel, text=" 🔬 Hex 视图  ")

        # Tab 4: Simulator
        self.simulator_panel = SimulatorPanel(
            self.notebook, self.log_engine, self.parser, self
        )
        self.notebook.add(self.simulator_panel, text=" 🖥️ 虚拟 MCU  ")

        # Tab 5: AI CLI
        self.ai_cli_panel = AICliPanel(self.notebook, self)
        self.notebook.add(self.ai_cli_panel, text=" ⌨️ CLI 终端  ")

        # Tab 6: Benchmark
        self.benchmark_panel = BenchmarkPanel(self.notebook, self)
        self.notebook.add(self.benchmark_panel, text="  📊 基准测试  ")

        # Connect log engine to log panel
        self.log_engine.on_event = self.log_panel.on_event

    def _build_status_bar(self) -> None:
        """Build the status bar at the bottom."""
        self.status_frame = ttk.Frame(self.root, relief=tk.SUNKEN)
        self.status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        self.status_label = ttk.Label(
            self.status_frame, text="✅ 就绪", padding=(5, 2)
        )
        self.status_label.pack(side=tk.LEFT)

        self.connection_status = ttk.Label(
            self.status_frame, text="⭕ 未连接", foreground="gray",
            padding=(5, 2)
        )
        self.connection_status.pack(side=tk.RIGHT)

        self.tx_count_label = ttk.Label(
            self.status_frame, text="📤 Tx:0", padding=(5, 2)
        )
        self.tx_count_label.pack(side=tk.RIGHT)

        self.rx_count_label = ttk.Label(
            self.status_frame, text="📥 Rx:0", padding=(5, 2)
        )
        self.rx_count_label.pack(side=tk.RIGHT)

        self.update_status_bar()

    def update_status_bar(self) -> None:
        """Update status bar information."""
        # Determine active IO and its state
        io = self.serial_io
        io_type = "串口"
        if self.connection_panel._active_mode.get() == "can":
            io = self.can_io
            io_type = "CAN"

        state = io.state
        if state.value == "connected":
            port_info = ""
            if self.connection_panel._active_mode.get() == "can":
                port_info = f"{io._can_interface}/{io._can_channel}"
            else:
                port_info = getattr(io, '_port', '')
                if io.is_tcp:
                    io_type = "TCP"
            self.connection_status.config(
                text=f"🟢 {io_type}: {port_info}",
                foreground="green"
            )
        elif state.value == "connecting":
            self.connection_status.config(text="🟡 连接中...", foreground="orange")
        elif state.value == "error":
            self.connection_status.config(text="🔴 错误", foreground="red")
        else:
            self.connection_status.config(text="⭕ 未连接", foreground="gray")

        # Message counts
        stats = io.get_stats()
        self.tx_count_label.config(text=f"📤 Tx:{stats['packets_sent']}")
        self.rx_count_label.config(text=f"📥 Rx:{stats['packets_received']}")

        # Schedule next update
        self.root.after(1000, self.update_status_bar)

    # ─── Serial callbacks ────────────────────────────────────────────

    def _on_serial_data(self, data: bytes) -> None:
        """Callback when serial data is received."""
        # Parse and log
        try:
            block = MessageBlock.decode(data)
            parsed = self.parser.parse_block(block, direction="Rx")
            self.log_engine.log_message(parsed, "Rx")
        except ValueError as e:
            self.log_engine.log_raw(data, "Rx", error=str(e))

    def _on_serial_error(self, error: Exception) -> None:
        """Callback on serial error."""
        self.log_engine.log_raw(
            b"", "Rx", msg_name="#error", error=str(error)
        )
        self.root.after(0, lambda: self.status_label.config(
            text=f"错误: {error}"
        ))

    def _on_serial_connect(self) -> None:
        """Callback on serial connection."""
        self.root.after(0, lambda: self.status_label.config(
            text=f"已连接到 {self.serial_io._port}"
        ))

    def _on_serial_disconnect(self) -> None:
        """Callback on serial disconnect."""
        self.root.after(0, lambda: self.status_label.config(
            text="🔌 串口已断开连接"
        ))

    def _on_can_connect(self) -> None:
        """Callback on CAN connection."""
        self.root.after(0, lambda: self.status_label.config(
            text=f"📡 CAN 已连接到 {self.can_io._can_interface}/{self.can_io._can_channel}"
        ))

    def _on_can_disconnect(self) -> None:
        """Callback on CAN disconnect."""
        self.root.after(0, lambda: self.status_label.config(
            text="📡 CAN 已断开连接"
        ))

    # ─── Actions ─────────────────────────────────────────────────────

    def _clear_log(self) -> None:
        """Clear all buffered log events."""
        self.log_engine.clear()
        self.log_panel.refresh()
        self.status_label.config(text="日志已清除")

    def _show_about(self) -> None:
        """Show about dialog."""
        messagebox.showinfo(
            __app_name__,
            f"{__app_name__} v{__version__}\n\n"
            "Kalico 固件协议调试上位机工具\n\n"
            "功能:\n"
            "  • 串口连接与通信\n"
            "  • 协议消息解析与日志\n"
            "  • Hex 原始数据查看\n"
            "  • 虚拟 MCU 模拟\n"
            "  • AI CLI 接口\n\n"
            "许可证: GPLv3"
        )

    def _on_close(self) -> None:
        """Handle window close event."""
        if self.serial_io.is_connected():
            self.serial_io.disconnect()
        if self.can_io.is_connected():
            self.can_io.disconnect()
        self.capture_mgr.stop()
        self.log_engine.stop_file_logging()
        self.root.destroy()

    def send_raw(self, data: bytes) -> bool:
        """Send raw bytes via active I/O channel (public API for CLI panel)."""
        mode = self.connection_panel._active_mode.get() if hasattr(
            self, 'connection_panel') else "serial"
        io = self.can_io if mode == "can" else self.serial_io
        if io.is_connected():
            self.log_engine.log_raw(data, "Tx")
            return io.send(data)
        return False

    def send_message(self, msg_name: str, seq: int = 0,
                     **params) -> bool:
        """Send a named message via active I/O channel (public API)."""
        encoded = self.parser.encode_message(msg_name, seq=seq, **params)
        if encoded:
            return self.send_raw(encoded)
        return False
