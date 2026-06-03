# Generic Arduino 固件技术分析文档

## 一、项目概述

`generic_arduino` 是 **Klipper/Kalico 3D打印机固件** 的 Arduino 移植版本。它将原本运行在专用 MCU（STM32、AVR 直接寄存器操作）上的 Klipper MCU 固件移植到 **Arduino 框架**上，使其能在 Arduino Uno、Mega、Due、Teensy、ESP32 等开发板上运行。

### 核心目标
- 通过 Arduino 框架抽象层，实现 Klipper MCU 固件的跨平台运行
- 提供 GPIO 输出、按键输入、调试通信等基础功能
- 作为 Klipper 主机（host）的协处理器，通过串口接收命令并执行硬件操作

---

## 二、整体架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                    Klipper Host (Python, Raspberry Pi)          │
│   klippy/extras/output_pin.py, gcode_button.py, etc.          │
└───────────────────────────────┬─────────────────────────────────┘
                                │ USB Serial (115200/250000 baud)
                                │ Klipper 二进制协议 (VLQ + CRC16)
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Arduino MCU (ATmega328P/2560/ARM/ESP32)       │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ main.cpp (入口)                                          │   │
│  │   setup() → 禁用 Timer0 → sched_main()                  │   │
│  │   loop()  → 永不执行 (sched_main 内含无限循环)           │   │
│  └────────────────────────┬─────────────────────────────────┘   │
│                           ▼                                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ sched.c (调度器核心)                                     │   │
│  │   sched_main()    → 初始化 → setjmp → run_tasks()        │   │
│  │   run_tasks()     → 协作式任务循环 (irq_poll+task执行)    │   │
│  │   timer管理       → 有序链表 (periodic/sentinel/deleted)  │   │
│  │   shutdown处理    → setjmp/longjmp 异常恢复               │   │
│  └─────┬──────────────┬──────────────┬──────────────────────┘   │
│        ▼              ▼              ▼                          │
│  ┌──────────┐  ┌────────────┐  ┌────────────────┐              │
│  │ Timer ISR│  │ Serial ISR │  │ Command Parser │              │
│  │ Timer1   │  │ UART/USB   │  │ VLQ编码/解码    │              │
│  │ 16-bit   │  │ polled     │  │ CRC16校验       │              │
│  └────┬─────┘  └─────┬──────┘  └───────┬────────┘              │
│       ▼              ▼                 ▼                        │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 命令处理层                                                │   │
│  │  basecmd.c     identify/config/clock/uptime/stats        │   │
│  │  gpiocmds.c    数字输出 (set/update/queue + 软件PWM)      │   │
│  │  buttons.c     按键检测 (去抖 + 重传)                     │   │
│  │  debugcmds.c   调试 (ping/read/write/nop)                │   │
│  └──────────────────────────────────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼─────────────────────────────────┐   │
│  │ 硬件抽象层 (HAL)                                         │   │
│  │  arduino/gpio.c    digitalWrite/Read/analogRead          │   │
│  │  arduino/timer.c   Timer1 16-bit + overflow → 32-bit    │   │
│  │  arduino/serial.cpp Arduino HardwareSerial 轮询          │   │
│  │  arduino/irq.c     noInterrupts/interrupts + 轮询调度    │   │
│  │  arduino/pgm.h     AVR PROGMEM 读写抽象                  │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 通用层 (generic/)                                        │   │
│  │  serial_irq.c    收发缓冲区 (192B RX + 192B TX)          │   │
│  │  timer_irq.c     timer_from_us/timer_is_before/dispatch  │   │
│  │  crc16_ccitt.c   CRC-CCITT 校验                          │   │
│  │  alloc.c         非AVR平台的20KB内存池                   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ 注册与配置层                                             │   │
│  │  registrations.c   手动维护 init/task/shutdown 列表       │   │
│  │  ctr_run.c         遍历列表执行注册函数                   │   │
│  │  compile_time_request.c  命令索引 + 响应编码器注册表      │   │
│  │  autoconf.h        静态配置 (时钟/串口/功能开关)          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、模块详细分析

### 3.1 入口点 (main.cpp)

**功能**: Arduino 程序入口，将 `setup()/loop()` 映射到 Kalico 调度器。

**关键函数**:
| 函数 | 说明 |
|------|------|
| `setup()` | 禁用 Arduino Timer0 ISR（TIMSK0=0），调用 `sched_main()` |
| `loop()` | 永不执行（`sched_main` 内含无限循环），仅作为安全兜底 |

**与原版差异**:
- 原版 Klipper 直接操作 AVR 寄存器启动，此处使用 Arduino `setup()` 入口
- **禁用 Timer0**: Arduino 的 `init()` 会启用 Timer0 溢出中断用于 `millis()/micros()`，但 Klipper 有自己的定时器系统，禁用可节省约 50 字节栈空间
- `sched_main()` 永不返回，Arduino 的 `loop()` 永远不会被调用

---

### 3.2 调度器 (sched.c / sched.h)

**功能**: 核心协作式调度器，管理定时器链表、任务循环和关机处理。

**关键数据结构**:
```c
struct timer {
    struct timer *next;           // 链表指针
    uint_fast8_t (*func)(struct timer*); // 回调函数
    uint32_t waketime;            // 唤醒时间（时钟tick）
};

struct task_wake {
    uint8_t wake;                 // 任务唤醒标志
};

static struct {
    struct timer *timer_list, *last_insert;  // 定时器链表
    int8_t tasks_status, tasks_busy;         // 任务状态
    uint8_t shutdown_status, shutdown_reason; // 关机状态
} SchedStatus;
```

