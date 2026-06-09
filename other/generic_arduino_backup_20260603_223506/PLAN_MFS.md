# Multi Function Shield (MFS) 驱动实现规划

## 硬件分析

### MFS 引脚分配（标准版）

| 组件 | Arduino 引脚 | 数字引脚号 | 电平 | 备注 |
|------|-------------|-----------|------|------|
| LED D1 | A1 | 15 | LOW=亮 | 与 S1 共用（跳线） |
| LED D2 | A2 | 16 | LOW=亮 | 与 S2 共用（跳线） |
| LED D3 | A3 | 17 | LOW=亮 | 与 S3 共用（跳线） |
| LED D4 | A4 | 18 | LOW=亮 | 独立 |
| 按键 S1 | A1 | 15 | LOW=按下 | 与 D1 共用（跳线） |
| 按键 S2 | A2 | 16 | LOW=按下 | 与 D2 共用（跳线） |
| 按键 S3 | A3 | 17 | LOW=按下 | 与 D3 共用（跳线） |
| 蜂鸣器 | D3 | 3 | LOW=响 | 支持 tone() |
| 电位器 | A0 | 14 | ADC | 10-bit |
| TM1637 CLK | D4 | 4 | - | 时钟线 |
| TM1637 DIO | D5 | 5 | - | 数据线 |

### 引脚冲突说明
- D1/D2/D3 同时连接 LED 和按键（通过跳线帽连接）
- **解决方案**：移除跳线帽，LED 和按键分离使用
- 或：保留跳线，只用 LED（按键读取时 LED 会亮）

### 未使用引脚
- D2 (pin 2) — 可用于其他用途
- D6-D13 — 可用于步进电机、加热器等
- A5 (pin 19) — 可用于其他传感器

---

## 实现方案

### 第一层：LED 控制（4 个 output_pin）

**使用现有 Klipper 模块**：`output_pin` + `gpiocmds.c`

**无需编写任何 MCU 代码**！Klipper 的 `config_digital_out` / `update_digital_out` 命令已经支持。

**printer.cfg 配置**：
```ini
[output_pin led_d1]
pin: ar15          # A1
value: 0
shutdown_value: 0

[output_pin led_d2]
pin: ar16          # A2
value: 0
shutdown_value: 0

[output_pin led_d3]
pin: ar17          # A3
value: 0
shutdown_value: 0

[output_pin led_d4]
pin: ar18          # A4
value: 0
shutdown_value: 0
```

**GCode 命令**：`SET_PIN PIN=led_d1 VALUE=1` （开灯）
             `SET_PIN PIN=led_d1 VALUE=0` （关灯）

**注意**：LED 低电平亮，需要 `invert: true` 或在 VALUE 中取反。

---

### 第二层：蜂鸣器控制

**方案 A：使用 output_pin（简单开关）**
```ini
[output_pin buzzer]
pin: ar3           # D3
value: 0
shutdown_value: 0
```
- `SET_PIN PIN=buzzer VALUE=1` → 响
- `SET_PIN PIN=buzzer VALUE=0` → 停

**方案 B：使用 tone() PWM（需要自定义命令）**

需要新增 MCU 命令 `buzzer_tone`：
```
// MCU 端
DECL_COMMAND(command_buzzer_tone, "buzzer_tone pin=%c frequency=%u duration=%u");
// 调用 Arduino tone(pin, freq, duration)
```

```python
# Host 端
# printer.cfg
[buzzer]
pin: ar3
# GCode: M300 S2000 P500  (2000Hz, 500ms)
```

**推荐方案 B** — 支持不同音调，更有用。

---

### 第三层：按键输入

**使用现有 Klipper 模块**：`buttons` + `buttons.c`

**无需编写任何 MCU 代码**！

**printer.cfg 配置**：
```ini
[buttons]
# 如果移除了跳线帽：
buttons:
  - pin: ^ar15     # S1, 上拉
  - pin: ^ar16     # S2, 上拉
  - pin: ^ar17     # S3, 上拉
press_gcode:
  M118 Button {0} pressed
release_gcode:
  M118 Button {0} released
```

或者使用 `[gcode_button]` 单独配置：
```ini
[gcode_button button_s1]
pin: ^ar15
press_gcode:
  M118 S1 pressed
release_gcode:
  M118 S1 released
```

**注意**：如果跳线帽保留，按键读取时 LED 会亮（共用引脚）。

---

### 第四层：TM1637 数码管（需要新代码）

**这是唯一需要编写新代码的部分。**

#### TM1637 协议

