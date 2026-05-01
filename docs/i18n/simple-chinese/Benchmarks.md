# 基准测试

本文档描述 Kalico 基准测试。

## 微控制器基准测试

本节描述用于生成 Kalico 微控制器步长率基准测试的机制。

基准测试的主要目标是为测量软件内的编码更改的影响提供一致的机制。次要目标是为芯片之间和软件平台之间的性能比较提供高级指标。

步长率基准设计用于找到硬件和软件可以达到的最大步进速率。此基准步进速率在日常使用中不可达到，因为 Kalico 需要执行其他任务（例如，mcu/主机通信、温度读取、限位开关检查）在任何现实世界的使用中。

通常，基准测试的引脚选择用于闪烁 LED 或其他无害的引脚。**在运行基准测试之前，请务必验证驱动配置的引脚是安全的。** 不建议在基准测试期间驱动实际步进电机。

### 步长率基准测试

测试使用 console.py 工具进行（在 [Debugging.md](Debugging.md) 中描述）。微控制器针对特定硬件平台进行配置（见下文），然后将以下内容切割并粘贴到 console.py 终端窗口中：
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

上述测试三个步进电机同时步进。如果运行上述结果导致"Rescheduled timer in the past"或"Stepper too far in past"错误，则表示 `ticks` 参数太低（导致步进速率太快）。目标是找到最低的 ticks 参数设置，可靠地导致测试成功完成。应该能够对 ticks 参数进行二分查找，直到找到稳定的值。

失败时，可以复制并粘贴以下内容来清除错误，为下一个测试做准备：
```
clear_shutdown
```

要获得单个步进电机基准测试，使用相同的配置序列，但仅将上述测试的第一个块切割并粘贴到 console.py 窗口中。

要生成 [Features](Features.md) 文档中找到的基准测试，总步数每秒计算为将活跃步进电机的数量乘以名义 mcu 频率并除以最终 ticks 参数。结果四舍五入到最近的 K。例如，三个活跃步进电机：
```
ECHO Test result is: {"%.0fK" % (3. * freq / ticks / 1000.)}
```

基准测试使用适合 TMC 驱动程序的参数运行。对于支持 `STEPPER_BOTH_EDGE=1` 的微控制器（如启动 console.py 时的 `MCU config` 行所报告的），使用 `step_pulse_duration=0` 和 `invert_step=-1` 在步脉冲的两个边缘上启用优化步进。对于其他微控制器，使用对应于 100ns 的 `step_pulse_duration`。

### AVR 步长率基准测试

以下配置序列用于 AVR 芯片：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA5 dir_pin=PA4 invert_step=0 step_pulse_ticks=32
config_stepper oid=1 step_pin=PA3 dir_pin=PA2 invert_step=0 step_pulse_ticks=32
config_stepper oid=2 step_pin=PC7 dir_pin=PC6 invert_step=0 step_pulse_ticks=32
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `avr-gcc (GCC) 5.4.0`。16Mhz 和 20Mhz 测试都使用为 atmega644p 配置的 simulavr 运行（以前的测试确认 simulavr 结果与 16Mhz at90usb 和 16Mhz atmega2560 上的测试相匹配）。

| avr              | ticks |
| ---------------- | ----- |
| 1 stepper        | 102   |
| 3 stepper        | 486   |

### Arduino Due 步长率基准测试

以下配置序列用于 Due：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PB27 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB26 dir_pin=PC30 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA21 dir_pin=PC30 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| sam3x8e              | ticks |
| -------------------- | ----- |
| 1 stepper            | 66    |
| 3 stepper            | 257   |

### Duet Maestro 步长率基准测试

以下配置序列用于 Duet Maestro：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC26 dir_pin=PC18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PC26 dir_pin=PA8 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PC26 dir_pin=PB4 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| sam4s8c              | ticks |
| -------------------- | ----- |
| 1 stepper            | 71    |
| 3 stepper            | 260   |

### Duet Wifi 步长率基准测试

以下配置序列用于 Duet Wifi：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PD6 dir_pin=PD11 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PD7 dir_pin=PD12 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PD8 dir_pin=PD13 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `gcc version 10.3.1 20210621 (release) (GNU Arm Embedded Toolchain 10.3-2021.07)`。

| sam4e8e          | ticks |
| ---------------- | ----- |
| 1 stepper        | 48    |
| 3 stepper        | 215   |

### Beaglebone PRU 步长率基准测试

