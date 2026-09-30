# 喷嘴与耗材直径命令

## 概述

允许在运行时调整喷嘴直径和耗材直径，无需修改 `printer.cfg`。更改在重启后持久化（通过 `SAVE_CONFIG` 保存）。

## G-code 命令

### SET_NOZZLE_DIAMETER

设置活动挤出机的喷嘴直径。

```
SET_NOZZLE_DIAMETER DIAMETER=<mm>
```

| 参数 | 类型 | 说明 |
|-----------|------|------|
| `DIAMETER` | float | 喷嘴直径（mm），必须>0 |

**示例：**
```
SET_NOZZLE_DIAMETER DIAMETER=0.4
```

### SET_FILAMENT_DIAMETER

设置活动挤出机的耗材直径。

```
SET_FILAMENT_DIAMETER DIAMETER=<mm>
```

| 参数 | 类型 | 说明 |
|-----------|------|------|
| `DIAMETER` | float | 耗材直径（mm），必须>喷嘴直径 |

**示例：**
```
SET_FILAMENT_DIAMETER DIAMETER=1.75
```

## 影响

这些命令调整：

- `nozzle_diameter` — 影响体积流量计算和碰撞检测
- `filament_area` — 计算为 `π ×（直径/2)²`
- `max_extrude_ratio` — 基于新值重新计算：`4 × 喷嘴直径² / 耗材面积`

## 安全

- 耗材直径必须**大于**喷嘴直径（否则报错）。
- 如果耗材直径等于喷嘴直径，最大挤出比恰好为4，这意味着挤出机最多能推动等于喷嘴面积的耗材量。这对大多数打印机来说在物理上不现实，因此挤出机会拒绝大的移动。

## 持久化存储

使用任一命令后，必须调用 `SAVE_CONFIG` 将更改持久化到 `printer.cfg`。打印机将以新值重启。