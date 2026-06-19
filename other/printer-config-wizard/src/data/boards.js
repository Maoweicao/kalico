export const boards = {
  // ========== BigTreeTech ==========
  'btt-skr-mini-e3-v3': {
    name: 'BTT SKR Mini E3 V3.0',
    desc: 'Creality Ender 3 升级首选',
    mcu: 'STM32G0B1',
    serial: '/dev/serial/by-id/usb-Kalico_stm32g0b1xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB13', dir_pin: '!PB12', enable_pin: '!PB14' },
      stepper_y: { step_pin: 'PB10', dir_pin: '!PB2', enable_pin: '!PB11' },
      stepper_z: { step_pin: 'PB0', dir_pin: 'PC5', enable_pin: '!PB1' },
      extruder: { step_pin: 'PB3', dir_pin: '!PB4', enable_pin: '!PD1' },
      heater_bed: { heater_pin: 'PD2' },
      fan: { pin: 'PC6' },
      tmc2209_x: { uart_pin: 'PC11' },
      tmc2209_y: { uart_pin: 'PC11' },
      tmc2209_z: { uart_pin: 'PC11' },
      tmc2209_e: { uart_pin: 'PC11' },
    },
    endstops: { x: '^PC1', y: '^PC3', z: '^PC2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'btt-skr-mini-e3-v2': {
    name: 'BTT SKR Mini E3 V2.0',
    desc: 'Ender 3/CR-10 升级',
    mcu: 'STM32F103',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f103xe_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB13', dir_pin: '!PB12', enable_pin: '!PB14' },
      stepper_y: { step_pin: 'PB10', dir_pin: '!PB2', enable_pin: '!PB11' },
      stepper_z: { step_pin: 'PB0', dir_pin: 'PC5', enable_pin: '!PB1' },
      extruder: { step_pin: 'PB3', dir_pin: '!PB4', enable_pin: '!PD1' },
      heater_bed: { heater_pin: 'PD2' },
      fan: { pin: 'PC6' },
      tmc2209_x: { uart_pin: 'PC11' },
      tmc2209_y: { uart_pin: 'PC11' },
      tmc2209_z: { uart_pin: 'PC11' },
      tmc2209_e: { uart_pin: 'PC11' },
    },
    endstops: { x: '^PC1', y: '^PC3', z: '^PC2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'btt-skr-2': {
    name: 'BTT SKR V2.0',
    desc: '高性能通用主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PD5', dir_pin: '!PD4', enable_pin: '!PD6' },
      stepper_z: { step_pin: 'PA15', dir_pin: '!PA10', enable_pin: '!PA8' },
      extruder: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PD12' },
      fan: { pin: 'PB7' },
      tmc2209_x: { uart_pin: 'PC13' },
      tmc2209_y: { uart_pin: 'PE1' },
      tmc2209_z: { uart_pin: 'PE4' },
      tmc2209_e: { uart_pin: 'PE1' },
    },
    endstops: { x: '^PB4', y: '^PB3', z: '^PA0' },
    thermistors: { extruder: 'PA2', heater_bed: 'PA1' }
  },
  'btt-skr-3': {
    name: 'BTT SKR V3.0',
    desc: 'STM32H723高性能主板',
    mcu: 'STM32H723',
    serial: '/dev/serial/by-id/usb-Kalico_stm32h723xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PD5', dir_pin: '!PD4', enable_pin: '!PD6' },
      stepper_z: { step_pin: 'PA15', dir_pin: '!PA10', enable_pin: '!PA8' },
      extruder: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PD12' },
      fan: { pin: 'PB7' },
      tmc2209_x: { uart_pin: 'PC13' },
      tmc2209_y: { uart_pin: 'PE1' },
      tmc2209_z: { uart_pin: 'PE4' },
      tmc2209_e: { uart_pin: 'PD3' },
    },
    endstops: { x: '^PB4', y: '^PB3', z: '^PA0' },
    thermistors: { extruder: 'PA2', heater_bed: 'PA1' }
  },
  'btt-skr-pico': {
    name: 'BTT SKR Pico',
    desc: '紧凑型RP2040主板',
    mcu: 'RP2040',
    serial: '/dev/serial/by-id/usb-Kalico_rp2040_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'GPIO11', dir_pin: '!GPIO10', enable_pin: '!GPIO12' },
      stepper_y: { step_pin: 'GPIO8', dir_pin: '!GPIO7', enable_pin: '!GPIO9' },
      stepper_z: { step_pin: 'GPIO6', dir_pin: '!GPIO5', enable_pin: '!GPIO4' },
      extruder: { step_pin: 'GPIO3', dir_pin: '!GPIO2', enable_pin: '!GPIO1' },
      heater_bed: { heater_pin: 'GPIO21' },
      fan: { pin: 'GPIO17' },
      tmc2209_x: { uart_pin: 'GPIO13' },
      tmc2209_y: { uart_pin: 'GPIO13' },
      tmc2209_z: { uart_pin: 'GPIO13' },
      tmc2209_e: { uart_pin: 'GPIO13' },
    },
    endstops: { x: '^GPIO16', y: '^GPIO17', z: '^GPIO18' },
    thermistors: { extruder: 'GPIO26', heater_bed: 'GPIO27' }
  },
  'btt-octopus-v1.1': {
    name: 'BTT Octopus V1.1',
    desc: '8轴高端主板',
    mcu: 'STM32F446',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f446xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PF13', dir_pin: '!PF12', enable_pin: '!PF14' },
      stepper_y: { step_pin: 'PG0', dir_pin: '!PG1', enable_pin: '!PF15' },
      stepper_z: { step_pin: 'PF11', dir_pin: '!PG3', enable_pin: '!PG5' },
      extruder: { step_pin: 'PG4', dir_pin: '!PC1', enable_pin: '!PA0' },
      heater_bed: { heater_pin: 'PA2' },
      fan: { pin: 'PA8' },
      tmc2209_x: { uart_pin: 'PC4' },
      tmc2209_y: { uart_pin: 'PD11' },
      tmc2209_z: { uart_pin: 'PC6' },
      tmc2209_e: { uart_pin: 'PC7' },
    },
    endstops: { x: '^PG6', y: '^PG9', z: '^PG10' },
    thermistors: { extruder: 'PF4', heater_bed: 'PF3' }
  },
  'btt-octopus-pro-v1.0': {
    name: 'BTT Octopus Pro V1.0',
    desc: '8轴专业版 H723',
    mcu: 'STM32H723',
    serial: '/dev/serial/by-id/usb-Kalico_stm32h723xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PF13', dir_pin: '!PF12', enable_pin: '!PF14' },
      stepper_y: { step_pin: 'PG0', dir_pin: '!PG1', enable_pin: '!PF15' },
      stepper_z: { step_pin: 'PF11', dir_pin: '!PG3', enable_pin: '!PG5' },
      extruder: { step_pin: 'PG4', dir_pin: '!PC1', enable_pin: '!PA0' },
      heater_bed: { heater_pin: 'PA2' },
      fan: { pin: 'PA8' },
      tmc2209_x: { uart_pin: 'PC4' },
      tmc2209_y: { uart_pin: 'PD11' },
      tmc2209_z: { uart_pin: 'PC6' },
      tmc2209_e: { uart_pin: 'PC7' },
    },
    endstops: { x: '^PG6', y: '^PG9', z: '^PG10' },
    thermistors: { extruder: 'PF4', heater_bed: 'PF3' }
  },
  'btt-manta-m4p': {
    name: 'BTT Manta M4P',
    desc: 'CB1/CB2计算模块主板',
    mcu: 'STM32G0B1',
    serial: '/dev/serial/by-id/usb-Kalico_stm32g0b1xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB15', dir_pin: '!PB14', enable_pin: '!PA8' },
      stepper_y: { step_pin: 'PB12', dir_pin: '!PB11', enable_pin: '!PB13' },
      stepper_z: { step_pin: 'PB10', dir_pin: '!PB2', enable_pin: '!PB1' },
      extruder: { step_pin: 'PB0', dir_pin: 'PC5', enable_pin: '!PB1' },
      heater_bed: { heater_pin: 'PA1' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC11' },
      tmc2209_y: { uart_pin: 'PC10' },
      tmc2209_z: { uart_pin: 'PC12' },
      tmc2209_e: { uart_pin: 'PD2' },
    },
    endstops: { x: '^PC0', y: '^PC1', z: '^PC2' },
    thermistors: { extruder: 'PC3', heater_bed: 'PC4' }
  },
  'btt-manta-m8p': {
    name: 'BTT Manta M8P',
    desc: '8轴计算模块主板',
    mcu: 'STM32G0B1',
    serial: '/dev/serial/by-id/usb-Kalico_stm32g0b1xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PF13', dir_pin: '!PF12', enable_pin: '!PF14' },
      stepper_y: { step_pin: 'PG0', dir_pin: '!PG1', enable_pin: '!PF15' },
      stepper_z: { step_pin: 'PF11', dir_pin: '!PG3', enable_pin: '!PG5' },
      extruder: { step_pin: 'PG4', dir_pin: '!PC1', enable_pin: '!PA0' },
      heater_bed: { heater_pin: 'PA2' },
      fan: { pin: 'PA8' },
      tmc2209_x: { uart_pin: 'PC4' },
      tmc2209_y: { uart_pin: 'PD11' },
      tmc2209_z: { uart_pin: 'PC6' },
      tmc2209_e: { uart_pin: 'PC7' },
    },
    endstops: { x: '^PG6', y: '^PG9', z: '^PG10' },
    thermistors: { extruder: 'PF4', heater_bed: 'PF3' }
  },

  // ========== Creality ==========
  'creality-v4.2.7': {
    name: 'Creality V4.2.7',
    desc: 'Ender 3 V2 原装板',
    mcu: 'STM32F103',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f103xe_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB9', dir_pin: '!PC2', enable_pin: '!PA8' },
      stepper_y: { step_pin: 'PB7', dir_pin: '!PB8', enable_pin: '!PA8' },
      stepper_z: { step_pin: 'PB5', dir_pin: '!PB6', enable_pin: '!PA8' },
      extruder: { step_pin: 'PB3', dir_pin: '!PB4', enable_pin: '!PA8' },
      heater_bed: { heater_pin: 'PA1' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC13' },
      tmc2209_y: { uart_pin: 'PC13' },
      tmc2209_z: { uart_pin: 'PC13' },
      tmc2209_e: { uart_pin: 'PC13' },
    },
    endstops: { x: '^PA15', y: '^PC0', z: '^PC1' },
    thermistors: { extruder: 'PC3', heater_bed: 'PC4' }
  },
  'creality-v4.2.2': {
    name: 'Creality V4.2.2',
    desc: 'Ender 3/CR-10 原装板',
    mcu: 'STM32F103',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f103xe_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB9', dir_pin: '!PC2', enable_pin: '!PA8' },
      stepper_y: { step_pin: 'PB7', dir_pin: '!PB8', enable_pin: '!PA8' },
      stepper_z: { step_pin: 'PB5', dir_pin: '!PB6', enable_pin: '!PA8' },
      extruder: { step_pin: 'PB3', dir_pin: '!PB4', enable_pin: '!PA8' },
      heater_bed: { heater_pin: 'PA1' },
      fan: { pin: 'PA0' },
    },
    endstops: { x: '^PA15', y: '^PC0', z: '^PC1' },
    thermistors: { extruder: 'PC3', heater_bed: 'PC4' }
  },
  'creality-v4.3.1': {
    name: 'Creality V4.3.1',
    desc: 'K1/Max 主板',
    mcu: 'STM32F103',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f103xe_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PB8', dir_pin: '!PB7', enable_pin: '!PA8' },
      stepper_y: { step_pin: 'PB6', dir_pin: '!PB5', enable_pin: '!PA8' },
      stepper_z: { step_pin: 'PB4', dir_pin: '!PB3', enable_pin: '!PA8' },
      extruder: { step_pin: 'PD2', dir_pin: '!PD3', enable_pin: '!PA8' },
      heater_bed: { heater_pin: 'PA1' },
      fan: { pin: 'PA0' },
    },
    endstops: { x: '^PA15', y: '^PC0', z: '^PC1' },
    thermistors: { extruder: 'PC3', heater_bed: 'PC4' }
  },

  // ========== MKS ==========
  'mks-robin-nano-v3': {
    name: 'MKS Robin Nano V3.0',
    desc: '3.5触摸屏主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE3', dir_pin: '!PE2', enable_pin: '!PE4' },
      stepper_y: { step_pin: 'PE0', dir_pin: '!PB9', enable_pin: '!PE1' },
      stepper_z: { step_pin: 'PB5', dir_pin: '!PB4', enable_pin: '!PB8' },
      extruder: { step_pin: 'PD6', dir_pin: '!PD3', enable_pin: '!PB3' },
      heater_bed: { heater_pin: 'PA0' },
      fan: { pin: 'PB0' },
    },
    endstops: { x: '^PA15', y: '^PA12', z: '^PA11' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'mks-robin-nano-v2': {
    name: 'MKS Robin Nano V2.0',
    desc: 'STM32F407主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE3', dir_pin: '!PE2', enable_pin: '!PE4' },
      stepper_y: { step_pin: 'PE0', dir_pin: '!PB9', enable_pin: '!PE1' },
      stepper_z: { step_pin: 'PB5', dir_pin: '!PB4', enable_pin: '!PB8' },
      extruder: { step_pin: 'PD6', dir_pin: '!PD3', enable_pin: '!PB3' },
      heater_bed: { heater_pin: 'PA0' },
      fan: { pin: 'PB0' },
    },
    endstops: { x: '^PA15', y: '^PA12', z: '^PA11' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'mks-sgen-l': {
    name: 'MKS SGen-L',
    desc: 'LPC1768主板',
    mcu: 'LPC1768',
    serial: '/dev/serial/by-id/usb-Kalico_lpc1768_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'P2.2', dir_pin: '!P2.6', enable_pin: '!P2.1' },
      stepper_y: { step_pin: 'P0.19', dir_pin: '!P0.20', enable_pin: '!P2.8' },
      stepper_z: { step_pin: 'P2.13', dir_pin: '!P0.11', enable_pin: '!P2.12' },
      extruder: { step_pin: 'P2.0', dir_pin: '!P0.5', enable_pin: '!P0.4' },
      heater_bed: { heater_pin: 'P2.5' },
      fan: { pin: 'P2.4' },
    },
    endstops: { x: '^P1.29', y: '^P1.28', z: '^P1.27' },
    thermistors: { extruder: 'P0.23', heater_bed: 'P0.24' }
  },
  'mks-monster8': {
    name: 'MKS Monster8',
    desc: '8轴STM32主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PE5', enable_pin: '!PC13' },
      stepper_y: { step_pin: 'PE4', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PE2', dir_pin: '!PE1', enable_pin: '!PB9' },
      extruder: { step_pin: 'PB8', dir_pin: '!PB7', enable_pin: '!PB6' },
      heater_bed: { heater_pin: 'PB5' },
      fan: { pin: 'PB4' },
    },
    endstops: { x: '^PA15', y: '^PA14', z: '^PA13' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'mks-eagle': {
    name: 'MKS Eagle',
    desc: '高性能H723主板',
    mcu: 'STM32H723',
    serial: '/dev/serial/by-id/usb-Kalico_stm32h723xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PE5', enable_pin: '!PC13' },
      stepper_y: { step_pin: 'PE4', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PE2', dir_pin: '!PE1', enable_pin: '!PB9' },
      extruder: { step_pin: 'PB8', dir_pin: '!PB7', enable_pin: '!PB6' },
      heater_bed: { heater_pin: 'PB5' },
      fan: { pin: 'PB4' },
    },
    endstops: { x: '^PA15', y: '^PA14', z: '^PA13' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },

  // ========== FYSETC ==========
  'fysetc-spider': {
    name: 'FYSETC Spider',
    desc: '高性能多轴主板',
    mcu: 'STM32F446',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f446xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PB7', dir_pin: '!PB6', enable_pin: '!PE0' },
      extruder: { step_pin: 'PB4', dir_pin: '!PB3', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PB11' },
      fan: { pin: 'PB15' },
    },
    endstops: { x: '^PA0', y: '^PC3', z: '^PA2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'fysetc-spider-v2': {
    name: 'FYSETC Spider V2.2',
    desc: '升级版多轴主板',
    mcu: 'STM32F446',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f446xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PB7', dir_pin: '!PB6', enable_pin: '!PE0' },
      extruder: { step_pin: 'PB4', dir_pin: '!PB3', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PB11' },
      fan: { pin: 'PB15' },
    },
    endstops: { x: '^PA0', y: '^PC3', z: '^PA2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'fysetc-cheetah-v3': {
    name: 'FYSETC Cheetah V3.0',
    desc: '紧凑型主板',
    mcu: 'STM32F446',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f446xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PB7', dir_pin: '!PB6', enable_pin: '!PE0' },
      extruder: { step_pin: 'PB4', dir_pin: '!PB3', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PB11' },
      fan: { pin: 'PB15' },
    },
    endstops: { x: '^PA0', y: '^PC3', z: '^PA2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },
  'fysetc-s6': {
    name: 'FYSETC S6 V2.0',
    desc: '6轴STM32主板',
    mcu: 'STM32F446',
    serial: '/dev/serial/by-id/usb-Kalico_stm32f446xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE6', dir_pin: '!PA14', enable_pin: '!PE0' },
      stepper_y: { step_pin: 'PE2', dir_pin: '!PE3', enable_pin: '!PE0' },
      stepper_z: { step_pin: 'PB7', dir_pin: '!PB6', enable_pin: '!PE0' },
      extruder: { step_pin: 'PB4', dir_pin: '!PB3', enable_pin: '!PE0' },
      heater_bed: { heater_pin: 'PB11' },
      fan: { pin: 'PB15' },
    },
    endstops: { x: '^PA0', y: '^PC3', z: '^PA2' },
    thermistors: { extruder: 'PC0', heater_bed: 'PC1' }
  },

  // ========== FLY (Mellow) ==========
  'fly-d8-f407': {
    name: 'FLY D8 (F407)',
    desc: '8轴高性能主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Klipper_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PA8', enable_pin: '!PA15' },
      stepper_y: { step_pin: 'PE4', dir_pin: 'PC11', enable_pin: '!PC12' },
      stepper_z: { step_pin: 'PE3', dir_pin: '!PD1', enable_pin: '!PD2' },
      stepper_z1: { step_pin: 'PE2', dir_pin: 'PD4', enable_pin: '!PD5' },
      stepper_z2: { step_pin: 'PE1', dir_pin: '!PD7', enable_pin: '!PB6' },
      stepper_z3: { step_pin: 'PE0', dir_pin: 'PC13', enable_pin: '!PC14' },
      extruder: { step_pin: 'PE7', dir_pin: 'PE11', enable_pin: '!PE10' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC9' },
      tmc2209_y: { uart_pin: 'PC10' },
      tmc2209_z: { uart_pin: 'PD0' },
      tmc2209_z1: { uart_pin: 'PD3' },
      tmc2209_z2: { uart_pin: 'PD6' },
      tmc2209_z3: { uart_pin: 'PB7' },
      tmc2209_e: { uart_pin: 'PC15' },
    },
    endstops: { x: 'PD9', y: '!PD8', z: '!PD11' },
    thermistors: { extruder: 'PC4', heater_bed: 'PC5' }
  },
  'fly-d8-pro-h723': {
    name: 'FLY D8 Pro (H723)',
    desc: '8轴H723高性能主板',
    mcu: 'STM32H723',
    serial: '/dev/serial/by-id/usb-Klipper_stm32h723xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PA8', enable_pin: '!PA15' },
      stepper_y: { step_pin: 'PE4', dir_pin: 'PC11', enable_pin: '!PC12' },
      stepper_z: { step_pin: 'PE3', dir_pin: '!PD1', enable_pin: '!PD2' },
      stepper_z1: { step_pin: 'PE2', dir_pin: 'PD4', enable_pin: '!PD5' },
      stepper_z2: { step_pin: 'PE1', dir_pin: '!PD7', enable_pin: '!PB6' },
      stepper_z3: { step_pin: 'PE0', dir_pin: 'PC13', enable_pin: '!PC14' },
      extruder: { step_pin: 'PE7', dir_pin: 'PE11', enable_pin: '!PE10' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC9' },
      tmc2209_y: { uart_pin: 'PC10' },
      tmc2209_z: { uart_pin: 'PD0' },
      tmc2209_z1: { uart_pin: 'PD3' },
      tmc2209_z2: { uart_pin: 'PD6' },
      tmc2209_z3: { uart_pin: 'PB7' },
      tmc2209_e: { uart_pin: 'PC15' },
    },
    endstops: { x: 'PD9', y: '!PD8', z: '!PD11' },
    thermistors: { extruder: 'PC4', heater_bed: 'PC5' }
  },
  'fly-cdy-v3': {
    name: 'FLY CDY V3',
    desc: '6轴STM32F407主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Klipper_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PC0', enable_pin: '!PC1' },
      stepper_y: { step_pin: 'PE4', dir_pin: '!PC13', enable_pin: '!PC14' },
      stepper_z: { step_pin: 'PE3', dir_pin: 'PB7', enable_pin: '!PB8' },
      extruder: { step_pin: 'PE2', dir_pin: 'PD6', enable_pin: '!PD7' },
      extruder1: { step_pin: 'PE1', dir_pin: '!PD3', enable_pin: '!PD4' },
      extruder2: { step_pin: 'PE0', dir_pin: '!PA15', enable_pin: '!PD0' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC15' },
      tmc2209_y: { uart_pin: 'PA8' },
      tmc2209_z: { uart_pin: 'PB6' },
      tmc2209_e: { uart_pin: 'PD5' },
      tmc2209_e1: { uart_pin: 'PD1' },
      tmc2209_e2: { uart_pin: 'PE9' },
    },
    endstops: { x: '^PC7', y: '^PD11', z: '^PB10' },
    thermistors: { extruder: 'PA3', heater_bed: 'PB1' }
  },
  'fly-super8-h723': {
    name: 'FLY Super8 (H723)',
    desc: '8轴H723高端主板',
    mcu: 'STM32H723',
    serial: '/dev/serial/by-id/usb-Klipper_stm32h723xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PA8', enable_pin: '!PA15' },
      stepper_y: { step_pin: 'PE4', dir_pin: 'PC11', enable_pin: '!PC12' },
      stepper_z: { step_pin: 'PE3', dir_pin: '!PD1', enable_pin: '!PD2' },
      extruder: { step_pin: 'PE7', dir_pin: 'PE11', enable_pin: '!PE10' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC9' },
      tmc2209_y: { uart_pin: 'PC10' },
      tmc2209_z: { uart_pin: 'PD0' },
      tmc2209_e: { uart_pin: 'PC15' },
    },
    endstops: { x: 'PD9', y: '!PD8', z: '!PD11' },
    thermistors: { extruder: 'PC4', heater_bed: 'PC5' }
  },
  'fly-e3-v2': {
    name: 'FLY E3 V2.0',
    desc: '紧凑型STM32主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Klipper_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PC0', enable_pin: '!PC1' },
      stepper_y: { step_pin: 'PE4', dir_pin: '!PC13', enable_pin: '!PC14' },
      stepper_z: { step_pin: 'PE3', dir_pin: 'PB7', enable_pin: '!PB8' },
      extruder: { step_pin: 'PE2', dir_pin: 'PD6', enable_pin: '!PD7' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
      tmc2209_x: { uart_pin: 'PC15' },
      tmc2209_y: { uart_pin: 'PA8' },
      tmc2209_z: { uart_pin: 'PB6' },
      tmc2209_e: { uart_pin: 'PD5' },
    },
    endstops: { x: '^PC7', y: '^PD11', z: '^PB10' },
    thermistors: { extruder: 'PA3', heater_bed: 'PB1' }
  },
  'fly-gemini-v2': {
    name: 'FLY Gemini V2.0',
    desc: '集成上位机主板',
    mcu: 'STM32F407',
    serial: '/dev/serial/by-id/usb-Klipper_stm32f407xx_000000000000000000000000-if00',
    pins: {
      stepper_x: { step_pin: 'PE5', dir_pin: 'PC0', enable_pin: '!PC1' },
      stepper_y: { step_pin: 'PE4', dir_pin: '!PC13', enable_pin: '!PC14' },
      stepper_z: { step_pin: 'PE3', dir_pin: 'PB7', enable_pin: '!PB8' },
      extruder: { step_pin: 'PE2', dir_pin: 'PD6', enable_pin: '!PD7' },
      heater_bed: { heater_pin: 'PB0' },
      fan: { pin: 'PA0' },
    },
    endstops: { x: '^PC7', y: '^PD11', z: '^PB10' },
    thermistors: { extruder: 'PA3', heater_bed: 'PB1' }
  },

  // ========== Duet ==========
  'duet2': {
    name: 'Duet 2 WiFi/Ethernet',
    desc: '高端网络主板',
    mcu: 'SAM4E8E',
    serial: '/dev/ttyACM0',
    pins: {
      stepper_x: { step_pin: 'PC6', dir_pin: '!PC9', enable_pin: '!PA2' },
      stepper_y: { step_pin: 'PC20', dir_pin: '!PC24', enable_pin: '!PA2' },
      stepper_z: { step_pin: 'PC17', dir_pin: '!PC16', enable_pin: '!PA2' },
      extruder: { step_pin: 'PD5', dir_pin: '!PD4', enable_pin: '!PA2' },
      heater_bed: { heater_pin: 'PC23' },
      fan: { pin: 'PC26' },
    },
    endstops: { x: '^PB6', y: '^PB5', z: '^PB4' },
    thermistors: { extruder: 'PA20', heater_bed: 'PA19' }
  },
  'duet3-6hc': {
    name: 'Duet 3 6HC',
    desc: '6轴高端主板',
    mcu: 'SAME70Q20B',
    serial: '/dev/ttyACM0',
    pins: {
      stepper_x: { step_pin: 'PC6', dir_pin: '!PC9', enable_pin: '!PA2' },
      stepper_y: { step_pin: 'PC20', dir_pin: '!PC24', enable_pin: '!PA2' },
      stepper_z: { step_pin: 'PC17', dir_pin: '!PC16', enable_pin: '!PA2' },
      extruder: { step_pin: 'PD5', dir_pin: '!PD4', enable_pin: '!PA2' },
      heater_bed: { heater_pin: 'PC23' },
      fan: { pin: 'PC26' },
    },
    endstops: { x: '^PB6', y: '^PB5', z: '^PB4' },
    thermistors: { extruder: 'PA20', heater_bed: 'PA19' }
  },

  // ========== 经典主板 ==========
  'ramps-1.4': {
    name: 'RAMPS 1.4',
    desc: '经典Arduino主板',
    mcu: 'ATmega2560',
    serial: '/dev/ttyACM0',
    pins: {
      stepper_x: { step_pin: 'PF0', dir_pin: 'PF1', enable_pin: '!PD7' },
      stepper_y: { step_pin: 'PF6', dir_pin: '!PF7', enable_pin: '!PF2' },
      stepper_z: { step_pin: 'PL3', dir_pin: 'PL1', enable_pin: '!PK0' },
      extruder: { step_pin: 'PA4', dir_pin: 'PA6', enable_pin: '!PA2' },
      heater_bed: { heater_pin: 'PH5' },
      fan: { pin: 'PH6' },
    },
    endstops: { x: '^PE5', y: '^PJ1', z: '^PD3' },
    thermistors: { extruder: 'PK5', heater_bed: 'PK6' }
  },

  // ========== 工具板 ==========
  'btt-ebb36-v1.2': {
    name: 'BTT EBB36 V1.2',
    desc: 'CAN工具板 (挤出机)',
    mcu: 'STM32G0B1',
    serial: '',
    canbus: true,
    pins: {
      stepper_e: { step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2' },
      heater: { heater_pin: 'PB14' },
      fan: { pin: 'PB15' },
      tmc2209_e: { uart_pin: 'PD5' },
    },
    endstops: {},
    thermistors: { extruder: 'PA3' }
  },
  'btt-ebb42-v1.2': {
    name: 'BTT EBB42 V1.2',
    desc: 'CAN工具板 (Voron)',
    mcu: 'STM32G0B1',
    serial: '',
    canbus: true,
    pins: {
      stepper_e: { step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2' },
      heater: { heater_pin: 'PB14' },
      fan: { pin: 'PB15' },
      tmc2209_e: { uart_pin: 'PD5' },
    },
    endstops: {},
    thermistors: { extruder: 'PA3' }
  },
  'fly-sht36-v2': {
    name: 'FLY SHT36 V2.0',
    desc: 'CAN工具板',
    mcu: 'STM32F072',
    serial: '',
    canbus: true,
    pins: {
      stepper_e: { step_pin: 'PB15', dir_pin: 'PB14', enable_pin: '!PA8' },
      heater: { heater_pin: 'PB13' },
      fan: { pin: 'PB12' },
      tmc2209_e: { uart_pin: 'PB11' },
    },
    endstops: {},
    thermistors: { extruder: 'PB0' }
  },
  'fly-sht42-v2': {
    name: 'FLY SHT42 V2.0',
    desc: 'CAN工具板 (42步进)',
    mcu: 'STM32F072',
    serial: '',
    canbus: true,
    pins: {
      stepper_e: { step_pin: 'PB15', dir_pin: 'PB14', enable_pin: '!PA8' },
      heater: { heater_pin: 'PB13' },
      fan: { pin: 'PB12' },
      tmc2209_e: { uart_pin: 'PB11' },
    },
    endstops: {},
    thermistors: { extruder: 'PB0' }
  }
}

export const boardCategories = [
  {
    name: 'BigTreeTech',
    icon: 'Cpu',
    boards: [
      'btt-skr-mini-e3-v3', 'btt-skr-mini-e3-v2', 'btt-skr-2', 'btt-skr-3',
      'btt-skr-pico', 'btt-octopus-v1.1', 'btt-octopus-pro-v1.0',
      'btt-manta-m4p', 'btt-manta-m8p'
    ]
  },
  {
    name: 'Creality',
    icon: 'Printer',
    boards: ['creality-v4.2.7', 'creality-v4.2.2', 'creality-v4.3.1']
  },
  {
    name: 'MKS',
    icon: 'Monitor',
    boards: ['mks-robin-nano-v3', 'mks-robin-nano-v2', 'mks-sgen-l', 'mks-monster8', 'mks-eagle']
  },
  {
    name: 'FYSETC',
    icon: 'Cpu',
    boards: ['fysetc-spider', 'fysetc-spider-v2', 'fysetc-cheetah-v3', 'fysetc-s6']
  },
  {
    name: 'FLY (Mellow)',
    icon: 'Connection',
    boards: ['fly-d8-f407', 'fly-d8-pro-h723', 'fly-cdy-v3', 'fly-super8-h723', 'fly-e3-v2', 'fly-gemini-v2']
  },
  {
    name: 'Duet',
    icon: 'Connection',
    boards: ['duet2', 'duet3-6hc']
  },
  {
    name: '经典主板',
    icon: 'Cpu',
    boards: ['ramps-1.4']
  },
  {
    name: 'CAN工具板',
    icon: 'Connection',
    boards: ['btt-ebb36-v1.2', 'btt-ebb42-v1.2', 'fly-sht36-v2', 'fly-sht42-v2']
  }
]

export const toolboards = [
  { id: 'none', name: '无', desc: '不使用工具板' },
  { id: 'btt-ebb36-v1.2', name: 'BTT EBB36 V1.2', desc: 'CAN工具板，36mm间距' },
  { id: 'btt-ebb42-v1.2', name: 'BTT EBB42 V1.2', desc: 'CAN工具板，42mm间距' },
  { id: 'fly-sht36-v2', name: 'FLY SHT36 V2.0', desc: 'CAN工具板，36mm间距' },
  { id: 'fly-sht42-v2', name: 'FLY SHT42 V2.0', desc: 'CAN工具板，42mm间距' },
  { id: 'btt-sb2209-v1.0', name: 'BTT SB2209 V1.0', desc: 'StealthBurner工具板' },
  { id: 'btt-sb2240-v1.0', name: 'BTT SB2240 V1.0', desc: 'StealthBurner工具板' },
  { id: 'custom', name: '自定义', desc: '手动配置工具板引脚' }
]
