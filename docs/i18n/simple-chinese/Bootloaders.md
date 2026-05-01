# 引导加载程序

本文档提供了有关Kalico支持的微控制器上常见的引导加载程序的信息。

引导加载程序是在微控制器首次启动时运行的第三方软件。它通常用于在不需要专门硬件的情况下将新应用程序（如Kalico）刷写到微控制器。遗憾的是，目前还没有行业范围内的微控制器刷写标准，也没有适用于所有微控制器的标准引导加载程序。更糟糕的是，每个引导加载程序通常都需要不同的步骤来刷写应用程序。

如果能向微控制器刷写引导加载程序，则通常也可以使用该机制来刷写应用程序，但这样做时要谨慎，因为您可能会无意中删除引导加载程序。相比之下，引导加载程序通常只允许用户刷写应用程序。因此，建议在可能的情况下使用引导加载程序来刷写应用程序。

本文档试图描述常见的引导加载程序、刷写引导加载程序所需的步骤以及刷写应用程序所需的步骤。本文档不是权威参考；它旨在作为Kalico开发人员积累的有用信息的汇编。

## AVR微控制器

一般来说，Arduino项目是8位Atmel Atmega微控制器的引导加载程序和刷写程序的良好参考。特别是"boards.txt"文件：
[https://github.com/arduino/Arduino/blob/1.8.5/hardware/arduino/avr/boards.txt](https://github.com/arduino/Arduino/blob/1.8.5/hardware/arduino/avr/boards.txt)

是一个有用的参考资料。

要刷写引导加载程序本身，AVR芯片需要一个外部硬件刷写工具（使用SPI与芯片通信）。这种工具可以购买（例如，在网络上搜索"avr isp"、"arduino isp"或"usb tiny isp"）。也可以使用另一个Arduino或树莓派来刷写AVR引导加载程序（例如，搜索"program an avr using raspberry pi"）。下面的示例假设使用"AVR ISP Mk2"类型的设备。

"avrdude"程序是刷写atmega芯片（引导加载程序刷写和应用程序刷写）的最常用工具。

### Atmega2560

这个芯片通常在"Arduino Mega"中找到，在3D打印机主板中非常常见。

要刷写引导加载程序本身，使用类似的命令：
```
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/stk500v2/stk500boot_v2_mega2560.hex'

avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xFD:m -U hfuse:w:0xD8:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -U flash:w:stk500boot_v2_mega2560.hex
avrdude -cavrispv2 -patmega2560 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似的命令：
```
avrdude -cwiring -patmega2560 -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

### Atmega1280

这个芯片通常在较早版本的"Arduino Mega"中找到。

要刷写引导加载程序本身，使用类似的命令：
`````````
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/atmega/ATmegaBOOT_168_atmega1280.hex'

avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xF5:m -U hfuse:w:0xDA:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -U flash:w:ATmegaBOOT_168_atmega1280.hex
avrdude -cavrispv2 -patmega1280 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似的命令：
```
avrdude -carduino -patmega1280 -P/dev/ttyACM0 -b57600 -D -Uflash:w:out/klipper.elf.hex:i
```

### Atmega1284p

这个芯片通常在"Melzi"风格的3D打印机主板中找到。

要刷写引导加载程序本身，使用类似的命令：
``````
wget 'https://github.com/Lauszus/Sanguino/raw/1.0.2/bootloaders/optiboot/optiboot_atmega1284p.hex'

avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0xFD:m -U hfuse:w:0xDE:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -U flash:w:optiboot_atmega1284p.hex
avrdude -cavrispv2 -patmega1284p -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要刷写应用程序，使用类似的命令：
```
avrdude -carduino -patmega1284p -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

请注意，许多"Melzi"风格的主板预装了使用57600波特率的引导加载程序。在这种情况下，要刷写应用程序，使用这样的命令：
```
avrdude -carduino -patmega1284p -P/dev/ttyACM0 -b57600 -D -Uflash:w:out/klipper.elf.hex:i
```

### At90usb1286

本文档不涵盖向At90usb1286刷写引导加载程序的方法，也不涵盖该设备上的一般应用程序刷写。

Teensy++设备来自pjrc.com，配备专有引导加载程序。它需要一个自定义的刷写工具：
[https://github.com/PaulStoffregen/teensy_loader_cli](https://github.com/PaulStoffregen/teensy_loader_cli)

可以使用类似的命令刷写应用程序：
```
teensy_loader_cli --mcu=at90usb1286 out/klipper.elf.hex -v
```

### Atmega168

Atmega168的闪存空间有限。如果使用引导加载程序，建议使用Optiboot引导加载程序。要刷写引导加载程序，使用类似的命令：
```
wget 'https://github.com/arduino/Arduino/raw/1.8.5/hardware/arduino/avr/bootloaders/optiboot/optiboot_atmega168.hex'

avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -e -u -U lock:w:0x3F:m -U efuse:w:0x04:m -U hfuse:w:0xDD:m -U lfuse:w:0xFF:m
avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -U flash:w:optiboot_atmega168.hex
avrdude -cavrispv2 -patmega168 -P/dev/ttyACM0 -b115200 -U lock:w:0x0F:m
```

要通过Optiboot引导加载程序刷写应用程序，使用类似的命令：
```
avrdude -carduino -patmega168 -P/dev/ttyACM0 -b115200 -D -Uflash:w:out/klipper.elf.hex:i
```

## SAM3微控制器（Arduino Due）

SAM3 MCU通常不使用引导加载程序。该芯片本身有一个ROM，允许从3.3V串行端口或USB编程闪存。

要启用ROM，"erase"引脚在复位期间保持高电平，这会擦除闪存内容，并导致ROM运行。在Arduino Due上，可以通过在"programming usb port"（USB端口最靠近电源）上设置1200波特率来完成此序列。

[https://github.com/shumatech/BOSSA](https://github.com/shumatech/BOSSA)上的代码可以用来编程SAM3。建议使用1.9或更高版本。

要刷写应用程序，使用类似的命令：
```
bossac -U -p /dev/ttyACM0 -a -e -w out/klipper.bin -v -b
bossac -U -p /dev/ttyACM0 -R
```

## SAM4微控制器（Duet Wifi）

SAM4 MCU通常不使用引导加载程序。该芯片本身有一个ROM，允许从3.3V串行端口或USB编程闪存。

要启用ROM，"erase"引脚在复位期间保持高电平，这会擦除闪存内容，并导致ROM运行。

[https://github.com/shumatech/BOSSA](https://github.com/shumatech/BOSSA)上的代码可以用来编程SAM4。必须使用`1.8.0`或更高版本。

要刷写应用程序，使用类似的命令：
```
bossac --port=/dev/ttyACM0 -b -U -e -w -v -R out/klipper.bin