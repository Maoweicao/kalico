# AVR 原生固件 vs Generic Arduino 固件 — 功能对比

## 一、架构对比总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Klipper Host (Python)                            │
└───────────────────────────────┬─────────────────────────────────────────┘
                                │ USB/Serial 二进制协议 (VLQ + CRC16)
                                ▼
┌─────────────────────────── 对比分界线 ───────────────────────────────────┐
│                                                                         │
│  ┌──── 原生 AVR (src/avr/) ────┐    ┌── generic_arduino ──┐            │
│  │                             │    │                     │            │
│  │ 通信层:                     │    │ 通信层:              │            │
│  │  serial.c (中断驱动UART)    │    │  serial.cpp (轮询)   │            │
│  │  usbserial.c (USB CDC)     │    │  (无 USB)            │            │
│  │  generic/serial_irq.c      │    │  generic/serial_irq.c│            │
│  ├─────────────────────────────┤    ├─────────────────────┤            │
│  │ 命令处理:                   │    │ 命令处理:            │            │
│  │  command.c (VLQ+CRC)       │    │  command.c (同)      │            │
│  │  basecmd.c (OID+内存+move) │    │  basecmd.c (修改版)  │            │
│  │  compile_time_request.c    │    │  compile_time_request.c│           │
│  │  (构建脚本自动生成)         │    │  (手工维护50个命令)  │            │
│  ├─────────────────────────────┤    ├─────────────────────┤            │
│  │ 功能模块:                   │    │ 功能模块:            │            │
│  │  ✅ stepper.c (3种优化路径) │    │  ❌ stepper.c (存根)  │            │
│  │  ✅ gpiocmds.c (输出+PWM)  │    │  ✅ gpiocmds.c (同)   │            │
│  │  ✅ endstop.c (过采样)     │    │  ❌ (未包含)          │            │
│  │  ✅ trsync.c (同步触发)    │    │  ❌ (未包含)          │            │
│  │  ✅ tmcuart.c (TMC UART)   │    │  ❌ (未包含)          │            │
│  │  ✅ thermocouple.c         │    │  ❌ (未包含)          │            │
│  │  ✅ sensor_adxl345.c       │    │  ❌ (未包含)          │            │
│  │  ✅ buttons.c              │    │  ✅ buttons.c (同)    │            │
│  │  ✅ debugcmds.c            │    │  ✅ debugcmds.c (同)  │            │
│  ├─────────────────────────────┤    ├─────────────────────┤            │
│  │ HAL 层:                     │    │ HAL 层:              │            │
│  │  avr/gpio.c  (寄存器直操)  │    │  arduino/gpio.c      │            │
│  │  avr/timer.c (Timer1 ISR)  │    │  arduino/timer.c     │            │
│  │  avr/adc.c   (ADCSRA)      │    │  (analogRead)        │            │
│  │  avr/spi.c   (SPCR)        │    │  ❌ 无               │            │
│  │  avr/i2c.c   (TWI)         │    │  ❌ 无               │            │
│  │  avr/hard_pwm.c (Timer0/2+)│    │  ❌ 无               │            │
│  │  avr/watchdog.c (WDT)      │    │  ❌ 无               │            │
│  ├─────────────────────────────┤    ├─────────────────────┤            │
│  │ 调度器:                     │    │ 调度器:              │            │
│  │  sched.c (原版)             │    │  sched.c (修改版)    │            │
│  │  ctr 自动生成               │    │  registrations.c 手动│            │
│  └─────────────────────────────┘    └─────────────────────┘            │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 二、模块级功能对比

### 2.1 调度器 (sched.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| 定时器链表管理 | ✅ 有序链表 | ✅ 同 | 相同 |
| 三特殊定时器 (periodic/sentinel/deleted) | ✅ | ✅ | 相同 |
| 任务循环 (run_tasks) | ✅ | ✅ | 相同 |
| setjmp/longjmp shutdown | ✅ | ✅ | 相同 |
| Shutdown 后等待主机 clear | ✅ | ❌ 自动恢复(50次) | **关键差异** |
| sendf("shutdown...") | ✅ 发送给主机 | ❌ 被注释掉 | **关键差异** |
| sched_report_shutdown() | ✅ 发送 is_shutdown | ❌ 空函数 | **关键差异** |
| "过去定时器" shutdown | ✅ try_shutdown | ❌ 注释掉 | **关键差异** |
| shutdown_count 计数 | ❌ | ✅ 限制50次 | 新增 |
| AVR 寄存器微优化 | ✅ inline asm | ✅ 同 | 相同 |

