# EtherCAT 伺服支持

本文档介绍 Kalico 对 EtherCAT 伺服驱动器的支持，使用 CoE（CANopen over EtherCAT）协议和 CiA 402 驱动器配置文件。通过以太网实现工业 EtherCAT 伺服电机的实时位置控制。

## 概述

EtherCAT 是高性能工业以太网协议。与 CANopen 或 RS485 不同，EtherCAT 帧在单次传输中遍历所有从站，实现亚微秒级的多轴同步。

Kalico 使用 **pysoem**（SOEM 的 Python 封装）作为 EtherCAT 主站栈。CiA 402 状态机复用 CANopen 模块，因为 CoE 使用相同的对象字典。

主要特性：
- **循环同步位置（CSP）** 模式，用于实时位置控制
- **轮廓位置（PP）** 模式，用于点到点运动
- **分布式时钟（DC）**，亚微秒级多轴同步
- **多从站支持**，单个 EtherCAT 网络支持多个驱动器
- **可配置周期**，250µs 到 20ms，默认 1ms

## 硬件要求

### 主机适配器

任何标准以太网适配器均可使用。EtherCAT 使用原始以太网帧，主机端不需要特殊硬件。但是：

- **Linux**：需要 root 权限或 `CAP_NET_RAW` capability
- **Windows**：需要安装 [Npcap](https://nmap.org/npcap/)，并启用 WinPcap API 兼容模式

### 伺服驱动器

任何支持 CoE（CANopen over EtherCAT）和 CiA 402 驱动器配置文件的 EtherCAT 伺服驱动器。已测试：

- **雷赛 CL3B-EC 系列** — EtherCAT 闭环步进驱动器
- 其他符合 CiA 402 的 EtherCAT 驱动器也应可用

### 网络接线

```
主机网卡 ─── CAT5/6 网线 ─── 从站 0（IN） ───（OUT） ─── 从站 1（IN） ─── ...
```

EtherCAT 使用标准以太网线缆（RJ45）。每个从站有 IN 和 OUT 端口。将主机连接到第一个从站的 IN 端口，然后从 OUT 串联到下一个从站的 IN。

### ESI 文件

每个 EtherCAT 从站需要一个 ESI（EtherCAT 从站信息）XML 文件。对于雷赛 CL3B 驱动器，从雷赛官网下载。ESI 文件通常由 SOEM 从从站的 EEPROM 自动检测。

## 安装

```bash
pip install pysoem
```

在 Linux 上，确保以 root 运行或设置 capabilities：
```bash
sudo setcap cap_net_raw+ep $(which python3)
```

## 配置

### 单个驱动器（CSP 模式）

```ini
[ethercat_stepper x]
ethercat_interface: eth0
ethercat_slave: 0
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200
```

### 多轴级联

```ini
[ethercat_stepper x]
ethercat_interface: eth0
ethercat_slave: 0
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PC1
homing_speed: 10.0
position_min: 0
position_max: 200

[ethercat_stepper y]
ethercat_interface: eth0
ethercat_slave: 1
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 40
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PD2
homing_speed: 10.0
position_min: 0
position_max: 200

[ethercat_stepper z]
ethercat_interface: eth0
ethercat_slave: 2
canopen_mode: CSP
ethercat_cycle_time: 0.001
rotation_distance: 8
microsteps: 1
full_steps_per_rotation: 200
endstop_pin: ^PE3
homing_speed: 5.0
position_min: 0
position_max: 300
```

## 配置参考

### [ethercat_stepper]

```
[ethercat_stepper x]
ethercat_interface:
#   网络接口名称。Linux: eth0, enp3s0 等。
#   Windows: Npcap 设备名。必填。
ethercat_slave: 0
#   从站位置索引（0 = 第一个从站）。默认 0。
#canopen_mode: CSP
#   运行模式。可选：CSP（循环同步位置）、PP（轮廓位置）、
#   CSV（循环同步速度）、HOMING。默认 CSP。
#ethercat_cycle_time: 0.001
#   DC 同步周期时间（秒）。范围：0.000250 到 0.020。
#   默认 0.001（1ms）。
rotation_distance:
#   伺服电机旋转一圈的距离（毫米）。必填。
microsteps:
#   EtherCAT 伺服设为 1（框架要求）。
#full_steps_per_rotation: 200
#   编码器每圈计数。默认 200。
#endstop_pin:
#   传统回原的限位引脚。回原必填。
#homing_speed: 5.0
#   回原速度（毫米/秒）。默认 5.0。
#position_min: 0
#   最小位置（毫米）。默认 0。
#position_max:
#   最大位置（毫米）。设置 endstop_pin 时必填。
```

## CL3B EtherCAT 寄存器映射

雷赛 CL3B-EC 系列 CSP 模式默认 PDO 映射：

### RxPDO 1（主站→从站，6 字节）

| 对象 | 子索引 | 类型 | 位数 | 描述 |
|------|--------|------|------|------|
| 0x6040 | 0x00 | UINT | 16 | 控制字 |
| 0x607A | 0x00 | DINT | 32 | 目标位置 |

### TxPDO 1（从站→主站，~15 字节）

| 对象 | 子索引 | 类型 | 位数 | 描述 |
|------|--------|------|------|------|
| 0x603F | 0x00 | UINT | 16 | 错误码 |
| 0x6041 | 0x00 | UINT | 16 | 状态字 |
| 0x6061 | 0x00 | SINT | 8 | 运行模式显示 |
| 0x6064 | 0x00 | DINT | 32 | 实际位置值 |
| 0x60B9 | 0x00 | UINT | 16 | 探针状态 |
| 0x60BA | 0x00 | DINT | 32 | 探针 1 正向值 |
| 0x60FD | 0x00 | UDINT | 32 | 数字输入 |

### CiA 402 控制字（0x6040）状态转换

| 转换 | 控制字 | 状态字 | 描述 |
|------|--------|--------|------|
| 上电→准备好 | 自动 | 0x0250 | 自动 |
| 准备好→开关禁用 | 0x0000 | 0x0250 | 关机 |
| 开关禁用→准备好 | 0x0006 | 0x0231 | 关机 |
| 准备好→等待使能 | 0x0007 | 0x0233 | 开关上电 |
| 等待使能→使能 | 0x000F | 0x0237 | 使能运行 |
| 故障→准备好 | 0x0080 | 0x0250 | 故障复位 |

### 支持的运行模式（0x6060）

| 值 | 模式 | 描述 |
|----|------|------|
| 1 | PP | 轮廓位置 |
| 3 | PV | 轮廓速度 |
| 6 | HM | 回原模式 |
| 8 | CSP | 循环同步位置 |

## 分布式时钟（DC）

EtherCAT DC 提供亚微秒级的多从站同步。CL3B 支持以下 DC 配置：

- AssignActivate: `#x0300`
- CycleTimeSync0: 可配置（默认 1ms）
- ShiftTimeSync0: 0

设置 `ethercat_cycle_time` 时自动启用 DC。同一网络上的所有从站共享相同的 DC 参考时钟。

## 数据流

```
Toolhead → generate_steps() → itersolve_get_commanded_pos()
  → EtherCATBackend
      ├─ 构建 RPDO: [控制字(2)] [目标位置(4)]
      ├─ slave.write_output(rpdo_data)
      ├─ slave.read_input() → TPDO
      └─ 解析 TPDO: [错误(2)] [状态字(2)] [模式(1)] [实际位置(4)]
          → PositionTracker
```

PDO 交换通过 `master.exchange_processdata()` 完成，由 DC 同步定时器按配置的周期时间调用。

## 故障排除

### 找不到从站

1. 检查网线连接
2. 确认接口名称正确（Linux 使用 `ip addr`）
3. 确保有 root 权限（Linux）或安装了 Npcap（Windows）
4. 检查从站是否上电

### 从站无法达到 OP 状态

1. 检查 ESI 文件与驱动器型号匹配
2. 确认驱动器未处于故障状态
3. 检查 DC 同步配置
4. 查看驱动器上的 RUN 和 ERR 指示灯

### 位置漂移

1. 确认编码器工作正常
2. 检查 `rotation_distance` 与机械结构匹配
3. 确保驱动器在 CSP 模式（0x6060 = 8）

### 通信超时

1. 检查网线质量和长度（每段最长 100 米）
2. 如果总线上从站过多，降低周期时间
3. 检查是否有网络干扰
