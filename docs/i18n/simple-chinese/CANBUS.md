# CANBUS

本文档描述了 Kalico 的 CAN 总线支持。

## 设备硬件

Kalico 目前支持在 stm32、SAME5x 和 rp2040 芯片上使用 CAN。
此外，微控制器 (MCU) 芯片必须在具有 CAN 收发器的电路板上。

要编译 CAN 支持，请运行 `make menuconfig` 并选择"CAN bus"作为
通信接口。最后，编译微控制器代码并将其刷入目标电路板。

## 主机硬件

要使用 CAN 总线，需要有主机适配器。
建议使用"USB 到 CAN 适配器"。市面上有许多来自不同制造商的
USB 到 CAN 适配器。选择时，建议验证其固件是否可以更新。
（不幸的是，我们发现某些 USB 适配器运行有缺陷的固件且被锁定，
所以请在购买前验证。）寻找能够直接运行 Kalico 的适配器
（在其"USB 到 CAN 桥接模式"下）或者运行 
[candlelight 固件](https://github.com/candle-usb/candleLight_fw) 的适配器。

还需要配置主机操作系统以使用该适配器。这通常通过创建一个名为
`/etc/network/interfaces.d/can0` 的新文件并包含以下内容来完成：
```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 128
```

## 终端电阻

CAN 总线应在 CANH 和 CANL 电线之间有两个 120 欧姆的电阻。
理想情况下，总线的每一端各有一个电阻。

请注意，某些设备内置了 120 欧姆电阻，无法轻易移除。
某些设备根本没有电阻。其他设备有选择电阻的机制（通常通过连接"跳线"）。
请务必检查 CAN 总线上所有设备的原理图，以验证总线上有且仅有两个 120 欧姆的电阻。

要测试电阻是否正确，可以断电打印机，然后使用万用表检查 CANH 和 CANL
电线之间的电阻——在正确接线的 CAN 总线上应显示约 60 欧姆。

## ⚠️ 查找新微控制器的 canbus_uuid

CAN 总线上的每个微控制器都被分配一个基于编码在每个微控制器中的
工厂芯片标识符的唯一 ID。要查找每个微控制器设备 ID，请确保硬件
已通电且接线正确，然后运行：
```
~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0
```

如果检测到 CAN 设备，上述命令将报告如下所示的行：
```
Found canbus_uuid=11aa22bb33cc, Application: Klipper, Unassigned
Found canbus_uuid=11aa22bb33cc, Application: Kalico, Assigned: 77
```

每个设备将有一个唯一标识符。在上面的示例中，
`11aa22bb33cc` 是微控制器的"canbus_uuid"。

请注意，`canbus_query.py` 工具仅报告未初始化的设备——如果 Kalico
（或类似工具）配置了设备，它将不再出现在列表中。

⚠️ 请注意，只有使用 Kalico 固件刷入的设备在分配了设备节点 ID 后才会
响应。使用 Klipper 固件的设备一旦配置就不再出现在列表中

## 配置 Kalico

更新 Kalico [mcu 配置](Config_Reference.md#mcu)以使用
CAN 总线与设备通信——例如：
```
[mcu my_can_mcu]
canbus_uuid: 11aa22bb33cc
```

## USB 到 CAN 总线桥接模式

某些微控制器支持在 Kalico 的"make menuconfig"期间选择"USB 到 CAN 总线桥接"模式。
此模式可能允许将微控制器用作"USB 到 CAN 总线适配器"和 Kalico 节点。

当 Kalico 使用此模式时，微控制器在 Linux 下显示为"USB CAN 总线适配器"。
"Kalico 桥接 mcu"本身将显示为在此 CAN 总线上——可以通过
`canbus_query.py` 识别它，并且必须像其他 CAN 总线 Kalico
节点一样配置它。

使用此模式时的一些重要注意事项：

* 需要在 Linux 中配置 `can0`（或类似）接口以与总线通信。
  但是，Linux CAN 总线速度和 CAN 总线比特时序选项会被 Kalico 忽略。
  目前，CAN 总线频率是在"make menuconfig"期间指定的，
  Linux 中指定的总线速度会被忽略。

* 每当"桥接 mcu"重置时，Linux 将禁用相应的 `can0` 接口。
  为确保正确处理 FIRMWARE_RESTART 和 RESTART 命令，
  建议在 `/etc/network/interfaces.d/can0` 文件中使用 `allow-hotplug`。
  例如：
```
allow-hotplug can0
iface can0 can static
    bitrate 1000000
    up ip link set $IFACE txqueuelen 128
```

* "桥接 mcu"实际上不在 CAN 总线上。来自和发往桥接 mcu 的消息
  不会被可能在 CAN 总线上的其他适配器看到。

* 可用于"桥接 mcu"本身和 CAN 总线上所有设备的带宽
  实际上受到 CAN 总线频率的限制。因此，建议在使用
  "USB 到 CAN 总线桥接模式"时使用 CAN 总线频率 1000000。

  即使 CAN 总线频率为 1000000，如果 XY 步进电机和加速度计
  都通过单个"USB 到 CAN 总线"接口通信，也可能没有足够的带宽
  来运行 `SHAPER_CALIBRATE` 测试。

* USB 到 CAN 桥接电路板不会显示为 USB 串行设备，
  它不会在运行 `ls /dev/serial/by-id` 时出现，
  并且不能在 Kalico 的 printer.cfg 文件中使用 `serial:` 参数配置。
  桥接电路板显示为"USB CAN 适配器"，在 printer.cfg 中配置为 [CAN 节点](#configuring-kalico)。

## 故障排查技巧

请参阅 [CAN 总线故障排查](CANBUS_Troubleshooting.md) 文档。