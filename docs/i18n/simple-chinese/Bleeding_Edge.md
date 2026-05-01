# 前沿功能文档

以下是 Kalico 前沿分支中的实验性功能，应谨慎使用。对这些功能的支持是有限的，您的体验可能会有所不同！如果您确实使用这些功能并发现它们有用、发现错误或有改进，请使用 Kalico [Discord 服务器](Contact.md#discord) 来讨论您的发现。

有关这些功能的打印机配置详情，请参阅 [前沿配置参考](Config_Reference_Bleeding_Edge.md)。

## 高精度步进和新的步进压缩协议

此功能的参考讨论：https://klipper.discourse.group/t/improved-stepcompress-implementation/3203

### 概述

新的步进压缩协议和精密步进功能是对步进电机运动的控制和精度的改进提案。此功能增强了步进压缩算法，这对于准确传输步进命令至关重要。

### 现有步进压缩机制

- **流程**：首先，迭代求解器根据运动和运动学生成步进时序。然后这些步进被压缩以进行传输，MCU 执行压缩的步进。
- **标准压缩**：用于压缩的格式是 step[i] = step[0] + interval * i + add * i * (i-1) / 2。仅传输 interval、add 和 count，使其成为有损压缩，相对于真实步进，每个步进都在特定范围内。

### 当前方法的局限性

- **系统性伪影**：现有方法在加速度曲线中引入系统性伪影，特别是在不同速度的交接处。
- **近似限制**：当前压缩有效地仅使用泰勒级数展开的第一项，导致步进时序不准确。

### 改进的步进压缩模式

- **新格式**：改进的公式是 step[i] = step[0] + (interval * i + add * i * (i-1) / 2 + add2 * i * (i-1) * (i-2) / 6) >> shift。这将第二项添加到泰勒展开中，并采用定点算术以获得更高精度。
- **实现**：考虑舍入和余数的实现，导致与实际步进时序的更精确匹配。

### 新方法的优势

- **误差范围降低**：新方法将误差范围降低到约 ±1.5% 的真实步进。
- **平顺加速度曲线**：确保平顺的加速度曲线，可能使输入整形更有效并减少振动伪影。

### 计算考虑

- **计算需求增加**：新协议的计算量更大，增加了传输到 MCU 的数据量。
- **性能影响**：虽然在大多数情况下高速性能得到保持，但在性能较弱的 MCU 上，最高可达成速度可能会略微降低。这种降低大致估计为比当前步进压缩算法低 20-40%。
- **推荐硬件**：RPIv4 或类似硬件，能够使用当前步进压缩算法处理 1M+ 步/秒。

### 真实测试和结果

- **基准测试和测试**：进行了各种测试，包括以高速打印复杂形状，以评估新步进压缩方法的实际影响。
- **不同硬件上的性能**：性能影响因 MCU 而异，对 32 位 MCU 影响最小，对 8 位 MCU 影响更大。
- **电动势考虑**：对于在给定电源电压下以最高速度运行的电动机，此方法可能不会提供太多优势。已由 Eddietheengineer {https://www.youtube.com/watch?v=4Z2FBA_cBoE&t=1s} 证明，当电动机反电动势接近 PSU 电压时，步进电流会失真。准确的步进变得不那么关键，因为步进电机驱动器无法再准确地将电流推入电动机。

## 平顺输入整形器（Smooth Input Shapers）

此功能的参考讨论：https://klipper.discourse.group/t/scurve-pa-branch/7621/3

### 概述

平顺输入整形器功能采用多项式平顺函数，设计用于在某些频率处消除振动，类似于常规输入整形器。该功能旨在提供具有某些更好整体特性的整形器。

### 主要功能

- **多项式平顺函数**：与传统的离散输入整形器不同，平顺输入整形器使用多项式平顺函数来更有效地平顺工具头运动。
- **类似于 S 曲线加速**：提供类似于 S 曲线加速的加速度曲线，但具有固定的时序而不是跨越整个加速/减速阶段，并且轮廓形状特别设计用于在某些频率处消除振动。

- **挤出机优点**：挤出机与压力推进的更好性能。挤出机与输入整形的同步。

- **改进的效果**：通常比对应的离散输入整形器更有效，提供稍微更多的平顺。

### 可用的平顺整形器

- **smooth_zv** - zv 输入整形器的平顺版本
- **smooth_mzv** - mzv 输入整形器的平顺版本
- **smooth_ei** - ei 输入整形器的平顺版本
- **smooth_2hump_ei** - 2hump_ei 输入整形器的平顺版本
- **smooth_zvd_ei** - 零振动导数 - 额外不敏感平顺整形器 _(文档和用例目前有限)_
- **smooth_si** - 超级不敏感平顺整形器 _(文档和用例目前有限)_

### 自定义平顺整形器

- 可以定义和使用自定义平顺整形器。_(文档和用例目前有限)_

### 硬件要求

- **计算强度**：此功能的计算需求更大。用户在实现此功能时应考虑其硬件和系统的功能。

- **最低硬件**：Raspberry Pi 3 是最低需要的硬件。在 Raspberry Pi 3B+ 上，它可以在 Ender 3 上有效运行，速度高达约 250 毫米/秒，具有 127 微步。

- **理想硬件**：建议使用 Raspberry Pi 4 或 Orange Pi 4 以获得最佳性能。

### 配置和用法

- **配置**：配置与常规输入整形器类似，但参数有一些区别。
- **平顺器频率参数**：此参数与当前主线 Klipper 输入整形器设置不完全对应。它表示平顺器取消或更准确地说是其取消的极点的最小频率。这种区别对于 smooth_ei 和 smooth_2hump_ei 整形器特别相关。

- **校准支持**：scripts/calibrate_shapers.py 支持自动校准和可用平顺器的概述，无需额外的用户输入。

## 挤出机 PA 与输入整形的同步

此功能的参考讨论：https://klipper.discourse.group/t/extruder-pa-synchronization-with-input-shaping/3843

### 概述

挤出机 PA（压力推进）与输入整形同步功能将丝材挤出（压力推进 - PA）与工具头的运动同步。此同步旨在通过补偿工具头运动的变化来减少伪影，尤其是在采用输入整形来最小化振动和响铃的场景中。

### 背景

输入整形是一种用于改变工具头运动以减少振动的技术。虽然 Klipper 的现有压力推进算法有助于将丝材挤出与工具头运动同步，但它与输入整形改变不完全一致。这种不对齐在 X 和 Y 轴具有不同共振频率的场景中特别明显，或者 PA 平顺时间与输入整形器持续时间显著偏离。

### 实现

该功能涉及：

1. 计算 X、Y 和 Z 轴上的工具头运动。
2. 对 X 和 Y 轴应用输入整形。
3. 使用线性化将此运动投影到 E（挤出机）轴。

如果输入整形器对于 X 和 Y 轴是一致的，则 XY 运动的同步是精确的。在其他情况下，该功能在 X/Y 偏差上提供线性近似，这是对先前状态的改进。

### 观察和改进

- **挤出运动**：实现在 PA 挤出运动期间显示较少的不规则行为，缩回和解缩回较少。
- **稳定的挤出机速度**：由于输入整形导致的工具头速度更稳定，挤出机速度变得更稳定。
- **擦拭行为**：改进的擦拭行为，具有更一致的缩回速度。

### 硬件要求

- **计算强度**：此功能的计算需求更大。用户在实现此功能时应考虑其硬件和系统的功能，并监控任何问题。

### 测试和结果

该功能已测试数月，显示实际打印质量的适度改进。它对直接驱动挤出机特别有效，具有较短的丝材路径。对于 Bowden 挤出机的影响预期是中性的。

### 使用建议

- **重新调整 PA**：建议在使用此分支时重新调整压力推进设置。具体来说，对于使用非柔性丝材的直接驱动挤出机，建议将 pressure_advance_smooth_time 从默认 0.04 降低到约 0.02 或 0.01。
- **监控领域**：注意工具头速度变化的领域，如转角、桥接和与周边的填充连接，以了解质量改进或降低。

## 响铃塔测试打印

此功能的参考讨论：https://klipper.discourse.group/t/alternative-ringing-tower-print-for-input-shaping-calibration/4517

### 概述

输入整形器校准的新测试方法解决了现有 ringing_tower 测试的一个关键限制。这种改进围绕在校准过程中隔离每个轴上的振动，从而提供更准确和可靠的结果。

![ringing_tower_cube](img/ringing_tower_cube.jpg)

### 当前响铃塔测试的局限性

- **同时轴运动**：当前的 ringing_tower 测试由于不可避免的对角线移动导致两个轴速度的改变，导致振动测量中的潜在干扰。
- **寄生波**：测试可能会产生寄生波，使得测量共振频率变得困难，特别是当一个轴的振动比另一个轴多得多时。

### 新测试方法学概念

- **隔离轴振动**：新测试被设计为一次仅在一个轴上激发振动，从而克服干扰问题。
- **GCode 生成要求**：此测试需要直接 GCode 生成，专注于轴的受控加速和减速。
- **初始加速度**：在对角线运动期间两个轴都加速。
  测试轴的减速：仅测试的轴减速到完全停止，而另一个保持其原始速度。
- **浮雕轴标签**：测试在边上包括浮雕字母，指示应在何处进行测量。这些字母还充当校准后平顺幅度的指示符。

### 优势

- **可靠的校准**：通过在特定测试区域中测量波距离和数字，允许更可靠的输入整形器校准。
- **多功能性**：虽然主要在 Ender 3 Pro 上测试过，但该方法可适应不同的打印机类型，如 CoreXY 或 Delta。

### 考虑

- **与加速度计数据比较**：由于每个轴上的多个共振，结果可能不会完全对应加速度计数据，但它们仍然有效，特别是使用 EI 输入整形器时。
- **加速度计校准的确认**：此测试是确认基于加速度计的校准结果的宝贵工具。
- **用户特定配置**：鼓励用户向起始 GCode 序列添加其特定配置（例如，加热、回位、床网格）。

### 示例运行命令：

注意，不建议在没有配置辅助宏的情况下直接运行该命令。

_RUN_RINGING_TEST NOZZLE=0.4 TARGET_TEMP=210 BED_TEMP=55._

### 示例辅助宏

此示例 Gcode 可以包含在 **printer.cfg** 或 **\*.cfg** 文件中并 #included 到 **printer.cfg**。应添加特定的开始/结束打印 Gcode 以确保其与标准打印过程一致，例如适当的加热、回位和床网格序列，以及其他功能，如启用风扇、额外的排出线、压力推进设置或调整流量。

```
[ringing_test]

[delayed_gcode start_ringing_test]

gcode:
    {% set vars = printer["gcode_macro RUN_RINGING_TEST"] %}
    # 在这里添加您的启动 GCode，例如：
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
    # 在这里添加您的结束 GCode，例如：
    # M104 S0 ; 关闭温度
    # M140 S0 ; 关闭热床
    # M107 ; 关闭风扇
    # G91 ; 相对定位
    # G1 Z5 ; 抬高 Z
    # G90 ; 绝对定位
    # G1 X0 Y200 ; 展示打印
    # M84 ; 禁用步进
    RESTORE_GCODE_STATE NAME=RINGING_TEST_STATE

[gcode_macro RUN_RINGING_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_nozzle: -1
variable_flow_rate: -1
variable_rawparams: ''
gcode:
    # 如果未提供所需参数，则尽早失败
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

该功能引入了一个新的模块，用于直接从固件打印压力推进（PA）校准塔。该模块简化了 PA 设置的校准过程，增强了最优打印质量调整的精度和便利性。

![pa_tower_annotated](img/pa_tower_annotated.jpg)

### 主要功能

- **集成 PA 测试打印**：允许用户直接从 Klipper 打印 PA 校准塔，绕过了外部 GCode 生成的需要。
- **可配置的参数**：设置了默认参数，但用户可以覆盖这些或添加具体内容，如喷嘴尺寸和目标温度。
- **速度转换**：在测试模式中创建多个速度转换，可能根据这些转换确定不同的最优 PA。

### 配置

- **基本设置**：简单地在打印机配置中添加 [pa_test] 可能对标准设置就足够了。
- **自定义选项**：用户可以在 printer.cfg 文件中覆盖参数或在 PRINT_PA_TOWER 命令中指定参数，如 BRIM_WIDTH、NOZZLE 和 TARGET_TEMP。
- **关键参数**：喷嘴尺寸和目标温度对准确的 PA 测试至关重要，每次都必须指定。
- **奇异运动学的手动定位**：对于具有非标准运动学的打印机（如极坐标或 Delta），可能需要手动指定塔的位置和大小。

### 操作

- **发起打印的命令**：使用 PRINT_PA_TOWER 命令开始打印 PA 塔。
- **预热要求**：挤出机必须单独预热，因为 PRINT_PA_TOWER 不会加热挤出机。目标温度用于对配置的挤出机温度进行完理性检查。
- **与虚拟 SD 卡集成**：修改后的 virtual_sdcard 模块支持从虚拟 SD 卡以外的源打印，允许进度跟踪和标准打印控制命令，如 PAUSE、RESUME 和 CANCEL_PRINT。

### 相比其他方法的优势

- **PA 值的平顺过渡**：与 Marlin 测试不同（对第一层校准敏感且 PA 值测试有限），Klipper PA 塔允许从层到层进行 PA 值的平顺过渡。
- **PA 的直接检查**：此方法直接检查应应用 PA 的速度转换，并不将 PA 与其他效果混合，如由输入整形导致的角平顺。用户不应该并且不应该在选择适当的 PA 值时查看模型的角。
- **用户友好的校准**：此方法提供了更用户友好和不那么麻烦的方法来微调 PA 值。
- **速度测试范围**：最优 PA 可能在加速和速度上有所不同。理想的 PA 值可能特定于这些不同的速度转换。

### 示例运行命令：

注意，不建议在没有配置辅助宏的情况下直接运行该命令。

_RUN_PA_TEST NOZZLE=0.4 TARGET_TEMP=205 BED_TEMP=55_

### 示例辅助宏

此示例 Gcode 可以包含在 **printer.cfg** 或 **\*.cfg** 文件中并 #included 到 **printer.cfg**。应添加特定的开始/结束打印 Gcode 以确保其与标准打印过程一致，例如适当的加热、回位和床网格序列，以及其他功能，如启用风扇、额外的排出线、压力推进设置或调整流量。

```
[delayed_gcode start_pa_test]
gcode:
    {% set vars = printer["gcode_macro RUN_PA_TEST"] %}
    # 在这里添加您的启动 GCode，例如：
    # G28
    # M190 S{vars.bed_temp}
    # M109 S{vars.hotend_temp}
    {% set flow_percent = vars.flow_rate|float * 100.0 %}
    {% if flow_percent > 0 %}
        M221 S{flow_percent}
    {% endif %}
    {% set height = printer.configfile.settings.pa_test.height %}  
    {% set pavalue = vars.pa_value %}
    ; 如果 pa_value 为 0，则我们测试从 0 开始的完整 pa 范围
    {% if  vars.pa_value == 0 %} 
        TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.005
    {% else %}
        ; 确保 delta 和 start 不能低于 0
        {% if vars.pa_value - vars.pa_range <= 0%} 
            {% set delta = vars.pa_range %}
            {% set start = 0 %}
        {% else %}
            ; 计算我们想测试的 pa 范围
            {% set delta = (vars.pa_value + vars.pa_range)  - (vars.pa_value - vars.pa_range)  %} 
            ; 计算 pa 开始值
            {% set start = vars.pa_value - vars.pa_range %} 
        {% endif %}
        TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START={start} FACTOR={delta / height}
    {% endif %}
    ; PRINT_PA_TOWER 必须是 start_pa_test 脚本中的最后一个命令：
    ; 它启动打印，然后立即返回而不等待打印完成
    PRINT_PA_TOWER {vars.rawparams} FINAL_GCODE_ID=end_pa_test

[delayed_gcode end_pa_test]
gcode:
    # 在这里添加您的结束 GCode，例如：
    # M104 S0 ; 关闭温度
    # M140 S0 ; 关闭热床
    # M107 ; 关闭风扇
    # G91 ; 相对定位
    # G1 Z5 ; 抬高 Z
    # G90 ; 绝对定位
    # G1 X0 Y200 ; 展示打印
    # M84 ; 禁用步进
    RESTORE_GCODE_STATE NAME=PA_TEST_STATE

[gcode_macro RUN_PA_TEST]
variable_bed_temp: -1
variable_hotend_temp: -1
variable_pa_value: 0             # 用于进一步微调 pa 值。如果值不为 0，则测试的 pa 值将仅为 +/-（由 pa_range 变量确定）pa_value 变量周围
variable_pa_range: 0.03          # 仅在 pa_value 设置为大于 0 时使用。用于设置应测试的 pa_value 周围的 +/- 区域
variable_flow_rate: -1
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
    SET_GCODE_VARIABLE MACRO=RUN_PA_TEST VARIABLE=rawparams VALUE="'{rawparams}'"
    SAVE_GCODE_STATE NAME=PA_TEST_STATE
    UPDATE_DELAYED_GCODE ID=start_pa_test DURATION=0.01
```

## 非线性压力推进

完整文档可在此处获得：[非线性压力推进](Nonlinear_Pressure_Advance.md)

### 概述

标准线性压力推进有时无法完全防止鼓起角，而不会导致变薄线条，最佳设置可能因速度和加速度而异。
此功能启用了推进和丝材流速之间的非线性关系，这改进了许多这些方面。

### 优势：

* 改进的打印质量
* 设置对速度和加速度的独立性更强。

### 考虑：

* 多个交互参数使调整变得更费时。
* 对于某些极高速打印机，要求的挤出机速度和加速度可能导致跳过。