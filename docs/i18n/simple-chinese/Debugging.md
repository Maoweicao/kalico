# 调试

本文档描述了一些 Kalico 调试工具。

## 运行回归测试

主 Kalico GitHub 存储库使用"github actions"来运行一系列回归测试。
在本地运行其中一些测试会很有用。

源代码"空格检查"可以运行如下：
```
./scripts/check_whitespace.sh
```

Klippy 回归测试套件需要来自许多平台的"数据字典"。
获取它们的最简单方法是 [从 github 下载](https://github.com/Klipper3d/klipper/issues/1438)。
下载数据字典后，使用以下命令运行回归套件：
```
tar xfz klipper-dict-20??????.tar.gz
~/klippy-env/bin/python ~/klipper/scripts/test_klippy.py -d dict/ ~/klipper/test/klippy/*.test
```

## 手动向微控制器发送命令

通常，主 klippy.py 进程会被用来将 gcode 命令转换为 Kalico 微控制器命令。
但是，也可以手动发送这些 MCU 命令（在 Kalico 源代码中用 DECL_COMMAND() 宏标记的函数）。
要执行此操作，请运行：

```
~/klippy-env/bin/python ./klippy/console.py /tmp/pseudoserial
```

有关其功能的更多信息，请参阅工具中的"HELP"命令。

可以使用一些命令行选项。有关更多信息，请运行：
`~/klippy-env/bin/python ./klippy/console.py --help`

## 将 gcode 文件转换为微控制器命令

Klippy 主机代码可以在批处理模式下运行以生成与 gcode 文件关联的低级
微控制器命令。当尝试了解低级硬件的操作时，检查这些低级命令很有用。
在代码更改后比较微控制器命令中的差异时也很有用。

要在批处理模式下运行 Klippy，需要一个一次性步骤来生成微控制器"数据字典"。
这是通过编译微控制器代码以获得 **out/klipper.dict** 文件来完成的：

```
make menuconfig
make
```

完成上述操作后，可以在批处理模式下运行 Kalico
（有关构建 python 虚拟环境和 printer.cfg 文件的必要步骤，
请参阅 [安装](Installation.md)）：

```
~/klippy-env/bin/python ./klippy/klippy.py ~/printer.cfg -i test.gcode -o test.serial -v -d out/klipper.dict
```

上面的命令将生成一个包含二进制串行输出的文件 **test.serial**。
此输出可以使用以下命令转换为可读文本：

```
~/klippy-env/bin/python ./klippy/parsedump.py out/klipper.dict test.serial > test.txt
```

生成的文件 **test.txt** 包含人类可读的微控制器命令列表。

批处理模式禁用某些响应/请求命令以使其能够正常工作。
因此，实际命令和上述输出之间会有一些差异。
生成的数据对于测试和检查很有用；它不适用于发送到真实微控制器。

## 运动分析和数据记录

Kalico 支持记录其内部运动历史，以供稍后分析。要使用此功能，
Kalico 必须以启用 [API Server](API_Server.md) 的方式启动。

数据记录通过 `data_logger.py` 工具启用。例如：
```
~/klipper/scripts/motan/data_logger.py /tmp/klippy_uds mylog
```

此命令将连接到 Kalico API Server，订阅状态和运动信息，
并记录结果。生成两个文件——一个压缩数据文件和一个索引文件
（例如，`mylog.json.gz` 和 `mylog.index.gz`）。启动记录后，
可以完成打印和其他操作——记录将在后台继续。
完成记录后，按 `ctrl-c` 退出 `data_logger.py` 工具。

生成的文件可以使用 `motan_graph.py` 工具读取和绘制。
在 Raspberry Pi 上生成图表需要一次性步骤来安装"matplotlib"包：
```
sudo apt-get update
sudo apt-get install python-matplotlib
```

但是，将数据文件与 `scripts/motan/` 目录中的 Python 代码复制到
桌面类计算机可能更方便。运动分析脚本应在任何装有
最新版本 [Python](https://python.org) 和 [Matplotlib](https://matplotlib.org/) 的计算机上运行。

可以使用如下命令生成图表：
```
~/klipper/scripts/motan/motan_graph.py mylog -o mygraph.png
```

可以使用 `-g` 选项指定要绘制的数据集
（它需要包含列表列表的 Python 字面量）。例如：
```
~/klipper/scripts/motan/motan_graph.py mylog -g '[["trapq(toolhead,velocity)"], ["trapq(toolhead,accel)"]]'
```

可以使用 `-l` 选项找到可用数据集的列表——例如：
```
~/klipper/scripts/motan/motan_graph.py -l
```

还可以为每个数据集指定 matplotlib 绘制选项：
```
~/klipper/scripts/motan/motan_graph.py mylog -g '[["trapq(toolhead,velocity)?color=red&alpha=0.4"]]'
```

许多 matplotlib 选项可用；一些示例是"color"、"label"、"alpha"和"linestyle"。

`motan_graph.py` 工具支持多个其他命令行选项——使用 `--help` 选项查看列表。
查看/修改 [motan_graph.py](../scripts/motan/motan_graph.py) 脚本本身也可能很方便。

`data_logger.py` 工具生成的原始数据日志遵循 [API Server](API_Server.md)
中描述的格式。使用 Unix 命令检查数据可能很有用，例如：
`gunzip < mylog.json.gz | tr '\03' '\n' | less`

## 生成负载图形

Klippy 日志文件 (/tmp/klippy.log) 存储带宽、微控制器负载和主机缓冲区负载的统计信息。
在打印后绘制这些统计信息可能很有用。

要生成图形，需要一次性步骤来安装"matplotlib"包：

```
sudo apt-get update
sudo apt-get install python-matplotlib
```

然后可以使用以下命令生成图形：

```
~/klipper/scripts/graphstats.py /tmp/klippy.log -o loadgraph.png
```

然后可以查看生成的 **loadgraph.png** 文件。

可以生成不同的图形。有关更多信息，请运行：
`~/klipper/scripts/graphstats.py --help`

## 从 klippy.log 文件提取信息

Klippy 日志文件 (/tmp/klippy.log) 也包含调试信息。
当分析微控制器关闭或类似问题时，可能有用的 logextract.py 脚本。
通常使用如下命令运行：

```
mkdir work_directory
cd work_directory
cp /tmp/klippy.log .
~/klipper/scripts/logextract.py ./klippy.log
```

脚本将提取打印机配置文件，并将提取 MCU 关闭信息。
MCU 关闭中的信息转储（如果存在）将按时间戳重新排序以协助诊断原因和结果场景。

## 使用 simulavr 测试

[simulavr](http://www.nongnu.org/simulavr/) 工具使能够模拟 Atmel ATmega 微控制器。
本部分描述了如何通过 simulavr 运行测试 gcode 文件。
建议在台式计算机（而不是 Raspberry Pi）上运行，
因为它确实需要大量 CPU 才能有效运行。

要使用 simulavr，请下载 simulavr 包并使用 python 支持进行编译。
请注意，构建系统可能需要安装一些包（如 swig）来构建 python 模块。

```
git clone git://git.savannah.nongnu.org/simulavr.git
cd simulavr
make python
make build
```

确保在上述编译后存在类似 **./build/pysimulavr/_pysimulavr.*.so** 的文件：
```
ls ./build/pysimulavr/_pysimulavr.*.so
```

此命令应报告特定文件（例如
**./build/pysimulavr/_pysimulavr.cpython-39-x86_64-linux-gnu.so**）
而不是错误。

如果您在基于 Debian 的系统（Debian、Ubuntu 等）上，
可以安装以下包并生成 *.deb 文件，用于 simulavr 的系统范围安装：
```
sudo apt update
sudo apt install g++ make cmake swig rst2pdf help2man texinfo
make cfgclean python debian
sudo dpkg -i build/debian/python3-simulavr*.deb
```

要为在 simulavr 中使用编译 Kalico，请运行：

```
cd /path/to/kalico
make menuconfig
```

并为 AVR atmega644p 编译微控制器软件，并选择 SIMULAVR 软件仿真支持。
然后可以编译 Kalico（运行 `make`），然后使用以下命令启动模拟：

```
PYTHONPATH=/path/to/simulavr/build/pysimulavr/ ./scripts/avrsim.py out/klipper.elf
```

请注意，如果您已系统范围安装了 python3-simulavr，则不需要设置 `PYTHONPATH`，
可以简单地将模拟器作为
```
./scripts/avrsim.py out/klipper.elf
```

然后，在另一个窗口中运行 simulavr，可以运行以下命令
从文件读取 gcode（例如"test.gcode"），使用 Klippy 处理它，
并将其发送到在 simulavr 中运行的 Kalico
（有关构建 python 虚拟环境的必要步骤，请参阅 [安装](Installation.md)）：

```
~/klippy-env/bin/python ./klippy/klippy.py config/generic-simulavr.cfg -i test.gcode -v
```

### 使用 gtkwave 的 simulavr

simulavr 的一个有用特性是其能够使用事件的精确时序创建信号波形生成文件。
要执行此操作，请按照上面的说明操作，但使用类似以下的命令行运行 avrsim.py：

```
PYTHONPATH=/path/to/simulavr/src/python/ ./scripts/avrsim.py out/klipper.elf -t PORTA.PORT,PORTC.PORT
```

上面的命令将创建一个文件 **avrsim.vcd**，其中包含 PORTA 和 PORTB 上的 GPIO
的每次更改信息。然后可以使用 gtkwave 查看这个文件：

```
gtkwave avrsim.vcd