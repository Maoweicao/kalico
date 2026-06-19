<template>
  <div class="step-card">
    <h2 class="step-title">挤出机配置</h2>
    <p class="step-description">
      挤出机负责将耗材送入热端融化并挤出。需要配置电机、加热器和温度传感器。
    </p>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><MagicStick /></el-icon>
        是否有挤出机
      </div>
      
      <el-switch 
        v-model="hasExtruder" 
        active-text="有挤出机" 
        inactive-text="无挤出机"
        @change="onToggle"
      />
      <div class="param-hint" style="margin-top: 8px;">
        如果使用工具板上的挤出机，可以在此跳过主板挤出机配置
      </div>
    </div>
    
    <div v-if="hasExtruder">
      <div class="info-box">
        <el-icon><InfoFilled /></el-icon>
        <p>
          <strong>挤出机组成：</strong><br>
          • <strong>步进电机</strong>：驱动齿轮推送耗材<br>
          • <strong>加热棒</strong>：加热热端融化耗材<br>
          • <strong>热敏电阻</strong>：检测热端温度<br>
          • <strong>喷嘴</strong>：控制挤出直径
        </p>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Cpu /></el-icon>
          电机引脚
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
            <el-input v-model="extruder.step_pin" placeholder="PB3" @input="update" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              DIR 引脚
              <el-tooltip content="方向引脚，加!可反转" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input v-model="extruder.dir_pin" placeholder="!PB4" @input="update" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              EN 引脚
              <el-tooltip content="使能引脚" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input v-model="extruder.enable_pin" placeholder="!PD1" @input="update" />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Setting /></el-icon>
        挤出参数
      </div>
      
      <el-row :gutter="16">
        <el-col :span="6">
          <el-form-item>
            <template #label>
              微步数
              <el-tooltip content="推荐16" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="extruder.microsteps" @change="update">
              <el-option :value="16" label="16 (推荐)" />
              <el-option :value="32" label="32" />
              <el-option :value="64" label="64" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              旋转距离 (mm)
              <el-tooltip content="电机转一圈挤出的耗材长度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="extruder.rotation_distance" 
              :min="1" 
              :max="100"
              :step="0.1"
              :precision="1"
              @change="update"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              喷嘴直径 (mm)
              <el-tooltip content="安装的喷嘴直径" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="extruder.nozzle_diameter" @change="update">
              <el-option :value="0.2" label="0.2mm" />
              <el-option :value="0.3" label="0.3mm" />
              <el-option :value="0.4" label="0.4mm (常见)" />
              <el-option :value="0.5" label="0.5mm" />
              <el-option :value="0.6" label="0.6mm" />
              <el-option :value="0.8" label="0.8mm" />
              <el-option :value="1.0" label="1.0mm" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              耗材直径 (mm)
              <el-tooltip content="使用的耗材直径" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="extruder.filament_diameter" @change="update">
              <el-option :value="1.75" label="1.75mm (常见)" />
              <el-option :value="2.85" label="2.85mm" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Sunny /></el-icon>
        加热器配置
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              加热引脚
              <el-tooltip content="加热棒控制引脚" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input v-model="extruder.heater_pin" placeholder="PB4" @input="update" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              传感器类型
              <el-tooltip content="热敏电阻型号" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="extruder.sensor_type" @change="update" filterable>
              <el-option label="EPCOS 100K (常见)" value="EPCOS 100K B57560G104F" />
              <el-option label="ATC Semitec 104GT-2" value="ATC Semitec 104GT-2" />
              <el-option label="Generic 3950" value="Generic 3950" />
              <el-option label="Honeywell 100K" value="Honeywell 100K 135-104LAG-J01" />
              <el-option label="PT1000" value="PT1000" />
              <el-option label="MAX6675 (热电偶)" value="MAX6675" />
              <el-option label="MAX31855 (热电偶)" value="MAX31855" />
              <el-option label="MAX31856 (热电偶)" value="MAX31856" />
              <el-option label="MAX31865 (RTD)" value="MAX31865" />
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
            <el-input v-model="extruder.sensor_pin" placeholder="PC0" @input="update" />
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
        <el-col :span="6">
          <el-form-item>
            <template #label>
              控制方式
              <el-tooltip content="PID精度高，watermark简单" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-select v-model="extruder.control" @change="update">
              <el-option label="PID (推荐)" value="pid" />
              <el-option label="Watermark" value="watermark" />
              <el-option label="MPC" value="mpc" />
            </el-select>
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              最低温度 (°C)
              <el-tooltip content="低于此温度报错" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="extruder.min_temp" 
              :min="0" 
              :max="50"
              @change="update"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              最高温度 (°C)
              <el-tooltip content="安全温度上限" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="extruder.max_temp" 
              :min="200" 
              :max="500"
              @change="update"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
        <el-col :span="6">
          <el-form-item>
            <template #label>
              最低挤出温度 (°C)
              <el-tooltip content="允许挤出的最低温度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="extruder.min_extrude_temp" 
              :min="0" 
              :max="250"
              @change="update"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <div v-if="extruder.control === 'pid'" class="pid-section">
        <el-alert type="info" :closable="false" show-icon>
          <template #title>
            PID参数需要校准。连接打印机后运行：<code>PID_CALIBRATE HEATER=extruder TARGET=200</code>
          </template>
        </el-alert>
        <el-row :gutter="16" style="margin-top: 12px;">
          <el-col :span="8">
            <el-form-item label="Kp">
              <el-input-number 
                v-model="extruder.pid_Kp" 
                :min="0" 
                :max="100"
                :step="0.1"
                :precision="2"
                @change="update"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Ki">
              <el-input-number 
                v-model="extruder.pid_Ki" 
                :min="0" 
                :max="10"
                :step="0.01"
                :precision="3"
                @change="update"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="Kd">
              <el-input-number 
                v-model="extruder.pid_Kd" 
                :min="0" 
                :max="500"
                :step="1"
                :precision="1"
                @change="update"
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
  InfoFilled, QuestionFilled, Cpu, Setting, Sunny, 
  TrendCharts, ArrowLeft, ArrowRight, MagicStick
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasExtruder = ref(true)

const defaultExtruder = {
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
  max_extrude_only_distance: 50
}

const extruder = ref({ ...defaultExtruder })

onMounted(() => {
  if (props.config.has_extruder === false) {
    hasExtruder.value = false
  }
  if (props.config.extruder) {
    extruder.value = { ...defaultExtruder, ...props.config.extruder }
  }
})

function onToggle() {
  emit('update', { has_extruder: hasExtruder.value })
  if (hasExtruder.value) {
    update()
  }
}

function update() {
  emit('update', {
    has_extruder: hasExtruder.value,
    extruder: { ...extruder.value }
  })
}
</script>

<style scoped>
.pid-section {
  margin-top: 12px;
}

.el-alert {
  margin-bottom: 12px;
}

code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
}
</style>