**关键函数**:
| 函数 | 说明 |
|------|------|
| `sched_main()` | 主入口：初始化 → 发送 "starting" → setjmp → run_tasks() |
| `run_tasks()` | 无限循环：irq_poll → 检查休眠 → 执行所有 task → 更新统计 |
| `sched_add_timer()` | 将定时器插入有序链表（按 waketime 排序） |
| `sched_del_timer()` | 从链表删除定时器（使用 deleted_timer 替代技巧） |
| `sched_timer_dispatch()` | 调度下一个定时器回调，支持 inline stepper hack |
| `sched_timer_reset()` | 清除所有用户定时器（shutdown 时调用） |
| `sched_wake_tasks()` | 标记有任务需要执行 |
| `sched_wake_task()` | 标记特定任务需要执行 |
| `sched_check_wake()` | 检查并清除任务唤醒标志 |
| `run_shutdown()` | 执行所有注册的 shutdown 函数 |
| `sched_clear_shutdown()` | 退出关机状态 |
| `sched_shutdown()` | `longjmp` 强制跳转到 shutdown 处理 |

**三个特殊定时器**:
1. **periodic_timer**: 每 100ms 唤醒一次，确保 stats 任务定期运行
2. **sentinel_timer**: 链表末尾哨兵，始终在 periodic_timer + 0x80000000
3. **deleted_timer**: 删除活跃定时器时的占位符

**⚠️ 关键修改 — Shutdown 自动恢复**:
```c
// sched_main() 中的修改
static uint8_t shutdown_count;
int ret = setjmp(shutdown_jmp);
if (ret) {
    run_shutdown(ret);
    shutdown_count++;
}
// 自动清除 shutdown（最多50次）
if (shutdown_count <= 50) {
    sched_clear_shutdown();
}
```
- **原版 Klipper**: shutdown 后发送 `shutdown` 消息给主机，等待主机发送 `clear_shutdown`
- **本项目**: 自动清除 shutdown，最多重试 50 次，防止因 AVR 资源限制导致的间歇性 shutdown 死循环
- `run_shutdown()` 中的 `sendf("shutdown ...")` 被注释掉
- `sched_report_shutdown()` 为空函数

**AVR 微优化**:
```c
#ifdef CONFIG_MACH_AVR
    // 减少寄存器压力的内联汇编
    asm("" : "+r"(prev));
#endif
```

---

### 3.3 命令协议 (command.c / command.h)

**功能**: Klipper 二进制通信协议的编解码和路由。

**协议格式**:
```
[LEN] [SEQ] [payload...] [CRC_HI] [CRC_LO] [SYNC=0x7E]
```
- 最小帧长: 5 字节，最大: 64 字节
- 序列号: 4-bit (0x0F 掩码)，目标标识: bit4 (0x10)
- 同步字节: 0x7E
- CRC: CRC16-CCITT

**VLQ 编码** (Variable Length Quantity):
- 整数使用变长编码，节省带宽
- 有符号数使用补码表示
- msgid 使用优化的 2 字节编码器

**关键函数**:
| 函数 | 说明 |
|------|------|
| `command_parsef()` | 解析二进制命令到 args 数组 |
| `command_encodef()` | 将 va_list 编码为二进制消息 |
| `command_find_block()` | 在接收缓冲区中查找完整消息帧 |
| `command_dispatch()` | 遍历消息中的所有命令并分发到处理函数 |
| `command_sendf()` | 编码并发送响应消息（带重入保护） |
| `command_send_ack()` | 发送 ACK 消息 |
| `command_find_and_dispatch()` | 组合：查找 + 分发 + ACK |

**命令/响应类型** (PT_*):
```c
enum { PT_uint32, PT_int32, PT_uint16, PT_int16, PT_byte,
       PT_string, PT_progmem_buffer, PT_buffer };
```

**编译时哈希查找** (替代原版字符串查找):
```c
#define _ENCODER_HASH(FMT) ((uint16_t)( \
    sizeof(FMT) * 31 + ((const char *)(FMT))[0] + ((const char *)(FMT))[sizeof(FMT)-2] ))

#define _DECL_ENCODER(FMT) ({ \
    DECL_CTR("_DECL_ENCODER " FMT); \
    ctr_lookup_encoder(_ENCODER_HASH(FMT)); })
```
- 原版使用字符串地址比较查找编码器
- 本项目使用编译时哈希（`sizeof*31 + 首字符 + 末字符`），通过 switch-case 分发
- 避免 AVR 链接器的字符串地址解析问题

**HF_IN_SHUTDOWN 标志**:
- 值为 0x01，标记命令可在 shutdown 状态下执行
- 用于 identify、get_config、get_clock、emergency_stop、clear_shutdown 等关键命令

---

### 3.4 命令注册表 (compile_time_request.c)

**功能**: 手工维护的完整命令/响应注册表，替代原版构建脚本自动生成。

**命令索引** (`command_index[]`):
50 个条目的 PROGMEM 数组，通过 encoded_msgid 索引：

