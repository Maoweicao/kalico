# Delta 校准

本文档描述了 Kalico 对"delta"风格打印机的自动校准系统。

Delta 校准涉及找到塔限位开关位置、塔角度、delta 半径和 delta 臂长。
这些设置控制 delta 打印机上的运动。这些参数中的每一个都有明显的非线性影响，
手动校准很困难。相比之下，软件校准代码只需几分钟就能提供出色的结果。
无需特殊探针硬件。

最终，delta 校准取决于塔限位开关的精度。
如果使用 Trinamic 步进电机驱动器，请考虑启用 [限位开关相位](Endstop_Phase.md)
检测以提高这些开关的精度。

## 自动与手动探针

Kalico 支持通过手动探针方法或自动 Z 探针校准 delta 参数。

许多 delta 打印机套件随附的自动 Z 探针精度不足
（具体来说，臂长的小差异可能导致效应器倾斜，这可能会扭曲自动探针）。
如果使用自动探针，请首先 [校准探针](Probe_Calibrate.md)，
然后检查 [探针位置偏差](Probe_Calibrate.md#location-bias-check)。
如果自动探针的偏差超过 25 微米 (.025mm)，则使用手动探针。
手动探针仅需几分钟，它消除了探针引入的误差。

如果使用安装在热端一侧的探针（即具有 X 或 Y 偏移），
请注意执行 delta 校准将使探针校准的结果无效。
这些类型的探针很少适合在 delta 上使用
（因为轻微的效应器倾斜会导致探针位置偏差）。
如果仍然使用探针，请确保在任何 delta 校准之后重新运行探针校准。

## 基本 Delta 校准

Kalico 有一个 DELTA_CALIBRATE 命令，可以执行基本 delta 校准。
此命令探针床上七个不同的点，并计算塔角度、塔限位开关和 delta 半径的新值。

为了执行此校准，必须提供初始 delta 参数（臂长、半径和限位开关位置），
它们的精度应在几毫米以内。大多数 delta 打印机套件会提供这些参数——
使用这些初始默认值配置打印机，然后如下所述运行 DELTA_CALIBRATE 命令。
如果没有可用的默认值，请在线搜索 delta 校准指南，可以提供基本起点。

在 delta 校准过程中，打印机可能需要探针低于否则被认为是床平面的位置。
在校准期间通过更新配置以便打印机的 `minimum_z_position=-5`
来允许这种情况是典型的。（校准完成后，可以从配置中移除此设置。）

有两种方法来执行探针——手动探针
(`DELTA_CALIBRATE METHOD=manual`) 和自动探针 (`DELTA_CALIBRATE`)。
手动探针方法会将头部移到床附近，然后等待用户按照["纸张测试"](Bed_Level.md#the-paper-test)
中描述的步骤确定喷嘴和床之间给定位置处的实际距离。

要执行基本探针，请确保配置定义了 [delta_calibrate] 部分，然后运行工具：
```
G28
DELTA_CALIBRATE METHOD=manual
```

探针七个点后，将计算新的 delta 参数。运行以下命令保存并应用这些参数：
```
SAVE_CONFIG
```

基本校准应提供足够精确的 delta 参数以进行基本打印。
如果这是新打印机，现在是打印一些基本对象并验证常规功能的好时机。

## 增强的 Delta 校准

基本 delta 校准通常在计算 delta 参数（使得喷嘴距离床的距离正确）方面做得很好。
但是，它不尝试校准 X 和 Y 尺寸精度。最好执行增强的 delta 校准
来验证尺寸精度。

此校准程序需要打印测试对象并用数字卡尺测量该测试对象的部分。

在运行增强的 delta 校准之前，必须运行基本 delta 校准
（通过 DELTA_CALIBRATE 命令）并保存结果（通过 SAVE_CONFIG 命令）。
请确保自上次执行基本 delta 校准以来打印机配置或硬件没有明显变化
（如果不确定，在打印下述测试对象之前重新运行
[基本 delta 校准](#basic-delta-calibration)，包括 SAVE_CONFIG。）

使用切片机从 [docs/prints/calibrate_size.stl](prints/calibrate_size.stl) 文件生成 G-Code。
使用慢速（例如 40mm/s）对对象进行切片。如果可能，为对象使用刚性塑料（如 PLA）。
该对象的直径为 140mm。如果这对打印机来说太大，则可以缩小它
（但要确保均匀缩放 X 和 Y 轴）。如果打印机支持明显更大的打印，
则此对象也可以增加大小。更大的尺寸可以改善测量精度，
但良好的打印粘附比更大的打印尺寸更重要。

打印测试对象并等待其完全冷却。必须使用与打印校准对象相同的打印机设置
运行下面描述的命令（不要在打印和测量之间运行 DELTA_CALIBRATE，
或执行其他会改变打印机配置的操作）。

如果可能，在对象仍然粘在打印床上时执行下述测量，但如果零件从床上脱落，
请不用担心——只需尽量避免在执行测量时弯曲对象。

首先测量中心柱和标有"A"的柱旁边柱子之间的距离
（也应该指向"A"塔）。

![delta-a-distance](img/delta-a-distance.jpg)

然后逆时针走，测量中心柱和其他柱之间的距离
（从中心到 C 标签对面的柱的距离、从中心到带有 B 标签的柱的距离等）。

![delta_cal_e_step1](img/delta_cal_e_step1.png)

使用逗号分隔的浮点数列表将这些参数输入到 Kalico 中：
```
DELTA_ANALYZE CENTER_DISTS=<a_dist>,<far_c_dist>,<b_dist>,<far_a_dist>,<c_dist>,<far_b_dist>
```

提供值时不包含空格。

然后测量 A 柱和 C 标签对面的柱之间的距离。

![delta-ab-distance](img/delta-outer-distance.jpg)

然后逆时针走，测量从 C 对面的柱到 B 柱的距离、
从 B 柱到 A 对面的柱的距离等。

![delta_cal_e_step2](img/delta_cal_e_step2.png)

将这些参数输入到 Kalico：
```
DELTA_ANALYZE OUTER_DISTS=<a_to_far_c>,<far_c_to_b>,<b_to_far_a>,<far_a_to_c>,<c_to_far_b>,<far_b_to_a>
```

此时可以从床上移除对象。最终的测量是柱子本身。
测量沿 A 轮辐中心柱的大小，然后是 B 轮辐，然后是 C 轮辐。

![delta-a-pillar](img/delta-a-pillar.jpg)

![delta_cal_e_step3](img/delta_cal_e_step3.png)

将它们输入到 Kalico：
```
DELTA_ANALYZE CENTER_PILLAR_WIDTHS=<a>,<b>,<c>
```

最终测量是外部柱子。首先测量沿从 A 到 C 对面的柱的线的 A 柱的距离。

![delta-ab-pillar](img/delta-outer-pillar.jpg)

然后逆时针走，测量剩余的外部柱子
（C 对面的柱沿到 B 的线、B 柱沿到 A 对面的柱的线等）。

![delta_cal_e_step4](img/delta_cal_e_step4.png)

并将它们输入到 Kalico：
```
DELTA_ANALYZE OUTER_PILLAR_WIDTHS=<a>,<far_c>,<b>,<far_a>,<c>,<far_b>
```

如果对象被缩放到更小或更大的尺寸，请提供切片对象时使用的缩放因子：
```
DELTA_ANALYZE SCALE=1.0
```

（缩放值 2.0 意味着对象是其原始大小的两倍，0.5 表示其原始大小的一半。）

最后，通过运行以下命令执行增强的 delta 校准：
```
DELTA_ANALYZE CALIBRATE=extended
```

此命令可能需要几分钟才能完成。完成后，
它将计算更新的 delta 参数（delta 半径、塔角度、限位开关位置和臂长）。
使用 SAVE_CONFIG 命令保存并应用设置：
```
SAVE_CONFIG
```

SAVE_CONFIG 命令将保存更新的 delta 参数和距离测量信息。
未来的 DELTA_CALIBRATE 命令也将利用这个距离信息。
运行 SAVE_CONFIG 后，不要尝试重新输入原始距离测量，
因为此命令更改打印机配置，原始测量不再适用。

### 其他注意事项

* 如果 delta 打印机具有良好的尺寸精度，则任何两个柱之间的距离应该约为 74mm，
  每个柱的宽度应该约为 9mm。（具体来说，目标是任何两个柱之间的距离
  减去其中一个柱的宽度恰好 65mm。）如果零件中存在尺寸不准确，
  则 DELTA_ANALYZE 例程将使用距离测量和上次 DELTA_CALIBRATE 命令的
  先前高度测量来计算新的 delta 参数。

* DELTA_ANALYZE 可能会生成令人惊讶的 delta 参数。例如，
  它可能建议不匹配打印机实际臂长的臂长。尽管如此，
  测试表明 DELTA_ANALYZE 通常生成卓越的结果。
  据信计算的 delta 参数能够说明硬件中的轻微错误。例如，
  臂长的小差异可能导致效应器倾斜，其中一些倾斜可能通过调整臂长参数来说明。

## 在 Delta 上使用床网格

可以在 delta 上使用 [床网格](Bed_Mesh.md)。但是，
在启用床网格之前获得良好的 delta 校准很重要。
使用不良 delta 校准运行床网格将导致令人困惑和糟糕的结果。

请注意，执行 delta 校准将使任何以前获得的床网格无效。
执行新的 delta 校准后，请确保重新运行 BED_MESH_CALIBRATE。