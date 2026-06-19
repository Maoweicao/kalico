# 配置参考

本文档是 Kalico 配置文件中可用选项的参考。

带有 ⚠️ 标记的章节和选项表示与原版 Klipper 相比有更改的配置。

本文档中的描述格式化为可以直接剪切粘贴到打印机配置文件中。请参阅
[安装文档](Installation.md) 获取设置 Kalico 和选择初始配置文件的信息。

## 微控制器配置

### 微控制器引脚名称格式

许多配置选项需要微控制器引脚的名称。
Kalico 使用这些引脚的硬件名称 - 例如 `PA4`。

引脚名称前面可以加 `!` 来表示应使用反向极性
（例如，在低电平而不是高电平时触发）。

输入引脚前面可以加 `^` 来表示应为该引脚启用硬件上拉电阻。如果微控制器
支持下拉电阻，则输入引脚也可以用 `~` 作为前缀。

请注意，某些配置部分可能会"创建"额外的引脚。在这种情况下，
定义引脚的配置部分必须在使用这些引脚的任何部分之前列在配置文件中。

### [mcu]

主微控制器的配置。

```
[mcu]
serial:
#   要连接到 MCU 的串口。如果不确定（或者如果它
#   会改变），请参阅常见问题解答中的"我的串口在哪里？"部分。
#   使用串口时必须提供此参数。
#baud: 250000
#   要使用的波特率。默认值为 250000。
#canbus_uuid:
#   如果使用连接到 CAN 总线的设备，则此设置用于连接的唯一
#   芯片标识符。使用 CAN 总线进行通信时必须提供此值。
#canbus_interface:
#   如果使用连接到 CAN 总线的设备，则此设置要使用的 CAN
#   网络接口。默认值为 'can0'。
#restart_method:
#   这控制主机用于重置微控制器的机制。选择包括 'arduino'、'cheetah'、'rpi_usb'
#   和 'command'。'arduino' 方法（切换 DTR）在 Arduino 板和克隆板上很常见。'cheetah'
#   方法是某些 Fysetc Cheetah 板所需的特殊方法。'rpi_usb' 方法在通过 USB 供电的
#   Raspberry Pi 板上的微控制器上很有用 - 它会短暂禁用所有 USB 端口的电源以
#   完成微控制器重置。'command' 方法涉及向微控制器发送 Kalico 命令，以便它可以
#   自行重置。如果微控制器通过串口通信，默认值为 'arduino'，否则为 'command'。
#is_non_critical: False
#   将此设置为 True 将允许 MCU 随意断开连接和重新连接而不产生错误。对于 USB 加速度计板
#   和 USB/CAN 探针很有帮助
```

### [mcu my_extra_mcu]

额外的微控制器（可以定义任意数量带有 "mcu" 前缀的部分）。
额外的微控制器引入的引脚可以配置为加热器、步进电机、风扇等。
例如，如果引入了 "[mcu extra_mcu]" 部分，则可以在配置的其他地方使用
"extra_mcu:ar9" 等引脚（其中 "ar9" 是给定 mcu 上的硬件引脚名称或别名）。

```
[mcu my_extra_mcu]
# 请参阅 "mcu" 部分了解配置参数。
```

## ⚠️ 危险选项

Kalico 特定系统选项的集合

```
[danger_options]
#error_on_unused_config_options: True
#   如果未使用的配置选项或部分是否应导致错误
#   如果为 False，将发出警告但允许 Kalico 继续运行。
#   默认值为 True。
#allow_plugin_override: False
#   允许 `plugins` 中的模块覆盖 `extras` 中同名模块
#   默认值为 False。
#single_mcu_trsync_timeout: 0.25
#   在使用单个 MCU 时，归位过程中 MCU 同步的超时时间（秒）。
#   默认值为 0.25
#multi_mcu_trsync_timeout: 0.025
#   在使用多个 MCU 时，归位过程中 MCU 同步的超时时间（秒）。
#   默认值为 0.025
#homing_elapsed_distance_tolerance: 0.5
#   第二次归位时移动距离的容差（毫米）。确保在使用无传感器归位时，
#   第二次归位距离与 `min_home_dist` 紧密匹配。默认值为 0.5mm。
#temp_ignore_limits: False
#   设置为 true 时，此参数忽略温度传感器的 min_value 和 max_value
#   限制。它通过允许超出指定范围的读数而不触发关闭来防止因
#   'ADC out of range' 和类似错误导致的关闭。默认值为 False。
#autosave_includes: False
#   设置为 true 时，SAVE_CONFIG 将递归读取 [include ...] 块以检查自动保存数据的
#   冲突。任何更新的配置将备份到 configs/config_backups。
#bgflush_extra_time: 0.250
#   这允许设置额外的刷新时间（秒）。在某些条件下，
#   如果消息未被刷新，较低的值将导致错误，较高的值
#   （0.250）将导致归位/探测延迟。默认值为 0.250
#homing_start_delay: 0.001
#   在开始用于归位的滴灌移动之前停留的时间
#endstop_sample_time: 0.000015
#   MCU 应采样限位开关状态的频率
#endstop_sample_count: 4
#   归位时应检查限位开关状态的次数
#   除非您的限位开关有噪声且不可靠，否则应能将此值降低到 1

# 挤出机安全限制覆盖：
#override_pressure_advance_smooth_time_max: 0.200
#   覆盖 pressure_advance_smooth_time 的最大值（配置和
#   SET_PRESSURE_ADVANCE）。对于需要超出内置默认值的非标准设置很有用。
#   默认值为 0.200。

# 日志选项：

#minimal_logging: False
#   设置所有日志选项的默认值。默认值为 False。
#log_statistics: True
#   是否应记录统计信息
#   （有助于在开发期间保持日志整洁）
#   默认值为 True。
#log_config_file_at_startup: True
#   启动时是否应记录配置文件
#   默认值为 True。
#log_bed_mesh_at_startup: True
#   启动时是否应记录热床网格
#   （有助于在开发期间保持日志整洁）
#   默认值为 True。
#log_velocity_limit_changes: True
#   是否应记录速度限制的更改。如果为 False，速度限制将仅在滚动时记录。
#   某些切片器会发出非常频繁的 SET_VELOCITY_LIMIT 命令
#   默认值为 True
#log_pressure_advance_changes: True
#   是否应记录压力推进的更改。如果为 false，压力推进数据
#   将仅在滚动时记录。
#   默认值为 True。
#log_shutdown_info: True
#   是否应在发生异常时记录详细的崩溃信息
#   大部分内容过于冗长和无用，我们仍然会获得正常异常的堆栈跟踪，
#   因此设置为 False 可以帮助在开发时节省时间
#   默认值为 True。
#log_serial_reader_warnings: True
#log_startup_info: True
#log_webhook_method_register_messages: False
#log_component_interactions: False
#   设置为 True 时，在 DEBUG 级别启用所有硬件组件交互（加热器 PWM/温度、
#   工具头移动、步进电机方向/位置/归位、MCU 命令等）的详细调试日志记录。
#   与 -v CLI 标志或 log_module_categories 一起使用以获得增强的诊断功能。
#   默认值为 False。
#log_module_categories: False
#   设置为 True 时，在主日志文件所在目录中创建单独的每模块日志文件
#   （module_heaters.log、module_toolhead.log、module_stepper.log、
#   module_mcu.log 等）。
#   每个文件仅包含其各自模块的日志条目。
#   默认值为 False。
```

## ⚠️ 配置引用

在您的配置中，您可以引用其他值以在多个部分之间共享配置。引用采用
`${option}` 的形式来复制当前部分中的值，或 `${section.option}` 来在配置中的其他位置查找值。请注意，常量必须始终为小写。

可以选择使用 `[constants]` 部分专门存储这些值。未使用的常量将显示警告。
但是，如果未使用任何常量，`[constants]` 将显示错误。

```
[constants]
run_current_ab:  1.0
i_am_not_used: True  # Will show "Constant 'i_am_not_used' is unused"

[tmc5160 stepper_x]
run_current: ${constants.run_current_ab}

[tmc5160 stepper_y]
run_current: ${tmc5160 stepper_x.run_current}
#   嵌套引用有效，但不建议使用
```

如果需要，可以使用 `\${such}` 来转义引用

## 通用运动学设置

### [printer]

打印机部分控制高级打印机设置。

```
[printer]
kinematics:
#   所使用的打印机类型。此选项可以是以下之一：cartesian、
#   corexy、corexz、hybrid_corexy、hybrid_corexz、rotary_delta、delta、
#   deltesian、polar、winch 或 none。必须指定此参数。
max_velocity:
#   工具头相对于打印的最大速度（mm/s）。
#   此值可以在运行时使用 SET_VELOCITY_LIMIT 命令更改。
#   必须指定此参数。
max_accel:
#   工具头相对于打印的最大加速度（mm/s^2）。虽然此参数被描述为"最大"
#   加速度，但在实践中，大多数加速或减速的移动将以此处指定的速率进行。
#   此处指定的值可以在运行时使用 SET_VELOCITY_LIMIT 命令更改。
#   必须指定此参数。
#minimum_cruise_ratio: 0.5
#   大多数移动将加速到巡航速度，以该巡航速度行驶，然后减速。但是，
#   一些短距离移动名义上可能加速然后立即减速。此选项降低这些移动的最高速度，
#   以确保始终在巡航速度下行驶最小距离。即，它强制要求相对于总行驶距离，
#   在巡航速度下行驶的最小距离。旨在减少短锯齿形移动的最高速度（从而
#   减少这些移动引起的打印机振动）。例如，minimum_cruise_ratio 为 0.5 将
#   确保单独的 1.5mm 移动在巡航速度下的最小距离为 0.75mm。指定 0.0 的比率
#   可禁用此功能（在加速和减速之间不会强制执行最小巡航距离）。
#   此处指定的值可以在运行时使用 SET_VELOCITY_LIMIT 命令更改。
#   默认值为 0.5。
#square_corner_velocity: 5.0
#   工具头可以 90 度角行驶的最大速度（mm/s）。非零值可以通过在转弯时
#   启用工具头的瞬时速度变化来减少挤出机流量的变化。此值配置内部向心速度
#   转弯算法；角度大于 90 度的角将具有更高的转弯速度，而角度小于 90 度的角
#   将具有较低的转弯速度。如果设置为零，工具头将在每个角落减速到零。
#   此处指定的值可以在运行时使用 SET_VELOCITY_LIMIT 命令更改。
#   默认值为 5mm/s。
#max_accel_to_decel:
#   此参数已弃用，不应再使用。
```

### [stepper]

步进电机定义。不同的打印机类型（由 [printer] 配置部分中的 "kinematics" 选项指定）需要不同的步进电机名称（例如，`stepper_x` 与 `stepper_a`）。以下是常见的步进电机定义。

请参阅 [旋转距离文档](Rotation_Distance.md) 了解计算 `rotation_distance` 参数的信息。请参阅 [多 MCU 归位](Multi_MCU_Homing.md) 文档了解使用多个微控制器进行归位的信息。

```
[stepper_x]
step_pin:
#   步进 GPIO 引脚（高电平触发）。必须提供此参数。
dir_pin:
#   方向 GPIO 引脚（高电平表示正方向）。必须提供此参数。
enable_pin:
#   使能引脚（默认为高电平使能；使用 ! 表示低电平使能）。
#   如果未提供此参数，则步进电机驱动器必须始终处于使能状态。
rotation_distance:
#   步进电机（或指定 gear_ratio 时的最终齿轮）旋转一整圈时
#   轴移动的距离（mm）。必须提供此参数。
microsteps:
#   步进电机驱动器使用的微步数。必须提供此参数。
#full_steps_per_rotation: 200
#   步进电机旋转一整圈的全步数。对于 1.8 度步进电机设置为 200，
#   对于 0.9 度电机设置为 400。默认值为 200。
#gear_ratio:
#   如果步进电机通过齿轮箱连接到轴，则齿轮比。例如，如果使用 5 比 1 的
#   齿轮箱，可以指定 "5:1"。如果轴有多个齿轮箱，可以指定以逗号分隔的
#   齿轮比列表（例如 "57:11, 2:1"）。如果指定了 gear_ratio，则
#   rotation_distance 指定最终齿轮旋转一整圈时轴移动的距离。
#   默认值为不使用齿轮比。
#step_pulse_duration:
#   步进脉冲信号边沿与后续"取消步进"信号边沿之间的最小时间。这也用于
#   设置步进脉冲与方向变化信号之间的最小时间。对于以 UART 或 SPI 模式
#   配置的 TMC 步进电机，默认值为 0.000000100（100ns），对于所有其他步进电机，
#   默认值为 0.000002（即 2us）。
endstop_pin:
#   限位开关检测引脚。如果此限位引脚与步进电机不在同一 MCU 上，
#   则启用"多 MCU 归位"。对于笛卡尔式打印机的 X、Y 和 Z
#   步进电机必须提供此参数。
#position_min: 0
#   用户可以命令步进电机移动到的最小有效距离（mm）。默认值为 0mm。
position_endstop:
#   限位开关的位置（mm）。对于笛卡尔式打印机的 X、Y 和 Z
#   步进电机必须提供此参数。
position_max:
#   用户可以命令步进电机移动到的最大有效距离（mm）。对于笛卡尔式打印机的
#   X、Y 和 Z 步进电机必须提供此参数。
#homing_speed: 5.0
#   归位时步进电机的最大速度（mm/s）。默认值为 5mm/s。
#homing_accel:
#   归位时步进电机的最大加速度（mm/s）。默认值为使用 [printer] 对象中配置的最大加速度。
#homing_retract_dist: 5.0
#   归位期间第二次归位前的回退距离（mm）。如果 `use_sensorless_homing` 为 false，
#   可以将此设置设置为零以禁用第二次归位。如果 `use_sensorless_homing`
#   为 true，此设置可以 > 0 以在归位后回退。默认值为 5mm。
#homing_retract_speed:
#   归位后回退移动使用的速度，如果与归位速度不同，则使用此值（默认值即为归位速度）
#min_home_dist:
#   无传感器归位前工具头的最小距离（mm）。如果距离限位开关比
#   `min_home_dist` 更近，则移动到此距离，然后归位。
#   如果更远，则直接归位并回退到 `homing_retract_dist`。
#   默认值等于 `homing_retract_dist`。
#second_homing_speed:
#   执行第二次归位时步进电机的速度（mm/s）。
#   默认值为 homing_speed/2。如果 `use_sensorless_homing`
#   为 true，则默认值为 homing_speed。
#homing_positive_dir:
#   如果为 true，归位将使步进电机向正方向移动（远离零点）；如果为 false，
#   向零点归位。使用默认值比指定此参数更好。如果 position_endstop 接近
#   position_max，则默认值为 true；如果接近 position_min，则为 false。
#use_sensorless_homing:
#   如果为 true，当 homing_retract_dist > 0 时禁用第二次归位操作。
#   如果 endstop_pin 配置为使用 virtual_endstop，则默认值为 true
```

### 笛卡尔运动学

请参阅 [example-cartesian.cfg](../config/example-cartesian.cfg) 了解笛卡尔运动学配置文件示例。

此处仅描述笛卡尔打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: cartesian
max_z_velocity:
#   这设置沿 Z 轴运动的最大速度（mm/s）。此设置可用于限制 Z 步进电机的
#   最大速度。默认值为将 max_velocity 用于 max_z_velocity。
max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。它限制 Z 步进电机的加速度。
#   默认值为将 max_accel 用于 max_z_accel。

# stepper_x 部分用于描述笛卡尔机器人中控制 X 轴的步进电机。
[stepper_x]

# stepper_y 部分用于描述笛卡尔机器人中控制 Y 轴的步进电机。
[stepper_y]

# stepper_z 部分用于描述笛卡尔机器人中控制 Z 轴的步进电机。
[stepper_z]
```

### ⚠️ 带有 X 和 Y 轴限制的笛卡尔运动学

行为与笛卡尔运动学完全相同，但允许为 X 和 Y 轴设置速度和加速度限制。这还使得命令 [`SET_KINEMATICS_LIMIT`](./G-Codes.md#set_kinematics_limit) 可用于在运行时设置这些限制。


```
[printer]
kinematics: limited_cartesian
max_x_velocity:
#   这设置沿 X 轴运动的最大速度（mm/s）。此设置可用于限制 X 步进电机的
#   最大速度。默认值为将 max_velocity 用于 max_x_velocity。
max_y_velocity:
#   这设置沿 Y 轴运动的最大速度（mm/s）。此设置可用于限制 Y 步进电机的
#   最大速度。默认值为将 max_velocity 用于 max_x_velocity。
max_z_velocity:
#   请参阅上方的笛卡尔设置。
max_velocity:
#   为了在对角线上获得最大速度增益，此值应等于或大于
#   max_x_velocity 和 max_y_velocity 的斜边（sqrt(x*x + y*y)）。
max_x_accel:
#   这设置沿 X 轴运动的最大加速度（mm/s^2）。它限制 X 步进电机的加速度。
#   默认值为将 max_accel 用于 max_x_accel。
max_y_accel:
#   这设置沿 Y 轴运动的最大加速度（mm/s^2）。它限制 Y 步进电机的加速度。
#   默认值为将 max_accel 用于 max_y_accel。
max_z_accel:
# 请参阅上方的笛卡尔设置。
max_accel:
# 请参阅上方的笛卡尔设置。
scale_xy_accel: False
#   为 true 时，按当前工具头加速度缩放 XY 限制。
#   因子为：切片器加速度 / sqrt(max_x_accel^2 + max_y_accel^2)。
#   请参阅下文。
```

如果 scale_xy_accel 为 `False`，由 `max_accel`、M204 或 SET_VELOCITY_LIMIT 设置的加速度将作为第三个限制。在这种情况下，此模块不会对加速度低于 `max_x_accel` 和 `max_y_accel` 的移动施加限制。当 scale_xy_accel 为 `True` 时，`max_x_accel` 和 `max_y_accel` 将按动态设置的加速度与 max_x_accel 和 `max_y_accel` 斜边的比率进行缩放，如 `SET_KINEMATICS_LIMIT` 所报告。这意味着实际加速度将始终取决于方向。例如，以下设置：

```
[printer]
max_x_accel: 12000
max_y_accel: 9000
scale_xy_accel: true
```

`SET_KINEMATICS_LIMIT` 将报告 37 度对角线上的最大加速度为 15000 mm/s^2。如果切片器发出 `M204 S3000`（3000 mm/s^2 加速度）。在这些 37 度和 143 度对角线上，工具头将以 3000 mm/s^2 加速。在 X 轴上，加速度将为 12000 * 3000 / 15000 = 2400 mm/s^2，纯 Y 移动为 18000 mm/s^2。

### 线性 Delta 运动学

请参阅 [example-delta.cfg](../config/example-delta.cfg) 了解线性 delta 运动学配置文件示例。请参阅 [delta 校准指南](Delta_Calibrate.md) 了解校准信息。

此处仅描述线性 delta 打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: delta
max_z_velocity:
#   对于 delta 打印机，这限制了包含 Z 轴运动的移动的最大速度（mm/s）。
#   此设置可用于降低上下移动的最大速度（在 delta 打印机上，这些移动需要
#   比其他移动更高的步进速率）。默认值为将 max_velocity 用于 max_z_velocity。
#max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。如果打印机在 XY 移动上能达到
#   比 Z 移动更高的加速度（例如，使用输入整形器时），设置此值可能很有用。
#   默认值为将 max_accel 用于 max_z_accel。
#minimum_z_position: 0
#   用户可以命令打印头移动到的最小 Z 位置。默认值为 0。
delta_radius:
#   三个线性轴塔形成的水平圆的半径（mm）。此参数也可以计算为：
#    delta_radius = smooth_rod_offset - effector_offset - carriage_offset
#   必须提供此参数。
#print_radius:
#   有效工具头 XY 坐标的半径（mm）。可以使用此设置来自定义工具头移动的
#   范围检查。如果在此处指定较大的值，则可能将工具头命令到与塔碰撞的位置。
#   默认值为将 delta_radius 用于 print_radius（通常可以防止塔碰撞）。

# stepper_a 部分描述控制前左塔（210 度）的步进电机。此部分还控制
# 所有塔的归位参数（homing_speed、homing_retract_dist）。
[stepper_a]
position_endstop:
#   当喷嘴位于构建区域中心且限位开关触发时，喷嘴与热床之间的距离（mm）。
#   此参数必须为 stepper_a 提供；对于 stepper_b 和 stepper_c，
#   此参数默认为为 stepper_a 指定的值。
arm_length:
#   连接此塔到打印头的对角杆的长度（mm）。此参数必须为 stepper_a 提供；
#   对于 stepper_b 和 stepper_c，此参数默认为为 stepper_a 指定的值。
#angle:
#   此选项指定塔所在的角度（度）。stepper_a 的默认值为 210，
#   stepper_b 为 330，stepper_c 为 90。

# stepper_b 部分描述控制前右塔（330 度）的步进电机。
[stepper_b]

# stepper_c 部分描述控制后塔（90 度）的步进电机。
[stepper_c]

# delta_calibrate 部分启用 DELTA_CALIBRATE 扩展 g-code 命令，
# 可以校准塔限位开关位置和角度。
[delta_calibrate]
radius:
#   可探测区域的半径（mm）。这是要探测的喷嘴坐标半径；如果使用带有 XY 偏移的
#   自动探针，则选择足够小的半径以确保探针始终位于热床上方。必须提供此参数。
#speed: 50
#   校准期间非探测移动的速度（mm/s）。默认值为 50。
#horizontal_move_z: 5
#   在开始探测操作之前命令打印头移动到的高度（mm）。默认值为 5。
#use_probe_xy_offsets: False
#   如果为 True，将 `[probe]` 的 XY 偏移应用于探测位置。
#   默认值为 False。
```

### Deltesian 运动学

请参阅 [example-deltesian.cfg](../config/example-deltesian.cfg) 了解 deltesian 运动学配置文件示例。

此处仅描述 deltesian 打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: deltesian
max_z_velocity:
#   对于 deltesian 打印机，这限制了包含 Z 轴运动的移动的最大速度（mm/s）。
#   此设置可用于降低上下移动的最大速度（在 deltesian 打印机上，这些移动需要
#   比其他移动更高的步进速率）。默认值为将 max_velocity 用于 max_z_velocity。
#max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。如果打印机在 XY 移动上能达到
#   比 Z 移动更高的加速度（例如，使用输入整形器时），设置此值可能很有用。
#   默认值为将 max_accel 用于 max_z_accel。
#minimum_z_position: 0
#   用户可以命令打印头移动到的最小 Z 位置。默认值为 0。
#min_angle: 5
#   这表示 deltesian 臂可以达到的相对于水平的最小角度（度）。此参数旨在限制
#   臂变得完全水平，这将导致 XZ 轴意外反转的风险。默认值为 5。
#print_width:
#   有效工具头 X 坐标的距离（mm）。可以使用此设置来自定义工具头移动的
#   范围检查。如果在此处指定较大的值，则可能将工具头命令到与塔碰撞的位置。
#   此设置通常对应于热床宽度（mm）。
#slow_ratio: 3
#   用于限制靠近 X 轴极端位置移动的速度和加速度的比率。如果垂直距离除以水平
#   距离超过 slow_ratio 的值，则速度和加速度限制为其标称值的一半。如果垂直
#   距离除以水平距离超过 slow_ratio 值的两倍，则速度和加速度限制为其标称值的
#   四分之一。默认值为 3。

# stepper_left 部分用于描述控制左塔的步进电机。此部分还控制
# 所有塔的归位参数（homing_speed、homing_retract_dist）。
[stepper_left]
position_endstop:
#   当喷嘴位于构建区域中心且限位开关触发时，喷嘴与热床之间的距离（mm）。
#   此参数必须为 stepper_left 提供；对于 stepper_right，
#   此参数默认为为 stepper_left 指定的值。
arm_length:
#   连接塔滑车到打印头的对角杆的长度（mm）。此参数必须为 stepper_left 提供；
#   对于 stepper_right，此参数默认为为 stepper_left 指定的值。
arm_x_length:
#   打印机归位时打印头与塔之间的水平距离。此参数必须为 stepper_left 提供；
#   对于 stepper_right，此参数默认为为 stepper_left 指定的值。

# stepper_right 部分用于描述控制右塔的步进电机。
[stepper_right]

# stepper_y 部分用于描述 deltesian 机器人中控制 Y 轴的步进电机。
[stepper_y]
```

### CoreXY 运动学

请参阅 [example-corexy.cfg](../config/example-corexy.cfg) 了解 corexy（和 h-bot）运动学文件示例。

此处仅描述 corexy 打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: corexy
max_z_velocity:
#   这设置沿 Z 轴运动的最大速度（mm/s）。此设置可用于限制 Z 步进电机的
#   最大速度。默认值为将 max_velocity 用于 max_z_velocity。
max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。它限制 Z 步进电机的加速度。
#   默认值为将 max_accel 用于 max_z_accel。

# stepper_x 部分用于描述 X 轴以及控制 X+Y 运动的步进电机。
[stepper_x]

# stepper_y 部分用于描述 Y 轴以及控制 X-Y 运动的步进电机。
[stepper_y]

# stepper_z 部分用于描述控制 Z 轴的步进电机。
[stepper_z]
```

### ⚠️ 带有 X 和 Y 轴限制的 CoreXY 运动学

行为与 CoreXY 运动学完全相同，但允许为 X 和 Y 轴设置加速度限制。

CoreXY 上没有 X 和 Y 的速度限制，因为两个轴的拉出速度是相同的。


```
[printer]
kinematics: limited_corexy
max_z_velocity:
#   请参阅上方的 CoreXY 设置。
max_x_accel:
#   这设置沿 X 轴运动的最大加速度（mm/s^2）。它限制 X 步进电机的加速度。
#   默认值为将 max_accel 用于 max_x_accel。
max_y_accel:
#   这设置沿 Y 轴运动的最大加速度（mm/s^2）。它限制 Y 步进电机的加速度。
#   默认值为将 max_accel 用于 max_y_accel。
max_z_accel:
# 请参阅上方的 CoreXY 设置。
max_accel:
# 请参阅上方的 CoreXY 设置。
scale_xy_accel:
#   为 True 时，按当前工具头加速度缩放 XY 限制。
#   因子为：切片器加速度 / max(max_x_accel, max_y_accel)。
```

### CoreXZ 运动学

请参阅 [example-corexz.cfg](../config/example-corexz.cfg) 了解 corexz 运动学配置文件示例。

此处仅描述 corexz 打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: corexz
max_z_velocity:
#   这设置沿 Z 轴运动的最大速度（mm/s）。默认值为将 max_velocity 用于 max_z_velocity。
max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。默认值为将 max_accel 用于 max_z_accel。

# stepper_x 部分用于描述 X 轴以及控制 X+Z 运动的步进电机。
[stepper_x]

# stepper_y 部分用于描述控制 Y 轴的步进电机。
[stepper_y]

# stepper_z 部分用于描述 Z 轴以及控制 X-Z 运动的步进电机。
[stepper_z]
```

### ⚠️ 带有 X 和 Y 轴限制的 CoreXZ 运动学

```
[printer]
kinematics: limited_corexz
max_velocity: 500 # 以下两个值的斜边
max_x_velocity: 400
max_y_velocity: 300
max_z_velocity: 5
max_accel: 1500 # 您选择的默认加速度
max_x_accel: 12000
max_y_accel: 9000
max_z_accel: 100
scale_xy_accel: [True/False, 默认 False]
```

`max_velocity` 通常是 X 和 Y 速度的斜边，例如：
`max_x_velocity: 300` 和 `max_y_velocity: 400`，建议值为 `max_velocity: 500`。

如果 `scale_xy_accel` 为 False，由 `M204` 或 `SET_VELOCITY_LIMIT` 设置的 `max_accel` 将作为第三个限制。在这种情况下，此模块不会对加速度低于 `max_x_accel` 和 `max_y_accel` 的移动施加限制。

当 `scale_xy_accel` 为 `True` 时，`max_x_accel` 和 `max_y_accel` 将按动态设置的加速度与 `max_x_accel` 和 `max_y_accel` 斜边的比率进行缩放，如 `SET_KINEMATICS_LIMIT` 所报告。这意味着实际加速度将始终取决于方向。

例如，以下设置：
```
[printer]
max_x_accel: 12000
max_y_accel: 9000
scale_xy_accel: True
```

SET_KINEMATICS_LIMIT 将报告 37 度对角线上的最大加速度为 15000 mm/s^2。因此，在切片器中设置 3000 mm/s^2 的加速度将使工具头在这些 37 度和 143 度对角线上以 3000 mm/s^2 加速，但在与 X 轴对齐的移动上仅为 12000 * 3000 / 15000 = 2400 mm/s^2，纯 Y 移动为 18000 mm/s^2。


### Hybrid-CoreXY 运动学

请参阅 [example-hybrid-corexy.cfg](../config/example-hybrid-corexy.cfg) 了解 hybrid corexy 运动学配置文件示例。

此运动学也称为 Markforged 运动学。

此处仅描述 hybrid corexy 打印机特有的参数 - 请参阅 [通用运动学设置](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: hybrid_corexy
invert_kinematics: False
# ⚠️ 某些带有双滑车的 hybrid_corexy 机器如果工具头反向移动可能需要反转运动学
max_z_velocity:
#   这设置沿 Z 轴运动的最大速度（mm/s）。默认值为将 max_velocity 用于 max_z_velocity。
max_z_accel:
#   这设置沿 Z 轴运动的最大加速度（mm/s^2）。默认值为将 max_accel 用于 max_z_accel。

# stepper_x 部分用于描述 X 轴以及控制 X-Y 运动的步进电机。
[stepper_x]

# stepper_y 部分用于描述控制 Y 轴的步进电机。
[stepper_y]
```

# stepper_z 部分用于描述控制
# Z 轴的步进电机。
[stepper_z]
```

### 混合 CoreXZ 运动学

查看 [example-hybrid-corexz.cfg](../config/example-hybrid-corexz.cfg)
获取一个混合 corexz 运动学配置文件示例。

此运动学也称为 Markforged 运动学。

这里仅描述混合 corexy 打印机的特定参数
请参阅 [common kinematic settings](#common-kinematic-settings) 了解可用参数。

```
[printer]
kinematics: hybrid_corexz
invert_kinematics: False
# ⚠️ 一些具有双滑车的 hybrid_corexy 机器可能需要
#   如果工具头反向移动，则反转运动学
max_z_velocity:
#   这设置沿 z 轴运动的最大速度（单位为 mm/s）
#   默认使用 max_velocity 作为 max_z_velocity。
max_z_accel:
#   这设置沿 z 轴运动的最大加速度（单位为 mm/s^2）
#   默认使用 max_accel 作为 max_z_accel。

