# 非线性压力推进

本文档提供有关调整 Kalico 的 `bleeding_edge_v2` 分支中的非线性压力推进的信息，以及一些其他相关固件。

如果您使用非线性压力推进，这取代了标准的 [压力推进文档页面](Pressure_Advance.md)。

## 压力推进概述

如果 3D 打印机以完全按比例于工具头速度的速度推动丝材，丝材从喷嘴出来的实际速率将不匹配。

当挤出机开始移动时，热端中的流动阻力将导致压缩下的丝材在可以的情况下弯曲（特别是在 Bowden 管中），然后线性缩短。

为了补偿这一点，使用了将热端中的压缩丝材和熔融塑料建模为线性弹簧的"压力推进"，增加了所请求的挤出机位置超过名义位置的量，与名义挤出速度成正比。

## 线性压力推进的问题

但是，有几个因素使此模型不完美。

首先，机械系统本身具有轻微的延迟。
丝材在挤出机处的运动到达喷嘴尖端需要时间。
这意味着随着工具头速度的变化，特别是在高加速度下，最小挤出点和最小工具头速度实际发生的实际角之间可能会出现剧烈的不同步。
这表现为角之前的增厚和角之后的变薄。
它另外导致在不同加速度下的不同行为。

其次，压缩下的丝材、张力下的结构和熔池不表现出弹性。
丝材的弯曲动作相对为低刚性，但一旦管中的所有空间被占用，它就停止进一步合规。
熔融本身的作用也是非线性的。
当丝材必须展开以与热块的墙壁接触时，压力因此流速影响热端中熔融和未熔融丝材的比例，这影响弹簧常数。

这意味着对一个速度和加速度正确的压力推进不会在所有速度和加速度下以最优方式表现。
很多时候，对更高速度角充分高的 PA 将对较低速度不足，如接缝和过悬挂附近的过渡。

这些效应对于需要更高 PA 的打印机（如 Bowden 打印机）倍增。

## 解释

非线性压力推进，而不是按速度按比例推进，允许使用非线性函数来确定所请求挤出相对于名义挤出量提前的量。

为了在较低速度下提供更高的有效 PA，推进的量可以配置为在低速时快速上升，然后对速度范围的其余部分降低到较低的斜率。

![非线性丝材推进量相对于丝材流速的图表](img/PA_photos/nonlin_advance_vs_flowrate.png)

在此示例中，一旦工具头达到其全速，将发生相同的总推进，但非线性推进在每个运动开始时上升得更快。

![非线性 PA 丝材位置相对于时间](img/PA_photos/nonlin_position_vs_time.png)

低速时的上升由固件中的两个参数控制：`nonlinear_offset` 和 `linearization_velocity`。
线性化速度之后发生的线性斜率由 `linear_advance` 控制。

为了完全清楚，由于实现，它们不是完美独立的。
低速推进受 `linear_advance` 设置的轻微影响，同样高速推进受偏移和线性化速度的影响。

这种交互意味着不同的参数需要通过迭代过程进行调整，不像只有一个变量可微调的标准 PA。

您可以在 [这个电子表格](resources/NonlinearPA_Kalico.ods) 中使用这个。

除了能够生成上面的两个图表外，还有提供预期丝材流速和加速的图表。
这在调整高速机器时很有用，知道挤出机的限制。

![非线性 PA 丝材流速相对于时间](img/PA_photos/nonlin_speed_vs_time.png)
![非线性 PA 丝材加速度相对于时间](img/PA_photos/nonlin_accel_vs_time.png)

根据具体设置，非线性 PA 可以请求更高的速度，几乎总是请求更高的加速度比标准 PA，所以您可以将此与测试结合使用，确保新的设置组合您尝试没有问题。

请注意有两个不同的非线性函数：倒数和 tanh。
它们都可以有类似的结果，但倒数提供了低速和高速 PA 之间更好的独立性，所以我们建议您使用它以简化调整。

## 设置

调整非线性压力推进的最佳方式是使用 `bleeding-edge-v2` Kalico 中内置的调整宏。

这生成 gcode 来打印调整塔，在改变一个参数的同时测试几个不同的速度转换。
因为您调整多个参数，您需要这个来查看您的参数是否在整个电路板上工作，或者您是否需要调整固定参数。

