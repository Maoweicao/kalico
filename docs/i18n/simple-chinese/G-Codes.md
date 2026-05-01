# G代码

本文档描述Kalico支持的命令。这些是可以在OctoPrint终端选项卡中输入的命令。

带有⚠️标记的部分和命令表示与Klipper不同或新增的命令。

## G代码命令

Kalico支持以下标准G代码命令：
- 移动(G0或G1)：`G1 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>] [F<speed>]`
- 停留：`G4 P<milliseconds>`
- 移到原点：`G28 [X] [Y] [Z]`
- 关闭电机：`M18`或`M84`
- 等待当前移动完成：`M400`
- 对挤出使用绝对/相对距离：`M82`、`M83`
- 使用绝对/相对坐标：`G90`、`G91`
- 设置位置：`G92 [X<pos>] [Y<pos>] [Z<pos>] [E<pos>]`
- 设置速度因子覆盖百分比：`M220 S<percent>`
- 设置挤出因子覆盖百分比：`M221 S<percent>`
- 设置加速度：`M204 S<value>`或`M204 P<value> T<value>`
  - 注意：如果未指定S，但指定了P和T，则加速度设置为P和T的最小值。如果仅指定P或T之一，则命令无效。
- 获取挤出机温度：`M105`
- 设置挤出机温度：`M104 [T<index>] [S<temperature>]`
- 设置挤出机温度并等待：`M109 [T<index>] S<temperature>`
  - 注意：M109始终等待温度稳定到请求的值
- 启用冷挤出：`M302 [T<index>] [P<enable>] [S<min_extrude_temp>]`
- 设置床温度：`M140 [S<temperature>]`
- 设置床温度并等待：`M190 S<temperature>`
  - 注意：M190始终等待温度稳定到请求的值
- 设置风扇速度：`M106 S<value>`
- 关闭风扇：`M107`
- 紧急停止：`M112`
- 获取当前位置：`M114`
- 获取固件版本：`M115`