TM1637 使用两线串行协议（类似 I2C 但不兼容）：

```
START: CLK=HIGH, DIO从HIGH→LOW
STOP:  CLK=HIGH, DIO从LOW→HIGH
数据:  CLK下降沿时DIO有效，MSB first
ACK:   第9个CLK，DIO被拉低表示应答
```

时序要求：
- CLK 频率：~100kHz（10μs 周期）
- 数据建立时间：>1μs
- CLK 高电平宽度：>1μs

#### TM1637 命令

| 命令 | 说明 | 格式 |
|------|------|------|
| 0x40 | 数据命令：写显示 | 0x40 + auto_inc + normal |
| 0x42 | 数据命令：读键扫 | 0x42 |
| 0x44 | 显示控制 | 0x44 + on + brightness |
| 0x80 | 地址命令 | 0xC0 + addr(0-5) |

显示数据：6 个字节（地址 0x00-0x05），对应 6 个段选
亮度：0-7 级

#### MCU 端实现

**新增文件**：`src/arduino/tm1637.c`

```c
// TM1637 两线协议实现
#include "autoconf.h"
#include "command.h"
#include "sched.h"
#include <avr/io.h>

// 引脚定义（使用 Arduino 引脚号）
#define TM1637_CLK_PIN  4   // D4
#define TM1637_DIO_PIN  5   // D5

// 直接操作 AVR 端口
// D4 = PD4 (PORTD bit 4)
// D5 = PD5 (PORTD bit 5)
#define CLK_PORT  PORTD
#define CLK_DDR   DDRD
#define CLK_BIT   PD4
#define DIO_PORT  PORTD
#define DIO_DDR   DDRD
#define DIO_BIT   PD5

static void tm1637_delay(void) {
    // ~2μs delay at 16MHz
    asm volatile("nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop"
                 "nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop"
                 "nop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop\nnop"
                 :::);
}

static void tm1637_clk_high(void) { CLK_PORT |= (1 << CLK_BIT); }
static void tm1637_clk_low(void)  { CLK_PORT &= ~(1 << CLK_BIT); }
static void tm1637_dio_high(void) { DIO_DDR &= ~(1 << DIO_BIT); DIO_PORT |= (1 << DIO_BIT); }
static void tm1637_dio_low(void)  { DIO_DDR |= (1 << DIO_BIT); DIO_PORT &= ~(1 << DIO_BIT); }

static void tm1637_start(void) {
    tm1637_dio_high();
    tm1637_clk_high();
    tm1637_delay();
    tm1637_dio_low();
    tm1637_delay();
}

static void tm1637_stop(void) {
    tm1637_clk_low();
    tm1637_delay();
    tm1637_dio_low();
    tm1637_delay();
    tm1637_clk_high();
    tm1637_delay();
    tm1637_dio_high();
}

static uint8_t tm1637_write_byte(uint8_t data) {
    for (uint8_t i = 0; i < 8; i++) {
        tm1637_clk_low();
        if (data & 0x01)
            tm1637_dio_high();
        else
            tm1637_dio_low();
        tm1637_delay();
        tm1637_clk_high();
        tm1637_delay();
        data >>= 1;
    }
    // ACK bit
    tm1637_clk_low();
    tm1637_dio_high();
    tm1637_delay();
    tm1637_clk_high();
    tm1637_delay();
    uint8_t ack = !(DIO_PORT & (1 << DIO_BIT));  // 实际应该读 PIND
    tm1637_clk_low();
    return ack;
}

// MCU 命令：显示数据
// tm1637_display brightness=%c data=%*s
void command_tm1637_display(uint32_t *args) {
    uint8_t brightness = args[0];
    uint8_t len = args[1];
    uint8_t *data = command_decode_ptr(args[2]);
    
    // 设置亮度 + 开显示
    tm1637_start();
    tm1637_write_byte(0x88 | (brightness & 0x07));
    tm1637_stop();
    
    // 写数据（自动递增模式）
    tm1637_start();
    tm1637_write_byte(0x40);  // 数据命令：自动递增
    tm1637_stop();
    
    tm1637_start();
    tm1637_write_byte(0xC0);  // 地址：从 0 开始
    for (uint8_t i = 0; i < len && i < 6; i++)
        tm1637_write_byte(data[i]);
    tm1637_stop();
}

DECL_COMMAND(command_tm1637_display,
    "tm1637_display brightness=%c data=%*s");

// MCU 命令：清屏
void command_tm1637_clear(uint32_t *args) {
    tm1637_start();
    tm1637_write_byte(0x88);  // 亮度 0
    tm1637_stop();
    
    tm1637_start();
    tm1637_write_byte(0x40);
    tm1637_stop();
    
    tm1637_start();
    tm1637_write_byte(0xC0);
    for (uint8_t i = 0; i < 6; i++)
        tm1637_write_byte(0x00);
    tm1637_stop();
}

DECL_COMMAND(command_tm1637_clear, "tm1637_clear");
```

