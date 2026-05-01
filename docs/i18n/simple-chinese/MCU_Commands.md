# MCU 命令

本文档提供有关从 Kalico"主机"软件发送并由 Kalico 微控制器（MCU - Micro-Controller Unit）软件处理的低级微控制器命令的信息。本文档不是这些命令的权威参考，也不是所有可用命令的排他性列表。

本文档可能对有兴趣理解低级微控制器命令的开发人员很有用。

有关命令格式及其传输的详细信息，请参见[协议](Protocol.md)文档。此处的命令使用其"printf"样式语法进行描述——对于不熟悉该格式的人，只需注意在看到"%..."序列时应将其替换为实际整数。例如，具有"count=%c"的描述可以替换为文本"count=10"。请注意，被认为是"枚举"的参数（请参阅上面的协议文档）取一个字符串值，它自动转换为微控制器的整数值。这对于名为"pin"的参数或具有"_pin"后缀的参数很常见。

## 启动命令

可能需要采取某些一次性操作来配置微控制器及其外设。本节列出了可用于该目的的常见命令。与大多数微控制器命令不同，这些命令在接收到时立即运行，并且它们不需要任何特定的设置。

常见启动命令：

* `set_digital_out pin=%u value=%c` ：此命令立即将给定引脚配置为数字输出 GPIO（通用输入/输出），并将其设置为低电平（value=0）或高电平（value=1）。此命令可能对配置 LED 的初始值以及配置步进驱动程序微步进引脚的初始值很有用。

* `set_pwm_out pin=%u cycle_ticks=%u value=%hu` ：此命令将立即将给定引脚配置为使用硬件脉冲宽度调制（PWM - Pulse-Width-Modulation），具有给定的 cycle_ticks 数。"cycle_ticks"是每个通电和关闭周期应该持续的 MCU 时钟刻度数。cycle_ticks 值 1 可以用来请求最快可能的循环时间。"value"参数在 0 到 255 之间，0 表示完全关闭状态，255 表示完全开启状态。此命令可能对启用 CPU 和喷嘴冷却风扇很有用。

## 低级微控制器配置

大多数微控制器中的命令需要在能够成功调用之前进行初始设置。本节提供了配置过程的概览。本节和以下各节可能仅对有兴趣了解 Kalico 内部细节的开发人员感兴趣。

当主机首次连接到微控制器时，它总是首先获取数据字典（有关更多信息，请参见[协议](Protocol.md)）。获得数据字典后，主机将检查微控制器是否处于"已配置"状态，如果没有则对其进行配置。配置涉及以下阶段：

* `get_config` ：主机首先检查微控制器是否已配置。微控制器用"config"响应消息响应此命令。微控制器软件在上电时总是以未配置状态开始。它保持这种状态，直到主机完成配置过程（通过发出 finalize_config 命令）。如果微控制器已从上一个会话配置，并且已使用所需设置配置（如果微控制器已从上一个会话配置，并已配置所需的设置），则主机不需要采取进一步的操作，配置过程成功结束。

* `allocate_oids count=%c` ：发出此命令以通知微控制器主机需要的对象-id (oid) 的最大数量。只有效发出此命令一次。oid 是分配给每个步进电机、每个端点和每个可计划 gpio 引脚的整数标识符。主机提前确定它需要多少个 oid 来操作硬件，并将其传递给微控制器，以便它可以分配足够的内存来存储从 oid 到内部对象的映射。

* `config_XXX oid=%c ...` ：按照惯例，任何以"config_"前缀开头的命令都会创建一个新的微控制器对象并为其分配给定的 oid。例如，config_digital_out 命令将配置指定的引脚作为数字输出 GPIO 并创建一个内部对象，主机可以使用它来计划对给定 GPIO 的更改。传递到配置命令中的 oid 参数由主机选择，必须在零和 allocate_oids 命令中提供的最大计数之间。config 命令只能在微控制器不处于已配置状态时运行（即，在主机发送 finalize_config 之前）并且在 allocate_oids 命令已发送后运行。

* `finalize_config crc=%u` ：finalize_config 命令将微控制器从未配置状态转换为已配置状态。传递给微控制器的 crc 参数被存储并在"config"响应消息中返回给主机。按照惯例，主机采用它将请求的配置的 32 位 CRC，并在后续通信会话的开始时检查存储在微控制器中的 CRC 与其所需的 CRC 完全匹配。如果 CRC 不匹配，那么主机知道微控制器还没有以主机所需的状态配置。

