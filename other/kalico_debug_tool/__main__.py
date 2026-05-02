#!/usr/bin/env python3
# Kalico Debug Tool - Main Entry Point
#
# Copyright (C) 2025  KalicoCrew
#
# This file may be distributed under the terms of the GNU GPLv3 license.

"""
Kalico Debug Tool
=================

Host-side debugging utility for Kalico 3D printer firmware protocol.

Usage:
    python -m kalico_debug_tool           # Launch GUI (default)
    python -m kalico_debug_tool --cli     # Interactive CLI mode
    python -m kalico_debug_tool --batch   # AI Bridge JSON mode
    python -m kalico_debug_tool --version # Show version
"""

import argparse
import logging
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Kalico 固件协议调试上位机工具"
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="启动交互式 CLI 模式"
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="启动 AI Bridge 批量 JSON 模式 (stdin/stdout)"
    )
    parser.add_argument(
        "--version", action="store_true",
        help="显示版本信息"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="启用详细日志输出"
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.WARNING
    logging.basicConfig(
        level=log_level,
        format="%(levelname)s: %(message)s",
    )

    if args.version:
        from . import __version__, __app_name__
        print(f"{__app_name__} v{__version__}")
        sys.exit(0)

    if args.batch:
        from .cli.ai_bridge import run_batch
        run_batch()
        sys.exit(0)

    if args.cli:
        from .cli.main_cli import run_cli
        run_cli()
        sys.exit(0)

    # Default: launch GUI
    try:
        import tkinter as tk
        from .gui.main_window import DebugToolWindow

        root = tk.Tk()
        app = DebugToolWindow(root)
        root.mainloop()
    except ImportError as e:
        print(f"GUI 不可用: {e}")
        print("请确保 tkinter 已安装，或使用 --cli 模式")
        sys.exit(1)
    except Exception as e:
        print(f"GUI 启动失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
