# API 服务器

本文档描述 Kalico 的应用程序编程接口 (API)。此接口允许外部应用程序查询和控制 Kalico 主机软件。

## 启用 API 套接字

为了使用 API 服务器，klippy.py 主机软件必须使用 `-a` 参数启动。例如：
```
~/klippy-env/bin/python ~/klipper/klippy/klippy.py ~/printer.cfg -a /tmp/klippy_uds -l /tmp/klippy.log
```

这导致主机软件创建一个 Unix 域套接字。客户端随后可以在该套接字上打开连接并向 Kalico 发送命令。

有关可以转发 HTTP 请求到 Kalico 的 API 服务器 Unix 域套接字的流行工具，请参阅 [Moonraker](https://github.com/Arksine/moonraker) 项目。

## 请求格式

在套接字上发送和接收的消息是 JSON 编码的字符串，以 ASCII 0x03 字符终止：
```
<json_object_1><0x03><json_object_2><0x03>...
```

Kalico 包含一个 `scripts/whconsole.py` 工具，可以执行上述消息帧处理。例如：
```
~/klipper/scripts/whconsole.py /tmp/klippy_uds
```

该工具可以从标准输入读取一系列 JSON 命令，将其发送到 Kalico，并报告结果。该工具期望每个 JSON 命令在单行上，并在传输请求时自动附加 0x03 终止符。（Kalico API 服务器不要求换行符。）

## API 协议

通信套接字上使用的命令协议受到 [json-rpc](https://www.jsonrpc.org/) 的启发。

请求可能如下所示：

`{"id": 123, "method": "info", "params": {}}`

响应可能如下所示：

`{"id": 123, "result": {"state_message": "Printer is ready", "klipper_path": "/home/pi/klipper", "config_file": "/home/pi/printer.cfg", "software_version": "v0.8.0-823-g883b1cb6", "hostname": "octopi", "cpu_info": "4 core ARMv7 Processor rev 4 (v7l)", "state": "ready", "python_path": "/home/pi/klippy-env/bin/python", "log_file": "/tmp/klippy.log"}}`

每个请求必须是一个 JSON 字典。（本文档使用 Python 术语 "dictionary" 来描述 "JSON object" — 包含在 `{}` 内的键值对的映射。）

请求字典必须包含一个 "method" 参数，该参数是可用 Kalico "endpoint" 的字符串名称。

请求字典可能包含一个 "params" 参数，该参数必须是字典类型。"params" 向处理请求的 Kalico "endpoint" 提供额外的参数信息。其内容特定于 "endpoint"。

请求字典可能包含一个 "id" 参数，该参数可以是任何 JSON 类型。如果存在 "id"，则 Kalico 将使用包含该 "id" 的响应消息来响应请求。如果省略 "id"（或设置为 JSON "null" 值），则 Kalico 将不对请求提供任何响应。响应消息是包含 "id" 和 "result" 的 JSON 字典。"result" 始终是一个字典 — 其内容特定于处理请求的 "endpoint"。

如果请求的处理导致错误，则响应消息将包含 "error" 字段而不是 "result" 字段。例如，请求：
`{"id": 123, "method": "gcode/script", "params": {"script": "G1 X200"}}`
可能导致错误响应，例如：
`{"id": 123, "error": {"message": "Must home axis first: 200.000 0.000 0.000 [0.000]", "error": "WebRequestError"}}`

Kalico 将始终按接收顺序开始处理请求。但是，某些请求可能不会立即完成，这可能导致关联的响应与其他请求的响应失序。JSON 请求永远不会暂停后续 JSON 请求的处理。

## 订阅

某些 Kalico "endpoint" 请求允许用户"订阅"未来的异步更新消息。

例如：

`{"id": 123, "method": "gcode/subscribe_output", "params": {"response_template":{"key": 345}}}`

可能最初响应：

`{"id": 123, "result": {}}`

并导致 Kalico 发送类似以下内容的未来消息：

`{"params": {"response": "ok B:22.8 /0.0 T0:22.4 /0.0"}, "key": 345}`

订阅请求在请求的 "params" 字段中接受一个 "response_template" 字典。该 "response_template" 字典用作未来异步消息的模板 — 它可能包含任意键值对。发送这些未来的异步消息时，Kalico 将添加一个包含端点特定内容的字典的 "params" 字段到响应模板，然后发送该模板。如果未提供 "response_template" 字段，则默认为空字典 (`{}`)。

## 可用的 "endpoints"

按照惯例，Kalico "endpoints" 的形式为 `<module_name>/<some_name>`。在向 "endpoint" 发出请求时，完整名称必须在请求字典的 "method" 参数中设置（例如，`{"method"="gcode/restart"}`）。

### info

"info" endpoint 用于从 Kalico 获取系统和版本信息。它也用于向 Kalico 提供客户端的版本信息。例如：
`{"id": 123, "method": "info", "params": { "client_info": { "version": "v1"}}}`

如果存在，"client_info" 参数必须是一个字典，但该字典可能有任意内容。鼓励客户端在首次连接到 Kalico API 服务器时提供客户端的名称及其软件版本。

### emergency_stop

"emergency_stop" endpoint 用于指示 Kalico 转换到"shutdown"状态。它的行为类似于 G-Code `M112` 命令。例如：
`{"id": 123, "method": "emergency_stop"}`

### register_remote_method

此 endpoint 允许客户端注册可以从 Kalico 调用的方法。成功时将返回一个空对象。

例如：
`{"id": 123, "method": "register_remote_method", "params": {"response_template": {"action": "run_paneldue_beep"}, "remote_method": "paneldue_beep"}}`
将返回：
`{"id": 123, "result": {}}`

远程方法 `paneldue_beep` 现在可以从 Kalico 调用。请注意，如果方法接受参数，应将其作为关键字参数提供。以下是如何从 gcode_macro 调用的示例：
```
[gcode_macro PANELDUE_BEEP]
gcode:
  {action_call_remote_method("paneldue_beep", frequency=300, duration=1.0)}
```

当执行 PANELDUE_BEEP gcode 宏时，Kalico 会在套接字上发送类似以下内容：
`{"action": "run_paneldue_beep", "params": {"frequency": 300, "duration": 1.0}}`

### objects/list

此 endpoint 查询可查询的可用打印机"对象"的列表（通过"objects/query" endpoint）。例如：
`{"id": 123, "method": "objects/list"}`
可能返回：
`{"id": 123, "result": {"objects": ["webhooks", "configfile", "heaters", "gcode_move", "query_endstops", "idle_timeout", "toolhead", "extruder"]}}`

### objects/query

此 endpoint 允许查询来自打印机对象的信息。例如：
`{"id": 123, "method": "objects/query", "params": {"objects": {"toolhead": ["position"], "webhooks": null}}}`
可能返回：
`{"id": 123, "result": {"status": {"webhooks": {"state": "ready", "state_message": "Printer is ready"}, "toolhead": {"position": [0.0, 0.0, 0.0, 0.0]}}, "eventtime": 3051555.377933684}}`

请求中的 "objects" 参数必须是包含要查询的打印机对象的字典 — 键包含打印机对象名称，值为 "null"（查询所有字段）或字段名称列表。

响应消息将包含一个 "status" 字段，其中包含所查询信息的字典 — 键包含打印机对象名称，值是包含其字段的字典。响应消息还将包含一个 "eventtime" 字段，其中包含查询进行时的时间戳。

可用字段在 [Status Reference](Status_Reference.md) 文档中有记载。

### objects/subscribe

此 endpoint 允许查询然后订阅来自打印机对象的信息。endpoint 请求和响应与 "objects/query" endpoint 相同。例如：
`{"id": 123, "method": "objects/subscribe", "params": {"objects":{"toolhead": ["position"], "webhooks": ["state"]}, "response_template":{}}}`
可能返回：
`{"id": 123, "result": {"status": {"webhooks": {"state": "ready"}, "toolhead": {"position": [0.0, 0.0, 0.0, 0.0]}}, "eventtime": 3052153.382083195}}`
并导致后续异步消息，例如：
`{"params": {"status": {"webhooks": {"state": "shutdown"}}, "eventtime": 3052165.418815847}}`

### gcode/help

此 endpoint 允许查询具有定义的帮助字符串的可用 G-Code 命令。例如：
`{"id": 123, "method": "gcode/help"}`
可能返回：
`{"id": 123, "result": {"RESTORE_GCODE_STATE": "Restore a previously saved G-Code state", "PID_CALIBRATE": "Run PID calibration test", "QUERY_ADC": "Report the last value of an analog pin", ...}}`

### gcode/script

此 endpoint 允许运行一系列 G-Code 命令。例如：
`{"id": 123, "method": "gcode/script", "params": {"script": "G90"}}`

如果提供的 G-Code 脚本引发错误，则会生成错误响应。但是，如果 G-Code 命令产生终端输出，则该终端输出不会在响应中提供。（使用 "gcode/subscribe_output" endpoint 获取 G-Code 终端输出。）

如果在接收此请求时正在处理 G-Code 命令，则提供的脚本将被排队。此延迟可能很重要（例如，如果 G-Code 等待温度命令正在运行）。当脚本的处理完全完成时，发送 JSON 响应消息。

### gcode/restart

此 endpoint 允许请求重启 — 类似于运行 G-Code "RESTART" 命令。例如：
`{"id": 123, "method": "gcode/restart"}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。

### gcode/firmware_restart

这类似于 "gcode/restart" endpoint — 它实现 G-Code "FIRMWARE_RESTART" 命令。例如：
`{"id": 123, "method": "gcode/firmware_restart"}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。

### gcode/subscribe_output

此 endpoint 用于订阅由 Kalico 生成的 G-Code 终端消息。例如：
`{"id": 123, "method": "gcode/subscribe_output", "params": {"response_template":{}}}`
稍后可能产生异步消息，例如：
`{"params": {"response": "// Klipper state: Shutdown"}}`

此 endpoint 旨在支持通过"终端窗口"界面进行人机交互。不建议从 G-Code 终端输出解析内容。使用 "objects/subscribe" endpoint 获取有关 Kalico 状态的更新。

### motion_report/dump_stepper

此 endpoint 用于订阅 Kalico 的内部 stepper queue_step 命令流以获取步进电机。获取这些低级运动更新可能对诊断和调试目的有用。使用此 endpoint 可能会增加 Kalico 的系统负载。

请求可能如下所示：
`{"id": 123, "method":"motion_report/dump_stepper", "params": {"name": "stepper_x", "response_template": {}}}`
可能返回：
`{"id": 123, "result": {"header": ["interval", "count", "add"]}}`
稍后可能产生异步消息，例如：
`{"params": {"first_clock": 179601081, "first_time": 8.98, "first_position": 0, "last_clock": 219686097, "last_time": 10.984, "data": [[179601081, 1, 0], [29573, 2, -8685], [16230, 4, -1525], [10559, 6, -160], [10000, 976, 0], [10000, 1000, 0], [10000, 1000, 0], [10000, 1000, 0], [9855, 5, 187], [11632, 4, 1534], [20756, 2, 9442]]}}`

初始查询响应中的 "header" 字段用于描述在后续 "data" 响应中找到的字段。

### motion_report/dump_trapq

此 endpoint 用于订阅 Kalico 的内部"梯形运动队列"。获取这些低级运动更新可能对诊断和调试目的有用。使用此 endpoint 可能会增加 Kalico 的系统负载。

请求可能如下所示：
`{"id": 123, "method": "motion_report/dump_trapq", "params": {"name": "toolhead", "response_template":{}}}`
可能返回：
`{"id": 1, "result": {"header": ["time", "duration", "start_velocity", "acceleration", "start_position", "direction"]}}`
稍后可能产生异步消息，例如：
`{"params": {"data": [[4.05, 1.0, 0.0, 0.0, [300.0, 0.0, 0.0], [0.0, 0.0, 0.0]], [5.054, 0.001, 0.0, 3000.0, [300.0, 0.0, 0.0], [-1.0, 0.0, 0.0]]]}}`

初始查询响应中的 "header" 字段用于描述在后续 "data" 响应中找到的字段。

### adxl345/dump_adxl345

此 endpoint 用于订阅 ADXL345 加速度计数据。获取这些低级运动更新可能对诊断和调试目的有用。使用此 endpoint 可能会增加 Kalico 的系统负载。

请求可能如下所示：
`{"id": 123, "method":"adxl345/dump_adxl345", "params": {"sensor": "adxl345", "response_template": {}}}`
可能返回：
`{"id": 123,"result":{"header":["time","x_acceleration","y_acceleration","z_acceleration"]}}`
稍后可能产生异步消息，例如：
`{"params":{"overflows":0,"data":[[3292.432935,-535.44309,-1529.8374,9561.4],[3292.433256,-382.45935,-1606.32927,9561.48375]]}}`

初始查询响应中的 "header" 字段用于描述在后续 "data" 响应中找到的字段。

### angle/dump_angle

此 endpoint 用于订阅 [角度传感器数据](Config_Reference.md#angle)。获取这些低级运动更新可能对诊断和调试目的有用。使用此 endpoint 可能会增加 Kalico 的系统负载。

请求可能如下所示：
`{"id": 123, "method":"angle/dump_angle", "params": {"sensor": "my_angle_sensor", "response_template": {}}}`
可能返回：
`{"id": 123,"result":{"header":["time","angle"]}}`
稍后可能产生异步消息，例如：
`{"params":{"position_offset":3.151562,"errors":0,"data":[[1290.951905,-5063],[1290.952321,-5065]]}}`

初始查询响应中的 "header" 字段用于描述在后续 "data" 响应中找到的字段。

### load_cell/dump_force

此 endpoint 用于订阅由 load_cell 生成的力数据。使用此 endpoint 可能会增加 Klipper 的系统负载。

请求可能如下所示：
`{"id": 123, "method":"load_cell/dump_force", "params": {"sensor": "load_cell", "response_template": {}}}`
可能返回：
`{"id": 123,"result":{"header":["time", "force (g)", "counts", "tare_counts"]}}`
稍后可能产生异步消息，例如：
`{"params":{"data":[[3292.432935, 40.65, 562534, -234467]]}}`

初始查询响应中的 "header" 字段用于描述在后续 "data" 响应中找到的字段。

### load_cell_probe/dump_taps

此 endpoint 用于订阅探针"点击"事件的详细信息。使用此 endpoint 可能会增加 Klipper 的系统负载。

请求可能如下所示：
`{"id": 123, "method":"load_cell/dump_force", "params": {"sensor": "load_cell", "response_template": {}}}`
可能返回：
`{"id": 123,"result":{"header":["probe_tap_event"]}}`
稍后可能产生异步消息，例如：
```
{"params":{"tap":{
   "time": [118032.28039, 118032.2834, ...],
   "force": [-459.4213119680034, -458.1640702543264, ...],
}}}
```

此数据可用于呈现：
* 时间/力图表

### pause_resume/cancel

此 endpoint 类似于运行 "PRINT_CANCEL" G-Code 命令。例如：
`{"id": 123, "method": "pause_resume/cancel"}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。

### pause_resume/pause

此 endpoint 类似于运行 "PAUSE" G-Code 命令。例如：
`{"id": 123, "method": "pause_resume/pause"}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。

### pause_resume/resume

此 endpoint 类似于运行 "RESUME" G-Code 命令。例如：
`{"id": 123, "method": "pause_resume/resume"}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。

### query_endstops/status

此 endpoint 将查询活跃的端点并返回其状态。例如：
`{"id": 123, "method": "query_endstops/status"}`
可能返回：
`{"id": 123, "result": {"y": "open", "x": "open", "z": "TRIGGERED"}}`

与 "gcode/script" endpoint 一样，此 endpoint 仅在任何待处理的 G-Code 命令完成后完成。