# 探针校准

本文档描述了在 Kalico 中校准"自动 Z 探针"的 X、Y 和 Z 偏移量的方法。这对于配置文件中包含 `[probe]` 或 `[bltouch]` 部分的用户很有用。

## 校准探针 X 和 Y 偏移量

要校准 X 和 Y 偏移量，请导航到 OctoPrint 的"控制"选项卡，归位打印机，然后使用 OctoPrint 的点动按钮将打印头移动到靠近热床中心的位置。

在探针下方的热床上放置一片蓝色美纹纸胶带（或类似物品）。导航到 OctoPrint 的"终端"选项卡并发出 PROBE 命令：
```
PROBE
```
在探针正下方的胶带上做一个标记（或使用类似方法记录热床上的位置）。

发出 `GET_POSITION` 命令并记录该命令报告的打印头 XY 位置。例如，如果看到：
```
Recv: // toolhead: X:46.500000 Y:27.000000 Z:15.000000 E:0.000000
```
则记录探针 X 位置为 46.5，探针 Y 位置为 27。

记录探针位置后，发出一系列 G1 命令，直到喷嘴位于热床上标记的正上方。例如，可以发出：
```
G1 F300 X57 Y30 Z15
```
将喷嘴移动到 X 位置 57，Y 位置 30。找到标记正上方的位置后，使用 `GET_POSITION` 命令报告该位置。这就是喷嘴位置。

然后 x_offset 为 `nozzle_x_position - probe_x_position`，y_offset 类似为 `nozzle_y_position - probe_y_position`。用给定的值更新 printer.cfg 文件，从热床上移除胶带/标记，然后发出 `RESTART` 命令使新值生效。

## 校准探针 Z 偏移量

提供准确的探针 z_offset 对于获得高质量打印至关重要。z_offset 是探针触发时喷嘴与热床之间的距离。Kalico 的 `PROBE_CALIBRATE` 工具可用于获取此值 - 它将运行自动探测来测量探针的 Z 触发位置，然后启动手动探测来获取喷嘴 Z 高度。探针 z_offset 将根据这些测量值计算得出。

首先归位打印机，然后将打印头移动到靠近热床中心的位置。导航到 OctoPrint 终端选项卡并运行 `PROBE_CALIBRATE` 命令启动该工具。

此工具将执行自动探测，然后抬起打印头，将喷嘴移动到探测点上方，并启动手动探测工具。如果喷嘴没有移动到自动探测点上方的位置，请 `ABORT` 手动探测工具并执行上面描述的 XY 探针偏移量校准。

