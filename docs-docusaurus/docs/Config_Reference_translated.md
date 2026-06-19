 
```
[stepper_z1]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   有关上述参数的定义，请参阅"stepper"部分。
#endstop_pin:
#   如果为额外的步进电机定义了 endstop_pin，则步进电机将
#   归位直至触发限位开关。否则，步进电机将归位直至
#   该轴主步进电机的限位开关被触发。
```

### [extruder1]

在多挤出机打印机中，为每个额外的挤出机添加一个挤出机部分。额外的挤出机部分应命名为"extruder1"、"extruder2"、"extruder3"等。有关可用参数的描述，请参阅"extruder"部分。

有关示例配置，请参阅 [sample-multi-extruder.cfg](../config/sample-multi-extruder.cfg)。

```
[extruder1]
#step_pin:
#dir_pin:
#...
#   有关可用的步进电机和加热器参数，请参阅"extruder"部分。
#shared_heater:
#   此选项已弃用，不应再指定。
```

### [dual_carriage]

支持单轴双滑车的笛卡尔和混合 corexy/z 打印机。滑车模式可通过 SET_DUAL_CARRIAGE 扩展 G 代码命令设置。例如，"SET_DUAL_CARRIAGE CARRIAGE=1"命令将激活在此部分定义的滑车（CARRIAGE=0 将激活返回到主滑车）。双滑车支持通常与额外的挤出机结合使用——SET_DUAL_CARRIAGE 命令通常与 ACTIVATE_EXTRUDER 命令同时调用。停用时请确保停放滑车。注意，在 G28 归位期间，通常先归位主滑车，然后归位在 `[dual_carriage]` 配置部分定义的滑车。但是，如果两个滑车都向正方向归位且 `[dual_carriage]` 滑车的 `position_endstop` 大于主滑车，或者两个滑车都向负方向归位且 `[dual_carriage]` 滑车的 `position_endstop` 小于主滑车，则先归位 `[dual_carriage]` 滑车。

此外，可以使用"SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY"或"SET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR"命令来激活双滑车的复制或镜像模式，此时它将相应地跟随滑车 0 的运动。这些命令可用于同时打印两个零件——两个相同的零件（在 COPY 模式下）或镜像零件（在 MIRROR 模式下）。注意，COPY 和 MIRROR 模式还需要适当配置双滑车上的挤出机，这通常可以通过"SYNC_EXTRUDER_MOTION MOTION_QUEUE=extruder EXTRUDER=\<dual_carriage_extruder\>"或类似命令实现。

有关示例配置，请参阅 [sample-idex.cfg](../config/sample-idex.cfg)。

```
[dual_carriage]
axis:
#   此额外滑车所在的轴（x 或 y）。必须提供此参数。
#safe_distance:
#   在双滑车和主滑车之间强制保持的最小距离（以毫米为单位）。如果执行的 G 代码命令使滑车
#   之间的距离小于指定限制，该命令将被拒绝并报错。如果未提供 safe_distance，它将从
#   双滑车和主滑车的 position_min 和 position_max 推断得出。如果设置为
#   0（或者 safe_distance 未设置且主滑车和双滑车的 position_min 和 position_max 相同），
#   则滑车接近性检查将被禁用。
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#endstop_pin:
#position_endstop:
#position_min:
#position_max:
#   有关上述参数的定义，请参阅"stepper"部分。
```

### [extruder_stepper]

支持与挤出机运动同步的额外步进电机（可以定义任意数量的带有"extruder_stepper"前缀的部分）。

