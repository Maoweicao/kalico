# 运动学

本文档提供了 Kalico 如何实现机器人运动（其[运动学](https://en.wikipedia.org/wiki/Kinematics)）的概述。本内容可能会对有兴趣研究 Kalico 软件的开发者以及有兴趣更好地了解其机器的机制的用户感兴趣。

## 加速度

Kalico 在打印头改变速度时实现恒加速方案——速度逐渐改变到新速度，而不是突然急停。Kalico 始终在工具头和打印件之间强制执行加速。离开挤出机的丝材可能相当脆弱——快速急停和/或挤出机流量变化会导致质量下降和床面粘附不良。即使不挤出，如果打印头与打印件处于同一高度，打印头的快速急停可能会导致最近沉积的丝材受到破坏。限制打印头的速度变化（相对于打印件）会降低破坏打印件的风险。

限制加速度也很重要，这样步进电机就不会跳跃或给机器造成过度的应力。Kalico 通过限制打印头的加速度来限制每个步进电机的扭矩。在打印头处强制执行加速度自然也会限制移动打印头的步进电机的扭矩（反之亦然）。

Kalico 实现恒加速度。恒加速度的关键公式是：
```
velocity(time) = start_velocity + accel*time
```

## 梯形发生器

Kalico 使用传统的"梯形发生器"来模拟每次移动的运动——每次移动都有开始速度，以恒定加速度加速到巡航速度，以恒定速度巡航，然后使用恒定加速度减速到结束速度。

![trapezoid](img/trapezoid.svg.png)

它被称为"梯形发生器"，因为移动的速度图看起来像梯形。

巡航速度总是大于或等于开始速度和结束速度。加速阶段可能持续时间为零（如果开始速度等于巡航速度），巡航阶段可能持续时间为零（如果移动在加速后立即开始减速），和/或减速阶段可能持续时间为零（如果结束速度等于巡航速度）。

![trapezoids](img/trapezoids.svg.png)

## 前瞻

"前瞻"系统用于确定移动之间的拐角速度。

考虑以下包含在 XY 平面上的两次移动：

![corner](img/corner.svg.png)

在上述情况下，可以在第一次移动后完全减速，然后在下一次移动开始时完全加速，但这并不理想，因为所有加速和减速都会大大增加打印时间，频繁的挤出机流量变化会导致打印质量下降。

为了解决这个问题，"前瞻"机制对多个传入移动进行排队并分析移动之间的角度，以确定在两次移动之间的"交接处"可以获得的合理速度。如果下一次移动几乎在同一方向上，则头部只需减速一点（如果有的话）。

![lookahead](img/lookahead.svg.png)

但是，如果下一次移动形成锐角（头部在下一次移动中将向几乎相反的方向行进），则仅允许较小的交接速度。

![lookahead](img/lookahead-slow.svg.png)

交接速度是使用"近似向心加速度"确定的。最好[由作者描述](https://onehossshay.wordpress.com/2011/09/24/improving_grbl_cornering_algorithm/)。但是，在 Kalico 中，交接速度是通过指定所需速度来配置的，90° 拐角应该有（"方形拐角速度"），其他角度的交接速度是从中推导的。

前瞻的关键公式：
```
end_velocity^2 = start_velocity^2 + 2*accel*move_distance
```

### 最小巡航比率

Kalico 还实现了一种平滑短"之字形"移动运动的机制。考虑以下移动：

![zigzag](img/zigzag.svg.png)

在上述情况下，从加速到减速的频繁变化可能导致机器振动，从而对机器造成应力并增加噪音。Kalico 实现了一种机制来确保始终在加速和减速之间以巡航速度进行一些运动。这是通过降低某些移动（或移动序列）的顶部速度来完成的，以确保与加速和减速期间行进的距离相比，在巡航速度下行进的距离最少。

Kalico 通过跟踪常规移动加速度以及虚拟的"加速到减速"速率来实现此功能：

![smoothed](img/smoothed.svg.png)

具体来说，代码计算如果受限于此虚拟"加速到减速"速率，每次移动的速度会是什么。在上面的图片中，虚线灰线表示第一次移动的此虚拟加速率。如果移动无法使用此虚拟加速率达到其完全巡航速度，其顶部速度将降低到这种虚拟加速率下可能达到的最大速度。

对于大多数移动，该限制将在或高于移动的现有限制，不会引起行为变化。但是，对于短之字形移动，此限制会降低顶部速度。注意它不会改变移动内的实际加速度——移动继续使用正常加速方案至其调整后的顶部速度。

## 生成步进

前瞻过程完成后，给定移动的打印头运动是完全已知的（时间、开始位置、结束位置、每个点的速度），可以为移动生成步进时间。此过程在 Kalico 代码中的"运动学类"中完成。在这些运动学类之外，所有内容都以毫米、秒和笛卡尔坐标空间跟踪。运动学类的任务是从此通用坐标系转换到特定打印机的硬件细节。

Kalico 使用[迭代求解器](https://en.wikipedia.org/wiki/Root-finding_algorithm)为每个步进电机生成步进时间。代码包含计算每个时刻理想笛卡尔坐标的公式，并且它具有运动学公式来根据这些笛卡尔坐标计算理想的步进电机位置。利用这些公式，Kalico 可以确定步进电机应该处于每个步进位置的理想时间。给定的步进然后以这些计算时间进行调度。

在恒定加速下确定移动应该行进多远的关键公式是：
```
move_distance = (start_velocity + .5 * accel * move_time) * move_time
```
和以恒定速度移动的关键公式是：
```
move_distance = cruise_velocity * move_time
```

确定给定移动距离的移动的笛卡尔坐标的关键公式是：
```
cartesian_x_position = start_x + move_distance * total_x_movement / total_movement
cartesian_y_position = start_y + move_distance * total_y_movement / total_movement
cartesian_z_position = start_z + move_distance * total_z_movement / total_movement
```

### 笛卡尔机器人

为笛卡尔打印机生成步进是最简单的情况。每个轴上的运动与笛卡尔空间中的运动直接相关。

关键公式：
```
stepper_x_position = cartesian_x_position
stepper_y_position = cartesian_y_position
stepper_z_position = cartesian_z_position
```

### CoreXY 机器人

在 CoreXY 机器上生成步进只是比基本笛卡尔机器人稍微复杂一点。关键公式是：
```
stepper_a_position = cartesian_x_position + cartesian_y_position
stepper_b_position = cartesian_x_position - cartesian_y_position
stepper_z_position = cartesian_z_position
```

### Delta 机器人

Delta 机器人上的步进生成基于勾股定理：
```
stepper_position = (sqrt(arm_length^2
                         - (cartesian_x_position - tower_x_position)^2
                         - (cartesian_y_position - tower_y_position)^2)
                    + cartesian_z_position)
```

### 步进电机加速限制

使用 Delta 运动学，在笛卡尔空间中加速的移动可能需要特定步进电机上的加速度大于移动的加速度。当步进电机臂比垂直更水平时，运动线通过该步进电机的塔附近时会发生这种情况。尽管这些移动可能需要大于打印机配置的最大移动加速度的步进电机加速度，但该步进电机移动的有效质量会更小。因此，更高的步进电机加速度不会导致显著更高的步进电机扭矩，因此被认为是无害的。

但是，为了避免极端情况，Kalico 强制执行最大步进电机加速度上限为打印机配置的最大移动加速度的三倍。（类似地，步进电机的最大速度限制为最大移动速度的三倍。）为了强制执行此限制，在构建包围体的极端边缘处的移动（其中步进电机臂可能几乎水平）将具有较低的最大加速度和速度。

### 挤出机运动学

Kalico 在其自己的运动学类中实现挤出机运动。由于每次移动的打印头运动的时间和速度完全已知，可以独立于打印头运动的步进时间计算来计算挤出机的步进时间。

基本的挤出机运动易于计算。步进时间生成使用与笛卡尔机器人相同的公式：
```
stepper_position = requested_e_position
```

### 压力提前

实验表明，可以改进挤出机的建模，使其超出基本的挤出机公式。在理想情况下，当挤出移动进行时，应该在沿移动的每个点沉积相同体积的丝材，并且在移动后应该没有挤出的体积。不幸的是，通常发现基本挤出公式导致在挤出移动开始时从挤出机中退出的丝材太少，而在挤出结束后有过量丝材挤出。这通常被称为"渗漏"。

![ooze](img/ooze.svg.png)

"压力提前"系统尝试通过使用不同的挤出机模型来解决这个问题。与天真地相信放入挤出机的每 mm³ 丝材将立即导致该量的 mm³ 丝材从挤出机中退出不同，它使用基于压力的模型。压力在丝材被推入挤出机时增加（如[胡克定律](https://en.wikipedia.org/wiki/Hooke%27s_law)），挤出所需的压力由通过喷嘴孔的流速主导（如[泊肃叶定律](https://en.wikipedia.org/wiki/Poiseuille_law)）。关键思想是丝材、压力和流速之间的关系可以使用线性系数进行建模：
```
pa_position = nominal_position + pressure_advance_coefficient * nominal_velocity
```

有关如何找到此压力提前系数的信息，请参阅[压力提前](Pressure_Advance.md)文档。

基本的压力提前公式可能会导致挤出机电机做出突然的速度变化。Kalico 实现了挤出机运动的"平滑"以避免这种情况。

![pressure-advance](img/pressure-velocity.png)

上面的图表显示了两个挤出移动的示例，其间有非零的拐角速度。注意压力提前系统导致在加速期间向挤出机中推入额外的丝材。所需的丝材流速越高，加速期间必须推入的丝材就越多以解释压力。在头部减速期间，额外的丝材被缩回（挤出机将具有负速度）。

"平滑"是通过使用小时间段（由 `pressure_advance_smooth_time` 配置参数指定）内的挤出机位置的加权平均值来实现的。这种平均可以跨越多个 g 代码移动。注意挤出机电机将在第一个挤出移动的名义开始之前开始移动，并将在最后一个挤出移动的名义结束后继续移动。

"平滑压力提前"的关键公式：
```
smooth_pa_position(t) =
    ( definitive_integral(pa_position(x) * (smooth_time/2 - abs(t - x)) * dx,
                          from=t-smooth_time/2, to=t+smooth_time/2)
     / (smooth_time/2)^2 )