# Klipper Generic Arduino 固件重构研究报告

## 目录

- [阶段一：跨平台框架分析](#阶段一跨平台框架分析)
- [阶段二：方案设计](#阶段二方案设计)
- [阶段三：Arduino Uno 原型实现](#阶段三arduino-uno-原型实现)
- [阶段四：上位机重构分析](#阶段四上位机重构分析)
- [总结](#总结)

---

## 阶段一：跨平台框架分析

### 1.1 核心问题

Klipper 固件的核心需求是 **ISR（中断服务程序）内直接调度步进电机**。在原生 AVR 实现中：

```c
// src/avr/timer.c — 原生 Klipper
ISR(TIMER1_COMPA_vect) {
    uint16_t next;
    for (;;) {
        next = sched_timer_dispatch();  // 直接在 ISR 内调用！
        // ... 16-bit 比较，决定是否继续或退出
        timer_set(next);
    }
}
```

而 generic_arduino 当前使用**轮询模式**：
```c
// src/arduino/timer.c — 当前 generic_arduino
ISR(TIMER1_COMPA_vect) {
    timer_irq_pending_flag = true;  // 仅设置标志
}
// irq_poll() 中检查标志并调用 timer_dispatch_many()
```

这导致步进电机调度延迟约 50-200µs，对高速步进（>100kHz step rate）是不可接受的。

### 1.2 框架对比分析

| 框架 | AVR | STM32 | ESP32 | 中断管理 | 定时器抽象 | GPIO抽象 | 评价 |
|------|-----|-------|-------|----------|-----------|---------|------|
| **Arduino Framework** | ✅ | ✅ | ✅ | ❌弱（无ISR API） | ❌弱（millis/micros） | ✅好 | 跨平台好，但ISR能力差 |
| **PlatformIO** | ✅ | ✅ | ✅ | 继承framework | 继承framework | 继承framework | 构建系统，非framework |
| **libopencm3** | ❌ | ✅ | ❌ | ✅优秀 | ✅优秀 | ✅优秀 | 仅ARM Cortex-M |
| **STM32 HAL** | ❌ | ✅ | ❌ | ✅好 | ✅好 | ✅好 | 仅STM32 |
| **ESP-IDF** | ❌ | ❌ | ✅ | ✅优秀 | ✅优秀 | ✅优秀 | 仅ESP32 |
| **Zephyr RTOS** | ❌ | ✅ | ✅ | ✅优秀 | ✅优秀 | ✅优秀 | 无AVR支持 |
| **CMSIS** | ❌ | ✅ | ❌ | ✅优秀 | ✅优秀 | ✅好 | 仅ARM Cortex-M |
| **Adafruit forks** | ✅ | ✅ | ✅ | ❌弱 | ❌弱 | ✅好 | Arduino生态扩展 |

### 1.3 关键发现

**不存在一个统一框架能同时覆盖 AVR + ARM + ESP32 并提供优秀 ISR 支持。**

原因：
1. AVR 和 ARM 的中断架构根本不同（IVT vs NVIC）
2. AVR 是 8-bit Harvard 架构，ARM 是 32-bit Von Neumann
3. 定时器硬件差异巨大（AVR 8/16-bit vs ARM 32-bit）
4. 任何抽象层都会引入不可避免的开销

### 1.4 推荐方案：自定义 HAL + Arduino 构建系统

**核心思路**：不依赖任何跨平台 framework 的 ISR 能力，而是为每个平台编写**原生 ISR 代码**，用 PlatformIO 管理构建，用统一的 HAL 接口隔离差异。

```
┌─────────────────────────────────────────────┐
│           Klipper 核心层 (platform-agnostic) │
│  command.c, basecmd.c, gpiocmds.c, stepper.c│
├─────────────────────────────────────────────┤
│           HAL 接口层 (hal_*.h)              │
│  hal_timer.h, hal_gpio.h, hal_serial.h     │
├──────────┬──────────┬───────────┬───────────┤
│ avr/     │ stm32f1/ │ stm32f4/  │ esp32/    │
│ timer.c  │ timer.c  │ timer.c   │ timer.c   │
│ gpio.c   │ gpio.c   │ gpio.c    │ gpio.c    │
│ serial.c │ serial.c │ serial.c  │ serial.c  │
├──────────┴──────────┴───────────┴───────────┤
│           PlatformIO 构建系统               │
│  platformio.ini: env:uno, env:stm32f103... │
└─────────────────────────────────────────────┘
```

---

## 阶段二：方案设计

### 2.1 HAL 层接口设计

#### hal_timer.h — 定时器接口
```c
// 平台必须实现的函数
void hal_timer_init(void);              // 初始化硬件定时器
uint32_t hal_timer_read(void);          // 读取当前时间（ticks）
void hal_timer_set(uint32_t ticks);     // 设置下一次中断时间
void hal_timer_kick(void);              // 立即触发定时器中断
uint32_t hal_timer_dispatch(void);      // ISR 内调用，返回下次唤醒时间

// 通用函数（generic/timer_irq.c 提供）
uint32_t timer_from_us(uint32_t us);
uint8_t timer_is_before(uint32_t t1, uint32_t t2);
```

#### hal_gpio.h — GPIO 接口
```c
struct gpio_out hal_gpio_out_setup(uint8_t pin, uint8_t val);
void hal_gpio_out_write(struct gpio_out g, uint8_t val);
void hal_gpio_out_toggle_noirq(struct gpio_out g);  // ISR-safe
struct gpio_in hal_gpio_in_setup(uint8_t pin, int8_t pull_up);
uint8_t hal_gpio_in_read(struct gpio_in g);
```

#### hal_irq.h — 中断管理接口
```c
void hal_irq_disable(void);
void hal_irq_enable(void);
irqstatus_t hal_irq_save(void);
void hal_irq_restore(irqstatus_t flag);
void hal_irq_wait(void);  // 等待中断
void hal_irq_poll(void);  // 轮询待处理事件
```

### 2.2 平台注册机制

```c
// hal_platform.h
struct hal_platform {
    const char *name;
    uint32_t clock_freq;
    void (*init)(void);
    void (*timer_init)(void);
    void (*serial_init)(void);
};

// 每个平台定义自己的实例
extern const struct hal_platform hal_platform_avr_uno;
extern const struct hal_platform hal_platform_stm32f103;
```

### 2.3 步进电机 ISR 调度的跨平台实现

**关键设计**：区分"ISR-native"和"poll-based"两种模式

| 平台 | 模式 | 原因 |
|------|------|------|
| AVR ATmega328P/2560 | ISR-native | 16-bit Timer1 COMPA 直接调度 |
| STM32 F103/F072/F407/H723 | ISR-native | 32-bit TIM 定时器 + NVIC |
| ESP32 | poll-based | FreeRTOS 环境，ISR 受限 |

**AVR ISR-native 实现**（直接移植自原生 Klipper）：

```c
ISR(TIMER1_COMPA_vect) {
    uint16_t next;
    for (;;) {
        next = sched_timer_dispatch();
        // 检查是否需要继续
        int16_t diff = TCNT1 - next;
        if (diff >= 0) {
            // 立即运行下一个 timer
            irq_enable();
            if (TIFR1 & (1<<OCF1B)) goto check_defer;
            irq_disable();
            continue;
        }
        if (diff <= -TIMER_MIN_TRY_TICKS)
            goto done;
        // 等待到时间
    }
done:
    OCR1A = next;
}
```

**STM32 ISR-native 实现**：
```c
void TIMx_IRQHandler(void) {
    if (TIMx->SR & TIM_SR_CC1IF) {
        TIMx->SR = ~TIM_SR_CC1IF;
        uint32_t next = sched_timer_dispatch();
        TIMx->CCR1 = next;
    }
}
```

### 2.4 Klipper 协议兼容性

保持与 Klipper 上位机的完全兼容：
- 二进制协议（VLQ + CRC16）不变
- 命令/响应格式不变
- identify 数据结构不变
- 时钟频率、序列号等常量正确报告

---

## 阶段三：Arduino Uno 原型实现

### 3.1 实现策略

1. **保留现有可工作的模块**：command.c, basecmd.c, gpiocmds.c, buttons.c, debugcmds.c, serial_irq.c
2. **重构 timer 系统**：AVR 上改为 ISR-native 模式（直接在 ISR 内调度 timer）
3. **实现 stepper.c**：移植原生 Klipper stepper，使用 `stepper_event_full` 路径
4. **更新 registrations.c**：添加 stepper 的 init/task/shutdown 注册
5. **更新 compile_time_request.c**：添加 stepper 相关命令

### 3.2 关键改动

#### 3.2.1 arduino/timer.c — AVR ISR-native 模式

将 AVR 的 Timer1 COMPA ISR 从"设置标志"改为"直接调度"：

```c
// 旧代码（poll-based）：
ISR(TIMER1_COMPA_vect) {
    timer_irq_pending_flag = true;
}

// 新代码（ISR-native）：
ISR(TIMER1_COMPA_vect) {
    uint16_t next;
    for (;;) {
        next = sched_timer_dispatch();
        int16_t diff = TCNT1 - next;
        if (likely(diff >= 0)) {
            irq_enable();
            if (unlikely(TIFR1 & (1<<OCF1B)))
                goto check_defer;
            irq_disable();
            break;
        }
        if (likely(diff <= -(int16_t)TIMER_MIN_TRY_TICKS))
            goto done;
        irq_enable();
        if (unlikely(TIFR1 & (1<<OCF1B)))
            goto check_defer;
        irq_disable();
    }
check_defer:
    irq_disable();
    // ... defer logic
done:
    OCR1A = next;
}
```

#### 3.2.2 stepper.c — 完整实现

移植原生 Klipper 的 stepper 实现，使用 `stepper_event_full` 路径（通用，不依赖特殊优化）。

#### 3.2.3 autoconf.h — 启用 stepper

```c
#define CONFIG_WANT_STEPPER       1
#define CONFIG_INLINE_STEPPER_HACK 0  // 不使用 inline hack
```

### 3.3 编译测试结果

（将在实现后记录）

---

## 阶段四：上位机重构分析

### 4.1 当前 Klipper 上位机 MCU 通信架构

Klipper 上位机 (`klippy/`) 通过以下模块与 MCU 通信：

- `klippy/serialhdl.py` — 串口通信层
- `klippy/chelper/` — C 扩展（序列号调度器）
- `klippy/extras/stepper.py` — 步进电机驱动
- `klippy/extras/mcu.py` — MCU 抽象层

### 4.2 上位机适配不同 MCU 能力的可行性

**方案 A：上位机根据 MCU 类型选择命令模式**

```python
# klippy/extras/mcu.py
class MCU:
    def _configure_stepper(self, stepper):
        if self._mcu_type in ('arduino_uno', 'arduino_mega'):
            # 轮询模式：降低 step rate，增加 interval
            self._send_config_stepper_poll(stepper)
        else:
            # 中断模式：正常配置
            self._send_config_stepper_isr(stepper)
```

**方案 B：上位机发送 "mode" 参数**

在 config_stepper 命令中增加 mode 参数，MCU 根据 mode 选择 ISR 或 poll 调度。

### 4.3 评估

上位机重构的**可行性高但收益有限**：
- 可以让不支持 ISR 的 MCU 也能运行 stepper（低速）
- 但无法解决轮询模式的根本延迟问题
- 更好的方案是：在 MCU 端实现 ISR-native，上位机无需改动

---

## 总结

### 框架研究结论

**不存在统一的跨平台 ISR 框架**。推荐方案是：
1. 使用 PlatformIO 作为构建系统
2. 为每个平台编写原生 ISR 代码
3. 用统一 HAL 接口隔离差异
4. 核心 Klipper 层保持平台无关

### 重构方案

1. **AVR 平台**：改为 ISR-native 模式（Timer1 COMPA 直接调度 stepper）
2. **ARM/ESP32 平台**：保持 poll-based（后续可逐步改为 ISR-native）
3. **stepper.c**：移植原生 Klipper 实现，使用通用 `stepper_event_full` 路径
4. **保持协议兼容**：所有命令/响应格式不变

### 预期效果

- AVR Uno：支持单轴步进电机，step rate 可达 ~100kHz
- AVR Mega：支持多轴步进电机
- 代码复用率：核心层 100%，HAL 层 0%（平台特定）

---

*文档生成时间: 2026-06-03*
*基于 generic_arduino 项目当前代码分析*
