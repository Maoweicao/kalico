# Klipper klippy 上位机重构可行性分析

> 分析日期: 2026-06-03
> 目的: 评估在 klippy (Python 上位机) 层面进行重构的可行性，
>        作为下位机 (C 固件) 重构不顺利时的备选方案。

## 1. 架构概览

Klipper 采用"上位机计算 + 下位机执行"的架构：

```
┌─────────────────────────────────────────────────────────┐
│  klippy (Python 上位机)                                  │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │
│  │ toolhead │→ │ stepper   │→ │ stepcompress (C FFI) │  │
│  │ (运动规划) │  │ (步进接口) │  │ (step→命令压缩)      │  │
│  └──────────┘  └───────────┘  └─────────┬────────────┘  │
│                                         ↓               │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │
│  │ clocksync│  │ serialhdl │→ │ serialqueue (C FFI)  │  │
│  │ (时钟同步) │  │ (串口管理) │  │ (底层串口收发)       │  │
│  └──────────┘  └───────────┘  └─────────┬────────────┘  │
└─────────────────────────────────────────┼───────────────┘
                                          ↓ (UART/CAN/USB)
┌─────────────────────────────────────────────────────────┐
│  MCU 固件 (C)                                            │
│  ┌──────────┐  ┌───────────┐  ┌──────────────────────┐  │
│  │ sched    │→ │ stepper   │→ │ timer IRQ            │  │
│  │ (调度器)  │  │ (步进执行) │  │ (硬件定时器)         │  │
│  └──────────┘  └───────────┘  └──────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

## 2. 关键模块分析

### 2.1 MCU 连接与配置 (`mcu.py`)

**连接流程:**
1. `MCU.__init__()` 读取配置 (serial/baud/canbus_uuid)
2. 创建 `SerialReader` 对象处理串口通信
3. `_mcu_identify()` 阶段：
   - 根据配置选择连接方式：`connect_uart()` / `connect_canbus()` / `connect_pipe()`
   - 调用 `ClockSync.connect()` 建立时钟同步
4. 从 MCU 固件读取数据字典 (identify 命令)，获取所有可用命令和常量
5. `_connect()` 阶段：
   - 发送配置命令 (`config_stepper`, `config_digital_out` 等)
   - 通过 `finalize_config` CRC 校验确认配置一致
   - 创建 `steppersync` 对象管理步进命令队列

**关键常量 (从 MCU 固件获取):**
- `CLOCK_FREQ`: MCU 主时钟频率 (如 16MHz, 72MHz, 120MHz)
- `SERIAL_BAUD`: 串口波特率
- `STATS_SUMSQ_BASE`: 统计信息基数
- `RECEIVE_WINDOW`: 接收窗口大小
- `ADC_MAX`: ADC 最大值
- `PWM_MAX`: PWM 最大值

**关键配置参数 (用户可调):**
| 参数 | 默认值 | 说明 |
|------|--------|------|
| `serial` | 必填 | 串口设备路径 |
| `baud` | 250000 | 串口波特率 (最低 2400) |
| `canbus_uuid` | 无 | CAN 总线 UUID |
| `canbus_interface` | can0 | CAN 接口名 |
| `restart_method` | command | 重启方式: None/arduino/cheetah/command/rpi_usb |
| `max_stepper_error` | 0.000025 | 最大步进误差 (秒) |
| `is_non_critical` | False | 是否为非关键 MCU |
| `reconnect_interval` | 2.0 | 重连间隔 (秒) |

### 2.2 步进电机命令发送 (`stepper.py`)

**命令流水线:**

```
G-code → toolhead → trapq (梯形运动队列)
    → itersolve (迭代求解步进时刻)
    → stepcompress (压缩为 queue_step 命令)
    → steppersync_flush (通过 serialqueue 发送到 MCU)
