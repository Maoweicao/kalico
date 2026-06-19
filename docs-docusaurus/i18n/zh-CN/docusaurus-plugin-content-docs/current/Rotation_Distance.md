# 旋转距离

Kalico 上的步进电机驱动需要在每个[步进器配置节](Config_Reference.md#stepper)中设置 `rotation_distance` 参数。`rotation_distance` 是步进电机每完整旋转一圈轴移动的距离。本文档描述了如何配置此值。

## 从 steps_per_mm（或 step_distance）获取 rotation_distance

你的 3d 打印机设计者最初是从旋转距离计算 `steps_per_mm` 的。如果你知道 steps_per_mm，则可以使用此通用公式获取原始旋转距离：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> / <steps_per_mm>
```

或者，如果你有较旧的 Kalico 配置并且知道 `step_distance` 参数，可以使用此公式：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> * <step_distance>
```

`<full_steps_per_rotation>` 设置由步进电机类型决定。大多数步进电机是"1.8 度步进器"，因此每圈有 200 个全步（360 除以 1.8 等于 200）。某些步进电机是"0.9 度步进器"，因此每圈有 400 个全步。其他步进电机很少见。如果不确定，请勿在配置文件中设置 full_steps_per_rotation，并在上面的公式中使用 200。

`<microsteps>` 设置由步进电机驱动决定。大多数驱动使用 16 个微步。如果不确定，请在配置中设置 `microsteps: 16` 并在上面的公式中使用 16。

几乎所有打印机在 X、Y 和 Z 类型轴上的 `rotation_distance` 都应该是整数。如果上述公式得出的 rotation_distance 与整数相差在 0.01 以内，则将最终值四舍五入到该整数。

## 校准挤出机的 rotation_distance

在挤出机上，`rotation_distance` 是步进电机每完整旋转一圈耗材移动的距离。获取此设置准确值的最佳方法是使用"测量和修剪"程序。

首先从旋转距离的初始猜测开始。这可以从 [steps_per_mm](#obtaining-rotation_distance-from-steps_per_mm-or-step_distance) 或[检查硬件](#extruder)获得。

然后使用以下"测量和修剪"程序：
1. 确保挤出机中有耗材，热端已加热到适当温度，打印机已准备好挤出。
2. 使用记号笔在距挤出机主体入口约 70mm 处的耗材上做一个标记。然后使用数字卡尺尽可能精确地测量该标记的实际距离。将其记为 `<initial_mark_distance>`。
3. 使用以下命令序列挤出 50mm 耗材：`G91` 后跟 `G1 E50 F60`。将 50mm 记为 `<requested_extrude_distance>`。等待挤出机完成移动（大约需要 50 秒）。重要的是使用缓慢的挤出速率进行此测试，因为较快的速率可能导致挤出机中产生高压，从而扭曲结果。（不要使用图形前端上的"挤出按钮"进行此测试，因为它们以快速率挤出。）
4. 使用数字卡尺测量挤出机主体和耗材上标记之间的新距离。将其记为 `<subsequent_mark_distance>`。然后计算：`actual_extrude_distance = <initial_mark_distance> - <subsequent_mark_distance>`
5. 计算 rotation_distance 为：`rotation_distance = <previous_rotation_distance> * <actual_extrude_distance> / <requested_extrude_distance>` 将新的 rotation_distance 四舍五入到三位小数。

如果 actual_extrude_distance 与 requested_extrude_distance 相差超过约 2mm，最好第二次执行上述步骤。

注意：*不要*使用"测量和修剪"类型的方法来校准 x、y 或 z 类型轴。"测量和修剪"方法对这些轴来说不够准确，可能会导致更差的配置。相反，如果需要，可以通过[测量皮带、滑轮和丝杠硬件](#obtaining-rotation_distance-by-inspecting-the-hardware)来确定这些轴。

## 通过检查硬件获取 rotation_distance

可以通过了解步进电机和打印机运动学来计算 rotation_distance。如果不知道 steps_per_mm 或设计新打印机，这可能很有用。

### 皮带驱动轴

计算使用皮带和滑轮的线性轴的 rotation_distance 很容易。

首先确定皮带类型。大多数打印机使用 2mm 皮带节距（即皮带上的每个齿相距 2mm）。然后数一数步进电机滑轮上的齿数。然后计算 rotation_distance：
```
rotation_distance = <belt_pitch> * <number_of_teeth_on_pulley>
```

例如，如果打印机有 2mm 皮带并使用 20 齿的滑轮，则旋转距离为 40。

### 带丝杠的轴

使用以下公式可以轻松计算常见丝杠的 rotation_distance：
```
rotation_distance = <screw_pitch> * <number_of_separate_threads>
```

例如，常见的"T8 丝杠"旋转距离为 8（螺距为 2mm，有 4 个独立螺纹）。

带有"螺纹杆"的较旧打印机丝杠上只有一个"螺纹"，因此旋转距离是螺钉的螺距。（螺距是螺钉上每个凹槽之间的距离。）因此，例如，M6 公制杆的旋转距离为 1，M8 杆的旋转距离为 1.25。

### 挤出机

可以通过测量推动耗材的"齿轮螺栓"的直径并使用以下公式来获得挤出机的初始旋转距离：`rotation_distance = <diameter> * 3.14`

如果挤出机使用齿轮，则还需要[确定并设置齿轮比](#using-a-gear_ratio)。

挤出机上的实际旋转距离会因打印机而异，因为啮合耗材的"齿轮螺栓"的抓力可能不同。甚至在不同的耗材卷之间也会有所不同。获得初始 rotation_distance 后，使用[测量和修剪程序](#calibrating-rotation_distance-on-extruders)来获得更准确的设置。

## 使用 gear_ratio

设置 `gear_ratio` 可以更轻松地配置带有齿轮箱（或类似装置）的步进器的 `rotation_distance`。大多数步进器没有齿轮箱——如果不确定，请勿在配置中设置 `gear_ratio`。

设置 `gear_ratio` 时，`rotation_distance` 表示齿轮箱上最终齿轮完整旋转一圈轴移动的距离。例如，如果使用"5:1"比的齿轮箱，则可以使用[硬件知识](#obtaining-rotation_distance-by-inspecting-the-hardware)计算 rotation_distance，然后在配置中添加 `gear_ratio: 5:1`。

对于使用皮带和滑轮实现的齿轮传动，可以通过数滑轮上的齿数来确定 gear_ratio。例如，如果一个 16 齿的滑轮驱动下一个 80 齿的滑轮，则应使用 `gear_ratio: 80:16`。实际上，可以打开常见的现成"齿轮箱"并数一数其中的齿数以确认其齿轮比。

请注意，有时齿轮箱的齿轮比与宣传的略有不同。常见的 BMG 挤出机电机齿轮就是一个例子——它们宣传为"3:1"，但实际上使用"50:17"齿轮传动。（使用没有公分母的齿数可能改善整体齿轮磨损，因为齿在每次旋转中并不总是以相同方式啮合。）常见的"5.18:1 行星齿轮箱"更准确地配置为 `gear_ratio: 57:11`。

如果在一个轴上使用多个齿轮，则可以向 gear_ratio 提供逗号分隔的列表。例如，"5:1"齿轮箱驱动 16 齿到 80 齿的滑轮可以使用 `gear_ratio: 5:1, 80:16`。

在大多数情况下，gear_ratio 应使用整数定义，因为常见齿轮和滑轮上有整数个齿。但是，在皮带使用摩擦而非齿驱动滑轮的情况下，可能在齿轮比中使用浮点数是有意义的（例如，`gear_ratio: 107.237:16`）。
