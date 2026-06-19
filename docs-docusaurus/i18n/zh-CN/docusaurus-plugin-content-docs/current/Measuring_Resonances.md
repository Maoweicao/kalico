# 测量谐振

Kalico 内置支持 ADXL345、MPU-9250 和 LIS2DW 兼容的加速度计，可用于测量打印机不同轴的谐振频率，并自动调谐 [输入整形器](Resonance_Compensation.md) 以补偿谐振。请注意，使用加速度计需要进行一些焊接和压接。ADXL345/LIS2DW 可以连接到 Raspberry Pi 或 MCU 板的 SPI 接口（需要足够快）。MPU 系列可以直接连接到 Raspberry Pi 的 I2C 接口，或连接到支持 Kalico 中 400kbit/s *快速模式* 的 MCU 板的 I2C 接口。

采购加速度计时，请注意有多种不同的 PCB 板设计和不同的克隆版本。如果要连接到 5V 打印机 MCU，请确保其具有稳压器和电平转换器。

对于 ADXL345/LIS2DW，请确保板子支持 SPI 模式（少数板子似乎通过将 SDO 拉至 GND 硬配置为 I2C）。

对于 MPU-9250/MPU-9255/MPU-6515/MPU-6050/MPU-6500/ICM20948 和 LIS2DW/LIS3DH，也有多种板设计和具有不同 I2C 上拉电阻的克隆版本，需要补充。

## 支持 Kalico I2C *快速模式* 的 MCU

| MCU 系列 | 已测试的 MCU | 支持的 MCU |
|:--:|:--|:--|
| Raspberry Pi | 3B+, Pico | 3A, 3A+, 3B, 4 |
| AVR ATmega | ATmega328p | ATmega32u4, ATmega128, ATmega168, ATmega328, ATmega644p, ATmega1280, ATmega1284, ATmega2560 |
| AVR AT90 | - | AT90usb646, AT90usb1286 |

## 安装说明

### 接线

建议使用带有屏蔽双绞线的以太网电缆（cat5e 或更高），以确保长距离信号完整性。如果仍然遇到信号完整性问题（SPI/I2C 错误）：

- 使用数字万用表仔细检查接线：
  - 关机时的正确连接（连续性）
  - 正确的电源和接地电压
