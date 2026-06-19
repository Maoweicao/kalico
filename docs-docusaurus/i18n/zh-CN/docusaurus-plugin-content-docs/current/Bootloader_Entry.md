# 引导加载程序入口

Kalico 可以通过以下方式之一指示重启进入[引导加载程序](Bootloaders.md)：

## 请求引导加载程序

### 虚拟串口

如果正在使用虚拟（USB-ACM）串口，在 1200 波特率下脉冲 DTR 将请求引导加载程序。

#### Python（使用 `flash_usb`）

使用 python 进入引导加载程序（使用 `flash_usb`）：

```shell
> cd klipper/scripts
> python3 -c 'import flash_usb as u; u.enter_bootloader("<DEVICE>")'
Entering bootloader on <DEVICE>
```

其中 `<DEVICE>` 是你的串口设备，例如 `/dev/serial.by-id/usb-Klipper[...]` 或 `/dev/ttyACM0`

请注意，如果此操作失败，将不会打印任何输出，成功由打印 `Entering bootloader on <DEVICE>` 表示。

#### Picocom

```shell
picocom -b 1200 <DEVICE>
<Ctrl-A><Ctrl-P>
```

其中 `<DEVICE>` 是你的串口设备，例如 `/dev/serial.by-id/usb-Klipper[...]` 或 `/dev/ttyACM0`

`<Ctrl-A><Ctrl-P>` 表示按住 `Ctrl`，按下并释放 `a`，按下并释放 `p`，然后释放 `Ctrl`

### 物理串口

如果 MCU 上正在使用物理串口（即使使用 USB 串口适配器连接到它），发送字符串 `<SPACE><FS><SPACE>Request Serial Bootloader!!<SPACE>~` 将请求引导加载程序。

`<SPACE>` 是 ASCII 空格字符，0x20。

`<FS>` 是 ASCII 文件分隔符，0x1c。

请注意，根据 [MCU 协议](Protocol.md#micro-controller-interface)，这不是一条有效消息，但同步字符（`~`）仍然有效。

因为此消息必须是接收到的"块"中唯一的内容，如果之前有其他工具正在访问串口，添加额外的同步字符可以提高可靠性。

#### Shell

```shell
stty <BAUD> < /dev/<DEVICE>
echo $'~ \x1c Request Serial Bootloader!! ~' >> /dev/<DEVICE>
```

其中 `<DEVICE>` 是你的串口，例如 `/dev/ttyS0` 或 `/dev/serial/by-id/gpio-serial2`，

`<BAUD>` 是串口的波特率，例如 `115200`。

### CANBUS

如果正在使用 CANBUS，特殊的[管理消息](CANBUS_protocol.md#admin-messages)将请求引导加载程序。即使设备已有 nodeid，此消息也会被尊重，并且如果 MCU 已关闭，它也会被处理。

此方法也适用于在 [CANBridge](CANBUS.md#usb-to-can-bus-bridge-mode) 模式下运行的设备。

#### Katapult 的 flashtool.py

```shell
python3 ./katapult/scripts/flashtool.py -i <CAN_IFACE> -u <UUID> -r
```

其中 `<CAN_IFACE>` 是要使用的 CAN 接口。如果使用 `can0`，可以省略 `-i` 和 `<CAN_IFACE>`。

`<UUID>` 是你的 CAN 设备的 UUID。

有关查找设备 CAN UUID 的信息，请参阅 [CANBUS 文档](CANBUS.md#finding-the-canbus_uuid-for-new-micro-controllers)。

## 进入引导加载程序

当 Kalico 收到上述引导加载程序请求之一时：

如果 Katapult（前身为 CANBoot）可用，Kalico 将请求 Katapult 在下次启动时保持活动状态，然后重置 MCU（从而进入 Katapult）。

如果 Katapult 不可用，Kalico 将尝试进入平台特定的引导加载程序，例如 STM32 的 DFU 模式（[参见说明](#stm32-dfu-warning)）。

简而言之，Kalico 将重启到已安装的 Katapult，然后如果可用则进入硬件特定的引导加载程序。

有关各平台上特定引导加载程序的详细信息，请参阅[引导加载程序](Bootloaders.md)。

## 注意事项

### STM32 DFU 警告

请注意，在某些板上（如 Octopus Pro v1），进入 DFU 模式可能导致不期望的操作（例如在 DFU 模式下为加热器供电）。使用 DFU 模式时，建议断开加热器并防止不期望的操作。有关更多详细信息，请参阅你的板的文档。
