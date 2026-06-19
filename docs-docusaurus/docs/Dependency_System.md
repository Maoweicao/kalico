# Dependency Auto-Disable System

Kalico provides a dependency tracking and auto-disable system that gracefully
handles stale references in configuration files. When enabled, objects that
reference non-existent or disabled dependent objects will be automatically
disabled with a warning instead of causing a configuration error.

## Overview

In a typical printer configuration, many sections depend on other sections:

| Dependent Object | Config Option | References |
|---|---|---|
| `[heater_fan]` | `heater:` | `PrinterHeaters` heatable objects |
| `[controller_fan]` | `heater:` / `stepper:` | Heaters and stepper enable lines |
| `[verify_heater]` | (auto-created per heater) | The parent `Heater` object |
| `[homing_heaters]` | `heaters:` / `steppers:` | Heaters and kinematic steppers |
| `[extruder_stepper]` | `extruder:` | `PrinterExtruder` objects |
| `[temperature_combined]` | `sensor_list:` | Any temperature-reporting sensor |
| `[tmcXXXX]` | (via section name) | The corresponding `[stepper]` section |
| `[belay]` | `extruder_stepper_name:` | An `[extruder_stepper]` section |

By default, if a referenced object is missing, Kalico raises a configuration
error and prevents the printer from starting. When `auto_disable_stale_refs`
is enabled, these missing dependencies cause the dependent object to be
automatically disabled with a warning, allowing the printer to start with
the remaining functional components.

## Configuration

Add these options to your `[danger_options]` section:

```
[danger_options]
auto_disable_stale_refs: True
dependency_report_format: both
```

### Options

| Option | Default | Description |
|---|---|---|
| `auto_disable_stale_refs` | `False` | Enable auto-disable of objects with stale dependencies |
| `dependency_report_format` | `none` | Report format: `none`, `tree`, `dot`, `both` |

When `auto_disable_stale_refs` is `True`, `dependency_report_format` defaults
to `tree`.

## Startup Report

When enabled, the system prints a dependency report at startup. Example:

```
=======================================================
DEPENDENCY DISABLE REPORT
=======================================================
The following objects were auto-disabled due to missing dependencies:
  [heater_fan case_fan] -> referenced 'heater extruder2' (heater) not found
  [controller_fan mcu_fan] -> referenced 'stepper stepper_z3' (stepper) not found
-------------------------------------------------------
DEPENDENCY TREE:
heater_bed (ACTIVE)
  verify_heater heater_bed (ACTIVE)
  heater_fan bed_fan (ACTIVE)
    heater extruder (ACTIVE)
extruder (ACTIVE)
  verify_heater extruder (ACTIVE)
  heater_fan hotend_fan (ACTIVE)
  temperature_fan part_cooling (ACTIVE)
  [DISABLED] heater_fan case_fan <- missing 'heater extruder2'
=======================================================
```

## DOT Graph Output

When `dependency_report_format` is set to `dot` or `both`, a Graphviz DOT file
is written alongside your config file (e.g., `printer_deps.dot`). This can be
rendered with:

```bash
dot -Tpng printer_deps.dot -o printer_deps.png
```

The graph shows:
- Solid black arrows: active dependencies
- Red arrows: stale/missing dependencies
- Pink nodes: referenced but non-existent objects

## Supported Dependency Types

| Type | Description | Modules |
|---|---|---|
| `heater` | Heater objects via `PrinterHeaters` | heater_fan, controller_fan, verify_heater, homing_heaters |
| `stepper` | Stepper objects via config section or kinematics | controller_fan, homing_heaters, tmc |
| `extruder` | `PrinterExtruder` objects | extruder_stepper, belay |
| `sensor` | Temperature-reporting objects | temperature_combined |
| `auto` | Auto-created dependencies | verify_heater (per heater) |
| `reference` | Generic object references | Any `lookup_object` call |

## Safety Notes

1. **Core objects are never auto-disabled.** Objects like `toolhead`, `gcode`,
   `heaters`, `mcu`, and `pins` are essential infrastructure. If these are
   missing, the printer cannot start regardless of this setting.

2. **Cascading disables.** If object A depends on B, and B is disabled due to
   a missing dependency C, then A is also disabled. The report shows the
   full chain.

3. **User configuration sections cannot be auto-created.** If you configure
   a `[heater_fan]` that references a heater that doesn't exist, the fan is
   disabled - not the heater. The missing heater must be configured separately.

4. **The system runs after all objects have been loaded.** The dependency
   report is printed after `klippy:ready`, so all objects have had a chance
   to register their dependencies.

## Use Cases

1. **Development/testing:** Enable the feature to quickly test new config
   sections without needing all dependencies configured.

2. **Modular configs:** Use `[include]` to share configs across printers.
   When a shared config includes sections that reference hardware not present
   on all printers, auto-disable prevents errors.

3. **Config migration:** When upgrading or changing hardware, auto-disable
   helps identify which sections depend on removed components.

4. **Debugging configuration issues:** The dependency tree report shows
   exactly which objects depend on which, making it easier to understand
   configuration relationships.
