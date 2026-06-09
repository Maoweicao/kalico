#!/usr/bin/env python3
# Kalico Doctor - Environment diagnostic and auto-repair tool
#
# Checks configuration, environment, MCU connectivity, and services.
# Supports --fix to auto-repair where possible.
#
# Copyright (C) 2026  Kalico contributors
# This file may be distributed under the terms of the GNU GPLv3 license.
from __future__ import annotations

import argparse
import configparser
import json
import logging
import os
import platform
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Project path setup
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(SCRIPT_DIR))

# ---------------------------------------------------------------------------
# Color output
# ---------------------------------------------------------------------------

IS_WINDOWS = platform.system() == "Windows"
FORCE_NO_COLOR = os.environ.get("NO_COLOR") == "1"
FORCE_COLOR = os.environ.get("FORCE_COLOR") == "1"

# Ensure UTF-8 output on Windows
if IS_WINDOWS:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def _supports_color() -> bool:
    if FORCE_NO_COLOR:
        return False
    if FORCE_COLOR:
        return True
    if IS_WINDOWS:
        return os.environ.get("TERM") in ("xterm", "xterm-256color", "screen")
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = _supports_color()


class C:
    RESET = "\033[0m" if USE_COLOR else ""
    BOLD = "\033[1m" if USE_COLOR else ""
    DIM = "\033[2m" if USE_COLOR else ""
    RED = "\033[31m" if USE_COLOR else ""
    GREEN = "\033[32m" if USE_COLOR else ""
    YELLOW = "\033[33m" if USE_COLOR else ""
    BLUE = "\033[34m" if USE_COLOR else ""
    MAGENTA = "\033[35m" if USE_COLOR else ""
    CYAN = "\033[36m" if USE_COLOR else ""
    WHITE = "\033[37m" if USE_COLOR else ""
    BG_RED = "\033[41m" if USE_COLOR else ""
    BG_GREEN = "\033[42m" if USE_COLOR else ""
    BG_YELLOW = "\033[43m" if USE_COLOR else ""


def _detect_unicode_support() -> bool:
    """Detect if the terminal supports Unicode box-drawing chars."""
    if IS_WINDOWS:
        enc = (sys.stdout.encoding or "").lower()
        # Only use Unicode if explicitly UTF-8
        if "utf-8" in enc or "utf8" in enc:
            return True
        # Check for Windows Terminal or VS Code
        if os.environ.get("WT_SESSION") or os.environ.get("TERM_PROGRAM") == "vscode":
            return True
        return False
    return True


USE_UNICODE = _detect_unicode_support()

SYM_OK = "✓" if USE_UNICODE else "[OK]"
SYM_WARN = "⚠" if USE_UNICODE else "[!!]"
SYM_ERR = "✗" if USE_UNICODE else "[ERR]"
SYM_INFO = "ℹ" if USE_UNICODE else "[i]"
SYM_ARROW = "→" if USE_UNICODE else "->"


def safe_print(msg: str):
    """Print with encoding error handling."""
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("utf-8", errors="replace").decode("utf-8", errors="replace"))


def ok(msg: str) -> str:
    return f"{C.GREEN}{C.BOLD}{SYM_OK}{C.RESET} {msg}"


def warn(msg: str) -> str:
    return f"{C.YELLOW}{C.BOLD}{SYM_WARN}{C.RESET} {msg}"


def err(msg: str) -> str:
    return f"{C.RED}{C.BOLD}{SYM_ERR}{C.RESET} {msg}"


def info(msg: str) -> str:
    return f"{C.BLUE}{C.BOLD}{SYM_INFO}{C.RESET} {msg}"


def heading(msg: str) -> str:
    return f"\n{C.CYAN}{C.BOLD}[{msg}]{C.RESET}"


def dim(msg: str) -> str:
    return f"{C.DIM}{msg}{C.RESET}"


def bold(msg: str) -> str:
    return f"{C.BOLD}{msg}{C.RESET}"


def green(msg: str) -> str:
    return f"{C.GREEN}{msg}{C.RESET}"


def red(msg: str) -> str:
    return f"{C.RED}{msg}{C.RESET}"


def yellow(msg: str) -> str:
    return f"{C.YELLOW}{msg}{C.RESET}"


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------


class Severity(Enum):
    OK = "ok"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"
    FIXABLE = "fixable"


@dataclass
class CheckResult:
    severity: Severity
    message: str
    detail: Optional[str] = None
    fix_id: Optional[str] = None
    fix_description: Optional[str] = None
    fix_data: Any = None

    def display(self, indent: int = 4) -> str:
        prefix = " " * indent
        if self.severity == Severity.OK:
            line = ok(self.message)
        elif self.severity == Severity.WARNING:
            line = warn(self.message)
        elif self.severity == Severity.ERROR:
            line = err(self.message)
        elif self.severity == Severity.FIXABLE:
            line = warn(f"{self.message} {dim('(fixable)')}")
        else:
            line = info(self.message)
        if self.detail:
            line += f"\n{prefix}  {dim(self.detail)}"
        return f"{prefix}{line}"


@dataclass
class CheckCategory:
    name: str
    results: List[CheckResult] = field(default_factory=list)
    skipped: bool = False
    skip_reason: str = ""

    @property
    def has_errors(self) -> bool:
        return any(r.severity == Severity.ERROR for r in self.results)

    @property
    def has_warnings(self) -> bool:
        return any(
            r.severity in (Severity.WARNING, Severity.FIXABLE)
            for r in self.results
        )

    @property
    def ok_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.OK)

    @property
    def warn_count(self) -> int:
        return sum(
            1
            for r in self.results
            if r.severity in (Severity.WARNING, Severity.FIXABLE)
        )

    @property
    def error_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.ERROR)

    @property
    def fixable_count(self) -> int:
        return sum(1 for r in self.results if r.severity == Severity.FIXABLE)

    def display(self) -> str:
        lines = [heading(self.name)]
        if self.skipped:
            lines.append(f"    {dim(f'Skipped: {self.skip_reason}')}")
            return "\n".join(lines)
        for r in self.results:
            lines.append(r.display())
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Config validation constants
# ---------------------------------------------------------------------------

