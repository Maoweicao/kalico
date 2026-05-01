# 引导加载程序入口

可以通过以下方式之一将 Kalico 指示重启进入[引导加载程序](Bootloaders.md)：

## 请求引导加载程序

### 虚拟串行

如果使用虚拟（USB-ACM）串行端口，在 1200 波特时脉冲 DTR 将请求引导加载程序。

#### Python（带 `flash_usb`）

使用 Python 进入引导加载程序（使用 `flash_usb`）：

```shell
> cd klipper/scripts
> python3 -c 'import flash_usb as u; u.enter_bootloader("<DEVICE>")'
Entering bootloader on <DEVICE>
```

其中 `<DEVICE>` 是串行设备，例如
`/dev/serial.by-id/usb-Klipper[...]` 或 `/dev/ttyACM0`

注意如果失败，将不打印任何输出，成功由打印 `Entering bootloader on <DEVICE>` 表示。

#### Picocom

```shell
picocom -b 1200 <DEVICE>
<Ctrl-A><Ctrl-P>
```

其中 `<DEVICE>` 是串行设备，例如
`/dev/serial.by-id/usb-Klipper[...]` 或 `/dev/ttyACM0`

`<Ctrl-A><Ctrl-P>` 意味着
按住 `Ctrl`，按下并释放 `a`，按下并释放 `p`，然后释放 `Ctrl`

### 物理串行

如果在 MCU（微控制器）上使用物理串行端口（即使使用 USB 串行适配器连接到它），发送字符串
`<SPACE><FS><SPACE>Request Serial Bootloader!!<SPACE>~` 请求引导加载程序。

`<SPACE>` 是 ASCII 字面空格，0x20。

`<FS>` 是 ASCII 文件分隔符，
0x1c。

注意这不是根据[MCU 协议](Protocol.md#micro-controller-interface)的有效消息，但仍然尊重同步字符（`~`）。

由于此消息必须是接收它的"块"中的唯一内容，因此在前面添加额外同步字符可以增加可靠性，如果其他工具以前访问过串行端口。

#### Shell

```shell
stty <BAUD> < /dev/<DEVICE>
echo $'~ \x1c Request Serial Bootloader!! ~' >> /dev/<DEVICE>
```

其中 `<DEVICE>` 是串行端口，例如 `/dev/ttyS0` 或
`/dev/serial/by-id/gpio-serial2`，并且

`<BAUD>` 是串行端口的波特率，例如 `115200`。

### CANBUS

如果使用 CANBUS，特殊的[管理员消息](CANBUS_protocol.md#admin-messages)将请求引导加载程序。即使设备已经有 nodeid，此消息也会被尊重，如果 mcu 关闭也会被处理。

此方法也适用于在[CANBridge](CANBUS.md#usb-to-can-bus-bridge-mode)模式下运行的设备。

#### Katapult 的 flashtool.py

```shell
python3 ./katapult/scripts/flashtool.py -i <CAN_IFACE> -u <UUID> -r
```

其中 `<CAN_IFACE>` 是要使用的 CAN 接口。如果使用 `can0`，则可以省略 `-i` 和 `<CAN_IFACE>`。

`<UUID>` 是 CAN 设备的 UUID。

请参阅[CANBUS 文档](CANBUS.md#finding-the-canbus_uuid-for-new-micro-controllers)了解有关查找设备 CAN UUID 的信息。

## 进入引导加载程序

当 Kalico 接收到上述任何引导加载程序请求时：

如果 Katapult（以前称为 CANBoot）可用，Kalico 将请求 Katapult 在下次启动时保持活动，然后重置 MCU（因此进入 Katapult）。

如果 Katapult 不可用，Kalico 将尝试进入平台特定的引导加载程序，例如 STM32 的 DFU 模式（[参见注意](#stm32-dfu-warning)）。

简言之，Kalico 将重启到 Katapult（如果已安装），然后是硬件特定的引导加载程序（如果可用）。

有关各种平台上特定引导加载程序的详细信息，请参阅[引导加载程序](Bootloaders.md)

## 注意

### STM32 DFU 警告

请注意，在某些板上（如 Octopus Pro v1），进入 DFU 模式可能会导致不期望的操作（例如在 DFU 模式下为加热器供电）。建议在使用 DFU 模式时断开加热器的连接，并以其他方式防止不期望的操作。有关详细信息，请咨询板的文档。