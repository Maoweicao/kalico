# 基准测试

本文档描述了 Kalico 的基准测试。

## 微控制器基准测试

本节描述了用于生成 Kalico 微控制器步进速率基准测试的机制。

基准测试的主要目标是提供一种一致的机制来衡量软件内部编码变更的影响。次要目标是提供高级指标，用于比较不同芯片和不同软件平台之间的性能。

步进速率基准测试旨在找到硬件和软件能够达到的最大步进速率。此基准测试步进速率在日常使用中是无法实现的，因为 Kalico 在任何实际使用中都需要执行其他任务（例如，mcu/主机通信、温度读取、限位开关检查）。

通常，基准测试测试的引脚选择用于闪烁 LED 或其他无害引脚。**在运行基准测试之前，请始终验证驱动配置的引脚是否安全。**不建议在基准测试期间驱动实际的步进电机。

### 步进速率基准测试

测试使用 console.py 工具执行（在 [Debugging.md](Debugging.md) 中描述）。微控制器配置为特定的硬件平台（见下文），然后将以下内容复制粘贴到 console.py 终端窗口中：
```
SET start_clock {clock+freq}
SET ticks 1000

reset_step_clock oid=0 clock={start_clock}
set_next_step_dir oid=0 dir=0
queue_step oid=0 interval={ticks} count=60000 add=0
set_next_step_dir oid=0 dir=1
queue_step oid=0 interval=3000 count=1 add=0

reset_step_clock oid=1 clock={start_clock}
set_next_step_dir oid=1 dir=0
queue_step oid=1 interval={ticks} count=60000 add=0
set_next_step_dir oid=1 dir=1
queue_step oid=1 interval=3000 count=1 add=0

reset_step_clock oid=2 clock={start_clock}
set_next_step_dir oid=2 dir=0
queue_step oid=2 interval={ticks} count=60000 add=0
set_next_step_dir oid=2 dir=1
queue_step oid=2 interval=3000 count=1 add=0
```

以上测试了三个步进电机同时步进。如果运行上述内容导致 "Rescheduled timer in the past" 或 "Stepper too far in past" 错误，则表明 `ticks` 参数太低（它导致步进速率过快）。目标是找到 `ticks` 参数的最低设置，该设置能可靠地使测试成功完成。应该可以对 `ticks` 参数进行二分查找，直到找到稳定的值。

失败时，可以复制粘贴以下内容以清除错误，为下一次测试做准备：
```
clear_shutdown
```

要获得单个步进电机的基准测试结果，使用相同的配置序列，但仅将上述测试的第一个块复制粘贴到 console.py 窗口中。

要生成 [Features](Features.md) 文档中的基准测试结果，每秒总步数是通过将活动步进电机数量乘以标称 mcu 频率，然后除以最终的 `ticks` 参数来计算的。结果四舍五入到最近的 K。例如，使用三个活动步进电机：
```
ECHO Test result is: {"%.0fK" % (3. * freq / ticks / 1000.)}
```

基准测试使用适用于 TMC 驱动器的参数运行。对于支持 `STEPPER_BOTH_EDGE=1` 的微控制器（如 console.py 首次启动时 `MCU config` 行中报告的那样），使用 `step_pulse_duration=0` 和 `invert_step=-1` 以启用在步进脉冲两个边沿上的优化步进。对于其他微控制器，使用对应于 100ns 的 `step_pulse_duration`。

### AVR 步进速率基准测试

AVR 芯片上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA5 dir_pin=PA4 invert_step=0 step_pulse_ticks=32
config_stepper oid=1 step_pin=PA3 dir_pin=PA2 invert_step=0 step_pulse_ticks=32
config_stepper oid=2 step_pin=PC7 dir_pin=PC6 invert_step=0 step_pulse_ticks=32
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `avr-gcc (GCC) 5.4.0`。16Mhz 和 20Mhz 测试均使用配置为 atmega644p 的 simulavr 运行（之前的测试已确认 simulavr 结果与 16Mhz at90usb 和 16Mhz atmega2560 上的测试结果匹配）。

| avr              | ticks |
| ---------------- | ----- |
| 1 stepper        | 102   |
| 3 stepper        | 486   |

### Arduino Due 步进速率基准测试

Due 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PB27 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB26 dir_pin=PC30 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA21 dir_pin=PC30 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| sam3x8e              | ticks |
| -------------------- | ----- |
| 1 stepper            | 66    |
| 3 stepper            | 257   |

### Duet Maestro 步进速率基准测试

Duet Maestro 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC26 dir_pin=PC18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PC26 dir_pin=PA8 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PC26 dir_pin=PB4 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| sam4s8c              | ticks |
| -------------------- | ----- |
| 1 stepper            | 71    |
| 3 stepper            | 260   |

### Duet Wifi 步进速率基准测试