以下配置序列用于 PRU：
```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio0_23 dir_pin=gpio1_12 invert_step=0 step_pulse_ticks=20
config_stepper oid=1 step_pin=gpio1_15 dir_pin=gpio0_26 invert_step=0 step_pulse_ticks=20
config_stepper oid=2 step_pin=gpio0_22 dir_pin=gpio2_1 invert_step=0 step_pulse_ticks=20
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `pru-gcc (GCC) 8.0.0 20170530 (experimental)`。

| pru              | ticks |
| ---------------- | ----- |
| 1 stepper        | 231   |
| 3 stepper        | 847   |

### STM32F042 步长率基准测试

以下配置序列用于 STM32F042：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA1 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PA3 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB8 dir_pin=PA2 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32f042        | ticks |
| ---------------- | ----- |
| 1 stepper        | 59    |
| 3 stepper        | 249   |

### STM32F103 步长率基准测试

以下配置序列用于 STM32F103：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC13 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB3 dir_pin=PB6 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA4 dir_pin=PB7 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32f103            | ticks |
| -------------------- | ----- |
| 1 stepper            | 61    |
| 3 stepper            | 264   |

### STM32F4 步长率基准测试

以下配置序列用于 STM32F4：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA5 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。STM32F407 结果通过在 STM32F446 上运行 STM32F407 二进制文件获得（因此使用 168Mhz 时钟）。

| stm32f446            | ticks |
| -------------------- | ----- |
| 1 stepper            | 46    |
| 3 stepper            | 205   |

| stm32f407            | ticks |
| -------------------- | ----- |
| 1 stepper            | 46    |
| 3 stepper            | 205   |

### STM32H7 步长率基准测试

以下配置序列用于 STM32H723：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA13 dir_pin=PB5 invert_step=-1 step_pulse_ticks=52
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=52
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=52
finalize_config crc=0
```

测试最后在提交 `554ae78d` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`。

| stm32h723            | ticks |
| -------------------- | ----- |
| 1 stepper            | 70    |
| 3 stepper            | 181   |

### STM32G0B1 步长率基准测试

以下配置序列用于 STM32G0B1：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PB13 dir_pin=PB12 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB10 dir_pin=PB2 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PB0 dir_pin=PC5 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `247cd753` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。

| stm32g0b1        | ticks |
| ---------------- | ----- |
| 1 stepper        | 58    |
| 3 stepper        | 243   |

### STM32G4 步长率基准测试

以下配置序列用于 STM32G431：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA0 dir_pin=PB5 invert_step=-1 step_pulse_ticks=17
config_stepper oid=1 step_pin=PB2 dir_pin=PB6 invert_step=-1 step_pulse_ticks=17
config_stepper oid=2 step_pin=PB3 dir_pin=PB7 invert_step=-1 step_pulse_ticks=17
finalize_config crc=0
```

测试最后在提交 `cfa48fe3` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`。

| stm32g431        | ticks |
| ---------------- | ----- |
| 1 stepper        | 47    |
| 3 stepper        | 208   |

### LPC176x 步长率基准测试

以下配置序列用于 LPC176x：
```
allocate_oids count=3
config_stepper oid=0 step_pin=P1.20 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=P1.21 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=P1.23 dir_pin=P1.18 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`。120Mhz LPC1769 结果通过超频 LPC1768 至 120Mhz 获得。

| lpc1768              | ticks |
| -------------------- | ----- |
| 1 stepper            | 52    |
| 3 stepper            | 222   |

| lpc1769              | ticks |
| -------------------- | ----- |
| 1 stepper            | 51    |
| 3 stepper            | 222   |

### SAMD21 步长率基准测试

以下配置序列用于 SAMD21：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA27 dir_pin=PA20 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PB3 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA17 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`，在 SAMD21G18 微控制器上进行。

| samd21               | ticks |
| -------------------- | ----- |
| 1 stepper            | 70    |
| 3 stepper            | 306   |

### SAMD51 步长率基准测试

以下配置序列用于 SAMD51：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PA22 dir_pin=PA20 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PA22 dir_pin=PA21 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PA22 dir_pin=PA19 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 10.2.0-4.fc34) 10.2.0`，在 SAMD51J19A 微控制器上进行。

| samd51               | ticks |
| -------------------- | ----- |
| 1 stepper            | 39    |
| 3 stepper            | 191   |
| 1 stepper (200Mhz)   | 39    |
| 3 stepper (200Mhz)   | 181   |

### SAME70 步长率基准测试

以下配置序列用于 SAME70：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PC18 dir_pin=PB5 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PC16 dir_pin=PD10 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PC28 dir_pin=PA4 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `34e9ea55` 上运行，gcc 版本 `arm-none-eabi-gcc (NixOS 10.3-2021.10) 10.3.1`，在 SAME70Q20B 微控制器上进行。

| same70               | ticks |
| -------------------- | ----- |
| 1 stepper            | 45    |
| 3 stepper            | 190   |

### AR100 步长率基准测试 ###

以下配置序列用于 AR100 CPU（Allwinner A64）：
```
allocate_oids count=3
config_stepper oid=0 step_pin=PL10 dir_pin=PE14 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=PL11 dir_pin=PE15 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=PL12 dir_pin=PE16 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0

