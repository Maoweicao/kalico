# From-Height Print / 从指定高度打印

## Overview / 概述

Allows resuming a print from a specific Z height instead of the beginning. The system parses the G-code file to find the target Z height, extracts the printer state (temperatures, fan speed, extrusion mode) at that point, and resumes printing from there with the correct preamble commands.

允许从指定Z高度恢复打印，而非从头开始。系统解析G-code文件找到目标Z高度，提取该位置的打印机状态（温度、风扇速度、挤出模式），并以正确的前置命令从此处恢复打印。

## How It Works / 工作原理

1. The Mainsail/Fluidd UI sends a POST request to `virtual_sdcard/from_height_print` with `filename` and `height` parameters.
2. A background thread parses the G-code file to find the target Z height.
3. The parser identifies the slicer type (CURA, OrcaSlicer, Simplify3D) and extracts:
   - Last extruder temperature
   - Last bed temperature
   - Last fan speed
   - Absolute/relative extrusion mode
   - Absolute/relative position mode
   - File byte position at the target Z height
4. Preamble scripts (M109, M190, M106, M82/M83, G90/G91) are injected before the main print loop.
5. The file seeks to the extracted position and printing continues.

1. Mainsail/Fluidd UI向 `virtual_sdcard/from_height_print` 发送POST请求，包含 `filename` 和 `height` 参数。
2. 后台线程解析G-code文件找到目标Z高度。
3. 解析器识别切片软件类型（CURA、OrcaSlicer、Simplify3D）并提取：
   - 最后挤出机温度
   - 最后热床温度
   - 最后风扇速度
   - 绝对/相对挤出模式
   - 绝对/相对位置模式
   - 目标Z高度处的文件字节位置
4. 在主打印循环前注入前置脚本（M109、M190、M106、M82/M83、G90/G91）。
5. 文件定位到提取的位置，继续打印。

## Webhook API / Webhook 接口

**Endpoint / 端点:** `POST /printerwebhook/virtual_sdcard/from_height_print`

| Parameter | Type | Description | 说明 |
|-----------|------|-------------|------|
| `filename` | string | G-code file path (relative to sdcard_dirname) | G-code文件路径（相对于sdcard_dirname） |
| `height` | float | Target Z height to resume from | 要恢复的Z高度 |

**Example / 示例:**
```json
{
    "filename": "my_print.gcode",
    "height": 10.5
}
```

## Supported Slicers / 支持的切片软件

| Slicer | Z-Height Detection | 说明 |
|--------|-------------------|------|
| CURA | G0/G1 Z commands | 通过G0/G1 Z命令检测 |
| OrcaSlicer | `;LAYER_CHANGE` comments | 通过 `;LAYER_CHANGE` 注释检测 |
| Simplify3D | `; layer` comments with `=` | 通过 `; layer` 注释检测 |

## State Machine / 状态机

The from-height feature uses a 3-state machine (`_parse_state`):

| State | Meaning | 说明 |
|-------|---------|------|
| 0 | Idle | 空闲 |
| 1 | Parsing in progress | 解析进行中 |
| 2 | Parse failed | 解析失败 |
| 3 | Parse complete, ready to print | 解析完成，准备打印 |

The `work_handler` polls `_parse_state` every 0.1s while parsing. On success (state 3), it falls through to the normal print loop with the injected preamble scripts.

`work_handler`在解析过程中每0.1秒轮询 `_parse_state`。成功时（状态3），以注入的前置脚本进入正常打印循环。

## External Parser / 外部解析器

The threaded parser (`_thread_parse_gcode`) uses an external `parse_gcode` binary via subprocess. If this binary is not available, the in-process parser (`_parse_gcode`) can be used as a fallback. The in-process parser is less efficient but has no external dependencies.

线程解析器（`_thread_parse_gcode`）通过子进程使用外部 `parse_gcode` 二进制文件。如果此二进制文件不可用，可以使用进程内解析器（`_parse_gcode`）作为后备。进程内解析器效率较低但无外部依赖。

## Status Variables / 状态变量

Access via `printer["virtual_sdcard"]`:

| Variable | Type | Description | 说明 |
|----------|------|-------------|------|
| `is_from_height` | bool | Whether from-height print is active | 是否正在进行从高度打印 |

## Safety Notes / 安全注意事项

- The printer will execute homing before resuming. Ensure the bed is clear.
- The preamble scripts restore the printer state that existed at the target Z height.
- If the target Z height is not found (e.g., slicer not supported), the parse will fail and the print will be cancelled.
- Canceling the print during parsing will properly clean up the parser thread.

- 打印机在恢复前会执行归位。确保热床畅通。
- 前置脚本恢复目标Z高度处存在的打印机状态。
- 如果未找到目标Z高度（如不支持的切片软件），解析将失败，打印将被取消。
- 解析期间取消打印将正确清理解析器线程。
