# MCU 命令

本文档提供了从 Kalico"主机"软件发送并由 Kalico 微控制器软件处理的底层微控制器命令信息。本文档不是这些命令的权威参考，也不是所有可用命令的完整列表。

本文档可能对有兴趣了解底层微控制器命令的开发者有用。

有关命令格式及其传输的更多信息，请参见 [protocol](Protocol.md) 文档。这里的命令使用其"printf"风格的语法描述 - 对于不熟悉该格式的人，只需注意看到 '%...' 序列时应将其替换为实际整数。例如，包含 "count=%c" 的描述可以替换为文本 "count=10"。请注意，被视为"枚举"的参数（参见上述协议文档）接受字符串值，该值会自动转换为微控制器的整数值。这对于名为"pin"（或以 "_pin" 为后缀）的参数很常见。

## 启动命令

可能需要采取某些一次性操作来配置微控制器及其外围设备。本节列出了用于此目的的常见命令。与大多数微控制器命令不同，这些命令在收到后立即运行，不需要任何特定设置。

常见启动命令：

* `set_digital_out pin=%u value=%c` : 此命令立即将给定引脚配置为数字输出 GPIO 并将其设置为低电平（value=0）或高电平（value=1）。此命令可用于配置 LED 的初始值以及配置步进电机驱动器微步进引脚的初始值。

* `set_pwm_out pin=%u cycle_ticks=%u value=%hu` : 此命令将立即将给定引脚配置为使用基于硬件的脉冲宽度调制（PWM），并使用给定的 cycle_ticks 数。"cycle_ticks"是每个通电和断电周期应持续的 MCU 时钟周期数。cycle_ticks 值为 1 可用于请求最快的可能周期时间。"value"参数在 0 到 255 之间，0 表示完全关闭状态，255 表示完全开启状态。此命令可用于启用 CPU 和喷嘴冷却风扇。

## 底层微控制器配置

微控制器中的大多数命令需要初始设置才能成功调用。本节概述了配置过程。本节和以下节可能只对有兴趣了解 Kalico 内部细节的开发者有用。

当主机首次连接到微控制器时，它总是从获取数据字典开始（有关更多信息，请参见 [protocol](Protocol.md)）。获取数据字典后，主机将检查微控制器是否处于"已配置"状态，如果不是则对其进行配置。配置涉及以下阶段：

* `get_config` : 主机首先检查微控制器是否已经配置。微控制器通过"config"响应消息响应该命令。微控制器软件在上电时始终以未配置状态启动。它保持在此状态直到主机完成配置过程（通过发出 finalize_config 命令）。如果微控制器已经在上一个会话中配置（并且配置了所需的设置），则主机不需要进一步操作，配置过程成功结束。

* `allocate_oids count=%c` : 发出此命令是为了通知微控制器主机所需的最大对象 ID（oid）数量。此命令只能有效发出一次。oid 是分配给每个步进电机、每个限位开关和每个可调度 GPIO 引脚的整数标识符。主机预先确定它将需要多少个 oid 来操作硬件，并将其传递给微控制器，以便分配足够的内存来存储从 oid 到内部对象的映射。

* `config_XXX oid=%c ...` : 按照惯例，任何以 "config_" 前缀开头的命令都会创建一个新的微控制器对象并分配给定的 oid。例如，config_digital_out 命令将指定的引脚配置为数字输出 GPIO 并创建一个内部对象，主机可以使用该对象来调度对给定 GPIO 的更改。传递给 config 命令的 oid 参数由主机选择，必须在零和 allocate_oids 命令中提供的最大计数之间。config 命令只能在微控制器未处于已配置状态时运行（即，在主机发送 finalize_config 之前），并且在 allocate_oids 命令发送之后。

* `finalize_config crc=%u` : finalize_config 命令将微控制器从未配置状态转换为已配置状态。传递给微控制器的 crc 参数被存储并在"config"响应消息中提供回主机。按照惯例，主机获取其将请求的配置的 32 位 CRC，并在后续通信会话开始时检查微控制器中存储的 CRC 是否与其所需的 CRC 完全匹配。如果不匹配，则主机知道微控制器未配置为主机所需的状态。

### 常见微控制器对象

本节列出了一些常用的 config 命令。

