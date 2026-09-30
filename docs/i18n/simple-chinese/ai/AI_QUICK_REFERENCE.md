# Kalico AI 快速参考

## 基本命令

```bash
# 列出所有已连接的 MCU
kalico mcu list --json

# 检查 MCU 配置
kalico mcu check --json

# 显示配置文件位置
kalico config show --json

# 运行诊断
kalico doctor --json

# 扫描 CAN 总线
kalico can scan --json

# 显示版本
kalico version --json
```

## 命令速查表

| 任务 | 命令 |
|------|---------|
| 列出 MCU | `kalico mcu list --json` |
| 检查配置 | `kalico mcu check --json` |
| 查找配置 | `kalico config show --json` |
| 验证配置 | `kalico config validate --json` |
| 完整诊断 | `kalico doctor --json` |
| 修复问题 | `kalico doctor --fix --json` |
| CAN 扫描 | `kalico can scan --json` |
| CAN 状态 | `kalico can info --json` |
| 版本信息 | `kalico version --json` |

## JSON 输出结构

所有 `--json` 命令返回：
```json
{
  "success": true,
  "data": [...],
  "errors": []
}
```

## 退出码

| 代码 | 含义 |
|------|---------|
| 0 | 成功 |
| 1 | 错误 |
| 2 | 配置错误 |
| 130 | 用户取消 |

## MCU 类型

- `serial` - USB/串口（`/dev/ttyUSB0`）
- `can` - CAN 总线（`canbus_uuid`）
- `tcp` - TCP 网络（`tcp_host`）
- `udp` - UDP 网络（`udp_host`）

## 状态值

- `OK` - 正常工作
- `WARNING` - 已找到但无响应
- `ERROR` - 未找到

## CAN 状态

- `Assigned` - 已有节点 ID
- `Unassigned` - 需要分配节点 ID

## 配置位置

1. `~/printer_data/config/printer.cfg`
2. `~/klipper_config/printer.cfg`
3. `~/.config/klipper/printer.cfg`
4. `/etc/klipper/printer.cfg`
5. `./printer.cfg`

## 工作流程示例

### 安装验证
```bash
kalico version --json
kalico config show --json
kalico config validate --json
kalico mcu list --json
kalico doctor --json
```

### 修复 MCU 配置
```bash
kalico mcu check --json
kalico mcu check --fix
kalico config validate --json
```

### CAN 故障排除
```bash
kalico can info --json
kalico can scan --json
kalico mcu check --json
```