KNOWN_KINEMATICS = [
    "cartesian",
    "corexy",
    "corexz",
    "delta",
    "rotary_delta",
    "polar",
    "winch",
    "hybrid_corexy",
    "hybrid_corexz",
    "deltesian",
    "none",
]

KNOWN_THERMISTORS = [
    "EPCOS 100K B57560G104F",
    "ATC Semitec 104GT-2",
    "Generic 3950",
    "Honeywell 100K 135-104LAG-J01",
    "NTC 100K beta 3950",
    "SliceEngineering 450",
    "TDK NTCG104LH104JT1",
    "PT100",
    "PT1000",
    "PT1000 INA826",
    "MAX6675",
    "MAX31855",
    "MAX31856",
    "MAX31865",
    "BME280",
    "HTU21D",
    "SHT3x",
    "SI7013",
    "AHT10",
    "LM75",
    "AD595",
    "AD8494",
    "AD8495",
    "AD8496",
    "AD8497",
    "thermocouple-ctype",
    "thermocouple-ktype",
    "thermocouple-ltype",
    "thermocouple-lotype",
    "thermocouple-mtype",
    "thermocouple-ntype",
    "thermocouple-stype",
    "thermocouple-ttype",
    "thermocouple-btype",
    "thermocouple-etype",
    "thermocouple-rtype",
    "temperature_mcu",
    "temperature_host",
    "temperature_combined",
]

REQUIRED_PRINTER_OPTIONS = {
    "printer": ["kinematics"],
}

PRINTER_OPTION_RANGES = {
    "printer": {
        "max_velocity": (1, 100000),
        "max_accel": (1, 1000000),
        "max_z_velocity": (0.001, 10000),
        "max_z_accel": (0.001, 1000000),
        "minimum_cruise_ratio": (0.0, 1.0),
        "square_corner_velocity": (0.0, 100.0),
    },
    "extruder": {
        "max_extrude_only_distance": (0.0, 10000.0),
        "max_extrude_cross_section": (0.0, 100.0),
        "nozzle_diameter": (0.001, 10.0),
        "filament_diameter": (0.001, 10.0),
        "max_temp": (0.0, 500.0),
        "min_temp": (-20.0, 200.0),
    },
    "heater_bed": {
        "max_temp": (0.0, 500.0),
        "min_temp": (-20.0, 200.0),
    },
}

DEPRECATED_OPTIONS: Dict[Tuple[str, str], str] = {
    ("danger_options", "adc_ignore_limits"): "temp_ignore_limits",
}

KNOWN_SECTIONS = {
    "mcu",
    "printer",
    "stepper_x",
    "stepper_y",
    "stepper_z",
    "stepper_a",
    "stepper_b",
    "stepper_c",
    "extruder",
    "extruder1",
    "heater_bed",
    "fan",
    "heater_fan",
    "controller_fan",
    "temperature_fan",
    "heater_generic",
    "bed_mesh",
    "bed_screws",
    "bed_tilt",
    "bltouch",
    "probe",
    "smart_effector",
    "dockable_probe",
    "load_cell_probe",
    "input_shaper",
    "tmc2130",
    "tmc2208",
    "tmc2209",
    "tmc2240",
    "tmc2660",
    "tmc5160",
    "tmc_uart",
    "display",
    "display_glyph",
    "display_template",
    "display_data",
    "display_menu",
    "neopixel",
    "dotstar",
    "pca9533",
    "pca9632",
    "save_variables",
    "idle_timeout",
    "pause_resume",
    "exclude_object",
    "firmware_retraction",
    "virtual_sdcard",
    "respond",
    "danger_options",
    "temperature_sensor",
    "temperature_combined",
    "resonance_tester",
    "adxl345",
    "lis2dw",
    "lis3dh",
    "mpu9250",
    "icm20948",
    "angle",
    "servo",
    "output_pin",
    "pwm_tool",
    "pwm_cycle_time",
    "multi_pin",
    "filament_switch_sensor",
    "filament_motion_sensor",
    "hall_filament_width_sensor",
    "tsl1401cl_filament_width_sensor",
    "delayed_gcode",
    "board_pins",
    "duplicate_pin_override",
    "gcode_macro",
    "gcode_arcs",
    "gcode_move",
    "gcode_shell_command",
    "safe_z_home",
    "homing_override",
    "homing_heaters",
    "z_tilt",
    "z_tilt_ng",
    "quad_gantry_level",
    "delta_calibrate",
    "delta",
    "skew_correction",
    "force_move",
    "stepper_enable",
    "manual_probe",
    "manual_stepper",
    "bed_mesh_calibrate",
    "z_calibration",
    "endstop_phase",
    "verify_heater",
    "adc_scaled",
    "adc_temperature",
    "thermistor",
    "spi_temperature",
    "bus",
    "buttons",
    "gcode_button",
    "query_adc",
    "query_endstops",
    "query_pins",
    "motion_report",
    "print_stats",
    "toolhead",
    "system_stats",
    "mcu_status",
    "webhooks",
    "configfile",
    "gcode",
    "heaters",
    "pins",
    "kinematics",
    "extras",
    "tuning_tower",
    "control_mc",
    "shaper_calibrate",
    "shaper_defs",
    "palette2",
    "trad_rack",
    "mux",
    "replicape",
    "samd_sercom",
    "sx1509",
    "mcp4018",
    "mcp4451",
    "mcp4728",
    "dac084S085",
    "ad5206",
    "hc595",
    "encoder",
    "tmc2130",
    "tmc2208",
    "tmc2209",
    "tmc2240",
    "tmc2660",
    "tmc5160",
    "z_thermal_adjust",
    "axis_twist_compensation",
    "load_cell",
    "extruder_stepper",
    "bed_mesh_default",
    "nozzle_cleanup",
    "gcode_mcu_trace",
    "force_move",
    "closed_loop",
    "belay",
    "mpc_ambient_temperature",
    "mpc_block_temperature",
}


