# In-app CLI terminal panel
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
AI CLI Terminal Panel
=====================

Embedded CLI terminal within the GUI for direct command input.
Provides a terminal-like interface for:
  - Sending protocol commands
  - Controlling the debug tool
  - AI-assisted debugging via text commands

Supports command history (up/down arrow keys).
"""

import logging
import shlex
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from ..main_window import DebugToolWindow


class AICliPanel(ttk.Frame):
    """Embedded CLI terminal within the GUI."""

    PROMPT = "kalico> "

    def __init__(self, parent, app: "DebugToolWindow"):
        super().__init__(parent)
        self.app = app
        self._history: List[str] = []
        self._history_index = -1

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the CLI terminal panel."""
        main = ttk.Frame(self, padding=5)
        main.pack(fill=tk.BOTH, expand=True)

        # Terminal output area
        output_frame = ttk.LabelFrame(main, text="终端输出", padding=5)
        output_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        self.output_text = tk.Text(
            output_frame, font=("Consolas", 10), wrap=tk.WORD,
            state="disabled", bg="#1e1e1e", fg="#d4d4d4",
            insertbackground="white", height=20
        )
        self.output_text.pack(fill=tk.BOTH, expand=True)

        v_scroll = ttk.Scrollbar(self.output_text, orient="vertical",
                                 command=self.output_text.yview)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_text.config(yscrollcommand=v_scroll.set)

        # Input area
        input_frame = ttk.Frame(main)
        input_frame.pack(fill=tk.X)

        ttk.Label(input_frame, text=self.PROMPT,
                  font=("Consolas", 10)).pack(side=tk.LEFT)

        self.input_var = tk.StringVar()
        self.input_entry = ttk.Entry(
            input_frame, textvariable=self.input_var,
            font=("Consolas", 10)
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.input_entry.bind("<Return>", self._on_enter)
        self.input_entry.bind("<Up>", self._on_history_up)
        self.input_entry.bind("<Down>", self._on_history_down)
        self.input_entry.focus_set()

        ttk.Button(input_frame, text="发送", width=6,
                   command=self._execute_command).pack(side=tk.RIGHT)

        # Quick help buttons
        help_frame = ttk.Frame(main)
        help_frame.pack(fill=tk.X, pady=(5, 0))

        for label, cmd in [
            ("帮助", "help"),
            ("状态", "status"),
            ("消息列表", "messages"),
            ("清屏", "clear"),
        ]:
            ttk.Button(
                help_frame, text=label, width=10,
                command=lambda c=cmd: self._quick_command(c)
            ).pack(side=tk.LEFT, padx=2)

    def _on_enter(self, event) -> None:
        """Handle Enter key in input."""
        self._execute_command()

    def _execute_command(self) -> None:
        """Execute the current input as a command."""
        cmd = self.input_var.get().strip()
        if not cmd:
            return
        self._add_history(cmd)
        self.input_var.set("")
        self._process_command(cmd)

    def _quick_command(self, cmd: str) -> None:
        """Execute a quick-command button."""
        self.input_var.set(cmd)
        self._execute_command()

    def _add_history(self, cmd: str) -> None:
        """Add command to history."""
        self._history.append(cmd)
        self._history_index = len(self._history)

    def _on_history_up(self, event) -> None:
        """Navigate history backward."""
        if not self._history:
            return
        if self._history_index > 0:
            self._history_index -= 1
            self.input_var.set(self._history[self._history_index])

    def _on_history_down(self, event) -> None:
        """Navigate history forward."""
        if self._history_index < len(self._history) - 1:
            self._history_index += 1
            self.input_var.set(self._history[self._history_index])
        else:
            self._history_index = len(self._history)
            self.input_var.set("")

    def _print(self, text: str) -> None:
        """Print text to terminal output."""
        self.output_text.config(state="normal")
        self.output_text.insert(tk.END, text + "\n")
        self.output_text.see(tk.END)
        self.output_text.config(state="disabled")

    def _process_command(self, cmd_line: str) -> None:
        """Parse and execute a CLI command."""
        try:
            parts = shlex.split(cmd_line)
        except ValueError as e:
            self._print(f"错误: {e}")
            return

        if not parts:
            return

        command = parts[0].lower()
        args = parts[1:]

        # Show command
        self._print(f"{self.PROMPT}{cmd_line}")

        # Dispatch commands
        handler_name = f"cmd_{command}"
        handler = getattr(self, handler_name, None)
        if handler:
            try:
                handler(args)
            except Exception as e:
                self._print(f"命令执行错误: {e}")
                logging.exception(f"CLI command error: {command}")
        else:
            self._print(f"未知命令: {command}")
            self._print("输入 'help' 查看命令列表")

    # ─── Built-in Commands ───────────────────────────────────────────

    def cmd_help(self, args: List[str]) -> None:
        """显示帮助信息"""
        self._print("可用命令:")
        self._print("  help             - 显示此帮助")
        self._print("  clear            - 清屏")
        self._print("  status           - 显示连接状态和统计")
        self._print("  connect <port> [baud] - 连接串口")
        self._print("  disconnect       - 断开串口")
        self._print("  send <hex>       - 发送原始 HEX 数据")
        self._print("  send_cmd <name> [params_json] - 发送命名命令")
        self._print("  monitor          - 持续监控消息")
        self._print("  messages         - 显示最近消息")
        self._print("  dict             - 显示 data dictionary")
        self._print("  sim_start        - 启动虚拟 MCU")
        self._print("  sim_stop         - 停止虚拟 MCU")
        self._print("  sim_send <name> [params_json] - 向虚拟 MCU 发送命令")
        self._print("  capture <file>   - 开始捕获")
        self._print("  capture_stop     - 停止捕获")
        self._print("  stats            - 详细统计")
        self._print("  export <fmt>     - 导出日志 (csv/text/hex)")

    def cmd_clear(self, args: List[str]) -> None:
        """清屏"""
        self.output_text.config(state="normal")
        self.output_text.delete("1.0", tk.END)
        self.output_text.config(state="disabled")

    def cmd_status(self, args: List[str]) -> None:
        """显示状态"""
        stats = self.app.serial_io.get_stats()
        self._print(f"串口状态: {stats['state']}")
        self._print(f"端口: {stats['port'] or 'N/A'}")
        self._print(f"波特率: {stats['baudrate']}")
        self._print(f"已发送: {stats['packets_sent']} 包 "
                    f"({stats['bytes_sent']} 字节)")
        self._print(f"已接收: {stats['packets_received']} 包 "
                    f"({stats['bytes_received']} 字节)")
        if self.app.virtual_mcu:
            mcu_stats = self.app.virtual_mcu.get_stats()
            self._print(f"虚拟 MCU: {mcu_stats['state']}")
            self._print(f"  命令接收: {mcu_stats['commands_received']}")
            self._print(f"  响应发送: {mcu_stats['responses_sent']}")
        log_count = self.app.log_engine.event_count
        self._print(f"日志事件: {log_count}")

    def cmd_connect(self, args: List[str]) -> None:
        """连接串口"""
        if not args:
            self._print("用法: connect <port> [baudrate]")
            return
        port = args[0]
        baudrate = int(args[1]) if len(args) > 1 else 250000
        self._print(f"正在连接 {port} @ {baudrate}...")
        result = self.app.serial_io.connect(port, baudrate)
        if result:
            self._print("连接成功")
        else:
            self._print("连接失败")

    def cmd_disconnect(self, args: List[str]) -> None:
        """断开串口"""
        self.app.serial_io.disconnect()
        self._print("已断开连接")

    def cmd_send(self, args: List[str]) -> None:
        """发送 HEX 数据"""
        if not args:
            self._print("用法: send <hex_bytes>")
            return
        from ...protocol.codec import hex_to_bytes
        try:
            data = hex_to_bytes("".join(args))
            if self.app.send_raw(data):
                self._print(f"已发送 {len(data)} 字节")
            else:
                self._print("发送失败 - 未连接")
        except ValueError as e:
            self._print(f"无效 HEX: {e}")

    def cmd_send_cmd(self, args: List[str]) -> None:
        """发送命名命令"""
        if not args:
            self._print("用法: send_cmd <name> [json_params]")
            return
        name = args[0]
        params = {}
        if len(args) > 1:
            import json
            params = json.loads(args[1])
        if self.app.send_message(name, **params):
            self._print(f"已发送命令: {name}")
        else:
            self._print(f"发送失败 - 未知命令 '{name}' 或未连接")

    def cmd_monitor(self, args: List[str]) -> None:
        """显示最近消息"""
        events = self.app.log_engine.get_all_events()
        for ev in events[-50:]:
            self._print(
                f"[{ev.timestamp:.3f}] {ev.direction:>2s} "
                f"[{ev.seq:02X}] {ev.msg_name}"
            )

    def cmd_messages(self, args: List[str]) -> None:
        """显示最近消息 (同 monitor)"""
        self.cmd_monitor(args)

    def cmd_dict(self, args: List[str]) -> None:
        """显示 data dictionary"""
        dict_obj = self.app.parser.get_dictionary()
        self._print(f"Dictionary 版本: {dict_obj.version}")
        self._print(f"消息数量: {len(dict_obj.messages)}")
        for mf in sorted(dict_obj.messages, key=lambda x: x.msgid):
            self._print(f"  [{mf.msgid:3d}] {mf.msgformat}")

    def cmd_sim_start(self, args: List[str]) -> None:
        """启动虚拟 MCU"""
        from ...simulator.virtual_mcu import VirtualMCU
        self.app.virtual_mcu = VirtualMCU("cli-mcu")
        self.app.virtual_mcu.on_response = self._on_sim_response
        self.app.virtual_mcu.start()
        self._print("虚拟 MCU 已启动")

    def cmd_sim_stop(self, args: List[str]) -> None:
        """停止虚拟 MCU"""
        if self.app.virtual_mcu:
            self.app.virtual_mcu.stop()
            self.app.virtual_mcu = None
            self._print("虚拟 MCU 已停止")
        else:
            self._print("虚拟 MCU 未运行")

    def cmd_sim_send(self, args: List[str]) -> None:
        """向虚拟 MCU 发送命令"""
        if not self.app.virtual_mcu:
            self._print("请先启动虚拟 MCU (sim_start)")
            return
        if not args:
            self._print("用法: sim_send <name> [json_params]")
            return
        name = args[0]
        params = {}
        if len(args) > 1:
            import json
            params = json.loads(args[1])
        encoded = self.app.parser.encode_message(name, **params)
        if encoded is None:
            self._print(f"未知命令: {name}")
            return
        self.app.virtual_mcu.feed_data(encoded)
        self._print(f"已发送: {name}")

    def _on_sim_response(self, resp_bytes: bytes) -> None:
        """Callback for virtual MCU response."""
        try:
            block = MessageBlock.decode(resp_bytes)
            parsed = self.app.parser.parse_block(block, direction="Rx")
            self._print(f"← 响应: {parsed.msg_name} {parsed.params}")
        except Exception as e:
            self._print(f"← 响应 (hex): {resp_bytes.hex()}")

    def cmd_capture(self, args: List[str]) -> None:
        """开始捕获"""
        path = self.app.capture_mgr.start()
        self._print(f"捕获已开始: {path}")

    def cmd_capture_stop(self, args: List[str]) -> None:
        """停止捕获"""
        path = self.app.capture_mgr.stop()
        self._print(f"捕获已停止: {path}")

    def cmd_stats(self, args: List[str]) -> None:
        """详细统计"""
        self.cmd_status(args)

    def cmd_export(self, args: List[str]) -> None:
        """导出日志"""
        fmt = args[0] if args else "text"
        from ...log.export import Exporter
        events = self.app.log_engine.get_all_events()
        if fmt == "csv":
            result = Exporter.to_csv(events)
        elif fmt == "text":
            result = Exporter.to_text(events)
        elif fmt == "hex":
            result = Exporter.to_hex_dump(events)
        else:
            self._print(f"不支持格式: {fmt} (支持: csv, text, hex)")
            return
        self._print(result)
