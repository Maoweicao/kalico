
# PID

PID 控制是 3D 打印世界中广泛使用的控制方法。当涉及温度控制时它无处不在，无论是使用加热器产生热量还是使用风扇移除热量。本文档旨在提供 PID 是什么以及如何在 Kalico 中最好地使用它的高级概述。

## PID 参数计算器

<div class="rd-calc-container">
  <style>
    .rd-calc-container{--calc-primary:#e67e22;--calc-primary-hover:#d35400;--calc-bg:#fff;--calc-border:#ddd;--calc-text:#333;--calc-text-light:#666;--calc-result-bg:#f8f9fa;--calc-tab-bg:#f1f1f1;--calc-success:#27ae60}[data-md-color-scheme="slate"] .rd-calc-container,[data-md-color-mode="dark"] .rd-calc-container{--calc-bg:#2d2d2d;--calc-border:#444;--calc-text:#e0e0e0;--calc-text-light:#aaa;--calc-result-bg:#383838;--calc-tab-bg:#363636}.rd-calc-container *{box-sizing:border-box}.rd-calc-container{background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:8px;padding:0;margin:1.5em 0;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.08)}.rd-calc-header{background:var(--calc-primary);color:#fff;padding:12px 20px;font-size:1.1em;font-weight:600;display:flex;align-items:center;gap:8px}.rd-calc-header svg{width:20px;height:20px;fill:currentColor}.rd-calc-tabs{display:flex;flex-wrap:wrap;background:var(--calc-tab-bg);border-bottom:1px solid var(--calc-border);padding:0;margin:0}.rd-calc-tab{padding:10px 16px;cursor:pointer;border:none;background:transparent;color:var(--calc-text-light);font-size:.85em;font-weight:500;transition:all .2s;border-bottom:2px solid transparent;white-space:nowrap}.rd-calc-tab:hover{color:var(--calc-primary);background:rgba(230,126,34,.05)}.rd-calc-tab.active{color:var(--calc-primary);border-bottom-color:var(--calc-primary);background:var(--calc-bg)}.rd-calc-content{padding:20px}.rd-calc-panel{display:none}.rd-calc-panel.active{display:block}.rd-calc-panel h4{margin:0 0 8px;color:var(--calc-text);font-size:1em}.rd-calc-panel p.formula{background:var(--calc-result-bg);padding:8px 12px;border-radius:4px;font-family:monospace;font-size:.9em;color:var(--calc-text-light);margin:0 0 16px;border-left:3px solid var(--calc-primary)}.rd-calc-form{display:grid;gap:12px}.rd-calc-field{display:grid;gap:4px}.rd-calc-field label{font-size:.85em;color:var(--calc-text-light);font-weight:500}.rd-calc-field input,.rd-calc-field select{padding:8px 12px;border:1px solid var(--calc-border);border-radius:4px;font-size:.95em;background:var(--calc-bg);color:var(--calc-text);transition:border-color .2s}.rd-calc-field input:focus,.rd-calc-field select:focus{outline:none;border-color:var(--calc-primary);box-shadow:0 0 0 2px rgba(230,126,34,.2)}.rd-calc-field .hint{font-size:.75em;color:var(--calc-text-light);margin-top:2px}.rd-calc-btn{background:var(--calc-primary);color:#fff;border:none;padding:10px 20px;border-radius:4px;font-size:.95em;font-weight:600;cursor:pointer;transition:background .2s;justify-self:start}.rd-calc-btn:hover{background:var(--calc-primary-hover)}.rd-calc-result{margin-top:16px;padding:12px 16px;background:var(--calc-result-bg);border-radius:4px;display:none}.rd-calc-result.show{display:block}.rd-calc-result .label{font-size:.8em;color:var(--calc-text-light);margin-bottom:4px}.rd-calc-result .value{font-size:1.4em;font-weight:700;color:var(--calc-success);font-family:monospace}.rd-calc-result .config{margin-top:8px;padding:8px 12px;background:var(--calc-bg);border:1px solid var(--calc-border);border-radius:4px;font-family:monospace;font-size:.85em;color:var(--calc-text);user-select:all}.rd-calc-row{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:480px){.rd-calc-row{grid-template-columns:1fr}.rd-calc-tab{padding:8px 10px;font-size:.78em}.rd-calc-content{padding:16px}}</style>
  <div class="rd-calc-header">
    <svg viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-7 14c-3.31 0-6-2.69-6-6s2.69-6 6-6 6 2.69 6 6-2.69 6-6 6zm3-6c0 1.66-1.34 3-3 3s-3-1.34-3-3 1.34-3 3-3 3 1.34 3 3z"/></svg>
    PID 参数计算器
  </div>
  <div class="rd-calc-tabs">
    <button class="rd-calc-tab active" data-tab="zn">Ziegler-Nichols</button>
    <button class="rd-calc-tab" data-tab="cc">Cohen-Coon</button>
  </div>
  <div class="rd-calc-content">
    <div class="rd-calc-panel active" data-panel="zn">
      <h4>Ziegler-Nichols PID 计算器</h4>
      <p class="formula">从 PID_CALIBRATE 日志中提取 Ku 和 Tu</p>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>Ku (终极增益)</label>
          <input type="number" id="pid_ku" step="any" placeholder="例如: 0.103092">
          <span class="hint">来自日志中的"Ziegler-Nichols constants"</span>
        </div>
        <div class="rd-calc-field">
          <label>Tu (终极周期)</label>
          <input type="number" id="pid_tu" step="any" placeholder="例如: 41.8">
          <span class="hint">来自日志中的"Ziegler-Nichols constants"</span>
        </div>
      </div>
      <button class="rd-calc-btn" onclick="calcZN()">计算</button>
      <div class="rd-calc-result" id="zn_result">
        <div class="label">PID 参数 (Ziegler-Nichols 变体)</div>
        <div class="value" id="zn_value" style="font-size:1em;line-height:1.8"></div>
        <div class="config" id="zn_config"></div>
      </div>
    </div>
    <div class="rd-calc-panel" data-panel="cc">
      <h4>Cohen-Coon PID 计算器</h4>
      <p class="formula">从 PID_CALIBRATE 日志中提取 Km、Theta 和 Tau</p>
      <div class="rd-calc-row">
        <div class="rd-calc-field">
          <label>Km (过程增益)</label>
          <input type="number" id="pid_km" step="any" placeholder="例如: -17.734845">
          <span class="hint">来自日志中的"Cohen-Coon constants"</span>
        </div>
        <div class="rd-calc-field">
          <label>Theta (死区时间)</label>
          <input type="number" id="pid_theta" step="any" placeholder="例如: 6.6">
          <span class="hint">来自日志中的"Cohen-Coon constants"</span>
        </div>
      </div>
      <div class="rd-calc-field">
        <label>Tau (时间常数)</label>
        <input type="number" id="pid_tau" step="any" placeholder="例如: -10.182680">
        <span class="hint">来自日志中的"Cohen-Coon constants"</span>
      </div>
      <button class="rd-calc-btn" onclick="calcCC()">计算</button>
      <div class="rd-calc-result" id="cc_result">
        <div class="label">PID 参数 (Cohen-Coon)</div>
        <div class="value" id="cc_value" style="font-size:1em;line-height:1.8"></div>
        <div class="config" id="cc_config"></div>
      </div>
    </div>
  </div>
  <script>
    (function(){
      document.querySelectorAll('.rd-calc-tab').forEach(function(t){t.addEventListener('click',function(){var c=this.closest('.rd-calc-container');c.querySelectorAll('.rd-calc-tab').forEach(function(x){x.classList.remove('active')});c.querySelectorAll('.rd-calc-panel').forEach(function(x){x.classList.remove('active')});this.classList.add('active');c.querySelector('[data-panel="'+this.dataset.tab+'"]').classList.add('active')})});
      window.calcZN=function(){var ku=parseFloat(document.getElementById('pid_ku').value);var tu=parseFloat(document.getElementById('pid_tu').value);if(isNaN(ku)||isNaN(tu))return;var classic={kp:0.6*ku,ki:1.2*ku/tu,kd:0.075*ku*tu};var p={kp:0.5*ku,ki:0,kd:0};var pi={kp:0.45*ku,ki:0.54*ku/tu,kd:0};var pid={kp:0.6*ku,ki:1.2*ku/tu,kd:0.075*ku*tu};var some={kp:0.33*ku,ki:0.66*ku/tu,kd:0.11*ku*tu};var html='<b>经典:</b> Kp='+classic.kp.toFixed(3)+' Ki='+classic.ki.toFixed(3)+' Kd='+classic.kd.toFixed(3)+'<br><b>仅P:</b> Kp='+p.kp.toFixed(3)+'<br><b>PI:</b> Kp='+pi.kp.toFixed(3)+' Ki='+pi.ki.toFixed(3)+'<br><b>PID:</b> Kp='+pid.kp.toFixed(3)+' Ki='+pid.ki.toFixed(3)+' Kd='+pid.kd.toFixed(3)+'<br><b>无超调:</b> Kp='+some.kp.toFixed(3)+' Ki='+some.ki.toFixed(3)+' Kd='+some.kd.toFixed(3);document.getElementById('zn_value').innerHTML=html;document.getElementById('zn_config').textContent='pid_Kp='+pid.kp.toFixed(3)+' pid_Ki='+pid.ki.toFixed(3)+' pid_Kd='+pid.kd.toFixed(3);document.getElementById('zn_result').classList.add('show')};
      window.calcCC=function(){var km=parseFloat(document.getElementById('pid_km').value);var theta=parseFloat(document.getElementById('pid_theta').value);var tau=parseFloat(document.getElementById('pid_tau').value);if(isNaN(km)||isNaN(theta)||isNaN(tau))return;var r=theta/tau;var kp=(1/(km*r))*(1+r/3);var ki=kp/(theta*(32+6*r)/(13+8*r));var kd=kp*theta*4/(11+2*r);document.getElementById('cc_value').innerHTML='<b>Cohen-Coon:</b><br>Kp='+kp.toFixed(3)+'<br>Ki='+ki.toFixed(3)+'<br>Kd='+kd.toFixed(3);document.getElementById('cc_config').textContent='pid_Kp='+kp.toFixed(3)+' pid_Ki='+ki.toFixed(3)+' pid_Kd='+kd.toFixed(3);document.getElementById('cc_result').classList.add('show')};
      document.querySelectorAll('.rd-calc-field input').forEach(function(i){i.addEventListener('keypress',function(e){if(e.key==='Enter'){var b=this.closest('.rd-calc-panel').querySelector('.rd-calc-btn');if(b)b.click()}})});
    })();
  </script>
</div>

## PID 校准
### 准备校准
执行校准测试时应最小化外部影响：
* 关闭辅助风扇
* 关闭室加热器
* 校准床面时关闭挤出机加热器，反之亦然
* 避免外部干扰，如气流等。

比上面列出的更重要的是，**PID 如何打印**。如果在打印时打开部分风扇，使用打开部分风扇的 PID 调整。

### 选择正确的 PID 算法
Kalico 提供两种不同的 PID 算法：位置型和速度型

* 位置型（`pid`）
    * 标准算法
    * 对嘈杂的温度读数非常稳健
    * 可能导致超调
    * 在边界情况下目标控制不足
* 速度型（`pid_v`）
    * 没有超调
    * 在某些场景中更好的目标控制
    * 对嘈杂传感器更敏感
    * 可能需要更大的平滑时间常数

参考[配置参考](Config_Reference.md#extruder)中的[控制语句](Config_Reference.md#extruder)。

### 运行 PID 校准
PID 校准通过 [PID_CALIBRATE](G-Codes.md#pid_calibrate) 命令调用。此命令将加热相应的加热器并让其在多个周期中围绕目标温度冷却，以确定所需的参数。

这样的校准周期看起来像以下片段：
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
注意 `asymmetry` 信息。它提供了加热器的功率是否足以确保对称"加热"与"冷却/热损失"行为的指示。它应该开始为正并收敛到零。负起始值表示热损失比加热快，这意味着系统不对称。校准仍然会成功，但应对干扰的保留可能很低。

## 高级/手动校准

许多方法存在于计算控制参数中，例如 Ziegler-Nichols、Cohen-Coon、Kappa-Tau、Lambda 等。默认情况下，生成经典 Ziegler-Nichols 参数。如果用户想尝试 Ziegler-Nichols 的其他风味或 Cohen-Coon 参数，可以从如下所示的日志中提取常数并将其输入到此[电子表格](resources/pid_params.xls)中。

```text
Ziegler-Nichols constants: Ku=0.103092 Tu=41.800000
Cohen-Coon constants: Km=-17.734845 Theta=6.600000 Tau=-10.182680
```

经典 Ziegler-Nichols 参数在所有场景中都有效。Cohen-Coon 参数对具有大量死时间/延迟的系统效果更好。例如，如果打印机有一个具有大热质量的床面，加热和稳定缓慢，Cohen-Coon 参数通常会更好地进行控制。

## 进一步阅读
### 历史

第一个原始 PID 控制器由 Elmer Sperry 在 1911 年开发，用于自动控制船舵。工程师 Nicolas Minorsky 在 1922 年发表了对 PID 控制器的第一个数学分析。1942 年，John Ziegler 和 Nathaniel Nichols 发表了他们的开创性论文"Optimum Settings for Automatic Controllers"，描述了一种试错法来调整 PID 控制器，现在通常称为"Ziegler-Nichols 方法"。

1984 年，Karl Astrom 和 Tore Hagglund 发表了论文"Automatic Tuning of Simple Regulators with Specifications on Phase and Amplitude Margins"。在论文中，他们引入了一种自动调整方法，通常称为"Astrom-Hagglund 方法"或"继电器方法"。

2019 年，Brandon Taysom 和 Carl Sorensen 发表了论文"Adaptive Relay Autotuning under Static and Non-static Disturbances with Application to Friction Stir Welding"，该论文列出了一种从继电器测试生成更准确结果的方法。这是 Kalico 目前使用的 PID 校准方法。

### 继电器测试的详情
如前所述，Kalico 使用继电器测试进行校准。标准继电器测试在概念上很简单。打开和关闭加热器的电源以使其围绕目标温度振荡，如下图所示。

![simple relay test](img/pid_01.png)

上面的图表显示了标准继电器测试的常见问题。如果正在校准的系统对于选定的目标温度功率过多或过少，将产生有偏和不对称的结果。如上所示，系统在关闭状态下花费的时间比开启状态多，目标温度上方的振幅比下方的振幅大。

在理想系统中，打开和关闭时间以及目标温度上方和下方的振幅都将相同。3D 打印机不会主动冷却热端或床面，所以它们永远无法达到理想状态。

下面的图表是基于 Taysom 和 Sorensen 列出的方法的继电器测试。在每次迭代后，分析数据并计算新的最大电源设置。如所见，系统以不对称开始测试，但以非常对称结束。

![advanced relay test](img/pid_02.png)

在校准运行期间可以实时监控不对称。它还可以提供对加热器对当前校准参数的适用性的见解。不对称开始为正且收敛到零时，加热器功率足以为校准参数实现对称。

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

当不对称开始为负时，它不会收敛到零。如果 Kalico 不报错，校准运行将完成并提供好的 PID 参数，但是加热器不太可能像功率充足的加热器那样处理干扰。

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

### Pid 控制算法

Kalico 目前支持两种控制算法：位置型和速度型。两种算法之间的根本区别在于位置型算法计算当前时间间隔的 PWM 值应该是什么，而速度型算法计算应该更改前一个 PWM 设置多少以获得当前时间间隔的 PWM 值。

位置型是默认算法，因为它在每种场景中都可以工作。速度型算法可以为位置型算法提供更好的结果，但需要更低的噪声传感器读数或更大的平滑时间设置。

两种算法之间最明显的区别是，对于相同的配置参数，速度控制将消除或大幅减少超调，如下图所示，因为它不容易发生积分饱和。

![algorithm comparison](img/pid_03.png)

![zoomed algorithm comparison](img/pid_04.png)

在某些场景中，速度控制在保持加热器目标温度和排斥干扰方面也会更好。这样做的主要原因是速度控制更像一个标准二阶微分方程。它考虑位置、速度和加速度。