# BL-Touch

## 连接 BL-Touch

开始前的**警告**：避免用裸手指触摸 BL-Touch 针，因为它对指纹油脂非常敏感。如果你确实触摸了，请非常轻柔，以避免弯曲或推动任何东西。

按照 BL-Touch 文档或 MCU 文档将 BL-Touch"伺服"连接器连接到 `control_pin`。使用原始布线，三线组中的黄色线是 `control_pin`，双线组中的白色线是 `sensor_pin`。你需要根据布线配置这些引脚。大多数 BL-Touch 设备需要在传感器引脚上接上拉电阻（在引脚名称前加"^"）。例如：

```
[bltouch]
sensor_pin: ^P1.24
control_pin: P1.26
```

如果 BL-Touch 将用于归零 Z 轴，则将 `endstop_pin: probe:z_virtual_endstop` 设置在 `[stepper_z]` 配置节中，并移除 `position_endstop`，然后添加 `[safe_z_home]` 配置节以抬升 Z 轴、归零 XY 轴、移动到床面中心并归零 Z 轴。例如：

```
[safe_z_home]
home_xy_position: 100, 100 # 将坐标更改为打印床中心
speed: 50
z_hop: 10                 # 向上移动 10mm
z_hop_speed: 5
```

重要的是 safe_z_home 中的 z_hop 移动要足够高，即使探针针恰好处于最低状态，探针也不会碰到任何东西。

## 初始测试

在继续之前，验证 BL-Touch 安装在正确的高度，针在缩回时应大致高于喷嘴 2 mm。

打开打印机时，BL-Touch 探针应执行自测试并上下移动针几次。自测试完成后，针应缩回，探针上的红色 LED 应亮起。如果有任何错误，例如探针闪烁红色或针向下而不是向上，请关闭打印机并检查布线和配置。

如果上述情况良好，是时候测试控制针是否正常工作了。首先在打印机终端中运行 `BLTOUCH_DEBUG COMMAND=pin_down`。验证针向下移动并且探针上的红色 LED 熄灭。如果没有，请再次检查布线和配置。接下来发出 `BLTOUCH_DEBUG COMMAND=pin_up`，验证针向上移动，并且红灯再次亮起。如果它在闪烁，则存在问题。

