# Kalico Fly Features / Kalico Fly 功能集

Features ported from [Fly-klipper](https://github.com/FLY-maker/FLY-Klipper) into Kalico, with enhancements and Chinese/English bilingual documentation.

从 [Fly-klipper](https://github.com/FLY-maker/FLY-Klipper) 移植到 Kalico 的功能，包含增强和中英文双语文档。

---

## Implemented Features / 已实现功能

### Core Features / 核心功能

| Feature | Description | 文档 |
|---------|-------------|------|
| **Power Loss Resume** / 断电续打 | Auto-save state on power loss, resume on restart | [power_loss_resume.md](power_loss_resume.md) |
| **Filament Blockage Detection** / 耗材堵塞检测 | MCU-level runout/slip/blockage detection | [filament_blockage_detection.md](filament_blockage_detection.md) |
| **Non-Fatal Error Handling** / 非致命错误处理 | Pause instead of shutdown on ADC/heater errors | [non_fatal_errors.md](non_fatal_errors.md) |

### User-Level Features / 用户级功能

| Feature | Description | 文档 |
|---------|-------------|------|
| **Nozzle/Filament Diameter** / 喷嘴与耗材直径 | Runtime diameter adjustment via G-code | [nozzle_filament_diameter.md](nozzle_filament_diameter.md) |
| **LDC1612 Frequency Config** / LDC1612频率配置 | External crystal frequency and auto-divider | [ldc1612_frequency.md](ldc1612_frequency.md) |
| **From-Height Print** / 从指定高度打印 | Resume print from a specific Z height | [from_height_print.md](from_height_print.md) |

---

## Quick Start / 快速入门

### Power Loss Resume / 断电续打

1. Add to `printer.cfg`:
   ```ini
   [power_loss_resume]
   ```

2. Test with `ENABLE_POWER_LOSS_RESUME`, then `STATUS_POWER_LOSS_RESUME`

3. On power loss, the state is saved automatically. On restart, `SAVE_RESTART gcode` is issued to resume.

添加到 `printer.cfg`：
```ini
[power_loss_resume]
```

用 `ENABLE_POWER_LOSS_RESUME` 和 `STATUS_POWER_LOSS_RESUME` 测试。断电时自动保存状态。重启后自动发出 `SAVE_RESTART gcode` 续打。

### Filament Blockage Detection / 耗材堵塞检测

1. Wire an encoder to your MCU GPIO
2. Add to `printer.cfg`:
   ```ini
   [filament_blockage_sensor my_sensor]
   encoder_pin: ^PA7
   ```
3. Run `CALIBRATE_FILAMENT_BLOCKAGE` after loading filament
4. Enable with `ENABLE_FILAMENT_BLOCKAGE`

将编码器连接到MCU GPIO。添加配置。加载耗材后运行校准。启用传感器。

### Nozzle/Filament Diameter / 喷嘴与耗材直径

```
SET_NOZZLE_DIAMETER DIAMETER=0.4
SET_FILAMENT_DIAMETER DIAMETER=1.75
SAVE_CONFIG
```

---

## Files Modified / 修改的文件

| File | Changes | 变更 |
|------|---------|------|
| `klippy/extras/power_loss_resume.py` | **NEW** — Power loss resume module | 断电续打模块 |
| `klippy/extras/virtual_sdcard.py` | Power loss hooks, layer change tracking | 断电续打钩子、层变更追踪 |
| `klippy/extras/filament_blockage_detection.py` | **NEW** — Filament blockage sensor | 耗材堵塞传感器 |
| `src/filament_blockage_detection.c` | **NEW** — MCU firmware for blockage detection | 堵塞检测MCU固件 |
| `src/Kconfig` | Added `WANT_FILAMENT_BLOCKAGE` | 添加堵塞检测配置 |
| `src/Makefile` | Added `filament_blockage_detection.c` | 添加源文件编译 |
| `klippy/printer.py` | Print state queries, non-fatal error methods | 打印状态查询、非致命错误方法 |
| `klippy/mcu.py` | `non_fatal_error` response handler | 非致命错误响应处理 |
| `src/adccmds.c` | Non-fatal ADC error on out-of-range | ADC超范围非致命错误 |
| `klippy/extras/verify_heater.py` | Pause on fault if printing | 打印时故障暂停 |
| `klippy/extras/heaters.py` | `is_wait` flag for temperature wait | 温度等待标志 |
| `klippy/kinematics/extruder.py` | `SET_NOZZLE_DIAMETER`, `SET_FILAMENT_DIAMETER` commands | 喷嘴/耗材直径命令 |
| `klippy/extras/ldc1612.py` | `max_sensor_hz` config, dynamic divider | 最大传感器频率配置、动态分频 |
| `klippy/extras/virtual_sdcard.py` | From-Height Print webhook + parsers | 从指定高度打印webhook+解析器 |

---

## Pending Features / 待实现功能

| Feature | Description | 文档 |
|---------|-------------|------|
| **Multi-threaded Steppersync** / 多线程步进同步 | Parallel step generation for faster MCU communication | — |
| **Trigger Analog Framework** / 模拟传感器触发框架 | Generic analog sensor trigger support | — |
| **Kin Generic** / 通用笛卡尔运动学 | Universal Cartesian kinematics for any kinematic chain | — |
| **Per-Move PA** / 每步进压力提前 | Per-move pressure advance (beyond dynamic PA) | — |
| **4096 Step Buffer** / 4096步进缓冲区 | Expanded step buffer for complex moves | — |
| **25-Pulse Input Shaping** / 25脉冲输入整形 | Extended input shaper pulse count | — |
| **Timer Retry** / 定时器重试 | Handle timer-too-near errors gracefully | — |
| **BMI160 Accelerometer** / BMI160加速度计 | BMI160 accelerometer support | — |
| **TCP API Server** / TCP端口API | External API server via TCP socket | — |
| **Enhanced Logging** / 增强日志 | Colored output, formatted timestamps | — |
| **MCU Startup GPIO** / MCU启动GPIO | Configure GPIO state on MCU startup | — |
| **.pyc/.so Loading** / .pyc/.so加载 | Native Python module loading for faster startup | — |

---

## Notes / 注意事项

- All features are designed to work with kalico's existing architecture
- No breaking changes to existing configurations
- BTT Eddy and standard sensor configurations remain unchanged
- All new features can be disabled by simply not adding their config sections

所有功能均设计为与kalico现有架构兼容。不对现有配置进行破坏性更改。BTT Eddy和标准传感器配置保持不变。所有新功能可通过不添加其配置段来禁用。