```

**`queue_step` 命令格式:**
```
queue_step oid=%c interval=%u count=%hu add=%hi
```
- `oid`: 步进电机对象 ID
- `interval`: 步进间隔 (MCU 时钟 ticks)
- `count`: 步进次数
- `add`: 间隔增量 (用于加速/减速)

**`set_next_step_dir` 命令:**
```
set_next_step_dir oid=%c dir=%c
```

**`reset_step_clock` 命令:**
```
reset_step_clock oid=%c clock=%u
```

**MCU_stepper._build_config() 中的能力检测:**
```python
constants = self._mcu.get_constants()
ssbe = int(constants.get("STEPPER_STEP_BOTH_EDGE", "0"))  # 新版双边沿步进
sbe = int(constants.get("STEPPER_BOTH_EDGE", "0"))         # 旧版双边沿
sou = int(constants.get("STEPPER_OPTIMIZED_UNSTEP", "0"))  # 优化的取消步进
```
这些常量决定了 klippy 是否启用双边沿步进模式，已有 MCU 能力适配机制。

### 2.3 时钟同步 (`clocksync.py`)

**ClockSync (主 MCU):**
- 使用线性回归持续校准 MCU 时钟与系统时间的映射
- 每 ~1 秒发送 `get_clock` 查询 MCU 当前时钟
- 通过最小 RTT (Round-Trip Time) 补偿通信延迟
- 丢弃异常值 (>25 标准差) 保证同步精度

**SecondarySync (次 MCU):**
- 继承 ClockSync，额外计算与主 MCU 的时钟偏移
- `calibrate_clock()` 持续调整频率使所有 MCU 时钟同步
- 支持不同频率的 MCU 共存

**关键限制:**
```python
MIN_SCHEDULE_TIME = 0.100      # 上位机最少需要 100ms 提前量
MAX_SCHEDULE_TICKS = (1 << 31) - 1  # 32 位有符号整数最大值
MAX_NOMINAL_DURATION = 3.0     # 最大可调度 3 秒的步进命令
```

### 2.4 Shutdown 处理

**流程:**
1. MCU 固件检测到错误 → 发送 `shutdown` 消息
2. `MCU._handle_shutdown()` 捕获消息：
   - 设置 `_is_shutdown = True`
   - 记录 shutdown 时钟和消息
   - 调用 `printer.invoke_async_shutdown()` 触发全局关机
3. 常见错误消息及含义 (在 `Common_MCU_errors` 中定义):
   - `"Timer too close"`: 上位机过载或 MCU 调度溢出
   - `"Missed scheduling of next "`: 通信中断
   - `"Rescheduled timer in the past"` / `"Stepper too far in past"`: MCU 步进速率超出能力

**自动恢复机制:**
- `clear_shutdown` 命令可清除 shutdown 状态
- 非关键 MCU 支持断线重连 (`non_critical_recon_event`)

### 2.5 串口通信 (`serialhdl.py`)

**底层实现:**
- 使用 C FFI (`serialqueue`) 管理串口收发
- 后台线程 (`_bg_thread`) 持续从 serialqueue 拉取消息
- 支持 UART、CAN、Pipe 三种连接方式
- 消息路由通过 `(name, oid)` 元组索引回调函数

**命令发送方式:**
- `raw_send()`: 无等待发送
- `raw_send_wait_ack()`: 等待确认
- `send_with_response()`: 带重试的请求-响应模式

## 3. klippy 层面重构可行性评估

### 3.1 多种命令模式（中断模式 vs 轮询模式）

**可行性: 中等**

当前架构中，klippy 发送的 `queue_step` 命令本质上是"预调度"模式——上位机提前计算好每一步的时间戳，MCU 按时间戳执行。这既不是纯粹的中断模式也不是轮询模式。

**在 klippy 层面可做的调整:**
- **批量发送 vs 实时发送**: 当前通过 `steppersync_flush` 批量发送，可以调整批量大小
- **发送频率**: 修改 `MOVE_BATCH_TIME` (toolhead.py) 和 `STEPCOMPRESS_FLUSH_TIME` 控制命令刷新频率
- **命令窗口大小**: 当前 `MAX_NOMINAL_DURATION = 3.0` 秒，可以减小以降低 MCU 内存需求

**限制:**
- klippy 无法改变 MCU 固件的命令执行模式
- 中断/轮询的选择完全在 MCU 固件侧

**推荐方案:**
```python
# 可在 MCU 配置中添加参数控制命令发送策略
# [mcu]
# command_buffer_time = 0.5    # 命令缓冲时间 (影响批量大小)
# step_flush_interval = 0.05   # 步进命令刷新间隔
```

### 3.2 根据 MCU 能力自动切换调度策略

**可行性: 高**

klippy 已经有 MCU 能力检测机制 (通过 `get_constants()`)。可以扩展此机制：

**当前已有的能力检测:**
- `STEPPER_STEP_BOTH_EDGE`: 双边沿步进支持
- `STEPPER_BOTH_EDGE`: 旧版双边沿
- `STEPPER_OPTIMIZED_UNSTEP`: 优化取消步进
- `CLOCK_FREQ`: 时钟频率
- `SERIAL_BAUD`: 波特率

**可扩展的能力检测:**
```python
# 在 MCU._mcu_identify() 中添加
mcu_type = msgparser.get_constant("MCU_TYPE", "unknown")
timer_bits = msgparser.get_constant("TIMER_BITS", 32)
max_stepper_rate = msgparser.get_constant("MAX_STEPPER_RATE", 0)
step_buffer_size = msgparser.get_constant("STEP_BUFFER_SIZE", 0)

