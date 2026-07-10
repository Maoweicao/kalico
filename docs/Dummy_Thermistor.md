# Dummy Thermistor

The dummy thermistor is a virtual temperature sensor that provides a fixed temperature reading without requiring a physical sensor. It is primarily used for:

- Testing and development without hardware
- Clay/concrete extruders that don't need temperature monitoring
- Debugging printer configurations

## Configuration

### Basic Usage

```
[temperature_sensor my_dummy_sensor]
sensor_type: dummy_thermistor
temperature: 25.0
#   The fixed temperature in Celsius to report. The default is 25.0.
#min_temp:
#max_temp:
#   See the "extruder" section for the definition of the above
#   parameters.
```

### Example: Cold Extruder for Clay

```
[extruder]
nozzle_diameter: 1.5
filament_diameter: 10.0
sensor_type: dummy_thermistor
temperature: 25.0
min_extrude_temp: 0
#   Set to 0 to allow cold extrusion
```

### Example: Testing Without Hardware

```
[extruder]
sensor_type: dummy_thermistor
temperature: 200.0
#   Simulates a hotend at 200°C

[heated_bed]
sensor_type: dummy_thermistor
temperature: 60.0
#   Simulates a heated bed at 60°C
```

## G-code Commands

### SET_DUMMY_TEMPERATURE

Set the temperature reported by a dummy thermistor at runtime.

```
SET_DUMMY_TEMPERATURE SENSOR=<name> [TEMPERATURE=<value>]
```

Parameters:
- `SENSOR`: Name of the dummy thermistor sensor (required)
- `TEMPERATURE`: New temperature value in Celsius (optional)

Examples:
```
# Set chamber sensor to 40°C
SET_DUMMY_TEMPERATURE SENSOR=chamber TEMPERATURE=40.0

# Query current temperature of mcu_temp sensor
SET_DUMMY_TEMPERATURE SENSOR=mcu_temp
```

## Use Cases

### 1. Development and Testing

When developing or testing printer configurations without physical hardware, dummy thermistors allow you to:

- Test G-code scripts that check temperature
- Verify heater control logic
- Run simulation without temperature errors

### 2. Cold Extrusion

For materials that don't require heating (clay, concrete, food paste), use a dummy thermistor to:

- Avoid "heater not configured" errors
- Maintain compatibility with slicers that expect temperature readings
- Allow M104/M109 commands to succeed without action

### 3. Temperature Monitoring Points

Create virtual temperature monitoring points for:

- Room temperature tracking
- Enclosure temperature simulation
- Debug temperature-dependent logic

## Technical Details

The dummy thermistor sensor:

- Reports a fixed temperature value (configurable)
- Updates at 1Hz (1 second intervals)
- Ignores min_temp/max_temp limits by default
- Can be dynamically updated via G-code
- Registers as a standard temperature sensor

## Comparison with Marlin

This implementation is similar to Marlin's dummy thermistor tables:

| Feature | Marlin | Kalico |
|---------|--------|--------|
| Sensor Type | Table 998 (25°C) / Table 999 (100°C) | `dummy_thermistor` |
| Fixed Temperature | Yes (via `DUMMY_THERMISTOR_*_VALUE`) | Yes (via `temperature` config) |
| Dynamic Update | No | Yes (via `SET_DUMMY_TEMPERATURE`) |
| Applicable Slots | All TEMP_SENSOR_* | Any sensor_type field |

## See Also

- [Temperature Sensors](Config_Reference.md#temperature-sensors)
- [Extruder Configuration](Config_Reference.md#extruder)
- [G-code Commands](G-Codes.md)
