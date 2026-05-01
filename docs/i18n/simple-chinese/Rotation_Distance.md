# 旋转距离

Kalico上的步进电机驱动器在每个
[步进配置部分](Config_Reference.md#stepper)中需要一个`rotation_distance`
参数。`rotation_distance`是轴通过步进电机的一次完整旋转所移动的距离。本文档描述了如何配置此值。

## 从steps_per_mm（或step_distance）获取rotation_distance

您的3D打印机的设计人员最初从旋转距离计算了`steps_per_mm`。如果您知道steps_per_mm，则可以使用此通用公式获取原始旋转距离：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> / <steps_per_mm>
```

或者，如果您有较旧的Kalico配置并知道`step_distance`参数，您可以使用此公式：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> * <step_distance>
```

`<full_steps_per_rotation>`设置由步进电机的类型决定。大多数步进电机是"1.8度步进器"，因此每旋转200个完整步长（360除以1.8等于200）。一些步进电机是"0.9度步进器"，因此每旋转400个完整步长。其他步进电机很少见。如果不确定，不要在配置文件中设置full_steps_per_rotation，在上面的公式中使用200。

`<microsteps>`设置由步进电机驱动器决定。大多数驱动器使用16个微步。如果不确定，在配置中设置`microsteps: 16`并在上面的公式中使用16。

几乎所有打印机在X、Y和Z类型轴上应该有一个整数的`rotation_distance`。如果上面的公式导致rotation_distance在整数的0.01以内，则将最终值舍入到该整数。

## 在挤出机上校准rotation_distance

在挤出机上，`rotation_distance`是灯丝通过步进电机一次完全旋转所行进的距离。获得此设置准确值的最佳方法是使用"测量和修剪"程序。

首先从rotation distance的初始猜测开始。这可以从
[steps_per_mm](#obtaining-rotation_distance-from-steps_per_mm-or-step_distance)
获得，也可以通过[检查硬件](#extruder)获得。

然后使用以下程序来"测量和修剪"：
1. 确保挤出机中有灯丝，热端加热到适当的温度，打印机准备好挤出。
2. 使用标记笔在挤出机体的进口周围约70mm处在灯丝上放置一个标记。然后使用数字卡尺尽可能精确地测量该标记的实际距离。将其记为`<initial_mark_distance>`。
3. 使用以下命令序列挤出50mm灯丝：`G91`，然后是`G1 E50 F60`。将50mm记为`<requested_extrude_distance>`。等待挤出机完成移动（需要约50秒）。对此测试使用缓慢的挤出速率很重要，因为更快的速率会导致挤出机中的高压力，这会歪斜结果。（不要对此测试使用图形前端上的"挤出按钮"，因为它们以快速速率挤出。）
4. 使用数字卡尺测量挤出机体和灯丝上的标记之间的新距离。将其记为`<subsequent_mark_distance>`。然后计算：
   `actual_extrude_distance = <initial_mark_distance> - <subsequent_mark_distance>`
5. 计算rotation_distance为：
   `rotation_distance = <previous_rotation_distance> * <actual_extrude_distance> / <requested_extrude_distance>`
   将新的rotation_distance舍入到三位小数。

如果actual_extrude_distance与requested_extrude_distance相差超过约2mm，则是一个好主意再次执行上述步骤。

注意：请*不要*使用"测量和修剪"类型的方法来校准x、y或z类型轴。"测量和修剪"方法对于这些轴的准确性不够，可能会导致更差的配置。相反，如果需要，那些轴可以通过[测量皮带、滑轮和丝杆硬件](#obtaining-rotation_distance-by-inspecting-the-hardware)来确定。

## 通过检查硬件获取rotation_distance

可以通过了解步进电机和打印机运动学来计算rotation_distance。如果不知道steps_per_mm或设计新打印机，这可能很有用。

### 皮带驱动的轴

对于使用皮带和滑轮的线性轴，计算rotation_distance很容易。

首先确定皮带的类型。大多数打印机使用2mm皮带间距（即皮带上的每个齿相距2mm）。然后计算步进电机滑轮上的齿数。然后计算rotation_distance为：
```
rotation_distance = <belt_pitch> * <number_of_teeth_on_pulley>
```

例如，如果打印机具有2mm皮带并使用具有20个齿的滑轮，则旋转距离为40。

### 具有丝杆的轴

使用以下公式可以轻松计算常见丝杆的rotation_distance：
```
rotation_distance = <screw_pitch> * <number_of_separate_threads>
```

例如，常见的"T8导螺杆"的旋转距离为8（间距为2mm，有4个单独的螺纹）。

较旧的打印机带有"螺纹杆"，导螺杆上只有一个"螺纹"，因此旋转距离是螺杆的间距。（螺杆间距是螺杆上每个凹槽之间的距离。）例如，M6公制棒的旋转距离为1，M8棒的旋转距离为1.25。

### 挤出机

通过测量推动灯丝的"爱好螺栓"的直径，可以获得挤出机的初始旋转距离，并使用以下公式：`rotation_distance = <diameter> * 3.14`

如果挤出机使用齿轮，则还需要[为挤出机确定并设置gear_ratio](#using-a-gear_ratio)。

挤出机上的实际旋转距离会因打印机而异，因为与灯丝啮合的"爱好螺栓"的抓握力可能会变化。它甚至可以在灯丝线轴之间变化。获得初始rotation_distance后，使用[测量和修剪程序](#calibrating-rotation_distance-on-extruders)来获得更准确的设置。

## 使用gear_ratio

设置`gear_ratio`可以更容易地在具有齿轮箱（或类似物）的步进器上配置`rotation_distance`。大多数步进器都没有齿轮箱——如果不确定，则不要在配置中设置`gear_ratio`。

设置`gear_ratio`时，`rotation_distance`表示轴通过齿轮箱上的最后一个齿轮的一次完全旋转所移动的距离。例如，如果使用具有"5:1"比率的齿轮箱，可以使用[硬件知识](#obtaining-rotation_distance-by-inspecting-the-hardware)计算rotation_distance，然后将`gear_ratio: 5:1`添加到配置中。

对于通过皮带和滑轮实现的齿轮传动，可以通过计算滑轮上的齿数来确定gear_ratio。例如，如果带有16个齿的步进器驱动下一个带有80个齿的滑轮，则使用`gear_ratio: 80:16`。事实上，可以打开普通现成的"齿轮箱"并计算其中的齿数来确认其齿轮比。

注意，有时齿轮箱的齿轮比与其宣传的略有不同。常见的BMG挤出机齿轮就是这样一个例子——它们被宣传为"3:1"，但实际上使用"50:17"齿轮。（使用没有公分母的齿数可能会改进整体齿轮磨损，因为齿不总是以相同方式啮合。）常见的"5.18:1行星齿轮箱"可以更准确地配置为`gear_ratio: 57:11`。

如果在轴上使用了多个齿轮，则可以为gear_ratio提供逗号分隔的列表。例如，"5:1"齿轮箱驱动16齿到80齿滑轮可以使用`gear_ratio: 5:1, 80:16`。

在大多数情况下，gear_ratio应该用整数定义，因为常见的齿轮和滑轮上有整数个齿。但是，在皮带使用摩擦而不是齿来驱动滑轮的情况下，在齿轮比中使用浮点数可能是有意义的（例如，`gear_ratio: 107.237:16`）。