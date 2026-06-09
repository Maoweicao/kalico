# ESP32 移植实施计划

## 概述

将 generic_arduino 项目移植到 ESP32 系列芯片，使用 **ISR-native gptimer** 方案。
参考 STM32H723 移植模式——创建独立的 `src/esp32/` 目录，复用 `src/generic/` 通用层。

**核心方案**：gptimer compare-match 中断直接调用 `timer_dispatch_many()`，
与 AVR/STM32 相同的 ISR-native 调度路径。

**目标芯片**：ESP32-S3（优先），ESP32（兼容）

---

## 文件结构

```
src/esp32/
├── timer.c          # ISR-native gptimer（核心）
├── irq.c            # irq_disable/enable/save/restore + irq_wait/irq_poll
├── serial.c         # USB Serial (CDC) 或 HardwareSerial
├── gpio.c           # GPIO out/in/adc/pwm
├── clock.c          # clock_freq / timer_read_time（如果从 timer.c 分离）
├── internal.h       # ESP32 平台内部声明
├── pgm.h            # PROGMEM 空宏（ESP32 不需要）
├── io.h             # 读写屏障
└── misc.h           # timer_from_us 等
```

---

## 实施步骤

### Phase 1：编译骨架（让项目跑起来）

**目标**：ESP32 环境能编译通过，串口能输出 "Starting."

#### 1.1 platformio.ini 添加 ESP32 环境

```ini
[env:esp32s3]
platform = espressif32
board = esp32-s3-devkitc-1
framework = arduino
build_flags =
    -Isrc
    -Isrc/board
    -Isrc/esp32
    -Isrc/generic
    -Isrc/lib/KalicoProtocol/src
    -DCONFIG_MACH_ESP32=1
    -DCONFIG_BOARD_DIRECTORY=\"\\\"esp32\\\"\"
    -DCONFIG_CLOCK_FREQ=80000000UL
    -DCONFIG_SERIAL_BAUD=250000
    ; IRAM 优化
    -mtext-section-literals
    ; FreeRTOS 配置
    -DconfigMAX_SYSCALL_INTERRUPT_PRIORITY=5
build_src_filter =
    +<*>
    -<.git/>
    -<.svn/>
    -<stm32/>
lib_extra_dirs =
    ${common.lib_extra_dirs_common}
monitor_speed = 250000
```

#### 1.2 src/esp32/internal.h

基本平台声明，参照 `src/arduino/internal.h` 和 `src/stm32/internal.h`。

#### 1.3 src/esp32/pgm.h, io.h, misc.h

- `pgm.h`：ESP32 统一地址空间，`pgm_read_byte` 直接解引用
- `io.h`：内存屏障（`__asm__ volatile("memw")`）
- `misc.h`：`timer_from_us()` 宏

#### 1.4 src/esp32/gpio.c

最小实现：`gpio_out_setup/write/toggle_noirq`，用 Arduino `digitalWrite`。
PWM/ADC 后续再做。

#### 1.5 src/esp32/serial.c

用 Arduino `HardwareSerial`（Serial0 → TX/RX 引脚）。
参照 `src/arduino/serial.cpp` 的缓冲区实现。

#### 1.6 src/esp32/irq.c

先用 poll-based 模式（和当前 `src/arduino/irq.c` 的 ESP32 分支一样），
确保编译通过后再切 ISR-native。

#### 1.7 src/esp32/timer.c

先用 poll-based 模式（`micros()` + flag），确保基础功能正常。

#### 1.8 main.cpp ESP32 初始化

添加 `#if defined(CONFIG_MACH_ESP32)` 分支：
- `setup()`：调用 `arduino_serial_init()` + `arduino_timer_init()`
- `loop()`：调用 `sched_main()`
- 将 loop 任务绑定到 Core 1

**验证**：`pio run -e esp32s3` 编译通过，串口输出正常。

---

### Phase 2：ISR-native gptimer

**目标**：定时器中断直接分发步进事件，延迟 < 5µs。

#### 2.1 timer.c 改造

替换 poll-based 为 ISR-native：

```c
// 核心：gptimer ISR 直接调用 timer_dispatch_many()
static bool IRAM_ATTR
gptimer_alarm_isr(gptimer_handle_t timer,
                  const gptimer_alarm_event_data_t *edata,
                  void *user_data)
{
    uint32_t next = timer_dispatch_many();
    // 设置下一次 alarm
    gptimer_alarm_config_t alarm_config = {
        .alarm_count = (uint64_t)next,
        .reload_count = 0,
        .flags.auto_reload_on_alarm = false,
    };
    gptimer_set_alarm_action(timer, &alarm_config);
    return false;
}
```

