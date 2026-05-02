# Virtual MCU simulator control panel
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Simulator Panel
===============

GUI panel for controlling the virtual MCU simulator:
  - Start/Stop/Reset the virtual MCU
  - Load data dictionary from file
  - Register custom command/response handlers
  - View virtual MCU state and statistics
  - Feed manual commands and see responses
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Any, Dict, Optional

from ...log.logger import LogEngine
from ...protocol.codec import MessageBlock
from ...protocol.dictionary import MessageDictionary
from ...protocol.parser import Parser, ParsedMessage
from ...simulator.virtual_mcu import VirtualMCU
from ..common_commands import COMMON_COMMANDS, get_categories, get_commands_by_category


class SimulatorPanel(ttk.Frame):
    """Panel for virtual MCU simulator control."""

    def __init__(self, parent, log_engine: LogEngine, parser: Parser,
                 app=None):
        super().__init__(parent)
        self.log_engine = log_engine
        self.parser = parser
        self.app = app
        self.virtual_mcu: Optional[VirtualMCU] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the simulator panel UI."""
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ─── Control Frame ───────────────────────────────────────────
        ctrl_frame = ttk.LabelFrame(main, text="模拟器控制", padding=10)
        ctrl_frame.pack(fill=tk.X, pady=(0, 10))

        btn_row = ttk.Frame(ctrl_frame)
        btn_row.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(
            btn_row, text="启动虚拟 MCU", command=self._start_simulator
        )
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(
            btn_row, text="停止", command=self._stop_simulator,
            state="disabled"
        )
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.reset_btn = ttk.Button(
            btn_row, text="重置", command=self._reset_simulator,
            state="disabled"
        )
        self.reset_btn.pack(side=tk.LEFT, padx=5)

        ttk.Button(
            btn_row, text="加载 Dictionary...",
            command=self._load_dictionary
        ).pack(side=tk.RIGHT, padx=5)

        # Status indicator
        self.sim_status = ttk.Label(
            ctrl_frame, text="● 未启动", foreground="gray", font=("", 10)
        )
        self.sim_status.pack(pady=5)

        # ─── Manual Command Frame ────────────────────────────────────
        cmd_frame = ttk.LabelFrame(main, text="手动发送命令", padding=10)
        cmd_frame.pack(fill=tk.X, pady=(0, 10))

        cmd_row = ttk.Frame(cmd_frame)
        cmd_row.pack(fill=tk.X, pady=5)

        ttk.Label(cmd_row, text="命令名称:").pack(side=tk.LEFT)
        self.cmd_name_var = tk.StringVar()
        ttk.Entry(cmd_row, textvariable=self.cmd_name_var,
                  width=20).pack(side=tk.LEFT, padx=5)

        ttk.Label(cmd_row, text="参数 (JSON):").pack(side=tk.LEFT)
        self.cmd_params_var = tk.StringVar(value='{"offset": 0, "count": 40}')
        ttk.Entry(cmd_row, textvariable=self.cmd_params_var,
                  width=30).pack(side=tk.LEFT, padx=5)

        ttk.Button(cmd_row, text="发送", width=6,
                   command=self._send_command).pack(side=tk.LEFT, padx=5)

        # Raw hex send
        hex_row = ttk.Frame(cmd_frame)
        hex_row.pack(fill=tk.X, pady=5)
        ttk.Label(hex_row, text="原始 Hex:").pack(side=tk.LEFT)
        self.raw_hex_var = tk.StringVar()
        ttk.Entry(hex_row, textvariable=self.raw_hex_var,
                  width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(hex_row, text="发送 HEX", width=8,
                   command=self._send_raw_hex).pack(side=tk.LEFT, padx=5)

        # ─── Common Command Presets ──────────────────────────────────
        preset_frame = ttk.LabelFrame(main, text="📋 常见指令预设", padding=8)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        # Tab-style: row of category buttons
        self._current_cat = tk.StringVar(value="发现与状态")
        cat_frame = ttk.Frame(preset_frame)
        cat_frame.pack(fill=tk.X, pady=2)
        for cat in self._get_categories():
            btn = ttk.Button(cat_frame, text=cat, width=12,
                             command=lambda c=cat: self._show_preset_category(c))
            btn.pack(side=tk.LEFT, padx=2)

        # Container for preset command buttons
        self._preset_container = ttk.Frame(preset_frame)
        self._preset_container.pack(fill=tk.X, pady=5)
        self._show_preset_category("发现与状态")

        # ─── Registered commands ─────────────────────────────────────
        reg_frame = ttk.LabelFrame(main, text="注册命令处理器", padding=10)
        reg_frame.pack(fill=tk.X, pady=(0, 10))

        reg_row = ttk.Frame(reg_frame)
        reg_row.pack(fill=tk.X, pady=5)
        ttk.Label(reg_row, text="命令名:").pack(side=tk.LEFT)
        self.reg_name_var = tk.StringVar()
        ttk.Entry(reg_row, textvariable=self.reg_name_var,
                  width=15).pack(side=tk.LEFT, padx=5)
        ttk.Label(reg_row, text="响应 Hex:").pack(side=tk.LEFT)
        self.reg_hex_var = tk.StringVar()
        ttk.Entry(reg_row, textvariable=self.reg_hex_var,
                  width=30).pack(side=tk.LEFT, padx=5)
        ttk.Button(reg_row, text="注册", width=6,
                   command=self._register_handler).pack(side=tk.LEFT, padx=5)

        # ─── Info ────────────────────────────────────────────────────
        info_frame = ttk.LabelFrame(main, text="模拟器状态", padding=10)
        info_frame.pack(fill=tk.BOTH, expand=True)

        self.info_text = tk.Text(
            info_frame, font=("Consolas", 9), wrap=tk.WORD,
            state="disabled", height=8
        )
        self.info_text.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.info_text, orient="vertical",
                                  command=self.info_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.info_text.config(yscrollcommand=scrollbar.set)

        # Periodic info update
        self._update_info()

    def _start_simulator(self) -> None:
        """Start the virtual MCU simulator."""
        self.virtual_mcu = VirtualMCU("simulator-mcu")
        self.virtual_mcu.on_response = self._on_mcu_response
        self.virtual_mcu.start()
        # Share the instance with the main window so other panels can access it
        self.app.virtual_mcu = self.virtual_mcu

        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.reset_btn.config(state="normal")
        self.sim_status.config(
            text="● 运行中", foreground="green"
        )
        self._append_info("虚拟 MCU 已启动\n")

    def _stop_simulator(self) -> None:
        """Stop the virtual MCU simulator."""
        if self.virtual_mcu:
            self.virtual_mcu.stop()
            self.virtual_mcu = None
        self.app.virtual_mcu = None

        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.reset_btn.config(state="disabled")
        self.sim_status.config(text="● 已停止", foreground="gray")
        self._append_info("虚拟 MCU 已停止\n")

    def _reset_simulator(self) -> None:
        """Reset the virtual MCU simulator."""
        self._stop_simulator()
        self._start_simulator()
        self._append_info("虚拟 MCU 已重置\n")

    def _load_dictionary(self) -> None:
        """Load a data dictionary from a JSON file."""
        path = filedialog.askopenfilename(
            title="加载 Data Dictionary",
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ]
        )
        if not path:
            return
        try:
            dictionary = MessageDictionary.load_from_file(path)
            self.parser.dictionary = dictionary
            self._append_info(f"已加载 Dictionary: {path}\n"
                              f"  版本: {dictionary.version}\n"
                              f"  消息数: {len(dictionary.messages)}\n")
        except Exception as e:
            messagebox.showerror("加载失败", str(e))

    def _send_command(self) -> None:
        """Send a named command to the virtual MCU."""
        if not self.virtual_mcu:
            messagebox.showwarning("提示", "请先启动虚拟 MCU")
            return

        cmd_name = self.cmd_name_var.get().strip()
        if not cmd_name:
            return

        try:
            params_str = self.cmd_params_var.get().strip()
            params = {}
            if params_str:
                import json
                params = json.loads(params_str)
        except json.JSONDecodeError as e:
            messagebox.showerror("参数格式错误", f"JSON 解析失败: {e}")
            return

        # Encode and feed to virtual MCU
        encoded = self.parser.encode_message(cmd_name, seq=0, **params)
        if encoded is None:
            messagebox.showerror("编码失败",
                                 f"未知命令: {cmd_name}\n"
                                 f"请检查命令名称是否在 dictionary 中")
            return

        # Log as Tx
        try:
            block = MessageBlock.decode(encoded)
            parsed = self.parser.parse_block(block, direction="Tx")
            self.log_engine.log_message(parsed, "Tx")
        except Exception as e:
            self.log_engine.log_raw(encoded, "Tx", error=str(e))

        # Feed to virtual MCU
        self._append_info(f"→ 发送命令: {cmd_name}\n")
        self.virtual_mcu.feed_data(encoded)

    def _send_raw_hex(self) -> None:
        """Send raw hex bytes to the virtual MCU."""
        if not self.virtual_mcu:
            messagebox.showwarning("提示", "请先启动虚拟 MCU")
            return

        hex_str = self.raw_hex_var.get().strip()
        if not hex_str:
            return

        try:
            from ...protocol.codec import hex_to_bytes
            data = hex_to_bytes(hex_str)
            self._append_info(f"→ 发送 HEX: {data.hex()}\n")
            self.log_engine.log_raw(data, "Tx")
            self.virtual_mcu.feed_data(data)
        except ValueError as e:
            messagebox.showerror("无效 Hex", str(e))

    def _register_handler(self) -> None:
        """Register a custom command handler."""
        if not self.virtual_mcu:
            messagebox.showwarning("提示", "请先启动虚拟 MCU")
            return

        cmd_name = self.reg_name_var.get().strip()
        hex_str = self.reg_hex_var.get().strip()
        if not cmd_name or not hex_str:
            return

        try:
            from ...protocol.codec import hex_to_bytes
            data = hex_to_bytes(hex_str)
            self.virtual_mcu.register_response(cmd_name, data)
            self._append_info(f"已注册命令 '{cmd_name}' 的响应\n")
        except ValueError as e:
            messagebox.showerror("无效 Hex", str(e))

    def _get_categories(self) -> list:
        """Get command categories, excluding CAN-only."""
        return [c for c in get_categories() if c != "CAN 总线"]

    def _show_preset_category(self, category: str) -> None:
        """Show command preset buttons for a category."""
        for w in self._preset_container.winfo_children():
            w.destroy()
        cmds = [c for c in COMMON_COMMANDS if c["category"] == category]
        row_frame = ttk.Frame(self._preset_container)
        row_frame.pack(fill=tk.X)
        for i, cmd in enumerate(cmds):
            btn = ttk.Button(
                row_frame, text=cmd["label"],
                command=lambda c=cmd: self._send_preset_command(c),
                width=28)
            btn.pack(side=tk.LEFT, padx=2, pady=1)
            if i % 2 == 1:
                row_frame = ttk.Frame(self._preset_container)
                row_frame.pack(fill=tk.X)

    def _send_preset_command(self, cmd: dict) -> None:
        """Send a preset command to the virtual MCU."""
        if not self.virtual_mcu:
            messagebox.showwarning("提示", "请先启动虚拟 MCU")
            return
        name = cmd["name"]
        params = cmd["default_params"].copy()
        encoded = self.parser.encode_message(name, **params)
        if encoded is None:
            self._append_info(f"✗ 未知命令: {name}\n")
            return
        # Log Tx
        try:
            block = MessageBlock.decode(encoded)
            parsed = self.parser.parse_block(block, direction="Tx")
            self.log_engine.log_message(parsed, "Tx")
        except Exception as e:
            self.log_engine.log_raw(encoded, "Tx", error=str(e))
        self._append_info(f"→ {name} {cmd['hint']}\n")
        self.virtual_mcu.feed_data(encoded)

    def _on_mcu_response(self, response_bytes: bytes) -> None:
        """Callback when virtual MCU generates a response."""
        try:
            block = MessageBlock.decode(response_bytes)
            parsed = self.parser.parse_block(block, direction="Rx")
            self.log_engine.log_message(parsed, "Rx")
            self._append_info(
                f"← 响应: {parsed.msg_name} "
                f"params={parsed.params}\n"
            )
        except ValueError as e:
            self.log_engine.log_raw(response_bytes, "Rx", error=str(e))

    def _update_info(self) -> None:
        """Periodically update simulator state info."""
        if self.virtual_mcu:
            stats = self.virtual_mcu.get_stats()
            info = (
                f"状态: {stats['state']}\n"
                f"运行时间: {stats['uptime']}s\n"
                f"命令接收: {stats['commands_received']}\n"
                f"响应发送: {stats['responses_sent']}\n"
                f"虚拟时钟: {stats['virtual_clock']} "
                f"(@ {stats['clock_freq']/1000000:.0f} MHz)\n"
                f"注册命令: {', '.join(stats['registered_commands'])}\n"
            )
            self.info_text.config(state="normal")
            self.info_text.delete("1.0", tk.END)
            self.info_text.insert(tk.END, info)
            self.info_text.config(state="disabled")

        self.after(2000, self._update_info)

    def _append_info(self, text: str) -> None:
        """Append text to the info display."""
        self.info_text.config(state="normal")
        self.info_text.insert(tk.END, text)
        self.info_text.see(tk.END)
        self.info_text.config(state="disabled")
