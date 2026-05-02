"""
i18n/en.py — English translations for all generic_arduino tools
=================================================================
To add new strings, add entries below.  Keys beginning with ``cfg.``
belong to ``configure_autoconf.py``; keys beginning with ``bft.``
belong to ``build_flash_tui.py``.

Translator notes:
  - ``[bold]`` / ``[/]`` are Rich/Textual markup tags (keep them).
  - ``\n`` is a newline in Rich ``Static`` renderings.
"""

TRANSLATIONS = {
    # =================================================================
    # ── Shared keys ─────────────────────────────────────────────────
    # =================================================================
    "name": "English",

    # =================================================================
    # ── configure_autoconf.py ───────────────────────────────────────
    # =================================================================

    # ── UI strings ──
    "cfg.title": "generic_arduino Config Tool",
    "cfg.category_panel": " 📁 Categories",
    "cfg.option_panel": " ⚙️  Config Options",
    "cfg.search_placeholder": "Search config items...",
    "cfg.unsaved": " ● Modified",
    "cfg.unchanged": " ● OK",
    "cfg.unknown_board": "Unknown",
    "cfg.search_results": " Search Results",
    "cfg.items": "items",
    "cfg.file": "File",
    "cfg.options": "Options",
    "cfg.target": "Target",
    "cfg.modified": "Modified",
    "cfg.saved": "saved",
    "cfg.save_ok": " items saved to ",
    "cfg.save_title": "Saved",
    "cfg.welcome": "Press [bold]?[/] help | [bold]Tab[/] switch | [bold]Enter[/] edit | [bold]s[/] save | [bold]P[/] presets | [bold]L[/] lang",
    "cfg.welcome_title": "Tip",

    # ── Help Screen ──
    "cfg.help_title": "configure_autoconf.py — Help",
    "cfg.help_keys": "Keys",
    "cfg.help_nav": "Navigate up/down",
    "cfg.help_tab": "Switch panel (Categories ↔ Options)",
    "cfg.help_enter": "Edit selected value",
    "cfg.help_search": "Search / filter",
    "cfg.help_save": "Save changes to file",
    "cfg.help_lang": "Toggle language (EN/CN)",
    "cfg.help_quit": "Quit",
    "cfg.help_help": "Show this help",
    "cfg.help_presets": "Presets (Uno/Mega/Due/Teensy/ESP32)",
    "cfg.help_panels": "Panels",
    "cfg.help_left": "Left: category list",
    "cfg.help_right": "Right: config options in selected category",
    "cfg.help_bottom": "Bottom: status bar",
    "cfg.help_edit_mode": "Edit Mode",
    "cfg.help_edit_desc": "Enter a new value then press Enter to confirm,\nor press Esc to cancel. Changes are staged\ntemporarily — press [bold]s[/] to save to file.",
    "cfg.help_dismiss": "Press any key to dismiss.",

    # ── Edit Screen ──
    "cfg.edit_title": "Edit Config Item",
    "cfg.edit_current": "Current value:",
    "cfg.edit_desc": "Description:",
    "cfg.edit_no_desc": "(no description)",
    "cfg.edit_placeholder": "Enter new value...",
    "cfg.btn_ok": " OK (Enter) ",
    "cfg.btn_cancel": " Cancel (Esc) ",

    # ── Preset Screen ──
    "cfg.presets_title": "Preset Configurations",
    "cfg.presets_prompt": "Enter number (1-5) to apply, Esc to cancel",
    "cfg.presets_updated": "items updated",
    "cfg.presets_uptodate": "already up to date",

    # ── CLI Fallback ──
    "cfg.cli_title": "generic_arduino autoconf.h Config Tool (CLI mode)",
    "cfg.cli_cmd_prompt": "Commands: enter number to edit | s=save | l=lang | q=quit | r=refresh",
    "cfg.cli_state": "State",
    "cfg.cli_unsaved": " (unsaved)",
    "cfg.cli_edit": "Edit",
    "cfg.cli_desc": "Description",
    "cfg.cli_new_val": "New value",
    "cfg.cli_saved": " saved to ",
    "cfg.cli_refreshed": "Reloaded",
    "cfg.cli_confirm_save": "Unsaved changes. Save? (y/N): ",
    "cfg.cli_lang_prompt": "Language (en/zh): ",
    "cfg.cond_mark": " [yellow]⚡[/]",

    # ── Category Display Names ──
    "cat.General": "General",
    "cat.Machine selection": "Machine Selection",
    "cat.Clock": "Clock",
    "cat.MCU Serial (host communication)": "MCU Serial (host)",
    "cat.Debug Serial": "Debug Serial",
    "cat.Memory management": "Memory Management",
    "cat.Feature flags": "Feature Flags",
    "cat.Stepper configuration (set to 0 if not using steppers)": "Stepper Config",
    "cat.MCU identification": "MCU Identification",

    # ── Option Descriptions ──
    "desc.CONFIG_MACH_ARDUINO": "Target MCU architecture: Arduino framework (AVR/ARM/ESP32)",
    "desc.CONFIG_BOARD_DIRECTORY": "HAL header directory name (maps to src/board/ and src/arduino/)",
    "desc.CONFIG_CLOCK_FREQ": "CPU clock frequency in Hz (e.g. 16000000UL for 16 MHz)",
    "desc.CONFIG_MCU_SERIAL_TYPE": "0=Hardware UART (fast, recommended)  1=Software Serial (bit-banged GPIO, flexible but slow)",
    "desc.CONFIG_SERIAL_BAUD": "Baud rate for communication with the host (e.g. Raspberry Pi)",
    "desc.CONFIG_MCU_SERIAL_HW_PORT": "Hardware UART port: 0=Serial, 1=Serial1, 2=Serial2, 3=Serial3",
    "desc.CONFIG_MCU_SERIAL_SW_RX": "Software Serial RX pin (receive from host → Arduino pin number)",
    "desc.CONFIG_MCU_SERIAL_SW_TX": "Software Serial TX pin (transmit to host → Arduino pin number)",
    "desc.CONFIG_SERIAL_BAUD_U2X": "Use double-speed mode on AVR (U2X) for higher baud rate accuracy",
    "desc.CONFIG_DEBUG_SERIAL_PORT": "Debug output port: 0=Serial(USB), 1=SerialUSB(native USB), 2=Disabled(no output)",
    "desc.CONFIG_DEBUG_SERIAL_BAUD": "Baud rate for debug serial output (USB monitor). Common: 115200, 250000",
    "desc.CONFIG_AVR_STACK_SIZE": "Dynamic memory pool / stack size (bytes) for AVR; larger for ARM/ESP32",
    "desc.CONFIG_HAVE_GPIO": "Enable basic digital GPIO read/write support (digitalWrite/digitalRead)",
    "desc.CONFIG_HAVE_GPIO_ADC": "Enable analog input support (analogRead / ADC)",
    "desc.CONFIG_HAVE_GPIO_SPI": "Enable hardware SPI peripheral (if available on target MCU)",
    "desc.CONFIG_HAVE_GPIO_I2C": "Enable hardware I2C peripheral (if available on target MCU)",
    "desc.CONFIG_HAVE_GPIO_HARD_PWM": "Enable hardware PWM support (analogWrite / timer-based PWM)",
    "desc.CONFIG_WANT_GPIO_BITBANGING": "Enable software bit-banging for generic GPIO protocols",
    "desc.CONFIG_WANT_SOFTWARE_SPI": "Build software (bit-bang) SPI implementation",
    "desc.CONFIG_WANT_SOFTWARE_I2C": "Build software (bit-bang) I2C implementation",
    "desc.CONFIG_WANT_ADC": "Build ADC sensor reading support (thermistor, etc.)",
    "desc.CONFIG_WANT_SPI": "Build SPI protocol support for external devices",
    "desc.CONFIG_WANT_I2C": "Build I2C protocol support for external devices",
    "desc.CONFIG_WANT_HARD_PWM": "Build hardware PWM output support (heaters, fans, servos)",
    "desc.CONFIG_WANT_BUTTONS": "Build button/endstop input support (mechanical switches)",
    "desc.CONFIG_WANT_STEPPER": "Enable stepper motor control (requires timer-based step generation)",
    "desc.CONFIG_WANT_ENDSTOPS": "Enable endstop switch support (homing and limit sensing)",
    "desc.CONFIG_INLINE_STEPPER_HACK": "Inline stepper dispatch (disabled for generic build)",
    "desc.CONFIG_HAVE_BOOTLOADER_REQUEST": "Bootloader request support (entering DFU/ST bootloader via command)",
    "desc.CONFIG_MCU_NAME": "Human-readable MCU name reported via the identify protocol",

    # ── Smart Editor Preset Labels ──
    "preset.CONFIG_CLOCK_FREQ": "Clock Frequency (Hz)",
    "preset.CONFIG_SERIAL_BAUD": "Serial Baud Rate",
    "preset.CONFIG_AVR_STACK_SIZE": "Stack / Memory Pool Size (bytes)",
    "preset.CONFIG_SERIAL_BAUD_U2X": "AVR U2X (Double Speed)",
    "preset.CONFIG_MCU_SERIAL_TYPE": "MCU Serial Type",
    "preset.CONFIG_MCU_SERIAL_HW_PORT": "Hardware UART Port",
    "preset.CONFIG_MCU_SERIAL_SW_RX": "Software Serial RX Pin",
    "preset.CONFIG_MCU_SERIAL_SW_TX": "Software Serial TX Pin",
    "preset.CONFIG_DEBUG_SERIAL_PORT": "Debug Serial Port",
    "preset.CONFIG_DEBUG_SERIAL_BAUD": "Debug Serial Baud Rate",
    "preset.CONFIG_HAVE_GPIO": "GPIO Support",
    "preset.CONFIG_HAVE_GPIO_ADC": "Analog Input (ADC)",
    "preset.CONFIG_HAVE_GPIO_SPI": "Hardware SPI",
    "preset.CONFIG_HAVE_GPIO_I2C": "Hardware I2C",
    "preset.CONFIG_HAVE_GPIO_HARD_PWM": "Hardware PWM",
    "preset.CONFIG_WANT_STEPPER": "Stepper Motor Control",
    "preset.CONFIG_WANT_ENDSTOPS": "Endstop / Limit Switches",
    "preset.CONFIG_WANT_ADC": "ADC Sensor Reading",
    "preset.CONFIG_WANT_SPI": "SPI Protocol",
    "preset.CONFIG_WANT_I2C": "I2C Protocol",
    "preset.CONFIG_WANT_HARD_PWM": "Hardware PWM Output",
    "preset.CONFIG_WANT_BUTTONS": "Button / Switch Input",
    "preset.CONFIG_WANT_GPIO_BITBANGING": "GPIO Bit-banging",
    "preset.CONFIG_WANT_SOFTWARE_SPI": "Software (Bit-bang) SPI",
    "preset.CONFIG_WANT_SOFTWARE_I2C": "Software (Bit-bang) I2C",
    "preset.CONFIG_HAVE_BOOTLOADER_REQUEST": "Bootloader Request",
    "preset.CONFIG_INLINE_STEPPER_HACK": "Inline Stepper Dispatch",

    # =================================================================
    # ── build_flash_tui.py ──────────────────────────────────────────
    # =================================================================

    # ── App / Window ──
    "bft.title": "generic_arduino Build & Flash",
    "bft.title_template": "generic_arduino Build & Flash — {}",
    "bft.dependency_error": "Error: Missing Textual dependency",

    # ── Panel Headers ──
    "bft.board_panel": " 🧩 Board Selection",
    "bft.action_panel": " 🎯 Actions",
    "bft.device_section": " 🔌 Serial Devices",
    "bft.log_panel": " 📋 Build / Flash Log",

    # ── Buttons ──
    "bft.btn_build": "📦 Build (b)",
    "bft.btn_upload": "📤 Upload (u)",
    "bft.btn_clean": "🗑️  Clean (c)",
    "bft.btn_devices": "🔄 Refresh Devices (d)",
    "bft.btn_monitor": "📟 Serial Monitor (s)",
    "bft.btn_clear_log": "Clear Log",

    # ── Status Bar ──
    "bft.status_no_board": "Not selected",
    "bft.status_devices": "devices",
    "bft.status_help": "b=Build  u=Upload  c=Clean  d=Refresh  s=Monitor  ?=Help",

    # ── Board Info ──
    "bft.board_arch": "Architecture",
    "bft.board_freq": "Frequency",
    "bft.board_ram": "RAM",

    # ── Log Messages ──
    "bft.log_welcome": "👋 Welcome to generic_arduino Build & Flash!\n",
    "bft.log_hint": "💡 Use ↑/↓ to select board, b to build, u to upload\n",
    "bft.log_scanning": "🔍 Scanning serial devices...\n",
    "bft.log_board_selected": "🧩 Selected board: [bold cyan]{}[/] ([dim]{}[/])\n",
    "bft.log_device_selected": "📌 Selected device: {}\n",
    "bft.log_no_board": "❌ Please select a board first!\n",
    "bft.log_busy": "⏳ Another task is running, please wait...\n",
    "bft.log_build_start": "📦 Building [bold cyan]{}[/] ({}) ...\n",
    "bft.log_build_ok": "\n✅ Build successful! [bold green]{}[/] firmware generated.\n",
    "bft.log_build_hint": "💡 Connect your board and press u to upload.\n",
    "bft.log_build_fail": "\n❌ Build failed (exit code: {})\n",
    "bft.log_firmware_path": "📄 Firmware: {} ({:,} bytes)\n",
    "bft.log_upload_start": "📤 Uploading firmware to [bold cyan]{}[/] ({}) ...\n",
    "bft.log_upload_warn": "⚠️  Ensure the board is connected via USB!\n",
    "bft.log_upload_ok": "\n✅ Upload successful! [bold green]{}[/] flashed.\n",
    "bft.log_upload_hint": "💡 Press s to launch serial monitor.\n",
    "bft.log_upload_fail": "\n❌ Upload failed (exit code: {})\n",
    "bft.log_upload_check": "💡 Please check:\n   1. Board is connected via USB\n   2. Correct drivers installed\n   3. No other program using the serial port\n",
    "bft.log_clean_start": "🗑️  Cleaning [bold cyan]{}[/] ({}) build files...\n",
    "bft.log_clean_ok": "✅ Clean complete!\n",
    "bft.log_clean_fail": "❌ Clean failed (exit code: {})\n",
    "bft.log_device_count": "✅ Found {} serial device(s):\n",
    "bft.log_device_item": "   • {}\n",
    "bft.log_no_devices": "⚠️  No serial devices detected. Connect a board and press d to refresh.\n",
    "bft.log_no_serial_module": "⚠️  Cannot detect serial devices (pyserial not installed)\n",
    "bft.log_install_pyserial": "💡 Install: pip install pyserial\n",
    "bft.log_clear": "📋 Log cleared.\n",
    "bft.log_monitor_start": "📟 Launching serial monitor: [bold]{}[/] @ 115200 baud\n",
    "bft.log_monitor_hint1": "💡 Close the terminal window to stop monitoring.\n",
    "bft.log_monitor_hint2": "💡 Monitor runs in an external terminal.\n",
    "bft.log_monitor_ok": "✅ Serial monitor launched!\n",
    "bft.log_monitor_fail": "❌ Failed to launch serial monitor: {}\n",
    "bft.log_monitor_manual": "💡 Run manually: pio device monitor -b 115200\n",
    "bft.log_pio_not_found": "pio command not found. Please install PlatformIO.",

    # ── Notifications ──
    "bft.notify_no_board": "Please select a board first!",
    "bft.notify_building": "Building {}...",
    "bft.notify_build_done": "{} build successful!",
    "bft.notify_build_fail": "Build failed, check log",
    "bft.notify_uploading": "Uploading to {}...",
    "bft.notify_upload_done": "{} flash successful!",
    "bft.notify_upload_fail": "Upload failed, check log",
    "bft.notify_clean_done": "Clean complete",
    "bft.notify_clean_fail": "Clean failed",
    "bft.notify_build_title": "Build",
    "bft.notify_upload_title": "Upload",
    "bft.notify_clean_title": "Clean",
    "bft.notify_hint_title": "Hint",
    "bft.notify_error_title": "Error",

    # ── Help Screen ──
    "bft.help_title": "generic_arduino Build & Flash — Help",
    "bft.help_keys": "Keys",
    "bft.help_nav": "Navigate lists",
    "bft.help_tab": "Switch panel (Board ↔ Actions ↔ Log)",
    "bft.help_enter": "Select board / confirm",
    "bft.help_b": "Build firmware",
    "bft.help_u": "Upload / flash firmware",
    "bft.help_c": "Clean build artifacts",
    "bft.help_d": "Refresh serial device list",
    "bft.help_s": "Launch serial monitor",
    "bft.help_q": "Quit",
    "bft.help_question": "Show this help",
    "bft.help_panels": "Panels",
    "bft.help_left": "Left: board selection list",
    "bft.help_center": "Center: action buttons & serial devices",
    "bft.help_right": "Right: build / flash log output",
    "bft.help_workflow": "Workflow",
    "bft.help_step1": "1. Select target board (↑/↓ then Enter)",
    "bft.help_step2": "2. Press b to build firmware",
    "bft.help_step3": "3. Connect board via USB, press d to detect",
    "bft.help_step4": "4. Press u to upload / flash",
    "bft.help_step5": "5. Press s to launch serial monitor",
    "bft.help_dismiss": "Press any key to dismiss.",

    # ── Binding Labels ──
    "bft.bind_build": "Build",
    "bft.bind_upload": "Upload",
    "bft.bind_clean": "Clean",
    "bft.bind_devices": "Devices",
    "bft.bind_monitor": "Monitor",
    "bft.bind_quit": "Quit",
    "bft.bind_help": "Help",
    "bft.bind_switch": "Switch Panel",
}
