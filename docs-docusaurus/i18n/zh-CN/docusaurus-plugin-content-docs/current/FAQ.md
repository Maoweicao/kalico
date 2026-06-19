# 常见问题

## 如何向该项目捐款？

感谢您的支持。请参阅 [赞助商页面](Sponsors.md) 了解相关信息。

## 如何计算 rotation_distance 配置参数？

请参阅 [旋转距离文档](Rotation_Distance.md)。

## 我的串行端口在哪里？

查找 USB 串行端口的通用方法是在主机机器的 ssh 终端中运行 `ls /dev/serial/by-id/*`。它可能会产生类似于以下内容的输出：
```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

在上面命令中找到的名称是稳定的，可以在配置文件中使用，也可以在刷新微控制器代码时使用。例如，刷新命令可能类似于：
```
sudo service klipper stop
make flash FLASH_DEVICE=/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
sudo service klipper start
```
更新后的配置可能如下所示：
```
[mcu]
serial: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

请确保从您上面运行的 "ls" 命令中复制粘贴名称，因为每台打印机的名称都会不同。

如果您使用多个微控制器且它们没有唯一 ID（具有 CH340 USB 芯片的板卡上常见），则请改用 `ls /dev/serial/by-path/*` 命令并按照上述说明操作。

## 当微控制器重启时，设备更改为 /dev/ttyUSB1

请按照 "[我的串行端口在哪里？](#wheres-my-serial-port)" 部分中的说明操作以防止此情况发生。

## "make flash" 命令不起作用

代码尝试使用每个平台最常见的方法来刷新设备。不幸的是，刷新方法有很多差异，因此 "make flash" 命令可能不适用于所有板卡。

