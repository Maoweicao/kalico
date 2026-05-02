#!/usr/bin/env python3
"""
configure_autoconf.py — TUI 配置工具 for generic_arduino autoconf.h
=============================================================================
终端可视化界面，用于查看和编辑 autoconf.h 中的编译配置选项。

用法:
    pip install -r tools/requirements.txt
    python tools/configure_autoconf.py
    python tools/configure_autoconf.py 路径/to/autoconf.h

快捷键:
    ↑/↓         导航选项
    Tab         切换面板（分类列表 ↔ 选项列表）
    Enter       编辑选中的配置值
    /           搜索配置项
    s           保存修改
    q / Esc     退出
    ?           显示帮助
"""

from __future__ import annotations

import re
import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Internationalisation (i18n) — loaded from tools/i18n/   ← EXTERNAL FILES  ←
# ---------------------------------------------------------------------------
#
# Language files live in tools/i18n/en.py and tools/i18n/zh.py.
# To add a language, copy en.py → yourlang.py, translate the strings,
# then add yourlang to LANGUAGE_CODES in tools/i18n/__init__.py.

# Ensure the tools/ directory is on sys.path so "import i18n" works
_tools_dir = Path(__file__).resolve().parent
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from i18n import _, get_option_description, set_language, get_language, toggle_language


# ---------------------------------------------------------------------------
# Preset configurations (predefined board profiles)
# ---------------------------------------------------------------------------

