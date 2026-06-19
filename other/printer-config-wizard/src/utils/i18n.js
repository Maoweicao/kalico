import { ref, computed } from 'vue'

const currentLocale = ref('zh')

const messages = {
  zh: {
    // Header
    appTitle: 'Kalico 打印机配置向导',
    langSwitch: 'English',
    
    // Steps
    stepWelcome: '欢迎',
    stepMcu: 'MCU连接',
    stepKinematics: '打印机类型',
    stepMotion: '运动参数',
    stepStepperX: 'X轴电机',
    stepStepperY: 'Y轴电机',
    stepStepperZ: 'Z轴电机',
    stepExtruder: '挤出机',
    stepHeaterBed: '热床',
    stepFan: '风扇',
    stepTmc: 'TMC驱动',
    stepToolboard: '工具板',
    stepProbe: '探针',
    stepBedMesh: '热床网格',
    stepInputShaper: '输入整形',
    stepDisplay: '显示屏',
    stepTempSensor: '温度传感器',
    stepExport: '导出配置',
    
    // Phases
    phaseBasic: '基本配置',
    phaseAdvanced: '高级配置',
    
    // Common
    next: '下一步',
    prev: '上一步',
    export: '导出配置',
    copy: '复制',
    exportCfg: '导出 .cfg 文件',
    exportJson: '导出 .json 文件',
    configPreview: '配置预览',
    
    // Welcome
    welcomeTitle: '欢迎使用 Kalico 配置向导',
    welcomeDesc: '本工具将引导您一步步创建 Kalico (Klipper) 打印机配置文件。\n即使您是完全的新手，也能轻松完成配置。',
    featureEasy: '简单易用',
    featureEasyDesc: '分步引导，每一步都有详细说明',
    featureSmart: '智能填充',
    featureSmartDesc: '选择主板自动填充引脚配置',
    featureExport: '双格式导出',
    featureExportDesc: '支持 .cfg 和 .json 两种格式',
    startConfig: '开始配置',
    
    // MCU
    mcuTitle: 'MCU 连接配置',
    mcuDesc: 'MCU (微控制器) 是打印机的主控板。需要配置它与树莓派/电脑的连接方式。',
    mcuWhat: '什么是MCU？',
    mcuWhatDesc: 'MCU就是打印机的"大脑"，通常是主板上的主芯片（如STM32、ATmega等）。\n它负责控制电机、读取温度、执行G-code指令等。',
    connectionType: '选择连接方式',
    serial: 'USB 串口',
    canbus: 'CAN 总线',
    selectBoard: '选择主板（自动填充引脚）',
    selectBoardPlaceholder: '选择您的主板型号',
    serialPath: '串口路径',
    baudRate: '波特率',
    canbusUuid: 'CAN UUID',
    canbusInterface: 'CAN 接口',
    
    // Kinematics
    kinematicsTitle: '打印机类型',
    kinematicsDesc: '选择您的打印机机械结构类型。不同的运动学类型决定了XYZ轴的运动方式。',
    cartesian: 'Cartesian（笛卡尔）',
    cartesianDesc: 'XYZ三轴独立运动，最常见类型。Ender 3、CR-10等。',
    corexy: 'CoreXY',
    corexyDesc: 'XY轴联动，速度快精度高。Voron、RatRig等。',
    corexz: 'CoreXZ',
    corexzDesc: 'XZ轴联动，Y轴独立。某些特殊结构打印机。',
    delta: 'Delta（三角洲）',
    deltaDesc: '三臂并联结构，打印高度大。Kossel、Rostock等。',
    
    // Motion
    motionTitle: '运动参数',
    motionDesc: '设置打印机的尺寸、最大速度和加速度。这些参数决定了打印机的运动性能上限。',
    printerSize: '打印机尺寸 (mm)',
    sizeX: 'X轴行程 (mm)',
    sizeY: 'Y轴行程 (mm)',
    sizeZ: 'Z轴行程 (mm)',
    maxVelocity: '最大速度 (mm/s)',
    maxAccel: '最大加速度 (mm/s²)',
    squareCornerVelocity: '直角速度 (mm/s)',
    maxZVelocity: 'Z轴最大速度 (mm/s)',
    maxZAccel: 'Z轴最大加速度 (mm/s²)',
    
    // Stepper
    stepperTitle: '轴步进电机配置',
    stepPin: 'STEP 引脚',
    dirPin: 'DIR 引脚',
    enablePin: 'EN 引脚',
    microsteps: '微步数',
    rotationDistance: '旋转距离 (mm)',
    endstopPin: '限位引脚',
    positionEndstop: '限位位置 (mm)',
    positionMax: '最大位置 (mm)',
    homingSpeed: '归位速度 (mm/s)',
    
    // Extruder
    extruderTitle: '挤出机配置',
    extruderDesc: '挤出机负责将耗材送入热端融化并挤出。需要配置电机、加热器和温度传感器。',
    hasExtruder: '是否有挤出机',
    nozzleDiameter: '喷嘴直径 (mm)',
    filamentDiameter: '耗材直径 (mm)',
    heaterPin: '加热引脚',
    sensorType: '传感器类型',
    sensorPin: '传感器引脚',
    control: '温控方式',
    minTemp: '最低温度 (°C)',
    maxTemp: '最高温度 (°C)',
    
    // Heater Bed
    heaterBedTitle: '热床配置',
    heaterBedDesc: '热床用于加热打印平台，提高耗材附着力。如果您的打印机没有热床，可以跳过此步。',
    hasHeaterBed: '有热床',
    noHeaterBed: '无热床',
    
    // Fan
    fanTitle: '风扇配置',
    fanDesc: '配置打印机的冷却风扇。零件冷却风扇用于在打印过程中冷却耗材，提高打印质量。',
    fanPin: '风扇引脚',
    maxPower: '最大功率',
    
    // TMC
    tmcTitle: 'TMC 驱动配置',
    tmcDesc: 'TMC步进驱动芯片可以大幅降低电机噪音、提高精度。如果您的驱动板不支持TMC，可以跳过此步。',
    driverType: '驱动类型选择',
    runCurrent: '运行电流 (A)',
    stealthchopThreshold: '静音模式阈值',
    
    // Toolboard
    toolboardTitle: '工具板配置',
    toolboardDesc: '工具板（Toolhead Board）安装在打印头上，通过CAN总线与主板通信，减少布线。',
    hasToolboard: '是否使用工具板',
    toolboardType: '工具板型号',
    toolboardName: '名称',
    
    // Probe
    probeTitle: '探针配置',
    probeDesc: '探针用于自动热床调平和Z轴归位。如果您的打印机没有探针，可以跳过此步。',
    hasProbe: '是否有探针',
    probeType: '探针类型',
    xOffset: 'X偏移 (mm)',
    yOffset: 'Y偏移 (mm)',
    zOffset: 'Z偏移 (mm)',
    probeSpeed: '探测速度 (mm/s)',
    samples: '采样次数',
    
    // Bed Mesh
    bedMeshTitle: '热床网格调平',
    bedMeshDesc: '热床网格调平通过探测多个点来补偿热床不平整。需要先配置探针。',
    hasBedMesh: '启用热床网格',
    probeCount: '探测点数 (X, Y)',
    meshMin: '网格最小坐标 (X, Y)',
    meshMax: '网格最大坐标 (X, Y)',
    algorithm: '插值算法',
    
    // Input Shaper
    inputShaperTitle: '输入整形',
    inputShaperDesc: '输入整形用于补偿打印机的共振，减少振纹，提高打印质量。',
    hasInputShaper: '启用输入整形',
    shaperType: '整形器类型',
    shaperFreqX: 'X轴频率 (Hz)',
    shaperFreqY: 'Y轴频率 (Hz)',
    
    // Display
    displayTitle: '显示屏配置',
    displayDesc: '配置LCD显示屏。如果您的打印机没有显示屏，可以跳过此步。',
    hasDisplay: '是否有显示屏',
    lcdType: '显示屏类型',
    
    // Temp Sensor
    tempSensorTitle: '温度传感器',
    tempSensorDesc: '添加额外的温度传感器，用于监控机箱温度、主板温度等。',
    hasSensors: '添加传感器',
    sensorName: '名称',
    
    // Export
    exportTitle: '导出配置',
    exportDesc: '恭喜！您已完成所有配置。现在可以导出您的打印机配置文件了。',
    cfgFormat: 'CFG 格式',
    cfgFormatDesc: 'Kalico/Klipper 原生配置格式',
    jsonFormat: 'JSON 格式',
    jsonFormatDesc: '结构化数据格式，便于程序处理',
    exportCfgFile: '导出 printer.cfg',
    exportJsonFile: '导出 printer.json',
    copyCfg: '复制 CFG 格式',
    copyJson: '复制 JSON 格式',
    copied: '已复制到剪贴板',
    exported: '已导出',
    
    // Info boxes
    info: '提示',
    warning: '警告',
    safetyTip: '安全提示',
  },
  en: {
    // Header
    appTitle: 'Kalico Printer Config Wizard',
    langSwitch: '中文',
    
    // Steps
    stepWelcome: 'Welcome',
    stepMcu: 'MCU Connection',
    stepKinematics: 'Printer Type',
    stepMotion: 'Motion',
    stepStepperX: 'X Axis',
    stepStepperY: 'Y Axis',
    stepStepperZ: 'Z Axis',
    stepExtruder: 'Extruder',
    stepHeaterBed: 'Heater Bed',
    stepFan: 'Fan',
    stepTmc: 'TMC Driver',
    stepToolboard: 'Toolboard',
    stepProbe: 'Probe',
    stepBedMesh: 'Bed Mesh',
    stepInputShaper: 'Input Shaper',
    stepDisplay: 'Display',
    stepTempSensor: 'Temp Sensor',
    stepExport: 'Export',
    
    // Phases
    phaseBasic: 'Basic',
    phaseAdvanced: 'Advanced',
    
    // Common
    next: 'Next',
    prev: 'Previous',
    export: 'Export Config',
    copy: 'Copy',
    exportCfg: 'Export .cfg file',
    exportJson: 'Export .json file',
    configPreview: 'Config Preview',
    
    // Welcome
    welcomeTitle: 'Welcome to Kalico Config Wizard',
    welcomeDesc: 'This tool will guide you step by step to create a Kalico (Klipper) printer configuration file.\nEven if you are a complete beginner, you can easily complete the configuration.',
    featureEasy: 'Easy to Use',
    featureEasyDesc: 'Step-by-step guidance with detailed explanations',
    featureSmart: 'Smart Fill',
    featureSmartDesc: 'Auto-fill pin config when selecting board',
    featureExport: 'Dual Format Export',
    featureExportDesc: 'Support both .cfg and .json formats',
    startConfig: 'Start Configuration',
    
    // MCU
    mcuTitle: 'MCU Connection Configuration',
    mcuDesc: 'MCU (Microcontroller Unit) is the main control board of the printer. Configure how it connects to Raspberry Pi/computer.',
    mcuWhat: 'What is MCU?',
    mcuWhatDesc: 'MCU is the "brain" of the printer, usually the main chip on the board (like STM32, ATmega).\nIt controls motors, reads temperatures, executes G-code commands, etc.',
    connectionType: 'Connection Type',
    serial: 'USB Serial',
    canbus: 'CAN Bus',
    selectBoard: 'Select Board (Auto-fill pins)',
    selectBoardPlaceholder: 'Select your board model',
    serialPath: 'Serial Path',
    baudRate: 'Baud Rate',
    canbusUuid: 'CAN UUID',
    canbusInterface: 'CAN Interface',
    
    // Kinematics
    kinematicsTitle: 'Printer Type',
    kinematicsDesc: 'Select your printer mechanical structure type. Different kinematics determine how XYZ axes move.',
    cartesian: 'Cartesian',
    cartesianDesc: 'XYZ axes move independently, most common. Ender 3, CR-10, etc.',
    corexy: 'CoreXY',
    corexyDesc: 'XY axes linked, fast and precise. Voron, RatRig, etc.',
    corexz: 'CoreXZ',
    corexzDesc: 'XZ axes linked, Y independent.',
    delta: 'Delta',
    deltaDesc: 'Three-arm parallel structure, tall print height. Kossel, Rostock, etc.',
    
    // Motion
    motionTitle: 'Motion Parameters',
    motionDesc: 'Set printer dimensions, maximum speed and acceleration. These parameters determine the printer motion performance limits.',
    printerSize: 'Printer Size (mm)',
    sizeX: 'X Axis Travel (mm)',
    sizeY: 'Y Axis Travel (mm)',
    sizeZ: 'Z Axis Travel (mm)',
    maxVelocity: 'Max Velocity (mm/s)',
    maxAccel: 'Max Acceleration (mm/s²)',
    squareCornerVelocity: 'Square Corner Velocity (mm/s)',
    maxZVelocity: 'Z Max Velocity (mm/s)',
    maxZAccel: 'Z Max Acceleration (mm/s²)',
    
    // Stepper
    stepperTitle: 'Axis Stepper Configuration',
    stepPin: 'STEP Pin',
    dirPin: 'DIR Pin',
    enablePin: 'EN Pin',
    microsteps: 'Microsteps',
    rotationDistance: 'Rotation Distance (mm)',
    endstopPin: 'Endstop Pin',
    positionEndstop: 'Endstop Position (mm)',
    positionMax: 'Max Position (mm)',
    homingSpeed: 'Homing Speed (mm/s)',
    
    // Extruder
    extruderTitle: 'Extruder Configuration',
    extruderDesc: 'The extruder feeds filament into the hotend for melting and extrusion. Configure motor, heater and temperature sensor.',
    hasExtruder: 'Has Extruder',
    nozzleDiameter: 'Nozzle Diameter (mm)',
    filamentDiameter: 'Filament Diameter (mm)',
    heaterPin: 'Heater Pin',
    sensorType: 'Sensor Type',
    sensorPin: 'Sensor Pin',
    control: 'Control Method',
    minTemp: 'Min Temperature (°C)',
    maxTemp: 'Max Temperature (°C)',
    
    // Heater Bed
    heaterBedTitle: 'Heater Bed Configuration',
    heaterBedDesc: 'The heated bed warms the print platform to improve filament adhesion. Skip if your printer has no heated bed.',
    hasHeaterBed: 'Has Heated Bed',
    noHeaterBed: 'No Heated Bed',
    
    // Fan
    fanTitle: 'Fan Configuration',
    fanDesc: 'Configure printer cooling fans. The part cooling fan cools filament during printing for better quality.',
    fanPin: 'Fan Pin',
    maxPower: 'Max Power',
    
    // TMC
    tmcTitle: 'TMC Driver Configuration',
    tmcDesc: 'TMC stepper drivers can significantly reduce motor noise and improve precision. Skip if your drivers don\'t support TMC.',
    driverType: 'Driver Type',
    runCurrent: 'Run Current (A)',
    stealthchopThreshold: 'StealthChop Threshold',
    
    // Toolboard
    toolboardTitle: 'Toolboard Configuration',
    toolboardDesc: 'Toolhead Board is mounted on the print head, communicates with main board via CAN bus to reduce wiring.',
    hasToolboard: 'Use Toolboard',
    toolboardType: 'Toolboard Model',
    toolboardName: 'Name',
    
    // Probe
    probeTitle: 'Probe Configuration',
    probeDesc: 'Probes are used for automatic bed leveling and Z-axis homing. Skip if your printer has no probe.',
    hasProbe: 'Has Probe',
    probeType: 'Probe Type',
    xOffset: 'X Offset (mm)',
    yOffset: 'Y Offset (mm)',
    zOffset: 'Z Offset (mm)',
    probeSpeed: 'Probe Speed (mm/s)',
    samples: 'Samples',
    
    // Bed Mesh
    bedMeshTitle: 'Bed Mesh Leveling',
    bedMeshDesc: 'Bed mesh leveling compensates for bed unevenness by probing multiple points. Requires probe configuration first.',
    hasBedMesh: 'Enable Bed Mesh',
    probeCount: 'Probe Count (X, Y)',
    meshMin: 'Mesh Min (X, Y)',
    meshMax: 'Mesh Max (X, Y)',
    algorithm: 'Algorithm',
    
    // Input Shaper
    inputShaperTitle: 'Input Shaper',
    inputShaperDesc: 'Input shaper compensates for printer resonance, reducing ringing and improving print quality.',
    hasInputShaper: 'Enable Input Shaper',
    shaperType: 'Shaper Type',
    shaperFreqX: 'X Frequency (Hz)',
    shaperFreqY: 'Y Frequency (Hz)',
    
    // Display
    displayTitle: 'Display Configuration',
    displayDesc: 'Configure LCD display. Skip if your printer has no display.',
    hasDisplay: 'Has Display',
    lcdType: 'LCD Type',
    
    // Temp Sensor
    tempSensorTitle: 'Temperature Sensors',
    tempSensorDesc: 'Add extra temperature sensors to monitor chamber temperature, board temperature, etc.',
    hasSensors: 'Add Sensor',
    sensorName: 'Name',
    
    // Export
    exportTitle: 'Export Configuration',
    exportDesc: 'Congratulations! You have completed all configurations. Now you can export your printer configuration file.',
    cfgFormat: 'CFG Format',
    cfgFormatDesc: 'Kalico/Klipper native config format',
    jsonFormat: 'JSON Format',
    jsonFormatDesc: 'Structured data format, easy for program processing',
    exportCfgFile: 'Export printer.cfg',
    exportJsonFile: 'Export printer.json',
    copyCfg: 'Copy CFG Format',
    copyJson: 'Copy JSON Format',
    copied: 'Copied to clipboard',
    exported: 'Exported',
    
    // Info boxes
    info: 'Info',
    warning: 'Warning',
    safetyTip: 'Safety Tip',
  }
}

export function useI18n() {
  const locale = computed(() => currentLocale.value)
  
  function t(key) {
    return messages[currentLocale.value]?.[key] || messages['zh']?.[key] || key
  }
  
  function toggleLocale() {
    currentLocale.value = currentLocale.value === 'zh' ? 'en' : 'zh'
  }
  
  function setLocale(lang) {
    currentLocale.value = lang
  }
  
  return {
    locale,
    t,
    toggleLocale,
    setLocale
  }
}
