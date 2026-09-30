#!/usr/bin/env python3
# =======================================================================#
# Copyright (C) 2020 - 2026 Dominik Willner <th33xitus@gmail.com>       #
#                                                                       #
# This file is part of KIAUH - Klipper Installation And Update Helper   #
# https://github.com/dw-0/kiauh                                         #
#                                                                       #
# This file may be distributed under the terms of the GNU GPLv3 license #
# =======================================================================#
"""
Kalico Documentation Server launcher.

Serves the real documentation site via `mkdocs serve` using the project
virtual environment (docs/_kalico/.venv), so the served pages use the
actual theme, overrides and extra.css from docs/_kalico/ instead of a
bundled fallback stylesheet.

Usage:
    python docs_server.py              # Start on default port 8800
    python docs_server.py --port 9000  # Custom port
    python docs_server.py --host 0.0.0.0  # Listen on all interfaces
"""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
MKDOCS_YML = SCRIPT_DIR / "docs" / "_kalico" / "mkdocs.yml"
VENV_DIR = SCRIPT_DIR / "docs" / "_kalico" / ".venv"

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8800


def find_venv_python() -> str:
    """Locate the Python interpreter inside the docs virtual environment."""
    if os.name == "nt":
        candidates = [
            VENV_DIR / "Scripts" / "python.exe",
            VENV_DIR / "bin" / "python",
        ]
    else:
        candidates = [
            VENV_DIR / "bin" / "python",
            VENV_DIR / "bin" / "python3",
        ]
    for candidate in candidates:
        if candidate.is_file():
            return str(candidate)
    return sys.executable


def port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Return True once the server is accepting connections on host:port."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except OSError:
        return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Kalico Documentation Server (mkdocs serve)"
    )
    parser.add_argument(
        "--host", default=DEFAULT_HOST, help=f"Bind address (default: {DEFAULT_HOST})"
    )
    parser.add_argument(
        "--port", type=int, default=DEFAULT_PORT, help=f"Port (default: {DEFAULT_PORT})"
    )
    args = parser.parse_args()

    if not MKDOCS_YML.is_file():
        print(f"ERROR: mkdocs config not found at {MKDOCS_YML}", file=sys.stderr)
        sys.exit(1)

    python = find_venv_python()

    print("=============================================")
    print("  Kalico Documentation Server (mkdocs serve)")
    print(f"  URL:      http://{args.host}:{args.port}/")
    print(f"  Config:   {MKDOCS_YML}")
    print(f"  Python:   {python}")
    print("  Press Ctrl+C to stop.")
    print("=============================================")

    cmd = [
        python,
        "-m",
        "mkdocs",
        "serve",
        "-f",
        str(MKDOCS_YML),
        "-a",
        f"{args.host}:{args.port}",
    ]

    proc = subprocess.Popen(cmd)
    opened = False
    try:
        deadline = time.time() + 60
        while proc.poll() is None and time.time() < deadline:
            if not opened and port_open(args.host, args.port):
                webbrowser.open(f"http://{args.host}:{args.port}/")
                opened = True
            time.sleep(0.5)
        proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down.")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    main()
