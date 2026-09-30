# Kalico Fly Features

Features ported from [Fly-klipper](https://github.com/FLY-maker/FLY-Klipper) into Kalico, with enhancements and Chinese/English bilingual documentation.

---

## Implemented Features

### Core Features

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Power Loss Resume** | Auto-save state on power loss, resume on restart | [power_loss_resume.md](power_loss_resume.md) |
| **Filament Blockage Detection** | MCU-level runout/slip/blockage detection | [filament_blockage_detection.md](filament_blockage_detection.md) |
| **Non-Fatal Error Handling** | Pause instead of shutdown on ADC/heater errors | [non_fatal_errors.md](non_fatal_errors.md) |

### User-Level Features

| Feature | Description | Documentation |
|---------|-------------|---------------|
| **Nozzle/Filament Diameter** | Runtime diameter adjustment via G-code | [nozzle_filament_diameter.md](nozzle_filament_diameter.md) |
| **LDC1612 Frequency Config** | External crystal frequency and auto-divider | [ldc1612_frequency.md](ldc1612_frequency.md) |
| **From-Height Print** | Resume print from a specific Z height | [from_height_print.md](from_height_print.md) |
| **BMI160 Accelerometer** | BMI160 accelerometer support (SPI or I2C) | [Config_Reference](../Config_Reference.md#bmi160) |

---

## Quick Start

### Power Loss Resume

1. Add to `printer.cfg`:
   ```ini
   [power_loss_resume]
   ```
2. Test with `ENABLE_POWER_LOSS_RESUME`, then `STATUS_POWER_LOSS_RESUME`
3. On power loss, the state is saved automatically. On restart, `SAVE_RESTART gcode` is issued to resume.

### Filament Blockage Detection

1. Wire an encoder to your MCU GPIO
2. Add to `printer.cfg`:
   ```ini
   [filament_blockage_sensor my_sensor]
   encoder_pin: ^PA7
   ```
3. Run `CALIBRATE_FILAMENT_BLOCKAGE` after loading filament
4. Enable with `ENABLE_FILAMENT_BLOCKAGE`

### Nozzle/Filament Diameter

```
SET_NOZZLE_DIAMETER DIAMETER=0.4
SET_FILAMENT_DIAMETER DIAMETER=1.75
SAVE_CONFIG
```

---

## Files Modified

| File | Changes |
|------|---------|
| `klippy/extras/power_loss_resume.py` | **NEW** — Power loss resume module |
| `klippy/extras/virtual_sdcard.py` | Power loss hooks, layer change tracking |
| `klippy/extras/filament_blockage_detection.py` | **NEW** — Filament blockage sensor |
| `src/filament_blockage_detection.c` | **NEW** — MCU firmware for blockage detection |
| `src/Kconfig` | Added `WANT_FILAMENT_BLOCKAGE` |
| `src/Makefile` | Added `filament_blockage_detection.c` |
| `klippy/printer.py` | Print state queries, non-fatal error methods |
| `klippy/mcu.py` | `non_fatal_error` response handler |
| `src/adccmds.c` | Non-fatal ADC error on out-of-range |
| `klippy/extras/verify_heater.py` | Pause on fault if printing |
| `klippy/extras/heaters.py` | `is_wait` flag for temperature wait |
| `klippy/kinematics/extruder.py` | `SET_NOZZLE_DIAMETER`, `SET_FILAMENT_DIAMETER` commands |
| `klippy/extras/ldc1612.py` | `max_sensor_hz` config, dynamic divider |
| `klippy/extras/virtual_sdcard.py` | From-Height Print webhook + parsers |

---

## Pending Features

| Feature | Description |
|---------|-------------|
| **Multi-threaded Steppersync** | Parallel step generation for faster MCU communication |
| **Trigger Analog Framework** | Generic analog sensor trigger support |
| **Kin Generic** | Universal Cartesian kinematics for any kinematic chain |
| **Per-Move PA** | Per-move pressure advance (beyond dynamic PA) |
| **4096 Step Buffer** | Expanded step buffer for complex moves |
| **25-Pulse Input Shaping** | Extended input shaper pulse count |
| **Timer Retry** | Handle timer-too-near errors gracefully |
| **TCP API Server** | External API server via TCP socket |
| **Enhanced Logging** | Colored output, formatted timestamps |
| **MCU Startup GPIO** | Configure GPIO state on MCU startup |
| **.pyc/.so Loading** | Native Python module loading for faster startup |

---

## Notes

- All features are designed to work with Kalico's existing architecture
- No breaking changes to existing configurations
- BTT Eddy and standard sensor configurations remain unchanged
- All new features can be disabled by simply not adding their config sections