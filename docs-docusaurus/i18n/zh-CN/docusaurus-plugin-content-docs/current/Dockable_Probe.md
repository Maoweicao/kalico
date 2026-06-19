# 可拆卸探针

可拆卸探针通常是安装在打印体上的微动开关，通过某种机械耦合方式连接到工具头。这种耦合通常通过磁铁完成，但也支持各种设计，包括伺服和步进驱动的耦合。

## 基本配置

要使用可拆卸探针，至少需要以下选项。一些用户可能从基于宏的命令集过渡过来，`[probe]` 配置部分的许多选项是相同的。`[dockable_probe]` 模块首先是一个 `[probe]`，但具有额外的功能。大多数可以为 `[probe]` 指定的选项对 `[dockable_probe]` 也有效。

```
[dockable_probe]
pin:
z_offset:
sample_retract_dist:
approach_position:
dock_position:
detach_position:
(check_open_attach: OR probe_sense_pin:) AND/OR dock_sense_pin:
```

### 连接和断开位置

- `dock_position: 300, 295, 0`\
  _必需_\
  这是工具头需要定位的 XYZ 坐标，以便连接探针。此参数是用逗号分隔的 X、Y 和 Z。

  许多配置将底座安装在移动龙门架上。这意味着 Z 轴定位无关紧要。但是，在执行对接步骤之前，可能需要将龙门架移开热床或其他打印机部件。在这种情况下，指定 `z_hop` 以强制 Z 轴移动。

  其他配置可能将底座安装在打印机热床旁边，因此在连接探针之前必须知道 Z 位置。在此配置中，_必须_提供 Z 轴参数，且在连接探针之前 Z 轴_必须_已归位。

- `approach_position: 300, 250, 0`\
  _必需_\
  最常见的底座设计使用从底座延伸出的叉或臂。为了将探针连接到工具头，工具头必须移入和移出底座到特定位置，以便这些臂能够捕获探针主体。

  与 `dock_position` 一样，不需要 Z 位置，但如果指定了，则工具头将在移动到 X、Y 坐标之前先移动到该 Z 位置。

  对于磁性耦合探针，`approach_position` 应与探针底座保持足够的距离，以使探针主体上的磁铁不会被工具头上的磁铁吸引。

- `detach_position: 250, 295, 0`\
  _必需_\
  大多数带有磁铁的探针需要工具头沿某个方向移动，以滑动方式剥离磁铁。这是为了防止磁铁因反复拉扯而脱位，从而影响探针精度。`detach_position` 通常定义为垂直于底座的点，以便当工具头移动时，探针保持在底座上但从工具头安装座上干净地脱离。

  与 `dock_position` 一样，不需要 Z 位置，但如果指定了，则工具头将在移动到 X、Y 坐标之前先移动到该 Z 位置。

  对于磁性耦合探针，`detach_position` 应与探针底座保持足够的距离，以使探针主体上的磁铁不会被工具头上的磁铁吸引。

- `extract_position: 295, 250, 0`\
  _默认值: approach\_position_\
  Euclid 探针要求工具头向不同方向移动以提取或插入 mag_probe。

- `insert_position: 295, 250, 0`\
  _默认值: extract\_position_\
  当底座在龙门架上时，通常与 Euclid 探针的提取位置相同。

- `z_hop: 15.0`\
  _默认值: 无_\
  在连接/断开探针之前抬升 Z 轴的距离（以 mm 为单位）。如果 Z 轴已经归位且当前 Z 位置小于 `z_hop`，则会将头部抬升到 `z_hop` 的高度。如果 Z 轴尚未归位，则头部抬升 `z_hop`。默认是不执行 Z hop。

- `restore_toolhead: False|True`\
  _默认值: True_\
  工具头的位置恢复到连接/断开移动之前的位置。见下表。

| 命令                    | 模块              | restore_th=True | restore_th=False | 备注                           |
| ----------------------- | ----------------- | --------------- | ---------------- | ------------------------------ |
| ATTACH_PROBE            | dockable_probe.py | True            | False            |                                |
| Z_TILT_ADJUST           | probe.py          | True            | False            |                                |
| QUAD_GANTRY_LEVEL       | probe.py          | True            | False            |                                |
| PROBE                   | probe.py          | True            | True             |                                |
| PROBE_ACCURACY          | probe.py          | True            | True             |                                |
| AXIS_TWIST_COMPENSATION | probe.py          | True            | True             |                                |
| CALIBRATE_Z             | z_calibration.py  | True            | False            |                                |
| G28 Z                   | probe.py          | True            | True             | **仅适用于 z_virtual_endstop** |


