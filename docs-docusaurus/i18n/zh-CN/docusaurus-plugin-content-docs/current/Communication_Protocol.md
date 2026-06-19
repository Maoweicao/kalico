# 通信协议：C 与 Python 接口

本文档描述了 `src/` 目录中的 C/C++ 代码与 `klippy/` 目录中的 Python 代码之间使用的各种通信机制。了解这些机制对于想要修改或扩展固件的开发人员至关重要。

---

## 概述

Kalico 采用了多层通信架构，以弥合高级 Python 主机代码与低级 C 微控制器固件之间的差距。共有**四种不同的通信通道**：

| 通道 | 机制 | 格式 | 方向 | 用途 |
|------|------|------|------|------|
| **CFFI** | `cffi` 库 | C 函数调用 | Python → C | 性能关键的计算 |
| **Serial/UART** | `pyserial` / `python-can` | 二进制协议 | 主机 → MCU | MCU 命令/响应 |
| **自定义二进制协议** | `msgproto.py` 和 `command.c` | VLQ + CRC16 | 主机 → MCU | 固件 RPC |
| **API 服务器** | Unix 域套接字 | JSON + ETX | 外部 → 主机 | 监控/控制 |

---

## 1. CFFI：Python 与 C 辅助库

### 位置
- Python 封装：`klippy/chelper/__init__.py`
- C 源文件：`klippy/chelper/*.c`
- 编译库：`klippy/chelper/c_helper.so`

### 工作原理

CFFI（C 外部函数接口）层允许 Python 代码直接调用 C 函数，以执行性能关键的操作。启动时，Kalico 会检查 `c_helper.so` 是否存在且是否为最新版本。如果不是，它将使用以下标志通过 `gcc` 编译所有 C 辅助文件：

```
-Wall -g -O2 -shared -fPIC -flto -fwhole-program -fno-use-linker-plugin
```

C 源文件被编译为单个共享库：

| C 源文件 | 用途 |
|----------|------|
| `pyhelper.c` | Python 日志回调注册 |
| `serialqueue.c` | 低延迟串行 I/O 队列 |
| `stepcompress.c` | 步进脉冲压缩 |
| `itersolve.c` | 步进定时的迭代求解器 |
| `trapq.c` | 梯形速度队列 |
| `pollreactor.c` | 基于轮询的事件反应器 |
| `msgblock.c` | 消息块帧 |
| `trdispatch.c` | 触发器调度 |
| `kin_cartesian.c` | 笛卡尔运动学 |
| `kin_corexy.c` | CoreXY 运动学 |
| `kin_corexz.c` | CoreXZ 运动学 |
| `kin_delta.c` | Delta 运动学 |
| `kin_deltesian.c` | Deltesian 运动学 |
| `kin_polar.c` | 极坐标运动学 |
| `kin_rotary_delta.c` | 旋转 delta 运动学 |
| `kin_winch.c` | 绞盘运动学 |
| `kin_extruder.c` | 挤出机压力提前 |
| `kin_shaper.c` | 输入整形器 |
| `kin_idex.c` | 双滑块 (IDEX) |

### CFFI 函数定义示例

在 `chelper/__init__.py` 中，函数签名以 C 字符串形式声明：

```python
defs_stepcompress = """
    struct stepcompress *stepcompress_alloc(uint32_t oid);
    void stepcompress_fill(struct stepcompress *sc, uint32_t max_error
        , int32_t queue_step_msgtag, int32_t set_next_step_dir_msgtag);
    void stepcompress_free(struct stepcompress *sc);
    // ...
"""
```

这些定义通过以下方式加载：

```python
import cffi
FFI_main = cffi.FFI()
FFI_main.cdef(defs_stepcompress)
FFI_lib = FFI_main.dlopen("c_helper.so")
```

### 在 Python 代码中的使用

Python 模块导入并使用 C 辅助函数的方式如下：

```python
from . import chelper
ffi_main, ffi_lib = chelper.get_ffi()

# 直接调用 C 函数
self._stepqueue = ffi_main.gc(
    ffi_lib.stepcompress_alloc(oid),
    ffi_lib.stepcompress_free
)
```

