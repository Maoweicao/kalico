# 配置变更

本文档涵盖了配置文件中最近的不向后兼容的软件变更。在升级 Kalico 软件时，建议查阅本文档。

本文档中的所有日期均为近似值。

## 变更

20260121：Kalico 现在使用自动月度发布标签，格式为 `vYYYY.MM.NN`（例如 `v2026.01.00`）。用户可以将 Moonraker 配置为跟踪稳定的月度发布版本，而不是最新的提交。详见 [从 Klipper 迁移](Migrating_from_Klipper.md#moonraker-update-configuration) 了解配置详情。

20250817：`gcode_button` 部分新增 `debounce_delay` 选项，该选项以秒为单位指定在采取任何操作前对按钮状态进行去抖动的延迟时间。默认值为 0，即不进行去抖动。

20250721：`[pca9632]` 和 `[mcp4018]` 模块不再接受 `scl_pin` 和 `sda_pin` 选项。请改用 `i2c_software_scl_pin` 和 `i2c_software_sda_pin`。

20250425：pwm `[output_pin]`、`[pwm_cycle_time]`、`[pwm_tool]` 及类似配置部分的最大 `cycle_time` 现在为 3 秒（从 5 秒降低）。`[pwm_tool]` 中的 `maximum_mcu_duration` 现在也是 3 秒。

20250816：`filament_switch_sensor` 新增 `debounce_delay` 选项，该选项以秒为单位指定在采取任何操作前对开关状态进行去抖动的延迟时间。默认值为 0，即不进行去抖动。

20250426：`TEST_RESONANCES` 和 `SHAPER_CALIBRATE` 中的选项 `CHIPS=<chip_name>` 现在需要指定加速度芯片的完整名称。例如，使用 `adxl345 rpi` 而不是缩写名 `rpi`。

20250207：tmc5160 新增 `driver_CS` 参数。此前，CS 值几乎总是设置为 31。现在默认值为 31，但可以更改。

20250121：步进电机配置部分中的 `second_homing_speed` 默认值在启用无传感器归位时现在设置为 `homing_speed`。

20250107：tmc2240 的 `rref` 参数现在为必填项，没有默认值。

20241202：`sense_resistor` 参数现在为必填项，没有默认值。

20241201：在某些情况下，Klipper 可能忽略了传统 G-Code 命令中的前导字符或空格。例如，"99M123" 可能被解释为 "M123"，"M 321" 可能被解释为 "M321"。Klipper 现在会通过 "Unknown command" 警告来报告这些情况。

20241125：风扇配置部分中的 `off_below` 参数已弃用。它将在不久后移除。请改用 [`min_power`](./Config_Reference.md#fans)。`printer[fan object].speed` 状态将被 `printer[fan object].value` 和 `printer[fan object].power` 替代。

20241223：`CLEAR_RETRACTION` 命令不再将参数重置为默认配置值，新增了 [`RESET_RETRACTION`](./G-Codes.md#reset_retraction) 命令来实现此功能。事件自动重置行为已被移除。

20240912：`SET_PIN`、`SET_SERVO`、`SET_FAN_SPEED`、`M106` 和 `M107` 命令现在会被合并。此前，如果对同一对象的多个更新发布速度快于最小调度时间（通常为 100ms），则实际更新可能会被推迟到很远的未来。现在，如果快速连续发布多个更新，则可能只有最新的请求会被应用。如果需要之前的行为，请考虑在更新之间添加显式的 `G4` 延迟命令。

20240912：已移除对 `[output_pin]` 配置部分中 `maximum_mcu_duration` 和 `static_value` 参数的支持。这些选项自 20240123 起已弃用。

20240430：`[danger_options]` 配置部分中的 `adc_ignore_limits` 参数已重命名为 `temp_ignore_limits`，现在涵盖所有可能的温度传感器。

20240415：`[virtual_sdcard]` 配置部分中的 `on_error_gcode` 参数现在有默认值。如果未指定此参数，现在默认为 `TURN_OFF_HEATERS`。如果需要之前的行为（在 virtual_sdcard 打印期间出错时不采取默认操作），请定义 `on_error_gcode` 为空值。

20240313：`[printer]` 配置部分中的 `max_accel_to_decel` 参数已弃用。`SET_VELOCITY_LIMIT` 命令的 `ACCEL_TO_DECEL` 参数已弃用。`printer.toolhead.max_accel_to_decel` 状态已被移除。请改用 [minimum_cruise_ratio 参数](./Config_Reference.md#printer)。弃用的功能将在不久后移除，在此期间使用它们可能会导致行为上的细微差异。

20240215：已移除多个弃用的功能。已移除使用 "NTC 100K beta 3950" 作为热敏电阻名称的功能（于 20211110 弃用）。`SYNC_STEPPER_TO_EXTRUDER` 和 `SET_EXTRUDER_STEP_DISTANCE` 命令已被移除，挤出机 `shared_heater` 配置选项已被移除（于 20220210 弃用）。bed_mesh 的 `relative_reference_index` 选项已被移除（于 20230619 弃用）。

20240128：`printer.kinematics` 现在接受 `limited_cartesian` 和 `limited_cartesian` 以及 `limited_corexy`，它们启用了 `max_{x,y}_accel` 和 `max_{x,y}_velocity`（仅适用于 `limited_cartesian`）。将来，此功能可能会移至原始运动学模块中（作为可选设置）。

20240123：已移除 output_pin 的 SET_PIN CYCLE_TIME 参数。如果需要动态更改 pwm 引脚的周期时间，请使用新的 [pwm_cycle_time](Config_Reference.md#pwm_cycle_time) 模块。

20240123：output_pin 的 `maximum_mcu_duration` 参数已弃用。请改用 [pwm_tool 配置部分](Config_Reference.md#pwm_tool)。该选项将在不久后移除。

20240123：output_pin 的 `static_value` 参数已弃用。请替换为 `value` 和 `shutdown_value` 参数。该选项将在不久后移除。

20231216：`[hall_filament_width_sensor]` 更改为在耗材厚度超过 `max_diameter` 时触发耗材用尽。最大直径默认为 `default_nominal_filament_diameter + max_difference`。详见 [[hall_filament_width_sensor] 配置参考](./Config_Reference.md#hall_filament_width_sensor)。

20231207：已移除 `[printer]` 配置部分中几个未文档化的配置参数（buffer_time_low、buffer_time_high、buffer_time_start 和 move_flush_time 参数）。

20231110：Klipper v0.12.0 发布。

20230826：如果 `[dual_carriage]` 中的 `safe_distance` 设置或计算为 0，则根据文档，滑架邻近检查将被禁用。用户可能希望显式配置 `safe_distance` 以防止滑架意外碰撞。此外，在某些配置中，主滑架和双滑架的归位顺序已更改（在某些配置中，两个滑架在同一方向归位，详见 [[dual_carriage] 配置参考](./Config_Reference.md#dual_carriage)）。

20230810：flash-sdcard.sh 脚本现在支持 Bigtreetech SKR-3 的两个变体：STM32H743 和 STM32H723。为此，原始标签 btt-skr-3 现在已更改为 btt-skr-3-h743 或 btt-skr-3-h723。

20230801：设置 `fan.off_bellow` 已更改为 `fan.min_power`。但是，此更改不会影响未使用此设置的用户。通过此更新，在 `min_power` 和 `max_power` 之间引入了 PWM 缩放。需要更高 `min_power` 的风扇现在可以访问其完整的 "安全" 功率曲线。通过正确设置 `min_power`，任何风扇（如 CPAP）即使在 `M106 S1` 时也应能启动。建议检查您的切片器/宏以调整风扇速度。您之前指定的 20% 风扇速度可能不再代表您的最低风扇设置，而是对应于实际的 20% 风扇速度。如果您之前将 `max_power` 设置为低于 1.0（默认值）的任何值，建议使用设置 `min_power: 0` 和 `max_power: 1` 重新校准 `min_power` 和 `kick_start_time`。

20230729：`dual_carriage` 导出的状态已更改。不再是导出 `mode` 和 `active_carriage`，而是将每个滑架的单独模式导出为 `printer.dual_carriage.carriage_0` 和 `printer.dual_carriage.carriage_1`。

20230619：`relative_reference_index` 选项已弃用，并被 `zero_reference_position` 选项取代。有关如何更新配置的详细信息，请参阅 [Bed Mesh 文档](./Bed_Mesh.md#the-deprecated-relative_reference_index)。随着此弃用，`RELATIVE_REFERENCE_INDEX` 不再作为 `BED_MESH_CALIBRATE` gcode 命令的参数可用。

20230530："make menuconfig" 中的默认 canbus 频率现在为 1000000。如果使用 canbus 并且需要其他频率，请确保在编译和刷写微控制器时在 "make menuconfig" 中选择 "Enable extra low-level configuration options" 并指定所需的 "CAN bus speed"。

20230525：如果 `[input_shaper]` 已启用，`SHAPER_CALIBRATE` 命令会立即应用输入整形器参数。

20230407：日志和 `printer.mcu.last_stats` 字段中的 `stalled_bytes` 计数器已重命名为 `upcoming_bytes`。

20230323：在 tmc5160 驱动器上，`multistep_filt` 现在默认启用。在 tmc5160 配置中设置 `driver_MULTISTEP_FILT: False` 以恢复之前的行为。

20230304：`SET_TMC_CURRENT` 命令现在可以正确调整具有该寄存器的驱动器的 globalscaler 寄存器。这消除了在 tmc5160 上，使用 `SET_TMC_CURRENT` 无法将电流提高到高于配置文件中设置的 `run_current` 值的限制。然而，这有一个副作用：运行 `SET_TMC_CURRENT` 后，如果使用 StealthChop2，步进电机必须保持静止 >130ms，以便驱动器执行 AT#1 校准。

20230202：`printer.screws_tilt_adjust` 状态信息的格式已更改。信息现在存储为包含测量结果的螺钉字典。详见 [状态参考](Status_Reference.md#screws_tilt_adjust)。

20230201：`[bed_mesh]` 模块在启动时不再加载 `default` 配置文件。建议使用 `default` 配置文件的用户在其 `START_PRINT` 宏中添加 `BED_MESH_PROFILE LOAD=default`（或在适用时添加到切片器的 "Start G-Code" 配置中）。

20230103：现在可以使用 flash-sdcard.sh 脚本刷写 Bigtreetech SKR-2 的两个变体：STM32F407 和 STM32F429。这意味着原始标签 btt-skr2 现在已更改为 btt-skr-2-f407 或 btt-skr-2-f429。

20221128：Klipper v0.11.0 发布。

20221122：此前，使用 safe_z_home 时，g28 归位后的 z_hop 可能向负 z 方向移动。现在，只有在 g28 后执行 z_hop 会导致正向跳动时才执行 z_hop，这与 g28 归位前发生的 z_hop 行为一致。

20220616：此前可以通过运行 `make flash FLASH_DEVICE=first` 在引导加载程序模式下刷写 rp2040。等效命令现在是 `make flash FLASH_DEVICE=2e8a:0003`。

20220612：rp2040 微控制器现在针对 "rp2040-e5" USB 勘误表有了解决方法。这应该会使初始 USB 连接更可靠。但是，它可能会导致 gpio15 引脚的行为发生变化。gpio15 行为变化不太可能被注意到。

20220407：temperature_fan 的 `pid_integral_max` 配置选项已被移除（于 20210612 弃用）。

20220407：pca9632 LED 的默认颜色顺序现在是 "RGBW"。在 pca9632 配置部分添加显式 `color_order: RBGW` 设置以获取之前的行为。

20220330：neopixel 和 dotstar 模块的 `printer.neopixel.color_data` 状态信息的格式已更改。信息现在存储为颜色列表的列表（而不是字典列表）。详见 [状态参考](Status_Reference.md#led)。

20220307：如果缺少 `P`，`M73` 将不再将打印进度设置为 0。

20220304：[extruder_stepper](Config_Reference.md#extruder_stepper) 配置部分的 `extruder` 参数不再有默认值。如果需要，请显式指定 `extruder: extruder` 以在启动时将步进电机与 "extruder" 运动队列关联。

20220210：`SYNC_STEPPER_TO_EXTRUDER` 命令已弃用；`SET_EXTRUDER_STEP_DISTANCE` 命令已弃用；[extruder](Config_Reference.md#extruder) 的 `shared_heater` 配置选项已弃用。这些功能将在不久后移除。将 `SET_EXTRUDER_STEP_DISTANCE` 替换为 `SET_EXTRUDER_ROTATION_DISTANCE`。将 `SYNC_STEPPER_TO_EXTRUDER` 替换为 `SYNC_EXTRUDER_MOTION`。将使用 `shared_heater` 的挤出机配置部分替换为 [extruder_stepper](Config_Reference.md#extruder_stepper) 配置部分，并更新所有激活宏以使用 [SYNC_EXTRUDER_MOTION](G-Codes.md#sync_extruder_motion)。

20220116：tmc2130、tmc2208、tmc2209 和 tmc2660 的 `run_current` 计算代码已更改。对于某些 `run_current` 设置，驱动器的配置可能有所不同。这个新配置应该更准确，但它可能会使之前的 tmc 驱动器调优失效。

20211230：用于调优输入整形器的脚本（`scripts/calibrate_shaper.py` 和 `scripts/graph_accelerometer.py`）已迁移到默认使用 Python3。因此，用户必须安装某些包的 Python3 版本（例如 `sudo apt install python3-numpy python3-matplotlib`）才能继续使用这些脚本。更多详细信息，请参阅 [软件安装](Measuring_Resonances.md#software-installation)。或者，用户可以通过在控制台中显式调用 Python2 解释器来临时强制在 Python 2 下执行这些脚本：`python2 ~/klipper/scripts/calibrate_shaper.py ...`

20211110："NTC 100K beta 3950" 温度传感器已弃用。此传感器将在不久后移除。大多数用户会发现 "Generic 3950" 温度传感器更准确。要继续使用较旧（通常不太准确）的定义，请定义自定义 [热敏电阻](Config_Reference.md#thermistor)，其中 `temperature1: 25`、`resistance1: 100000` 和 `beta: 3950`。

20211104："make menuconfig" 中的 "step pulse duration" 选项已被移除。配置为 UART 或 SPI 模式的 TMC 驱动器的默认步进持续时间现在为 100ns。需要自定义脉冲持续时间的所有步进电机应在 [stepper 配置部分](Config_Reference.md#stepper) 中设置新的 `step_pulse_duration`。

20211102：已移除多个弃用的功能。步进电机 `step_distance` 选项已被移除（于 20201222 弃用）。`rpi_temperature` 传感器别名已被移除（于 20210219 弃用）。mcu `pin_map` 选项已被移除（于 20210325 弃用）。gcode_macro `default_parameter_<name>` 和通过 `params` 伪变量以外的方式访问宏参数已被移除（于 20210503 弃用）。加热器 `pid_integral_max` 选项已被移除（于 20210612 弃用）。

20210929：Klipper v0.10.0 发布。

20210903：加热器的默认 [`smooth_time`](Config_Reference.md#extruder) 已更改为 1 秒（从 2 秒更改）。对于大多数打印机，这将导致更稳定的温度控制。

20210830：adxl345 的默认名称现在是 "adxl345"。`ACCELEROMETER_MEASURE` 和 `ACCELEROMETER_QUERY` 的默认 CHIP 参数现在也是 "adxl345"。

20210830：adxl345 的 ACCELEROMETER_MEASURE 命令不再支持 RATE 参数。要更改查询速率，请更新 printer.cfg 文件并发出 RESTART 命令。

20210821：`printer.configfile.settings` 中的某些配置设置现在将报告为列表而不是原始字符串。如果需要实际的原始字符串，请改用 `printer.configfile.config`。

20210819：在某些情况下，`G28` 归位移动可能以名义上超出有效运动范围的位置结束。在极少数情况下，这可能会在归位后导致令人困惑的 "Move out of range" 错误。如果发生这种情况，请更改您的启动脚本，以便在归位立即将工具头移动到有效位置。

20210814：atmega168 和 atmega328 上的仅模拟伪引脚已从 PE0/PE1 重命名为 PE2/PE3。

20210720：controller_fan 部分现在默认监控所有步进电机（而不仅仅是运动学步进电机）。如果需要之前的行为，请参阅 [配置参考](Config_Reference.md#controller_fan) 中的 `stepper` 配置选项。

20210703：`samd_sercom` 配置部分现在必须通过 `sercom` 选项指定其正在配置的 sercom 总线。

20210612：加热器和 temperature_fan 部分中的 `pid_integral_max` 配置选项已弃用。该选项将在不久后移除。

20210503：gcode_macro `default_parameter_<name>` 配置选项已弃用。请使用 `params` 伪变量访问宏参数。其他访问宏参数的方法将在不久后移除。大多数用户可以将 `default_parameter_NAME: VALUE` 配置选项替换为宏开头的如下行：`{% set NAME = params.NAME|default(VALUE)|float %}`。有关示例，请参阅 [命令模板文档](Command_Templates.md)。

20210430：SET_VELOCITY_LIMIT（和 M204）命令现在可以设置大于配置文件中指定值的速度、加速度和 square_corner_velocity。

20210325：对 `pin_map` 配置选项的支持已弃用。请使用 [sample-aliases.cfg](../config/sample-aliases.cfg) 文件转换为实际的微控制器引脚名称。`pin_map` 配置选项将在不久后移除。

20210313：Klipper 对使用 CAN 总线通信的微控制器的支持已更改。如果使用 CAN 总线，则必须重新刷写所有微控制器，并且必须更新 [Klipper 配置](CANBUS.md)。

20210310：TMC2660 的 driver_SFILT 默认值已从 1 更改为 0。

20210227：UART 或 SPI 模式的 TMC 步进电机驱动器现在在启用时每秒查询一次——如果无法联系驱动器或驱动器报告错误，则 Klipper 将转换为关机状态。

20210219：`rpi_temperature` 模块已重命名为 `temperature_host`。将任何 `sensor_type: rpi_temperature` 替换为 `sensor_type: temperature_host`。温度文件的路径可以在 `sensor_path` 配置变量中指定。`rpi_temperature` 名称已弃用，将在不久后移除。

20210201：`TEST_RESONANCES` 命令现在会在之前启用输入整形时禁用它（并在测试后重新启用）。要覆盖此行为并保持输入整形启用，可以向命令传递额外参数 `INPUT_SHAPING=1`。

20210201：`ACCELEROMETER_MEASURE` 命令现在会将加速度计芯片的名称附加到输出文件名中，前提是芯片在 printer.cfg 的相应 adxl345 部分中被赋予了名称。

20201222：步进电机配置部分中的 `step_distance` 设置已弃用。建议更新配置以使用 [`rotation_distance`](Rotation_Distance.md) 设置。对 `step_distance` 的支持将在不久后移除。

20201218：endstop_phase 模块中的 `endstop_phase` 设置已替换为 `trigger_phase`。如果使用端点相位模块，则需要转换为 [`rotation_distance`](Rotation_Distance.md) 并通过运行 ENDSTOP_PHASE_CALIBRATE 命令重新校准所有端点相位。

20201218：旋转 delta 和极坐标打印机现在必须为其旋转步进电机指定 `gear_ratio`，并且不再能指定 `step_distance` 参数。有关新 gear_ratio 参数的格式，请参阅 [配置参考](Config_Reference.md#stepper)。

20201213：使用 "probe:z_virtual_endstop" 时，指定 Z "position_endstop" 是无效的。如果使用 "probe:z_virtual_endstop" 指定 Z "position_endstop"，现在将引发错误。请删除 Z "position_endstop" 定义以修复错误。

20201120：`[board_pins]` 配置部分现在在显式 `mcu:` 参数中指定 mcu 名称。如果将 board_pins 用于辅助 mcu，则必须更新配置以指定该名称。有关更多详细信息，请参阅 [配置参考](Config_Reference.md#board_pins)。

20201112：`print_stats.print_duration` 报告的时间已更改。现在排除了第一次检测到挤出之前的时间。

20201029：neopixel 的 `color_order_GRB` 配置选项已被移除。如有必要，请更新配置以将新的 `color_order` 选项设置为 RGB、GRB、RGBW 或 GRBW。

20201029：mcu 配置部分中的 serial 选项不再默认为 /dev/ttyS0。在 /dev/ttyS0 是所需串行端口的极少数情况下，必须显式指定它。

20201020：Klipper v0.9.0 发布。

20200902：MAX31865 转换器的 RTD 电阻到温度计算已更正，不再读取偏低值。如果您使用此类设备，应重新校准打印温度和 PID 设置。

20200816：gcode 宏 `printer.gcode` 对象已重命名为 `printer.gcode_move`。`printer.toolhead` 和 `printer.gcode` 中的几个未文档化变量已被移除。有关可用模板变量的列表，请参阅 docs/Command_Templates.md。

20200816：gcode 宏 "action_" 系统已更改。将任何对 `printer.gcode.action_emergency_stop()` 的调用替换为 `action_emergency_stop()`，将 `printer.gcode.action_respond_info()` 替换为 `action_respond_info()`，将 `printer.gcode.action_respond_error()` 替换为 `action_raise_error()`。

20200809：菜单系统已被重写。如果菜单已被自定义，则需要更新到新的配置。有关配置详情，请参阅 config/example-menu.cfg，有关示例，请参阅 klippy/extras/display/menu.cfg。

20200731：`virtual_sdcard` 打印机对象报告的 `progress` 属性的行为已更改。暂停打印时，进度不再重置为 0。现在它将始终根据内部文件位置报告进度，如果没有加载文件则为 0。

20200725：servo `enable` 配置参数和 SET_SERVO `ENABLE` 参数已被移除。更新任何宏以使用 `SET_SERVO SERVO=my_servo WIDTH=0` 来禁用舵机。

20200608：LCD 显示支持更改了一些内部 "字形" 的名称。如果实现了自定义显示布局，可能需要更新到最新的字形名称（有关可用字形的列表，请参阅 klippy/extras/display/display.cfg）。

20200606：linux mcu 上的引脚名称已更改。引脚现在具有 `gpiochip<chipid>/gpio<gpio>` 形式的名称。对于 gpiochip0，您也可以使用简短的 `gpio<gpio>`。例如，以前称为 `P20` 的现在变为 `gpio20` 或 `gpiochip0/gpio20`。

20200603：默认的 16x4 LCD 布局将不再显示打印中剩余的估计时间。（仅显示已用时间。）如果需要旧行为，可以使用该信息自定义菜单显示（有关详细信息，请参阅 config/example-extras.cfg 中 display_data 的说明）。

20200531：默认的 USB 供应商/产品 ID 现在是 0x1d50/0x614e。这些新 ID 是为 Klipper 保留的（感谢 openmoko 项目）。此更改不需要任何配置更改，但新 ID 可能会出现在系统日志中。

20200524：tmc5160 pwm_freq 字段的默认值现在是零（而不是一）。

20200425：gcode_macro 命令模板变量 `printer.heater` 已重命名为 `printer.heaters`。

20200313：具有 16x4 屏幕的多挤出机打印机的默认 LCD 布局已更改。单挤出机屏幕布局现在是默认布局，它将显示当前活动的挤出机。要使用之前的显示布局，请在 printer.cfg 文件的 [display] 部分中设置 "display_group: _multiextruder_16x4"。

20200308：默认的 `__test` 菜单项已被移除。如果配置文件具有自定义菜单，请确保移除所有对此 `__test` 菜单项的引用。

20200308：菜单的 "deck" 和 "card" 选项已被移除。要自定义 LCD 屏幕的布局，请使用新的 display_data 配置部分（有关详细信息，请参阅 config/example-extras.cfg）。

20200109：bed_mesh 模块现在引用探针的位置用于网格配置。因此，一些配置选项已重命名以更准确地反映其预期功能。对于矩形床，`min_point` 和 `max_point` 已分别重命名为 `mesh_min` 和 `mesh_max`。对于圆形床，`bed_radius` 已重命名为 `mesh_radius`。圆形床还添加了新的 `mesh_origin` 选项。请注意，这些更改与之前保存的网格配置文件也不兼容。如果检测到不兼容的配置文件，它将被忽略并计划删除。可以通过发出 SAVE_CONFIG 命令完成删除过程。用户需要重新校准每个配置文件。

20191218：显示配置部分不再支持 "lcd_type: st7567"。请改用 "uc1701" 显示类型 - 设置 "lcd_type: uc1701" 并将 "rs_pin: some_pin" 更改为 "rst_pin: some_pin"。可能还需要添加 "contrast: 60" 配置设置。

20191210：内置的 T0、T1、T2、... 命令已被移除。挤出机 activate_gcode 和 deactivate_gcode 配置选项已被移除。如果需要这些命令（和脚本），请定义调用 ACTIVATE_EXTRUDER 命令的单个 [gcode_macro T0] 风格的宏。有关示例，请参阅 config/sample-idex.cfg 和 sample-multi-extruder.cfg 文件。

20191210：对 M206 命令的支持已被移除。请替换为对 SET_GCODE_OFFSET 的调用。如果需要 M206 支持，请添加调用 SET_GCODE_OFFSET 的 [gcode_macro M206] 配置部分。（例如 `SET_GCODE_OFFSET Z=-{params.Z}`。）

20191202：对 "G4" 命令未文档化的 "S" 参数的支持已被移除。将任何 S 替换为标准 "P" 参数（以毫秒为单位指定的延迟）。

20191126：具有原生 USB 支持的微控制器上的 USB 名称已更改。它们现在默认使用唯一的芯片 ID（如果可用）。如果 "mcu" 配置部分使用以 "/dev/serial/by-id/" 开头的 "serial" 设置，则可能需要更新配置。在 ssh 终端中运行 "ls /dev/serial/by-id/*" 以确定新的 ID。

20191121：pressure_advance_lookahead_time 参数已被移除。有关替代配置设置，请参阅 example.cfg。

20191112：tmc 步进驱动器虚拟启用功能现在在步进电机没有专用步进启用引脚时自动启用。从配置中移除对 tmcXXXX:virtual_enable 的引用。在 stepper enable_pin 配置中控制多个引脚的功能已被移除。如果需要多个引脚，请使用 multi_pin 配置部分。

20191107：主挤出机配置部分必须指定为 "extruder"，不再能指定为 "extruder0"。查询挤出机状态的 Gcode 命令模板现在通过 "{printer.extruder}" 访问。

20191021：Klipper v0.8.0 发布

20191003：[safe_z_homing] 中的 move_to_previous 选项现在默认为 False。（在 20190918 之前实际上为 False。）

20190918：[safe_z_homing] 中的 zhop 选项在 Z 轴归位完成后始终重新应用。这可能需要用户更新基于此模块的自定义脚本。

20190806：SET_NEOPIXEL 命令已重命名为 SET_LED。

20190726：mcp4728 数模转换代码已更改。默认 i2c_address 现在是 0x60，电压参考现在相对于 mcp4728 的内部 2.048 伏参考。

20190710：z_hop 选项已从 [firmware_retract] 配置部分中移除。z_hop 支持不完整，可能导致几个常见切片器出现不正确的行为。

20190710：PROBE_ACCURACY 命令的可选参数已更改。可能需要更新使用该命令的任何宏或脚本。

20190628：[skew_correction] 部分中的所有配置选项已被移除。skew_correction 的配置现在通过 SET_SKEW gcode 完成。有关推荐用法，请参阅 [倾斜校正](Skew_Correction.md)。

20190607：gcode_macro 的 "variable_X" 参数（以及 SET_GCODE_VARIABLE 的 VALUE 参数）现在被解析为 Python 字面量。如果需要为值分配字符串，请将值包装在引号中，以便将其评估为字符串。

20190606："samples"、"samples_result" 和 "sample_retract_dist" 配置选项已移至 "probe" 配置部分。这些选项在 "delta_calibrate"、"bed_tilt"、"bed_mesh"、"screws_tilt_adjust"、"z_tilt" 或 "quad_gantry_level" 配置部分中不再受支持。

20190528：gcode_macro 模板评估中的神奇 "status" 变量已重命名为 "printer"。

20190520：SET_GCODE_OFFSET 命令已更改；请相应更新任何 G 代码宏。该命令不再将请求的偏移量应用于下一个 G1 命令。旧行为可以通过使用新的 "MOVE=1" 参数来近似。

20190404：Python 宿主软件包已更新。用户需要重新运行 ~/klipper/scripts/install-octopi.sh 脚本（或者如果不使用标准的 OctoPi 安装，则以其他方式升级 python 依赖项）。

20190404：i2c_bus 和 spi_bus 参数（在各种配置部分中）现在接受总线名称而不是数字。

20190404：sx1509 配置参数已更改。'address' 参数现在是 'i2c_address'，必须指定为十进制数。以前使用 0x3E 的地方，请指定 62。

20190328：[temperature_fan] 中的 min_speed 值现在将被尊重，风扇在 PID 模式下始终以此速度或更高速度运行。

20190322：[tmc2660] 配置部分中 "driver_HEND" 的默认值从 6 更改为 3。"driver_VSENSE" 字段已被移除（现在从 run_current 自动计算）。

20190310：[controller_fan] 配置部分现在始终采用名称（例如 [controller_fan my_controller_fan]）。

20190308：[tmc2130] 和 [tmc2208] 配置部分中的 "driver_BLANK_TIME_SELECT" 字段已重命名为 "driver_TBL"。

20190308：[tmc2660] 配置部分已更改。现在必须提供新的 sense_resistor 配置参数。几个 driver_XXX 参数的含义已更改。

20190228：SAMD21 板上使用 SPI 或 I2C 的用户现在必须通过 [samd_sercom] 配置部分指定总线引脚。

20190224：bed_shape 选项已从 bed_mesh 中移除。radius 选项已重命名为 bed_radius。使用圆形床的用户应提供 bed_radius 和 round_probe_count 选项。

20190107：mcp4451 配置部分中的 i2c_address 参数已更改。这是 Smoothieboard 上的常见设置。新值是旧值的一半（88 应更改为 44，90 应更改为 45）。

20181220：Klipper v0.7.0 发布