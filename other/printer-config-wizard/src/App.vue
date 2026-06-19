<template>
  <div class="app-container">
    <div class="app-header">
      <div class="header-content">
        <div class="logo-section">
          <el-icon :size="28" color="#409eff"><Setting /></el-icon>
          <h1>{{ t('appTitle') }}</h1>
        </div>
        <div class="header-actions">
          <el-button @click="toggleLocale" text>
            <el-icon><Operation /></el-icon>
            {{ t('langSwitch') }}
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="app-body">
      <div class="sidebar">
        <StepSidebar 
          :current-step="currentStep" 
          :steps="translatedSteps"
          @go-to-step="goToStep"
        />
      </div>
      
      <div class="main-content">
        <transition :name="slideDirection" mode="out-in">
          <component 
            :is="currentStepComponent" 
            :key="currentStep"
            :config="config"
            :t="t"
            @update="updateConfig"
            @next="nextStep"
            @prev="prevStep"
          />
        </transition>
      </div>
      
      <div class="preview-panel">
        <ConfigPreview :config="config" :t="t" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import { Setting, Operation } from '@element-plus/icons-vue'
import { useI18n } from './utils/i18n.js'
import StepSidebar from './components/StepSidebar.vue'
import ConfigPreview from './components/ConfigPreview.vue'
import WelcomeStep from './components/steps/WelcomeStep.vue'
import McuStep from './components/steps/McuStep.vue'
import KinematicsStep from './components/steps/KinematicsStep.vue'
import MotionStep from './components/steps/MotionStep.vue'
import StepperConfigStep from './components/steps/StepperConfigStep.vue'
import ExtruderStep from './components/steps/ExtruderStep.vue'
import HeaterBedStep from './components/steps/HeaterBedStep.vue'
import FanStep from './components/steps/FanStep.vue'
import ToolboardStep from './components/steps/ToolboardStep.vue'
import TmcStep from './components/steps/TmcStep.vue'
import ProbeStep from './components/steps/ProbeStep.vue'
import BedMeshStep from './components/steps/BedMeshStep.vue'
import InputShaperStep from './components/steps/InputShaperStep.vue'
import DisplayStep from './components/steps/DisplayStep.vue'
import TempSensorStep from './components/steps/TempSensorStep.vue'
import ExportStep from './components/steps/ExportStep.vue'

const { locale, t, toggleLocale } = useI18n()

provide('t', t)
provide('locale', locale)

const currentStep = ref(0)
const slideDirection = ref('slide-right')

const steps = [
  { id: 0, nameKey: 'stepWelcome', icon: 'HomeFilled', phase: 'basic', component: 'WelcomeStep' },
  { id: 1, nameKey: 'stepMcu', icon: 'Connection', phase: 'basic', component: 'McuStep' },
  { id: 2, nameKey: 'stepKinematics', icon: 'Printer', phase: 'basic', component: 'KinematicsStep' },
  { id: 3, nameKey: 'stepMotion', icon: 'Odometer', phase: 'basic', component: 'MotionStep' },
  { id: 4, nameKey: 'stepStepperX', icon: 'Right', phase: 'basic', component: 'StepperConfigStep', props: { axis: 'x' } },
  { id: 5, nameKey: 'stepStepperY', icon: 'Top', phase: 'basic', component: 'StepperConfigStep', props: { axis: 'y' } },
  { id: 6, nameKey: 'stepStepperZ', icon: 'Bottom', phase: 'basic', component: 'StepperConfigStep', props: { axis: 'z' } },
  { id: 7, nameKey: 'stepExtruder', icon: 'MagicStick', phase: 'basic', component: 'ExtruderStep' },
  { id: 8, nameKey: 'stepHeaterBed', icon: 'Sunny', phase: 'basic', component: 'HeaterBedStep' },
  { id: 9, nameKey: 'stepFan', icon: 'ColdDrink', phase: 'basic', component: 'FanStep' },
  { id: 10, nameKey: 'stepTmc', icon: 'Cpu', phase: 'advanced', component: 'TmcStep' },
  { id: 11, nameKey: 'stepToolboard', icon: 'Connection', phase: 'advanced', component: 'ToolboardStep' },
  { id: 12, nameKey: 'stepProbe', icon: 'Aim', phase: 'advanced', component: 'ProbeStep' },
  { id: 13, nameKey: 'stepBedMesh', icon: 'Grid', phase: 'advanced', component: 'BedMeshStep' },
  { id: 14, nameKey: 'stepInputShaper', icon: 'TrendCharts', phase: 'advanced', component: 'InputShaperStep' },
  { id: 15, nameKey: 'stepDisplay', icon: 'Monitor', phase: 'advanced', component: 'DisplayStep' },
  { id: 16, nameKey: 'stepTempSensor', icon: 'Sunny', phase: 'advanced', component: 'TempSensorStep' },
  { id: 17, nameKey: 'stepExport', icon: 'Download', phase: 'advanced', component: 'ExportStep' }
]

