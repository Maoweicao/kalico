#!/usr/bin/env python3
# Tool for installing Kalico plugins from git repositories or local paths.
# Automatically analyzes plugin structure, detects G-code commands and
# dependencies, and provides configuration hints.
#
# Usage:
#   python scripts/install_plugin.py <git-url> [options]
#   python scripts/install_plugin.py <local-path> --name <module-name>
#
# Copyright (C) 2025  Kalico Contributors
#
# This file may be distributed under the terms of the GNU GPLv3 license.

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from argparse import ArgumentParser
from pathlib import Path
from typing import Optional


KALICO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = KALICO_ROOT / "klippy" / "plugins"

# ANSI color helpers
_CYN = "\033[36m"
_GRN = "\033[32m"
_YEL = "\033[33m"
_RED = "\033[31m"
_BLD = "\033[1m"
_RST = "\033[0m"


# ── AST Analysis ─────────────────────────────────────────────────────────────

class PluginAnalyzer(ast.NodeVisitor):
    """Walk a Python file AST to extract entry points, gcode commands,
    and dependency references."""

    def __init__(self) -> None:
        self.entry_points: dict[str, bool] = {}
        self.gcode_commands: list[tuple[str, Optional[str]]] = []
        self.dependencies: set[str] = set()
        self.has_error = False

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        if node.name in ("load_config", "load_config_prefix", "register_components"):
            self.entry_points[node.name] = True
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        self._check_register_command(node)
        self._check_lookup(node)
        self.generic_visit(node)

    def _check_register_command(self, node: ast.Call) -> None:
        """Detect: gcode.register_command("CMD", ...[, "help"])"""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        if func.attr != "register_command":
            return
        args = node.args
        if len(args) < 1:
            return
        cmd_name = self._extract_str(args[0])
        if cmd_name is None:
            return
        desc = None
        if len(args) >= 3:
            desc = self._extract_str(args[2])
        self.gcode_commands.append((cmd_name, desc))

    def _check_lookup(self, node: ast.Call) -> None:
        """Detect: printer.lookup_object("name") or
           printer.load_object(config, "name")"""
        func = node.func
        if not isinstance(func, ast.Attribute):
            return
        if func.attr not in ("lookup_object", "load_object"):
            return
        args = node.args
        target_arg = 0
        if func.attr == "load_object":
            target_arg = 1  # load_object(config, "name")
        if len(args) <= target_arg:
            return
        name = self._extract_str(args[target_arg])
        if name is not None:
            self.dependencies.add(name)

    @staticmethod
    def _extract_str(node: ast.expr) -> Optional[str]:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        return None


def analyze_file(filepath: Path) -> PluginAnalyzer:
    """Parse a single .py file and return analysis results."""
    analyzer = PluginAnalyzer()
    try:
        source = filepath.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(filepath))
        analyzer.visit(tree)
    except SyntaxError as e:
        analyzer.has_error = True
        print(f"  {_RED}Syntax error in {filepath.name}: {e}{_RST}")
    except Exception as e:
        analyzer.has_error = True
        print(f"  {_RED}Failed to parse {filepath.name}: {e}{_RST}")
    return analyzer


# ── Plugin Discovery ─────────────────────────────────────────────────────────

