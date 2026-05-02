# Benchmark panel for Kalico MCU performance testing
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Benchmark Panel
===============

GUI panel for running MCU performance benchmarks against a real or
virtual Kalico MCU. Supports individual benchmark types and a
full combined test.

Benchmarks:
  - 步进速率: Stepper step rate saturation test
  - 串口吞吐量: Serial throughput measurement
  - 命令延迟: Roundtrip command latency distribution
  - 时钟精度: MCU clock stability measurement
  - 完整测试: All benchmarks with combined report
"""

import logging
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from ...protocol.parser import Parser
from ...protocol.codec import MessageBlock

if TYPE_CHECKING:
    from ..main_window import DebugToolWindow


class BenchmarkPanel(ttk.Frame):
    """Panel for running MCU performance benchmarks."""

    def __init__(self, parent, app: "DebugToolWindow"):
        super().__init__(parent)
        self.app = app
        self._engine = None
        self._running = False
        self._current_results: Optional[Dict[str, Any]] = None

        self._build_ui()

    def _build_ui(self) -> None:
        """Build the benchmark panel UI."""
        main = ttk.Frame(self, padding=10)
        main.pack(fill=tk.BOTH, expand=True)

        # ─── Top: Mode + shared connection status ────────────────────
        mode_frame = ttk.LabelFrame(main, text="🎯 测试目标", padding=8)
        mode_frame.pack(fill=tk.X, pady=(0, 10))

        mode_row = ttk.Frame(mode_frame)
        mode_row.pack(fill=tk.X, pady=3)
        self._target_var = tk.StringVar(value="real")
        ttk.Radiobutton(mode_row, text="🔌 使用连接面板的连接",
                        variable=self._target_var,
                        value="real").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(mode_row, text="🖥️ 虚拟 MCU",
                        variable=self._target_var,
                        value="virtual").pack(side=tk.LEFT, padx=10)

        # Live connection status indicator
        self._conn_status_label = ttk.Label(
            mode_frame, text="⭕ 未连接", foreground="gray", font=("", 9))
        self._conn_status_label.pack(anchor=tk.W, padx=10, pady=(0, 3))

        # The refresh/status button is redundant — we auto-update

        # ─── Config Frame ────────────────────────────────────────────
        cfg_frame = ttk.LabelFrame(main, text="测试参数", padding=8)
        cfg_frame.pack(fill=tk.X, pady=(0, 10))

        cfg_grid = ttk.Frame(cfg_frame)
        cfg_grid.pack(fill=tk.X)

        # Row 0: Stepper OID + Sample count
        ttk.Label(cfg_grid, text="步进电机 OID:").grid(row=0, column=0,
                                                      sticky=tk.W, padx=3)
        self._oid_var = tk.StringVar(value="0")
        ttk.Spinbox(cfg_grid, from_=0, to=255, width=5,
                    textvariable=self._oid_var).grid(row=0, column=1,
                                                      sticky=tk.W, padx=3)

        ttk.Label(cfg_grid, text="延迟采样数:").grid(row=0, column=2,
                                                    sticky=tk.W, padx=3)
        self._latency_samples_var = tk.StringVar(value="100")
        ttk.Spinbox(cfg_grid, from_=10, to=1000, width=6,
                    textvariable=self._latency_samples_var).grid(
            row=0, column=3, sticky=tk.W, padx=3)

        ttk.Label(cfg_grid, text="吞吐量包数:").grid(row=0, column=4,
                                                    sticky=tk.W, padx=3)
        self._tp_packets_var = tk.StringVar(value="2000")
        ttk.Spinbox(cfg_grid, from_=100, to=50000, width=6,
                    textvariable=self._tp_packets_var).grid(
            row=0, column=5, sticky=tk.W, padx=3)

        ttk.Label(cfg_grid, text="时钟测试时长(s):").grid(row=1, column=0,
                                                        sticky=tk.W, padx=3)
        self._clock_duration_var = tk.StringVar(value="10")
        ttk.Spinbox(cfg_grid, from_=2, to=120, width=5,
                    textvariable=self._clock_duration_var).grid(
            row=1, column=1, sticky=tk.W, padx=3)

        # ─── Buttons ─────────────────────────────────────────────────
        btn_frame = ttk.LabelFrame(main, text="运行测试", padding=8)
        btn_frame.pack(fill=tk.X, pady=(0, 10))

        btn_row = ttk.Frame(btn_frame)
        btn_row.pack(fill=tk.X, pady=3)

        self._btn_latency = ttk.Button(btn_row, text="⏱ 命令延迟",
                                       command=lambda: self._run_single("latency"),
                                       width=14)
        self._btn_latency.pack(side=tk.LEFT, padx=4)

        self._btn_throughput = ttk.Button(btn_row, text="📊 吞吐量",
                                          command=lambda: self._run_single("throughput"),
                                          width=14)
        self._btn_throughput.pack(side=tk.LEFT, padx=4)

        self._btn_steprate = ttk.Button(btn_row, text="⚡ 步进速率",
                                        command=lambda: self._run_single("step_rate"),
                                        width=14)
        self._btn_steprate.pack(side=tk.LEFT, padx=4)

        self._btn_clock = ttk.Button(btn_row, text="🕐 时钟精度",
                                     command=lambda: self._run_single("clock"),
                                     width=14)
        self._btn_clock.pack(side=tk.LEFT, padx=4)

        self._btn_full = ttk.Button(btn_row, text="🚀 完整测试",
                                    command=self._run_full,
                                    width=14, style="Accent.TButton")
        self._btn_full.pack(side=tk.LEFT, padx=4)

        self._btn_stop = ttk.Button(btn_row, text="⏹ 停止",
                                    command=self._stop_benchmark,
                                    state="disabled", width=8)
        self._btn_stop.pack(side=tk.RIGHT, padx=4)

        # ─── Progress ────────────────────────────────────────────────
        progress_frame = ttk.Frame(main)
        progress_frame.pack(fill=tk.X, pady=(0, 5))

        self._progress_var = tk.StringVar(value="就绪")
        ttk.Label(progress_frame, textvariable=self._progress_var,
                  font=("", 9)).pack(side=tk.LEFT)

        self._progress_bar = ttk.Progressbar(
            progress_frame, mode="indeterminate", length=200)
        self._progress_bar.pack(side=tk.RIGHT)

        # ─── Results ─────────────────────────────────────────────────
        result_frame = ttk.LabelFrame(main, text="测试结果", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True)

        # Results paned: summary table + detail text
        result_paned = ttk.PanedWindow(result_frame, orient=tk.VERTICAL)
        result_paned.pack(fill=tk.BOTH, expand=True)

        # Summary tree
        summary_frame = ttk.Frame(result_paned)
        result_paned.add(summary_frame, weight=1)

        self._result_tree = ttk.Treeview(
            summary_frame, columns=("name", "result", "val1", "val2"),
            show="headings", height=4
        )
        self._result_tree.heading("name", text="测试项")
        self._result_tree.heading("result", text="结果")
        self._result_tree.heading("val1", text="指标 1")
        self._result_tree.heading("val2", text="指标 2")
        self._result_tree.column("name", width=120)
        self._result_tree.column("result", width=60)
        self._result_tree.column("val1", width=200)
        self._result_tree.column("val2", width=200)
        self._result_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)

        vsb = ttk.Scrollbar(summary_frame, orient="vertical",
                            command=self._result_tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self._result_tree.configure(yscrollcommand=vsb.set)

        # Detail text
        detail_frame = ttk.Frame(result_paned)
        result_paned.add(detail_frame, weight=2)

        self._result_text = tk.Text(
            detail_frame, font=("Consolas", 9), wrap=tk.WORD,
            state="disabled", height=10
        )
        self._result_text.pack(fill=tk.BOTH, expand=True)

        ttk.Scrollbar(self._result_text, orient="vertical",
                      command=self._result_text.yview).pack(
            side=tk.RIGHT, fill=tk.Y)
        self._result_text.config(yscrollcommand=lambda *a: None)

        # Toolbar below results
        tool_row = ttk.Frame(result_frame)
        tool_row.pack(fill=tk.X, pady=3)
        ttk.Button(tool_row, text="📋 复制报告",
                   command=self._copy_report).pack(side=tk.LEFT, padx=3)
        ttk.Button(tool_row, text="🗑 清除结果",
                   command=self._clear_results).pack(side=tk.LEFT, padx=3)

        # Initial state
        self._refresh_status()

    # ── Engine creation ──────────────────────────────────────────────

    def _create_engine(self) -> Optional[Any]:
        """Create a BenchmarkEngine for the current target."""
        from ...benchmark.engine import BenchmarkEngine

        target = self._target_var.get()
        if target == "virtual":
            mcu = self.app.virtual_mcu
            if mcu is None:
                messagebox.showwarning("提示", "请先在「虚拟 MCU」标签页启动模拟器")
                return None

            def send_fn(data: bytes) -> bool:
                mcu.feed_data(data)
                return True

            def recv_fn():
                # Not directly available from virtual MCU,
                # use log engine as proxy
                return self.app.log_engine.get_all_events()

            return BenchmarkEngine(
                parser=self.app.parser,
                send_fn=send_fn,
                recv_fn=recv_fn,
                simulator_mode=True,
                on_progress=self._on_progress_msg,
            )

        # Real device
        mode = self.app.connection_panel._active_mode.get()
        io = self.app.can_io if mode == "can" else self.app.serial_io

        if not io.is_connected():
            messagebox.showwarning("未连接", "请先连接到设备")
            return None

        def send_fn(data: bytes) -> bool:
            return io.send(data)

        def recv_fn():
            return self.app.log_engine.get_all_events()

        return BenchmarkEngine(
            parser=self.app.parser,
            send_fn=send_fn,
            recv_fn=recv_fn,
            simulator_mode=False,
            on_progress=self._on_progress_msg,
        )

    # ── Run benchmarks ───────────────────────────────────────────────

    def _run_single(self, btype: str) -> None:
        """Run a single benchmark type."""
        engine = self._create_engine()
        if engine is None:
            return

        self._running = True
        engine._running = True
        self._set_running_state(True)
        self._progress_var.set(f"运行 {btype}...")
        self._progress_bar.start(10)

        from ...benchmark.engine import BenchmarkConfig, BenchmarkType

        def make_cfg(bt: BenchmarkType):
            try:
                oid = int(self._oid_var.get())
            except ValueError:
                oid = 0
            try:
                lat_samples = int(self._latency_samples_var.get())
            except ValueError:
                lat_samples = 100
            try:
                tp_packets = int(self._tp_packets_var.get())
            except ValueError:
                tp_packets = 2000
            try:
                clk_dur = float(self._clock_duration_var.get())
            except ValueError:
                clk_dur = 10.0
            return BenchmarkConfig(
                type=bt, stepper_oid=oid,
                latency_sample_count=lat_samples,
                throughput_packet_count=tp_packets,
                clock_duration=clk_dur,
            )

        def thread():
            try:
                result = None
                if btype == "latency":
                    result = engine.run_latency(make_cfg(BenchmarkType.LATENCY))
                elif btype == "throughput":
                    result = engine.run_throughput(
                        make_cfg(BenchmarkType.THROUGHPUT))
                elif btype == "step_rate":
                    result = engine.run_step_rate(
                        make_cfg(BenchmarkType.STEP_RATE))
                elif btype == "clock":
                    result = engine.run_clock(make_cfg(BenchmarkType.CLOCK))
                self.after(0, self._display_single_result, btype, result)
            except Exception as e:
                self.after(0, lambda: self._progress_var.set(
                    f"错误: {e}"))
            finally:
                self.after(0, lambda: self._set_running_state(False))
                self.after(0, self._progress_bar.stop)
                self._running = False

        threading.Thread(target=thread, daemon=True).start()

    def _run_full(self) -> None:
        """Run the full benchmark suite."""
        engine = self._create_engine()
        if engine is None:
            return

        self._running = True
        engine._running = True
        self._set_running_state(True)
        self._progress_var.set("运行完整基准测试...")
        self._progress_bar.start(10)

        from ...benchmark.engine import BenchmarkConfig

        def thread():
            try:
                oid = int(self._oid_var.get())
            except ValueError:
                oid = 0
            try:
                lat_samples = int(self._latency_samples_var.get())
            except ValueError:
                lat_samples = 100
            try:
                tp_packets = int(self._tp_packets_var.get())
            except ValueError:
                tp_packets = 2000
            try:
                clk_dur = float(self._clock_duration_var.get())
            except ValueError:
                clk_dur = 10.0

            cfg = BenchmarkConfig(
                stepper_oid=oid,
                latency_sample_count=lat_samples,
                throughput_packet_count=tp_packets,
                clock_duration=clk_dur,
            )

            try:
                results = engine.run_full(cfg)
                self.after(0, self._display_full_results, results)
            except Exception as e:
                self.after(0, lambda: self._progress_var.set(
                    f"错误: {e}"))
            finally:
                self.after(0, lambda: self._set_running_state(False))
                self.after(0, self._progress_bar.stop)
                self._running = False

        threading.Thread(target=thread, daemon=True).start()

    def _stop_benchmark(self) -> None:
        """Stop the currently running benchmark."""
        self._running = False
        self._progress_var.set("已停止")

    # ── Display results ──────────────────────────────────────────────

    def _display_single_result(self, btype: str,
                               result: Any) -> None:
        """Display a single benchmark result."""
        from ...benchmark.engine import BenchmarkResult, format_result_summary

        if not isinstance(result, BenchmarkResult):
            return
        s = result.summary()

        # Clear tree
        for item in self._result_tree.get_children():
            self._result_tree.delete(item)

        labels = {
            "latency": "命令延迟", "throughput": "串口吞吐量",
            "step_rate": "步进速率", "clock": "时钟精度",
        }
        label = labels.get(btype, btype)
        status = "✓" if s["success"] else "✗"
        val1 = ""
        val2 = ""
        if s["success"]:
            if btype == "latency":
                val1 = f"avg={s['avg']:.1f} µs"
                val2 = f"max={s['max']:.1f} µs"
            elif btype == "throughput":
                val1 = f"avg={s['avg']/1024:.1f} KB/s"
                val2 = f"max={s['max']/1024:.1f} KB/s"
            elif btype == "step_rate":
                val1 = f"max={s['max']:.0f} steps/s"
                val2 = f"avg={s['avg']:.0f} steps/s"
            elif btype == "clock":
                val1 = f"drift={s['avg']:+.1f} µs"
                val2 = f"stddev={s['stddev']:.1f} µs"

        self._result_tree.insert("", tk.END,
                                 values=(label, status, val1, val2))

        # Detail text
        self._result_text.config(state="normal")
        self._result_text.delete("1.0", tk.END)
        self._result_text.insert(tk.END, result.text_report())
        self._result_text.config(state="disabled")

        self._current_results = {"single": s}
        self._progress_var.set(f"{label} 完成 ({s['duration']}s)")

    def _display_full_results(self,
                              results: Dict[str, Any]) -> None:
        """Display full benchmark results."""
        from ...benchmark.engine import BenchmarkResult, format_result_summary

        for item in self._result_tree.get_children():
            self._result_tree.delete(item)

        all_ok = True
        for name, r in results.items():
            if not isinstance(r, BenchmarkResult):
                continue
            s = r.summary()
            if not s["success"]:
                all_ok = False
            labels = {
                "latency": "命令延迟", "throughput": "串口吞吐量",
                "step_rate": "步进速率", "clock": "时钟精度",
            }
            label = labels.get(name, name)
            status = "✓" if s["success"] else "✗"
            val1 = ""
            val2 = ""
            if s["success"]:
                if name == "latency":
                    val1 = f"avg={s['avg']:.1f} µs"
                    val2 = f"max={s['max']:.1f} µs"
                elif name == "throughput":
                    val1 = f"avg={s['avg']/1024:.1f} KB/s"
                    val2 = f"{s['samples']} samples"
                elif name == "step_rate":
                    val1 = f"max={s['max']:.0f} steps/s"
                    val2 = f"avg={s['avg']:.0f} steps/s"
                elif name == "clock":
                    val1 = f"stddev={s['stddev']:.1f} µs"
                    val2 = f"{s['duration']}s duration"

            self._result_tree.insert("", tk.END,
                                     values=(label, status, val1, val2))

        # Full text report
        report = format_result_summary(results)
        self._result_text.config(state="normal")
        self._result_text.delete("1.0", tk.END)
        self._result_text.insert(tk.END, report)
        self._result_text.config(state="disabled")

        status = "全部通过 ✓" if all_ok else "部分失败"
        self._progress_var.set(f"完整测试完成 - {status}")
        self._current_results = results

    # ── UI helpers ───────────────────────────────────────────────────

    def _on_progress_msg(self, msg: str) -> None:
        """Progress callback (called from benchmark thread)."""
        self.after(0, lambda: self._progress_var.set(msg))

    def _set_running_state(self, running: bool) -> None:
        """Enable/disable buttons during benchmark."""
        state = "disabled" if running else "normal"
        for btn in [self._btn_latency, self._btn_throughput,
                     self._btn_steprate, self._btn_clock, self._btn_full]:
            btn.config(state=state)
        self._btn_stop.config(state="normal" if running else "disabled")

    def _refresh_status(self) -> None:
        """Refresh the connection status display — shows live state of
        the connection panel's active I/O (real device) or
        virtual MCU status."""
        # Check real device connection
        mode = self.app.connection_panel._active_mode.get()
        io = self.app.can_io if mode == "can" else self.app.serial_io
        io_type = mode.upper()
        if io.is_tcp:
            io_type = "TCP"

        state = io.state.value
        if state == "connected":
            port = getattr(io, '_port', '') or getattr(io, '_can_channel', '')
            self._conn_status_label.config(
                text=f"🟢 [{io_type}] 已连接 {port}",
                foreground="green")
        elif state == "connecting":
            self._conn_status_label.config(
                text="🟡 连接中...", foreground="orange")
        elif state == "error":
            self._conn_status_label.config(
                text="🔴 连接错误", foreground="red")
        else:
            self._conn_status_label.config(
                text="⭕ [连接面板] 未连接 — 请先在「🔌 连接」标签页连接设备",
                foreground="gray")

        # Also check virtual MCU
        if self.app.virtual_mcu:
            vmcu_stats = self.app.virtual_mcu.get_stats()
            vmcu_status = f"🟢 虚拟MCU运行中 ({vmcu_stats['commands_received']} cmds)"
        else:
            vmcu_status = "⭕ 虚拟MCU未启动"

        self.after(2000, self._refresh_status)

    def _copy_report(self) -> None:
        """Copy the result text to clipboard."""
        self._result_text.config(state="normal")
        text = self._result_text.get("1.0", tk.END)
        self._result_text.config(state="disabled")
        if text.strip():
            self.clipboard_clear()
            self.clipboard_append(text.strip())

    def _clear_results(self) -> None:
        """Clear displayed results."""
        for item in self._result_tree.get_children():
            self._result_tree.delete(item)
        self._result_text.config(state="normal")
        self._result_text.delete("1.0", tk.END)
        self._result_text.config(state="disabled")
        self._current_results = None
        self._progress_var.set("结果已清除")
