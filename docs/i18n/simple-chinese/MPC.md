# 模型预测控制

模型预测控制（MPC）是提供传统PID控制替代方案的先进温度控制方法。
MPC利用系统模型来模拟热端的温度并调整加热器功率以与目标温度对齐。

与反应性方法不同，MPC主动运行，提前调整以应对温度波动。
它利用热端的模型，考虑系统的热质量、加热器功率、向环境空气的热损失、
风扇和热转移到灯丝中的因素。该模型允许MPC预测在给定时间内
从热端散发的热能量，并通过相应调整加热器功率进行补偿。
因此，MPC可以准确计算必要的热能输入以维持稳定的温度或过渡到新温度。

MPC相比PID控制提供多个优势：

- **更快更响应的温度控制：** MPC的主动方法允许它更快速更准确地
  响应来自风扇或流速变化的温度变化。
- **单一校准的广泛功能：** 一旦校准，MPC在宽范围的打印温度下有效运行。
- **简化的校准过程：** MPC比传统PID控制更容易校准。
- **与所有热端传感器类型的兼容性：** MPC与所有类型的热端传感器工作，
  包括产生噪声温度读数的传感器。
- **加热器类型的多功能性：** MPC在标准笛卡尔加热器和PTC加热器上性能良好。
- **有效用于高低流量热端：** 无论热端的流速如何，MPC保持有效的温度控制。