* `config_digital_out oid=%c pin=%u value=%c default_value=%c max_duration=%u` : 此命令为给定的 GPIO 'pin' 创建一个内部微控制器对象。该引脚将配置为数字输出模式并设置为由 'value' 指定的初始值（0 为低电平，1 为高电平）。创建 digital_out 对象允许主机在指定时间调度对给定引脚的 GPIO 更新（请参见下面描述的 queue_digital_out 命令）。如果微控制器软件进入关闭模式，则所有配置的 digital_out 对象将设置为 'default_value'。'max_duration' 参数用于实现安全检查 - 如果为非零，则它是主机可以在没有进一步更新的情况下将给定 GPIO 设置为非默认值的最大时钟周期数。例如，如果 default_value 为零且 max_duration 为 16000，则如果主机将 gpio 设置为 1，则它必须在 16000 个时钟周期内安排对 gpio 引脚的另一次更新（设置为零或 1）。此安全功能可用于加热器引脚，以确保主机不会启用加热器然后离线。

* `config_pwm_out oid=%c pin=%u cycle_ticks=%u value=%hu default_value=%hu max_duration=%u` : 此命令为硬件 PWM 引脚创建一个内部对象，主机可以为其调度更新。其用法类似于 config_digital_out - 有关参数描述，请参见 'set_pwm_out' 和 'config_digital_out' 命令的描述。

* `config_analog_in oid=%c pin=%u` : 此命令用于将引脚配置为模拟输入采样模式。配置后，可以使用 query_analog_in 命令（见下文）定期对该引脚进行采样。

* `config_stepper oid=%c step_pin=%c dir_pin=%c invert_step=%c step_pulse_ticks=%u` : 此命令创建一个内部步进电机对象。'step_pin' 和 'dir_pin' 参数分别指定步进和方向引脚；此命令将它们配置为数字输出模式。'invert_step' 参数指定步进发生在上升沿（invert_step=0）还是下降沿（invert_step=1）。'step_pulse_ticks' 参数指定步进脉冲的最小持续时间。如果 MCU 导出常量 'STEPPER_BOTH_EDGE=1'，则设置 step_pulse_ticks=0 和 invert_step=-1 将设置为在步进引脚的上升沿和下降沿都进行步进。

* `config_endstop oid=%c pin=%c pull_up=%c stepper_count=%c` : 此命令创建一个内部"限位开关"对象。它用于指定限位开关引脚并启用"归位"操作（请参见下面的 endstop_home 命令）。该命令将指定的引脚配置为数字输入模式。'pull_up' 参数决定是否启用硬件为该引脚提供的上拉电阻（如果有）。'stepper_count' 参数指定此限位开关在归位操作期间可能需要停止的最大步进电机数量（请参见下面的 endstop_home）。

* `config_spi oid=%c bus=%u pin=%u mode=%u rate=%u shutdown_msg=%*s` : 此命令创建一个内部 SPI 对象。它与 spi_transfer 和 spi_send 命令一起使用（见下文）。"bus" 标识要使用的 SPI 总线（如果微控制器有多个可用的 SPI 总线）。"pin" 指定设备的片选（CS）引脚。"mode" 是 SPI 模式（应在 0 到 3 之间）。"rate" 参数指定 SPI 总线速率（以每秒周期数为单位）。最后，"shutdown_msg" 是如果微控制器进入关闭状态时发送给给定设备的 SPI 命令。

* `config_spi_without_cs oid=%c bus=%u mode=%u rate=%u shutdown_msg=%*s` : 此命令类似于 config_spi，但没有 CS 引脚定义。它对于没有片选线的 SPI 设备很有用。

## 常见命令

本节列出了一些常用的运行时命令。它可能只对希望深入了解 Kalico 的开发者有用。

* `set_digital_out_pwm_cycle oid=%c cycle_ticks=%u` : 此命令将数字输出引脚（由 config_digital_out 创建）配置为使用"软件 PWM"。'cycle_ticks' 是 PWM 周期的时钟周期数。由于输出切换在微控制器软件中实现，建议 'cycle_ticks' 对应 10ms 或更长时间。

* `queue_digital_out oid=%c clock=%u on_ticks=%u` : 此命令将在给定的时钟时间调度对数字输出 GPIO 引脚的更改。要使用此命令，必须在微控制器配置期间发出具有相同 'oid' 参数的 'config_digital_out' 命令。如果已调用 'set_digital_out_pwm_cycle'，则 'on_ticks' 是 PWM 周期的开启持续时间（以时钟周期为单位）。否则，'on_ticks' 应为 0（低电压）或 1（高电压）。

