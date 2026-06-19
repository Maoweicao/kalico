# 模型预测控制

模型预测控制（MPC）是一种先进的温度控制方法，为传统 PID 控制提供了替代方案。MPC 利用系统模型来模拟热端的温度，并调整加热器功率以与目标温度保持一致。

与反应式方法不同，MPC 主动运行，预期温度波动并进行调整。它利用热端模型，考虑系统热质量、加热器功率、向环境空气和风扇的热损失以及向耗材的热传递等因素。该模型允许 MPC 预测在给定时间内将从热端散发的热量，并通过相应地调整加热器功率来补偿这一点。因此，MPC 可以准确计算维持稳定温度或过渡到新温度所需的热能输入。

MPC 相比 PID 控制具有以下优势：

- **更快、响应更灵敏的温度控制：** MPC 的主动方法使其能够更快速、更准确地响应风扇或流速变化引起的温度变化。
- **单一校准即可实现广泛功能：** 校准后，MPC 可在广泛的打印温度范围内有效运行。
- **简化的校准过程：** 与传统 PID 控制相比，MPC 更易于校准。
- **兼容所有热端传感器类型：** MPC 适用于所有类型的热端传感器，包括产生噪声温度读数的传感器。
- **加热器类型的多功能性：** MPC 在标准加热棒和 PTC 加热器上表现良好。
- **对高低流量热端均有效：** 无论热端的流量如何，MPC 都能保持有效的温度控制。