> [!CAUTION]
> 此功能控制3D打印机的可变得非常热的部分。所有标准Kalico警告适用。
> 请将所有问题和错误报告到[GitHub](https://github.com/KalicoCrew/kalico/issues)
> 或[Discord](Contact.md#discord)。

# 基本配置

要使用MPC作为挤出机的温度控制器，使用以下基本配置块。

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
  _必需_  
  温度控制方法。
  
- `heater_power: 50`  
  _必需_   
  标称加热器功率（瓦特）。
  对于PTC（非线性加热器），MPC由于相对于加热器温度的功率输出变化
  可能不会最优工作。建议将heater_power设置为预期打印温度
  下的功率输出。
  
- `cooling_fan:`  
  _默认值：无_  
  冷却挤出灯丝和热端的风扇。默认无风扇，因此
  控制加热器时不会考虑风扇。指定"fan"将自动使用部分冷却风扇。
  
- `filament_diameter: 1.75`  
  _默认值：1.75（毫米）_  
  这是灯丝直径。
  
- `filament_density: 1.20`   
  _默认值：1.20（克/毫米^3）_  
  这是所打印灯丝的材料密度。
  
- `filament_heat_capacity: 1.80`  
  _默认值：1.80（焦耳/克/开尔文）_  
  这是所打印灯丝的材料比热容。

## 可选配置参数

这些可以在配置中指定，但对于大多数用户不应该从默认值更改。

- `maximum_retract:`  
  _默认值：2.0（毫米）_  
  此值限制在MPC FFF计算期间单个周期内挤出机向后允许的多少。
  这让灯丝功率变成负并为系统添加少量能量。

- `target_reach_time:`  
  _默认值：2.0（秒）_  
 
- `smoothing:`  
  _默认值：0.83（秒）_  
  此参数影响模型学习的速度，代表每秒应用的温度差异比率。
  1.0的值表示模型中没有使用平滑。
  
- `min_ambient_change:`  
  _默认值：1.0（摄氏度/秒）_  
  MIN_AMBIENT_CHANGE的较大值将导致更快的收敛，
  但也会导致模拟环境温度在理想值周围有些混乱地波动。
  
- `steady_state_rate:`  
  _默认值：0.5（摄氏度/秒）_  
  
- `ambient_temp_sensor: temperature_sensor <sensor_name>`  
  _默认值：MPC估计_  
  建议不指定此参数，让MPC估计。这用于初始状态温度和校准，
  但不用于实际控制。可以使用任何温度传感器，但传感器应靠近热端
  或测量热端周围的环境空气。

## PTC加热器功率

对于PTC风格加热器，建议在正常打印温度下设置`heater power:`。
下面给出一些常见PTC加热器以供参考。如果您的加热器未列出，
制造商应能够提供温度和功率曲线。

| 加热器温度（℃） | Rapido 2（瓦） | Rapido 1（瓦） | Dragon Ace旧（瓦） | Dragon Ace新（瓦） | Revo 40（瓦） |Revo 60（瓦） |
|:---------------:|:------------:|:------------:|:------------------:|:------------------:|:-----------:|:----------:|
| 180             | 72           | 52           | 51                 | 66                 | 30          |45          |
| 200             | 70           | 51           | 48                 | 63                 | 29          |44          |
| 220             | 67           | 50           | 46                 | 60                 | 28          |43          |
| 240             | 65           | 49           | 44                 | 58                 | 28          |42          |
| 260             | 64           | 48           | 43                 | 55                 | 27          |40          |
| 280             | 62           | 47           | 41                 | 53                 | 27          |39          |
| 300             | 60           | 46           | 39                 | 51                 | 26          |38          |

## 灯丝前馈配置

灯丝前馈（FFF）功能允许MPC向前看，查看可能需要更多或更少热输入
以维持目标温度的挤出速率变化。此功能大大提高了模型在打印期间
的准确性和响应性。它默认启用，可以用`filament_density`
和`filament_heat_capacity`配置参数更详细定义。默认值设置为涵盖
包括ABS、ASA、PLA、PETG在内的广泛标准材料。

FFF参数可以为打印机会话设置，使用`MPC_SET` G代码命令：

`MPC_SET HEATER=<heater> FILAMENT_DENSITY=<value> FILAMENT_HEAT_CAPACITY=<value> [FILAMENT_TEMP=<sensor|ambient|<value>>]`

- `HEATER`:  
  仅支持挤出机
  
- `FILAMENT_DENSITY`:  
  灯丝密度（克/毫米^3）
  
- `FILAMENT_HEAT_CAPACITY`:  
  灯丝热容（焦耳/克/开尔文）
  
- `FILAMENT_TEMP`:  
  这可以设置为`sensor`、`ambient`或设置温度值。FFF将使用
  加热灯丝所需的特定能量，功率损失将基于温度增量计算。

例如，更新ASA的灯丝材料属性将是：

```
MPC_SET HEATER=extruder FILAMENT_DENSITY=1.07 FILAMENT_HEAT_CAPACITY=1.7  
```

## 灯丝物理属性

MPC最好知道加热1毫米灯丝1°C需要多少能量（焦耳）。
下表中的材料值已从流行的灯丝制造商和材料数据参考中精编。
这些值足以使MPC实施FFF功能。高级用户可能基于制造商数据表调整
`filament_density`和`filament_heat_capacity`参数。

### 常见材料

| 材料 | 密度[克/立方厘米] | 比热[焦耳/克/开尔文] |
| -------- |:---------------:|:---------------------:|
| PLA      | 1.25            | 1.8 - 2.2             |
| PETG     | 1.27            | 1.7 - 2.2             |
| PC+ABS   | 1.15            | 1.5 - 2.2             |
| ABS      | 1.06            | 1.25 - 2.4            |
| ASA      | 1.07            | 1.3 - 2.1             |
| PA6      | 1.12            | 2 - 2.5               |
| PA       | 1.15            | 2 - 2.5               |
| PC       | 1.20            | 1.1 - 1.9             |
| TPU      | 1.21            | 1.5 - 2               |
| TPU-90A  | 1.15            | 1.5 - 2               |
| TPU-95A  | 1.22            | 1.5 - 2               |

### 常见碳纤维填充材料

| 材料                                     | 密度[克/立方厘米] | 比热[焦耳/克/开尔文] |
| -------------------------------------------- |:---------------:|:---------------------:|
| ABS-CF                                       | 1.11            | ^                     |
| ASA-CF                                       | 1.11            | ^                     |
| PA6-CF                                       | 1.19            | ^                     |
| PC+ABS-CF                                    | 1.22            | ^                     |
| PC+CF                                        | 1.36            | ^                     |
| PLA-CF                                       | 1.29            | ^                     |
| PETG-CF                                      | 1.30            | ^                     |  

^ 使用基聚合物的比热

# 校准

MPC默认校准程序执行以下步骤：

> 1. 冷却到环境：校准程序需要知道大约的环境温度，并等待直到热端温度
>    稳定并停止相对于环境降低。
> 2. 加热超过200°C：测量温度上升最快的点，以及该点处的时间和温度。
>    还需要三个温度测量在初始延迟生效后的某个点。
> 3. 保持温度同时测量环境热损失：此时已知足够进行MPC算法参与。
>    校准程序对200°C将发生的过冲进行最佳猜测，
>    并以大约一分钟的目标此温度同时在无风扇的情况下测量环境热损失
>    和风扇启用（如果指定`cooling_fan`）。
> 4. MPC校准程序创建适当的模型常数。此时模型参数是临时的，还未保存到打印机配置。

MPC校准程序必须为要由MPC控制的每个加热器运行以确定模型参数。
要使MPC校准成功，挤出机必须能够达到200℃。校准使用以下G代码命令执行。

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`

- `HEATER=<heater>`:  
  要校准的挤出机加热器。
  
- `TARGET=<temperature>`:  
  _默认值：200（摄氏度）_  
  设置校准温度。200℃的默认值对挤出机是很好的目标。
  MPC校准是温度独立的，所以在更高的温度下校准挤出机
  不一定会产生更好的模型参数。这是高级用户探索的领域。
  
- `FAN_BREAKPOINTS=<value>`:  
  _默认值：3_  
  设置在校准期间测试的风扇设置点数。可以指定任意数量的断点，
  例如7个断点会导致（0、16%、33%、50%、66%、83%、100%）风扇速度。
  建议使用一个数字来捕获一个或多个测试点低于最常使用的最低级别的风扇。
  例如，如果20%风扇是最常使用的最低速度，建议使用11个断点
  以在低范围测试10%和20%风扇。

默认使用七个风扇断点校准热端：
```
MPC_CALIBRATE HEATER=extruder FAN_BREAKPOINTS=7
```
> [!NOTE]
> 确保部分冷却风扇在开始校准前关闭。

成功校准后，该方法将为参考生成关键模型参数到日志。

![校准参数输出](img/MPC_calibration_output.png)

然后需要`SAVE_CONFIG`命令提交这些校准的模型参数到打印机配置，
或用户可以手动更新值。_SAVE_CONFIG_块随后应看起来像：

```
#*# <----------- SAVE_CONFIG ----------->
#*# 不编辑此块或以下。内容是自动生成的。
#*# [extruder]
#*# control = mpc
#*# block_heat_capacity = 22.3110
#*# sensor_responsiveness = 0.0998635
#*# ambient_transfer = 0.155082
#*# fan_ambient_transfer=0.155082, 0.20156, 0.216441
```

> [!NOTE]
> 如果[extruder]部分位于printer.cfg以外的.cfg文件中，
> `SAVE_CONFIG`命令可能无法写入校准参数，klippy将提供错误。

这些模型参数不适合预配置或不能明确确定。高级用户可能基于以下指导
在校准后调整这些参数：略微增加这些值将增加MPC结算的温度，
略微减少它们将减少结算温度。

- `block_heat_capacity:`  
  加热器块的热容（焦耳/开尔文）。
  
- `ambient_transfer:`  
  加热器块到环境的热传递（瓦/开尔文）。
  
- `sensor_responsiveness:`  
  代表加热器块到传感器的热传递系数和传感器热容
  的单一常数（开尔文/秒/开尔文）。
  
- `fan_ambient_transfer:`  
  启用风扇时加热器块到环境的热传递（瓦/开尔文）。

# 支持宏

## 温度等待

以下宏可用于用利用`temperature_wait` G代码的宏替换`M109`热端温度设置
和`M190`床温度设置G代码命令。这可用于传感器温度需要很长时间才能
收敛到设置温度的系统中。
> [!NOTE]
> 此行为主要发生是因为MPC控制建模的块温度而不是热端温度传感器。
> 对于几乎所有情况，当温度传感器过冲/下冲发生时，块建模的温度
> 将正确处于设置温度。但是，Kalico系统仅基于传感器温度执行操作，
> 这可能导致股票`M109`和`M190`命令的打印操作中不理想的延迟。

```
[gcode_macro M109] # 等待热端温度
rename_existing: M109.1
gcode:
    #参数
    {% set s = params.S|float %}

    M104 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}  # 设置热端温度
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=extruder MINIMUM={s-2} MAXIMUM={s+5}   # 等待热端温度（在n度内）
    {% endif %}


[gcode_macro M190] # 等待床温度
rename_existing: M190.1
gcode:
    #参数
    {% set s = params.S|float %}

    M140 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}   # 设置床温度
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=heater_bed MINIMUM={s-2} MAXIMUM={s+5}  # 等待床温度（在n度内）
    {% endif %}
