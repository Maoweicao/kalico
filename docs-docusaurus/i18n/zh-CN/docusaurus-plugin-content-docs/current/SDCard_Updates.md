# SD 卡更新

当今许多流行的控制器板都附带能够通过 SD 卡更新固件的引导加载程序。虽然这在许多情况下很方便，但这些引导加载程序通常不提供其他更新固件的方式。如果你的板安装在难以访问的位置或者你需要经常更新固件，这可能很麻烦。在将 Kalico 初始刷写到控制器后，可以通过 ssh 将新固件传输到 SD 卡并启动刷写过程。

## 典型升级过程

使用 SD 卡更新 MCU 固件的过程与其他方法类似。与其使用 `make flash`，需要运行辅助脚本 `flash-sdcard.sh`。更新 BigTreeTech SKR 1.3 可能如下所示：
```
sudo service klipper stop
cd ~/klipper
git pull
make clean
make menuconfig
make
./scripts/flash-sdcard.sh /dev/ttyACM0 btt-skr-v1.3
sudo service klipper start
```

用户需要确定设备位置和板名称。如果用户需要刷写多个板，应在重启 Klipper 服务之前为每个板运行 `flash-sdcard.sh`（或在适当时使用 `make flash`）。

可以使用以下命令列出支持的板：
```
./scripts/flash-sdcard.sh -l
```
如果你没有看到你的板列在其中，可能需要添加新的板定义，[如下所述](#board-definitions)。

## 高级用法

上述命令假设你的 MCU 以默认波特率 250000 连接，固件位于 `~/klipper/out/klipper.bin`。`flash-sdcard.sh` 脚本提供了更改这些默认值的选项。所有选项可以通过帮助屏幕查看：
```
./scripts/flash-sdcard.sh -h
SD Card upload utility for Kalico

usage: flash_sdcard.sh [-h] [-l] [-c] [-b <baud>] [-f <firmware>]
                       <device> <board>

positional arguments:
  <device>        device serial port
  <board>         board type

optional arguments:
  -h              show this message
  -l              list available boards
  -c              run flash check/verify only (skip upload)
  -b <baud>       serial baud rate (default is 250000)
  -f <firmware>   path to klipper.bin
```

如果你的板使用自定义波特率的固件刷写，可以通过指定 `-b` 选项来升级：
```
./scripts/flash-sdcard.sh -b 115200 /dev/ttyAMA0 btt-skr-v1.3
```

如果你想刷写位于默认位置以外的 Kalico 构建版本，可以通过指定 `-f` 选项来完成：
```
./scripts/flash-sdcard.sh -f ~/downloads/klipper.bin /dev/ttyAMA0 btt-skr-v1.3
```

请注意，升级 MKS Robin E3 时，不需要手动运行 `update_mks_robin.py` 并将生成的二进制文件提供给 `flash-sdcard.sh`。此过程在上传过程中自动完成。

`-c` 选项用于执行仅检查或验证操作，以测试板是否正确运行指定的固件。此选项主要用于需要手动电源循环才能完成刷写过程的情况，例如使用 SDIO 模式（而不是 SPI）访问其 SD 卡的引导加载程序。（请参阅下面的注意事项）但是，它也可以随时用于验证刷写到板上的代码是否与构建文件夹中的版本匹配。

## 注意事项

- 如介绍中所述，此方法仅适用于升级固件。初始刷写过程必须根据适用于你的控制器板的说明手动完成。
- 虽然可以刷写更改串口波特率或连接接口（即从 USB 到 UART）的构建版本，但验证将始终失败，因为脚本将无法重新连接到 MCU 以验证当前版本。
- 仅支持使用 SPI 进行 SD 卡通信的板。使用 SDIO 的板（如 Flymaker Flyboard 和 MKS Robin Nano V1/V2）在 SDIO 模式下将无法工作。但是，通常可以使用软件 SPI 模式代替来刷写此类板。但如果板的引导加载程序仅使用 SDIO 模式访问 SD 卡，则需要对板和 SD 卡进行电源循环，以便将模式从 SPI 切换回 SDIO 以完成重新刷写。此类板应定义为启用 `skip_verify` 以在刷写后立即跳过验证步骤。然后在手动电源循环后，你可以重新运行完全相同的 `./scripts/flash-sdcard.sh` 命令，但添加 `-c` 选项以完成检查/验证操作。有关示例，请参阅[刷写使用 SDIO 的板](#flashing-boards-that-use-sdio)。

## 板定义

大多数常见板应该可用，但如有必要，可以添加新的板定义。板定义位于 `~/klipper/scripts/spi_flash/board_defs.py` 中。定义存储在字典中，例如：
```python
BOARD_DEFS = {
    'generic-lpc1768': {
        'mcu': "lpc1768",
        'spi_bus': "ssp1",
        "cs_pin": "P0.6"
    },
    ...<further definitions>
}
```

可以指定以下字段：
- `mcu`：MCU 类型。这可以通过在通过 `make menuconfig` 配置构建后运行 `cat .config | grep CONFIG_MCU` 来获取。此字段是必需的。
- `spi_bus`：连接到 SD 卡的 SPI 总线。这应该从板的原理图中获取。此字段是必需的。
- `cs_pin`：连接到 SD 卡的芯片选择引脚。这应该从板的原理图中获取。此字段是必需的。
- `firmware_path`：固件应传输到的 SD 卡上的路径。默认为 `firmware.bin`。
- `current_firmware_path`：成功刷写后重命名的固件文件在 SD 卡上的路径。默认为 `firmware.cur`。
- `skip_verify`：定义布尔值，告诉脚本在刷写过程中跳过固件验证步骤。默认为 `False`。对于需要手动电源循环才能完成刷写的板，可以设置为 `True`。之后要验证固件，请使用 `-c` 选项再次运行脚本以执行验证步骤。[请参阅 SDIO 卡的注意事项](#caveats)

如果需要软件 SPI，`spi_bus` 字段应设置为 `swspi`，并且应指定以下附加字段：
- `spi_pins`：这应该是 3 个以逗号分隔的引脚，连接到 SD 卡，格式为 `miso,mosi,sclk`。

软件 SPI 应该非常罕见，通常只有具有设计错误或通常仅支持 SD 卡 SDIO 模式的板才需要它。`btt-skr-pro` 板定义提供了前者的示例，`btt-octopus-f446-v1` 板定义提供了后者的示例。

在创建新的板定义之前，应检查现有板定义是否满足新板所需的条件。如果是这种情况，可以指定 `BOARD_ALIAS`。例如，可以添加以下别名来指定 `my-new-board` 作为 `generic-lpc1768` 的别名：
```python
BOARD_ALIASES = {
    ...<previous aliases>,
    'my-new-board': BOARD_DEFS['generic-lpc1768'],
}
```

如果你需要新的板定义并且对上面概述的过程不满意，建议在 Kalico [Discord 服务器](Contact.md#discord)中请求一个。

## 刷写使用 SDIO 的板

[如注意事项中所述](#caveats)，引导加载程序使用 SDIO 模式访问其 SD 卡的板需要对板进行电源循环，特别是 SD 卡本身，以便从写入文件时使用的 SPI 模式切换回 SDIO 模式，以便引导加载程序将其刷写到板中。这些板定义将使用 `skip_verify` 标志，该标志告诉刷写工具在将固件写入 SD 卡后停止，以便可以手动电源循环板，并将验证步骤推迟到完成后。

有两种情况——一种是 RPi 主机在单独的电源上运行，另一种是 RPi 主机与正在刷写的主板在同一电源上运行。区别在于是否需要在刷写完成后关闭 RPi 并重新 `ssh` 才能执行验证步骤，或者验证是否可以立即执行。以下是两种情况的示例：

### RPi 使用单独电源的 SDIO 编程

RPi 使用单独电源的典型会话如下所示。当然，你需要使用正确的设备路径和板名称：
```
sudo service klipper stop
cd ~/klipper
git pull
make clean
make menuconfig
make
./scripts/flash-sdcard.sh /dev/ttyACM0 btt-octopus-f446-v1
[[[在指示时手动电源循环打印机板]]]
./scripts/flash-sdcard.sh -c /dev/ttyACM0 btt-octopus-f446-v1
sudo service klipper start
```

### RPi 使用相同电源的 SDIO 编程

RPi 使用相同电源的典型会话如下所示。当然，你需要使用正确的设备路径和板名称：
```
sudo service klipper stop
cd ~/klipper
git pull
make clean
make menuconfig
make
./scripts/flash-sdcard.sh /dev/ttyACM0 btt-octopus-f446-v1
sudo shutdown -h now
[[[等待 RPi 关机，然后在重新启动时电源循环并重新 ssh 到 RPi]]]
sudo service klipper stop
cd ~/klipper
./scripts/flash-sdcard.sh -c /dev/ttyACM0 btt-octopus-f446-v1
sudo service klipper start
```

在这种情况下，由于 RPi 主机正在重启，这将重启 `klipper` 服务，因此需要在执行验证步骤之前再次停止 `klipper`，并在验证完成后重启它。

### SDIO 到 SPI 引脚映射

如果你的板的原理图使用 SDIO 作为其 SD 卡，你可以按照下图中的描述映射引脚，以确定在 `board_defs.py` 文件中分配的兼容软件 SPI 引脚：

| SD 卡引脚 | Micro SD 卡引脚 | SDIO 引脚名称 | SPI 引脚名称 |
| :---------: | :----------------: | :--------------: | :--------------: |
| 9 | 1 | DATA2 | None (PU)* |
| 1 | 2 | CD/DATA3 | CS |
| 2 | 3 | CMD | MOSI |
| 4 | 4 | +3.3V (VDD) | +3.3V (VDD) |
| 5 | 5 | CLK | SCLK |
| 3 | 6 | GND (VSS) | GND (VSS) |
| 7 | 7 | DATA0 | MISO |
| 8 | 8 | DATA1 | None (PU)* |
| N/A | 9 | Card Detect (CD) | Card Detect (CD) |
| 6 | 10 | GND | GND |

\* None (PU) 表示带有上拉电阻的未使用引脚
