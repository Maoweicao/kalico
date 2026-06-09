# 插件开发指南

本文档介绍了如何为 Kalico 开发、安装和管理插件。插件可以在不修改核心源代码树的情况下
扩展 Kalico 的功能，确保自定义代码不会因为更新而丢失。

## 目录

- [概述](#概述)
- [快速入门](#快速入门)
- [插件目录结构](#插件目录结构)
- [架构](#架构)
- [生命周期](#生命周期)
- [插件 API 参考](#插件-api-参考)
- [子系统组件注册](#子系统组件注册)
- [服务定位器模式](#服务定位器模式)
- [生命周期事件](#生命周期事件)
- [G-code 命令注册](#g-code-命令注册)
- [Webhooks / 远程 API](#webhooks--远程-api)
- [配置](#配置)
- [最佳实践](#最佳实践)
- [调试与自检](#调试与自检)
- [从 `extras/` 迁移到 `plugins/`](#从-extras-迁移到-plugins)
- [使用插件安装器](#使用插件安装器)
- [完整示例](#完整示例)
- [故障排除](#故障排除)

---

## 概述

Kalico 的插件系统采用 **约定优于配置** 的设计。不需要 XML 清单、JSON 元数据或插件注册表——
一个插件就是一个普通的 Python 模块（`.py` 文件或子包），放到 `klippy/plugins/` 目录即可。
文件的存在本身就是注册。

**核心概念：**

| 概念 | 说明 |
|------|------|
| **extras** | Kalico 内置模块，位于 `klippy/extras/` |
| **plugins** | 用户/外部模块，位于 `klippy/plugins/`（git 不跟踪） |
| **PrinterModule** | 已发现模块的包装器；负责延迟加载和错误追踪 |
| **配置段** | `printer.cfg` 中的 `[name]` 或 `[name suffix]` 条目，触发模块实例化 |
| **Printer.objects** | 核心 OrderedDict，所有已实例化模块实例的集合 |

### 关键设计决策

- **没有启用/禁用列表。** 插件只有在 `printer.cfg` 中存在对应的 `[section]` 时才会加载。
  如果没有配置段，模块会被导入但永远不会实例化（在 `LIST_MODULES` 中标记为"unused"）。
- **`plugins/` 目录不受 git 跟踪。** 它不存在于上游 Kalico 仓库中。随意往里面放文件——
  不会产生 dirty git tree。
- **插件覆盖受开关控制。** 如果插件名称与内置 extra 同名，Kalico 会报错，除非在
  `[danger_options]` 中设置 `allow_plugin_override: True`。这可以防止意外覆盖。

---

## 快速入门

创建 `klippy/plugins/my_tool.py`：

```python
class MyTool:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("MY_COMMAND", self.cmd_MY_COMMAND)
        self.printer.register_event_handler("klippy:ready", self._on_ready)

    def _on_ready(self):
        pass  # 需要已连接打印机的初始化工作

    def cmd_MY_COMMAND(self, gcmd):
        gcmd.respond_info("Hello from my_tool!")

def load_config(config):
    return MyTool(config)
```

在 `printer.cfg` 中添加：

```ini
[my_tool]
```

重启 Kalico，在控制台中运行 `MY_COMMAND` —— 即可看到 "Hello from my_tool!"。

---

## 插件目录结构

```
klippy/
├── extras/                  # 内置模块（Kalico 核心的一部分）
│   ├── __init__.py
│   ├── respond.py
│   └── ...
├── plugins/                 # 用户插件（git 不跟踪）
│   ├── __init__.py          # 包标记（始终存在）
│   ├── my_tool.py           # 单文件插件
│   ├── my_complex_plugin/   # 子包插件
│   │   ├── __init__.py      # 包含 load_config / load_config_prefix
│   │   ├── helpers.py
│   │   └── sensor.py
│   └── ...
```

### 单文件 vs 子包

| 方式 | 适用场景 | 示例 |
|------|---------|------|
| **单个 `.py` 文件** | 简单插件，无辅助文件 | `my_tool.py` |
| **含 `__init__.py` 的子包** | 包含多个模块/辅助文件/数据文件的插件 | `my_complex_plugin/` |

两种方式都会被自动发现。模块名称是文件名（去掉 `.py`）或目录名。

### 导入规则

你的插件位于 `klippy.plugins` 包中。需要从内置 extras 导入时，使用完整的 `klippy.extras.*` 路径：

```python
from klippy.extras.gcode_macro import Template  # 正确
from klippy.extras.servo import Servo            # 正确
```

插件子包内部的相对导入照常工作：

```python
from .helpers import my_helper                   # 插件子包内部
```

---

## 架构

下图展示了各关键组件之间的交互：

![插件架构图](../img/zh/plugin-architecture.svg)

- **printer.cfg** 提供 `[section]` 定义和选项值。
- **ConfigWrapper** 包装每个配置段，提供类型化访问（`get()`、`getfloat()`、`getint()` 等）。
- 你的 **插件** 实现 `load_config(config)` 或 `load_config_prefix(config)`，接收一个 `ConfigWrapper`。
- **Printer** 充当 **服务定位器** —— 你的插件按名称拉取依赖：
  - `printer.lookup_object("gcode")` — 获取已注册的服务
  - `printer.load_object(config, "heaters")` — 懒加载其他模块
  - `printer.register_event_handler("klippy:ready", cb)` — 订阅事件
  - `printer.lookup_components("load_cell_sensors")` — 查询子系统注册表

---

## 生命周期

![插件生命周期](../img/zh/plugin-lifecycle.svg)

### 各阶段详情

**阶段 1 – 发现**（`printer.py:_load_modules`）
`klippy/extras/` 和 `klippy/plugins/` 中的所有 `*.py` 文件通过
`pkgutil.iter_modules()` 被发现。每个文件变成一个 `PrinterModule`，存储在
`printer.printer_modules` 中。如果插件与已有的 extra 同名，除非设置了
`allow_plugin_override: True`，否则 Kalico 会报错。

**阶段 2 – 加载**（`printer.py:_load_modules`）
每个 `PrinterModule.load()` 调用 `importlib.import_module(module_info.name)`。
导入期间的异常会被捕获并暂存——只有当该模块实际被使用时才会抛出错误。这意味着
一个损坏的、从未在 `printer.cfg` 中被引用的插件不会导致启动崩溃。

**阶段 3 – 组件注册**（`printer.py:_register_subsystem_components`）
如果模块定义了 `register_components(subsystem)`，它会被调用来填充命名的子系统注册表。
这是可选的，通常由提供驱动类组件的插件使用（例如，用于称重传感器系统的传感器类型）。

**阶段 4 – 配置初始化**（`printer.py:_read_config`）
对于 `printer.cfg` 中的每个 `[section]`，`printer.load_object(config, section)`
找到匹配的 `PrinterModule` 并调用其 `load_config(config)` 或
`load_config_prefix(config)`。返回的实例存储在 `printer.objects` 中。
配置段必须在此阶段读取其所有参数；未读取的参数会被标记为错误。

**阶段 5 – 连接**（`printer.py:_connect`）
`"klippy:connect"` 事件在所有模块实例化后触发。在此阶段进行跨模块查找、
配置验证和硬件握手。

**阶段 6 – 就绪**（`printer.py:_connect`）
`"klippy:ready"` 事件在所有 connect 处理程序完成后触发。
打印机已准备好处理 G-code 命令。请勿在此处抛出错误。

**阶段 7 – 关闭 / 重启**（`printer.py:run`）
在 `RESTART` 或 `FIRMWARE_RESTART` 时，`Printer` 和 `Reactor` 被销毁并
从头重建。所有模块会被重新导入和重新初始化。不支持热插拔——需要完全重启。

---

## 插件 API 参考

每个插件模块必须暴露以下至少一个模块级函数：

### `load_config(config)` → 对象

```python
def load_config(config):
    return MyPlugin(config)
```

当 `printer.cfg` 包含 `[my_plugin]`（精确匹配，无后缀）时调用。
接收该配置段的 `ConfigWrapper`。必须返回构造好的对象。

### `load_config_prefix(config)` → 对象

```python
def load_config_prefix(config):
    return MyPlugin(config)
```

用于 `[my_plugin instance1]`、`[my_plugin instance2]` 等形式的配置段（前缀匹配）。
支持同一模块的多个实例。

### `register_components(subsystem)`（可选）

```python
def register_components(subsystem):
    subsystem.register_component("my_subsystem", "my_component", MyDriver)
```

在启动期间调用，用于将命名组件注册到子系统注册表中。
详见[子系统组件注册](#子系统组件注册)。

### `ConfigWrapper` API

```python
value = config.get("option_name", default=None)
flag  = config.getboolean("bool_option", False)
num   = config.getfloat("float_option", 1.0, minval=0.0, maxval=10.0)
count = config.getint("int_option", 5, minval=0)
choice = config.getchoice("mode", {"fast": 1, "slow": 2}, "fast")
name  = config.get_name()         # 完整配置段名称，如 "my_plugin instance1"
printer = config.get_printer()    # Printer 服务定位器
section = config.getsection("subsection")  # 获取嵌套配置段
```

---

## 子系统组件注册

有些插件不是"独立模块"，而是为更大的子系统提供组件。
例如，每个 ADC 传感器驱动都向 `"load_cell_sensors"` 子系统注册自己，
主 `[load_cell]` 配置段通过 `config.getchoice("sensor_type", sensors)` 让用户选择。

### 提供方（注册到子系统）

```python
# 在插件的 register_components() 中：
def register_components(subsystem):
    subsystem.register_component(
        "my_subsystem",           # 子系统名称（字符串键）
        "my_driver_v1",           # 组件名称（配置中显示给用户）
        MyDriverClass             # 组件（类、函数或值）
    )
```

参考 `klippy/extras/load_cell/__init__.py:14` 中的实际例子。

### 消费方（从子系统查询）

```python
sensors = printer.lookup_components("my_subsystem")  # → {"my_driver_v1": MyDriverClass, ...}
chosen = config.getchoice("driver_type", sensors)    # 用户从选项中选取
instance = chosen(config)                             # 实例化选中的组件
```

---

## 服务定位器模式

Kalico 使用 **服务定位器**（拉取式）模式，而不是依赖注入（推送式）。
你的插件负责从 `Printer` 实例中拉取所需的依赖。

### `Printer` 上的关键方法

```python
# 获取 Printer 实例的引用
printer = config.get_printer()

# 通过配置段名称查找之前注册的对象
gcode = printer.lookup_object("gcode")
toolhead = printer.lookup_object("toolhead")

# 懒加载另一个模块（后续调用返回缓存的实例）
heaters = printer.load_object(config, "heaters")

# 查询子系统组件注册表
components = printer.lookup_components("load_cell_sensors")

# 获取 reactor（用于定时器、文件 I/O、sleep）
reactor = printer.get_reactor()

# 获取启动参数
args = printer.get_start_args()

# 检查打印机是否处于关闭状态
if printer.is_shutdown():
    return
```

### 为什么使用拉取式？

- 初始化顺序不是线性的——你的插件被构造时，并非所有模块都存在。
  将依赖查找推迟到事件处理函数（如 `"klippy:connect"`）中执行，以避免缺少依赖。
- `gcode` 和 `pins` 对象始终可以早期获取。
- 使用 `printer.load_object(config, "module_name")` 来强制加载一个依赖。

---

## 生命周期事件

通过注册事件处理函数来挂钩 Kalico 的生命周期：

```python
printer.register_event_handler("event_name", callback_function)
```

### 标准事件

| 事件 | 阶段 | 常见用途 |
|------|------|---------|
| `"klippy:connect"` | 所有模块实例化后 | 跨模块查找、配置验证、硬件检查和握手 |
| `"klippy:ready"` | 打印机完全就绪 | 开始自动例程、启用功能 |
| `"klippy:disconnect"` | 重启/关闭期间 | 关闭文件、socket，清理资源 |
| `"klippy:shutdown"` | 错误/故障关闭 | 安全停止硬件，记录状态 |
| `"klippy:firmware_restart"` | 固件重启前 | MCU 复位前保存状态 |
| `"klippy:mcu_identify"` | MCU 识别阶段 | 注册 MCU 相关对象 |
| `"gcode:command_error"` | G-code 解析错误 | 自定义错误恢复 |
| `"gcode:unknown_command"` | 未识别的 G-code | 实现自定义命令解析 |

### 事件处理函数规范

```python
def _handle_connect(self):
    # 安全：查找其他对象
    self.toolhead = self.printer.lookup_object("toolhead")

def _handle_ready(self):
    # 安全：开始操作，发送命令
    # 不要在这里抛出错误

def _handle_shutdown(self):
    try:
        self.motor.stop()
    except:
        pass  # 在关闭期间抑制错误
```

---

## G-code 命令注册

在模块的 `__init__` 中注册自定义 G-code 命令：

```python
class MyPlugin:
    def __init__(self, config):
        self.gcode = self.printer.lookup_object("gcode")
        self.gcode.register_command("MY_CMD", self.cmd_MY_CMD, "帮助描述文本")

    def cmd_MY_CMD(self, gcmd):
        # 读取参数
        speed = gcmd.get_float("S", 0.0)
        value = gcmd.get("PARAM", "default")

        # 向控制台回复
        gcmd.respond_info(f"Got S={speed}, PARAM={value}")

        # 输入无效时抛出错误
        if speed < 0:
            raise gcmd.error("Speed must be positive")
```

### `gcmd` 对象 API

```python
gcmd.get("NAME", default=None)              # 字符串参数
gcmd.get_float("S", default=0., minval=0)    # 浮点参数
gcmd.get_int("N", default=0, minval=0)       # 整数参数
gcmd.respond_info("message")                 # 标准回复
gcmd.respond_raw("raw text")                 # 原始输出
gcmd.error("error message")                  # 抛出错误（终止命令执行）
```

---

## Webhooks / 远程 API

为外部客户端（Mainsail、Fluidd 等）暴露 JSON-RPC 端点：

```python
class MyPlugin:
    def __init__(self, config):
        webhooks = self.printer.lookup_object("webhooks")
        webhooks.register_endpoint("my_plugin/get_status", self._handle_api)

    def _handle_api(self, web_request):
        return {
            "temperature": 42.0,
            "status": "ok",
        }
```

### `get_status()` 自动状态暴露

在你的打印机对象上定义 `get_status()` 方法，即可通过 API 服务器和 Jinja 模板
自动暴露其状态：

```python
class MyPlugin:
    def get_status(self):
        return {
            "value": self.current_value,
            "active": self.is_active,
        }
```

状态值必须是：`int`、`float`、`str`、`bool`、`list`、`dict`、`tuple` 或 `None`。
导出的列表和字典必须视为"不可变"——如果内容发生变化，必须从 `get_status()` 返回新对象，
否则 API 服务器不会检测到这些变化。

---

## 配置

### 基本配置段

```ini
[my_tool]
option1: some_value
option2: 3.14
option3: True
```

### 通过 `load_config_prefix` 实现多实例

```ini
[my_tool extruder]
name: hotend_left
max_temp: 300

[my_tool bed]
name: heated_bed
max_temp: 120
```

你的 `load_config_prefix()` 会为每个实例收到单独的 `ConfigWrapper`。

### 插件覆盖

如果你的插件与内置 extra 同名（例如创建了 `klippy/plugins/respond.py`），
则必须启用覆盖：

```ini
[danger_options]
allow_plugin_override: True
```

否则 Kalico 会报错：`"Module 'respond' found in both extras and plugins!"`。

### 包含其他配置文件

在插件的配置中使用 `!!include` 引入更大的配置：

```ini
[my_tool]
!!include path/to/my_tool_defaults.cfg
custom_option: my_value
```

---

## 最佳实践

1. **不要使用全局变量。** 所有状态都应存储在打印机对象实例中。
   `RESTART` 会重新创建 `Printer`，全局变量会导致状态泄露。

2. **在 `__init__` 中分配所有成员变量。** 避免动态创建属性——
   在构造函数中使用 `self.xyz = None`。

3. **浮点值使用浮点常量。** 优先使用 `self.speed = 1.` 而不是 `self.speed = 1`，
   优先使用 `self.speed = 2. * x` 而不是 `self.speed = 2 * x`。
   这可以避免 Python 类型转换中的隐蔽错误。

4. **在构造期间读取所有配置选项。** 在 `__init__` 期间未读取的参数
   会被标记为拼写错误并导致配置错误。

5. **不要访问其他模块的 `_` 前缀成员。** 这些是可能会不通知就更改的私有实现细节。

6. **将繁重的工作推迟到事件处理函数中执行。** 使用 `"klippy:connect"` 查找可能
   还不存在的模块，使用 `"klippy:ready"` 需要完全初始化打印机的操作。

7. **在 disconnect 时关闭文件/socket。** 注册 `"klippy:disconnect"` 事件：

   ```python
   self.printer.register_event_handler("klippy:disconnect", self._cleanup)
   ```

8. **在 shutdown 处理函数中抑制错误。** 在紧急关闭期间，记录错误并吞下异常
   比阻止关闭序列执行更好。

---

## 调试与自检

### `LIST_MODULES` 命令

检查所有已加载模块的状态：

```
LIST_MODULES DETAIL=1
```

输出示例：
```
Loaded modules:

  my_tool (plugins, loaded)
    Path: klippy/plugins/my_tool.py
    Loaded: 2025-05-14 12:00:00
    Used: yes
```

字段说明：
- **source**：`"plugins"` 或 `"extras"` —— 模块来源
- **loaded**：模块是否导入成功（导入错误会在此处报告）
- **used**：是否有 `printer.cfg` 的配置段引用了此模块
- **error**：加载失败的异常详情（仅在 `loaded: False` 时显示）

### 日志

```python
import logging

logging.info("信息性消息")
logging.warning("警告消息")
logging.exception("异常回溯")  # 在 except 块中使用
```

日志输出到 Kalico 的 `klippy.log`（如果未配置日志文件则输出到 stderr）。

### 测试

以 `test/klippy_testing_plugin.py` 参考测试插件为模板。
使用 `scripts/test_klippy.py` 运行测试。

---

## 从 `extras/` 迁移到 `plugins/`

如果你在 `klippy/extras/` 中已有模块，想迁移到 `klippy/plugins/` 以保持 Kalico 仓库干净：

### 自动迁移

使用插件安装器并指定本地路径：

```
python scripts/install_plugin.py /path/to/your/local/plugin --name my_plugin
```

详见[使用插件安装器](#使用插件安装器)。

### 手动迁移步骤

1. **移动文件。** 将 `klippy/extras/my_module.py` → `klippy/plugins/my_module.py`。

2. **检查导入。** 如果你的模块从 `klippy.extras.*` 导入，这些导入已经是
   完全限定的，**不需要修改**。`extras/` 和 `plugins/` 模块都在 `klippy` 包下。

3. **从 extras 中删除。** 从 `klippy/extras/` 中删除原文件。

4. **添加配置段。** 确保 `printer.cfg` 中有 `[my_module]`。

5. **启用覆盖（如适用）。** 如果你要替换同名的内置模块，
   在 `[danger_options]` 中添加 `allow_plugin_override: True`。

6. **重启 Kalico。** 运行 `RESTART` 或重启 Kalico 服务。

### 何时使用 `allow_plugin_override`

只有当你的插件名称与已有的 extra 模块名称**完全相同时**才需要。
对于独特的插件名称，不需要覆盖标志。

---

## 使用插件安装器

Kalico 提供了 `scripts/install_plugin.py`，一个自动化获取、分析和安装
git 仓库插件的工具。

### 基本用法

```bash
python scripts/install_plugin.py <url> [options]
```

| 选项 | 说明 |
|------|------|
| `--branch <name>` | 克隆指定 git 分支（默认：默认分支） |
| `--name <name>` | 强制指定安装后的模块名称（默认：从仓库推断） |
| `--force` | 覆盖已有的同名插件 |
| `--dry-run` | 仅分析和报告，不安装任何文件 |

### 工作流程

1. 将 git 仓库克隆到临时目录。
2. 扫描插件文件 —— 包含 `load_config` 或 `load_config_prefix` 的任何 `.py` 文件。
3. 检测正确的安装布局（单文件 vs 子包）。
4. 使用 AST 分析发现：
   - **G-code 命令**：任何 `gcode.register_command("CMD", ...)` 调用
   - **依赖关系**：任何 `printer.lookup_object("name")` 或
     `printer.load_object(config, "name")` 调用
5. 将插件复制到 `klippy/plugins/<module_name>/`。
6. 打印友好的安装摘要。

### 示例输出

```
Fetching plugin from https://github.com/user/kalico-my-cool-sensor...

[1/4] Cloning repository... done.
[2/4] Scanning for plugin modules...
       Found: my_cool_sensor.py (entry: load_config)
[3/4] Analyzing plugin...
       G-code commands detected: COOL_CALIBRATE, COOL_REPORT
       Dependencies detected: gcode, heaters, toolhead
[4/4] Installing to klippy/plugins/...
       klippy/plugins/my_cool_sensor.py installed.

========================================
 Plugin installed: my_cool_sensor
========================================

  Source:        https://github.com/user/kalico-my-cool-sensor
  Install path:  klippy/plugins/my_cool_sensor.py
  Entry point:   load_config(config)

  Available G-code commands:
    COOL_CALIBRATE    → calibrate the cool sensor
    COOL_REPORT       → report current readings

  Required config section (add to printer.cfg):
    [my_cool_sensor]
    sensor_pin: PA0
    # see the plugin's README for full options

  Dependencies (ensure these exist in your config):
    gcode
    heaters
    toolhead

  To activate: send RESTART to Kalico
========================================
```

### 从本地目录安装

你也可以将安装器指向本地路径，将插件从 `extras/` 迁移过来：

```bash
python scripts/install_plugin.py ./klippy/extras/my_module.py --name my_module
```

### 从 GitHub 仓库安装

```bash
# 默认分支
python scripts/install_plugin.py https://github.com/user/kalico-my-plugin

# 指定分支或标签
python scripts/install_plugin.py https://github.com/user/kalico-my-plugin --branch v1.2.0
```

---

## 完整示例

以下是基于 `test/klippy_testing_plugin.py` 的完整插件示例。
它注册了一个自定义 G-code 命令 `ASSERT`，用于评估 Jinja2 表达式。

```python
# klippy/plugins/assert_plugin.py
#
# 评估表达式，如果为 False 则报错。
# 用法：ASSERT TEST="{1 + 1 == 2}"

import ast
from klippy.extras.gcode_macro import Template


class AssertPlugin:
    def __init__(self, config):
        self.printer = config.get_printer()
        gcode = self.printer.lookup_object("gcode")
        self.gcode_macro = self.printer.load_object(config, "gcode_macro")

        self.printer.register_event_handler(
            "gcode:command_error", self._on_command_error
        )
        self.printer.register_event_handler(
            "gcode:unknown_command", self._on_unknown_command
        )
        gcode.register_command("ASSERT", self.cmd_ASSERT)

    def _on_command_error(self):
        self.printer.request_exit("error_exit")
        self.printer.invoke_shutdown("测试期间发生异常")

    def _on_unknown_command(self, cmd):
        self.printer.request_exit("error_exit")
        self.printer.invoke_shutdown(
            f"测试期间出现未知命令: {cmd}"
        )

    def cmd_ASSERT(self, gcmd):
        expression = gcmd.get("TEST")
        try:
            template = Template(
                self.printer,
                self.gcode_macro.env,
                "ASSERT:runtime_expression",
                expression,
            )
        except Exception:
            raise gcmd.error(f"ASSERT: 无法解析 '{expression}'")

        context = self.gcode_macro.create_template_context()
        result = template.render(context)
        value = ast.literal_eval(result) if result else None

        if not value:
            raise gcmd.error(f"ASSERT: {expression} == {value}")


def load_config(config):
    return AssertPlugin(config)
```

`printer.cfg` 中的配置：

```ini
[assert_plugin]
```

---

## 故障排除

### "Module 'xxx' found in both extras and plugins!"

你的插件与内置模块同名。要么：
- 将插件重命名为唯一的名称，或者
- 在 `[danger_options]` 中添加 `allow_plugin_override: True`

### "Unable to load module 'xxx'"

配置中有 `[xxx]` 段，但在 `extras/` 或 `plugins/` 中找不到名为 `xxx` 的模块。请检查：
- 文件名完全匹配（例如 `my_tool.py` → `[my_tool]`）
- 文件在 `klippy/plugins/` 中
- 没有 Python 语法错误

### "Unknown config object 'xxx'"

你调用了 `printer.lookup_object("xxx")` 但模块 `xxx` 尚未加载。要么：
- 将查找移到 `"klippy:connect"` 事件处理函数中
- 先用 `printer.load_object(config, "xxx")` 强制加载

### 插件在 LIST_MODULES 中不显示

- 确保文件放在 `klippy/plugins/<name>.py`（精确路径）
- 重启 Kalico（需要 `RESTART`——不支持动态重新加载）
- 检查 `klippy.log` 中的 Python 导入错误

### 在 LIST_MODULES 中显示为 "unused"

模块已被加载，但没有配置段引用它。在 `printer.cfg` 中添加 `[module_name]`。
没有这个配置段，模块会被导入但永远不会实例化。
