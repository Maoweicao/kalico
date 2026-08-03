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
#   The serial port to connect to the MCU. If unsure (or if it
#   changes) see the "Where's my serial port?" section of the FAQ.
#   This parameter must be provided when using a serial port.
#baud: 250000
#   The baud rate to use. The default is 250000.
#canbus_uuid:
#   If using a device connected to a CAN bus then this sets the unique
#   chip identifier to connect to. This value must be provided when using
#   CAN bus for communication.
#canbus_interface:
#   If using a device connected to a CAN bus then this sets the CAN
#   network interface to use. The default is 'can0'.
#restart_method:
#   This controls the mechanism the host will use to reset the
#   micro-controller. The choices are 'arduino', 'cheetah', 'rpi_usb',
#   and 'command'. The 'arduino' method (toggle DTR) is common on
#   Arduino boards and clones. The 'cheetah' method is a special
#   method needed for some Fysetc Cheetah boards. The 'rpi_usb' method
#   is useful on Raspberry Pi boards with micro-controllers powered
#   over USB - it briefly disables power to all USB ports to
#   accomplish a micro-controller reset. The 'command' method involves
#   sending a Kalico command to the micro-controller so that it can
#   reset itself. The default is 'arduino' if the micro-controller
#   communicates over a serial port, 'command' otherwise.
#is_non_critical: False
#   Setting this to True will allow the mcu to be disconnected and
#   reconnected at will without errors. Helpful for USB-accelerometer boards
#   and USB/CAN-probes
```

### [mcu my_extra_mcu]

额外微控制器（可以定义任意数量的前缀为"mcu"的配置段）。额外微控制器会引入额外的引脚，可配置为加热器、步进电机、风扇等。例如，如果引入了"[mcu extra_mcu]"配置段，则可以在配置文件的其他位置使用"extra_mcu:ar9"等引脚（其中"ar9"是给定MCU上的硬件引脚名或别名）。

```
[mcu my_extra_mcu]
# See the "mcu" section for configuration parameters.
```

## ⚠️ 危险选项

一组Kalico特有的系统选项

```
[danger_options]
#error_on_unused_config_options: True
#   If an unused config option or section should cause an error
#   if False, will warn but allow Kalico to still run.
#   The default is True.
#allow_plugin_override: False
#   Allows modules in `plugins` to override modules of the same name in `extras`
#   The default is False.
#single_mcu_trsync_timeout: 0.25
#   The timeout (in seconds) for MCU synchronization during the homing process when
#   a single MCUs is in use. The default is 0.25
#multi_mcu_trsync_timeout: 0.025
#   The timeout (in seconds) for MCU synchronization during the homing process when
#   multiple MCUs are in use. The default is 0.025
#homing_elapsed_distance_tolerance: 0.5
#   Tolerance (in mm) for distance moved in the second homing. Ensures the
#   second homing distance closely matches the `min_home_dist` when using
#   sensorless homing. The default is 0.5mm.
#temp_ignore_limits: False
#   When set to true, this parameter ignores the min_value and max_value
#   limits for temperature sensors. It prevents shutdowns due to
#   'ADC out of range' and similar errors by allowing readings outside the
#   specified range without triggering a shutdown. The default is False.
#autosave_includes: False
#   When set to true, SAVE_CONFIG will recursively read [include ...] blocks
#   for conflicts to autosave data. Any configurations updated will be backed
#   up to configs/config_backups.
#bgflush_extra_time: 0.250
#   This allows to set extra flush time (in seconds). Under certain conditions,
#   a low value will result in an error if message is not get flushed, a high value
#   (0.250) will result in homing/probing latency. The default is 0.250
#homing_start_delay: 0.001
#   How long to dwell before beginning a drip move for homing
#endstop_sample_time: 0.000015
#   How often the MCU should sample the endstop state
#endstop_sample_count: 4
#   How many times we should check the endstop state when homing
#   Unless your endstop is noisy and unreliable, you should be able to lower this to 1

# Extruder safety limit overrides:
#override_pressure_advance_smooth_time_max: 0.200
#   Override maximum for pressure_advance_smooth_time (config and
#   SET_PRESSURE_ADVANCE). Useful for non-standard setups that need
#   values beyond the built-in default. The default is 0.200.

# Logging options:

#minimal_logging: False
#   Set the default for all log options. The default is False.
#log_statistics: True
#   If statistics should be logged
#   (helpful for keeping the log clean during development)
#   The default is True.
#log_config_file_at_startup: True
#   If the config file should be logged at startup
#   The default is True.
#log_bed_mesh_at_startup: True
#   If the bed mesh should be logged at startup
#   (helpful for keeping the log clean during development)
#   The default is True.
#log_velocity_limit_changes: True
#   If changes to velocity limits should be logged. If False, velocity limits will only
#   be logged at rollover. Some slicers emit very frequent SET_VELOCITY_LIMIT commands
#   The default is True
#log_pressure_advance_changes: True
#   If changes to pressure advance should be logged. If false, pressure advance data
#   will only be logged at rollover.
#   The default is True.
#log_shutdown_info: True
#   If we should log detailed crash info when an exception occurs
#   Most of it is overly-verbose and fluff and we still get a stack trace
#   for normal exceptions, so setting to False can help save time while developing
#   The default is True.
#log_serial_reader_warnings: True
#log_startup_info: True
#log_webhook_method_register_messages: False
#log_component_interactions: False
#   When set to True, enables detailed debug logging of all hardware
#   component interactions (heaters PWM/temp, toolhead moves, stepper
#   direction/position/homing, MCU commands, etc.) at DEBUG level.
#   Use together with the -v CLI flag or log_module_categories for
#   enhanced diagnostics. The default is False.
#log_module_categories: False
#   When set to True, creates separate per-module log files
#   (module_heaters.log, module_toolhead.log, module_stepper.log,
#   module_mcu.log, etc.) in the same directory as the main log file.
#   Each file contains only log entries from its respective module.
#   The default is False.
```

## ⚠️ 配置引用

在配置中，可以引用其他值以在多个配置段之间共享配置。引用的形式为 `${option}` 以复制当前配置段中的值，或 `${section.option}` 以查找配置中其他位置的值。注意，常量必须始终为小写。

引用是纯文本替换：引用的值按原样复制。表达式和类似Python的函数不会被求值。

可以选择使用 `[constants]` 配置段专门存储这些值。未使用的常量会显示警告。但是，如果没有任何常量被使用，`[constants]` 会显示错误。

```
[constants]
run_current_ab:  1.0
i_am_not_used: True  # Will show "Constant 'i_am_not_used' is unused"

[tmc5160 stepper_x]
run_current: ${constants.run_current_ab}

[tmc5160 stepper_y]
run_current: ${tmc5160 stepper_x.run_current}
#   Nested references work, but are not advised
```

如果需要，可以使用 `\${such}` 转义引用

## 通用运动学设置

### [printer]

printer配置段控制高层打印机设置。

```
[printer]
kinematics:
#   The type of printer in use. This option may be one of: cartesian,
#   corexy, corexz, hybrid_corexy, hybrid_corexz, rotary_delta, delta,
#   deltesian, polar, winch, or none. This parameter must be specified.
max_velocity:
#   Maximum velocity (in mm/s) of the toolhead (relative to the
#   print). This value may be changed at runtime using the
#   SET_VELOCITY_LIMIT command. This parameter must be specified.
max_accel:
#   Maximum acceleration (in mm/s^2) of the toolhead (relative to the
#   print). Although this parameter is described as a "maximum"
#   acceleration, in practice most moves that accelerate or decelerate
#   will do so at the rate specified here. The value specified here
#   may be changed at runtime using the SET_VELOCITY_LIMIT command.
#   This parameter must be specified.
#minimum_cruise_ratio: 0.5
#   Most moves will accelerate to a cruising speed, travel at that
#   cruising speed, and then decelerate. However, some moves that
#   travel a short distance could nominally accelerate and then
#   immediately decelerate. This option reduces the top speed of these
#   moves to ensure there is always a minimum distance traveled at a
#   cruising speed. That is, it enforces a minimum distance traveled
#   at cruising speed relative to the total distance traveled. It is
#   intended to reduce the top speed of short zigzag moves (and thus
#   reduce printer vibration from these moves). For example, a
#   minimum_cruise_ratio of 0.5 would ensure that a standalone 1.5mm
#   move would have a minimum cruising distance of 0.75mm. Specify a
#   ratio of 0.0 to disable this feature (there would be no minimum
#   cruising distance enforced between acceleration and deceleration).
#   The value specified here may be changed at runtime using the
#   SET_VELOCITY_LIMIT command. The default is 0.5.
#square_corner_velocity: 5.0
#   The maximum velocity (in mm/s) that the toolhead may travel a 90
#   degree corner at. A non-zero value can reduce changes in extruder
#   flow rates by enabling instantaneous velocity changes of the
#   toolhead during cornering. This value configures the internal
#   centripetal velocity cornering algorithm; corners with angles
#   larger than 90 degrees will have a higher cornering velocity while
#   corners with angles less than 90 degrees will have a lower
#   cornering velocity. If this is set to zero then the toolhead will
#   decelerate to zero at each corner. The value specified here may be
#   changed at runtime using the SET_VELOCITY_LIMIT command. The
#   default is 5mm/s.
```

### [stepper]

步进电机定义。不同打印机类型（由[printer]配置段中的"kinematics"选项指定）需要不同的步进电机名称（例如，`stepper_x` vs `stepper_a`）。以下是常见的步进电机定义。

有关计算`rotation_distance`参数的信息，请参见[旋转距离文档](Rotation_Distance.md)。有关使用多个微控制器归位的信息，请参见[多MCU归位](Multi_MCU_Homing.md)文档。

```
[stepper_x]
step_pin:
#   Step GPIO pin (triggered high). This parameter must be provided.
dir_pin:
#   Direction GPIO pin (high indicates positive direction). This
#   parameter must be provided.
enable_pin:
#   Enable pin (default is enable high; use ! to indicate enable
#   low). If this parameter is not provided then the stepper motor
#   driver must always be enabled.
rotation_distance:
#   Distance (in mm) that the axis travels with one full rotation of
#   the stepper motor (or final gear if gear_ratio is specified).
#   This parameter must be provided.
microsteps:
#   The number of microsteps the stepper motor driver uses. This
#   parameter must be provided.
#full_steps_per_rotation: 200
#   The number of full steps for one rotation of the stepper motor.
#   Set this to 200 for a 1.8 degree stepper motor or set to 400 for a
#   0.9 degree motor. The default is 200.
#gear_ratio:
#   The gear ratio if the stepper motor is connected to the axis via a
#   gearbox. For example, one may specify "5:1" if a 5 to 1 gearbox is
#   in use. If the axis has multiple gearboxes one may specify a comma
#   separated list of gear ratios (for example, "57:11, 2:1"). If a
#   gear_ratio is specified then rotation_distance specifies the
#   distance the axis travels for one full rotation of the final gear.
#   The default is to not use a gear ratio.
#step_pulse_duration:
#   The minimum time between the step pulse signal edge and the
#   following "unstep" signal edge. This is also used to set the
#   minimum time between a step pulse and a direction change signal.
#   The default is 0.000000100 (100ns) for TMC steppers that are
#   configured in UART or SPI mode, and the default is 0.000002 (which
#   is 2us) for all other steppers.
endstop_pin:
#   Endstop switch detection pin. If this endstop pin is on a
#   different mcu than the stepper motor then it enables "multi-mcu
#   homing". This parameter must be provided for the X, Y, and Z
#   steppers on cartesian style printers.
#position_min: 0
#   Minimum valid distance (in mm) the user may command the stepper to
#   move to.  The default is 0mm.
position_endstop:
#   Location of the endstop (in mm). This parameter must be provided
#   for the X, Y, and Z steppers on cartesian style printers.
position_max:
#   Maximum valid distance (in mm) the user may command the stepper to
#   move to. This parameter must be provided for the X, Y, and Z
#   steppers on cartesian style printers.
#homing_speed: 5.0
#   Maximum velocity (in mm/s) of the stepper when homing. The default
#   is 5mm/s.
#homing_accel:
#   Maximum accel (in mm/s) of the stepper when homing. The default
#   is to use the max accel configured in the [printer]'s object.
#homing_retract_dist: 5.0
#   Distance to backoff (in mm) before homing a second time during
#   homing. If `use_sensorless_homing` is false, this setting can be set
#   to zero to disable the second home. If `use_sensorless_homing` is
#   true, this setting can be > 0 to backoff after homing. The default
#   is 5mm.
#homing_retract_speed:
#   Speed to use on the retract move after homing in case this should
#   be different from the homing speed, which is the default for this
#   parameter
#min_home_dist:
#   Minimum distance (in mm) for toolhead before sensorless homing. If closer
#   than `min_home_dist` to endstop, it moves away to this distance, then homes.
#   If further, it directly homes and retracts to `homing_retract_dist`.
#   The default is equal to `homing_retract_dist`.
#second_homing_speed:
#   Velocity (in mm/s) of the stepper when performing the second home.
#   The default is homing_speed/2. If `use_sensorless_homing` is
#   true, the default is homing_speed.
#homing_positive_dir:
#   If true, homing will cause the stepper to move in a positive
#   direction (away from zero); if false, home towards zero. It is
#   better to use the default than to specify this parameter. The
#   default is true if position_endstop is near position_max and false
#   if near position_min.
#use_sensorless_homing:
#   If true, disables the second home action if homing_retract_dist > 0.
#   The default is true if endstop_pin is configured to use virtual_endstop
```

### 直角坐标运动学

查看 [example-cartesian.cfg](../config/example-cartesian.cfg) 获取直角坐标运动学配置文件的示例。

此处仅描述直角坐标打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: cartesian
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. This setting can be used to restrict the maximum speed of
#   the z stepper motor. The default is to use max_velocity for
#   max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. It limits the acceleration of the z stepper motor. The
#   default is to use max_accel for max_z_accel.

# The stepper_x section is used to describe the stepper controlling
# the X axis in a cartesian robot.
[stepper_x]

# The stepper_y section is used to describe the stepper controlling
# the Y axis in a cartesian robot.
[stepper_y]

# The stepper_z section is used to describe the stepper controlling
# the Z axis in a cartesian robot.
[stepper_z]
```

### ⚠️ 带X和Y轴限制的直角坐标运动学