# 根据能力调整策略
if max_stepper_rate > 0 and max_stepper_rate < 100000:
    # 低性能 MCU: 降低命令发送频率，增大命令间隔
    self._low_perf_mode = True
```

**实现方式:**
1. 在 MCU 固件编译时嵌入能力常量 (如 `MAX_STEPPER_RATE`, `TIMER_BITS`)
2. klippy 在 `_mcu_identify()` 阶段读取这些常量
3. 根据常量自动调整：
   - `max_stepper_error`: 低性能 MCU 使用更大的容错值
   - `step_pulse_duration`: 根据 MCU 速度调整脉冲宽度
   - 命令缓冲策略

### 3.3 为低性能 MCU 优化命令发送频率

**可行性: 高**

这是 klippy 层面最容易实现的优化。

**当前的关键参数:**
```python
# mcu.py
MIN_SCHEDULE_TIME = 0.100      # 100ms 提前量
MAX_NOMINAL_DURATION = 3.0     # 最大 3 秒调度窗口

# toolhead.py
BUFFER_TIME_START = 0.250      # 初始缓冲时间
MOVE_BATCH_TIME = 0.500        # 运动批量时间
STEPCOMPRESS_FLUSH_TIME = 0.050  # 步进压缩刷新时间
```

**优化策略:**

1. **增大命令间隔**: 对于 ATmega328P (16MHz)，可以增大 `MIN_SCHEDULE_TIME` 到 200-300ms
2. **降低步进频率**: 通过增大 `step_pulse_duration` 降低有效步进率
3. **减少命令队列深度**: `move_count` 由 MCU 固件报告，但可以预留更多 slots
4. **批量发送优化**: 增大 `MOVE_BATCH_TIME` 减少通信频率

**具体实现:**
```python
# 在 MCU 类中添加低性能模式
class MCU:
    def _apply_low_perf_optimizations(self):
        mcu_freq = self._mcu_freq
        if mcu_freq < 20000000:  # < 20MHz
            # 增大调度提前量
            self._min_schedule_time = 0.200
            # 降低最大步进误差容限
            self._max_stepper_error = 0.000050
        elif mcu_freq < 50000000:  # < 50MHz
            self._min_schedule_time = 0.150
