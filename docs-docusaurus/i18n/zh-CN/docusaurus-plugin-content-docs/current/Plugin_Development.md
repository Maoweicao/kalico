# 插件开发指南

本文档描述了如何为 Kalico 开发、安装和管理插件。插件允许您扩展 Kalico 的功能，而无需修改核心源代码树，确保您的自定义设置在更新后仍然有效。

## 目录

- [概述](#概述)
- [快速开始](#快速开始)
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
- [调试和自省](#调试和自省)
- [从 `extras/` 迁移到 `plugins/`](#从-extras-迁移到-plugins)
- [使用插件安装程序](#使用插件安装程序)
- [完整示例](#完整示例)
- [故障排除](#故障排除)

---

## 概述

Kalico 的插件系统遵循**约定优于配置**的设计。插件不是 XML 清单、JSON 元数据或插件注册表，而是一个放在 `klippy/plugins/` 中的 Python 模块（`.py` 文件或子包）。文件的存在就是它的注册。

**核心概念：**

| 概念 | 描述 |
|------|------|
| **extras** | Kalico 附带的内置模块，位于 `klippy/extras/` |
| **plugins** | 用户/外部模块，位于 `klippy/plugins/`（git 不跟踪） |
| **PrinterModule** | 发现模块的包装器；处理延迟加载、错误跟踪 |
| **配置部分** | `printer.cfg` 中触发模块实例化的 `[name]` 或 `[name suffix]` 条目 |
| **Printer.objects** | 所有实例化模块实例所在的中心 OrderedDict |

### 关键设计决策

- **没有启用/禁用列表。** 只有当对应的 `[section]` 出现在 `printer.cfg` 中时，插件才会被加载。没有它，模块会被导入但永远不会实例化（在 `LIST_MODULES` 中标记为 "unused"）。
- **`plugins/` 目录不被 git 跟踪。** 它在上游 Kalico 树中不存在。可以自由地将文件放在这里——不会弄乱 git 树。
- **插件覆盖受到控制。** 如果插件与内置 extra 同名，除非在 `[danger_options]` 中设置了 `allow_plugin_override: True`，否则 Kalico 会引发错误。这可以防止意外覆盖。

---

## 快速开始

创建文件 `klippy/plugins/my_tool.py`：

```python
class MyTool:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.name = config.get_name()
        gcode = self.printer.lookup_object("gcode")
        gcode.register_command("MY_COMMAND", self.cmd_MY_COMMAND)
        self.printer.register_event_handler("klippy:ready", self._on_ready)

    def _on_ready(self):
        pass  # 需要连接打印机的初始化

    def cmd_MY_COMMAND(self, gcmd):
        gcmd.respond_info("Hello from my_tool!")

def load_config(config):
    return MyTool(config)
```

添加到 `printer.cfg`：

```ini
[my_tool]
```

重启 Kalico。从控制台运行 `MY_COMMAND`——您应该看到 "Hello from my_tool!"。

---

## 插件目录结构

```
klippy/
├── extras/                  # 内置模块（Kalico 核心的一部分）
│  ├── __init__.py
│  ├── respond.py
│  └── ...
├── plugins/                 # 用户插件（git 不跟踪）
│  ├── __init__.py          # 包标记（始终存在）
│  ├── my_tool.py           # 单文件插件
│  ├── my_complex_plugin/   # 子包插件
│  │  ├── __init__.py      # 包含 load_config / load_config_prefix
│  │  ├── helpers.py
│  │  └── sensor.py
│  └── ...
```

### 单文件与子包

| 样式 | 何时使用 | 示例 |
|------|----------|------|
| **单 `.py` 文件** | 简单插件，没有辅助文件 | `my_tool.py` |
| **带 `__init__.py` 的子包** | 具有多个模块、辅助程序或数据文件的插件 | `my_complex_plugin/` |

两种样式都会自动发现。模块名称是文件名（不带 `.py`）或目录名。

### 导入规则

您的插件位于 `klippy.plugins` 包内。当您需要从内置 extra 导入时，请使用完整的 `klippy.extras.*` 路径：

```python
from klippy.extras.gcode_macro import Template  # 正确
from klippy.extras.servo import Servo            # 正确
```

您自己的子包内的相对导入按常规工作：

```python
from .helpers import my_helper                   # 在您的子包内
```

---

## 架构

下图显示了关键组件如何交互：

![插件架构图](/img/plugin-architecture.svg)

- **printer.cfg** 提供 `[section]` 定义和选项值。
- **ConfigWrapper** 包装每个部分，提供类型化访问（`get()`、`getfloat()`、`getint()` 等）。
- 您的 **Plugin** 实现 `load_config(config)` 或 `load_config_prefix(config)`，接收一个 `ConfigWrapper`。
- **Printer** 充当**服务定位器**——您的插件按名称拉取依赖项：
  - `printer.lookup_object("gcode")` ——获取已注册的服务
  - `printer.load_object(config, "heaters")` ——延迟加载另一个模块
  - `printer.register_event_handler("klippy:ready", cb)` ——订阅事件
  - `printer.lookup_components("load_cell_sensors")` ——查询子系统注册表

---

## 生命周期

![插件生命周期](/img/plugin-lifecycle.svg)

### 阶段详情

**阶段 1 - 发现** (`printer.py:_load_modules`)
通过 `pkgutil.iter_modules()` 发现 `klippy/extras/` 和 `klippy/plugins/` 中的所有 `*.py` 文件。每个文件都成为一个存储在 `printer.printer_modules` 中的 `PrinterModule`。如果插件与现有 extra 同名，除非设置了 `allow_plugin_override: True`，否则 Kalico 会引发错误。

**阶段 2 - 加载** (`printer.py:_load_modules`)
每个 `PrinterModule.load()` 调用 `importlib.import_module(module_info.name)`。导入期间的异常被捕获并存储——只有在模块实际使用时才会引发错误。这意味着从未在 `printer.cfg` 中引用的损坏插件不会使启动崩溃。

**阶段 3 - 组件注册** (`printer.py:_register_subsystem_components`)
如果模块定义了 `register_components(subsystem)`，则会调用它来填充命名子系统注册表。这是可选的，由提供类似驱动程序组件的插件使用（例如，负载单元子系统的传感器类型）。

**阶段 4 - 配置初始化** (`printer.py:_read_config`)
对于 `printer.cfg` 中的每个 `[section]`，`printer.load_object(config, section)` 找到匹配的 `PrinterModule` 并调用其 `load_config(config)` 或 `load_config_prefix(config)`。返回的实例存储在 `printer.objects` 中。配置部分必须在此阶段读取所有参数；未读取的参数将被标记为错误。

**阶段 5 - 连接** (`printer.py:_connect`)
在所有模块实例化后，`"klippy:connect"` 事件触发。将此阶段用于跨模块查找、配置验证和硬件握手。

**阶段 6 - 就绪** (`printer.py:_connect`)
在所有连接处理程序完成后，`"klippy:ready"` 事件触发。打印机现在可以处理 G-code 命令了。不要在此处引发错误。

**阶段 7 - 关机/重启** (`printer.py:run`)
在 `RESTART` 或 `FIRMWARE_RESTART` 时，`Printer` 和 `Reactor` 被销毁并从头重新创建。所有模块都被重新导入和重新初始化。没有热插拔机制——需要重启。

---

## 插件 API 参考

每个插件模块必须至少暴露以下模块级函数之一：

### `load_config(config)` ——对象

```python
def load_config(config):
    return MyPlugin(config)
```

当 `printer.cfg` 包含 `[my_plugin]`（精确匹配，无后缀）时调用。接收该部分的 `ConfigWrapper`。必须返回构造的对象。

### `load_config_prefix(config)` ——对象

```python
def load_config_prefix(config):
    return MyPlugin(config)
```

为 `[my_plugin instance1]`、`[my_plugin instance2]` 等部分调用（前缀匹配，模块名称和后缀之间用空格分隔）。启用同一模块的多个实例。

### `register_components(subsystem)` （可选）

```python
def register_components(subsystem):
    subsystem.register_component("my_subsystem", "my_component", MyDriver)
```

在启动期间调用，将命名组件注册到子系统注册表中。有关详细信息，请参阅 [子系统组件注册](#子系统组件注册)。

### `ConfigWrapper` API

```python
value = config.get("option_name", default=None)
flag  = config.getboolean("bool_option", False)
num   = config.getfloat("float_option", 1.0, minval=0.0, maxval=10.0)
count = config.getint("int_option", 5, minval=0)
choice = config.getchoice("mode", {"fast": 1, "slow": 2}, "fast")
name  = config.get_name()         # 完整部分名称，例如 "my_plugin instance1"
printer = config.get_printer()    # Printer 服务定位器
section = config.getsection("subsection")  # 获取嵌套部分
```

---

## 子系统组件注册

一些插件不是"独立模块"，而是为更大的子系统提供组件。例如，每个 ADC 传感器驱动程序将自己注册到 `"load_cell_sensors"` 子系统中，主 `[load_cell]` 配置部分使用 `config.getchoice("sensor_type", sensors)` 让用户选择。

### 提供者端（注册到子系统）

```python
# 在插件的 register_components() 中：
def register_components(subsystem):
    subsystem.register_component(
        "my_subsystem",           # 子系统名称（字符串键）
        "my_driver_v1",           # 组件名称（在配置中向用户显示）
        MyDriverClass             # 组件（类、函数或值）
    )
```

有关真实示例，请参阅 `klippy/extras/load_cell/__init__.py:14`。

### 消费者端（从子系统查找）

```python
sensors = printer.lookup_components("my_subsystem")  # -> {"my_driver_v1": MyDriverClass, ...}
chosen = config.getchoice("driver_type", sensors)    # 用户从选项中选择
instance = chosen(config)                             # 实例化所选内容
```

---

## 服务定位器模式

Kalico 使用**服务定位器**（拉取式）模式，而不是依赖注入（推送式）。您的插件负责从 `Printer` 实例拉取其依赖项。

### `Printer` 上的关键方法

```python
# 获取 Printer 实例的引用
printer = config.get_printer()

# 按配置部分名称查找先前注册的对象
gcode = printer.lookup_object("gcode")
toolhead = printer.lookup_object("toolhead")

# 延迟加载另一个模块（后续调用返回缓存实例）
heaters = printer.load_object(config, "heaters")

# 查询子系统组件注册表
components = printer.lookup_components("load_cell_sensors")

# 获取反应器（用于定时器、文件 I/O、休眠）
reactor = printer.get_reactor()

# 获取启动参数
args = printer.get_start_args()

# 检查打印机是否处于关机状态
if printer.is_shutdown():
    return
```

### 为什么是拉取式？

- 初始化顺序不简单——当您的插件构造时，并非所有模块都存在。将查找推迟到事件处理程序（例如 `"klippy:connect"`）以避免缺少依赖项。
- `gcode` 和 `pins` 对象始终可以早期获取。
- 使用 `printer.load_object(config, "module_name")` 强制加载依赖项。

---

## 生命周期事件

注册事件处理程序以挂钩到 Kalico 的生命周期：

```python
printer.register_event_handler("event_name", callback_function)
```

### 标准事件

| 事件 | 阶段 | 常见用途 |
|------|------|----------|
| `"klippy:connect"` | 所有模块实例化后 | 跨模块查找、配置验证、硬件检查 |
| `"klippy:ready"` | 打印机完全可操作 | 开始自动例程、启用功能 |
| `"klippy:disconnect"` | 重启/关机期间 | 关闭文件、套接字、清理资源 |
| `"klippy:shutdown"` | 错误/故障关机 | 安全停止硬件、记录状态 |
| `"klippy:firmware_restart"` | 固件重启前 | 在 MCU 重置前保存状态 |
| `"klippy:mcu_identify"` | MCU 识别阶段 | 注册依赖于 MCU 的对象 |
| `"gcode:command_error"` | G-code 解析错误 | 自定义错误恢复 |
| `"gcode:unknown_command"` | 无法识别的 G-code | 实现自定义命令解析 |

### 事件处理程序准则

```python
def _handle_connect(self):
    # 安全：查找其他对象
    self.toolhead = self.printer.lookup_object("toolhead")

def _handle_ready(self):
    # 安全：启动操作、发送命令
    # 不要在此处引发错误

def _handle_shutdown(self):
    try:
        self.motor.stop()
    except:
        pass  # 抑制关机期间的错误
```

---

## G-code 命令注册

在模块的 `__init__` 中注册自定义 G-code 命令：

```python
class MyPlugin:
    def __init__(self, config):
        self.gcode = self.printer.lookup_object("gcode")
        self.gcode.register_command("MY_CMD", self.cmd_MY_CMD, "Description for help")

    def cmd_MY_CMD(self, gcmd):
        # 读取参数
        speed = gcmd.get_float("S", 0.0)
        value = gcmd.get("PARAM", "default")

        # 响应控制台
        gcmd.respond_info(f"Got S={speed}, PARAM={value}")

        # 对无效输入引发错误
        if speed < 0:
            raise gcmd.error("Speed must be positive")
```

### `gcmd` 对象 API

```python
gcmd.get("NAME", default=None)           # 字符串参数
gcmd.get_float("S", default=0., minval=0)  # 浮点参数
gcmd.get_int("N", default=0, minval=0)   # 整数参数
gcmd.respond_info("message")             # 标准响应
gcmd.respond_raw("raw text")             # 原始输出
gcmd.error("error message")              # 引发错误（中止命令）
```

---

## Webhooks / 远程 API

为外部客户端（Mainsail、Fluidd 等）公开 JSON-RPC 端点：

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

### 用于自动状态暴露的 `get_status()`

在打印机对象上定义 `get_status()` 以通过 API 服务器和 Jinja 模板自动暴露其状态：

```python
class MyPlugin:
    def get_status(self):
        return {
            "value": self.current_value,
            "active": self.is_active,
        }
```

状态值必须是：`int`、`float`、`str`、`bool`、`list`、`dict`、`tuple` 或 `None`。列表和字典必须被视为不可变——如果内容更改，请返回新对象。

---

## 配置

### 基本部分

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

您的 `load_config_prefix()` 为每个实例接收单独的 `ConfigWrapper`。

### 插件覆盖

如果您的插件与内置 extra 同名（例如，您创建了 `klippy/plugins/respond.py`），您必须启用覆盖：

```ini
[danger_options]
allow_plugin_override: True
```

没有这个，Kalico 会引发错误：`"Module 'respond' found in both extras and plugins!"`。

### 包含其他配置文件

在插件的配置中使用 `!!include` 来引入更大的配置：

```ini
[my_tool]
!!include path/to/my_tool_defaults.cfg
custom_option: my_value
```

---

## 最佳实践

1. **不要使用全局变量。** 将所有状态存储在打印机对象实例中。`RESTART` 会重新创建 `Printer`，全局变量会泄漏状态。

2. **在 `__init__` 中分配所有成员变量。** 避免动态创建属性——在构造函数中使用 `self.xyz = None`。

3. **为浮点数使用浮点常量。** 优先使用 `self.speed = 1.` 而不是 `self.speed = 1`，使用 `self.speed = 2. * x` 而不是 `self.speed = 2 * x`。这可以避免微妙的 Python 类型转换错误。

4. **在构造期间读取所有配置选项。** 在 `__init__` 期间未读取的参数将被标记为拼写错误并导致配置错误。

5. **不要访问其他模块的 `_` 前缀成员。** 这些是私有实现细节，可能会在不通知的情况下更改。

6. **将繁重的工作推迟到事件处理程序。** 使用 `"klippy:connect"` 查找可能尚不存在的模块，使用 `"klippy:ready"` 执行需要完全初始化打印机的操作。

7. **在断开连接时关闭文件/套接字。** 注册 `"klippy:disconnect"`：

   ```python
   self.printer.register_event_handler("klippy:disconnect", self._cleanup)
   ```

8. **在关机处理程序中抑制错误。** 在紧急关机期间，记录错误并吞没异常比阻塞关机序列更好。

---

## 调试和自省

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
- **source**：`"plugins"` 或 `"extras"` ——模块来自哪里
- **loaded**：模块是否已成功导入（任何导入错误都在此报告）
- **used**：是否有任何 `printer.cfg` 部分引用此模块
- **error**：如果加载失败，异常详细信息（仅在 `loaded: False` 时显示）

### 日志记录

```python
import logging

logging.info("Informational message")
logging.warning("Warning message")
logging.exception("Exception traceback")  # 在 except 块中
```

日志输出将进入 Kalico 的 `klippy.log`（如果没有配置日志文件，则进入 stderr）。

### 测试

使用 `test/klippy_testing_plugin.py` 中的参考测试插件作为模板。使用 `scripts/test_klippy.py` 运行测试。

---

## 从 `extras/` 迁移到 `plugins/`

如果您在 `klippy/extras/` 中有一个现有模块，想要将其移动到 `klippy/plugins/` 以保持 Kalico 树的整洁：

### 自动迁移

使用带有本地路径的插件安装程序：

```
python scripts/install_plugin.py /path/to/your/local/plugin --name my_plugin
```

有关详细信息，请参阅 [使用插件安装程序](#使用插件安装程序)。

### 手动迁移步骤

1. **移动文件。** 将 `klippy/extras/my_module.py` 复制到 `klippy/plugins/my_module.py`。

2. **检查导入。** 如果您的模块从 `klippy.extras.*` 导入，这些导入已经是完全限定的，**不需要更改**。`extras/` 和 `plugins/` 模块都在 `klippy` 包下。

3. **从 extras 中删除。** 从 `klippy/extras/` 中删除原始文件。

4. **添加配置部分。** 确保您的 `printer.cfg` 具有 `[my_module]`。

5. **启用覆盖（如果适用）。** 如果您正在替换同名的内置模块，请在 `[danger_options]` 中添加 `allow_plugin_override: True`。

6. **重启 Kalico。** 运行 `RESTART` 或重启 Kalico 服务。

### 何时使用 `allow_plugin_override`

仅当您的插件名称**匹配**现有 extra 模块名称时。对于唯一的插件名称，不需要覆盖标志。

---

## 使用插件安装程序

Kalico 附带 `scripts/install_plugin.py`，这是一个自动化从 git 仓库获取、分析和安装插件的工具。

### 基本用法

```bash
python scripts/install_plugin.py <url> [options]
```

| 选项 | 描述 |
|------|------|
| `--branch <name>` | 克隆特定的 git 分支（默认：默认分支） |
| `--name <name>` | 强制已安装模块的名称（默认：从仓库推断） |
| `--force` | 覆盖同名的现有插件 |
| `--dry-run` | 分析并报告而不安装 |

### 它的工作原理

1. 将 git 仓库克隆到临时目录。
2. 扫描插件文件——任何包含 `load_config` 或 `load_config_prefix` 的 `.py` 文件。
3. 检测正确的安装布局（单文件与子包）。
4. 使用 AST 分析发现：
   - **G-code 命令**：任何对 `gcode.register_command("CMD", ...)` 的调用
   - **依赖项**：任何对 `printer.lookup_object("name")` 或 `printer.load_object(config, "name")` 的调用
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
    COOL_CALIBRATE    - calibrate the cool sensor
    COOL_REPORT       - report current readings

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

您也可以将安装程序指向本地路径以从 `extras/` 迁移插件：

```bash
python scripts/install_plugin.py ./klippy/extras/my_module.py --name my_module
```

### 从 GitHub 仓库安装

```bash
# 默认分支
python scripts/install_plugin.py https://github.com/user/kalico-my-plugin

# 特定分支或标签
python scripts/install_plugin.py https://github.com/user/kalico-my-plugin --branch v1.2.0
```

---

## 完整示例

以下是基于 `test/klippy_testing_plugin.py` 的完整插件示例。它注册了一个自定义 G-code 命令 `ASSERT`，该命令评估 Jinja2 表达式。

```python
# klippy/plugins/assert_plugin.py
#
# 评估表达式，如果为 False 则引发错误。
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
        self.printer.invoke_shutdown("Exception during testing")

    def _on_unknown_command(self, cmd):
        self.printer.request_exit("error_exit")
        self.printer.invoke_shutdown(
            f"Unknown command during test: {cmd}"
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
            raise gcmd.error(f"ASSERT: Failed to parse '{expression}'")

        context = self.gcode_macro.create_template_context()
        result = template.render(context)
        value = ast.literal_eval(result) if result else None

        if not value:
            raise gcmd.error(f"ASSERT: {expression} == {value}")


def load_config(config):
    return AssertPlugin(config)
```

在 `printer.cfg` 中的配置：

```ini
[assert_plugin]
```

---

## 故障排除

### "Module 'xxx' found in both extras and plugins!"

您的插件与内置模块同名。要么：
- 将插件重命名为唯一的名称，或者
- 在 `[danger_options]` 中添加 `allow_plugin_override: True`

### "Unable to load module 'xxx'"

配置有 `[xxx]` 部分，但在 `extras/` 或 `plugins/` 中未找到名为 `xxx` 的模块。请检查：
- 文件名完全匹配（例如 `my_tool.py` 对应 `[my_tool]`）
- 文件在 `klippy/plugins/` 中
- 没有 Python 语法错误

### "Unknown config object 'xxx'"

您调用了 `printer.lookup_object("xxx")`，但模块 `xxx` 尚未加载。要么：
- 将查找移动到 `"klippy:connect"` 事件处理程序
- 使用 `printer.load_object(config, "xxx")` 先强制加载它

### "Plugin not showing in LIST_MODULES"

- 确保文件放在 `klippy/plugins/<name>.py`（精确路径）
- 重启 Kalico（需要 `RESTART`——不支持动态重新加载）
- 检查 `klippy.log` 中的 Python 导入错误

### "Unused" in LIST_MODULES

您的模块已加载，但没有配置部分引用它。在您的 `printer.cfg` 中添加 `[module_name]`。没有这个，模块会被导入但永远不会实例化。