Duet Wifi 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PD6 dir_pin=PD11 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PD7 dir_pin=PD12 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PD8 dir_pin=PD13 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `gcc version 10.3.1 20210621 (release) (GNU Arm Embedded Toolchain 10.3-2021.07)`。

| sam4e8e          | ticks |
| ---------------- | ----- |
| 1 stepper        | 48    |
| 3 stepper        | 215   |

### Beaglebone PRU 步进速率基准测试

PRU 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio0_23 dir_pin=gpio1_12 invert_step=0 step_pulse_ticks=20
config_stepper oid=1 step_pin=gpio1_15 dir_pin=gpio0_26 invert_step=0 step_pulse_ticks=20
config_stepper oid=2 step_pin=gpio0_22 dir_pin=gpio2_1 invert_step=0 step_pulse_ticks=20
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `pru-gcc (GCC) 8.0.0 20170530 (experimental)`。

| pru              | ticks |
| ---------------- | ----- |
| 1 stepper        | 231   |
| 3 stepper        | 847   |

### STM32F042 步进速率基准测试

STM32F042 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA1 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PA3 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB8 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32f042        | ticks |
| ---------------- | ----- |
| 1 stepper        | 59    |
| 3 stepper        | 249   |

### STM32F103 步进速率基准测试

STM32F103 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC13 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB3 dir_pin=PB6 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA4 dir_pin=PB7 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32f103            | ticks |
| -------------------- | ----- |
| 1 stepper            | 61    |
| 3 stepper            | 264   |

### STM32F4 步进速率基准测试

STM32F4 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA5 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。STM32F407 结果是在 STM32F446 上运行 STM32F407 二进制文件获得的（因此使用 168Mhz 时钟）。

| stm32f446            | ticks |
| -------------------- | ----- |
| 1 stepper            | 46    |
| 3 stepper            | 205   |

| stm32f407            | ticks |
| -------------------- | ----- |
| 1 stepper            | 46    |
| 3 stepper            | 205   |

### STM32H7 步进速率基准测试

STM32H723 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA13 dir_pin=PB5 invert_step=-1 step_pulse_ticks=52
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=52
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=52
finalize_config crc=0
```

测试上次在提交 `554ae78d` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`。

| stm32h723            | ticks |
| -------------------- | ----- |
| 1 stepper            | 70    |
| 3 stepper            | 181   |

### STM32G0B1 步进速率基准测试

STM32G0B1 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PB13 dir_pin=PB12 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB10 dir_pin=PB2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB0 dir_pin=PC5 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `247cd753` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32g0b1        | ticks |
| ---------------- | ----- |
| 1 stepper        | 58    |
| 3 stepper        | 243   |

### STM32G4 步进速率基准测试

STM32G431 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA0 dir_pin=PB5 invert_step=-1 step_pulse_ticks=17
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=17
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=17
finalize_config crc=0
```

测试上次在提交 `cfa48fe3` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`。

| stm32g431        | ticks |
| ---------------- | ----- |
| 1 stepper        | 47    |
| 3 stepper        | 208   |

### LPC176x 步进速率基准测试

LPC176x 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=P1.20 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=P1.21 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=P1.23 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。120Mhz LPC1769 结果是通过将 LPC1768 超频至 120Mhz 获得的。

| lpc1768              | ticks |
| -------------------- | ----- |
| 1 stepper            | 52    |
| 3 stepper            | 222   |

| lpc1769              | ticks |
| -------------------- | ----- |
| 1 stepper            | 51    |
| 3 stepper            | 222   |

### SAMD21 步进速率基准测试

SAMD21 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA27 dir_pin=PA20 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB3 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA17 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`，在 SAMD21G18 微控制器上。

| samd21               | ticks |
| -------------------- | ----- |
| 1 stepper            | 70    |
| 3 stepper            | 306   |

### SAMD51 步进速率基准测试

SAMD51 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA22 dir_pin=PA20 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PA22 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA22 dir_pin=PA19 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`，在 SAMD51J19A 微控制器上。

| samd51               | ticks |
| -------------------- | ----- |
| 1 stepper            | 39    |
| 3 stepper            | 191   |
| 1 stepper (200Mhz)   | 39    |
| 3 stepper (200Mhz)   | 181   |

### SAME70 步进速率基准测试

SAME70 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC18 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PC16 dir_pin=PD10 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PC28 dir_pin=PA4 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```


测试上次在提交 `34e9ea55` 上运行，gcc 版本为 `arm-none-eabi-gcc (NixOS 10.3-2021.10) 10.3.1`，在 SAME70Q20B 微控制器上。

| same70               | ticks |
| -------------------- | ----- |
| 1 stepper            | 45    |
| 3 stepper            | 190   |

### AR100 步进速率基准测试

AR100 CPU（Allwinner A64）上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PL10 dir_pin=PE14 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PL11 dir_pin=PE15 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PL12 dir_pin=PE16 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0

```

测试上次在提交 `b7978d37` 上运行，gcc 版本为 `or1k-linux-musl-gcc (GCC) 9.2.0`，在 Allwinner A64-H 微控制器上。

