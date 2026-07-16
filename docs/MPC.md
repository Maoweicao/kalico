# Model Predictive Control

Model Predictive Control (MPC) is an advanced temperature control method that offers an alternative to traditional PID control. MPC leverages a system model to simulate the temperature of the hotend and adjusts the heater power to align with the target temperature.  

Unlike reactive methods, MPC operates proactively, adjusting in anticipation of temperature fluctuations. It utilizes a model of the hotend, considering factors such as the thermal masses of the system, heater power, heat loss to ambient air and fans, and heat transfer into the filament. This model allows MPC to predict the amount of heat energy that will be dissipated from the hotend over a given duration, and it compensates for this by adjusting the heater power accordingly. As a result, MPC can accurately calculate the necessary heat energy input to maintain a steady temperature or to transition to a new temperature.

MPC offers several advantages over PID control:

- **Faster and more responsive temperature control:** MPC's proactive approach allows it to respond more quickly and accurately to changes in temperature from fans or flow rate changes. 
- **Broad functionality with single calibration:** Once calibrated, MPC functions effectively across a wide range of printing temperatures.  
- **Simplified calibration process:** MPC is easier to calibrate compared to traditional PID control. 
- **Compatibility with all hotend sensor types:** MPC works with all types of hotend sensors, including those that produce noisy temperature readings.
- **Versatility with heater types:** MPC performs well with standard cartridge heaters and PTC heaters.
- **Effective for high and low flow hotends:** Regardless of the flow rate of the hotend, MPC maintains effective temperature control.     

