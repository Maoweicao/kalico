# Bondtech INDX

本文档介绍如何与 Kalico 一起设置和校准 [Bondtech INDX](https://www.bondtech.se/) 工具板。INDX 工具板驱动感应式喷嘴加热器，带有非接触式红外温度传感器，并在工具板 MCU 上运行自己的 PID 控制器。

支持包括 `[indx]` 主机模块（参见[配置参考](Config_Reference.md#indx)）和针对工具板 SAME51 MCU 的专用固件，两者都包含在 Kalico 中。Kalico 是参考实现；[BondtechAB/indx_klipper](https://github.com/BondtechAB/indx_klipper) 模块跟踪 Kalico，为主流 Klipper 提供兼容性。另请参阅原始[调试指南](https://gist.github.com/dalegaard/b5106af63fcdde305e8c47421a8cc9b9)。

## 烧录固件

通过 USB 连接工具板，并在上电的同时桥接 `CAN RESET` 跳线以强制进入引导加载程序。设备应显示为 "INDX Toolboard Bootloader"，USB ID 为 `04d8:e483`：

```
$ lsusb | grep INDX
```

Kalico 附带了一个现成的构建配置。从 Kalico 目录运行：

```
$ KCONFIG_CONFIG=board_configs/bondtech_indx_usb.config make
$ KCONFIG_CONFIG=board_configs/bondtech_indx_usb.config make flash FLASH_DEVICE=04d8:e483
```

## 配置

最小配置如下所示：

```
[mcu indxmcu]
serial: /dev/serial/by-id/usb-Bondtech_INDX_<YOUR SERIAL>-if00

[indx]
mcu: indxmcu

[extruder]
sensor_type: indx
min_temp: 0
max_temp: 300
heater_pin: indx:heater
control: watermark
nozzle_diameter: 0.4
filament_diameter: 1.75
step_pin: indxmcu:motor_step
dir_pin: indxmcu:motor_dir
enable_pin: !indxmcu:motor_enable
microsteps: 32
rotation_distance: 5.7

[tmc2240 extruder]
cs_pin: indxmcu:motor_cs
spi_software_sclk_pin: indxmcu:motor_sclk
spi_software_mosi_pin: indxmcu:motor_mosi
spi_software_miso_pin: indxmcu:motor_miso
rref: 24000
run_current: 0.6

[fan]
pin: indxmcu:part_cooling
tachometer_pin: indxmcu:part_cooling_tacho
```

`[indx]` 模块为所有工具板引脚注册了命名别名（如 `indxmcu:motor_step`、`indxmcu:part_cooling`、`indxmcu:endstop`），并自动配置 SERCOM 外设。挤出机加热器作为虚拟引脚 `indx:heater` 暴露，喷嘴温度作为 `sensor_type: indx` 暴露。散热风扇由工具板模块自身管理：只要加热器激活、喷嘴发热或工具板上的步进电机启用，风扇就会开启，风扇堵塞会触发关机。

## 校准

在加热器校准前不会加热。在喷嘴冷却且打印机空闲时运行：

```
INDX_CALIBRATE
```

这会首先调整感应线圈驱动时序，然后执行加热/保温/降温循环以拟合热模型。完成后运行 `SAVE_CONFIG` 以持久化结果。

可选地校准零件冷却风扇补偿（需要配置零件冷却风扇）：

```
INDX_FAN_CALIBRATE
SAVE_CONFIG
```

热模型还会考虑熔融耗材带走的热量。可以直接设置耗材参数：

```
INDX_SET_MODEL_PARAMS FILAMENT_DENSITY=<g/cm3> FILAMENT_HEAT_CAPACITY=<J/g/K>
```

或者在喷嘴处于打印温度时加载耗材以测量这些参数：

```
INDX_LOAD_FILAMENT
```

使用 `INDX_CLEAR_FILAMENT` 重置耗材参数，并使用 `SAVE_CONFIG` 持久化任何这些值。

有关 INDX 命令及其参数的完整列表，请参见 [G-Code 参考](G-Codes.md#indx)。