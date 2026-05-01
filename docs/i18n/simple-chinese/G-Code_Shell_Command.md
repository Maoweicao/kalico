# G-Code Shell 命令扩展

### 此扩展的创建者是 [Arksine](https://github.com/Arksine)。

这是关于如何使用 Kalico 的 shell 命令扩展的简要说明，您可以使用 KIAUH 进行安装。

安装扩展后，您可以从 Kalico 中使用打印机 .cfg 中定义的自定义命令执行 Linux 命令或甚至脚本。

#### 如何配置 shell 命令：

```shell
# 从 Kalico 中运行 Linux 命令或脚本。请注意，需要密码身份验证的 sudo 命令
# 是不允许的。所有可执行脚本应包含 shebang。
# [gcode_shell_command my_shell_cmd]
#command:
#  要执行的 Linux shell 命令/脚本。必须提供此参数
#timeout: 2.
#  命令被强制终止的超时秒数。默认值为 2 秒。
#verbose: True
#  如果启用，命令的输出将转发到终端。建议对可能快速连续
#  运行的命令将其设置为 false。默认值为 True。
```

在打印机 .cfg 中使用上述参数设置 shell 命令后，可以如下运行命令：
`RUN_SHELL_COMMAND CMD=name`

示例：

```
[gcode_shell_command hello_world]
command: echo hello world
timeout: 2.
verbose: True
```

执行方式：
`RUN_SHELL_COMMAND CMD=hello_world`

### 传递参数：

从提交 [f231fa9](https://github.com/dw-0/kiauh/commit/f231fa9c69191f23277b4e3319f6b675bfa0ee42) 开始，也可以将可选参数传递给 `gcode_shell_command`。
下面的简短示例展示了将挤出机温度存储在变量中、使用参数将该值传递给 `gcode_shell_command`，然后，
当 gcode_macro 运行并调用 gcode_shell_command 时，执行 `script.sh`。脚本随后向控制台发出消息（如果 `verbose: True`）
并将参数值写入位于主目录中的名为 `test.txt` 的文本文件。

`gcode_shell_command` 和 `gcode_macro` 的内容：

```
[gcode_shell_command print_to_file]
command: sh /home/pi/printer_data/config/script.sh
timeout: 30.
verbose: True

[gcode_macro GET_TEMP]
gcode:
    {% set temp = printer.extruder.temperature %}
    { action_respond_info("%s" % (temp)) }
    RUN_SHELL_COMMAND CMD=print_to_file PARAMS={temp}
```

`script.sh` 的内容：

```shell
#!/bin/sh

echo "temp is: $1"
echo "$1" >> "${HOME}/test.txt"
```

## 警告

如果使用不当，此扩展可能会有很高的滥用潜能！另外，根据您执行的命令，可能会发生高系统负载并可能导致系统不稳定。
请自担风险使用此扩展，仅当您知道自己在做什么时才使用！