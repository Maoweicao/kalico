# 状态参考

本文档是Kalico[宏](Command_Templates.md)、[显示字段](Config_Reference.md#display)和[API服务器](API_Server.md)中可用的打印机状态信息的参考。

本文档中的字段可能会更改 - 如果使用属性，请在升级Kalico软件时确保查看[配置更改文档](Config_Changes.md)。

## angle

以下信息在[angle some_name](Config_Reference.md#angle)对象中可用：
- `temperature`：来自tle5012b磁性霍尔传感器的最后一次温度读数（摄氏度）。仅当角度传感器是tle5012b芯片且测量正在进行时，此值才可用（否则报告`None`）。

## bed_mesh

以下信息在[bed_mesh](Config_Reference.md#bed_mesh)对象中可用：
- `profile_name`、`mesh_min`、`mesh_max`、`probed_matrix`、`mesh_matrix`：有关当前活动bed_mesh的信息。
- `profiles`：当前定义的配置文件集，使用BED_MESH_PROFILE设置。

## bed_screws

以下信息在`Config_Reference.md#bed_screws`对象中可用：
- `is_active`：如果当前活动床螺钉调整工具，则返回True。
- `state`：床螺钉调整工具状态。它是以下字符串之一："adjust"、"fine"。
- `current_screw`：当前要调整的螺钉的索引。
- `accepted_screws`：已接受的螺钉数量。

## belay

以下信息在[belay some_name](Config_Reference.md#belay)对象中可用：
- `printer["belay <config_name>"].last_state`：如果belay的传感器处于触发状态（指示其滑块被压缩），则返回True。
- `printer["belay <config_name>"].enabled`：如果当前启用belay，则返回True。

## canbus_stats

以下信息在`canbus_stats some_mcu_name`对象中可用（如果MCU配置为使用canbus，则此对象自动可用）：
- `rx_error`：微控制器canbus硬件检测到的接收错误数。
- `tx_error`：微控制器canbus硬件检测到的传输错误数。
- `tx_retries`：由于总线竞争或错误而重试的传输尝试数。
- `bus_state`：接口的状态（通常正常操作时为"active"，最近出现错误时为"warn"，不再传输canbus错误帧时为"passive"，或不再传输或接收消息时为"off"）。

请注意，只有rp2XXX微控制器报告非零`tx_retries`字段，rp2XXX微控制器始终报告`tx_error`为零，`bus_state`为"active"。

## configfile

以下信息在`configfile`对象中可用（此对象始终可用）：
- `settings.<section>.<option>`：返回给定的配置文件设置（或默认值）在最后一次软件启动或重新启动期间。（在运行时更改的任何设置不会在这里反映。）
- `config.<section>.<option>`：返回给定的原始配置文件设置，如Kalico在最后一次软件启动或重新启动期间所读取的。（在运行时更改的任何设置不会在这里反映。）所有值都作为字符串返回。
- `save_config_pending`：如果有`SAVE_CONFIG`命令可能持久化到磁盘的更新，则返回true。
- `save_config_pending_items`：包含已更改的部分和选项，这些将由`SAVE_CONFIG`持久化。
- `warnings`：关于配置选项的警告列表。列表中的每个条目都是一个字典，包含`type`和`message`字段（都是字符串）。根据警告类型，可能有其他字段可用。

## control_mpc

以下信息在`extruder.control_stats`对象中可用（如果[extruder](Config_Reference.md#extruder)配置部分的控制类型设置为[mpc](MPC.md)，此对象自动可用）：
- `loss_ambient`：当前/最后的环境损耗率。
- `loss_filament`：当前/最后的灯丝损耗率。
- `filament_temp`：当前灯丝温度。
- `filament_heat_capacity`：灯丝的当前比热容量（J/g/K）。
- `filament_density`：灯丝的当前密度（g/mm³）。

## display_status

以下信息在`display_status`对象中可用（如果定义了[display](Config_Reference.md#display)配置部分，此对象自动可用）：
- `progress`：最后一个`M73` G代码命令的进度值（或`virtual_sdcard.progress`，如果最近没有收到`M73`）。
- `message`：最后一个`M117` G代码命令中包含的消息。

## dockable_probe

以下信息在[dockable_probe](Config_Reference.md#dockable_probe)中可用：
- `last_status`：探针的UNKNOWN/ATTACHED/DOCKED状态，如最后一个QUERY_DOCKABLE_PROBE命令所报告的。请注意，如果这在宏中使用，由于模板扩展的顺序，必须在包含此引用的宏之前运行QUERY_DOCKABLE_PROBE命令。

## endstop_phase

以下信息在[endstop_phase](Config_Reference.md#endstop_phase)对象中可用：
- `last_home.<stepper name>.phase`：上一次归零尝试结束时步进电机的阶段。
- `last_home.<stepper name>.phases`：步进电机上可用的总阶段数。
- `last_home.<stepper name>.mcu_position`：上一次归零尝试结束时步进电机的位置（由微控制器跟踪）。该位置是向前方向中采取的总步数减去自微控制器最后一次重启以来反向采取的总步数。

## exclude_object

以下信息在[exclude_object](Exclude_Object.md)对象中可用：
- `objects`：已知对象的数组，由`EXCLUDE_OBJECT_DEFINE`命令提供。这与`EXCLUDE_OBJECT VERBOSE=1`命令提供的信息相同。如果在原始`EXCLUDE_OBJECT_DEFINE`中提供了`center`和`polygon`字段，则只会显示这些字段。

## extruder_stepper

对extruder_stepper对象（以及[extruder](Config_Reference.md#extruder)对象）可用以下信息：
- `pressure_advance`：当前[压力提前](Pressure_Advance.md)值。
- `smooth_time`：当前压力提前平滑时间。
- `motion_queue`：此挤出机步进电机当前同步到的挤出机的名称。如果挤出机步进电机当前未与挤出机关联，则报告为`None`。

## fan

以下信息在[fan](Config_Reference.md#fan)、[heater_fan some_name](Config_Reference.md#heater_fan)和[controller_fan some_name](Config_Reference.md#controller_fan)对象中可用：
- `value`：风扇速度值，介于0.0和1.0之间的浮点数。
- `power`：风扇功率，介于0|`min_power`和1.0|`max_power`之间的浮点数。
- `rpm`：如果风扇定义了tachometer_pin，则以转数/分钟为单位的测量风扇速度。

弃用的对象（仅用于UI兼容性）：
- `speed`：风扇速度，介于0.0和`max_power`之间的浮点数。