## 位置示例

探针安装在打印热床后方的框架上，Z 位置固定。要连接探针，工具头将向后移动然后向前移动。要断开，工具头将向后移动，然后向侧面移动。

```
+--------+
|   p>   |
|   ^    |
|        |
+--------+
```

```
approach_position: 150, 300, 5
dock_position: 150, 330, 5
detach_position: 170, 330
```


探针安装在移动龙门架的侧面，热床固定。在这里，探针可以在任何 Z 位置连接。要连接探针，工具头将向侧面移动然后向后移动。要断开，工具头将向侧面移动然后向前移动。

```
+--------+
|        |
| p<     |
| v      |
+--------+
```

```
approach_position: 50, 150
dock_position: 10, 150
detach_position: 10, 130
```


探针安装在固定龙门架的侧面，热床在 Z 方向移动。探针可以在任何 Z 位置连接，但为了安全起见强制 Z hop。工具头移动与上述相同。

```
+--------+
|        |
| p<     |
| v      |
+--------+
```

```
approach_position: 50, 150
dock_position: 10, 150
detach_position: 10, 130
z_hop: 15
```


Euclid 风格的探针，要求连接和断开移动以相反的顺序进行。连接：接近，移动到底座，提取。断开：移动到提取位置，移动到底座，移动到接近位置。接近和断开位置相同，提取和插入位置也相同。

```
连接:
+--------+
|        |
| p<     |
| v      |
+--------+
断开:
+--------+
|        |
| p>     |
| ^      |
+--------+
```

```
approach_position: 50, 150
dock_position: 10, 150
extract_position: 10, 130
detach_position: 50, 150
z_hop: 15
```

### 附加 G 代码

