# 床面网格

床面网格模块可用于补偿床面不规则性，以在整个床面上实现更好的第一层。应该注意，基于软件的校正不会实现完美的结果，它只能近似床面的形状。床面网格也无法补偿机械和电气问题。如果轴倾斜或探针不准确，则 bed_mesh 模块将无法从探针过程接收准确的结果。

在进行网格校准之前，您需要确保您的探针的 Z 偏移已校准。如果使用端点开关进行 Z 归位，也需要进行校准。有关更多信息，请参阅 [Probe Calibrate](Probe_Calibrate.md) 和 [Manual Level](Manual_Level.md) 中的 Z_ENDSTOP_CALIBRATE。

## 基本配置

### 矩形床面
此示例假设打印机具有 250 mm x 220 mm 矩形床面和探针 x 偏移为 24 mm、y 偏移为 5 mm。

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
  工具在各点之间移动的速度。

- `horizontal_move_z: 5`\
  _默认值: 5_\
  探针在各点之间移动前上升的 Z 坐标。

- `mesh_min: 35, 6`\
  _必需_\
  第一个探针坐标，最接近原点。此坐标相对于探针的位置。

- `mesh_max: 240, 198`\
  _必需_\
  距离原点最远的探针坐标。这不一定是最后探针的点，因为探针过程以之字形方式进行。与 `mesh_min` 一样，此坐标相对于探针的位置。

- `probe_count: 5, 3`\
  _默认值: 3, 3_\
  在每个轴上探针的点数，指定为 X、Y 整数值。在此示例中，沿 X 轴将探针 5 个点，沿 Y 轴 3 个点，总共 15 个探针点。请注意，如果需要方形网格（例如 3x3），可以将其指定为应用于两个轴的单个整数值，即 `probe_count: 3`。请注意，网格在每个轴上需要最少 3 个 probe_count。

下图演示了如何使用 `mesh_min`、`mesh_max` 和 `probe_count` 选项生成探针点。箭头指示探针过程的方向，从 `mesh_min` 开始。作为参考，当探针在 `mesh_min` 时，喷嘴将位于 (11, 1)，当探针在 `mesh_max` 时，喷嘴将位于 (206, 193)。

![bedmesh_rect_basic](img/bedmesh_rect_basic.svg)

### 圆形床面
此示例假设打印机配备圆形床面，半径为 100mm。我们将使用与矩形示例相同的探针偏移，X 方向 24 mm，Y 方向 5 mm。

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
  相对于 `mesh_origin` 的探针网格的半径（毫米）。请注意，探针的偏移限制了网格半径的大小。在此示例中，大于 76 的半径将使工具超出打印机的范围。

- `mesh_origin: 0, 0`\
  _默认值: 0, 0_\
  网格的中心点。此坐标相对于探针的位置。虽然默认值为 0, 0，但调整原点可能很有用，以便探针床面的更大部分。请参阅下面的图示。

- `round_probe_count: 5`\
  _默认值: 5_\
  一个整数值，定义沿 X 和 Y 轴的最大探针点数。按"最大"，我们指沿网格原点探针的点数。此值必须是奇数，因为需要探针网格的中心。

下图显示了探针点的生成方式。如您所见，将 `mesh_origin` 设置为 (-10, 0) 允许我们指定更大的网格半径 85。

![bedmesh_round_basic](img/bedmesh_round_basic.svg)

## 高级配置

下面详细解释更多高级配置选项。每个示例将基于上面显示的基本矩形床配置构建。每个高级选项以相同的方式应用于圆形床。

### 网格插值

虽然可以使用简单的双线性插值直接采样探针矩阵以确定探针点之间的 Z 值，但使用更高级的插值算法来增加网格密度通常很有用。这些算法向网格添加曲率，试图模拟床面的材料特性。床面网格提供拉格朗日和双三次插值来完成此任务。

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
  `mesh_pps` 选项是"每段网格点"的缩写。此选项指定为沿 X 和 Y 轴的每个段插值多少个点。考虑"段"为每个探针点之间的空间。与 `probe_count` 一样，`mesh_pps` 指定为 X、Y 整数对，也可以指定为应用于两个轴的单个整数。在此示例中，沿 X 轴有 4 个段，沿 Y 轴有 2 个段。这评估为沿 X 8 个插值点、沿 Y 6 个插值点，导致 13x9 网格。请注意，如果 mesh_pps 设置为 0，则禁用网格插值，探针矩阵将被直接采样。