下一步是确认传感器针正常工作。运行 `BLTOUCH_DEBUG COMMAND=pin_down`，验证针向下移动，运行 `BLTOUCH_DEBUG COMMAND=touch_mode`，运行 `QUERY_PROBE`，并验证该命令报告"probe: open"。然后用指甲轻轻向上推针时再次运行 `QUERY_PROBE`。验证该命令报告"probe: TRIGGERED"。如果任一查询未报告正确的消息，通常表示接线或配置不正确（尽管某些[克隆](#bl-touch-clones)可能需要特殊处理）。完成此测试后运行 `BLTOUCH_DEBUG COMMAND=pin_up` 并验证针向上移动。

完成 BL-Touch 控制针和传感器针测试后，现在是时候测试探测了，但有一个转折。不是让探针针接触打印床，而是让它接触你手指上的指甲。将工具头定位到远离床面的位置，发出 `G28`（如果不使用 probe:z_virtual_endstop，则使用 `PROBE`），等到工具头开始向下移动，然后通过用指甲非常轻柔地触摸针来停止移动。你可能需要做两次，因为默认归零配置会探测两次。准备好在触摸针时关闭打印机。

如果成功，请再做一次 `G28`（或 `PROBE`），但这次让它按应有的方式接触床面。

## BL-Touch 变坏

一旦 BL-Touch 处于不一致状态，它会开始闪烁红色。你可以通过发出以下命令强制其离开该状态：

 BLTOUCH_DEBUG COMMAND=reset

如果探针被阻挡无法弹出，中断了其校准，可能会发生这种情况。

但是，BL-Touch 可能也无法再自我校准。如果其顶部的螺丝位置不正确或探针针内的磁芯移动，就会发生这种情况。如果它向上移动并粘在螺丝上，它可能无法再降低其针。对于这种行为，你需要打开螺丝并使用圆珠笔将其轻轻推回原位。将针重新插入 BL-Touch，使其落入弹出位置。仔细将无头螺丝重新调整到位。你需要找到正确的位置，使其能够降低和升起针，并且红灯亮起和熄灭。使用 `reset`、`pin_up` 和 `pin_down` 命令来实现此目的。

## BL-Touch"克隆"

许多 BL-Touch"克隆"设备使用默认配置与 Kalico 正常工作。但是，某些"克隆"设备可能不支持 `QUERY_PROBE` 命令，某些"克隆"设备可能需要配置 `pin_up_reports_not_triggered` 或 `pin_up_touch_mode_reports_triggered`。

重要！不要在遵循这些说明之前将 `pin_up_reports_not_triggered` 或 `pin_up_touch_mode_reports_triggered` 配置为 False。不要在真正的 BL-Touch 上将其中任何一个配置为 False。错误地将这些设置为 False 可能会增加探测时间并增加损坏打印机的风险。

某些"克隆"设备不支持 `touch_mode`，因此 `QUERY_PROBE` 命令不起作用。尽管如此，仍然可以使用这些设备进行探测和归零。在这些设备上，[初始测试](#initial-tests)期间的 `QUERY_PROBE` 命令将不会成功，但是后续的 `G28`（或 `PROBE`）测试确实成功。如果不使用 `QUERY_PROBE` 命令且不启用 `probe_with_touch_mode` 功能，可能可以将这些"克隆"设备与 Kalico 一起使用。

某些"克隆"设备无法执行 Kalico 的内部传感器验证测试。在这些设备上，尝试归零或探测可能导致 Kalico 报告"BLTouch failed to verify sensor state"错误。如果发生这种情况，请手动运行[初始测试部分](#initial-tests)中描述的步骤来确认传感器针正常工作。如果该测试中的 `QUERY_PROBE` 命令始终产生预期结果，但仍然出现"BLTouch failed to verify sensor state"错误，则可能需要在 Kalico 配置文件中将 `pin_up_touch_mode_reports_triggered` 设置为 False。

极少数旧的"克隆"设备无法报告它们已成功升起探针。在这些设备上，Kalico 将在每次归零或探测尝试后报告"BLTouch failed to raise probe"错误。可以测试这些设备——将头远离床面，运行 `BLTOUCH_DEBUG COMMAND=pin_down`，验证针已向下移动，运行 `QUERY_PROBE`，验证该命令报告"probe: open"，运行 `BLTOUCH_DEBUG COMMAND=pin_up`，验证针已向上移动，并运行 `QUERY_PROBE`。如果针保持向上，设备未进入错误状态，并且第一个查询报告"probe: open"而第二个查询报告"probe: TRIGGERED"，则表示应在 Kalico 配置文件中将 `pin_up_reports_not_triggered` 设置为 False。

## BL-Touch v3

某些 BL-Touch v3.0 和 BL-Touch 3.1 设备可能需要在打印机配置文件中配置 `probe_with_touch_mode`。

如果 BL-Touch v3.0 的信号线连接到限位引脚（带有噪声滤波电容），则 BL-Touch v3.0 可能无法在归零和探测期间持续发送信号。如果[初始测试部分](#initial-tests)中的 `QUERY_PROBE` 命令始终产生预期结果，但工具头在 G28/PROBE 命令期间并不总是停止，则表明存在此问题。解决方法是在配置文件中设置 `probe_with_touch_mode: True`。

BL-Touch v3.1 可能在成功的探测尝试后错误地进入错误状态。症状是 BL-Touch v3.1 上偶尔闪烁灯光，在成功接触床面后持续几秒钟。Kalico 应自动清除此错误，通常是无害的。但是，可以在配置文件中设置 `probe_with_touch_mode` 以避免此问题。

重要！某些"克隆"设备和 BL-Touch v2.0（及更早版本）在 `probe_with_touch_mode` 设置为 True 时可能精度降低。将此设置为 True 还会增加部署探针所需的时间。如果在"克隆"或旧版 BL-Touch 设备上配置此值，请务必在设置此值前后测试探针精度（使用 `PROBE_ACCURACY` 命令进行测试）。

## 无收回的多次探测

默认情况下，Kalico 会在每次探测尝试开始时部署探针，然后在之后收回探针。探针的这种重复部署和收回可能会增加涉及许多探测测量的校准序列的总时间。Kalico 支持在连续探测之间保持探针部署，这可以减少探测的总时间。通过在配置文件中将 `stow_on_each_sample` 配置为 False 来启用此模式。

重要！将 `stow_on_each_sample` 设置为 False 可能导致 Kalico 在探针部署时进行水平工具头移动。在将此值设置为 False 之前，请务必验证所有探测操作具有足够的 Z 间隙。如果间隙不足，水平移动可能导致针被障碍物卡住并导致打印机损坏。

重要！建议在使用 `stow_on_each_sample` 配置为 False 时使用 `probe_with_touch_mode` 配置为 True。如果未设置 `probe_with_touch_mode`，某些"克隆"设备可能无法检测到后续的床面接触。在所有设备上，使用这两个设置的组合简化了设备信号，可以提高整体稳定性。

但是请注意，某些"克隆"设备和 BL-Touch v2.0（及更早版本）在 `probe_with_touch_mode` 设置为 True 时可能精度降低。在这些设备上，在设置 `probe_with_touch_mode` 前后测试探针精度是个好主意（使用 `PROBE_ACCURACY` 命令进行测试）。

## 校准 BL-Touch 偏移

按照[探针校准](Probe_Calibrate.md)指南中的说明设置 x_offset、y_offset 和 z_offset 配置参数。

验证 Z 偏移接近 1mm 是个好主意。如果不是，你可能需要向上或向下移动探针来修复它。你希望它在喷嘴碰到床面之前就触发，这样可能卡住的耗材或翘曲的床面不会影响任何探测操作。但同时，你希望缩回位置尽可能远离喷嘴，以避免接触打印部件。如果对探针位置进行了调整，请重新运行探针校准步骤。

## BL-Touch 输出模式

* BL-Touch V3.0 支持设置 5V 或 OPEN-DRAIN 输出模式，BL-Touch V3.1 也支持此功能，但也可以将其存储在其内部 EEPROM 中。如果你的控制器板需要 5V 模式的固定 5V 高逻辑电平，你可以在打印机配置文件的 [bltouch] 节中将 'set_output_mode' 参数设置为"5V"。

  *** 仅当你的控制器板输入线路为 5V 耐压时才使用 5V 模式。这就是这些 BL-Touch 版本的默认配置为 OPEN-DRAIN 模式的原因。你可能会损坏控制器板的 CPU ***

  因此：
  如果控制器板需要 5V 模式，并且其输入信号线路为 5V 耐压，并且如果

  - 你有 BL-Touch Smart V3.0，你需要使用 'set_output_mode: 5V' 参数来确保每次启动时的此设置，因为探针无法记住所需的设置。
  - 你有 BL-Touch Smart V3.1，你可以选择使用 'set_output_mode: 5V' 或通过使用 'BLTOUCH_STORE MODE=5V' 命令手动存储一次模式，而不使用 'set_output_mode:' 参数。
  - 你有其他探针：某些探针在电路板上有走线可以剪断或跳线可以设置，以（永久）设置输出模式。在这种情况下，完全省略 'set_output_mode' 参数。

  如果你有 V3.1，请不要自动化或重复存储输出模式，以避免磨损探针的 EEPROM。BLTouch EEPROM 可支持约 100,000 次更新。每天 100 次存储大约需要 3 年的操作才会磨损。因此，将输出模式存储在 V3.1 中是供应商设计的复杂操作（工厂默认为安全的 OPEN DRAIN 模式），不适合由切片软件、宏或其他任何东西重复发出，最好仅在首次将探针集成到打印机电子设备中时使用。
