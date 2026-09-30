# System Configuration Checklist

This interactive checklist helps you diagnose and verify your Klipper/Kalico printer configuration step by step. Select your printer's kinematics type first, then work through each section.

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
    <h2>System Configuration Checklist</h2>
    <p>Step-by-step diagnostic for Klipper/Kalico printer configuration</p>
  </div>
</div>

<div class="sc-body">
  <div class="sc-controls">
    <button class="sc-btn sc-btn-danger" onclick="SC.resetAll()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17.65 6.35A7.958 7.958 0 0012 4c-4.42 0-7.99 3.58-7.99 8s3.57 8 7.99 8c3.73 0 6.84-2.55 7.73-6h-2.08A5.99 5.99 0 0112 18c-3.31 0-6-2.69-6-6s2.69-6 6-6c1.66 0 3.14.69 4.22 1.78L13 11h7V4l-2.35 2.35z"/></svg>
      Reset All
    </button>
    <button class="sc-btn sc-btn-info" onclick="SC.exportJSON()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
      Export JSON
    </button>
    <button class="sc-btn sc-btn-success" onclick="SC.exportPDF()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
      Print / PDF
    </button>
  </div>

  <div class="sc-progress">
    <div class="sc-progress-bar" id="sc-progress-bar" style="width: 0%">0%</div>
  </div>

  <!-- Kinematics Selector -->
  <div class="sc-kinematics-selector">
    <h3>⚠️ Select Your Printer Kinematics Type</h3>
    
    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Standard 3D Printers</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="cartesian" onclick="SC.selectKinematics(this)">Cartesian</div>
        <div class="sc-kin-option" data-kin="corexy" onclick="SC.selectKinematics(this)">CoreXY</div>
        <div class="sc-kin-option" data-kin="corexz" onclick="SC.selectKinematics(this)">CoreXZ</div>
        <div class="sc-kin-option" data-kin="delta" onclick="SC.selectKinematics(this)">Delta</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Core Variants</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="coreyx" onclick="SC.selectKinematics(this)">CoreYX</div>
        <div class="sc-kin-option" data-kin="coreyz" onclick="SC.selectKinematics(this)">CoreYZ</div>
        <div class="sc-kin-option" data-kin="corezx" onclick="SC.selectKinematics(this)">CoreZX</div>
        <div class="sc-kin-option" data-kin="corezy" onclick="SC.selectKinematics(this)">CoreZY</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Limited Variants (per-axis velocity/accel limits)</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="limited_cartesian" onclick="SC.selectKinematics(this)">Limited Cartesian</div>
        <div class="sc-kin-option" data-kin="limited_corexy" onclick="SC.selectKinematics(this)">Limited CoreXY</div>
        <div class="sc-kin-option" data-kin="limited_corexz" onclick="SC.selectKinematics(this)">Limited CoreXZ</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Hybrid / IDEX Structures</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="hybrid_corexy" onclick="SC.selectKinematics(this)">Hybrid CoreXY</div>
        <div class="sc-kin-option" data-kin="hybrid_corexz" onclick="SC.selectKinematics(this)">Hybrid CoreXZ</div>
      </div>
    </div>

    <div class="sc-kin-group">
      <div class="sc-kin-group-title">Special Structures</div>
      <div class="sc-kin-options">
        <div class="sc-kin-option" data-kin="deltesian" onclick="SC.selectKinematics(this)">Deltesian</div>
        <div class="sc-kin-option" data-kin="polar" onclick="SC.selectKinematics(this)">Polar</div>
        <div class="sc-kin-option" data-kin="rotary_delta" onclick="SC.selectKinematics(this)">Rotary Delta</div>
        <div class="sc-kin-option" data-kin="scara" onclick="SC.selectKinematics(this)">SCARA</div>
        <div class="sc-kin-option" data-kin="tpara" onclick="SC.selectKinematics(this)">TPARA</div>
        <div class="sc-kin-option" data-kin="polargraph" onclick="SC.selectKinematics(this)">Polargraph</div>
        <div class="sc-kin-option" data-kin="belt" onclick="SC.selectKinematics(this)">Belt (Conveyor)</div>
        <div class="sc-kin-option" data-kin="robot_arm" onclick="SC.selectKinematics(this)">Robot Arm</div>
        <div class="sc-kin-option" data-kin="foam_cutter" onclick="SC.selectKinematics(this)">Foam Cutter</div>
      </div>
    </div>
  </div>

  <!-- Section 1: Power & Hardware -->
  <div class="sc-section" id="sc-section-power">
    <div class="sc-section-header" onclick="SC.toggleSection('power')">
      <span class="arrow">▼</span>
      <span>🔌 Power & Hardware Connection</span>
      <span class="sc-section-badge" id="sc-badge-power">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-power">
      <div class="sc-item">
        <input type="checkbox" id="sc-p1" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">Power Supply Voltage Match</div>
          <div class="sc-item-desc">Verify the PSU output voltage matches your motherboard requirements (typically 24V for most boards).</div>
          <div class="sc-item-tip">💡 Check the label on your PSU and compare with motherboard specs.</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p2" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">Motherboard Power Connection</div>
          <div class="sc-item-desc">Ensure all power cables are properly connected to the motherboard, drivers, and heated bed (if applicable).</div>
          <div class="sc-item-warning">⚠️ Always disconnect power before checking wiring!</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p3" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">MCU Connection Status</div>
          <div class="sc-item-desc">Verify MCU is recognized by the host. Run <code>STATUS</code> command to confirm communication.</div>
          <div class="sc-item-command">STATUS</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p4" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">Stepper Drivers Installed</div>
          <div class="sc-item-desc">Verify all stepper drivers are properly seated in their sockets and orientation is correct.</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-p5" onchange="SC.updateCheck('power')">
        <div class="sc-item-info">
          <div class="sc-item-title">CAN Bus Connection (if applicable)</div>
          <div class="sc-item-desc">If using CAN bus, verify the CAN interface is up and MCU is reachable.</div>
          <div class="sc-item-command">bash-canbus.sh canscan</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Section 2: Endstops -->
  <div class="sc-section" id="sc-section-endstop">
    <div class="sc-section-header" onclick="SC.toggleSection('endstop')">
      <span class="arrow">▼</span>
      <span>🔴 Endstop Switch Check</span>
      <span class="sc-section-badge" id="sc-badge-endstop">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-endstop">
      <div class="sc-item">
        <input type="checkbox" id="sc-e1" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">Select Endstop Type</div>
          <div class="sc-item-desc">Choose the type of endstop switches you are using:</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-endstop="micro" onclick="SC.selectEndstop(this)">Microswitch (NC)</div>
            <div class="sc-kin-option" data-endstop="tap" onclick="SC.selectEndstop(this)">Voron TAP</div>
            <div class="sc-kin-option" data-endstop="optical" onclick="SC.selectEndstop(this)">Optical</div>
            <div class="sc-kin-option" data-endstop="inductive" onclick="SC.selectEndstop(this)">Inductive/Capacitive</div>
            <div class="sc-kin-option" data-endstop="sensorless" onclick="SC.selectEndstop(this)">Sensorless Homing</div>
          </div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e2" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">Endstop Wiring Check</div>
          <div class="sc-item-desc">Verify endstop wiring is correct. For microswitches, use NC (Normally Closed) for safety.</div>
          <div class="sc-item-danger">🔴 Three-wire microswitches: Cut the 5V wire (usually red) to prevent short circuits on FLY boards!</div>
          <div class="sc-item-config">[stepper_x]
