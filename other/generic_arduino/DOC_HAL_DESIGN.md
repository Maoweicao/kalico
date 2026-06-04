# HAL 接口设计文档

## 概述

本文档定义了 generic_arduino 项目的硬件抽象层（HAL）接口设计。目标是为 Arduino 框架上的 Klipper MCU 固件提供清晰的分层架构，支持 AVR/ARM/ESP32 等多平台。

## 架构分层

```
┌─────────────────────────────────────────────┐
│  Klipper 协议层 (command.c, sched.c)         │
│  - 命令解析/编码                              │
│  - 定时器调度                                 │
│  - 任务管理                                   │
├─────────────────────────────────────────────┤
│  业务逻辑层 (stepper.c, gpiocmds.c, ...)      │
│  - 步进电机控制                               │
│  - GPIO 命令                                  │
│  - 按钮输入                                   │
├─────────────────────────────────────────────┤
│  通用层 (generic/)                            │
│  - serial_irq.c — 中断驱动串口逻辑            │
│  - timer_irq.c — 定时器分发逻辑               │
│  - crc16_ccitt.c — CRC 校验                   │
│  - gpio.h — GPIO 结构体定义                   │
├─────────────────────────────────────────────┤
│  HAL 层 (arduino/)                            │
│  - irq.c — 中断管理                           │
│  - timer.c — 硬件定时器                       │
│  - serial.cpp — UART 串口                     │
│  - gpio.c — GPIO 操作                         │
│  - pgm.h — PROGMEM 抽象                      │
│  - io.h — 内存屏障 I/O                        │
├─────────────────────────────────────────────┤
│  Arduino 框架层                               │
│  - HardwareSerial, digitalWrite, etc.         │
└─────────────────────────────────────────────┘
```

## 1. hal_gpio.h — GPIO 操作接口

### 结构体定义

```c
// 输出引脚
struct gpio_out {
    uint8_t pin;        // Arduino 数字引脚号
    uint8_t invert;     // 反转输出 (1 = 低有效)
    uint8_t is_static;  // 静态输出标志
    void*   pwm_ptr;    // PWM 硬件指针 (平台相关)
};

// 输入引脚
struct gpio_in {
    uint8_t pin;        // Arduino 数字引脚号
    uint8_t invert;     // 反转输入 (1 = 低有效)
};

// ADC 输入
struct gpio_adc {
    uint8_t pin;        // Arduino 模拟引脚号 (A0→0, A1→1, ...)
};

// PWM 输出
struct gpio_pwm {
    uint8_t pin;        // Arduino 数字引脚号
    uint8_t channel;    // PWM 通道
    void*   hw;         // PWM 硬件指针
};
```

### 接口函数

```c
// GPIO 输出
struct gpio_out gpio_out_setup(uint8_t pin, uint8_t val);
void gpio_out_reset(struct gpio_out g, uint8_t val);
void gpio_out_toggle_noirq(struct gpio_out g);  // ISR 安全
void gpio_out_toggle(struct gpio_out g);
void gpio_out_write(struct gpio_out g, uint8_t val);
uint8_t gpio_out_valid(struct gpio_out g, uint8_t val);

// GPIO 输入
struct gpio_in gpio_in_setup(uint8_t pin, int8_t pull_up);
void gpio_in_reset(struct gpio_in g, int8_t pull_up);
uint8_t gpio_in_read(struct gpio_in g);

// ADC
struct gpio_adc gpio_adc_setup(uint8_t pin);
void gpio_adc_reset(struct gpio_adc g);
uint32_t gpio_adc_sample(struct gpio_adc g);
uint16_t gpio_adc_read(struct gpio_adc g);
void gpio_adc_cancel_sample(struct gpio_adc g);

// PWM
struct gpio_pwm gpio_pwm_setup(uint8_t pin, uint32_t cycle_time, uint8_t val);
void gpio_pwm_write(struct gpio_pwm g, uint8_t val);
```

