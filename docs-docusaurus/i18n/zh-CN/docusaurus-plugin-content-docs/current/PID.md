
# PID

PID 控制是 3D 打印领域广泛使用的控制方法。它在温度控制方面无处不在，无论是加热器产生热量还是风扇去除热量。本文档旨在提供 PID 的高级概述以及如何在 Kalico 中最好地使用它。

## PID 校准

### 准备校准
执行校准测试时，应尽可能减少外部影响：
* 关闭辅助风扇
* 关闭腔室加热器
* 校准床面时关闭挤出机加热器，反之亦然
* 避免气流等外部干扰

比上面列出的更重要的是，**按你打印的方式进行 PID 校准**。如果你打印时部件风扇开着，请在它们开着的情况下进行 PID 调优。

### 选择正确的 PID 算法
Kalico 提供两种不同的 PID 算法：位置式和速度式

* 位置式 (`pid`)
    * 标准算法
    * 对噪声温度读数非常鲁棒
    * 可能导致过冲
    * 在边缘情况下目标控制不足
* 速度式 (`pid_v`)
    * 无过冲
    * 在某些场景下目标控制更好
    * 更容易受噪声传感器影响
    * 可能需要更大的平滑时间常数

请参阅配置参考中的[控制语句](Config_Reference.md#extruder)。

### 运行 PID 校准
PID 校准通过 [PID_CALIBRATE](G-Codes.md#pid_calibrate) 命令调用。此命令将加热相应的加热器，并让它在目标温度附近多个周期内冷却，以确定所需的参数。

这样的校准周期如下所示：
```
3:12 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:15 PM   sample:1 pwm:1.0000 asymmetry:3.7519 tolerance:n/a
3:15 PM   sample:2 pwm:0.6229 asymmetry:0.3348 tolerance:n/a
3:16 PM   sample:3 pwm:0.5937 asymmetry:0.0840 tolerance:n/a
3:17 PM   sample:4 pwm:0.5866 asymmetry:0.0169 tolerance:0.4134
3:18 PM   sample:5 pwm:0.5852 asymmetry:0.0668 tolerance:0.0377
3:18 PM   sample:6 pwm:0.5794 asymmetry:0.0168 tolerance:0.0142
3:19 PM   sample:7 pwm:0.5780 asymmetry:-0.1169 tolerance:0.0086
3:19 PM   PID parameters: pid_Kp=16.538 pid_Ki=0.801 pid_Kd=85.375
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```
注意 `asymmetry` 信息。它提供了加热器功率是否足以确保对称的"加热"与"冷却/热损失"行为的指示。它应该从正值开始并收敛到零。负的起始值表示热损失快于加热，这意味着系统是不对称的。校准仍然会成功，但抵御干扰的余量可能较低。

## 高级/手动校准

有许多方法可用于计算控制参数，如 Ziegler-Nichols、Cohen-Coon、Kappa-Tau、Lambda 等。默认情况下，生成经典的 Ziegler-Nichols 参数。如果用户想尝试其他风格的 Ziegler-Nichols 或 Cohen-Coon 参数，可以从日志中提取常数（如下所示），并将其输入到此[电子表格](resources/pid_params.xls)中。

```text
Ziegler-Nichols constants: Ku=0.103092 Tu=41.800000
Cohen-Coon constants: Km=-17.734845 Theta=6.600000 Tau=-10.182680
```

经典的 Ziegler-Nichols 参数在所有场景下都能工作。Cohen-Coon 参数在具有大量死区时间/延迟的系统中效果更好。例如，如果打印机具有热质量大、加热和稳定慢的床面，Cohen-Coon 参数通常在控制方面做得更好。

## 进一步阅读
### 历史

第一个初级 PID 控制器由 Elmer Sperry 于 1911 年开发，用于自动控制船舶的舵。工程师 Nicolas Minorsky 于 1922 年发表了第一篇 PID 控制器的数学分析。1942 年，John Ziegler 和 Nathaniel Nichols 发表了他们的开创性论文"自动控制器的最佳设置"，描述了一种调整 PID 控制器的试错方法，现在通常称为"Ziegler-Nichols 方法"。

1984 年，Karl Astrom 和 Tore Hagglund 发表了他们的论文"具有相位和幅度裕度规格的简单调节器的自动调谐"，在论文中他们介绍了一种通常称为"Astrom-Hagglund 方法"或"继电器方法"的自动调谐方法。

2019 年，Brandon Taysom 和 Carl Sorensen 发表了他们的论文"静态和非静态扰动下的自适应继电器自动调谐及其在搅拌摩擦焊中的应用"，提出了一种从继电器测试中生成更准确结果的方法。这就是 Kalico 目前使用的 PID 校准方法。

### 继电器测试的细节
如前所述，Kalico 使用继电器测试进行校准。标准继电器测试在概念上很简单。你打开和关闭加热器的电源，使其在目标温度附近振荡，如下图所示。

![simple relay test](/img/pid_01.png)

上图显示了标准继电器测试的常见问题。如果被校准的系统对于所选目标温度来说功率过多或过少，它将产生偏倚和不对称的结果。如上所示，系统处于关闭状态的时间比开启状态多，并且高于目标温度的振幅比低于目标温度的振幅大。

在理想系统中，开启和关闭时间以及高于和低于目标温度的振幅将相同。3D 打印机不会主动冷却热端或床面，因此它们永远无法达到理想状态。

下图是基于 Taysom 和 Sorensen 提出的方法论的继电器测试。每次迭代后，分析数据并计算新的最大功率设置。如图所示，系统开始测试时不对称，但结束时非常对称。

![advanced relay test](/img/pid_02.png)

在校准运行期间可以实时监控不对称性。它还可以提供加热器是否适合当前校准参数的见解。当不对称性从正值开始并收敛到零时，加热器有充足的功率来实现校准参数的对称性。

```
3:12 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:15 PM   sample:1 pwm:1.0000 asymmetry:3.7519 tolerance:n/a
3:15 PM   sample:2 pwm:0.6229 asymmetry:0.3348 tolerance:n/a
3:16 PM   sample:3 pwm:0.5937 asymmetry:0.0840 tolerance:n/a
3:17 PM   sample:4 pwm:0.5866 asymmetry:0.0169 tolerance:0.4134
3:18 PM   sample:5 pwm:0.5852 asymmetry:0.0668 tolerance:0.0377
3:18 PM   sample:6 pwm:0.5794 asymmetry:0.0168 tolerance:0.0142
3:19 PM   sample:7 pwm:0.5780 asymmetry:-0.1169 tolerance:0.0086
3:19 PM   PID parameters: pid_Kp=16.538 pid_Ki=0.801 pid_Kd=85.375
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```

当不对称性从负值开始时，它不会收敛到零。如果 Kalico 没有报错，校准运行将完成并提供良好的 PID 参数，然而加热器处理干扰的能力不如具有功率余量的加热器。

```
3:36 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:38 PM   sample:1 pwm:1.0000 asymmetry:-2.1149 tolerance:n/a
3:39 PM   sample:2 pwm:1.0000 asymmetry:-2.0140 tolerance:n/a
3:39 PM   sample:3 pwm:1.0000 asymmetry:-1.8811 tolerance:n/a
3:40 PM   sample:4 pwm:1.0000 asymmetry:-1.8978 tolerance:0.0000
3:40 PM   PID parameters: pid_Kp=21.231 pid_Ki=1.227 pid_Kd=91.826
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```

### PID 控制算法

Kalico 目前支持两种控制算法：位置式和速度式。两种算法之间的根本区别在于，位置式算法计算当前时间间隔的 PWM 值应该是多少，而速度式算法计算应将之前的 PWM 设置更改多少以获得当前时间间隔的 PWM 值。

位置式是默认算法，因为它在所有场景下都能工作。速度式算法可以提供比位置式算法更好的结果，但需要较低噪声的传感器读数或较大的平滑时间设置。

两种算法之间最明显的区别是，对于相同的配置参数，速度控制将消除或大幅减少过冲，如下图所示，因为它不受积分饱和的影响。

![algorithm comparison](/img/pid_03.png)

![zoomed algorithm comparison](/img/pid_04.png)

在某些场景下，速度控制在将加热器保持在其目标温度和抑制干扰方面也更好。主要原因是速度控制更像标准的二阶微分方程。它考虑了位置、速度和加速度。