**注册**：在 `registrations.c` 中添加 `DECL_COMMAND(command_tm1637_display, ...)`

**编译配置**：在 `platformio.ini` 的 `build_flags` 中添加：
```
-DHAVE_TM1637=1
```

#### Host 端实现

**新增文件**：`/home/mellow/klipper/klippy/extras/mfs.py`

```python
# Multi Function Shield driver for Klipper
import logging

class MFSDisplay:
    """TM1637 4-digit 7-segment display on MFS"""
    
    # 7-segment encoding (common cathode, TM1637 bit order: dp-g-f-e-d-c-b-a)
    SEGMENTS = {
        '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F,
        '4': 0x66, '5': 0x6D, '6': 0x7D, '7': 0x07,
        '8': 0x7F, '9': 0x6F, 'A': 0x77, 'b': 0x7C,
        'C': 0x39, 'd': 0x5E, 'E': 0x79, 'F': 0x71,
        '-': 0x40, ' ': 0x00, '.': 0x80,
    }
    
    def __init__(self, config):
        self.printer = config.get_printer()
        self.mcu = None
        self.cmd_display = None
        self.cmd_clear = None
        self.brightness = config.getint('brightness', 7, minval=0, maxval=7)
        self.mcu.register_config_callback(self.build_config)
        
        # Register GCode commands
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('MFS_DISPLAY', self.cmd_MFS_DISPLAY)
        gcode.register_command('MFS_CLEAR', self.cmd_MFS_CLEAR)
    
    def build_config(self):
        cmd_queue = self.mcu.alloc_command_queue()
        self.cmd_display = self.mcu.lookup_command(
            "tm1637_display brightness=%c data=%*s", cq=cmd_queue)
        self.cmd_clear = self.mcu.lookup_command(
            "tm1637_clear", cq=cmd_queue)
    
    def encode_text(self, text):
        """Encode text string to TM1637 segment data"""
        data = bytearray(6)  # 4 digits + 2 extra
        pos = 0
        i = 0
        while i < len(text) and pos < 6:
            ch = text[i]
            if ch == '.' and pos > 0:
                # Decimal point goes on previous digit
                data[pos - 1] |= 0x80
            else:
                seg = self.SEGMENTS.get(ch, 0x00)
                if i + 1 < len(text) and text[i + 1] == '.':
                    seg |= 0x80
                    i += 1
                data[pos] = seg
                pos += 1
            i += 1
        return data
    
    def display_text(self, text, brightness=None):
        """Send text to display"""
        if brightness is None:
            brightness = self.brightness
        data = self.encode_text(text)
        self.cmd_display.send([brightness, data])
    
    def clear(self):
        """Clear display"""
        self.cmd_clear.send([])
    
    def cmd_MFS_DISPLAY(self, gcmd):
        text = gcmd.get('TEXT', '    ')
        brightness = gcmd.get_int('BRIGHTNESS', self.brightness, minval=0, maxval=7)
        self.display_text(text, brightness)
    
    def cmd_MFS_CLEAR(self, gcmd):
        self.clear()


class MFSBuzzer:
    """Buzzer on MFS (pin D3)"""
    
    def __init__(self, config):
        self.printer = config.get_printer()
        self.mcu = None
        self.cmd_tone = None
        self.mcu.register_config_callback(self.build_config)
        
        gcode = self.printer.lookup_object('gcode')
        gcode.register_command('MFS_BEEP', self.cmd_MFS_BEEP)
    
    def build_config(self):
        cmd_queue = self.mcu.alloc_command_queue()
        self.cmd_tone = self.mcu.lookup_command(
            "buzzer_tone pin=%c frequency=%u duration=%u", cq=cmd_queue)
    
    def beep(self, frequency=2000, duration=100):
        self.cmd_tone.send([3, frequency, duration])  # pin=3 (D3)
    
    def cmd_MFS_BEEP(self, gcmd):
        freq = gcmd.get_int('FREQUENCY', 2000, minval=100, maxval=10000)
        dur = gcmd.get_int('DURATION', 100, minval=10, maxval=5000)
        self.beep(freq, dur)


def load_config(config):
    return MFSDisplay(config)

def load_config_prefix(config):
    # For [mfs_display] and [mfs_buzzer]
    return MFSDisplay(config)
```

