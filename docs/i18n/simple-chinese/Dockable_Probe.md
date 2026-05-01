# 可收纳式探针

可收纳式探针通常是安装到打印的本体中的微开关，该本体通过某种机械耦合方式连接到工具头。这种耦合通常通过磁铁完成，虽然支持各种设计，包括伺服和步进电机驱动的耦合。

## 基本配置

要使用可收纳式探针，至少需要以下选项。某些用户可能正在从基于宏的命令集合转换，`[probe]` 配置部分的许多选项是相同的。`[dockable_probe]` 模块首先是 `[probe]`，但具有其他功能。可以为 `[probe]` 指定的大多数选项对 `[dockable_probe]` 有效。

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

### 附着和分离位置

- `dock_position: 300, 295, 0`\
  _必需_\
  这是工具头需要定位以连接探针的 XYZ 坐标。此参数为 X、Y 和 Z，以逗号分隔。

  许多配置在移动龙门架上安装有停靠位。这意味着 Z 轴定位无关。但是，在执行停靠步骤之前可能需要将龙门架清除床面或其他打印机部件。在这种情况下，指定 `z_hop` 以强制 Z 移动。

  其他配置可能在打印机床面旁边安装有停靠位，因此 Z 位置_必须_在连接探针之前已知。在此配置中，Z 轴参数_必须_提供，并且 Z 轴_必须_在连接探针之前进行归位。

- `approach_position: 300, 250, 0`\
  _必需_\
  最常见的停靠设计使用从停靠位延伸出来的叉子或臂。为了将探针连接到工具头，工具头必须移入和远离停靠位到特定位置，以便这些臂可以捕获探针本体。

  与 `dock_position` 一样，Z 位置不是必需的，但如果指定，工具头将在 X、Y 坐标之前移动到该 Z 位置。

  对于磁耦合探针，`approach_position` 应该离探针停靠位足够远，以便探针本体上的磁铁不被工具头上的磁铁吸引。

- `detach_position: 250, 295, 0`\
  _必需_\
  大多数带磁铁的探针需要工具头以滑动运动的方向移动以将磁铁脱离。这是为了防止磁铁因反复拉动而脱座，从而影响探针精度。`detach_position` 通常定义为垂直于停靠位的点，以便当工具头移动时，探针保持停靠但从工具头安装座中干净地分离。

  与 `dock_position` 一样，Z 位置不是必需的，但如果指定，工具头将在 X、Y 坐标之前移动到该 Z 位置。

  对于磁耦合探针，`detach_position` 应该离探针停靠位足够远，以便探针本体上的磁铁不被工具头上的磁铁吸引。

- `extract_position: 295, 250, 0`\
  _默认值：approach\_position_\
  Euclid 探针需要工具头向不同方向移动以提取或停靠磁探针。

- `insert_position: 295, 250, 0`\
  _默认值：extract\_position_\
  对于停靠位在龙门架上的 Euclid 探针，通常与提取位置相同。

- `z_hop: 15.0`\
  _默认值：None_\
  Z 轴在连接/分离探针之前向上提升的距离（以 mm 为单位）。如果 Z 轴已经归位，当前 Z 位置小于 `z_hop`，那么这将把头部抬起到 `z_hop` 的高度。如果 Z 轴还未归位，头部将被抬起 `z_hop`。默认是不实施 Z hop。

- `restore_toolhead: False|True`\
  _默认值：True_\
  工具头的位置恢复到连接/分离运动之前的位置。请参见下表。

| 命令                    | 模块            | restore_th=True | restore_th=False | 注释                           |
| ----------------------- | --------------- | --------------- | ---------------- | ------------------------------ |
| ATTACH_PROBE            | dockable_probe.py | True            | False            |                                |
| Z_TILT_ADJUST           | probe.py          | True            | False            |                                |
| QUAD_GANTRY_LEVEL       | probe.py          | True            | False            |                                |
| PROBE                   | probe.py          | True            | True             |                                |
| PROBE_ACCURACY          | probe.py          | True            | True             |                                |
| AXIS_TWIST_COMPENSATION | probe.py          | True            | True             |                                |
| CALIBRATE_Z             | z_calibration.py  | True            | False            |                                |
| G28 Z                   | probe.py          | True            | True             | **仅适用于 z_virtual_endstop** |


## 位置示例

探针安装在床面后部的框架上，固定 Z 位置。要连接探针，工具头将向后然后向前移动。要分离，工具头将向后移动，然后向一侧移动。

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


探针安装在移动龙门架的一侧，床面固定。这里无论 Z 位置如何都可以连接探针。要连接探针，工具头将向一侧然后向后移动。要分离，工具头将向一侧然后向前移动。

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


探针安装在固定龙门架的一侧，床面在 Z 轴上移动。无论 Z 位置如何探针都可连接，但为了安全起见强制 Z hop。工具头运动与上面相同。

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