```

**效果预估:**
- ATmega328P (16MHz): 可支持约 5000-8000 步/秒 (当前 AVR 328P 限制)
- ATmega2560 (16MHz): 可支持约 15000-20000 步/秒
- STM32F103 (72MHz): 可支持约 100000+ 步/秒

### 3.4 在上位机层面补偿下位机定时器精度不足

**可行性: 低**

这是最具挑战性的需求。当前架构的核心设计假设是 MCU 有精确的硬件定时器。

**当前补偿机制:**
- `stepcompress` (C 代码) 已经在上位机侧做了步进时间压缩
- `max_stepper_error` 参数定义了可接受的时间误差
- `ClockSync` 使用线性回归持续校准时钟映射

**为什么上位机补偿困难:**

1. **通信延迟不可控**: UART 通信有 0.5-5ms 的延迟抖动，CAN 总线更严重
2. **命令执行不可抢占**: MCU 按 `queue_step` 的时间戳执行，无法在运行时调整
3. **定时器精度是硬约束**: ATmega328P 的 16 位定时器，16MHz 下精度为 62.5ns，但调度粒度受中断延迟影响 (~4-10μs)

**可能的补偿策略 (有限效果):**

1. **增大 max_stepper_error**:
   ```python
   # 接受更大的时间误差，减少 "Timer too close" 错误
   # 代价: 打印精度降低
   max_stepper_error: 0.000100  # 100μs (默认 25μs)
   ```

2. **降低最大步进率**: 在运动规划阶段限制速度
   ```python
   # 通过 printer.cfg 限制
   max_velocity: 200      # 降低最大速度
   max_accel: 1000        # 降低最大加速度
   ```

3. **使用更大的 step_pulse_duration**: 给 MCU 更多处理时间
   ```python
   step_pulse_duration: 0.000005  # 5μs (默认 2μs)
   ```

4. **预补偿通信延迟** (理论可行但效果有限):
   - 在 `print_time_to_clock()` 中加入通信延迟补偿
   - 问题: 延迟不恒定，补偿可能引入新误差

**结论**: 上位机无法真正补偿 MCU 定时器精度不足。步进时序必须由 MCU 精确控制，上位机只能通过降低性能要求来适应低精度 MCU。

## 4. 改造方案对比

| 方案 | 改动范围 | 难度 | 效果 | 风险 |
|------|----------|------|------|------|
| A. 下位机重构 (当前方案) | MCU C 固件 | 高 | 最佳 | 高 |
| B. klippy 添加低性能适配 | klippy Python | 中 | 良好 | 低 |
| C. klippy + 简化固件 | 两边 | 中 | 良好 | 中 |
| D. 完全自定义上位机 | 全新 | 极高 | 理论最佳 | 极高 |

## 5. 推荐的 klippy 侧改造方案 (方案 B/C)

### 5.1 最小改动方案 (仅 klippy)

**改动文件:**
- `klippy/mcu.py`: 添加 MCU 能力检测和自适应参数
- `klippy/stepper.py`: 根据 MCU 能力调整 step_pulse 和 both_edge 设置
- `klippy/toolhead.py`: 添加低性能 MCU 的缓冲策略

**具体改动:**

```python
# mcu.py - MCU._mcu_identify() 中添加
def _detect_mcu_capabilities(self):
    """检测 MCU 能力并设置优化参数"""
    constants = self.get_constants()
    mcu_freq = self._mcu_freq
    
    # 检测 MCU 类型
    self._timer_bits = int(constants.get("TIMER_BITS", "32"))
    self._max_stepper_rate = int(constants.get("MAX_STEPPER_RATE", "0"))
    self._step_buffer_size = int(constants.get("STEP_BUFFER_SIZE", "0"))
    
    # 根据能力调整参数
    if mcu_freq < 20000000:  # < 20MHz (如 ATmega328P)
        self._low_perf_mode = True
        self._min_schedule_time = 0.200
        self._max_stepper_error = max(self._max_stepper_error, 0.000050)
    elif mcu_freq < 50000000:  # < 50MHz (如 STM32F103)
        self._low_perf_mode = True
        self._min_schedule_time = 0.150
    else:
        self._low_perf_mode = False
