# Kalico 新增功能

## 对 Klipper 默认值的更改

- [`[force_move]`](./Config_Reference.md#force_move) 默认启用。使用 `[force_move] enable_force_move: False` 来禁用它
- [`[respond]`](./Config_Reference.md#respond) 默认启用。使用 `[respond] enable_respond: False` 来禁用它
- [`[exclude_object]`](./Config_Reference.md#exclude_object) 默认启用。使用 `[exclude_object] enable_exclude_object: False` 来禁用它

## 附加配置选项

- [`[mcu] is_non_critical`](./Config_Reference.md#mcu) 允许将 MCU 标记为可选 - 它可以随意断开和连接。（适用于基于 MCU 的加速度计板、在高温腔室中关闭的基于 MCU 的探针等...）
- [`[danger_options]`](./Config_Reference.md#danger-options) - 新的配置选项，用于调整之前隐藏的 Kalico 值
- 附加运动学版本支持每轴加速度限制，参见 [limited_cartesian](./Config_Reference.md#cartesian-kinematics-with-limits-for-x-and-y-axes) 和 [limited_corexy](./Config_Reference.md#corexy-kinematics-with-limits-for-x-and-y-axes)
- `--rotate-log-at-restart` 可以添加到你的 Kalico 启动脚本或服务中，以在每次重启时强制轮换日志
- [`[virtual_sdcard] with_subdirs`](./Config_Reference.md#virtual_sdcard) 启用扫描子目录中的 .gcode 文件，用于菜单和 M20/M23 命令
- [`[firmware_retraction] z_hop_height`](./Config_Reference.md#firmware_retraction) 在使用固件回缩时添加自动 Z 抬升
- [`[constants]` 和 `${constants.value}`](./Config_Reference.md#configuration-references) 允许在配置中重复使用值

## 增强行为

- [`canbus_query.py`](./CANBUS.md#finding-the-canbus_uuid-for-new-micro-controllers) 现在响应所有 Kalico 设备，即使在分配了 node_id 之后。
- 输入整形校准现在会警告可能影响测量精度的活动风扇。
- [`BED_MESH_CHECK`](./G-Codes.md#bed_mesh_check) 根据指定标准验证当前床面网格，允许你在打印前检查最大偏差和相邻点之间的斜率。
- [`[resonance_tester]`](./Config_Reference.md#resonance_tester) 现在通过新的 `accel_chips` 参数支持多个加速度计芯片，允许组合来自多个加速度计的数据以获得更准确的输入整形校准。

## 新 Kalico 模块

- [gcode_shell_command](./G-Code_Shell_Command.md) - 从 Kalico 内部执行 Linux 命令和脚本

## 无传感器归零

- [`[tmcXXXX] home_current`](./Config_Reference.md#tmc-stepper-driver-configuration) 在归零时自动设置不同的电流
- [`[tmcXXXX] current_change_dwell_time`](./Config_Reference.md#tmc-stepper-driver-configuration) 在归零前添加延迟
- [`[stepper_X] homing_retract_dist, homing_retract_speed`](./Config_Reference.md#stepper) 添加短回缩和第二次归零以提高精度
- [`[stepper_X] min_home_dist`](./Config_Reference.md#stepper) 在归零前远离限位开关

## 探针和探测

- [`[probe] drop_first_result: True`](./Config_Reference.md#probe) 在探测时丢弃第一个结果。这可以提高第一个采样存在异常值的打印机的探测精度。
- [`[dockable_probe]`](./Config_Reference.md#dockable_probe) 为可停靠探针（如 Annex Quickdraw、Klicky/Unklicky 以及无数其他探针）提供有用的原生支持。
- [`[z_calibration]`](./Config_Reference.md#z_calibration) 使用参考限位开关（如 Voron 2.4 喷嘴限位开关）启用自动探针 Z 偏移校准。
- [`[z_tilt_ng]`](./Config_Reference.md#z_tilt_ng) 添加强制 3 点 Z 倾斜校准
- [`[z_tilt/quad_gantry_level] increasing_threshold`](./Config_Reference.md#z_tilt) 允许你在多次探测时自定义允许的变化
- [`[z_tilt/quad_gantry_level] adaptive_horizontal_move_z`](./Config_Reference.md#z_tilt) 根据结果误差自适应减少 horizontal_move_z - z_tilt 和 QGL 更快更安全！
- [`[safe_z_home] home_y_before_x`](./Config_Reference.md#safe_z_home) 允许你在 X 之前归零 Y。
- [`[z_tilt/quad_gantry_level/etc] use_probe_xy_offsets`](./Config_Reference.md#z_tilt) 让你决定是否将 `[probe] XY 偏移应用于探测位置。
- [`[z_tilt/quad_gantry_level/etc] alternate_probe_direction`](./Config_Reference.md#z_tilt) 在重试之间交替探测方向，以减少线缆、鲍登管、脐带和耗材路径的扭曲，同时避免额外的回程移动。

## 加热器、风扇和 PID 变更

- [模型预测控制](./MPC.md) 是一种先进的温度控制方法，提供了传统 PID 控制的替代方案。
- [速度 PID](./PID.md) 可能比位置式 PID 更精确，但更容易受到噪声传感器的影响，可能需要更大的平滑时间
- [`PID_PROFILE [LOAD/SAVE]`](./G-Codes.md#pid_profile) 允许你在多个温度和风扇速度下校准和保存 PID 配置文件，之后可以恢复它们。通过一些巧妙的宏，自动按材料 PID 调优就在眼前！
- [`SET_HEATER_PID HEATER= KP= KI= KD=`](./G-Codes.md#set_heater_pid) 可以在不重新加载的情况下更新你的 PID 参数。
- [`HEATER_INTERRUPT`](./G-Codes.md#heater_interrupt) 将中断 `TEMPERATURE_WAIT`。
- ADC 超范围错误现在包含是哪个加热器以及辅助故障排除的附加信息

- [`[temperature_fan] control: curve`](./Config_Reference.md#temperature_fan) 允许你设置风扇曲线而不是线性控制
- [`[temperature_fan] reverse: True`](./Config_Reference.md#temperature_fan) 允许你以与温度控制相反的方式控制风扇。温度越低，风扇运行速度越高。
- 风扇现在在 `min_power` 和 `max_power` 范围内标准化 PWM 功率，因此将风扇设置为 10% 将在你配置的最小/最大范围内获得 10% 的风扇速度。
- 双环 PID 控制，准确管理床面温度，同时限制加热器功率以防止超过最大温度。

## TMC 驱动

- [`[tmc2240] driver_CS 和 current_range`](./Config_Reference.md#tmc2240) 允许你调整 tmc2240 驱动的电流缩放器和电流范围。

## 宏

- 已启用 jinja `do` 扩展。你现在可以在宏中调用函数，而无需使用变通方法：`{% do array.append(5) %}`
- Python [`math`](https://docs.python.org/3/library/math.html) 库可供宏使用。`{math.sin(math.pi * variable)}` 等！
- 新的 [`RELOAD_GCODE_MACROS`](./G-Codes.md#reload_gcode_macros) G-Code 命令，无需重启即可重新加载 `[gcode_macro]` 模板。
- G-Code 宏可以用 Python 编写。更多信息请参阅[这里](./Command_Templates.md)
  - 宏也可以从其他文件加载，使用 `!!include path/to/file.py`
- 在宏内部，你可以使用 `RETURN` 提前结束宏执行而不引发错误。

## 插件

使用自定义插件扩展你的 Kalico 安装。

你的 Python 插件现在可以扩展 [`klippy/extras`](https://github.com/KalicoCrew/kalico/tree/main/klippy/extras)，向 Kalico 添加新模块，而不会导致更新因"脏"git 树而失败。

启用 `[danger_options] allow_plugin_override: True` 以覆盖现有的 extras。
