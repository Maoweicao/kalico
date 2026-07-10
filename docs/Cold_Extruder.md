# Cold Extruder (No Heater)

The cold extruder configuration allows using extruders without heaters for materials that don't require heating, such as:

- Clay
- Concrete
- Food paste
- Silicone
- Other cold-extrusion materials

## Configuration

### Basic Usage

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
#   Set to true to configure this as a cold extruder without a heater.
#   The default is false.
sensor_type: dummy_thermistor
#   Use a dummy thermistor since no real sensor is needed.
temperature: 25.0
#   Room temperature or any fixed value.
```

### Full Example: Clay Printer

```
[printer]
kinematics: cartesian
max_velocity: 100
max_accel: 500

[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 50.0
max_extrude_only_distance: 100.0
max_extrude_only_velocity: 10
max_extrude_only_accel: 50
step_pin: PC1
dir_pin: PC0
rotation_distance: 28.0

[stepper_x]
step_pin: PA0
dir_pin: PA1
endstop_pin: PA2
position_endstop: 0
position_max: 200

[stepper_y]
step_pin: PB0
dir_pin: PB1
endstop_pin: PB2
position_endstop: 0
position_max: 200

[stepper_z]
step_pin: PC0
dir_pin: PC1
endstop_pin: PC2
position_endstop: 0
position_max: 200
```

### Multiple Cold Extruders

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
step_pin: PC1
dir_pin: PC0
rotation_distance: 28.0

[extruder1]
nozzle_diameter: 3.0
filament_diameter: 15.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
step_pin: PD1
dir_pin: PD0
rotation_distance: 35.0
```

## Configuration Options

When `no_heater: true` is set:

- No `heater_pin` is required
- No temperature control (PID, bang-bang, etc.) is configured
- `min_extrude_temp` is automatically set to 0
- The extruder can extrude at any temperature
- A temperature sensor is still recommended for compatibility

### Recommended Settings for Cold Materials

| Parameter | Clay | Concrete | Food Paste |
|-----------|------|----------|------------|
| nozzle_diameter | 1.0-2.0mm | 3.0-5.0mm | 0.8-1.5mm |
| filament_diameter | 5-15mm | 10-20mm | 3-5mm |
| max_extrude_only_velocity | 5-15 mm/s | 2-5 mm/s | 10-20 mm/s |
| max_extrude_only_accel | 25-100 mm/s² | 10-50 mm/s² | 50-200 mm/s² |

## G-code Compatibility

Cold extruders maintain full G-code compatibility:

- `M104 S0` - Succeeds without action
- `M109 S0` - Succeeds without waiting
- `M302` - Reports cold extrusion enabled
- `G1 E10` - Extrudes material

## Use Cases

### 1. Clay Printing

Clay printers use large nozzles (1-3mm) and extrude at slow speeds. The material is typically loaded into a syringe or cartridge.

```
[extruder]
nozzle_diameter: 2.0
filament_diameter: 20.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 100.0
max_extrude_only_distance: 200.0
max_extrude_only_velocity: 5
max_extrude_only_accel: 25
```

### 2. Food Printing

Food printers extrude chocolate, dough, or other food materials. Temperature control may be handled separately (e.g., chocolate tempering).

```
[extruder]
nozzle_diameter: 0.8
filament_diameter: 5.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 22.0
max_extrude_cross_section: 20.0
max_extrude_only_velocity: 15
max_extrude_only_accel: 100
```

### 3. Concrete/Construction Printing

Large-scale construction printers extrude concrete mixtures. Flow control is critical.

```
[extruder]
nozzle_diameter: 10.0
filament_diameter: 50.0
no_heater: true
sensor_type: dummy_thermistor
temperature: 25.0
max_extrude_cross_section: 500.0
max_extrude_only_distance: 500.0
max_extrude_only_velocity: 2
max_extrude_only_accel: 10
```

## Troubleshooting

### "Extrude below minimum temp" Error

If you see this error, ensure:
1. `no_heater: true` is set in the extruder section
2. A dummy thermistor is configured (or any sensor_type)

### Slicer Temperature Commands

Most slicers send `M104` and `M109` commands. With a cold extruder:
- `M104 S200` will succeed without heating
- `M109 S200` will succeed without waiting

### Flow Control

For viscous materials, consider:
- Increasing `max_extrude_only_distance`
- Decreasing `max_extrude_only_velocity`
- Using larger `nozzle_diameter`

## See Also

- [Extruder Configuration](Config_Reference.md#extruder)
- [Dummy Thermistor](Dummy_Thermistor.md)
- [G-code Commands](G-Codes.md)