```

```python
# stepper.py - MCU_stepper._build_config() 中添加
def _build_config(self):
    # ... 现有代码 ...
    
    # 低性能 MCU 优化
    if self._mcu._low_perf_mode:
        # 强制禁用双边沿步进 (减少 MCU 处理负担)
        self._step_both_edge = False
        # 增大脉冲宽度
        self._step_pulse_duration = max(self._step_pulse_duration, 0.000005)
```

### 5.2 配置文件支持

```ini
# printer.cfg 中的 MCU 配置
[mcu]
serial: /dev/ttyUSB0
baud: 115200
# 新增参数
max_stepper_error: 0.000050
low_perf_mode: True          # 显式启用低性能模式
command_buffer_time: 0.3     # 命令缓冲时间
```

### 5.3 需要在 MCU 固件中嵌入的常量

为了支持自动检测，MCU 固件需要编译时嵌入以下常量：

```c
// 在 MCU 固件的编译时常量中添加
DECL_CONSTANT("MCU_TYPE", MCU_TYPE_AVR);       // MCU 类型
DECL_CONSTANT("TIMER_BITS", 16);                // 定时器位数
DECL_CONSTANT("MAX_STEPPER_RATE", 5000);        // 最大步进率 (步/秒)
DECL_CONSTANT("STEP_BUFFER_SIZE", 16);          // 步进缓冲区大小
```

## 6. 限制与注意事项

### 6.1 klippy 层面无法解决的问题

1. **定时器精度**: 硬件定时器精度无法通过软件补偿
2. **中断延迟**: MCU 中断响应时间是硬约束
3. **内存限制**: ATmega328P 的 2KB SRAM 限制命令缓冲区大小
4. **通信带宽**: 115200 baud UART 的理论最大吞吐量约 11.5KB/s

### 6.2 性能估算

| MCU | 时钟 | 最大步进率 | 适用场景 |
|-----|------|-----------|----------|
| ATmega328P | 16MHz | ~5000 步/秒 | 简单 3D 打印 (低速) |
| ATmega2560 | 16MHz | ~15000 步/秒 | 标准 3D 打印 |
| STM32F103 | 72MHz | ~100000 步/秒 | 高速 3D 打印 |
| STM32F407 | 168MHz | ~200000+ 步/秒 | 高性能应用 |

### 6.3 测试建议

1. 先在模拟环境中测试 (使用 `debugoutput` 模式)
2. 逐步降低 MCU 时钟频率，观察 klippy 的适应能力
3. 重点测试场景：
   - 高速直线移动 (最大步进率)
   - 圆弧插补 (持续高频率)
   - 回原点 (trsync 超时)
   - 温度控制 (ADC 采样与步进竞争)

## 7. 结论

**klippy 层面重构的可行性: 可行，但效果有限**

- ✅ 可以实现 MCU 能力自动检测和参数适配
- ✅ 可以优化命令发送频率和缓冲策略
- ✅ 可以为低性能 MCU 提供更好的容错
- ❌ 无法补偿 MCU 定时器精度不足
- ❌ 无法改变 MCU 固件的命令执行模式
- ❌ 无法突破通信带宽和延迟的物理限制

**推荐策略:**
1. **首选**: 继续推进下位机重构 (方案 A)，这是根本解决方案
2. **备选**: 实施 klippy 侧适配 (方案 B)，作为过渡方案
3. **长期**: 考虑 klippy + 简化固件的组合方案 (方案 C)

klippy 侧的改动工作量相对较小 (约 200-500 行 Python 代码)，可以与下位机重构并行推进，作为风险缓解措施。
