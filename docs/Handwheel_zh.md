# 手轮（Jog Wheel）支持

## 概述

手轮模块允许使用物理旋转编码器直接控制打印机轴的移动。通过旋转编码器，用户可以精确地手动移动 X、Y、Z 或 E 轴，适用于校准、调试和手动操作场景。

## 配置

在 `printer.cfg` 中添加 `[handwheel]` 配置节：

```ini
[handwheel]
# 旋转编码器的 A、B 相引脚（必填）
encoder_pins: ^PA0, ^PA1

# 编码器每卡位的步数：2（半步）或 4（全步）（默认：4）
encoder_steps_per_detent: 4

# 按钮引脚，用于切换手轮模式开/关（可选）
click_pin: ^PA2

# 按钮消抖延迟，单位秒（默认：0，不消抖）
# debounce_delay: 0.025

# 默认活动轴：X、Y、Z 或 E（默认：X）
axis: X

# 每卡位移动距离，单位 mm（默认：1.0）
step_distance: 1.0

# 普通移动速度，单位 mm/s（默认：100.0）
speed: 100.0

# 快速旋转时的移动速度，单位 mm/s（默认：6000.0）
jog_speed: 6000.0

# 快速旋转判定阈值，单位秒（默认：0.030）
# 两次旋转间隔小于此值时使用 jog_speed
fast_rate: 0.030
```

## 引脚说明

| 参数 | 说明 | 示例 |
|------|------|------|
| `encoder_pins` | 旋转编码器 A、B 相引脚，逗号分隔 | `^PA0, ^PA1` |
| `click_pin` | 编码器按钮引脚（可选） | `^PA2` |
| `encoder_steps_per_detent` | 每卡位步数，2 或 4 | `4` |

> **注意**：如果 `[display]` 配置中已使用相同的 `encoder_pins`，则两个模块会共享同一个物理编码器。手轮激活时，菜单导航自动禁用；手轮关闭时，菜单导航恢复。

## G-code 命令

### JOG

启动或停止手轮点动模式。

```
JOG [AXIS=<axis>] [STEP=<distance>] [SPEED=<speed>] [STOP]
```

**参数**：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `AXIS` | 活动轴（X/Y/Z/E） | 配置值 |
| `STEP` | 每卡位移动距离 mm | 1.0 |
| `SPEED` | 移动速度 mm/s | 100.0 |
| `STOP` | 停止手轮模式 | - |

**示例**：

```gcode
JOG                        # 使用默认参数启动
JOG AXIS=Z STEP=0.1        # 控制 Z 轴，每步 0.1mm
JOG SPEED=200               # 设置速度为 200mm/s
JOG STOP                    # 停止手轮模式
```

### SET_JOG

修改手轮参数，不改变当前激活状态。

```
SET_JOG [AXIS=<axis>] [STEP=<distance>] [SPEED=<speed>] [JOG_SPEED=<speed>]
```

**参数**：

| 参数 | 说明 |
|------|------|
| `AXIS` | 活动轴（X/Y/Z/E） |
| `STEP` | 每卡位移动距离 mm |
| `SPEED` | 普通移动速度 mm/s |
| `JOG_SPEED` | 快速旋转移动速度 mm/s |

**示例**：

```gcode
SET_JOG AXIS=Y              # 切换到 Y 轴
SET_JOG STEP=0.01           # 设置每步 0.01mm
SET_JOG SPEED=200 JOG_SPEED=12000  # 设置速度
```

## 使用方法

### 方法一：G-code 命令

通过终端发送 G-code 命令激活手轮：

```gcode
JOG AXIS=X STEP=1.0
```

激活后，旋转编码器控制 X 轴移动，每卡位移动 1.0mm。

### 方法二：LCD 菜单

如果配置了 LCD 显示屏，可以通过菜单操作：

1. 进入 **Control** → **Handwheel**
2. 选择 **Jog: OFF** 切换为 **Jog: ON**
3. 使用 **Axis** 选择活动轴
4. 使用 **Step** 选择步进距离

### 方法三：物理按钮

如果配置了 `click_pin`，短按编码器按钮切换手轮模式开/关。

## 工作模式

| 模式 | 编码器旋转 | 按钮点击 |
|------|-----------|---------|
| 菜单模式（默认） | 导航菜单上下 | 确认选择 |
| 手轮模式 | 控制轴移动 | 切换回菜单模式 |

## 安全限制

- **未归位保护**：X/Y/Z 轴必须归位后才能通过手轮移动
- **E 轴限制**：E 轴移动需要 X 轴已归位
- **异常处理**：移动失败时自动记录日志，不会中断系统

## 状态查询

手轮状态可通过 `printer.handwheel` 访问：

```gcode
{printer.handwheel.is_active}      # 是否激活
{printer.handwheel.active_axis}    # 当前活动轴
{printer.handwheel.step_distance}  # 当前步进距离
{printer.handwheel.speed}          # 当前速度
```

## 接线示例

典型的旋转编码器模块（如 KY-040）接线：

```
编码器引脚    MCU 引脚
─────────────────────
CLK (A)  →  PA0 (上拉)
DT  (B)  →  PA1 (上拉)
SW       →  PA2 (上拉)
VCC      →  3.3V
GND      →  GND
```

配置示例：

```ini
[handwheel]
encoder_pins: ^PA0, ^PA1
click_pin: ^PA2
encoder_steps_per_detent: 4
axis: X
step_distance: 1.0
speed: 100.0
```

## 故障排除

| 问题 | 可能原因 | 解决方法 |
|------|---------|---------|
| 旋转无反应 | 手轮未激活 | 发送 `JOG` 命令或按按钮激活 |
| 移动方向相反 | A、B 相接反 | 交换 `encoder_pins` 中的两个引脚 |
| 每次移动多步 | `steps_per_detent` 设置错误 | 尝试改为 `2` 或 `4` |
| 移动不连续 | 编码器质量问题 | 增加 `debounce_delay` 值 |
| 菜单无法导航 | 手轮处于激活状态 | 按按钮或发送 `JOG STOP` 关闭手轮 |