### 从 Python 到 C 的回调

C 代码也可以通过 CFFI 回调调用 Python 函数。例如，从 C 到 Python 的日志记录：

```python
# 在 chelper/__init__.py 中
@FFI_main.callback("void func(const char *)")
def logging_callback(msg):
    logging.info("MCU: %s", ffi_main.string(msg).decode())

pyhelper_logging_callback = FFI_main.callback(
    "void func(const char *)", logging_callback
)
FFI_lib.set_python_logging_callback(pyhelper_logging_callback)
```

### 数据流：CFFI

![CFFI 数据流](/img/en/comm-cffi-flow.svg)

---

## 2. 串行 / UART 通信

### 位置
- Python：`klippy/serialhdl.py`
- C 底层：`src/generic/serial_irq.c`
- 平台特定：`src/*/serial.c`

### 工作原理

主机计算机（如 Raspberry Pi）通过串行连接与微控制器通信。可以是：

- **UART（TTL 串行）**：基于 GPIO 的直接串行
- **USB CDC ACM**：通过 USB 的虚拟串行端口
- **CAN 总线**：使用 `python-can` 的控制器局域网

### 连接建立

```python
# 在 serialhdl.py 中
import serial
self.serial = serial.Serial(port, baudrate)
```

对于 CAN 总线：

```python
import can
self.can = can.interface.Bus(channel='can0', bustype='socketcan')
```

### C 端串行处理

在微控制器上，串行数据接收由中断驱动：

```c
// 在 src/generic/serial_irq.c 中
void serial_enable_receive(int fd) {
    // 启用 UART RX 中断
}
```

接收到的字节被累积并传递给 `command_find_and_dispatch()`，该函数定位完整的消息块并调度命令。

### 数据流：串行

![串行数据流](/img/en/comm-serial-flow.svg)

---

## 3. 二进制消息协议（核心 RPC 层）

这是主机与微控制器之间**最重要**的通信机制。它是一种自定义二进制协议，类似于远程过程调用（RPC）系统。

### 位置
- Python 编码器/解码器：`klippy/msgproto.py`
- C 编码器/解码器/调度器：`src/command.c` + `src/command.h`

### 消息块格式

主机和 MCU 之间传输的每条消息都封装在具有以下结构的消息块中：

```
Offset  Size  Field
─────────────────────────
 0       1    长度（总块大小，最小=5，最大=64）
 1       1    序列号（4位 seq | 0x10）
 2       n    内容（VLQ 编码的命令/响应）
 2+n     2    CRC-16 CCITT
 2+n+2   1    同步字节（0x7E）
```

**关键常量**（在 `msgproto.py` 和 `command.h` 中相同）：

| 常量 | 值 | 描述 |
|------|----|------|
| `MESSAGE_MIN` | 5 | 最小消息块大小 |
| `MESSAGE_MAX` | 64 | 最大消息块大小 |
| `MESSAGE_HEADER_SIZE` | 2 | 头部字节（len + seq） |
| `MESSAGE_TRAILER_SIZE` | 3 | 尾部字节（crc16[2] + sync） |
| `MESSAGE_SYNC` | 0x7E | 帧同步标记 |
| `MESSAGE_DEST` | 0x10 | 序列号高位 |

### 变长数量（VLQ）编码

消息内容中的整数使用自定义 VLQ 方案编码，支持正数和负数：

| 整数范围 | 编码字节数 |
|----------|-----------|
| -32 .. 95 | 1 字节 |
| -4096 .. 12287 | 2 字节 |
| -524288 .. 1572863 | 3 字节 |
| -67108864 .. 201326591 | 4 字节 |
| -2147483648 .. 4294967295 | 5 字节 |

**编码规则**：
- 每个字节使用 7 位数据，1 位（MSB）作为继续标志
- 符号扩展在解码时处理
- 较小的绝对值使用更少的字节

