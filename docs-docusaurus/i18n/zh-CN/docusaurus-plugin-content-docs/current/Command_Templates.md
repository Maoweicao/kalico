# 命令模板

本文档提供了在 gcode_macro（及类似）配置节中实现 G-Code 命令序列的相关信息。

## G-Code 宏命名

G-Code 宏名称不区分大小写 — MY_MACRO 和 my_macro 的计算结果相同，可以使用大写或小写调用。如果宏名称中使用了任何数字，则这些数字必须全部位于名称末尾（例如，TEST_MACRO25 是有效的，但 MACRO25_TEST3 则无效）。

## 配置中 G-Code 的格式化

在配置文件中定义宏时，缩进非常重要。要指定多行 G-Code 序列，每行都必须具有正确的缩进。例如：

```
[gcode_macro blink_led]
gcode:
  SET_PIN PIN=my_led VALUE=1
  G4 P2000
  SET_PIN PIN=my_led VALUE=0
```

请注意 `gcode:` 配置选项始终从行首开始，而 G-Code 宏中的后续行永远不从行首开始。

## 为宏添加描述

为了帮助识别功能，可以添加简短的描述。添加 `description:` 并附上简短的文本来描述功能。如果未指定，默认值为 "G-Code macro"。例如：

```
[gcode_macro blink_led]
description: Blink my_led one time
gcode:
  SET_PIN PIN=my_led VALUE=1
  G4 P2000
  SET_PIN PIN=my_led VALUE=0
```

当您使用 `HELP` 命令或自动完成功能时，终端将显示描述。

## 保存/恢复 G-Code 移动状态

不幸的是，G-Code 命令语言可能难以使用。移动工具头的标准机制是通过 `G1` 命令（`G0` 命令是 `G1` 的别名，可以互换使用）。但是，此命令依赖于 `M82`、`M83`、`G90`、`G91`、`G92` 和之前的 `G1` 命令设置的 "G-Code 解析状态"。创建 G-Code 宏时，最好在发出 `G1` 命令之前始终显式设置 G-Code 解析状态。（否则，`G1` 命令可能会发出不期望的请求。）

实现此目的的常用方法是将 `G1` 移动包装在 `SAVE_GCODE_STATE`、`G91` 和 `RESTORE_GCODE_STATE` 中。例如：

```
[gcode_macro MOVE_UP]
gcode:
  SAVE_GCODE_STATE NAME=my_move_up_state
  G91
  G1 Z10 F300
  RESTORE_GCODE_STATE NAME=my_move_up_state
```

`G91` 命令将 G-Code 解析状态置于"相对移动模式"，而 `RESTORE_GCODE_STATE` 命令将状态恢复到进入宏之前的状态。请务必在第一个 `G1` 命令上指定显式速度（通过 `F` 参数）。

## 模板扩展

gcode_macro 的 `gcode:` 配置节使用 Jinja2 模板语言或 Python 进行求值。

### Jinja2

