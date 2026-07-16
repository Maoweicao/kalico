# 歪斜纠正

基于软件的歪斜纠正可以帮助解决由于打印机组装不完全成正方形而导致的尺寸不准确。注意，如果您的打印机明显歪斜，强烈建议在应用基于软件的纠正之前，先采取机械手段使打印机尽可能成正方形。

## 歪斜纠正计算器

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-tabs{display:flex;flex-wrap:wrap;background:var(--calc-tab-bg);border-bottom:1px solid var(--calc-border);padding:0;margin:0}.rd-calc-tab{padding:10px 16px;cursor:pointer;border:none;background:transparent;color:var(--calc-text-light);font-size:.85em;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;white-space:nowrap}.rd-calc-tab:hover{color:var(--calc-primary);background:rgba(230,126,34,.05)}.rd-calc-tab.active{color:var(--calc-primary);border-bottom-color:var(--calc-primary);background:var(--calc-bg)}.rd-calc-content{padding:20px}.rd-calc-panel{display:none}.rd-calc-panel.active{display:block}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-tab{padding:8px 10px;font-size:.78em}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    歪斜纠正计算器
  </div>
  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="set">SET_SKEW</button>
    <button class="rd-calc-tab" data-tab="calc">CALC_MEASURED_SKEW</button>
  </div>
  <div class="rd-calc-content">
    <div class="rd-calc-panel active" data-panel="set">
      <h4>生成 SET_SKEW 命令</h4>
      <p>输入校准对象的测量长度以生成 SET_SKEW 命令。</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>XY 平面测量</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_xy_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_xy_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_xy_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <div class="rd-calc-field">
          <label>XZ 平面测量 (可选)</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_xz_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_xz_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_xz_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <div class="rd-calc-field">
          <label>YZ 平面测量 (可选)</label>
          <div class="rd-calc-row">
            <input type="number" id="skew_yz_ac" step="any" placeholder="AC (mm)">
            <input type="number" id="skew_yz_bd" step="any" placeholder="BD (mm)">
            <input type="number" id="skew_yz_ad" step="any" placeholder="AD (mm)">
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcSkew()">生成命令</button>
        <div class="rd-calc-result" id="set_result">
          <div class="label">SET_SKEW 命令</div>
          <div class="value" id="set_value" style="font-size:1em;word-break:break-all"></div>
        </div>
      </div>
    </div>
    <div class="rd-calc-panel" data-panel="calc">
      <h4>验证歪斜纠正</h4>
      <p>输入启用歪斜纠正后重新打印校准对象的测量值。</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>AC (mm)</label>
            <input type="number" id="skew_calc_ac" step="any" placeholder="例如: 140.2">
          </div>
          <div class="rd-calc-field">
            <label>BD (mm)</label>
            <input type="number" id="skew_calc_bd" step="any" placeholder="例如: 140.4">
          </div>
          <div class="rd-calc-field">
            <label>AD (mm)</label>
            <input type="number" id="skew_calc_ad" step="any" placeholder="例如: 100.0">
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcMeasuredSkew()">计算</button>
        <div class="rd-calc-result" id="calc_result">
          <div class="label">CALC_MEASURED_SKEW 命令</div>
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

## 打印校准对象

纠正歪斜的第一步是沿您要纠正的平面打印一个
[校准对象](https://www.thingiverse.com/thing:2563185/files)。
也有一个
[校准对象](https://www.thingiverse.com/thing:2972743)
包含一个模型中的所有平面。您希望对象的方向使得角A朝向平面的原点。

确保在此打印期间未应用歪斜纠正。您可以通过从printer.cfg中删除`[skew_correction]`模块或发出`SET_SKEW CLEAR=1`  gcode来执行此操作。

## 进行测量

`[skew_correction]`模块需要为您要纠正的每个平面进行3次测量；从角A到角C的长度、从角B到角D的长度以及从角A到角D的长度。测量长度AD时，不要包括某些测试对象提供的角上的平面。

![skew_lengths](img/skew_lengths.png)

## 配置您的歪斜

确保`[skew_correction]`在printer.cfg中。您现在可以使用`SET_SKEW` gcode来配置歪斜纠正。例如，如果您沿XY测量的长度如下：

```
Length AC = 140.4
Length BD = 142.8
Length AD = 99.8
```

可以使用`SET_SKEW`为XY平面配置歪斜纠正。

```
SET_SKEW XY=140.4,142.8,99.8
```
您还可以为XZ和YZ添加测量值到gcode：

```
SET_SKEW XY=140.4,142.8,99.8 XZ=141.6,141.4,99.8 YZ=142.4,140.5,99.5
```

`[skew_correction]`模块也支持类似于`[bed_mesh]`的配置文件管理。使用`SET_SKEW` gcode设置歪斜后，您可以使用`SKEW_PROFILE` gcode来保存它：

```
SKEW_PROFILE SAVE=my_skew_profile
```
执行此命令后，系统会提示您发出`SAVE_CONFIG` gcode以将配置文件保存到持久存储。如果不存在名为`my_skew_profile`的配置文件，则将创建一个新配置文件。如果指定的配置文件存在，它将被覆盖。

拥有保存的配置文件后，您可以加载它：
```
SKEW_PROFILE LOAD=my_skew_profile
```

也可以删除旧的或过时的配置文件：
```
SKEW_PROFILE REMOVE=my_skew_profile
```
删除配置文件后，系统会提示您发出`SAVE_CONFIG`以使此更改持久化。

## 验证您的纠正

配置歪斜纠正后，您可以重新打印启用纠正的校准件。使用以下gcode检查每个平面的歪斜。结果应低于通过`GET_CURRENT_SKEW`报告的结果。

```
CALC_MEASURED_SKEW AC=<ac_length> BD=<bd_length> AD=<ad_length>
```

## 注意事项

由于歪斜纠正的性质，建议在您的启动gcode中配置歪斜，在归位和任何类似吹气或喷嘴擦拭等接近打印区域边缘的运动之后。您可以使用`SET_SKEW`或`SKEW_PROFILE` gcodes来实现此目的。还建议在结束gcode中发出`SET_SKEW CLEAR=1`。

请记住，`[skew_correction]`可能会生成一个纠正，将工具移动到打印机在X和/或Y轴上的边界之外。建议在使用`[skew_correction]`时将零件排列在远离边缘的地方。