```

测试最后在提交 `b7978d37` 上运行，gcc 版本 `or1k-linux-musl-gcc (GCC) 9.2.0`，在 Allwinner A64-H 微控制器上进行。

| AR100 R_PIO          | ticks |
| -------------------- | ----- |
| 1 stepper            | 85    |
| 3 stepper            | 359   |

### RPxxxx 步长率基准测试

以下配置序列用于 RP2040 和 RP2350：

```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio25 dir_pin=gpio3 invert_step=-1 step_pulse_ticks=0
config_stepper oid=1 step_pin=gpio26 dir_pin=gpio4 invert_step=-1 step_pulse_ticks=0
config_stepper oid=2 step_pin=gpio27 dir_pin=gpio5 invert_step=-1 step_pulse_ticks=0
finalize_config crc=0
```

测试最后在提交 `14c105b8` 上运行，gcc 版本 `arm-none-eabi-gcc (Fedora 14.1.0-1.fc40) 14.1.0`，在 Raspberry Pi Pico 和 Pico 2 板上进行。

| rp2040 (*)           | ticks |
| -------------------- | ----- |
| 1 stepper            | 3     |
| 3 stepper            | 14    |

| rp2350               | ticks |
| -------------------- | ----- |
| 1 stepper            | 36    |
| 3 stepper            | 169   |

(*) 请注意，报告的 rp2040 ticks 相对于 12Mhz 调度计时器，不对应于其 200Mhz 内部 ARM 处理速率。预期 5 个调度 ticks 对应约 42 ARM 核心周期，14 个调度 ticks 对应约 225 ARM 核心周期。

### Linux MCU 步长率基准测试

以下配置序列用于 Raspberry Pi：
```
allocate_oids count=3
config_stepper oid=0 step_pin=gpio2 dir_pin=gpio3 invert_step=0 step_pulse_ticks=5
config_stepper oid=1 step_pin=gpio4 dir_pin=gpio5 invert_step=0 step_pulse_ticks=5
config_stepper oid=2 step_pin=gpio6 dir_pin=gpio17 invert_step=0 step_pulse_ticks=5
finalize_config crc=0
```

测试最后在提交 `59314d99` 上运行，gcc 版本 `gcc (Raspbian 8.3.0-6+rpi1) 8.3.0`，在 Raspberry Pi 3（修订版本 a02082）上进行。很难在这个基准测试中获得稳定的结果。

| Linux (RPi3)         | ticks |
| -------------------- | ----- |
| 1 stepper            | 160   |
| 3 stepper            | 380   |

## 命令分派基准测试

命令分派基准测试测试微控制器可以处理多少"虚拟"命令。它主要是硬件通信机制的测试。测试使用 console.py 工具进行（在 [Debugging.md](Debugging.md) 中描述）。以下内容被切割并粘贴到 console.py 终端窗口中：
```
DELAY {clock + 2*freq} get_uptime
FLOOD 100000 0.0 debug_nop
get_uptime
```

当测试完成时，确定两个"uptime"响应消息中报告的时钟之间的差异。总命令数每秒然后是 `100000 * mcu_frequency / clock_diff`。

请注意，此测试可能使 Raspberry Pi 的 USB/CPU 容量饱和。如果在 Raspberry Pi、Beaglebone 或类似主机计算机上运行，则增加延迟（例如，`DELAY {clock + 20*freq} get_uptime`）。在适用的情况下，以下基准测试是使用 console.py 在桌面级机器上运行的，设备通过高速集线器连接。

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

可以使用"批处理"模式处理机制在主机软件上运行计时测试（在 [Debugging.md](Debugging.md) 中描述）。这通常是通过选择大型复杂 G-Code 文件并计时主机软件处理它需要多长时间来完成的。例如：
```
time ~/klippy-env/bin/python ./klippy/klippy.py config/example-cartesian.cfg -i something_complex.gcode -o /dev/null -d out/klipper.dict