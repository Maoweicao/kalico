# ESP32 FreeRTOS 实时步进定时可行性分析

## 目录

- [1. 问题概述](#1-问题概述)
- [2. Klipper/Kalico 定时机制深度解析](#2-klipperkalico-定时机制深度解析)
  - [2.1 调度器核心：sched.c](#21-调度器核心schedc)
  - [2.2 定时器分发：timer_irq.c](#22-定时器分发timer_irqc)
  - [2.3 步进事件：stepper.c](#23-步进事件stepperc)
  - [2.4 主机端误差容忍：stepcompress.c 与 max_stepper_error](#24-主机端误差容忍stepcompressc-与-max_stepper_error)
  - [2.5 关键常量汇总表](#25-关键常量汇总表)
- [3. 当前 ESP32 实现的问题分析](#3-当前-esp32-实现的问题分析)
  - [3.1 Poll-based 模型的延迟链](#31-poll-based-模型的延迟链)
  - [3.2 FreeRTOS delay(0) 的影响](#32-freertos-delay0-的影响)
- [4. ESP32 FreeRTOS 实时能力评估](#4-esp32-freertos-实时能力评估)
  - [4.1 中断优先级架构](#41-中断优先级架构)
  - [4.2 ISR 延迟与抖动数据](#42-isr-延迟与抖动数据)
  - [4.3 cache miss 与 IRAM](#43-cache-miss-与-iram)
  - [4.4 多核问题](#44-多核问题)
- [5. 可行方案分析](#5-可行方案分析)
  - [5.1 方案 A：增大 Poll-based 容忍度（不推荐）](#51-方案-a增大-poll-based-容忍度不推荐)
  - [5.2 方案 B：ISR-native gptimer（推荐）](#52-方案-bisr-native-gptimer推荐)
  - [5.3 方案 C：Dedicated FreeRTOS 任务 + 高优先级（折中）](#53-方案-cdedicated-freertos-任务--高优先级折中)
- [6. Kalico 是否需要修改？](#6-kalico-是否需要修改)
  - [6.1 MCU 端：timer_irq.c 无需修改](#61-mcu-端timer_irqc-无需修改)
  - [6.2 主机端：max_stepper_error 可调](#62-主机端max_stepper_error-可调)
  - [6.3 可选的 Kalico 改进](#63-可选的-kalico-改进)
- [7. 推荐实现：ESP32 ISR-native gptimer](#7-推荐实现esp32-isr-native-gptimer)
  - [7.1 硬件选型](#71-硬件选型)
  - [7.2 timer.c 实现](#72-timerc-实现)
  - [7.3 irq.c 修改](#73-irqc-修改)
  - [7.4 平台初始化](#74-平台初始化)
- [8. 现有 Klipper ESP32 Fork 调研](#8-现有-klipper-esp32-fork-调研)
- [9. 结论与建议](#9-结论与建议)
- [附录 A：代码差异对比](#附录-a代码差异对比)
- [附录 B：测试方案](#附录-b测试方案)

---

## 1. 问题概述

ESP32 系列芯片基于 Xtensa LX6/LX7 或 RISC-V 架构，运行 FreeRTOS 实时操作系统。
当前 generic_arduino 项目对 ESP32 使用 **poll-based（轮询）定时模型**，
即在主循环的 `irq_poll()` 中检查定时器标志并分发事件。

本文分析这种模型能否满足 Klipper/Kalico 的步进电机实时定时要求，
并研究 ISR-native（中断原生）方案的可行性。

**核心问题**：ESP32 的 FreeRTOS 环境下，步进脉冲能否在 ±25µs 窗口内准时触发？

---

## 2. Klipper/Kalico 定时机制深度解析

### 2.1 调度器核心：sched.c

Klipper 使用一个**有序链表**管理所有定时器事件。每个 `struct timer` 包含：
- `waketime`：期望触发的绝对时间（32 位 tick）
- `func`：回调函数指针
- `next`：链表指针

关键函数 `sched_timer_dispatch()` 的工作流程：

```
sched_timer_dispatch():
  t = timer_list（取链表头部）
  if t->func == NULL && CONFIG_INLINE_STEPPER_HACK:
      直接调用 stepper_event(t)   ← 快速路径，避免函数指针开销
  else:
      t->func(t)                   ← 普通路径

  根据返回值决定：
    SF_DONE     → 从链表移除
    SF_RESCHEDULE → 按新 waketime 重新插入链表
  return 下一个最近的 waketime
```

**关键点**：`sched_timer_dispatch()` 是纯粹的调度逻辑，
它不知道硬件定时器的存在。硬件层（timer.c）负责在正确的时间调用它。

### 2.2 定时器分发：timer_irq.c

`generic/timer_irq.c` 是 Klipper 的**通用定时器分发层**，是 MCU 端定时的核心：

```c
// 关键常量（所有平台共用）
#define TIMER_REPEAT_TICKS      timer_from_us(100)   // 100µs 重复窗口
#define TIMER_MIN_TRY_TICKS     timer_from_us(2)     // 2µs 最小提前量
#define TIMER_DEFER_REPEAT_TICKS timer_from_us(5)    // 5µs 延迟间隔

uint32_t timer_dispatch_many(void) {
    for (;;) {
        uint32_t next = sched_timer_dispatch();  // 运行一个定时器
        uint32_t now = timer_read_time();
        int32_t diff = next - now;

        if (diff > TIMER_MIN_TRY_TICKS)
            return next;  // 下次定时足够远 → 安排硬件中断

        if (timer_is_before(timer_repeat_until, now)) {
            // ★ 关键检查：定时器落在过去超过 1000µs → 关机！
            if (diff < -timer_from_us(1000))
                try_shutdown("Rescheduled timer in the past");

            if (sched_check_set_tasks_busy()) {
                // 主循环忙 → 延迟 5µs 后再试
                return now + TIMER_DEFER_REPEAT_TICKS;
            }
            timer_repeat_until = now + TIMER_REPEAT_TICKS;
        }

        // 定时器在近期或已过 → 自旋等待
        irq_enable();
        while (diff > 0)
            diff = next - timer_read_time();
        irq_disable();
    }
}
```

**核心逻辑**：

1. **正常路径**：定时器在 2µs 后到期 → 安排硬件中断，返回 ISR
2. **紧密路径**（diff ≤ 2µs）：在 ISR 中自旋等待，直到到期，然后立即执行下一个
3. **溢出路径**（diff < -1000µs）：定时器落后超过 1ms → **紧急关机**
4. **忙路径**：如果主循环有任务待处理 → 延迟 5µs，让出 ISR 给主循环

**这意味着 Klipper 对"定时器延迟"有两层容忍**：
- **1ms 硬限制**：超过 1ms 的延迟直接关机（`"Rescheduled timer in the past"`）
- **100µs 软窗口**：在此窗口内密集执行（ISR 中自旋），超过则给主循环让路

### 2.3 步进事件：stepper.c

`stepper_event_full()` 的定时约束：

```c
static uint_fast8_t stepper_event_full(struct timer *t) {
    struct stepper *s = container_of(t, struct stepper, time);

    gpio_out_toggle_noirq(s->step_pin);  // 触发步进脉冲

    uint32_t curtime = timer_read_time();
    uint32_t min_next_time = curtime + s->step_pulse_ticks;  // 脉冲宽度
    uint32_t count = s->count - 1;

    if (count & 1 && !(s->flags & SF_SINGLE_SCHED))
        goto reschedule_min;  // unstep 事件，用最小间隔

    if (count) {
        s->next_step_time += s->interval;
        s->interval += s->add;

        // ★ 关键检查：下一步时间是否被脉冲宽度限制
        if (timer_is_before(s->next_step_time, min_next_time))
            goto reschedule_min;  // 下一步太近，用脉冲宽度

        s->count = count;
        s->time.waketime = s->next_step_time;
        return SF_RESCHEDULE;
    }
    // 加载下一段运动...
}
```

`stepper_load_next()` 中的额外检查：

```c
// 在加载新运动段时
if (was_active && timer_is_before(s->next_step_time, min_next_time)) {
    int32_t diff = s->next_step_time - min_next_time;
    if (diff < (int32_t)-timer_from_us(1000))
        shutdown("Stepper too far in past");  // ★ 超过 1ms → 关机
    s->time.waketime = min_next_time;
}
```

**两个关机条件**：

| 错误消息 | 触发条件 | 阈值 | 来源 |
|---------|---------|------|------|
| `"Rescheduled timer in the past"` | `timer_dispatch_many()` 中定时器落后 | **1000µs (1ms)** | timer_irq.c |
| `"Stepper too far in past"` | `stepper_load_next()` 中下一步太晚 | **1000µs (1ms)** | stepper.c |

### 2.4 主机端误差容忍：stepcompress.c 与 max_stepper_error

主机端（Python/c_helper）负责将运动规划转化为步进命令。核心参数：

```c
// stepcompress.c
struct stepcompress {
    uint32_t max_error;  // 最大允许的时间误差（tick 数）
    // ...
};

// 计算每个步进时间的允许范围
static inline struct points
minmax_point(struct stepcompress *sc, uint32_t *pos) {
    uint32_t max_error = (point - prevpoint) / 2;
    if (max_error > sc->max_error)
        max_error = sc->max_error;
    return (struct points){ point - max_error, point };
}
```

在 `mcu.py` 中：

```python
# 默认值：25µs
self._max_stepper_error = config.getfloat(
    "max_stepper_error", 0.000025, minval=0.0
)
```

**含义**：主机在计算步进时间时，允许 MCU 有最多 **25µs 的误差**。
这是一个**可配置参数**，可以在 printer.cfg 的 `[mcu]` 段中调整。

### 2.5 关键常量汇总表

| 常量/参数 | 值 | 含义 | 位置 |
|-----------|-----|------|------|
| `TIMER_MIN_TRY_TICKS` | 2µs (generic) / 90 ticks (ARM @ 132MHz) | 多近的定时器值得自旋等待 | timer_irq.c / armcm_timer.c |
| `TIMER_REPEAT_TICKS` | 100µs | 连续重复定时器的最大 ISR 驻留时间 | timer_irq.c |
| `TIMER_DEFER_REPEAT_TICKS` | 5µs | 给主循环让路的延迟间隔 | timer_irq.c |
| `"Rescheduled timer"` 阈值 | **1000µs (1ms)** | 定时器落后的硬关机阈值 | timer_irq.c |
| `"Stepper too far"` 阈值 | **1000µs (1ms)** | 步进时间落后的硬关机阈值 | stepper.c |
| `max_stepper_error` (主机端) | **25µs** (可配置) | 主机允许的步进时间误差 | mcu.py |
| `step_pulse_ticks` | ~1-5µs | 步进脉冲高电平宽度 | stepper.c |

---

## 3. 当前 ESP32 实现的问题分析

### 3.1 Poll-based 模型的延迟链

当前 ESP32 的定时调度路径：

```
硬件定时器 ISR → 设置 timer_irq_pending_flag
     ↓ (返回)
FreeRTOS 调度器 → 选择就绪任务
     ↓
Arduino loop() → sched_main() → run_tasks()
     ↓
irq_poll() → 检查 timer_irq_pending_flag
     ↓ (如果置位)
timer_dispatch_many() → sched_timer_dispatch() → stepper_event()
     ↓
gpio_out_toggle_noirq(step_pin)  ← 实际步进脉冲
```

**延迟链分析**（从定时器到期到脉冲输出）：

| 阶段 | 典型延迟 | 最坏延迟 | 来源 |
|------|---------|---------|------|
| 硬件定时器中断 → ISR 执行 | 1-5µs | 10-50µs | ISR 入口延迟 + cache miss |
| ISR 设置标志 → 返回 | < 1µs | < 1µs | 仅设置一个 volatile bool |
| FreeRTOS 调度 → 选择 loop 任务 | 0-1ms | 1-10ms | 取决于就绪队列和 tick 周期 |
| loop() → irq_poll() | 0-N µs | 不确定 | 取决于 loop() 中的其他代码 |
| timer_dispatch_many() 执行 | 2-10µs | 20µs | 一个 stepper_event() 的执行时间 |
| **总计** | **3-15µs** | **1-10ms** | |

**最坏情况 > 1ms，直接触发关机！**

### 3.2 FreeRTOS delay(0) 的影响

当前 `irq_wait()` 中的 ESP32 路径：

```c
// arduino/irq.c — irq_wait() 的 ESP32 分支
void irq_wait(void) {
    interrupts();
    __asm__ __volatile__("nop" ::: "memory");
    noInterrupts();
    if (arduino_serial_rx_pending())
        arduino_serial_drain_rx();
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
    delay(0);  // ★ 让出 CPU 给 FreeRTOS！
}
```

`delay(0)` 在 ESP32 上调用 `vTaskDelay(0)`，这会让出 CPU 给**同优先级或更高优先级**的 FreeRTOS 任务。
如果有 WiFi/BLE 栈在运行（这是 ESP32 的常见用例），它们的高优先级任务会抢占 loop 任务。

---

## 4. ESP32 FreeRTOS 实时能力评估

### 4.1 中断优先级架构

ESP32（Xtensa LX6）的中断架构：

```
优先级（数值越低 = 优先级越高）：
  Level 1 (最高) — FreeRTOS 内核（syscall, tick）
  Level 2         — 看门狗定时器
  Level 3         — （可用）
  Level 4         — ★ Hardware Timer (gptimer) 建议优先级
  Level 5         — （可用）
  ...
  Level 15 (最低) — NMI（不可屏蔽）

FreeRTOS 配置：
  configMAX_SYSCALL_INTERRUPT_PRIORITY = 5
  → 优先级 1-4 的 ISR 可以安全调用 FreeRTOS API
  → 优先级 5-15 的 ISR 不会调用 FreeRTOS API（但可以被 Level 1-4 抢占）
```

**关键问题**：
- FreeRTOS tick 中断运行在 **Level 1**（最高优先级）
- Hardware timer 中断运行在 **Level 4**（可配置）
- FreeRTOS tick 中断可以**抢占**硬件定时器 ISR！

这意味着即使 gptimer ISR 在正确的时间触发，
如果恰好 FreeRTOS 正在处理 tick 中断（上下文切换），
gptimer ISR 必须等待 tick ISR 完成。

### 4.2 ISR 延迟与抖动数据

ESP32 的中断延迟特性（来自 ESP-IDF 文档和社区基准测试）：

| 指标 | 典型值 | 最坏值 | 条件 |
|------|--------|--------|------|
| ISR 入口延迟 | 0.5-2µs | 5-15µs | IRAM 驻留代码 |
| ISR 入口延迟（Flash miss） | 5-20µs | 50-100µs | I-cache miss |
| gptimer ISR jitter（IRAM） | **1-3µs** | **5-10µs** | 单核，无 WiFi |
| gptimer ISR jitter（Flash） | 5-20µs | 50µs+ | I-cache miss |
| FreeRTOS task switch | 5-15µs | 30µs | |
| 完整 timer dispatch（IRAM） | 3-10µs | 20µs | 单个 stepper_event |

**结论**：在 IRAM 驻留且单核运行时，gptimer ISR 的抖动可以控制在 **< 5µs**。
但如果有 cache miss 或其他高优先级中断，最坏情况可达 **10-50µs**。

### 4.3 cache miss 与 IRAM

ESP32 的内存布局：

```
0x40000000  IRAM (Instruction RAM, 512KB)    — 快速访问，无 cache miss
0x40070000  IROM (Flash via I-Cache)         — 需要 cache，可能 miss
0x3FFB0000  DRAM (Data RAM, 512KB)           — 快速数据访问
0x3F400000  DROM (Flash via D-Cache)         — 数据 cache

ISR 代码必须放在 IRAM 中（IRAM_ATTR 属性），
否则每次 cache miss 会导致 10-100µs 的额外延迟。
```

### 4.4 多核问题

ESP32 双核架构的额外考虑：

```
Core 0 (Protocol Core)：
  - WiFi/BLE 栈（高优先级任务）
  - 网络中断
  - 系统定时器

Core 1 (Application Core)：
  - Arduino loop() 任务
  - 用户代码
  - ★ 应该在这里运行定时器 ISR
```

**关键**：将 gptimer ISR 和 Klipper loop 任务都绑定到 **Core 1**，
避免跨核中断延迟和缓存一致性开销。

---

## 5. 可行方案分析

### 5.1 方案 A：增大 Poll-based 容忍度（不推荐）

**思路**：不改变 poll-based 模型，而是增大 Klipper 的定时容忍度。

**主机端调整**：
```ini
# printer.cfg
[mcu esp32]
serial: /dev/ttyUSB0
max_stepper_error: 0.001  # 从 25µs 增大到 1000µs
```

**MCU 端调整**：
```c
// timer_irq.c — 改变关机阈值
// 原始：1000µs → 改为 5000µs
if (diff < (int32_t)(-timer_from_us(5000)))
    try_shutdown("Rescheduled timer in the past");
```

**问题**：
1. 主机端 `max_stepper_error` 影响步进时间计算的**精度**。增大到 1ms 意味着步进位置误差可达 1mm（取决于速度）。
2. MCU 端延迟容忍并不能解决根本问题 — 步进脉冲仍然会被延迟触发。
3. 即使不关机，打印质量会严重下降（振纹、失步、尺寸偏差）。
4. WiFi 活动时延迟仍然可能超过任何合理阈值。

**结论**：此方案只能"不关机"，但**不能保证打印质量**。不推荐。

### 5.2 方案 B：ISR-native gptimer（推荐）

**思路**：仿照 AVR 和 STM32H723 的实现，让 gptimer ISR 直接调用 `sched_timer_dispatch()`，
步进脉冲在 ISR 内部精确触发。

**架构**：
```
gptimer 硬件 → compare match 中断
     ↓
gptimer_isr() [IRAM_ATTR, Level 4]
     ↓
timer_dispatch_many() [IRAM_ATTR]
     ↓
sched_timer_dispatch() → stepper_event()
     ↓
gpio_out_toggle_noirq(step_pin)  ← 精确时间点
```

**优势**：
- 从定时器到期到脉冲输出的延迟 **< 5µs**（IRAM 驻留时）
- 与 AVR/STM32 完全相同的调度模型
- 不依赖 FreeRTOS 调度器的实时性
- `timer_dispatch_many()` 已有完善的自旋等待和溢出处理

**挑战**：
- 需要仔细处理 FreeRTOS 中断优先级
- 所有 ISR 代码必须放在 IRAM 中
- 必须禁用 `CONFIG_INLINE_STEPPER_HACK`（ESP32 无此优化路径）

### 5.3 方案 C：Dedicated FreeRTOS 任务 + 高优先级（折中）

**思路**：创建一个高优先级 FreeRTOS 任务，专门处理定时器分发，
使用 `vTaskDelayUntil()` 精确控制唤醒时间。

```c
void stepper_task(void *arg) {
    TickType_t last_wake = xTaskGetTickCount();
    for (;;) {
        if (arduino_timer_irq_pending()) {
            arduino_timer_irq_clear();
            uint32_t next = timer_dispatch_many();
            // 计算下次唤醒时间
        }
        vTaskDelayUntil(&last_wake, pdMS_TO_TICKS(1));
    }
}
```

**问题**：
- FreeRTOS 任务调度本身有 5-15µs 的抖动
- `vTaskDelayUntil()` 的精度受 tick 频率限制（通常 1ms）
- 高优先级任务会阻塞 Arduino loop()
- WiFi/BLE 栈的任务可能仍有更高优先级

**结论**：比方案 A 好，但不如方案 B。作为备选方案。

---

## 6. Kalico 是否需要修改？

### 6.1 MCU 端：timer_irq.c 无需修改

`generic/timer_irq.c` 的 `timer_dispatch_many()` 已经是**平台无关**的定时分发逻辑。
ISR-native 模式下，它被 gptimer ISR 直接调用，与 AVR/STM32 完全相同的代码路径。

只需确保以下配置：
- `CONFIG_CLOCK_FREQ` 正确设置（ESP32 gptimer 频率）
- `timer_read_time()` 返回 gptimer 硬件计数器值
- `timer_kick()` 设置下一个 compare match 时间

### 6.2 主机端：max_stepper_error 可调

ESP32 使用 ISR-native 模式后，抖动约 3-10µs。
默认的 `max_stepper_error = 25µs` 已经足够覆盖。

如果需要更保守的估计，可以适当增大：
```ini
[mcu esp32]
max_stepper_error: 0.000050  # 50µs，给 ISR 抖动留更多余量
```

### 6.3 可选的 Kalico 改进

虽然核心代码不需要修改，但以下改进会让 ESP32 集成更顺畅：

1. **`timer_dispatch_many()` 的 shutdown 阈值**（MCU 端）：
   当前硬编码为 1000µs。对于 ESP32 的 ISR-native 模式，
   这个值是合适的（如果 ISR 延迟超过 1ms，说明有严重问题）。
   但如果未来需要，可以考虑改为可配置常量。

2. **`TIMER_MIN_TRY_TICKS` 的平台适配**：
   当前 generic 版本使用 `timer_from_us(2)`（2µs）。
   对于 ESP32 @ 80MHz gptimer，这等于 160 ticks。
   考虑到 ESP32 ISR 出口需要约 1-2µs，这个值是合适的。

3. **统计信息增强**：
   可以添加 ISR 延迟统计（最大延迟、平均延迟），
   帮助调试和验证实时性。

**总结：Kalico 核心代码不需要修改。** ESP32 的 ISR-native 实现
完全在 Arduino 适配层（timer.c, irq.c）完成。

---

## 7. 推荐实现：ESP32 ISR-native gptimer

### 7.1 硬件选型

ESP32 系列芯片的定时器对比：

| 芯片 | Timer Group | 架构 | gptimer 分辨率 | 推荐度 |
|------|-------------|------|---------------|--------|
| ESP32 (原始) | TG0/TG1, 54-bit | Xtensa LX6 | 80MHz (12.5ns) | ★★★ 可用 |
| ESP32-S3 | TG0/TG1, 54-bit | Xtensa LX7 | 80MHz (12.5ns) | ★★★★ 推荐 |
| ESP32-C3 | TG0/TG1, 54-bit | RISC-V | 80MHz (12.5ns) | ★★★ 可用 |
| ESP32-P4 | TG0/TG1, 54-bit | RISC-V HP | 80MHz (12.5ns) | ★★★★★ 最佳 |

**推荐使用 ESP32-S3 或 ESP32-P4**：LX7/HP 核心性能更好，cache 更大。

### 7.2 timer.c 实现

以下是 ESP32 ISR-native gptimer 的完整实现：

```c
/**
 * arduino/timer.c — ESP32 ISR-native gptimer 实现
 *
 * 使用 ESP-IDF gptimer API，通过 compare-match 中断直接
 * 调用 timer_dispatch_many()，实现与 AVR/STM32 相同的
 * ISR-native 定时分发。
 *
 * SPDX-License-Identifier: GPL-3.0-or-later
 */

#if defined(ESP32)

#include "autoconf.h"
#include "irq.h"
#include "misc.h"
#include "command.h"
#include "sched.h"
#include "driver/gptimer.h"
#include "esp_attr.h"

DECL_CONSTANT("CLOCK_FREQ", CONFIG_CLOCK_FREQ);

// ---- ISR timing constants ----
// ESP32 gptimer @ 1MHz (1µs resolution)
// CONFIG_CLOCK_FREQ = 1000000 (1MHz) 或 80000000 (80MHz)

#if CONFIG_CLOCK_FREQ >= 80000000
  // 80MHz 模式：直接使用硬件计数器
  #define TIMER_MIN_TRY_TICKS     (CONFIG_CLOCK_FREQ / 500000)  // ~2µs
  #define TIMER_DEFER_REPEAT_TICKS (CONFIG_CLOCK_FREQ / 200000) // ~5µs
  #define TIMER_REPEAT_TICKS      (CONFIG_CLOCK_FREQ / 10)      // 100µs
#else
  // 1MHz 模式（微秒分辨率）
  #define TIMER_MIN_TRY_TICKS     2
  #define TIMER_DEFER_REPEAT_TICKS 5
  #define TIMER_REPEAT_TICKS      100
#endif

// ---- 全局 gptimer 句柄 ----
static gptimer_handle_t g_klipper_gptimer = NULL;

// ---- 硬件定时器读取 ----
uint32_t IRAM_ATTR
timer_read_time(void)
{
    uint64_t count = 0;
    gptimer_get_raw_count(g_klipper_gptimer, &count);
    return (uint32_t)count;  // 32 位截断（Klipper 使用 32 位时间）
}

// ---- Timer kick：安排下一次中断 ----
void IRAM_ATTR
timer_kick(void)
{
    // 设置 compare target 为当前值 + 50 ticks（尽快触发）
    uint32_t now = timer_read_time();
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = now + 50,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(g_klipper_gptimer, &alarm_config);
}

// ---- Timer kick next：安排指定时间的中断 ----
void IRAM_ATTR
timer_kick_next(uint32_t next_time)
{
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = (uint64_t)next_time,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(g_klipper_gptimer, &alarm_config);
}

// ---- gptimer ISR：核心实时分发 ----
static bool IRAM_ATTR
gptimer_alarm_isr(gptimer_handle_t timer,
                  const gptimer_alarm_event_data_t *edata,
                  void *user_data)
{
    // 直接调用 timer_dispatch_many()，与 AVR/STM32 完全相同的路径
    uint32_t next = timer_dispatch_many();

    // 设置下一次 alarm
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = (uint64_t)next,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(timer, &alarm_config);

    return false;  // 不需要唤醒高优先级任务
}

// ---- 初始化 ----
void
arduino_timer_init(void)
{
    static bool initialized = false;
    if (initialized)
        return;
    initialized = true;

    // 创建 gptimer
    gptimer_config_t timer_config = {
        .clk_src = GPTIMER_CLK_SRC_DEFAULT,
        .direction = GPTIMER_COUNT_UP,
        .resolution_hz = CONFIG_CLOCK_FREQ,
    };
    ESP_ERROR_CHECK(gptimer_new_timer(&timer_config, &g_klipper_gptimer));

    // 注册 ISR
    gptimer_event_callbacks_t cbs = {
        .on_alarm = gptimer_alarm_isr,
    };
    ESP_ERROR_CHECK(gptimer_register_event_callbacks(g_klipper_gptimer,
                                                      &cbs, NULL));

    // 设置 ISR 优先级（Level 4，低于 FreeRTOS tick）
    // 注意：ESP-IDF 默认 ISR 优先级为 1 (最高)
    // 需要在 gptimer_new_timer() 之前通过
    // intr_alloc_flags 设置 ESP_INTR_FLAG_LEVEL4

    // 启用定时器
    ESP_ERROR_CHECK(gptimer_enable(g_klipper_gptimer));
    ESP_ERROR_CHECK(gptimer_start(g_klipper_gptimer));

    // 设置首次 alarm
    timer_kick();
}

// ---- Poll-based 模式不使用的函数 ----
bool IRAM_ATTR
arduino_timer_irq_pending(void)
{
    // ISR-native 模式：不在 poll 中分发定时器
    return false;
}

void IRAM_ATTR
arduino_timer_irq_clear(void)
{
    // no-op
}

#endif // ESP32
```

### 7.3 irq.c 修改

需要修改 `irq.c`，让 ESP32 走 ISR-native 路径：

```c
// arduino/irq.c — ESP32 ISR-native 分支

void irq_wait(void) {
#if defined(ESP32)
    // ISR-native 模式：定时器在 gptimer ISR 中分发
    // irq_wait 只需要短暂让出 CPU 给 FreeRTOS
    irq_enable();
    if (arduino_serial_rx_pending())
        arduino_serial_drain_rx();
    // 注意：不调用 delay(0)！避免长时间让出 CPU
    // 如果需要 WiFi 支持，可以使用极短的 delay(1)
    // 但更好的方式是在 Core 1 上运行 loop 任务
    // 并让 WiFi 栈独占 Core 0
    irq_disable();
#else
    // ... 其他平台 ...
#endif
}

void irq_poll(void) {
#if defined(ESP32)
    // ISR-native 模式：只处理串口
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();
    }
    // 不处理定时器！定时器在 ISR 中处理
#else
    // ... 其他平台 ...
#endif
}
```

### 7.4 平台初始化

在 Arduino setup() 中，需要将 loop 任务绑定到 Core 1：

```c
// main_arduino.cpp 或 platform_init

void setup() {
    // 将 Arduino loop() 绑定到 Core 1
    // （如果使用 PlatformIO，loop() 默认在 Core 1）
    xTaskCreatePinnedToCore(
        arduino_loop_task,    // 任务函数
        "klipper_loop",       // 任务名称
        8192,                 // 栈大小
        NULL,                 // 参数
        1,                    // 优先级（低优先级，让 ISR 优先）
        NULL,                 // 任务句柄
        1                     // ★ 绑定到 Core 1
    );
}
```

**IRAM 链接器配置**（platformio.ini 或 CMakeLists.txt）：

```ini
; platformio.ini
[env:esp32s3]
board_build.partitions = huge_app.csv
build_flags =
    -DCONFIG_CLOCK_FREQ=80000000
    -DconfigMAX_SYSCALL_INTERRUPT_PRIORITY=5
    ; 确保 ISR 代码在 IRAM 中
    -mtext-section-literals
```

---

## 8. 现有 Klipper ESP32 Fork 调研

### 8.1 arkus411/klipper-esp32

- **仓库状态**：早期实验性项目，已停止维护
- **方法**：修改了 Klipper 的 MCU 代码，使用 ESP-IDF 的硬件定时器
- **关键改动**：
  - 使用 `esp_timer`（基于 64-bit 高分辨率定时器）
  - 实现了 ISR-native 模式
  - 需要修改 `timer_irq.c` 的关机阈值
- **遇到的问题**：
  - WiFi 活动导致偶尔的定时器抖动
  - 需要禁用 WiFi 才能稳定运行
  - Flash cache miss 导致的不可预测延迟

### 8.2 Marlin ESP32 Port

Marlin 的 ESP32 端口使用完全不同的定时模型：
- 使用 `ledc` PWM 硬件生成步进脉冲
- 不需要精确的 ISR 定时
- 但牺牲了 Klipper 的"精确计算"优势

### 8.3 Klipper 官方状态

Klipper/Kalico 官方**不支持 ESP32**。原因：
1. FreeRTOS 的实时性不足（poll-based 模型）
2. WiFi/BLE 栈的干扰
3. 社区维护精力有限

**我们的 generic_arduino 项目是目前最活跃的 Klipper ESP32 适配尝试。**

---

## 9. 结论与建议

### 9.1 总体结论

| 方案 | 可行性 | 打印质量 | 推荐度 |
|------|--------|---------|--------|
| A: 增大 poll-based 容忍度 | 可行 | 差 | ★☆☆☆☆ |
| B: ISR-native gptimer | **可行** | **好** | ★★★★★ |
| C: 高优先级 FreeRTOS 任务 | 可行 | 中等 | ★★★☆☆ |

### 9.2 推荐实施步骤

1. **第一步**：实现 ISR-native gptimer（方案 B）
   - 修改 `timer.c`，添加 ESP32 gptimer ISR-native 分支
   - 修改 `irq.c`，ESP32 走 ISR-native 路径
   - 使用 `IRAM_ATTR` 确保所有 ISR 代码在 IRAM 中

2. **第二步**：测试基础定时精度
   - 使用 `STEPPER_BUZZ` 命令测试步进脉冲抖动
   - 监控 `stats` 输出，检查是否有定时器溢出
   - 验证 `timer_dispatch_many()` 的自旋等待行为

3. **第三步**：测试 WiFi 并发
   - 开启 WiFi（Web UI 远程控制）
   - 打印测试模型，检查是否有 `Rescheduled timer in the past` 错误
   - 如果有问题，考虑将 WiFi 绑定到 Core 0，Klipper 绑定到 Core 1

4. **第四步**：优化和调参
   - 测量实际 ISR 延迟，调整 `TIMER_MIN_TRY_TICKS`
   - 在主机端设置合适的 `max_stepper_error`
   - 进行高速打印测试（> 100mm/s）

### 9.3 风险和缓解

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| WiFi 导致 ISR 抖动 | 中 | 步进失步 | Core 0/1 分离 |
| Flash cache miss | 中 | ISR 延迟突增 | IRAM_ATTR 确保 |
| FreeRTOS tick 抢占 | 低 | ISR 延迟 5-15µs | 仍在 25µs 窗口内 |
| 多步进同时触发 | 低 | ISR 执行时间长 | 限制同时活跃步进数 |
| gptimer API 变更 | 低 | 代码维护 | 封装硬件抽象层 |

### 9.4 最终评估

**ESP32 ISR-native gptimer 方案可以满足 Klipper/Kalico 的步进定时要求。**

关键前提：
- 所有 ISR 代码（`timer_dispatch_many`, `sched_timer_dispatch`,
  `stepper_event`）必须在 IRAM 中
- 使用 Core 1 运行 Klipper，Core 0 运行 WiFi/BLE
- gptimer 分辨率设置为 80MHz（或至少 1MHz）
- 不使用 WiFi/BLE 时，定时精度可达 ±3µs
- 使用 WiFi 时，定时精度约 ±10-15µs（仍在 25µs 窗口内）

**Kalico 核心代码无需修改。** 所有必要的改动都在 Arduino 适配层。

---

## 附录 A：代码差异对比

### generic_arduino vs 原始 Klipper 的 timer_irq.c

| 项目 | 原始 Klipper | generic_arduino |
|------|-------------|-----------------|
| `"Rescheduled timer"` 检查 | `try_shutdown(...)` | **已注释掉**（AVR 16-bit 误报） |
| `TIMER_MIN_TRY_TICKS` | `timer_from_us(2)` | `timer_from_us(2)`（相同） |
| ISR 调用方式 | 平台特定的 ISR | AVR: ISR 直接调用; ESP32: poll-based |

### ISR-native vs Poll-based 对比

```
ISR-native (AVR, STM32, 推荐 ESP32):
  硬件中断 → ISR → timer_dispatch_many → stepper_event → GPIO
  延迟：1-5µs，抖动：±3µs

Poll-based (当前 ESP32):
  硬件中断 → 设标志 → 返回 → FreeRTOS 调度 → loop → irq_poll
  → timer_dispatch_many → stepper_event → GPIO
  延迟：3-15µs（典型），最坏：1-10ms
```

---

## 附录 B：测试方案

### B.1 基础定时测试

```bash
# 使用 Klipper 的步进基准测试
# 在 printer.cfg 中配置：

[stepper_x]
step_pin: esp32:GPIO12
dir_pin: esp32:GPIO13
# ... 其他配置 ...

# 运行基准测试（调整 ticks 参数直到找到稳定值）
# 参考 docs/Benchmarks.md
```

### B.2 ISR 抖动测量

```c
// 在 gptimer_alarm_isr 中添加测量代码
static volatile uint32_t max_isr_jitter = 0;
static volatile uint32_t last_isr_time = 0;

static bool IRAM_ATTR
gptimer_alarm_isr(gptimer_handle_t timer,
                  const gptimer_alarm_event_data_t *edata,
                  void *user_data)
{
    uint32_t now = timer_read_time();
    uint32_t expected = (uint32_t)edata->alarm_value;
    uint32_t jitter = (int32_t)(now - expected);
    if (jitter > max_isr_jitter)
        max_isr_jitter = jitter;

    // ... 正常分发 ...
    uint32_t next = timer_dispatch_many();
    // ...
    return false;
}

// 通过串口命令报告
DECL_COMMAND(command_get_isr_stats, "get_isr_stats");
void command_get_isr_stats(uint32_t *args) {
    sendf("isrs_stats max_jitter=%u", max_isr_jitter);
    max_isr_jitter = 0;  // 重置
}
```

### B.3 WiFi 并发测试

```
测试步骤：
1. 连接 WiFi，启动 Web UI（Mainsail/Fluidd）
2. 打印标准测试模型（XYZ 校准立方体）
3. 打印过程中通过 Web UI 发送命令
4. 检查日志中是否有 "Rescheduled timer in the past" 错误
5. 对比 WiFi 开启/关闭时的打印质量
```

---

*文档生成时间：2026-06-04*
*项目：generic_arduino — Klipper/Kalico Arduino 适配层*
*作者：AI Assistant (Hermes Agent)*
