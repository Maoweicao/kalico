#!/usr/bin/env python3
"""
build_flash_tui.py — TUI 编译 & 刷写工具 for generic_arduino
=============================================================================
终端可视化界面，用于编译固件并刷写到选中的设备。

用法:
    pip install -r tools/requirements.txt
    python tools/build_flash_tui.py

快捷键:
    ↑/↓           导航选项
    Tab           切换面板
    Enter         执行选中操作 / 选择板子
    b             编译固件
    u             上传刷写
    c             清理构建
    d             刷新设备列表
    s             启动串口监视器
    q / Esc       退出
    ?             显示帮助
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
from pathlib import Path
from typing import List, Optional

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent  # generic_arduino/

# ---------------------------------------------------------------------------
# Internationalisation (i18n) — loaded from tools/i18n/
# ---------------------------------------------------------------------------

_tools_dir = SCRIPT_DIR
if str(_tools_dir) not in sys.path:
    sys.path.insert(0, str(_tools_dir))

from i18n import _, set_language, get_language, toggle_language

# ---------------------------------------------------------------------------
# Board definitions
# ---------------------------------------------------------------------------

BOARDS = {
    "mega2560": {
        "name": "Arduino Mega 2560",
        "name_zh": "Arduino Mega 2560",
        "arch": "AVR (ATmega2560)",
    },
    "uno": {
        "name": "Arduino Uno",
        "name_zh": "Arduino Uno",
        "arch": "AVR (ATmega328P)",
    },
    "due": {
        "name": "Arduino Due",
        "name_zh": "Arduino Due",
        "arch": "ARM Cortex-M3 (ATSAM3X8E)",
    },
    "teensy40": {
        "name": "Teensy 4.0",
        "name_zh": "Teensy 4.0",
        "arch": "ARM Cortex-M7 (IMXRT1062)",
    },
    "esp32dev": {
        "name": "ESP32 DevKit",
        "name_zh": "ESP32 DevKit",
        "arch": "Xtensa LX6",
    },
}

BOARD_LIST = list(BOARDS.keys())


def _board_display_name(env: str) -> str:
    b = BOARDS[env]
    return b.get("name_zh", b["name"]) if get_language() == "zh" else b["name"]

# ---------------------------------------------------------------------------
# Textual TUI
# ---------------------------------------------------------------------------

try:
    from textual.app import App, ComposeResult
    from textual.containers import Horizontal, Vertical, VerticalScroll
    from textual.widgets import (
        Header, Footer, Static, ListView, ListItem, Label,
        Button, RichLog, Input, RadioSet, RadioButton,
    )
    from textual.screen import ModalScreen
    from textual.binding import Binding
    from rich.text import Text
    TEXTUAL_AVAILABLE = True
except ImportError as e:
    TEXTUAL_AVAILABLE = False
    IMPORT_ERROR = str(e)


class HelpScreen(ModalScreen):

    def compose(self) -> ComposeResult:
        yield Static(
            "\n"
            f"  [bold yellow]{_('bft.help_title')}[/]\n"
            "  ───────────────────────────────────────────────\n"
            "  \n"
            f"  [bold]{_('bft.help_keys')}[/]\n"
            f"  [dim]  ↑/↓[/]        {_('bft.help_nav')}\n"
            f"  [dim]  Tab[/]        {_('bft.help_tab')}\n"
            f"  [dim]  Enter[/]      {_('bft.help_enter')}\n"
            f"  [dim]  b[/]          {_('bft.help_b')}\n"
            f"  [dim]  u[/]          {_('bft.help_u')}\n"
            f"  [dim]  c[/]          {_('bft.help_c')}\n"
            f"  [dim]  d[/]          {_('bft.help_d')}\n"
            f"  [dim]  s[/]          {_('bft.help_s')}\n"
            f"  [dim]  q / Esc[/]    {_('bft.help_q')}\n"
            f"  [dim]  ?[/]          {_('bft.help_question')}\n"
            "  \n"
            f"  [bold]{_('bft.help_panels')}[/]\n"
            f"  [dim]  {_('bft.help_left')}[/]\n"
            f"  [dim]  {_('bft.help_center')}[/]\n"
            f"  [dim]  {_('bft.help_right')}[/]\n"
            "  \n"
            f"  [bold]{_('bft.help_workflow')}[/]\n"
            f"  [dim]  {_('bft.help_step1')}[/]\n"
            f"  [dim]  {_('bft.help_step2')}[/]\n"
            f"  [dim]  {_('bft.help_step3')}[/]\n"
            f"  [dim]  {_('bft.help_step4')}[/]\n"
            f"  [dim]  {_('bft.help_step5')}[/]\n"
            "  \n"
            f"  {_('bft.help_dismiss')}"
        )

    def on_key(self, event):
        self.dismiss()


class BoardItem(ListItem):

    def __init__(self, env_name: str, **kwargs):
        super().__init__(**kwargs)
        self.env_name = env_name

    def compose(self) -> ComposeResult:
        board = BOARDS[self.env_name]
        name = _board_display_name(self.env_name)
        arch = board["arch"]
        yield Static(
            f"  [bold cyan]{name:<24}[/]\n"
            f"  [dim]{arch}[/]"
        )


# ── Main App ────────────────────────────────────────────────────────────────

class BuildFlashApp(App):

    TITLE = _("bft.title")
    CSS = """
    Screen { background: $surface; }
    #main-container { height: 100%; }
    #board-panel {
        width: 30; min-width: 26; border: solid $primary;
        border-title-color: $text; background: $panel; margin: 0 1 0 0;
    }
    #board-panel > Static {
        padding: 0 1; text-style: bold; background: $accent; color: $text;
    }
    #board-list { height: 1fr; }
    #board-info {
        height: 4; padding: 0 1; background: $boost; border-top: solid $primary;
    }
    #action-panel {
        width: 26; min-width: 22; border: solid $success;
        border-title-color: $text; background: $panel; margin: 0 1 0 0;
    }
    #action-panel > Static {
        padding: 0 1; text-style: bold; background: $accent; color: $text;
    }
    #action-buttons { height: auto; padding: 0 1; }
    #action-buttons Button { width: 100%; margin: 0 0 1 0; }
    #device-section {
        height: 1fr; border-top: solid $secondary; padding: 0 0;
    }
    #device-section > Static {
        padding: 0 1; text-style: bold; background: $boost; color: $text;
    }
    #device-list { height: 1fr; }
    #device-status {
        height: 3; padding: 0 1; background: $boost; border-top: solid $secondary;
    }
    #log-panel {
        width: 1fr; border: solid $warning;
        border-title-color: $text; background: $panel;
    }
    #log-panel > Static {
        padding: 0 1; text-style: bold; background: $accent; color: $text;
    }
    #log-output { height: 1fr; }
    #log-buttons {
        height: 3; padding: 0 1; align: center middle;
        border-top: solid $warning;
    }
    #log-buttons Button { margin: 0 1; }
    #status-bar {
        height: 1; background: $boost; padding: 0 1;
        content-align: left middle;
    }
    ListView { border: none; }
    ListItem { padding: 0 0; }
    """

    BINDINGS = [
        Binding("b", "build", _("bft.bind_build"), show=True),
        Binding("u", "upload", _("bft.bind_upload"), show=True),
        Binding("c", "clean", _("bft.bind_clean"), show=True),
        Binding("d", "refresh_devices", _("bft.bind_devices"), show=True),
        Binding("s", "serial_monitor", _("bft.bind_monitor"), show=True),
        Binding("l", "toggle_lang", "Lang", show=True),
        Binding("q", "quit", _("bft.bind_quit"), show=True),
        Binding("question_mark", "show_help", _("bft.bind_help"), show=True),
        Binding("tab", "focus_next_pane", _("bft.bind_switch"), show=True, priority=True),
    ]

    def __init__(self):
        super().__init__()
        self.selected_board: Optional[str] = None
        self.devices: List[str] = []
        self._busy_count: int = 0
        self._busy_lock: threading.Lock = threading.Lock()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal(id="main-container"):
            with Vertical(id="board-panel"):
                yield Static(_("bft.board_panel"))
                yield ListView(*[BoardItem(env) for env in BOARD_LIST], id="board-list")
                yield Static("", id="board-info")

            with Vertical(id="action-panel"):
                yield Static(_("bft.action_panel"))
                with Vertical(id="action-buttons"):
                    yield Button(_("bft.btn_build"), variant="primary", id="btn-build")
                    yield Button(_("bft.btn_upload"), variant="success", id="btn-upload")
                    yield Button(_("bft.btn_clean"), variant="default", id="btn-clean")
                    yield Button(_("bft.btn_devices"), variant="default", id="btn-devices")
                    yield Button(_("bft.btn_monitor"), variant="warning", id="btn-monitor")
                with Vertical(id="device-section"):
                    yield Static(_("bft.device_section"))
                    yield ListView(id="device-list")
                    yield Static("", id="device-status")

            with Vertical(id="log-panel"):
                yield Static(_("bft.log_panel"))
                yield RichLog(id="log-output", highlight=True, markup=True, wrap=True)
                with Horizontal(id="log-buttons"):
                    yield Button(_("bft.btn_clear_log"), variant="default", id="btn-clear-log")

        yield Static(id="status-bar")
        yield Footer()

    def on_mount(self) -> None:
        board_list = self.query_one("#board-list", ListView)
        if board_list.children:
            board_list.index = 0
            self._select_board(0)
        self._update_status()
        self.call_after_refresh(self._focus_board_list)
        self._log_info(_("bft.log_welcome"))
        self._log_info(_("bft.log_hint"))
        self._log_info(_("bft.log_scanning"))
        self._refresh_devices_async()

    def _focus_board_list(self) -> None:
        self.set_focus(self.query_one("#board-list", ListView))

    def _update_status(self) -> None:
        bname = _board_display_name(self.selected_board) if self.selected_board else _("bft.status_no_board")
        devs = len(self.devices)
        s = self.query_one("#status-bar", Static)
        s.update(
            f" 🧩 {bname}  |  🔌 {devs} {_('bft.status_devices')}"
            f"  |  [dim]{_('bft.status_help')}[/]"
        )

    def _update_board_info(self) -> None:
        info = self.query_one("#board-info", Static)
        if not self.selected_board:
            info.update("")
            return
        b = BOARDS[self.selected_board]
        name = _board_display_name(self.selected_board)
        info.update(
            f"[bold]{name}[/]\n"
            f"[dim]{_('bft.board_arch')}: {b['arch']}[/]"
        )

    # ── Logging ─────────────────────────────────────────────────────────────

    def _log(self, text: str, style: str = "") -> None:
        self.query_one("#log-output", RichLog).write(Text(text, style=style))

    def _log_info(self, text: str) -> None:
        self._log(text, "dim white")

    def _log_ok(self, text: str) -> None:
        self._log(text, "bold green")

    def _log_error(self, text: str) -> None:
        self._log(text, "bold red")

    def _log_warn(self, text: str) -> None:
        self._log(text, "bold yellow")

    def _log_cmd(self, text: str) -> None:
        self._log(text, "cyan")

    def _log_build_output(self, line: str) -> None:
        lo = line.lower()
        if "error:" in lo or "failed" in lo:
            self._log(line, "red")
        elif "warning:" in lo:
            self._log(line, "yellow")
        elif "success" in lo or "=====" in line:
            self._log(line, "green")
        else:
            self._log(line, "")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        if event.list_view.id == "board-list":
            idx = event.list_view.index
            if idx is not None:
                self._select_board(idx)
        elif event.list_view.id == "device-list":
            item = event.item
            if hasattr(item, "device_info"):
                self._log_info(_("bft.log_device_selected").format(item.device_info))

    def _select_board(self, idx: int) -> None:
        if idx < 0 or idx >= len(BOARD_LIST):
            return
        env = BOARD_LIST[idx]
        self.selected_board = env
        self._update_board_info()
        self._update_status()
        dname = _board_display_name(env)
        self._log_info(_("bft.log_board_selected").format(dname, env))
        self.title = _("bft.title_template").format(dname)

    # ── Device Detection ────────────────────────────────────────────────────

    def _parse_pio_device_list(self, output: str) -> List[str]:
        """解析 pio device list 输出"""
        devices = []
        for line in output.splitlines():
            # 匹配串口设备行
            m = re.match(r'^([/\\.\w]+)\s+', line)
            if m:
                port = m.group(1).strip()
                if port and not port.startswith("---"):
                    devices.append(line.strip())
        if not devices:
            # Windows: 尝试解析 COM 端口
            for line in output.splitlines():
                if "COM" in line.upper() or line.strip().startswith("/"):
                    devices.append(line.strip())
        return devices

    def _refresh_devices_async(self) -> None:
        """异步刷新设备列表"""
        self._log_info("🔍 正在扫描串口设备...\n")
        self._run_pio_command_async(["device", "list"], self._on_devices_result)

    def _on_devices_result(self, returncode: int, stdout: str, stderr: str) -> None:
        dev_list = self.query_one("#device-list", ListView)
        dev_list.clear()
        status = self.query_one("#device-status", Static)
        if returncode != 0:
            self._detect_devices_fallback()
            return
        devices = self._parse_pio_device_list(stdout)
        self.devices = devices
        if not devices:
            status.update("[dim]⚠️  " + _("bft.log_no_devices").strip() + "[/]")
            self._log_warn(_("bft.log_no_devices"))
            return
        for dev in devices:
            item = ListItem(Static(f"  {dev}"))
            item.device_info = dev
            dev_list.append(item)
        status.update(f"[green]✅ {len(devices)} {_('bft.status_devices')}[/]")
        self._log_ok(_("bft.log_device_count").format(len(devices)))
        for d in devices:
            self._log_info(_("bft.log_device_item").format(d))
        self._update_status()

    def _detect_devices_fallback(self) -> None:
        try:
            import serial.tools.list_ports
            ports = serial.tools.list_ports.comports()
            dev_list = self.query_one("#device-list", ListView)
            dev_list.clear()
            status = self.query_one("#device-status", Static)
            devices = []
            for p in ports:
                desc = f"{p.device}  —  {p.description}" if p.description else p.device
                devices.append(desc)
                item = ListItem(Static(f"  {desc}"))
                item.device_info = p.device
                dev_list.append(item)
            self.devices = devices
            if devices:
                status.update(f"[green]✅ {len(devices)} {_('bft.status_devices')}[/]")
                self._log_ok(_("bft.log_device_count").format(len(devices)))
                for d in devices:
                    self._log_info(_("bft.log_device_item").format(d))
            else:
                status.update("[dim]⚠️  " + _("bft.log_no_devices").strip() + "[/]")
                self._log_warn(_("bft.log_no_devices"))
            self._update_status()
        except ImportError:
            self._log_warn(_("bft.log_no_serial_module"))
            self._log_info(_("bft.log_install_pyserial"))

    # ── Build / Upload / Clean (异步进程管理) ──────────────────────────────

    def _run_pio_command_async(self, args: List[str], callback, cwd: Optional[Path] = None) -> None:
        cmd = ["pio"] + args
        with self._busy_lock:
            self._busy_count += 1

        def run():
            try:
                proc = subprocess.Popen(
                    cmd, cwd=cwd or PROJECT_DIR,
                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, encoding="utf-8", errors="replace",
                )
                stdout, _ = proc.communicate()
                result = (proc.returncode, stdout, "")
            except FileNotFoundError:
                result = (-1, "", _("bft.log_pio_not_found"))
            except Exception as e:
                result = (-1, "", str(e))
            finally:
                with self._busy_lock:
                    self._busy_count -= 1
                self.call_from_thread(callback, *result)

        threading.Thread(target=run, daemon=True).start()

    def _is_busy(self) -> bool:
        with self._busy_lock:
            return self._busy_count > 0

    def _check_board(self) -> bool:
        if not self.selected_board:
            self._log_error(_("bft.log_no_board"))
            self.notify(_("bft.notify_no_board"), title=_("bft.notify_hint_title"), severity="warning", timeout=3)
            return False
        return True

    def action_build(self) -> None:
        if not self._check_board() or self._is_busy():
            if self._is_busy(): self._log_warn(_("bft.log_busy"))
            return
        env = self.selected_board
        dname = _board_display_name(env)
        self._log_cmd(_("bft.log_build_start").format(dname, env))
        self.notify(_("bft.notify_building").format(dname), title=_("bft.notify_build_title"), severity="information", timeout=2)
        self._run_pio_command_async(["run", "-e", env], self._on_build_done)

    def _on_build_done(self, returncode: int, stdout: str, stderr: str) -> None:
        for line in stdout.splitlines():
            self._log_build_output(line + "\n")
        if stderr:
            for line in stderr.splitlines():
                self._log_build_output(line + "\n")
        dname = _board_display_name(self.selected_board)
        if returncode == 0:
            self._log_ok(_("bft.log_build_ok").format(dname))
            self._log_info(_("bft.log_build_hint"))
            self.notify(_("bft.notify_build_done").format(dname), title=_("bft.notify_build_title"), severity="information", timeout=3)
            env = self.selected_board
            for ext in [".hex", ".bin"]:
                fw = PROJECT_DIR / ".pio" / "build" / env / ("firmware" + ext)
                if fw.exists():
                    self._log_info(_("bft.log_firmware_path").format(str(fw), fw.stat().st_size))
                    break
        else:
            self._log_error(_("bft.log_build_fail").format(returncode))
            self.notify(_("bft.notify_build_fail"), title=_("bft.notify_error_title"), severity="error", timeout=5)
        self._update_status()

    def action_upload(self) -> None:
        if not self._check_board() or self._is_busy():
            if self._is_busy(): self._log_warn(_("bft.log_busy"))
            return
        env = self.selected_board
        dname = _board_display_name(env)
        self._log_cmd(_("bft.log_upload_start").format(dname, env))
        self._log_info(_("bft.log_upload_warn"))
        self.notify(_("bft.notify_uploading").format(dname), title=_("bft.notify_upload_title"), severity="information", timeout=5)
        self._run_pio_command_async(["run", "-e", env, "-t", "upload"], self._on_upload_done)

    def _on_upload_done(self, returncode: int, stdout: str, stderr: str) -> None:
        for line in stdout.splitlines():
            self._log_build_output(line + "\n")
        if stderr:
            for line in stderr.splitlines():
                self._log_build_output(line + "\n")
        dname = _board_display_name(self.selected_board)
        if returncode == 0:
            self._log_ok(_("bft.log_upload_ok").format(dname))
            self._log_info(_("bft.log_upload_hint"))
            self.notify(_("bft.notify_upload_done").format(dname), title=_("bft.notify_upload_title"), severity="information", timeout=3)
        else:
            self._log_error(_("bft.log_upload_fail").format(returncode))
            self._log_info(_("bft.log_upload_check"))
            self.notify(_("bft.notify_upload_fail"), title=_("bft.notify_error_title"), severity="error", timeout=5)
        self._update_status()

    def action_clean(self) -> None:
        if not self._check_board() or self._is_busy():
            if self._is_busy(): self._log_warn(_("bft.log_busy"))
            return
        env = self.selected_board
        dname = _board_display_name(env)
        self._log_cmd(_("bft.log_clean_start").format(dname, env))
        self._run_pio_command_async(["run", "-e", env, "-t", "clean"], self._on_clean_done)

    def _on_clean_done(self, returncode: int, stdout: str, stderr: str) -> None:
        for line in stdout.splitlines():
            self._log_build_output(line + "\n")
        if returncode == 0:
            self._log_ok(_("bft.log_clean_ok"))
            self.notify(_("bft.notify_clean_done"), title=_("bft.notify_clean_title"), severity="information", timeout=2)
        else:
            self._log_error(_("bft.log_clean_fail").format(returncode))
            self.notify(_("bft.notify_clean_fail"), title=_("bft.notify_error_title"), severity="error", timeout=3)
        self._update_status()

    def action_refresh_devices(self) -> None:
        if self._is_busy():
            self._log_warn(_("bft.log_busy"))
            return
        self._refresh_devices_async()

    def action_serial_monitor(self) -> None:
        if not self._check_board() or not self.devices:
            if not self.devices: self._log_warn(_("bft.log_no_devices"))
            return
        first_dev = self.devices[0]
        port = first_dev.split()[0].split("—")[0].strip()
        self._log_cmd(_("bft.log_monitor_start").format(port))
        self._log_info(_("bft.log_monitor_hint2"))
        try:
            if os.name == "nt":
                subprocess.Popen(["start", "cmd", "/k", f"pio device monitor -b 115200 --port {port}"], cwd=PROJECT_DIR, shell=True)
            else:
                subprocess.Popen(["x-terminal-emulator", "-e", f"pio device monitor -b 115200 --port {port}"], cwd=PROJECT_DIR)
            self._log_ok(_("bft.log_monitor_ok"))
        except Exception as e:
            self._log_error(_("bft.log_monitor_fail").format(e))
            self._log_info(_("bft.log_monitor_manual"))

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_toggle_lang(self) -> None:
        new_lang = toggle_language()
        self.TITLE = _("bft.title")
        self.refresh_bindings()
        self._rebuild_ui()
        self._update_status()

    def _rebuild_ui(self) -> None:
        self.query_one("#board-panel > Static").update(_("bft.board_panel"))
        self.query_one("#action-panel > Static").update(_("bft.action_panel"))
        self.query_one("#device-section > Static").update(_("bft.device_section"))
        self.query_one("#log-panel > Static").update(_("bft.log_panel"))
        self._update_board_info()

    def action_focus_next_pane(self) -> None:
        board_list = self.query_one("#board-list", ListView)
        device_list = self.query_one("#device-list", ListView)
        log_output = self.query_one("#log-output", RichLog)
        focused = self.focused
        if focused == board_list:
            self.set_focus(device_list)
        elif focused == device_list:
            self.set_focus(log_output)
        else:
            self.set_focus(board_list)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        btn_id = event.button.id
        if btn_id == "btn-build": self.action_build()
        elif btn_id == "btn-upload": self.action_upload()
        elif btn_id == "btn-clean": self.action_clean()
        elif btn_id == "btn-devices": self.action_refresh_devices()
        elif btn_id == "btn-monitor": self.action_serial_monitor()
        elif btn_id == "btn-clear-log":
            self.query_one("#log-output", RichLog).clear()
            self._log_info(_("bft.log_clear"))


def main():
    if not TEXTUAL_AVAILABLE:
        print("=" * 60)
        print(f"  {_('bft.dependency_error')}")
        print(f"  {IMPORT_ERROR}")
        print()
        print(f"  pip install -r {SCRIPT_DIR / 'requirements.txt'}")
        print("=" * 60)
        sys.exit(1)
    BuildFlashApp().run()


if __name__ == "__main__":
    main()
