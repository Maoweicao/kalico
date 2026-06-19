# 非线性压力推进

本文档提供了关于调整 Kalico `bleeding_edge_v2` 分支以及其他一些相关固件中非线性压力推进的信息。

如果你正在使用非线性压力推进，这将取代标准的[压力推进文档页面](Pressure_Advance.md)。

## 压力推进概述

如果 3D 打印机以与工具头速度完全成正比的速度推送耗材，那么实际从喷嘴流出的塑料速率将不匹配。

当挤出机开始移动时，热端中的流动阻力会导致压缩状态下的耗材在可能的情况下发生弯曲（特别是在鲍登管中），然后被线性缩短。

为了补偿这一点，使用了"压力推进"，它将热端中压缩的耗材和熔化的塑料建模为线性弹簧，将请求的挤出机位置提前到名义位置之前，提前量与名义挤出速度成正比。

## 线性压力推进的问题

然而，有几个因素使这个模型并不完美。

首先，机械系统本身固有地存在轻微延迟。
耗材在挤出机处的运动需要时间才能到达喷嘴尖端。
这意味着当工具头速度发生变化时，特别是在高加速度下，最小挤出点与实际最小工具头速度出现的拐角之间可能存在显著的不同步。
这表现为拐角前的增厚和拐角后的变薄。
此外，它还会导致不同加速度下的行为不同。

其次，压缩状态下的耗材、受拉伸的结构和熔池的行为并非弹性。
耗材的弯曲作用相对较低，但一旦管道中的所有空间被占据，它就不再具有柔韧性。
熔化本身的作用也是非线性的。
由于耗材必须膨胀才能与加热块的壁接触，压力和流速会影响热端中已熔化和未熔化耗材的比例，从而影响弹簧常数。

这意味着在一个速度和加速度下正确的压力推进在所有速度和加速度下都不会达到最佳效果。
通常，对于较高速度拐角足够的 PA 在较低速度下会不足，例如接缝和较慢悬垂面附近的过渡。

对于需要更高 PA 的打印机（如鲍登打印机），这些影响会被放大。

## 解释

非线性压力推进不是与速度成比例地推进，而是允许使用非线性函数来确定请求的挤出量比名义挤出量提前多少。

为了在较低速度下提供更高的有效 PA，可以将推进量配置为在低速时快速上升，然后在剩余的速度范围内降低到较低的斜率。

![非线性耗材推进量与耗材流速的关系图](/img/PA_photos/nonlin_advance_vs_flowrate.png)

在此示例中，一旦工具头达到全速，总推进量相同，但非线性推进在每个运动开始时上升更快。

![非线性 PA 耗材位置与时间的关系](/img/PA_photos/nonlin_position_vs_time.png)

低速时的上升由固件中的两个参数控制：`nonlinear_offset` 和 `linearization_velocity`。
超过线性化速度后出现的线性斜率由 `linear_advance` 控制。

需要明确的是，由于实现方式，它们并非完全独立。
低速时的推进会受到 `linear_advance` 设置的轻微影响，同样，高速时的推进也会受到偏移量和线性化速度的影响。

这种交互意味着需要以迭代过程调整不同的参数，而不是像标准 PA 那样只有一个变量需要调整。

你可以在[此电子表格](resources/NonlinearPA_Kalico.ods)中进行实验。

除了能够生成上述两个图表外，还有提供预期耗材进料速度和加速度的图表。
在调整高速机器时，了解挤出机的极限非常有用。

![非线性 PA 耗材进料速度与时间的关系](/img/PA_photos/nonlin_speed_vs_time.png)
![非线性 PA 耗材加速度与时间的关系](/img/PA_photos/nonlin_accel_vs_time.png)

根据具体设置，非线性 PA 可以请求更高速度，并且几乎总是比标准 PA 请求更高的加速度，因此你可以结合测试来确保你尝试的新设置组合没有问题。