---

## 实现步骤

### Phase 1: LED + 按键（零代码，仅配置）

**目标**：4 个 LED 和 3 个按键立即可用

1. 创建 printer.cfg 配置
2. 测试 SET_PIN 命令控制 LED
3. 测试按钮事件回调

**预计时间**：10 分钟
**代码量**：0 行 C 代码，~30 行 printer.cfg

### Phase 2: 蜂鸣器（小改动）

**目标**：蜂鸣器能发出不同音调

1. 在 MCU 端添加 `buzzer_tone` 命令（~30 行 C 代码）
2. 使用 Arduino `tone()` 函数
3. 在 registrations.c 中注册
4. 编译烧录测试

**预计时间**：20 分钟
**代码量**：~30 行 C 代码

### Phase 3: TM1637 数码管（核心工作）

**目标**：4 位数码管显示数字/文字

1. 编写 MCU 端 TM1637 驱动（~120 行 C 代码）
2. 编写 Host 端 Python 模块（~100 行）
3. 注册 MCU 命令
4. 编译烧录测试
5. 集成到 Klipper

**预计时间**：1 小时
**代码量**：~120 行 C 代码 + ~100 行 Python 代码

### Phase 4: 集成测试

1. 编写完整 printer.cfg
2. 测试所有功能
3. 编写 GCode 宏示例

---

## 风险与注意事项

### 内存预算
- 当前 Flash: ~5678B (17.6%)，RAM: 497B (24.3%)
- TM1637 驱动：~300B Flash, ~0B RAM（无状态）
- 蜂鸣器驱动：~100B Flash, ~0B RAM
- **预计总增加**：~400B Flash, ~0B RAM
- **安全余量充足**

### 时序约束
- TM1637 需要精确的 μs 级时序
- AVR 16MHz 下一个 nop = 62.5ns，16 个 nop ≈ 1μs
- UART ISR 可能干扰时序（~30μs），但 TM1637 不需要连续时钟
- **解决方案**：在 TM1637 传输期间临时禁用 UART 中断

### 引脚冲突
- LED/按键共用引脚（A1-A3）
- **解决方案**：移除跳线帽，或在配置中说明

### Arduino 兼容性
- 使用 `digitalWrite()` 还是直接操作寄存器？
- 直接操作寄存器更快，但 GPIO 层已经有 Arduino 兼容
- **推荐**：TM1637 用直接寄存器操作（需要精确时序），其他用 Arduino API

---

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/arduino/tm1637.c` | 新增 | TM1637 MCU 驱动 |
| `src/arduino/buzzer.c` | 新增 | 蜂鸣器 tone 命令 |
| `registrations.c` | 修改 | 注册新命令 |
| `src/compile_time_request.c` | 修改 | 添加新命令到索引 |
| `/home/mellow/klipper/klippy/extras/mfs.py` | 新增 | Host 端 MFS 模块 |
| `printer_mfs.cfg` | 新增 | 完整 MFS 配置示例 |

---

## 验证计划

### LED 测试
```
SET_PIN PIN=led_d1 VALUE=1   # 开灯
SET_PIN PIN=led_d1 VALUE=0   # 关灯
SET_PIN PIN=led_d2 VALUE=1
SET_PIN PIN=led_d3 VALUE=1
SET_PIN PIN=led_d4 VALUE=1
```

### 按键测试
```
# 按下 S1，观察日志输出
# 按下 S2，观察日志输出
# 按下 S3，观察日志输出
```

### 蜂鸣器测试
```
MFS_BEEP FREQUENCY=1000 DURATION=200
MFS_BEEP FREQUENCY=2000 DURATION=200
MFS_BEEP FREQUENCY=3000 DURATION=200
```

### 数码管测试
```
MFS_DISPLAY TEXT=1234
MFS_DISPLAY TEXT=56.78
MFS_DISPLAY TEXT=AbCd
MFS_CLEAR
```

### 综合测试 GCode 宏
```ini
[gcode_macro MFS_TEST]
gcode:
  SET_PIN PIN=led_d1 VALUE=1
  MFS_BEEP FREQUENCY=1000 DURATION=100
  MFS_DISPLAY TEXT=Hi
  G4 P500
  SET_PIN PIN=led_d1 VALUE=0
  MFS_DISPLAY TEXT=----  
```
