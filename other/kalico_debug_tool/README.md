# Kalico Debug Tool

**上位机调试工具** — 用于调试 Kalico/Klipper 3D 打印机固件协议的主机端工具。

## 功能特性

| # | 功能 | 说明 |
|---|------|------|
| 1 | **图形化界面** | 基于 tkinter 的多标签页 GUI，可在桌面环境可视化调试 |
| 2 | **协议交互日志** | 实时显示 Tx/Rx 消息，彩色高亮，支持过滤和导出 |
| 3 | **虚拟 MCU 模拟** | 无需硬件即可模拟 MCU 行为，支持自定义命令/响应 |
| 4 | **AI CLI 接口** | JSON-RPC 风格的 AI Agent 接口，方便 Copilot 等工具自动化调试 |
| 5 | **数据捕获与回放** | 串口数据实时捕获到 JSON Lines 文件，支持离线回放 |

## 启动方式

```bash
# 图形化界面（默认）
python -m kalico_debug_tool

# 交互式 CLI 模式
python -m kalico_debug_tool --cli

# AI Bridge 批量模式（JSON in/out）
echo '{"id":"1","cmd":"get_status","params":{}}' | python -m kalico_debug_tool --batch

# 查看版本
python -m kalico_debug_tool --version
```

## 连接模式

支持两种通信模式在 GUI 中通过单选框切换:

### 🔌 串口模式 (UART/USB CDC ACM)
- 标准 RS232 串口连接
- 自动扫描可用 COM 端口
- 支持 9600 ~ 500000 波特率

### 📡 CAN 总线模式
- 通过 USB-CAN 桥接器连接 (Windows 支持)
- 支持接口类型:
  - **slcan**: 串口转 CAN (Lawicel CANUSB, USB2CAN 等) — 通过 COM 端口
  - **pcan**: PEAK PCAN-USB 系列
  - **virtual**: 虚拟 CAN 总线 (无需硬件, 用于测试)
- CAN 发现: 自动查找总线上的 MCU 节点
- NodeID 分配: 支持 UUID → NodeID 映射

### 依赖

```bash
pip install -r other/kalico_debug_tool/requirements.txt
```

依赖:
- `pyserial` — 串口通信
- `python-can` — CAN 总线通信 (Win/Linux/Mac)

```
other/kalico_debug_tool/
├── __main__.py              # 启动入口（GUI / CLI / Batch）
├── requirements.txt         # pyserial, python-can
├── protocol/                # 协议编解码层（纯 Python）
│   ├── codec.py             # VLQ 编解码、CRC16-CCITT、消息块组帧
│   ├── parser.py            # 消息解析器（解码/编码）
│   └── dictionary.py        # Data Dictionary 管理
├── io/                      # I/O 层
│   ├── serial_io.py         # 串口通信封装
│   ├── can_io.py            # CAN 总线通信（slcan/pcan/virtual）
│   ├── capture.py           # 实时数据捕获
│   └── replay.py            # 离线数据回放
├── simulator/               # 虚拟 MCU
│   ├── virtual_mcu.py       # MCU 模拟器核心
│   ├── command_handler.py   # 命令处理器框架
│   └── responder.py         # 自动响应生成器
├── log/                     # 日志子系统
│   ├── logger.py            # JSON Lines 结构化日志
│   ├── filter.py            # 事件过滤器
│   └── export.py            # CSV/Text/Hex 导出
├── gui/                     # 图形界面
│   ├── common_commands.py   # 常见指令预设定义
│   ├── main_window.py       # 主窗口 + Notebook
│   └── panels/
│       ├── connection_panel.py  # 串口/CAN 连接面板 + 指令按钮
│       ├── log_panel.py         # 协议日志面板
│       ├── hex_panel.py         # Hex 视图面板
│       ├── simulator_panel.py   # 虚拟 MCU 面板 + 指令预设
│       └── ai_cli_panel.py      # 内嵌 CLI 终端
├── cli/                     # CLI 接口
│   ├── main_cli.py          # 交互式 REPL
│   ├── commands.py          # 命令实现（含 CAN 支持）
│   └── ai_bridge.py         # AI Agent JSON-RPC 接口
└── tests/                   # 测试
    └── test_integration.py  # 集成测试
```

## 安装依赖

```bash
pip install -r other/kalico_debug_tool/requirements.txt
```

依赖:
- `pyserial` — 串口通信（必需）
- `python-can` — CAN 总线通信（可选，仅 Linux）

## 使用方法

### GUI 模式

启动后可见 5 个标签页:

1. **连接** — 选择串口、波特率，连接/断开 MCU
2. **协议日志** — 实时显示解析后的 Tx/Rx 消息，彩色标记
3. **Hex 视图** — 原始字节 Hex Dump + 协议字段解析
4. **虚拟 MCU** — 启动/停止模拟 MCU，发送测试命令
5. **CLI 终端** — 内嵌命令行，支持所有 CLI 命令

### CLI 模式

常用命令:

```
connect COM3 250000     — 连接串口
send_cmd identify {}    — 发送 identify 命令
monitor                 — 显示最近 50 条消息
dict                    — 查看 data dictionary
sim_start               — 启动虚拟 MCU
sim_send identify {}    — 向虚拟 MCU 发送命令
capture test_capture    — 开始捕获数据
capture_stop            — 停止捕获
export csv log.csv      — 导出日志为 CSV
```

### AI Bridge 模式

用于 AI Agent 调用的 JSON-RPC 接口。每个命令一行 JSON：

```json
{"id": "1", "cmd": "connect", "params": {"port": "COM3", "baudrate": 250000}}
{"id": "2", "cmd": "get_status", "params": {}}
{"id": "3", "cmd": "send_command", "params": {"name": "identify", "params": {}}}
{"id": "4", "cmd": "get_messages", "params": {"count": 10}}
```

响应格式：

```json
{"id": "1", "ok": true, "data": {"port": "COM3", ...}}
{"id": "3", "ok": false, "error": "Not connected"}
```

## 协议支持

本工具实现了 Kalico 自定义二进制 RPC 协议的完整编解码:

- **VLQ 编码** — 可变长度整数编码（1-5 字节）
- **CRC16-CCITT** — 消息完整性校验
- **消息块格式** — [Length][Seq][Content][CRC][Sync]
- **Data Dictionary** — 从固件识别响应中提取消息定义

协议文档详见: `docs/i18n/simple-chinese/Communication_Protocol.md`

## 许可

GNU General Public License v3 (GPLv3)
