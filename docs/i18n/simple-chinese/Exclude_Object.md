# 排除对象

`[exclude_object]` 模块允许 Kalico 在打印进行中排除对象。要启用此功能，请包含 [exclude_object 配置部分](Config_Reference.md#exclude_object)（也请参阅 [命令参考](G-Codes.md#exclude_object) 和 [sample-macros.cfg](../config/sample-macros.cfg) 文件以获取与 Marlin/RepRapFirmware 兼容的 M486 G-Code 宏。）

与其他 3D 打印机固件选项不同，运行 Kalico 的打印机使用一套组件，用户有许多选择。因此，为了提供一致的用户体验，`[exclude_object]` 模块将建立一种契约或 API。该契约涵盖 gcode 文件的内容、模块的内部状态如何控制，以及该状态如何提供给客户端。

## 工作流概述
打印文件的典型工作流可能如下所示：
1. 切片完成，文件上传供打印。在上传期间，处理文件并将 `[exclude_object]` 标记添加到文件中。或者，切片器可能被配置为原生或在其自己的预处理步骤中准备对象排除标记。
2. 打印开始时，Kalico 将重置 `[exclude_object]` [状态](Status_Reference.md#exclude_object)。
3. 当 Kalico 处理 `EXCLUDE_OBJECT_DEFINE` 块时，它将使用已知对象更新状态并将其传递给客户端。
4. 客户端可以使用该信息向用户呈现用户界面，以便可以跟踪进度。Kalico 将更新状态以包括当前打印的对象，客户端可以用于显示目的。
5. 如果用户请求取消对象，客户端将向 Kalico 发出 `EXCLUDE_OBJECT NAME=<name>` 命令。
6. 当 Kalico 处理命令时，它将把对象添加到排除对象的列表中并为客户端更新状态。
7. 客户端将从 Kalico 接收更新的状态，并可以使用该信息在用户界面中反映对象的状态。
8. 打印完成后，`[exclude_object]` 状态将继续可用，直到另一个操作重置它。

## GCode 文件
支持排除对象所需的专业 gcode 处理不符合 Kalico 的核心设计目标。因此，此模块要求在将文件发送到 Kalico 进行打印之前处理该文件。在切片器中使用后处理脚本或在上传时让中间件处理文件是为 Kalico 准备文件的两种可能性。参考后处理脚本既可作为可执行文件也可作为 Python 库提供，请参阅 [cancelobject-preprocessor](https://github.com/kageurufu/cancelobject-preprocessor)。

### 对象定义

`EXCLUDE_OBJECT_DEFINE` 命令用于提供 gcode 文件中每个对象的摘要以供打印。提供文件中对象的摘要。对象不需要被定义才能被其他命令引用。此命令的主要目的是在不需要解析整个 gcode 文件的情况下向用户界面提供信息。

对象定义已命名，允许用户轻松选择要排除的对象，并且可以提供其他元数据以允许图形取消显示。当前定义的元数据包括 `CENTER` X、Y 坐标和 `POLYGON` X、Y 点列表，表示对象的最小轮廓。这可以是简单的边界框，也可以是复杂的包络以显示打印对象的更详细的可视化。特别是当 gcode 文件包含多个边界区域重叠的部分时，中心点变得难以在视觉上区分。`POLYGONS` 必须是无空格的点 `[X,Y]` 元组的 json 兼容数组。其他参数将作为字符串保存在对象定义中并在状态更新中提供。

`EXCLUDE_OBJECT_DEFINE NAME=calibration_pyramid CENTER=50,50 POLYGON=[[40,40],[50,60],[60,40]]`

所有可用的 G-Code 命令都在 [G-Code 参考](G-Codes.md#exclude_object) 中记录

## 状态信息
此模块的状态通过 [exclude_object 状态](Status_Reference.md#exclude_object) 提供给客户端。

状态在以下情况下重置：
- Kalico 固件重新启动。
- `[virtual_sdcard]` 重置。值得注意的是，这在 Kalico 打印开始时重置。
- 当发出 `EXCLUDE_OBJECT_DEFINE RESET=1` 命令时。

定义的对象列表以 `exclude_object.objects` 状态字段表示。在定义良好的 gcode 文件中，这将通过文件开头的 `EXCLUDE_OBJECT_DEFINE` 命令完成。这将为客户端提供对象名称和坐标，以便用户界面可以提供对象的图形表示（如果需要）。

随着打印的进行，当 Kalico 处理 `EXCLUDE_OBJECT_START` 和 `EXCLUDE_OBJECT_END` 命令时，`exclude_object.current_object` 状态字段将更新。即使对象已被排除，`current_object` 字段也将被设置。用 `EXCLUDE_OBJECT_START` 标记的未定义对象将被添加到已知对象中以帮助用户界面提示，但不包含任何其他元数据。

当发出 `EXCLUDE_OBJECT` 命令时，排除的对象列表在 `exclude_object.excluded_objects` 数组中提供。由于 Kalico 提前处理即将到来的 gcode，在发出命令和状态更新之间可能会有延迟。