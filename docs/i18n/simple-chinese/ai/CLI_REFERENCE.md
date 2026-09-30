# 面向 AI 助手的 Kalico CLI 参考

本文档为 Kalico CLI 工具提供全面参考，专为 AI 助手理解和与 Kalico 3D 打印机固件交互而设计。

## 概述

Kalico 提供统一的 CLI 接口（`kalico`）用于管理 3D 打印机固件、MCU 设备和系统配置。所有命令都支持 JSON 输出，便于编程访问。

## 命令结构

```
kalico <command> [subcommand] [options]
```

## 全局选项

| 选项 | 说明 |
|--------|-------------|
| `-v, --verbose` | 启用详细输出 |
| `--json` | 以 JSON 格式输出 |
| `--version` | 显示版本信息 |
| `-h, --help` | 显示帮助信息 |

## 命令

### 1. MCU 管理（`kalico mcu`）

#### 列出已连接的 MCU

```bash
kalico mcu list [--transport serial|can|tcp|udp|all] [--scan-network] [--json]
```

**用途**：枚举所有通过不同传输协议连接的 MCU 设备。

**选项**：
- `--transport`：按传输类型过滤（默认：all）
- `--scan-network`：包含对 TCP/UDP 设备的网络扫描
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
[
  {
    "type": "serial",
    "path": "/dev/ttyUSB0",
    "description": "CH340 USB-Serial",
    "is_kalico": true,
    "vid": 6790,
    "pid": 29987,
    "serial_number": "A123456"
  }
]
```

**AI 使用场景**：
- 在配置前发现可用的 MCU 设备
- 验证设备连接
- 生成配置建议

#### 检查 MCU 配置

```bash
kalico mcu check [--fix] [--config PATH] [--json]
```

**用途**：根据实际设备验证 MCU 配置。

**选项**：
- `--fix`：交互式配置修复向导
- `--config PATH`：printer.cfg 的路径
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
[
  {
    "mcu": "main",
    "transport": "serial",
    "matched": true,
    "responsive": true,
    "firmware": "Detected (Kalico protocol)",
    "issues": [],
    "suggestions": []
  }
]
```

**AI 使用场景**：
- 诊断配置问题
- 建议配置修复
- 验证固件连接

### 2. 配置管理（`kalico config`）

#### 显示配置位置

```bash
kalico config show [--config PATH] [--json]
```

**用途**：显示配置文件的位置和详细信息。

**选项**：
- `--config PATH`：指定自定义配置路径
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
{
  "path": "/home/user/printer_data/config/printer.cfg",
  "absolute_path": "/home/user/printer_data/config/printer.cfg",
  "size": 4096,
  "modified": 1717234567.0
}
```

**AI 使用场景**：
- 定位配置文件以便读取/编辑
- 检查配置文件状态
- 验证文件权限

#### 验证配置

```bash
kalico config validate [--config PATH] [--json]
```

**用途**：验证配置文件的语法和结构。

**选项**：
- `--config PATH`：指定自定义配置路径
- `--json`：以 JSON 格式输出

**AI 使用场景**：
- 应用前检查配置
- 验证语法更改
- 确保配置完整性

### 3. 系统诊断（`kalico doctor`）

#### 运行诊断

```bash
kalico doctor [--fix] [--dry-fix] [--config PATH] [--network] [--json]
```

**用途**：全面的系统诊断和自动修复。

**选项**：
- `--fix`：自动修复可修复的问题
- `--dry-fix`：预览修复而不实际应用
- `--config PATH`：printer.cfg 的路径
- `--network`：扫描网络中的设备
- `--json`：以 JSON 格式输出
- `--skip-env`：跳过环境检查
- `--skip-config`：跳过配置检查
- `--skip-mcu`：跳过 MCU 检查
- `--skip-service`：跳过服务检查

**AI 使用场景**：
- 全面的系统健康检查
- 自动化问题处理
- 环境验证

### 4. CAN 总线管理（`kalico can`）

#### 扫描 CAN 总线

```bash
kalico can scan [--interface can0 can1] [--timeout 2.0] [--json]
```

**用途**：扫描 CAN 总线上已连接的设备。

**选项**：
- `--interface`：要扫描的 CAN 接口
- `--timeout`：扫描超时时间（秒，默认：2.0）
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
{
  "can0": [
    {
      "uuid": 1234567890,
      "app_name": "Kalico",
      "app_id": 7,
      "node_id": 1,
      "status": "Assigned",
      "interface": "can0"
    }
  ]
}
```

**AI 使用场景**：
- 发现 CAN 设备
- 验证 CAN 配置
- 诊断 CAN 连接问题

#### 显示 CAN 接口信息

```bash
kalico can info [--interface can0 can1] [--json]
```

**用途**：显示 CAN 接口的状态和统计信息。