### 2.2 命令协议 (command.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| VLQ 编解码 | ✅ | ✅ | 相同 |
| CRC16-CCITT 校验 | ✅ (AVR硬件加速) | ✅ (软件实现) | 性能差异 |
| 消息帧 (LEN/SEQ/CRC/SYNC) | ✅ | ✅ | 相同 |
| 命令路由 dispatch | ✅ | ✅ | 相同 |
| 编码器查找 | 字符串地址比较 | 编译时哈希 switch-case | **实现差异** |
| HF_IN_SHUTDOWN 标志 | ✅ | ✅ | 相同 |
| command_parsef/encodef | ✅ | ✅ | 相同 |

### 2.3 基础命令 (basecmd.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| 内存分配 (alloc_chunk) | ✅ OOM→shutdown | ✅ OOM→return NULL | **AVR 保护** |
| Move Queue (1024节点) | ✅ | ✅ (32节点) | 容量差异 |
| OID 系统 | ✅ | ✅ | 相同 |
| get_config/finalize_config | ✅ | ✅ | 相同 |
| get_clock/get_uptime | ✅ | ✅ | 相同 |
| identify 数据 | ✅ 自动生成 | ✅ 手工维护(825B) | 来源不同 |
| stats 统计上报 | ✅ 5秒周期 | ✅ 同 | 相同 |
| config_finalized_flag | ❌ | ✅ 防重复配置 | 新增保护 |

### 2.4 GPIO 命令 (gpiocmds.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| config_digital_out | ✅ | ✅ | 相同 |
| set_digital_out (无OID) | ✅ | ✅ | 相同 |
| update_digital_out | ✅ | ✅ | 相同 |
| queue_digital_out (定时) | ✅ | ✅ | 相同 |
| set_digital_out_pwm_cycle | ✅ | ✅ | 相同 |
| 软件 PWM 状态机 | ✅ | ✅ | 相同 |
| digital_out_shutdown | ✅ 恢复默认值 | ✅ 同 | 相同 |

### 2.5 步进电机 (stepper.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| stepper_event | ✅ 3种优化路径 | ❌ shutdown存根 | **完全缺失** |
| config_stepper | ✅ | ❌ | 缺失 |
| queue_step | ✅ | ❌ | 缺失 |
| set_next_step_dir | ✅ | ❌ | 缺失 |
| reset_step_clock | ✅ | ❌ | 缺失 |
| stepper_get_position | ✅ | ❌ | 缺失 |
| stepper_stop_on_trigger | ✅ | ❌ | 缺失 |
| AVR 优化路径 (step+unstep同ISR) | ✅ | ❌ | 缺失 |
| 加速控制 (interval+add) | ✅ | ❌ | 缺失 |
| trsync 集成 | ✅ | ❌ | 缺失 |

### 2.6 限位开关 (endstop.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| config_endstop | ✅ | ❌ | 缺失 |
| endstop_home | ✅ | ❌ | 缺失 |
| 过采样检测 | ✅ | ❌ | 缺失 |
| trsync 触发 | ✅ | ❌ | 缺失 |

### 2.7 同步触发 (trsync.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| 信号回调链表 | ✅ | ❌ | 缺失 |
| 超时触发 | ✅ | ❌ | 缺失 |
| 报告机制 | ✅ | ❌ | 缺失 |

### 2.8 传感器与驱动

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| TMC UART (tmcuart.c) | ✅ 软件UART | ❌ | 缺失 |
| 热电偶 (thermocouple.c) | ✅ SPI读取 | ❌ | 缺失 |
| ADXL345 (sensor_adxl345.c) | ✅ SPI读取 | ❌ | 缺失 |

### 2.9 按键 (buttons.c) 和调试 (debugcmds.c)

| 功能点 | 原生 AVR | generic_arduino | 差异说明 |
|--------|---------|-----------------|---------|
| 按键检测+去抖 | ✅ | ✅ | 相同 |
| 重传机制 | ✅ | ✅ | 相同 |
| debug_ping/read/write/nop | ✅ | ✅ | 相同 |

---

## 三、HAL 层对比

### 3.1 GPIO

| 功能点 | 原生 AVR (avr/gpio.c) | generic_arduino (arduino/gpio.c) | 差异说明 |
|--------|----------------------|----------------------------------|---------|
| 实现方式 | 直接操作 PIN/DDR/PORT 寄存器 | Arduino digitalWrite/Read API | **核心差异** |
| 引脚编码 | `GPIO('B',3)` = port*8+bit | `ar0`~`ar69` + 兼容名 | 命名不同 |
| 输出翻转 | 写 PIN 寄存器 (硬件翻转) | read→invert→write (3条指令) | 性能差异 |
| 原子保护 | irq_save/restore | 无特殊保护 | 可靠性差异 |
| ADC | 直接操作 ADCSRA/ADMUX | analogRead() API | 封装层次不同 |
| 数据结构 | `struct gpio_out {regs*, bit}` | `struct gpio_out {pin, invert, is_static, pwm_ptr}` | 字段不同 |