手动探测工具启动后，按照 ["the paper test"](Bed_Level.md#the-paper-test) 中描述的步骤来确定给定位置处喷嘴与热床之间的实际距离。完成这些步骤后，可以 `ACCEPT` 该位置并使用以下命令将结果保存到配置文件：
```
SAVE_CONFIG
```

请注意，如果对打印机的运动系统、热端位置或探针位置进行了更改，则会使 PROBE_CALIBRATE 的结果失效。

如果探针具有 X 或 Y 偏移量，并且热床倾斜度发生了变化（例如，通过调整热床螺丝、运行 DELTA_CALIBRATE、运行 Z_TILT_ADJUST、运行 QUAD_GANTRY_LEVEL 或类似操作），则会使 PROBE_CALIBRATE 的结果失效。在进行上述任何调整后，需要重新运行 PROBE_CALIBRATE。

如果 PROBE_CALIBRATE 的结果失效，则之前使用该探针获得的任何 [bed mesh](Bed_Mesh.md) 结果也会失效 - 重新校准探针后需要重新运行 BED_MESH_CALIBRATE。

## 重复性检查

校准探针 X、Y 和 Z 偏移量后，最好验证探针是否提供可重复的结果。首先归位打印机，然后将打印头移动到靠近热床中心的位置。导航到 OctoPrint 终端选项卡并运行 `PROBE_ACCURACY` 命令。

此命令将运行探测十次并产生类似以下的输出：
```
Recv: // probe accuracy: at X:0.000 Y:0.000 Z:10.000
Recv: // and read 10 times with speed of 5 mm/s
Recv: // probe at -0.003,0.005 is z=2.506948
Recv: // probe at -0.003,0.005 is z=2.519448
Recv: // probe at -0.003,0.005 is z=2.519448
Recv: // probe at -0.003,0.005 is z=2.506948
Recv: // probe at -0.003,0.005 is z=2.519448
Recv: // probe at -0.003,0.005 is z=2.519448
Recv: // probe at -0.003,0.005 is z=2.506948
Recv: // probe at -0.003,0.005 is z=2.506948
Recv: // probe at -0.003,0.005 is z=2.519448
Recv: // probe at -0.003,0.005 is z=2.506948
Recv: // probe accuracy results: maximum 2.519448, minimum 2.506948, range 0.012500, average 2.513198, median 2.513198, standard deviation 0.006250
```

理想情况下，工具会报告相同的最大值和最小值。
（即，理想情况下探针在所有十次探测中获得相同的结果。）但是，最小值和最大值相差一个 Z "步进距离"或最多 5 微米（.005mm）是正常的。"步进距离"是
`rotation_distance/(full_steps_per_rotation*microsteps)`。最小值和最大值之间的距离称为范围。因此，在上面的示例中，由于打印机使用 .0125 的 Z 步进距离，
0.012500 的范围被认为是正常的。

如果测试结果显示范围值大于 25 微米（.025mm），则探针的精度不足以用于典型的热床调平操作。可能可以通过调整探针速度和/或探针起始高度来改善探针的重复性。`PROBE_ACCURACY` 命令允许使用不同的参数运行测试以查看其影响 - 更多详情请参见 [G-Codes 文档](G-Codes.md#probe_accuracy)。如果探针通常获得可重复的结果但偶尔有异常值，则可以通过在每次探测中使用多个样本来解决此问题 - 有关详细信息，请阅读 [配置参考](Config_Reference.md#probe) 中探针 `samples` 配置参数的说明。

如果需要新的探针速度、样本书或其他设置，请更新 printer.cfg 文件并发出 `RESTART` 命令。如果是这样，最好
[重新校准 z_offset](#calibrating-probe-z-offset)。如果无法获得可重复的结果，则不要使用探针进行热床调平。Kalico 有几个手动探测工具可以替代使用 - 更多详情请参见 [Bed Level 文档](Bed_Level.md)。

## 位置偏差检查

某些探针可能存在系统性偏差，导致在某些打印头位置的探测结果不准确。例如，如果探针安装座在沿 Y 轴移动时略有倾斜，则可能导致在不同 Y 位置探测报告有偏差的结果。

这是 delta 打印机上探针的常见问题，但也可能发生在所有打印机上。

可以使用 `PROBE_CALIBRATE` 命令在不同的 X 和 Y 位置测量探针 z_offset 来检查位置偏差。理想情况下，探针 z_offset 在每个打印机位置都应该是恒定值。

对于 delta 打印机，尝试在靠近 A 塔的位置、靠近 B 塔的位置和靠近 C 塔的位置测量 z_offset。对于笛卡尔、corexy 和类似的打印机，尝试在热床四个角附近的位置测量 z_offset。

在开始此测试之前，首先按照本文档开头描述的方法校准探针 X、Y 和 Z 偏移量。然后归位打印机并导航到第一个 XY 位置。按照 [校准探针 Z 偏移量](#calibrating-probe-z-offset) 中的步骤运行 `PROBE_CALIBRATE` 命令、`TESTZ` 命令和 `ACCEPT` 命令，但不要运行 `SAVE_CONFIG`。记录报告的 z_offset。然后导航到其他 XY 位置，重复这些 `PROBE_CALIBRATE` 步骤，并记录报告的 z_offset。

如果报告的最小 z_offset 和最大 z_offset 之间的差值大于 25 微米（.025mm），则该探针不适合用于典型的热床调平操作。有关手动探测替代方案，请参见 [Bed Level 文档](Bed_Level.md)。

## 温度偏差

许多探针在不同温度下探测时存在系统性偏差。例如，当探针温度较高时，探针可能会在较低的高度持续触发。

建议在一致的温度下运行热床调平工具以考虑这种偏差。例如，始终在打印机处于室温时运行这些工具，或者始终在打印机达到一致的打印温度后运行这些工具。在任何一种情况下，最好在达到所需温度后等待几分钟，以使打印机设备始终处于所需温度。

要检查温度偏差，首先将打印机置于室温下，然后归位打印机，将打印头移动到靠近热床中心的位置，并运行 `PROBE_ACCURACY` 命令。记录结果。然后，不进行归位或禁用步进电机，将打印机喷嘴和热床加热到打印温度，并再次运行 `PROBE_ACCURACY` 命令。理想情况下，命令将报告相同的结果。如上所述，如果探针确实存在温度偏差，则请始终在一致的温度下使用探针。
