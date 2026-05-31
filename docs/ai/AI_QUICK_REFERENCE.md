# Kalico AI Quick Reference

## Essential Commands

```bash
# List all connected MCUs
kalico mcu list --json

# Check MCU configuration
kalico mcu check --json

# Show config file location
kalico config show --json

# Run diagnostics
kalico doctor --json

# Scan CAN bus
kalico can scan --json

# Show version
kalico version --json
```

## Command Cheat Sheet

| Task | Command |
|------|---------|
| List MCUs | `kalico mcu list --json` |
| Check config | `kalico mcu check --json` |
| Find config | `kalico config show --json` |
| Validate config | `kalico config validate --json` |
| Full diagnostics | `kalico doctor --json` |
| Fix issues | `kalico doctor --fix --json` |
| CAN scan | `kalico can scan --json` |
| CAN status | `kalico can info --json` |
| Version info | `kalico version --json` |

## JSON Output Structure

All `--json` commands return:
```json
{
  "success": true,
  "data": [...],
  "errors": []
}
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 2 | Config error |
| 130 | User cancel |

## MCU Types

- `serial` - USB/Serial (`/dev/ttyUSB0`)
- `can` - CAN bus (`canbus_uuid`)
- `tcp` - TCP network (`tcp_host`)
- `udp` - UDP network (`udp_host`)

## Status Values

- `OK` - Working
- `WARNING` - Found but not responding
- `ERROR` - Not found

## CAN Status

- `Assigned` - Has node ID
- `Unassigned` - Needs assignment

## Config Locations

1. `~/printer_data/config/printer.cfg`
2. `~/klipper_config/printer.cfg`
3. `~/.config/klipper/printer.cfg`
4. `/etc/klipper/printer.cfg`
5. `./printer.cfg`

## Workflow Examples

### Setup Validation
```bash
kalico version --json
kalico config show --json
kalico config validate --json
kalico mcu list --json
kalico doctor --json
```

### Fix MCU Config
```bash
kalico mcu check --json
kalico mcu check --fix
kalico config validate --json
```

### CAN Troubleshooting
```bash
kalico can info --json
kalico can scan --json
kalico mcu check --json
```