> [!CAUTION]
> This feature controls the portions of the 3D printer that can get very hot. All standard Kalico warnings apply. Please report all issues and bugs to [GitHub](https://github.com/KalicoCrew/kalico/issues) or [Discord](Contact.md#discord).

## MPC Material & Heater Calculator

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-tabs{display:flex;flex-wrap:wrap;background:var(--calc-tab-bg);border-bottom:1px solid var(--calc-border);padding:0;margin:0}.rd-calc-tab{padding:10px 16px;cursor:pointer;border:none;background:transparent;color:var(--calc-text-light);font-size:.85em;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;white-space:nowrap}.rd-calc-tab:hover{color:var(--calc-primary);background:rgba(230,126,34,.05)}.rd-calc-tab.active{color:var(--calc-primary);border-bottom-color:var(--calc-primary);background:var(--calc-bg)}.rd-calc-content{padding:20px}.rd-calc-panel{display:none}.rd-calc-panel.active{display:block}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-panel p.formula{background:var(--calc-result-bg);padding:8px 12px;border-radius:4px;font-family:monospace;font-size:.9em;color:var(--calc-text-light);margin:0 0 16px;border-left:3px solid var(--calc-primary)}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input,.rd-calc-field select{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus,.rd-calc-field select:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-tab{padding:8px 10px;font-size:.78em}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    MPC Material & Heater Calculator
  </div>
  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="material">Material Lookup</button>
    <button class="rd-calc-tab" data-tab="ptc">PTC Heater Power</button>
  </div>
  <div class="rd-calc-content">
    <!-- Material Parameter Lookup -->
    <div class="rd-calc-panel active" data-panel="material">
      <h4>Filament Material Parameters</h4>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>Select Material</label>
          <select id="mpc_material" onchange="lookupMaterial()">
            <option value="">-- Select material --</option>
            <option value="PLA|1.25|2.00">PLA</option>
            <option value="PETG|1.27|1.95">PETG</option>
            <option value="ABS|1.06|1.83">ABS</option>
            <option value="ASA|1.07|1.70">ASA</option>
            <option value="PC|1.20|1.50">PC</option>
            <option value="PC+ABS|1.15|1.85">PC+ABS</option>
            <option value="PA|1.15|2.25">PA (Nylon)</option>
            <option value="PA6|1.12|2.25">PA6</option>
            <option value="TPU|1.21|1.75">TPU</option>
            <option value="TPU-90A|1.15|1.75">TPU-90A</option>
            <option value="TPU-95A|1.22|1.75">TPU-95A</option>
          </select>
        </div>
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Filament Density (g/cm³)</label>
            <input type="number" id="mpc_density" step="any" placeholder="e.g. 1.20">
            <span class="hint">filament_density config parameter</span>
          </div>
          <div class="rd-calc-field">
            <label>Specific Heat (J/g/K)</label>
            <input type="number" id="mpc_heat" step="any" placeholder="e.g. 1.80">
            <span class="hint">filament_heat_capacity config parameter</span>
          </div>
        </div>
        <button class="rd-calc-btn" onclick="generateMPCCommand()">Generate MPC_SET Command</button>
        <div class="rd-calc-result" id="material_result">
          <div class="label">MPC_SET G-Code Command</div>
          <div class="value" id="material_value" style="font-size:1em;word-break:break-all"></div>
          <div class="config" id="material_config"></div>
        </div>
      </div>
    </div>
    <!-- PTC Heater Power Lookup -->
    <div class="rd-calc-panel" data-panel="ptc">
      <h4>PTC Heater Power Lookup</h4>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>Heater Model</label>
          <select id="mpc_heater">
            <option value="rapido2">Rapido 2</option>
            <option value="rapido1">Rapido 1</option>
            <option value="dragonace_old">Dragon Ace (old)</option>
            <option value="dragonace_new">Dragon Ace (new)</option>
            <option value="revo40">Revo 40W</option>
            <option value="revo60">Revo 60W</option>
          </select>
        </div>
        <div class="rd-calc-field">
          <label>Print Temperature (°C)</label>
          <input type="number" id="mpc_temp" value="240" step="1">
          <span class="hint">Select your typical print temperature</span>
        </div>
        <button class="rd-calc-btn" onclick="lookupPTC()">Lookup Power</button>
        <div class="rd-calc-result" id="ptc_result">
          <div class="label">Recommended heater_power</div>
          <div class="value" id="ptc_value"></div>
          <div class="config" id="ptc_config"></div>
        </div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      document.querySelectorAll('.rd-calc-tab').forEach(function(t){t.addEventListener('click',function(){var c=this.closest('.rd-calc-container');c.querySelectorAll('.rd-calc-tab').forEach(function(x){x.classList.remove('active')});c.querySelectorAll('.rd-calc-panel').forEach(function(x){x.classList.remove('active')});this.classList.add('active');c.querySelector('[data-panel="'+this.dataset.tab+'"]').classList.add('active')})});
      var ptcData={rapido2:{180:72,200:70,220:67,240:65,260:64,280:62,300:60},rapido1:{180:52,200:51,220:50,240:49,260:48,280:47,300:46},dragonace_old:{180:51,200:48,220:46,240:44,260:43,280:41,300:39},dragonace_new:{180:66,200:63,220:60,240:58,260:55,280:53,300:51},revo40:{180:30,200:29,220:28,240:28,260:27,280:27,300:26},revo60:{180:45,200:44,220:43,240:42,260:40,280:39,300:38}};
      window.lookupMaterial=function(){var sel=document.getElementById('mpc_material').value;if(!sel)return;var parts=sel.split('|');document.getElementById('mpc_density').value=parts[1];document.getElementById('mpc_heat').value=parts[2]};
      window.generateMPCCommand=function(){var d=document.getElementById('mpc_density').value;var h=document.getElementById('mpc_heat').value;if(!d||!h)return;document.getElementById('material_value').textContent='MPC_SET HEATER=extruder FILAMENT_DENSITY='+d+' FILAMENT_HEAT_CAPACITY='+h;document.getElementById('material_config').textContent='filament_density: '+d+'\nfilament_heat_capacity: '+h;document.getElementById('material_result').classList.add('show')};
      window.lookupPTC=function(){var heater=document.getElementById('mpc_heater').value;var temp=parseInt(document.getElementById('mpc_temp').value);var data=ptcData[heater];if(!data)return;var temps=Object.keys(data).map(Number).sort(function(a,b){return a-b});var best=temps[0];for(var i=0;i<temps.length;i++){if(Math.abs(temps[i]-temp)<Math.abs(best-temp))best=temps[i]}var power=data[best];document.getElementById('ptc_value').textContent=power+' W at '+best+'°C';document.getElementById('ptc_config').textContent='heater_power: '+power;document.getElementById('ptc_result').classList.add('show')};
    })();
  </script>
</div>

# Basic Configuration

To use MPC as the temperature controller for the extruder use the following basic configuration block.

```
[extruder]
control: mpc
heater_power: 50  
cooling_fan:
filament_diameter: 1.75
filament_density: 1.20
filament_heat_capacity: 1.8 
```

