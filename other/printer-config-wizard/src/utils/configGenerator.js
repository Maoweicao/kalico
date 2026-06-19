export function generateCfg(config) {
  let lines = []
  
  lines.push('# =============================================')
  lines.push('# Kalico 打印机配置文件')
  lines.push('# 由 Printer Config Wizard 生成')
  lines.push('# =============================================')
  lines.push('')
  
  if (config.mcu) {
    lines.push('[mcu]')
    if (config.mcu.serial) {
      lines.push(`serial: ${config.mcu.serial}`)
    }
    if (config.mcu.canbus_uuid) {
      lines.push(`canbus_uuid: ${config.mcu.canbus_uuid}`)
    }
    if (config.mcu.canbus_interface) {
      lines.push(`canbus_interface: ${config.mcu.canbus_interface}`)
    }
    lines.push('')
  }
  
  if (config.printer) {
    lines.push('[printer]')
    lines.push(`kinematics: ${config.printer.kinematics || 'cartesian'}`)
    lines.push(`max_velocity: ${config.printer.max_velocity || 300}`)
    lines.push(`max_accel: ${config.printer.max_accel || 3000}`)
    if (config.printer.kinematics !== 'delta') {
      lines.push(`max_z_velocity: ${config.printer.max_z_velocity || 5}`)
      lines.push(`max_z_accel: ${config.printer.max_z_accel || 100}`)
    }
    if (config.printer.square_corner_velocity !== undefined) {
      lines.push(`square_corner_velocity: ${config.printer.square_corner_velocity}`)
    }
    lines.push('')
  }
  
  const stepperNames = getStepperNames(config.printer?.kinematics || 'cartesian')
  
  for (const stepperName of stepperNames) {
    const stepper = config.steppers?.[stepperName]
    if (stepper) {
      lines.push(`[${stepperName}]`)
      if (stepper.step_pin) lines.push(`step_pin: ${stepper.step_pin}`)
      if (stepper.dir_pin) lines.push(`dir_pin: ${stepper.dir_pin}`)
      if (stepper.enable_pin) lines.push(`enable_pin: ${stepper.enable_pin}`)
      if (stepper.microsteps) lines.push(`microsteps: ${stepper.microsteps}`)
      if (stepper.rotation_distance) lines.push(`rotation_distance: ${stepper.rotation_distance}`)
      if (stepper.full_steps_per_rotation && stepper.full_steps_per_rotation !== 200) {
        lines.push(`full_steps_per_rotation: ${stepper.full_steps_per_rotation}`)
      }
      if (stepper.endstop_pin) lines.push(`endstop_pin: ${stepper.endstop_pin}`)
      if (stepper.position_endstop !== undefined) lines.push(`position_endstop: ${stepper.position_endstop}`)
      if (stepper.position_max !== undefined) lines.push(`position_max: ${stepper.position_max}`)
      if (stepper.position_min !== undefined && stepper.position_min !== 0) {
        lines.push(`position_min: ${stepper.position_min}`)
      }
      if (stepper.homing_speed) lines.push(`homing_speed: ${stepper.homing_speed}`)
      if (stepper.homing_retract_dist && stepper.homing_retract_dist !== 5) {
        lines.push(`homing_retract_dist: ${stepper.homing_retract_dist}`)
      }
      if (stepper.second_homing_speed) lines.push(`second_homing_speed: ${stepper.second_homing_speed}`)
      if (stepper.gear_ratio) lines.push(`gear_ratio: ${stepper.gear_ratio}`)
      lines.push('')
    }
  }
  
  if (config.has_extruder !== false && config.extruder) {
    lines.push('[extruder]')
    const ext = config.extruder
    if (ext.step_pin) lines.push(`step_pin: ${ext.step_pin}`)
    if (ext.dir_pin) lines.push(`dir_pin: ${ext.dir_pin}`)
    if (ext.enable_pin) lines.push(`enable_pin: ${ext.enable_pin}`)
    if (ext.microsteps) lines.push(`microsteps: ${ext.microsteps}`)
    if (ext.rotation_distance) lines.push(`rotation_distance: ${ext.rotation_distance}`)
    if (ext.gear_ratio) lines.push(`gear_ratio: ${ext.gear_ratio}`)
    if (ext.nozzle_diameter) lines.push(`nozzle_diameter: ${ext.nozzle_diameter}`)
    if (ext.filament_diameter) lines.push(`filament_diameter: ${ext.filament_diameter}`)
    if (ext.max_extrude_only_distance && ext.max_extrude_only_distance !== 50) {
      lines.push(`max_extrude_only_distance: ${ext.max_extrude_only_distance}`)
    }
    if (ext.heater_pin) lines.push(`heater_pin: ${ext.heater_pin}`)
    if (ext.sensor_type) lines.push(`sensor_type: ${ext.sensor_type}`)
    if (ext.sensor_pin) lines.push(`sensor_pin: ${ext.sensor_pin}`)
    if (ext.control) {
      lines.push(`control: ${ext.control}`)
      if (ext.control === 'pid') {
        if (ext.pid_Kp !== undefined) lines.push(`pid_Kp: ${ext.pid_Kp}`)
        if (ext.pid_Ki !== undefined) lines.push(`pid_Ki: ${ext.pid_Ki}`)
        if (ext.pid_Kd !== undefined) lines.push(`pid_Kd: ${ext.pid_Kd}`)
      }
      if (ext.control === 'mpc') {
        if (ext.heater_power) lines.push(`heater_power: ${ext.heater_power}`)
      }
    }
    if (ext.min_temp !== undefined) lines.push(`min_temp: ${ext.min_temp}`)
    if (ext.max_temp !== undefined) lines.push(`max_temp: ${ext.max_temp}`)
    if (ext.min_extrude_temp !== undefined && ext.min_extrude_temp !== 170) {
      lines.push(`min_extrude_temp: ${ext.min_extrude_temp}`)
    }
    if (ext.pressure_advance !== undefined && ext.pressure_advance !== 0) {
      lines.push(`pressure_advance: ${ext.pressure_advance}`)
    }
    if (ext.pressure_advance_smooth_time !== undefined && ext.pressure_advance_smooth_time !== 0.040) {
      lines.push(`pressure_advance_smooth_time: ${ext.pressure_advance_smooth_time}`)
    }
    lines.push('')
  }
  
  if (config.heater_bed) {
    lines.push('[heater_bed]')
    const bed = config.heater_bed
    if (bed.heater_pin) lines.push(`heater_pin: ${bed.heater_pin}`)
    if (bed.sensor_type) lines.push(`sensor_type: ${bed.sensor_type}`)
    if (bed.sensor_pin) lines.push(`sensor_pin: ${bed.sensor_pin}`)
    if (bed.control) {
      lines.push(`control: ${bed.control}`)
      if (bed.control === 'pid') {
        if (bed.pid_Kp !== undefined) lines.push(`pid_Kp: ${bed.pid_Kp}`)
        if (bed.pid_Ki !== undefined) lines.push(`pid_Ki: ${bed.pid_Ki}`)
        if (bed.pid_Kd !== undefined) lines.push(`pid_Kd: ${bed.pid_Kd}`)
      }
    }
    if (bed.min_temp !== undefined) lines.push(`min_temp: ${bed.min_temp}`)
    if (bed.max_temp !== undefined) lines.push(`max_temp: ${bed.max_temp}`)
    lines.push('')
  }
  
  if (config.fan) {
    lines.push('[fan]')
    if (config.fan.pin) lines.push(`pin: ${config.fan.pin}`)
    if (config.fan.max_power !== undefined && config.fan.max_power !== 1) {
      lines.push(`max_power: ${config.fan.max_power}`)
    }
    if (config.fan.kick_start_time !== undefined && config.fan.kick_start_time !== 0.1) {
      lines.push(`kick_start_time: ${config.fan.kick_start_time}`)
    }
    lines.push('')
  }
  
  if (config.tmc) {
    for (const [stepperName, tmcConfig] of Object.entries(config.tmc)) {
      if (tmcConfig && Object.keys(tmcConfig).length > 0) {
        const driverType = tmcConfig.driver_type || 'tmc2209'
        lines.push(`[${driverType} ${stepperName}]`)
        if (tmcConfig.uart_pin) lines.push(`uart_pin: ${tmcConfig.uart_pin}`)
        if (tmcConfig.spi_pin) lines.push(`spi_pin: ${tmcConfig.spi_pin}`)
        if (tmcConfig.cs_pin) lines.push(`cs_pin: ${tmcConfig.cs_pin}`)
        if (tmcConfig.run_current) lines.push(`run_current: ${tmcConfig.run_current}`)
        if (tmcConfig.hold_current !== undefined) lines.push(`hold_current: ${tmcConfig.hold_current}`)
        if (tmcConfig.interpolate !== undefined && tmcConfig.interpolate !== true) {
          lines.push(`interpolate: ${tmcConfig.interpolate}`)
        }
        if (tmcConfig.stealthchop_threshold !== undefined) {
          lines.push(`stealthchop_threshold: ${tmcConfig.stealthchop_threshold}`)
        }
        if (tmcConfig.sense_resistor !== undefined && tmcConfig.sense_resistor !== 0.110) {
          lines.push(`sense_resistor: ${tmcConfig.sense_resistor}`)
        }
        if (tmcConfig.driver_SGTHRS !== undefined) {
          lines.push(`driver_SGTHRS: ${tmcConfig.driver_SGTHRS}`)
        }
        if (tmcConfig.diag_pin) lines.push(`diag_pin: ${tmcConfig.diag_pin}`)
        lines.push('')
      }
    }
  }
  
  if (config.toolboards && config.toolboards.length > 0) {
    for (const tb of config.toolboards) {
      if (tb.type && tb.type !== 'none') {
        const sectionName = tb.name || 'toolhead'
        lines.push(`# 工具板: ${tb.type}`)
        lines.push(`[mcu ${sectionName}]`)
        if (tb.canbus_uuid) {
          lines.push(`canbus_uuid: ${tb.canbus_uuid}`)
        }
        lines.push('')
      }
    }
  }
  
  if (config.probe) {
    const probeType = config.probe.type || 'probe'
    lines.push(`[${probeType}]`)
    const probe = config.probe
    if (probe.pin) lines.push(`pin: ${probe.pin}`)
    if (probe.x_offset !== undefined) lines.push(`x_offset: ${probe.x_offset}`)
    if (probe.y_offset !== undefined) lines.push(`y_offset: ${probe.y_offset}`)
    if (probe.z_offset !== undefined) lines.push(`z_offset: ${probe.z_offset}`)
    if (probe.speed) lines.push(`speed: ${probe.speed}`)
    if (probe.samples) lines.push(`samples: ${probe.samples}`)
    if (probe.samples_result) lines.push(`samples_result: ${probe.samples_result}`)
    if (probe.sample_retract_dist) lines.push(`sample_retract_dist: ${probe.sample_retract_dist}`)
    if (probe.probe_type === 'bltouch') {
      if (probe.control_pin) lines.push(`control_pin: ${probe.control_pin}`)
    }
    lines.push('')
  }
  
  if (config.bed_mesh) {
    lines.push('[bed_mesh]')
    const mesh = config.bed_mesh
    if (mesh.probe_count) lines.push(`probe_count: ${mesh.probe_count}`)
    if (mesh.mesh_min) lines.push(`mesh_min: ${mesh.mesh_min}`)
    if (mesh.mesh_max) lines.push(`mesh_max: ${mesh.mesh_max}`)
    if (mesh.algorithm) lines.push(`algorithm: ${mesh.algorithm}`)
    if (mesh.fade_start !== undefined) lines.push(`fade_start: ${mesh.fade_start}`)
    if (mesh.fade_end !== undefined) lines.push(`fade_end: ${mesh.fade_end}`)
    if (mesh.horizontal_move_z) lines.push(`horizontal_move_z: ${mesh.horizontal_move_z}`)
    lines.push('')
  }
  
  if (config.input_shaper) {
    lines.push('[input_shaper]')
    const shaper = config.input_shaper
    if (shaper.shaper_type) lines.push(`shaper_type: ${shaper.shaper_type}`)
    if (shaper.shaper_freq_x) lines.push(`shaper_freq_x: ${shaper.shaper_freq_x}`)
    if (shaper.shaper_freq_y) lines.push(`shaper_freq_y: ${shaper.shaper_freq_y}`)
    lines.push('')
  }
  
  if (config.display) {
    lines.push('[display]')
    const disp = config.display
    if (disp.lcd_type) lines.push(`lcd_type: ${disp.lcd_type}`)
    if (disp.lcd_type === 'st7920') {
      if (disp.cs_pin) lines.push(`cs_pin: ${disp.cs_pin}`)
      if (disp.sclk_pin) lines.push(`sclk_pin: ${disp.sclk_pin}`)
      if (disp.sid_pin) lines.push(`sid_pin: ${disp.sid_pin}`)
    }
    if (disp.encoder_pins) lines.push(`encoder_pins: ${disp.encoder_pins}`)
    if (disp.click_pin) lines.push(`click_pin: ${disp.click_pin}`)
    if (disp.kill_pin) lines.push(`kill_pin: ${disp.kill_pin}`)
    lines.push('')
  }
  
  if (config.temperature_sensors && config.temperature_sensors.length > 0) {
    for (const sensor of config.temperature_sensors) {
      if (sensor.name) {
        lines.push(`[temperature_sensor ${sensor.name}]`)
        if (sensor.sensor_type) lines.push(`sensor_type: ${sensor.sensor_type}`)
        if (sensor.sensor_pin) lines.push(`sensor_pin: ${sensor.sensor_pin}`)
        if (sensor.min_temp !== undefined) lines.push(`min_temp: ${sensor.min_temp}`)
        if (sensor.max_temp !== undefined) lines.push(`max_temp: ${sensor.max_temp}`)
        lines.push('')
      }
    }
  }
  
  if (config.safe_z_home) {
    lines.push('[safe_z_home]')
    if (config.safe_z_home.home_xy_position) {
      lines.push(`home_xy_position: ${config.safe_z_home.home_xy_position}`)
    }
    if (config.safe_z_home.speed) lines.push(`speed: ${config.safe_z_home.speed}`)
    if (config.safe_z_home.z_hop) lines.push(`z_hop: ${config.safe_z_home.z_hop}`)
    lines.push('')
  }
  
  if (config.bed_screws) {
    lines.push('[bed_screws]')
    for (let i = 0; i < config.bed_screws.length; i++) {
      if (config.bed_screws[i]) {
        lines.push(`screw${i + 1}: ${config.bed_screws[i]}`)
      }
    }
    lines.push('')
  }
  
  return lines.join('\n')
}

function getStepperNames(kinematics) {
  switch (kinematics) {
    case 'delta':
      return ['stepper_a', 'stepper_b', 'stepper_c']
    case 'deltesian':
      return ['stepper_left', 'stepper_right', 'stepper_y']
    case 'polar':
      return ['stepper_bed', 'stepper_arm', 'stepper_z']
    case 'rotary_delta':
      return ['stepper_a', 'stepper_b', 'stepper_c']
    case 'winch':
      return ['stepper_a', 'stepper_b', 'stepper_c']
    default:
      return ['stepper_x', 'stepper_y', 'stepper_z']
  }
}
