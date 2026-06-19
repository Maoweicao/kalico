# Delta 校准

本文档描述 Kalico 的自动校准系统用于"delta"风格打印机。

Delta 校准涉及查找塔限位位置、塔角度、delta 半径和 delta 臂长。这些设置控制 delta 打印机上的打印机运动。每个参数都有不明显的非线性影响，手动校准它们很困难。相比之下，软件校准代码只需几分钟即可提供出色的结果。不需要特殊的探测硬件。

最终，delta 校准取决于塔限位开关的精度。如果你使用 Trinamic 步进电机驱动，请考虑启用[限位相位](Endstop_Phase.md)检测以提高这些开关的精度。

## 自动与手动探测

Kalico 支持通过手动探测方法或通过自动 Z 探针校准 delta 参数。

一些 delta 打印机套件附带的自动 Z 探针精度不够（具体来说，臂长的微小差异可能导致效应器倾斜，从而扭曲自动探针）。如果使用自动探针，请先[校准探针](Probe_Calibrate.md)，然后检查[探针位置偏差](Probe_Calibrate.md#location-bias-check)。如果自动探针的偏差超过 25 微米（0.025mm），则改用手动探测。手动探测只需几分钟，并且消除了探针引入的误差。

如果使用安装在热端侧面的探针（即它具有 X 或 Y 偏移），请注意执行 delta 校准将使探针校准的结果无效。此类探针很少适合在 delta 上使用（因为微小的效应器倾斜会导致探针位置偏差）。如果无论如何使用探针，请务必在任何 delta 校准后重新运行探针校准。

## 基本 delta 校准

Kalico 有一个 DELTA_CALIBRATE 命令，可以执行基本 delta 校准。此命令探测床面上的七个不同点，并计算塔角度、塔限位和 delta 半径的新值。

为了执行此校准，必须提供初始 delta 参数（臂长、半径和限位位置），并且它们应具有几毫米以内的精度。大多数 delta 打印机套件将提供这些参数——使用这些初始默认值配置打印机，然后继续运行下面描述的 DELTA_CALIBRATE 命令。如果没有默认值可用，请在线搜索可以提供基本起点的 delta 校准指南。

在 delta 校准过程中，打印机可能需要探测到否则被视为床面平面以下的位置。通常通过更新配置允许在校准期间这样做，使打印机的 `minimum_z_position=-5`。（校准完成后，可以从配置中删除此设置。）

有两种方法执行探测——手动探测（`DELTA_CALIBRATE METHOD=manual`）和自动探测（`DELTA_CALIBRATE`）。手动探测方法将把头移动到床面附近，然后等待用户按照["纸张测试"](Bed_Level.md#the-paper-test)中描述的步骤确定给定位置喷嘴与床面之间的实际距离。

要执行基本探测，请确保配置中定义了 [delta_calibrate] 节，然后运行工具：
```
G28
DELTA_CALIBRATE METHOD=manual
```
探测七个点后，将计算新的 delta 参数。通过运行以下命令保存并应用这些参数：
```
SAVE_CONFIG
```

基本校准应提供足够精确的 delta 参数以进行基本打印。如果这是新打印机，这是打印一些基本对象并验证一般功能的好时机。

## 增强 delta 校准

基本 delta 校准通常能很好地计算 delta 参数，使喷嘴与床面保持正确的距离。但是，它不尝试校准 X 和 Y 尺寸精度。执行增强 delta 校准以验证尺寸精度是个好主意。

此校准过程需要打印测试对象并使用数字卡尺测量该测试对象的部件。

在运行增强 delta 校准之前，必须运行基本 delta 校准（通过 DELTA_CALIBRATE 命令）并保存结果（通过 SAVE_CONFIG 命令）。确保自上次执行基本 delta 校准以来打印机配置或硬件没有明显变化（如果不确定，请在打印下面描述的测试对象之前重新运行[基本 delta 校准](#basic-delta-calibration)，包括 SAVE_CONFIG）。

使用切片软件从 [docs/prints/calibrate_size.stl](prints/calibrate_size.stl) 文件生成 G-Code。使用慢速（例如 40mm/s）切片对象。如果可能，使用硬塑料（如 PLA）打印对象。对象直径为 140mm。如果这对打印机来说太大，可以缩小它（但请确保均匀缩放 X 和 Y 轴）。如果打印机支持明显更大的打印件，也可以增加此对象的大小。更大的尺寸可以提高测量精度，但良好的打印附着力比更大的打印尺寸更重要。

打印测试对象并等待其完全冷却。下面描述的命令必须使用与打印校准对象相同的打印机设置运行（不要在打印和测量之间运行 DELTA_CALIBRATE，或执行会更改打印机配置的其他操作）。

如果可能，在对象仍附着在打印床上时执行下面描述的测量，但如果零件从床上脱落也不要担心——只需在执行测量时避免弯曲对象。

首先测量中心柱与"A"标签旁边的柱之间的距离（该标签也应指向"A"塔）。

![delta-a-distance](/img/delta-a-distance.jpg)

然后逆时针方向测量中心柱与其他柱之间的距离（从中心到 C 标签对面的柱的距离、从中心到带有 B 标签的柱的距离等）。

![delta_cal_e_step1](/img/delta_cal_e_step1.png)

将这些参数输入 Kalico，使用逗号分隔的浮点数列表：
```
DELTA_ANALYZE CENTER_DISTS=<a_dist>,<far_c_dist>,<b_dist>,<far_a_dist>,<c_dist>,<far_b_dist>
```
提供值时不要在它们之间留空格。

然后测量 A 柱与 C 标签对面的柱之间的距离。

![delta-ab-distance](/img/delta-outer-distance.jpg)

然后逆时针方向测量 C 对面的柱与 B 柱之间的距离、B 柱与 A 对面的柱之间的距离，依此类推。

![delta_cal_e_step2](/img/delta_cal_e_step2.png)

将这些参数输入 Kalico：
```
DELTA_ANALYZE OUTER_DISTS=<a_to_far_c>,<far_c_to_b>,<b_to_far_a>,<far_a_to_c>,<c_to_far_b>,<far_b_to_a>
```

此时可以将对象从床上取下。最后的测量是柱本身。沿 A 辐条测量中心柱的大小，然后是 B 辐条，然后是 C 辐条。

![delta-a-pillar](/img/delta-a-pillar.jpg)

![delta_cal_e_step3](/img/delta_cal_e_step3.png)

将它们输入 Kalico：
```
DELTA_ANALYZE CENTER_PILLAR_WIDTHS=<a>,<b>,<c>
```

最后的测量是外部柱。首先测量 A 柱沿从 A 到 C 对面柱的线的距离。

![delta-ab-pillar](/img/delta-outer-pillar.jpg)

然后逆时针方向测量剩余的外部柱（沿从 C 到 B 的线对面的柱、B 柱沿到 A 对面柱的线等）。

![delta_cal_e_step4](/img/delta_cal_e_step4.png)

并将它们输入 Kalico：
```
DELTA_ANALYZE OUTER_PILLAR_WIDTHS=<a>,<far_c>,<b>,<far_a>,<c>,<far_b>
```

如果对象被缩放到更小或更大的尺寸，请提供切片对象时使用的缩放因子：
```
DELTA_ANALYZE SCALE=1.0
```
（缩放值 2.0 表示对象是其原始大小的两倍，0.5 表示是其原始大小的一半。）

最后，通过运行以下命令执行增强 delta 校准：
```
DELTA_ANALYZE CALIBRATE=extended
```
此命令可能需要几分钟才能完成。完成后，它将计算更新的 delta 参数（delta 半径、塔角度、限位位置和臂长）。使用 SAVE_CONFIG 命令保存并应用设置：
```
SAVE_CONFIG
```

SAVE_CONFIG 命令将保存更新的 delta 参数和距离测量的信息。未来的 DELTA_CALIBRATE 命令也将利用此距离信息。不要尝试在运行 SAVE_CONFIG 后重新输入原始距离测量值，因为此命令会更改打印机配置，原始测量值不再适用。

### 附加说明

* 如果 delta 打印机具有良好的尺寸精度，则任意两个柱之间的距离应约为 74mm，每个柱的宽度应约为 9mm。（具体来说，目标是任意两个柱之间的距离减去一个柱的宽度正好是 65mm。）如果零件存在尺寸不准确，DELTA_ANALYZE 例程将使用距离测量和上次 DELTA_CALIBRATE 命令的先前高度测量来计算新的 delta 参数。

* DELTA_ANALYZE 可能会产生令人惊讶的 delta 参数。例如，它可能建议与打印机实际臂长不匹配的臂长。尽管如此，测试表明 DELTA_ANALYZE 通常能产生更优越的结果。据信，计算的 delta 参数能够解释硬件其他地方的微小误差。例如，臂长的微小差异可能导致效应器倾斜，其中一些倾斜可以通过调整臂长参数来解释。

## 在 Delta 上使用床面网格

可以在 delta 上使用[床面网格](Bed_Mesh.md)。但是，在启用床面网格之前获得良好的 delta 校准非常重要。使用较差的 delta 校准运行床面网格将导致混乱和较差的结果。

请注意，执行 delta 校准将使之前获得的任何床面网格无效。执行新的 delta 校准后，务必重新运行 BED_MESH_CALIBRATE。
