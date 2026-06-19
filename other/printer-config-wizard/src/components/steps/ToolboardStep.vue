<template>
  <div class="step-card">
    <h2 class="step-title">工具板配置</h2>
    <p class="step-description">
      工具板（Toolhead Board）安装在打印头上，通过CAN总线与主板通信，减少布线。如果您的打印机没有使用工具板，可以跳过此步。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>什么是工具板？</strong><br>
        工具板安装在打印头附近，将挤出机电机、加热器、风扇、探针等信号通过CAN总线传回主板。<br>
        优势：减少拖链中的线缆数量，提高可靠性。
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Connection /></el-icon>
        是否使用工具板
      </div>
      
      <el-switch 
        v-model="hasToolboard" 
        active-text="使用工具板" 
        inactive-text="不使用"
        @change="onToggle"
      />
    </div>
    
    <div v-if="hasToolboard">
      <div v-for="(board, index) in toolboards" :key="index" class="form-section toolboard-section">
        <div class="form-section-title">
          <el-icon><Cpu /></el-icon>
          工具板 {{ index + 1 }}
          <el-button 
            type="danger" 
            text 
            size="small" 
            @click="removeToolboard(index)"
            style="margin-left: auto;"
          >
            <el-icon><Delete /></el-icon>
            删除
          </el-button>
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                工具板型号
                <el-tooltip content="选择工具板型号或自定义" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="board.type" @change="onTypeChange(index)" filterable>
                <el-option 
                  v-for="tb in toolboardOptions" 
                  :key="tb.id" 
                  :label="tb.name" 
                  :value="tb.id"
                >
                  <div>
                    <span>{{ tb.name }}</span>
                    <span style="float: right; color: #909399; font-size: 12px;">{{ tb.desc }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                CAN UUID
                <el-tooltip content="工具板的CAN总线UUID" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="board.canbus_uuid" 
                placeholder="1234567890abcdef"
                @input="update"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                名称
                <el-tooltip content="工具板的自定义名称" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="board.name" 
                placeholder="toolhead"
                @input="update"
              />
            </el-form-item>
          </el-col>
        </el-row>
        
        <div v-if="board.type === 'custom'" class="custom-pins">
          <el-divider content-position="left">自定义引脚</el-divider>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-form-item label="挤出机STEP">
                <el-input v-model="board.pins.step_pin" placeholder="PD4" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="挤出机DIR">
                <el-input v-model="board.pins.dir_pin" placeholder="PD3" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="加热棒">
                <el-input v-model="board.pins.heater_pin" placeholder="PB14" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="温度传感器">
                <el-input v-model="board.pins.sensor_pin" placeholder="PA3" @input="update" />
              </el-form-item>
            </el-col>
          </el-row>
          <el-row :gutter="16">
            <el-col :span="6">
              <el-form-item label="风扇0">
                <el-input v-model="board.pins.fan_pin" placeholder="PB15" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="风扇1">
                <el-input v-model="board.pins.fan1_pin" placeholder="PB12" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="探针">
                <el-input v-model="board.pins.probe_pin" placeholder="PB0" @input="update" />
              </el-form-item>
            </el-col>
            <el-col :span="6">
              <el-form-item label="UART引脚">
                <el-input v-model="board.pins.uart_pin" placeholder="PD5" @input="update" />
              </el-form-item>
            </el-col>
          </el-row>
        </div>
        
        <div v-if="board.type !== 'none' && board.type !== 'custom'" class="toolboard-info">
          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="步进引脚">{{ getPins('step_pin') }}</el-descriptions-item>
            <el-descriptions-item label="方向引脚">{{ getPins('dir_pin') }}</el-descriptions-item>
            <el-descriptions-item label="加热引脚">{{ getPins('heater_pin') }}</el-descriptions-item>
            <el-descriptions-item label="传感器引脚">{{ getPins('sensor_pin') }}</el-descriptions-item>
            <el-descriptions-item label="风扇引脚">{{ getPins('fan_pin') }}</el-descriptions-item>
            <el-descriptions-item label="UART引脚">{{ getPins('uart_pin') }}</el-descriptions-item>
          </el-descriptions>
        </div>
      </div>
      
      <el-button @click="addToolboard" style="width: 100%;">
        <el-icon class="el-icon--left"><Plus /></el-icon>
        添加工具板
      </el-button>
      
      <div class="form-section" style="margin-top: 16px;">
        <div class="form-section-title">
          <el-icon><InfoFilled /></el-icon>
          常见工具板类型
        </div>
        
        <div class="toolboard-grid">
          <div class="toolboard-card">
            <h4>BTT EBB36/42</h4>
            <p>适用于Voron StealthBurner</p>
          </div>
          <div class="toolboard-card">
            <h4>FLY SHT36/42</h4>
            <p>Mellow出品，兼容性强</p>
          </div>
          <div class="toolboard-card">
            <h4>BTT SB2209/2240</h4>
            <p>StealthBurner专用</p>
          </div>
          <div class="toolboard-card">
            <h4>Mellow BHT36</h4>
            <p>适用于各种热端</p>
          </div>
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
  InfoFilled, QuestionFilled, Connection, Cpu, 
  Delete, Plus, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasToolboard = ref(false)

const toolboardOptions = [
  { id: 'none', name: '无', desc: '不使用工具板' },
  { id: 'btt-ebb36-v1.2', name: 'BTT EBB36 V1.2', desc: 'CAN工具板，36mm间距' },
  { id: 'btt-ebb42-v1.2', name: 'BTT EBB42 V1.2', desc: 'CAN工具板，42mm间距' },
  { id: 'fly-sht36-v2', name: 'FLY SHT36 V2.0', desc: 'CAN工具板，36mm间距' },
  { id: 'fly-sht42-v2', name: 'FLY SHT42 V2.0', desc: 'CAN工具板，42mm间距' },
  { id: 'btt-sb2209-v1.0', name: 'BTT SB2209 V1.0', desc: 'StealthBurner工具板' },
  { id: 'btt-sb2240-v1.0', name: 'BTT SB2240 V1.0', desc: 'StealthBurner工具板' },
  { id: 'custom', name: '自定义', desc: '手动配置工具板引脚' }
]

const toolboardPins = {
  'btt-ebb36-v1.2': {
    step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2',
    heater_pin: 'PB14', sensor_pin: 'PA3', fan_pin: 'PB15', uart_pin: 'PD5'
  },
  'btt-ebb42-v1.2': {
    step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2',
    heater_pin: 'PB14', sensor_pin: 'PA3', fan_pin: 'PB15', uart_pin: 'PD5'
  },
  'fly-sht36-v2': {
    step_pin: 'PB15', dir_pin: 'PB14', enable_pin: '!PA8',
    heater_pin: 'PB13', sensor_pin: 'PB0', fan_pin: 'PB12', uart_pin: 'PB11'
  },
  'fly-sht42-v2': {
    step_pin: 'PB15', dir_pin: 'PB14', enable_pin: '!PA8',
    heater_pin: 'PB13', sensor_pin: 'PB0', fan_pin: 'PB12', uart_pin: 'PB11'
  },
  'btt-sb2209-v1.0': {
    step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2',
    heater_pin: 'PB14', sensor_pin: 'PA3', fan_pin: 'PB15', uart_pin: 'PD5'
  },
  'btt-sb2240-v1.0': {
    step_pin: 'PD4', dir_pin: 'PD3', enable_pin: '!PD2',
    heater_pin: 'PB14', sensor_pin: 'PA3', fan_pin: 'PB15', cs_pin: 'PD5'
  }
}

const defaultToolboard = {
  type: 'btt-ebb36-v1.2',
  canbus_uuid: '',
  name: 'toolhead',
  pins: {
    step_pin: '',
    dir_pin: '',
    enable_pin: '',
    heater_pin: '',
    sensor_pin: '',
    fan_pin: '',
    fan1_pin: '',
    probe_pin: '',
    uart_pin: ''
  }
}

const toolboards = ref([])

onMounted(() => {
  if (props.config.toolboards && props.config.toolboards.length > 0) {
    hasToolboard.value = true
    toolboards.value = props.config.toolboards.map(tb => ({
      ...defaultToolboard,
      ...tb,
      pins: { ...defaultToolboard.pins, ...tb.pins }
    }))
  }
})

function onToggle() {
  if (!hasToolboard.value) {
    emit('update', { toolboards: [] })
  } else {
    if (toolboards.value.length === 0) {
      addToolboard()
    }
  }
}

function addToolboard() {
  toolboards.value.push({ ...defaultToolboard, pins: { ...defaultToolboard.pins } })
  update()
}

function removeToolboard(index) {
  toolboards.value.splice(index, 1)
  if (toolboards.value.length === 0) {
    hasToolboard.value = false
  }
  update()
}

function onTypeChange(index) {
  const board = toolboards.value[index]
  if (board.type !== 'custom' && board.type !== 'none') {
    const pins = toolboardPins[board.type]
    if (pins) {
      board.pins = { ...pins }
    }
  }
  update()
}

function getPins(pinName) {
  return '...'
}

function update() {
  emit('update', {
    toolboards: toolboards.value.filter(tb => tb.type !== 'none')
  })
}
</script>

<style scoped>
.toolboard-section {
  border-left: 3px solid var(--primary-color);
  padding-left: 16px;
}

.custom-pins {
  margin-top: 12px;
}

.toolboard-info {
  margin-top: 12px;
}

.toolboard-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.toolboard-card {
  background: var(--bg-color);
  border-radius: var(--radius-medium);
  padding: 12px;
  border: 1px solid var(--border-color);
}

.toolboard-card h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  color: var(--text-primary);
}

.toolboard-card p {
  margin: 0;
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
