# Non-Fatal Error Handling

## Overview

Normally, certain errors (ADC out of range, heater faults) cause an immediate MCU shutdown, which aborts the print. This feature converts these errors into non-fatal errors that **pause** the print instead of shutting down, allowing recovery.

## How It Works

When a non-fatal error occurs while printing:

1. The MCU sends a `non_fatal_error` response (instead of `shutdown`)
2. Klipper pauses the print and issues `PAUSE`
3. The user can diagnose the issue, fix it, then `RESUME`

## Affected Errors

| Error | Old Behavior | New Behavior |
|-------|-------------|--------------|
| ADC out of range | MCU shutdown | Non-fatal error + pause |
| Heater fault (while printing) | MCU shutdown | Non-fatal error + pause |

## Status

This feature is always active when printing. No configuration is required. The `is_printing()`, `is_paused()`, `is_cancelled()`, and `is_complete()` methods on the Printer object provide the state queries used by all modules.

## Important Notes

- **Heater safety is preserved**: The heater will still shut down if it exceeds the `max_delta` safety margin. Only *intermittent* faults (e.g., brief sensor glitches) are converted to non-fatal errors. Sustained faults still trigger shutdown.
- **ADC errors**: An ADC reading outside the configured valid range triggers a non-fatal error, allowing you to check the wiring without losing the print.
- **Not available during homing**: During homing moves, errors remain fatal (shutdown) for safety.