- `control: mpc`  
  *Required*  
  The temperature control method.
  
- `heater_power: 50`  
  *Required*   
  The nameplate heater power in watts.  
  For a PTC, a non-linear heater, MPC may not work optimally due
  to the change in power output relative to heater temperature for this style of
  heater. Setting heater_power to the power output at the expected printing
  temperature is recommended.
  
- `cooling_fan:`  
  _Default Value: Nothing_  
  The fan that is cooling extruded filament and the hotend. Default is no fan so 
  there will be no fan taken into account for controlling the heater.
  Specifying "fan" will automatically use the part cooling fan. Any other fan
  section can also be used, e.g. `cooling_fan: fan_generic <fan_name>`.
  
- `filament_diameter: 1.75`  
  _Default Value: 1.75 (mm)_  
  This is the filament diameter.  
  
- `filament_density: 1.20`   
  _Default Value: 1.20 (g/mm^3)_  
  This is the material density of the filament being printed.
  
- `filament_heat_capacity: 1.80`  
  _Default Value: 1.80 (J/g/K)_  
  This is the material specific heat capacity of the filament being printed.  

## Optional Config Parameters

These can be specified in the config but should not need to be changed from the default values for most users.

- `maximum_retract:`  
  _Default Value: 2.0 (mm)_  
  This value clamps how much the extruder is allowed to go backwards in a single period during MPC FFF calculations. This lets the filament power go negative and add a small amount of energy to the system.  

- `target_reach_time:`  
  _Default Value: 2.0 (sec)_  
 
- `smoothing:`  
  _Default Value: 0.83 (sec)_  
  This parameter affects how quickly the model learns and it represents the ratio of temperature difference applied per second. A value of 1.0 represents no smoothing used in the model.  
  
- `min_ambient_change:`  
  _Default Value: 1.0 (deg C/s)_  
  Larger values of MIN_AMBIENT_CHANGE will result in faster convergence but will also cause the simulated ambient temperature to flutter somewhat chaotically around the ideal value.  
  
- `steady_state_rate:`  
  _Default Value: 0.5 (deg C/s)_  
  
- `ambient_temp_sensor: temperature_sensor <sensor_name>`  
  _Default Value: MPC ESTIMATE_  
  It is recommended not to specify this parameter and let MPC will estimate. This is used for initial state temperature and calibration but not for actual control.
  Any temperature sensor could be used, but the sensor should be in proximity to the hotend or measuring the ambient air surrounding the hotend.  

## PTC Heater Power

The `heater power:` for PTC style heaters is recommended to be set at the normal print temperature for the printer. Some common PTC heaters are given below for reference. If your heater is not listed the manufacturer should be able to provide a temperature and power curve.

| Heater Temp (C) | Rapido 2 (W) | Rapido 1 (W) | Dragon Ace old (W) | Dragon Ace new (W) | Revo 40 (W) |Revo 60 (W) |
|:---------------:|:------------:|:------------:|:------------------:|:------------------:|:-----------:|:----------:|
| 180             | 72           | 52           | 51                 | 66                 | 30          |45          |
| 200             | 70           | 51           | 48                 | 63                 | 29          |44          |
| 220             | 67           | 50           | 46                 | 60                 | 28          |43          |
| 240             | 65           | 49           | 44                 | 58                 | 28          |42          |
| 260             | 64           | 48           | 43                 | 55                 | 27          |40          |
| 280             | 62           | 47           | 41                 | 53                 | 27          |39          |
| 300             | 60           | 46           | 39                 | 51                 | 26          |38          |

## Filament Feed Forward Configuration

The filament feed forward (FFF) feature allows MPC to look forward and see changes in extrusion rates which could require more or less heat input to maintain target temperature. This feature substantially improves the accuracy and responsiveness of the model during printing. It is enabled by default and can be defined is more detail with the `filament_density` and `filament_heat_capacity` config parameters. The default values are set to cover a wide range of standard materials including ABS, ASA, PLA, PETG. 

 FFF parameters can be set, for the printer session, via the `MPC_SET` G-Code command:  

`MPC_SET HEATER=<heater> FILAMENT_DENSITY=<value> FILAMENT_HEAT_CAPACITY=<value> [FILAMENT_TEMP=<sensor|ambient|<value>>]`

