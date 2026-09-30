# 系统配置检查表

本交互式检查表帮助您逐步诊断和验证 Klipper/Kalico 打印机配置。请先选择打印机的运动学类型，然后逐一完成各项检查。

<div class="rd-calc-container" id="system-checklist">

<style>
:root {
  --sc-primary: #e67e22;
  --sc-primary-dark: #d35400;
  --sc-success: #27ae60;
  --sc-warning: #f39c12;
  --sc-danger: #e74c3c;
  --sc-info: #3498db;
  --sc-bg: #f8f9fa;
  --sc-border: #dee2e6;
  --sc-text: #2c3e50;
  --sc-radius: 8px;
}
[data-md-color-scheme="slate"] {
  --sc-bg: #1e1e2e;
  --sc-border: #45475a;
  --sc-text: #cdd6f4;
}
.sc-header {
  background: linear-gradient(135deg, var(--sc-primary), var(--sc-primary-dark));
  color: white;
  padding: 20px 24px;
  border-radius: var(--sc-radius) var(--sc-radius) 0 0;
  display: flex;
  align-items: center;
  gap: 16px;
}
.sc-header svg { width: 32px; height: 32px; fill: white; }
.sc-header-text h2 { margin: 0; font-size: 1.4em; }
.sc-header-text p { margin: 4px 0 0; opacity: 0.9; font-size: 0.9em; }
.sc-body { padding: 20px 24px; background: var(--sc-bg); border: 1px solid var(--sc-border); border-top: none; border-radius: 0 0 var(--sc-radius) var(--sc-radius); }
.sc-controls { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px; padding-bottom: 16px; border-bottom: 1px solid var(--sc-border); }
.sc-btn {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 0.9em;
  font-weight: 500;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.sc-btn-primary { background: var(--sc-primary); color: white; }
.sc-btn-primary:hover { background: var(--sc-primary-dark); transform: translateY(-1px); }
.sc-btn-danger { background: var(--sc-danger); color: white; }
.sc-btn-danger:hover { background: #c0392b; }
.sc-btn-success { background: var(--sc-success); color: white; }
.sc-btn-success:hover { background: #219a52; }
.sc-btn-info { background: var(--sc-info); color: white; }
.sc-btn-info:hover { background: #2980b9; }
.sc-progress {
  background: var(--sc-border);
  border-radius: 20px;
  height: 24px;
  margin-bottom: 20px;
  overflow: hidden;
  position: relative;
}
.sc-progress-bar {
  background: linear-gradient(90deg, var(--sc-success), #2ecc71);
  height: 100%;
  border-radius: 20px;
  transition: width 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 0.8em;
  font-weight: bold;
  min-width: 40px;
}
.sc-section {
  margin-bottom: 24px;
  border: 1px solid var(--sc-border);
  border-radius: var(--sc-radius);
  overflow: hidden;
}
.sc-section-header {
  padding: 12px 16px;
  background: var(--sc-border);
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 600;
  user-select: none;
  transition: background 0.2s;
}
.sc-section-header:hover { background: #d0d5dd; }
[data-md-color-scheme="slate"] .sc-section-header:hover { background: #585b70; }
.sc-section-header .arrow { transition: transform 0.2s; }
.sc-section-header.collapsed .arrow { transform: rotate(-90deg); }
.sc-section-badge {
  margin-left: auto;
  background: var(--sc-primary);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 0.8em;
}
.sc-section-content { padding: 16px; }
.sc-section-content.hidden { display: none; }
.sc-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid var(--sc-border);
}
.sc-item:last-child { border-bottom: none; }
.sc-item input[type="checkbox"] {
  width: 20px;
  height: 20px;
  margin-top: 2px;
  accent-color: var(--sc-primary);
  cursor: pointer;
  flex-shrink: 0;
}
.sc-item-info { flex: 1; }
.sc-item-title { font-weight: 600; margin-bottom: 4px; }
.sc-item-desc { font-size: 0.9em; color: #666; }
[data-md-color-scheme="slate"] .sc-item-desc { color: #a6adc8; }
.sc-item-command {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 8px 12px;
  border-radius: 6px;
  font-family: 'Fira Code', monospace;
  font-size: 0.85em;
  margin-top: 6px;
  overflow-x: auto;
}
.sc-item-config {
  background: #1e1e2e;
  color: #cdd6f4;
  padding: 10px 14px;
  border-radius: 6px;
  font-family: 'Fira Code', monospace;
  font-size: 0.85em;
  margin-top: 8px;
  border-left: 3px solid var(--sc-primary);
}
.sc-item-tip {
  background: var(--sc-info);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85em;
  margin-top: 8px;
}
.sc-item-warning {
  background: var(--sc-warning);
  color: #2c3e50;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85em;
  margin-top: 8px;
}
.sc-item-danger {
  background: var(--sc-danger);
  color: white;
  padding: 8px 12px;
  border-radius: 6px;
  font-size: 0.85em;
  margin-top: 8px;
}
.sc-kinematics-selector {
  background: var(--sc-bg);
  border: 2px solid var(--sc-primary);
  border-radius: var(--sc-radius);
  padding: 20px;
  margin-bottom: 24px;
}
.sc-kinematics-selector h3 {
  margin: 0 0 16px;
  color: var(--sc-primary);
}
.sc-kin-group { margin-bottom: 16px; }
.sc-kin-group-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--sc-text);
  font-size: 0.95em;
}
.sc-kin-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.sc-kin-option {
  padding: 8px 14px;
  border: 2px solid var(--sc-border);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9em;
  background: white;
}
[data-md-color-scheme="slate"] .sc-kin-option { background: #313244; }
.sc-kin-option:hover { border-color: var(--sc-primary); background: #fff5eb; }
[data-md-color-scheme="slate"] .sc-kin-option:hover { background: #45475a; }
.sc-kin-option.selected {
  border-color: var(--sc-primary);
  background: var(--sc-primary);
  color: white;
}
.sc-diagnostic {
  background: #fff8f0;
  border: 2px solid var(--sc-warning);
  border-radius: var(--sc-radius);
  padding: 16px;
  margin-top: 12px;
}
[data-md-color-scheme="slate"] .sc-diagnostic { background: #313244; border-color: #f9e2af; }
.sc-diagnostic h4 { margin: 0 0 12px; color: var(--sc-warning); }
.sc-diagnostic-option {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 8px 0;
  cursor: pointer;
}
.sc-diagnostic-option input[type="radio"] {
  width: 18px;
  height: 18px;
  margin-top: 2px;
  accent-color: var(--sc-warning);
}
.sc-diagnostic-result {
  margin-top: 12px;
  padding: 12px;
  border-radius: 6px;
  font-size: 0.9em;
  display: none;
}
.sc-diagnostic-result.show { display: block; }
.sc-diagnostic-result.success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
.sc-diagnostic-result.warning { background: #fff3cd; color: #856404; border: 1px solid #ffeeba; }
.sc-diagnostic-result.danger { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
[data-md-color-scheme="slate"] .sc-diagnostic-result.success { background: #1e3a2f; color: #a3d9a5; border-color: #2d5a3f; }
[data-md-color-scheme="slate"] .sc-diagnostic-result.warning { background: #3d3520; color: #f9e2af; border-color: #5a4f2a; }
[data-md-color-scheme="slate"] .sc-diagnostic-result.danger { background: #3d2020; color: #f5a0a0; border-color: #5a2a2a; }
.sc-export-section {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--sc-border);
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}
.sc-hidden { display: none !important; }
@media print {
  .sc-controls, .sc-export-section, .sc-btn, input[type="checkbox"] { display: none !important; }
  .sc-section-content { display: block !important; }
  .sc-item { page-break-inside: avoid; }
}
@media (max-width: 768px) {
  .sc-kin-options { flex-direction: column; }
  .sc-kin-option { width: 100%; text-align: center; }
}
</style>

<div class="sc-header">
  <svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z"/></svg>
  <div class="sc-header-text">
    <h2>系统配置检查表</h2>
    <p>Klipper/Kalico 打印机配置逐步诊断工具</p>
  </div>
</div>

<div class="sc-body">
  <div class="sc-controls">
    <button class="sc-btn sc-btn-danger" onclick="SC.resetAll()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
      重置全部
    </button>
    <button class="sc-btn sc-btn-info" onclick="SC.exportJSON()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
      导出 JSON
    </button>
    <button class="sc-btn sc-btn-success" onclick="SC.exportPDF()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
      打印 / PDF
    </button>
  </div>

  <div class="sc-progress">
    <div class="sc-progress-bar" id="sc-progress-bar" style="width: 0%">0%</div>
  </div>

  <!-- 运动学类型选择器 -->
  <div class="sc-kinematics-selector">
    <h3>⚠️ 请选择打印机运动学类型</h3>
    
    <div class="sc-kin-group">
      <div class="sc-kin-group-title">标准 3D 打印机</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="cartesian" onclick="SC.selectKinematics(this)">Cartesian（传统龙门）</div>
        <div class="sc-kin-option" data-kin="corexy" onclick="SC.selectKinematics(this)">CoreXY（高速结构）</div>
        <div class="sc-kin-option" data-kin="corexz" onclick="SC.selectKinematics(this)">CoreXZ</div>
        <div class="sc-kin-option" data-kin="delta" onclick="SC.selectKinematics(this)">Delta（线性 Delta）</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Core 变体</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="coreyx" onclick="SC.selectKinematics(this)">CoreYX</div>
        <div class="sc-kin-option" data-kin="coreyz" onclick="SC.selectKinematics(this)">CoreYZ</div>
        <div class="sc-kin-option" data-kin="corezx" onclick="SC.selectKinematics(this)">CoreZX</div>
        <div class="sc-kin-option" data-kin="corezy" onclick="SC.selectKinematics(this)">CoreZY</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Limited 变体（单轴速度/加速度限制）</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="limited_cartesian" onclick="SC.selectKinematics(this)">Limited Cartesian</div>
        <div class="sc-kin-option" data-kin="limited_corexy" onclick="SC.selectKinematics(this)">Limited CoreXY</div>
        <div class="sc-kin-option" data-kin="limited_corexz" onclick="SC.selectKinematics(this)">Limited CoreXZ</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Hybrid / IDEX 结构</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="hybrid_corexy" onclick="SC.selectKinematics(this)">Hybrid CoreXY</div>
        <div class="sc-kin-option" data-kin="hybrid_corexz" onclick="SC.selectKinematics(this)">Hybrid CoreXZ</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">特殊结构</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="deltesian" onclick="SC.selectKinematics(this)">Deltesian</div>
        <div class="sc-kin-option" data-kin="polar" onclick="SC.selectKinematics(this)">Polar（极坐标）</div>
        <div class="sc-kin-option" data-kin="rotary_delta" onclick="SC.selectKinematics(this)">Rotary Delta</div>
        <div class="sc-kin-option" data-kin="scara" onclick="SC.selectKinematics(this)">SCARA</div>
        <div class="sc-kin-option" data-kin="tpara" onclick="SC.selectKinematics(this)">TPARA</div>
        <div class="sc-kin-option" data-kin="polargraph" onclick="SC.selectKinematics(this)">Polargraph（墙式绘图仪）</div>
        <div class="sc-kin-option" data-kin="belt" onclick="SC.selectKinematics(this)">Belt（传送带打印机）</div>
        <div class="sc-kin-option" data-kin="robot_arm" onclick="SC.selectKinematics(this)">Robot Arm（机器人臂）</div>
        <div class="sc-kin-option" data-kin="foam_cutter" onclick="SC.selectKinematics(this)">Foam Cutter（热丝切割机）</div>
      </div>
    </div>
  </div>

  <!-- 第一组：电源与硬件连接 -->
  <div class="sc-section" id="sc-section-power">
    <div class="sc-section-header" onclick="SC.toggleSection('power')">
      <span class="arrow">▼</span>
      <span>🔌 电源与硬件连接</span>
      <span class="sc-section-badge" id="sc-badge-power">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-power">
      <div class="sc-item">
        <input type="checkbox" id="sc-p1" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">电源电压匹配</div>
          <div class="sc-item-desc">确认电源输出电压与主板要求一致（通常为 24V）。</div>
          <div class="sc-item-tip">💡 检查电源标签上的输出电压，与主板规格进行对比。</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p2" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">主板供电连接</div>
          <div class="sc-item-desc">确保所有电源线正确连接到主板、驱动器和热床（如适用）。</div>
          <div class="sc-item-warning">⚠️ 检查接线前请务必断电！</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p3" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">MCU 连接状态</div>
          <div class="sc-item-desc">确认 MCU 已被主机识别。执行 <code>STATUS</code> 命令验证通信。</div>
          <div class="sc-item-command">STATUS</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p4" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">步进驱动模块安装</div>
          <div class="sc-item-desc">确认所有步进驱动器已正确安装在插槽中，方向正确。</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p5" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">CAN 总线连接（如适用）</div>
          <div class="sc-item-desc">如果使用 CAN 总线，确认 CAN 接口已启动且 MCU 可达。</div>
          <div class="sc-item-command">bash-canbus.sh canscan</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 第二组：限位开关检查 -->
  <div class="sc-section" id="sc-section-endstop">
    <div class="sc-section-header" onclick="SC.toggleSection('endstop')">
      <span class="arrow">▼</span>
      <span>🔴 限位开关检查</span>
      <span class="sc-section-badge" id="sc-badge-endstop">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-endstop">
      <div class="sc-item">
        <input type="checkbox" id="sc-e1" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">选择限位类型</div>
          <div class="sc-item-desc">选择您使用的限位开关类型：</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-endstop="micro" onclick="SC.selectEndstop(this)">微动限位（NC）</div>
            <div class="sc-kin-option" data-endstop="tap" onclick="SC.selectEndstop(this)">Voron TAP</div>
            <div class="sc-kin-option" data-endstop="optical" onclick="SC.selectEndstop(this)">光电限位</div>
            <div class="sc-kin-option" data-endstop="inductive" onclick="SC.selectEndstop(this)">电感/电容式</div>
            <div class="sc-kin-option" data-endstop="sensorless" onclick="SC.selectEndstop(this)">无限位归位</div>
          </div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e2" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">限位接线检查</div>
          <div class="sc-item-desc">确认限位开关接线正确。微动限位建议使用 NC（常闭）接法以提高安全性。</div>
          <div class="sc-item-danger">🔴 三线微动限位：必须剪断 5V 线（通常为红色），否则可能烧毁 FLY 主板！</div>
          <div class="sc-item-config">[stepper_x]
endstop_pin: ^!PD9  # ^ = 上拉, ! = 反转（NC 限位）</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e3" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">QUERY_ENDSTOPS 测试</div>
          <div class="sc-item-desc">执行此命令验证限位状态。未触发时应显示 "open"。</div>
          <div class="sc-item-command">QUERY_ENDSTOPS</div>
          <div class="sc-item-tip">💡 手动触发每个限位开关，验证其状态变为 "TRIGGERED"。</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e4" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">限位触发方向</div>
          <div class="sc-item-desc">确认触发逻辑正确：未触发时为 "open"，按下时为 "TRIGGERED"。</div>
          <div class="sc-item-tip">💡 如果状态反转，在 endstop_pin 中添加或删除 <code>!</code>。如果无变化，检查接线并添加 <code>^</code> 上拉。</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e5" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">上拉电阻配置</div>
          <div class="sc-item-desc">确保大多数限位类型（微动、光电等）的 endstop_pin 中包含 <code>^</code>。</div>
          <div class="sc-item-config">endstop_pin: ^!PD9  # ^ 启用内部上拉电阻</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 第三组：电机方向校准（根据运动学类型动态显示） -->
  <div class="sc-section" id="sc-section-motor">
    <div class="sc-section-header" onclick="SC.toggleSection('motor')">
      <span class="arrow">▼</span>
      <span>⚙️ 电机方向校准</span>
      <span class="sc-section-badge" id="sc-badge-motor">0/4</span>
    </div>
    <div class="sc-section-content" id="sc-content-motor">
      <div id="sc-motor-content">
        <p><em>请在上方选择运动学类型以查看电机校准步骤。</em></p>
      </div>
    </div>
  </div>

  <!-- 第四组：加热系统检查 -->
  <div class="sc-section" id="sc-section-heat">
    <div class="sc-section-header" onclick="SC.toggleSection('heat')">
      <span class="arrow">▼</span>
      <span>🌡️ 加热系统检查</span>
      <span class="sc-section-badge" id="sc-badge-heat">0/6</span>
    </div>
    <div class="sc-section-content" id="sc-content-heat">
      <div class="sc-item">
        <input type="checkbox" id="sc-h1" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">挤出头温度读数</div>
          <div class="sc-item-desc">确认挤出头温度正常报告且稳定（不会自行上升）。</div>
          <div class="sc-item-danger">🔴 如果温度在未加热时上升，请立即断电！</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h2" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">热床（如适用）</div>
          <div class="sc-item-desc">检查打印机是否有热床。如有，确认温度读数稳定。</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-bed="yes" onclick="SC.selectBed(this)">有热床</div>
            <div class="sc-kin-option" data-bed="no" onclick="SC.selectBed(this)">无热床</div>
          </div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h3" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">M112 紧急停止测试</div>
          <div class="sc-item-desc">发送 M112 命令测试紧急停止功能。验证 Klipper 进入关闭状态。使用 FIRMWARE_RESTART 清除。</div>
          <div class="sc-item-command">M112
# 等待关闭，然后：
FIRMWARE_RESTART</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h4" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">挤出头加热测试</div>
          <div class="sc-item-desc">设置挤出头到 50°C 并确认温度上升。监控温度曲线。</div>
          <div class="sc-item-command">M104 S50  # 设置挤出头到 50°C
# 等待 30-60 秒，确认温度上升
M104 S0   # 关闭</div>
          <div class="sc-item-tip">💡 如果温度不上升，检查 heater_pin 配置。</div>
        </div>
      </div>
      <div class="sc-item" id="sc-h5-bed" style="display:none;">
        <input type="checkbox" id="sc-h5" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">热床加热测试</div>
          <div class="sc-item-desc">设置热床到 50°C 并确认温度上升。</div>
          <div class="sc-item-command">M140 S50  # 设置热床到 50°C
# 等待 30-60 秒，确认温度上升
M140 S0   # 关闭</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h6" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">PID 校准</div>
          <div class="sc-item-desc">验证加热功能正常后，运行 PID 校准以获得稳定的温度控制。</div>
          <div class="sc-item-command">PID_CALIBRATE HEATER=extruder TARGET=200
SAVE_CONFIG
# 如有热床：
PID_CALIBRATE HEATER=heater_bed TARGET=60
SAVE_CONFIG</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 第五组：校准流程 -->
  <div class="sc-section" id="sc-section-calibration">
    <div class="sc-section-header" onclick="SC.toggleSection('calibration')">
      <span class="arrow">▼</span>
      <span>📏 校准流程</span>
      <span class="sc-section-badge" id="sc-badge-calibration">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-calibration">
      <div class="sc-item">
        <input type="checkbox" id="sc-c1" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Rotation Distance 校准</div>
          <div class="sc-item-desc">校准挤出机旋转距离以确保精确挤出。标记耗材，挤出 50mm，测量实际距离。</div>
          <div class="sc-item-command">G91
G1 E50 F60  # 以慢速挤出 50mm
# 测量实际挤出长度
# new_rotation_distance = old_value * actual_length / 50</div>
          <div class="sc-item-config">[extruder]
rotation_distance: 23.280  # 更新为校准后的值</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c2" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Z Offset 校准</div>
          <div class="sc-item-desc">使用纸张法校准喷嘴与热床的距离。调整至纸张有轻微阻力。</div>
          <div class="sc-item-command">G28
G90
G1 X150 Y150 F3000  # 移动到中心
G1 Z2 F300
# 使用 baby stepping 或调整 Z offset
# 机械限位：Z_OFFSET_APPLY_ENDSTOP
# 探针：Z_OFFSET_APPLY_PROBE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c3" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Bed Mesh 校准（如适用）</div>
          <div class="sc-item-desc">如果使用自动调平，运行床面网格校准。</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-mesh="yes" onclick="SC.selectMesh(this)">使用 Bed Mesh</div>
            <div class="sc-kin-option" data-mesh="no" onclick="SC.selectMesh(this)">不使用 Bed Mesh</div>
          </div>
          <div class="sc-item-command" id="sc-mesh-cmd" style="display:none;">BED_MESH_CALIBRATE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c4" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Input Shaper 校准（如适用）</div>
          <div class="sc-item-desc">如果使用 ADXL345 加速度计，校准输入整形器以减少振纹。</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-shaper="yes" onclick="SC.selectShaper(this)">使用 Input Shaper</div>
            <div class="sc-kin-option" data-shaper="no" onclick="SC.selectShaper(this)">不使用 Input Shaper</div>
          </div>
          <div class="sc-item-command" id="sc-shaper-cmd" style="display:none;">SHAPER_CALIBRATE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c5" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Pressure Advance 校准（如适用）</div>
          <div class="sc-item-desc">校准压力提前以改善拐角处的挤出控制。</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-pa="yes" onclick="SC.selectPA(this)">使用 PA</div>
            <div class="sc-kin-option" data-pa="no" onclick="SC.selectPA(this)">不使用 PA</div>
          </div>
          <div class="sc-item-config" id="sc-pa-config" style="display:none;">[extruder]
pressure_advance: 0.04
pressure_advance_smooth_time: 0.040</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 第六组：可选外设检查 -->
  <div class="sc-section" id="sc-section-peripheral">
    <div class="sc-section-header" onclick="SC.toggleSection('peripheral')">
      <span class="arrow">▼</span>
      <span>🔧 可选外设检查</span>
      <span class="sc-section-badge" id="sc-badge-peripheral">0/10</span>
    </div>
    <div class="sc-section-content" id="sc-content-peripheral">
      <div class="sc-item">
        <input type="checkbox" id="sc-per1" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">BLTouch / CR Touch</div>
          <div class="sc-item-desc">自动调平探针。检查部署、收回和 Z 限位功能。</div>
          <div class="sc-item-command">DEPLOY_PROBE
# 确认探针已部署
QUERY_ENDSTOPS  # 应显示探针已触发
STOW_PROBE</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per2" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Voron TAP</div>
          <div class="sc-item-desc">基于喷嘴的探针。确认探针引脚响应喷嘴接触。</div>
          <div class="sc-item-config">[probe]
pin: ^PC15
x_offset: 0
y_offset: 0
# z_offset: 0  # 通过 PROBE_CALIBRATE 设置</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per3" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">多 Z 轴</div>
          <div class="sc-item-desc">多个 Z 步进电机（双 Z/三 Z/四 Z）。确认所有 Z 电机正确运动。</div>
          <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z
STEPPER_BUZZ STEPPER=stepper_z1
# STEPPER_BUZZ STEPPER=stepper_z2（如适用）
# STEPPER_BUZZ STEPPER=stepper_z3（如适用）</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per4" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Z Tilt Adjustment</div>
          <div class="sc-item-desc">多 Z 轴打印机，运行 Z 倾斜调整以校准龙门架水平。</div>
          <div class="sc-item-command">Z_TILT_ADJUST</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per5" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">龙门校正 (Skew Correction)</div>
          <div class="sc-item-desc">补偿 XY 平面的机械偏差。</div>
          <div class="sc-item-config">[skew_correction]</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per6" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">断料检测</div>
          <div class="sc-item-desc">耗材用尽检测传感器。</div>
          <div class="sc-item-command">FILAMENT_SENSOR_ENABLE SENSOR=runout
# 模拟断料进行测试</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per7" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">舵机 (Servo)</div>
          <div class="sc-item-desc">舵机电机（如用于笔升降、自动调平等）。</div>
          <div class="sc-item-command">SET_SERVO SERVO=servo0 ANGLE=0
SET_SERVO SERVO=servo0 ANGLE=90</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per8" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">RGB LED 灯带</div>
          <div class="sc-item-desc">可寻址 LED 灯带，用于状态指示。</div>
          <div class="sc-item-command">SET_LED LED=led_print LED=white TRANSMIT=1</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per9" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">ADXL345 加速度计</div>
          <div class="sc-item-desc">用于输入整形器校准。验证 SPI 连接。</div>
          <div class="sc-item-command">ACCELEROMETER_QUERY  # 应返回数值</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per10" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">IDEX 双龙门</div>
          <div class="sc-item-desc">独立双挤出，两个打印头。</div>
          <div class="sc-item-command">SET_DUAL_CARRIAGE CARRIAGE=1 MODE=PRIMARY
# 测试独立运动</div>
        </div>
      </div>
    </div>
  </div>

  <!-- 第七组：高级运动学设置（动态） -->
  <div class="sc-section sc-hidden" id="sc-section-advanced">
    <div class="sc-section-header" onclick="SC.toggleSection('advanced')">
      <span class="arrow">▼</span>
      <span>🚀 高级运动学设置</span>
      <span class="sc-section-badge" id="sc-badge-advanced">0/3</span>
    </div>
    <div class="sc-section-content" id="sc-content-advanced">
      <div id="sc-advanced-content"></div>
    </div>
  </div>

  <!-- 导出区域 -->
  <div class="sc-export-section">
    <button class="sc-btn sc-btn-info" onclick="SC.exportJSON()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
      导出 JSON 报告
    </button>
    <button class="sc-btn sc-btn-success" onclick="SC.exportPDF()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
      打印 / 保存 PDF
    </button>
  </div>

</div>

<script>
(function() {
  'use strict';
  
  const STORAGE_KEY = 'kalico_system_checklist';
  const SECTIONS = ['power', 'endstop', 'motor', 'heat', 'calibration', 'peripheral', 'advanced'];
  
  let state = {
    kinematics: null,
    endstopType: null,
    hasBed: null,
    hasMesh: null,
    hasShaper: null,
    hasPA: null,
    checks: {}
  };

  function loadState() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        state = { ...state, ...parsed };
        restoreUI();
      }
    } catch(e) {
      console.warn('Failed to load checklist state:', e);
    }
  }

  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch(e) {
      console.warn('Failed to save checklist state:', e);
    }
  }

  function restoreUI() {
    Object.keys(state.checks).forEach(id => {
      const el = document.getElementById(id);
      if (el) el.checked = state.checks[id];
    });

    if (state.kinematics) {
      const kinEl = document.querySelector(`.sc-kin-option[data-kin="${state.kinematics}"]`);
      if (kinEl) selectKinematics(kinEl, false);
    }

    if (state.endstopType) {
      const endEl = document.querySelector(`.sc-kin-option[data-endstop="${state.endstopType}"]`);
      if (endEl) endEl.classList.add('selected');
    }

    if (state.hasBed !== null) {
      const bedEl = document.querySelector(`.sc-kin-option[data-bed="${state.hasBed}"]`);
      if (bedEl) {
        bedEl.classList.add('selected');
        document.getElementById('sc-h5-bed').style.display = state.hasBed === 'yes' ? 'flex' : 'none';
      }
    }

    if (state.hasMesh !== null) {
      const meshEl = document.querySelector(`.sc-kin-option[data-mesh="${state.hasMesh}"]`);
      if (meshEl) {
        meshEl.classList.add('selected');
        document.getElementById('sc-mesh-cmd').style.display = state.hasMesh === 'yes' ? 'block' : 'none';
      }
    }

    if (state.hasShaper !== null) {
      const shaperEl = document.querySelector(`.sc-kin-option[data-shaper="${state.hasShaper}"]`);
      if (shaperEl) {
        shaperEl.classList.add('selected');
        document.getElementById('sc-shaper-cmd').style.display = state.hasShaper === 'yes' ? 'block' : 'none';
      }
    }

    if (state.hasPA !== null) {
      const paEl = document.querySelector(`.sc-kin-option[data-pa="${state.hasPA}"]`);
      if (paEl) {
        paEl.classList.add('selected');
        document.getElementById('sc-pa-config').style.display = state.hasPA === 'yes' ? 'block' : 'none';
      }
    }

    updateProgress();
  }

  function selectKinematics(el, save) {
    if (save === undefined) save = true;
    document.querySelectorAll('.sc-kinematics-selector .sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.kinematics = el.dataset.kin;
    
    updateMotorSection();
    updateAdvancedSection();
    updateProgress();
    
    if (save) saveState();
  }

  function selectEndstop(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.endstopType = el.dataset.endstop;
    saveState();
  }

  function selectBed(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasBed = el.dataset.bed;
    document.getElementById('sc-h5-bed').style.display = state.hasBed === 'yes' ? 'flex' : 'none';
    updateProgress();
    saveState();
  }

  function selectMesh(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasMesh = el.dataset.mesh;
    document.getElementById('sc-mesh-cmd').style.display = state.hasMesh === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  function selectShaper(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasShaper = el.dataset.shaper;
    document.getElementById('sc-shaper-cmd').style.display = state.hasShaper === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  function selectPA(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasPA = el.dataset.pa;
    document.getElementById('sc-pa-config').style.display = state.hasPA === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  function toggleSection(section) {
    var header = document.querySelector('#sc-section-' + section + ' .sc-section-header');
    var content = document.getElementById('sc-content-' + section);
    header.classList.toggle('collapsed');
    content.classList.toggle('hidden');
  }

  function updateCheck(section) {
    var content = document.getElementById('sc-content-' + section);
    var checkboxes = content.querySelectorAll('input[type="checkbox"]');
    var checked = 0;
    checkboxes.forEach(function(cb) {
      state.checks[cb.id] = cb.checked;
      if (cb.checked) checked++;
    });
    document.getElementById('sc-badge-' + section).textContent = checked + '/' + checkboxes.length;
    updateProgress();
    saveState();
  }

  function updateProgress() {
    var total = 0;
    var checked = 0;
    SECTIONS.forEach(function(section) {
      if (section === 'advanced' && !document.getElementById('sc-section-advanced').classList.contains('sc-hidden')) {
        var content = document.getElementById('sc-content-' + section);
        if (content) {
          var cbs = content.querySelectorAll('input[type="checkbox"]');
          total += cbs.length;
          cbs.forEach(function(cb) { if (cb.checked) checked++; });
        }
      } else if (section !== 'advanced') {
        var content = document.getElementById('sc-content-' + section);
        if (content) {
          var cbs = content.querySelectorAll('input[type="checkbox"]');
          total += cbs.length;
          cbs.forEach(function(cb) { if (cb.checked) checked++; });
        }
      }
    });
    
    total++;
    if (state.kinematics) checked++;
    
    var pct = total > 0 ? Math.round((checked / total) * 100) : 0;
    var bar = document.getElementById('sc-progress-bar');
    bar.style.width = pct + '%';
    bar.textContent = pct + '%';
  }

  function updateMotorSection() {
    var container = document.getElementById('sc-motor-content');
    var kin = state.kinematics;
    
    if (!kin) {
      container.innerHTML = '<p><em>请在上方选择运动学类型以查看电机校准步骤。</em></p>';
      return;
    }

    var html = '';
    
    var corexyVariants = ['corexy', 'coreyx'];
    var corexzVariants = ['corexz', 'coreyz', 'corezx', 'corezy'];
    var deltaTypes = ['delta', 'rotary_delta'];
    
    if (corexyVariants.indexOf(kin) !== -1 || kin === 'limited_corexy' || kin === 'hybrid_corexy') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">X 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 X 步进电机正确运动。电机应前后振荡 1mm。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Y 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Y 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Z 步进电机正确运动。<strong>Z 必须先向上移动，再向下</strong>。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div><div class="sc-item-warning">⚠️ 如果 Z 先向下移动，通过添加/删除 <code>!</code> 反转 dir_pin</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">CoreXY 方向诊断</div><div class="sc-item-desc">选择您观察到的问题以获取解决方案：</div><div class="sc-diagnostic"><h4>⚙️ CoreXY 电机方向诊断</h4><p style="margin:0 0 8px;font-size:0.9em;">使用 <code>G91</code> + <code>G1 X10 F3000</code> 和 <code>G1 Y10 F3000</code> 测试。观察哪个电机实际运动及方向。</p><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case1\')"><input type="radio" name="corexy_diag" id="corexy-case1"><div><strong>情况一：</strong>XY 轴控制互相颠倒，且 XY 移动正负方向皆相反<div class="sc-diagnostic-result" id="corexy-result-case1"><strong>解决方案：</strong>反转 X 电机接线（对调 X 电机任意两相线）。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case2\')"><input type="radio" name="corexy_diag" id="corexy-case2"><div><strong>情况二：</strong>XY 轴控制互相颠倒，但 XY 移动正负方向正确<div class="sc-diagnostic-result" id="corexy-result-case2"><strong>解决方案：</strong>反转 Y 电机接线（对调 Y 电机任意两相线）。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case3\')"><input type="radio" name="corexy_diag" id="corexy-case3"><div><strong>情况三：</strong>XY 轴控制互相颠倒，X 正负方向正确，Y 正负方向相反<div class="sc-diagnostic-result" id="corexy-result-case3"><strong>解决方案：</strong>1) 反转 X 电机接线。2) 整体对调 X 与 Y 的电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case4\')"><input type="radio" name="corexy_diag" id="corexy-case4"><div><strong>情况四：</strong>XY 轴控制互相颠倒，X 正负方向相反，Y 正负方向正确<div class="sc-diagnostic-result" id="corexy-result-case4"><strong>解决方案：</strong>1) 反转 Y 电机接线。2) 整体对调 X 与 Y 的电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case5\')"><input type="radio" name="corexy_diag" id="corexy-case5"><div><strong>情况五：</strong>XY 轴控制正确，但 XY 正负方向都相反<div class="sc-diagnostic-result" id="corexy-result-case5"><strong>解决方案：</strong>同时反转 X 电机和 Y 电机接线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case6\')"><input type="radio" name="corexy_diag" id="corexy-case6"><div><strong>情况六：</strong>XY 轴控制正确，X 正负方向正确，Y 正负方向相反<div class="sc-diagnostic-result" id="corexy-result-case6"><strong>解决方案：</strong>整体对调 X 与 Y 的电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexy\', \'case7\')"><input type="radio" name="corexy_diag" id="corexy-case7"><div><strong>情况七：</strong>XY 轴控制正确，X 正负方向相反，Y 正负方向正确<div class="sc-diagnostic-result" id="corexy-result-case7"><strong>解决方案：</strong>1) 整体对调 X 与 Y 的电机线。2) 同时反转 X 和 Y 电机接线。</div></div></div></div></div></div>';
    } else if (corexzVariants.indexOf(kin) !== -1 || kin === 'limited_corexz' || kin === 'hybrid_corexz') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">X 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 X 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Y 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Y 步进电机正确运动（独立轴）。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Z 步进电机正确运动。<strong>Z 必须先向上移动</strong>。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div><div class="sc-item-warning">⚠️ 如果 Z 先向下移动，通过添加/删除 <code>!</code> 反转 dir_pin</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">CoreXZ 方向诊断</div><div class="sc-item-desc">X 和 Z 在 CoreXZ 中耦合。选择您观察到的问题：</div><div class="sc-diagnostic"><h4>⚙️ CoreXZ 电机方向诊断</h4><p style="margin:0 0 8px;font-size:0.9em;">使用 <code>G91</code> + <code>G1 X10 F3000</code> 和 <code>G1 Z10 F3000</code> 测试。</p><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case1\')"><input type="radio" name="corexz_diag" id="corexz-case1"><div><strong>情况一：</strong>XZ 轴控制互相颠倒，且 XZ 移动正负方向皆相反<div class="sc-diagnostic-result" id="corexz-result-case1"><strong>解决方案：</strong>反转 X 电机接线（对调任意两相线）。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case2\')"><input type="radio" name="corexz_diag" id="corexz-case2"><div><strong>情况二：</strong>XZ 轴控制互相颠倒，但 XZ 移动正负方向正确<div class="sc-diagnostic-result" id="corexz-result-case2"><strong>解决方案：</strong>反转 Z 电机接线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case3\')"><input type="radio" name="corexz_diag" id="corexz-case3"><div><strong>情况三：</strong>XZ 轴控制互相颠倒，X 正负方向正确，Z 正负方向相反<div class="sc-diagnostic-result" id="corexz-result-case3"><strong>解决方案：</strong>1) 反转 X 电机接线。2) 对调 X 和 Z 电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case4\')"><input type="radio" name="corexz_diag" id="corexz-case4"><div><strong>情况四：</strong>XZ 轴控制互相颠倒，X 正负方向相反，Z 正负方向正确<div class="sc-diagnostic-result" id="corexz-result-case4"><strong>解决方案：</strong>1) 反转 Z 电机接线。2) 对调 X 和 Z 电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case5\')"><input type="radio" name="corexz_diag" id="corexz-case5"><div><strong>情况五：</strong>XZ 轴控制正确，但 XZ 正负方向都相反<div class="sc-diagnostic-result" id="corexz-result-case5"><strong>解决方案：</strong>同时反转 X 和 Z 电机接线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case6\')"><input type="radio" name="corexz_diag" id="corexz-case6"><div><strong>情况六：</strong>XZ 轴控制正确，X 正负方向正确，Z 正负方向相反<div class="sc-diagnostic-result" id="corexz-result-case6"><strong>解决方案：</strong>对调 X 和 Z 电机线。</div></div></div><div class="sc-diagnostic-option" onclick="SC.selectDiagnostic(\'corexz\', \'case7\')"><input type="radio" name="corexz_diag" id="corexz-case7"><div><strong>情况七：</strong>XZ 轴控制正确，X 正负方向相反，Z 正负方向正确<div class="sc-diagnostic-result" id="corexz-result-case7"><strong>解决方案：</strong>1) 对调 X 和 Z 电机线。2) 同时反转 X 和 Z 电机接线。</div></div></div></div></div></div>';
    } else if (deltaTypes.indexOf(kin) !== -1) {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">A 塔 STEPPER_BUZZ</div><div class="sc-item-desc">验证 A 塔步进电机正确运动（应先向上移动）。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">B 塔 STEPPER_BUZZ</div><div class="sc-item-desc">验证 B 塔步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">C 塔 STEPPER_BUZZ</div><div class="sc-item-desc">验证 C 塔步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Delta 校准</div><div class="sc-item-desc">运行 DELTA_CALIBRATE 校准 Delta 几何参数。校准后保存结果。</div><div class="sc-item-command">DELTA_CALIBRATE
# 按提示探测校准点
SAVE_CONFIG</div><div class="sc-item-config">[printer]
kinematics: delta
delta_radius: 100  # 校准后的值

[stepper_a]
arm_length: 200  # 必须大于 delta_radius</div></div></div>';
    } else if (kin === 'scara') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肩部电机 (Stepper A) STEPPER_BUZZ</div><div class="sc-item-desc">验证肩部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肘部电机 (Stepper B) STEPPER_BUZZ</div><div class="sc-item-desc">验证肘部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Z 步进电机正确运动（应先向上移动）。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">SCARA 臂长验证</div><div class="sc-item-desc">确认臂长已准确测量并配置。</div><div class="sc-item-config">[scara]
linkage_1: 100  # 内臂长度 (mm)
linkage_2: 100  # 外臂长度 (mm)
offset_x: 0     # 塔相对于床中心的偏移
offset_y: 0
variant: morgan  # 或 "mp"</div></div></div>';
    } else if (kin === 'tpara') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">基座电机 (Stepper A) STEPPER_BUZZ</div><div class="sc-item-desc">验证基座旋转步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肩部电机 (Stepper B) STEPPER_BUZZ</div><div class="sc-item-desc">验证肩部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肘部电机 (Stepper C) STEPPER_BUZZ</div><div class="sc-item-desc">验证肘部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">TPARA 臂长验证</div><div class="sc-item-desc">确认臂长已准确测量。</div><div class="sc-item-config">[tpara]
linkage_1: 100  # 内臂长度 (mm)
linkage_2: 100  # 外臂长度 (mm)</div></div></div>';
    } else if (kin === 'polargraph') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">左电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证左步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_left</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">右电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证右步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_right</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">电机间距验证</div><div class="sc-item-desc">确认电机间距已准确测量并配置。</div><div class="sc-item-config">[polargraph]
motor_distance_x: 400  # 电机中心间距 (mm)</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机（笔升降）STEPPER_BUZZ（如适用）</div><div class="sc-item-desc">如果使用 Z 轴进行笔升降，验证其工作。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div></div></div>';
    } else if (kin === 'belt') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">X 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 X 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Y 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Y 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机（传送带）STEPPER_BUZZ</div><div class="sc-item-desc">验证传送带电机正确运动。注意：Z 轴是无限的（无需归位）。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">床面倾角验证</div><div class="sc-item-desc">确认床面倾角与物理设置一致（通常为 45°）。</div><div class="sc-item-config">[belt]
bed_tilt: 45.0  # 必须与物理角度完全一致
bed_rotation_axis: y  # 或 "x"</div></div></div>';
    } else if (kin === 'robot_arm') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">基座电机 (Stepper A) STEPPER_BUZZ</div><div class="sc-item-desc">验证基座旋转步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肩部电机 (Stepper B) STEPPER_BUZZ</div><div class="sc-item-desc">验证肩部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">肘部电机 (Stepper C) STEPPER_BUZZ</div><div class="sc-item-desc">验证肘部步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">DH 参数验证</div><div class="sc-item-desc">确认连杆长度已准确测量并配置。</div><div class="sc-item-config">[robot_arm]
d1: 100   # 基座高度 (mm)
a1: 50    # 连杆 1 长度 (mm)
a2: 200   # 连杆 2 长度 (mm)
a3: 150   # 连杆 3 长度 (mm)</div></div></div>';
    } else if (kin === 'foam_cutter') {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">X 电机（上丝）STEPPER_BUZZ</div><div class="sc-item-desc">验证 X 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Y 电机（上丝）STEPPER_BUZZ</div><div class="sc-item-desc">验证 Y 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">U 电机（下丝 X）STEPPER_BUZZ</div><div class="sc-item-desc">验证 U 步进电机（下部 X）正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_u</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">V 电机（下丝 Y）STEPPER_BUZZ</div><div class="sc-item-desc">验证 V 步进电机（下部 Y）正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_v</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m5" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">热丝长度验证</div><div class="sc-item-desc">确认热丝长度配置正确。如果端点距离超过此值，移动将被拒绝。</div><div class="sc-item-config">[foam_cutter]
wire_length: 500.0  # 热丝长度 (mm)</div></div></div>';
    } else {
      html = '<div class="sc-item"><input type="checkbox" id="sc-m1" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">X 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 X 步进电机正确运动。电机应前后振荡 1mm。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m2" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Y 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Y 步进电机正确运动。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m3" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">Z 电机 STEPPER_BUZZ</div><div class="sc-item-desc">验证 Z 步进电机正确运动。<strong>Z 必须先向上移动，再向下</strong>。</div><div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div><div class="sc-item-warning">⚠️ 如果 Z 先向下移动，通过添加/删除 <code>!</code> 反转 dir_pin</div></div></div><div class="sc-item"><input type="checkbox" id="sc-m4" onchange="SC.updateCheck(\'motor\')"><div class="sc-item-info"><div class="sc-item-title">电机方向验证</div><div class="sc-item-desc">使用 G1 命令验证所有电机朝正确方向运动。</div><div class="sc-item-command">G91
G1 X10 F3000  # X 应向右移动
G1 Y10 F3000  # Y 应向前移动
G1 Z10 F300   # Z 应向上移动
G1 X-10 F3000
G1 Y-10 F3000
G1 Z-10 F300</div><div class="sc-item-tip">💡 如果任何轴方向错误，通过添加/删除 <code>!</code> 反转该轴的 dir_pin。</div></div></div>';
    }
    
    container.innerHTML = html;
  }

  function updateAdvancedSection() {
    var container = document.getElementById('sc-advanced-content');
    var section = document.getElementById('sc-section-advanced');
    var kin = state.kinematics;
    
    var limitedTypes = ['limited_cartesian', 'limited_corexy', 'limited_corexz'];
    var hybridTypes = ['hybrid_corexy', 'hybrid_corexz'];
    
    if (limitedTypes.indexOf(kin) !== -1) {
      section.classList.remove('sc-hidden');
      var baseKin = kin.replace('limited_', '');
      container.innerHTML = '<div class="sc-item"><input type="checkbox" id="sc-a1" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">单轴速度限制</div><div class="sc-item-desc">为每个轴独立配置最大速度。</div><div class="sc-item-config">[printer]
kinematics: ' + kin + '
max_velocity: 500  # 应为 X 和 Y 速度的斜边
max_accel: 5000

[' + baseKin + ']
max_x_velocity: 400
max_y_velocity: 300
max_z_velocity: 5
max_x_accel: 5000
max_y_accel: 4000
max_z_accel: 100</div></div></div><div class="sc-item"><input type="checkbox" id="sc-a2" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">动态限制调整</div><div class="sc-item-desc">测试 SET_KINEMATICS_LIMIT 命令动态调整限制。</div><div class="sc-item-command">SET_KINEMATICS_LIMIT X_ACCEL=4000 Y_ACCEL=3000
# 查询当前限制：
SET_KINEMATICS_LIMIT QUERY=1</div></div></div><div class="sc-item"><input type="checkbox" id="sc-a3" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">缩放 XY 加速度</div><div class="sc-item-desc">如果启用，单轴加速度限制将按 M204 值比例缩放。</div><div class="sc-item-config">[' + baseKin + ']
scale_xy_accel: True  # 或 False</div></div></div>';
    } else if (hybridTypes.indexOf(kin) !== -1) {
      section.classList.remove('sc-hidden');
      container.innerHTML = '<div class="sc-item"><input type="checkbox" id="sc-a1" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">双龙门配置</div><div class="sc-item-desc">配置第二个打印头用于 IDEX 操作。</div><div class="sc-item-config">[dual_carriage]
axis: x
max_velocity: 300
max_accel: 3000
step_pin: <第二个打印头 step>
dir_pin: <第二个打印头 dir>
enable_pin: <第二个打印头 enable></div></div></div><div class="sc-item"><input type="checkbox" id="sc-a2" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">反转运动学（如需要）</div><div class="sc-item-desc">如果电机方向反转，尝试反转运动学耦合。</div><div class="sc-item-config">[' + kin + ']
invert_kinematics: true  # 或 false</div></div></div><div class="sc-item"><input type="checkbox" id="sc-a3" onchange="SC.updateCheck(\'advanced\')"><div class="sc-item-info"><div class="sc-item-title">IDEX 模式测试</div><div class="sc-item-desc">测试双龙门模式：PRIMARY、COPY、MIRROR。</div><div class="sc-item-command">SET_DUAL_CARRIAGE CARRIAGE=1 MODE=PRIMARY
G28 X
SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY
# 测试复制模式
SET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR
# 测试镜像模式</div></div></div>';
    } else {
      section.classList.add('sc-hidden');
    }
  }

  function selectDiagnostic(type, caseId) {
    document.querySelectorAll('[id^="' + type + '-result-"]').forEach(function(el) {
      el.classList.remove('show');
    });
    var result = document.getElementById(type + '-result-' + caseId);
    if (result) {
      result.classList.add('show');
    }
  }

  function resetAll() {
    if (!confirm('确定要重置所有检查项吗？此操作不可撤销。')) {
      return;
    }
    
    state = {
      kinematics: null,
      endstopType: null,
      hasBed: null,
      hasMesh: null,
      hasShaper: null,
      hasPA: null,
      checks: {}
    };
    
    localStorage.removeItem(STORAGE_KEY);
    
    document.querySelectorAll('#system-checklist input[type="checkbox"]').forEach(function(cb) {
      cb.checked = false;
    });
    
    document.querySelectorAll('.sc-kin-option.selected').forEach(function(opt) {
      opt.classList.remove('selected');
    });
    
    document.querySelectorAll('[id$="-result-case1"], [id$="-result-case2"], [id$="-result-case3"], [id$="-result-case4"], [id$="-result-case5"], [id$="-result-case6"], [id$="-result-case7"]').forEach(function(el) {
      el.classList.remove('show');
    });
    
    document.getElementById('sc-h5-bed').style.display = 'none';
    document.getElementById('sc-mesh-cmd').style.display = 'none';
    document.getElementById('sc-shaper-cmd').style.display = 'none';
    document.getElementById('sc-pa-config').style.display = 'none';
    document.getElementById('sc-section-advanced').classList.add('sc-hidden');
    
    document.getElementById('sc-motor-content').innerHTML = '<p><em>请在上方选择运动学类型以查看电机校准步骤。</em></p>';
    
    SECTIONS.forEach(function(section) {
      var badge = document.getElementById('sc-badge-' + section);
      if (badge) {
        var content = document.getElementById('sc-content-' + section);
        if (content) {
          var total = content.querySelectorAll('input[type="checkbox"]').length;
          badge.textContent = '0/' + total;
        }
      }
    });
    
    updateProgress();
  }

  function exportJSON() {
    var data = {
      timestamp: new Date().toISOString(),
      kinematics: state.kinematics,
      endstopType: state.endstopType,
      hasBed: state.hasBed,
      hasMesh: state.hasMesh,
      hasShaper: state.hasShaper,
      hasPA: state.hasPA,
      sections: {}
    };
    
    SECTIONS.forEach(function(section) {
      var content = document.getElementById('sc-content-' + section);
      if (content) {
        var items = [];
        content.querySelectorAll('.sc-item').forEach(function(item) {
          var checkbox = item.querySelector('input[type="checkbox"]');
          var title = item.querySelector('.sc-item-title');
          if (checkbox && title) {
            items.push({
              id: checkbox.id,
              title: title.textContent,
              checked: checkbox.checked
            });
          }
        });
        data.sections[section] = items;
      }
    });
    
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = 'kalico-checklist-' + new Date().toISOString().slice(0,10) + '.json';
    a.click();
    URL.revokeObjectURL(url);
  }

  function exportPDF() {
    window.print();
  }

  function init() {
    loadState();
    updateProgress();
  }

  window.SC = {
    selectKinematics: selectKinematics,
    selectEndstop: selectEndstop,
    selectBed: selectBed,
    selectMesh: selectMesh,
    selectShaper: selectShaper,
    selectPA: selectPA,
    toggleSection: toggleSection,
    updateCheck: updateCheck,
    selectDiagnostic: selectDiagnostic,
    resetAll: resetAll,
    exportJSON: exportJSON,
    exportPDF: exportPDF
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>

</div>
