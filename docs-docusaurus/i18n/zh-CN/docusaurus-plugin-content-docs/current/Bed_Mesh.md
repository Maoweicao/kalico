# 热床网格

热床网格模块可用于补偿热床表面不规则性，以在整个热床上实现更好的第一层。需要注意的是，基于软件的校正无法达到完美的结果，它只能近似热床的形状。热床网格也无法补偿机械和电气问题。如果轴倾斜或探针不精确，则 bed_mesh 模块将无法从探测过程中获得准确的结果。

在进行网格校准之前，您需要确保探针的 Z 偏移已校准。如果使用限位开关进行 Z 归位，也需要对其进行校准。有关更多信息，请参阅 [探针校准](Probe_Calibrate.md) 和 [手动调平](Manual_Level.md) 中的 Z_ENDSTOP_CALIBRATE。

## 基本配置

### 矩形热床
此示例假设打印机具有 250 mm x 220 mm 的矩形热床，探针的 x 偏移为 24 mm，y 偏移为 5 mm。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
```

- `speed: 120`\
  _默认值: 50_\
  工具在点之间移动的速度。

- `horizontal_move_z: 5`\
  _默认值: 5_\
  探针在点之间移动之前升起的 Z 坐标。

- `mesh_min: 35, 6`\
  _必需_\
  最靠近原点的第一个探测坐标。此坐标相对于探针的位置。

- `mesh_max: 240, 198`\
  _必需_\
  距离原点最远的探测坐标。这不一定是最后一个探测点，因为探测过程以锯齿形进行。与 `mesh_min` 一样，此坐标相对于探针的位置。

- `probe_count: 5, 3`\
  _默认值: 3, 3_\
  每个轴上的探测点数，指定为 X、Y 整数值。在此示例中，将沿 X 轴探测 5 个点，沿 Y 轴探测 3 个点，总共 15 个探测点。请注意，如果您想要方形网格，例如 3x3，可以将其指定为单个整数值，该值同时适用于两个轴，即 `probe_count: 3`。请注意，网格需要每个轴至少 3 个 probe_count。

下图演示了如何使用 `mesh_min`、`mesh_max` 和 `probe_count` 选项来生成探测点。箭头表示探测过程的方向，从 `mesh_min` 开始。作为参考，当探针在 `mesh_min` 时，喷嘴将在 (11, 1)，当探针在 `mesh_max` 时，喷嘴将在 (206, 193)。

![bedmesh_rect_basic](/img/bedmesh_rect_basic.svg)

### 圆形热床
此示例假设打印机配备半径为 100mm 的圆形热床。我们将使用与矩形示例相同的探针偏移，X 方向 24 mm，Y 方向 5 mm。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_radius: 75
mesh_origin: 0, 0
round_probe_count: 5
```

- `mesh_radius: 75`\
  _必需_\
  探测网格的半径（以 mm 为单位），相对于 `mesh_origin`。请注意，探针的偏移限制了网格半径的大小。在此示例中，大于 76 的半径会将工具移出打印机的范围。

- `mesh_origin: 0, 0`\
  _默认值: 0, 0_\
  网格的中心点。此坐标相对于探针的位置。虽然默认值为 0, 0，但调整原点以探测更大比例的热床可能很有用。请参阅下图。

- `round_probe_count: 5`\
  _默认值: 5_\
  这是一个整数值，定义了沿 X 和 Y 轴的最大探测点数。"最大"是指沿网格原点探测的点数。此值必须是奇数，因为需要探测网格的中心。

下图显示了探测点是如何生成的。如您所见，将 `mesh_origin` 设置为 (-10, 0) 允许我们指定更大的网格半径 85。

![bedmesh_round_basic](/img/bedmesh_round_basic.svg)

## 高级配置

下面详细解释更高级的配置选项。每个示例都基于上面显示的基本矩形热床配置。每个高级选项同样适用于圆形热床。

### 网格插值

