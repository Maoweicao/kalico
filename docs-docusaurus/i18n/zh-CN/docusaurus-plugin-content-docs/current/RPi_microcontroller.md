# RPi 微控制器

本文档描述在 RPi 上运行 Kalico 并将同一 RPi 用作辅助 MCU 的过程。

## 为什么使用 RPi 作为辅助 MCU？

通常，专用于控制 3D 打印机的 MCU 具有有限且预配置数量的引脚来管理主要打印功能（热敏电阻、挤出机、步进器...）。将安装了 Kalico 的 RPi 用作辅助 MCU，可以无需使用 OctoPrint 插件（如果使用）或外部程序，直接在 Kalico 中使用 RPi 的 GPIO 和总线（i2c、spi），从而能够通过打印 GCODE 控制所有内容。

**警告**：如果你的平台是 _Beaglebone_ 并且你已正确遵循安装步骤，Linux MCU 已安装并为你的系统配置。

## 安装 rc 脚本

如果你想将主机用作辅助 MCU，klipper_mcu 进程必须在 klippy 进程之前运行。

安装 Kalico 后，安装脚本。运行：
```
cd ~/klipper/
sudo cp ./scripts/klipper-mcu.service /etc/systemd/system/
sudo systemctl enable klipper-mcu.service
```

## 构建微控制器代码

要编译 Kalico 微控制器代码，首先将其配置为"Linux 进程"：
```
cd ~/klipper/
make menuconfig
```

在菜单中，将"Microcontroller Architecture"设置为"Linux process"，然后保存并退出。

要构建和安装新的微控制器代码，运行：
```
sudo service klipper stop
make flash
sudo service klipper start
```

如果 klippy.log 在尝试连接到 `/tmp/klipper_host_mcu` 时报告"Permission denied"错误，则需要将用户添加到 tty 组。以下命令将"pi"用户添加到 tty 组：
```
sudo usermod -a -G tty pi
```

## 剩余配置

通过按照 [RaspberryPi 示例配置](../config/sample-raspberry-pi.cfg) 和 [Multi MCU 示例配置](../config/sample-multi-mcu.cfg) 中的说明配置 Kalico 辅助 MCU 来完成安装。

## 可选：启用 SPI

通过运行 `sudo raspi-config` 并在"Interfacing options"菜单中启用 SPI 来确保 Linux SPI 驱动已启用。

## 可选：启用 I2C

通过运行 `sudo raspi-config` 并在"Interfacing options"菜单中启用 I2C 来确保 Linux I2C 驱动已启用。如果计划将 I2C 用于 MPU 加速度计，还需要通过在 `/boot/config.txt`（或某些发行版中的 `/boot/firmware/config.txt`）中添加/取消注释 `dtparam=i2c_arm=on,i2c_arm_baudrate=400000` 将波特率设置为 400000。

## 可选：识别正确的 gpiochip

在 Raspberry Pi 和许多克隆产品上，GPIO 上暴露的引脚属于第一个 gpiochip。因此，只需通过名称 `gpio0..n` 引用它们即可在 Kalico 中使用它们。但是，在某些情况下，暴露的引脚属于第一个以外的 gpiochip。例如，在某些 OrangePi 型号的情况下或如果使用端口扩展器。在这些情况下，使用命令访问 _Linux GPIO 字符设备_ 来验证配置很有用。

要将 _Linux GPIO 字符设备 - 二进制文件_ 安装在基于 debian 的发行版（如 octopi）上，运行：
```
sudo apt-get install gpiod
```

要检查可用的 gpiochip，运行：
```
gpiodetect
```

要检查引脚编号和引脚可用性，运行：
```
gpioinfo
```

因此，所选引脚可以在配置中用作 `gpiochip<n>/gpio<o>`，其中 **n** 是 `gpiodetect` 命令看到的芯片编号，**o** 是 `gpioinfo` 命令看到的行编号。

***警告：*** 只有标记为 `unused` 的 gpio 才能使用。一个 _line_ 不能同时被多个进程使用。

