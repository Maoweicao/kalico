# 代码概览

本文档描述了 Kalico 的整体代码布局和主要代码流。

## 目录布局

**src/** 目录包含微控制器代码的 C 源代码。**src/atsam/**、**src/atsamd/**、**src/avr/**、**src/linux/**、**src/lpc176x/**、**src/pru/** 和 **src/stm32/** 目录包含特定于体系结构的微控制器代码。**src/simulator/** 包含代码存根，允许微控制器在其他体系结构上进行测试编译。**src/generic/** 目录包含可能在不同体系结构中有用的辅助代码。构建安排"board/somefile.h"的包含首先在当前体系结构目录中查找（例如，src/avr/somefile.h），然后在通用目录中查找（例如，src/generic/somefile.h）。

**klippy/** 目录包含主机软件。大部分主机软件使用 Python 编写，但 **klippy/chelper/** 目录包含一些 C 代码助手。**klippy/kinematics/** 目录包含机器人运动学代码。**klippy/extras/** 目录包含主机代码可扩展"模块"。

**lib/** 目录包含构建某些目标所需的外部第三方库代码。

**config/** 目录包含示例打印机配置文件。

**scripts/** 目录包含用于编译微控制器代码的构建时脚本。

**test/** 目录包含自动化测试用例。

在编译过程中，构建可能会创建一个 **out/** 目录。这包含临时构建时对象。构建的最终微控制器对象在 AVR 上为 **out/klipper.elf.hex**，在 ARM 上为 **out/klipper.bin**。

## 微控制器代码流

微控制器代码的执行从特定于体系结构的代码开始（例如，**src/avr/main.c**），最终调用位于 **src/sched.c** 中的 sched_main()。sched_main() 代码通过运行所有已用 DECL_INIT() 宏标记的函数开始。然后继续重复运行所有用 DECL_TASK() 宏标记的函数。

主要任务函数之一是位于 **src/command.c** 中的 command_dispatch()。这个函数从特定于板的输入/输出代码（例如，**src/avr/serial.c**、**src/generic/serial_irq.c**）中调用，并运行在输入流中找到的命令相关的命令函数。命令函数使用 DECL_COMMAND() 宏声明（有关更多信息，请参见[协议](Protocol.md)文档）。

任务、初始化和命令函数总是在启用中断的情况下运行（但它们可以根据需要临时禁用中断）。这些函数应该避免长暂停、延迟或耗时的工作。（这些"任务"函数中的长延迟导致其他"任务"的调度抖动——超过 100us 的延迟可能会变得明显，超过 500us 的延迟可能导致命令重新传输，超过 100ms 的延迟可能导致看门狗重启。）这些函数通过计划计时器来在特定时间计划工作。

计时器函数通过调用 sched_add_timer()（位于 **src/sched.c**）来计划。调度程序代码将安排在请求的时钟时间调用给定的函数。计时器中断最初在特定于体系结构的中断处理程序中处理（例如，**src/avr/timer.c**），它调用位于 **src/sched.c** 中的 sched_timer_dispatch()。计时器中断导致调度计时器函数的执行。计时器函数总是在中断被禁用的情况下运行。计时器函数应该总是在几微秒内完成。在计时器事件完成时，该函数可以选择重新计划自己。

如果检测到错误，代码可以调用 shutdown()（调用位于 **src/sched.c** 的 sched_shutdown() 的宏）。调用 shutdown() 导致所有用 DECL_SHUTDOWN() 宏标记的函数被运行。关闭函数总是在中断被禁用的情况下运行。

微控制器的大部分功能涉及使用通用输入/输出引脚（GPIO - General-Purpose Input/Output）。为了将低级特定于体系结构的代码从高级任务代码中抽象出来，所有 GPIO 事件都在特定于体系结构的包装器中实现（例如，**src/avr/gpio.c**）。代码使用 gcc 的"-flto -fwhole-program"优化进行编译，该优化在编译单元之间内联函数方面做得很好，因此大多数这些微小的 gpio 函数都被内联到它们的调用者中，并且没有运行时成本。

## Klippy 代码概览

主机代码（Klippy）旨在在与微控制器配对的低成本计算机（例如 Raspberry Pi）上运行。该代码主要用 Python 编写，但它确实使用 CFFI 在 C 代码中实现一些功能。

初始执行从 **klippy/klippy.py** 开始。这读取命令行参数、打开打印机配置文件、实例化主打印机对象并启动串行连接。G-code 命令的主要执行在 **klippy/gcode.py** 中的 process_commands() 方法中。这个代码将 G-code 命令转换为打印机对象调用，这经常将动作转换为要在微控制器上执行的命令（通过微控制器代码中的 DECL_COMMAND 宏声明）。

Klippy 主机代码中有四个线程。主线程处理传入的 gcode 命令。第二个线程（完全驻留在 **klippy/chelper/serialqueue.c** C 代码中）处理与串行端口的低级 IO。第三个线程用于处理 Python 代码中来自微控制器的响应消息（参见 **klippy/serialhdl.py**）。第四个线程将调试消息写入日志（参见 **klippy/queuelogger.py**），以便其他线程从不阻塞日志写入。

## 移动命令的代码流

当"G1"命令发送到 Klippy 主机时开始典型的打印机移动，当在微控制器上生成相应的步进脉冲时完成。本节概述了典型移动命令的代码流。[运动学](Kinematics.md)文档提供了有关移动机制的进一步信息。

* 移动命令的处理从 gcode.py 开始。gcode.py 的目标是将 G-code 转换为内部调用。G1 命令将调用 klippy/extras/gcode_move.py 中的 cmd_G1()。gcode_move.py 代码处理原点的变化（例如，G92）、相对与绝对位置的变化（例如，G90）和单位变化（例如，F6000=100mm/s）。移动的代码路径是：`_process_data() -> _process_commands() -> cmd_G1()`。最终调用 ToolHead 类来执行实际请求：`cmd_G1() -> ToolHead.move()`

* ToolHead 类（在 toolhead.py 中）处理"前瞻"并跟踪打印动作的时序。移动的主要代码路径是：`ToolHead.move() -> LookAheadQueue.add_move() -> LookAheadQueue.flush() -> Move.set_junction() -> ToolHead._process_moves()`。
  * ToolHead.move() 使用移动的参数创建 Move() 对象（在笛卡尔空间中，以及以秒和毫米为单位）。
  * 运动学类有机会审计每个移动（`ToolHead.move() -> kin.check_move()`）。运动学类位于 klippy/kinematics/ 目录中。check_move() 代码如果移动无效可能会引发错误。如果 check_move() 成功完成，则底层运动学必须能够处理移动。
  * LookAheadQueue.add_move() 将移动对象放在"前瞻"队列上。
  * LookAheadQueue.flush() 确定每个移动的起始和结束速度。
  * Move.set_junction() 在移动上实现"梯形发生器"。"梯形发生器"将每个移动分为三部分：恒加速阶段、后跟恒速阶段、后跟恒减速阶段。每个移动按此顺序包含这三个阶段，但某些阶段可能的持续时间为零。
  * 当 ToolHead._process_moves() 被调用时，关于移动的所有内容都是已知的——其起始位置、其结束位置、其加速度、其起始/巡航/结束速度以及在加速/巡航/减速期间行进的距离。所有信息都存储在 Move() 类中，并且以笛卡尔空间的单位（毫米和秒）形式存在。

* Kalico 使用[迭代求解器](https://en.wikipedia.org/wiki/Root-finding_algorithm)为每个步进电机生成步进时间。出于效率原因，步进脉冲时间在 C 代码中生成。移动首先被放在"梯形运动队列"上：`ToolHead._process_moves() -> trapq_append()`（在 klippy/chelper/trapq.c 中）。步进时间然后被生成：`ToolHead._process_moves() -> ToolHead._advance_move_time() -> ToolHead._advance_flush_time() -> MCU_Stepper.generate_steps() -> itersolve_generate_steps() -> itersolve_gen_steps_range()`（在 klippy/chelper/itersolve.c 中）。迭代求解器的目标是给定计算步进电机位置时间的函数来找到步进时间。这是通过重复"猜测"各种时间直到步进电机位置公式返回下一步在步进电机上的所需位置来完成的。从每个猜测产生的反馈用于改进未来的猜测，以便过程快速收敛到所需时间。运动学步进电机位置公式位于 klippy/chelper/ 目录中（例如，kin_cart.c、kin_corexy.c、kin_delta.c、kin_extruder.c）。

* 注意挤出机在其自己的运动学类中处理：`ToolHead._process_moves() -> PrinterExtruder.move()`。由于 Move() 类指定了精确的运动时间，并且步进脉冲以特定的时序发送到微控制器，由挤出机类生成的步进电机运动将与头部运动同步，尽管代码保持分离。

* 在迭代求解器计算出步进时间后，它们被添加到数组中：`itersolve_gen_steps_range() -> stepcompress_append()`（在 klippy/chelper/stepcompress.c 中）。该数组（struct stepcompress.queue）存储每个步的相应微控制器时钟计数器时间。这里"微控制器时钟计数器"值直接对应于微控制器的硬件计数器——它相对于微控制器最后一次通电时。

* 下一步主要是压缩步进：`stepcompress_flush() -> compress_bisect_add()`（在 klippy/chelper/stepcompress.c 中）。这个代码生成并编码一系列微控制器"queue_step"命令，对应于在前一阶段构建的步进时间列表。然后这些"queue_step"命令被排队、优先化并发送到微控制器（通过 stepcompress.c:steppersync 和 serialqueue.c:serialqueue）。

* 微控制器上 queue_step 命令的处理从 src/command.c 开始，它解析命令并调用 `command_queue_step()`。command_queue_step() 代码（在 src/stepper.c 中）只是将每个 queue_step 命令的参数追加到每个步进电机队列中。在正常操作下，queue_step 命令在其第一步时间之前至少 100ms 处被解析和排队。最后，步进电机事件的生成在 `stepper_event()` 中完成。它从硬件计时器中断在第一步的计划时间调用。stepper_event() 代码生成一个步脉冲，然后重新计划自己以在给定 queue_step 参数的下一步脉冲的时间运行。每个 queue_step 命令的参数是"interval"、"count"和"add"。在高层，stepper_event() 运行以下内容"count"次：`do_step(); next_wake_time = last_wake_time + interval; interval += add;`

上面可能看起来是执行移动的很多复杂性。但是，真正有趣的部分在于 ToolHead 和运动学类中。这部分代码指定运动及其时序。处理的其余部分主要只是通信和管道。

## 添加主机模块

Klippy 主机代码具有动态模块加载功能。如果在打印机配置文件中找到名为"[my_module]"的配置部分，软件将自动尝试加载 Python 模块 klippy/extras/my_module.py。这个模块系统是向 Kalico 添加新功能的首选方法。

添加新模块的最简单方法是使用现有模块作为参考——参见 **klippy/extras/servo.py** 作为示例。

以下可能也很有用：
* 模块的执行从模块级 `load_config()` 函数开始（对于形式为 [my_module] 的配置部分）或在 `load_config_prefix()`（对于形式为 [my_module my_name] 的配置部分）。这个函数被传递一个"config"对象，它必须返回一个新的"打印机对象"，与给定的配置部分相关联。
* 在实例化新打印机对象的过程中，config 对象可以用来从给定的配置部分读取参数。这是使用 `config.get()`、`config.getfloat()`、`config.getint()` 等方法完成的。确保在打印机对象的构造期间从配置中读取所有值——如果用户指定了在此阶段未读取的配置参数，那么它将被假定为配置中的打字错误并将引发错误。
* 使用 `config.get_printer()` 方法来获取对主"打印机"类的引用。这个"打印机"类存储了所有已实例化的"打印机对象"的引用。使用 `printer.lookup_object()` 方法来查找对其他打印机对象的引用。几乎所有功能（甚至核心运动学模块）都封装在这些打印机对象之一中。注意，当实例化新模块时，并非所有其他打印机对象都将被实例化。"gcode"和"pins"模块将始终可用，但对于其他模块最好延迟查找。
* 使用 `printer.register_event_handler()` 方法注册事件处理程序，如果代码需要在由其他打印机对象引发的"事件"期间被调用。每个事件名称都是一个字符串，按照约定，它是引发事件的主源模块的名称，加上正在发生的动作的简短名称（例如，"klippy:connect"）。传递给每个事件处理程序的参数是特定于给定事件的（事件处理和执行上下文也是如此）。两个常见的启动事件是：
  * klippy:connect - 此事件在所有打印机对象实例化后生成。它通常用于查找其他打印机对象、验证配置设置以及与打印机硬件执行初始"握手"。
  * klippy:ready - 此事件在所有连接处理程序成功完成后生成。它表示打印机正在转换到准备好处理正常操作的状态。不要在此回调中引发错误。
* 如果用户的配置中有错误，请确保在 `load_config()` 或"connect event"阶段引发它。使用 `raise config.error("my error")` 或 `raise printer.config_error("my error")` 来报告错误。
* 使用"pins"模块来配置微控制器上的引脚。这通常使用类似于 `printer.lookup_object("pins").setup_pin("pwm", config.get("my_pin"))` 的东西完成。返回的对象可以在运行时命令。
* 如果打印机对象定义了 `get_status()` 方法，那么模块可以通过[宏](Command_Templates.md)和[API 服务器](API_Server.md)导出[状态信息](Status_Reference.md)。`get_status()` 方法必须返回一个 Python 字典，其键是字符串，值是整数、浮点数、字符串、列表、字典、True、False 或 None。元组（和命名元组）也可以使用（当通过 API 服务器访问时这些显示为列表）。导出的列表和字典必须被视为"不可变的"——如果它们的内容改变，那么必须从 `get_status()` 返回一个新对象，否则 API 服务器将不会检测到这些变化。
* 如果模块需要访问系统计时或外部文件描述符，那么使用 `printer.get_reactor()` 来获取对全局"事件反应器"类的访问权。这个反应器类允许人们计划计时器、等待文件描述符上的输入，并"睡眠"主机代码。
* 不要使用全局变量。所有状态应该存储在从 `load_config()` 函数返回的打印机对象中。这很重要，因为否则 RESTART 命令可能不会按预期执行。同样，由于类似的原因，如果任何外部文件（或套接字）被打开，那么确保注册一个"klippy:disconnect"事件处理程序并从该回调中关闭它们。
* 避免访问其他打印机对象的内部成员变量（或调用以下划线开头的方法）。遵守这一惯例使得更容易管理未来的更改。
* 建议为 Python 类的 Python 构造函数中的所有成员变量分配值。（从而避免利用 Python 动态创建新成员变量的能力。）
* 如果一个 Python 变量要存储浮点值，建议始终用浮点常量分配和操作该变量（从不使用整数常量）。例如，更喜欢 `self.speed = 1.` 而不是 `self.speed = 1`，并更喜欢 `self.speed = 2. * x` 而不是 `self.speed = 2 * x`。一致地使用浮点值可以避免 Python 类型转换中难以调试的古怪现象。
* 如果提交模块以包含在主 Kalico 代码中，请确保在模块顶部放置版权声明。参见现有模块以了解首选格式。

## 添加固件模块

除了添加新的主机模块，还可以添加新的固件模块，这些模块将被固件构建系统自动发现。这对于存在于自己的存储库中的扩展特别有用。虽然主机模块按名称自动发现，但固件模块需要有一个 `Makefile` 和一个 `Kconfig` 文件以及它们的源文件。

Kalico 将包括 `src/extras` 内每个目录中的 `Makefile` 和 `Kconfig`。例如，为了创建一个称为 `my-module` 的新固件模块，创建以下文件：

`src/extras/my-module/Kconfig`:
```
config WANT_NEW_THING
    bool "Include the new thing!"
```

`src/extras/my-module/Makefile`:
```
dirs-y += src/extras/my-module
src-$(CONFIG_WANT_NEW_THING) += extras/my-module/new-thing.c
```

`src/extras/my-module/new-thing.c`:
```
/* firmware source goes here */
```

要特别注意 `Makefile` ——目录（带 `src` 前缀）需要添加到 `dirs-y`（或 `dirs-$(CONFIG_WANT_NEW_THING)`），源文件需要显式添加到 `src-*`。

当用户调用 `menuconfig` 时，他们会有一个新的"Include the new thing!"选项，他们可以根据需要启用或禁用。完整的 `Kconfig` 语言可用于更复杂的配置。

`my-module` 目录也可以是指向存在于 Kalico 源树之外的目录的符号链接。

## 添加新的运动学

本节提供了一些关于添加对 Kalico 支持额外打印机运动学类型的技巧。这种类型的活动需要对目标运动学的数学公式有极好的理解。它还需要软件开发技能——尽管人们应该只需要更新主机软件。

有用的步骤：
1. 首先研究 "[移动命令的代码流](#移动命令的代码流)" 部分和[运动学](Kinematics.md)文档。
2. 查看 klippy/kinematics/ 目录中现有的运动学类。运动学类的任务是将笛卡尔坐标中的移动转换为每个步进电机上的运动。应该能够复制这些文件之一作为起点。
3. 如果已经没有的话，实现每个步进电机的 C 步进运动学位置函数（参见 kin_cart.c、kin_corexy.c 和 kin_delta.c 在 klippy/chelper/）。该函数应该调用 `move_get_coord()` 以将给定的移动时间（以秒为单位）转换为笛卡尔坐标（以毫米为单位），然后从该笛卡尔坐标计算所需的步进电机位置（以毫米为单位）。
4. 在新的运动学类中实现 `calc_position()` 方法。这个方法从每个步进电机的位置计算笛卡尔坐标中工具头的位置。它不需要高效，因为它通常只在归位和探测操作期间调用。
5. 其他方法。实现 `check_move()`、`get_status()`、`get_steppers()`、`home()`、`clear_homing_state()` 和 `set_position()` 方法。这些函数通常用于提供运动学特定的检查。但是，在开发开始时，人们可以在此处使用样板代码。
6. 实现测试用例。创建一个 g-code 文件，其中包含一系列可以测试给定运动学重要情况的移动。按照[调试文档](Debugging.md)将这个 g-code 文件转换为微控制器命令。这对于行使边界情况和检查回归很有用。

## 移植到新的微控制器

本节提供了一些关于将 Kalico 的微控制器代码移植到新体系结构的技巧。这种类型的活动需要对嵌入式开发有很好的了解，并且需要对目标微控制器的动手访问。

有用的步骤：
1. 首先确定将在端口中使用的任何第三方库。常见的例子包括"CMSIS"包装器和制造商"HAL"库。所有第三方代码都需要是 GNU GPLv3 兼容的。第三方代码应提交到 Kalico lib/ 目录。使用关于在何处以及何时获得库的信息更新 lib/README 文件。最好将代码未更改地复制到 Kalico 存储库中，但如果需要任何更改，那么这些更改应该在 lib/README 文件中明确列出。
2. 在 src/ 目录中创建一个新的体系结构子目录并添加初始 Kconfig 和 Makefile 支持。使用现有的体系结构作为指南。src/simulator 提供了最小起点的基本示例。
3. 第一项主要编码任务是为目标板带来通信支持。这是新端口中最困难的步骤。一旦基本通信工作，其余步骤往往更容易得多。在初始开发期间通常使用 UART 类型串行设备，因为这些类型的硬件设备通常更容易启用和控制。在这个阶段，自由地使用来自 src/generic/ 目录的辅助代码（检查 src/simulator/Makefile 如何将通用 C 代码包含到构建中）。在这个阶段也有必要定义 timer_read_time()（它返回当前系统时钟），但不需要完全支持计时器 irq 处理。
4. 熟悉 console.py 工具（如[调试文档](Debugging.md)中所述）并验证与 micro-controller 的连接。这个工具将低级微控制器通信协议转换为人类可读的形式。
5. 添加从硬件中断进行计时器调度的支持。参见 Kalico [提交 970831ee](https://github.com/KalicoCrew/kalico/commit/970831ee0d3b91897196e92270d98b2a3067427f) 作为对 LPC176x 体系结构执行步骤 1-5 的示例。
6. 带来基本 GPIO 输入和输出支持。参见 Kalico [提交 c78b9076](https://github.com/KalicoCrew/kalico/commit/c78b90767f19c9e8510c3155b89fb7ad64ca3c54) 作为这个的示例。
7. 带来额外外围设备——例如参见 Kalico 提交 [65613aed](https://github.com/KalicoCrew/kalico/commit/65613aeddfb9ef86905cb1dade9e773a02ef3c27)、[c812a40a](https://github.com/KalicoCrew/kalico/commit/c812a40a3782415e454b04bf7bd2158a6f0ec8b5) 和 [c381d03a](https://github.com/KalicoCrew/kalico/commit/c381d03aad5c3ee761169b7c7bced519cc14da29)。
8. 在 config/ 目录中创建一个示例 Kalico 配置文件。使用主 klippy.py 程序测试微控制器。
9. 考虑在 test/ 目录中添加构建测试用例。

额外的编码提示：
1. 避免使用"C 位字段"来访问 IO 寄存器；更喜欢 32 位、16 位或 8 位整数的直接读写操作。C 语言规范没有清楚地指定编译器如何必须实现 C 位字段（例如，字节顺序和位布局），很难确定在 C 位字段读写上会发生什么 IO 操作。
2. 更喜欢向 IO 寄存器写入显式值，而不是使用读-修改-写操作。也就是说，如果更新 IO 寄存器中的字段，其中其他字段具有已知值，那么最好显式写入寄存器的全部内容。显式写入生成更小、更快、更容易调试的代码。

## 坐标系统

在内部，Kalico 主要以相对于配置文件中指定的坐标系的笛卡尔坐标跟踪工具头的位置。也就是说，大多数 Kalico 代码永远不会经历坐标系的变化。如果用户请求改变原点（例如，`G92` 命令），那么这个效果是通过将未来命令转换为主坐标系来获得的。

但是，在某些情况下获得某个其他坐标系中的工具头位置很有用，Kalico 具有几个工具来便于此。这可以通过运行 GET_POSITION 命令看到。例如：

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

"mcu"位置（代码中的 `stepper.get_mcu_position()`）是微控制器自上次重置以来以正方向发出的步数减去以负方向发出的步数。如果在发出查询时机器人在运动中，那么报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。

"stepper"位置（`stepper.get_commanded_position()`）是由运动学代码跟踪的给定步进电机的位置。这通常对应于相对于配置文件中指定的 position_endstop 的沿其导轨的托架的位置（以毫米为单位）。（某些运动学用弧度而不是毫米跟踪步进电机位置。）如果在发出查询时机器人在运动中，那么报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。可以使用 `toolhead.flush_step_generation()` 或 `toolhead.wait_moves()` 调用来完全刷新前瞻和步进生成代码。

"kinematic"位置（`kin.calc_position()`）是工具头的笛卡尔位置，由"stepper"位置衍生，相对于配置文件中指定的坐标系。由于步进电机的粒度，这可能与请求的笛卡尔位置不同。如果在获取"stepper"位置时机器人在运动中，那么报告的值包括微控制器上缓冲的移动，但不包括前瞻队列上的移动。可以使用 `toolhead.flush_step_generation()` 或 `toolhead.wait_moves()` 调用来完全刷新前瞻和步进生成代码。

"toolhead"位置（`toolhead.get_position()`）是相对于配置文件中指定的坐标系的笛卡尔坐标中最后请求的工具头位置。如果在发出查询时机器人在运动中，那么报告的值包括所有请求的移动（甚至那些在等待发出到步进电机驱动程序的缓冲区中的移动）。

"gcode"位置是来自 `G1`（或 `G0`）命令在相对于配置文件中指定的坐标系的笛卡尔坐标中的最后请求的位置。如果 g-code 变换（例如，bed_mesh、bed_tilt、skew_correction）生效，这可能与"toolhead"位置不同。如果 g-code 原点已更改（例如，`G92`、`SET_GCODE_OFFSET`、`M221`），这可能与最后一个 `G1` 命令中指定的实际坐标不同。`M114` 命令（`gcode_move.get_status()['gcode_position']`）将报告最后一个 g-code 位置相对于当前 g-code 坐标系。

"gcode base"是相对于配置文件中指定的坐标系的笛卡尔坐标中 g-code 原点的位置。`G92`、`SET_GCODE_OFFSET` 和 `M221` 等命令改变这个值。

"gcode homing"是在 `G28` 主页命令之后用于 g-code 原点的位置（在笛卡尔坐标中相对于配置文件中指定的坐标系）。`SET_GCODE_OFFSET` 命令可以改变这个值。

## 时间

对 Kalico 运行至关重要的是时钟、时间和时间戳的处理。Kalico 通过计划事件在不久的将来发生来执行打印机上的动作。例如，要打开风扇，代码可能会计划 GPIO 引脚的更改在 100ms 内。代码很少尝试采取瞬时行动。因此，Kalico 中的时间处理对于正确的操作至关重要。

Kalico 主机软件内部跟踪三种类型的时间：
* 系统时间。系统时间使用系统的单调时钟——它是一个以秒为单位存储的浮点数，并且它（通常）相对于主机计算机最后一次启动。系统时间在软件中的使用受限——它们主要用于与操作系统交互时。在主机代码中，系统时间通常存储在名为 *eventtime* 或 *curtime* 的变量中。
* 打印时间。打印时间与主微控制器时钟同步（在"[mcu]"配置部分中定义的微控制器）。它是一个以秒为单位存储的浮点数，相对于主 mcu 最后一次重启。可以通过将打印时间乘以 mcu 的静态配置的频率速率来从"打印时间"转换为主微控制器的硬件时钟。高级主机代码使用打印时间来计算几乎所有物理动作（例如，头部运动、加热器变化等）。在主机代码中，打印时间通常存储在名为 *print_time* 或 *move_time* 的变量中。
* MCU 时钟。这是每个微控制器上的硬件时钟计数器。它存储为一个整数，其更新速率相对于给定微控制器的频率。主机软件在传输到 mcu 之前将其内部时间转换为时钟。mcu 代码只以时钟刻度跟踪时间。在主机代码中，时钟值作为 64 位整数进行跟踪，而 mcu 代码使用 32 位整数。在主机代码中，时钟通常存储在名称包含 *clock* 或 *ticks* 的变量中。

不同时间格式之间的转换主要在 **klippy/clocksync.py** 代码中实现。

查看代码时要注意的一些事项：
* 32 位和 64 位时钟：为了减少带宽并提高微控制器效率，微控制器上的时钟作为 32 位整数进行跟踪。在 mcu 代码中比较两个时钟时，必须始终使用 `timer_is_before()` 函数以确保正确处理整数溢出。主机软件通过从最后接收到的 mcu 时间戳追加高位来将 32 位时钟转换为 64 位时钟——来自 mcu 的任何消息都永远不会超过 2^31 个时钟刻度在未来或过去，所以这个转换从不是模糊的。主机通过简单地截断高位来从 64 位时钟转换为 32 位时钟。为了确保这个转换中没有歧义，**klippy/chelper/serialqueue.c** 代码将缓冲消息，直到它们在其目标时间的 2^31 个时钟刻度内。
* 多个微控制器：主机软件支持在单个打印机上使用多个微控制器。在这种情况下，每个微控制器的"MCU 时钟"被单独跟踪。clocksync.py 代码通过修改将"打印时间"转换为"MCU 时钟"的方式来处理微控制器之间的时钟漂移。在次要 mcu 上，在这个转换中使用的 mcu 频率定期更新以考虑测量的漂移。