建议将宏和调整塔配置参数放在它们自己的 `testing_macros.cfg` 文件中。

根据您的机器的参数设置 `[pa_test]` 部分。
通常保持大小和高度不变。
将起点放在您希望塔的中心位置。

将中等和快速速度设置在您想要的地方附近。
对于 300mm/s 打印机，让 `fast_velocity` 为 300，`medium_velocity` 为 100。
最好在 20 处保持缓慢速度，以更好地探测过悬挂和接缝附近的速度。

在 `[delayed_gcode start_pa_test]` 部分内，放入您的启动 gcode（无论是单个 `print_start` 宏还是一系列单个 gcode 调用）。

如果需要在调整塔上有更多范围，调整适当参数的 `FACTOR`。

```
[pa_test]
size_x: 100   # X 维度塔尺寸  (mm)
size_y: 50    # Y 维度塔尺寸  (mm)
height: 50    # 塔的高度 (mm)
origin_x: 100 # 床在 X 中的中心
origin_y: 100 # 床在 Y 中的中心
layer_height: 0.2 # mm
first_layer_height: 0.24 # mm
perimeters: 2 # 要为塔打印的周长数
brim_width: 6 # 边框宽度 (mm)
slow_velocity:   20 # PA 测试段的最慢速度 (mm/s)
medium_velocity: 50 # PA 测试段的中等速度 (mm/s)
fast_velocity:  150 # PA 测试段的结束速度 (mm/s)
filament_diameter: 1.75
fan_speed: 0.5 # 打印边框后应用的风扇速度

[delayed_gcode start_pa_test]
gcode:
    {% set vars = printer["gcode_macro RUN_PA_TEST"] %}
    ; 在这里放入您的启动 GCODE========================================================
    {% set flow_percent = vars.flow_rate|float * 100.0 %}
    {% if flow_percent > 0 %}
        M221 S{flow_percent}
    {% endif %}
    {% set height = printer.configfile.settings.pa_test.height %}
    {% set pavalue = vars.pa_value %}
    ; 如果 pa_value 为 0，则我们测试从 0 开始的完整 pa 范围
    {% if  vars.pa_value == 0 %}
        {% if vars.testparam == 0 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.001 ; Bowden 为 .01
        {% elif vars.testparam == 1 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=OFFSET START=0 FACTOR=.01 ; Bowden 为 .02
        {% elif vars.testparam == 2 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=TIME_OFFSET START=0 FACTOR=.0001
        {% endif %}
    {% else %}
        ; 确保 delta 和 start 不能低于 0
        {% if (vars.pa_value - vars.pa_range <= 0) and (vars.testparam <= 2) %}
            {% set delta = vars.pa_range %}
            {% set start = 0 %}
        {% else %}
            ; 计算我们想测试的 pa 范围
            {% set delta = (vars.pa_value + vars.pa_range)  - (vars.pa_value - vars.pa_range)  %}
            ; 计算 pa 开始值
            {% set start = vars.pa_value - vars.pa_range %}
        {% endif %}
        {% if vars.testparam == 0 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START={start} FACTOR={delta / height}
        {% elif vars.testparam == 1 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=OFFSET START={start} FACTOR={delta / height}
        {% elif vars.testparam == 2 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=TIME_OFFSET START={start} FACTOR={delta / height}
        {% endif %}
    {% endif %}
    ; PRINT_PA_TOWER 必须是 start_pa_test 脚本中的最后一个命令：
    ; 它启动打印，然后立即返回而不等待打印完成
    PRINT_PA_TOWER {vars.rawparams} FINAL_GCODE_ID=end_pa_test

[delayed_gcode end_pa_test]
gcode:
    END_PRINT
    RESTORE_GCODE_STATE NAME=PA_TEST_STATE

[gcode_macro RUN_PA_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_pa_value: 0             # 用于进一步微调 pa 值。如果值不为 0，则测试的 pa 值将仅为 +/-（由 pa_range 变量确定）pa_value 变量周围
variable_pa_range: 0.03          # 仅在 pa_value 设置为大于 0 时使用。用于设置应测试的 pa_value 周围的 +/- 区域
variable_flow_rate: -1
variable_testparam: 0            # 0 = advance，1 = offset，2 = time_offset
variable_fan_speed: 0.5
variable_rawparams: ''
gcode:
    # 如果未提供所需参数，则尽早失败
    {% if params.NOZZLE is not defined %}
    {action_raise_error('必须提供 NOZZLE= 参数')}
    {% endif %}
    {% if params.TARGET_TEMP is not defined %}
    {action_raise_error('必须提供 TARGET_TEMP= 参数')}
    {% endif %}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=bed_temp VALUE={params.BED_TEMP|default(60)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=hotend_temp VALUE={params.TARGET_TEMP}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=pa_value VALUE={params.PA_VALUE|default(0)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=pa_range VALUE={params.PA_RANGE|default(0.01)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=flow_rate VALUE={params.FLOW_RATE|default(-1)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=testparam VALUE={params.TESTPARAM|default(0)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=fan_speed VALUE={params.FAN_SPEED|default(0.5)}
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=rawparams VALUE="'{rawparams}'"
    SAVE_GCODE_STATE NAME=PA_TEST_STATE
    UPDATE_DELAYED_GCODE ID=start_pa_test DURATION=0.01
```

