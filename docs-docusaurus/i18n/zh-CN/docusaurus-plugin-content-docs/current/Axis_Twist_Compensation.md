# 轴扭曲补偿

本文档介绍 `[axis_twist_compensation]` 模块。

某些打印机的 X 轨道可能存在轻微扭曲，这可能会使安装在 X 托架上的探针结果产生偏差。
这在 Prusa MK3、Sovol SV06 等设计的打印机中很常见，在[探针位置偏差](Probe_Calibrate.md#location-bias-check)中有进一步描述。它可能导致[床面网格](Bed_Mesh.md)、[螺钉倾斜调整](G-Codes.md#screws_tilt_adjust)、[Z 倾斜调整](G-Codes.md#z_tilt_adjust)等探测操作返回不准确的床面表示。

此模块使用用户的手动测量来校正探针的结果。请注意，如果你的轴有明显的扭曲，强烈建议先使用机械方法修复，然后再应用软件校正，因为校准可能会受到探针精度、床面平整度、Z 轴对齐等问题的影响。

**警告：** 此模块目前尚不兼容可拆卸探针，如果你使用它，它将尝试在不连接探针的情况下探测床面。

## 补偿使用概述

> **提示：** 确保[探针 X 和 Y 偏移量](Config_Reference.md#probe)设置正确，因为它们会极大地影响校准。

### 基本用法：X 轴校准
1. 设置 `[axis_twist_compensation]` 模块后，运行：
```
AXIS_TWIST_COMPENSATION_CALIBRATE
```
此命令默认校准 X 轴。
   - 校准向导将提示你在床面上的多个点测量探针 Z 偏移量。
   - 默认情况下，校准使用 3 个点，但你可以使用以下选项指定不同的数量：
``
SAMPLE_COUNT=<value>
``

2. **调整 Z 偏移量：**
完成校准后，请务必[调整 Z 偏移量](Probe_Calibrate.md#calibrating-probe-z-offset)。

3. **执行床面调平操作：**
根据需要使用基于探针的操作，例如：
   - [螺钉倾斜调整](G-Codes.md#screws_tilt_adjust)
   - [Z 倾斜调整](G-Codes.md#z_tilt_adjust)

4. **完成设置：**
   - 归零所有轴，必要时执行[床面网格](Bed_Mesh.md)。
   - 运行测试打印，然后根据需要进行微调。

### Y 轴校准
Y 轴的校准过程与 X 轴类似。要校准 Y 轴，请使用：
```
AXIS_TWIST_COMPENSATION_CALIBRATE AXIS=Y
```
这将引导你完成与 X 轴相同的测量过程。

> **提示：** 床面温度、喷嘴温度和尺寸似乎对校准过程没有影响。

## [axis_twist_compensation] 设置和命令

`[axis_twist_compensation]` 的配置选项可以在[配置参考](Config_Reference.md#axis_twist_compensation)中找到。

`[axis_twist_compensation]` 的命令可以在 [G-Codes 参考](G-Codes.md#axis_twist_compensation)中找到。
