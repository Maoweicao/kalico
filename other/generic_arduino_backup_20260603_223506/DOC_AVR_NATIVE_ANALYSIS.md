# Klipper AVR 原生固件实现 — 完整技术分析

## 目录

- [1. 总体架构概览](#1-总体架构概览)
- [2. AVR 平台适配层](#2-avr-平台适配层)
  - [2.1 main.c — 入口与启动](#21-mainc--入口与启动)
  - [2.2 irq.h — 中断管理](#22-irqh--中断管理)
  - [2.3 internal.h — GPIO 寄存器抽象](#23-internalh--gpio-寄存器抽象)
  - [2.4 pgm.h — PROGMEM 闪存读取](#24-pgmh--progmem-闪存读取)
  - [2.5 gpio.c / gpio.h — 数字 GPIO](#25-gpioc--gpioh--数字-gpio)
  - [2.6 adc.c — ADC 模数转换](#26-adcc--adc-模数转换)
  - [2.7 timer.c — 定时器与 32 位时钟](#27-timerc--定时器与-32-位时钟)
  - [2.8 serial.c — UART 串口](#28-serialc--uart-串口)
  - [2.9 usbserial.c — USB CDC 虚拟串口](#29-usbserialc--usb-cdc-虚拟串口)
  - [2.10 spi.c — SPI 总线](#210-spic--spi-总线)
  - [2.11 i2c.c — I2C/TWI 总线](#211-i2cc--i2ctwi-总线)
  - [2.12 hard_pwm.c — 硬件 PWM](#212-hard_pwmc--硬件-pwm)
  - [2.13 watchdog.c — 看门狗](#213-watchdogc--看门狗)
- [3. 通用核心层 (src/)](#3-通用核心层-src)
  - [3.1 sched.c / sched.h — 调度器](#31-schedc--schedh--调度器)
  - [3.2 command.c / command.h — 命令协议](#32-commandc--commandh--命令协议)
  - [3.3 basecmd.c / basecmd.h — 基础命令与内存管理](#33-basecmdc--basecmdh--基础命令与内存管理)
  - [3.4 gpiocmds.c — GPIO 命令层](#34-gpiocmdsc--gpio-命令层)
  - [3.5 stepper.c / stepper.h — 步进电机驱动](#35-stepperc--stepperh--步进电机驱动)
  - [3.6 trsync.c / trsync.h — 同步触发系统](#36-trsyncc--trsynch--同步触发系统)
  - [3.7 endstop.c — 限位开关](#37-endstopc--限位开关)
  - [3.8 tmcuart.c — TMC UART 通信](#38-tmcuartc--tmc-uart-通信)
  - [3.9 thermocouple.c — 热电偶传感器](#39-thermocouplec--热电偶传感器)
  - [3.10 sensor_adxl345.c — 加速度传感器](#310-sensor_adxl345c--加速度传感器)
  - [3.11 initial_pins.c — 初始引脚配置](#311-initial_pinsc--初始引脚配置)
- [4. 构建系统](#4-构建系统)
- [5. 整体数据流与架构图](#5-整体数据流与架构图)
- [6. 总结](#6-总结)

---

## 1. 总体架构概览

Klipper 的 AVR 固件采用 **双层架构**：

- **平台适配层** (`src/avr/`)：直接操作 AVR 硬件寄存器，提供统一的 GPIO、ADC、Timer、Serial、SPI、I2C、PWM、Watchdog 抽象
- **通用核心层** (`src/`)：实现调度器、命令协议、步进电机控制、传感器管理等平台无关逻辑

两层通过标准头文件接口 (`board/gpio.h`, `board/irq.h`, `board/misc.h`, `board/pgm.h`) 解耦。

### 支持的 MCU

| MCU 型号 | Flash | RAM | 特性 |
|----------|-------|-----|------|
| ATmega168 | 16KB | 1KB | 基础型 |
| ATmega328/328p | 32KB | 2KB | Arduino Uno 主控 |
| ATmega644p | 64KB | 4KB | 多 UART |
| ATmega1284p | 128KB | 16KB | 大 RAM |
| AT90USB646/1286 | 64/128KB | 4/8KB | 内置 USB |
| ATmega32u4 | 32KB | 2.5KB | Arduino Leonardo |
| ATmega1280/2560 | 128/256KB | 8/16KB | Arduino Mega |

---

## 2. AVR 平台适配层

### 2.1 main.c — 入口与启动

**文件**: `src/avr/main.c` (72 行)

**功能**：
- 程序入口点 `main()`，调用 `irq_enable()` 后进入 `sched_main()` 主循环
- `dynmem_start()` / `dynmem_end()`：动态内存边界，从链接器符号 `_end` 到 `SP - STACK_SIZE`
- `prescaler_init()`：时钟预分频器初始化（DECL_INIT），处理 AT90USB 系列的 1/8 分频问题
- `crc16_ccitt()`：利用 AVR 内置 `_crc_ccitt_update` 指令的优化 CRC16 实现

**关键细节**：
```c
// 动态内存：从 _end 到 (SP & ~0xFF) - STACK_SIZE
void *dynmem_end(void) {
    return (void*)ALIGN(AVR_STACK_POINTER_REG, 256) - CONFIG_AVR_STACK_SIZE;
}
```
- 堆栈默认 256 字节 (`CONFIG_AVR_STACK_SIZE`)
- 时钟预分频设置需要特殊的写保护序列：先写 `CLKPR = 0x80`，再写实际值

---

### 2.2 irq.h — 中断管理

**文件**: `src/avr/irq.h` (38 行)

**核心函数**：

| 函数 | 实现 | 说明 |
|------|------|------|
| `irq_disable()` | `cli(); barrier()` | 关中断 + 编译器屏障 |
| `irq_enable()` | `barrier(); sei()` | 编译器屏障 + 开中断 |
| `irq_save()` | 读 SREG → cli，返回旧 SREG | 保存并关中断 |
| `irq_restore(flag)` | `barrier(); SREG = flag` | 恢复中断状态 |
| `irq_wait()` | `sei; nop; cli` | 原子等待一个中断周期 |
| `irq_poll()` | 空操作 | AVR 上无需轮询 |

**数据类型**：`irqstatus_t` = `uint8_t`（SREG 寄存器大小）

**设计要点**：
- `irq_save/restore` 不使用嵌套计数器，而是直接保存/恢复 SREG，效率最高
- `irq_wait()` 实现了单周期中断窗口：sei → nop → cli，允许一个中断在此期间触发
- `barrier()` 编译器内存屏障防止指令重排跨越中断边界

---

### 2.3 internal.h — GPIO 寄存器抽象

**文件**: `src/avr/internal.h` (18 行)

**核心定义**：

```c
#define GPIO(PORT, NUM)  (((PORT)-'A') * 8 + (NUM))   // 引脚编码: port*8 + bit
#define GPIO2PORT(PIN)   ((PIN) / 8)                    // 提取端口号
#define GPIO2BIT(PIN)    (1<<((PIN) % 8))               // 提取位掩码

struct gpio_digital_regs {
    volatile uint8_t in : 8, mode : 8, out : 8;  // PIN, DDR, PORT
};

#define GPIO2REGS(pin)  ((struct gpio_digital_regs*)READP(digital_regs[GPIO2PORT(pin)]))
```

**关键设计**：
- 将 AVR 的 PIN/DDR/PORT 三个寄存器封装为 `in/mode/out` 结构体
- 端口 A-L 映射为数字 0-11，每个端口 8 个引脚
- 通过 PROGMEM 指针表 `digital_regs[]` 间接访问，节省 RAM

---

### 2.4 pgm.h — PROGMEM 闪存读取

**文件**: `src/avr/pgm.h` (27 行)

**功能**：提供 `READP()` 宏，自动根据数据大小选择 `pgm_read_byte/word/dword`

```c
#define READP(VAR) ({
    __builtin_choose_expr(sizeof(VAR) == 1, (typeof(VAR))pgm_read_byte(&(VAR)),
    __builtin_choose_expr(sizeof(VAR) == 2, (typeof(VAR))pgm_read_word(&(VAR)),
    __builtin_choose_expr(sizeof(VAR) == 4, (typeof(VAR))pgm_read_dword(&(VAR)),
    __force_link_error__unknown_type)));
})
```

**作用**：AVR 的 Harvard 架构要求从 Flash 读取数据使用特殊指令（LPM），`READP` 统一了 RAM 和 Flash 的访问接口。所有静态配置表（引脚映射、PWM 信息等）都存放在 PROGMEM 中。

---

### 2.5 gpio.c / gpio.h — 数字 GPIO

**文件**: `src/avr/gpio.c` (130 行) + `src/avr/gpio.h` (57 行)

**数据结构**：
```c
struct gpio_out { struct gpio_digital_regs *regs; uint8_t bit; };
struct gpio_in  { struct gpio_digital_regs *regs; uint8_t bit; };
```

**引脚枚举**：
- PA0-PA7, PB0-PB7, PC0-PC7, PD0-PD7 等通过 `DECL_ENUMERATION_RANGE` 注册
- ATmega328p 额外定义 PE0（328pb 特有）

**函数列表**：

| 函数 | 功能 | 关键操作 |
|------|------|---------|
| `gpio_out_setup(pin, val)` | 配置输出引脚 | 查表 → reset → 设置 DDR=1 |
| `gpio_out_reset(g, val)` | 重置输出状态 | irq_save → 设置 PORT 和 DDR |
| `gpio_out_write(g, val)` | 写输出值 | irq_save → 置位/清除 PORT |
| `gpio_out_toggle_noirq(g)` | 原子翻转 | 写 PIN 寄存器（AVR 硬件翻转特性）|
| `gpio_out_toggle(g)` | 翻转（同上） | 调用 toggle_noirq |
| `gpio_in_setup(pin, pull_up)` | 配置输入引脚 | DDR=0, 可选上拉 |
| `gpio_in_reset(g, pull_up)` | 重置输入 | 设置 PORT 上拉位 |
| `gpio_in_read(g)` | 读取输入 | 读 PIN 寄存器 |

**AVR 特有优化**：
- **硬件翻转**：写 1 到 PIN 寄存器的某位会翻转对应 PORT 位，无需读-改-写
- `digital_regs[]` 表存放在 PROGMEM，通过 `READP()` 访问
- 所有写操作使用 `irq_save/restore` 保护原子性

---

### 2.6 adc.c — ADC 模数转换

**文件**: `src/avr/adc.c` (122 行)

**数据结构**：
```c
struct gpio_adc { uint8_t chan; };  // 仅需通道号
```

**引脚映射表** (PROGMEM)：

| MCU | ADC 通道引脚 |
|-----|-------------|
| ATmega168/328 | PC0-PC5, PE2, PE3 |
| ATmega644p/1284p | PA0-PA7 |
| AT90USB/ATmega32u4 | PF0-PF7 (+ PD4,PD6,PD7,PB4 for 32u4) |
| ATmega1280/2560 | PF0-PF7, PK0-PK7 |

**函数列表**：

| 函数 | 功能 | 说明 |
|------|------|------|
| `gpio_adc_setup(pin)` | 初始化 ADC | 查找通道 → 使能 ADC → 禁用数字输入 |
| `gpio_adc_sample(g)` | 启动/检查采样 | 状态机：忙→等待, 同通道→就绪, 空闲→启动 |
| `gpio_adc_read(g)` | 读取结果 | 返回 ADC 寄存器值，重置状态 |
| `gpio_adc_cancel_sample(g)` | 取消采样 | 重置 last_analog_read |

**关键常量**：
- `ADMUX_DEFAULT = 0x40`：AVcc 参考电压，右对齐
- `ADC_ENABLE`：PS=128 分频（16MHz → 125KHz ADC 时钟），使能 ADC
- `ADC_MAX = 1023`：10 位分辨率
- 采样延迟：`(13+1)*128 + 200` 时钟周期（≈14 转换周期 × 128 分频 + 余量）

**状态管理**：
- 使用全局 `last_analog_read` 跟踪当前采样通道
- `ADC_DUMMY = 0xFF` 表示空闲状态
- 避免同时对多通道采样（单 ADC 资源）

**MUX5 支持**：ATmega2560 等芯片的 ADC 通道 8-15 需要设置 ADCSRB 的 MUX5 位。

---

### 2.7 timer.c — 定时器与 32 位时钟

**文件**: `src/avr/timer.c` (211 行)

**核心设计**：使用 **Timer1** (16 位) 硬件定时器，软件扩展为 32 位时钟。

**数据结构**：
```c
union u32_u {
    struct { uint8_t b0, b1, b2, b3; };
    struct { uint16_t lo, hi; };
    uint32_t val;
};
static uint16_t timer_high;  // 高 16 位溢出计数器
```

**函数列表**：

| 函数 | 功能 | 说明 |
|------|------|------|
| `timer_from_us(us)` | 微秒→时钟周期 | `us * (CLOCK_FREQ / 1000000)` |
| `timer_is_before(t1, t2)` | 时间比较 | 手写汇编优化，处理回绕 |
| `timer_get()` | 读 TCNT1 | 16 位硬件计数器 |
| `timer_set(next)` | 设置 OCR1A | 下一个比较匹配值 |
| `timer_repeat_set(next)` | 设置 OCR1B | 防止重复执行限制 |
| `timer_kick()` | 立即触发中断 | 设置 OCR1A = TCNT1 + 50 |
| `timer_read_time()` | 读 32 位时间 | 高 16 位 + 低 16 位，处理溢出 |
| `timer_init()` | 初始化 Timer1 | Normal 模式，CS10=1（无分频）|
| `timer_reset()` | 重置 wrap_timer | shutdown 时调用 |

**32 位时间读取算法**：
```c
uint32_t timer_read_time(void) {
    irq_save();
    calc.val = TCNT1;
    calc.hi = timer_high;
    if (TIFR1 & (1<<TOV1)) {    // 硬件溢出标志
        irq_restore();
        if (calc.b1 < 0xff)     // 溢出发生在读取之后
            calc.hi++;
        return calc.val;
    }
    irq_restore();
    return calc.val;
}
```

**wrap_timer**：每约 2ms 执行一次，更新 `timer_high` 溢出计数器，确保 32 位时间连续。

**Timer1 中断处理 (ISR)**：
```c
ISR(TIMER1_COMPA_vect) {
    for (;;) {
        next = sched_timer_dispatch();  // 执行软件定时器回调
        // 检查下一个定时器是否已到时
        // 如果接近，短暂开中断后继续
        // 使用 OCR1B 防止无限循环（TIMER_REPEAT_TICKS = 3000）
    }
}
```

**关键常量**：
- `TIMER_REPEAT_TICKS = 3000`：单次 IRQ 最大执行时间
- `TIMER_MIN_ENTRY_TICKS = 44`：中断入口开销
- `TIMER_MIN_EXIT_TICKS = 47`：中断出口开销
- `TIMER_DEFER_REPEAT_TICKS = 256`：延迟重试间隔

**timer_is_before 汇编优化**：
```asm
cp  %A1, %A2    ; 比较低 16 位
cpc %B1, %B2    ; 带借位比较
cpc %C1, %C2
sbc %0,  %D2   ; 带借位减法，结果在高位
```
等价于 `(int32_t)(time1 - time2) < 0`，但手写汇编减少寄存器压力。

---

### 2.8 serial.c — UART 串口

**文件**: `src/avr/serial.c` (88 行)

**支持的串口**：
- UART0 (默认，ATmega328: PD0/PD1, ATmega2560: PE0/PE1)
- UART1 (PD2/PD3)
- UART2 (PH0/PH1，仅 ATmega2560/1280)
- UART3 (PJ0/PJ1，仅 ATmega2560/1280)

**宏技巧**：通过 `AVR_SERIAL_REG` 宏将串口号拼接到寄存器名：
```c
#define UCSRxA  AVR_SERIAL_REG(UCSR, CONFIG_SERIAL_PORT, A)  // → UCSR0A
```

**函数列表**：

| 函数 | 功能 |
|------|------|
| `serial_init()` | 配置波特率、8N1、使能收发和中断 |
| `ISR(USARTx_RX_vect)` | 接收中断 → `serial_rx_byte(UDRx)` |
| `ISR(USARTx_UDRE_vect)` | 发送空中断 → `serial_get_tx_byte()` |
| `serial_enable_tx_irq()` | 使能 UDRE 中断 |

**波特率计算**：
```c
UBRRx = DIV_ROUND_CLOSEST(CLOCK_FREQ, cm * BAUD) - 1;
// cm = 8 (U2X 模式) 或 16 (正常模式)
```

**与通用层接口**：
- `serial_rx_byte()` / `serial_get_tx_byte()` 由 `generic/serial_irq.c` 提供
- `serial_enable_tx_irq()` 供通用层调用以启动发送

---

### 2.9 usbserial.c — USB CDC 虚拟串口

**文件**: `src/avr/usbserial.c` (255 行)

**支持芯片**：AT90USB1286, AT90USB646, ATmega32u4

**端点配置**：
| 端点 | 类型 | 缓冲 |
|------|------|------|
| EP0 | Control | 单缓冲 |
| CDC ACM | Interrupt IN | 单缓冲 |
| CDC Bulk OUT | Bulk OUT | 双缓冲 |
| CDC Bulk IN | Bulk IN | 双缓冲 |

**函数列表**：

| 函数 | 功能 |
|------|------|
| `usb_read_bulk_out()` | 读取 USB 批量输出数据 |
| `usb_send_bulk_in()` | 发送 USB 批量输入数据 |
| `usb_read_ep0()` | 读取 EP0 数据 |
| `usb_read_ep0_setup()` | 读取 EP0 SETUP 包 |
| `usb_send_ep0()` | 发送 EP0 数据 |
| `usb_send_ep0_progmem()` | 从 PROGMEM 发送 EP0 数据 |
| `usb_stall_ep0()` | STALL EP0 |
| `usb_set_address()` | 设置 USB 地址（延迟到 ACK 发送后）|
| `usb_set_configure()` | 配置 CDC 端点 |
| `usbserial_init()` | USB 硬件初始化 |

**初始化序列**：
1. `UHWCON` → 设备模式 + 电压调节器
2. `USBCON` → 使能 USB + 冻结时钟
3. `PLLCSR` → 配置 PLL（48MHz USB 时钟）
4. 等待 PLL 锁定
5. `UDCON` → 使能上拉
6. `UDIEN` → 使能 EORST 中断

**中断处理**：
- `ISR(USB_GEN_vect)`：USB 复位完成 → 配置 EP0
- `ISR(USB_COM_vect)`：端点中断 → 通知通用层（`usb_notify_ep0/bulk_out/bulk_in`）

**地址设置延迟**：`usb_set_address()` 保存地址，等 EP0 ACK 发送完成后才写 `UDADDR`。

---

### 2.10 spi.c — SPI 总线

**文件**: `src/avr/spi.c` (106 行)

**引脚映射**：

| MCU | MISO | MOSI | SCK | SS |
|-----|------|------|-----|----|
| ATmega168/328 | PB4 | PB3 | PB5 | PB2 |
| ATmega644p/1284p | PB6 | PB5 | PB7 | PB4 |
| AT90USB/ATmega32u4/Mega | PB3 | PB2 | PB1 | PB0 |

**函数列表**：

| 函数 | 功能 |
|------|------|
| `spi_setup(bus, mode, rate)` | 配置 SPI 主机模式、速率、极性 |
| `spi_prepare(config)` | 写入 SPCR/SPSR 配置 |
| `spi_transfer(config, recv, len, data)` | 执行 SPI 传输 |

**速率分频**：
```
F_CPU/2   → SPI2X=1, SPR=0
F_CPU/4   → SPI2X=0, SPR=0
F_CPU/8   → SPI2X=1, SPR=1
F_CPU/16  → SPI2X=0, SPR=1
F_CPU/32  → SPI2X=1, SPR=2
F_CPU/64  → SPI2X=0, SPR=2
F_CPU/128 → SPI2X=0, SPR=3
```

**初始化**：确保 SS 引脚为输出（AVR SPI 主机要求），设置 MSTR + SPE。

---

### 2.11 i2c.c — I2C/TWI 总线

**文件**: `src/avr/i2c.c` (128 行)

**引脚映射**：

| MCU | SCL | SDA |
|-----|-----|-----|
| ATmega168/328 | PC5 | PC4 |
| ATmega644p/1284p | PC0 | PC1 |
| AT90USB/ATmega32u4/Mega | PD0 | PD1 |

**函数列表**：

| 函数 | 功能 |
|------|------|
| `i2c_setup(bus, rate, addr)` | 初始化 TWI，配置速率 |
| `i2c_write(config, len, data)` | 写数据到从设备 |
| `i2c_read(config, reg_len, reg, read_len, data)` | 先写寄存器地址再读数据 |

**内部函数**：
- `i2c_wait(timeout)`：等待 TWINT 标志，带超时（5ms）
- `i2c_start(timeout)`：发送 START/REPEATED START
- `i2c_send_byte(b, timeout)`：发送字节
- `i2c_receive_byte(read, timeout, ack)`：接收字节，可选 ACK/NACK
- `i2c_stop(timeout)`：发送 STOP

**速率配置**：
```c
TWBR = ((CLOCK_FREQ / rate) - 16) / 2;  // TWPS=0 (TWSR=0)
```
- 400KHz 快速模式或 100KHz 标准模式

**地址格式**：`config.addr = addr << 1`（7 位地址左移，最低位由 R/W 控制）

---

### 2.12 hard_pwm.c — 硬件 PWM

**文件**: `src/avr/hard_pwm.c` (147 行)

**PWM 定时器资源**（以 ATmega2560 为例）：

| 定时器 | OCR | 引脚 | 分辨率 |
|--------|-----|------|--------|
| Timer0 | OCR0A/B | PB7, PG5 | 8 位 |
| Timer1 | OCR1A/B/C | PB5, PB6, PB7 | 16 位 |
| Timer2 | OCR2A/B | PB4, PH6 | 8 位 |
| Timer3 | OCR3A/B/C | PE3, PE4, PE5 | 16 位 |
| Timer4 | OCR4A/B/C | PH3, PH4, PH5 | 16 位 |
| Timer5 | OCR5A/B/C | PL3, PL4, PL5 | 16 位 |

**重要限制**：Timer1 被定时器系统占用，**不能用于 PWM**。

**数据结构**：
```c
struct gpio_pwm_info {
    uint8_t pin;
    volatile void *ocr;         // OCR 寄存器地址
    volatile uint8_t *rega, *regb;  // TCCRxA, TCCRxB
    uint8_t en_bit;             // COM 位
    uint8_t flags;              // GP_8BIT, GP_AFMT
};
struct gpio_pwm { void *reg; uint8_t size8; };
```

**函数列表**：

| 函数 | 功能 |
|------|------|
| `gpio_pwm_setup(pin, cycle_time, val)` | 配置 PWM 输出 |
| `gpio_pwm_write(g, val)` | 设置占空比 (0-255) |

**时钟分频选择**：
- 8 位定时器 (Timer0/2)：CS=1-7，从 F_CPU/1 到 F_CPU/1024
- 16 位定时器 (Timer1/3/4/5)：CS=1-5，从 F_CPU/1 到 F_CPU/1024
- 异步格式定时器 (Timer2) 有不同的分频比

**PWM 模式**：快速 PWM (`WGM00=1`)，单斜率计数。

**常量**：`PWM_MAX = 255`（8 位分辨率）

---

### 2.13 watchdog.c — 看门狗

**文件**: `src/avr/watchdog.c` (58 行)

**函数列表**：

| 函数 | 功能 | 触发方式 |
|------|------|---------|
| `watchdog_init()` | 0.5s 超时，中断+复位模式 | DECL_INIT |
| `watchdog_reset()` | 喂狗 + 恢复中断模式 | DECL_TASK |
| `watchdog_early_init()` | .init3 段，禁用看门狗 | 链接器段 |
| `command_reset()` | 软复位（15ms 看门狗超时）| DECL_COMMAND |

**工作机制**：
1. `.init3` 段在 `main()` 前执行，清除 MCUSR 并禁用看门狗
2. `watchdog_init()` 启用 500ms 看门狗，设置为中断模式
3. `watchdog_reset()` 每个任务周期喂狗
4. 若超时触发 `ISR(WDT_vect)` → `shutdown("Watchdog timer!")`
5. 软复位：禁中断 → 启用 15ms 看门狗 → 死循环等待复位

**DECL_COMMAND_FLAGS**：`command_reset` 带 `HF_IN_SHUTDOWN` 标志，shutdown 状态下仍可执行。

---

## 3. 通用核心层 (src/)

### 3.1 sched.c / sched.h — 调度器

**文件**: `src/sched.c` (360 行) + `src/sched.h` (48 行)

**核心数据结构**：
```c
struct timer {
    struct timer *next;
    uint_fast8_t (*func)(struct timer*);
    uint32_t waketime;
};
enum { SF_DONE=0, SF_RESCHEDULE=1 };

struct task_wake { uint8_t wake; };
```

**调度器状态**：
```c
static struct {
    struct timer *timer_list, *last_insert;
    int8_t tasks_status, tasks_busy;
    uint8_t shutdown_status, shutdown_reason;
} SchedStatus;
```

**定时器管理**：

| 函数 | 功能 |
|------|------|
| `sched_add_timer(add)` | 按 waketime 插入有序链表 |
| `sched_del_timer(del)` | 从链表删除（使用 deleted_timer 占位）|
| `sched_timer_dispatch()` | 执行链表头定时器，返回下一个唤醒时间 |
| `sched_timer_reset()` | 清除所有用户定时器 |

**三个特殊定时器**：
1. `periodic_timer`：每 100ms 唤醒一次，确保 stats 任务运行
2. `sentinel_timer`：链表尾哨兵，waketime = periodic + 0x80000000
3. `deleted_timer`：删除占位符，避免中断上下文中的链表修改

**任务系统**：
```c
enum { TS_IDLE=-1, TS_REQUESTED=0, TS_RUNNING=1 };
```
- `sched_wake_tasks()` → 设置 tasks_status = TS_REQUESTED
- `sched_wake_task(w)` → 设置 wake 标志 + 唤醒任务
- `sched_check_wake(w)` → 检查并清除 wake 标志

**主循环** (`run_tasks`)：
```
while (1) {
    if (无任务请求) {
        irq_disable();
        tasks_status = IDLE;
        do { irq_wait(); } while (status != REQUESTED);
        irq_enable();
    }
    tasks_status = RUNNING;
    ctr_run_taskfuncs();    // 执行所有 DECL_TASK
    stats_update(start, cur);
}
```

**Shutdown 机制**：
- `sched_shutdown(reason)` → `longjmp(shutdown_jmp, reason)` 立即跳转
- `run_shutdown()` → 禁中断 → 重置定时器 → 执行所有 DECL_SHUTDOWN → 发送 shutdown 消息
- 使用 `setjmp/longjmp` 实现非本地跳转

**`sched_timer_dispatch()` 优化**：
```c
if (CONFIG_INLINE_STEPPER_HACK && likely(!t->func)) {
    res = stepper_event(t);  // 内联优化：步进电机无 func 指针
}
```

---

### 3.2 command.c / command.h — 命令协议

**文件**: `src/command.c` (366 行) + `src/command.h` (111 行)

**消息格式**：
```
[LEN] [SEQ] [MSGID VLQ] [PARAMS...] [CRC_HI] [CRC_LO] [SYNC=0x7E]
```
- 最小 5 字节，最大 64 字节
- LEN: 总长度（含头尾）
- SEQ: 序列号 (4 位) + 目标标识 (4 位 = 0x10)
- SYNC: 0x7E 帧同步字节

**VLQ 编码**：
```c
// 编码：符号扩展，5/12/19/26 位边界判断
// 解码：高位连续 → 右移 7 位拼接
```

**命令解析器**：
```c
struct command_parser {
    uint16_t encoded_msgid;
    uint8_t num_args, flags, num_params;
    const uint8_t *param_types;   // PROGMEM
    void (*func)(uint32_t *args);
};
```

**参数类型**：`PT_uint32, PT_int32, PT_uint16, PT_int16, PT_byte, PT_string, PT_buffer, PT_progmem_buffer`

**关键函数**：

| 函数 | 功能 |
|------|------|
| `command_parsef()` | 解析命令参数到 args 数组 |
| `command_encodef()` | 编码响应消息 |
| `command_add_frame()` | 添加 LEN/SEQ/CRC/SYNC 帧 |
| `command_find_block()` | 在接收缓冲区中查找完整消息 |
| `command_dispatch()` | 解析并执行消息中的所有命令 |
| `command_sendf()` | 编码并发送响应（带 IRQ 重入保护）|
| `command_find_and_dispatch()` | 查找 + 执行 + 发送 ACK |

**消息查找状态机**：
```
NEED_SYNC → 扫描 SYNC 字节
检查 LEN 范围 [5, 64]
检查 SEQ 目标
检查尾部 SYNC
验证 CRC16
检查序列号（丢帧则 NAK）
```

**DECL_ 宏系统**：
- `DECL_COMMAND(func, "msg_spec")` → 注册命令处理器
- `DECL_CONSTANT(name, value)` → 导出常量到主机
- `DECL_ENUMERATION(enum, name, value)` → 导出枚举
- `sendf("fmt", args...)` → 发送响应消息
- `shutdown("msg")` → 紧急停机

这些宏通过 `DECL_CTR` 写入编译时请求文件，由 Python 工具链在编译期间生成 `compile_time_request.c`。

---

### 3.3 basecmd.c / basecmd.h — 基础命令与内存管理

**文件**: `src/basecmd.c` (374 行) + `src/basecmd.h` (32 行)

**内存分配器**：
```c
static void *alloc_end;  // 堆指针（只增不减）

void *alloc_chunk(size_t size);     // 分配并对齐
void *alloc_chunks(size, count, *avail); // 分配数组
```
- 从 `dynmem_start()` 到 `dynmem_end()` 线性分配
- 无 free 功能（shutdown 时整体重置）

**Move Queue 系统**：
```c
struct move_node { struct move_node *next; };
struct move_queue_head { struct move_node *first, *last; };
```
- 空闲链表 `move_free_list`：预分配 1024 个节点
- `move_alloc()` → 从空闲链表取（IRQ 安全）
- `move_free(m)` → 归还到空闲链表
- `move_queue_push/pop/first/empty/clear` → FIFO 队列操作

**OID (Object ID) 系统**：
```c
struct oid_s { void *type, *data; };
static struct oid_s *oids;
```
- `oid_alloc(oid, type, size)` → 分配对象
- `oid_lookup(oid, type)` → 查找对象（类型检查）
- `oid_next(i, type)` → 遍历同类型对象

**注册的命令**：

| 命令 | 功能 |
|------|------|
| `allocate_oids count=%c` | 分配 OID 空间 |
| `finalize_config crc=%u` | 固化配置 + 分配 move queue |
| `get_config` | 查询配置状态 |
| `get_clock` | 获取当前时钟 |
| `get_uptime` | 获取运行时间 |
| `emergency_stop` | 紧急停机 |
| `clear_shutdown` | 清除停机状态 |
| `identify offset=%u count=%c` | 读取固件标识数据 |

**统计系统** (`stats_update`)：
- 每 5 秒发送一次 `stats count=%u sum=%u sumsq=%u`
- 记录任务执行次数、累计时间、时间平方和（用于计算 CPU 负载）

---

### 3.4 gpiocmds.c — GPIO 命令层

**文件**: `src/gpiocmds.c` (215 行)

**数据结构**：
```c
struct digital_out_s {
    struct timer timer;
    uint32_t on_duration, off_duration, end_time;
    struct gpio_out pin;
    uint32_t max_duration, cycle_time;
    struct move_queue_head mq;
    uint8_t flags;
};
struct digital_move {
    struct move_node node;
    uint32_t waketime, on_duration;
};
```

**状态标志**：
- `DF_ON`：当前输出高
- `DF_TOGGLING`：软件 PWM 翻转中
- `DF_CHECK_END`：需要检查结束时间
- `DF_DEFAULT_ON`：shutdown 时默认值

**命令列表**：

| 命令 | 功能 |
|------|------|
| `config_digital_out` | 配置数字输出引脚 |
| `set_digital_out_pwm_cycle` | 设置软件 PWM 周期 |
| `queue_digital_out` | 排队输出事件（定时开/关）|
| `update_digital_out` | 立即更新输出值 |
| `set_digital_out` | 直接设置引脚（无 OID）|

**软件 PWM 机制**：
1. `queue_digital_out` 入队 `digital_move`
2. 首个入队项 → 安装 `digital_load_event` 定时器
3. `digital_load_event` → 从队列取出 → 设置输出 → 计算下一次事件
4. 若 `on_duration < cycle_time` → 切换到 `digital_load_event` 翻转模式
5. 翻转中：交替设置 `on_duration` 和 `off_duration` 唤醒

**Shutdown 处理**：所有输出恢复 `DF_DEFAULT_ON` 状态，清空队列。

---

### 3.5 stepper.c / stepper.h — 步进电机驱动

**文件**: `src/stepper.c` (393 行) + `src/stepper.h` (8 行)

**核心数据结构**：
```c
struct stepper_move {
    struct move_node node;
    uint32_t interval;      // 步进间隔（时钟周期）
    int16_t add;            // 加速度增量
    uint16_t count;         // 步数
    uint8_t flags;          // MF_DIR 方向变化
};

struct stepper {
    struct timer time;
    uint32_t interval, add;
    uint32_t count;
    uint32_t next_step_time, step_pulse_ticks;
    struct gpio_out step_pin, dir_pin;
    uint32_t position;
    struct move_queue_head mq;
    struct trsync_signal stop_signal;
    uint8_t flags;
};
```

**三种步进事件函数**：

| 函数 | 适用场景 | 特点 |
|------|---------|------|
| `stepper_event_full()` | 通用 | 完整调度，step/unstep 分开 |
| `stepper_event_avr()` | AVR 优化 | 在 ISR 内完成 step+unstep |
| `stepper_event_edge()` | 双边沿模式 | toggle 实现 step，count 减半 |

**AVR 优化路径** (`stepper_event_avr`)：
```c
gpio_out_toggle_noirq(s->step_pin);   // step 上升沿
count = s->count - 1;
if (likely(count)) {
    s->time.waketime += s->interval;
    gpio_out_toggle_noirq(s->step_pin);  // step 下降沿（在同一 ISR 内）
    if (s->flags & SF_HAVE_ADD) s->interval += s->add;
    return SF_RESCHEDULE;
}
stepper_load_next(s);
gpio_out_toggle_noirq(s->step_pin);   // unstep
```
- 使用 16 位 count（优化 AVR 寄存器使用）
- step/unstep 在同一中断内完成，无需两次调度
- `AVR_STEP_TICKS = 40`：最小脉冲宽度

**命令列表**：

| 命令 | 功能 |
|------|------|
| `config_stepper` | 配置步进电机（引脚、方向、脉冲宽度）|
| `queue_step` | 排队步进（interval, count, add）|
| `set_next_step_dir` | 设置下一步方向 |
| `reset_step_clock` | 重置时基 |
| `stepper_get_position` | 获取当前位置 |
| `stepper_stop_on_trigger` | 关联 trsync（归位用）|

**归位集成**：通过 `trsync_add_signal` 注册 `stepper_stop` 回调，限位触发时自动停止。

---

### 3.6 trsync.c / trsync.h — 同步触发系统

**文件**: `src/trsync.c` (203 行) + `src/trsync.h` (19 行)

**数据结构**：
```c
struct trsync_signal {
    struct trsync_signal *next;
    trsync_callback_t func;
};

struct trsync {
    struct timer report_time, expire_time;
    uint32_t report_ticks;
    struct trsync_signal *signals;   // 回调链表
    uint8_t flags, trigger_reason, expire_reason;
};
```

**工作流程**：
1. `trsync_start` → 初始化，设置报告定时器
2. 注册信号回调（如 `stepper_stop`）
3. 硬件触发（endstop）或超时 → `trsync_do_trigger()`
4. 触发时：遍历信号链表，依次调用回调
5. 设置 TSF_REPORT → 任务层报告给主机

**命令列表**：

| 命令 | 功能 |
|------|------|
| `config_trsync` | 配置同步触发器 |
| `trsync_start` | 启动监控 |
| `trsync_set_timeout` | 设置超时时间 |
| `trsync_trigger` | 手动触发 |

**任务层** (`trsync_task`)：检查 TSF_REPORT 标志，发送 `trsync_state` 消息。

---

### 3.7 endstop.c — 限位开关

**文件**: `src/endstop.c` (115 行)

**数据结构**：
```c
struct endstop {
    struct timer time;
    struct gpio_in pin;
    uint32_t rest_time, sample_time, nextwake;
    struct trsync *ts;
    uint8_t flags, sample_count, trigger_count, trigger_reason;
};
```

**采样机制**：
1. `endstop_event`：每 `rest_time` 周期读取引脚
2. 匹配时切换到 `endstop_oversample_event`
3. 过采样：连续 `sample_count` 次匹配 → `trsync_do_trigger`
4. 任何一次不匹配 → 回退到基础检测

**命令**：

| 命令 | 功能 |
|------|------|
| `config_endstop` | 配置限位引脚 |
| `endstop_home` | 启动归位检测 |
| `endstop_query_state` | 查询当前状态 |

---

### 3.8 tmcuart.c — TMC UART 通信

**文件**: `src/tmcuart.c` (249 行)

**功能**：软件实现 TMC2208/2209 步进驱动的单线 UART 协议。

**数据结构**：
```c
struct tmcuart_s {
    struct timer timer;
    struct gpio_out tx_pin;
    struct gpio_in rx_pin;
    uint8_t flags, pos, read_count, write_count;
    uint32_t cfg_bit_time, bit_time;
    uint8_t data[10];
};
```

**状态机**：
1. `tmcuart_send_sync_event`：发送同步 nibble（0x2A），校准实际波特率
2. `tmcuart_send_event`：逐位发送，跳过连续相同位（优化 toggle 次数）
3. `tmcuart_send_finish_event`：发送完成 → 准备接收
4. `tmcuart_read_sync_event`：等待 RX 起始位
5. `tmcuart_read_event`：逐位接收

**波特率校准**：通过测量同步 nibble 的实际 toggle 时间差，修正后续通信的 `bit_time`。

---

### 3.9 thermocouple.c — 热电偶传感器

**文件**: `src/thermocouple.c` (199 行)

**支持芯片**：MAX31855, MAX31856, MAX31865, MAX6675

**工作模式**：定时器触发 → 任务层通过 SPI 读取 → 发送结果到主机

**错误处理**：
- 可配置 `min_value`, `max_value`, `max_invalid_count`
- 超出范围或通信错误 → 递增 `invalid_count`
- 超过阈值 → `try_shutdown("Thermocouple reader fault")`

---

### 3.10 sensor_adxl345.c — 加速度传感器

**文件**: `src/sensor_adxl345.c` (161 行)

**功能**：通过 SPI 读取 ADXL345 三轴加速度数据，支持连续采集模式。

**使用 `sensor_bulk` 机制**批量传输数据，减少通信开销。

---

### 3.11 initial_pins.c — 初始引脚配置

**文件**: `src/initial_pins.c` (27 行)

**功能**：在 MCU 启动时（`DECL_INIT`）根据配置设置指定引脚的初始电平。

---

## 4. 构建系统

### Makefile

```makefile
CROSS_PREFIX=avr-
dirs-y += src/avr src/generic
CFLAGS += -mmcu=$(CONFIG_MCU)

src-y += avr/main.c avr/timer.c
src-$(CONFIG_HAVE_GPIO) += avr/gpio.c
src-$(CONFIG_WANT_GPIO_ADC) += avr/adc.c
src-$(CONFIG_WANT_GPIO_SPI) += avr/spi.c
src-$(CONFIG_WANT_GPIO_I2C) += avr/i2c.c
src-$(CONFIG_WANT_HARD_PWM) += avr/hard_pwm.c
src-$(CONFIG_AVR_WATCHDOG) += avr/watchdog.c
src-$(CONFIG_USBSERIAL) += avr/usbserial.c generic/usb_cdc.c
src-$(CONFIG_SERIAL) += avr/serial.c generic/serial_irq.c
```

**输出**：`klipper.elf.hex` (Intel HEX 格式)

**烧录**：`avrdude -p$(MCU) -c$(PROTOCOL) -P"$(FLASH_DEVICE)" -D -U"flash:w:hex:i"`

### Kconfig 特性

| 特性 | 说明 |
|------|------|
| `HAVE_GPIO` | 支持数字 GPIO |
| `HAVE_GPIO_ADC` | 支持 ADC |
| `HAVE_GPIO_SPI` | 支持 SPI |
| `HAVE_GPIO_I2C` | 支持 I2C |
| `HAVE_GPIO_HARD_PWM` | 支持硬件 PWM |
| `HAVE_STRICT_TIMING` | 严格时序要求 |
| `HAVE_LIMITED_CODE_SIZE` | Flash 受限（168/328/32u4）|

---

## 5. 整体数据流与架构图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        主机 (Klippy Python)                         │
│                     通过 USB/Serial 发送命令                         │
└────────────────────────────┬────────────────────────────────────────┘
                             │ 二进制协议 (VLQ + CRC16)
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    通信层 (USB CDC / UART)                           │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │ usbserial.c  │  │  serial.c    │                                │
│  │ (AT90USB/    │  │ (ATmega      │                                │
│  │  32u4)       │  │  168/328/    │                                │
│  │              │  │  644/2560)   │                                │
│  └──────┬───────┘  └──────┬───────┘                                │
│         │ generic/         │ generic/                               │
│         │ usb_cdc.c        │ serial_irq.c                          │
│         └────────┬─────────┘                                        │
└──────────────────┼──────────────────────────────────────────────────┘
                   ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    命令处理层 (command.c)                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐            │
│  │ 消息解析     │  │ VLQ 编解码   │  │ CRC16 校验       │            │
│  │ find_block  │  │ parse_int    │  │ crc16_ccitt      │            │
│  │ dispatch    │  │ encode_int   │  │ (AVR 硬件加速)    │            │
│  └──────┬──────┘  └──────────────┘  └─────────────────┘            │
│         ▼                                                           │
│  ┌──────────────────────────────────────────────────────┐           │
│  │              命令路由 (command_index[])                │           │
│  │  config_stepper / queue_step / config_digital_out ... │           │
│  └──────────────────────────────────────────────────────┘           │
└──────────────────────────────────────────────────────────────────────┘
                   │
    ┌──────────────┼──────────────┬──────────────┐
    ▼              ▼              ▼              ▼
┌─────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ stepper  │  │ gpiocmds │  │ endstop  │  │ sensors  │
│ .c       │  │ .c       │  │ .c       │  │ (ADXL,   │
│          │  │          │  │          │  │ thermo,  │
│ 步进电机  │  │ 数字输出  │  │ 限位开关  │  │ TMC UART)│
│ 加速控制  │  │ 软件PWM  │  │ 过采样   │  │ SPI/I2C  │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │              │
     ▼             ▼             ▼              ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     调度器层 (sched.c)                                │
│  ┌────────────────────────────────────────────────────────┐          │
│  │  定时器链表: periodic → stepper → digital_out → ...    │          │
│  │  按 waketime 排序，最早到期的在表头                       │          │
│  └────────────────────────┬───────────────────────────────┘          │
│                           │                                          │
│  ┌────────────────────────┼───────────────────────────────┐          │
│  │  任务循环:              │                               │          │
│  │  while(1) {            │                               │          │
│  │    if (idle) sleep;    │                               │          │
│  │    run all DECL_TASK;  │                               │          │
│  │    stats_update();     │                               │          │
│  │  }                     ▼                               │          │
│  └────────────────────────────────────────────────────────┘          │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    AVR 硬件抽象层 (src/avr/)                          │
│                                                                      │
│  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐            │
│  │timer.c │ │gpio.c  │ │adc.c   │ │spi.c   │ │i2c.c   │            │
│  │Timer1  │ │PIN/    │ │ADC     │ │SPCR    │ │TWI     │            │
│  │32bit   │ │DDR/    │ │ADCSRA  │ │SPDR    │ │TWBR    │            │
│  │扩展    │ │PORT    │ │ADMUX   │ │        │ │TWDR    │            │
│  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘            │
│      │          │          │          │          │                   │
│  ┌───┴────┐ ┌───┴────┐ ┌───┴────┐                                          
│  │hard_   │ │watchdog│ │irq.h   │                                          
│  │pwm.c   │ │.c      │ │cli/sei │                                          
│  │Timer0  │ │WDT     │ │save/   │                                          
│  │Timer2-5│ │0.5s    │ │restore │                                          
│  └────────┘ └────────┘ └────────┘                                          
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │              AVR 硬件 (ATmega 系列 MCU)                         │  │
│  │  SRAM (1-16KB)  |  Flash (16-256KB)  |  EEPROM  |  外设        │  │
│  └────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

### 启动序列

```
硬件复位
  │
  ▼
.watchdog_early_init (.init3)  ──→  清除 MCUSR, 禁用 WDT
  │
  ▼
main()
  ├── irq_enable()
  └── sched_main()
        │
        ├── ctr_run_initfuncs()   ──→  所有 DECL_INIT 按序执行:
        │     ├── prescaler_init()      时钟预分频
        │     ├── timer_init()          Timer1 初始化
        │     ├── watchdog_init()       看门狗启动
        │     ├── serial_init()         串口初始化
        │     ├── alloc_init()          内存分配器
        │     └── ...
        │
        ├── sendf("starting")     ──→  通知主机固件就绪
        │
        ├── setjmp(shutdown_jmp)  ──→  设置 shutdown 跳转点
        │
        └── run_tasks()           ──→  主循环
              ├── irq_wait()           空闲时低功耗等待
              ├── ctr_run_taskfuncs()  执行所有 DECL_TASK
              │     ├── watchdog_reset()
              │     ├── trsync_task()
              │     ├── tmcuart_task()
              │     └── ...
              └── stats_update()       统计上报
```

### 步进电机定时序列

```
时间轴 →
│
│ queue_step(interval=100, count=5, add=0)
│
├─ t0: toggle(step_pin) ↑     ← stepper_event_avr
│      count=4
│      waketime += 100
│      toggle(step_pin) ↓     ← 同一 ISR 内完成
│
├─ t0+100: toggle ↑
│           count=3
│           waketime += 100
│           toggle ↓
│
├─ t0+200: toggle ↑
│           count=2
│           ...
│
├─ t0+300: toggle ↑
│           count=1
│           ...
│
├─ t0+400: toggle ↑
│           count=0 → stepper_load_next()
│           toggle ↓
│
└─ 队列空 → SF_DONE, 定时器移除
```

---

## 6. 总结

### Klipper AVR 固件栈提供的完整功能

| 类别 | 功能 | 实现文件 |
|------|------|---------|
| **时序** | 32 位高精度时钟 (≥16MHz) | timer.c |
| **GPIO** | 数字输入/输出，上拉支持 | gpio.c |
| **ADC** | 10 位模数转换，多通道 | adc.c |
| **PWM** | 硬件 PWM (Timer0/2-5) + 软件 PWM | hard_pwm.c, gpiocmds.c |
| **通信** | UART (最多 4 路) + USB CDC | serial.c, usbserial.c |
| **总线** | SPI (主机) + I2C/TWI (主机) | spi.c, i2c.c |
| **运动** | 多轴步进电机，S 曲线加速 | stepper.c |
| **触发** | 同步触发系统 (trsync) | trsync.c |
| **限位** | 过采样限位检测 | endstop.c |
| **传感器** | 加速度计、热电偶、TMC UART | sensor_*.c, thermocouple.c, tmcuart.c |
| **安全** | 看门狗、紧急停机、shutdown 机制 | watchdog.c, sched.c |
| **协议** | 二进制消息协议，VLQ 编码，CRC16 | command.c |
| **调度** | 优先级定时器 + 任务循环 | sched.c |
| **内存** | 线性分配器 + move queue | basecmd.c |

### 设计哲学

1. **实时性优先**：定时器中断中直接执行步进电机脉冲生成，最小化延迟
2. **极简设计**：无动态内存分配（只增不减的 bump allocator），无虚函数表
3. **平台解耦**：通过 `board/` 头文件接口隔离平台差异
4. **编译时配置**：大量使用 `DECL_*` 宏在编译时生成命令表、常量表
5. **AVR 特化**：手写汇编优化关键路径（timer_is_before, stepper_event_avr），PROGMEM 数据表，硬件特性利用（PIN 寄存器翻转）
6. **安全机制**：看门狗 + shutdown + setjmp/longjmp 非本地跳转，确保任何异常都能安全停机