### 关键约束
- `gpio_out_write()` 和 `gpio_out_toggle_noirq()` 必须是 ISR 安全的（可在 Timer1 ISR 中调用）
- ATmega328P: 使用直接端口寄存器操作（PORTB/PORTC/PORTD）可获得更好的性能
- 当前实现使用 Arduino `digitalWrite()`，在 ISR 中可能有 ~5µs 延迟

## 2. hal_timer.h — 定时器接口

### ISR-Native 调度模式（AVR）

在 AVR 上，Timer1 COMPA ISR 直接调用 `sched_timer_dispatch()`，实现零延迟步进脉冲调度。

```
Timer1 COMPA ISR:
  ┌──────────────────────────────┐
  │ sched_timer_dispatch()       │ ← 返回下一个唤醒时间
  │   ├─ stepper_event()         │ ← 步进脉冲在这里生成
  │   ├─ digital_toggle_event()  │ ← GPIO PWM 切换
  │   └─ periodic_event()        │ ← 周期性任务唤醒
  │                              │
  │ 检查是否需要 spin-wait       │
  │ 设置 OCR1A = next_waketime   │
  └──────────────────────────────┘
```

### 核心接口

```c
// 读取当前时间（32 位绝对时钟 ticks）
uint32_t timer_read_time(void);

// 立即触发定时器调度
void timer_kick(void);

// 设置下一个定时器唤醒时间
void timer_kick_next(uint32_t next_time);

// 时间比较（处理 32 位溢出）
uint8_t timer_is_before(uint32_t time1, uint32_t time2);

// 微秒转 ticks
uint32_t timer_from_us(uint32_t us);
```

### Timer1 配置（ATmega328P）

| 寄存器 | 值 | 说明 |
|--------|-----|------|
| TCCR1A | 0x00 | 正常模式 |
| TCCR1B | 0x01 | 无预分频 (16 MHz) |
| TIMSK1 | 0x02 | 使能 OCIE1A |
| OCR1A | 动态 | 下一个唤醒时间 |

### ISR 时序常量

```c
#define TIMER_REPEAT_TICKS      3000    // 重复检查间隔
#define TIMER_MIN_ENTRY_TICKS   44      // ISR 入口延迟
#define TIMER_MIN_EXIT_TICKS    47      // ISR 出口延迟
#define TIMER_MIN_TRY_TICKS     91      // 最小尝试间隔
#define TIMER_DEFER_REPEAT_TICKS 256    // 延迟重复间隔
```

### 32 位定时器扩展

ATmega328P 的 Timer1 是 16 位的，通过 `wrap_timer` 软件定时器追踪高 16 位溢出：

```c
static uint16_t timer_high;  // 高 16 位计数器
static struct timer wrap_timer;  // 溢出检测定时器
```

## 3. hal_serial.h — 串口接口

### 架构

```
┌─────────────────────┐
│ generic/serial_irq.c │ ← Klipper 协议层
│ - serial_rx_byte()   │
│ - serial_get_tx_byte │
│ - console_sendf()    │
│ - console_task()     │
├─────────────────────┤
│ arduino/serial.cpp   │ ← HAL 实现
│ - serial_enable_tx_irq│
│ - arduino_serial_drain_rx│
│ - arduino_serial_rx_pending│
│ - arduino_serial_init│
├─────────────────────┤
│ Arduino HardwareSerial│ ← 框架层
└─────────────────────┘
```

### 接口

```c
// 初始化串口
void arduino_serial_init(void);

// 检查是否有待接收数据
bool arduino_serial_rx_pending(void);

// 从 Arduino 缓冲区读取数据到 Klipper 协议层
void arduino_serial_drain_rx(void);

// 启动发送（将 Klipper 缓冲区数据写入硬件）
void serial_enable_tx_irq(void);
```

### 缓冲区配置

```c
#define RX_BUFFER_SIZE 192  // 接收缓冲区
// 发送缓冲区: 192 bytes
```

### 波特率

- 默认: 115200 (Uno)
- Mega: 250000

## 4. hal_irq.h — 中断管理接口

### 接口

```c
typedef unsigned long irqstatus_t;

void irq_disable(void);           // 禁用全局中断
void irq_enable(void);            // 启用全局中断
irqstatus_t irq_save(void);       // 保存并禁用中断
void irq_restore(irqstatus_t flag); // 恢复中断状态
void irq_wait(void);              // 等待中断（idle 模式）
void irq_poll(void);              // 轮询处理待处理事件
```

