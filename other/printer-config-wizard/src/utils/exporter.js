export function generateJson(config) {
  const output = {}
  
  if (config.mcu) {
    output.mcu = {}
    if (config.mcu.serial) output.mcu.serial = config.mcu.serial
    if (config.mcu.canbus_uuid) output.mcu.canbus_uuid = config.mcu.canbus_uuid
    if (config.mcu.canbus_interface) output.mcu.canbus_interface = config.mcu.canbus_interface
    if (config.mcu.baud) output.mcu.baud = config.mcu.baud
  }
  
  if (config.printer) {
    output.printer = {
      kinematics: config.printer.kinematics || 'cartesian',
      max_velocity: config.printer.max_velocity || 300,
      max_accel: config.printer.max_accel || 3000
    }
    if (config.printer.kinematics !== 'delta') {
      output.printer.max_z_velocity = config.printer.max_z_velocity || 5
      output.printer.max_z_accel = config.printer.max_z_accel || 100
    }
    if (config.printer.square_corner_velocity !== undefined) {
      output.printer.square_corner_velocity = config.printer.square_corner_velocity
    }
  }
  
  const stepperNames = getStepperNames(config.printer?.kinematics || 'cartesian')
  
  for (const stepperName of stepperNames) {
    const stepper = config.steppers?.[stepperName]
    if (stepper) {
      output[stepperName] = {}
      if (stepper.step_pin) output[stepperName].step_pin = stepper.step_pin
      if (stepper.dir_pin) output[stepperName].dir_pin = stepper.dir_pin
      if (stepper.enable_pin) output[stepperName].enable_pin = stepper.enable_pin
      if (stepper.microsteps) output[stepperName].microsteps = stepper.microsteps
      if (stepper.rotation_distance) output[stepperName].rotation_distance = stepper.rotation_distance
      if (stepper.full_steps_per_rotation && stepper.full_steps_per_rotation !== 200) {
        output[stepperName].full_steps_per_rotation = stepper.full_steps_per_rotation
      }
      if (stepper.endstop_pin) output[stepperName].endstop_pin = stepper.endstop_pin
      if (stepper.position_endstop !== undefined) output[stepperName].position_endstop = stepper.position_endstop
      if (stepper.position_max !== undefined) output[stepperName].position_max = stepper.position_max
      if (stepper.position_min !== undefined && stepper.position_min !== 0) {
        output[stepperName].position_min = stepper.position_min
      }
      if (stepper.homing_speed) output[stepperName].homing_speed = stepper.homing_speed
      if (stepper.homing_retract_dist && stepper.homing_retract_dist !== 5) {
        output[stepperName].homing_retract_dist = stepper.homing_retract_dist
      }
      if (stepper.second_homing_speed) output[stepperName].second_homing_speed = stepper.second_homing_speed
      if (stepper.gear_ratio) output[stepperName].gear_ratio = stepper.gear_ratio
    }
  }
  
  if (config.extruder) {
    output.extruder = {}
    const ext = config.extruder
    if (ext.step_pin) output.extruder.step_pin = ext.step_pin
    if (ext.dir_pin) output.extruder.dir_pin = ext.dir_pin
    if (ext.enable_pin) output.extruder.enable_pin = ext.enable_pin
    if (ext.microsteps) output.extruder.microsteps = ext.microsteps
    if (ext.rotation_distance) output.extruder.rotation_distance = ext.rotation_distance
    if (ext.gear_ratio) output.extruder.gear_ratio = ext.gear_ratio
    if (ext.nozzle_diameter) output.extruder.nozzle_diameter = ext.nozzle_diameter
    if (ext.filament_diameter) output.extruder.filament_diameter = ext.filament_diameter
    if (ext.max_extrude_only_distance && ext.max_extrude_only_distance !== 50) {
      output.extruder.max_extrude_only_distance = ext.max_extrude_only_distance
    }
    if (ext.heater_pin) output.extruder.heater_pin = ext.heater_pin
    if (ext.sensor_type) output.extruder.sensor_type = ext.sensor_type
    if (ext.sensor_pin) output.extruder.sensor_pin = ext.sensor_pin
    if (ext.control) {
      output.extruder.control = ext.control
      if (ext.control === 'pid') {
        if (ext.pid_Kp !== undefined) output.extruder.pid_Kp = ext.pid_Kp
        if (ext.pid_Ki !== undefined) output.extruder.pid_Ki = ext.pid_Ki
        if (ext.pid_Kd !== undefined) output.extruder.pid_Kd = ext.pid_Kd
      }
      if (ext.control === 'mpc') {
        if (ext.heater_power) output.extruder.heater_power = ext.heater_power
      }
    }
    if (ext.min_temp !== undefined) output.extruder.min_temp = ext.min_temp
    if (ext.max_temp !== undefined) output.extruder.max_temp = ext.max_temp
    if (ext.min_extrude_temp !== undefined && ext.min_extrude_temp !== 170) {
      output.extruder.min_extrude_temp = ext.min_extrude_temp
    }
    if (ext.pressure_advance !== undefined && ext.pressure_advance !== 0) {
      output.extruder.pressure_advance = ext.pressure_advance
    }
    if (ext.pressure_advance_smooth_time !== undefined && ext.pressure_advance_smooth_time !== 0.040) {
      output.extruder.pressure_advance_smooth_time = ext.pressure_advance_smooth_time
    }
  }
  
  if (config.heater_bed) {
    output.heater_bed = {}
    const bed = config.heater_bed
    if (bed.heater_pin) output.heater_bed.heater_pin = bed.heater_pin
    if (bed.sensor_type) output.heater_bed.sensor_type = bed.sensor_type
    if (bed.sensor_pin) output.heater_bed.sensor_pin = bed.sensor_pin
    if (bed.control) {
      output.heater_bed.control = bed.control
      if (bed.control === 'pid') {
        if (bed.pid_Kp !== undefined) output.heater_bed.pid_Kp = bed.pid_Kp
        if (bed.pid_Ki !== undefined) output.heater_bed.pid_Ki = bed.pid_Ki
        if (bed.pid_Kd !== undefined) output.heater_bed.pid_Kd = bed.pid_Kd
      }
    }
    if (bed.min_temp !== undefined) output.heater_bed.min_temp = bed.min_temp
    if (bed.max_temp !== undefined) output.heater_bed.max_temp = bed.max_temp
  }
  
  if (config.fan) {
    output.fan = {}
    if (config.fan.pin) output.fan.pin = config.fan.pin
    if (config.fan.max_power !== undefined && config.fan.max_power !== 1) {
      output.fan.max_power = config.fan.max_power
    }
    if (config.fan.kick_start_time !== undefined && config.fan.kick_start_time !== 0.1) {
      output.fan.kick_start_time = config.fan.kick_start_time
    }
  }
  
  if (config.tmc) {
    for (const [stepperName, tmcConfig] of Object.entries(config.tmc)) {
      if (tmcConfig && Object.keys(tmcConfig).length > 0) {
        const driverType = tmcConfig.driver_type || 'tmc2209'
        const sectionName = `${driverType} ${stepperName}`
        output[sectionName] = {}
        if (tmcConfig.uart_pin) output[sectionName].uart_pin = tmcConfig.uart_pin
        if (tmcConfig.spi_pin) output[sectionName].spi_pin = tmcConfig.spi_pin
        if (tmcConfig.cs_pin) output[sectionName].cs_pin = tmcConfig.cs_pin
        if (tmcConfig.run_current) output[sectionName].run_current = tmcConfig.run_current
        if (tmcConfig.hold_current !== undefined) output[sectionName].hold_current = tmcConfig.hold_current
        if (tmcConfig.interpolate !== undefined && tmcConfig.interpolate !== true) {
          output[sectionName].interpolate = tmcConfig.interpolate
        }
        if (tmcConfig.stealthchop_threshold !== undefined) {
          output[sectionName].stealthchop_threshold = tmcConfig.stealthchop_threshold
        }
        if (tmcConfig.sense_resistor !== undefined && tmcConfig.sense_resistor !== 0.110) {
          output[sectionName].sense_resistor = tmcConfig.sense_resistor
        }
        if (tmcConfig.driver_SGTHRS !== undefined) {
          output[sectionName].driver_SGTHRS = tmcConfig.driver_SGTHRS
        }
        if (tmcConfig.diag_pin) output[sectionName].diag_pin = tmcConfig.diag_pin
      }
    }
  }
  
  if (config.probe) {
    const probeType = config.probe.type || 'probe'
    output[probeType] = {}
    const probe = config.probe
    if (probe.pin) output[probeType].pin = probe.pin
    if (probe.x_offset !== undefined) output[probeType].x_offset = probe.x_offset
    if (probe.y_offset !== undefined) output[probeType].y_offset = probe.y_offset
    if (probe.z_offset !== undefined) output[probeType].z_offset = probe.z_offset
    if (probe.speed) output[probeType].speed = probe.speed
    if (probe.samples) output[probeType].samples = probe.samples
    if (probe.samples_result) output[probeType].samples_result = probe.samples_result
    if (probe.sample_retract_dist) output[probeType].sample_retract_dist = probe.sample_retract_dist
    if (probe.probe_type === 'bltouch') {
      if (probe.control_pin) output[probeType].control_pin = probe.control_pin
    }
  }
  
  if (config.bed_mesh) {
    output.bed_mesh = {}
    const mesh = config.bed_mesh
    if (mesh.probe_count) output.bed_mesh.probe_count = mesh.probe_count
    if (mesh.mesh_min) output.bed_mesh.mesh_min = mesh.mesh_min
    if (mesh.mesh_max) output.bed_mesh.mesh_max = mesh.mesh_max
    if (mesh.algorithm) output.bed_mesh.algorithm = mesh.algorithm
    if (mesh.fade_start !== undefined) output.bed_mesh.fade_start = mesh.fade_start
    if (mesh.fade_end !== undefined) output.bed_mesh.fade_end = mesh.fade_end
    if (mesh.horizontal_move_z) output.bed_mesh.horizontal_move_z = mesh.horizontal_move_z
  }
  
  if (config.input_shaper) {
    output.input_shaper = {}
    const shaper = config.input_shaper
    if (shaper.shaper_type) output.input_shaper.shaper_type = shaper.shaper_type
    if (shaper.shaper_freq_x) output.input_shaper.shaper_freq_x = shaper.shaper_freq_x
    if (shaper.shaper_freq_y) output.input_shaper.shaper_freq_y = shaper.shaper_freq_y
  }
  
  if (config.display) {
    output.display = {}
    const disp = config.display
    if (disp.lcd_type) output.display.lcd_type = disp.lcd_type
    if (disp.lcd_type === 'st7920') {
      if (disp.cs_pin) output.display.cs_pin = disp.cs_pin
      if (disp.sclk_pin) output.display.sclk_pin = disp.sclk_pin
      if (disp.sid_pin) output.display.sid_pin = disp.sid_pin
    }
    if (disp.encoder_pins) output.display.encoder_pins = disp.encoder_pins
    if (disp.click_pin) output.display.click_pin = disp.click_pin
    if (disp.kill_pin) output.display.kill_pin = disp.kill_pin
  }
  
  if (config.temperature_sensors && config.temperature_sensors.length > 0) {
    for (const sensor of config.temperature_sensors) {
      if (sensor.name) {
        const sectionName = `temperature_sensor ${sensor.name}`
        output[sectionName] = {}
        if (sensor.sensor_type) output[sectionName].sensor_type = sensor.sensor_type
        if (sensor.sensor_pin) output[sectionName].sensor_pin = sensor.sensor_pin
        if (sensor.min_temp !== undefined) output[sectionName].min_temp = sensor.min_temp
        if (sensor.max_temp !== undefined) output[sectionName].max_temp = sensor.max_temp
      }
    }
  }
  
  if (config.safe_z_home) {
    output.safe_z_home = {}
    if (config.safe_z_home.home_xy_position) {
      output.safe_z_home.home_xy_position = config.safe_z_home.home_xy_position
    }
    if (config.safe_z_home.speed) output.safe_z_home.speed = config.safe_z_home.speed
    if (config.safe_z_home.z_hop) output.safe_z_home.z_hop = config.safe_z_home.z_hop
  }
  
  if (config.bed_screws) {
    output.bed_screws = {}
    for (let i = 0; i < config.bed_screws.length; i++) {
      if (config.bed_screws[i]) {
        output.bed_screws[`screw${i + 1}`] = config.bed_screws[i]
      }
    }
  }
  
  return JSON.stringify(output, null, 2)
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
