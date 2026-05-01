# 常见问题

## 我如何向该项目捐赠？

感谢您的支持。有关信息，请参阅 [赞助商页面](Sponsors.md)。

## 我如何计算 rotation_distance 配置参数？

请参阅 [rotation distance 文档](Rotation_Distance.md)。

## 我的串行端口在哪里？

查找 USB 串行端口的常见方法是从主机的 ssh 终端运行 `ls /dev/serial/by-id/*`。它可能会产生类似于以下内容的输出：
```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

在上述命令中找到的名称是稳定的，可以在配置文件中使用它，并在刷新微控制器代码时使用。例如，刷新命令可能看起来类似于：
```
sudo service klipper stop
make flash FLASH_DEVICE=/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
sudo service klipper start
```
更新后的配置可能看起来像：
```
[mcu]
serial: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

务必复制粘贴从上面运行的"ls"命令中找到的名称，因为每台打印机的名称将不同。

如果您使用多个微控制器，它们没有唯一的 id（在带有 CH340 USB 芯片的主板上很常见），则请使用命令 `ls /dev/serial/by-path/*` 按照上述方向进行。

## 当微控制器重新启动时设备更改为 /dev/ttyUSB1

按照 ["我的串行端口在哪里？"](#我的串行端口在哪里) 部分中的指示来防止这种情况发生。

## "make flash"命令不起作用

代码尝试使用每个平台最常见的方法刷新设备。不幸的是，刷新方法存在很多差异，所以"make flash"命令可能不适用于所有主板。

如果您遇到间歇性故障或确实有标准设置，则仔细检查 Kalico 在刷新时未运行（sudo service klipper stop），确保 OctoPrint 未尝试直接连接到设备（打开网页中的"连接"选项卡，如果串行端口设置为设备，则单击"断开连接"），并确保 FLASH_DEVICE 为您的主板正确设置（请参阅 [上面的问题](#我的串行端口在哪里)）。

但是，如果"make flash"对您的主板就是不工作，则您需要手动刷新。查看 [config 目录](../config) 中是否有配置文件，其中包含有关如何刷新设备的具体说明。另外，检查主板制造商的文档以查看它是否描述了如何刷新设备。最后，可能可以使用"avrdude"或"bossac"之类的工具手动刷新设备 - 有关更多信息，请参阅 [引导程序文档](Bootloaders.md)。

## 我如何改变串行波特率？

Kalico 推荐的波特率为 250000。此波特率在 Kalico 支持的所有微控制器主板上都工作良好。如果您找到了在线指南推荐不同的波特率，请忽略该指南的该部分，并继续使用默认值 250000。

如果您想无论如何改变波特率，则新速率需要在微控制器中配置（在 **make menuconfig** 期间），并且更新的代码需要编译并刷新到微控制器。Kalico 打印机 .cfg 文件也需要更新以匹配该波特率（有关详细信息，请参阅 [配置参考](Config_Reference.md#mcu)）。例如：
```
[mcu]
baud: 250000
```

OctoPrint 网页上显示的波特率对内部 Kalico 微控制器波特率没有影响。使用 Kalico 时，始终将 OctoPrint 波特率设置为 250000。

Kalico 微控制器波特率与微控制器引导程序的波特率无关。有关引导程序的更多信息，请参阅 [引导程序文档](Bootloaders.md)。

## 我可以在 Raspberry Pi 3 以外的东西上运行 Kalico 吗？

推荐的硬件是 Raspberry Pi 2、Raspberry Pi 3 或 Raspberry Pi 4。

Kalico 将在 Raspberry Pi 1 和 Raspberry Pi Zero 上运行，但这些主板没有足够的处理能力来很好地运行 OctoPrint。在这些较慢的机器上从 OctoPrint 直接打印时，通常会发生打印停滞。（打印机的移动速度可能快于 OctoPrint 发送移动命令的速度。）如果您无论如何希望在其中一个较慢的主板上运行，请考虑在打印时使用"virtual_sdcard"功能（有关详细信息，请参阅 [配置参考](Config_Reference.md#virtual_sdcard)）。

有关在 Beaglebone 上运行的信息，请参阅 [Beaglebone 特定安装说明](Beaglebone.md)。

Kalico 已在其他机器上运行。Kalico 主机软件仅需要在 Linux（或类似）计算机上运行 Python。但是，如果您希望在不同的机器上运行它，您需要 Linux 管理员知识来为该特定机器安装系统先决条件。有关必要的 Linux 管理步骤的更多信息，请参阅 [install-octopi.sh](../scripts/install-octopi.sh) 脚本。

如果您考虑在低端芯片上运行 Kalico 主机软件，请注意，至少需要具有"双精度浮点"硬件的机器。

如果您考虑在共享通用桌面或服务器级计算机上运行 Kalico 主机软件，请注意 Kalico 有一些实时调度要求。如果在打印期间主计算机也执行密集的通用计算任务（例如碎片整理硬盘、3D 渲染、大量交换等），则可能导致 Kalico 报告打印错误。

注意：如果您未使用 OctoPi 映像，请注意几个 Linux 发行版启用了可能中断串行通信的"ModemManager"（或类似）程序包。（这可能导致 Kalico 报告看似随机的"与 MCU 通信丢失"错误。）如果您在其中一个发行版上安装 Kalico，您可能需要禁用该程序包。

## 我可以在同一主机上运行多个 Kalico 实例吗？

可以在同一主机上运行多个 Kalico 主机软件实例，但这样做需要 Linux 管理员知识。Kalico 安装脚本最终导致以下 Unix 命令运行：
```
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer.cfg -l /tmp/klippy.log
```
只要每个实例有自己的打印机配置文件、自己的日志文件和自己的伪 tty，就可以运行上述命令的多个实例。例如：
```
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer2.cfg -l /tmp/klippy2.log -I /tmp/printer2
```

如果您选择这样做，您需要实现必要的启动、停止和安装脚本（如果有的话）。[install-octopi.sh](../scripts/install-octopi.sh) 脚本和 [klipper-start.sh](../scripts/klipper-start.sh) 脚本可能作为示例有用。

## 我必须使用 OctoPrint 吗？

Kalico 软件不依赖于 OctoPrint。可以使用替代软件向 Kalico 发送命令，但这样做需要 Linux 管理员知识。

Kalico 通过"/tmp/printer"文件创建"虚拟串行端口"，并通过该文件模拟经典 3D 打印机串行接口。通常，替代软件可以使用 Kalico，只要它可以配置为将"/tmp/printer"用于打印机串行端口。

## 为什么我不能在归位打印机之前移动步进电机？

代码这样做是为了减少意外命令头进入床或墙壁的机会。打印机归位后，软件尝试验证每个移动都在配置文件中定义的 position_min/max 范围内。如果电机被禁用（通过 M84 或 M18 命令），则电机将需要在运动前再次归位。

如果您想在通过 OctoPrint 取消打印后移动头部，请考虑更改 OctoPrint 取消序列为您执行此操作。在 OctoPrint 中通过网络浏览器在以下位置进行配置：Settings->GCODE Scripts

如果您想在打印完成后移动头部，请考虑将所需的移动添加到切片器的"自定义 g-code"部分。

如果打印机需要在归位过程本身中进行一些额外的移动，或者根本上没有归位过程，请考虑在配置文件中使用 safe_z_home 或 homing_override 部分。如果您需要移动步进电机进行诊断或调试目的，请考虑在配置文件中添加 force_move 部分。有关这些选项的更多详细信息，请参阅 [配置参考](Config_Reference.md#customized-homing)。

## 为什么 Z position_endstop 在默认配置中设置为 0.5？

对于笛卡尔式打印机，Z position_endstop 指定当限位开关触发时喷嘴距床有多远。如果可能，建议使用 Z-max 限位并从床上远离归位（因为这减少了床碰撞的可能性）。但是，如果必须向床上归位，建议定位限位开关使其在喷嘴仍距床一小段距离时触发。这样，当归位轴时，它将在喷嘴接触床之前停止。有关更多信息，请参阅 [床平整文档](Bed_Level.md)。

## 我从 Marlin 转换了我的配置，X/Y 轴工作正常，但当归位 Z 轴时我只听到刺耳的噪音

简短答案：首先，确保您已按照 [配置检查文档](Config_checks.md) 中的说明验证了步进电机配置。如果问题仍然存在，请尝试减少打印机配置中的 max_z_velocity 设置。

完整答案：实际上，Marlin 通常只能以每秒大约 10000 步的速率进行步进。如果请求以需要更高步进速率的速度移动，Marlin 通常将尽可能快地步进。Kalico 能够达到更高的步进速率，但步进电机可能没有足够的扭矩以更高的速度移动。因此，对于具有高齿轮比或高微步设置的 Z 轴，实际可达到的 max_z_velocity 可能小于在 Marlin 中配置的值。

## 我的 TMC 电机驱动器在打印中途关闭

如果在"独立模式"中使用 TMC2208（或 TMC2224）驱动器，请确保使用 [最新版本的 Kalico](#how-do-i-upgrade-to-the-latest-software)。针对 TMC2208"stealthchop"驱动器问题的解决方法在 2020 年 3 月中旬添加到 Kalico。

## 我不断收到随机的"与 MCU 通信丢失"错误

这通常是由主机和微控制器之间的 USB 连接上的硬件错误引起的。要查找的事项：
- 在主机和微控制器之间使用高质量 USB 电缆。确保插头安全。
- 如果使用 Raspberry Pi，为 Raspberry Pi 使用 [高质量电源](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)，并使用 [高质量 USB 电缆](https://forums.raspberrypi.com/viewtopic.php?p=589877#p589877) 将该电源连接到 Pi。如果您从 OctoPrint 收到"欠压"警告，这与电源有关，必须修复。
- 确保打印机的电源不被过载。（电源波动到微控制器的 USB 芯片可能导致该芯片重置。）
- 验证步进器、加热器和其他打印机线缆未被压扁或磨损。（打印机移动可能会对故障线缆造成压力，导致其失去接触、短暂短路或产生过多噪音。）
- 有报告称，当打印机电源和主机 5V 电源混合时，USB 噪音很高。（如果您发现微控制器在打印机电源打开或 USB 电缆插入时上电，则表示 5V 电源被混合。）可能有助于配置微控制器仅从一个电源使用电源。（或者，如果微控制器主板无法配置其电源，可能需要修改 USB 电缆，使其不在主机和微控制器之间传输 5V 电源。）

## 我的 Raspberry Pi 在打印期间不断重启

这很可能是由于电压波动。遵循与 ["与 MCU 通信丢失"](#i-keep-getting-random-lost-communication-with-mcu-errors) 错误相同的故障排除步骤。

## 当我设置 `restart_method=command` 时我的 AVR 设备在重启时卡住

一些旧版本的 AVR 引导程序在看门狗事件处理中有已知的错误。这通常在打印机 .cfg 文件将 restart_method 设置为"command"时表现出来。当错误发生时，AVR 设备将无响应，直到断开电源并重新应用到设备为止（电源或状态 LED 也可能在断开电源之前闪烁重复）。

解决方法是使用"command"以外的 restart_method 或将更新的引导程序刷新到 AVR 设备。刷新新引导程序是一个一次性步骤，通常需要外部编程器 - 有关更多详细信息，请参阅 [引导程序](Bootloaders.md)。

## 如果 Raspberry Pi 崩溃，加热器会保持打开吗？

该软件已被设计为防止这种情况。一旦主机启用加热器，主机软件需要每 5 秒确认一次该启用。如果微控制器在 5 秒内未收到确认，它将进入"关闭"状态，该状态旨在关闭所有加热器和步进电机。

有关更多详细信息，请参阅 [MCU 命令](MCU_Commands.md) 文档中的"config_digital_out"命令。

此外，微控制器软件在启动时为每个加热器配置了最小和最大温度范围（有关详细信息，请参阅 [配置参考](Config_Reference.md#extruder) 中的 min_temp 和 max_temp 参数）。如果微控制器检测到温度超出该范围，它也将进入"关闭"状态。

另外，主机软件还实现了代码来检查加热器和温度传感器是否正常工作。有关更多详细信息，请参阅 [配置参考](Config_Reference.md#verify_heater)。

## 我如何将 Marlin 引脚号转换为 Kalico 引脚名称？

简短答案：[sample-aliases.cfg](../config/sample-aliases.cfg) 文件中提供了映射。使用该文件作为查找实际微控制器引脚名称的指南。（也可以将相关的 [board_pins](Config_Reference.md#board_pins) 配置部分复制到您的配置文件中并在您的配置中使用别名，但最好是翻译并使用实际的微控制器引脚名称。）请注意，sample-aliases.cfg 文件使用以"ar"前缀开头的引脚名称而不是"D"（例如，Arduino 引脚 `D23` 是 Kalico 别名 `ar23`）和"analog"前缀而不是"A"（例如，Arduino 引脚 `A14` 是 Kalico 别名 `analog14`）。

完整答案：Kalico 使用微控制器定义的标准引脚名称。在 Atmega 芯片上，这些硬件引脚有 `PA4`、`PC7` 或 `PD2` 等名称。

很久以前，Arduino 项目决定避免使用标准硬件名称，而是采用基于递增数字的自己的引脚名称 - 这些 Arduino 名称通常看起来像 `D23` 或 `A14`。这是一个不幸的选择，导致了很大的混淆。特别是 Arduino 引脚号经常不会转换为相同的硬件名称。例如，`D21` 在一个常见的 Arduino 板上是 `PD0`，但在另一个常见的 Arduino 板上是 `PC7`。

为了避免这种混淆，核心 Kalico 代码使用微控制器定义的标准引脚名称。

## 我是否必须将我的设备连接到特定类型的微控制器引脚？

这取决于设备类型和引脚类型：

ADC 引脚（或模拟引脚）：对于热敏电阻和类似的"模拟"传感器，设备必须连接到微控制器上支持"模拟"或"ADC"的引脚。如果您将 Kalico 配置为使用不支持模拟的引脚，Kalico 将报告"不是有效的 ADC 引脚"错误。

PWM 引脚（或计时器引脚）：默认情况下，Kalico 不对任何设备使用硬件 PWM。因此，通常，可以将加热器、风扇和类似设备连接到任何通用 IO 引脚。但是，风扇和 output_pin 设备可能选择性地配置为使用 `hardware_pwm: True`，在这种情况下，微控制器必须在该引脚上支持硬件 PWM（否则，Kalico 将报告"不是有效的 PWM 引脚"错误）。

IRQ 引脚（或中断引脚）：Kalico 不使用 IO 引脚上的硬件中断，因此永远不需要将设备连接到其中一个微控制器引脚。

SPI 引脚：使用硬件 SPI 时，需要将引脚连接到微控制器的 SPI 兼容引脚。但是，大多数设备可以配置为使用"软件 SPI"，在这种情况下，可以使用任何通用 IO 引脚。

I2C 引脚：使用 I2C 时，需要将引脚连接到微控制器的 I2C 兼容引脚。

其他设备可能连接到任何通用 IO 引脚。例如，步进器、加热器、风扇、Z 探针、伺服器、LED、通用 hd44780/st7920 LCD 显示器、Trinamic UART 控制线可能连接到任何通用 IO 引脚。

## 我如何取消 M109/M190"等待温度"请求？

导航到 OctoPrint 终端选项卡并在终端框中发出 M112 命令。M112 命令将导致 Kalico 进入"关闭"状态，并导致 OctoPrint 与 Kalico 断开连接。导航到 OctoPrint 连接区域并单击"连接"以导致 OctoPrint 重新连接。导航回终端选项卡并发出 FIRMWARE_RESTART 命令以清除 Kalico 错误状态。完成此序列后，先前的加热请求将被取消，新的打印可能会启动。

## 我能否找出打印机是否丢失了步数？

在某种程度上，可以。归位打印机，发出 `GET_POSITION` 命令，运行您的打印，再次归位并发出另一个 `GET_POSITION` 命令。然后比较 `mcu:` 行中的值。

这可能有助于调整设置，如步进电机电流、加速度和速度，而无需实际打印某些东西并浪费灯丝：只需在 `GET_POSITION` 命令之间进行一些高速移动即可。

请注意，限位开关本身往往以略有不同的位置触发，因此差异为几个微步可能是限位不准确的结果。步进电机本身只能以 4 个整步的增量丢失步数。（因此，如果使用 16 微步，则步进电机上丢失的步数将导致"mcu："步计数器偏离 64 微步的倍数。）

## 为什么 Kalico 报告错误？我丢失了打印！

简短答案：我们希望了解我们的打印机是否检测到问题，以便可以修复基本问题，我们可以获得高质量的打印。我们肯定不希望我们的打印机以静默方式产生低质量的打印。

完整答案：Kalico 已被设计为自动解决许多暂时性问题。例如，它自动检测通信错误并将重新传输；它提前计划操作并在多个层缓冲命令以实现精确时序，即使存在间歇性干扰。但是，如果软件检测到无法恢复的错误，被命令采取无效操作，或检测到无法执行其命令任务，则 Kalico 将报告错误。在这些情况下，存在产生低质量打印（或更糟）的高风险。希望提醒用户能够使他们纠正基本问题并提高打印整体质量。

有一些相关问题：为什么 Kalico 不暂停打印呢？报告警告呢？在打印前检查错误呢？忽略用户输入的命令中的错误呢？等等。目前，Kalico 使用 G-Code 协议读取命令，不幸的是 G-Code 命令协议不够灵活，无法实际进行这些替代方案。开发人员对改善异常事件期间的用户体验感兴趣，但预计这将需要显著的基础设施工作（包括远离 G-Code 的转变）。

## 我如何升级到最新软件？

升级软件的第一步是查看最新的 [配置更改](Config_Changes.md) 文档。偶尔，对软件进行更改，需要用户作为软件升级的一部分更新其设置。在升级之前审阅此文档是个好主意。

准备好升级后，一般方法是通过 ssh 进入 Raspberry Pi 并运行：

```
cd ~/klipper
git pull
~/klipper/scripts/install-octopi.sh
```

然后可以重新编译和刷新微控制器代码。例如：

```
make menuconfig
make clean
make

sudo service klipper stop
make flash FLASH_DEVICE=/dev/ttyACM0
sudo service klipper start
```

但是，通常只有主机软件改变。在这种情况下，可以仅使用以下命令更新和重启主机软件：

```
cd ~/klipper
git pull
sudo service klipper restart
```

如果在使用此快捷方式后软件警告需要重新刷新微控制器或发生其他异常错误，则遵循上面概述的完整升级步骤。

如果任何错误仍然存在，则仔细检查 [配置更改](Config_Changes.md) 文档，因为您可能需要修改打印机配置。

请注意，RESTART 和 FIRMWARE_RESTART G-Code 命令不加载新软件 - 上面的"sudo service klipper restart"和"make flash"命令是软件更改生效所需的。

## 我如何卸载 Kalico？

在固件端，无需进行特殊操作。只需遵循新固件的刷新方向。

在 Raspberry Pi 端，卸载脚本在 [scripts/klipper-uninstall.sh](../scripts/klipper-uninstall.sh) 中可用。例如：
```
sudo ~/klipper/scripts/klipper-uninstall.sh
rm -rf ~/klippy-env ~/klipper