# CLI interface for mcu_sim
#
# Copyright (C) 2025-2026 KalicoCrew
# SPDX-License-Identifier: GPL-3.0-or-later

"""
Command-Line Interface
======================

Provides the ``mcu_sim`` command with the following subcommands::

    serve      Start a pure-Python MCU simulator (recommended)
    run        Load firmware and start QEMU-based simulation
    info       Show firmware file metadata
    backends   List available QEMU backends on this system
    test       Run a quick identify-protocol smoke test against a live MCU
"""

from __future__ import annotations

import argparse
import logging
import sys
import time

from .core import MCUSimulator
from .firmware import FirmwareFile
from .backends.registry import list_backends, list_models
from .py_mcu import PyMCU
from .protocol_test import run_smoke_test


def _setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    fmt = "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s"
    logging.basicConfig(level=level, format=fmt, datefmt="%H:%M:%S")


def _cmd_serve(args: argparse.Namespace) -> int:
    """Execute the ``serve`` subcommand — start a pure-Python MCU."""
    _setup_logging(args.verbose)
    logger = logging.getLogger("mcu_sim")
    logger.info("Starting Python MCU simulator '%s'...", args.name)
    mcu = PyMCU(name=args.name, serial_port=args.port or 0)
    mcu.start()
    return 0


# ---------------------------------------------------------------------------
# Subcommand: run
# ---------------------------------------------------------------------------

def _cmd_run(args: argparse.Namespace) -> int:
    """Execute the ``run`` subcommand."""
    _setup_logging(args.verbose)
    logger = logging.getLogger("mcu_sim")

    sim = MCUSimulator(
        host=args.host,
        port=args.port or 0,
    )

    try:
        sim.load(args.firmware, mcu=args.mcu)
        sim.start(wait_ready=not args.no_wait, ready_timeout=args.timeout)

        if args.oneshot:
            # Run the auto-test and exit
            return _run_auto_test(sim, args)

        logger.info("")
        logger.info("Simulation running. Press Ctrl+C to stop.")
        logger.info("Connect kalico_debug_tool to tcp:%s:%d", args.host, sim.serial_port)

        # Keep alive until user interrupts
        while sim.is_running:
            time.sleep(0.5)

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as exc:
        logger.error("Error: %s", exc)
        if args.verbose:
            raise
        return 1
    finally:
        sim.stop()

    return 0


def _run_auto_test(sim: MCUSimulator, args: argparse.Namespace) -> int:
    """Run a built-in identify protocol smoke test."""
    logger = logging.getLogger("mcu_sim.test")

    logger.info("Running auto-test (identify protocol smoke test)...")
    logger.info("Serial port: tcp:%s:%d", args.host, sim.serial_port)

    # Give the firmware a moment to boot
    time.sleep(1.0)

    # Read any boot messages from the debug serial
    boot_output = sim.recv_line(timeout=3.0)
    if boot_output:
        logger.info("Boot banner: %s", boot_output[:120])

    # Now test Kalico protocol via the bridge
    # We need to connect via TCP and send an identify command
    from .protocol_test import run_smoke_test
    return run_smoke_test(host=args.host, port=sim.serial_port)


# ---------------------------------------------------------------------------
# Subcommand: info
# ---------------------------------------------------------------------------

def _cmd_info(args: argparse.Namespace) -> int:
    """Execute the ``info`` subcommand."""
    fw = FirmwareFile.from_path(args.firmware)
    print(f"File:       {fw.path}")
    print(f"Format:     {fw.format.upper()}")
    print(f"Arch:       {fw.arch.display_name} ({fw.arch.value})")
    print(f"Size:       {fw.total_size:,} bytes ({fw.total_size / 1024:.1f} KB)")
    print(f"Load addr:  0x{fw.load_address:08X}")
    if fw.entry_point is not None:
        print(f"Entry:      0x{fw.entry_point:08X}")
    print()
    return 0


# ---------------------------------------------------------------------------
# Subcommand: backends
# ---------------------------------------------------------------------------