PRESETS = {
    "Arduino Uno": {
        "name": "Arduino Uno",
        "name_zh": "Arduino Uno",
        "desc": "ATmega328P @ 16 MHz, 2 KB RAM",
        "desc_zh": "ATmega328P @ 16 MHz，2 KB RAM",
        "values": {
            "CONFIG_CLOCK_FREQ": "16000000UL",
            "CONFIG_SERIAL_BAUD": "250000",
            "CONFIG_MCU_SERIAL_TYPE": "0",
            "CONFIG_MCU_SERIAL_HW_PORT": "0",
            "CONFIG_MCU_SERIAL_SW_RX": "10",
            "CONFIG_MCU_SERIAL_SW_TX": "11",
            "CONFIG_SERIAL_BAUD_U2X": "1",
            "CONFIG_DEBUG_SERIAL_PORT": "0",
            "CONFIG_DEBUG_SERIAL_BAUD": "250000",
            "CONFIG_AVR_STACK_SIZE": "128",
            "CONFIG_WANT_STEPPER": "0",
            "CONFIG_HAVE_GPIO": "1",
            "CONFIG_HAVE_GPIO_ADC": "1",
            "CONFIG_HAVE_GPIO_SPI": "0",
            "CONFIG_HAVE_GPIO_I2C": "0",
            "CONFIG_HAVE_GPIO_HARD_PWM": "1",
            "CONFIG_WANT_GPIO_BITBANGING": "1",
            "CONFIG_WANT_SOFTWARE_SPI": "0",
            "CONFIG_WANT_SOFTWARE_I2C": "0",
            "CONFIG_WANT_ADC": "0",
            "CONFIG_WANT_SPI": "0",
            "CONFIG_WANT_I2C": "0",
            "CONFIG_WANT_HARD_PWM": "0",
            "CONFIG_WANT_BUTTONS": "0",
            "CONFIG_WANT_STEPPER": "0",
            "CONFIG_WANT_ENDSTOPS": "0",
            "CONFIG_INLINE_STEPPER_HACK": "0",
            "CONFIG_HAVE_BOOTLOADER_REQUEST": "0",
            "CONFIG_MCU_NAME": '"arduino_uno"',
        },
    },
    "Arduino Mega": {
        "name": "Arduino Mega",
        "name_zh": "Arduino Mega",
        "desc": "ATmega2560 @ 16 MHz, 8 KB RAM",
        "desc_zh": "ATmega2560 @ 16 MHz，8 KB RAM",
        "values": {
            "CONFIG_CLOCK_FREQ": "16000000UL",
            "CONFIG_SERIAL_BAUD": "250000",
            "CONFIG_MCU_SERIAL_TYPE": "0",
            "CONFIG_MCU_SERIAL_HW_PORT": "1",
            "CONFIG_MCU_SERIAL_SW_RX": "10",
            "CONFIG_MCU_SERIAL_SW_TX": "11",
            "CONFIG_SERIAL_BAUD_U2X": "0",
            "CONFIG_DEBUG_SERIAL_PORT": "0",
            "CONFIG_DEBUG_SERIAL_BAUD": "115200",
            "CONFIG_AVR_STACK_SIZE": "256",
            "CONFIG_WANT_STEPPER": "0",
            "CONFIG_HAVE_GPIO": "1",
            "CONFIG_HAVE_GPIO_ADC": "1",
            "CONFIG_HAVE_GPIO_SPI": "0",
            "CONFIG_HAVE_GPIO_I2C": "0",
            "CONFIG_HAVE_GPIO_HARD_PWM": "1",
            "CONFIG_WANT_GPIO_BITBANGING": "1",
            "CONFIG_WANT_SOFTWARE_SPI": "0",
            "CONFIG_WANT_SOFTWARE_I2C": "0",
            "CONFIG_WANT_ADC": "0",
            "CONFIG_WANT_SPI": "0",
            "CONFIG_WANT_I2C": "0",
            "CONFIG_WANT_HARD_PWM": "0",
            "CONFIG_WANT_BUTTONS": "0",
            "CONFIG_WANT_STEPPER": "0",
            "CONFIG_WANT_ENDSTOPS": "0",
            "CONFIG_INLINE_STEPPER_HACK": "0",
            "CONFIG_HAVE_BOOTLOADER_REQUEST": "0",
            "CONFIG_MCU_NAME": '"arduino_mega"',
        },
    },
    "Arduino Due": {
        "name": "Arduino Due",
        "name_zh": "Arduino Due",
        "desc": "ATSAM3X8E @ 84 MHz, 96 KB RAM",
        "desc_zh": "ATSAM3X8E @ 84 MHz，96 KB RAM",
        "values": {
            "CONFIG_CLOCK_FREQ": "84000000UL",
            "CONFIG_SERIAL_BAUD": "250000",
            "CONFIG_MCU_SERIAL_TYPE": "0",
            "CONFIG_MCU_SERIAL_HW_PORT": "1",
            "CONFIG_MCU_SERIAL_SW_RX": "10",
            "CONFIG_MCU_SERIAL_SW_TX": "11",
            "CONFIG_SERIAL_BAUD_U2X": "0",
            "CONFIG_DEBUG_SERIAL_PORT": "1",
            "CONFIG_DEBUG_SERIAL_BAUD": "115200",
            "CONFIG_AVR_STACK_SIZE": "4096",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_HAVE_GPIO": "1",
            "CONFIG_HAVE_GPIO_ADC": "1",
            "CONFIG_HAVE_GPIO_SPI": "1",
            "CONFIG_HAVE_GPIO_I2C": "1",
            "CONFIG_HAVE_GPIO_HARD_PWM": "1",
            "CONFIG_WANT_GPIO_BITBANGING": "1",
            "CONFIG_WANT_SOFTWARE_SPI": "0",
            "CONFIG_WANT_SOFTWARE_I2C": "0",
            "CONFIG_WANT_ADC": "1",
            "CONFIG_WANT_SPI": "1",
            "CONFIG_WANT_I2C": "1",
            "CONFIG_WANT_HARD_PWM": "1",
            "CONFIG_WANT_BUTTONS": "1",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_WANT_ENDSTOPS": "1",
            "CONFIG_INLINE_STEPPER_HACK": "0",
            "CONFIG_HAVE_BOOTLOADER_REQUEST": "1",
            "CONFIG_MCU_NAME": '"arduino_due"',
        },
    },
    "Teensy 4.0": {
        "name": "Teensy 4.0",
        "name_zh": "Teensy 4.0",
        "desc": "IMXRT1062 @ 600 MHz, 2 MB RAM",
        "desc_zh": "IMXRT1062 @ 600 MHz，2 MB RAM",
        "values": {
            "CONFIG_CLOCK_FREQ": "600000000UL",
            "CONFIG_SERIAL_BAUD": "250000",
            "CONFIG_MCU_SERIAL_TYPE": "0",
            "CONFIG_MCU_SERIAL_HW_PORT": "1",
            "CONFIG_MCU_SERIAL_SW_RX": "10",
            "CONFIG_MCU_SERIAL_SW_TX": "11",
            "CONFIG_SERIAL_BAUD_U2X": "0",
            "CONFIG_DEBUG_SERIAL_PORT": "1",
            "CONFIG_DEBUG_SERIAL_BAUD": "115200",
            "CONFIG_AVR_STACK_SIZE": "65536",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_HAVE_GPIO": "1",
            "CONFIG_HAVE_GPIO_ADC": "1",
            "CONFIG_HAVE_GPIO_SPI": "1",
            "CONFIG_HAVE_GPIO_I2C": "1",
            "CONFIG_HAVE_GPIO_HARD_PWM": "1",
            "CONFIG_WANT_GPIO_BITBANGING": "1",
            "CONFIG_WANT_SOFTWARE_SPI": "0",
            "CONFIG_WANT_SOFTWARE_I2C": "0",
            "CONFIG_WANT_ADC": "1",
            "CONFIG_WANT_SPI": "1",
            "CONFIG_WANT_I2C": "1",
            "CONFIG_WANT_HARD_PWM": "1",
            "CONFIG_WANT_BUTTONS": "1",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_WANT_ENDSTOPS": "1",
            "CONFIG_INLINE_STEPPER_HACK": "1",
            "CONFIG_HAVE_BOOTLOADER_REQUEST": "1",
            "CONFIG_MCU_NAME": '"teensy40"',
        },
    },
    "ESP32 DevKit": {
        "name": "ESP32 DevKit",
        "name_zh": "ESP32 DevKit",
        "desc": "Xtensa LX6 @ 240 MHz, 512 KB RAM",
        "desc_zh": "Xtensa LX6 @ 240 MHz，512 KB RAM",
        "values": {
            "CONFIG_CLOCK_FREQ": "240000000UL",
            "CONFIG_SERIAL_BAUD": "250000",
            "CONFIG_MCU_SERIAL_TYPE": "0",
            "CONFIG_MCU_SERIAL_HW_PORT": "1",
            "CONFIG_MCU_SERIAL_SW_RX": "16",
            "CONFIG_MCU_SERIAL_SW_TX": "17",
            "CONFIG_SERIAL_BAUD_U2X": "0",
            "CONFIG_DEBUG_SERIAL_PORT": "0",
            "CONFIG_DEBUG_SERIAL_BAUD": "115200",
            "CONFIG_AVR_STACK_SIZE": "32768",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_HAVE_GPIO": "1",
            "CONFIG_HAVE_GPIO_ADC": "1",
            "CONFIG_HAVE_GPIO_SPI": "1",
            "CONFIG_HAVE_GPIO_I2C": "1",
            "CONFIG_HAVE_GPIO_HARD_PWM": "1",
            "CONFIG_WANT_GPIO_BITBANGING": "1",
            "CONFIG_WANT_SOFTWARE_SPI": "0",
            "CONFIG_WANT_SOFTWARE_I2C": "0",
            "CONFIG_WANT_ADC": "1",
            "CONFIG_WANT_SPI": "1",
            "CONFIG_WANT_I2C": "1",
            "CONFIG_WANT_HARD_PWM": "1",
            "CONFIG_WANT_BUTTONS": "1",
            "CONFIG_WANT_STEPPER": "1",
            "CONFIG_WANT_ENDSTOPS": "1",
            "CONFIG_INLINE_STEPPER_HACK": "0",
            "CONFIG_HAVE_BOOTLOADER_REQUEST": "1",
            "CONFIG_MCU_NAME": '"esp32"',
        },
    },
}

