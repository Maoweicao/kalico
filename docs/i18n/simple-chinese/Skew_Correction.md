# 歪斜纠正

基于软件的歪斜纠正可以帮助解决由于打印机组装不完全成正方形而导致的尺寸不准确。注意，如果您的打印机明显歪斜，强烈建议在应用基于软件的纠正之前，先采取机械手段使打印机尽可能成正方形。

## 打印校准对象

纠正歪斜的第一步是沿您要纠正的平面打印一个
[校准对象](https://www.thingiverse.com/thing:2563185/files)。
也有一个
[校准对象](https://www.thingiverse.com/thing:2972743)
包含一个模型中的所有平面。您希望对象的方向使得角A朝向平面的原点。

确保在此打印期间未应用歪斜纠正。您可以通过从printer.cfg中删除`[skew_correction]`模块或发出`SET_SKEW CLEAR=1`  gcode来执行此操作。

## 进行测量

`[skew_correction]`模块需要为您要纠正的每个平面进行3次测量；从角A到角C的长度、从角B到角D的长度以及从角A到角D的长度。测量长度AD时，不要包括某些测试对象提供的角上的平面。

![skew_lengths](img/skew_lengths.png)

## 配置您的歪斜

确保`[skew_correction]`在printer.cfg中。您现在可以使用`SET_SKEW` gcode来配置歪斜纠正。例如，如果您沿XY测量的长度如下：

```
Length AC = 140.4
Length BD = 142.8
Length AD = 99.8
```

可以使用`SET_SKEW`为XY平面配置歪斜纠正。

```
SET_SKEW XY=140.4,142.8,99.8
```
您还可以为XZ和YZ添加测量值到gcode：

```
SET_SKEW XY=140.4,142.8,99.8 XZ=141.6,141.4,99.8 YZ=142.4,140.5,99.5
```

`[skew_correction]`模块也支持类似于`[bed_mesh]`的配置文件管理。使用`SET_SKEW` gcode设置歪斜后，您可以使用`SKEW_PROFILE` gcode来保存它：

```
SKEW_PROFILE SAVE=my_skew_profile
```
执行此命令后，系统会提示您发出`SAVE_CONFIG` gcode以将配置文件保存到持久存储。如果不存在名为`my_skew_profile`的配置文件，则将创建一个新配置文件。如果指定的配置文件存在，它将被覆盖。

拥有保存的配置文件后，您可以加载它：
```
SKEW_PROFILE LOAD=my_skew_profile
```

也可以删除旧的或过时的配置文件：
```
SKEW_PROFILE REMOVE=my_skew_profile
```
删除配置文件后，系统会提示您发出`SAVE_CONFIG`以使此更改持久化。

## 验证您的纠正

配置歪斜纠正后，您可以重新打印启用纠正的校准件。使用以下gcode检查每个平面的歪斜。结果应低于通过`GET_CURRENT_SKEW`报告的结果。

```
CALC_MEASURED_SKEW AC=<ac_length> BD=<bd_length> AD=<ad_length>
```

## 注意事项

由于歪斜纠正的性质，建议在您的启动gcode中配置歪斜，在归位和任何类似吹气或喷嘴擦拭等接近打印区域边缘的运动之后。您可以使用`SET_SKEW`或`SKEW_PROFILE` gcodes来实现此目的。还建议在结束gcode中发出`SET_SKEW CLEAR=1`。

请记住，`[skew_correction]`可能会生成一个纠正，将工具移动到打印机在X和/或Y轴上的边界之外。建议在使用`[skew_correction]`时将零件排列在远离边缘的地方。