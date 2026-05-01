# 轴扭转补偿

本文档描述了 `[axis_twist_compensation]` 模块。

某些打印机的 X 导轨可能存在轻微扭转，这会导致安装在 X 滑架上的探针结果产生偏差。
这在 Prusa MK3、Sovol SV06 等设计的打印机中很常见，并在[探针位置偏差](Probe_Calibrate.md#location-bias-check)中进一步描述。这可能导致探针操作（如[热床网格](Bed_Mesh.md)、[螺丝倾斜调整](G-Codes.md#screws_tilt_adjust)、[Z 轴倾斜调整](G-Codes.md#z_tilt_adjust)等）返回不准确的热床表示。

此模块使用用户的手动测量来校正探针的结果。
请注意，如果您的轴严重扭转，强烈建议在应用软件校正之前首先使用机械方法修复它，
因为校准可能受探针精度、热床平整度、Z 轴对齐等问题的影响。

**警告**：此模块尚不兼容可停靠探针，如果使用它，将在未连接探针的情况下尝试探测热床。

## 补偿使用概述

> **提示：** 确保[探针 X 和 Y 偏移](Config_Reference.md#probe)设置正确，因为它们极大地影响校准。

### 基本用法：X 轴校准
1. 设置好 `[axis_twist_compensation]` 模块后，运行：
```
AXIS_TWIST_COMPENSATION_CALIBRATE
```
此命令默认校准 X 轴。
  - 校准向导将提示您沿热床在多个点测量探针 Z 偏移。
  - 默认情况下，校准使用 3 个点，但您可以使用以下选项指定不同的数量：
``
SAMPLE_COUNT=<value>
``

2. **调整您的 Z 偏移：**
完成校准后，请务必[调整您的 Z 偏移](Probe_Calibrate.md#calibrating-probe-z-offset)。

3. **执行热床调平操作：**
根据需要执行基于探针的操作，例如：
  - [螺丝倾斜调整](G-Codes.md#screws_tilt_adjust)
  - [Z 轴倾斜调整](G-Codes.md#z_tilt_adjust)

4. **完成设置：**
  - 所有轴归位，并在必要时执行[热床网格](Bed_Mesh.md)。
  - 进行测试打印，然后根据需要微调。

### Y 轴校准
Y 轴的校准过程与 X 轴类似。要校准 Y 轴，请使用：
```
AXIS_TWIST_COMPENSATION_CALIBRATE AXIS=Y
```
这将引导您完成与 X 轴相同的测量过程。

> **提示：** 热床温度、喷嘴温度和尺寸似乎对校准过程没有影响。

## [axis_twist_compensation] 设置和命令

`[axis_twist_compensation]` 的配置选项可在[配置参考](Config_Reference.md#axis_twist_compensation)中找到。

`[axis_twist_compensation]` 的命令可在 [G-Code 参考](G-Codes.md#axis_twist_compensation)中找到。
