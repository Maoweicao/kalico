# Kalico CLI Reference for AI Assistants

This document provides a comprehensive reference for the Kalico CLI tool, specifically designed for AI assistants to understand and interact with Kalico 3D printer firmware.

## Overview

Kalico provides a unified CLI interface (`kalico`) for managing 3D printer firmware, MCU devices, and system configuration. All commands support JSON output for programmatic access.

## Command Structure

```
kalico <command> [subcommand] [options]
```

## Global Options

| Option | Description |
|--------|-------------|
| `-v, --verbose` | Enable verbose output |
| `--json` | Output in JSON format |
| `--version` | Show version information |
| `-h, --help` | Show help message |

## Commands

### 1. MCU Management (`kalico mcu`)

#### List Connected MCUs

```bash
kalico mcu list [--transport serial|can|tcp|udp|all] [--scan-network] [--json]
```

**Purpose**: Enumerate all connected MCU devices across different transport protocols.

**Options**:
- `--transport`: Filter by transport type (default: all)
- `--scan-network`: Include network scan for TCP/UDP devices
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
[
  {
    "type": "serial",
    "path": "/dev/ttyUSB0",
    "description": "CH340 USB-Serial",
    "is_kalico": true,
    "vid": 6790,
    "pid": 29987,
    "serial_number": "A123456"
  }
]
```

**AI Use Cases**:
- Discover available MCU devices before configuration
- Validate device connectivity
- Generate configuration suggestions

#### Check MCU Configuration

```bash
kalico mcu check [--fix] [--config PATH] [--json]
```

**Purpose**: Validate MCU configuration against actual devices.

**Options**:
- `--fix`: Interactive configuration fix wizard
- `--config PATH`: Path to printer.cfg
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
[
  {
    "mcu": "main",
    "transport": "serial",
    "matched": true,
    "responsive": true,
    "firmware": "Detected (Kalico protocol)",
    "issues": [],
    "suggestions": []
  }
]
```

**AI Use Cases**:
- Diagnose configuration issues
- Suggest configuration fixes
- Validate firmware connectivity

### 2. Configuration Management (`kalico config`)

#### Show Configuration Location

```bash
kalico config show [--config PATH] [--json]
```

**Purpose**: Display the location and details of the configuration file.

**Options**:
- `--config PATH`: Specify custom config path
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
{
  "path": "/home/user/printer_data/config/printer.cfg",
  "absolute_path": "/home/user/printer_data/config/printer.cfg",
  "size": 4096,
  "modified": 1717234567.0
}
```

**AI Use Cases**:
- Locate configuration file for reading/editing
- Check configuration file status
- Validate file permissions

#### Validate Configuration

```bash
kalico config validate [--config PATH] [--json]
```

**Purpose**: Validate configuration file syntax and structure.

**Options**:
- `--config PATH`: Specify custom config path
- `--json`: Output as JSON

**AI Use Cases**:
- Check configuration before applying
- Validate syntax changes
- Ensure configuration integrity

### 3. System Diagnostics (`kalico doctor`)

#### Run Diagnostics

```bash
kalico doctor [--fix] [--dry-fix] [--config PATH] [--network] [--json]
```

**Purpose**: Comprehensive system diagnostics and auto-repair.

**Options**:
- `--fix`: Auto-fix fixable issues
- `--dry-fix`: Preview fixes without applying
- `--config PATH`: Path to printer.cfg
- `--network`: Scan network for devices
- `--json`: Output as JSON
- `--skip-env`: Skip environment checks
- `--skip-config`: Skip config checks
- `--skip-mcu`: Skip MCU checks
- `--skip-service`: Skip service checks

**AI Use Cases**:
- Comprehensive system health check
- Automated issue resolution
- Environment validation

### 4. CAN Bus Management (`kalico can`)

#### Scan CAN Bus

```bash
kalico can scan [--interface can0 can1] [--timeout 2.0] [--json]
```

**Purpose**: Scan CAN bus for connected devices.

**Options**:
- `--interface`: CAN interface(s) to scan
- `--timeout`: Scan timeout in seconds (default: 2.0)
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
{
  "can0": [
    {
      "uuid": 1234567890,
      "app_name": "Kalico",
      "app_id": 7,
      "node_id": 1,
      "status": "Assigned",
      "interface": "can0"
    }
  ]
}
```

**AI Use Cases**:
- Discover CAN devices
- Validate CAN configuration
- Diagnose CAN connectivity issues

#### Show CAN Interface Info

```bash
kalico can info [--interface can0 can1] [--json]
```

**Purpose**: Display CAN interface status and statistics.

