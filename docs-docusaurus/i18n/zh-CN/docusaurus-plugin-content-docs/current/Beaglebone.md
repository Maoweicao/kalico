# Beaglebone

本文档描述了在 Beaglebone PRU 上运行 Kalico 的过程。

## 构建操作系统镜像

首先安装
[Debian 11.7 2023-09-02 4GB microSD IoT](https://beagleboard.org/latest-images)
镜像。可以从 micro-SD 卡或内置 eMMC 运行镜像。如果使用 eMMC，请立即按照上述链接的说明将其安装到 eMMC。

然后通过 ssh 登录到 Beaglebone 机器（`ssh debian@beaglebone` -- 密码为 `temppwd`）。

在开始安装 Kalico 之前，你需要释放额外的空间。有 3 个选项可以做到这一点：
1. 移除一些 BeagleBone "Demo" 资源
2. 如果你是从 SD-Card 启动的，并且它大于 4Gb - 你可以扩展当前文件系统以占用整个卡空间
3. 同时执行选项 #1 和 #2。

要移除一些 BeagleBone "Demo" 资源，请执行以下命令：
```
sudo apt remove bb-node-red-installer
sudo apt remove bb-code-server
```

要将文件系统扩展到 SD-Card 的完整大小，请执行此命令，无需重启：
```
sudo growpart /dev/mmcblk0 1
sudo resize2fs /dev/mmcblk0p1
```

通过运行以下命令安装 Kalico：

```
git clone https://github.com/KalicoCrew/kalico klipper
./klipper/scripts/install-beaglebone.sh
```

安装 Kalico 后，你需要决定需要什么样的部署类型，但请注意 BeagleBone 是基于 3.3v 的硬件，在大多数情况下，你不能直接将引脚连接到基于 5v 或 12v 的硬件，需要转换板。

由于 Kalico 在 BeagleBone 上具有多模块架构，你可以实现许多不同的用例，但一般如下：

用例 1：仅使用 BeagleBone 作为主机系统来运行 Kalico 和其他软件，如 OctoPrint/Fluidd + Moonraker/... 此配置将通过串行/usb/canbus 连接驱动外部微控制器。

用例 2：将 BeagleBone 与扩展板（cape）一起使用，如 CRAMPS 板。在此配置中，BeagleBone 将托管 Kalico + 其他软件，并将使用 BeagleBone PRU 核心（2 个额外核心 200Mh，32Bit）驱动扩展板。

用例 3：与"用例 1"相同，但你希望通过利用 PRU 核心来卸载主 CPU，从而高速驱动 BeagleBone GPIO。

## 安装 Octoprint

可以安装 Octoprint，或者如果希望使用其他软件则完全跳过此部分：
```
git clone https://github.com/foosel/OctoPrint.git
cd OctoPrint/
virtualenv venv
./venv/bin/python setup.py install
```

并设置 OctoPrint 在启动时运行：
```
sudo cp ~/OctoPrint/scripts/octoprint.init /etc/init.d/octoprint
sudo chmod +x /etc/init.d/octoprint
sudo cp ~/OctoPrint/scripts/octoprint.default /etc/default/octoprint
sudo update-rc.d octoprint defaults
```

需要修改 OctoPrint 的 **/etc/default/octoprint** 配置文件。必须将 `OCTOPRINT_USER` 用户更改为 `debian`，将 `NICELEVEL` 更改为 `0`，取消注释 `BASEDIR`、`CONFIGFILE` 和 `DAEMON` 设置，并将引用从 `/home/pi/` 更改为 `/home/debian/`：
```
sudo nano /etc/default/octoprint
```

然后启动 Octoprint 服务：
```
sudo systemctl start octoprint
```
等待 1-2 分钟，确保 OctoPrint Web 服务器可访问 - 它应该在：
[http://beaglebone:5000/](http://beaglebone:5000/)

## 构建 BeagleBone PRU 微控制器代码（PRU 固件）
此部分是上述"用例 2"和"用例 3"所必需的，对于"用例 1"应跳过。

检查所需设备是否存在

```
sudo beagle-version
```
你应该检查输出是否包含成功的 "remoteproc" 驱动加载以及 PRU 核心的存在，
在内核 5.10 中，它们应该是 "remoteproc1" 和 "remoteproc2"（4a334000.pru，4a338000.pru）
还要检查是否加载了许多 GPIO，它们看起来像 "Allocated GPIO id=0 name='P8_03'"
通常一切正常，不需要硬件配置。
如果缺少某些内容 - 尝试使用 "uboot overlays" 选项或 cape-overlays
仅供参考，使用 CRAMPS 板的正常 BeagleBone Black 配置的一些输出：
```
model:[TI_AM335x_BeagleBone_Black]
UBOOT: Booted Device-Tree:[am335x-boneblack-uboot-univ.dts]
UBOOT: Loaded Overlay:[BB-ADC-00A0.bb.org-overlays]
UBOOT: Loaded Overlay:[BB-BONE-eMMC1-01-00A0.bb.org-overlays]
kernel:[5.10.168-ti-r71]
/boot/uEnv.txt Settings:
uboot_overlay_options:[enable_uboot_overlays=1]
uboot_overlay_options:[disable_uboot_overlay_video=0]
uboot_overlay_options:[disable_uboot_overlay_audio=1]
uboot_overlay_options:[disable_uboot_overlay_wireless=1]
uboot_overlay_options:[enable_uboot_cape_universal=1]
pkg:[bb-cape-overlays]:[4.14.20210821.0-0~bullseye+20210821]
pkg:[bb-customizations]:[1.20230720.1-0~bullseye+20230720]
pkg:[bb-usb-gadgets]:[1.20230414.0-0~bullseye+20230414]
pkg:[bb-wl18xx-firmware]:[1.20230414.0-0~bullseye+20230414]
.............
.............

```

要编译 Kalico 微控制器代码，首先将其配置为"Beaglebone PRU"，对于"BeagleBone Black"，另外在"可选功能"中禁用"Support GPIO Bit-banging devices"和禁用"Support LCD devices"，因为它们无法放入 8Kb PRU 固件内存中，然后退出并保存配置：
```
cd ~/klipper/
make menuconfig
```

要构建并安装新的 PRU 微控制器代码，请运行：
```
sudo service klipper stop
make flash
sudo service klipper start
```
执行上述命令后，你的 PRU 固件应已准备就绪并启动，要检查一切是否正常，可以执行以下命令
```
dmesg
```
并将最后的消息与示例进行比较，该示例表示一切正常启动：
```
[   71.105499] remoteproc remoteproc1: 4a334000.pru is available
[   71.157155] remoteproc remoteproc2: 4a338000.pru is available
[   73.256287] remoteproc remoteproc1: powering up 4a334000.pru
[   73.279246] remoteproc remoteproc1: Booting fw image am335x-pru0-fw, size 97112
[   73.285807]  remoteproc1#vdev0buffer: registered virtio0 (type 7)
[   73.285836] remoteproc remoteproc1: remote processor 4a334000.pru is now up
[   73.286322] remoteproc remoteproc2: powering up 4a338000.pru
[   73.313717] remoteproc remoteproc2: Booting fw image am335x-pru1-fw, size 188560
[   73.313753] remoteproc remoteproc2: header-less resource table
[   73.329964] remoteproc remoteproc2: header-less resource table
[   73.348321] remoteproc remoteproc2: remote processor 4a338000.pru is now up
[   73.443355] virtio_rpmsg_bus virtio0: creating channel rpmsg-pru addr 0x1e
[   73.443727] virtio_rpmsg_bus virtio0: msg received with no recipient
[   73.444352] virtio_rpmsg_bus virtio0: rpmsg host is online
[   73.540993] rpmsg_pru virtio0.rpmsg-pru.-1.30: new rpmsg_pru device: /dev/rpmsg_pru30
```
注意 "/dev/rpmsg_pru30" - 它是你将来用于主 mcu 配置的串行设备，
此设备必须存在，如果不存在 - 你的 PRU 核心未正确启动。

## 构建和安装 Linux 主机微控制器代码
此部分是上述"用例 2"所必需的，对于"用例 3"是可选的

还需要为 Linux 主机进程编译和安装微控制器代码。第二次将其配置为"Linux process"：
```
make menuconfig
```

然后也安装此微控制器代码：
```
sudo service klipper stop
make flash
sudo service klipper start
```
注意 "/tmp/klipper_host_mcu" - 它将是你将来用于"mcu host"的串行设备
如果该文件不存在 - 请参阅 "scripts/klipper-mcu.service" 文件，它是由前面的命令安装的，并且负责它。

对于"用例 2"，请注意以下内容：当你定义打印机配置时，应始终使用来自"mcu host"的温度传感器，因为默认"mcu"（PRU 核心）中不存在 ADC。
挤出机和加热床的"sensor_pin"示例配置可在"generic-cramps.cfg"中找到
你可以通过引用"host:gpiochip1/gpio17"直接从"mcu host"使用任何其他 GPIO，
但应避免这样做，因为这会在主 CPU 上创建额外负载，并且很可能无法将其用于步进控制。

## 剩余配置

按照主[安装](Installation.md)文档中的说明配置 Kalico 来完成安装。

## 在 Beaglebone 上打印

不幸的是，Beaglebone 处理器有时可能难以良好运行 OctoPrint。已知在复杂打印中会发生打印停滞（打印机可能比 OctoPrint 能够发送移动命令的速度更快）。如果发生这种情况，请考虑使用"virtual_sdcard"功能（详情请参阅[配置参考](Config_Reference.md#virtual_sdcard)）直接从 Kalico 打印，并禁用你可能已启用的任何 DEBUG 或 VERBOSE 日志记录选项。

## AVR 微控制器代码构建
此环境包含构建必要微控制器代码所需的一切，但不包括 AVR，AVR 包因与 PRU 包冲突而被移除。
如果仍要在此环境中构建 AVR 微控制器代码，你需要移除 PRU 包并安装 AVR 包，执行以下命令

```
sudo apt-get remove gcc-pru
sudo apt-get install avrdude gcc-avr binutils-avr avr-libc
```
如果需要恢复 PRU 包 - 那么在此之前移除 ARV 包
```
sudo apt-get remove avrdude gcc-avr binutils-avr avr-libc
sudo apt-get install gcc-pru
```

## 硬件引脚指定
BeagleBone 在引脚指定方面非常灵活，相同的引脚可以配置为不同的功能，但始终是单引脚的单一功能，相同的功能可以出现在不同的引脚上。
因此，你不能在单个引脚上有多个功能或在多个引脚上有相同的功能。
示例：
P9_20 - i2c2_sda/can0_tx/spi1_cs0/gpio0_12/uart1_ctsn
P9_19 - i2c2_scl/can0_rx/spi1_cs1/gpio0_13/uart1_rtsn
P9_24 - i2c1_scl/can1_rx/gpio0_15/uart1_tx
P9_26 - i2c1_sda/can1_tx/gpio0_14/uart1_rx

引脚指定是通过使用特殊的"overlays"定义的，这些 overlay 在 linux 启动期间加载
它们通过使用提升权限编辑文件 /boot/uEnv.txt 来配置
```
sudo editor /boot/uEnv.txt
```
并定义要加载的功能，例如要启用 CAN1，你需要为其定义 overlay
```
uboot_overlay_addr4=/lib/firmware/BB-CAN1-00A0.dtbo
```
此 overlay BB-CAN1-00A0.dtbo 将重新配置 CAN1 的所有必需引脚，并在 Linux 中创建 CAN 设备。
对 overlay 的任何更改都需要系统重启才能生效。
如果你需要了解某些 overlay 中涉及哪些引脚 - 你可以分析此位置的源文件：
/opt/sources/bb.org-overlays/src/arm/
或在 BeagleBone 论坛中搜索信息。

## 启用硬件 SPI
BeagleBone 通常有多个硬件 SPI 总线，例如 BeagleBone Black 可以有 2 个，
它们可以工作在高达 48Mhz，但通常它们被内核 Device-tree 限制为 16Mhz。
默认情况下，在 BeagleBone Black 中，某些 SPI1 引脚被配置为 HDMI-Audio 输出，
要完全启用 4 线 SPI1，你需要禁用 HDMI Audio 并启用 SPI1
为此，使用提升权限编辑文件 /boot/uEnv.txt
```
sudo editor /boot/uEnv.txt
```
取消注释变量
```
disable_uboot_overlay_audio=1
```

接下来取消注释变量并以如下方式定义它
```
uboot_overlay_addr4=/lib/firmware/BB-SPIDEV1-00A0.dtbo
```
保存 /boot/uEnv.txt 中的更改并重启板子。
现在你已启用 SPI1，要验证其存在，请执行命令
```
ls /dev/spidev1.*
```
注意 BeagleBone 通常是基于 3.3v 的硬件，要使用 5V SPI 设备，
你需要添加电平转换芯片，例如 SN74CBTD3861、SN74LVC1G34 或类似芯片。
如果你使用的是 CRAMPS 板 - 它已经包含电平转换芯片，SPI1 引脚
将在 P503 端口上可用，并且它们可以接受 5v 硬件，
请查看 CRAMPS 板原理图以获取引脚参考。

## 启用硬件 I2C
BeagleBone 通常有多个硬件 I2C 总线，例如 BeagleBone Black 可以有 3 个，
它们支持高达 400Kbit 快速模式的速度。
默认情况下，在 BeagleBone Black 中有两个（i2c-1 和 i2c-2），通常都已配置并
出现在 P9 上，第三个 ic2-0 通常保留供内部使用。
如果你使用的是 CRAMPS 板，则 i2c-2 出现在 P303 端口上，电平为 3.3v，
如果你想在 CRAMPS 板上获取 I2c-1 - 你可以在 Extruder1.Step、Extruder1.Dir 引脚上获取它们，
它们也是基于 3.3v 的，请查看 CRAMPS 板原理图以获取引脚参考。
相关的 overlays，用于[硬件引脚指定](#hardware-pin-designation)：
I2C1(100Kbit): BB-I2C1-00A0.dtbo
I2C1(400Kbit): BB-I2C1-FAST-00A0.dtbo
I2C2(100Kbit): BB-I2C2-00A0.dtbo
I2C2(400Kbit): BB-I2C2-FAST-00A0.dtbo

## 启用硬件 UART（串行）/CAN
BeagleBone 最多有 6 个硬件 UART（串行）总线（最高 3Mbit）
和最多 2 个硬件 CAN（1Mbit）总线。
UART1(RX,TX) 和 CAN1(TX,RX) 和 I2C2(SDA,SCL) 使用相同的引脚 - 所以你需要选择使用什么
UART1(CTSN,RTSN) 和 CAN0(TX,RX) 和 I2C1(SDA,SCL) 使用相同的引脚 - 所以你需要选择使用什么
所有 UART/CAN 相关引脚都是基于 3.3v 的，因此你需要使用收发器芯片/板，如 SN74LVC2G241DCUR（用于 UART）、
SN65HVD230（用于 CAN）、TTL-RS485（用于 RS-485）或类似芯片，可以将 3.3v 信号转换为适当的电平。

相关的 overlays，用于[硬件引脚指定](#hardware-pin-designation)
CAN0: BB-CAN0-00A0.dtbo
CAN1: BB-CAN1-00A0.dtbo
UART0: - 用于控制台
UART1(RX,TX):  BB-UART1-00A0.dtbo
UART1(RTS,CTS): BB-UART1-RTSCTS-00A0.dtbo
UART2(RX,TX): BB-UART2-00A0.dtbo
UART3(RX,TX): BB-UART3-00A0.dtbo
UART4(RS-485): BB-UART4-RS485-00A0.dtbo
UART5(RX,TX): BB-UART5-00A0.dtbo
