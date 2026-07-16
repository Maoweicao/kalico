# Skew correction

Software based skew correction can help resolve dimensional inaccuracies
resulting from a printer assembly that is not perfectly square.  Note
that if your printer is significantly skewed it is strongly recommended to
first use mechanical means to get your printer as square as possible prior
to applying software based correction.

## Skew Correction Calculator

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-tabs{display:flex;flex-wrap:wrap;background:var(--calc-tab-bg);border-bottom:1px solid var(--calc-border);padding:0;margin:0}.rd-calc-tab{padding:10px 16px;cursor:pointer;border:none;background:transparent;color:var(--calc-text-light);font-size:.85em;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;white-space:nowrap}.rd-calc-tab:hover{color:var(--calc-primary);background:rgba(230,126,34,.05)}.rd-calc-tab.active{color:var(--calc-primary);border-bottom-color:var(--calc-primary);background:var(--calc-bg)}.rd-calc-content{padding:20px}.rd-calc-panel{display:none}.rd-calc-panel.active{display:block}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-tab{padding:8px 10px;font-size:.78em}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    Skew Correction Calculator
  </div>
  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="set">SET_SKEW</button>
    <button class="rd-calc-tab" data-tab="calc">CALC_MEASURED_SKEW</button>
  </div>
  <div class="rd-calc-content">
    <!-- SET_SKEW Command Generator -->
    <div class="rd-calc-panel active" data-panel="set">
      <h4>Generate SET_SKEW Command</h4>
      <p>Enter measured lengths from the calibration object to generate the SET_SKEW command.</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>XY Plane Measurements</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_xy_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_xy_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_xy_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <div class="rd-calc-field">
          <label>XZ Plane Measurements (optional)</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_xz_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_xz_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_xz_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <div class="rd-calc-field">
          <label>YZ Plane Measurements (optional)</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_yz_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_yz_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_yz_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcSkew()">Generate Command</button>
        <div class="rd-calc-result" id="set_result">
          <div class="label">SET_SKEW Command</div>
          <div class="value" id="set_value" style="font-size:1em;word-break:break-all"></div>
        </div>
      </div>
    </div>
    <!-- CALC_MEASURED_SKEW -->
    <div class="rd-calc-panel" data-panel="calc">
      <h4>Verify Skew Correction</h4>
      <p>Enter measurements from reprinting the calibration object with skew correction enabled.</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>AC (mm)</label>
            <input type="number" id="skew_calc_ac" step="any" placeholder="e.g. 140.2">
          </div>
          <div class="rd-calc-field">
            <label>BD (mm)</label>
            <input type="number" id="skew_calc_bd" step="any" placeholder="e.g. 140.4">
          </div>
          <div class="rd-calc-field">
            <label>AD (mm)</label>
            <input type="number" id="skew_calc_ad" step="any" placeholder="e.g. 100.0">
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcMeasuredSkew()">Calculate</button>
        <div class="rd-calc-result" id="calc_result">
          <div class="label">CALC_MEASURED_SKEW Command</div>
          <div class="value" id="calc_value" style="font-size:1em;word-break:break-all"></div>
        </div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      document.querySelectorAll('.rd-calc-tab').forEach(function(t){t.addEventListener('click',function(){var c=this.closest('.rd-calc-container');c.querySelectorAll('.rd-calc-tab').forEach(function(x){x.classList.remove('active')});c.querySelectorAll('.rd-calc-panel').forEach(function(x){x.classList.remove('active')});this.classList.add('active');c.querySelector('[data-panel="'+this.dataset.tab+'"]').classList.add('active')})});
      window.calcSkew=function(){var cmd='SET_SKEW';var xy_ac=parseFloat(document.getElementById('skew_xy_ac').value);var xy_bd=parseFloat(document.getElementById('skew_xy_bd').value);var xy_ad=parseFloat(document.getElementById('skew_xy_ad').value);if(!isNaN(xy_ac)&&!isNaN(xy_bd)&&!isNaN(xy_ad))cmd+=' XY='+xy_ac+','+xy_bd+','+xy_ad;var xz_ac=parseFloat(document.getElementById('skew_xz_ac').value);var xz_bd=parseFloat(document.getElementById('skew_xz_bd').value);var xz_ad=parseFloat(document.getElementById('skew_xz_ad').value);if(!isNaN(xz_ac)&&!isNaN(xz_bd)&&!isNaN(xz_ad))cmd+=' XZ='+xz_ac+','+xz_bd+','+xz_ad;var yz_ac=parseFloat(document.getElementById('skew_yz_ac').value);var yz_bd=parseFloat(document.getElementById('skew_yz_bd').value);var yz_ad=parseFloat(document.getElementById('skew_yz_ad').value);if(!isNaN(yz_ac)&&!isNaN(yz_bd)&&!isNaN(yz_ad))cmd+=' YZ='+yz_ac+','+yz_bd+','+yz_ad;document.getElementById('set_value').textContent=cmd;document.getElementById('set_result').classList.add('show')};
      window.calcMeasuredSkew=function(){var ac=parseFloat(document.getElementById('skew_calc_ac').value);var bd=parseFloat(document.getElementById('skew_calc_bd').value);var ad=parseFloat(document.getElementById('skew_calc_ad').value);if(isNaN(ac)||isNaN(bd)||isNaN(ad))return;document.getElementById('calc_value').textContent='CALC_MEASURED_SKEW AC='+ac+' BD='+bd+' AD='+ad;document.getElementById('calc_result').classList.add('show')};
      document.querySelectorAll('.rd-calc-field input').forEach(function(i){i.addEventListener('keypress',function(e){if(e.key==='Enter'){var b=this.closest('.rd-calc-panel').querySelector('.rd-calc-btn');if(b)b.click()}})});
    })();
  </script>