### irq_wait() 行为

| 平台 | 行为 |
|------|------|
| AVR | `sei; drain_serial/nop; cli` — 定时器在 ISR 中处理 |
| ARM | `__enable_irq; nop; __disable_irq; drain_serial; check_timer` |
| ESP32 | `interrupts; nop; noInterrupts; drain_serial; check_timer` |

### irq_poll() 行为

| 平台 | 行为 |
|------|------|
| AVR | 仅 drain serial（定时器在 ISR 中处理） |
| ARM/ESP32 | drain serial + 检查定时器 |

## 5. 平台检测宏和条件编译策略

### 平台检测

```c
// AVR 系列 (ATmega328P, ATmega2560)
#if defined(__AVR__)

// ARM 系列 (Arduino Due, Teensy 3.x/4.x)
#elif defined(__arm__) || defined(__ARM_ARCH)

// ESP32 / 其他
#else

#endif
```

### 功能宏

```c
// autoconf.h 中定义
CONFIG_MACH_ARDUINO        // Arduino 框架
CONFIG_MACH_AVR            // AVR 架构
CONFIG_CLOCK_FREQ          // 时钟频率 (16000000UL)
CONFIG_SERIAL_BAUD         // 串口波特率
CONFIG_WANT_STEPPER        // 步进电机支持
CONFIG_INLINE_STEPPER_HACK // ISR 内联步进分发
CONFIG_AVR_STACK_SIZE      // AVR 栈大小
```

### 条件编译策略

1. **架构隔离**: 使用 `#if defined(__AVR__)` / `#elif defined(__arm__)` 隔离平台代码
2. **功能开关**: 使用 `CONFIG_WANT_*` 宏控制功能模块
3. **性能优化**: AVR 上使用 `CONFIG_INLINE_STEPPER_HACK` 绕过函数指针调用
4. **内存优化**: AVR 上使用 PROGMEM 存储常量数据

## 文件映射

| HAL 模块 | 头文件路径 | 实现文件路径 |
|----------|-----------|-------------|
| GPIO | `src/board/gpio.h` → `src/generic/gpio.h` | `src/arduino/gpio.c` |
| Timer | `src/board/timer_irq.h` → `src/generic/timer_irq.h` | `src/arduino/timer.c` + `src/generic/timer_irq.c` |
| Serial | `src/board/serial_irq.h` → `src/generic/serial_irq.h` | `src/arduino/serial.cpp` + `src/generic/serial_irq.c` |
| IRQ | `src/board/irq.h` → `src/arduino/irq.h` | `src/arduino/irq.c` |
| IO | `src/board/io.h` → `src/arduino/io.h` | 内联函数 |
| PGM | `src/board/pgm.h` → `src/arduino/pgm.h` | 宏定义 |
| Misc | `src/board/misc.h` → `src/arduino/misc.h` | 分散在多个文件中 |

## 内存布局 (ATmega328P)

```
Flash: 32KB
├── 代码段 (.text)        ~16KB
├── 常量数据 (.rodata)     ~2KB (含 PROGMEM)
└── 向量表                 ~0.4KB

SRAM: 2KB
├── 全局变量 (.data/.bss)  ~1.4KB
├── 堆 (dynamic alloc)     ~0.3KB
└── 栈                     ~0.3KB (CONFIG_AVR_STACK_SIZE=128)
```

## 设计决策记录

1. **ISR-Native vs Poll-Based**: AVR 使用 ISR-Native 模式，定时器调度在 Timer1 ISR 中完成，确保步进脉冲精度
2. **Arduino HardwareSerial vs 直接 UART**: 使用 Arduino 框架的 HardwareSerial，牺牲少量性能换取兼容性
3. **digitalWrite vs 端口寄存器**: 当前使用 Arduino API，未来可优化为直接端口操作
4. **软件溢出检测**: 使用 wrap_timer 软件定时器追踪 Timer1 的 16→32 位溢出
