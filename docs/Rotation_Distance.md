# Rotation distance

Stepper motor drivers on Kalico require a `rotation_distance`
parameter in each
[stepper config section](Config_Reference.md#stepper). The
`rotation_distance` is the amount of distance that the axis moves with
one full revolution of the stepper motor. This document describes how
one can configure this value.

## Rotation Distance Calculator

<div class="rd-calc-container">
  <style>
    .rd-calc-container {
      --calc-primary: #e67e22;
      --calc-primary-hover: #d35400;
      --calc-bg: #fff;
      --calc-border: #ddd;
      --calc-text: #333;
      --calc-text-light: #666;
      --calc-result-bg: #f8f9fa;
      --calc-tab-bg: #f1f1f1;
      --calc-success: #27ae60;
    }
    [data-md-color-scheme="slate"] .rd-calc-container,
    [data-md-color-mode="dark"] .rd-calc-container {
      --calc-bg: #2d2d2d;
      --calc-border: #444;
      --calc-text: #e0e0e0;
      --calc-text-light: #aaa;
      --calc-result-bg: #383838;
      --calc-tab-bg: #363636;
    }
    .rd-calc-container * {
      box-sizing: border-box;
    }
    .rd-calc-container {
      background: var(--calc-bg);
      border: 1px solid var(--calc-border);
      border-radius: 8px;
      padding: 0;
      margin: 1.5em 0;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    .rd-calc-header {
      background: var(--calc-primary);
      color: white;
      padding: 12px 20px;
      font-size: 1.1em;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .rd-calc-header svg {
      width: 20px;
      height: 20px;
      fill: currentColor;
    }
    .rd-calc-tabs {
      display: flex;
      flex-wrap: wrap;
      background: var(--calc-tab-bg);
      border-bottom: 1px solid var(--calc-border);
      padding: 0;
      margin: 0;
    }
    .rd-calc-tab {
      padding: 10px 16px;
      cursor: pointer;
      border: none;
      background: transparent;
      color: var(--calc-text-light);
      font-size: 0.85em;
      font-weight: 500;
      transition: all 0.2s;
      border-bottom: 2px solid transparent;
      white-space: nowrap;
    }
    .rd-calc-tab:hover {
      color: var(--calc-primary);
      background: rgba(230, 126, 34, 0.05);
    }
    .rd-calc-tab.active {
      color: var(--calc-primary);
      border-bottom-color: var(--calc-primary);
      background: var(--calc-bg);
    }
    .rd-calc-content {
      padding: 20px;
    }
    .rd-calc-panel {
      display: none;
    }
    .rd-calc-panel.active {
      display: block;
    }
    .rd-calc-panel h4 {
      margin: 0 0 8px 0;
      color: var(--calc-text);
      font-size: 1em;
    }
    .rd-calc-panel p.formula {
      background: var(--calc-result-bg);
      padding: 8px 12px;
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.9em;
      color: var(--calc-text-light);
      margin: 0 0 16px 0;
      border-left: 3px solid var(--calc-primary);
    }
    .rd-calc-form {
      display: grid;
      gap: 12px;
    }
    .rd-calc-field {
      display: grid;
      gap: 4px;
    }
    .rd-calc-field label {
      font-size: 0.85em;
      color: var(--calc-text-light);
      font-weight: 500;
    }
    .rd-calc-field input,
    .rd-calc-field select {
      padding: 8px 12px;
      border: 1px solid var(--calc-border);
      border-radius: 4px;
      font-size: 0.95em;
      background: var(--calc-bg);
      color: var(--calc-text);
      transition: border-color 0.2s;
    }
    .rd-calc-field input:focus,
    .rd-calc-field select:focus {
      outline: none;
      border-color: var(--calc-primary);
      box-shadow: 0 0 0 2px rgba(230, 126, 34, 0.2);
    }
    .rd-calc-field .hint {
      font-size: 0.75em;
      color: var(--calc-text-light);
      margin-top: 2px;
    }
    .rd-calc-btn {
      background: var(--calc-primary);
      color: white;
      border: none;
      padding: 10px 20px;
      border-radius: 4px;
      font-size: 0.95em;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.2s;
      justify-self: start;
    }
    .rd-calc-btn:hover {
      background: var(--calc-primary-hover);
    }
    .rd-calc-result {
      margin-top: 16px;
      padding: 12px 16px;
      background: var(--calc-result-bg);
      border-radius: 4px;
      display: none;
    }
    .rd-calc-result.show {
      display: block;
    }
    .rd-calc-result .label {
      font-size: 0.8em;
      color: var(--calc-text-light);
      margin-bottom: 4px;
    }
    .rd-calc-result .value {
      font-size: 1.4em;
      font-weight: 700;
      color: var(--calc-success);
      font-family: monospace;
    }
    .rd-calc-result .config {
      margin-top: 8px;
      padding: 8px 12px;
      background: var(--calc-bg);
      border: 1px solid var(--calc-border);
      border-radius: 4px;
      font-family: monospace;
      font-size: 0.85em;
      color: var(--calc-text);
      user-select: all;
    }
    .rd-calc-row {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    @media (max-width: 480px) {
      .rd-calc-row {
        grid-template-columns: 1fr;
      }
      .rd-calc-tab {
        padding: 8px 10px;
        font-size: 0.78em;
      }
      .rd-calc-content {
        padding: 16px;
      }
    }
  </style>

  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    Rotation Distance Calculator
  </div>

  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="steps">Steps/mm</button>
    <button class="rd-calc-tab" data-tab="stepdist">Step Distance</button>
    <button class="rd-calc-tab" data-tab="belt">Belt & Pulley</button>
    <button class="rd-calc-tab" data-tab="screw">Lead Screw</button>
    <button class="rd-calc-tab" data-tab="extruder">Extruder Dia.</button>
    <button class="rd-calc-tab" data-tab="calibrate">Calibrate</button>
  </div>

  <div class="rd-calc-content">
    <!-- Steps/mm Calculator -->
    <div class="rd-calc-panel active" data-panel="steps">
      <h4>Calculate from Steps per mm</h4>
      <p class="formula">rotation_distance = full_steps × microsteps / steps_per_mm</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Full Steps per Rotation</label>
            <input type="number" id="steps_full" value="200" min="1">
            <span class="hint">200 for 1.8° motors, 400 for 0.9° motors</span>
          </div>
          <div class="rd-calc-field">
            <label>Microsteps</label>
            <input type="number" id="steps_micro" value="16" min="1">
            <span class="hint">Usually 16 for most drivers</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>Steps per mm</label>
          <input type="number" id="steps_per_mm" step="any" placeholder="e.g. 80">
        </div>
        <button class="rd-calc-btn" onclick="calcSteps()">Calculate</button>
        <div class="rd-calc-result" id="steps_result">
          <div class="label">Rotation Distance</div>
          <div class="value" id="steps_value"></div>
          <div class="config" id="steps_config"></div>
        </div>
      </div>
    </div>

    <!-- Step Distance Calculator -->
    <div class="rd-calc-panel" data-panel="stepdist">
      <h4>Calculate from Step Distance</h4>
      <p class="formula">rotation_distance = full_steps × microsteps × step_distance</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Full Steps per Rotation</label>
            <input type="number" id="stepdist_full" value="200" min="1">
            <span class="hint">200 for 1.8° motors, 400 for 0.9° motors</span>
          </div>
          <div class="rd-calc-field">
            <label>Microsteps</label>
            <input type="number" id="stepdist_micro" value="16" min="1">
            <span class="hint">Usually 16 for most drivers</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>Step Distance (mm)</label>
          <input type="number" id="step_distance" step="any" placeholder="e.g. 0.00625">
          <span class="hint">The distance per step in mm</span>
        </div>
        <button class="rd-calc-btn" onclick="calcStepDist()">Calculate</button>
        <div class="rd-calc-result" id="stepdist_result">
          <div class="label">Rotation Distance</div>
          <div class="value" id="stepdist_value"></div>
          <div class="config" id="stepdist_config"></div>
        </div>
      </div>
    </div>

    <!-- Belt & Pulley Calculator -->
    <div class="rd-calc-panel" data-panel="belt">
      <h4>Belt Driven Axis</h4>
      <p class="formula">rotation_distance = belt_pitch × teeth_on_pulley</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Belt Pitch (mm)</label>
            <input type="number" id="belt_pitch" value="2" step="any">
            <span class="hint">Usually 2mm for GT2 belts</span>
          </div>
          <div class="rd-calc-field">
            <label>Teeth on Pulley</label>
            <input type="number" id="belt_teeth" placeholder="e.g. 20" min="1">
            <span class="hint">Count teeth on the motor pulley</span>
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcBelt()">Calculate</button>
        <div class="rd-calc-result" id="belt_result">
          <div class="label">Rotation Distance</div>
          <div class="value" id="belt_value"></div>
          <div class="config" id="belt_config"></div>
        </div>
      </div>
    </div>

    <!-- Lead Screw Calculator -->
    <div class="rd-calc-panel" data-panel="screw">
      <h4>Lead Screw Axis</h4>
      <p class="formula">rotation_distance = screw_pitch × number_of_threads</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Screw Pitch (mm)</label>
            <input type="number" id="screw_pitch" step="any" placeholder="e.g. 2">
            <span class="hint">Distance between grooves</span>
          </div>
          <div class="rd-calc-field">
            <label>Number of Threads</label>
            <input type="number" id="screw_threads" placeholder="e.g. 4" min="1">
            <span class="hint">T8 = 4, M6/M8 = 1</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>Common Presets</label>
          <select id="screw_preset" onchange="applyScrewPreset()">
            <option value="">-- Select preset --</option>
            <option value="2,4">T8 Leadscrew (pitch=2, threads=4)</option>
            <option value="2,2">T4 Leadscrew (pitch=2, threads=2)</option>
            <option value="1.25,1">M8 Rod (pitch=1.25, threads=1)</option>
            <option value="1,1">M6 Rod (pitch=1, threads=1)</option>
          </select>
        </div>
        <button class="rd-calc-btn" onclick="calcScrew()">Calculate</button>
        <div class="rd-calc-result" id="screw_result">
          <div class="label">Rotation Distance</div>
          <div class="value" id="screw_value"></div>
          <div class="config" id="screw_config"></div>
        </div>
      </div>
    </div>

    <!-- Extruder Diameter Calculator -->
    <div class="rd-calc-panel" data-panel="extruder">
      <h4>Extruder (by Gear Diameter)</h4>
      <p class="formula">rotation_distance = diameter × π (3.14159)</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>Hobbed Bolt/Gear Diameter (mm)</label>
          <input type="number" id="extruder_dia" step="any" placeholder="e.g. 7.3">
          <span class="hint">Measure the effective diameter of the drive gear</span>
        </div>
        <button class="rd-calc-btn" onclick="calcExtruder()">Calculate</button>
        <div class="rd-calc-result" id="extruder_result">
          <div class="label">Rotation Distance (before gear_ratio)</div>
          <div class="value" id="extruder_value"></div>
          <div class="config" id="extruder_config"></div>
        </div>
      </div>
    </div>

    <!-- Calibration Calculator -->
    <div class="rd-calc-panel" data-panel="calibrate">
      <h4>Extruder Calibration (Measure & Trim)</h4>
      <p class="formula">new_rd = previous_rd × actual_distance / requested_distance</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>Previous Rotation Distance</label>
          <input type="number" id="cal_prev_rd" step="any" placeholder="e.g. 22.678">
          <span class="hint">Your current rotation_distance setting</span>
        </div>
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>Initial Mark Distance (mm)</label>
            <input type="number" id="cal_initial" step="any" placeholder="e.g. 70">
            <span class="hint">Distance from extruder to mark before extruding</span>
          </div>
          <div class="rd-calc-field">
            <label>Subsequent Mark Distance (mm)</label>
            <input type="number" id="cal_subsequent" step="any" placeholder="e.g. 20">
            <span class="hint">Distance from extruder to mark after extruding</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>Requested Extrude Distance (mm)</label>
          <input type="number" id="cal_requested" value="50" step="any">
          <span class="hint">Usually 50mm as per the calibration procedure</span>
        </div>
        <button class="rd-calc-btn" onclick="calcCalibrate()">Calculate</button>
        <div class="rd-calc-result" id="calibrate_result">
          <div class="label">New Rotation Distance</div>
          <div class="value" id="calibrate_value"></div>
          <div class="config" id="calibrate_config"></div>
          <div id="calibrate_warn" style="margin-top:8px;color:#e74c3c;font-size:0.85em;display:none;">
            ⚠ Actual extrude distance differs from requested by more than 2mm. Consider re-calibrating.
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    (function() {
      // Tab switching
      document.querySelectorAll('.rd-calc-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
          var container = this.closest('.rd-calc-container');
          container.querySelectorAll('.rd-calc-tab').forEach(function(t) { t.classList.remove('active'); });
          container.querySelectorAll('.rd-calc-panel').forEach(function(p) { p.classList.remove('active'); });
          this.classList.add('active');
          container.querySelector('[data-panel="' + this.dataset.tab + '"]').classList.add('active');
        });
      });

      // Helper to show result
      function showResult(resultId, valueId, configId, value, configText) {
        document.getElementById(valueId).textContent = value;
        document.getElementById(configId).textContent = 'rotation_distance: ' + configText;
        document.getElementById(resultId).classList.add('show');
      }

      // Steps/mm calculator
      window.calcSteps = function() {
        var full = parseFloat(document.getElementById('steps_full').value);
        var micro = parseFloat(document.getElementById('steps_micro').value);
        var spm = parseFloat(document.getElementById('steps_per_mm').value);
        if (isNaN(full) || isNaN(micro) || isNaN(spm) || spm === 0) return;
        var rd = (full * micro) / spm;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('steps_result', 'steps_value', 'steps_config', rounded.toFixed(3), rounded.toFixed(3));
      };

      // Step distance calculator
      window.calcStepDist = function() {
        var full = parseFloat(document.getElementById('stepdist_full').value);
        var micro = parseFloat(document.getElementById('stepdist_micro').value);
        var sd = parseFloat(document.getElementById('step_distance').value);
        if (isNaN(full) || isNaN(micro) || isNaN(sd)) return;
        var rd = full * micro * sd;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('stepdist_result', 'stepdist_value', 'stepdist_config', rounded.toFixed(3), rounded.toFixed(3));
      };

      // Belt calculator
      window.calcBelt = function() {
        var pitch = parseFloat(document.getElementById('belt_pitch').value);
        var teeth = parseFloat(document.getElementById('belt_teeth').value);
        if (isNaN(pitch) || isNaN(teeth)) return;
        var rd = pitch * teeth;
        showResult('belt_result', 'belt_value', 'belt_config', rd.toFixed(1), rd.toFixed(1));
      };

      // Screw calculator
      window.calcScrew = function() {
        var pitch = parseFloat(document.getElementById('screw_pitch').value);
        var threads = parseFloat(document.getElementById('screw_threads').value);
        if (isNaN(pitch) || isNaN(threads)) return;
        var rd = pitch * threads;
        showResult('screw_result', 'screw_value', 'screw_config', rd.toFixed(2), rd.toFixed(2));
      };

      // Screw preset
      window.applyScrewPreset = function() {
        var val = document.getElementById('screw_preset').value;
        if (!val) return;
        var parts = val.split(',');
        document.getElementById('screw_pitch').value = parts[0];
        document.getElementById('screw_threads').value = parts[1];
      };

      // Extruder diameter calculator
      window.calcExtruder = function() {
        var dia = parseFloat(document.getElementById('extruder_dia').value);
        if (isNaN(dia)) return;
        var rd = dia * Math.PI;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('extruder_result', 'extruder_value', 'extruder_config', rounded.toFixed(3), rounded.toFixed(3));
      };

      // Calibration calculator
      window.calcCalibrate = function() {
        var prevRd = parseFloat(document.getElementById('cal_prev_rd').value);
        var initial = parseFloat(document.getElementById('cal_initial').value);
        var subsequent = parseFloat(document.getElementById('cal_subsequent').value);
        var requested = parseFloat(document.getElementById('cal_requested').value);
        if (isNaN(prevRd) || isNaN(initial) || isNaN(subsequent) || isNaN(requested) || requested === 0) return;
        var actual = initial - subsequent;
        var newRd = prevRd * actual / requested;
        var rounded = Math.round(newRd * 1000) / 1000;
        showResult('calibrate_result', 'calibrate_value', 'calibrate_config', rounded.toFixed(3), rounded.toFixed(3));
        var warn = document.getElementById('calibrate_warn');
        warn.style.display = Math.abs(actual - requested) > 2 ? 'block' : 'none';
      };

      // Enter key support
      document.querySelectorAll('.rd-calc-field input').forEach(function(input) {
        input.addEventListener('keypress', function(e) {
          if (e.key === 'Enter') {
            var btn = this.closest('.rd-calc-panel').querySelector('.rd-calc-btn');
            if (btn) btn.click();
          }
        });
      });
    })();
  </script>
</div>

## Obtaining rotation_distance from steps_per_mm (or step_distance)

The designers of your 3d printer originally calculated `steps_per_mm`
from a rotation distance. If you know the steps_per_mm then it is
possible to use this general formula to obtain that original rotation
distance:
```
rotation_distance = <full_steps_per_rotation> * <microsteps> / <steps_per_mm>
```

Or, if you have an older Kalico configuration and know the
`step_distance` parameter you can use this formula:
```
rotation_distance = <full_steps_per_rotation> * <microsteps> * <step_distance>
```

The `<full_steps_per_rotation>` setting is determined from the type of
stepper motor. Most stepper motors are "1.8 degree steppers" and
therefore have 200 full steps per rotation (360 divided by 1.8 is
200). Some stepper motors are "0.9 degree steppers" and thus have 400
full steps per rotation. Other stepper motors are rare. If unsure, do
not set full_steps_per_rotation in the config file and use 200 in the
formula above.

The `<microsteps>` setting is determined by the stepper motor driver.
Most drivers use 16 microsteps. If unsure, set `microsteps: 16` in the
config and use 16 in the formula above.

Almost all printers should have a whole number for `rotation_distance`
on X, Y, and Z type axes. If the above formula results in a
rotation_distance that is within .01 of a whole number then round the
final value to that whole_number.

## Calibrating rotation_distance on extruders

On an extruder, the `rotation_distance` is the amount of distance the
filament travels for one full rotation of the stepper motor. The best
way to get an accurate value for this setting is to use a "measure and
trim" procedure.

First start with an initial guess for the rotation distance. This may
be obtained from
[steps_per_mm](#obtaining-rotation_distance-from-steps_per_mm-or-step_distance)
or by [inspecting the hardware](#extruder).

Then use the following procedure to "measure and trim":
1. Make sure the extruder has filament in it, the hotend is heated to
   an appropriate temperature, and the printer is ready to extrude.
2. Use a marker to place a mark on the filament around 70mm from the
   intake of the extruder body. Then use a digital calipers to measure
   the actual distance of that mark as precisely as one can. Note this
   as `<initial_mark_distance>`.
3. Extrude 50mm of filament with the following command sequence: `G91`
   followed by `G1 E50 F60`. Note 50mm as
   `<requested_extrude_distance>`. Wait for the extruder to finish the
   move (it will take about 50 seconds). It is important to use the
   slow extrusion rate for this test as a faster rate can cause high
   pressure in the extruder which will skew the results. (Do not use
   the "extrude button" on graphical front-ends for this test as they
   extrude at a fast rate.)
4. Use the digital calipers to measure the new distance between the
   extruder body and the mark on the filament. Note this as
   `<subsequent_mark_distance>`. Then calculate:
   `actual_extrude_distance = <initial_mark_distance> - <subsequent_mark_distance>`
5. Calculate rotation_distance as:
   `rotation_distance = <previous_rotation_distance> * <actual_extrude_distance> / <requested_extrude_distance>`
   Round the new rotation_distance to three decimal places.

If the actual_extrude_distance differs from requested_extrude_distance
by more than about 2mm then it is a good idea to perform the steps
above a second time.

Note: Do *not* use a "measure and trim" type of method to calibrate x,
y, or z type axes. The "measure and trim" method is not accurate
enough for those axes and will likely lead to a worse configuration.
Instead, if needed, those axes can be determined by
[measuring the belts, pulleys, and lead screw hardware](#obtaining-rotation_distance-by-inspecting-the-hardware).

## Obtaining rotation_distance by inspecting the hardware

It's possible to calculate rotation_distance with knowledge of the
stepper motors and printer kinematics. This may be useful if the
steps_per_mm is not known or if designing a new printer.

### Belt driven axes

It is easy to calculate rotation_distance for a linear axis that uses
a belt and pulley.

First determine the type of belt. Most printers use a 2mm belt pitch
(that is, each tooth on the belt is 2mm apart). Then count the number
of teeth on the stepper motor pulley. The rotation_distance is then
calculated as:
```
rotation_distance = <belt_pitch> * <number_of_teeth_on_pulley>
```

For example, if a printer has a 2mm belt and uses a pulley with 20
teeth, then the rotation distance is 40.

### Axes with a lead screw

It is easy to calculate the rotation_distance for common lead screws
using the following formula:
```
rotation_distance = <screw_pitch> * <number_of_separate_threads>
```

For example, the common "T8 leadscrew" has a rotation distance of 8
(it has a pitch of 2mm and has 4 separate threads).

Older printers with "threaded rods" have only one "thread" on the lead
screw and thus the rotation distance is the pitch of the screw. (The
screw pitch is the distance between each groove on the screw.) So, for
example, an M6 metric rod has a rotation distance of 1 and an M8 rod
has a rotation distance of 1.25.

### Extruder

It's possible to obtain an initial rotation distance for extruders by
measuring the diameter of the "hobbed bolt" that pushes the filament
and using the following formula: `rotation_distance = <diameter> * 3.14`

If the extruder uses gears then it will also be necessary to
[determine and set the gear_ratio](#using-a-gear_ratio) for the
extruder.

The actual rotation distance on an extruder will vary from printer to
printer, because the grip of the "hobbed bolt" that engages the
filament can vary. It can even vary between filament spools. After
obtaining an initial rotation_distance, use the
[measure and trim procedure](#calibrating-rotation_distance-on-extruders)
to obtain a more accurate setting.

## Using a gear_ratio

Setting a `gear_ratio` can make it easier to configure the
`rotation_distance` on steppers that have a gear box (or similar)
attached to it. Most steppers do not have a gear box - if unsure then
do not set `gear_ratio` in the config.

When `gear_ratio` is set, the `rotation_distance` represents the
distance the axis moves with one full rotation of the final gear on
the gear box. If, for example, one is using a gearbox with a "5:1"
ratio, then one could calculate the rotation_distance with
[knowledge of the hardware](#obtaining-rotation_distance-by-inspecting-the-hardware)
and then add `gear_ratio: 5:1` to the config.

For gearing implemented with belts and pulleys, it is possible to
determine the gear_ratio by counting the teeth on the pulleys. For
example, if a stepper with a 16 toothed pulley drives the next pulley
with 80 teeth then one would use `gear_ratio: 80:16`. Indeed, one
could open a common off the shelf "gear box" and count the teeth in it
to confirm its gear ratio.

Note that sometimes a gearbox will have a slightly different gear
ratio than what it is advertised as. The common BMG extruder motor
gears are an example of this - they are advertised as "3:1" but
actually use "50:17" gearing. (Using teeth numbers without a common
denominator may improve overall gear wear as the teeth don't always
mesh the same way with each revolution.) The common "5.18:1 planetary
gearbox", is more accurately configured with `gear_ratio: 57:11`.

If several gears are used on an axis then it is possible to provide a
comma separated list to gear_ratio. For example, a "5:1" gear box
driving a 16 toothed to 80 toothed pulley could use
`gear_ratio: 5:1, 80:16`.

In most cases, gear_ratio should be defined with whole numbers as
common gears and pulleys have a whole number of teeth on them.
However, in cases where a belt drives a pulley using friction instead
of teeth, it may make sense to use a floating point number in the gear
ratio (eg, `gear_ratio: 107.237:16`).
