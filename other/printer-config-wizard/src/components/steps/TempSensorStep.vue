<template>
  <div class="step-card">
    <h2 class="step-title">温度传感器</h2>
    <p class="step-description">
      添加额外的温度传感器，用于监控机箱温度、主板温度等。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>常见用途：</strong><br>
        • 机箱温度监控<br>
        • 主板温度监控<br>
        • 耗材干燥箱温度<br>
        • 水冷系统温度
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Sunny /></el-icon>
        是否添加传感器
      </div>
      
      <el-switch 
        v-model="hasSensors" 
        active-text="添加传感器" 
        inactive-text="不需要"
        @change="onToggle"
      />
    </div>
    
    <div v-if="hasSensors">
      <div v-for="(sensor, index) in sensors" :key="index" class="form-section sensor-section">
        <div class="form-section-title">
          <el-icon><Sunny /></el-icon>
          传感器 {{ index + 1 }}
          <el-button 
            type="danger" 
            text 
            size="small" 
            @click="removeSensor(index)"
            style="margin-left: auto;"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
        
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item>
              <template #label>
                名称
                <el-tooltip content="传感器的唯一名称" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="sensor.name" 
                placeholder="chamber"
                @input="update"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                传感器类型
                <el-tooltip content="热敏电阻型号" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="sensor.sensor_type" @change="update" filterable>
                <el-option label="EPCOS 100K" value="EPCOS 100K B57560G104F" />
                <el-option label="Generic 3950" value="Generic 3950" />
                <el-option label="DS18B20" value="DS18B20" />
                <el-option label="BME280" value="BME280" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                传感器引脚
                <el-tooltip content="ADC引脚或数字引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="sensor.sensor_pin" 
                placeholder="PC2"
                @input="update"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                最高温度 (°C)
                <el-tooltip content="报警温度上限" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="sensor.max_temp" 
                :min="0" 
                :max="200"
                @change="update"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <el-button @click="addSensor" style="width: 100%;">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        添加传感器
      </el-button>
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
  InfoFilled, QuestionFilled, Delete, 
  Plus, ArrowLeft, ArrowRight, Sunny
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasSensors = ref(false)

const defaultSensor = {
  name: '',
  sensor_type: 'Generic 3950',
  sensor_pin: '',
  min_temp: 0,
  max_temp: 100
}

const sensors = ref([])

onMounted(() => {
  if (props.config.temperature_sensors && props.config.temperature_sensors.length > 0) {
    hasSensors.value = true
    sensors.value = props.config.temperature_sensors.map(s => ({ ...defaultSensor, ...s }))
  }
})

function onToggle() {
  if (!hasSensors.value) {
    emit('update', { temperature_sensors: [] })
  } else {
    if (sensors.value.length === 0) {
      addSensor()
    }
  }
}

function addSensor() {
  sensors.value.push({ ...defaultSensor })
  update()
}

function removeSensor(index) {
  sensors.value.splice(index, 1)
  if (sensors.value.length === 0) {
    hasSensors.value = false
  }
  update()
}

function update() {
  emit('update', {
    temperature_sensors: sensors.value.filter(s => s.name)
  })
}
</script>

<style scoped>
.sensor-section {
  border-left: 3px solid var(--primary-color);
  padding-left: 16px;
}
</style>
