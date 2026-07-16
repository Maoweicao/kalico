# Non-Fatal Error Handling / 非致命错误处理

## Overview / 概述

Normally, certain errors (ADC out of range, heater faults) cause an immediate MCU shutdown, which aborts the print. This feature converts these errors into non-fatal errors that **pause** the print instead of shutting down, allowing recovery.

正常情况下，某些错误（ADC超范围、加热器故障）会导致MCU立即关机，从而中止打印。此功能将这些错误转换为非致命错误，**暂停**打印而非关机，允许恢复。

## How It Works / 工作原理

When a non-fatal error occurs while printing:

1. The MCU sends a `non_fatal_error` response (instead of `shutdown`)
2. Klipper pauses the print and issues `PAUSE`
3. The user can diagnose the issue, fix it, then `RESUME`

当打印过程中发生非致命错误时：

1. MCU发送 `non_fatal_error` 响应（而非 `shutdown`）
2. Klipper暂停打印并发出 `PAUSE`
3. 用户可以诊断问题、修复，然后 `RESUME`

## Affected Errors / 受影响的错误

| Error | Old Behavior | New Behavior | 旧行为 | 新行为 |
|-------|-------------|--------------|--------|--------|
| ADC out of range | MCU shutdown | Non-fatal error + pause | MCU关机 | 非致命错误+暂停 |
| Heater fault (while printing) | MCU shutdown | Non-fatal error + pause | MCU关机 | 非致命错误+暂停 |

## Status / 状态

This feature is always active when printing. No configuration is required. The `is_printing()`, `is_paused()`, `is_cancelled()`, and `is_complete()` methods on the Printer object provide state queries used by all modules.

此功能在打印时始终活动，无需配置。Printer对象上的 `is_printing()`、`is_paused()`、`is_cancelled()` 和 `is_complete()` 方法提供所有模块使用的状态查询。

## Important Notes / 重要说明

- **Heater safety is preserved**: The heater will still shut down if it exceeds the `max_delta` safety margin. Only *intermittent* faults (e.g., brief sensor glitches) are converted to non-fatal errors. Sustained faults still trigger shutdown.
- **ADC errors**: An ADC reading outside the configured valid range triggers a non-fatal error, allowing you to check wiring without losing the print.
- **Not available during homing**: During homing moves, errors remain fatal (shutdown) for safety.

- **加热器安全得到保留**：如果加热器超过 `max_delta` 安全余量，仍会关闭。只有*间歇性*故障（如短暂的传感器毛刺）会转换为非致命错误。持续故障仍会触发关机。
- **ADC错误**：ADC读数超出配置的有效范围会触发非致命错误，允许您检查接线而不丢失打印。
- **归位期间不可用**：归位移动期间，出于安全考虑，错误仍为致命错误（关机）。