**C 实现**（`src/command.c`）：
```c
static uint8_t *encode_int(uint8_t *p, uint32_t v) {
    int32_t sv = v;
    if (sv < (3L<<5)  && sv >= -(1L<<5))  goto f4;  // 1 字节
    if (sv < (3L<<12) && sv >= -(1L<<12)) goto f3;  // 2 字节
    if (sv < (3L<<19) && sv >= -(1L<<19)) goto f2;  // 3 字节
    if (sv < (3L<<26) && sv >= -(1L<<26)) goto f1;  // 4 字节
    *p++ = (v>>28) | 0x80;                           // 5 字节
f1: *p++ = ((v>>21) & 0x7f) | 0x80;
f2: *p++ = ((v>>14) & 0x7f) | 0x80;
f3: *p++ = ((v>>7) & 0x7f) | 0x80;
f4: *p++ = v & 0x7f;
    return p;
}
```

**Python 实现**（`klippy/msgproto.py`）：
```python
class PT_uint32:
    def encode(self, out, v):
        if v >= 0xC000000 or v < -0x4000000:
            out.append((v >> 28) & 0x7F | 0x80)
        if v >= 0x180000 or v < -0x80000:
            out.append((v >> 21) & 0x7F | 0x80)
        if v >= 0x3000 or v < -0x1000:
            out.append((v >> 14) & 0x7F | 0x80)
        if v >= 0x60 or v < -0x20:
            out.append((v >> 7) & 0x7F | 0x80)
        out.append(v & 0x7F)
```

### 参数类型

协议支持以下参数类型：

| 类型名称 | C 枚举 | Python 类 | 描述 |
|----------|--------|-----------|------|
| `%u` | `PT_uint32` | `PT_uint32` | 无符号 32 位整数 |
| `%i` | `PT_int32` | `PT_int32` | 有符号 32 位整数 |
| `%hu` | `PT_uint16` | `PT_uint16` | 无符号 16 位整数 |
| `%hi` | `PT_int16` | `PT_int16` | 有符号 16 位整数 |
| `%c` | `PT_byte` | `PT_byte` | 8 位字节 |
| `%s` | `PT_string` | `PT_string` | 动态字符串 |
| `%.*s` | `PT_progmem_buffer` | `PT_progmem_buffer` | Flash 存储的缓冲区 |
| `%*s` | `PT_buffer` | `PT_buffer` | RAM 缓冲区 |

### 命令声明（C 端）

命令在 C 中使用 `DECL_COMMAND()` 声明：

```c
DECL_COMMAND(command_update_digital_out,
             "update_digital_out oid=%c value=%c");
```

这会在编译后的二进制文件中生成一个 `command_parser` 结构：

```c
struct command_parser {
    uint16_t encoded_msgid;   // VLQ 编码的消息 ID
    uint8_t num_args;         // 函数参数数量
    uint8_t flags;            // 处理器标志（例如 HF_IN_SHUTDOWN）
    uint8_t num_params;       // 线路格式参数数量
    const uint8_t *param_types; // 参数类型枚举数组
    void (*func)(uint32_t *args); // 处理器函数指针
};
```

### 响应传输（C 端）

响应使用 `sendf()` 宏发送：

```c
sendf("status clock=%u status=%c",
      sched_read_time(), sched_is_shutdown());
```

### 消息内容：每个块多个命令

单个消息块可以包含多个命令：

```
人类可读格式：
  update_digital_out oid=6 value=1
  update_digital_out oid=5 value=0
  get_config
  get_clock

二进制格式（VLQ 整数）：
  <id_update_digital_out><6><1><id_update_digital_out><5><0><id_get_config><id_get_clock>
```

### CRC-16 CCITT

双方使用相同的 CRC-16 CCITT 实现进行数据完整性验证：

```python
# Python（msgproto.py）
def crc16_ccitt(buf):
    crc = 0xFFFF
    for data in buf:
        data ^= crc & 0xFF
        data ^= (data & 0x0F) << 4
        crc = ((data << 8) | (crc >> 8)) ^ (data >> 4) ^ (data << 3)
    return [crc >> 8, crc & 0xFF]
```

C 实现在特定于板卡的代码中（例如 `src/generic/crc16_ccitt.c`）。