* `queue_pwm_out oid=%c clock=%u value=%hu` : 调度对硬件 PWM 输出引脚的更改。有关更多信息，请参见 'queue_digital_out' 和 'config_pwm_out' 命令。

* `query_analog_in oid=%c clock=%u sample_ticks=%u sample_count=%c rest_ticks=%u min_value=%hu max_value=%hu` : 此命令设置模拟输入采样的定期调度。要使用此命令，必须在微控制器配置期间发出具有相同 'oid' 参数的 'config_analog_in' 命令。采样将从 'clock' 时间开始，每 'rest_ticks' 个时钟周期报告一次获取的值，将过采样 'sample_count' 次，并在过采样之间暂停 'sample_ticks' 个时钟周期。'min_value' 和 'max_value' 参数实现安全功能 - 微控制器软件将验证采样值（在任何过采样之后）始终在提供的范围内。这旨在用于连接到控制加热器的热敏电阻的引脚 - 可用于检查加热器是否在温度范围内。

* `get_clock` : 此命令使微控制器生成"clock"响应消息。主机每秒发送此命令一次，以获取微控制器时钟值并估算主机和微控制器时钟之间的漂移。它使主机能够准确估算微控制器时钟。

### 步进电机命令

* `queue_step oid=%c interval=%u count=%hu add=%hi` : 此命令为给定的步进电机调度 'count' 个步进，每个步进之间有 'interval' 个时钟周期。第一个步进将距离给定步进电机的上一个调度步进 'interval' 个时钟周期。如果 'add' 非零，则每个步进后将调整 'interval' 量 'add'。此命令将给定的 interval/count/add 序列附加到每步进电机队列中。在正常操作期间，可能有数百个此类序列排队。新序列附加到队列末尾，当每个序列完成其 'count' 个步进时，它从队列前面弹出。此系统允许微控制器排队可能数十万个步进 - 所有步进都具有可靠且可预测的调度时间。

* `set_next_step_dir oid=%c dir=%c` : 此命令指定下一个 queue_step 命令将使用的 dir_pin 的值。

* `reset_step_clock oid=%c clock=%u` : 通常，步进时间相对于给定步进电机的上一个步进。此命令重置时钟，使下一步进相对于提供的 'clock' 时间。主机通常只在打印开始时发送此命令。

* `stepper_get_position oid=%c` : 此命令使微控制器生成包含步进电机当前位置的"stepper_position"响应消息。位置是使用 dir=1 生成的总步进数减去使用 dir=0 生成的总步进数。

* `endstop_home oid=%c clock=%u sample_ticks=%u sample_count=%c rest_ticks=%u pin_value=%c` : 此命令用于步进电机"归位"操作期间。要使用此命令，必须在微控制器配置期间发出具有相同 'oid' 参数的 'config_endstop' 命令。调用此命令时，微控制器将每 'rest_ticks' 个时钟周期采样一次限位开关引脚，并检查其值是否等于 'pin_value'。如果值匹配（并且它继续匹配分布在 'sample_ticks' 间隔中的 'sample_count' 个额外采样），则关联步进电机的移动队列将被清除，步进电机将立即停止。主机使用此命令实现归位 - 主机指示限位开关采样限位开关触发，然后发出一系列 queue_step 命令将步进电机移向限位开关。一旦步进电机碰到限位开关，触发器将被检测到，移动停止，主机得到通知。

### 移动队列

每个 queue_step 命令使用微控制器"移动队列"中的一个条目。此队列在接收到"finalize_config"命令时分配，并在"config"响应消息中报告可用队列条目数量。

主机有责任确保在发送 queue_step 命令之前队列中有可用空间。主机通过计算每个 queue_step 命令完成的时间并相应地调度新的 queue_step 命令来实现此目的。

### SPI 命令

* `spi_transfer oid=%c data=%*s` : 此命令使微控制器将 'data' 发送到由 'oid' 指定的 SPI 设备，并生成包含传输期间返回数据的 "spi_transfer_response" 响应消息。

* `spi_send oid=%c data=%*s` : 此命令类似于 "spi_transfer"，但不生成 "spi_transfer_response" 消息。