| ID | 命令 | 处理函数 | Flags |
|----|------|---------|-------|
| 1 | `identify offset=%u count=%c` | command_identify | HF_IN_SHUTDOWN |
| 2 | `clear_shutdown` | command_clear_shutdown | HF_IN_SHUTDOWN |
| 3 | `emergency_stop` | command_emergency_stop | HF_IN_SHUTDOWN |
| 4 | `get_uptime` | command_get_uptime | HF_IN_SHUTDOWN |
| 5 | `get_clock` | command_get_clock | HF_IN_SHUTDOWN |
| 6 | `finalize_config crc=%u` | command_finalize_config | HF_IN_SHUTDOWN |
| 7 | `get_config` | command_get_config | HF_IN_SHUTDOWN |
| 8 | `allocate_oids count=%c` | command_allocate_oids | HF_IN_SHUTDOWN |
| 9-12 | debug_* | debugcmds.c 函数 | HF_IN_SHUTDOWN |
| 13-17 | digital_out_* | gpiocmds.c 函数 | 0 |
| 46-49 | buttons_* | buttons.c 函数 | 0 |

**响应编码器** (11个):
| ID | 格式串 | 最大大小 |
|----|--------|---------|
| 235 | `starting` | 7 |
| 236 | `is_shutdown static_string_id=%hu` | 16 |
| 237 | `shutdown clock=%u static_string_id=%hu` | 32 |
| 238 | `stats count=%u sum=%u sumsq=%u` | 32 |
| 239 | `uptime high=%u clock=%u` | 24 |
| 240 | `clock clock=%u` | 16 |
| 241 | `config is_config=%c crc=%u is_shutdown=%c move_count=%hu` | 32 |
| 242 | `pong data=%*s` | 64 |
| 243 | `debug_result val=%u` | 16 |
| 250 | `buttons_state oid=%c ack_count=%c state=%*s` | 64 |

**Identify 数据**: 825 字节的 zlib 压缩 JSON，存储在 PROGMEM 中，描述 MCU 能力。

**哈希查找函数**:
```c
const struct command_encoder *ctr_lookup_encoder(uint16_t hash) {
    switch (hash) {
    case  497: return &enc_starting;      // "starting"
    case 1398: return &enc_identify_response;
    case 1245: return &enc_is_shutdown;
    // ... 共11个case
    default:   return &enc_starting;
    }
}
```

---

### 3.5 基础命令 (basecmd.c)

**功能**: 核心基础设施命令，包括内存分配、OID 管理、配置 CRC、统计等。

#### 内存分配器
```c
static void *alloc_end;  // 分配指针

void alloc_init(void);      // 初始化：alloc_end = ALIGN(dynmem_start)
void *alloc_chunk(size_t);  // 线性分配（bump allocator）
void *alloc_chunks(size_t, size_t, uint16_t*); // 分配数组
```

**⚠️ AVR 修改**: `alloc_chunk()` 在内存耗尽时返回 NULL 而非 shutdown，因为 AVR 的 2KB RAM 极其有限。

#### Move Queue（移动队列）
```c
struct move_node { struct move_node *next; };
struct move_queue_head { struct move_node *first, *last; };
```
- FIFO 队列，用于 GPIO 输出的定时事件调度
- `move_queue_setup()`: 初始化队列并记录节点大小
- `move_finalize()`: 分配 32 个 move 节点的内存池
- `config_finalized_flag`: 防止重复配置

#### OID 系统
```c
struct oid_s { void *type, *data; };
```
- 通用对象 ID 系统，每个 GPIO/按键等组件分配一个 OID
- `oid_alloc()`: 分配并绑定类型
- `oid_lookup()`: 查找并验证类型
- `oid_next()`: 遍历特定类型的所有 OID
- `foreach_oid()`: 宏，遍历所有指定类型的 OID

**⚠️ AVR 修改**: `oid_alloc()` 在内存耗尽时撤销类型赋值并 shutdown，而非直接崩溃。

#### 命令列表
| 命令 | 格式 | 说明 |
|------|------|------|
| `get_config` | 无参 | 返回配置状态、CRC、shutdown 状态 |
| `finalize_config` | `crc=%u` | 完成配置，分配 move 队列 |
| `get_clock` | 无参 | 返回当前时钟 |
| `get_uptime` | 无参 | 返回运行时间 |
| `allocate_oids` | `count=%c` | 分配 OID 数组 |
| `identify` | `offset=%u count=%c` | 返回 identify 数据 |
| `emergency_stop` | 无参 | 触发紧急停止 |
| `clear_shutdown` | 无参 | 清除 shutdown 状态 |

#### 统计更新
```c
void stats_update(uint32_t start, uint32_t cur);
```
- 每 5 秒发送一次 `stats` 消息
- 计算任务循环的 count、sum、sumsq（用于负载监控）

---

### 3.6 GPIO 命令 (gpiocmds.c)

**功能**: 数字输出引脚控制，支持直接输出和软件 PWM。

**关键数据结构**:
```c
struct digital_out_s {
    struct timer timer;                    // 软件PWM定时器
    uint32_t on_duration, off_duration, end_time;
    struct gpio_out pin;                   // GPIO引脚
    uint32_t max_duration, cycle_time;     // PWM参数
    struct move_queue_head mq;             // 事件队列
    uint8_t flags;                         // DF_ON|DF_TOGGLING|DF_CHECK_END|DF_DEFAULT_ON
};

struct digital_move {
    struct move_node node;
    uint32_t waketime, on_duration;
};
```

