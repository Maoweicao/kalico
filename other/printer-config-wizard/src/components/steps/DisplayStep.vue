<template>
  <div class="step-card">
    <h2 class="step-title">显示屏配置</h2>
    <p class="step-description">
      配置LCD显示屏。如果您的打印机没有显示屏，可以跳过此步。
    </p>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Monitor /></el-icon>
        是否有显示屏
      </div>
      
      <el-switch 
        v-model="hasDisplay" 
        active-text="有显示屏" 
        inactive-text="无显示屏"
        @change="onToggle"
      />
    </div>
    
    <div v-if="hasDisplay">
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Monitor /></el-icon>
          显示屏类型
        </div>
        
        <div class="display-types">
          <div 
            v-for="display in displayTypes" 
            :key="display.value"
            class="display-option"
            :class="{ active: lcdType === display.value }"
            @click="selectDisplay(display.value)"
          >
            <div class="display-name">{{ display.label }}</div>
            <div class="display-desc">{{ display.desc }}</div>
          </div>
        </div>
      </div>
      
      <div v-if="lcdType" class="form-section">
        <div class="form-section-title">
          <el-icon><Cpu /></el-icon>
          引脚配置
        </div>
        
        <div v-if="lcdType === 'st7920'">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  CS 引脚
                  <el-tooltip content="片选引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.cs_pin" placeholder="PA3" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  SCLK 引脚
                  <el-tooltip content="时钟引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.sclk_pin" placeholder="PA1" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  SID 引脚
                  <el-tooltip content="数据引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.sid_pin" placeholder="PA2" @input="update" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <div v-else>
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  EN 引脚
                  <el-tooltip content="使能引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.cs_pin" placeholder="PA3" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  RS 引脚
                  <el-tooltip content="寄存器选择引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.sclk_pin" placeholder="PA1" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  D4 引脚
                  <el-tooltip content="数据引脚" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input v-model="displayPins.sid_pin" placeholder="PA2" @input="update" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                旋转编码器引脚
                <el-tooltip content="A,B引脚用逗号分隔" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="displayPins.encoder_pins" placeholder="PA4, PA5" @input="update" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                确认按钮引脚
                <el-tooltip content="编码器按下引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="displayPins.click_pin" placeholder="PA6" @input="update" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                停止按钮引脚
                <el-tooltip content="紧急停止按钮引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="displayPins.kill_pin" placeholder="PA7" @input="update" />
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
  InfoFilled, QuestionFilled, Monitor, Cpu, 
  ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasDisplay = ref(false)
const lcdType = ref('')

const displayTypes = [
  { value: 'st7920', label: 'ST7920', desc: '128x64全图形屏，Ender 3 V2等' },
  { value: 'hd44780', label: 'HD44780', desc: '20x4字符屏，经典款' },
  { value: 'uc1701', label: 'UC1701', desc: '128x64图形屏' },
  { value: 'ssd1306', label: 'SSD1306', desc: 'OLED显示屏' },
  { value: 'sh1106', label: 'SH1106', desc: 'OLED显示屏' }
]

const displayPins = ref({
  cs_pin: '',
  sclk_pin: '',
  sid_pin: '',
  encoder_pins: '',
  click_pin: '',
  kill_pin: ''
})

onMounted(() => {
  if (props.config.display) {
    hasDisplay.value = true
    lcdType.value = props.config.display.lcd_type || ''
    displayPins.value = {
      cs_pin: props.config.display.cs_pin || '',
      sclk_pin: props.config.display.sclk_pin || '',
      sid_pin: props.config.display.sid_pin || '',
      encoder_pins: props.config.display.encoder_pins || '',
      click_pin: props.config.display.click_pin || '',
      kill_pin: props.config.display.kill_pin || ''
    }
  }
})

function onToggle() {
  if (!hasDisplay.value) {
    emit('update', { display: null })
  } else {
    update()
  }
}

function selectDisplay(value) {
  lcdType.value = value
  update()
}

function update() {
  emit('update', {
    display: {
      lcd_type: lcdType.value,
      ...displayPins.value
    }
  })
}
</script>

<style scoped>
.display-types {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.display-option {
  border: 2px solid var(--border-color);
  border-radius: var(--radius-medium);
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: center;
}

.display-option:hover {
  border-color: var(--primary-light);
}

.display-option.active {
  border-color: var(--primary-color);
  background: #ecf5ff;
}

.display-name {
  font-weight: 600;
  font-size: 14px;
  margin-bottom: 4px;
}

.display-desc {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
