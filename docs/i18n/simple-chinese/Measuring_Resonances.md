# 测量共振

Kalico内置支持ADXL345、MPU-9250和LIS2DW兼容的加速度计，可用于测量打印机不同轴的共振频率，并自动调整[输入整形器](Resonance_Compensation.md)来补偿共振。请注意，使用加速度计需要进行一些焊接和压接。ADXL345/LIS2DW可以连接到树莓派或MCU主板的SPI接口（需要相当快）。MPU系列可以直接连接到树莓派的I2C接口，或连接到支持400kbit/s*快速模式*的MCU主板的I2C接口。

采购加速度计时，请注意有多种不同的PCB电路板设计和不同的克隆产品。如果要连接到5V打印机MCU，请确保它有电压调节器和电平移位器。

对于ADXL345s/LIS2DWs，请确保电路板支持SPI模式（少数电路板似乎通过将SDO拉低到GND来硬配置为I2C）。

对于MPU-9250/MPU-9255/MPU-6515/MPU-6050/MPU-6500/ICM20948s和LIS2DW/LIS3DH，也有多种电路板设计和具有不同I2C上拉电阻的克隆产品，这些需要补充。

## 支持Kalico I2C*快速模式*的MCU

| MCU系列 | 测试过的MCU | 支持的MCU |
|:--:|:--|:--|
| 树莓派 | 3B+, Pico | 3A, 3A+, 3B, 4 |
| AVR ATmega | ATmega328p | ATmega32u4, ATmega128, ATmega168, ATmega328, ATmega644p, ATmega1280, ATmega1284, ATmega2560 |
| AVR AT90 | - | AT90usb646, AT90usb1286 |

## 安装说明

### 布线

对于长距离的信号完整性，建议使用带屏蔽双绞线的以太网电缆（cat5e或更好）。如果仍然遇到信号完整性问题（SPI/I2C错误）：

- 使用数字万用表仔细检查接线：
  - 关闭时的正确连接（连续性）
  - 正确的电源和地电压
