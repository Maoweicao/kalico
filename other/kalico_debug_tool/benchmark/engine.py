# Kalico MCU Benchmark Engine
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Benchmark Engine
================

MCU performance benchmarking suite for Kalico/Klipper firmware.
Runs standardized benchmarks against a real or virtual MCU to
measure step rate capacity, serial throughput, command latency,
clock accuracy, and overall MCU performance.

Benchmark Types:
  - step_rate:   Measure maximum step rate before MCU stalls
  - throughput:  Serial communication bandwidth test
  - latency:     Command roundtrip time distribution
  - clock:       Clock accuracy and drift measurement
  - full:        Comprehensive combined benchmark
"""

import logging
import math
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..protocol.codec import MessageBlock, VLQEncoder
from ..protocol.parser import Parser, ParsedMessage


__all__ = [
    "BenchmarkType", "BenchmarkResult", "BenchmarkConfig",
    "BenchmarkEngine", "format_result_summary",
]


class BenchmarkType(str, Enum):
    """Available benchmark types."""
    STEP_RATE = "step_rate"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    CLOCK = "clock"
    FULL = "full"


@dataclass
class BenchmarkConfig:
    """Configuration for a benchmark run."""
    type: BenchmarkType = BenchmarkType.FULL

    # Step rate test
    stepper_oid: int = 0
    step_interval_start: int = 100     # initial interval (ticks)
    step_interval_end: int = 1000       # max interval (ticks)
    step_interval_step: int = -50       # decrease per step
    step_count_per_test: int = 1000     # steps per test point
    step_add: int = 0                   # interval add (acceleration)

    # Throughput test
    payload_size: int = 40              # bytes per command
    throughput_packet_count: int = 2000 # total commands to send

    # Latency test
    latency_sample_count: int = 100     # number of ping samples

    # Clock test
    clock_duration: float = 10.0        # seconds to monitor
    clock_sample_interval: float = 0.5  # seconds between samples

    def label(self) -> str:
        return {
            BenchmarkType.STEP_RATE: "步进速率测试",
            BenchmarkType.THROUGHPUT: "串口吞吐量测试",
            BenchmarkType.LATENCY: "命令延迟测试",
            BenchmarkType.CLOCK: "时钟精度测试",
            BenchmarkType.FULL: "完整基准测试",
        }.get(self.type, "未知")


@dataclass
class BenchmarkSample:
    """A single measurement data point."""
    label: str              # data point label
    value: float            # measured value
    unit: str               # unit string (steps/s, µs, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkResult:
    """Complete result of a benchmark run."""
    type: BenchmarkType
    config: BenchmarkConfig
    success: bool
    duration: float = 0.0
    error: str = ""
    samples: List[BenchmarkSample] = field(default_factory=list)

    # Computed summary metrics
    max_value: float = 0.0
    min_value: float = 0.0
    avg_value: float = 0.0
    stddev_value: float = 0.0
    unit: str = ""

    def _compute_stats(self) -> None:
        """Compute summary statistics from samples."""
        values = [s.value for s in self.samples if s.value > 0]
        if not values:
            return
        self.max_value = max(values)
        self.min_value = min(values)
        self.avg_value = sum(values) / len(values)
        if len(values) > 1:
            variance = sum((v - self.avg_value) ** 2 for v in values) / len(values)
            self.stddev_value = math.sqrt(variance)
        if self.samples:
            self.unit = self.samples[0].unit

    def summary(self) -> Dict[str, Any]:
        """Get a dict summary of the benchmark result."""
        self._compute_stats()
        return {
            "type": self.type.value,
            "success": self.success,
            "duration": round(self.duration, 3),
            "error": self.error,
            "max": round(self.max_value, 2),
            "min": round(self.min_value, 2),
            "avg": round(self.avg_value, 2),
            "stddev": round(self.stddev_value, 2),
            "unit": self.unit,
            "samples": len(self.samples),
        }

    def text_report(self) -> str:
        """Generate human-readable report."""
        s = self.summary()
        lines = [
            f"{'='*50}",
            f"  Test: {self.config.label()}",
            f"  Result: {'PASS' if self.success else 'FAIL'}",
            f"  Duration: {s['duration']}s",
            f"{'='*50}",
        ]
        if self.error:
            lines.append(f"  Error: {self.error}")
        if self.samples:
            lines.append(
                f"  Max: {s['max']} {s['unit']}"
            )
            lines.append(
                f"  Min: {s['min']} {s['unit']}"
            )
            lines.append(
                f"  Avg: {s['avg']} {s['unit']}"
            )
            lines.append(
                f"  StdDev: {s['stddev']} {s['unit']}"
            )
            lines.append(f"  Samples: {s['samples']}")
            lines.append("")
            lines.append("  Data:")
            for sample in self.samples:
                lines.append(
                    f"    {sample.label}: {sample.value} {sample.unit}"
                )
        lines.append(f"{'='*50}")
        return "\n".join(lines)


# ─── Send function type ──────────────────────────────────────────────

SendFunc = Callable[[bytes], bool]


class BenchmarkEngine:
    """Runs benchmarks against a Kalico MCU.

    Requires a `send` function that sends raw bytes to the MCU
    and a `recv` function that returns recently received responses.
    """

    def __init__(self, parser: Parser,
                 send_fn: SendFunc,
                 recv_fn: Callable[[], List[ParsedMessage]],
                 simulator_mode: bool = False,
                 on_progress: Optional[Callable[[str], None]] = None):
        self.parser = parser
        self.send_fn = send_fn
        self.recv_fn = recv_fn
        self.simulator_mode = simulator_mode
        self.on_progress = on_progress

        # Runtime state
        self._running = True  # starts True; set False to stop
        self._current_seq = 0
        self._clock_freq: float = 1000000.0  # 1 MHz default

    def _progress(self, msg: str) -> None:
        if self.on_progress:
            self.on_progress(msg)
        logging.info(f"[benchmark] {msg}")

    def _get_seq(self) -> int:
        s = self._current_seq
        self._current_seq = (self._current_seq + 1) & 0x0F
        return s

    def _send_cmd(self, name: str, **params) -> bool:
        """Send a named command via the I/O channel."""
        encoded = self.parser.encode_message(name, seq=self._get_seq(),
                                             **params)
        if encoded is None:
            return False
        return self.send_fn(encoded)

    def _get_msg_count(self) -> int:
        """Get number of received messages since last call."""
        msgs = self.recv_fn()
        return len(msgs)

    def _wait_for_responses(self, min_count: int = 1,
                            timeout: float = 2.0) -> int:
        """Wait until we have at least min_count messages or timeout."""
        start = time.monotonic()
        total = 0
        while time.monotonic() - start < timeout:
            total += self._get_msg_count()
            if total >= min_count:
                return total
            time.sleep(0.01)
        return total

    def _drain_responses(self) -> None:
        """Drain all pending responses."""
        self.recv_fn()  # discard

    # ── Individual Benchmarks ─────────────────────────────────────────

    def run_step_rate(self, cfg: Optional[BenchmarkConfig] = None
                      ) -> BenchmarkResult:
        """Step Rate Benchmark.

        Sends queue_step commands at increasing rates until the MCU
        fails to keep up. Measures the maximum sustainable step rate.
        """
        cfg = cfg or BenchmarkConfig(type=BenchmarkType.STEP_RATE)
        result = BenchmarkResult(type=BenchmarkType.STEP_RATE, config=cfg,
                                 success=True)
        start_time = time.monotonic()

        try:
            # Try decreasing intervals (faster steps)
            interval = cfg.step_interval_start
            direction = cfg.step_interval_step  # typically negative = faster
            last_success_interval = None
            success_count = 0

            self._progress("步进速率测试开始...")
            while True:
                if not self._running:
                    raise InterruptedError("测试被中断")

                interval = interval + direction
                if direction < 0 and interval < 10:
                    # Too fast, check if we have enough samples
                    if success_count < 3:
                        # Go back and try finer granularity
                        interval = last_success_interval or 100
                        direction = max(-1, int(direction / 2))
                        if direction == 0:
                            break
                        continue
                    break
                if direction > 0 and interval > 10000:
                    break

                # Send queue_step commands
                self._drain_responses()
                for _ in range(cfg.step_count_per_test):
                    self._send_cmd("queue_step", oid=cfg.stepper_oid,
                                   interval=interval, count=1, add=0)

                # Wait for ACKs / responses
                resp_count = self._wait_for_responses(
                    min_count=cfg.step_count_per_test // 2,
                    timeout=0.5)

                if resp_count >= cfg.step_count_per_test // 4:
                    # MCU can keep up
                    step_rate = (self._clock_freq / interval
                                 if interval > 0 else float('inf'))
                    last_success_interval = interval
                    success_count += 1

                    sample = BenchmarkSample(
                        label=f"interval={interval}",
                        value=step_rate,
                        unit="steps/s",
                        metadata={"interval": interval,
                                  "responses": resp_count},
                    )
                    result.samples.append(sample)

                    self._progress(
                        f"  interval={interval:5d} → "
                        f"{step_rate:10.0f} steps/s ✓"
                    )
                else:
                    # MCU can't keep up
                    self._progress(
                        f"  interval={interval:5d} → "
                        f"失败 (仅 {resp_count}/{cfg.step_count_per_test} 响应)"
                    )
                    if direction < 0:
                        # Getting faster, hitting limit - reverse direction
                        if last_success_interval is not None:
                            interval = last_success_interval
                            direction = max(-1, int(direction / 2))
                            if direction == 0:
                                break
                            continue
                        break
                    break

                # Limit total test time
                if time.monotonic() - start_time > 30:
                    self._progress("测试时间上限(30s)")
                    break

        except InterruptedError:
            result.success = False
            result.error = "测试被中断"
        except Exception as e:
            result.success = False
            result.error = str(e)
            logging.exception("Step rate benchmark error")

        result.duration = time.monotonic() - start_time
        if not result.samples:
            result.success = False
            result.error = result.error or "无有效数据"
        self._progress(f"步进速率测试完成 ({result.duration:.1f}s)")
        return result

    def run_throughput(self, cfg: Optional[BenchmarkConfig] = None
                       ) -> BenchmarkResult:
        """Serial Throughput Benchmark.

        Sends many commands rapidly and measures throughput.
        """
        cfg = cfg or BenchmarkConfig(type=BenchmarkType.THROUGHPUT)
        result = BenchmarkResult(type=BenchmarkType.THROUGHPUT,
                                 config=cfg, success=True)
        start_time = time.monotonic()

        batch_size = 100
        total_sent = 0

        try:
            self._progress("串口吞吐量测试开始...")

            # Pre-build payload: get_config command (smallest fixed)
            raw_payload = self.parser.encode_message("get_config")
            if raw_payload is None:
                raw_payload = self.parser.encode_message("identify",
                                                         offset=0, count=40)
            if raw_payload is None:
                raise RuntimeError("无法编码测试命令")
            payload_len = len(raw_payload)

            while total_sent < cfg.throughput_packet_count:
                if not self._running:
                    raise InterruptedError("测试被中断")

                batch = min(batch_size,
                            cfg.throughput_packet_count - total_sent)
                for _ in range(batch):
                    self.send_fn(raw_payload)
                total_sent += batch

                # Brief pause to let MCU breathe
                if not self.simulator_mode:
                    time.sleep(0.01)

                if total_sent % 500 == 0 or total_sent == batch:
                    elapsed = time.monotonic() - start_time
                    rate = 0.0
                    if elapsed > 0:
                        rate = (total_sent * payload_len) / elapsed
                    sample = BenchmarkSample(
                        label=f"pkt={total_sent}",
                        value=rate,
                        unit="bytes/s",
                        metadata={"packets": total_sent,
                                  "payload": payload_len},
                    )
                    result.samples.append(sample)
                    self._progress(
                        f"  已发送 {total_sent}/{cfg.throughput_packet_count} "
                        f"({rate/1024:.1f} KB/s)"
                    )

        except InterruptedError as e:
            result.success = False
            result.error = str(e)
        except Exception as e:
            result.success = False
            result.error = str(e)

        result.duration = time.monotonic() - start_time
        if not result.samples:
            result.success = False
            result.error = result.error or "No data collected"
        self._progress(f"吞吐量测试完成 ({result.duration:.1f}s)")
        return result

    def run_latency(self, cfg: Optional[BenchmarkConfig] = None
                    ) -> BenchmarkResult:
        """Roundtrip Latency Benchmark.

        Measures the time from sending a command to receiving its
        response. Uses get_config as a lightweight ping.
        """
        cfg = cfg or BenchmarkConfig(type=BenchmarkType.LATENCY)
        result = BenchmarkResult(type=BenchmarkType.LATENCY,
                                 config=cfg, success=True)
        start_time = time.monotonic()
        latencies: List[float] = []

        try:
            self._progress("命令延迟测试开始...")

            # Get a response-eliciting command
            ping_cmd = self.parser.encode_message("get_config")
            if ping_cmd is None:
                ping_cmd = self.parser.encode_message("identify",
                                                       offset=0, count=40)
            if ping_cmd is None:
                raise RuntimeError("无法编码 ping 命令")

            # Warmup
            self._drain_responses()
            for _ in range(5):
                self.send_fn(ping_cmd)
                time.sleep(0.02)
            self._wait_for_responses(min_count=1, timeout=0.5)
            self._drain_responses()

            for i in range(cfg.latency_sample_count):
                if not self._running:
                    raise InterruptedError("测试被中断")

                t0 = time.monotonic()
                self.send_fn(ping_cmd)
                self._wait_for_responses(min_count=1, timeout=2.0)
                t1 = time.monotonic()

                latency = (t1 - t0) * 1_000_000  # seconds → µs
                latencies.append(latency)

                sample = BenchmarkSample(
                    label=f"#{i+1}",
                    value=latency,
                    unit="µs",
                    metadata={},
                )
                result.samples.append(sample)

                if (i + 1) % 20 == 0:
                    avg = sum(latencies[-20:]) / len(latencies[-20:])
                    self._progress(
                        f"  #{i+1}/{cfg.latency_sample_count} "
                        f"延迟: {avg:.1f} µs"
                    )

        except InterruptedError:
            result.success = result.samples and True
            result.error = "测试被中断"
        except Exception as e:
            result.success = result.samples and True or False
            result.error = str(e)

        result.duration = time.monotonic() - start_time
        if not latencies:
            result.success = False
            result.error = result.error or "无有效数据"
        self._progress(
            f"延迟测试完成: "
            f"{result.summary()['avg']:.1f} µs avg "
            f"({result.duration:.1f}s)"
        )
        return result

    def run_clock(self, cfg: Optional[BenchmarkConfig] = None
                  ) -> BenchmarkResult:
        """Clock Accuracy Benchmark.

        Monitors the MCU clock over time to measure frequency stability
        and drift. Requires the MCU to respond to get_config or similar.
        """
        cfg = cfg or BenchmarkConfig(type=BenchmarkType.CLOCK)
        result = BenchmarkResult(type=BenchmarkType.CLOCK,
                                 config=cfg, success=True)
        start_time = time.monotonic()

        try:
            self._progress("时钟精度测试开始...")

            ping_cmd = self.parser.encode_message("get_config")
            if ping_cmd is None:
                ping_cmd = self.parser.encode_message("status")
            if ping_cmd is None:
                ping_cmd = self.parser.encode_message("identify",
                                                       offset=0, count=40)
            if ping_cmd is None:
                raise RuntimeError("无法编码时钟查询命令")

            sample_count = int(cfg.clock_duration / cfg.clock_sample_interval)
            last_sample_time = 0.0

            for i in range(sample_count):
                if not self._running:
                    raise InterruptedError("测试被中断")

                now = time.monotonic()
                elapsed = now - start_time

                self._drain_responses()
                self.send_fn(ping_cmd)
                self._wait_for_responses(min_count=1, timeout=1.0)

                sample_elapsed = time.monotonic() - now
                drift = sample_elapsed - cfg.clock_sample_interval

                sample = BenchmarkSample(
                    label=f"t={elapsed:.1f}s",
                    value=drift * 1_000_000,  # seconds → µs
                    unit="µs",
                    metadata={"elapsed": elapsed, "drift": drift},
                )
                result.samples.append(sample)

                if (i + 1) % 5 == 0:
                    self._progress(
                        f"  t={elapsed:.1f}s "
                        f"drift={drift*1_000_000:.1f} µs"
                    )

                # Wait for next sample interval
                next_time = (i + 1) * cfg.clock_sample_interval
                wait = next_time - (time.monotonic() - start_time)
                if wait > 0:
                    time.sleep(wait)

        except InterruptedError:
            result.success = True
            result.error = "测试被中断"
        except Exception as e:
            result.success = result.samples and True or False
            result.error = str(e)

        result.duration = time.monotonic() - start_time
        self._progress(f"时钟测试完成 ({result.duration:.1f}s)")
        return result

    def run_full(self, cfg: Optional[BenchmarkConfig] = None
                 ) -> Dict[str, BenchmarkResult]:
        """Run all benchmarks and return combined results."""
        results: Dict[str, BenchmarkResult] = {}

        self._progress("╔══════════════════════════════════════╗")
        self._progress("║     完整基准测试开始                 ║")
        self._progress("╚══════════════════════════════════════╝")

        # 1. Latency
        lat_cfg = BenchmarkConfig(
            type=BenchmarkType.LATENCY,
            latency_sample_count=(cfg.latency_sample_count
                                  if cfg else 100),
        )
        self._progress("\n--- 命令延迟测试 ---")
        results["latency"] = self.run_latency(lat_cfg)

        # 2. Throughput
        tp_cfg = BenchmarkConfig(
            type=BenchmarkType.THROUGHPUT,
            throughput_packet_count=(cfg.throughput_packet_count
                                     if cfg else 2000),
        )
        self._progress("\n--- 串口吞吐量测试 ---")
        results["throughput"] = self.run_throughput(tp_cfg)

        # 3. Step rate (if applicable, skip for virtual MCU)
        if not self.simulator_mode:
            sr_cfg = BenchmarkConfig(
                type=BenchmarkType.STEP_RATE,
                stepper_oid=(cfg.stepper_oid if cfg else 0),
            )
            self._progress("\n--- 步进速率测试 ---")
            results["step_rate"] = self.run_step_rate(sr_cfg)
        else:
            self._progress("\n--- 步进速率测试 (跳过 - 虚拟MCU) ---")

        # 4. Clock accuracy
        clk_cfg = BenchmarkConfig(
            type=BenchmarkType.CLOCK,
            clock_duration=max(5.0, (cfg.clock_duration / 2)
                               if cfg else 5.0),
        )
        self._progress("\n--- 时钟精度测试 ---")
        results["clock"] = self.run_clock(clk_cfg)

        self._progress("\n完整基准测试完成!")
        return results


def format_result_summary(results: Dict[str, BenchmarkResult]) -> str:
    """Format benchmark results into a compact table."""
    lines = [
        "+--------------------------------------------------+",
        "|              Kalico MCU Benchmark Report          |",
        "+--------------------------------------------------+",
    ]
    all_ok = True
    for name, r in results.items():
        s = r.summary()
        label = {
            "latency": "Latency",
            "throughput": "Throughput",
            "step_rate": "Step Rate",
            "clock": "Clock",
        }.get(name, name)
        status = "PASS" if s["success"] else "FAIL"
        if not s["success"]:
            all_ok = False
        row = f"|  {status:<5s} {label:<12s} "
        if s["success"]:
            if name == "latency":
                row += f"avg={s['avg']:>8.1f} us   max={s['max']:>8.1f} us"
            elif name == "throughput":
                row += f"avg={s['avg']/1024:>8.1f} KB/s  max={s['max']/1024:>8.1f} KB/s"
            elif name == "step_rate":
                row += f"max={s['max']:>10.0f} steps/s  avg={s['avg']:>10.0f} steps/s"
            elif name == "clock":
                row += f"drift={s['avg']:>+8.1f} us    stddev={s['stddev']:>8.1f} us"
        else:
            row += f"FAILED: {r.error or 'No data'}"
        row += " " * max(1, 48 - len(row)) + "|"
        lines.append(row)

    status_line = "ALL PASSED" if all_ok else "SOME FAILED"
    lines.append(f"+--------------------------------------------------+")
    lines.append(f"|  Overall: {status_line:<37s}|")
    lines.append(f"+--------------------------------------------------+")
    return "\n".join(lines)