endstop_pin: ^!PD9  # ^ = pullup, ! = invert for NC switch</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e3" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">QUERY_ENDSTOPS Test</div>
          <div class="sc-item-desc">Run this command to verify endstop states. All should show "open" when not triggered.</div>
          <div class="sc-item-command">QUERY_ENDSTOPS</div>
          <div class="sc-item-tip">💡 Manually trigger each endstop and verify it shows "TRIGGERED".</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e4" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">Endstop Trigger Direction</div>
          <div class="sc-item-desc">Verify the trigger logic is correct: "open" when not triggered, "TRIGGERED" when pressed.</div>
          <div class="sc-item-tip">💡 If inverted, add or remove <code>!</code> in endstop_pin. If no change, check wiring and add <code>^</code> for pullup.</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-e5" onchange="SC.updateCheck('endstop')">
        <div class="sc-item-info">
          <div class="sc-item-title">Pullup Resistor Configuration</div>
          <div class="sc-item-desc">Ensure <code>^</code> is present in endstop_pin for most endstop types (microswitch, optical, etc.).</div>
          <div class="sc-item-config">endstop_pin: ^!PD9  # ^ enables internal pullup resistor</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Section 3: Motor Direction (dynamic based on kinematics) -->
  <div class="sc-section" id="sc-section-motor">
    <div class="sc-section-header" onclick="SC.toggleSection('motor')">
      <span class="arrow">▼</span>
      <span>⚙️ Motor Direction Calibration</span>
      <span class="sc-section-badge" id="sc-badge-motor">0/4</span>
    </div>
    <div class="sc-section-content" id="sc-content-motor">
      <!-- Content populated dynamically by JavaScript -->
      <div id="sc-motor-content">
        <p><em>Please select your kinematics type above to see motor calibration steps.</em></p>
      </div>
    </div>
  </div>

  <!-- Section 4: Heating System -->
  <div class="sc-section" id="sc-section-heat">
    <div class="sc-section-header" onclick="SC.toggleSection('heat')">
      <span class="arrow">▼</span>
      <span>🌡️ Heating System Check</span>
      <span class="sc-section-badge" id="sc-badge-heat">0/6</span>
    </div>
    <div class="sc-section-content" id="sc-content-heat">
      <div class="sc-item">
        <input type="checkbox" id="sc-h1" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">Extruder Temperature Reading</div>
          <div class="sc-item-desc">Verify the extruder temperature is being reported and is stable (not rising on its own).</div>
          <div class="sc-item-danger">🔴 If temperature is rising without heating command, disconnect power immediately!</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h2" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">Heated Bed (if applicable)</div>
          <div class="sc-item-desc">Check if your printer has a heated bed. If yes, verify temperature reading is stable.</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-bed="yes" onclick="SC.selectBed(this)">Has Heated Bed</div>
            <div class="sc-kin-option" data-bed="no" onclick="SC.selectBed(this)">No Heated Bed</div>
          </div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h3" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">M112 Emergency Stop Test</div>
          <div class="sc-item-desc">Send M112 command to test emergency stop. Verify Klipper enters shutdown state. Clear with FIRMWARE_RESTART.</div>
          <div class="sc-item-command">M112
# Wait for shutdown, then:
FIRMWARE_RESTART</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h4" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">Extruder Heating Test</div>
          <div class="sc-item-desc">Set extruder to 50°C and verify temperature rises. Monitor the temperature graph.</div>
          <div class="sc-item-command">M104 S50  # Set extruder to 50°C
# Wait 30-60 seconds, verify temp rises
M104 S0   # Turn off</div>
          <div class="sc-item-tip">💡 If temp doesn't rise, check heater_pin configuration.</div>
        </div>
      </div>
      <div class="sc-item" id="sc-h5-bed" style="display:none;">
        <input type="checkbox" id="sc-h5" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">Heated Bed Heating Test</div>
          <div class="sc-item-desc">Set bed to 50°C and verify temperature rises.</div>
          <div class="sc-item-command">M140 S50  # Set bed to 50°C