**命令列表**:
| 命令 | 格式 | 说明 |
|------|------|------|
| `config_digital_out` | `oid=%c pin=%u value=%c default_value=%c max_duration=%u` | 配置数字输出 |
| `set_digital_out_pwm_cycle` | `oid=%c cycle_ticks=%u` | 设置 PWM 周期 |
| `queue_digital_out` | `oid=%c clock=%u on_ticks=%u` | 排队定时输出事件 |
| `update_digital_out` | `oid=%c value=%c` | 立即更新输出值 |
| `set_digital_out` | `pin=%u value=%c` | 直接设置引脚（无需 OID） |

**软件 PWM 状态机**:
```
digital_toggle_event() ←→ digital_load_event()
     ↑                         ↑
     │ (toggle on/off)         │ (load next from queue)
     └─────────────────────────┘
```
- `digital_toggle_event()`: 在 on/off 之间切换引脚
- `digital_load_event()`: 从 move 队列加载下一个 PWM 参数
- 支持 max_duration 安全超时

**Shutdown 处理**:
```c
void digital_out_shutdown(void) {
    foreach_oid(i, d, command_config_digital_out) {
        gpio_out_write(d->pin, d->flags & DF_DEFAULT_ON);  // 恢复默认值
        move_queue_clear(&d->mq);
    }
}
```

---

### 3.7 按键检测 (buttons.c)

**功能**: GPIO 输入引脚的去抖检测和状态上报。

**关键数据结构**:
```c
struct buttons {
    struct timer time;           // 定时采样定时器
    uint32_t rest_ticks;         // 采样间隔
    uint8_t pressed, last_pressed; // 当前/上次状态
    uint8_t report_count, reports[8]; // 报告队列
    uint8_t ack_count, retransmit_state, retransmit_count;
    uint8_t button_count;
    struct gpio_in pins[0];      // 柔性数组，最多8个引脚
};
```

**去抖算法**:
1. 每个采样周期读取所有引脚状态
2. 与 `pressed`（已确认状态）和 `last_pressed`（上次读取）比较
3. 如果某个引脚连续两次读取结果一致（`debounced`），则确认状态变化
4. 状态变化加入报告队列，唤醒 `buttons_task`

**重传机制**:
- 报告发送后设置 `retransmit_state = retransmit_count`
- 每次定时器递减，超时后重新发送
- 主机 ACK 后清除

**命令列表**:
| 命令 | 格式 | 说明 |
|------|------|------|
| `config_buttons` | `oid=%c button_count=%c` | 配置按键组（最多8个） |
| `buttons_add` | `oid=%c pos=%c pin=%u pull_up=%c` | 添加按键引脚 |
| `buttons_query` | `oid=%c clock=%u rest_ticks=%u retransmit_count=%c invert=%c` | 启动查询 |
| `buttons_ack` | `oid=%c count=%c` | 确认收到报告 |

---

### 3.8 调试命令 (debugcmds.c)

**功能**: 底层内存读写和连通性测试。

| 命令 | 格式 | 说明 |
|------|------|------|
| `debug_read` | `order=%c addr=%u` | 读取内存 (byte/word/dword) |
| `debug_write` | `order=%c addr=%u val=%u` | 写入内存 |
| `debug_ping` | `data=%*s` | 返回 pong 响应 |
| `debug_nop` | 无参 | 空操作 |

所有调试命令都标记为 `HF_IN_SHUTDOWN`，可在 shutdown 状态下执行。

---

### 3.9 Stepper 子系统 (stepper.c / stepper.h)

**功能**: 步进电机控制的存根实现。

```c
unsigned int stepper_event(struct timer *t) {
    shutdown("stepper_event called without stepper support");
    return SF_DONE;
}
```

**说明**:
- `CONFIG_WANT_STEPPER=0`，步进电机未启用
- 提供 `stepper_event()` 存根，满足 `sched_timer_dispatch()` 中的 `CONFIG_INLINE_STEPPER_HACK` 代码路径
- 此 generic_arduino 固件定位为 **GPIO/按键控制器**，非完整运动控制器

---

### 3.10 硬件抽象层 — GPIO (arduino/gpio.c)

**功能**: 使用 Arduino API 实现 GPIO 操作。

**引脚枚举**:
```c
DECL_ENUMERATION_RANGE("pin", "ar0", 0, 70);  // Arduino 引脚名
DECL_ENUMERATION_RANGE("pin", "PD0", 0, 70);  // 兼容名
```

**GPIO 结构体**:
```c
struct gpio_out { uint8_t pin, invert, is_static; void* pwm_ptr; };
struct gpio_in  { uint8_t pin, invert; };
struct gpio_adc { uint8_t pin; };
struct gpio_pwm { uint8_t pin, channel; void* hw; };
```

**实现函数**:
| 函数 | Arduino API | 说明 |
|------|------------|------|
| `gpio_out_setup()` | `pinMode(OUTPUT)` | 配置输出引脚 |
| `gpio_out_write()` | `digitalWrite(pin, val^invert)` | 写入输出 |
| `gpio_out_toggle_noirq()` | `digitalWrite(pin, !digitalRead(pin))` | 翻转输出 |
| `gpio_in_setup()` | `pinMode(INPUT/_PULLUP)` | 配置输入引脚 |
| `gpio_in_read()` | `digitalRead(pin) ^ invert` | 读取输入 |
| `gpio_adc_sample()` | `analogRead(pin+A0)` | ADC 采样 |
| `gpio_pwm_setup()` | `pinMode(OUTPUT)` + `analogWrite()` | PWM 输出 |
| `gpio_pwm_write()` | `analogWrite(pin, val)` | 写入 PWM |