***关键注意***

PA 测试宏将在打印机 `printer.cfg` 部分中指定的加速度下运行 `[printer]`。
将其设置为您期望在挤出时使用的最高加速度（例如，对于填充）。

### 通过 G-Code 设置值

要在运行时更改非线性 PA，无论是在打印机命令行还是在您的切片软件丝材设置中，使用 `SET_PRESSURE_ADVANCE` 命令，带有以下参数：

* `ADVANCE=` linear_advance（线性推进）
* `OFFSET=` nonlinear_offset（非线性偏移）
* `VELOCITY=` linearization_velocity（线性化速度）
* `TIME_OFFSET=` pressure_advance_time_offset（压力推进时间偏移）

## 调整程序

对于更平凡的打印机（由偏移主导）与超快速打印机（将具有更多线性推进分量）或 Bowden 管打印机（对两者都有大值）的调整程序将略有不同。

评估由 PA 测试宏生成的调整塔时，使用明亮的灯从极端左或右侧照亮很有帮助。

### 直接驱动、低至中等性能

1. 安装 Kalico 并确保使用 `bleeding-edge-v2` 分支。
2. 按照设置部分中的说明设置 PA 测试宏，并确保在 `[printer]` 中设置所需的加速度。
3. 如果您计划在所有情况下使用输入整形，请进行设置。它影响调整塔的可读性。用 `enabled_extruders: extruder` 设置挤出机同步。
4. 在您的打印机配置中，将 `pressure_advance_model` 设置为 `tanh`、`linear_advance` 设置为 0、`nonlinear_offset` 设置为 0、`linearization_velocity` 设置为 1，`pressure_advance_smooth_time` 设置为 0.02。重启打印机以加载新设置。
5. 使用 `NOZZLE` 设置为您的喷嘴直径、`TARGET_TEMP` 设置为您的预期热端温度、`TESTPARAM` 为 1 运行 pa 测试宏，以改变 `nonlinear_offset`。
6. 评估塔，主要看左侧。根据在那里看起来最好的高度（以及测试宏代码中的 `factor`）在您的打印机配置中设置 `nonlinear_offset`，然后重启。
7. 使用您的喷嘴直径、您的预期热端温度、`TESTPARAM` 为 0 运行 pa 测试宏，以改变 `linear_advance`。
8. 评估塔，主要查看左侧和前侧，并进行二分查找以找到最优偏移和推进。
    1. 如果左侧在前侧下方收敛，则在您的配置中轻微降低 `nonlinear_offset`（从 10% 开始，如果过度则减少），重启，并用 `TESTPARAM` 0 重新打印 PA 测试宏。
    2. 如果左侧在前侧上方收敛，则在您的配置中轻微提高 `nonlinear_offset`（从 10% 开始，如果过度则减少），重启，并用 `TESTPARAM` 0 重新打印 PA 测试宏。
    3. 如果左侧在前侧相同高度收敛，则使用该高度和测试宏代码中的 `factor` 在您的打印机配置中设置 `linear_advance`，然后重启。
