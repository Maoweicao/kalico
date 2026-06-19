# G-Code

本文档描述了 Kalico 支持的命令。这些是可以在 OctoPrint 终端选项卡中输入的命令。

标记有 ⚠️ 的章节和命令表示新增的或与 Klipper 行为不同的命令

## G-Code 命令

Kalico 支持以下标准 G-Code 命令：
- 移动 (G0 或 G1): `G1 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>] [F<speed>]`
- 停顿: `G4 P<milliseconds>`
- 回到原点: `G28 [X] [Y] [Z]`
- 关闭电机: `M18` 或 `M84`
- 等待当前移动完成: `M400`
- 使用绝对/相对距离进行挤出: `M82`, `M83`
- 使用绝对/相对坐标: `G90`, `G91`
- 设置位置: `G92 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>]`
- 设置速度因子覆盖百分比: `M220 S<percent>`
- 设置挤出因子覆盖百分比: `M221 S<percent>`
- 设置加速度: `M204 S<value>` 或 `M204 P<value> T<value>`
  - 注意：如果未指定 S 且同时指定了 P 和 T，则加速度设置为 P 和 T 中的较小值。如果仅指定了 P 或 T 中的一个，该命令无效。
- 获取挤出机温度: `M105`
- 设置挤出机温度: `M104 [T<index>] [S<temperature>]`
- 设置挤出机温度并等待: `M109 [T<index>] S<temperature>`
  - 注意：M109 始终等待温度稳定到请求值
- 启用冷挤出: `M302 [T<index>] [P<enable>] [S<min_extrude_temp>]`
- 设置热床温度: `M140 [S<temperature>]`
- 设置热床温度并等待: `M190 S<temperature>`
  - 注意：M190 始终等待温度稳定到请求值
- 设置风扇速度: `M106 S<value>`
- 关闭风扇: `M107`
- 紧急停止: `M112`
- 获取当前位置: `M114`
- 获取固件版本: `M115`

