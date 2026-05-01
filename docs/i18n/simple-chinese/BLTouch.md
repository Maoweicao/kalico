# BL-Touch

## 连接 BL-Touch

**开始前的警告**：避免用裸露的手指触摸 BL-Touch 针脚，因为它对手指油脂非常敏感。如果接触到，请务必小心翼翼，以免弯曲或推动任何东西。

根据 BL-Touch 文档或 MCU（微控制器）文档，将 BL-Touch "伺服"连接器连接到 `control_pin`。使用原始接线，三芯线中的黄线是 `control_pin`，双芯线中的白线是 `sensor_pin`。需要根据接线配置这些针脚。大多数 BL-Touch 设备在传感器针脚上需要上拉电阻（在针脚名称前加"^"前缀）。例如：

```
[bltouch]
sensor_pin: ^P1.24
control_pin: P1.26
```

如果将 BL-Touch 用于 Z 轴归位，则设置 `endstop_pin: probe:z_virtual_endstop` 并在 `[stepper_z]` 配置部分中删除 `position_endstop`，然后添加 `[safe_z_home]` 配置部分以抬起 z 轴、归位 xy 轴、移至床面中心并归位 z 轴。例如：

```
[safe_z_home]
home_xy_position: 100, 100 # 改为打印床面中心的坐标
speed: 50
z_hop: 10                 # 向上移动 10mm
z_hop_speed: 5
```

safe_z_home 中的 z_hop 运动必须足够高，这样即使探针针脚碰巧处于其最低状态，探针也不会撞到任何东西，这一点很重要。

## 初始测试

在继续之前，验证 BL-Touch 安装在正确的高度，收缩时针脚应该大约在喷嘴上方 2mm

打开打印机电源时，BL-Touch 探针应该执行自检并上下移动针脚几次。自检完成后，针脚应该缩回，探针上的红色 LED 应该亮起。如果出现任何错误，例如探针闪烁红色或针脚在下而不是在上，请关闭打印机并检查接线和配置。

如果上述情况良好，现在是测试控制针脚是否正常工作的时候了。首先在打印机终端中运行 `BLTOUCH_DEBUG COMMAND=pin_down`。验证针脚向下移动且探针上的红色 LED 关闭。如果没有，请再次检查接线和配置。接下来发出 `BLTOUCH_DEBUG COMMAND=pin_up`，验证针脚向上移动，红色灯再次亮起。如果闪烁，则表示有问题。

