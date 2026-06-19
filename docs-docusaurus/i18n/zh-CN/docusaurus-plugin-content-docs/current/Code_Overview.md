# 代码概述

本文档描述了 Kalico 的整体代码布局和主要代码流程。

## 目录布局

**src/** 目录包含微控制器代码的 C 源代码。**src/atsam/**、**src/atsamd/**、**src/avr/**、**src/linux/**、**src/lpc176x/**、**src/pru/** 和 **src/stm32/** 目录包含特定于架构的微控制器代码。**src/simulator/** 包含允许在其他架构上进行测试编译的代码桩。**src/generic/** 目录包含可能在不同架构之间有用的辅助代码。构建安排使 "board/somefile.h" 的包含首先在当前架构目录中查找（例如，src/avr/somefile.h），然后在通用目录中查找（例如，src/generic/somefile.h）。

**klippy/** 目录包含主机软件。主机软件的大部分是用 Python 编写的，但是 **klippy/chelper/** 目录包含一些 C 代码辅助程序。**klippy/kinematics/** 目录包含机器人运动学代码。**klippy/extras/** 目录包含主机代码的可扩展"模块"。

**lib/** 目录包含构建某些目标所需的外部第三方库代码。

**config/** 目录包含示例打印机配置文件。

**scripts/** 目录包含用于编译微控制器代码的构建时脚本。

**test/** 目录包含自动化测试用例。

在编译期间，构建可能会创建 **out/** 目录。这包含临时构建时对象。构建的最终微控制器对象在 AVR 上是 **out/klipper.elf.hex**，在 ARM 上是 **out/klipper.bin**。

## 微控制器代码流程

微控制器代码的执行从特定于架构的代码开始（例如，**src/avr/main.c**），最终调用位于 **src/sched.c** 中的 sched_main()。sched_main() 代码首先运行所有用 DECL_INIT() 宏标记的函数。然后继续重复运行所有用 DECL_TASK() 宏标记的函数。

主要任务函数之一是位于 **src/command.c** 中的 command_dispatch()。此函数从板特定的输入/输出代码调用（例如，**src/avr/serial.c**、**src/generic/serial_irq.c**），并运行与输入流中找到的命令相关的命令函数。命令函数使用 DECL_COMMAND() 宏声明（有关更多信息，请参阅 [协议](Protocol.md) 文档）。

任务、初始化和命令函数始终在启用中断的情况下运行（但是，如果需要，它们可以临时禁用中断）。这些函数应避免长时间暂停、延迟或持续时间很长的工作。（这些"任务"函数中的长时间延迟会导致其他"任务"的调度抖动 - 超过 100us 的延迟可能会变得明显，超过 500us 的延迟可能导致命令重传，超过 100ms 的延迟可能导致看门狗重启。）这些函数通过调度定时器来调度特定时间的工作。

定时器函数通过调用 sched_add_timer()（位于 **src/sched.c** 中）来调度。调度器代码将安排在请求的时钟时间调用给定函数。定时器中断最初在特定于架构的中断处理程序中处理（例如，**src/avr/timer.c**），该处理程序调用位于 **src/sched.c** 中的 sched_timer_dispatch()。定时器中断导致调度定时器函数的执行。定时器函数始终在禁用中断的情况下运行。定时器函数应始终在几微秒内完成。在定时器事件完成时，函数可以选择重新调度自身。

在检测到错误的情况下，代码可以调用 shutdown()（一个调用位于 **src/sched.c** 中的 sched_shutdown() 的宏）。调用 shutdown() 会导致所有用 DECL_SHUTDOWN() 宏标记的函数运行。关闭函数始终在禁用中断的情况下运行。

微控制器的许多功能涉及使用通用输入/输出引脚 (GPIO)。为了将底层特定于架构的代码与高层任务代码抽象化，所有 GPIO 事件都在特定于架构的包装器中实现（例如，**src/avr/gpio.c**）。代码使用 gcc 的 "-flto -fwhole-program" 优化编译，该优化在跨编译单元内联函数方面表现出色，因此大多数这些微小的 gpio 函数都被内联到其调用者中，使用它们没有运行时成本。

## Klippy 代码概述

主机代码（Klippy）旨在运行在与微控制器配对的低成本计算机（如 Raspberry Pi）上。代码主要用 Python 编写，但它确实使用 CFFI 在 C 代码中实现某些功能。

初始执行从 **klippy/klippy.py** 开始。这读取命令行参数，打开打印机配置文件，实例化主打印机对象，并启动串行连接。G 代码命令的主要执行在 **klippy/gcode.py** 中的 process_commands() 方法中。此代码将 G 代码命令转换为打印机对象调用，这些调用通常将操作转换为在微控制器上执行的命令（如微控制器代码中通过 DECL_COMMAND 宏声明的那样）。

Klippy 主机代码中有四个线程。主线程处理传入的 gcode 命令。第二个线程（完全位于 **klippy/chelper/serialqueue.c** C 代码中）处理与串行端口的底层 IO。第三个线程用于在 Python 代码中处理来自微控制器的响应消息（请参阅 **klippy/serialhdl.py**）。第四个线程将调试消息写入日志（请参阅 **klippy/queuelogger.py**），以便其他线程永远不会被日志写入阻塞。

## 移动命令的代码流程

典型的打印机移动从 "G1" 命令发送到 Klippy 主机开始，当相应的步进脉冲在微控制器上产生时完成。本节概述了典型移动命令的代码流程。[运动学](Kinematics.md) 文档提供了有关移动机制的更多信息。

* 移动命令的处理从 gcode.py 开始。gcode.py 的目标是将 G 代码转换为内部调用。G1 命令将调用 klippy/extras/gcode_move.py 中的 cmd_G1()。gcode_move.py 代码处理原点更改（例如 G92）、相对与绝对位置更改（例如 G90）和单位更改（例如 F6000=100mm/s）。移动的代码路径为：`_process_data() -> _process_commands() -> cmd_G1()`。最终调用 ToolHead 类来执行实际请求：`cmd_G1() -> ToolHead.move()`

* ToolHead 类（在 toolhead.py 中）处理"前瞻"并跟踪打印操作的时间安排。移动的主要代码路径为：`ToolHead.move() -> LookAheadQueue.add_move() -> LookAheadQueue.flush() -> Move.set_junction() -> ToolHead._process_moves()`。
  * ToolHead.move() 使用移动参数（在笛卡尔空间中，单位为秒和毫米）创建 Move() 对象。
  * 运动学类有机会审查每个移动（`ToolHead.move() -> kin.check_move()`）。运动学类位于 klippy/kinematics/ 目录中。如果移动无效，check_move() 代码可能会引发错误。如果 check_move() 成功完成，则底层运动学必须能够处理该移动。
  * LookAheadQueue.add_move() 将移动对象放在"前瞻"队列上。
  * LookAheadQueue.flush() 确定每个移动的起始和结束速度。
  * Move.set_junction() 在移动上实现"梯形生成器"。"梯形生成器"将每个移动分为三个部分：恒定加速阶段，后跟恒定速度阶段，后跟恒定减速阶段。每个移动按此顺序包含这三个阶段，但某些阶段的持续时间可能为零。
  * 当调用 ToolHead._process_moves() 时，关于移动的一切都是已知的 - 其起始位置、结束位置、加速度、起始/巡航/结束速度以及加速/巡航/减速期间行进的距离。所有信息都存储在 Move() 类中，并在笛卡尔空间中以毫米和秒为单位。

* Kalico 使用 [迭代求解器](https://en.wikipedia.org/wiki/Root-finding_algorithm) 为每个步进器生成步进时间。为了提高效率，步进脉冲时间在 C 代码中生成。移动首先放在"梯形运动队列"上：`ToolHead._process_moves() -> trapq_append()`（在 klippy/chelper/trapq.c 中）。然后生成步进时间：`ToolHead._process_moves() -> ToolHead._advance_move_time() -> ToolHead._advance_flush_time() -> MCU_Stepper.generate_steps() -> itersolve_generate_steps() -> itersolve_gen_steps_range()`（在 klippy/chelper/itersolve.c 中）。迭代求解器的目标是在给定从时间计算步进器位置的函数的情况下，找到步进时间。这是通过反复"猜测"各种时间直到步进器位置公式返回步进器上所需下一步的位置来完成的。每次猜测产生的反馈用于改进未来的猜测，使过程快速收敛到所需时间。运动学步进器位置公式位于 klippy/chelper/ 目录中（例如，kin_cart.c、kin_corexy.c、kin_delta.c、kin_extruder.c）。

* 请注意，挤出机在其自己的运动学类中处理：`ToolHead._process_moves() -> PrinterExtruder.move()`。由于 Move() 类指定了精确的移动时间，并且步进脉冲以特定的时间发送到微控制器，因此挤出机类产生的步进移动将与头部移动同步，即使代码是分开的。

* 在迭代求解器计算步进时间后，将它们添加到数组中：`itersolve_gen_steps_range() -> stepcompress_append()`（在 klippy/chelper/stepcompress.c 中）。数组（struct stepcompress.queue）存储每个步进对应的微控制器时钟计数器时间。这里的"微控制器时钟计数器"值直接对应于微控制器的硬件计数器 - 它是相对于微控制器上次上电的时间。

* 下一个主要步骤是压缩步进：`stepcompress_flush() -> compress_bisect_add()`（在 klippy/chelper/stepcompress.c 中）。此代码生成并编码一系列微控制器 "queue_step" 命令，这些命令对应于上一阶段构建的步进器步进时间列表。这些 "queue_step" 命令然后被排队、优先化并发送到微控制器（通过 stepcompress.c:steppersync 和 serialqueue.c:serialqueue）。

* 微控制器上 queue_step 命令的处理从 src/command.c 开始，该代码解析命令并调用 `command_queue_step()`。command_queue_step() 代码（在 src/stepper.c 中）只是将每个 queue_step 命令的参数附加到每个步进器的队列中。在正常操作下，queue_step 命令在其第一个步骤时间之前至少 100ms 被解析和排队。最后，步进器事件的生成在 `stepper_event()` 中完成。它从硬件定时器中断在第一个步骤的预定时间调用。stepper_event() 代码生成步进脉冲，然后重新调度自身在给定 queue_step 参数的下一个步进脉冲时间运行。每个 queue_step 命令的参数是 "interval"、"count" 和 "add"。在高级别上，stepper_event() 运行以下内容，'count' 次：`do_step(); next_wake_time = last_wake_time + interval; interval += add;`

以上内容对于执行移动来说似乎很复杂。然而，唯一真正有趣的部分在 ToolHead 和运动学类中。正是代码的这一部分指定了移动及其时间安排。处理的其余部分主要是通信和管道。

## 添加主机模块

Klippy 主机代码具有动态模块加载功能。如果在打印机配置文件中找到名为 "[my_module]" 的配置部分，则软件将自动尝试加载 python 模块 klippy/extras/my_module.py。此模块系统是向 Kalico 添加新功能的首选方法。

添加新模块最简单的方法是使用现有模块作为参考 - 请参阅 **klippy/extras/servo.py** 作为示例。

以下内容也可能有用：
* 模块的执行从模块级 `load_config()` 函数开始（用于 [my_module] 形式的配置部分）或在 `load_config_prefix()` 中（用于 [my_module my_name] 形式的配置部分）。此函数传递一个 "config" 对象，它必须返回与给定配置部分关联的新 "printer object"。
* 在实例化新的打印机对象的过程中，config 对象可用于从给定配置部分读取参数。这是使用 `config.get()`、`config.getfloat()`、`config.getint()` 等方法完成的。确保在打印机对象构造期间从配置中读取所有值 - 如果用户在此阶段未读取的配置参数，则将假设它是配置中的拼写错误并引发错误。
* 使用 `config.get_printer()` 方法获取对主 "printer" 类的引用。此 "printer" 类存储所有已实例化的 "printer objects" 的引用。使用 `printer.lookup_object()` 方法查找对其他打印机对象的引用。几乎所有功能（甚至核心运动学模块）都封装在这些打印机对象之一中。但是，请注意，当新模块实例化时，并非所有其他打印机对象都将已实例化。"gcode" 和 "pins" 模块将始终可用，但对于其他模块，最好延迟查找。
* 如果代码需要在由其他打印机对象引发的"事件"期间调用，请使用 `printer.register_event_handler()` 方法注册事件处理程序。每个事件名称都是一个字符串，按照惯例，它是引发事件的主要源模块的名称以及正在发生的操作的简短名称（例如，"klippy:connect"）。传递给每个事件处理程序的参数特定于给定事件（异常处理和执行上下文也是如此）。两个常见的启动事件是：
  * klippy:connect - 此事件在所有打印机对象实例化后生成。它通常用于查找其他打印机对象、验证配置设置以及与打印机硬件执行初始"握手"。
  * klippy:ready - 此事件在所有 connect 处理程序成功完成后生成。它表示打印机正在转换为准备好处理正常操作的状态。不要在此回调中引发错误。
* 如果用户配置中存在错误，请确保在 `load_config()` 或 "connect event" 阶段引发它。使用 `raise config.error("my error")` 或 `raise printer.config_error("my error")` 来报告错误。
* 使用 "pins" 模块配置微控制器上的引脚。这通常通过类似 `printer.lookup_object("pins").setup_pin("pwm", config.get("my_pin"))` 的方式完成。返回的对象可以在运行时进行控制。
* 如果打印机对象定义了 `get_status()` 方法，则模块可以通过 [宏](Command_Templates.md) 和 [API Server](API_Server.md) 导出 [状态信息](Status_Reference.md)。`get_status()` 方法必须返回一个 Python 字典，其键为字符串，值为整数、浮点数、字符串、列表、字典、True、False 或 None。也可以使用元组（和命名元组）（通过 API Server 访问时它们显示为列表）。导出的列表和字典必须被视为"不可变" - 如果其内容发生变化，则必须从 `get_status()` 返回新对象，否则 API Server 将无法检测到这些更改。
* 如果模块需要访问系统时间或外部文件描述符，则使用 `printer.get_reactor()` 获取对全局 "event reactor" 类的访问。此反应器类允许安排定时器、等待文件描述符上的输入以及"休眠"主机代码。
* 不要使用全局变量。所有状态都应存储在 `load_config()` 函数返回的打印机对象中。这很重要，否则 RESTART 命令可能无法按预期执行。同样，出于类似原因，如果打开了任何外部文件（或套接字），请确保注册 "klippy:disconnect" 事件处理程序并从该回调中关闭它们。
* 避免访问其他打印机对象的内部成员变量（或调用以下划线开头的方法）。遵循此约定使管理未来的更改更容易。
* 建议在 Python 类的 Python 构造函数中为所有成员变量赋值。（因此避免利用 Python 动态创建新成员变量的能力。）
* 如果 Python 变量要存储浮点值，则建议始终使用浮点常量分配和操作该变量（永远不要使用整数常量）。例如，优先使用 `self.speed = 1.` 而不是 `self.speed = 1`，优先使用 `self.speed = 2. * x` 而不是 `self.speed = 2 * x`。一致使用浮点值可以避免 Python 类型转换中难以调试的异常情况。
* 如果提交模块以包含在 Kalico 主代码中，请确保在模块顶部放置版权声明。请参阅现有模块以获取首选格式。

## 添加固件模块

除了添加新的主机模块外，还可以添加新的固件模块，这些模块将被固件构建系统自动发现。这对于位于自己的仓库中的扩展特别有用。虽然主机模块按名称自动发现，但固件模块需要与源文件一起拥有 `Makefile` 和 `Kconfig` 文件。

Kalico 将包含 `src/extras` 内每个目录中的 `Makefile` 和 `Kconfig`。例如，为了创建一个名为 `my-module` 的新固件模块，请创建以下文件：

`src/extras/my-module/Kconfig`：
```
config WANT_NEW_THING
    bool "Include the new thing!"
```

`src/extras/my-module/Makefile`：
```
dirs-y += src/extras/my-module
src-$(CONFIG_WANT_NEW_THING) += extras/my-module/new-thing.c
```

`src/extras/my-module/new-thing.c`：
```
/* firmware source goes here */
```

特别注意 `Makefile` -- 目录（带 `src` 前缀）需要添加到 `dirs-y`（或 `dirs-$(CONFIG_WANT_NEW_THING)`），源文件需要显式添加到 `src-*`。

当用户调用 `menuconfig` 时，他们将有一个新的 "Include the new thing!" 选项，可以根据需要启用或禁用。完整的 `Kconfig` 语言可用于更复杂的配置。

`my-module` 目录也可以是位于 Kalico 源代码树外部的目录的符号链接。

## 添加新运动学

本节提供有关向 Kalico 添加其他类型打印机运动学支持的一些提示。此类活动需要对目标运动学的数学公式有出色的了解。它还需要软件开发技能 - 但应该只需要更新主机软件。

有用的步骤：
1. 首先研究 "[移动的代码流程](#code-flow-of-a-move-command)" 部分和 [运动学文档](Kinematics.md)。
2. 查看 klippy/kinematics/ 目录中现有的运动学类。运动学类的任务是将笛卡尔坐标中的移动转换为每个步进器上的运动。应该能够复制其中一个文件作为起点。
3. 如果尚不可用，请为每个步进器实现 C 步进器运动学位置函数（请参阅 klippy/chelper/ 中的 kin_cart.c、kin_corexy.c 和 kin_delta.c）。该函数应调用 `move_get_coord()` 将给定的移动时间（以秒为单位）转换为笛卡尔坐标（以毫米为单位），然后根据该笛卡尔坐标计算所需的步进器位置（以毫米为单位）。
4. 在新的运动学类中实现 `calc_position()` 方法。此方法根据每个步进器的位置计算工具头在笛卡尔坐标中的位置。它不需要高效，因为它通常只在归位和探测操作期间调用。
5. 其他方法。实现 `check_move()`、`get_status()`、`get_steppers()`、`home()`、`clear_homing_state()` 和 `set_position()` 方法。这些函数通常用于提供运动学特定的检查。但是，在开发开始时可以在此处使用样板代码。
6. 实现测试用例。创建一个包含一系列移动的 g-code 文件，可以测试给定运动学的重要情况。按照 [调试文档](Debugging.md) 将此 g-code 文件转换为微控制器命令。这对于演练边缘情况和检查回归很有用。

## 移植到新的微控制器

本节提供有关将 Kalico 的微控制器代码移植到新架构的一些提示。此类活动需要良好的嵌入式开发知识和对目标微控制器的动手访问。

有用的步骤：
1. 首先识别将在移植期间使用的任何第三方库。常见的示例包括 "CMSIS" 包装器和制造商 "HAL" 库。所有第三方代码需要与 GNU GPLv3 兼容。第三方代码应提交到 Kalico lib/ 目录。更新 lib/README 文件，提供有关库获取时间和地点的信息。最好将代码原封不动地复制到 Kalico 仓库中，但如果需要任何更改，则应在 lib/README 文件中明确列出这些更改。
2. 在 src/ 目录中创建新的架构子目录，并添加初始 Kconfig 和 Makefile 支持。使用现有架构作为指南。src/simulator 提供了最小起点的基本示例。
3. 第一个主要编码任务是启动与目标板的通信支持。这是新移植中最困难的步骤。一旦基本通信工作正常，其余步骤往往会变得容易得多。在初始开发期间通常使用 UART 类型的串行设备，因为这些类型的硬件设备通常更容易启用和控制。在此阶段，大量使用 src/generic/ 目录中的辅助代码（检查 src/simulator/Makefile 如何将通用 C 代码包含到构建中）。还需要在此阶段定义 timer_read_time()（返回当前系统时钟），但不需要完全支持定时器 irq 处理。
4. 熟悉 console.py 工具（如 [调试文档](Debugging.md) 中所述），并使用它验证与微控制器的连接。此工具将底层微控制器通信协议转换为人类可读的形式。
5. 添加来自硬件中断的定时器分发支持。请参阅 Kalico [commit 970831ee](https://github.com/KalicoCrew/kalico/commit/970831ee0d3b91897196e92270d98b2a3067427f) 作为为 LPC176x 架构完成的步骤 1-5 的示例。
6. 启动基本 GPIO 输入和输出支持。请参阅 Kalico [commit c78b9076](https://github.com/KalicoCrew/kalico/commit/c78b90767f19c9e8510c3155b89fb7ad64ca3c54) 作为示例。
7. 启动其他外围设备 - 例如，请参阅 Kalico commit [65613aed](https://github.com/KalicoCrew/kalico/commit/65613aeddfb9ef86905cb1dade9e773a02ef3c27)、[c812a40a](https://github.com/KalicoCrew/kalico/commit/c812a40a3782415e454b04bf7bd2158a6f0ec8b5) 和 [c381d03a](https://github.com/KalicoCrew/kalico/commit/c381d03aad5c3ee761169b7c7bced519cc14da29)。
8. 在 config/ 目录中创建示例 Kalico 配置文件。使用主 klippy.py 程序测试微控制器。
9. 考虑在 test/ 目录中添加构建测试用例。

其他编码提示：
1. 避免使用 "C bitfields" 访问 IO 寄存器；优先直接读取和写入 32 位、16 位或 8 位整数。C 语言规范没有明确指定编译器必须如何实现 C bitfields（例如，字节序和位布局），并且很难确定对 C bitfield 进行读取或写入时会发生什么 IO 操作。
2. 优先向 IO 寄存器写入显式值，而不是使用读-修改-写操作。也就是说，如果更新 IO 寄存器中的字段且其他字段具有已知值，则最好显式写入寄存器的完整内容。显式写入产生更小、更快且更易于调试的代码。

## 坐标系

在内部，Kalico 主要在相对于配置文件中指定的坐标系的笛卡尔坐标中跟踪工具头的位置。也就是说，大多数 Kalico 代码将永远不会经历坐标系的变化。如果用户发出更改原点的请求（例如 `G92` 命令），则通过将未来的命令转换为主坐标系来实现该效果。

但是，在某些情况下，获取工具头在其他坐标系中的位置是有用的，Kalico 提供了几个工具来方便这一点。可以通过运行 GET_POSITION 命令看到这一点。例如：

```
Send: GET_POSITION
Recv: // mcu: stepper_a:-2060 stepper_b:-1169 stepper_c:-1613
Recv: // stepper: stepper_a:457.254159 stepper_b:466.085669 stepper_c:465.382132
Recv: // kinematic: X:8.339144 Y:-3.131558 Z:233.347121
Recv: // toolhead: X:8.338078 Y:-3.123175 Z:233.347878 E:0.000000
Recv: // gcode: X:8.338078 Y:-3.123175 Z:233.347878 E:0.000000
Recv: // gcode base: X:0.000000 Y:0.000000 Z:0.000000 E:0.000000
Recv: // gcode homing: X:0.000000 Y:0.000000 Z:0.000000
```

"mcu" 位置（代码中的 `stepper.get_mcu_position()`）是微控制器自上次重置以来在正方向上发出的总步数减去在负方向上发出的步数。如果在发出查询时机器人正在运动，则报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。

"stepper" 位置（`stepper.get_commanded_position()`）是由运动学代码跟踪的给定步进器的位置。这通常对应于滑架沿其导轨的位置（以 mm 为单位），相对于配置文件中指定的 position_endstop。（某些运动学以弧度而不是毫米跟踪步进器位置。）如果在发出查询时机器人正在运动，则报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。可以使用 `toolhead.flush_step_generation()` 或 `toolhead.wait_moves()` 调用完全刷新前瞻和步进生成代码。

"kinematic" 位置（`kin.calc_position()`）是根据 "stepper" 位置得出的工具头笛卡尔位置，相对于配置文件中指定的坐标系。这可能与请求的笛卡尔位置不同，因为步进电机的粒度。如果在获取 "stepper" 位置时机器人正在运动，则报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。可以使用 `toolhead.flush_step_generation()` 或 `toolhead.wait_moves()` 调用完全刷新前瞻和步进生成代码。

"toolhead" 位置（`toolhead.get_position()`）是相对于配置文件中指定的坐标系的工具头最后请求的位置。如果在发出查询时机器人正在运动，则报告的值包括所有请求的移动（甚至包括等待发送到步进电机驱动器的缓冲区中的移动）。

"gcode" 位置是来自 `G1`（或 `G0`）命令的最后请求位置，相对于配置文件中指定的坐标系。如果 g 代码转换（例如，bed_mesh、bed_tilt、skew_correction）生效，这可能与 "toolhead" 位置不同。如果 g 代码原点已更改（例如，`G92`、`SET_GCODE_OFFSET`、`M221`），这可能与最后 `G1` 命令中指定的实际坐标不同。`M114` 命令（`gcode_move.get_status()['gcode_position']`）将报告相对于当前 g 代码坐标系的最后 g 代码位置。

"gcode base" 是在相对于配置文件中指定的坐标系的笛卡尔坐标中的 g 代码原点的位置。`G92`、`SET_GCODE_OFFSET` 和 `M221` 等命令会更改此值。

"gcode homing" 是在 `G28` 归位命令后使用的 g 代码原点位置（在相对于配置文件中指定的坐标系的笛卡尔坐标中）。`SET_GCODE_OFFSET` 命令可以更改此值。

## 时间

Kalico 操作的基础是处理时钟、时间和时间戳。Kalico 通过调度即将发生的事件来对打印机执行操作。例如，要打开风扇，代码可能会安排在 100ms 后更改 GPIO 引脚。代码很少尝试执行瞬时操作。因此，Kalico 内部的时间处理对于正确操作至关重要。

在 Kalico 主机软件中内部跟踪三种类型的时间：
* 系统时间。系统时间使用系统的单调时钟 - 它是存储为秒的浮点数，通常是相对于主机计算机上次启动的时间。系统时间在软件中的用途有限 - 它们主要用于与操作系统交互。在主机代码中，系统时间通常存储在名为 *eventtime* 或 *curtime* 的变量中。
* 打印时间。打印时间与主微控制器时钟（在 "[mcu]" 配置部分中定义的微控制器）同步。它是存储为秒的浮点数，相对于主 MCU 上次重新启动的时间。可以通过将打印时间乘以 MCU 的静态配置频率，将"打印时间"转换为主微控制器的硬件时钟。高级主机代码使用打印时间来计算几乎所有物理操作（例如，头部移动、加热器更改等）。在主机代码中，打印时间通常存储在名为 *print_time* 或 *move_time* 的变量中。
* MCU 时钟。这是每个微控制器上的硬件时钟计数器。它存储为整数，其更新速率相对于给定微控制器的频率。主机软件在传输到 MCU 之前将其内部时间转换为时钟。MCU 代码仅以时钟刻度跟踪时间。在主机代码中，时钟值被跟踪为 64 位整数，而 MCU 代码使用 32 位整数。在主机代码中，时钟通常存储在名称中包含 *clock* 或 *ticks* 的变量中。

不同时间格式之间的转换主要在 **klippy/clocksync.py** 代码中实现。

审查代码时需要注意的一些事项：
* 32 位和 64 位时钟：为了减少带宽并提高微控制器效率，微控制器上的时钟被跟踪为 32 位整数。在 MCU 代码中比较两个时钟时，必须始终使用 `timer_is_before()` 函数来确保正确处理整数回绕。主机软件通过附加从它收到的最后一个 MCU 时间戳的高位位将 32 位时钟转换为 64 位时钟 - 来自 MCU 的消息永远不会超过 2^31 个时钟刻度的未来或过去，因此此转换永远不会产生歧义。主机通过简单地截断高位位将 64 位时钟转换为 32 位时钟。为了确保此转换没有歧义，**klippy/chelper/serialqueue.c** 代码将缓冲消息，直到它们在其目标时间的 2^31 个时钟刻度内。
* 多个微控制器：主机软件支持在单个打印机上使用多个微控制器。在这种情况下，每个微控制器的 "MCU clock" 是单独跟踪的。clocksync.py 代码通过修改从"打印时间"到 "MCU clock" 的转换方式来处理微控制器之间的时钟漂移。在辅助 MCU 上，用于此转换的 MCU 频率会定期更新以考虑测量到的漂移。