**动态内存区域**:
```c
// AVR: 使用链接器符号 _end 和 SP
void *dynmem_start(void) { extern char _end; return &_end; }
void *dynmem_end(void) { return (void*)ALIGN(AVR_STACK_POINTER_REG, 256) - CONFIG_AVR_STACK_SIZE; }

// 非AVR: 使用 20KB 静态池 (generic/alloc.c)
```

---

### 3.11 硬件抽象层 — Timer (arduino/timer.c)

**功能**: 平台相关的定时器实现，支持 AVR/ARM/ESP32。

#### AVR 实现 (Timer1 16-bit)
```c
// Timer1 配置：Normal mode, 预分频=1 (16MHz)
TCCR1A = 0;
TCCR1B = (1 << CS10);  // 无预分频
TIMSK1 = (1 << TOIE1) | (1 << OCIE1A);  // 溢出 + 比较匹配中断

// 32位时间扩展
static volatile uint32_t timer_overflow_count = 0;

ISR(TIMER1_OVF_vect) { timer_overflow_count++; }
ISR(TIMER1_COMPA_vect) { timer_irq_pending_flag = true; }

uint32_t timer_read_time(void) {
    // 原子读取 TCNT1 + overflow_count，处理溢出竞态
    uint16_t cnt = TCNT1;
    uint32_t ovf = timer_overflow_count;
    if ((TIFR1 & (1 << TOV1)) && cnt < 32768) ovf++;
    return (ovf << 16) | cnt;
}
```

**⚠️ 关键设计决策 — timer_kick_next()**:
```c
void timer_kick_next(uint32_t next_time) {
    OCR1A = (uint16_t)(next_time & 0xFFFF);
    TIFR1 = 1 << OCF1A;  // 清除 pending 标志
}
```
- **不添加"太接近"保护**: 在 16 位定时器上，32 位时间的低 16 位可能看起来在"过去"（回绕），但 AVR 硬件正确处理这种情况
- 添加保护反而会导致 OCR1A 被设为 now+50，造成 COMPA 每 3µs 触发 → 定时器饱和

#### ARM 实现
```c
uint32_t timer_read_time(void) {
    uint32_t ms = millis();
    uint32_t us_part = micros() % 1000;
    return timer_from_us(ms * 1000UL + us_part);
}
```
- 使用 Arduino 的 `millis()/micros()` 组合
- `timer_kick()` 仅设置标志，`timer_kick_next()` 为空操作
- 定时器调度在 `irq_poll()` 中同步完成

#### ESP32 实现
```c
uint32_t timer_read_time(void) {
    return micros() * (CONFIG_CLOCK_FREQ / 1000000UL);
}
```

---

### 3.12 硬件抽象层 — Serial (arduino/serial.cpp)

**功能**: 串口通信实现，支持硬件 UART 和软件串口。

**串口选择** (由 `autoconf.h` 控制):
```cpp
// 硬件 UART: Serial / Serial1 / Serial2 / Serial3
#define KALICO_SERIAL   Serial1  // (默认)

// 软件串口: SoftwareSerial
static SoftwareSerial swSerial(CONFIG_MCU_SERIAL_SW_RX, CONFIG_MCU_SERIAL_SW_TX);
```

**关键函数**:
| 函数 | 说明 |
|------|------|
| `arduino_serial_init()` | 初始化串口，带双重初始化保护 |
| `arduino_serial_drain_rx()` | 从 Arduino 缓冲区读取字节到 Kalico 缓冲区 |
| `arduino_serial_rx_pending()` | 检查是否有待读取数据 |
| `serial_enable_tx_irq()` | 立即刷新所有待发送字节（轮询模式） |

**通信模式**: 轮询（非中断驱动）
- Arduino HardwareSerial 使用内部中断缓冲区接收数据
- `arduino_serial_drain_rx()` 从 Arduino 缓冲区取出数据，喂给 `serial_rx_byte()`
- TX 端：`serial_enable_tx_irq()` 直接调用 `KALICO_SERIAL.write()` 循环发送

---

### 3.13 硬件抽象层 — IRQ (arduino/irq.c)

**功能**: 中断管理和轮询调度。

**关键函数**:
| 函数 | 说明 |
|------|------|
| `irq_disable()` | `noInterrupts()` |
| `irq_enable()` | `interrupts()` |
| `irq_save()` | 保存 SREG/PRIMASK 并禁用中断 |
| `irq_restore()` | 恢复之前的中断状态 |
| `irq_wait()` | 等待中断（10µs 延迟 + 串口轮询 + 定时器处理） |
| `irq_poll()` | 轮询检查串口和定时器事件 |

