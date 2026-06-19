<template>
  <div class="step-card">
    <h2 class="step-title">风扇配置</h2>
    <p class="step-description">
      配置打印机的冷却风扇。零件冷却风扇用于在打印过程中冷却耗材，提高打印质量。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>风扇类型说明：</strong><br>
        • <strong>零件冷却风扇 [fan]</strong>：冷却打印件，由切片软件控制<br>
        • <strong>热端风扇 [heater_fan]</strong>：冷却热端散热片，加热时自动开启<br>
        • <strong>控制器风扇 [controller_fan]</strong>：冷却主板，活动时自动开启
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><ColdDrink /></el-icon>
        零件冷却风扇
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              风扇引脚
              <el-tooltip content="风扇控制引脚" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input v-model="fan.pin" placeholder="PC6" @input="update" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              最大功率
              <el-tooltip content="风扇最大功率百分比" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-slider 
              v-model="fan.max_power" 
              :min="0.1" 
              :max="1" 
              :step="0.05"
              :format-tooltip="v => `${Math.round(v * 100)}%`"
              @change="update"
            />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              启动时间 (s)
              <el-tooltip content="风扇启动时全速运行帮助启动" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="fan.kick_start_time" 
              :min="0" 
              :max="1"
              :step="0.05"
              :precision="2"
              @change="update"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Setting /></el-icon>
        热端风扇 (可选)
      </div>
      
      <el-switch 
        v-model="hasHeaterFan" 
        active-text="添加热端风扇" 
        inactive-text="不需要"
        @change="updateHeaterFan"
      />
      
      <div v-if="hasHeaterFan" style="margin-top: 16px;">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                风扇引脚
                <el-tooltip content="热端散热风扇引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="heaterFan.pin" placeholder="PC7" @input="updateHeaterFan" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <template #label>
                关联加热器
                <el-tooltip content="哪个加热器开启时风扇运转" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="heaterFan.heater" @change="updateHeaterFan" multiple>
                <el-option label="extruder" value="extruder" />
                <el-option label="heater_bed" value="heater_bed" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
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
  InfoFilled, QuestionFilled, Setting, 
  ArrowLeft, ArrowRight, ColdDrink
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasHeaterFan = ref(false)

const defaultFan = {
  pin: '',
  max_power: 1.0,
  kick_start_time: 0.1
}

const fan = ref({ ...defaultFan })

const heaterFan = ref({
  pin: '',
  heater: ['extruder']
})

onMounted(() => {
  if (props.config.fan) {
    fan.value = { ...defaultFan, ...props.config.fan }
  }
})

function update() {
  emit('update', {
    fan: { ...fan.value }
  })
}

function updateHeaterFan() {
  if (hasHeaterFan.value) {
    emit('update', {
      heater_fan: {
        pin: heaterFan.value.pin,
        heater: heaterFan.value.heater.join(',')
      }
    })
  } else {
    emit('update', { heater_fan: null })
  }
}
</script>

<style scoped>
.el-slider {
  --el-slider-main-bg-color: var(--primary-color);
}
</style>
