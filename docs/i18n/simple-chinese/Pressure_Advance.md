# 压力前进

本文档提供有关为特定喷嘴和灯丝调整"压力前进"配置变量的信息。压力前进功能有助于减少渗出。有关压力前进如何实现的更多信息，请参阅[运动学](Kinematics.md)文档。

## 压力前进计算器

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-content{padding:20px}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-panel p.formula{background:var(--calc-result-bg);padding:8px 12px;border-radius:4px;font-family:monospace;font-size:.9em;color:var(--calc-text-light);margin:0 0 16px;border-left:3px solid var(--calc-primary)}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input,.rd-calc-field select{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus,.rd-calc-field select:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}.rd-calc-presets{display:flex;gap:8px;flex-wrap:wrap}.rd-calc-preset{background:var(--calc-tab-bg);border:1px solid var(--calc-border);padding:6px 12px;border-radius:4px;cursor:pointer;font-size:.85em;color:var(--calc-text);transition:all .2s}.rd-calc-preset:hover{border-color:var(--calc-primary);color:var(--calc-primary)}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    压力前进计算器
  </div>
  <div class="rd-calc-content">
    <h4>从测试塔计算压力前进值</h4>
    <p class="formula">pressure_advance = start + 测量高度 × factor</p>
    <div class="rd-calc-form">
      <div class="rd-calc-field">
        <label>预设</label>
        <div class="rd-calc-presets">
          <button class="rd-calc-preset" onclick="setPA(0,0.005)">直接驱动</button>
          <button class="rd-calc-preset" onclick="setPA(0,0.020)">波顿管</button>
          <button class="rd-calc-preset" onclick="setPA(0,0.001)">自定义 (0.001)</button>
        </div>
      </div>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>START 值</label>
          <input type="number" id="pa_start" value="0" step="any">
          <span class="hint">通常为0</span>
        </div>
        <div class="rd-calc-field">
          <label>FACTOR 值</label>
          <input type="number" id="pa_factor" value="0.005" step="any">
          <span class="hint">直接驱动=0.005，波顿管=0.020</span>
        </div>
      </div>
      <div class="rd-calc-field">
        <label>测量高度 (毫米)</label>
        <input type="number" id="pa_height" step="any" placeholder="例如: 12.90">
        <span class="hint">测试塔中最佳质量角的高度</span>
      </div>
      <button class="rd-calc-btn" onclick="calcPA()">计算</button>
      <div class="rd-calc-result" id="pa_result">
        <div class="label">压力前进值</div>
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

## 调整压力前进

压力前进做两件有用的事情——它减少非挤出移动期间的渗出，也减少转角过程中的blob现象。本指南使用第二个功能（减少转角过程中的blob现象）作为调整的机制。

为了校准压力前进，打印机必须配置并可操作，因为调整测试涉及打印和检查测试对象。在运行测试之前最好仔细阅读本文档。

使用切片机为在[docs/prints/square_tower.stl](prints/square_tower.stl)中找到的大空心正方形生成g代码。使用高速度（例如100mm/s）、零填充和粗糙层高（层高应约为喷嘴直径的75%）。确保在切片机中禁用任何"动态加速度控制"和"斜角接缝"。

