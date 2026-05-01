# 通信协议：C 与 Python 接口

本文档描述了 Kalico 中 `src/` 目录下的 C/C++ 代码
与 `klippy/` 目录下的 Python 代码之间的各种通信机制。
理解这些机制对于想要修改或扩展固件的开发者至关重要。

---

## 概述

Kalico 采用多层通信架构来桥接高层 Python 主控代码与
底层 C 微控制器固件。共有 **四个不同的通信通道**：

| 通道 | 机制 | 格式 | 方向 | 用途 |
|---------|-----------|--------|-----------|----------|
| **CFFI** | `cffi` 库 | C 函数调用 | Python ↔ C | 性能关键型计算 |
| **串口/UART** | `pyserial` / `python-can` | 二进制协议 | 主机 ↔ MCU | MCU 命令/响应 |
| **自定义二进制协议** | `msgproto.py` ↔ `command.c` | VLQ + CRC16 | 主机 ↔ MCU | 固件 RPC |
| **API 服务器** | Unix 域套接字 | JSON + ETX | 外部 ↔ 主机 | 监控/控制 |

---

## 1. CFFI：Python ↔ C 辅助库

### 位置
- Python 封装：`klippy/chelper/__init__.py`
- C 源文件：`klippy/chelper/*.c`
- 编译后的动态库：`klippy/chelper/c_helper.so`

### 工作原理

CFFI（C Foreign Function Interface，C 语言外部函数接口）层允许 Python
代码直接调用 C 函数来执行性能关键型操作。启动时，Kalico 会检查
`c_helper.so` 是否存在且是最新的。如果不是，则使用 `gcc` 编译所有 C
辅助文件，编译参数如下：

```
-Wall -g -O2 -shared -fPIC -flto -fwhole-program -fno-use-linker-plugin
```

所有 C 源文件被编译成一个共享库：

| C 源文件 | 用途 |
|---------------|---------|
| `pyhelper.c` | Python 日志回调注册 |
| `serialqueue.c` | 低延迟串口 I/O 队列 |
| `stepcompress.c` | 步进脉冲压缩 |
| `itersolve.c` | 步进时序迭代求解器 |
| `trapq.c` | 梯形速度队列 |
| `pollreactor.c` | 基于轮询的事件反应器 |
| `msgblock.c` | 消息块组帧 |
| `trdispatch.c` | 触发分发 |
| `kin_cartesian.c` | 笛卡尔坐标系运动学 |
| `kin_corexy.c` | CoreXY 运动学 |
| `kin_corexz.c` | CoreXZ 运动学 |
| `kin_delta.c` | Delta 运动学 |
| `kin_deltesian.c` | Deltesian 运动学 |
| `kin_polar.c` | 极坐标运动学 |
| `kin_rotary_delta.c` | 旋转 Delta 运动学 |
| `kin_winch.c` | 绞车运动学 |
| `kin_extruder.c` | 挤出机压力提前 |
| `kin_shaper.c` | 输入整形器 |
| `kin_idex.c` | 双喷头 (IDEX) |

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

Python 模块按如下方式导入并使用 C 辅助函数：

```python
from . import chelper
ffi_main, ffi_lib = chelper.get_ffi()

# 直接调用 C 函数
self._stepqueue = ffi_main.gc(
    ffi_lib.stepcompress_alloc(oid),
    ffi_lib.stepcompress_free
)
```

### 从 C 回调 Python

C 代码也可以通过 CFFI 回调来调用 Python 函数。例如，将日志从 C 输出到 Python：

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

![CFFI 数据流](../img/zh/comm-cffi-flow.svg)

---

## 2. 串口 / UART 通信

### 位置
- Python：`klippy/serialhdl.py`
- C 底层：`src/generic/serial_irq.c`
- 各平台实现：`src/*/serial.c`

### 工作原理

主机（如树莓派）通过串行连接与微控制器通信，可以是：

- **UART（TTL 串口）**：直接基于 GPIO 的串口通信
- **USB CDC ACM**：通过 USB 的虚拟串口
- **CAN 总线（Controller Area Network）**：使用 `python-can` 库

### 建立连接

```python
# 在 serialhdl.py 中
import serial
self.serial = serial.Serial(port, baudrate)
```

CAN 总线的连接方式：

```python
import can
self.can = can.interface.Bus(channel='can0', bustype='socketcan')
```

### C 端的串口处理

在微控制器端，串口数据接收是中断驱动的：

```c
// 在 src/generic/serial_irq.c 中
void serial_enable_receive(int fd) {
    // 启用 UART 接收中断
}
```

接收到的字节不断累积，然后传递给 `command_find_and_dispatch()`，
由它定位完整的消息块并分发其中的命令。

### 数据流：串口通信

