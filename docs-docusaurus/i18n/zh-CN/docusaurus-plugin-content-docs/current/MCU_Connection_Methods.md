# MCU 连接方法

本文档描述了微控制器（MCU）可以连接到 Kalico 主机（`klippy`）的所有方式，包括其内部架构、配置和权衡。

---

## 概述

Kalico 支持**六种不同的传输方法**用于 MCU 到主机的通信。每种方法最终为 C 级 `serialqueue.c` 传输层提供文件描述符（fd），该层处理消息帧、命令队列、重传和时钟同步。

| # | 方法 | 配置键 | 传输 | 拓扑 |
|---|--------|-----------|-----------|----------|
| 1 | **UART/串口** | `serial` + `baud` | USB CDC ACM / 物理 UART | 点对点 |
| 2 | **CAN 总线** | `canbus_uuid` | SocketCAN | 多点总线 |
| 3 | **管道 / PTY** | `serial`（无 baud） | 命名管道 / PTY | 本地 IPC |
| 4 | **TCP** | `tcp_host` + `tcp_port` | TCP/IP 流 | 网络（有线/WiFi） |
| 5 | **UDP** | `udp_host` + `udp_port` | UDP/IP 数据报 | 网络（有线/WiFi） |
| 6 | **调试文件** | CLI 参数 | 文件回放 | 离线调试 |

---

## 内部架构

通信栈有三层：

```
klippy/mcu.py          ── 配置、连接/断开逻辑
klippy/serialhdl.py    ── 传输适配器（UART、CAN、TCP、UDP、Pipe、File）
klippy/chelper/serialqueue.c ── 底层 I/O、重传、时钟跟踪
```

C 传输层（`serialqueue.c`）定义了四种内部 fd 类型：

| 常量 | 值 | 描述 |
|----------|-------|-------------|
| `SQT_UART` | `'u'` | 串口设备上的字节流 |
| `SQT_CAN` | `'c'` | 通过 SocketCAN 的 CAN 帧 |
| `SQT_DEBUGFILE` | `'f'` | 基于文件的回放 |
| `SQT_TCP` | `'t'` | TCP 套接字上的字节流 |
| `SQT_UDP` | `'d'` | UDP 套接字上的数据报 |

传输层使用 Linux epoll（或其他平台上的 poll）进行异步 I/O，具有以实时优先级（`SCHED_FIFO`）运行的专用后台线程。

---

## 1. UART / 串口（USB）

最常见的连接方式。MCU 以 USB CDC ACM 设备枚举或通过物理 UART 通信。

### 配置

```ini
[mcu]
serial: /dev/serial/by-id/usb-Klipper_stm32f103xe_12345-if00
baud: 250000
restart_method: arduino
```

### 工作原理

- **主机**：通过 Python `pyserial` 打开串口，将 fd 传递给 `serialqueue_alloc(fd, 'u', 0)`。
- **C 层**：读取原始字节，通过 `msgblock_check()` 处理消息帧。通过 `write()` 写入原始字节。重传时，调用 `tcflush(TCOFLUSH)` 刷新 UART 输出缓冲区。
- **固件**：`src/generic/serial_irq.c` 处理每字节的中断驱动 RX/TX。平台特定的 `serial.c` 提供硬件接口。

### 重启方法

| 方法 | 描述 |
|--------|-------------|
| `arduino` | 切换 DTR 线（Arduino/STM32 板常用） |
| `cheetah` | Fysetc Cheetah 板的特殊序列 |
| `command` | 发送 Klipper 协议重置命令 |
| `rpi_usb` | 通过 `hub-ctrl` 切换 USB 端口电源 |

---

## 2. CAN 总线

使用 Linux 上 SocketCAN 的多点总线。支持单个接口上的多个设备，每个设备由 UUID 标识。

### 配置

```ini
[mcu]
canbus_uuid: 0a1b2c3d4e5f
canbus_interface: can0
```

### 工作原理

- **主机**：使用 Python `python-can` 库（`bustype=socketcan`）。发送 `CMD_SET_NODEID` 管理帧（CAN ID `0x3F0`）来分配节点 ID。将 CAN 套接字 fd 作为 `serialqueue_alloc(fd, 'c', txid)` 传递。
- **C 层**：从套接字读取 `struct can_frame`（最大 8 字节）。将输出拆分为 8 字节 CAN 帧进行写入。
- **固件**：`src/generic/canserial.c` 实现 CAN 串口协议。`src/generic/canbus.c` 封装平台 CAN 硬件。