可以通过将表达式包裹在 `{ }` 字符中在运行时对其进行求值，或使用包裹在 `{% %}` 中的条件语句。有关语法的更多信息，请参阅 [Jinja2 文档](http://jinja.pocoo.org/docs/2.10/templates/)。

复杂的 Jinja2 宏示例：
```
[gcode_macro clean_nozzle]
gcode:
  {% set wipe_count = 8 %}
  SAVE_GCODE_STATE NAME=clean_nozzle_state
  G90
  G0 Z15 F300
  {% for wipe in range(wipe_count) %}
    {% for coordinate in [(275, 4),(235, 4)] %}
      G0 X{coordinate[0]} Y{coordinate[1] + 0.25 * wipe} Z9.7 F12000
    {% endfor %}
  {% endfor %}
  RESTORE_GCODE_STATE NAME=clean_nozzle_state
```

此外，在宏上下文中，您可以使用 `RETURN` 提前结束宏执行。

#### Jinja2：宏参数

在调用宏时检查传递给宏的参数通常很有用。这些参数可通过 `params` 伪变量访问。例如，如果宏：

```
[gcode_macro SET_PERCENT]
gcode:
  M117 Now at { params.VALUE|float * 100 }%
```

被调用为 `SET_PERCENT VALUE=.2`，则将计算为 `M117 Now at 20%`。请注意，参数名称在宏中进行求值时始终为大写，并且始终作为字符串传递。如果执行数学运算，则必须将其显式转换为整数或浮点数。

通常使用 Jinja2 `set` 指令来使用默认参数，并将结果分配给本地名称。例如：

```
[gcode_macro SET_BED_TEMPERATURE]
gcode:
  {% set bed_temp = params.TEMPERATURE|default(40)|float %}
  M140 S{bed_temp}
```

#### Jinja2："rawparams" 变量

可以通过 `rawparams` 伪变量访问正在运行的宏的完整未解析参数。

请注意，这将包含原始命令中作为注释的部分。

有关如何使用 `rawparams` 覆盖 `M117` 命令的示例，请参阅 [sample-macros.cfg](../config/sample-macros.cfg) 文件。

#### Jinja2："printer" 变量

可以通过 `printer` 伪变量检查（和更改）打印机的当前状态。例如：

```
[gcode_macro slow_fan]
gcode:
  M106 S{ printer.fan.speed * 0.9 * 255}
```

可用字段在 [状态参考](Status_Reference.md) 文档中定义。

重要！宏首先被完整求值，然后才执行生成的命令。如果宏发出更改打印机状态的命令，则在宏求值期间不会看到该状态更改的结果。当宏生成调用其他宏的命令时，这也可能导致细微的行为差异，因为被调用的宏在被调用时进行求值（这是在调用宏的完整求值之后）。

按照惯例，`printer` 后面的名称是配置节的名称。因此，例如，`printer.fan` 指的是 `[fan]` 配置节创建的风扇对象。此规则有一些例外 - 特别是 `gcode_move` 和 `toolhead` 对象。如果配置节包含空格，则可以通过 `[ ]` 访问器访问它 - 例如：`printer["generic_heater my_chamber_heater"].temperature`。

请注意，Jinja2 `set` 指令可以将本地名称分配给 `printer` 层次结构中的对象。这可以使宏更具可读性并减少输入。例如：
```
[gcode_macro QUERY_HTU21D]
gcode:
    {% set sensor = printer["htu21d my_sensor"] %}
    M117 Temp:{sensor.temperature} Humidity:{sensor.humidity}
```

### Python

模板也可以用 Python 代码编写。如果行以 `!` 为前缀，模板将自动解释为 Python。
注意：不能混合使用 Python 和 Jinja2。

复杂的 Python 宏示例：
```
[gcode_macro clean_nozzle]
gcode:
  !wipe_count = 8
  !emit("G90")
  !emit("G0 Z15 F300")
  !for wipe in range(wipe_count):
  !  for coordinate in [(275, 4), (235, 4)]:
  !    emit(f"G0 X{coordinate[0]} Y{coordinate[1] + 0.25 * wipe} Z9.7 F12000")
```

为便于编写 Python 宏，可以从 `.py` 文件中读取它们。宏的 Python 类型存根也可在 `klippy.macro` 下找到。

```
## printer.cfg

[gcode_macro clean_nozzle]
gcode: !!include my_macros/clean_nozzle.py

## my_macros/clean_nozzle.py

wipe_count = 8
emit("G90")
emit("G0 Z15 F300")
...

```

#### Python：宏参数

传递给 Python 宏的参数存储在 `params` 变量中。

```
[gcode_macro PARAMETER_EXAMPLE]
gcode:
  !respond_info(f"{params}")
```

#### Python：Rawparams

```
[gcode_macro G4]
rename_existing: G4.1
gcode:
  !if rawparams and "S" in rawparams:
  !  s = int(rawparams.split("S")[1])
  !  respond_info(f"Sleeping for {s} seconds")
  !  emit(f"G4.1 P{s * 1000}")
  !else:
  !  p = int(rawparams.split("P")[1])
  !  respond_info(f"Sleeping for {p/1000} seconds")
  !  emit(f"G4.1 {rawparams}")
```

#### Python：变量

```
[gcode_macro POKELOOP]
variable_count: 10
variable_speed: 3
gcode:
  !for i in range(own_vars.count):
  !  emit(f"BEACON_POKE SPEED={own_vars.speed} TOP=5 BOTTOM=-0.3")
```

#### Python：打印机对象

```
[gcode_macro EXTRUDER_TEMP]
gcode:
    !ACTUAL_TEMP = printer["extruder"]["temperature"]
    !TARGET_TEMP = printer["extruder"]["target"]
    !
    !respond_info("Extruder Target: %.1fC, Actual: %.1fC" % (TARGET_TEMP, ACTUAL_TEMP))
```

#### Python：辅助函数

- emit
- wait_while
- wait_until
- wait_moves
- blocking
- sleep
- set_gcode_variable
- emergency_stop / action_emergency_stop
- respond_info / action_respond_info
- raise_error / action_raise_error
- call_remote_method / action_call_remote_method
- math

## 操作

有一些可用的命令可以更改打印机的状态。例如，`{ action_emergency_stop() }` 会导致打印机进入关闭状态。请注意，这些操作在宏求值时执行，这可能在生成的 G-Code 命令执行之前很长时间。

可用的"操作"命令：
- `action_respond_info(msg)`：将给定的 `msg` 写入 /tmp/printer 伪终端。`msg` 的每一行都将带有 "// " 前缀发送。
- `action_log(msg)`：将给定的 msg 写入 klippy.log
- `action_raise_error(msg)`：中止当前宏（及所有调用宏）并将给定的 `msg` 写入 /tmp/printer 伪终端。`msg` 的第一行将带有 "!! " 前缀发送，后续行将带有 "// " 前缀。
- `action_emergency_stop(msg)`：将打印机转换为关闭状态。`msg` 参数是可选的，可用于描述关闭的原因。
- `action_call_remote_method(method_name)`：调用远程客户端注册的方法。如果方法接受参数，则应通过关键字参数提供，例如：`action_call_remote_method("print_stuff", my_arg="hello_world")`

## 变量

SET_GCODE_VARIABLE 命令可能有助于在宏调用之间保存状态。变量名称不得包含任何大写字符。例如：

```
[gcode_macro start_probe]
variable_bed_temp: 0
gcode:
  # 将目标温度保存到 bed_temp 变量
  SET_GCODE_VARIABLE MACRO=start_probe VARIABLE=bed_temp VALUE={printer.heater_bed.target}
  # 禁用热床加热器
  M140
  # 执行探测
  PROBE
  # 探测完成后调用 finish_probe 宏
  finish_probe

[gcode_macro finish_probe]
gcode:
  # 恢复温度
  M140 S{printer["gcode_macro start_probe"].bed_temp}
```

使用 SET_GCODE_VARIABLE 时，请务必考虑宏求值和命令执行的时间。

## 延迟 Gcode

[delayed_gcode] 配置选项可用于执行延迟 Gcode 序列：

```
[delayed_gcode clear_display]
description: Clear the LCD display message
gcode:
  M117

[gcode_macro load_filament]
description: Load 50mm of filament
gcode:
 G91
 G1 E50
 G90
 M400
 M117 Load Complete!
 UPDATE_DELAYED_GCODE ID=clear_display DURATION=10
```

当上面的 `load_filament` 宏执行时，它将在挤出完成后显示"Load Complete!"消息。Gcode 的最后一行启用 "clear_display" delayed_gcode，设置为 10 秒后执行。

`initial_duration` 配置选项可设置为在打印机启动时执行 delayed_gcode。倒计时在打印机进入"就绪"状态时开始。例如，以下 delayed_gcode 将在打印机就绪后 5 秒执行，使用"Welcome!"消息初始化显示屏：

```
[delayed_gcode welcome]
initial_duration: 5.
gcode:
  M117 Welcome!
```

可以通过在 gcode 选项中更新自身来重复执行 delayed gcode：

```
[delayed_gcode report_temp]
initial_duration: 2.
gcode:
  {action_respond_info("Extruder Temp: %.1f" % (printer.extruder0.temperature))}
  UPDATE_DELAYED_GCODE ID=report_temp DURATION=2
```

上述 delayed_gcode 将每 2 秒向 Octoprint 发送 "// Extruder Temp: [ex0_temp]"。可以使用以下 gcode 取消：


```
UPDATE_DELAYED_GCODE ID=report_temp DURATION=0
```

## 菜单模板

如果启用了 [display 配置节](Config_Reference.md#display)，则可以使用 [menu](Config_Reference.md#menu) 配置节来自定义菜单。

以下只读属性在菜单模板中可用：
* `menu.width` - 元素宽度（显示列数）
* `menu.ns` - 元素命名空间
* `menu.event` - 触发脚本的事件名称
* `menu.input` - 输入值，仅在输入脚本上下文中可用

以下操作在菜单模板中可用：
* `menu.back(force, update)`：将执行菜单返回命令，可选布尔参数 `<force>` 和 `<update>`。
  * 当 `<force>` 设置为 True 时，它还将停止编辑。默认值为 False。
  * 当 `<update>` 设置为 False 时，不会更新父容器项。默认值为 True。
* `menu.exit(force)` - 将执行菜单退出命令，可选布尔参数 `<force>`，默认值为 False。
  * 当 `<force>` 设置为 True 时，它还将停止编辑。默认值为 False。

### 菜单对话框

使用菜单对话框时，模板中还有其他只读属性。
* `dialog` - 值字典。键是元素 `id`（标识符的最后一部分）。禁用的元素的值为 `None`，否则使用 `input` 模板作为默认值。

[默认菜单集](../klippy/extras/display/menu.cfg) 中的 `[menu __main __setup __tuning __hotend_mpc_dialog]` 可用作构建更复杂对话框的参考。

## 将变量保存到磁盘

如果已启用 [save_variables 配置节](Config_Reference.md#save_variables)，则可以使用 `SAVE_VARIABLE VARIABLE=<name> VALUE=<value>` 将变量保存到磁盘，以便在重启之间使用。所有存储的变量在启动时加载到 `printer.save_variables.variables` 字典中，可在 Gcode 宏中使用。为避免行过长，可以在宏顶部添加以下内容：
```
{% set svv = printer.save_variables.variables %}
```

例如，它可以用于保存 2 合 1 出料热端的状态，并在开始打印时确保使用活动挤出机，而不是 T0：

```
[gcode_macro T1]
gcode:
  ACTIVATE_EXTRUDER extruder=extruder1
  SAVE_VARIABLE VARIABLE=currentextruder VALUE='"extruder1"'

[gcode_macro T0]
gcode:
  ACTIVATE_EXTRUDER extruder=extruder
  SAVE_VARIABLE VARIABLE=currentextruder VALUE='"extruder"'

[gcode_macro START_GCODE]
gcode:
  {% set svv = printer.save_variables.variables %}
  ACTIVATE_EXTRUDER extruder={svv.currentextruder}
```