**Options**:
- `--interface`: CAN interface(s) to query
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
[
  {
    "name": "can0",
    "state": "UP",
    "bitrate": 500000,
    "can_state": "ACTIVE",
    "stats": {
      "rx_errors": 0,
      "tx_errors": 0,
      "rx_over_errors": 0,
      "tx_dropped": 0
    }
  }
]
```

**AI Use Cases**:
- Monitor CAN bus health
- Diagnose CAN errors
- Validate CAN configuration

### 5. Version Information (`kalico version`)

```bash
kalico version [--json]
```

**Purpose**: Display version and system information.

**Options**:
- `--json`: Output as JSON

**Example Output (JSON)**:
```json
{
  "app_name": "Kalico",
  "cli_version": "0.1.0",
  "git_version": "v0.12.1-123-gabcdef",
  "git_branch": "main",
  "git_remote": "origin",
  "git_url": "https://github.com/KalicoCrew/kalico.git",
  "python_version": "3.12.0",
  "platform": "Linux-6.1.0-x86_64",
  "architecture": "x86_64"
}
```

## Common Workflows

### Workflow 1: Initial Setup Validation

```bash
# 1. Check version and environment
kalico version --json

# 2. Locate configuration
kalico config show --json

# 3. Validate configuration
kalico config validate --json

# 4. List connected MCUs
kalico mcu list --json

# 5. Run comprehensive diagnostics
kalico doctor --json
```

### Workflow 2: MCU Configuration Fix

```bash
# 1. Check MCU configuration
kalico mcu check --json

# 2. If issues found, run fix
kalico mcu check --fix

# 3. Validate changes
kalico config validate --json
```

### Workflow 3: CAN Bus Troubleshooting

```bash
# 1. Check CAN interface status
kalico can info --json

# 2. Scan for devices
kalico can scan --json

# 3. Validate configuration
kalico mcu check --json
```

## Error Handling

All commands return appropriate exit codes:
- `0`: Success
- `1`: General error
- `2`: Configuration error
- `130`: User cancellation (Ctrl+C)

## JSON Output Format

When using `--json`, output follows this structure:

```json
{
  "command": "mcu list",
  "timestamp": "2026-05-31T12:00:00Z",
  "success": true,
  "data": [...],
  "errors": [],
  "warnings": []
}
```

## AI Integration Tips

1. **Always use `--json`** for programmatic access
2. **Check exit codes** for operation success
3. **Parse error messages** for user feedback
4. **Use verbose mode** for debugging
5. **Chain commands** for complex workflows

## Configuration File Locations

Default search paths for `printer.cfg`:
1. `~/printer_data/config/printer.cfg`
2. `~/klipper_config/printer.cfg`
3. `~/.config/klipper/printer.cfg`
4. `/etc/klipper/printer.cfg`
5. `./printer.cfg` (current directory)

## Transport Types

| Transport | Description | Configuration |
|-----------|-------------|---------------|
| `serial` | USB/Serial connection | `serial: /dev/ttyUSB0` |
| `can` | CAN bus connection | `canbus_uuid: <uuid>` |
| `tcp` | TCP network connection | `tcp_host: <ip>` |
| `udp` | UDP network connection | `udp_host: <ip>` |

## Status Codes

### MCU Status
- `OK`: MCU connected and responding
- `WARNING`: MCU found but not responding to protocol
- `ERROR`: MCU not found or configuration mismatch

### CAN Device Status
- `Assigned`: Device has a node ID assigned
- `Unassigned`: Device needs node ID assignment
- `Unknown`: Status cannot be determined

## Examples for AI Assistants

### Example 1: Discover and Configure MCU

```python
import subprocess
import json

# List available MCUs
result = subprocess.run(['kalico', 'mcu', 'list', '--json'], capture_output=True, text=True)
mcus = json.loads(result.stdout)

# Check configuration
result = subprocess.run(['kalico', 'mcu', 'check', '--json'], capture_output=True, text=True)
checks = json.loads(result.stdout)

# Suggest fixes based on issues
for check in checks:
    if check['issues']:
        print(f"Issues with {check['mcu']}:")
        for issue in check['issues']:
            print(f"  - {issue}")
```

### Example 2: Validate Configuration

```python
import subprocess
import json

# Get config location
result = subprocess.run(['kalico', 'config', 'show', '--json'], capture_output=True, text=True)
config_info = json.loads(result.stdout)

# Validate config
result = subprocess.run(['kalico', 'config', 'validate', '--json'], capture_output=True, text=True)
validation = json.loads(result.stdout)

if validation.get('success'):
    print("Configuration is valid")
else:
    print(f"Configuration error: {validation.get('error')}")
```

### Example 3: CAN Bus Diagnostics

```python
import subprocess
import json

# Scan CAN bus
result = subprocess.run(['kalico', 'can', 'scan', '--json'], capture_output=True, text=True)
devices = json.loads(result.stdout)

# Check interface status
result = subprocess.run(['kalico', 'can', 'info', '--json'], capture_output=True, text=True)
interfaces = json.loads(result.stdout)

# Report status
for iface in interfaces:
    print(f"{iface['name']}: {iface['state']}, {iface['bitrate']} bps")
```

## See Also

- [Kalico Documentation](https://docs.kalico.gg/)
- [Configuration Reference](https://docs.kalico.gg/Configuration.html)
- [MCU Commands](https://docs.kalico.gg/MCU_Commands.html)
