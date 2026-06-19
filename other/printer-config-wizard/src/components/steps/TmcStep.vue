<template>
  <div class="step-card">
    <h2 class="step-title">TMC 驱动配置</h2>
    <p class="step-description">
      TMC步进驱动芯片可以大幅降低电机噪音、提高精度。如果您的驱动板不支持TMC，可以跳过此步。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>常见TMC驱动：</strong><br>
        • <strong>TMC2209</strong>：最常用，UART接口，支持无传感器归位<br>
        • <strong>TMC2208</strong>：较老型号，UART接口<br>
        • <strong>TMC2130</strong>：SPI接口，功能丰富<br>
        • <strong>TMC5160</strong>：高性能，大电流<br>
        • <strong>TMC2240</strong>：新一代，支持UART/SPI
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Cpu /></el-icon>
        驱动类型选择
      </div>
      
      <el-radio-group v-model="driverType" class="driver-type-select">
        <el-radio-button label="tmc2209">TMC2209</el-radio-button>
        <el-radio-button label="tmc2208">TMC2208</el-radio-button>
        <el-radio-button label="tmc2130">TMC2130</el-radio-button>
        <el-radio-button label="tmc5160">TMC5160</el-radio-button>
        <el-radio-button label="tmc2240">TMC2240</el-radio-button>
      </el-radio-group>
    </div>
    
    <div v-for="stepperName in stepperNames" :key="stepperName" class="form-section">
      <div class="form-section-title">
        <el-icon><Setting /></el-icon>
        {{ stepperLabels[stepperName] }} 配置
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              {{ isSpiDriver ? 'SPI引脚' : 'UART引脚' }}
              <el-tooltip :content="isSpiDriver ? 'SPI通信引脚' : 'UART通信引脚'" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input 
              v-model="tmcConfigs[stepperName][isSpiDriver ? 'spi_pin' : 'uart_pin']" 
              :placeholder="isSpiDriver ? 'PA4' : 'PC11'"
              @input="updateTmc(stepperName)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              运行电流 (A)
              <el-tooltip content="电机运行时的电流，建议不超过额定值的80%" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="tmcConfigs[stepperName].run_current" 
              :min="0.1" 
              :max="3"
              :step="0.1"
              :precision="2"
              @change="updateTmc(stepperName)"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              静音模式阈值
              <el-tooltip content="0=性能优先，999999=静音优先" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="tmcConfigs[stepperName].stealthchop_threshold" @change="updateTmc(stepperName)">
              <el-option :value="0" label="关闭 (性能优先)" />
              <el-option :value="999999" label="始终静音" />
              <el-option :value="100" label="100mm/s以下静音" />
              <el-option :value="200" label="200mm/s以下静音" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              插值
              <el-tooltip content="启用256微步插值，推荐开启" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-switch 
              v-model="tmcConfigs[stepperName].interpolate" 
              @change="updateTmc(stepperName)"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              采样电阻 (Ω)
              <el-tooltip content="TMC2209=0.110，TMC5160=0.075" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="tmcConfigs[stepperName].sense_resistor" @change="updateTmc(stepperName)">
              <el-option :value="0.110" label="0.110 (TMC2209/2208)" />
              <el-option :value="0.075" label="0.075 (TMC5160)" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col v-if="driverType === 'tmc2209'" :span="8">
          <el-form-item>
            <template #label>
              StallGuard阈值
              <el-tooltip content="无传感器归位灵敏度，0-255" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="tmcConfigs[stepperName].driver_SGTHRS" 
              :min="0" 
              :max="255"
              @change="updateTmc(stepperName)"
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
import { ref, computed, onMounted } from 'vue'
import { 
  InfoFilled, QuestionFilled, Cpu, Setting, 
  ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const driverType = ref('tmc2209')

const stepperNames = ['stepper_x', 'stepper_y', 'stepper_z', 'extruder']

const stepperLabels = {
  stepper_x: 'X轴',
  stepper_y: 'Y轴',
  stepper_z: 'Z轴',
  extruder: '挤出机'
}

const isSpiDriver = computed(() => {
  return ['tmc2130', 'tmc5160', 'tmc2240'].includes(driverType.value)
})

const defaultTmc = {
  driver_type: 'tmc2209',
  uart_pin: '',
  spi_pin: '',
  run_current: 0.8,
  interpolate: true,
  stealthchop_threshold: 0,
  sense_resistor: 0.110,
  driver_SGTHRS: 100
}

const tmcConfigs = ref({
  stepper_x: { ...defaultTmc },
  stepper_y: { ...defaultTmc },
  stepper_z: { ...defaultTmc },
  extruder: { ...defaultTmc, run_current: 0.6 }
})

onMounted(() => {
  if (props.config.tmc) {
    for (const name of stepperNames) {
      if (props.config.tmc[name]) {
        tmcConfigs.value[name] = { ...defaultTmc, ...props.config.tmc[name] }
        if (props.config.tmc[name].driver_type) {
          driverType.value = props.config.tmc[name].driver_type
        }
      }
    }
  }
})

function updateTmc(stepperName) {
  const configs = {}
  for (const name of stepperNames) {
    configs[name] = {
      ...tmcConfigs.value[name],
      driver_type: driverType.value
    }
  }
  emit('update', { tmc: configs })
}
</script>

<style scoped>
.driver-type-select {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
