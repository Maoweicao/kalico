#!/usr/bin/env python3
"""
Kalico CLI - Unified Command-Line Interface for Kalico 3D Printer Firmware

This is the main entry point for all Kalico CLI operations.
It provides a unified interface for MCU management, configuration,
diagnostics, and system operations.

Usage:
    kalico <command> [options]
    kalico mcu list [--verbose]
    kalico mcu check [--fix]
    kalico config show
    kalico config validate
    kalico doctor [--fix]
    kalico can scan [--interface can0]
    kalico version

Copyright (C) 2026 Kalico contributors
SPDX-License-Identifier: GPL-3.0-or-later
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

# Project path setup
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Version info
__version__ = "0.1.0"
__app_name__ = "kalico"


class KalicoCLI:
    """Main CLI class for Kalico unified interface."""

    def __init__(self):
        self.parser = self._create_parser()
        self.args = None

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create the main argument parser."""
        parser = argparse.ArgumentParser(
            prog=__app_name__,
            description="Kalico - Unified CLI for 3D Printer Firmware",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s mcu list                     List connected MCUs
  %(prog)s mcu check --fix              Check and fix MCU configuration
  %(prog)s config show                  Show configuration file location
  %(prog)s config validate              Validate configuration
  %(prog)s doctor --fix                 Run diagnostics and auto-fix
  %(prog)s can scan                     Scan CAN bus for devices
  %(prog)s version                      Show version information
  %(prog)s --help                       Show this help message
            """
        )
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose output"
        )
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        parser.add_argument(
            "--version",
            action="version",
            version=f"%(prog)s {__version__}"
        )

        # Create subparsers for commands
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands"
        )

        # MCU commands
        mcu_parser = subparsers.add_parser(
            "mcu",
            help="MCU management commands"
        )
        mcu_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        mcu_subparsers = mcu_parser.add_subparsers(
            dest="mcu_command",
            help="MCU subcommands"
        )

        # mcu list
        mcu_list_parser = mcu_subparsers.add_parser(
            "list",
            help="List connected MCUs"
        )
        mcu_list_parser.add_argument(
            "--transport",
            choices=["serial", "can", "tcp", "udp", "all"],
            default="all",
            help="Filter by transport type"
        )
        mcu_list_parser.add_argument(
            "--scan-network",
            action="store_true",
            help="Scan network for TCP/UDP devices"
        )

        # mcu check
        mcu_check_parser = mcu_subparsers.add_parser(
            "check",
            help="Check MCU configuration"
        )
        mcu_check_parser.add_argument(
            "--fix",
            action="store_true",
            help="Interactive configuration fix"
        )
        mcu_check_parser.add_argument(
            "-c", "--config",
            help="Path to printer.cfg"
        )

        # Config commands
        config_parser = subparsers.add_parser(
            "config",
            help="Configuration management"
        )
        config_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        config_subparsers = config_parser.add_subparsers(
            dest="config_command",
            help="Config subcommands"
        )

        # config show
        config_show_parser = config_subparsers.add_parser(
            "show",
            help="Show configuration file location"
        )
        config_show_parser.add_argument(
            "-c", "--config",
            help="Path to printer.cfg"
        )

        # config validate
        config_validate_parser = config_subparsers.add_parser(
            "validate",
            help="Validate configuration file"
        )
        config_validate_parser.add_argument(
            "-c", "--config",
            help="Path to printer.cfg"
        )

        # Doctor command
        doctor_parser = subparsers.add_parser(
            "doctor",
            help="Run diagnostics and auto-fix"
        )
        doctor_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        doctor_parser.add_argument(
            "--fix",
            action="store_true",
            help="Auto-fix fixable issues"
        )
        doctor_parser.add_argument(
            "--dry-fix",
            action="store_true",
            help="Preview fixes without applying"
        )
        doctor_parser.add_argument(
            "-c", "--config",
            help="Path to printer.cfg"
        )
        doctor_parser.add_argument(
            "-n", "--network",
            nargs="?",
            const="auto",
            default=None,
            help="Scan network for TCP/UDP devices"
        )
        doctor_parser.add_argument(
            "--skip-env",
            action="store_true",
            help="Skip environment checks"
        )
        doctor_parser.add_argument(
            "--skip-config",
            action="store_true",
            help="Skip config checks"
        )
        doctor_parser.add_argument(
            "--skip-mcu",
            action="store_true",
            help="Skip MCU checks"
        )
        doctor_parser.add_argument(
            "--skip-service",
            action="store_true",
            help="Skip service checks"
        )

        # CAN commands
        can_parser = subparsers.add_parser(
            "can",
            help="CAN bus management"
        )
        can_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        can_subparsers = can_parser.add_subparsers(
            dest="can_command",
            help="CAN subcommands"
        )

        # can scan
        can_scan_parser = can_subparsers.add_parser(
            "scan",
            help="Scan CAN bus for devices"
        )
        can_scan_parser.add_argument(
            "-i", "--interface",
            nargs="+",
            help="CAN interface(s) to scan"
        )
        can_scan_parser.add_argument(
            "--timeout",
            type=float,
            default=2.0,
            help="Scan timeout in seconds"
        )

        # can info
        can_info_parser = can_subparsers.add_parser(
            "info",
            help="Show CAN interface information"
        )
        can_info_parser.add_argument(
            "-i", "--interface",
            nargs="+",
            help="CAN interface(s) to query"
        )

        # Version command
        version_parser = subparsers.add_parser(
            "version",
            help="Show version information"
        )
        version_parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )

        # Add --json to all subparsers
        for subparser in [mcu_list_parser, mcu_check_parser, config_show_parser, 
                         config_validate_parser, can_scan_parser, can_info_parser]:
            subparser.add_argument(
                "--json",
                action="store_true",
                help="Output in JSON format"
            )

        return parser

    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments."""
        self.args = self.parser.parse_args(args)

        # Setup logging
        if self.args.verbose:
            logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
        else:
            logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")

        # Dispatch to command handlers
        if self.args.command is None:
            self.parser.print_help()
            return 0

        try:
            handler = getattr(self, f"_cmd_{self.args.command}", None)
            if handler:
                return handler()
            else:
                print(f"Unknown command: {self.args.command}")
                return 1
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return 130
        except Exception as e:
            logging.exception("Command failed")
            print(f"Error: {e}")
            return 1

    def _cmd_mcu(self) -> int:
        """Handle MCU commands."""
        if not self.args.mcu_command:
            print("Usage: kalico mcu {list|check}")
            return 1

        if self.args.mcu_command == "list":
            return self._mcu_list()
        elif self.args.mcu_command == "check":
            return self._mcu_check()
        else:
            print(f"Unknown mcu command: {self.args.mcu_command}")
            return 1

    def _mcu_list(self) -> int:
        """List connected MCUs."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from mcu_check import SerialScanner, CANScanner, NetworkScanner, PrinterConfigParser

        print("=" * 60)
        print("Connected MCU Devices")
        print("=" * 60)

        transport_filter = self.args.transport
        devices = []

        # Serial devices
        if transport_filter in ("serial", "all"):
            print("\n[Serial Ports]")
            serial_devices = SerialScanner.list_ports()
            if serial_devices:
                for dev in serial_devices:
                    self._print_device(dev)
                devices.extend(serial_devices)
            else:
                print("  No serial ports found")

        # CAN devices
        if transport_filter in ("can", "all"):
            print("\n[CAN Interfaces]")
            can_scanner = CANScanner()
            can_ifaces = can_scanner.list_interfaces()
            if can_ifaces:
                for iface_info in can_ifaces:
                    iface_name = iface_info['name']
                    print(f"  Scanning {iface_name}...")
                    devs = can_scanner.scan_devices(iface_name)
                    for dev in devs:
                        self._print_device(dev, indent=4)
                    devices.extend(devs)
            else:
                print("  No CAN interfaces found")

        # Network devices
        if transport_filter in ("tcp", "udp", "all") and self.args.scan_network:
            print("\n[Network Scan]")
            network_devices = NetworkScanner.scan_network(
                progress_callback=lambda msg: print(f"  {msg}")
            )
            for dev in network_devices:
                self._print_device(dev)
            devices.extend(network_devices)

        # Summary
        print("\n" + "=" * 60)
        print(f"Total devices found: {len(devices)}")
        print("=" * 60)

        if self.args.json:
            json_devices = []
            for dev in devices:
                json_devices.append({
                    "type": dev.device_type,
                    "path": dev.path,
                    "description": dev.description,
                    "is_kalico": dev.is_kalico,
                    "vid": dev.vid,
                    "pid": dev.pid,
                    "serial_number": dev.serial_number,
                })
            print("\nJSON Output:")
            print(json.dumps(json_devices, indent=2))

        return 0

    def _mcu_check(self) -> int:
        """Check MCU configuration."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from mcu_check import MCUChecker

        checker = MCUChecker(config_path=self.args.config, verbose=self.args.verbose)
        results = checker.check_all()

        if self.args.json:
            json_results = []
            for r in results:
                json_results.append({
                    "mcu": r.mcu_config.display_name,
                    "transport": r.mcu_config.transport,
                    "matched": r.matched_device is not None,
                    "responsive": r.is_responsive,
                    "firmware": r.firmware_version,
                    "issues": r.issues,
                    "suggestions": r.suggestions,
                })
            print(json.dumps(json_results, indent=2))

        if self.args.fix:
            checker.interactive_fix(results)

        return 0 if all(r.is_responsive or not r.matched_device for r in results) else 1

    def _cmd_config(self) -> int:
        """Handle config commands."""
        if not self.args.config_command:
            print("Usage: kalico config {show|validate}")
            return 1

        if self.args.config_command == "show":
            return self._config_show()
        elif self.args.config_command == "validate":
            return self._config_validate()
        else:
            print(f"Unknown config command: {self.args.config_command}")
            return 1

    def _config_show(self) -> int:
        """Show configuration file location."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from mcu_check import PrinterConfigParser
        
        config_path = PrinterConfigParser.find_config(self.args.config)

        if config_path:
            print(f"Configuration file: {config_path}")
            print(f"Absolute path: {os.path.abspath(config_path)}")

            # Show file info
            stat = os.stat(config_path)
            print(f"File size: {stat.st_size} bytes")
            print(f"Last modified: {stat.st_mtime}")

            if self.args.json:
                print(json.dumps({
                    "path": config_path,
                    "absolute_path": os.path.abspath(config_path),
                    "size": stat.st_size,
                    "modified": stat.st_mtime,
                }, indent=2))
            return 0
        else:
            print("Configuration file not found")
            print("\nSearched in:")
            print("  ~/printer_data/config/printer.cfg")
            print("  ~/klipper_config/printer.cfg")
            print("  ~/.config/klipper/printer.cfg")
            print("  /etc/klipper/printer.cfg")
            print("  ./printer.cfg")
            print("\nUse --config to specify the path")
            return 1

    def _config_validate(self) -> int:
        """Validate configuration file."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from mcu_check import PrinterConfigParser, MCUChecker
        
        config_path = PrinterConfigParser.find_config(self.args.config)
        if not config_path:
            print("Configuration file not found")
            return 1

        print(f"Validating configuration: {config_path}")

        # Parse config
        try:
            mcu_configs = PrinterConfigParser.parse_config(config_path)
            print(f"Found {len(mcu_configs)} MCU configuration(s)")

            for mcu in mcu_configs:
                print(f"\n  [{mcu.display_name}]")
                print(f"    Transport: {mcu.transport}")
                if mcu.transport == "serial":
                    print(f"    Port: {mcu.serial}")
                    print(f"    Baud: {mcu.baud}")
                elif mcu.transport == "can":
                    print(f"    UUID: {mcu.canbus_uuid}")
                    print(f"    Interface: {mcu.canbus_interface}")
                elif mcu.transport == "tcp":
                    print(f"    Host: {mcu.tcp_host}:{mcu.tcp_port}")
                elif mcu.transport == "udp":
                    print(f"    Host: {mcu.udp_host}:{mcu.udp_port}")

            print("\nConfiguration syntax is valid")
            return 0

        except Exception as e:
            print(f"Configuration error: {e}")
            return 1

    def _cmd_doctor(self) -> int:
        """Run diagnostics."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from kalico_doctor import DoctorRunner

        # Create a namespace for doctor
        doctor_args = argparse.Namespace(
            config=self.args.config,
            verbose=self.args.verbose,
            network=self.args.network,
            fix=self.args.fix,
            dry_fix=self.args.dry_fix,
            json=self.args.json,
            skip_env=self.args.skip_env,
            skip_config=self.args.skip_config,
            skip_mcu=self.args.skip_mcu,
            skip_service=self.args.skip_service,
        )

        runner = DoctorRunner(doctor_args)
        return runner.run()

    def _cmd_can(self) -> int:
        """Handle CAN commands."""
        if not self.args.can_command:
            print("Usage: kalico can {scan|info}")
            return 1

        if self.args.can_command == "scan":
            return self._can_scan()
        elif self.args.can_command == "info":
            return self._can_info()
        else:
            print(f"Unknown can command: {self.args.can_command}")
            return 1

    def _can_scan(self) -> int:
        """Scan CAN bus for devices."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from canbus_query import scan_can_devices, get_can_interfaces, print_scan_results

        interfaces = self.args.interface or get_can_interfaces()

        if not interfaces:
            print("No CAN interfaces found")
            return 1

        print("=" * 60)
        print("CAN Bus Scan")
        print("=" * 60)

        devices_by_iface = {}
        for iface in interfaces:
            print(f"\nScanning {iface}...")
            devs, error = scan_can_devices(iface, self.args.timeout)
            if error:
                print(f"  Error: {error}")
                devices_by_iface[iface] = []
            else:
                devices_by_iface[iface] = devs
                print(f"  Found {len(devs)} device(s)")

        print_scan_results(devices_by_iface, quiet=False)

        if self.args.json:
            all_devices = []
            for iface, devs in devices_by_iface.items():
                for dev in devs:
                    dev["interface"] = iface
                    all_devices.append(dev)
            print("\nJSON Output:")
            print(json.dumps(all_devices, indent=2))

        return 0

    def _can_info(self) -> int:
        """Show CAN interface information."""
        # Import from the same directory
        sys.path.insert(0, str(SCRIPT_DIR))
        from canbus_query import (
            get_can_interfaces, get_interface_state,
            get_can_bitrate, get_can_state, get_interface_stats,
            format_bitrate, BUS_STATE_NAMES
        )

        interfaces = self.args.interface or get_can_interfaces()

        if not interfaces:
            print("No CAN interfaces found")
            return 1

        print("=" * 60)
        print("CAN Interface Information")
        print("=" * 60)

        for iface in interfaces:
            print(f"\n[{iface}]")
            state = get_interface_state(iface)
            print(f"  State: {state}")

            bitrate = get_can_bitrate(iface)
            print(f"  Bitrate: {format_bitrate(bitrate)}")

            can_state = get_can_state(iface)
            if can_state:
                print(f"  CAN State: {can_state}")

            stats = get_interface_stats(iface)
            if stats:
                print(f"  RX Errors: {stats.get('rx_errors', 'N/A')}")
                print(f"  TX Errors: {stats.get('tx_errors', 'N/A')}")
                print(f"  RX Over Errors: {stats.get('rx_over_errors', 'N/A')}")
                print(f"  TX Dropped: {stats.get('tx_dropped', 'N/A')}")

        if self.args.json:
            json_data = []
            for iface in interfaces:
                iface_data = {
                    "name": iface,
                    "state": get_interface_state(iface),
                    "bitrate": get_can_bitrate(iface),
                    "can_state": get_can_state(iface),
                    "stats": get_interface_stats(iface),
                }
                json_data.append(iface_data)
            print("\nJSON Output:")
            print(json.dumps(json_data, indent=2))

        return 0

    def _cmd_version(self) -> int:
        """Show version information."""
        import subprocess
        
        # Get git info
        git_info = {"version": "unknown", "branch": "unknown", "remote": "unknown", "url": "unknown"}
        try:
            result = subprocess.run(['git', 'describe', '--tags', '--always'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            if result.returncode == 0:
                git_info['version'] = result.stdout.strip()
            
            result = subprocess.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            if result.returncode == 0:
                git_info['branch'] = result.stdout.strip()
            
            result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                                  capture_output=True, text=True, cwd=PROJECT_ROOT)
            if result.returncode == 0:
                git_info['url'] = result.stdout.strip()
                git_info['remote'] = 'origin'
        except Exception:
            pass
        
        print("=" * 60)
        print("Kalico Version Information")
        print("=" * 60)
        print(f"\nApp Name: Kalico")
        print(f"CLI Version: {__version__}")
        print(f"Git Version: {git_info['version']}")
        print(f"Git Branch: {git_info['branch']}")
        print(f"Git Remote: {git_info['remote']}")
        print(f"Git URL: {git_info['url']}")
        print(f"\nPython: {sys.version}")
        print(f"Platform: {platform.platform()}")
        print(f"Architecture: {platform.machine()}")
        
        if self.args.json:
            print(json.dumps({
                "app_name": "Kalico",
                "cli_version": __version__,
                "git_version": git_info['version'],
                "git_branch": git_info['branch'],
                "git_remote": git_info['remote'],
                "git_url": git_info['url'],
                "python_version": sys.version,
                "platform": platform.platform(),
                "architecture": platform.machine(),
            }, indent=2))
        
        return 0

    def _print_device(self, device, indent: int = 2):
        """Print device information."""
        prefix = " " * indent
        type_str = device.display_type
        print(f"{prefix}{device.path} - {type_str}")
        if device.description and device.description != type_str:
            print(f"{prefix}  Description: {device.description}")
        if device.serial_number:
            print(f"{prefix}  Serial: {device.serial_number}")
        if device.manufacturer:
            print(f"{prefix}  Manufacturer: {device.manufacturer}")
        if device.is_kalico:
            print(f"{prefix}  * Kalico/Klipper device detected")
        print()


def main(args: Optional[list] = None) -> int:
    """Main entry point for the CLI."""
    cli = KalicoCLI()
    return cli.run(args)


if __name__ == "__main__":
    sys.exit(main())