### 工具

- `scripts/canbus_query.py` - 发现 CAN 总线设备及其 UUID
- `klippy/extras/canbus_ids.py` - 跟踪 CAN 节点 ID 分配
- `klippy/extras/canbus_stats.py` - 报告 CAN 总线状态/错误

### CAN 总线桥接

`src/generic/usb_canbus.c` 使用 Linux `gs_usb` 协议实现 USB 转 CAN 桥接。这允许 MCU 充当其他 CAN 设备的 USB CAN 适配器。

---

## 3. 管道 / PTY（Linux 进程 MCU）

用于"主机 MCU"（Linux 进程）或基于 PRU 的设备（BeagleBone）。数据通过本地管道或伪终端传递，无需硬件串口开销。

### 配置

```ini
[mcu host]
serial: /tmp/klipper_host_mcu
```

### 工作原理

- **主机**：使用 `os.open(path, O_RDWR | O_NOCTTY)` 打开文件。将 fd 作为 `serialqueue_alloc(fd, 'u', 0)` 传递。跳过波特率配置。
- **固件**：`src/linux/console.c` 通过 `openpty()` 创建 PTY。`src/linux/main.c` 默认使用 `/tmp/klipper_host_mcu`。

### 检测

以 `/dev/rpmsg_` 或 `/tmp/klipper_host_` 开头的路径会自动被视为管道连接（无需 baud）。

---

## 4. TCP（网络流）

通过 TCP/IP 网络连接到 MCU。适用于有线以太网或 WiFi 连接。MCU 必须运行 TCP 服务器（原生或通过桥接设备）。

### 配置

```ini
[mcu]
tcp_host: 192.168.1.100
tcp_port: 5500
```

### 工作原理

- **主机**：创建启用 `TCP_NODELAY` 的 TCP 套接字（禁用 Nagle 算法以实现低延迟）。连接到 `host:port`。将套接字 fd 作为 `serialqueue_alloc(fd, 't', 0)` 传递。
- **C 层**：通过套接字读取/写入原始字节，与 UART 流模式相同。无 `tcflush`（不适用于套接字）。
- **重启方法**：始终为 `command`（物理重置方法无法通过网络工作）。

### 连接生命周期

1. Klippy 解析主机名并尝试 TCP 连接
2. 成功后，开始协议握手（数据字典交换）
3. 失败后，每 5 秒重试一次，最多 90 秒
4. 如果连接断开，Klippy 检测到 EOF 并触发重连

### 固件选项

**选项 A：桥接设备**（对现有 MCU 零固件更改）

```
MCU (STM32/AVR/...) ──UART──► ESP32/RPi (桥接) ──TCP──► Klippy
```

桥接运行 TCP 转 UART 代理。MCU 固件不变。桥接设备处理 WiFi/以太网连接，并通过 TCP 暴露 MCU 的 UART 数据流。

**选项 B：固件中的原生 TCP**

MCU 固件直接实现 TCP/IP 协议栈。示例：
- STM32 + W5500 以太网模块（基于 SPI）
- 带内置 WiFi 的 ESP32
- 带内置 TCP 协议栈的 Linux MCU

### 示例：ESP32 TCP 转 UART 桥接（伪代码）

```c
void app_main() {
    wifi_connect("SSID", "password");
    int server = tcp_listen(5500);
    int client = tcp_accept(server);
    uart_init(115200);

    while (1) {
        // TCP → UART
        uint8_t buf[256];
        int len = tcp_read(client, buf, sizeof(buf));
        if (len > 0) uart_write(buf, len);

        // UART → TCP
        len = uart_read(buf, sizeof(buf));
        if (len > 0) tcp_write(client, buf, len);
    }
}
```

---

## 5. UDP（网络数据报）

通过 UDP/IP 连接到 MCU。适用于 TCP 连接开销不理想或底层链路本质上是基于数据报的场景。

### 配置

```ini
[mcu]
udp_host: 192.168.1.100
udp_port: 5500
```

### 工作原理

