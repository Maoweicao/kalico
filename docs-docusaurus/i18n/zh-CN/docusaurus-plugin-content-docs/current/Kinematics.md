# 运动学

本文档概述了 Kalico 如何实现机器人运动（其[运动学](https://en.wikipedia.org/wiki/Kinematics)）。内容可能对 both 对 Kalico 软件感兴趣的开发者以及对更好地理解其机器力学感兴趣的用户都有兴趣。

## 加速度

Kalico 在打印头改变速度时实现恒定加速度——速度逐渐改变到新速度，而不是突然猛拉到它。Kalico 始终在工具头和打印之间强制执行加速度。离开挤出机的耗材可能非常脆弱——快速猛拉和/或挤出机流量变化会导致质量和床面附着力差。即使不挤出，如果打印头与打印处于同一水平，快速猛拉打印头也可能导致最近沉积的耗材中断。限制打印头（相对于打印）的速度变化可以降低中断打印的风险。

限制加速度也很重要，这样步进电机不会跳过或对机器施加过大压力。Kalico 通过限制打印头的加速度来限制每个步进器的扭矩。在打印头强制执行加速度自然也限制了移动打印头的步进器的扭矩（反之并不总是正确的）。

Kalico 实现恒定加速度。恒定加速度的关键公式是：
```
velocity(time) = start_velocity + accel*time
```

## 梯形发生器

Kalico 使用传统的"梯形发生器"来模拟每次移动的运动——每次移动有一个起始速度，它以恒定加速度加速到巡航速度，以恒定速度巡航，然后以恒定加速度减速到结束速度。

![trapezoid](/img/trapezoid.svg.png)

它被称为"梯形发生器"，因为移动的速度图看起来像一个梯形。

巡航速度始终大于或等于起始速度和结束速度。加速阶段可能为零持续时间（如果起始速度等于巡航速度），巡航阶段可能为零持续时间（如果移动在加速后立即开始减速），和/或减速阶段可能为零持续时间（如果结束速度等于巡航速度）。

![trapezoids](/img/trapezoids.svg.png)

## 前瞻

"前瞻"系统用于确定移动之间的转角速度。

考虑以下两个包含在 XY 平面上的移动：

![corner](/img/corner.svg.png)

在上述情况下，可以在第一次移动后完全减速，然后在下一次移动开始时完全加速，但这并不理想，因为所有这些加速度和减速会大大增加打印时间，并且挤出机流量的频繁变化会导致打印质量差。

为了解决这个问题，"前瞻"机制排队多个传入移动并分析移动之间的角度，以确定在两次移动之间的"接合"期间可以实现的合理速度。如果下一个移动几乎在相同方向，则头只需要稍微减速（如果有的话）。

![lookahead](/img/lookahead.svg.png)

但是，如果下一个移动形成锐角（头将在下一个移动中几乎反向移动），则只允许小的接合速度。

![lookahead](/img/lookahead-slow.svg.png)

接合速度使用"近似向心加速度"确定。最好由[作者描述](https://onehossshay.wordpress.com/2011/09/24/improving_grbl_cornering_algorithm/)。然而，在 Kalico 中，接合速度通过指定 90° 角应具有的所需速度（"方角速度"）来配置，其他角度的接合速度由此派生。

前瞻的关键公式：
```
end_velocity^2 = start_velocity^2 + 2*accel*move_distance
```

### 最小巡航比率

Kalico 还实现了一种机制来平滑短"锯齿形"移动的运动。考虑以下移动：

![zigzag](/img/zigzag.svg.png)

在上面，从加速到减速的频繁变化会导致机器振动，这会给机器施加压力并增加噪音。Kalico 实现了一种机制，确保在加速和减速之间始终有一些以巡航速度进行的运动。这是通过降低某些移动（或移动序列）的最高速度来实现的，以确保相对于加速和减速期间行进的距离，以巡航速度行进的最小距离。

Kalico 通过跟踪常规移动加速度和虚拟"加速度到减速"速率来实现此功能：

![smoothed](/img/smoothed.svg.png)

具体来说，代码计算每个移动的速度，如果它受限于此虚拟"加速度到减速"速率。在上面的图片中，灰色虚线表示第一个移动的此虚拟加速度速率。如果移动无法使用此虚拟加速度速率达到其全巡航速度，则其最高速度将降低到在此虚拟加速度速率下可获得的最大速度。

对于大多数移动，限制将处于或高于移动的现有限制，并且不会引起行为变化。然而，对于短锯齿形移动，此限制会降低最高速度。请注意，它不会改变移动内的实际加速度——移动继续使用正常加速度方案，直到其调整后的最高速度。

## 生成步进

前瞻过程完成后，给定移动的打印头运动已完全已知（时间、起始位置、结束位置、每个点的速度），可以为移动生成步进时间。此过程在 Kalico 代码中的"运动学类"内完成。在这些运动学类之外，所有内容都以毫米、秒和笛卡尔坐标空间进行跟踪。运动学类的任务是将此通用坐标系转换为特定打印机的硬件细节。

Kalico 使用[迭代求解器](https://en.wikipedia.org/wiki/Root-finding_algorithm)为每个步进器生成步进时间。代码包含计算每个时刻头的理想笛卡尔坐标的公式，并且具有基于这些笛卡尔坐标计算理想步进器位置的运动学公式。使用这些公式，Kalico 可以确定步进器应在每个步进位置的理想时间。然后在这些计算的时间安排给定的步进。

确定移动在恒定加速度下行进多远的关键公式是：
```
move_distance = (start_velocity + .5 * accel * move_time) * move_time
```
恒定速度运动的关键公式是：
```
move_distance = cruise_velocity * move_time
```

给定移动距离确定移动的笛卡尔坐标的关键公式是：
```
cartesian_x_position = start_x + move_distance * total_x_movement / total_movement
cartesian_y_position = start_y + move_distance * total_y_movement / total_movement
cartesian_z_position = start_z + move_distance * total_z_movement / total_movement
```

### 笛卡尔机器人

为笛卡尔打印机生成步进是最简单的情况。每个轴上的运动直接与笛卡尔空间中的运动相关。

关键公式：
```
stepper_x_position = cartesian_x_position
stepper_y_position = cartesian_y_position
stepper_z_position = cartesian_z_position
```

### CoreXY 机器人

在 CoreXY 机器上生成步进仅比基本笛卡尔机器人稍微复杂一点。关键公式是：
```
stepper_a_position = cartesian_x_position + cartesian_y_position
stepper_b_position = cartesian_x_position - cartesian_y_position
stepper_z_position = cartesian_z_position
```

### Delta 机器人

Delta 机器人上的步进生成基于毕达哥拉斯定理：
```
stepper_position = (sqrt(arm_length^2
                         - (cartesian_x_position - tower_x_position)^2
                         - (cartesian_y_position - tower_y_position)^2)
                    + cartesian_z_position)
```

### 步进电机加速度限制

使用 delta 运动学，在笛卡尔空间中加速的移动可能需要在特定步进电机上施加大于移动加速度的加速度。当步进臂比垂直更水平并且运动线经过该步进器的塔附近时，可能会发生这种情况。尽管这些移动可能需要步进电机加速度大于打印机配置的最大移动加速度，但该步进器移动的有效质量会更小。因此，较高的步进加速度不会导致明显较高的步进扭矩，因此被认为是无害的。

但是，为避免极端情况，Kalico 对步进加速度强制执行最大上限，为打印机配置的最大移动加速度的三倍。（类似地，步进器的最大速度限制为最大移动速度的三倍。）为了强制执行此限制，在构建包络极端边缘（步进臂可能几乎水平）的移动将具有较低的最大加速度和速度。

### 挤出机运动学

Kalico 在其自己的运动学类中实现挤出机运动。由于每次打印头移动的时间和速度对于每次移动都完全已知，因此可以独立于打印头移动的步进时间计算来计算挤出机的步进时间。

基本挤出机运动很容易计算。步进时间生成使用与笛卡尔机器人相同的公式：
```
stepper_position = requested_e_position
```

### 压力提前

实验表明，可以超出基本挤出机公式来改进挤出机的建模。在理想情况下，随着挤出移动的进行，应沿移动的每个点沉积相同体积的耗材，并且在移动后不应挤出任何体积。不幸的是，通常发现基本挤出公式导致在挤出移动开始时从挤出机排出的耗材太少，并且在挤出结束后挤出过多的耗材。这通常被称为"渗出"。

![ooze](/img/ooze.svg.png)

"压力提前"系统试图通过使用不同的挤出机模型来解决这个问题。它不是天真地相信送入挤出机的每立方毫米耗材将导致该量的立方毫米立即从挤出机排出，而是使用基于压力的模型。当耗材被推入挤出机时压力增加（如[胡克定律](https://en.wikipedia.org/wiki/Hooke%27s_law)），挤出所需的压力主要由通过喷嘴孔的流速决定（如[泊肃叶定律](https://en.wikipedia.org/wiki/Poiseuille_law)）。关键思想是耗材、压力和流速之间的关系可以使用线性系数建模：
```
pa_position = nominal_position + pressure_advance_coefficient * nominal_velocity
```

有关如何找到此压力提前系数的信息，请参阅[压力提前](Pressure_Advance.md)文档。

基本压力提前公式可能导致挤出机电机突然改变速度。Kalico 实现挤出机运动的"平滑"以避免这种情况。

![pressure-advance](/img/pressure-velocity.png)

上图显示了两个挤出移动之间具有非零转角速度的示例。请注意，压力提前系统在加速期间将额外的耗材推入挤出机。所需耗材流速越高，在加速期间必须推入更多耗材以考虑压力。在头减速期间，额外的耗材被回缩（挤出机将具有负速度）。

"平滑"是使用挤出机位置在小时间段内（由 `pressure_advance_smooth_time` 配置参数指定）的加权平均来实现的。此平均可以跨越多个 g-code 移动。请注意，挤出机电机将在第一次挤出移动的标称开始之前开始移动，并在最后一次挤出移动的标称结束后继续移动。

"平滑压力提前"的关键公式：
```
smooth_pa_position(t) =
    ( definitive_integral(pa_position(x) * (smooth_time/2 - abs(t - x)) * dx,
                          from=t-smooth_time/2, to=t+smooth_time/2)
     / (smooth_time/2)^2 )
```