9. 使用您的喷嘴直径、您的预期热端温度、`TESTPARAM` 为 2 运行 pa 测试宏，以改变 `pressure_advance_time_offset`。
10. 评估塔，主要查看前侧。这可以*非常*微妙，所以确保使用良好的照明来显示差异。根据那里看起来最好的高度和测试宏代码中的 `factor` 在您的配置中设置 `pressure_advance_time_offset`，然后重启。

### Bowden 或超高速直接驱动打印机

确保调整 PA 测试宏中 Bowden 打印机的因素。

1. 安装 Kalico 并确保使用 `bleeding-edge-v2` 分支。
2. 按照设置部分中的说明设置 PA 测试宏，并确保在 `[printer]` 中设置所需的加速度。
3. 如果您计划在所有情况下使用输入整形，请进行设置。它影响调整塔的可读性。用 `enabled_extruders: extruder` 设置挤出机同步。
4. 在您的打印机配置中，将 `pressure_advance_model` 设置为 `tanh`、`linear_advance` 设置为 0、`nonlinear_offset` 设置为 0、`linearization_velocity` 设置为 1（对于 Bowden 为 2 或可能 3，其中高加速度加上大 PA 值可能导致挤出机加速度需求过高和低线性化速度），`pressure_advance_smooth_time` 设置为 0.02。重启打印机以加载新设置。
5. 使用 `NOZZLE` 设置为您的喷嘴直径、`TARGET_TEMP` 设置为您的预期热端温度、`TESTPARAM` 为 0 运行 pa 测试宏，以改变 `linear_advance`。
6. 评估塔，主要查看前侧。根据那里看起来最好的高度和测试宏代码中的 `factor` 评估理想的 `linear_advance`，记下该值，但在配置中将其设置为该值的 80%，然后重启。
7. 使用您的喷嘴直径、您的预期热端温度、`TESTPARAM` 为 1 运行 pa 测试宏，以改变 `nonlinear_offset`。
8. 评估塔，主要查看左侧和前侧，并进行二分查找以找到最优偏移和推进。
    1. 如果左侧在前侧下方收敛，则在您的配置中轻微提高 `linear_advance`（从 10% 开始，如果过度则减少），重启，并用 `TESTPARAM` 1 重新打印 PA 测试宏。
    2. 如果左侧在前侧上方收敛，则在您的配置中轻微降低 `linear_advance`（从 10% 开始，如果过度则减少），重启，并用 `TESTPARAM` 1 重新打印 PA 测试宏。
    3. 如果左侧在前侧相同高度收敛，则使用该高度和测试宏代码中的 `factor` 在您的打印机配置中设置 `nonlinear_offset`，然后重启。
9. 使用您的喷嘴直径、您的预期热端温度、`TESTPARAM` 为 2 运行 pa 测试宏，以改变 `pressure_advance_time_offset`。
10. 评估塔，主要查看前侧。这可以*非常*微妙，所以确保使用良好的照明来显示差异。根据那里看起来最好的高度和测试宏代码中的 `factor` 在您的配置中设置 `pressure_advance_time_offset`，然后重启。
11. 再次用 `TESTPARAM` 为 1 运行 PA 测试宏，并使用第 8 步中的程序再次微调您的设置。

### SV06 Plus 示例

这是在 Sovol SV06 Plus（具有标准火山长度热端的特性，喷嘴尖端稍长）上以 150mm/s 和 5k 加速度调整 Kalico 非线性 PA 的示例，使用 215°C 的标准 PLA。

首先用测试参数 0 进行 PA 测试塔，并根据前速度转换设置 `linear_advance`。
在这种情况下，`linear_advance` 为 0.04。

![linear advance test tower](img/PA_photos/0.advance=x.001.jpg)

接下来，打印了响铃测试塔以设置整形器，因为没有床加速度计。启用了挤出机同步。
打印了另一个响铃测试塔来检查响铃是否被抑制。

`linear_advance` 被设置回零、`linearization_velocity` 设置为 1、`pressure_advance_smooth_time` 设置为 0.02、`pressure_advance_time_offset` 设置为 0。
然后用测试参数 1 打印了 PA 测试塔。

