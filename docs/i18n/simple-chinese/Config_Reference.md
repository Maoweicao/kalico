# 配置参考

本文档是 Kalico 配置文件中可用选项的参考。

带有 ⚠️ 标记的配置段和选项表示与原始 Klipper 不同的配置。

本文档中的描述格式使得可以直接复制粘贴到打印机配置文件中。有关设置 Kalico 和选择初始配置文件的信息，请参见[安装文档](Installation.md)。

## 微控制器配置

### 微控制器引脚名称格式

许多配置选项需要微控制器引脚的名称。Kalico 使用这些引脚的硬件名称——例如 `PA4`。

引脚名称前可以加 `!` 表示应使用反向极性（例如，低电平触发而非高电平）。

输入引脚前可以加 `^` 表示为该引脚启用硬件上拉电阻。如果微控制器支持下拉电阻，则输入引脚前也可以加 `~`。

注意，某些配置段可能会"创建"额外的引脚。在这种情况下，定义引脚的配置段必须在任何使用这些引脚的配置段之前在配置文件中列出。

### [mcu]

主微控制器的配置。

```
[mcu]
serial:
#   要连接的串口。如果不确定（或者经常改变），请参见 FAQ 的"我的串口在哪里？"部分。
#   使用串口时必须提供此参数。
#baud: 250000
#   要使用的波特率。默认值为 250000。
#canbus_uuid:
#   如果使用连接到 CAN 总线的设备，则设置要连接的唯一芯片标识符。
#   使用 CAN 总线通信时必须提供此值。
#canbus_interface:
#   如果使用连接到 CAN 总线的设备，则设置要使用的 CAN 网络接口。
#   默认值为"can0"。
#restart_method:
#   这控制主机用于重置微控制器的机制。选择为"arduino"、"cheetah"、
#   "rpi_usb"和"command"。"arduino"方法（切换 DTR）在 Arduino 板及克隆板上很常见。
#   "cheetah"方法是某些 Fysetc Cheetah 板需要的特殊方法。"rpi_usb"方法在 Raspberry Pi
#   板上很有用，其微控制器由 USB 供电——它会暂时禁用所有 USB 端口以完成微控制器重置。
#   "command"方法涉及向微控制器发送 Kalico 命令，以便它可以自行重置。如果微控制器通过
#   串口通信，默认值为"arduino"，否则为"command"。
#is_non_critical: False
#   设置为 True 将允许 MCU 随意断开和重新连接，而不会出现错误。
#   对 USB 加速度计板和 USB/CAN 探针很有用。
```

### [mcu my_extra_mcu]

额外微控制器（可以使用"mcu"前缀定义任意数量的部分）。额外的微控制器引入可配置为加热器、步进器、风扇等的额外引脚。例如，如果引入了"[mcu extra_mcu]"部分，则可以在配置中的其他位置使用"extra_mcu:ar9"之类的引脚（其中"ar9"是给定 MCU 上的硬件引脚名称或别名）。

```
[mcu my_extra_mcu]
# 参见"mcu"部分以获取配置参数。
```

## ⚠️ 危险选项

Kalico 特定的系统选项集合

```
[danger_options]
#error_on_unused_config_options: True
#   如果未使用的配置选项或部分应导致错误，则为 True；
#   如果为 False，将发出警告但允许 Kalico 仍然运行。
#   默认值为 True。
#allow_plugin_override: False
#   允许"plugins"中的模块覆盖"extras"中同名的模块。
#   默认值为 False。
#single_mcu_trsync_timeout: 0.25
#   使用单个 MCU 时主轴同步期间的超时时间（以秒为单位）。默认值为 0.25
#multi_mcu_trsync_timeout: 0.025
#   使用多个 MCU 时主轴同步期间的超时时间（以秒为单位）。默认值为 0.025
#homing_elapsed_distance_tolerance: 0.5
#   第二次主轴移动距离的容差（毫米）。确保在使用无传感器主轴时，
#   第二次主轴距离与"min_home_dist"紧密匹配。默认值为 0.5mm。
#temp_ignore_limits: False
#   设置为 true 时，此参数忽略温度传感器的 min_value 和 max_value 限制。
#   它通过允许超出指定范围的读数而不触发关闭来防止由于"ADC 超出范围"等错误导致的关闭。
#   默认值为 False。
#autosave_includes: False
#   设置为 true 时，SAVE_CONFIG 将递归读取 [include ...] 块以查找冲突以自动保存数据。
#   任何更新的配置都将备份到 configs/config_backups。
#bgflush_extra_time: 0.250
#   这允许设置额外的刷新时间（以秒为单位）。在某些条件下，低值会导致错误（如果未刷新消息），
#   高值 (0.250) 会导致主轴/探针延迟。默认值为 0.250
#homing_start_delay: 0.001
#   开始主轴移动前的停留时间
#endstop_sample_time: 0.000015
#   MCU 应对限位开关状态进行采样的频率
#endstop_sample_count: 4
#   主轴时应检查限位开关状态的次数
#   除非您的限位开关有噪声且不可靠，否则您应该能够将其降低到 1

# 挤出机安全限制覆盖：
#override_pressure_advance_smooth_time_max: 0.200
#   覆盖 pressure_advance_smooth_time（配置和 SET_PRESSURE_ADVANCE）的最大值。
#   对于需要超出内置默认值的非标准设置很有用。默认值为 0.200。

# 日志选项：

#minimal_logging: False
#   为所有日志选项设置默认值。默认值为 False。
#log_statistics: True
#   是否应记录统计信息
#   (有助于在开发过程中保持日志清洁)
#   默认值为 True。
#log_config_file_at_startup: True
#   启动时是否应记录配置文件
#   默认值为 True。
#log_bed_mesh_at_startup: True
#   启动时是否应记录床网格
#   (有助于在开发过程中保持日志清洁)
#   默认值为 True。
#log_velocity_limit_changes: True
#   是否应记录速度限制的变化。如果为 False，速度限制将仅在翻转时记录。
#   某些切片软件会发出非常频繁的 SET_VELOCITY_LIMIT 命令。
#   默认值为 True
#log_pressure_advance_changes: True
#   是否应记录压力提前的变化。如果为 false，压力提前数据将仅在翻转时记录。
#   默认值为 True。
#log_shutdown_info: True
#   发生异常时是否应记录详细的崩溃信息
#   大部分内容过于冗长和无用，我们仍然会获得常见异常的堆栈跟踪，
#   因此设置为 False 可以帮助在开发时节省时间
#   默认值为 True。
#log_serial_reader_warnings: True
#log_startup_info: True
#log_webhook_method_register_messages: False
```

