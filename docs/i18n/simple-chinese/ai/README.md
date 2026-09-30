# Kalico AI 文档

本目录包含专门为与 Kalico 3D 打印机固件协作的 AI 助手设计的文档。

## 内容

### [CLI 参考](CLI_REFERENCE.md)
所有 Kalico CLI 命令的全面参考，包括：
- 命令语法和选项
- JSON 输出格式
- 错误处理
- 常见工作流程
- AI 集成技巧

### [快速参考](AI_QUICK_REFERENCE.md)
快速参考卡，包含：
- 基本命令
- 命令速查表
- 状态码
- 配置位置

## 快速上手

### 安装

CLI 随 Kalico 一起提供。安装 Kalico 后即可使用 CLI：

```bash
pip install -e .
```

### 基本用法

```bash
# 显示帮助
kalico --help

# 显示版本
kalico version

# 列出已连接的 MCU
kalico mcu list

# 运行诊断
kalico doctor
```

### JSON 输出

所有命令都支持 JSON 输出，便于编程访问：

```bash
kalico mcu list --json
kalico config show --json
kalico doctor --json
```

## AI 集成

### 面向 AI 助手

使用 Kalico 时，AI 助手应：

1. **使用 JSON 输出** 以可靠地解析数据
2. **检查退出码** 确认操作成功
3. **修改前验证配置**
4. **运行诊断** 识别问题
5. **使用详细模式** 进行调试

### 示例工作流程

```bash
# 1. 获取系统信息
kalico version --json

# 2. 查找配置
kalico config show --json

# 3. 验证配置
kalico config validate --json

# 4. 检查 MCU 连接
kalico mcu check --json

# 5. 运行完整诊断
kalico doctor --json
```

## 命令分类

### MCU 管理
- `kalico mcu list` - 列出已连接的 MCU
- `kalico mcu check` - 检查 MCU 配置

### 配置
- `kalico config show` - 显示配置位置
- `kalico config validate` - 验证配置

### 诊断
- `kalico doctor` - 运行系统诊断

### CAN 总线
- `kalico can scan` - 扫描 CAN 总线
- `kalico can info` - 显示 CAN 接口信息

### 系统
- `kalico version` - 显示版本信息

## 支持

- [Kalico 文档](https://docs.kalico.gg/)
- [GitHub Issues](https://github.com/KalicoCrew/kalico/issues)
- [配置参考](https://docs.kalico.gg/Configuration.html)