#!/usr/bin/env python3
# Tool for uninstalling Kalico plugins from the klippy/plugins/ directory.
# Detects plugin files, removes them, and optionally scans config files
# for leftover [section] references.
#
# Usage:
#   python scripts/uninstall_plugin.py <plugin-name> [plugin-name ...] [options]
#   python scripts/uninstall_plugin.py --all [options]
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from __future__ import annotations

import os
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional

KALICO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = KALICO_ROOT / "klippy" / "plugins"

_CYN = "\033[36m"
_GRN = "\033[32m"
_YEL = "\033[33m"
_RED = "\033[31m"
_BLD = "\033[1m"
_RST = "\033[0m"


# ── Plugin Detection ─────────────────────────────────────────────────────────

def list_plugin_paths(plugin_name: str) -> Optional[list[Path]]:
    """Find all paths associated with a plugin name.
    Returns a list of [file.py] or [dir/] paths, or None if not found."""
    py_file = PLUGINS_DIR / f"{plugin_name}.py"
    pkg_dir = PLUGINS_DIR / plugin_name

    found: list[Path] = []
    if py_file.exists() and py_file.is_file():
        found.append(py_file)
    if pkg_dir.exists() and pkg_dir.is_dir():
        for f in pkg_dir.rglob("*"):
            if f.is_file():
                found.append(f)
        found.append(pkg_dir)
    return found if found else None


def list_installed_plugins() -> list[str]:
    """Return sorted list of installed plugin names."""
    names: set[str] = set()
    for entry in PLUGINS_DIR.iterdir():
        if entry.name == "__init__.py":
            continue
        if entry.is_file() and entry.suffix == ".py":
            names.add(entry.stem)
        elif entry.is_dir():
            if (entry / "__init__.py").exists():
                names.add(entry.name)
            else:
                for f in entry.rglob("*.py"):
                    names.add(entry.name if entry.name else f.stem)
    return sorted(names)


# ── Config Scanning ──────────────────────────────────────────────────────────

def find_config_references(
    plugin_names: list[str], config_path: Optional[str] = None
) -> dict[str, list[tuple[str, int]]]:
    """Scan a config file for [plugin_name] or [plugin_name ...] sections.
    Returns {plugin_name: [(filepath, line_number), ...]}."""
    if config_path is None:
        # Try common config locations
        candidates = [
            KALICO_ROOT / "printer.cfg",
            Path.home() / "printer.cfg",
            Path("/etc/kalico/printer.cfg"),
        ]
        config_path = None
        for c in candidates:
            if c.exists():
                config_path = str(c)
                break
        if config_path is None:
            return {}

    refs: dict[str, list[tuple[str, int]]] = {}
    try:
        lines = Path(config_path).read_text(encoding="utf-8").splitlines()
    except Exception:
        return refs

    for lineno, line in enumerate(lines, 1):
        stripped = line.strip()
        for name in plugin_names:
            if stripped.startswith(f"[{name}]") or stripped.startswith(
                f"[{name} "
            ):
                if name not in refs:
                    refs[name] = []
                refs[name].append((str(config_path), lineno))

    return refs


# ── CLI ──────────────────────────────────────────────────────────────────────

def _section_header(text: str) -> None:
    print(f"\n{_BLD}{'=' * 46}{_RST}")
    print(f" {_BLD}{text}{_RST}")
    print(f"{_BLD}{'=' * 46}{_RST}")


def _ok(msg: str) -> None:
    print(f"  {_GRN}[OK]{_RST} {msg}")


def _warn(msg: str) -> None:
    print(f"  {_YEL}[WARN]{_RST} {msg}")


def _info(label: str, value: str) -> None:
    print(f"  {_CYN}{label:<15}{_RST} {value}")


