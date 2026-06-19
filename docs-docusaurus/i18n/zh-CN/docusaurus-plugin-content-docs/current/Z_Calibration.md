# 自动 Z 偏移校准

本文档提供有关自动校准喷嘴 Z 偏移的信息。启用此功能后，手动 Z 偏移或第一层校准变得不必要。它始终计算正确的偏移，与当前温度、使用的喷嘴或使用的打印床或柔性板无关。

# 为什么需要这个

- Voron V1 或 V2 打印机中使用的 Z 限位开关是一个巧妙的设计，因为喷嘴点击固定在打印床上的开关。这使得更换喷嘴无需更改偏移（开关和床面之间）：
  ![endstop offset](/img/z_calibrate-endstop.png)
- 或者，使用表面探测探针（如磁探针）作为 Z 限位开关。这使得更换柔性板无需调整偏移：
  ![probe offset](/img/z_calibrate-probe.png)
  电感式探针将不起作用，因为它不会直接探测床面表面！
- 但是，不能两者兼得吗？

这是可能的，这就是此扩展的功能！

# 要求

但是，有一些使用要求：

- 一个 Z 限位开关，喷嘴尖端在其上驱动开关（如原装 Voron V1/V2 限位开关）。它不能与配置为限位开关的探针虚拟引脚一起使用！
- 打印头上的（磁性）开关式探针
- Z 限位开关和磁探针都已正确配置，归零和任何类型的床面调平都正常工作。
- 需要此配置的磁探针连接和断开宏。

# 它做什么

1. 使用 Z 限位开关对所有轴进行正常归零（这不是此插件的一部分）。之后，在 Z 中有一个定义的零点。从现在起，一切都是相对于此点的。因此，新的归零将更改一切，因为归零不是那么精确。
2. 通过在 Z 限位开关上探测喷嘴尖端来确定喷嘴的高度（如步骤 1 中的归零。但这个可能产生稍微不同的值）：
   ![nozzle position](/img/z_calibrate-nozzle.png)
3. 通过在 Z 限位开关上探测开关体来确定磁探针的高度：
   ![switch position](/img/z_calibrate-switch.png)
4. 计算喷嘴尖端和磁探针触发点之间的偏移：

   `nozzle switch offset = mag probe height - nozzle height + switch offset`

   ![switch offset](/img/z_calibrate-offset.png)

   磁探针的触发点无法直接探测。这就是为什么在限位开关上点击的是开关体而不是触发旋钮。这就是为什么这里使用小的开关偏移来反映旋钮和开关体在触发时的偏移。此偏移是固定的。
5. 通过在床面上用磁探针探测一个点来确定打印表面的高度（最好是已配置/使用网格的中心或"bed_mesh:relative_reference_index"）。
6. 现在，最终偏移计算如下：

   `probe offset = probed height - calculated nozzle switch offset`

7. 最后，通过使用 `SET_GCODE_OFFSET` 命令应用计算的偏移（之前的偏移会被重置！）。

## 干扰

温度或湿度变化不是大问题，因为开关不太受它们的影响，并且所有值都在短时间内探测，只使用相互之间的关系。步骤 2 中的喷嘴高度可以在一段时间后确定，甚至在打印机腔室中比步骤 1 中的归零高出许多摄氏度。这就是为什么再次探测喷嘴，并且可以与第一次归零位置略有不同。

## 示例输出

校准输出及所有确定的位置如下所示（偏移是作为 GCode 偏移应用的偏移）：

```
Z-CALIBRATION: ENDSTOP=-0.300 NOZZLE=-0.300 SWITCH=6.208 PROBE=7.013 --> OFFSET=-0.170
```

限位值是归零的 Z 位置，始终为零或配置的"stepper_z:position_endstop"设置——在这种情况下，它甚至与探测的喷嘴高度相同。

# 配置