## ⚠️ 配置引用

在您的配置中，您可以引用其他值以在多个部分之间共享配置。引用采用 `${option}` 的形式来复制当前部分中的值，或 `${section.option}` 来在配置中的其他位置查找值。注意，常数必须始终为小写。

也可以使用 `[constants]` 部分专门存储这些值。未使用的常数将显示警告。但是，如果没有使用任何常数，`[constants]` 将显示错误。

```
[constants]
run_current_ab:  1.0
i_am_not_used: True  # 将显示"常数'i_am_not_used'未被使用"

[tmc5160 stepper_x]
run_current: ${constants.run_current_ab}

[tmc5160 stepper_y]
run_current: ${tmc5160 stepper_x.run_current}
#   嵌套引用有效，但不建议使用
```

如果需要，引用可以转义为 `\${such}`

## 通用运动学设置

### [printer]

打印机部分控制高级打印机设置。

```
[printer]
kinematics:
#   正在使用的打印机类型。此选项可能是以下之一：cartesian（直角坐标）、
#   corexy、corexz、hybrid_corexy、hybrid_corexz、rotary_delta、delta、
#   deltesian、polar、winch 或 none。必须指定此参数。
max_velocity:
#   工具头的最大速度（毫米/秒）（相对于打印）。此值可以在运行时使用
#   SET_VELOCITY_LIMIT 命令更改。必须指定此参数。
max_accel:
#   工具头的最大加速度（毫米/秒²）（相对于打印）。虽然此参数被描述为"最大"加速度，
#   但实际上大多数加速或减速的移动都会以此处指定的速率进行。此处指定的值
#   可以在运行时使用 SET_VELOCITY_LIMIT 命令更改。必须指定此参数。
#minimum_cruise_ratio: 0.5
#   大多数移动会加速到巡航速度、以该巡航速度移动，然后减速。但是，某些
#   移动距离较短的移动可能会名义上加速然后立即减速。此选项降低这些移动的
#   最高速度以确保始终有最小距离在巡航速度下移动。也就是说，它强制在相对于
#   总距离的巡航速度下移动最小距离。它旨在降低短之字形移动的最高速度（从而
#   减少这些移动对打印机的震动）。例如，0.5 的 minimum_cruise_ratio 将确保
#   独立的 1.5mm 移动的最小巡航距离为 0.75mm。指定 0.0 以禁用此功能（不会
#   在加速和减速之间强制执行最小巡航距离）。此处指定的值可以在运行时使用
#   SET_VELOCITY_LIMIT 命令更改。默认值为 0.5。
#square_corner_velocity: 5.0
#   工具头可在 90 度角处移动的最大速度（毫米/秒）。非零值可以通过在转角处启用
#   工具头的瞬时速度变化来减少挤出机流速的变化。此值配置内部离心速度转角算法；
#   大于 90 度的角的转角速度将更高，而小于 90 度的角的转角速度将更低。
#   如果设置为零，工具头将在每个角处减速到零。此处指定的值可以在运行时使用
#   SET_VELOCITY_LIMIT 命令更改。默认值为 5mm/s。
#max_accel_to_decel:
#   此参数已弃用，不应再使用。
```

### [stepper]

步进电机定义。不同的打印机类型（由 [printer] 配置部分中的"kinematics"选项指定）需要步进器的不同名称（例如 `stepper_x` vs `stepper_a`）。下面是常见的步进器定义。

有关计算 `rotation_distance` 参数的信息，请参见[旋转距离文档](Rotation_Distance.md)。有关使用多个微控制器进行主轴的信息，请参见[多 MCU 主轴](Multi_MCU_Homing.md)文档。

