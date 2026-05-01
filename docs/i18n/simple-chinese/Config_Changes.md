# 配置变更

本文档涵盖了不向后兼容的配置文件最近软件变更。升级Kalico软件时，查阅本文档是一个好主意。

本文档中的所有日期都是近似的。

## 变更

20260121: Kalico现在使用自动月度发布标签，格式为
`vYYYY.MM.NN`（例如，`v2026.01.00`）。用户可以配置Moonraker跟踪
稳定月度发布而不是最新提交。详见
[从Klipper迁移](Migrating_from_Klipper.md#moonraker-update-configuration)
了解配置详情。

20250817: gcode_button部分添加了新选项`debounce_delay`，
该选项以秒为单位取值，用于在执行任何操作之前消除按钮状态的抖动。
默认值为0，表示没有消抖。

20250721: `[pca9632]`和`[mcp4018]`模块不再接受
`scl_pin`和`sda_pin`选项。改用`i2c_software_scl_pin`和
`i2c_software_sda_pin`。

20250425: pwm `[output_pin]`、
`[pwm_cycle_time]`、`[pwm_tool]`及类似配置部分的最大`cycle_time`
现在为3秒（从5秒降低）。`[pwm_tool]`中的`maximum_mcu_duration`
现在也是3秒。

20250816: filament_switch_sensor添加了新选项`debounce_delay`，
该选项以秒为单位取值，用于在执行任何操作之前消除开关状态的抖动。
默认值为0，表示没有消抖。

20250426: `TEST_RESONANCES`和`SHAPER_CALIBRATE`中的选项`CHIPS=<chip_name>`
需要指定加速度计芯片的完整名称。例如，`adxl345 rpi`而不是短名称`rpi`。

20250207: `driver_CS`参数已添加到tmc5160。之前CS值几乎总是设置为31。
现在默认为31，但可以更改。

20250121: 当启用无传感器回零时，stepper配置部分中的
`second_homing_speed`默认值现在设置为`homing_speed`。

20250107: tmc2240的`rref`参数现在是强制的，没有默认值。

20241202: `sense_resistor`参数现在是强制的，没有默认值。

20241201: 在某些情况下，Klipper可能忽略了传统G代码命令中的前导字符或
空格。例如，"99M123"可能被解释为"M123"，"M 321"可能被解释为
"M321"。Klipper现在会报告这些情况的"未知命令"警告。

20241125: 风扇配置部分中的`off_below`参数已弃用。
它将在不久的将来被删除。改用
[`min_power`](./Config_Reference.md#fans)。`printer[fan object].speed`
状态将被替换为`printer[fan object].value`和`printer[fan object].power`。

20241223: `CLEAR_RETRACTION`命令不再将参数重置为
默认配置值，添加了[`RESET_RETRACTION`](./G-Codes.md#reset_retraction)
命令来实现此功能。自动重置行为已被移除。

20240912: `SET_PIN`、`SET_SERVO`、`SET_FAN_SPEED`、`M106`和`M107`
命令现在被整理。以前，如果对同一对象的许多更新的发送速度快于最小调度时间
（通常为100毫秒），则实际更新可能会排队到未来很久。现在，如果许多更新
快速连续发送，可能只有最新请求会被应用。如果需要以前的行为，
请考虑在更新之间添加显式`G4`延迟命令。

20240912: `[output_pin]`配置部分中对`maximum_mcu_duration`和`static_value`
参数的支持已被移除。这些选项自20240123以来已弃用。

20240430: `[danger_options]`配置部分中的`adc_ignore_limits`参数
已重命名为`temp_ignore_limits`，现在涵盖所有可能的温度传感器。

20240415: `[virtual_sdcard]`配置部分中的`on_error_gcode`参数现在有默认值。
如果未指定此参数，现在默认为`TURN_OFF_HEATERS`。如果需要以前的行为
（在虚拟SD卡打印过程中出错时不采取默认操作），则将`on_error_gcode`
定义为空值。

20240313: `[printer]`配置部分中的`max_accel_to_decel`参数已弃用。
`SET_VELOCITY_LIMIT`命令的`ACCEL_TO_DECEL`参数已弃用。
`printer.toolhead.max_accel_to_decel`状态已被移除。改用
[最小巡航比率参数](./Config_Reference.md#printer)。
弃用的功能将在不久的将来被移除，在此期间使用它们可能会导致
略微不同的行为。

20240215: 已移除多个弃用的功能。使用"NTC 100K beta 3950"作为
热敏电阻名称已被移除（在20211110弃用）。`SYNC_STEPPER_TO_EXTRUDER`和
`SET_EXTRUDER_STEP_DISTANCE`命令已被移除，bed_mesh`relative_reference_index`
选项已被移除（在20230619弃用）。

20240128: `printer.kinematics`现在接受启用`max_{x,y}_accel`和
`max_{x,y}_velocity`（仅适用于`limited_cartesian`）的`limited_cartesian`和
`limited_corexy`。将来，此功能可能被移入原始运动学模块（作为可选设置）。

20240123: output_pin SET_PIN CYCLE_TIME参数已被移除。
如果需要动态更改pwm引脚的周期时间，使用新的
[pwm_cycle_time](Config_Reference.md#pwm_cycle_time)模块。

20240123: output_pin`maximum_mcu_duration`参数已弃用。
改用[pwm_tool配置部分](Config_Reference.md#pwm_tool)。
该选项将在不久的将来被移除。

20240123: output_pin`static_value`参数已弃用。
替换为`value`和`shutdown_value`参数。该选项将在不久的将来被移除。

20231216: `[hall_filament_width_sensor]`已更改为在灯丝厚度超过`max_diameter`时
触发灯丝耗尽。最大直径默认为`default_nominal_filament_diameter + max_difference`。
详见[[hall_filament_width_sensor]配置
参考](./Config_Reference.md#hall_filament_width_sensor)了解更多信息。

20231207: `[printer]`配置部分中已移除多个未记录的配置参数
（buffer_time_low、buffer_time_high、buffer_time_start和move_flush_time参数）。

20231110: Klipper v0.12.0发布。

20230826: 如果在`[dual_carriage]`中`safe_distance`设置或计算为0，
滑车接近度检查将按文档禁用。用户可能希望明确配置`safe_distance`
以防止滑车相互发生意外碰撞。此外，在某些配置中主滑车和双滑车的
回零顺序已更改（某些两个滑车向同一方向回零的配置，详见
[[dual_carriage]配置参考](./Config_Reference.md#dual_carriage)）。

20230810: flash-sdcard.sh脚本现在支持Bigtreetech SKR-3的两种变体，
STM32H743和STM32H723。因此，btt-skr-3的原始标签现已更改为
btt-skr-3-h743或btt-skr-3-h723。

20230801: 设置`fan.off_bellow`已更改为`fan.min_power`。
但是，此更改不会影响不使用此设置的用户。随着此更新，
已引入`min_power`和`max_power`之间的PWM缩放。需要更高`min_power`的风扇
现在可以访问其完整的"安全"功率曲线。通过正确设置`min_power`，
任何风扇（如CPAP）应该即使在`M106 S1`也能启动。建议查看您的切片机/宏
来调整风扇速度。您之前指定的20%风扇速度可能不再代表您的最低风扇设置，
但现在将对应于实际的20%风扇速度。
如果您之前将`max_power`设置为低于1.0（默认值）的任何值，
建议使用设置`min_power: 0`和`max_power: 1`重新校准`min_power`和`kick_start_time`。

20230729: `dual_carriage`的导出状态已更改。代替导出`mode`和`active_carriage`，
每个滑车的各个模式导出为`printer.dual_carriage.carriage_0`和
`printer.dual_carriage.carriage_1`。

20230619: `relative_reference_index`选项已弃用
并由`zero_reference_position`选项取代。详见
[Bed Mesh文档](./Bed_Mesh.md#the-deprecated-relative_reference_index)
了解如何更新配置。随着此弃用，`RELATIVE_REFERENCE_INDEX`
不再作为`BED_MESH_CALIBRATE` gcode命令的参数可用。

20230530: "make menuconfig"中的默认canbus频率
现在为1000000。如果使用canbus且需要使用其他频率的canbus，
请在编译和刷写微控制器时确保选择"启用额外的低级配置选项"
并指定所需的"CAN总线速度"。

20230525: 如果`[input_shaper]`已启用，`SHAPER_CALIBRATE`命令会立即应用
输入整形器参数。

20230407: 日志中和`printer.mcu.last_stats`字段中的`stalled_bytes`计数器
已重命名为`upcoming_bytes`。

20230323: 在tmc5160驱动器上，`multistep_filt`现在默认启用。
设置`driver_MULTISTEP_FILT: False`在tmc5160配置中以获得以前的行为。

20230304: `SET_TMC_CURRENT`命令现在正确调整了有该寄存器的驱动器的
全局缩放寄存器。这消除了在tmc5160上无法使用`SET_TMC_CURRENT`将
电流提高超过配置文件中设置的`run_current`值的限制。
但是，这有一个副作用：运行`SET_TMC_CURRENT`后，如果使用StealthChop2，
步进电机必须停止超过130毫秒，以便驱动器执行AT#1校准。

20230202: `printer.screws_tilt_adjust`状态信息的格式已更改。
该信息现在存储为螺钉字典及其产生的测量。详见
[状态参考](Status_Reference.md#screws_tilt_adjust)了解详情。

20230201: `[bed_mesh]`模块在启动时不再加载`default`配置文件。
建议使用`default`配置文件的用户将`BED_MESH_PROFILE LOAD=default`
添加到其`START_PRINT`宏（或其切片机的"开始G代码"配置）中。

20230103: 现在可以使用flash-sdcard.sh脚本刷写Bigtreetech SKR-2的两种变体，
STM32F407和STM32F429。这意味着btt-skr2的原始标签现已更改为
btt-skr-2-f407或btt-skr-2-f429。

20221128: Klipper v0.11.0发布。

20221122: 以前，使用safe_z_home时，g28回零后的z_hop可能
会沿负z方向进行。现在，只有在z_hop结果为正跳跃时才在g28后执行z_hop，
反映了g28回零前发生的z_hop行为。

20220616: 以前可以通过运行`make flash FLASH_DEVICE=first`在引导加载程序模式下
刷写rp2040。等效命令现在是`make flash FLASH_DEVICE=2e8a:0003`。

20220612: rp2040微控制器现在有"rp2040-e5" USB勘误表的解决方法。
这应该使初始USB连接更可靠。但是，可能会导致gpio15引脚的行为改变。
gpio15行为改变不太可能被注意到。

20220407: temperature_fan`pid_integral_max`配置选项已被移除
（在20210612弃用）。

20220407: pca9632 LED的默认颜色顺序现在为"RGBW"。
添加显式`color_order: RBGW`设置到pca9632配置部分以获得以前的行为。

20220330: neopixel和dotstar模块的`printer.neopixel.color_data`状态
信息格式已更改。该信息现在存储为颜色列表列表（而不是字典列表）。
详见[状态参考](Status_Reference.md#led)了解详情。

20220307: 如果缺少`P`，`M73`将不再将打印进度设置为0。

20220304: [extruder_stepper](Config_Reference.md#extruder_stepper)
配置部分的`extruder`参数不再有默认值。如果需要，明确指定
`extruder: extruder`以在启动时将步进电机与"挤出机"运动队列相关联。

20220210: `SYNC_STEPPER_TO_EXTRUDER`命令已弃用；
`SET_EXTRUDER_STEP_DISTANCE`命令已弃用；
[extruder](Config_Reference.md#extruder)`shared_heater`配置选项
已弃用。这些功能将在不久的将来被移除。
将`SET_EXTRUDER_STEP_DISTANCE`替换为`SET_EXTRUDER_ROTATION_DISTANCE`。
将`SYNC_STEPPER_TO_EXTRUDER`替换为`SYNC_EXTRUDER_MOTION`。
使用`shared_heater`替换extruder配置部分为
[extruder_stepper](Config_Reference.md#extruder_stepper)配置部分
并更新任何激活宏以使用[SYNC_EXTRUDER_MOTION](G-Codes.md#sync_extruder_motion)。

20220116: tmc2130、tmc2208、tmc2209和tmc2660`run_current`
计算代码已更改。对于某些`run_current`设置，驱动器现在可能配置不同。
此新配置应更准确，但可能使以前的tmc驱动器调整无效。

20211230: 用于调整输入整形器的脚本（`scripts/calibrate_shaper.py`
和`scripts/graph_accelerometer.py`）已迁移为默认使用Python3。
因此，用户必须安装某些包的Python3版本
（例如`sudo apt install python3-numpy python3-matplotlib`）以继续使用这些脚本。
详见[软件安装](Measuring_Resonances.md#software-installation)。
或者，用户可以通过在控制台中明确调用Python2解释器来临时强制在Python 2下执行这些脚本：
`python2 ~/klipper/scripts/calibrate_shaper.py ...`

20211110: "NTC 100K beta 3950"温度传感器已弃用。
该传感器将在不久的将来被移除。大多数用户会发现
"Generic 3950"温度传感器更准确。要继续使用较旧的
（通常不太准确的）定义，请定义自定义[thermistor](Config_Reference.md#thermistor)，
其中`temperature1: 25`、`resistance1: 100000`和`beta: 3950`。

20211104: "make menuconfig"中的"step pulse duration"选项已被移除。
在UART或SPI模式下配置的TMC驱动器的默认步长持续时间现在为100ns。
需要自定义脉冲持续时间的所有步进电机的[stepper配置部分](Config_Reference.md#stepper)
中应设置新的`step_pulse_duration`设置。

20211102: 已移除多个弃用的功能。stepper`step_distance`选项已被移除
（在20201222弃用）。`rpi_temperature`传感器别名已被移除
（在20210219弃用）。mcu`pin_map`选项已被移除（在20210325弃用）。
gcode_macro`default_parameter_<name>`和宏访问命令参数以外的`params`
伪变量的方式已被移除（在20210503弃用）。
heater`pid_integral_max`选项已被移除（在20210612弃用）。

20210929: Klipper v0.10.0发布。

20210903: 加热器的默认[`smooth_time`](Config_Reference.md#extruder)
已更改为1秒（从2秒）。对于大多数打印机，这将导致更稳定的温度控制。

20210830: 默认adxl345名称现在为"adxl345"。`ACCELEROMETER_MEASURE`
和`ACCELEROMETER_QUERY`的默认CHIP参数现在也为"adxl345"。

20210830: adxl345 ACCELEROMETER_MEASURE命令不再支持RATE参数。
要更改查询速率，请更新printer.cfg文件并发出RESTART命令。

20210821: `printer.configfile.settings`中的多个配置设置
现在将作为列表而不是原始字符串报告。如果需要实际原始字符串，
改用`printer.configfile.config`。

20210819: 在某些情况下，`G28`回零移动可能以名义上
在有效运动范围外的位置结束。在罕见情况下，
这可能导致回零后令人困惑的"移出范围"错误。
如果发生这种情况，更改您的启动脚本以在回零后立即将工具头移动到有效位置。

20210814: atmega168和atmega328上仅模拟伪引脚
已从PE0/PE1重命名为PE2/PE3。

20210720: controller_fan部分现在默认监视所有步进电机
（不仅仅是运动学步进电机）。如果需要以前的行为，
详见[配置参考](Config_Reference.md#controller_fan)中的`stepper`配置选项。

20210703: `samd_sercom`配置部分现在必须通过`sercom`选项
指定其配置的sercom总线。

20210612: heater和temperature_fan部分中的`pid_integral_max`
配置选项已弃用。该选项将在不久的将来被移除。

20210503: gcode_macro`default_parameter_<name>`配置选项已弃用。
使用`params`伪变量访问宏参数。访问宏参数的其他方法将在不久的将来被移除。
大多数用户可以用宏开头的如下所示的行替换`default_parameter_NAME: VALUE`
配置选项：` {% set NAME = params.NAME|default(VALUE)|float %}`。
详见[命令模板文档](Command_Templates.md)了解示例。

20210430: SET_VELOCITY_LIMIT（和M204）命令现在可以设置
大于配置文件中指定的值的速度、加速度和square_corner_velocity。

20210325: 对`pin_map`配置选项的支持已弃用。使用
[sample-aliases.cfg](../config/sample-aliases.cfg)文件翻译为
实际的微控制器引脚名称。`pin_map`配置选项将在不久的将来被移除。

20210313: Klipper对使用CAN总线通信的微控制器的支持已更改。
如果使用CAN总线，则所有微控制器必须重新刷写并且
[Klipper配置必须更新](CANBUS.md)。

20210310: tmc5160 pwm_freq字段的默认值已从1更改为0。

20210227: UART或SPI模式下的TMC步进电机驱动器现在每秒查询一次
（只要它们被启用）——如果无法联系驱动器或驱动器报告错误，
Klipper将转换为关闭状态。

20210219: `rpi_temperature`模块已重命名为`temperature_host`。
将任何`sensor_type: rpi_temperature`替换为`sensor_type: temperature_host`。
温度文件的路径可以在`sensor_path`配置变量中指定。
`rpi_temperature`名称已弃用并将在不久的将来被移除。

20210201: `TEST_RESONANCES`命令将立即禁用输入整形器
（如果以前启用过）并在测试后重新启用它。要覆盖此行为
并保持输入整形器启用，可以向命令传递附加参数`INPUT_SHAPING=1`。

20210201: 如果在相应的printer.cfg中给加速度计芯片命名，
`ACCELEROMETER_MEASURE`命令现在会将加速度计芯片的名称追加到输出文件名。

20201222: stepper配置部分中的`step_distance`设置已弃用。
建议更新配置以使用[`rotation_distance`](Rotation_Distance.md)设置。
对`step_distance`的支持将在不久的将来被移除。

20201218: endstop_phase模块中的`endstop_phase`设置已被
`trigger_phase`替换。如果使用endstop phases模块，则需要转换为
[`rotation_distance`](Rotation_Distance.md)并通过运行
ENDSTOP_PHASE_CALIBRATE命令重新校准任何endstop phases。

20201218: 旋转增量和极坐标打印机现在必须为其旋转步进电机指定
`gear_ratio`，他们可能不再指定`step_distance`参数。详见
[配置参考](Config_Reference.md#stepper)了解新gear_ratio参数的格式。

20201213: 使用"probe:z_virtual_endstop"时指定Z"position_endstop"无效。
如果使用"probe:z_virtual_endstop"指定Z"position_endstop"，
现在将引发错误。移除Z"position_endstop"定义来修复错误。

20201120: `[board_pins]`配置部分现在在显式`mcu:`参数中指定mcu名称。
如果为辅助mcu使用board_pins，则必须更新配置以指定该名称。
详见[配置参考](Config_Reference.md#board_pins)了解进一步详情。

20201112: `print_stats.print_duration`报告的时间已更改。
首次检测到挤出前的持续时间现在被排除。

20201029: neopixel`color_order_GRB`配置选项已被移除。
如果需要，更新配置以将新的`color_order`选项设置为RGB、GRB、RGBW或GRBW。

20201029: mcu配置部分中的serial选项不再默认为/dev/ttyS0。
在/dev/ttyS0为所需串行端口的罕见情况下，必须明确指定。

20201020: Klipper v0.9.0发布。

20200902: MAX31865转换器的RTD电阻到温度计算已修正，
不会读取过低。如果您使用这样的设备，应重新校准打印温度和PID设置。

20200816: gcode宏`printer.gcode`对象已重命名为`printer.gcode_move`。
`printer.toolhead`和`printer.gcode`中的多个未记录变量已被移除。
详见docs/Command_Templates.md了解可用的模板变量列表。

20200816: gcode宏"action_"系统已更改。将任何调用
`printer.gcode.action_emergency_stop()`替换为`action_emergency_stop()`，
`printer.gcode.action_respond_info()`替换为`action_respond_info()`，
`printer.gcode.action_respond_error()`替换为`action_raise_error()`。

20200809: 菜单系统已被重写。如果菜单已自定义，
则需要更新到新配置。详见config/example-menu.cfg了解配置详情，
见klippy/extras/display/menu.cfg了解示例。

20200731: `virtual_sdcard`打印机对象报告的`progress`
属性行为已更改。暂停打印时不再将进度重置为0。
它现在将始终基于内部文件位置报告进度，或如果当前未加载文件则为0。

20200725: servo`enable`配置参数和SET_SERVO`ENABLE`参数已被移除。
更新任何宏以使用`SET_SERVO SERVO=my_servo WIDTH=0`禁用servo。

20200608: LCD显示支持已更改一些内部"字形"的名称。
如果实现了自定义显示布局，可能需要更新为最新的字形名称
（详见klippy/extras/display/display.cfg了解可用字形列表）。

20200606: linux mcu上的引脚名称已更改。引脚现在具有
`gpiochip<chipid>/gpio<gpio>`形式的名称。对于gpiochip0，
您也可以使用短`gpio<gpio>`。例如，之前称为`P20`的现在变为
`gpio20`或`gpiochip0/gpio20`。

20200603: 默认16x4 LCD布局不再显示打印中的剩余估计时间。
（仅显示已用时间。）如果需要以前的行为，可以通过使用
config/example-extras.cfg中display_data的说明自定义菜单显示
（详见详情）。

20200531: 默认USB供应商/产品ID现在为0x1d50/0x614e。
这些新ID为Klipper预留（感谢openmoko项目）。
此更改不应需要任何配置更改，但新ID可能出现在系统日志中。

20200524: tmc5160 pwm_freq字段的默认值现在为零（而不是一）。

20200425: gcode_macro命令模板变量`printer.heater`已重命名为`printer.heaters`。

20200313: 具有16x4屏幕的多挤出机打印机的默认lcd布局已更改。
单挤出机屏幕布局现在是默认值，将显示当前活动的挤出机。
要使用以前的显示布局，在printer.cfg文件的[display]部分中设置
"display_group: _multiextruder_16x4"。

20200308: 默认`__test`菜单项已被移除。如果配置文件有自定义菜单，
请确保移除所有对此`__test`菜单项的引用。

20200308: 菜单"deck"和"card"选项已被移除。要自定义lcd屏幕的布局，
使用新的display_data配置部分（详见config/example-extras.cfg了解详情）。

20200109: bed_mesh模块现在参考探针位置进行网格配置。
因此，某些配置选项已重命名以更准确地反映其预期功能。
对于矩形床，`min_point`和`max_point`已重命名为`mesh_min`和`mesh_max`。
对于圆形床，`bed_radius`已重命名为`mesh_radius`。为圆形床添加了新的`mesh_origin`选项。
请注意，这些更改也与之前保存的网格配置文件不兼容。
如果检测到不兼容的配置文件，将被忽略并安排删除。可以通过发出
SAVE_CONFIG命令完成删除过程。用户需要重新校准每个配置文件。

20191218: display配置部分不再支持"lcd_type: st7567"。
改用"uc1701"显示类型——设置"lcd_type: uc1701"
并将"rs_pin: some_pin"更改为"rst_pin: some_pin"。
可能还需要添加"contrast: 60"配置设置。

20191210: 内置T0、T1、T2...命令已被移除。extruder
activate_gcode和deactivate_gcode配置选项已被移除。
如果这些命令（和脚本）是必要的，则定义个别[gcode_macro T0]
风格的宏来调用ACTIVATE_EXTRUDER命令。详见config/sample-idex.cfg
和sample-multi-extruder.cfg文件了解示例。

20191210: 对M206命令的支持已被移除。替换为调用SET_GCODE_OFFSET。
如果需要M206支持，添加调用SET_GCODE_OFFSET的[gcode_macro M206]配置部分。
（例如"SET_GCODE_OFFSET Z=-{params.Z}"。）

20191202: 对"G4"命令的未记录"S"参数的支持已被移除。
将任何S出现替换为标准"P"参数（以毫秒为单位指定的延迟）。

20191126: 具有本机USB支持的微控制器上的USB名称已更改。
它们现在默认使用唯一的芯片ID（如果可用）。
如果"mcu"配置部分使用以"/dev/serial/by-id/"开头的"serial"设置，
可能需要更新配置。在ssh终端中运行"ls /dev/serial/by-id/*"确定新ID。

20191121: pressure_advance_lookahead_time参数已被移除。
详见example.cfg了解替代配置设置。

20191112: tmc步进电机驱动程序虚拟启用功能现在自动启用，
如果步进电机没有专用步进电机启用引脚。从配置中移除tmcXXXX:virtual_enable
引用。在stepper enable_pin配置中控制多个引脚的能力已被移除。
如果需要多个引脚，使用multi_pin配置部分。

20191107: 主挤出机配置部分必须指定为"extruder"，
不再可以指定为"extruder0"。查询挤出机状态的gcode命令模板
现在通过"{printer.extruder}"访问。

20191021: Klipper v0.8.0发布

20191003: [safe_z_homing]中的move_to_previous选项现在默认为False。
（在20190918之前它实际上为False。）

20190918: [safe_z_homing]中的zhop选项在Z轴回零完成后总是重新应用。
这可能需要用户更新基于此模块的自定义脚本。

20190806: SET_NEOPIXEL命令已重命名为SET_LED。

20190726: mcp4728数模转换代码已更改。默认i2c_address现在为0x60，
电压参考现在相对于mcp4728的内部2.048伏参考。

20190710: z_hop选项已从[firmware_retract]配置部分移除。
z_hop支持不完整，可能导致多个常见切片机的不正确行为。

20190710: PROBE_ACCURACY命令的可选参数已更改。
可能需要更新任何使用该命令的宏或脚本。

20190628: 已从[skew_correction]部分移除所有配置选项。
skew_correction配置现在通过SET_SKEW gcode完成。
详见[斜率校正](Skew_Correction.md)了解建议的使用方法。

20190607: gcode_macro的"variable_X"参数（以及SET_GCODE_VARIABLE的
VALUE参数）现在被解析为Python文字。如果需要为值分配字符串，
使用引号包装值以使其作为字符串评估。

20190606: "samples"、"samples_result"和"sample_retract_dist"
配置选项已移至"probe"配置部分。这些选项不再在"delta_calibrate"、
"bed_tilt"、"bed_mesh"、"screws_tilt_adjust"、"z_tilt"或
"quad_gantry_level"配置部分中受支持。

20190528: gcode_macro模板评估中的魔术"status"变量已重命名为"printer"。

20190520: SET_GCODE_OFFSET命令已更改；相应更新任何g代码宏。
该命令将不再对下一个G1命令应用所请求的偏移。旧行为可以通过
使用新的"MOVE=1"参数来近似。

20190404: Python主机软件包已更新。用户需要重新运行
~/klipper/scripts/install-octopi.sh脚本（或以其他方式升级python依赖项，
如果未使用标准OctoPi安装）。

20190404: i2c_bus和spi_bus参数（在各种配置部分中）
现在采用总线名称而不是数字。

20190404: sx1509配置参数已更改。'address'参数现在为'i2c_address'
并且必须指定为十进制数。其中之前使用0x3E，现在指定62。

20190328: [temperature_fan]配置中的min_speed值
现在将被尊重，风扇在PID模式下将始终以此速度或更高速度运行。

20190322: [tmc2660]配置部分中"driver_HEND"的默认值已从6更改为3。
已移除"driver_VSENSE"字段（现在从run_current自动计算）。

20190310: [controller_fan]配置部分现在总是采用名称
（如[controller_fan my_controller_fan]）。

20190308: [tmc2130]和[tmc2208]配置部分中的"driver_BLANK_TIME_SELECT"字段
已重命名为"driver_TBL"。

20190308: [tmc2660]配置部分已更改。现在必须提供新的
sense_resistor配置参数。多个driver_XXX参数的含义已更改。

20190228: SAMD21开发板上的SPI或I2C用户现在必须通过
[samd_sercom]配置部分指定总线引脚。

20190224: bed_mesh中的bed_shape选项已被移除。
radius选项已重命名为bed_radius。具有圆形床的用户应提供
bed_radius和round_probe_count选项。

20190107: mcp4451配置部分中的i2c_address参数已更改。
这是Smoothieboards上的常见设置。新值是旧值的一半
（88应更改为44，90应更改为45）。

20181220: Klipper v0.7.0发布