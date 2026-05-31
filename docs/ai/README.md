# Kalico AI Documentation

This directory contains documentation specifically designed for AI assistants working with Kalico 3D printer firmware.

## Contents

### [CLI Reference](CLI_REFERENCE.md)
Comprehensive reference for all Kalico CLI commands, including:
- Command syntax and options
- JSON output formats
- Error handling
- Common workflows
- AI integration tips

### [Quick Reference](AI_QUICK_REFERENCE.md)
Quick reference card with:
- Essential commands
- Command cheat sheet
- Status codes
- Configuration locations

## Getting Started

### Installation

The CLI is included with Kalico. Install Kalico and the CLI will be available:

```bash
pip install -e .
```

### Basic Usage

```bash
# Show help
kalico --help

# Show version
kalico version

# List connected MCUs
kalico mcu list

# Run diagnostics
kalico doctor
```

### JSON Output

All commands support JSON output for programmatic access:

```bash
kalico mcu list --json
kalico config show --json
kalico doctor --json
```

## AI Integration

### For AI Assistants

When working with Kalico, AI assistants should:

1. **Use JSON output** for reliable data parsing
2. **Check exit codes** for operation success
3. **Validate configuration** before making changes
4. **Run diagnostics** to identify issues
5. **Use verbose mode** for debugging

### Example Workflow

```bash
# 1. Get system info
kalico version --json

# 2. Find configuration
kalico config show --json

# 3. Validate configuration
kalico config validate --json

# 4. Check MCU connectivity
kalico mcu check --json

# 5. Run full diagnostics
kalico doctor --json
```

## Command Categories

### MCU Management
- `kalico mcu list` - List connected MCUs
- `kalico mcu check` - Check MCU configuration

### Configuration
- `kalico config show` - Show config location
- `kalico config validate` - Validate configuration

### Diagnostics
- `kalico doctor` - Run system diagnostics

### CAN Bus
- `kalico can scan` - Scan CAN bus
- `kalico can info` - Show CAN interface info

### System
- `kalico version` - Show version info

## Support

- [Kalico Documentation](https://docs.kalico.gg/)
- [GitHub Issues](https://github.com/KalicoCrew/kalico/issues)
- [Configuration Reference](https://docs.kalico.gg/Configuration.html)