```
[stepper_x]
step_pin:
#   步进 GPIO 引脚（高电平触发）。必须提供此参数。
dir_pin:
#   方向 GPIO 引脚（高电平表示正方向）。必须提供此参数。
enable_pin:
#   启用引脚（默认为启用高电平；使用 ! 表示启用低电平）。如果未提供此参数，
#   则步进电机驱动必须始终启用。
rotation_distance:
#   轴通过一次完整步进电机旋转（如果指定了 gear_ratio，则为最终齿轮）
#   移动的距离（毫米）。必须提供此参数。
microsteps:
#   步进电机驱动使用的微步数。必须提供此参数。
#full_steps_per_rotation: 200
#   步进电机一次旋转的完整步数。对于 1.8 度步进电机，设置为 200；
#   对于 0.9 度电机，设置为 400。默认值为 200。
#gear_ratio:
#   如果步进电机通过齿轮箱连接到轴，则为齿轮比。例如，如果使用 5:1 减速箱，
#   可以指定"5:1"。如果轴有多个齿轮箱，可以指定逗号分隔的齿轮比列表
#   (例如"57:11, 2:1")。如果指定了 gear_ratio，则 rotation_distance 指定
#   轴通过最终齿轮的一次完整旋转移动的距离。默认值为不使用齿轮比。
#step_pulse_duration:
#   步进脉冲信号边与随后的"取消步进"信号边之间的最小时间。这也用于设置
#   步进脉冲与方向更改信号之间的最小时间。对于 UART 或 SPI 模式下配置的 TMC
#   步进器，默认值为 0.000000100 (100ns)，对于所有其他步进器，默认值为 0.000002 (2us)。
endstop_pin:
#   限位开关检测引脚。如果此限位引脚与步进电机在不同的 MCU 上，则启用
#   "多 MCU 主轴"。对于直角坐标打印机上的 X、Y 和 Z 步进器，必须提供此参数。
#position_min: 0
#   用户可能命令步进器移动到的最小有效距离（毫米）。默认值为 0mm。
position_endstop:
#   限位开关位置（毫米）。对于直角坐标打印机上的 X、Y 和 Z 步进器，必须提供此参数。
position_max:
#   用户可能命令步进器移动到的最大有效距离（毫米）。对于直角坐标打印机上的 X、Y 和 Z 步进器，必须提供此参数。
#homing_speed: 5.0
#   主轴时步进器的最大速度（毫米/秒）。默认值为 5mm/s。
#homing_accel:
#   主轴时步进器的最大加速度（毫米/秒²）。默认值为使用 [printer] 对象中配置的最大加速度。
#homing_retract_dist: 5.0
#   主轴第二次前回退的距离（毫米）。如果 `use_sensorless_homing` 为 false，
#   可以将此设置设置为零以禁用第二个主轴。如果 `use_sensorless_homing` 为 true，
#   此设置可以 > 0 以在主轴后回退。默认值为 5mm。
#homing_retract_speed:
#   主轴后的回退移动上要使用的速度，以防此速度应与主轴速度不同（默认值）
#min_home_dist:
#   主轴前工具头的最小距离（毫米）。如果比 `min_home_dist` 更接近限位开关，
#   则向该距离远离，然后主轴。如果更远，则直接主轴并回退到 `homing_retract_dist`。
#   默认值等于 `homing_retract_dist`。
#second_homing_speed:
#   执行第二个主轴时步进器的速度（毫米/秒）。默认值为 homing_speed/2。
#   如果 `use_sensorless_homing` 为 true，默认值为 homing_speed。
#homing_positive_dir:
#   如果为 true，主轴会导致步进器向正方向移动（离开零）；如果为 false，则朝零主轴。
#   最好使用默认值而不是指定此参数。如果 position_endstop 接近 position_max，
#   则默认值为 true；如果接近 position_min，则默认值为 false。
#use_sensorless_homing:
#   如果为 true，且 homing_retract_dist > 0，则禁用第二个主轴动作。
#   默认值为 true，如果 endstop_pin 配置为使用 virtual_endstop。
```

### 直角坐标运动学

查看 [example-cartesian.cfg](../config/example-cartesian.cfg) 获取直角坐标运动学配置文件的示例。

此处仅描述直角坐标打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: cartesian
max_z_velocity:
#   这设置沿 z 轴运动的最大速度（毫米/秒）。此设置可用于限制 z 步进电机的最大速度。
#   默认值是对 max_z_velocity 使用 max_velocity。
max_z_accel:
#   这设置沿 z 轴运动的最大加速度（毫米/秒²）。它限制 z 步进电机的加速度。
#   默认值是对 max_z_accel 使用 max_accel。

# stepper_x 部分用于描述直角坐标机器人中控制 X 轴的步进器。
[stepper_x]

# stepper_y 部分用于描述直角坐标机器人中控制 Y 轴的步进器。
[stepper_y]

