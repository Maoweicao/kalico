"""
i18n/zh.py — 简体中文翻译 for all generic_arduino tools
=============================================================
要添加新的字符串，请在本文件追加翻译条目。
以 ``cfg.`` 开头的 key 属于 ``configure_autoconf.py``；
以 ``bft.`` 开头的 key 属于 ``build_flash_tui.py``。

译者注意：
  - ``[bold]`` / ``[/]`` 是 Rich/Textual 标记（请保留）。
  - ``\n`` 是 Rich ``Static`` 渲染中的换行符。
"""

TRANSLATIONS = {
    # =================================================================
    # ── 共享键 ─────────────────────────────────────────────────────
    # =================================================================
    "name": "简体中文",

    # =================================================================
    # ── configure_autoconf.py ───────────────────────────────────────
    # =================================================================

    # ── UI 字符串 ──
    "cfg.title": "generic_arduino 配置工具",
    "cfg.category_panel": " 📁 分类",
    "cfg.option_panel": " ⚙️  配置选项",
    "cfg.search_placeholder": "搜索配置项...",
    "cfg.unsaved": " ● 已修改",
    "cfg.unchanged": " ● 未修改",
    "cfg.unknown_board": "未知",
    "cfg.search_results": " 🔍 搜索结果",
    "cfg.items": "项",
    "cfg.file": "文件",
    "cfg.options": "选项",
    "cfg.target": "目标板",
    "cfg.modified": "已修改",
    "cfg.saved": "已保存",
    "cfg.save_ok": " 个配置项已保存到 ",
    "cfg.save_title": "保存成功",
    "cfg.welcome": "按 [bold]?[/] 帮助 | [bold]Tab[/] 切换 | [bold]Enter[/] 编辑 | [bold]s[/] 保存 | [bold]P[/] 预制 | [bold]L[/] 语言",
    "cfg.welcome_title": "提示",

    # ── 帮助界面 ──
    "cfg.help_title": "configure_autoconf.py — 帮助",
    "cfg.help_keys": "快捷键",
    "cfg.help_nav": "导航选项列表",
    "cfg.help_tab": "切换面板（分类 ↔ 选项）",
    "cfg.help_enter": "编辑选中的配置值",
    "cfg.help_search": "搜索过滤",
    "cfg.help_save": "保存修改到文件",
    "cfg.help_lang": "切换语言 (EN/CN)",
    "cfg.help_quit": "退出",
    "cfg.help_help": "显示此帮助",
    "cfg.help_presets": "预制配置 (Uno/Mega/Due/Teensy/ESP32)",
    "cfg.help_panels": "面板说明",
    "cfg.help_left": "左栏: 配置分类列表",
    "cfg.help_right": "右栏: 当前分类下的配置选项",
    "cfg.help_bottom": "底部: 状态栏与操作提示",
    "cfg.help_edit_mode": "编辑模式",
    "cfg.help_edit_desc": "输入新值后按 Enter 确认，\n或按 Esc 取消。修改暂存于内存，\n按 [bold]s[/] 保存到文件。",
    "cfg.help_dismiss": "按任意键关闭",

    # ── 编辑界面 ──
    "cfg.edit_title": "编辑配置项",
    "cfg.edit_current": "当前值:",
    "cfg.edit_desc": "说明:",
    "cfg.edit_no_desc": "(无描述)",
    "cfg.edit_placeholder": "输入新值...",
    "cfg.btn_ok": "  确定 (Enter)  ",
    "cfg.btn_cancel": "  取消 (Esc)    ",

    # ── 预制配置界面 ──
    "cfg.presets_title": "预制配置",
    "cfg.presets_prompt": "输入编号 (1-5) 应用配置, Esc 取消",
    "cfg.presets_updated": "项已更新",
    "cfg.presets_uptodate": "配置已是最新",

    # ── 命令行回退 ──
    "cfg.cli_title": "generic_arduino autoconf.h 配置工具 (命令行模式)",
    "cfg.cli_cmd_prompt": "命令: 输入编号编辑值 | s=保存 | l=切换语言 | q=退出 | r=刷新",
    "cfg.cli_state": "状态",
    "cfg.cli_unsaved": " (未保存)",
    "cfg.cli_edit": "编辑",
    "cfg.cli_desc": "描述",
    "cfg.cli_new_val": "新值",
    "cfg.cli_saved": " 已保存到 ",
    "cfg.cli_refreshed": "已刷新",
    "cfg.cli_confirm_save": "有未保存的修改，是否保存？(y/N): ",
    "cfg.cli_lang_prompt": "语言 (en/zh): ",
    "cfg.cond_mark": " [yellow]⚡[/]",

    # ── 分类显示名称 ──
    "cat.General": "通用",
    "cat.Machine selection": "机器选择",
    "cat.Clock": "时钟",
    "cat.MCU Serial (host communication)": "MCU 串口（主机通信）",
    "cat.Debug Serial": "调试串口",
    "cat.Memory management": "内存管理",
    "cat.Feature flags": "功能开关",
    "cat.Stepper configuration (set to 0 if not using steppers)": "步进电机配置",
    "cat.MCU identification": "MCU 标识",

    # ── 选项描述 ──
    "desc.CONFIG_MACH_ARDUINO": "目标 MCU 架构：Arduino 框架 (AVR/ARM/ESP32)",
    "desc.CONFIG_BOARD_DIRECTORY": "HAL 头文件目录名 (映射到 src/board/ 和 src/arduino/)",
    "desc.CONFIG_CLOCK_FREQ": "CPU 时钟频率，单位 Hz（如 16000000UL = 16 MHz）",
    "desc.CONFIG_MCU_SERIAL_TYPE": "0=硬件 UART（快速推荐）  1=软件串口（GPIO 位冲，灵活但慢）",
    "desc.CONFIG_SERIAL_BAUD": "与主机（如树莓派）通信的串口波特率",
    "desc.CONFIG_MCU_SERIAL_HW_PORT": "硬件 UART 端口号: 0=Serial, 1=Serial1, 2=Serial2, 3=Serial3",
    "desc.CONFIG_MCU_SERIAL_SW_RX": "软件串口 RX 引脚（接收主机数据 → Arduino 引脚号）",
    "desc.CONFIG_MCU_SERIAL_SW_TX": "软件串口 TX 引脚（发送给主机 → Arduino 引脚号）",
    "desc.CONFIG_SERIAL_BAUD_U2X": "AVR 上使用双倍速模式 (U2X) 以提高波特率精度",
    "desc.CONFIG_DEBUG_SERIAL_PORT": "调试输出端口: 0=Serial(USB), 1=SerialUSB(原生USB), 2=禁用(无输出)",
    "desc.CONFIG_DEBUG_SERIAL_BAUD": "调试串口波特率（USB 监视器）。常用: 115200, 250000",
    "desc.CONFIG_AVR_STACK_SIZE": "动态内存池/栈大小（字节），AVR 较小，ARM/ESP32 可更大",
    "desc.CONFIG_HAVE_GPIO": "启用基础数字 GPIO 读写支持 (digitalWrite/digitalRead)",
    "desc.CONFIG_HAVE_GPIO_ADC": "启用模拟输入支持 (analogRead / ADC)",
    "desc.CONFIG_HAVE_GPIO_SPI": "启用硬件 SPI 外设（如果目标 MCU 支持）",
    "desc.CONFIG_HAVE_GPIO_I2C": "启用硬件 I2C 外设（如果目标 MCU 支持）",
    "desc.CONFIG_HAVE_GPIO_HARD_PWM": "启用硬件 PWM 支持 (analogWrite / 定时器 PWM)",
    "desc.CONFIG_WANT_GPIO_BITBANGING": "启用 GPIO 软件模拟协议（位冲模式）",
    "desc.CONFIG_WANT_SOFTWARE_SPI": "编译软件（位冲）SPI 实现",
    "desc.CONFIG_WANT_SOFTWARE_I2C": "编译软件（位冲）I2C 实现",
    "desc.CONFIG_WANT_ADC": "编译 ADC 传感器读取支持（热敏电阻等）",
    "desc.CONFIG_WANT_SPI": "编译 SPI 协议支持（用于外部设备通信）",
    "desc.CONFIG_WANT_I2C": "编译 I2C 协议支持（用于外部设备通信）",
    "desc.CONFIG_WANT_HARD_PWM": "编译硬件 PWM 输出支持（加热棒、风扇、舵机）",
    "desc.CONFIG_WANT_BUTTONS": "编译按钮/限位开关输入支持（机械开关）",
    "desc.CONFIG_WANT_STEPPER": "启用步进电机控制（需要定时器生成步进脉冲）",
    "desc.CONFIG_WANT_ENDSTOPS": "启用限位开关支持（归零和限位检测）",
    "desc.CONFIG_INLINE_STEPPER_HACK": "内联步进调度（通用构建关闭）",
    "desc.CONFIG_HAVE_BOOTLOADER_REQUEST": "引导加载程序请求支持（通过命令进入 DFU/ST 引导）",
    "desc.CONFIG_MCU_NAME": "通过 identify 协议上报的人类可读 MCU 名称",

    # ── 智能编辑器预设标签 ──
    "preset.CONFIG_CLOCK_FREQ": "时钟频率 (Hz)",
    "preset.CONFIG_SERIAL_BAUD": "串口波特率",
    "preset.CONFIG_AVR_STACK_SIZE": "栈 / 内存池大小 (字节)",
    "preset.CONFIG_SERIAL_BAUD_U2X": "AVR U2X (双倍速)",
    "preset.CONFIG_MCU_SERIAL_TYPE": "MCU 串口类型",
    "preset.CONFIG_MCU_SERIAL_HW_PORT": "硬件 UART 端口",
    "preset.CONFIG_MCU_SERIAL_SW_RX": "软件串口 RX 引脚",
    "preset.CONFIG_MCU_SERIAL_SW_TX": "软件串口 TX 引脚",
    "preset.CONFIG_DEBUG_SERIAL_PORT": "调试串口端口",
    "preset.CONFIG_DEBUG_SERIAL_BAUD": "调试串口波特率",
    "preset.CONFIG_HAVE_GPIO": "GPIO 支持",
    "preset.CONFIG_HAVE_GPIO_ADC": "模拟输入 (ADC)",
    "preset.CONFIG_HAVE_GPIO_SPI": "硬件 SPI",
    "preset.CONFIG_HAVE_GPIO_I2C": "硬件 I2C",
    "preset.CONFIG_HAVE_GPIO_HARD_PWM": "硬件 PWM",
    "preset.CONFIG_WANT_STEPPER": "步进电机控制",
    "preset.CONFIG_WANT_ENDSTOPS": "限位开关",
    "preset.CONFIG_WANT_ADC": "ADC 传感器读取",
    "preset.CONFIG_WANT_SPI": "SPI 协议",
    "preset.CONFIG_WANT_I2C": "I2C 协议",
    "preset.CONFIG_WANT_HARD_PWM": "硬件 PWM 输出",
    "preset.CONFIG_WANT_BUTTONS": "按钮/开关输入",
    "preset.CONFIG_WANT_GPIO_BITBANGING": "GPIO 位冲模式",
    "preset.CONFIG_WANT_SOFTWARE_SPI": "软件 SPI (位冲)",
    "preset.CONFIG_WANT_SOFTWARE_I2C": "软件 I2C (位冲)",
    "preset.CONFIG_HAVE_BOOTLOADER_REQUEST": "引导加载请求",
    "preset.CONFIG_INLINE_STEPPER_HACK": "内联步进调度",

    # =================================================================
    # ── build_flash_tui.py ──────────────────────────────────────────
    # =================================================================

    # ── 应用 / 窗口 ──
    "bft.title": "generic_arduino 编译刷写工具",
    "bft.title_template": "generic_arduino 编译 & 刷写 — {}",
    "bft.dependency_error": "错误: 缺少 Textual 依赖",

    # ── 面板标题 ──
    "bft.board_panel": " 🧩 开发板选择",
    "bft.action_panel": " 🎯 操作",
    "bft.device_section": " 🔌 串口设备",
    "bft.log_panel": " 📋 编译/刷写日志",

    # ── 按钮 ──
    "bft.btn_build": "📦 编译 (b)",
    "bft.btn_upload": "📤 上传 (u)",
    "bft.btn_clean": "🗑️  清理 (c)",
    "bft.btn_devices": "🔄 刷新设备 (d)",
    "bft.btn_monitor": "📟 串口监视 (s)",
    "bft.btn_clear_log": "清空日志",

    # ── 状态栏 ──
    "bft.status_no_board": "未选择",
    "bft.status_devices": "个设备",
    "bft.status_help": "b=编译  u=上传  c=清理  d=刷新  s=串口  ?=帮助",

    # ── 板子信息 ──
    "bft.board_arch": "架构",
    "bft.board_freq": "频率",
    "bft.board_ram": "RAM",

    # ── 日志消息 ──
    "bft.log_welcome": "👋 欢迎使用 generic_arduino 编译刷写工具！\n",
    "bft.log_hint": "💡 使用 ↑/↓ 选择开发板，按 b 编译，按 u 上传\n",
    "bft.log_scanning": "🔍 正在检测串口设备...\n",
    "bft.log_board_selected": "🧩 已选择开发板: [bold cyan]{}[/] ([dim]{}[/])\n",
    "bft.log_device_selected": "📌 选中设备: {}\n",
    "bft.log_no_board": "❌ 请先选择一个开发板！\n",
    "bft.log_busy": "⏳ 当前有任务正在执行，请等待完成...\n",
    "bft.log_build_start": "📦 开始编译 [bold cyan]{}[/] ({}) ...\n",
    "bft.log_build_ok": "\n✅ 编译成功！[bold green]{}[/] 固件已生成。\n",
    "bft.log_build_hint": "💡 连接开发板后按 u 上传刷写。\n",
    "bft.log_build_fail": "\n❌ 编译失败（返回码: {}）\n",
    "bft.log_firmware_path": "📄 固件: {} ({:,} bytes)\n",
    "bft.log_upload_start": "📤 开始上传固件到 [bold cyan]{}[/] ({}) ...\n",
    "bft.log_upload_warn": "⚠️  请确保开发板已通过 USB 连接！\n",
    "bft.log_upload_ok": "\n✅ 上传成功！[bold green]{}[/] 固件已刷写完成。\n",
    "bft.log_upload_hint": "💡 按 s 键启动串口监视器查看输出。\n",
    "bft.log_upload_fail": "\n❌ 上传失败（返回码: {}）\n",
    "bft.log_upload_check": "💡 请检查:\n   1. 开发板已通过 USB 连接\n   2. 已安装正确的驱动程序\n   3. 没有其他程序占用串口\n",
    "bft.log_clean_start": "🗑️  清理 [bold cyan]{}[/] ({}) 构建文件...\n",
    "bft.log_clean_ok": "✅ 清理完成！\n",
    "bft.log_clean_fail": "❌ 清理失败（返回码: {}）\n",
    "bft.log_device_count": "✅ 发现 {} 个串口设备:\n",
    "bft.log_device_item": "   • {}\n",
    "bft.log_no_devices": "⚠️  未检测到串口设备。请连接开发板后按 d 刷新。\n",
    "bft.log_no_serial_module": "⚠️  无法检测串口设备（未安装 pyserial）\n",
    "bft.log_install_pyserial": "💡 安装: pip install pyserial\n",
    "bft.log_clear": "📋 日志已清空。\n",
    "bft.log_monitor_start": "📟 启动串口监视器: [bold]{}[/] @ 115200 baud\n",
    "bft.log_monitor_hint1": "💡 按 Ctrl+C 或在终端中关闭窗口以停止监视。\n",
    "bft.log_monitor_hint2": "💡 监视器在外部终端中运行。\n",
    "bft.log_monitor_ok": "✅ 串口监视器已启动！\n",
    "bft.log_monitor_fail": "❌ 启动串口监视器失败: {}\n",
    "bft.log_monitor_manual": "💡 请手动运行: pio device monitor -b 115200\n",
    "bft.log_pio_not_found": "pio 命令未找到，请确保 PlatformIO 已安装",

    # ── 通知 ──
    "bft.notify_no_board": "请先选择一个开发板！",
    "bft.notify_building": "开始编译 {}...",
    "bft.notify_build_done": "{} 编译成功！",
    "bft.notify_build_fail": "编译失败，请检查日志",
    "bft.notify_uploading": "正在上传到 {}...",
    "bft.notify_upload_done": "{} 刷写成功！",
    "bft.notify_upload_fail": "上传失败，请检查日志",
    "bft.notify_clean_done": "清理完成",
    "bft.notify_clean_fail": "清理失败",
    "bft.notify_build_title": "编译中",
    "bft.notify_upload_title": "上传中",
    "bft.notify_clean_title": "清理",
    "bft.notify_hint_title": "提示",
    "bft.notify_error_title": "错误",

    # ── 帮助界面 ──
    "bft.help_title": "generic_arduino 编译刷写工具 — 帮助",
    "bft.help_keys": "快捷键",
    "bft.help_nav": "导航选项列表",
    "bft.help_tab": "切换面板（板子 ↔ 操作 ↔ 日志）",
    "bft.help_enter": "选择板子 / 确认操作",
    "bft.help_b": "编译固件",
    "bft.help_u": "上传/刷写固件",
    "bft.help_c": "清理构建文件",
    "bft.help_d": "刷新串口设备列表",
    "bft.help_s": "启动串口监视器",
    "bft.help_q": "退出",
    "bft.help_question": "显示此帮助",
    "bft.help_panels": "面板说明",
    "bft.help_left": "左栏: 开发板选择列表",
    "bft.help_center": "中栏: 操作按钮 & 串口设备",
    "bft.help_right": "右栏: 编译/刷写日志输出",
    "bft.help_workflow": "使用流程",
    "bft.help_step1": "1. 选择目标开发板（↑/↓ 然后 Enter）",
    "bft.help_step2": "2. 按 b 编译固件",
    "bft.help_step3": "3. 连接开发板 USB，按 d 识别设备",
    "bft.help_step4": "4. 按 u 上传刷写",
    "bft.help_step5": "5. 按 s 启动串口监视器查看输出",
    "bft.help_dismiss": "按任意键关闭帮助",

    # ── 绑定标签 ──
    "bft.bind_build": "编译",
    "bft.bind_upload": "上传",
    "bft.bind_clean": "清理",
    "bft.bind_devices": "设备",
    "bft.bind_monitor": "监视",
    "bft.bind_quit": "退出",
    "bft.bind_help": "帮助",
    "bft.bind_switch": "切换面板",
}
