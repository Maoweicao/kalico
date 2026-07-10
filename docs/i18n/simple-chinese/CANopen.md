# CANopen 伺服支持

本文档介绍 Kalico 对 CANopen CiA 402 伺服驱动器的支持。CANopen 允许通过 CAN 总线直接使用工业伺服电机，无需步进/方向脉冲信号。

## 概述

CANopen 是基于 CAN 总线的高层协议（CiA 301）。与 Kalico 原生 CAN 协议（将 CAN 作为 MCU 步进/方向命令的传输层）不同，CANopen 直接向智能伺服驱动器发送位置指令。驱动器自行处理轨迹生成、电流控制和编码器反馈。

主要特性：
- **循环同步位置（CSP）** 模式，用于实时位置控制
- **循环同步速度（CSV）** 模式，用于速度控制
- **轮廓位置（PP）** 模式，使用驱动器内部轨迹生成器
- **CiA 402 回原**，支持 11 种回原方法（限位开关、原点开关、索引脉冲）
- **EDS/DCF 设备描述文件** 支持（INI 格式，CiA 306 标准）
- **SYNC 分组**，用于多轴同步运动

## 硬件要求

### CAN 总线接口

需要一个连接到主机的 CAN 总线适配器。有关主机端 CAN 硬件和操作系统配置，请参阅 [CANBUS](CANBUS.md) 文档。

### 伺服驱动器

任何符合 CANopen CiA 402 标准的伺服驱动器均可使用。常见驱动器：
- **EtherCAT/CANopen 双模驱动器**（如雷赛、汇川、台达等）
- **CANopen 伺服驱动器**
- **带 CiA 402 支持的 BLDC/PMSM 驱动器**

驱动器必须至少支持以下运行模式之一：
- **CSP（循环同步位置）** — 推荐用于 CNC/3D 打印
- **CSV（循环同步速度）** — 速度控制的替代方案
- **PP（轮廓位置）** — 使用驱动器内部轨迹生成器

### EDS/DCF 文件

每个驱动器需要一个 INI 格式的 EDS（电子数据表）或 DCF（设备配置文件）。该文件描述驱动器的对象字典、支持的模式和默认参数。文件通常由驱动器制造商提供。

支持的文件格式：
- `.eds` — 标准电子数据表（CiA 306 INI 格式）
- `.dcf` — 设备配置文件（相同格式，含设备特定值）

## 配置

### 基本单轴配置

```ini
[canopen_stepper x]
can_interface: socketcan
can_channel: can0
can_bitrate: 1000000
node_id: 1
eds_file: ~/servo_configs/servo_x.eds
canopen_mode: CSP
sync_group: default
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### 多轴共享总线

多个伺服共享同一 CAN 总线时，使用 `[canopen_bus]` 段避免重复总线参数：

```ini
[canopen_bus main]
interface: socketcan
channel: can0
bitrate: 1000000

[canopen_stepper x]
canopen_bus: main
node_id: 1
eds_file: ~/configs/servo_x.eds
canopen_mode: CSP
sync_group: xy_group
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200

[canopen_stepper y]
canopen_bus: main
node_id: 2
eds_file: ~/configs/servo_y.eds
canopen_mode: CSP
sync_group: xy_group
sync_period: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200

[canopen_stepper z]
canopen_bus: main
node_id: 3
eds_file: ~/configs/servo_z.eds
canopen_mode: CSP
sync_group: z_group
sync_period: 0.002
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

### CiA 402 回原（伺服内部回原）

可以使用伺服驱动器内置的 CiA 402 回原模式，代替连接到 MCU GPIO 的物理限位开关：

```ini
[canopen_stepper z]
canopen_bus: main
node_id: 3
eds_file: ~/configs/servo_z.eds
canopen_mode: CSP
sync_group: z_group
sync_period: 0.001
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: canopen
canopen_homing_method: negative_limit
canopen_homing_speed_switch: 1000
canopen_homing_speed_zero: 500
canopen_homing_accel: 5000
canopen_homing_offset: 100
homing_speed: 5.0
position_min: 0
position_max: 300
```

## 配置参考

### [canopen_bus]

多个 CANopen 步进电机共享的 CAN 总线参数。

```
[canopen_bus my_bus]
interface: socketcan
#   CAN 接口类型。必填。常用值："socketcan"（Linux）、
#   "slcan"（串行线路 CAN）、"pcan"（PEAK）。
channel: can0
#   CAN 通道名称。必填。对于 socketcan，这是网络接口名称
#   （如 "can0"）。对于 slcan，这是串口设备（如 "/dev/ttyACM0"）。
#bitrate: 1000000
#   CAN 总线波特率（bps）。默认 1000000（1 Mbit/s）。
```

### [canopen_stepper]

CANopen CiA 402 伺服步进电机配置。

