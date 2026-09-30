# 从指定高度打印

## 概述

允许从指定Z高度恢复打印，而非从头开始。系统解析G-code文件找到目标Z高度，提取该位置的打印机状态（温度、风扇速度、挤出模式），并以正确的前置命令从此处恢复打印。

## 工作原理

1. Mainsail/Fluidd UI向 `virtual_sdcard/from_height_print` 发送POST请求，包含 `filename` 和 `height` 参数。
2. 后台线程解析G-code文件找到目标Z高度。
3. 解析器识别切片软件类型（Cura、OrcaSlicer、Simplify3D）并提取：
   - 最后挤出机温度
   - 最后热床温度
   - 最后风扇速度
   - 绝对/相对挤出模式
   - 绝对/相对位置模式
   - 目标Z高度处的文件字节位置
4. 在主打印循环前注入前置脚本（M109、M190、M106、M82/M83、G90/G91）。
5. 文件定位到提取的位置，继续打印。

## Webhook 接口

**端点：** `POST /printerwebhook/virtual_sdcard/from_height_print`

| 参数 | 类型 | 说明 |
|-----------|------|-------------|
| `filename` | string | G-code文件路径（相对于sdcard_dirname） |
| `height` | float | 要恢复的Z高度 |

**示例：**
```json
{
    "filename": "my_print.gcode",
    "height": 10.5
}
```

## 支持的切片软件

| 切片软件 | Z高度检测 |
|--------|-------------------|
| Cura | 通过G0/G1 Z命令检测 |
| OrcaSlicer | 通过 `;LAYER_CHANGE` 注释检测 |
| Simplify3D | 通过 `; layer` 注释检测 |

## 状态机

从高度打印功能使用一个3状态状态机（`_parse_state`）：

| 状态 | 说明 |
|-------|------|
| 0 | 空闲 |
| 1 | 解析进行中 |
| 2 | 解析失败 |
| 3 | 解析完成，准备打印 |

`work_handler`在解析过程中每0.1秒轮询 `_parse_state`。成功时（状态3），以注入的前置脚本进入正常打印循环。

## 外部解析器

线程解析器（`_thread_parse_gcode`）通过子进程使用外部 `parse_gcode` 二进制文件。如果此二进制文件不可用，可以使用进程内解析器（`_parse_gcode`）作为后备。进程内解析器效率较低但无外部依赖。

## 状态变量

通过 `printer["virtual_sdcard"]` 访问：

| 变量 | 类型 | 说明 |
|----------|------|------|
| `is_from_height` | bool | 是否正在进行从高度打印 |

## 安全注意事项

- 打印机在恢复前会执行归位。确保热床畅通。
- 前置脚本恢复目标Z高度处存在的打印机状态。
- 如果未找到目标Z高度（如不支持的切片软件），解析将失败，打印将被取消。
- 解析期间取消打印将正确清理解析器线程。