- `algorithm: lagrange`\
  _默认值: lagrange_\
  用于插值网格的算法。可以是 `lagrange` 或 `bicubic`。拉格朗日插值限于 6 个探针点，因为更多样本往往会产生振荡。双三次插值在每个轴上需要至少 4 个探针点，如果指定少于 4 个点，则强制使用拉格朗日采样。如果 `mesh_pps` 设置为 0，则此值被忽略，因为不执行网格插值。

- `bicubic_tension: 0.2`\
  _默认值: 0.2_\
  如果 `algorithm` 选项设置为双三次，可能会指定张力值。张力越高，插值斜率越多。调整此项时要小心，因为较高的值也会产生更多超调，这将导致插值值高于或低于探针点。

下图显示了上述选项如何用于生成插值网格。

![bedmesh_interpolated](img/bedmesh_interpolated.svg)

### 移动分割

床面网格通过拦截 gcode 移动命令并对其 Z 坐标应用变换来工作。长移动必须分割成较小的移动以正确跟随床面的形状。下面的选项控制分割行为。

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
  在执行分割前检查所需 Z 变化的最小距离。在此示例中，长于 5mm 的移动将由算法遍历。每 5mm 将进行网格 Z 查找，将其与前一次移动的 Z 值进行比较。如果增量满足由 `split_delta_z` 设置的阈值，移动将被分割并继续遍历。此过程重复，直到到达移动的末尾，其中将应用最终调整。短于 `move_check_distance` 的移动将直接将正确的 Z 调整应用到移动，无需遍历或分割。

- `split_delta_z: .025`\
  _默认值: .025_\
  如上所述，这是触发移动分割所需的最小偏差。在此示例中，任何 Z 值偏差 +/- .025mm 将触发分割。

通常，这些选项的默认值足够，实际上 `move_check_distance` 的默认值 5mm 可能有点过头。但是，高级用户可能希望试验这些选项，以试图为第一层挤出最优性能。

### 网格淡出

启用"淡出"时，Z 调整在配置定义的距离上逐步消除。这是通过对层高度进行小的调整来完成的，根据床面的形状增加或减少。当淡出完成时，不再应用 Z 调整，允许打印的顶部平坦而不是镜像床面的形状。淡出也可能有一些不理想的特性，如果淡出太快，可能会导致打印上可见的伪影。此外，如果您的床面显著弯曲，淡出可能会收缩或拉伸打印的 Z 高度。因此，淡出默认被禁用。

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
  开始逐步消除调整的 Z 高度。在开始淡出过程前向下推进几层是个好主意。

- `fade_end: 10`\
  _默认值: 0_\
  淡出应完成的 Z 高度。如果此值低于 `fade_start`，则淡出被禁用。根据打印表面弯曲程度，可能需要调整此值。显著弯曲的表面应在更长的距离上淡出。接近平坦的表面可能能够减少此值以更快地淡出。如果使用 `fade_start` 的默认值 1，10mm 是一个合理的起始值。

- `fade_target: 0`\
  _默认值: 网格的平均 Z 值_\
  `fade_target` 可以认为是淡出完成后应用于整个床面的额外 Z 偏移。通常，我们希望此值为 0，但在某些情况下不应该是 0。例如，假设您的床上的归位位置是一个异常值，比床面探针平均高度低 0.2 mm。如果 `fade_target` 为 0，淡出将在整个床面上平均缩小打印 0.2 mm。通过将 `fade_target` 设置为 0.2，归位区域将扩大 0.2 mm，但是，床面的其余部分将准确调整大小。通常，最好从配置中省略 `fade_target`，以便使用网格的平均高度，但是如果想在床面的特定部分上打印，调整淡出目标可能是需要的。

### 配置零参考位置