# stepper_x 部分用于描述 X 轴以及控制
# 控制 X-Z 运动的步进电机。
[stepper_x]

# stepper_y 部分用于描述控制
# Y 轴的步进电机。
[stepper_y]

# stepper_z 部分用于描述控制
# Z 轴的步进电机。
[stepper_z]
```

### 极坐标运动学

查看 [example-polar.cfg](../config/example-polar.cfg) 获取一个
极坐标运动学配置文件示例。

这里仅描述极坐标打印机的特定参数 - 请参阅
[common kinematic settings](#common-kinematic-settings) 了解可用参数。

极坐标运动学正在开发中。已知在 0, 0
位置周围移动无法正常工作。

```
[printer]
kinematics: polar
max_z_velocity:
#   这设置沿 z 轴运动的最大速度（单位为 mm/s）。此设置可用于限制
#   z 步进电机的最大速度。默认使用 max_velocity 作为
#   max_z_velocity。
max_z_accel:
#   这设置沿 z 轴运动的最大加速度（单位为 mm/s^2）。它限制了 z 步进
#   电机的加速度。默认使用 max_accel 作为 max_z_accel。

# stepper_bed 部分用于描述控制
# 热床的步进电机。
[stepper_bed]
gear_ratio:
#   必须指定 gear_ratio，且不能指定 rotation_distance。
#   例如，如果热床有一个 80 齿的滑轮由一个 16 齿的滑轮驱动，
#   则应指定齿轮比为 "80:16"。此参数必须提供。

# stepper_arm 部分用于描述控制
# 臂上滑车的步进电机。
[stepper_arm]

# stepper_z 部分用于描述控制
# Z 轴的步进电机。
[stepper_z]
```

### 旋转三角洲运动学

查看 [example-rotary-delta.cfg](../config/example-rotary-delta.cfg) 获取
一个旋转三角洲运动学配置文件示例。

这里仅描述旋转三角洲打印机的特定参数 - 请参阅
[common kinematic settings](#common-kinematic-settings) 了解可用参数。

旋转三角洲运动学正在开发中。归位移动可能会
超时，并且一些边界检查尚未实现。

```
[printer]
kinematics: rotary_delta
max_z_velocity:
#   对于三角洲打印机，这限制了具有 z 轴运动移动的最大速度（单位为 mm/s）。
#   此设置可用于降低上下移动的最大速度（在三角洲打印机上，这需要比
#   其他移动更高的步进速率）。默认使用 max_velocity 作为 max_z_velocity。
#minimum_z_position: 0
#   用户可能命令头部移动到的最小 Z 位置。默认为 0。
shoulder_radius:
#   由三个肩关节形成的水平圆的半径（单位为 mm），减去由
#   效应器关节形成的圆的半径。此参数也可以计算为：
#     shoulder_radius = (delta_f - delta_e) / sqrt(12)
#   此参数必须提供。
shoulder_height:
#   肩关节距离热床的距离（单位为 mm），减去效应器工具头高度。此参数必须提供。

# stepper_a 部分描述控制右后臂（30度）的步进电机。此部分还控制所有臂的
# 归位参数（homing_speed, homing_retract_dist）。
[stepper_a]
gear_ratio:
#   必须指定 gear_ratio，且不能指定 rotation_distance。例如，如果臂有一个
#   80 齿的滑轮由一个 16 齿的滑轮驱动，而该滑轮又连接到一个由 16 齿滑轮驱动的
#   60 齿滑轮，则应指定齿轮比为 "80:16, 60:16"。此参数必须提供。
position_endstop:
#   当喷头位于构建区域中心且限位开关触发时，喷头与热床之间的距离（单位为 mm）。
#   此参数对于 stepper_a 必须提供；对于 stepper_b 和 stepper_c，
#   此参数默认为 stepper_a 指定的值。
upper_arm_length:
#   连接“肩关节”和“肘关节”的臂的长度（单位为 mm）。此参数对于 stepper_a
#   必须提供；对于 stepper_b 和 stepper_c，此参数默认为 stepper_a 指定的值。
lower_arm_length:
#   连接“肘关节”和“效应器关节”的臂的长度（单位为 mm）。此参数对于 stepper_a
#   必须提供；对于 stepper_b 和 stepper_c，此参数默认为 stepper_a 指定的值。
#angle:
#   此选项指定臂所处的角度（单位为度）。默认为 stepper_a 为 30，stepper_b 为 150，
#   stepper_c 为 270。

# stepper_b 部分描述控制左后臂（150度）的步进电机。
[stepper_b]

# stepper_c 部分描述控制前臂（270度）的步进电机。
[stepper_c]

# delta_calibrate 部分启用一个 DELTA_CALIBRATE 扩展
# g-code 命令，可以校准肩限位位置。
[delta_calibrate]
radius:
#   可探测区域的半径（单位为 mm）。这是要探测的喷头坐标的半径；
#   如果使用具有 XY 偏移的自动探针，请选择一个足够小的半径，以便探针
#   始终位于热床上方。此参数必须提供。
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头部应被命令移动到的高度（单位为 mm）。默认为 5。
```

### 钢缆绞盘运动学

查看 [example-winch.cfg](../config/example-winch.cfg) 获取
一个钢缆绞盘运动学配置文件示例。

这里仅描述钢缆绞盘打印机的特定参数 - 请参阅
[common kinematic settings](#common-kinematic-settings) 了解可用参数。

钢缆绞盘支持是实验性的。钢缆绞盘运动学尚未实现归位。
为了归位打印机，请手动发送移动命令，直到工具头位于 0, 0, 0，然后发出
`G28` 命令。

```
[printer]
kinematics: winch

# stepper_a 部分描述连接到第一个钢缆绞盘的步进电机。可以定义
# 最少 3 个和最多 26 个钢缆绞盘（stepper_a 到 stepper_z），但通常定义 4 个。
[stepper_a]
rotation_distance:
#   rotation_distance 是步进电机每完整旋转一次时，工具头
#   向钢缆绞盘移动的标称距离（单位为 mm）。此参数必须提供。
anchor_x:
anchor_y:
anchor_z:
#   钢缆绞盘在笛卡尔空间中的 X、Y 和 Z 位置。
#   这些参数必须提供。
```

### 无运动学

可以定义一个特殊的“无”运动学以禁用 Kalico 中的运动学支持。
这对于控制非典型 3D 打印机的设备或用于调试目的可能很有用。

```
[printer]
kinematics: none
max_velocity: 1
max_accel: 1
#   必须定义 max_velocity 和 max_accel 参数。这些值不用于“无”运动学。
```

## 通用挤出机和热床支持

### [extruder]

挤出机部分用于描述喷头热端的加热器参数以及控制挤出机的步进电机。请参阅
[command reference](G-Codes.md#extruder) 了解更多信息。
请参阅 [pressure advance guide](Pressure_Advance.md) 了解有关调整压力
推进的信息。请参阅 [PID](PID.md) 或 [MPC](MPC.md) 了解有关控制方法的更详细信息。

```
[extruder]
step_pin:
dir_pin:
enable_pin:
microsteps:
rotation_distance:
#full_steps_per_rotation:
#gear_ratio:
#   请参阅“stepper”部分了解上述参数的描述。如果未指定上述参数，
#   则不会将任何步进电机与喷头热端关联（尽管 SYNC_EXTRUDER_MOTION 命令
#   可以在运行时关联一个）。
nozzle_diameter:
#   喷嘴孔的直径（单位为 mm）。此参数必须提供。
filament_diameter:
#   进入挤出机的原始灯丝的标称直径（单位为 mm）。此参数必须提供。
#max_extrude_cross_section:
#   挤出横截面的最大面积（单位为 mm^2）（例如，挤出宽度乘以层高）。此设置
#   防止在相对较小的 XY 移动期间过度挤出。如果移动请求超过此值的挤出速率，
#   将导致返回错误。默认为：4.0 * nozzle_diameter^2
#instantaneous_corner_velocity: 1.000
#   挤出机在两次移动连接处的最大瞬时速度变化（单位为 mm/s）。默认为 1mm/s。
#max_extrude_only_distance: 50.0
#   回抽或仅挤出移动可能具有的最大长度（单位为 mm 的原始灯丝）。如果回抽或
#   仅挤出移动请求的距离大于此值，将导致返回错误。默认为 50mm。
#max_extrude_only_velocity:
#max_extrude_only_accel:
#   挤出机电机用于回抽和仅挤出移动的最大速度（单位为 mm/s）和加速度
#   （单位为 mm/s^2）。这些设置对正常打印移动没有影响。如果未指定，
#   则它们将被计算为与横截面为 4.0*nozzle_diameter^2 的 XY 打印移动
#   的限制相匹配。
#pressure_advance: 0.0
#   在挤出机加速期间推入挤出机的原始灯丝量。在减速期间会回抽相同量的灯丝。
#   它以毫米/毫米/秒为单位测量。默认为 0，这会禁用压力推进。
#pressure_advance_smooth_time: 0.040
#   用于计算压力推进的平均挤出机速度的时间范围（单位为秒）。较大的值会导致
#   挤出机移动更平滑。此参数不得超过 200ms。此设置仅在 pressure_advance
#   非零时适用。默认为 0.040（40 毫秒）。
#
# 剩下的变量描述挤出机加热器。
heater_pin:
#   控制加热器的 PWM 输出引脚。此参数必须提供。
#max_power: 1.0
#   heater_pin 可设置的最大功率（表示为 0.0 到 1.0 的值）。值 1.0 允许引脚
#   在延长期内完全启用，而值 0.5 则允许引脚最多启用一半的时间。此设置可用于
#   将加热器的总功率输出（在延长期内）限制在一定范围内。默认为 1.0。
sensor_type:
#   传感器类型 - 常见热敏电阻有 "EPCOS 100K B57560G104F"、
#   "ATC Semitec 104GT-2"、"ATC Semitec 104NT-4-R025H42G"、"Generic
#   3950"、"Honeywell 100K 135-104LAG-J01"、"NTC 100K MGB18-104F39050L32"、
#   "SliceEngineering 450" 和 "TDK NTCG104LH104JT1"。请参阅“温度传感器”部分
#   了解其他传感器。此参数必须提供。
sensor_pin:
#   连接到传感器的模拟输入引脚。此参数必须提供。
#pullup_resistor: 4700
#   连接到热敏电阻的上拉电阻的电阻值（单位为欧姆）。此参数仅在传感器为
#   热敏电阻时有效。默认为 4700 欧姆。
#smooth_time: 1.0
#   温度测量值将被平滑处理以减少测量噪声影响的时间值（单位为秒）。默认为 1 秒。
control:
#   控制算法（pid、pid_v、dual_loop_pid、watermark 或 mpc）。此参数必须提供。
#   pid_v 应仅用于校准良好且噪声低到中等的加热器。
#
#   如果 control: pid、pid_v 或 dual_loop_pid
#pid_Kp:
#pid_Ki:
#pid_Kd:
#   PID 反馈控制系统的比例（pid_Kp）、积分（pid_Ki）和微分（pid_Kd）设置。
#   Kalico 使用以下通用公式评估 PID 设置：
#     heater_pwm = (Kp*error + Ki*integral(error) - Kd*derivative(error)) / 255
#   其中“error”是“requested_temperature - measured_temperature”，
#   “heater_pwm”是请求的加热速率，0.0 表示完全关闭，1.0 表示完全打开。
#   考虑使用 PID_CALIBRATE 命令获取这些参数。对于 PID 加热器，必须提供
#   pid_Kp、pid_Ki 和 pid_Kd 参数。
#
#   如果 control: watermark
#max_delta: 2.0
#   在“watermark”控制的加热器上，这是在禁用加热器之前高于目标温度的摄氏度数，
#   以及在重新启用加热器之前低于目标温度的摄氏度数。默认为 2 摄氏度。
#
#   如果 control: mpc
#   请参阅 MPC.md 了解有关这些参数的详细信息。
#heater_power:
#cooling_fan:
#ambient_temp_sensor:
#filament_diameter: 1.75
#filament_density: 1.2
#filament_heat_capacity: 1.8
#
#pwm_cycle_time: 0.100
#   加热器每个软件 PWM 周期的时间（单位为秒）。除非有电气要求将加热器切换
#   速度提高到每秒 10 次以上，否则不建议设置此值。默认为 0.100 秒。
#lost_update_tolerance: 2
#   可从中恢复的最大连续传感器丢失样本数。
#min_extrude_temp: 170
#   可以发出挤出机移动命令的最低温度（单位为摄氏度）。默认为 170 摄氏度。
min_temp:
max_temp:
#   加热器必须保持在内的有效温度的最大范围（单位为摄氏度）。这控制了微控制器
#   代码中实现的安全功能 - 如果测量温度超出此范围，微控制器将进入关闭状态。
#   此检查有助于检测一些加热器和传感器硬件故障。将此范围设置得足够宽，
#   以便合理的温度不会导致错误。这些参数必须提供。
per_move_pressure_advance: False
#   如果为 true，则在处理移动时使用 trapq 中的压力推进常数
#   这导致压力推进的更改立即被考虑，对于当前队列中的所有移动，
#   而不是在队列被刷新后约 250ms。
#
#   如果: control: dual_loop_pid
#inner_sensor_name:
#   用于与 'dual_loop_pid' 进行温度控制的第二个传感器的 temperature_sensor 名称。
#   此传感器将限制加热器功率，以不允许温度超过 'inner_max_temp' 值。
#
#   如果: control: dual_loop_pid
#inner_max_temp:
#   内部传感器允许的最大温度目标。
#
#   如果 control: dual_loop_pid
#inner_pid_Kp:
#inner_pid_Ki:
#inner_pid_Kd:
#   'dual_loop_pid' 控制使用两个 PID 环路来控制温度。内部（次要）PID 环路
#   直接控制温度。主 PID 环路控制向次要 PID 环路的功率。这允许主 PID 环路
#   针对温度控制进行调优，而次要 PID 环路可以针对功率控制进行调优，不超过
#   在 'inner_max_temp' 上设置的温度限制。主传感器位于温度测量应更准确的位置
#   （例如，在热床表面上）。次要传感器位于温度测量不应超过限制的位置
#   （例如，在硅胶加热器上）。
```

### [heater_bed]

heater_bed 部分描述了一个加热热床。它使用“extruder”部分中描述的相同加热器设置。

```
[heater_bed]
heater_pin:
sensor_type:
sensor_pin:
control:
min_temp:
max_temp:
#   请参阅“extruder”部分了解上述参数的描述。
```

### [pid_profile]

PID 配置文件指定一组可以在运行时加载的 PID 值。

```
[pid_profile <heater> <profile-name>]
pid_version: 1
# 这定义了保存时的版本，对于兼容性检查很重要，请保持为 1！
pid_target:
# 仅供参考，指定配置文件校准的温度。如果您创建自定义配置文件，
# 请输入该配置文件预期使用的温度，或留空。
pid_tolerance:
# 配置文件自动校准时使用的容差。如果您定义自定义配置文件，请留空。
control: <pid|pid_v>
# 必须是 pid 或 pid_v。
# 此参数是必需的。
pid_kp:
# PID 控制的 P 值。
# 此参数是必需的。
pid_ki:
# PID 控制的 I 值。
# 此参数是必需的。
pid_kd:
# PID 控制的 D 值。
# 此参数是必需的。
```
有关更多信息，请阅读 docs/PID.md

## 热床调平支持

### [bed_mesh]

网格热床调平。可以定义 bed_mesh 配置部分以启用基于探测点生成的网格来偏移 Z 轴的移动转换。当使用探针来归位 Z 轴时，建议在 printer.cfg 中定义一个 safe_z_home 部分，以便向打印区域中心归位。

请参阅 [bed mesh guide](Bed_Mesh.md) 和 [command reference](G-Codes.md#bed_mesh) 了解更多信息。

可视化示例：

```
 矩形热床, probe_count = 3, 3:
             x---x---x (max_point)
             |
             x---x---x
                     |
 (min_point) x---x---x

 圆形热床, round_probe_count = 5, bed_radius = r:
                 x (0, r) end
               /
             x---x---x
                       \
 (-r, 0) x---x---x---x---x (r, 0)
           \
             x---x---x
                   /
                 x  (0, -r) start
```

```
[bed_mesh]
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头部应被命令移动到的高度（单位为 mm）。默认为 5。
#horizontal_z_clearance:
#   工具头在移动到下一个网格点之前将在每个网格点抬升的相对高度（单位为 mm）。
#   如果启用，`horizontal_move_z` 值仅用于移动到第一个网格点的行程移动。
#   默认为 None。
#mesh_radius:
#   定义圆形热床要探测的网格半径。请注意，半径是相对于 mesh_origin 选项
#   指定的坐标。对于圆形热床，此参数必须提供；对于矩形热床，必须省略。
#mesh_origin:
#   定义圆形热床网格的中心 X、Y 坐标。此坐标相对于探针的位置。调整
#   mesh_origin 以最大化网格半径可能很有用。默认为 0, 0。对于矩形热床，
#   此参数必须省略。
#mesh_min:
#   定义矩形热床网格的最小 X、Y 坐标。此坐标相对于探针的位置。这将是
#   最靠近原点的第一个探测点。对于矩形热床，此参数必须提供。
#mesh_max:
#   定义矩形热床网格的最大 X、Y 坐标。遵循与 mesh_min 相同的原则，但这将是
#   距离热床原点最远的探测点。对于矩形热床，此参数必须提供。
#probe_count: 3, 3
#   对于矩形热床，这是一个逗号分隔的整数对 X、Y，定义沿每个轴要探测的点数。
#   单个值也有效，在这种情况下，该值将应用于两个轴。默认为 3, 3。
#round_probe_count: 5
#   对于圆形热床，此整数值定义沿每个轴要探测的最大点数。此值必须为奇数。
#   默认为 5。
#fade_start: 1.0
#   启用淡入淡出时，开始逐步淘汰 z 调整的 gcode z 位置。默认为 1.0。
#fade_end: 0.0
#   淡入淡出完成的 gcode z 位置。当设置为低于 fade_start 的值时，淡入淡出被禁用。
#   应注意的是，淡入淡出可能会在打印的 z 轴上添加不必要的缩放。如果用户希望
#   启用淡入淡出，建议值为 10.0。默认为 0.0，这会禁用淡入淡出。
#fade_target:
#   淡入淡出应收敛的 z 位置。当此值设置为非零值时，它必须在网格的 z 值范围内。
#   希望收敛到 z 归位位置的用户应将其设置为 0。默认为网格的平均 z 值。
#split_delta_z: .025
#   沿移动触发拆分的 Z 差异量（单位为 mm）。默认为 .025。
#move_check_distance: 5.0
#   沿移动检查 split_delta_z 的距离（单位为 mm）。这也是移动可被拆分的最小
#   长度。默认为 5.0。
#mesh_pps: 2, 2
#   逗号分隔的整数对 X、Y，定义沿每个轴在网格中每个段要插值的点数。
#   “段”可以定义为每个探测点之间的空间。用户可以输入一个值，该值将应用于
#   两个轴。默认为 2, 2。
#algorithm: lagrange
#   要使用的插值算法。可以是“lagrange”或“bicubic”。此选项不会影响 3x3 网格，
#   这些网格被强制使用 lagrange 采样。默认为 lagrange。
#bicubic_tension: .2
#   使用 bicubic 算法时，可以应用上述张力参数来改变插值的斜率量。较大的数字
#   将增加斜率量，这会导致网格中更多的曲率。默认为 .2。
#zero_reference_position:
#   指定 Z = 0 的热床位置的可选 X,Y 坐标。指定此选项时，网格将被偏移，
#   以便在此位置发生零 Z 调整。默认为无零参考。
#faulty_region_1_min:
#faulty_region_1_max:
#   定义故障区域的可选点。请参阅 docs/Bed_Mesh.md 了解有关故障区域的详细信息。
#   最多可以添加 99 个故障区域。默认情况下没有设置故障区域。
#adaptive_margin:
#   生成自适应网格时，在定义的打印对象使用的热床区域周围添加的可选边距
#   （单位为 mm）。
#bed_mesh_default:
#   可选地提供您希望在初始化时加载的配置文件名称。默认情况下，不加载配置文件。
#use_probe_xy_offsets: True
#   如果为 True，将 `[probe]` XY 偏移应用于探测位置。默认为 True。
```

### [bed_tilt]

热床倾斜补偿。可以定义 bed_tilt 配置部分以启用考虑热床倾斜的移动转换。请注意，bed_mesh 和 bed_tilt 不兼容；不能同时定义两者。

请参阅 [command reference](G-Codes.md#bed_tilt) 了解更多信息。

```
[bed_tilt]
#x_adjust: 0
#   对于 X 轴上的每毫米，要添加到每个移动 Z 高度的量。默认为 0。
#y_adjust: 0
#   对于 Y 轴上的每毫米，要添加到每个移动 Z 高度的量。默认为 0。
#z_adjust: 0
#   当喷头名义上位于 0, 0 时要添加到 Z 高度的量。默认为 0。
# 剩余参数控制一个 BED_TILT_CALIBRATE 扩展
# g-code 命令，可用于校准适当的 x 和 y 调整参数。
#points:
#   应在 BED_TILT_CALIBRATE 命令期间探测的 X、Y 坐标列表（每行一个；后续行缩进）。
#   指定喷头的坐标，并确保探针在给定的喷头坐标处位于热床上方。默认是
#   不启用该命令。
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头部应被命令移动到的高度（单位为 mm）。默认为 5。
#use_probe_xy_offsets: False
#   如果为 True，将 `[probe]` XY 偏移应用于探测位置。默认为 False。
```

### [bed_screws]

帮助调整热床调平螺钉的工具。可以定义 [bed_screws] 配置部分以启用 BED_SCREWS_ADJUST g-code 命令。

请参阅 [leveling guide](Manual_Level.md#adjusting-bed-leveling-screws) 和 [command reference](G-Codes.md#bed_screws) 了解更多信息。

```
[bed_screws]
#screw1:
#   第一个热床调平螺钉的 X、Y 坐标。这是要命令喷头移动到的、直接位于热床
#   螺钉上方（或尽可能接近但仍在热床上方）的位置。此参数必须提供。
#screw1_name:
#   给定螺钉的任意名称。当辅助脚本运行时显示此名称。默认使用基于螺钉 XY 位置的
#   名称。
#screw1_fine_adjust:
#   要命令喷头移动到的 X、Y 坐标，以便可以微调热床调平螺钉。默认是不执行
#   热床螺钉的精细调整。
#screw2:
#screw2_name:
#screw2_fine_adjust:
#...
#   额外的热床调平螺钉。必须定义至少三个螺钉。
#horizontal_move_z: 5
#   从一个螺钉位置移动到下一个位置时，头部应被命令移动到的高度（单位为 mm）。
#   默认为 5。
#probe_height: 0
#   调整热床和喷头的热膨胀后探针的高度（单位为 mm）。默认为零。
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#probe_speed: 5
#   从 horizontal_move_z 位置移动到 probe_height 位置时的速度（单位为 mm/s）。
#   默认为 5。
```

### [screws_tilt_adjust]

使用 Z 探针帮助调整热床螺钉倾斜的工具。可以定义 screws_tilt_adjust 配置部分以启用 SCREWS_TILT_CALCULATE g-code 命令。

请参阅 [leveling guide](Manual_Level.md#adjusting-bed-leveling-screws-using-the-bed-probe) 和 [command reference](G-Codes.md#screws_tilt_adjust) 了解更多信息。

```
[screws_tilt_adjust]
#screw1:
#   第一个热床调平螺钉的 (X, Y) 坐标。这是要命令喷头移动到的位置，以便探针
#   直接位于热床螺钉上方（或尽可能接近但仍在热床上方）。这是用于计算的基础
#   螺钉。此参数必须提供。
#screw1_name:
#   给定螺钉的任意名称。当辅助脚本运行时显示此名称。默认使用基于螺钉 XY 位置的
#   名称。
#screw2:
#screw2_name:
#...
#   额外的热床调平螺钉。必须定义至少两个螺钉。
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头部应被命令移动到的高度（单位为 mm）。默认为 5。
#screw_thread: CW-M3
#   用于热床调平的螺钉类型，M3、M4 或 M5，以及用于调平热床的旋钮的旋转方向。
#   接受的值：CW-M3、CCW-M3、CW-M4、CCW-M4、CW-M5、CCW-M5、CW-M8、CCW-M8。
#   默认值为 CW-M3，大多数打印机使用。顺时针旋转旋钮会减小喷头与热床之间的
#   间隙。相反，逆时针旋转会增加间隙。
#use_probe_xy_offsets: False
#   如果为 True，将 `[probe]` XY 偏移应用于探测位置。默认为 False。
```

### [z_tilt]

多 Z 步进电机倾斜调整。此功能允许独立调整多个 z 步进电机（请参阅“stepper_z1”部分）以调整倾斜。如果存在此部分，则 Z_TILT_ADJUST 扩展 [G-Code 命令](G-Codes.md#z_tilt) 可用。

```
[z_tilt]
#z_positions:
#   描述每个热床“枢轴点”位置的 X、Y 坐标列表（每行一个；后续行缩进）。
#   “枢轴点”是热床连接到给定 Z 步进电机的点。它使用喷头坐标（喷头如果可以直接
#   移动到该点上方时的 X、Y 位置）描述。第一个条目对应于 stepper_z，第二个对应于
#   stepper_z1，第三个对应于 stepper_z2，依此类推。此参数必须提供。
#points:
#   应在 Z_TILT_ADJUST 命令期间探测的 X、Y 坐标列表（每行一个；后续行缩进）。
#   指定喷头的坐标，并确保探针在给定的喷头坐标处位于热床上方。此参数必须提供。
#speed: 50
#   校准期间非探测移动的速度（单位为 mm/s）。默认为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头部应被命令移动到的高度（单位为 mm）。默认为 5。
#min_horizontal_move_z: 1.0
#   启用 adaptive_horizontal_move_z 时使用的水平移动 z 的最小值。默认为 1mm
#adaptive_horizontal_move_z: False
#   将其设置为 True 以在第一轮调整后自动调整水平移动 z，基于误差。
#   启用时，初始 horizontal_move_z 是配置值，后续迭代将 horizontal_move_z 设置为
#   误差的 ceil 或 min_horizontal_move_z - 以较大者为准。默认为 False。
#retries: 0
#   如果探测点不在容差范围内，则重试的次数。
#retry_tolerance: 0
#   如果启用了重试，则当最大和最小探测点差异超过 retry_tolerance 时重试。请注意，
#   这里变化的最小单位将是单个步进。但是，如果您探测的点多于步进电机数，则您可能
#   会有一个固定的最小值用于探测点的范围，您可以通过观察命令输出来学习。
#increasing_threshold: 0.0000001
#   设置探测点在 z_tilt 中止之前可以增加的阈值。要禁用验证，请将此参数设置为
#   较高的值。
#use_probe_xy_offsets: False
#   如果为 True，将 `[probe]` XY 偏移应用于探测位置。默认为 False。
#enforce_lift_speed: False
#   默认情况下，达到 `horizontal_move_z` 的第一次 Z 移动使用 `speed`。
#   将 `enforce_lift_speed` 设置为 True 以强制使用 `lift_speed`。默认为 False。
#use_adjustments: False
#   如果设置为 true，则使用 trails 在此处描述的行为：
#   https://github.com/Trails5000/klipper/commit/47b5a91f96761961e693031fa514a0025a877117
#alternate_probe_direction: False
#   如果为 True，则在完整探测通过/重试之间交替物理探测方向。第一次通过使用配置的
#   点顺序，下一次通过以相反顺序探测相同的点。测量结果仍以配置的逻辑点顺序返回，
#   因此 z_tilt 计算不变。这可以减少大型机器上鲍登管、灯丝路径、脐带和电缆束的
#   重复扭曲。它还避免了重试通过之间从最后一个点回到第一个点的额外行程移动。
#   默认为 False。
#start_reverse: False
#   如果为 True 并且启用了 alternate_probe_direction，则以相反顺序开始第一次
#   探测通过。后续重试通过将继续交替方向。默认为 False。
```

#### [z_tilt_ng]

z_tilt 的下一代，添加了 Z_TILT_CALIBRATE 和 Z_TILT_AUTODETECT
扩展 [G-Code 命令](G-Codes.md#z_tilt_ng)。Z_TILT_CALIBRATE 执行多次
探测运行以计算 z_offsets，从而使用更少的探测点实现精确的倾斜调整。Z_TILT_AUTODETECT 通过迭代探测自动确定每个 Z 步进电机的枢轴位置。当存在此部分时，这些扩展命令可用，提高床面调平精度和校准效率。

```
[z_tilt_ng]
#z_positions:
# 参见 [z_tilt]。除非提供了参数 "extra_points"，否则必须提供此参数。在这种情况下，只能运行命令 Z_TILT_AUTODETECT 来自动确定 z_positions。请参阅下面的 'extra_points'。
#z_offsets:
#   每个 z_position 的 Z 偏移列表。在 Z_TILT_ADJUST 期间，z_offset 会添加到每个探测值中，以补偿床面的不平整。这些值也可以通过运行 Z_TILT_CALIBRATE 自动检测。请参阅下面的 "extra_points"。
#points:
# 参见 [z_tilt]
#speed: 50
# 参见 [z_tilt]
#horizontal_move_z: 5
# 参见 [z_tilt]
#min_horizontal_move_z: 1.0
# 参见 [z_tilt]
#adaptive_horizontal_move_z: False
# 参见 [z_tilt]
#retries: 0
# 参见 [z_tilt]
#retry_tolerance: 0
# 参见 [z_tilt]
#increasing_threshold: 0.0000001
# 参见 [z_tilt]
#use_probe_xy_offsets: False
# 参见 [z_tilt]
#enforce_lift_speed: False
# 参见 [z_tilt]
#extra_points:
#   与上面 "points" 格式相同的列表。此列表包含在 Z_TILT_CALIBRATE 和 Z_TILT_AUTODETECT 两个校准命令期间要探测的额外点。如果床面不完全平整，可以使用 "points" 指定更多探测点。在这种情况下，Z_TILT_ADJUST 将通过最小二乘算法确定最佳拟合。由于这会在每次 Z_TILT_ADJUST 运行时带来额外开销，因此可以将额外探测点移动到这里，并使用 Z_TILT_CALIBRATE 来查找用于 Z_TILT_ADJUST 中探测点的 z_offsets。
#   额外点也用于 T_ZILT_AUTODETECT 期间。此命令可以通过在故意倾斜的床面上进行多次探测来自动确定 z_positions。目前仅针对 3 个 z 步进电机实现。
#   请注意，要使两个命令正常工作，必须安装 numpy。
#averaging_len: 3
#   Z_TILT_CALIBRATE 和 Z_TILT_AUTODETECT 都会重复运行，直到结果无法再改进。为确定这一点，探测值会被平均。用于平均的运行次数通过此参数配置。
#autodetect_delta: 1.0
#   Z_TILT_AUTODETECT 故意倾斜床面的程度。较高的值会产生更好的结果，但也可能导致床面倾斜到喷嘴在探测之前接触床面的情况。默认值是保守的。
#use_adjustments: False
#   如果设置为 true，则使用此处 trails 描述的行为：https://github.com/Trails5000/klipper/commit/47b5a91f96761961e693031fa514a0025a877117
```

### [quad_gantry_level]

使用 4 个独立控制的 Z 电机进行移动龙门调平。
校正移动龙门上的双曲抛物面效应（薯片效应），龙门更具灵活性。
警告：在移动床上使用此功能可能导致不良结果。
如果存在此部分，则 QUAD_GANTRY_LEVEL 扩展 G 代码命令可用。此例程假设以下 Z 电机配置：

```
 ----------------
 |Z1          Z2|
 |  ---------   |
 |  |       |   |
 |  |       |   |
 |  x--------   |
 |Z           Z3|
 ----------------