```

### 从切片机设置FFF参数

此宏将在从切片机传递材料类型时自动设置FFF参数。

```ini
[gcode_macro _SET_MPC_MATERIAL]
description: 设置给定材料的加热器MPC参数
variable_filament_table:
    ## 更新此表以调整材料设置
    {
        ## （密度，热容）# 建议的热容范围
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

        RESPOND PREFIX=🔥 MSG="为{heater}配置的{material}MPC。密度：{density}，热容：{heat_capacity}"
    {% else %}
        {% set density = extruder_config.filament_density %}
        {% set heat_capacity=extruder_config.filament_heat_capacity %}

        RESPOND PREFIX=🔥 MSG="未知材料'{material}'，为{heater}使用默认mpc参数"
    {% endif %}

    MPC_SET HEATER={heater} FILAMENT_DENSITY={density} FILAMENT_HEAT_CAPACITY={heat_capacity}
```

切片机必须配置为将当前材料类型传递到您的`PRINT_START`宏。
对于PrusaSlicer，您应在启动G代码部分向`print_start`添加以下参数行：

```
MATERIAL=[filament_type[initial_extruder]]
```

PrusaSlicer中的print_start行将看起来像：

```
start_print MATERIAL=[filament_type[initial_extruder]] EXTRUDER_TEMP={first_layer_temperature[initial_extruder]} BED_TEMP={first_layer_bed_temperature[initial_extruder]} CHAMBER_TEMP={chamber_temperature}
```

然后，在您的`PRINT_START`宏中包括以下宏调用：

```
_SET_MPC_MATERIAL MATERIAL={params.MATERIAL}
```

# 实时模型状态

实时温度和模型状态可以从浏览器通过输入以下本地地址查看。

```
https://192.168.xxx.xxx:7125/printer/objects/query?extruder
```

![校准](img/MPC_realtime_output.png)

# 实验功能

## 床加热器

使用MPC进行床加热器控制是可行的，但性能不能保证或目前不支持。
可以简单地配置床的MPC。

```
[heater_bed]
control: mpc
heater_power: 400
```

- `control: mpc`  
  _必需_  
  温度控制方法。
  
- `heater_power: 50`  
  _必需_  
  标称加热器功率（瓦特）。
  
- `cooling_fan: fan_generic <fan_name>`  
  _无默认值_  
  这是冷却床的风扇。可选参数支持床风扇。

床应该能够达到至少90℃以使用以下G代码进行校准。

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`

- `HEATER=<heater>`:  
  要校准的床加热器。
  
- `TARGET=<temperature>`:  
  _默认值：90（摄氏度）_  
  设置校准温度。90℃的默认值是床的很好目标。
  
- `FAN_BREAKPOINTS=<value>`:  
  _默认值：3_  
  设置在校准期间测试的风扇设置点数。

默认使用五个风扇断点校准热端：
```
MPC_CALIBRATE HEATER=heater_bed FAN_BREAKPOINTS=5
```

这些校准的模型参数需要手动保存到_SAVE_CONFIG_块或使用`SAVE_CONFIG`命令。

## 在运行时更新校准参数

类似于[`SET_HEATER_PID`](G-Codes.md#set_heater_pid)，
您可以在运行时更新您的MPC校准配置文件。

`MPC_SET HEATER=<heater_name> [BLOCK_HEAT_CAPACITY=0.0] [SENSOR_RESPONSIVENESS=0.0] [AMBIENT_TRANSFER=0.0] [FAN_AMBIENT_TRANSFER=0.01,0.02,0.03]`

# 背景

## MPC算法

MPC将热端系统建模为四个热质量：环境空气、灯丝、加热器块和传感器。
加热器功率直接加热建模的加热器块。环境空气加热或冷却加热器块。
灯丝冷却加热器块。加热器块加热或冷却传感器。

每次MPC算法运行时，它使用以下信息计算模拟热端和传感器的新温度：

- 热端的最后功率设置。
- 对环境温度的现在最佳猜测。
- 风扇对向环境空气热损失的影响。
- 灯丝进料速率对热损失的影响。假设灯丝在与环境空气相同的温度。

完成此计算后，模拟传感器温度与测得的温度进行比较，
差异的一部分被添加到建模的传感器和加热器块温度。
这将模拟系统拖向真实系统。因为只应用差异的一部分，
传感器噪声被减少并随时间平均到零。模拟和真实传感器都展示相同的（或非常相似的）延迟。
因此，当这些值相互比较时，延迟的影响被消除。
所以，模拟热端仅最小受传感器噪声和延迟的影响。

平滑是应用于模拟和测得传感器温度之间差异的因子。在其最大值1，
模拟传感器温度连续设置等于测得的传感器温度。较低的值将导致
MPC输出中更大的稳定性，但也导致响应性降低。大约0.25的值似乎工作得很好。

没有模拟是完美的，无论如何，真实生活环境温度改变。
所以MPC也维持对环境温度的最佳猜测。当模拟系统接近稳定状态时，
模拟环境温度持续调整。稳定状态由MPC算法不在其限制处驱动热端
（即完全或零加热器功率）或当处于其限制但温度仍然没有改变很多时
确定——这将在渐近温度发生（通常当目标温度为零且热端处于环境时）。

steady_state_rate用于识别渐近条件。每当模拟热端温度在算法的
两个连续运行之间以小于steady_state_rate的绝对速率改变时，
应用稳定状态逻辑。因为算法频繁运行，即使少量噪声也会导致
相当高的热端温度变化的瞬时速率。实际上，1°C/秒似乎对steady_state_rate有效。

当处于稳定状态时，真实和模拟传感器温度之间的差异用于驱动
对环境温度的变化。但是，当温度真的接近时，min_ambient_change
确保模拟环境温度相对快速收敛。min_ambient_change的较大值
将导致更快的收敛但也导致模拟环境温度在理想值周围有些混乱地波动。
这不是一个问题，因为环境温度的影响相当小，
甚至短期10°C或更多变化将不会产生明显的影响。

重要的是注意模拟环境温度只有在环境热传递系数完全准确时
才会收敛到真实的世界环境温度。实际上不会是这样的情况，
因此模拟环境温度也充当对这些不准确性的修正。

最后，配备新的温度集合，MPC算法计算必须应用多少功率
使加热器块在下两秒内达到目标温度。此计算考虑预期损失到环境空气
和灯丝加热的热。这个功率值随后转换为PWM输出。

## 额外细节

请参见出色的Marlin MPC文档了解关于相应整形器的模型推导、
调整方法和热转移系数的深入概述。此部分包含对受支持的输入整形器
的一些（通常近似）参数的简短概述。

# 确认

此功能是Marlin MPC实现的一个端口，所有信用归功于其团队
和社区为开源3D打印开拓此功能。Marlin MPC文档和github页面
被大量参考，在某些情况下直接复制和编辑以创建本文档。

- Marlin MPC文档：[https://marlinfw.org/docs/features/model_predictive_control.html]
- 在Marlin中实现MPC的GITHUB PR：[https://github.com/MarlinFirmware/Marlin/pull/23751]
- Marlin源代码：[https://github.com/MarlinFirmware/Marlin]