许多探针容易"漂移"，即由热量或干扰引起的探针不准确。这可能使计算探针的 z 偏移变得困难，特别是在不同床温下。因此，一些打印机使用端点开关对 Z 轴进行归位，使用探针来校准网格。在此配置中，可能会偏移网格，以便 (X, Y) `参考位置` 应用零调整。`参考位置` 应该是进行 [Z_ENDSTOP_CALIBRATE](./Manual_Level.md#calibrating-a-z-endstop) 纸张测试的床面位置。bed_mesh 模块为指定此坐标提供 `zero_reference_position` 选项：

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
  _默认值: None (disabled)_\
  `zero_reference_position` 期望 (X, Y) 坐标与上面描述的 `参考位置` 匹配。如果坐标位于网格内，则网格将被偏移，以便参考位置应用零调整。如果坐标位于网格外，则将在校准后探针该坐标，将生成的 z 值用作 z 偏移。请注意，此坐标不得位于指定为 `faulty_region` 的位置（如果需要探针）。

#### 弃用的 relative_reference_index

使用 `relative_reference_index` 选项的现有配置必须更新为使用 `zero_reference_position`。对 [BED_MESH_OUTPUT PGP=1](#output) gcode 命令的响应将包含与索引关联的 (X, Y) 坐标；此位置可用作 `zero_reference_position` 的值。输出看起来类似于以下内容：

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

_注意: 上述输出在初始化期间也打印在 `klippy.log` 中。_

使用上面的示例，我们看到 `relative_reference_index` 与其坐标一起打印。因此 `zero_reference_position` 为 `131.5, 108`。

### 故障区域

由于特定位置的"故障"，床面的某些区域在探针时可能报告不准确的结果。最好的例子是具有一系列集成磁铁的床，用于保持可移动钢板。这些磁铁处及其周围的磁场可能导致感应探针以比其他情况下更高或更低的距离触发，导致网格不准确代表这些位置的表面。**注意: 这不应与探针位置偏差混淆，后者在整个床面上产生不准确的结果。**

`faulty_region` 选项可以配置为补偿这个影响。如果生成的点位于故障区域内，bed mesh 将尝试探针该区域边界处最多 4 个点。这些探针值将被平均并作为 Z 值插入网格中，位于生成的 (X, Y) 坐标处。

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
  _默认值: None (disabled)_\
  故障区域的定义方式类似于网格本身，其中必须为每个区域指定最小和最大 (X, Y) 坐标。故障区域可能延伸到网格外，但生成的替换点将始终在网格边界内。没有两个区域可能重叠。

下图说明了当生成的点位于故障区域内时如何生成替换点。显示的区域与上面的示例配置中的区域匹配。替换点及其坐标用绿色标识。

![bedmesh_interpolated](img/bedmesh_faulty_regions.svg)

### 自适应网格

自适应床面网格是一种通过仅探针被打印对象使用的床面区域来加快床面网格生成的方法。使用时，该方法将根据定义的打印对象占据的区域自动调整网格参数。

自适应网格区域将从所有定义的打印对象的边界定义的区域计算，因此涵盖每个对象，包括配置中定义的任何边距。计算区域后，探针点数将根据默认网格区域与自适应网格区域的比率按比例缩小。为了说明这一点，请考虑以下示例：

对于 150mmx150mm 床，`mesh_min` 设置为 `25,25`，`mesh_max` 设置为 `125,125`，默认网格区域是 100mmx100mm 正方形。自适应网格区域 `50,50` 意味着自适应区域与默认网格区域之间的比率为 `0.5x0.5`。

如果 `bed_mesh` 配置指定 `probe_count` 为 `7x7`，自适应床网格将使用 4x4 探针点（7 * 0.5 四舍五入）。

![adaptive_bedmesh](img/adaptive_bed_mesh.svg)

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
  在由定义的对象使用的床面区域周围添加边距（毫米）。下图显示了具有 `adaptive_margin` 5mm 的自适应床网格区域。自适应网格区域（绿色区域）计算为使用的床面区域（蓝色区域）加上定义的边距。

  ![adaptive_bedmesh_margin](img/adaptive_bed_mesh_margin.svg)

由其性质，自适应床网格使用被打印的 Gcode 文件定义的对象。因此，预期每个 Gcode 文件将生成探针床面不同区域的网格。因此，自适应床网格不应被重用。预期是如果使用自适应网格，将为每次打印生成新网格。

还重要的是要考虑自适应床网格最适合用于通常能够探针整个床面并实现最大方差小于或等于 1 层高度的机器。具有机械问题的机器，通常通过完整床网格补偿的，在尝试在探针区域"外"进行打印移动时可能会产生不理想的结果。如果完整床网格的方差大于 1 层高度，在使用自适应床网格时必须谨慎，并尝试在探针区域外进行打印移动。

## 床面网格 Gcodes

### 校准

`BED_MESH_CALIBRATE PROFILE=<name> METHOD=[manual | automatic] [<probe_parameter>=<value>] [<mesh_parameter>=<value>] [ADAPTIVE=[0|1] [ADAPTIVE_MARGIN=<value>]`\
_默认配置文件: default_\
_默认方法: 如果检测到探针则自动，否则手动_ \
_默认自适应: 0_ \
_默认自适应边距: 0_

启动床面网格校准的探针过程。

网格将保存到由 `PROFILE` 参数指定的配置文件中，或如果未指定则保存到 `default`。如果选择 `METHOD=manual`，则将进行手动探针。在自动和手动探针之间切换时，生成的网格点将自动调整。

可以指定网格参数来修改探针区域。以下参数可用：

- 矩形床（笛卡尔）：
  - `MESH_MIN`
  - `MESH_MAX`
  - `PROBE_COUNT`
- 圆形床（增量）：
  - `MESH_RADIUS`
  - `MESH_ORIGIN`
  - `ROUND_PROBE_COUNT`
- 所有床：
  - `ALGORITHM`
  - `ADAPTIVE`
  - `ADAPTIVE_MARGIN`

有关每个参数如何应用于网格的详细信息，请参阅上面的配置文档。

### 配置文件

`BED_MESH_PROFILE SAVE=<name> LOAD=<name> REMOVE=<name>`

执行 BED_MESH_CALIBRATE 后，可以将当前网格状态保存到命名配置文件中。这使得无需重新探针床面即可加载网格成为可能。配置文件使用 `BED_MESH_PROFILE SAVE=<name>` 保存后，可以执行 `SAVE_CONFIG` gcode 将配置文件写入 printer.cfg。

配置文件可以通过执行 `BED_MESH_PROFILE LOAD=<name>` 加载。

应该注意，每次发生 BED_MESH_CALIBRATE 时，当前状态会自动保存到 _default_ 配置文件。_default_ 配置文件可以如下移除：

`BED_MESH_PROFILE REMOVE=default`

任何其他保存的配置文件可以以相同的方式移除，将 _default_ 替换为您希望移除的命名配置文件。

#### 加载默认配置文件

`bed_mesh` 的早期版本在启动时始终加载名为 _default_ 的配置文件（如果存在）。此行为已被移除，以支持允许用户确定何时加载配置文件。如果用户希望加载 `default` 配置文件，建议将 `BED_MESH_PROFILE LOAD=default` 添加到其 `START_PRINT` 宏或其切片器的"Start G-Code"配置中，以适用者为准。

或者，可以通过 `[delayed_gcode]` 恢复在启动时加载配置文件的旧行为：

```ini
[delayed_gcode bed_mesh_init]
initial_duration: .01
gcode:
  BED_MESH_PROFILE LOAD=default
```

### 输出

`BED_MESH_OUTPUT PGP=[0 | 1]`

将当前网格状态输出到终端。请注意，网格本身是输出的

PGP 参数是"Print Generated Points"的缩写。如果设置 `PGP=1`，生成的探针点将输出到终端：

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

"Tool Adjusted"点指每个点的喷嘴位置，"Probe"点指探针位置。请注意，手动探针时，"Probe"点将指代工具和喷嘴位置。

### 清除网格状态

`BED_MESH_CLEAR`

此 gcode 可用于清除内部网格状态。

### 应用 X/Y 偏移

`BED_MESH_OFFSET [X=<value>] [Y=<value>] [ZFADE=<value>]`

这对具有多个独立挤出机的打印机很有用，因为工具更换后需要偏移来产生正确的 Z 调整。偏移应相对于主挤出机指定。也就是说，如果次挤出机安装在主挤出机右侧，应指定正 X 偏移，如果次挤出机安装在主挤出机"后面"，应指定正 Y 偏移，如果次挤出机喷嘴位于主挤出机喷嘴上方，应指定正 ZFADE 偏移。

请注意，ZFADE 偏移 *不能* 直接应用额外调整。它旨在在启用 [网格淡出](#mesh-fade) 时补偿 `gcode 偏移`。例如，如果次挤出机高于主挤出机，需要负 gcode 偏移，即：`SET_GCODE_OFFSET Z=-.2`，它可以在 `bed_mesh` 中通过 `BED_MESH_OFFSET ZFADE=.2` 来解决。