const translatedSteps = computed(() => {
  return steps.map(step => ({
    ...step,
    name: t(step.nameKey)
  }))
})

const componentMap = {
  WelcomeStep,
  McuStep,
  KinematicsStep,
  MotionStep,
  StepperConfigStep,
  ExtruderStep,
  HeaterBedStep,
  FanStep,
  TmcStep,
  ToolboardStep,
  ProbeStep,
  BedMeshStep,
  InputShaperStep,
  DisplayStep,
  TempSensorStep,
  ExportStep
}

const config = ref({
  mcu: {
    serial: '',
    canbus_uuid: '',
    canbus_interface: 'can0'
  },
  printer: {
    kinematics: 'cartesian',
    size_x: 235,
    size_y: 235,
    size_z: 250,
    max_velocity: 300,
    max_accel: 3000,
    max_z_velocity: 5,
    max_z_accel: 100,
    square_corner_velocity: 5.0
  },
  steppers: {
    stepper_x: {
      step_pin: '',
      dir_pin: '',
      enable_pin: '',
      microsteps: 16,
      rotation_distance: 40,
      endstop_pin: '',
      position_endstop: 0,
      position_max: 235,
      homing_speed: 50
    },
    stepper_y: {
      step_pin: '',
      dir_pin: '',
      enable_pin: '',
      microsteps: 16,
      rotation_distance: 40,
      endstop_pin: '',
      position_endstop: 0,
      position_max: 235,
      homing_speed: 50
    },
    stepper_z: {
      step_pin: '',
      dir_pin: '',
      enable_pin: '',
      microsteps: 16,
      rotation_distance: 8,
      endstop_pin: '',
      position_endstop: 0,
      position_max: 250,
      homing_speed: 5
    }
  },
  has_extruder: true,
  extruder: {
    step_pin: '',
    dir_pin: '',
    enable_pin: '',
    microsteps: 16,
    rotation_distance: 33.5,
    nozzle_diameter: 0.4,
    filament_diameter: 1.75,
    heater_pin: '',
    sensor_type: 'EPCOS 100K B57560G104F',
    sensor_pin: '',
    control: 'pid',
    pid_Kp: 22.2,
    pid_Ki: 1.08,
    pid_Kd: 114,
    min_temp: 0,
    max_temp: 250,
    min_extrude_temp: 170,
    pressure_advance: 0,
    pressure_advance_smooth_time: 0.04,
    max_extrude_only_distance: 50
  },
  heater_bed: {
    heater_pin: '',
    sensor_type: 'EPCOS 100K B57560G104F',
    sensor_pin: '',
    control: 'pid',
    pid_Kp: 54.027,
    pid_Ki: 0.77,
    pid_Kd: 948.182,
    min_temp: 0,
    max_temp: 130
  },
  fan: {
    pin: '',
    max_power: 1.0,
    kick_start_time: 0.1
  },
  tmc: {},
  toolboards: [],
  probe: null,
  bed_mesh: null,
  input_shaper: null,
  display: null,
  temperature_sensors: [],
  safe_z_home: null,
  bed_screws: null
})

const currentStepComponent = computed(() => {
  const step = steps[currentStep.value]
  return componentMap[step.component]
})

function updateConfig(updates) {
  Object.assign(config.value, updates)
}

function nextStep() {
  if (currentStep.value < steps.length - 1) {
    slideDirection.value = 'slide-right'
    currentStep.value++
  }
}

function prevStep() {
  if (currentStep.value > 0) {
    slideDirection.value = 'slide-left'
    currentStep.value--
  }
}

function goToStep(stepId) {
  slideDirection.value = stepId > currentStep.value ? 'slide-right' : 'slide-left'
  currentStep.value = stepId
}
</script>

<style scoped>
.app-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-color);
}

.app-header {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: white;
  padding: 0 24px;
  height: 60px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 100;
}

.header-content {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-section h1 {
  font-size: 18px;
  font-weight: 600;
  margin: 0;
  background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions .el-button {
  color: rgba(255, 255, 255, 0.8) !important;
}

.header-actions .el-button:hover {
  color: white !important;
}

.app-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  background: white;
  border-right: 1px solid var(--border-color);
  overflow-y: auto;
  flex-shrink: 0;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  min-width: 0;
}

.preview-panel {
  width: 380px;
  background: white;
  border-left: 1px solid var(--border-color);
  overflow-y: auto;
  flex-shrink: 0;
}

@media (max-width: 1200px) {
  .preview-panel {
    display: none;
  }
}

@media (max-width: 768px) {
  .sidebar {
    display: none;
  }
  
  .main-content {
    padding: 16px;
  }
}
</style>