# Wait 30-60 seconds, verify temp rises
M140 S0   # Turn off</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-h6" onchange="SC.updateCheck('heat')">
        <div class="sc-item-info">
          <div class="sc-item-title">PID Calibration</div>
          <div class="sc-item-desc">After verifying heating works, run PID calibration for stable temperature control.</div>
          <div class="sc-item-command">PID_CALIBRATE HEATER=extruder TARGET=200
SAVE_CONFIG
# If heated bed:
PID_CALIBRATE HEATER=heater_bed TARGET=60
SAVE_CONFIG</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Section 5: Calibration -->
  <div class="sc-section" id="sc-section-calibration">
    <div class="sc-section-header" onclick="SC.toggleSection('calibration')">
      <span class="arrow">▼</span>
      <span>📏 Calibration</span>
      <span class="sc-section-badge" id="sc-badge-calibration">0/5</span>
    </div>
    <div class="sc-section-content" id="sc-content-calibration">
      <div class="sc-item">
        <input type="checkbox" id="sc-c1" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Rotation Distance Calibration</div>
          <div class="sc-item-desc">Calibrate extruder rotation distance for accurate extrusion. Mark filament, extrude 50mm, measure actual distance.</div>
          <div class="sc-item-command">G91
G1 E50 F60  # Extrude 50mm at slow speed
# Measure actual extruded length
# new_rotation_distance = old_value * actual_length / 50</div>
          <div class="sc-item-config">[extruder]
rotation_distance: 23.280  # Update with calibrated value</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c2" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Z Offset Calibration</div>
          <div class="sc-item-desc">Calibrate nozzle-to-bed distance using paper method. Adjust until paper has slight resistance.</div>
          <div class="sc-item-command">G28
G90
G1 X150 Y150 F3000  # Move to center
G1 Z2 F300
# Use baby stepping or adjust Z offset
# For mechanical endstop: Z_OFFSET_APPLY_ENDSTOP
# For probe: Z_OFFSET_APPLY_PROBE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c3" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Bed Mesh Calibration (if applicable)</div>
          <div class="sc-item-desc">If using automatic bed leveling, run bed mesh calibration.</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-mesh="yes" onclick="SC.selectMesh(this)">Uses Bed Mesh</div>
            <div class="sc-kin-option" data-mesh="no" onclick="SC.selectMesh(this)">No Bed Mesh</div>
          </div>
          <div class="sc-item-command" id="sc-mesh-cmd" style="display:none;">BED_MESH_CALIBRATE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c4" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Input Shaper Calibration (if applicable)</div>
          <div class="sc-item-desc">If using ADXL345 accelerometer, calibrate input shaper to reduce ringing.</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-shaper="yes" onclick="SC.selectShaper(this)">Uses Input Shaper</div>
            <div class="sc-kin-option" data-shaper="no" onclick="SC.selectShaper(this)">No Input Shaper</div>
          </div>
          <div class="sc-item-command" id="sc-shaper-cmd" style="display:none;">SHAPER_CALIBRATE
SAVE_CONFIG</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-c5" onchange="SC.updateCheck('calibration')">
        <div class="sc-item-info">
          <div class="sc-item-title">Pressure Advance Calibration (if applicable)</div>
          <div class="sc-item-desc">Calibrate Pressure Advance for better extrusion control at corners.</div>
          <div class="sc-kin-options" style="margin-top: 8px;">
            <div class="sc-kin-option" data-pa="yes" onclick="SC.selectPA(this)">Uses PA</div>
            <div class="sc-kin-option" data-pa="no" onclick="SC.selectPA(this)">No PA</div>
          </div>
          <div class="sc-item-config" id="sc-pa-config" style="display:none;">[extruder]
pressure_advance: 0.04
pressure_advance_smooth_time: 0.040</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Section 6: Optional Peripherals -->
  <div class="sc-section" id="sc-section-peripheral">
    <div class="sc-section-header" onclick="SC.toggleSection('peripheral')">
      <span class="arrow">▼</span>
      <span>🔧 Optional Peripherals</span>
      <span class="sc-section-badge" id="sc-badge-peripheral">0/9</span>
    </div>
    <div class="sc-section-content" id="sc-content-peripheral">
      <div class="sc-item">
        <input type="checkbox" id="sc-per1" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">BLTouch / CR Touch</div>
          <div class="sc-item-desc">Auto bed leveling probe. Check deployment, stowing, and Z endstop function.</div>
          <div class="sc-item-command">DEPLOY_PROBE
# Verify probe deploys
QUERY_ENDSTOPS  # Should show probe triggered
STOW_PROBE</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per2" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Voron TAP</div>
          <div class="sc-item-desc">Nozzle-based probe. Verify probe pin responds to nozzle contact.</div>
          <div class="sc-item-config">[probe]
pin: ^PC15
x_offset: 0
y_offset: 0
# z_offset: 0  # Set via PROBE_CALIBRATE</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per3" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Multi-Z Axis</div>
          <div class="sc-item-desc">Multiple Z stepper motors (dual/triple/quad Z). Verify all Z motors move correctly.</div>
          <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z