# ---------------------------------------------------------------------------
# Environment check
# ---------------------------------------------------------------------------


class EnvironmentCheck:
    """Check Python, dependencies, system tools, and user groups."""

    def __init__(self, project_root: Path, venv_path: Optional[str] = None):
        self.project_root = project_root
        self.venv_path = venv_path

    def run(self) -> List[CheckResult]:
        results: List[CheckResult] = []
        results.extend(self._check_python())
        results.extend(self._check_dependencies())
        results.extend(self._check_system_tools())
        results.extend(self._check_user_groups())
        results.extend(self._check_disk_space())
        return results

    def _check_python(self) -> List[CheckResult]:
        results = []
        v = sys.version_info
        ver_str = f"{v.major}.{v.minor}.{v.micro}"
        if v >= (3, 9):
            results.append(
                CheckResult(Severity.OK, f"Python {ver_str}")
            )
        else:
            results.append(
                CheckResult(
                    Severity.ERROR,
                    f"Python {ver_str} (requires >= 3.9)",
                )
            )
        return results

    def _check_dependencies(self) -> List[CheckResult]:
        results = []
        req_file = self.project_root / "scripts" / "klippy-requirements.txt"
        if not req_file.exists():
            results.append(
                CheckResult(
                    Severity.WARNING,
                    "klippy-requirements.txt not found",
                )
            )
            return results

        required = self._parse_requirements(req_file)
        installed = self._get_installed_packages()

        for pkg_name, pkg_spec in required.items():
            pkg_lower = pkg_name.lower().replace("-", "_")
            if pkg_lower in installed:
                inst_ver = installed[pkg_lower]
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"{pkg_name} {inst_ver}",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        Severity.FIXABLE,
                        f"{pkg_name} not installed",
                        detail=f"Required: {pkg_spec}",
                        fix_id="pip_install",
                        fix_description=f"pip install {pkg_name}",
                        fix_data=pkg_name,
                    )
                )
        return results

    def _parse_requirements(self, req_file: Path) -> Dict[str, str]:
        pkgs: Dict[str, str] = {}
        try:
            for line in req_file.read_text().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Handle lines like: "cffi==1.15.1 ; python_full_version < '3.13'"
                # Extract just the package==version part
                if ";" in line:
                    line = line.split(";")[0].strip()
                if "==" in line:
                    name, ver = line.split("==", 1)
                    pkgs[name.strip()] = ver.strip()
                elif ">=" in line:
                    name, ver = line.split(">=", 1)
                    pkgs[name.strip()] = f">={ver.strip()}"
                elif "~=" in line:
                    name, ver = line.split("~=", 1)
                    pkgs[name.strip()] = f"~={ver.strip()}"
                else:
                    pkgs[line.strip()] = ""
        except Exception as e:
            logging.debug(f"Error parsing requirements: {e}")
        return pkgs

    def _get_installed_packages(self) -> Dict[str, str]:
        installed: Dict[str, str] = {}
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                for pkg in json.loads(result.stdout):
                    name = pkg["name"].lower().replace("-", "_")
                    installed[name] = pkg["version"]
        except Exception:
            pass
        return installed

    def _check_system_tools(self) -> List[CheckResult]:
        results = []
        tools = [
            ("git", "Version control"),
            ("make", "Build system"),
        ]
        for tool_name, desc in tools:
            path = shutil.which(tool_name)
            if path:
                results.append(
                    CheckResult(Severity.OK, f"{tool_name} ({desc})")
                )
            else:
                results.append(
                    CheckResult(
                        Severity.WARNING,
                        f"{tool_name} not found ({desc})",
                    )
                )
        return results

    def _check_user_groups(self) -> List[CheckResult]:
        results = []
        if IS_WINDOWS:
            results.append(
                CheckResult(
                    Severity.INFO,
                    "User group check skipped (Windows)",
                )
            )
            return results

        try:
            import grp

            try:
                dialout = grp.getgrnam("dialout")
                import getpass

                user = getpass.getuser()
                if user in dialout.gr_mem:
                    results.append(
                        CheckResult(
                            Severity.OK,
                            f"User '{user}' in dialout group",
                        )
                    )
                else:
                    results.append(
                        CheckResult(
                            Severity.FIXABLE,
                            f"User '{user}' not in dialout group",
                            detail="Serial port access may be denied",
                            fix_id="add_dialout_group",
                            fix_description=f"usermod -aG dialout {user}",
                            fix_data=user,
                        )
                    )
            except KeyError:
                results.append(
                    CheckResult(
                        Severity.INFO,
                        "dialout group not found on this system",
                    )
                )
        except ImportError:
            results.append(
                CheckResult(
                    Severity.INFO,
                    "grp module not available (non-Linux)",
                )
            )
        return results

    def _check_disk_space(self) -> List[CheckResult]:
        results = []
        try:
            usage = shutil.disk_usage(str(self.project_root))
            free_gb = usage.free / (1024**3)
            if free_gb < 1.0:
                results.append(
                    CheckResult(
                        Severity.WARNING,
                        f"Low disk space: {free_gb:.1f} GB free",
                    )
                )
            else:
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"Disk space: {free_gb:.1f} GB free",
                    )
                )
        except Exception:
            pass
        return results