def main() -> None:
    parser = ArgumentParser(
        description="Uninstall Kalico plugin(s) from klippy/plugins/",
        usage="%(prog)s <plugin-name> [plugin-name ...] [options]",
    )
    parser.add_argument(
        "plugins",
        nargs="*",
        help="Plugin name(s) to uninstall",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Uninstall ALL installed plugins (except __init__.py)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List installed plugins and exit",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Skip confirmation prompt",
    )
    parser.add_argument(
        "--config",
        help="Path to printer.cfg to scan for leftover sections",
        default=None,
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be removed without actually removing",
    )
    args = parser.parse_args()

    # ── List mode ────────────────────────────────────────────────────────
    if args.list:
        installed = list_installed_plugins()
        if not installed:
            print(f"{_YEL}No plugins installed.{_RST}")
            return
        print(f"\n{_BLD}Installed plugins:{_RST}")
        for name in installed:
            paths = list_plugin_paths(name)
            if paths:
                kind = "package" if any(p.is_dir() for p in paths) else "file"
                print(f"  {_CYN}{name:<24}{_RST} ({kind})")
        return

    # ── Resolve plugin list ──────────────────────────────────────────────
    if args.all:
        plugin_names = list_installed_plugins()
        if not plugin_names:
            print(f"{_YEL}No plugins installed to remove.{_RST}")
            return
    elif args.plugins:
        plugin_names = list(args.plugins)
    else:
        parser.print_help()
        print(f"\n{_YEL}Specify plugin name(s), --all, or --list.{_RST}")
        return

    # ── Validate that all requested plugins exist ────────────────────────
    not_found: list[str] = []
    resolved: dict[str, list[Path]] = {}
    for name in plugin_names:
        paths = list_plugin_paths(name)
        if paths:
            resolved[name] = paths
        else:
            not_found.append(name)

    if not_found:
        for name in not_found:
            print(f"  {_RED}Not found:{_RST} {name}")
        if not resolved:
            print(f"\n{_YEL}Hint: use --list to see installed plugins.{_RST}")
            return

    # ── Show what will be removed ────────────────────────────────────────
    _section_header("Plugins to remove")
    for name, paths in resolved.items():
        py_file = PLUGINS_DIR / f"{name}.py"
        pkg_dir = PLUGINS_DIR / name
        if pkg_dir.exists() and pkg_dir.is_dir():
            file_count = sum(1 for p in paths if p.is_file())
            _info(name, f"package ({file_count} files)")
        else:
            _info(name, str(py_file.relative_to(KALICO_ROOT)))

    # ── Scan config for leftover references ──────────────────────────────
    config_refs = find_config_references(list(resolved.keys()), args.config)
    if config_refs:
        print(f"\n  {_YEL}Config references found (remove manually):{_RST}")
        for name, locations in config_refs.items():
            for filepath, lineno in locations:
                print(f"    [{name}] in {filepath}:{lineno}")

    # ── Confirm ──────────────────────────────────────────────────────────
    if args.dry_run:
        print(f"\n{_YEL}Dry run — no files removed.{_RST}")
        if config_refs:
            print(
                f"{_YEL}Remove the config sections above and RESTART to complete.{_RST}"
            )
        return

    if not args.force:
        print(f"\n  {_YEL}Remove the above plugin(s)?{_RST}")
        try:
            answer = input("  Type 'yes' to confirm: ").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{_YEL}Cancelled.{_RST}")
            return
        if answer.lower() != "yes":
            print(f"{_YEL}Cancelled.{_RST}")
            return

    # ── Remove ───────────────────────────────────────────────────────────
    print()
    for name, paths in resolved.items():
        # Remove files first, then directories
        files = [p for p in paths if p.is_file()]
        dirs = [p for p in paths if p.is_dir()]
        for fp in files:
            try:
                os.remove(fp)
                _ok(f"Removed {fp.relative_to(KALICO_ROOT)}")
            except OSError as e:
                print(f"  {_RED}Failed:{_RST} {e}")
        for dp in dirs:
            try:
                remaining = list(dp.rglob("*"))
                if remaining:
                    _warn(
                        f"Directory not empty, skipping: {dp.relative_to(KALICO_ROOT)}"
                    )
                else:
                    dp.rmdir()
                    _ok(f"Removed directory {dp.relative_to(KALICO_ROOT)}")
            except OSError as e:
                print(f"  {_RED}Failed:{_RST} {e}")

    _section_header("Done")
    if config_refs:
        print(f"  {_YEL}Remember to remove config sections:{_RST}")
        for name, locations in config_refs.items():
            for filepath, lineno in locations:
                print(f"    [{name}] in {filepath}:{lineno}")
    print(f"  Send {_CYN}RESTART{_RST} to Kalico to apply.\n")


if __name__ == "__main__":
    main()