> [!CAUTION]
> 此功能控制 3D 打印机中可能变得非常热的部分。所有标准 Kalico 警告均适用。请将所有问题和错误报告给 [GitHub](https://github.com/KalicoCrew/kalico/issues) 或 [Discord](Contact.md#discord)。

# 基本配置

要使用 MPC 作为挤出机的温度控制器，请使用以下基本配置块。

```
[extruder]
control: mpc
heater_power: 50  
cooling_fan:
filament_diameter: 1.75
filament_density: 1.20
filament_heat_capacity: 1.8 
```

- `control: mpc`
  *必需*
  温度控制方法。

- `heater_power: 50`
  *必需*
  加热器铭牌功率（瓦特）。
  对于 PTC（非线性加热器），MPC 可能无法达到最佳效果，因为这种加热器的功率输出相对于加热器温度会发生变化。建议将 heater_power 设置为预期打印温度下的功率输出。

- `cooling_fan:`
  _默认值：无_
  冷却挤出耗材和热端的风扇。默认情况下没有风扇，因此控制加热器时不会考虑任何风扇。指定"fan"将自动使用部件冷却风扇。

- `filament_diameter: 1.75`
  _默认值：1.75 (mm)_
  这是耗材直径。

- `filament_density: 1.20`
  _默认值：1.20 (g/mm^3)_
  这是正在打印的耗材的材料密度。

- `filament_heat_capacity: 1.80`
  _默认值：1.80 (J/g/K)_
  这是正在打印的耗材的材料比热容。

## 可选配置参数

这些可以在配置中指定，但对于大多数用户来说不需要更改默认值。

- `maximum_retract:`
  _默认值：2.0 (mm)_
  此值限制在 MPC FFF 计算期间单个周期内挤出机允许向后移动的量。这允许耗材功率变为负值并向系统添加少量能量。

- `target_reach_time:`
  _默认值：2.0 (sec)_

- `smoothing:`
  _默认值：0.83 (sec)_
  此参数影响模型学习的速度，它表示每秒应用的温度差异比率。值 1.0 表示模型中未使用平滑。

- `min_ambient_change:`
  _默认值：1.0 (deg C/s)_
  较大的 MIN_AMBIENT_CHANGE 值会导致更快的收敛，但也会导致模拟环境温度在理想值附近有些混乱地波动。

- `steady_state_rate:`
  _默认值：0.5 (deg C/s)_

- `ambient_temp_sensor: temperature_sensor <sensor_name>`
  _默认值：MPC ESTIMATE_
  建议不要指定此参数，让 MPC 进行估算。这用于初始状态温度和校准，但不用于实际控制。任何温度传感器都可以使用，但传感器应靠近热端或测量热端周围的环境空气。

## PTC 加热器功率

建议将 PTC 式加热器的 `heater_power:` 设置为打印机的正常打印温度。下面提供了一些常见的 PTC 加热器供参考。如果你的加热器未列出，制造商应能提供温度和功率曲线。

| 加热器温度 (C) | Rapido 2 (W) | Rapido 1 (W) | Dragon Ace 旧版 (W) | Dragon Ace 新版 (W) | Revo 40 (W) | Revo 60 (W) |
|:---------------:|:------------:|:------------:|:------------------:|:------------------:|:-----------:|:----------:|
| 180             | 72           | 52           | 51                 | 66                 | 30          | 45          |
| 200             | 70           | 51           | 48                 | 63                 | 29          | 44          |
| 220             | 67           | 50           | 46                 | 60                 | 28          | 43          |
| 240             | 65           | 49           | 44                 | 58                 | 28          | 42          |
| 260             | 64           | 48           | 43                 | 55                 | 27          | 40          |
| 280             | 62           | 47           | 41                 | 53                 | 27          | 39          |
| 300             | 60           | 46           | 39                 | 51                 | 26          | 38          |

## 耗材前馈配置

耗材前馈（FFF）功能使 MPC 能够前瞻并查看挤出速率的变化，这可能需要更多或更少的热量输入来维持目标温度。此功能在打印期间显著提高了模型的准确性和响应性。默认启用，可以通过 `filament_density` 和 `filament_heat_capacity` 配置参数进行更详细的定义。默认值设置为覆盖广泛的常用材料，包括 ABS、ASA、PLA、PETG。

可以通过 `MPC_SET` G-Code 命令为打印机会话设置 FFF 参数：

`MPC_SET HEATER=<heater> FILAMENT_DENSITY=<value> FILAMENT_HEAT_CAPACITY=<value> [FILAMENT_TEMP=<sensor|ambient|<value>>]`

- `HEATER`：
  仅支持挤出机

- `FILAMENT_DENSITY`：
  耗材密度（g/mm^3）

- `FILAMENT_HEAT_CAPACITY`：
  耗材热容量（J/g/K）

- `FILAMENT_TEMP`：
  可以设置为 `sensor`、`ambient` 或设定的温度值。FFF 将使用加热耗材所需的特定能量，并根据温度差计算功率损失。

例如，更新 ASA 的耗材材料属性：

```
MPC_SET HEATER=extruder FILAMENT_DENSITY=1.07 FILAMENT_HEAT_CAPACITY=1.7  
```

## 耗材物理属性

MPC 最好知道加热 1mm 耗材升高 1°C 所需的能量（焦耳）。下表中的材料值来自流行的耗材制造商和材料数据参考。这些值足以让 MPC 实现 FFF 功能。高级用户可以根据制造商数据表调整 `filament_density` 和 `filament_heat_capacity` 参数。

### 常用材料

| 材料   | 密度 [g/cm³] | 比热 [J/g/K] |
| ------ |:------------:|:------------:|
| PLA    | 1.25         | 1.8 - 2.2    |
| PETG   | 1.27         | 1.7 - 2.2    |
| PC+ABS | 1.15         | 1.5 - 2.2    |
| ABS    | 1.06         | 1.25 - 2.4   |
| ASA    | 1.07         | 1.3 - 2.1    |
| PA6    | 1.12         | 2 - 2.5      |
| PA     | 1.15         | 2 - 2.5      |
| PC     | 1.20         | 1.1 - 1.9    |
| TPU    | 1.21         | 1.5 - 2      |
| TPU-90A| 1.15         | 1.5 - 2      |
| TPU-95A| 1.22         | 1.5 - 2      |

### 常用碳纤维填充材料

| 材料                    | 密度 [g/cm³] | 比热 [J/g/K] |
| ---------------------- |:------------:|:------------:|
| ABS-CF                 | 1.11         | ^            |
| ASA-CF                 | 1.11         | ^            |
| PA6-CF                 | 1.19         | ^            |
| PC+ABS-CF              | 1.22         | ^            |
| PC+CF                  | 1.36         | ^            |
| PLA-CF                 | 1.29         | ^            |
| PETG-CF                | 1.30         | ^            |

^ 使用基础聚合物的比热

# 校准

MPC 默认校准例程采用以下步骤：

> 1. 冷却至环境温度：校准例程需要知道近似的环境温度，并等待热端温度稳定并停止相对于环境温度下降。
> 2. 加热超过 200°C：测量温度上升最快的点，以及该点的时间和温度。此外，在初始延迟生效后的某个时间点需要进行三次温度测量。
> 3. 测量环境热损失时保持温度：此时 MPC 算法已掌握足够信息。校准例程会猜测超过 200°C 时的超调量，并将此温度作为目标约一分钟，同时在不启动和启动风扇的情况下测量环境热损失（如果指定了 `cooling_fan`）。
> 4. MPC 校准例程创建适当的模型常量。此时模型参数是临时的，尚未保存到打印机配置中。

必须为每个受 MPC 控制的加热器运行 MPC 校准例程，以确定模型参数。为了使 MPC 校准成功，挤出机必须能够达到 200C。使用以下 G-code 命令执行校准。

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`

- `HEATER=<heater>`：
  要校准的挤出机加热器。

- `TARGET=<temperature>`：
  _默认值：200 (deg C)_
  设置校准温度。默认的 200C 是挤出机的良好目标。MPC 校准与温度无关，因此在更高温度下校准挤出机不一定会产生更好的模型参数。这是高级用户探索的领域。

- `FAN_BREAKPOINTS=<value>`：
  _默认值：3_
  设置在校准期间测试的风扇设定点数量。可以指定任意数量的断点，例如 7 个断点将导致（0、16%、33%、50%、66%、83%、100%）的风扇速度。
  建议使用一个能捕获一个或多个低于通常使用的最低级别风扇测试点的数字。例如，如果 20% 风扇是最常用的最低速度，建议使用 11 个断点在低范围内测试 10% 和 20% 风扇。

使用七个风扇断点进行热端默认校准：
```
MPC_CALIBRATE HEATER=extruder FAN_BREAKPOINTS=7
```
> [!NOTE]
> 请确保在开始校准前部件冷却风扇已关闭。

成功校准后，该方法将关键模型参数生成到日志中以供将来参考。

![校准参数输出](/img/MPC_calibration_output.png)

然后需要 `SAVE_CONFIG` 命令将这些校准的模型参数提交到打印机配置，或者用户可以手动更新值。_SAVE_CONFIG_ 块应如下所示：

```
#*# <----------- SAVE_CONFIG ----------->
#*# DO NOT EDIT THIS BLOCK OR BELOW. The contents are auto-generated.
#*# [extruder]
#*# control = mpc
#*# block_heat_capacity = 22.3110
#*# sensor_responsiveness = 0.0998635
#*# ambient_transfer = 0.155082
#*# fan_ambient_transfer=0.155082, 0.20156, 0.216441
```

> [!NOTE]
> 如果 [extruder] 部分在 printer.cfg 以外的 .cfg 文件中，`SAVE_CONFIG` 命令可能无法写入校准参数，klippy 将提供错误。

这些模型参数不适合预先配置或无法明确确定。高级用户可以根据以下指导在校准后进行微调：略微增加这些值会增加 MPC 稳定的温度，略微减小它们会降低稳定温度。

- `block_heat_capacity:`
  加热块的热容量（J/K）。

- `ambient_transfer:`
  从加热块到环境的热传递（W/K）。

- `sensor_responsiveness:`
  表示从加热块到传感器的热传递系数和传感器热容量的单一常数（K/s/K）。

- `fan_ambient_transfer:`
  启用风扇时从加热块到环境的热传递（W/K）。

# 支持宏

## 温度等待

以下宏可用于用利用 `temperature_wait` G-code 的宏替换 `M109` 热端温度设置和 `M190` 热床温度设置 G-code 命令。这可用于传感器温度需要较长时间才能收敛到设定温度的系统。

> [!NOTE]
> 此行为主要发生是因为 MPC 控制的是模拟的加热块温度，而不是热端温度传感器。在几乎所有情况下，当温度传感器出现超调/欠调时，加热块模拟温度将正确处于设定温度。但是，Kalico 系统仅基于传感器温度执行操作，这可能导致使用标准 `M109` 和 `M190` 命令时打印操作出现不良延迟。

```
[gcode_macro M109] # 等待热端温度
rename_existing: M109.1
gcode:
    #参数
    {% set s = params.S|float %}

    M104 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}  # 设置热端温度
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=extruder MINIMUM={s-2} MAXIMUM={s+5}   # 等待热端温度（在 n 度范围内）
    {% endif %}