```

其中 x 是床上的 0, 0 点。

```
[quad_gantry_level]
#gantry_corners:
#   描述龙门两个对角点的 X、Y 坐标列表，以换行符分隔。第一个条目对应 Z，第二个对应 Z2。此参数必须提供。
#points:
#   应在 QUAD_GANTRY_LEVEL 命令期间探测的四个 X、Y 点列表，以换行符分隔。位置的顺序很重要，应依次对应 Z、Z1、Z2 和 Z3 位置。此参数必须提供。为获得最大精度，请确保配置了探测偏移。
#speed: 50
#   校准期间非探测移动的速度（mm/s）。默认值为 50。
#horizontal_move_z: 5
#   在开始探测操作之前，头应被命令移动到的高度（mm）。默认值为 5。
#min_horizontal_move_z: 1.0
#   启用 adaptive_horizontal_move_z 时使用的水平移动 z 最小值。默认值为 1mm。
#adaptive_horizontal_move_z: False
#   设置为 True 以在第一轮调整后根据误差自动调整水平移动 z。启用时，初始 horizontal_move_z 为配置值，后续迭代将 horizontal_move_z 设置为误差的 ceil 或 min_horizontal_move_z - 取较大值。默认值为 False。
#max_adjust: 4
#   如果请求的调整大于此值，安全限制将中止 quad_gantry_level。
#retries: 0
#   如果探测点不在公差内，则重试的次数。
#retry_tolerance: 0
#   如果启用重试，则当最大和最小探测点相差超过 retry_tolerance 时重试。
#increasing_threshold: 0.0000001
#   设置探测点在 qgl 中止前可以增加的阈值。要禁用验证，请将此参数设置为一个高值。
#use_probe_xy_offsets: False
#   如果为 True，将 `[probe]` XY 偏移应用于探测位置。默认值为 False。
#enforce_lift_speed: False
#   默认情况下，首次达到 `horizontal_move_z` 的 Z 移动使用 `speed`。将 `enforce_lift_speed` 设置为 True 以强制使用 `lift_speed`。默认值为 False。
#alternate_probe_direction: False
#   如果为 True，在完整的探测通过/重试之间交替物理探测方向。第一次通过使用配置的点顺序，下一次通过以相反顺序探测相同的点。测量结果仍以配置的逻辑点顺序返回，因此四龙门调平计算不变。这可以减少大型机器上鲍登管、耗材路径、脐带和电缆束的重复扭曲。它还避免了在重试通过之间从最后一点返回到第一点的额外移动。默认值为 False。
#start_reverse: False
#   如果为 True 且启用了 alternate_probe_direction，则第一次探测通过以相反顺序开始。后续重试通过将继续交替方向。默认值为 False。
```

### [skew_correction]

打印机偏斜校正。可以使用软件校正三个平面上的打印机偏斜：xy、xz、yz。这是通过沿平面打印校准模型并测量三个长度来完成的。由于偏斜校正的性质，这些长度通过 gcode 设置。详情请参阅 [偏斜校正](Skew_Correction.md) 和 [命令参考](G-Codes.md#skew_correction)。

```
[skew_correction]
```

### [z_thermal_adjust]

温度相关的工具头 Z 位置调整。使用温度传感器（通常与框架的垂直部分耦合）实时补偿由打印机框架热膨胀引起的垂直工具头移动。可以定义多个部分作为 [z_thermal_adjust 组件]，以补偿不同打印机组件（如热端、热断裂和框架）的热膨胀。

另请参阅：[扩展 g-code 命令](G-Codes.md#z_thermal_adjust)。

```
[z_thermal_adjust]
#temp_coeff:
#   膨胀温度系数，单位为 mm/degC。例如，temp_coeff 为 0.01 mm/degC 时，温度传感器每升高一摄氏度，Z 轴将向下移动 0.01 mm。默认值为 0.0 mm/degC，即不进行调整。
#smooth_time:
#   应用于温度传感器的平滑窗口（秒）。可以减少由于传感器噪声引起的过度小校正导致的电机噪声。默认值为 2.0 秒。
#z_adjust_off_above:
#   在此 Z 高度 [mm] 以上禁用调整。最后一次计算的校正将保持应用，直到工具头再次移动到指定的 Z 高度以下。默认值为 99999999.0 mm（始终开启）。
#max_z_adjustment:
#   可应用于 Z 轴的最大绝对调整量 [mm]。默认值为 99999999.0 mm（无限制）。
#sensor_type:
#sensor_pin:
#min_temp:
#max_temp:
#   温度传感器配置。
#   请参阅 "extruder" 部分以了解上述参数的定义。
#gcode_id:
#   请参阅 "heater_generic" 部分以了解此参数的定义。
```

## 自定义归位

### [safe_z_home]

安全 Z 归位。可以使用此机制在特定 X、Y 坐标处归位 Z 轴。这在工具头（例如）必须移动到床面中心才能归位 Z 时很有用。

```
[safe_z_home]
home_xy_position:
#   应执行 Z 归位的 X、Y 坐标（例如 100, 100）。此参数必须提供。
#speed: 50.0
#   工具头移动到安全 Z 归位坐标的速度。默认值为 50 mm/s。
#z_hop:
#   归位前提升 Z 轴的距离（mm）。这适用于任何归位命令，即使它不归位 Z 轴。如果 Z 轴已归位且当前 Z 位置小于 z_hop，则会将头提升到 z_hop 的高度。如果 Z 轴尚未归位，头将提升 z_hop。默认值为不实现 Z hop。
#z_hop_speed: 15.0
#   归位前提升 Z 轴的速度（mm/s）。默认值为 15 mm/s。
#move_to_previous: False
#   设置为 True 时，Z 轴归位后 X 和 Y 轴将重置到其先前位置。默认值为 False。
#home_y_before_x: False
#  # 如果为 True，Y 轴将首先归位。默认值为 False。
```

### [homing_override]

归位覆盖。可以使用此机制运行一系列 g-code 命令来替代正常 g-code 输入中的 G28。这在需要特定程序来归位打印机的打印机上可能很有用。

```
[homing_override]
gcode:
#   应执行的 G-Code 命令列表，以替代正常 g-code 输入中的 G28 命令。有关 G-Code 格式，请参阅 docs/Command_Templates.md。如果此命令列表中包含 G28，则将调用打印机的正常归位过程。此处列出的命令必须归位所有轴。此参数必须提供。
#axes: xyz
#   要覆盖的轴。例如，如果设置为 "z"，则仅当 z 轴归位时（例如通过 "G28" 或 "G28 Z0" 命令）才会运行覆盖脚本。请注意，覆盖脚本仍应归位所有轴。默认值为 "xyz"，导致覆盖脚本在所有 G28 命令处运行。
#set_position_x:
#set_position_y:
#set_position_z:
#   如果指定，打印机将在运行上述 g-code 命令之前假定轴处于指定位置。设置此项会禁用该轴的归位检查。如果在调用正常 G28 机制之前必须移动头，这可能很有用。默认值为不强制设置轴的位置。
```

### [endstop_phase]

步进相位调整的限位开关。要使用此功能，请定义一个带有 "endstop_phase" 前缀后跟相应步进配置部分名称的配置部分（例如 "[endstop_phase stepper_z]"）。此功能可以提高限位开关的准确性。添加一个裸的 "[endstop_phase]" 声明以启用 ENDSTOP_PHASE_CALIBRATE 命令。

有关其他信息，请参阅 [限位相位指南](Endstop_Phase.md) 和 [命令参考](G-Codes.md#endstop_phase)。

```
[endstop_phase stepper_z]
#endstop_accuracy:
#   设置限位开关的预期精度（mm）。这表示限位开关可能触发的最大误差距离（例如，如果限位开关可能偶尔提前 100um 或最多延迟 100um 触发，则设置为 0.200 以表示 200um）。默认值为 4*rotation_distance/full_steps_per_rotation。
#trigger_phase:
#   这指定撞击限位开关时预期的步进电机驱动器相位。它由两个数字组成，用斜杠分隔 - 相位和总相数（例如 "7/64"）。仅当确定步进电机驱动器在每次 MCU 复位时都复位时才设置此值。如果未设置，则步进相位将在第一次归位时检测，并且该相位将用于所有后续归位。
#endstop_align_zero: False
#   如果为 true，则轴的 position_endstop 将被有效修改，以便轴的零位置发生在步进电机的全步上。（如果用于 Z 轴且打印层高是全步距离的倍数，则每层都将发生在全步上。）默认值为 False。
```

## G-Code 宏和事件

### [gcode_macro]

G-Code 宏（可以定义任意数量带有 "gcode_macro" 前缀的部分）。有关更多信息，请参阅 [命令模板指南](Command_Templates.md)。

```
[gcode_macro my_cmd]
#gcode:
#   应执行的 G-Code 命令列表，以替代 "my_cmd"。有关 G-Code 格式，请参阅 docs/Command_Templates.md。此参数必须提供。
#variable_<name>:
#   可以指定任意数量带有 "variable_" 前缀的选项。给定的变量名将被分配给定值（解析为 Python 字面量），并在宏扩展期间可用。例如，具有 "variable_fan_speed = 75" 的配置可能包含 "M106 S{ fan_speed * 255 }" 的 gcode 命令。可以使用 SET_GCODE_VARIABLE 命令在运行时更改变量（有关详细信息，请参阅 docs/Command_Templates.md）。变量名不得使用大写字符。
#rename_existing:
#   此选项将导致宏覆盖现有的 G-Code 命令，并通过此处提供的名称提供命令的先前定义。这可用于覆盖内置 G-Code 命令。覆盖命令时应小心，因为它可能导致复杂且意外的结果。默认值为不覆盖现有 G-Code 命令。
#description: G-Code 宏
#   这将添加一个简短描述，用于 HELP 命令或使用自动完成功能时。默认值为 "G-Code 宏"。
```

### [delayed_gcode]

在设定延迟后执行 gcode。有关更多信息，请参阅 [命令模板指南](Command_Templates.md#delayed-gcodes) 和 [命令参考](G-Codes.md#delayed_gcode)。

```
[delayed_gcode my_delayed_gcode]
gcode:
#   延迟持续时间过后应执行的 G-Code 命令列表。支持 G-Code 模板。此参数必须提供。
#initial_duration: 0.0
#   初始延迟的持续时间（秒）。如果设置为非零值，delayed_gcode 将在打印机进入 "ready" 状态后指定的秒数后执行。这对于初始化过程或重复的 delayed_gcode 很有用。如果设置为 0，delayed_gcode 将在启动时执行。默认值为 0。
#description: 更新 delayed_gcode 的持续时间
#   这将添加一个简短描述，用于 HELP 命令或使用自动完成功能时。默认值为 "更新 delayed_gcode 的持续时间"。
```

### [save_variables]

支持将变量保存到磁盘，以便在重启后保留。有关更多信息，请参阅 [命令模板](Command_Templates.md#save-variables-to-disk) 和 [G-Code 参考](G-Codes.md#save_variables)。

```
[save_variables]
filename:
#   必需 - 提供一个用于将变量保存到磁盘的文件名，例如 ~/variables.cfg
```

### [idle_timeout]

空闲超时。空闲超时自动启用 - 添加显式的 idle_timeout 配置部分以更改默认设置。

```
[idle_timeout]
#gcode:
#   空闲超时时应执行的 G-Code 命令列表。有关 G-Code 格式，请参阅 docs/Command_Templates.md。默认值为运行 "TURN_OFF_HEATERS" 和 "M84"。
#timeout: 600
#   运行上述 G-Code 命令之前的空闲时间（秒）。设置为 0 以禁用超时功能。默认值为 600 秒。
```

## 可选 G-Code 功能

### [virtual_sdcard]

如果主机速度不够快，无法很好地运行 OctoPrint，虚拟 sdcard 可能很有用。它允许 Kalico 主机软件直接使用标准 sdcard G-Code 命令（例如 M24）打印存储在主机目录中的 gcode 文件。

```
[virtual_sdcard]
path:
#   主机上本地目录的路径，用于查找 g-code 文件。这是一个只读目录（不支持 sdcard 文件写入）。可以将此指向 OctoPrint 的上传目录（通常为 ~/.octoprint/uploads/）。此参数必须提供。
#on_error_gcode:
#   报告错误时应执行的 G-Code 命令列表。有关 G-Code 格式，请参阅 docs/Command_Templates.md。默认值为运行 TURN_OFF_HEATERS。
#with_subdirs: False
#   启用菜单以及 M20 和 M23 命令的子目录扫描。默认值为 False。
```

### [sdcard_loop]

一些具有舞台清理功能的打印机（如零件弹出器或皮带打印机）可以找到循环使用 sdcard 文件段的方法。（例如，重复打印相同的零件，或为链条或其他重复图案重复零件的某个部分）。

有关支持的命令，请参阅 [命令参考](G-Codes.md#sdcard_loop)。有关 Marlin 兼容的 M808 G-Code 宏，请参阅 [sample-macros.cfg](../config/sample-macros.cfg) 文件。

```
[sdcard_loop]
```

### ⚠️ [force_move]

此模块在 Kalico 中默认启用！

支持手动移动步进电机以进行诊断。请注意，使用此功能可能使打印机处于无效状态 - 有关重要详细信息，请参阅 [命令参考](G-Codes.md#force_move)。

```
[force_move]
#enable_force_move: True
#   设置为 `True` 以启用 FORCE_MOVE 和 SET_KINEMATIC_POSITION 扩展 G-Code 命令。默认值为 `True`。
```

### [pause_resume]

暂停/恢复功能，支持位置捕获和恢复。有关更多信息，请参阅 [命令参考](G-Codes.md#pause_resume)。

```
[pause_resume]
#recover_velocity: 50.
#   启用捕获/恢复时，返回到捕获位置的速度（mm/s）。默认值为 50.0 mm/s。
```

### [firmware_retraction]

固件耗材回抽。这启用了许多切片器发出的 G10（回抽）和 G11（取消回抽）GCODE 命令。下面的参数提供启动默认值，尽管这些值可以通过 SET_RETRACTION [命令](G-Codes.md#firmware_retraction)）进行调整，允许按耗材设置和运行时调整。

```
[firmware_retraction]
#retract_length: 0.0
#   执行 G10 命令时回抽的耗材长度（mm）。执行 G11 命令时，unretract_length 是 retract_length 和 unretract_extra_length 的总和（见下文）。最小值和默认值均为 0 mm，这会禁用固件回抽。
#retract_speed: 20.0
#   耗材回抽移动的速度（mm/s）。此值通常设置得相对较高（>40 mm/s），除非是柔软和/或渗出的耗材，如 TPU 和 PETG（20 到 30 mm/s）。最小值为 1 mm/s，默认值为 20 mm/s。
#unretract_extra_length: 0.0
#   与回抽移动长度相比，取消回抽时添加到耗材移动的*额外*长度（mm）或要减去的长度。这允许预填喷嘴（正额外长度）或在取消回抽后延迟挤出（负长度）。后者可能有助于减少结块。最小值为 -1 mm（对于 1.75 mm 耗材为 2.41 mm3 体积），默认值为 0 mm。
#unretract_speed: 10.0
#   耗材取消回抽移动的速度（mm/s）。此参数并非特别关键，但通常低于 retract_speed。最小值为 1 mm/s，默认值为 10 mm/s。
#z_hop_height: 0.0
#   在回抽期间，喷嘴从打印件上垂直提升的高度，以防止在移动过程中与打印件碰撞。最小值为 0 mm，默认值为 0 mm，这会禁用 zhop 移动。如果 zhop 移动达到最大 z，则该值将减小。
#clear_zhop_on_z_moves: False
#   如果为 True，当工具头回抽时发送 Z 变化，z_hop 将被取消，直到下次回抽。否则，`z_hop_height` 将作为所有移动的偏移量应用。
```

### [gcode_arcs]

支持 gcode 圆弧（G2/G3）命令。

```
[gcode_arcs]
#resolution: 1.0
#   圆弧将被分成段。每段的长度将等于上面设置的分辨率（mm）。较低的值将产生更精细的圆弧，但也给您的机器带来更多的工作。小于配置值的圆弧将变成直线。默认值为 1mm。
```

### [respond]

此模块在 Kalico 中默认启用！

启用 "M118" 和 "RESPOND" 扩展 [命令](G-Codes.md#respond)。

```
[respond]
#default_type: echo
#   将 "M118" 和 "RESPOND" 输出的默认前缀设置为以下之一：
#       echo: "echo: "（这是默认值）
#       command: "// "
#       error: "!! "
#default_prefix: echo:
#   直接设置默认前缀。如果存在，此值将覆盖 "default_type"。
#enable_respond: True
#   设置为 `True` 以启用 M118 和 RESPOND 扩展 G-Code 命令。默认值为 `True`。
```

### [exclude_object]

此模块在 Kalico 中默认启用！

支持在打印过程中排除或取消单个对象。

有关其他信息，请参阅 [排除对象指南](Exclude_Object.md) 和 [命令参考](G-Codes.md#exclude_object)。有关 Marlin/RepRapFirmware 兼容的 M486 G-Code 宏，请参阅 [sample-macros.cfg](../config/sample-macros.cfg) 文件。

```
[exclude_object]
#enable_exclude_object: True
#   设置为 `True` 以启用 `EXCLUDE_OBJECT_*` 扩展 G-Code 命令。默认值为 `True`。
```

## 谐振补偿

### [input_shaper]

启用 [谐振补偿](Resonance_Compensation.md)。另请参阅 [命令参考](G-Codes.md#input_shaper)。

```
[input_shaper]
#shaper_freq_x: 0
#   X 轴输入整形器的频率（Hz）。这通常是输入整形器应抑制的 X 轴谐振频率。对于更复杂的整形器，如 2 驼峰和 3 驼峰 EI 输入整形器，此参数可以根据不同的考虑进行设置。默认值为 0，这会禁用 X 轴的输入整形。
#shaper_freq_y: 0
#   Y 轴输入整形器的频率（Hz）。这通常是输入整形器应抑制的 Y 轴谐振频率。对于更复杂的整形器，如 2 驼峰和 3 驼峰 EI 输入整形器，此参数可以根据不同的考虑进行设置。默认值为 0，这会禁用 Y 轴的输入整形。
#shaper_type: mzv
#   用于 X 和 Y 轴的输入整形器类型。支持的整形器有 zv、mzv、zvd、ei、2hump_ei 和 3hump_ei。默认值为 mzv 输入整形器。
#shaper_type_x:
#shaper_type_y:
#   如果未设置 shaper_type，这两个参数可用于为 X 和 Y 轴配置不同的输入整形器。支持的值与 shaper_type 参数相同。
#damping_ratio_x: 0.1
#damping_ratio_y: 0.1
#   输入整形器使用的 X 和 Y 轴振动阻尼比，以改善振动抑制。默认值为 0.1，这是大多数打印机的通用值。在大多数情况下，此参数不需要调整，不应更改。
```

### [adxl345]

支持 ADXL345 加速度计。此支持允许从传感器查询加速度计测量值。这启用 ACCELEROMETER_MEASURE 命令（有关更多信息，请参阅 [G-Codes](G-Codes.md#adxl345)）。默认芯片名称为 "default"，但可以指定一个显式名称（例如 [adxl345 my_chip_name]）。

```
[adxl345]
cs_pin:
#   传感器的 SPI 启用引脚。此参数必须提供。
#spi_speed: 5000000
#   与芯片通信时使用的 SPI 速度（hz）。默认值为 5000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   请参阅 "common SPI 设置" 部分以了解上述参数的描述。
#axes_map: x, y, z
#   打印机 X、Y 和 Z 轴各自的加速度计轴。如果加速度计的安装方向与打印机方向不匹配，这可能很有用。例如，可以将其设置为 "y, x, z" 以交换 X 和 Y 轴。如果加速度计方向相反（例如 "x, z, -y"），也可以反转一个轴。默认值为 "x, y, z"。
#rate: 3200
#   ADXL345 的输出数据速率。ADXL345 支持以下数据速率：3200、1600、800、400、200、100、50 和 25。请注意，不建议将此速率从默认值 3200 更改，低于 800 的速率将大大影响谐振测量的质量。
```

### [icm20948]

支持 icm20948 加速度计。

```
[icm20948]
#i2c_address:
#   默认值为 104 (0x68)。如果 AD0 为高，则为 0x69。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   请参阅 "common I2C 设置" 部分以了解上述参数的描述。默认 "i2c_speed" 为 400000。
#axes_map: x, y, z
#   有关此参数的信息，请参阅 "adxl345" 部分。
```

### [lis2dw]

支持 LIS2DW 加速度计。

```
[lis2dw]
#cs_pin:
#   传感器的 SPI 启用引脚。如果使用 SPI，则必须提供此参数。
#spi_speed: 5000000
#   与芯片通信时使用的 SPI 速度（hz）。默认值为 5000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   请参阅 "common SPI 设置" 部分以了解上述参数的描述。
#i2c_address:
#   默认值为 25 (0x19)。如果 SA0 为高，则为 24 (0x18)。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   请参阅 "common I2C 设置" 部分以了解上述参数的描述。默认 "i2c_speed" 为 400000。
#axes_map: x, y, z
#   有关此参数的信息，请参阅 "adxl345" 部分。
```

### [lis3dh]

支持 LIS3DH 加速度计。

```
[lis3dh]
#cs_pin:
#   传感器的 SPI 启用引脚。如果使用 SPI，则必须提供此参数。
#spi_speed: 5000000
#   与芯片通信时使用的 SPI 速度（hz）。默认值为 5000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   请参阅 "common SPI 设置" 部分以了解上述参数的描述。
#i2c_address:
#   默认值为 25 (0x19)。如果 SA0 为高，则为 24 (0x18)。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   请参阅 "common I2C 设置" 部分以了解上述参数的描述。默认 "i2c_speed" 为 400000。
#axes_map: x, y, z
#   有关此参数的信息，请参阅 "adxl345" 部分。
```

### [mpu9250]

支持 MPU-9250、MPU-9255、MPU-6515、MPU-6050 和 MPU-6500 加速度计（可以定义任意数量带有 "mpu9250" 前缀的部分）。

```
[mpu9250 my_accelerometer]
#i2c_address:
#   默认值为 104 (0x68)。如果 AD0 为高，则为 0x69。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   请参阅 "common I2C 设置" 部分以了解上述参数的描述。默认 "i2c_speed" 为 400000。
#axes_map: x, y, z
#   有关此参数的信息，请参阅 "adxl345" 部分。
```

### [resonance_tester]

支持谐振测试和自动输入整形器校准。要使用此模块的大部分功能，必须安装额外的软件依赖项；有关更多信息，请参阅 [测量谐振](Measuring_Resonances.md) 和 [命令参考](G-Codes.md#resonance_tester)。有关 `max_smoothing` 参数及其用法的更多信息，请参阅测量谐振指南的 [最大平滑](Measuring_Resonances.md#max-smoothing) 部分。

```
[resonance_tester]
#probe_points:
#   要测试谐振的点列表（每行一个点），X、Y、Z 坐标。至少需要一个点。确保所有点在 XY 平面上有一定的安全边距（约几厘米），并且工具头可以到达。
#accel_chips:
#   用于测量的加速度计芯片逗号分隔列表。例如，"accel_chips: adxl345 head, adxl345 bed" 将使用两个单独的加速度计芯片。如果指定此参数，则优先于其他加速度计参数。
#accel_chip:
#   用于测量的加速度计芯片名称。如果 adxl345 芯片未定义显式名称，则此参数可以简单地引用为 "accel_chip: adxl345"，否则还必须提供显式名称，例如 "accel_chip: adxl345 my_chip_name"。必须设置此参数、'accel_chips' 或以下两个参数之一。
#accel_chip_x:
#accel_chip_y:
#   用于每个轴测量的加速度计芯片名称。例如，在床移动打印机上，如果两个单独的加速度计安装在床（Y 轴）和工具头（X 轴）上，这可能很有用。这些参数与 'accel_chip' 参数格式相同。仅需提供 'accel_chips'、'accel_chip' 或这两个参数之一。
#max_smoothing:
#   在整形器自动校准（使用 'SHAPER_CALIBRATE' 命令）期间允许每个轴的最大输入整形器平滑度。默认情况下，未指定最大平滑度。有关使用此功能的更多详细信息，请参阅 Measuring_Resonances 指南。
#move_speed: 50
#   校准期间将工具头移动到测试点之间以及测试点之间的速度（mm/s）。默认值为 50。
#min_freq: 5
#   要测试谐振的最小频率。默认值为 5 Hz。
#max_freq: 133.33
```
#   测试共振的最大频率。默认值为133.33 Hz。
#accel_per_hz: 75
#   此参数用于确定测试特定频率时使用的加速度：accel = accel_per_hz * freq。值越高，
#   振荡能量越大。如果打印机上共振过强，可以设置为低于默认值的值。
#   然而，较低的值会使高频共振的测量精度降低。默认值为75
#   (mm/sec)。
#   使用扫描共振测试仪时，设置为60作为良好的基准值。
#hz_per_sec: 1
#   确定测试速度。当测试[min_freq, max_freq]范围内的所有频率时，
#   每秒频率增加hz_per_sec。较小的值使测试变慢，而较大的值
#   会降低测试精度。默认值为1.0
#   (Hz/sec == sec^-2)。
#sweeping_accel: 400
#   慢扫描移动的加速度。默认值为400 mm/sec^2。
#sweeping_period: 0
#   慢扫描移动的周期。避免设置为太小的非零值，以免污染测量结果。
#   要启用它，首先将其设置为1.2秒，这是一个良好的通用选择。
#   设置为0以禁用它。默认值为0。
```

## 配置文件辅助工具

### [board_pins]

板引脚别名（可以定义任意数量的"board_pins"前缀的节）。
用于定义微控制器上引脚的别名。

```
[board_pins my_aliases]
mcu: mcu
#   逗号分隔的微控制器列表，这些微控制器可以使用这些别名。
#   默认是将别名应用于主"mcu"。
aliases:
aliases_<name>:
#   为给定微控制器创建的"name=value"别名的逗号分隔列表。
#   例如，"EXP1_1=PE6"将为"PE6"引脚创建一个"EXP1_1"别名。
#   然而，如果"value"被"<>"括起来，则"name"被创建为保留引脚
#   （例如，"EXP1_9=<GND>"将保留"EXP1_9"）。
#   可以指定任意数量的以"aliases_"开头的选项。
```

### [include]

包含文件支持。可以从主打印机配置文件包含额外的配置文件。
也可以使用通配符（例如，"configs/*.cfg"，或"configs/**/*.cfg"，
如果使用python版本>=3.5）。

```
[include my_other_config.cfg]
```

### [duplicate_pin_override]

此工具允许在配置文件中多次定义单个微控制器引脚，
而不会进行正常的错误检查。这用于诊断和调试目的。
在Kalico支持多次使用相同引脚的地方不需要此节，
使用此覆盖可能会导致混淆和意外结果。
可以指定显式名称（例如，[duplicate_pin_override my_name]）
来定义多个实例。

```
[duplicate_pin_override]
pins:
#   逗号分隔的引脚列表，这些引脚可以在配置文件中多次使用
#   而无需进行正常的错误检查。必须提供此参数。
```

## 床探测硬件

### [probe]