要激活扩展，需要在打印机配置中有一个 `[z_calibration]` 节。配置属性在[此处](Config_Reference.md#z_calibration)有详细描述。

## 开关偏移

"z_calibration:switch_offset"是已经提到的从开关体（探测位置）到其上方实际触发点的偏移。此值的起点可以从数据手册中获取，如 Omron 开关（D2F-5：0.5mm 和 SSG-5H：0.7mm）。最好根据你对第一层的偏好从略小的值开始（D2F-5 大约为 0.45）。因此，较小的偏移值会使喷嘴离床面更远！该值不能为负。

例如，D2F-5 的数据手册：

![endstop offset](/img/z_calibrate-d2f.png)

以及偏移基础的计算：

```
offset base = OP (Operation Position) - switch body height
     0.5 mm = 5.5 mm - 5 mm
```

## 连接和断开探针

磁探针的连接和断开可以通过为 `CALIBRATE_Z` 命令创建宏并用适当的命令包围它来完成：

```
[gcode_macro CALIBRATE_Z]
description: Automatically calibrates the nozzles offset to the print surface and dock/undock MagProbe
rename_existing: CALIBRATE_Z_BASE
gcode:
  ATTACH_PROBE     # 替换为你的特定连接宏的名称
  CALIBRATE_Z_BASE
  DETACH_PROBE     # 替换为你的特定断开宏的名称
```

也可以使用 `start_gcode` 和 `end_gcode` 属性来调用连接和断开命令：

```
[z_calibration]
...
start_gcode: ATTACH_PROBE  # 替换为你的特定连接宏的名称
end_gcode: DETACH_PROBE    # 替换为你的特定断开宏的名称
```

如果存在空间限制，并且无法在连接探针的情况下在限位开关上探测喷嘴，则可以使用 `before_switch_gcode` 属性来连接探针，而不是 `start_gcode`。然后，在探测探针在限位开关上之前不会连接探针：

```
[z_calibration]
...
before_switch_gcode: ATTACH_PROBE  # 替换为你的特定连接宏的名称
end_gcode: DETACH_PROBE            # 替换为你的特定断开宏的名称
```

## 床面网格

如果使用床面网格，在打印床上探测的坐标必须正好是网格的相对参考索引点，因为这是网格的零点！但是，可以完全省略这些属性，网格的相对参考索引点将自动获取（为此，需要"bed_mesh:relative_reference_index"设置，并且目前不支持圆形床面/网格）！

# 如何测试它

不要过多关注计算偏移的绝对值。这些可能变化很大。只有从喷嘴到床面的真实位置才重要。要测试这一点，可以首先通过 `GET_POSITION` 查询校准结果：

```
> CALIBRATE_Z
> Z-CALIBRATION: ENDSTOP=-0.300 NOZZLE=-0.267 SWITCH=2.370 PROBE=3.093 --> OFFSET=-0.010000
> GET_POSITION
> mcu: stepper_x:17085 stepper_y:15625 stepper_z:-51454 stepper_z1:-51454 stepper_z2:-51454 stepper_z3:-51454
> stepper: stepper_x:552.500000 stepper_y:-47.500000 stepper_z:10.022500 stepper_z1:10.022500 stepper_z2:10.022500 stepper_z3:10.022500
> kinematic: X:252.500000 Y:300.000000 Z:10.022500
> toolhead: X:252.500000 Y:300.000000 Z:10.021472 E:0.000000
> gcode: X:252.500000 Y:300.000000 Z:9.990000 E:0.000000
> gcode base: X:0.000000 Y:0.000000 Z:-0.010000 E:0.000000
> gcode homing: X:0.000000 Y:0.000000 Z:-0.010000
```

这里，"gcode base"中的 Z 位置反映了校准的 Z 偏移。

然后，可以通过将喷嘴缓慢向下移动到零来测试偏移，方法是分多个步骤移动。最好通过使用 GCode 来完成此操作，因为偏移是作为 GCode 偏移应用的。例如这样：

```
> G90
> G0 Z5
> G0 Z3
> G0 Z1
> G0 Z0.5
> G0 Z0.3
> G0 Z0.1
```

在每个步骤后检查到打印表面的距离。如果存在小的差异（应小于开关数据手册中的偏移基础），则通过该值调整"z_calibration:switch_offset"。减小"switch_offset"将使喷嘴离床面更远。

最后，如果你已经仔细检查了校准的偏移是正确的，你可以通过实际打印第一层测试来微调"z_calibration:switch_offset"。这只需要做一次！

# 如何使用它

## 命令 CALIBRATE_Z

使用 `CALIBRATE_Z` 命令启动校准。没有更多参数。运行此命令需要干净的喷嘴。

此校准何时被调用（以及在什么温度下）并不重要。但是，在打印机热的时候在开始打印之前调用它很重要。因此，最好将 `CALIBRATE_Z` 命令添加到 `PRINT_START` 宏中（从切片软件的起始 gCode 调用）。此宏的序列可以如下：

1. 归零所有轴
2. 加热床面和喷嘴（以及腔室）
3. 获取探针，如果需要执行任何床面调平（如 QGL、Z-Tilt），停放探针
4. 清洁和清洁喷嘴
5. 获取探针，CALIBRATE_Z，停放探针
6. （如果需要调整 Z 偏移）
7. 打印介绍行（如果使用）
8. 开始打印...

**：感叹号：并在此处删除任何旧的 Z 偏移调整（如 `SET_GCODE_OFFSET`）**

对于纹理打印表面，可能需要更接近床面。要从切片软件的起始 GCode 调整偏移，可以在调用 Z 校准**之后**将以下命令添加到 `PRINT_START` 宏中：

```
    # 如果需要，调整 G-Code Z 偏移
    SET_GCODE_OFFSET Z_ADJUST={params.Z_ADJUST|default(0.0)|float} MOVE=1
```

然后，可以在切片软件中的 `PRINT_START` 命令中添加 `Z_ADJUST=0.0`。这**不会**将偏移重置为该值，而是根据给定量进行调整！

>**注意：** 运行 Z 校准后不要再次归零 Z，否则需要再次执行！

## 命令 PROBE_Z_ACCURACY

还有一个 `PROBE_Z_ACCURACY` 命令来测试 Z 限位开关的精度（类似于探针的 `PROBE_ACCURACY` 命令）：

```
PROBE_Z_ACCURACY [PROBE_SPEED=<mm/s>] [LIFT_SPEED=<mm/s>] [SAMPLES=<count>] [SAMPLE_RETRACT_DIST=<mm>]
```

它通过获取限位开关上配置的喷嘴位置来计算多次探针采样的最大值、最小值、平均值、中位数和标准偏差。可选参数默认为 z_calibration 配置节中的等效设置。

## 渗出缓解

任何喷嘴探针限位开关的渗出都可能导致不准确，因为耗材会继续泄漏或在多次探测的空间内变形。强烈建议在此插件的喷嘴探针部分之前采取一些措施来防止渗出积累。

在打印结束时进行缓慢的长回缩（最多 15mm）可以减少渗出的可能性。如果你这样做，考虑在打印开始序列的最后一个命令中添加相当的挤出，将塑料带回尖端。（超过 5mm 的回缩与许多热端中的堵塞有关，特别是 Rapido。这可能最好作为最后的手段，具体取决于确切的硬件和耗材。）

在擦洗之前加热喷嘴约一分钟——使用清洁桶——将允许所有剩余塑料从喷嘴排出并被简单的擦拭清除。如果使用清洁和擦洗桶，请不要在此阶段挤出耗材。

需要更强激活力的限位开关（如带有弹簧的 sexbolt 或 unklicky z）可以帮助压碎任何剩余的渗出并提高一致性。

可以在低于打印完全温度的热端温度下进行探测。如果你在 250 度打印，可以将喷嘴预热到 180 度，并在完成加热到完全温度之前运行此脚本。这可能根据使用的温度产生不同的效果。

另外，考虑在喷嘴擦拭之前拿起探针，以便此脚本可以在清洁后立即探测喷嘴。
