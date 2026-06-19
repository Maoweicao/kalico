# CANBUS

本文档介绍 Kalico 的 CAN 总线支持。

## 设备硬件

Kalico 目前支持 stm32、SAME5x 和 rp2040 芯片上的 CAN。此外，微控制器芯片必须位于具有 CAN 收发器的板上。

要编译 CAN，请运行 `make menuconfig` 并选择"CAN bus"作为通信接口。最后，编译微控制器代码并将其刷写到目标板。

## 主机硬件

为了使用 CAN 总线，需要有一个主机适配器。建议使用"USB 转 CAN 适配器"。有许多不同制造商的不同 USB 转 CAN 适配器可用。选择时，我们建议验证是否可以更新其固件。（不幸的是，我们发现一些 USB 适配器运行有缺陷的固件并被锁定，因此请在购买前验证。）寻找可以直接运行 Kalico 的适配器（在其"USB 转 CAN 桥接模式"下）或运行 [candlelight 固件](https://github.com/candle-usb/candleLight_fw)的适配器。

还需要配置主机操作系统以使用适配器。这通常通过创建一个名为 `/etc/network/interfaces.d/can0` 的新文件来完成，内容如下：
```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 128
```

## 终端电阻

CAN 总线应在 CANH 和 CANL 线之间有两个 120 欧姆电阻。理想情况下，一个电阻位于总线的每一端。

请注意，某些设备具有内置的 120 欧姆电阻，无法轻松移除。某些设备根本不包含电阻。其他设备具有选择电阻的机制（通常通过连接"引脚跳线"）。务必检查 CAN 总线上所有设备的原理图，以验证总线上有且仅有两个 120 欧姆电阻。

要测试电阻是否正确，可以断开打印机电源并使用万用表检查 CANH 和 CANL 线之间的电阻——正确接线的 CAN 总线应报告约 60 欧姆。

## ⚠️ 查找新微控制器的 canbus_uuid

CAN 总线上的每个微控制器都根据编码在每个微控制器中的工厂芯片标识符分配一个唯一的 ID。要查找每个微控制器设备 ID，请确保硬件已正确供电和接线，然后运行：
```
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

如果检测到 CAN 设备，上述命令将报告如下行：
```
Found canbus_uuid=11aa22bb33cc, Application: Klipper, Unassigned
Found canbus_uuid=11aa22bb33cc, Application: Kalico, Assigned: 77
```

每个设备都有一个唯一的标识符。在上面的示例中，`11aa22bb33cc` 是微控制器的"canbus_uuid"。

请注意，`canbus_query.py` 工具只会报告未初始化的设备——如果 Kalico（或类似工具）配置了该设备，它将不再出现在列表中。

⚠️ 请注意，只有使用 Kalico 固件刷写的设备在分配设备节点 ID 后才会响应。使用 Klipper 固件的设备在配置后将不再出现在列表中。

## 配置 Kalico

更新 Kalico [mcu 配置](Config_Reference.md#mcu)以使用 CAN 总线与设备通信——例如：
```
[mcu my_can_mcu]
canbus_uuid: 11aa22bb33cc
```

## USB 转 CAN 总线桥接模式

某些微控制器支持在 Kalico 的"make menuconfig"期间选择"USB 转 CAN 总线桥接"模式。此模式可能允许将微控制器同时用作"USB 转 CAN 总线适配器"和 Kalico 节点。

当 Kalico 使用此模式时，微控制器在 Linux 下显示为"USB CAN 总线适配器"。"Kalico 桥接 mcu"本身将显示为在此 CAN 总线上——它可以通过 `canbus_query.py` 识别，并且必须像其他 CAN 总线 Kalico 节点一样配置。

使用此模式的一些重要注意事项：

* 需要在 Linux 中配置 `can0`（或类似）接口才能与总线通信。但是，Kalico 会忽略 Linux CAN 总线速度和 CAN 总线位定时选项。目前，CAN 总线频率在"make menuconfig"期间指定，而 Linux 中指定的总线速度会被忽略。

* 每当"桥接 mcu"重置时，Linux 将禁用相应的 `can0` 接口。为确保正确处理 FIRMWARE_RESTART 和 RESTART 命令，建议在 `/etc/network/interfaces.d/can0` 文件中使用 `allow-hotplug`。例如：
```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 128
```

* "桥接 mcu"实际上不在 CAN 总线上。发送到和从桥接 mcu 接收的消息不会被可能在 CAN 总线上的其他适配器看到。

* "桥接 mcu"本身和 CAN 总线上所有设备的可用带宽实际上受 CAN 总线频率限制。因此，建议在使用"USB 转 CAN 总线桥接模式"时使用 1000000 的 CAN 总线频率。

  即使在 1000000 的 CAN 总线频率下，如果 XY 步进器和加速度计都通过单个"USB 转 CAN 总线"接口通信，可能也没有足够的带宽来运行 `SHAPER_CALIBRATE` 测试。

* USB 转 CAN 桥接板不会显示为 USB 串口设备，运行 `ls /dev/serial/by-id` 时不会显示，并且不能在 Kalico 的 printer.cfg 文件中使用 `serial:` 参数配置。桥接板显示为"USB CAN 适配器"，在 printer.cfg 中配置为 [CAN 节点](#configuring-kalico)。

## 故障排除提示

请参阅 [CAN 总线故障排除](CANBUS_Troubleshooting.md)文档。