# stepper_z 部分用于描述直角坐标机器人中控制 Z 轴的步进器。
[stepper_z]
```

### ⚠️ 带 X 和 Y 轴限制的直角坐标运动学

行为与直角坐标运动学完全相同，但允许为 X 和 Y 轴设置速度和加速度限制。这还使命令 [`SET_KINEMATICS_LIMIT`](./G-Codes.md#set_kinematics_limit) 可用于在运行时设置这些限制。

```
[printer]
kinematics: limited_cartesian
max_x_velocity:
#   这设置沿 x 轴运动的最大速度（毫米/秒）。此设置可用于限制 x 步进电机的最大速度。
#   默认值是对 max_x_velocity 使用 max_velocity。
max_y_velocity:
#   这设置沿 y 轴运动的最大速度（毫米/秒）。此设置可用于限制 y 步进电机的最大速度。
#   默认值是对 max_y_velocity 使用 max_velocity。
max_z_velocity:
#   参见上面的 cartesian。
max_velocity:
#   为了在对角线上获得最大速度增益，这应该等于或大于 max_x_velocity 和 max_y_velocity
#   的斜边（sqrt(x*x + y*y)）。
max_x_accel:
#   这设置沿 x 轴运动的最大加速度（毫米/秒²）。它限制 x 步进电机的加速度。
#   默认值是对 max_x_accel 使用 max_accel。
max_y_accel:
#   这设置沿 y 轴运动的最大加速度（毫米/秒²）。它限制 y 步进电机的加速度。
#   默认值是对 max_y_accel 使用 max_accel。
max_z_accel:
# 参见上面的 cartesian。
max_accel:
# 参见上面的 cartesian。
scale_xy_accel: False
#   当为真时，按当前工具头加速度缩放 XY 限制。
#   系数为：slicer accel / hypot(max_x_accel, max_y_accel)。
#   参见下文。
```

如果 scale_xy_accel 为 `False`，则由 `max_accel`、M204 或 SET_VELOCITY_LIMIT 设置的加速度充当第三个限制。在这种情况下，如果移动的加速度低于 `max_x_accel` 和 `max_y_accel`，此模块不会应用限制。当 scale_xy_accel 为 `True` 时，`max_x_accel` 和 `max_y_accel` 按动态设置加速度与 max_x_accel 和 `max_y_accel` 斜边的比率进行缩放，如 `SET_KINEMATICS_LIMIT` 所报告的。这意味着实际加速度将始终取决于方向。例如，这些设置：

```
[printer]
max_x_accel: 12000
max_y_accel: 9000
scale_xy_accel: true
```

在 37° 对角线上，`SET_KINEMATICS_LIMIT` 将报告最大加速度为 15000 mm/s²。如果切片软件发出 `M204 S3000`（3000 mm/s² 加速度）。在这 37° 和 143° 对角线上，工具头将以 3000 mm/s² 加速。在 X 轴上，加速度将为 12000 * 3000 / 15000 = 2400 mm/s²，而对于纯 Y 移动则为 18000 mm/s²。

（文档持续...由于篇幅限制，翻译将在多个文件块中继续）

### 线性 Delta 运动学

查看 [example-delta.cfg](../config/example-delta.cfg) 获取线性 delta 运动学配置文件的示例。参见 [delta 标定指南](Delta_Calibrate.md) 了解标定信息。

此处仅描述线性 delta 打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

\\\
[printer]
kinematics: delta
max_z_velocity:
#   对于 delta 打印机，这限制了具有 z 轴运动的移动的最大速度（毫米/秒）。
#   此设置可用于减少向上/向下移动的最大速度（这在 delta 打印机上需要比其他移动更高的步进速率）。
#   默认值是对 max_z_velocity 使用 max_velocity。
#max_z_accel:
#   这设置沿 z 轴运动的最大加速度（毫米/秒²）。如果打印机可以在 XY 移动上达到更高的加速度
#   比 Z 移动更高（例如使用输入整形器时），这可能很有用。
#   默认值是对 max_z_accel 使用 max_accel。
#minimum_z_position: 0
#   用户可能命令头部移动到的最小 Z 位置。默认值为 0。
delta_radius:
#   由三个线性轴塔形成的水平圆形的半径（毫米）。此参数也可计算为：
#    delta_radius = smooth_rod_offset - effector_offset - carriage_offset
#   必须提供此参数。
#print_radius:
#   有效工具头 XY 坐标的半径（毫米）。可以使用此设置来自定义工具头移动的范围检查。
#   如果在此处指定了大值，则可能可以将工具头命令到与塔的碰撞中。
#   默认值是对 print_radius 使用 delta_radius（这通常会防止塔碰撞）。

# stepper_a 部分描述控制前左塔（位于 210 度）的步进器。
# 此部分也控制所有塔的主轴参数（homing_speed、homing_retract_dist）。
[stepper_a]
position_endstop:
#   喷嘴与床之间的距离（毫米），当喷嘴位于建造面的中心且限位开关触发时。
#   此参数必须为 stepper_a 提供；对于 stepper_b 和 stepper_c，此参数默认为
#   为 stepper_a 指定的值。
arm_length:
#   连接此塔与打印头的对角线杆的长度（毫米）。此参数必须为 stepper_a 提供；
#   对于 stepper_b 和 stepper_c，此参数默认为为 stepper_a 指定的值。
#angle:
#   此选项指定塔所在的角度（以度为单位）。stepper_a 的默认值为 210，
#   stepper_b 为 330，stepper_c 为 90。

# stepper_b 部分描述控制前右塔（位于 330 度）的步进器。
[stepper_b]

# stepper_c 部分描述控制后塔（位于 90 度）的步进器。
[stepper_c]

# delta_calibrate 部分启用可以标定塔限位位置和角度的 DELTA_CALIBRATE
# 扩展 g 代码命令。
[delta_calibrate]
radius:
#   可能被探针的区域的半径（毫米）。这是要探针的喷嘴坐标的半径；
#   如果使用具有 XY 偏移的自动探针，则选择一个足够小的半径，以便探针
#   总是位于床的上方。必须提供此参数。
#speed: 50
#   标定期间非探针移动的速度（毫米/秒）。默认值为 50。
#horizontal_move_z: 5
#   在开始探针操作之前应命令头部移动到的高度（毫米）。默认值为 5。
#use_probe_xy_offsets: False
#   如果为 True，将 \[probe]\ XY 偏移应用于探针位置。默认值为 False。
\\\

### [extruder]

挤出机部分用于描述喷嘴热端的加热器参数以及控制挤出机的步进器。有关其他信息，请参见[命令参考](G-Codes.md#extruder)。有关调整压力提前的信息，请参见[压力提前指南](Pressure_Advance.md)。有关控制方法的更多详细信息，请参见 [PID](PID.md) 或 [MPC](MPC.md)。

\\\
[extruder]
step_pin:
dir_pin:
enable_pin:
microsteps:
rotation_distance:
#full_steps_per_rotation:
#gear_ratio:
#   参见"stepper"部分以获取对上述参数的描述。如果未指定上述任何参数，
#   则不会将任何步进器与喷嘴热端关联（尽管 SYNC_EXTRUDER_MOTION 命令可能在运行时关联一个）。
nozzle_diameter:
#   喷嘴孔径（毫米）。必须提供此参数。
filament_diameter:
#   进入挤出机的原始灯丝的名义直径（毫米）。必须提供此参数。
#max_extrude_cross_section:
#   最大挤出截面面积（毫米²）（例如，挤出宽度乘以层高）。此设置可防止
#   在相对较小的 XY 移动期间过度挤出。如果移动请求超过此值的挤出速率，
#   则会返回错误。默认值为：4.0 * nozzle_diameter^2
#instantaneous_corner_velocity: 1.000
#   两次移动交界处挤出机的最大瞬时速度变化（毫米/秒）。默认值为 1mm/s。
#max_extrude_only_distance: 50.0
#   回退或仅挤出移动可能具有的最大长度（毫米的原始灯丝）。如果回退或仅挤出
#   移动请求大于此值的距离，将返回错误。默认值为 50mm。
#max_extrude_only_velocity:
#max_extrude_only_accel:
#   挤出机电机对于回退和仅挤出移动的最大速度（毫米/秒）和加速度（毫米/秒²）。
#   这些设置对正常打印移动没有任何影响。如果未指定，则计算为匹配具有 
#   4.0*nozzle_diameter^2 截面的 XY 打印移动所具有的限制。
#pressure_advance: 0.0
#   在挤出机加速期间推入挤出机的原始灯丝量。在减速期间回退等量的灯丝。
#   以毫米/毫米/秒为单位。默认值为 0，禁用压力提前。
#pressure_advance_smooth_time: 0.040
#   用于计算挤出机平均速度以实现压力提前的时间范围（以秒为单位）。
#   较大的值会导致更平滑的挤出机移动。此参数不能超过 200ms。
#   此设置仅在 pressure_advance 非零时适用。默认值为 0.040（40 毫秒）。
#
# 其余变量描述挤出机加热器。
heater_pin:
#   控制加热器的 PWM 输出引脚。必须提供此参数。
#max_power: 1.0
#   可将 heater_pin 设置为的最大功率（表示为 0.0 到 1.0 的值）。值 1.0 允许
#   在长时间内将引脚设置为完全启用，而 0.5 的值最多允许在一半的时间内启用该引脚。
#   此设置可用于限制总功率输出（在扩展时间内）到加热器。默认值为 1.0。
sensor_type:
#   传感器类型——常见的温度计是"EPCOS 100K B57560G104F"、
#   "ATC Semitec 104GT-2"、"ATC Semitec 104NT-4-R025H42G"、"Generic 3950"、
#   "Honeywell 100K 135-104LAG-J01"、"NTC 100K MGB18-104F39050L32"、
#   "SliceEngineering 450"和"TDK NTCG104LH104JT1"。有关其他传感器，
#   请参见"温度传感器"部分。必须提供此参数。
sensor_pin:
#   连接到传感器的模拟输入引脚。必须提供此参数。
#pullup_resistor: 4700
#   连接到温度计的上拉电阻的电阻（欧姆）。只有在传感器是温度计时，
#   此参数才有效。默认值为 4700 欧姆。
#smooth_time: 1.0
#   对温度测量进行平滑处理的时间值（以秒为单位），以减少测量噪声的影响。
#   默认值为 1 秒。
control:
#   控制算法（pid、pid_v、dual_loop_pid、watermark 或 mpc）。
#   必须提供此参数。pid_v 仅应在具有低到中等噪声的良好标定加热器上使用。
#
#   如果 control: pid、pid_v 或 dual_loop_pid
#pid_Kp:
#pid_Ki:
#pid_Kd:
#   PID 反馈控制系统的比例 (pid_Kp)、积分 (pid_Ki) 和导数 (pid_Kd) 设置。
#   Kalico 使用以下通用公式评估 PID 设置：
#     heater_pwm = (Kp*error + Ki*integral(error) - Kd*derivative(error)) / 255
#   其中"error"是"requested_temperature - measured_temperature"，
#   "heater_pwm"是请求的加热速率，0.0 为完全关闭，1.0 为完全打开。
#   考虑使用 PID_CALIBRATE 命令来获取这些参数。pid_Kp、pid_Ki 和 pid_Kd 
#   参数必须为 PID 加热器提供。
#
#   如果 control: watermark
#max_delta: 2.0
#   在"watermark"控制的加热器上，这是禁用加热器之前目标温度以上的摄氏度数，
#   以及重新启用加热器之前目标温度以下的摄氏度数。默认值为 2 摄氏度。
#
#   如果 control: mpc
#   有关这些参数的详细信息，请参见 MPC.md。
#heater_power:
#cooling_fan:
#ambient_temp_sensor:
#filament_diameter: 1.75
#filament_density: 1.2
#filament_heat_capacity: 1.8
#
#pwm_cycle_time: 0.100
#   每个加热器软件 PWM 周期的时间（秒）。除非有电气要求以每秒超过 10 次的速率
#   切换加热器，否则不建议设置此值。默认值为 0.100 秒。
#min_extrude_temp: 170
#   可能发出挤出机移动命令的最低温度（摄氏度）。默认值为 170 摄氏度。
min_temp:
max_temp:
#   加热器必须保持在其中的有效温度范围（摄氏度）。这控制了在微控制器代码中
#   实现的安全功能——如果测量的温度曾经超出此范围，微控制器将进入关闭状态。
#   此检查可以帮助检测某些加热器和传感器硬件故障。设置此范围的宽度足以使得
#   合理的温度不会导致错误。必须提供这些参数。
per_move_pressure_advance: False
#   如果为真，则在处理移动时使用 trapq 中的压力提前常数。
#   这会导致压力提前的更改立即被考虑，对于当前队列中的所有移动，
#   而不是在队列刷新后的约 250ms 后。
#
#   如果：control: dual_loop_pid
#inner_sensor_name:
#   第二个传感器的 temperature_sensor 名称，用于 dual_loop_pid 进行温度控制。
#   此传感器将限制加热器功率，以不允许温度超过"inner_max_temp"值。
#
#   如果：control: dual_loop_pid
#inner_max_temp:
#   内传感器将允许的最大温度目标。
#
#   如果 control: dual_loop_pid
#inner_pid_Kp:
#inner_pid_Ki:
#inner_pid_Kd:
#   "dual_loop_pid"控制使用两个 PID 循环来控制温度。内（次要）PID 循环
#   直接控制温度。主 PID 循环控制次 PID 循环的功率。这允许主 PID 循环针对
#   温度控制进行调整，而次 PID 循环可以针对功率控制进行调整，不超过在
#   "inner_max_temp"上设置的温度限制。
#   主传感器位置靠近温度测量应更准确的地方（例如床面）。
#   次传感器位置靠近温度测量不应超过限制的地方（例如硅加热器上）。
\\\

### [heater_bed]

heater_bed 部分描述加热的床。它使用"extruder"部分中描述的相同加热器设置。

\\\
[heater_bed]
heater_pin:
sensor_type:
sensor_pin:
control:
min_temp:
max_temp:
#   参见"extruder"部分以获取对上述参数的描述。
\\\

### [pid_profile]

Pid 配置文件指定可在运行时加载的一组 PID 值。

\\\
[pid_profile <heater> <profile-name>]
pid_version: 1
# 这定义了保存时的版本，对兼容性检查很重要，保持在 1！
pid_target:
# 仅供参考，指定配置文件标定的温度。
# 如果创建自定义配置文件，请输入配置文件的预期使用温度或将其留空。
pid_tolerance:
# 自动标定配置文件时使用的容差。如果定义自定义配置文件，请将其留空。
control: <pid|pid_v>
# 必须是 pid 或 pid_v。
# 必须提供此参数。
pid_kp:
# PID 控制的 P 值。
# 必须提供此参数。
pid_ki:
# PID 控制的 I 值。
# 必须提供此参数。
pid_kd:
# PID 控制的 D 值。
# 必须提供此参数。
\\\

有关详细信息，请阅读 docs/PID.md

### ⚠️ [hc595]

74HC595 移位寄存器输出扩展（可以使用"hc595"前缀定义任意数量的部分）。74HC595 是一个串行到并行移位寄存器，仅使用 3 个 MCU 引脚（数据、时钟、锁存）提供 8 个额外的数字输出引脚。多个芯片可以菊花链式连接以获得最多 32 个输出。HC595 输出可在任何接受标准数字输出引脚的位置使用，方法是将其引用为 \chip_name:N\，其中 N 是输出编号（0 到 chain_count*8 - 1）。chip_name 是配置部分标题中给定的名称。

\\\
[hc595 my_shift]
data_pin:
#   连接到 74HC595 SER（串行数据输入）线的引脚，
#   通常是 IC 上的 14 引脚。必须提供此参数。
clock_pin:
#   连接到 74HC595 SRCLK（移位寄存器时钟）线的引脚，
#   通常是 IC 上的 11 引脚。必须提供此参数。
latch_pin:
#   连接到 74HC595 RCLK（存储寄存器时钟/锁存）线的引脚，
#   通常是 IC 上的 12 引脚。必须提供此参数。
#oe_pin:
#   可选引脚连接到 74HC595 OE（输出启用）线，
#   通常是 IC 上的 13 引脚。此引脚处于低电平。如果未
#   指定，OE 引脚应接地以永久启用输出。
#chain_count: 1
#   菊花链式 74HC595 芯片的数量。必须在 1 到 4 之间。
#   每个芯片添加 8 个额外的输出引脚。默认值为 1。
\\\

#### HC595 接线

对于单个 74HC595，连接：
- 74HC595 14 引脚 (SER) 到 MCU 引脚由 \data_pin\ 指定
- 74HC595 11 引脚 (SRCLK) 到 MCU 引脚由 \clock_pin\ 指定
- 74HC595 12 引脚 (RCLK) 到 MCU 引脚由 \latch_pin\ 指定
- 74HC595 13 引脚 (OE) 到地（或到 MCU 引脚由 \oe_pin\ 指定）
- 74HC595 10 引脚 (SRCLR) 到 VCC
- 74HC595 8 引脚 (GND) 到地
- 74HC595 16 引脚 (VCC) 到 +3.3V 或 +5V
- 74HC595 输出引脚为 QA-QH（15、1-7 引脚）

对于菊花链式，将第一个芯片的 Q7'（9 引脚）连接到下一个芯片的 SER（14 引脚）。
所有芯片共享相同的 CLOCK、LATCH 和 OE 线。

#### HC595 使用示例

\\\
[hc595 my_shift]
data_pin: PA1
clock_pin: PA2
latch_pin: PA3

# 使用 HC595 输出 0 控制风扇
[fan]
pin: my_shift:0

# 使用 HC595 输出 3 控制加热器
[heater_generic chamber_heater]
heater_pin: my_shift:3
max_power: 1.0
# ... 其他加热器参数

# 使用 HC595 输出 7 作为通用输出引脚
[output_pin my_output]
pin: my_shift:7
value: 0
shutdown_value: 0
\\\

提供以下扩展 G 代码命令：

- \SET_HC595 CHIP=<config_name> [BITS=<value>]\：同时设置或查询所有
  HC595 输出引脚。不带 BITS，报告当前引脚状态。
  使用 BITS，将给定的整数值应用于所有输出（位 0 = 输出 0 等）。


### [stepper_z1]

在一个"可升级的加热床"上添加额外的步进电机。（参见运动学文档。）

此部分支持stepper部分中描述的所有参数。

### [stepper_z2]

在一个"可升级的加热床"上添加额外的步进电机。此部分支持stepper部分中描述的所有参数。

### [stepper_z3]

在一个"可升级的加热床"上添加额外的步进电机。此部分支持stepper部分中描述的所有参数。

### [extruder1]

在多挤出机打印机中添加额外的挤出机。此部分支持extruder部分中描述的所有参数。

### [dual_carriage]

使用"可升级运动学"支持"双托架"打印机。

\\\
[dual_carriage]
axis:
#   此对偶托架使用的轴(x或y)。必须提供此参数。
\\\

### [extruder_stepper]

支持使用"分步式外挤出机"的打印机(一个步进电动机在工具头上，一个或多个步进电动机在打印机机构本身)。

\\\
[extruder_stepper my_stepper]
extruder:
#   此步进器对应的挤出机的名称。如果未指定，则不进行自动
#   挤出机同步。可以使用一个虚拟名称"分享"来同步所有定义
#   的挤出机(注意：这个虚拟名称在工具头情况下不能使用)。
step_pin:
dir_pin:
enable_pin:
#   参见"stepper"部分以获取对这些参数的描述。
microsteps:
rotation_distance:
#   参见"stepper"部分以获取对这些参数的描述。如果在此处指定
#   rotation_distance，则此步进器的旋转距离将在SYNC_EXTRUDER_MOTION
#   命令期间用于覆盖挤出机的rotation_distance。
\\\

### [manual_stepper]

手动步进电机（此部分可使用任意标识符定义多次）。

\\\
[manual_stepper my_stepper]
step_pin:
dir_pin:
enable_pin:
#   参见"stepper"部分以获取对这些参数的描述。必须提供
#   step_pin、enable_pin或dir_pin。
velocity:
#   通过MANUAL_STEPPER命令移动时使用的默认速度(mm/s或 mm/s²)。
#   默认值为5。
accel:
#   通过MANUAL_STEPPER命令移动时使用的默认加速度
#   (mm/s² 或 mm/s³)。值0表示无加速。默认值为0。
#microsteps:
#rotation_distance:
#   参见"stepper"部分以获取对这些参数的描述。
\\\

### [verify_heater]

验证加热器配置。如果加热器未能在指定的时间段内达到指定的温度，将生成错误消息。

\\\
[verify_heater extruder]
#max_error: 120
#   如果加热器无法在指定的秒数内从当前温度内达到目标温度，
#   如果回到温度增长小于此值，生成错误。默认值为120秒。
#check_gain_time:
#   如果加热器没有在指定秒数内增加（"check_gain_time" / "max_error"）
#   摄氏度以上，生成一个错误。默认值为20秒。
#hysteresis: 5
#   在超温冷却启用时，冷却程度的范围（摄氏度）。当加热器在
#   超温冷却过程中达到目标温度时（目标温度 - hysteresis），
#   加热器被置于待命状态，直到达到新的目标温度。
#   默认值为5。
\\\

### [homing_heaters]

该工具在G28运动期间禁用加热器。

\\\
[homing_heaters]
#steppers: extruder, stepper_z
#   在归位运动时要禁用其加热器的步进器的逗号分隔列表。
#   默认行为是在所有Z轴归位运动期间禁用挤出机加热器。
#   注意：如果启用了双托架、双升降或多个上升轴，则可能需要
#   配置此选项。
\\\

### [thermistor]

热敏电阻（此部分可使用任意标识符定义多次）。

\\\
[thermistor my_thermistor]
temperature1:
resistance1:
temperature2:
resistance2:
temperature3:
resistance3:
#   三个温度/电阻点。它们应该跨越所考虑的温度范围。如果
#   挤出机温度是通过这些点进行外推而计算的，则这三个参数
#   都是必需的。注意：这些参数本身取代了任何"Steinhart-Hart
#   系数"参数。
\\\

### [adc_temperature]

ADC温度传感器（此部分可使用任意标识符定义多次）。

\\\
[adc_temperature my_adc_temperature]
sensor_pin:
#   连接到温度传感器的ADC引脚。此参数必须提供。
#pullup_resistor: 4700
#   连接到温度计的上拉电阻的电阻(欧姆)。
#   默认值为4700欧姆。
\\\

### [temperature_sensor]

通用温度传感器（此部分可使用任意标识符定义多次）。

\\\
[temperature_sensor my_sensor]
sensor_type:
#   温度传感器的类型。支持的类型有："EPCOS 100K B57560G104F"、
#   "PT1000"、"PT100"、"ADS1220"、"ADS131M02"、"ADS131M04"。
#   必须提供此参数。
sensor_pin:
#   连接到温度传感器的ADC引脚或IIC地址。如果温度传感器是DS18B20（one-wire）、
#   PT100 (RTD)、PT1000 (RTD)、则需要MCU引脚名称。对于ADS等外部传感器，
#   则需要IIC地址。必须提供此参数。
#min_temp: -40
#   最小温度。如果温度低于此值，将自动关闭打印机。
#   默认值为-40摄氏度。
#max_temp: 85
#   最大温度。如果温度超过此值，将自动关闭打印机。
#   默认值为85摄氏度。
#gcode_id:
#   OctoPrint在报告温度时使用的gcode_id。
\\\

### [heater_generic]

通用加热器配置（此部分可使用任意标识符定义多次）。

\\\
[heater_generic my_heater]
heater_pin:
max_power:
sensor_type:
sensor_pin:
control:
min_temp:
max_temp:
#   参见"extruder"部分以获取对这些参数的描述。
#gcode_id:
#   OctoPrint在报告温度时使用的gcode_id。
\\\

### [fan]

打印风扇。

\\\
[fan]
pin:
#   控制风扇的PWM输出引脚。必须提供此参数。
#max_power: 1.0
#   可将引脚设置为的最大功率(表示为0.0到1.0的值)。
#   1.0的值允许在长时间内将引脚设置为完全启用，而0.5的值
#   最多允许在一半的时间内启用该引脚。此设置可用于限制总功率
#   输出(在扩展时间内)到风扇。默认值为1.0。
#shutdown_speed: 0
#   风扇在微控制器关闭时应设置的所需速度(表示为0.0到1.0之间的值)。
#   默认值为0。
#cycle_time: 0.010
#   每个PWM周期的时间(秒)。除非有电气要求以每秒超过10次的速率
#   切换输出，否则不建议设置此值。默认值为0.010秒。
#hardware_pwm: False
#   使用硬件PWM而不是软件PWM。使用硬件PWM通常可以达到更高的脉冲
#   宽度调制频率，但是会有一些限制——某些脚位置之间的引脚可能无法
#   实现独立的硬件PWM。默认值为False。
#kick_start_time: 0.100
#   当启用风扇时，必须以最大功率打开的最短时间(以秒为单位)。
#   这仅适用于无法通过低功率设置检测到风扇旋转的情况。
#   默认值为0.100秒。
#off_below: 0.0
#   最小输入速度，可使用PWM控制打开风扇。如果下面指定的速度
#   更低，则风扇将处于关闭状态。默认值为0.0。
\\\

### [heater_fan]

加热器冷却风扇(风扇将在指定时间内与加热器一同打开和关闭)。

\\\
[heater_fan my_heater_fan]
pin:
max_power:
shutdown_speed:
cycle_time:
hardware_pwm:
kick_start_time:
off_below:
#   参见"fan"部分以获取对这些参数的描述。
heater: extruder
#   关联此风扇的加热器的配置部分名称。
#   如果加热器被启用，则此风扇会被启用。
#   必须提供此参数。
#heater_temp: 50.0
#   加热器必须超过的温度以启用此风扇。
#   默认值为50摄氏度。
#fan_speed: 1.0
#   启用此风扇时的PWM速度(表示为0.0到1.0之间的值)。
#   默认值为1.0。
\\\

### [controller_fan]

控制器冷却风扇(一个向微控制器或其他电子设备供冷的风扇)。

\\\
[controller_fan my_controller_fan]
pin:
max_power:
shutdown_speed:
cycle_time:
hardware_pwm:
kick_start_time:
off_below:
#   参见"fan"部分以获取对这些参数的描述。
#fan_speed: 1.0
#   启用此风扇时的PWM速度(表示为0.0到1.0之间的值)。
#   默认值为1.0。
#idle_timeout: 30
#   如果打印机没有进行任何运动或加热/冷却活动时间超过
#   idle_timeout秒数，风扇将被禁用。
#   默认值为30秒。
#idle_speed: 0.0
#   在idle_timeout秒后要设置风扇的PWM速度。
#   默认值为0.0。
\\\

### [temperature_fan]

温度激活的风扇。

\\\
[temperature_fan my_temp_fan]
pin:
max_power:
shutdown_speed:
cycle_time:
hardware_pwm:
kick_start_time:
off_below:
#   参见"fan"部分以获取对这些参数的描述。
sensor_type:
sensor_pin:
control:
min_temp:
max_temp:
#   参见"extruder"部分以获取对这些参数的描述。
#target_temp: 40.0
#   目标温度。此参数必须提供。
#max_speed: 1.0
#   当传感器温度超过目标温度的最大风扇速度(表示为0.0到1.0之间的值)。
#   默认值为1.0。
#min_speed: 0.3
#   最小风扇速度(表示为0.0到1.0之间的值)当传感器温度高于目标温度时。
#   默认值为0.3。
#hysteresis: 2.0
#   当传感器温度减少到目标温度下方hysteresis摄氏度时，
#   风扇的速度将减少。默认值为2摄氏度。
\\\

### [fan_generic]

通用定速度风扇(此部分可使用任意标识符定义多次)。

\\\
[fan_generic extruder_cooling_fan]
pin:
max_power:
shutdown_speed:
cycle_time:
hardware_pwm:
kick_start_time:
off_below:
#   参见"fan"部分以获取对这些参数的描述。
\\\

### [led]

LED支持（此部分可使用任意标识符定义多次）。

\\\
[led my_led]
pin:
#   控制LED的PWM输出引脚。必须提供此参数。
#   此引脚必须使用"PWM"功能进行配置(不是"数字输出")。
#red_pin:
#green_pin:
#blue_pin:
#white_pin:
#   对于RGB或RGBW LED，红色、绿色、蓝色、白色输出的PWM引脚。
#   至少要指定red_pin或pin中的一个。
#cycle_time: 0.010
#   每个PWM周期的时间(秒)。默认值为0.010秒。
#hardware_pwm: False
#   使用硬件PWM而不是软件PWM。硬件PWM通常可以达到
#   更高的脉冲宽度调制频率，因此可以获得更平滑的尺寸变化。
#   默认值为False。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   LED的初始LED状态。每个值应该在0.0到1.0之间。
#   默认值为0。
\\\

### [neopixel]

Neopixel (WS2812) LED支持（此部分可使用任意标识符定义多次）。

\\\
[neopixel my_neopixel]
pin:
#   连接到neopixel数据线的输出引脚。此参数必须提供。
chain_count:
#   chained neopixels的数目。默认值为1(只有一个led)。
#color_order: GRB
#   设置pixel颜色顺序。可以是RGB、GRB或RGBW。默认值为GRB。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   初始LED状态。每个值应该在0.0到1.0之间。默认值为0。
\\\

### [output_pin]

输出引脚（此部分可使用任意标识符定义多次）。

\\\
[output_pin my_pin]
pin:
#   要输出到的MCU引脚。此参数必须提供。
#pwm: False
#   如果输出引脚应该能够PWM。如果为False，则输出引脚
#   应该使用数字输出。如果未指定，则使用PWM。
#value: 0.0
#   引脚应该输出到的初始值。如果pwm为True，则应该在0.0
#   到1.0之间，否则应该为0或1。默认值为0。
#shutdown_value: 0
#   当微控制器关闭时，引脚应该设置到的值。
#   如果pwm为True，则应该在0.0到1.0之间，否则应该为0或1。
#   默认值为0。
#maximum_mcu_duration: 0
#   最长时间长期驱动输出脉冲的最大时间长度。
#   如果不是0，MCU将周期性停止驱动该线并等待主机重新启用该输出。
#   这对于驱动可能在意外MCU硬件故障后无限期致动的设备（如继电器）很有用。
#   默认值为0(禁用)。
#cycle_time: 0.100
#   每个PWM周期的时间(秒)。如果pwm为True，此值应该在0.004到3600之间。
#   默认值为0.100秒。
#hardware_pwm: False
#   使用硬件PWM而不是软件PWM。使用硬件PWM通常可以达到更高的脉冲
#   宽度调制频率，但仍然受到MCU能力的限制。
#   默认值为False。
\\\

### [servo]

伺服（此部分可使用任意标识符定义多次）。

\\\
[servo my_servo]
pin:
#   控制伺服的PWM输出引脚。必须提供此参数。
#maximum_servo_angle: 180
#   伺服可以命令到的最大角度。
#   默认值为180。
#minimum_pulse_width: 0.001
#   最小脉冲宽度时间(秒)。
#   对应于0度角。默认值为0.001秒。
#maximum_pulse_width: 0.002
#   最大脉冲宽度时间(秒)。对应于maximum_servo_angle。
#   默认值为0.002秒。
\\\

### [static_digital_output]

静态数字输出（此部分可使用任意标识符定义多次）。

\\\
[static_digital_output my_output]
pins:
#   输出引脚列表(使用逗号分隔)。至少必须提供一个输出引脚。
#   此参数必须提供。
#value: 0
#   要输出到引脚的初始值。0为低(0V)，1为高(+3.3V)。
#   默认值为0。
\\\

### [multi_pin]

多引脚输出（此部分可使用任意标识符定义多次）。

\\\
[multi_pin my_multi_pin]
pins:
#   逗号分隔的引脚列表。至少必须提供两个引脚。
#   此参数必须提供。
\\\

完成日期：2024年