- `HEATER`:  
  Only extruder is supported
  
- `FILAMENT_DENSITY`:  
  Filament density in g/mm^3
  
- `FILAMENT_HEAT_CAPACITY`:  
  Filament heat capacity in J/g/K
  
- `FILAMENT_TEMP`:  
  This can be set to either `sensor`, `ambient`, or a set temperature value. FFF will use the specific energy required to heat the filament and the power loss will be calculated based on the temperature delta.  

For example, updating the filament material properties for ASA would be:   

```
MPC_SET HEATER=extruder FILAMENT_DENSITY=1.07 FILAMENT_HEAT_CAPACITY=1.7  
```

## Filament Physical Properties

MPC works best knowing how much energy (in Joules) it takes to heat 1mm of filament by 1°C. The material values from the tables below have been curated from popular filament manufacturers and material data references. These values are sufficient for MPC to implement the FFF feature.  Advanced users could tune the `filament_density` and `filament_heat_capacity` parameters based on manufacturers datasheets. 

### Common Materials

| Material | Density [g/cm³] | Specific heat [J/g/K] |
| -------- |:---------------:|:---------------------:|
| PLA      | 1.25            | 1.8 - 2.2             |
| PETG     | 1.27            | 1.7 - 2.2             |
| PC+ABS   | 1.15            | 1.5 - 2.2             |
| ABS      | 1.06            | 1.25 - 2.4            |
| ASA      | 1.07            | 1.3 - 2.1             |
| PA6      | 1.12            | 2 - 2.5               |
| PA       | 1.15            | 2 - 2.5               |
| PC       | 1.20            | 1.1 - 1.9             |
| TPU      | 1.21            | 1.5 - 2               |
| TPU-90A  | 1.15            | 1.5 - 2               |
| TPU-95A  | 1.22            | 1.5 - 2               |

### Common Carbon Fiber Filled Materials

| Material                                     | Density [g/cm³] | Specific heat [J/g/K] |
| -------------------------------------------- |:---------------:|:---------------------:|
| ABS-CF                                       | 1.11            | ^                     |
| ASA-CF                                       | 1.11            | ^                     |
| PA6-CF                                       | 1.19            | ^                     |
| PC+ABS-CF                                    | 1.22            | ^                     |
| PC+CF                                        | 1.36            | ^                     |
| PLA-CF                                       | 1.29            | ^                     |
| PETG-CF                                      | 1.30            | ^                     |  

^ Use the specific heat from the base polymer  

# Calibration

The MPC default calibration routine takes the following steps:

> 1. Cool to ambient: The calibration routine needs to know the approximate ambient temperature and waits until the hotend temperature stabilises and stops decreasing relative to ambient.
> 2. Heat past 200°C: Measure the point where the temperature is increasing most rapidly, and the time and temperature at that point. Also, three temperature measurements are needed at some point after the initial latency has taken effect. 
> 3. Hold temperature while measuring ambient heat-loss: At this point enough is known for the MPC algorithm to engage. The calibration routine makes a best guess at the overshoot past 200°C which will occur and targets this temperature for about a minute while ambient heat-loss is measured without and with the fan engaged (if a `cooling_fan` is specified).
> 4. The MPC calibration routine creates the appropriate model constants. At this time the model parameters are temporary and not yet saved to the printer configuration.  

