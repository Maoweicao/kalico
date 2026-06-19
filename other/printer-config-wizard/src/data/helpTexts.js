export const helpTexts = {
  mcu: {
    serial: {
      title: '串口路径',
      desc: 'MCU通过USB连接到树莓派时的串口设备路径。',
      detail: '常见路径：\n• /dev/ttyACM0 - 大多数Arduino和STM32主板\n• /dev/ttyUSB0 - 某些CH340芯片的主板\n• /dev/serial/by-id/... - 推荐使用，更稳定的路径',
      example: 'serial: /dev/ttyACM0'
    },
    canbus_uuid: {
      title: 'CAN总线UUID',
      desc: '如果使用CAN总线连接MCU，需要填入UUID。',
      detail: '通过以下命令获取UUID：\n~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0',
      example: 'canbus_uuid: 1234567890abcdef'
    },
    baud: {
      title: '波特率',
      desc: '串口通信波特率，通常保持默认即可。',
      detail: '默认值250000适用于大多数主板。如果遇到通信问题，可以尝试115200。',
      example: 'baud: 250000'
    }
  },
  printer: {
    kinematics: {
      title: '运动学类型',
      desc: '选择打印机的机械结构类型。',
      detail: '常见类型：\n• cartesian - 普通XYZ三轴独立运动（Ender 3, CR-10等）\n• corexy - XY轴联动，速度快（Voron, RatRig等）\n• corexz - XZ轴联动\n• delta - 三角洲打印机（Kossel, Rostock等）',
      example: 'kinematics: cartesian'
    },
    max_velocity: {
      title: '最大速度 (mm/s)',
      desc: '打印机的最大移动速度。',
      detail: '安全范围：\n• Cartesian: 200-500 mm/s\n• CoreXY: 300-600 mm/s\n• Delta: 300-600 mm/s\n建议从较低值开始测试。',
      example: 'max_velocity: 300'
    },
    max_accel: {
      title: '最大加速度 (mm/s²)',
      desc: '打印机的最大加速度。',
      detail: '安全范围：\n• Cartesian: 1000-5000 mm/s²\n• CoreXY: 3000-10000 mm/s²\n• Delta: 3000-10000 mm/s²\n过高的值可能导致丢步或振动。',
      example: 'max_accel: 3000'
    },
    max_z_velocity: {
      title: 'Z轴最大速度 (mm/s)',
      desc: 'Z轴的最大移动速度。',
      detail: 'Z轴通常使用丝杆，速度较低：\n• 普通丝杆: 5-25 mm/s\n• 高速丝杆: 25-50 mm/s',
      example: 'max_z_velocity: 5'
    },
    max_z_accel: {
      title: 'Z轴最大加速度 (mm/s²)',
      desc: 'Z轴的最大加速度。',
      detail: '通常设为100-300 mm/s²，过高可能导致Z轴丢步。',
      example: 'max_z_accel: 100'
    },
    square_corner_velocity: {
      title: '直角速度 (mm/s)',
      desc: '直角转弯时的最大速度。',
      detail: '影响打印质量，值越小转角越精确。\n默认5.0 mm/s，范围0-30。',
      example: 'square_corner_velocity: 5.0'
    }
  },
  stepper: {
    step_pin: {
      title: '步进引脚',
      desc: '步进电机驱动的STEP引脚。',
      detail: '每个主板的引脚不同，请参考主板文档。\n引脚前缀表示端口：\n• PA, PB, PC... - STM32\n• PF, PH, PJ... - ATmega',
      example: 'step_pin: PB13'
    },
    dir_pin: {
      title: '方向引脚',
      desc: '控制电机旋转方向的DIR引脚。',
      detail: '如果电机方向相反，添加!前缀反转：\ndir_pin: PB12 (正向)\ndir_pin: !PB12 (反向)',
      example: 'dir_pin: !PB12'
    },
    enable_pin: {
      title: '使能引脚',
      desc: '控制电机使能的EN引脚。',
      detail: '大多数驱动板低电平使能，需要!前缀：\nenable_pin: !PB14',
      example: 'enable_pin: !PB14'
    },
    microsteps: {
      title: '微步数',
      desc: '驱动的微步细分。',
      detail: '常见值：\n• 16 - 最常用，平衡性能和噪音\n• 32 - 更安静但CPU占用更高\n• 64/128/256 - 极少使用\n推荐使用16。',
      example: 'microsteps: 16'
    },
    rotation_distance: {
      title: '旋转距离 (mm)',
      desc: '电机转一圈移动的距离。',
      detail: '计算公式：\n• 直驱: 丝杆螺距 (如T8丝杆=8)\n• 带齿轮: 齿轮比 × 丝杆螺距\n• XY轴皮带: 齿轮齿数 × 皮带齿距\n  如20齿GT2齿轮: 20 × 2 = 40mm',
      example: 'rotation_distance: 40'
    },
    full_steps_per_rotation: {
      title: '每圈全步数',
      desc: '电机每圈的全步数。',
      detail: '常见值：\n• 200 - 1.8度电机（最常见）\n• 400 - 0.9度电机（更精确）',
      example: 'full_steps_per_rotation: 200'
    },
    endstop_pin: {
      title: '限位引脚',
      desc: '限位开关的信号引脚。',
      detail: '前缀说明：\n• ^ - 启用内部上拉电阻\n• ! - 反转信号极性\n• ^PC1 - 上拉，正常极性\n• ^!PC1 - 上拉，反转极性',
      example: 'endstop_pin: ^PC1'
    },
    position_endstop: {
      title: '限位位置 (mm)',
      desc: '限位开关触发时喷嘴的位置。',
      detail: '• 0 - 限位在轴的最小端（最常见）\n• position_max - 限位在轴的最大端',
      example: 'position_endstop: 0'
    },
    position_max: {
      title: '最大位置 (mm)',
      desc: '轴的最大行程。',
      detail: '常见值：\n• Ender 3: X=235, Y=235, Z=250\n• Ender 5: X=220, Y=220, Z=300\n• Voron 250: X=250, Y=250, Z=250',
      example: 'position_max: 235'
    },
    position_min: {
      title: '最小位置 (mm)',
      desc: '轴的最小行程，通常为0。',
      detail: '如果限位在最大端，这里可以设为负值。',
      example: 'position_min: 0'
    },
    homing_speed: {
      title: '归位速度 (mm/s)',
      desc: '第一次归位的移动速度。',
      detail: '建议50-100 mm/s，过快可能损坏限位开关。',
      example: 'homing_speed: 50'
    },
    homing_retract_dist: {
      title: '归位回退距离 (mm)',
      desc: '触发限位后回退的距离。',
      detail: '默认5mm，一般不需要修改。',
      example: 'homing_retract_dist: 5'
    },
    second_homing_speed: {
      title: '二次归位速度 (mm/s)',
      desc: '第二次归位的移动速度。',
      detail: '通常比第一次慢，以提高精度。\n默认为homing_speed的一半。',
      example: 'second_homing_speed: 5'
    }
  },
  extruder: {
    nozzle_diameter: {
      title: '喷嘴直径 (mm)',
      desc: '安装的喷嘴直径。',
      detail: '常见值：0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0mm\n0.4mm是最常用的。',
      example: 'nozzle_diameter: 0.400'
    },
    filament_diameter: {
      title: '耗材直径 (mm)',
      desc: '使用的耗材直径。',
      detail: '• 1.75mm - 最常见\n• 2.85mm - Ultimaker等打印机使用',
      example: 'filament_diameter: 1.750'
    },
    max_extrude_only_distance: {
      title: '最大挤出距离 (mm)',
      desc: '单次挤出的最大距离。',
      detail: '默认50mm，如果使用长距离退料可以增加到100-150mm。',
      example: 'max_extrude_only_distance: 100.0'
    },
    max_extrude_cross_section: {
      title: '最大挤出截面 (mm²)',
      desc: '挤出的最大横截面积。',
      detail: '默认值通常足够，如果使用大流量挤出机可以增加。',
      example: 'max_extrude_cross_section: 5.0'
    },
    pressure_advance: {
      title: '压力提前',
      desc: '补偿挤出机压力延迟。',
      detail: '范围0-2，默认0（关闭）。\n直驱挤出机通常0.02-0.1\n远程挤出机通常0.1-0.6\n需要校准后设置。',
      example: 'pressure_advance: 0.05'
    },
    pressure_advance_smooth_time: {
      title: '压力提前平滑时间 (s)',
      desc: '压力提前的平滑时间。',
      detail: '默认0.040秒，范围0-0.200。',
      example: 'pressure_advance_smooth_time: 0.040'
    },
    heater_pin: {
      title: '加热引脚',
      desc: '加热棒的控制引脚。',
      detail: '通常是PWM输出引脚。',
      example: 'heater_pin: PB4'
    },
    sensor_type: {
      title: '温度传感器类型',
      desc: '热敏电阻或热电偶的类型。',
      detail: '常见类型：\n• EPCOS 100K B57560G104F - 最常见\n• ATC Semitec 104GT-2 - 高温\n• Generic 3950 - 通用\n• PT1000 - 铂电阻\n• MAX6675/MAX31855/MAX31856 - 热电偶',
      example: 'sensor_type: EPCOS 100K B57560G104F'
    },
    sensor_pin: {
      title: '传感器引脚',
      desc: '温度传感器的ADC引脚。',
      detail: '必须是模拟输入引脚。',
      example: 'sensor_pin: PC0'
    },
    control: {
      title: '温控方式',
      desc: '温度控制算法。',
      detail: '• pid - PID控制，精度高（推荐）\n• watermark - 开关控制，简单但波动大\n• mpc - 模型预测控制（Kalico新功能）',
      example: 'control: pid'
    },
    pid_Kp: {
      title: 'PID Kp',
      desc: 'PID比例系数。',
      detail: '通过PID_CALIBRATE命令自动校准。\n或者手动调整：\n• Kp过大 - 温度振荡\n• Kp过小 - 响应慢',
      example: 'pid_Kp: 22.2'
    },
    pid_Ki: {
      title: 'PID Ki',
      desc: 'PID积分系数。',
      detail: '通过PID_CALIBRATE命令自动校准。',
      example: 'pid_Ki: 1.08'
    },
    pid_Kd: {
      title: 'PID Kd',
      desc: 'PID微分系数。',
      detail: '通过PID_CALIBRATE命令自动校准。',
      example: 'pid_Kd: 114'
    },
    min_temp: {
      title: '最低温度 (°C)',
      desc: '允许的最低温度。',
      detail: '低于此温度将报错。通常设为0或室温。',
      example: 'min_temp: 0'
    },
    max_temp: {
      title: '最高温度 (°C)',
      desc: '允许的最高温度。',
      detail: '安全限制：\n• 普通热敏电阻: 250-260°C\n• 全金属热端: 300°C\n• 热电偶: 400°C+',
      example: 'max_temp: 250'
    },
    min_extrude_temp: {
      title: '最低挤出温度 (°C)',
      desc: '允许挤出的最低温度。',
      detail: '默认170°C，防止低温挤出损坏挤出机。',
      example: 'min_extrude_temp: 170'
    }
  },
  heater_bed: {
    heater_pin: {
      title: '加热引脚',
      desc: '热床加热的控制引脚。',
      detail: '通常是大电流MOSFET输出。',
      example: 'heater_pin: PD2'
    },
    sensor_type: {
      title: '温度传感器类型',
      desc: '热床热敏电阻的类型。',
      detail: '通常与挤出机使用相同类型。',
      example: 'sensor_type: EPCOS 100K B57560G104F'
    },
    sensor_pin: {
      title: '传感器引脚',
      desc: '热床温度传感器的ADC引脚。',
      example: 'sensor_pin: PC1'
    },
    max_temp: {
      title: '最高温度 (°C)',
      desc: '热床最高允许温度。',
      detail: '安全限制：\n• 普通热床: 110-120°C\n• 高温热床: 150°C',
      example: 'max_temp: 130'
    }
  },
  fan: {
    pin: {
      title: '风扇引脚',
      desc: '零件冷却风扇的控制引脚。',
      detail: '支持PWM调速的引脚。',
      example: 'pin: PC6'
    },
    max_power: {
      title: '最大功率',
      desc: '风扇最大功率百分比。',
      detail: '范围0-1，默认1.0（100%）。\n降低可减少噪音。',
      example: 'max_power: 1.0'
    },
    kick_start_time: {
      title: '启动时间 (s)',
      desc: '风扇启动时的全速运行时间。',
      detail: '帮助风扇从停止状态启动。\n默认0.1秒。',
      example: 'kick_start_time: 0.100'
    }
  },
  tmc: {
    uart_pin: {
      title: 'UART引脚',
      desc: 'TMC驱动的UART通信引脚。',
      detail: '用于配置驱动参数。\n某些主板所有驱动共享一个引脚。',
      example: 'uart_pin: PC11'
    },
    spi_pin: {
      title: 'SPI引脚',
      desc: 'TMC驱动的SPI通信引脚。',
      detail: 'TMC2130/TMC5160使用SPI通信。',
      example: 'spi_pin: PA4'
    },
    run_current: {
      title: '运行电流 (A)',
      desc: '电机运行时的电流。',
      detail: '根据电机额定电流设置：\n• 42电机: 0.6-0.8A\n• 42-48电机: 0.8-1.2A\n• 57电机: 1.5-2.5A\n建议不超过额定值的70-80%。',
      example: 'run_current: 0.800'
    },
    hold_current: {
      title: '保持电流 (A)',
      desc: '电机静止时的电流。',
      detail: '默认为run_current的一半。\n降低可减少发热和功耗。',
      example: 'hold_current: 0.400'
    },
    stealthchop_threshold: {
      title: '静音模式阈值 (mm/s)',
      desc: '低于此速度使用静音模式。',
      detail: '• 0 - 始终使用spreadCycle（性能优先）\n• 999999 - 始终使用stealthChop（静音优先）\n• 200 - 低速静音，高速性能',
      example: 'stealthchop_threshold: 0'
    },
    interpolate: {
      title: '插值',
      desc: '启用256微步插值。',
      detail: '默认true，几乎总是建议启用。',
      example: 'interpolate: true'
    },
    sense_resistor: {
      title: '采样电阻 (Ω)',
      desc: '驱动板的采样电阻值。',
      detail: '• 0.110 - TMC2209/TMC2208/TMC2226\n• 0.075 - TMC5160\n通常不需要修改。',
      example: 'sense_resistor: 0.110'
    },
    driver_SGTHRS: {
      title: 'StallGuard阈值',
      desc: '用于无传感器归位的灵敏度。',
      detail: 'TMC2209使用。\n范围0-255，值越小越灵敏。\n需要测试找到合适值。',
      example: 'driver_SGTHRS: 100'
    }
  },
  probe: {
    pin: {
      title: '探针引脚',
      desc: '探针的信号引脚。',
      detail: '通常需要上拉电阻（^前缀）。',
      example: 'pin: ^PB1'
    },
    x_offset: {
      title: 'X偏移 (mm)',
      desc: '探针相对于喷嘴的X偏移。',
      detail: '探针在喷嘴右边为正，左边为负。',
      example: 'x_offset: -44'
    },
    y_offset: {
      title: 'Y偏移 (mm)',
      desc: '探针相对于喷嘴的Y偏移。',
      detail: '探针在喷嘴前方为正，后方为负。',
      example: 'y_offset: -6'
    },
    z_offset: {
      title: 'Z偏移 (mm)',
      desc: '探针触发时喷嘴与热床的距离。',
      detail: '通过PROBE_CALIBRATE命令校准。\n通常是负值（喷嘴在探针下方）。',
      example: 'z_offset: 1.0'
    },
    speed: {
      title: '探测速度 (mm/s)',
      desc: '探针下降探测的速度。',
      detail: '默认5 mm/s，过快可能损坏探针。',
      example: 'speed: 5.0'
    },
    samples: {
      title: '采样次数',
      desc: '每个点探测的次数。',
      detail: '默认1次，增加可提高精度但降低速度。\n推荐1-3次。',
      example: 'samples: 1'
    },
    samples_result: {
      title: '采样结果',
      desc: '多次采样的取值方式。',
      detail: '• average - 取平均值（推荐）\n• median - 取中位数',
      example: 'samples_result: average'
    },
    sample_retract_dist: {
      title: '回退距离 (mm)',
      desc: '探测后回退的距离。',
      detail: '默认2mm，确保探针完全释放。',
      example: 'sample_retract_dist: 2.0'
    }
  },
  bed_mesh: {
    probe_count: {
      title: '探测点数',
      desc: '网格的探测点数量。',
      detail: '格式: X点数, Y点数\n• 3,3 - 快速但粗糙\n• 5,5 - 常用\n• 7,7 - 精确但慢\n建议奇数。',
      example: 'probe_count: 5, 5'
    },
    mesh_min: {
      title: '网格最小坐标',
      desc: '网格左下角的坐标。',
      detail: '格式: X, Y\n需要考虑探针偏移，确保探针能到达。',
      example: 'mesh_min: 30, 30'
    },
    mesh_max: {
      title: '网格最大坐标',
      desc: '网格右上角的坐标。',
      detail: '格式: X, Y\n需要考虑探针偏移，确保探针能到达。',
      example: 'mesh_max: 200, 200'
    },
    algorithm: {
      title: '插值算法',
      desc: '网格点之间的插值方法。',
      detail: '• lagrange - 拉格朗日插值\n• bicubic - 双三次插值（更平滑）',
      example: 'algorithm: bicubic'
    },
    fade_start: {
      title: '淡出起始高度',
      desc: '开始淡出补偿的高度。',
      detail: '默认0.0，从第一层开始补偿。',
      example: 'fade_start: 0.0'
    },
    fade_end: {
      title: '淡出结束高度',
      desc: '完全淡出补偿的高度。',
      detail: '默认10.0mm，在此高度后完全不补偿。',
      example: 'fade_end: 10.0'
    }
  },
  input_shaper: {
    shaper_type: {
      title: '整形器类型',
      desc: '输入整形算法类型。',
      detail: '• mzv - 推荐，平衡性能和效果\n• zv - 最简单\n• ei - 更强的抑制\n• 2hump_ei - 双驼峰\n• 3hump_ei - 三驼峰',
      example: 'shaper_type: mzv'
    },
    shaper_freq_x: {
      title: 'X轴频率 (Hz)',
      desc: 'X轴的共振频率。',
      detail: '通过测量共振获得。\n运行SHAPER_CALIBRATE自动测量。',
      example: 'shaper_freq_x: 50.0'
    },
    shaper_freq_y: {
      title: 'Y轴频率 (Hz)',
      desc: 'Y轴的共振频率。',
      detail: '通过测量共振获得。\n运行SHAPER_CALIBRATE自动测量。',
      example: 'shaper_freq_y: 40.0'
    }
  },
  display: {
    lcd_type: {
      title: '显示屏类型',
      desc: 'LCD显示屏的型号。',
      detail: '常见类型：\n• st7920 - 128x64全图形屏\n• hd44780 - 20x4字符屏\n• uc1701 - 128x64图形屏\n• ssd1306 - OLED屏\n• sh1106 - OLED屏',
      example: 'lcd_type: st7920'
    }
  },
  temperature_sensor: {
    sensor_type: {
      title: '传感器类型',
      desc: '温度传感器的型号。',
      detail: '常见类型：\n• EPCOS 100K B57560G104F\n• Generic 3950\n• DS18B20 - 数字温度传感器\n• BME280 - 温湿度气压传感器',
      example: 'sensor_type: Generic 3950'
    },
    sensor_pin: {
      title: '传感器引脚',
      desc: '温度传感器的ADC引脚。',
      detail: '必须是模拟输入引脚（热敏电阻）\n或数字引脚（DS18B20等）。',
      example: 'sensor_pin: PC2'
    },
    min_temp: {
      title: '最低温度 (°C)',
      desc: '允许的最低温度。',
      detail: '低于此温度将报错。',
      example: 'min_temp: 0'
    },
    max_temp: {
      title: '最高温度 (°C)',
      desc: '允许的最高温度。',
      detail: '高于此温度将报错。',
      example: 'max_temp: 100'
    }
  }
}
