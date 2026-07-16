
# PID

PID control is a widely used control method in the 3D printing world.
It's ubiquitous when it comes to temperature control, be it with heaters to
generate heat or fans to remove heat. This document aims to provide a
high-level overview of what PID is and how to use it best in Kalico.

## PID Parameter Calculator

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-tabs{display:flex;flex-wrap:wrap;background:var(--calc-tab-bg);border-bottom:1px solid var(--calc-border);padding:0;margin:0}.rd-calc-tab{padding:10px 16px;cursor:pointer;border:none;background:transparent;color:var(--calc-text-light);font-size:.85em;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;white-space:nowrap}.rd-calc-tab:hover{color:var(--calc-primary);background:rgba(230,126,34,.05)}.rd-calc-tab.active{color:var(--calc-primary);border-bottom-color:var(--calc-primary);background:var(--calc-bg)}.rd-calc-content{padding:20px}.rd-calc-panel{display:none}.rd-calc-panel.active{display:block}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-panel p.formula{background:var(--calc-result-bg);padding:8px 12px;border-radius:4px;font-family:monospace;font-size:.9em;color:var(--calc-text-light);margin:0 0 16px;border-left:3px solid var(--calc-primary)}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input,.rd-calc-field select{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus,.rd-calc-field select:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-tab{padding:8px 10px;font-size:.78em}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    PID Parameter Calculator
  </div>
  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="zn">Ziegler-Nichols</button>
    <button class="rd-calc-tab" data-tab="cc">Cohen-Coon</button>
  </div>
  <div class="rd-calc-content">
    <!-- Ziegler-Nichols Calculator -->
    <div class="rd-calc-panel active" data-panel="zn">
      <h4>Ziegler-Nichols PID Calculator</h4>
      <p class="formula">Extract Ku and Tu from PID_CALIBRATE log</p>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>Ku (Ultimate Gain)</label>
          <input type="number" id="pid_ku" step="any" placeholder="e.g. 0.103092">
          <span class="hint">From "Ziegler-Nichols constants" in log</span>
        </div>
        <div class="rd-calc-field">
          <label>Tu (Ultimate Period)</label>
          <input type="number" id="pid_tu" step="any" placeholder="e.g. 41.8">
          <span class="hint">From "Ziegler-Nichols constants" in log</span>
        </div>
      </div>
      <button class="rd-calc-btn" onclick="calcZN()">Calculate</button>
      <div class="rd-calc-result" id="zn_result">
        <div class="label">PID Parameters (Ziegler-Nichols Variants)</div>
        <div class="value" id="zn_value" style="font-size:1em;line-height:1.8"></div>
        <div class="config" id="zn_config"></div>
      </div>
    </div>
    <!-- Cohen-Coon Calculator -->
    <div class="rd-calc-panel" data-panel="cc">
      <h4>Cohen-Coon PID Calculator</h4>
      <p class="formula">Extract Km, Theta, and Tau from PID_CALIBRATE log</p>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>Km (Process Gain)</label>
          <input type="number" id="pid_km" step="any" placeholder="e.g. -17.734845">
          <span class="hint">From "Cohen-Coon constants" in log</span>
        </div>
        <div class="rd-calc-field">
          <label>Theta (Dead Time)</label>
          <input type="number" id="pid_theta" step="any" placeholder="e.g. 6.6">
          <span class="hint">From "Cohen-Coon constants" in log</span>
        </div>
      </div>
      <div class="rd-calc-field">
        <label>Tau (Time Constant)</label>
        <input type="number" id="pid_tau" step="any" placeholder="e.g. -10.182680">
        <span class="hint">From "Cohen-Coon constants" in log</span>
      </div>
      <button class="rd-calc-btn" onclick="calcCC()">Calculate</button>
      <div class="rd-calc-result" id="cc_result">
        <div class="label">PID Parameters (Cohen-Coon)</div>
        <div class="value" id="cc_value" style="font-size:1em;line-height:1.8"></div>
        <div class="config" id="cc_config"></div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      document.querySelectorAll('.rd-calc-tab').forEach(function(t){t.addEventListener('click',function(){var c=this.closest('.rd-calc-container');c.querySelectorAll('.rd-calc-tab').forEach(function(x){x.classList.remove('active')});c.querySelectorAll('.rd-calc-panel').forEach(function(x){x.classList.remove('active')});this.classList.add('active');c.querySelector('[data-panel="'+this.dataset.tab+'"]').classList.add('active')})});
      window.calcZN=function(){var ku=parseFloat(document.getElementById('pid_ku').value);var tu=parseFloat(document.getElementById('pid_tu').value);if(isNaN(ku)||isNaN(tu))return;var classic={kp:0.6*ku,ki:1.2*ku/tu,kd:0.075*ku*tu};var p={kp:0.5*ku,ki:0,kd:0};var pi={kp:0.45*ku,ki:0.54*ku/tu,kd:0};var pid={kp:0.6*ku,ki:1.2*ku/tu,kd:0.075*ku*tu};var some={kp:0.33*ku,ki:0.66*ku/tu,kd:0.11*ku*tu};var html='<b>Classic:</b> Kp='+classic.kp.toFixed(3)+' Ki='+classic.ki.toFixed(3)+' Kd='+classic.kd.toFixed(3)+'<br><b>P only:</b> Kp='+p.kp.toFixed(3)+'<br><b>PI:</b> Kp='+pi.kp.toFixed(3)+' Ki='+pi.ki.toFixed(3)+'<br><b>PID:</b> Kp='+pid.kp.toFixed(3)+' Ki='+pid.ki.toFixed(3)+' Kd='+pid.kd.toFixed(3)+'<br><b>No Overshoot:</b> Kp='+some.kp.toFixed(3)+' Ki='+some.ki.toFixed(3)+' Kd='+some.kd.toFixed(3);document.getElementById('zn_value').innerHTML=html;document.getElementById('zn_config').textContent='pid_Kp='+pid.kp.toFixed(3)+' pid_Ki='+pid.ki.toFixed(3)+' pid_Kd='+pid.kd.toFixed(3);document.getElementById('zn_result').classList.add('show')};
      window.calcCC=function(){var km=parseFloat(document.getElementById('pid_km').value);var theta=parseFloat(document.getElementById('pid_theta').value);var tau=parseFloat(document.getElementById('pid_tau').value);if(isNaN(km)||isNaN(theta)||isNaN(tau))return;var r=theta/tau;var kp=(1/(km*r))*(1+r/3);var ki=kp/(theta*(32+6*r)/(13+8*r));var kd=kp*theta*4/(11+2*r);document.getElementById('cc_value').innerHTML='<b>Cohen-Coon:</b><br>Kp='+kp.toFixed(3)+'<br>Ki='+ki.toFixed(3)+'<br>Kd='+kd.toFixed(3);document.getElementById('cc_config').textContent='pid_Kp='+kp.toFixed(3)+' pid_Ki='+ki.toFixed(3)+' pid_Kd='+kd.toFixed(3);document.getElementById('cc_result').classList.add('show')};
      document.querySelectorAll('.rd-calc-field input').forEach(function(i){i.addEventListener('keypress',function(e){if(e.key==='Enter'){var b=this.closest('.rd-calc-panel').querySelector('.rd-calc-btn');if(b)b.click()}})});
    })();
  </script>
