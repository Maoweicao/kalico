# Connection configuration panel
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Connection Panel
================

GUI panel for connection management (Serial + CAN) and common commands:
  - Serial: port selection, baud rate, connect/disconnect
  - CAN bus: interface type, channel, bitrate, UUID/nodeid, discover/connect
  - Data capture controls
  - Common MCU command test buttons (grouped by category)
"""

import json
import logging
import os
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from ...log.logger import LogEngine
from ...protocol.parser import Parser
from ...io.serial_io import SerialIO, ConnectionState
from ...io.can_io import CANIO
from ...io.capture import CaptureManager
from ..common_commands import COMMON_COMMANDS, get_categories, get_commands_by_category


class ConnectionPanel(ttk.Frame):
    """Panel for managing connections (Serial or CAN) to MCU devices."""

    def __init__(self, parent, serial_io: SerialIO,
                 can_io: CANIO, log_engine: LogEngine, parser: Parser):
        super().__init__(parent)
        self.serial_io = serial_io
        self.can_io = can_io
        self.log_engine = log_engine
        self.parser = parser
        self.capture_mgr = CaptureManager()
        self._capturing = False

        # Currently active I/O: 'serial' or 'can'
        self._active_mode = tk.StringVar(value="serial")

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the connection panel UI."""
        # Use PanedWindow for left (settings) / right (commands) split
        paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # ─── LEFT: Settings ──────────────────────────────────────────
        left = ttk.Frame(paned, padding=5)
        paned.add(left, weight=1)

        # Mode selector
        mode_frame = ttk.LabelFrame(left, text="🔗 连接模式", padding=5)
        mode_frame.pack(fill=tk.X, pady=(0, 5))
        mode_row = ttk.Frame(mode_frame)
        mode_row.pack(fill=tk.X, pady=2)
        for mode, text in [("serial", "🔌 串口 (UART)"), ("tcp", "🌐 TCP 桥接"),
                           ("can", "📡 CAN 总线")]:
            ttk.Radiobutton(mode_row, text=text, variable=self._active_mode,
                            value=mode, command=self._on_mode_change).pack(
                side=tk.LEFT, padx=5)

        # ── Serial Settings ──────────────────────────────────────────
        self.serial_frame = ttk.LabelFrame(left, text="串口设置", padding=8)
        self.serial_frame.pack(fill=tk.X, pady=2)

        port_row = ttk.Frame(self.serial_frame)
        port_row.pack(fill=tk.X, pady=3)
        ttk.Label(port_row, text="端口:").pack(side=tk.LEFT)
        self.port_var = tk.StringVar()
        self.port_combo = ttk.Combobox(
            port_row, textvariable=self.port_var, width=28, state="readonly")
        self.port_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(port_row, text="刷新", width=4,
                   command=self._refresh_ports).pack(side=tk.LEFT)
        ttk.Button(port_row, text="🔍 自动探测", width=8,
                   command=self._auto_detect).pack(side=tk.LEFT, padx=3)

        # Probe status (hidden until auto-detect is running)
        self.probe_status_var = tk.StringVar()
        self.probe_label = ttk.Label(self.serial_frame,
                                     textvariable=self.probe_status_var,
                                     foreground="#888", font=("", 8))
        self.probe_label.pack(fill=tk.X, pady=1)

        baud_row = ttk.Frame(self.serial_frame)
        baud_row.pack(fill=tk.X, pady=3)
        ttk.Label(baud_row, text="波特率:").pack(side=tk.LEFT)
        self.baud_var = tk.StringVar(value="250000")
        ttk.Combobox(baud_row, textvariable=self.baud_var,
                     values=["9600","19200","38400","57600","115200",
                             "230400","250000","500000"],
                     width=12, state="readonly").pack(side=tk.LEFT, padx=5)

        # ── TCP Settings (virtual serial bridge, e.g. mcu_sim) ──────
        self.tcp_frame = ttk.LabelFrame(left, text="🌐 TCP 桥接设置", padding=8)
        self.tcp_frame.pack(fill=tk.X, pady=2)
        self.tcp_frame.pack_forget()  # hidden initially

        tcp_row = ttk.Frame(self.tcp_frame)
        tcp_row.pack(fill=tk.X, pady=3)
        ttk.Label(tcp_row, text="地址:").pack(side=tk.LEFT)
        self.tcp_host_var = tk.StringVar(value="127.0.0.1")
        ttk.Entry(tcp_row, textvariable=self.tcp_host_var,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(tcp_row, text=":").pack(side=tk.LEFT)
        self.tcp_port_var = tk.StringVar(value="58183")
        ttk.Spinbox(tcp_row, from_=1, to=65535, width=6,
                    textvariable=self.tcp_port_var).pack(side=tk.LEFT, padx=3)

        # Port preset buttons for common mcu_sim ports
        preset_tcp_row = ttk.Frame(self.tcp_frame)
        preset_tcp_row.pack(fill=tk.X, pady=2)
        ttk.Label(preset_tcp_row, text="快速端口:", font=("", 8)).pack(side=tk.LEFT)
        for preset_name, preset_port in [("mcu_sim", "58183"), ("SimulAVR", "1234"),
                                         ("Custom", "25000")]:
            ttk.Button(preset_tcp_row, text=preset_name, width=8,
                       command=lambda p=preset_port: self.tcp_port_var.set(p)
                       ).pack(side=tk.LEFT, padx=2)

        # ── CAN Settings ─────────────────────────────────────────────
        self.can_frame = ttk.LabelFrame(left, text="📡 CAN 设置", padding=8)
        self.can_frame.pack(fill=tk.X, pady=2)
        self.can_frame.pack_forget()  # hidden initially

        # Interface type
        iface_row = ttk.Frame(self.can_frame)
        iface_row.pack(fill=tk.X, pady=3)
        ttk.Label(iface_row, text="接口类型:").pack(side=tk.LEFT)
        self.can_iface_var = tk.StringVar(value="slcan")
        self.can_iface_combo = ttk.Combobox(
            iface_row, textvariable=self.can_iface_var,
            values=CANIO.list_interfaces(), width=12, state="readonly")
        self.can_iface_combo.pack(side=tk.LEFT, padx=5)

        # Channel
        chan_row = ttk.Frame(self.can_frame)
        chan_row.pack(fill=tk.X, pady=3)
        ttk.Label(chan_row, text="通道:").pack(side=tk.LEFT)
        self.can_chan_var = tk.StringVar(value="COM5")
        self.can_chan_combo = ttk.Combobox(
            chan_row, textvariable=self.can_chan_var, width=22)
        self.can_chan_combo.pack(side=tk.LEFT, padx=5)
        ttk.Button(chan_row, text="扫描串口", width=8,
                   command=self._refresh_can_ports).pack(side=tk.LEFT, padx=2)

        # Bitrate
        bit_row = ttk.Frame(self.can_frame)
        bit_row.pack(fill=tk.X, pady=3)
        ttk.Label(bit_row, text="比特率:").pack(side=tk.LEFT)
        self.can_bit_var = tk.StringVar(value="500000")
        ttk.Combobox(bit_row, textvariable=self.can_bit_var,
                     values=["125000","250000","500000","1000000"],
                     width=10, state="readonly").pack(side=tk.LEFT, padx=5)

        # UUID / NodeID
        uuid_row = ttk.Frame(self.can_frame)
        uuid_row.pack(fill=tk.X, pady=3)
        ttk.Label(uuid_row, text="MCU UUID:").pack(side=tk.LEFT)
        self.can_uuid_var = tk.StringVar()
        ttk.Entry(uuid_row, textvariable=self.can_uuid_var,
                  width=18).pack(side=tk.LEFT, padx=5)
        ttk.Label(uuid_row, text="NodeID:").pack(side=tk.LEFT)
        self.can_nodeid_var = tk.StringVar(value="64")
        ttk.Spinbox(uuid_row, from_=0, to=127,
                    textvariable=self.can_nodeid_var,
                    width=5).pack(side=tk.LEFT, padx=3)

        # CAN action buttons
        can_btn_row = ttk.Frame(self.can_frame)
        can_btn_row.pack(fill=tk.X, pady=5)
        ttk.Button(can_btn_row, text="🔍 发现设备",
                   command=self._can_discover).pack(side=tk.LEFT, padx=3)
        ttk.Button(can_btn_row, text="📌 分配 NodeID",
                   command=self._can_assign).pack(side=tk.LEFT, padx=3)

        # ── Connect/Disconnect ───────────────────────────────────────
        ctrl_frame = ttk.LabelFrame(left, text="连接控制", padding=8)
        ctrl_frame.pack(fill=tk.X, pady=5)

        self.connect_btn = ttk.Button(
            ctrl_frame, text="🚀 连接", command=self._toggle_connection)
        self.connect_btn.pack(pady=5)

        self.status_indicator = ttk.Label(
            ctrl_frame, text="● 未连接", foreground="gray", font=("", 10))
        self.status_indicator.pack()

        # ── Capture ──────────────────────────────────────────────────
        cap_frame = ttk.LabelFrame(left, text="数据捕获", padding=8)
        cap_frame.pack(fill=tk.X, pady=5)

        cap_row = ttk.Frame(cap_frame)
        cap_row.pack(fill=tk.X, pady=2)
        self.capture_btn = ttk.Button(
            cap_row, text="⏺ 开始捕获", command=self._toggle_capture,
            state="disabled")
        self.capture_btn.pack(side=tk.LEFT)
        self.capture_status = ttk.Label(cap_row, text="未捕获", foreground="gray")
        self.capture_status.pack(side=tk.LEFT, padx=8)

        # ── Info ──────────────────────────────────────────────────────
        info_frame = ttk.LabelFrame(left, text="连接信息", padding=5)
        info_frame.pack(fill=tk.BOTH, expand=True, pady=2)

        self.info_text = tk.Text(info_frame, height=6,
                                 font=("Consolas", 9), state="disabled")
        self.info_text.pack(fill=tk.BOTH, expand=True)
        ttk.Scrollbar(self.info_text, orient="vertical",
                      command=self.info_text.yview).pack(
            side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=lambda *a: None)

        # ─── RIGHT: Common Commands ──────────────────────────────────
        right = ttk.Frame(paned, padding=5)
        paned.add(right, weight=2)

        cmd_outer = ttk.LabelFrame(right, text="📋 常见指令测试", padding=5)
        cmd_outer.pack(fill=tk.BOTH, expand=True)

        # Scrollable canvas for command buttons
        cmd_canvas = tk.Canvas(cmd_outer, highlightthickness=0)
        cmd_scroll = ttk.Scrollbar(cmd_outer, orient="vertical",
                                   command=cmd_canvas.yview)
        cmd_scroll_frame = ttk.Frame(cmd_canvas)

        cmd_scroll_frame.bind("<Configure>",
                              lambda e: cmd_canvas.configure(
                                  scrollregion=cmd_canvas.bbox("all")))
        cmd_canvas.create_window((0, 0), window=cmd_scroll_frame, anchor="nw")
        cmd_canvas.configure(yscrollcommand=cmd_scroll.set)

        cmd_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        cmd_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # Mouse wheel scrolling
        def _on_mousewheel(event):
            cmd_canvas.yview_scroll(-1 * (event.delta // 120), "units")
        cmd_canvas.bind("<Enter>", lambda e: cmd_canvas.bind_all(
            "<MouseWheel>", _on_mousewheel))
        cmd_canvas.bind("<Leave>", lambda e: cmd_canvas.unbind_all(
            "<MouseWheel>"))

        # Build command buttons grouped by category
        self._build_command_buttons(cmd_scroll_frame)

        # Initial port scan
        self._refresh_ports()

    def _build_command_buttons(self, parent: ttk.Frame) -> None:
        """Build common command buttons grouped by category."""
        for cat in get_categories():
            cmds = get_commands_by_category(cat)
            if not cmds:
                continue
            # Category label
            sep = ttk.Separator(parent, orient="horizontal")
            sep.pack(fill=tk.X, pady=(8, 2))
            lbl = ttk.Label(parent, text=f"▸ {cat}",
                            font=("", 9, "bold"), foreground="#555")
            lbl.pack(anchor=tk.W, padx=2)

            # Button row (3 per row)
            btn_frame = ttk.Frame(parent)
            btn_frame.pack(fill=tk.X, pady=2)
            for i, cmd in enumerate(cmds):
                btn = ttk.Button(
                    btn_frame, text=cmd["label"],
                    command=lambda c=cmd: self._send_common_command(c),
                    width=28)
                btn.pack(side=tk.LEFT, padx=2, pady=1)
                if i % 2 == 1:  # wrap every 2 buttons
                    btn_frame = ttk.Frame(parent)
                    btn_frame.pack(fill=tk.X, pady=2)

    def _on_mode_change(self) -> None:
        """Handle Serial/TCP/CAN mode toggle."""
        mode = self._active_mode.get()
        self.serial_frame.pack_forget()
        self.tcp_frame.pack_forget()
        self.can_frame.pack_forget()
        if mode == "can":
            self.can_frame.pack(fill=tk.X, pady=2, before=self.info_text)
        elif mode == "tcp":
            self.tcp_frame.pack(fill=tk.X, pady=2, before=self.info_text)
        else:
            self.serial_frame.pack(fill=tk.X, pady=2, before=self.info_text)

    # ─── Port scanning ───────────────────────────────────────────────

    def _refresh_ports(self) -> None:
        """Scan for available serial ports."""
        ports = SerialIO.list_ports()
        if ports:
            self.port_combo["values"] = ports
            self.port_var.set(ports[0])
        else:
            self.port_combo["values"] = ["(无可用串口)"]
            self.port_var.set("(无可用串口)")

    def _refresh_can_ports(self) -> None:
        """Scan for slcan-compatible serial ports."""
        ports = CANIO.list_slcan_ports()
        if ports:
            self.can_chan_combo["values"] = ports
            self.can_chan_var.set(ports[0])
        else:
            self.can_chan_combo["values"] = ["(无)"]
            self.can_chan_var.set("(无)")

    # ─── Auto-detect ────────────────────────────────────────────────

    def _auto_detect(self) -> None:
        """Auto-detect Kalico MCU by scanning all serial ports."""
        if self.serial_io.is_connected():
            messagebox.showinfo("提示", "请先断开当前连接")
            return

        self._append_info("开始自动探测 MCU 设备...\n")
        self.probe_status_var.set("正在扫描...")

        def progress_cb(msg: str) -> None:
            self.after(0, lambda: self.probe_status_var.set(msg))
            self.after(0, lambda: self._append_info(msg + "\n"))

        def detect_thread() -> None:
            result = self.serial_io.auto_detect(
                on_progress=progress_cb,
                timeout_per_port=0.6,
            )
            if result is not None:
                port, baudrate = result
                self.after(0, lambda: self.port_var.set(port))
                self.after(0, lambda: self.baud_var.set(str(baudrate)))
                self.after(0, lambda: self.probe_status_var.set(
                    f"✓ 已发现: {port} @ {baudrate}"))
                self.after(0, lambda: self._append_info(
                    f"✓ 设备发现完成: {port} @ {baudrate}\n"))
                # Auto-connect after short delay
                self.after(500, self._connect_serial)
            else:
                self.after(0, lambda: self.probe_status_var.set(
                    "未发现 Kalico 设备"))
                self.after(0, lambda: self._append_info(
                    "✗ 未发现 Kalico MCU 设备\n"))

        threading.Thread(target=detect_thread, daemon=True).start()

    # ─── Connection logic ────────────────────────────────────────────

    def _toggle_connection(self) -> None:
        """Connect or disconnect based on active mode."""
        mode = self._active_mode.get()
        if mode == "serial":
            if self.serial_io.is_connected():
                self._disconnect_serial()
            else:
                self._connect_serial()
        elif mode == "tcp":
            if self.serial_io.is_connected():
                self._disconnect_serial()
            else:
                self._connect_tcp()
        else:
            if self.can_io.is_connected():
                self._disconnect_can()
            else:
                self._connect_can()

    def _connect_serial(self) -> None:
        port_desc = self.port_var.get()
        if not port_desc or port_desc == "(无可用串口)":
            messagebox.showwarning("连接失败", "请先选择有效的串口端口")
            return
        port = SerialIO.get_port_name(port_desc)
        try:
            baudrate = int(self.baud_var.get())
        except ValueError:
            baudrate = 250000
        self._append_info(f"🔌 连接串口 {port} @ {baudrate}...\n")
        def thread():
            ok = self.serial_io.connect(port, baudrate)
            self.after(0, self._on_connected if ok else self._on_failed)
        threading.Thread(target=thread, daemon=True).start()

    def _connect_tcp(self) -> None:
        """Connect via TCP virtual serial bridge (e.g. mcu_sim)."""
        host = self.tcp_host_var.get().strip()
        port_str = self.tcp_port_var.get().strip()
        if not host or not port_str:
            messagebox.showwarning("连接失败", "请输入 TCP 地址和端口")
            return
        tcp_addr = f"tcp:{host}:{port_str}"
        self._append_info(f"🌐 连接 TCP 桥接 {host}:{port_str}...\n")
        def thread():
            ok = self.serial_io.connect(tcp_addr, timeout=3.0)
            self.after(0, self._on_connected if ok else self._on_failed)
        threading.Thread(target=thread, daemon=True).start()

    def _disconnect_serial(self) -> None:
        self.serial_io.disconnect()
        self._on_disconnected()

    def _connect_can(self) -> None:
        iface = self.can_iface_var.get()
        channel = self.can_chan_var.get()
        try:
            bitrate = int(self.can_bit_var.get())
        except ValueError:
            bitrate = 500000
        self._append_info(f"连接 CAN {iface}/{channel} @ {bitrate}...\n")
        def thread():
            ok = False
            if iface == "slcan":
                ok = self.can_io.connect_slcan(channel, bitrate)
            elif iface == "pcan":
                ok = self.can_io.connect_pcan(channel, bitrate)
            else:
                ok = self.can_io.connect_virtual(channel, bitrate)
            self.after(0, self._on_connected if ok else self._on_failed)
        threading.Thread(target=thread, daemon=True).start()

    def _disconnect_can(self) -> None:
        self.can_io.disconnect()
        self._on_disconnected()

    # ─── CAN discovery & assignment ──────────────────────────────────

    def _can_discover(self) -> None:
        """Discover MCU nodes on the CAN bus."""
        uuid_str = self.can_uuid_var.get().strip() or None
        self._append_info(f"发现 CAN 节点 (uuid={uuid_str or 'any'})...\n")
        def thread():
            nodeid = self.can_io.discover_mcu(uuid=uuid_str, timeout=3.0)
            self.after(0, lambda: self._append_info(
                f"发现结果: nodeid={nodeid}\n" if nodeid is not None
                else "未发现设备\n"))

            if nodeid is not None and nodeid > 0:
                self.after(0, lambda: self.can_nodeid_var.set(str(nodeid)))
        threading.Thread(target=thread, daemon=True).start()

    def _can_assign(self) -> None:
        """Assign nodeid to an MCU."""
        uuid_str = self.can_uuid_var.get().strip()
        try:
            nodeid = int(self.can_nodeid_var.get())
        except ValueError:
            nodeid = 64
        if not uuid_str:
            messagebox.showwarning("分配失败", "请输入 MCU UUID")
            return
        self._append_info(f"分配 nodeid={nodeid} 给 uuid={uuid_str}\n")
        def thread():
            ok = self.can_io.assign_nodeid(uuid_str, nodeid)
            self.after(0, lambda: self._append_info(
                "NodeID 分配成功\n" if ok else "分配失败\n"))
            if ok:
                self.after(500, lambda: self._connect_can_nodeid())
        threading.Thread(target=thread, daemon=True).start()

    def _connect_can_nodeid(self) -> None:
        """Connect to CAN node after assignment."""
        try:
            nodeid = int(self.can_nodeid_var.get())
        except ValueError:
            return
        self.can_io.connect_node(nodeid)
        self._append_info(f"CAN 过滤器已设置: nodeid={nodeid}\n")

    # ─── Connection state handlers ───────────────────────────────────

    def _on_connected(self) -> None:
        mode = self._active_mode.get()
        io = self.serial_io if mode == "serial" else self.can_io
        port_str = io._port if mode == "serial" else f"{io._can_interface}/{io._can_channel}"
        self.connect_btn.config(text="🔌 断开连接")
        self.status_indicator.config(text=f"● 已连接 {port_str}", foreground="green")
        self.capture_btn.config(state="normal")
        self._append_info("✓ 连接成功\n")

    def _on_failed(self) -> None:
        self.status_indicator.config(text="● 连接失败", foreground="red")
        self._append_info("✗ 连接失败\n")

    def _on_disconnected(self) -> None:
        self.connect_btn.config(text="🚀 连接")
        self.status_indicator.config(text="● 未连接", foreground="gray")
        self.capture_btn.config(state="disabled", text="⏺ 开始捕获")
        self._capturing = False
        self._append_info("已断开连接\n")

    # ─── Common command sending ──────────────────────────────────────

    def _send_common_command(self, cmd: dict) -> None:
        """Send a common command via active I/O channel."""
        mode = self._active_mode.get()
        io = self.serial_io if mode == "serial" else self.can_io
        if not io.is_connected():
            messagebox.showwarning("未连接", "请先连接到设备")
            return

        name = cmd["name"]
        params = cmd["default_params"].copy()
        encoded = self.parser.encode_message(name, **params)
        if encoded is None:
            self._append_info(f"✗ 未知命令: {name} (需先获取 dictionary)\n")
            return

        # Log Tx
        try:
            from ...protocol.codec import MessageBlock
            block = MessageBlock.decode(encoded)
            parsed = self.parser.parse_block(block, direction="Tx")
            self.log_engine.log_message(parsed, "Tx")
        except Exception as e:
            self.log_engine.log_raw(encoded, "Tx", error=str(e))

        io.send(encoded)
        self._append_info(f"→ {name} {cmd['hint']}\n")

    # ─── Capture ─────────────────────────────────────────────────────

    def _toggle_capture(self) -> None:
        if self._capturing:
            self._stop_capture()
        else:
            self._start_capture()

    def _start_capture(self) -> None:
        path = self.capture_mgr.start()
        self._capturing = True
        self.capture_btn.config(text="⏹ 停止捕获")
        self.capture_status.config(text=f"捕获中...", foreground="green")
        self._append_info(f"捕获开始: {path}\n")

    def _stop_capture(self) -> None:
        path = self.capture_mgr.stop()
        self._capturing = False
        self.capture_btn.config(text="⏺ 开始捕获")
        self.capture_status.config(text="已停止", foreground="blue")
        if path:
            self._append_info(f"捕获已保存: {path}\n")

    def _append_info(self, text: str) -> None:
        self.info_text.config(state="normal")
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state="disabled")
        """Start capturing serial data to a file."""
        capture_dir = self.capture_path_var.get() or "captures"
        path = self.capture_mgr.start()
        self._capturing = True
        self.capture_btn.config(text="停止捕获")
        self.capture_status.config(
            text=f"捕获中 → {os.path.basename(path)}", foreground="green"
        )
        self._append_info(f"开始捕获: {path}\n")

    def _stop_capture(self) -> None:
        """Stop capturing serial data."""
        path = self.capture_mgr.stop()
        self._capturing = False
        self.capture_btn.config(text="开始捕获")
        self.capture_status.config(
            text=f"已保存: {os.path.basename(path) if path else '无'}",
            foreground="blue"
        )
        if path:
            self._append_info(f"捕获已保存: {path}\n")

    def _append_info(self, text: str) -> None:
        """Append text to the info display."""
        self.info_text.config(state="normal")
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state="disabled")
