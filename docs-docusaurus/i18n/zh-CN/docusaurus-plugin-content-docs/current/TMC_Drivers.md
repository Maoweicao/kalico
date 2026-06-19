# TMC 驱动器

本文档提供了有关在 Kalico 上使用 SPI/UART 模式下的 Trinamic 步进电机驱动器的信息。

Kalico 还可以在"独立模式"下使用 Trinamic 驱动器。但是，当驱动器处于此模式时，不需要特殊的 Kalico 配置，本文档讨论的高级 Kalico 功能不可用。

除了本文档外，请务必查看 [TMC 驱动器配置参考](Config_Reference.md#tmc-stepper-driver-configuration)。

## 调节电机电流

更高的驱动器电流会提高位置精度和扭矩。但是，更高的电流也会增加步进电机和步进电机驱动器产生的热量。如果步进电机驱动器过热，它将禁用自身，Kalico 将报告错误。如果步进电机过热，它会失去扭矩和位置精度。（如果变得非常热，它还可能熔化连接在其上或附近的塑料部件。）

作为一般的调节提示，只要步进电机不会变得太热且步进电机驱动器不会报告警告或错误，就更倾向于使用较高的电流值。通常，步进电机感觉温热是可以的，但不应该变得烫到无法触摸。

## 建议不指定 hold_current

如果配置了 `hold_current`，则当 TMC 驱动器检测到步进电机未移动时，可以降低步进电机的电流。但是，改变电机电流本身可能会引入电机运动。这可能是由于步进电机内的"齿槽力"（转子中的永磁体向定子中的铁齿拉近）或轴滑架上的外力造成的。

大多数步进电机在正常打印期间不会因降低电流而获得显著的好处，因为很少有打印移动会使步进电机闲置足够长的时间以激活 `hold_current` 功能。而且，不太可能希望在少数使步进电机闲置足够长的打印移动中引入细微的打印瑕疵。

如果希望在打印例程开始时降低电机电流，请考虑在 [START_PRINT 宏](Slicers.md#kalico-gcode_macro) 中发出 [SET_TMC_CURRENT](G-Codes.md#set_tmc_current) 命令，以在正常打印移动之前和之后调整电流。

一些在正常打印移动期间有专用 Z 电机的打印机（无 bed_mesh、无 bed_tilt、无 Z skew_correction、无"花瓶模式"打印等）可能会发现 Z 电机确实使用 `hold_current` 运行时温度更低。如果实现此功能，请务必考虑在调平、探测、探针校准等过程中此类非预期的 Z 轴移动。`driver_TPOWERDOWN` 和 `driver_IHOLDDELAY` 也应相应校准。如果不确定，建议不指定 `hold_current`。

## 设置 "spreadCycle" 与 "stealthChop" 模式

默认情况下，Kalico 将 TMC 驱动器置于 "spreadCycle" 模式。如果驱动器支持 "stealthChop"，则可以通过在 TMC 配置部分添加 `stealthchop_threshold: 999999` 来启用它。

通常，spreadCycle 模式比 stealthChop 模式提供更大的扭矩和更高的位置精度。但是，stealthChop 模式在某些打印机上可能会显著降低可听噪声。

比较模式的测试表明，在恒定速度移动期间使用 stealthChop 模式时，"位置滞后"增加了约 75% 的全步（例如，在具有 40mm rotation_distance 和 200 steps_per_rotation 的打印机上，恒速移动的位置偏差增加了约 0.150mm）。但是，这种"获取请求位置的延迟"可能不会表现为明显的打印缺陷，人们可能更喜欢 stealthChop 模式的安静行为。

建议始终使用 "spreadCycle" 模式（不指定 `stealthchop_threshold`）或始终使用 "stealthChop" 模式（将 `stealthchop_threshold` 设置为 999999）。不幸的是，如果在电机处于非零速度时改变模式，驱动器通常会产生糟糕且令人困惑的结果。

请注意，`stealthchop_threshold` 配置选项不会影响无感归位，因为 Klipper 在无感归位操作期间会自动将 TMC 驱动器切换到适当的模式。

## TMC 插值设置引入微小位置偏差

TMC 驱动器 `interpolate` 设置可能会降低打印机移动的可听噪声，代价是引入微小的系统位置误差。这种系统位置误差源于驱动器执行 Kalico 发送的"步进"的延迟。在恒定速度移动期间，此延迟会导致几乎半个已配置微步的位置误差（更准确地说，误差是半个微步距离减去全步距离的 512 分之一）。例如，在具有 40mm rotation_distance、200 steps_per_rotation 和 16 微步的轴上，恒速移动期间引入的系统误差约为 0.006mm。

为了获得最佳位置精度，考虑使用 spreadCycle 模式并禁用插值（在 TMC 驱动器配置中设置 `interpolate: False`）。以此方式配置时，可以增加 `microstep` 设置以降低步进电机移动期间的可听噪声。通常，`64` 或 `128` 的微步设置将具有与插值相似的可听噪声，并且不会引入系统位置误差。

如果使用 stealthChop 模式，则插值引入的位置不准确性相对于 stealthChop 模式引入的位置不准确性较小。因此，在 stealthChop 模式下调节插值不被认为是有用的，可以保持插值的默认状态。

## 无感归位

无感归位允许在不需要物理限位开关的情况下对轴进行归位。相反，轴上的滑架被移动到机械极限，使步进电机丢步。步进驱动器感应到丢步并通过切换引脚向控制 MCU（Kalico）指示。Kalico 可以将此信息用作轴的限位开关。

本指南介绍如何为（笛卡尔）打印机的 X 轴设置无感归位。但是，它适用于所有其他需要限位开关的轴。您应该一次配置和调节一个轴。

### 限制

请确保您的机械部件能够承受滑架反复撞击轴极限的负载。特别是丝杠可能会产生很大的力。通过将喷嘴撞入打印表面来归位 Z 轴可能不是个好主意。为了获得最佳结果，请验证轴滑架将与轴极限进行牢固接触。

此外，无感归位可能不够精确，无法满足您的打印机。虽然在笛卡尔机器上对 X 和 Y 轴归位可能效果良好，但归位 Z 轴通常不够精确，可能导致第一层高度不一致。由于缺乏精度，不建议对 delta 打印机进行无感归位。

此外，步进驱动器的失速检测取决于电机的机械负载、电机电流和电机温度（线圈电阻）。

无感归位在中等电机速度下效果最佳。对于非常慢的速度（小于 10 RPM），电机不会产生显著的反电动势，TMC 无法可靠地检测电机失速。此外，在非常高的速度下，电机的反电动势接近电机的电源电压，因此 TMC 无法再检测到失速。建议查看特定 TMC 的数据手册。在那里您还可以找到有关此设置限制的更多详细信息。

### 先决条件

使用无感归位需要一些先决条件：

1. 支持 stallGuard 的 TMC 步进驱动器（tmc2130、tmc2209、tmc2660、tmc5160 或 tmc2160）。
2. TMC 驱动器的 SPI/UART 接口连接到微控制器（独立模式不适用）。
3. TMC 驱动器的适当 "DIAG" 或 "SG_TST" 引脚连接到微控制器。
4. 必须运行 [config checks](Config_checks.md) 文档中的步骤，以确认步进电机已正确配置和工作。

### 调节

此处描述的过程有六个主要步骤：

1. 选择归位速度。
2. 配置 `printer.cfg` 文件以启用无感归位。
3. 找到能成功归位的最高灵敏度 stallguard 设置。
4. 找到能单次接触成功归位的最低灵敏度 stallguard 设置。
5. 使用所需的 stallguard 设置更新 `printer.cfg`。
6. 创建或更新 `printer.cfg` 宏以一致地归位。

#### 选择归位速度

执行无感归位时，归位速度是一个重要的选择。最好使用较慢的归位速度，这样滑架在接触导轨末端时不会对框架施加过大的力。但是，TMC 驱动器在非常慢的速度下无法可靠地检测到失速。

归位速度的一个好的起点是步进电机每两秒进行一次完整旋转。对于许多轴，这将是 `rotation_distance` 除以二。例如：
```
[stepper_x]
rotation_distance: 40
homing_speed: 20
...
```

#### 为无感归位配置 printer.cfg

确保在配置的 TMC 驱动器部分中未指定 `hold_current` 设置。（如果设置了 hold_current，则在接触后，电机在滑架压在导轨末端时停止，在该位置减少电流可能会导致滑架移动 - 这会导致性能不佳并使调节过程混乱。）

需要配置无感归位引脚并配置初始 "stallguard" 设置。X 轴的 tmc2209 示例配置可能如下所示：
```
[tmc2209 stepper_x]
diag_pin: ^PA1      # 设置为连接到 TMC DIAG 引脚的 MCU 引脚
driver_SGTHRS: 255  # 255 是最灵敏的值，0 是最不灵敏的
home_current: 1
...

[stepper_x]
endstop_pin: tmc2209_stepper_x:virtual_endstop
homing_retract_dist: 10 # 必须大于 0 或设置 use_sensorless_homing: True
...
```

tmc2130 或 tmc5160 的配置示例可能如下所示：
```
[tmc2130 stepper_x]
diag1_pin: ^!PA1 # 连接到 TMC DIAG1 引脚的引脚（或使用 diag0_pin / DIAG0 引脚）
driver_SGT: -64  # -64 是最灵敏的值，63 是最不灵敏的
home_current: 1
...

[stepper_x]
endstop_pin: tmc2130_stepper_x:virtual_endstop
homing_retract_dist: 10
...
```

tmc2660 的配置示例可能如下所示：
```
[tmc2660 stepper_x]
driver_SGT: -64     # -64 是最灵敏的值，63 是最不灵敏的
home_current: 1
...

[stepper_x]
endstop_pin: ^PA1   # 连接到 TMC SG_TST 引脚的引脚
use_sensorless_homing: True # 如果 endstop_pin 不是 virtual_endstop 则需要
homing_retract_dist: 10
...
```

以上示例仅显示了特定于无感归位的设置。有关所有可用选项，请参阅 [配置参考](Config_Reference.md#tmc-stepper-driver-configuration)。

#### 找到能成功归位的最高灵敏度

将滑架放在导轨中心附近。使用 SET_TMC_FIELD 命令设置最高灵敏度。对于 tmc2209：
```
SET_TMC_FIELD STEPPER=stepper_x FIELD=SGTHRS VALUE=255
```
对于 tmc2130、tmc5160、tmc2160 和 tmc2660：
```
SET_TMC_FIELD STEPPER=stepper_x FIELD=sgt VALUE=-64
```

然后发出 `G28 X0` 命令并验证轴是否完全不移动或快速停止移动。如果轴未停止，则发出 `M112` 以停止打印机 - diag/sg_tst 引脚接线或配置有问题，必须在继续之前进行更正。

接下来，持续降低 `VALUE` 设置的灵敏度并再次运行 `SET_TMC_FIELD` `G28 X0` 命令，以找到能成功使滑架完全移动到限位开关并停止的最高灵敏度。（对于 tmc2209 驱动器，这将是降低 SGTHRS，对于其他驱动器，这将是增加 sgt。）确保每次尝试都将滑架放在导轨中心附近（如果需要，发出 `M84` 然后手动将滑架移动到中心）。应该能够找到能可靠归位的最高灵敏度（较高灵敏度的设置会导致较小或没有运动）。记下找到的值为 *maximum_sensitivity*。（如果在没有任何滑架运动的情况下获得最小可能灵敏度（SGTHRS=0 或 sgt=63），则 diag/sg_tst 引脚接线或配置有问题，必须在继续之前进行更正。）

在搜索 maximum_sensitivity 时，跳转到不同的 VALUE 设置可能很方便（以便对 VALUE 参数进行二分查找）。如果这样做，请准备好发出 `M112` 命令以停止打印机，因为非常低的灵敏度设置可能导致轴反复"撞击"导轨末端。

确保在每次归位尝试之间等待几秒钟。在 TMC 驱动器检测到失速后，可能需要一点时间来清除其内部指示器并能够再次检测到失速。

在这些调节测试期间，如果 `G28 X0` 命令未完全移动到轴极限，则在发出任何常规移动命令（例如 `G1`）时要小心。Kalico 将无法正确理解滑架位置，移动命令可能导致不理想且令人困惑的结果。

#### 找到能单次接触归位的最低灵敏度

使用找到的 *maximum_sensitivity* 值归位时，轴应移动到导轨末端并以"单次接触"停止 - 即，不应该有"咔嗒"声或"撞击"声。（如果在 maximum_sensitivity 时有撞击声或咔嗒声，则归位速度可能太低，驱动器电流可能太低，或者无感归位可能不是该轴的好选择。）

下一步是再次持续将滑架移动到导轨中心附近的位置，降低灵敏度，并运行 `SET_TMC_FIELD` `G28 X0` 命令 - 现在的目标是找到仍能使滑架以"单次接触"成功归位的最低灵敏度。即，在接触导轨末端时不会"撞击"或"咔嗒"。记下找到的值为 *minimum_sensitivity*。

#### 使用灵敏度值更新 printer.cfg

找到 *maximum_sensitivity* 和 *minimum_sensitivity* 后，使用计算器获得推荐灵敏度为 *minimum_sensitivity + (maximum_sensitivity - minimum_sensitivity)/3*。推荐灵敏度应在最小值和最大值之间，但略接近最小值。将最终值四舍五入到最近的整数值。

对于 tmc2209，在配置中将其设置为 `driver_SGTHRS`，对于其他 TMC 驱动器，在配置中将其设置为 `driver_SGT`。

如果 *maximum_sensitivity* 和 *minimum_sensitivity* 之间的范围很小（例如，小于 5），则可能导致归位不稳定。更快的归位速度可能会增加范围并使操作更稳定。

请注意，如果对驱动器电流、归位速度进行了任何更改，或对打印机硬件进行了显著更改，则需要再次运行调节过程。

#### 使用宏进行归位

与 Klipper 不同，在 Kalico 中，您不需要宏来管理无感归位。归位电流由 TMC 块处理，归位回退距离用于定义最小归位距离（也可以手动配置），用于无感归位验证以及归位后回退。无感设置的深入指南即将推出。

### CoreXY 无感归位提示

可以在 CoreXY 打印机的 X 和 Y 滑架上使用无感归位。Kalico 在归位 X 滑架时使用 `[stepper_x]` 步进电机检测失速，在归位 Y 滑架时使用 `[stepper_y]` 步进电机检测失速。

使用上述调节指南为每个滑架找到合适的"失速灵敏度"，但请注意以下限制：
1. 在 CoreXY 上使用无感归位时，确保两个步进电机都没有配置 `hold_current`。
2. 调节时，确保 X 和 Y 滑架在每次归位尝试之前都靠近其导轨中心。
3. 调节完成后，当同时归位 X 和 Y 时，使用宏确保首先归位一个轴，然后将该滑架移离轴极限，暂停至少 2 秒，然后开始归位另一个滑架。移离轴极限可避免在另一个滑架压在轴极限时归位一个轴（这可能会使失速检测产生偏差）。暂停是必要的，以确保在再次归位之前驱动器的失速标志已清除。

CoreXY 归位宏的示例可能如下所示：
```
[gcode_macro HOME]
gcode:
    G90
    # 归位 Z
    G28 Z0
    G1 Z10 F1200
    # 归位 Y
    G28 Y0
    G1 Y5 F1200
    # 归位 X
    G4 P2000
    G28 X0
    G1 X5 F1200
```

## 查询和诊断驱动器设置

`[DUMP_TMC 命令](G-Codes.md#dump_tmc)` 是配置和诊断驱动器时的有用工具。它将报告 Kalico 配置的所有字段以及可以从驱动器查询的所有字段。

所有报告的字段都在每个驱动器的 Trinamic 数据手册中定义。可以在 [Trinamic 网站](https://www.trinamic.com/) 上找到这些数据手册。获取并查看驱动器的 Trinamic 数据手册以解释 DUMP_TMC 的结果。

## 配置 driver_XXX 设置

Kalico 支持使用 `driver_XXX` 设置配置许多底层驱动器字段。[TMC 驱动器配置参考](Config_Reference.md#tmc-stepper-driver-configuration) 有每种驱动器类型的可用字段完整列表。

此外，几乎所有字段都可以在运行时使用 [SET_TMC_FIELD 命令](G-Codes.md#set_tmc_field) 进行修改。

每个字段都在每个驱动器的 Trinamic 数据手册中定义。可以在 [Trinamic 网站](https://www.trinamic.com/) 上找到这些数据手册。

请注意，Trinamic 数据手册有时使用的措辞可能会将高级设置（如 "hysteresis end"）与底层字段值（如 "HEND"）混淆。在 Kalico 中，`driver_XXX` 和 SET_TMC_FIELD 始终设置实际写入驱动器的底层字段值。因此，例如，如果 Trinamic 数据手册声明必须将值 3 写入 HEND 字段以获得 "hysteresis end" 为 0，则设置 `driver_HEND=3` 以获得高级值 0。

## 常见问题

### 我可以在具有压力推进的挤出机上使用 stealthChop 模式吗？

许多人成功地在 Kalico 的压力推进中使用 "stealthChop" 模式。Kalico 实现了 [平滑压力推进](Kinematics.md#pressure-advance)，不会引入任何瞬时速度变化。

但是，"stealthChop" 模式可能会产生较低的电机扭矩和/或产生更高的电机热量。对于您的特定打印机，它可能是也可能不是足够的模式。

### 我不断收到 "Unable to read tmc uart 'stepper_x' register IFCNT" 错误？

当 Kalico 无法与 tmc2208 或 tmc2209 驱动器通信时，会发生此错误。

确保电机电源已启用，因为步进电机驱动器通常需要电机电源才能与微控制器通信。

如果此错误在首次刷写 Kalico 后发生，则步进驱动器可能以前被编程为与 Kalico 不兼容的状态。要重置状态，请从打印机上断开所有电源几秒钟（物理拔掉 USB 和电源插头）。

否则，此错误通常是 UART 引脚接线不正确或 Kalico UART 引脚设置配置不正确的结果。

### 我不断收到 "Unable to write tmc spi 'stepper_x' register ..." 错误？

当 Kalico 无法与 tmc2130、tmc5160 或 tmc2160 驱动器通信时，会发生此错误。

确保电机电源已启用，因为步进电机驱动器通常需要电机电源才能与微控制器通信。

否则，此错误通常是 SPI 接线不正确、Kalico SPI 设置配置不正确或 SPI 总线上的设备配置不完整的结果。

请注意，如果驱动器与多个设备在共享 SPI 总线上，请确保在 Kalico 中完全配置该共享 SPI 总线上的每个设备。如果共享 SPI 总线上的设备未配置，它可能会错误地响应不是针对它的命令，并损坏与目标设备的通信。如果共享 SPI 总线上有无法在 Kalico 中配置的设备，请使用 [static_digital_output 配置部分](Config_Reference.md#static_digital_output) 将未使用设备的 CS 引脚设置为高电平（以便它不会尝试使用 SPI 总线）。电路板的原理图通常是查找哪些设备在 SPI 总线上及其关联引脚的有用参考。

### 为什么我收到 "TMC reports error: ..." 错误？

此类错误表示 TMC 驱动器检测到问题并已禁用自身。即，驱动器停止保持其位置并忽略移动命令。如果 Kalico 检测到活动驱动器已禁用自身，它将使打印机进入"关闭"状态。

由于 SPI 错误阻止与驱动器通信（在 tmc2130、tmc5160、tmc2160 或 tmc2660 上），也可能发生 **TMC reports error** 关闭。如果发生这种情况，报告的驱动器状态通常显示 `00000000` 或 `ffffffff` - 例如：`TMC reports error: DRV_STATUS: ffffffff ...` 或 `TMC reports error: READRSP@RDSEL2: 00000000 ...`。此类故障可能是由于 SPI 接线问题或 TMC 驱动器的自复位或故障。

一些常见错误及其诊断提示：

#### TMC reports error: `... ot=1(OvertempError!)`

这表示电机驱动器因过热而禁用自身。典型的解决方案是降低步进电机电流，增加步进电机驱动器的冷却，和/或增加步进电机的冷却。

#### TMC reports error: `... ShortToGND` OR `ShortToSupply`

这表示驱动器因检测到通过驱动器的非常高的电流而禁用自身。这可能表示到步进电机的电线松动或短路，或步进电机内部短路。

如果使用 stealthChop 模式且 TMC 驱动器无法准确预测电机的机械负载，也可能发生此错误。（如果驱动器做出不好的预测，它可能会通过电机发送过多电流并触发自身的过流检测。）要测试此问题，请禁用 stealthChop 模式并检查错误是否继续发生。

#### TMC reports error: `... reset=1(Reset)` OR `CS_ACTUAL=0(Reset?)` OR `SE=0(Reset?)`

这表示驱动器在打印过程中重置了自身。这可能是由于电压或接线问题。

#### TMC reports error: `... uv_cp=1(Undervoltage!)`

这表示驱动器检测到低电压事件并已禁用自身。这可能是由于接线或电源问题。

### 如何调节驱动器上的 spreadCycle/coolStep 等模式？

[Trinamic 网站](https://www.trinamic.com/) 有关于配置驱动器的指南。这些指南通常是技术性的、底层的，可能需要专门的硬件。无论如何，它们是最佳信息来源。
