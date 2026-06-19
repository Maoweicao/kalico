# 状态参考

本文档是 Kalico [宏](Command_Templates.md)、[显示字段](Config_Reference.md#display) 和通过 [API 服务器](API_Server.md) 可用的打印机状态信息的参考。

本文档中的字段可能会更改 - 如果使用某个属性，在升级 Kalico 软件时请务必查阅 [配置变更文档](Config_Changes.md)。

## angle

以下信息可在 [angle some_name](Config_Reference.md#angle) 对象中找到：
- `temperature`：来自 tle5012b 磁性霍尔传感器的最后温度读数（以摄氏度为单位）。此值仅在角度传感器是 tle5012b 芯片且测量正在进行时可用（否则报告 `None`）。

## bed_mesh

以下信息可在 [bed_mesh](Config_Reference.md#bed_mesh) 对象中找到：
- `profile_name`、`mesh_min`、`mesh_max`、`probed_matrix`、`mesh_matrix`：当前活动 bed_mesh 的信息。
- `profiles`：使用 BED_MESH_PROFILE 设置的当前定义的配置文件集。

## bed_screws

以下信息可在 `Config_Reference.md#bed_screws` 对象中找到：
- `is_active`：如果床螺丝调整工具当前处于活动状态，则返回 True。
- `state`：床螺丝调整工具状态。是以下字符串之一："adjust"、"fine"。
- `current_screw`：当前正在调整的螺丝索引。
- `accepted_screws`：已接受的螺丝数量。

## belay

以下信息可在 [belay some_name](Config_Reference.md#belay) 对象中找到：
- `printer["belay <config_name>"].last_state`：如果 belay 的传感器处于触发状态（表示其滑块已压缩），则返回 True。
- `printer["belay <config_name>"].enabled`：如果 belay 当前已启用，则返回 True。

## canbus_stats

以下信息可在 `canbus_stats some_mcu_name` 对象中找到（如果 mcu 配置为使用 canbus，则此对象自动可用）：
- `rx_error`：微控制器 canbus 硬件检测到的接收错误数量。
- `tx_error`：微控制器 canbus 硬件检测到的发送错误数量。
- `tx_retries`：由于总线争用或错误而重试的发送尝试次数。
- `bus_state`：接口状态（通常 "active" 表示正常运行的总线，"warn" 表示最近有错误的总线，"passive" 表示不再发送 canbus 错误帧的总线，或 "off" 表示不再发送或接收消息的总线）。

请注意，只有 rp2XXX 微控制器报告非零 `tx_retries` 字段，且 rp2XXX 微控制器始终将 `tx_error` 报告为零，将 `bus_state` 报告为 "active"。

## configfile

以下信息可在 `configfile` 对象中找到（此对象始终可用）：
- `settings.<section>.<option>`：返回上次软件启动或重启时给定的配置文件设置（或默认值）。（运行时更改的任何设置不会反映在此处。）
- `config.<section>.<option>`：返回 Kalico 在上次软件启动或重启期间读取的给定原始配置文件设置。（运行时更改的任何设置不会反映在此处。）所有值都作为字符串返回。
- `save_config_pending`：如果有 `SAVE_CONFIG` 命令可能持久化到磁盘的更新，则返回 true。
- `save_config_pending_items`：包含已更改并会被 `SAVE_CONFIG` 持久化的部分和选项。
- `warnings`：关于配置选项的警告列表。列表中的每个条目将是一个包含 `type` 和 `message` 字段（都是字符串）的字典。根据警告类型，可能有其他字段可用。

## control_mpc

以下信息可在 `extruder.control_stats` 对象中找到（如果 [extruder](Config_Reference.md#extruder) 配置部分的控制类型设置为 [mpc](MPC.md)，则此对象自动可用）：
- `loss_ambient`：当前/最后的环境损失率。
- `loss_filament`：当前/最后的耗材损失率。
- `filament_temp`：当前耗材温度。
- `filament_heat_capacity`：当前耗材比热容，单位为 J/g/K。
- `filament_density`：当前耗材密度，单位为 g/mm^3。

## display_status

以下信息可在 `display_status` 对象中找到（如果定义了 [display](Config_Reference.md#display) 配置部分，则此对象自动可用）：
- `progress`：最后一个 `M73` G-Code 命令的进度值（或者如果最近没有收到 `M73`，则为 `virtual_sdcard.progress`）。
- `message`：最后一个 `M117` G-Code 命令中包含的消息。

## dockable_probe

以下信息可在 [dockable_probe](Config_Reference.md#dockable_probe) 中找到：
- `last_status`：探针的 UNKNOWN/ATTACHED/DOCKED 状态，如最后一次 QUERY_DOCKABLE_PROBE 命令期间报告。请注意，如果在宏中使用此命令，由于模板扩展顺序，必须在包含此引用的宏之前运行 QUERY_DOCKABLE_PROBE 命令。

## endstop_phase

以下信息可在 [endstop_phase](Config_Reference.md#endstop_phase) 对象中找到：
- `last_home.<stepper name>.phase`：上次归位尝试结束时步进电机的相位。
- `last_home.<stepper name>.phases`：步进电机上可用的总相数。
- `last_home.<stepper name>.mcu_position`：上次归位尝试结束时步进电机的位置（由微控制器跟踪）。位置是自上次微控制器重启以来向前方向采取的总步数减去向后方向采取的总步数。

## exclude_object

以下信息可在 [exclude_object](Exclude_Object.md) 对象中找到：

- `objects`：由 `EXCLUDE_OBJECT_DEFINE` 命令提供的已知对象数组。这与 `EXCLUDE_OBJECT VERBOSE=1` 命令提供的信息相同。`center` 和 `polygon` 字段仅在原始 `EXCLUDE_OBJECT_DEFINE` 中提供时才存在。

  以下是 JSON 示例：
```
[
  {
    "polygon": [
      [ 156.25, 146.2511675 ],
      [ 156.25, 153.7488325 ],
      [ 163.75, 153.7488325 ],
      [ 163.75, 146.2511675 ]
    ],
    "name": "CYLINDER_2_STL_ID_2_COPY_0",
    "center": [ 160, 150 ]
  },
  {
    "polygon": [
      [ 146.25, 146.2511675 ],
      [ 146.25, 153.7488325 ],
      [ 153.75, 153.7488325 ],
      [ 153.75, 146.2511675 ]
    ],
    "name": "CYLINDER_2_STL_ID_1_COPY_0",
    "center": [ 150, 150 ]
  }
]
```
- `excluded_objects`：列出排除对象名称的字符串数组。
- `current_object`：当前正在打印的对象的名称。

## extruder_stepper

以下信息可用于 extruder_stepper 对象（以及 [extruder](Config_Reference.md#extruder) 对象）：
- `pressure_advance`：当前的 [压力提前](Pressure_Advance.md) 值。
- `smooth_time`：当前压力提前平滑时间。
- `motion_queue`：此挤出机步进器当前同步到的挤出机名称。如果挤出机步进器当前未与挤出机关联，则报告为 `None`。

## fan

以下信息可在 [fan](Config_Reference.md#fan)、[heater_fan some_name](Config_Reference.md#heater_fan) 和 [controller_fan some_name](Config_Reference.md#controller_fan) 对象中找到：
- `value`：风扇速度值，介于 0.0 和 1.0 之间的浮点数。
- `power`：风扇功率，介于 0|`min_power` 和 1.0|`max_power` 之间的浮点数。
- `rpm`：如果风扇定义了 tachometer_pin，则为测量的风扇转速（每分钟转数）。
已弃用的对象（仅用于 UI 兼容性）：
- `speed`：风扇速度，介于 0.0 和 `max_power` 之间的浮点数。

## filament_switch_sensor

以下信息可在 [filament_switch_sensor some_name](Config_Reference.md#filament_switch_sensor) 对象中找到：
- `enabled`：如果开关传感器当前已启用，则返回 True。
- `filament_detected`：如果传感器处于触发状态，则返回 True。

## filament_motion_sensor

以下信息可在 [filament_motion_sensor some_name](Config_Reference.md#filament_motion_sensor) 对象中找到：
- `enabled`：如果运动传感器当前已启用，则返回 True。
- `filament_detected`：如果传感器处于触发状态，则返回 True。

## firmware_retraction

以下信息可在 [firmware_retraction](Config_Reference.md#firmware_retraction) 对象中找到：
- `retract_length`：耗材回抽移动长度的当前设置。
- `retract_speed`：耗材回抽移动速度的当前设置。
- `unretract_extra_length`：耗材反回抽移动的额外长度的当前设置（正值将导致耗材挤出，而负值最大为 1 mm（1.75 mm 耗材为 2.41 mm3）将导致耗材滞后挤出）。
- `unretract_speed`：耗材反回抽移动速度的当前设置。
- `unretract_length`：反回抽移动长度（回抽和额外反回抽长度之和）。
- `z_hop_height`：喷嘴抬升移动（Z-Hop）高度的当前设置。
- 如果 `SET_RETRACTION` 命令更改了它们，上述 firmware_retraction 模块的设置可能与配置文件不同。其他可用信息如下。
- `retract_state`：如果耗材已回抽，则返回 'True'。
- `zhop_state`：如果当前应用了 zhop，则返回 'True'。

## gcode

以下信息可在 `gcode` 对象中找到：
- `commands`：返回所有当前可用命令的列表。对于每个命令，如果定义了帮助字符串，也会提供。

## gcode_button

以下信息可在 [gcode_button some_name](Config_Reference.md#gcode_button) 对象中找到：
- `state`：当前按钮状态，返回 "PRESSED" 或 "RELEASED"

## gcode_button

以下信息可在 [gcode_button some_name](Config_Reference.md#gcode_button) 对象中找到：
- `state`：当前按钮状态，返回 "PRESSED" 或 "RELEASED"

## gcode_macro

以下信息可在 [gcode_macro some_name](Config_Reference.md#gcode_macro) 对象中找到：
- `<variable>`：[gcode_macro 变量](Command_Templates.md#variables) 的当前值。

## gcode_move

以下信息可在 `gcode_move` 对象中找到（此对象始终可用）：
- `gcode_position`：工具头相对于当前 G-Code 原点的当前位置。也就是说，可以直接发送到 `G1` 命令的位置。可以访问此位置的 x、y、z 和 e 分量（例如 `gcode_position.x`）。
- `position`：使用配置文件中指定的坐标系的工具头最后命令位置。可以访问此位置的 x、y、z 和 e 分量（例如 `position.x`）。
- `homing_origin`：`G28` 命令后使用的 gcode 坐标系的原点（相对于配置文件中指定的坐标系）。`SET_GCODE_OFFSET` 命令可以更改此位置。可以访问此位置的 x、y 和 z 分量（例如 `homing_origin.x`）。
- `speed`：在 `G1` 命令中设置的最后速度（以 mm/s 为单位）。
- `speed_factor`：由 `M220` 命令设置的 "速度因子覆盖"。这是一个浮点值，其中 1.0 表示不覆盖，例如 2.0 将使请求速度加倍。
- `extrude_factor`：由 `M221` 命令设置的 "挤出因子覆盖"。这是一个浮点值，其中 1.0 表示不覆盖，例如 2.0 将使请求挤出量加倍。
- `absolute_coordinates`：如果在 `G90` 绝对坐标模式下，则返回 True；如果在 `G91` 相对模式下，则返回 False。
- `absolute_extrude`：如果在 `M82` 绝对挤出模式下，则返回 True；如果在 `M83` 相对模式下，则返回 False。

## hall_filament_width_sensor

以下信息可在 [hall_filament_width_sensor](Config_Reference.md#hall_filament_width_sensor) 对象中找到：
- 来自 [filament_switch_sensor](Status_Reference.md#filament_switch_sensor) 的所有项目
- `is_active`：如果传感器当前处于活动状态，则返回 True。
- `Diameter`：传感器的最后读数（以 mm 为单位）。
- `Raw`：传感器的最后原始 ADC 读数。

## heater

以下信息可用于加热器对象，如 [extruder](Config_Reference.md#extruder)、[heater_bed](Config_Reference.md#heater_bed) 和 [heater_generic](Config_Reference.md#heater_generic)：
- `temperature`：给定加热器的最后报告温度（以摄氏度为单位的浮点数）。
- `target`：给定加热器的当前目标温度（以摄氏度为单位的浮点数）。
- `power`：与加热器关联的 PWM 引脚的最后设置（0.0 到 1.0 之间的值）。
- `can_extrude`：如果挤出机可以挤出（由 `min_extrude_temp` 定义），仅适用于 [extruder](Config_Reference.md#extruder)

## heaters

以下信息可在 `heaters` 对象中找到（如果定义了任何加热器，则此对象可用）：
- `available_heaters`：返回所有当前可用加热器的完整配置部分名称列表，例如 `["extruder", "heater_bed", "heater_generic my_custom_heater"]`。
- `available_sensors`：返回所有当前可用温度传感器的完整配置部分名称列表，例如 `["extruder", "heater_bed", "heater_generic my_custom_heater", "temperature_sensor electronics_temp"]`。
- `available_monitors`：返回所有当前可用温度监视器的完整配置部分名称列表，例如 `["tmc2240 stepper_x"]`。虽然温度传感器始终可以读取，但温度监视器可能不可用，在这种情况下将返回 null。

## idle_timeout

以下信息可在 [idle_timeout](Config_Reference.md#idle_timeout) 对象中找到（此对象始终可用）：
- `state`：由 idle_timeout 模块跟踪的打印机当前状态。是以下字符串之一："Idle"、"Printing"、"Ready"。
- `printing_time`：打印机处于 "Printing" 状态的时间量（以秒为单位）（由 idle_timeout 模块跟踪）。

## led

以下信息可用于 printer.cfg 中定义的每个 `[led led_name]`、`[neopixel led_name]`、`[dotstar led_name]`、`[pca9533 led_name]` 和 `[pca9632 led_name]` 配置部分：
- `color_data`：包含链中 LED 的 RGBW 值的颜色列表列表。每个值表示为 0.0 到 1.0 之间的浮点数。每个颜色列表包含 4 个项目（红色、绿色、蓝色、白色），即使底层 LED 支持更少的颜色通道。例如，可以访问链中第二个 neopixel 的蓝色值（颜色列表中的第 3 个项目） `printer["neopixel <config_name>"].color_data[1][2]`。

## load_cell

以下信息可用于每个 `[load_cell name]`：
- 'is_calibrated'：True/False 负载单元是否已校准
- 'counts_per_gram'：等于 1 克力的原始传感器计数
- 'reference_tare_counts'：0 力的参考原始传感器计数
- 'tare_counts'：0 力的当前原始传感器计数
- 'force_g'：以克为单位的力，在最后一个轮询期间取平均值。
- 'min_force_g'：在最后一个轮询期间的最小力（以克为单位）。
- 'max_force_g'：在最后一个轮询期间的最大力（以克为单位）。

## load_cell_probe

以下信息可用于 `[load_cell_probe]`：
- 来自 [load_cell](Status_Reference.md#load_cell) 的所有项目
- 来自 [probe](Status_Reference.md#probe) 的所有项目
- 'endstop_tare_counts'：负载单元探针保持与负载单元独立的去皮值。每次探针开始时重新设置。
- 'last_trigger_time'：最后一次归位触发的时间戳

## manual_probe

以下信息可在 `manual_probe` 对象中找到：
- `is_active`：如果手动探测辅助脚本当前处于活动状态，则返回 True。
- `z_position`：喷嘴的当前高度（根据打印机当前的理解）。
- `z_position_lower`：刚好低于当前高度的最后探测尝试。
- `z_position_upper`：刚好高于当前高度的最后探测尝试。

## mcu

以下信息可在 [mcu](Config_Reference.md#mcu) 和 [mcu some_name](Config_Reference.md#mcu-my_extra_mcu) 对象中找到：
- `mcu_version`：微控制器报告的 Kalico 代码版本。
- `mcu_build_versions`：有关用于生成微控制器代码的构建工具的信息（由微控制器报告）。
- `mcu_constants.<constant_name>`：微控制器报告的编译时常量。可用的常量可能因微控制器架构和每个代码修订而异。
- `last_stats.<statistics_name>`：有关微控制器连接的统计信息。
- `non_critical_disconnected`：mcu 是否已断开连接的 True/False。

## mixing_extruder

以下信息可在 `mixing_extruder` 对象中找到（如果定义了任何步进器配置部分，则此对象自动可用）：

以下信息可在 [mixing_extruder](Config_Reference.md#mixing_extruder) 对象中找到：
- `<mixing>`：配置的挤出机的当前混合权重（以百分比为单位），以逗号分隔
- `<ticks>`：配置的挤出机的当前 mcu 位置的逗号分隔列表

## motion_report

以下信息可在 `motion_report` 对象中找到（如果定义了任何步进器配置部分，则此对象自动可用）：
- `live_position`：插值到当前时间的请求工具头位置。
- `live_velocity`：当前时间的请求工具头速度（以 mm/s 为单位）。
- `live_extruder_velocity`：当前时间的请求挤出机速度（以 mm/s 为单位）。

## output_pin

以下信息可在 [output_pin some_name](Config_Reference.md#output_pin) 和 [pwm_tool some_name](Config_Reference.md#pwm_tool) 对象中找到：
- `value`：由 `SET_PIN` 命令设置的引脚的 "值"。

## palette2

以下信息可在 [palette2](Config_Reference.md#palette2) 对象中找到：
- `ping`：最后报告的 Palette 2 ping 的百分比。
- `remaining_load_length`：开始 Palette 2 打印时，这将是加载到挤出机中的耗材量。
- `is_splicing`：当 Palette 2 正在拼接耗材时为 True。

## pause_resume

以下信息可在 [pause_resume](Config_Reference.md#pause_resume) 对象中找到：
- `is_paused`：如果已执行 PAUSE 命令而没有相应的 RESUME，则返回 true。

## print_stats

以下信息可在 `print_stats` 对象中找到（如果定义了 [virtual_sdcard](Config_Reference.md#virtual_sdcard) 配置部分，则此对象自动可用）：
- `filename`、`total_duration`、`print_duration`、`filament_used`、`state`、`message`：当 virtual_sdcard 打印处于活动状态时，关于当前打印的估计信息。
- `info.total_layer`：最后一个 `SET_PRINT_STATS_INFO TOTAL_LAYER=<value>` G-Code 命令的总层值。
- `info.current_layer`：最后一个 `SET_PRINT_STATS_INFO CURRENT_LAYER=<value>` G-Code 命令的当前层值。

## probe

以下信息可在 [probe](Config_Reference.md#probe) 对象中找到（如果定义了 [bltouch](Config_Reference.md#bltouch) 配置部分，则此对象也可用）：
- `name`：返回正在使用的探针的名称。
- `last_query`：如果探针在最后一次 QUERY_PROBE 命令期间报告为 "triggered"，则返回 True。请注意，如果在宏中使用此命令，由于模板扩展顺序，必须在包含此引用的宏之前运行 QUERY_PROBE 命令。
- `last_z_result`：返回最后一个 PROBE 命令的 Z 结果值。请注意，如果在宏中使用此命令，由于模板扩展顺序，必须在包含此引用的宏之前运行 PROBE（或类似）命令。

## pwm_cycle_time

以下信息可在 [pwm_cycle_time some_name](Config_Reference.md#pwm_cycle_time) 对象中找到：
- `value`：由 `SET_PIN` 命令设置的引脚的 "值"。

## quad_gantry_level

以下信息可在 `quad_gantry_level` 对象中找到（如果定义了 quad_gantry_level，则此对象可用）：
- `applied`：如果龙门架调平过程已运行并成功完成，则为 True。

## query_endstops

以下信息可在 `query_endstops` 对象中找到（如果定义了任何端点，则此对象可用）：
- `last_query["<endstop>"]`：如果给定的端点在最后一次 QUERY_ENDSTOP 命令期间报告为 "triggered"，则返回 True。请注意，如果在宏中使用此命令，由于模板扩展顺序，必须在包含此引用的宏之前运行 QUERY_ENDSTOP 命令。

## screws_tilt_adjust

以下信息可在 `screws_tilt_adjust` 对象中找到：
- `error`：如果最近的 `SCREWS_TILT_CALCULATE` 命令包含 `MAX_DEVIATION` 参数且任何探测的螺钉点超过指定的 `MAX_DEVIATION`，则返回 True。
- `max_deviation`：返回最近的 `SCREWS_TILT_CALCULATE` 命令的最后一个 `MAX_DEVIATION` 值。
- `results["<screw>"]`：包含以下键的字典：
  - `z`：螺钉位置的测量 Z 高度。
  - `sign`：指定调整螺钉所需旋转方向的字符串。"CW" 表示顺时针，"CCW" 表示逆时针。
  - `adjust`：调整螺钉所需的螺钉转动次数，以 "HH:MM" 格式给出，其中 "HH" 是完整螺钉转动次数，"MM" 表示部分螺钉转动的 "时钟面分钟数"。（例如 "01:15" 表示将螺钉转动一又四分之一圈。）
  - `is_base`：如果这是基础螺钉，则返回 True。

## servo

以下信息可在 [servo some_name](Config_Reference.md#servo) 对象中找到：
- `printer["servo <config_name>"].value`：与舵机关联的 PWM 引脚的最后设置（0.0 到 1.0 之间的值）。

## skew_correction.py

以下信息可在 `skew_correction` 对象中找到（如果定义了任何 skew_correction，则此对象可用）：
- `current_profile_name`：返回当前加载的 SKEW_PROFILE 的名称。

## stepper_enable

以下信息可在 `stepper_enable` 对象中找到（如果定义了任何步进器，则此对象可用）：
- `steppers["<stepper>"]`：如果给定的步进器已启用，则返回 True。

## system_stats

以下信息可在 `system_stats` 对象中找到（此对象始终可用）：
- `sysload`、`cputime`、`memavail`：有关宿主操作系统和进程负载的信息。

## 温度传感器

以下信息可在以下对象中找到：

[bme280 config_section_name](Config_Reference.md#bmp180bmp280bme280bmp388bme680-temperature-sensor)、
[htu21d config_section_name](Config_Reference.md#htu21d-sensor)、
[sht3x config_section_name](Config_Reference.md#sht3x-sensor)、
[lm75 config_section_name](Config_Reference.md#lm75-temperature-sensor)、
[temperature_host config_section_name](Config_Reference.md#host-temperature-sensor)
和
[temperature_combined config_section_name](Config_Reference.md#combined-temperature-sensor)
对象：
- `temperature`：来自传感器的最后读取温度。
- `humidity`、`pressure`、`gas`：来自传感器的最后读取值（仅适用于 bme280、htu21d、sht3x 和 lm75 传感器）。

## temperature_fan

以下信息可在 [temperature_fan some_name](Config_Reference.md#temperature_fan) 对象中找到：
- `temperature`：来自传感器的最后读取温度。
- `target`：风扇的目标温度。

## temperature_sensor

以下信息可在 [temperature_sensor some_name](Config_Reference.md#temperature_sensor) 对象中找到：
- `temperature`：来自传感器的最后读取温度。
- `measured_min_temp`、`measured_max_temp`：自上次重启 Kalico 宿主软件以来传感器看到的最低和最高温度。

## tmc 驱动器

以下信息可在 [TMC 步进驱动器](Config_Reference.md#tmc-stepper-driver-configuration) 对象中找到（例如 `[tmc2208 stepper_x]`）：
- `mcu_phase_offset`：与驱动器的 "零" 相位对应的微控制器步进位置。如果相位偏移未知，此字段可能为 null。
- `phase_offset_position`：与驱动器的 "零" 相位对应的 "命令位置"。如果相位偏移未知，此字段可能为 null。
- `drv_status`：最后驱动器状态查询的结果。（仅报告非零字段。）如果驱动器未启用（因此未定期查询），此字段将为 null。
- `temperature`：驱动器报告的内部温度。如果驱动器未启用或驱动器不支持温度报告，此字段将为 null。
- `run_current`：当前设置的运行电流。
- `hold_current`：当前设置的保持电流。

## toolhead

以下信息可在 `toolhead` 对象中找到（此对象始终可用）：
- `position`：工具头相对于配置文件中指定的坐标系的最后命令位置。可以访问此位置的 x、y、z 和 e 分量（例如 `position.x`）。
- `extruder`：当前活动挤出机的名称。例如，在宏中可以使用 `printer[printer.toolhead.extruder].target` 来获取当前挤出机的目标温度。
- `homed_axes`：当前被认为处于 "已归位" 状态的笛卡尔轴。这是一个包含 "x"、"y"、"z" 中一个或多个的字符串。
- `axis_minimum`、`axis_maximum`：归位后的轴行程限制（mm）。可以访问此限制值的 x、y、z 分量（例如 `axis_minimum.x`、`axis_maximum.z`）。
- 对于 Delta 打印机，`cone_start_z` 是最大半径处的最大 z 高度（`printer.toolhead.cone_start_z`）。
- `max_velocity`、`max_accel`、`minimum_cruise_ratio`、`square_corner_velocity`：当前生效的打印限制。如果 `SET_VELOCITY_LIMIT`（或 `M204`）命令在运行时更改了它们，这可能与配置文件设置不同。
- `stalls`：自上次重启以来，打印机因工具头移动速度快于可以从 G-Code 输入读取的移动而必须暂停的总次数。

## dual_carriage

以下信息可在笛卡尔、hybrid_corexy 或 hybrid_corexz 机器人上的 [dual_carriage](Config_Reference.md#dual_carriage) 中找到：
- `carriage_0`：滑架 0 的模式。可能的值为："INACTIVE" 和 "PRIMARY"。
- `carriage_1`：滑架 1 的模式。可能的值为："INACTIVE"、"PRIMARY"、"COPY" 和 "MIRROR"。

## tools_calibrate

以下信息可在 [tools_calibrate](Config_Reference.md#tools_calibrate) 对象中找到：
- `sensor_location`：校准后，传感器的位置
- `last_result`：上次工具校准结果
- `calibration_probe_inactive`：自上次 `TOOL_CALIBRATE_QUERY_PROBE` 以来校准探针的状态

## trad_rack

以下信息可在 [trad_rack](Config_Reference.md#trad_rack) 对象中找到：
- `curr_lane`：选择器当前所在的位置。
- `active_lane`：当前加载到工具头中的位置。
- `next_lane`：如果正在进行工具更改，则下一个要加载到工具头中的位置。
- `next_tool`：如果正在进行工具更改，则下一个要加载到工具头中的工具（如果为工具更改指定了工具编号）。
- `tool_map`：整数数组，列出每个位置分配的工具。可以使用 `tool_map[<lane index>]` 访问指定位置的工具编号。
- `selector_homed`：选择器轴是否已归位。

## virtual_sdcard

以下信息可在 [virtual_sdcard](Config_Reference.md#virtual_sdcard) 对象中找到：
- `is_active`：如果当前正在从文件打印，则返回 True。
- `progress`：当前打印进度的估计（基于文件大小和文件位置）。
- `file_path`：当前加载文件的完整路径。
- `file_position`：活动打印的当前位置（以字节为单位）。
- `file_size`：当前加载文件的文件大小（以字节为单位）。

## webhooks

以下信息可在 `webhooks` 对象中找到（此对象始终可用）：
- `state`：返回指示当前 Kalico 状态的字符串。可能的值为："ready"、"startup"、"shutdown"、"error"。
- `state_message`：提供有关当前 Kalico 状态的额外上下文的人类可读字符串。

## z_thermal_adjust

以下信息可在 `z_thermal_adjust` 对象中找到（如果定义了 [z_thermal_adjust](Config_Reference.md#z_thermal_adjust)，则此对象可用）。
- `enabled`：如果启用调整，则返回 True。
- `temperature`：定义传感器的当前（平滑）温度。[degC]
- `measured_min_temp`：测量的最低温度。[degC]
- `measured_max_temp`：测量的最高温度。[degC]
- `current_z_adjust`：最后计算的 Z 调整 [mm]。
- `z_adjust_ref_temperature`：用于计算 Z `current_z_adjust` 的当前参考温度 [degC]。

## z_tilt

以下信息可在 `z_tilt` 对象中找到（如果定义了 z_tilt，则此对象可用）：
- `applied`：如果 z-tilt 调平过程已运行并成功完成，则为 True。