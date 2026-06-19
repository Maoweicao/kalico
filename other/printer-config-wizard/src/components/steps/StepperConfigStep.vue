<template>
  <div class="step-card">
    <h2 class="step-title">{{ axisName }}轴步进电机配置</h2>
    <p class="step-description">
      配置{{ axisName }}轴的步进电机引脚、运动参数和限位开关。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>步进电机基础知识：</strong><br>
        • <strong>STEP引脚</strong>：控制电机步进脉冲<br>
        • <strong>DIR引脚</strong>：控制电机旋转方向（如果方向反了，加!前缀）<br>
        • <strong>EN引脚</strong>：使能电机（大多数驱动板低电平使能，需要!前缀）<br>
        • <strong>限位开关</strong>：检测轴的起始位置
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Cpu /></el-icon>
        电机引脚配置
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              STEP 引脚
              <el-tooltip content="步进脉冲引脚" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input 
              v-model="stepper.step_pin" 
              placeholder="PB13"
              @input="updateStepper"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              DIR 引脚
              <el-tooltip content="方向引脚，加!可反转方向" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input 
              v-model="stepper.dir_pin" 
              placeholder="!PB12"
              @input="updateStepper"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              EN 引脚
              <el-tooltip content="使能引脚，通常需要!前缀" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input 
              v-model="stepper.enable_pin" 
              placeholder="!PB14"
              @input="updateStepper"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Setting /></el-icon>
        电机参数
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              微步数
              <el-tooltip content="推荐使用16" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="stepper.microsteps" @change="updateStepper">
              <el-option :value="1" label="1 (全步)" />
              <el-option :value="2" label="2" />
              <el-option :value="4" label="4" />
              <el-option :value="8" label="8" />
              <el-option :value="16" label="16 (推荐)" />
              <el-option :value="32" label="32" />
              <el-option :value="64" label="64" />
              <el-option :value="128" label="128" />
              <el-option :value="256" label="256" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              旋转距离 (mm)
              <el-tooltip content="电机转一圈移动的距离" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.rotation_distance" 
              :min="0.1" 
              :max="1000" 
              :step="0.1"
              :precision="1"
              @change="updateStepper"
              style="width: 100%"
            />
            <div class="param-hint">{{ rotationDistanceHint }}</div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              每圈步数
              <el-tooltip content="1.8度电机=200，0.9度电机=400" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="stepper.full_steps_per_rotation" @change="updateStepper">
              <el-option :value="200" label="200 (1.8度，常见)" />
              <el-option :value="400" label="400 (0.9度，精确)" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Aim /></el-icon>
        限位开关配置
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              限位引脚
              <el-tooltip content="^启用上拉，!反转信号" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input 
              v-model="stepper.endstop_pin" 
              placeholder="^PC1"
              @input="updateStepper"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              限位位置 (mm)
              <el-tooltip content="限位触发时喷嘴的位置" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.position_endstop" 
              :min="-100" 
              :max="500"
              :step="0.1"
              :precision="1"
              @change="updateStepper"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              最大位置 (mm)
              <el-tooltip content="轴的最大行程" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.position_max" 
              :min="0" 
              :max="1000"
              :step="1"
              @change="updateStepper"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><VideoPlay /></el-icon>
        归位参数
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              归位速度 (mm/s)
              <el-tooltip content="第一次归位的速度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.homing_speed" 
              :min="1" 
              :max="200"
              :step="5"
              @change="updateStepper"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              回退距离 (mm)
              <el-tooltip content="触发限位后回退的距离" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.homing_retract_dist" 
              :min="0" 
              :max="20"
              :step="0.5"
              :precision="1"
              @change="updateStepper"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              二次归位速度 (mm/s)
              <el-tooltip content="第二次归位的速度，通常较慢" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="stepper.second_homing_speed" 
              :min="1" 
              :max="100"
              :step="1"
              @change="updateStepper"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="step-actions">
      <el-button @click="$emit('prev')">
        <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
        上一步
      </el-button>
      <el-button type="primary" @click="$emit('next')">
        下一步
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { 
  InfoFilled, QuestionFilled, Cpu, Setting, Aim, 
  VideoPlay, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object,
  axis: {
    type: String,
    default: 'x'
  }
})

const emit = defineEmits(['update', 'next', 'prev'])

const axisNames = {
  x: 'X',
  y: 'Y',
  z: 'Z'
}

const axisName = computed(() => axisNames[props.axis] || props.axis)

const stepperKey = computed(() => `stepper_${props.axis}`)

const defaultStepper = {
  step_pin: '',
  dir_pin: '',
  enable_pin: '',
  microsteps: 16,
  rotation_distance: props.axis === 'z' ? 8 : 40,
  full_steps_per_rotation: 200,
  endstop_pin: '',
  position_endstop: 0,
  position_max: props.axis === 'z' ? 250 : 235,
  homing_speed: props.axis === 'z' ? 5 : 50,
  homing_retract_dist: 5,
  second_homing_speed: props.axis === 'z' ? 2 : 5
}

const stepper = ref({ ...defaultStepper })

const rotationDistanceHint = computed(() => {
  if (props.axis === 'z') {
    return 'T8丝杆=8mm，T10丝杆=10mm'
  }
  return 'GT2皮带20齿: 20×2=40mm'
})

onMounted(() => {
  if (props.config.steppers?.[stepperKey.value]) {
    stepper.value = { ...defaultStepper, ...props.config.steppers[stepperKey.value] }
  }
})

watch(() => props.axis, () => {
  if (props.config.steppers?.[stepperKey.value]) {
    stepper.value = { ...defaultStepper, ...props.config.steppers[stepperKey.value] }
  } else {
    stepper.value = { ...defaultStepper }
  }
})

function updateStepper() {
  emit('update', {
    steppers: {
      ...props.config.steppers,
      [stepperKey.value]: { ...stepper.value }
    }
  })
}
</script>

<style scoped>
.param-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}
</style>