</div>

## PID Calibration

### Preparing the Calibration
When a calibration test is performed external influences should be minimized as
much as possible:
* Turn off aux fans
* Turn off chamber heaters
* Turn off the extruder heater when calibrating the bed and vice versa
* Avoid external disturbances like drafts, etc.

More important than listed above, **PID how you print**. If your part fans are on when printing, PID tune with them on.

### Choosing the right PID Algorithm
Kalico offers two different PID algorithms: Positional and Velocity

* Positional (`pid`)
    * The standard algorithm
    * Very robust against noisy temperature readings
    * Can cause overshoots
    * Insufficient target control in edge cases
* Velocity (`pid_v`)
    * No overshoot
    * Better target control in certain scenarios
    * More susceptible to noisy sensors
    * Might require larger smoothing time constants

Refer to the [control statement](Config_Reference.md#extruder) in the
Configuration Reference.

### Running the PID Calibration
The PID calibration is invoked via the [PID_CALIBRATE](G-Codes.md#pid_calibrate) command.
This command will heat up the respective  heater and let it cool down around
the target temperature in multiple cycles to determine the needed
parameters.

Such a calibration cycles looks like the following snippet:
```
3:12 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:15 PM   sample:1 pwm:1.0000 asymmetry:3.7519 tolerance:n/a
3:15 PM   sample:2 pwm:0.6229 asymmetry:0.3348 tolerance:n/a
3:16 PM   sample:3 pwm:0.5937 asymmetry:0.0840 tolerance:n/a
3:17 PM   sample:4 pwm:0.5866 asymmetry:0.0169 tolerance:0.4134
3:18 PM   sample:5 pwm:0.5852 asymmetry:0.0668 tolerance:0.0377
3:18 PM   sample:6 pwm:0.5794 asymmetry:0.0168 tolerance:0.0142
3:19 PM   sample:7 pwm:0.5780 asymmetry:-0.1169 tolerance:0.0086
3:19 PM   PID parameters: pid_Kp=16.538 pid_Ki=0.801 pid_Kd=85.375
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```
Note the `asymmetry` information. It provides an indication if the heater's
power is sufficient to ensure a symmetrical "heat up" versus "cool down /
heat loss" behavior. It should start positive and converge to zero.
A negative starting value indicates that the heat loss is faster than the heat
up, this means the system is asymmetrical. The calibration will still be
successful but reserves to counter disturbances might be low.

## Advanced / Manual Calibration

Many methods exist for calculating control parameters, such as Ziegler-Nichols,
Cohen-Coon, Kappa-Tau, Lambda, and many more. By default, classical
Ziegler-Nichols parameters are generated. If a user wants to experiment with
other flavors of Ziegler-Nichols, or Cohen-Coon parameters, they can extract the
constants from the log as seen below and enter them into this
[spreadsheet](resources/pid_params.xls).

```text
Ziegler-Nichols constants: Ku=0.103092 Tu=41.800000
Cohen-Coon constants: Km=-17.734845 Theta=6.600000 Tau=-10.182680
```

Classic Ziegler-Nichols parameters work in all scenarios. Cohen-Coon parameters
work better with systems that have a large amount of dead time/delay. For
example, if a printer has a bed with a large thermal mass that’s slow to heat
up and stabilize, the Cohen-Coon parameters will generally do a better job at
controlling it.

## Further Readings
### History

The first rudimentary PID controller was developed by Elmer Sperry in 1911 to
automate the control of a ship's rudder. Engineer Nicolas Minorsky published the
first mathematical analysis of a PID controller in 1922. In 1942, John Ziegler &
Nathaniel Nichols published their seminal paper, "Optimum Settings for Automatic
Controllers," which described a trial-and-error method for tuning a PID
controller, now commonly referred to as the "Ziegler-Nichols method.

In 1984, Karl Astrom and Tore Hagglund published their paper "Automatic Tuning
of Simple Regulators with Specifications on Phase and Amplitude Margins". In the
paper they introduced an automatic tuning method commonly referred to as the
"Astrom-Hagglund method" or the "relay method".

In 2019 Brandon Taysom & Carl Sorensen published their paper "Adaptive Relay
Autotuning under Static and Non-static Disturbances with Application to
Friction Stir Welding", which laid out a method to generate more accurate
results from a relay test. This is the PID calibration method currently used by
Kalico.

### Details of the Relay Test
As previously mentioned, Kalico uses a relay test for calibration purposes. A
standard relay test is conceptually simple. You turn the heater’s power on and
off to get it to oscillate about the target temperature, as seen in the
following graph.

![simple relay test](img/pid_01.png)

The above graph shows a common issue with a standard relay test. If the system
being calibrated has too much or too little power for the chosen target
temperature, it will produce biased and asymmetric results. As can be seen
above, the system spends more time in the off state than on and has a larger
amplitude above the target temperature than below.

In an ideal system, both the on and off times and the amplitude above and below
the target temperature would be the same. 3D printers don’t actively cool the
hot end or bed, so they can never reach the ideal state.

The following graph is a relay test based on the methodology laid out by
Taysom & Sorensen. After each iteration, the data is analyzed and a new maximum
power setting is calculated. As can be seen, the system starts the test
asymmetric but ends very symmetric.

![advanced relay test](img/pid_02.png)

Asymmetry can be monitored in real time during a calibration run. It can also
provide insight into how suitable the heater is for the current calibration
parameters. When asymmetry starts off positive and converges to zero, the
heater has more than enough power to achieve symmetry for the calibration
parameters.

```
3:12 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:15 PM   sample:1 pwm:1.0000 asymmetry:3.7519 tolerance:n/a
3:15 PM   sample:2 pwm:0.6229 asymmetry:0.3348 tolerance:n/a
3:16 PM   sample:3 pwm:0.5937 asymmetry:0.0840 tolerance:n/a
3:17 PM   sample:4 pwm:0.5866 asymmetry:0.0169 tolerance:0.4134
3:18 PM   sample:5 pwm:0.5852 asymmetry:0.0668 tolerance:0.0377
3:18 PM   sample:6 pwm:0.5794 asymmetry:0.0168 tolerance:0.0142
3:19 PM   sample:7 pwm:0.5780 asymmetry:-0.1169 tolerance:0.0086
3:19 PM   PID parameters: pid_Kp=16.538 pid_Ki=0.801 pid_Kd=85.375
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```

When asymmetry starts off negative, It will not converge to zero. If Kalico
does not error out, the calibration run will complete and provide good PID
parameters, However the heater is less likely to handle disturbances as well
as a heater with power in reserve.

```
3:36 PM   PID_CALIBRATE HEATER=extruder TARGET=220 TOLERANCE=0.01 WRITE_FILE=1
3:38 PM   sample:1 pwm:1.0000 asymmetry:-2.1149 tolerance:n/a
3:39 PM   sample:2 pwm:1.0000 asymmetry:-2.0140 tolerance:n/a
3:39 PM   sample:3 pwm:1.0000 asymmetry:-1.8811 tolerance:n/a
3:40 PM   sample:4 pwm:1.0000 asymmetry:-1.8978 tolerance:0.0000
3:40 PM   PID parameters: pid_Kp=21.231 pid_Ki=1.227 pid_Kd=91.826
               The SAVE_CONFIG command will update the printer config file
               with these parameters and restart the printer.
```

### Pid Control Algorithms

Kalico currently supports two control algorithms: Positional and Velocity.
The fundamental difference between the two algorithms is that the Positional
algorithm calculates what the PWM value should be for the current time
interval, and the Velocity algorithm calculates how much the previous PWM
setting should be changed to get the PWM value for the current time interval.

Positional is the default algorithm, as it will work in every scenario. The
Velocity algorithm can provide superior results to the Positional algorithm but
requires lower noise sensor readings, or a larger smoothing time setting.

The most noticeable difference between the two algorithms is that for the same
configuration parameters, velocity control will eliminate or drastically reduce
overshoot, as seen in the graphs below, as it isn’t susceptible to integral
wind-up.

![algorithm comparison](img/pid_03.png)

![zoomed algorithm comparison](img/pid_04.png)

In some scenarios Velocity control will also be better at holding the heater at
its target temperature, and rejecting disturbances. The primary reason for this
is that velocity control is more like a standard second order differential
equation. It takes into account position, velocity, and acceleration.
