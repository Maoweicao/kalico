# 共振补偿

Kalico 支持输入整形 - 一种可用于减少打印中振铃（也称为回声、重影或波纹）的技术。振铃是一种表面打印缺陷，通常边缘等元素在打印表面上重复自身，形成微妙的"回声"：

|![振铃测试](/img/ringing-test.jpg)|![3D Benchy](/img/ringing-3dbenchy.jpg)|

振铃是由打印机中由于打印方向快速变化引起的机械振动造成的。请注意，振铃通常具有机械原因：打印机框架刚性不足、皮带不紧或弹性过大、机械部件对齐问题、移动质量过大等。如果可能，应首先检查并修复这些问题。

[输入整形](https://en.wikipedia.org/wiki/Input_shaping)是一种开环控制技术，它创建一个可以抵消自身振动的控制信号。输入整形需要一些调优和测量才能启用。除了振铃之外，输入整形通常还会减少打印机的整体振动和晃动，并且还可能提高 Trinamic 步进驱动器 stealthChop 模式的可靠性。

## 调优

基本调优需要通过打印测试模型来测量打印机的振铃频率。

在切片器中切片振铃测试模型，该模型可在 [docs/prints/ringing_tower.stl](prints/ringing_tower.stl) 中找到：

* 建议的层高为 0.2 或 0.25 mm。
* 填充和顶层可以设置为 0。
* 使用 1-2 个外围轮廓，或者更好的是使用 1-2 mm 底部的平滑花瓶模式。
* **外部**外围轮廓使用足够高的速度，约 80-100 mm/sec。
* 确保最小层时间**最多**为 3 秒。
* 确保切片器中禁用任何"动态加速度控制"。
* 不要旋转模型。模型背面有 X 和 Y 标记。请注意标记相对于打印机轴的不寻常位置 - 这不是错误。这些标记可以在调优过程中用作参考，因为它们显示了测量对应于哪个轴。

### 振铃频率

首先，测量**振铃频率**。

1. 如果更改了 `square_corner_velocity` 参数，请将其恢复为 5.0。使用输入整形时不建议增加它，因为它会导致零件中出现更多平滑 - 最好使用更高的加速度值。
2. 通过发出以下命令禁用 `minimum_cruise_ratio` 功能：`SET_VELOCITY_LIMIT MINIMUM_CRUISE_RATIO=0`
3. 禁用压力提前：`SET_PRESSURE_ADVANCE ADVANCE=0`
4. 如果您已经将 `[input_shaper]` 部分添加到 printer.cfg，请执行 `SET_INPUT_SHAPER SHAPER_FREQ_X=0 SHAPER_FREQ_Y=0` 命令。如果您得到"Unknown command"错误，此时可以安全地忽略它并继续测量。
5. 执行命令：
   `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`
   基本上，我们尝试通过设置不同的大加速度值使振铃更加明显。此命令将从 1500 mm/sec^2 开始每 5 mm 增加加速度：1500 mm/sec^2、2000 mm/sec^2、2500 mm/sec^2，依此类推，直到最后一个频带的 7000 mm/sec^2。
6. 使用建议的参数切片测试模型。
7. 如果振铃清晰可见并且您看到加速度对于您的打印机来说过高（例如，打印机晃动过大或开始丢步），可以提前停止打印。
8. 使用模型背面的 X 和 Y 标记作为参考。应使用带有 X 标记一侧的测量值进行 X 轴*配置*，Y 标记用于 Y 轴配置。测量带有 X 标记部分上几个振荡之间的距离 *D*（以 mm 为单位），靠近凹口处，最好跳过第一个或两个振荡。为了更容易测量振荡之间的距离，请先标记振荡，然后用尺子或卡尺测量标记之间的距离：

    |![标记振铃](/img/ringing-mark.jpg)|![测量振铃](/img/ringing-measure.jpg)|

9. 计算测量距离 *D* 对应多少个振荡 *N*。如果您不确定如何计算振荡，请参考上图，其中显示 *N* = 6 个振荡。
10. 计算 X 轴的振铃频率为 *V* &middot; *N* / *D* (Hz)，其中 *V* 是外围轮廓的速度（mm/sec）。对于上面的示例，我们标记了 6 个振荡，测试以 100 mm/sec 的速度打印，因此频率为 100 * 6 / 12.14 ≈ 49.4 Hz。
11. 对 Y 标记也执行 (8) - (10)。

请注意，测试打印上的振铃应遵循弯曲凹口的模式，如上图所示。如果不是，则此缺陷实际上不是振铃，而是具有不同的来源 - 机械问题或挤出机问题。在启用和调优输入整形之前应首先修复它。

如果测量不可靠，例如振荡之间的距离不稳定，则可能意味着打印机在同一轴上有多个共振频率。可以尝试遵循[振铃频率的不可靠测量](#unreliable-measurements-of-ringing-frequencies)部分中描述的调优过程，仍然可以从输入整形技术中获得一些效果。

振铃频率可能取决于模型在构建板中的位置和 Z 高度，*尤其是在 delta 打印机上*；您可以检查是否在测试模型侧面的不同位置和不同高度看到频率差异。如果是这种情况，您可以计算 X 和 Y 轴上的平均振铃频率。

如果测量的振铃频率非常低（低于约 20-25 Hz），在继续进一步的输入整形调优之前，最好投资加强打印机或减少移动质量 - 取决于您的情况适用的内容 - 然后重新测量频率。对于许多流行的打印机型号，通常已经有一些可用的解决方案。

请注意，如果对打印机进行影响移动质量或改变系统刚度的更改，振铃频率可能会发生变化，例如：

* 在工具头上安装、移除或更换某些工具，改变其质量，例如安装新的（更重或更轻的）直接挤出步进电机或新的热端，添加带有管道的重型风扇等。
* 皮带被拉紧。
* 安装了一些增加框架刚性的附件。
* 在床式打印机上安装不同的打印平台，或添加玻璃等。

如果进行此类更改，最好至少测量振铃频率以查看它们是否已更改。

### 输入整形器配置

测量 X 和 Y 轴的振铃频率后，可以将以下部分添加到您的 `printer.cfg`：
```
[input_shaper]
shaper_freq_x: ...  # 测试模型 X 标记的频率
shaper_freq_y: ...  # 测试模型 Y 标记的频率
```

对于上面的示例，我们得到 shaper_freq_x/y = 49.4。

### 选择输入整形器

Kalico 支持多种输入整形器。它们对确定共振频率的误差敏感度不同，并且对打印零件造成的平滑程度也不同。此外，某些整形器如 2HUMP_EI 和 3HUMP_EI 通常不应与 shaper_freq = 共振频率一起使用 - 它们是从不同的考虑因素配置的，以同时减少多个共振。

对于大多数打印机，可以推荐 MZV 或 EI 整形器。本节描述了一个测试过程，以在它们之间进行选择，并找出一些其他相关参数。

按照以下方式打印振铃测试模型：

1. 重启固件：`RESTART`
2. 准备测试：`SET_VELOCITY_LIMIT MINIMUM_CRUISE_RATIO=0`
3. 禁用压力提前：`SET_PRESSURE_ADVANCE ADVANCE=0`
4. 执行：`SET_INPUT_SHAPER SHAPER_TYPE=MZV`
5. 执行命令：
   `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`
6. 使用建议的参数切片测试模型。

如果此时没有看到振铃，则可以推荐使用 MZV 整形器。

如果您确实看到一些振铃，请使用[振铃频率](#ringing-frequency)部分中描述的步骤 (8)-(10) 重新测量频率。如果频率与您之前获得的值差异显著，则需要更复杂的输入整形器配置。您可以参考[输入整形器](#input-shapers)部分的技术细节。否则，请继续下一步。

现在尝试 EI 输入整形器。要尝试它，请重复上面的步骤 (1)-(6)，但在步骤 4 中执行以下命令代替：
`SET_INPUT_SHAPER SHAPER_TYPE=EI`。

比较使用 MZV 和 EI 输入整形器的两次打印。如果 EI 明显比 MZV 效果更好，则使用 EI 整形器，否则优先使用 MZV。请注意，EI 整形器会在打印零件中造成更多平滑（有关更多详细信息，请参阅下一节）。将 `shaper_type: mzv`（或 ei）参数添加到 [input_shaper] 部分，例如：
```
[input_shaper]
shaper_freq_x: ...
shaper_freq_y: ...
shaper_type: mzv
```

关于整形器选择的一些说明：

* EI 整形器可能更适合床式打印机（如果共振频率和由此产生的平滑允许的话）：随着更多耗材沉积在移动床上，床的质量增加，共振频率将降低。由于 EI 整形器对共振频率变化更稳健，在打印大型零件时可能效果更好。
* 由于 delta 运动学的性质，共振频率在构建体积的不同部分可能有很大差异。因此，EI 整形器可能比 MZV 或 ZV 更适合 delta 打印机，应考虑使用。如果共振频率足够大（超过 50-60 Hz），则可以尝试测试 2HUMP_EI 整形器（通过运行上面建议的测试并使用 `SET_INPUT_SHAPER SHAPER_TYPE=2HUMP_EI`），但在启用之前请检查[下面部分](#selecting-max_accel)中的注意事项。

### 选择 max_accel

您应该有一个使用上一步选择的整形器打印的测试（如果没有，请使用[建议的参数](#tuning)切片测试模型，禁用压力提前 `SET_PRESSURE_ADVANCE ADVANCE=0` 并启用调优塔 `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`）。请注意，在非常高的加速度下，根据共振频率和您选择的输入整形器（例如，EI 整形器比 MZV 产生更多平滑），输入整形可能导致零件过度平滑和圆角。因此，max_accel 的选择应防止这种情况。另一个可能影响平滑的参数是 `square_corner_velocity`，因此不建议将其增加到默认的 5 mm/sec 以上以防止增加平滑。

为了选择合适的 max_accel 值，请检查所选输入整形器的模型。首先，注意在哪个加速度下振铃仍然很小 - 您可以接受它。

接下来，检查平滑度。为了帮助解决这个问题，测试模型在墙壁中有一个小间隙（0.15 mm）：

![测试间隙](/img/smoothing-test.png)

随着加速度的增加，平滑度也会增加，打印中的实际间隙会变宽：

![整形器平滑](/img/shaper-smoothing.jpg)

在此图片中，加速度从左到右增加，间隙从 3500 mm/sec^2 开始增长（从左数第 5 个频带）。因此，在此情况下，max_accel 的良好值为 3000 (mm/sec^2) 以避免过度平滑。

请注意测试打印中间隙仍然非常小时的加速度。如果您看到凸起，但在高加速度下墙壁中根本没有间隙，可能是由于禁用了压力提前，尤其是在鲍登挤出机上。如果是这种情况，您可能需要在启用 PA 的情况下重复打印。也可能是耗材流量校准错误（过高）的结果，因此最好也检查一下。

选择两个加速度值中的较小值（来自振铃和平滑），并将其作为 `max_accel` 放入 printer.cfg 中。

请注意，可能会发生 - 特别是在低振铃频率下 - EI 整形器即使在较低加速度下也会导致过多的平滑。在这种情况下，MZV 可能是更好的选择，因为它可能允许更高的加速度值。

在非常低的振铃频率下（约 25 Hz 及以下），即使 MZV 整形器也可能产生过多的平滑。如果是这种情况，您也可以尝试使用 ZV 整形器重复[选择输入整形器](#choosing-input-shaper)部分中的步骤，方法是使用 `SET_INPUT_SHAPER SHAPER_TYPE=ZV` 命令代替。ZV 整形器应该比 MZV 显示更少的平滑，但对测量振铃频率的误差更敏感。

另一个考虑因素是，如果共振频率太低（低于 20-25 Hz），最好增加打印机刚度或减少移动质量。否则，加速度和打印速度可能会因为过多的平滑而受到限制，而不是振铃。


### 微调共振频率

请注意，使用振铃测试模型测量共振频率的精度对于大多数目的来说已经足够，因此不建议进一步调优。如果您仍然想尝试仔细检查您的结果（例如，如果您在使用与您之前测量的相同频率的输入整形器打印测试模型后仍然看到一些振铃），您可以按照本节中的步骤操作。请注意，如果在启用 [input_shaper] 后在不同频率下看到振铃，本节将无法帮助解决这个问题。

假设您已使用建议的参数切片振铃模型，请为 X 和 Y 轴中的每一个完成以下步骤：

1. 准备测试：`SET_VELOCITY_LIMIT MINIMUM_CRUISE_RATIO=0`
2. 确保压力提前已禁用：`SET_PRESSURE_ADVANCE ADVANCE=0`
3. 执行：`SET_INPUT_SHAPER SHAPER_TYPE=ZV`
4. 从使用您选择的输入整形器的现有振铃测试模型中选择显示足够振铃的加速度，并使用以下命令设置：`SET_VELOCITY_LIMIT ACCEL=...`
5. 计算 `TUNING_TOWER` 命令调优 `shaper_freq_x` 参数所需的必要参数如下：start = shaper_freq_x * 83 / 132，factor = shaper_freq_x / 66，其中此处的 `shaper_freq_x` 是 `printer.cfg` 中的当前值。
6. 执行命令：
   `TUNING_TOWER COMMAND=SET_INPUT_SHAPER PARAMETER=SHAPER_FREQ_X START=start FACTOR=factor BAND=5`
   使用步骤 (5) 中计算的 `start` 和 `factor` 值。
7. 打印测试模型。
8. 重置原始频率值：`SET_INPUT_SHAPER SHAPER_FREQ_X=...`。
9. 找到显示振铃最少的频带并从底部开始计算其编号（从 1 开始）。
10. 通过旧的 shaper_freq_x * (39 + 5 * #频带编号) / 66 计算新的 shaper_freq_x 值。

以相同的方式对 Y 轴重复这些步骤，将对 X 轴的引用替换为 Y 轴（例如，在公式和 `TUNING_TOWER` 命令中将 `shaper_freq_x` 替换为 `shaper_freq_y`）。

例如，假设您测量了一个轴的振铃频率为 45 Hz。这给出了 `TUNING_TOWER` 命令的 start = 45 * 83 / 132 = 28.30 和 factor = 45 / 66 = 0.6818 值。
现在假设打印测试模型后，从底部数第四个频带显示的振铃最少。这给出了更新的 shaper_freq_? 值等于 45 * (39 + 5 * 4) / 66 ≈ 40.23。

计算出新的 `shaper_freq_x` 和 `shaper_freq_y` 参数后，您可以使用新的 `shaper_freq_x` 和 `shaper_freq_y` 值更新 `printer.cfg` 中的 `[input_shaper]` 部分。

### 压力提前

如果您使用压力提前，可能需要重新调优。请按照[说明](Pressure_Advance.md#tuning-pressure-advance)查找新值（如果与之前不同）。请确保在调优压力提前之前重启 Kalico。

### 振铃频率的不可靠测量

如果您无法测量振铃频率，例如振荡之间的距离不稳定，您仍然可以利用输入整形技术，但结果可能不如正确测量频率时那么好，并且需要更多的调优和打印测试模型。请注意，另一种可能性是购买并安装加速度计并使用它测量共振（请参阅描述所需硬件和设置过程的[文档](Measuring_Resonances.md)）- 但此选项需要一些压接和焊接。


要进行调优，请在 `printer.cfg` 中添加空的 `[input_shaper]` 部分。然后，假设您已使用建议的参数切片振铃模型，请按照以下方式打印测试模型 3 次。第一次打印前，运行

1. `RESTART`
2. `SET_VELOCITY_LIMIT MINIMUM_CRUISE_RATIO=0`
3. `SET_PRESSURE_ADVANCE ADVANCE=0`
4. `SET_INPUT_SHAPER SHAPER_TYPE=2HUMP_EI SHAPER_FREQ_X=60 SHAPER_FREQ_Y=60`
5. `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`

并打印模型。然后再次打印模型，但在打印前运行

1. `SET_INPUT_SHAPER SHAPER_TYPE=2HUMP_EI SHAPER_FREQ_X=50 SHAPER_FREQ_Y=50`
2. `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`

然后第三次打印模型，但现在运行

1. `SET_INPUT_SHAPER SHAPER_TYPE=2HUMP_EI SHAPER_FREQ_X=40 SHAPER_FREQ_Y=40`
2. `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`

本质上，我们使用 TUNING_TOWER 打印振铃测试模型，使用 2HUMP_EI 整形器，shaper_freq = 60 Hz、50 Hz 和 40 Hz。

如果没有一个模型显示振铃改善，那么不幸的是，输入整形技术似乎无法帮助您的情况。

否则，可能所有模型都没有显示振铃，或者一些显示振铃而一些不那么明显。选择仍然显示良好振铃改善的最高频率测试模型。例如，如果 40 Hz 和 50 Hz 模型几乎不显示振铃，而 60 Hz 模型已经显示更多振铃，则坚持使用 50 Hz。

现在检查 EI 整形器在您的情况下是否足够好。根据您选择的 2HUMP_EI 整形器的频率选择 EI 整形器频率：

* 对于 2HUMP_EI 60 Hz 整形器，使用 shaper_freq = 50 Hz 的 EI 整形器。
* 对于 2HUMP_EI 50 Hz 整形器，使用 shaper_freq = 40 Hz 的 EI 整形器。
* 对于 2HUMP_EI 40 Hz 整形器，使用 shaper_freq = 33 Hz 的 EI 整形器。

现在再次打印测试模型，运行

1. `SET_INPUT_SHAPER SHAPER_TYPE=EI SHAPER_FREQ_X=... SHAPER_FREQ_Y=...`
2. `TUNING_TOWER COMMAND=SET_VELOCITY_LIMIT PARAMETER=ACCEL START=1500 STEP_DELTA=500 STEP_HEIGHT=5`

提供之前确定的 shaper_freq_x=... 和 shaper_freq_y=...。

如果 EI 整形器显示出与 2HUMP_EI 整形器非常相当的好结果，则坚持使用 EI 整形器和之前确定的频率，否则使用 2HUMP_EI 整形器及相应的频率。将结果添加到 `printer.cfg` 中，例如：
```
[input_shaper]
shaper_freq_x: 50
shaper_freq_y: 50
shaper_type: 2hump_ei
```

继续使用[选择 max_accel](#selecting-max_accel) 部分进行调优。


## 故障排除和常见问题

### 我无法获得可靠的共振频率测量

首先，请确保不是打印机的其他问题而不是振铃。如果测量不可靠，例如振荡之间的距离不稳定，则可能意味着打印机在同一轴上有多个共振频率。可以尝试遵循[振铃频率的不可靠测量](#unreliable-measurements-of-ringing-frequencies)部分中描述的调优过程，仍然可以从输入整形技术中获得一些效果。另一种可能性是安装加速度计，使用它[测量](Measuring_Resonances.md)共振，并使用这些测量的结果自动调优输入整形器。

### 启用 [input_shaper] 后，我打印的零件过度平滑，细节丢失

检查[选择 max_accel](#selecting-max_accel) 部分中的注意事项。如果共振频率较低，不应设置过高的 max_accel 或增加 square_corner_velocity 参数。最好选择 MZV 甚至 ZV 输入整形器而不是 EI（或 2HUMP_EI 和 3HUMP_EI 整形器）。


### 在没有振铃的情况下成功打印一段时间后，它似乎又回来了

一段时间后共振频率可能会发生变化。例如，可能皮带张力发生了变化（皮带变得更松）等。最好检查并重新测量振铃频率，如[振铃频率](#ringing-frequency)部分所述，并在必要时更新您的配置文件。

### 输入整形器支持双滑块设置吗？

是的。在这种情况下，应为每个滑块测量两次共振。例如，如果第二个（双）滑块安装在 X 轴上，则可以为主滑块和双滑块的 X 轴设置不同的输入整形器。但是，Y 轴的输入整形器对于两个滑块应该相同（因为最终该轴由一个或多个步进电机驱动，每个电机被命令执行完全相同的步骤）。配置此类设置的输入整形器的一种可能性是保持 `[input_shaper]` 部分为空，并在 `printer.cfg` 中另外定义 `[delayed_gcode]` 部分，如下所示：
```
[input_shaper]
# 故意为空

[delayed_gcode init_shaper]
initial_duration: 0.1
gcode:
  SET_DUAL_CARRIAGE CARRIAGE=1
  SET_INPUT_SHAPER SHAPER_TYPE_X=<dual_carriage_shaper> SHAPER_FREQ_X=<dual_carriage_freq> SHAPER_TYPE_Y=<y_shaper> SHAPER_FREQ_Y=<y_freq>
  SET_DUAL_CARRIAGE CARRIAGE=0
  SET_INPUT_SHAPER SHAPER_TYPE_X=<primary_carriage_shaper> SHAPER_FREQ_X=<primary_carriage_freq> SHAPER_TYPE_Y=<y_shaper> SHAPER_FREQ_Y=<y_freq>
```
请注意，`SHAPER_TYPE_Y` 和 `SHAPER_FREQ_Y` 在两个命令中应该相同。也可以将类似的代码片段放入切片器的开始 G-code 中，但这样在开始任何打印之前整形器不会被启用。

请注意，输入整形器只需要配置一次。通过 `SET_DUAL_CARRIAGE` 命令后续更改滑块或其模式将保留配置的输入整形器参数。

### input_shaper 会影响打印时间吗？

不会，`input_shaper` 功能本身对打印时间几乎没有影响。但是，`max_accel` 的值肯定会影响（此参数的调优在[本节](#selecting-max_accel)中描述）。

## 技术细节

### 输入整形器

Kalico 中使用的输入整形器是相当标准的，可以在描述相应整形器的文章中找到更深入的概述。本节包含一些支持的输入整形器的技术方面的简要概述。下表显示了每个整形器的一些（通常是近似的）参数。

| 输入 <br/> 整形器 | 整形器 <br/> 持续时间 | 振动减少 20 倍 <br/>（5% 振动容差） | 振动减少 10 倍 <br/>（10% 振动容差） |
|:--:|:--:|:--:|:--:|
| ZV | 0.5 / shaper_freq | 不适用 | ± 5% shaper_freq |
| MZV | 0.75 / shaper_freq | ± 4% shaper_freq | -10%...+15% shaper_freq |
| ZVD | 1 / shaper_freq | ± 15% shaper_freq | ± 22% shaper_freq |
| EI | 1 / shaper_freq | ± 20% shaper_freq | ± 25% shaper_freq |
| 2HUMP_EI | 1.5 / shaper_freq | ± 35% shaper_freq | ± 40 shaper_freq |
| 3HUMP_EI | 2 / shaper_freq | -45...+50% shaper_freq | -50%...+55% shaper_freq |

关于振动减少的说明：上表中的值是近似的。如果已知每个轴的打印机阻尼比，则可以更精确地配置整形器，它将在更宽的频率范围内减少共振。但是，阻尼比通常是未知的，并且在没有特殊设备的情况下很难估计，因此 Kalico 默认使用 0.1 值，这是一个很好的通用值。表中的频率范围涵盖了围绕该值的许多不同可能的阻尼比（大约从 0.05 到 0.2）。

还要注意，EI、2HUMP_EI 和 3HUMP_EI 被调优为将振动减少到 5%，因此 10% 振动容差的值仅供参考。

**如何使用此表：**

* 整形器持续时间影响零件的平滑度 - 它越大，零件越平滑。这种依赖性不是线性的，但可以让人了解在相同频率下哪些整形器"平滑"更多。按平滑度排序如下：ZV < MZV < ZVD ≈ EI < 2HUMP_EI < 3HUMP_EI。此外，将 shaper_freq = 共振频率设置为整形器 2HUMP_EI 和 3HUMP_EI 很少实用（它们应用于减少多个频率的振动）。
* 可以估计整形器减少振动的频率范围。例如，shaper_freq = 35 Hz 的 MZV 将频率 [33.6, 36.4] Hz 的振动减少到 5%。shaper_freq = 50 Hz 的 3HUMP_EI 将范围 [27.5, 75] Hz 内的振动减少到 5%。
* 可以使用此表检查在需要减少多个频率的振动时应使用哪个整形器。例如，如果在同一轴上有 35 Hz 和 60 Hz 的共振：a) EI 整形器需要 shaper_freq = 35 / (1 - 0.2) = 43.75 Hz，并且它将减少共振直到 43.75 * (1 + 0.2) = 52.5 Hz，因此不够；b) 2HUMP_EI 整形器需要 shaper_freq = 35 / (1 - 0.35) = 53.85 Hz，并将减少振动直到 53.85 * (1 + 0.35) = 72.7 Hz - 因此这是一个可接受的配置。始终尝试对给定的整形器使用尽可能高的 shaper_freq（可能带有一些安全边际，因此在此示例中 shaper_freq ≈ 50-52 Hz 效果最好），并尝试使用整形器持续时间尽可能小的整形器。
* 如果需要减少几个非常不同频率的振动（例如，30 Hz 和 100 Hz），可能会发现上表没有提供足够的信息。在这种情况下，使用 [scripts/graph_shaper.py](../scripts/graph_shaper.py) 脚本可能会更幸运，它更灵活。