**⚠️ 关键修改 — irq_wait() 中的串口轮询**:
```c
void irq_wait(void) {
    interrupts();
    delayMicroseconds(10);
    noInterrupts();
    // 关键：在等待期间轮询串口
    if (arduino_serial_rx_pending()) {
        arduino_serial_drain_rx();  // 喂数据到命令解析器
    }
    // 处理定时器事件
    if (arduino_timer_irq_pending()) {
        arduino_timer_irq_clear();
        uint32_t next = timer_dispatch_many();
        timer_kick_next(next);
    }
}
```
- 原版 Klipper 使用中断驱动的 UART，ISR 直接调用 `serial_rx_byte()`
- 本项目使用 Arduino 的轮询模式，必须在 `irq_wait()` 和 `irq_poll()` 中主动轮询
- 不轮询会导致死锁：`run_tasks()` 进入休眠，`sched_wake_tasks()` 永远不会被调用

---

### 3.14 通用层 — Serial IRQ (generic/serial_irq.c)

**功能**: 串口收发缓冲区管理和命令处理循环。

**缓冲区**:
```c
#define RX_BUFFER_SIZE 192
static uint8_t receive_buf[RX_BUFFER_SIZE], receive_pos;
static uint8_t transmit_buf[192], transmit_pos, transmit_max;
```

**关键函数**:
| 函数 | 说明 |
|------|------|
| `serial_rx_byte()` | 接收一个字节，遇到 SYNC 时唤醒任务 |
| `serial_get_tx_byte()` | 获取下一个待发送字节 |
| `console_task()` | 主任务：查找消息帧 → 分发命令 → 发送 ACK |
| `console_sendf()` | 编码并缓冲响应消息 |
| `console_pop_input()` | 从接收缓冲区移除已处理数据（带竞态保护） |

**竞态保护** (console_pop_input):
```c
for (;;) {
    rpos = readb(&receive_pos);
    // ... 复制数据 ...
    irqstatus_t flag = irq_save();
    if (rpos != readb(&receive_pos)) {
        // 与中断处理程序竞态，重试
        irq_restore(flag);
        continue;
    }
    receive_pos = needcopy;
    irq_restore(flag);
    break;
}
```

---

### 3.15 通用层 — Timer IRQ (generic/timer_irq.c)

**功能**: 通用定时器调度函数。

**关键函数**:
| 函数 | 说明 |
|------|------|
| `timer_from_us()` | 微秒转时钟 tick (us * CLOCK_FREQ/1000000) |
| `timer_is_before()` | 安全的时间比较（处理回绕） |
| `timer_dispatch_many()` | 循环调度定时器，返回下一个唤醒时间 |
| `timer_task()` | 定期清理 timer_repeat_until 防止溢出 |

**⚠️ 关键修改 — 禁用"过去定时器"shutdown**:
```c
// 原版 Klipper:
// if (diff < (int32_t)(-timer_from_us(1000)))
//     try_shutdown("Rescheduled timer in the past");

// 本项目: 注释掉上述检查
// 原因: AVR 16-bit 定时器截断会导致误判
// MCU 会通过 periodic_timer (100ms) 自动恢复
```

**定时器常量**:
```c
#define TIMER_REPEAT_TICKS      timer_from_us(100)  // 100µs
#define TIMER_MIN_TRY_TICKS     timer_from_us(2)     // 2µs
#define TIMER_DEFER_REPEAT_TICKS timer_from_us(5)    // 5µs
```

---

### 3.16 通用层 — CRC16 (generic/crc16_ccitt.c)

**功能**: CRC-CCITT 校验算法实现。

```c
uint16_t crc16_ccitt(uint8_t *buf, uint_fast8_t len) {
    uint16_t crc = 0xffff;
    while (len--) {
        uint8_t data = *buf++;
        data ^= crc & 0xff;
        data ^= data << 4;
        crc = ((((uint16_t)data << 8) | (crc >> 8))
               ^ (uint8_t)(data >> 4) ^ ((uint16_t)data << 3));
    }
    return crc;
}
```
- 初始值: 0xFFFF
- 用于 Klipper 协议的消息帧校验

---

### 3.17 通用层 — 内存池 (generic/alloc.c)

**功能**: 非 AVR 平台的动态内存池。

```c
#if !defined(__AVR__)
static char dynmem_pool[20 * 1024];  // 20KB 静态池
void *dynmem_start(void) { return dynmem_pool; }
void *dynmem_end(void) { return &dynmem_pool[sizeof(dynmem_pool)]; }
#endif
```
- AVR 平台使用 `arduino/gpio.c` 中基于 `_end` 和 `SP` 的堆管理
- 非 AVR 平台使用 20KB 静态数组

---

### 3.18 注册系统 (registrations.c / ctr_run.c / ctr_run.h)

**功能**: 替代原版 Klipper 的构建时自动提取机制。

**原版 Klipper**:
- `DECL_INIT(func)` 将字符串放入 `.compile_time_request` 段
- 构建脚本提取这些字符串，生成 `compile_time_request.c`
- 运行时遍历注册表执行

**本项目**:
- `DECL_INIT/DECL_TASK/DECL_SHUTDOWN` 宏变为空操作（仅作文档标记）
- 在 `registrations.c` 中手动维护三个函数指针数组
- `ctr_run.c` 遍历数组执行

**注册表**:
```c
// Init (启动时执行一次)
init_func_t ctr_init_list[] = {
    alloc_init,           // 内存分配器初始化
    arduino_serial_init,  // 串口初始化
    arduino_timer_init,   // 定时器初始化
};

// Task (主循环中周期执行)
task_func_t ctr_task_list[] = {
    console_task,   // 串口命令处理
    timer_task,     // 定时器维护
    buttons_task,   // 按键状态上报
};

// Shutdown (紧急停止时执行)
shutdown_func_t ctr_shutdown_list[] = {
    sendf_shutdown,        // 重置 sendf 重入标志
    digital_out_shutdown,  // 恢复 GPIO 默认值
};
```

