# AI Agent Integration Guide

本指南面向 AI Agent（如 GitHub Copilot），描述如何通过 JSON-RPC 接口与 Kalico Debug Tool 交互。

## 接口地址

```bash
echo '<JSON_COMMAND>' | python -m kalico_debug_tool --batch
```

或通过管道传递多个命令：

```bash
echo '{"id":"1","cmd":"connect","params":{"port":"COM3"}}' | python -m kalico_debug_tool --batch
```

## 命令参考

### 连接管理

#### `connect`
连接串口设备。

```json
{"id": "1", "cmd": "connect", "params": {"port": "COM3", "baudrate": 250000}}
```

#### `disconnect`
断开串口连接。

```json
{"id": "2", "cmd": "disconnect", "params": {}}
```

#### `get_status`
获取连接状态和统计。

```json
{"id": "3", "cmd": "get_status", "params": {}}
```

响应示例：
```json
{
  "id": "3",
  "ok": true,
  "data": {
    "connection": {
      "state": "connected",
      "port": "COM3",
      "packets_sent": 5,
      "packets_received": 10
    },
    "log_events": 15,
    "virtual_mcu": null
  }
}
```

### 数据收发

#### `send_raw`
发送原始 Hex 字节。

```json
{"id": "4", "cmd": "send_raw", "params": {"hex_str": "0a 1b 2c"}}
```

#### `send_command`
发送命名命令（使用 data dictionary 编码）。

```json
{"id": "5", "cmd": "send_command", "params": {"name": "identify", "params": {"offset": 0, "count": 40}}}
```

### 查看

#### `get_messages`
获取最近的消息记录。

```json
{"id": "6", "cmd": "get_messages", "params": {"count": 10}}
```

#### `get_dictionary`
获取 data dictionary 内容（固件支持的所有命令列表）。

```json
{"id": "7", "cmd": "get_dictionary", "params": {}}
```

### 虚拟 MCU

#### `sim_start`
启动虚拟 MCU 模拟器（无需真实硬件即可调试）。

```json
{"id": "8", "cmd": "sim_start", "params": {"name": "my-mcu"}}
```

#### `sim_send`
向虚拟 MCU 发送命令。

```json
{"id": "9", "cmd": "sim_send", "params": {"name": "identify", "params": {"offset": 0, "count": 40}}}
```

#### `sim_register`
注册自定义命令响应。

```json
{"id": "10", "cmd": "sim_register", "params": {"cmd_name": "my_command", "response_hex": "0a1b2c"}}
```

#### `sim_stop`
停止虚拟 MCU。

```json
{"id": "11", "cmd": "sim_stop", "params": {}}
```

### 捕获

#### `capture_start`
开始捕获串口数据到文件。

```json
{"id": "12", "cmd": "capture_start", "params": {"name": "debug_session_1"}}
```

#### `capture_stop`
停止捕获。

```json
{"id": "13", "cmd": "capture_stop", "params": {}}
```

### CAN 总线

#### `connect` (CAN)
连接 CAN 总线设备。`port` 格式: `接口类型:通道`

```json
{"id": "14", "cmd": "connect", "params": {"port": "slcan:COM3", "baudrate": 500000, "io_type": "can"}}
```

支持接口类型: `slcan` (USB转CAN串口桥), `pcan` (PEAK PCAN), `virtual` (虚拟CAN)

#### `can_discover`
发现 CAN 总线上的 MCU 节点。

```json
{"id": "15", "cmd": "can_discover", "params": {"timeout": 3.0}}
```

#### `can_assign`
分配 NodeID 给指定 UUID 的 MCU。

```json
{"id": "16", "cmd": "can_assign", "params": {"uuid": "a1b2c3d4e5f6", "nodeid": 64}}
```

#### `disconnect` (CAN)
断开 CAN 连接。

```json
{"id": "17", "cmd": "disconnect", "params": {"io_type": "can"}}
```

### CAN 命令参考 (AI Bridge)

所有标准命令 (`send_raw`, `send_command`, `get_status` 等) 支持 `io_type` 参数:

```json
{"id": "18", "cmd": "send_command", "params": {"name": "get_canbus_id", "io_type": "can"}}
```

## 典型调试流程

### 场景 1：连接真实 MCU 并监控

```json
{"id":"1","cmd":"connect","params":{"port":"COM3"}}
{"id":"2","cmd":"send_command","params":{"name":"identify","params":{"offset":0,"count":40}}}
{"id":"3","cmd":"get_messages","params":{"count":5}}
{"id":"4","cmd":"get_dictionary","params":{}}
```

### 场景 2：使用虚拟 MCU 离线调试

```json
{"id":"1","cmd":"sim_start","params":{}}
{"id":"2","cmd":"sim_send","params":{"name":"identify","params":{"offset":0,"count":40}}}
{"id":"3","cmd":"get_messages","params":{"count":5}}
{"id":"4","cmd":"sim_send","params":{"name":"config","params":{"oid":0}}}
```

### 场景 3：捕获-回放调试

```json
{"id":"1","cmd":"connect","params":{"port":"/dev/ttyACM0"}}
{"id":"2","cmd":"capture_start","params":{"name":"bug_repro"}}
{"id":"3","cmd":"send_command","params":{"name":"identify","params":{"offset":0,"count":40}}}
{"id":"4","cmd":"get_messages","params":{"count":20}}
{"id":"5","cmd":"capture_stop","params":{}}
{"id":"6","cmd":"get_status","params":{}}
```

## 错误处理

所有响应均包含 `ok` 字段：

```json
{"id": "5", "ok": true, "data": {...}}
{"id": "5", "ok": false, "error": "Not connected"}
```

常见错误：
- `"Not connected"` — 未连接串口时尝试发送数据
- `"Unknown command: xxx"` — 命令名不在 data dictionary 中
- `"Virtual MCU not running"` — 未启动虚拟 MCU 时尝试向它发送命令