![linear offset test tower](img/PA_photos/1.offset=x.005.jpg)

在这种情况下，左侧在大约 27mm * 0.005 处看起来最好，所以 `nonlinear_offset` 被设置为 0.135 以开始，并用测试参数 0 打印了 PA 测试塔。

![linear advance test tower with 0.135 linear offset](img/PA_photos/2.offset=.135_advance=x.001.jpg)

在此测试中，左侧在最下方收敛，但右侧收敛上方，所以 `nonlinear_offset` 被稍微降低至 0.120。
回顾一下，查看 `nonlinear_offset` 的前一个测试塔，左侧上的左行在 24mm 处刚刚开始具有 "厚薄" 模式，右行仅略欠补偿。
总的来说，最好在初始 `nonlinear_offset` 上轻微欠补偿，因为 `linear_advance` 甚至在低速时会给出一点推动。

在 `nonlinear_offset` 降低至 0.120 后，用测试参数 0 打印了另一个测试塔。

![linear advance test tower with 0.120 linear offset](img/PA_photos/3.offset=.120_advance=x.001.jpg)

这显示了左侧和前侧都在 17mm * 0.001 处的良好收敛，所以理想的 `linear_advance` 为 0.017，无需进一步微调 `nonlinear_offset`。

仅作演示，以下是对 `nonlinear_offset` 到 0.100 的轻微过度补偿在用测试参数 0 打印测试塔时的样子：

![linear advance test tower with 0.100 linear offset](img/PA_photos/4.offset=.100_advance=x.001.jpg)

这不是那么清楚，但左侧收敛的高度略高于测试塔的前侧。如果您看到这个，您会将 `nonlinear_offset` 轻微向上推动并重新测试。

最后，时间偏移被调整为正确地使压力推进补偿与实际工具头运动对齐。

最后一个调整塔用打印机设置为 0.120 线性偏移、0.017 线性推进和宏的测试参数设置为 2 打印。

![time offset test tower](img/PA_photos/5.time_offset=x.0001.jpg)

这是很难看到效果的，但极端侧照显示前面上的最左侧和最右侧转换受益于 18mm * 0.0001 的高度，指示 `pressure_advance_time_offset` 应设置为 0.0018。这意味着压力推进应提前 1.8 毫秒以最好地同步流量与工具头运动。

### 性能比较

这是用三个不同的线性 PA（无时间偏移）与非线性调整打印的 Voron 测试立方体的比较。

周长以适度的 3000 mm/s^2 加速度打印以获得最大质量，但即使如此，差异也是可见的。
在更高加速度处，差异将更加可见。

此外，此比较不与主分支或 vanilla Klipper 比较，它们不具有与输入整形同步的挤出机。

![压力推进的校准立方体比较](img/PA_photos/voroncube.jpg)

从左到右的列是：侧照下、侧照 Y、顶照 Y、侧照 X、顶照 X、顶部的立方体前照。

在底部，0.025 线性 PA 在 ESE 角有明显的鼓起，而其他的显示很少的差异。

在侧照 Y 面上，您可以看到所有三个线性 PA 在六边形的侧面和顶面周围具有黑色轮廓，其中存在轻微的降低区域。
他们也在过悬挂角处明显鼓起，其中线性 PA 在过悬挂的低速处欠补偿。
相比之下，非线性 PA 的面极其平坦。

用顶部照明观看，很容易看到非线性 PA 从六边形顶面的鼓起量少多少。

侧照 X 面显示非线性测试立方体中围绕槽的表面更平坦，而线性测试立方体显示槽右侧的阴影区域。

当顶照时，0.04 和 0.03 线性 PA 在每个槽后略晚显示大鼓起，铸造下方的阴影。
0.025 线性 PA 显示可能来自从非常缓慢的桥速转换到墙速的顶部槽的小压痕。
非线性 PA 表现出类似的效果但程度小得多。

顶部视图说明 0.03 已经是足够多的线性 PA 以在角周围保持完全挤出。
0.04 线性具有周长线之间的大间隙，并且在实心填充线的末端开始具有空隙。
非线性和 0.025 线性都在角周围完全挤出。