### 常见的微控制器对象

本节列出了一些常用的配置命令。

* `config_digital_out oid=%c pin=%u value=%c default_value=%c max_duration=%u` ：此命令为给定的 GPIO 引脚创建一个内部微控制器对象。引脚将在数字输出模式下配置，并设置为由"value"指定的初始值（低电平为 0，高电平为 1）。创建 digital_out 对象允许主机在指定时间为给定引脚计划 GPIO 更新（参见下面描述的 queue_digital_out 命令）。如果微控制器软件进入关闭模式，则所有已配置的 digital_out 对象将设置为"default_value"。"max_duration"参数用于实现安全检查——如果它非零，则它是主机可以将给定 GPIO 设置为非默认值而不进行进一步更新的最大时钟刻度数。例如，如果 default_value 为零且 max_duration 为 16000，那么如果主机将 gpio 设置为 1 的值，那么它必须在 16000 个时钟刻度内计划对 gpio 引脚的另一个更新（为零或 1）。此安全功能可与加热器引脚配合使用，以确保主机不启用加热器然后离线。

* `config_pwm_out oid=%c pin=%u cycle_ticks=%u value=%hu default_value=%hu max_duration=%u` ：此命令为基于硬件 PWM（脉冲宽度调制）引脚创建一个内部对象，主机可以计划更新。它的用法类似于 config_digital_out——有关参数描述，请参见"set_pwm_out"和"config_digital_out"命令的说明。

* `config_analog_in oid=%c pin=%u` ：此命令用于在模拟输入采样模式下配置引脚。配置后，可以使用 query_analog_in 命令以定期间隔对引脚进行采样（参见下面）。

* `config_stepper oid=%c step_pin=%c dir_pin=%c invert_step=%c step_pulse_ticks=%u` ：此命令创建一个内部步进电机对象。"step_pin"和"dir_pin"参数分别指定步进和方向引脚；此命令将在数字输出模式下配置它们。"invert_step"参数指定步进是否在上升沿（invert_step=0）或下降沿（invert_step=1）发生。"step_pulse_ticks"参数指定步脉冲的最小持续时间。如果 mcu 导出常量"STEPPER_BOTH_EDGE=1"，则设置 step_pulse_ticks=0 和 invert_step=-1 将设置为在步进引脚的上升和下降沿上进行步进。

* `config_endstop oid=%c pin=%c pull_up=%c stepper_count=%c` ：此命令创建一个内部"endstop"（端点）对象。它用于指定端点引脚并启用"归位"操作（参见下面的 endstop_home 命令）。该命令将在数字输入模式下配置指定的引脚。"pull_up"参数确定是否为引脚启用硬件提供的上拉电阻（如果可用）。"stepper_count"参数指定在归位操作期间此端点可能需要停止的最大步进电机数（参见下面的 endstop_home）。

* `config_spi oid=%c bus=%u pin=%u mode=%u rate=%u shutdown_msg=%*s` ：此命令创建一个内部 SPI（串行外设接口）对象。它与 spi_transfer 和 spi_send 命令配合使用（参见下面）。"bus"标识要使用的 SPI 总线（如果微控制器有多个 SPI 总线可用）。"pin"指定设备的片选（CS - Chip Select）引脚。"mode"是 SPI 模式（应在 0 到 3 之间）。"rate"参数指定 SPI 总线速率（以每秒周期为单位）。最后，"shutdown_msg"是当微控制器进入关闭状态时发送到给定设备的 SPI 命令。

* `config_spi_without_cs oid=%c bus=%u mode=%u rate=%u shutdown_msg=%*s` ：此命令类似于 config_spi，但没有 CS 引脚定义。它对于没有片选线的 SPI 设备很有用。

## 常见命令

本节列出了一些常用的运行时命令。它可能仅对寻求深入了解 Kalico 的开发人员感兴趣。

* `set_digital_out_pwm_cycle oid=%c cycle_ticks=%u` ：此命令配置数字输出引脚（由 config_digital_out 创建）以使用"软件 PWM"。"cycle_ticks"是 PWM 周期的时钟刻度数。由于输出切换在微控制器软件中实现，建议"cycle_ticks"对应于 10ms 或更长时间。