STEPPER_BUZZ STEPPER=stepper_z1
# STEPPER_BUZZ STEPPER=stepper_z2 (if applicable)
# STEPPER_BUZZ STEPPER=stepper_z3 (if applicable)</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per4" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Z Tilt Adjustment</div>
          <div class="sc-item-desc">For multi-Z printers, run Z tilt adjustment to level the gantry.</div>
          <div class="sc-item-command">Z_TILT_ADJUST</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per5" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Skew Correction</div>
          <div class="sc-item-desc">Compensate for mechanical skew in XY plane.</div>
          <div class="sc-item-config">[skew_correction]</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per6" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Filament Sensor</div>
          <div class="sc-item-desc">Filament runout detection sensor.</div>
          <div class="sc-item-command">FILAMENT_SENSOR_ENABLE SENSOR=runout
# Test by simulating runout</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per7" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">Servo</div>
          <div class="sc-item-desc">Servo motor (e.g., for pen lift, bed leveling).</div>
          <div class="sc-item-command">SET_SERVO SERVO=servo0 ANGLE=0
SET_SERVO SERVO=servo0 ANGLE=90</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per8" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">RGB LED Strip</div>
          <div class="sc-item-desc">Addressable LED strip for status indication.</div>
          <div class="sc-item-command">SET_LED LED=led_print LED=white TRANSMIT=1</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per9" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">ADXL345 Accelerometer</div>
          <div class="sc-item-desc">For input shaper calibration. Verify SPI connection.</div>
          <div class="sc-item-command">ACCELEROMETER_QUERY  # Should return values</div>
        </div>
      </div>
      <div class="sc-item">
        <input type="checkbox" id="sc-per10" onchange="SC.updateCheck('peripheral')">
        <div class="sc-item-info">
          <div class="sc-item-title">IDEX Dual Carriage</div>
          <div class="sc-item-desc">Independent dual extrusion with two print heads.</div>
          <div class="sc-item-command">SET_DUAL_CARRIAGE CARRIAGE=1 MODE=PRIMARY
