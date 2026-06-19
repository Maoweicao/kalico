# G-Code Shell Command 扩展

### 此扩展的创建者是 [Arksine](https://github.com/Arksine)。

这是关于如何在 Kalico 中使用 shell 命令扩展的简要说明，你可以通过 KIAUH 安装它。

安装扩展后，你可以使用在 printer.cfg 中定义的自定义命令在 Kalico 中执行 Linux 命令甚至脚本。

#### 如何配置 shell 命令：

```shell
# 从 Kalico 内部运行 Linux 命令或脚本。注意，需要密码认证的 sudo 命令是不允许的。
# 所有可执行脚本都应包含 shebang。
# [gcode_shell_command my_shell_cmd]
#command:
#  要执行的 Linux shell 命令/脚本。必须提供此参数
#timeout: 2.
#  命令被强制终止前的超时时间（秒）。默认为 2 秒。
#verbose: True
#  如果启用，命令的输出将被转发到终端。对于可能连续快速运行的命令，建议将其设置为 false。
#  默认为 True。
```

设置好带有上述参数的 shell 命令后，你可以按如下方式运行命令：
`RUN_SHELL_COMMAND CMD=name`

示例：

```
[gcode_shell_command hello_world]
command: echo hello world
timeout: 2.
verbose: True
```

执行：
`RUN_SHELL_COMMAND CMD=hello_world`

### 传递参数：

自提交 [f231fa9](https://github.com/dw-0/kiauh/commit/f231fa9c69191f23277b4e3319f6b675bfa0ee42) 起，还可以向 `gcode_shell_command` 传递可选参数。
以下简短示例展示了将挤出机温度存储到变量中，然后通过参数将该值传递给 `gcode_shell_command` 的过程。当 gcode_macro 运行并调用 gcode_shell_command 时，它将执行 `script.sh`。该脚本随后将消息回显到控制台（如果 `verbose: True`），并将参数值写入位于主目录中名为 `test.txt` 的文本文件。

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

如果不小心使用，此扩展可能有很高的滥用风险！此外，根据你执行的命令，可能会出现高系统负载并导致系统不稳定。
使用此扩展的风险由你自己承担，仅在你知道自己在做什么时才使用！