def _cmd_backends(args: argparse.Namespace) -> int:
    """Execute the ``backends`` subcommand."""
    print("Available QEMU backends:")
    print("-" * 60)
    for info in list_backends():
        status = "✓ AVAILABLE" if info.available else "✗ NOT FOUND"
        print(f"  {info.name:20s}  {status}")
        print(f"    binary: {info.binary}")
        print(f"    path:   {info.path}")
        if info.version:
            print(f"    ver:    {info.version}")
        print()

    print("Supported MCU models:")
    print("-" * 60)
    for model in list_models():
        print(f"  {model.name:15s}  {model.arch.value:15s}  {model.description}")
    print()

    return 0


# ---------------------------------------------------------------------------
# Subcommand: test
# ---------------------------------------------------------------------------

def _cmd_test(args: argparse.Namespace) -> int:
    """Execute the ``test`` subcommand.

    Loads a firmware image, starts the simulator, runs an identify
    protocol smoke test against it, and reports the result.
    """
    _setup_logging(args.verbose)
    logger = logging.getLogger("mcu_sim")

    sim = MCUSimulator(host=args.host, port=args.port or 0)

    try:
        sim.load(args.firmware, mcu=args.mcu)
        sim.start(wait_ready=True, ready_timeout=args.timeout)

        # Read boot banner
        boot_output = sim.recv_line(timeout=5.0)
        if boot_output:
            print(f"[BOOT] {boot_output[:200]}")

        return _run_auto_test(sim, args)

    except KeyboardInterrupt:
        logger.info("Interrupted")
    except Exception as exc:
        logger.error("Test failed: %s", exc)
        if args.verbose:
            raise
        return 1
    finally:
        sim.stop()

    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mcu_sim",
        description="MCU firmware simulator for Kalico protocol testing",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # ---- serve ---- (recommended)
    p_serve = sub.add_parser("serve", help="Start a pure-Python MCU simulator")
    p_serve.add_argument("--port", "-p", type=int, default=0,
                         help="TCP port (0=auto, default: 0)")
    p_serve.add_argument("--name", default="py-mcu",
                         help="MCU name reported in identify response")
    p_serve.set_defaults(func=_cmd_serve)

    # ---- run ----
    p_run = sub.add_parser("run", help="Load firmware and start simulation")
    p_run.add_argument("firmware", help="Path to .hex, .bin, or .elf firmware file")
    p_run.add_argument("--mcu", "-m", default=None,
                       help="MCU model (atmega328p, atmega2560, sam3x8e, imxrt1062, esp32)")
    p_run.add_argument("--host", default="127.0.0.1", help="TCP host (default: 127.0.0.1)")
    p_run.add_argument("--port", "-p", type=int, default=0,
                       help="TCP port (0 = auto, default: 0)")
    p_run.add_argument("--no-wait", action="store_true",
                       help="Don't wait for MCU ready signal")
    p_run.add_argument("--timeout", type=float, default=15.0,
                       help="Ready timeout in seconds (default: 15)")
    p_run.add_argument("--oneshot", action="store_true",
                       help="Run auto-test and exit (instead of staying alive)")
    p_run.set_defaults(func=_cmd_run)

    # ---- info ----
    p_info = sub.add_parser("info", help="Show firmware file metadata")
    p_info.add_argument("firmware", help="Path to firmware file")
    p_info.set_defaults(func=_cmd_info)

    # ---- backends ----
    p_backends = sub.add_parser("backends", help="List available QEMU backends")
    p_backends.set_defaults(func=_cmd_backends)

    # ---- test ----
    p_test = sub.add_parser("test", help="Run identify protocol smoke test")
    p_test.add_argument("firmware", help="Path to firmware file")
    p_test.add_argument("--mcu", "-m", default=None, help="MCU model")
    p_test.add_argument("--host", default="127.0.0.1", help="TCP host")
    p_test.add_argument("--port", "-p", type=int, default=0, help="TCP port")
    p_test.add_argument("--timeout", type=float, default=15.0, help="Ready timeout")
    p_test.set_defaults(func=_cmd_test)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(args: list[str] | None = None) -> int:
    """Main CLI entry point.

    Returns:
        Exit code (0 = success).
    """
    parser = _build_parser()
    ns = parser.parse_args(args)
    return ns.func(ns)


if __name__ == "__main__":
    sys.exit(main())