---

### 3.19 配置文件 (autoconf.h)

**功能**: 静态配置，替代原版 Kconfig/menuconfig。

**关键配置项**:
| 配置 | 默认值 | 说明 |
|------|--------|------|
| `CONFIG_MACH_ARDUINO` | 1 | Arduino 框架 |
| `CONFIG_CLOCK_FREQ` | 16000000 | 16MHz (AVR) |
| `CONFIG_MCU_SERIAL_TYPE` | 0 | 0=硬件UART, 1=软件串口 |
| `CONFIG_SERIAL_BAUD` | 115200 | 串口波特率 |
| `CONFIG_AVR_STACK_SIZE` | 128 | AVR 栈保留大小 |
| `CONFIG_HAVE_GPIO` | 1 | GPIO 支持 |
| `CONFIG_HAVE_GPIO_ADC` | 1 | ADC 支持 |
| `CONFIG_WANT_BUTTONS` | 0 | 按键支持 |
| `CONFIG_WANT_STEPPER` | 0 | 步进电机（禁用） |
| `CONFIG_INLINE_STEPPER_HACK` | 0 | 内联步进调度（禁用） |
| `CONFIG_DEBUG_SERIAL_PORT` | 2 | 调试串口（禁用） |
| `CONFIG_MCU_NAME` | "arduino_uno" | MCU 名称 |

**平台检测**:
```cpp
#if defined(ARDUINO_AVR_UNO) || defined(ARDUINO_AVR_NANO)
  #define CONFIG_MCU_SERIAL_HW_PORT  0  // Serial (USB)
#else
  #define CONFIG_MCU_SERIAL_HW_PORT  1  // Serial1
#endif
```

---

### 3.20 构建系统 (platformio.ini)

**支持的开发板**:
| 环境 | 平台 | MCU | 时钟 | 波特率 |
|------|------|-----|------|--------|
| mega2560 (默认) | atmelavr | ATmega2560 | 16MHz | 250000 |
| uno | atmelavr | ATmega328P | 16MHz | 115200 |
| due | atmelsam | SAM3X8E | 84MHz | - |
| teensy40 | teensy | IMXRT1062 | 600MHz | - |
| esp32dev | espressif32 | ESP32 | 240MHz | - |

**构建标志**:
```ini
-DCONFIG_MACH_AVR=1        # AVR 架构标识
-DCONFIG_CLOCK_FREQ=16000000UL
-DCONFIG_SERIAL_BAUD=250000
-DCONFIG_AVR_STACK_SIZE=256
-fno-lto                   # 禁用 LTO（避免字符串优化问题）
```

---

### 3.21 PROGMEM 抽象 (arduino/pgm.h)

**功能**: AVR 程序存储器读写抽象。

```c
// AVR: 使用 pgm_read_* 从 Flash 读取
#define READP(VAR) ({ \
    __builtin_choose_expr(sizeof(VAR) == 1, (typeof(VAR))pgm_read_byte(&(VAR)), \
    __builtin_choose_expr(sizeof(VAR) == 2, (typeof(VAR))pgm_read_word(&(VAR)), \
    __builtin_choose_expr(sizeof(VAR) == 4, (typeof(VAR))pgm_read_dword(&(VAR)), \
    __force_link_error__unknown_type))); })

// 非AVR: 直接访问（Flash 内存映射）
#define READP(VAR) (VAR)
#define PROGMEM
```
- ATmega328P 只有 2KB SRAM，必须将常量数据放在 Flash 中
- 所有 `command_index[]`、编码器、参数类型都标记为 `PROGMEM`

---

## 四、与原版 Klipper 的关键差异总结

### 4.1 Shutdown 处理

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| Shutdown 通知 | 发送 `shutdown` 消息给主机 | **注释掉**，不发送 |
| 恢复方式 | 主机发送 `clear_shutdown` | **自动恢复** (最多50次) |
| is_shutdown 报告 | 发送 `is_shutdown` 消息 | **空函数** |
| 目的 | 确保主机知道 MCU 状态 | 避免 AVR 资源限制导致的死循环 |

### 4.2 定时器"过去"检查

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| 检查 | `try_shutdown("Rescheduled timer in the past")` | **注释掉** |
| 原因 | AVR 16-bit 定时器截断导致误判 | periodic_timer 会自动恢复 |

### 4.3 内存分配失败

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| alloc_chunk 失败 | `shutdown("alloc_chunk failed")` | **返回 NULL** (AVR) |
| alloc_chunks 失败 | `shutdown(...)` | **返回 NULL** (AVR) |
| oid_alloc 失败 | 直接 shutdown | 撤销类型赋值后 shutdown |
| allocate_oids 失败 | shutdown | **静默跳过** |

### 4.4 注册机制

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| DECL_INIT/TASK/SHUTDOWN | 构建脚本自动提取 | **手动维护** registrations.c |
| 命令注册 | 构建脚本生成 compile_time_request.c | **手工编写** |
| 编码器查找 | 字符串地址比较 | **编译时哈希** switch-case |

