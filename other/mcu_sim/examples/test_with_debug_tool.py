#!/usr/bin/env python3
"""
Integration test: mcu_sim + kalico_debug_tool
=============================================

End-to-end test that:

1. Starts mcu_sim with a compiled generic_arduino firmware (.hex)
2. Connects kalico_debug_tool (CLI mode) via TCP
3. Runs the identify protocol handshake
4. Verifies identify_response is received and parsed correctly

Usage::

    # From kalico root directory:
    python other/mcu_sim/examples/test_with_debug_tool.py firmware.hex
    python other/mcu_sim/examples/test_with_debug_tool.py firmware.hex --mcu atmega2560

Prerequisites:
    - QEMU installed (qemu-system-avr on PATH)
    - Compiled generic_arduino firmware (.hex file)
    - kalico_debug_tool dependencies (pyserial)
"""

from __future__ import annotations

import argparse
import logging
import pathlib
import subprocess
import sys
import time


# Add project root to sys.path so we can import both tools
_PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT / "other" / "kalico_debug_tool"))
sys.path.insert(0, str(_PROJECT_ROOT / "other"))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Integration test: mcu_sim + kalico_debug_tool",
    )
    parser.add_argument("firmware", help="Path to .hex firmware file")
    parser.add_argument("--mcu", "-m", default=None,
                        help="MCU model (atmega328p, atmega2560, etc.)")
    parser.add_argument("--host", default="127.0.0.1",
                        help="TCP host for virtual serial bridge")
    parser.add_argument("--port", "-p", type=int, default=0,
                        help="TCP port (0 = auto)")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="Overall test timeout in seconds")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(levelname)-7s] %(message)s",
        datefmt="%H:%M:%S",
    )
    logger = logging.getLogger("integration_test")

    firmware_path = pathlib.Path(args.firmware)
    if not firmware_path.is_file():
        logger.error("Firmware file not found: %s", args.firmware)
        return 1

    # Step 1: Start mcu_sim
    logger.info("=" * 60)
    logger.info("Step 1: Starting MCU simulator...")
    logger.info("=" * 60)

    from mcu_sim.core import MCUSimulator
    from mcu_sim.firmware import FirmwareFile

    # Inspect firmware
    fw = FirmwareFile.from_path(args.firmware)
    logger.info("Firmware: %s (%d bytes, arch=%s)",
                fw.path.name, fw.total_size, fw.arch.value)

    mcu = args.mcu
    if not mcu:
        from mcu_sim.backends.registry import find_model_for_arch
        models = find_model_for_arch(fw.arch)
        if models:
            mcu = models[0].name
            logger.info("Auto-detected MCU: %s", mcu)

    sim = MCUSimulator(host=args.host, port=args.port)

    try:
        sim.load(str(firmware_path), mcu=mcu)
        serial_port = sim.start(wait_ready=True, ready_timeout=15.0)

        # Step 2: Wait a moment then read boot banner
        time.sleep(0.5)
        boot = sim.recv_line(timeout=3.0)
        if boot:
            logger.info("MCU boot banner: %s", boot[:200])

        # Step 3: Run the built-in protocol smoke test
        logger.info("=" * 60)
        logger.info("Step 2: Running identify protocol smoke test...")
        logger.info("=" * 60)

        from mcu_sim.protocol_test import run_smoke_test
        result = run_smoke_test(host=args.host, port=serial_port, timeout=15.0)

        if result == 0:
            logger.info("=" * 60)
            logger.info("✓ Integration test PASSED!")
            logger.info("=" * 60)
            logger.info("")
            logger.info("To use interactively:")
            logger.info("  1. Start:  python -m mcu_sim run %s --mcu %s",
                        args.firmware, mcu)
            logger.info("  2. Connect: python -m other.kalico_debug_tool --port tcp:%s:%d",
                        args.host, serial_port)
            logger.info("     or in CLI: connect tcp:%s:%d", args.host, serial_port)
            logger.info("  3. In kalico_debug_tool CLI: send_command identify offset=0 count=40")

        return result

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 130
    except Exception as exc:
        logger.error("Test failed: %s", exc, exc_info=args.verbose)
        return 1
    finally:
        sim.stop()


if __name__ == "__main__":
    sys.exit(main())