请注意，有两种不同的非线性函数：倒数函数和 tanh 函数。
它们都可以产生相似的结果，但倒数函数在低速和高速 PA 之间提供更好的独立性，因此我们建议你使用它以便于调整。

## 设置

调整非线性压力推进的最佳方法是使用 `bleeding-edge-v2` Kalico 中内置的调整宏。

这会生成用于打印调整塔的 gcode，该调整塔测试多个不同的速度过渡，同时改变一个参数。
由于你正在调整多个参数，你需要它来查看你的参数是否在整个范围内有效，或者你是否需要调整固定参数。

建议将宏和调整塔配置参数放在它们自己的 `testing_macros.cfg` 文件中。

根据你的机器参数设置 `[pa_test]` 部分。
通常保持尺寸和高度不变。
将原点放在你想要塔中心的位置。

将中等和快速速度设置在你想要的附近。
对于 300mm/s 的打印机，将 `fast_velocity` 设置为 300，`medium_velocity` 设置为 100。
最好将慢速速度保持在 20，以便更好地探测悬垂面和接缝附近的速度。

在 `[delayed_gcode start_pa_test]` 部分中，放入你的启动 gcode（无论是单个 `print_start` 宏还是单独的 gcode 调用序列）。

如果你需要更大的调整塔范围，请调整相应参数的 `FACTOR`。

