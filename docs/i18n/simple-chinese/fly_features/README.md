# Kalico Fly 功能集

从 [Fly-klipper](https://github.com/FLY-maker/FLY-Klipper) 移植到 Kalico 的功能，包含增强和中英文双语文档。

---

## 已实现功能

### 核心功能

| 功能 | 说明 | 文档 |
|---------|-------------|------|
| **断电续打** | 断电时自动保存状态，重启后续打 | [power_loss_resume.md](power_loss_resume.md) |
| **耗材堵塞检测** | MCU级断料/打滑/堵塞检测 | [filament_blockage_detection.md](filament_blockage_detection.md) |
| **非致命错误处理** | ADC/加热器错误时暂停而非关机 | [non_fatal_errors.md](non_fatal_errors.md) |

### 用户级功能

| 功能 | 说明 | 文档 |
|---------|-------------|------|
| **喷嘴/耗材直径** | 通过G-code在运行时调整直径 | [nozzle_filament_diameter.md](nozzle_filament_diameter.md) |
| **LDC1612频率配置** | 外部晶振频率和自动分频器 | [ldc1612_frequency.md](ldc1612_frequency.md) |
| **从指定高度打印** | 从指定Z高度恢复打印 | [from_height_print.md](from_height_print.md) |
| **BMI160加速度计** | BMI160加速度计支持（SPI或I2C） | [Config_Reference](../Config_Reference.md#bmi160) |

---

## 快速入门

### 断电续打

1. 添加到 `printer.cfg`：
   ```ini
   [power_loss_resume]
   ```
2. 用 `ENABLE_POWER_LOSS_RESUME`，然后 `STATUS_POWER_LOSS_RESUME` 测试
3. 断电时自动保存状态。重启后自动发出 `SAVE_RESTART gcode` 续打。

### 耗材堵塞检测

1. 将编码器连接到MCU GPIO
2. 添加到 `printer.cfg`：
   ```ini
   [filament_blockage_sensor my_sensor]
   encoder_pin: ^PA7
   ```
3. 加载耗材后运行 `CALIBRATE_FILAMENT_BLOCKAGE`
4. 用 `ENABLE_FILAMENT_BLOCKAGE` 启用

### 喷嘴/耗材直径

```
SET_NOZZLE_DIAMETER DIAMETER=0.4
SET_FILAMENT_DIAMETER DIAMETER=1.75
SAVE_CONFIG
```

---

## 修改的文件

| 文件 | 变更 |
|------|---------|
| `klippy/extras/power_loss_resume.py` | **新增** — 断电续打模块 |
| `klippy/extras/virtual_sdcard.py` | 断电续打钩子、层变更追踪 |
| `klippy/extras/filament_blockage_detection.py` | **新增** — 耗材堵塞传感器 |
| `src/filament_blockage_detection.c` | **新增** — 堵塞检测MCU固件 |
| `src/Kconfig` | 添加 `WANT_FILAMENT_BLOCKAGE` |
| `src/Makefile` | 添加 `filament_blockage_detection.c` |
| `klippy/printer.py` | 打印状态查询、非致命错误方法 |
| `klippy/mcu.py` | `non_fatal_error` 响应处理 |
| `src/adccmds.c` | ADC超范围非致命错误 |
| `klippy/extras/verify_heater.py` | 打印时故障暂停 |
| `klippy/extras/heaters.py` | 温度等待 `is_wait` 标志 |
| `klippy/kinematics/extruder.py` | `SET_NOZZLE_DIAMETER`、`SET_FILAMENT_DIAMETER` 命令 |
| `klippy/extras/ldc1612.py` | `max_sensor_hz` 配置、动态分频 |
| `klippy/extras/virtual_sdcard.py` | 从指定高度打印webhook+解析器 |

---

## 待实现功能

| 功能 | 说明 |
|---------|-------------|
| **多线程步进同步** | 并行步进生成，加快MCU通信 |
| **模拟传感器触发框架** | 通用模拟传感器触发支持 |
| **通用笛卡尔运动学** | 适用于任何运动链的通用笛卡尔运动学 |
| **每步进压力提前** | 每步进压力提前（超越动态PA） |
| **4096步进缓冲区** | 扩展步进缓冲区，处理复杂移动 |
| **25脉冲输入整形** | 扩展输入整形器脉冲计数 |
| **定时器重试** | 优雅处理定时器过近错误 |
| **TCP端口API** | 通过TCP套接字的外部API服务器 |
| **增强日志** | 彩色输出、格式化时间戳 |
| **MCU启动GPIO** | 在MCU启动时配置GPIO状态 |
| **.pyc/.so加载** | 原生Python模块加载，加快启动 |

---

## 注意事项

- 所有功能均设计为与Kalico现有架构兼容
- 不对现有配置进行破坏性更改
- BTT Eddy和标准传感器配置保持不变
- 所有新功能可通过不添加其配置段来禁用