有关上述命令的更多详细信息，请参见[RepRap G代码文档](http://reprap.org/wiki/G-code)。

Kalico的目标是支持常见第三方软件（例如OctoPrint、Printrun、Slic3r、Cura等）在其标准配置中生成的G代码命令。不是目标支持所有可能的G代码命令。相反，Kalico更倾向于使用人类可读的["扩展G代码命令"](#其他命令)。同样，G代码终端输出仅供人类阅读——如果从外部软件控制Kalico，请参见[API服务器文档](API_Server.md)。

如果需要较不常见的G代码命令，则可能可以使用自定义[gcode_macro配置部分](Config_Reference.md#gcode_macro)来实现。例如，可以使用它来实现：`G12`、`G29`、`G30`、`G31`、`M42`、`M80`、`M81`、`T1`等。

## 其他命令

Kalico使用"扩展"G代码命令进行一般配置和状态。这些扩展命令都遵循类似的格式——它们以命令名称开头，可能后跟一个或多个参数。例如：`SET_SERVO SERVO=myservo ANGLE=5.3`。在本文档中，命令和参数以大写显示，但它们不区分大小写。(因此，"SET_SERVO"和"set_servo"都运行相同的命令。)

此部分按Kalico模块名称组织，通常遵循[打印机配置文件](Config_Reference.md)中指定的部分名称。请注意，某些模块是自动加载的。

### [adxl345]

启用[adxl345配置部分](Config_Reference.md#adxl345)时，以下命令可用。

#### ACCELEROMETER_MEASURE
`ACCELEROMETER_MEASURE [CHIP=<config_name>] [NAME=<value>]`：以请求的每秒样本数启动加速度计测量。如果未指定CHIP，则默认为"adxl345"。该命令以开始-停止模式工作：首次执行时，它启动测量；下一次执行停止测量。测量结果写入名为`/tmp/adxl345-<chip>-<name>.csv`的文件，其中`<chip>`是加速度计芯片的名称(来自`[adxl345 my_chip_name]`的`my_chip_name`)，`<name>`是可选的NAME参数。如果未指定NAME，则默认为"YYYYMMDD_HHMMSS"格式的当前时间。如果加速度计在其配置部分中没有名称(只是`[adxl345]`)，则不生成名称的`<chip>`部分。

#### ACCELEROMETER_QUERY
`ACCELEROMETER_QUERY [CHIP=<config_name>] [RATE=<value>] [SAMPLES=<value>] [RETURN=<value>]`：查询加速度计的当前值。如果未指定CHIP，则默认为"adxl345"。如果未指定RATE，则使用默认值。此命令对于测试与ADXL345加速度计的连接很有用：返回的值之一应该是自由落体加速度(±芯片的一些噪声)。`SAMPLES`参数可以设置为从传感器采样多个读数。读数将被平均在一起。默认值是收集单个样本。`RETURN`参数可以取`vector`(默认值)或`tilt`的值。在`vector`模式下，返回原始自由落体加速度矢量。在`tilt`模式下，计算并显示垂直于自由落体矢量的平面的X和Y角度。

#### ACCELEROMETER_DEBUG_READ
`ACCELEROMETER_DEBUG_READ [CHIP=<config_name>] REG=<register>`：查询ADXL345寄存器"register"(例如44或0x2C)。对调试可能有用。

#### ACCELEROMETER_DEBUG_WRITE
`ACCELEROMETER_DEBUG_WRITE [CHIP=<config_name>] REG=<register> VAL=<value>`：将原始"value"写入寄存器"register"。"value"和"register"都可以是十进制或十六进制整数。请谨慎使用，并参考ADXL345数据表以获取参考。

### [angle]

启用[angle配置部分](Config_Reference.md#angle)时，以下命令可用。

#### ANGLE_CALIBRATE
`ANGLE_CALIBRATE CHIP=<chip_name>`：对给定的传感器执行角度标定(必须存在指定了`stepper`参数的`[angle chip_name]`配置部分)。重要——此工具将命令步进电机移动，而不检查普通运动学边界限制。理想情况下，电机应在执行标定之前从任何打印机托架断开连接。如果步进器无法从打印机断开连接，请确保托架在开始标定之前位于其导轨的中心附近。(步进电机在此测试期间可能向前或向后移动两次完整旋转。)完成此测试后，使用`SAVE_CONFIG`命令将标定数据保存到配置文件。为了使用此工具，必须安装Python"numpy"包(有关详细信息，请参见[测量共振文档](Measuring_Resonances.md#software-installation))。

#### ANGLE_CHIP_CALIBRATE
`ANGLE_CHIP_CALIBRATE CHIP=<chip_name>`：执行内部传感器标定(如果实现)(MT6826S/MT6835)。

- **MT68XX**：电机应在执行标定之前从任何打印机托架断开连接。标定后，应通过断开电源来重置传感器。

#### ANGLE_DEBUG_READ
`ANGLE_DEBUG_READ CHIP=<config_name> REG=<register>`：查询传感器寄存器"register"(例如44或0x2C)。对调试可能有用。这仅适用于tle5012b芯片。

#### ANGLE_DEBUG_WRITE
`ANGLE_DEBUG_WRITE CHIP=<config_name> REG=<register> VAL=<value>`：将原始"value"写入寄存器"register"。"value"和"register"都可以是十进制或十六进制整数。请谨慎使用，并参考传感器数据表以获取参考。这仅适用于tle5012b芯片。

### [axis_twist_compensation]

启用[axis_twist_compensation配置部分](Config_Reference.md#axis_twist_compensation)时，以下命令可用。

#### AXIS_TWIST_COMPENSATION_CALIBRATE
`AXIS_TWIST_COMPENSATION_CALIBRATE [AXIS=<X|Y>] [SAMPLE_COUNT=<value>] [<probe_parameter>=<value>]`：

通过指定目标轴或启用自动标定来标定轴扭曲补偿。

- **SAMPLE_COUNT**：标定期间测试的点数。如果未指定，则默认为3。

- **AXIS**：定义将标定扭曲补偿的轴(`X`或`Y`)。如果未指定，则轴默认为`'X'`。

### [bed_mesh]

启用[bed_mesh配置部分](Config_Reference.md#bed_mesh)时，以下命令可用(另请参见[床网格指南](Bed_Mesh.md))。

#### BED_MESH_CALIBRATE
`BED_MESH_CALIBRATE [PROFILE=<name>] [METHOD=manual] [HORIZONTAL_MOVE_Z=<value>] [<probe_parameter>=<value>] [<mesh_parameter>=<value>] [ADAPTIVE=1] [ADAPTIVE_MARGIN=<value>]`：此命令使用配置中的参数指定的生成点来探测床。探测后，生成网格，并根据网格调整z运动。网格将被保存到`PROFILE`参数指定的配置文件中，或者如果未指定则保存到`default`。有关可选探针参数的详细信息，请参见PROBE命令。如果指定METHOD=manual，则激活手动探针工具——有关此工具处于活动状态时可用的其他命令的详细信息，请参见上面的MANUAL_PROBE命令。可选的`HORIZONTAL_MOVE_Z`值覆盖配置文件中指定的`horizontal_move_z`选项。如果指定ADAPTIVE=1，则将使用由正在打印的G代码文件定义的对象来定义探针区域。可选的`ADAPTIVE_MARGIN`值覆盖配置文件中指定的`adaptive_margin`选项。

### ⚠️ [hc595]

启用[hc595配置部分](Config_Reference.md#hc595)时，以下命令可用。

#### SET_HC595
`SET_HC595 CHIP=<config_name> [BITS=<value>]`：设置或查询HC595的所有输出引脚。不带BITS，报告当前引脚状态。使用BITS，将给定的整数值应用于所有输出(位0=输出0等)。

## 传感器命令

传感器命令涉及查询和检索来自打印机上各种传感器的信息。

### QUERY_ADC
`QUERY_ADC [NAME=<config_name>] [SAMPLE_COUNT=<value>] [SAMPLE_TIME=<value>] [SAMPLES_RESULT=average|median]`：查询配置的模数转换器通道。如果NAME未指定，则返回所有已配置ADC的列表。如果指定NAME，则返回单个命名ADC通道的当前值。`SAMPLE_COUNT`参数设置要收集的样本数(默认值：1)。`SAMPLE_TIME`参数定义MCU在每个样本之间应该等待多少秒(默认值：0)。`SAMPLES_RESULT`参数定义了多个样本应如何处理(默认值：average)。

## 温度命令

温度命令涉及查询和检索与加热器、冷却风扇和温度传感器相关的信息。

### SET_HEATER_TEMPERATURE
`SET_HEATER_TEMPERATURE HEATER=<config_name> [TARGET=<temperature>]`：设置给定加热器的目标温度。如果未提供目标温度，则目标设置为0。

### SET_TEMPERATURE_FAN_TARGET
`SET_TEMPERATURE_FAN_TARGET TEMPERATURE_FAN=<config_name> [TARGET=<temperature>]`：设置温度风扇的目标温度。如果未提供目标温度，则目标设置为0。

### TEMPERATURE_WAIT
`TEMPERATURE_WAIT SENSOR=<config_name> MINIMUM=<value> [MAXIMUM=<value>]`：等待直到给定温度传感器读数大于或等于给定最小值且小于或等于给定最大值。如果未指定MAXIMUM，则默认为给定的MINIMUM。

## 运动命令

运动命令涉及移动工具头和修改移动配置。

### GET_POSITION
`GET_POSITION`：返回工具头的当前位置。提供的值为：
- `mcu`: MCU微控制器报告的工具头位置
- `stepper`: 步进器电机报告的工具头位置
- `kinematic`: 运动学系统计算的工具头位置
- `toolhead`: 工具头报告的当前位置

### SET_VELOCITY_LIMIT
`SET_VELOCITY_LIMIT [VELOCITY=<value>] [ACCEL=<value>] [ACCEL_TO_DECEL=<value>] [SQUARE_CORNER_VELOCITY=<value>] [MINIMUM_CRUISE_RATIO=<value>]`：修改打印机速度限制。可以在运行时查询任何参数而不设置新值。有关这些参数的详细信息，请参见[运动学配置](Config_Reference.md#运动学)部分。

### SET_KINEMATICS_LIMIT
`SET_KINEMATICS_LIMIT [VELOCITY=<value>] [ACCEL=<value>]`：根据运动学对象设置或查询速度和加速度限制(对于具有独立轴限制的运动学类型如corexy、corexz、hybrid_corexy、hybrid_corexz)。

### MANUAL_PROBE
`MANUAL_PROBE [SPEED=<speed>]`：运行手动探针工具。有关此工具的详细信息，请参见上面的PROBE命令。此工具允许用户手动探针打印机床并记录Z位置。有关使用手动探针工具的更多信息，请参见[BED_MESH_CALIBRATE](#bed_mesh)。

### FORCE_MOVE
`FORCE_MOVE STEPPER=<config_name> DIRECTION=[1|-1] DISTANCE=<value> VELOCITY=<value> [ACCEL=<value>]`：强制给定的步进器在给定方向上移动给定距离，距离以毫米为单位，速度为毫米/秒。如果提供，加速度为毫米/秒²。

注意：此命令仅在⚠️[force_move]配置部分启用时可用。该模块在Kalico中默认启用。

### SET_KINEMATICS_POSITION
`SET_KINEMATICS_POSITION [X=<value>] [Y=<value>] [Z=<value>]`：强制更新给定轴的运动学位置。这对于诊断和调试很有用。

### MOVE_AVOIDING_DOCK
`MOVE_AVOIDING_DOCK LOCATION=[safe|dock]`：为支持停靠探针的打印机移动工具头以避免停靠。LOCATION=safe将工具头移到安全位置，LOCATION=dock将其移到停靠位置。

## 挤出机命令

挤出机命令涉及设置多挤出机打印机中的活动挤出机。

### ACTIVATE_EXTRUDER
`ACTIVATE_EXTRUDER EXTRUDER=<config_name>`：激活给定的挤出机。此命令在多挤出机打印机中的挤出机之间切换。

### SET_EXTRUDER_ROTATION_DISTANCE
`SET_EXTRUDER_ROTATION_DISTANCE EXTRUDER=<config_name> [DISTANCE=<value>]`：设置给定挤出机的旋转距离。如果未指定值，则返回当前旋转距离。

### SET_PRESSURE_ADVANCE
`SET_PRESSURE_ADVANCE [EXTRUDER=<config_name>] [ADVANCE=<value>] [SMOOTH_TIME=<value>]`：设置给定挤出机的压力提前参数。如果未指定挤出机，则使用当前活动挤出机。有关压力提前的更多信息，请参见[压力提前指南](Pressure_Advance.md)。

### SET_EXTRUDER_TRFIFO
`SET_EXTRUDER_TRFIFO [EXTRUDER=<config_name>] [COUNT=<value>]`：设置对挤出机TRfifo进行操作的启用状态。

### SYNC_EXTRUDER_MOTION
`SYNC_EXTRUDER_MOTION MOTION_QUEUE=<name> [EXTRUDER=<config_name>]`：将给定的挤出机同步到运动队列。给定的运动队列应为"extruder"或"heater_bed"。