```
[pa_test]
size_x: 100   # X 维度塔尺寸（mm）
size_y: 50    # Y 维度塔尺寸（mm）
height: 50    # 塔高度（mm）
origin_x: 100 # 热床 X 方向中心
origin_y: 100 # 热床 Y 方向中心
layer_height: 0.2 # mm
first_layer_height: 0.24 # mm
perimeters: 2 # 塔要打印的周长数量
brim_width: 6 # 边缘宽度（mm）
slow_velocity:   20 # PA 测试段最慢速度（mm/s）
medium_velocity: 50 # PA 测试段中等速度（mm/s）
fast_velocity:  150 # PA 测试段结束速度（mm/s）
filament_diameter: 1.75
fan_speed: 0.5 # 打印边缘后应用的风扇速度

[delayed_gcode start_pa_test]
gcode:
    {% set vars = printer["gcode_macro RUN_PA_TEST"] %}
    ; 在此放置你的启动 gcode========================================================
    {% set flow_percent = vars.flow_rate|float * 100.0 %}
    {% if flow_percent > 0 %}
        M221 S{flow_percent}
    {% endif %}
    {% set height = printer.configfile.settings.pa_test.height %}
    {% set pavalue = vars.pa_value %}
    ; 如果 pa_value 为 0，则从 0 开始测试完整的 pa 范围
    {% if  vars.pa_value == 0 %}
        {% if vars.testparam == 0 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.001 ; 鲍登为 .01
        {% elif vars.testparam == 1 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=OFFSET START=0 FACTOR=.01 ; 鲍登为 .02
        {% elif vars.testparam == 2 %}
            TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=TIME_OFFSET START=0 FACTOR=.0001
        {% endif %}
    {% else %}
        ; 确保 delta 和 start 不能低于 0
        {% if (vars.pa_value - vars.pa_range <= 0) and (vars.testparam <= 2) %}
            {% set delta = vars.pa_range %}
            {% set start = 0 %}
        {% else %}
            ; 计算我们要测试的 pa 范围
            {% set delta = (vars.pa_value + vars.pa_range)  - (vars.pa_value - vars.pa_range)  %}
            ; 计算 pa 起始值
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
    ; 它会开始打印，然后立即返回而不等待打印完成
    PRINT_PA_TOWER {vars.rawparams} FINAL_GCODE_ID=end_pa_test

[delayed_gcode end_pa_test]
gcode:
    END_PRINT
    RESTORE_GCODE_STATE NAME=PA_TEST_STATE

[gcode_macro RUN_PA_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_pa_value: 0             # 用于进一步调整 pa 值。如果值不为 0，则测试的 pa 值将仅在 pa_value 变量周围 +/-（由 pa_range 变量确定）
variable_pa_range: 0.03          # 仅在 pa_value 设置为大于 0 时使用。用于设置应在 pa_value 周围测试的 +/- 区域
variable_flow_rate: -1
variable_testparam: 0            # 0 = advance，1 = offset，2 = time_offset
variable_fan_speed: 0.5
variable_rawparams: ''
gcode:
    # 如果未提供必需参数则提前失败
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

***重要提示***

PA 测试宏将以你 `printer.cfg` 中 `[printer]` 部分指定的加速度运行。
将其设置为挤出时（例如填充）预期使用的最高加速度。

### 通过 G-Code 设置值

要在运行时更改非线性 PA，无论是在打印机命令行中还是在你的切片器耗材设置中，使用 `SET_PRESSURE_ADVANCE` 命令及以下参数：

* `ADVANCE=` linear_advance
* `OFFSET=` nonlinear_offset
* `VELOCITY=` linearization_velocity
* `TIME_OFFSET=` pressure_advance_time_offset

## 调整程序

对于以偏移量为主的普通打印机，调整程序将与具有更多线性推进分量的超高速打印机或具有较大值的鲍登管打印机略有不同。

在评估 PA 测试宏生成的调整塔时，从极左或极右侧使用强光照射会很有帮助。

### 直驱，低到中等性能

1. 安装 Kalico 并确保使用 `bleeding-edge-v2` 分支。
2. 按照设置部分的说明设置 PA 测试宏，并确保在 `[printer]` 中设置所需的加速度。
3. 如果你计划使用输入整形，请设置输入整形。它会影响调整塔的可读性。使用 `enabled_extruders: extruder` 设置挤出机同步。
4. 在你的打印机配置中，将 `pressure_advance_model` 设置为 `tanh`，`linear_advance` 设置为 0，`nonlinear_offset` 设置为 0，`linearization_velocity` 设置为 1，`pressure_advance_smooth_time` 设置为 0.02。重启打印机以加载新设置。
5. 运行 pa 测试宏，将 `NOZZLE` 设置为你的喷嘴直径，`TARGET_TEMP` 设置为你预期的热端温度，`TESTPARAM` 设置为 1 以改变 `nonlinear_offset`。
6. 评估塔，主要查看左侧。根据那里看起来最好的高度（以及测试宏代码中的 `factor`）在打印机配置中设置 `nonlinear_offset`，然后重启。
7. 运行 PA 测试宏，使用你的喷嘴直径、预期的热端温度和 `TESTPARAM` 为 0 以改变 `linear_advance`。
8. 评估塔，主要查看左侧和前侧，并进行二分查找以找到最佳偏移量和推进量。
    1. 如果左侧收敛于前侧下方，则在配置中略微减小（从 10% 开始，如果超出则减少）`nonlinear_offset`，重启，并使用 `TESTPARAM` 0 重新打印 PA 测试宏。
    2. 如果左侧收敛于前侧上方，则在配置中略微增加（从 10% 开始，如果超出则减少）`nonlinear_offset`，重启，并使用 `TESTPARAM` 0 重新打印 PA 测试宏。
    3. 如果左侧和前侧在同一高度收敛，则使用该高度和测试宏代码中的 `factor` 在打印机配置中设置 `linear_advance`，然后重启。
9. 运行 PA 测试宏，使用你的喷嘴直径、预期的热端温度和 `TESTPARAM` 为 2 以改变 `pressure_advance_time_offset`。
10. 评估塔，主要查看前侧。这可能*非常*微妙，因此请确保使用良好的光照来揭示差异。根据那里看起来最好的高度和测试宏代码中的 `factor` 在你的配置中设置 `pressure_advance_time_offset`，然后重启。

### 鲍登或超高速直驱打印机

确保为鲍登打印机调整 PA 测试宏中的因子。

1. 安装 Kalico 并确保使用 `bleeding-edge-v2` 分支。
2. 按照设置部分的说明设置 PA 测试宏，并确保在 `[printer]` 中设置所需的加速度。
3. 如果你计划使用输入整形，请设置输入整形。它会影响调整塔的可读性。使用 `enabled_extruders: extruder` 设置挤出机同步。
4. 在你的打印机配置中，将 `pressure_advance_model` 设置为 `tanh`，`linear_advance` 设置为 0，`nonlinear_offset` 设置为 0，`linearization_velocity` 设置为 1（鲍登为 2 或可能为 3，其中高加速度加上大 PA 值可能导致挤出机加速度要求过高，而低线性化速度），`pressure_advance_smooth_time` 设置为 0.02。重启打印机以加载新设置。
5. 运行 PA 测试宏，将 `NOZZLE` 设置为你的喷嘴直径，`TARGET_TEMP` 设置为你预期的热端温度，`TESTPARAM` 设置为 0 以改变 `linear_advance`。
6. 评估塔，主要查看前侧。根据那里看起来最好的高度和测试宏代码中的 `factor` 评估理想的 `linear_advance`，记下该值，但将配置设置为该值的 80%，然后重启。
7. 运行 PA 测试宏，使用你的喷嘴直径、预期的热端温度和 `TESTPARAM` 为 1 以改变 `nonlinear_offset`。
8. 评估塔，主要查看左侧和前侧，并进行二分查找以找到最佳偏移量和推进量。
    1. 如果左侧收敛于前侧下方，则在配置中略微增加（从 10% 开始，如果超出则减少）`linear_advance`，重启，并使用 `TESTPARAM` 1 重新打印 PA 测试宏。
    2. 如果左侧收敛于前侧上方，则在配置中略微减小（从 10% 开始，如果超出则减少）`linear_advance`，重启，并使用 `TESTPARAM` 1 重新打印 PA 测试宏。
    3. 如果左侧和前侧在同一高度收敛，则使用该高度和测试宏代码中的 `factor` 在打印机配置中设置 `nonlinear_offset`，然后重启。
9. 运行 PA 测试宏，使用你的喷嘴直径、预期的热端温度和 `TESTPARAM` 为 2 以改变 `pressure_advance_time_offset`。
10. 评估塔，主要查看前侧。这可能*非常*微妙，因此请确保使用良好的光照来揭示差异。根据那里看起来最好的高度和测试宏代码中的 `factor` 在你的配置中设置 `pressure_advance_time_offset`，然后重启。
11. 再次运行 PA 测试宏，`TESTPARAM` 为 1，并使用步骤 8 中的程序再次微调你的设置。

### SV06 Plus 示例

这是在 Sovol SV06 Plus（配备标准火山长度热端和略长的喷嘴尖端）上使用标准 PLA 在 215 C 下以 150mm/s 和 5k 加速度调整非线性 PA 的示例。

首先使用测试参数 0 打印 PA 测试塔，并根据前侧速度过渡设置 `linear_advance`。
在这种情况下，`linear_advance` 为 0.04。

![线性推进测试塔](/img/PA_photos/0.advance=x.001.jpg)

接下来，打印振铃测试塔以设置整形器，因为没有热床加速度计。启用挤出机同步。
打印另一个振铃测试塔以检查振铃是否被抑制。

`linear_advance` 设置回零，`linearization_velocity` 设置为 1，`pressure_advance_smooth_time` 设置为 0.02，`pressure_advance_time_offset` 设置为 0。
然后使用测试参数 1 打印 PA 测试塔。

![线性偏移测试塔](/img/PA_photos/1.offset=x.005.jpg)

在这种情况下，左侧在大约 27mm \* 0.005 处看起来最好，因此 `nonlinear_offset` 初始设置为 0.135，并使用测试参数 0 打印 PA 测试塔。

![具有 0.135 线性偏移的线性推进测试塔](/img/PA_photos/2.offset=.135_advance=x.001.jpg)

在此测试中，左侧收敛于最底部，但右侧收敛于其上方，因此 `nonlinear_offset` 略微减小至 0.120。
回想起来，查看之前 `nonlinear_offset` 的测试塔，左侧的左线在 24mm 处刚刚开始出现"粗-细"模式，右线仅略微欠补偿。
通常，初始 `nonlinear_offset` 最好略微欠补偿，因为即使在低速下 `linear_advance` 也会提供一点提升。

将 `nonlinear_offset` 减小到 0.120 后，使用测试参数 0 打印了另一个测试塔。

![具有 0.120 线性偏移的线性推进测试塔](/img/PA_photos/3.offset=.120_advance=x.001.jpg)

这显示左侧和前侧在 17mm \* 0.001 处良好收敛，因此理想的 `linear_advance` 为 0.017，无需进一步调整 `nonlinear_offset`。

仅作为演示，以下是当使用测试参数 0 打印测试塔时，`nonlinear_offset` 轻微过度补偿至 0.100 的样子：

![具有 0.100 线性偏移的线性推进测试塔](/img/PA_photos/4.offset=.100_advance=x.001.jpg)

这并不那么明显，但左侧收敛于测试塔前侧的稍高位置。如果你看到这种情况，你会略微增加 `nonlinear_offset` 并重新测试。

最后调整时间偏移以正确对齐压力推进补偿与实际工具头运动。

最后一个调整塔使用打印机设置为 0.120 线性偏移、0.017 线性推进，并将宏的测试参数设置为 2 进行打印。

![时间偏移测试塔](/img/PA_photos/5.time_offset=x.0001.jpg)

这更难看出效果，但极端的侧面光照显示前表面上最左侧和最右侧的过渡受益于 18mm \* 0.0001 的高度，表明 `pressure_advance_time_offset` 应设置为 0.0018。这意味着压力推进应提前 1.8 毫秒发生，以最好地同步流量与工具头运动。

### 性能比较

这是使用三种不同线性 PA（无时间偏移）与非线性调整打印的 Voron 测试立方体的比较。

周长以适度的 3000 mm/s^2 加速度打印以获得最大质量，但即使如此，差异也是可见的。
在更高加速度下，差异将更加明显。

此外，此比较不与主分支或原版 Klipper 进行比较，后者没有将挤出机与输入整形同步。

![压力推进的校准立方体比较](/img/PA_photos/voroncube.jpg)

从左到右的列是：侧光照底部、侧光照 Y、顶光照 Y、侧光照 X、顶光照 X，以及立方体顶部正光照。

在底部，0.025 线性 PA 在 ESE 拐角处有明显的凸起，而其他显示差异很小。

在侧光照 Y 面上，你可以看到所有三个线性 PA 在六边形的侧面和顶面周围都有深色轮廓，这些位置有轻微的凹陷区域。
它们还在悬垂拐角附近明显凸出，线性 PA 在悬垂打印的低速下补偿不足。
相比之下，非线性 PA 的表面极其平坦。

在顶光照下，很容易看出非线性 PA 在六边形顶面的凸起要小得多。

侧光照 X 面显示非线性测试立方体上槽口周围的表面要平坦得多，而线性测试立方体在槽口右侧显示阴影区域。

在顶光照下，0.04 和 0.03 线性 PA 在每个槽口后略微延迟出现大凸起，在下方投下阴影。
0.025 线性 PA 在每个槽口顶部后显示小凹陷，可能是从非常慢的桥接速度到墙壁速度过渡的结果。
非线性 PA 表现出类似的效果，但程度要小得多。

俯视图说明 0.03 已经是太多的线性 PA，无法在拐角周围保持完全挤出。
0.04 线性在周长线之间有大间隙，并且开始在实心填充线的末端出现空隙。
非线性和 0.025 线性都能在拐角周围完全挤出。