The MPC calibration routine must be run for each heater, to be controlled by MPC, in order to determine the model parameters. For an MPC calibration to be successful an extruder must be able to reach 200C. Calibration is performed with the following G-code command.

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`  

- `HEATER=<heater>`:  
  The extruder heater to be calibrated.  
  
- `TARGET=<temperature>`:  
  _Default Value: 200 (deg C)_  
  Sets the calibration temperature. The default of 200C is a good target for the extruder. MPC calibration is temperature independent, so calibrating the extruder at higher temperatures will not necessarily produce better model parameters. This is an area of exploration for advanced users.  
  
- `FAN_BREAKPOINTS=<value>`:  
  _Default Value: 3_  
  Sets the number off fan setpoint to test during calibration. An arbitrary number of breakpoints can be specified e.g. 7 breakpoints would result in (0, 16%, 33%, 50%, 66%, 83%, 100%) fan speeds.
  It is recommended to use a number that will capture one or more test points below the lowest level of fan normally used. For example, if 20% fan is the lowest commonly used speed, using 11 break points is recommended to test 10% and 20% fan at the low range.  
  
Default calibration of the hotend with seven fan breakpoints:  
```
MPC_CALIBRATE HEATER=extruder FAN_BREAKPOINTS=7
```
> [!NOTE]
> Ensure that the part cooling fan is off before starting calibration.  

After successful  calibration the method will generate the key model parameters into the log for future reference.  

![Calibration Parameter Output](img/MPC_calibration_output.png)

A `SAVE_CONFIG` command is then required to commit these calibrated model parameters to the printer config or the user can manually update the values. The _SAVE_CONFIG_ block should then look like: 

```
#*# <----------- SAVE_CONFIG ----------->
#*# DO NOT EDIT THIS BLOCK OR BELOW. The contents are auto-generated.
#*# [extruder]
#*# control = mpc
#*# block_heat_capacity = 22.3110
#*# sensor_responsiveness = 0.0998635
#*# ambient_transfer = 0.155082
#*# fan_ambient_transfer=0.155082, 0.20156, 0.216441
```

> [!NOTE]
> If the [extruder] section is in a .cfg file other than printer.cfg the `SAVE_CONFIG` command may not be able to write the calibration parameters and klippy will provide an error. 

These model parameters are not suitable for pre-configuration or are not explicitly determinable. Advanced users could tweak these post calibration based on the following guidance: Slightly increasing these values will increase the temperature where MPC settles and slightly decreasing them will decrease the settling temperature.  

- `block_heat_capacity:`  
  Heat capacity of the heater block in (J/K).  
  
- `ambient_transfer:`  
  Heat transfer from heater block to ambient in (W/K).  
  
- `sensor_responsiveness:`  
  A single constant representing the coefficient of heat transfer from heater block to sensor and heat capacity of the sensor in (K/s/K).  
  
- `fan_ambient_transfer:`  
  Heat transfer from heater block to ambient in with fan enabled in (W/K).  
  
# Support Macros

## Temperature Wait

The following macro can be used to replace `M109` hotend temperature set and `M190` bed temperature set G-code commands with a macro utilizing `temperature_wait` G-codes. This can be utilized in systems where the sensor temperature takes an extended time to converge on the set temperature. 
> [!NOTE]
> This behaviour occurs primarily because MPC controls the modelled block temperature and not the hotend temperature sensor. For almost all cases, when temperature sensor overshoot/undershoot occurs, the block modelled temperature will be correctly at the set temperature. However, the Kalico system performs actions based on the sensor temperature only which can lead to undesirable delays in print actions with stock `M109` and `M190` commands.

```
[gcode_macro M109] # Wait Hotend Temp
rename_existing: M109.1
gcode:
    #Parameters
    {% set s = params.S|float %}

    M104 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}  # Set hotend temp
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=extruder MINIMUM={s-2} MAXIMUM={s+5}   # Wait for hotend temp (within n degrees)
    {% endif %}


[gcode_macro M190] # Wait Bed Temp
rename_existing: M190.1
gcode:
    #Parameters
    {% set s = params.S|float %}

    M140 {% for p in params %}{'%s%s' % (p, params[p])}{% endfor %}   # Set bed temp
    {% if s != 0 %}
        TEMPERATURE_WAIT SENSOR=heater_bed MINIMUM={s-2} MAXIMUM={s+5}  # Wait for bed temp (within n degrees)
    {% endif %}