Z高度探测器。可以定义此节以启用Z高度探测硬件。
启用此节后，PROBE和QUERY_PROBE扩展[g-code命令](G-Codes.md#probe)可用。
另请参阅[探测校准指南](Probe_Calibrate.md)。
探测器节还会创建一个虚拟"probe:z_virtual_endstop"引脚。
在使用探测器代替Z限位开关的笛卡尔式打印机上，
可以将stepper_z的endstop_pin设置为这个虚拟引脚。
如果使用"probe:z_virtual_endstop"，则不要在stepper_z配置节中
定义position_endstop。

```
[probe]
pin:
#   探测器检测引脚。如果引脚在与Z步进电机不同的微控制器上，
#   则启用"多微控制器归位"。必须提供此参数。
#deactivate_on_each_sample: True
#   确定在执行多次探测序列时，Kalico是否在每次探测尝试之间
#   执行停用gcode。默认值为True。
#x_offset: 0.0
#   探测器与喷嘴之间沿x轴的距离（单位为mm）。默认值为0。
#y_offset: 0.0
#   探测器与喷嘴之间沿y轴的距离（单位为mm）。默认值为0。
z_offset:
#   探测器触发时，床与喷嘴之间的距离（单位为mm）。
#   必须提供此参数。
#speed: 5.0
#   探测时Z轴的速度（单位为mm/s）。默认值为5mm/s。
#samples: 1
#   每个点探测的次数。探测到的z值将取平均值。
#   默认为探测1次。
#sample_retract_dist: 2.0
#   每次采样之间抬起工具头的距离（单位为mm）（如果采样次数超过一次）。
#   默认值为2mm。
#lift_speed:
#   在采样之间抬起探测器时Z轴的速度（单位为mm/s）。
#   默认使用与'speed'参数相同的值。
#samples_result: average
#   多次采样时的计算方法 - "median"或"average"。
#   默认值为average。
#samples_tolerance: 0.100
#   一个样本可能与其他样本不同的最大Z距离（单位为mm）。
#   如果超出此公差，则会报告错误或重新开始尝试
#   （参见samples_tolerance_retries）。默认值为0.100mm。
#samples_tolerance_retries: 0
#   如果发现超过samples_tolerance的样本，则重试的次数。
#   重试时，所有当前样本都被丢弃，探测尝试重新开始。
#   如果在给定重试次数内未获得有效的样本集，
#   则会报告错误。默认值为零，表示在第一个超过
#   samples_tolerance的样本时报告错误。
#activate_gcode:
#   在每次探测尝试之前执行的G-Code命令列表。
#   参见docs/Command_Templates.md了解G-Code格式。
#   如果探测器需要以某种方式激活，这可能很有用。
#   不要在此处发出任何移动工具头的命令（例如，G1）。
#   默认是在激活时不运行任何特殊的G-Code命令。
#deactivate_gcode:
#   在每次探测尝试完成后执行的G-Code命令列表。
#   参见docs/Command_Templates.md了解G-Code格式。
#   不要在此处发出任何移动工具头的命令。
#   默认是在停用时不运行任何特殊的G-Code命令。
#drop_first_result: False
#   设置为`True`将探测一次额外次数，并从计算中删除第一个样本。
#   这可以提高具有异常第一个样本的打印机的探测精度。
#⚠️ bad_probe_strategy: RETRY
#   当探测器尝试被探测器的质量检测逻辑认为是"不良"时应用的策略。
#   如果探测器不支持质量检测，则所有探测都被认为是良好的。
#   可选值：fail、ignore、retry或circle。
#   - fail：在第一个不良探测时立即停止并报错。
#   - ignore：无论质量如何都接受所有探测。
#   - retry：在相同位置重新尝试探测。
#   - circle：使用圆形偏移模式重新尝试探测以避免污染。
#   默认值为retry。
#⚠️ bad_probe_retries: 6
#   当检测到不良探测时，根据'bad_probe_strategy'进行的额外探测尝试次数。
#   设置为0以禁用重试。默认值为6。
#⚠️ retry_speed:
#   在重试时移动探测器的水平移动速度（单位为mm/s）。
#   如果未指定，默认值为'speed'的值。
#⚠️ nozzle_scrubber_gcode:
#   执行自定义喷嘴清洁例程的G-Code块。
#   此G代码可在PROBE重试之间和NOZZLE_CLEANUP命令中调用。
#   gcode模板接收以下参数：
#   - ATTEMPT：当前重试尝试编号
#   - RETRIES：配置的最大重试次数
#   - X, Y：当前工具头位置
#⚠️ scrubbing_frequency: 0
#   控制喷嘴清洁器响应不良探测的频率。
#   如果设置为正数N，则nozzle_scrubber_gcode将在每N次不良探测后调用。
#   1将在每次不良探测后运行清洁器。
#   0将禁用清洁。默认值为0。
```

### [nozzle_cleanup]

启用[NOZZLE_CLEANUP](G-Codes.md#nozzle_cleanup) gcode命令。
这会执行一个喷嘴清洁例程，通过在网格模式上探测来清除喷嘴上的渗出物。
要正常工作，您的探测器需要支持探测器质量检测，例如[load_cell_probe](#load_cell_probe)。
```
#samples: 3
#   在一个位置连续进行良好探测的次数才能成功。
#   默认值为3。
#stepover: 2.0
#   网格中探测位置之间的间距（单位为mm）。默认值为2mm。
#pattern_x: 10
#   沿X轴的探测位置数量。可以为负数。默认值为10。
#pattern_y: 4
#   沿Y轴的探测位置数量。可以为负数。默认值为4。
#
#如果未指定，这些配置值将从[probe]继承：
#speed:
#lift_speed:
#retry_speed:
#sample_retract_dist:
#nozzle_scrubber_gcode:
#scrubbing_frequency:
```


### [bltouch]

BLTouch探测器。可以定义此节（而不是probe节）以启用BLTouch探测器。
参见[BL-Touch指南](BLTouch.md)和[命令参考](G-Codes.md#bltouch)了解更多信息。
还会创建一个虚拟"probe:z_virtual_endstop"引脚（详见"probe"节）。

```
[bltouch]
sensor_pin:
#   连接到BLTouch传感器引脚的引脚。大多数BLTouch设备需要
#   传感器引脚上的上拉电阻（在引脚名称前加"^"）。
#   必须提供此参数。
control_pin:
#   连接到BLTouch控制引脚的引脚。必须提供此参数。
#pin_move_time: 0.680
#   等待BLTouch引脚向上或向下移动的时间量（单位为秒）。
#   默认值为0.680秒。
#stow_on_each_sample: True
#   确定在执行多次探测序列时，Kalico是否应该命令引脚
#   在每次探测尝试之间向上移动。在设置此值为False之前，
#   请阅读docs/BLTouch.md中的说明。默认值为True。
#probe_with_touch_mode: False
#   如果设置为True，则Kalico将以"touch_mode"模式进行探测。
#   默认值为False（以"pin_down"模式探测）。
#pin_up_reports_not_triggered: True
#   如果BLTouch在成功的"pin_up"命令后始终报告探测器处于
#   "not triggered"状态，则设置此项。所有正品BLTouch设备
#   都应为True。在设置此值为False之前，请阅读
#   docs/BLTouch.md中的说明。默认值为True。
#pin_up_touch_mode_reports_triggered: True
#   如果BLTouch在"pin_up"命令后跟"touch_mode"命令后
#   始终报告"triggered"状态，则设置此项。所有正品BLTouch设备
#   都应为True。在设置此值为False之前，请阅读
#   docs/BLTouch.md中的说明。默认值为True。
#set_output_mode:
#   请求BLTouch V3.0（及更高版本）上的特定传感器引脚输出模式。
#   此设置不应用于其他类型的探测器。
#   设置为"5V"以请求5伏的传感器引脚输出（仅当控制器板需要5V模式
#   且其输入信号线耐受5V时使用）。设置为"OD"以请求传感器引脚
#   输出使用开漏模式。默认是不请求输出模式。
#x_offset:
#y_offset:
#z_offset:
#speed:
#lift_speed:
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#   参见"probe"节了解这些参数的信息。
```

### ⚠️ [dockable_probe]

某些探测器通过磁性耦合到工具头，不使用时存放在停靠站中。
如果探测器使用磁铁连接并使用停靠站存储，则应定义此节
而不是probe节。参见[可停靠探测器指南](Dockable_Probe.md)
了解有关配置和设置的更详细信息。

```
[dockable_probe]
dock_position: 0,0,0
#   探测器停靠站相对于床原点的物理位置。
#   坐标指定为逗号分隔的X, Y, Z值列表。
#   某些停靠站设计与Z轴无关。
#   如果指定了Z，工具头将在X, Y坐标之前移动到Z位置。
#   此参数是必需的。
approach_position: 0,0,0
#   工具头在进入停靠站之前需要位于的X, Y, Z位置，
#   以便探测器正确对齐以进行连接或断开。
#   如果指定了Z，工具头将在X, Y坐标之前移动到Z位置。
#   此参数是必需的。
detach_position: 0,0,0
#   与approach_position类似，detach_position是探测器
#   停靠后工具头移动到的坐标。
#   对于磁性耦合的探测器，这通常与approach_position垂直，
#   方向不会导致工具与打印机碰撞。
#   如果指定了Z，工具头将在X, Y坐标之前移动到Z位置。
#   此参数是必需的。
#extract_position: 0,0,0
#   与approach_position类似，extract_position是工具头
#   从停靠站提取探测器时移动到的坐标。
#   如果指定了Z，工具头将在X, Y坐标之前移动到Z位置。
#   默认值为approach_probe值。
#insert_position: 0,0,0
#   与extract_position类似，insert_position是工具头
#   将探测器插入停靠站之前移动到的坐标。
#   如果指定了Z，工具头将在X, Y坐标之前移动到Z位置。
#   默认值为extract_probe值。
#safe_dock_distance :
#   此设置定义在ATTACH/DETACH_PROBE命令期间停靠站周围的安全区域。
#   在区域内时，工具头会在到达approach或insert位置之前移开。
#   默认值是approach、detach、insert位置到停靠站的最小距离。
#   它只能低于默认值。
#safe_position : approach_position
#   安全位置，确保MOVE_AVOIDING_DOCK行程不会将工具头移出范围。
#z_hop: 15.0
#   在连接/断开探测器之前抬起Z轴的距离（单位为mm）。
#   如果Z轴已经归位且当前Z位置小于`z_hop`，则将头部
#   抬高到`z_hop`的高度。如果Z轴尚未归位，则将头部
#   抬高`z_hop`。默认是不实现Z hop。
#restore_toolhead: True
#   当为True时，工具头位置将恢复到连接/断开移动之前的位置。
#   默认值为True。
#dock_retries:
#   在报错并中止探测之前，尝试连接/停靠探测器的次数。
#   默认值为0。
#auto_attach_detach: False
#   在需要探测器的操作期间启用/禁用探测器的自动连接/断开。
#   默认值为True。
#attach_speed:
#detach_speed:
#travel_speed:
#   移动期间使用的可选速度。
#   默认是使用`probe`的`speed`或5.0。
#check_open_attach:
#   归位前应验证探测器状态。将此选项设置为true将在连接后检查
#   探测器"限位开关"是否为"open"，如果不是则中止探测，
#   并在停靠后检查"triggered"。
#   相反，将此设置为false，探测器连接后应读取"triggered"，
#   停靠后应读取"open"。如果不是，则探测将中止。
#probe_sense_pin:
#   可以定义此辅助引脚来确定连接状态，而不是check_open_attach。
#dock_sense_pin:
#   可以定义此辅助引脚来确定停靠状态，除了probe_sense_pin或
#   check_open_attach之外。
#pre_attach_gcode:
#   在探测器连接之前运行的代码
#post_attach_gcode:
#   在探测器连接之后运行的代码
#pre_detach_gcode:
#   在探测器断开之前运行的代码
#post_detach_gcode:
#   在探测器断开之后运行的代码
#
#x_offset:
#y_offset:
#z_offset:
#lift_speed:
#speed:
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#activate_gcode:
#deactivate_gcode:
#   参见"probe"节了解这些参数的信息。
```

### [smart_effector]

来自Duet3d的"Smart Effector"使用力传感器实现Z探测器。
可以定义此节而不是`[probe]`以启用Smart Effector特定功能。
这还会启用[运行时命令](G-Codes.md#smart_effector)来调整
Smart Effector的参数。

```
[smart_effector]
pin:
#   连接到Smart Effector Z探测器输出引脚（引脚5）的引脚。
#   注意，板上的上拉电阻通常不需要。但是，如果输出引脚
#   连接到具有上拉电阻的板引脚，则该电阻必须是高值
#   （例如，10K欧姆或更高）。某些板在Z探测器输入上具有
#   低值上拉电阻，这可能导致探测器始终处于触发状态。
#   在这种情况下，将Smart Effector连接到板上的不同引脚。
#   必须提供此参数。
#control_pin:
#   连接到Smart Effector控制输入引脚（引脚7）的引脚。
#   如果提供，Smart Effector灵敏度编程命令将可用。
#probe_accel:
#   如果设置，限制探测移动的加速度（单位为mm/sec^2）。
#   探测移动开始时突然的大加速度可能导致虚假的探测器触发，
#   尤其是如果热端较重。为了防止这种情况，可能需要通过
#   此参数降低探测移动的加速度。
#recovery_time: 0.4
#   行程移动和探测移动之间的延迟，单位为秒。
#   探测前的快速行程移动可能导致虚假的探测器触发。
#   如果未设置延迟，这可能导致'Probe triggered prior to movement'错误。
#   值0禁用恢复延迟。默认值为0.4。
#x_offset:
#y_offset:
#   应保持未设置（或设置为0）。
z_offset:
#   探测器的触发高度。从-0.1（mm）开始，稍后使用
#   `PROBE_CALIBRATE`命令调整。必须提供此参数。
#speed:
#   探测时Z轴的速度（单位为mm/s）。建议从20 mm/s的探测速度开始，
#   根据需要进行调整以提高探测器触发的精度和重复性。
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#activate_gcode:
#deactivate_gcode:
#deactivate_on_each_sample:
#   参见"probe"节了解上述参数的更多信息。
```

### [probe_eddy_current]

支持涡流感应探测器。可以定义此节（而不是probe节）以启用此探测器。
参见[命令参考](G-Codes.md#probe_eddy_current)了解更多信息。

```
[probe_eddy_current my_eddy_probe]
sensor_type: ldc1612
#   用于执行涡流测量的传感器芯片。必须提供此参数并设置为ldc1612。
#frequency:
#   LDC1612芯片的外部晶振频率（单位为Hz）。默认值为12000000。
#intb_pin:
#   连接到ldc1612传感器INTB引脚的MCU gpio引脚（如果可用）。
#   默认是不使用INTB引脚。
#z_offset:
#   探测尝试应停止的喷嘴与床之间的标称距离（单位为mm）。
#   必须提供此参数。
#i2c_address:
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   传感器芯片的i2c设置。参见"common I2C settings"节
#   了解上述参数的描述。
#x_offset:
#y_offset:
#speed:
#lift_speed:
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#   参见"probe"节了解这些参数的信息。
```

### [axis_twist_compensation]

用于补偿X或Y龙门架扭曲导致的探测读数不准确的工具。
参见[轴扭曲补偿指南](Axis_Twist_Compensation.md)
了解有关症状、配置和设置的更详细信息。

```
[axis_twist_compensation]
#speed: 50
#   校准期间非探测移动的速度（单位为mm/s）。默认值为50。
#horizontal_move_z: 5
#   开始探测操作之前，头部应被命令移动到的高度（单位为mm）。
#   默认值为5。
calibrate_start_x: 20
#   定义校准的最小X坐标
#   这应该是将喷嘴定位在校准起始位置的X坐标。
calibrate_end_x: 200
#   定义校准的最大X坐标
#   这应该是将喷嘴定位在校准结束位置的X坐标。
calibrate_y: 112.5
#   定义校准的Y坐标
#   这应该是在校准过程中定位喷嘴的Y坐标。
#   建议将此参数设置在床的中心附近。

# 对于Y轴扭曲补偿，请指定以下参数：
calibrate_start_y: ...
#   定义校准的最小Y坐标
#   这应该是将喷嘴定位在Y轴校准起始位置的Y坐标。
#   如果补偿Y轴扭曲，则必须提供此参数。
calibrate_end_y: ...
#   定义校准的最大Y坐标
#   这应该是将喷嘴定位在校准结束位置的Y坐标。
#   如果补偿Y轴扭曲，则必须提供此参数。
calibrate_x: ...
#   定义Y轴扭曲补偿的校准X坐标
#   这应该是在Y轴扭曲补偿校准过程中定位喷嘴的X坐标。
#   必须提供此参数，建议将其设置在床的中心附近。

# 以下参数在运行AXIS_TWIST_COMPENSATION_CALIBRATE后
# 由SAVE_CONFIG自动保存，通常不应手动修改。
# 注意：如果设置了z_compensations，则还必须设置compensation_start_x
# 和compensation_end_x。类似地，zy_compensations需要
# compensation_start_y和compensation_end_y。
#z_compensations:
#   X轴扭曲的Z偏移补偿值的逗号分隔列表。
#   这些表示从compensation_start_x到compensation_end_x
#   均匀分布点的Z调整值。在X轴校准期间自动生成。
#   需要设置compensation_start_x和compensation_end_x。
#   默认为空列表。
#compensation_start_x:
#   X轴扭曲补偿的起始X坐标。
#   在校准期间自动设置。默认值为未设置。
#compensation_end_x:
#   X轴扭曲补偿的结束X坐标。
#   在校准期间自动设置。默认值为未设置。
#zy_compensations:
#   Y轴扭曲的Z偏移补偿值的逗号分隔列表。
#   类似于z_compensations但用于Y轴。在Y轴校准（AXIS=Y）期间自动生成。
#   需要设置compensation_start_y和compensation_end_y。
#   默认为空列表。
#compensation_start_y:
#   Y轴扭曲补偿的起始Y坐标。
#   在Y轴校准期间自动设置。默认值为未设置。
#compensation_end_y:
#   Y轴扭曲补偿的结束Y坐标。
#   在Y轴校准期间自动设置。默认值为未设置。
```

### ⚠️ [z_calibration]

自动Z偏移校准。如果打印机能够自动校准喷嘴偏移，可以定义此节。
参见[Z-校准指南](Z_Calibration.md)了解更多信息。

```
[z_calibration]
nozzle_xy_position:
#   喷嘴在Z限位开关上点击的X, Y坐标（例如，100,100）。
switch_xy_position:
#   探测器开关体在Z限位开关上点击的X, Y坐标（例如，100,100）。
bed_xy_position: 默认来自bed_mesh的relative_reference_index
#   打印表面（例如，中心点）被探测的X, Y坐标（例如，100,100）。
#   这些坐标将由探测器的X和Y偏移进行调整。
#   默认值是配置的bed_mesh的relative_reference_index（如果已配置）。
#   可以在运行时更改relative_reference_index或使用
#   CALIBRATE_Z的GCode参数BED_POSITION。
switch_offset:
#   使用的磁性探测器开关的触发点偏移。
#   较大的值将使喷嘴更靠近床。
#   这需要手动找出。稍后在本节中介绍。
max_deviation: 1.0
#   计算偏移允许的最大偏差。
#   如果偏移超过此值，它将停止！
#   默认值为1.0 mm。
samples: 默认来自"probe:samples"节
#   每个点探测的次数。探测到的z值将取平均值。
#   默认值来自探测器的配置。
samples_tolerance: 默认来自"probe:samples_tolerance"节
#   一个样本可能与其他样本不同的最大Z距离（单位为mm）。
#   默认值来自探测器的配置。
samples_tolerance_retries: 默认来自"probe:samples_tolerance_retries"节
#   如果发现超过samples_tolerance的样本，则重试的次数。
#   默认值来自探测器的配置。
samples_result: 默认来自"probe:samples_result"节
#   多次采样时的计算方法 - "median"或"average"。
#   默认值来自探测器的配置。
clearance: 2 * 来自"probe:z_offset"节的z_offset
#   在移动到下一个位置之前向上移动的距离（单位为mm）。
#   默认值为探测器配置中z_offset的两倍。
position_min: 默认来自"stepper_z:position_min"节。
#   用于探测移动的最小有效距离（单位为mm）。
#   默认值来自Z导轨配置。
speed: 50
#   X和Y的移动速度。默认值为50 mm/s。
lift_speed: 默认来自"probe:lift_speed"节
#   在采样和间隙移动之间抬起探测器时Z轴的速度（单位为mm/s）。
#   默认值来自探测器的配置。
probing_speed: 默认来自"stepper_z:homing_speed"节。
#   当probing_first_fast激活时使用的快速探测速度（单位为mm/s）。
#   默认值来自Z导轨配置。
probing_second_speed: 默认来自"stepper_z:second_homing_speed"节。
#   用于探测记录样本的较慢速度（单位为mm/s）。
#   默认值为Z导轨配置的second_homing_speed。
probing_retract_dist: 默认来自"stepper_z:homing_retract_dist"节。
#   在探测下一个样本之前回缩的距离（单位为mm）。
#   默认值为Z导轨配置的homing_retract_dist。
probing_first_fast: false
#   如果为true，则通过探测速度更快地完成第一次探测。
#   这是为了更快地下降，结果不记录为探测样本。
#   默认值为false。
start_gcode:
#   在每个校准命令之前执行的G-Code命令列表。
#   参见docs/Command_Templates.md了解G-Code格式。
#   这可用于连接探测器。
before_switch_gcode:
#   在磁性探测器上每次探测之前执行的G-Code命令列表。
#   参见docs/Command_Templates.md了解G-Code格式。
#   这可用于在喷嘴上探测后、在磁性探测器上探测之前连接探测器。
end_gcode:
#   在每个校准命令之后执行的G-Code命令列表。
#   参见docs/Command_Templates.md了解G-Code格式。
#   这可用于之后断开探测器。
```

## 额外的步进电机和挤出机

### [stepper_z1]

多步进轴。在笛卡尔式打印机上，控制给定轴的步进电机可以有
额外的配置块，定义应与主步进电机同步运行的步进电机。
可以定义任意数量的以数字后缀开头的节（从1开始），
（例如，"stepper_z1"、"stepper_z2"等）。

```
[stepper_z1]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   参见"stepper"节了解上述参数的定义。
#endstop_pin:
#   如果为额外的步进电机定义了endstop_pin，则该步进电机将
#   归位直到限位开关被触发。否则，该步进电机将归位直到
#   该轴主步进电机上的限位开关被触发。
```

### [extruder1]

在多挤出机打印机中，为每个额外的挤出机添加一个额外的挤出机节。
额外的挤出机节应命名为"extruder1"、"extruder2"、"extruder3"等。
参见"extruder"节了解可用参数的描述。

参见[sample-multi-extruder.cfg](../config/sample-multi-extruder.cfg)
了解示例配置。

```
[extruder1]
#step_pin:
#dir_pin:
#...
#   参见"extruder"节了解可用的步进电机和加热器参数。
#shared_heater:
#   此选项已弃用，不应再指定。
```

### [dual_carriage]

支持在单个轴上具有双滑车的笛卡尔和混合corexy/z打印机。
滑车模式可以通过SET_DUAL_CARRIAGE扩展g-code命令设置。
例如，"SET_DUAL_CARRIAGE CARRIAGE=1"命令将激活此节中定义的
滑车（CARRIAGE=0将激活返回到主滑车）。
双滑车支持通常与额外的挤出机结合使用 - SET_DUAL_CARRIAGE命令
通常与ACTIVATE_EXTRUDER命令同时调用。确保在停用期间停放滑车。
注意，在G28归位期间，通常首先归位主滑车，然后归位
`[dual_carriage]`配置节中定义的滑车。
但是，如果两个滑车都沿正方向归位且[dual_carriage]滑车的
`position_endstop`大于主滑车，或者如果两个滑车都沿负方向归位
且`[dual_carriage]`滑车的`position_endstop`小于主滑车，
则`[dual_carriage]`滑车将首先归位。

此外，可以使用"SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY"或
"SET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR"命令来激活双滑车的
复制或镜像模式，在这种情况下，它将相应地跟随滑车0的运动。
这些命令可用于同时打印两个零件 - 两个相同的零件（在COPY模式下）
或镜像零件（在MIRROR模式下）。注意，COPY和MIRROR模式还需要
适当配置双滑车上的挤出机，这通常可以通过
"SYNC_EXTRUDER_MOTION MOTION_QUEUE=extruder EXTRUDER=\<dual_carriage_extruder\>"
或类似命令实现。

参见[sample-idex.cfg](../config/sample-idex.cfg)了解示例配置。

```
[dual_carriage]
axis:
#   此额外滑车所在的轴（x或y）。必须提供此参数。
#safe_distance:
#   强制执行双滑车和主滑车之间的最小距离（单位为mm）。
#   如果执行的G-Code命令将使滑车比指定的限制更接近，
#   则该命令将被拒绝并报错。如果未提供safe_distance，
#   则将从双滑车和主滑车的position_min和position_max推断。
#   如果设置为0（或safe_distance未设置且主滑车和双滑车的
#   position_min和position_max相同），则滑车接近检查将被禁用。
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#endstop_pin:
#position_endstop:
#position_min:
#position_max:
#   参见"stepper"节了解上述参数的定义。
```

### [extruder_stepper]

支持与挤出机运动同步的额外步进电机（可以定义任意数量的
"extruder_stepper"前缀的节）。

参见[命令参考](G-Codes.md#extruder)了解更多信息。

```
[extruder_stepper my_extra_stepper]
extruder:
#   此步进电机同步到的挤出机。如果设置为空字符串，
#   则该步进电机将不会与挤出机同步。必须提供此参数。
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   参见"stepper"节了解上述参数的定义。
```

### [manual_stepper]

手动步进电机（可以定义任意数量的"manual_stepper"前缀的节）。
这些是通过MANUAL_STEPPER g-code命令控制的步进电机。
例如："MANUAL_STEPPER STEPPER=my_stepper MOVE=10 SPEED=5"。
参见[G-Codes](G-Codes.md#manual_stepper)文件了解
MANUAL_STEPPER命令的描述。这些步进电机不连接到正常的打印机运动学。

```
[manual_stepper my_stepper]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   参见"stepper"节了解这些参数的描述。
#velocity:
#   设置步进电机的默认速度（单位为mm/s）。
#   如果MANUAL_STEPPER命令未指定SPEED参数，将使用此值。
#   默认值为5mm/s。
#accel:
#   设置步进电机的默认加速度（单位为mm/s^2）。
#   零加速度将导致没有加速度。如果MANUAL_STEPPER命令未指定
#   ACCEL参数，将使用此值。默认值为零。
#endstop_pin:
#   限位开关检测引脚。如果指定，则可以通过在MANUAL_STEPPER
#   移动命令中添加STOP_ON_ENDSTOP参数来执行"归位移动"。
```

### [mixing_extruder]

具有n-in-1-out混合喷嘴的混合打印头。激活后，额外的G-Code命令可用。
参见[G-Codes](G-Codes.md#mixing_extruder)了解额外命令的详细描述。

```
[mixing_extruder]
#steppers:
#   哪些步进电机送入热端/喷头。提供一个逗号
#   分隔的列表，例如 "extruder,extruder1,extruder2"。应为
#   extruder 部分或 extruder_stepper 部分的名称
#   此配置是必需的。
#extruder_name:
#   用于同步 steppers 列表中步进电机的挤出机名称。
#   默认是 "steppers" 列表中的第一个条目。
```


## 自定义加热器和传感器

### [verify_heater]

加热器和温度传感器验证。对于打印机上配置的每个加热器，
都会自动启用加热器验证。使用 verify_heater 部分来更改默认设置。

```
[verify_heater heater_config_name]
#max_error: 120
#   在触发错误之前的最大"累积温度误差"。较小的值导致更严格的检查，较大的
#   值允许在报告错误之前有更多时间。具体来说，温度每秒检查一次，如果
#   接近目标温度，则内部"错误计数器"被重置；否则，如果温度低于
#   目标范围，则计数器增加报告温度与该范围的差值。如果计数器
#   超过此 "max_error"，则会触发错误。默认为 120。
#check_gain_time:
#   这控制初始加热期间的加热器验证。较小的值导致更严格的检查，较大的值允许
#   在报告错误之前有更多时间。具体来说，在初始加热期间，只要加热器在
#   此时间范围内（以秒为单位）增加温度，则内部"错误计数器"被重置。
#   挤出机默认为 20 秒，heater_bed 默认为 60 秒。
#hysteresis: 5
#   考虑在目标范围内的目标温度最大温差（摄氏度）。这控制 max_error 范围检查。
#   很少自定义此值。默认为 5。
#heating_gain: 2
#   在 check_gain_time 检查期间加热器必须增加的最小温度（摄氏度）。
#   很少自定义此值。默认为 2。
```

### [homing_heaters]

在归位或探测轴时禁用加热器的工具。

```
[homing_heaters]
#steppers:
#   一个逗号分隔的步进电机列表，这些步进电机应导致加热器被禁用。
#   默认是为任何归位/探测移动禁用加热器。
#   典型示例：stepper_z
#heaters:
#   一个逗号分隔的加热器列表，在归位/探测移动期间禁用。默认是禁用所有加热器。
#   典型示例：extruder, heater_bed
```

### [thermistor]

自定义热敏电阻（可以定义任意数量带有 "thermistor" 前缀的部分）。自定义热敏电阻可以在
加热器配置部分的 sensor_type 字段中使用。（例如，如果定义了
"[thermistor my_thermistor]" 部分，则在定义加热器时可以使用 "sensor_type: my_thermistor"。）
确保将热敏电阻部分放在配置文件中其首次在加热器部分使用之前。

```
[thermistor my_thermistor]
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#temperature3:
#resistance3:
#   在给定温度（摄氏度）下的三个电阻测量值（欧姆）。这三个测量值将用于计算
#   热敏电阻的 Steinhart-Hart 系数。使用 Steinhart-Hart 定义热敏电阻时
#   必须提供这些参数。
#beta:
#   或者，可以定义 temperature1、resistance1 和 beta 来定义热敏电阻参数。
#   使用 "beta" 定义热敏电阻时必须提供此参数。
```

### [adc_temperature]

自定义 ADC 温度传感器（可以定义任意数量带有 "adc_temperature" 前缀的部分）。这允许定义一个自定义
温度传感器，该传感器测量模数转换器（ADC）引脚上的电压，并使用一组
配置的温度/电压（或温度/电阻）测量值之间的线性插值来确定温度。生成的传感器可以
用作加热器部分中的 sensor_type。（例如，如果定义了 "[adc_temperature my_sensor]"
部分，则在定义加热器时可以使用 "sensor_type: my_sensor"。）确保将传感器部分放在
配置文件中其首次在加热器部分使用之前。

```
[adc_temperature my_sensor]
#temperature1:
#voltage1:
#temperature2:
#voltage2:
#...
#   一组温度（摄氏度）和电压（伏特），用作转换温度时的参考。
#   使用此传感器的加热器部分也可以指定 adc_voltage 和 voltage_offset
#   参数来定义 ADC 电压（详见 "Common temperature amplifiers" 部分）。
#   必须至少提供两个测量值。
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#...
#   或者，可以指定一组温度（摄氏度）和电阻（欧姆），用作转换温度时的参考。
#   使用此传感器的加热器部分也可以指定 pullup_resistor 参数
#   （详见 "extruder" 部分）。必须至少提供两个测量值。
```

### [heater_generic]

通用加热器（可以定义任意数量带有 "heater_generic" 前缀的部分）。这些加热器的行为类似于标准
加热器（挤出机、加热床）。使用 SET_HEATER_TEMPERATURE 命令（详见 [G-Codes](G-Codes.md#heaters)）来设置目标温度。

```
[heater_generic my_generic_heater]
#gcode_id:
#   在 M105 命令中报告温度时使用的 id。必须提供此参数。
#heater_pin:
#max_power:
#sensor_type:
#sensor_pin:
#smooth_time:
#control:
#pid_Kp:
#pid_Ki:
#pid_Kd:
#pwm_cycle_time:
#lost_update_tolerance:
#min_temp:
#max_temp:
#   上述参数的定义请参见 "extruder" 部分。
```

### [temperature_sensor]

通用温度传感器。可以定义任意数量的额外温度传感器，这些传感器通过 M105 命令报告。

```
[temperature_sensor my_sensor]
#sensor_type:
#sensor_pin:
#min_temp:
#max_temp:
#   上述参数的定义请参见 "extruder" 部分。
#gcode_id:
#   此参数的定义请参见 "heater_generic" 部分。
```

## 温度传感器

Kalico 包含许多类型温度传感器的定义。
这些传感器可以在任何需要温度传感器的配置部分中使用（例如 `[extruder]` 或 `[heater_bed]` 部分）。

### 常见热敏电阻

常见热敏电阻。以下参数在使用这些传感器之一的加热器部分中可用。

```
sensor_type:
#   以下之一："EPCOS 100K B57560G104F"、"ATC Semitec 104GT-2"、
#   "ATC Semitec 104NT-4-R025H42G"、"Generic 3950"、
#   "Honeywell 100K 135-104LAG-J01"、"NTC 100K MGB18-104F39050L32"、
#   "SliceEngineering 450" 或 "TDK NTCG104LH104JT1"
sensor_pin:
#   连接到热敏电阻的模拟输入引脚。必须提供此参数。
#pullup_resistor: 4700
#   连接到热敏电阻的上拉电阻的阻值（欧姆）。默认为 4700 欧姆。
#inline_resistor: 0
#   与热敏电阻串联的额外（非热敏）电阻的阻值（欧姆）。很少设置此值。默认为 0 欧姆。
```

### 常见温度放大器

常见温度放大器。以下参数在使用这些传感器之一的加热器部分中可用。

```
sensor_type:
#   以下之一："PT100 INA826"、"AD595"、"AD597"、"AD8494"、"AD8495"、
#   "AD8496" 或 "AD8497"。
sensor_pin:
#   连接到传感器的模拟输入引脚。必须提供此参数。
#adc_voltage: 5.0
#   ADC 比较电压（伏特）。默认为 5 伏。
#voltage_offset: 0
#   ADC 电压偏移（伏特）。默认为 0。
```

### 直接连接的 PT1000 传感器

直接连接的 PT1000 传感器。以下参数在使用这些传感器之一的加热器部分中可用。

```
sensor_type: PT1000
sensor_pin:
#   连接到传感器的模拟输入引脚。必须提供此参数。
#pullup_resistor: 4700
#   连接到传感器的上拉电阻的阻值（欧姆）。默认为 4700 欧姆。
```

### MAXxxxxx 温度传感器

MAXxxxxx 串行外设接口（SPI）温度传感器。以下参数在使用这些传感器类型之一的加热器部分中可用。

```
sensor_type:
#   以下之一："MAX6675"、"MAX31855"、"MAX31856" 或 "MAX31865"。
sensor_pin:
#   传感器芯片的片选线。必须提供此参数。
#spi_speed: 4000000
#   与芯片通信时使用的 SPI 速度（Hz）。默认为 4000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   上述参数的描述请参见 "common SPI settings" 部分。
#tc_type: K
#tc_use_50Hz_filter: False
#tc_averaging_count: 1
#   上述参数控制 MAX31856 芯片的传感器参数。每个参数的默认值在上面列表中参数名称旁边。
#rtd_nominal_r: 100
#rtd_reference_r: 430
#rtd_num_of_wires: 2
#rtd_use_50Hz_filter: False
#   上述参数控制 MAX31865 芯片的传感器参数。每个参数的默认值在上面列表中参数名称旁边。
```

### BMP180/BMP280/BME280/BMP388/BME680 温度传感器

BMP180/BMP280/BME280/BMP388/BME680 双线接口（I2C）环境传感器。
请注意，这些传感器不适用于挤出机和加热床，而是用于监控环境温度（°C）、
压力（hPa）、相对湿度，以及 BME680 的气体水平。有关可用于报告压力和湿度（除了
温度）的 gcode_macro，请参见 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: BME280
#i2c_address:
#   默认为 118（0x76）。BMP180、BMP388 和一些 BME280 传感器
#   的地址为 119（0x77）。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   上述参数的描述请参见 "common I2C settings" 部分。
```

### AHT10/AHT20/AHT21/AHT30 温度传感器

AHT10/AHT20/AHT21/AHT30 双线接口（I2C）环境传感器。
请注意，这些传感器不适用于挤出机和加热床，而是用于监控环境温度（°C）和
相对湿度。有关可用于报告湿度（除了温度）的 gcode_macro，请参见
[sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: AHT10
#   必须为 "AHT1X"、"AHT2X"、"AHT3X"
#   一些 AHT20 传感器可以使用 "AHT1X"
#i2c_address:
#   默认为 56（0x38）。一些 AHT10 传感器可以选择使用
#   57（0x39）通过移动电阻器。
#i2c_mcu:
#i2c_bus:
#i2c_speed:
#   上述参数的描述请参见 "common I2C settings" 部分。
#aht10_report_time:
#   读数之间的间隔（秒）。默认为 30，最小为 5
```

### HTU21D 传感器

HTU21D 系列双线接口（I2C）环境传感器。请注意，
此传感器不适用于挤出机和加热床，而是用于监控环境温度（°C）和相对
湿度。有关可用于报告湿度（除了温度）的 gcode_macro，请参见
[sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type:
#   必须为 "HTU21D"、"SI7013"、"SI7020"、"SI7021" 或 "SHT21"
#i2c_address:
#   默认为 64（0x40）。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   上述参数的描述请参见 "common I2C settings" 部分。
#htu21d_hold_master:
#   传感器是否可以在读取时保持 I2C 总线。如果为 True，则在读取期间无法执行其他
#   总线通信。默认为 False。
#htu21d_resolution:
#   温度和湿度读数的分辨率。
#   有效值为：
#    'TEMP14_HUM12' -> 温度 14 位，湿度 12 位
#    'TEMP13_HUM10' -> 温度 13 位，湿度 10 位
#    'TEMP12_HUM08' -> 温度 12 位，湿度 08 位
#    'TEMP11_HUM11' -> 温度 11 位，湿度 11 位
#   默认为："TEMP11_HUM11"
#htu21d_report_time:
#   读数之间的间隔（秒）。默认为 30
```

### SHT3X 传感器

SHT3X 系列双线接口（I2C）环境传感器。这些传感器
的范围为 -55~125°C，因此可用于例如腔室温度监控。它们还可以用作简单的风扇/加热器控制器。

```
sensor_type: SHT3X
#i2c_address:
#   默认为 68（0x44）。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   上述参数的描述请参见 "common I2C settings" 部分。
```

### LM75 温度传感器

LM75/LM75A 双线（I2C）连接的温度传感器。这些传感器
的范围为 -55~125°C，因此可用于例如腔室温度监控。它们还可以用作简单的风扇/加热器控制器。

```
sensor_type: LM75
#i2c_address:
#   默认为 72（0x48）。正常范围是 72-79（0x48-0x4F），地址的 3
#   个低位通过芯片上的引脚配置（通常通过跳线或硬连线）。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   上述参数的描述请参见 "common I2C settings" 部分。
#lm75_report_time:
#   读数之间的间隔（秒）。默认为 0.8，最小为 0.5。
```

### 内置微控制器温度传感器

atsam、atsamd、stm32 和 rp2040 微控制器包含一个内部
温度传感器。可以使用 "temperature_mcu" 传感器来监控这些温度。

```
sensor_type: temperature_mcu
#sensor_mcu: mcu
#   要读取的微控制器。默认为 "mcu"。
#reference_voltage:
#   微控制器 ADC 的参考电压。默认为 3.3
#sensor_temperature1:
#sensor_adc1:
#   指定以上两个参数（摄氏度温度和 0.0 到 1.0 之间的浮点数 ADC 值）来校准
#   微控制器温度。这可能会提高某些芯片上报告的温度精度。获取此
#   校准信息的一种典型方法是完全切断打印机电源几小时
#   （以确保其处于环境温度），然后通电并使用 QUERY_ADC 命令
#   获取 ADC 测量值。使用打印机上的其他温度传感器找到相应的环境温度。
#   默认是使用微控制器上的出厂校准数据（如果适用）或微控制器规范中的
#   标称值。
#sensor_temperature2:
#sensor_adc2:
#   如果指定了 sensor_temperature1/sensor_adc1，则还可以指定
#   sensor_temperature2/sensor_adc2 校准数据。这样做可能会提供校准的"温度斜率"信息。
#   默认是使用微控制器上的出厂校准数据（如果适用）或微控制器规范中的
#   标称值。
```

### 主机温度传感器

来自运行主机软件的机器（例如 Raspberry Pi）的温度。

```
sensor_type: temperature_host
#sensor_path:
#   温度系统文件的路径。默认为 "/sys/class/thermal/thermal_zone0/temp"，
#   这是 Raspberry Pi 计算机上的温度系统文件。
```

### DS18B20 温度传感器

DS18B20 是一种单总线（w1）数字温度传感器。请注意，此传感器不适用于挤出机和加热床，而是用于监控
环境温度（°C）。这些传感器的范围高达 125°C，因此可用于
例如腔室温度监控。它们还可以用作简单的风扇/加热器控制器。DS18B20 传感器仅在"主机 mcu"上支持，
例如 Raspberry Pi。必须安装 w1-gpio Linux 内核模块。

```
sensor_type: DS18B20
serial_no:
#   每个单总线设备都有一个用于标识设备的唯一序列号，
#   通常格式为 28-031674b175ff。必须提供此参数。
#   可以使用以下 Linux 命令列出连接的单总线设备：
#   ls /sys/bus/w1/devices/
#ds18_report_time:
#   读数之间的间隔（秒）。默认为 3.0，最小为 1.0
#sensor_mcu:
#   要读取的微控制器。必须为 host_mcu
```

### 组合温度传感器

组合温度传感器是基于其他几个传感器的虚拟温度传感器。此传感器可用于挤出机、heater_generic 和加热床。

```
sensor_type: temperature_combined
#sensor_list:
#   必须提供。组合成新"虚拟"传感器的传感器列表。
#   每个条目应是温度报告对象的完整名称，如其在配置中出现的那样
#   （例如 'extruder'、'heater_bed' 或自定义传感器的 'temperature_sensor <name>'）。
#   例如 'temperature_sensor sensor1, temperature_sensor sensor2'
#   例如 'extruder, heater_bed'
#   例如 'temperature_sensor chamber, extruder, heater_bed'
#combination_method:
#   必须提供。用于传感器的组合方法。
#   可用选项为 'max'、'min'、'mean'。
#maximum_deviation:
#   必须提供。要组合的传感器之间允许的最大偏差（例如 5 度）。要禁用它，请使用较大的值（例如 999.9）
```

### MPC 环境传感器

虚拟 MPC 传感器，用于显示内部环境温度值（如果使用 MPC 以外的任何算法，则默认为 25）

```
sensor_type: mpc_ambient_temperature
heater_name: extruder
#   填入此传感器所连接的加热器名称（此参数是必需的）
#gcode_id: AT
min_temp: 0
max_temp: 325
#ignore_limits: False
#   忽略温度限制（如果设置为 true，则可以省略 min_temp 和 max_temp）
#echo_limits_to_console: False
#   如果设置为 true，限制将被回显到控制台，而不仅仅是被忽略（如果 ignore_limits 为 true）
```

### MPC 块传感器

虚拟 MPC 传感器，用于显示内部环境温度值（如果使用 MPC 以外的任何算法，则默认为 25）

```
sensor_type: mpc_block_temperature
heater_name: extruder
#   填入此传感器所连接的加热器名称（此参数是必需的）
#gcode_id: BE
min_temp: 0
max_temp: 325
#ignore_limits: False
#   忽略温度限制（如果设置为 true，则可以省略 min_temp 和 max_temp）
#echo_limits_to_console: False
#   如果设置为 true，限制将被回显到控制台，而不仅仅是被忽略（如果 ignore_limits 为 true）
```


## 风扇

### [fan]

打印冷却风扇。

```
[fan]
pin:
#   控制风扇的输出引脚。必须提供此参数。
#max_power: 1.0
#   引脚可设置的最大功率（0.0 到 1.0）。值 1.0 可在较长时间内完全启用引脚，
#   而 0.5 允许最多一半的时间。使用它来限制（较长时间内）风扇的总功率输出。
#   此值与 min_power 结合以缩放风扇速度。当 `min_power` 为 0.3 且
#   `max_power` 为 1.0 时，风扇速度请求在 0.3（min_power）和 1.0（max_power）之间缩放。
#   请求 10% 风扇速度的结果为 0.37。默认为 1.0。
#shutdown_speed: 0
#   如果微控制器软件进入错误状态，所需的风扇速度（表示为 0.0 到 1.0 的值）。默认为 0。
#cycle_time: 0.010
#   每个 PWM 功率周期到风扇的时间量（秒）。建议在使用基于软件的 PWM 时为 10 毫秒或更大。
#   默认为 0.010 秒。
#hardware_pwm: False
#   启用此项以使用硬件 PWM 而不是软件 PWM。大多数风扇与硬件 PWM 配合不佳，因此
#   除非有电气要求以极高速度切换，否则不建议启用此项。使用硬件 PWM 时，实际周期时间
#   受实现限制，可能与请求的 cycle_time 显著不同。默认为 False。
#kick_start_time: 0.100
#   在首次启用或增加超过 50% 时，以全速运行风扇的时间（秒）（有助于启动风扇）。
#   默认为 0.100 秒。
#min_power: 0.0
#   将为风扇供电的最小输入功率（表示为 0.0 到 1.0 的值）。默认为 0.0。
#
#   要校准此设置，从 min_power=0 和 max_power=1 开始，逐渐降低风扇速度以确定
#   可靠驱动风扇而不失速的最低输入速度。将 min_power 设置为对应于此值的占空比
#   （例如，12% -> 0.12）或稍高。
#tachometer_pin:
#   用于监控风扇速度的转速计输入引脚。通常需要上拉。此参数可选。
#tachometer_ppr: 2
#   指定 tachometer_pin 时，这是转速计信号每转的脉冲数。对于 BLDC 风扇，这通常是
#   极数的一半。默认为 2。
#tachometer_poll_interval: 0.0015
#   指定 tachometer_pin 时，这是转速计引脚的轮询周期（秒）。默认为 0.0015，
#   对于低于 10000 RPM 且 2 PPR 的风扇来说足够快。这必须小于
#   30/(tachometer_ppr*rpm)，并留有一定余量，其中 rpm 是风扇的最大速度（RPM）。
#enable_pin:
#   可选的引脚，用于启用风扇电源。这对于具有专用 PWM 输入的风扇很有用。其中一些风扇
#   即使在 0% PWM 输入下也会保持开启。在这种情况下，PWM 引脚可以正常使用，例如，
#   接地开关 FET（标准风扇引脚）可用于控制风扇电源。
#off_below:
#   此选项已弃用，不应再指定。请改用 `min_power`。
#initial_speed:
#   如果指定，风扇速度将在启动时设置为此值。值为 0.0 到 1.0。
```

### [heated_fan]

加热的打印冷却风扇。一个用于高温打印的实验性模块，要求部件冷却空气接近打印部件温度。

```

[heated_fan]
#   风扇参数的描述请参见 "fan" 部分。
#   加热器参数的描述请参见 "heater_generic" 部分。
#heater_temp: 50
#   风扇开启时加热器的目标温度（摄氏度）。默认为 50 摄氏度。
#min_speed: 1.0
#   当关联的加热器开启时，风扇将设置的最低风扇速度（表示为 0.0 到 1.0 的值）（例如：
#   保护风道免于熔化）。如果风扇设置的速度低于 min_speed，则应用 min_speed 值。
#   默认为 1.0（100%）
#idle_timeout: 60
#   当风扇被请求关闭时，风扇保持开启的超时时间（秒），以保护风道免于熔化。默认为 60（秒）。
```

### [heater_fan]

加热器冷却风扇（可以定义任意数量带有 "heater_fan" 前缀的部分）。"加热器风扇"是在其关联的
加热器激活时启用的风扇。默认情况下，heater_fan 的 shutdown_speed 等于 max_power。

```
[heater_fan heatbreak_cooling_fan]
#pin:
#max_power:
#shutdown_speed:
#cycle_time:
#hardware_pwm:
#kick_start_time:
#min_power:
#tachometer_pin:
#tachometer_ppr:
#tachometer_poll_interval:
#enable_pin:
#initial_speed:
#   上述参数的描述请参见 "fan" 部分。
#heater: extruder
#   定义此风扇关联的加热器的配置部分的名称。如果此处提供逗号分隔的加热器名称列表，
#   则在任何给定的加热器启用时风扇将启用。默认为 "extruder"。
#heater_temp: 50.0
#   在风扇被禁用之前，加热器必须降至其下的温度（摄氏度）。默认为 50 摄氏度。
#fan_speed: 1.0
#   当关联的加热器启用时，风扇将设置的风扇速度（表示为 0.0 到 1.0 的值）。默认为 1.0
```

### [controller_fan]

控制器冷却风扇（可以定义任意数量带有 "controller_fan" 前缀的部分）。"控制器风扇"是在其关联的
加热器或其关联的步进驱动器激活时启用的风扇。每当达到 idle_timeout 时风扇将停止，
以确保在停用被监视的组件后不会发生过热。

```
[controller_fan my_controller_fan]
#pin:
#max_power:
#shutdown_speed:
#cycle_time:
#hardware_pwm:
#kick_start_time:
#min_power:
#tachometer_pin:
#tachometer_ppr:
#tachometer_poll_interval:
#enable_pin:
#   上述参数的描述请参见 "fan" 部分。
#fan_speed: 1.0
#   当加热器或步进驱动器激活时，风扇将设置的风扇速度（表示为 0.0 到 1.0 的值）。
#   默认为 1.0
#idle_timeout:
#   在步进驱动器或加热器活跃后，风扇应保持运行的时间量（秒）。默认为 30 秒。
#idle_speed:
#   在加热器或步进驱动器活跃后且在 idle_timeout 达到之前，风扇将设置的风扇速度
#   （表示为 0.0 到 1.0 的值）。默认为 fan_speed。
#heater:
#stepper:
#   定义此风扇关联的加热器/步进的配置部分的名称。如果此处提供逗号分隔的加热器/步进名称列表，
#   则在任何给定的加热器/步进启用时风扇将启用。默认加热器为 "extruder"，默认步进为所有。
```

### [temperature_fan]

温度触发的冷却风扇（可以定义任意数量带有 "temperature_fan" 前缀的部分）。"温度风扇"是在其关联的
传感器高于设定温度时启用的风扇。默认情况下，temperature_fan 的 shutdown_speed 等于 max_power。

有关其他信息，请参见 [命令参考](G-Codes.md#temperature_fan)。

```
[temperature_fan my_temp_fan]
#pin:
#max_power:
#shutdown_speed:
#cycle_time:
#hardware_pwm:
#kick_start_time:
#min_power:
#tachometer_pin:
#tachometer_ppr:
#tachometer_poll_interval:
#enable_pin:
#   上述参数的描述请参见 "fan" 部分。
#sensor_type:
#sensor_pin:
#control:
#max_delta:
#min_temp:
#max_temp:
#   上述参数的描述请参见 "extruder" 部分。
#pid_Kp:
#pid_Ki:
#pid_Kd:
#   PID 反馈控制系统的比例（pid_Kp）、积分（pid_Ki）和微分（pid_Kd）设置。
#   Kalico 使用以下通用公式评估 PID 设置：
#     fan_pwm = max_power - (Kp*e + Ki*integral(e) - Kd*derivative(e)) / 255
#   其中 "e" 是 "target_temperature - measured_temperature"，"fan_pwm" 是请求的
#   风扇速率，0.0 表示完全关闭，1.0 表示完全开启。当启用 PID 控制算法时，
#   必须提供 pid_Kp、pid_Ki 和 pid_Kd 参数。
#pid_deriv_time: 2.0
#   使用 PID 控制算法时，温度测量值将在此时间值（秒）内平滑。这可能会减少
#   测量噪声的影响。默认为 2 秒。
#target_temp: 40.0
#   目标温度（摄氏度）。默认为 40 度。
#max_speed: 1.0
#   当传感器温度超过设定值时，风扇将设置的风扇速度（表示为 0.0 到 1.0 的值）。
#   默认为 1.0。
#min_speed: 0.3
#   PID 温度风扇将设置的最低风扇速度（表示为 0.0 到 1.0 的值）。默认为 0.3。
#gcode_id:
#   如果设置，温度将在 M105 查询中使用给定的 id 报告。默认是不通过 M105 报告温度。
#reverse: False
#   如果为 true，风扇的工作模式将反转。如果温度低于目标温度，风扇速度增加；
#   否则，风扇速度降低。默认为 False。
```

```
control: curve
#points:
#  50.0, 0.0
#  55.0, 0.5
#   用户可以定义一个点列表，这些点由温度及其关联的风扇速度组成（temp, fan_speed）。
#   target_temp 值定义了风扇将以全速运行的温度。
#   该算法将使用线性插值来获取两点之间的风扇速度（如果定义了 50° 为 0.0 且 60° 为 1.0，则
#   风扇将在 55° 时以 0.5 速度运行
#cooling_hysteresis: 0.0
#   定义降低风扇速度的温度滞后值
#   （简单来说，此设置在冷却时将风扇曲线偏移指定的摄氏度数。
#   例如，如果滞后设置为 5°C，风扇曲线将移动 -5°C。
#   此设置可用于减少目标温度附近快速变化的温度对风扇的影响，
#   这会导致风扇反复加速和减速。）
#heating_hysteresis: 0.0
#   与 cooling_hysteresis 相同，但用于增加风扇速度，
#   出于安全原因建议保持为 0
#smooth_readings: 10
#   此参数已弃用，不应再使用。
```

### [fan_generic]

手动控制的风扇（可以定义任意数量的 "fan_generic" 前缀部分）。
手动控制风扇的速度通过 SET_FAN_SPEED [gcode 命令](G-Codes.md#fan_generic) 设置。

```
[fan_generic extruder_partfan]
#pin:
#max_power:
#shutdown_speed:
#cycle_time:
#hardware_pwm:
#kick_start_time:
#min_power:
#tachometer_pin:
#tachometer_ppr:
#tachometer_poll_interval:
#enable_pin:
#   有关上述参数的描述，请参阅 "fan" 部分。
```

## LEDs

### [led]

支持通过微控制器 PWM 引脚控制的 LED（和 LED 灯带）（可以定义任意数量的 "led" 前缀部分）。更多信息请参阅[命令参考](G-Codes.md#led)。

```
[led my_led]
#red_pin:
#green_pin:
#blue_pin:
#wite_pin:
#   控制给定 LED 颜色的引脚。至少必须提供上述一个参数。
#cycle_time: 0.010
#   每个 PWM 周期的时间长度（以秒为单位）。使用基于软件的 PWM 时，建议此值为 10 毫秒或更大。默认值为 0.010 秒。
#hardware_pwm: False
#   启用此项以使用硬件 PWM 而不是软件 PWM。使用硬件 PWM 时，实际周期时间受实现限制，可能与请求的 cycle_time 有显著差异。默认值为 False。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   设置初始 LED 颜色。每个值应在 0.0 到 1.0 之间。每种颜色的默认值为 0。
```

### [neopixel]

Neopixel（也称为 WS2812）LED 支持（可以定义任意数量的 "neopixel" 前缀部分）。更多信息请参阅[命令参考](G-Codes.md#led)。

请注意，[linux mcu](RPi_microcontroller.md) 实现目前不支持直接连接的 Neopixel。当前使用 Linux 内核接口的设计不允许这种场景，因为内核 GPIO 接口不够快，无法提供所需的脉冲速率。

```
[neopixel my_neopixel]
pin:
#   连接到 Neopixel 的引脚。必须提供此参数。
#chain_count:
#   菊花链连接到所提供引脚的 Neopixel 芯片数量。默认值为 1（表示只有一个 Neopixel 连接到引脚）。
#color_order: GRB
#   设置 LED 硬件所需的像素顺序（使用包含字母 R、G、B、W 的字符串，W 可选）。或者，这可以是像素顺序的逗号分隔列表 - 链中每个 LED 一个。默认值为 GRB。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   有关这些参数的信息，请参阅 "led" 部分。
```

### [dotstar]

Dotstar（也称为 APA102）LED 支持（可以定义任意数量的 "dotstar" 前缀部分）。更多信息请参阅[命令参考](G-Codes.md#led)。

```
[dotstar my_dotstar]
data_pin:
#   连接到 dotstar 数据线的引脚。必须提供此参数。
clock_pin:
#   连接到 dotstar 时钟线的引脚。必须提供此参数。
#chain_count:
#   有关此参数的信息，请参阅 "neopixel" 部分。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#   有关这些参数的信息，请参阅 "led" 部分。
```

### [pca9533]

PCA9533 LED 支持。PCA9533 用于 mightyboard。

```
[pca9533 my_pca9533]
#i2c_address: 98
#   芯片在 i2c 总线上使用的 i2c 地址。PCA9533/1 使用 98，PCA9533/2 使用 99。默认值为 98。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   有关这些参数的信息，请参阅 "led" 部分。
```

### [pca9632]

PCA9632 LED 支持。PCA9632 用于 FlashForge Dreamer。

```
[pca9632 my_pca9632]
#i2c_address: 98
#   芯片在 i2c 总线上使用的 i2c 地址。可以是 96、97、98 或 99。默认值为 98。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
#color_order: RGBW
#   设置 LED 的像素顺序（使用包含字母 R、G、B、W 的字符串）。默认值为 RGBW。
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   有关这些参数的信息，请参阅 "led" 部分。
```

## 附加的舵机、按钮和其他引脚

### [servo]

舵机（可以定义任意数量的 "servo" 前缀部分）。舵机可以使用 SET_SERVO [g-code 命令](G-Codes.md#servo) 控制。例如：SET_SERVO SERVO=my_servo ANGLE=180

```
[servo my_servo]
pin:
#   控制舵机的 PWM 输出引脚。必须提供此参数。
#maximum_servo_angle: 180
#   此舵机可设置的最大角度（以度为单位）。默认值为 180 度。
#minimum_pulse_width: 0.001
#   最小脉冲宽度时间（以秒为单位）。这应对应于 0 度的角度。默认值为 0.001 秒。
#maximum_pulse_width: 0.002
#   最大脉冲宽度时间（以秒为单位）。这应对应于 maximum_servo_angle 的角度。默认值为 0.002 秒。
#initial_angle:
#   设置舵机的初始角度（以度为单位）。默认值是在启动时不发送任何信号。
#initial_pulse_width:
#   设置舵机的初始脉冲宽度时间（以秒为单位）。（仅在未设置 initial_angle 时有效。）默认值是在启动时不发送任何信号。
```

### [gcode_button]

按下或释放按钮时（或引脚状态改变时）执行 gcode。您可以使用 `QUERY_BUTTON button=my_gcode_button` 检查按钮状态。

```
[gcode_button my_gcode_button]
pin:
#   按钮连接的引脚。必须提供此参数。
#analog_range:
#   两个以逗号分隔的电阻值（以欧姆为单位），指定按钮的最小和最大电阻范围。如果提供 analog_range，则引脚必须是支持模拟的引脚。默认值是使用数字 gpio 作为按钮。
#analog_pullup_resistor:
#   指定 analog_range 时的上拉电阻（以欧姆为单位）。默认值为 4700 欧姆。
#press_gcode:
#   按下按钮时要执行的 G-Code 命令列表。支持 G-Code 模板。必须提供此参数。
#release_gcode:
#   释放按钮时要执行的 G-Code 命令列表。支持 G-Code 模板。默认值是在按钮释放时不运行任何命令。
#debounce_delay:
#   运行按钮 gcode 之前用于消除事件抖动的时间段（以秒为单位）。如果在此延迟期间按下并释放按钮，则整个按钮按下将被忽略。默认值为 0。
```

### [output_pin]

运行时可配置的输出引脚（可以定义任意数量的 "output_pin" 前缀部分）。此处配置的引脚将设置为输出引脚，可以使用 "SET_PIN PIN=my_pin VALUE=.1" 类型的扩展 [g-code 命令](G-Codes.md#output_pin) 在运行时修改它们。

```
[output_pin my_pin]
pin:
#   要配置为输出的引脚。必须提供此参数。
#pwm: False
#   设置输出引脚是否应支持脉冲宽度调制。如果为 true，则值字段应在 0 和 1 之间；如果为 false，则值字段应为 0 或 1。默认值为 False。
#value:
#   在 MCU 配置期间设置引脚的初始值。默认值为 0（低电压）。
#shutdown_value:
#   在 MCU 关闭事件时设置引脚的值。默认值为 0（低电压）。
#cycle_time: 0.100
#   每个 PWM 周期的时间长度（以秒为单位）。使用基于软件的 PWM 时，建议此值为 10 毫秒或更大。pwm 引脚的默认值为 0.100 秒。
#hardware_pwm: False
#   启用此项以使用硬件 PWM 而不是软件 PWM。使用硬件 PWM 时，实际周期时间受实现限制，可能与请求的 cycle_time 有显著差异。默认值为 False。
#scale:
#   此参数可用于更改 'value' 和 'shutdown_value' 参数的解释方式（针对 pwm 引脚）。如果提供，则 'value' 参数应在 0.0 和 'scale' 之间。这在配置控制步进电压参考的 PWM 引脚时很有用。'scale' 可以设置为 PWM 完全启用时的等效步进电流，然后可以使用所需步进电流指定 'value' 参数。默认值是不缩放 'value' 参数。
#maximum_mcu_duration:
#static_value:
#   这些选项已弃用，不应再指定。
```

### [static_pwm_clock]

静态可配置的输出引脚（可以定义任意数量的 "static_pwm_clock" 前缀部分）。此处配置的引脚将设置为时钟输出引脚。通常用于为板上的其他硬件提供时钟输入。

```
[static_pwm_clock my_pin]
pin:
#   要配置为输出的引脚。必须提供此参数。
#frequency: 100
#   目标输出频率。
```

### [pwm_tool]

能够进行高速更新的脉宽调制数字输出引脚（可以定义任意数量的 "output_pin" 前缀部分）。此处配置的引脚将设置为输出引脚，可以使用 "SET_PIN PIN=my_pin VALUE=.1" 类型的扩展 [g-code 命令](G-Codes.md#output_pin) 在运行时修改它们。

```
[pwm_tool my_tool]
pin:
#   要配置为输出的引脚。必须提供此参数。
#maximum_mcu_duration:
#   MCU 可以驱动非关闭值而无需主机确认的最大持续时间。如果主机无法跟上更新，MCU 将关闭并将所有引脚设置为各自的关闭值。默认值：0（禁用）。通常值约为 5 秒。
#value:
#shutdown_value:
#cycle_time: 0.100
#hardware_pwm: False
#scale:
#   有关这些参数的定义，请参阅 "output_pin" 部分。
```

### [pwm_cycle_time]

具有动态 pwm 周期时序的运行时可配置输出引脚（可以定义任意数量的 "pwm_cycle_time" 前缀部分）。此处配置的引脚将设置为输出引脚，可以使用 "SET_PIN PIN=my_pin VALUE=.1 CYCLE_TIME=0.100" 类型的扩展 [g-code 命令](G-Codes.md#pwm_cycle_time) 在运行时修改它们。

```
[pwm_cycle_time my_pin]
pin:
#value:
#shutdown_value:
#cycle_time: 0.100
#scale:
#   有关这些参数的信息，请参阅 "output_pin" 部分。
```

### [static_digital_output]

静态配置的数字输出引脚（可以定义任意数量的 "static_digital_output" 前缀部分）。此处配置的引脚将在 MCU 配置期间设置为 GPIO 输出。它们不能在运行时更改。

```
[static_digital_output my_output_pins]
pins:
#   要设置为 GPIO 输出引脚的引脚逗号分隔列表。除非引脚名称以 "!" 开头，否则引脚将设置为高电平。必须提供此参数。
```

### [hc595]

74HC595 移位寄存器输出扩展（可以定义任意数量的 "hc595" 前缀部分）。74HC595 是一个串行转并行移位寄存器，仅使用 3 个 MCU 引脚（数据、时钟、锁存）提供 8 个额外的数字输出引脚。多个芯片可以菊花链连接，最多提供 32 个输出。HC595 输出可以在任何接受标准数字输出引脚的地方使用，通过将它们引用为 `chip_name:N` 来实现，其中 N 是输出编号（0 到 chain_count*8 - 1）。chip_name 是在配置部分标题中给出的名称。

```
[hc595 my_shift]
data_pin:
#   连接到 74HC595 SER（串行数据输入）线的引脚，通常是 IC 上的引脚 14。必须提供此参数。
clock_pin:
#   连接到 74HC595 SRCLK（移位寄存器时钟）线的引脚，通常是 IC 上的引脚 11。必须提供此参数。
latch_pin:
#   连接到 74HC595 RCLK（存储寄存器时钟/锁存）线的引脚，通常是 IC 上的引脚 12。必须提供此参数。
#oe_pin:
#   可选的连接到 74HC595 OE（输出使能）线的引脚，通常是 IC 上的引脚 13。此引脚为低电平有效。如果未指定，OE 引脚应连接到地以永久启用输出。
#chain_count: 1
#   菊花链连接的 74HC595 芯片数量。必须在 1 到 4 之间。每个芯片添加 8 个额外的输出引脚。默认值为 1。
```

#### HC595 接线

对于单个 74HC595，连接：
- 74HC595 引脚 14 (SER) 到 MCU 引脚（由 `data_pin` 指定）
- 74HC595 引脚 11 (SRCLK) 到 MCU 引脚（由 `clock_pin` 指定）
- 74HC595 引脚 12 (RCLK) 到 MCU 引脚（由 `latch_pin` 指定）
- 74HC595 引脚 13 (OE) 接地（或连接到 MCU 引脚（由 `oe_pin` 指定））
- 74HC595 引脚 10 (SRCLR) 接 VCC
- 74HC595 引脚 8 (GND) 接地
- 74HC595 引脚 16 (VCC) 接 +3.3V 或 +5V
- 74HC595 输出引脚为 QA-QH（引脚 15、1-7）

对于菊花链连接，将第一个芯片的 Q7'（引脚 9）连接到下一个芯片的 SER（引脚 14）。所有芯片共享相同的 CLOCK、LATCH 和 OE 线。

#### HC595 使用示例

```
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
```

以下扩展 G-Code 命令可用：

- `SET_HC595 CHIP=<config_name> [BITS=<value>]`：一次性设置或查询所有 HC595 输出引脚。不带 BITS 时，报告当前引脚状态。带 BITS 时，将给定的整数值应用于所有输出（位 0 = 输出 0，依此类推）。

### [multi_pin]

多引脚输出（可以定义任意数量的 "multi_pin" 前缀部分）。multi_pin 输出创建一个内部引脚别名，每次设置别名引脚时可以修改多个输出引脚。例如，可以定义一个包含两个引脚的 "[multi_pin my_fan]" 对象，然后在 "[fan]" 部分设置 "pin=multi_pin:my_fan" - 每次风扇更改时，两个输出引脚都会更新。这些别名不能用于步进电机引脚。

```
[multi_pin my_multi_pin]
pins:
#   与此别名关联的引脚逗号分隔列表。必须提供此参数。
```

## TMC 步进驱动器配置

在 UART/SPI 模式下配置 Trinamic 步进电机驱动器。更多信息请参阅 [TMC 驱动器指南](TMC_Drivers.md) 和[命令参考](G-Codes.md#tmcxxxx)。

### [tmc2130]

通过 SPI 总线配置 TMC2130 步进电机驱动器。要使用此功能，请定义一个以 "tmc2130" 前缀开头的配置部分，后跟相应步进配置部分的名称（例如 "[tmc2130 stepper_x]"）。

```
[tmc2130 stepper_x]
cs_pin:
#   对应于 TMC2130 芯片选择线的引脚。此引脚在 SPI 消息开始时设置为低电平，消息完成后升为高电平。必须提供此参数。
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
#chain_position:
#chain_length:
#   这些参数配置 SPI 菊花链。这两个参数定义了步进器在链中的位置和总链长度。位置 1 对应于连接到 MOSI 信号的步进器。默认值是不使用 SPI 菊花链。
#interpolate: True
#   如果为 true，则启用步进插值（驱动器将以 256 微步的速率内部步进）。此插值确实会引入微小的系统性位置偏差 - 详情请参阅 TMC_Drivers.md。默认值为 True。
run_current:
#   配置驱动器在步进移动期间使用的电流量（以安培 RMS 为单位）。必须提供此参数。
#hold_current:
#   配置驱动器在步进器不移动时使用的电流量（以安培 RMS 为单位）。不建议设置 hold_current（详情请参阅 TMC_Drivers.md）。默认值是不降低电流。
#home_current:
#   配置驱动器在归位过程中使用的电流量（以安培 RMS 为单位）。默认值是不降低电流。
#current_change_dwell_time:
#   更改归位电流后等待的时间量（以秒为单位）。默认值为 0.5 秒。
sense_resistor:
#   驱动器检测电阻的阻值（以欧姆为单位）。必须提供此参数。大多数 TMC2209 驱动器的常见值为 0.110 欧姆，TMC5160 驱动器为 0.075 欧姆。请检查您的步进驱动器文档或电路板原理图以确认正确的值。
#stealthchop_threshold: 0
#   设置 "stealthChop" 阈值的速度（以 mm/s 为单位）。设置后，如果步进电机速度低于此值，将启用 "stealthChop" 模式。请注意，"sensorless homing" 代码可能会在归位操作期间临时覆盖此设置。默认值为 0，这会禁用 "stealthChop" 模式。
#coolstep_threshold:
#   设置 TMC 驱动器内部 "CoolStep" 阈值的速度（以 mm/s 为单位）。如果设置，当步进电机速度接近或超过此值时，将启用 coolstep 功能。重要 - 如果设置了 coolstep_threshold 并且使用了 "sensorless homing"，则必须确保归位速度高于 coolstep 阈值！默认值是不启用 coolstep 功能。
#high_velocity_threshold:
#   设置 TMC 驱动器内部 "high velocity" 阈值 (THIGH) 的速度（以 mm/s 为单位）。这通常用于在高速时禁用 "CoolStep" 功能。默认值是不设置 TMC "high velocity" 阈值。
#driver_MSLUT0: 2863314260
#driver_MSLUT1: 1251300522
#driver_MSLUT2: 608774441
#driver_MSLUT3: 269500962
#driver_MSLUT4: 4227858431
#driver_MSLUT5: 3048961917
#driver_MSLUT6: 1227445590
#driver_MSLUT7: 4211234
#driver_W0: 2
#driver_W1: 1
#driver_W2: 1
#driver_W3: 1
#driver_X1: 128
#driver_X2: 255
#driver_X3: 255
#driver_START_SIN: 0
#driver_START_SIN90: 247
#   这些字段直接控制微步表寄存器。最佳波表特定于每个电机，并且可能随电流变化。最优配置将具有由非线性步进运动引起的最小打印伪影。上面指定的值是驱动器使用的默认值。值必须指定为十进制整数（不支持十六进制形式）。要计算波表字段，请参阅 Trinamic 网站上的 tmc2130 "Calculation Sheet"。
#driver_IHOLDDELAY: 8
#driver_TPOWERDOWN: 0
#driver_TBL: 1
#driver_TOFF: 4
#driver_HEND: 7
#driver_HSTRT: 0
#driver_VHIGHFS: 0
#driver_VHIGHCHM: 0
#driver_PWM_AUTOSCALE: True
#driver_PWM_FREQ: 1
#driver_PWM_GRAD: 4
#driver_PWM_AMPL: 128
#driver_FREEWHEEL: 0
#driver_SGT: 0
#driver_SEMIN: 0
#driver_SEUP: 0
#driver_SEMAX: 0
#driver_SEDN: 0
#driver_SEIMIN: 0
#driver_SFILT: 0
#   在配置 TMC2130 芯片期间设置给定的寄存器。这可用于设置自定义电机参数。每个参数的默认值在上面列表中参数名称旁边。
#diag0_pin:
#diag1_pin:
#   连接到 TMC2130 芯片其中一个 DIAG 线的微控制器引脚。应仅指定一个 diag 引脚。该引脚为 "低电平有效"，因此通常以 "^!" 开头。设置此项会创建 "tmc2130_stepper_x:virtual_endstop" 虚拟引脚，可用作步进器的 endstop_pin。这样做会启用 "sensorless homing"。（请确保还将 driver_SGT 设置为适当的灵敏度值。）默认值是不启用 sensorless homing。
```

### [tmc2208]

通过单线 UART 配置 TMC2208（或 TMC2224）步进电机驱动器。要使用此功能，请定义一个以 "tmc2208" 前缀开头的配置部分，后跟相应步进配置部分的名称（例如 "[tmc2208 stepper_x]"）。

```
[tmc2208 stepper_x]
uart_pin:
#   连接到 TMC2208 PDN_UART 线的引脚。必须提供此参数。
#tx_pin:
#   如果使用单独的接收和发送线与驱动器通信，则将 uart_pin 设置为接收引脚，将 tx_pin 设置为发送引脚。默认值是使用 uart_pin 进行读写。
#select_pins:
#   访问 tmc2208 UART 之前要设置的引脚逗号分隔列表。这可用于配置用于 UART 通信的模拟多路复用器。默认值是不配置任何引脚。
#interpolate: True
#   如果为 true，则启用步进插值（驱动器将以 256 微步的速率内部步进）。此插值确实会引入微小的系统性位置偏差 - 详情请参阅 TMC_Drivers.md。默认值为 True。
run_current:
#   配置驱动器在步进移动期间使用的电流量（以安培 RMS 为单位）。必须提供此参数。
#hold_current:
#   配置驱动器在步进器不移动时使用的电流量（以安培 RMS 为单位）。不建议设置 hold_current（详情请参阅 TMC_Drivers.md）。默认值是不降低电流。
#home_current:
#   配置驱动器在归位过程中使用的电流量（以安培 RMS 为单位）。默认值是不降低电流。
#current_change_dwell_time:
#   更改归位电流后等待的时间量（以秒为单位）。默认值为 0.5 秒。
sense_resistor:
#   驱动器检测电阻的阻值（以欧姆为单位）。必须提供此参数。大多数 TMC2209 驱动器的常见值为 0.110 欧姆，TMC5160 驱动器为 0.075 欧姆。请检查您的步进驱动器文档或电路板原理图以确认正确的值。
#stealthchop_threshold: 0
#   设置 "stealthChop" 阈值的速度（以 mm/s 为单位）。设置后，如果步进电机速度低于此值，将启用 "stealthChop" 模式。请注意，"sensorless homing" 代码可能会在归位操作期间临时覆盖此设置。默认值为 0，这会禁用 "stealthChop" 模式。
#driver_MULTISTEP_FILT: True
#driver_IHOLDDELAY: 8
#driver_TPOWERDOWN: 20
#driver_TBL: 2
#driver_TOFF: 3
#driver_HEND: 0
#driver_HSTRT: 5
#driver_PWM_AUTOGRAD: True
#driver_PWM_AUTOSCALE: True
#driver_PWM_LIM: 12
#driver_PWM_REG: 8
#driver_PWM_FREQ: 1
#driver_PWM_GRAD: 14
#driver_PWM_OFS: 36
#driver_FREEWHEEL: 0
#   在配置 TMC2208 芯片期间设置给定的寄存器。这可用于设置自定义电机参数。每个参数的默认值在上面列表中参数名称旁边。
```

### [tmc2209]

通过单线 UART 配置 TMC2209 步进电机驱动器。要使用此功能，请定义一个以 "tmc2209" 前缀开头的配置部分，后跟相应步进配置部分的名称（例如 "[tmc2209 stepper_x]"）。

```
[tmc2209 stepper_x]
uart_pin:
#tx_pin:
#select_pins:
#interpolate: True
run_current:
#hold_current:
#home_current:
#current_change_dwell_time:
sense_resistor:
#stealthchop_threshold: 0
#   有关这些参数的定义，请参阅 "tmc2208" 部分。
#coolstep_threshold:
#   设置 TMC 驱动器内部 "CoolStep" 阈值的速度（以 mm/s 为单位）。如果设置，当步进电机速度接近或超过此值时，将启用 coolstep 功能。重要 - 如果设置了 coolstep_threshold 并且使用了 "sensorless homing"，则必须确保归位速度高于 coolstep 阈值！默认值是不启用 coolstep 功能。
#uart_address:
#   用于 UART 消息的 TMC2209 芯片地址（0 到 3 之间的整数）。这通常用于多个 TMC2209 芯片连接到同一个 UART 引脚时。默认值为零。
#driver_MULTISTEP_FILT: True
#driver_IHOLDDELAY: 8
#driver_TPOWERDOWN: 20
#driver_TBL: 2
#driver_TOFF: 3
#driver_HEND: 0
#driver_HSTRT: 5
#driver_PWM_AUTOGRAD: True
#driver_PWM_AUTOSCALE: True
#driver_PWM_LIM: 12
#driver_PWM_REG: 8
#driver_PWM_FREQ: 1
#driver_PWM_GRAD: 14
#driver_PWM_OFS: 36
#driver_FREEWHEEL: 0
#driver_SGTHRS: 0
#driver_SEMIN: 0
#driver_SEUP: 0
#driver_SEMAX: 0
#driver_SEDN: 0
#driver_SEIMIN: 0
#   在配置 TMC2209 芯片期间设置给定的寄存器。这可用于设置自定义电机参数。每个参数的默认值在上面列表中参数名称旁边。
#diag_pin:
#   连接到 TMC2209 芯片 DIAG 线的微控制器引脚。通常以 "^" 开头以启用上拉。设置此项会创建 "tmc2209_stepper_x:virtual_endstop" 虚拟引脚，可用作步进器的 endstop_pin。这样做会启用 "sensorless homing"。（请确保还将 driver_SGTHRS 设置为适当的灵敏度值。）默认值是不启用 sensorless homing。
```

### [tmc2660]

通过 SPI 总线配置 TMC2660 步进电机驱动器。要使用此功能，请定义一个以 tmc2660 前缀开头的配置部分，后跟相应步进配置部分的名称（例如 "[tmc2660 stepper_x]"）。

```
[tmc2660 stepper_x]
cs_pin:
#   对应于 TMC2660 芯片选择线的引脚。此引脚在 SPI 消息开始时设置为低电平，消息传输完成后设置为高电平。必须提供此参数。
#spi_speed: 4000000
#   用于与 TMC2660 步进驱动器通信的 SPI 总线频率。默认值为 4000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
#interpolate: True
#   如果为 true，则启用步进插值（驱动器将以 256 微步的速率内部步进）。这仅在 microsteps 设置为 16 时有效。插值确实会引入微小的系统性位置偏差 - 详情请参阅 TMC_Drivers.md。默认值为 True。
run_current:
#   驱动器在步进移动期间使用的电流量（以安培 RMS 为单位）。必须提供此参数。
#home_current:
#   配置驱动器在归位过程中使用的电流量（以安培 RMS 为单位）。默认值是不降低电流。
#current_change_dwell_time:
#   更改归位电流后等待的时间量（以秒为单位）。默认值为 0.5 秒。
sense_resistor:
#   驱动器检测电阻的阻值（以欧姆为单位）。必须提供此参数。大多数 TMC2209 驱动器的常见值为 0.110 欧姆，TMC5160 驱动器为 0.075 欧姆。请检查您的步进驱动器文档或电路板原理图以确认正确的值。
#idle_current_percent: 100
#   空闲超时到期时步进驱动器将降低到的 run_current 百分比（您需要使用 [idle_timeout] 配置部分设置超时）。一旦步进器再次需要移动，电流将再次升高。确保将此值设置得足够高，以便步进器不会丢失位置。在电流再次升高之前还有很小的延迟，因此在步进器空闲时发出快速移动命令时请考虑到这一点。默认值为 100（不降低）。
#driver_TBL: 2
#driver_RNDTF: 0
#driver_HDEC: 0
#driver_CHM: 0
#driver_HEND: 3
#driver_HSTRT: 3
#driver_TOFF: 4
#driver_SEIMIN: 0
#driver_SEDN: 0
#driver_SEMAX: 0
#driver_SEUP: 0
#driver_SEMIN: 0
#driver_SFILT: 0
#driver_SGT: 0
#driver_SLPH: 0
#driver_SLPL: 0
#driver_DISS2G: 0
#driver_TS2G: 3
#   在 TMC2660 芯片配置期间设置给定参数。
#   这可用于设置自定义驱动参数。每个参数的默认值
#   在上方列表中紧邻参数名称。有关每个参数的作用
#   以及参数组合限制，请参阅 TMC2660 数据手册。
#   特别注意 CHOPCONF 寄存器，将 CHM 设置为
#   零或一将导致布局更改（此时 HDEC 的第一位
#   被解释为 HSTRT 的最高有效位）。
```

### [tmc2240]

通过 SPI 总线或 UART 配置 TMC2240 步进电机驱动器。要使用此功能，
请定义一个配置节，以 "tmc2240" 为前缀，后跟对应步进配置节的名称
（例如 "[tmc2240 stepper_x]"）。

```
[tmc2240 stepper_x]
cs_pin:
#   对应 TMC2240 片选线的引脚。此引脚将在 SPI 消息开始时
#   设为低电平，并在消息完成后升为高电平。此参数必须提供。
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
#uart_pin:
#   连接到 TMC2240 DIAG1/SW 线的引脚。如果提供此参数，
#   则使用 UART 通信而非 SPI。
#chain_position:
#chain_length:
#   这些参数用于配置 SPI 菊花链。这两个参数定义链中的
#   步进位置和总链长。位置 1 对应连接到 MOSI 信号的步进。
#   默认为不使用 SPI 菊花链。
#interpolate: True
#   如果为 true，则启用步进插值（驱动器将以 256 微步的速率
#   内部步进）。默认为 True。
run_current:
#   驱动器在步进电机运动期间配置使用的电流量（安培 RMS）。
#   此参数必须提供。
#hold_current:
#   步进电机未运动时驱动器配置使用的电流量（安培 RMS）。
#   不建议设置 hold_current（详见 TMC_Drivers.md）。
#   默认为不减小电流。
#home_current:
#   驱动器在归位过程中配置使用的电流量（安培 RMS）。
#   默认为不减小电流。
#current_change_dwell_time:
#   更改归位电流后等待的时间（秒）。默认为 0.5 秒。
#rref:
#   IREF 和 GND 之间电阻的阻值（欧姆）。此参数必须提供。
#stealthchop_threshold: 0
#   设置 "stealthChop" 阈值的速度（mm/s）。设置后，如果步进
#   电机速度低于此值，则启用 "stealthChop" 模式。请注意，
#   "无传感器归位" 代码可能在归位操作期间暂时覆盖此设置。
#   默认为 0，即禁用 "stealthChop" 模式。
#coolstep_threshold:
#   设置 TMC 驱动器内部 "CoolStep" 阈值的速度（mm/s）。
#   如果设置，当步进电机速度接近或超过此值时，将启用
#   coolstep 功能。重要 - 如果设置了 coolstep_threshold 并
#   使用 "无传感器归位"，则必须确保归位速度高于 coolstep
#   阈值！默认为不启用 coolstep 功能。
#high_velocity_threshold:
#   设置 TMC 驱动器内部 "high velocity" 阈值 (THIGH) 的速度
#   （mm/s）。通常用于在高速时禁用 "CoolStep" 功能。
#   默认为不设置 TMC "high velocity" 阈值。
#current_range:
#   驱动器的 current_range 位值。有效值为 0-3。
#   默认为自动计算以匹配请求的 run_current。
#   更多信息请查阅 tmc2240 数据手册和调整表。
#driver_CS:
#   TMC 驱动器的电流比例值。
#   理想的 `driver_CS` 值可通过在 TMC 计算电子表格
#   (https://www.analog.com/media/en/engineering-tools/design-tools/tmc5240_tmc2240_tmc2210_calculations.xlsx)
#   的斩波器选项卡中设置 `CS` 值来找到，
#   使迟滞不被标记为过高。
#   虽然不必更改 CS 值，但这可能有助于在低电流步进上
#   实现足够的迟滞值。
#   默认情况下，此值是自动计算的。
#   如果指定了 driver_CS，则此值将用于归位，因此请确保使用给定的 currentscaler 值能够达到您的 homing_current
#driver_MSLUT0: 2863314260
#driver_MSLUT1: 1251300522
#driver_MSLUT2: 608774441
#driver_MSLUT3: 269500962
#driver_MSLUT4: 4227858431
#driver_MSLUT5: 3048961917
#driver_MSLUT6: 1227445590
#driver_MSLUT7: 4211234
#driver_W0: 2
#driver_W1: 1
#driver_W2: 1
#driver_W3: 1
#driver_X1: 128
#driver_X2: 255
#driver_X3: 255
#driver_START_SIN: 0
#driver_START_SIN90: 247
#driver_OFFSET_SIN90: 0
#   这些字段直接控制微步查找表寄存器。最优的波表
#   因每个电机而异，并且可能随电流变化。最优配置
#   将最大程度减少因非线性步进运动造成的打印瑕疵。
#   上述指定的值是驱动器使用的默认值。值必须指定为
#   十进制整数（不支持十六进制形式）。要计算波表字段，
#   请参阅 Trinamic 网站上的 tmc2130 "Calculation Sheet"。
#   此外，此驱动器还具有 OFFSET_SIN90 字段，可用于
#   调整线圈不平衡的电机。有关此字段及如何调整的信息，
#   请参阅数据手册中的 `Sine Wave Lookup Table` 部分。
#driver_MULTISTEP_FILT: True
#driver_IHOLDDELAY: 6
#driver_IRUNDELAY: 4
#driver_TPOWERDOWN: 10
#driver_TBL: 2
#driver_TOFF: 3
#driver_HEND: 2
#driver_HSTRT: 5
#driver_FD3: 0
#driver_TPFD: 4
#driver_CHM: 0
#driver_VHIGHFS: 0
#driver_VHIGHCHM: 0
#driver_DISS2G: 0
#driver_DISS2VS: 0
#driver_PWM_AUTOSCALE: True
#driver_PWM_AUTOGRAD: True
#driver_PWM_FREQ: 0
#driver_FREEWHEEL: 0
#driver_PWM_GRAD: 0
#driver_PWM_OFS: 29
#driver_PWM_REG: 4
#driver_PWM_LIM: 12
#driver_SLOPE_CONTROL: 0
#   控制栅极驱动器输出的压摆率。芯片默认值为 0，
#   对应 100V/µs。设置为 2 (400V/µs) 或 3 (570V/µs) 可
#   显著降低驱动器温度（用户报告在 50kHz 斩波频率下
#   降低约 15-20°C）。值 2 与 TMC2209 压摆率匹配。
#   更高的值可能增加 EMI。详见 TMC2240 数据手册。
#driver_SGT: 0
#driver_SEMIN: 0
#driver_SEUP: 0
#driver_SEMAX: 0
#driver_SEDN: 0
#driver_SEIMIN: 0
#driver_SFILT: 0
#driver_SG4_ANGLE_OFFSET: 1
#   在 TMC2240 芯片配置期间设置给定寄存器。
#   这可用于设置自定义电机参数。每个参数的默认值
#   在上方列表中紧邻参数名称。
#diag0_pin:
#diag1_pin:
#   连接到 TMC2240 芯片任一 DIAG 线的微控制器引脚。
#   只应指定一个 diag 引脚。该引脚为 "低电平有效"，
#   因此前缀通常为 "^!"。设置此引脚将创建一个
#   "tmc2240_stepper_x:virtual_endstop" 虚拟引脚，
#   可用作步进的 endstop_pin。这样做可启用
#   "无传感器归位"。（请确保同时将 driver_SGT 设置为
#   合适的灵敏度值。）默认为不启用无传感器归位。
```

### [tmc5160]

通过 SPI 总线配置 TMC5160 或 TMC2160 步进电机驱动器。
要使用此功能，请定义一个配置节，以 "tmc5160" 为前缀，
后跟对应步进配置节的名称
（例如 "[tmc5160 stepper_x]"）。

```
[tmc5160 stepper_x]
cs_pin:
#   对应 TMC5160 或 TMC2160 片选线的引脚。此引脚将在
#   SPI 消息开始时设为低电平，并在消息完成后升为高电平。
#   此参数必须提供。
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
#chain_position:
#chain_length:
#   这些参数用于配置 SPI 菊花链。这两个参数定义链中的
#   步进位置和总链长。位置 1 对应连接到 MOSI 信号的步进。
#   默认为不使用 SPI 菊花链。
#interpolate: True
#   如果为 true，则启用步进插值（驱动器将以 256 微步的速率
#   内部步进）。默认为 True。
run_current:
#   驱动器在步进电机运动期间配置使用的电流量（安培 RMS）。
#   此参数必须提供。
#hold_current:
#   步进电机未运动时驱动器配置使用的电流量（安培 RMS）。
#   不建议设置 hold_current（详见 TMC_Drivers.md）。
#   默认为不减小电流。
#home_current:
#   驱动器在归位过程中配置使用的电流量（安培 RMS）。
#   默认为不减小电流。
#current_change_dwell_time:
#   更改归位电流后等待的时间（秒）。默认为 0.5 秒。
sense_resistor:
#   驱动器采样电阻的阻值（欧姆）。此参数必须提供。
#   大多数 TMC2209 驱动器的常见值为 0.110 欧姆，
#   TMC5160 驱动器为 0.075 欧姆。请查阅步进驱动器
#   文档或电路板原理图以确认正确的值。
#stealthchop_threshold: 0
#   设置 "stealthChop" 阈值的速度（mm/s）。设置后，如果步进
#   电机速度低于此值，则启用 "stealthChop" 模式。请注意，
#   "无传感器归位" 代码可能在归位操作期间暂时覆盖此设置。
#   默认为 0，即禁用 "stealthChop" 模式。
#coolstep_threshold:
#   设置 TMC 驱动器内部 "CoolStep" 阈值的速度（mm/s）。
#   如果设置，当步进电机速度接近或超过此值时，将启用
#   coolstep 功能。重要 - 如果设置了 coolstep_threshold 并
#   使用 "无传感器归位"，则必须确保归位速度高于 coolstep
#   阈值！默认为不启用 coolstep 功能。
#high_velocity_threshold:
#   设置 TMC 驱动器内部 "high velocity" 阈值 (THIGH) 的速度
#   （mm/s）。通常用于在高速时禁用 "CoolStep" 功能。
#   默认为不设置 TMC "high velocity" 阈值。
#driver_MSLUT0: 2863314260
#driver_MSLUT1: 1251300522
#driver_MSLUT2: 608774441
#driver_MSLUT3: 269500962
#driver_MSLUT4: 4227858431
#driver_MSLUT5: 3048961917
#driver_MSLUT6: 1227445590
#driver_MSLUT7: 4211234
#driver_W0: 2
#driver_W1: 1
#driver_W2: 1
#driver_W3: 1
#driver_X1: 128
#driver_X2: 255
#driver_X3: 255
#driver_START_SIN: 0
#driver_START_SIN90: 247
#   这些字段直接控制微步查找表寄存器。最优的波表
#   因每个电机而异，并且可能随电流变化。最优配置
#   将最大程度减少因非线性步进运动造成的打印瑕疵。
#   上述指定的值是驱动器使用的默认值。值必须指定为
#   十进制整数（不支持十六进制形式）。要计算波表字段，
#   请参阅 Trinamic 网站上的 tmc2130 "Calculation Sheet"。
#driver_MULTISTEP_FILT: True
#driver_IHOLDDELAY: 6
#driver_TPOWERDOWN: 10
#driver_TBL: 2
#driver_TOFF: 3
#driver_HEND: 2
#driver_HSTRT: 5
#driver_FD3: 0
#driver_TPFD: 4
#driver_CHM: 0
#driver_VHIGHFS: 0
#driver_VHIGHCHM: 0
#driver_CS:
#   TMC 驱动器的电流比例值。
#   理想的 `driver_CS` 值可通过在 TMC 计算电子表格
#   (https://www.analog.com/media/en/engineering-tools/design-tools/tmc5160_calculations.xlsx)
#   的斩波器选项卡中设置 `CS` 值来找到，
#   使迟滞不被标记为过高。
#   虽然不必更改 CS 值，但这可能有助于在低电流步进上
#   实现足够的迟滞值。
#   默认情况下，此值是自动计算的。
#   如果指定了 driver_CS，则此值将用于归位，因此请确保使用给定的 currentscaler 值能够达到您的 homing_current
#driver_DISS2G: 0
#driver_DISS2VS: 0
#driver_PWM_AUTOSCALE: True
#driver_PWM_AUTOGRAD: True
#driver_PWM_FREQ: 0
#driver_FREEWHEEL: 0
#driver_PWM_GRAD: 0
#driver_PWM_OFS: 30
#driver_PWM_REG: 4
#driver_PWM_LIM: 12
#driver_SGT: 0
#driver_SEMIN: 0
#driver_SEUP: 0
#driver_SEMAX: 0
#driver_SEDN: 0
#driver_SEIMIN: 0
#driver_SFILT: 0
#driver_DRVSTRENGTH: 0
#driver_BBMCLKS: 4
#driver_BBMTIME: 0
#driver_FILT_ISENSE: 0
#   在 TMC5160 或 TMC2160 芯片配置期间设置给定寄存器。
#   这可用于设置自定义电机参数。每个参数的默认值
#   在上方列表中紧邻参数名称。
#⚠️driver_s2vs_level: 6   # 对电源短路容差，范围 4 到 15
#⚠️driver_s2g_level: 6    # 对地短路容差，范围 2 到 15
#⚠️driver_shortdelay: 0   # 短路触发延迟，0=750ns，1=1500ns
#⚠️driver_short_filter: 1
#   短路滤波带宽。0=100ns，1=1us（默认），2=2us，3=3us
#diag0_pin:
#diag1_pin:
#   连接到 TMC5160 或 TMC2160 芯片任一 DIAG 线的微控制器引脚。
#   只应指定一个 diag 引脚。该引脚为 "低电平有效"，
#   因此前缀通常为 "^!"。设置此引脚将创建一个
#   "tmc5160_stepper_x:virtual_endstop" 虚拟引脚，
#   可用作步进的 endstop_pin。这样做可启用
#   "无传感器归位"。（请确保同时将 driver_SGT 设置为
#   合适的灵敏度值。）默认为不启用无传感器归位。
```

## 运行时步进电机电流配置

### [ad5206]

通过 SPI 总线连接的静态配置 AD5206 数字电位器（可定义任意数量
以 "ad5206" 为前缀的配置节）。

```
[ad5206 my_digipot]
enable_pin:
#   对应 AD5206 片选线的引脚。此引脚将在 SPI 消息开始时
#   设为低电平，并在消息完成后升为高电平。此参数必须提供。
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
#channel_1:
#channel_2:
#channel_3:
#channel_4:
#channel_5:
#channel_6:
#   要静态设置的给定 AD5206 通道的值。通常设置为 0.0 到 1.0
#   之间的数字，其中 1.0 为最高电阻，0.0 为最低电阻。
#   但是，可以通过 'scale' 参数更改范围（见下文）。
#   如果未指定通道，则保持未配置状态。
#scale:
#   此参数可用于更改 'channel_x' 参数的解释方式。如果提供，
#   则 'channel_x' 参数应在 0.0 到 'scale' 之间。当 AD5206 用于
#   设置步进电压参考时，这可能很有用。'scale' 可设置为
#   AD5206 在最高电阻时等效的步进电流值，然后 'channel_x'
#   参数可以使用步进所需的电流值来指定。
#   默认为不缩放 'channel_x' 参数。
```

### [mcp4451]

通过 I2C 总线连接的静态配置 MCP4451 数字电位器（可定义任意数量
以 "mcp4451" 为前缀的配置节）。

```
[mcp4451 my_digipot]
i2c_address:
#   芯片在 i2c 总线上使用的 i2c 地址。此参数必须提供。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
#wiper_0:
#wiper_1:
#wiper_2:
#wiper_3:
#   要静态设置的给定 MCP4451 "wiper" 的值。通常设置为
#   0.0 到 1.0 之间的数字，其中 1.0 为最高电阻，0.0 为
#   最低电阻。但是，可以通过 'scale' 参数更改范围（见下文）。
#   如果未指定 wiper，则保持未配置状态。
#scale:
#   此参数可用于更改 'wiper_x' 参数的解释方式。如果提供，
#   则 'wiper_x' 参数应在 0.0 到 'scale' 之间。当 MCP4451 用于
#   设置步进电压参考时，这可能很有用。'scale' 可设置为
#   MCP4451 在最高电阻时等效的步进电流值，然后 'wiper_x'
#   参数可以使用步进所需的电流值来指定。
#   默认为不缩放 'wiper_x' 参数。
```

### [mcp4728]

通过 I2C 总线连接的静态配置 MCP4728 数模转换器（可定义任意数量
以 "mcp4728" 为前缀的配置节）。

```
[mcp4728 my_dac]
#i2c_address: 96
#   芯片在 i2c 总线上使用的 i2c 地址。默认为 96。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
#channel_a:
#channel_b:
#channel_c:
#channel_d:
#   要静态设置的给定 MCP4728 通道的值。通常设置为 0.0 到 1.0
#   之间的数字，其中 1.0 为最高电压 (2.048V)，0.0 为最低电压。
#   但是，可以通过 'scale' 参数更改范围（见下文）。
#   如果未指定通道，则保持未配置状态。
#scale:
#   此参数可用于更改 'channel_x' 参数的解释方式。如果提供，
#   则 'channel_x' 参数应在 0.0 到 'scale' 之间。当 MCP4728 用于
#   设置步进电压参考时，这可能很有用。'scale' 可设置为
#   MCP4728 在最高电压 (2.048V) 时等效的步进电流值，
#   然后 'channel_x' 参数可以使用步进所需的电流值来指定。
#   默认为不缩放 'channel_x' 参数。
```

### [mcp4018]

通过 i2c 连接的静态配置 MCP4018 数字电位器（可定义任意数量
以 "mcp4018" 为前缀的配置节）。

```
[mcp4018 my_digipot]
#i2c_address: 47
#   芯片在 i2c 总线上使用的 i2c 地址。默认为 47。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
wiper:
#   要静态设置的给定 MCP4018 "wiper" 的值。通常设置为
#   0.0 到 1.0 之间的数字，其中 1.0 为最高电阻，0.0 为
#   最低电阻。但是，可以通过 'scale' 参数更改范围（见下文）。
#   此参数必须提供。
#scale:
#   此参数可用于更改 'wiper' 参数的解释方式。如果提供，
#   则 'wiper' 参数应在 0.0 到 'scale' 之间。当 MCP4018 用于
#   设置步进电压参考时，这可能很有用。'scale' 可设置为
#   MCP4018 在最高电阻时等效的步进电流值，然后 'wiper'
#   参数可以使用步进所需的电流值来指定。
#   默认为不缩放 'wiper' 参数。
```

## 显示屏支持

### [display]

支持连接到微控制器的显示屏。

```
[display]
lcd_type:
#   使用的 LCD 芯片类型。可以是 "hd44780"、"hd44780_spi"、
#   "aip31068_spi"、"st7920"、"emulated_st7920"、"uc1701"、
#   "ssd1306" 或 "sh1106"。
#   有关每种类型及其提供的其他参数的信息，请参阅下方的
#   显示部分。此参数必须提供。
#display_group:
#   要在显示屏上显示的 display_data 组的名称。这控制屏幕的
#   内容（更多信息请参阅 "display_data" 部分）。hd44780 或
#   aip31068_spi 显示的默认值为 _default_20x4，其他显示的
#   默认值为 _default_16x4。
#menu_timeout:
#   菜单超时。不活跃此秒数将触发菜单退出或在启用自动运行时
#   返回根菜单。默认为 0 秒（禁用）。
#menu_root:
#   在主屏幕点击编码器时显示的主菜单节名称。
#   默认为 __main，显示 klippy/extras/display/menu.cfg 中
#   定义的默认菜单。
#menu_reverse_navigation:
#   启用后将反转列表导航的上下方向。默认为 False。
#   此参数可选。
#encoder_pins:
#   连接到编码器的引脚。使用编码器时必须提供 2 个引脚。
#   使用菜单时必须提供此参数。
#encoder_steps_per_detent:
#   编码器每个档位（"点击"）发出的步数。如果编码器需要
#   两个档位才能在条目之间移动，或一个档位移动两个条目，
#   请尝试更改此值。允许的值为 2（半步）或 4（全步）。
#   默认为 4。
#click_pin:
#   连接到 "enter" 按钮或编码器 "click" 的引脚。
#   使用菜单时必须提供此参数。'analog_range_click_pin'
#   配置参数的存在会将此参数从数字变为模拟。
#back_pin:
#   连接到 "back" 按钮的引脚。此参数可选，菜单可以不用它。
#   'analog_range_back_pin' 配置参数的存在会将此参数从
#   数字变为模拟。
#up_pin:
#   连接到 "up" 按钮的引脚。不使用编码器使用菜单时必须
#   提供此参数。'analog_range_up_pin' 配置参数的存在会
#   将此参数从数字变为模拟。
#down_pin:
#   连接到 "down" 按钮的引脚。不使用编码器使用菜单时必须
#   提供此参数。'analog_range_down_pin' 配置参数的存在会
#   将此参数从数字变为模拟。
#kill_pin:
#   连接到 "kill" 按钮的引脚。此按钮将调用紧急停止。
#   'analog_range_kill_pin' 配置参数的存在会将此参数从
#   数字变为模拟。
#analog_pullup_resistor: 4700
#   连接到模拟按钮的上拉电阻的阻值（欧姆）。
#   默认为 4700 欧姆。
#analog_range_click_pin:
#   "enter" 按钮的电阻范围。使用模拟按钮时必须提供
#   范围最小值和最大值的逗号分隔值。
#analog_range_back_pin:
#   "back" 按钮的电阻范围。使用模拟按钮时必须提供
#   范围最小值和最大值的逗号分隔值。
#analog_range_up_pin:
#   "up" 按钮的电阻范围。使用模拟按钮时必须提供
#   范围最小值和最大值的逗号分隔值。
#analog_range_down_pin:
#   "down" 按钮的电阻范围。使用模拟按钮时必须提供
#   范围最小值和最大值的逗号分隔值。
#analog_range_kill_pin:
#   "kill" 按钮的电阻范围。使用模拟按钮时必须提供
#   范围最小值和最大值的逗号分隔值。
```

#### hd44780 显示

配置 hd44780 显示的信息（用于 "RepRapDiscount 2004 Smart Controller"
类型显示）。

```
[display]
lcd_type: hd44780
#   对于 hd44780 显示，设置为 "hd44780"。
rs_pin:
e_pin:
d4_pin:
d5_pin:
d6_pin:
d7_pin:
#   连接到 hd44780 类型 lcd 的引脚。这些参数必须提供。
#hd44780_protocol_init: True
#   在 hd44780 显示上执行 8 位/4 位协议初始化。
#   这在真实 hd44780 设备上是必要的。但是，在某些
#   "克隆" 设备上可能需要禁用此功能。默认为 True。
#line_length:
#   设置 hd44780 类型 lcd 每行的字符数。
#   可能的值为 20（默认）和 16。行数固定为 4。
...
```

#### hd44780_spi 显示

配置 hd44780_spi 显示的信息 - 一个通过硬件 "移位寄存器"
控制的 20x04 显示（用于 mightyboard 打印机）。

```
[display]
lcd_type: hd44780_spi
#   对于 hd44780_spi 显示，设置为 "hd44780_spi"。
latch_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   连接到控制显示的移位寄存器的引脚。
#   spi_software_miso_pin 需要设置为打印机主板上的未使用引脚，
#   因为移位寄存器没有 MISO 引脚，但软件 spi 实现
#   需要配置此引脚。
#hd44780_protocol_init: True
#   在 hd44780 显示上执行 8 位/4 位协议初始化。
#   这在真实 hd44780 设备上是必要的。但是，在某些
#   "克隆" 设备上可能需要禁用此功能。默认为 True。
#line_length:
#   设置 hd44780 类型 lcd 每行的字符数。
#   可能的值为 20（默认）和 16。行数固定为 4。
...
```

#### aip31068_spi 显示

配置 aip31068_spi 显示的信息 - 与 hd44780_spi 非常相似的
20x04（20 个符号 x 4 行）显示，内部协议略有不同。

```
[display]
lcd_type: aip31068_spi
latch_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   连接到控制显示的移位寄存器的引脚。
#   spi_software_miso_pin 需要设置为打印机主板上的未使用引脚，
#   因为移位寄存器没有 MISO 引脚，但软件 spi 实现
#   需要配置此引脚。
#line_length:
#   设置 hd44780 类型 lcd 每行的字符数。
#   可能的值为 20（默认）和 16。行数固定为 4。
...
```

#### st7920 显示

配置 st7920 显示的信息（用于 "RepRapDiscount 12864 Full Graphic
Smart Controller" 类型显示）。

```
[display]
lcd_type: st7920
#   对于 st7920 显示，设置为 "st7920"。
cs_pin:
sclk_pin:
sid_pin:
#   连接到 st7920 类型 lcd 的引脚。这些参数必须提供。
...
```

#### emulated_st7920 显示

配置模拟 st7920 显示的信息 - 存在于某些 "2.4 英寸触摸屏设备"
及类似产品中。

```
[display]
lcd_type: emulated_st7920
#   对于 emulated_st7920 显示，设置为 "emulated_st7920"。
en_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   连接到 emulated_st7920 类型 lcd 的引脚。en_pin 对应
#   st7920 类型 lcd 的 cs_pin，spi_software_sclk_pin 对应
#   sclk_pin，spi_software_mosi_pin 对应 sid_pin。
#   spi_software_miso_pin 需要设置为打印机主板上的未使用引脚，
#   因为 st7920 没有 MISO 引脚，但软件 spi 实现
#   需要配置此引脚。
...
```

#### uc1701 显示

配置 uc1701 显示的信息（用于 "MKS Mini 12864" 类型显示）。

```
[display]
lcd_type: uc1701
#   对于 uc1701 显示，设置为 "uc1701"。
cs_pin:
a0_pin:
#   连接到 uc1701 类型 lcd 的引脚。这些参数必须提供。
#rst_pin:
#   连接到 lcd 上 "rst" 引脚的引脚。如果未指定，则
#   硬件必须在相应的 lcd 线上具有上拉。
#contrast:
#   要设置的对比度。值范围为 0 到 63，默认为 40。
...
```

#### ssd1306 和 sh1106 显示

配置 ssd1306 和 sh1106 显示的信息。

```
[display]
lcd_type:
#   对于给定的显示类型，设置为 "ssd1306" 或 "sh1106"。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   通过 i2c 总线连接的显示的可选参数。
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
#cs_pin:
#dc_pin:
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   处于 "4 线" spi 模式时连接到 lcd 的引脚。
#   有关以 "spi_" 开头的参数的描述，请参阅
#   "common SPI settings" 部分。默认为使用 i2c 模式。
#reset_pin:
#   可在显示上指定复位引脚。如果未指定，则硬件必须
#   在相应的 lcd 线上具有上拉。
#contrast:
#   要设置的对比度。值范围为 0 到 256，默认为 239。
#vcomh: 0
#   设置显示上的 Vcomh 值。此值与某些 OLED 显示上的
#   "拖影" 效果相关。值范围为 0 到 63。默认为 0。
#invert: False
#   TRUE 在某些 OLED 显示上反转像素。默认为 False。
#x_offset: 0
#   设置 SH1106 显示上的水平偏移值。默认为 0。
...
```

### [display_data]

支持在 lcd 屏幕上显示自定义数据。可以创建任意数量的显示组，
并在这些组下创建任意数量的数据项。如果 [display] 节中的
display_group 选项设置为给定的组名，显示将显示该组的所有数据项。

[默认显示组](../klippy/extras/display/display.cfg)是自动创建的。
可以通过在主 printer.cfg 配置文件中覆盖默认值来替换或扩展这些
display_data 项。

```
[display_data my_group_name my_data_name]
position:
#   用于显示信息的显示位置的行列，逗号分隔。
#   此参数必须提供。
text:
#   要在给定位置显示的文本。此字段使用命令模板求值
#   （详见 docs/Command_Templates.md）。此参数必须提供。
```

### [display_template]

显示数据文本 "宏"（可定义任意数量以 display_template 为前缀的配置节）。
有关模板求值的信息，请参阅 [命令模板](Command_Templates.md) 文档。

此功能允许减少 display_data 节中的重复定义。可以在 display_data 节中
使用内置 `render()` 函数来求值模板。例如，如果定义了
`[display_template my_template]`，则可以在 display_data 节中使用
`{ render('my_template') }`。

此功能也可用于通过
[SET_LED_TEMPLATE](G-Codes.md#set_led_template) 命令进行连续 LED 更新。

```
[display_template my_template_name]
#param_<name>:
#   可以指定任意数量以 "param_" 为前缀的选项。给定的名称将被赋予
#   给定的值（解析为 Python 字面量），并在宏展开期间可用。如果在
#   render() 调用中传入了该参数，则在宏展开期间将使用该值。例如，
#   配置中 "param_speed = 75" 可能有一个调用者使用
#   "render('my_template_name', param_speed=80)"。参数名不能使用
#   大写字符。
text:
#   此模板渲染时返回的文本。此字段使用命令模板进行求值（参见
#   docs/Command_Templates.md）。此参数必须提供。
```

### [display_glyph]

在支持的显示器上显示自定义字形。给定的名称将被赋予给定的显示数据，
然后可以通过该名称在显示模板中引用，名称两侧用两个"波浪线"符号
包围，即 `~my_display_glyph~`

参见 [sample-glyphs.cfg](../config/sample-glyphs.cfg) 了解一些示例。

```
[data_glyph my_display_glyph]
#data:
#   显示数据，存储为 16 行，每行 16 位（每像素 1 位），其中 '.' 为空白像素，
#   '*' 为点亮像素（例如，"****************" 显示一条实心水平线）。
#   或者，可以使用 '0' 表示空白像素，'1' 表示点亮像素。将每个显示行
#   放入单独的配置行中。字形必须恰好由 16 行组成，每行 16 位。
#   此参数是可选的。
#hd44780_data:
#   在 20x4 hd44780 显示器上使用的字形。字形必须恰好由 8 行组成，
#   每行 5 位。此参数是可选的。
#hd44780_slot:
#   存储字形的 hd44780 硬件索引（0..7）。如果多个不同的图像使用
#   同一个槽位，请确保在任何给定屏幕上仅使用其中一个图像。
#   如果指定了 hd44780_data，则此参数是必需的。
```

### [display my_extra_display]

如果在 printer.cfg 中定义了如上所示的主 [display] 部分，则可以定义多个辅助显示器。请注意，辅助显示器目前不支持菜单功能，因此不支持"menu"选项或按钮配置。

```
[display my_extra_display]
# 有关可用参数，请参阅 "display" 部分。
```

### ⚠️ [menu]

可自定义的 LCD 显示菜单。

会自动创建一组[默认菜单](../klippy/extras/display/menu.cfg)。可以通过在主 printer.cfg 配置文件中覆盖默认值来替换或扩展菜单。

参见[命令模板文档](Command_Templates.md#menu-templates)了解模板渲染期间可用的菜单属性信息。

```
# 所有菜单配置部分可用的通用参数。
#[menu __some_list __some_name]
#type: disabled
#   永久禁用的菜单元素，唯一必需的属性是 'type'。
#   允许您轻松禁用/隐藏现有菜单项。

#[menu some_name]
#type:
#   以下之一：command、input、list、text：
#       command      - 具有各种脚本触发器的基本菜单元素
#       input        - 与 'command' 相同，但具有值更改功能。
#                      按下将开始/停止编辑模式。
#       list         - 允许将菜单项分组到可滚动列表中。
#                      通过使用 "some_list" 作为前缀创建菜单配置
#                      来添加到列表中 - 例如：
#                      [menu some_list some_item_in_the_list]
#       vsdlist      - 与 'list' 相同，但会附加虚拟 SD 卡中的文件
#                      （已弃用，将来会移除）
#    ⚠️ file_browser - 扩展 SD 卡浏览器，支持目录和排序。
#                      （替代 vsdlist）
#    ⚠️ dialog       - 菜单对话框，一组输入以及最终的确认或取消选择。
#                      用于更复杂的场景，如 PID/MPC 校准，其中您
#                      可能需要为单个命令设置多个值
#name:
#   菜单项名称 - 作为模板求值。
#enable:
#   求值为 True 或 False 的模板。
#index:
#   项目需要插入列表中的位置。默认情况下，项目将被添加到末尾。

#[menu some_list]
#type: list
#name:
#enable:
#   有关上述参数的描述，请参阅上文。

#[menu sdcard]
#type: file_browser
#name:
#sort_by:
#   `last_modified`（默认）或 `name`
#enable:
#   有关上述参数的描述，请参阅上文。

#[menu some_list some_command]
#type: command
#name:
#enable:
#   有关上述参数的描述，请参阅上文。
#gcode:
#   按钮点击或长按时运行的脚本。作为模板求值。

#[menu some_list some_input]
#type: input
#name:
#enable:
#   有关上述参数的描述，请参阅上文。
#input:
#   编辑时使用的初始值 - 作为模板求值。结果必须是浮点数。
#input_min:
#   范围的最小值 - 作为模板求值。默认为 -99999。
#input_max:
#   范围的最大值 - 作为模板求值。默认为 99999。
#input_step:
#   编辑步长 - 必须是正整数或浮点值。它具有内部快速步长。
#   当 "(input_max - input_min) / input_step > 100" 时，快速步长
#   为 10 * input_step，否则快速步长与 input_step 相同。
#realtime:
#   此属性接受静态布尔值。启用后，每次值更改后都会运行 gcode
#   脚本。默认为 False。
#gcode:
#   按钮点击、长按或值更改时运行的脚本。作为模板求值。
#   按钮点击将触发编辑模式的开始或结束。

#[menu neopixel]
#type: dialog
#name:
#enable:
#   有关上述参数的描述，请参阅上文。
#title:
#   显示在对话框顶部的可选标题。如果未设置，将使用 `name`
#confirm_text:
#cancel_text
#   确认和取消选项的模板
#gcode:
#   确认时运行的 G-Code。确认后对话框将关闭。
#   可以使用 `{menu.exit()}` 来关闭菜单。
```

## 耗材传感器

### [filament_switch_sensor]

耗材开关传感器。使用开关传感器（如限位开关）支持耗材插入和断料检测。

参见[命令参考](G-Codes.md#filament_switch_sensor)了解更多信息。

```
[filament_switch_sensor my_sensor]
#pause_on_runout: True
#   设置为 True 时，在检测到断料后将立即执行 PAUSE。请注意，
#   如果 pause_on_runout 为 False 且省略了 runout_gcode，则
#   断料检测将被禁用。默认为 True。
#runout_gcode:
#   检测到断料后要执行的 G-Code 命令列表。有关 G-Code 格式，
#   请参见 docs/Command_Templates.md。如果 pause_on_runout
#   设置为 True，则此 G-Code 将在 PAUSE 完成后运行。默认是不
#   运行任何 G-Code 命令。
#immediate_runout_gcode:
#   检测到断料后立即执行的 G-Code 命令列表（且 runout_distance
#   大于 0）。有关 G-Code 格式，请参见 docs/Command_Templates.md。
#insert_gcode:
#   检测到耗材插入后要执行的 G-Code 命令列表。有关 G-Code 格式，
#   请参见 docs/Command_Templates.md。默认是不运行任何 G-Code
#   命令，这会禁用插入检测。
#runout_distance: 0.0
#   定义开关传感器触发后仍可拉动的耗材长度（例如，您在挤出机
#   和传感器之间有 60cm 的反向鲍登管，那么您可以将
#   runout_distance 设置为 590 左右以留出小的安全余量，这样
#   打印不会在传感器触发时立即暂停，而是继续打印直到耗材到达
#   挤出机）。默认为 0 毫米。
#event_delay: 3.0
#   事件之间延迟的最短时间（秒）。在此时间段内触发的事件将被
#   静默忽略。默认为 3 秒。
#pause_delay: 0.5
#   暂停命令分发和 runout_gcode 执行之间的延迟时间（秒）。
#   如果 OctoPrint 出现奇怪的暂停行为，增加此延迟可能有用。
#   默认为 0.5 秒。
#debounce_delay:
#   在运行开关 gcode 之前对事件进行防抖的时间段（秒）。开关
#   必须保持单一状态至少这么长时间才能激活。如果开关在此延迟
#   期间切换开/关，则事件将被忽略。默认为 0。
#switch_pin:
#   开关连接的引脚。此参数必须提供。
#smart:
#   设置为 true 时，传感器将使用 virtual_sd_card 模块来确定
#   打印机是否正在打印，这更可靠，但在通过 USB 或类似方式
#   流式传输打印时将不起作用。
#always_fire_events:
#   设置为 true 时，无论传感器是否启用，断料事件始终会触发。
#   对 MMU 很有用
#check_on_print_start:
#   设置为 true 时，打印开始时将重新评估传感器，如果未检测到
#   耗材，则无论定义的 runout_distance 如何，都会运行
#   runout_gcode（在这种情况下不会运行 immediate_runout_gcode）
```

### [filament_motion_sensor]

耗材运动传感器。使用编码器支持耗材插入和断料检测，该编码器在
耗材通过传感器移动时切换输出引脚。

参见[命令参考](G-Codes.md#filament_switch_sensor)了解更多信息。

```
[filament_motion_sensor my_sensor]
detection_length: 7.0
#   通过传感器拉动的最小耗材长度，以触发 switch_pin 上的状态变化。
#   默认为 7 mm。
extruder:
#   此传感器关联的挤出机部分的名称。此参数必须提供。
switch_pin:
#pause_on_runout:
#runout_gcode:
#insert_gcode:
#event_delay:
#pause_delay:
#smart:
#always_fire_events:
#   有关上述参数的描述，请参阅 "filament_switch_sensor" 部分。
```

### [tsl1401cl_filament_width_sensor]

基于 TSL1401CL 的耗材宽度传感器。参见[指南](TSL1401CL_Filament_Width_Sensor.md)了解更多信息。

```
[tsl1401cl_filament_width_sensor]
#pin:
#default_nominal_filament_diameter: 1.75 # (mm)
#   最大允许的耗材直径差（mm）。
#max_difference: 0.2
#   传感器到熔融腔的距离（mm）。
#measurement_delay: 100
```

### [hall_filament_width_sensor]

霍尔耗材宽度传感器（参见 [Hall Filament Width Sensor](Hall_Filament_Width_Sensor.md)）。

```
[hall_filament_width_sensor]
adc1:
adc2:
#   连接到传感器的模拟输入引脚。这些参数必须提供。
#cal_dia1: 1.50
#cal_dia2: 2.00
#   传感器的校准值（mm）。cal_dia1 默认为 1.50，cal_dia2 默认为 2.00。
#raw_dia1: 9500
#raw_dia2: 10500
#   传感器的原始校准值。raw_dia1 默认为 9500，raw_dia2 默认为 10500。
#default_nominal_filament_diameter: 1.75
#   标称耗材直径。此参数必须提供。
#max_difference: 0.200
#   最大允许的耗材直径差（mm）。如果标称耗材直径与传感器输出之间
#   的差值超过 +- max_difference，则挤出倍率将被设置回 %100。
#   默认为 0.200。
#measurement_delay: 70
#   从传感器到熔融腔/热端的距离（mm）。传感器和热端之间的耗材
#   将被视为 default_nominal_filament_diameter。主机模块使用
#   FIFO 逻辑工作。它将每个传感器值和位置保存在数组中，并在
#   正确的位置弹出。此参数必须提供。
#enable: False
#   电源开启后传感器启用或禁用。默认为禁用。
#measurement_interval: 10
#   传感器读数之间的近似距离（mm）。默认为 10mm。
#logging: False
#   通过命令可以开启/关闭输出直径到终端和 klippy.log。
#min_diameter: 1.0
#   触发虚拟 filament_switch_sensor 的最小直径。
#max_diameter:
#   触发虚拟 filament_switch_sensor 的最大直径。
#   默认为 default_nominal_filament_diameter + max_difference。
#use_current_dia_while_delay: False
#   在测量延迟未运行完成时使用当前直径而不是标称直径。
#pause_on_runout:
#immediate_runout_gcode:
#runout_gcode:
#insert_gcode:
#event_delay:
#pause_delay:
#smart:
#always_fire_events:
#check_on_print_start:
#   有关上述参数的描述，请参阅 "filament_switch_sensor" 部分。
```

### [belay]

Belay 挤出机同步传感器（可以定义任意数量以 "belay" 为前缀的部分）。

```
[belay my_belay]
extruder_type:
#   辅助挤出机的类型。可选值为 'trad_rack' 或 'extruder_stepper'。
#   此参数必须指定。
extruder_stepper_name:
#   用作辅助挤出机的 extruder_stepper 的名称。如果 extruder_type
#   设置为 'extruder_stepper'，则必须指定此参数，否则不应指定。
#   例如，如果辅助挤出机的配置部分是 [extruder_stepper
#   my_extruder_stepper]，则此参数的值为 'my_extruder_stepper'。
sensor_pin:
#   连接到传感器的输入引脚。此参数必须提供。
#multiplier_high: 1.05
#   向前挤出且 Belay 被压缩时，或向后挤出且 Belay 被扩展时，
#   为辅助挤出机设置的高倍率。默认为 1.05。
#multiplier_low: 0.95
#   向前挤出且 Belay 被扩展时，或向后挤出且 Belay 被压缩时，
#   为辅助挤出机设置的低倍率。默认为 0.95。
#debug_level: 0
#   控制发送到控制台的消息。设置为 0 时不发送任何消息。设置为 1 时，
#   将报告倍率重置，并在因开关状态变化而设置倍率时报告。设置为 2 时，
#   行为与 1 相同，但在因检测到挤出方向变化而设置倍率时会附加消息。
#   默认为 0。
```
## 负载传感器
### [load_cell]
负载传感器。使用连接到负载传感器的 ADC 传感器创建数字秤。
```
[load_cell]
sensor_type:
#   这必须是支持的传感器类型之一，请参见下文。
#counts_per_gram:
#   浮点数，表示 1 克力的传感器计数。此值由 LOAD_CELL_CALIBRATE 命令计算。
#reference_tare_counts:
#   整数去皮值，以原始传感器计数为单位，在运行 LOAD_CELL_CALIBRATE 时
#   获取。这是 klipper 启动时的默认去皮值。
#sensor_orientation:
#   更改传感器的方向。可以是 'normal' 或 'inverted'。
#   默认为 'normal'。如果传感器在负载下报告递减的力值，请使用 'inverted'。
```

#### HX711
这是一款 24 位低采样率芯片，使用"位冲击"通信。适用于耗材秤。
```
[load_cell]
sensor_type: hx711
sclk_pin:
#   连接到 HX711 时钟线的引脚。此参数必须提供。
dout_pin:
#   连接到 HX711 数据输出线的引脚。此参数必须提供。
#gain: A-128
#   gain 的有效值为：A-128、A-64、B-32。默认为 A-128。
#   'A' 表示输入通道，数字表示增益。芯片仅支持列出的 3 种组合。
#   请注意，更改增益设置也会选择正在读取的通道。
#sample_rate: 80
#   sample_rate 的有效值为 80 或 10。默认值为 80。
#   这必须与芯片的接线匹配。采样率无法在软件中更改。
```

#### HX717
这是 HX711 的 4 倍高采样率版本，适用于探测。
```
[load_cell]
sensor_type: hx717
sclk_pin:
#   连接到 HX717 时钟线的引脚。此参数必须提供。
dout_pin:
#   连接到 HX717 数据输出线的引脚。此参数必须提供。
#gain: A-128
#   gain 的有效值为 A-128、B-64、A-64、B-8。
#   'A' 表示输入通道，数字表示增益设置。芯片仅支持列出的 4 种组合。
#   请注意，更改增益设置也会选择正在读取的通道。
#sample_rate: 320
#   sample_rate 的有效值为：10、20、80、320。默认为 320。
#   这必须与芯片的接线匹配。采样率无法在软件中更改。
```

#### ADS1220
ADS1220 是一款 24 位 ADC，支持最高 2Khz 的采样率，可通过软件配置。
```
[load_cell]
sensor_type: ads1220
cs_pin:
#   连接到 ADS1220 片选线的引脚。此参数必须提供。
#spi_speed: 512000
#   此芯片支持 2 种速度：256000 或 512000。更快的速度仅在使用 Turbo
#   采样率之一时启用。根据采样率选择正确的 spi_speed。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
data_ready_pin:
#   连接到 ADS1220 数据就绪线的引脚。此参数必须提供。
#gain: 128
#   有效的增益值为 128、64、32、16、8、4、2、1
#   默认为 128
#pga_bypass: False
#   禁用内部可编程增益放大器。如果设置为 True，则 PGA 将在增益为
#   1、2 和 4 时禁用。无论 pga_bypass 设置如何，PGA 在增益设置
#   8 到 128 时始终启用。如果使用 AVSS 作为输入，pga_bypass 将
#   强制为 True。默认为 False。
#sample_rate: 660
#   此芯片支持两个采样率范围：Normal 和 Turbo。在 Turbo 模式下，
#   芯片的内部时钟运行速度加倍，SPI 通信速度也加倍。
#   Normal 采样率：20、45、90、175、330、600、1000
#   Turbo 采样率：40、90、180、350、660、1200、2000
#   默认为 660
#input_mux:
#   输入多路复用器配置，选择要使用的一对引脚。第一个引脚为正极 AINP，
#   第二个引脚为负极 AINN。有效值为：'AIN0_AIN1'、'AIN0_AIN2'、
#   'AIN0_AIN3'、'AIN1_AIN2'、'AIN1_AIN3'、'AIN2_AIN3'、
#   'AIN1_AIN0'、'AIN3_AIN2'、'AIN0_AVSS'、'AIN1_AVSS'、
#   'AIN2_AVSS' 和 'AIN3_AVSS'。如果使用 AVSS，PGA 将被旁路，
#   pga_bypass 设置将强制为 True。默认为 AIN0_AIN1。
#vref:
#   选择的电压参考。有效值为：'internal'、'REF0'、'REF1'
#   和 'analog_supply'。默认为 'internal'。
```

#### ADS131M02
ADS131M02 是一款 24 位、2 通道 delta-sigma ADC，具有同时采样功能。
它使用 SPI 通信，提供适合负载传感器探测的高精度测量。
```
[load_cell]
sensor_type: ads131m02
cs_pin:
#   连接到 ADS131M02 片选线的引脚。此参数必须提供。
#spi_speed: 8192000
#   SPI 总线速度。默认为 8.192 MHz。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅 "common SPI settings" 部分。
data_ready_pin:
#   连接到 ADS131M02 数据就绪 (DRDY) 线的引脚。此参数必须提供。
#gain: 128
#   可编程增益放大器设置。有效值为 1、2、4、8、16、32、64 和 128。
#   默认为 128。
#sample_rate: 500
#   每秒采样数。有效值为 250、500、1000、2000、4000、8000、
#   16000 和 32000。默认为 500。
#enable_global_chop: False
#   启用全局斩波模式。此模式在每个采样时交替输入的极性。
#   这会减少噪声，但也会将有效采样率降低到标称值的 1/3。
#   默认为关闭。
#gloabl_chop_delay: 16
#   全局斩波模式下采样之间的延迟（以时钟周期为单位）。这允许
#   在采样开始前有额外的稳定时间。芯片默认为 16 个时钟周期。
#   值为 2 到 65536 的 2 的幂。
#channels: 0
#   要启用和求和的输入通道的逗号分隔列表。有效通道为 0 和 1。
#   默认为 0。
```

#### ADS131M04
ADS131M04 是一款 24 位、4 通道 delta-sigma ADC，具有同时采样功能。
它使用 SPI 通信，提供适合负载传感器探测的高精度测量。最多可以
将 4 个通道组合成单个传感器，非常适合床下负载传感器。
```
[load_cell]
sensor_type: ads131m04
cs_pin:
#spi_speed: 8192000
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
data_ready_pin:
#gain: 128
#sample_rate: 500
#enable_global_chop: False
#gloabl_chop_delay: 16
#   有关这些参数的详细信息，请参阅 "ADS131M02" 部分。
#channels: 0
#   要启用和求和的输入通道的逗号分隔列表。有效通道为：
#   0、1、2、3。默认为 0。
```


### [load_cell_probe]
负载传感器探针。这结合了 [probe] 和 [load_cell] 的功能。

另请参见 [simple_tap_classifier] 了解敲击验证配置。

```
[load_cell_probe]
sensor_type:
#   这必须是支持的批量 ADC 传感器类型之一，并且必须支持
#   mcu 上的负载传感器限位。
#counts_per_gram:
#reference_tare_counts:
#sensor_orientation:
#   这些参数必须在探针运行之前配置。有关更多详细信息，
#   请参见 [load_cell] 部分。
#force_safety_limit: 2000
#   启动探针的安全力限制。这相对于 reference_tare_counts，
#   即传感器的绝对 0 力值。设置为 0 以禁用。默认为 +/-2Kg。
#drift_safety_limit: 1000
#   探测期间允许的最大绝对力变化。设置为 0 以禁用。
#   默认为 +/-1Kg。
#trigger_force: 75.0
#   探针触发时的力。默认为 75g。
#drift_filter_cutoff_frequency: 0.8
#   在归位和探测期间启用可选的连续去皮以拒绝漂移。
#   该值是以 Hz 为单位的频率，低于此频率的漂移将被忽略。
#   此选项需要 SciPy 库。默认：无
#drift_filter_delay: 2
#   漂移滤波器的延迟或"阶数"。这控制触发检测所需的样本数。
#   可以是 1 或 2，默认为 2。
#buzz_filter_cutoff_frequency: 100.0
#   该值是以 Hz 为单位的频率，高于此频率的负载传感器中的
#   高频噪声将被滤除。此选项需要 SciPy 库。默认：无
#buzz_filter_delay: 2
#   嗡嗡滤波器的延迟或"阶数"。这控制触发检测所需的样本数。
#   可以是 1 或 2，默认为 2。
#notch_filter_frequencies: 50, 60
#   从负载传感器数据中滤除的 1 或 2 个频率（Hz）。这用于
#   拒绝电源线噪声。此选项需要 SciPy 库。默认：无
#notch_filter_quality: 2.0
#   控制陷波滤波器移除的频率范围的窄度。较大的数字产生
#   较窄的滤波器。最小值为 0.5，最大值为 3.0。默认：2.0
#tare_time:
#   每次探测前用于负载传感器去皮的时间（秒）。默认值为：
#   5 / 50 = 0.1。这从 50Hz/60Hz 市电的 5/6 个周期中收集样本
#   以消除电源线噪声。
#disable_pullback_move: False
#   设置为 True 时，禁用探针触发后的回退移动和敲击分析。
#   探针将使用原始触发位置，而不是敲击分析计算的 Z=0。
#   这会降低探针精度，但对于故障排除或兼容性测试可能有用。
#   默认为 False。
#pullback_distance: 0.2
#   慢慢抬起探针以执行精确 Z=0 测量的距离（mm）。此移动在
#   探针检测到接触后立即发生。该距离需要约为探针与床断开
#   接触所需距离的 2 倍。有效范围为 0.01 到 2.0 mm。
#   默认为 0.2 mm。
#pullback_speed:
#   探针触发后回退移动的速度（mm/s）。有效范围为 0.1 到 1.0 mm/s。
#   默认设置为每个传感器样本 1 微米 (0.001mm)。
#tap_classifier_module:
#   可选的自定义敲击验证模块。默认为 TapQualityClassifier。
#   设置自定义分类器会用您的实现覆盖 TapQualityClassifier。
#min_tap_quality: 40.0
#   最低可接受的敲击质量分数。有效范围为 0 到 100 百分比。
#   默认为 40%。
#decompression_angle:
#   干净敲击的解压线的平均角度。测量的解压角度与此角度偏差
#   越大，其敲击质量分数越差。没有默认值，必须测量。它是
#   0 到 90 之间的度数。
#max_approach_force: 50
#max_departure_force: 25
#max_baseline_force_delta: 25
#max_dwell_force_drop: 75
#   以百分比表示的敲击质量检查最大值。
#z_offset:
#speed:
#samples:
#sample_retract_dist:
#lift_speed:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#activate_gcode:
#deactivate_gcode:
#   有关上述参数的描述，请参阅 "[probe]" 部分。
```

有关敲击质量最大值的更多详细信息，请参见 [Tap Quality Components](Load_Cell.md#tap-quality-components)。

## 主板特定硬件支持

### [sx1509]

配置 SX1509 I2C 到 GPIO 扩展器。由于 I2C 通信造成的延迟，
您不应将 SX1509 引脚用作步进使能、步进或方向引脚或任何其他
需要快速位冲击的引脚。它们最适合作为静态或 gcode 控制的
数字输出或硬件 PWM 引脚（例如风扇）。可以定义任意数量
以 "sx1509" 为前缀的部分。每个扩展器提供一组 16 个引脚
（sx1509_my_sx1509:PIN_0 到 sx1509_my_sx1509:PIN_15），
可在打印机配置中使用。

参见 [generic-duet2-duex.cfg](../config/generic-duet2-duex.cfg)
文件了解示例。

```
[sx1509 my_sx1509]
i2c_address:
#   此扩展器使用的 I2C 地址。根据硬件跳线，这是以下地址之一：
#   62、63、112、113。此参数必须提供。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅 "common I2C settings" 部分。
```

### [samd_sercom]

SAMD SERCOM 配置，用于指定给定 SERCOM 上使用哪些引脚。
可以定义任意数量以 "samd_sercom" 为前缀的部分。每个 SERCOM
必须在用作 SPI 或 I2C 外设之前进行配置。将此配置部分放在
使用 SPI 或 I2C 总线的任何其他部分之前。

```
[samd_sercom my_sercom]
sercom:
#   要在微控制器中配置的 sercom 总线的名称。可用名称为
#   "sercom0"、"sercom1" 等。此参数必须提供。
tx_pin:
#   用于 SPI 通信的 MOSI 引脚，或用于 I2C 通信的 SDA（数据）引脚。
#   该引脚必须具有给定 SERCOM 外设的有效 pinmux 配置。
#   此参数必须提供。
#rx_pin:
#   用于 SPI 通信的 MISO 引脚。此引脚不用于 I2C 通信
#   （I2C 使用 tx_pin 同时发送和接收）。该引脚必须具有
#   给定 SERCOM 外设的有效 pinmux 配置。此参数是可选的。
clk_pin:
#   用于 SPI 通信的 CLK 引脚，或用于 I2C 通信的 SCL（时钟）引脚。
#   该引脚必须具有给定 SERCOM 外设的有效 pinmux 配置。
#   此参数必须提供。
```

### [adc_scaled]

Duet2 Maestro 通过 vref 和 vssa 读数进行模拟缩放。
定义 adc_scaled 部分会启用虚拟 ADC 引脚（如 "my_name:PB0"），
这些引脚会自动由板载 vref 和 vssa 监控引脚进行调整。
请确保将此配置部分放在使用这些虚拟引脚的任何配置部分之前。

参见 [generic-duet2-maestro.cfg](../config/generic-duet2-maestro.cfg)
文件了解示例。

```
[adc_scaled my_name]
vref_pin:
#   用于 VREF 监控的 ADC 引脚。此参数必须提供。
vssa_pin:
#   用于 VSSA 监控的 ADC 引脚。此参数必须提供。
#smooth_time: 2.0
#   vref 和 vssa 测量将被平滑的时间值（秒），以减少测量噪声
#   的影响。默认为 2 秒。
```

### [replicape]

Replicape 支持 - 参见 [beaglebone guide](Beaglebone.md) 和
[generic-replicape.cfg](../config/generic-replicape.cfg) 文件
了解示例。

```
# "replicape" 配置部分添加了 "replicape:stepper_x_enable"
# 虚拟步进使能引脚（用于步进器 X、Y、Z、E 和 H）和
# "replicape:power_x" PWM 输出引脚（用于热床、e、h、fan0、
# fan1、fan2 和 fan3），然后可以在配置文件的其他地方使用。
[replicape]
revision:
#   replicape 硬件版本。目前仅支持版本 "B3"。此参数必须提供。
#enable_pin: !gpio0_20
#   replicape 全局使能引脚。默认为 !gpio0_20（又名 P9_41）。
host_mcu:
#   与 Kalico "linux process" mcu 实例通信的 mcu 配置部分的名称。
#   此参数必须提供。
#standstill_power_down: False
#   此参数控制所有步进电机的 CFG6_ENN 线。True 将使能线设置为
#   "open"。默认为 False。
#stepper_x_microstep_mode:
#stepper_y_microstep_mode:
#stepper_z_microstep_mode:
#stepper_e_microstep_mode:
#stepper_h_microstep_mode:
#   此参数控制给定步进电机驱动器的 CFG1 和 CFG2 引脚。
#   可用选项为：disable、1、2、spread2、4、16、spread4、
#   spread16、stealth4 和 stealth16。默认为 disable。
#stepper_x_current:
#stepper_y_current:
#stepper_z_current:
#stepper_e_current:
#stepper_h_current:
#   步进电机驱动器配置的最大电流（安培）。如果步进器不在
#   disable 模式下，则必须提供此参数。
#stepper_x_chopper_off_time_high:
#stepper_y_chopper_off_time_high:
#stepper_z_chopper_off_time_high:
#stepper_e_chopper_off_time_high:
#stepper_h_chopper_off_time_high:
#   此参数控制步进电机驱动器的 CFG0 引脚（True 将 CFG0 设置为
#   高电平，False 将其设置为低电平）。默认为 False。
#stepper_x_chopper_hysteresis_high:
#stepper_y_chopper_hysteresis_high:

#stepper_z_chopper_hysteresis_high:
#stepper_e_chopper_hysteresis_high:
#stepper_h_chopper_hysteresis_high:
#   此参数控制步进电机驱动器的 CFG4 引脚
#   （True 将 CFG4 设为高电平，False 将其设为低电平）。默认值为 False。
#stepper_x_chopper_blank_time_high:
#stepper_y_chopper_blank_time_high:
#stepper_z_chopper_blank_time_high:
#stepper_e_chopper_blank_time_high:
#stepper_h_chopper_blank_time_high:
#   此参数控制步进电机驱动器的 CFG5 引脚
#   （True 将 CFG5 设为高电平，False 将其设为低电平）。默认值为 True。
```

## 其他自定义模块

### [palette2]

Palette 2 多材料支持 - 提供更紧密的集成，
支持以连接模式使用 Palette 2 设备。

此模块还需要 `[virtual_sdcard]` 和 `[pause_resume]`
才能实现完整功能。

如果您使用此模块，请不要使用 Octoprint 的 Palette 2 插件，
因为它们会冲突，其中一个可能无法正确初始化，
很可能导致您的打印中止。

如果您使用 Octoprint 并通过串口流式传输 gcode 而不是
从 virtual_sd 打印，那么在 _Settings > Serial Connection > Firmware & protocol_ 中的 _Pausing commands_ 里移除 **M1** 和 **M0**，
将避免在 Palette 2 上启动打印后还需要在 Octoprint 中取消暂停
才能开始打印的问题。

```
[palette2]
serial:
#   连接到 Palette 2 的串口。
#baud: 115200
#   使用的波特率。默认值为 115200。
#feedrate_splice: 0.8
#   拼接时使用的进给速率，默认值为 0.8
#feedrate_normal: 1.0
#   拼接后使用的进给速率，默认值为 1.0
#auto_load_speed: 2
#   自动加载时的挤出进给速率，默认值为 2（mm/s）
#auto_cancel_variation: 0.1
#   当 ping 变化超过此阈值时自动取消打印
```

### [angle]

磁性霍尔角度传感器支持，用于读取步进电机的角度轴测量值，
支持使用 a1333、as5047d、mt6816、mt6826s
或 tle5012b SPI 芯片。
测量结果可通过 [API Server](API_Server.md) 和
[运动分析工具](Debugging.md#motion-analysis-and-data-logging) 获取。
可用命令请参阅 [G-Code 参考](G-Codes.md#angle)。

```
[angle my_angle_sensor]
sensor_type:
#   磁性霍尔传感器芯片的类型。可选项有
#   "a1333"、"as5047d"、"mt6816"、"mt6826s" 和 "tle5012b"。此参数必须指定。
#sample_period: 0.000400
#   测量时使用的查询周期（以秒为单位）。
#   默认值为 0.000400（即每秒 2500 个采样点）。
#stepper:
#   角度传感器所连接的步进电机的名称（例如
#   "stepper_x"）。设置此值将启用角度校准
#   工具。要使用此功能，必须安装 Python "numpy" 包。
#   默认不启用角度传感器的角度校准。
cs_pin:
#   传感器的 SPI 使能引脚。此参数必须提供。
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   以上参数的说明请参见"通用 SPI 设置"部分。
```

### ⚠️ [tools_calibrate]

多工具头喷嘴偏移量校准，使用三轴喷嘴接触探针，
例如 [Zruncho3D 的 Nudge Probe](https://github.com/zruncho3d/nudge)。

```
[tools_calibrate]
pin:
travel_speed: 20
#   X 和 Y 轴移动速度，单位为 mm/sec
spread: 5
#spread_x:
#spread_y:
#   探针周围的 X 和 Y 轴移动距离
#initial_spread:
#initial_spread_x:
#initial_spread_y:
#   初始探针定位移动的 X 和 Y 轴移动距离
lower_z: 1.0
#   Z 轴下降与探针侧面接触的距离
speed: 2
#   探测之间回退的速度（mm/sec）
lift_speed: 4
#   探测后的 Z 轴抬升速度
final_lift_z: 6
#   校准后的 Z 轴抬升距离，必须大于
#   工具头之间的最大高度差
trigger_to_bottom_z: 0.25
#   从探针触发到垂直运动到底部的偏移量。
#   如果喷嘴太高则减小此值，太低则增大此值。
#samples: 1
#   每个点的探测次数。探测的 z 值将
#   取平均值。默认探测 1 次。
#sample_retract_dist: 2.0
#   每次采样之间抬起工具头的距离（mm）（如果
#   采样次数大于 1）。默认值为 2mm。
#samples_result: average
#   多次采样时的计算方法 - 可选
#   "median" 或 "average"。默认值为 average。
#samples_tolerance: 0.100
#   采样值与其他采样值之间允许的最大 Z 轴距离偏差（mm）。
#   如果超过此公差，则会报告错误或重新尝试
#   （请参见 samples_tolerance_retries）。默认值为 0.100mm。
```

### [trad_rack]

Trad Rack 多材料系统支持。更多信息请参阅 TradRack 仓库中的
以下文档：
- [Tuning.md](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md)：
  下方部分配置选项引用的文档。
- [Trad Rack 配置参考文档](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Config_Reference.md)：包含与 [trad_rack] 一起使用的
  其他配置部分的信息。

```
[trad_rack]
selector_max_velocity:
#   选择器的最大速度（mm/s）。
#   此参数必须指定。
selector_max_accel:
#   选择器的最大加速度（mm/s^2）。
#   此参数必须指定。
#filament_max_velocity:
#   耗材移动的最大速度（mm/s）。
#   默认值为 buffer_pull_speed。
#filament_max_accel: 1500.0
#   耗材移动的最大加速度（mm/s^2）。
#   默认值为 1500.0。
toolhead_fil_sensor_pin:
#   工具头耗材传感器连接的引脚。
#   如果未指定引脚，则不会使用工具头耗材传感器。
lane_count:
#   耗材通道的数量。此参数必须指定。
lane_spacing:
#   耗材通道之间的间距（mm）。
#   此参数必须指定。
#lane_offset_<lane index>:
#   带有 "lane_offset_" 前缀的选项可以为任何
#   通道（从 0 到 lane_count - 1）指定。该选项将对
#   对应通道的位置应用偏移量（mm）。通道偏移量
#   不会影响选项名称中指定的通道以外的任何通道的位置。
#   此选项用于微调每个通道的位置，以确保通道模块和
#   选择器中的耗材路径彼此对齐。
#   每个通道的默认值为 0.0。
#lane_spacing_mod_<lane index>:
#   带有 "lane_spacing_mod_" 前缀的选项可以为任何
#   通道（从 0 到 lane_count - 1）指定。该选项将对
#   对应通道以及所有更高索引通道的位置应用偏移量（mm）。
#   例如，如果 lane_spacing_mod_2 为 4.0，则索引为 2 或
#   更高的所有通道的位置将增加 4.0。此选项用于解决
#   通道模块的变化对其自身位置以及后续更高索引模块
#   位置的影响。
#   每个通道的默认值为 0.0。
servo_down_angle:
#   舵机下降位置的角度（度）。
#   此参数必须指定。
servo_up_angle:
#   舵机上升位置的角度（度）。
#   此参数必须指定。
#servo_wait_ms: 500
#   等待舵机完成上升和下降角度之间移动的时间（毫秒）。
#   默认值为 500。
selector_unload_length:
#   在选择器传感器触发或取消触发后，将一段耗材
#   从选择器中回退到通道模块的长度（mm）。
#   此参数必须指定。
#selector_unload_length_extra: 0.0
#   在将耗材从选择器回退到通道模块时，
#   添加到 selector_unload_length 的额外长度（mm）。
#   回退后，耗材也会向前移动此长度
#   （因此此选项的值对耗材的最终位置没有影响）。
#   当与带有电机驱动的线轴回卷器一起使用 Trad Rack 时，
#   此选项可能很有用，该回卷器通过感知耗材在线轴和
#   Trad Rack 之间的张力或压缩来确定何时旋转线轴。
#   回退后耗材的额外向前移动旨在迫使回卷器的传感器
#   检测到耗材中的张力，从而使回卷立即停止，
#   以免耗材尖端被多余的线轴移动移出位置。
#   默认值为 0.0。
#eject_length: 10.0
#   在卸载耗尽的线轴后，将耗材弹射到通道模块中
#   超过 selector_unload_length 定义长度的距离（mm）。
#   每次卸载耗尽的线轴时都会弹射耗材，
#   以确保在该段耗材被更换之前不会再次加载。
bowden_length:
#   在加载和卸载期间，通过波顿管在 Trad Rack 和
#   工具头之间快速移动耗材的长度（mm）。
#   详情请参见 Tuning.md。此参数必须指定。
extruder_load_length:
#   加载工具头时将耗材移入挤出机的长度（mm）。
#   详情请参见 Tuning.md。
#   此参数必须指定。
hotend_load_length:
#   加载工具头时将耗材移入热端的长度（mm）。
#   详情请参见 Tuning.md。
#   此参数必须指定。
toolhead_unload_length:
#   卸载时将耗材移出工具头的长度（mm）。
#   详情请参见 Tuning.md。如果指定了 toolhead_fil_sensor_pin，
#   则必须指定此参数。
#   如果未指定 toolhead_fil_sensor_pin，
#   默认值为 extruder_load_length + hotend_load_length。
#selector_sense_speed: 40.0
#   在移动耗材直到选择器传感器触发或取消触发时的速度（mm/s）。
#   有关此速度的应用场景，请参见 Tuning.md。
#   默认值为 40.0。
#selector_unload_speed: 60.0
#   卸载选择器时移动耗材的速度（mm/s）。
#   默认值为 60.0。
#eject_speed: 80.0
#   将耗材段弹射到通道模块中时的移动速度（mm/s）。
#spool_pull_speed: 100.0
#   从线轴加载时通过波顿管移动耗材的速度（mm/s）。
#   详情请参见 Tuning.md。
#   默认值为 100.0。
#buffer_pull_speed:
#   从缓冲区卸载或加载时通过波顿管移动耗材的速度（mm/s）。
#   详情请参见 Tuning.md。
#   默认值为 spool_pull_speed。
#toolhead_sense_speed:
#   在移动耗材直到工具头传感器触发或取消触发时的速度（mm/s）。
#   有关此速度的应用场景，请参见 Tuning.md。
#   默认值为 selector_sense_speed。
#extruder_load_speed:
#   加载工具头时将耗材移入挤出机的速度（mm/s）。
#   详情请参见 Tuning.md。默认值为 60.0。
#hotend_load_speed:
#   加载工具头时将耗材移入热端的速度（mm/s）。
#   详情请参见 Tuning.md。默认值为 7.0。
#toolhead_unload_speed:
#   卸载工具头时移动耗材的速度（mm/s）。
#   详情请参见 Tuning.md。默认值为 extruder_load_speed。
#load_with_toolhead_sensor: True
#   加载工具头时是否使用工具头传感器。
#   详情请参见 Tuning.md。默认值为 True，但如果未指定
#   toolhead_fil_sensor_pin，则忽略此选项。
#unload_with_toolhead_sensor: True
#   卸载工具头时是否使用工具头传感器。
#   详情请参见 Tuning.md。默认值为 True，但如果未指定
#   toolhead_fil_sensor_pin，则忽略此选项。
#fil_homing_retract_dist: 20.0
#   在进行下一步移动之前，将耗材从耗材传感器处
#   回退的距离（mm）。每当在通过波顿管的快速移动中
#   耗材传感器提前触发时，就会发生此回退。
#   详情请参见 Tuning.md。默认值为 20.0。
#target_toolhead_homing_dist:
#   加载时向工具头耗材传感器归位的目标耗材移动距离（mm）。
#   详情请参见 Tuning.md。
#   默认值为 10.0 或 toolhead_unload_length 中的较大值。
#target_selector_homing_dist:
#   卸载时向选择器耗材传感器归位的目标耗材移动距离（mm）。
#   详情请参见 Tuning.md。默认值为 10.0。
#bowden_length_samples: 10
#   用于设置加载和卸载波顿长度的最大平均采样数。
#   详情请参见 Tuning.md。默认值为 10。
#load_lane_time: 15
#   使用 TR_LOAD_LANE gcode 命令加载通道时，
#   等待耗材到达选择器耗材传感器的大致最大时间（秒）。
#   此时间从提示用户插入耗材时开始计时，
#   并决定在未检测到耗材时提前终止命令的时间。
#   默认值为 15。
#load_selector_homing_dist:
#   从通道模块加载到选择器耗材传感器时，
#   在终止归位移动之前尝试移动耗材的最大距离。
#   此值不被 TR_LOAD_LANE 命令使用，但用于
#   不涉及用户交互的类似场景。
#   默认值为 selector_unload_length * 2。
#bowden_load_homing_dist:
#   在工具头加载接近尾声时（在向工具头传感器的
#   慢速归位移动期间），在终止归位移动之前
#   尝试移动耗材的最大距离。默认值为 bowden_length。
#bowden_unload_homing_dist:
#   在工具头卸载接近尾声时（在向选择器传感器的
#   慢速归位移动期间），在终止归位移动之前
#   尝试移动耗材的最大距离。默认值为 bowden_length。
#unload_toolhead_homing_dist:
#   在工具头卸载开始时（在向工具头传感器的
#   归位移动期间），在终止归位移动之前
#   尝试移动耗材的最大距离。
#   默认值为 (extruder_load_length + hotend_load_length) * 2。
#sync_to_extruder: False
#   在打印期间以及工具头加载或卸载中的任何
#   通常仅涉及挤出机的挤出移动期间，
#   将 Trad Rack 的耗材驱动器与挤出机同步。
#   默认值为 False。
#user_wait_time: 15
#   在自动继续之前等待用户操作的时间（秒）。
#   如果设置为 -1，Trad Rack 将无限期等待用户。
#   此值当前由 TR_LOCATE_SELECTOR gcode 命令使用。
#   默认值为 15。
#register_toolchange_commands: True
#   是否注册 gcode 命令 T0、T1、T2 等，以便它们
#   可用于通过 Trad Rack 发起工具切换。如果设置为
#   False，仍可使用 TR_LOAD_TOOLHEAD 命令作为
#   替代方案来发起工具切换。默认值为 True。
#save_active_lane: True
#   使用 save_variables 设置活动通道时是否将其保存到磁盘。
#   如果设置为 True，当选择器耗材传感器触发且之前保存过
#   活动通道时，TR_LOCATE_SELECTOR gcode 命令将推断
#   活动通道。默认值为 True。
#log_bowden_lengths: False
#   是否记录波顿加载长度数据和波顿卸载长度数据
#   （分别记录到 ~/bowden_load_lengths.csv 和
#   ~/bowden_unload_lengths.csv）。默认值为 False。
#pre_unload_gcode:
#   工具头卸载前运行的 Gcode 命令模板。
#   默认不运行额外命令。
#post_unload_gcode:
#   工具头卸载后运行的 Gcode 命令模板。
#   默认不运行额外命令。
#pre_load_gcode:
#   工具头加载前运行的 Gcode 命令模板。
#   默认不运行额外命令。
#post_load_gcode:
#   工具头加载后运行的 Gcode 命令模板。
#   默认不运行额外命令。
#pause_gcode:
#   当 Trad Rack 需要暂停打印时（通常由于加载或卸载失败）
#   运行的 Gcode 命令模板。默认运行 PAUSE gcode 命令。
#resume_gcode:
#   当 TR_RESUME 命令需要恢复打印时
#   运行的 Gcode 命令模板。默认运行 RESUME gcode 命令。
```

## 通用总线参数

### 通用 SPI 设置

以下参数通常适用于使用 SPI 总线的设备。

```
#spi_speed:
#   与设备通信时使用的 SPI 速度（Hz）。
#   默认值取决于设备类型。
#spi_bus:
#   如果微控制器支持多个 SPI 总线，则可以在此处指定
#   微控制器总线名称。默认值取决于微控制器类型。
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   指定以上参数以使用"基于软件的 SPI"。此模式不需要
#   微控制器硬件支持（通常可以使用任何通用引脚）。
#   默认不使用"软件 spi"。
```

### 通用 I2C 设置

以下参数通常适用于使用 I2C 总线的设备。

请注意，Kalico 当前微控制器对 I2C 的支持
通常不能容忍线路噪声。I2C 线上的意外错误可能导致
Kalico 抛出运行时错误。Kalico 对错误恢复的支持
因微控制器类型而异。通常建议仅使用与微控制器在
同一印刷电路板上的 I2C 设备。

大多数 Kalico 微控制器实现仅支持 100000 的
`i2c_speed`（_标准模式_，100kbit/s）。Kalico "Linux"
微控制器支持 400000 速度（_快速模式_，400kbit/s），但必须
[在操作系统中设置](RPi_microcontroller.md#optional-enabling-i2c)，
`i2c_speed` 参数在其他情况下会被忽略。Kalico
"RP2040" 微控制器和 ATmega AVR 系列以及部分 STM32
（F0、G0、G4、L4、F7、H7）支持通过 `i2c_speed` 参数设置 400000 的速率。
所有其他 Kalico 微控制器使用 100000 的速率
并忽略 `i2c_speed` 参数。

```
#i2c_address:
#   设备的 i2c 地址。必须以十进制数字指定
#   （不能使用十六进制）。默认值取决于设备类型。
#i2c_mcu:
#   芯片所连接的微控制器的名称。
#   默认值为 "mcu"。
#i2c_bus:
#   如果微控制器支持多个 I2C 总线，则可以在此处指定
#   微控制器总线名称。默认值取决于微控制器类型。
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#   指定这些参数以使用基于微控制器软件的
#   I2C "bit-banging" 支持。这两个参数应指定微控制器上
#   用于 scl 和 sda 线路的两个引脚。
#   默认使用由 i2c_bus 参数指定的基于硬件的 I2C 支持。
#i2c_speed:
#   与设备通信时使用的 I2C 速度（Hz）。
#   大多数微控制器上的 Kalico 实现硬编码为
#   100000，更改此值无效。默认值为 100000。
#   Linux、RP2040 和 ATmega 支持 400000。
```