```
[canopen_stepper x]
#canopen_bus:
#   引用 [canopen_bus] 段。如果未指定，需要直接提供
#   can_interface、can_channel 和 can_bitrate。
#can_interface:
#can_channel:
#can_bitrate: 1000000
#   直接总线配置（替代 canopen_bus）。
node_id:
#   CANopen 节点 ID（1-127）。必填。
eds_file:
#   设备的 EDS/DCF 文件路径（CiA 306 INI 格式）。必填。
#   支持 ~/ 表示主目录。相对路径从配置文件目录解析。
#canopen_mode: CSP
#   运行模式。可选：CSP（循环同步位置）、CSV（循环同步速度）、
#   PP（轮廓位置）、PV（轮廓速度）、CST（循环同步转矩）。
#   默认 CSP。
#sync_group: default
#   SYNC 分组名称。相同 sync_group 的步进电机共享 CANopen
#   SYNC 信号，PDO 交换同步进行。默认 "default"。
#sync_period: 0.001
#   SYNC 周期（秒），范围 0.000250 到 0.010。控制位置指令
#   发送到驱动器的频率。默认 0.001（1ms，1kHz）。
rotation_distance:
#   伺服电机旋转一圈轴移动的距离（毫米）。必填。
microsteps:
#   CANopen 伺服设为 1（框架要求，实际不使用）。
#full_steps_per_rotation: 200
#   编码器每圈计数或电机极数。默认 200。
#endstop_pin:
#   限位引脚。设为 "canopen" 使用 CiA 402 内部回原，
#   或指定 GPIO 引脚使用传统限位开关。回原必填。
#canopen_homing_method: negative_limit
#   CiA 402 回原方法（仅 endstop_pin 为 "canopen" 时使用）。
#   可选：current_position、positive_limit、negative_limit、
#   positive_home、negative_home、positive_home_index、
#   negative_home_index、negative_limit_index、
#   positive_limit_index、index_positive、index_negative。
#   也接受数字（1-35）。默认 "negative_limit"。
#canopen_homing_speed_switch:
#   搜索开关速度（编码器计数/秒）。未指定时使用驱动器默认值。
#canopen_homing_speed_zero:
#   搜索零点速度（编码器计数/秒）。未指定时使用驱动器默认值。
#canopen_homing_accel:
#   回原加速度（编码器计数/秒²）。未指定时使用驱动器默认值。
#canopen_homing_offset: 0
#   零点偏移（编码器计数）。默认 0。
```

## SYNC 分组

SYNC 分组控制多个 CANopen 节点的同步方式。同一 SYNC 分组中的所有节点共享相同的 SYNC 帧时序，位置指令在同一时刻更新。

```ini
[canopen_stepper x]
sync_group: xy_group    # 同组 = 同步
sync_period: 0.001

[canopen_stepper y]
sync_group: xy_group    # 与 x 轴共享 SYNC
sync_period: 0.001      # 组内周期必须一致

[canopen_stepper z]
sync_group: z_group     # 独立 SYNC
sync_period: 0.002      # 可以有不同周期
```

SYNC 分组中第一个注册的步进电机会成为 SYNC 生产者。组内其他步进电机都是消费者。

## CiA 402 回原方法

使用 `endstop_pin: canopen` 时，可选择以下回原方法：

| 方法 | 编号 | 描述 |
|------|------|------|
| `current_position` | 35 | 使用当前位置作为原点 |
| `positive_limit` | 17 | 正向限位开关 |
| `negative_limit` | 18 | 负向限位开关 |
| `positive_home` | 1 | 正向原点开关 |
| `negative_home` | 2 | 负向原点开关 |
| `positive_home_index` | 11 | 正向原点开关 + 索引脉冲 |
| `negative_home_index` | 12 | 负向原点开关 + 索引脉冲 |
| `negative_limit_index` | 23 | 负向限位开关 + 索引脉冲 |
| `positive_limit_index` | 27 | 正向限位开关 + 索引脉冲 |
| `index_positive` | 33 | 索引脉冲，正方向 |
| `index_negative` | 34 | 索引脉冲，负方向 |

具体行为取决于伺服驱动器对 CiA 402 回原的实现。请参考驱动器手册了解每种方法的详细说明。

## EDS 文件格式

EDS（电子数据表）文件使用 CiA 306 INI 格式。典型的 EDS 文件包含：

```ini
[DeviceInfo]
VendorName=MyServo
VendorNumber=0x12345678
ProductName=ServoX
ProductCode=0x00010001

[Objects]
1000=1
1018=4
6040=1
6041=1
6060=1
607A=1
6064=1

[1000]
ParameterName=Device Type
ObjectType=7
DataType=0x0007
AccessType=ro
DefaultValue=0x00020192

[6040]
ParameterName=Controlword
ObjectType=7
DataType=0x0006
AccessType=rw
DefaultValue=0x0000
PDOMapping=1
```

必须存在的关键对象：
- `0x1000` — 设备类型
- `0x1018` — 身份对象（厂商 ID、产品代码）
- `0x6040` — 控制字
- `0x6041` — 状态字
- `0x6060` — 运行模式
- `0x607A` — 目标位置（CSP 模式）
- `0x6064` — 实际位置
- `0x1600` — RPDO 1 映射
- `0x1A00` — TPDO 1 映射

## 故障排除

### 驱动器无法使能

检查以下内容：
1. EDS 文件与驱动器型号匹配
2. node_id 与驱动器配置的 ID 一致
3. CAN 总线波特率与驱动器配置一致
4. 驱动器已上电且未处于故障状态

### 回原失败

对于 CiA 402 回原：
1. 确认 `canopen_homing_method` 与硬件设置匹配
2. 检查回原速度在驱动器限制范围内
3. 确保驱动器支持所选的回原方法（查看 EDS）

### 位置漂移

如果实际位置与指令位置漂移：
1. 检查驱动器是否在正确的运行模式（CSP）
2. 确认编码器工作正常
3. 检查 CAN 总线错误（重传、丢帧）

### CAN 总线错误

如果出现 CAN 总线错误：
1. 检查终端电阻（总线两端各一个 120 欧姆电阻）
2. 确认总线长度在规格范围内
3. 检查接地是否正确
4. 使用长电缆时降低总线速度
