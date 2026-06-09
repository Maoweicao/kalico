# Arduino 下位机固件完整重规划

## 一、架构总览

```
┌─────────────────────────────────────────────────────┐
│                 Klipper 主机 (Python)                │
│   klippy/extras/gcode_move.py, output_pin.py, etc. │
└───────────────────────┬─────────────────────────────┘
                        │ USB Serial (115200 baud)
                        ▼
┌─────────────────────────────────────────────────────┐
│              Arduino Uno (ATmega328P)                │
│                                                     │
│  ┌──────────────────────────────────────────────┐   │
│  │ serial.cpp  ← 原生 AVR UART 中断驱动         │   │
│  │   USART_RX_vect  → serial_rx_byte()          │   │
│  │   USART_UDRE_vect ← serial_get_tx_byte()     │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐   │
│  │ serial_irq.c  ← 通用收发缓冲区               │   │
│  │   receive_buf[192]  transmit_buf[96]          │   │
│  │   console_task()  → command_find_block()      │   │
│  │   console_sendf() → command_encode_and_frame()│   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐   │
│  │ command.c  ← 命令解析/响应编码               │   │
│  │   command_dispatch()  → command_index[cmdid]  │   │
│  │   command_sendf()     → ctr_lookup_encoder()  │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐   │
│  │ compile_time_request.c  ← 核心注册表          │   │
│  │   command_index[]     命令→处理函数映射        │   │
│  │   ctr_lookup_encoder() 格式串→编码器映射       │   │
│  │   command_identify_data[] 握手JSON(zlib)      │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐   │
│  │ 命令处理模块                                  │   │
│  │   basecmd.c    identify/uptime/clock/config   │   │
│  │   gpiocmds.c   GPIO输出(set/update/queue)     │   │
│  │   buttons.c    按键检测(config/add/query)      │   │
│  │   debugcmds.c  调试(ping/read/write/nop)      │   │
│  │   sched.c      调度器(stats/shutdown)         │   │
│  └──────────────┬───────────────────────────────┘   │
│                 │                                    │
│  ┌──────────────▼───────────────────────────────┐   │
│  │ 硬件抽象层                                    │   │
│  │   gpio.c     Arduino digitalWrite/Read        │   │
│  │   timer.c    Timer1 CTC 中断调度              │   │
│  │   irq.c      sei/cli 中断管理                 │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## 二、问题根因分析

### 问题1：LTO 优化删除 sendf 格式字符串

**根因**：`sendf("uptime high=%u clock=%u", ...)` 中的格式字符串是编译时常量。
LTO 分析时，编译器认为 `ctr_lookup_encoder()` 只是做字符串比较返回指针，
可能将整个查找逻辑内联并优化掉"不可达"的分支，导致格式字符串被删除。

**解决方案**：在 `compile_time_request.c` 中将格式字符串定义为 `static const PROGMEM`
并加上 `__attribute__((used))`，确保它们与 `ctr_lookup_encoder()` 在同一编译单元中。
这样 LTO 能直接看到字符串的使用点，不会误删。

### 问题2：缺少关键编码器

当前 `compile_time_request.c` 只有 4 个编码器（starting, identify_response,
shutdown, is_shutdown），缺少 uptime、clock、config、stats、debug_result、pong、
buttons_state 等。任何 sendf 调用找不到编码器都会静默失败。

### 问题3：command_index 数组太小

当前 command_index 只有 3 个条目（ID 0-2），但 GPIO 命令需要 ID 13-17，
buttons 命令需要 ID 46-49。数组越界导致 undefined behavior。

### 问题4：缺少 buttons_task 注册

`buttons.c` 中的 `DECL_TASK(buttons_task)` 不会被构建系统提取，
需要在 `registrations.c` 中手动注册。

## 三、完整命令/响应 ID 映射

### 命令 (MCU 接收)
| ID  | 格式串                                                    | 处理函数                    | 来源        |
|-----|----------------------------------------------------------|---------------------------|-------------|
| 1   | `identify offset=%u count=%c`                            | command_identify          | basecmd.c   |
| 2   | `clear_shutdown`                                         | command_clear_shutdown    | basecmd.c   |
| 3   | `emergency_stop`                                         | command_emergency_stop    | basecmd.c   |
| 4   | `get_uptime`                                             | command_get_uptime        | basecmd.c   |
| 5   | `get_clock`                                              | command_get_clock         | basecmd.c   |
| 6   | `finalize_config crc=%u`                                 | command_finalize_config   | basecmd.c   |
| 7   | `get_config`                                             | command_get_config        | basecmd.c   |
| 8   | `allocate_oids count=%c`                                 | command_allocate_oids     | basecmd.c   |
| 9   | `debug_nop`                                              | command_debug_nop         | debugcmds.c |
| 10  | `debug_ping data=%*s`                                    | command_debug_ping        | debugcmds.c |
| 11  | `debug_write order=%c addr=%u val=%u`                    | command_debug_write       | debugcmds.c |
| 12  | `debug_read order=%c addr=%u`                            | command_debug_read        | debugcmds.c |
| 13  | `set_digital_out pin=%u value=%c`                        | command_set_digital_out   | gpiocmds.c  |
| 14  | `update_digital_out oid=%c value=%c`                     | command_update_digital_out| gpiocmds.c  |
| 15  | `queue_digital_out oid=%c clock=%u on_ticks=%u`          | command_queue_digital_out | gpiocmds.c  |
| 16  | `set_digital_out_pwm_cycle oid=%c cycle_ticks=%u`        | command_set_digital_out_pwm_cycle | gpiocmds.c |
| 17  | `config_digital_out oid=%c pin=%u value=%c default_value=%c max_duration=%u` | command_config_digital_out | gpiocmds.c |
| 46  | `buttons_ack oid=%c count=%c`                            | command_buttons_ack       | buttons.c   |
| 47  | `buttons_query oid=%c clock=%u rest_ticks=%u retransmit_count=%c invert=%c` | command_buttons_query | buttons.c |
| 48  | `buttons_add oid=%c pos=%c pin=%u pull_up=%c`            | command_buttons_add       | buttons.c   |
| 49  | `config_buttons oid=%c button_count=%c`                  | command_config_buttons    | buttons.c   |

### 响应 (MCU 发送)
| ID  | 格式串                                                    | 来源        |
|-----|----------------------------------------------------------|-------------|
| 235 | `starting`                                               | sched.c     |
| 236 | `is_shutdown static_string_id=%hu`                       | sched.c     |
| 237 | `shutdown clock=%u static_string_id=%hu`                 | sched.c     |
| 238 | `stats count=%u sum=%u sumsq=%u`                         | basecmd.c   |
| 239 | `uptime high=%u clock=%u`                                | basecmd.c   |
| 240 | `clock clock=%u`                                         | basecmd.c   |
| 241 | `config is_config=%c crc=%u is_shutdown=%c move_count=%hu` | basecmd.c |
| 242 | `pong data=%*s`                                          | debugcmds.c |
| 243 | `debug_result val=%u`                                    | debugcmds.c |
| 250 | `buttons_state oid=%c ack_count=%c state=%*s`            | buttons.c   |

## 四、实施计划

### Phase 1: 修复核心通信 (compile_time_request.c)
- [ ] 添加所有缺失的编码器（uptime, clock, config, stats, debug_result, pong, buttons_state）
- [ ] 扩展 command_index 数组到 50+ 条目
- [ ] 注册所有命令处理函数
- [ ] 使用 `__attribute__((used))` 和 PROGMEM 保护格式字符串
- [ ] 更新 identify JSON 数据（包含所有新命令/响应）

### Phase 2: 更新注册表 (registrations.c)
- [ ] 添加 buttons_task 到任务列表
- [ ] 添加 digital_out_shutdown 到关机列表
- [ ] 确保所有 DECL_INIT/DECL_TASK/DECL_SHUTDOWN 都有对应注册

### Phase 3: 修复平台配置
- [ ] platformio.ini: 确认 `-fno-lto` 已启用
- [ ] autoconf.h: 启用 CONFIG_WANT_BUTTONS=1
- [ ] 确认 GPIO 引脚枚举正确

### Phase 4: 验证测试
- [ ] 编译通过（无警告）
- [ ] Flash 使用率 < 30KB (93%)
- [ ] RAM 使用率 < 1.5KB (75%)
- [ ] Klipper 能完成 identify 握手
- [ ] 所有命令正确响应
- [ ] GPIO 输出可控
- [ ] 按键输入可读

## 五、关键约束

1. **不写新 C 代码**：复用上游 Klipper 的 gpiocmds.c 和 buttons.c
2. **不使用 Arduino HardwareSerial**：直接操作 AVR UART 寄存器
3. **PROGMEM 必须启用**：ATmega328P 只有 2KB RAM
4. **ATmega328P 限制**：32KB Flash, 2KB RAM, 1KB EEPROM
5. **波特率 115200**：与 printer.cfg 一致