虽然可以使用简单的双线性插值直接对探测矩阵进行采样，以确定探测点之间的 Z 值，但通常使用更高级的插值算法来插值额外的点以增加网格密度是有用的。这些算法为网格添加曲率，试图模拟热床的材料特性。热床网格提供拉格朗日和双三次插值来实现这一点。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
mesh_pps: 2, 3
algorithm: bicubic
bicubic_tension: 0.2
```

- `mesh_pps: 2, 3`\
  _默认值: 2, 2_\
  `mesh_pps` 选项是 Mesh Points Per Segment 的缩写。此选项指定沿 X 和 Y 轴每个段要插值的点数。将"段"视为每个探测点之间的空间。与 `probe_count` 一样，`mesh_pps` 被指定为 X、Y 整数对，也可以指定为应用于两个轴的单个整数。在此示例中，X 轴有 4 个段，Y 轴有 2 个段。这计算出沿 X 有 8 个插值点，沿 Y 有 6 个插值点，结果为 13x9 网格。请注意，如果 mesh_pps 设置为 0，则禁用网格插值，探测矩阵将被直接采样。

- `algorithm: lagrange`\
  _默认值: lagrange_\
  用于插值网格的算法。可以是 `lagrange` 或 `bicubic`。拉格朗日插值限制为 6 个探测点，因为较大数量的样本往往会产生振荡。双三次插值要求每个轴至少 4 个探测点，如果指定的点少于 4 个，则强制使用拉格朗日采样。如果 `mesh_pps` 设置为 0，则忽略此值，因为不进行网格插值。

- `bicubic_tension: 0.2`\
  _默认值: 0.2_\
  如果 `algorithm` 选项设置为 bicubic，则可以指定张力值。张力越高，插值的斜率越大。调整此值时要小心，因为较高的值也会产生更多过冲，这将导致插值值高于或低于您的探测点。

下图显示了上述选项如何用于生成插值网格。

![bedmesh_interpolated](/img/bedmesh_interpolated.svg)

### 移动分割

热床网格的工作原理是拦截 gcode 移动命令并对其 Z 坐标应用变换。长移动必须分割为较小的移动，才能正确跟随热床的形状。以下选项控制分割行为。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
move_check_distance: 5
split_delta_z: .025
```

- `move_check_distance: 5`\
  _默认值: 5_\
  在执行分割之前检查所需 Z 变化的最小距离。在此示例中，将遍历长度超过 5mm 的移动。每 5mm 进行一次网格 Z 查找，将其与上一次移动的 Z 值进行比较。如果差值满足 `split_delta_z` 设置的阈值，则移动将被分割，遍历将继续。此过程重复直到移动结束，此时将应用最终调整。短于 `move_check_distance` 的移动将直接应用正确的 Z 调整，无需遍历或分割。

- `split_delta_z: .025`\
  _默认值: .025_\
  如上所述，这是触发移动分割所需的最小偏差。在此示例中，任何偏差在 +/- .025mm 范围内的 Z 值都将触发分割。

通常这些选项的默认值就足够了，事实上 `move_check_distance` 的默认值 5mm 可能有些过头。但是，高级用户可能希望尝试这些选项，以挤出最佳的第一层。

### 网格淡出