更多信息请参阅 [命令参考](G-Codes.md#extruder)。

```
[extruder_stepper my_extra_stepper]
extruder:
#   此步进电机同步到的挤出机。如果设置为空字符串，则步进电机将不会
#   同步到任何挤出机。必须提供此参数。
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   有关上述参数的定义，请参阅"stepper"部分。
```

### [manual_stepper]

手动步进电机（可以定义任意数量的带有"manual_stepper"前缀的部分）。这些步进电机由 MANUAL_STEPPER G 代码命令控制。例如："MANUAL_STEPPER STEPPER=my_stepper MOVE=10 SPEED=5"。有关 MANUAL_STEPPER 命令的描述，请参阅 [G-Codes](G-Codes.md#manual_stepper) 文件。这些步进电机不连接到正常的打印机运动学。

```
[manual_stepper my_stepper]
#step_pin:
#dir_pin:
#enable_pin:
#microsteps:
#rotation_distance:
#   有关这些参数的描述，请参阅"stepper"部分。
#velocity:
#   设置步进电机的默认速度（以毫米/秒为单位）。如果 MANUAL_STEPPER
#   命令未指定 SPEED 参数，将使用此值。默认值为 5mm/s。
#accel:
#   设置步进电机的默认加速度（以毫米/秒^2 为单位）。加速度为零表示没有加速度。
#   如果 MANUAL_STEPPER 命令未指定 ACCEL 参数，将使用此值。默认值为零。
#endstop_pin:
#   限位开关检测引脚。如果指定，则可以通过向 MANUAL_STEPPER 运动命令添加
#   STOP_ON_ENDSTOP 参数来执行"归位移动"。
```

### [mixing_extruder]

具有 n 进 1 出混合喷嘴的混合打印头。激活后，可以使用额外的 G 代码命令。
有关额外命令的详细描述，请参阅 [G-Codes](G-Codes.md#mixing_extruder)。

```
[mixing_extruder]
#steppers:
#   哪些步进电机向热端/喷嘴进料。提供逗号分隔的列表，例如
#   "extruder,extruder1,extruder2"。应该是挤出机部分或 extruder_stepper 部分的名称
#   此配置是必需的。
#extruder_name:
#   要将 steppers 列表中的步进电机同步到的挤出机名称。
#   默认是"steppers"列表中的第一个条目。
```


## 自定义加热器和传感器

### [verify_heater]

加热器和温度传感器验证。对于打印机上配置的每个加热器，加热器验证会自动启用。使用 verify_heater 部分来更改默认设置。

```
[verify_heater heater_config_name]
#max_error: 120
#   在引发错误之前允许的最大"累积温度误差"。较小的值导致更严格的检查，
#   较大的值允许在报告错误之前有更多时间。具体来说，每秒检查一次温度，
#   如果温度接近目标温度，则重置内部"错误计数器"；否则，如果温度低于目标范围，
#   则计数器增加报告温度与范围之差的量。如果计数器超过此"max_error"，
#   则引发错误。默认值为 120。
#check_gain_time:
#   控制初始加热期间的加热器验证。较小的值导致更严格的检查，较大的值允许
#   在报告错误之前有更多时间。具体来说，在初始加热期间，只要加热器在此时间范围内
#   （以秒为单位）温度升高，则重置内部"错误计数器"。对于挤出机默认为 20 秒，
#   对于 heater_bed 默认为 60 秒。
#hysteresis: 5
#   被认为在目标范围内的目标温度的最大温差（以摄氏度为单位）。这控制 max_error 范围检查。
#   自定义此值很少见。默认值为 5。
#heating_gain: 2
#   在 check_gain_time 检查期间加热器必须升高的最低温度（以摄氏度为单位）。自定义此值
#   很少见。默认值为 2。
```

### [homing_heaters]

在归位或探测轴时禁用加热器的工具。

```
[homing_heaters]
#steppers:
#   应导致加热器被禁用的步进电机的逗号分隔列表。默认情况下，任何归位/探测
#   移动都会禁用加热器。
#   典型示例：stepper_z
#heaters:
#   在归位/探测移动期间要禁用的加热器的逗号分隔列表。默认情况下禁用所有加热器。
#   典型示例：extruder, heater_bed
```

### [thermistor]

自定义热敏电阻（可以定义任意数量的带有"thermistor"前缀的部分）。自定义热敏电阻可用于加热器配置部分的 sensor_type 字段中。（例如，如果定义了"[thermistor my_thermistor]"部分，则可以在定义加热器时使用"sensor_type: my_thermistor"。）确保将热敏电阻部分放在配置文件中其首次在加热器部分使用之前。

```
[thermistor my_thermistor]
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#temperature3:
#resistance3:
#   在给定温度（以摄氏度为单位）下的三个电阻测量值（以欧姆为单位）。这三个测量值将用于
#   计算热敏电阻的 Steinhart-Hart 系数。使用 Steinhart-Hart 定义热敏电阻时必须提供这些参数。
#beta:
#   或者，可以定义 temperature1、resistance1 和 beta 来定义热敏电阻参数。
#   使用"beta"定义热敏电阻时必须提供此参数。
```

### [adc_temperature]

自定义 ADC 温度传感器（可以定义任意数量的带有"adc_temperature"前缀的部分）。这允许定义一个自定义温度传感器，该传感器测量模拟数字转换器（ADC）引脚上的电压，并使用一组配置的温度/电压（或温度/电阻）测量值之间的线性插值来确定温度。生成的传感器可用作加热器部分中的 sensor_type。（例如，如果定义了"[adc_temperature my_sensor]"部分，则可以在定义加热器时使用"sensor_type: my_sensor"。）确保将传感器部分放在配置文件中其首次在加热器部分使用之前。

```
[adc_temperature my_sensor]
#temperature1:
#voltage1:
#temperature2:
#voltage2:
#...
#   一组温度（以摄氏度为单位）和电压（以伏特为单位）作为转换温度时的参考。使用此传感器的
#   加热器部分还可以指定 adc_voltage 和 voltage_offset 参数来定义 ADC 电压（详见
#   "常见温度放大器"部分）。必须提供至少两个测量值。
#temperature1:
#resistance1:
#temperature2:
#resistance2:
#...
#   或者，可以指定一组温度（以摄氏度为单位）和电阻（以欧姆为单位）作为转换温度时的参考。
#   使用此传感器的加热器部分还可以指定 pullup_resistor 参数（详见"extruder"部分）。
#   必须提供至少两个测量值。
```

### [heater_generic]

通用加热器（可以定义任意数量的带有"heater_generic"前缀的部分）。这些加热器的行为类似于标准加热器（挤出机、加热床）。使用 SET_HEATER_TEMPERATURE 命令（详见 [G-Codes](G-Codes.md#heaters)）设置目标温度。

```
[heater_generic my_generic_heater]
#gcode_id:
#   在 M105 命令中报告温度时使用的 id。必须提供此参数。
#heater_pin:
#max_power:
#sensor_type:
#sensor_pin:
#smooth_time:
#control:
#pid_Kp:
#pid_Ki:
#pid_Kd:
#pwm_cycle_time:
#lost_update_tolerance:
#min_temp:
#max_temp:
#   有关上述参数的定义，请参阅"extruder"部分。
```

### [temperature_sensor]

通用温度传感器。可以定义任意数量的额外温度传感器，通过 M105 命令报告。

```
[temperature_sensor my_sensor]
#sensor_type:
#sensor_pin:
#min_temp:
#max_temp:
#   有关上述参数的定义，请参阅"extruder"部分。
#gcode_id:
#   有关此参数的定义，请参阅"heater_generic"部分。
```

## 温度传感器

Kalico 包含许多类型温度传感器的定义。这些传感器可用于任何需要温度传感器的配置部分（例如 `[extruder]` 或 `[heater_bed]` 部分）。

### 常见热敏电阻

常见热敏电阻。以下参数在使用其中一种传感器的加热器部分中可用。

```
sensor_type:
#   以下之一："EPCOS 100K B57560G104F"、"ATC Semitec 104GT-2"、
#   "ATC Semitec 104NT-4-R025H42G"、"Generic 3950"、
#   "Honeywell 100K 135-104LAG-J01"、"NTC 100K MGB18-104F39050L32"、
#   "SliceEngineering 450" 或 "TDK NTCG104LH104JT1"
sensor_pin:
#   连接到热敏电阻的模拟输入引脚。必须提供此参数。
#pullup_resistor: 4700
#   连接到热敏电阻的上拉电阻（以欧姆为单位）。默认值为 4700 欧姆。
#inline_resistor: 0
#   与热敏电阻串联的额外（非温度变化）电阻（以欧姆为单位）。设置此值很少见。
#   默认值为 0 欧姆。
```

### 常见温度放大器

常见温度放大器。以下参数在使用其中一种传感器的加热器部分中可用。

```
sensor_type:
#   以下之一："PT100 INA826"、"AD595"、"AD597"、"AD8494"、"AD8495"、
#   "AD8496" 或 "AD8497"。
sensor_pin:
#   连接到传感器的模拟输入引脚。必须提供此参数。
#adc_voltage: 5.0
#   ADC 比较电压（以伏特为单位）。默认值为 5 伏特。
#voltage_offset: 0
#   ADC 电压偏移（以伏特为单位）。默认值为 0。
```

### 直接连接的 PT1000 传感器

直接连接的 PT1000 传感器。以下参数在使用其中一种传感器的加热器部分中可用。

```
sensor_type: PT1000
sensor_pin:
#   连接到传感器的模拟输入引脚。必须提供此参数。
#pullup_resistor: 4700
#   连接到传感器的上拉电阻（以欧姆为单位）。默认值为 4700 欧姆。
```

### MAXxxxxx 温度传感器

MAXxxxxx 串行外设接口（SPI）温度传感器。以下参数在使用其中一种传感器类型的加热器部分中可用。

```
sensor_type:
#   以下之一："MAX6675"、"MAX31855"、"MAX31856" 或 "MAX31865"。
sensor_pin:
#   传感器芯片的片选线。必须提供此参数。
#spi_speed: 4000000
#   与芯片通信时使用的 SPI 速度（以赫兹为单位）。默认值为 4000000。
#spi_bus:
#spi_software_sclk_pin:
#spi_software_mosi_pin:
#spi_software_miso_pin:
#   有关上述参数的描述，请参阅"常见 SPI 设置"部分。
#tc_type: K
#tc_use_50Hz_filter: False
#tc_averaging_count: 1
#   以上参数控制 MAX31856 芯片的传感器参数。每个参数的默认值在上列表中参数名称旁边。
#rtd_nominal_r: 100
#rtd_reference_r: 430
#rtd_num_of_wires: 2
#rtd_use_50Hz_filter: False
#   以上参数控制 MAX31865 芯片的传感器参数。每个参数的默认值在上列表中参数名称旁边。
```

### BMP180/BMP280/BME280/BMP388/BME680 温度传感器

BMP180/BMP280/BME280/BMP388/BME680 双线接口（I2C）环境传感器。注意，这些传感器不用于挤出机和加热床，而是用于监测环境温度（摄氏度）、压力（百帕）、相对湿度以及 BME680 的气体浓度。有关可用于报告压力和湿度的 gcode_macro，请参阅 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: BME280
#i2c_address:
#   默认是 118 (0x76)。BMP180、BMP388 和一些 BME280 传感器的地址为 119 (0x77)。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅"常见 I2C 设置"部分。
```

### AHT10/AHT20/AHT21/AHT30 温度传感器

AHT10/AHT20/AHT21/AHT30 双线接口（I2C）环境传感器。注意，这些传感器不用于挤出机和加热床，而是用于监测环境温度（摄氏度）和相对湿度。有关可用于报告湿度和温度的 gcode_macro，请参阅 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type: AHT10
#   必须是 "AHT1X"、"AHT2X"、"AHT3X"
#   一些 AHT20 传感器可以使用 "AHT1X"
#i2c_address:
#   默认是 56 (0x38)。一些 AHT10 传感器可以通过移动电阻来使用 57 (0x39)。
#i2c_mcu:
#i2c_bus:
#i2c_speed:
#   有关上述参数的描述，请参阅"常见 I2C 设置"部分。
#aht10_report_time:
#   读取间隔（以秒为单位）。默认值为 30，最小值为 5
```

### HTU21D 传感器

HTU21D 系列双线接口（I2C）环境传感器。注意，此传感器不用于挤出机和加热床，而是用于监测环境温度（摄氏度）和相对湿度。有关可用于报告湿度和温度的 gcode_macro，请参阅 [sample-macros.cfg](../config/sample-macros.cfg)。

```
sensor_type:
#   必须是 "HTU21D"、"SI7013"、"SI7020"、"SI7021" 或 "SHT21"
#i2c_address:
#   默认是 64 (0x40)。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅"常见 I2C 设置"部分。
#htu21d_hold_master:
#   传感器是否可以在读取时保持 I2C 缓冲区。如果为 True，读取期间不能执行其他总线通信。
#   默认值为 False。
#htu21d_resolution:
#   温度和湿度读取的分辨率。
#   有效值为：
#    'TEMP14_HUM12' -> 温度 14 位，湿度 12 位
#    'TEMP13_HUM10' -> 温度 13 位，湿度 10 位
#    'TEMP12_HUM08' -> 温度 12 位，湿度 08 位
#    'TEMP11_HUM11' -> 温度 11 位，湿度 11 位
#   默认值为："TEMP11_HUM11"
#htu21d_report_time:
#   读取间隔（以秒为单位）。默认值为 30
```

### SHT3X 传感器

SHT3X 系列双线接口（I2C）环境传感器。这些传感器的范围为 -55~125 摄氏度，因此可用于例如腔室温度监测。它们还可以用作简单的风扇/加热器控制器。

```
sensor_type: SHT3X
#i2c_address:
#   默认是 68 (0x44)。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅"常见 I2C 设置"部分。
```

### LM75 温度传感器

LM75/LM75A 双线（I2C）连接的温度传感器。这些传感器的范围为 -55~125 摄氏度，因此可用于例如腔室温度监测。它们还可以用作简单的风扇/加热器控制器。

```
sensor_type: LM75
#i2c_address:
#   默认是 72 (0x48)。正常范围是 72-79 (0x48-0x4F)，地址的 3 个低位通过芯片上的引脚配置
#   （通常使用跳线或硬连线）。
#i2c_mcu:
#i2c_bus:
#i2c_software_scl_pin:
#i2c_software_sda_pin:
#i2c_speed:
#   有关上述参数的描述，请参阅"常见 I2C 设置"部分。
#lm75_report_time:
#   读取间隔（以秒为单位）。默认值为 0.8，最小值为 0.5。
```

### 内置微控制器温度传感器

atsam、atsamd、stm32 和 rp2040 微控制器包含一个内部温度传感器。可以使用"temperature_mcu"传感器来监测这些温度。

```
sensor_type: temperature_mcu
#sensor_mcu: mcu
#   要从中读取的微控制器。默认值为"mcu"。
#reference_voltage:
#   微控制器 ADC 的参考电压。默认值为 3.3
#sensor_temperature1:
#sensor_adc1:
#   指定以上两个参数（摄氏度温度和 0.0 到 1.0 之间的 ADC 浮点值）以校准微控制器温度。
#   这可能会提高某些芯片上报告温度的准确性。获取此校准信息的一种典型方法是完全切断
#   打印机的电源几个小时（以确保其处于环境温度），然后接通电源并使用 QUERY_ADC 命令
#   获取 ADC 测量值。使用打印机上的其他温度传感器来找到相应的环境温度。默认使用
#   微控制器上的出厂校准数据（如果适用）或微控制器规格中的标称值。
#sensor_temperature2:
#sensor_adc2:
#   如果指定了 sensor_temperature1/sensor_adc1，则还可以指定
#   sensor_temperature2/sensor_adc2 校准数据。这样做可能会提供校准的"温度斜率"信息。
#   默认使用微控制器上的出厂校准数据（如果适用）或微控制器规格中的标称值。
```

### 主机温度传感器

运行主机软件的机器（例如 Raspberry Pi）的温度。

```
sensor_type: temperature_host
#sensor_path:
#   温度系统文件的路径。默认是"/sys/class/thermal/thermal_zone0/temp"，
#   这是 Raspberry Pi 计算机上的温度系统文件。
```

### DS18B20 温度传感器

DS18B20 是一种 1 线（w1）数字温度传感器。注意，此传感器不用于挤出机和加热床，而是用于监测环境温度（摄氏度）。这些传感器的范围高达 125 摄氏度，因此可用于例如腔室温度监测。它们还可以用作简单的风扇/加热器控制器。DS18B20 传感器仅在"host mcu"（例如 Raspberry Pi）上受支持。必须安装 w1-gpio Linux 内核模块。

```
sensor_type: DS18B20
serial_no:
#   每个 1 线设备都有一个唯一的序列号用于识别设备，通常格式为 28-031674b175ff。
#   必须提供此参数。可以使用以下 Linux 命令列出附加的 1 线设备：
#   ls /sys/bus/w1/devices/
#ds18_report_time:
#   读取间隔（以秒为单位）。默认值为 3.0，最小值为 1.0
#sensor_mcu:
#   要从中读取的微控制器。必须是 host_mcu
```

### 组合温度传感器

组合温度传感器是基于其他几个传感器的虚拟温度传感器。此传感器可用于挤出机、heater_generic 和加热床。

```
sensor_type: temperature_combined
#sensor_list:
#   必须提供。要组合成新"虚拟"传感器的传感器列表。每个条目应为温度报告对象的全名，
#   如其在配置中所示（例如 'extruder'、'heater_bed' 或自定义传感器的 'temperature_sensor <name>'）。
#   例如 'temperature_sensor sensor1, temperature_sensor sensor2'
#   例如 'extruder, heater_bed'
#   例如 'temperature_sensor chamber, extruder, heater_bed'
#combination_method:
#   必须提供。用于传感器的组合方法。可用选项为 'max'、'min'、'mean'。
#maximum_deviation:
#   必须提供。要组合的传感器之间允许的最大偏差（例如 5 度）。要禁用它，请使用大值（例如 999.9）
```

### MPC 环境传感器

虚拟 MPC 传感器，显示内部环境温度值（如果使用除 MPC 以外的任何算法，默认值为 25）

```
sensor_type: mpc_ambient_temperature
heater_name: extruder
#   输入此传感器绑定的加热器名称（此参数是必需的）
#gcode_id: AT
min_temp: 0
max_temp: 325
#ignore_limits: False
#   忽略温度限制（如果设置为 true，则可以省略最小和最大温度）
#echo_limits_to_console: False
#   如果设置为 true，限制将回显到控制台，而不仅仅是忽略（如果 ignore_limits 为 true）
```

### MPC 模块传感器

虚拟 MPC 传感器，显示内部环境温度值（如果使用除 MPC 以外的任何算法，默认值为 25）

```
sensor_type: mpc_block_temperature
heater_name: extruder
#   输入此传感器绑定的加热器名称（此参数是必需的）
#gcode_id: BE
min_temp: 0
max_temp: 325
#ignore_limits: False
#   忽略温度限制（如果设置为 true，则可以省略最小和最大温度）
#echo_limits_to_console: False
#   如果设置为 true，限制将回显到控制台，而不仅仅是忽略（如果 ignore_limits 为 true）
```


## 风扇

### [fan]

打印冷却风扇。

```
[fan]
pin:
#   控制风扇的输出引脚。必须提供此参数。
#max_power: 1.0
#   引脚可以设置的最大功率（0.0 到 1.0）。值 1.0 长时间完全启用引脚，而 0.5 允许
#   它不超过一半时间。用于限制风扇的总功率输出（长时间）。此值与 min_power 结合
#   以缩放风扇速度。当 `min_power` 为 0.3 且 `max_power` 为 1.0 时，风扇速度请求在
#   0.3 (min_power) 和 1.0 (max_power) 之间缩放。请求 10% 风扇速度导致值为 0.37。
#   默认值为 1.0。
#shutdown_speed: 0
#   如果微控制器软件进入错误状态，所需的风扇速度（表示为 0.0 到 1.0 之间的值）。
#   默认值为 0。
#cycle_time: 0.010
#   每个 PWM 功率周期的时间（以秒为单位）。使用基于软件的 PWM 时，建议为 10 毫秒或更大。
#   默认值为 0.010 秒。
#hardware_pwm: False
#   启用此项以使用硬件 PWM 而不是软件 PWM。大多数风扇不能很好地工作在硬件 PWM 上，
#   因此不建议启用此项，除非有电气要求需要以非常高的速度切换。使用硬件 PWM 时，
#   实际周期时间受实现限制，可能与请求的 cycle_time 显著不同。默认值为 False。
#kick_start_time: 0.100
#   首次启用或将其增加超过 50% 时以全速运行风扇的时间（以秒为单位）（有助于启动
#   风扇旋转）。默认值为 0.100 秒。
#min_power: 0.0
#   将驱动风扇的最低输入功率（表示为 0.0 到 1.0 之间的值）。默认值为 0.0。
#
#   要校准此设置，从 min_power=0 和 max_power=1 开始
#   逐渐降低风扇速度以确定可靠驱动风扇而不会失速的最低输入速度。将 min_power 设置为
#   对应此值的占空比（例如，12% -> 0.12）或稍高一点。
#tachometer_pin:
#   用于监测风扇速度的转速计输入引脚。通常需要上拉。此参数是可选的。
#tachometer_ppr: 2
#   指定 tachometer_pin 时，这是转速计信号每转的脉冲数。对于 BLDC 风扇，这通常是
#   极数的一半。默认值为 2。
#tachometer_poll_interval: 0.0015
#   指定 tachometer_pin 时，这是转速计引脚的轮询周期（以秒为单位）。默认值为 0.0015，
#   这对于转速低于 10000 RPM、PPR 为 2 的风扇来说足够快。此值必须小于
```