通过发出以下G代码命令为测试做准备：
```
SET_VELOCITY_LIMIT SQUARE_CORNER_VELOCITY=1 ACCEL=500
```
此命令使喷嘴通过转角更慢地移动，以强调挤出机压力的影响。然后，对于具有直接驱动挤出机的打印机，运行命令：
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.005
```
对于长Bowden挤出机，使用：
```
TUNING_TOWER COMMAND=SET_PRESSURE_ADVANCE PARAMETER=ADVANCE START=0 FACTOR=.020
```
然后打印对象。完全打印后，测试打印看起来像：

![tuning_tower](img/tuning_tower.jpg)

上面的TUNING_TOWER命令指示Kalico在打印的每一层改变pressure_advance设置。打印中较高的层将设置较大的压力前进值。低于理想pressure_advance设置的层将在转角处出现blob，而高于理想设置的层可能导致转角处圆角和挤出质量下降。

如果观察到转角不再打印良好，可以提前取消打印（因此可以避免打印已知高于理想pressure_advance值的层）。

检查打印并使用数字卡尺找到转角质量最好的高度。如有疑问，选择较低的高度。

![tune_pa](img/tune_pa.jpg)

然后可以计算pressure_advance值为`pressure_advance = <start> + <measured_height> * <factor>`。（例如，`0 + 12.90 * .020`将是`.258`。）

如果这有助于确定最佳压力前进设置，可以为START和FACTOR选择自定义设置。执行此操作时，请确保在每次测试打印开始时发出TUNING_TOWER命令。

典型的压力前进值在0.050和1.000之间（高端通常仅对Bowden挤出机）。如果使用高达1.000的压力前进没有显著改进，则压力前进不太可能改进打印质量。返回压力前进禁用的默认配置。

尽管此调整练习直接改进转角的质量，但值得记住的是，良好的压力前进配置也会在整个打印中减少渗出。

完成此测试后，在配置文件的`[extruder]`部分中设置`pressure_advance = <calculated_value>`并发出RESTART命令。RESTART命令将清除测试状态并将加速度和转角速度返回到正常值。

## 重要注意事项

* 压力前进值取决于挤出机、喷嘴和灯丝。对于来自不同制造商或具有不同颜料的灯丝通常需要显著不同的压力前进值。因此，应该对每台打印机和每个灯丝线轴校准压力前进。

* 打印温度和挤出速率可能会影响压力前进。在调整压力前进之前，请务必调整[挤出机rotation_distance](Rotation_Distance.md#calibrating-rotation_distance-on-extruders)和[喷嘴温度](http://reprap.org/wiki/Triffid_Hunter%27s_Calibration_Guide#Nozzle_Temperature)。

* 测试打印设计为以高挤出机流速运行，但其他方面"正常"切片机设置。通过使用高打印速度（例如100mm/s）和粗糙层高（通常约为喷嘴直径的75%）来获得高流速。其他切片机设置应类似于其默认值（例如，2或3条线的周边、正常回抽量）。设置外周边速度与打印的其余部分相同可能会有用，但这不是必需的。

* 通常测试打印在每个转角上显示不同的行为。通常切片机会在一个转角处安排层变化，这可能导致该转角与其余三个转角明显不同。如果发生这种情况，请忽略该转角并使用其他三个转角调整压力前进。其余转角也通常略有变化。（这可能发生在打印机框架对某些方向转角的反应方式存在细微差异时。）尝试选择一个适用于所有其余转角的值。如有疑问，选择较低的压力前进值。

* 如果使用高压力前进值（例如超过0.200），您可能会发现在返回打印机的正常加速度时挤出机会打滑。压力前进系统通过在加速度期间推入额外灯丝并在减速期间缩回该灯丝来计算压力。对于高加速度和高压力前进，挤出机可能没有足够的扭矩来推动所需的灯丝。如果发生这种情况，要么使用较低的加速度值，要么禁用压力前进。

* 在Kalico中调整压力前进后，配置切片机中的小回抽值（例如0.75mm）并使用切片机的"回抽时擦拭选项"（如果可用）可能仍然很有用。这些切片机设置可能有助于抵消由灯丝内聚引起的渗出（灯丝由于塑料的粘性从喷嘴中拉出）。建议禁用切片机的"回抽时Z提升"选项。

* 压力前进系统不会改变工具头的定时或路径。启用压力前进的打印将花费与未启用压力前进的打印相同的时间。压力前进也不会改变打印期间挤出的灯丝总量。压力前进导致在移动加速度和减速度期间的额外挤出机运动。非常高的压力前进设置将导致加速度和减速度期间的大量挤出机运动，并且没有配置设置限制该运动的数量。