当启用"淡出"时，Z 调整将在配置定义的距离内逐渐消失。这是通过对层高进行微小调整来实现的，根据热床的形状增加或减少。淡出完成后，不再应用 Z 调整，允许打印件顶部是平坦的而不是镜像热床的形状。淡出也可能有一些不理想的特性，如果您淡出太快，可能会在打印件上产生可见的瑕疵。此外，如果您的热床明显翘曲，淡出可能会缩小或拉伸打印件的 Z 高度。因此，默认情况下禁用淡出。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
fade_start: 1
fade_end: 10
fade_target: 0
```

- `fade_start: 1`\
  _默认值: 1_\
  开始逐渐消除调整的 Z 高度。最好在开始淡出过程之前先打印几层。

- `fade_end: 10`\
  _默认值: 0_\
  淡出应完成的 Z 高度。如果此值低于 `fade_start`，则禁用淡出。可以根据打印表面的翘曲程度调整此值。明显翘曲的表面应该在更长的距离上淡出。接近平坦的表面可能能够减少此值以更快地淡出。如果使用 `fade_start` 的默认值 1，则 10mm 是一个合理的起始值。

- `fade_target: 0`\
  _默认值: 网格的平均 Z 值_\
  可以将 `fade_target` 视为淡出完成后应用于整个热床的附加 Z 偏移。一般来说，我们希望此值为 0，但在某些情况下不应该。例如，假设您在热床上的归位位置是一个异常值，它比平均探测高度低 0.2 mm。如果 `fade_target` 为 0，淡出将使打印件在热床上平均缩小 0.2 mm。通过将 `fade_target` 设置为 .2，归位区域将扩展 0.2 mm，但热床的其余部分将准确尺寸。通常最好在配置中不指定 `fade_target`，以便使用网格的平均高度，但如果想要在热床的特定部分上打印，可能需要手动调整淡出目标。

### 配置零参考位置

许多探针容易出现"漂移"，即由热量或干扰引起的探测不准确。这可能使计算探针的 z 偏移具有挑战性，特别是在不同的热床温度下。因此，一些打印机使用限位开关来归位 Z 轴，使用探针来校准网格。在此配置中，可以偏移网格，使 (X, Y) `reference position` 应用零调整。`reference position` 应该是在热床上执行 [Z_ENDSTOP_CALIBRATE](./Manual_Level.md#calibrating-a-z-endstop) 纸张测试的位置。bed_mesh 模块提供 `zero_reference_position` 选项用于指定此坐标：

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
zero_reference_position: 125, 110
probe_count: 5, 3
```
- `zero_reference_position: `\
  _默认值: 无（已禁用）_\
  `zero_reference_position` 期望一个与上述 `reference position` 匹配的 (X, Y) 坐标。如果坐标位于网格内，则网格将被偏移，使参考位置应用零调整。如果坐标位于网格之外，则校准后将探测该坐标，得到的 z 值用作 z 偏移。请注意，如果需要探测，此坐标不得位于指定为 `faulty_region` 的位置。

#### 已弃用的 relative_reference_index