def find_plugins(source_dir: Path) -> dict[str, list[Path]]:
    """Scan a directory for plugin modules. Returns a mapping of
    module_name → [files].

    Handles these common repository layouts:
        - flat: my_plugin.py
        - flat package: my_plugin/__init__.py + helpers.py
        - nested: src/my_plugin/__init__.py

    The module_name is always the directory containing the entry point(s),
    or the filename without extension for single-file plugins.
    
    Priority: if an __init__.py already declares a package, sibling *.py files
    are treated as supporting files (not separate plugins), even if they
    also define load_config / load_config_prefix.
    """
    plugins: dict[str, list[Path]] = {}
    package_dirs: set[Path] = set()  # parent dirs of discovered packages

    def _add_file(module_name: str, filepath: Path) -> None:
        if module_name not in plugins:
            plugins[module_name] = []
        if filepath not in plugins[module_name]:
            plugins[module_name].append(filepath)

    # Pass 1: find __init__.py with entry points → these define packages
    for py_file in source_dir.rglob("*.py"):
        if py_file.name != "__init__.py":
            continue
        analyzer = analyze_file(py_file)
        if not analyzer.entry_points:
            continue
        # Determine module name from the __init__.py's parent directory
        rel = py_file.relative_to(source_dir)
        if len(rel.parts) >= 2:
            mod_name = rel.parts[-2]
        else:
            mod_name = source_dir.name
        _add_file(mod_name, py_file)
        package_dirs.add(py_file.parent)

    # Pass 2: find standalone .py files outside detected packages
    for py_file in source_dir.rglob("*.py"):
        if py_file.name == "__init__.py":
            continue
        # Skip files that live inside (or at root of) an already-detected package
        py_parent = py_file.parent
        if py_parent in package_dirs:
            _add_file(py_parent.name, py_file)
            continue
        # Check if any ancestor is a package dir
        is_inside_package = False
        for pkg_dir in package_dirs:
            try:
                py_file.relative_to(pkg_dir)
                is_inside_package = True
                break
            except ValueError:
                pass
        if is_inside_package:
            continue
        # Standalone single-file plugin
        analyzer = analyze_file(py_file)
        if analyzer.entry_points:
            rel = py_file.relative_to(source_dir)
            mod_name = rel.stem  # filename without .py
            _add_file(mod_name, py_file)

    # Pass 3: collect remaining supporting files for discovered packages
    # (files in subdirectories of package dirs)
    if package_dirs:
        for py_file in source_dir.rglob("*.py"):
            if py_file.name == "__init__.py":
                continue
            for pkg_dir in package_dirs:
                try:
                    py_file.relative_to(pkg_dir)
                    _add_file(pkg_dir.name, py_file)
                    break
                except ValueError:
                    pass

    return plugins


# ── Installation ─────────────────────────────────────────────────────────────

def install_single_file(
    source: Path, dest: Path, force: bool = False
) -> bool:
    """Copy a single .py file to the plugins directory."""
    if dest.exists() and not force:
        print(f"  {_YEL}File already exists: {dest} (use --force to overwrite){_RST}")
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)
    return True


def install_package(
    files: list[Path],
    source_dir: Path,
    dest_dir: Path,
    force: bool = False,
) -> bool:
    """Copy a directory tree (sub-package) to the plugins directory."""
    if dest_dir.exists() and not force:
        print(f"  {_YEL}Directory already exists: {dest_dir} (use --force to overwrite){_RST}")
        return False
    if dest_dir.exists():
        shutil.rmtree(dest_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)

    for f in files:
        rel = f.relative_to(source_dir)
        if len(rel.parts) > 1:
            target_dir = dest_dir / Path(*rel.parts[:-1])
        else:
            target_dir = dest_dir
        target_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(f, target_dir / f.name)

    # Ensure __init__.py exists (just in case)
    init_py = dest_dir / "__init__.py"
    if not init_py.exists():
        init_py.write_text("# Kalico plugin package\n")
    return True


# ── CLI ──────────────────────────────────────────────────────────────────────

def _section_header(text):
    print(f"\n{_BLD}{'='*46}{_RST}")
    print(f" {_BLD}{text}{_RST}")
    print(f"{_BLD}{'='*46}{_RST}")


def _ok(msg: str) -> None:
    print(f"  {_GRN}[OK]{_RST} {msg}")


def _info(label: str, value: str) -> None:
    print(f"  {_CYN}{label:<15}{_RST} {value}")