[gcode_macro M190] # 等待热床温度
rename_existing: M190.1
gcode:
    #参数
    {% set s = params.S|float %}

    M140 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}   # 设置热床温度
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=heater_bed MINIMUM={s-2} MAXIMUM={s+5}  # 等待热床温度（在 n 度范围内）
    {% endif %}
```

### 从切片器设置 FFF 参数

当从切片器传递材料类型时，此宏将自动设置 FFF 参数。

```ini
[gcode_macro _SET_MPC_MATERIAL]
description: 设置给定材料的加热器 MPC 参数
variable_filament_table:
    ## 更新此表以调整材料设置
    {
        ## ( 密度, 热容量 )  # 建议的热容量范围
        "PLA"       : ( 1.25, 2.20 ),  # 1.80 - 2.20
        "PETG"      : ( 1.27, 2.20 ),  # 1.70 - 2.20
        "PC+ABS"    : ( 1.15, 2.20 ),  # 1.50 - 2.20
        "ABS"       : ( 1.06, 2.40 ),  # 1.25 - 2.40
        "ASA"       : ( 1.07, 2.10 ),  # 1.30 - 2.10
        "PA6"       : ( 1.12, 2.50 ),  # 2.00 - 2.50
        "PA"        : ( 1.15, 2.50 ),  # 2.00 - 2.50
        "PC"        : ( 1.20, 1.90 ),  # 1.10 - 1.90
        "TPU"       : ( 1.21, 2.00 ),  # 1.50 - 2.00
        "TPU-90A"   : ( 1.15, 2.00 ),  # 1.50 - 2.00
        "TPU-95A"   : ( 1.22, 2.00 ),  # 1.50 - 2.00
        "ABS-CF"    : ( 1.11, 2.40 ),  # 1.25 - 2.40
        "ASA-CF"    : ( 1.11, 2.10 ),  # 1.30 - 2.10
        "PA6-CF"    : ( 1.19, 2.50 ),  # 2.00 - 2.50
        "PC+ABS-CF" : ( 1.22, 2.20 ),  # 1.50 - 2.20
        "PC+CF"     : ( 1.36, 1.90 ),  # 1.10 - 1.90
        "PLA-CF"    : ( 1.29, 2.20 ),  # 1.80 - 2.20
        "PETG-CF"   : ( 1.30, 2.20 ),  # 1.70 - 2.20
    }