Euclid 风格的探针需要附着和分离运动以相反的顺序发生。附着：靠近、移至停靠位、提取。分离：移至提取位置、移至停靠位、移至靠近位置。靠近位置和分离位置相同，提取位置和插入位置也相同。

```
附着：
+--------+
|        |
| p<     |
| v      |
+--------+
分离：
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

### 其他 G 代码

如果探针具有特殊的设置/拆除步骤（例如，移动伺服），可以使用以下配置选项来执行自定义 G 代码，而不是覆盖[单个运动](#individual-movements)命令：

- `pre_attach_gcode:`\
  _默认值：None_\
  在连接探针之前立即执行的 G 代码。

- `post_attach_gcode:`\
  _默认值：None_\
  在连接探针之后立即执行的 G 代码。

- `pre_detach_gcode:`\
  _默认值：None_\
  在分离探针之前立即执行的 G 代码。

- `post_detach_gcode:`\
  _默认值：None_\
  在分离探针之后立即执行的 G 代码。

### 归位

不需要特定于可收纳式探针的配置。但是，当使用探针作为虚拟限位开关时，需要使用 `[safe_z_home]` 或 `[homing_override]`。

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
    # 探针已连接，无需返回停靠位。
    G28 Z  
  {% endif %}
```

- #### safe_z_home
使用 safe_z_home 进行 Z 归位时，工具头将移动到 home_xy_position，然后移动到停靠位，然后返回到 home_xy_position。
```elixir
[safe_z_home]
home_xy_position: 150,150
z_hop: 10
```

使用 `safe_z_home` 时，可以使探针在 Z 归位时自动分离。
```elixir
[dockable_probe]
detach_dockable_before_z_home: True
```


### 探针连接验证

考虑到这种类型探针的性质，有必要验证其是否在尝试探针移动之前成功连接。可以使用多种方法来验证探针连接状态。

- `check_open_attach:`\
  _默认值：None_\
  某些探针在连接时报告 `OPEN`，在分离时的非探针状态下报告 `TRIGGERED`。当 `check_open_attach` 设置为 `True` 时，在执行探针连接或分离操作后检查探针针脚的状态。如果探针在连接探针后立即未读取 `OPEN`，将引发错误并中止进一步操作。

  这旨在防止喷嘴撞到床面，因为假设如果探针针脚在探针前读取 `TRIGGERED`，探针未连接。

  将此设置为 `False` 将在探针不读取 `TRIGGERED` 时连接后中止所有操作。

- `probe_sense_pin:`\
  _默认值：None_\
  探针可能包含用于连接验证的单独针脚。这是一个标准针脚定义，类似于限位开关针脚，定义如何处理来自传感器的输入。与 `check_open_attach` 选项类似，检查在工具连接或分离探针后立即完成。如果在尝试连接后未检测到探针，或在尝试分离后保持连接，将引发错误并中止进一步操作。

- `dock_sense_pin:`\
  _默认值：None_\
  停靠位可以在其设计中并入传感器或开关，以报告探针当前位于停靠位中。`dock_sense_pin` 可用于提供验证，确保探针正确定位在停靠位中。这是一个标准针脚定义，类似于限位开关针脚，定义如何处理来自传感器的输入。在尝试连接探针之前和尝试分离后检查此针脚。如果未检测到停靠位中的探针，将引发错误并中止进一步操作。

- `dock_retries: 5`\
  _默认值：0_\
  磁探针可能需要多次连接或分离尝试。如果指定 `dock_retries` 并且探针未能连接或分离，连接/分离操作将重复进行，直到成功。如果达到重试限制且探针仍未处于正确状态，将引发错误并中止进一步操作。

## 工具速度

- `attach_speed: 5.0`\
  _默认值：探针 `speed` 或 5_\
  在 `MOVE_TO_DOCK_PROBE` 期间连接探针时的移动速度。

- `detach_speed: 5.0`\
  _默认值：探针 `speed` 或 5_\
  在 `MOVE_TO_DETACH_PROBE` 期间分离探针时的移动速度。

- `travel_speed: 5.0`\
  _默认值：探针 `speed` 或 5_\
  在 `MOVE_TO_APPROACH_PROBE` 期间靠近探针时和连接/分离后返回工具头到其先前位置时的移动速度。

## 安全停靠区

定义了安全停靠区以避免在探针连接/分离移动期间与停靠位碰撞。参见 `MOVE_AVOIDING_DOCK`。

- `safe_dock_distance:`\
  _默认值：停靠位的 approach\_position 或 insert\_position 的最小距离_ \
  这在插件的第一个版本中推出。它定义了在 ATTACH/DETACH_PROBE 操作期间以停靠位为中心的安全区域。靠近、插入和分离位置应在该区域之外。  

- `safe_position: 250, 295, 0`
  _默认值：approach_position_
  一个安全位置，以确保 MOVE_AVOIDING_DOCK 行进不超出范围

### MOVE_AVOIDING_DOCK 描述
![safe dock area](./img/move_avoiding_dock.jpg)
下面描述的策略由连接和分离命令使用以避免停靠碰撞。

