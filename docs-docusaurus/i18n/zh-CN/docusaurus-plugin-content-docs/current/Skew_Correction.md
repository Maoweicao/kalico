# 偏斜校正

基于软件的偏斜校正可以帮助解决由于打印机装配不完全方正而导致的尺寸不准确问题。请注意，如果你的打印机有明显的偏斜，强烈建议在应用软件校正之前，先使用机械方法使打印机尽可能方正。

## 打印校准对象

校正偏斜的第一步是沿你要校正的平面打印一个[校准对象](https://www.thingiverse.com/thing:2563185/files)。还有一个包含所有平面的[校准对象](https://www.thingiverse.com/thing:2972743)。你需要将对象定向，使角 A 朝向平面的原点。

确保在此打印期间不应用偏斜校正。你可以通过从 printer.cfg 中移除 `[skew_correction]` 模块或发出 `SET_SKEW CLEAR=1` gcode 来实现。

## 进行测量

`[skew_correction]` 模块需要为你要校正的每个平面进行 3 次测量：角 A 到角 C 的长度、角 B 到角 D 的长度，以及角 A 到角 D 的长度。测量长度 AD 时，请勿包含某些测试对象提供的角部平坦部分。

![skew_lengths](/img/skew_lengths.png)

## 配置偏斜

确保 printer.cfg 中包含 `[skew_correction]`。你现在可以使用 `SET_SKEW` gcode 来配置 skew_correction。例如，如果你沿 XY 的测量长度如下：

```
Length AC = 140.4
Length BD = 142.8
Length AD = 99.8
```

`SET_SKEW` 可用于配置 XY 平面的偏斜校正。

```
SET_SKEW XY=140.4,142.8,99.8
```
你还可以在 gcode 中添加 XZ 和 YZ 的测量值：

```
SET_SKEW XY=140.4,142.8,99.8 XZ=141.6,141.4,99.8 YZ=142.4,140.5,99.5
```

`[skew_correction]` 模块还支持与 `[bed_mesh]` 类似的配置文件管理。使用 `SET_SKEW` gcode 设置偏斜后，你可以使用 `SKEW_PROFILE` gcode 来保存它：

```
SKEW_PROFILE SAVE=my_skew_profile
```
此命令后，系统将提示你发出 `SAVE_CONFIG` gcode 将配置文件保存到持久存储中。如果不存在名为 `my_skew_profile` 的配置文件，则会创建一个新的配置文件。如果存在同名配置文件，它将被覆盖。

保存配置文件后，你可以加载它：
```
SKEW_PROFILE LOAD=my_skew_profile
```

也可以删除旧的或过期的配置文件：
```
SKEW_PROFILE REMOVE=my_skew_profile
```
删除配置文件后，系统将提示你发出 `SAVE_CONFIG` 以使此更改持久化。

## 验证校正

配置 skew_correction 后，你可以启用校正重新打印校准件。使用以下 gcode 检查每个平面的偏斜。结果应低于通过 `GET_CURRENT_SKEW` 报告的结果。

```
CALC_MEASURED_SKEW AC=<ac_length> BD=<bd_length> AD=<ad_length>
```

## 注意事项

由于偏斜校正的性质，建议在起始 gcode 中配置偏斜，即在归零和任何靠近打印区域边缘的移动（如清洁或喷嘴擦拭）之后。你可以使用 `SET_SKEW` 或 `SKEW_PROFILE` gcode 来完成此操作。还建议在结束 gcode 中发出 `SET_SKEW CLEAR=1`。

请记住，`[skew_correction]` 可能会生成使工具超出打印机 X 和/或 Y 轴边界的校正。使用 `[skew_correction]` 时，建议将零件远离边缘放置。