![串口数据流](../img/zh/comm-serial-flow.svg)

---

## 3. 二进制消息协议（核心 RPC 层）

这是主机与微控制器之间**最重要的**通信机制。它是一个自定义二进制协议，
工作方式类似于远程过程调用（RPC，Remote Procedure Call）系统。

### 位置
- Python 编码/解码：`klippy/msgproto.py`
- C 编码/解码/分发：`src/command.c` + `src/command.h`

### 消息块格式

主机与 MCU 之间传输的每条消息都被封装在具有如下结构的消息块中：

```
偏移  大小  字段
─────────────────────────
 0     1    长度（总块大小，最小=5，最大=64）
 1     1    序列号（低 4 位序号 | 高 4 位 0x10）
 2     n    内容（VLQ 编码的命令/响应）
 2+n   2    CRC-16 CCITT 校验码
 2+n+2 1    同步字节 (0x7E)
```

**关键常量**（`msgproto.py` 和 `command.h` 中完全一致）：

| 常量 | 值 | 描述 |
|----------|-------|-------------|
| `MESSAGE_MIN` | 5 | 最小消息块大小（字节） |
| `MESSAGE_MAX` | 64 | 最大消息块大小（字节） |
| `MESSAGE_HEADER_SIZE` | 2 | 头部字节数（长度 + 序列号） |
| `MESSAGE_TRAILER_SIZE` | 3 | 尾部字节数（CRC16[2] + 同步字节） |
| `MESSAGE_SYNC` | 0x7E | 帧同步标记 |
| `MESSAGE_DEST` | 0x10 | 序列号字节的高 4 位固定值 |

### 可变长度数量（VLQ）编码

消息内容中的整数采用自定义 VLQ 方案编码，同时支持正数和负数：

| 整数范围 | 编码字节数 |
|---------------|---------------|
| -32 .. 95 | 1 字节 |
| -4096 .. 12287 | 2 字节 |
| -524288 .. 1572863 | 3 字节 |
| -67108864 .. 201326591 | 4 字节 |
| -2147483648 .. 4294967295 | 5 字节 |

**编码规则**：
- 每个字节低 7 位为数据位，最高位（MSB）为连续标志位
- 符号扩展在解码时处理
- 绝对值越小的整数占用的字节越少

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

| 类型名 | C 枚举值 | Python 类 | 描述 |
|-----------|--------|--------------|-------------|
| `%u` | `PT_uint32` | `PT_uint32` | 无符号 32 位整数 |
| `%i` | `PT_int32` | `PT_int32` | 有符号 32 位整数 |
| `%hu` | `PT_uint16` | `PT_uint16` | 无符号 16 位整数 |
| `%hi` | `PT_int16` | `PT_int16` | 有符号 16 位整数 |
| `%c` | `PT_byte` | `PT_byte` | 8 位字节 |
| `%s` | `PT_string` | `PT_string` | 动态长度字符串 |
| `%.*s` | `PT_progmem_buffer` | `PT_progmem_buffer` | Flash 中存储的缓冲区 |
| `%*s` | `PT_buffer` | `PT_buffer` | RAM 中的缓冲区 |

### 命令声明（C 端）

在 C 代码中使用 `DECL_COMMAND()` 宏来声明命令：

```c
DECL_COMMAND(command_update_digital_out,
             "update_digital_out oid=%c value=%c");
```

这会在编译后的固件中生成一个 `command_parser` 结构体：

```c
struct command_parser {
    uint16_t encoded_msgid;   // VLQ 编码的消息 ID
    uint8_t num_args;         // 函数参数个数
    uint8_t flags;            // 处理函数标志（如 HF_IN_SHUTDOWN）
    uint8_t num_params;       // 线路上传输的参数个数
    const uint8_t *param_types; // 参数类型枚举数组
    void (*func)(uint32_t *args); // 处理函数指针
};
```

### 响应发送（C 端）

使用 `sendf()` 宏发送响应：

```c
sendf("status clock=%u status=%c",
      sched_read_time(), sched_is_shutdown());
```

### 消息内容：一个块中包含多条命令

单个消息块可以包含多条命令：

```
人类可读形式：
  update_digital_out oid=6 value=1
  update_digital_out oid=5 value=0
  get_config
  get_clock

二进制形式（VLQ 整数序列）：
  <id_update_digital_out><6><1><id_update_digital_out><5><0><id_get_config><id_get_clock>
```

### CRC-16 CCITT 校验

收发双方使用完全相同的 CRC-16 CCITT 实现进行数据完整性校验：