### 数据字典（识别协议）

当主机首次连接到 MCU 时，必须下载**数据字典**。此字典将命令/响应格式字符串映射到其数字 ID。

1. 主机发送 `identify` 命令请求数据块
2. MCU 使用包含压缩 JSON 的 `identify_response` 响应
3. JSON 经过 zlib 压缩并存储在 MCU 的 flash 中
4. 组装完成后，主机解析 JSON 以了解所有可用的命令、响应、枚举和常量

`identify` 命令（ID=1）和 `identify_response`（ID=0）是唯一具有硬编码 ID 的消息。其他所有内容都是动态的。

### 确认和重传

**主机 → MCU**（可靠传输）：
- 每个正确接收的块都会触发 MCU 发送 ACK
- 主机超时后重传
- MCU 对损坏/乱序的块发送 NAK
- 窗口机制允许多个在途块

**MCU → 主机**（尽力传输）：
- 无自动重传
- 高级代码必须处理缺失的响应
- 序列号仅跟踪主机发起的流量

---

## 4. API 服务器：Unix 域套接字 + JSON

### 位置
- Python：`klippy/webhooks.py`

### 工作原理

API 服务器通过 Unix 域套接字提供对外部打印机状态和控制的访问：

```python
# 在 webhooks.py 中
self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
self.sock.bind("/tmp/kalico_uds")
```

### 消息格式

消息是 JSON 编码的字符串，以 `0x03`（ETX）终止：

```
<json_object_1><0x03><json_object_2><0x03>...
```

这允许 OctoPrint、Mainsail 和 Fluidd 等工具与 Kalico 通信以进行监控和控制。

---

## 5. 线程架构

主机端 Klippy 进程使用 **4 个线程**：

| 线程 | 位置 | 用途 |
|------|------|------|
| 主线程 | `klippy/gcode.py` | 传入 G-code 处理 |
| 串行 I/O | `klippy/chelper/serialqueue.c` | 底层串行端口 I/O |
| 响应处理器 | `klippy/serialhdl.py` | 处理 MCU 响应消息 |
| 日志记录器 | `klippy/queuelogger.py` | 非阻塞调试日志记录 |

---

## 6. 完整数据流图

![完整架构](/img/en/comm-full-architecture.svg)

---

## 7. 总结

| 层 | Python 端 | C 端 | 格式 | 可靠性 |
|----|-----------|------|------|--------|
| **CFFI** | `chelper/__init__.py` | `chelper/*.c` | 直接函数调用 | 不适用（进程内） |
| **二进制协议** | `msgproto.py` | `command.c/h` | VLQ 整数 + CRC16 | ACK/重传 |
| **串行传输** | `serialhdl.py` | `serial_irq.c` | UART/CAN/USB 上的原始字节 | 依赖硬件 |
| **API 服务器** | `webhooks.py` | 不适用 | Unix 套接字上的 JSON + ETX | TCP 可靠性 |
| **数据字典** | `msgproto.py`（解析） | `compile_time_request.c`（生成） | Zlib 压缩的 JSON | 连接时识别 |

### 关键设计原则

1. **最小化 MCU 复杂性**：MCU 使用静态（编译时）数据字典。主机适配 MCU 提供的任何内容。
2. **带宽效率**：VLQ 编码将常见小值的字节数降到最低。多个命令按块批量处理。
3. **错误检测**：CRC-16 CCITT 捕获损坏。序列号检测乱序传输。
4. **关注点分离**：CFFI 处理计算，串行处理传输，msgproto 处理编码，API 服务器处理外部访问。
5. **性能关键路径使用 C**：步进压缩、迭代求解和串行 I/O 都用 C 实现以提高速度，而高级逻辑保留在 Python 中以保持灵活性。

---

## 另请参阅

- [协议](Protocol.md) — 主机与 MCU 二进制协议的详细信息
- [代码概览](Code_Overview.md) — 整体代码结构
- [MCU 命令](MCU_Commands.md) — 可用的 MCU 命令
- [调试](Debugging.md) — 如何检查协议消息
