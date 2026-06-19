# 压力提前

本文档提供有关为特定喷嘴和耗材调整"压力提前"配置变量的信息。压力提前功能有助于减少渗出。有关压力提前如何实现的更多信息，请参阅[运动学](Kinematics.md)文档。

## 调整压力提前

压力提前做两件有用的事情——它减少了非挤出移动期间的渗出，并减少了转角处的拉丝。本指南使用第二个功能（减少转角处的拉丝）作为调整机制。

为了校准压力提前，打印机必须已配置并可运行，因为调整测试涉及打印和检查测试对象。建议在运行测试之前完整阅读本文档。

使用切片软件为 [docs/prints/square_tower.stl](prints/square_tower.stl) 中的大空心正方形生成 g-code。使用高速度（例如 100mm/s）、零填充和粗略的层高（层高应约为喷嘴直径的 75%）。确保在切片软件中禁用任何"动态加速度控制"和"斜接缝"。

通过发出以下 G-Code 命令为测试做准备：
```
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=1 ACCEL=500
```
此命令使喷嘴在转角处移动得更慢，以强调挤出机压力的效果。然后对于具有直接驱动挤出机的打印机，运行命令：
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.005
```
对于长鲍登管挤出机，使用：
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.020
```
然后打印对象。完全打印后，测试打印件如下所示：

![tuning_tower](/img/tuning_tower.jpg)

上面的 TUNING_TOWER 命令指示 Kalico 在打印的每一层上更改 pressure_advance 设置。打印中较高的层将设置较大的 pressure_advance 值。低于理想 pressure_advance 设置的层将在转角处出现拉丝，而高于理想设置的层可能导致圆角和转角前的挤出不良。

如果观察到转角不再打印良好，可以提前取消打印（从而避免打印已知高于理想 pressure_advance 值的层）。

检查打印件，然后使用数字卡尺找到具有最佳质量转角的高度。如有疑问，选择较低的高度。

![tune_pa](/img/tune_pa.jpg)

然后可以计算 pressure_advance 值为 `pressure_advance = <start> + <measured_height> * <factor>`。（例如，`0 + 12.90 * .020` 为 `.258`。）

如果有助于识别最佳 pressure_advance 设置，可以选择 START 和 FACTOR 的自定义设置。执行此操作时，请务必在每次测试打印开始时发出 TUNING_TOWER 命令。

典型的 pressure_advance 值在 0.050 到 1.000 之间（高端通常仅用于鲍登管挤出机）。如果 pressure_advance 高达 1.000 仍没有显著改善，则 pressure advance 不太可能改善打印质量。返回到禁用 pressure advance 的默认配置。

虽然此调整练习直接改善了转角质量，但值得记住的是，良好的 pressure advance 配置还可以减少整个打印过程中的渗出。

测试完成后，在配置文件的 `[extruder]` 节中设置 `pressure_advance = <calculated_value>` 并发出 RESTART 命令。RESTART 命令将清除测试状态，并将加速度和转角速度恢复为其正常值。

## 重要说明

* pressure advance 值取决于挤出机、喷嘴和耗材。来自不同制造商或具有不同颜料的耗材通常需要显著不同的 pressure advance 值。因此，应在每台打印机和每卷耗材上校准 pressure advance。

* 打印温度和挤出速率可能会影响 pressure advance。务必在调整 pressure advance 之前调整[挤出机 rotation_distance](Rotation_Distance.md#calibrating-rotation_distance-on-extruders) 和[喷嘴温度](http://reprap.org/wiki/Triffid_Hunter%27s_Calibration_Guide#Nozzle_Temperature)。

* 测试打印设计为以高挤出机流量运行，但其他方面使用"正常"切片软件设置。高流量通过使用高打印速度（例如 100mm/s）和粗略的层高（通常约为喷嘴直径的 75%）获得。其他切片软件设置应类似于其默认值（例如 2 或 3 条线的周长，正常的回缩量）。将外部周长速度设置为与打印其余部分相同的速度可能很有用，但这不是必需的。

* 测试打印在每个转角显示不同的行为是很常见的。通常切片软件会安排在一个转角处更改层，这可能导致该转角与其他三个转角明显不同。如果发生这种情况，请忽略该转角并使用其他三个转角调整 pressure advance。其余转角略有变化也很常见。（这可能是由于打印机框架在某些方向上的反应存在微小差异造成的。）尝试选择对所有其余转角都有效的值。如有疑问，选择较低的 pressure advance 值。

* 如果使用高 pressure advance 值（例如超过 0.200），可能会发现挤出机在返回打印机的正常加速度时会跳过。pressure advance 系统通过在加速期间推入额外的耗材并在减速期间回缩该耗材来考虑压力。在高加速度和高 pressure advance 下，挤出机可能没有足够的扭矩来推动所需的耗材。如果发生这种情况，请使用较低的加速度值或禁用 pressure advance。

* 一旦在 Kalico 中调整好 pressure advance，在切片软件中配置小的回缩值（例如 0.75mm）并使用切片软件的"回缩时擦拭"选项（如果可用）可能仍然有用。这些切片软件设置可能有助于抵消由耗材内聚力（塑料粘性导致耗材被拉出喷嘴）引起的渗出。建议禁用切片软件的"回缩时 Z 抬升"选项。

* pressure advance 系统不会改变工具头的时序或路径。启用 pressure advance 的打印将与不启用 pressure advance 的打印花费相同的时间。Pressure advance 也不会改变打印期间挤出的耗材总量。Pressure advance 导致在移动加速和减速期间产生额外的挤出机运动。非常高的 pressure advance 设置将在加速和减速期间导致非常大量的挤出机运动，并且没有配置设置对此运动量施加限制。
