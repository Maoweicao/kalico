# 前沿功能文档

以下是在 Kalico 前沿分支中发现的实验性功能，使用时请自行谨慎。这些功能的支持有限，您的体验可能有所不同！如果您确实使用了这些功能并发现它们有用，发现了错误或有改进建议，请使用 Kalico [Discord 服务器](Contact.md#discord)讨论您的发现。

有关这些功能的打印机配置详情，请参阅[前沿配置参考](Config_Reference_Bleeding_Edge.md)。

## 高精度步进和新的步进压缩协议

此功能的参考讨论：https://klipper.discourse.group/t/improved-stepcompress-implementation/3203

### 概述

新的步进压缩协议和精密步进功能是对步进电机运动控制和精度的改进提议。该功能增强了步进压缩算法，这对于准确传输步进命令至关重要。

### 现有步进压缩机制

- **过程**：最初，迭代求解器根据运动和运动学生成步进时序。然后压缩这些步进进行传输，MCU 执行压缩后的步进。
- **标准压缩**：使用的压缩格式为 step[i] = step[0] + interval _ i + add _ i * (i-1) / 2。仅传输 interval、add 和 count，这使得这是一种有损压缩，每个步进相对于真实步进落在特定范围内。

### 当前方法的局限性

- **系统性伪影**：现有方法在加速曲线中引入系统性伪影，特别是在不同速度的交界处。
- **近似限制**：当前压缩实际上仅使用泰勒级数展开的第一项，导致步进时序不准确。

### 改进的步进压缩方案

- **新格式**：改进的公式为 step[i] = step[0] + (interval _ i + add _ i _ (i-1) / 2 + add2 _ i _ (i-1) _ (i-2) / 6) >> shift。这为泰勒展开添加了第二项，并采用定点算术以获得更高的精度。
- **实现**：在实现时考虑了舍入和余数，从而与实际步进时序更精确地匹配。

### 新方法的优点

- **减小误差范围**：新方法将误差范围减小到真实步进的约 +/- 1.5%。
- **平滑加速曲线**：确保更平滑的加速曲线，可能使输入整形更有效并减少振动伪影。

### 计算考虑

- **计算需求增加**：新协议计算量更大，并增加了传输到 MCU 的数据量。
- **性能影响**：虽然在大多数情况下保持了高速性能，但在功能较弱的 MCU 上最大可实现速度可能会略有降低。这种降低粗略估计比当前步进压缩算法慢 20-40%。
- **推荐硬件**：RPIv4 或能够使用当前步进压缩算法处理 1M+ 步进/秒的类似硬件。

### 实际测试和结果

- **基准测试和测试**：进行了各种测试，包括高速打印复杂形状，以评估新步进压缩方法的实际影响。
- **不同硬件上的性能**：性能影响因 MCU 而异，对 32 位 MCU 影响最小，对 8 位 MCU 影响更大。
- **电机反电动势考虑**：对于在给定电源电压下以最高速度运行的电机，此方法可能不会提供太多优势。Eddietheengineer 在[此处](https://www.youtube.com/watch?v=4Z2FBA_cBoE&t=1s)已经证明，当电机反电动势接近电源电压时，步进电流失真。由于步进电机驱动器无法再准确地将电流推入电机，因此精确步进变得不那么重要。

## 平滑输入整形器

此功能的参考讨论：https://klipper.discourse.group/t/scurve-pa-branch/7621/3

### 概述

平滑输入整形器功能采用多项式平滑函数，旨在在某些频率下消除振动，类似于常规输入整形器。该目标是提供具有一些更好整体特性的整形器。

### 主要特点

- **多项式平滑函数**：与传统的离散输入整形器不同，平滑输入整形器使用多项式平滑函数来更有效地平滑工具头运动。
- **类似于 S 曲线加速**：提供类似于 S 曲线加速的加速曲线，但具有固定的时间而不是跨越整个加速/减速阶段，并且配置文件形状专门设计用于消除某些频率下的振动。

- **挤出机优势**：挤出机与压力推进的性能更好。挤出机与输入整形同步。

- **提高有效性**：通常比相应的离散输入整形器更有效，提供稍微多一点的平滑处理。

### 可用的平滑整形器

- **smooth_zv** - zv 输入整形器的平滑版本
- **smooth_mzv** - mzv 输入整形器的平滑版本
- **smooth_ei** - ei 输入整形器的平滑版本
- **smooth_2hump_ei** - 2hump_ei 输入整形器的平滑版本
- **smooth_zvd_ei** - 零振动导数 - 额外不敏感的平滑整形器 _（文档和用例目前有限）_
- **smooth_si** - 超级不敏感平滑整形器 _（文档和用例目前有限）_

### 自定义平滑整形器

- 可以定义和使用自定义平滑整形器。 _（文档和用例目前有限）_

### 硬件要求

- **计算强度**：此功能在计算上要求更高。用户在实施此功能时应考虑其硬件和系统的能力。

- **最低硬件**：Raspberry Pi 3 是所需的最低硬件。它在 Ender 3 上有效地运行，在 Raspberry Pi 3B+ 上速度最高可达约 250 mm/sec，使用 127 个微步。

- **理想硬件**：建议使用 Raspberry Pi 4 或 Orange Pi 4 以获得最佳性能。

### 配置和使用

- **配置**：配置类似于常规输入整形器，但参数上有一些差异。
- **smoother*freq*? 参数**：此参数不完全对应于当前主线 Klipper 输入整形器设置。它表示平滑器取消的最小频率，或者更准确地说，它取消的极点的最小频率。此区别对于 smooth_ei 和 smooth_2hump_ei 整形器尤其相关。

- **校准支持**：scripts/calibrate_shapers.py 自动支持校准和概览可用的平滑器，无需额外的用户输入。

## 挤出机 PA 与输入整形同步

此功能的参考讨论：https://klipper.discourse.group/t/extruder-pa-synchronization-with-input-shaping/3843

### 概述

挤出机 PA 与输入整形同步功能将耗材挤出（压力推进 - PA）与工具头的运动同步。这种同步旨在通过补偿工具头运动的变化来减少伪影，特别是在使用输入整形来最小化振动和振铃的场景中。

### 背景

输入整形是用于改变工具头运动以减少振动的技术。虽然 Klipper 现有的压力推进算法有助于将耗材挤出与工具头运动同步，但它并未与输入整形更改完全对齐。这种不对齐在 X 和 Y 轴具有不同的共振频率，或者 PA 平滑时间显著偏离输入整形器持续时间的场景中可能特别明显。

### 实现

该功能涉及：

1. 计算 X、Y 和 Z 轴上的工具头运动。
2. 对 X 和 Y 轴应用输入整形。
3. 使用线性化将此运动投影到 E（挤出机）轴上。

如果输入整形器对 X 和 Y 轴一致，则对 XY 运动的同步是精确的。在其他情况下，该功能提供对 X/Y 偏差的线性近似，这是对以前状态的改进。

### 观察和改进

- **挤出运动**：实现显示在挤出运动期间 PA 的行为不那么不稳定，回抽和反回抽更少。
- **稳定的挤出机速度**：挤出机速度变得更加稳定，反映了由于输入整形而更稳定的工具头速度。
- **擦拭行为**：改进的擦拭行为，具有更一致的回抽速度。

### 硬件要求

- **计算强度**：此功能在计算上要求更高。用户在实施此功能并监控任何问题时应考虑其硬件和系统的能力。

### 测试和结果

该功能已经过数月的测试，在实际打印质量上显示出适度的改善。它对于具有短耗材路径的直驱挤出机特别有效。对鲍登挤出机的影响预计是中性的。

### 使用建议

- **重新调整 PA**：使用此分支时建议重新调整压力推进设置。具体来说，对于使用非柔性耗材的直驱挤出机，建议将 pressure_advance_smooth_time 从默认的 0.04 减小到大约 0.02 或 0.01。
- **需要监控的区域**：注意工具头速度变化的区域，例如拐角、桥接和填充与周长的连接处，以观察质量的改善或退化。

## 振铃塔测试打印

此功能的参考讨论：https://klipper.discourse.group/t/alternative-ringing-tower-print-for-input-shaping-calibration/4517

### 概述

用于输入整形器校准的新测试方法解决了现有振铃塔测试的一个关键限制。此改进的核心是在校准过程中隔离每个轴上的振动，从而提供更准确和可靠的结果。

![振铃塔立方体](/img/ringing_tower_cube.jpg)

### 当前振铃塔测试的限制

- **同时轴运动**：当前的振铃塔测试由于不可避免的对角线移动而改变了两个轴的速度，导致振动测量可能存在干扰。
- **寄生波**：测试可能会产生寄生波，使得难以准确测量共振频率，特别是当一个轴比另一个轴振动更大时。

### 新测试方法概念

- **隔离轴振动**：新测试旨在一次仅在一个轴上激发振动，从而克服干扰问题。
- **GCode 生成要求**：此测试需要直接生成 GCode，重点关注轴的受控加速和减速。
- **初始加速**：两个轴在对角线移动期间加速。
  被测轴减速：仅被测轴减速至完全停止，而另一个保持其原始速度。
- **浮雕轴字母**：测试在侧面包含浮雕字母，指示应进行测量的位置。这些字母还用作校准后平滑幅度的指示器。

### 优点

- **可靠的校准**：通过测量特定测试区域中的波距离和数量，允许更可靠的输入整形器校准。
- **多功能性**：虽然主要在 Ender 3 Pro 上进行了测试，但该方法适用于不同类型的打印机，如 CoreXY 或 Delta。

### 考虑事项

- **与加速度计数据的比较**：由于每个轴上的多个共振，结果可能无法与加速度计数据完全对应，但它们仍然有效，特别是对于 EI 输入整形器。
- **确认加速度计校准**：此测试是确认基于加速度计的校准结果的宝贵工具。
- **用户特定配置**：鼓励用户将其特定配置（例如，加热、归位、床网格）添加到启动 GCode 序列中。

### 示例运行命令：

请注意，不建议在未配置辅助宏的情况下直接运行命令。

_RUN_RINGING_TEST NOZZLE=0.4 TARGET_TEMP=210 BED_TEMP=55._

### 示例辅助宏

此示例 Gcode 可以包含在 **printer.cfg** 或单独的 **\*.cfg** 文件中，并 #included 在 **printer.cfg** 中。应添加打印机的特定启动/结束打印 Gcode，以确保它与标准打印过程对齐，例如适当的加热、归位和床网格序列，以及启用风扇、额外的清洗线、压力推进设置或调整流速等附加功能。

```
[ringing_test]

[delayed_gcode start_ringing_test]

gcode:
    {% set vars = printer["gcode_macro RUN_RINGING_TEST"] %}
    # 在此添加你的启动 GCode，例如：
    # G28
    # M190 S{vars.bed_temp}
    # M109 S{vars.hotend_temp}
    # M106 S255
    {% set flow_percent = vars.flow_rate|float * 100.0 %}
    {% if flow_percent > 0 %}
    M221 S{flow_percent}
    {% endif %}
    {% set layer_height = vars.nozzle * 0.5 %}
    {% set first_layer_height = layer_height * 1.25 %}
    PRINT_RINGING_TOWER {vars.rawparams} LAYER_HEIGHT={layer_height} FIRST_LAYER_HEIGHT={first_layer_height} FINAL_GCODE_ID=end_ringing_test

[delayed_gcode end_ringing_test]
gcode:
    # 在此添加你的结束 GCode，例如：
    # M104 S0 ; 关闭温度
    # M140 S0 ; 关闭热床
    # M107 ; 关闭风扇
    # G91 ; 相对定位
    # G1 Z5 ; 抬高 Z
    # G90 ; 绝对定位
    # G1 X0 Y200 ; 展示打印
    # M84 ; 禁用步进电机
    RESTORE_GCODE_STATE NAME=RINGING_TEST_STATE

[gcode_macro RUN_RINGING_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_nozzle: -1
variable_flow_rate: -1
variable_rawparams: ''
gcode:
    # 如果未提供必需参数则提前失败
    {% if params.NOZZLE is not defined %}
    {action_raise_error('必须提供 NOZZLE= 参数')}
    {% endif %}
    {% if params.TARGET_TEMP is not defined %}
    {action_raise_error('必须提供 TARGET_TEMP= 参数')}
    {% endif %}
    SET_GCODE_VARIABLE MACRO=RUN_RINGING_TEST VARIABLE=bed_temp VALUE={params.BED_TEMP|default(60)}
    SET_GCODE_VARIABLE MACRO=RUN_RINGING_TEST VARIABLE=hotend_temp VALUE={params.TARGET_TEMP}
    SET_GCODE_VARIABLE MACRO=RUN_RINGING_TEST VARIABLE=nozzle VALUE={params.NOZZLE}
    SET_GCODE_VARIABLE MACRO=RUN_RINGING_TEST VARIABLE=flow_rate VALUE={params.FLOW_RATE|default(-1)}
    SET_GCODE_VARIABLE MACRO=RUN_RINGING_TEST VARIABLE=rawparams VALUE="'{rawparams}'"
    SAVE_GCODE_STATE NAME=RINGING_TEST_STATE
    UPDATE_DELAYED_GCODE ID=start_ringing_test DURATION=0.01
```

## PA 塔测试打印

此功能的参考讨论：https://klipper.discourse.group/t/extruder-pa-synchronization-with-input-shaping/3843/27

### 概述

该功能引入了一个新模块，用于直接从固件打印压力推进（PA）校准塔。该模块简化了校准 PA 设置的过程，增强了调整最佳打印质量的精度和便利性。

![PA 塔注释](/img/pa_tower_annotated.jpg)

### 主要特点

- **集成 PA 测试打印**：允许用户直接从 Klipper 打印 PA 校准塔，无需外部 GCode 生成。
- **可配置参数**：设置了默认参数，但用户可以覆盖这些参数或添加具体参数，如 NOZZLE 尺寸和 TARGET_TEMP。
- **速度过渡**：在测试图案中创建多个速度过渡，以可能根据这些过渡确定不同的最佳 PA。

### 配置

- **基本设置**：对于标准设置，只需在打印机配置中添加 [pa_test] 可能就足够了。
- **自定义选项**：用户可以在 printer.cfg 文件中覆盖参数或在 PRINT_PA_TOWER 命令中指定它们，例如 BRIM_WIDTH、NOZZLE 和 TARGET_TEMP。
- **关键参数**：NOZZLE 尺寸和 TARGET_TEMP 对于准确的 PA 测试至关重要，每次必须指定。
- **非标准运动学的手动定位**：对于具有非标准运动学（如极坐标或 Delta）的打印机，可能需要手动指定塔的位置和大小。

### 操作

- **启动打印的命令**：使用 PRINT_PA_TOWER 命令开始打印 PA 塔。
- **预热要求**：挤出机必须单独预热，因为 PRINT_PA_TOWER 不会加热挤出机。TARGET_TEMP 用于对配置的挤出机温度进行完整性检查。
- **与虚拟 SD 卡集成**：修改后的 virtual_sdcard 模块支持从虚拟 SD 卡以外的源进行打印，允许进度跟踪和标准打印控制命令，如 PAUSE、RESUME 和 CANCEL_PRINT。

### 相对于其他方法的优点

- **PA 值的平滑过渡**：与 Marlin 测试不同，Marlin 测试可能对第一层校准敏感且 PA 值测试有限，Klipper PA 塔允许 PA 值在层与层之间平滑过渡。
- **直接检查 PA**：此方法直接检查应应用 PA 的速度过渡，并且不会将 PA 与其他效果混合，例如由于输入整形导致的拐角平滑。用户在选择合适的 PA 值时不需要也不应该查看模型的拐角。
- **用户友好的校准**：此方法提供了一种更用户友好且不那么繁琐的微调 PA 值的方法。
- **速度测试范围**：最佳 PA 可能随加速度和速度而变化。理想的 PA 值可能特定于这些不同的速度过渡。

### 示例运行命令：

请注意，不建议在未配置辅助宏的情况下直接运行命令。

_RUN_PA_TEST NOZZLE=0.4 TARGET_TEMP=205 BED_TEMP=55_

### 示例辅助宏

此示例 Gcode 可以包含在 **printer.cfg** 或单独的 **\*.cfg** 文件中，并 #included 在 **printer.cfg** 中。应添加打印机的特定启动/结束打印 Gcode，以确保它与标准打印过程对齐，例如适当的加热、归位和床网格序列，以及启用风扇、额外的清洗线、压力推进设置或调整流速等附加功能。

```
[delayed_gcode start_pa_test]
gcode:
    {% set vars = printer["gcode_macro RUN_PA_TEST"] %}
    # 在此添加你的启动 GCode，例如：
    # G28
    # M190 S{vars.bed_temp}
    # M109 S{vars.hotend_temp}
    {% set flow_percent = vars.flow_rate|float * 100.0 %}
    {% if flow_percent > 0 %}
        M221 S{flow_percent}
    {% endif %}
    {% set height = printer.configfile.settings.pa_test.height %}  
    {% set pavalue = vars.pa_value %}
    ; 如果 pa_value 为 0，则从 0 开始测试完整的 pa 范围
    {% if  vars.pa_value == 0 %} 
        TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.005
    {% else %}
        ; 确保 delta 和 start 不能低于 0
        {% if vars.pa_value - vars.pa_range <= 0%} 
            {% set delta = vars.pa_range %}
            {% set start = 0 %}
        {% else %}
            ; 计算我们要测试的 pa 范围
            {% set delta = (vars.pa_value + vars.pa_range)  - (vars.pa_value - vars.pa_range)  %} 
            ; 计算 pa 起始值
            {% set start = vars.pa_value - vars.pa_range %} 
        {% endif %}
        TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START={start} FACTOR={delta / height}
    {% endif %}
    ; PRINT_PA_TOWER 必须是 start_pa_test 脚本中的最后一个命令：
    ; 它会开始打印，然后立即返回而不等待打印完成
    PRINT_PA_TOWER {vars.rawparams} FINAL_GCODE_ID=end_pa_test

[delayed_gcode end_pa_test]
gcode:
    # 在此添加你的结束 GCode，例如：
    # M104 S0 ; 关闭温度
    # M140 S0 ; 关闭热床
    # M107 ; 关闭风扇
    # G91 ; 相对定位
    # G1 Z5 ; 抬高 Z
    # G90 ; 绝对定位
    # G1 X0 Y200 ; 展示打印
    # M84 ; 禁用步进电机
    RESTORE_GCODE_STATE NAME=PA_TEST_STATE

[gcode_macro RUN_PA_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_pa_value: 0             # 用于进一步调整 pa 值。如果值不为 0，则测试的 pa 值将仅在 pa_value 变量周围 +/-（由 pa_range 变量确定）
variable_pa_range: 0.03          # 仅在 pa_value 设置为大于 0 时使用。用于设置应在 pa_value 周围测试的 +/- 区域
variable_flow_rate: -1
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
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=rawparams VALUE="'{rawparams}'"
    SAVE_GCODE_STATE NAME=PA_TEST_STATE
    UPDATE_DELAYED_GCODE ID=start_pa_test DURATION=0.01
```

## 非线性压力推进

完整文档请参阅此处：[非线性压力推进](Nonlinear_Pressure_Advance.md)

### 概述

标准线性压力推进有时无法在不导致线条变细的情况下完全防止拐角凸起，并且最佳设置会随速度和加速度而变化。
此功能实现了推进和耗材进料速率之间的非线性关系，改善了这些方面。

### 优点：

* 提高打印质量
* 设置与速度和加速度的依赖性更小。

### 考虑事项：

* 多个相互作用的参数使调整更加耗时。
* 对于一些极快的打印机，请求的挤出机速度和加速度可能导致跳步。