**选项**：
- `--interface`：要查询的 CAN 接口
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
[
  {
    "name": "can0",
    "state": "UP",
    "bitrate": 500000,
    "can_state": "ACTIVE",
    "stats": {
      "rx_errors": 0,
      "tx_errors": 0,
      "rx_over_errors": 0,
      "tx_dropped": 0
    }
  }
]
```

**AI 使用场景**：
- 监控 CAN 总线健康状况
- 诊断 CAN 错误
- 验证 CAN 配置

### 5. 版本信息（`kalico version`）

```bash
kalico version [--json]
```

**用途**：显示版本和系统信息。

**选项**：
- `--json`：以 JSON 格式输出

**示例输出（JSON）**：
```json
{
  "app_name": "Kalico",
  "cli_version": "0.1.0",
  "git_version": "v0.12.1-123-gabcdef",
  "git_branch": "main",
  "git_remote": "origin",
  "git_url": "https://github.com/KalicoCrew/kalico.git",
  "python_version": "3.12.0",
  "platform": "Linux-6.1.0-x86_64",
  "architecture": "x86_64"
}
```

## 常见工作流程

### 工作流程 1：初始安装验证

```bash
# 1. 检查版本和环境
kalico version --json

# 2. 定位配置
kalico config show --json

# 3. 验证配置
kalico config validate --json

# 4. 列出已连接的 MCU
kalico mcu list --json

# 5. 运行全面诊断
kalico doctor --json
```

### 工作流程 2：MCU 配置修复

```bash
# 1. 检查 MCU 配置
kalico mcu check --json

# 2. 如果发现问题，运行修复
kalico mcu check --fix

# 3. 验证更改
kalico config validate --json
```

### 工作流程 3：CAN 总线故障排除

```bash
# 1. 检查 CAN 接口状态
kalico can info --json

# 2. 扫描设备
kalico can scan --json

# 3. 验证配置
kalico mcu check --json
```

## 错误处理

所有命令返回相应的退出码：
- `0`：成功
- `1`：一般错误
- `2`：配置错误
- `130`：用户取消（Ctrl+C）

## JSON 输出格式

使用 `--json` 时，输出遵循以下结构：

```json
{
  "command": "mcu list",
  "timestamp": "2026-05-31T12:00:00Z",
  "success": true,
  "data": [...],
  "errors": [],
  "warnings": []
}
```

## AI 集成技巧

1. **始终使用 `--json`** 进行编程访问
2. **检查退出码** 确认操作成功
3. **解析错误消息** 用于用户反馈
4. **使用详细模式** 进行调试
5. **串联命令** 处理复杂工作流程

## 配置文件位置

查找 `printer.cfg` 的默认搜索路径：
1. `~/printer_data/config/printer.cfg`
2. `~/klipper_config/printer.cfg`
3. `~/.config/klipper/printer.cfg`
4. `/etc/klipper/printer.cfg`
5. `./printer.cfg`（当前目录）

## 传输类型

| 传输 | 说明 | 配置 |
|-----------|-------------|---------------|
| `serial` | USB/串口连接 | `serial: /dev/ttyUSB0` |
| `can` | CAN 总线连接 | `canbus_uuid: <uuid>` |
| `tcp` | TCP 网络连接 | `tcp_host: <ip>` |
| `udp` | UDP 网络连接 | `udp_host: <ip>` |

## 状态码

### MCU 状态
- `OK`：MCU 已连接且有响应
- `WARNING`：找到 MCU 但对协议无响应
- `ERROR`：未找到 MCU 或配置不匹配

### CAN 设备状态
- `Assigned`：设备已分配节点 ID
- `Unassigned`：设备需要分配节点 ID
- `Unknown`：无法确定状态

## 面向 AI 助手的示例

### 示例 1：发现并配置 MCU

```python
import subprocess
import json

# 列出可用的 MCU
result = subprocess.run(['kalico', 'mcu', 'list', '--json'], capture_output=True, text=True)
mcus = json.loads(result.stdout)

# 检查配置
result = subprocess.run(['kalico', 'mcu', 'check', '--json'], capture_output=True, text=True)
checks = json.loads(result.stdout)

# 根据问题建议修复
for check in checks:
    if check['issues']:
        print(f"Issues with {check['mcu']}:")
        for issue in check['issues']:
            print(f"  - {issue}")
```

### 示例 2：验证配置

```python
import subprocess
import json

# 获取配置位置
result = subprocess.run(['kalico', 'config', 'show', '--json'], capture_output=True, text=True)
config_info = json.loads(result.stdout)

# 验证配置
result = subprocess.run(['kalico', 'config', 'validate', '--json'], capture_output=True, text=True)
validation = json.loads(result.stdout)

if validation.get('success'):
    print("Configuration is valid")
else:
    print(f"Configuration error: {validation.get('error')}")
```

### 示例 3：CAN 总线诊断

```python
import subprocess
import json

# 扫描 CAN 总线
result = subprocess.run(['kalico', 'can', 'scan', '--json'], capture_output=True, text=True)
devices = json.loads(result.stdout)

# 检查接口状态
result = subprocess.run(['kalico', 'can', 'info', '--json'], capture_output=True, text=True)
interfaces = json.loads(result.stdout)

# 报告状态
for iface in interfaces:
    print(f"{iface['name']}: {iface['state']}, {iface['bitrate']} bps")
```

## 另请参阅

- [Kalico 文档](https://docs.kalico.gg/)
- [配置参考](https://docs.kalico.gg/Configuration.html)
- [MCU 命令](https://docs.kalico.gg/MCU_Commands.html)