行为与直角坐标运动学完全相同，但允许为 X 和 Y 轴设置速度和加速度限制。这还使得命令
[`SET_KINEMATICS_LIMIT`](./G-Codes.md#set_kinematics_limit) 可用，以便在运行时设置这些限制。


```
[printer]
kinematics: limited_cartesian
max_x_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the x
#   axis. This setting can be used to restrict the maximum speed of
#   the x stepper motor. The default is to use max_velocity for
#   max_x_velocity.
max_y_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the y
#   axis. This setting can be used to restrict the maximum speed of
#   the y stepper motor. The default is to use max_velocity for
#   max_x_velocity.
max_z_velocity:
#   See cartesian above.
max_velocity:
#   In order to get maximum velocity gains on diagonals, this should be equal or
#   greater than the hypotenuse (sqrt(x*x + y*y)) of max_x_velocity and
#   max_y_velocity.
max_x_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the x axis. It limits the acceleration of the x stepper motor. The
#   default is to use max_accel for max_x_accel.
max_y_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the y axis. It limits the acceleration of the y stepper motor. The
#   default is to use max_accel for max_y_accel.
max_z_accel:
# See cartesian above.
max_accel:
# See cartesian above.
scale_xy_accel: False
#   When true, scales the XY limits by the current tool head acceleration.
#   The factor is: slicer accel / hypot(max_x_accel, max_y_accel).
#   See below.
```

如果 scale_xy_accel 为 `False`，由 `max_accel`、M204 或 SET_VELOCITY_LIMIT 设置的加速度将作为第三个限制。在这种情况下，此模块不会对加速度低于 `max_x_accel` 和 `max_y_accel` 的运动施加限制。当 scale_xy_accel 为 `True` 时，`max_x_accel` 和 `max_y_accel` 将按动态设置的加速度与 `max_x_accel` 和 `max_y_accel` 的斜边的比率进行缩放，该比率由 `SET_KINEMATICS_LIMIT` 报告。这意味着实际加速度将始终取决于方向。例如，以下设置：

```
[printer]
max_x_accel: 12000
max_y_accel: 9000
scale_xy_accel: true
```

`SET_KINEMATICS_LIMIT` 将报告在 37° 对角线上最大加速度为 15000 mm/s^2。如果切片器发出 `M204 S3000`（3000 mm/s^2 加速度）。在这些 37° 和 143° 对角线上，工具头将以 3000 mm/s^2 加速。在 X 轴上，加速度将为 12000 * 3000 / 15000 = 2400 mm/s^2，而纯 Y 运动为 18000 mm/s^2。

### 线性Delta运动学

查看 [example-delta.cfg](../config/example-delta.cfg) 获取线性 delta 运动学配置文件的示例。参见 [delta 标定指南](Delta_Calibrate.md) 了解标定信息。

此处仅描述线性delta打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: delta
max_z_velocity:
#   For delta printers this limits the maximum velocity (in mm/s) of
#   moves with z axis movement. This setting can be used to reduce the
#   maximum speed of up/down moves (which require a higher step rate
#   than other moves on a delta printer). The default is to use
#   max_velocity for max_z_velocity.
#max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. Setting this may be useful if the printer can reach higher
#   acceleration on XY moves than Z moves (eg, when using input shaper).
#   The default is to use max_accel for max_z_accel.
#minimum_z_position: 0
#   The minimum Z position that the user may command the head to move
#   to. The default is 0.
delta_radius:
#   Radius (in mm) of the horizontal circle formed by the three linear
#   axis towers. This parameter may also be calculated as:
#    delta_radius = smooth_rod_offset - effector_offset - carriage_offset
#   This parameter must be provided.
#print_radius:
#   The radius (in mm) of valid toolhead XY coordinates. One may use
#   this setting to customize the range checking of toolhead moves. If
#   a large value is specified here then it may be possible to command
#   the toolhead into a collision with a tower. The default is to use
#   delta_radius for print_radius (which would normally prevent a
#   tower collision).

# The stepper_a section describes the stepper controlling the front
# left tower (at 210 degrees). This section also controls the homing
# parameters (homing_speed, homing_retract_dist) for all towers.
[stepper_a]
position_endstop:
#   Distance (in mm) between the nozzle and the bed when the nozzle is
#   in the center of the build area and the endstop triggers. This
#   parameter must be provided for stepper_a; for stepper_b and
#   stepper_c this parameter defaults to the value specified for
#   stepper_a.
arm_length:
#   Length (in mm) of the diagonal rod that connects this tower to the
#   print head. This parameter must be provided for stepper_a; for
#   stepper_b and stepper_c this parameter defaults to the value
#   specified for stepper_a.
#angle:
#   This option specifies the angle (in degrees) that the tower is
#   at. The default is 210 for stepper_a, 330 for stepper_b, and 90
#   for stepper_c.

# The stepper_b section describes the stepper controlling the front
# right tower (at 330 degrees).
[stepper_b]

# The stepper_c section describes the stepper controlling the rear
# tower (at 90 degrees).
[stepper_c]

# The delta_calibrate section enables a DELTA_CALIBRATE extended
# g-code command that can calibrate the tower endstop positions and
# angles.
[delta_calibrate]
radius:
#   Radius (in mm) of the area that may be probed. This is the radius
#   of nozzle coordinates to be probed; if using an automatic probe
#   with an XY offset then choose a radius small enough so that the
#   probe always fits over the bed. This parameter must be provided.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#use_probe_xy_offsets: False
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is False.
```

### Deltesian运动学

查看 [example-deltesian.cfg](../config/example-deltesian.cfg) 获取 Deltesian 运动学配置文件的示例。

此处仅描述Deltesian打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: deltesian
max_z_velocity:
#   For deltesian printers, this limits the maximum velocity (in mm/s) of
#   moves with z axis movement. This setting can be used to reduce the
#   maximum speed of up/down moves (which require a higher step rate
#   than other moves on a deltesian printer). The default is to use
#   max_velocity for max_z_velocity.
#max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. Setting this may be useful if the printer can reach higher
#   acceleration on XY moves than Z moves (eg, when using input shaper).
#   The default is to use max_accel for max_z_accel.
#minimum_z_position: 0
#   The minimum Z position that the user may command the head to move
#   to. The default is 0.
#min_angle: 5
#   This represents the minimum angle (in degrees) relative to horizontal
#   that the deltesian arms are allowed to achieve. This parameter is
#   intended to restrict the arms from becoming completely horizontal,
#   which would risk accidental inversion of the XZ axis. The default is 5.
#print_width:
#   The distance (in mm) of valid toolhead X coordinates. One may use
#   this setting to customize the range checking of toolhead moves. If
#   a large value is specified here then it may be possible to command
#   the toolhead into a collision with a tower. This setting usually
#   corresponds to bed width (in mm).
#slow_ratio: 3
#   The ratio used to limit velocity and acceleration on moves near the
#   extremes of the X axis. If vertical distance divided by horizontal
#   distance exceeds the value of slow_ratio, then velocity and
#   acceleration are limited to half their nominal values. If vertical
#   distance divided by horizontal distance exceeds twice the value of
#   the slow_ratio, then velocity and acceleration are limited to one
#   quarter of their nominal values. The default is 3.

# The stepper_left section is used to describe the stepper controlling
# the left tower. This section also controls the homing parameters
# (homing_speed, homing_retract_dist) for all towers.
[stepper_left]
position_endstop:
#   Distance (in mm) between the nozzle and the bed when the nozzle is
#   in the center of the build area and the endstops are triggered. This
#   parameter must be provided for stepper_left; for stepper_right this
#   parameter defaults to the value specified for stepper_left.
arm_length:
#   Length (in mm) of the diagonal rod that connects the tower carriage to
#   the print head. This parameter must be provided for stepper_left; for
#   stepper_right, this parameter defaults to the value specified for
#   stepper_left.
arm_x_length:
#   Horizontal distance between the print head and the tower when the
#   printers is homed. This parameter must be provided for stepper_left;
#   for stepper_right, this parameter defaults to the value specified for
#   stepper_left.

# The stepper_right section is used to describe the stepper controlling the
# right tower.
[stepper_right]

# The stepper_y section is used to describe the stepper controlling
# the Y axis in a deltesian robot.
[stepper_y]
```

### CoreXY运动学

查看 [example-corexy.cfg](../config/example-corexy.cfg) 获取 CoreXY（和 h-bot）运动学配置文件的示例。

此处仅描述CoreXY打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: corexy
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. This setting can be used to restrict the maximum speed of
#   the z stepper motor. The default is to use max_velocity for
#   max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. It limits the acceleration of the z stepper motor. The
#   default is to use max_accel for max_z_accel.

# The stepper_x section is used to describe the X axis as well as the
# stepper controlling the X+Y movement.
[stepper_x]

# The stepper_y section is used to describe the Y axis as well as the
# stepper controlling the X-Y movement.
[stepper_y]

# The stepper_z section is used to describe the stepper controlling
# the Z axis.
[stepper_z]
```

### ⚠️ 带X和Y轴限制的CoreXY运动学

行为与 CoreXY 运动学完全相同，但允许为 X 和 Y 轴设置加速度限制。

X 和 Y 没有速度限制，因为在 CoreXY 上，两个轴的拉出速度是相同的。


```
[printer]
kinematics: limited_corexy
max_z_velocity:
#   See CoreXY above.
max_x_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the x axis. It limits the acceleration of the x stepper motor. The
#   default is to use max_accel for max_x_accel.
max_y_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the y axis. It limits the acceleration of the y stepper motor. The
#   default is to use max_accel for max_y_accel.
max_z_accel:
# See CoreXY above.
max_accel:
# See CoreXY above..
scale_xy_accel:
#   When True, scales the XY limits by the current tool head acceleration.
#   The factor is: slicer accel / max(max_x_accel, max_y_accel).
```

### CoreXZ运动学

查看 [example-corexz.cfg](../config/example-corexz.cfg) 获取CoreXZ运动学配置文件的示例。

此处仅描述CoreXZ打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

```
[printer]
kinematics: corexz
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. The default is to use max_velocity for max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. The default is to use max_accel for max_z_accel.

# The stepper_x section is used to describe the X axis as well as the
# stepper controlling the X+Z movement.
[stepper_x]

# The stepper_y section is used to describe the stepper controlling
# the Y axis.
[stepper_y]

# The stepper_z section is used to describe the Z axis as well as the
# stepper controlling the X-Z movement.
[stepper_z]
```

### ⚠️ 带X和Y轴限制的CoreXZ运动学

```
[printer]
kinematics: limited_corexz
max_velocity: 500 # Hypotenuse of the two values bellow
max_x_velocity: 400
max_y_velocity: 300
max_z_velocity: 5
max_accel: 1500 # Default acceleration of your choice
max_x_accel: 12000
max_y_accel: 9000
max_z_accel: 100
scale_xy_accel: [True/False, default False]
```

`max_velocity` is usually the hypotenuses of X and Y velocity, For example:
with `max_x_velocity: 300` and `max_y_velocity: 400`, the recommended value
is `max_velocity: 500`.

If `scale_xy_accel` is False, `max_accel`, set by `M204` or
`SET_VELOCITY_LIMIT`, acts as a third limit. In that case, this module
doesn't apply limitations to moves with an acceleration lower than
`max_x_accel` and `max_y_accel`.

When `scale_xy_accel` is `True`, `max_x_accel` and `max_y_accel` are scaled by
the ratio of the dynamically set acceleration and the hypotenuse of
`max_x_accel` and `max_y_accel`, as reported from `SET_KINEMATICS_LIMIT`.
This means that the actual acceleration will always depend on the
direction.

For example with these settings:
```
[printer]
max_x_accel: 12000
max_y_accel: 9000
scale_xy_accel: True
```

SET_KINEMATICS_LIMIT will report a maximum acceleration of 15000 mm/s^2
on 37 degrees diagonals. Thus, setting an acceleration of 3000 mm/s^2 in
the slicer will make the toolhead accelerate at 3000 mm/s^2 on these 37
and 143 degrees diagonals, but only 12000 * 3000 / 15000 = 2400 mm/s^2
for moves aligned with the X axis and 18000 mm/s^2 for pure Y moves.


### 混合CoreXY运动学

查看 [example-hybrid-corexy.cfg](../config/example-hybrid-corexy.cfg)
获取混合 CoreXY 运动学配置文件的示例。

此运动学也称为 Markforged 运动学。

此处仅描述混合 CoreXY 打印机特定的参数——有关可用参数，请参见[通用运动学设置](#common-kinematic-settings)。

```
[printer]
kinematics: hybrid_corexy
invert_kinematics: False
# ⚠️ Some hybrid_corexy machines with dual carriages may need to
#   invert the kinematics if the toolheads move in reverse
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. The default is to use max_velocity for max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. The default is to use max_accel for max_z_accel.

# The stepper_x section is used to describe the X axis as well as the
# stepper controlling the X-Y movement.
[stepper_x]

# Additional steppers may be added to the X rail as [stepper_x1],
# [stepper_x2], etc. Each additional X stepper is driven with the
# mirrored belt direction. Combined with additional Y steppers
# ([stepper_y1]) this supports four motor hybrid machines such as the
# RatRig V-Core hybrid.

# The stepper_y section is used to describe the stepper controlling
# the Y axis.
[stepper_y]

# The stepper_z section is used to describe the stepper controlling
# the Z axis.
[stepper_z]
```

### 混合CoreXZ运动学

查看 [example-hybrid-corexz.cfg](../config/example-hybrid-corexz.cfg)
获取混合 CoreXZ 运动学配置文件的示例。

此运动学也称为 Markforged 运动学。

此处仅描述混合 CoreXZ 打印机特定的参数——有关可用参数，请参见[通用运动学设置](#common-kinematic-settings)。

```
[printer]
kinematics: hybrid_corexz
invert_kinematics: False
# ⚠️ Some hybrid_corexy machines with dual carriages may need to
#   invert the kinematics if the toolheads move in reverse
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. The default is to use max_velocity for max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. The default is to use max_accel for max_z_accel.

# The stepper_x section is used to describe the X axis as well as the
# stepper controlling the X-Z movement.
[stepper_x]

# Additional steppers may be added to the X rail as [stepper_x1],
# [stepper_x2], etc. Each additional X stepper is driven with the
# mirrored belt direction.

# The stepper_y section is used to describe the stepper controlling
# the Y axis.
[stepper_y]

# The stepper_z section is used to describe the stepper controlling
# the Z axis.
[stepper_z]
```

### 极坐标运动学

查看 [example-polar.cfg](../config/example-polar.cfg) 获取极坐标运动学配置文件的示例。

此处仅描述极坐标打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

极坐标运动学正在开发中。已知在 0, 0 位置周围的运动不能正常工作。

```
[printer]
kinematics: polar
max_z_velocity:
#   This sets the maximum velocity (in mm/s) of movement along the z
#   axis. This setting can be used to restrict the maximum speed of
#   the z stepper motor. The default is to use max_velocity for
#   max_z_velocity.
max_z_accel:
#   This sets the maximum acceleration (in mm/s^2) of movement along
#   the z axis. It limits the acceleration of the z stepper motor. The
#   default is to use max_accel for max_z_accel.

# The stepper_bed section is used to describe the stepper controlling
# the bed.
[stepper_bed]
gear_ratio:
#   A gear_ratio must be specified and rotation_distance may not be
#   specified. For example, if the bed has an 80 toothed pulley driven
#   by a stepper with a 16 toothed pulley then one would specify a
#   gear ratio of "80:16". This parameter must be provided.

# The stepper_arm section is used to describe the stepper controlling
# the carriage on the arm.
[stepper_arm]

# The stepper_z section is used to describe the stepper controlling
# the Z axis.
[stepper_z]
```

### 旋转Delta运动学

查看 [example-rotary-delta.cfg](../config/example-rotary-delta.cfg) 获取旋转 delta 运动学配置文件的示例。

此处仅描述旋转delta打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

旋转 Delta 运动学正在开发中。归位运动可能会超时，某些边界检查尚未实现。

```
[printer]
kinematics: rotary_delta
max_z_velocity:
#   For delta printers this limits the maximum velocity (in mm/s) of
#   moves with z axis movement. This setting can be used to reduce the
#   maximum speed of up/down moves (which require a higher step rate
#   than other moves on a delta printer). The default is to use
#   max_velocity for max_z_velocity.
#minimum_z_position: 0
#   The minimum Z position that the user may command the head to move
#   to.  The default is 0.
shoulder_radius:
#   Radius (in mm) of the horizontal circle formed by the three
#   shoulder joints, minus the radius of the circle formed by the
#   effector joints. This parameter may also be calculated as:
#     shoulder_radius = (delta_f - delta_e) / sqrt(12)
#   This parameter must be provided.
shoulder_height:
#   Distance (in mm) of the shoulder joints from the bed, minus the
#   effector toolhead height. This parameter must be provided.

# The stepper_a section describes the stepper controlling the rear
# right arm (at 30 degrees). This section also controls the homing
# parameters (homing_speed, homing_retract_dist) for all arms.
[stepper_a]
gear_ratio:
#   A gear_ratio must be specified and rotation_distance may not be
#   specified. For example, if the arm has an 80 toothed pulley driven
#   by a pulley with 16 teeth, which is in turn connected to a 60
#   toothed pulley driven by a stepper with a 16 toothed pulley, then
#   one would specify a gear ratio of "80:16, 60:16". This parameter
#   must be provided.
position_endstop:
#   Distance (in mm) between the nozzle and the bed when the nozzle is
#   in the center of the build area and the endstop triggers. This
#   parameter must be provided for stepper_a; for stepper_b and
#   stepper_c this parameter defaults to the value specified for
#   stepper_a.
upper_arm_length:
#   Length (in mm) of the arm connecting the "shoulder joint" to the
#   "elbow joint". This parameter must be provided for stepper_a; for
#   stepper_b and stepper_c this parameter defaults to the value
#   specified for stepper_a.
lower_arm_length:
#   Length (in mm) of the arm connecting the "elbow joint" to the
#   "effector joint". This parameter must be provided for stepper_a;
#   for stepper_b and stepper_c this parameter defaults to the value
#   specified for stepper_a.
#angle:
#   This option specifies the angle (in degrees) that the arm is at.
#   The default is 30 for stepper_a, 150 for stepper_b, and 270 for
#   stepper_c.

# The stepper_b section describes the stepper controlling the rear
# left arm (at 150 degrees).
[stepper_b]

# The stepper_c section describes the stepper controlling the front
# arm (at 270 degrees).
[stepper_c]

# The delta_calibrate section enables a DELTA_CALIBRATE extended
# g-code command that can calibrate the shoulder endstop positions.
[delta_calibrate]
radius:
#   Radius (in mm) of the area that may be probed. This is the radius
#   of nozzle coordinates to be probed; if using an automatic probe
#   with an XY offset then choose a radius small enough so that the
#   probe always fits over the bed. This parameter must be provided.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
```

### 缆绳绞车运动学

查看 [example-winch.cfg](../config/example-winch.cfg) 获取缆绳绞车运动学配置文件的示例。

此处仅描述缆绳绞车打印机特定的参数——有关可用参数，请参见[通用运动学设置](#通用运动学设置)。

缆绳绞车支持为实验性功能。缆绳绞车运动学尚未实现归位功能。要归位打印机，请手动发送运动命令直到工具头位于 0, 0, 0，然后发出 `G28` 命令。

```
[printer]
kinematics: winch

# The stepper_a section describes the stepper connected to the first
# cable winch. A minimum of 3 and a maximum of 26 cable winches may be
# defined (stepper_a to stepper_z) though it is common to define 4.
[stepper_a]
rotation_distance:
#   The rotation_distance is the nominal distance (in mm) the toolhead
#   moves towards the cable winch for each full rotation of the
#   stepper motor. This parameter must be provided.
anchor_x:
anchor_y:
anchor_z:
#   The X, Y, and Z position of the cable winch in cartesian space.
#   These parameters must be provided.
```

### 无运动学

可以定义特殊的 "none" 运动学来禁用 Kalico 中的运动学支持。这对于控制非典型 3D 打印机的设备或用于调试目的可能很有用。

```
[printer]
kinematics: none
max_velocity: 1
max_accel: 1
#   The max_velocity and max_accel parameters must be defined. The
#   values are not used for "none" kinematics.
```

## CANopen伺服步进支持

### [canopen_bus]

多个 CANopen 步进电机共享的 CAN 总线参数。有关硬件要求和设置，请参见 [CANopen 指南](CANopen.md)。

```
[canopen_bus my_bus]
interface: socketcan
#   CAN interface type. Required. Typical values: "socketcan" (Linux),
#   "slcan" (serial-line CAN), "pcan" (PEAK).
channel: can0
#   CAN channel name. Required. For socketcan this is the network
#   interface name. For slcan this is the serial port.
#bitrate: 1000000
#   CAN bus bitrate in bps. Default is 1000000 (1 Mbit/s).
```

### [canopen_stepper]

CANopen CiA 402 伺服步进电机配置。这允许使用支持 CANopen 协议的工业伺服驱动器来替代传统的 step/dir 步进电机驱动器。

```
[canopen_stepper x]
#canopen_bus:
#   Reference to a [canopen_bus] section. If not specified, you must
#   provide can_interface, can_channel, and can_bitrate directly.
#can_interface:
#can_channel:
#can_bitrate: 1000000
#   Direct bus configuration (alternative to canopen_bus).
node_id:
#   CANopen node ID (1-127). Required.
eds_file:
#   Path to the EDS/DCF file for this device (CiA 306 INI format).
#   Required. Supports ~/ for home directory. Relative paths are
#   resolved from the config file directory.
#canopen_mode: CSP
#   Operating mode. Options: CSP (Cyclic Synchronous Position),
#   CSV (Cyclic Synchronous Velocity), PP (Profile Position),
#   PV (Profile Velocity), CST (Cyclic Synchronous Torque).
#   Default is CSP.
#sync_group: default
#   SYNC group name. Steppers with the same sync_group share the same
#   CANopen SYNC signal and are synchronized in their PDO exchange.
#   Default is "default".
#sync_period: 0.001
#   SYNC period in seconds (0.000250 to 0.010). This controls how
#   often position setpoints are sent to the drive. Default is 0.001
#   (1ms, 1kHz).
rotation_distance:
#   Distance (in mm) that the axis travels with one full rotation of
#   the servo motor. This parameter must be provided.
microsteps:
#   Set to 1 for CANopen servos (not used, but required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation or motor pole count. Default is 200.
#endstop_pin:
#   Endstop pin. Set to "canopen" to use CiA 402 internal homing, or
#   specify a GPIO pin for traditional endstop. Required for homing.
#canopen_homing_method: negative_limit
#   CiA 402 homing method (only used when endstop_pin is "canopen").
#   Options: current_position, positive_limit, negative_limit,
#   positive_home, negative_home, positive_home_index,
#   negative_home_index, negative_limit_index, positive_limit_index,
#   index_positive, index_negative. Can also be a number (1-35).
#   Default is "negative_limit".
#canopen_homing_speed_switch:
#   Speed for switch search in encoder counts/s. If not specified,
#   uses the drive's default.
#canopen_homing_speed_zero:
#   Speed for zero search in encoder counts/s. If not specified,
#   uses the drive's default.
#canopen_homing_accel:
#   Homing acceleration in encoder counts/s^2. If not specified,
#   uses the drive's default.
#canopen_homing_offset: 0
#   Home offset in encoder counts. Default is 0.
#alm_pin:
#   GPIO pin connected to servo drive ALM (alarm) output. When
#   configured, monitors this pin for alarm signals. Optional.
#alarm_action: shutdown
#   Action to take when ALM pin is triggered. Options: shutdown
#   (emergency stop), pause (pause print), gcode (execute alarm_gcode),
#   none (log only). Default is shutdown.
#alm_invert: false
#   Invert the ALM pin logic. Set to true for active-high alarm
#   outputs. Most servo drives use active-low (open-collector) alarm
#   outputs. Default is false.
```

有关 SYNC 组、归位方法和 EDS 文件格式的更多信息，请参见 [CANopen 指南](CANopen.md)。

## EtherCAT伺服步进支持

### [ethercat_stepper]

使用 CoE（CANopen over EtherCAT）和 CiA 402 驱动配置文件的 EtherCAT 伺服步进电机配置。需要安装 pysoem（`pip install pysoem`）。有关硬件设置和详细信息，请参见 [EtherCAT 指南](EtherCAT.md)。

```
[ethercat_stepper x]
ethercat_interface:
#   Network interface name. Linux: eth0, enp3s0, etc.
#   Windows: Npcap device name. Required.
ethercat_slave: 0
#   Slave position index (0 = first slave). Default is 0.
#canopen_mode: CSP
#   Operating mode. Options: CSP (Cyclic Synchronous Position),
#   PP (Profile Position), CSV (Cyclic Synchronous Velocity),
#   HOMING. Default is CSP.
#ethercat_cycle_time: 0.001
#   DC sync cycle time in seconds. Range: 0.000250 to 0.020.
#   Default is 0.001 (1ms).
rotation_distance:
#   Distance (mm) per full rotation. Required.
microsteps:
#   Set to 1 for EtherCAT servos (required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation. Default is 200.
#endstop_pin:
#   Endstop pin for traditional homing. Required for homing.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum position in mm. Default is 0.
#position_max:
#   Maximum position in mm. Required if endstop_pin is set.
#alm_pin:
#   GPIO pin connected to servo drive ALM (alarm) output. When
#   configured, monitors this pin for alarm signals. Optional.
#alarm_action: shutdown
#   Action to take when ALM pin is triggered. Options: shutdown
#   (emergency stop), pause (pause print), gcode (execute alarm_gcode),
#   none (log only). Default is shutdown.
#alm_invert: false
#   Invert the ALM pin logic. Set to true for active-high alarm
#   outputs. Most servo drives use active-low (open-collector) alarm
#   outputs. Default is false.
```

有关 CL3B 寄存器映射、DC 同步和故障排除，请参见 [EtherCAT 指南](EtherCAT.md)。

## RS485伺服步进支持

### [rs485_stepper]

RS485 伺服步进电机配置。支持通过 RS485 连接的工业伺服驱动器的 Modbus RTU 协议和自定义协议。有关硬件设置和协议详细信息，请参见 [RS485 指南](RS485.md)。

```
[rs485_stepper x]
#rs485_transport: host
#   传输层类型。"host" 通过 pyserial 使用 USB 转 RS485 适配器。
#   "mcu" 使用单个 MCU GPIO 引脚上的软件位翻转 Modbus UART（与 LYX
#   步进驱动相同的固件驱动）。默认 "host"。
serial_port:
#   串口路径。当 rs485_transport 为 "host" 时必填。示例：/dev/ttyUSB0、COM3。
#uart_pin:
#   单线 Modbus RTU 总线的 MCU GPIO 引脚。当 rs485_transport 为 "mcu"
#   时必填。固件需编译时启用 "Support software Modbus RTU UART
#   communication" 选项。
#baud_rate: 9600
#   波特率。范围：1200 至 115200。默认 9600。
#rs485_protocol: modbus_rtu
#   Protocol type. Options: modbus_rtu, uart_passthrough, custom.
#   Default is modbus_rtu.
#rs485_slave_id: 1
#   Modbus slave address (1-247). Default is 1.
#rs485_parity: N
#   Parity. Options: N (none), E (even), O (odd). Default is N.
#rs485_stopbits: 1
#   Stop bits. Options: 1, 1.5, 2. Default is 1.
#rs485_bytesize: 8
#   Data bits. Options: 5, 6, 7, 8. Default is 8.
#rs485_direction_pin: rts
#   DE/RE control method. "rts" uses RTS signal. "none" for
#   adapters with hardware auto-direction. Default is "rts".
#rs485_response_delay:
#   Delay after write before reading response (seconds).
#rs485_inter_frame_delay:
#   Minimum delay between frames (seconds).
#register_control_word:
#register_status_word:
#register_target_position:
#register_actual_position:
#register_error_code:
#   Custom register addresses for CiA 402 objects (modbus_rtu only).
#   If not specified, uses standard CiA 402 addresses.
#protocol_class:
#   Python class path for custom protocol. Required when
#   rs485_protocol is "custom". Format: module.ClassName
rotation_distance:
#   Distance (mm) per full rotation. Required.
microsteps:
#   Set to 1 for RS485 servos (required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation. Default is 200.
#endstop_pin:
#   Endstop pin for homing. Required for homing.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum position in mm. Default is 0.
#position_max:
#   Maximum position in mm. Required if endstop_pin is set.
#alm_pin:
#   GPIO pin connected to servo drive ALM (alarm) output. When
#   configured, monitors this pin for alarm signals. Optional.
#alarm_action: shutdown
#   Action to take when ALM pin is triggered. Options: shutdown
#   (emergency stop), pause (pause print), gcode (execute alarm_gcode),
#   none (log only). Default is shutdown.
#alm_invert: false
#   Invert the ALM pin logic. Set to true for active-high alarm
#   outputs. Most servo drives use active-low (open-collector) alarm
#   outputs. Default is false.
```

有关协议、自定义协议开发和故障排除的更多信息，请参见 [RS485 指南](RS485.md)。

## 伺服安全监控

### [servo_alarm]

独立的伺服报警引脚监控器。监控连接到伺服驱动器 ALM（报警）输出的 GPIO 引脚，并触发可配置的操作。

```
[servo_alarm my_servo]
alm_pin:
#   GPIO pin for alarm input. Required. Supports pin modifiers:
#   ^ (pull-up), ~ (pull-down), ! (invert).
#action: shutdown
#   Action to take when alarm is triggered. Options: shutdown
#   (emergency stop), pause (pause print), gcode (execute
#   alarm_gcode), none (log only). Default is shutdown.
#invert: false
#   Invert pin logic. Set to true for active-high alarm outputs.
#   Default is false.
#debounce: 0.01
#   Debounce time in seconds. Default is 0.01.
#gcode:
#   G-code to execute when action is "gcode". This is a Jinja2
#   template. Optional.
```

可以定义多个 [servo_alarm] 部分用于多轴监控。每个部分创建 QUERY_ALARM_<name> 和 CLEAR_ALARM_<name> G-code 命令。

### [servo_status]

伺服状态 G-code 命令模块。提供用于查询和管理所有已配置伺服步进电机的伺服驱动器状态的命令。

```
[servo_status]
#   No configuration options. This module is automatically loaded
#   when servo steppers are configured.
```

有关接线图、配置示例和故障排除，请参见 [伺服安全指南](servo-safety.md)。

## 外部脉冲发生器步进支持

### [pulse_gen_stepper]

外部脉冲发生器模块配置。向外部模块发送位置或速度命令，该模块在内部生成高速差分 step/dir 脉冲。有关详细信息，请参见 [PulseGen 指南](PulseGen.md)。

```
[pulse_gen_stepper x]
serial_port:
#   Serial port path. Required.
#baud_rate: 9600
#   Baud rate. Default is 9600.
#pulse_gen_protocol: modbus_rtu
#   Protocol type. Options: modbus_rtu, uart_passthrough, custom.
#   Default is modbus_rtu.
#pulse_gen_slave_id: 1
#   Slave address (1-247). Default is 1.
#pulse_gen_mode: absolute
#   Command mode. Options: absolute (absolute position),
#   relative (relative displacement), velocity. Default is absolute.
#register_target_position: 0x607A
#   Register for target position (absolute mode). Default 0x607A.
#register_actual_position: 0x6064
#   Register for actual position feedback. Set to 0 for open-loop.
#   Default 0x6064.
#register_relative_position: 0x0020
#   Register for relative displacement (relative mode). Default 0x0020.
#register_velocity: 0x0030
#   Register for velocity command (velocity mode). Default 0x0030.
#rs485_parity: N
#   Parity. Options: N, E, O. Default is N.
#rs485_stopbits: 1
#   Stop bits. Default is 1.
#rs485_bytesize: 8
#   Data bits. Default is 8.
#rs485_direction_pin: rts
#   DE/RE control. Default is "rts".
#protocol_class:
#   Custom protocol class path (when pulse_gen_protocol is "custom").
rotation_distance:
#   Distance (mm) per full rotation. Required.
microsteps:
#   Set to 1 for pulse generators (required by framework).
#full_steps_per_rotation: 200
#   Encoder counts per rotation. Default is 200.
#endstop_pin:
#   Endstop pin for homing. Required for homing.
#homing_speed: 5.0
#   Homing speed in mm/s. Default is 5.0.
#position_min: 0
#   Minimum position in mm. Default is 0.
#position_max:
#   Maximum position in mm. Required if endstop_pin is set.
```

有关命令模式、开环与闭环操作以及自定义协议的更多信息，请参见 [PulseGen 指南](PulseGen.md)。

## 通用挤出机和热床支持

### [extruder]

extruder 部分用于描述喷嘴热端的加热器参数以及控制挤出机的步进电机。有关更多信息，请参见[命令参考](G-Codes.md#extruder)。有关调节压力推进的信息，请参见[压力推进指南](Pressure_Advance.md)。有关控制方法的更详细信息，请参见 [PID](PID.md) 或 [MPC](MPC.md)。

```
[extruder]
step_pin:
dir_pin:
enable_pin:
microsteps:
rotation_distance:
#full_steps_per_rotation:
#gear_ratio:
#   See the "stepper" section for a description of the above
#   parameters. If none of the above parameters are specified then no
#   stepper will be associated with the nozzle hotend (though a
#   SYNC_EXTRUDER_MOTION command may associate one at run-time).
nozzle_diameter:
#   Diameter of the nozzle orifice (in mm). This parameter must be
#   provided.
filament_diameter:
#   The nominal diameter of the raw filament (in mm) as it enters the
#   extruder. This parameter must be provided.
#no_heater: false
#   If set to true, the extruder will be configured as a cold extruder
#   without a heater. This is useful for materials that don't require
#   heating (clay, concrete, food paste, etc.). When enabled, no
#   heater_pin is required and the extruder can extrude at any
#   temperature. See [Cold Extruder](Cold_Extruder.md) for details.
#max_extrude_cross_section:
#   Maximum area (in mm^2) of an extrusion cross section (eg,
#   extrusion width multiplied by layer height). This setting prevents
#   excessive amounts of extrusion during relatively small XY moves.
#   If a move requests an extrusion rate that would exceed this value
#   it will cause an error to be returned. The default is: 4.0 *
#   nozzle_diameter^2
#instantaneous_corner_velocity: 1.000
#   The maximum instantaneous velocity change (in mm/s) of the
#   extruder during the junction of two moves. The default is 1mm/s.
#max_extrude_only_distance: 50.0
#   Maximum length (in mm of raw filament) that a retraction or
#   extrude-only move may have. If a retraction or extrude-only move
#   requests a distance greater than this value it will cause an error
#   to be returned. The default is 50mm.
#max_extrude_only_velocity:
#max_extrude_only_accel:
#   Maximum velocity (in mm/s) and acceleration (in mm/s^2) of the
#   extruder motor for retractions and extrude-only moves. These
#   settings do not have any impact on normal printing moves. If not
#   specified then they are calculated to match the limit an XY
#   printing move with a cross section of 4.0*nozzle_diameter^2 would
#   have.
#pressure_advance: 0.0
#   The amount of raw filament to push into the extruder during
#   extruder acceleration. An equal amount of filament is retracted
#   during deceleration. It is measured in millimeters per
#   millimeter/second. The default is 0, which disables pressure
#   advance.
#pressure_advance_smooth_time: 0.040
#   A time range (in seconds) to use when calculating the average
#   extruder velocity for pressure advance. A larger value results in
#   smoother extruder movements. This parameter may not exceed 200ms.
#   This setting only applies if pressure_advance is non-zero. The
#   default is 0.040 (40 milliseconds).
#
# The remaining variables describe the extruder heater.
heater_pin:
#   PWM output pin controlling the heater. This parameter must be
#   provided.
#max_power: 1.0
#   The maximum power (expressed as a value from 0.0 to 1.0) that the
#   heater_pin may be set to. The value 1.0 allows the pin to be set
#   fully enabled for extended periods, while a value of 0.5 would
#   allow the pin to be enabled for no more than half the time. This
#   setting may be used to limit the total power output (over extended
#   periods) to the heater. The default is 1.0.
sensor_type:
#   Type of sensor - common thermistors are "EPCOS 100K B57560G104F",
#   "ATC Semitec 104GT-2", "ATC Semitec 104NT-4-R025H42G", "Generic
#   3950","Honeywell 100K 135-104LAG-J01", "NTC 100K MGB18-104F39050L32",
#   "SliceEngineering 450", and "TDK NTCG104LH104JT1". See the
#   "Temperature sensors" section for other sensors. This parameter
#   must be provided.
sensor_pin:
#   Analog input pin connected to the sensor. This parameter must be
#   provided.
#pullup_resistor: 4700
#   The resistance (in ohms) of the pullup attached to the thermistor.
#   This parameter is only valid when the sensor is a thermistor. The
#   default is 4700 ohms.
#smooth_time: 1.0
#   A time value (in seconds) over which temperature measurements will
#   be smoothed to reduce the impact of measurement noise. The default
#   is 1 seconds.
control:
#   Control algorithm (either pid, pid_v, dual_loop_pid, watermark or mpc).
#   This parameter must be provided. pid_v should only be used on well
#   calibrated heaters with low to moderate noise.
#
#   If control: pid, pid_v or dual_loop_pid
#pid_Kp:
#pid_Ki:
#pid_Kd:
#   The proportional (pid_Kp), integral (pid_Ki), and derivative
#   (pid_Kd) settings for the PID feedback control system. Kalico
#   evaluates the PID settings with the following general formula:
#     heater_pwm = (Kp*error + Ki*integral(error) - Kd*derivative(error)) / 255
#   Where "error" is "requested_temperature - measured_temperature"
#   and "heater_pwm" is the requested heating rate with 0.0 being full
#   off and 1.0 being full on. Consider using the PID_CALIBRATE
#   command to obtain these parameters. The pid_Kp, pid_Ki, and pid_Kd
#   parameters must be provided for PID heaters.
#
#   If control: watermark
#max_delta: 2.0
#   On 'watermark' controlled heaters this is the number of degrees in
#   Celsius above the target temperature before disabling the heater
#   as well as the number of degrees below the target before
#   re-enabling the heater. The default is 2 degrees Celsius.
#
#   If control: mpc
#   See MPC.md for details about these parameters.
#heater_power:
#cooling_fan:
#ambient_temp_sensor:
#filament_diameter: 1.75
#filament_density: 1.2
#filament_heat_capacity: 1.8
#
#pwm_cycle_time: 0.100
#   Time in seconds for each software PWM cycle of the heater. It is
#   not recommended to set this unless there is an electrical
#   requirement to switch the heater faster than 10 times a second.
#   The default is 0.100 seconds.
#lost_update_tolerance: 2
#   Maximum number of consecutive sensor lost samples that can be
#   recovered from.
#min_extrude_temp: 170
#   The minimum temperature (in Celsius) at which extruder move
#   commands may be issued. The default is 170 Celsius.
min_temp:
max_temp:
#   The maximum range of valid temperatures (in Celsius) that the
#   heater must remain within. This controls a safety feature
#   implemented in the micro-controller code - should the measured
#   temperature ever fall outside this range then the micro-controller
#   will go into a shutdown state. This check can help detect some
#   heater and sensor hardware failures. Set this range just wide
#   enough so that reasonable temperatures do not result in an error.
#   These parameters must be provided.
per_move_pressure_advance: False
#   If true, uses pressure advance constant from trapq when processing moves
#   This causes changes to pressure advance be taken into account immediately,
#   for all moves in the current queue, rather than ~250ms later once the queue gets flushed
#
#   If: control: dual_loop_pid
#inner_sensor_name:
#   The temperature_sensor name of a second sensor used by
#   'dual_loop_pid' for the inner PID loop.
#
#   If: control: dual_loop_pid
#inner_target_temp:
#   The target temperature for the inner PID loop. During calibration,
#   the temperature will oscillate above and below this value. This
#   behavior is expected and does not indicate a safety failure.
#inner_max_temp:
#   Deprecated alias for inner_target_temp.
#
#   If control: dual_loop_pid
#inner_pid_Kp:
#inner_pid_Ki:
#inner_pid_Kd:
#   'dual_loop_pid' control uses two PID loops to control the temperature.
#   The inner(secondary) PID loop controls the temperature directly. The
#   primary PID loop controls the power to the secondary PID loop. This
#   allows the primary PID loop to be tuned for temperature control,
#   while the secondary PID loop can be tuned for power control while
#   tracking 'inner_target_temp'.
#   The primary sensor is positioned close where the temperature
#   measurament should be more accurate (e.g. on the bed surface). The
#   secondary sensor is positioned where the temperature measurament
#   should not exceed a limit (e.g. on the silicone heater).
```

### [heater_bed]

heater_bed 部分描述加热床。它使用与 extruder 部分中描述的相同的加热器设置。

```
[heater_bed]
heater_pin:
sensor_type:
sensor_pin:
control:
min_temp:
max_temp:
#   See the "extruder" section for a description of the above parameters.
```

### [pid_profile]

PID 配置文件指定一组可以在运行时加载的 PID 值。

```
[pid_profile <heater> <profile-name>]
pid_version: 1
# This defines the version it was saved with and is important for compatibility
# checks, leave it at 1!
pid_target:
# For reference only, specifies the temperature the profile was calibrated for.
# If you create a custom profile, either enter the temperature that profile is
# intended to be used at or leave it blank.
pid_tolerance:
# The tolerance that was used when autocalibrating the profile. If you define
# a custom profile, leave it empty.
control: <pid|pid_v>
# Has to be either pid or pid_v.
# This parameter is required.
pid_kp:
# The P value for the PID Control.
# This parameter is required.
pid_ki:
# The I value for the PID Control.
# This parameter is required.
pid_kd:
# The D value for the PID Control.
# This parameter is required.
```
更多信息，请阅读 docs/PID.md

## 调平支持

### [bed_mesh]

网格床调平。可以定义 bed_mesh 配置部分以启用基于探测点生成的网格来偏移 Z 轴的移动变换。当使用探针归位 Z 轴时，建议在 printer.cfg 中定义 safe_z_home 部分，以便向打印区域中心归位。

有关更多信息，请参见[网格床指南](Bed_Mesh.md)和[命令参考](G-Codes.md#bed_mesh)。

Visual Examples:

```
 rectangular bed, probe_count = 3, 3:
             x---x---x (max_point)
             |
             x---x---x
                     |
 (min_point) x---x---x

 round bed, round_probe_count = 5, bed_radius = r:
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
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#horizontal_z_clearance:
#   A relative height (in mm) that the toolhead will lift at each mesh
#   point before moving to the next one. If enabled, the `horizontal_move_z`
#   value is only used for the travel move to the first mesh point. The default
#   is None.
#mesh_radius:
#   Defines the radius of the mesh to probe for round beds. Note that
#   the radius is relative to the coordinate specified by the
#   mesh_origin option. This parameter must be provided for round beds
#   and omitted for rectangular beds.
#mesh_origin:
#   Defines the center X, Y coordinate of the mesh for round beds. This
#   coordinate is relative to the probe's location. It may be useful
#   to adjust the mesh_origin in an effort to maximize the size of the
#   mesh radius. Default is 0, 0. This parameter must be omitted for
#   rectangular beds.
#mesh_min:
#   Defines the minimum X, Y coordinate of the mesh for rectangular
#   beds. This coordinate is relative to the probe's location. This
#   will be the first point probed, nearest to the origin. This
#   parameter must be provided for rectangular beds.
#mesh_max:
#   Defines the maximum X, Y coordinate of the mesh for rectangular
#   beds. Adheres to the same principle as mesh_min, however this will
#   be the furthest point probed from the bed's origin. This parameter
#   must be provided for rectangular beds.
#probe_count: 3, 3
#   For rectangular beds, this is a comma separate pair of integer
#   values X, Y defining the number of points to probe along each
#   axis. A single value is also valid, in which case that value will
#   be applied to both axes. Default is 3, 3.
#round_probe_count: 5
#   For round beds, this integer value defines the maximum number of
#   points to probe along each axis. This value must be an odd number.
#   Default is 5.
#fade_start: 1.0
#   The gcode z position in which to start phasing out z-adjustment
#   when fade is enabled. Default is 1.0.
#fade_end: 0.0
#   The gcode z position in which phasing out completes. When set to a
#   value below fade_start, fade is disabled. It should be noted that
#   fade may add unwanted scaling along the z-axis of a print. If a
#   user wishes to enable fade, a value of 10.0 is recommended.
#   Default is 0.0, which disables fade.
#fade_target:
#   The z position in which fade should converge. When this value is
#   set to a non-zero value it must be within the range of z-values in
#   the mesh. Users that wish to converge to the z homing position
#   should set this to 0. Default is the average z value of the mesh.
#split_delta_z: .025
#   The amount of Z difference (in mm) along a move that will trigger
#   a split. Default is .025.
#move_check_distance: 5.0
#   The distance (in mm) along a move to check for split_delta_z.
#   This is also the minimum length that a move can be split. Default
#   is 5.0.
#mesh_pps: 2, 2
#   A comma separated pair of integers X, Y defining the number of
#   points per segment to interpolate in the mesh along each axis. A
#   "segment" can be defined as the space between each probed point.
#   The user may enter a single value which will be applied to both
#   axes. Default is 2, 2.
#algorithm: lagrange
#   The interpolation algorithm to use. May be either "lagrange" or
#   "bicubic". This option will not affect 3x3 grids, which are forced
#   to use lagrange sampling. Default is lagrange.
#bicubic_tension: .2
#   When using the bicubic algorithm the tension parameter above may
#   be applied to change the amount of slope interpolated. Larger
#   numbers will increase the amount of slope, which results in more
#   curvature in the mesh. Default is .2.
#zero_reference_position:
#   An optional X,Y coordinate that specifies the location on the bed
#   where Z = 0.  When this option is specified the mesh will be offset
#   so that zero Z adjustment occurs at this location.  The default is
#   no zero reference.
#faulty_region_1_min:
#faulty_region_1_max:
#   Optional points that define a faulty region.  See docs/Bed_Mesh.md
#   for details on faulty regions.  Up to 99 faulty regions may be added.
#   By default no faulty regions are set.
#adaptive_margin:
#   An optional margin (in mm) to be added around the bed area used by
#   the defined print objects when generating an adaptive mesh.
#bed_mesh_default:
#   Optionally provide the name of a profile you would like loaded on init.
#   By default, no profile is loaded.
#use_probe_xy_offsets: True
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is True.
```

### [bed_tilt]

床倾斜补偿。可以定义 bed_tilt 配置部分以启用考虑倾斜床的移动变换。请注意，bed_mesh 和 bed_tilt 不兼容；不能同时定义两者。

有关更多信息，请参见[命令参考](G-Codes.md#bed_tilt)。

```
[bed_tilt]
#x_adjust: 0
#   The amount to add to each move's Z height for each mm on the X
#   axis. The default is 0.
#y_adjust: 0
#   The amount to add to each move's Z height for each mm on the Y
#   axis. The default is 0.
#z_adjust: 0
#   The amount to add to the Z height when the nozzle is nominally at
#   0, 0. The default is 0.
# The remaining parameters control a BED_TILT_CALIBRATE extended
# g-code command that may be used to calibrate appropriate x and y
# adjustment parameters.
#points:
#   A list of X, Y coordinates (one per line; subsequent lines
#   indented) that should be probed during a BED_TILT_CALIBRATE
#   command. Specify coordinates of the nozzle and be sure the probe
#   is above the bed at the given nozzle coordinates. The default is
#   to not enable the command.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#use_probe_xy_offsets: False
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is False.
```

### [bed_screws]

帮助调整调平螺钉的工具。可以定义 [bed_screws] 配置部分以启用 BED_SCREWS_ADJUST G-code 命令。

有关更多信息，请参见[调平指南](Manual_Level.md#adjusting-bed-leveling-screws)和[命令参考](G-Codes.md#bed_screws)。

```
[bed_screws]
#screw1:
#   The X, Y coordinate of the first bed leveling screw. This is a
#   position to command the nozzle to that is directly above the bed
#   screw (or as close as possible while still being above the bed).
#   This parameter must be provided.
#screw1_name:
#   An arbitrary name for the given screw. This name is displayed when
#   the helper script runs. The default is to use a name based upon
#   the screw XY location.
#screw1_fine_adjust:
#   An X, Y coordinate to command the nozzle to so that one can fine
#   tune the bed leveling screw. The default is to not perform fine
#   adjustments on the bed screw.
#screw2:
#screw2_name:
#screw2_fine_adjust:
#...
#   Additional bed leveling screws. At least three screws must be
#   defined.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   when moving from one screw location to the next. The default is 5.
#probe_height: 0
#   The height of the probe (in mm) after adjusting for the thermal
#   expansion of bed and nozzle. The default is zero.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#probe_speed: 5
#   The speed (in mm/s) when moving from a horizontal_move_z position
#   to a probe_height position. The default is 5.
```

### [screws_tilt_adjust]

帮助使用 Z 探针调整螺钉倾斜的工具。可以定义 screws_tilt_adjust 配置部分以启用 SCREWS_TILT_CALCULATE G-code 命令。

有关更多信息，请参见[调平指南](Manual_Level.md#adjusting-bed-leveling-screws-using-the-bed-probe)和[命令参考](G-Codes.md#screws_tilt_adjust)。

```
[screws_tilt_adjust]
#screw1:
#   The (X, Y) coordinate of the first bed leveling screw. This is a
#   position to command the nozzle to so that the probe is directly
#   above the bed screw (or as close as possible while still being
#   above the bed). This is the base screw used in calculations. This
#   parameter must be provided.
#screw1_name:
#   An arbitrary name for the given screw. This name is displayed when
#   the helper script runs. The default is to use a name based upon
#   the screw XY location.
#screw2:
#screw2_name:
#...
#   Additional bed leveling screws. At least two screws must be
#   defined.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#screw_thread: CW-M3
#   The type of screw used for bed leveling, M3, M4, or M5, and the
#   rotation direction of the knob that is used to level the bed.
#   Accepted values: CW-M3, CCW-M3, CW-M4, CCW-M4, CW-M5, CCW-M5, CW-M8, CCW-M8.
#   Default value is CW-M3 which most printers use. A clockwise
#   rotation of the knob decreases the gap between the nozzle and the
#   bed. Conversely, a counter-clockwise rotation increases the gap.
#use_probe_xy_offsets: False
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is False.
```

### [z_tilt]

多 Z 步进电机倾斜调整。此功能允许独立调整多个 Z 步进电机（参见 "stepper_z1" 部分）以调整倾斜。如果存在此部分，则可以使用 Z_TILT_ADJUST 扩展 [G-Code 命令](G-Codes.md#z_tilt)。

```
[z_tilt]
#z_positions:
#   A list of X, Y coordinates (one per line; subsequent lines
#   indented) describing the location of each bed "pivot point". The
#   "pivot point" is the point where the bed attaches to the given Z
#   stepper. It is described using nozzle coordinates (the X, Y position
#   of the nozzle if it could move directly above the point). The
#   first entry corresponds to stepper_z, the second to stepper_z1,
#   the third to stepper_z2, etc. This parameter must be provided.
#points:
#   A list of X, Y coordinates (one per line; subsequent lines
#   indented) that should be probed during a Z_TILT_ADJUST command.
#   Specify coordinates of the nozzle and be sure the probe is above
#   the bed at the given nozzle coordinates. This parameter must be
#   provided.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#min_horizontal_move_z: 1.0
#   The minimum value for horizontal move z to be used when
#   adaptive_horizontal_move_z is enabled.
#   The default is 1mm
#adaptive_horizontal_move_z: False
#   Set it to True to automatically adjust horizontal move z after the first
#   adjustment round, based on error.
#   When enabled, the initial horizontal_move_z is the config value,
#   and subsequent iterations will set horizontal_move_z to
#   the ceil of error, or min_horizontal_move_z - whichever is greater.
#   The default is False.
#retries: 0
#   Number of times to retry if the probed points aren't within
#   tolerance.
#retry_tolerance: 0
#   If retries are enabled then retry if largest and smallest probed
#   points differ more than retry_tolerance. Note the smallest unit of
#   change here would be a single step. However if you are probing
#   more points than steppers then you will likely have a fixed
#   minimum value for the range of probed points which you can learn
#   by observing command output.
#increasing_threshold: 0.0000001
#   Sets the threshold that probe points can increase before z_tilt aborts.
#   To disable the validation, set this parameter to a high value.
#use_probe_xy_offsets: False
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is False.
#enforce_lift_speed: False
#   By default, the first Z movement to reach `horizontal_move_z` uses `speed`.
#   Set `enforce_lift_speed` to True to enforce the `lift_speed`.
#   The default is False.
#use_adjustments: False
#   If set to true it uses the behaviour described by trails here:
#   https://github.com/Trails5000/klipper/commit/47b5a91f96761961e693031fa514a0025a877117
#alternate_probe_direction: False
#   If True, alternate the physical probing direction between full
#   probing passes/retries. The first pass uses the configured point
#   order, and the next pass probes the same points in reverse order.
#   The measured results are still returned in the configured logical
#   point order, so the z_tilt calculations are unchanged. This can
#   reduce repeated twisting of Bowden tubes, filament paths, umbilicals,
#   and cable bundles on large-format machines. It also avoids the extra
#   travel move from the last point back to the first point between retry
#   passes. The default is False.
#start_reverse: False
#   If True and alternate_probe_direction is enabled, start the first
#   probing pass in reverse order. Subsequent retry passes will continue
#   alternating direction. The default is False.
```

#### [z_tilt_ng]

z_tilt 的下一代版本，增加了 Z_TILT_CALIBRATE 和 Z_TILT_AUTODETECT 扩展 [G-Code 命令](G-Codes.md#z_tilt_ng)。Z_TILT_CALIBRATE 执行多次探测运行以计算 z_offset，从而使用更少的探测点实现精确的倾斜调整。Z_TILT_AUTODETECT 通过迭代探测自动确定每个 Z 步进电机的枢轴位置。当存在此部分时，这些扩展命令将可用，增强床调平精度和校准效率。

```
[z_tilt_ng]
#z_positions:
# See [z_tilt]. This parameter must be provided,
#   unless the parameter "extra_points" is provided. In that case only
#   the command Z_TILT_AUTODETECT can be run to automatically determine
#   the z_positions. See 'extra_points' below.
#z_offsets:
#   A list of Z offsets for each z_position. The z_offset is added to each
#   probed value during Z_TILT_ADJUST to offset for unevenness of the bed.
#   This values can also be automatically detected by running
#   Z_TILT_CALIBRATE. See "extra_points" below.
#points:
# See [z_tilt]
#speed: 50
# See [z_tilt]
#horizontal_move_z: 5
# See [z_tilt]
#min_horizontal_move_z: 1.0
# See [z_tilt]
#adaptive_horizontal_move_z: False
# See [z_tilt]
#retries: 0
# See [z_tilt]
#retry_tolerance: 0
# See [z_tilt]
#increasing_threshold: 0.0000001
# See [z_tilt]
#use_probe_xy_offsets: False
# See [z_tilt]
#enforce_lift_speed: False
# See [z_tilt]
#extra_points:
#   A list in the same format as "points" above. This list contains
#   additional points to be probed during the two calibration commands
#   Z_TILT_CALIBRATE and Z_TILT_AUTODETECT. If the bed is not perfectly
#   level, it is possible to specify more probing points with "points".
#   In that Z_TILT_ADJUST will determine the best fit via a least squares
#   algorithm. As this comes with additional overhead on each Z_TILT_ADJUST
#   run, it is instead possible to move the additional probing points here,
#   and use Z_TILT_CALIBRATE to find z_offsets to use for the probing points
#   used in Z_TILT_ADJUST.
#   The extra points are also used during T_ZILT_AUTODETECT. This command
#   can determine the z_positions automatically by during several probings
#   with intentionally tilted bed. It is currently only implemented for 3
#   z steppers.
#   Note that for both commands to work numpy has to be installed.
#averaging_len: 3
#   Z_TILT_CALIBRATE and Z_TILT_AUTODETECT both run repeatedly until the
#   result can no longer be improved. To determine this, the probed values
#   are averaged. The number of runs to average over is configured with this
#   parameter.
#autodetect_delta: 1.0
#   The amount by which Z_TILT_AUTODETECT intentionally tilts the bed. Higher
#   values yield better results, but can also lead to situations where the
#   bed is tilted in a way that the nozzle touched the bed before the probe.
#   The default is conservative.
#use_adjustments: False
#   If set to true it uses the behaviour described by trails here:
#   https://github.com/Trails5000/klipper/commit/47b5a91f96761961e693031fa514a0025a877117
```

### [quad_gantry_level]

使用 4 个独立控制的 Z 电机进行移动龙门调平。校正移动龙门上的双曲抛物面效应（薯片效应），龙门越灵活效果越明显。
警告：在移动床上使用此功能可能会导致不良结果。
如果存在此部分，则可以使用 QUAD_GANTRY_LEVEL 扩展 G-Code 命令。此例程假设以下 Z 电机配置：

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

Where x is the 0, 0 point on the bed

```
[quad_gantry_level]
#gantry_corners:
#   A newline separated list of X, Y coordinates describing the two
#   opposing corners of the gantry. The first entry corresponds to Z,
#   the second to Z2. This parameter must be provided.
#points:
#   A newline separated list of four X, Y points that should be probed
#   during a QUAD_GANTRY_LEVEL command. Order of the locations is
#   important, and should correspond to Z, Z1, Z2, and Z3 location in
#   order. This parameter must be provided. For maximum accuracy,
#   ensure your probe offsets are configured.
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
#min_horizontal_move_z: 1.0
#   The minimum value for horizontal move z to be used when
#   adaptive_horizontal_move_z is enabled.
#   The default is 1mm
#adaptive_horizontal_move_z: False
#   Set it to True to automatically adjust horizontal move z after the first
#   adjustment round, based on error.
#   When enabled, the initial horizontal_move_z is the config value,
#   and subsequent iterations will set horizontal_move_z to
#   the ceil of error, or min_horizontal_move_z - whichever is greater.
#   The default is False.
#max_adjust: 4
#   Safety limit if an adjustment greater than this value is requested
#   quad_gantry_level will abort.
#retries: 0
#   Number of times to retry if the probed points aren't within
#   tolerance.
#retry_tolerance: 0
#   If retries are enabled then retry if largest and smallest probed
#   points differ more than retry_tolerance.
#increasing_threshold: 0.0000001
#   Sets the threshold that probe points can increase before qgl aborts.
#   To disable the validation, set this parameter to a high value.
#use_probe_xy_offsets: False
#   If True, apply the `[probe]` XY offsets to the probed positions. The
#   default is False.
#enforce_lift_speed: False
#   By default, the first Z movement to reach `horizontal_move_z` uses `speed`.
#   Set `enforce_lift_speed` to True to enforce the `lift_speed`.
#   The default is False.
#alternate_probe_direction: False
#   If True, alternate the physical probing direction between full
#   probing passes/retries. The first pass uses the configured point
#   order, and the next pass probes the same points in reverse order.
#   The measured results are still returned in the configured logical
#   point order, so the quad gantry leveling calculations are unchanged.
#   This can reduce repeated twisting of Bowden tubes, filament paths,
#   umbilicals, and cable bundles on large-format machines. It also
#   avoids the extra travel move from the last point back to the first
#   point between retry passes. The default is False.
#start_reverse: False
#   If True and alternate_probe_direction is enabled, start the first
#   probing pass in reverse order. Subsequent retry passes will continue
#   alternating direction. The default is False.
```

### [skew_correction]

打印机偏斜校正。可以使用软件在 3 个平面上校正打印机偏斜：xy、xz、yz。这是通过沿平面打印校准模型并测量三个长度来完成的。由于偏斜校正的特性，这些长度通过 gcode 设置。有关详细信息，请参见[偏斜校正](Skew_Correction.md)和[命令参考](G-Codes.md#skew_correction)。

```
[skew_correction]
```

### [z_thermal_adjust]

温度相关的工具头 Z 位置调整。使用温度传感器（通常耦合到机架的垂直部分）实时补偿由打印机框架热膨胀引起的垂直工具头移动。可以定义多个部分为 [z_thermal_adjust component] 以补偿不同打印机部件的热膨胀，例如热端、热断和框架。

另请参见：[扩展 G-Code 命令](G-Codes.md#z_thermal_adjust)。

```
[z_thermal_adjust]
#temp_coeff:
#   The temperature coefficient of expansion, in mm/degC. For example, a
#   temp_coeff of 0.01 mm/degC will move the Z axis downwards by 0.01 mm for
#   every degree Celsius that the temperature sensor increases. Defaults to
#   0.0 mm/degC, which applies no adjustment.
#smooth_time:
#   Smoothing window applied to the temperature sensor, in seconds. Can reduce
#   motor noise from excessive small corrections in response to sensor noise.
#   The default is 2.0 seconds.
#z_adjust_off_above:
#   Disables adjustments above this Z height [mm]. The last computed correction
#   will remain applied until the toolhead moves below the specified Z height
#   again. The default is 99999999.0 mm (always on).
#max_z_adjustment:
#   Maximum absolute adjustment that can be applied to the Z axis [mm]. The
#   default is 99999999.0 mm (unlimited).
#sensor_type:
#sensor_pin:
#min_temp:
#max_temp:
#   Temperature sensor configuration.
#   See the "extruder" section for the definition of the above
#   parameters.
#gcode_id:
#   See the "heater_generic" section for the definition of this
#   parameter.
```

## 自定义归位

### [safe_z_home]

安全 Z 归位。可以使用此机制在特定的 X, Y 坐标处归位 Z 轴。如果工具头，例如，必须在 Z 归位之前移动到床中心，这将很有用。

```
[safe_z_home]
home_xy_position:
#   A X, Y coordinate (e.g. 100, 100) where the Z homing should be
#   performed. This parameter must be provided.
#speed: 50.0
#   Speed at which the toolhead is moved to the safe Z home
#   coordinate. The default is 50 mm/s
#z_hop:
#   Distance (in mm) to lift the Z axis prior to homing. This is
#   applied to any homing command, even if it doesn't home the Z axis.
#   If the Z axis is already homed and the current Z position is less
#   than z_hop, then this will lift the head to a height of z_hop. If
#   the Z axis is not already homed the head is lifted by z_hop.
#   The default is to not implement Z hop.
#z_hop_speed: 15.0
#   Speed (in mm/s) at which the Z axis is lifted prior to homing. The
#   default is 15 mm/s.
#move_to_previous: False
#   When set to True, the X and Y axes are reset to their previous
#   positions after Z axis homing. The default is False.
#home_y_before_x: False
#  # If True, the Y axis will home first. The default is False.
```

### [homing_override]

归位覆盖。可以使用此机制在正常 G-Code 输入中找到 G28 时运行一系列 G-Code 命令。这在需要特定程序来归位打印机的打印机上可能很有用。

```
[homing_override]
gcode:
#   A list of G-Code commands to execute in place of G28 commands
#   found in the normal g-code input. See docs/Command_Templates.md
#   for G-Code format. If a G28 is contained in this list of commands
#   then it will invoke the normal homing procedure for the printer.
#   The commands listed here must home all axes. This parameter must
#   be provided.
#axes: xyz
#   The axes to override. For example, if this is set to "z" then the
#   override script will only be run when the z axis is homed (eg, via
#   a "G28" or "G28 Z0" command). Note, the override script should
#   still home all axes. The default is "xyz" which causes the
#   override script to be run in place of all G28 commands.
#set_position_x:
#set_position_y:
#set_position_z:
#   If specified, the printer will assume the axis is at the specified
#   position prior to running the above g-code commands. Setting this
#   disables homing checks for that axis. This may be useful if the
#   head must move prior to invoking the normal G28 mechanism for an
#   axis. The default is to not force a position for an axis.
```

### [endstop_phase]

步进电机相位调整的限位开关。要使用此功能，请定义一个以 "endstop_phase" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[endstop_phase stepper_z]"）。此功能可以提高限位开关的准确性。添加裸的 "[endstop_phase]" 声明以启用 ENDSTOP_PHASE_CALIBRATE 命令。

有关更多信息，请参见[限位相位指南](Endstop_Phase.md)和[命令参考](G-Codes.md#endstop_phase)。

```
[endstop_phase stepper_z]
#endstop_accuracy:
#   Sets the expected accuracy (in mm) of the endstop. This represents
#   the maximum error distance the endstop may trigger (eg, if an
#   endstop may occasionally trigger 100um early or up to 100um late
#   then set this to 0.200 for 200um). The default is
#   4*rotation_distance/full_steps_per_rotation.
#trigger_phase:
#   This specifies the phase of the stepper motor driver to expect
#   when hitting the endstop. It is composed of two numbers separated
#   by a forward slash character - the phase and the total number of
#   phases (eg, "7/64"). Only set this value if one is sure the
#   stepper motor driver is reset every time the mcu is reset. If this
#   is not set, then the stepper phase will be detected on the first
#   home and that phase will be used on all subsequent homes.
#endstop_align_zero: False
#   If true then the position_endstop of the axis will effectively be
#   modified so that the zero position for the axis occurs at a full
#   step on the stepper motor. (If used on the Z axis and the print
#   layer height is a multiple of a full step distance then every
#   layer will occur on a full step.) The default is False.
```

## G-Code宏和事件

### [gcode_macro]

G-Code 宏（可以定义任意数量的以 "gcode_macro" 为前缀的部分）。有关更多信息，请参见[命令模板指南](Command_Templates.md)。

```
[gcode_macro my_cmd]
#gcode:
#   A list of G-Code commands to execute in place of "my_cmd". See
#   docs/Command_Templates.md for G-Code format. This parameter must
#   be provided.
#variable_<name>:
#   One may specify any number of options with a "variable_" prefix.
#   The given variable name will be assigned the given value (parsed
#   as a Python literal) and will be available during macro expansion.
#   For example, a config with "variable_fan_speed = 75" might have
#   gcode commands containing "M106 S{ fan_speed * 255 }". Variables
#   can be changed at run-time using the SET_GCODE_VARIABLE command
#   (see docs/Command_Templates.md for details). Variable names may
#   not use upper case characters.
#rename_existing:
#   This option will cause the macro to override an existing G-Code
#   command and provide the previous definition of the command via the
#   name provided here. This can be used to override builtin G-Code
#   commands. Care should be taken when overriding commands as it can
#   cause complex and unexpected results. The default is to not
#   override an existing G-Code command.
#description: G-Code macro
#   This will add a short description used at the HELP command or while
#   using the auto completion feature. Default "G-Code macro"
```

### [delayed_gcode]

在设定延迟后执行 gcode。有关更多信息，请参见[命令模板指南](Command_Templates.md#delayed-gcodes)和[命令参考](G-Codes.md#delayed_gcode)。

```
[delayed_gcode my_delayed_gcode]
gcode:
#   A list of G-Code commands to execute when the delay duration has
#   elapsed. G-Code templates are supported. This parameter must be
#   provided.
#initial_duration: 0.0
#   The duration of the initial delay (in seconds). If set to a
#   non-zero value the delayed_gcode will execute the specified number
#   of seconds after the printer enters the "ready" state. This can be
#   useful for initialization procedures or a repeating delayed_gcode.
#   If set to 0 the delayed_gcode will not execute on startup.
#   Default is 0.
#description: Update the duration of a delayed_gcode
#   This will add a short description used at the HELP command or while
#   using the auto completion feature. Default "Update the duration of 
#   a delayed_gcode"
```

### [save_variables]

支持将变量保存到磁盘，以便在重启后保留它们。有关更多信息，请参见[命令模板](Command_Templates.md#save-variables-to-disk)和 [G-Code 参考](G-Codes.md#save_variables)。

```
[save_variables]
filename:
#   Required - provide a filename that would be used to save the
#   variables to disk e.g. ~/variables.cfg
```

### [idle_timeout]

Idle timeout. An idle timeout is automatically enabled - add an
explicit idle_timeout config section to change the default settings.

```
[idle_timeout]
#gcode:
#   A list of G-Code commands to execute on an idle timeout. See
#   docs/Command_Templates.md for G-Code format. The default is to run
#   "TURN_OFF_HEATERS" and "M84".
#timeout: 600
#   Idle time (in seconds) to wait before running the above G-Code
#   commands. Set it to 0 to disable the timeout feature.
#   The default is 600 seconds.
```

## 可选G-Code功能

### [virtual_sdcard]

A virtual sdcard may be useful if the host machine is not fast enough
to run OctoPrint well. It allows the Kalico host software to directly
print gcode files stored in a directory on the host using standard
sdcard G-Code commands (eg, M24).

```
[virtual_sdcard]
path:
#   The path of the local directory on the host machine to look for
#   g-code files. This is a read-only directory (sdcard file writes
#   are not supported). One may point this to OctoPrint's upload
#   directory (generally ~/.octoprint/uploads/ ). This parameter must
#   be provided.
#on_error_gcode:
#   A list of G-Code commands to execute when an error is reported.
#   See docs/Command_Templates.md for G-Code format. The default is to
#   run TURN_OFF_HEATERS.
#with_subdirs: False
#   Enable scanning of subdirectories for the menu and for the
#   M20 and M23 commands. The default is False.
```

### [sdcard_loop]

Some printers with stage-clearing features, such as a part ejector or
a belt printer, can find use in looping sections of the sdcard file.
(For example, to print the same part over and over, or repeat the
a section of a part for a chain or other repeated pattern).

See the [command reference](G-Codes.md#sdcard_loop) for supported
commands. See the [sample-macros.cfg](../config/sample-macros.cfg)
file for a Marlin compatible M808 G-Code macro.

```
[sdcard_loop]
```

### ⚠️ [force_move]

This module is enabled by default in Kalico!

Support manually moving stepper motors for diagnostic purposes. Note,
using this feature may place the printer in an invalid state - see the
[command reference](G-Codes.md#force_move) for important details.

```
[force_move]
#enable_force_move: True
#   Set to `True` to enable FORCE_MOVE and SET_KINEMATIC_POSITION
#   extended G-Code commands. The default is `True`.
```

### [pause_resume]

Pause/Resume functionality with support of position capture and
restore. See the [command reference](G-Codes.md#pause_resume) for more
information.

```
[pause_resume]
#recover_velocity: 50.
#   When capture/restore is enabled, the speed at which to return to
#   the captured position (in mm/s). Default is 50.0 mm/s.
```

### [firmware_retraction]

Firmware filament retraction. This enables G10 (retract) and G11
(unretract) GCODE commands issued by many slicers. The parameters
below provide startup defaults, although the values can be adjusted
via the SET_RETRACTION [command](G-Codes.md#firmware_retraction)),
allowing per-filament settings and runtime tuning.

```
[firmware_retraction]
#retract_length: 0.0
#   The length of filament (in mm) to retract when a G10 command is
#   executed. When a G11 command is executed, the unretract_length
#   is the sum of the retract_length and the unretract_extra_length
#   (see below). The minimum value and default are 0 mm, which
#   disables firmware retraction.
#retract_speed: 20.0
#   The speed of filament retraction moves (in mm/s).
#   This value is typically set relatively high (>40 mm/s),
#   except for soft and/oozy filaments like TPU and PETG
#   (20 to 30 mm/s). The minimum value is 1 mm/s, the default value
#   is 20 mm/s.
#unretract_extra_length: 0.0
#   The *additional* length (in mm) to add or the length to subtract
#   from the filament move when unretracting compared to the retract
#   move length. This allows priming the nozzle (positive extra length)
#   or delaying extrusion after unretracting (negative length). The
#   latter may help reduce blobbing. The minimum value is -1 mm
#   (2.41 mm3 volume for 1.75 mm filament), the default value is 0 mm.
#unretract_speed: 10.0
#   The speed of filament unretraction moves (in mm/s).
#   This parameter is not particularly critical, although often lower
#   than retract_speed. The minimum value is 1 mm/s, the default value
#   is 10 mm/s.
#z_hop_height: 0.0
#   The vertical height by which the nozzle is lifted from the print to
#   prevent collisions with the print during travel moves when retracted.
#   The minimum value is 0 mm, the default value is 0 mm, which disables
#   zhop moves. The value will be reduced if the zhop move reaches
#   maximum z.
#clear_zhop_on_z_moves: False
#   If True, when a change in Z is sent while toolhead is retracted,
#   z_hop is cancelled until next retraction. Otherwise,
#   `z_hop_height` is applied as an offset to all movements.
```

### [gcode_arcs]

Support for gcode arc (G2/G3) commands.

```
[gcode_arcs]
#resolution: 1.0
#   An arc will be split into segments. Each segment's length will
#   equal the resolution in mm set above. Lower values will produce a
#   finer arc, but also more work for your machine. Arcs smaller than
#   the configured value will become straight lines. The default is
#   1mm.
```

### [respond]

This module is enabled by default in Kalico!

Enable the "M118" and "RESPOND" extended
[commands](G-Codes.md#respond).

```
[respond]
#default_type: echo
#   Sets the default prefix of the "M118" and "RESPOND" output to one
#   of the following:
#       echo: "echo: " (This is the default)
#       command: "// "
#       error: "!! "
#default_prefix: echo:
#   Directly sets the default prefix. If present, this value will
#   override the "default_type".
#enable_respond: True
#   Set to `True` to enable M118 and RESPOND
#   extended G-Code commands. The default is `True`.
```

### [exclude_object]

This module is enabled by default in Kalico!

Enables support to exclude or cancel individual objects during the printing
process.

See the [exclude objects guide](Exclude_Object.md) and
[command reference](G-Codes.md#exclude_object)
for additional information. See the
[sample-macros.cfg](../config/sample-macros.cfg) file for a
Marlin/RepRapFirmware compatible M486 G-Code macro.

```
[exclude_object]
#enable_exclude_object: True
#   Set to `True` to enable `EXCLUDE_OBJECT_*` extended G-Code commands.
#   The default is `True`.
```

## 共振补偿

### [input_shaper]

Enables [resonance compensation](Resonance_Compensation.md). Also see
the [command reference](G-Codes.md#input_shaper).

```
[input_shaper]
#shaper_freq_x: 0
#   A frequency (in Hz) of the input shaper for X axis. This is
#   usually a resonance frequency of X axis that the input shaper
#   should suppress. For more complex shapers, like 2- and 3-hump EI
#   input shapers, this parameter can be set from different
#   considerations. The default value is 0, which disables input
#   shaping for X axis.
#shaper_freq_y: 0
#   A frequency (in Hz) of the input shaper for Y axis. This is
#   usually a resonance frequency of Y axis that the input shaper
#   should suppress. For more complex shapers, like 2- and 3-hump EI
#   input shapers, this parameter can be set from different
#   considerations. The default value is 0, which disables input
#   shaping for Y axis.
#shaper_type: mzv
#   A type of the input shaper to use for both X and Y axes. Supported
#   shapers are zv, mzv, zvd, ei, 2hump_ei, and 3hump_ei. The default
#   is mzv input shaper.
#shaper_type_x:
#shaper_type_y:
#   If shaper_type is not set, these two parameters can be used to
#   configure different input shapers for X and Y axes. The same
#   values are supported as for shaper_type parameter.
#damping_ratio_x: 0.1
#damping_ratio_y: 0.1
#   Damping ratios of vibrations of X and Y axes used by input shapers
#   to improve vibration suppression. Default value is 0.1 which is a
#   good all-round value for most printers. In most circumstances this
#   parameter requires no tuning and should not be changed.
```

### [adxl345]

ADXL345 加速度计支持。此支持允许从传感器查询加速度计测量值。这将启用 ACCELEROMETER_MEASURE 命令（有关更多信息，请参见 [G-Codes](G-Codes.md#adxl345)）。默认芯片名称为 "default"，但您可以指定一个显式名称（例如，[adxl345 my_chip_name]）。

```
[adxl345]
cs_pin:
#   The SPI enable pin for the sensor. This parameter must be provided.
#spi_speed: 5000000
#   The SPI speed (in hz) to use when communicating with the chip.
#   The default is 5000000.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#axes_map: x, y, z
#   The accelerometer axis for each of the printer's X, Y, and Z axes.
#   This may be useful if the accelerometer is mounted in an
#   orientation that does not match the printer orientation. For
#   example, one could set this to "y, x, z" to swap the X and Y axes.
#   It is also possible to negate an axis if the accelerometer
#   direction is reversed (eg, "x, z, -y"). The default is "x, y, z".
#rate: 3200
#   Output data rate for ADXL345. ADXL345 supports the following data
#   rates: 3200, 1600, 800, 400, 200, 100, 50, and 25. Note that it is
#   not recommended to change this rate from the default 3200, and
#   rates below 800 will considerably affect the quality of resonance
#   measurements.
```

### [icm20948]

icm20948 加速度计支持。

```
[icm20948]
#i2c_address:
#   Default is 104 (0x68). If AD0 is high, it would be 0x69 instead.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   See the "common I2C settings" section for a description of the
#   above parameters. The default "i2c_speed" is 400000.
#axes_map: x, y, z
#   See the "adxl345" section for information on this parameter.
```

### [lis2dw]

LIS2DW 加速度计支持。

```
[lis2dw]
#cs_pin:
#   The SPI enable pin for the sensor. This parameter must be provided
#   if using SPI.
#spi_speed: 5000000
#   The SPI speed (in hz) to use when communicating with the chip.
#   The default is 5000000.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#i2c_address:
#   Default is 25 (0x19). If SA0 is high, it would be 24 (0x18) instead.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   See the "common I2C settings" section for a description of the
#   above parameters. The default "i2c_speed" is 400000.
#axes_map: x, y, z
#   See the "adxl345" section for information on this parameter.
```

### [lis3dh]

LIS3DH 加速度计支持。

```
[lis3dh]
#cs_pin:
#   The SPI enable pin for the sensor. This parameter must be provided
#   if using SPI.
#spi_speed: 5000000
#   The SPI speed (in hz) to use when communicating with the chip.
#   The default is 5000000.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#i2c_address:
#   Default is 25 (0x19). If SA0 is high, it would be 24 (0x18) instead.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   See the "common I2C settings" section for a description of the
#   above parameters. The default "i2c_speed" is 400000.
#axes_map: x, y, z
#   See the "adxl345" section for information on this parameter.
```

### [mpu9250]

MPU-9250, MPU-9255, MPU-6515, MPU-6050 和 MPU-6500 加速度计支持（可以定义任意数量的 "mpu9250" 前缀部分）。

```
[mpu9250 my_accelerometer]
#i2c_address:
#   Default is 104 (0x68). If AD0 is high, it would be 0x69 instead.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed: 400000
#   See the "common I2C settings" section for a description of the
#   above parameters. The default "i2c_speed" is 400000.
#axes_map: x, y, z
#   See the "adxl345" section for information on this parameter.
```

### [resonance_tester]

共振测试和自动输入整形器校准支持。要使用此模块的大部分功能，必须安装其他软件依赖项；有关更多信息，请参见[测量共振](Measuring_Resonances.md)和[命令参考](G-Codes.md#resonance_tester)。有关 `max_smoothing` 参数及其用法的更多信息，请参见测量共振指南的 [Max smoothing](Measuring_Resonances.md#max-smoothing) 部分。

```
[resonance_tester]
#probe_points:
#   A list of X, Y, Z coordinates of points (one point per line) to test
#   resonances at. At least one point is required. Make sure that all
#   points with some safety margin in XY plane (~a few centimeters)
#   are reachable by the toolhead.
#accel_chips:
#   A comma-separated list of accelerometer chips to use for measurements.
#   For example, "accel_chips: adxl345 head, adxl345 bed" would use two
#   separate accelerometer chips. This parameter has priority over the
#   other accelerometer parameters if specified.
#accel_chip:
#   A name of the accelerometer chip to use for measurements. If
#   adxl345 chip was defined without an explicit name, this parameter
#   can simply reference it as "accel_chip: adxl345", otherwise an
#   explicit name must be supplied as well, e.g. "accel_chip: adxl345
#   my_chip_name". Either this, 'accel_chips', or the next two parameters
#   must be set.
#accel_chip_x:
#accel_chip_y:
#   Names of the accelerometer chips to use for measurements for each
#   of the axis. Can be useful, for instance, on bed slinger printer,
#   if two separate accelerometers are mounted on the bed (for Y axis)
#   and on the toolhead (for X axis). These parameters have the same
#   format as 'accel_chip' parameter. Only one of 'accel_chips', 'accel_chip',
#   or these two parameters must be provided.
#max_smoothing:
#   Maximum input shaper smoothing to allow for each axis during shaper
#   auto-calibration (with 'SHAPER_CALIBRATE' command). By default no
#   maximum smoothing is specified. Refer to Measuring_Resonances guide
#   for more details on using this feature.
#move_speed: 50
#   The speed (in mm/s) to move the toolhead to and between test points
#   during the calibration. The default is 50.
#min_freq: 5
#   Minimum frequency to test for resonances. The default is 5 Hz.
#max_freq: 133.33
#   Maximum frequency to test for resonances. The default is 133.33 Hz.
#accel_per_hz: 75
#   This parameter is used to determine which acceleration to use to
#   test a specific frequency: accel = accel_per_hz * freq. Higher the
#   value, the higher is the energy of the oscillations. Can be set to
#   a lower than the default value if the resonances get too strong on
#   the printer. However, lower values make measurements of
#   high-frequency resonances less precise. The default value is 75
#   (mm/sec).
#   Set it to 60 as a good baseline when using the sweeping resonance tester.
#hz_per_sec: 1
#   Determines the speed of the test. When testing all frequencies in
#   range [min_freq, max_freq], each second the frequency increases by
#   hz_per_sec. Small values make the test slow, and the large values
#   will decrease the precision of the test. The default value is 1.0
#   (Hz/sec == sec^-2).
#sweeping_accel: 400
#   An acceleration of slow sweeping moves. The default is 400 mm/sec^2.
#sweeping_period: 0
#   A period of slow sweeping moves. Avoid setting it to a too small
#   non-zero value in order to not poison the measurements.
#   To enable it, start by setting it to 1.2 sec which is a good all-round
#   choice. Set it to 0 do disable it. The default is 0.
```

## 配置文件辅助工具

### [board_pins]

引脚别名（可以定义任意数量的 "board_pins" 前缀部分）。用于定义微控制器上引脚的别名。

```
[board_pins my_aliases]
mcu: mcu
#   A comma separated list of micro-controllers that may use the
#   aliases. The default is to apply the aliases to the main "mcu".
aliases:
aliases_<name>:
#   A comma separated list of "name=value" aliases to create for the
#   given micro-controller. For example, "EXP1_1=PE6" would create an
#   "EXP1_1" alias for the "PE6" pin. However, if "value" is enclosed
#   in "<>" then "name" is created as a reserved pin (for example,
#   "EXP1_9=<GND>" would reserve "EXP1_9"). Any number of options
#   starting with "aliases_" may be specified.
```

### [include]

包含文件支持。可以从主打印机配置文件中包含其他配置文件。也可以使用通配符（例如 "configs/\*.cfg"，或者如果使用 python 版本 >=3.5 则为 "configs/\*\*/\*.cfg"）。

```
[include my_other_config.cfg]
```

### [duplicate_pin_override]

此工具允许在配置文件中多次定义单个微控制器引脚，而无需正常的错误检查。这用于诊断和调试目的。当 Kalico 支持多次使用同一引脚时，不需要此部分，并且使用此覆盖可能会导致令人困惑和意外的结果。您可以指定一个显式名称（例如 [duplicate_pin_override my_name]）来定义多个实例。

```
[duplicate_pin_override]
pins:
#   A comma separated list of pins that may be used multiple times in
#   a config file without normal error checks. This parameter must be
#   provided.
```

## 床探测硬件

### [probe]

Z 高度探针。可以定义此部分以启用 Z 高度探测硬件。启用此部分后，PROBE 和 QUERY_PROBE 扩展 [g-code 命令](G-Codes.md#probe) 变得可用。另请参见 [探针校准指南](Probe_Calibrate.md)。probe 部分还会创建一个虚拟 "probe:z_virtual_endstop" 引脚。您可以在使用探针代替 z 限位开关的笛卡尔式打印机上将 stepper_z 的 endstop_pin 设置为此虚拟引脚。如果使用 "probe:z_virtual_endstop"，则不要在 stepper_z 配置部分中定义 position_endstop。

```
[probe]
pin:
#   Probe detection pin. If the pin is on a different microcontroller
#   than the Z steppers then it enables "multi-mcu homing". This
#   parameter must be provided.
#deactivate_on_each_sample: True
#   This determines if Kalico should execute deactivation gcode
#   between each probe attempt when performing a multiple probe
#   sequence. The default is True.
#x_offset: 0.0
#   The distance (in mm) between the probe and the nozzle along the
#   x-axis. The default is 0.
#y_offset: 0.0
#   The distance (in mm) between the probe and the nozzle along the
#   y-axis. The default is 0.
z_offset:
#   The distance (in mm) between the bed and the nozzle when the probe
#   triggers. This parameter must be provided.
#speed: 5.0
#   Speed (in mm/s) of the Z axis when probing. The default is 5mm/s.
#samples: 1
#   The number of times to probe each point. The probed z-values will
#   be averaged. The default is to probe 1 time.
#sample_retract_dist: 2.0
#   The distance (in mm) to lift the toolhead between each sample (if
#   sampling more than once). The default is 2mm.
#lift_speed:
#   Speed (in mm/s) of the Z axis when lifting the probe between
#   samples. The default is to use the same value as the 'speed'
#   parameter.
#samples_result: average
#   The calculation method when sampling more than once - either
#   "median" or "average". The default is average.
#samples_tolerance: 0.100
#   The maximum Z distance (in mm) that a sample may differ from other
#   samples. If this tolerance is exceeded then either an error is
#   reported or the attempt is restarted (see
#   samples_tolerance_retries). The default is 0.100mm.
#samples_tolerance_retries: 0
#   The number of times to retry if a sample is found that exceeds
#   samples_tolerance. On a retry, all current samples are discarded
#   and the probe attempt is restarted. If a valid set of samples are
#   not obtained in the given number of retries then an error is
#   reported. The default is zero which causes an error to be reported
#   on the first sample that exceeds samples_tolerance.
#activate_gcode:
#   A list of G-Code commands to execute prior to each probe attempt.
#   See docs/Command_Templates.md for G-Code format. This may be
#   useful if the probe needs to be activated in some way. Do not
#   issue any commands here that move the toolhead (eg, G1). The
#   default is to not run any special G-Code commands on activation.
#deactivate_gcode:
#   A list of G-Code commands to execute after each probe attempt
#   completes. See docs/Command_Templates.md for G-Code format. Do not
#   issue any commands here that move the toolhead. The default is to
#   not run any special G-Code commands on deactivation.
#drop_first_result: False
#   Set to `True` will probe one extra time and remove the first
#   sample from calculation. This can improve probe accuracy for
#   printers that have an outlier first sample.
#⚠️ bad_probe_strategy: RETRY
#   Strategy to apply when a probe attempt is considered "bad" based on
#   the probe's quality detection logic. If the probe doesn't support 
#   quality detection all probes are assumed to be good.
#   One of: fail, ignore, retry or circle.
#   - fail: Stop immediately with an error on first bad probe.
#   - ignore: Accept all probes regardless of quality.
#   - retry: Re-attempt the probe at the same location.
#   - circle: Re-attempt the probe using a circular offset pattern to
#     avoid fouling.
#   The default is retry.
#⚠️ bad_probe_retries: 6
#   Number of additional probe attempts to make when a bad probe
#   is detected, according to 'bad_probe_strategy'. Set to 0 to disable
#   retries. The default is 6.
#⚠️ retry_speed:
#   Probe horizontal movement speed (in mm/s) to use when moving the probe
#   for a retry. If not specified, the default value is the value of 'speed'.
#⚠️ nozzle_scrubber_gcode:
#   A block of G-Code to perform a custom nozzle scrubbing routine. This
#   G-code may be invoked between PROBE retries and by the NOZZLE_CLEANUP
#   command. The gcode template receives the following parameters:
#   - ATTEMPT: The current retry attempt number
#   - RETRIES: The maximum number of retries configured
#   - X, Y: The current toolhead position
#⚠️ scrubbing_frequency: 0
#   Controls how often the nozzle scrubber is used in response to bad probes.
#   If set to a positive number, N, the nozzle_scrubber_gcode will be invoked
#   after every Nth bad probe. 1 will run the scrubber after every bad probe.
#   0 will disable scrubbing. The default is 0.
```

### [nozzle_cleanup]

启用 [NOZZLE_CLEANUP](G-Codes.md#nozzle_cleanup) gcode 命令。这将执行一个喷嘴清洁程序，通过在网格图案上探测来清除喷嘴上的渗出物。要正常工作，您的探针需要支持探测质量检测，例如 [load_cell_probe](#load_cell_probe)。
```
#samples: 3
#   Number of consecutive good probes required at one location to succeed.
#   Default is 3.
#stepover: 2.0
#   The spacing (in mm) between probe locations in the grid. Default is 2mm.
#pattern_x: 10
#   Number of probe locations along the X axis. Can be negative. Default is 10.
#pattern_y: 4
#   Number of probe locations along the Y axis. Can be negative. Default is 4.
#
#These config values are inherited from [probe] if not specified:
#speed:
#lift_speed:
#retry_speed:
#sample_retract_dist:
#nozzle_scrubber_gcode:
#scrubbing_frequency:
```


### [bltouch]

BLTouch 探针。可以定义此部分（而不是 probe 部分）以启用 BLTouch 探针。有关更多信息，请参见 [BL-Touch 指南](BLTouch.md) 和 [命令参考](G-Codes.md#bltouch)。还会创建一个虚拟 "probe:z_virtual_endstop" 引脚（有关详细信息，请参见 "probe" 部分）。

```
[bltouch]
sensor_pin:
#   Pin connected to the BLTouch sensor pin. Most BLTouch devices
#   require a pullup on the sensor pin (prefix the pin name with "^").
#   This parameter must be provided.
control_pin:
#   Pin connected to the BLTouch control pin. This parameter must be
#   provided.
#pin_move_time: 0.680
#   The amount of time (in seconds) to wait for the BLTouch pin to
#   move up or down. The default is 0.680 seconds.
#stow_on_each_sample: True
#   This determines if Kalico should command the pin to move up
#   between each probe attempt when performing a multiple probe
#   sequence. Read the directions in docs/BLTouch.md before setting
#   this to False. The default is True.
#probe_with_touch_mode: False
#   If this is set to True then Kalico will probe with the device in
#   "touch_mode". The default is False (probing in "pin_down" mode).
#pin_up_reports_not_triggered: True
#   Set if the BLTouch consistently reports the probe in a "not
#   triggered" state after a successful "pin_up" command. This should
#   be True for all genuine BLTouch devices. Read the directions in
#   docs/BLTouch.md before setting this to False. The default is True.
#pin_up_touch_mode_reports_triggered: True
#   Set if the BLTouch consistently reports a "triggered" state after
#   the commands "pin_up" followed by "touch_mode". This should be
#   True for all genuine BLTouch devices. Read the directions in
#   docs/BLTouch.md before setting this to False. The default is True.
#set_output_mode:
#   Request a specific sensor pin output mode on the BLTouch V3.0 (and
#   later). This setting should not be used on other types of probes.
#   Set to "5V" to request a sensor pin output of 5 Volts (only use if
#   the controller board needs 5V mode and is 5V tolerant on its input
#   signal line). Set to "OD" to request the sensor pin output use
#   open drain mode. The default is to not request an output mode.
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
#   See the "probe" section for information on these parameters.
```

### ⚠️ [dockable_probe]

某些探针与工具头磁性耦合，不使用时存放在停靠点。如果探针使用磁铁连接和停靠点进行存储，则应定义此部分而不是 probe 部分。有关配置和设置的更多详细信息，请参见 [可停靠探针指南](Dockable_Probe.md)。

```
[dockable_probe]
dock_position: 0,0,0
#   The physical position of the probe dock relative to the origin of
#   the bed. The coordinates are specified as a comma separated X, Y, Z
#   list of values. Certain dock designs are independent of the Z axis.
#   If Z is specified the toolhead will move to the Z location before the X, Y
#   coordinates.
#   This parameter is required.
approach_position: 0,0,0
#   The X, Y, Z position where the toolhead needs to be prior to moving into the
#   dock so that the probe is aligned properly for attaching or detaching.
#   If Z is specified the toolhead will move to the Z location before the X, Y
#   coordinates.
#   This parameter is required.
detach_position: 0,0,0
#   Similar to the approach_position, the detach_position is the coordinates
#   where the toolhead is moved after the probe has been docked.
#   For magnetically coupled probes, this is typically perpendicular to
#   the approach_position in a direction that does not cause the tool to
#   collide with the printer.
#   If Z is specified the toolhead will move to the Z location before the X, Y
#   coordinates.
#   This parameter is required.
#extract_position: 0,0,0
#   Similar to the approach_position, the extract_position is the coordinates
#   where the toolhead is moved to extract the probe from the dock.
#   If Z is specified the toolhead will move to the Z location before the X, Y
#   coordinates.
#   The default value is approach_probe value.
#insert_position: 0,0,0
#   Similar to the extract_position, the insert_position is the coordinates
#   where the toolhead is moved before inserting the probe into the dock.
#   If Z is specified the toolhead will move to the Z location before the X, Y
#   coordinates.
#   The default value is extract_probe value.
#safe_dock_distance :
#   This setting defines a security area around dock during ATTACH/DETACH_PROBE
#   commands. While inside the area, the toolhead move away prior to reach the
#   approach or insert position.
#   Default is the smallest distance to the dock of approach, detach, insert
#   position. It could be only lower than the Default value.
#safe_position : approach_position
#   A safe position to ensure MOVE_AVOIDING_DOCK travel does not move the
#   toolhead out of range.
#z_hop: 15.0
#   Distance (in mm) to lift the Z axis prior to attaching/detaching the probe.
#   If the Z axis is already homed and the current Z position is less
#   than `z_hop`, then this will lift the head to a height of `z_hop`. If
#   the Z axis is not already homed the head is lifted by `z_hop`.
#   The default is to not implement Z hop.
#restore_toolhead: True
#   While True, the position of the toolhead is restored to the position prior
#   to the attach/detach movements.
#   The default value is True.
#dock_retries:
#   The number of times to attempt to attach/dock the probe before raising
#   an error and aborting probing.
#   The default is 0.
#auto_attach_detach: False
#   Enable/Disable the automatic attaching/detaching of the probe during
#   actions that require the probe.
#   The default is True.
#attach_speed:
#detach_speed:
#travel_speed:
#   Optional speeds used during moves.
#   The default is to use `speed` of `probe` or 5.0.
#check_open_attach:
#   The probe status should be verified prior to homing. Setting this option
#   to true will check the probe "endstop" is "open" after attaching and
#   will abort probing if not, also checking for "triggered" after docking.
#   Conversively, setting this to false, the probe should read "triggered"
#   after attaching and "open" after docking. If not, probing will abort.
#probe_sense_pin:
#   This supplemental pin can be defined to determine an attached state
#   instead of check_open_attach.
#dock_sense_pin:
#   This supplemental pin can be defined to determine a docked state in
#   addition to probe_sense_pin or check_open_attach.
#pre_attach_gcode:
#   Code to run right before the probe gets attached
#post_attach_gcode:
#   Code to run right after the probe gets attached
#pre_detach_gcode:
#   Code to run right before the probe gets detached
#post_detach_gcode:
#   Code to run right after the probe gets detached
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
#   See the "probe" section for information on these parameters.
```

### [smart_effector]

Duet3d 的 "Smart Effector" 使用力传感器实现 Z 探针。可以定义此部分而不是 `[probe]` 以启用 Smart Effector 特定功能。这还将启用[运行时命令](G-Codes.md#smart_effector)以在运行时调整 Smart Effector 的参数。

```
[smart_effector]
pin:
#   Pin connected to the Smart Effector Z Probe output pin (pin 5). Note that
#   pullup resistor on the board is generally not required. However, if the
#   output pin is connected to the board pin with a pullup resistor, that
#   resistor must be high value (e.g. 10K Ohm or more). Some boards have a low
#   value pullup resistor on the Z probe input, which will likely result in an
#   always-triggered probe state. In this case, connect the Smart Effector to
#   a different pin on the board. This parameter is required.
#control_pin:
#   Pin connected to the Smart Effector control input pin (pin 7). If provided,
#   Smart Effector sensitivity programming commands become available.
#probe_accel:
#   If set, limits the acceleration of the probing moves (in mm/sec^2).
#   A sudden large acceleration at the beginning of the probing move may
#   cause spurious probe triggering, especially if the hotend is heavy.
#   To prevent that, it may be necessary to reduce the acceleration of
#   the probing moves via this parameter.
#recovery_time: 0.4
#   A delay between the travel moves and the probing moves in seconds. A fast
#   travel move prior to probing may result in a spurious probe triggering.
#   This may cause 'Probe triggered prior to movement' errors if no delay
#   is set. Value 0 disables the recovery delay.
#   Default value is 0.4.
#x_offset:
#y_offset:
#   Should be left unset (or set to 0).
z_offset:
#   Trigger height of the probe. Start with -0.1 (mm), and adjust later using
#   `PROBE_CALIBRATE` command. This parameter must be provided.
#speed:
#   Speed (in mm/s) of the Z axis when probing. It is recommended to start
#   with the probing speed of 20 mm/s and adjust it as necessary to improve
#   the accuracy and repeatability of the probe triggering.
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#activate_gcode:
#deactivate_gcode:
#deactivate_on_each_sample:
#   See the "probe" section for more information on the parameters above.
```

### [probe_eddy_current]

涡流感应探针支持。可以定义此部分（而不是 probe 部分）以启用此探针。有关更多信息，请参见[命令参考](G-Codes.md#probe_eddy_current)。

```
[probe_eddy_current my_eddy_probe]
sensor_type: ldc1612
#   The sensor chip used to perform eddy current measurements. This
#   parameter must be provided and must be set to ldc1612.
#frequency:
#   The external crystal frequency (in Hz) of the LDC1612 chip.
#   The default is 12000000.
#intb_pin:
#   MCU gpio pin connected to the ldc1612 sensor's INTB pin (if
#   available). The default is to not use the INTB pin.
#z_offset:
#   The nominal distance (in mm) between the nozzle and bed that a
#   probing attempt should stop at. This parameter must be provided.
#i2c_address:
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   The i2c settings for the sensor chip. See the "common I2C
#   settings" section for a description of the above parameters.
#x_offset:
#y_offset:
#speed:
#lift_speed:
#samples:
#sample_retract_dist:
#samples_result:
#samples_tolerance:
#samples_tolerance_retries:
#   See the "probe" section for information on these parameters.
```

### [axis_twist_compensation]

补偿由于 X 或 Y 龙门扭曲导致的不准确探针读数的工具。有关症状、配置和设置的更多详细信息，请参见 [轴扭曲补偿指南](Axis_Twist_Compensation.md)。

```
[axis_twist_compensation]
#speed: 50
#   The speed (in mm/s) of non-probing moves during the calibration.
#   The default is 50.
#horizontal_move_z: 5
#   The height (in mm) that the head should be commanded to move to
#   just prior to starting a probe operation. The default is 5.
calibrate_start_x: 20
#   Defines the minimum X coordinate of the calibration
#   This should be the X coordinate that positions the nozzle at the starting
#   calibration position.
calibrate_end_x: 200
#   Defines the maximum X coordinate of the calibration
#   This should be the X coordinate that positions the nozzle at the ending
#   calibration position.
calibrate_y: 112.5
#   Defines the Y coordinate of the calibration
#   This should be the Y coordinate that positions the nozzle during the
#   calibration process. This parameter is recommended to
#   be near the center of the bed

# For Y-axis twist compensation, specify the following parameters:
calibrate_start_y: ...
#   Defines the minimum Y coordinate of the calibration
#   This should be the Y coordinate that positions the nozzle at the starting
#   calibration position for the Y axis. This parameter must be provided if
#   compensating for Y axis twist.
calibrate_end_y: ...
#   Defines the maximum Y coordinate of the calibration
#   This should be the Y coordinate that positions the nozzle at the ending
#   calibration position for the Y axis. This parameter must be provided if
#   compensating for Y axis twist.
calibrate_x: ...
#   Defines the X coordinate of the calibration for Y axis twist compensation
#   This should be the X coordinate that positions the nozzle during the
#   calibration process for Y axis twist compensation. This parameter must be
#   provided and is recommended to be near the center of the bed.

# The following parameters are automatically saved by SAVE_CONFIG after
# running AXIS_TWIST_COMPENSATION_CALIBRATE and typically should not be
# manually modified. Note: if z_compensations is set, compensation_start_x
# and compensation_end_x must also be set. Similarly, zy_compensations
# requires compensation_start_y and compensation_end_y.
#z_compensations:
#   A comma-separated list of Z offset compensation values for X-axis twist.
#   These represent Z adjustments at evenly-spaced points from
#   compensation_start_x to compensation_end_x. Generated automatically
#   during X-axis calibration. Requires compensation_start_x and
#   compensation_end_x to be set. The default is an empty list.
#compensation_start_x:
#   The starting X coordinate for X-axis twist compensation.
#   Set automatically during calibration. The default is unset.
#compensation_end_x:
#   The ending X coordinate for X-axis twist compensation.
#   Set automatically during calibration. The default is unset.
#zy_compensations:
#   A comma-separated list of Z offset compensation values for Y-axis twist.
#   Similar to z_compensations but for the Y axis. Generated automatically
#   during Y-axis calibration (AXIS=Y). Requires compensation_start_y and
#   compensation_end_y to be set. The default is an empty list.
#compensation_start_y:
#   The starting Y coordinate for Y-axis twist compensation.
#   Set automatically during Y-axis calibration. The default is unset.
#compensation_end_y:
#   The ending Y coordinate for Y-axis twist compensation.
#   Set automatically during Y-axis calibration. The default is unset.
```

### ⚠️ [z_calibration]

自动 Z 偏移校准。如果打印机能够自动校准喷嘴偏移，则可以定义此部分。有关更多信息，请参见 [Z 校准指南](Z_Calibration.md)。

```
[z_calibration]
nozzle_xy_position:
#   A X, Y coordinate (e.g. 100,100) of the nozzle, clicking on the Z endstop.
switch_xy_position:
#   A X, Y coordinate (e.g. 100,100) of the probe's switch body, clicking on
#   the Z endstop.
bed_xy_position: default from relative_reference_index of bed_mesh
#   a X, Y coordinate (e.g. 100,100) where the print surface (e.g. the center
#   point) is probed. These coordinates will be adapted by the
#   probe's X and Y offsets. The default is the relative_reference_index
#   of the configured bed_mesh, if configured. It's possible to change the relative
#   reference index at runtime or use the GCode argument BED_POSITION of CALIBRATE_Z.
switch_offset:
#   The trigger point offset of the used mag-probe switch.
#   Larger values will position the nozzle closer to the bed.
#   This needs to be find out manually. More on this later
#   in this section..
max_deviation: 1.0
#   The maximum allowed deviation of the calculated offset.
#   If the offset exceeds this value, it will stop!
#   The default is 1.0 mm.
samples: default from "probe:samples" section
#   The number of times to probe each point. The probed z-values
#   will be averaged. The default is from the probe's configuration.
samples_tolerance: default from "probe:samples_tolerance" section
#   The maximum Z distance (in mm) that a sample may differ from other
#   samples. The default is from the probe's configuration.
samples_tolerance_retries: default from "probe:samples_tolerance_retries" section
#   The number of times to retry if a sample is found that exceeds
#   samples_tolerance. The default is from the probe's configuration.
samples_result: default from "probe:samples_result" section
#   The calculation method when sampling more than once - either
#   "median" or "average". The default is from the probe's configuration.
clearance: 2 * z_offset from the "probe:z_offset" section
#   The distance in mm to move up before moving to the next
#   position. The default is two times the z_offset from the probe's
#   configuration.
position_min: default from "stepper_z:position_min" section.
#   Minimum valid distance (in mm) used for probing move. The
#   default is from the Z rail configuration.
speed: 50
#   The moving speed in X and Y. The default is 50 mm/s.
lift_speed: default from "probe:lift_speed" section
#   Speed (in mm/s) of the Z axis when lifting the probe between
#   samples and clearance moves. The default is from the probe's
#   configuration.
probing_speed: default from "stepper_z:homing_speed" section.
#   The fast probing speed (in mm/s) used, when probing_first_fast
#   is activated. The default is from the Z rail configuration.
probing_second_speed: default from "stepper_z:second_homing_speed" section.
#   The slower speed (in mm/s) for probing the recorded samples.
#   The default is second_homing_speed of the Z rail configuration.
probing_retract_dist: default from "stepper_z:homing_retract_dist" section.
#   Distance to retract (in mm) before probing the next sample.
#   The default is homing_retract_dist from the Z rail configuration.
probing_first_fast: false
#   If true, the first probing is done faster by the probing speed.
#   This is to get faster down and the result is not recorded as a
#   probing sample. The default is false.
start_gcode:
#   A list of G-Code commands to execute prior to each calibration command.
#   See docs/Command_Templates.md for G-Code format. This can be used to
#   attach the probe.
before_switch_gcode:
#   A list of G-Code commands to execute prior to each probing on the
#   mag-probe. See docs/Command_Templates.md for G-Code format. This can be
#   used to attach the probe after probing on the nozzle and before probing
#   on the mag-probe.
end_gcode:
#   A list of G-Code commands to execute after each calibration command.
#   See docs/Command_Templates.md for G-Code format. This can be used to
#   detach the probe afterwards.
```

## 额外步进电机和挤出机

### [stepper_z1]

多步进轴。在笛卡尔式打印机上，控制给定轴的步进电机可以有额外的配置块，定义应与主步进电机同步移动的步进电机。您可以定义任意数量的以数字后缀开头的部分（从 1 开始，例如 "stepper_z1"、"stepper_z2" 等）。

```
[stepper_z1]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   See the "stepper" section for the definition of the above parameters.
#endstop_pin:
#   If an endstop_pin is defined for the additional stepper then the
#   stepper will home until the endstop is triggered. Otherwise, the
#   stepper will home until the endstop on the primary stepper for the
#   axis is triggered.
```

### [extruder1]

在多挤出机打印机上，为每个额外的挤出机添加一个额外的挤出机部分。额外的挤出机部分应命名为 "extruder1"、"extruder2"、"extruder3" 等。有关可用参数的描述，请参见 "extruder" 部分。

有关示例配置，请参见 [sample-multi-extruder.cfg](../config/sample-multi-extruder.cfg)。

```
[extruder1]
#step_pin:
#dir_pin:
#...
#   See the "extruder" section for available stepper and heater
#   parameters.
#shared_heater:
#   This option is deprecated and should no longer be specified.
```

### [dual_carriage]

支持具有单轴双滑车的笛卡尔和混合 corexy/z 打印机。可以通过 SET_DUAL_CARRIAGE 扩展 g-code 命令设置滑车模式。例如，"SET_DUAL_CARRIAGE CARRIAGE=1" 命令将激活在此部分中定义的滑车（CARRIAGE=0 将激活恢复为主滑车）。双滑车支持通常与额外挤出机结合使用 - SET_DUAL_CARRIAGE 命令通常与 ACTIVATE_EXTRUDER 命令同时调用。请确保在停用期间停放滑车。请注意，在 G28 归位期间，通常先归位主滑车，然后归位在 `[dual_carriage]` 配置部分中定义的滑车。但是，如果两个滑车都向正方向归位，且 `[dual_carriage]` 滑车的 `position_endstop` 大于主滑车，或者如果两个滑车都向负方向归位，且 `[dual_carriage]` 滑车的 `position_endstop` 小于主滑车，则将先归位 `[dual_carriage]` 滑车。

此外，您可以使用 "SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY" 或 "SET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR" 命令来激活双滑车的复制或镜像模式，在这种情况下，它将相应地跟随滑车 0 的运动。这些命令可用于同时打印两个零件 - 两个相同的零件（在 COPY 模式下）或镜像零件（在 MIRROR 模式下）。请注意，COPY 和 MIRROR 模式还需要双滑车上挤出机的适当配置，这通常可以通过 "SYNC_EXTRUDER_MOTION MOTION_QUEUE=extruder EXTRUDER=<dual_carriage_extruder>" 或类似命令来实现。

有关示例配置，请参见 [sample-idex.cfg](../config/sample-idex.cfg)。

```
[dual_carriage]
axis:
#   The axis this extra carriage is on (either x or y). This parameter
#   must be provided.
#safe_distance:
#   The minimum distance (in mm) to enforce between the dual and the primary
#   carriages. If a G-Code command is executed that will bring the carriages
#   closer than the specified limit, such a command will be rejected with an
#   error. If safe_distance is not provided, it will be inferred from
#   position_min and position_max for the dual and primary carriages. If set
#   to 0 (or safe_distance is unset and position_min and position_max are
#   identical for the primary and dual carraiges), the carriages proximity
#   checks will be disabled.
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#endstop_pin:
#position_endstop:
#position_min:
#position_max:
#   See the "stepper" section for the definition of the above parameters.
```

### [extruder_stepper]

支持与挤出机运动同步的额外步进电机（可以定义任意数量的 "extruder_stepper" 前缀部分）。

有关更多信息，请参见[命令参考](G-Codes.md#extruder)。

```
[extruder_stepper my_extra_stepper]
extruder:
#   The extruder this stepper is synchronized to. If this is set to an
#   empty string then the stepper will not be synchronized to an
#   extruder. This parameter must be provided.
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   See the "stepper" section for the definition of the above
#   parameters.
```

### [manual_stepper]

手动步进电机（可以定义任意数量的 "manual_stepper" 前缀部分）。这些是由 MANUAL_STEPPER g-code 命令控制的步进电机。例如："MANUAL_STEPPER STEPPER=my_stepper MOVE=10 SPEED=5"。有关 MANUAL_STEPPER 命令的描述，请参见 [G-Codes](G-Codes.md#manual_stepper) 文件。这些步进电机不连接到正常的打印机运动学。

```
[manual_stepper my_stepper]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   See the "stepper" section for a description of these parameters.
#velocity:
#   Set the default velocity (in mm/s) for the stepper. This value
#   will be used if a MANUAL_STEPPER command does not specify a SPEED
#   parameter. The default is 5mm/s.
#accel:
#   Set the default acceleration (in mm/s^2) for the stepper. An
#   acceleration of zero will result in no acceleration. This value
#   will be used if a MANUAL_STEPPER command does not specify an ACCEL
#   parameter. The default is zero.
#endstop_pin:
#   Endstop switch detection pin. If specified, then one may perform
#   "homing moves" by adding a STOP_ON_ENDSTOP parameter to
#   MANUAL_STEPPER movement commands.
#position_min:
#position_max:
#   The minimum and maximum position the stepper can be commanded to
#   move to. If specified then one may not command the stepper to move
#   past the given position. Note that these limits do not prevent
#   setting an arbitrary position with the `MANUAL_STEPPER
#   SET_POSITION=x` command. The default is to not enforce a limit.
```

### [mixing_extruder]

具有 <n> 入 1 出混合喷嘴的混合打印头。激活后，额外的 G-Code 命令可用。有关额外命令的详细描述，请参见 [G-Codes](G-Codes.md#mixing_extruder)。

```
[mixing_extruder]
#steppers:
#   Which steppers feed into the hotend/nozzle. provide a comma
#   separated list, eg. "extruder,extruder1,extruder2". Should be
#   the names of either extruder sections or extruder_stepper sections
#   This configuration is required.
#extruder_name:
#   The name of the extruder to synchronize the steppers in the steppers
#   list to.
#   The default is the first entry in the
#   "steppers" list.
```


## 自定义加热器和传感器

### [verify_heater]

加热器和温度传感器验证。加热器验证会自动为打印机上配置的每个加热器启用。使用 verify_heater 部分来更改默认设置。

```
[verify_heater heater_config_name]
#max_error: 120
#   The maximum "cumulative temperature error" before raising an
#   error. Smaller values result in stricter checking and larger
#   values allow for more time before an error is reported.
#   Specifically, the temperature is inspected once a second and if it
#   is close to the target temperature then an internal "error
#   counter" is reset; otherwise, if the temperature is below the
#   target range then the counter is increased by the amount the
#   reported temperature differs from that range. Should the counter
#   exceed this "max_error" then an error is raised. The default is
#   120.
#check_gain_time:
#   This controls heater verification during initial heating. Smaller
#   values result in stricter checking and larger values allow for
#   more time before an error is reported. Specifically, during
#   initial heating, as long as the heater increases in temperature
#   within this time frame (specified in seconds) then the internal
#   "error counter" is reset. The default is 20 seconds for extruders
#   and 60 seconds for heater_bed.
#hysteresis: 5
#   The maximum temperature difference (in Celsius) to a target
#   temperature that is considered in range of the target. This
#   controls the max_error range check. It is rare to customize this
#   value. The default is 5.
#heating_gain: 2
#   The minimum temperature (in Celsius) that the heater must increase
#   by during the check_gain_time check. It is rare to customize this
#   value. The default is 2.
```

### [homing_heaters]

Tool to disable heaters when homing or probing an axis.

```
[homing_heaters]
#steppers:
#   A comma separated list of steppers that should cause heaters to be
#   disabled. The default is to disable heaters for any homing/probing
#   move.
#   Typical example: stepper_z
#heaters:
#   A comma separated list of heaters to disable during homing/probing
#   moves. The default is to disable all heaters.
#   Typical example: extruder, heater_bed
```

### [thermistor]

Custom thermistors (one may define any number of sections with a
"thermistor" prefix). A custom thermistor may be used in the
sensor_type field of a heater config section. (For example, if one
defines a "[thermistor my_thermistor]" section then one may use a
"sensor_type: my_thermistor" when defining a heater.) Be sure to place
the thermistor section in the config file above its first use in a
heater section.

```
[thermistor my_thermistor]
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#temperature3:
#resistance3:
#   Three resistance measurements (in Ohms) at the given temperatures
#   (in Celsius). The three measurements will be used to calculate the
#   Steinhart-Hart coefficients for the thermistor. These parameters
#   must be provided when using Steinhart-Hart to define the
#   thermistor.
#beta:
#   Alternatively, one may define temperature1, resistance1, and beta
#   to define the thermistor parameters. This parameter must be
#   provided when using "beta" to define the thermistor.
```

### [adc_temperature]

Custom ADC temperature sensors (one may define any number of sections
with an "adc_temperature" prefix). This allows one to define a custom
temperature sensor that measures a voltage on an Analog to Digital
Converter (ADC) pin and uses linear interpolation between a set of
configured temperature/voltage (or temperature/resistance)
measurements to determine the temperature. The resulting sensor can be
used as a sensor_type in a heater section. (For example, if one
defines a "[adc_temperature my_sensor]" section then one may use a
"sensor_type: my_sensor" when defining a heater.) Be sure to place the
sensor section in the config file above its first use in a heater
section.

```
[adc_temperature my_sensor]
#temperature1:
#voltage1:
#temperature2:
#voltage2:
#...
#   A set of temperatures (in Celsius) and voltages (in Volts) to use
#   as reference when converting a temperature. A heater section using
#   this sensor may also specify adc_voltage and voltage_offset
#   parameters to define the ADC voltage (see "Common temperature
#   amplifiers" section for details). At least two measurements must
#   be provided.
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#...
#   Alternatively one may specify a set of temperatures (in Celsius)
#   and resistance (in Ohms) to use as reference when converting a
#   temperature. A heater section using this sensor may also specify a
#   pullup_resistor parameter (see "extruder" section for details). At
#   least two measurements must be provided.
```

### [heater_generic]

通用加热器（可以定义任意数量的 "heater_generic" 前缀部分）。这些加热器的行为类似于标准加热器（挤出机、加热床）。使用 SET_HEATER_TEMPERATURE 命令设置目标温度（有关详细信息，请参见 [G-Codes](G-Codes.md#heaters)）。

```
[heater_generic my_generic_heater]
#gcode_id:
#   The id to use when reporting the temperature in the M105 command.
#   This parameter must be provided.
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
#   See the "extruder" section for the definition of the above
#   parameters.
```

### [temperature_sensor]

通用温度传感器。可以定义任意数量的额外温度传感器，这些传感器通过 M105 命令报告。

```
[temperature_sensor my_sensor]
#sensor_type:
#sensor_pin:
#min_temp:
#max_temp:
#   See the "extruder" section for the definition of the above
#   parameters.
#gcode_id:
#   See the "heater_generic" section for the definition of this
#   parameter.
```

## 温度传感器

Kalico includes definitions for many types of temperature sensors.
These sensors may be used in any config section that requires a
temperature sensor (such as an `[extruder]` or `[heater_bed]`
section).

### 热敏电阻通用设置

Common thermistors. The following parameters are available in heater
sections that use one of these sensors.

```
sensor_type:
#   One of "EPCOS 100K B57560G104F", "ATC Semitec 104GT-2",
#   "ATC Semitec 104NT-4-R025H42G", "Generic 3950",
#   "Honeywell 100K 135-104LAG-J01", "NTC 100K MGB18-104F39050L32",
#   "SliceEngineering 450", or "TDK NTCG104LH104JT1"
sensor_pin:
#   Analog input pin connected to the thermistor. This parameter must
#   be provided.
#pullup_resistor: 4700
#   The resistance (in ohms) of the pullup attached to the thermistor.
#   The default is 4700 ohms.
#inline_resistor: 0
#   The resistance (in ohms) of an extra (not heat varying) resistor
#   that is placed inline with the thermistor. It is rare to set this.
#   The default is 0 ohms.
```

### 温度放大器通用设置

Common temperature amplifiers. The following parameters are available
in heater sections that use one of these sensors.

```
sensor_type:
#   One of "PT100 INA826", "AD595", "AD597", "AD8494", "AD8495",
#   "AD8496", or "AD8497".
sensor_pin:
#   Analog input pin connected to the sensor. This parameter must be
#   provided.
#adc_voltage: 5.0
#   The ADC comparison voltage (in Volts). The default is 5 volts.
#voltage_offset: 0
#   The ADC voltage offset (in Volts). The default is 0.
```

### 直连PT1000传感器

Directly connected PT1000 sensor. The following parameters are
available in heater sections that use one of these sensors.

```
sensor_type: PT1000
sensor_pin:
#   Analog input pin connected to the sensor. This parameter must be
#   provided.
#pullup_resistor: 4700
#   The resistance (in ohms) of the pullup attached to the sensor. The
#   default is 4700 ohms.
```

### MAXxxxxx温度传感器

MAXxxxxx serial peripheral interface (SPI) temperature based
sensors. The following parameters are available in heater sections
that use one of these sensor types.

```
sensor_type:
#   One of "MAX6675", "MAX31855", "MAX31856", or "MAX31865".
sensor_pin:
#   The chip select line for the sensor chip. This parameter must be
#   provided.
#spi_speed: 4000000
#   The SPI speed (in hz) to use when communicating with the chip.
#   The default is 4000000.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#tc_type: K
#tc_use_50Hz_filter: False
#tc_averaging_count: 1
#   The above parameters control the sensor parameters of MAX31856
#   chips. The defaults for each parameter are next to the parameter
#   name in the above list.
#rtd_nominal_r: 100
#rtd_reference_r: 430
#rtd_num_of_wires: 2
#rtd_use_50Hz_filter: False
#   The above parameters control the sensor parameters of MAX31865
#   chips. The defaults for each parameter are next to the parameter
#   name in the above list.
```

### BMP180/BMP280/BME280/BMP388/BME680温度传感器

BMP180/BMP280/BME280/BMP388/BME680 双线接口 (I2C) 环境传感器。请注意，这些传感器不适用于挤出机和加热床，而是用于监测环境温度 (C)、压力 (hPa)、相对湿度以及 BME680 的气体水平。有关可用于报告压力和湿度（除温度外）的 gcode_macro，请参见 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: BME280
#i2c_address:
#   Default is 118 (0x76). The BMP180, BMP388 and some BME280 sensors
#   have an address of 119 (0x77).
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
```

### AHT10/AHT20/AHT21/AHT30温度传感器

AHT10/AHT20/AHT21/AHT30 双线接口 (I2C) 环境传感器。请注意，这些传感器不适用于挤出机和加热床，而是用于监测环境温度 (C) 和相对湿度。有关可用于报告湿度（除温度外）的 gcode_macro，请参见 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: AHT10
#   Must be "AHT1X" , "AHT2X", "AHT3X"
#   Some AHT20 sensors can use "AHT1X"
#i2c_address:
#   Default is 56 (0x38). Some AHT10 sensors give the option to use
#   57 (0x39) by moving a resistor.
#i2c_mcu:
#i2c_bus:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#aht10_report_time:
#   Interval in seconds between readings. Default is 30, minimum is 5
```

### HTU21D传感器

HTU21D 系列双线接口 (I2C) 环境传感器。请注意，此传感器不适用于挤出机和加热床，而是用于监测环境温度 (C) 和相对湿度。有关可用于报告湿度（除温度外）的 gcode_macro，请参见 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type:
#   Must be "HTU21D" , "SI7013", "SI7020", "SI7021" or "SHT21"
#i2c_address:
#   Default is 64 (0x40).
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#htu21d_hold_master:
#   If the sensor can hold the I2C buf while reading. If True no other
#   bus communication can be performed while reading is in progress.
#   Default is False.
#htu21d_resolution:
#   The resolution of temperature and humidity reading.
#   Valid values are:
#    'TEMP14_HUM12' -> 14bit for Temp and 12bit for humidity
#    'TEMP13_HUM10' -> 13bit for Temp and 10bit for humidity
#    'TEMP12_HUM08' -> 12bit for Temp and 08bit for humidity
#    'TEMP11_HUM11' -> 11bit for Temp and 11bit for humidity
#   Default is: "TEMP11_HUM11"
#htu21d_report_time:
#   Interval in seconds between readings. Default is 30
```

### SHT3X传感器

SHT3X 系列双线接口 (I2C) 环境传感器。这些传感器的范围为 -55~125 C，因此可用于例如腔室温度监测。它们还可以充当简单的风扇/加热器控制器。

```
sensor_type: SHT3X
#i2c_address:
#   Default is 68 (0x44).
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
```

### LM75温度传感器

LM75/LM75A 双线 (I2C) 连接的温度传感器。这些传感器的范围为 -55~125 C，因此可用于例如腔室温度监测。它们还可以充当简单的风扇/加热器控制器。

```
sensor_type: LM75
#i2c_address:
#   Default is 72 (0x48). Normal range is 72-79 (0x48-0x4F) and the 3
#   low bits of the address are configured via pins on the chip
#   (usually with jumpers or hard wired).
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#lm75_report_time:
#   Interval in seconds between readings. Default is 0.8, with minimum
#   0.5.
```

### 内置微控制器温度传感器

atsam、atsamd、stm32 和 rp2040 微控制器包含内部温度传感器。可以使用 "temperature_mcu" 传感器来监测这些温度。

```
sensor_type: temperature_mcu
#sensor_mcu: mcu
#   The micro-controller to read from. The default is "mcu".
#reference_voltage:
#   The reference voltage for the ADC of the mcu. Default is 3.3
#sensor_temperature1:
#sensor_adc1:
#   Specify the above two parameters (a temperature in Celsius and an
#   ADC value as a float between 0.0 and 1.0) to calibrate the
#   micro-controller temperature. This may improve the reported
#   temperature accuracy on some chips. A typical way to obtain this
#   calibration information is to completely remove power from the
#   printer for a few hours (to ensure it is at the ambient
#   temperature), then power it up and use the QUERY_ADC command to
#   obtain an ADC measurement. Use some other temperature sensor on
#   the printer to find the corresponding ambient temperature. The
#   default is to use the factory calibration data on the
#   micro-controller (if applicable) or the nominal values from the
#   micro-controller specification.
#sensor_temperature2:
#sensor_adc2:
#   If sensor_temperature1/sensor_adc1 is specified then one may also
#   specify sensor_temperature2/sensor_adc2 calibration data. Doing so
#   may provide calibrated "temperature slope" information. The
#   default is to use the factory calibration data on the
#   micro-controller (if applicable) or the nominal values from the
#   micro-controller specification.
```

### 主机温度传感器

运行主机软件的机器（例如 Raspberry Pi）的温度。

```
sensor_type: temperature_host
#sensor_path:
#   The path to temperature system file. The default is
#   "/sys/class/thermal/thermal_zone0/temp" which is the temperature
#   system file on a Raspberry Pi computer.
```

### DS18B20温度传感器

DS18B20 是一个 1-wire (w1) 数字温度传感器。请注意，此传感器不适用于挤出机和加热床，而是用于监测环境温度 (C)。这些传感器的范围最高可达 125 C，因此可用于例如腔室温度监测。它们还可以充当简单的风扇/加热器控制器。DS18B20 传感器仅在 "host mcu" 上受支持，例如 Raspberry Pi。必须安装 w1-gpio Linux 内核模块。

```
sensor_type: DS18B20
serial_no:
#   Each 1-wire device has a unique serial number used to identify the device,
#   usually in the format 28-031674b175ff. This parameter must be provided.
#   Attached 1-wire devices can be listed using the following Linux command:
#   ls /sys/bus/w1/devices/
#ds18_report_time:
#   Interval in seconds between readings. Default is 3.0, with a minimum of 1.0
#sensor_mcu:
#   The micro-controller to read from. Must be the host_mcu
```

### 假热敏传感器

假热敏传感器是一个虚拟温度传感器，提供固定的温度读数，无需物理传感器。适用于测试、开发和冷挤出机（粘土、混凝土等）。

```
sensor_type: dummy_thermistor
temperature: 25.0
#   The fixed temperature in Celsius to report. The default is 25.0.
#   This value can be changed at runtime using SET_DUMMY_TEMPERATURE command.
#min_temp:
#max_temp:
#   See the "extruder" section for the definition of the above
#   parameters.
```

See [Dummy Thermistor](Dummy_Thermistor.md) for detailed documentation.

### 组合温度传感器

组合温度传感器是基于多个其他传感器的虚拟温度传感器。此传感器可用于挤出机、heater_generic 和加热床。

```
sensor_type: temperature_combined
#sensor_list:
#   Must be provided. List of sensors to combine to new "virtual"
#   sensor. Each entry should be the full name of a temperature-
#   reporting object as it appears in the config (e.g. 'extruder',
#   'heater_bed', or 'temperature_sensor <name>' for custom sensors).
#   E.g. 'temperature_sensor sensor1, temperature_sensor sensor2'
#   E.g. 'extruder, heater_bed'
#   E.g. 'temperature_sensor chamber, extruder, heater_bed'
#combination_method:
#   Must be provided. Combination method used for the sensor.
#   Available options are 'max', 'min', 'mean'.
#maximum_deviation:
#   Must be provided. Maximum permissible deviation between the sensors
#   to combine (e.g. 5 degrees). To disable it, use a large value (e.g. 999.9)
```

### MPC环境传感器

虚拟 MPC 传感器，显示内部环境温度值（如果使用 MPC 以外的任何算法，则默认为 25）

```
sensor_type: mpc_ambient_temperature
heater_name: extruder
#   Put the name of the heater this sensor is tied to (this parameter is required)
#gcode_id: AT
min_temp: 0
max_temp: 325
#ignore_limits: False
#   Ignore the temp limits (if set to true, the min and max temp can be omitted)
#echo_limits_to_console: False
#   If set to true, limits will be echoed to console instead of just being ignored if ignore_limits is true
```

### MPC块传感器

虚拟 MPC 传感器，显示内部块温度值（如果使用 MPC 以外的任何算法，则默认为 25）

```
sensor_type: mpc_block_temperature
heater_name: extruder
#   Put the name of the heater this sensor is tied to (this parameter is required)
#gcode_id: BE
min_temp: 0
max_temp: 325
#ignore_limits: False
#   Ignore the temp limits (if set to true, the min and max temp can be omitted)
#echo_limits_to_console: False
#   If set to true, limits will be echoed to console instead of just being ignored if ignore_limits is true
```

### INDX温度传感器

由 [Bondtech INDX 工具板](#indx) 报告的温度。默认的 "heater" 类型报告喷嘴温度，是挤出机要使用的类型；其他类型主要用于诊断。

```
sensor_type: indx
#indx_sensor: heater
#   The temperature to report. Available kinds are "heater" (nozzle
#   temperature), "sensor" (IR sensor die temperature), "board"
#   (toolboard temperature), "bracket" (sensor bracket temperature),
#   "ldc_coil" (eddy current probe coil temperature), "check_model"
#   (thermal model prediction) and "check_model_delta" (difference
#   between the model prediction and the measured temperature).
```


## 风扇

### [fan]

打印冷却风扇。

```
[fan]
pin:
#   Output pin controlling the fan. This parameter must be provided.
#max_power: 1.0
#   The maximum power (0.0 to 1.0) that the pin may be set to. A value
#   of 1.0 enables the pin fully for extended periods, while 0.5 allows
#   it for no more than half the time. Use it to limit total power output
#   (over extended periods) to the fan. This value is combined with
#   min_power to scale fan speed. With `min_power` at 0.3 and
#   `max_power` at 1.0, fan speed request scales between 0.3 (min_power)
#   and 1.0 (max_power). Requesting 10% fan speed results in a value of
#   0.37. Default is 1.0.
#shutdown_speed: 0
#   The desired fan speed (expressed as a value from 0.0 to 1.0) if
#   the micro-controller software enters an error state. The default
#   is 0.
#cycle_time: 0.010
#   The amount of time (in seconds) for each PWM power cycle to the
#   fan. It is recommended this be 10 milliseconds or greater when
#   using software based PWM. The default is 0.010 seconds.
#hardware_pwm: False
#   Enable this to use hardware PWM instead of software PWM. Most fans
#   do not work well with hardware PWM, so it is not recommended to
#   enable this unless there is an electrical requirement to switch at
#   very high speeds. When using hardware PWM the actual cycle time is
#   constrained by the implementation and may be significantly
#   different than the requested cycle_time. The default is False.
#kick_start_time: 0.100
#   Time (in seconds) to run the fan at full speed when either first
#   enabling or increasing it by more than 50% (helps get the fan
#   spinning). The default is 0.100 seconds.
#min_power: 0.0
#   The minimum input power which will power the fan (expressed as a
#   value from 0.0 to 1.0). The default is 0.0.
#
#   To calibrate this setting, start with min_power=0 and max_power=1
#   Gradually lower the fan speed to determine the lowest
#   input speed which reliably drives the fan without stalls. Set
#   min_power to the duty cycle corresponding to this value (for
#   example, 12% -> 0.12) or slightly higher.
#tachometer_pin:
#   Tachometer input pin for monitoring fan speed. A pullup is generally
#   required. This parameter is optional.
#tachometer_ppr: 2
#   When tachometer_pin is specified, this is the number of pulses per
#   revolution of the tachometer signal. For a BLDC fan this is
#   normally half the number of poles. The default is 2.
#tachometer_poll_interval: 0.0015
#   When tachometer_pin is specified, this is the polling period of the
#   tachometer pin, in seconds. The default is 0.0015, which is fast
#   enough for fans below 10000 RPM at 2 PPR. This must be smaller than
#   30/(tachometer_ppr*rpm), with some margin, where rpm is the
#   maximum speed (in RPM) of the fan.
#enable_pin:
#   Optional pin to enable power to the fan. This can be useful for fans
#   with dedicated PWM inputs. Some of these fans stay on even at 0% PWM
#   input. In such a case, the PWM pin can be used normally, and e.g. a
#   ground-switched FET(standard fan pin) can be used to control power to
#   the fan.
#off_below:
#   These option is deprecated and should no longer be specified.
#   Use `min_power` instead.
#initial_speed:
#   Fan speed will be set to this value on startup if specified. Value
#   is from 0.0 to 1.0.
```

### [heated_fan]

加热打印冷却风扇。用于高温打印的实验性模块，需要零件冷却空气更接近打印零件的温度。

```

[heated_fan]
#   See the "fan" section for a description for fan parameters.
#   See the "heater_generic" section for a description for the heater
#   parameters.
#heater_temp: 50
#   The target temperature (in Celsius) for the heater when the fan is
#   turned on. The default is 50 Celsius.
#min_speed: 1.0
#   The minimum fan speed (expressed as a value from 0.0 to 1.0) that the
#   fan will be set to when its associated heater is on (e.g.: to protect
#   ducts from melting). If the fan is set to a speed lower than min_speed,
#   the min_speed value is applied. The default is 1.0 (100%)
#idle_timeout: 60
#   A timeout in seconds for the fan to stay on when it is requested to turn
#   off, to protect ducts from melting. The default is 60 (s).
```

### [heater_fan]

加热器冷却风扇（可以定义任意数量的 "heater_fan" 前缀部分）。"加热器风扇" 是在其关联的加热器活动时启用的风扇。默认情况下，heater_fan 的 shutdown_speed 等于 max_power。

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
#   See the "fan" section for a description of the above parameters.
#heater: extruder
#   Name of the config section defining the heater that this fan is
#   associated with. If a comma separated list of heater names is
#   provided here, then the fan will be enabled when any of the given
#   heaters are enabled. The default is "extruder".
#heater_temp: 50.0
#   A temperature (in Celsius) that the heater must drop below before
#   the fan is disabled. The default is 50 Celsius.
#fan_speed: 1.0
#   The fan speed (expressed as a value from 0.0 to 1.0) that the fan
#   will be set to when its associated heater is enabled. The default
#   is 1.0
```

### [controller_fan]

控制器冷却风扇（可以定义任意数量的 "controller_fan" 前缀部分）。"控制器风扇" 是在其关联的加热器或关联的步进电机驱动器活动时启用的风扇。当达到 idle_timeout 时，风扇将停止，以确保在停用受监视组件后不会发生过热。

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
#   See the "fan" section for a description of the above parameters.
#fan_speed: 1.0
#   The fan speed (expressed as a value from 0.0 to 1.0) that the fan
#   will be set to when a heater or stepper driver is active.
#   The default is 1.0
#idle_timeout:
#   The amount of time (in seconds) after a stepper driver or heater
#   was active and the fan should be kept running. The default
#   is 30 seconds.
#idle_speed:
#   The fan speed (expressed as a value from 0.0 to 1.0) that the fan
#   will be set to when a heater or stepper driver was active and
#   before the idle_timeout is reached. The default is fan_speed.
#heater:
#stepper:
#   Name of the config section defining the heater/stepper that this fan
#   is associated with. If a comma separated list of heater/stepper names
#   is provided here, then the fan will be enabled when any of the given
#   heaters/steppers are enabled. The default heater is "extruder", the
#   default stepper is all of them.
```

### [temperature_fan]

温度触发的冷却风扇（可以定义任意数量的 "temperature_fan" 前缀部分）。"温度风扇" 是在其关联的传感器高于设定温度时启用的风扇。默认情况下，temperature_fan 的 shutdown_speed 等于 max_power。

有关更多信息，请参见[命令参考](G-Codes.md#temperature_fan)。

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
#   See the "fan" section for a description of the above parameters.
#sensor_type:
#sensor_pin:
#control:
#max_delta:
#min_temp:
#max_temp:
#   See the "extruder" section for a description of the above parameters.
#pid_Kp:
#pid_Ki:
#pid_Kd:
#   The proportional (pid_Kp), integral (pid_Ki), and derivative
#   (pid_Kd) settings for the PID feedback control system. Kalico
#   evaluates the PID settings with the following general formula:
#     fan_pwm = max_power - (Kp*e + Ki*integral(e) - Kd*derivative(e)) / 255
#   Where "e" is "target_temperature - measured_temperature" and
#   "fan_pwm" is the requested fan rate with 0.0 being full off and
#   1.0 being full on. The pid_Kp, pid_Ki, and pid_Kd parameters must
#   be provided when the PID control algorithm is enabled.
#pid_deriv_time: 2.0
#   A time value (in seconds) over which temperature measurements will
#   be smoothed when using the PID control algorithm. This may reduce
#   the impact of measurement noise. The default is 2 seconds.
#target_temp: 40.0
#   A temperature (in Celsius) that will be the target temperature.
#   The default is 40 degrees.
#max_speed: 1.0
#   The fan speed (expressed as a value from 0.0 to 1.0) that the fan
#   will be set to when the sensor temperature exceeds the set value.
#   The default is 1.0.
#min_speed: 0.3
#   The minimum fan speed (expressed as a value from 0.0 to 1.0) that
#   the fan will be set to for PID temperature fans.
#   The default is 0.3.
#gcode_id:
#   If set, the temperature will be reported in M105 queries using the
#   given id. The default is to not report the temperature via M105.
#reverse: False
#   If true, the working mode of the fan is reversed. If the temperature
#   is lower than the target temperature, the fan speed increases;
#   otherwise, the fan speed decreases.
#   The default is False.
```

```
control: curve
#points:
#  50.0, 0.0
#  55.0, 0.5
#   A user might defne a list of points which consist of a temperature with
#   it's associated fan speed (temp, fan_speed).
#   The target_temp value defines the temperature at which the fan will run
#   at full speed.
#   The algorithm will use linear interpolation to get the fan speeds
#   between two points (if one has defined 0.0 for 50° and 1.0 for 60° the
#   fan would run with 0.5 at 55°)
#cooling_hysteresis: 0.0
#   define the temperature hysteresis for lowering the fan speed
#   (in simple terms this setting offsets the fan curve when cooling down
#   by the specified amount of degrees celsius. For example, if the
#   hysteresis is set to 5°C, the fan curve will be moved by -5°C. This
#   setting can be used to reduce the effects of quickly changing
#   temperatures around a target temperature which would cause the fan to
#   speed up and slow down repeatedly.)
#heating_hysteresis: 0.0
#   same as cooling_hysteresis but for increasing the fan speed, it is
#   recommended to be left at 0 for safety reasons
#smooth_readings: 10
#   This parameter is deprecated and should no longer be used.
```

### [fan_generic]

手动控制的风扇（可以定义任意数量的 "fan_generic" 前缀部分）。手动控制的风扇的速度使用 SET_FAN_SPEED [gcode 命令](G-Codes.md#fan_generic) 设置。

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
#   See the "fan" section for a description of the above parameters.
```

## LED灯

### [led]

通过微控制器 PWM 引脚控制的 LED（和 LED 灯条）支持（可以定义任意数量的 "led" 前缀部分）。有关更多信息，请参见[命令参考](G-Codes.md#led)。

```
[led my_led]
#red_pin:
#green_pin:
#blue_pin:
#white_pin:
#   The pin controlling the given LED color. At least one of the above
#   parameters must be provided.
#cycle_time: 0.010
#   The amount of time (in seconds) per PWM cycle. It is recommended
#   this be 10 milliseconds or greater when using software based PWM.
#   The default is 0.010 seconds.
#hardware_pwm: False
#   Enable this to use hardware PWM instead of software PWM. When
#   using hardware PWM the actual cycle time is constrained by the
#   implementation and may be significantly different than the
#   requested cycle_time. The default is False.
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   Sets the initial LED color. Each value should be between 0.0 and
#   1.0. The default for each color is 0.
```

### [neopixel]

Neopixel（也称为 WS2812）LED 支持（可以定义任意数量的 "neopixel" 前缀部分）。有关更多信息，请参见[命令参考](G-Codes.md#led)。

请注意，[linux mcu](RPi_microcontroller.md) 实现目前不支持直接连接的 neopixel。当前使用 Linux 内核接口的设计不允许这种场景，因为内核 GPIO 接口速度不够快，无法提供所需的脉冲速率。

```
[neopixel my_neopixel]
pin:
#   The pin connected to the neopixel. This parameter must be
#   provided.
#chain_count:
#   The number of Neopixel chips that are "daisy chained" to the
#   provided pin. The default is 1 (which indicates only a single
#   Neopixel is connected to the pin).
#color_order: GRB
#   Set the pixel order required by the LED hardware (using a string
#   containing the letters R, G, B, W with W optional). Alternatively,
#   this may be a comma separated list of pixel orders - one for each
#   LED in the chain. The default is GRB.
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   See the "led" section for information on these parameters.
```

### [dotstar]

Dotstar（也称为 APA102）LED 支持（可以定义任意数量的 "dotstar" 前缀部分）。有关更多信息，请参见[命令参考](G-Codes.md#led)。

```
[dotstar my_dotstar]
data_pin:
#   The pin connected to the data line of the dotstar. This parameter
#   must be provided.
clock_pin:
#   The pin connected to the clock line of the dotstar. This parameter
#   must be provided.
#chain_count:
#   See the "neopixel" section for information on this parameter.
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#   See the "led" section for information on these parameters.
```

### [pca9533]

PCA9533 LED 支持。PCA9533 用于 mightyboard。

```
[pca9533 my_pca9533]
#i2c_address: 98
#   The i2c address that the chip is using on the i2c bus. Use 98 for
#   the PCA9533/1, 99 for the PCA9533/2. The default is 98.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   See the "led" section for information on these parameters.
```

### [pca9632]

PCA9632 LED 支持。PCA9632 用于 FlashForge Dreamer。

```
[pca9632 my_pca9632]
#i2c_address: 98
#   The i2c address that the chip is using on the i2c bus. This may be
#   96, 97, 98, or 99.  The default is 98.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#color_order: RGBW
#   Set the pixel order of the LED (using a string containing the
#   letters R, G, B, W). The default is RGBW.
#initial_RED: 0.0
#initial_GREEN: 0.0
#initial_BLUE: 0.0
#initial_WHITE: 0.0
#   See the "led" section for information on these parameters.
```

## 额外伺服、按钮和其他引脚

### [servo]

舵机（可以定义任意数量的 "servo" 前缀部分）。可以使用 SET_SERVO [g-code 命令](G-Codes.md#servo) 控制舵机。例如：SET_SERVO SERVO=my_servo ANGLE=180

```
[servo my_servo]
pin:
#   PWM output pin controlling the servo. This parameter must be
#   provided.
#maximum_servo_angle: 180
#   The maximum angle (in degrees) that this servo can be set to. The
#   default is 180 degrees.
#minimum_pulse_width: 0.001
#   The minimum pulse width time (in seconds). This should correspond
#   with an angle of 0 degrees. The default is 0.001 seconds.
#maximum_pulse_width: 0.002
#   The maximum pulse width time (in seconds). This should correspond
#   with an angle of maximum_servo_angle. The default is 0.002
#   seconds.
#initial_angle:
#   Initial angle (in degrees) to set the servo to. The default is to
#   not send any signal at startup.
#initial_pulse_width:
#   Initial pulse width time (in seconds) to set the servo to. (This
#   is only valid if initial_angle is not set.) The default is to not
#   send any signal at startup.
```

### [gcode_button]

按下或释放按钮时执行 gcode（或者引脚状态改变时）。您可以使用 `QUERY_BUTTON button=my_gcode_button` 来检查按钮的状态。

```
[gcode_button my_gcode_button]
pin:
#   The pin on which the button is connected. This parameter must be
#   provided.
#analog_range:
#   Two comma separated resistances (in Ohms) specifying the minimum
#   and maximum resistance range for the button. If analog_range is
#   provided then the pin must be an analog capable pin. The default
#   is to use digital gpio for the button.
#analog_pullup_resistor:
#   The pullup resistance (in Ohms) when analog_range is specified.
#   The default is 4700 ohms.
#press_gcode:
#   A list of G-Code commands to execute when the button is pressed.
#   G-Code templates are supported. This parameter must be provided.
#release_gcode:
#   A list of G-Code commands to execute when the button is released.
#   G-Code templates are supported. The default is to not run any
#   commands on a button release.
#debounce_delay:
#   A period of time in seconds to debounce events prior to running the
#   button gcode. If the button is pressed and released during this
#   delay, the entire button press is ignored. Default is 0.
```

### [output_pin]

运行时可配置的输出引脚（可以定义任意数量的 "output_pin" 前缀部分）。此处配置的引脚将设置为输出引脚，您可以在运行时使用 "SET_PIN PIN=my_pin VALUE=.1" 类型的扩展 [g-code 命令](G-Codes.md#output_pin) 修改它们。

```
[output_pin my_pin]
pin:
#   The pin to configure as an output. This parameter must be
#   provided.
#pwm: False
#   Set if the output pin should be capable of pulse-width-modulation.
#   If this is true, the value fields should be between 0 and 1; if it
#   is false the value fields should be either 0 or 1. The default is
#   False.
#value:
#   The value to initially set the pin to during MCU configuration.
#   The default is 0 (for low voltage).
#shutdown_value:
#   The value to set the pin to on an MCU shutdown event. The default
#   is 0 (for low voltage).
#cycle_time: 0.100
#   The amount of time (in seconds) per PWM cycle. It is recommended
#   this be 10 milliseconds or greater when using software based PWM.
#   The default is 0.100 seconds for pwm pins.
#hardware_pwm: False
#   Enable this to use hardware PWM instead of software PWM. When
#   using hardware PWM the actual cycle time is constrained by the
#   implementation and may be significantly different than the
#   requested cycle_time. The default is False.
#scale:
#   This parameter can be used to alter how the 'value' and
#   'shutdown_value' parameters are interpreted for pwm pins. If
#   provided, then the 'value' parameter should be between 0.0 and
#   'scale'. This may be useful when configuring a PWM pin that
#   controls a stepper voltage reference. The 'scale' can be set to
#   the equivalent stepper amperage if the PWM were fully enabled, and
#   then the 'value' parameter can be specified using the desired
#   amperage for the stepper. The default is to not scale the 'value'
#   parameter.
#maximum_mcu_duration:
#static_value:
#   These options are deprecated and should no longer be specified.
```

### [static_pwm_clock]

静态可配置输出引脚（可以定义任意数量的 "static_pwm_clock" 前缀部分）。此处配置的引脚将设置为时钟输出引脚。通常用于为板上的其他硬件提供时钟输入。
```
[static_pwm_clock my_pin]
pin:
#   The pin to configure as an output. This parameter must be provided.
#frequency: 100
#   Target output frequency.
```

### [pwm_tool]

Pulse width modulation digital output pins capable of high speed
updates (one may define any number of sections with an "output_pin"
prefix). Pins configured here will be setup as output pins and one may
modify them at run-time using "SET_PIN PIN=my_pin VALUE=.1" type
extended [g-code commands](G-Codes.md#output_pin).

```
[pwm_tool my_tool]
pin:
#   The pin to configure as an output. This parameter must be provided.
#maximum_mcu_duration:
#   The maximum duration a non-shutdown value may be driven by the MCU
#   without an acknowledge from the host.
#   If host can not keep up with an update, the MCU will shutdown
#   and set all pins to their respective shutdown values.
#   Default: 0 (disabled)
#   Usual values are around 5 seconds.
#value:
#shutdown_value:
#cycle_time: 0.100
#hardware_pwm: False
#scale:
#   See the "output_pin" section for the definition of these parameters.
```

### [pwm_cycle_time]

Run-time configurable output pins with dynamic pwm cycle timing (one
may define any number of sections with an "pwm_cycle_time" prefix).
Pins configured here will be setup as output pins and one may modify
them at run-time using "SET_PIN PIN=my_pin VALUE=.1 CYCLE_TIME=0.100"
type extended [g-code commands](G-Codes.md#pwm_cycle_time).

```
[pwm_cycle_time my_pin]
pin:
#value:
#shutdown_value:
#cycle_time: 0.100
#scale:
#   See the "output_pin" section for information on these parameters.
```

### [input_pin]

通用数字输入引脚（可以定义任意数量的 "input_pin" 前缀部分）。此处配置的引脚将设置为 GPIO 输入引脚，可以在运行时使用 "QUERY_INPUT_PIN PIN=my_sensor" 类型的扩展 [g-code 命令](G-Codes.md#input_pin) 查询。

```
[input_pin my_sensor]
pin:
#   The pin to configure as an input. This parameter must be provided.
#pull_up:
#   Set if the internal pull-up resistor should be enabled. Use "^pin"
#   syntax in the pin description as an alternative. The default is
#   False.
#invert: False
#   Set if the pin logic should be inverted. Use "!pin" syntax in the
#   pin description as an alternative. The default is False.
#poll_interval: 0.5
#   The amount of time (in seconds) between polling cycles. This
#   controls how often the pin state is refreshed for status queries.
#   The default is 0.5 seconds (range: 0.05 to 5.0).
```

### [adc_pin]

通用模拟输入 (ADC) 引脚（可以定义任意数量的 "adc_pin" 前缀部分）。此处配置的引脚将设置为 ADC 输入引脚，可以在运行时使用 "QUERY_ADC_PIN PIN=my_adc" 类型的扩展 [g-code 命令](G-Codes.md#adc_pin) 查询。

```
[adc_pin my_adc]
pin:
#   The pin to configure as an ADC input. This parameter must be
#   provided.
#sample_time: 0.001
#   The amount of time (in seconds) per ADC sample. The default is
#   0.001 seconds.
#sample_count: 8
#   The number of ADC samples to take and average. The default is 8.
#report_time: 0.015
#   The amount of time (in seconds) between reporting the ADC value.
#   The default is 0.015 seconds.
#min_value: 0.0
#   The minimum expected ADC value. Values outside this range will
#   trigger a shutdown if range_check_count is non-zero. The default
#   is 0.0.
#max_value: 1.0
#   The maximum expected ADC value. Values outside this range will
#   trigger a shutdown if range_check_count is non-zero. The default
#   is 1.0.
#range_check_count: 0
#   The number of consecutive out-of-range readings before triggering
#   a shutdown. The default is 0 (no range checking).
```

### [dac_pin]

使用 PWM 的通用模拟输出 (DAC) 引脚（可以定义任意数量的 "dac_pin" 前缀部分）。此处配置的引脚将设置为 PWM 输出引脚，可以在运行时使用 "SET_DAC_PIN PIN=my_dac VALUE=1.65" 类型的扩展 [g-code 命令](G-Codes.md#dac_pin) 控制。

```
[dac_pin my_dac]
pin:
#   The pin to configure as a DAC output. This parameter must be
#   provided.
#scale: 3.3
#   The voltage range of the DAC output. The VALUE parameter in
#   SET_DAC_PIN commands will be interpreted as a voltage between 0
#   and scale. The default is 3.3.
#value: 0.0
#   The initial voltage to set the pin to during MCU configuration.
#   The default is 0.0.
#shutdown_value: 0.0
#   The voltage to set the pin to on an MCU shutdown event. The
#   default is 0.0.
#cycle_time: 0.100
#   The amount of time (in seconds) per PWM cycle. The default is
#   0.100 seconds.
#hardware_pwm: False
#   Enable this to use hardware PWM instead of software PWM. The
#   default is False.
```

### [static_digital_output]

静态配置的数字输出引脚（可以定义任意数量的 "static_digital_output" 前缀部分）。此处配置的引脚将在 MCU 配置期间设置为 GPIO 输出。它们不能在运行时更改。

```
[static_digital_output my_output_pins]
pins:
#   A comma separated list of pins to be set as GPIO output pins. The
#   pin will be set to a high level unless the pin name is prefaced
#   with "!". This parameter must be provided.
```

### [hc595]

74HC595 移位寄存器输出扩展（可以定义任意数量的 "hc595" 前缀部分）。74HC595 是一个串行到并行移位寄存器，仅使用 3 个 MCU 引脚（数据、时钟、锁存）即可提供 8 个额外的数字输出引脚。多个芯片可以菊花链连接，最多 32 个输出。HC595 输出可以在任何接受标准数字输出引脚的地方使用，通过将它们引用为 `chip_name:N`（其中 N 是输出编号，从 0 到 chain_count*8 - 1）。chip_name 是在配置部分标题中给出的名称。

```
[hc595 my_shift]
data_pin:
#   Pin connected to the 74HC595 SER (serial data input) line,
#   typically pin 14 on the IC. This parameter must be provided.
clock_pin:
#   Pin connected to the 74HC595 SRCLK (shift register clock) line,
#   typically pin 11 on the IC. This parameter must be provided.
latch_pin:
#   Pin connected to the 74HC595 RCLK (storage register clock/latch)
#   line, typically pin 12 on the IC. This parameter must be provided.
#oe_pin:
#   Optional pin connected to the 74HC595 OE (output enable) line,
#   typically pin 13 on the IC. This pin is active low. If not
#   specified, the OE pin should be tied to ground to permanently
#   enable the outputs.
#chain_count: 1
#   The number of daisy-chained 74HC595 chips. Must be between 1 and 4.
#   Each chip adds 8 additional output pins. The default is 1.
```

#### HC595 Wiring

For a single 74HC595, connect:
- 74HC595 pin 14 (SER) to the MCU pin specified by `data_pin`
- 74HC595 pin 11 (SRCLK) to the MCU pin specified by `clock_pin`
- 74HC595 pin 12 (RCLK) to the MCU pin specified by `latch_pin`
- 74HC595 pin 13 (OE) to ground (or to the MCU pin specified by `oe_pin`)
- 74HC595 pin 10 (SRCLR) to VCC
- 74HC595 pin 8 (GND) to ground
- 74HC595 pin 16 (VCC) to +3.3V or +5V
- 74HC595 output pins are QA-QH (pins 15, 1-7)

For daisy-chaining, connect Q7' (pin 9) of the first chip to SER
(pin 14) of the next chip. All chips share the same CLOCK, LATCH,
and OE lines.

#### HC595 Usage Example

```
[hc595 my_shift]
data_pin: PA1
clock_pin: PA2
latch_pin: PA3

# Use HC595 output 0 to control a fan
[fan]
pin: my_shift:0

# Use HC595 output 3 to control a heater
[heater_generic chamber_heater]
heater_pin: my_shift:3
max_power: 1.0
# ... additional heater parameters

# Use HC595 output 7 as a generic output pin
[output_pin my_output]
pin: my_shift:7
value: 0
shutdown_value: 0
```

The following extended G-Code command is available:

- `SET_HC595 CHIP=<config_name> [BITS=<value>]`: Set or query all
  HC595 output pins at once. Without BITS, the current pin states
  are reported. With BITS, the given integer value is applied to
  all outputs (bit 0 = output 0, etc.).

### [multi_pin]

多引脚输出（可以定义任意数量的 "multi_pin" 前缀部分）。multi_pin 输出创建一个内部引脚别名，每次设置别名引脚时都可以修改多个输出引脚。例如，您可以定义一个包含两个引脚的 "[multi_pin my_fan]" 对象，然后在 "[fan]" 部分中设置 "pin=multi_pin:my_fan" - 每次风扇更改时，两个输出引脚都会更新。这些别名不能与步进电机引脚一起使用。

```
[multi_pin my_multi_pin]
pins:
#   A comma separated list of pins associated with this alias. This
#   parameter must be provided.
```

## TMC步进驱动配置

UART/SPI 模式下的 Trinamic 步进电机驱动器配置。更多信息请参见 [TMC 驱动器指南](TMC_Drivers.md)和[命令参考](G-Codes.md#tmcxxxx)。

### [tmc2130]

通过 SPI 总线配置 TMC2130 步进电机驱动器。要使用此功能，请定义一个以 "tmc2130" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc2130 stepper_x]"）。

```
[tmc2130 stepper_x]
cs_pin:
#   The pin corresponding to the TMC2130 chip select line. This pin
#   will be set to low at the start of SPI messages and raised to high
#   after the message completes. This parameter must be provided.
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#chain_position:
#chain_length:
#   These parameters configure an SPI daisy chain. The two parameters
#   define the stepper position in the chain and the total chain length.
#   Position 1 corresponds to the stepper that connects to the MOSI signal.
#   The default is to not use an SPI daisy chain.
#interpolate: True
#   If true, enable step interpolation (the driver will internally
#   step at a rate of 256 micro-steps). This interpolation does
#   introduce a small systemic positional deviation - see
#   TMC_Drivers.md for details. The default is True.
run_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during stepper movement. This parameter must be provided.
#hold_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   when the stepper is not moving. Setting a hold_current is not
#   recommended (see TMC_Drivers.md for details). The default is to
#   not reduce the current.
#home_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during homing procedures. The default is to not reduce the current.
#current_change_dwell_time:
#   The amount of time (in seconds) to wait after changing homing current.
#   The default is 0.5 seconds.
sense_resistor:
#   The resistance (in ohms) of the driver sense resistor. This parameter
#   must be provided. Common values are 0.110 ohms for most TMC2209 drivers
#   and 0.075 ohms for TMC5160 drivers. Check your stepper driver documentation
#   or board schematic to confirm the correct value.
#stealthchop_threshold: 0
#   The velocity (in mm/s) to set the "stealthChop" threshold to. When
#   set, "stealthChop" mode will be enabled if the stepper motor
#   velocity is below this value. Note that the "sensorless homing"
#   code may temporarily override this setting during homing
#   operations. The default is 0, which disables "stealthChop" mode.
#coolstep_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "CoolStep"
#   threshold to. If set, the coolstep feature will be enabled when
#   the stepper motor velocity is near or above this value. Important
#   - if coolstep_threshold is set and "sensorless homing" is used,
#   then one must ensure that the homing speed is above the coolstep
#   threshold! The default is to not enable the coolstep feature.
#high_velocity_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "high
#   velocity" threshold (THIGH) to. This is typically used to disable
#   the "CoolStep" feature at high speeds. The default is to not set a
#   TMC "high velocity" threshold.
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
#   These fields control the Microstep Table registers directly. The optimal
#   wave table is specific to each motor and might vary with current. An
#   optimal configuration will have minimal print artifacts caused by
#   non-linear stepper movement. The values specified above are the default
#   values used by the driver. The value must be specified as a decimal integer
#   (hex form is not supported). In order to compute the wave table fields,
#   see the tmc2130 "Calculation Sheet" from the Trinamic website.
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
#   Set the given register during the configuration of the TMC2130
#   chip. This may be used to set custom motor parameters. The
#   defaults for each parameter are next to the parameter name in the
#   above list.
#diag0_pin:
#diag1_pin:
#   The micro-controller pin attached to one of the DIAG lines of the
#   TMC2130 chip. Only a single diag pin should be specified. The pin
#   is "active low" and is thus normally prefaced with "^!". Setting
#   this creates a "tmc2130_stepper_x:virtual_endstop" virtual pin
#   which may be used as the stepper's endstop_pin. Doing this enables
#   "sensorless homing". (Be sure to also set driver_SGT to an
#   appropriate sensitivity value.) The default is to not enable
#   sensorless homing.
```

### [tmc2208]

通过单线 UART 配置 TMC2208（或 TMC2224）步进电机驱动器。要使用此功能，请定义一个以 "tmc2208" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc2208 stepper_x]"）。

```
[tmc2208 stepper_x]
uart_pin:
#   The pin connected to the TMC2208 PDN_UART line. This parameter
#   must be provided.
#tx_pin:
#   If using separate receive and transmit lines to communicate with
#   the driver then set uart_pin to the receive pin and tx_pin to the
#   transmit pin. The default is to use uart_pin for both reading and
#   writing.
#select_pins:
#   A comma separated list of pins to set prior to accessing the
#   tmc2208 UART. This may be useful for configuring an analog mux for
#   UART communication. The default is to not configure any pins.
#interpolate: True
#   If true, enable step interpolation (the driver will internally
#   step at a rate of 256 micro-steps). This interpolation does
#   introduce a small systemic positional deviation - see
#   TMC_Drivers.md for details. The default is True.
run_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during stepper movement. This parameter must be provided.
#hold_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   when the stepper is not moving. Setting a hold_current is not
#   recommended (see TMC_Drivers.md for details). The default is to
#   not reduce the current.
#home_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during homing procedures. The default is to not reduce the current.
#current_change_dwell_time:
#   The amount of time (in seconds) to wait after changing homing current.
#   The default is 0.5 seconds.
sense_resistor:
#   The resistance (in ohms) of the driver sense resistor. This parameter
#   must be provided. Common values are 0.110 ohms for most TMC2209 drivers
#   and 0.075 ohms for TMC5160 drivers. Check your stepper driver documentation
#   or board schematic to confirm the correct value.
#stealthchop_threshold: 0
#   The velocity (in mm/s) to set the "stealthChop" threshold to. When
#   set, "stealthChop" mode will be enabled if the stepper motor
#   velocity is below this value. Note that the "sensorless homing"
#   code may temporarily override this setting during homing
#   operations. The default is 0, which disables "stealthChop" mode.
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
#   Set the given register during the configuration of the TMC2208
#   chip. This may be used to set custom motor parameters. The
#   defaults for each parameter are next to the parameter name in the
#   above list.
```

### [tmc2209]

通过单线 UART 配置 TMC2209 步进电机驱动器。要使用此功能，请定义一个以 "tmc2209" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc2209 stepper_x]"）。

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
#   See the "tmc2208" section for the definition of these parameters.
#coolstep_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "CoolStep"
#   threshold to. If set, the coolstep feature will be enabled when
#   the stepper motor velocity is near or above this value. Important
#   - if coolstep_threshold is set and "sensorless homing" is used,
#   then one must ensure that the homing speed is above the coolstep
#   threshold! The default is to not enable the coolstep feature.
#uart_address:
#   The address of the TMC2209 chip for UART messages (an integer
#   between 0 and 3). This is typically used when multiple TMC2209
#   chips are connected to the same UART pin. The default is zero.
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
#   Set the given register during the configuration of the TMC2209
#   chip. This may be used to set custom motor parameters. The
#   defaults for each parameter are next to the parameter name in the
#   above list.
#diag_pin:
#   The micro-controller pin attached to the DIAG line of the TMC2209
#   chip. The pin is normally prefaced with "^" to enable a pullup.
#   Setting this creates a "tmc2209_stepper_x:virtual_endstop" virtual
#   pin which may be used as the stepper's endstop_pin. Doing this
#   enables "sensorless homing". (Be sure to also set driver_SGTHRS to
#   an appropriate sensitivity value.) The default is to not enable
#   sensorless homing.
```

### [tmc2660]

通过 SPI 总线配置 TMC2660 步进电机驱动器。要使用此功能，请定义一个以 tmc2660 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc2660 stepper_x]"）。

```
[tmc2660 stepper_x]
cs_pin:
#   The pin corresponding to the TMC2660 chip select line. This pin
#   will be set to low at the start of SPI messages and set to high
#   after the message transfer completes. This parameter must be
#   provided.
#spi_speed: 4000000
#   SPI bus frequency used to communicate with the TMC2660 stepper
#   driver. The default is 4000000.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#interpolate: True
#   If true, enable step interpolation (the driver will internally
#   step at a rate of 256 micro-steps). This only works if microsteps
#   is set to 16. Interpolation does introduce a small systemic
#   positional deviation - see TMC_Drivers.md for details. The default
#   is True.
run_current:
#   The amount of current (in amps RMS) used by the driver during
#   stepper movement. This parameter must be provided.
#home_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during homing procedures. The default is to not reduce the current.
#current_change_dwell_time:
#   The amount of time (in seconds) to wait after changing homing current.
#   The default is 0.5 seconds.
sense_resistor:
#   The resistance (in ohms) of the driver sense resistor. This parameter
#   must be provided. Common values are 0.110 ohms for most TMC2209 drivers
#   and 0.075 ohms for TMC5160 drivers. Check your stepper driver documentation
#   or board schematic to confirm the correct value.
#idle_current_percent: 100
#   The percentage of the run_current the stepper driver will be
#   lowered to when the idle timeout expires (you need to set up the
#   timeout using a [idle_timeout] config section). The current will
#   be raised again once the stepper has to move again. Make sure to
#   set this to a high enough value such that the steppers do not lose
#   their position. There is also small delay until the current is
#   raised again, so take this into account when commanding fast moves
#   while the stepper is idling. The default is 100 (no reduction).
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
#   Set the given parameter during the configuration of the TMC2660
#   chip. This may be used to set custom driver parameters. The
#   defaults for each parameter are next to the parameter name in the
#   list above. See the TMC2660 datasheet about what each parameter
#   does and what the restrictions on parameter combinations are. Be
#   especially aware of the CHOPCONF register, where setting CHM to
#   either zero or one will lead to layout changes (the first bit of
#   HDEC) is interpreted as the MSB of HSTRT in this case).
```

### [tmc2240]

通过 SPI 总线或 UART 配置 TMC2240 步进电机驱动器。要使用此功能，请定义一个以 "tmc2240" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc2240 stepper_x]"）。

```
[tmc2240 stepper_x]
cs_pin:
#   The pin corresponding to the TMC2240 chip select line. This pin
#   will be set to low at the start of SPI messages and raised to high
#   after the message completes. This parameter must be provided.
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#uart_pin:
#   The pin connected to the TMC2240 DIAG1/SW line. If this parameter
#   is provided UART communication is used rather then SPI.
#chain_position:
#chain_length:
#   These parameters configure an SPI daisy chain. The two parameters
#   define the stepper position in the chain and the total chain length.
#   Position 1 corresponds to the stepper that connects to the MOSI signal.
#   The default is to not use an SPI daisy chain.
#interpolate: True
#   If true, enable step interpolation (the driver will internally
#   step at a rate of 256 micro-steps). The default is True.
run_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during stepper movement. This parameter must be provided.
#hold_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   when the stepper is not moving. Setting a hold_current is not
#   recommended (see TMC_Drivers.md for details). The default is to
#   not reduce the current.
#home_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during homing procedures. The default is to not reduce the current.
#current_change_dwell_time:
#   The amount of time (in seconds) to wait after changing homing current.
#   The default is 0.5 seconds.
#rref:
#   The resistance (in ohms) of the resistor between IREF and GND. This
#   parameter must be provided.
#stealthchop_threshold: 0
#   The velocity (in mm/s) to set the "stealthChop" threshold to. When
#   set, "stealthChop" mode will be enabled if the stepper motor
#   velocity is below this value. Note that the "sensorless homing"
#   code may temporarily override this setting during homing
#   operations. The default is 0, which disables "stealthChop" mode.
#coolstep_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "CoolStep"
#   threshold to. If set, the coolstep feature will be enabled when
#   the stepper motor velocity is near or above this value. Important
#   - if coolstep_threshold is set and "sensorless homing" is used,
#   then one must ensure that the homing speed is above the coolstep
#   threshold! The default is to not enable the coolstep feature.
#high_velocity_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "high
#   velocity" threshold (THIGH) to. This is typically used to disable
#   the "CoolStep" feature at high speeds. The default is to not set a
#   TMC "high velocity" threshold.
#current_range:
#   The current_range bit value for the driver. Valid values are 0-3.
#   The defaul is to auto-calculate to match the requested run_current.
#   For further information consult the tmc2240 datasheet and tuning table.
#driver_CS:
#   The current scale value for the TMC driver.
#   The ideal `driver_CS` value may be found by setting the `CS` value in the
#   TMC calculations spreadsheet (https://www.analog.com/media/en/engineering-tools/design-tools/tmc5240_tmc2240_tmc2210_calculations.xlsx),
#   under the chopper tab so the hysteresis is not marked as too high.
#   While it's not necessary to change the CS value, it can be helpful to achieve
#   adequate hysteresis values on low current steppers.
#   By default, this value is autocalculated.
#   If driver_CS is specified this value will be used for homing so make sure it is possible to achieve your homing_current
#   with the given currentscaler value.
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
#   These fields control the Microstep Table registers directly. The optimal
#   wave table is specific to each motor and might vary with current. An
#   optimal configuration will have minimal print artifacts caused by
#   non-linear stepper movement. The values specified above are the default
#   values used by the driver. The value must be specified as a decimal integer
#   (hex form is not supported). In order to compute the wave table fields,
#   see the tmc2130 "Calculation Sheet" from the Trinamic website.
#   Additionally, this driver also has the OFFSET_SIN90 field which can be used
#   to tune a motor with unbalanced coils. See the `Sine Wave Lookup Table`
#   section in the datasheet for information about this field and how to tune
#   it.
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
#   Controls the slew rate of the gate driver output. The chip default is 0,
#   corresponding to 100V/µs. Setting to 2 (400V/µs) or 3 (570V/µs) can
#   significantly reduce driver temperature (users report ~15-20°C reduction
#   at 50kHz chopper frequency). A value of 2 matches TMC2209 slew rate.
#   Higher values may increase EMI. See TMC2240 datasheet for details.
#driver_SGT: 0
#driver_SEMIN: 0
#driver_SEUP: 0
#driver_SEMAX: 0
#driver_SEDN: 0
#driver_SEIMIN: 0
#driver_SFILT: 0
#driver_SG4_THRS: 0
#driver_SG4_ANGLE_OFFSET: 1
#   Set the given register during the configuration of the TMC2240
#   chip. This may be used to set custom motor parameters. The
#   defaults for each parameter are next to the parameter name in the
#   above list.
#diag0_pin:
#diag1_pin:
#   The micro-controller pin attached to one of the DIAG lines of the
#   TMC2240 chip. Only a single diag pin should be specified. The pin
#   is "active low" and is thus normally prefaced with "^!". Setting
#   this creates a "tmc2240_stepper_x:virtual_endstop" virtual pin
#   which may be used as the stepper's endstop_pin. Doing this enables
#   "sensorless homing". (Be sure to also set driver_SGT OR driver_SG4_THRS
#   to an appropriate sensitivity value.) The default is to not enable
#   sensorless homing.
```

### [tmc5160]

通过 SPI 总线配置 TMC5160 或 TMC2160 步进电机驱动器。要使用此功能，请定义一个以 "tmc5160" 为前缀后跟相应步进电机配置部分名称的配置部分（例如 "[tmc5160 stepper_x]"）。

```
[tmc5160 stepper_x]
cs_pin:
#   The pin corresponding to the TMC5160 or TMC2160 chip select line.
#   This pin will be set to low at the start of SPI messages and raised
#   to high after the message completes. This parameter must be provided.
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#chain_position:
#chain_length:
#   These parameters configure an SPI daisy chain. The two parameters
#   define the stepper position in the chain and the total chain length.
#   Position 1 corresponds to the stepper that connects to the MOSI signal.
#   The default is to not use an SPI daisy chain.
#interpolate: True
#   If true, enable step interpolation (the driver will internally
#   step at a rate of 256 micro-steps). The default is True.
run_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during stepper movement. This parameter must be provided.
#hold_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   when the stepper is not moving. Setting a hold_current is not
#   recommended (see TMC_Drivers.md for details). The default is to
#   not reduce the current.
#home_current:
#   The amount of current (in amps RMS) to configure the driver to use
#   during homing procedures. The default is to not reduce the current.
#current_change_dwell_time:
#   The amount of time (in seconds) to wait after changing homing current.
#   The default is 0.5 seconds.
sense_resistor:
#   The resistance (in ohms) of the driver sense resistor. This parameter
#   must be provided. Common values are 0.110 ohms for most TMC2209 drivers
#   and 0.075 ohms for TMC5160 drivers. Check your stepper driver documentation
#   or board schematic to confirm the correct value.
#stealthchop_threshold: 0
#   The velocity (in mm/s) to set the "stealthChop" threshold to. When
#   set, "stealthChop" mode will be enabled if the stepper motor
#   velocity is below this value. Note that the "sensorless homing"
#   code may temporarily override this setting during homing
#   operations. The default is 0, which disables "stealthChop" mode.
#coolstep_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "CoolStep"
#   threshold to. If set, the coolstep feature will be enabled when
#   the stepper motor velocity is near or above this value. Important
#   - if coolstep_threshold is set and "sensorless homing" is used,
#   then one must ensure that the homing speed is above the coolstep
#   threshold! The default is to not enable the coolstep feature.
#high_velocity_threshold:
#   The velocity (in mm/s) to set the TMC driver internal "high
#   velocity" threshold (THIGH) to. This is typically used to disable
#   the "CoolStep" feature at high speeds. The default is to not set a
#   TMC "high velocity" threshold.
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
#   These fields control the Microstep Table registers directly. The optimal
#   wave table is specific to each motor and might vary with current. An
#   optimal configuration will have minimal print artifacts caused by
#   non-linear stepper movement. The values specified above are the default
#   values used by the driver. The value must be specified as a decimal integer
#   (hex form is not supported). In order to compute the wave table fields,
#   see the tmc2130 "Calculation Sheet" from the Trinamic website.
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
#   The current scale value for the TMC driver.
#   The ideal `driver_CS` value may be found by setting the `CS` value in the
#   TMC calculations spreadsheet (https://www.analog.com/media/en/engineering-tools/design-tools/tmc5160_calculations.xlsx),
#   under the chopper tab so the hysteresis is not marked as too high.
#   While it's not necessary to change the CS value, it can be helpful to achieve
#   adequate hysteresis values on low current steppers.
#   By default, this value is autocalculated.
#   If driver_CS is specified this value will be used for homing so make sure it is possible to achieve your homing_current
#   with the given currentscaler value.
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
#   Set the given register during the configuration of the TMC5160 or
#   TMC2160 chip. This may be used to set custom motor parameters. The
#   defaults for each parameter are next to the parameter name in the
#   above list.
#⚠️driver_s2vs_level: 6   # Short to Supply tolerance, from 4 to 15
#⚠️driver_s2g_level: 6    # Short to Ground tolerance, from 2 to 15
#⚠️driver_shortdelay: 0   # Short trigger delay, 0=750ns, 1=1500ns
#⚠️driver_short_filter: 1
#   Short filtering bandwidth. 0=100ns, 1=1us (Default), 2=2us, 3=3us
#diag0_pin:
#diag1_pin:
#   The micro-controller pin attached to one of the DIAG lines of the
#   TMC5160 or TMC2160 chip. Only a single diag pin should be specified.
#   The pin is "active low" and is thus normally prefaced with "^!".
#   Setting this creates a "tmc5160_stepper_x:virtual_endstop" virtual pin
#   which may be used as the stepper's endstop_pin. Doing this enables
#   "sensorless homing". (Be sure to also set driver_SGT to an
#   appropriate sensitivity value.) The default is to not enable
#   sensorless homing.
```

## LYX 步进驱动配置

通过软件位翻转（bit-bang）的 Modbus RTU 总线配置 LYX9231 闭环步进
电机驱动器。更多信息请参阅 [LYX 驱动指南](LYX_Drivers.md)。

### [lyx9231]

通过单个 GPIO 引脚上的软件位翻转 Modbus RTU 总线配置 LYX9231 闭环
步进电机驱动器。使用时，定义一个以 "lyx9231" 为前缀、后跟对应步进
配置段名称的配置段（例如 "[lyx9231 stepper_x]"）。固件必须编译时启用
"Support software Modbus RTU UART communication" 选项。

电机的 STEP/DIR 控制由常规的 [stepper] 配置段处理；本配置段仅用于
配置驱动器寄存器。

```
[lyx9231 stepper_x]
uart_pin:
#  用于单线 Modbus RTU 总线的 GPIO 引脚。必填。
uart_address: 1
#  该驱动器的 Modbus 从站地址。在共享同一 uart_pin 的驱动中必须
#  唯一。默认 1。
#sense_resistor: 0.050
#  用于将寄存器值换算为电流的采样电阻值（欧姆）。默认 0.050。
#run_current: 1.4
#  驱动器运行电流（安培）。默认 1.4。
#hold_current:
#  驱动器保持电流（安培）。未指定时默认为运行电流的一半。
#microstep: 16
#  微步细分（1-256）。默认 16。
#driver_motor_type: 1
#  电机相型：1 为 1.8 度，0 为 0.9 度。默认 1。
#driver_op_mode: 2
#  控制模式。0=开环，1=普通闭环，2=超级闭环，3=伺服闭环，
#  4=力矩模式。默认 2。
#driver_run_current: 896
#  运行电流寄存器的原始值。通常由 run_current 自动计算。默认 896。
#driver_half_cur_en: 0
#  启用半电流功能（1=开，0=关）。默认 0。
#driver_half_cur_time: 3000
#  施加半电流之前的延时（毫秒）。默认 3000。
#driver_half_cur_ratio: 64
#  半电流比例寄存器值（0-128）。64 对应运行电流的一半。默认 64。
#driver_boost_level: 1
#  额外力矩的 boost 档位。默认 1。
#driver_noise_en: 0
#  启用降噪功能（1=开，0=关）。默认 0。
```

## 运行时步进电机电流配置

### [ad5206]

通过 SPI 总线连接的静态配置 AD5206 数字电位器（可以定义任意数量的 "ad5206" 前缀部分）。

```
[ad5206 my_digipot]
enable_pin:
#   The pin corresponding to the AD5206 chip select line. This pin
#   will be set to low at the start of SPI messages and raised to high
#   after the message completes. This parameter must be provided.
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
#channel_1:
#channel_2:
#channel_3:
#channel_4:
#channel_5:
#channel_6:
#   The value to statically set the given AD5206 channel to. This is
#   typically set to a number between 0.0 and 1.0 with 1.0 being the
#   highest resistance and 0.0 being the lowest resistance. However,
#   the range may be changed with the 'scale' parameter (see below).
#   If a channel is not specified then it is left unconfigured.
#scale:
#   This parameter can be used to alter how the 'channel_x' parameters
#   are interpreted. If provided, then the 'channel_x' parameters
#   should be between 0.0 and 'scale'. This may be useful when the
#   AD5206 is used to set stepper voltage references. The 'scale' can
#   be set to the equivalent stepper amperage if the AD5206 were at
#   its highest resistance, and then the 'channel_x' parameters can be
#   specified using the desired amperage value for the stepper. The
#   default is to not scale the 'channel_x' parameters.
```

### [mcp4451]

通过 I2C 总线连接的静态配置 MCP4451 数字电位器（可以定义任意数量的 "mcp4451" 前缀部分）。

```
[mcp4451 my_digipot]
i2c_address:
#   The i2c address that the chip is using on the i2c bus. This
#   parameter must be provided.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#wiper_0:
#wiper_1:
#wiper_2:
#wiper_3:
#   The value to statically set the given MCP4451 "wiper" to. This is
#   typically set to a number between 0.0 and 1.0 with 1.0 being the
#   highest resistance and 0.0 being the lowest resistance. However,
#   the range may be changed with the 'scale' parameter (see below).
#   If a wiper is not specified then it is left unconfigured.
#scale:
#   This parameter can be used to alter how the 'wiper_x' parameters
#   are interpreted. If provided, then the 'wiper_x' parameters should
#   be between 0.0 and 'scale'. This may be useful when the MCP4451 is
#   used to set stepper voltage references. The 'scale' can be set to
#   the equivalent stepper amperage if the MCP4451 were at its highest
#   resistance, and then the 'wiper_x' parameters can be specified
#   using the desired amperage value for the stepper. The default is
#   to not scale the 'wiper_x' parameters.
```

### [mcp4728]

通过 I2C 总线连接的静态配置 MCP4728 数模转换器（可以定义任意数量的 "mcp4728" 前缀部分）。

```
[mcp4728 my_dac]
#i2c_address: 96
#   The i2c address that the chip is using on the i2c bus. The default
#   is 96.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
#channel_a:
#channel_b:
#channel_c:
#channel_d:
#   The value to statically set the given MCP4728 channel to. This is
#   typically set to a number between 0.0 and 1.0 with 1.0 being the
#   highest voltage (2.048V) and 0.0 being the lowest voltage.
#   However, the range may be changed with the 'scale' parameter (see
#   below). If a channel is not specified then it is left
#   unconfigured.
#scale:
#   This parameter can be used to alter how the 'channel_x' parameters
#   are interpreted. If provided, then the 'channel_x' parameters
#   should be between 0.0 and 'scale'. This may be useful when the
#   MCP4728 is used to set stepper voltage references. The 'scale' can
#   be set to the equivalent stepper amperage if the MCP4728 were at
#   its highest voltage (2.048V), and then the 'channel_x' parameters
#   can be specified using the desired amperage value for the
#   stepper. The default is to not scale the 'channel_x' parameters.
```

### [mcp4018]

通过 i2c 连接的静态配置 MCP4018 数字电位器（可以定义任意数量的 "mcp4018" 前缀部分）。

```
[mcp4018 my_digipot]
#i2c_address: 47
#   The i2c address that the chip is using on the i2c bus. The default
#   is 47.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
wiper:
#   The value to statically set the given MCP4018 "wiper" to. This is
#   typically set to a number between 0.0 and 1.0 with 1.0 being the
#   highest resistance and 0.0 being the lowest resistance. However,
#   the range may be changed with the 'scale' parameter (see below).
#   This parameter must be provided.
#scale:
#   This parameter can be used to alter how the 'wiper' parameter is
#   interpreted. If provided, then the 'wiper' parameter should be
#   between 0.0 and 'scale'. This may be useful when the MCP4018 is
#   used to set stepper voltage references. The 'scale' can be set to
#   the equivalent stepper amperage if the MCP4018 is at its highest
#   resistance, and then the 'wiper' parameter can be specified using
#   the desired amperage value for the stepper. The default is to not
#   scale the 'wiper' parameter.
```

## 显示屏支持

### [display]

连接到微控制器的显示屏支持。

```
[display]
lcd_type:
#   The type of LCD chip in use. This may be "hd44780", "hd44780_spi",
#   "aip31068_spi", "st7920", "emulated_st7920", "uc1701", "ssd1306", or
#   "sh1106".
#   See the display sections below for information on each type and
#   additional parameters they provide. This parameter must be
#   provided.
#display_group:
#   The name of the display_data group to show on the display. This
#   controls the content of the screen (see the "display_data" section
#   for more information). The default is _default_20x4 for hd44780 or
#   aip31068_spi displays and _default_16x4 for other displays.
#menu_timeout:
#   Timeout for menu. Being inactive this amount of seconds will
#   trigger menu exit or return to root menu when having autorun
#   enabled. The default is 0 seconds (disabled)
#menu_root:
#   Name of the main menu section to show when clicking the encoder
#   on the home screen. The defaults is __main, and this shows the
#   the default menus as defined in klippy/extras/display/menu.cfg
#menu_reverse_navigation:
#   When enabled it will reverse up and down directions for list
#   navigation. The default is False. This parameter is optional.
#encoder_pins:
#   The pins connected to encoder. 2 pins must be provided when using
#   encoder. This parameter must be provided when using menu.
#encoder_steps_per_detent:
#   How many steps the encoder emits per detent ("click"). If the
#   encoder takes two detents to move between entries or moves two
#   entries from one detent, try changing this. Allowed values are 2
#   (half-stepping) or 4 (full-stepping). The default is 4.
#click_pin:
#   The pin connected to 'enter' button or encoder 'click'. This
#   parameter must be provided when using menu. The presence of an
#   'analog_range_click_pin' config parameter turns this parameter
#   from digital to analog.
#back_pin:
#   The pin connected to 'back' button. This parameter is optional,
#   menu can be used without it. The presence of an
#   'analog_range_back_pin' config parameter turns this parameter from
#   digital to analog.
#up_pin:
#   The pin connected to 'up' button. This parameter must be provided
#   when using menu without encoder. The presence of an
#   'analog_range_up_pin' config parameter turns this parameter from
#   digital to analog.
#down_pin:
#   The pin connected to 'down' button. This parameter must be
#   provided when using menu without encoder. The presence of an
#   'analog_range_down_pin' config parameter turns this parameter from
#   digital to analog.
#kill_pin:
#   The pin connected to 'kill' button. This button will call
#   emergency stop. The presence of an 'analog_range_kill_pin' config
#   parameter turns this parameter from digital to analog.
#analog_pullup_resistor: 4700
#   The resistance (in ohms) of the pullup attached to the analog
#   button. The default is 4700 ohms.
#analog_range_click_pin:
#   The resistance range for a 'enter' button. Range minimum and
#   maximum comma-separated values must be provided when using analog
#   button.
#analog_range_back_pin:
#   The resistance range for a 'back' button. Range minimum and
#   maximum comma-separated values must be provided when using analog
#   button.
#analog_range_up_pin:
#   The resistance range for a 'up' button. Range minimum and maximum
#   comma-separated values must be provided when using analog button.
#analog_range_down_pin:
#   The resistance range for a 'down' button. Range minimum and
#   maximum comma-separated values must be provided when using analog
#   button.
#analog_range_kill_pin:
#   The resistance range for a 'kill' button. Range minimum and
#   maximum comma-separated values must be provided when using analog
#   button.
```

#### hd44780 显示屏

配置 hd44780 显示屏的信息（用于 "RepRapDiscount 2004 Smart Controller" 类型的显示屏）。

```
[display]
lcd_type: hd44780
#   Set to "hd44780" for hd44780 displays.
rs_pin:
e_pin:
d4_pin:
d5_pin:
d6_pin:
d7_pin:
#   The pins connected to an hd44780 type lcd. These parameters must
#   be provided.
#hd44780_protocol_init: True
#   Perform 8-bit/4-bit protocol initialization on an hd44780 display.
#   This is necessary on real hd44780 devices. However, one may need
#   to disable this on some "clone" devices. The default is True.
#line_length:
#   Set the number of characters per line for an hd44780 type lcd.
#   Possible values are 20 (default) and 16. The number of lines is
#   fixed to 4.
...
```

#### hd44780_spi 显示屏

配置 hd44780_spi 显示屏的信息 - 通过硬件 "移位寄存器" 控制的 20x04 显示屏（用于基于 mightyboard 的打印机）。

```
[display]
lcd_type: hd44780_spi
#   Set to "hd44780_spi" for hd44780_spi displays.
latch_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   The pins connected to the shift register controlling the display.
#   The spi_software_miso_pin needs to be set to an unused pin of the
#   printer mainboard as the shift register does not have a MISO pin,
#   but the software spi implementation requires this pin to be
#   configured.
#hd44780_protocol_init: True
#   Perform 8-bit/4-bit protocol initialization on an hd44780 display.
#   This is necessary on real hd44780 devices. However, one may need
#   to disable this on some "clone" devices. The default is True.
#line_length:
#   Set the number of characters per line for an hd44780 type lcd.
#   Possible values are 20 (default) and 16. The number of lines is
#   fixed to 4.
...
```

#### aip31068_spi 显示屏

配置 aip31068_spi 显示屏的信息 - 与 hd44780_spi 非常相似的 20x04（20 个符号 x 4 行）显示屏，具有稍微不同的内部协议。

```
[display]
lcd_type: aip31068_spi
latch_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   The pins connected to the shift register controlling the display.
#   The spi_software_miso_pin needs to be set to an unused pin of the
#   printer mainboard as the shift register does not have a MISO pin,
#   but the software spi implementation requires this pin to be
#   configured.
#line_length:
#   Set the number of characters per line for an hd44780 type lcd.
#   Possible values are 20 (default) and 16. The number of lines is
#   fixed to 4.
...
```

#### st7920 显示屏

配置 st7920 显示屏的信息（用于 "RepRapDiscount 12864 Full Graphic Smart Controller" 类型的显示屏）。

```
[display]
lcd_type: st7920
#   Set to "st7920" for st7920 displays.
cs_pin:
sclk_pin:
sid_pin:
#   The pins connected to an st7920 type lcd. These parameters must be
#   provided.
...
```

#### emulated_st7920 显示屏

配置模拟 st7920 显示屏的信息 - 在某些 "2.4 英寸触摸屏设备" 等中找到。

```
[display]
lcd_type: emulated_st7920
#   Set to "emulated_st7920" for emulated_st7920 displays.
en_pin:
spi_software_sclk_pin:
spi_software_mosi_pin:
spi_software_miso_pin:
#   The pins connected to an emulated_st7920 type lcd. The en_pin
#   corresponds to the cs_pin of the st7920 type lcd,
#   spi_software_sclk_pin corresponds to sclk_pin and
#   spi_software_mosi_pin corresponds to sid_pin. The
#   spi_software_miso_pin needs to be set to an unused pin of the
#   printer mainboard as the st7920 as no MISO pin but the software
#   spi implementation requires this pin to be configured.
...
```

#### uc1701 显示屏

配置 uc1701 显示屏的信息（用于 "MKS Mini 12864" 类型的显示屏）。

```
[display]
lcd_type: uc1701
#   Set to "uc1701" for uc1701 displays.
cs_pin:
a0_pin:
#   The pins connected to a uc1701 type lcd. These parameters must be
#   provided.
#rst_pin:
#   The pin connected to the "rst" pin on the lcd. If it is not
#   specified then the hardware must have a pull-up on the
#   corresponding lcd line.
#contrast:
#   The contrast to set. The value may range from 0 to 63 and the
#   default is 40.
...
```

#### ssd1306 和 sh1106 显示屏

配置 ssd1306 和 sh1106 显示屏的信息。

```
[display]
lcd_type:
#   Set to either "ssd1306" or "sh1106" for the given display type.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   Optional parameters available for displays connected via an i2c
#   bus. See the "common I2C settings" section for a description of
#   the above parameters.
#cs_pin:
#dc_pin:
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   The pins connected to the lcd when in "4-wire" spi mode. See the
#   "common SPI settings" section for a description of the parameters
#   that start with "spi_". The default is to use i2c mode for the
#   display.
#reset_pin:
#   A reset pin may be specified on the display. If it is not
#   specified then the hardware must have a pull-up on the
#   corresponding lcd line.
#contrast:
#   The contrast to set. The value may range from 0 to 256 and the
#   default is 239.
#vcomh: 0
#   Set the Vcomh value on the display. This value is associated with
#   a "smearing" effect on some OLED displays. The value may range
#   from 0 to 63. Default is 0.
#invert: False
#   TRUE inverts the pixels on certain OLED displays.  The default is
#   False.
#x_offset: 0
#   Set the horizontal offset value on SH1106 displays. The default is
#   0.
...
```

### [display_data]

在 LCD 屏幕上显示自定义数据的支持。您可以创建任意数量的显示组和这些组下的任意数量的数据项。如果 [display] 部分中的 display_group 选项设置为给定的组名，显示屏将显示该给定组的所有数据项。

自动创建[默认显示组集](../klippy/extras/display/display.cfg)。您可以通过在主 printer.cfg 配置文件中覆盖默认值来替换或扩展这些 display_data 项。

```
[display_data my_group_name my_data_name]
position:
#   Comma separated row and column of the display position that should
#   be used to display the information. This parameter must be
#   provided.
text:
#   The text to show at the given position. This field is evaluated
#   using command templates (see docs/Command_Templates.md). This
#   parameter must be provided.
```

### [display_template]

显示数据文本 "宏"（可以定义任意数量的 display_template 前缀部分）。有关模板评估的信息，请参见[命令模板](Command_Templates.md)文档。

此功能允许您减少 display_data 部分中的重复定义。您可以在 display_data 部分中使用内置的 `render()` 函数来评估模板。例如，如果您定义了 `[display_template my_template]`，则可以在 display_data 部分中使用 `{ render('my_template') }`。

此功能也可用于使用 [SET_LED_TEMPLATE](G-Codes.md#set_led_template) 命令进行连续 LED 更新。

```
[display_template my_template_name]
#param_<name>:
#   One may specify any number of options with a "param_" prefix. The
#   given name will be assigned the given value (parsed as a Python
#   literal) and will be available during macro expansion. If the
#   parameter is passed in the call to render() then that value will
#   be used during macro expansion. For example, a config with
#   "param_speed = 75" might have a caller with
#   "render('my_template_name', param_speed=80)". Parameter names may
#   not use upper case characters.
text:
#   The text to return when the this template is rendered. This field
#   is evaluated using command templates (see
#   docs/Command_Templates.md). This parameter must be provided.
```

### [display_glyph]

在支持的显示屏上显示自定义字形。给定的名称将被分配给给定的显示数据，然后可以在显示模板中通过其名称（由两个 "波浪号" 符号包围）引用，即 `~my_display_glyph~`

有关一些示例，请参见 [sample-glyphs.cfg](../config/sample-glyphs.cfg)。

```
[display_glyph my_display_glyph]
#data:
#   The display data, stored as 16 lines consisting of 16 bits (1 per
#   pixel) where '.' is a blank pixel and '*' is an on pixel (e.g.,
#   "****************" to display a solid horizontal line).
#   Alternatively, one can use '0' for a blank pixel and '1' for an on
#   pixel. Put each display line into a separate config line. The
#   glyph must consist of exactly 16 lines with 16 bits each. This
#   parameter is optional.
#hd44780_data:
#   Glyph to use on 20x4 hd44780 displays. The glyph must consist of
#   exactly 8 lines with 5 bits each. This parameter is optional.
#hd44780_slot:
#   The hd44780 hardware index (0..7) to store the glyph at. If
#   multiple distinct images use the same slot then make sure to only
#   use one of those images in any given screen. This parameter is
#   required if hd44780_data is specified.
```

### [display my_extra_display]

如果在 printer.cfg 中定义了主 [display] 部分（如上所示），则可以定义多个辅助显示屏。请注意，辅助显示屏目前不支持菜单功能，因此它们不支持 "menu" 选项或按钮配置。

```
[display my_extra_display]
# See the "display" section for available parameters.
```

### ⚠️ [menu]

自定义 LCD 显示菜单。

自动创建[默认菜单集](../klippy/extras/display/menu.cfg)。您可以通过在主 printer.cfg 配置文件中覆盖默认值来替换或扩展菜单。

有关模板渲染期间可用菜单属性的信息，请参见[命令模板文档](Command_Templates.md#menu-templates)。

```
# Common parameters available for all menu config sections.
#[menu __some_list __some_name]
#type: disabled
#   Permanently disabled menu element, only required attribute is 'type'.
#   Allows you to easily disable/hide existing menu items.

#[menu some_name]
#type:
#   One of command, input, list, text:
#       command      - basic menu element with various script triggers
#       input        - same like 'command' but has value changing capabilities.
#                      Press will start/stop edit mode.
#       list         - it allows for menu items to be grouped together in a
#                      scrollable list.  Add to the list by creating menu
#                      configurations using "some_list" as a prefix - for
#                      example: [menu some_list some_item_in_the_list]
#       vsdlist      - same as 'list' but will append files from virtual sdcard
#                      (deprecated, will be removed in the future)
#    ⚠️ file_browser - Extended SD Card browser, supporting directories and
#                      sorting. (replaces vsdlist)
#    ⚠️ dialog       - Menu Dialogs, a list of inputs with a final choice to
#                      confirm or cancel. Used for more complex scenarios like
#                      PID/MPC calibration where you may want to set multiple
#                      values for a single command
#name:
#   Name of menu item - evaluated as a template.
#enable:
#   Template that evaluates to True or False.
#index:
#   Position where an item needs to be inserted in list. By default
#   the item is added at the end.

#[menu some_list]
#type: list
#name:
#enable:
#   See above for a description of these parameters.

#[menu sdcard]
#type: file_browser
#name:
#sort_by:
#   `last_modified` (default) or `name`
#enable:
#   See above for a description of these parameters.

#[menu some_list some_command]
#type: command
#name:
#enable:
#   See above for a description of these parameters.
#gcode:
#   Script to run on button click or long click. Evaluated as a
#   template.

#[menu some_list some_input]
#type: input
#name:
#enable:
#   See above for a description of these parameters.
#input:
#   Initial value to use when editing - evaluated as a template.
#   Result must be float.
#input_min:
#   Minimum value of range - evaluated as a template. Default -99999.
#input_max:
#   Maximum value of range - evaluated as a template. Default 99999.
#input_step:
#   Editing step - Must be a positive integer or float value. It has
#   internal fast rate step. When "(input_max - input_min) /
#   input_step > 100" then fast rate step is 10 * input_step else fast
#   rate step is same input_step.
#realtime:
#   This attribute accepts static boolean value. When enabled then
#   gcode script is run after each value change. The default is False.
#gcode:
#   Script to run on button click, long click or value change.
#   Evaluated as a template. The button click will trigger the edit
#   mode start or end.

#[menu neopixel]
#type: dialog
#name:
#enable:
#   See above for a description of these parameters.
#title:
#   An optional title to display at the top of the dialog. `name` will
#   used if not set
#confirm_text:
#cancel_text
#   Templates for the confirmation and cancel options
#gcode:
#   G-Code to run on confirmation. The dialog will be closed on
#   confirmation. `{menu.exit()}` may be used to close the menu
#   instead.
```

## 耗材传感器

### [filament_switch_sensor]

长丝开关传感器。支持使用开关传感器（例如限位开关）进行长丝插入和耗尽检测。

有关更多信息，请参见[命令参考](G-Codes.md#filament_switch_sensor)。

```
[filament_switch_sensor my_sensor]
#pause_on_runout: True
#   When set to True, a PAUSE will execute immediately after a runout
#   is detected. Note that if pause_on_runout is False and the
#   runout_gcode is omitted then runout detection is disabled. Default
#   is True.
#runout_gcode:
#   A list of G-Code commands to execute after a filament runout is
#   detected. See docs/Command_Templates.md for G-Code format. If
#   pause_on_runout is set to True this G-Code will run after the
#   PAUSE is complete. The default is not to run any G-Code commands.
#immediate_runout_gcode:
#   A list of G-Code commands to execute immediately after a filament
#   runout is detected and runout_distance is greater than 0.
#   See docs/Command_Templates.md for G-Code format.
#insert_gcode:
#   A list of G-Code commands to execute after a filament insert is
#   detected. See docs/Command_Templates.md for G-Code format. The
#   default is not to run any G-Code commands, which disables insert
#   detection.
#runout_distance: 0.0
#   Defines how much filament can still be pulled after the
#   switch sensor triggered (e.g. you have a 60cm reverse bowden between your
#   extruder and your sensor, you would then set runout_distance to something
#   like 590 to leave a small safety margin and now the print will not
#   immediately pause when the sensor triggers but rather keep printing until
#   the filament is at the extruder). The default is 0 millimeters.
#event_delay: 3.0
#   The minimum amount of time in seconds to delay between events.
#   Events triggered during this time period will be silently
#   ignored. The default is 3 seconds.
#pause_delay: 0.5
#   The amount of time to delay, in seconds, between the pause command
#   dispatch and execution of the runout_gcode. It may be useful to
#   increase this delay if OctoPrint exhibits strange pause behavior.
#   Default is 0.5 seconds.
#debounce_delay:
#   A period of time in seconds to debounce events prior to running the
#   switch gcode. The switch must he held in a single state for at least
#   this long to activate. If the switch is toggled on/off during this delay,
#   the event is ignored. Default is 0.
#switch_pin:
#   The pin on which the switch is connected. This parameter must be
#   provided.
#smart:
#   If set to true the sensor will use the virtual_sd_card module to determine
#   whether the printer is printing which is more reliable but will not work
#   when streaming a print over usb or similar.
#always_fire_events:
#   If set to true, runout events will always fire no matter whether the sensor
#   is enabled or disabled. Usefull for MMUs
#check_on_print_start:
#   If set to true, the sensor will be reevaluated when a print starts and if
#   no filament is detected the runout_gcode will be run no matter the defined
#   runout_distance(immediate_runout_gcode will not be run in this case)
```

### [filament_motion_sensor]

Filament Motion Sensor. Support for filament insert and runout
使用在长丝通过传感器移动期间切换输出引脚的编码器进行检测。

有关更多信息，请参见[命令参考](G-Codes.md#filament_switch_sensor)。

```
[filament_motion_sensor my_sensor]
detection_length: 7.0
#   The minimum length of filament pulled through the sensor to trigger
#   a state change on the switch_pin
#   Default is 7 mm.
extruder:
#   The name of the extruder section this sensor is associated with.
#   This parameter must be provided.
switch_pin:
#pause_on_runout:
#runout_gcode:
#insert_gcode:
#event_delay:
#pause_delay:
#smart:
#always_fire_events:
#   See the "filament_switch_sensor" section for a description of the
#   above parameters.
```

### [tsl1401cl_filament_width_sensor]

基于 TSLl401CL 的长丝宽度传感器。有关更多信息，请参见[指南](TSL1401CL_Filament_Width_Sensor.md)。

```
[tsl1401cl_filament_width_sensor]
#pin:
#default_nominal_filament_diameter: 1.75 # (mm)
#   Maximum allowed filament diameter difference as mm.
#max_difference: 0.2
#   The distance from sensor to the melting chamber as mm.
#measurement_delay: 100
```

### [hall_filament_width_sensor]

霍尔长丝宽度传感器（参见 [Hall Filament Width Sensor](Hall_Filament_Width_Sensor.md)）。

```
[hall_filament_width_sensor]
adc1:
adc2:
#   Analog input pins connected to the sensor. These parameters must
#   be provided.
#cal_dia1: 1.50
#cal_dia2: 2.00
#   The calibration values (in mm) for the sensors. The default is
#   1.50 for cal_dia1 and 2.00 for cal_dia2.
#raw_dia1: 9500
#raw_dia2: 10500
#   The raw calibration values for the sensors. The default is 9500
#   for raw_dia1 and 10500 for raw_dia2.
#default_nominal_filament_diameter: 1.75
#   The nominal filament diameter. This parameter must be provided.
#max_difference: 0.200
#   Maximum allowed filament diameter difference in millimeters (mm).
#   If difference between nominal filament diameter and sensor output
#   is more than +- max_difference, extrusion multiplier is set back
#   to %100. The default is 0.200.
#measurement_delay: 70
#   The distance from sensor to the melting chamber/hot-end in
#   millimeters (mm). The filament between the sensor and the hot-end
#   will be treated as the default_nominal_filament_diameter. Host
#   module works with FIFO logic. It keeps each sensor value and
#   position in an array and POP them back in correct position. This
#   parameter must be provided.
#enable: False
#   Sensor enabled or disabled after power on. The default is to
#   disable.
#measurement_interval: 10
#   The approximate distance (in mm) between sensor readings. The
#   default is 10mm.
#logging: False
#   Out diameter to terminal and klippy.log can be turn on|of by
#   command.
#min_diameter: 1.0
#   Minimal diameter for trigger virtual filament_switch_sensor.
#max_diameter:
#   Maximum diameter for triggering virtual filament_switch_sensor.
#   The default is default_nominal_filament_diameter + max_difference.
#use_current_dia_while_delay: False
#   Use the current diameter instead of the nominal diameter while
#   the measurement delay has not run through.
#pause_on_runout:
#immediate_runout_gcode:
#runout_gcode:
#insert_gcode:
#event_delay:
#pause_delay:
#smart:
#always_fire_events:
#check_on_print_start:
#   See the "filament_switch_sensor" section for a description of the
#   above parameters.
```

### [belay]

Belay 挤出机同步传感器（可以定义任意数量的 "belay" 前缀部分）。

```
[belay my_belay]
extruder_type:
#   The type of secondary extruder. Available choices are 'trad_rack'
#   or 'extruder_stepper'. This parameter must be specified.
extruder_stepper_name:
#   The name of the extruder_stepper being used as the secondary
#   extruder. Must be specified if extruder_type is set to
#   'extruder_stepper', but should not be specified otherwise. For
#   example, if the config section for the secondary extruder is
#   [extruder_stepper my_extruder_stepper], this parameter's value
#   would be 'my_extruder_stepper'.
sensor_pin:
#   Input pin connected to the sensor. This parameter must be
#   provided.
#multiplier_high: 1.05
#   High multiplier to set for the secondary extruder when extruding
#   forward and Belay is compressed or when extruding backward and
#   Belay is expanded. The default is 1.05.
#multiplier_low: 0.95
#   Low multiplier to set for the secondary extruder when extruding
#   forward and Belay is expanded or when extruding backward and
#   Belay is compressed. The default is 0.95.
#debug_level: 0
#   Controls messages sent to the console. If set to 0, no messages
#   will be sent. If set to 1, multiplier resets will be reported, and
#   the multiplier will be reported whenever it is set in response to
#   a switch state change. If set to 2, the behavior is the same as 1
#   but with an additional message whenever the multiplier is set in
#   response to detecting an extrusion direction change. The default
#   is 0.
```
## 称重传感器
### [load_cell]
称重传感器。使用连接到称重传感器的 ADC 传感器创建数字秤。
```
[load_cell]
sensor_type:
#   This must be one of the supported sensor types, see below.
#counts_per_gram:
#   The floating point number of sensor counts that indicates 1 gram of force.
#   This value is calculated by the LOAD_CELL_CALIBRATE command.
#reference_tare_counts:
#   The integer tare value, in raw sensor counts, taken when LOAD_CELL_CALIBRATE
#   is run. This is the default tare value when klipper starts up.
#sensor_orientation:
#   Change the sensor's orientation. Can be either 'normal' or 'inverted'.
#   The default is 'normal'. Use 'inverted' if the sensor reports a
#   decreasing force value when placed under load.
```

#### HX711
这是一个使用 "bit-bang" 通信的 24 位低采样率芯片。适用于长丝秤。
```
[load_cell]
sensor_type: hx711
sclk_pin:
#   The pin connected to the HX711 clock line. This parameter must be provided.
dout_pin:
#   The pin connected to the HX711 data output line. This parameter must be
#   provided.
#gain: A-128
#   Valid values for gain are: A-128, A-64, B-32. The default is A-128.
#   'A' denotes the input channel and the number denotes the gain. Only the 3
#   listed combinations are supported by the chip. Note that changing the gain
#   setting also selects the channel being read.
#sample_rate: 80
#   Valid values for sample_rate are 80 or 10. The default value is 80.
#   This must match the wiring of the chip. The sample rate cannot be changed
#   in software.
```

#### HX717
这是 HX711 的 4 倍采样率版本，适用于探测。
```
[load_cell]
sensor_type: hx717
sclk_pin:
#   The pin connected to the HX717 clock line. This parameter must be provided.
dout_pin:
#   The pin connected to the HX717 data output line. This parameter must be
#   provided.
#gain: A-128
#   Valid values for gain are A-128, B-64, A-64, B-8.
#   'A' denotes the input channel and the number denotes the gain setting.
#   Only the 4 listed combinations are supported by the chip. Note that
#   changing the gain setting also selects the channel being read.
#sample_rate: 320
#   Valid values for sample_rate are: 10, 20, 80, 320. The default is 320.
#   This must match the wiring of the chip. The sample rate cannot be changed
#   in software.
```

#### ADS1220
ADS1220 是一个支持高达 2Khz 采样率的 24 位 ADC，可通过软件配置。
```
[load_cell]
sensor_type: ads1220
cs_pin:
#   The pin connected to the ADS1220 chip select line. This parameter must
#   be provided.
#spi_speed: 512000
#   This chip supports 2 speeds: 256000 or 512000. The faster speed is only
#   enabled when one of the Turbo sample rates is used. The correct spi_speed
#   is selected based on the sample rate.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
data_ready_pin:
#   Pin connected to the ADS1220 data ready line. This parameter must be
#   provided.
#gain: 128
#   Valid gain values are 128, 64, 32, 16, 8, 4, 2, 1
#   The default is 128
#pga_bypass: False
#   Disable the internal Programmable Gain Amplifier. If
#   True the PGA will be disabled for gains 1, 2, and 4. The PGA is always
#   enabled for gain settings 8 to 128, regardless of the pga_bypass setting.
#   If AVSS is used as an input pga_bypass is forced to True.
#   The default is False.
#sample_rate: 660
#   This chip supports two ranges of sample rates, Normal and Turbo. In turbo
#   mode the chip's internal clock runs twice as fast and the SPI communication
#   speed is also doubled.
#   Normal sample rates: 20, 45, 90, 175, 330, 600, 1000
#   Turbo sample rates: 40, 90, 180, 350, 660, 1200, 2000
#   The default is 660
#input_mux:
#   Input multiplexer configuration, select a pair of pins to use. The first pin
#   is the positive, AINP, and the second pin is the negative, AINN. Valid
#   values are: 'AIN0_AIN1', 'AIN0_AIN2', 'AIN0_AIN3', 'AIN1_AIN2', 'AIN1_AIN3',
#   'AIN2_AIN3', 'AIN1_AIN0', 'AIN3_AIN2', 'AIN0_AVSS', 'AIN1_AVSS', 'AIN2_AVSS'
#   and 'AIN3_AVSS'. If AVSS is used the PGA is bypassed and the pga_bypass
#   setting will be forced to True.
#   The default is AIN0_AIN1.
#vref:
#   The selected voltage reference. Valid values are: 'internal', 'REF0', 'REF1'
#   and 'analog_supply'. Default is 'internal'.
```

#### ADS131M02
ADS131M02 是一个 24 位、2 通道 delta-sigma ADC，具有同步采样功能。它使用 SPI 通信，提供适合称重传感器探测的高精度测量。
```
[load_cell]
sensor_type: ads131m02
cs_pin:
#   The pin connected to the ADS131M02 chip select line. This parameter must
#   be provided.
#spi_speed: 8192000
#   SPI bus speed. The default is 8.192 MHz.
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
data_ready_pin:
#   Pin connected to the ADS131M02 data ready (DRDY) line. This parameter must
#   be provided.
#gain: 128
#   Programmable gain amplifier setting. Valid values are 1, 2, 4, 8, 16, 32,
#   64, and 128. The default is 128.
#sample_rate: 500
#   Sample rate in samples per second. Valid values are 250, 500, 1000, 2000,
#   4000, 8000, 16000, and 32000. The default is 500.
#enable_global_chop: False
#   Enable the global chopper mode. This mode alternats the polarity of the inputs
#   for each samlple. This reduces noise but also reduces the effective 
#   sample rate to 1/3rd of its face value. Off by default.
#gloabl_chop_delay: 16
#   The delay, in clock cycles, between sample in global chop mode. This allows 
#   additional time for settling before sampling starts. The chip default is 16 
#   clock cycles. Values are powers of 2 from 2 to 65536. 
#channels: 0
#   Comma separated list of input channels to enable and sum. Valid channels are 0 and 1.
#   The default is 0.
```

#### ADS131M04
ADS131M04 是一个 24 位、4 通道 delta-sigma ADC，具有同步采样功能。它使用 SPI 通信，提供适合称重传感器探测的高精度测量。最多可以将 4 个通道组合成一个传感器，非常适合用于床下的称重传感器。
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
#   See the "ADS131M02" sections for details on these parameters.
#channels: 0
#   Comma separated list of input channels to enable and sum. Valid channels
#   are: 0, 1, 2, 3. The default is 0.
```


### [load_cell_probe]
称重传感器探针。这结合了 [probe] 和 [load_cell] 的功能。

另请参见 [simple_tap_classifier] 以获取点击验证配置。

```
[load_cell_probe]
sensor_type:
#   This must be one of the supported bulk ADC sensor types and support
#   load cell endstops on the mcu.
#counts_per_gram:
#reference_tare_counts:
#sensor_orientation:
#   These parameters must be configured before the probe will operate.
#   See the [load_cell] section for further details.
#force_safety_limit: 2000
#   The safe force limit for starting a probe. This is relative to the 
#   reference_tare_counts which is the sensor's absolute 0 force value.
#   Set to 0 to disable. The default is +/-2Kg.
#drift_safety_limit: 1000
#   The maximum absolute force change allowed while probing. Set to 0 to disable.
#   The default is +/-1Kg.
#trigger_force: 75.0
#   The force that the probe will trigger at. 75g is the default.
#drift_filter_cutoff_frequency: 0.8
#   Enable optional continuous taring while homing & probing to reject drift.
#   The value is a frequency, in Hz, below which drift will be ignored. This
#   option requires the SciPy library. Default: None
#drift_filter_delay: 2
#   The delay, or 'order', of the drift filter. This controls the number of
#   samples required to make a trigger detection. Can be 1 or 2, the default
#   is 2.
#buzz_filter_cutoff_frequency: 100.0
#   The value is a frequency, in Hz, above which high frequency noise in the
#   load cell will be filtered out. This option requires the SciPy
#   library. Default: None
#buzz_filter_delay: 2
#   The delay, or 'order', of the buzz filter. This controls the number of
#   samples required to make a trigger detection. Can be 1 or 2, the default
#   is 2.
#notch_filter_frequencies: 50, 60
#   1 or 2 frequencies, in Hz, to filter out of the load cell data. This is
#   intended to reject power line noise. This option requires the SciPy
#   library.  Default: None
#notch_filter_quality: 2.0
#   Controls how narrow the range of frequencies are that the notch filter
#   removes. Larger numbers produce a narrower filter. Minimum value is 0.5 and
#   maximum is 3.0. Default: 2.0
#tare_time:
#   The time in seconds used for taring the load_cell before each probe. The
#   default value is: 5 / 50 = 0.1. This collects samples from 5 cycles of
#   50Hz / 6 cycles of 60Hz mains power to cancel power line noise.
#disable_pullback_move: False
#   When True, disables the pullback move and tap analysis after probe trigger.
#   The probe will use the raw trigger position instead of the calculated Z=0
#   from tap analysis. This reduces probe accuracy but may be useful for
#   troubleshooting or compatibility testing. The default is False.
#pullback_distance: 0.2
#   The distance in mm to slowly raise the probe to perform precise Z=0
#   measurments. This move occurs immediately after the probe detects contact.
#   The distance needs to be approximatly 2x the distance required for the probe
#   to break contact with the bed. Valid range is 0.01 to 2.0 mm.
#   The default is 0.2 mm.
#pullback_speed:
#   The speed in mm/s for the pullback move after probe trigger. Valid range is
#   0.1 to 1.0 mm/s. The default is set to 1 micron (0.001mm) per sensor sample.
#tap_classifier_module:
#   Optional module for custom tap validation. The default is TapQualityClassifier.
#   Setting a custom classifier overrides TapQualityClassifier with your implementation.
#min_tap_quality: 40.0
#   The minimum acceptable tap quality score. Valid range is 0 to 100 percent.
#   The default is 40%.
#decompression_angle:
#   The average angle of the decompression line for clean taps. The further the
#   measured decompression angle is from this angle, the worse its tap quality score.
#   There is no default, this must be measured. It is a number in degrees
#   between 0 and 90.
#max_approach_force: 50
#max_departure_force: 25
#max_baseline_force_delta: 25
#max_dwell_force_drop: 75
#   Maximums for tap quality checks expressed as a percentage.
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
#   See the "[probe]" section for a description of the above parameters.
```

See [Tap Quality Components](Load_Cell.md#tap-quality-components) for more details on maximum for tap quality.

## 特定硬件支持

### [indx]

支持带有感应喷嘴加热器、非接触式 IR 温度传感器和板载 PID 控制器的 Bondtech INDX 工具板。工具板必须运行启用了 "Bondtech INDX Heater" 选项的 Kalico 固件。有关设置和校准说明，请参见 [INDX 文档](INDX.md)，有关可用命令，请参见 [G-Codes](G-Codes.md#indx)。

该模块为工具板引脚注册命名别名（例如 `<mcu>:motor_step`、`<mcu>:part_cooling`、`<mcu>:endstop`），将喷嘴加热器公开为虚拟引脚 `indx:heater`，将喷嘴温度公开为 `sensor_type: indx`，并自动管理散热风扇。在运行 INDX_CALIBRATE 之前，加热器不会加热。

```
[indx]
mcu:
#   The name of the mcu config section for the INDX toolboard (e.g.
#   "indxmcu" when the toolboard is defined as "[mcu indxmcu]"). This
#   parameter must be provided.
#part_cooling_fan: fan
#   Name of the part cooling fan object on the tool. The fan speed is
#   used by the thermal model to compensate for part cooling airflow.
#   Set to an empty string to disable.
#pid_kp: 4.0
#pid_ti: 0.0
#pid_td: 0.0
#pid_b: 1.0
#   Parameters for the PID controller running on the toolboard. The
#   defaults should work for most setups.
#max_temp_nozzle: 305.0
#max_temp_sensor: 130.0
#max_temp_bracket: 130.0
#max_temp_board: 100.0
#   Maximum allowed temperature for the nozzle, the IR sensor die,
#   the sensor bracket and the toolboard. Exceeding any of these
#   triggers a shutdown.
#max_model_error: 50.0
#   Maximum allowed difference (in Celsius) between the measured
#   nozzle temperature and the thermal model prediction before a
#   shutdown is triggered.
#coil_time_on:
#coil_time_off:
#coil_time_on_first:
#   Inductive coil drive timings in microseconds. These are measured
#   by INDX_CALIBRATE and stored by SAVE_CONFIG; they should not
#   normally be set by hand.
#max_power:
#model_max_power_temp_coeff:
#model_thermal_capacity:
#model_to_ambient_r:
#   Thermal model parameters. These are measured by INDX_CALIBRATE
#   and stored by SAVE_CONFIG; they should not normally be set by
#   hand.
#model_filament_diameter: 1.75
#model_filament_density: 1.20
#model_filament_heat_capacity: 1.8
#   Filament parameters used by the thermal model to account for the
#   energy carried away by extruded filament. The density is in
#   g/cm^3 and the heat capacity in J/(g*K). These can also be
#   measured with INDX_LOAD_FILAMENT or changed at runtime with
#   INDX_SET_MODEL_PARAMS.
#model_part_cooling_fan_a: 0.0
#model_part_cooling_fan_k: 0.0
#   Part cooling fan compensation for the thermal model, measured by
#   INDX_FAN_CALIBRATE and stored by SAVE_CONFIG.
#model_ambient_blend_board: 0.0
#model_ambient_blend_bracket: 1.0
#model_ambient_blend_sensor: 1.0
#   Relative weights of the toolboard, sensor bracket and IR sensor
#   die temperatures when estimating the ambient temperature for the
#   thermal model.
#model_error_application: 1.0
#   Fraction of the observed model error fed back into the thermal
#   model on each update.
#ir_sensor_exponent:
#ir_sensor_obj_gain:
#ir_sensor_bracket_gain:
#   Override the IR sensor tuning parameters stored in the sensor
#   EEPROM. All three must be provided if any is given. These should
#   not normally be set.
```

### [sx1509]

Configure an SX1509 I2C to GPIO expander. Due to the delay incurred by
I2C communication you should NOT use SX1509 pins as stepper enable,
step or dir pins or any other pin that requires fast bit-banging. They
are best used as static or gcode controlled digital outputs or
hardware-pwm pins for e.g. fans. One may define any number of sections
with an "sx1509" prefix. Each expander provides a set of 16 pins
(sx1509_my_sx1509:PIN_0 to sx1509_my_sx1509:PIN_15) which can be used
in the printer configuration.

See the [generic-duet2-duex.cfg](../config/generic-duet2-duex.cfg)
file for an example.

```
[sx1509 my_sx1509]
i2c_address:
#   I2C address used by this expander. Depending on the hardware
#   jumpers this is one out of the following addresses: 62 63 112
#   113. This parameter must be provided.
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   See the "common I2C settings" section for a description of the
#   above parameters.
```

### [samd_sercom]

SAMD SERCOM 配置，用于指定在给定的 SERCOM 上使用哪些引脚。您可以定义任意数量的 "samd_sercom" 前缀部分。每个 SERCOM 必须在将其用作 SPI 或 I2C 外设之前进行配置。将此配置部分放在任何使用 SPI 或 I2C 总线的其他部分之前。

```
[samd_sercom my_sercom]
sercom:
#   The name of the sercom bus to configure in the micro-controller.
#   Available names are "sercom0", "sercom1", etc.. This parameter
#   must be provided.
tx_pin:
#   MOSI pin for SPI communication, or SDA (data) pin for I2C
#   communication. The pin must have a valid pinmux configuration
#   for the given SERCOM peripheral. This parameter must be provided.
#rx_pin:
#   MISO pin for SPI communication. This pin is not used for I2C
#   communication (I2C uses tx_pin for both sending and receiving).
#   The pin must have a valid pinmux configuration for the given
#   SERCOM peripheral. This parameter is optional.
clk_pin:
#   CLK pin for SPI communication, or SCL (clock) pin for I2C
#   communication. The pin must have a valid pinmux configuration
#   for the given SERCOM peripheral. This parameter must be provided.
```

### [adc_scaled]

通过 vref 和 vssa 读数进行 Duet2 Maestro 模拟缩放。定义 adc_scaled 部分会启用虚拟 adc 引脚（例如 "my_name:PB0"），这些引脚会通过板的 vref 和 vssa 监控引脚自动调整。确保将此配置部分放在任何使用这些虚拟引脚的配置部分之上。

有关示例，请参见 [generic-duet2-maestro.cfg](../config/generic-duet2-maestro.cfg) 文件。

```
[adc_scaled my_name]
vref_pin:
#   The ADC pin to use for VREF monitoring. This parameter must be
#   provided.
vssa_pin:
#   The ADC pin to use for VSSA monitoring. This parameter must be
#   provided.
#smooth_time: 2.0
#   A time value (in seconds) over which the vref and vssa
#   measurements will be smoothed to reduce the impact of measurement
#   noise. The default is 2 seconds.
```

### [replicape]

Replicape 支持 - 有关示例，请参见 [beaglebone 指南](Beaglebone.md) 和 [generic-replicape.cfg](../config/generic-replicape.cfg) 文件。

```
# The "replicape" config section adds "replicape:stepper_x_enable"
# virtual stepper enable pins (for steppers X, Y, Z, E, and H) and
# "replicape:power_x" PWM output pins (for hotbed, e, h, fan0, fan1,
# fan2, and fan3) that may then be used elsewhere in the config file.
[replicape]
revision:
#   The replicape hardware revision. Currently only revision "B3" is
#   supported. This parameter must be provided.
#enable_pin: !gpio0_20
#   The replicape global enable pin. The default is !gpio0_20 (aka
#   P9_41).
host_mcu:
#   The name of the mcu config section that communicates with the
#   Kalico "linux process" mcu instance. This parameter must be
#   provided.
#standstill_power_down: False
#   This parameter controls the CFG6_ENN line on all stepper
#   motors. True sets the enable lines to "open". The default is
#   False.
#stepper_x_microstep_mode:
#stepper_y_microstep_mode:
#stepper_z_microstep_mode:
#stepper_e_microstep_mode:
#stepper_h_microstep_mode:
#   This parameter controls the CFG1 and CFG2 pins of the given
#   stepper motor driver. Available options are: disable, 1, 2,
#   spread2, 4, 16, spread4, spread16, stealth4, and stealth16. The
#   default is disable.
#stepper_x_current:
#stepper_y_current:
#stepper_z_current:
#stepper_e_current:
#stepper_h_current:
#   The configured maximum current (in Amps) of the stepper motor
#   driver. This parameter must be provided if the stepper is not in a
#   disable mode.
#stepper_x_chopper_off_time_high:
#stepper_y_chopper_off_time_high:
#stepper_z_chopper_off_time_high:
#stepper_e_chopper_off_time_high:
#stepper_h_chopper_off_time_high:
#   This parameter controls the CFG0 pin of the stepper motor driver
#   (True sets CFG0 high, False sets it low). The default is False.
#stepper_x_chopper_hysteresis_high:
#stepper_y_chopper_hysteresis_high:
#stepper_z_chopper_hysteresis_high:
#stepper_e_chopper_hysteresis_high:
#stepper_h_chopper_hysteresis_high:
#   This parameter controls the CFG4 pin of the stepper motor driver
#   (True sets CFG4 high, False sets it low). The default is False.
#stepper_x_chopper_blank_time_high:
#stepper_y_chopper_blank_time_high:
#stepper_z_chopper_blank_time_high:
#stepper_e_chopper_blank_time_high:
#stepper_h_chopper_blank_time_high:
#   This parameter controls the CFG5 pin of the stepper motor driver
#   (True sets CFG5 high, False sets it low). The default is True.
```

## 其他自定义模块

### [palette2]

Palette 2 多材料支持 - 提供更紧密的集成，支持在连接模式下运行的 Palette 2 设备。

此模块还需要 `[virtual_sdcard]` 和 `[pause_resume]` 才能实现完整功能。

如果您使用此模块，请不要使用 Octoprint 的 Palette 2 插件，因为它们会发生冲突，并且其中一个可能无法正确初始化，从而可能导致打印中止。

如果您使用 Octoprint 并通过串口流式传输 gcode，而不是从 virtual_sdcard 打印，则从 _设置 > 串口连接 > 固件和协议_ 中的 _暂停命令_ 中删除 **M1** 和 **M0** 将避免在 Palette 2 上启动打印并在 Octoprint 中取消暂停以开始打印的需要。

```
[palette2]
serial:
#   The serial port to connect to the Palette 2.
#baud: 115200
#   The baud rate to use. The default is 115200.
#feedrate_splice: 0.8
#   The feedrate to use when splicing, default is 0.8
#feedrate_normal: 1.0
#   The feedrate to use after splicing, default is 1.0
#auto_load_speed: 2
#   Extrude feedrate when autoloading, default is 2 (mm/s)
#auto_cancel_variation: 0.1
#   Auto cancel print when ping variation is above this threshold
```

### [angle]

磁性霍尔角度传感器支持，用于使用 a1333、as5047d、mt6816、mt6826s 或 tle5012b SPI 芯片读取步进电机角度轴测量值。测量值可通过 [API 服务器](API_Server.md)和[运动分析工具](Debugging.md#motion-analysis-and-data-logging)获得。有关可用命令，请参见 [G-Code 参考](G-Codes.md#angle)。

```
[angle my_angle_sensor]
sensor_type:
#   The type of the magnetic hall sensor chip. Available choices are
#   "a1333", "as5047d", "mt6816", "mt6826s", and "tle5012b". This parameter must be
#   specified.
#sample_period: 0.000400
#   The query period (in seconds) to use during measurements. The
#   default is 0.000400 (which is 2500 samples per second).
#stepper:
#   The name of the stepper that the angle sensor is attached to (eg,
#   "stepper_x"). Setting this value enables an angle calibration
#   tool. To use this feature, the Python "numpy" package must be
#   installed. The default is to not enable angle calibration for the
#   angle sensor.
cs_pin:
#   The SPI enable pin for the sensor. This parameter must be provided.
#spi_speed:
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   See the "common SPI settings" section for a description of the
#   above parameters.
```

### ⚠️ [tools_calibrate]

多工具头喷嘴偏移校准，使用 3 轴喷嘴接触探针，例如 [Zruncho3D 的 Nudge Probe](https://github.com/zruncho3d/nudge)。

```
[tools_calibrate]
pin:
travel_speed: 20
#   X and Y travel speed in mm/sec
spread: 5
#spread_x:
#spread_y:
#   X and Y travel distance around the probe
#initial_spread:
#initial_spread_x:
#initial_spread_y:
#   X and Y travel distance for the initial probe locating moves
lower_z: 1.0
#   Distance to lower in Z for contact with the sides of the probe
speed: 2
#   The speed (in mm/sec) to retract between probes
lift_speed: 4
#   Z Lift speed after probing
final_lift_z: 6
#   Z lift distance after calibration, must be greater than any
#   height variance between tools
trigger_to_bottom_z: 0.25
#   Offset from probe trigger to vertical motion bottoms out.
#   decrease if the nozzle is too high, increase if too low.
#samples: 1
#   The number of times to probe each point. The probed z-values will
#   be averaged. The default is to probe 1 time.
#sample_retract_dist: 2.0
#   The distance (in mm) to lift the toolhead between each sample (if
#   sampling more than once). The default is 2mm.
#samples_result: average
#   The calculation method when sampling more than once - either
#   "median" or "average". The default is average.
#samples_tolerance: 0.100
#   The maximum Z distance (in mm) that a sample may differ from other
#   samples. If this tolerance is exceeded then either an error is
#   reported or the attempt is restarted (see
#   samples_tolerance_retries). The default is 0.100mm.
```

### [trad_rack]

Trad Rack 多材料系统支持。有关更多信息，请参见 TradRack 仓库中的以下文档：
- [Tuning.md](https://github.com/Annex-Engineering/TradRack/blob/main/docs/Tuning.md)：下面一些配置选项引用的文档。
- [Trad Rack 配置参考文档](https://github.com/Annex-Engineering/TradRack/blob/main/docs/kalico/Config_Reference.md)：包含有关预计与 [trad_rack] 一起使用的其他配置部分的信息。

```
[trad_rack]
selector_max_velocity:
#   Maximum velocity (in mm/s) of the selector.
#   This parameter must be specified.
selector_max_accel:
#   Maximum acceleration (in mm/s^2) of the selector.
#   This parameter must be specified.
#filament_max_velocity:
#   Maximum velocity (in mm/s) for filament movement.
#   Defaults to buffer_pull_speed.
#filament_max_accel: 1500.0
#   Maximum acceleration (in mm/s^2) for filament movement.
#   The default is 1500.0.
toolhead_fil_sensor_pin:
#   The pin on which the toolhead filament sensor is connected.
#   If a pin is not specified, no toolhead filament sensor will
#   be used.
lane_count:
#   The number of filament lanes. This parameter must be specified.
lane_spacing:
#   Spacing (in mm) between filament lanes.
#   This parameter must be specified.
#lane_offset_<lane index>:
#   Options with a "lane_offset_" prefix may be specified for any of
#   the lanes (from 0 to lane_count - 1). The option will apply an
#   offset (in mm) to the corresponding lane's position. Lane offsets
#   do not affect the position of any lanes besides the one specified
#   in the option name. This option is intended for fine adjustment
#   of each lane's position to ensure that the filament paths in the
#   lane module and selector line up with each other.
#   The default is 0.0 for each lane.
#lane_spacing_mod_<lane index>:
#   Options with a "lane_spacing_mod_" prefix may be specified for any
#   of the lanes (from 0 to lane_count - 1). The option will apply an
#   offset (in mm) to the corresponding lane's position, as well as
#   any lane with a higher index. For example, if lane_spacing_mod_2
#   is 4.0, any lane with an index of 2 or above will have its
#   position increased by 4.0. This option is intended to account for
#   variations in a lane module that will affect its position as well
#   as the positions of any subsequent modules with a higher index.
#   The default is 0.0 for each lane.
servo_down_angle:
#   The angle (in degrees) for the servo's down position.
#   This parameter must be specified.
servo_up_angle:
#   The angle (in degrees) for the servo's up position.
#   This parameter must be specified.
#servo_wait_ms: 500
#   Time (in milliseconds) to wait for the servo to complete moves
#   between the up and down angles. The default is 500.
selector_unload_length:
#   Length (in mm) to retract a piece of filament out of the selector
#   and back into the lane module after the selector sensor has been
#   triggered or untriggered. This parameter must be specified.
#selector_unload_length_extra: 0.0
#   Extra length (in mm) that is added to selector_unload_length when
#   retracting a piece of filament out of the selector and back into
#   the lane module. After the retraction, the filament is moved
#   forward by this length as well (so this option's value has no
#   effect on the final position of the filament). This option may be
#   useful when using Trad Rack with a motorized spool rewinder that
#   senses tension or compression in the filament between the spool
#   and Trad Rack in order to determine when to rotate the spool. The
#   extra forward movement of the filament after retracting is
#   intended to force the rewinder's sensor to detect tension in the
#   filament, causing rewinding to cease immediately so the filament
#   tip is not moved out of position by excess spool movement. The
#   default is 0.0.
#eject_length: 10.0
#   Length (in mm) to eject the filament into the lane module past the
#   length defined by selector_unload_length. The filament is ejected
#   whenever unloading a depleted spool after a runout to make sure
#   that filament segment is not loaded again until it has been
#   replaced.
bowden_length:
#   Length (in mm) to quickly move filament through the bowden tube
#   between Trad Rack and the toolhead during loads and unloads.
#   See Tuning.md for details. This parameter must be specified.
extruder_load_length:
#   Length (in mm) to move filament into the extruder when loading the
#   toolhead. See Tuning.md for details.
#   This parameter must be specified.
hotend_load_length:
#   Length (in mm) to move filament into the hotend when loading the
#   toolhead. See Tuning.md for details.
#   This parameter must be specified.
toolhead_unload_length:
#   Length (in mm) to move filament out of the toolhead during an
#   unload. See Tuning.md for details. If toolhead_fil_sensor_pin is
#   specified, this parameter must be specified.
#   If toolhead_fil_sensor_pin is not specified, the default is
#   extruder_load_length + hotend_load_length.
#selector_sense_speed: 40.0
#   Speed (in mm/s) when moving filament until the selector
#   sensor is triggered or untriggered. See Tuning.md for details
#   on when this speed is applied. The default is 40.0.
#selector_unload_speed: 60.0
#   Speed (in mm/s) to move filament when unloading the selector.
#   The default is 60.0.
#eject_speed: 80.0
#   Speed (in mm/s) to move the filament when ejecting a filament
#   segment into the lane module.
#spool_pull_speed: 100.0
#   Speed (in mm/s) to move filament through the bowden tube when
#   loading from a spool. See Tuning.md for details.
#   The default is 100.0.
#buffer_pull_speed:
#   Speed (in mm/s) to move filament through the bowden tube when
#   unloading or loading from a buffer. See Tuning.md for details.
#   Defaults to spool_pull_speed.
#toolhead_sense_speed:
#   Speed (in mm/s) when moving filament until the toolhead
#   sensor is triggered or untriggered. See Tuning.md for details on
#   when this speed is applied. Defaults to selector_sense_speed.
#extruder_load_speed:
#   Speed (in mm/s) to move filament into the extruder when loading
#   the toolhead. See Tuning.md for details. The default is 60.0.
#hotend_load_speed:
#   Speed (in mm/s) to move filament into the hotend when loading the
#   toolhead. See Tuning.md for details. The default is 7.0.
#toolhead_unload_speed:
#   Speed (in mm/s) to move filament when unloading the toolhead.
#   See Tuning.md for details. Defaults to extruder_load_speed.
#load_with_toolhead_sensor: True
#   Whether to use the toolhead sensor when loading the toolhead.
#   See Tuning.md for details. Defaults to True but is ignored if
#   toolhead_fil_sensor_pin is not specified.
#unload_with_toolhead_sensor: True
#   Whether to use the toolhead sensor when unloading the toolhead.
#   See Tuning.md for details. Defaults to True but is ignored if
#   toolhead_fil_sensor_pin is not specified.
#fil_homing_retract_dist: 20.0
#   Distance (in mm) to retract filament away from a filament sensor
#   before moving on to the next move. This retraction occurs whenever
#   a filament sensor is triggered early during a fast move through
#   the bowden tube. See Tuning.md for details. The default is 20.0.
#target_toolhead_homing_dist:
#   Target filament travel distance (in mm) when homing to the
#   toolhead filament sensor during a load. See Tuning.md for details.
#   Defaults to either 10.0 or toolhead_unload_length, whichever is
#   greater.
#target_selector_homing_dist:
#   Target filament travel distance (in mm) when homing to the
#   selector filament sensor during an unload. See Tuning.md for
#   details. The default is 10.0.
#bowden_length_samples: 10
#   Maximum number of samples that are averaged to set bowden lengths
#   for loading and unloading. See Tuning.md for details. The default
#   is 10.
#load_lane_time: 15
#   Approximate maximum time (in seconds) to wait for filament to
#   reach the selector filament sensor when loading a lane with the
#   TR_LOAD_LANE gcode command. This time starts when the user is
#   prompted to insert filament and determines when the command will
#   be halted early if no filament is detected. The default is 15.
#load_selector_homing_dist:
#   Maximum distance to try to move filament when loading from a lane
#   module to the selector filament sensor before halting the homing
#   move. This value is not used by the TR_LOAD_LANE command but is
#   used in similar scenarios that do not involve user interaction.
#   Defaults to selector_unload_length * 2.
#bowden_load_homing_dist:
#   Maximum distance to try to move filament near the end of a
#   toolhead load (during the slow homing move to the toolhead sensor)
#   before halting the homing move. Defaults to bowden_length.
#bowden_unload_homing_dist:
#   Maximum distance to try to move filament near the end of a
#   toolhead unload (during the slow homing move to the selector
#   sensor) before halting the homing move. Defaults to bowden_length.
#unload_toolhead_homing_dist:
#   Maximum distance to try to move filament near the beginning of a
#   toolhead unload (during the homing move to the toolhead sensor)
#   before halting the homing move.
#   Defaults to (extruder_load_length + hotend_load_length) * 2.
#sync_to_extruder: False
#   Syncs Trad Rack's filament driver to the extruder during printing,
#   as well as during any extrusion moves within toolhead loading or
#   unloading that would normally involve only the extruder.
#   The default is False.
#user_wait_time: 15
#   Time (in seconds) to wait for the user to take an action
#   before continuing automatically. If set to -1, Trad Rack will wait
#   for the user indefinitely. This value is currently used by the
#   TR_LOCATE_SELECTOR gcode command. The default is 15.
#register_toolchange_commands: True
#   Whether to register gcode commands T0, T1, T2, etc. so that they
#   can be used to initiate toolchanges with Trad Rack. If set to
#   False, the TR_LOAD_TOOLHEAD command can still be used as a
#   substitute to initiate toolchanges. The default is True.
#save_active_lane: True
#   Whether to save the active lane to disk whenever it is set using
#   save_variables. If set to True, the TR_LOCATE_SELECTOR gcode
#   command will infer the active lane if the selector filament sensor
#   is triggered and an active lane was saved previously.
#   The default is True.
#log_bowden_lengths: False
#   Whether to log bowden load length data and bowden unload length
#   data (to ~/bowden_load_lengths.csv and ~/bowden_unload_lengths.csv
#   respectively). The default is False.
#pre_unload_gcode:
#   Gcode command template that is run before the toolhead is
#   unloaded. The default is to run no extra commands.
#post_unload_gcode:
#   Gcode command template that is run after the toolhead is
#   unloaded. The default is to run no extra commands.
#pre_load_gcode:
#   Gcode command template that is run before the toolhead is
#   loaded. The default is to run no extra commands.
#post_load_gcode:
#   Gcode command template that is run after the toolhead is
#   loaded. The default is to run no extra commands.
#pause_gcode:
#   Gcode command template that is run whenever Trad Rack needs to
#   pause the print (usually due to a failed load or unload). The
#   default is to run the PAUSE gcode command.
#resume_gcode:
#   Gcode command template that is run whenever the TR_RESUME command
#   needs to resume the print. The default is to run the RESUME
#   gcode command.
```

## 总线通用参数

### SPI通用设置

以下参数通常可用于使用 SPI 总线的设备。

```
#spi_speed:
#   The SPI speed (in hz) to use when communicating with the device.
#   The default depends on the type of device.
#spi_bus:
#   If the micro-controller supports multiple SPI busses then one may
#   specify the micro-controller bus name here. The default depends on
#   the type of micro-controller.
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   Specify the above parameters to use "software based SPI". This
#   mode does not require micro-controller hardware support (typically
#   any general purpose pins may be used). The default is to not use
#   "software spi".
```

### I2C通用设置

The following parameters are generally available for devices using an
I2C bus.

Note that Kalico's current micro-controller support for I2C is
generally not tolerant to line noise. Unexpected errors on the I2C
wires may result in Kalico raising a run-time error. Kalico's
support for error recovery varies between each micro-controller type.
It is generally recommended to only use I2C devices that are on the
same printed circuit board as the micro-controller.

Most Kalico micro-controller implementations only support an
`i2c_speed` of 100000 (_standard mode_, 100kbit/s). The Kalico "Linux"
micro-controller supports a 400000 speed (_fast mode_, 400kbit/s), but it must be
[set in the operating system](RPi_microcontroller.md#optional-enabling-i2c)
and the `i2c_speed` parameter is otherwise ignored. The Kalico
"RP2040" micro-controller and ATmega AVR family and some STM32
(F0, G0, G4, L4, F7, H7) support a rate of 400000 via the `i2c_speed` parameter.
All other Kalico micro-controllers use a
100000 rate and ignore the `i2c_speed` parameter.

```
#i2c_address:
#   设备的 I2C 地址。必须指定为十进制数（不是十六进制）。
#   默认值取决于设备类型。
#i2c_mcu:
#   芯片连接的微控制器名称。默认为 "mcu"。
#i2c_bus:
#   如果微控制器支持多个 I2C 总线，则可以在此处指定微控制器总线名称。
#   默认值取决于微控制器类型。
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#   指定这些参数以使用基于微控制器软件的 I2C "bit-banging" 支持。
#   这两个参数应指定微控制器上用于 scl 和 sda 线的两个引脚。
#   默认是使用由 i2c_bus 参数指定的基于硬件的 I2C 支持。
#i2c_speed:
#   与设备通信时使用的 I2C 速度（以 Hz 为单位）。
#   大多数微控制器上的 Kalico 实现硬编码为 100000，更改此值没有效果。
#   默认为 100000。Linux、RP2040 和 ATmega 支持 400000。
```