</div>

## Print a Calibration Object

The first step in correcting skew is to print a
[calibration object](https://www.thingiverse.com/thing:2563185/files)
along the plane you want to correct.  There is also a
[calibration object](https://www.thingiverse.com/thing:2972743)
that includes all planes in one model.  You want the object oriented
so that corner A is toward the origin of the plane.

Make sure that no skew correction is applied during this print.  You may
do this by either removing the `[skew_correction]` module from printer.cfg
or by issuing a `SET_SKEW CLEAR=1` gcode.

## Take your measurements

The `[skew_correction]` module requires 3 measurements for each plane you want
to correct; the length from Corner A to Corner C, the length from Corner B
to Corner D, and the length from Corner A to Corner D.  When measuring length
AD do not include the flats on the corners that some test objects provide.

![skew_lengths](img/skew_lengths.png)

## Configure your skew

Make sure `[skew_correction]` is in printer.cfg.  You may now use the `SET_SKEW`
gcode to configure skew_correcton.  For example, if your measured lengths
along XY are as follows:

```
Length AC = 140.4
Length BD = 142.8
Length AD = 99.8
```

`SET_SKEW` can be used to configure skew correction for the XY plane.

```
SET_SKEW XY=140.4,142.8,99.8
```
You may also add measurements for XZ and YZ to the gcode:

```
SET_SKEW XY=140.4,142.8,99.8 XZ=141.6,141.4,99.8 YZ=142.4,140.5,99.5
```

The `[skew_correction]` module also supports profile management in a manner
similar to `[bed_mesh]`.  After setting skew using the `SET_SKEW` gcode,
you may use the `SKEW_PROFILE` gcode to save it:

```
SKEW_PROFILE SAVE=my_skew_profile
```
After this command you will be prompted to issue a `SAVE_CONFIG` gcode to
save the profile to persistent storage.  If no profile is named
`my_skew_profile` then a new profile will be created.  If the named profile
exists it will be overwritten.

Once you have a saved profile, you may load it:
```
SKEW_PROFILE LOAD=my_skew_profile
```

It is also possible to remove an old or out of date profile:
```
SKEW_PROFILE REMOVE=my_skew_profile
```
After removing a profile you will be prompted to issue a `SAVE_CONFIG` to
make this change persist.

## Verifying your correction

After skew_correction has been configured you may reprint the calibration
part with correction enabled.  Use the following gcode to check your
skew on each plane.  The results should be lower than those reported via
`GET_CURRENT_SKEW`.

```
CALC_MEASURED_SKEW AC=<ac_length> BD=<bd_length> AD=<ad_length>
```

## Caveats

Due to the nature of skew correction it is recommended to configure skew
in your start gcode, after homing and any kind of movement that travels
near the edge of the print area such as a purge or nozzle wipe.   You may
use use the `SET_SKEW` or `SKEW_PROFILE` gcodes to accomplish this.  It is
also recommended to issue a `SET_SKEW CLEAR=1` in your end gcode.

Keep in mind that it is possible for `[skew_correction]` to generate a correction
that moves the tool beyond the printer's boundaries on the X and/or Y axes.  It
is recommended to arrange parts away from the edges when using
`[skew_correction]`.