如果您遇到间歇性故障或确实具有标准设置，请仔细检查刷新时 Kalico 是否未运行（sudo service klipper stop），确保 OctoPrint 未尝试直接连接设备（在网页中打开"连接"选项卡，如果串行端口设置为该设备，请单击"断开连接"），并确保为您的板卡正确设置了 FLASH_DEVICE（请参阅[上述问题](#wheres-my-serial-port)）。

但是，如果 "make flash" 对您的板卡不起作用，则需要手动刷新。查看 [config 目录](../config) 中是否有包含刷新设备特定说明的配置文件。同时，检查板卡制造商的文档以了解其是否描述了如何刷新设备。最后，可以使用 "avrdude" 或 "bossac" 等工具手动刷新设备 - 有关其他信息，请参阅 [引导加载程序文档](Bootloaders.md)。

## 如何更改串行波特率？

Kalico 的推荐波特率为 250000。此波特率在 Kalico 支持的所有微控制器板卡上运行良好。如果您找到在线指南建议使用不同的波特率，请忽略该指南的该部分并继续使用默认值 250000。

如果您仍想更改波特率，则需要在微控制器中配置新波特率（在 **make menuconfig** 期间），并且需要将更新后的代码编译并刷新到微控制器。Kalico printer.cfg 文件也需要更新以匹配该波特率（有关详细信息，请参阅 [config reference](Config_Reference.md#mcu)）。例如：
```
[mcu]
baud: 250000
```

OctoPrint 网页上显示的波特率对内部 Kalico 微控制器波特率没有影响。使用 Kalico 时，始终将 OctoPrint 波特率设置为 250000。

Kalico 微控制器波特率与微控制器的引导加载程序波特率无关。有关引导加载程序的更多信息，请参阅 [引导加载程序文档](Bootloaders.md)。

## 我可以在 Raspberry Pi 3 以外的设备上运行 Kalico 吗？

推荐的硬件是 Raspberry Pi 2、Raspberry Pi 3 或 Raspberry Pi 4。

Kalico 可以在 Raspberry Pi 1 和 Raspberry Pi Zero 上运行，但这些板卡没有足够的处理能力来良好运行 OctoPrint。当直接从 OctoPrint 打印时，这些较慢的机器上经常会发生打印停顿。（打印机的移动速度可能超过 OctoPrint 发送移动命令的速度。）如果您仍希望在这些较慢的板卡之一上运行，请考虑在打印时使用 "virtual_sdcard" 功能（有关详细信息，请参阅 [config reference](Config_Reference.md#virtual_sdcard)）。

有关在 Beaglebone 上运行的信息，请参阅 [Beaglebone 特定安装说明](Beaglebone.md)。

Kalico 已在其他机器上运行。Kalico 主机软件只需要在 Linux（或类似）计算机上运行 Python。但是，如果您希望在其他机器上运行它，则需要 Linux 管理知识来安装该特定机器的系统先决条件。有关必要的 Linux 管理步骤的更多信息，请参阅 [install-octopi.sh](../scripts/install-octopi.sh) 脚本。

如果您希望在低端芯片上运行 Kalico 主机软件，请注意，至少需要具有"双精度浮点"硬件的机器。

如果您希望在共享的通用桌面或服务器级机器上运行 Kalico 主机软件，请注意 Kalico 有一些实时调度要求。如果在打印期间，主机计算机还执行密集的通用计算任务（如硬盘碎片整理、3D 渲染、大量交换等），则可能导致 Kalico 报告打印错误。

注意：如果您不使用 OctoPi 镜像，请注意某些 Linux 发行版启用了 "ModemManager"（或类似）包，该包可能干扰串行通信。（这可能导致 Kalico 报告看似随机的"与 MCU 通信丢失"错误。）如果您在这些发行版之一上安装 Kalico，可能需要禁用该包。

## 我可以在同一台主机机器上运行多个 Kalico 实例吗？

可以运行多个 Kalico 主机软件实例，但这样做需要 Linux 管理知识。Kalico 安装脚本最终会导致以下 Unix 命令运行：
```
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer.cfg -l /tmp/klippy.log
```
只要每个实例有自己的打印机配置文件、自己的日志文件和自己的伪终端，就可以运行上述命令的多个实例。例如：
```
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer2.cfg -l /tmp/klippy2.log -I /tmp/printer2
```

如果您选择这样做，则需要实现必要的启动、停止和安装脚本（如果有）。[install-octopi.sh](../scripts/install-octopi.sh) 脚本和 [klipper-start.sh](../scripts/klipper-start.sh) 脚本可能作为示例很有用。

## 我必须使用 OctoPrint 吗？

Kalico 软件不依赖于 OctoPrint。可以使用替代软件向 Kalico 发送命令，但这需要 Linux 管理知识。

Kalico 通过 "/tmp/printer" 文件创建"虚拟串行端口"，并通过该文件模拟经典 3D 打印机串行接口。通常，只要替代软件可以配置为使用 "/tmp/printer" 作为打印机串行端口，它就可以与 Kalico 配合使用。

## 为什么在归位打印机之前无法移动步进电机？

代码这样做是为了减少意外将工具头移动到打印平台或墙壁上的可能性。一旦打印机归位，软件会尝试验证每次移动是否在配置文件中定义的 position_min/max 范围内。如果电机被禁用（通过 M84 或 M18 命令），则需要在移动前再次归位。

如果您希望在通过 OctoPrint 取消打印后移动工具头，请考虑更改 OctoPrint 取消序列以自动执行此操作。它在 OctoPrint 中通过 Web 浏览器配置：Settings->GCODE Scripts。

如果您希望在打印完成后移动工具头，请考虑在切片软件的 "custom g-code" 部分添加所需的移动。

如果打印机在归位过程本身中需要一些额外的移动（或者从根本上没有归位过程），则考虑在配置文件中使用 safe_z_home 或 homing_override 部分。如果您需要出于诊断或调试目的移动步进电机，请考虑在配置文件中添加 force_move 部分。有关这些选项的更多信息，请参阅 [config reference](Config_Reference.md#customized-homing)。

## 为什么 Z position_endstop 在默认配置中设置为 0.5？

对于笛卡尔风格的打印机，Z position_endstop 指定限位开关触发时喷嘴距离打印平台的距离。如果可能，建议使用 Z-max 限位开关并远离打印平台归位（因为这减少了碰撞打印平台的可能性）。但是，如果必须朝向打印平台归位，则建议将限位开关定位在喷嘴仍与打印平台有一定距离时触发。这样，在归位轴时，它将在喷嘴接触打印平台之前停止。有关更多信息，请参阅 [床面调平文档](Bed_Level.md)。

## 我从 Marlin 转换了配置，X/Y 轴工作正常，但在归位 Z 轴时只听到刺耳的噪音

简短回答：首先，确保您已按照 [config check document](Config_checks.md) 中的描述验证了步进配置。如果问题仍然存在，请尝试降低打印机配置中的 max_z_velocity 设置。

详细回答：实际上，Marlin 通常只能以大约每秒 10000 步的速率步进。如果要求其以需要更高速率的速度移动，则 Marlin 通常只会尽可能快地步进。Kalico 能够实现更高的步进速率，但步进电机可能没有足够的扭矩以更高速度移动。因此，对于具有高齿轮比或高微步设置的 Z 轴，实际可获得的 max_z_velocity 可能小于 Marlin 中配置的值。

## 我的 TMC 电机驱动器在打印过程中关闭

如果在"独立模式"下使用 TMC2208（或 TMC2224）驱动器，请确保使用 [最新版本的 Kalico](#how-do-i-upgrade-to-the-latest-software)。Kalico 在 2020 年 3 月中旬添加了针对 TMC2208 "stealthchop" 驱动器问题的解决方法。

## 我一直收到随机"与 MCU 通信丢失"错误

这通常是由主机机器和微控制器之间的 USB 连接硬件错误引起的。需要检查的事项：
- 在主机机器和微控制器之间使用高质量 USB 电缆。确保插头牢固。
- 如果使用 Raspberry Pi，请为 Raspberry Pi 使用 [高质量电源](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#power-supply)，并使用 [高质量 USB 电缆](https://forums.raspberrypi.com/viewtopic.php?p=589877#p589877) 将该电源连接到 Pi。如果从 OctoPrint 收到"欠压"警告，这与电源有关，必须修复。
- 确保打印机电源没有过载。（微控制器 USB 芯片的电源波动可能导致该芯片重置。）
- 验证步进电机、加热器和其他打印机电线没有压接或磨损。（打印机移动可能会对有故障的电线施加压力，导致其失去接触、短暂短路或产生过多噪音。）
- 有报告称当打印机电源和主机的 5V 电源混合使用时，USB 噪声很高。（如果您发现微控制器在打印机电源打开或 USB 电缆插入时开机，则表明 5V 电源被混合使用。）将微控制器配置为仅使用一个电源可能会有所帮助。（或者，如果微控制器板卡无法配置其电源，可以修改 USB 电缆使其不在主机和微控制器之间传输 5V 电源。）

## 我的 Raspberry Pi 在打印过程中不断重启

这很可能是由于电压波动。请按照 ["与 MCU 通信丢失"](#i-keep-getting-random-lost-communication-with-mcu-errors) 错误的相同故障排除步骤操作。

## 当我设置 `restart_method=command` 时，我的 AVR 设备在重启时挂起

某些旧版本的 AVR 引导加载程序在看门狗事件处理中存在已知错误。这通常在 printer.cfg 文件将 restart_method 设置为 "command" 时出现。当错误发生时，AVR 设备将没有响应，直到移除并重新应用电源（电源或状态 LED 也可能在移除电源之前反复闪烁）。

解决方法是使用除 "command" 以外的 restart_method，或向 AVR 设备刷新更新的引导加载程序。刷新新的引导加载程序是一次性步骤，通常需要外部编程器 - 有关更多信息，请参阅 [引导加载程序](Bootloaders.md)。

## 如果 Raspberry Pi 崩溃，加热器会保持打开状态吗？

该软件的设计旨在防止这种情况。一旦主机启用加热器，主机软件需要每 5 秒确认一次该启用。如果微控制器在 5 秒内未收到确认，它将进入"关闭"状态，该状态旨在关闭所有加热器和步进电机。

有关详细信息，请参阅 [MCU 命令](MCU_Commands.md) 文档中的 "config_digital_out" 命令。

此外，微控制器软件在启动时为每个加热器配置了最小和最大温度范围（有关详细信息，请参阅 [config reference](Config_Reference.md#extruder) 中的 min_temp 和 max_temp 参数）。如果微控制器检测到温度超出该范围，它也将进入"关闭"状态。

另外，主机软件还实现了检查加热器和温度传感器是否正常工作的代码。有关详细信息，请参阅 [config reference](Config_Reference.md#verify_heater)。

## 如何将 Marlin 引脚编号转换为 Kalico 引脚名称？

简短回答：[sample-aliases.cfg](../config/sample-aliases.cfg) 文件中有映射。使用该文件作为查找实际微控制器引脚名称的指南。（也可以将相关的 [board_pins](Config_Reference.md#board_pins) 配置节复制到您的配置文件中并在配置中使用别名，但最好翻译并使用实际的微控制器引脚名称。）请注意，sample-aliases.cfg 文件使用以 "ar" 为前缀的引脚名称（例如，Arduino 引脚 `D23` 是 Kalico 别名 `ar23`），以及以 "analog" 为前缀的引脚名称（例如，Arduino 引脚 `A14` 是 Kalico 别名 `analog14`）。

详细回答：Kalico 使用微控制器定义的标准引脚名称。在 Atmega 芯片上，这些硬件引脚的名称类似于 `PA4`、`PC7` 或 `PD2`。

很久以前，Arduino 项目决定避免使用标准硬件名称，而使用基于递增数字的自己的引脚名称 - 这些 Arduino 名称通常类似于 `D23` 或 `A14`。这是一个不幸的选择，导致了大量混乱。特别是 Arduino 引脚编号经常无法转换为相同的硬件名称。例如，`D21` 在一个常见 Arduino 板卡上是 `PD0`，但在另一个常见 Arduino 板卡上是 `PC7`。

为避免这种混乱，Kalico 核心代码使用微控制器定义的标准引脚名称。

## 我必须将设备连接到特定类型的微控制器引脚吗？

这取决于设备类型和引脚类型：

ADC 引脚（或模拟引脚）：对于热敏电阻和类似的"模拟"传感器，设备必须连接到微控制器上具有"模拟"或"ADC"功能的引脚。如果您将 Kalico 配置为使用不支持模拟的引脚，Kalico 将报告"Not a valid ADC pin"错误。

PWM 引脚（或定时器引脚）：Kalico 默认不为任何设备使用硬件 PWM。因此，通常可以将加热器、风扇和类似设备连接到任何通用 IO 引脚。但是，风扇和 output_pin 设备可以选择配置为使用 `hardware_pwm: True`，在这种情况下，微控制器必须支持该引脚上的硬件 PWM（否则，Kalico 将报告"Not a valid PWM pin"错误）。

IRQ 引脚（或中断引脚）：Kalico 不使用 IO 引脚上的硬件中断，因此永远不需要将设备连接到这些微控制器引脚之一。

SPI 引脚：使用硬件 SPI 时，需要将引脚连接到微控制器的 SPI 兼容引脚。但是，大多数设备可以配置为使用"软件 SPI"，在这种情况下可以使用任何通用 IO 引脚。

I2C 引脚：使用 I2C 时，需要将引脚连接到微控制器的 I2C 兼容引脚。

其他设备可以连接到任何通用 IO 引脚。例如，步进电机、加热器、风扇、Z 探针、舵机、LED、常见的 hd44780/st7920 LCD 显示屏、Trinamic UART 控制线都可以连接到任何通用 IO 引脚。

## 如何取消 M109/M190 "等待温度"请求？

导航到 OctoPrint 终端选项卡并在终端框中发出 M112 命令。M112 命令将导致 Kalico 进入"关闭"状态，并将导致 OctoPrint 与 Kalico 断开连接。导航到 OctoPrint 连接区域并单击"连接"以使 OctoPrint 重新连接。导航回终端选项卡并发出 FIRMWARE_RESTART 命令以清除 Kalico 错误状态。完成此序列后，之前的加热请求将被取消，可以开始新的打印。

## 能否发现打印机是否丢步了？

在某种程度上，是的。归位打印机，发出 `GET_POSITION` 命令，运行打印，再次归位并发出另一个 `GET_POSITION`。然后比较 `mcu:` 行中的值。

这对于调整步进电机电流、加速度和速度等设置可能很有帮助，而无需实际打印某些东西并浪费耗材：只需在 `GET_POSITION` 命令之间运行一些高速移动。

请注意，限位开关本身往往会在略有不同的位置触发，因此几个微步的差异可能是限位开关不准确的结果。步进电机本身只能以 4 个全步为增量丢失步数。（因此，如果使用 16 个微步，则步进电机上丢失的步数将导致 "mcu:" 步进计数器偏差为 64 个微步的倍数。）

## 为什么 Kalico 报告错误？我丢失了我的打印！

简短回答：我们希望知道打印机是否检测到问题，以便可以修复根本问题并获得高质量的打印。我们绝对不希望打印机静默地产生低质量的打印。

详细回答：Kalico 经过设计可以自动处理许多瞬态问题。例如，它自动检测通信错误并会重新传输；它提前调度操作并在多个层缓冲命令，即使存在间歇性干扰也能实现精确计时。但是，如果软件检测到无法恢复的错误、被命令执行无效操作，或者检测到它无法执行其命令任务，则 Kalico 将报告错误。在这些情况下，产生低质量打印（或更糟）的风险很高。希望通过提醒用户来帮助他们修复根本问题并提高打印的整体质量。

有一些相关问题：为什么 Kalico 不暂停打印？为什么不是报告警告？为什么不在打印前检查错误？为什么不忽略用户输入命令中的错误？等等？目前 Kalico 使用 G-Code 协议读取命令，不幸的是，G-Code 命令协议不够灵活，无法使这些替代方案在今天变得实用。开发者有兴趣改善异常事件期间的用户体验，但预计这将需要大量的基础设施工作（包括从 G-Code 的转变）。

## 如何升级到最新软件？

升级软件的第一步是查看最新的 [config changes](Config_Changes.md) 文档。有时，软件会进行更改，要求用户在软件升级过程中更新设置。在升级之前查看此文档是个好主意。

准备升级时，通用方法是 ssh 到 Raspberry Pi 并运行：

```
cd ~/klipper
git pull
~/klipper/scripts/install-octopi.sh
```

然后可以重新编译并刷新微控制器代码。例如：

```
make menuconfig
make clean
make

sudo service klipper stop
make flash FLASH_DEVICE=/dev/ttyACM0
sudo service klipper start
```

但是，通常只有主机软件更改。在这种情况下，可以只更新和重启主机软件：

```
cd ~/klipper
git pull
sudo service klipper restart
```

如果使用此快捷方式后软件警告需要重新刷新微控制器或发生其他异常错误，请按照上述完整升级步骤操作。

如果任何错误持续存在，请仔细检查 [config changes](Config_Changes.md) 文档，因为您可能需要修改打印机配置。

请注意，RESTART 和 FIRMWARE_RESTART G-Code 命令不会加载新软件 - 需要上述 "sudo service klipper restart" 和 "make flash" 命令才能使软件更改生效。

## 如何卸载 Kalico？

在固件端，不需要任何特殊操作。只需按照新固件的刷新说明操作。

在 Raspberry Pi 端，卸载脚本可在 [scripts/klipper-uninstall.sh](../scripts/klipper-uninstall.sh) 中找到。例如：
```
sudo ~/klipper/scripts/klipper-uninstall.sh
rm -rf ~/klippy-env ~/klipper
```