gcode:
    {% set material = params.MATERIAL | upper %}
    {% set heater = params.HEATER | default('extruder') %}
    {% set extruder_config = printer.configfile.settings[heater] %}

    {% if material in filament_table %}
        {% set (density, heat_capacity) = filament_table[material] %}

        RESPOND PREFIX=🔥 MSG="已为 {material} 配置 {heater} MPC。密度：{density}，热容量：{heat_capacity}"
    {% else %}
        {% set density = extruder_config.filament_density %}
        {% set heat_capacity=extruder_config.filament_heat_capacity %}

        RESPOND PREFIX=🔥 MSG="未知材料 '{material}'，使用 {heater} 的默认 mpc 参数"
    {% endif %}

    MPC_SET HEATER={heater} FILAMENT_DENSITY={density} FILAMENT_HEAT_CAPACITY={heat_capacity}
```

切片器必须配置为将当前材料类型传递给你的 `PRINT_START` 宏。对于 PrusaSlinger，你应该在 Start G-Code 部分的 `print_start` 中添加以下参数行：

```
MATERIAL=[filament_type[initial_extruder]]
```

PrusaSlicer 中的 print_start 行应如下所示：

```
start_print MATERIAL=[filament_type[initial_extruder]] EXTRUDER_TEMP={first_layer_temperature[initial_extruder]} BED_TEMP={first_layer_bed_temperature[initial_extruder]} CHAMBER_TEMP={chamber_temperature}
```

然后，在你的 `PRINT_START` 宏中包含以下宏调用：

```
_SET_MPC_MATERIAL MATERIAL={params.MATERIAL}
```

# 实时模型状态

可以通过在浏览器中输入计算机的以下本地地址来查看实时温度和模型状态。

```
https://192.168.xxx.xxx:7125/printer/objects/query?extruder
```

![校准](/img/MPC_realtime_output.png)

# 实验性功能

## 热床加热器

使用 MPC 控制热床加热器是可行的，但性能不保证或目前不受支持。可以简单地配置热床的 MPC。

```
[heater_bed]
control: mpc
heater_power: 400
```

- `control: mpc`
  *必需*
  温度控制方法。

- `heater_power: 50`
  *必需*
  加热器铭牌功率（瓦特）。

- `cooling_fan: fan_generic <fan_name>`
  _无默认值_
  这是冷却热床的风扇。可选参数以支持热床风扇。

热床应能至少达到 90C 才能使用以下 G-code 执行校准。

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`

- `HEATER=<heater>`：
  要校准的热床加热器。

- `TARGET=<temperature>`：
  _默认值：90 (deg C)_
  设置校准温度。默认的 90C 是热床的良好目标。

- `FAN_BREAKPOINTS=<value>`：
  _默认值：3_
  设置在校准期间测试的风扇设定点数量。

使用五个风扇断点进行热端默认校准：
```
MPC_CALIBRATE HEATER=heater_bed FAN_BREAKPOINTS=5
```

这些校准的模型参数需要手动或通过使用 `SAVE_CONFIG` 命令保存到 _SAVE_CONFIG_ 块。

## 在运行时更新校准参数

类似于 [`SET_HEATER_PID`](G-Codes.md#set_heater_pid)，你可以在运行时更新 MPC 校准配置文件。

`MPC_SET HEATER=<heater_name> [BLOCK_HEAT_CAPACITY=0.0] [SENSOR_RESPONSIVENESS=0.0] [AMBIENT_TRANSFER=0.0] [FAN_AMBIENT_TRANSFER=0.01,0.02,0.03]`

# 背景

## MPC 算法

MPC 将热端系统建模为四个热质量：环境空气、耗材、加热块和传感器。加热器功率直接加热模拟的加热块。环境空气加热或冷却加热块。耗材冷却加热块。加热块加热或冷却传感器。

每次 MPC 算法运行时，它使用以下信息计算模拟热端和传感器的新温度：

- 热端的上次功率设置。
- 环境温度的当前最佳估计。
- 风扇对向环境空气热损失的影响。
- 耗材进料速率对向耗材热损失的影响。耗材被假定与环境空气处于相同温度。

一旦完成此计算，将模拟传感器温度与测量温度进行比较，并将差值的一小部分添加到模拟的传感器和加热块温度中。这会将模拟系统向真实系统方向拖动。由于只应用了差值的一小部分，传感器噪声会减小，并且随着时间的推移平均为零。模拟和真实传感器都表现出相同（或非常相似）的延迟。因此，当这些值相互比较时，延迟的影响被消除。因此，模拟热端仅受到传感器噪声和延迟的最小影响。

SMOOTHING 是应用于模拟和测量传感器温度差值的因子。在其最大值 1 时，模拟传感器温度持续设置为等于测量传感器温度。较低的值将导致 MPC 输出功率更高的稳定性，但也会降低响应性。0.25 左右的值似乎效果很好。

没有完美的模拟，而且无论如何，现实生活中的环境温度会变化。因此 MPC 还维护环境温度的最佳估计。当模拟系统接近稳态时，模拟环境温度会持续调整。稳态被确定为 MPC 算法未以其极限驱动热端（即，全功率或零功率）时，或者当它处于极限但温度变化仍然不大时——这通常在渐近温度时发生（通常当目标温度为零且热端处于环境温度时）。

steady_state_rate 用于识别渐近条件。每当模拟热端温度在两次连续算法运行之间的绝对变化率小于 steady_state_rate 时，就会应用稳态逻辑。由于算法频繁运行，即使少量噪声也可能导致热端温度的瞬时变化率相当高。实际上，1°C/s 似乎对于 steady_state_rate 效果良好。

在稳态下，真实和模拟传感器温度之间的差异用于驱动环境温度的变化。但是，当温度非常接近时，min_ambient_change 确保模拟环境温度相对较快地收敛。较大的 min_ambient_change 值会导致更快的收敛，但也会导致模拟环境温度在理想值附近有些混乱地波动。这不是问题，因为环境温度的影响相当小，即使 10°C 或更大的短期变化也不会产生明显影响。

重要的是要注意，如果环境热传递系数完全准确，模拟环境温度将只收敛到真实世界的环境温度。在实践中这不会发生，因此模拟环境温度也充当这些不准确性的校正。

最后，根据新的温度集，MPC 算法计算必须施加多少功率才能在接下来的两秒内使加热块达到目标温度。此计算考虑了预期向环境空气和耗材加热的热量损失。然后将此功率值转换为 PWM 输出。

## 附加详情

请参阅优秀的 Marlin MPC 文档，了解此功能中使用的模型推导、调整方法和热传递系数信息。

# 致谢

此功能是 Marlin MPC 实现的移植，所有荣誉归于他们的团队和社区，他们为开源 3D 打印开创了此功能。Marlin MPC 文档和 github 页面被大量引用，在某些情况下直接复制和编辑以创建此文档。

- Marlin MPC 文档：[https://marlinfw.org/docs/features/model_predictive_control.html]
- 在 Marlin 中实现 MPC 的 GITHUB PR：[https://github.com/MarlinFirmware/Marlin/pull/23751]
- Marlin 源代码：[https://github.com/MarlinFirmware/Marlin]
