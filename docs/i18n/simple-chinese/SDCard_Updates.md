# SD 卡更新

当今许多流行的控制器板都配有能够通过 SD 卡更新固件的引导加载程序。虽然这在许多情况下很方便，但这些引导加载程序通常不提供其他更新固件的方式。如果您的板安装在难以接触的位置或您需要频繁更新固件，这可能会很麻烦。在 Kalico 首次刷写到控制器后，可以通过 ssh 将新固件传输到 SD 卡并启动刷写过程。

## 典型升级过程

使用 SD 卡更新 MCU（微控制器）固件的过程与其他方法类似。不是使用 `make flash`，而是需要运行辅助脚本 `flash-sdcard.sh`。更新 BigTreeTech SKR 1.3 可能如下所示：
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

用户需要确定设备位置和板名称。如果用户需要刷写多个板，在重启 Klipper 服务之前应为每个板运行 `flash-sdcard.sh`（或适当时的 `make flash`）。

支持的板可以通过以下命令列出：
```
./scripts/flash-sdcard.sh -l
```
如果没有看到您的板列出，可能需要[如下所述](#board-definitions)添加新的板定义。

## 高级用法

上述命令假设您的 MCU 以默认波特率 250000 连接，且固件位于 `~/klipper/out/klipper.bin`。`flash-sdcard.sh` 脚本提供了更改这些默认值的选项。所有选项可以通过帮助屏幕查看：
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

如果您的板刷写有以自定义波特率连接的固件，可以通过指定 `-b` 选项来升级。

如果希望刷写位于默认位置以外的 Kalico 构建，可以通过指定 `-f` 选项来完成。

## 注意事项

- 如引言所述，此方法仅适用于升级固件。初始刷写过程必须按照适用于您控制器板的说明手动完成。
- 虽然可以刷写更改串口波特率或连接接口（即从 USB 到 UART）的构建，但验证将始终失败，因为脚本将无法重新连接到 MCU 以验证当前版本。
- 仅支持使用 SPI 进行 SD 卡通信的板。使用 SDIO 的板在 SDIO 模式下将无法工作。但是，通常可以使用软件 SPI 模式来刷写此类板。但如果板的引导加载程序仅使用 SDIO 模式访问 SD 卡，则需要手动断电再通电。
- 这样的板应定义 `skip_verify` 启用以跳过刷写后立即验证的步骤。然后在手动断电再通电后，可以重新运行完全相同的命令但添加 `-c` 选项来完成检查/验证操作。

## 板定义

大多数常见板应该可用，但如果需要可以添加新的板定义。板定义位于 `~/klipper/scripts/spi_flash/board_defs.py` 中。定义存储在字典中，例如：
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
- `mcu`：MCU 类型。可以在配置构建后通过运行 `cat .config | grep CONFIG_MCU` 检索。此字段是必需的。
- `spi_bus`：连接到 SD 卡的 SPI 总线。应从板的原理图中检索。此字段是必需的。
- `cs_pin`：连接到 SD 卡的片选引脚。应从板的原理图中检索。此字段是必需的。
- `firmware_path`：固件应传输到的 SD 卡上的路径。默认为 `firmware.bin`。
- `current_firmware_path`：成功刷写后重命名固件文件所在的 SD 卡上的路径。默认为 `firmware.cur`。
- `skip_verify`：定义布尔值，告知脚本在刷写过程中跳过固件验证步骤。默认为 `False`。

如果需要软件 SPI，`spi_bus` 字段应设置为 `swspi`，并应指定以下附加字段：
- `spi_pins`：应为 3 个逗号分隔的引脚，按 `miso,mosi,sclk` 格式连接到 SD 卡。

如果需要新的板定义且您对上述过程不熟悉，建议在 Kalico [Discord 服务器](Contact.md#discord)上请求一个。