### 3.2 定时器

| 功能点 | 原生 AVR (avr/timer.c) | generic_arduino (arduino/timer.c) | 差异说明 |
|--------|----------------------|----------------------------------|---------|
| 硬件定时器 | Timer1 CTC 模式 | Timer1 Normal + overflow | 模式不同 |
| 32位扩展 | overflow_count + TCNT1 | 同，但有 TOV1 竞态保护 | 实现细节不同 |
| ISR 模式 | COMPA 中断内直接调度回调 | COMPA 仅设标志，irq_poll 中处理 | **关键差异** |
| timer_kick | 设置 OCR1A = TCNT1 + 50 | 设置 OCR1A = next_time | 行为不同 |
| timer_is_before | 手写汇编优化 | C 代码 (int32_t 比较) | 性能差异 |
| Timer0 | 不使用 (留给 PWM) | **禁用** (TIMSK0=0) | 策略不同 |
| 调度位置 | ISR 内直接 sched_timer_dispatch | irq_poll/irq_wait 中调用 | **关键差异** |

### 3.3 串口

| 功能点 | 原生 AVR (avr/serial.c) | generic_arduino (arduino/serial.cpp) | 差异说明 |
|--------|------------------------|--------------------------------------|---------|
| 通信模式 | **中断驱动** (RX/TX ISR) | **轮询** (irq_wait 中 drain_rx) | **核心差异** |
| TX 方式 | UDRE 中断逐字节发送 | KALICO_SERIAL.write() 同步刷新 | 性能/实时性差异 |
| 接收缓冲 | generic/serial_irq.c 192B | 同 + Arduino 内部缓冲 | 多一层缓冲 |
| USB CDC | ✅ usbserial.c | ❌ 不支持 | 功能缺失 |
| 波特率 | UBRR 寄存器直算 | Arduino begin() API | 封装不同 |
| 多串口 | 最多4路 (2560) | Serial/Serial1/Serial2/Serial3 | 框架抽象 |

### 3.4 中断管理

| 功能点 | 原生 AVR (avr/irq.h) | generic_arduino (arduino/irq.c) | 差异说明 |
|--------|---------------------|--------------------------------|---------|
| 关中断 | cli() | noInterrupts() | 等价 |
| 开中断 | sei() | interrupts() | 等价 |
| 保存/恢复 | SREG 读写 | SREG/PRIMASK | 等价 |
| irq_wait | sei→nop→cli (单周期窗口) | interrupts→delay(10µs)→noInterrupts + 轮询 | **关键差异** |
| irq_poll | 空操作 | 轮询串口+定时器 | **关键差异** |

---

## 四、关键差异深度分析

### 4.1 Shutdown 机制 — 最大的分歧

```
原生 AVR 流程:
  异常发生 → shutdown("reason")
    → longjmp → run_shutdown()
      → 禁中断 → 重置定时器 → 执行所有 DECL_SHUTDOWN
      → sendf("shutdown clock=%u reason=%s")  ← 通知主机
      → 进入死循环，等待主机发送 clear_shutdown

generic_arduino 流程:
  异常发生 → shutdown("reason")
    → longjmp → run_shutdown()
      → 禁中断 → 重置定时器 → 执行所有 shutdown 函数
      → (sendf 被注释掉)  ← 不通知主机
      → shutdown_count++
      → if (count <= 50) sched_clear_shutdown()  ← 自动恢复
      → 继续 run_tasks() 主循环
```

**影响**：generic_arduino 在遇到间歇性错误时会自动恢复，但也意味着主机可能不知道 MCU 曾经出错。

### 4.2 定时器调度 — ISR 内 vs 轮询

```
原生 AVR:
  Timer1 COMPA 中断
    └→ 直接调用 sched_timer_dispatch()
       └→ 执行 stepper_event() 等回调
       └→ 返回下一个唤醒时间
       └→ 设置 OCR1A = next
  延迟: 从中断到回调执行 ≈ 44 周期 (2.75µs @16MHz)

generic_arduino:
  Timer1 COMPA 中断
    └→ 仅设置 timer_irq_pending_flag = true
    └→ 返回

  irq_poll() / irq_wait()  [主循环中]
    └→ 检查 timer_irq_pending_flag
    └→ 调用 timer_dispatch_many()
       └→ sched_timer_dispatch()
       └→ 执行回调
    └→ timer_kick_next(next)
  延迟: 从标志设置到回调执行 = 不确定（取决于主循环周期）
```