使用 `relative_reference_index` 选项的现有配置必须更新为使用 `zero_reference_position`。[BED_MESH_OUTPUT PGP=1](#output) gcode 命令的响应将包含与索引关联的 (X, Y) 坐标；此位置可用作 `zero_reference_position` 的值。输出将类似于以下内容：

```
// bed_mesh: generated points
// Index | Tool Adjusted | Probe
// 0 | (1.0, 1.0) | (24.0, 6.0)
// 1 | (36.7, 1.0) | (59.7, 6.0)
// 2 | (72.3, 1.0) | (95.3, 6.0)
// 3 | (108.0, 1.0) | (131.0, 6.0)
... (additional generated points)
// bed_mesh: relative_reference_index 24 is (131.5, 108.0)
```

_注意：上述输出也会在初始化期间打印在 `klippy.log` 中。_

使用上面的示例，我们看到 `relative_reference_index` 与其坐标一起打印。因此 `zero_reference_position` 是 `131.5, 108`。



### 故障区域

热床的某些区域在探测时可能由于特定位置的"故障"而报告不准确的结果。最好的例子是带有用于固定可拆卸钢板的系列集成磁铁的热床。这些磁铁处及周围的磁场可能导致电感探针在比正常更高或更低的距离处触发，导致网格不能准确表示这些位置的表面。**注意：这不应与探针位置偏差混淆，后者在整个热床上产生不准确的结果。**

可以配置 `faulty_region` 选项来补偿这种影响。如果生成的点位于故障区域内，bed_mesh 将尝试探测该区域边界处的最多 4 个点。这些探测值将被平均并插入网格中，作为生成的 (X, Y) 坐标处的 Z 值。

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
faulty_region_1_min: 130.0, 0.0
faulty_region_1_max: 145.0, 40.0
faulty_region_2_min: 225.0, 0.0
faulty_region_2_max: 250.0, 25.0
faulty_region_3_min: 165.0, 95.0
faulty_region_3_max: 205.0, 110.0
faulty_region_4_min: 30.0, 170.0
faulty_region_4_max: 45.0, 210.0
```

- `faulty_region_{1...99}_min`\
  `faulty_region_{1..99}_max`\
  _默认值: 无（已禁用）_\
  故障区域的定义方式与网格本身类似，每个区域必须指定最小和最大 (X, Y) 坐标。故障区域可以延伸到网格之外，但生成的替代点始终在网格边界内。两个区域不能重叠。

下图说明了当生成的点位于故障区域内时如何生成替换点。所示区域与上面示例配置中的区域匹配。替换点及其坐标以绿色标识。

![bedmesh_interpolated](/img/bedmesh_faulty_regions.svg)

### 自适应网格

自适应热床网格是一种通过仅探测打印对象使用的热床区域来加速热床网格生成的方法。使用时，该方法将根据定义的打印对象占据的区域自动调整网格参数。

自适应网格区域将从所有定义的打印对象的边界定义的区域计算，因此它覆盖每个对象，包括配置中定义的任何边距。计算区域后，探测点数将根据默认网格区域和自适应网格区域的比率进行缩放。为了说明这一点，请考虑以下示例：

对于 150mmx150mm 的热床，`mesh_min` 设置为 `25,25`，`mesh_max` 设置为 `125,125`，默认网格区域为 100mmx100mm 的正方形。`50,50` 的自适应网格区域意味着自适应区域和默认网格区域之间的比率为 `0.5x0.5`。

如果 `bed_mesh` 配置指定 `probe_count` 为 `7x7`，自适应热床网格将使用 4x4 个探测点（7 * 0.5 向上取整）。

![adaptive_bedmesh](/img/adaptive_bed_mesh.svg)

```
[bed_mesh]
speed: 120
horizontal_move_z: 5
mesh_min: 35, 6
mesh_max: 240, 198
probe_count: 5, 3
adaptive_margin: 5
```

- `adaptive_margin` \
  _默认值: 0_ \
  在定义对象使用的热床区域周围添加的边距（以 mm 为单位）。下图显示了 `adaptive_margin` 为 5mm 的自适应热床网格区域。自适应网格区域（绿色区域）计算为使用的热床区域（蓝色区域）加上定义的边距。

  ![adaptive_bedmesh_margin](/img/adaptive_bed_mesh_margin.svg)

自适应热床网格本质上使用正在打印的 Gcode 文件中定义的对象。因此，预计每个 Gcode 文件将生成一个探测打印床不同区域的网格。因此，不应重复使用自适应热床网格。预期是如果使用自适应网格，则每次打印都会生成新的网格。

还需要考虑的是，自适应热床网格最适合用于通常可以探测整个热床并实现最大方差小于或等于 1 层高的机器。具有机械问题的机器（完整热床网格通常会补偿这些问题）在尝试在探测区域**之外**进行打印移动时可能会产生不理想的结果。如果完整热床网格的方差大于 1 层高，在使用自适应热床网格并尝试在网格化区域之外进行打印移动时必须谨慎。

## 热床网格 G 代码

### 校准

`BED_MESH_CALIBRATE PROFILE=<name> METHOD=[manual | automatic] [<probe_parameter>=<value>]
 [<mesh_parameter>=<value>] [ADAPTIVE=[0|1] [ADAPTIVE_MARGIN=<value>]`\
_默认配置文件: default_\
_默认方法: 如果检测到探针则为 automatic，否则为 manual_ \
_默认自适应: 0_ \
_默认自适应边距: 0_

启动热床网格校准的探测过程。

网格将保存到 `PROFILE` 参数指定的配置文件中，如果未指定则保存到 `default`。如果选择 `METHOD=manual`，则将进行手动探测。在自动和手动探测之间切换时，生成的网格点将自动调整。

可以指定网格参数来修改探测区域。以下参数可用：

- 矩形热床（笛卡尔）：
  - `MESH_MIN`
  - `MESH_MAX`
  - `PROBE_COUNT`
- 圆形热床（delta）：
  - `MESH_RADIUS`
  - `MESH_ORIGIN`
  - `ROUND_PROBE_COUNT`
- 所有热床：
  - `ALGORITHM`
  - `ADAPTIVE`
  - `ADAPTIVE_MARGIN`

有关每个参数如何应用于网格的详细信息，请参阅上面的配置文档。


### 配置文件

`BED_MESH_PROFILE SAVE=<name> LOAD=<name> REMOVE=<name>`

执行 BED_MESH_CALIBRATE 后，可以将当前网格状态保存到命名的配置文件中。这使得可以在不重新探测热床的情况下加载网格。使用 `BED_MESH_PROFILE SAVE=<name>` 保存配置文件后，可以执行 `SAVE_CONFIG` gcode 将配置文件写入 printer.cfg。

可以通过执行 `BED_MESH_PROFILE LOAD=<name>` 加载配置文件。

需要注意的是，每次执行 BED_MESH_CALIBRATE 时，当前状态都会自动保存到 _default_ 配置文件中。可以按如下方式删除 _default_ 配置文件：

`BED_MESH_PROFILE REMOVE=default`

任何其他保存的配置文件都可以用同样的方式删除，将 _default_ 替换为您希望删除的命名配置文件。


#### 加载默认配置文件

`bed_mesh` 的早期版本在启动时总是加载名为 _default_ 的配置文件（如果存在）。此行为已被移除，改为允许用户确定何时加载配置文件。如果用户希望加载 `default` 配置文件，建议将 `BED_MESH_PROFILE LOAD=default` 添加到其 `START_PRINT` 宏或切片器的"Start G-Code"配置中，具体取决于适用情况。

或者，可以使用 `[delayed_gcode]` 恢复启动时加载配置文件的旧行为：

```ini
[delayed_gcode bed_mesh_init]
initial_duration: .01
gcode:
  BED_MESH_PROFILE LOAD=default
```

### 输出

`BED_MESH_OUTPUT PGP=[0 | 1]`

将当前网格状态输出到终端。请注意，网格本身是输出的。

PGP 参数是 "Print Generated Points" 的缩写。如果设置 `PGP=1`，生成的探测点将输出到终端：

```
// bed_mesh: generated points
// Index | Tool Adjusted | Probe
// 0 | (11.0, 1.0) | (35.0, 6.0)
// 1 | (62.2, 1.0) | (86.2, 6.0)
// 2 | (113.5, 1.0) | (137.5, 6.0)
// 3 | (164.8, 1.0) | (188.8, 6.0)
// 4 | (216.0, 1.0) | (240.0, 6.0)
// 5 | (216.0, 97.0) | (240.0, 102.0)
// 6 | (164.8, 97.0) | (188.8, 102.0)
// 7 | (113.5, 97.0) | (137.5, 102.0)
// 8 | (62.2, 97.0) | (86.2, 102.0)
// 9 | (11.0, 97.0) | (35.0, 102.0)
// 10 | (11.0, 193.0) | (35.0, 198.0)
// 11 | (62.2, 193.0) | (86.2, 198.0)
// 12 | (113.5, 193.0) | (137.5, 198.0)
// 13 | (164.8, 193.0) | (188.8, 198.0)
// 14 | (216.0, 193.0) | (240.0, 198.0)
```

"Tool Adjusted" 点指的是每个点的喷嘴位置，"Probe" 点指的是探针位置。请注意，手动探测时 "Probe" 点将同时指工具和喷嘴位置。

### 清除网格状态

`BED_MESH_CLEAR`

此 gcode 可用于清除内部网格状态。

### 应用 X/Y 偏移

`BED_MESH_OFFSET [X=<value>] [Y=<value>] [ZFADE=<value>]`

这对于具有多个独立挤出机的打印机很有用，因为偏移对于在工具更换后产生正确的 Z 调整是必要的。偏移应相对于主挤出机指定。也就是说，如果副挤出机安装在主挤出机的右侧，则应指定正的 X 偏移；如果副挤出机安装在主挤出机的"后面"，则应指定正的 Y 偏移；如果副挤出机的喷嘴在主挤出机之上，则应指定正的 ZFADE 偏移。

请注意，ZFADE 偏移不会*直接*应用额外的调整。它旨在补偿启用 [网格淡出](#mesh-fade) 时的 `gcode offset`。例如，如果副挤出机比主挤出机高，需要负的 gcode 偏移，即：`SET_GCODE_OFFSET Z=-.2`，可以在 `bed_mesh` 中使用 `BED_MESH_OFFSET ZFADE=.2` 来补偿。