```

### Setting FFF Parameters From The Slicer

This macro will set FFF parameters automatically when the material type is passed from the slicer. 

```ini
[gcode_macro _SET_MPC_MATERIAL]
description: Set heater MPC parameters for a given material
variable_filament_table:
    ## Update this table to adjust material settings
    {
        ## ( density, heat capacity )  # suggested heat capacity range
        "PLA"       : ( 1.25, 2.20 ),  # 1.80 - 2.20
        "PETG"      : ( 1.27, 2.20 ),  # 1.70 - 2.20
        "PC+ABS"    : ( 1.15, 2.20 ),  # 1.50 - 2.20
        "ABS"       : ( 1.06, 2.40 ),  # 1.25 - 2.40
        "ASA"       : ( 1.07, 2.10 ),  # 1.30 - 2.10
        "PA6"       : ( 1.12, 2.50 ),  # 2.00 - 2.50
        "PA"        : ( 1.15, 2.50 ),  # 2.00 - 2.50
        "PC"        : ( 1.20, 1.90 ),  # 1.10 - 1.90
        "TPU"       : ( 1.21, 2.00 ),  # 1.50 - 2.00
        "TPU-90A"   : ( 1.15, 2.00 ),  # 1.50 - 2.00
        "TPU-95A"   : ( 1.22, 2.00 ),  # 1.50 - 2.00
        "ABS-CF"    : ( 1.11, 2.40 ),  # 1.25 - 2.40
        "ASA-CF"    : ( 1.11, 2.10 ),  # 1.30 - 2.10
        "PA6-CF"    : ( 1.19, 2.50 ),  # 2.00 - 2.50
        "PC+ABS-CF" : ( 1.22, 2.20 ),  # 1.50 - 2.20
        "PC+CF"     : ( 1.36, 1.90 ),  # 1.10 - 1.90
        "PLA-CF"    : ( 1.29, 2.20 ),  # 1.80 - 2.20
        "PETG-CF"   : ( 1.30, 2.20 ),  # 1.70 - 2.20
    }
gcode:
    {% set material = params.MATERIAL | upper %}
    {% set heater = params.HEATER | default('extruder') %}
    {% set extruder_config = printer.configfile.settings[heater] %}

    {% if material in filament_table %}
        {% set (density, heat_capacity) = filament_table[material] %}

        RESPOND PREFIX=🔥 MSG="Configured {heater} MPC for {material}. Density: {density}, Heat Capacity: {heat_capacity}"
    {% else %}
        {% set density = extruder_config.filament_density %}
        {% set heat_capacity=extruder_config.filament_heat_capacity %}

        RESPOND PREFIX=🔥 MSG="Unknown material '{material}', using default mpc parameters for {heater}"
    {% endif %}

    MPC_SET HEATER={heater} FILAMENT_DENSITY={density} FILAMENT_HEAT_CAPACITY={heat_capacity}