# Smart editor preset values for common options
# Options listed here get a RadioSet of common values + a custom input field
PRESET_VALUES = {
    "CONFIG_CLOCK_FREQ": {
        "label": "Clock Frequency (Hz)",
        "label_zh": "时钟频率 (Hz)",
        "options": [
            ("16000000UL",     "16 MHz  (Uno / Mega)"),
            ("84000000UL",     "84 MHz  (Due)"),
            ("240000000UL",    "240 MHz (ESP32)"),
            ("600000000UL",    "600 MHz (Teensy 4.0)"),
        ],
    },
    "CONFIG_SERIAL_BAUD": {
        "label": "Serial Baud Rate",
        "label_zh": "串口波特率",
        "options": [
            ("115200",  "115200"),
            ("250000",  "250000 (Klipper default)"),
            ("500000",  "500000"),
            ("1000000", "1000000 (1M)"),
        ],
    },
    "CONFIG_AVR_STACK_SIZE": {
        "label": "Stack / Memory Pool Size (bytes)",
        "label_zh": "栈 / 内存池大小 (字节)",
        "options": [
            ("128",    "128   (Uno, minimal)"),
            ("256",    "256   (Mega, default)"),
            ("1024",   "1024  (ARM small)"),
            ("4096",   "4096  (ARM medium)"),
            ("32768",  "32768 (ESP32)"),
            ("65536",  "65536 (Teensy 4.0)"),
        ],
    },
    "CONFIG_SERIAL_BAUD_U2X": {
        "label": "AVR U2X (Double Speed)",
        "label_zh": "AVR U2X (双倍速)",
        "options": [
            ("0", "Disabled (Mega / ARM / ESP32)"),
            ("1", "Enabled (Uno, better baud accuracy)"),
        ],
    },
    "CONFIG_MCU_SERIAL_TYPE": {
        "label": "MCU Serial Type",
        "label_zh": "MCU 串口类型",
        "options": [
            ("0", "Hardware UART (fast, reliable)"),
            ("1", "Software Serial (bit-bang GPIO, flexible)"),
        ],
    },
    "CONFIG_MCU_SERIAL_HW_PORT": {
        "label": "Hardware UART Port",
        "label_zh": "硬件 UART 端口",
        "options": [
            ("0", "Serial  (Uno/Nano, pins 0/1)"),
            ("1", "Serial1 (Mega 18/19, Due, Teensy, ESP32)"),
            ("2", "Serial2 (Mega 16/17)"),
            ("3", "Serial3 (Mega 14/15)"),
        ],
    },
    "CONFIG_MCU_SERIAL_SW_RX": {
        "label": "Software Serial RX Pin",
        "label_zh": "软件串口 RX 引脚",
        "options": [
            ("2",  "Pin 2"),
            ("3",  "Pin 3"),
            ("10", "Pin 10 (default)"),
            ("11", "Pin 11"),
            ("12", "Pin 12"),
        ],
    },
    "CONFIG_MCU_SERIAL_SW_TX": {
        "label": "Software Serial TX Pin",
        "label_zh": "软件串口 TX 引脚",
        "options": [
            ("2",  "Pin 2"),
            ("3",  "Pin 3"),
            ("10", "Pin 10"),
            ("11", "Pin 11 (default)"),
            ("12", "Pin 12"),
        ],
    },
    "CONFIG_DEBUG_SERIAL_PORT": {
        "label": "Debug Serial Port",
        "label_zh": "调试串口端口",
        "options": [
            ("0", "Serial (USB, most boards)"),
            ("1", "SerialUSB (native USB: Due/Teensy)"),
            ("2", "Disabled (no output)"),
        ],
    },
    "CONFIG_DEBUG_SERIAL_BAUD": {
        "label": "Debug Serial Baud Rate",
        "label_zh": "调试串口波特率",
        "options": [
            ("9600",   "9600"),
            ("115200", "115200 (default)"),
            ("250000", "250000"),
            ("500000", "500000"),
            ("1000000","1000000 (1M)"),
        ],
    },
    "CONFIG_HAVE_GPIO": {
        "label": "GPIO Support",
        "label_zh": "GPIO 支持",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_HAVE_GPIO_ADC": {
        "label": "Analog Input (ADC)",
        "label_zh": "模拟输入 (ADC)",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_HAVE_GPIO_SPI": {
        "label": "Hardware SPI",
        "label_zh": "硬件 SPI",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_HAVE_GPIO_I2C": {
        "label": "Hardware I2C",
        "label_zh": "硬件 I2C",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_HAVE_GPIO_HARD_PWM": {
        "label": "Hardware PWM",
        "label_zh": "硬件 PWM",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_STEPPER": {
        "label": "Stepper Motor Control",
        "label_zh": "步进电机控制",
        "options": [("0", "Disabled (save resources)"), ("1", "Enabled")],
    },
    "CONFIG_WANT_ENDSTOPS": {
        "label": "Endstop / Limit Switches",
        "label_zh": "限位开关",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_ADC": {
        "label": "ADC Sensor Reading",
        "label_zh": "ADC 传感器读取",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_SPI": {
        "label": "SPI Protocol",
        "label_zh": "SPI 协议",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_I2C": {
        "label": "I2C Protocol",
        "label_zh": "I2C 协议",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_HARD_PWM": {
        "label": "Hardware PWM Output",
        "label_zh": "硬件 PWM 输出",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_BUTTONS": {
        "label": "Button / Switch Input",
        "label_zh": "按钮/开关输入",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_GPIO_BITBANGING": {
        "label": "GPIO Bit-banging",
        "label_zh": "GPIO 位冲模式",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_SOFTWARE_SPI": {
        "label": "Software (Bit-bang) SPI",
        "label_zh": "软件 SPI (位冲)",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_WANT_SOFTWARE_I2C": {
        "label": "Software (Bit-bang) I2C",
        "label_zh": "软件 I2C (位冲)",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_HAVE_BOOTLOADER_REQUEST": {
        "label": "Bootloader Request",
        "label_zh": "引导加载请求",
        "options": [("0", "Disabled"), ("1", "Enabled")],
    },
    "CONFIG_INLINE_STEPPER_HACK": {
        "label": "Inline Stepper Dispatch",
        "label_zh": "内联步进调度",
        "options": [("0", "Disabled (generic)"), ("1", "Enabled (optimized)")],
    },
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ConfigOption:
    """单个配置选项的数据模型"""
    name: str           # 宏名称 (如 CONFIG_CLOCK_FREQ)
    value: str          # 当前值 (如 "16000000UL")
    description: str    # 描述文本 (来自上方注释)
    category: str       # 分类 (如 "Clock")
    line_number: int    # 在文件中的行号 (1-based)
    raw_text: str       # 整行原文
    is_conditioned: bool = False  # 是否在 #ifdef/#if 条件中
    condition_line: int = -1      # 条件行号


# ---------------------------------------------------------------------------
# Parser — 解析 autoconf.h
# ---------------------------------------------------------------------------

SECTION_RE = re.compile(r'^//\s*-{4,}\s*(.+?)\s*-{4,}')
COMMENT_RE = re.compile(r'^//\s*(.+)$')
DEFINE_RE = re.compile(r'^#define\s+(\w+)(?:\s+(.+))?')
IFNDEF_RE = re.compile(r'^#ifndef\s+(\w+)')
IFDEF_RE = re.compile(r'^#ifdef\s+(\w+)')
IF_RE = re.compile(r'^#if\s+(.+)$')
ELSE_RE = re.compile(r'^#else')
ENDIF_RE = re.compile(r'^#endif')

def parse_autoconf(path: Path) -> Tuple[List[ConfigOption], List[str]]:
    """解析 autoconf.h，返回 (选项列表, 原始行列表)"""
    lines = path.read_text(encoding="utf-8").splitlines()
    options: List[ConfigOption] = []
    current_category = "General"
    pending_desc: List[str] = []
    condition_stack: List[Tuple[str, int]] = []  # [(condition_text, line_number)]

    for i, line in enumerate(lines):
        lineno = i + 1
        stripped = line.strip()

        # 分类标题
        m = SECTION_RE.match(stripped)
        if m:
            current_category = m.group(1).strip()
            pending_desc.clear()
            continue

        # 普通注释 → 累积为描述
        m = COMMENT_RE.match(stripped)
        if m:
            pending_desc.append(m.group(1).strip())
            continue

        # #ifdef — 保存当前描述栈
        m = IFDEF_RE.match(stripped)
        if m:
            guard_name = m.group(1)
            condition_stack.append((f"#ifdef {guard_name}", lineno, list(pending_desc)))
            pending_desc.clear()
            continue

        # #ifndef — 保存当前描述栈, 跳过 include guard
        m = IFNDEF_RE.match(stripped)
        if m:
            guard_name = m.group(1)
            # 跳过 include guard 的条件块（如 #ifndef __AUTOCONF_H）
            if guard_name.startswith("__"):
                pending_desc.clear()
                continue
            condition_stack.append((f"#ifndef {guard_name}", lineno, list(pending_desc)))
            pending_desc.clear()
            continue

        # #if — 保存当前描述栈
        m = IF_RE.match(stripped)
        if m:
            condition_stack.append((m.group(1).strip(), lineno, list(pending_desc)))
            pending_desc.clear()
            continue

        # #else — 保留进入 #if 前保存的描述, 但清除行内注释
        if ELSE_RE.match(stripped):
            if condition_stack:
                prev_cond, prev_lineno, prev_desc = condition_stack[-1]
                # 保留原始描述（#else 分支复用同一段注释）
                condition_stack[-1] = (f"!({prev_cond})", prev_lineno, prev_desc)
            pending_desc.clear()
            continue

        # #endif — 弹出条件栈
        if ENDIF_RE.match(stripped):
            if condition_stack:
                condition_stack.pop()
            continue

        # #define
        m = DEFINE_RE.match(stripped)
        if m:
            name = m.group(1)
            value = (m.group(2) or "1").strip()

            # 跳过 include guard (如 __AUTOCONF_H, __INCLUDE_GUARD__)
            if name.startswith("__") and value == "1":
                pending_desc.clear()
                continue

            # 取描述: 优先使用 #define 前的注释, 否则从条件栈恢复
            desc = " ".join(pending_desc).strip() if pending_desc else ""
            if not desc and condition_stack:
                # 尝试从条件栈顶层获取进入条件块前保存的描述
                saved = condition_stack[-1][2]
                if saved:
                    desc = " ".join(saved).strip()
                    # 不消费描述: #ifdef/#else 多个分支共享同一段注释

            is_cond = bool(condition_stack)
            cond_line = condition_stack[-1][1] if condition_stack else -1

            options.append(ConfigOption(
                name=name,
                value=value,
                description=desc,
                category=current_category,
                line_number=lineno,
                raw_text=line,
                is_conditioned=is_cond,
                condition_line=cond_line,
            ))
            pending_desc.clear()
            continue

        # 空行或非匹配行 — 不清空 pending_desc（允许跨空行关联注释）
        # 只清空在连续空行 + 非注释内容时
        if stripped == "":
            continue
        # 非注释、非 # 开头的行才清空描述缓存
        if not stripped.startswith("#"):
            pending_desc.clear()

    return options, lines


# ---------------------------------------------------------------------------
# 写入回文件
# ---------------------------------------------------------------------------

def apply_changes(lines: List[str], option: ConfigOption, new_value: str) -> List[str]:
    """将修改应用到文件行列表"""
    idx = option.line_number - 1
    old_line = lines[idx]
    # 保持缩进格式
    indent = re.match(r'^(\s*)', old_line).group(1)
    lines[idx] = f"{indent}#define {option.name}       {new_value}"
    option.value = new_value
    option.raw_text = lines[idx]
    return lines


# ---------------------------------------------------------------------------
# Textual TUI App
# ---------------------------------------------------------------------------

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.widgets import (
        Header, Footer, Static, ListView, ListItem, Label, Input,
        Button, RichLog, ContentSwitcher, RadioSet, RadioButton
    )
    from textual.screen import Screen, ModalScreen
    from textual.binding import Binding
    from textual.widget import Widget
    from textual.reactive import reactive
    from textual.message import Message
    from rich.text import Text
    from rich.table import Table
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.layout import Layout
    from rich.style import Style
    TEXTUAL_AVAILABLE = True
except ImportError:
    TEXTUAL_AVAILABLE = False


# ── Help screen ──────────────────────────────────────────────────────────

class HelpScreen(ModalScreen):
    """帮助信息弹窗"""

    def compose(self) -> ComposeResult:
        yield Static(
            "\n"
            f"  [bold yellow]{_('cfg.help_title')}[/]\n"
            "  ─────────────────────────────────────────\n"
            "  \n"
            f"  [bold]{_('cfg.help_keys')}[/]\n"
            f"  [dim]  \u2191/\u2193[/]       {_('cfg.help_nav')}\n"
            f"  [dim]  Tab[/]        {_('cfg.help_tab')}\n"
            f"  [dim]  Enter[/]      {_('cfg.help_enter')}\n"
            f"  [dim]  /[/]          {_('cfg.help_search')}\n"
            f"  [dim]  s[/]          {_('cfg.help_save')}\n"
            f"  [dim]  P[/]          {_('cfg.help_presets')}\n"
            f"  [dim]  L[/]          {_('cfg.help_lang')}\n"
            f"  [dim]  q / Esc[/]    {_('cfg.help_quit')}\n"
            f"  [dim]  ?[/]          {_('cfg.help_help')}\n"
            "  \n"
            f"  [bold]{_('cfg.help_panels')}[/]\n"
            f"  [dim]  {_('cfg.help_left')}[/]\n"
            f"  [dim]  {_('cfg.help_right')}[/]\n"
            f"  [dim]  {_('cfg.help_bottom')}[/]\n"
            "  \n"
            f"  [bold]{_('cfg.help_edit_mode')}[/]\n"
            f"  {_('cfg.help_edit_desc')}\n"
            "  \n"
            f"  {_('cfg.help_dismiss')}"
        )

    def on_key(self, event):
        self.dismiss()


# ── Preset Screen ────────────────────────────────────────────────────────

class PresetScreen(ModalScreen):
    """预制配置选择弹窗"""

    def compose(self) -> ComposeResult:
        rows = []
        for key, preset in PRESETS.items():
            name = preset["name"]
            desc = preset["desc"]
            if _current_language == "zh":
                name = preset.get("name_zh", name)
                desc = preset.get("desc_zh", desc)
            rows.append(f"  [bold cyan]{name:<20}[/] [dim]{desc}[/]")
        rows_str = "\n".join(rows)

        yield Static(
            "\n"
            f"  [bold yellow]{_('cfg.presets_title')}[/]\n"
            "  ─────────────────────────────────────────\n"
            "  \n"
            f"{rows_str}\n"
            "  \n"
            f"  {_('cfg.presets_prompt')}"
        )

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)
        elif event.key.isdigit():
            idx = int(event.key) - 1
            keys = list(PRESETS.keys())
            if 0 <= idx < len(keys):
                self.dismiss(keys[idx])

    def on_click(self, event) -> None:
        self.dismiss(None)


