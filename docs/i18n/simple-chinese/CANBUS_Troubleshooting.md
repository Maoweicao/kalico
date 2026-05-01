# CANBUS 故障排查

本文档提供有关使用 [Kalico 和 CAN 总线](CANBUS.md) 时
通信问题的故障排查信息。

## 验证 CAN 总线接线

故障排查通信问题的第一步是验证 CAN 总线接线。

确保 CAN 总线上恰好有两个 120 欧姆的[终端电阻](CANBUS.md#terminating-resistors)。
如果电阻未正确安装，则消息可能无法发送，或连接可能出现偶发不稳定。

CANH 和 CANL 总线接线应相互缠绕。至少，接线应每隔几厘米
有一处缠绕。避免将 CANH 和 CANL 接线缠绕在电源线周围，
并确保与 CANH 和 CANL 电线平行的电源线不具有相同数量的缠绕。

验证 CAN 总线接线上的所有插头和线夹都已完全固定。
打印机工具头的运动可能会使 CAN 总线接线松动，导致
接线不好或未固定的插头导致间歇性通信错误。

## 检查递增的 bytes_invalid 计数器

当打印机活跃时，Kalico 日志文件每秒报告一条 `Stats` 行。
这些"Stats"行将为每个微控制器包含一个 `bytes_invalid` 计数器。
在正常打印机操作期间此计数器不应递增（在 RESTART 后计数器为非零
是正常的，每月递增一次左右不是问题）。如果此计数器在正常打印
期间在 CAN 总线微控制器上递增（每隔几小时或更频繁地递增），
则表示存在严重问题。

CAN 总线连接上递增的 `bytes_invalid` 是 CAN 总线上消息乱序的症状。
如果出现这种情况，请确保：
* 使用 Linux 内核版本 6.6.0 或更高版本。
* 如果使用运行 candlelight 固件的 USB 到 CANBUS 适配器，
  请使用 v2.0 或更高版本的 candleLight_fw。
* 如果使用 Klipper 的 USB 到 CANBUS 桥接模式，请确保
  桥接节点使用 Klipper v0.12.0 或更高版本刷入。

消息乱序是一个严重问题，必须修复。它会导致不稳定行为，
并可能在打印的任何部分导致令人困惑的错误。递增的 `bytes_invalid`
不是由接线或类似硬件问题引起的，只能通过识别和更新有问题的软件来修复。

较旧版本的 Linux 内核在 gs_usb canbus 驱动程序代码中有一个 bug
可能导致 canbus 数据包乱序。该问题被认为已在
[Linux commit 24bc41b4](https://github.com/torvalds/linux/commit/24bc41b4558347672a3db61009c339b1f5692169)
中修复，该 commit 在 v6.6.0 中发布。在某些情况下，
较旧的 Linux 版本可能不会显示问题（由于硬件中断的配置方式），
但是如果出现问题，建议的解决方案是升级到更新的内核。

较旧版本的 candlelight 固件可能会导致 canbus 数据包乱序，
该问题被认为已在
[candlelight_fw commit 8b3a7b45](https://github.com/candle-usb/candleLight_fw/commit/8b3a7b4565a3c9521b762b154c94c72c5acb2bcf)
中修复。

较旧版本的 Klipper USB 到 CANBUS 桥接代码可能会错误地丢弃 canbus 消息。
这不如消息乱序那么严重，但仍应修复。被认为已在
[Klipper PR #6175](https://github.com/Klipper3d/klipper/pull/6175) 中修复。

## 使用适当的 txqueuelen 设置

Kalico 代码使用 Linux 内核来管理 CAN 总线流量。
默认情况下，内核只排队 10 个 CAN 传输数据包。建议
[配置 can0 设备](CANBUS.md#host-hardware) 使用
`txqueuelen 128` 来增加该大小。

如果 Kalico 传输一个数据包而 Linux 已填满其所有传输队列空间，
则 Linux 将丢弃该数据包，Kalico 日志中将出现如下消息：
```
Got error -1 in can write: (105)No buffer space available
```

Kalico 将自动重新传输丢失的消息，作为其正常应用级消息重新传输系统的一部分。
因此，此日志消息是一个警告，它不表示不可恢复的错误。

如果发生完整的 CAN 总线故障（例如 CAN 电线断裂），
则 Linux 将无法在 CAN 总线上传输任何消息，通常会在 Kalico 日志中
找到上述消息。在这种情况下，日志消息是更大问题的症状
（无法传输任何消息），与 Linux `txqueuelen` 无关。

可以通过运行 Linux 命令 `ip link show can0` 来检查当前队列大小。
它应报告大量文本，包括片段 `qlen 128`。如果看到类似 `qlen 10` 的内容，
则表示 CAN 设备未正确配置。

不建议使用大小远大于 128 的 `txqueuelen`。
CAN 总线以 1000000 频率运行通常需要约 120us 来传输一个 CAN 数据包。
因此，128 个数据包的队列可能需要约 15-20ms 才能排空。
更大的队列可能导致消息往返时间出现过度尖峰，这可能导致不可恢复的错误。
换句话说，如果 Kalico 不必等待 Linux 排空可能过时数据的过大队列，
其应用重新传输系统会更加稳健。这类似于
[bufferbloat](https://en.wikipedia.org/wiki/Bufferbloat) 在互联网路由器上的问题。

在正常情况下，Kalico 可能每个 MCU 利用约 25 个队列槽——
通常仅在重新传输期间使用更多槽。（具体来说，Kalico 主机最多可以
向每个 Kalico MCU 传输 192 字节，然后才能从该 MCU 收到确认。）
如果单个 CAN 总线上有 5 个或更多 Kalico MCU，则可能有必要
将 `txqueuelen` 增加到推荐值 128 以上。但是，如上所述，
选择新值时应小心以避免过度的往返时间延迟。

## 获取 candump 日志

发送到和来自微控制器的 CAN 总线消息由 Linux 内核处理。
可以从内核捕获这些消息以进行调试。这些消息的日志可能对诊断有用。

Linux [can-utils](https://github.com/linux-can/can-utils) 工具
提供了捕获软件。它通常通过运行以下命令安装在计算机上：
```
sudo apt-get update && sudo apt-get install can-utils
```

安装后，可以使用以下命令获取接口上所有 CAN 总线消息的捕获：
```
candump -tz -Ddex can0,#FFFFFFFF > mycanlog
```

可以查看生成的日志文件（上面示例中的 `mycanlog`）以查看
Kalico 发送和接收的每个原始 CAN 总线消息。理解这些消息的内容
可能需要对 Kalico 的 [CANBUS 协议](CANBUS_protocol.md)
和 Kalico 的 [MCU 命令](MCU_Commands.md) 的深入了解。

### 解析 candump 日志中的 Kalico 消息

可以使用 `parsecandump.py` 工具解析 candump 日志中包含的
低级 Kalico 微控制器消息。使用此工具是一个高级主题，
需要了解 Kalico [MCU 命令](MCU_Commands.md)。例如：
```
./scripts/parsecandump.py mycanlog 108 ./out/klipper.dict
```

此工具生成的输出类似于 [parsedump 工具](Debugging.md#translating-gcode-files-to-micro-controller-commands)。
有关生成 Kalico 微控制器数据字典的信息，请参阅该工具的文档。

在上面的示例中，`108` 是 [CAN 总线 ID](CANBUS_protocol.md#micro-controller-id-assignment)。
这是一个十六进制数。ID `108` 由 Kalico 分配给第一个微控制器。
如果 CAN 总线上有多个微控制器，则第二个微控制器将是 `10a`，
第三个将是 `10c`，以此类推。

candump 日志必须使用 `-tz -Ddex` 命令行参数生成
（例如：`candump -tz -Ddex can0,#FFFFFFFF`）才能使用 `parsecandump.py` 工具。

## 在 canbus 接线上使用逻辑分析仪

[Sigrok Pulseview](https://sigrok.org/wiki/PulseView) 软件
加上低成本的 [逻辑分析仪](https://en.wikipedia.org/wiki/Logic_analyzer)
可用于诊断 CAN 总线信号。这是一个高级主题，可能只对专家感兴趣。

经常可以找到价格低于 15 美元的"USB 逻辑分析仪"（截至 2023 年的美国定价）。
这些设备通常列为"Saleae logic 克隆"或"24MHz 8 通道 USB 逻辑分析仪"。

![pulseview-canbus](img/pulseview-canbus.png)

上面的图片是使用 Pulseview 和"Saleae 克隆"逻辑分析仪拍摄的。
Sigrok 和 Pulseview 软件安装在台式计算机上
（如果单独打包，还应安装"fx2lafw"固件）。
逻辑分析仪上的 CH0 引脚连接到 CAN Rx 线，CH1 引脚连接到 CAN Tx 引脚，
GND 连接到 GND。Pulseview 配置为仅显示 D0 和 D1 线（红色"探针"图标中心顶部工具栏）。
样本数设置为 500 万（顶部工具栏），采样率设置为 24Mhz（顶部工具栏）。
添加了 CAN 解码器（黄色和绿色"气泡图标"右上角工具栏）。
D0 通道标记为 RX 并设置为在下降沿触发（单击左边黑色 D0 标签）。
D1 通道标记为 TX（单击棕色 D1 标签）。CAN 解码器配置为 1Mbit 速率
（单击左边绿色 CAN 标签）。CAN 解码器移到显示顶部（单击并拖动绿色 CAN 标签）。
最后，启动了捕获（单击左上角"Run"），在 CAN 总线上传输了一个数据包
(`cansend can0 123#121212121212`)。

逻辑分析仪提供了一个独立工具来捕获数据包并验证比特时序。