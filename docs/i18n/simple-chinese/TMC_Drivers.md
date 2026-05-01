# TMC驱动程序

本文档提供了关于在Kalico中以SPI/UART模式使用Trinamic步进电机驱动程序的信息。

Kalico也可以在"standalone mode"中使用Trinamic驱动程序。但是，当驱动程序处于此模式时，不需要特殊的Kalico配置，并且本文档中讨论的高级Kalico功能不可用。

除了本文档外，请确保查看[TMC驱动程序配置参考](Config_Reference.md#tmc-stepper-driver-configuration)。

## 调整电机电流

更高的驱动程序电流会增加位置精度和扭矩。但是，更高的电流也会增加步进电机和步进电机驱动程序产生的热量。如果步进电机驱动程序过热，它会禁用自己，Kalico将报告错误。如果步进电机过热，它会失去扭矩和位置精度。（如果过热，它可能也会熔化附着在其上或附近的塑料部件。）

作为一般调整提示，尽可能使用较高的电流值，只要步进电机不会过热，步进电机驱动程序不会报告警告或错误。通常，步进电机感到温暖是可以的，但不应该太热以至于用手接触会感到疼痛。

## 倾向于不指定hold_current

如果配置了`hold_current`，那么当TMC驱动程序检测到步进电机未移动时，可以减少对步进电机的电流。但是，改变电机电流本身可能会引起电机移动。这可能由于步进电机内的"制动力"（转子中的永磁体向定子中的铁齿拉动）或轴滑架上的外力而发生。

大多数步进电机在正常打印期间不会从减少电流中获得显著的收益，因为很少有打印移动会让步进电机闲置足够长以激活`hold_current`功能。而且，不太可能有人想在极少数确实让步进电机闲置足够长的打印移动上引入微妙的打印伪影。

如果希望在打印启动例程期间减少电机电流，请考虑在[START_PRINT macro](Slicers.md#kalico-gcode_macro)中发出[SET_TMC_CURRENT](G-Codes.md#set_tmc_current)命令，以在正常打印移动前后调整电流。

某些打印机具有在正常打印移动期间闲置的专用Z电机（无bed_mesh、无bed_tilt、无Z skew_correction、无"vase mode"打印等），可能会发现Z电机使用`hold_current`运行更凉快。如果实现这个，那么一定要考虑到这种类型的非命令Z轴移动，在床面调平、床面探测、探针校准和类似的过程中。`driver_TPOWERDOWN`和`driver_IHOLDDELAY`也应该相应地校准。如果不确定，倾向于不指定`hold_current`。

## 设置"spreadCycle"vs"stealthChop"模式

默认情况下，Kalico将TMC驱动程序置于"spreadCycle"模式。如果驱动程序支持"stealthChop"，则可以通过在TMC配置部分添加`stealthchop_threshold: 999999`来启用它。

一般而言，spreadCycle模式提供比stealthChop模式更大的扭矩和位置精度。但是，stealthChop模式在某些打印机上可能产生明显更低的可听噪音。

比较模式的测试显示，在使用stealthChop模式时，在恒定速度移动期间"positional lag"增加约75%的全步（例如，在具有40毫米rotation_distance和200 steps_per_rotation的打印机上，恒定速度移动的位置偏差增加约0.150毫米）。但是，这种"获得请求位置的延迟"可能不会表现为显著的打印缺陷，并且可能更喜欢stealthChop模式的更安静的行为。

建议始终使用"spreadCycle"模式（通过不指定`stealthchop_threshold`）或始终使用"stealthChop"模式（通过将`stealthchop_threshold`设置为999999）。不幸的是，如果在电机以非零速度运行时改变模式，驱动程序通常会产生较差和混乱的结果。

请注意，`stealthchop_threshold`配置选项不会影响无传感器归零，因为Kalico在无传感器归零操作期间会自动将TMC驱动程序切换到适当的模式。

## TMC插值设置引入小位置偏差

TMC驱动程序`interpolate`设置可能会以牺牲引入小的系统位置误差的代价降低打印机移动的可听噪音。这个系统位置误差来自驱动程序在执行Kalico发送给它的"steps"时的延迟。在恒定速度移动期间，这个延迟导致的位置误差约为配置的微步的一半（更准确地说，误差是微步距离的一半减去512分之一的完整步距离）。例如，在具有40毫米rotation_distance、200 steps_per_rotation和16微步的轴上，在恒定速度移动期间引入的系统误差约为0.006毫米。

为了获得最佳的位置精度，建议使用spreadCycle模式并禁用插值（在TMC驱动程序配置中设置`interpolate: False`）。以这种方式配置时，可以增加`microstep`设置以减少步进电机移动期间的可听噪音。通常，`64`或`128`的微步设置将具有与插值相似的可听噪音，并且在不引入系统位置误差的情况下执行此操作。

如果使用stealthChop模式，则插值的位置不准确相对于stealthChop模式引入的位置不准确很小。因此，在stealthChop模式下调整插值不被认为是有用的，可以将插值保持在其默认状态。

## 无传感器归零

无传感器归零允许在不需要物理限位开关的情况下对轴进行归零。相反，轴上的滑架被移动到机械极限，使步进电机失步。步进驱动程序感知失步并通过切换引脚向控制MCU (Kalico)指示这一点。这些信息可以由Kalico用作轴的端点。

本指南涵盖为您的（笛卡尔）打印机X轴设置无传感器归零。但是，它对所有其他轴（需要限位开关）的工作方式相同。应逐轴配置和调整。

### 限制

确保机械部件能够处理滑架重复碰撞轴限制的负载。特别是丝杆可能产生很大的力。通过将喷嘴碰撞到打印表面来对Z轴进行归零可能不是个好主意。为了获得最佳结果，验证轴滑架将与轴限制进行牢固接触。

此外，无传感器归零对于您的打印机可能不够准确。虽然在笛卡尔机器上对X和Y轴进行归零可以很好地工作，但Z轴归零通常不够准确，可能导致不一致的第一层高度。三角洲打印机的无传感器归零不可取，因为精度不足。

此外，步进驱动程序的失速检测取决于电机上的机械负载、电机电流和电机温度（线圈电阻）。

无传感器归零在中等电机速度下工作效果最好。对于非常慢的速度（少于10 RPM），电机不会产生显著的反电动势，TMC无法可靠地检测电机失速。此外，在非常高的速度下，电机的反电动势接近电机的供电电压，因此TMC无法检测失速。建议查看特定TMC的数据表。那里您也可以找到有关此设置的限制的更多详细信息。

### 先决条件

使用无传感器归零需要满足几个先决条件：

1. 一个支持stallGuard的TMC步进驱动程序（tmc2130、tmc2209、tmc2660、tmc5160或tmc2160）。
2. 步进驱动程序的SPI / UART接口接线到微控制器（standalone mode无法工作）。
3. TMC驱动程序的适当"DIAG"或"SG_TST"引脚连接到微控制器。
4. 必须运行[配置检查](Config_checks.md)文档中的步骤以确认步进电机已配置并正常工作。

### 调整

这里描述的过程有六个主要步骤：

1. 选择归零速度。
2. 配置`printer.cfg`文件以启用无传感器归零。
3. 找到成功归零的最高灵敏度的stallguard设置。
4. 找到通过单一接触成功归零的最低灵敏度的stallguard设置。
5. 使用所需的stallguard设置更新`printer.cfg`。
6. 创建或更新`printer.cfg`宏以一致地进行归零。

#### 选择归零速度

选择归零速度是执行无传感器归零时的一个重要选择。最好使用慢速归零速度，以便在与轨道末端接触时滑架不会对框架施加过度的力。但是，TMC驱动程序无法在非常低的速度下可靠地检测失速。

归零速度的一个好的起点是步进电机每两秒进行一次完整旋转。对于许多轴，这将是`rotation_distance`除以二。例如：
```
[stepper_x]
rotation_distance: 40
homing_speed: 20
...
```

#### 为无传感器归零配置printer.cfg

确保未在配置的TMC驱动程序部分中指定`hold_current`设置。（如果设置了hold_current，则在进行接触后，电机停止，同时滑架被压在轨道的末端，减少该位置的电流可能会导致滑架移动 - 这会导致性能不佳，并将混淆调整过程。）

有必要配置无传感器归零引脚并配置初始"stallguard"设置。tmc2209示例配置为X轴可能看起来像：
```
[tmc2209 stepper_x]
diag_pin: ^PA1      # 设置为连接到TMC DIAG引脚的MCU引脚
driver_SGTHRS: 255  # 255是最敏感的值，0是最不敏感的值
home_current: 1
...

[stepper_x]
endstop_pin: tmc2209_stepper_x:virtual_endstop
homing_retract_dist: 10 # 必须大于0或设置use_sensorless_homing: True
...
```

tmc2130或tmc5160配置示例可能看起来像：
```
[tmc2130 stepper_x]
diag1_pin: ^!PA1 # 连接到TMC DIAG1引脚的引脚（或使用diag0_pin / DIAG0引脚）
driver_SGT: -64  # -64是最敏感的值，63是最不敏感的值
home_current: 1
...

[stepper_x]
endstop_pin: tmc2130_stepper_x:virtual_endstop
homing_retract_dist: 10
...
```

tmc2660配置示例可能看起来像：
```
[tmc2660 stepper_x]
driver_SGT: -64     # -64是最敏感的值，63是最不敏感的值
home_current: 1
...

[stepper_x]
endstop_pin: ^PA1   # 连接到TMC SG_TST引脚的引脚
use_sensorless_homing: True # 如果endstop_pin不是virtual_endstop，则需要
homing_retract_dist: 10
...
```

上面的示例仅显示特定于无传感器归零的设置。有关所有可用选项，请参阅[配置参考](Config_Reference.md#tmc-stepper-driver-configuration)。

#### 找到成功归零的最高灵敏度

将滑架放在轨道的中心附近。使用SET_TMC_FIELD命令设置最高灵敏度。对于tmc2209：
```
SET_TMC_FIELD STEPPER=stepper_x FIELD=SGTHRS VALUE=255
```
对于tmc2130、tmc5160、tmc2160和tmc2660：
```
SET_TMC_FIELD STEPPER=stepper_x FIELD=sgt VALUE=-64
```

然后发出`G28 X0`命令并验证轴根本不移动或快速停止移动。如果轴不停止，则发出`M112`以停止打印机 - diag/sg_tst引脚接线或配置有问题，必须在继续之前纠正。

接下来，不断降低`VALUE`设置的灵敏度，并再次运行`SET_TMC_FIELD` `G28 X0`命令，以找到导致滑架成功移动到限位停止并停止的最高灵敏度。（对于tmc2209驱动程序，这将降低SGTHRS，对于其他驱动程序，这将增加sgt。）确保在轨道中心附近开始每个尝试（如果需要，发出`M84`然后手动将滑架移动到中心）。应该可以找到最高灵敏度可靠地归零（具有更高灵敏度的设置导致小或没有移动）。注意找到的值为*maximum_sensitivity*。（如果在没有任何滑架移动的情况下获得最小可能的灵敏度（SGTHRS=0或sgt=63），则diag/sg_tst引脚接线或配置有问题，必须在继续之前纠正。）

搜索maximum_sensitivity时，可能方便跳转到不同的VALUE设置（以便等分VALUE参数）。如果这样做，请准备好发出`M112`命令停止打印机，因为具有非常低灵敏度的设置可能导致轴重复地"碰撞"进入轨道的末端。

确保在每个归零尝试之间等待几秒钟。在TMC驱动程序检测到失速后，可能需要一些时间来清除其内部指示器，并能够检测另一个失速。

在这些调整测试期间，如果`G28 X0`命令不移动到轴限制，请小心发出任何常规移动命令（例如`G1`）。Kalico将没有对滑架位置的正确理解，移动命令可能导致不期望和混乱的结果。

#### 找到通过单一接触成功归零的最低灵敏度

使用找到的*maximum_sensitivity*值进行归零时，轴应移动到轨道末端并通过"single touch"停止 - 即不应有"clicking"或"banging"声音。（如果在maximum_sensitivity处有banging或clicking声音，则homing_speed可能太低，驱动程序电流可能太低，或无传感器归零可能不是该轴的好选择。）

下一步是再次不断将滑架移动到靠近轨道中心的位置，降低灵敏度，并运行`SET_TMC_FIELD` `G28 X0`命令 - 目标现在是找到仍然导致滑架成功使用"single touch"进行归零的最低灵敏度。即，与轨道末端接触时不会"bang"或"click"。注意找到的值为*minimum_sensitivity*。

#### 使用灵敏度值更新printer.cfg

找到*maximum_sensitivity*和*minimum_sensitivity*后，使用计算器获得推荐的灵敏度为*minimum_sensitivity + (maximum_sensitivity - minimum_sensitivity)/3*。推荐的灵敏度应在最小和最大之间，但略更接近最小。将最终值舍入到最近的整数值。

对于tmc2209在配置中将其设置为`driver_SGTHRS`，对于其他TMC驱动程序在配置中将其设置为`driver_SGT`。

如果*maximum_sensitivity*和*minimum_sensitivity*之间的范围很小（例如少于5），则可能导致不稳定的归零。更快的归零速度可能会增加范围并使操作更稳定。

请注意，如果驱动程序电流、归零速度或对打印机硬件进行了显著更改，则将需要再次运行调整过程。