下一步是确认传感器针脚工作正常。运行 `BLTOUCH_DEBUG COMMAND=pin_down`，验证针脚向下移动，运行 `BLTOUCH_DEBUG COMMAND=touch_mode`，运行 `QUERY_PROBE`，并验证命令报告"probe: open"。然后用手指指甲轻轻向上推动针脚，同时再次运行 `QUERY_PROBE`。验证命令报告"probe: TRIGGERED"。如果任一查询没有报告正确的消息，通常表示接线或配置错误（尽管某些[克隆产品](#bl-touch-克隆产品)可能需要特殊处理）。在此测试完成时，运行 `BLTOUCH_DEBUG COMMAND=pin_up` 并验证针脚向上移动。

完成 BL-Touch 控制针脚和传感器针脚测试后，现在是时候测试探针了，但有个转折。不是让探针针脚触摸打印床面，而是让它触摸手指上的指甲。将工具头放在远离床面的位置，发出 `G28`（或如果不使用 probe:z_virtual_endstop 则发出 `PROBE`），等待工具头开始向下移动，然后通过非常轻轻地用指甲触摸针脚来停止运动。可能需要做两次，因为默认归位配置探针两次。如果它在触摸针脚时不停止，请准备好关闭打印机。

如果成功，再做一次 `G28`（或 `PROBE`），但这次让它按预期触摸床面。

## BL-Touch 故障

一旦 BL-Touch 处于不一致的状态，它就会开始闪烁红色。可以通过发出以下命令强制其离开该状态：

 BLTOUCH_DEBUG COMMAND=reset

如果探针被阻止提取而导致其校准中断，就可能发生这种情况。

但是，BL-Touch 可能也无法再校准自己。当其顶部的螺钉位置错误或探针针脚内的磁芯移动时会发生这种情况。如果它移动到坚持螺钉，它可能无法再降低针脚。通过这种行为，需要打开螺钉并用圆珠笔轻轻将其推回原位。将针脚重新插入 BL-Touch，使其落入提取位置。小心调整无头螺钉到位。需要找到正确的位置，以便能够降低和提高针脚，红色灯打开和关闭。使用 `reset`、`pin_up` 和 `pin_down` 命令来实现这一点。

## BL-Touch "克隆产品"

许多 BL-Touch "克隆"设备使用默认配置可以与 Kalico 正常工作。但是，某些"克隆"设备可能不支持 `QUERY_PROBE` 命令，某些"克隆"设备可能需要配置 `pin_up_reports_not_triggered` 或 `pin_up_touch_mode_reports_triggered`。

重要！在首先按照这些说明操作之前，不要将 `pin_up_reports_not_triggered` 或 `pin_up_touch_mode_reports_triggered` 配置为 False。不要在真正的 BL-Touch 上将这两者中的任何一个配置为 False。不正确地将这些设置为 False 可能会增加探针时间并增加损坏打印机的风险。

某些"克隆"设备不支持 `touch_mode`，因此 `QUERY_PROBE` 命令不起作用。尽管如此，仍然可能使用这些设备执行探针和归位。在这些设备上，初始测试期间的 `QUERY_PROBE` 命令不会成功，但是后续的 `G28`（或 `PROBE`）测试会成功。如果不使用 `QUERY_PROBE` 命令并且不启用 `probe_with_touch_mode` 功能，则可能可以将这些"克隆"设备用于 Kalico。

某些"克隆"设备无法执行 Kalico 的内部传感器验证测试。在这些设备上，尝试归位或探针可能导致 Kalico 报告"BLTouch failed to verify sensor state"错误。如果发生这种情况，则手动运行[初始测试部分](#初始测试)中描述的步骤以确认传感器针脚是否工作。如果该测试中的 `QUERY_PROBE` 命令始终产生预期结果，并且仍然发生"BLTouch failed to verify sensor state"错误，则可能需要在 Kalico 配置文件中将 `pin_up_touch_mode_reports_triggered` 设置为 False。

很少数量的旧"克隆"设备无法报告何时成功抬起探针。在这些设备上，Kalico 将在每次归位或探针尝试后报告"BLTouch failed to raise probe"错误。可以测试这些设备——将头部远离床面，运行 `BLTOUCH_DEBUG COMMAND=pin_down`，验证针脚已向下移动，运行 `QUERY_PROBE`，验证该命令报告"probe: open"，运行 `BLTOUCH_DEBUG COMMAND=pin_up`，验证针脚已向上移动，然后运行 `QUERY_PROBE`。如果针脚保持向上，设备不进入错误状态，第一个查询报告"probe: open"而第二个查询报告"probe: TRIGGERED"，则表明应在 Kalico 配置文件中将 `pin_up_reports_not_triggered` 设置为 False。

## BL-Touch v3

某些 BL-Touch v3.0 和 BL-Touch 3.1 设备可能需要在打印机配置文件中配置 `probe_with_touch_mode`。

如果 BL-Touch v3.0 的信号线连接到限位开关针脚（带有噪声滤波电容器），则 BL-Touch v3.0 可能无法在归位和探针期间一致地发送信号。如果[初始测试部分](#初始测试)中的 `QUERY_PROBE` 命令始终产生预期结果，但工具头在 G28/PROBE 命令期间不总是停止，则表示存在这个问题。一种解决方法是在配置文件中设置 `probe_with_touch_mode: True`。

BL-Touch v3.1 在探针尝试成功后可能错误地进入错误状态。症状是 BL-Touch v3.1 上的偶发闪烁灯，在成功接触床面后持续几秒钟。Kalico 应该自动清除此错误，通常是无害的。但是，可以在配置文件中设置 `probe_with_touch_mode` 以避免此问题。

重要！某些"克隆"设备和 BL-Touch v2.0（及更早版本）在 `probe_with_touch_mode` 设置为 True 时可能会降低精度。将此设置为 True 也会增加展开探针所需的时间。如果在"克隆"或较旧的 BL-Touch 设备上配置此值，请务必在设置此值之前和之后测试探针精度（使用 `PROBE_ACCURACY` 命令进行测试）。

## 多探针无收回

默认情况下，Kalico 将在每次探针尝试的开始时展开探针，然后在之后收起探针。这种重复的探针展开和收起可能会增加涉及多次探针测量的校准序列的总时间。Kalico 支持在连续探针之间保持探针展开，这可以减少探针的总时间。通过在配置文件中将 `stow_on_each_sample` 配置为 False 可以启用此模式。

重要！将 `stow_on_each_sample` 设置为 False 会导致 Kalico 在探针展开时进行水平工具头移动。请务必在将此值设置为 False 之前验证所有探针操作具有足够的 Z 间隙。如果间隙不足，则水平移动可能导致针脚卡在障碍物上，从而损坏打印机。

重要！在使用 `stow_on_each_sample` 配置为 False 时，建议使用 `probe_with_touch_mode` 配置为 True。某些"克隆"设备如果未设置 `probe_with_touch_mode` 可能无法检测到后续床面接触。在所有设备上，使用这两个设置的组合可以简化设备信号，从而提高整体稳定性。

但是，某些"克隆"设备和 BL-Touch v2.0（及更早版本）在 `probe_with_touch_mode` 设置为 True 时可能会降低精度。在这些设备上，最好在设置 `probe_with_touch_mode` 之前和之后测试探针精度（使用 `PROBE_ACCURACY` 命令进行测试）。

## 校准 BL-Touch 偏移

按照[探针校准](Probe_Calibrate.md)指南中的说明设置 x_offset、y_offset 和 z_offset 配置参数。

最好验证 Z 偏移接近 1mm。如果不是，则可能想移动探针上下以解决此问题。希望它在喷嘴撞到床面之前触发，这样粘住的丝材或翘曲的床面不会影响任何探针操作。但同时，希望收缩位置尽可能远离喷嘴上方以避免接触打印部件。如果对探针位置进行了调整，则重新运行探针校准步骤。

## BL-Touch 输出模式

* BL-Touch V3.0 支持设置 5V 或 OPEN-DRAIN 输出模式，BL-Touch V3.1 也支持，但也可以将其存储在其内部 EEPROM 中。如果控制板需要 5V 模式的固定 5V 高逻辑电平，可以将打印机配置文件的 [bltouch] 部分中的 'set_output_mode' 参数设置为"5V"。

  *** 仅当控制板的输入线 5V 容限时才使用 5V 模式。这就是为什么这些 BL-Touch 版本的默认配置是 OPEN-DRAIN 模式。您可能会损坏控制板的 CPU ***

  所以因此：
  如果控制板需要 5V 模式，它的输入信号线上 5V 容限，并且

  - 拥有 BL-Touch Smart V3.0，需要使用 'set_output_mode: 5V' 参数以在每次启动时确保此设置，因为探针无法记住所需的设置。
  - 拥有 BL-Touch Smart V3.1，可以选择使用 'set_output_mode: 5V' 或通过手动使用 'BLTOUCH_STORE MODE=5V' 命令存储一次模式，并且不使用参数 'set_output_mode:'。
  - 拥有其他一些探针：某些探针在电路板上有要切割的迹线或要设置的跳线，以便（永久）设置输出模式。在这种情况下，完全省略 'set_output_mode' 参数。

  如果拥有 V3.1，不要自动化或重复存储输出模式以避免磨损探针的 EEPROM。BLTouch EEPROM 适用于约 100,000 次更新。每天 100 次存储将增加到大约 3 年的操作时间，然后才能磨损。因此，在 V3.1 中存储输出模式由供应商设计为复杂操作（工厂默认为安全的 OPEN DRAIN 模式），不适合被切片器、宏或其他任何东西重复发出，最好仅在首次将探针集成到打印机电子设备时使用。