- 仅 I2C：
  - 检查 SCL 和 SDA 线到 3.3V 的电阻是否在 900 欧姆到 1.8K 范围内
  - 有关 *快速模式* 的完整技术细节，请参阅 [I2C 总线规范和用户手册 UM10204 第 7 章](https://www.pololu.com/file/0J435/UM10204.pdf)
- 缩短电缆

仅将以太网电缆屏蔽层连接到 MCU 板/Pi 接地。

***在上电前仔细检查接线，以防止损坏 MCU/Raspberry Pi 或加速度计。***

### SPI 加速度计

三对双绞线的建议顺序：

```
GND+MISO
3.3V+MOSI
SCLK+CS
```

请注意，与电缆屏蔽层不同，GND 必须在两端连接。

#### ADXL345

##### 直接连接到 Raspberry Pi

**注意：许多 MCU 可以在 SPI 模式下与 ADXL345 一起工作（例如 Pi Pico），接线和配置将根据您的特定板和可用引脚而有所不同。**

您需要通过 SPI 将 ADXL345 连接到 Raspberry Pi。请注意，ADXL345 文档中建议的 I2C 连接吞吐量太低，**无法工作**。推荐的连接方案：

| ADXL345 引脚 | RPi 引脚 | RPi 引脚名称 |
|:--:|:--:|:--:|
| 3V3 (或 VCC) | 01 | 3.3V DC 电源 |
| GND | 06 | 接地 |
| CS | 24 | GPIO08 (SPI0_CE0_N) |
| SDO | 21 | GPIO09 (SPI0_MISO) |
| SDA | 19 | GPIO10 (SPI0_MOSI) |
| SCL | 23 | GPIO11 (SPI0_SCLK) |

一些 ADXL345 板的 Fritzing 接线图：

![ADXL345-Rpi](/img/adxl345-fritzing.png)

##### 使用 Raspberry Pi Pico

您可以将 ADXL345 连接到 Raspberry Pi Pico，然后通过 USB 将 Pico 连接到 Raspberry Pi。这样可以轻松地在其他 Kalico 设备上重复使用加速度计，因为您可以通过 USB 而不是 GPIO 连接。Pico 的处理能力有限，因此请确保它只运行加速度计，不执行任何其他职责。

为避免损坏 RPi，请确保仅将 ADXL345 连接到 3.3V。根据板的布局，可能存在电平转换器，这使得 5V 对您的 RPi 危险。

| ADXL345 引脚 | Pico 引脚 | Pico 引脚名称 |
|:--:|:--:|:--:|
| 3V3 (或 VCC) | 36 | 3.3V DC 电源 |
| GND | 38 | 接地 |
| CS | 2 | GP1 (SPI0_CSn) |
| SDO | 1 | GP0 (SPI0_RX) |
| SDA | 5 | GP3 (SPI0_TX) |
| SCL | 4 | GP2 (SPI0_SCK) |

一些 ADXL345 板的接线图：

![ADXL345-Pico](/img/adxl345-pico.png)

### I2C 加速度计

三对双绞线的建议顺序（首选）：

```
3.3V+GND
SDA+GND
SCL+GND
```

或两对：

```
3.3V+SDA
GND+SCL
```

请注意，与电缆屏蔽层不同，任何 GND 都应在两端连接。

#### MPU-9250/MPU-9255/MPU-6515/MPU-6050/MPU-6500/ICM20948

这些加速度计已测试可在 RPi、RP2040 (Pico) 和 AVR 上以 400kbit/s (*快速模式*) 通过 I2C 工作。一些 MPU 加速度计模块包含上拉电阻，但有些太大（10K），必须更换或用较小的并联电阻补充。

在 Raspberry Pi 上 I2C 的推荐连接方案：

| MPU-9250 引脚 | RPi 引脚 | RPi 引脚名称 |
|:--:|:--:|:--:|
| VCC | 01 | 3.3v DC 电源 |
| GND | 09 | 接地 |
| SDA | 03 | GPIO02 (SDA1) |
| SCL | 05 | GPIO03 (SCL1) |

RPi 在 SCL 和 SDA 上内置 1.8K 上拉电阻。

![MPU-9250 连接到 Pi](/img/mpu9250-PI-fritzing.png)

RP2040 上 I2C (i2c0a) 的推荐连接方案：

| MPU-9250 引脚 | RP2040 引脚 | RP2040 引脚名称 |
|:--:|:--:|:--:|
| VCC | 36 | 3v3 |
| GND | 38 | 接地 |
| SDA | 01 | GP0 (I2C0 SDA) |
| SCL | 02 | GP1 (I2C0 SCL) |

Pico 不包含任何内置 I2C 上拉电阻。

![MPU-9250 连接到 Pico](/img/mpu9250-PICO-fritzing.png)

##### AVR ATmega328P Arduino Nano 上 I2C(TWI) 的推荐连接方案：

| MPU-9250 引脚 | Atmega328P TQFP32 引脚 | Atmega328P 引脚名称 | Arduino Nano 引脚 |
|:--:|:--:|:--:|:--:|
| VCC | 39 | - | - |
| GND | 38 | 接地 | GND |
| SDA | 27 | SDA | A4 |
| SCL | 28 | SCL | A5 |

Arduino Nano 不包含任何内置上拉电阻，也没有 3.3V 电源引脚。

### 安装加速度计

加速度计必须安装在工具头上。需要设计一个合适的安装座以适应自己的 3D 打印机。最好将加速度计的轴与打印机的轴对齐（但如果更方便，可以交换轴 - 即无需将 X 轴与 X 对齐等 - 即使加速度计的 Z 轴是打印机的 X 轴等，应该也没问题）。

在 SmartEffector 上安装 ADXL345 的示例：

![ADXL345 在 SmartEffector 上](/img/adxl345-mount.jpg)

请注意，在床移动打印机上，您需要设计两个安装座：一个用于工具头，一个用于热床，并运行两次测量。有关更多详细信息，请参阅相应的 [部分](#bed-slinger-printers)。

**注意：** 确保加速度计和任何将其固定到位的螺丝不接触打印机的任何金属部件。基本上，必须设计安装座以确保加速度计与打印机框架的电气隔离。如果未能确保这一点，可能会在系统中产生接地环路，从而可能损坏电子设备。

### 软件安装

请注意，谐振测量和整形器自动校准需要额外的软件依赖项，默认情况下未安装。首先，在您的 Raspberry Pi 上运行以下命令：
```
sudo apt update
sudo apt install libatlas-base-dev libopenblas-dev
```

接下来，为了在 Kalico 环境中安装 NumPy，请运行命令：
```
~/klippy-env/bin/pip install -v numpy matplotlib
```
请注意，根据 CPU 的性能，这可能需要*很长时间*，最多 10-20 分钟。请耐心等待安装完成。在某些情况下，如果板子 RAM 太少，安装可能会失败，您需要启用交换空间。

安装完成后，请检查以下命令没有错误：
```
~/klippy-env/bin/python -c 'import numpy;'
```
正确的输出应该只是一个新行。

#### 使用 RPi 配置 ADXL345

首先，检查并按照 [RPi 微控制器文档](RPi_microcontroller.md) 中的说明在 Raspberry Pi 上设置 "linux mcu"。这将配置在 Pi 上运行的第二个 Kalico 实例。

通过运行 `sudo raspi-config` 并在 "Interfacing options" 菜单下启用 SPI 来确保启用 Linux SPI 驱动程序。

将以下内容添加到 printer.cfg 文件：

```
[mcu rpi]
serial: /tmp/klipper_host_mcu

[adxl345]
cs_pin: rpi:None

[resonance_tester]
accel_chip: adxl345
probe_points:
    100, 100, 20  # an example
```
建议从一个探测点开始，位于打印床中间，略高于其上方。

#### 使用 Pi Pico 配置 ADXL345

##### 刷写 Pico 固件

在 Raspberry Pi 上，为 Pico 编译固件。

```
cd ~/klipper
make clean
make menuconfig
```
![Pico menuconfig](/img/klipper_pico_menuconfig.png)

现在，按住 Pico 上的 `BOOTSEL` 按钮，通过 USB 将 Pico 连接到 Raspberry Pi。编译并刷写固件。
```
make flash FLASH_DEVICE=first
```

如果失败，系统会告诉您使用哪个 `FLASH_DEVICE`。在此示例中，为 ```make flash FLASH_DEVICE=2e8a:0003```。
![确定闪存设备](/img/flash_rp2040_FLASH_DEVICE.png)

##### 配置连接

Pico 现在将使用新固件重新启动，并应显示为串行设备。使用 `ls /dev/serial/by-id/*` 查找 pico 串行设备。现在您可以添加一个包含以下设置的 `adxl.cfg` 文件：

```
[mcu adxl]
# Change <mySerial> to whatever you found above. For example,
# usb-Klipper_rp2040_E661640843545B2E-if00
serial: /dev/serial/by-id/usb-Klipper_rp2040_<mySerial>

[adxl345]
cs_pin: adxl:gpio1
spi_bus: spi0a
axes_map: x,z,y

[resonance_tester]
accel_chip: adxl345
probe_points:
    # Somewhere slightly above the middle of your print bed
    147,154, 20

[output_pin power_mode] # Improve power stability
pin: adxl:gpio23
```

如果如上所述在单独的文件中设置 ADXL345 配置，您还需要修改 `printer.cfg` 文件以包含以下内容：

```
[include adxl.cfg] # Comment this out when you disconnect the accelerometer
```

通过 `RESTART` 命令重启 Kalico。

#### 配置 LIS2DW 系列

```
[mcu lis]
# Change <mySerial> to whatever you found above. For example,
# usb-Klipper_rp2040_E661640843545B2E-if00
serial: /dev/serial/by-id/usb-Klipper_rp2040_<mySerial>

[lis2dw]
cs_pin: lis:gpio1
spi_bus: spi0a
axes_map: x,z,y

[resonance_tester]
accel_chip: lis2dw
probe_points:
    # Somewhere slightly above the middle of your print bed
    147,154, 20
```

#### 使用 RPi 配置 MPU-6000/9000 系列

确保启用 Linux I2C 驱动程序，并将波特率设置为 400000（有关更多详细信息，请参阅 [启用 I2C](RPi_microcontroller.md#optional-enabling-i2c) 部分）。然后，将以下内容添加到 printer.cfg：

```
[mcu rpi]
serial: /tmp/klipper_host_mcu

[mpu9250]
i2c_mcu: rpi
i2c_bus: i2c.1

[resonance_tester]
accel_chip: mpu9250
probe_points:
    100, 100, 20  # an example
```
如果您使用的是 ICM20948，请将 "mpu9250" 替换为 "icm20948"。

#### 使用 Pico 配置 MPU-9520 兼容设备

Pico I2C 默认设置为 400000。只需将以下内容添加到 printer.cfg：

```
[mcu pico]
serial: /dev/serial/by-id/<your Pico's serial ID>

[mpu9250]
i2c_mcu: pico
i2c_bus: i2c0a

[resonance_tester]
accel_chip: mpu9250
probe_points:
    100, 100, 20  # an example

[static_digital_output pico_3V3pwm] # Improve power stability
pins: pico:gpio23
```
如果您使用的是 ICM20948，请将 "mpu9250" 替换为 "icm20948"。

#### 使用 AVR 配置 MPU-9520 兼容设备

AVR I2C 将由 mpu9250 选项设置为 400000。只需将以下内容添加到 printer.cfg：

```
[mcu nano]
serial: /dev/serial/by-id/<your nano's serial ID>

[mpu9250]
i2c_mcu: nano

[resonance_tester]
accel_chip: mpu9250
probe_points:
    100, 100, 20  # an example
```
如果您使用的是 ICM20948，请将 "mpu9250" 替换为 "icm20948"。

通过 `RESTART` 命令重启 Kalico。

## 测量谐振

### 检查设置

现在您可以测试连接。

- 对于 "非床移动打印机"（例如一个加速度计），在 Octoprint 中，输入 `ACCELEROMETER_QUERY`
- 对于 "床移动打印机"（例如多个加速度计），输入 `ACCELEROMETER_QUERY CHIP=<chip>`，其中 `<chip>` 是输入的芯片名称，例如 `CHIP=bed`（请参阅：[床移动打印机](#bed-slinger-printers)）以获取所有已安装的加速度计芯片。

您应该看到来自加速度计的当前测量值，包括自由落体加速度，例如
```
Recv: // adxl345 values (x, y, z): 470.719200, 941.438400, 9728.196800
```

如果您收到类似 `Invalid adxl345 id (got xx vs e5)` 的错误，其中 `xx` 是其他 ID，请立即重试。存在 SPI 初始化问题。如果仍然出错，则表明与 ADXL345 的连接问题，或传感器故障。仔细检查电源、接线（确保与原理图匹配，没有导线断裂或松动等），以及焊接质量。

**如果您使用 MPU-9250 兼容加速度计，且显示为 `mpu-unknown`，请谨慎使用！它们可能是翻新芯片！**

接下来，尝试在 Octoprint 中运行 `MEASURE_AXES_NOISE`，您应该会获得加速度计在各轴上噪声的基线值（应在 ~1-100 范围内）。过高的轴噪声（例如 1000 及以上）可能表明传感器问题、电源问题或 3D 打印机上噪声过大的不平衡风扇。

### 测量谐振

现在您可以运行一些实际测试。运行以下命令：
```
TEST_RESONANCES AXIS=X
```
请注意，这将使 X 轴产生振动。如果之前启用了输入整形，它还将禁用输入整形，因为在启用输入整形器的情况下运行谐振测试是无效的。

**注意！** 第一次运行时请务必观察打印机，确保振动不会变得过于剧烈（在紧急情况下可以使用 `M112` 命令中止测试；希望不会发生这种情况）。如果振动确实变得过于强烈，您可以尝试在 `[resonance_tester]` 部分指定低于默认值的 `accel_per_hz` 参数，例如
```
[resonance_tester]
accel_chip: adxl345
accel_per_hz: 50  # default is 75
probe_points: ...
```

如果对 X 轴有效，请也为 Y 轴运行：
```
TEST_RESONANCES AXIS=Y
```
这将生成 2 个 CSV 文件 (`/tmp/resonances_x_*.csv` 和 `/tmp/resonances_y_*.csv`)。这些文件可以使用 Raspberry Pi 上的独立脚本进行处理。该脚本旨在为每个测量的轴使用单个 CSV 文件，但如果您希望对结果取平均值，也可以使用多个 CSV 文件。对结果取平均值可能很有用，例如，如果在多个测试点进行了谐振测试。如果您不希望对它们取平均值，请删除多余的 CSV 文件。
```
~/klippy-env/bin/python ~/klipper/scripts/calibrate_shaper.py /tmp/resonances_x_*.csv -o /tmp/shaper_calibrate_x.png
~/klippy-env/bin/python ~/klipper/scripts/calibrate_shaper.py /tmp/resonances_y_*.csv -o /tmp/shaper_calibrate_y.png
```
此脚本将生成包含频率响应的图表 `/tmp/shaper_calibrate_x.png` 和 `/tmp/shaper_calibrate_y.png`。您还将获得每个输入整形器的建议频率，以及为您的设置推荐的输入整形器。例如：

![谐振](/img/calibrate-y.png)
```
Fitted shaper 'zv' frequency = 34.4 Hz (vibrations = 4.0%, smoothing ~= 0.132)
To avoid too much smoothing with 'zv', suggested max_accel <= 4500 mm/sec^2
Fitted shaper 'mzv' frequency = 34.6 Hz (vibrations = 0.0%, smoothing ~= 0.170)
To avoid too much smoothing with 'mzv', suggested max_accel <= 3500 mm/sec^2
Fitted shaper 'ei' frequency = 41.4 Hz (vibrations = 0.0%, smoothing ~= 0.188)
To avoid too much smoothing with 'ei', suggested max_accel <= 3200 mm/sec^2
Fitted shaper '2hump_ei' frequency = 51.8 Hz (vibrations = 0.0%, smoothing ~= 0.201)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 3000 mm/sec^2
Fitted shaper '3hump_ei' frequency = 61.8 Hz (vibrations = 0.0%, smoothing ~= 0.215)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 2800 mm/sec^2
Recommended shaper is mzv @ 34.6 Hz
```

建议的配置可以添加到 `printer.cfg` 的 `[input_shaper]` 部分，例如：
```
[input_shaper]
shaper_freq_x: ...
shaper_type_x: ...
shaper_freq_y: 34.6
shaper_type_y: mzv

[printer]
max_accel: 3000  # should not exceed the estimated max_accel for X and Y axes
```
或者您可以根据生成的图表自己选择一些其他配置：图表上功率谱密度的峰值对应于打印机的谐振频率。

请注意，您也可以直接从 Kalico [运行](#input-shaper-auto-calibration) 输入整形器自动校准，这很方便，例如，用于输入整形器 [重新校准](#input-shaper-re-calibration)。

### 床移动打印机

如果您的打印机是床移动打印机，则需要在 X 轴和 Y 轴测量之间更改加速度计的位置：在工具头上安装加速度计测量 X 轴谐振，在热床上安装加速度计测量 Y 轴谐振（通常的床移动打印机设置）。

但是，您也可以同时连接两个加速度计，但 ADXL345 必须连接到不同的板（例如，连接到 RPi 和打印机 MCU 板），或连接到同一板上的两个不同物理 SPI 接口（很少可用）。然后可以按以下方式配置它们：

```
[adxl345 hotend]
# Assuming `hotend` chip is connected to an RPi
cs_pin: rpi:None

[adxl345 bed]
# Assuming `bed` chip is connected to a printer MCU board
cs_pin: ...  # Printer board SPI chip select (CS) pin

[resonance_tester]
# Assuming the typical setup of the bed slinger printer
accel_chip_x: adxl345 hotend
accel_chip_y: adxl345 bed
probe_points: ...
```

两个 MPU 可以共享一条 I2C 总线，但它们**不能**同时测量，因为 400kbit/s I2C 总线速度不够快。一个必须将其 AD0 引脚拉低至 0V（地址 104），另一个必须将其 AD0 引脚拉高至 3.3V（地址 105）：

```
[mpu9250 hotend]
i2c_mcu: rpi
i2c_bus: i2c.1
i2c_address: 104 # This MPU has pin AD0 pulled low

[mpu9250 bed]
i2c_mcu: rpi
i2c_bus: i2c.1
i2c_address: 105 # This MPU has pin AD0 pulled high

[resonance_tester]
# Assuming the typical setup of the bed slinger printer
accel_chip_x: mpu9250 hotend
accel_chip_y: mpu9250 bed
probe_points: ...
```
[在将两个 MPU 连接到总线之前，请单独测试每个 MPU 以便于调试。]

然后命令 `TEST_RESONANCES AXIS=X` 和 `TEST_RESONANCES AXIS=Y` 将为每个轴使用正确的加速度计。

### 最大平滑度

请记住，输入整形器可能会在零件中产生一些平滑度。由 `calibrate_shaper.py` 脚本或 `SHAPER_CALIBRATE` 命令执行的输入整形器自动调谐试图不加剧平滑度，但同时试图最小化产生的振动。有时它们可能会做出次优的整形器频率选择，或者您可能只是希望在零件中减少平滑度，以牺牲较大的残余振动为代价。在这些情况下，您可以要求限制输入整形器的最大平滑度。

让我们考虑以下自动调谐的结果：

![谐振](/img/calibrate-x.png)
```
Fitted shaper 'zv' frequency = 57.8 Hz (vibrations = 20.3%, smoothing ~= 0.053)
To avoid too much smoothing with 'zv', suggested max_accel <= 13000 mm/sec^2
Fitted shaper 'mzv' frequency = 34.8 Hz (vibrations = 3.6%, smoothing ~= 0.168)
To avoid too much smoothing with 'mzv', suggested max_accel <= 3600 mm/sec^2
Fitted shaper 'ei' frequency = 48.8 Hz (vibrations = 4.9%, smoothing ~= 0.135)
To avoid too much smoothing with 'ei', suggested max_accel <= 4400 mm/sec^2
Fitted shaper '2hump_ei' frequency = 45.2 Hz (vibrations = 0.1%, smoothing ~= 0.264)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 2200 mm/sec^2
Fitted shaper '3hump_ei' frequency = 48.0 Hz (vibrations = 0.0%, smoothing ~= 0.356)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 1500 mm/sec^2
Recommended shaper is 2hump_ei @ 45.2 Hz
```
请注意，报告的 `smoothing` 值是一些抽象的投影值。这些值可用于比较不同的配置：值越高，整形器产生的平滑度越多。然而，这些平滑度分数并不代表任何实际的平滑度度量，因为实际平滑度取决于 [`max_accel`](#selecting-max_accel) 和 `square_corner_velocity` 参数。因此，您应该打印一些测试打印件，看看所选配置究竟产生多少平滑度。

在上面的示例中，建议的整形器参数并不差，但如果您希望在 X 轴上获得更少的平滑度怎么办？您可以尝试使用以下命令限制最大整形器平滑度：
```
~/klippy-env/bin/python ~/klipper/scripts/calibrate_shaper.py /tmp/resonances_x_*.csv -o /tmp/shaper_calibrate_x.png --max_smoothing=0.2
```
这将平滑度限制为 0.2 分。现在您可以得到以下结果：

![谐振](/img/calibrate-x-max-smoothing.png)
```
Fitted shaper 'zv' frequency = 55.4 Hz (vibrations = 19.7%, smoothing ~= 0.057)
To avoid too much smoothing with 'zv', suggested max_accel <= 12000 mm/sec^2
Fitted shaper 'mzv' frequency = 34.6 Hz (vibrations = 3.6%, smoothing ~= 0.170)
To avoid too much smoothing with 'mzv', suggested max_accel <= 3500 mm/sec^2
Fitted shaper 'ei' frequency = 48.2 Hz (vibrations = 4.8%, smoothing ~= 0.139)
To avoid too much smoothing with 'ei', suggested max_accel <= 4300 mm/sec^2
Fitted shaper '2hump_ei' frequency = 52.0 Hz (vibrations = 2.7%, smoothing ~= 0.200)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 3000 mm/sec^2
Fitted shaper '3hump_ei' frequency = 72.6 Hz (vibrations = 1.4%, smoothing ~= 0.155)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 3900 mm/sec^2
Recommended shaper is 3hump_ei @ 72.6 Hz
```

与之前建议的参数相比，振动稍大，但平滑度显著小于之前，允许更大的最大加速度。

在决定选择哪个 `max_smoothing` 参数时，您可以采用试错法。尝试几个不同的值，看看得到哪些结果。请注意，输入整形器产生的实际平滑度主要取决于打印机的最低谐振频率：最低谐振频率越高，平滑度越小。因此，如果您要求脚本找到具有不切实际的小平滑度的输入整形器配置，它将以前者为代价增加最低谐振频率处的振铃（通常在打印件中也更明显可见）。因此，请始终仔细检查脚本报告的投影残余振动，并确保它们不会太高。

请注意，如果您为两个轴选择了良好的 `max_smoothing` 值，您可以将其存储在 `printer.cfg` 中，如下所示
```
[resonance_tester]
accel_chip: ...
probe_points: ...
max_smoothing: 0.25  # an example
```
那么，如果将来使用 `SHAPER_CALIBRATE` Kalico 命令 [重新运行](#input-shaper-re-calibration) 输入整形器自动调谐，它将使用存储的 `max_smoothing` 值作为参考。

### 选择 max_accel

由于输入整形器可能会在零件中产生一些平滑度，特别是在高加速度下，您仍然需要选择 `max_accel` 值，该值不会在打印件中产生太多平滑度。校准脚本提供了一个 `max_accel` 参数估计值，该值不应产生太多平滑度。请注意，校准脚本显示的 `max_accel` 只是一个理论最大值，相应的整形器仍能在不产生过多平滑度的情况下工作。这绝不是建议设置此加速度进行打印。您的打印机能够承受的最大加速度取决于其机械性能和所用步进电机的最大扭矩。因此，建议在 `[printer]` 部分设置 `max_accel`，该值不超过 X 轴和 Y 轴的估计值，可能带有一些保守的安全余量。

或者，请遵循 [此](Resonance_Compensation.md#selecting-max_accel) 部分的输入整形器调谐指南，并打印测试模型以实验性地选择 `max_accel` 参数。

同样的注意事项适用于使用 `SHAPER_CALIBRATE` 命令的输入整形器 [自动校准](#input-shaper-auto-calibration)：在自动校准后仍然需要选择正确的 `max_accel` 值，建议的加速度限制不会自动应用。

请记住，没有太多平滑度的最大加速度取决于 `square_corner_velocity`。一般建议不要将其从默认值 5.0 更改，这是 `calibrate_shaper.py` 脚本默认使用的值。但是，如果您确实更改了它，则应通过传递 `--square_corner_velocity=...` 参数通知脚本，例如
```
~/klippy-env/bin/python ~/klipper/scripts/calibrate_shaper.py /tmp/resonances_x_*.csv -o /tmp/shaper_calibrate_x.png --square_corner_velocity=10.0
```
以便它可以正确计算最大加速度建议。请注意，`SHAPER_CALIBRATE` 命令已经考虑了配置的 `square_corner_velocity` 参数，因此无需显式指定。

如果您正在进行整形器重新校准，并且所建议的整形器配置的报告平滑度与您在上一次校准中得到的结果几乎相同，则可以跳过此步骤。

### 测试自定义轴

`TEST_RESONANCES` 命令支持自定义轴。虽然这对于输入整形器校准不太有用，但可用于深入研究打印机谐振并检查例如皮带张力。

要检查 CoreXY 打印机上的皮带张力，请执行
```
TEST_RESONANCES AXIS=1,1 OUTPUT=raw_data
TEST_RESONANCES AXIS=1,-1 OUTPUT=raw_data
```
并使用 `graph_accelerometer.py` 处理生成的文件，例如
```
~/klippy-env/bin/python ~/klipper/scripts/graph_accelerometer.py -c /tmp/raw_data_axis*.csv -o /tmp/resonances.png
```
这将生成 `/tmp/resonances.png` 以比较谐振。

对于具有默认塔放置（塔 A ~= 210 度，B ~= 330 度，C ~= 90 度）的 Delta 打印机，请执行
```
TEST_RESONANCES AXIS=0,1 OUTPUT=raw_data
TEST_RESONANCES AXIS=-0.866025404,-0.5 OUTPUT=raw_data
TEST_RESONANCES AXIS=0.866025404,-0.5 OUTPUT=raw_data
```
然后使用相同的命令
```
~/klippy-env/bin/python ~/klipper/scripts/graph_accelerometer.py -c /tmp/raw_data_axis*.csv -o /tmp/resonances.png
```
生成 `/tmp/resonances.png` 以比较谐振。

## 输入整形器自动校准

除了手动选择输入整形器功能的适当参数外，还可以直接从 Kalico 运行输入整形器的自动调谐。通过 Octoprint 终端运行以下命令：
```
SHAPER_CALIBRATE
```

这将对两个轴运行完整测试，并生成用于频率响应和建议输入整形器的 CSV 输出（默认为 `/tmp/calibration_data_*.csv`）。您还将在 Octoprint 控制台上获得每个输入整形器的建议频率，以及为您的设置推荐的输入整形器。例如：

```
Calculating the best input shaper parameters for y axis
Fitted shaper 'zv' frequency = 39.0 Hz (vibrations = 13.2%, smoothing ~= 0.105)
To avoid too much smoothing with 'zv', suggested max_accel <= 5900 mm/sec^2
Fitted shaper 'mzv' frequency = 36.8 Hz (vibrations = 1.7%, smoothing ~= 0.150)
To avoid too much smoothing with 'mzv', suggested max_accel <= 4000 mm/sec^2
Fitted shaper 'ei' frequency = 36.6 Hz (vibrations = 2.2%, smoothing ~= 0.240)
To avoid too much smoothing with 'ei', suggested max_accel <= 2500 mm/sec^2
Fitted shaper '2hump_ei' frequency = 48.0 Hz (vibrations = 0.0%, smoothing ~= 0.234)
To avoid too much smoothing with '2hump_ei', suggested max_accel <= 2500 mm/sec^2
Fitted shaper '3hump_ei' frequency = 59.0 Hz (vibrations = 0.0%, smoothing ~= 0.235)
To avoid too much smoothing with '3hump_ei', suggested max_accel <= 2500 mm/sec^2
Recommended shaper_type_y = mzv, shaper_freq_y = 36.8 Hz
```
如果您同意建议的参数，可以现在执行 `SAVE_CONFIG` 来保存它们并重启 Kalico。请注意，这不会更新 `[printer]` 部分的 `max_accel` 值。您应该根据 [选择 max_accel](#selecting-max_accel) 部分中的考虑手动更新它。

如果您的打印机是床移动打印机，您可以指定要测试的轴，以便可以在测试之间更改加速度计安装点（默认情况下，对两个轴都执行测试）：
```
SHAPER_CALIBRATE AXIS=Y
```

您可以在校准每个轴后执行两次 `SAVE_CONFIG`。

但是，如果您同时连接了两个加速度计，只需运行 `SHAPER_CALIBRATE` 而不指定轴，即可一次为两个轴校准输入整形器。

### 输入整形器重新校准

`SHAPER_CALIBRATE` 命令也可用于将来重新校准输入整形器，特别是在对打印机进行可能影响其运动学的更改时。可以使用 `SHAPER_CALIBRATE` 命令重新运行完整校准，也可以通过提供 `AXIS=` 参数将自动校准限制为单个轴，例如
```
SHAPER_CALIBRATE AXIS=X
```

**警告！** 不建议非常频繁地运行整形器自动校准（例如在每次打印之前或每天）。为了确定谐振频率，自动校准会在每个轴上产生强烈的振动。通常，3D 打印机设计为不能承受长时间暴露在谐振频率附近的振动中。这样做可能会增加打印机部件的磨损并缩短其使用寿命。还有一些部件松动或变松的风险。每次自动调谐后，请务必检查打印机的所有部件（包括通常可能不会移动的部件）是否已牢固固定到位。

此外，由于测量中的一些噪声，调谐结果可能与一次校准到另一次校准略有不同。尽管如此，预计噪声不会对打印质量产生太大影响。但是，仍然建议仔细检查建议的参数，并在使用前打印一些测试打印件以确认它们是良好的。

## 加速度计数据的离线处理

可以生成原始加速度计数据并进行离线处理（例如在主机上），例如查找谐振。为此，请通过 Octoprint 终端运行以下命令：
```
SET_INPUT_SHAPER SHAPER_FREQ_X=0 SHAPER_FREQ_Y=0
TEST_RESONANCES AXIS=X OUTPUT=raw_data
```
忽略 `SET_INPUT_SHAPER` 命令的任何错误。对于 `TEST_RESONANCES` 命令，指定所需的测试轴。原始数据将写入 RPi 上的 `/tmp` 目录。

原始数据也可以通过在正常打印机活动期间运行两次 `ACCELEROMETER_MEASURE` 命令来获得 - 第一次开始测量，然后停止测量并写入输出文件。有关更多详细信息，请参阅 [G-Codes](G-Codes.md#adxl345)。

数据可以稍后由以下脚本处理：`scripts/graph_accelerometer.py` 和 `scripts/calibrate_shaper.py`。根据模式，两者都接受一个或几个原始 CSV 文件作为输入。graph_accelerometer.py 脚本支持多种操作模式：

* 绘制原始加速度计数据（使用 `-r` 参数），仅支持 1 个输入；
* 绘制频率响应（不需要额外参数），如果指定多个输入，则计算平均频率响应；
* 比较多个输入之间的频率响应（使用 `-c` 参数）；您可以通过 `-a x`、`-a y` 或 `-a z` 参数额外指定要考虑哪个加速度计轴（如果未指定，则使用所有轴的振动之和）；
* 绘制频谱图（使用 `-s` 参数），仅支持 1 个输入；您可以通过 `-a x`、`-a y` 或 `-a z` 参数额外指定要考虑哪个加速度计轴（如果未指定，则使用所有轴的振动之和）。

请注意，graph_accelerometer.py 脚本仅支持 raw_data\*.csv 文件，不支持 resonances\*.csv 或 calibration_data\*.csv 文件。

例如，
```
~/klippy-env/bin/python ~/klipper/scripts/graph_accelerometer.py /tmp/raw_data_x_*.csv -o /tmp/resonances_x.png -c -a z
```
将绘制多个 `/tmp/raw_data_x_*.csv` 文件的 Z 轴比较到 `/tmp/resonances_x.png` 文件。

shaper_calibrate.py 脚本接受 1 个或多个输入，可以运行输入整形器的自动调谐，并建议适用于所有提供的输入的最佳参数。它将建议的参数打印到控制台，如果提供 `-o output.png` 参数，还可以生成图表，或如果指定 `-c output.csv` 参数，则生成 CSV 文件。

向 shaper_calibrate.py 脚本提供多个输入可能很有用，例如在运行输入整形器的一些高级调谐时：

* 在床移动打印机上对单个轴运行 `TEST_RESONANCES AXIS=X OUTPUT=raw_data`（和 `Y` 轴）两次，第一次将加速度计安装在工具头上，第二次将加速度计安装在热床上，以检测轴交叉谐振并尝试使用输入整形器消除它们。
* 在具有玻璃热床和磁性表面（较轻）的床移动打印机上运行 `TEST_RESONANCES AXIS=Y OUTPUT=raw_data` 两次，以找到适用于任何打印表面配置的输入整形器参数。
* 组合来自多个测试点的谐振数据。
* 组合来自 2 个轴的谐振数据（例如在床移动打印机上，从 X 和 Y 轴谐振配置 X 轴输入整形器，以在喷嘴在 X 轴方向移动时'抓住'打印件时消除*热床*的振动）。