例如，在 Kalico 使用 GPIO20 作为开关的 RPi 3B+ 上：
```
$ gpiodetect
gpiochip0 [pinctrl-bcm2835] (54 lines)
gpiochip1 [raspberrypi-exp-gpio] (8 lines)

$ gpioinfo
gpiochip0 - 54 lines:
        line   0:      unnamed       unused   input  active-high
        line   1:      unnamed       unused   input  active-high
        line   2:      unnamed       unused   input  active-high
        line   3:      unnamed       unused   input  active-high
        line   4:      unnamed       unused   input  active-high
        line   5:      unnamed       unused   input  active-high
        line   6:      unnamed       unused   input  active-high
        line   7:      unnamed       unused   input  active-high
        line   8:      unnamed       unused   input  active-high
        line   9:      unnamed       unused   input  active-high
        line  10:      unnamed       unused   input  active-high
        line  11:      unnamed       unused   input  active-high
        line  12:      unnamed       unused   input  active-high
        line  13:      unnamed       unused   input  active-high
        line  14:      unnamed       unused   input  active-high
        line  15:      unnamed       unused   input  active-high
        line  16:      unnamed       unused   input  active-high
        line  17:      unnamed       unused   input  active-high
        line  18:      unnamed       unused   input  active-high
        line  19:      unnamed       unused   input  active-high
        line  20:      unnamed    "klipper"  output  active-high [used]
        line  21:      unnamed       unused   input  active-high
        line  22:      unnamed       unused   input  active-high
        line  23:      unnamed       unused   input  active-high
        line  24:      unnamed       unused   input  active-high
        line  25:      unnamed       unused   input  active-high
        line  26:      unnamed       unused   input  active-high
        line  27:      unnamed       unused   input  active-high
        line  28:      unnamed       unused   input  active-high
        line  29:      unnamed       "led0"  output  active-high [used]
        line  30:      unnamed       unused   input  active-high
        line  31:      unnamed       unused   input  active-high
        line  32:      unnamed       unused   input  active-high
        line  33:      unnamed       unused   input  active-high
        line  34:      unnamed       unused   input  active-high
        line  35:      unnamed       unused   input  active-high
        line  36:      unnamed       unused   input  active-high
        line  37:      unnamed       unused   input  active-high
        line  38:      unnamed       unused   input  active-high
        line  39:      unnamed       unused   input  active-high
        line  40:      unnamed       unused   input  active-high
        line  41:      unnamed       unused   input  active-high
        line  42:      unnamed       unused   input  active-high
        line  43:      unnamed       unused   input  active-high
        line  44:      unnamed       unused   input  active-high
        line  45:      unnamed       unused   input  active-high
        line  46:      unnamed       unused   input  active-high
        line  47:      unnamed       unused   input  active-high
        line  48:      unnamed       unused   input  active-high
        line  49:      unnamed       unused   input  active-high
        line  50:      unnamed       unused   input  active-high
        line  51:      unnamed       unused   input  active-high
        line  52:      unnamed       unused   input  active-high
        line  53:      unnamed       unused   input  active-high
gpiochip1 - 8 lines:
        line   0:      unnamed       unused   input  active-high
        line   1:      unnamed       unused   input  active-high
        line   2:      unnamed       "led1"  output   active-low [used]
        line   3:      unnamed       unused   input  active-high
        line   4:      unnamed       unused   input  active-high
        line   5:      unnamed       unused   input  active-high
        line   6:      unnamed       unused   input  active-high
        line   7:      unnamed       unused   input  active-high
```

## 可选：硬件 PWM

Raspberry Pi 有两个 PWM 通道（PWM0 和 PWM1），在排针上暴露，或者如果不可用，可以路由到现有的 gpio 引脚。Linux MCU 守护进程使用 pwmchip sysfs 接口控制 Linux 主机上的硬件 pwm 设备。pwm sysfs 接口默认不暴露在 Raspberry Pi 上，可以通过向 `/boot/config.txt` 添加一行来激活：
```
# Enable pwmchip sysfs interface
dtoverlay=pwm,pin=12,func=4
```
此示例仅启用 PWM0 并将其路由到 gpio12。如果需要同时启用两个 PWM 通道，可以使用 `pwm-2chan`：
```
# Enable pwmchip sysfs interface
dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
```
此示例另外启用 PWM1 并将其路由到 gpio13。

overlay 不会在启动时在 sysfs 上暴露 pwm 线，需要通过将 pwm 通道编号回显到 `/sys/class/pwm/pwmchip0/export` 来导出。这将在文件系统中创建设备 `/sys/class/pwm/pwmchip0/pwm0`。最简单的方法是在 `/etc/rc.local` 中的 `exit 0` 行之前添加以下内容：
```
# Enable pwmchip sysfs interface
echo 0 > /sys/class/pwm/pwmchip0/export
```
使用两个 PWM 通道时，还需要回显第二个通道的编号：
```
# Enable pwmchip sysfs interface
echo 0 > /sys/class/pwm/pwmchip0/export
echo 1 > /sys/class/pwm/pwmchip0/export
```

sysfs 就位后，可以通过向 `printer.cfg` 添加以下配置来使用 pwm 通道：
```
[output_pin caselight]
pin: host:pwmchip0/pwm0
pwm: True
hardware_pwm: True
cycle_time: 0.000001

[output_pin beeper]
pin: host:pwmchip0/pwm1
pwm: True
hardware_pwm: True
value: 0
shutdown_value: 0
cycle_time: 0.0005
```
这将为 Pi 上的 gpio12 和 gpio13 添加硬件 pwm 控制（因为 overlay 被配置为将 pwm0 路由到 pin=12，pwm1 路由到 pin=13）。

PWM0 可以路由到 gpio12 和 gpio18，PWM1 可以路由到 gpio13 和 gpio19：

| PWM | gpio PIN | 功能 |
| --- | -------- | ---- |
| 0 | 12 | 4 |
| 0 | 18 | 2 |
| 1 | 13 | 4 |
| 1 | 19 | 2 |
