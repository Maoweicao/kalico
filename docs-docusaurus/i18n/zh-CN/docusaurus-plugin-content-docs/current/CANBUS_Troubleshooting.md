# CAN 总线故障排除

本文档提供了在使用 [Kalico 与 CAN 总线](CANBUS.md) 时排除通信问题的信息。

## 验证 CAN 总线接线

排除通信问题的第一步是验证 CAN 总线接线。

请确保 CAN 总线上恰好有两个 120 欧姆 [终端电阻](CANBUS.md#terminating-resistors)。如果电阻安装不正确，则消息可能完全无法发送，或者连接可能出现间歇性不稳定。

CANH 和 CANL 总线接线应相互绞合。至少，接线应每隔几厘米绞合一次。避免将 CANH 和 CANL 接线与电源线绞合在一起，并确保与 CANH 和 CANL 接线平行的电源线具有相同的绞合量。

验证 CAN 总线接线上的所有插头和线缆压接是否完全牢固。打印机打印头的移动可能会晃动 CAN 总线接线，导致不良的线缆压接或未固定的插头造成间歇性通信错误。

## 检查 bytes_invalid 计数器递增

Kalico 日志文件在打印机活动时每秒报告一行 `Stats`。这些"Stats"行将为每个微控制器提供一个 `bytes_invalid` 计数器。在正常打印机操作期间，此计数器不应递增（在 RESTART 之后计数器为非零是正常的，如果计数器每月左右递增一次也不用担心）。如果 CAN 总线微控制器上的此计数器在正常打印期间递增（每几小时或更频繁地递增一次），则表明存在严重问题。

CAN 总线连接上的递增 `bytes_invalid` 是 CAN 总线上消息重新排序的症状。如果看到此问题，请确保：
* 使用 Linux 内核版本 6.6.0 或更高版本。
* 如果使用运行 candlelight 固件的 USB-to-CANBUS 适配器，请使用 candleLight_fw v2.0 或更高版本。
* 如果使用 Klipper 的 USB-to-CANBUS 桥接模式，请确保桥接节点刷写了 Klipper v0.12.0 或更高版本。

消息重新排序是一个必须修复的严重问题。它会导致不稳定的行为，并可能导致打印任何部分出现令人困惑的错误。递增的 `bytes_invalid` 不是由接线或类似硬件问题引起的，只能通过识别和更新有问题的软件来修复。

旧版本的 Linux 内核在 gs_usb canbus 驱动代码中存在一个 bug，可能导致 CAN 总线数据包重新排序。该问题被认为已在 [Linux commit 24bc41b4](https://github.com/torvalds/linux/commit/24bc41b4558347672a3db61009c339b1f5692169) 中修复，该版本在 v6.6.0 中发布。在某些情况下，旧版本的 Linux 可能不会显示此问题（取决于硬件中断的配置方式），但如果出现问题，建议的解决方案是升级到较新的内核。

旧版本的 candlelight 固件可能会重新排序 CAN 总线数据包，该问题被认为已在 [candlelight_fw commit 8b3a7b45](https://github.com/candle-usb/candleLight_fw/commit/8b3a7b4565a3c9521b762b154c94c72c5acb2bcf) 中修复。

旧版本的 Klipper USB-to-CANBUS 桥接代码可能会错误地丢弃 CAN 总线消息。这不如重新排序消息严重，但仍应修复。该问题被认为已在 [Klipper PR #6175](https://github.com/Klipper3d/klipper/pull/6175) 中修复。

## 使用适当的 txqueuelen 设置

Kalico 代码使用 Linux 内核来管理 CAN 总线流量。默认情况下，内核只会排队 10 个 CAN 发送数据包。建议将 can0 设备配置为 `txqueuelen 128` 以增加该大小。

如果 Kalico 发送一个数据包而 Linux 已经填满了所有发送队列空间，则 Linux 将丢弃该数据包，并且 Kalico 日志中会出现类似以下的消息：
```
Got error -1 in can write: (105)No buffer space available
```
Kalico 会作为其正常应用级消息重传系统的一部分自动重传丢失的消息。因此，此日志消息是一个警告，不表示不可恢复的错误。

如果发生完整的 CAN 总线故障（例如 CAN 线缆断裂），则 Linux 将无法在 CAN 总线上传输任何消息，并且通常会在 Kalico 日志中找到上述消息。在这种情况下，日志消息是更大问题（无法传输任何消息）的症状，与 Linux `txqueuelen` 没有直接关系。

可以通过运行 Linux 命令 `ip link show can0` 来检查当前队列大小。它应该报告一堆文本，包括 `qlen 128` 片段。如果看到类似 `qlen 10` 的内容，则表示 CAN 设备未正确配置。

不建议使用明显大于 128 的 `txqueuelen`。以 1000000 频率运行的 CAN 总线通常需要约 120us 来传输一个 CAN 数据包。因此，128 个数据包的队列可能需要约 15-20ms 来排空。明显更大的队列可能导致消息往返时间出现过度峰值，这可能导致不可恢复的错误。换句话说，Kalico 的应用重传系统在不必等待 Linux 排空可能过时的过多数据队列时更加健壮。这类似于互联网路由器上的 [bufferbloat](https://en.wikipedia.org/wiki/Bufferbloat) 问题。

在正常情况下，Kalico 可能每个 MCU 使用约 25 个队列槽位 - 通常仅在重传期间使用更多槽位。（具体来说，Kalico 主机可能在从该 MCU 接收确认之前向每个 Kalico MCU 发送最多 192 字节。）如果单个 CAN 总线上有 5 个或更多 Kalico MCU，则可能需要将 `txqueuelen` 增加到推荐值 128 以上。但是，如上所述，在选择新值时应小心，以避免过多的往返时间延迟。

## 获取 candump 日志

发送到和从微控制器发出的 CAN 总线消息由 Linux 内核处理。可以从内核捕获这些消息用于调试目的。这些消息的日志可能在诊断中很有用。

Linux [can-utils](https://github.com/linux-can/can-utils) 工具提供捕获软件。通常通过运行以下命令在机器上安装：
```
sudo apt-get update && sudo apt-get install can-utils
```

安装后，可以使用以下命令捕获接口上的所有 CAN 总线消息：
```
candump -tz -Ddex can0,#FFFFFFFF > mycanlog
```

可以查看生成的日志文件（上面示例中的 `mycanlog`）以查看 Kalico 发送和接收的每个原始 CAN 总线消息。理解这些消息的内容可能需要了解 Kalico 的 [CANBUS 协议](CANBUS_protocol.md) 和 Kalico 的 [MCU 命令](MCU_Commands.md) 的底层知识。

### 在 candump 日志中解析 Kalico 消息

可以使用 `parsecandump.py` 工具解析 candump 日志中包含的 Kalico 底层微控制器消息。使用此工具是一个高级主题，需要了解 Kalico [MCU 命令](MCU_Commands.md)。例如：
```
./scripts/parsecandump.py mycanlog 108 ./out/klipper.dict
```

此工具产生类似于 [parsedump 工具](Debugging.md#translating-gcode-files-to-micro-controller-commands) 的输出。有关生成 Kalico 微控制器数据字典的信息，请参见该工具的文档。

在上面的示例中，`108` 是 [CAN 总线 id](CANBUS_protocol.md#micro-controller-id-assignment)。它是一个十六进制数字。Kalico 将 id `108` 分配给第一个微控制器。如果 CAN 总线上有多个微控制器，则第二个微控制器为 `10a`，第三个为 `10c`，依此类推。

candump 日志必须使用 `-tz -Ddex` 命令行参数生成（例如：`candump -tz -Ddex can0,#FFFFFFFF`）才能使用 `parsecandump.py` 工具。

## 在 CAN 总线接线上使用逻辑分析仪

[Sigrok Pulseview](https://sigrok.org/wiki/PulseView) 软件和低成本 [逻辑分析仪](https://en.wikipedia.org/wiki/Logic_analyzer) 可用于诊断 CAN 总线信号。这是一个高级主题，可能只对专家感兴趣。

通常可以找到低于 15 美元（2023 年美国价格）的"USB 逻辑分析仪"。这些设备通常被列为"Saleae 逻辑克隆"或"24MHz 8 通道 USB 逻辑分析仪"。

![pulseview-canbus](/img/pulseview-canbus.png)

上图是使用 Pulseview 和"Saleae 克隆"逻辑分析仪时拍摄的。Sigrok 和 Pulseview 软件安装在台式机上（如果单独打包，还要安装"fx2lafw"固件）。逻辑分析仪上的 CH0 引脚连接到 CAN Rx 线，CH1 引脚连接到 CAN Tx 引脚，GND 连接到 GND。Pulseview 配置为仅显示 D0 和 D1 线（顶部工具栏中间的红色"探针"图标）。采样数设置为 500 万（顶部工具栏），采样率设置为 24Mhz（顶部工具栏）。添加了 CAN 解码器（顶部工具栏右侧的黄绿色"气泡图标"）。D0 通道标记为 RX 并设置为在下降沿触发（点击左侧黑色 D0 标签）。D1 通道标记为 TX（点击左侧棕色 D1 标签）。CAN 解码器配置为 1Mbit 速率（点击左侧绿色 CAN 标签）。CAN 解码器移动到显示顶部（点击并拖动绿色 CAN 标签）。最后，开始捕获（点击左上角的"Run"），并在 CAN 总线上传输数据包（`cansend can0 123#121212121212`）。

逻辑分析仪提供了一个独立的工具来捕获数据包和验证位时序。
