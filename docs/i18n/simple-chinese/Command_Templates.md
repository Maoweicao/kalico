# 命令模板

本文档提供有关在 gcode_macro（和类似的）配置部分中实现 G-Code 命令序列的信息。

## G-Code 宏命名

G-Code 宏名称不区分大小写——MY_MACRO 和 my_macro 将计算结果相同，
可以以任一大小写调用。如果在宏名称中使用任何数字，则它们必须全部
在名称末尾（例如，TEST_MACRO25 有效，但 MACRO25_TEST3 无效）。

## 配置中的 G-Code 格式

在配置文件中定义宏时，缩进很重要。要指定多行 G-Code 序列，
每行必须具有正确的缩进。例如：

```
[gcode_macro blink_led]
gcode:
  SET_PIN PIN=my_led VALUE=1
  G4 P2000
  SET_PIN PIN=my_led VALUE=0
```

请注意 `gcode:` 配置选项始终从行的开头开始，
G-Code 宏中的后续行永远不会从开头开始。

## 添加描述到您的宏

为了帮助识别功能，可以添加简短描述。
添加 `description:` 并加上简短文本以描述功能。
如果未指定，默认为"G-Code macro"。
例如：

```
[gcode_macro blink_led]
description: Blink my_led one time
gcode:
  SET_PIN PIN=my_led VALUE=1
  G4 P2000
  SET_PIN PIN=my_led VALUE=0
```

当您使用 `HELP` 命令或自动完成功能时，终端将显示描述。

## 保存/恢复 G-Code 移动的状态

不幸的是，G-Code 命令语言的使用可能很有挑战性。
移动工具头的标准机制是通过 `G1` 命令（`G0` 命令是 `G1` 的别名，
可以与其互换使用）。但是，该命令依赖于由 `M82`、`M83`、`G90`、`G91`、`G92`
和之前的 `G1` 命令设置的"G-Code 解析状态"。创建 G-Code 宏时，
最好始终在发出 `G1` 命令之前显式设置 G-Code 解析状态。
（否则，`G1` 命令有可能会发出不希望的请求。）

一个常见的方法是使用 `SAVE_GCODE_STATE`、`G91` 和 `RESTORE_GCODE_STATE`
来包装 `G1` 移动。例如：

```
[gcode_macro MOVE_UP]
gcode:
  SAVE_GCODE_STATE NAME=my_move_up_state
  G91
  G1 Z10 F300
  RESTORE_GCODE_STATE NAME=my_move_up_state
```

`G91` 命令将 G-Code 解析状态放入"相对移动模式"，
`RESTORE_GCODE_STATE` 命令将状态恢复为进入宏之前的状态。
确保在第一个 `G1` 命令上指定明确的速度（通过 `F` 参数）。

## 模板展开

gcode_macro `gcode:` 配置部分使用 Jinja2 模板语言或 Python 进行评估。

### Jinja2

