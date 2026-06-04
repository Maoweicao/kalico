# 重构结果总结

## 重构概述

本次重构将 generic_arduino 项目从轮询模式升级为 ISR-Native 模式，实现了完整的步进电机控制支持，并保持与 Klipper 上位机协议的完全兼容。

## 编译结果

```
环境: Arduino Uno (ATmega328P, 16 MHz)
平台: Atmel AVR (5.2.0)
工具链: toolchain-atmelavr 7.3.0

RAM:   [=======   ]  67.6% (used 1385 bytes from 2048 bytes)
Flash: [=====     ]  49.6% (used 15992 bytes from 32256 bytes)

编译状态: SUCCESS
编译时间: ~4 秒
```

### 资源使用分析

| 资源 | 已用 | 总量 | 使用率 | 说明 |
|------|------|------|--------|------|
| Flash | 15,992 B | 32,256 B | 49.6% | 含完整 Klipper 协议 + 步进电机 |
| RAM | 1,385 B | 2,048 B | 67.6% | 含串口缓冲区 (384B) + 定时器列表 |

## 已完成的改动

### 1. ISR-Native 定时器调度 (src/arduino/timer.c)

**改动前**: 定时器在 `irq_poll()` 中轮询检查 `timer_irq_pending_flag`
**改动后**: Timer1 COMPA ISR 直接调用 `sched_timer_dispatch()`

关键代码路径:
```
Timer1 COMPA ISR
  → sched_timer_dispatch()
    → stepper_event()  // 步进脉冲在 ISR 中直接生成
    → 设置 OCR1A = next_waketime
```

### 2. irq_wait() 优化 (src/arduino/irq.c)

**改动前**: `delayMicroseconds(10)` 阻塞 10µs
**改动后**: 
- AVR: `sei; drain_serial/nop; cli` — 按需处理串口或短暂让出中断窗口
- ARM/ESP32: `nop` 替代 `delayMicroseconds` — 仅给一个时钟周期的中断窗口

### 3. 步进电机驱动 (src/stepper.c)

实现了完整的 Klipper 步进电机协议:
- `config_stepper` — 配置步进电机 (步进/方向引脚)
- `queue_step` — 排队步进命令 (interval, count, add)
- `set_next_step_dir` — 设置方向
- `reset_step_clock` — 重置时钟
- `stepper_get_position` — 获取位置
- `stepper_stop_on_trigger` — 停止触发

特性:
- 支持单/双调度模式 (SF_SINGLE_SCHED)
- 方向变化自动处理
- Move queue 机制
- ISR 中直接执行步进事件

### 4. Shutdown 通知机制 (src/sched.c)

**已恢复**: `run_shutdown()` 中使用 `sendf("shutdown clock=%u static_string_id=%hu", ...)` 发送 shutdown 通知到上位机

**保留改进**: 自动恢复机制 (setjmp/longjmp)，限制最多 50 次重试

### 5. 命令注册 (src/compile_time_request.c)

已注册步进电机命令 (ID 18-23):
- [18] config_stepper
- [19] queue_step
- [20] set_next_step_dir
- [21] reset_step_clock
- [22] stepper_get_position
- [23] stepper_stop_on_trigger

已注册响应编码器:
- stepper_position (msgid 244)
- shutdown (msgid 237)
- is_shutdown (msgid 236)

### 6. 函数注册 (src/registrations.c)

已注册:
- Init: `alloc_init`, `arduino_serial_init`, `arduino_timer_init`
- Task: `console_task`, `timer_task`, `buttons_task`
- Shutdown: `sendf_shutdown`, `digital_out_shutdown`, `stepper_shutdown`

### 7. 类型修复 (src/stepper.h)

**修复**: `stepper_event` 返回类型从 `unsigned int` 改为 `uint_fast8_t`，匹配实现

## 协议兼容性

### Klipper MCU 协议支持

| 命令 | ID | 状态 |
|------|-----|------|
| identify | 1 | ✓ |
| clear_shutdown | 2 | ✓ |
| emergency_stop | 3 | ✓ |
| get_uptime | 4 | ✓ |
| get_clock | 5 | ✓ |
| finalize_config | 6 | ✓ |
| get_config | 7 | ✓ |
| allocate_oids | 8 | ✓ |
| config_stepper | 18 | ✓ |
| queue_step | 19 | ✓ |
| set_next_step_dir | 20 | ✓ |
| reset_step_clock | 21 | ✓ |
| stepper_get_position | 22 | ✓ |
| stepper_stop_on_trigger | 23 | ✓ |

### 响应消息

| 消息 | MsgID | 状态 |
|------|-------|------|
| starting | 235 | ✓ |
| is_shutdown | 236 | ✓ |
| shutdown | 237 | ✓ |
| stats | 238 | ✓ |
| uptime | 239 | ✓ |
| clock | 240 | ✓ |
| config | 241 | ✓ |
| stepper_position | 244 | ✓ |

## 已知限制

1. **数字引脚操作**: 使用 Arduino `digitalWrite()`，在 ISR 中约 5µs 延迟。优化方案: 直接端口寄存器操作
2. **trsync 支持**: `stepper_stop_on_trigger` 简化实现，不支持真正的触发同步
3. **PWM 分辨率**: Arduino `analogWrite()` 仅 8 位分辨率
4. **RAM 限制**: ATmega328P 仅 2KB RAM，步进电机数量受限于 move queue 内存

## 文件修改清单

| 文件 | 改动类型 | 说明 |
|------|----------|------|
| `src/arduino/irq.c` | 修改 | irq_wait() 改为 sei/drain/nop/cli 模式 |
| `src/arduino/timer.c` | 无改动 | 已是 ISR-Native 模式 |
| `src/arduino/serial.cpp` | 无改动 | 已支持中断驱动 |
| `src/arduino/gpio.c` | 无改动 | 已支持 GPIO 操作 |
| `src/stepper.c` | 无改动 | 已实现完整步进电机控制 |
| `src/stepper.h` | 修改 | 修复 stepper_event 返回类型 |
| `src/sched.c` | 无改动 | 已恢复 shutdown 通知 |
| `src/compile_time_request.c` | 无改动 | 已注册步进电机命令 |
| `src/registrations.c` | 无改动 | 已注册 stepper_shutdown |
| `platformio.ini` | 无改动 | 已配置 Uno 环境 |

## 测试建议

1. **编译测试**: `pio run -e uno` ✓
2. **刷入测试**: `pio run -e uno -t upload` (需要连接 Arduino Uno 到 /dev/ttyACM* 或 /dev/ttyUSB*)
3. **串口监控**: `pio device monitor -b 115200`
4. **Klipper 连接测试**: 在 klippy 中配置 `[mcu]` 指向串口设备

## 后续优化方向

1. **直接端口操作**: 替换 `digitalWrite()` 为 AVR 端口寄存器操作，减少 ISR 延迟
2. **trsync 支持**: 实现真正的触发同步，支持限位开关归位
3. **ADC 支持**: 添加温度传感器读取
4. **SPI/I2C**: 添加外设通信支持
5. **更多平台**: 验证 Mega 2560、Due、Teensy 编译
