# 引导加载程序

本文档提供了 Kalico 支持的微控制器上常见引导加载程序的信息。

引导加载程序是在微控制器首次上电时运行的第三方软件。它通常用于将新应用程序（例如 Kalico）刷写到微控制器，而无需专用硬件。遗憾的是，刷写微控制器没有行业标准，也没有适用于所有微控制器的标准引导加载程序。更糟糕的是，每个引导加载程序通常需要不同的步骤来刷写应用程序。

如果能够将引导加载程序刷写到微控制器，通常也可以使用该机制刷写应用程序，但这样做时应小心，因为可能会意外删除引导加载程序。相比之下，引导加载程序通常只允许用户刷写应用程序。因此，建议尽可能使用引导加载程序来刷写应用程序。

本文档试图描述常见的引导加载程序、刷写引导加载程序所需的步骤以及刷写应用程序所需的步骤。本文档不是权威参考；它旨在作为 Kalico 开发人员积累的有用信息集合。

## AVR 微控制器

一般来说，Arduino 项目是 8 位 Atmel Atmega 微控制器上引导加载程序和刷写过程的良好参考。特别是 "boards.txt" 文件：
[https://github.com/arduino/Arduino/blob/1.8.5/hardware/arduino/avr/boards.txt](https://github.com/arduino/Arduino/blob/1.8.5/hardware/arduino/avr/boards.txt)
是一个有用的参考。

要刷写引导加载程序本身，AVR 芯片需要外部硬件刷写工具（使用 SPI 与芯片通信）。可以购买此工具（例如，搜索 "avr isp"、"arduino isp" 或 "usb tiny isp"）。也可以使用另一个 Arduino 或 Raspberry Pi 刷写 AVR 引导加载程序（例如，搜索 "program an avr using raspberry pi"）。下面的示例假设使用 "AVR ISP Mk2" 类型设备。

"avrdude" 程序是用于刷写 atmega 芯片（包括引导加载程序刷写和应用程序刷写）的最常用工具。

### Atmega2560

此芯片通常在 "Arduino Mega" 中找到，在 3d 打印机板中非常常见。

要刷写引导加载程序本身，使用类似以下的命令：
```
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/stk500v2/stk500boot_v2_mega2560.hex'

avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xFD:m -U hfuse:w:0xD8:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -U flash:w:stk500boot_v2_mega2560.hex
avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似以下的命令：
```
avrdude -cwiring -patmega2560 -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

### Atmega1280

此芯片通常在早期版本的 "Arduino Mega" 中找到。

要刷写引导加载程序本身，使用类似以下的命令：
```
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/atmega/ATmegaBOOT_168_atmega1280.hex'

avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xF5:m -U hfuse:w:0xDA:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -U flash:w:ATmegaBOOT_168_atmega1280.hex
avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似以下的命令：
```
avrdude -carduino -patmega1280 -P/dev/ttyACM0 -b57600 -D -Uflash:w:out/klipper.elf.hex:i
```

### Atmega1284p

此芯片通常在 "Melzi" 风格的 3d 打印机板中找到。

要刷写引导加载程序本身，使用类似以下的命令：
```
wget 'https://github.com/Lauszus/Sanguino/raw/1.0.2/bootloaders/optiboot/optiboot_atmega1284p.hex'

avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xFD:m -U hfuse:w:0xDE:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -U flash:w:optiboot_atmega1284p.hex
avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似以下的命令：
```
avrdude -carduino -patmega1284p -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

请注意，许多 "Melzi" 风格的板子预装了使用 57600 波特率的引导加载程序。在这种情况下，请改用类似以下的命令刷写应用程序：
```
avrdude -carduino -patmega1284p -P/dev/ttyACM0 -b57600 -D -Uflash:w:out/klipper.elf.hex:i
```

### At90usb1286

本文档不介绍将引导加载程序刷写到 At90usb1286 的方法，也不介绍此设备的通用应用程序刷写。

pjrc.com 的 Teensy++ 设备附带专有引导加载程序。它需要来自 [https://github.com/PaulStoffregen/teensy_loader_cli](https://github.com/PaulStoffregen/teensy_loader_cli) 的自定义刷写工具。可以使用类似以下的命令刷写应用程序：

```
teensy_loader_cli --mcu=at90usb1286 out/klipper.elf.hex -v
```

### Atmega168

atmega168 的 flash 空间有限。如果使用引导加载程序，建议使用 Optiboot 引导加载程序。要刷写该引导加载程序，使用类似以下的命令：
```
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/optiboot/optiboot_atmega168.hex'

avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0x04:m -U hfuse:w:0xDD:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -U flash:w:optiboot_atmega168.hex
avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要通过 Optiboot 引导加载程序刷写应用程序，使用类似以下的命令：
```
avrdude -carduino -patmega168 -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

## SAM3 微控制器（Arduino Due）

SAM3 mcu 通常不使用引导加载程序。芯片本身具有 ROM，允许从 3.3V 串行端口或 USB 编程 flash。

要启用 ROM，在复位期间将 "erase" 引脚保持高电平，这会擦除 flash 内容并导致 ROM 运行。在 Arduino Due 上，可以通过在 "programming usb port"（最靠近电源的 USB 端口）上设置 1200 波特率来完成此序列。

[https://github.com/shumatech/BOSSA](https://github.com/shumatech/BOSSA) 中的代码可用于编程 SAM3。建议使用 1.9 或更高版本。

要刷写应用程序，使用类似以下的命令：
```
bossac -U -p /dev/ttyACM0 -a -e -w out/klipper.bin -v -b
bossac -U -p /dev/ttyACM0 -R
```

## SAM4 微控制器（Duet Wifi）

SAM4 mcu 通常不使用引导加载程序。芯片本身具有 ROM，允许从 3.3V 串行端口或 USB 编程 flash。

要启用 ROM，在复位期间将 "erase" 引脚保持高电平，这会擦除 flash 内容并导致 ROM 运行。

[https://github.com/shumatech/BOSSA](https://github.com/shumatech/BOSSA) 中的代码可用于编程 SAM4。需要使用版本 `1.8.0` 或更高版本。

要刷写应用程序，使用类似以下的命令：
```
bossac --port=/dev/ttyACM0 -b -U -e -w -v -R out/klipper.bin
```

## SAMDC21 微控制器（Duet3D Toolboard 1LC）

SAMC21 通过 ARM Serial Wire Debug (SWD) 接口刷写。通常使用专用的 SWD 硬件加密狗完成。或者，可以使用 [Raspberry Pi 和 OpenOCD](#在-raspberry-pi-上运行-openocd)。

使用 OpenOCD 和 SAMC21 时，如果板子将 SWD 引脚用于其他目的，必须采取额外步骤首先将芯片置于 Cold Plugging 模式。如果在 Raspberry Pi 上使用 OpenOCD，可以在调用 OpenOCD 之前运行以下命令来完成：
```
SWCLK=25
SWDIO=24
SRST=18

echo "Exporting SWCLK and SRST pins."
echo $SWCLK > /sys/class/gpio/export
echo $SRST > /sys/class/gpio/export
echo "out" > /sys/class/gpio/gpio$SWCLK/direction
echo "out" > /sys/class/gpio/gpio$SRST/direction

echo "Setting SWCLK low and pulsing SRST."
echo "0" > /sys/class/gpio/gpio$SWCLK/value
echo "0" > /sys/class/gpio/gpio$SRST/value
echo "1" > /sys/class/gpio/gpio$SRST/value

echo "Unexporting SWCLK and SRST pins."
echo $SWCLK > /sys/class/gpio/unexport
echo $SRST > /sys/class/gpio/unexport
```

要使用 OpenOCD 刷写程序，请使用以下芯片配置：
```
source [find target/at91samdXX.cfg]
```
获取程序；例如，可以为此芯片构建 Kalico。使用类似以下的 OpenOCD 命令刷写：
```
at91samd chip-erase
at91samd bootloader 0
program out/klipper.elf verify
```

## SAMD21 微控制器（Arduino Zero）

SAMD21 引导加载程序通过 ARM Serial Wire Debug (SWD) 接口刷写。通常使用专用的 SWD 硬件加密狗完成。或者，可以使用 [Raspberry Pi 和 OpenOCD](#在-raspberry-pi-上运行-openocd)。

要使用 OpenOCD 刷写引导加载程序，请使用以下芯片配置：
```
source [find target/at91samdXX.cfg]
```
获取引导加载程序 - 例如：
```
wget 'https://github.com/arduino/ArduinoCore-samd/raw/1.8.3/bootloaders/zero/samd21_sam_ba.bin'
```
使用类似以下的 OpenOCD 命令刷写：
```
at91samd bootloader 0
program samd21_sam_ba.bin verify
```

SAMD21 上最常见的引导加载程序是 "Arduino Zero" 上的那个。它使用 8KiB 引导加载程序（应用程序必须以 8KiB 的起始地址编译）。可以通过双击复位按钮进入此引导加载程序。要刷写应用程序，使用类似以下的命令：
```
bossac -U -p /dev/ttyACM0 --offset=0x2000 -w out/klipper.bin -v -b -R
```

相比之下，"Arduino M0" 使用 16KiB 引导加载程序（应用程序必须以 16KiB 的起始地址编译）。要在此引导加载程序上刷写应用程序，请复位微控制器并在启动后的前几秒内运行刷写命令 - 类似以下：
```
avrdude -c stk500v2 -p atmega2560 -P /dev/ttyACM0 -u -Uflash:w:out/klipper.elf.hex:i
```

## SAMD51 微控制器（Adafruit Metro-M4 及类似设备）

与 SAMD21 类似，SAMD51 引导加载程序通过 ARM Serial Wire Debug (SWD) 接口刷写。要使用 [Raspberry Pi 上的 OpenOCD](#在-raspberry-pi-上运行-openocd) 刷写引导加载程序，请使用以下芯片配置：
```
source [find target/atsame5x.cfg]
```
获取引导加载程序 - 有几个引导加载程序可从 [https://github.com/adafruit/uf2-samdx1/releases/latest](https://github.com/adafruit/uf2-samdx1/releases/latest) 获取。例如：
```
wget 'https://github.com/adafruit/uf2-samdx1/releases/download/v3.7.0/bootloader-itsybitsy_m4-v3.7.0.bin'
```
使用类似以下的 OpenOCD 命令刷写：
```
at91samd bootloader 0
program bootloader-itsybitsy_m4-v3.7.0.bin verify
at91samd bootloader 16384
```

SAMD51 使用 16KiB 引导加载程序（应用程序必须以 16KiB 的起始地址编译）。要刷写应用程序，使用类似以下的命令：
```
bossac -U -p /dev/ttyACM0 --offset=0x4000 -w out/klipper.bin -v -b -R
```

## STM32F103 微控制器（Blue Pill 设备）

STM32F103 设备具有 ROM，可以通过 3.3V 串行端口刷写引导加载程序或应用程序。通常将 PA10（MCU Rx）和 PA9（MCU Tx）引脚连接到 3.3V UART 适配器。要访问 ROM，应将 "boot 0" 引脚连接到高电平，"boot 1" 引脚连接到低电平，然后复位设备。然后可以使用 "stm32flash" 包来刷写设备，类似以下：
```
stm32flash -w out/klipper.bin -v -g 0 /dev/ttyAMA0
```

请注意，如果使用 Raspberry Pi 进行 3.3V 串行通信，stm32flash 协议使用串行奇偶校验模式，而 Raspberry Pi 的 "mini UART" 不支持该模式。有关在 Raspberry Pi GPIO 引脚上启用完整 UART 的详细信息，请参阅 [https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts](https://www.raspberrypi.com/documentation/computers/configuration.html#configuring-uarts)。

刷写后，将 "boot 0" 和 "boot 1" 都设置回低电平，以便将来从 flash 启动复位。

### 带 stm32duino 引导加载程序的 STM32F103

"stm32duino" 项目有一个支持 USB 的引导加载程序 - 请参阅：
[https://github.com/rogerclarkmelbourne/STM32duino-bootloader](https://github.com/rogerclarkmelbourne/STM32duino-bootloader)

此引导加载程序可以通过 3.3V 串行端口刷写，类似以下：
```
wget 'https://github.com/rogerclarkmelbourne/STM32duino-bootloader/raw/master/binaries/generic_boot20_pc13.bin'

stm32flash -w generic_boot20_pc13.bin -v -g 0 /dev/ttyAMA0
```

此引导加载程序使用 8KiB 的 flash 空间（应用程序必须以 8KiB 的起始地址编译）。使用类似以下的命令刷写应用程序：
```
dfu-util -d 1eaf:0003 -a 2 -R -D out/klipper.bin
```

引导加载程序通常在启动后仅运行很短的时间。可能需要计时上述命令，使其在引导加载程序仍处于活动状态时运行（引导加载程序运行时会闪烁板载 LED）。或者，将 "boot 0" 引脚设置为低电平，"boot 1" 引脚设置为高电平，以便在复位后停留在引导加载程序中。

### 带 HID 引导加载程序的 STM32F103

[HID 引导加载程序](https://github.com/Serasidis/STM32_HID_Bootloader) 是一个紧凑的无驱动程序引导加载程序，可以通过 USB 刷写。还有一个 [针对 SKR Mini E3 1.2 的构建分支](https://github.com/Arksine/STM32_HID_Bootloader/releases/latest)。

对于通用的 STM32F103 板（如 blue pill），可以使用上述 stm32duino 部分中提到的 stm32flash 通过 3.3V 串行端口刷写引导加载程序，将文件名替换为所需的 hid 引导加载程序二进制文件（例如：blue pill 的 hid_generic_pc13.bin）。

对于 SKR Mini E3，无法使用 stm32flash，因为 boot0 引脚直接接地，没有通过排针引出。建议使用 STLink V2 和 STM32Cubeprogrammer 刷写引导加载程序。如果您没有 STLink，也可以使用 [Raspberry Pi 和 OpenOCD](#在-raspberry-pi-上运行-openocd)，使用以下芯片配置：

```
source [find target/stm32f1x.cfg]
```
如果您愿意，可以使用以下命令备份当前 flash。请注意，完成可能需要一些时间：
```
flash read_bank 0 btt_skr_mini_e3_backup.bin
```
最后，您可以使用类似以下的命令刷写：
```
stm32f1x mass_erase 0
program hid_btt_skr_mini_e3.bin verify 0x08000000
```
注意事项：
- 上面的示例擦除芯片然后编程引导加载程序。无论选择哪种刷写方法，都建议在刷写前擦除芯片。
- 在使用此引导加载程序刷写 SKR Mini E3 之前，您应该知道您将无法再通过 sdcard 更新固件。
- 您可能需要在启动 OpenOCD 时按住板上的复位按钮。它应该显示类似以下内容：
  ```
  Open On-Chip Debugger 0.10.0+dev-01204-gc60252ac-dirty (2020-04-27-16:00)
  Licensed under GNU GPL v2
  For bug reports, read
          http://openocd.org/doc/doxygen/bugs.html
  DEPRECATED! use 'adapter speed' not 'adapter_khz'
  Info : BCM2835 GPIO JTAG/SWD bitbang driver
  Info : JTAG and SWD modes enabled
  Info : clock speed 40 kHz
  Info : SWD DPIDR 0x1ba01477
  Info : stm32f1x.cpu: hardware has 6 breakpoints, 4 watchpoints
  Info : stm32f1x.cpu: external reset detected
  Info : starting gdb server for stm32f1x.cpu on 3333
  Info : Listening on port 3333 for gdb connections
  ```
  然后您可以释放复位按钮。

此引导加载程序需要 2KiB 的 flash 空间（应用程序必须以 2KiB 的起始地址编译）。

hid-flash 程序用于将二进制文件上传到引导加载程序。您可以使用以下命令安装此软件：
```
sudo apt install libusb-1.0
cd ~/klipper/lib/hidflash
make
```

如果引导加载程序正在运行，您可以使用类似以下的命令刷写：
```
~/klipper/lib/hidflash/hid-flash ~/klipper/out/klipper.bin
```
或者，您可以使用 `make flash` 直接刷写 Kalico：
```
make flash FLASH_DEVICE=1209:BEBA
```
或者，如果之前已经刷写过 Kalico：
```
make flash FLASH_DEVICE=/dev/ttyACM0
```

可能需要手动进入引导加载程序，可以通过将 "boot 0" 设置为低电平，"boot 1" 设置为高电平来完成。在 SKR Mini E3 上 "Boot 1" 不可用，因此如果您刷写了 "hid_btt_skr_mini_e3.bin"，可以通过将 PA2 引脚设置为低电平来完成。此引脚在 SKR Mini E3 的 "PIN" 文档中的 TFT 排针上标记为 "TX0"。PA2 旁边有一个接地引脚，您可以用它将 PA2 拉低。

### 带 MSC 引导加载程序的 STM32F103/STM32F072

[MSC 引导加载程序](https://github.com/Telekatz/MSC-stm32f103-bootloader) 是一个无驱动程序引导加载程序，可以通过 USB 刷写。

可以使用上述 stm32duino 部分中提到的 stm32flash 通过 3.3V 串行端口刷写引导加载程序，将文件名替换为所需的 MSC 引导加载程序二进制文件（例如：blue pill 的 MSCboot-Bluepill.bin）。

对于 STM32F072 板，也可以通过 USB（通过 DFU）刷写引导加载程序，类似以下：

```
 dfu-util -d 0483:df11 -a 0 -R -D  MSCboot-STM32F072.bin -s0x08000000:leave
```

此引导加载程序使用 8KiB 或 16KiB 的 flash 空间，请参阅引导加载程序的说明（应用程序必须以相应的起始地址编译）。

可以通过按两次板上的复位按钮来激活引导加载程序。一旦引导加载程序被激活，板子将作为 USB 闪存驱动器出现，可以将 klipper.bin 文件复制到其中。

### 带 CanBoot 引导加载程序的 STM32F103/STM32F0x2

[CanBoot](https://github.com/Arksine/CanBoot) 引导加载程序提供了通过 CANBUS 上传 Kalico 固件的选项。引导加载程序本身源自 Kalico 的源代码。目前 CanBoot 支持 STM32F103、STM32F042 和 STM32F072 型号。

建议使用 ST-Link Programmer 刷写 CanBoot，但应该可以在 STM32F103 设备上使用 `stm32flash`，在 STM32F042/STM32F072 设备上使用 `dfu-util` 刷写。有关这些刷写方法的说明，请参阅本文档前面的部分，在适当的地方将 `canboot.bin` 替换为文件名。上面链接的 CanBoot 存储库提供了构建引导加载程序的说明。

第一次刷写 CanBoot 时，它应该检测到没有应用程序并进入引导加载程序。如果这没有发生，可以通过连续按两次复位按钮进入引导加载程序。

`lib/canboot` 文件夹中提供的 `flash_can.py` 工具可用于上传 Kalico 固件。刷写需要设备 UUID。如果您没有 UUID，可以查询当前运行引导加载程序的节点：
```
python3 flash_can.py -q
```
这将返回所有当前未分配 UUID 的已连接节点的 UUID。这应该包括所有当前在引导加载程序中的节点。

获得 UUID 后，您可以使用以下命令上传固件：
```
python3 flash_can.py -i can0 -f ~/klipper/out/klipper.bin -u aabbccddeeff
```

其中 `aabbccddeeff` 替换为您的 UUID。请注意，`-i` 和 `-f` 选项可以省略，它们分别默认为 `can0` 和 `~/klipper/out/klipper.bin`。

构建与 CanBoot 一起使用的 Kalico 时，选择 8 KiB Bootloader 选项。

## STM32F4 微控制器（SKR Pro 1.1）

STM32F4 微控制器配备了内置系统引导加载程序，可以通过 USB（通过 DFU）、3.3V 串行端口和各种其他方法刷写（有关更多信息，请参阅 STM 文档 AN2606）。一些 STM32F4 板（如 SKR Pro 1.1）无法进入 DFU 引导加载程序。对于基于 STM32F405/407 的板子，如果用户更喜欢通过 USB 刷写而不是使用 sdcard，可以使用 HID 引导加载程序。请注意，您可能需要配置并构建特定于您的板子的版本，[SKR Pro 1.1 的构建在此处可用](https://github.com/Arksine/STM32_HID_Bootloader/releases/latest)。

除非您的板子支持 DFU，否则最方便的刷写方法可能是通过 3.3V 串行端口，这遵循与 [使用 stm32flash 刷写 STM32F103](#stm32f103-微控制器blue-pill-设备) 相同的过程。例如：
```
wget https://github.com/Arksine/STM32_HID_Bootloader/releases/download/v0.5-beta/hid_bootloader_SKR_PRO.bin

stm32flash -w hid_bootloader_SKR_PRO.bin -v -g 0 /dev/ttyAMA0
```

此引导加载程序在 STM32F4 上需要 16KiB 的 flash 空间（应用程序必须以 16KiB 的起始地址编译）。

与 STM32F1 一样，STM32F4 使用 hid-flash 工具将二进制文件上传到 MCU。有关如何构建和使用 hid-flash 的详细信息，请参阅上面的说明。

可能需要手动进入引导加载程序，可以通过将 "boot 0" 设置为低电平，"boot 1" 设置为高电平并插入设备来完成。编程完成后，拔掉设备并将 "boot 1" 设置回低电平，以便加载应用程序。

## LPC176x 微控制器（Smoothieboards）

本文档不描述刷写引导加载程序本身的方法 - 有关该主题的更多信息，请参阅：
[http://smoothieware.org/flashing-the-bootloader](http://smoothieware.org/flashing-the-bootloader)

Smoothieboards 通常附带来自 [https://github.com/triffid/LPC17xx-DFU-Bootloader](https://github.com/triffid/LPC17xx-DFU-Bootloader) 的引导加载程序。使用此引导加载程序时，应用程序必须以 16KiB 的起始地址编译。使用此引导加载程序刷写应用程序的最简单方法是将应用程序文件（例如 `out/klipper.bin`）复制到 SD 卡上名为 `firmware.bin` 的文件，然后使用该 SD 卡重新启动微控制器。

## 在 Raspberry Pi 上运行 OpenOCD

OpenOCD 是一个软件包，可以执行底层芯片刷写和调试。它可以使用 Raspberry Pi 上的 GPIO 引脚与各种 ARM 芯片通信。

本节介绍如何安装和启动 OpenOCD。它源自以下说明：
[https://learn.adafruit.com/programming-microcontrollers-using-openocd-on-raspberry-pi](https://learn.adafruit.com/programming-microcontrollers-using-openocd-on-raspberry-pi)

首先下载并编译软件（每个步骤可能需要几分钟，"make" 步骤可能需要 30 分钟以上）：

```
sudo apt-get update
sudo apt-get install autoconf libtool telnet
mkdir ~/openocd
cd ~/openocd/
git clone http://openocd.zylin.com/openocd
cd openocd
./bootstrap
./configure --enable-sysfsgpio --enable-bcm2835gpio --prefix=/home/pi/openocd/install
make
make install
```

### 配置 OpenOCD

创建一个 OpenOCD 配置文件：

```
nano ~/openocd/openocd.cfg
```

使用类似以下的配置：

```
# Uses RPi pins: GPIO25 for SWDCLK, GPIO24 for SWDIO, GPIO18 for nRST
source [find interface/raspberrypi2-native.cfg]
bcm2835gpio_swd_nums 25 24
bcm2835gpio_srst_num 18
transport select swd

# Use hardware reset wire for chip resets
reset_config srst_only
adapter_nsrst_delay 100
adapter_nsrst_assert_width 100

# Specify the chip type
source [find target/atsame5x.cfg]

# Set the adapter speed
adapter_khz 40

# Connect to chip
init
targets
reset halt
```

### 将 Raspberry Pi 连接到目标芯片

在接线之前，请关闭 Raspberry Pi 和目标芯片的电源！在连接到 Raspberry Pi 之前，请验证目标芯片使用 3.3V！

将目标芯片上的 GND、SWDCLK、SWDIO 和 RST 分别连接到 Raspberry Pi 上的 GND、GPIO25、GPIO24 和 GPIO18。

然后打开 Raspberry Pi 的电源并为目标芯片供电。

### 运行 OpenOCD

运行 OpenOCD：

```
cd ~/openocd/
sudo ~/openocd/install/bin/openocd -f ~/openocd/openocd.cfg
```

上述操作应该会使 OpenOCD 输出一些文本消息然后等待（它不应该立即返回到 Unix shell 提示符）。如果 OpenOCD 自行退出或继续输出文本消息，请仔细检查接线。

一旦 OpenOCD 正在运行且稳定，可以通过 telnet 向其发送命令。打开另一个 ssh 会话并运行以下命令：

```
telnet 127.0.0.1 4444
```

（可以通过按 ctrl+] 然后运行 "quit" 命令退出 telnet。）

### OpenOCD 和 gdb

可以将 OpenOCD 与 gdb 一起使用来调试 Kalico。以下命令假设在桌面计算机上运行 gdb。

将以下内容添加到 OpenOCD 配置文件：

```
bindto 0.0.0.0
gdb_port 44444
```

在 Raspberry Pi 上重启 OpenOCD，然后在桌面计算机上运行以下 Unix 命令：

```
cd /path/to/klipper/
gdb out/klipper.elf
```

在 gdb 中运行：

```
target remote octopi:44444
```

（将 "octopi" 替换为 Raspberry Pi 的主机名。）一旦 gdb 正在运行，就可以设置断点并检查寄存器。