* `queue_digital_out oid=%c clock=%u on_ticks=%u` ：此命令将在给定的时钟时间计划对数字输出 GPIO 引脚的更改。为了使用此命令，在微控制器配置期间必须已发出具有相同"oid"参数的"config_digital_out"命令。如果已调用"set_digital_out_pwm_cycle"，则"on_ticks"是 pwm 周期的打开持续时间（以时钟刻度为单位）。否则，"on_ticks"应为 0（对于低电压）或 1（对于高电压）。

* `queue_pwm_out oid=%c clock=%u value=%hu` ：计划对硬件 PWM 输出引脚的更改。有关更多信息，请参阅"queue_digital_out"和"config_pwm_out"命令。

* `query_analog_in oid=%c clock=%u sample_ticks=%u sample_count=%c rest_ticks=%u min_value=%hu max_value=%hu` ：此命令设置模拟输入样品的经常性计划。为了使用此命令，在微控制器配置期间必须已发出具有相同"oid"参数的"config_analog_in"命令。样品将从"clock"时间开始，它将每"rest_ticks"时钟刻度报告一次获得的值，它将过采样"sample_count"次数，并将在过采样样品之间暂停"sample_ticks"个时钟刻度。"min_value"和"max_value"参数实现安全功能——微控制器软件将验证采样值（在任何过采样后）始终在提供的范围内。这旨在与附加到控制加热器的热敏电阻的引脚配合使用——它可用于检查加热器是否在温度范围内。

* `get_clock` ：此命令导致微控制器生成"clock"响应消息。主机每秒发送一次此命令以获取微控制器时钟的值并估计主机和微控制器时钟之间的漂移。它使主机能够准确估计微控制器时钟。

### 步进电机命令

* `queue_step oid=%c interval=%u count=%hu add=%hi` ：此命令为给定的步进电机计划"count"个步数，每步之间具有"interval"个时钟刻度。第一步将在给定步进电机的最后一个计划步之后"interval"个时钟刻度。如果"add"非零，则在每个步之后将通过"add"量调整间隔。此命令将给定的间隔/计数/添加序列追加到每个步进电机队列。在正常操作期间，可能有数百个这些序列排队。新序列被追加到队列的末尾，当每个序列完成其"count"个步时，它从队列的前面弹出。这个系统允许微控制器排队数百个潜在的数千步——所有具有可靠且可预测的调度时间。

* `set_next_step_dir oid=%c dir=%c` ：此命令指定下一个 queue_step 命令将使用的 dir_pin 的值。

* `reset_step_clock oid=%c clock=%u` ：通常，步进时序相对于给定步进电机的最后一个步。此命令重置时钟，以便下一个步相对于提供的"clock"时间。主机通常仅在打印开始时发送此命令。

* `stepper_get_position oid=%c` ：此命令导致微控制器生成一个"stepper_position"响应消息，其中包含步进电机的当前位置。位置是使用 dir=1 生成的步数总数减去使用 dir=0 生成的步数总数。

* `endstop_home oid=%c clock=%u sample_ticks=%u sample_count=%c rest_ticks=%u pin_value=%c` ：此命令在步进电机"归位"操作期间使用。为了使用此命令，在微控制器配置期间必须已发出具有相同"oid"参数的"config_endstop"命令。当调用此命令时，微控制器将每"rest_ticks"个时钟刻度对端点引脚进行采样，并检查它是否具有等于"pin_value"的值。如果该值匹配（并且它继续匹配"sample_count"个额外样品，相隔"sample_ticks"），那么关联步进电机的运动队列将被清除，步进电机将立即停止。主机使用此命令实现归位——主机指示端点采样端点触发，然后它发出一系列 queue_step 命令以将步进电机移动到端点。一旦步进电机击中端点，触发器将被检测到，运动将停止，并且主机将被通知。

### 移动队列

每个 queue_step 命令在微控制器"移动队列"中利用一个条目。当它接收到"finalize_config"命令时，该队列被分配，并且它在"config"响应消息中报告可用队列条目的数量。

这是主机在发送 queue_step 命令之前确保队列中有可用空间的责任。主机通过计算每个 queue_step 命令何时完成并相应地计划新的 queue_step 命令来实现这一点。

### SPI 命令

* `spi_transfer oid=%c data=%*s` ：此命令导致微控制器向由"oid"指定的 spi 设备发送"data"，并生成具有在传输期间返回的数据的"spi_transfer_response"响应消息。

* `spi_send oid=%c data=%*s` ：此命令类似于"spi_transfer"，但不生成"spi_transfer_response"消息。