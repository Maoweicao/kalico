# Kalico Debug Tool - Interactive CLI REPL
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Interactive CLI REPL
====================

Command-line interface for Kalico protocol debugging using Python's
`cmd` module. Provides all commands available in the GUI CLI panel,
plus additional features for scripted usage.

Usage:
    python -m kalico_debug_tool --cli
"""

import cmd
import json
import logging
import shlex
import sys
import time
from typing import Any, Dict, List, Optional

from ..log.logger import LogEngine
from ..log.export import Exporter
from ..protocol.codec import (
    MessageBlock, bytes_to_hex, hex_to_bytes, format_hex_dump,
)
from ..protocol.parser import Parser, ParsedMessage
from ..protocol.dictionary import MessageDictionary
from ..io.serial_io import SerialIO, ConnectionState
from ..io.capture import CaptureManager
from ..io.replay import ReplayPlayback
from ..simulator.virtual_mcu import VirtualMCU


def _serialize_param(v: Any) -> str:
    """Serialize a parameter value for display."""
    if isinstance(v, bytes):
        return repr(v)
    return str(v)


class InteractiveCLI(cmd.Cmd):
    """Interactive command-line REPL for Kalico protocol debugging."""

    intro = (
        "\n╔══════════════════════════════════════════════╗\n"
        "║        Kalico Debug Tool - CLI Mode          ║\n"
        "║  Type 'help' for command list                ║\n"
        "║  Type 'exit' or Ctrl+C to quit               ║\n"
        "╚══════════════════════════════════════════════╝\n"
    )
    prompt = "(kalico) "

    def __init__(self):
        super().__init__()
        self.log_engine = LogEngine(max_events=10000)
        self.parser = Parser()
        self.serial_io = SerialIO(
            on_data=self._on_serial_data,
            on_error=self._on_serial_error,
        )
        self.capture_mgr = CaptureManager()
        self.virtual_mcu: Optional[VirtualMCU] = None
        self._monitoring = False

    # ─── Core Callbacks ──────────────────────────────────────────────

    def _on_serial_data(self, data: bytes) -> None:
        """Callback when serial data is received."""
        try:
            block = MessageBlock.decode(data)
            parsed = self.parser.parse_block(block, direction="Rx")
            self.log_engine.log_message(parsed, "Rx")
            print(f"  Rx [{parsed.seq:02X}] {parsed.msg_name}")
        except ValueError as e:
            self.log_engine.log_raw(data, "Rx", error=str(e))
            print(f"  Rx [raw] {data.hex()} ({e})")

    def _on_serial_error(self, error: Exception) -> None:
        """Callback on serial error."""
        print(f"  ⚠ 串口错误: {error}")

    # ─── Command Implementations ─────────────────────────────────────

    def do_help(self, arg: str) -> None:
        """显示命令帮助列表"""
        print("\n命令列表:")
        print("=" * 50)

        categories = {
            "连接管理": ["connect", "disconnect", "ports", "status"],
            "数据收发": ["send", "send_cmd", "send_raw"],
            "查看": ["monitor", "messages", "dict", "hex"],
            "捕获与回放": ["capture", "capture_stop", "replay"],
            "虚拟 MCU": ["sim_start", "sim_stop", "sim_send", "sim_reg", "sim_info"],
            "日志与导出": ["history", "stats", "export", "clear"],
            "工具": ["help", "exit"],
        }

        for category, cmds in categories.items():
            print(f"\n  {category}:")
            for c in cmds:
                doc = getattr(self, f"do_{c}", None)
                if doc and doc.__doc__:
                    first_line = doc.__doc__.strip().split("\n")[0]
                    print(f"    {c:<18} - {first_line}")
        print()

    def help_help(self) -> None:
        self.do_help("")

    def do_exit(self, arg: str) -> bool:
        """退出 CLI"""
        print("正在关闭...")
        if self.serial_io.is_connected():
            self.serial_io.disconnect()
        if self.virtual_mcu:
            self.virtual_mcu.stop()
        return True

    def do_EOF(self, arg: str) -> bool:
        """Ctrl+D to exit"""
        return self.do_exit(arg)

    # ─── Connection ──────────────────────────────────────────────────

    def do_ports(self, arg: str) -> None:
        """列出可用串口"""
        ports = SerialIO.list_ports()
        if ports:
            print("可用串口:")
            for p in ports:
                print(f"  - {p}")
        else:
            print("未检测到串口")

    def do_connect(self, arg: str) -> None:
        """连接串口: connect <port> [baudrate]"""
        args = shlex.split(arg)
        if not args:
            print("用法: connect <port> [baudrate]")
            return
        port = args[0]
        baudrate = int(args[1]) if len(args) > 1 else 250000
        print(f"正在连接 {port} @ {baudrate}...")
        result = self.serial_io.connect(port, baudrate)
        if result:
            print("✓ 连接成功")
        else:
            print("✗ 连接失败")

    def do_disconnect(self, arg: str) -> None:
        """断开串口连接"""
        self.serial_io.disconnect()
        print("已断开连接")

    def do_status(self, arg: str) -> None:
        """显示连接状态和统计"""
        stats = self.serial_io.get_stats()
        print(f"串口状态: {stats['state']}")
        print(f"  端口: {stats['port'] or 'N/A'}")
        print(f"  波特率: {stats['baudrate']}")
        print(f"  已发送: {stats['packets_sent']} 包")
        print(f"  已接收: {stats['packets_received']} 包")
        print(f"  持续时间: {stats['duration']}s")
        if self.virtual_mcu:
            mcu_stats = self.virtual_mcu.get_stats()
            print(f"虚拟 MCU:")
            print(f"  状态: {mcu_stats['state']}")
            print(f"  已接收命令: {mcu_stats['commands_received']}")
            print(f"  已发送响应: {mcu_stats['responses_sent']}")

    # ─── Send ────────────────────────────────────────────────────────

    def do_send(self, arg: str) -> None:
        """发送原始 HEX: send <hex_bytes>"""
        if not arg.strip():
            print("用法: send <hex_bytes>")
            return
        try:
            data = hex_to_bytes(arg)
            if not self.serial_io.is_connected():
                print("未连接")
                return
            self.log_engine.log_raw(data, "Tx")
            self.serial_io.send(data)
            print(f"已发送 {len(data)} 字节: {data.hex()}")
        except ValueError as e:
            print(f"无效 HEX: {e}")

    def do_send_cmd(self, arg: str) -> None:
        """发送命令: send_cmd <name> [json_params]"""
        try:
            args = shlex.split(arg)
        except ValueError:
            print("参数解析错误")
            return
        if not args:
            print("用法: send_cmd <name> [json_params]")
            return
        name = args[0]
        params = {}
        if len(args) > 1:
            try:
                params = json.loads(args[1])
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
                return
        if self.serial_io.is_connected():
            encoded = self.parser.encode_message(name, **params)
            if encoded:
                self.log_engine.log_raw(encoded, "Tx")
                self.serial_io.send(encoded)
                print(f"已发送命令: {name}")
            else:
                print(f"未知命令: {name}")
        else:
            print("未连接")

    def do_send_raw(self, arg: str) -> None:
        """发送原始字节 (同 send)"""
        self.do_send(arg)

    # ─── View ────────────────────────────────────────────────────────

    def do_monitor(self, arg: str) -> None:
        """显示最近消息"""
        events = self.log_engine.get_all_events()
        if not events:
            print("暂无消息")
            return
        for ev in events[-50:]:
            print(
                f"  [{ev.timestamp:.3f}] {ev.direction} "
                f"[{ev.seq:02X}] {ev.msg_name}"
            )

    def do_messages(self, arg: str) -> None:
        """显示消息列表"""
        self.do_monitor(arg)

    def do_dict(self, arg: str) -> None:
        """显示 data dictionary"""
        dict_obj = self.parser.get_dictionary()
        print(f"Dictionary 版本: {dict_obj.version}")
        print(f"消息数: {len(dict_obj.messages)}")
        for mf in sorted(dict_obj.messages, key=lambda x: x.msgid):
            print(f"  [{mf.msgid:3d}] {mf.msgformat}")

    def do_hex(self, arg: str) -> None:
        """显示最近的 HEX dump"""
        events = self.log_engine.get_all_events()
        if not events:
            print("暂无消息")
            return
        ev = events[-1]
        print(f"最新消息: {ev.msg_name} [{ev.direction}]")
        print(format_hex_dump(ev.raw_bytes))

    # ─── Capture & Replay ────────────────────────────────────────────

    def do_capture(self, arg: str) -> None:
        """开始捕获: capture [name]"""
        name = arg.strip() or None
        path = self.capture_mgr.start(name)
        print(f"捕获已开始: {path}")

    def do_capture_stop(self, arg: str) -> None:
        """停止捕获"""
        path = self.capture_mgr.stop()
        print(f"捕获已停止: {path}")

    def do_replay(self, arg: str) -> None:
        """回放捕获文件: replay <file> [speed]"""
        args = shlex.split(arg)
        if not args:
            print("用法: replay <file> [speed]")
            return
        filepath = args[0]
        speed = float(args[1]) if len(args) > 1 else 1.0
        import os
        if not os.path.exists(filepath):
            print(f"文件不存在: {filepath}")
            return
        playback = ReplayPlayback(filepath)
        playback.speed = speed
        playback.on_rx = lambda data: print(f"  Rx: {data.hex()}")
        playback.on_tx = lambda data: print(f"  Tx: {data.hex()}")
        print(f"回放开始: {filepath} @ {speed}x")
        playback.play()

    # ─── Virtual MCU ─────────────────────────────────────────────────

    def do_sim_start(self, arg: str) -> None:
        """启动虚拟 MCU: sim_start [name]"""
        name = arg.strip() or "cli-mcu"
        self.virtual_mcu = VirtualMCU(name)
        self.virtual_mcu.on_response = self._on_sim_response
        self.virtual_mcu.start()
        print(f"虚拟 MCU '{name}' 已启动")

    def do_sim_stop(self, arg: str) -> None:
        """停止虚拟 MCU"""
        if self.virtual_mcu:
            self.virtual_mcu.stop()
            self.virtual_mcu = None
            print("虚拟 MCU 已停止")
        else:
            print("虚拟 MCU 未运行")

    def do_sim_send(self, arg: str) -> None:
        """向虚拟 MCU 发送命令: sim_send <name> [json_params]"""
        try:
            args = shlex.split(arg)
        except ValueError:
            print("参数解析错误")
            return
        if not self.virtual_mcu:
            print("请先启动虚拟 MCU (sim_start)")
            return
        if not args:
            print("用法: sim_send <name> [json_params]")
            return
        name = args[0]
        params = {}
        if len(args) > 1:
            try:
                params = json.loads(args[1])
            except json.JSONDecodeError as e:
                print(f"JSON 解析错误: {e}")
                return
        encoded = self.parser.encode_message(name, **params)
        if encoded is None:
            print(f"未知命令: {name}")
            return
        self.virtual_mcu.feed_data(encoded)
        print(f"已发送: {name}")

    def do_sim_reg(self, arg: str) -> None:
        """注册模拟响应: sim_reg <name> <hex_response>"""
        args = shlex.split(arg)
        if not self.virtual_mcu:
            print("请先启动虚拟 MCU")
            return
        if len(args) < 2:
            print("用法: sim_reg <name> <hex_response>")
            return
        name = args[0]
        try:
            data = hex_to_bytes(args[1])
            self.virtual_mcu.register_response(name, data)
            print(f"已注册命令 '{name}' 的响应")
        except ValueError as e:
            print(f"无效 HEX: {e}")

    def do_sim_info(self, arg: str) -> None:
        """显示虚拟 MCU 状态"""
        if not self.virtual_mcu:
            print("虚拟 MCU 未运行")
            return
        stats = self.virtual_mcu.get_stats()
        for k, v in stats.items():
            print(f"  {k}: {v}")

    def _on_sim_response(self, resp_bytes: bytes) -> None:
        """Callback for virtual MCU response."""
        try:
            block = MessageBlock.decode(resp_bytes)
            parsed = self.parser.parse_block(block, direction="Rx")
            print(f"  ← {parsed.msg_name} {parsed.params}")
        except Exception as e:
            print(f"  ← raw: {resp_bytes.hex()}")

    # ─── Log & Export ────────────────────────────────────────────────

    def do_history(self, arg: str) -> None:
        """显示历史消息 (同 monitor)"""
        self.do_monitor(arg)

    def do_stats(self, arg: str) -> None:
        """显示详细统计"""
        self.do_status(arg)

    def do_export(self, arg: str) -> None:
        """导出日志: export <csv|text|hex> [file]"""
        args = shlex.split(arg)
        if not args:
            print("用法: export <csv|text|hex> [file]")
            return
        fmt = args[0]
        filepath = args[1] if len(args) > 1 else None
        events = self.log_engine.get_all_events()
        if not events:
            print("暂无日志")
            return
        if fmt == "csv":
            result = Exporter.to_csv(events, filepath)
        elif fmt == "text":
            result = Exporter.to_text(events, filepath)
        elif fmt == "hex":
            result = Exporter.to_hex_dump(events, filepath)
        else:
            print(f"不支持格式: {fmt}")
            return
        if result:
            print(result)
        else:
            print(f"已导出到: {filepath}")

    def do_clear(self, arg: str) -> None:
        """清除日志缓冲区"""
        self.log_engine.clear()
        print("日志已清除")


def run_cli() -> None:
    """Run the interactive CLI."""
    try:
        InteractiveCLI().cmdloop()
    except KeyboardInterrupt:
        print("\n正在退出...")
