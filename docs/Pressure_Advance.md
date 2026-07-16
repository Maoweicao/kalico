# Pressure advance

This document provides information on tuning the "pressure advance"
configuration variable for a particular nozzle and filament. The
pressure advance feature can be helpful in reducing ooze. For more
information on how pressure advance is implemented see the
[kinematics](Kinematics.md) document.

## Pressure Advance Calculator

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-content{padding:20px}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-panel p.formula{background:var(--calc-result-bg);padding:8px 12px;border-radius:4px;font-family:monospace;font-size:.9em;color:var(--calc-text-light);margin:0 0 16px;border-left:3px solid var(--calc-primary)}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input,.rd-calc-field select{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus,.rd-calc-field select:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.rd-calc-presets{display:flex;gap:8px;flex-wrap:wrap}.rd-calc-preset{background:var(--calc-tab-bg);border:1px solid var(--calc-border);padding:6px 12px;border-radius:4px;cursor:pointer;font-size:.85em;color:var(--calc-text);transition:all .2s}.rd-calc-preset:hover{border-color:var(--calc-primary);color:var(--calc-primary)}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    Pressure Advance Calculator
  </div>
  <div class="rd-calc-content">
    <h4>Calculate Pressure Advance from Test Tower</h4>
    <p class="formula">pressure_advance = start + measured_height × factor</p>
    <div class="rd-calc-form">
      <div class="rd-calc-field">
        <label>Presets</label>
        <div class="rd-calc-presets">
          <button class="rd-calc-preset" onclick="setPA(0,0.005)">Direct Drive</button>
          <button class="rd-calc-preset" onclick="setPA(0,0.020)">Bowden Tube</button>
          <button class="rd-calc-preset" onclick="setPA(0,0.001)">Custom (0.001)</button>
        </div>
      </div>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>START value</label>
          <input type="number" id="pa_start" value="0" step="any">
          <span class="hint">Usually 0 for standard tests</span>
        </div>
        <div class="rd-calc-field">
          <label>FACTOR value</label>
          <input type="number" id="pa_factor" value="0.005" step="any">
          <span class="hint">0.005 for direct drive, 0.020 for bowden</span>
        </div>
      </div>
      <div class="rd-calc-field">
        <label>Measured Height (mm)</label>
        <input type="number" id="pa_height" step="any" placeholder="e.g. 12.90">
        <span class="hint">Height of best quality corners from test tower</span>
      </div>
      <button class="rd-calc-btn" onclick="calcPA()">Calculate</button>
      <div class="rd-calc-result" id="pa_result">
        <div class="label">Pressure Advance</div>
        <div class="value" id="pa_value"></div>
        <div class="config" id="pa_config"></div>
      </div>
    </div>
  </div>
  <script>
    function setPA(s,f){document.getElementById('pa_start').value=s;document.getElementById('pa_factor').value=f}
    function calcPA(){var s=parseFloat(document.getElementById('pa_start').value);var f=parseFloat(document.getElementById('pa_factor').value);var h=parseFloat(document.getElementById('pa_height').value);if(isNaN(s)||isNaN(f)||isNaN(h))return;var pa=s+h*f;var r=Math.round(pa*1000)/1000;document.getElementById('pa_value').textContent=r.toFixed(3);document.getElementById('pa_config').textContent='pressure_advance: '+r.toFixed(3);document.getElementById('pa_result').classList.add('show')}
    document.querySelectorAll('#pa_height,#pa_start,#pa_factor').forEach(function(i){i.addEventListener('keypress',function(e){if(e.key==='Enter')calcPA()})});
  </script>
</div>

## Tuning pressure advance

Pressure advance does two useful things - it reduces ooze during
non-extrude moves and it reduces blobbing during cornering. This guide
uses the second feature (reducing blobbing during cornering) as a
mechanism for tuning.

In order to calibrate pressure advance the printer must be configured
and operational as the tuning test involves printing and inspecting a
test object. It is a good idea to read this document in full prior to
running the test.

Use a slicer to generate g-code for the large hollow square found in
[docs/prints/square_tower.stl](prints/square_tower.stl). Use a high
speed (eg, 100mm/s), zero infill, and a coarse layer height (the layer
height should be around 75% of the nozzle diameter). Make sure any
"dynamic acceleration control" and "scarf joint" seams are disabled in the slicer.

Prepare for the test by issuing the following G-Code command:
```
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=1 ACCEL=500
```
This command makes the nozzle travel slower through corners to
emphasize the effects of extruder pressure. Then for printers with a
direct drive extruder run the command:
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.005
```
For long bowden extruders use:
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.020
```
Then print the object. When fully printed the test print looks like:

![tuning_tower](img/tuning_tower.jpg)

The above TUNING_TOWER command instructs Kalico to alter the
pressure_advance setting on each layer of the print. Higher layers in
the print will have a larger pressure advance value set. Layers below
the ideal pressure_advance setting will have blobbing at the corners,
and layers above the ideal setting can lead to rounded corners and
poor extrusion leading up to the corner.

One can cancel the print early if one observes that the corners are no
longer printing well (and thus one can avoid printing layers that are
known to be above the ideal pressure_advance value).

Inspect the print and then use a digital calipers to find the height
that has the best quality corners. When in doubt, prefer a lower
height.

![tune_pa](img/tune_pa.jpg)

The pressure_advance value can then be calculated as `pressure_advance
= <start> + <measured_height> * <factor>`. (For example, `0 + 12.90 *
.020` would be `.258`.)

It is possible to choose custom settings for START and FACTOR if that
helps identify the best pressure advance setting. When doing this, be
sure to issue the TUNING_TOWER command at the start of each test
print.

Typical pressure advance values are between 0.050 and 1.000 (the high
end usually only with bowden extruders). If there is no significant
improvement with a pressure advance up to 1.000, then pressure advance
is unlikely to improve the quality of prints. Return to a default
configuration with pressure advance disabled.

Although this tuning exercise directly improves the quality of
corners, it's worth remembering that a good pressure advance
configuration also reduces ooze throughout the print.

At the completion of this test, set
`pressure_advance = <calculated_value>` in the `[extruder]` section of
the configuration file and issue a RESTART command. The RESTART
command will clear the test state and return the acceleration and
cornering speeds to their normal values.

## Important Notes

* The pressure advance value is dependent on the extruder, the nozzle,
  and the filament. It is common for filament from different
  manufactures or with different pigments to require significantly
  different pressure advance values. Therefore, one should calibrate
  pressure advance on each printer and with each spool of filament.

* Printing temperature and extrusion rates can impact pressure
  advance. Be sure to tune the
  [extruder rotation_distance](Rotation_Distance.md#calibrating-rotation_distance-on-extruders)
  and
  [nozzle temperature](http://reprap.org/wiki/Triffid_Hunter%27s_Calibration_Guide#Nozzle_Temperature)
  prior to tuning pressure advance.

* The test print is designed to run with a high extruder flow rate,
  but otherwise "normal" slicer settings. A high flow rate is obtained
  by using a high printing speed (eg, 100mm/s) and a coarse layer
  height (typically around 75% of the nozzle diameter). Other slicer
  settings should be similar to their defaults (eg, perimeters of 2 or
  3 lines, normal retraction amount). It can be useful to set the
  external perimeter speed to be the same speed as the rest of the
  print, but it is not a requirement.

* It is common for the test print to show different behavior on each
  corner. Often the slicer will arrange to change layers at one corner
  which can result in that corner being significantly different from
  the remaining three corners. If this occurs, then ignore that corner
  and tune pressure advance using the other three corners. It is also
  common for the remaining corners to vary slightly. (This can occur
  due to small differences in how the printer's frame reacts to
  cornering in certain directions.) Try to choose a value that works
  well for all the remaining corners. If in doubt, prefer a lower
  pressure advance value.

* If a high pressure advance value (eg, over 0.200) is used then one
  may find that the extruder skips when returning to the printer's
  normal acceleration. The pressure advance system accounts for
  pressure by pushing in extra filament during acceleration and
  retracting that filament during deceleration. With a high
  acceleration and high pressure advance the extruder may not have
  enough torque to push the required filament. If this occurs, either
  use a lower acceleration value or disable pressure advance.

* Once pressure advance is tuned in Kalico, it may still be useful to
  configure a small retract value in the slicer (eg, 0.75mm) and to
  utilize the slicer's "wipe on retract option" if available. These
  slicer settings may help counteract ooze caused by filament cohesion
  (filament pulled out of the nozzle due to the stickiness of the
  plastic). It is recommended to disable the slicer's "z-lift on
  retract" option.

* The pressure advance system does not change the timing or path of
  the toolhead. A print with pressure advance enabled will take the
  same amount of time as a print without pressure advance. Pressure
  advance also does not change the total amount of filament extruded
  during a print. Pressure advance results in extra extruder movement
  during move acceleration and deceleration. A very high pressure
  advance setting will result in a very large amount of extruder
  movement during acceleration and deceleration, and no configuration
  setting places a limit on the amount of that movement.