如果您的探针有特殊的设置/拆卸步骤（例如，移动伺服），您可以使用以下配置选项在连接/断开探针之前或之后执行自定义 G 代码，而不是覆盖[单独移动](#individual-movements)命令：

- `pre_attach_gcode:`\
  _默认值: 无_\
  在连接探针之前立即执行的 G 代码。

- `post_attach_gcode:`\
  _默认值: 无_\
  在连接探针之后立即执行的 G 代码。

- `pre_detach_gcode:`\
  _默认值: 无_\
  在断开探针之前立即执行的 G 代码。

- `post_detach_gcode:`\
  _默认值: 无_\
  在断开探针之后立即执行的 G 代码。

### 归位

不需要特定于可拆卸探针的配置。但是，当将探针用作虚拟限位开关时，需要使用 `[safe_z_home]` 或 `[homing_override]`。

#### 探针作为虚拟限位开关的示例
- #### 归位覆盖
```elixir
[homing_override]
axes: xyz
set_position_z: 0
gcode:
  
  G90
  {% set home_all = 'X' not in params and 'Y' not in params and 'Z' not in params %}

  {% if home_all or 'X' in params %}
    G0 Z10
    G28 X
  {% endif %}

  {% if home_all or 'Y' in params %}
    G0 Z10
    G28 Y
  {% endif %}
  
  {% if home_all or 'Z' in params %}
    ATTACH_PROBE
    MOVE_AVOIDING_DOCK X=150 Y=150 SPEED=300
    # 探针已连接，无需返回底座。
    G28 Z  
  {% endif %}
```

- #### safe_z_home
使用 safe_z_home 归位 Z 时，工具头将移动到 home_xy_position，然后移动到底座并返回到 home_xy_position。
```elixir
[safe_z_home]
home_xy_position: 150,150
z_hop: 10
```

使用 `safe_z_home` 时，可以在 Z 归位后自动断开探针。
```elixir
[dockable_probe]
detach_dockable_before_z_home: True
```


### 探针连接验证

鉴于此类探针的性质，有必要在尝试探测移动之前验证它是否已成功连接。可以使用几种方法来验证探针连接状态。

- `check_open_attach:`\
  _默认值: 无_\
  某些探针在连接时会报告 `OPEN`，在非探测状态下断开时会报告 `TRIGGERED`。当 `check_open_attach` 设置为 `True` 时，会在执行探针连接或断开操作后检查探针引脚的状态。如果探针在连接后未立即读取 `OPEN`，将引发错误并中止进一步操作。

  这旨在防止喷嘴撞到热床，因为假设如果探测前探针引脚读取 `TRIGGERED`，则探针未连接。

  将其设置为 `False` 将导致如果连接后探针未读取 `TRIGGERED`，则中止所有操作。

- `probe_sense_pin:`\
  _默认值: 无_\
  探针可能包含一个用于连接验证的单独引脚。这是一个标准引脚定义，类似于限位开关引脚，定义了如何处理来自传感器的输入。与 `check_open_attach` 选项类似，检查是在工具连接或断开探针后立即执行的。如果在尝试连接后未检测到探针，或者在尝试断开后探针仍然连接，将引发错误并中止进一步操作。

- `dock_sense_pin:`\
  _默认值: 无_\
  底座可以在其设计中包含传感器或开关，以报告探针当前位于底座中。`dock_sense_pin` 可用于提供验证，确保探针正确放置在底座中。这是一个类似于限位开关引脚的标准引脚定义，定义了如何处理来自传感器的输入。在尝试连接探针之前和尝试断开探针之后，会检查此引脚。如果在底座中未检测到探针，将引发错误并中止进一步操作。

- `dock_retries: 5`\
  _默认值: 0_\
  磁性探针可能需要多次尝试才能连接或断开。如果指定了 `dock_retries` 且探针未能连接或断开，则会重复连接/断开操作直到成功。如果达到重试限制且探针仍处于不正确的状态，将引发错误并中止进一步操作。

## 工具速度

- `attach_speed: 5.0`\
  _默认值: 探针 `speed` 或 5_\
  在 `MOVE_TO_DOCK_PROBE` 期间连接探针时的移动速度。

- `detach_speed: 5.0`\
  _默认值: 探针 `speed` 或 5_\
  在 `MOVE_TO_DETACH_PROBE` 期间断开探针时的移动速度。

- `travel_speed: 5.0`\
  _默认值: 探针 `speed` 或 5_\
  在 `MOVE_TO_APPROACH_PROBE` 期间接近探针时以及在连接/断开后将工具头返回到先前位置时的移动速度。

## 安全对接区域

定义了安全对接区域以避免在探针连接/断开移动期间与底座碰撞。参见 `MOVE_AVOIDING_DOCK`。

- `safe_dock_distance:`\
  _默认值: approach\_position 或 insert\_position 到底座的最小距离_ \
  这是在插件的第一个版本中引入的。它定义了在 ATTACH/DETACH_PROBE 操作期间以对接位置为中心的安全区域。
  接近、插入和断开位置应在此区域之外。

- `safe_position: 250, 295, 0`
  _默认值: approach_position_
  确保 MOVE_AVOIDING_DOCK 行程不会超出范围的安全位置

### MOVE_AVOIDING_DOCK 描述
![安全对接区域](/img/move_avoiding_dock.jpg)
下面描述的策略被连接和断开命令用于避免底座碰撞。

> [!NOTE]  
> 默认的 `safe_position` 是 `approach_position`。为了帮助确定避让路径并防止超出范围，应将其配置为安全区域内最远离"超出范围"区域的点。

说明了以下几种情况：
1. 从 `A` 移动到 `B`：请求的轨迹经过安全对接区域，因此计算的轨迹绕过对接区域，接近安全位置。
2. 从 `A'` 移动到 `B`：工具头通过最短路径离开安全对接区域，然后按之前方式到达 `B`。
3. 从 `A` 移动到 `B'`：由于 `B'` 在安全区域内，工具头停止在 `B"`。
4. 从 `A'` 移动到 `B'`：工具头通过最短路径离开安全对接区域。

## 可拆卸探针 G 代码

### 通用

`ATTACH_PROBE`

此命令将工具头移动到底座，连接探针，并将其返回到先前位置。如果探针已连接，该命令不会执行任何操作。

此命令将调用 `MOVE_TO_APPROACH_PROBE`、`MOVE_TO_DOCK_PROBE` 和 `MOVE_TO_EXTRACT_PROBE`。

`DETACH_PROBE`

此命令将工具头移动到底座，断开探针，并将其返回到先前位置。如果探针已断开，该命令不会执行任何操作。

此命令将调用 `MOVE_TO_APPROACH_PROBE`、`MOVE_TO_DOCK_PROBE` 和 `MOVE_TO_DETACH_PROBE`。

### 单独移动

这些命令在设置期间很有用，可防止完整的连接/断开序列撞到热床或损坏探针/底座。

如果您的探针有特殊的设置/拆卸步骤（例如移动伺服），可以通过在配置中使用[附加 G 代码](#additional-g-codes)或覆盖以下 G 代码来实现。

`MOVE_TO_APPROACH_PROBE`

此命令将工具头移动到 `approach_position`。可以覆盖此命令以移动伺服（如果连接探针需要）。

`MOVE_TO_DOCK_PROBE`

此命令将工具头移动到 `dock_position`。

`MOVE_TO_EXTRACT_PROBE`

此命令将工具头移动到 `extract_position`。

`MOVE_TO_INSERT_PROBE`

此命令将工具头移动到 `insert_position`。

`MOVE_TO_DETACH_PROBE`

此命令将工具头移动到 `detach_position`。可以覆盖此命令以移动伺服（如果断开探针需要）。

`MOVE_AVOIDING_DOCK [X=<value>] [Y=<value>] [SPEED=<value>]`

此命令将工具头移动到绝对坐标，避开安全对接区域。

### 状态

`QUERY_DOCKABLE_PROBE`

在 gcode 终端中响应当前探针状态。有效状态为 UNKNOWN、ATTACHED 和 DOCKED。这在设置期间很有用，可确认探针配置是否按预期工作。

`SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0|1`

在需要探针的操作期间启用/禁用探针的自动连接/断开。

此命令在打印开始宏中很有用，因为宏中将使用探针执行多个操作，而无需断开探针。例如：

```
SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0
G28
ATTACH_PROBE                             # 显式连接探针
QUAD_GANTRY_LEVEL                        # 校准龙门架与热床平行
BED_MESH_CALIBRATE                       # 创建热床网格
DETACH_PROBE                             # 手动断开探针
SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=1  # 确保探针在未来已连接
```

## 典型探针执行流程

### 探测开始时：

    - 执行需要使用探针的 gcode 命令。

    - 这会触发探针连接。

    - 如果配置了，会检查底座感应引脚以查看探针当前是否在底座中。

    - 将工具头位置与底座位置进行比较。

    - 执行 pre_attach_gcode

    - 如果工具头在最小安全半径之外，则命令工具头移动到接近向量，即与底座角度对齐的距底座最小安全距离处的位置。(MOVE_TO_APPROACH_PROBE)

    - 如果工具头在最小安全半径之内，则命令工具头移动到接近向量线上最近的点。(MOVE_TO_APPROACH_PROBE)

    - 工具沿接近向量移动到底座坐标。(MOVE_TO_DOCK_PROBE)

    - 命令工具头沿底座角度反方向移出底座，回到最小安全距离。(MOVE_TO_EXTRACT_PROBE)

    - 执行 post_attach_gcode

    - 如果配置了，会检查探针是否已连接。

    - 如果探针未连接，模块可能会重试直到连接或引发错误。

    - 如果配置了，会检查底座感应引脚以查看探针是否仍然存在，模块可能会重试直到探针不存在或引发错误。

    - 探针移动到第一个探测点并开始探测。

### 探测完成后：

    - 探针不再需要后，触发探针断开。

    - 将工具头位置与底座位置进行比较。

    - 执行 pre_detach_gcode

    - 如果工具头在最小安全半径之外，则命令工具头移动到接近向量，即与底座角度对齐的距底座最小安全距离处的位置。(MOVE_TO_APPROACH_PROBE)

    - 如果工具头在最小安全半径之内，则命令工具头移动到接近向量线上最近的点。(MOVE_TO_APPROACH_PROBE)

    - 工具头沿接近向量移动到底座坐标。(MOVE_TO_DOCK_PROBE)

    - 命令工具头沿断开向量（如果提供）或基于轴参数计算的方向移动。(MOVE_TO_DETACH_PROBE)

    - 执行 post_detach_gcode

    - 如果配置了，会检查探针是否已断开。

    - 如果探针未断开，模块将工具头移回接近向量并可能重试直到断开或引发错误。

    - 如果配置了，会检查底座感应引脚以查看探针是否在底座中。如果不在，模块将工具头移回接近向量并可能重试直到断开或引发错误。
