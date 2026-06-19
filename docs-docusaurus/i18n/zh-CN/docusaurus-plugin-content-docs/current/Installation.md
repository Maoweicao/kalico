# 安装

这些说明假设软件将运行在运行 Kalico 兼容前端的基于 Linux 的主机上。建议使用 SBC（单板计算机）（如 Raspberry Pi 或基于 Debian 的 Linux 设备）作为主机（有关其他选项，请参阅 [FAQ](FAQ.md#can-i-run-kalico-on-something-other-than-a-raspberry-pi-3)）。

在这些说明中，主机指 Linux 设备，MCU 指打印机板。SBC 指单板计算机，如 Raspberry Pi。

## 获取 Kalico 配置文件

大多数 Kalico 设置由"打印机配置文件" printer.cfg 决定，该文件将存储在主机上。通常可以在 Kalico [config 目录](../config/)中找到以"printer-"开头且与目标打印机对应的适当配置文件。Kalico 配置文件包含安装期间所需的打印机技术信息。

如果 Kalico 配置目录中没有适当的打印机配置文件，请尝试搜索打印机制造商的网站，查看他们是否有适当的 Kalico 配置文件。

如果找不到打印机的配置文件，但知道打印机控制板的类型，请查找以"generic-"开头的适当[配置文件](../config/)。这些示例打印机板文件应该允许成功完成初始安装，但需要一些自定义才能获得完整的打印机功能。

也可以从头定义新的打印机配置。但是，这需要关于打印机及其电子设备的重要技术知识。建议大多数用户从适当的配置文件开始。如果创建新的自定义打印机配置文件，请从最接近的示例[配置文件](../config/)开始，并使用 Kalico[配置参考](Config_Reference.md)获取更多信息。

## 与 Kalico 交互

Kalico 是 3D 打印机固件，因此需要某种方式让用户与之交互。

目前最好的选择是通过 [Moonraker Web API](https://moonraker.readthedocs.io/) 检索信息的前端，还有使用 [OctoPrint](https://octoprint.org/) 控制 Kalico 的选项。

选择取决于用户使用什么，但底层的 Kalico 在所有情况下都是相同的。我们鼓励用户研究可用的选项并做出明智的决定。

## 获取 SBC 的 OS 镜像

有许多方法可以获取用于 SBC 使用的 Kalico OS 镜像，大多数取决于你希望使用什么前端。一些 SBC 板制造商还提供自己的以 Klipper 为中心的镜像，这些镜像也与 Kalico 兼容。

两个主要的基于 Moonraker 的前端是 [Fluidd](https://docs.fluidd.xyz/) 和 [Mainsail](https://docs.mainsail.xyz/)，后者有一个预制的安装镜像 ["MainsailOS"](https://docs-os.mainsail.xyz/)，它有 Raspberry Pi 和一些 OrangePi 变体的选项。

Fluidd 可以通过 KIAUH（Klipper 安装和更新助手）安装，如下所述，它是所有 Kalico 相关内容的第三方安装程序。

OctoPrint 可以通过流行的 OctoPi 镜像或通过 KIAUH 安装，此过程在 [OctoPrint.md](OctoPrint.md) 中说明。

## 通过 KIAUH 安装

通常你会从 SBC 的基础镜像开始，例如 RPiOS Lite，或者对于 x86 Linux 设备，Ubuntu Server。请注意，不建议使用桌面变体，因为某些辅助程序可能会阻止某些 Kalico 功能工作，甚至掩盖对某些打印机板的访问。

KIAUH 可用于在各种运行 Debian 系列的 Linux 系统上安装 Kalico 及其相关程序。更多信息可以在 https://github.com/dw-0/kiauh 找到。

## 构建和刷写微控制器

要编译微控制器代码，首先在主机设备上运行以下命令：

```
cd ~/klipper/
make menuconfig
```

[打印机配置文件](#obtain-a-kalico-configuration-file)顶部的注释应描述在"make menuconfig"期间需要设置的设置。在 Web 浏览器或文本编辑器中打开文件，并在文件顶部附近查找这些说明。配置适当的"menuconfig"设置后，按"Q"退出，然后按"Y"保存。然后运行：

```
make
```

如果[打印机配置文件](#obtain-a-kalico-configuration-file)顶部的注释描述了将最终镜像"刷写"到打印机控制板的自定义步骤，请遵循这些步骤，然后继续[配置 OctoPrint](OctoPrint.md#configuring-octoprint-to-use-kalico)。

否则，通常使用以下步骤将打印机控制板"刷写"。首先，需要确定连接到微控制器的串口。运行以下命令：

```
ls /dev/serial/by-id/*
```

它应该报告类似以下内容：

```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

每台打印机都有自己独特的串口名称是很常见的。此唯一名称将在刷写微控制器时使用。上述输出中可能有多行——如果有多行，请选择与微控制器对应的行。如果列出了许多项目且选择不明确，请拔掉板子并重新运行命令，缺少的项目将是你的打印板（有关更多信息，请参阅 [FAQ](FAQ.md#wheres-my-serial-port)）。

对于使用 STM32 或克隆芯片、LPC 芯片等的常见微控制器，通常需要通过 SD 卡进行初始 Kalico 刷写。

使用此方法刷写时，重要的是确保打印板未通过 USB 连接到主机，因为某些板能够向板供电并阻止刷写发生。

对于使用 Atmega 芯片（例如 2560）的常见微控制器，可以使用类似以下方式刷写代码：

```
sudo service klipper stop
make flash FLASH_DEVICE=/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
sudo service klipper start
```

务必使用打印机的唯一串口名称更新 FLASH_DEVICE。

对于使用 RP2040 芯片的常见微控制器，可以使用类似以下方式刷写代码：

```
sudo service klipper stop
make flash FLASH_DEVICE=first
sudo service klipper start
```

重要提示：RP2040 芯片可能需要在此操作之前进入启动模式。

## 配置 Kalico

下一步是将[打印机配置文件](#obtain-a-kalico-configuration-file)复制到主机。

可以说设置 Kalico 配置文件最简单的方法是使用 Mainsail 或 Fluidd 中的内置编辑器。这些编辑器允许用户打开配置示例并将其保存为 printer.cfg。

另一个选项是使用支持通过"scp"和/或"sftp"协议编辑文件的桌面编辑器。有免费可用的工具支持此功能（例如 Notepad++、WinSCP 和 Cyberduck）。在编辑器中加载打印机配置文件，然后将其保存为 pi 用户主目录（即 /home/pi/printer.cfg）中名为"printer.cfg"的文件。

或者，也可以通过 SSH 直接在主机上复制和编辑文件。它可能看起来像以下内容（务必更新命令以使用适当的打印机配置文件名）：

```
cp ~/klipper/config/example-cartesian.cfg ~/printer.cfg
nano ~/printer.cfg
```

每台打印机都有自己独特的微控制器名称是很常见的。刷写 Kalico 后名称可能会更改，因此即使在刷写时已经完成，也要重新运行这些步骤。运行：

```
ls /dev/serial/by-id/*
```

它应该报告类似以下内容：

```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

然后使用唯一名称更新配置文件。例如，更新 `[mcu]` 节使其看起来类似：

```
[mcu]
serial: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

创建和编辑文件后，需要在命令控制台中发出"restart"命令来加载配置。如果 Kalico 配置文件成功读取且微控制器成功找到并配置，"status"命令将报告打印机已就绪。

自定义打印机配置文件时，Kalico 报告配置错误并不罕见。如果发生错误，对打印机配置文件进行必要的更正并发出"restart"，直到"status"报告打印机已就绪。

Kalico 通过命令控制台和 Fluidd 和 Mainsail 中的弹出窗口报告错误消息。"status"命令可用于重新报告错误消息。有一个日志可用，通常位于 `~/printer_data/logs/klippy.log`。

Kalico 报告打印机已就绪后，请继续阅读[配置检查文档](Config_checks.md)以对配置文件中的定义执行一些基本检查。有关其他信息，请参阅主要[文档参考](Overview.md)。
