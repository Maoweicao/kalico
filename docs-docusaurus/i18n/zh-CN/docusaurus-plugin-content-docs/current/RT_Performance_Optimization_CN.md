# 实时性能优化

Kalico 的主机端运动管线已通过三层实时性改进进行了优化。本文档描述了架构、所做的更改，以及如何配�?PREEMPT_RT 内核以获得最大收益�?

## 架构

Kalico 中的运动时序管线如下�?

```
G代码解析 (Python, ~ms/�?
  -> 前瞻 + 拐角速度规划 (Python, ~us)
  -> trapq_append (C) �?梯形速度队列
  -> itersolve (C) �?割线法迭代步进时刻求�?
  -> stepcompress (C) �?步进脉冲压缩/排队
  -> serialqueue (C, 后台线程) �?定时串口/CAN 发送至 MCU
  -> UART/CAN 硬件
```

所有性能关键 C 代码通过 CFFI 在运行时编译�?`c_helper.so`�?
时序瓶颈在于 **serialqueue 后台线程**，它必须在微秒级响应硬件和定时器事件，以�?MCU 缓冲区欠载�?

## 已实施的更改

### 1. poll() �?epoll + timerfd (`pollreactor.c`)

**问题�?* 原先�?`pollreactor` 使用 `poll()`，超时精度为毫秒级（最�?1ms）。定时器回调�?`poll()` 返回*之后*才检查，引入了不可避免的调度抖动�?

**解决方案�?* �?Linux 上（`#ifdef __linux__`），事件循环现在使用�?
- `epoll_create1` / `epoll_wait` �?O(1) 事件驱动分发
- `timerfd_create` / `timerfd_settime` �?纳秒级定时器精度
  - 每个定时器回调拥有独立的 `timerfd` 文件描述�?
  - `epoll_wait` �?timerfd 到期时直接唤�?
  - 无需手动计算超时或轮�?

**回退方案�?* �?Linux 平台（macOS、BSD）保留原�?`poll()` 实现以保持兼容性�?

| 指标 | 修改�?(`poll()`) | 修改�?(`epoll`+`timerfd`) |
|------|-------------------|---------------------------|
| 定时器精�?| 1 ms | 1 ns |
| FD 分发方式 | O(n) 扫描 | O(1) 事件驱动 |
| 空闲 CPU 开销 | 最�?1000�?秒唤�?| 空闲�?0 次唤�?|

### 2. 实时线程调度 (`serialqueue.c`)

**问题�?* 串口后台线程以默认的 `SCHED_OTHER` 调度类别运行，与 Python 线程、文件系统刷新、网�?I/O 和其他系统任务平等竞争。在繁忙系统上，这可能导致串行数据延迟数十毫秒�?

**解决方案�?* 线程创建后，后台线程被提升为 `SCHED_FIFO` 优先级：

```c
struct sched_param sp;
sp.sched_priority = 1;
pthread_setschedparam(sq->tid, SCHED_FIFO, &sp);
```

- �?**PREEMPT_RT** 内核上，这将串行线程调度到所�?`SCHED_OTHER` 任务之上，确保及时执行�?
- �?*标准** Linux 内核上，`pthread_setschedparam` 会静默忽略此请求（或需�?`CAP_SYS_NICE`），安全回退�?`SCHED_OTHER`�?

### 3. 优先级继承互斥锁 (`serialqueue.c`)

**问题�?* Python 主线程和 C 串行线程共享互斥锁（`sq->lock`、`sq->fast_reader_dispatch_lock`）。当 Python 持有互斥锁且高优先级的串行线程阻塞时，会发生优先级反转——Python 线程以低优先级运行，导致互斥锁无法快速释放�?

**解决方案�?* 互斥锁使�?`PTHREAD_PRIO_INHERIT` 初始化：

```c
pthread_mutexattr_t mutex_attr;
pthread_mutexattr_init(&mutex_attr);
pthread_mutexattr_setprotocol(&mutex_attr, PTHREAD_PRIO_INHERIT);
pthread_mutex_init(&sq->lock, &mutex_attr);
```

- �?**PREEMPT_RT** 内核上，Python 线程在持锁期间临时继承串行线程的高优先级，消除优先级反转�?
- �?*标准**内核上，`PTHREAD_PRIO_INHERIT` 是安全的无操作指令�?

## PREEMPT_RT 内核配置

要充分发挥这些优化的效果，请在主机（通常是树莓派）上安装 PREEMPT_RT 补丁内核�?

### 内核命令行参�?

添加�?`/boot/cmdline.txt`（树莓派）或 `/etc/default/grub`（`GRUB_CMDLINE_LINUX`）：

```
isolcpus=3 nohz_full=3 rcu_nocbs=3 irqaffinity=0-2
```

| 参数 | 作用 |
|------|------|
| `isolcpus=3` | �?CPU 核心 3 从通用内核调度中隔�?|
| `nohz_full=3` | 核心 3 空闲或单任务时禁用调度器 tick |
| `rcu_nocbs=3` | 从核�?3 卸载 RCU 回调 |
| `irqaffinity=0-2` | 将所有硬件中断路由到核心 0-2 |

### �?Klipper 绑定到隔离核�?

�?Klipper 服务单元文件中（�?`/etc/systemd/system/klipper.service`）：

```ini
[Service]
CPUAffinity=3
```

### 内核编译选项

编译自定义内核时必要�?PREEMPT_RT 配置�?

```
CONFIG_PREEMPT_RT_FULL=y
CONFIG_HZ=1000
CONFIG_HIGH_RES_TIMERS=y
CONFIG_CPU_ISOLATION=y
CONFIG_NO_HZ_FULL=y
```

## 预期改进

| 指标 | 标准内核 | + epoll/timerfd | + SCHED_FIFO | + PREEMPT_RT |
|------|---------|-----------------|--------------|--------------|
| 定时器唤醒精�?| ~1 ms | ~10 us | ~10 us | ~5 us |
| 定时器唤醒抖�?| +/- 5 ms | +/- 100 us | +/- 50 us | +/- 10 us |
| 串行线程抢占延迟 | 0-50 ms | 0-50 ms | 0-5 ms | < 100 us |
| 互斥锁优先级反转 | 可能 | 可能 | 减少 | 消除 |
| MCU 缓冲欠载风险 | 中等 | �?| 极低 | 近乎为零 |

## 兼容�?

- **Linux（树莓派 OS、Armbian 等）�?* 完整�?epoll/timerfd + RT 支持�?
- **macOS / BSD�?* 回退到原�?`poll()` 实现。SCHED_FIFO �?PI 互斥锁为无操作�?
- **Windows�?* 不推荐也不支持作�?Klipper 主机�?

## 代码变更摘要

| 文件 | 变更 |
|------|------|
| `klippy/chelper/pollreactor.c` | Linux 路径：epoll + timerfd。非 Linux：原�?poll() |
| `klippy/chelper/serialqueue.c` | `#include <sched.h>`，PI 互斥锁初始化，SCHED_FIFO 线程 |
| `klippy/chelper/pollreactor.h` | �?API 变更（完全兼容） |
| `klippy/chelper/__init__.py` | 无需变更 |

## 参考资�?

- [Linux PREEMPT_RT Wiki](https://wiki.linuxfoundation.org/realtime/)
- [timerfd_create(2) 手册页](https://man7.org/linux/man-pages/man2/timerfd_create.2.html)
- [epoll(7) 手册页](https://man7.org/linux/man-pages/man7/epoll.7.html)
- Klipper/Kalico 串行队列架构：`klippy/chelper/serialqueue.c`
