# Predefined common Kalico MCU commands
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Common MCU Commands
===================

Templates for frequently used Kalico MCU commands, shared between
the connection panel (real MCU) and simulator panel (virtual MCU).

Each command dict has:
  - name:      message name in the data dictionary
  - label:     display label for the button
  - default_params: default parameter values
  - hint:      parameter descriptions for UI
  - category:  functional category
"""

COMMON_COMMANDS = [
    # ─── Discovery & Status ──────────────────────────────────────────
    {
        "name": "identify",
        "label": "identify (发现命令)",
        "default_params": {"offset": 0, "count": 40},
        "hint": "offset=0 count=40",
        "category": "发现与状态",
    },
    {
        "name": "get_config",
        "label": "get_config (获取配置)",
        "default_params": {},
        "hint": "无参数",
        "category": "发现与状态",
    },
    {
        "name": "get_clock",
        "label": "get_clock (获取时钟)",
        "default_params": {},
        "hint": "无参数",
        "category": "发现与状态",
    },
    {
        "name": "get_status",
        "label": "get_status (获取状态)",
        "default_params": {},
        "hint": "无参数",
        "category": "发现与状态",
    },
    {
        "name": "finalize_config",
        "label": "finalize_config (完成配置)",
        "default_params": {"crc": 0},
        "hint": "crc=0",
        "category": "发现与状态",
    },

    # ─── Digital I/O ─────────────────────────────────────────────────
    {
        "name": "update_digital_out",
        "label": "digital_out ON (引脚开)",
        "default_params": {"oid": 0, "value": 1},
        "hint": "oid=0 value=1",
        "category": "数字 I/O",
    },
    {
        "name": "update_digital_out",
        "label": "digital_out OFF (引脚关)",
        "default_params": {"oid": 0, "value": 0},
        "hint": "oid=0 value=0",
        "category": "数字 I/O",
    },
    {
        "name": "set_digital_out_pwm",
        "label": "PWM 输出",
        "default_params": {"oid": 0, "value": 128},
        "hint": "oid=0 value=128",
        "category": "数字 I/O",
    },

    # ─── Analog I/O ──────────────────────────────────────────────────
    {
        "name": "query_analog",
        "label": "query_analog (查询模拟)",
        "default_params": {"oid": 0, "clock": 0, "rest_ticks": 100000},
        "hint": "oid=0 clock=0 rest_ticks=100000",
        "category": "模拟 I/O",
    },

    # ─── Stepper Motor ───────────────────────────────────────────────
    {
        "name": "queue_step",
        "label": "queue_step (步进一步)",
        "default_params": {"oid": 0, "interval": 1000, "count": 1, "add": 0},
        "hint": "oid=0 interval=1000 count=1 add=0",
        "category": "步进电机",
    },
    {
        "name": "set_next_step_dir",
        "label": "set_dir + (方向+)",
        "default_params": {"oid": 0, "dir": 1},
        "hint": "oid=0 dir=1",
        "category": "步进电机",
    },
    {
        "name": "set_next_step_dir",
        "label": "set_dir - (方向-)",
        "default_params": {"oid": 0, "dir": 0},
        "hint": "oid=0 dir=0",
        "category": "步进电机",
    },
    {
        "name": "stepper_get_position",
        "label": "get_position (获取位置)",
        "default_params": {"oid": 0},
        "hint": "oid=0",
        "category": "步进电机",
    },
    {
        "name": "reset_step_clock",
        "label": "reset_step_clock (重置时钟)",
        "default_params": {"oid": 0, "clock": 0},
        "hint": "oid=0 clock=0",
        "category": "步进电机",
    },

    # ─── Configuration ───────────────────────────────────────────────
    {
        "name": "config",
        "label": "config (配置对象)",
        "default_params": {"oid": 0},
        "hint": "oid=0",
        "category": "配置",
    },
    {
        "name": "config_key",
        "label": "config_key (配置键)",
        "default_params": {"oid": 0, "key": b"hello"},
        "hint": "oid=0 key=hello",
        "category": "配置",
    },

    # ─── CAN Bus ─────────────────────────────────────────────────────
    {
        "name": "get_canbus_id",
        "label": "get_canbus_id (查询CAN ID)",
        "default_params": {},
        "hint": "无参数 (仅CAN)",
        "category": "CAN 总线",
    },
]


def get_commands_by_category(category: str) -> list:
    """Get all commands in a category."""
    return [c for c in COMMON_COMMANDS if c["category"] == category]


def get_categories() -> list:
    """Get all unique category names in order."""
    seen = []
    for c in COMMON_COMMANDS:
        if c["category"] not in seen:
            seen.append(c["category"])
    return seen