有关上述命令的更多详细信息，请参阅 [RepRap G-Code 文档](http://reprap.org/wiki/G-code)。

Kalico 的目标是支持常见第三方软件（例如 OctoPrint、Printrun、Slic3r、Cura 等）在其标准配置中生成的 G-Code 命令。支持所有可能的 G-Code 命令并非目标。相反，Kalico 更倾向于使用人类可读的 ["扩展 G-Code 命令"](#additional-commands)。同样，G-Code 终端输出仅设计为人类可读——如果需要从外部软件控制 Kalico，请参阅 [API 服务器文档](API_Server.md)。

如果需要使用不太常见的 G-Code 命令，可以通过自定义 [gcode_macro 配置部分](Config_Reference.md#gcode_macro) 来实现。例如，可以使用此方法实现：`G12`、`G29`、`G30`、`G31`、`M42`、`M80`、`M81`、`T1` 等。

## 附加命令

Kalico 使用"扩展" G-Code 命令进行常规配置和状态查询。这些扩展命令都遵循类似的格式——它们以命令名称开头，后面可跟一个或多个参数。例如：`SET_SERVO SERVO=myservo ANGLE=5.3`。在本文档中，命令和参数以大写字母显示，但它们不区分大小写。（因此，"SET_SERVO" 和 "set_servo" 运行的是同一个命令。）

本节按 Kalico 模块名称组织，通常遵循 [打印机配置文件](Config_Reference.md) 中指定的部分名称。请注意，某些模块会自动加载。

### [adxl345]

当启用 [adxl345 配置部分](Config_Reference.md#adxl345) 时，可以使用以下命令。

#### ACCELEROMETER_MEASURE
`ACCELEROMETER_MEASURE [CHIP=<config_name>] [NAME=<value>]`：以请求的每秒采样数开始加速度计测量。如果未指定 CHIP，则默认为 "adxl345"。该命令在启动-停止模式下工作：第一次执行时开始测量，下次执行时停止测量。测量结果写入名为 `/tmp/adxl345-<chip>-<name>.csv` 的文件，其中 `<chip>` 是加速度计芯片的名称（来自 `[adxl345 my_chip_name]` 的 `my_chip_name`），`<name>` 是可选的 NAME 参数。如果未指定 NAME，则默认为 "YYYYMMDD_HHMMSS" 格式的当前时间。如果加速度计在配置部分中没有名称（仅为 `[adxl345]`），则名称中不会生成 `<chip>` 部分。

#### ACCELEROMETER_QUERY
`ACCELEROMETER_QUERY [CHIP=<config_name>] [RATE=<value>] [SAMPLES=<value>] [RETURN=<value>]`：查询加速度计的当前值。如果未指定 CHIP，则默认为 "adxl345"。如果未指定 RATE，则使用默认值。此命令可用于测试与 ADXL345 加速度计的连接：返回的值之一应为自由落体加速度（正负一些芯片噪声）。`SAMPLES` 参数可用于设置从传感器采样多次读数。读数将取平均值。默认是采集单个样本。`RETURN` 参数可取值 `vector`（默认）或 `tilt`。在 `vector` 模式下，返回原始自由落体加速度向量。在 `tilt` 模式下，计算并显示垂直于自由落体向量的平面的 X 和 Y 角度。

#### ACCELEROMETER_DEBUG_READ
`ACCELEROMETER_DEBUG_READ [CHIP=<config_name>] REG=<register>`：查询 ADXL345 寄存器 "register"（例如 44 或 0x2C）。可用于调试目的。

#### ACCELEROMETER_DEBUG_WRITE
`ACCELEROMETER_DEBUG_WRITE [CHIP=<config_name>] REG=<register> VAL=<value>`：将原始 "value" 写入寄存器 "register"。"value" 和 "register" 都可以是十进制或十六进制整数。请谨慎使用，并参考 ADXL345 数据手册。

### [angle]

当启用 [angle 配置部分](Config_Reference.md#angle) 时，可以使用以下命令。

#### ANGLE_CALIBRATE
`ANGLE_CALIBRATE CHIP=<chip_name>`：对给定传感器执行角度校准（必须有一个指定了 `stepper` 参数的 `[angle chip_name]` 配置部分）。重要提示——此工具将命令步进电机移动，而不检查正常的运动边界限制。理想情况下，在执行校准之前应将电机与任何打印机滑车断开连接。如果步进电机无法与打印机断开连接，请确保在开始校准之前滑车靠近其导轨的中心。（步进电机在此测试期间可能正向或反向移动两个完整旋转。）完成此测试后，使用 `SAVE_CONFIG` 命令将校准数据保存到配置文件。要使用此工具，必须安装 Python "numpy" 包（有关更多信息，请参阅 [测量谐振文档](Measuring_Resonances.md#software-installation)）。

#### ANGLE_CHIP_CALIBRATE
`ANGLE_CHIP_CALIBRATE CHIP=<chip_name>`：如果已实现，执行内部传感器校准（MT6826S/MT6835）。

- **MT68XX**：校准前应将电机与任何打印机滑车断开连接。校准后，应通过断开电源来重置传感器。

#### ANGLE_DEBUG_READ
`ANGLE_DEBUG_READ CHIP=<config_name> REG=<register>`：查询传感器寄存器 "register"（例如 44 或 0x2C）。可用于调试目的。仅适用于 tle5012b 芯片。

#### ANGLE_DEBUG_WRITE
`ANGLE_DEBUG_WRITE CHIP=<config_name> REG=<register> VAL=<value>`：将原始 "value" 写入寄存器 "register"。"value" 和 "register" 都可以是十进制或十六进制整数。请谨慎使用，并参考传感器数据手册。仅适用于 tle5012b 芯片。

### [axis_twist_compensation]

当启用 [axis_twist_compensation 配置部分](Config_Reference.md#axis_twist_compensation) 时，可以使用以下命令。

#### AXIS_TWIST_COMPENSATION_CALIBRATE
`AXIS_TWIST_COMPENSATION_CALIBRATE [AXIS=<X|Y>] [SAMPLE_COUNT=<value>] [<probe_parameter>=<value>]`：

通过指定目标轴或启用自动校准来校准轴扭转补偿。

- **SAMPLE_COUNT：** 校准期间测试的点数。如果未指定，则默认为 3。

- **AXIS：** 定义将进行扭转补偿校准的轴（`X` 或 `Y`）。如果未指定，则轴默认为 `'X'`。

### [bed_mesh]

当启用 [bed_mesh 配置部分](Config_Reference.md#bed_mesh) 时（另请参阅 [热床网格指南](Bed_Mesh.md)），可以使用以下命令。

#### BED_MESH_CALIBRATE
`BED_MESH_CALIBRATE [PROFILE=<name>] [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>] [<mesh_parameter>=<value>] [ADAPTIVE=1] [ADAPTIVE_MARGIN=<value>]`：此命令使用配置中参数指定的生成点探测热床。探测后，生成网格并根据网格调整 Z 运动。网格将保存到 `PROFILE` 参数指定的配置文件中，如果未指定则为 `default`。有关可选探测参数的详细信息，请参阅 PROBE 命令。如果指定 METHOD=manual，则激活手动探测工具——有关此工具处于活动状态时可用的其他命令，请参阅上方的 MANUAL_PROBE 命令。可选的 `HORIZONTAL_MOVE_Z` 值覆盖配置文件中指定的 `horizontal_move_z` 选项。如果指定 ADAPTIVE=1，则将使用正在打印的 Gcode 文件中定义的对象来定义探测区域。可选的 `ADAPTIVE_MARGIN` 值覆盖配置文件中指定的 `adaptive_margin` 选项。

#### BED_MESH_OUTPUT
`BED_MESH_OUTPUT PGP=[<0:1>]`：此命令将当前探测的 Z 值和当前网格值输出到终端。如果指定 PGP=1，则 bed_mesh 生成的 X、Y 坐标及其关联索引将输出到终端。

#### BED_MESH_MAP
`BED_MESH_MAP`：与 BED_MESH_OUTPUT 类似，此命令将当前网格状态打印到终端。它不是以人类可读的格式打印值，而是以 JSON 格式序列化状态。这允许 OctoPrint 插件轻松捕获数据并生成近似热床表面的高度图。

#### BED_MESH_CLEAR
`BED_MESH_CLEAR`：此命令清除网格并移除所有 Z 调整。建议将其放入结束 GCode 中。

#### BED_MESH_PROFILE
`BED_MESH_PROFILE LOAD=<name> SAVE=<name> REMOVE=<name>`：此命令提供网格状态的配置文件管理。LOAD 将从与提供的名称匹配的配置文件恢复网格状态。SAVE 将当前网格状态保存到与提供的名称匹配的配置文件。REMOVE 将从持久存储中删除与提供的名称匹配的配置文件。请注意，在运行 SAVE 或 REMOVE 操作后，必须运行 SAVE_CONFIG GCode 才能使对持久存储的更改生效。

#### BED_MESH_OFFSET
`BED_MESH_OFFSET [X=<value>] [Y=<value>] [ZFADE=<value]`：将 X、Y 和/或 ZFADE 偏移应用于网格查找。这对于具有独立挤出机的打印机很有用，因为工具切换后需要偏移才能产生正确的 Z 调整。请注意，ZFADE 偏移不会直接应用额外的 Z 调整，它用于在 Z 轴上应用了 `gcode offset` 时更正 `fade` 计算。

#### BED_MESH_CHECK
`BED_MESH_CHECK [MAX_DEVIATION=<value>] [MAX_SLOPE=<value>]`：根据指定标准验证当前热床网格。如果指定 MAX_DEVIATION，检查最高和最低网格点之间的差值是否不超过提供的值。如果指定 MAX_SLOPE，检查相邻网格点之间的最大斜率是否不超过提供的值（单位 mm/mm）。如果任何指定检查失败，命令将引发错误，或者如果所有检查通过，则显示确认网格有效的消息。如果未指定参数，命令将列出可用的验证检查。

### [bed_screws]

当启用 [bed_screws 配置部分](Config_Reference.md#bed_screws) 时（另请参阅 [手动调平指南](Manual_Level.md#adjusting-bed-leveling-screws)），可以使用以下命令。

#### BED_SCREWS_ADJUST
`BED_SCREWS_ADJUST`：此命令将调用热床螺丝调整工具。它将命令喷嘴移动到不同位置（如配置文件中定义的），并允许调整热床螺丝，使热床与喷嘴保持恒定距离。

### [bed_tilt]

当启用 [bed_tilt 配置部分](Config_Reference.md#bed_tilt) 时，可以使用以下命令。

#### BED_TILT_CALIBRATE
`BED_TILT_CALIBRATE [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`：此命令将探测配置中指定的点，然后推荐更新的 X 和 Y 倾斜调整。有关可选探测参数的详细信息，请参阅 PROBE 命令。如果指定 METHOD=manual，则激活手动探测工具——有关此工具处于活动状态时可用的其他命令，请参阅上方的 MANUAL_PROBE 命令。可选的 `HORIZONTAL_MOVE_Z` 值覆盖配置文件中指定的 `horizontal_move_z` 选项。

### [belay]

当启用 [belay 配置部分](Config_Reference.md#belay) 时，可以使用以下命令。

#### BELAY_ENABLE
`BELAY_ENABLE BELAY=<config_name>`：启用 `BELAY` 指定的 belay 补偿。

#### BELAY_DISABLE
`BELAY_DISABLE BELAY=<config_name>`：禁用 `BELAY` 指定的 belay 补偿。此设置不会在重启后保留。

#### QUERY_BELAY
`QUERY_BELAY BELAY=<config_name>`：查询 `BELAY` 指定的 belay 的状态。

#### BELAY_SET_MULTIPLIER
`BELAY_SET_MULTIPLIER BELAY=<config_name> [HIGH=<multiplier_high>] [LOW=<multiplier_low>]`：设置 `BELAY` 指定的 belay 的 multiplier_high 和/或 multiplier_low 的值，覆盖其来自相应 [belay 配置部分](Config_Reference.md#belay) 的值。通过此命令设置的值不会在重启后保留。

#### BELAY_SET_STEPPER
`BELAY_SET_STEPPER BELAY=<config_name> STEPPER=<extruder_stepper_name>`：选择将由 `BELAY` 指定的 belay 控制其倍率的 extruder_stepper。切换到新步进之前，将重置前一个步进的倍率。通过此命令进行的步进选择不会在重启后保留。仅当相应 [belay 配置部分](Config_Reference.md#belay) 中将 extruder_type 设置为 'extruder_stepper' 时，此命令才可用。

### [bltouch]

当启用 [bltouch 配置部分](Config_Reference.md#bltouch) 时（另请参阅 [BL-Touch 指南](BLTouch.md)），可以使用以下命令。

#### BLTOUCH_DEBUG
`BLTOUCH_DEBUG COMMAND=<command>`：向 BLTouch 发送命令。这可能对调试有用。可用命令有：`pin_down`、`touch_mode`、`pin_up`、`self_test`、`reset`。BL-Touch V3.0 或 V3.1 还可能支持 `set_5V_output_mode`、`set_OD_output_mode`、`output_mode_store` 命令。

#### BLTOUCH_STORE
`BLTOUCH_STORE MODE=<output_mode>`：将输出模式存储到 BLTouch V3.1 的 EEPROM 中。可用的 output_modes 有：`5V`、`OD`

### [configfile]

configfile 模块会自动加载。

#### SAVE_CONFIG
`SAVE_CONFIG [RESTART=0|1]`：此命令将覆盖主打印机配置文件并重启主机软件。此命令与其它校准命令配合使用以存储校准测试的结果。如果 RESTART 设置为 0，将不执行重启！！请谨慎使用！！

### [delayed_gcode]

如果启用了 [delayed_gcode 配置部分](Config_Reference.md#delayed_gcode)（另请参阅 [模板指南](Command_Templates.md#delayed-gcodes)），则启用以下命令。

#### UPDATE_DELAYED_GCODE
`UPDATE_DELAYED_GCODE [ID=<name>] [DURATION=<seconds>]`：更新已识别的 [delayed_gcode] 的延迟持续时间并启动 GCode 执行的计时器。值为 0 将取消待执行的延迟 GCode。

### [delta_calibrate]

当启用 [delta_calibrate] 配置部分时（另请参阅 [delta 校准指南](Delta_Calibrate.md)），可以使用以下命令。

#### DELTA_CALIBRATE
`DELTA_CALIBRATE [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`：此命令将探测热床上的七个点并推荐更新的限位位置、塔角度和半径。有关可选探测参数的详细信息，请参阅 PROBE 命令。如果指定 METHOD=manual，则激活手动探测工具——有关此工具处于活动状态时可用的其他命令，请参阅上方的 MANUAL_PROBE 命令。可选的 `HORIZONTAL_MOVE_Z` 值覆盖配置文件中指定的 `horizontal_move_z` 选项。

#### DELTA_ANALYZE
`DELTA_ANALYZE`：此命令用于增强型 delta 校准。有关详细信息，请参阅 [Delta 校准](Delta_Calibrate.md)。

### [display]

当启用 [display 配置部分](Config_Reference.md#gcode_macro) 时，可以使用以下命令。

#### SET_DISPLAY_GROUP
`SET_DISPLAY_GROUP [DISPLAY=<display>] GROUP=<group>`：设置 LCD 显示屏的活动显示组。这允许在配置中定义多个显示数据组，例如 `[display_data <group> <elementname>]`，并使用此扩展 GCode 命令在它们之间切换。如果未指定 DISPLAY，则默认为 "display"（主显示屏）。

### [display_status]

如果启用了 [display 配置部分](Config_Reference.md#display)，display_status 模块会自动加载。它提供以下标准 G-Code 命令：
- 显示消息：`M117 <message>`
- 设置构建百分比：`M73 P<percent>`

还提供以下扩展 G-Code 命令：
- `SET_DISPLAY_TEXT MSG=<message>`：执行与 M117 等效的操作，将提供的 `MSG` 设置为当前显示消息。如果省略 `MSG`，将清除显示。

## [dockable_probe]

除了 `[probe]` 的常规命令外，当启用 [dockable_probe 配置部分](Config_Reference.md#dockable_probe) 时（另请参阅 [可拆卸探针指南](Dockable_Probe.md)），还可以使用以下命令：

- `ATTACH_PROBE`：移动到停靠位置并将探针连接到工具头，连接后工具头将返回到之前的位置。
- `DETACH_PROBE`：移动到停靠位置并将探针从工具头上拆下，拆下后工具头将返回到之前的位置。
- `QUERY_DOCKABLE_PROBE`：响应当前探针状态。这可用于验证配置设置是否按预期工作。
- `SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0|1`：在需要探针的操作期间启用/禁用探针的自动连接/拆卸。
- `MOVE_TO_APPROACH_PROBE`：移动到接近探针停靠位置。
- `MOVE_TO_DOCK_PROBE`：移动到探针停靠位置（这应该触发探针连接）。
- `MOVE_TO_EXTRACT_PROBE`：在探针已连接的情况下移动离开停靠位置。
- `MOVE_TO_INSERT_PROBE`：在探针已连接的情况下移动到停靠位置附近的插入位置。
- `MOVE_TO_DETACH_PROBE`：远离停靠位置以将探针与工具头断开连接。
- `MOVE_AVOIDING_DOCK [X=<value>] [Y=<value>] [SPEED=<value>]`：移动到定义的点（绝对坐标），避开安全停靠区域

### [dual_carriage]

当启用 [dual_carriage 配置部分](Config_Reference.md#dual_carriage) 时，可以使用以下命令。

#### SET_DUAL_CARRIAGE
`SET_DUAL_CARRIAGE CARRIAGE=[0|1] [MODE=[PRIMARY|COPY|MIRROR]]`：此命令将更改指定滑车的模式。如果未提供 `MODE`，则默认为 `PRIMARY`。将模式设置为 `PRIMARY` 会停用另一个滑车并使指定滑车按原样执行后续 G-Code 命令。`COPY` 和 `MIRROR` 模式仅适用于 `CARRIAGE=1`。当设置为这些模式之一时，滑车 1 将跟踪滑车 0 的后续移动，并复制其相对移动（在 `COPY` 模式下）或以相反（镜像）方向执行它们（在 `MIRROR` 模式下）。

#### SAVE_DUAL_CARRIAGE_STATE
`SAVE_DUAL_CARRIAGE_STATE [NAME=<state_name>]`：保存双滑车的当前位置及其模式。保存和恢复 DUAL_CARRIAGE 状态在脚本和宏中很有用，也可用于归位例程覆盖。如果提供 NAME，则允许将保存的状态命名为给定的字符串。如果未提供 NAME，则默认为 "default"。

#### RESTORE_DUAL_CARRIAGE_STATE
`RESTORE_DUAL_CARRIAGE_STATE [NAME=<state_name>] [MOVE=[0|1] [MOVE_SPEED=<speed>]]`：恢复之前保存的双滑车位置及其模式，除非指定 "MOVE=0"，在这种情况下仅恢复保存的模式，而不恢复滑车的位置。如果正在恢复位置且指定了 "MOVE_SPEED"，则工具头移动将以给定速度（单位 mm/s）执行；否则工具头移动将使用导轨归位速度。请注意，滑车仅在其自己的轴上恢复位置，这对于正确恢复双滑车的 COPY 和 MIRROR 模式可能是必要的。

### [endstop_phase]

当启用 [endstop_phase 配置部分](Config_Reference.md#endstop_phase) 时（另请参阅 [限位相位指南](Endstop_Phase.md)），可以使用以下命令。

#### ENDSTOP_PHASE_CALIBRATE
`ENDSTOP_PHASE_CALIBRATE [STEPPER=<config_name>]`：如果未提供 STEPPER 参数，则此命令将报告过去归位操作中限位步进相位的统计数据。当提供 STEPPER 参数时，它会安排将给定的限位相位设置写入配置文件（与 SAVE_CONFIG 命令配合使用）。

### [exclude_object]

当启用 [exclude_object 配置部分](Config_Reference.md#exclude_object) 时（另请参阅 [排除对象指南](Exclude_Object.md)），可以使用以下命令：

#### `EXCLUDE_OBJECT`
`EXCLUDE_OBJECT [NAME=object_name] [CURRENT=1] [RESET=1]`：不带参数时，将返回当前所有被排除对象的列表。

当给出 `NAME` 参数时，指定的对象将被排除在打印之外。

当给出 `CURRENT` 参数时，当前对象将被排除在打印之外。

当给出 `RESET` 参数时，将清除被排除对象的列表。额外包含 `NAME` 将仅重置指定的对象。如果层已经被跳过，这**可能导致**打印失败。

#### `EXCLUDE_OBJECT_DEFINE`
`EXCLUDE_OBJECT_DEFINE [NAME=object_name [CENTER=X,Y] [POLYGON=[[x,y],...]] [RESET=1] [JSON=1]`：提供文件中对象的摘要。

不提供参数时，将列出 Kalico 已知的已定义对象。返回字符串列表，除非给出 `JSON` 参数，否则将以 JSON 格式返回对象详细信息。

当包含 `NAME` 参数时，定义要排除的对象。

  - `NAME`：此参数是必需的。它是此模块中其他命令使用的标识符。
  - `CENTER`：对象的 X,Y 坐标。
  - `POLYGON`：提供对象轮廓的 X,Y 坐标数组。

当提供 `RESET` 参数时，所有已定义的对象将被清除，`[exclude_object]` 模块将被重置。

#### `EXCLUDE_OBJECT_START`
`EXCLUDE_OBJECT_START NAME=object_name`：此命令接受一个 `NAME` 参数，表示当前层上对象 GCode 的开始。

#### `EXCLUDE_OBJECT_END`
`EXCLUDE_OBJECT_END [NAME=object_name]`：表示对象 GCode 层的结束。它与 `EXCLUDE_OBJECT_START` 配对。`NAME` 参数是可选的，仅当提供的名称与当前对象不匹配时才会发出警告。

### [extruder]

如果启用了 [extruder 配置部分](Config_Reference.md#extruder)，可以使用以下命令：

#### ACTIVATE_EXTRUDER
`ACTIVATE_EXTRUDER EXTRUDER=<config_name>`：在具有多个 [extruder](Config_Reference.md#extruder) 配置部分的打印机中，此命令更改活动喷头。

#### SET_PRESSURE_ADVANCE
`SET_PRESSURE_ADVANCE [EXTRUDER=<config_name>] [ADVANCE=<pressure_advance>] [SMOOTH_TIME=<pressure_advance_smooth_time>]`：设置挤出机步进的压力提前参数（如 [extruder](Config_Reference.md#extruder) 或 [extruder_stepper](Config_Reference.md#extruder_stepper) 配置部分中所定义）。如果未指定 EXTRUDER，则默认为活动喷头中定义的步进。

#### SET_EXTRUDER_ROTATION_DISTANCE
`SET_EXTRUDER_ROTATION_DISTANCE EXTRUDER=<config_name> [DISTANCE=<distance>]`：为提供的挤出机步进的 "rotation distance" 设置新值（如 [extruder](Config_Reference.md#extruder) 或 [extruder_stepper](Config_Reference.md#extruder_stepper) 配置部分中所定义）。如果旋转距离为负数，则步进运动将被反转（相对于配置文件中指定的步进方向）。更改的设置在 Kalico 重置后不会保留。请谨慎使用，因为微小的更改可能导致挤出机和喷头之间产生过大的压力。使用前请用耗材进行正确校准。如果未提供 'DISTANCE' 值，则此命令将返回当前旋转距离。

#### SYNC_EXTRUDER_MOTION
`SYNC_EXTRUDER_MOTION EXTRUDER=<name> MOTION_QUEUE=<name>`：此命令将使 EXTRUDER 指定的步进（如 [extruder](Config_Reference.md#extruder) 或 [extruder_stepper](Config_Reference.md#extruder_stepper) 配置部分中所定义）与 MOTION_QUEUE 指定的挤出机（如 [extruder](Config_Reference.md#extruder) 配置部分中所定义）的运动同步。如果 MOTION_QUEUE 是空字符串，则步进将与所有挤出机运动去同步。

### [mixing_extruder]

当启用 [mixingextruder 配置部分](Config_Reference.md#mixing_extruder) 时，可以使用以下命令：

#### SET_MIXING_EXTRUDER
`SET_MIXING_EXTRUDER [FACTORS=<factor1>[:<factor2>[:<factor3>...]]] [ENABLE=[0|1]]`：此命令激活指定的混合挤出机。后续 G1 命令使用因子定义的混合。FACTORS 通过提供多个正值来定义混合。值的数量应对应于配置中定义的步进数量。值在内部被归一化以加总为 1，相应步进的挤出量将乘以该值。如果省略 ENABLED，当前混合状态不会更改。如果既未提供 FACTORS 也未提供 ENABLE，则显示当前混合状态。

#### SET_MIXING_EXTRUDER_GRADIENT
`SET_MIXING_EXTRUDER_GRADIENT [START_FACTORS=<s1>[,<s2>[,<s3>...]] END_FACTORS=<e1>[,<e2>[,<e3>...]] START_HEIGHT=<start> END_HEIGHT=<end> [ENABLE=[0|1|RESET]] [METHOD=[linear|spherical] [VECTOR=<x>,<y>,<z>]]`：当提供 START_FACTORS、END_FACTORS、START_HEIGHT、END_HEIGHT 时，将添加渐变配置。START_FACTORS 定义 START_HEIGHT 以下及到 START_HEIGHT 的混合。END_FACTORS 分别定义从 END_HEIGHT 开始的混合。中间的混合是线性插值的。当 ENABLE 为 0 或 1 或指定 METHOD 时，混合渐变将关闭或开启，并选择应使用的渐变方法（METHOD）。启用时使用所有先前添加的渐变。可选的 VECTOR 配置取决于 METHOD 的参数：例如，对于 linear，VECTOR 定义向上方向；对于 spherical，它定义球体的原点。当 ENABLE 为 RESET 时，所有配置的渐变将被移除，渐变处理将被禁用。未提供参数时，显示当前混合渐变状态。

### [heated_fan]

当启用 [heated_fan](Config_Reference.md#heated_fan) 时，可以使用以下命令。

### SET_HEATED_FAN_TARGET
`SET_HEATED_FAN_TARGET TARGET=<temperature>`：覆盖 [heated_fan 配置部分](Config_Reference.md#heated_fan) 中的 `heater_temp` 设置，直到 Kalico 重启。对于切片软件在不同层设置不同的加热风扇温度很有用。

### [fan_generic]

当启用 [fan_generic 配置部分](Config_Reference.md#fan_generic) 时，可以使用以下命令。

#### SET_FAN_SPEED
`SET_FAN_SPEED FAN=config_name SPEED=<speed>` 此命令设置风扇的速度。"speed" 必须在 0.0 到 1.0 之间。

`SET_FAN_SPEED PIN=config_name TEMPLATE=<template_name> [<param_x>=<literal>]`：如果指定 `TEMPLATE`，则将 [display_template](Config_Reference.md#display_template) 分配给给定的风扇。例如，如果定义了 `[display_template my_fan_template]` 配置部分，则可以在此处分配 `TEMPLATE=my_fan_template`。display_template 应产生包含所需值的浮点数的字符串。模板将被持续评估，风扇将自动设置为结果速度。可以在模板评估期间设置 display_template 参数（参数将被解析为 Python 字面量）。如果 TEMPLATE 是空字符串，则此命令将清除分配给引脚的任何先前模板（然后可以使用 `SET_FAN_SPEED` 命令直接管理值）。

### [filament_switch_sensor]

当启用 [filament_switch_sensor](Config_Reference.md#filament_switch_sensor) 或 [filament_motion_sensor](Config_Reference.md#filament_motion_sensor) 配置部分时，可以使用以下命令。

#### QUERY_FILAMENT_SENSOR
`QUERY_FILAMENT_SENSOR SENSOR=<sensor_name>`：查询耗材传感器的当前状态。终端上显示的数据将取决于配置中定义的传感器类型。

#### SET_FILAMENT_SENSOR
###### 对于 filament_switch_sensor：
`SET_FILAMENT_SENSOR SENSOR=<sensor_name> [ENABLE=0|1] [RESET=0|1] [RUNOUT_DISTANCE=<mm>] [SMART=0|1] [ALWAYS_FIRE_EVENTS=0|1] [CHECK_ON_PRINT_START=0|1]`：设置耗材传感器的值。如果省略所有参数，将报告当前统计数据。 <br/>
ENABLE 设置耗材传感器的开/关。如果设置为 0，耗材传感器将被禁用；如果设置为 1，则启用。如果传感器状态发生变化，将触发重置。 <br/>
RESET 移除所有待处理的 runout_gcodes 和暂停，并强制重新评估传感器状态。 <br/>
RUNOUT_DISTANCE 设置 runout_distance。 <br/>
SMART 设置 smart 参数。 <br/>
ALWAYS_FIRE_EVENTS 设置 always_fire_events 参数，如果设置为 true，将触发传感器重置。 <br/>
CHECK_ON_PRINT_START 设置 check_on_print_start 参数。

###### 对于 filament_motion_sensor：
`SET_FILAMENT_SENSOR SENSOR=<sensor_name> [ENABLE=0|1] [RESET=0|1] [DETECTION_LENGTH=<mm>] [SMART=0|1] [ALWAYS_FIRE_EVENTS=0|1]`：设置耗材传感器的值。如果省略所有参数，将报告当前统计数据。 <br/>
ENABLE 设置耗材传感器的开/关。如果设置为 0，耗材传感器将被禁用；如果设置为 1，则启用。如果传感器之前被禁用且被启用，将触发重置。 <br/>
RESET 重置传感器状态并设置为检测到耗材。 <br/>
DETECTION_LENGTH 设置 detection_length，如果新的检测长度与旧的不同，将触发重置。 <br/>
SMART 设置 smart 参数。 <br/>
ALWAYS_FIRE_EVENTS 设置 always_fire_events 参数，不会触发重置。

### [firmware_retraction]

当启用 [firmware_retraction 配置部分](Config_Reference.md#firmware_retraction) 时，可以使用以下标准 G-Code 命令。这些命令允许利用许多切片软件中可用的固件回缩功能。回缩是一种在打印件一部分到另一部分的移动（非挤出）过程中减少拉丝的策略。请注意，在调整回缩参数之前应正确配置压力提前，以确保最佳结果。
- `G10`：使用当前配置的参数回缩耗材。如果 z_hop_height 设置为大于零的值，除了回缩耗材外，喷嘴还会抬升设定值。
- `G11`：使用当前配置的参数取消回缩耗材。如果 z_hop_height 设置为大于零的值，除了取消回缩耗材外，喷嘴还会以垂直运动降回打印件。

还提供以下附加命令。

#### SET_RETRACTION
`SET_RETRACTION [RETRACT_LENGTH=<mm>] [RETRACT_SPEED=<mm/s>] [UNRETRACT_EXTRA_LENGTH=<mm>] [UNRETRACT_SPEED=<mm/s>] [Z_HOP_HEIGHT=<mm>]`：调整固件回缩使用的参数。RETRACT_LENGTH 确定回缩的耗材长度（最小值和标准值均为 0 mm）。RETRACT_SPEED 确定耗材回缩移动的速度（最小值为 1 mm/s，标准值为 20 mm/s）。此值通常设置得相对较高（>40 mm/s），但 TPU 和 PETG 等柔软和/或易渗出的耗材除外（20 到 30 mm/s）。UNRETRACT_SPEED 设置耗材取消回缩移动的速度（最小值为 1 mm/s，标准值为 10 mm/s）。此参数不是特别关键，但通常低于 RETRACT_SPEED。UNRETRACT_EXTRA_LENGTH 允许向耗材取消回缩移动添加少量长度以填充喷嘴，或从耗材取消回缩移动中减去少量长度以减少接缝处的凸起（最小值为 -1 mm（1.75 mm 耗材的 2.41 mm3 体积），标准值为 0 mm）。Z_HOP_HEIGHT 确定喷嘴从打印件抬升的垂直高度，以防止在移动过程中与打印件碰撞（最小值为 0 mm，标准值为 0 mm，这会禁用 Z-Hop 移动）。如果在回缩时设置参数，新值仅在 G11 或 CLEAR_RETRACTION 事件后才会生效。SET_RETRACTION 通常作为切片软件每耗材配置的一部分设置，因为不同的耗材需要不同的参数设置。该命令可以在运行时发出。

#### GET_RETRACTION
`GET_RETRACTION`：查询固件回缩模块使用的当前参数以及回缩状态。RETRACT_LENGTH、RETRACT_SPEED、UNRETRACT_EXTRA_LENGTH、UNRETRACT_SPEED、Z_HOP_HEIGHT、RETRACT_STATE（如果回缩则为 True）、ZHOP_STATE（如果当前应用了 zhop 偏移则为 True）将显示在终端上。

#### CLEAR_RETRACTION
`CLEAR_RETRACTION`：在不移动挤出机或运动系统的情况下清除当前回缩状态。所有与回缩状态相关的标志都将重置为 False。

注意：当步进禁用时（M84，通常是结束 GCode 的一部分，也是 OctoPrint 在取消打印时的标准行为）或打印机归位时（G28，通常是开始 GCode 的一部分），zhop 状态也会重置为 False。因此，在结束或取消打印以及通过 GCode 流或虚拟 SD 卡开始新打印时，工具头不会应用 `z_hop_height`，直到下一次 G11（如果耗材已回缩）。尽管如此，建议在开始和结束 GCode 中添加 `CLEAR_RETRACTION`，以确保每次打印前后回缩状态都被重置。

#### RESET_RETRACTION
`RESET_RETRACTION`：通过先前 SET_RETRACTION 命令对回缩参数所做的所有更改都将重置为配置值。

注意：建议在开始和结束 GCode 中添加 `RESET_RETRACTION`（可能在耗材开始 GCode 中覆盖以通过 `SET_RETRACTION` 设置耗材特定的固件回缩默认值覆盖）。

### [force_move]

force_move 模块会自动加载，但某些命令需要在 [打印机配置](Config_Reference.md#force_move) 中设置 `enable_force_move`。

#### STEPPER_BUZZ
`STEPPER_BUZZ STEPPER=<config_name>`：将给定步进向前移动一毫米，然后向后移动一毫米，重复 10 次。这是一个诊断工具，用于帮助验证步进连接。

#### FORCE_MOVE
`FORCE_MOVE STEPPER=<config_name> DISTANCE=<value> VELOCITY=<value> [ACCEL=<value>]`：此命令将以给定的恒定速度（单位 mm/s）强制将给定步进移动给定距离（单位 mm）。如果指定 ACCEL 且大于零，则使用给定的加速度（单位 mm/s^2）；否则不执行加速度。不执行边界检查；不进行运动学更新；轴上的其他并行步进不会移动。请谨慎使用，因为不正确的命令可能导致损坏！使用此命令几乎肯定会将低级运动学置于不正确的状态；之后发出 G28 以重置运动学。此命令用于低级诊断和调试。

#### SET_KINEMATIC_POSITION
`SET_KINEMATIC_POSITION [X=<value>] [Y=<value>] [Z=<value>] [CLEAR=<[X][Y][Z]>]`：强制低级运动学代码相信工具头位于给定的笛卡尔位置。这是一个诊断和调试命令；对于常规轴变换，请使用 SET_GCODE_OFFSET 和/或 G28。如果未指定轴，则默认为头部最后命令的位置。设置不正确或无效的位置可能导致内部软件错误。使用 CLEAR 参数忘记给定轴的归位状态。请注意，CLEAR 不会覆盖先前的功能；如果未指定要清除的轴，其运动学位置将按上述方式设置。此命令可能使未来的边界检查失效；之后发出 G28 以重置运动学。

### [gcode]

gcode 模块会自动加载。

#### RESTART
`RESTART`：这将导致主机软件重新加载其配置并执行内部重置。此命令不会清除微控制器的错误状态（请参阅 FIRMWARE_RESTART），也不会加载新软件（请参阅 [FAQ](FAQ.md#how-do-i-upgrade-to-the-latest-software)）。

#### FIRMWARE_RESTART
`FIRMWARE_RESTART`：类似于 RESTART 命令，但它也会清除微控制器的所有错误状态。

#### HEATER_INTERRUPT
`HEATER_INTERRUPT`：中断 TEMPERATURE_WAIT 命令。

#### LOG_ROLLOVER
`LOG_ROLLOVER`：触发 klippy.log 滚动并生成新的日志文件。

#### STATUS
`STATUS`：报告 Kalico 主机软件状态。

#### HELP
`HELP`：报告可用的扩展 G-Code 命令列表。

### [gcode_arcs]

如果启用了 [gcode_arcs 配置部分](Config_Reference.md#gcode_arcs)，可以使用以下标准 G-Code 命令：
- 顺时针弧形移动 (G2)，逆时针弧形移动 (G3)：`G2|G3 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>] [F<speed>] I<value> J<value>|I<value> K<value>|J<value> K<value>`
- 弧平面选择：G17（XY 平面）、G18（XZ 平面）、G19（YZ 平面）

### [gcode_macro]

当启用 [gcode_macro 配置部分](Config_Reference.md#gcode_macro) 时（另请参阅 [命令模板指南](Command_Templates.md)），可以使用以下命令。

#### SET_GCODE_VARIABLE
`SET_GCODE_VARIABLE MACRO=<macro_name> VARIABLE=<name> VALUE=<value>`：此命令允许在运行时更改 gcode_macro 变量的值。提供的 VALUE 将被解析为 Python 字面量。

#### RELOAD_GCODE_MACROS
`RELOAD_GCODE_MACROS`：此命令读取配置文件并重新加载所有先前加载的 GCode 模板。它不会加载新的 `[gcode_macro]` 对象或卸载已删除的对象。使用 SET_GCODE_VARIABLE 修改的变量不受影响。

### [gcode_move]

gcode_move 模块会自动加载。

#### GET_POSITION
`GET_POSITION`：返回工具头当前位置的信息。有关更多信息，请参阅 [GET_POSITION 输出](Code_Overview.md#coordinate-systems) 的开发人员文档。

#### SET_GCODE_OFFSET
`SET_GCODE_OFFSET [X=<pos>|X_ADJUST=<adjust>] [Y=<pos>|Y_ADJUST=<adjust>] [Z=<pos>|Z_ADJUST=<adjust>] [MOVE=1 [MOVE_SPEED=<speed>]]`：设置应用于未来 G-Code 命令的位置偏移。这通常用于在切换挤出机时虚拟更改 Z 热床偏移或设置喷嘴 XY 偏移。例如，如果发送 "SET_GCODE_OFFSET Z=0.2"，则未来的 G-Code 移动将在其 Z 高度上增加 0.2mm。如果使用 X_ADJUST 样式参数，则调整将添加到任何现有偏移中（例如，"SET_GCODE_OFFSET Z=-0.2" 后跟 "SET_GCODE_OFFSET Z_ADJUST=0.3" 将导致总 Z 偏移为 0.1）。如果指定 "MOVE=1"，则将发出工具头移动以应用给定的偏移（否则偏移将在下一个指定给定轴的绝对 G-Code 移动时生效）。如果指定 "MOVE_SPEED"，则工具头移动将以给定速度（单位 mm/s）执行；否则工具头移动将使用最后指定的 G-Code 速度。

#### SAVE_GCODE_STATE
`SAVE_GCODE_STATE [NAME=<state_name>]`：保存当前 G-Code 坐标解析状态。保存和恢复 G-Code 状态在脚本和宏中很有用。此命令保存当前 G-Code 绝对坐标模式（G90/G91）、绝对挤出模式（M82/M83）、原点（G92）、偏移（SET_GCODE_OFFSET）、速度覆盖（M220）、挤出机覆盖（M221）、移动速度、当前 XYZ 位置和相对挤出机 "E" 位置。如果提供 NAME，则允许将保存的状态命名为给定的字符串。如果未提供 NAME，则默认为 "default"。

#### RESTORE_GCODE_STATE
`RESTORE_GCODE_STATE [NAME=<state_name>] [MOVE=1 [MOVE_SPEED=<speed>]]`：恢复通过 SAVE_GCODE_STATE 之前保存的状态。如果指定 "MOVE=1"，则将发出工具头移动以移回之前的 XYZ 位置。如果指定 "MOVE_SPEED"，则工具头移动将以给定速度（单位 mm/s）执行；否则工具头移动将使用恢复的 G-Code 速度。

### [hall_filament_width_sensor]

当启用 [tsl1401cl 耗材宽度传感器配置部分](Config_Reference.md#tsl1401cl_filament_width_sensor) 或 [hall 耗材宽度传感器配置部分](Config_Reference.md#hall_filament_width_sensor) 时（另请参阅 [TSLl401CL 耗材宽度传感器](TSL1401CL_Filament_Width_Sensor.md) 和 [Hall 耗材宽度传感器](Hall_Filament_Width_Sensor.md)），可以使用以下命令：

#### QUERY_FILAMENT_WIDTH
`QUERY_FILAMENT_WIDTH`：返回当前测量的耗材宽度。

#### RESET_FILAMENT_WIDTH_SENSOR
`RESET_FILAMENT_WIDTH_SENSOR`：清除所有传感器读数。在更换耗材后很有帮助。

#### DISABLE_FILAMENT_WIDTH_SENSOR
`DISABLE_FILAMENT_WIDTH_SENSOR`：关闭耗材宽度传感器并停止将其用于流量控制。

#### ENABLE_FILAMENT_WIDTH_SENSOR
`ENABLE_FILAMENT_WIDTH_SENSOR`：打开耗材宽度传感器并开始将其用于流量控制。

#### QUERY_RAW_FILAMENT_WIDTH
`QUERY_RAW_FILAMENT_WIDTH`：返回当前 ADC 通道读数和校准点的 RAW 传感器值。

#### ENABLE_FILAMENT_WIDTH_LOG
`ENABLE_FILAMENT_WIDTH_LOG`：开启直径日志记录。

#### DISABLE_FILAMENT_WIDTH_LOG
`DISABLE_FILAMENT_WIDTH_LOG`：关闭直径日志记录。

### [load_cell]

如果启用了 [load_cell 配置部分](Config_Reference.md#load_cell)，则启用以下命令。

### LOAD_CELL_DIAGNOSTIC
`LOAD_CELL_DIAGNOSTIC [LOAD_CELL=<config_name>]`：此命令收集 10 秒的 load cell 数据并报告可帮助您验证 load cell 正常工作的统计数据。此命令可在已校准和未校准的 load cell 上运行。

### LOAD_CELL_CALIBRATE
`LOAD_CELL_CALIBRATE [LOAD_CELL=<config_name>]`：启动引导式校准实用程序。校准是一个 3 步过程：
1. 首先从 load cell 上移除所有负载并运行 `TARE` 命令
2. 然后对 load cell 施加已知负载并运行 `CALIBRATE GRAMS=nnn` 命令
3. 最后使用 `ACCEPT` 命令保存结果

您可以随时使用 `ABORT` 取消校准过程。

### LOAD_CELL_TARE
`LOAD_CELL_TARE [LOAD_CELL=<config_name>]`：其工作原理类似于数字秤上的去皮按钮。它将 load cell 的当前原始读数设置为零点参考值。响应是传感器量程被读取的百分比和原始计数值。如果 load cell 已校准，还会报告以克为单位的力。

### LOAD_CELL_READ load_cell="name"
`LOAD_CELL_READ [LOAD_CELL=<config_name>]`：此命令从 load cell 获取读数。响应是传感器量程被读取的百分比和原始计数值。如果 load cell 已校准，还会报告以克为单位的力。


### [heaters]

如果在配置文件中定义了加热器，heaters 模块会自动加载。

#### TURN_OFF_HEATERS
`TURN_OFF_HEATERS`：关闭所有加热器。

#### TEMPERATURE_WAIT
`TEMPERATURE_WAIT SENSOR=<config_name> [MINIMUM=<target>] [MAXIMUM=<target>]`：等待给定的温度传感器达到或高于提供的 MINIMUM 和/或达到或低于提供的 MAXIMUM。

#### SET_HEATER_TEMPERATURE
`SET_HEATER_TEMPERATURE HEATER=<heater_name> [TARGET=<target_temperature>]`：设置加热器的目标温度。如果未提供目标温度，则目标为 0。

#### COLD_EXTRUDE
`COLD_EXTRUDE HEATER=<heater_name> [ENABLE=<0 or 1>] [MIN_EXTRUDE_TEMP=<min_extrude_temp>]`：启用或禁用冷挤出。如果未提供 ENABLE 和 MIN_EXTRUDE_TEMP，它将报告当前状态。如果 ENABLE 为 0，冷挤出被禁用；如果为 1，则启用。

#### SET_SMOOTH_TIME
`SET_SMOOTH_TIME HEATER=<heater_name> [SMOOTH_TIME=<smooth_time>] [SAVE_TO_PROFILE=0|1]`：设置指定加热器的 smooth_time。如果省略 SMOOTH_TIME，则 smooth_time 将重置为配置中的值。如果 SAVE_TO_PROFILE 设置为 1，新值将写入当前 PID_PROFILE。

### [idle_timeout]

idle_timeout 模块会自动加载。

#### SET_IDLE_TIMEOUT
`SET_IDLE_TIMEOUT [TIMEOUT=<timeout>]`：允许用户设置空闲超时时间（单位秒）。

### [input_shaper]

如果启用了 [input_shaper 配置部分](Config_Reference.md#input_shaper)（另请参阅 [谐振补偿指南](Resonance_Compensation.md)），则启用以下命令。

#### SET_INPUT_SHAPER
`SET_INPUT_SHAPER [SHAPER_FREQ_X=<shaper_freq_x>] [SHAPER_FREQ_Y=<shaper_freq_y>] [DAMPING_RATIO_X=<damping_ratio_x>] [DAMPING_RATIO_Y=<damping_ratio_y>] [SHAPER_TYPE=<shaper>] [SHAPER_TYPE_X=<shaper_type_x>] [SHAPER_TYPE_Y=<shaper_type_y>]`：修改输入整形器参数。请注意，SHAPER_TYPE 参数会重置 X 和 Y 轴的输入整形器，即使在 [input_shaper] 部分中配置了不同的整形器类型。SHAPER_TYPE 不能与 SHAPER_TYPE_X 和 SHAPER_TYPE_Y 参数一起使用。有关这些参数的更多详细信息，请参阅 [配置参考](Config_Reference.md#input_shaper)。

### [load_cell]

如果启用了 [load_cell 配置部分](Config_Reference.md#load_cell)，则启用以下命令。

### LOAD_CELL_DIAGNOSTIC
`LOAD_CELL_DIAGNOSTIC [LOAD_CELL=<config_name>]`：此命令收集 10 秒的 load cell 数据并报告可帮助您验证 load cell 正常工作的统计数据。此命令可在已校准和未校准的 load cell 上运行。

### LOAD_CELL_CALIBRATE
`LOAD_CELL_CALIBRATE [LOAD_CELL=<config_name>]`：启动引导式校准实用程序。校准是一个 3 步过程：
1. 首先从 load cell 上移除所有负载并运行 `TARE` 命令
2. 然后对 load cell 施加已知负载并运行 `CALIBRATE GRAMS=nnn` 命令
3. 最后使用 `ACCEPT` 命令保存结果

您可以随时使用 `ABORT` 取消校准过程。

### LOAD_CELL_TARE
`LOAD_CELL_TARE [LOAD_CELL=<config_name>]`：其工作原理类似于数字秤上的去皮按钮。它将 load cell 的当前原始读数设置为零点参考值。响应是传感器量程被读取的百分比和原始计数值。如果 load cell 已校准，还会报告以克为单位的力。

### LOAD_CELL_READ load_cell="name"
`LOAD_CELL_READ [LOAD_CELL=<config_name>]`：此命令从 load cell 获取读数。响应是传感器量程被读取的百分比和原始计数值。如果 load cell 已校准，还会报告以克为单位的力。

### [load_cell_probe]

如果启用了 [load_cell 配置部分](Config_Reference.md#load_cell_probe)，则启用以下命令。

### LOAD_CELL_TEST_TAP
`LOAD_CELL_TEST_TAP [TAPS=<taps>] [TIMEOUT=<timeout>]`：运行测试例程，报告 load cell 上的敲击。工具头不会移动，但 load cell 探针会像探测一样感知敲击。这可以用作健全性检查以确保探针正常工作。此工具替代了 load cell 探针的 QUERY_ENDSTOPS 和 QUERY_PROBE。
- `TAPS`：工具预期的敲击次数
- `TIMEOOUT`：工具在中止前等待每次敲击的时间（单位秒）。

### Load Cell 命令扩展
执行探测的命令（如 [`PROBE`](#probe)、[`PROBE_ACCURACY`](#probe_accuracy)、[`BED_MESH_CALIBRATE`](#bed_mesh_calibrate) 等）如果定义了 `[load_cell_probe]`，将接受额外参数。这些参数覆盖 [`[load_cell_probe]`](./Config_Reference.md#load_cell_probe) 配置中的相应设置：
- `FORCE_SAFETY_LIMIT=<grams>`
- `TRIGGER_FORCE=<grams>`
- `DRIFT_FILTER_CUTOFF_FREQUENCY=<frequency_hz>`
- `DRIFT_FILTER_DELAY=<1|2>`
- `BUZZ_FILTER_CUTOFF_FREQUENCY=<frequency_hz>`
- `BUZZ_FILTER_DELAY=<1|2>`
- `NOTCH_FILTER_FREQUENCIES=<list of frequency_hz>`
- `NOTCH_FILTER_QUALITY=<quality>`
- `TARE_TIME=<seconds>`
- `PULLBACK_DISTANCE=<mm>`
- `PULLBACK_SPEED=<mm/s>`
- `MIN_TAP_QUALITY=<percent>`
- `DECOMPRESSION_ANGLE=<angle>`

### [manual_probe]

manual_probe 模块会自动加载。

#### MANUAL_PROBE
`MANUAL_PROBE [SPEED=<speed>]`：运行一个辅助脚本，用于测量给定位置处喷嘴的高度。如果指定 SPEED，它将设置 TESTZ 命令的速度（默认为 5mm/s）。在手动探测期间，可以使用以下附加命令：
- `ACCEPT`：此命令接受当前位置并结束手动探测工具。
- `ABORT`：此命令终止手动探测工具。
- `TESTZ Z=<value>`：此命令将喷嘴向上或向下移动 "value" 指定的量。例如，`TESTZ Z=-.1` 将使喷嘴向下移动 .1mm，而 `TESTZ Z=.1` 将使喷嘴向上移动 .1mm。该值也可以是 `+`、`-`、`++` 或 `--`，以相对于之前的尝试将喷嘴向上或向下移动一定量。

#### Z_ENDSTOP_CALIBRATE
`Z_ENDSTOP_CALIBRATE [SPEED=<speed>]`：运行一个辅助脚本，用于校准 Z position_endstop 配置设置。有关参数的详细信息以及工具处于活动状态时可用的其他命令，请参阅 MANUAL_PROBE 命令。

#### Z_OFFSET_APPLY_ENDSTOP
`Z_OFFSET_APPLY_ENDSTOP`：获取当前 Z GCode 偏移（也称为 babystepping），并将其从 stepper_z 的 endstop_position 中减去。这相当于获取经常使用的 babystepping 值并"使其永久化"。需要 `SAVE_CONFIG` 才能生效。

### [manual_stepper]

当启用 [manual_stepper 配置部分](Config_Reference.md#manual_stepper) 时，可以使用以下命令。

#### MANUAL_STEPPER
`MANUAL_STEPPER STEPPER=config_name [ENABLE=[0|1]] [SET_POSITION=<pos>] [SPEED=<speed>] [ACCEL=<accel>] [MOVE=<pos>] [STOP_ON_ENDSTOP=[1|2|-1|-2]] [SYNC=0]]`：此命令将更改步进的状态。使用 ENABLE 参数启用/禁用步进。使用 SET_POSITION 参数强制步进认为它在给定位置。使用 MOVE 参数请求移动到给定位置。如果指定 SPEED 和/或 ACCEL，则使用给定的值而不是配置文件中指定的默认值。如果指定加速度为零，则不执行加速度。如果指定 STOP_ON_ENDSTOP=1，则当限位报告触发时移动将提前结束（使用 STOP_ON_ENDSTOP=2 以在限位不触发的情况下无错误完成移动，使用 -1 或 -2 在限位报告未触发时停止）。通常，未来的 G-Code 命令将安排在步进移动完成后运行，但如果手动步进移动使用 SYNC=0，则未来的 G-Code 移动命令可能与步进移动并行运行。

### [mcp4018]

当启用 [mcp4018 配置部分](Config_Reference.md#mcp4018) 时，可以使用以下命令。

#### SET_DIGIPOT

`SET_DIGIPOT DIGIPOT=config_name WIPER=<value>`：此命令将更改数字电位器的当前值。此值通常应在 0.0 到 1.0 之间，除非在配置中定义了 'scale'。定义 'scale' 时，此值应在 0.0 到 'scale' 之间。

### [led]

当启用任何 [led 配置部分](Config_Reference.md#leds) 时，可以使用以下命令。

#### SET_LED
`SET_LED LED=<config_name> RED=<value> GREEN=<value> BLUE=<value> WHITE=<value> [INDEX=<index>] [TRANSMIT=0] [SYNC=1]`：设置 LED 输出。每个颜色 `<value>` 必须在 0.0 到 1.0 之间。WHITE 选项仅对 RGBW LED 有效。如果 LED 支持菊花链中的多个芯片，则可以指定 INDEX 以仅更改给定芯片的颜色（第一个芯片为 1，第二个为 2，依此类推）。如果未提供 INDEX，则菊花链中的所有 LED 都将设置为提供的颜色。如果指定 TRANSMIT=0，则颜色更改仅在下一个不指定 TRANSMIT=0 的 SET_LED 命令时生效；这可以与 INDEX 参数结合使用，以便在菊花链中批量进行多个更新。默认情况下，SET_LED 命令将与其正在进行的 GCode 命令同步更改。如果在打印机未打印时设置 LED，这可能导致不良行为，因为它会重置空闲超时。如果不需要精确计时，可以指定可选的 SYNC=0 参数以应用更改而不重置空闲超时。

#### SET_LED_TEMPLATE
`SET_LED_TEMPLATE LED=<led_name> TEMPLATE=<template_name> [<param_x>=<literal>] [INDEX=<index>]`：将 [display_template](Config_Reference.md#display_template) 分配给给定的 [LED](Config_Reference.md#leds)。例如，如果定义了 `[display_template my_led_template]` 配置部分，则可以在此处分配 `TEMPLATE=my_led_template`。display_template 应产生一个逗号分隔的字符串，包含对应于红色、绿色、蓝色和白色颜色设置的四个浮点数。模板将被持续评估，LED 将自动设置为结果颜色。可以在模板评估期间设置 display_template 参数（参数将被解析为 Python 字面量）。如果未指定 INDEX，则 LED 菊花链中的所有芯片都将设置为模板，否则仅将具有给定索引的芯片更新。如果 TEMPLATE 是空字符串，则此命令将清除分配给 LED 的任何先前模板（然后可以使用 `SET_LED` 命令管理 LED 的颜色设置）。

### [output_pin]

当启用 [output_pin 配置部分](Config_Reference.md#output_pin) 或 [pwm_tool 配置部分](Config_Reference.md#pwm_tool) 时，可以使用以下命令。

#### SET_PIN
`SET_PIN PIN=config_name VALUE=<value>`：将引脚设置为给定的输出 `VALUE`。对于 "digital" 输出引脚，VALUE 应为 0 或 1。对于 PWM 引脚，设置为 0.0 到 1.0 之间的值，或如果在 output_pin 配置部分中配置了 scale，则为 0.0 到 `scale` 之间的值。

`SET_PIN PIN=config_name TEMPLATE=<template_name> [<param_x>=<literal>]`：如果指定 `TEMPLATE`，则将 [display_template](Config_Reference.md#display_template) 分配给给定的引脚。例如，如果定义了 `[display_template my_pin_template]` 配置部分，则可以在此处分配 `TEMPLATE=my_pin_template`。display_template 应产生包含所需值的浮点数的字符串。模板将被持续评估，引脚将自动设置为结果值。可以在模板评估期间设置 display_template 参数（参数将被解析为 Python 字面量）。如果 TEMPLATE 是空字符串，则此命令将清除分配给引脚的任何先前模板（然后可以使用 `SET_PIN` 命令直接管理值）。

### [palette2]

当启用 [palette2 配置部分](Config_Reference.md#palette2) 时，可以使用以下命令。

Palette 打印通过在 GCode 文件中嵌入特殊 OCode（Omega Code）来工作：
- `O1`...`O32`：这些代码从 GCode 流中读取，由该模块处理并传递到 Palette 2 设备。

还提供以下附加命令。

#### PALETTE_CONNECT
`PALETTE_CONNECT`：此命令初始化与 Palette 2 的连接。

#### PALETTE_DISCONNECT
`PALETTE_DISCONNECT`：此命令断开与 Palette 2 的连接。

#### PALETTE_CLEAR
`PALETTE_CLEAR`：此命令指示 Palette 2 清除所有输入和输出路径中的耗材。

#### PALETTE_CUT
`PALETTE_CUT`：此命令指示 Palette 2 切割当前加载在拼接核心中的耗材。

#### PALETTE_SMART_LOAD
`PALETTE_SMART_LOAD`：此命令在 Palette 2 上启动智能加载序列。耗材通过挤出设备上校准的距离自动加载，并在加载完成后指示 Palette 2。此命令等同于在耗材加载完成后直接在 Palette 2 屏幕上按 **Smart Load**。

### [pid_calibrate]

如果在配置文件中定义了加热器，pid_calibrate 模块会自动加载。

#### PID_CALIBRATE
`PID_CALIBRATE HEATER=<config_name> TARGET=<temperature> [WRITE_FILE=1] [TOLERANCE=0.02]`：执行 PID 校准测试。指定的加热器将被启用直到达到指定的目标温度，然后加热器将在多个周期内打开和关闭。如果启用 WRITE_FILE 参数，则将创建文件 /tmp/heattest.csv，其中包含测试期间所有温度样本的日志。如果未传入，TOLERANCE 默认为 0.02。容差越紧，校准结果越好，但可以达到的紧度取决于传感器读数的干净程度。低噪声读数可能允许使用 0.01，而噪声较大的读数可能需要 0.03 或更高的值。

#### SET_HEATER_PID
`SET_HEATER_PID HEATER=<heater_name> KP=<kp> KI=<ki> KD=<kd>`：允许在不重新加载固件的情况下手动更改加热器的 PID 参数。HEATER 接受短名称（因此对于 `heater_generic chamber`，您只需写 `chamber`）

### [pid_profile]

如果在配置文件中定义了加热器，PID_PROFILE 模块会自动加载。

HEATER 通常接受短名称（因此对于 `heater_generic chamber`，您只需写 `chamber`）

#### PID_PROFILE
`PID_PROFILE LOAD=<profile_name> HEATER=<heater_name> [DEFAULT=<profile_name>] [VERBOSE=<verbosity>] [KEEP_TARGET=0|1] [LOAD_CLEAN=0|1]`：为指定的加热器加载给定的 PID_PROFILE。如果指定 DEFAULT，当 LOAD 的给定配置文件找不到时，将加载 DEFAULT 中指定的配置文件（类似于 getOrDefault 方法）。如果 VERBOSE 设置为 LOW，将在控制台中写入最少的信息。如果设置为 NONE，将不给出控制台输出。如果 KEEP_TARGET 设置为 1，加热器将保持其目标温度；如果设置为 0，目标温度将设置为 0。默认情况下，加热器的目标温度将设置为 0，以便算法有时间稳定。如果 LOAD_CLEAN 设置为 1，配置文件将如同打印机刚启动一样加载；如果设置为 0，配置文件将保留之前的加热信息。默认情况下信息将被保留以减少超调，如果在切换配置文件时遇到奇怪的行为，请更改此值。

`PID_PROFILE SAVE=<profile_name> HEATER=<heater_name>`：将指定加热器的当前加载配置文件保存到配置中给定的名称下。

`PID_PROFILE REMOVE=<profile_name> HEATER=<heater_name>`：从当前会话的配置文件列表中删除给定的配置文件，并在之后发出 SAVE_CONFIG 时从配置中删除。

`PID_PROFILE SET_VALUES=<profile_name> HEATER=<heater_name> TARGET=<target_temp> TOLERANCE=<tolerance> CONTROL=<control_type> KP=<kp> KI=<ki> KD=<kd> [RESET_TARGET=0|1] [LOAD_CLEAN=0|1]`：使用给定的 PID 值创建新配置文件，CONTROL 必须是 `pid` 或 `pid_v`，必须指定 TOLERANCE 和 TARGET 以创建有效的配置文件，但值本身并不重要。如果 KEEP_TARGET 设置为 1，加热器将保持其目标温度；如果设置为 0，目标温度将设置为 0。默认情况下，加热器的目标温度将设置为 0，以便算法有时间稳定。如果 LOAD_CLEAN 设置为 1，配置文件将如同打印机刚启动一样加载；如果设置为 0，配置文件将保留之前的加热信息。默认情况下信息将被保留以减少超调，如果在切换配置文件时遇到奇怪的行为，请更改此值。

`PID_PROFILE GET_VALUES HEATER=<heater_name>`：将给定加热器的当前加载 pid_profile 的值输出到控制台。

### [pause_resume]

当启用 [pause_resume 配置部分](Config_Reference.md#pause_resume) 时，可以使用以下命令：

#### PAUSE
`PAUSE`：暂停当前打印。当前位置被捕获以便在恢复时使用。

#### RESUME
`RESUME [VELOCITY=<value>]`：从暂停中恢复打印，首先恢复之前捕获的位置。VELOCITY 参数确定工具应返回到原始捕获位置的速度。

#### CLEAR_PAUSE
`CLEAR_PAUSE`：清除当前暂停状态而不恢复打印。如果您决定在 PAUSE 后取消打印，这很有用。建议将其添加到开始 GCode 中，以确保每次打印的暂停状态都是新的。

#### CANCEL_PRINT
`CANCEL_PRINT`：取消当前打印。

### [print_stats]

print_stats 模块会自动加载。

#### SET_PRINT_STATS_INFO
`SET_PRINT_STATS_INFO [TOTAL_LAYER=<total_layer_count>] [CURRENT_LAYER=<current_layer>]`：将切片器信息（如当前层和总层数）传递给 Kalico。将 `SET_PRINT_STATS_INFO [TOTAL_LAYER=<total_layer_count>]` 添加到切片器开始 GCode 部分，将 `SET_PRINT_STATS_INFO [CURRENT_LAYER=<current_layer>]` 添加到层更改 GCode 部分，以将切片器的层信息传递给 Kalico。

### [probe]

当启用 [probe 配置部分](Config_Reference.md#probe) 或 [bltouch 配置部分](Config_Reference.md#bltouch) 时（另请参阅 [探针校准指南](Probe_Calibrate.md)），可以使用以下命令。

#### PROBE
`PROBE [PROBE_SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [SAMPLES=<count>] [SAMPLE_RETRACT_DIST=<mm>] [SAMPLES_TOLERANCE=<mm>] [SAMPLES_TOLERANCE_RETRIES=<count>] [SAMPLES_RESULT=median|average] [BAD_PROBE_STRATEGY=<FAIL|IGNORE|RETRY|CIRCLE>] [BAD_PROBE_RETRIES=<count>] [RETRY_SPEED=<mm/s>] [HOME=<z>]`：⚠️ 将喷嘴向下移动直到探针触发。如果提供了任何可选参数，它们将覆盖 [probe 配置部分](Config_Reference.md#probe) 中的等效设置。
- `HOME`：设置值 `z` 以从探针结果归位 Z 轴
以下可选参数控制探针质量处理（对于支持质量检测的探针）：⚠️
- `BAD_PROBE_STRATEGY`：检测到不良探针时使用的策略。有关可用策略，请参阅探针配置部分。
- `BAD_PROBE_RETRIES`：不良探针的最大重试次数。
- `RETRY_SPEED`：在重试位置之间水平移动时使用的探测速度。
- `PATTERN_SPACING`：使用 CIRCLE 策略时圆形重试模式的间距（单位 mm）。

#### QUERY_PROBE
`QUERY_PROBE`：报告探针的当前状态（"triggered" 或 "open"）。

#### PROBE_ACCURACY
`PROBE_ACCURACY [PROBE_SPEED=<mm/s>] [SAMPLES=<count>] [SAMPLE_RETRACT_DIST=<mm>]`：计算多个探针样本的最大值、最小值、平均值、中位数和标准偏差。默认情况下，采集 10 个样本。否则，可选参数默认为探针配置部分中的等效设置。

#### PROBE_CALIBRATE
`PROBE_CALIBRATE [SPEED=<speed>] [<probe_parameter>=<value>]`：运行一个辅助脚本，用于校准探针的 z_offset。有关可选探测参数的详细信息，请参阅 PROBE 命令。有关 SPEED 参数和工具处于活动状态时可用的其他命令的详细信息，请参阅 MANUAL_PROBE 命令。请注意，PROBE_CALIBRATE 命令使用速度变量在 XY 方向以及 Z 方向移动。

#### Z_OFFSET_APPLY_PROBE
`Z_OFFSET_APPLY_PROBE`：获取当前 Z GCode 偏移（也称为 babystepping），并将其从探针的 z_offset 中减去。这相当于获取经常使用的 babystepping 值并"使其永久化"。需要 `SAVE_CONFIG` 才能生效。

### [nozzle_cleanup]
当启用 [nozzle_cleanup 配置部分](Config_Reference.md#nozzle_cleanup) 时，可以使用以下命令。

#### NOZZLE_CLEANUP
`NOZZLE_CLEANUP [SAMPLES=<count>] [PATTERN_STEP=<mm>] [PATTERN_X=<count>] [PATTERN_Y=<count>] [SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [RETRY_SPEED=<mm/s>] [SAMPLE_RETRACT_DIST=<mm>] [SCRUBBING_FREQUENCY=<count>]`：⚠️

执行喷嘴清洁例程，通过在网格模式上探测来去除喷嘴上的渗出物。这对于没有清洁硬件的基于喷嘴的探针特别有用。在热床网格之前运行此命令可以减少网格期间遇到的不良探测，并将渗出物排除在第一层之外。该命令探测一组位置网格，并在记录指定数量的连续良好探测后结束。喷嘴在每次探测时始终移动到新位置以促进清洁。喷嘴清洁可以与敲击混合以增强清洁效果。

要使用该命令，请将工具头定位到要开始清洁的位置。例如，靠近打印区域的边缘。`PATTERN_X` 和 `PATTERN_Y` 控制每个轴的网格点数。正值沿轴的正方向扩展网格，负值则相反。例如，如果将工具头定位在打印区域的左前方，并且希望将清洁杂物保持在打印区域之外，应使用 `PATTERN_Y=-4` 将模式向热床前方扩展，远离打印区域。

### [probe_eddy_current]

当启用 [probe_eddy_current 配置部分](Config_Reference.md#probe_eddy_current) 时，可以使用以下命令。

#### PROBE_EDDY_CURRENT_CALIBRATE
`PROBE_EDDY_CURRENT_CALIBRATE CHIP=<config_name>`：此工具校准传感器谐振频率到对应的 Z 高度。该工具需要几分钟才能完成。完成后，使用 SAVE_CONFIG 命令将结果存储到 printer.cfg 文件中。

#### LDC_CALIBRATE_DRIVE_CURRENT
`LDC_CALIBRATE_DRIVE_CURRENT CHIP=<config_name>` 此工具将校准 ldc1612 DRIVE_CURRENT0 寄存器。使用此工具之前，将传感器移动到靠近热床中心且距热床表面约 20mm 的位置。运行此命令以确定传感器的适当 DRIVE_CURRENT。运行此命令后，使用 SAVE_CONFIG 命令将新设置存储到 printer.cfg 配置文件中。

### [pwm_cycle_time]

当启用 [pwm_cycle_time 配置部分](Config_Reference.md#pwm_cycle_time) 时，可以使用以下命令。

#### SET_PIN
`SET_PIN PIN=config_name VALUE=<value> [CYCLE_TIME=<cycle_time>]`：此命令的工作方式类似于 [output_pin](#output_pin) SET_PIN 命令。此处的命令支持使用 CYCLE_TIME 参数设置显式周期时间（单位秒）。请注意，CYCLE_TIME 参数不会在 SET_PIN 命令之间存储（任何不带显式 CYCLE_TIME 参数的 SET_PIN 命令将使用 pwm_cycle_time 配置部分中指定的 `cycle_time`）。

### [quad_gantry_level]

当启用 [quad_gantry_level 配置部分](Config_Reference.md#quad_gantry_level) 时，可以使用以下命令。

#### QUAD_GANTRY_LEVEL
`QUAD_GANTRY_LEVEL [RETRIES=<value>] [RETRY_TOLERANCE=<value>] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`：此命令将探测配置中指定的点，然后对每个 Z 步进进行独立调整以补偿倾斜。有关可选探测参数的详细信息，请参阅 PROBE 命令。可选的 `RETRIES`、`RETRY_TOLERANCE`、`HORIZONTAL_MOVE_Z` 和 `ENFORCE_LIFT_SPEED` 值覆盖配置文件中指定的这些选项。

### [query_adc]

query_adc 模块会自动加载。

#### QUERY_ADC
`QUERY_ADC [NAME=<config_name>] [PULLUP=<value>]`：报告为配置的模拟引脚接收的最后一个模拟值。如果未提供 NAME，则报告可用的 adc 名称列表。如果提供 PULLUP（以欧姆为单位），则报告原始模拟值以及该上拉电阻下的等效电阻。

### [query_endstops]

query_endstops 模块会自动加载。当前可用以下标准 G-Code 命令，但不建议使用：
- 获取限位状态：`M119`（改用 QUERY_ENDSTOPS。）

#### QUERY_ENDSTOPS
`QUERY_ENDSTOPS`：探测轴限位并报告它们是 "triggered" 还是 "open" 状态。此命令通常用于验证限位是否正常工作。

### [resonance_tester]

当启用 [resonance_tester 配置部分](Config_Reference.md#resonance_tester) 时（另请参阅 [测量谐振指南](Measuring_Resonances.md)），可以使用以下命令。

#### MEASURE_AXES_NOISE
`MEASURE_AXES_NOISE`：测量并输出所有已启用加速度计芯片的所有轴的噪声。

#### TEST_RESONANCES
`TEST_RESONANCES AXIS=<axis> [OUTPUT=<resonances,raw_data>] [NAME=<name>] [FREQ_START=<min_freq>] [FREQ_END=<max_freq>] [HZ_PER_SEC=<hz_per_sec>] [CHIPS=<chip_name>] [POINT=x,y,z] [ACCEL_PER_HZ=<accel_per_hz>] [INPUT_SHAPING=<0:1>]`：对所有配置的探测点运行请求 "轴" 的谐振测试，并使用为相应轴配置的加速度计芯片测量加速度。"轴" 可以是 X 或 Y，或指定任意方向为 `AXIS=dx,dy`，其中 dx 和 dy 是定义方向向量的浮点数（例如 `AXIS=X`、`AXIS=Y` 或 `AXIS=1,-1` 定义对角线方向）。请注意，`AXIS=dx,dy` 和 `AXIS=-dx,-dy` 等效。`chip_name` 可以是一个或多个配置的加速芯片，用逗号分隔，例如 `CHIPS="adxl345, adxl345 rpi"`。如果指定 POINT 或 ACCEL_PER_HZ，它们将覆盖 `[resonance_tester]` 中配置的相应字段。如果 `INPUT_SHAPING=0` 或未设置（默认），则禁用谐振测试的输入整形，因为在启用输入整形器的情况下运行谐振测试是无效的。`OUTPUT` 参数是逗号分隔的输出列表。如果请求 `raw_data`，则原始加速度计数据写入文件或一系列文件 `/tmp/raw_data_<axis>_[<chip_name>_][<point>_]<name>.csv`（如果配置了多个探测点或指定了 POINT，则生成 `<point>_` 部分）。如果指定 `resonances`，则计算频率响应（跨所有探测点）并写入 `/tmp/resonances_<axis>_<name>.csv` 文件。如果未设置，OUTPUT 默认为 `resonances`，NAME 默认为 "YYYYMMDD_HHMMSS" 格式的当前时间。

#### SHAPER_CALIBRATE
`SHAPER_CALIBRATE [AXIS=<axis>] [NAME=<name>] [FREQ_START=<min_freq>] [FREQ_END=<max_freq>] [ACCEL_PER_HZ=<accel_per_hz>] [HZ_PER_SEC=<hz_per_sec>] [CHIPS=<chip_name>] [MAX_SMOOTHING=<max_smoothing>] [INPUT_SHAPING=<0:1>]`：与 `TEST_RESONANCES` 类似，按配置运行谐振测试，并尝试为请求的轴（或如果未设置 `AXIS` 参数，则为 X 和 Y 两个轴）找到输入整形器的最佳参数。如果未设置 `MAX_SMOOTHING`，其值取自 `[resonance_tester]` 部分，默认为未设置。有关此功能使用的更多信息，请参阅测量谐振指南的 [最大平滑度](Measuring_Resonances.md#max-smoothing)。调谐结果将打印到控制台，频率响应和不同的输入整形器值将写入 CSV 文件 `/tmp/calibration_data_<axis>_<name>.csv`。除非指定，否则 NAME 默认为 "YYYYMMDD_HHMMSS" 格式的当前时间。请注意，建议的输入整形器参数可以通过发出 `SAVE_CONFIG` 命令持久化到配置中，如果之前已启用 `[input_shaper]`，这些参数将立即生效。

### [respond]

当启用 [respond 配置部分](Config_Reference.md#respond) 时，可以使用以下标准 G-Code 命令：
- `M118 <message>`：回显带有配置的默认前缀的消息（如果未配置前缀，则为 `echo: `）。

还提供以下附加命令。

#### RESPOND
- `RESPOND MSG="<message>"`：回显带有配置的默认前缀的消息（如果未配置前缀，则为 `echo: `）。
- `RESPOND TYPE=echo MSG="<message>"`：回显带有 `echo: ` 前缀的消息。
- `RESPOND TYPE=echo_no_space MSG="<message>"`：回显带有 `echo:` 前缀的消息，前缀和消息之间没有空格，有助于与期望非常特定格式的一些 OctoPrint 插件兼容。
- `RESPOND TYPE=command MSG="<message>"`：回显带有 `// ` 前缀的消息。OctoPrint 可以配置为响应这些消息（例如 `RESPOND TYPE=command MSG=action:pause`）。
- `RESPOND TYPE=error MSG="<message>"`：回显带有 `!! ` 前缀的消息。
- `RESPOND PREFIX=<prefix> MSG="<message>"`：回显带有 `<prefix>` 前缀的消息。（`PREFIX` 参数将优先于 `TYPE` 参数）

### [save_variables]

如果启用了 [save_variables 配置部分](Config_Reference.md#save_variables)，则启用以下命令。

#### SAVE_VARIABLE
`SAVE_VARIABLE VARIABLE=<name> VALUE=<value>`：将变量保存到磁盘，以便可以在重启后使用。所有存储的变量在启动时加载到 `printer.save_variables.variables` 字典中，可在 GCode 宏中使用。提供的 VALUE 将被解析为 Python 字面量。

### [screws_tilt_adjust]

当启用 [screws_tilt_adjust 配置部分](Config_Reference.md#screws_tilt_adjust) 时（另请参阅 [手动调平指南](Manual_Level.md#adjusting-bed-leveling-screws-using-the-bed-probe)），可以使用以下命令。

#### SCREWS_TILT_CALCULATE
`SCREWS_TILT_CALCULATE [DIRECTION=CW|CCW] [MAX_DEVIATION=<value>] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>]`：此命令将调用热床螺丝调整工具。它将命令喷嘴移动到不同位置（如配置文件中定义的），探测 Z 高度并计算调整热床调平所需的旋钮转动次数。如果指定 DIRECTION，旋钮转动将全部为相同方向，顺时针（CW）或逆时针（CCW）。有关可选探测参数的详细信息，请参阅 PROBE 命令。重要提示：在使用此命令之前，您必须始终执行 G28。如果指定 MAX_DEVIATION，则当螺丝高度相对于基本螺丝高度的任何差值大于提供的值时，命令将引发 GCode 错误。可选的 `HORIZONTAL_MOVE_Z` 值覆盖配置文件中指定的 `horizontal_move_z` 选项。

### [sdcard_loop]

当启用 [sdcard_loop 配置部分](Config_Reference.md#sdcard_loop) 时，可以使用以下扩展命令。

#### SDCARD_LOOP_BEGIN
`SDCARD_LOOP_BEGIN COUNT=<count>`：在 SD 打印中开始一个循环部分。计数为 0 表示该部分应无限循环。

#### SDCARD_LOOP_END
`SDCARD_LOOP_END`：结束 SD 打印中的循环部分。

#### SDCARD_LOOP_DESIST
`SDCARD_LOOP_DESIST`：完成现有循环而不再进行迭代。

### [servo]

当启用 [servo 配置部分](Config_Reference.md#servo) 时，可以使用以下命令。

#### SET_SERVO
`SET_SERVO SERVO=config_name [ANGLE=<degrees> | WIDTH=<seconds>]`：将舵机位置设置为给定角度（单位度）或脉冲宽度（单位秒）。使用 `WIDTH=0` 禁用舵机输出。

### [skew_correction]

当启用 [skew_correction 配置部分](Config_Reference.md#skew_correction) 时（另请参阅 [倾斜校正](Skew_Correction.md) 指南），可以使用以下命令。

#### SET_SKEW
`SET_SKEW [XY=<ac_length,bd_length,ad_length>] [XZ=<ac,bd,ad>] [YZ=<ac,bd,ad>] [CLEAR=<0|1>]`：使用从校准打印件获取的测量值（单位 mm）配置 [skew_correction] 模块。可以为任何平面组合输入测量值，未输入的平面将保留其当前值。如果输入 `CLEAR=1`，则所有倾斜校正将被禁用。

#### GET_CURRENT_SKEW
`GET_CURRENT_SKEW`：以弧度和度为单位报告每个平面的当前打印机倾斜。倾斜基于通过 `SET_GCODE_OFFSET` GCode 提供的参数计算。

#### CALC_MEASURED_SKEW
`CALC_MEASURED_SKEW [AC=<ac_length>] [BD=<bd_length>] [AD=<ad_length>]`：基于测量的打印件计算并报告倾斜（单位弧度和度）。这对于在应用校正后确定打印机的当前倾斜很有用。在应用校正之前确定是否需要倾斜校正也可能很有用。有关倾斜校准对象和测量的详细信息，请参阅 [倾斜校正](Skew_Correction.md)。

#### SKEW_PROFILE
`SKEW_PROFILE [LOAD=<name>] [SAVE=<name>] [REMOVE=<name>]`：skew_correction 的配置文件管理。LOAD 将从与提供的名称匹配的配置文件恢复倾斜状态。SAVE 将当前倾斜状态保存到与提供的名称匹配的配置文件。REMOVE 将从持久存储中删除与提供的名称匹配的配置文件。请注意，在运行 SAVE 或 REMOVE 操作后，必须运行 SAVE_CONFIG GCode 才能使对持久存储的更改生效。

### ⚠️ [smart_effector]

当启用 [smart_effector 配置部分](Config_Reference.md#smart_effector) 时，可以使用多个命令。在更改 Smart Effector 参数之前，请务必查看 [Duet3D Wiki](https://duet3d.dozuki.com/Wiki/Smart_effector_and_carriage_adapters_for_delta_printer) 上 Smart Effector 的官方文档。另请参阅 [探针校准指南](Probe_Calibrate.md)。

#### SET_SMART_EFFECTOR
`SET_SMART_EFFECTOR [SENSITIVITY=<sensitivity>] [ACCEL=<accel>] [RECOVERY_TIME=<time>]`：设置 Smart Effector 参数。当指定 `SENSITIVITY` 时，相应的值将写入 SmartEffector EEPROM（需要提供 `control_pin`）。可接受的 `<sensitivity>` 值为 0..255，默认为 50。较低的值需要较小的喷嘴接触力即可触发（但由于探测过程中的振动，有更高的误触发风险），而较高的值减少误触发（但需要更大的接触力才能触发）。由于灵敏度写入 EEPROM，因此在关闭后保留，因此不需要在每次打印机启动时配置。`ACCEL` 和 `RECOVERY_TIME` 允许在运行时覆盖相应参数，有关这些参数的更多信息，请参阅 Smart Effector 的 [配置部分](Config_Reference.md#smart_effector)。

#### RESET_SMART_EFFECTOR
`RESET_SMART_EFFECTOR`：将 Smart Effector 灵敏度重置为出厂设置。需要在配置部分中提供 `control_pin`。

### [stepper_enable]

stepper_enable 模块会自动加载。

#### SET_STEPPER_ENABLE
`SET_STEPPER_ENABLE STEPPER=<config_name> ENABLE=[0|1]`：仅启用或禁用给定的步进。这是一个诊断和调试工具，必须谨慎使用。禁用轴电机会重置归位信息。手动移动已禁用的步进可能导致电机在安全限制之外运行。这可能导致轴组件、热端和打印表面损坏。

### [temperature_fan]

当启用 [temperature_fan 配置部分](Config_Reference.md#temperature_fan) 时，可以使用以下命令。

#### SET_TEMPERATURE_FAN_TARGET
`SET_TEMPERATURE_FAN_TARGET temperature_fan=<temperature_fan_name> [target=<target_temperature>] [min_speed=<min_speed>] [max_speed=<max_speed>]`：设置 temperature_fan 的目标温度。如果未提供目标，则设置为配置文件中指定的温度。如果未提供速度，则不应用更改。

### [tmcXXXX]

当启用任何 [tmcXXXX 配置部分](Config_Reference.md#tmc-stepper-driver-configuration) 时，可以使用以下命令。

#### DUMP_TMC
`DUMP_TMC STEPPER=<name> [REGISTER=<name>]`：此命令将读取所有 TMC 驱动器寄存器并报告其值。如果提供 REGISTER，则仅转储指定的寄存器。

#### INIT_TMC
`INIT_TMC STEPPER=<name>`：此命令将初始化 TMC 寄存器。如果芯片的电源关闭然后重新打开，需要重新启用驱动器。

#### SET_TMC_CURRENT
`SET_TMC_CURRENT STEPPER=<name> CURRENT=<amps> HOLDCURRENT=<amps>`：这将调整 TMC 驱动器的运行和保持电流。`HOLDCURRENT` 不适用于 tmc2660 驱动器。当用于具有 `globalscaler` 字段的驱动器（tmc5160 和 tmc2240）时，如果使用 StealthChop2，步进必须保持静止超过 130ms，以便驱动器执行 AT#1 校准。

#### SET_TMC_FIELD
`SET_TMC_FIELD STEPPER=<name> FIELD=<field> VALUE=<value> VELOCITY=<value>`：这将更改 TMC 驱动器指定寄存器字段的值。此命令仅用于低级诊断和调试，因为在运行时更改字段可能导致打印机的不良和潜在危险行为。永久性更改应使用打印机配置文件进行。不执行给定值的健全性检查。也可以指定 VELOCITY 而不是 VALUE。此速度将转换为基于 20 位 TSTEP 的值表示。仅对表示速度的字段使用 VELOCITY 参数。

### [toolhead]

toolhead 模块会自动加载。

#### SET_VELOCITY_LIMIT
`SET_VELOCITY_LIMIT [VELOCITY=<value>] [ACCEL=<value>] [MINIMUM_CRUISE_RATIO=<value>] [SQUARE_CORNER_VELOCITY=<value>] [X_VELOCITY=<value>] [X_ACCEL=<value>] [Y_VELOCITY=<value>] [Y_ACCEL=<value>] [Z_VELOCITY=<value>] [Z_ACCEL=<value>]`：此命令可以更改打印机配置文件中指定的速度限制。有关每个参数的描述，请参阅 [打印机配置部分](Config_Reference.md#printer)。X_VELOCITY、X_ACCEL、Y_VELOCITY、Y_ACCEL、Z_VELOCITY 和 Z_ACCEL 仅在运动学支持时可用。

### RESET_VELOCITY_LIMIT
`RESET_VELOCITY_LIMIT`：此命令将速度限制重置为打印机配置文件中指定的值。有关每个参数的描述，请参阅 [打印机配置部分](Config_Reference.md#printer)。

#### ⚠️ SET_KINEMATICS_LIMIT

`SET_KINEMATICS_LIMIT [<X,Y,Z>_ACCEL=<value>] [<X,Y,Z>_VELOCITY=<value>] [SCALE=<0:1>]`：更改每轴限制。

此命令仅在 `kinematics` 设置为 [`limited_cartesian`](./Config_Reference.md#cartesian-kinematics-with-limits-for-x-and-y-axes) 或 [`limited_corexy`](./Config_Reference.md#corexy-kinematics-with-limits-for-x-and-y-axes) 时可用。CoreXY 上不可用速度参数。没有参数时，此命令响应具有最大加速度或速度的移动方向。

### ⚠️ [tools_calibrate]

当启用 [tools_calibrate 配置部分](Config_Reference.md#tools_calibrate) 时，可以使用以下命令。

#### TOOL_CALIBRATE_QUERY_PROBE
`TOOL_CALIBRATE_QUERY_PROBE`：查询当前校准探针状态。

#### TOOL_LOCATE_SENSOR
`TOOL_LOCATE_SENSOR`：相对于初始工具定位传感器。初始工具是 0 偏移，其他工具基于此进行校准。

在运行 `TOOL_LOCATE_SENSOR` 之前，将您的主工具头定位在校准探针的中心上方。

#### TOOL_CALIBRATE_TOOL_OFFSET
`TOOL_CALIBRATE_TOOL_OFFSET`：使用初始工具定位传感器后，将每个附加工具定位在传感器上方并运行 `TOOL_CALIBRATE_TOOL_OFFSET` 以找到它们的偏移。

#### TOOL_CALIBRATE_SAVE_TOOL_OFFSET
`TOOL_CALIBRATE_SAVE_TOOL_OFFSET MACRO=<macro_name> VARIABLE=<variable_name> [VALUE="({x:0.6f}, {y:0.6f}, {z:0.6f})"]`：将上次校准结果保存到宏变量。

`TOOL_CALIBRATE_SAVE_TOOL_OFFSET SECTION= ATTRIBUTE= [VALUE="{x:0.6f}, {y:0.6f}, {z:0.6f}"]`：将上次校准结果保存到配置中的字段。以这种方式保存的校准数据在 `RESTART` 打印机之前不会生效。

### [trad_rack]

当启用 [trad_rack 配置部分](Config_Reference.md#trad_rack) 时，可以使用以下命令。

#### TR_HOME
`TR_HOME`：归位选择器。

#### TR_GO_TO_LANE
`TR_GO_TO_LANE LANE=<lane index>`：将选择器移动到指定通道。

#### TR_LOAD_LANE
`TR_LOAD_LANE LANE=<lane index> [RESET_SPEED=<0|1>]`：确保耗材已加载到指定通道的模块中，方法是提示用户插入耗材、将耗材从模块加载到选择器中，并将耗材缩回到模块中。如果 RESET_SPEED 为 1，指定 LANE 使用的鲍登移动速度将重置为 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中的 spool_pull_speed（有关鲍登速度设置如何使用的详细信息，请参阅 [鲍登速度](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md#bowden-speeds)）。如果未指定，RESET_SPEED 默认为 1。

#### TR_LOAD_TOOLHEAD
`TR_LOAD_TOOLHEAD LANE=<lane index>|TOOL=<tool index> [MIN_TEMP=<temperature>] [EXACT_TEMP=<temperature>] [BOWDEN_LENGTH=<mm>] [EXTRUDER_LOAD_LENGTH=<mm>] [HOTEND_LOAD_LENGTH=<mm>]`：从指定通道或工具将耗材加载到工具头*。必须指定 LANE 或 TOOL。如果两者都指定，则 LANE 优先。如果之前已加载工具头，因此存在"活动通道"，则在加载新耗材之前将卸载它。如果指定 `MIN_TEMP` 且高于挤出机的当前温度，则在卸载/加载之前将挤出机加热到至少 `MIN_TEMP`；如果高于 `MIN_TEMP`，可能会使用当前挤出机温度目标，如果不是，则可能使用 [tr_last_heater_target](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md)。如果指定 `EXACT_TEMP`，则在卸载/加载之前将挤出机加热到 `EXACT_TEMP`，而不管任何其他温度设置。如果指定任何可选长度参数，它们将覆盖 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中的相应设置。

\* 有关通道和工具之间的差异以及它们如何相互关联的详细信息，请参阅 [工具映射文档](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tool_Mapping.md)。

#### T0, T1, T2 等。
`T<tool index>`：等效于调用 `TR_LOAD_TOOLHEAD TOOL=<tool index>`。TR_LOAD_TOOLHEAD 命令接受的所有可选参数也可以与这些命令一起使用。

#### TR_UNLOAD_TOOLHEAD
`TR_UNLOAD_TOOLHEAD [MIN_TEMP=<temperature>] [EXACT_TEMP=<temperature>]`：将耗材从工具头卸载回其模块。如果指定 `MIN_TEMP` 且高于挤出机的当前温度，则在卸载之前将挤出机加热到至少 `MIN_TEMP`；如果高于 `MIN_TEMP`，可能会使用当前挤出机温度目标，如果不是，则可能使用 [tr_last_heater_target](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md)。如果指定 `EXACT_TEMP`，则在卸载/加载之前将挤出机加热到 `EXACT_TEMP`，而不管任何其他温度设置。

#### TR_SERVO_DOWN
`TR_SERVO_DOWN [FORCE=<0|1>]`：移动舵机使驱动齿轮下降。除非 FORCE 为 1，否则在使用此命令之前必须将选择器移动到有效通道。如果未指定，FORCE 默认为 0。FORCE 参数在正常使用中不安全，仅应在舵机未连接到 Trad Rack 滑车时使用。

#### TR_SERVO_UP
`TR_SERVO_UP`：移动舵机使驱动齿轮上升。

#### TR_SET_ACTIVE_LANE
`TR_SET_ACTIVE_LANE LANE=<lane index>`：告诉 Trad Rack 假设工具头已从指定通道加载了耗材。选择器的位置也将从此通道推断，如果选择器电机尚未启用，则将启用它。

#### TR_RESET_ACTIVE_LANE
`TR_RESET_ACTIVE_LANE`：告诉 Trad Rack 假设工具头未被加载。

#### TR_RESUME
`TR_RESUME`：完成 Trad Rack 恢复所需的必要操作（和/或检查 Trad Rack 是否准备好继续），然后在所有这些操作成功完成后恢复打印。例如，如果打印因工具切换失败而暂停，则此命令将重试工具切换，如果工具切换成功完成则恢复打印。如果 Trad Rack 已暂停打印并在尝试恢复和继续之前需要用户交互或确认，您将被提示使用此命令。

#### TR_LOCATE_SELECTOR
`TR_LOCATE_SELECTOR`：确保 Trad Rack 选择器的位置已知，以便它准备好进行打印。如果用户需要采取操作，他们将被提示这样做，打印将暂停（例如，如果选择器传感器已触发但未设置活动通道）。[trad_rack 配置部分](Config_Reference.md#trad_rack) 中的 user_wait_time 配置选项确定 Trad Rack 在自动卸载工具头并恢复之前等待用户操作的时间。此外，save_active_lane 配置选项确定此命令是否可以从上次重启前保存的值推断"活动通道"，如果选择器耗材传感器已触发但当前未设置活动通道。建议在打印开始 GCode 中调用此命令。

#### TR_NEXT
`TR_NEXT`：如果 Trad Rack 在继续操作之前需要用户确认，您将被提示使用此命令。

#### TR_SYNC_TO_EXTRUDER
`TR_SYNC_TO_EXTRUDER`：在打印期间以及工具头加载或卸载期间通常仅涉及挤出机的任何挤出移动期间，将 Trad Rack 的耗材驱动器与挤出机同步。有关更多详细信息，请参阅 [挤出机同步文档](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Extruder_Syncing.md)。如果您希望耗材驱动器在每次启动时都与挤出机同步，而无需调用此命令，可以在 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中将 sync_to_extruder 设置为 True。

#### TR_UNSYNC_FROM_EXTRUDER
`TR_UNSYNC_FROM_EXTRUDER`：在打印期间以及工具头加载或卸载期间通常仅涉及挤出机的任何挤出移动期间，将 Trad Rack 的耗材驱动器与挤出机去同步。这是默认行为，除非您在 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中将 sync_to_extruder 设置为 True。

#### TR_SERVO_TEST
`TR_SERVO_TEST [ANGLE=<degrees>]`：将舵机移动到相对于下降位置的指定角度。如果未指定 ANGLE，舵机将移动到 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中 servo_up_angle 定义的上升位置。此命令用于测试不同的舵机角度以找到 servo_up_angle 的正确值。

#### TR_CALIBRATE_SELECTOR
`TR_CALIBRATE_SELECTOR`：启动校准 lane_spacing 以及选择器电机的 min、endstop 和 max 位置的过程。您将通过控制台中的消息被引导完成选择器校准过程。

#### TR_SET_HOTEND_LOAD_LENGTH
`TR_SET_HOTEND_LOAD_LENGTH VALUE=<value>|ADJUST=<adjust>`：设置 hotend_load_length 的值，覆盖其来自 [trad_rack 配置部分](Config_Reference.md#trad_rack) 的值。不会在重启后保留。如果使用 VALUE 参数，hotend_load_length 将设置为传入的值。如果使用 ADJUST 参数，调整将添加到 hotend_load_length 的当前值。

#### TR_DISCARD_BOWDEN_LENGTHS
`TR_DISCARD_BOWDEN_LENGTHS [MODE=[ALL|LOAD|UNLOAD]]`：丢弃 "bowden_load_length" 和/或 "bowden_unload_length" 的保存值（有关这些设置如何使用的详细信息，请参阅 [鲍登长度](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md#bowden-lengths)）。这些设置将各自重置为 [trad_rack 配置部分](Config_Reference.md#trad_rack) 中的 `bowden_length` 值，并将为 [tr_calib_bowden_load_length 和 tr_calib_bowden_unload_length](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Save_Variables.md) 保存空字典。如果指定 MODE=LOAD，"bowden_load_length" 和 tr_calib_bowden_load_length 将受影响；如果指定 MODE=UNLOAD，"bowden_unload_length" 和 tr_calib_bowden_unload_length 将受影响；如果指定 MODE=ALL，所有 4 个都将受影响。如果未指定，MODE 默认为 ALL。

#### TR_ASSIGN_LANE
`TR_ASSIGN_LANE LANE=<lane index> TOOL=<tool index> [SET_DEFAULT=<0|1>]`：将指定 LANE 分配给指定 TOOL。如果 SET_DEFAULT 为 1，LANE 将成为该工具的默认通道。如果未指定，SET_DEFAULT 默认为 0。

#### TR_SET_DEFAULT_LANE
`TR_SET_DEFAULT_LANE LANE=<lane index> [TOOL=<tool index>]`：如果指定 TOOL，LANE 将设置为该工具的默认通道。如果未指定 TOOL，LANE 将设置为其当前分配工具的默认通道。

#### TR_RESET_TOOL_MAP
`TR_RESET_TOOL_MAP`：重置通道/工具映射。每个工具将映射到一个通道组，该组由与工具索引相同的单个通道组成。

#### TR_PRINT_TOOL_MAP
`TR_PRINT_TOOL_MAP`：将通道/工具映射表打印到控制台，行对应于工具，列对应于通道。

#### TR_PRINT_TOOL_GROUPS
`TR_PRINT_TOOL_GROUPS`：将分配给每个工具的通道列表打印到控制台。如果一个工具有多个分配的通道，将指示默认通道。

### [tuning_tower]

tuning_tower 模块会自动加载。

#### TUNING_TOWER
`TUNING_TOWER COMMAND=<command> PARAMETER=<name> START=<value> [SKIP=<value>] [FACTOR=<value> [BAND=<value>]] | [STEP_DELTA=<value> STEP_HEIGHT=<value>]`：一个在打印期间调整每个 Z 高度参数的工具。该工具将以分配的值运行给定的 `COMMAND`，该值根据公式随 `Z` 变化。如果您将使用尺子或卡尺测量最佳值的 Z 高度，请使用 `FACTOR`；如果调谐塔模型具有与温度塔常见的离散值带，请使用 `STEP_DELTA` 和 `STEP_HEIGHT`。如果指定 `SKIP=<value>`，调谐过程直到达到 Z 高度 `<value>` 才开始，在此之下，值将设置为 `START`；在这种情况下，下面公式中使用的 `z_height` 实际上是 `max(z - skip, 0)`。有三种可能的选项组合：
- `FACTOR`：值以每毫米 `factor` 的速率变化。使用的公式是：`value = start + factor * z_height`。您可以将最佳 Z 高度直接代入公式以确定最佳参数值。
- `FACTOR` 和 `BAND`：值以每毫米 `factor` 的平均速率变化，但在离散带中，调整仅在每 `BAND` 毫米 Z 高度时进行。使用的公式是：`value = start + factor * ((floor(z_height / band) + .5) * band)`。
- `STEP_DELTA` 和 `STEP_HEIGHT`：值每 `STEP_HEIGHT` 毫米变化 `STEP_DELTA`。使用的公式是：`value = start + step_delta * floor(z_height / step_height)`。您可以简单地数带或读取调谐塔标签以确定最佳值。

### [virtual_sdcard]

如果启用 [virtual_sdcard 配置部分](Config_Reference.md#virtual_sdcard)，Kalico 支持以下标准 G-Code 命令：
- 列出 SD 卡：`M20`
- 初始化 SD 卡：`M21`
- 选择 SD 文件：`M23 <filename>`
- 开始/恢复 SD 打印：`M24`
- 暂停 SD 打印：`M25`
- 设置 SD 位置：`M26 S<offset>`
- 报告 SD 打印状态：`M27`

此外，当启用 "virtual_sdcard" 配置部分时，可以使用以下扩展命令。

#### SDCARD_PRINT_FILE
`SDCARD_PRINT_FILE FILENAME=<filename>`：加载文件并开始 SD 打印。

#### SDCARD_RESET_FILE
`SDCARD_RESET_FILE`：卸载文件并清除 SD 状态。

### [z_thermal_adjust]

当启用 [z_thermal_adjust 配置部分](Config_Reference.md#z_thermal_adjust) 时，可以使用以下命令。

#### SET_Z_THERMAL_ADJUST
`SET_Z_THERMAL_ADJUST [COMPONENT=name] [ENABLE=<0:1>] [TEMP_COEFF=<value>] [REF_TEMP=<value>]`：
- `COMPONENT`：如果定义了多个热调整，使用 `COMPONENT` 指定要调整哪一个。
- `ENABLE`：启用或禁用 Z 热调整。禁用不会移除已应用的任何调整，但会冻结当前调整值——这防止潜在不安全的向下 Z 移动。重新启用可能会导致向上工具移动，因为调整被更新和应用。
- `TEMP_COEFF`：允许在运行时调整调整温度系数（即 `TEMP_COEFF` 配置参数）。`TEMP_COEFF` 值不会保存到配置中。
- `REF_TEMP` 手动覆盖通常在归位期间设置的参考温度（用于非标准归位例程等）——归位时将自动重置。

### ⚠️ [z_calibration]

当启用 [z_calibration 配置部分](Config_Reference.md#z_calibration) 时（另请参阅 [Z 校准指南](Z_Calibration.md)），可以使用以下命令：
- `CALIBRATE_Z`：校准喷嘴和打印表面之间的当前偏移。
- `PROBE_Z_ACCURACY [PROBE_SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [SAMPLES=<count>] [SAMPLE_RETRACT_DIST=<mm>]`：计算多个探针样本的最大值、最小值、平均值、中位数和标准偏差。默认情况下，采集 10 个样本。否则，可选参数默认为 z_calibration 或 probe 配置部分中的等效设置。
*注意* 需要适当的宏和/或配置来连接和分离磁性探针才能使用这些命令！

### [z_tilt]

当启用 [z_tilt 配置部分](Config_Reference.md#z_tilt) 时，可以使用以下命令。

#### Z_TILT_ADJUST
`Z_TILT_ADJUST [HORIZONTAL_MOVE_Z=<value>] [ENFORCE_LIFT_SPEED=0|1] [<probe_parameter>=<value>]`：此命令将探测配置中指定的点，然后对每个 Z 步进进行独立调整以补偿倾斜。有关可选探测参数的详细信息，请参阅 PROBE 命令。可选的 `HORIZONTAL_MOVE_Z` 和 `ENFORCE_LIFT_SPEED` 值覆盖配置文件中指定的这些选项。

### [z_tilt_ng]

当启用 [z_tilt_ng 配置部分](Config_Reference.md#z_tilt_ng) 时，可以使用以下命令。

#### Z_TILT_ADJUST
`Z_TILT_ADJUST [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>] [INCREASING_THRESHOLD=<value>]`：此命令将探测配置中指定的点，然后对每个 Z 步进进行独立调整以补偿倾斜。有关可选探测参数的详细信息，请参阅 PROBE 命令。可选的 `HORIZONTAL_MOVE_Z` 值覆盖配置文件中指定的 `horizontal_move_z` 选项。INCREASING_THRESHOLD 设置 z_tilt 的 increasing_threshold 参数。当在 z_tilt_ng 部分中配置了 "extra_points" 参数时，可以使用以下命令：
- `Z_TILT_CALIBRATE [AVGLEN=<value>]`：此命令执行多次探测运行，类似于 Z_TILT_ADJUST，但包含 "extra_points" 中给出的额外点。如果热床不是完全平坦的，这将导致更平衡的热床调整。该命令对多次运行的误差取平均值，直到误差不再减少。它计算 z_offsets 配置参数的值，这将反过来被 T_TILT_ADJUST 使用以在没有额外点的情况下实现相同的精度。
- `Z_TILT_AUTODETECT [AVGLEN=<value>] [DELTA=<value>]`：此命令确定每个步进电机的枢轴点位置。其工作原理类似于 Z_TILT_CALIBRATE，但它使用步进的有意小不对齐来探测热床。不对齐的量可以用 DELTA 参数配置。它迭代直到计算的位置无法进一步改进。这可能是一个漫长的过程。