**影响**：原生 AVR 的定时器精度更高，适合步进电机等实时性要求高的场景。generic_arduino 的轮询模式适合 GPIO 输出等非实时场景。

### 4.3 注册机制 — 自动生成 vs 手工维护

```
原生 AVR:
  源码中写 DECL_INIT(func) / DECL_TASK(func) / DECL_COMMAND(func, "fmt")
    → 编译时 Python 脚本扫描 .compile_time_request 段
    → 自动生成 compile_time_request.c (命令表、编码器表、init/task/shutdown 列表)
    → 运行时 ctr_run_initfuncs() / ctr_run_taskfuncs() 遍历执行

generic_arduino:
  DECL_INIT/TASK/SHUTDOWN 宏变为空操作
  手工在 registrations.c 中维护:
    ctr_init_list[] = { alloc_init, serial_init, timer_init, ... }
    ctr_task_list[] = { console_task, timer_task, buttons_task, ... }
    ctr_shutdown_list[] = { sendf_shutdown, digital_out_shutdown }
  手工在 compile_time_request.c 中维护命令表和编码器表
```

**影响**：generic_arduino 不依赖构建脚本，可以用 PlatformIO 直接编译，但添加新功能需要手动更新注册表。

### 4.4 内存管理

```
原生 AVR:
  alloc_chunk(size) → 检查 alloc_end + size <= dynmem_end()
    → 超出: shutdown("alloc_chunk failed")
    → 成功: alloc_end += size, 返回指针

generic_arduino (AVR 平台):
  alloc_chunk(size) → 同样的检查
    → 超出: return NULL  ← 不 shutdown
    → 成功: 同上
```

**影响**：generic_arduino 在 2KB RAM 的 ATmega328P 上不会因为内存不足而死循环，但调用者需要检查 NULL。

---

## 五、功能覆盖度总结

```
功能覆盖度 = generic_arduino 已实现 / 原生 AVR 总功能

通信协议层:    ████████████████████ 100%  (VLQ, CRC, 帧格式完全相同)
基础命令层:    ████████████████████ 100%  (identify, config, clock, stats)
GPIO 输出:     ████████████████████ 100%  (含软件 PWM)
GPIO 输入:     ████████████████████ 100%  (含去抖)
ADC:           ████████████████████ 100%  (通过 Arduino API)
按键检测:      ████████████████████ 100%  (buttons.c 完全相同)
调试命令:      ████████████████████ 100%  (debugcmds.c 完全相同)
定时器调度:    ██████████████░░░░░░  70%  (功能相同，实时性差)
步进电机:      ░░░░░░░░░░░░░░░░░░░░   0%  (仅存根)
限位开关:      ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
同步触发:      ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
SPI:           ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
I2C:           ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
硬件 PWM:      ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
看门狗:        ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
USB CDC:       ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
TMC UART:      ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
温度传感器:    ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
加速度传感器:  ░░░░░░░░░░░░░░░░░░░░   0%  (未包含)
```

**总体覆盖度: 约 35%**（核心通信+GPIO 完整，运动控制和传感器完全缺失）

---

## 六、能否达到相同功能？可行性分析

### 6.1 已经对齐的部分 ✅

| 模块 | 状态 | 说明 |
|------|------|------|
| 二进制协议 | ✅ 完全对齐 | 相同的 VLQ + CRC16 帧格式 |
| GPIO 输出 | ✅ 完全对齐 | 相同的 gpiocmds.c，底层 API 不同但功能等价 |
| GPIO 输入/按键 | ✅ 完全对齐 | 相同的 buttons.c |
| 调试命令 | ✅ 完全对齐 | 相同的 debugcmds.c |
| 调度器核心 | ✅ 基本对齐 | 定时器链表、任务循环相同，shutdown 策略不同 |
| 内存管理 | ✅ 基本对齐 | bump allocator 相同，OOM 处理不同 |

### 6.2 可以实现但有差距的部分 ⚠️

| 模块 | 差距 | 实现难度 | 说明 |
|------|------|---------|------|
| 定时器实时性 | ISR 内调度 vs 轮询 | 中 | 可以改为 ISR 内直接调度，但需要小心 Arduino 框架兼容性 |
| 硬件 PWM | 缺失 | 低 | 可以用 Arduino analogWrite() 替代，但分辨率只有 8 位 |
| ADC | 已实现但封装不同 | 无 | analogRead() 功能等价 |
| 看门狗 | 缺失 | 低 | 可以用 Arduino watchdog 库或直接操作 WDT 寄存器 |

