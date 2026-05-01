# RPi 微控制器

本文档描述了在树莓派（RPi）上运行 Kalico 且将同一树莓派用作辅助 MCU（微控制器）的过程。

## 为什么将树莓派用作辅助 MCU？

通常用于控制 3D 打印机的 MCU 具有有限且预配置数量的暴露引脚来管理主要打印功能（热敏电阻、挤出机、步进电机等）。将安装 Kalico 的树莓派用作辅助 MCU 可以直接在 Kalico 内使用树莓派的 GPIO（通用输入输出）和总线（I2C、SPI），无需使用 OctoPrint 插件（如果使用）或外部程序，从而能够在打印 GCODE 内控制一切。

**警告**：如果您的平台是 _Beaglebone_ 且您已正确按照安装步骤操作，则 Linux MCU 已经安装并为您的系统配置好了。

## 安装 rc 脚本

如果您想将主机用作辅助 MCU，则 klipper_mcu 进程必须在 klippy 进程之前运行。

安装 Kalico 后，安装脚本。运行：
```
cd ~/klipper/
sudo cp ./scripts/klipper-mcu.service /etc/systemd/system/
sudo systemctl enable klipper-mcu.service
```

## 构建微控制器代码

要编译 Kalico 微控制器代码，首先为其配置"Linux process"：
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

如果 klippy.log 报告尝试连接到 `/tmp/klipper_host_mcu` 时出现"Permission denied"错误，则需要将您的用户添加到 tty 组。以下命令将"pi"用户添加到 tty 组：
```
sudo usermod -a -G tty pi
```

## 剩余配置

按照 [RaspberryPi 示例配置](../config/sample-raspberry-pi.cfg)和[多 MCU 示例配置](../config/sample-multi-mcu.cfg)中的说明完成 Kalico 辅助 MCU 的安装配置。

## 可选：启用 SPI

通过运行 `sudo raspi-config` 并在"Interfacing options"菜单下启用 SPI 来确保 Linux SPI 驱动程序已启用。

## 可选：启用 I2C

通过运行 `sudo raspi-config` 并在"Interfacing options"菜单下启用 I2C 来确保 Linux I2C 驱动程序已启用。
如果计划将 I2C 用于 MPU 加速度计，还需要通过在 `/boot/config.txt`（或某些发行版中的 `/boot/firmware/config.txt`）中添加/取消注释 `dtparam=i2c_arm=on,i2c_arm_baudrate=400000` 来将波特率设置为 400000。

## 可选：识别正确的 gpiochip

在树莓派和许多克隆板上，GPIO 上暴露的引脚属于第一个 gpiochip。因此，可以通过名称 `gpio0..n` 简单地在 Kalico 中引用它们。但是，在某些情况下，暴露的引脚属于第一个以外的 gpiochip。例如，在 OrangePi 某些型号或使用端口扩展器的情况下。在这些情况下，使用命令访问 _Linux GPIO 字符设备_ 来验证配置很有用。

要在基于 Debian 的发行版（如 OctoPi）上安装 _Linux GPIO 字符设备 - 二进制文件_，运行：
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

因此，所选引脚可以在配置中使用为 `gpiochip<n>/gpio<o>`，其中 **n** 是 `gpiodetect` 命令看到的芯片编号，**o** 是 `gpioinfo` 命令看到的线编号。

***警告：*** 只有标记为 `unused` 的 GPIO 可以使用。一条 _线_ 不能同时被多个进程使用。

例如，在树莓派 3B+ 上，Kalico 使用 GPIO20 作为开关：
```
$ gpiodetect
gpiochip0 [pinctrl-bcm2835] (54 lines)
gpiochip1 [raspberrypi-exp-gpio] (8 lines)

$ gpioinfo
gpiochip0 - 54 lines:
        line   0:      unnamed       unused   input  active-high
        line   1:      unnamed       unused   input  active-high
        ...
        line  20:      unnamed    "klipper"  output  active-high [used]
        ...
```

## 可选：硬件 PWM

树莓派有两个 PWM 通道（PWM0 和 PWM1），它们暴露在排针上，或者如果没有，可以路由到现有的 GPIO 引脚。Linux MCU 守护进程使用 pwmchip sysfs 接口来控制 Linux 主机上的硬件 PWM 设备。PWM sysfs 接口在树莓派上默认不暴露，可以通过在 `/boot/config.txt` 中添加一行来激活：
```
# 启用 pwmchip sysfs 接口
dtoverlay=pwm,pin=12,func=4
```
此示例仅启用 PWM0 并将其路由到 gpio12。如果需要启用两个 PWM 通道，可以使用 `pwm-2chan`：
```
# 启用 pwmchip sysfs 接口
dtoverlay=pwm-2chan,pin=12,func=4,pin2=13,func2=4
```
此示例额外启用 PWM1 并将其路由到 gpio13。

叠加层不会在启动时在 sysfs 上暴露 PWM 线，需要通过将 PWM 通道编号 echo 到 `/sys/class/pwm/pwmchip0/export` 来导出。这将在文件系统中创建设备 `/sys/class/pwm/pwmchip0/pwm0`。最简单的方法是在 `/etc/rc.local` 中 `exit 0` 行之前添加以下内容：
```
# 启用 pwmchip sysfs 接口
echo 0 > /sys/class/pwm/pwmchip0/export
```

有了 sysfs，您现在可以通过将以下配置添加到 `printer.cfg` 来使用 PWM 通道：
```
[output_pin caselight]
pin: host:pwmchip0/pwm0
pwm: True
hardware_pwm: True
cycle_time: 0.000001
```

PWM0 可以路由到 gpio12 和 gpio18，PWM1 可以路由到 gpio13 和 gpio19：

| PWM | GPIO 引脚 | 功能 |
| --- | -------- | ---- |
|   0 |       12 |    4 |
|   0 |       18 |    2 |