| AR100 R_PIO          | ticks |
| -------------------- | ----- |
| 1 stepper            | 85    |
| 3 stepper            | 359   |

### RPxxxx 步进速率基准测试

RP2040 和 RP2350 上使用以下配置序列：

```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio25 dir_pin=gpio3 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=gpio26 dir_pin=gpio4 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=gpio27 dir_pin=gpio5 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试上次在提交 `14c105b8` 上运行，gcc 版本为 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`，在 Raspberry Pi Pico 和 Pico 2 板上。

| rp2040 (*)           | ticks |
| -------------------- | ----- |
| 1 stepper            | 3     |
| 3 stepper            | 14    |

| rp2350               | ticks |
| -------------------- | ----- |
| 1 stepper            | 36    |
| 3 stepper            | 169   |

(*) 注意报告的 rp2040 ticks 是相对于 12Mhz 调度定时器的，与其 200Mhz 内部 ARM 处理速率不对应。预计 5 个调度 ticks 对应约 42 个 ARM 核心周期，14 个调度 ticks 对应约 225 个 ARM 核心周期。

### Linux MCU 步进速率基准测试

Raspberry Pi 上使用以下配置序列：
```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio2 dir_pin=gpio3 invert_step=0 step_pulse_ticks=5
config_stepper oid=1 step_pin=gpio4 dir_pin=gpio5 invert_step=0 step_pulse_ticks=5
config_stepper oid=2 step_pin=gpio6 dir_pin=gpio17 invert_step=0 step_pulse_ticks=5
finalize_config crc=0
```

测试上次在提交 `59314d99` 上运行，gcc 版本为 `gcc (Raspbian 8.3.0-6+rpi1) 8.3.0`，在 Raspberry Pi 3（修订版 a02082）上。在此基准测试中很难获得稳定的结果。

| Linux (RPi3)         | ticks |
| -------------------- | ----- |
| 1 stepper            | 160   |
| 3 stepper            | 380   |

## 命令分发基准测试

命令分发基准测试测试微控制器可以处理多少个"虚拟"命令。它主要是对硬件通信机制的测试。测试使用 console.py 工具运行（在 [Debugging.md](Debugging.md) 中描述）。将以下内容复制粘贴到 console.py 终端窗口中：
```
DELAY {clock + 2*freq} get_uptime
FLOOD 100000 0.0 debug_nop
get_uptime
```

测试完成后，确定两个"uptime"响应消息中报告的时钟之间的差异。然后每秒总命令数为 `100000 * mcu_frequency / clock_diff`。

请注意，此测试可能会使 Raspberry Pi 的 USB/CPU 容量饱和。如果在 Raspberry Pi、Beaglebone 或类似的主机计算机上运行，则增加延迟（例如，`DELAY {clock + 20*freq} get_uptime`）。在适用的情况下，以下基准测试是在台式机上运行 console.py，设备通过高速集线器连接的结果。

| MCU                 | Rate | Build    | Build compiler      |
| ------------------- | ---- | -------- | ------------------- |
| stm32f042 (CAN)     |  18K | c105adc8 | arm-none-eabi-gcc (GNU Tools 7-2018-q3-update) 7.3.1 |
| atmega2560 (serial) |  23K | b161a69e | avr-gcc (GCC) 4.8.1 |
| sam3x8e (serial)    |  23K | b161a69e | arm-none-eabi-gcc (Fedora 7.1.0-5.fc27) 7.1.0 |
| at90usb1286 (USB)   |  75K | 01d2183f | avr-gcc (GCC) 5.4.0 |
| ar100 (serial)      | 138K | 08d037c6 | or1k-linux-musl-gcc 9.3.0 |
| samd21 (USB)        | 223K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| pru (shared memory) | 260K | c5968a08 | pru-gcc (GCC) 8.0.0 20170530 (experimental) |
| stm32f103 (USB)     | 355K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| sam3x8e (USB)       | 418K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| lpc1768 (USB)       | 534K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| lpc1769 (USB)       | 628K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| sam4s8c (USB)       | 650K | 8d4a5c16 | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| samd51 (USB)        | 864K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| stm32f446 (USB)     | 870K | 01d2183f | arm-none-eabi-gcc (Fedora 7.4.0-1.fc30) 7.4.0 |
| rp2040 (USB)        | 885K | f6718291 | arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0 |
| rp2350 (USB)        | 885K | f6718291 | arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0 |

## 主机基准测试

可以使用"批处理模式"处理机制（在 [Debugging.md](Debugging.md) 中描述）对主机软件运行计时测试。这通常通过选择一个大型且复杂的 G-Code 文件，并计时主机软件处理该文件所需的时间来完成。例如：
```
time ~/klippy-env/bin/python ./klippy/klippy.py config/example-cartesian.cfg -i something_complex.gcode -o /dev/null -d out/klipper.dict
```