### 6.3 难以在 Arduino 框架上实现的部分 ❌

| 模块 | 困难 | 原因 |
|------|------|------|
| **步进电机** | 高 | 需要 ISR 内精确到 cycle 级别的脉冲生成，Arduino 框架的中断开销和定时器抽象会引入不确定性 |
| **限位开关** | 高 | 依赖 trsync 同步触发，而 trsync 依赖 stepper 的精确时序 |
| **TMC UART** | 中 | 软件 UART 需要精确的位时序，轮询模式下延迟不可控 |
| **SPI 传感器** | 中 | 可以用 Arduino SPI 库，但需要适配 Klipper 的 sensor_bulk 批量传输机制 |
| **USB CDC** | 低 | ATmega32u4 的 Arduino 框架自带 USB CDC，但需要适配 Klipper 的端点管理 |

### 6.4 generic_arduino 的定位

generic_arduino **不是**一个完整的 3D 打印机固件，而是一个 **GPIO/按键控制器**：

```
原生 AVR 固件:  3D 打印机完整控制
  ├── 运动控制 (步进电机 × N 轴)
  ├── 温度管理 (热电偶 + 加热器 + PID)
  ├── 归位 (限位开关 + trsync)
  ├── 传感器 (ADXL345 加速度计)
  ├── 驱动通信 (TMC UART)
  └── GPIO 辅助 (LED/风扇/蜂鸣器)

generic_arduino:  GPIO 扩展板
  ├── GPIO 输出 (LED/继电器/蜂鸣器)
  ├── GPIO 输入 (按键/开关)
  ├── ADC 读取 (电位器/模拟传感器)
  └── 调试接口 (ping/read/write)
```

**典型用途**：将 Arduino Uno/Mega 作为 Klipper 的 GPIO 扩展板，控制 Multi Function Shield 上的 LED、数码管、蜂鸣器，读取按键。不参与运动控制。

---

## 七、改动清单（generic_arduino 相对于原版的修改）

### 7.1 文件级修改

| 文件 | 修改类型 | 修改内容 |
|------|---------|---------|
| sched.c | **重写** | 添加 shutdown 自动恢复、注释 sendf/shutdown 消息、添加 shutdown_count |
| command.c | **小改** | 注释掉 "timer in the past" shutdown、修改编码器查找为哈希方式 |
| basecmd.c | **小改** | alloc_chunk/alloc_chunks 返回 NULL 而非 shutdown、添加 config_finalized_flag |
| compile_time_request.c | **重写** | 手工维护的完整命令/响应注册表 |
| stepper.c | **重写** | 仅保留 shutdown 存根 |
| registrations.c | **新增** | 手动维护 init/task/shutdown 函数列表 |
| ctr_run.c/ctr_run.h | **新增** | 遍历注册表执行函数 |
| main.cpp | **新增** | Arduino setup() 入口，禁用 Timer0 |
| arduino/gpio.c | **新增** | Arduino API GPIO 实现 |
| arduino/timer.c | **新增** | Timer1 16-bit + overflow 32-bit 扩展 |
| arduino/serial.cpp | **新增** | Arduino HardwareSerial 轮询实现 |
| arduino/irq.c | **新增** | irq_wait/irq_poll 中轮询串口和定时器 |
| autoconf.h | **新增** | 静态配置替代 Kconfig |
| platformio.ini | **新增** | PlatformIO 构建配置 |

### 7.2 代码标记

在 generic_arduino 代码中搜索以下标记可以找到所有修改点：

- `shutdown_count` — 自动恢复计数器
- `HF_IN_SHUTDOWN` — shutdown 状态下可执行的命令
- `config_finalized_flag` — 防重复配置标志
- `suppress_shutdown` / 注释掉的 `sendf` — 被抑制的 shutdown 通知
- `arduino_serial_drain_rx` — 轮询式串口接收
- `arduino_timer_irq_pending` — 轮询式定时器调度

---

## 八、结论

generic_arduino 成功地将 Klipper MCU 固件的核心通信和 GPIO 功能移植到了 Arduino 框架上，但**有意放弃了运动控制相关的实时功能**。这不是一个"简化版 Klipper"，而是一个**专门的 GPIO 扩展固件**，用于在 Klipper 体系下控制 LED、蜂鸣器、按键等非实时外设。

如果要在此基础上实现步进电机控制，最大的挑战是定时器调度的实时性——需要将 `irq_poll` 中的轮询改为 ISR 内直接调度，这与 Arduino 框架的抽象层存在一定冲突。
