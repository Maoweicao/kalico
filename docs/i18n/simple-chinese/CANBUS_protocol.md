# CANBUS 协议

本文档描述了 Kalico 使用的通过
[CAN 总线](https://en.wikipedia.org/wiki/CAN_bus)通信的协议。
有关如何使用 CAN 总线配置 Kalico 的信息，请参阅
[CANBUS.md](CANBUS.md)。

## 微控制器 ID 分配

Kalico 仅使用 CAN 2.0A 标准大小 CAN 总线数据包，
这些数据包限制为 8 个数据字节和 11 位 CAN 总线标识符。
为了支持高效通信，每个微控制器在运行时被分配一个唯一的 1 字节
CAN 总线节点 ID (`canbus_nodeid`) 用于常规 Kalico 命令和响应流量。
从主机到微控制器的 Kalico 命令消息使用 `canbus_nodeid * 2 + 256`
的 CAN 总线 ID，而从微控制器到主机的 Kalico 响应消息使用
`canbus_nodeid * 2 + 256 + 1`。

每个微控制器都有一个工厂分配的唯一芯片标识符，用于 ID 分配。
该标识符可能超过一个 CAN 数据包的长度，因此使用哈希函数从工厂
ID 生成唯一的 6 字节 ID (`canbus_uuid`)。

## 管理消息

管理消息用于 ID 分配。从主机发送到微控制器的管理消息使用
CAN 总线 ID `0x3f0`，从微控制器发送到主机的消息使用
CAN 总线 ID `0x3f1`。所有微控制器都监听 ID `0x3f0` 上的消息；
该 ID 可以被认为是"广播地址"。

### CMD_QUERY_UNASSIGNED 消息

此命令查询所有尚未被分配 `canbus_nodeid` 的微控制器。
未分配的微控制器将使用 RESP_NEED_NODEID 响应消息进行响应。

CMD_QUERY_UNASSIGNED 消息格式为：
`<1-byte message_id = 0x00>`

### CMD_SET_KLIPPER_NODEID 消息

此命令为给定 `canbus_uuid` 的微控制器分配一个 `canbus_nodeid`。

CMD_SET_KLIPPER_NODEID 消息格式为：
`<1-byte message_id = 0x01><6-byte canbus_uuid><1-byte canbus_nodeid>`

### RESP_NEED_NODEID 消息

RESP_NEED_NODEID 消息格式为：
`<1-byte message_id = 0x20><6-byte canbus_uuid><1-byte set_klipper_nodeid = 0x01>`

## 数据数据包

通过 CMD_SET_KLIPPER_NODEID 命令被分配了 nodeid 的微控制器
可以发送和接收数据包。

使用节点接收 CAN 总线 ID 的消息中的数据包数据
(`canbus_nodeid * 2 + 256`) 简单地被附加到缓冲区，
当找到完整的 [mcu 协议消息](Protocol.md) 时，其内容被解析和处理。
数据被视为字节流——Kalico 消息块的开始不需要与
CAN 总线数据包的开始对齐。

类似地，mcu 协议消息响应通过将消息数据复制到一个或多个
具有节点传输 CAN 总线 ID 的数据包中，从微控制器发送到主机
(`canbus_nodeid * 2 + 256 + 1`)。