```

The slicer must be configured to pass the current material type to your `PRINT_START` macro. For PrusaSlicer you should add the following parameter line to `print_start` in the Start G-Code section:

```
MATERIAL=[filament_type[initial_extruder]]
```

The print_start line, in PrusaSlicer, would look like:

```
start_print MATERIAL=[filament_type[initial_extruder]] EXTRUDER_TEMP={first_layer_temperature[initial_extruder]} BED_TEMP={first_layer_bed_temperature[initial_extruder]} CHAMBER_TEMP={chamber_temperature}
```

Then, in your `PRINT_START` macro include the following macro call:

```
_SET_MPC_MATERIAL MATERIAL={params.MATERIAL}
```

# Real-Time Model State

The real-time temperatures and model states can be viewed from a browser by entering the following local address for your computer.

```
https://192.168.xxx.xxx:7125/printer/objects/query?extruder
```

![Calibration](img/MPC_realtime_output.png)

# EXPERIMENTAL FEATURES

## Bed Heater

Using MPC for bed heater control is functional but the performance is not guaranteed or currently supported.  MPC for the bed can be configured simply.

```
[heater_bed]
control: mpc
heater_power: 400
```

- `control: mpc`  
  *Required*  
  The temperature control method.  
  
- `heater_power: 50`  
  *Required*  
  The nameplate heater power in watts.  
  
- `cooling_fan: fan_generic <fan_name>`  
  _No Default Value_  
  This is the fan cooling the bed. Optional parameter to support bed fans.  

The bed should be able to reach at least 90C to perform calibration with the following G-code. 

`MPC_CALIBRATE HEATER=<heater> [TARGET=<temperature>] [FAN_BREAKPOINTS=<value>]`  

- `HEATER=<heater>`:  
  The bed heater to be calibrated.  
  
- `TARGET=<temperature>`:  
  _Default Value: 90 (deg C)_  
  Sets the calibration temperature. The default of 90C is a good target for the bed.  
  
- `FAN_BREAKPOINTS=<value>`:  
  _Default Value: 3_  
  Sets the number of fan setpoint to test during calibration.    

Default calibration of the hotend with five fan breakpoints:  
```
MPC_CALIBRATE HEATER=heater_bed FAN_BREAKPOINTS=5
```

These calibrated model parameters need to be saved to the _SAVE_CONFIG_ block manually or by using the `SAVE_CONFIG` command.

## Updating calibration parameters at runtime

Similar to [`SET_HEATER_PID`](G-Codes.md#set_heater_pid), you can update your MPC calibration profile at runtime.

`MPC_SET HEATER=<heater_name> [BLOCK_HEAT_CAPACITY=0.0] [SENSOR_RESPONSIVENESS=0.0] [AMBIENT_TRANSFER=0.0] [FAN_AMBIENT_TRANSFER=0.01,0.02,0.03]`

# BACKGROUND

## MPC Algorithm

MPC models the hotend system as four thermal masses: ambient air, the filament, the heater block and the sensor. Heater power heats the modelled heater block directly. Ambient air heats or cools the heater block. Filament cools the heater block. The heater block heats or cools the sensor.  

Every time the MPC algorithm runs it uses the following information to calculate a new temperature for the simulated hotend and sensor:  

- The last power setting for the hotend.  
- The present best-guess of the ambient temperature.  
- The effect of the fan on heat-loss to the ambient air.  
- The effect of filament feedrate on heat-loss to the filament. Filament is assumed to be at the same temperature as the ambient air.  

Once this calculation is done, the simulated sensor temperature is compared to the measured temperature and a fraction of the difference is added to the modelled sensor and heater block temperatures. This drags the simulated system in the direction of the real system. Because only a fraction of the difference is applied, sensor noise is diminished and averages out to zero over time. Both the simulated and the real sensor exhibit the same (or very similar) latency. Consequently, the effects of latency are eliminated when these values are compared to each other. So, the simulated hotend is only minimally affected by sensor noise and latency.   

SMOOTHING is the factor applied to the difference between simulated and measured sensor temperature. At its maximum value of 1, the simulated sensor temperature is continually set equal to the measured sensor temperature. A lower value will result in greater stability in MPC output power but also in decreased responsiveness. A value around 0.25 seems to work quite well.  

No simulation is perfect and, anyway, real life ambient temperature changes. So MPC also maintains a best guess estimate of ambient temperature. When the simulated system is close to steady state the simulated ambient temperature is continually adjusted. Steady state is determined to be when the MPC algorithm is not driving the hotend at its limits (i.e., full or zero heater power) or when it is at its limit but temperatures are still not changing very much - which will occur at asymptotic temperature (usually when target temperature is zero and the hotend is at ambient).  

Steady_state_rate is used to recognize the asymptotic condition. Whenever the simulated hotend temperature changes at an absolute rate less than steady_state_rate between two successive runs of the algorithm, the steady state logic is applied. Since the algorithm runs frequently, even a small amount of noise can result in a fairly high instantaneous rate of change of hotend temperature. In practice 1°C/s seems to work well for steady_state_rate.  

When in steady state, the difference between real and simulated sensor temperatures is used to drive the changes to ambient temperature. However, when the temperatures are really close min_ambient_change ensures that the simulated ambient temperature converges relatively quickly. Larger values of min_ambient_change will result in faster convergence but will also cause the simulated ambient temperature to flutter somewhat chaotically around the ideal value. This is not a problem because the effect of ambient temperature is fairly small and short-term variations of even 10°C or more will not have a noticeable effect.  

It is important to note that the simulated ambient temperature will only converge on real world ambient temperature if the ambient heat transfer coefficients are exactly accurate. In practice this will not be the case and the simulated ambient temperature therefore also acts a correction to these inaccuracies.  

Finally, armed with a new set of temperatures, the MPC algorithm calculates how much power must be applied to get the heater block to target temperature in the next two seconds. This calculation takes into account the heat that is expected to be lost to ambient air and filament heating. This power value is then converted to a PWM output.  

## Additional Details

Please refer to that the excellent Marlin MPC Documentation for information on the model derivations, tuning methods, and heat transfer coefficients used in this feature.   

# Acknowledgements

This feature is a port of the Marlin MPC implementation, and all credit goes to their team and community for pioneering this feature for open source 3D printing. The Marlin MPC documentation and github pages were heavily referenced and, in some cases directly copied and edited to create this document.  

- Marlin MPC Documentation: [https://marlinfw.org/docs/features/model_predictive_control.html]
- GITHUB PR that implemented MPC in Marlin: [https://github.com/MarlinFirmware/Marlin/pull/23751]
- Marlin Source Code: [https://github.com/MarlinFirmware/Marlin]