> [!NOTE]  
> 默认 `safe_position` 是 `approach_position`。为了帮助确定避免路径并防止超出范围移动，应将其配置为停靠区域旁边的点，距离"超出范围移动"区域最远。 

说明了几种情况：
1. 从 `A` 移动到 `B`：请求的轨迹通过安全停靠区，所以计算的轨迹绕过停靠区，靠近安全位置。
2. 从 `A'` 移动到 `B`：工具头以最短路径离开安全停靠区并如前所述到达 `B`。
3. 从 `A` 移动到 `B'`：由于 `B'` 在安全区域，工具头停在 `B"`。
4. 从 `A'` 移动到 `B'`：工具头以最短路径离开安全停靠区。

## 可收纳式探针 G 代码

### 常规

`ATTACH_PROBE`

此命令会将工具头移动到停靠位、连接探针并将其返回到其先前位置。如果探针已连接，命令不执行任何操作。

此命令将调用 `MOVE_TO_APPROACH_PROBE`、`MOVE_TO_DOCK_PROBE` 和 `MOVE_TO_EXTRACT_PROBE`。

`DETACH_PROBE`

此命令会将工具头移动到停靠位、分离探针并将其返回到其先前位置。如果探针已分离，命令不执行任何操作。

此命令将调用 `MOVE_TO_APPROACH_PROBE`、`MOVE_TO_DOCK_PROBE` 和 `MOVE_TO_DETACH_PROBE`。

### 单个运动

这些命令在设置期间很有用，可以防止完整的连接/分离序列撞到床面或损坏探针/停靠位。

如果探针具有特殊的设置/拆除步骤（例如移动伺服），可以通过在配置中使用[其他 G_codes](#additional-g-codes)或覆盖以下 gcodes 来容纳。

`MOVE_TO_APPROACH_PROBE`

此命令会将工具头移动到 `approach_position`。可以覆盖以移动伺服，如果这对连接探针是必需的。

`MOVE_TO_DOCK_PROBE`

此命令会将工具头移动到 `dock_position`。

`MOVE_TO_EXTRACT_PROBE`

此命令会将工具头移动到 `extract_position`。

`MOVE_TO_INSERT_PROBE`

此命令会将工具头移动到 `insert_position`。

`MOVE_TO_DETACH_PROBE`

此命令会将工具头移动到 `detach_position`。可以覆盖以移动伺服，如果这对分离探针是必需的。

`MOVE_AVOIDING_DOCK [X=<value>] [Y=<value>] [SPEED=<value>]`

此命令会将工具头移动到绝对坐标，避免安全停靠区。

### 状态

`QUERY_DOCKABLE_PROBE`

在 gcode 终端中响应当前探针状态。有效状态为 UNKNOWN、ATTACHED 和 DOCKED。这在设置期间很有用，可以确认探针配置是否按预期工作。

`SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0|1`

启用/禁用在需要探针的操作期间自动连接/分离探针。

此命令在打印启动宏中很有用，其中将执行多个需要探针的操作，无需分离探针。例如：

```
SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=0
G28
ATTACH_PROBE                             # 明确连接探针
QUAD_GANTRY_LEVEL                        # 将龙门架平行于床面
BED_MESH_CALIBRATE                       # 创建床面网格
DETACH_PROBE                             # 手动分离探针
SET_DOCKABLE_PROBE AUTO_ATTACH_DETACH=1  # 确保未来连接探针
```

## 典型的探针执行流程

### 探针已启动：

    - 执行需要使用探针的 gcode 命令。

    - 这会触发探针连接。

    - 如果已配置，检查停靠传感器针脚以查看探针当前是否位于停靠位。

    - 工具头位置与停靠位位置进行比较。

    - 执行 pre_attach_gcode

    - 如果工具头在最小安全半径之外，工具头被命令移动到靠近向量，即与停靠位最小安全距离对齐的位置。
      (MOVE_TO_APPROACH_PROBE)

    - 如果工具头在最小安全半径之内，工具头被命令移动到靠近向量线上的最近点。
      (MOVE_TO_APPROACH_PROBE)

    - 工具沿靠近向量移动到停靠坐标。
      (MOVE_TO_DOCK_PROBE)

    - 工具头被命令沿停靠角反方向移出停靠位到最小安全距离。
      (MOVE_TO_EXTRACT_PROBE)

    - 执行 post_attach_gcode

    - 如果已配置，检查探针以查看其是否已连接。

    - 如果探针未连接，模块可能会重试直到连接或引发错误。

    - 如果已配置，检查停靠传感器针脚以查看探针是否仍然存在，模块可能会重试直到探针不存在或引发错误。

    - 探针移动到第一个探针点并开始探针。

### 探针完成：

    - 不再需要探针后，探针被触发分离。

    - 工具头位置与停靠位位置进行比较。

    - 执行 pre_detach_gcode