def main():
    parser = ArgumentParser(
        description="Install a Kalico plugin from a git repository or local path",
        usage="%(prog)s <url-or-path> [options]",
    )
    parser.add_argument(
        "source",
        help="Git repository URL or local path to the plugin",
    )
    parser.add_argument(
        "--branch", "-b",
        help="Git branch/tag to clone (default: default branch)",
        default=None,
    )
    parser.add_argument(
        "--name", "-n",
        help="Force the installed module name (auto-detected if not given)",
        default=None,
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing plugin of the same name",
    )
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Analyze and report without installing anything",
    )
    args = parser.parse_args()

    source = args.source.strip()
    is_local = source.startswith("/") or source.startswith("./") or source.startswith(
        "." + os.sep
    ) or source.startswith("~") or ":" in source and not source.startswith(
        # Windows path detection
        ("http://", "https://", "git@", "ssh://")
    )
    
    # Refine: if it's just a bare directory name, treat as local
    source_path = Path(source)
    is_local = is_local or source_path.exists()

    # ── Step 1: Obtain source ────────────────────────────────────────────────
    print(f"\n{_CYN}Fetching plugin from {_RST}{source}")

    temp_dir = None
    try:
        if is_local:
            source_path = Path(source).resolve()
            if not source_path.exists():
                print(f"{_RED}Error: Path does not exist: {source}{_RST}")
                sys.exit(1)
            if source_path.is_file():
                # Single file — wrap in a temp dir
                temp_dir = tempfile.mkdtemp(prefix="kalico_plugin_")
                shutil.copy2(source_path, Path(temp_dir) / source_path.name)
                source_root = Path(temp_dir)
                _ok("Using local source")
            else:
                source_root = source_path
                _ok("Using local source")
        else:
            # Clone from git
            temp_dir = tempfile.mkdtemp(prefix="kalico_plugin_")
            clone_cmd = ["git", "clone", "--depth", "1"]
            if args.branch:
                clone_cmd.extend(["--branch", args.branch])
            clone_cmd.extend([source, temp_dir])

            print(f"  Cloning repository...")
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode != 0:
                print(f"{_RED}Error cloning repository:{_RST}")
                print(f"  {result.stderr.strip()}")
                sys.exit(1)
            source_root = Path(temp_dir)
            _ok("Repository cloned")

        # ── Step 2: Find plugins ────────────────────────────────────────────
        print(f"\n  Scanning for plugin modules...")
        plugins = find_plugins(source_root)

        if not plugins:
            print(f"  {_YEL}No plugin entry points found (load_config / load_config_prefix).{_RST}")
            print(f"\n  Looked for .py files with load_config() or load_config_prefix()")
            print(f"  in: {source_root}")
            if is_local:
                print(f"\n  If this is a raw directory, ensure Python files are present.")
            sys.exit(1)

        # ── Step 3: Choose module ───────────────────────────────────────────
        plugin_names = list(plugins.keys())
        if args.name:
            # User is renaming the plugin — use discovered files under new name
            if args.name in plugins:
                source_module = args.name
            else:
                source_module = plugin_names[0]
                print(f"  {_YEL}Note: Using files from '{source_module}',"
                      f" installing as '{args.name}'{_RST}")
            module_name = args.name
            files = plugins[source_module]
        elif len(plugin_names) == 1:
            module_name = plugin_names[0]
            files = plugins[module_name]
        else:
            # Multiple found — pick the one matching the repo/input name
            # or just use the first and warn
            if source_path.name in plugins:
                module_name = source_path.name
            else:
                module_name = plugin_names[0]
            print(f"  {_YEL}Multiple modules found: {plugin_names}")
            print(f"  {_YEL}Using: {module_name} (use --name to choose){_RST}")
            files = plugins[module_name]
        is_package = len(files) > 1 or (
            len(files) == 1 and files[0].name == "__init__.py"
        )

        # ── Step 4: Analyze ─────────────────────────────────────────────────
        print(f"\n  Analyzing plugin...")

        # Aggregate analysis across all files
        all_entry_points: dict[str, bool] = {}
        all_commands: list[tuple[str, Optional[str]]] = []
        all_deps: set[str] = set()

        for f in files:
            analyzer = analyze_file(f)
            all_entry_points.update(analyzer.entry_points)
            all_commands.extend(analyzer.gcode_commands)
            all_deps.update(analyzer.dependencies)

        if all_entry_points:
            entries = [k for k in sorted(all_entry_points)]
            _info("Entry points", ", ".join(entries))
        if all_commands:
            _info("Commands", ", ".join(c[0] for c in all_commands))
        if all_deps:
            _info("Dependencies", ", ".join(sorted(all_deps)))

        # ── Step 5: Check for extras/ migration hints ────────────────────────
        extras_refs = _check_extras_references(source_root, files)
        if extras_refs:
            print(f"\n  {_YEL}Note: This plugin references the following extras/ modules:{_RST}")
            for ext in extras_refs:
                print(f"    - klippy.extras.{ext}")
            print(f"  {_YEL}These imports are compatible with plugins/ — no changes needed.{_RST}")

        # ── Step 6: Install ─────────────────────────────────────────────────
        dest = PLUGINS_DIR / module_name
        dest_file = PLUGINS_DIR / f"{module_name}.py"

        if args.dry_run:
            _section_header("Dry Run — No files installed")
            if is_package:
                print(f"  Would create: {PLUGINS_DIR / module_name}/")
                for f in files:
                    rel = f.relative_to(source_root)
                    print(f"    {rel}")
            else:
                print(f"  Would create: {dest_file}")
            print(f"\n  Detected {len(all_commands)} G-code command(s), {len(all_deps)} dependency(ies)")
            _print_commands_section(all_commands)
            return

        print(f"\n  Installing to klippy/plugins/...")

        if is_package:
            ok = install_package(files, source_root, dest, force=args.force)
            install_path = dest
        else:
            source_file = files[0]
            ok = install_single_file(source_file, dest_file, force=args.force)
            install_path = dest_file

        if not ok:
            print(f"{_RED}Installation aborted (use --force to overwrite).{_RST}")
            sys.exit(1)

        _ok("Installed")

        # ── Step 7: Friendly report ─────────────────────────────────────────
        _section_header(f"Plugin installed: {module_name}")
        _info("Source", source)
        _info("Install path", str(install_path.relative_to(KALICO_ROOT)))

        entry_str = ", ".join(sorted(all_entry_points)) if all_entry_points else "none"
        _info("Entry points", entry_str)

        _print_commands_section(all_commands)

        if all_deps:
            print(f"\n  {_BLD}Dependencies{_RST} (ensure these are configured):")
            for dep in sorted(all_deps):
                print(f"    {_CYN}→{_RST} {dep}")

        print(f"\n  {_BLD}Config section{_RST} (add to printer.cfg):")
        print(f"    {_GRN}[{module_name}]{_RST}")

        print(f"\n  {_BLD}To activate:{_RST} send {_CYN}RESTART{_RST} to Kalico")
        print(f"{_BLD}{'='*46}{_RST}\n")

    finally:
        if temp_dir and os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir, ignore_errors=True)


def _check_extras_references(source_root, files):
    """Look for references to klippy.extras modules in plugin files."""
    extras_refs: set[str] = set()
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            for match in re.finditer(
                r'(?:from|import)\s+klippy\.extras\.(\w+)', content
            ):
                extras_refs.add(match.group(1))
        except Exception:
            pass
    return sorted(extras_refs)


def _print_commands_section(commands):
    if not commands:
        return
    print(f"\n  {_BLD}Available G-code commands:{_RST}")
    for cmd_name, desc in commands:
        if desc:
            print(f"    {_CYN}{cmd_name:<22}{_RST} {desc}")
        else:
            print(f"    {_CYN}{cmd_name}{_RST}")


if __name__ == "__main__":
    main()