# Test independent movement</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Section 7: Advanced (dynamic based on kinematics) -->
  <div class="sc-section sc-hidden" id="sc-section-advanced">
    <div class="sc-section-header" onclick="SC.toggleSection('advanced')">
      <span class="arrow">▼</span>
      <span>🚀 Advanced Kinematics Settings</span>
      <span class="sc-section-badge" id="sc-badge-advanced">0/3</span>
    </div>
    <div class="sc-section-content" id="sc-content-advanced">
      <div id="sc-advanced-content">
        <!-- Populated dynamically -->
      </div>
    </div>
  </div>

  <!-- Export Section -->
  <div class="sc-export-section">
    <button class="sc-btn sc-btn-info" onclick="SC.exportJSON()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/></svg>
      Export JSON Report
    </button>
    <button class="sc-btn sc-btn-success" onclick="SC.exportPDF()">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M19 8H5c-1.66 0-3 1.34-3 3v6h4v4h12v-4h4v-6c0-1.66-1.34-3-3-3zm-3 11H8v-5h8v5zm3-7c-.55 0-1-.45-1-1s.45-1 1-1 1 .45 1 1-.45 1-1 1zm-1-9H6v4h12V3z"/></svg>
      Print / Save PDF
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

  // Load state from localStorage
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

  // Save state to localStorage
  function saveState() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch(e) {
      console.warn('Failed to save checklist state:', e);
    }
  }

  // Restore UI from state
  function restoreUI() {
    // Restore checkboxes
    Object.keys(state.checks).forEach(id => {
      const el = document.getElementById(id);
      if (el) el.checked = state.checks[id];
    });

    // Restore kinematics selection
    if (state.kinematics) {
      const kinEl = document.querySelector(`.sc-kin-option[data-kin="${state.kinematics}"]`);
      if (kinEl) {
        selectKinematics(kinEl, false);
      }
    }

    // Restore endstop selection
    if (state.endstopType) {
      const endEl = document.querySelector(`.sc-kin-option[data-endstop="${state.endstopType}"]`);
      if (endEl) endEl.classList.add('selected');
    }

    // Restore bed selection
    if (state.hasBed !== null) {
      const bedEl = document.querySelector(`.sc-kin-option[data-bed="${state.hasBed}"]`);
      if (bedEl) {
        bedEl.classList.add('selected');
        document.getElementById('sc-h5-bed').style.display = state.hasBed === 'yes' ? 'flex' : 'none';
      }
    }

    // Restore mesh selection
    if (state.hasMesh !== null) {
      const meshEl = document.querySelector(`.sc-kin-option[data-mesh="${state.hasMesh}"]`);
      if (meshEl) {
        meshEl.classList.add('selected');
        document.getElementById('sc-mesh-cmd').style.display = state.hasMesh === 'yes' ? 'block' : 'none';
      }
    }

    // Restore shaper selection
    if (state.hasShaper !== null) {
      const shaperEl = document.querySelector(`.sc-kin-option[data-shaper="${state.hasShaper}"]`);
      if (shaperEl) {
        shaperEl.classList.add('selected');
        document.getElementById('sc-shaper-cmd').style.display = state.hasShaper === 'yes' ? 'block' : 'none';
      }
    }

    // Restore PA selection
    if (state.hasPA !== null) {
      const paEl = document.querySelector(`.sc-kin-option[data-pa="${state.hasPA}"]`);
      if (paEl) {
        paEl.classList.add('selected');
        document.getElementById('sc-pa-config').style.display = state.hasPA === 'yes' ? 'block' : 'none';
      }
    }

    updateProgress();
  }

  // Select kinematics type
  function selectKinematics(el, save = true) {
    document.querySelectorAll('.sc-kinematics-selector .sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.kinematics = el.dataset.kin;
    
    updateMotorSection();
    updateAdvancedSection();
    updateProgress();
    
    if (save) saveState();
  }

  // Select endstop type
  function selectEndstop(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.endstopType = el.dataset.endstop;
    saveState();
  }

  // Select bed option
  function selectBed(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasBed = el.dataset.bed;
    document.getElementById('sc-h5-bed').style.display = state.hasBed === 'yes' ? 'flex' : 'none';
    updateProgress();
    saveState();
  }

  // Select mesh option
  function selectMesh(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasMesh = el.dataset.mesh;
    document.getElementById('sc-mesh-cmd').style.display = state.hasMesh === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  // Select shaper option
  function selectShaper(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasShaper = el.dataset.shaper;
    document.getElementById('sc-shaper-cmd').style.display = state.hasShaper === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  // Select PA option
  function selectPA(el) {
    el.parentElement.querySelectorAll('.sc-kin-option').forEach(opt => {
      opt.classList.remove('selected');
    });
    el.classList.add('selected');
    state.hasPA = el.dataset.pa;
    document.getElementById('sc-pa-config').style.display = state.hasPA === 'yes' ? 'block' : 'none';
    updateProgress();
    saveState();
  }

  // Toggle section collapse
  function toggleSection(section) {
    const header = document.querySelector(`#sc-section-${section} .sc-section-header`);
    const content = document.getElementById(`sc-content-${section}`);
    header.classList.toggle('collapsed');
    content.classList.toggle('hidden');
  }

  // Update checkbox state and save
  function updateCheck(section) {
    const content = document.getElementById(`sc-content-${section}`);
    const checkboxes = content.querySelectorAll('input[type="checkbox"]');
    let checked = 0;
    checkboxes.forEach(cb => {
      state.checks[cb.id] = cb.checked;
      if (cb.checked) checked++;
    });
    document.getElementById(`sc-badge-${section}`).textContent = `${checked}/${checkboxes.length}`;
    updateProgress();
    saveState();
  }

  // Update progress bar
  function updateProgress() {
    let total = 0;
    let checked = 0;
    SECTIONS.forEach(section => {
      if (section === 'advanced' && !document.getElementById('sc-section-advanced').classList.contains('sc-hidden')) {
        const content = document.getElementById(`sc-content-${section}`);
        if (content) {
          const cbs = content.querySelectorAll('input[type="checkbox"]');
          total += cbs.length;
          cbs.forEach(cb => { if (cb.checked) checked++; });
        }
      } else if (section !== 'advanced') {
        const content = document.getElementById(`sc-content-${section}`);
        if (content) {
          const cbs = content.querySelectorAll('input[type="checkbox"]');
          total += cbs.length;
          cbs.forEach(cb => { if (cb.checked) checked++; });
        }
      }
    });
    
    // Add kinematics selection as a check
    total++;
    if (state.kinematics) checked++;
    
    const pct = total > 0 ? Math.round((checked / total) * 100) : 0;
    const bar = document.getElementById('sc-progress-bar');
    bar.style.width = pct + '%';
    bar.textContent = pct + '%';
  }

  // Update motor section based on kinematics
  function updateMotorSection() {
    const container = document.getElementById('sc-motor-content');
    const kin = state.kinematics;
    
    if (!kin) {
      container.innerHTML = '<p><em>Please select your kinematics type above to see motor calibration steps.</em></p>';
      return;
    }

    let html = '';
    
    // Group kinematics by type for motor diagnostics
    const corexyVariants = ['corexy', 'coreyx'];
    const corexzVariants = ['corexz', 'coreyz', 'corezx', 'corezy'];
    const deltaTypes = ['delta', 'rotary_delta'];
    const armTypes = ['scara', 'tpara', 'robot_arm'];
    
    if (corexyVariants.includes(kin) || kin === 'limited_corexy' || kin === 'hybrid_corexy') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">X Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify X stepper motor moves correctly. Motor should oscillate 1mm forward and back.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Y Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Y stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Z stepper motor moves correctly. <strong>Z must move UP first, then DOWN</strong>.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
            <div class="sc-item-warning">⚠️ If Z moves down first, invert dir_pin by adding/removing <code>!</code></div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">CoreXY Direction Diagnostic</div>
            <div class="sc-item-desc">Select the issue you observe to get a solution:</div>
            <div class="sc-diagnostic">
              <h4>⚙️ CoreXY Motor Direction Diagnosis</h4>
              <p style="margin:0 0 8px;font-size:0.9em;">Move the toolhead manually via <code>G91</code> + <code>G1 X10 F3000</code> and <code>G1 Y10 F3000</code>. Observe which motor actually moves and the direction.</p>
              
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case1')">
                <input type="radio" name="corexy_diag" id="corexy-case1">
                <div>
                  <strong>Case 1:</strong> XY axes swapped AND directions reversed
                  <div class="sc-diagnostic-result" id="corexy-result-case1">
                    <strong>Solution:</strong> Swap X motor wiring (exchange any two phase wires of X motor).
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case2')">
                <input type="radio" name="corexy_diag" id="corexy-case2">
                <div>
                  <strong>Case 2:</strong> XY axes swapped, but directions correct
                  <div class="sc-diagnostic-result" id="corexy-result-case2">
                    <strong>Solution:</strong> Swap Y motor wiring (exchange any two phase wires of Y motor).
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case3')">
                <input type="radio" name="corexy_diag" id="corexy-case3">
                <div>
                  <strong>Case 3:</strong> XY swapped, X direction correct, Y reversed
                  <div class="sc-diagnostic-result" id="corexy-result-case3">
                    <strong>Solution:</strong> 1) Swap X motor wiring. 2) Swap X and Y motor cables at the board.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case4')">
                <input type="radio" name="corexy_diag" id="corexy-case4">
                <div>
                  <strong>Case 4:</strong> XY swapped, X reversed, Y correct
                  <div class="sc-diagnostic-result" id="corexy-result-case4">
                    <strong>Solution:</strong> 1) Swap Y motor wiring. 2) Swap X and Y motor cables at the board.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case5')">
                <input type="radio" name="corexy_diag" id="corexy-case5">
                <div>
                  <strong>Case 5:</strong> XY axes correct, but both directions reversed
                  <div class="sc-diagnostic-result" id="corexy-result-case5">
                    <strong>Solution:</strong> Swap both X and Y motor wiring (invert both).
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case6')">
                <input type="radio" name="corexy_diag" id="corexy-case6">
                <div>
                  <strong>Case 6:</strong> XY correct, X correct, Y reversed
                  <div class="sc-diagnostic-result" id="corexy-result-case6">
                    <strong>Solution:</strong> Swap X and Y motor cables at the board.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexy', 'case7')">
                <input type="radio" name="corexy_diag" id="corexy-case7">
                <div>
                  <strong>Case 7:</strong> XY correct, X reversed, Y correct
                  <div class="sc-diagnostic-result" id="corexy-result-case7">
                    <strong>Solution:</strong> 1) Swap X and Y motor cables. 2) Swap both X and Y motor wiring.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (corexzVariants.includes(kin) || kin === 'limited_corexz' || kin === 'hybrid_corexz') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">X Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify X stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Y Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Y stepper motor moves correctly (independent axis).</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Z stepper motor moves correctly. <strong>Z must move UP first</strong>.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
            <div class="sc-item-warning">⚠️ If Z moves down first, invert dir_pin by adding/removing <code>!</code></div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">CoreXZ Direction Diagnostic</div>
            <div class="sc-item-desc">X and Z are coupled in CoreXZ. Select the issue you observe:</div>
            <div class="sc-diagnostic">
              <h4>⚙️ CoreXZ Motor Direction Diagnosis</h4>
              <p style="margin:0 0 8px;font-size:0.9em;">Use <code>G91</code> + <code>G1 X10 F3000</code> and <code>G1 Z10 F3000</code> to test.</p>
              
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case1')">
                <input type="radio" name="corexz_diag" id="corexz-case1">
                <div>
                  <strong>Case 1:</strong> XZ axes swapped AND directions reversed
                  <div class="sc-diagnostic-result" id="corexz-result-case1">
                    <strong>Solution:</strong> Swap X motor wiring (exchange any two phase wires).
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case2')">
                <input type="radio" name="corexz_diag" id="corexz-case2">
                <div>
                  <strong>Case 2:</strong> XZ swapped, directions correct
                  <div class="sc-diagnostic-result" id="corexz-result-case2">
                    <strong>Solution:</strong> Swap Z motor wiring.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case3')">
                <input type="radio" name="corexz_diag" id="corexz-case3">
                <div>
                  <strong>Case 3:</strong> XZ swapped, X correct, Z reversed
                  <div class="sc-diagnostic-result" id="corexz-result-case3">
                    <strong>Solution:</strong> 1) Swap X motor wiring. 2) Swap X and Z motor cables.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case4')">
                <input type="radio" name="corexz_diag" id="corexz-case4">
                <div>
                  <strong>Case 4:</strong> XZ swapped, X reversed, Z correct
                  <div class="sc-diagnostic-result" id="corexz-result-case4">
                    <strong>Solution:</strong> 1) Swap Z motor wiring. 2) Swap X and Z motor cables.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case5')">
                <input type="radio" name="corexz_diag" id="corexz-case5">
                <div>
                  <strong>Case 5:</strong> XZ correct, both directions reversed
                  <div class="sc-diagnostic-result" id="corexz-result-case5">
                    <strong>Solution:</strong> Swap both X and Z motor wiring.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case6')">
                <input type="radio" name="corexz_diag" id="corexz-case6">
                <div>
                  <strong>Case 6:</strong> XZ correct, X correct, Z reversed
                  <div class="sc-diagnostic-result" id="corexz-result-case6">
                    <strong>Solution:</strong> Swap X and Z motor cables at the board.
                  </div>
                </div>
              </div>
              <div class="sc-diagnostic-option" onclick="SC.selectDiagnostic('corexz', 'case7')">
                <input type="radio" name="corexz_diag" id="corexz-case7">
                <div>
                  <strong>Case 7:</strong> XZ correct, X reversed, Z correct
                  <div class="sc-diagnostic-result" id="corexz-result-case7">
                    <strong>Solution:</strong> 1) Swap X and Z motor cables. 2) Swap both motor wiring.
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } else if (deltaTypes.includes(kin)) {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Tower A STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Tower A stepper motor moves correctly (should move UP first).</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Tower B STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Tower B stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Tower C STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Tower C stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Delta Calibration</div>
            <div class="sc-item-desc">Run DELTA_CALIBRATE to calibrate delta geometry. Save results after calibration.</div>
            <div class="sc-item-command">DELTA_CALIBRATE
# Follow prompts to probe calibration points
SAVE_CONFIG</div>
            <div class="sc-item-config">[printer]
kinematics: delta
delta_radius: 100  # Calibrated value

[stepper_a]
arm_length: 200  # Must be > delta_radius</div>
          </div>
        </div>
      `;
    } else if (kin === 'scara') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Shoulder Motor (Stepper A) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify shoulder stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Elbow Motor (Stepper B) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify elbow stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Z stepper motor moves correctly (should move UP first).</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">SCARA Arm Length Verification</div>
            <div class="sc-item-desc">Verify linkage lengths are accurately measured and configured.</div>
            <div class="sc-item-config">[scara]
linkage_1: 100  # Inner arm length (mm)
linkage_2: 100  # Outer arm length (mm)
offset_x: 0     # Tower offset from bed center
offset_y: 0
variant: morgan  # or "mp"</div>
          </div>
        </div>
      `;
    } else if (kin === 'tpara') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Base Motor (Stepper A) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify base rotation stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Shoulder Motor (Stepper B) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify shoulder stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Elbow Motor (Stepper C) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify elbow stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">TPARA Arm Length Verification</div>
            <div class="sc-item-desc">Verify linkage lengths are accurately measured.</div>
            <div class="sc-item-config">[tpara]
