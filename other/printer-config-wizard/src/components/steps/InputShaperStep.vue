<template>
  <div class="step-card">
    <h2 class="step-title">输入整形</h2>
    <p class="step-description">
      输入整形用于补偿打印机的共振，减少振纹，提高打印质量。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>什么是输入整形？</strong><br>
        打印机在高速运动时会产生共振，导致打印表面出现振纹。<br>
        输入整形通过在运动指令中加入反向振动来抵消共振。<br>
        <strong>校准方法：</strong>运行 <code>SHAPER_CALIBRATE</code> 自动测量
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><TrendCharts /></el-icon>
        是否启用
      </div>
      
      <el-switch 
        v-model="hasInputShaper" 
        active-text="启用输入整形" 
        inactive-text="不使用"
        @change="onToggle"
      />
    </div>
    
    <div v-if="hasInputShaper">
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Setting /></el-icon>
          整形器类型
        </div>
        
        <div class="shaper-types">
          <div 
            v-for="shaper in shaperTypes" 
            :key="shaper.value"
            class="shaper-option"
            :class="{ active: shaperType === shaper.value }"
            @click="selectShaper(shaper.value)"
          >
            <div class="shaper-name">{{ shaper.label }}</div>
            <div class="shaper-desc">{{ shaper.desc }}</div>
          </div>
        </div>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Odometer /></el-icon>
          共振频率
        </div>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                X轴频率 (Hz)
                <el-tooltip content="X轴的共振频率，通过测量获得" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="shaperFreqX" 
                :min="0" 
                :max="200"
                :step="0.5"
                :precision="1"
                @change="update"
                style="width: 100%"
              />
              <div class="param-hint">运行 SHAPER_CALIBRATE AXIS=X 测量</div>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <template #label>
                Y轴频率 (Hz)
                <el-tooltip content="Y轴的共振频率，通过测量获得" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="shaperFreqY" 
                :min="0" 
                :max="200"
                :step="0.5"
                :precision="1"
                @change="update"
                style="width: 100%"
              />
              <div class="param-hint">运行 SHAPER_CALIBRATE AXIS=Y 测量</div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><InfoFilled /></el-icon>
          校准说明
        </div>
        
        <div class="info-box">
          <el-icon><InfoFilled /></el-icon>
          <p>
            <strong>自动校准步骤：</strong><br>
            1. 连接打印机<br>
            2. 运行 <code>SHAPER_CALIBRATE</code><br>
            3. 系统会自动测量并设置最佳参数<br>
            4. 运行 <code>SAVE_CONFIG</code> 保存配置
          </p>
        </div>
        
        <div class="warning-box">
          <el-icon><Warning /></el-icon>
          <p>
            <strong>手动设置注意事项：</strong><br>
            • 频率值必须通过实际测量获得<br>
            • 错误的频率值会降低打印质量<br>
            • 建议使用自动校准
          </p>
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
  InfoFilled, QuestionFilled, TrendCharts, Setting, 
  Odometer, Warning, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasInputShaper = ref(false)
const shaperType = ref('mzv')
const shaperFreqX = ref(50)
const shaperFreqY = ref(40)

const shaperTypes = [
  { value: 'zv', label: 'ZV', desc: '最简单，效果一般' },
  { value: 'mzv', label: 'MZV', desc: '推荐，平衡性能和效果' },
  { value: 'zvd', label: 'ZVD', desc: '更强的抑制效果' },
  { value: 'ei', label: 'EI', desc: '更强调抑振' },
  { value: '2hump_ei', label: '2HUMP_EI', desc: '双驼峰，适合复杂共振' },
  { value: '3hump_ei', label: '3HUMP_EI', desc: '三驼峰，最强抑制' }
]

onMounted(() => {
  if (props.config.input_shaper) {
    hasInputShaper.value = true
    shaperType.value = props.config.input_shaper.shaper_type || 'mzv'
    shaperFreqX.value = props.config.input_shaper.shaper_freq_x || 50
    shaperFreqY.value = props.config.input_shaper.shaper_freq_y || 40
  }
})

function onToggle() {
  if (!hasInputShaper.value) {
    emit('update', { input_shaper: null })
  } else {
    update()
  }
}

function selectShaper(value) {
  shaperType.value = value
  update()
}

function update() {
  emit('update', {
    input_shaper: {
      shaper_type: shaperType.value,
      shaper_freq_x: shaperFreqX.value,
      shaper_freq_y: shaperFreqY.value
    }
  })
}
</script>

<style scoped>
.shaper-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.shaper-option {
  border: 2px solid var(--border-color);
  border-radius: var(--radius-medium);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.shaper-option:hover {
  border-color: var(--primary-light);
}

.shaper-option.active {
  border-color: var(--primary-color);
  background: #ecf5ff;
}

.shaper-name {
  font-weight: 600;
  font-size: 16px;
  margin-bottom: 4px;
}

.shaper-desc {
  font-size: 12px;
  color: var(--text-secondary);
}

.param-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}

code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
}
</style>
