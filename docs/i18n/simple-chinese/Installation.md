# 安装

这些说明假设软件将在运行 Kalico 兼容前端的基于 Linux 的主机上运行。建议使用
SBC（小型单板计算机）（如 Raspberry Pi 或基于 Debian 的 Linux
设备）作为主机（请参阅
[常见问题解答](FAQ.md#can-i-run-kalico-on-something-other-than-a-raspberry-pi-3)
了解其他选项）。

为了这些说明的目的，主机指的是 Linux 设备，mcu 指的是打印机主板。SBC 指的是小型单板计算机的术语
如 Raspberry Pi。

## 获取 Kalico 配置文件

大多数 Kalico 设置由"打印机配置文件"printer.cfg 确定，该文件将存储在主机上。通常可以通过在 Kalico
[config 目录](../config/) 中查找以"printer-"开头的文件来找到合适的配置
前缀对应于目标打印机。Kalico
配置文件包含安装过程中需要的打印机的技术信息。

如果 Kalico config 目录中没有合适的打印机配置文件，则尝试搜索打印机制造商的
网站以查看他们是否有合适的 Kalico 配置文件。

如果找不到打印机的配置文件，但已知打印机控制板的类型，则查找合适的
[config 文件](../config/)，以"generic-"开头。这些
示例打印机板文件应允许成功完成
初始安装，但将需要一些自定义以
获得完整的打印机功能。

也可以从头开始定义新的打印机配置。但是，这需要
关于打印机及其电子产品的重要技术知识。建议大多数用户
从合适的配置文件开始。如果创建新的自定义
打印机配置文件，则从最接近的示例
[config 文件](../config/) 开始，并使用 Kalico
[配置参考](Config_Reference.md) 获取更多信息。

## 与 Kalico 交互

Kalico 是 3D 打印机固件，所以需要某种方式
用户与其交互。

目前，最好的选择是通过 [Moonraker 网络 API](https://moonraker.readthedocs.io/) 检索信息的前端，也可以选择使用 [Octoprint](https://octoprint.org/) 来控制 Kalico。

选择使用什么的决定取决于用户，但基础 Kalico 在所有情况下都是相同的。我们鼓励用户研究可用选项并做出知情决定。

## 为 SBC 获取操作系统映像

获取 Kalico 操作系统映像的方法很多，大多数取决于
您想要使用什么前端。这些 SBC 主板的某些制造商也提供
自己的 Klipper 中心映像，这些也与 Kalico 兼容。

两个主要的 Moonraker 前端是 [Fluidd](https://docs.fluidd.xyz/)
和 [Mainsail](https://docs.mainsail.xyz/)，后者有一个预制的安装
映像 ["MainsailOS"](https://docs-os.mainsail.xyz/)，适用于 Raspberry Pi
和一些 OrangePi 变体。

Fluidd 可以通过 KIAUH（Klipper 安装和更新助手）进行安装，
其中说明了这是所有 Kalico 事项的第三方安装程序。

OctoPrint 可以通过流行的 OctoPi 映像或通过 KIAUH 进行安装，
这个过程在 [OctoPrint.md](OctoPrint.md) 中进行了解释

## 通过 KIAUH 安装

通常，您会从 SBC 的基础映像开始，例如 RPiOS Lite，
或者在 x86 Linux 设备的情况下，Ubuntu Server。请注意，不建议使用桌面变体
因为某些辅助程序可能会阻止某些 Kalico 功能正常工作，甚至掩盖某些打印机主板的访问权限。

KIAUH 可用于在运行 Debian 形式的各种基于 Linux 的系统上安装 Kalico 及其相关程序。更多信息
可以在 https://github.com/dw-0/kiauh 中找到

## 构建和刷新微控制器

要编译微控制器代码，请首先在主机设备上运行这些命令：

```
cd ~/klipper/
make menuconfig
```

[打印机配置文件](#obtain-a-kalico-configuration-file) 顶部的注释
应描述在"make menuconfig"期间需要设置的设置。在网络浏览器或文本编辑器中打开文件并查找
文件顶部附近的这些说明。一旦适当的"menuconfig"设置已配置，按"Q"退出，然后按"Y"保存。然后运行：

```
make
```

如果 [打印机配置文件](#obtain-a-kalico-configuration-file) 顶部的注释
描述了"刷新"最终映像到打印机
控制板的自定义步骤，然后遵循这些步骤，然后继续
[配置 OctoPrint](OctoPrint.md#configuring-octoprint-to-use-kalico)。

否则，以下步骤经常用于"刷新"打印机
控制板。首先，有必要确定连接到微控制器的串行端口。运行以下内容：

```
ls /dev/serial/by-id/*
```

它应该报告类似于以下内容的内容：

```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

每台打印机通常有自己唯一的串行端口名称。
这个唯一的名称将在刷新微控制器时使用。可能
上面的输出中可能有多行 - 如果是这样，选择与微控制器对应的行。如果列出了许多项目并且选择不明确，请断开主板连接并再次运行命令，缺少的项目将是您的打印板（有关更多信息，请参阅
[常见问题解答](FAQ.md#wheres-my-serial-port)）。

对于具有 STM32 或克隆芯片、LPC 芯片和其他常见微控制器，
通常需要通过 SD 卡进行初始 Kalico 刷新。

使用此方法刷新时，务必确保
打印板未通过 USB 连接到主机，因为某些主板
能够向主板反馈电源，阻止刷新。

对于使用 Atmega 芯片（例如 2560）的常见微控制器，
代码可以使用类似以下方法刷新：

```
sudo service klipper stop
make flash FLASH_DEVICE=/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
sudo service klipper start
```

务必使用打印机的唯一串行
端口名称更新 FLASH_DEVICE。

对于使用 RP2040 芯片的常见微控制器，代码可以使用
类似于以下方法进行刷新：

```
sudo service klipper stop
make flash FLASH_DEVICE=first
sudo service klipper start
```

务必注意 RP2040 芯片在此操作之前可能需要进入启动模式。


## 配置 Kalico

下一步是复制
[打印机配置文件](#obtain-a-kalico-configuration-file) 到
主机。

可以说，设置 Kalico 配置文件的最简单方法是使用
Mainsail 或 Fluidd 中的内置编辑器。这些将允许用户打开
配置示例并将其保存为 printer.cfg。

另一个选项是使用支持通过"scp"和/或"sftp"协议编辑文件的桌面编辑器。有免费提供的工具
支持这一点（例如 Notepad++、WinSCP 和 Cyberduck）。
在编辑器中加载打印机配置文件，然后将其保存为名为"printer.cfg"的文件
在 pi 用户的主目录中
（即 /home/pi/printer.cfg）。

或者，也可以直接通过 SSH 在
主机上复制和编辑文件。这可能看起来像以下内容（请务必
更新命令以使用合适的打印机配置
文件名）：

```
cp ~/klipper/config/example-cartesian.cfg ~/printer.cfg
nano ~/printer.cfg
```

每台打印机通常对微控制器有自己的唯一名称。该名称可能在刷新 Kalico 后改变，所以即使已经
完成，也要再次运行这些步骤。运行：

```
ls /dev/serial/by-id/*
```

它应该报告类似于以下内容的内容：

```
/dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

然后使用唯一的名称更新配置文件。例如，更新
`[mcu]` 部分看起来类似于：

```
[mcu]
serial: /dev/serial/by-id/usb-1a86_USB2.0-Serial-if00-port0
```

创建并编辑文件后，将需要在
命令控制台中发出"restart"命令来加载配置。一个
"status"命令将报告打印机已准备好，如果 Kalico
配置文件已成功读取，并且微控制器已
成功找到并配置。

自定义打印机配置文件时，Kalico 不常见
报告配置错误。如果发生错误，对打印机
配置文件进行必要的更正并发出"restart"直到"status"报告打印机已准备就绪。

Kalico 通过命令控制台和 Fluidd 和 Mainsail 中的弹窗报告错误消息。"status"命令可用于重新报告错误消息。日志可用并且通常位于
`~/printer_data/logs/klippy.log`。

Kalico 报告打印机已准备好后，继续进行
[配置检查文档](Config_checks.md)来执行一些基本检查
在配置文件中的定义。有关其他信息，请参阅主要
[文档参考](Overview.md)。