<template>
  <div class="step-card">
    <h2 class="step-title">热床配置</h2>
    <p class="step-description">
      热床用于加热打印平台，提高耗材附着力。如果您的打印机没有热床，可以跳过此步。
    </p>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Sunny /></el-icon>
        热床开关
      </div>
      
      <el-switch 
        v-model="hasHeaterBed" 
        active-text="有热床" 
        inactive-text="无热床"
        @change="update"
      />
    </div>
    
    <div v-if="hasHeaterBed">
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Cpu /></el-icon>
          引脚配置
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                加热引脚
                <el-tooltip content="热床加热控制引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="heater_bed.heater_pin" placeholder="PD2" @input="updateBed" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                传感器类型
                <el-tooltip content="热床热敏电阻型号" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="heater_bed.sensor_type" @change="updateBed" filterable>
                <el-option label="EPCOS 100K (常见)" value="EPCOS 100K B57560G104F" />
                <el-option label="ATC Semitec 104GT-2" value="ATC Semitec 104GT-2" />
                <el-option label="Generic 3950" value="Generic 3950" />
                <el-option label="Honeywell 100K" value="Honeywell 100K 135-104LAG-J01" />
                <el-option label="PT1000" value="PT1000" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                传感器引脚
                <el-tooltip content="温度传感器ADC引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="heater_bed.sensor_pin" placeholder="PC1" @input="updateBed" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><TrendCharts /></el-icon>
          温控配置
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                控制方式
                <el-tooltip content="PID精度高，watermark简单" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="heater_bed.control" @change="updateBed">
                <el-option label="PID (推荐)" value="pid" />
                <el-option label="Watermark" value="watermark" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                最低温度 (°C)
                <el-tooltip content="低于此温度报错" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="heater_bed.min_temp" 
                :min="0" 
                :max="50"
                @change="updateBed"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                最高温度 (°C)
                <el-tooltip content="热床安全温度上限" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="heater_bed.max_temp" 
                :min="60" 
                :max="150"
                @change="updateBed"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <div v-if="heater_bed.control === 'pid'" class="pid-section">
          <el-alert type="info" :closable="false" show-icon>
            <template #title>
              PID参数需要校准。运行：<code>PID_CALIBRATE HEATER=heater_bed TARGET=60</code>
            </template>
          </el-alert>
          <el-row :gutter="16" style="margin-top: 12px;">
            <el-col :span="8">
              <el-form-item label="Kp">
                <el-input-number 
                  v-model="heater_bed.pid_Kp" 
                  :min="0" 
                  :max="200"
                  :step="0.1"
                  :precision="2"
                  @change="updateBed"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Ki">
                <el-input-number 
                  v-model="heater_bed.pid_Ki" 
                  :min="0" 
                  :max="10"
                  :step="0.01"
                  :precision="3"
                  @change="updateBed"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="Kd">
                <el-input-number 
                  v-model="heater_bed.pid_Kd" 
                  :min="0" 
                  :max="2000"
                  :step="1"
                  :precision="1"
                  @change="updateBed"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
      </div>
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
import { ref, onMounted } from 'vue'
import { 
  InfoFilled, QuestionFilled, Cpu, Sunny, 
  TrendCharts, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasHeaterBed = ref(true)

const defaultBed = {
  heater_pin: '',
  sensor_type: 'EPCOS 100K B57560G104F',
  sensor_pin: '',
  control: 'pid',
  pid_Kp: 54.027,
  pid_Ki: 0.77,
  pid_Kd: 948.182,
  min_temp: 0,
  max_temp: 130
}

const heater_bed = ref({ ...defaultBed })

onMounted(() => {
  if (props.config.heater_bed && props.config.heater_bed.heater_pin) {
    heater_bed.value = { ...defaultBed, ...props.config.heater_bed }
    hasHeaterBed.value = true
  } else {
    hasHeaterBed.value = false
  }
})

function update() {
  if (!hasHeaterBed.value) {
    emit('update', { heater_bed: null })
  } else {
    updateBed()
  }
}

function updateBed() {
  emit('update', {
    heater_bed: { ...heater_bed.value }
  })
}
</script>

<style scoped>
.pid-section {
  margin-top: 12px;
}

code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
}
</style>
