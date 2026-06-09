# 依赖自动禁用系统

Kalico 提供了一个依赖追踪和自动禁用系统，用于优雅地处理配置中的"过时引用"。
启用后，引用了不存在或已禁用的依赖对象的配置节将被自动禁用并显示警告，
而不是导致配置错误。

## 概述

在典型的打印机配置中，许多配置节依赖于其他配置节：

| 依赖对象 | 配置选项 | 引用的对象 |
|---|---|---|
| `[heater_fan]` | `heater:` | `PrinterHeaters` 可加热对象 |
| `[controller_fan]` | `heater:` / `stepper:` | 加热器和步进器使能线 |
| `[verify_heater]` | (每个加热器自动创建) | 父 `Heater` 对象 |
| `[homing_heaters]` | `heaters:` / `steppers:` | 加热器和运动学步进器 |
| `[extruder_stepper]` | `extruder:` | `PrinterExtruder` 对象 |
| `[temperature_combined]` | `sensor_list:` | 任何可报告温度的传感器 |
| `[tmcXXXX]` | (通过节名称) | 对应的 `[stepper]` 配置节 |
| `[belay]` | `extruder_stepper_name:` | 一个 `[extruder_stepper]` 配置节 |

默认情况下，如果引用的对象缺失，Kalico 会引发配置错误并阻止打印机启动。
当启用 `auto_disable_stale_refs` 后，缺失的依赖关系将导致依赖对象自动
禁用并显示警告，允许打印机以剩余的功能组件正常启动。

## 配置

将以下选项添加到 `[danger_options]` 部分：

```
[danger_options]
auto_disable_stale_refs: True
dependency_report_format: both
```

### 选项说明

| 选项 | 默认值 | 描述 |
|---|---|---|
| `auto_disable_stale_refs` | `False` | 启用过时依赖的自动禁用 |
| `dependency_report_format` | `none` | 报告格式: `none`, `tree`, `dot`, `both` |

当 `auto_disable_stale_refs` 为 `True` 时，`dependency_report_format` 默认为 `tree`。

## 启动报告

启用后，系统会在启动时打印依赖报告。示例：

```
=======================================================
DEPENDENCY DISABLE REPORT
=======================================================
The following objects were auto-disabled due to missing dependencies:
  [heater_fan case_fan] -> referenced 'heater extruder2' (heater) not found
  [controller_fan mcu_fan] -> referenced 'stepper stepper_z3' (stepper) not found
-------------------------------------------------------
DEPENDENCY TREE:
heater_bed (ACTIVE)
  verify_heater heater_bed (ACTIVE)
  heater_fan bed_fan (ACTIVE)
    heater extruder (ACTIVE)
extruder (ACTIVE)
  verify_heater extruder (ACTIVE)
  heater_fan hotend_fan (ACTIVE)
  temperature_fan part_cooling (ACTIVE)
  [DISABLED] heater_fan case_fan <- missing 'heater extruder2'
=======================================================
```

## DOT 图输出

当 `dependency_report_format` 设置为 `dot` 或 `both` 时，会在配置文件旁边
生成一个 Graphviz DOT 文件（如 `printer_deps.dot`）。可以使用以下命令渲染：

```bash
dot -Tpng printer_deps.dot -o printer_deps.png
```

图中：
- 黑色实线箭头：活跃的依赖关系
- 红色箭头：过时/缺失的依赖关系
- 粉色节点：被引用但不存在的对象

## 支持的依赖类型

| 类型 | 描述 | 涉及模块 |
|---|---|---|
| `heater` | 通过 `PrinterHeaters` 的加热器对象 | heater_fan, controller_fan, verify_heater, homing_heaters |
| `stepper` | 通过配置节或运动学的步进器对象 | controller_fan, homing_heaters, tmc |
| `extruder` | `PrinterExtruder` 对象 | extruder_stepper, belay |
| `sensor` | 可报告温度的对象 | temperature_combined |
| `auto` | 自动创建的依赖 | verify_heater (每个加热器) |
| `reference` | 通用对象引用 | 任何 `lookup_object` 调用 |

## 安全注意事项

1. **核心对象不会被自动禁用。** `toolhead`、`gcode`、`heaters`、`mcu`、
   `pins` 等是基础架构对象。如果这些缺失，无论此设置如何，打印机都无法启动。

2. **级联禁用。** 如果对象 A 依赖于 B，而 B 因缺失依赖 C 而被禁用，
   那么 A 也会被禁用。报告中会显示完整的依赖链。

3. **用户配置节不会自动创建。** 如果你配置了一个引用了不存在的加热器的
   `[heater_fan]`，风扇会被禁用，而不是加热器。缺失的加热器需要单独配置。

4. **系统在所有对象加载后运行。** 依赖报告在 `klippy:ready` 之后打印，
   此时所有对象都有机会注册它们的依赖关系。

## 使用场景

1. **开发/测试：** 启用此功能可以快速测试新的配置节，而无需所有依赖项都已配置。

2. **模块化配置：** 使用 `[include]` 在多台打印机之间共享配置。
   当共享配置中包含引用了某些打印机上不存在的硬件的配置节时，
   自动禁用可以防止错误。

3. **配置迁移：** 在升级或更换硬件时，自动禁用可帮助识别
   哪些配置节依赖于已被移除的组件。

4. **调试配置问题：** 依赖树报告精确显示了哪些对象依赖于哪些对象，
   使理解配置关系更加容易。