- 仅限I2C：
  - 检查SCL和SDA线对3.3V的电阻在900欧到1.8K范围内
  - 有关完整的技术细节，请查阅[I2C总线规范和用户手册UM10204第7章](https://www.pololu.com/file/0J435/UM10204.pdf)了解*快速模式*
- 缩短电缆

仅将以太网电缆屏蔽连接到MCU主板/Pi接地。

***通电前请仔细检查布线，以防止损坏MCU/树莓派或加速度计。***

### SPI加速度计

建议的三条双绞线对的顺序：

```
GND+MISO
3.3V+MOSI
SCLK+CS
```

请注意，与电缆屏蔽不同，必须在两端连接GND。

#### ADXL345

##### 直接连接到树莓派

**注意：许多MCU可以以SPI模式与ADXL345配合工作（例如Pi Pico），布线和配置将根据您的特定主板和可用的引脚而有所不同。**

需要通过SPI将ADXL345连接到树莓派。请注意，ADXL345文档建议的I2C连接吞吐量太低，**无法工作**。推荐的连接方案：

| ADXL345引脚 | RPi引脚 | RPi引脚名称 |
|:--:|:--:|:--:|
| 3V3 (或VCC) | 01 | 3.3V直流电源 |
| GND | 06 | 接地 |
| CS | 24 | GPIO08 (SPI0_CE0_N) |
| SDO | 21 | GPIO09 (SPI0_MISO) |
| SDA | 19 | GPIO10 (SPI0_MOSI) |
| SCL | 23 | GPIO11 (SPI0_SCLK) |

某些ADXL345电路板的Fritzing接线图：

![ADXL345-Rpi](img/adxl345-fritzing.png)

##### 使用树莓派Pico

您可以将ADXL345连接到树莓派Pico，然后通过USB将Pico连接到树莓派。这样可以轻松在其他Kalico设备上重复使用加速度计，因为您可以通过USB而不是GPIO连接。Pico的处理能力不强，因此请确保它只运行加速度计，不执行任何其他任务。

为了避免对RPi的损坏，请确保仅将ADXL345连接到3.3V。根据电路板的布局，可能存在电平移位器，这使得5V对您的RPi很危险。

| ADXL345引脚 | Pico引脚 | Pico引脚名称 |
|:--:|:--:|:--:|
| 3V3 (或VCC) | 36 | 3.3V直流电源 |
| GND | 38 | 接地 |
| CS | 2 | GP1 (SPI0_CSn) |
| SDO | 1 | GP0 (SPI0_RX) |
| SDA | 5 | GP3 (SPI0_TX) |
| SCL | 4 | GP2 (SPI0_SCK) |

某些ADXL345电路板的接线图：

![ADXL345-Pico](img/adxl345-pico.png)

### I2C加速度计

建议的三对双绞线对的顺序（首选）：

```
3.3V+GND
SDA+GND
SCL+GND
```

或者两对：

```
3.3V+SDA
GND+SCL
```

请注意，与电缆屏蔽不同，任何GND应在两端连接。

#### MPU-9250/MPU-9255/MPU-6515/MPU-6050/MPU-6500/ICM20948

这些加速度计已被测试可在RPi、RP2040 (Pico)和AVR上以400kbit/s(*快速模式*)工作。某些MPU加速度计模块包括上拉电阻，但有些太大（10K），必须更改或由较小的并联电阻补充。

树莓派上I2C的推荐连接方案：

| MPU-9250引脚 | RPi引脚 | RPi引脚名称 |
|:--:|:--:|:--:|
| VCC | 01 | 3.3v直流电源 |
| GND | 09 | 接地 |
| SDA | 03 | GPIO02 (SDA1) |
| SCL | 05 | GPIO03 (SCL1) |

RPi在SCL和SDA上都有1.8K内置上拉电阻。

![MPU-9250连接到Pi](img/mpu9250-PI-fritzing.png)

RP2040上I2C (i2c0a)的推荐连接方案：

| MPU-9250引脚 | RP2040引脚 | RP2040引脚名称 |
|:--:|:--:|:--:|
| VCC | 36 | 3v3 |
| GND | 38 | 接地 |
| SDA | 01 | GP0 (I2C0 SDA) |
| SCL | 02 | GP1 (I2C0 SCL) |

Pico不包括任何内置的I2C上拉电阻。

![MPU-9250连接到Pico](img/mpu9250-PICO-fritzing.png)

##### AVR ATmega328P Arduino Nano上I2C(TWI)的推荐连接方案：

| MPU-9250引脚 | Atmega328P TQFP32引脚 | Atmega328P引脚名称 | Arduino Nano引脚 |
|:--:|:--:|:--:|:--:|
| VCC | 39 | - | - |
| GND | 38 | 接地 | GND |
| SDA | 27 | SDA | A4 |
| SCL | 28 | SCL | A5 |

Arduino Nano不包括任何内置的上拉电阻，也没有3.3V电源引脚。

### 安装加速度计

加速度计必须安装在工具头上。需要设计一个适合自己3D打印机的适当安装件。最好将加速度计的轴与打印机的轴对齐（但如果方便的话，轴可以交换 - 即不需要将X轴与X对齐等等 - 即使加速度计的Z轴是打印机的X轴也应该很好）。

在SmartEffector上安装ADXL345的示例：

![ADXL345在SmartEffector上](img/adxl345-mount.jpg)

请注意，在床式滑块打印机上，必须设计2个安装件：一个用于工具头，一个用于床，并且需要运行两次测量。有关详细信息，请参阅相应的[部分](#床式打印机)。

**警告：**确保加速度计和任何固定它的螺钉不接触打印机的任何金属部分。基本上，必须设计安装件以确保加速度计与打印机框架的电隔离。未能确保这一点可能会在系统中产生接地回路，可能损坏电子设备。

### 软件安装

请注意，共振测量和整形器自动校准需要默认情况下未安装的额外软件依赖项。首先，在树莓派上运行以下命令：
```
sudo apt update
sudo apt install libatlas-base-dev libopenblas-dev
```

接下来，为了在Kalico环境中安装NumPy，运行命令：
```
~/klippy-env/bin/pip install -v numpy matplotlib
```
请注意，根据CPU的性能，这可能需要*很长*的时间，最多10-20分钟。请耐心等待安装完成。在某些情况下，如果主板RAM太少，安装可能会失败，您将需要启用交换空间。

安装后，请检查以下命令没有显示错误：
```
~/klippy-env/bin/python -c 'import numpy;'
```
正确的输出应该只是一个新行。

#### 使用RPi配置ADXL345

首先，查看并按照[RPi微控制器文档](RPi_microcontroller.md)中的说明设置树莓派上的"linux mcu"。这将配置运行在您的Pi上的第二个Kalico实例。

确保通过运行`sudo raspi-config`并在"Interfacing options"菜单下启用SPI来启用Linux SPI驱动程序。

将以下内容添加到printer.cfg文件中：

```
[mcu rpi]
serial: /tmp/klipper_host_mcu

[adxl345]
cs_pin: rpi:None

[resonance_tester]
accel_chip: adxl345
probe_points:
    100, 100, 20  # 一个示例
```
建议从1个探测点开始，位于打印床中间，略高于床面。

#### 使用Pi Pico配置ADXL345

##### 刷写Pico固件

在树莓派上，为Pico编译固件。

```
cd ~/klipper
make clean
make menuconfig
```
![Pico menuconfig](img/klipper_pico_menuconfig.png)

现在，按住Pico上的`BOOTSEL`按钮，通过USB将Pico连接到树莓派。编译并刷写固件。
```
make flash FLASH_DEVICE=first
```

如果失败，您会被告知要使用的`FLASH_DEVICE`。在本例中，那是```make flash FLASH_DEVICE=2e8a:0003```。
![确定刷写设备](img/flash_rp2040_FLASH_DEVICE.png)

##### 配置连接

Pico现在将使用新固件重启，应显示为串行设备。使用`ls /dev/serial/by-id/*`找到pico串行设备。现在可以添加带有以下设置的`adxl.cfg`文件：

```
[mcu adxl]
# 将<mySerial>更改为上面找到的内容。例如，
# usb-Klipper_rp2040_E661640843545B2E-if00
serial: /dev/serial/by-id/usb-Klipper_rp2040_<mySerial>

[adxl345]
cs_pin: adxl:gpio1
spi_bus: spi0a
axes_map: x,z,y

[resonance_tester]
accel_chip: adxl345
probe_points:
    # 打印床中间略高处的某处
    147,154, 20

[output_pin power_mode] # 改进电源稳定性
pin: adxl:gpio23
```

如果在单独的文件中设置ADXL345配置（如上所示），您还需要修改`printer.cfg`文件以包含以下内容：

```
[include adxl.cfg] # 断开加速度计时注释掉此项
```

通过`RESTART`命令重启Kalico。

#### 配置LIS2DW系列

```
[mcu lis]
# 将<mySerial>更改为上面找到的内容。例如，
# usb-Klipper_rp2040_E661640843545B2E-if00
serial: /dev/serial/by-id/usb-Klipper_rp2040_<mySerial>

[lis2dw]
cs_pin: lis:gpio1
spi_bus: spi0a
axes_map: x,z,y

[resonance_tester]
accel_chip: lis2dw
probe_points:
    # 打印床中间略高处的某处
    147,154, 20
```

#### 使用RPi配置MPU-6000/9000系列

确保启用Linux I2C驱动程序并将波特率设置为400000（有关更多详细信息，请参阅[启用I2C](RPi_microcontroller.md#optional-enabling-i2c)部分）。然后，将以下内容添加到printer.cfg：

```
[mcu rpi]
serial: /tmp/klipper_host_mcu

[mpu9250]
i2c_mcu: rpi
i2c_bus: i2c.1

[resonance_tester]
accel_chip: mpu9250
probe_points: