# Beaglebone

本文档描述了在 Beaglebone PRU 上运行 Kalico 的流程。

## 构建操作系统镜像

首先安装 [Debian 11.7 2023-09-02 4GB microSD IoT](https://beagleboard.org/latest-images) 镜像。您可以从 micro-SD 卡或内置 eMMC 运行该镜像。如果使用 eMMC，请按照上述链接中的说明将其安装到 eMMC。

然后通过 SSH 连接到 Beaglebone 机器（`ssh debian@beaglebone` -- 密码是 `temppwd`）。

在开始安装 Kalico 之前，您需要释放额外的空间。有 3 个选项可以做到这一点：
1. 删除某些 BeagleBone "演示"资源
2. 如果您从 SD 卡启动，并且容量大于 4Gb，您可以扩展当前文件系统以占用整个卡空间
3. 同时执行选项 #1 和 #2。

要删除某些 BeagleBone "演示"资源，请执行这些命令
```
sudo apt remove bb-node-red-installer
sudo apt remove bb-code-server
```

要将文件系统扩展到 SD 卡的完整大小，请执行此命令，无需重启。
```
sudo growpart /dev/mmcblk0 1
sudo resize2fs /dev/mmcblk0p1
```

通过运行以下命令安装 Kalico：

```
git clone https://github.com/KalicoCrew/kalico klipper
./klipper/scripts/install-beaglebone.sh
```

安装 Kalico 后，您需要决定需要什么样的部署方式，但请注意 BeagleBone 是基于 3.3v 的硬件，在大多数情况下，您无法直接将引脚连接到 5v 或 12v 的硬件，需要使用转换板。

由于 Kalico 在 BeagleBone 上具有多模块架构，您可以实现许多不同的用例，但一般用例如下：

用例 1：仅将 BeagleBone 用作主机系统来运行 Kalico 和附加软件（如 OctoPrint/Fluidd + Moonraker/...），此配置将通过 serial/usb/canbus 连接驱动外部微控制器。

用例 2：将 BeagleBone 与扩展板（cape）（如 CRAMPS 板）一起使用。在此配置中，BeagleBone 将托管 Kalico + 附加软件，并将使用 BeagleBone PRU 核心（2 个额外核心 200Mh、32Bit）驱动扩展板。

用例 3：与"用例 1"相同，但另外您还想通过利用 PRU 核心卸载主 CPU 来以高速驱动 BeagleBone GPIO。

## 安装 Octoprint

如果需要，您可以安装 Octoprint 或完全跳过此部分以使用其他软件：
```
git clone https://github.com/foosel/OctoPrint.git
cd OctoPrint/
virtualenv venv
./venv/bin/python setup.py install
```

并设置 OctoPrint 在启动时启动：
```
sudo cp ~/OctoPrint/scripts/octoprint.init /etc/init.d/octoprint
sudo chmod +x /etc/init.d/octoprint
sudo cp ~/OctoPrint/scripts/octoprint.default /etc/default/octoprint
sudo update-rc.d octoprint defaults
```

需要修改 OctoPrint 的 **/etc/default/octoprint** 配置文件。必须将 `OCTOPRINT_USER` 用户改为 `debian`，将 `NICELEVEL` 改为 `0`，取消注释 `BASEDIR`、`CONFIGFILE` 和 `DAEMON` 设置，并将引用从 `/home/pi/` 改为 `/home/debian/`：
```
sudo nano /etc/default/octoprint
```

然后启动 Octoprint 服务：
```
sudo systemctl start octoprint
```
等待 1-2 分钟，确保 OctoPrint 网络服务器可访问 - 应在以下位置：
[http://beaglebone:5000/](http://beaglebone:5000/)

## 构建 BeagleBone PRU 微控制器代码（PRU 固件）
此部分对于上述"用例 2"和"用例 3"是必需的，对于"用例 1"应跳过它。

检查所需设备是否存在

```
sudo beagle-version
```
您应检查输出是否包含成功的 "remoteproc" 驱动程序加载和 PRU 核心的存在，在 Kernel 5.10 中，它们应该是 "remoteproc1" 和 "remoteproc2"（4a334000.pru、4a338000.pru）
还要检查是否加载了许多 GPIO，它们看起来像 "Allocated GPIO id=0 name='P8_03'"
通常一切都很好，不需要硬件配置。
如果缺少什么 - 尝试使用 "uboot overlays" 选项或 cape-overlays
仅作参考，以下是 CRAMPS 板配置的工作 BeagleBone Black 的一些输出：
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

要编译 Kalico 微控制器代码，首先为 "Beaglebone PRU" 配置它，对于 "BeagleBone Black" 还在 "可选功能" 中禁用 "支持 GPIO Bit-banging 设备" 和禁用 "支持 LCD 设备"，因为它们不适合 8Kb PRU 固件内存，然后退出并保存配置：
```
cd ~/klipper/
make menuconfig
```

要构建和安装新的 PRU 微控制器代码，请运行：
```
sudo service klipper stop
make flash
sudo service klipper start
```
执行前面的命令后，您的 PRU 固件应该已准备好并开始启动，要检查一切是否正常，您可以执行以下命令
```
dmesg
```
并将最后的消息与示例消息进行比较，该消息表示一切都正确启动：
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
请注意 "/dev/rpmsg_pru30" - 这是您主 mcu 配置的将来串行设备，此设备必须存在，如果不存在 - 您的 PRU 核心未正确启动。

## 构建和安装 Linux 主机微控制器代码
此部分对于上述"用例 2"是必需的，对于"用例 3"是可选的

还需要编译和安装 Linux 主机进程的微控制器代码。第二次为 "Linux 进程" 配置它：
```
make menuconfig
```

然后也安装此微控制器代码：
```
sudo service klipper stop
make flash
sudo service klipper start
```
请注意 "/tmp/klipper_host_mcu" - 这将是您 "mcu host" 的将来串行设备，如果该文件不存在 - 请参阅 "scripts/klipper-mcu.service" 文件，它由前面的命令安装，并负责创建它。

请注意"用例 2"的以下内容：定义打印机配置时，应始终使用来自 "mcu host" 的温度传感器，因为 ADC 在默认 "mcu"（PRU 核心）中不存在。
"extruder" 和 "heated bed" 的 "sensor_pin" 示例配置可在 "generic-cramps.cfg" 中获得
您可以通过这种方式引用来自 "mcu host" 的任何其他 GPIO "host:gpiochip1/gpio17"，但应避免这样做，因为它会在主 CPU 上创建额外的负载，您最有可能无法将它们用于步进控制。

## 完成配置

按照主 [安装](Installation.md) 文档中的说明完成 Kalico 的安装。

## 在 Beaglebone 上打印

不幸的是，Beaglebone 处理器有时在运行 OctoPrint 时可能会遇到困难。在复杂打印上可能会出现打印停顿（打印机移动速度可能快于 OctoPrint 发送运动命令的速度）。如果发生这种情况，请考虑使用 "virtual_sdcard" 功能（有关详细信息，请参阅 [配置参考](Config_Reference.md#virtual_sdcard)），直接从 Kalico 打印，并禁用任何 DEBUG 或 VERBOSE 日志选项（如果您已启用）。

## AVR 微控制器代码构建
此环境具有构建必要微控制器代码的所有内容，除了 AVR，由于与 PRU 包的冲突，AVR 包已被删除。
如果您仍然想在此环境中构建 AVR 微控制器代码，您需要删除 PRU 包并通过执行以下命令安装 AVR 包

```
sudo apt-get remove gcc-pru
sudo apt-get install avrdude gcc-avr binutils-avr avr-libc
```
如果您需要恢复 PRU 包 - 那么在之前删除 ARV 包
```
sudo apt-get remove avrdude gcc-avr binutils-avr avr-libc
sudo apt-get install gcc-pru
```

## 硬件引脚分配
Beaglebone 在引脚分配方面非常灵活，同一引脚可以配置为不同功能，但始终是单个引脚的单一功能，同一功能可以出现在不同引脚上。
因此，您不能在单个引脚上具有多个功能或在多个引脚上具有相同功能。
示例：
P9_20 - i2c2_sda/can0_tx/spi1_cs0/gpio0_12/uart1_ctsn
P9_19 - i2c2_scl/can0_rx/spi1_cs1/gpio0_13/uart1_rtsn
P9_24 - i2c1_scl/can1_rx/gpio0_15/uart1_tx
P9_26 - i2c1_sda/can1_tx/gpio0_14/uart1_rx

引脚分配是通过使用特殊的 "overlays"（覆盖层）定义的，这些覆盖层将在 Linux 启动期间加载，通过编辑具有提升权限的 /boot/uEnv.txt 文件来配置
```
sudo editor /boot/uEnv.txt
```
并定义要加载的功能，例如要启用 CAN1，您需要为其定义覆盖层
```
uboot_overlay_addr4=/lib/firmware/BB-CAN1-00A0.dtbo
```
此覆盖层 BB-CAN1-00A0.dtbo 将重新配置 CAN1 的所有必需引脚并在 Linux 中创建 CAN 设备。
覆盖层中的任何更改都需要系统重启以应用。
如果您需要了解某个覆盖层涉及的引脚 - 您可以分析此位置中的源文件：/opt/sources/bb.org-overlays/src/arm/
或在 BeagleBone 论坛中搜索信息。

## 启用硬件 SPI
Beaglebone 通常有多个硬件 SPI 总线，例如 BeagleBone Black 可以有 2 个，它们最高可达 48Mhz，但通常受内核设备树限制为 16Mhz。
默认情况下，在 BeagleBone Black 上，某些 SPI1 引脚配置为 HDMI 音频输出，要完全启用 4 线 SPI1，您需要禁用 HDMI 音频并启用 SPI1
为此，使用提升权限编辑 /boot/uEnv.txt 文件
```
sudo editor /boot/uEnv.txt
```
取消注释变量
```
disable_uboot_overlay_audio=1
```

接下来取消注释变量并按以下方式定义它
```
uboot_overlay_addr4=/lib/firmware/BB-SPIDEV1-00A0.dtbo
```
保存 /boot/uEnv.txt 中的更改并重启主板。
现在您已启用 SPI1，要验证其存在，请执行命令
```
ls /dev/spidev1.*
```
请注意 Beaglebone 通常是基于 3.3v 的硬件，要使用 5V SPI 设备，您需要添加级位移芯片，例如 SN74CBTD3861、SN74LVC1G34 或类似的。
如果您使用 CRAMPS 板 - 它已经包含级位移芯片和 SPI1 引脚，将在 P503 端口上可用，它们可以接受 5v 硬件，检查 CRAMPS 板原理图以了解引脚参考。

## 启用硬件 I2C
Beaglebone 通常有多个硬件 I2C 总线，例如 BeagleBone Black 可以有 3 个，它们支持高达 400Kbit 快速模式的速度。
默认情况下，在 BeagleBone Black 上有两个（i2c-1 和 i2c-2）通常都已在 P9 上配置并存在，第三个 ic2-0 通常保留供内部使用。
如果您使用 CRAMPS 板，则 i2c-2 在 P303 端口上，具有 3.3v 电平，如果您想在 CRAMPS 板上获得 I2c-1 - 您可以在 Extruder1.Step、Extruder1.Dir 引脚上获得它们，它们也是 3.3v 的，检查 CRAMPS 板原理图以了解引脚参考。
相关覆盖层，用于 [硬件引脚分配](#硬件引脚分配)：
I2C1(100Kbit): BB-I2C1-00A0.dtbo
I2C1(400Kbit): BB-I2C1-FAST-00A0.dtbo
I2C2(100Kbit): BB-I2C2-00A0.dtbo
I2C2(400Kbit): BB-I2C2-FAST-00A0.dtbo

## 启用硬件 UART（串行）/CAN
Beaglebone 最多有 6 个硬件 UART（串行）总线（最高 3Mbit）和最多 2 个硬件 CAN（1Mbit）总线。
UART1(RX,TX) 和 CAN1(TX,RX) 和 I2C2(SDA,SCL) 使用相同的引脚 - 所以您需要选择使用哪一个
UART1(CTSN,RTSN) 和 CAN0(TX,RX) 和 I2C1(SDA,SCL) 使用相同的引脚 - 所以您需要选择使用哪一个
所有 UART/CAN 相关引脚都是 3.3v 的，所以您需要使用收发器芯片/板，如 SN74LVC2G241DCUR（用于 UART）、SN65HVD230（用于 CAN）、TTL-RS485（用于 RS-485）或类似的，可以将 3.3v 信号转换为适当电平。

相关覆盖层，用于 [硬件引脚分配](#硬件引脚分配)
CAN0: BB-CAN0-00A0.dtbo
CAN1: BB-CAN1-00A0.dtbo
UART0: - 用于控制台
UART1(RX,TX):  BB-UART1-00A0.dtbo
UART1(RTS,CTS): BB-UART1-RTSCTS-00A0.dtbo
UART2(RX,TX): BB-UART2-00A0.dtbo
UART3(RX,TX): BB-UART3-00A0.dtbo
UART4(RS-485): BB-UART4-RS485-00A0.dtbo
UART5(RX,TX): BB-UART5-00A0.dtbo