可以通过将表达式包装在 `{ }` 字符中或使用包装在 `{% %}`
中的条件语句来在运行时评估表达式。有关语法的更多信息，
请参阅 [Jinja2 文档](http://jinja.pocoo.org/docs/2.10/templates/)。

复杂 Jinja2 宏的示例：
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

此外，在宏上下文中，您可以使用 `RETURN` 来提前结束宏执行。

#### Jinja2：宏参数

检查传递给宏时的参数通常很有用。
这些参数可通过 `params` 伪变量获得。例如，如果宏：

```
[gcode_macro SET_PERCENT]
gcode:
  M117 Now at { params.VALUE|float * 100 }%
`````````

在调用时为 `SET_PERCENT VALUE=.2`，它将计算为 `M117 Now at 20%`。
请注意，在宏中评估时参数名称始终大写，
并始终作为字符串传递。如果执行数学运算，则必须显式转换为整数或浮点数。

通常使用 Jinja2 `set` 指令来使用默认参数并将结果分配给本地名称。
例如：

```
[gcode_macro SET_BED_TEMPERATURE]
gcode:
  {% set bed_temp = params.TEMPERATURE|default(40)|float %}
  M140 S{bed_temp}
```

#### Jinja2：rawparams 变量

可以通过 `rawparams` 伪变量访问正在运行的宏的完整未解析参数。

请注意，这将包括作为原始命令的一部分的任何注释。

请参阅 [sample-macros.cfg](../config/sample-macros.cfg) 文件以获得
显示如何使用 `rawparams` 覆盖 `M117` 命令的示例。

#### Jinja2 "printer" 变量

可以通过 `printer` 伪变量检查（和修改）打印机的当前状态。
例如：

```
[gcode_macro slow_fan]
gcode:
  M106 S{ printer.fan.speed * 0.9 * 255}
```

可用字段在 [状态参考](Status_Reference.md) 文档中定义。

重要！宏首先完整评估，然后执行生成的命令。
如果宏发出改变打印机状态的命令，该状态更改的结果在宏评估期间将不可见。
当宏生成调用其他宏的命令时，这也会导致微妙的行为，
因为被调用的宏是在调用时评估的（在调用宏的整个评估之后）。

按照惯例，`printer` 之后立即出现的名称是配置部分的名称。
因此，例如，`printer.fan` 指的是 `[fan]` 配置部分创建的 fan 对象。
这个规则有一些例外——特别是 `gcode_move` 和 `toolhead` 对象。
如果配置部分名称中包含空格，可以通过 `[ ]` 访问器访问它——例如：
`printer["generic_heater my_chamber_heater"].temperature`。

请注意，Jinja2 `set` 指令可以将本地名称分配给 `printer` 层次结构中的对象。
这可以使宏更易读且减少输入。例如：
```
[gcode_macro QUERY_HTU21D]
gcode:
    {% set sensor = printer["htu21d my_sensor"] %}
    M117 Temp:{sensor.temperature} Humidity:{sensor.humidity}
```

### Python

模板也可以用 Python 代码编写。如果行前缀为 `!`，模板将自动
被解释为 Python。注意：您不能混合 Python 和 Jinja2。

复杂 Python 宏的示例：
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

为了便于编写 python 宏，可以从 `.py` 文件中读取它们。
Python 类型 stubs for macros 也可在 `klippy.macro` 下获得。

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

传递给 python 宏的参数存储在 `params` 变量中。

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

#### Python：助手

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

有一些命令可用来改变打印机的状态。
例如，`{ action_emergency_stop() }` 将导致打印机进入关闭状态。
请注意，这些操作在宏被评估时进行，这可能在生成的 g-code 命令
执行前相隔显著的时间。

可用的"操作"命令：
- `action_respond_info(msg)`: 将给定的 `msg` 写入
  /tmp/printer 伪终端。`msg` 的每一行都将使用"// "前缀发送。
- `action_log(msg)`: 将给定的 msg 写入 klippy.log
- `action_raise_error(msg)`: 中止当前宏（和任何调用宏）
  并将给定的 `msg` 写入 /tmp/printer 伪终端。`msg` 的第一行
  将使用"!! "前缀发送，后续行将具有"// "前缀。
- `action_emergency_stop(msg)`: 将打印机转移到关闭状态。
  `msg` 参数是可选的，可能用于描述关闭的原因。
- `action_call_remote_method(method_name)`: 调用由远程客户端
  注册的方法。如果方法需要参数，应通过关键字参数提供，
  即：`action_call_remote_method("print_stuff", my_arg="hello_world")`

## 变量

SET_GCODE_VARIABLE 命令可能对在宏调用之间保存状态很有用。
变量名可能不包含任何大写字符。例如：

```
[gcode_macro start_probe]
variable_bed_temp: 0
gcode:
  # Save target temperature to bed_temp variable
  SET_GCODE_VARIABLE MACRO=start_probe VARIABLE=bed_temp VALUE={printer.heater_bed.target}
  # Disable bed heater
  M140
  # Perform probe
  PROBE
  # Call finish_probe macro at completion of probe
  finish_probe

[gcode_macro finish_probe]
gcode:
  # Restore temperature
  M140 S{printer["gcode_macro start_probe"].bed_temp}
```

在使用 SET_GCODE_VARIABLE 时，请确保考虑宏评估和命令执行的时序。

## 延迟 Gcodes

[delayed_gcode] 配置选项可用于执行延迟的 gcode 序列：

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

当上面的 `load_filament` 宏执行时，它将在挤出完成后显示
"Load Complete!"消息。gcode 的最后一行启用"clear_display"
延迟 gcode，设置在 10 秒内执行。

`initial_duration` 配置选项可以设置为在打印机启动时执行延迟 gcode。
倒计时始于打印机进入"ready"状态时。例如，
下面的延迟 gcode 将在打印机准备好后 5 秒执行，
用"Welcome!"消息初始化显示：

```
[delayed_gcode welcome]
initial_duration: 5.
gcode:
  M117 Welcome!
```

延迟 gcode 可能会通过在 gcode 选项中更新自身来重复：

```
[delayed_gcode report_temp]
initial_duration: 2.
gcode:
  {action_respond_info("Extruder Temp: %.1f" % (printer.extruder0.temperature))}
  UPDATE_DELAYED_GCODE ID=report_temp DURATION=2
```

上面的延迟 gcode 每 2 秒将"// Extruder Temp: [ex0_temp]"
发送到 Octoprint。这可以用以下 gcode 取消：

```
UPDATE_DELAYED_GCODE ID=report_temp DURATION=0
```

## 菜单模板

如果启用了 [display 配置部分](Config_Reference.md#display)，
则可以使用 [menu](Config_Reference.md#menu) 配置部分自定义菜单。

以下只读属性可在菜单模板中使用：
* `menu.width` - 元素宽度（显示列数）
* `menu.ns` - 元素命名空间
* `menu.event` - 触发脚本的事件名称
* `menu.input` - 输入值，仅在输入脚本上下文中可用

以下操作可在菜单模板中使用：
* `menu.back(force, update)`: 将执行菜单返回命令，可选
  布尔参数 `<force>` 和 `<update>`。
  * 当 `<force>` 设置为 True 时，它也将停止编辑。默认
    值是 False。
  * 当 `<update>` 设置为 False 时，父容器项不会
    更新。默认值是 True。
* `menu.exit(force)` - 将执行菜单退出命令，可选
  布尔参数 `<force>` 默认值 False。
  * 当 `<force>` 设置为 True 时，它也将停止编辑。默认
    值是 False。

### 菜单对话框

使用菜单对话框时，模板中可用额外的只读属性。
* `dialog` - 值的字典。键是元素 `id`，其标识符的最后部分。
  禁用的元素值为 `None`，否则使用 `input` 模板作为默认值。

[default set of menus](../klippy/extras/display/menu.cfg) 中的
`[menu __main __setup __tuning __hotend_mpc_dialog]` 可用作
参考以建立更复杂的对话框。

## 将变量保存到磁盘

如果启用了 [save_variables 配置部分](Config_Reference.md#save_variables)，
可以使用 `SAVE_VARIABLE VARIABLE=<name> VALUE=<value>` 
将变量保存到磁盘，以便可以在重启时使用。所有存储的变量都在启动时
加载到 `printer.save_variables.variables` 字典中，可以在 gcode 宏中使用。
为了避免过长的行，可以在宏的顶部添加以下内容：
```
{% set svv = printer.save_variables.variables %}
```

例如，它可用于保存 2-in-1-out 热端的状态，并在开始打印时
确保使用活跃的挤出机，而不是 T0：

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