```python
# Python 端 (msgproto.py)
def crc16_ccitt(buf):
    crc = 0xFFFF
    for data in buf:
        data ^= crc & 0xFF
        data ^= (data & 0x0F) << 4
        crc = ((data << 8) | (crc >> 8)) ^ (data >> 4) ^ (data << 3)
    return [crc >> 8, crc & 0xFF]
```

C 端的实现在各平台的板级支持代码中（例如 `src/generic/crc16_ccitt.c`）。

### 数据字典（识别协议）

当主机首次连接到 MCU 时，必须先下载**数据字典**。该字典将命令/响应的
格式字符串映射到其数值 ID。

1. 主机发送 `identify` 命令，分段请求数据
2. MCU 以 `identify_response` 响应，其中包含 zlib 压缩的 JSON 数据
3. JSON 数据经过 zlib 压缩后存储在 MCU 的 Flash 中
4. 主机收集全部分段后，解压并解析 JSON，获知所有可用的命令、响应、枚举和常量

`identify` 命令（ID=1）和 `identify_response`（ID=0）是仅有的两个
硬编码 ID 的消息。其余所有消息 ID 都是动态分配的。

### 确认与重传机制

**主机 → MCU**（可靠传输）：
- MCU 每正确接收一个消息块就回复一个 ACK
- 主机超时未收到 ACK 则自动重传
- MCU 检测到损坏或乱序的块时发送 NAK，触发快速重传
- 窗口机制允许多个消息块同时"在途"，充分利用带宽

**MCU → 主机**（尽力而为传输）：
- 不提供自动重传机制
- 上层代码需自行处理偶发的响应丢失（通常通过重新请求或设置周期性响应）
- 序列号字段仅用于跟踪主机发起的流量

---

## 4. API 服务器：Unix 域套接字 + JSON

### 位置
- Python：`klippy/webhooks.py`

### 工作原理

API 服务器通过 Unix 域套接字向外部工具提供打印机状态和控制的访问：

```python
# 在 webhooks.py 中
self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
self.sock.bind("/tmp/kalico_uds")
```

### 消息格式

消息是 JSON 编码的字符串，以 `0x03`（ETX，文终字符）作为分隔符：

```
<json_object_1><0x03><json_object_2><0x03>...
```

这使得 OctoPrint、Mainsail、Fluidd 等上位机工具能够与 Kalico 通信，
实现状态监控和远程控制。

---

## 5. 线程架构

Klippy 主机进程共使用 **4 个线程**：

| 线程 | 位置 | 职责 |
|--------|----------|---------|
| 主线程 | `klippy/gcode.py` | 处理传入的 G-code 命令 |
| 串口 I/O 线程 | `klippy/chelper/serialqueue.c` | 底层串口数据的收发 |
| 响应处理线程 | `klippy/serialhdl.py` | 处理来自 MCU 的响应消息 |
| 日志线程 | `klippy/queuelogger.py` | 非阻塞地写入调试日志 |

---

## 6. 完整数据流图

![完整架构](../img/zh/comm-full-architecture.svg)

---

## 7. 总结

| 层次 | Python 端 | C 端 | 格式 | 可靠性 |
|-------|-------------|--------|--------|-------------|
| **CFFI** | `chelper/__init__.py` | `chelper/*.c` | 直接函数调用 | 不适用（进程内） |
| **二进制协议** | `msgproto.py` | `command.c/h` | VLQ 整数 + CRC16 | ACK / 自动重传 |
| **串口传输** | `serialhdl.py` | `serial_irq.c` | UART/CAN/USB 上的原始字节 | 取决于硬件 |
| **API 服务器** | `webhooks.py` | 不适用 | Unix 套接字上的 JSON + ETX | TCP 级可靠 |
| **数据字典** | `msgproto.py`（解析） | `compile_time_request.c`（生成） | Zlib 压缩的 JSON | 连接时完成识别 |

### 关键设计原则

1. **最小化 MCU 复杂度**：MCU 使用静态（编译时）数据字典，主机负责适配
   MCU 提供的任何内容。
2. **带宽效率**：VLQ 编码让常见的小值只占极少字节，多条命令可打包进
   同一个消息块。
3. **错误检测**：CRC-16 CCITT 捕获数据损坏，序列号检测乱序到达。
4. **关注点分离**：CFFI 负责计算，串口负责传输，msgproto 负责编解码，
   API 服务器负责外部访问。
5. **性能关键路径用 C 实现**：步进压缩、迭代求解、串口 I/O 均在 C 中
   实现以获得极致速度，而高层逻辑保留在 Python 中以获得灵活性。

---

## 参见

- [协议](Protocol.md) — 主机↔MCU 二进制协议详解
- [代码概览](Code_Overview.md) — 整体代码结构
- [MCU 命令](MCU_Commands.md) — 可用的 MCU 命令列表
- [调试](Debugging.md) — 如何查看协议消息