- **主机**：创建已连接的 UDP 套接字。将套接字 fd 作为 `serialqueue_alloc(fd, 'd', 0)` 传递。
- **C 层**：在已连接的 UDP 套接字上 `read()` 返回一个数据报的数据量。`write()` 将缓冲区作为单个 UDP 数据报发送。最大写缓冲区大小为 `MESSAGE_MAX (64) * MAX_PENDING_BLOCKS (12) = 768 字节`，远在 UDP 的 65507 字节限制内。
- **可靠性**：UDP 不保证传递。Klipper 协议的内置序列号和重传机制在应用层处理丢失的数据报。
- **重启方法**：始终为 `command`。

### 连接生命周期

1. Klippy"连接" UDP 套接字（设置默认对等地址，不发送数据包）
2. 成功后，开始协议握手
3. 失败后，每 5 秒重试一次，最多 90 秒
4. UDP 是无连接的，因此无法在传输层检测到"断开连接"。协议的重传超时处理此问题。

### 何时使用 UDP 与 TCP

| 方面 | TCP | UDP |
|--------|-----|-----|
| 可靠性 | 保证传递 | 尽力而为 |
| 排序 | 有序 | 无排序保证 |
| 连接状态 | 面向连接 | 无连接 |
| 延迟 | 较高（TCP 级别重传） | 较低 |
| 开销 | 连接建立 + 拆除 | 最小 |
| 用例 | 通用远程 MCU | 低延迟，仅限局域网 |

---

## 6. 调试文件（离线回放）

用于离线调试。Klippy 从文件读取预录制的串口流量，而不是连接到真实硬件。

### 用法

```bash
klippy.py --debugoutput=/tmp/klipper.log --dictionary=/tmp/dict.bin
```

### 工作原理

- **主机**：打开调试输出和字典文件。直接处理字典。创建 `serialqueue_alloc(fd, 'f', 0)`。
- **C 层**：设置 `receive_seq = -1`（无需消息同步）和 `rto = PR_NEVER`（无需重传）。从文件读取预录制数据。

---

## 连接选择流程

MCU 初始化代码根据配置文件参数选择传输方法，按以下顺序评估：

1. 设置了 `tcp_host` → **TCP**
2. 设置了 `udp_host` → **UDP**
3. 设置了 `canbus_uuid` → **CAN 总线**
4. 设置了 `serial`，以 `/dev/rpmsg_` 或 `/tmp/klipper_host_` 开头 → **管道 / PTY**
5. 设置了 `serial`，其他路径 → **UART / 串口**

这些选项互斥。每个 `[mcu]` 节只能指定一种连接方法。

---

## 多 MCU 设置

Kalico 支持单台打印机中的多个 MCU。每个 MCU 节可以使用不同的传输方法：

```ini
# 主板通过 USB
[mcu]
serial: /dev/serial/by-id/usb-main_board

# 工具头板通过 CAN
[mcu toolhead]
canbus_uuid: 1a2b3c4d5e6f

# 加速度计通过 TCP（WiFi）
[mcu accelerometer]
tcp_host: 192.168.1.200
tcp_port: 5500
is_non_critical: True
```

主 `[mcu]` 节不能标记为非关键。辅助 MCU 可以使用 `is_non_critical: True` 来允许断开连接而不停止打印机。

---

## 代码参考

### 主机端（Python）

| 文件 | 角色 |
|------|------|
| `klippy/mcu.py` | MCU 类、连接/断开逻辑、配置解析 |
| `klippy/serialhdl.py` | 包含所有传输适配器的 SerialReader 类 |
| `klippy/chelper/serialqueue.c` | C 级 I/O、重传、线程 |
| `klippy/chelper/serialqueue.h` | C API 头文件 |
| `klippy/chelper/pollreactor.c` | epoll/poll 事件循环 |

### 固件端（C）

| 文件 | 角色 |
|------|------|
| `src/generic/serial_irq.c` | UART 传输的中断驱动串口 |
| `src/generic/canserial.c` | CAN 总线串口协议 |
| `src/generic/canbus.c` | CAN 硬件抽象 |
| `src/generic/usb_canbus.c` | USB 转 CAN 桥接 |
| `src/linux/console.c` | Linux MCU 的 PTY 控制台 |
| `src/linux/main.c` | Linux MCU 入口点 |
| `src/*/serial.c` | 平台特定的 UART 硬件驱动 |

### 工具

| 文件 | 角色 |
|------|------|
| `scripts/canbus_query.py` | CAN 总线设备扫描器 |
| `scripts/console.py` | 调试控制台（支持所有传输） |
| `other/mcu_sim/` | 带 TCP 支持的 MCU 模拟器，用于测试 |
