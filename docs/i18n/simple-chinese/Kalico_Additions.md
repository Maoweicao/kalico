# Kalico 增强功能

## 对 Klipper 默认值的更改

- [`[force_move]`](./Config_Reference.md#force_move) 默认启用。使用 `[force_move] enable_force_move: False` 禁用
- [`[respond]`](./Config_Reference.md#respond) 默认启用。使用 `[respond] enable_respond: False` 禁用
- [`[exclude_object]`](./Config_Reference.md#exclude_object) 默认启用。使用 `[exclude_object] enable_exclude_object: False` 禁用

## 其他配置选项

- [`[mcu] is_non_critical`](./Config_Reference.md#mcu) 启用将 mcu 标记为可选 - 可以随意断开连接和连接。（对于基于 MCU 的加速度计板、在热室中关闭的基于 mcu 的探针等有用...）
- [`[danger_options]`](./Config_Reference.md#danger-options) - 新配置选项调整之前隐藏的 Kalico 值
- 启用按轴加速度的其他运动学版本，请参阅 [limited_cartesian](./Config_Reference.md#cartesian-kinematics-with-limits-for-x-and-y-axes) 和 [limited_corexy](./Config_Reference.md#corexy-kinematics-with-limits-for-x-and-y-axes)
- 其他运动学：[SCARA、TPARA、Polargraph、传送带打印机、机器人臂、热丝切割机](./Kinematics_Additions.md)以及 CoreYX/CoreYZ/CoreZX/CoreZY 变体
- `--rotate-log-at-restart` 可以添加到 Kalico 启动脚本或服务以强制每次重启时进行日志轮换。
- [`[virtual_sdcard] with_subdirs`](./Config_Reference.md#virtual_sdcard) 启用扫描子目录中的 .gcode 文件，用于菜单和 M20/M23 命令
- [`[firmware_retraction] z_hop_height`](./Config_Reference.md#firmware_retraction) 在使用固件回抽时添加自动 z 跳跃
- [`[constants]` 和 `${constants.value}`](./Config_Reference.md#configuration-references) 允许在配置中重复使用值

## 增强的行为

- [`canbus_query.py`](./CANBUS.md#finding-the-canbus_uuid-for-new-micro-controllers) 现在以所有 Kalico 设备响应，即使在分配了 node_id 后。
- 输入整形校准现在警告可能影响测量精度的活跃风扇。
- [`BED_MESH_CHECK`](./G-Codes.md#bed_mesh_check) 根据指定条件验证当前床网格，允许在打印前检查最大偏差和相邻点之间的斜率。
- [`[resonance_tester]`](./Config_Reference.md#resonance_tester) 现在通过新的 `accel_chips` 参数支持多个加速度计芯片，允许来自多个加速度计的数据组合以进行更准确的输入整形校准。

## 固定设备标识（自定义 CAN UUID / USB 名称）

以下选项在固件编译时通过 `make menuconfig` 配置。

### 自定义 / 固定 CAN 总线 UUID

默认情况下，CAN 总线 UUID 由微控制器的出厂芯片 id 派生而来（参见 [CANBUS](./CANBUS.md#finding-the-canbus_uuid-for-new-micro-controllers)）。Kalico 还允许你设置一个自己定义的固定 UUID：

1. 运行 `make menuconfig` 并打开 **"CAN bus UUID"** 菜单。
2. `CAN_UUID_USE_CHIPID`（默认启用）会对芯片 id 进行哈希来生成 UUID。取消勾选它，改为使用你自己定义的值。
3. 在 `CAN_UUID_CUSTOM` 中填入任意字符串（例如 `myboard01`）。固件会对该字符串运行 `fasthash64` 以生成固定的 6 字节 UUID。相同的字符串总是映射到相同的 UUID，因此同一值可跨多块板卡复用。

支持 stm32、atsamd、atsam、rp2040 和 lpc176x 微控制器。同时适用于直接 CAN 模式和 USB 转 CAN 桥接模式（在桥接模式下 UUID 仍由 `chipid_init` 生成）。

### 固定 USB 设备名称

使用 USB（USB 串口 / `USB-CDC`）模式时，可以固定 Linux 下的设备名称：

1. 运行 `make menuconfig` 并打开 **"USB ids"** 菜单。
2. `USB_MANUFACTURER` – 厂商名称（默认 `Klipper`）。
3. `USB_PRODUCT` – 产品名称（默认为 MCU 型号）。
4. `USB_SERIAL_NUMBER` – 固定序列号（默认 `12345`）。`USB_SERIAL_NUMBER_CHIPID` 会用芯片 id 替代该值。

这些会以形如 `usb-<厂商>_<产品>_<序列号>-if00` 的稳定 `/dev/serial/by-id/` 路径出现在 Linux 中，可从 printer.cfg 引用（参见 [MCU 连接方式](./MCU_Connection_Methods.md)）。

> 注意：在 **USB 转 CAN 桥接**模式下，USB 厂商/产品 id 固定为 gs_usb 的 `1d50:606f`，不可自定义（这是为了让内核 gs_usb 驱动绑定所需的）。在桥接模式下，节点通过其 CAN UUID 而非 USB 名称来识别。

## 新 Kalico 模块

- [gcode_shell_command](./G-Code_Shell_Command.md) - 从 Kalico 中执行 Linux 命令和脚本
- [dummy_thermistor](./Dummy_Thermistor.md) - 用于测试和冷挤出机的虚拟温度传感器
- [冷挤出机](./Cold_Extruder.md) - 用于陶泥、混凝土和其他冷材料的无加热器挤出机支持
- [`[closed_loop]`](./Config_Reference.md#closed_loop) - 使用 [encoder](./Config_Reference.md#encoder) 反馈的闭环位置控制
- [`[encoder]`](./Config_Reference.md#encoder) - 位置编码器支持（SPI 绝对传感器和正交传感器），带 `ENCODER_POSITION` 和 `ENCODER_RAW_DATA` 命令
- [`[gcode_mcu_trace]`](./Config_Reference.md#gcode_mcu_trace) - G-code 到 MCU 命令的追踪，带 `MCU_RECORD_START`、`MCU_RECORD_STOP`、`MCU_REPLAY` 和 `MCU_TRACE_STATUS` 命令
- [`[bmi160]`](./Config_Reference.md#bmi160) - bmi160 加速度计支持（SPI 或 I2C）
- [`[query_pins]`](./Config_Reference.md#query_pins) - 使用 `QUERY_PINS` 命令查询 MCU 引脚/总线配置的实用工具

## 无传感器归位

- [`[tmcXXXX] home_current`](./Config_Reference.md#tmc-stepper-driver-configuration) 自动为归位设置不同的电流
- [`[tmcXXXX] current_change_dwell_time`](./Config_Reference.md#tmc-stepper-driver-configuration) 将在归位前添加延迟
- [`[stepper_X] homing_retract_dist, homing_retract_speed`](./Config_Reference.md#stepper) 添加短回抽和第二次归位以获得更好的准确性
- [`[stepper_X] min_home_dist`](./Config_Reference.md#stepper) 将在归位前远离限位

## 探针和探测

- [`[probe] drop_first_result: True`](./Config_Reference.md#probe) 在探测时将丢弃第一个结果。这可以改进具有异常值的第一个样本的打印机的探针精度。
- [`[dockable_probe]`](./Config_Reference.md#dockable_probe) 为停靠探针提供有帮助的本地支持，例如 Annex Quickdraw、Klicky/Unklicky 和许多其他产品。
- [`[z_calibration]`](./Config_Reference.md#z_calibration) 启用使用参考限位（如 Voron 2.4 喷嘴限位）的自动探针 Z 偏移校准。
- [`[z_tilt_ng]`](./Config_Reference.md#z_tilt_ng) 添加强制 3 点 z 倾斜校准
- [`[z_tilt/quad_gantry_level] increasing_threshold`](./Config_Reference.md#z_tilt) 允许自定义在多次探测时允许的变化
- [`[z_tilt/quad_gantry_level] adaptive_horizontal_move_z`](./Config_Reference.md#z_tilt) 根据产生的误差自适应地降低 horizontal_move_z - z_tilt 和 QGL 更快更安全！
- [`[safe_z_home] home_y_before_x`](./Config_Reference.md#safe_z_home) 让您在 X 之前进行 Y 归位。
- [`[z_tilt/quad_gantry_level/etc] use_probe_xy_offsets`](./Config_Reference.md#z_tilt) 让您决定是否将 `[probe] XY 偏移应用于探针位置。

## 加热器、风扇和 PID 更改

- [模型预测控制](./MPC.md) 是一种提供传统 PID 控制替代方案的先进温度控制方法。
- [速度 PID](./PID.md) 可以比位置 PID 更准确，但对嘈杂的传感器更敏感，可能需要更大的平滑时间
- [`PID_PROFILE [LOAD/SAVE]`](./G-Codes.md#pid_profile) 允许在多个温度和风扇速度下校准和保存 PID 配置文件，稍后恢复。使用一些聪明的宏，自动按材料 pid 调整是可以实现的！
- [`SET_HEATER_PID HEATER= KP= KI= KD=`](./G-Codes.md#set_heater_pid) 可以在不重新加载的情况下更新 PID 参数。
- [`HEATER_INTERRUPT`](./G-Codes.md#heater_interrupt) 将中断 `TEMPERATURE_WAIT`。
- ADC 超出范围的错误现在包括哪个加热器和其他信息以协助排除故障

- [`[temperature_fan] control: curve`](./Config_Reference.md#temperature_fan) 让您设置风扇曲线而不是线性控制
- [`[temperature_fan] reverse: True`](./Config_Reference.md#temperature_fan) 将让您反向控制风扇以进行温度控制。温度越低，风扇运行越高。
- 风扇现在在 `min_power` 和 `max_power` 范围内标准化 PWM 功率，因此将风扇设置为 10% 将在配置的最小/最大范围内获得 10% 的风扇速度。
- 双循环 PID 控制以精确管理床的温度，同时限制加热器功率以防止超过最高温度。

## TMC 驱动器

- [`[tmc2240] driver_CS 和 current_range`](./Config_Reference.md#tmc2240) 让您调整 tmc2240 驱动器的电流缩放器和电流范围。

## 宏

- Jinja `do` 扩展已启用。现在可以在宏中调用函数而不需要诉诸肮脏的黑客：`{% do array.append(5) %}`
- Python [`math`](https://docs.python.org/3/library/math.html) 库对宏可用。`{math.sin(math.pi * variable)}` 等等！
- 新的 [`RELOAD_GCODE_MACROS`](./G-Codes.md#reload_gcode_macros) G-Code 命令以重新加载 `[gcode_macro]` 模板，而无需重启。
- G-Code 宏可以用 Python 编写。阅读更多内容 [此处](./Command_Templates.md)
  - 宏也可以从其他文件加载，使用 `!!include path/to/file.py`
- 在宏中，可以使用 `RETURN` 在不引发错误的情况下提前结束宏执行。

## 插件

使用自定义插件扩展 Kalico 安装。

您的 Python 插件现在可以扩展 [`klippy/extras`](https://github.com/KalicoCrew/kalico/tree/main/klippy/extras)，在 Kalico 中添加新模块，而不会因"dirty"git 树而导致更新失败。

启用 `[danger_options] allow_plugin_override: True` 以覆盖现有的额外功能。