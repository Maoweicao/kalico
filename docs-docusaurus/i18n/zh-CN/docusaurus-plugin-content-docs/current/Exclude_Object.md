# 排除对象

`[exclude_object]` 模块允许 Kalico 在打印过程中排除对象。要启用此功能，请包含 [exclude_object 配置节](Config_Reference.md#exclude_object)（另请参阅[命令参考](G-Codes.md#exclude_object)和 [sample-macros.cfg](../config/sample-macros.cfg) 文件，其中包含与 Marlin/RepRapFirmware 兼容的 M486 G-Code 宏。）

与其他 3D 打印机固件选项不同，运行 Kalico 的打印机利用了一套组件，用户有许多选择。因此，为了提供一致的用户体验，`[exclude_object]` 模块将建立某种契约或 API。该契约涵盖 gcode 文件的内容、模块内部状态的控制方式以及该状态如何提供给客户端。

## 工作流概述
打印文件的典型工作流可能如下所示：
1. 切片完成，文件被上传进行打印。在上传过程中，文件被处理并添加 `[exclude_object]` 标记。或者，切片软件可以配置为原生准备对象排除标记，或在其自己的预处理步骤中准备。
2. 打印开始时，Kalico 将重置 `[exclude_object]` [状态](Status_Reference.md#exclude_object)。
3. 当 Kalico 处理 `EXCLUDE_OBJECT_DEFINE` 块时，它将使用已知对象更新状态并将其传递给客户端。
4. 客户端可以使用该信息向用户呈现 UI，以便跟踪进度。Kalico 将更新状态以包含当前正在打印的对象，客户端可以将其用于显示目的。
5. 如果用户请求取消某个对象，客户端将向 Kalico 发出 `EXCLUDE_OBJECT NAME=<name>` 命令。
6. 当 Kalico 处理该命令时，它会将该对象添加到排除对象列表中并更新客户端状态。
7. 客户端将从 Kalico 接收更新后的状态，并可以使用该信息在 UI 中反映对象的状态。
8. 打印完成后，`[exclude_object]` 状态将保持可用，直到另一个操作重置它。

## GCode 文件
支持对象排除所需的专业 gcode 处理不符合 Kalico 的核心设计目标。因此，此模块要求在将文件发送给 Kalico 打印之前对其进行处理。使用切片软件中的后处理脚本或在上传时让中间件处理文件是为 Kalico 准备文件的两种可能性。参考后处理脚本可作为可执行文件和 Python 库使用，请参阅 [cancelobject-preprocessor](https://github.com/kageurufu/cancelobject-preprocessor)。

### 对象定义

`EXCLUDE_OBJECT_DEFINE` 命令用于提供 gcode 文件中每个待打印对象的摘要。提供文件中对象的摘要。对象无需定义即可被其他命令引用。此命令的主要目的是在无需解析整个 gcode 文件的情况下向 UI 提供信息。

对象定义是命名的，允许用户轻松选择要排除的对象，还可以提供附加元数据以允许图形化的取消显示。当前定义的元数据包括 `CENTER` X,Y 坐标和表示对象最小轮廓的 `POLYGON` X,Y 点列表。这可以是简单的边界框，也可以是用于显示更详细打印对象可视化的复杂凸包。特别是当 gcode 文件包含具有重叠边界区域的多个部分时，中心点在视觉上变得难以区分。`POLYGONS` 必须是点 `[X,Y]` 元组的 JSON 兼容数组，不带空白字符。附加参数将作为字符串保存在对象定义中，并在状态更新中提供。

`EXCLUDE_OBJECT_DEFINE NAME=calibration_pyramid CENTER=50,50 POLYGON=[[40,40],[50,60],[60,40]]`

所有可用的 G-Code 命令文档请参阅 [G-Code 参考](G-Codes.md#exclude_object)

## 状态信息
此模块的状态通过 [exclude_object 状态](Status_Reference.md#exclude_object)提供给客户端。

状态在以下情况下重置：
- Kalico 固件重启时。
- `[virtual_sdcard]` 重置时。值得注意的是，Kalico 在打印开始时会重置它。
- 发出 `EXCLUDE_OBJECT_DEFINE RESET=1` 命令时。

已定义对象的列表在 `exclude_object.objects` 状态字段中表示。在定义良好的 gcode 文件中，这将通过文件开头的 `EXCLUDE_OBJECT_DEFINE` 命令完成。这将向客户端提供对象名称和坐标，以便 UI 可以在需要时提供对象的图形表示。

随着打印的进行，当 Kalico 处理 `EXCLUDE_OBJECT_START` 和 `EXCLUDE_OBJECT_END` 命令时，`exclude_object.current_object` 状态字段将被更新。即使对象已被排除，`current_object` 字段也会被设置。标记为 `EXCLUDE_OBJECT_START` 的未定义对象将被添加到已知对象中以辅助 UI 提示，而不带任何附加元数据。

随着 `EXCLUDE_OBJECT` 命令的发出，排除对象列表在 `exclude_object.excluded_objects` 数组中提供。由于 Kalico 向前查看以处理即将执行的 gcode，命令发出和状态更新之间可能存在延迟。