### 4.5 串口通信

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| UART 模式 | 中断驱动 (ISR 直接调用 serial_rx_byte) | **轮询模式** (irq_wait/irq_poll 中轮询) |
| TX 方式 | 中断驱动 (UDRE 中断) | **同步刷新** (write+flush) |

### 4.6 定时器

| 方面 | 原版 Klipper | generic_arduino |
|------|-------------|-----------------|
| AVR 定时器 | Timer1 CTC 模式 | Timer1 Normal 模式 + overflow 扩展 |
| 32位扩展 | overflow_count + TCNT1 | 同上，但有 TOV1 竞态保护 |
| Timer0 | 不使用 | **禁用** (TIMSK0=0) |

---

## 五、提供的功能 vs 缺失的功能

### ✅ 已实现
- [x] Klipper 二进制协议通信（VLQ + CRC16）
- [x] 命令路由和分发
- [x] GPIO 数字输出（含软件 PWM）
- [x] GPIO 数字输入（含去抖）
- [x] GPIO ADC 读取
- [x] 按键检测和状态上报
- [x] 调试命令（ping/read/write）
- [x] 定时器调度系统
- [x] Shutdown 处理和自动恢复
- [x] 统计上报
- [x] 多平台支持（AVR/ARM/ESP32）
- [x] PROGMEM 优化（AVR Flash 常量）

### ❌ 未实现
- [ ] 步进电机控制（CONFIG_WANT_STEPPER=0）
- [ ] 限位开关/归位（CONFIG_WANT_ENDSTOPS=0）
- [ ] SPI 通信（CONFIG_WANT_SPI=0）
- [ ] I2C 通信（CONFIG_WANT_I2C=0）
- [ ] 硬件 PWM（CONFIG_WANT_HARD_PWM=0）
- [ ] ADC 传感器（CONFIG_WANT_ADC=0）
- [ ] 软件 SPI/I2C
- [ ] 引导加载程序请求
- [ ] 温度传感器（热敏电阻）
- [ ] 加热器控制
- [ ] 风扇控制
- [ ] TMC 驱动通信
- [ ] NeoPixel/LED 控制

---

## 六、数据流详解

### 6.1 命令接收流程
```
Arduino HardwareSerial RX ISR
  → Arduino 内部缓冲区
    → irq_poll() / irq_wait()
      → arduino_serial_drain_rx()
        → serial_rx_byte()          [generic/serial_irq.c]
          → receive_buf[] 缓冲
          → 遇到 0x7E → sched_wake_tasks()
            → run_tasks() 循环
              → console_task()       [generic/serial_irq.c]
                → command_find_block()  [command.c]
                  → CRC 校验
                  → 序列号检查
                → command_dispatch()    [command.c]
                  → command_parsef()    [命令解码]
                  → func(args)          [命令处理]
                → command_send_ack()    [发送 ACK]
```

### 6.2 响应发送流程
```
命令处理函数调用 sendf("format", args...)
  → command_sendf()                 [command.c]
    → _DECL_ENCODER() → ctr_lookup_encoder(hash)  [compile_time_request.c]
    → console_sendf(ce, args)       [generic/serial_irq.c]
      → command_encode_and_frame()  [command.c]
        → command_encodef()         [VLQ 编码]
        → command_add_frame()       [LEN+SEQ+CRC+SYNC]
      → serial_enable_tx_irq()      [arduino/serial.cpp]
        → KALICO_SERIAL.write()     [Arduino API]
```

### 6.3 Timer 调度流程
```
Timer1 COMPA 中断
  → ISR(TIMER1_COMPA_vect)
    → timer_irq_pending_flag = true

irq_poll() / irq_wait()
  → arduino_timer_irq_pending()
  → arduino_timer_irq_clear()
  → timer_dispatch_many()           [generic/timer_irq.c]
    → sched_timer_dispatch()        [sched.c]
      → t->func(t)                  [定时器回调]
      → 更新定时器链表
    → 返回 next_waketime
  → timer_kick_next(next)           [arduino/timer.c]
    → OCR1A = next_time
```

---

## 七、配置实例（Arduino Uno + Multi Function Shield）

基于项目中的 `PLAN_MFS.md`，以下是典型应用场景：

```ini
# printer.cfg
[mcu arduino]
serial: /dev/ttyACM0
baud: 115200

[output_pin led_d1]
pin: ar15    # A1
value: 0
shutdown_value: 0

[output_pin led_d2]
pin: ar16    # A2
value: 0
shutdown_value: 0

[gcode_button button_s1]
pin: ^ar15   # 上拉输入
press_gcode:
  SET_PIN PIN=led_d1 VALUE=1
release_gcode:
  SET_PIN PIN=led_d1 VALUE=0
```

---

## 八、技术约束与注意事项

1. **ATmega328P 资源极限**: 32KB Flash, 2KB RAM, 1KB EEPROM
2. **PROGMEM 必须启用**: 所有常量数据必须放在 Flash 中
3. **禁用 LTO**: `-fno-lto` 防止编译器优化掉格式字符串
4. **轮询串口**: Arduino HardwareSerial 的 RX 由 ISR 缓存，但 Kalico 层使用轮询取出
5. **自动 Shutdown 恢复**: 最多 50 次重试，防止无限循环
6. **16-bit 定时器截断**: `timer_kick_next()` 不能添加"太接近"保护
7. **双重初始化保护**: `arduino_serial_init()` 和 `arduino_timer_init()` 使用 `static bool` 防止重复初始化