linkage_1: 100  # Inner arm length (mm)
linkage_2: 100  # Outer arm length (mm)</div>
          </div>
        </div>
      `;
    } else if (kin === 'polargraph') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Left Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify left stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_left</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Right Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify right stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_right</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Motor Distance Verification</div>
            <div class="sc-item-desc">Verify the distance between motors is accurately measured and configured.</div>
            <div class="sc-item-config">[polargraph]
motor_distance_x: 400  # Distance between motor centers (mm)</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor (Pen Lift) STEPPER_BUZZ (if applicable)</div>
            <div class="sc-item-desc">If using a Z axis for pen lift, verify it works.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
          </div>
        </div>
      `;
    } else if (kin === 'belt') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">X Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify X stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Y Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Y stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor (Conveyor Belt) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify conveyor belt motor moves correctly. Note: Z axis is infinite (no homing needed).</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Bed Tilt Angle Verification</div>
            <div class="sc-item-desc">Verify bed tilt angle matches your physical setup (typically 45°).</div>
            <div class="sc-item-config">[belt]
bed_tilt: 45.0  # Must match physical angle exactly
bed_rotation_axis: y  # or "x"</div>
          </div>
        </div>
      `;
    } else if (kin === 'robot_arm') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Base Motor (Stepper A) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify base rotation stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_a</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Shoulder Motor (Stepper B) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify shoulder stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_b</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Elbow Motor (Stepper C) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify elbow stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_c</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">DH Parameter Verification</div>
            <div class="sc-item-desc">Verify link lengths are accurately measured and configured.</div>
            <div class="sc-item-config">[robot_arm]
d1: 100   # Base height (mm)
a1: 50    # Link 1 length (mm)
a2: 200   # Link 2 length (mm)
a3: 150   # Link 3 length (mm)</div>
          </div>
        </div>
      `;
    } else if (kin === 'foam_cutter') {
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">X Motor (Wire Top) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify X stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Y Motor (Wire Top) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Y stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">U Motor (Wire Bottom) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify U stepper motor (bottom X) moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_u</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">V Motor (Wire Bottom) STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify V stepper motor (bottom Y) moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_v</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m5" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Wire Length Verification</div>
            <div class="sc-item-desc">Verify hot wire length is correctly configured. Moves will be rejected if endpoints exceed this distance.</div>
            <div class="sc-item-config">[foam_cutter]
wire_length: 500.0  # Wire length in mm</div>
          </div>
        </div>
      `;
    } else {
      // Cartesian and other simple kinematics
      html = `
        <div class="sc-item">
          <input type="checkbox" id="sc-m1" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">X Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify X stepper motor moves correctly. Motor should oscillate 1mm forward and back.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_x</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m2" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Y Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Y stepper motor moves correctly.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_y</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m3" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Z Motor STEPPER_BUZZ</div>
            <div class="sc-item-desc">Verify Z stepper motor moves correctly. <strong>Z must move UP first, then DOWN</strong>.</div>
            <div class="sc-item-command">STEPPER_BUZZ STEPPER=stepper_z</div>
            <div class="sc-item-warning">⚠️ If Z moves down first, invert dir_pin by adding/removing <code>!</code></div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-m4" onchange="SC.updateCheck('motor')">
          <div class="sc-item-info">
            <div class="sc-item-title">Motor Direction Verification</div>
            <div class="sc-item-desc">Verify all motors move in the correct direction when using G1 commands.</div>
            <div class="sc-item-command">G91
G1 X10 F3000  # X should move right
G1 Y10 F3000  # Y should move forward
G1 Z10 F300   # Z should move up
G1 X-10 F3000
G1 Y-10 F3000
G1 Z-10 F300</div>
            <div class="sc-item-tip">💡 If any axis moves in wrong direction, add or remove <code>!</code> in the dir_pin for that axis.</div>
          </div>
        </div>
      `;
    }
    
    container.innerHTML = html;
  }

  // Update advanced section based on kinematics
  function updateAdvancedSection() {
    const container = document.getElementById('sc-advanced-content');
    const section = document.getElementById('sc-section-advanced');
    const kin = state.kinematics;
    
    const limitedTypes = ['limited_cartesian', 'limited_corexy', 'limited_corexz'];
    const hybridTypes = ['hybrid_corexy', 'hybrid_corexz'];
    const multiZTypes = ['limited_cartesian', 'cartesian', 'corexy'];
    
    if (limitedTypes.includes(kin)) {
      section.classList.remove('sc-hidden');
      container.innerHTML = `
        <div class="sc-item">
          <input type="checkbox" id="sc-a1" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">Per-Axis Velocity Limits</div>
            <div class="sc-item-desc">Configure maximum velocity for each axis independently.</div>
            <div class="sc-item-config">[printer]
kinematics: ${kin}
max_velocity: 500  # Should be hypotenuse of X and Y velocities
max_accel: 5000

[${kin.replace('limited_', '')}]
max_x_velocity: 400
max_y_velocity: 300
max_z_velocity: 5
max_x_accel: 5000
max_y_accel: 4000
max_z_accel: 100</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-a2" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">Dynamic Limit Adjustment</div>
            <div class="sc-item-desc">Test the SET_KINEMATICS_LIMIT command to dynamically adjust limits.</div>
            <div class="sc-item-command">SET_KINEMATICS_LIMIT X_ACCEL=4000 Y_ACCEL=3000
# Query current limits:
SET_KINEMATICS_LIMIT QUERY=1</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-a3" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">Scale XY Accel</div>
            <div class="sc-item-desc">If enabled, per-axis acceleration limits scale proportionally with M204 value.</div>
            <div class="sc-item-config">[${kin.replace('limited_', '')}]
scale_xy_accel: True  # or False</div>
          </div>
        </div>
      `;
    } else if (hybridTypes.includes(kin)) {
      section.classList.remove('sc-hidden');
      const kinName = kin === 'hybrid_corexy' ? 'corexy' : 'corexz';
      container.innerHTML = `
        <div class="sc-item">
          <input type="checkbox" id="sc-a1" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">Dual Carriage Configuration</div>
            <div class="sc-item-desc">Configure the second carriage (toolhead) for IDEX operation.</div>
            <div class="sc-item-config">[dual_carriage]
axis: x
max_velocity: 300
max_accel: 3000
step_pin: <second_carriage_step>
dir_pin: <second_carriage_dir>
enable_pin: <second_carriage_enable></div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-a2" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">Invert Kinematics (if needed)</div>
            <div class="sc-item-desc">If motor direction is reversed, try inverting the kinematics coupling.</div>
            <div class="sc-item-config">[${kin}]
invert_kinematics: true  # or false</div>
          </div>
        </div>
        <div class="sc-item">
          <input type="checkbox" id="sc-a3" onchange="SC.updateCheck('advanced')">
          <div class="sc-item-info">
            <div class="sc-item-title">IDEX Mode Test</div>
            <div class="sc-item-desc">Test dual carriage modes: PRIMARY, COPY, MIRROR.</div>
            <div class="sc-item-command">SET_DUAL_CARRIAGE CARRIAGE=1 MODE=PRIMARY
G28 X
SET_DUAL_CARRIAGE CARRIAGE=1 MODE=COPY
# Test copy mode
SET_DUAL_CARRIAGE CARRIAGE=1 MODE=MIRROR
# Test mirror mode</div>
          </div>
        </div>
      `;
    } else {
      section.classList.add('sc-hidden');
    }
  }

  // CoreXY/CoreXZ diagnostic selection
  function selectDiagnostic(type, caseId) {
    document.querySelectorAll(`[id^="${type}-result-"]`).forEach(el => {
      el.classList.remove('show');
    });
    const result = document.getElementById(`${type}-result-${caseId}`);
    if (result) {
      result.classList.add('show');
    }
  }

  // Reset all checks
  function resetAll() {
    if (!confirm('Are you sure you want to reset all checklist items? This cannot be undone.')) {
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
    
    // Reset all checkboxes
    document.querySelectorAll('#system-checklist input[type="checkbox"]').forEach(cb => {
      cb.checked = false;
    });
    
    // Reset all selections
    document.querySelectorAll('.sc-kin-option.selected').forEach(opt => {
      opt.classList.remove('selected');
    });
    
    // Reset diagnostic results
    document.querySelectorAll('[id$="-result-case1"], [id$="-result-case2"], [id$="-result-case3"], [id$="-result-case4"], [id$="-result-case5"], [id$="-result-case6"], [id$="-result-case7"]').forEach(el => {
      el.classList.remove('show');
    });
    
    // Hide conditional elements
    document.getElementById('sc-h5-bed').style.display = 'none';
    document.getElementById('sc-mesh-cmd').style.display = 'none';
    document.getElementById('sc-shaper-cmd').style.display = 'none';
    document.getElementById('sc-pa-config').style.display = 'none';
    document.getElementById('sc-section-advanced').classList.add('sc-hidden');
    
    // Reset motor section
    document.getElementById('sc-motor-content').innerHTML = '<p><em>Please select your kinematics type above to see motor calibration steps.</em></p>';
    
    // Reset badges
    SECTIONS.forEach(section => {
      const badge = document.getElementById(`sc-badge-${section}`);
      if (badge) {
        const content = document.getElementById(`sc-content-${section}`);
        if (content) {
          const total = content.querySelectorAll('input[type="checkbox"]').length;
          badge.textContent = `0/${total}`;
        }
      }
    });
    
    updateProgress();
  }

  // Export as JSON
  function exportJSON() {
    const data = {
      timestamp: new Date().toISOString(),
      kinematics: state.kinematics,
      endstopType: state.endstopType,
      hasBed: state.hasBed,
      hasMesh: state.hasMesh,
      hasShaper: state.hasShaper,
      hasPA: state.hasPA,
      sections: {}
    };
    
    SECTIONS.forEach(section => {
      const content = document.getElementById(`sc-content-${section}`);
      if (content) {
        const items = [];
        content.querySelectorAll('.sc-item').forEach(item => {
          const checkbox = item.querySelector('input[type="checkbox"]');
          const title = item.querySelector('.sc-item-title');
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
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kalico-checklist-${new Date().toISOString().slice(0,10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // Export as PDF (print)
  function exportPDF() {
    window.print();
  }

  // Initialize
  function init() {
    loadState();
    updateProgress();
  }

  // Public API
  window.SC = {
    selectKinematics,
    selectEndstop,
    selectBed,
    selectMesh,
    selectShaper,
    selectPA,
    toggleSection,
    updateCheck,
    selectDiagnostic,
    resetAll,
    exportJSON,
    exportPDF
  };

  // Run on DOM ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
</script>

</div>