关键点：
- 所有 ISR 路径代码加 `IRAM_ATTR`
- `timer_read_time()` 读 gptimer 硬件计数器
- `timer_kick()` / `timer_kick_next()` 设置 compare match
- `arduino_timer_irq_pending()` 返回 false（ISR 直接处理）

#### 2.2 irq.c 改造

ESP32 走 ISR-native 路径（和 AVR 一样）：

```c
// irq_wait：只处理串口，不处理定时器
// irq_poll：只处理串口，不处理定时器
```

#### 2.3 ISR 优先级配置

gptimer ISR 设为 Level 4（低于 FreeRTOS tick 的 Level 1）。
在 `gptimer_new_timer()` 之前设置 `intr_alloc_flags`。

**验证**：编译通过，`timer_dispatch_many()` 在 ISR 中被调用。

---

### Phase 3：基础测试

**目标**：验证步进脉冲定时精度。

#### 3.1 串口连接测试

printer.cfg：
```ini
[mcu esp32]
serial: /dev/ttyUSB0
baud: 250000
```

验证 MCU 能正常握手。

#### 3.2 GPIO 测试

用 `SET_PIN` 命令测试 GPIO 输出。

#### 3.3 步进定时测试

配置一个步进电机，用 `STEPPER_BUZZ` 测试。
监控 `stats` 输出，检查是否有定时器溢出。

#### 3.4 ISR 抖动测量

在 gptimer ISR 中添加测量代码：
```c
static volatile uint32_t max_isr_jitter = 0;
// 在 ISR 中：
uint32_t now = timer_read_time();
uint32_t expected = (uint32_t)edata->alarm_value;
uint32_t jitter = (int32_t)(now - expected);
if (jitter > max_isr_jitter) max_isr_jitter = jitter;
```

**验证**：ISR 抖动 < 10µs。

---

### Phase 4：WiFi 并发测试

**目标**：WiFi 开启时步进定时仍然稳定。

#### 4.1 Core 绑定

- Core 0：WiFi/BLE 栈（ESP-IDF 默认）
- Core 1：Klipper loop 任务 + gptimer ISR

#### 4.2 测试方法

1. 连接 WiFi，启动 Web UI
2. 打印 XYZ 校准立方体
3. 打印过程中通过 Web UI 发送命令
4. 检查日志中是否有 "Rescheduled timer in the past" 错误

**验证**：WiFi 活动时无定时器溢出。

---

### Phase 5：外设驱动

#### 5.1 ADC（温度读取）

`gpio_adc_setup/sample/read`，用 ESP32 ADC2 通道。

#### 5.2 PWM（加热器/风扇）

`gpio_pwm_setup/write`，用 ESP32 LEDC 硬件。

#### 5.3 SPI/I2C（可选）

显示屏、加速度计等外设支持。

---

## 风险与缓解

| 风险 | 概率 | 缓解 |
|------|------|------|
| WiFi 导致 ISR 抖动 > 10µs | 中 | Core 0/1 分离，WiFi 绑 Core 0 |
| Flash cache miss 导致 ISR 延迟 | 中 | 所有 ISR 代码加 IRAM_ATTR |
| gptimer API 不兼容旧 ESP32 | 低 | 用 `GPTIMER_CLK_SRC_DEFAULT`，兼容全系列 |
| Arduino 框架和 ESP-IDF 冲突 | 中 | 用 PlatformIO 的 ESP32 Arduino 框架，它已集成 ESP-IDF |
| IRAM 空间不足 | 低 | 只把关键 ISR 路径放 IRAM，其他代码留 Flash |

## 参考资料

- `DOC_ESP32_REALTIME.md`：完整技术分析（已有）
- `src/stm32/`：STM32H723 移植参考
- `src/arduino/timer.c`：AVR ISR-native 实现参考
- ESP-IDF gptimer 文档：https://docs.espressif.com/projects/esp-idf/en/latest/esp32s3/api-reference/peripherals/gptimer.html

---

## 预估工作量

| 阶段 | 时间 | 依赖 |
|------|------|------|
| Phase 1：编译骨架 | 2-3h | 无 |
| Phase 2：ISR-native | 3-4h | Phase 1 |
| Phase 3：基础测试 | 1-2h | Phase 2 + 硬件 |
| Phase 4：WiFi 测试 | 1-2h | Phase 3 |
| Phase 5：外设驱动 | 3-5h | Phase 3 |

总计约 **10-16 小时**（不含硬件调试时间）。