# ── Smart Edit Screen ────────────────────────────────────────────────────

class SmartEditScreen(ModalScreen):
    """智能编辑弹窗：RadioSet + 自定义输入框"""

    def __init__(self, option: ConfigOption, preset: dict, **kwargs):
        super().__init__(**kwargs)
        self.option = option
        self.preset = preset
        self._selected_value = option.value

    def compose(self) -> ComposeResult:
        desc = get_option_description(self.option.name, self.option.description)
        label = (self.preset.get("label_zh") if _current_language == "zh"
                 else self.preset.get("label"))

        widgets = [
            Static(f"\n  [bold yellow]{_('cfg.edit_title')}[/]  [cyan]{self.option.name}[/]", id="edit-title"),
            Static(f"  [dim]{_('cfg.edit_desc')}[/]   {desc or _('cfg.edit_no_desc')}", id="edit-desc"),
            Static(f"  [bold]{label or ''}[/]", id="smart-label"),
            Static("", id="smart-spacer"),
        ]

        radio_buttons = []
        for value, hint in self.preset["options"]:
            selected = (value == self.option.value)
            radio_buttons.append(RadioButton(hint, value=value, initial_state=selected))
        radio_buttons.append(RadioButton(
            "Custom..." if _current_language == "en" else "自定义...",
            value="__custom__",
            initial_state=not any(v == self.option.value for v, _ in self.preset["options"]),
        ))

        self.radio_set = RadioSet(*radio_buttons, id="smart-radioset")
        widgets.append(self.radio_set)

        widgets.append(Static("", id="custom-spacer"))
        self.custom_input = Input(
            value=self.option.value,
            placeholder=_('cfg.edit_placeholder'),
            id="smart-custom-input",
        )
        is_custom = not any(v == self.option.value for v, _ in self.preset["options"])
        self.custom_input.visible = is_custom
        self.custom_input.disabled = not is_custom
        widgets.append(self.custom_input)

        widgets.append(Horizontal(
            Button(_("cfg.btn_ok"), variant="primary", id="btn-ok"),
            Button(_("cfg.btn_cancel"), variant="default", id="btn-cancel"),
            classes="edit-buttons",
        ))
        widgets.append(Static("", id="smart-bottom"))

        yield Vertical(*widgets, id="smart-dialog")

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        value = event.new
        self._selected_value = value
        if value == "__custom__":
            self.custom_input.visible = True
            self.custom_input.disabled = False
            self.custom_input.focus()
        else:
            self.custom_input.visible = False
            self.custom_input.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ok":
            value = self._selected_value
            if value == "__custom__":
                value = self.custom_input.value.strip() or self.option.value
            self.dismiss(value)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "smart-custom-input":
            self.dismiss(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ── Simple Edit Screen (plain text, fallback) ────────────────────────────

class EditScreen(ModalScreen):
    """编辑配置值的弹窗"""

    def __init__(self, option: ConfigOption, **kwargs):
        super().__init__(**kwargs)
        self.option = option

    def compose(self) -> ComposeResult:
        desc = get_option_description(self.option.name, self.option.description)
        yield Vertical(
            Static(f"\n  [bold yellow]{_('cfg.edit_title')}[/]  [cyan]{self.option.name}[/]\n", id="edit-title"),
            Static(f"  [dim]{_('cfg.edit_current')}[/] {self.option.value}", id="edit-current"),
            Static(f"  [dim]{_('cfg.edit_desc')}[/]   {desc or _('cfg.edit_no_desc')}", id="edit-desc"),
            Static("", id="edit-spacer"),
            Input(value=self.option.value, placeholder=_('cfg.edit_placeholder'), id="edit-input"),
            Horizontal(
                Button(_("cfg.btn_ok"), variant="primary", id="btn-ok"),
                Button(_("cfg.btn_cancel"), variant="default", id="btn-cancel"),
                classes="edit-buttons",
            ),
            id="edit-dialog",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-ok":
            input_widget = self.query_one("#edit-input", Input)
            self.dismiss(input_widget.value)
        else:
            self.dismiss(None)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.dismiss(None)


# ── Category List Item ───────────────────────────────────────────────────

class CategoryItem(ListItem):
    """分类列表项"""

    def __init__(self, name: str, count: int, **kwargs):
        super().__init__(**kwargs)
        self.cat_name = name
        self.cat_count = count

    def compose(self) -> ComposeResult:
        # 获取翻译后的分类名
        translated = _(f"cat.{self.cat_name}")
        yield Static(f"[bold]{translated}[/]  [dim]({self.cat_count})[/]")


# ── Option List Item ─────────────────────────────────────────────────────

class OptionItem(ListItem):
    """配置选项列表项"""

    def __init__(self, option: ConfigOption, **kwargs):
        super().__init__(**kwargs)
        self.option = option

    def compose(self) -> ComposeResult:
        # 值着色
        val = self.option.value
        val_style = "green" if val not in ("0", "0UL", "0ull") else "dim"
        # 条件编译标记
        cond_mark = _("cfg.cond_mark") if self.option.is_conditioned else ""
        desc = get_option_description(self.option.name, self.option.description)
        yield Static(
            f"  [cyan]{self.option.name:<36}[/] [bold {val_style}]{val:<20}[/]"
            f"{cond_mark}\n"
            f"  [dim]{desc}[/]"
        )


# ── Main App ─────────────────────────────────────────────────────────────

class ConfigApp(App):
    """generic_arduino autoconf.h 配置工具"""

    TITLE = _("cfg.title")
    language = reactive("en")  # en / zh
    CSS = """
    Screen {
        background: $surface;
    }

    #main-container {
        height: 100%;
    }

    #category-panel {
        width: 30;
        min-width: 24;
        border: solid $primary;
        border-title-color: $text;
        background: $panel;
        margin: 0 1 0 0;
    }

    #category-panel > Static {
        padding: 0 1;
        text-style: bold;
        background: $accent;
        color: $text;
    }

    #category-list {
        height: 1fr;
    }

    #option-panel {
        width: 1fr;
        border: solid $primary;
        border-title-color: $text;
        background: $panel;
    }

    #option-panel > Static {
        padding: 0 1;
        text-style: bold;
        background: $accent;
        color: $text;
    }

    #option-list {
        height: 1fr;
    }

    #status-bar {
        height: 1;
        background: $boost;
        padding: 0 1;
        content-align: left middle;
    }

    #search-container {
        height: 3;
        padding: 0 1;
        background: $surface;
        border: solid $secondary;
        visibility: hidden;
    }

    ListView {
        border: none;
    }

    ListItem {
        padding: 0 0;
    }

    #edit-dialog {
        width: 60;
        height: auto;
        min-height: 12;
        border: thick $warning;
        background: $surface;
        padding: 1 2;
        margin: 4 8;
    }

    #edit-title {
        text-style: bold;
        padding-bottom: 0;
    }

    #edit-current {
        padding: 0 0;
    }

    #edit-desc {
        padding: 0 0;
    }

    #edit-input {
        margin: 1 0;
    }

    .edit-buttons {
        align: center middle;
        height: 3;
    }

    .edit-buttons Button {
        margin: 0 1;
    }

    /* Smart dialog */
    #smart-dialog {
        width: 66;
        height: auto;
        min-height: 16;
        border: thick $success;
        background: $surface;
        padding: 1 2;
        margin: 2 6;
    }

    #smart-dialog > Static {
        padding: 0 0;
    }

    #smart-radioset {
        margin: 1 0;
        height: auto;
        max-height: 16;
    }

    #smart-radioset RadioButton {
        padding: 0 1;
    }

    #smart-custom-input {
        margin: 0 0 1 0;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("s", "save", "Save", show=True),
        Binding("l", "toggle_language", "Lang", show=True),
        Binding("slash", "search", "Search", show=True),
        Binding("p", "apply_preset", "Presets", show=True),
        Binding("question_mark", "show_help", "Help", show=True),
        Binding("tab", "focus_next_pane", "Switch Panel", show=True, priority=True),
    ]

    def __init__(self, file_path: Path):
        super().__init__()
        self.file_path = file_path
        self.options, self.lines = parse_autoconf(file_path)
        self.modified = False
        global _current_language
        _current_language = "en"

        # 构建分类索引
        self.categories: List[Tuple[str, List[ConfigOption]]] = []
        seen: dict = {}
        for opt in self.options:
            cat = opt.category
            if cat not in seen:
                seen[cat] = []
                self.categories.append((cat, seen[cat]))
            seen[cat].append(opt)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-container"):
            # 左栏：分类列表
            with Vertical(id="category-panel"):
                yield Static(_("cfg.category_panel"))
                yield ListView(*[
                    CategoryItem(cat, len(opts))
                    for cat, opts in self.categories
                ], id="category-list")
            # 右栏：选项列表
            with Vertical(id="option-panel"):
                yield Static(_("cfg.option_panel"))
                yield ListView(id="option-list")
        # 搜索栏
        yield Input(placeholder=_("cfg.search_placeholder"), id="search-container")
        # 状态栏
        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        """应用启动时"""
        cat_list = self.query_one("#category-list", ListView)
        if cat_list.children:
            cat_list.index = 0
        self._show_category_options(0)
        self._update_status()
        self.call_after_refresh(self._focus_category)
        self.set_timer(0.5, self._notify_welcome)

    def _focus_category(self) -> None:
        """聚焦到分类列表"""
        self.set_focus(self.query_one("#category-list", ListView))

    def _update_status(self) -> None:
        """更新状态栏"""
        lang_name = LANGUAGES[_current_language]["name"]
        modified_str = f" [bold yellow]{_('cfg.unsaved')}[/]" if self.modified else f" [dim]{_('cfg.unchanged')}[/]"
        n = len(self.options)
        board = _("cfg.unknown_board")
        for opt in self.options:
            if opt.name == "CONFIG_CLOCK_FREQ":
                freq_map = {
                    "16000000UL": "Uno/Mega (16 MHz)",
                    "84000000UL": "Due (84 MHz)",
                    "600000000UL": "Teensy 4.0 (600 MHz)",
                    "240000000UL": "ESP32 (240 MHz)",
                }
                board = freq_map.get(opt.value, f"{opt.value}")
                break
        sb = self.query_one("#status-bar", Static)
        sb.update(
            f" 📄 {self.file_path.name}"
            f"  |  {_('cfg.options')}: {n}"
            f"  |  {_('cfg.target')}: {board}"
            f"  |  [{lang_name}]"
            f"{modified_str}"
        )

    def _show_category_options(self, cat_index: int) -> None:
        """显示指定分类下的选项"""
        if cat_index < 0 or cat_index >= len(self.categories):
            return
        cat_name, opts = self.categories[cat_index]
        opt_list = self.query_one("#option-list", ListView)
        opt_list.clear()
        for opt in opts:
            opt_list.append(OptionItem(opt))
        if opt_list.children:
            opt_list.index = 0

        # 更新面板标题
        translated_cat = _(f"cat.{cat_name}")
        panel_title = self.query_one("#option-panel > Static")
        panel_title.update(f"{_('cfg.option_panel')} — {translated_cat} ({len(opts)} {_('cfg.items')})")

    def action_show_help(self) -> None:
        """显示帮助"""
        self.push_screen(HelpScreen())

    def action_save(self) -> None:
        """保存修改到文件"""
        self.lines = self._rebuild_lines_from_options()
        self.file_path.write_text("\n".join(self.lines) + "\n", encoding="utf-8")
        self.modified = False
        self._update_status()
        self.notify(
            f"{len(self.options)} {_('cfg.save_ok')}{self.file_path.name}",
            title=_("cfg.save_title"),
            severity="information",
            timeout=3,
        )

    def _rebuild_lines_from_options(self) -> List[str]:
        """从 options 对象重建文件内容"""
        lines = list(self.lines)
        for opt in self.options:
            idx = opt.line_number - 1
            if idx < len(lines):
                indent = re.match(r'^(\s*)', lines[idx]).group(1)
                new_line = f"{indent}#define {opt.name}       {opt.value}"
                # 保留尾部注释
                old_comment = re.search(r'//(.+)$', lines[idx])
                if old_comment and opt.name not in lines[idx]:
                    new_line += f"  //{old_comment.group(1)}"
                lines[idx] = new_line
        return lines

    def action_search(self) -> None:
        """打开搜索栏"""
        search_input = self.query_one("#search-container", Input)
        search_input.visible = True
        search_input.disabled = False
        search_input.value = ""
        self.set_focus(search_input)

    def on_input_changed(self, event: Input.Changed) -> None:
        """搜索输入变化时过滤选项"""
        if event.input.id != "search-container":
            return
        query = event.value.strip().lower()
        opt_list = self.query_one("#option-list", ListView)
        opt_list.clear()

        # 找出当前选中的分类
        cat_list = self.query_one("#category-list", ListView)
        current_cat_idx = cat_list.index

        if not query:
            # 没有搜索词 → 显示当前分类
            if current_cat_idx is not None and 0 <= current_cat_idx < len(self.categories):
                _, opts = self.categories[current_cat_idx]
                for opt in opts:
                    opt_list.append(OptionItem(opt))
            return

        # 搜索所有选项
        for opt in self.options:
            if (query in opt.name.lower() or query in opt.value.lower() or query in opt.description.lower()):
                opt_list.append(OptionItem(opt))

        panel_title = self.query_one("#option-panel > Static")
        panel_title.update(f"{_('cfg.search_results')}: '{event.value}' ({len(opt_list.children)} {_('cfg.items')})")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        """搜索提交后关闭搜索栏"""
        if event.input.id == "search-container":
            search_input = self.query_one("#search-container", Input)
            search_input.visible = False
            search_input.disabled = True
            self.set_focus(self.query_one("#option-list", ListView))

    def on_key(self, event) -> None:
        """全局按键处理"""
        if event.key == "escape":
            # 如果搜索栏可见，先关闭搜索栏
            search_input = self.query_one("#search-container", Input)
            if search_input.visible:
                search_input.visible = False
                search_input.disabled = True
                self.set_focus(self.query_one("#option-list", ListView))
                event.prevent_default()
                return
        if event.key == "question_mark" or (event.key == "slash" and event.ctrl):
            event.prevent_default()

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """列表项被选中时"""
        if event.list_view.id == "category-list":
            # 分类选中 → 切换选项
            idx = event.list_view.index
            if idx is not None:
                self._show_category_options(idx)
                self._update_status()
        elif event.list_view.id == "option-list":
            # 选项选中 → 打开编辑
            item = event.item
            if isinstance(item, OptionItem):
                self._edit_option(item.option)

    def action_focus_next_pane(self) -> None:
        """Tab 切换焦点"""
        cat_list = self.query_one("#category-list", ListView)
        opt_list = self.query_one("#option-list", ListView)
        focused = self.focused
        if focused == cat_list:
            self.set_focus(opt_list)
        elif focused == opt_list:
            self.set_focus(cat_list)
        else:
            self.set_focus(cat_list)

    def action_toggle_language(self) -> None:
        """切换语言 EN ↔ CN"""
        global _current_language
        new_lang = "zh" if _current_language == "en" else "en"
        _current_language = new_lang
        self.language = new_lang
        self.title = _("cfg.title")
        self.refresh_bindings()
        self._rebuild_category_list()
        self._rebuild_option_list()
        self._update_status()

    def watch_language(self, new_lang: str) -> None:
        """language reactive 变化时刷新 UI"""
        # Most work is done in action_toggle_language

    def _rebuild_category_list(self) -> None:
        """重建分类列表（语言切换后）"""
        cat_list = self.query_one("#category-list", ListView)
        for i, child in enumerate(cat_list.children):
            if isinstance(child, CategoryItem) and i < len(self.categories):
                cat_name, opts = self.categories[i]
                translated = _(f"cat.{cat_name}")
                child.cat_name = cat_name
                # 重建内部 Static
                child._composed_content = None
                child.compose_add_child(Static(f"[bold]{translated}[/]  [dim]({len(opts)})[/]"))

    def _rebuild_option_list(self) -> None:
        """重建当前选项列表（语言切换后）"""
        cat_list = self.query_one("#category-list", ListView)
        idx = cat_list.index if cat_list.index is not None else 0
        self._show_category_options(idx)
        # 更新面板标题语言
        if 0 <= idx < len(self.categories):
            cat_name, opts = self.categories[idx]
            translated = _(f"cat.{cat_name}")
            panel_title = self.query_one("#option-panel > Static")
            panel_title.update(f"{_('cfg.option_panel')} — {translated} ({len(opts)} {_('cfg.items')})")

    def _edit_option(self, option: ConfigOption) -> None:
        """打开编辑对话框（智能模式：有预制值用 RadioSet，否则用纯文本）"""
        def on_edit_done(result: Optional[str]) -> None:
            if result is not None and result != option.value:
                self.lines = apply_changes(self.lines, option, result)
                self.modified = True
                # 刷新选项列表
                self._refresh_option_list()
                self._update_status()
                self.notify(
                    f"[cyan]{option.name}[/] → [green]{result}[/]",
                    title=_("cfg.modified"),
                    severity="information",
                    timeout=2,
                )

        # 如果选项有预制值列表，使用智能编辑弹窗
        if option.name in PRESET_VALUES:
            self.push_screen(SmartEditScreen(option, PRESET_VALUES[option.name]), on_edit_done)
        else:
            self.push_screen(EditScreen(option), on_edit_done)

    def action_apply_preset(self) -> None:
        """应用预制配置"""
        def on_preset_done(preset_key: Optional[str]) -> None:
            if preset_key is None or preset_key not in PRESETS:
                return
            preset = PRESETS[preset_key]
            name = preset["name_zh"] if _current_language == "zh" else preset["name"]
            count = 0
            for opt in self.options:
                if opt.name in preset["values"]:
                    new_val = preset["values"][opt.name]
                    if new_val != opt.value:
                        self.lines = apply_changes(self.lines, opt, new_val)
                        count += 1
            if count > 0:
                self.notify(
                    f"{name}: {count} {_('cfg.presets_updated')}",
                    title=_("cfg.save_title"),
                    severity="information",
                    timeout=3,
                )
            else:
                self.notify(
                    f"{name}: {_('cfg.presets_uptodate')}",
                    title=_("cfg.save_title"),
                    severity="information",
                    timeout=2,
                )

        self.push_screen(PresetScreen(), on_preset_done)

    def _refresh_option_list(self) -> None:
        """刷新当前选项列表显示"""
        cat_list = self.query_one("#category-list", ListView)
        idx = cat_list.index if cat_list.index is not None else 0
        self._show_category_options(idx)

    def _notify_welcome(self) -> None:
        """挂载完成后显示欢迎提示"""
        self.notify(
            _("cfg.welcome"),
            title=_("cfg.welcome_title"),
            severity="information",
            timeout=5,
        )


# ---------------------------------------------------------------------------
# Fallback: 纯命令行模式（当 textual 不可用时）
# ---------------------------------------------------------------------------

def cli_fallback(file_path: Path) -> None:
    """当 textual 不可用时的简单交互式配置"""
    global _current_language
    options, lines = parse_autoconf(file_path)
    modified = False

    print()
    print("=" * 66)
    print(f"  {_('cfg.cli_title')}")
    print("=" * 66)
    print(f"  {_('cfg.file')}: {file_path}")
    print(f"  {_('cfg.options')}: {len(options)}")
    print()

    while True:
        # 按分类显示
        for cat_name, cat_opts in _group_by_category(options).items():
            translated_cat = _(f"cat.{cat_name}")
            print(f"\n  [ {translated_cat} ]")
            print("-" * 66)
            for j, opt in enumerate(cat_opts):
                marker = " *" if opt.is_conditioned else "  "
                desc = get_option_description(opt.name, opt.description)
                print(f"  {marker} {j+1:2d}. {opt.name:<38s} = {opt.value}")
                if desc:
                    print(f"       {desc}")

        print()
        print("-" * 66)
        lang_name = LANGUAGES[_current_language]["name"]
        print(f"  [{lang_name}] {_('cfg.cli_cmd_prompt')}")
        modified_str = f" {_('cfg.cli_unsaved')}" if modified else ""
        print(f"  {_('cfg.cli_state')}: {len(options)} {_('cfg.options')}{modified_str}")

        try:
            cmd = input("\n  >> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if cmd == "q":
            if modified:
                confirm = input(_("cfg.cli_confirm_save")).strip().lower()
                if confirm == "y":
                    _save_cli(options, lines, file_path)
            break
        elif cmd == "s":
            _save_cli(options, lines, file_path)
            modified = False
        elif cmd == "l":
            new_lang = "zh" if _current_language == "en" else "en"
            _current_language = new_lang
            print(f"  Language: {LANGUAGES[new_lang]['name']}")
        elif cmd == "r":
            options, lines = parse_autoconf(file_path)
            modified = False
            print(f"  [OK] {_('cfg.cli_refreshed')}")
        else:
            try:
                idx = int(cmd) - 1
                all_opts = [o for cat_opts in _group_by_category(options).values() for o in cat_opts]
                if 0 <= idx < len(all_opts):
                    opt = all_opts[idx]
                    desc = get_option_description(opt.name, opt.description)
                    print(f"\n  {_('cfg.cli_edit')}: {opt.name}")
                    print(f"  {_('cfg.cli_desc')}: {desc or _('cfg.edit_no_desc')}")
                    new_val = input(f"  {_('cfg.cli_new_val')} [{opt.value}]: ").strip()
                    if new_val and new_val != opt.value:
                        lines = apply_changes(lines, opt, new_val)
                        modified = True
                        print("  [OK] Modified")
                else:
                    print("  [ERR] Invalid number")
            except ValueError:
                print("  [ERR] Invalid input")


def _group_by_category(options: List[ConfigOption]) -> dict:
    groups = {}
    for opt in options:
        groups.setdefault(opt.category, []).append(opt)
    return groups


def _save_cli(options, lines, file_path):
    file_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  [OK]{_('cfg.cli_saved')}{file_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def find_autoconf() -> Path:
    """自动查找 autoconf.h 文件"""
    # 1. 命令行参数
    if len(sys.argv) > 1:
        p = Path(sys.argv[1])
        if p.exists() and p.is_file():
            return p.resolve()

    # 2. 相对于脚本位置
    script_dir = Path(__file__).resolve().parent
    candidates = [
        script_dir / ".." / "src" / "autoconf.h",
        script_dir.parent / "src" / "autoconf.h",
        Path.cwd() / "autoconf.h",
        Path.cwd() / "src" / "autoconf.h",
    ]
    for c in candidates:
        resolved = c.resolve()
        if resolved.exists() and resolved.is_file():
            return resolved

    # 3. 当前工作目录向上查找
    cwd = Path.cwd().resolve()
    for parent in [cwd] + list(cwd.parents):
        candidate = parent / "autoconf.h"
        if candidate.exists():
            return candidate

    print("✗ 找不到 autoconf.h！请指定路径:")
    print(f"  python {sys.argv[0]} 路径/to/autoconf.h")
    sys.exit(1)


def main():
    file_path = find_autoconf()
    print(f"📂 载入: {file_path}")

    if TEXTUAL_AVAILABLE:
        app = ConfigApp(file_path)
        app.run()
    else:
        print("⚠️  'textual' 未安装，使用命令行回退模式。")
        print("   安装: pip install -r tools/requirements.txt")
        print()
        cli_fallback(file_path)


if __name__ == "__main__":
    main()