# ---------------------------------------------------------------------------
# Config check
# ---------------------------------------------------------------------------


class ConfigCheck:
    """Validate printer.cfg configuration."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def find_config(self, config_path: Optional[str] = None) -> Optional[str]:
        if config_path:
            return config_path if os.path.exists(config_path) else None
        search = [
            os.path.expanduser("~/printer_data/config/printer.cfg"),
            os.path.expanduser("~/klipper_config/printer.cfg"),
            os.path.expanduser("~/.config/klipper/printer.cfg"),
            "/etc/klipper/printer.cfg",
            "printer.cfg",
        ]
        for p in search:
            if os.path.exists(p):
                return p
        return None

    def run(self, config_path: Optional[str] = None) -> Tuple[List[CheckResult], Optional[str]]:
        results: List[CheckResult] = []
        resolved = self.find_config(config_path)
        if not resolved:
            results.append(
                CheckResult(
                    Severity.ERROR,
                    "printer.cfg not found",
                    detail="Searched: ~/printer_data/config/printer.cfg, "
                    "~/klipper_config/printer.cfg, ./printer.cfg",
                )
            )
            return results, None
        results.append(
            CheckResult(Severity.OK, f"Config file: {resolved}")
        )
        results.extend(self._check_syntax(resolved))
        results.extend(self._check_sections(resolved))
        results.extend(self._check_deprecated(resolved))
        results.extend(self._check_required(resolved))
        results.extend(self._check_ranges(resolved))
        results.extend(self._check_heaters(resolved))
        results.extend(self._check_includes(resolved))
        return results, resolved

    def _read_config(self, path: str) -> Optional[configparser.ConfigParser]:
        cfg = configparser.ConfigParser(interpolation=None)
        try:
            cfg.read(path)
            return cfg
        except configparser.Error as e:
            return None

    def _check_syntax(self, path: str) -> List[CheckResult]:
        results = []
        cfg = configparser.ConfigParser(interpolation=None)
        try:
            cfg.read(path)
            results.append(
                CheckResult(Severity.OK, "Config syntax valid")
            )
        except configparser.MissingSectionHeaderError as e:
            results.append(
                CheckResult(
                    Severity.ERROR,
                    "Syntax error: missing section header",
                    detail=str(e),
                )
            )
        except configparser.ParsingError as e:
            results.append(
                CheckResult(
                    Severity.ERROR,
                    "Syntax error",
                    detail=str(e),
                )
            )
        except Exception as e:
            results.append(
                CheckResult(
                    Severity.ERROR,
                    "Failed to parse config",
                    detail=str(e),
                )
            )
        return results

    def _check_sections(self, path: str) -> List[CheckResult]:
        results = []
        cfg = self._read_config(path)
        if not cfg:
            return results

        unknown = []
        for section in cfg.sections():
            base = section.split(" ", 1)[0] if " " in section else section
            if base not in KNOWN_SECTIONS and not base.startswith("mcu"):
                unknown.append(section)

        if unknown:
            for s in unknown:
                results.append(
                    CheckResult(
                        Severity.WARNING,
                        f"Unknown section [{s}]",
                        detail="This section is not recognized. "
                        "Check for typos or verify it's a plugin.",
                    )
                )
        else:
            results.append(
                CheckResult(Severity.OK, "All config sections recognized")
            )
        return results

    def _check_deprecated(self, path: str) -> List[CheckResult]:
        results = []
        cfg = self._read_config(path)
        if not cfg:
            return results

        found_deprecated = False
        for (section, option), replacement in DEPRECATED_OPTIONS.items():
            if cfg.has_section(section) and cfg.has_option(section, option):
                found_deprecated = True
                results.append(
                    CheckResult(
                        Severity.FIXABLE,
                        f"[{section}] {option} is deprecated",
                        detail=f"Replace with: {replacement}",
                        fix_id="fix_deprecated",
                        fix_description=f"Rename {option} to {replacement}",
                        fix_data=(section, option, replacement),
                    )
                )

        if not found_deprecated:
            results.append(
                CheckResult(Severity.OK, "No deprecated options found")
            )
        return results

    def _check_required(self, path: str) -> List[CheckResult]:
        results = []
        cfg = self._read_config(path)
        if not cfg:
            return results

        for section, options in REQUIRED_PRINTER_OPTIONS.items():
            if not cfg.has_section(section):
                results.append(
                    CheckResult(
                        Severity.ERROR,
                        f"Required section [{section}] missing",
                    )
                )
                continue
            for opt in options:
                if not cfg.has_option(section, opt):
                    results.append(
                        CheckResult(
                            Severity.ERROR,
                            f"[{section}] {opt} is required",
                        )
                    )
                else:
                    val = cfg.get(section, opt)
                    results.append(
                        CheckResult(
                            Severity.OK,
                            f"[{section}] {opt} = {val}",
                        )
                    )
        return results

    def _check_ranges(self, path: str) -> List[CheckResult]:
        results = []
        cfg = self._read_config(path)
        if not cfg:
            return results

        for section, options in PRINTER_OPTION_RANGES.items():
            if not cfg.has_section(section):
                continue
            for opt, (lo, hi) in options.items():
                if not cfg.has_option(section, opt):
                    continue
                try:
                    val = cfg.getfloat(section, opt)
                    if val < lo or val > hi:
                        results.append(
                            CheckResult(
                                Severity.WARNING,
                                f"[{section}] {opt} = {val} "
                                f"(expected {lo}..{hi})",
                            )
                        )
                except (ValueError, TypeError):
                    pass

        # Check min_temp < max_temp for heaters
        for section in cfg.sections():
            if section.startswith("extruder") or section == "heater_bed":
                if cfg.has_option(section, "min_temp") and cfg.has_option(
                    section, "max_temp"
                ):
                    try:
                        mn = cfg.getfloat(section, "min_temp")
                        mx = cfg.getfloat(section, "max_temp")
                        if mn >= mx:
                            results.append(
                                CheckResult(
                                    Severity.ERROR,
                                    f"[{section}] min_temp ({mn}) >= max_temp ({mx})",
                                )
                            )
                    except (ValueError, TypeError):
                        pass

        return results

    def _check_heaters(self, path: str) -> List[CheckResult]:
        results = []
        cfg = self._read_config(path)
        if not cfg:
            return results

        for section in cfg.sections():
            if section.startswith("extruder") or section == "heater_bed":
                sensor = cfg.get(section, "sensor_type", fallback=None)
                if sensor and sensor not in KNOWN_THERMISTORS:
                    # Check partial match for compound names
                    matched = any(
                        t.lower() in sensor.lower() for t in KNOWN_THERMISTORS
                    )
                    if not matched:
                        results.append(
                            CheckResult(
                                Severity.WARNING,
                                f"[{section}] Unknown sensor_type: {sensor}",
                            )
                        )
        return results

    def _check_includes(self, path: str) -> List[CheckResult]:
        results = []
        try:
            content = Path(path).read_text()
        except Exception:
            return results

        import re

        include_pattern = re.compile(r"!!include\s+(.+)")
        base_dir = Path(path).parent
        for line in content.splitlines():
            match = include_pattern.search(line)
            if match:
                inc_path = match.group(1).strip()
                full_path = base_dir / inc_path
                if not full_path.exists():
                    # Try glob
                    import glob as globmod

                    if not globmod.glob(str(full_path)):
                        results.append(
                            CheckResult(
                                Severity.WARNING,
                                f"Include file not found: {inc_path}",
                            )
                        )
        if not results:
            results.append(
                CheckResult(Severity.OK, "All include files found")
            )
        return results


# ---------------------------------------------------------------------------
# MCU check (delegates to mcu_check.py)
# ---------------------------------------------------------------------------


class MCUCheck:
    """Check MCU connectivity by reusing mcu_check.py."""

    def __init__(self, config_path: Optional[str], scan_network: bool = False):
        self.config_path = config_path
        self.scan_network = scan_network

    def run(self) -> List[CheckResult]:
        results: List[CheckResult] = []
        try:
            from mcu_check import (
                CANScanner,
                NetworkScanner,
                PrinterConfigParser,
                SerialScanner,
            )
        except ImportError:
            results.append(
                CheckResult(
                    Severity.WARNING,
                    "mcu_check.py not available, skipping MCU check",
                )
            )
            return results

        config_file = self.config_path
        if not config_file:
            parser = PrinterConfigParser()
            config_file = parser.find_config()

        if not config_file:
            results.append(
                CheckResult(
                    Severity.WARNING,
                    "No config file for MCU check",
                )
            )
            return results

        mcu_configs = PrinterConfigParser.parse_config(config_file)
        if not mcu_configs:
            results.append(
                CheckResult(
                    Severity.INFO,
                    "No MCU sections found in config",
                )
            )
            return results

        # Scan serial ports
        serial_devices = SerialScanner.list_ports()
        can_devices: list = []
        network_devices: list = []

        # Scan CAN
        can_ifaces = CANScanner.list_interfaces()
        for iface_info in can_ifaces:
            iface_name = iface_info["name"]
            iface_type = iface_info.get("type", "socketcan")
            devs = CANScanner.scan_devices(
                iface_name, timeout=1.0, iface_type=iface_type
            )
            can_devices.extend(devs)

        # Scan network if requested
        if self.scan_network:
            network_devices = NetworkScanner.scan_network(timeout=0.5)

        all_devices = serial_devices + can_devices + network_devices

        # Check each MCU
        for mcu in mcu_configs:
            results.extend(
                self._check_mcu(mcu, all_devices, serial_devices, can_devices)
            )

        return results

    def _check_mcu(
        self, mcu, all_devices, serial_devices, can_devices
    ) -> List[CheckResult]:
        results = []
        name = mcu.display_name

        if mcu.transport == "serial":
            if not mcu.serial:
                results.append(
                    CheckResult(
                        Severity.ERROR,
                        f"MCU [{name}]: No serial port configured",
                    )
                )
                return results

            matched = None
            for dev in all_devices:
                if dev.device_type == "serial":
                    try:
                        if os.path.realpath(dev.path) == os.path.realpath(
                            mcu.serial
                        ):
                            matched = dev
                            break
                    except Exception:
                        if dev.path == mcu.serial:
                            matched = dev
                            break

            if matched:
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"MCU [{name}]: serial {mcu.serial} found",
                    )
                )
            else:
                if os.path.exists(mcu.serial):
                    results.append(
                        CheckResult(
                            Severity.FIXABLE,
                            f"MCU [{name}]: {mcu.serial} exists but not "
                            "detected as MCU device",
                            fix_id="fix_mcu_serial",
                            fix_description="Update serial port path",
                            fix_data={
                                "mcu": mcu,
                                "serial_devices": serial_devices,
                            },
                        )
                    )
                else:
                    avail = [d.path for d in serial_devices]
                    results.append(
                        CheckResult(
                            Severity.ERROR,
                            f"MCU [{name}]: {mcu.serial} does not exist",
                            detail=f"Available: {', '.join(avail) if avail else 'none'}",
                            fix_id="fix_mcu_serial",
                            fix_description="Update serial port path",
                            fix_data={
                                "mcu": mcu,
                                "serial_devices": serial_devices,
                            },
                        )
                    )

        elif mcu.transport == "can":
            if not mcu.canbus_uuid:
                results.append(
                    CheckResult(
                        Severity.ERROR,
                        f"MCU [{name}]: No CAN UUID configured",
                    )
                )
                return results

            uuid_upper = mcu.canbus_uuid.upper()
            matched = None
            for dev in all_devices:
                if dev.device_type == "can":
                    dev_uuid = dev.extra_info.get("uuid_hex", "").upper()
                    if dev_uuid == uuid_upper:
                        matched = dev
                        break

            if matched:
                app = matched.extra_info.get("app_name", "Unknown")
                status = matched.extra_info.get("status", "Unknown")
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"MCU [{name}]: CAN UUID {mcu.canbus_uuid} found "
                        f"({app}, {status})",
                    )
                )
            else:
                avail = [
                    d.path
                    for d in can_devices
                    if d.device_type == "can"
                ]
                results.append(
                    CheckResult(
                        Severity.ERROR,
                        f"MCU [{name}]: CAN UUID {mcu.canbus_uuid} "
                        "not found on bus",
                        detail=f"Found: {', '.join(avail) if avail else 'none'}",
                        fix_id="fix_mcu_can",
                        fix_description="Update CAN UUID",
                        fix_data={
                            "mcu": mcu,
                            "can_devices": can_devices,
                        },
                    )
                )

        elif mcu.transport in ("tcp", "udp"):
            host = mcu.tcp_host or mcu.udp_host
            port = mcu.tcp_port or mcu.udp_port
            results.append(
                CheckResult(
                    Severity.INFO,
                    f"MCU [{name}]: {mcu.transport.upper()} "
                    f"{host}:{port} (not probed)",
                )
            )

        return results


# ---------------------------------------------------------------------------
# Service check
# ---------------------------------------------------------------------------


class ServiceCheck:
    """Check klipper/moonraker systemd services."""

    SERVICES = ["klipper", "moonraker"]

    def run(self) -> List[CheckResult]:
        results: List[CheckResult] = []
        if IS_WINDOWS:
            results.append(
                CheckResult(
                    Severity.INFO,
                    "Service check skipped (Windows)",
                )
            )
            return results

        if not shutil.which("systemctl"):
            results.append(
                CheckResult(
                    Severity.INFO,
                    "systemctl not found, skipping service check",
                )
            )
            return results

        for svc in self.SERVICES:
            results.extend(self._check_service(svc))
        return results

    def _check_service(self, name: str) -> List[CheckResult]:
        results = []
        # Check if service exists
        try:
            ret = subprocess.run(
                ["systemctl", "cat", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if ret.returncode != 0:
                results.append(
                    CheckResult(
                        Severity.INFO,
                        f"{name}.service not installed",
                    )
                )
                return results
        except Exception:
            results.append(
                CheckResult(
                    Severity.INFO,
                    f"Cannot check {name}.service",
                )
            )
            return results

        # Check active state
        try:
            ret = subprocess.run(
                ["systemctl", "is-active", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            state = ret.stdout.strip()
            if state == "active":
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"{name}.service is running",
                    )
                )
            elif state == "inactive":
                results.append(
                    CheckResult(
                        Severity.FIXABLE,
                        f"{name}.service is not running",
                        fix_id="restart_service",
                        fix_description=f"systemctl start {name}",
                        fix_data=name,
                    )
                )
            elif state == "failed":
                results.append(
                    CheckResult(
                        Severity.ERROR,
                        f"{name}.service has failed",
                        detail="Check: journalctl -u {name} -n 50",
                        fix_id="restart_service",
                        fix_description=f"systemctl restart {name}",
                        fix_data=name,
                    )
                )
            else:
                results.append(
                    CheckResult(
                        Severity.WARNING,
                        f"{name}.service state: {state}",
                    )
                )
        except Exception:
            pass

        # Check enabled state
        try:
            ret = subprocess.run(
                ["systemctl", "is-enabled", name],
                capture_output=True,
                text=True,
                timeout=5,
            )
            enabled = ret.stdout.strip()
            if enabled == "enabled":
                results.append(
                    CheckResult(
                        Severity.OK,
                        f"{name}.service enabled at boot",
                    )
                )
            elif enabled == "disabled":
                results.append(
                    CheckResult(
                        Severity.FIXABLE,
                        f"{name}.service not enabled at boot",
                        fix_id="enable_service",
                        fix_description=f"systemctl enable {name}",
                        fix_data=name,
                    )
                )
        except Exception:
            pass

        return results


# ---------------------------------------------------------------------------
# Fix engine
# ---------------------------------------------------------------------------


class FixEngine:
    """Apply fixes for fixable issues."""

    def __init__(self, dry_run: bool = False):
        self.dry_run = dry_run
        self.applied: List[str] = []
        self.failed: List[str] = []
        self.skipped: List[str] = []

    def backup_config(self, config_path: str) -> Optional[str]:
        if not os.path.exists(config_path):
            return None
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = f"{config_path}.bak.{ts}"
        if self.dry_run:
            safe_print(f"  {dim(f'[dry-run] Would backup: {config_path} -> {backup}')}")
            return backup
        try:
            shutil.copy2(config_path, backup)
            safe_print(f"  {dim(f'Backup: {config_path} -> {backup}')}")
            return backup
        except Exception as e:
            safe_print(f"  {err(f'Backup failed: {e}')}")
            return None

    def apply_fixes(
        self,
        categories: List[CheckCategory],
        config_path: Optional[str],
    ) -> None:
        fixable = []
        for cat in categories:
            for r in cat.results:
                if r.severity == Severity.FIXABLE and r.fix_id:
                    fixable.append(r)

        if not fixable:
            safe_print(f"\n{info('No fixable issues found.')}")
            return

        safe_print(f"\n{bold(f'Found {len(fixable)} fixable issue(s):')}")
        for r in fixable:
            safe_print(f"  {yellow(SYM_ARROW)} {r.message}")
            if r.fix_description:
                safe_print(f"    {dim(r.fix_description)}")

        if self.dry_run:
            safe_print(f"\n{dim('[dry-run] No changes made.')}")
            return

        # Backup config if any fix touches it
        config_fixes = [
            r for r in fixable if r.fix_id in ("fix_deprecated",)
        ]
        if config_fixes and config_path:
            self.backup_config(config_path)

        safe_print("")
        for r in fixable:
            self._apply_one(r, config_path)

        # Summary
        if self.applied:
            safe_print(
                f"\n{green(f'Applied {len(self.applied)} fix(es):')}"
            )
            for s in self.applied:
                safe_print(f"  {green(SYM_OK)} {s}")
        if self.failed:
            safe_print(f"\n{red(f'Failed {len(self.failed)} fix(es):')}")
            for s in self.failed:
                safe_print(f"  {red(SYM_ERR)} {s}")
        if self.skipped:
            safe_print(f"\n{dim(f'Skipped {len(self.skipped)} fix(es):')}")
            for s in self.skipped:
                safe_print(f"  {dim('-')} {s}")

    def _apply_one(self, result: CheckResult, config_path: Optional[str]):
        fix_id = result.fix_id
        if fix_id == "pip_install":
            self._fix_pip_install(result)
        elif fix_id == "add_dialout_group":
            self._fix_dialout(result)
        elif fix_id == "fix_deprecated":
            self._fix_deprecated(result, config_path)
        elif fix_id == "restart_service":
            self._fix_restart_service(result)
        elif fix_id == "enable_service":
            self._fix_enable_service(result)
        elif fix_id in ("fix_mcu_serial", "fix_mcu_can"):
            self._fix_mcu(result)
        else:
            self.skipped.append(f"{result.message} (no handler for {fix_id})")

    def _fix_pip_install(self, result: CheckResult):
        pkg = result.fix_data
        safe_print(f"  Installing {pkg}...")
        try:
            ret = subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if ret.returncode == 0:
                self.applied.append(f"Installed {pkg}")
            else:
                self.failed.append(f"pip install {pkg}: {ret.stderr[:200]}")
        except Exception as e:
            self.failed.append(f"pip install {pkg}: {e}")

    def _fix_dialout(self, result: CheckResult):
        user = result.fix_data
        safe_print(f"  Adding {user} to dialout group...")
        try:
            ret = subprocess.run(
                ["sudo", "usermod", "-aG", "dialout", user],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if ret.returncode == 0:
                self.applied.append(
                    f"Added {user} to dialout (re-login required)"
                )
            else:
                self.failed.append(f"usermod: {ret.stderr[:200]}")
        except Exception as e:
            self.failed.append(f"usermod: {e}")

    def _fix_deprecated(self, result: CheckResult, config_path: Optional[str]):
        if not config_path:
            self.skipped.append(f"{result.message} (no config path)")
            return
        section, old_opt, new_opt = result.fix_data
        try:
            content = Path(config_path).read_text()
            import re

            # Replace old option name with new one in the section
            pattern = re.compile(
                rf"^(\s*){re.escape(old_opt)}(\s*[:=])",
                re.MULTILINE | re.IGNORECASE,
            )
            new_content, count = pattern.subn(
                rf"\g<1>{new_opt}\g<2>", content
            )
            if count > 0:
                Path(config_path).write_text(new_content)
                self.applied.append(
                    f"Renamed {old_opt} → {new_opt} ({count} occurrence(s))"
                )
            else:
                self.skipped.append(f"{old_opt} not found in config")
        except Exception as e:
            self.failed.append(f"Config edit: {e}")

    def _fix_restart_service(self, result: CheckResult):
        svc = result.fix_data
        safe_print(f"  Restarting {svc}...")
        try:
            ret = subprocess.run(
                ["sudo", "systemctl", "restart", svc],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if ret.returncode == 0:
                self.applied.append(f"Restarted {svc}")
            else:
                self.failed.append(f"systemctl restart {svc}: {ret.stderr[:200]}")
        except Exception as e:
            self.failed.append(f"systemctl restart {svc}: {e}")

    def _fix_enable_service(self, result: CheckResult):
        svc = result.fix_data
        safe_print(f"  Enabling {svc}...")
        try:
            ret = subprocess.run(
                ["sudo", "systemctl", "enable", svc],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if ret.returncode == 0:
                self.applied.append(f"Enabled {svc}")
            else:
                self.failed.append(f"systemctl enable {svc}: {ret.stderr[:200]}")
        except Exception as e:
            self.failed.append(f"systemctl enable {svc}: {e}")

    def _fix_mcu(self, result: CheckResult):
        # MCU fixes require interactive input - delegate to mcu_check.py
        self.skipped.append(
            f"{result.message} "
            "(run 'python3 scripts/mcu_check.py --fix' interactively)"
        )


# ---------------------------------------------------------------------------
# Doctor runner
# ---------------------------------------------------------------------------


class DoctorRunner:
    """Orchestrate all checks and produce the final report."""

    def __init__(self, args: argparse.Namespace):
        self.args = args
        self.project_root = PROJECT_ROOT
        self.categories: List[CheckCategory] = []

    def run(self) -> int:
        self._config_path: Optional[str] = None
        banner = f"""
{C.CYAN}{C.BOLD}{'=' * 55}
  Kalico Doctor - Environment Diagnostic
{'=' * 55}{C.RESET}"""
        safe_print(banner)

        # Run each category
        if not self.args.skip_env:
            cat = CheckCategory("Environment")
            checker = EnvironmentCheck(self.project_root)
            cat.results = checker.run()
            self.categories.append(cat)
        else:
            cat = CheckCategory("Environment")
            cat.skipped = True
            cat.skip_reason = "--skip-env"
            self.categories.append(cat)

        if not self.args.skip_config:
            cat = CheckCategory("Configuration")
            checker = ConfigCheck(self.project_root)
            cat.results, self._config_path = checker.run(self.args.config)
            self.categories.append(cat)
        else:
            cat = CheckCategory("Configuration")
            cat.skipped = True
            cat.skip_reason = "--skip-config"
            self.categories.append(cat)
            self._config_path = self.args.config

        if not self.args.skip_mcu:
            cat = CheckCategory("MCU Connectivity")
            checker = MCUCheck(
                self._config_path,
                scan_network=self.args.network is not None,
            )
            cat.results = checker.run()
            self.categories.append(cat)
        else:
            cat = CheckCategory("MCU Connectivity")
            cat.skipped = True
            cat.skip_reason = "--skip-mcu"
            self.categories.append(cat)

        if not self.args.skip_service:
            cat = CheckCategory("Services")
            checker = ServiceCheck()
            cat.results = checker.run()
            self.categories.append(cat)
        else:
            cat = CheckCategory("Services")
            cat.skipped = True
            cat.skip_reason = "--skip-service"
            self.categories.append(cat)

        # Display
        for cat in self.categories:
            safe_print(cat.display())

        # Summary
        self._print_summary()

        # Fix
        if self.args.fix or self.args.dry_fix:
            engine = FixEngine(dry_run=self.args.dry_fix)
            engine.apply_fixes(self.categories, self._config_path)

        # JSON output
        if self.args.json:
            self._print_json()

        # Exit code
        has_errors = any(c.has_errors for c in self.categories)
        return 1 if has_errors else 0

    def _print_summary(self):
        total_ok = sum(c.ok_count for c in self.categories)
        total_warn = sum(c.warn_count for c in self.categories)
        total_err = sum(c.error_count for c in self.categories)
        total_fix = sum(c.fixable_count for c in self.categories)

        safe_print(f"\n{C.CYAN}{C.BOLD}{'=' * 55}")
        safe_print("  Summary")
        safe_print(f"{'=' * 55}{C.RESET}")

        parts = []
        if total_ok:
            parts.append(green(f"{total_ok} passed"))
        if total_warn:
            parts.append(yellow(f"{total_warn} warning(s)"))
        if total_err:
            parts.append(red(f"{total_err} error(s)"))
        if total_fix:
            parts.append(yellow(f"{total_fix} fixable"))
        safe_print(f"  {', '.join(parts)}")

        if total_err > 0 or total_warn > 0:
            if not self.args.fix and not self.args.dry_fix:
                safe_print(
                    f"\n  Run with {bold('--fix')} to auto-fix "
                    f"where possible, or {bold('--dry-fix')} to preview."
                )
        else:
            safe_print(f"\n  {green('All checks passed!')}")

        safe_print("")

    def _print_json(self):
        data = {}
        for cat in self.categories:
            data[cat.name] = {
                "skipped": cat.skipped,
                "ok": cat.ok_count,
                "warnings": cat.warn_count,
                "errors": cat.error_count,
                "fixable": cat.fixable_count,
                "results": [
                    {
                        "severity": r.severity.value,
                        "message": r.message,
                        "detail": r.detail,
                        "fix_id": r.fix_id,
                    }
                    for r in cat.results
                ],
            }
        safe_print(f"\n{json.dumps(data, indent=2)}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Kalico Doctor - Environment diagnostic and auto-repair",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          Run all checks
  %(prog)s --fix                    Auto-fix where possible
  %(prog)s --dry-fix                Preview fixes without applying
  %(prog)s --json                   JSON output
  %(prog)s --skip-mcu               Skip MCU connectivity check
  %(prog)s -c ~/printer.cfg         Specify config file
  %(prog)s -n                       Scan network for MCU devices
        """,
    )
    parser.add_argument(
        "-c", "--config", help="Path to printer.cfg"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Verbose output"
    )
    parser.add_argument(
        "-n",
        "--network",
        nargs="?",
        const="auto",
        default=None,
        help="Scan network for TCP/UDP devices",
    )
    parser.add_argument(
        "-f", "--fix", action="store_true", help="Auto-fix fixable issues"
    )
    parser.add_argument(
        "--dry-fix",
        action="store_true",
        help="Preview fixes without applying",
    )
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--skip-env", action="store_true", help="Skip environment checks")
    parser.add_argument("--skip-config", action="store_true", help="Skip config checks")
    parser.add_argument("--skip-mcu", action="store_true", help="Skip MCU checks")
    parser.add_argument("--skip-service", action="store_true", help="Skip service checks")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    runner = DoctorRunner(args)
    sys.exit(runner.run())


if __name__ == "__main__":
    main()
