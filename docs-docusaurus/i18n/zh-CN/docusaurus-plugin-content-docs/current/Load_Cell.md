# 称重传感器

本文档描述了对称重传感器的支持。称重传感器使用 ADC 测量施加在应变片上的力。它们可用于读取力数据、称量耗材卷等物品，或作为探针使用。

警告：在使用称重传感器之前必须对其进行校准。如果校准不正确，报告的力/重量将不正确，这可能导致称重传感器和/或打印机永久损坏。此模块无法补偿校准不良、应变片损坏或电气噪声。

## 基本称重传感器配置

称重传感器可以配置为用作秤。

```ini
[load_cell]
sensor_type: hx717
sclk_pin: PA5
dout_pin: PA4
sample_rate: 320
counts_per_gram: 245
reference_tare_counts: 12345
```

- `sensor_type: hx717`\
  _必需_\
  每个传感器有不同的必填字段，请检查其配置参考以获取详细信息：

  * [`hx711`](Config_Reference.md#hx711)
  * [`hx717`](Config_Reference.md#hx717)
  * [`ads1220`](Config_Reference.md#ads1220)
  * [`ads131m02`](Config_Reference.md#ads131m02)
  * [`ads131m04`](Config_Reference.md#ads131m04)

- `counts_per_gram: 245`\
  _默认值：None_\
  从原始传感器计数到克的转换系数，由 `LOAD_CELL_CALIBRATE` 计算。

- `reference_tare_counts: 12345`\
  _必需_\
  原始传感器计数的基线皮重值，由 `LOAD_CELL_CALIBRATE` 设置。

## 诊断

### 检查称重传感器操作

`LOAD_CELL_DIAGNOSTIC`（[文档](G-Codes.md#load_cell_diagnostic)）

从称重传感器收集样本并报告健康状况和统计信息。首次连接称重传感器时运行此命令以验证接线和配置。

```
LOAD_CELL_DIAGNOSTIC
// Collecting load cell data for 10 seconds...
// Samples Collected: 3211
// Measured samples per second: 332.0
// Good samples: 3211, Saturated samples: 0, Unique values: 900
// Sample range: [4.01% to 4.02%]
// Sample range / sensor capacity: 0.00524%
```

检查输出：
- 每秒测量样本数应接近配置的 `sample_rate`。如果不是，请检查配置。对于 HX711，采样率由硬件设置。
- 饱和样本应为 0。非零表示超出传感器测量范围的过大作用力。
- 唯一值应占收集样本的很大比例。如果唯一值为 1，请验证接线。
- 在测试期间轻敲或推动传感器。如果传感器工作正常，样本范围应增加。

## 校准

### 校准称重传感器

`LOAD_CELL_CALIBRATE`（[文档](G-Codes.md#load_cell_calibrate)）

启动交互式校准实用程序。校准过程包括三个步骤：

1. `TARE` - 建立零力值并设置 `reference_tare_counts`
2. `CALIBRATE GRAMS=<value>` - 施加已知力并计算 `counts_per_gram`
3. `ACCEPT` - 将校准结果保存到配置

随时可以使用 `ABORT` 取消校准。

校准后运行 `LOAD_CELL_DIAGNOSTIC` 将显示以克为单位的附加信息。

#### 施加已知力

`CALIBRATE GRAMS=<value>` 步骤需要施加已知力。方法取决于称重传感器的位置：

**平台安装的称重传感器**（在打印平台或耗材支架下方）：
将已知质量的物体放在平台上。理想情况下使用称重传感器额定容量的很大比例（例如，对于 5 kg 称重传感器使用 5 kg）。

**工具头称重传感器**：
将数字秤放在打印平台上，轻轻降低工具头到秤上（如果打印平台移动则抬高打印平台）。使用至少 1 kg 的力。过大的力可能会损坏打印平台或工具头，因此请以小步骤移动。从数字秤读取读数并输入到 `CALIBRATE GRAMS=<value>` 命令中。

#### 理解校准结果

```
CALIBRATE GRAMS=555
// Calibration value: -2.78% (-559467), Counts/gram: 87.944082,
Total capacity: +/- 29.14Kg
```

`Calibration value:` 显示传感器范围的百分比用于校准。

`Counts/gram:` 是等于 1 克力的传感器计数。此数字越大，秤越精确。

`Total capacity` 是传感器可记录的最大力。`Total capacity` 应接近称重传感器的额定容量。如果大得多，请考虑更高的增益设置或更灵敏的称重传感器。这对于位宽低于 24 位的传感器更为重要。

## 操作

### 读取力数据

`LOAD_CELL_READ`

读取称重传感器上的当前力。

```
LOAD_CELL_READ
// 10.6g (1.94%)
```

力数据也可在 `load_cell` 打印机对象中获取：

```gcode
{% set grams = printer.load_cell.force_g %}
```

此值在最近 1 秒内取平均值，类似于温度传感器。

### 称重传感器去皮

`LOAD_CELL_TARE`

将当前读数设置为零力。用于测量相对重量变化，例如打印期间的耗材消耗。

```
LOAD_CELL_TARE
// Load cell tare value: 5.32% (445903)
```

皮重值可在 `load_cell` 打印机对象中获取：

```gcode
{% set tare_counts = printer.load_cell.tare_counts %}
```

## 称重传感器探针配置

此示例为已校准的称重传感器添加探针功能。`[load_cell_probe]` 部分包含所有 `[load_cell]` 参数、称重传感器探针特定参数和 [`[probe]`](Config_Reference.md#probe) 参数。

```ini
[load_cell_probe]
# 称重传感器设置
sensor_type: hx717 # 传感器特定配置
counts_per_gram: 245
reference_tare_counts: 12345
# 称重传感器探针设置
trigger_force: 75
force_safety_limit: 2000
drift_safety_limit: 1000
drift_filter_cutoff_frequency: 0.5
# 探针设置
z_offset: 0.0
```
- `sensor_type: hx717`
- `counts_per_gram: 245`\
  这些与基本称重传感器相同
- `reference_tare_counts: 12345`\
  _默认值：None_\
  原始传感器计数的基线皮重值，由 `LOAD_CELL_CALIBRATE` 设置。用作 `force_safety_limit` 的零值以定义安全工作范围。

- `trigger_force: 75`\
  _默认值：75（75 克）_\
  探针期间触发限位开关的力（以克为单位），相对于探针开始时的皮重值测量。预期有超调；更高的探针速度或更低的采样率会增加峰值力。有关多 MCU 时序考虑，请参阅 [多 MCU 归位](Multi_MCU_Homing.md)。75g 默认值是保守的。更高的值（最高 200g）可以在处理渗出的耗材时提高性能。

- `force_safety_limit: 2000`\
  _默认值：2000（+/-2Kg）_\
  为了安全地开始探测移动，探针上的力必须低于此限制。这将 `reference_tare_counts` 视为其零值。可以通过将值设置为 0 来禁用此检查。如果超出，探针将停止并显示错误 `!! Load Cell Probe Error: force of 3000g exceeds force_safety_limit (2000g) before probing!`。此值需要足够大以允许：
  - 在整个打印体积和探测移动长度中变化的鲍登管和拖链力
  - 在整个探测温度范围内的温度漂移

- `drift_safety_limit: 1000`\
  _默认值：1000（+/-1Kg）_\
  这是探针在探测移动中允许的最大力，超过此值将触发错误。设置为 0 以禁用此安全检查。如果超出，探针将停止并显示错误 `!! Load Cell Probe Error: force exceeded drift_safety_limit before triggering!`。当使用 `drift_filter_cutoff_frequency` 时，此安全措施很重要，因为过高的截止频率可能会使探针触发失效。

- `drift_filter_cutoff_frequency: 0.5`\
  _默认值：None（禁用）_\
  连续皮重漂移滤波器的截止频率（以 Hz 为单位）。在 MCU 上启用滤波器以跟踪来自鲍登管和拖链的漂移。需要 [SciPy](#installing-scipy)。将此值设置得过高可能会延迟探针触发并增加工具头上的力。

- `z_offset: 0.0`\
  _必需_\
  探针触发时打印平台与喷嘴之间的距离（以 mm 为单位）。对于称重传感器探针，此值为 0。

有关所有可用选项，请参阅 [配置参考](Config_Reference.md#load_cell_probe)。

### 安全性

称重传感器是直接喷嘴接触探针。系统包含安全检查以防止工具头上承受过大的力。选择不当的配置值可能会使这些保护失效。

**校准检查：**
在归位或探测之前，称重传感器探针会检查其是否已校准。如果没有，打印机将停止并显示错误 `!! Load Cell Probe Error: Load Cell not calibrated`。

**准确的 `counts_per_gram`：**
此设置将原始计数转换为克。所有安全限制均以克为单位。不准确的值会导致工具头上承受过大的力。永远不要猜测此值 - 始终使用 `LOAD_CELL_CALIBRATE`。

**保守的 `trigger_force`：**
探测始终在停止前超过 `trigger_force`。设置为 100 g 可能导致 350 g 峰值力。超调随更快的探测速度、低采样率或多 MCU 配置而增加。

**`force_safety_limit` 保护：**
此设置在开始归位或探测之前检测探针上的过大作用力。如果超出限制，探针将停止并显示错误，例如 `!! Load Cell Probe Error: force of 3000g exceeds force_safety_limit (2000g) before probing!`。这可能是由于：
- 探针在探测开始前与打印平台碰撞，例如通过水平移动进入倾斜的打印平台
- 鲍登管或拖链的过大力量
- 挤出机推动耗材导致应变片上的过大力量
- 应变片损坏，导致零点偏离 `reference_tare_counts` 值太远

**`drift_safety_limit` 保护：**
这设置了探针触发前允许的最大力。如果测量的力变化超过限制，探针将停止并显示错误：`!! Load Cell Probe Error: force exceeded drift_safety_limit before triggering!`。这可能由于多种原因触发：
- 探针在探测期间被主动加热，导致皮重值漂移
- `drift_filter_cutoff_frequency` 设置过高，导致点击事件被过滤掉
- 探测期间鲍登管/拖链力发生较大变化

**看门狗任务：**
在归位期间，看门狗监控传感器数据。如果传感器在 2 个采样周期内未能发送测量值，MCU 将关闭并显示错误 `!! Load Cell Probe Error: timed out waiting for sensor data`。这通常表示 ADC 故障或接地不足。确保机架、电源和打印床接地。可能需要多个接地连接。在接地连接点打磨阳极氧化铝以获得良好的电气接触。

**点击验证和重试：**
探针验证每次点击的形状、断开接触时序和运动时序。无效的点击将被拒绝（`is_valid=False`），并根据探针配置的 `bad_probe_strategy` 和 `bad_probe_retries` 进行重试。这可以防止接受污染或质量差的点击。有关验证失败类型，请参阅 [点击验证错误代码](#tap-validation-error-codes)。请注意，验证可以捕获许多但并非所有不良点击，正确的喷嘴温度和清洁度仍然至关重要。

### 测试探针操作

`LOAD_CELL_TEST_TAP [COUNT=<taps>] [TIMEOUT=<seconds>]`\
_默认 COUNT：3_\
_默认 TIMEOUT：30_

在不移动轴的情况下测试探针操作。在结束前检测指定数量的点击。如果在超时时间内未检测到点击，命令将失败。该命令验证点击质量并将验证错误记录到控制台。

**注意：** 称重传感器探针不支持 `QUERY_ENDSTOPS` 或 `QUERY_PROBE`，它们始终返回未触发状态。在探测前使用 `LOAD_CELL_TEST_TAP` 验证功能。

### 归位配置

称重传感器探针支持 Z 轴归位。归位不如使用 `PROBE` 命令进行探测准确。归位后，使用 `PROBE` 进行高精度 Z 归位：

```gcode
PROBE HOME=Z
```

### 探测温度

在归位和探测期间保持喷嘴温度低于耗材渗出点。140°C 是所有耗材类型的良好起点。

耗材渗出是探测误差的主要来源。Kalico 验证点击质量并拒绝许多不良点击（例如，由于渗出）。防止渗出并保持喷嘴清洁仍然是最佳实践。不建议在打印温度下进行探测。观察控制台中的点击验证错误（例如，`TAP_SHAPE_INVALID`、`TAP_BREAK_CONTACT_TOO_LATE`），这些错误表明点击质量差。

### 喷嘴保护

请参阅 [Voron Tap 的 activate_gcode](https://github.com/VoronDesign/Voron-Tap/blob/main/config/tap_klipper_instructions.md) 以保护打印表面免受热喷嘴的影响。

### 喷嘴清洁

在探测前清洁喷嘴。建议的顺序：
1. 将喷嘴加热到探测温度（例如，`M109 S140`）
2. 归位机器（`G28`）
3. 擦拭喷嘴
4. 打印平台热浸
5. 执行探测任务（QGL、床面网格等）

### 喷嘴温度补偿

由于渗出，无法在打印温度下进行探测。探测后加热喷嘴，导致其膨胀。喷嘴在其长度方向上膨胀最多，朝向打印平台。这应该通过 [z_thermal_adjust](Config_Reference.md#z_thermal_adjust) 进行补偿。

在两个温度下测量 `PROBE_ACCURACY`（例如 180°C 和 290°C）并计算：

```
temp_coeff = (z_average_hot - z_average_cold) / (temp_hot - temp_cold)
```

示例：`temp_coeff = -0.05 / (290 - 180) = -0.00045455`

预期为负值（`z_thermal_adjust` 将使用负值将喷嘴移离打印平台，使用正值移向打印平台）。

示例配置：

```ini
[z_thermal_adjust nozzle]
temp_coeff: -0.00045455
sensor_type: temperature_combined
sensor_list: extruder
combination_method: max
min_temp: 0
max_temp: 400
max_z_adjustment: 0.1
```

### 床面网格设置

**禁用 `relative_reference_index`**
因为称重传感器探针给出的 z 值是绝对值，不相对于任何东西，所以不需要 `relative_reference_index`。只需删除 `[bed_mesh]` 中的设置。从配置中删除该行即可将其关闭。

**启用激进移动分割**
```ini
move_check_distance: 3.0
split_delta_z: 0.01
```
设置网格以尽可能频繁地调整 z 高度。这两个设置更改床面网格如何评估 z 变化。最小化 `split_delta_z` 以获得高分辨率网格跟随（0.01 是 10 微米，是探针分辨率的 10 倍）。为 `move_check_distance` 选择小值会强制 bed_mesh 更频繁地重新评估 z 高度。如果这些设置保持默认值，您可能会在第一层中看到由不频繁调整引起的条纹。

**启用 `horizontal_z_clearance`**
```ini
horizontal_z_clearance: 0.4
```
使用 `horizontal_z_clearance`，探针在网格点之间始终缩回该距离。这可以大大减少 z 行程距离，同时适应打印平台形状。更少的行程距离可以加快探测速度。

**在网格化前使用 NOZZLE_CLEANUP**
```
NOZZLE_CLEANUP
```
这会轻敲喷嘴直到它报告连续 3 次成功探测，证明喷嘴是干净的。这在网格化之前清除喷嘴上的任何渗出，以获得最佳网格质量。这应该在打印区域外执行。请参阅 [NOZZLE_CLEANUP](G-Codes.md#nozzle_cleanup)

**使用 CIRCLE 策略进行网格化**
```
BED_MESH STRATEGY=CIRCLE
```
circle 策略是 `[probe]` 的一个功能。当称重传感器探针检测到污染的探针时，它将移动到圆圈图案中的相邻位置。对于床面网格，这种轻微的位置偏移远不如使用污染的探针重要。重新探测到污染的位置不太可能成功，并可能导致网格化操作失败。

## 高级配置

### 连续皮重滤波

称重传感器探针支持 MCU 上的滤波器，以补偿来自外部力量（如鲍登管和脐带电缆）的漂移。如果探针在接触打印平台之前触发，这可能是原因。这有时称为*连续去皮*，用于在探测期间承受可变外部力的工具头安装传感器。

#### 安装 SciPy

滤波器默认关闭。需要 [SciPy](https://scipy.org/) 库来从配置值计算滤波器系数。它需要安装在 klipper 虚拟环境中。通常：

```bash
~/klippy-env/bin/pip install scipy
```

预编译版本适用于 32 位 Raspberry Pi 系统上的 Python 3。

#### 滤波器调优

`drift_filter_cutoff_frequency` 参数应根据正常运行期间观察到的漂移来选择。

基本调优指南：
- 从 `drift_filter_cutoff_frequency: 0.5` Hz 开始
- Prusa 使用 0.8 Hz（MK4）和 11.2 Hz（XL）；此范围对于实验是合理的
- 仅增加直到消除鲍登管漂移
- 设置过高会导致触发缓慢和过大的力
- 保持 `trigger_force` 较低（默认 75 g）；漂移滤波器将内部读数保持在零附近
- 调优期间保持 `force_safety_limit` 保守（默认 2 kg）
- 调优期间保持 `drift_safety_limit` 保守（默认 1 kg）
- **注意：** 过度激进的 `drift_filter_cutoff_frequency` 可能会扭曲点击形状和时序，导致验证失败（例如，`TAP_BREAK_CONTACT_TOO_LATE`）。如果出现此类错误，请降低截止频率或探测速度。

其他滤波器参数的调优超出了本文档的范围。
在 [scripts/filter_workbench.ipynb](../scripts/filter_workbench.ipynb) 中提供了一个 Jupyter 笔记本，其中包含详细分析的示例。

### 点击验证

**点击探测简介**

称重传感器探针的工作方式与其他探针不同，它在构建表面上"点击"。探针与构建表面接触后，会向远离构建表面的方向做一个小移动，称为回拉移动。这种向下/向上运动的组合称为"点击"。分析完整的点击序列，并从原始力数据构建表示。此表示是一系列由线连接的点。这是一个典型点击的图表，清楚地标记了运动阶段：

##### 图 1：点击阶段
![显示探针、停留和回拉阶段的有效点击](/img/load-cell/tap-phases.png)

*图 1 - 有效点击阶段。图表显示测量力（黑线）随时间的变化，并带有拟合验证线（红色）。三个阶段用颜色编码：探针（蓝色）力随喷嘴接触打印平台而上升，停留（绿色）力在触发后稳定，回拉（红色）力随着回拉移动抬起喷嘴而恢复到基线。垂直线标记阶段边界：蓝色（探针结束/停留开始）、绿色（停留结束/回拉开始）、红色（回拉结束）。理想的点击显示在探测期间急剧上升，在停留期间力稳定，在回拉期间干净地返回基线。*

图表中的每条线都有一个名称：

##### 图 2：点击段
![在真实力数据上标记的点击段](/img/load-cell/tap-segments.png)

*图 1a - 点击图显示命名的点击线：接近（接触前的平坦基线）、压缩（力增大时的陡峭上升）、停留（探针稳定时的稳定高力）、**减压**（回拉期间的力下降）和离开（回拉完成时返回基线）。垂直彩色线标记阶段之间的边界。*

减压线和离开线的交点由探针报告为 Z=0 点。这是图表上最关键的点。

回拉移动非常小（约 0.2mm）且非常缓慢。由于其缓慢的速度，减压线的斜率比压缩线更浅。这提高了探针的准确性，因为力随时间的变化更小，意味着探针的 z 分辨率提高。本质上，回拉移动是在一个点上对打印平台的高分辨率力扫描。回拉移动由配置中的 `pullback_speed` 和 `pullback_dist` 选项控制。默认设置以每微米 1 个 ADC 采样进行扫描，使探针具有 1 微米的预期分辨率。

根据图表的形状，可以判断探针是否良好。探针对点的顺序和线形成的形状执行一些基本检查。如果它不是"点击"形状，探针将被报告为不良。有关验证失败的详细信息，请参阅 [点击验证错误代码](#tap-validation-error-codes)。

#### 点击验证错误代码

当检测到低质量点击时，会记录特定的错误代码。其中大多数错误可能是喷嘴污染的症状，但有些可能表明配置或设置问题：

| 错误代码 | 描述 | 常见原因 |
|----------|------|----------|
| `TAP_CHRONOLOGY` | 点击图表上的 4 个点在时间上顺序错误 | 污染：数据失真太大，看起来不像点击 |
| `TAP_SHAPE_INVALID` | 点击形状的某个段没有按预期方向移动 | 污染：数据失真太大，看起来不像点击 |
| `TAP_BREAK_CONTACT_TOO_EARLY` | 在回拉移动中过早检测到断开接触 | `pullback_distance` 太长。 |
| `TAP_BREAK_CONTACT_TOO_LATE` | 在回拉移动中过晚检测到断开接触 | `pullback_distance` 太短。 |
| `TAP_PULLBACK_TOO_SHORT` | 回拉移动期间喷嘴从未与打印平台断开接触 | `pullback_distance` 太短。 |
| `COASTING_MOVE_ACCELERATION` | 探测移动在探针触发前开始减速 | Z 未配置负 `min_position` 以允许探针移动到 z=0 以下。例如：`position_min: -5`。 |
| `TOO_FEW_PROBING_MOVES` | 梯形移动少于预期 | 这不常见 |
| `TOO_MANY_PROBING_MOVES` | 梯形移动多于预期 | 这不常见 |

#### 点击质量

除了基本的点击形状检查外，一个称为**点击质量分类器**的模块为每次点击给出 0 到 100 的质量分数。分类器的主要目标是区分可用于清洁的点击和无法使用的渗出点击。

分类器使用比率指标，使其更易于在不同打印机之间传输。它使用压缩线中的总力比率，因为这是点击中的最佳参考指标。这允许其他量随压缩力而缩放。而绝对指标（角度、力）对于单个物理工具头设计和探测配置效果良好，但当这些改变时就会失效。

##### 点击质量组件

| 组件 | 描述 | 原因？ |
|------|------|--------|
| 接近力 | 接近线中的力变化与压缩力的比率。预期接近 0。 | 接近线中的大力与在接触打印平台之前撞击熔融塑料有关 |
| 离开力 | 离开线中的力变化与压缩力的比率。预期接近 0。 | 在此移动期间喷嘴应在自由空气中，因此任何变形通常是由渗出拉动喷嘴引起的。 |
| 基线力 | 喷嘴接触打印平台与断开接触的点之间的力差，与压缩力的比率。预期接近 0。 | 您期望秤在取下重量时读数为零。较大的差异意味着施加了意外的力。 |
| 停留力下降 | 停留期间力的下降与压缩力的比率。 | 虽然一些下降并不罕见，但大下降与塑料从喷嘴和打印平台之间渗出有关。 |
| 归一化减压角度 | 减压线的斜率与理想减压斜率的匹配程度。归一化为 `(actual - expected) / expected` | 渗出会拉动喷嘴，改变斜率。这会破坏测量的准确性。 |

这些因素结合在一起给出最终的质量分数。唯一需要在打印机上测量的组件是**归一化减压角度**。

每个组件都有一个最大阈值。如果组件超过阈值，点击质量分数将降至 0%。每个值是压缩力的百分比：

| 组件 | 阈值 | 配置参数 |
|------|------|----------|
| 接近力 | 50% | max_approach_force=50 |
| 离开力 | 25% | max_departure_force=25 |
| 基线力 | 25% | max_baseline_force_delta=25 |
| 停留力下降 | 75% | max_dwell_force_drop=75 |

#### 点击质量错误代码
如果默认点击质量分类器处于活动状态，它可能会报告其他错误代码：

| 错误代码 | 描述 | 常见原因 |
|----------|------|----------|
| `LOW_COMPRESSION_FORCE` | 计算的压缩力小于 `trigger_force` | 污染：喷嘴上的热塑料导致力上升非常缓慢。探测非常柔软的东西。 |
| `LOW_TAP_QUALITY` | 点击质量低于 `min_tap_quality` 设置 | 污染：点击特征可识别但失真。配置的 `min_tap_quality` 太低。 |

所有验证错误都会被记录以供故障排除。


## 开发者说明

本节涵盖了开发具有称重传感器探针支持的工具头板卡的指导。

### 点击分析和验证

称重传感器探针在每次探测尝试时执行完整的点击分析。分析样本以识别点击点并构建代表接近、压缩、停留、减压和离开阶段的线。使用详尽的肘部查找算法识别点，并使用线性回归构建线。然后计算这些线的交点，得到一组点。

请参阅 [图 2](#figure-2-低减压力) 和 [图 3](#figure-3-严重污染)

接下来执行一组基本的健全性检查：

1. **运动时序**：检查点以确保它们按时间顺序排列。由于它们基于力数据、线性回归和交点，因此它们可能顺序错乱。

2. **形状验证**：检查点以确保它们形成"点击"形状的图表。这可以是正梯形或负梯形形状。

3. **断开接触时序**：探针验证断开接触时间发生在回拉移动的中间三分之二内。太早或太晚会使分析不太可靠。

如果这些检查中的任何一个失败，探针将被标记为不良。如果全部通过，将调用配置的 `TapClassifierModule` 来进一步决定点击是好还是坏。内置分类器称为 `TapQualityClassifier`，通过校准 `decompression_angle` 启用。

**自定义点击分类器**：可以通过 `tap_classifier_module` 配置值完全替换内置的 `TapQualityClassifier`。分类器接收 `TapAnalysis` 对象，可以执行额外的验证或修改点击位置计算。使用适当的数据集，可以使用机器学习技术（例如 [决策树](https://scikit-learn.org/stable/modules/tree.html)）构建更准确的点击分类器，针对特定打印机的硬件进行定制。

#### 失败点击的可视化示例

要快速诊断，请将您的点击跟踪与 [图 1](#figure-1-点击阶段)（有效点击）和下面的失败示例进行比较。将模式与上表中的错误代码匹配。

##### 图 2：低减压力
![低减压力失败](/img/load-cell/bad-tap-low-decompression-force.png)

*图 2 - 低减压力（`LOW_DECOMPRESSION_FORCE`）。构建板未与加热床牢固接触（塑料碎片在板上），导致停留阶段力显著下降。减压力与触发力相比太低。*

##### 图 3：严重污染
![严重塑料污染](/img/load-cell/bad-tap-major-plastic-fouling.png)

*图 3 - 严重塑料污染。喷嘴上的软塑料导致峰值力大幅下降，并在停留期间力持续衰减，因为塑料从喷嘴和打印平台之间渗出。这可能导致 `LOW_DECOMPRESSION_FORCE` 错误。*

##### 图 4：回拉粘附
![回拉期间的轻微塑料粘附](/img/load-cell/bad-tap-minor-plastic-adhesion.png)

*图 4 - 轻微塑料粘附。喷嘴孔内的渗出塑料在回拉阶段导致一个小的力下降（圈出）。塑料在从构建板上抬起时将喷嘴向下拉。此点击通过了验证，因为异常很小，但表明喷嘴温度可能过高或塑料正在渗出。*

##### 图 5：基线不一致
![基线力不一致失败](/img/load-cell/bad-tap-baseline-force-inconsistent.png)

*图 5 - 基线力不一致（`BASELINE_FORCE_INCONSISTENT`）。喷嘴上的塑料导致"缓慢碰撞"，表现为接近线中的正斜率。压缩角度远小于 90 度，并且接近和离开之间的基线力差异显著。*

### ADC 传感器选择

推荐的传感器特性：
- 至少 24 位分辨率
- SPI 通信
- 数据就绪（`DRDY`）引脚，用于无需 SPI 查询的样本就绪指示
- 带有 128× 增益的可编程增益放大器，以消除外部放大器
- SPI 复位指示以检测传感器重启，这是电气问题的常见指示
- 可选采样率在 350 Hz 和 2 kHz 之间（低于 250 Hz 的速率需要较慢的探测速度并增加工具头力）
- 对于具有多个称重传感器的打印平台下应用，使用具有所有通道同时采样的 ADC，例如 [ADS131M04](Config_Reference.md#ads131m04)。多路复用 ADC 在通道切换后有稳定延迟，并且读数存在时间展宽问题，这会降低准确性。

Klipper 的 `bulk_sensor` 和 `load_cell_probe` 基础设施简化了对新传感器的支持。传感器可以从 Python 配置，采样循环用 C 编写。

### 电源滤波

使用比 ADC 制造商规范建议的更大的电容器。ADC 数据手册假设低噪声电池供电环境。3D 打印机产生显著的 5V 总线噪声。在最终确定电容器值之前，使用典型电源和有源步进驱动器测试传感器。

ADC 芯片和称重传感器应由 LDO 供电。开关降压转换器不适合此应用。

### 接地

ADC 芯片容易受到噪声和 ESD 的影响。在芯片下方的第一层板上使用大型接地平面。将芯片远离电源部分和 DC-DC 转换器。确保正确接地到直流电源。

### HX711 和 HX717 说明

这些传感器很受欢迎，但有局限性：
- 位操作通信具有较高的 MCU 开销；SPI 传感器更高效
- 无法向 MCU 传达复位事件，隐藏电气故障
- HX717（320 Hz）强烈优于 HX711（80 Hz）用于探测；将 HX711 探测速度限制在 2 mm/s
- HX711 采样率是硬件配置的，不是软件可配置的；10 SPS 版本必须重新接线才能达到 80 SPS
