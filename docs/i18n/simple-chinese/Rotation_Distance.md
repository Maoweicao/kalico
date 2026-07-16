# 旋转距离

Kalico上的步进电机驱动器在每个
[步进配置部分](Config_Reference.md#stepper)中需要一个`rotation_distance`
参数。`rotation_distance`是轴通过步进电机的一次完整旋转所移动的距离。本文档描述了如何配置此值。

## 旋转距离计算器

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
    旋转距离计算器
  </div>

  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="steps">步数/毫米</button>
    <button class="rd-calc-tab" data-tab="stepdist">步进距离</button>
    <button class="rd-calc-tab" data-tab="belt">皮带轮</button>
    <button class="rd-calc-tab" data-tab="screw">丝杆</button>
    <button class="rd-calc-tab" data-tab="extruder">挤出机直径</button>
    <button class="rd-calc-tab" data-tab="calibrate">校准</button>
  </div>

  <div class="rd-calc-content">
    <!-- 步数/毫米计算器 -->
    <div class="rd-calc-panel active" data-panel="steps">
      <h4>从步数/毫米计算</h4>
      <p class="formula">rotation_distance = 全步数 × 微步数 / 步数每毫米</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>每转全步数</label>
            <input type="number" id="steps_full" value="200" min="1">
            <span class="hint">1.8°电机=200，0.9°电机=400</span>
          </div>
          <div class="rd-calc-field">
            <label>微步数</label>
            <input type="number" id="steps_micro" value="16" min="1">
            <span class="hint">大多数驱动器使用16</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>步数/毫米</label>
          <input type="number" id="steps_per_mm" step="any" placeholder="例如: 80">
        </div>
        <button class="rd-calc-btn" onclick="calcSteps()">计算</button>
        <div class="rd-calc-result" id="steps_result">
          <div class="label">旋转距离</div>
          <div class="value" id="steps_value"></div>
          <div class="config" id="steps_config"></div>
        </div>
      </div>
    </div>

    <!-- 步进距离计算器 -->
    <div class="rd-calc-panel" data-panel="stepdist">
      <h4>从步进距离计算</h4>
      <p class="formula">rotation_distance = 全步数 × 微步数 × 步进距离</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>每转全步数</label>
            <input type="number" id="stepdist_full" value="200" min="1">
            <span class="hint">1.8°电机=200，0.9°电机=400</span>
          </div>
          <div class="rd-calc-field">
            <label>微步数</label>
            <input type="number" id="stepdist_micro" value="16" min="1">
            <span class="hint">大多数驱动器使用16</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>步进距离 (毫米)</label>
          <input type="number" id="step_distance" step="any" placeholder="例如: 0.00625">
          <span class="hint">每步移动的距离（毫米）</span>
        </div>
        <button class="rd-calc-btn" onclick="calcStepDist()">计算</button>
        <div class="rd-calc-result" id="stepdist_result">
          <div class="label">旋转距离</div>
          <div class="value" id="stepdist_value"></div>
          <div class="config" id="stepdist_config"></div>
        </div>
      </div>
    </div>

    <!-- 皮带轮计算器 -->
    <div class="rd-calc-panel" data-panel="belt">
      <h4>皮带驱动轴</h4>
      <p class="formula">rotation_distance = 皮带齿距 × 滑轮齿数</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>皮带齿距 (毫米)</label>
            <input type="number" id="belt_pitch" value="2" step="any">
            <span class="hint">GT2皮带通常为2mm</span>
          </div>
          <div class="rd-calc-field">
            <label>滑轮齿数</label>
            <input type="number" id="belt_teeth" placeholder="例如: 20" min="1">
            <span class="hint">数电机滑轮上的齿数</span>
          </div>
        </div>
        <button class="rd-calc-btn" onclick="calcBelt()">计算</button>
        <div class="rd-calc-result" id="belt_result">
          <div class="label">旋转距离</div>
          <div class="value" id="belt_value"></div>
          <div class="config" id="belt_config"></div>
        </div>
      </div>
    </div>

    <!-- 丝杆计算器 -->
    <div class="rd-calc-panel" data-panel="screw">
      <h4>丝杆轴</h4>
      <p class="formula">rotation_distance = 螺距 × 线数</p>
      <div class="rd-calc-form">
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>螺距 (毫米)</label>
            <input type="number" id="screw_pitch" step="any" placeholder="例如: 2">
            <span class="hint">相邻螺纹之间的距离</span>
          </div>
          <div class="rd-calc-field">
            <label>线数</label>
            <input type="number" id="screw_threads" placeholder="例如: 4" min="1">
            <span class="hint">T8=4，M6/M8=1</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>常用预设</label>
          <select id="screw_preset" onchange="applyScrewPreset()">
            <option value="">-- 选择预设 --</option>
            <option value="2,4">T8 导螺杆 (螺距=2, 线数=4)</option>
            <option value="2,2">T4 导螺杆 (螺距=2, 线数=2)</option>
            <option value="1.25,1">M8 螺杆 (螺距=1.25, 线数=1)</option>
            <option value="1,1">M6 螺杆 (螺距=1, 线数=1)</option>
          </select>
        </div>
        <button class="rd-calc-btn" onclick="calcScrew()">计算</button>
        <div class="rd-calc-result" id="screw_result">
          <div class="label">旋转距离</div>
          <div class="value" id="screw_value"></div>
          <div class="config" id="screw_config"></div>
        </div>
      </div>
    </div>

    <!-- 挤出机直径计算器 -->
    <div class="rd-calc-panel" data-panel="extruder">
      <h4>挤出机（按齿轮直径）</h4>
      <p class="formula">rotation_distance = 直径 × π (3.14159)</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>挤出齿轮直径 (毫米)</label>
          <input type="number" id="extruder_dia" step="any" placeholder="例如: 7.3">
          <span class="hint">测量驱动齿轮的有效直径</span>
        </div>
        <button class="rd-calc-btn" onclick="calcExtruder()">计算</button>
        <div class="rd-calc-result" id="extruder_result">
          <div class="label">旋转距离（未计算齿轮比）</div>
          <div class="value" id="extruder_value"></div>
          <div class="config" id="extruder_config"></div>
        </div>
      </div>
    </div>

    <!-- 校准计算器 -->
    <div class="rd-calc-panel" data-panel="calibrate">
      <h4>挤出机校准（测量与修剪）</h4>
      <p class="formula">新rotation_distance = 旧值 × 实际距离 / 请求距离</p>
      <div class="rd-calc-form">
        <div class="rd-calc-field">
          <label>当前旋转距离</label>
          <input type="number" id="cal_prev_rd" step="any" placeholder="例如: 22.678">
          <span class="hint">您当前的rotation_distance设置</span>
        </div>
        <div class="rd-calc-row">
          <div class="rd-calc-field">
            <label>初始标记距离 (毫米)</label>
            <input type="number" id="cal_initial" step="any" placeholder="例如: 70">
            <span class="hint">挤出前挤出机到标记的距离</span>
          </div>
          <div class="rd-calc-field">
            <label>后续标记距离 (毫米)</label>
            <input type="number" id="cal_subsequent" step="any" placeholder="例如: 20">
            <span class="hint">挤出后挤出机到标记的距离</span>
          </div>
        </div>
        <div class="rd-calc-field">
          <label>请求挤出距离 (毫米)</label>
          <input type="number" id="cal_requested" value="50" step="any">
          <span class="hint">通常为50mm（按校准流程）</span>
        </div>
        <button class="rd-calc-btn" onclick="calcCalibrate()">计算</button>
        <div class="rd-calc-result" id="calibrate_result">
          <div class="label">新旋转距离</div>
          <div class="value" id="calibrate_value"></div>
          <div class="config" id="calibrate_config"></div>
          <div id="calibrate_warn" style="margin-top:8px;color:#e74c3c;font-size:0.85em;display:none;">
            ⚠ 实际挤出距离与请求距离相差超过2mm，建议重新校准。
          </div>
        </div>
      </div>
    </div>
  </div>

  <script>
    (function() {
      document.querySelectorAll('.rd-calc-tab').forEach(function(tab) {
        tab.addEventListener('click', function() {
          var container = this.closest('.rd-calc-container');
          container.querySelectorAll('.rd-calc-tab').forEach(function(t) { t.classList.remove('active'); });
          container.querySelectorAll('.rd-calc-panel').forEach(function(p) { p.classList.remove('active'); });
          this.classList.add('active');
          container.querySelector('[data-panel="' + this.dataset.tab + '"]').classList.add('active');
        });
      });

      function showResult(resultId, valueId, configId, value, configText) {
        document.getElementById(valueId).textContent = value;
        document.getElementById(configId).textContent = 'rotation_distance: ' + configText;
        document.getElementById(resultId).classList.add('show');
      }

      window.calcSteps = function() {
        var full = parseFloat(document.getElementById('steps_full').value);
        var micro = parseFloat(document.getElementById('steps_micro').value);
        var spm = parseFloat(document.getElementById('steps_per_mm').value);
        if (isNaN(full) || isNaN(micro) || isNaN(spm) || spm === 0) return;
        var rd = (full * micro) / spm;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('steps_result', 'steps_value', 'steps_config', rounded.toFixed(3), rounded.toFixed(3));
      };

      window.calcStepDist = function() {
        var full = parseFloat(document.getElementById('stepdist_full').value);
        var micro = parseFloat(document.getElementById('stepdist_micro').value);
        var sd = parseFloat(document.getElementById('step_distance').value);
        if (isNaN(full) || isNaN(micro) || isNaN(sd)) return;
        var rd = full * micro * sd;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('stepdist_result', 'stepdist_value', 'stepdist_config', rounded.toFixed(3), rounded.toFixed(3));
      };

      window.calcBelt = function() {
        var pitch = parseFloat(document.getElementById('belt_pitch').value);
        var teeth = parseFloat(document.getElementById('belt_teeth').value);
        if (isNaN(pitch) || isNaN(teeth)) return;
        var rd = pitch * teeth;
        showResult('belt_result', 'belt_value', 'belt_config', rd.toFixed(1), rd.toFixed(1));
      };

      window.calcScrew = function() {
        var pitch = parseFloat(document.getElementById('screw_pitch').value);
        var threads = parseFloat(document.getElementById('screw_threads').value);
        if (isNaN(pitch) || isNaN(threads)) return;
        var rd = pitch * threads;
        showResult('screw_result', 'screw_value', 'screw_config', rd.toFixed(2), rd.toFixed(2));
      };

      window.applyScrewPreset = function() {
        var val = document.getElementById('screw_preset').value;
        if (!val) return;
        var parts = val.split(',');
        document.getElementById('screw_pitch').value = parts[0];
        document.getElementById('screw_threads').value = parts[1];
      };

      window.calcExtruder = function() {
        var dia = parseFloat(document.getElementById('extruder_dia').value);
        if (isNaN(dia)) return;
        var rd = dia * Math.PI;
        var rounded = Math.round(rd * 1000) / 1000;
        showResult('extruder_result', 'extruder_value', 'extruder_config', rounded.toFixed(3), rounded.toFixed(3));
      };

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

## 从steps_per_mm（或step_distance）获取rotation_distance

您的3D打印机的设计人员最初从旋转距离计算了`steps_per_mm`。如果您知道steps_per_mm，则可以使用此通用公式获取原始旋转距离：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> / <steps_per_mm>
```

或者，如果您有较旧的Kalico配置并知道`step_distance`参数，您可以使用此公式：
```
rotation_distance = <full_steps_per_rotation> * <microsteps> * <step_distance>
```

`<full_steps_per_rotation>`设置由步进电机的类型决定。大多数步进电机是"1.8度步进器"，因此每旋转200个完整步长（360除以1.8等于200）。一些步进电机是"0.9度步进器"，因此每旋转400个完整步长。其他步进电机很少见。如果不确定，不要在配置文件中设置full_steps_per_rotation，在上面的公式中使用200。

`<microsteps>`设置由步进电机驱动器决定。大多数驱动器使用16个微步。如果不确定，在配置中设置`microsteps: 16`并在上面的公式中使用16。

几乎所有打印机在X、Y和Z类型轴上应该有一个整数的`rotation_distance`。如果上面的公式导致rotation_distance在整数的0.01以内，则将最终值舍入到该整数。

## 在挤出机上校准rotation_distance

在挤出机上，`rotation_distance`是灯丝通过步进电机一次完全旋转所行进的距离。获得此设置准确值的最佳方法是使用"测量和修剪"程序。

首先从rotation distance的初始猜测开始。这可以从
[steps_per_mm](#obtaining-rotation_distance-from-steps_per_mm-or-step_distance)
获得，也可以通过[检查硬件](#extruder)获得。

然后使用以下程序来"测量和修剪"：
1. 确保挤出机中有灯丝，热端加热到适当的温度，打印机准备好挤出。
2. 使用标记笔在挤出机体的进口周围约70mm处在灯丝上放置一个标记。然后使用数字卡尺尽可能精确地测量该标记的实际距离。将其记为`<initial_mark_distance>`。
3. 使用以下命令序列挤出50mm灯丝：`G91`，然后是`G1 E50 F60`。将50mm记为`<requested_extrude_distance>`。等待挤出机完成移动（需要约50秒）。对此测试使用缓慢的挤出速率很重要，因为更快的速率会导致挤出机中的高压力，这会歪斜结果。（不要对此测试使用图形前端上的"挤出按钮"，因为它们以快速速率挤出。）
4. 使用数字卡尺测量挤出机体和灯丝上的标记之间的新距离。将其记为`<subsequent_mark_distance>`。然后计算：
   `actual_extrude_distance = <initial_mark_distance> - <subsequent_mark_distance>`
5. 计算rotation_distance为：
   `rotation_distance = <previous_rotation_distance> * <actual_extrude_distance> / <requested_extrude_distance>`
   将新的rotation_distance舍入到三位小数。

如果actual_extrude_distance与requested_extrude_distance相差超过约2mm，则是一个好主意再次执行上述步骤。

注意：请*不要*使用"测量和修剪"类型的方法来校准x、y或z类型轴。"测量和修剪"方法对于这些轴的准确性不够，可能会导致更差的配置。相反，如果需要，那些轴可以通过[测量皮带、滑轮和丝杆硬件](#obtaining-rotation_distance-by-inspecting-the-hardware)来确定。

## 通过检查硬件获取rotation_distance

可以通过了解步进电机和打印机运动学来计算rotation_distance。如果不知道steps_per_mm或设计新打印机，这可能很有用。

### 皮带驱动的轴

对于使用皮带和滑轮的线性轴，计算rotation_distance很容易。

首先确定皮带的类型。大多数打印机使用2mm皮带间距（即皮带上的每个齿相距2mm）。然后计算步进电机滑轮上的齿数。然后计算rotation_distance为：
```
rotation_distance = <belt_pitch> * <number_of_teeth_on_pulley>
```

例如，如果打印机具有2mm皮带并使用具有20个齿的滑轮，则旋转距离为40。

### 具有丝杆的轴

使用以下公式可以轻松计算常见丝杆的rotation_distance：
```
rotation_distance = <screw_pitch> * <number_of_separate_threads>
```

例如，常见的"T8导螺杆"的旋转距离为8（间距为2mm，有4个单独的螺纹）。

较旧的打印机带有"螺纹杆"，导螺杆上只有一个"螺纹"，因此旋转距离是螺杆的间距。（螺杆间距是螺杆上每个凹槽之间的距离。）例如，M6公制棒的旋转距离为1，M8棒的旋转距离为1.25。

### 挤出机

通过测量推动灯丝的"爱好螺栓"的直径，可以获得挤出机的初始旋转距离，并使用以下公式：`rotation_distance = <diameter> * 3.14`

如果挤出机使用齿轮，则还需要[为挤出机确定并设置gear_ratio](#using-a-gear_ratio)。

挤出机上的实际旋转距离会因打印机而异，因为与灯丝啮合的"爱好螺栓"的抓握力可能会变化。它甚至可以在灯丝线轴之间变化。获得初始rotation_distance后，使用[测量和修剪程序](#calibrating-rotation_distance-on-extruders)来获得更准确的设置。

## 使用gear_ratio

设置`gear_ratio`可以更容易地在具有齿轮箱（或类似物）的步进器上配置`rotation_distance`。大多数步进器都没有齿轮箱——如果不确定，则不要在配置中设置`gear_ratio`。

设置`gear_ratio`时，`rotation_distance`表示轴通过齿轮箱上的最后一个齿轮的一次完全旋转所移动的距离。例如，如果使用具有"5:1"比率的齿轮箱，可以使用[硬件知识](#obtaining-rotation_distance-by-inspecting-the-hardware)计算rotation_distance，然后将`gear_ratio: 5:1`添加到配置中。

对于通过皮带和滑轮实现的齿轮传动，可以通过计算滑轮上的齿数来确定gear_ratio。例如，如果带有16个齿的步进器驱动下一个带有80个齿的滑轮，则使用`gear_ratio: 80:16`。事实上，可以打开普通现成的"齿轮箱"并计算其中的齿数来确认其齿轮比。

注意，有时齿轮箱的齿轮比与其宣传的略有不同。常见的BMG挤出机齿轮就是这样一个例子——它们被宣传为"3:1"，但实际上使用"50:17"齿轮。（使用没有公分母的齿数可能会改进整体齿轮磨损，因为齿不总是以相同方式啮合。）常见的"5.18:1行星齿轮箱"可以更准确地配置为`gear_ratio: 57:11`。

如果在轴上使用了多个齿轮，则可以为gear_ratio提供逗号分隔的列表。例如，"5:1"齿轮箱驱动16齿到80齿滑轮可以使用`gear_ratio: 5:1, 80:16`。

在大多数情况下，gear_ratio应该用整数定义，因为常见的齿轮和滑轮上有整数个齿。但是，在皮带使用摩擦而不是齿来驱动滑轮的情况下，在齿轮比中使用浮点数可能是有意义的（例如，`gear_ratio: 107.237:16`）。