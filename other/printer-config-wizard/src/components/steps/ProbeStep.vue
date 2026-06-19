<template>
  <div class="step-card">
    <h2 class="step-title">探针配置</h2>
    <p class="step-description">
      探针用于自动热床调平和Z轴归位。如果您的打印机没有探针，可以跳过此步。
    </p>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Aim /></el-icon>
        是否有探针
      </div>
      
      <el-switch 
        v-model="hasProbe" 
        active-text="有探针" 
        inactive-text="无探针"
        @change="onProbeToggle"
      />
    </div>
    
    <div v-if="hasProbe">
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Connection /></el-icon>
          探针类型
        </div>
        
        <el-radio-group v-model="probeType" class="probe-type-select">
          <el-radio-button label="probe">
            <div class="probe-option">
              <span class="probe-name">普通探针</span>
              <span class="probe-desc">电感/涡流探针</span>
            </div>
          </el-radio-button>
          <el-radio-button label="bltouch">
            <div class="probe-option">
              <span class="probe-name">BLTouch</span>
              <span class="probe-desc">伺服式探针</span>
            </div>
          </el-radio-button>
          <el-radio-button label="dockable_probe">
            <div class="probe-option">
              <span class="probe-name">可停靠探针</span>
              <span class="probe-desc">磁吸式探针</span>
            </div>
          </el-radio-button>
        </el-radio-group>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Cpu /></el-icon>
          引脚配置
        </div>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                信号引脚
                <el-tooltip content="探针信号引脚，通常需要^前缀" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="probe.pin" placeholder="^PB1" @input="updateProbe" />
            </el-form-item>
          </el-col>
          <el-col v-if="probeType === 'bltouch'" :span="12">
            <el-form-item>
              <template #label>
                控制引脚
                <el-tooltip content="BLTouch的伺服控制引脚" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input v-model="probe.control_pin" placeholder="PB0" @input="updateProbe" />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Position /></el-icon>
          偏移配置
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                X偏移 (mm)
                <el-tooltip content="探针相对于喷嘴的X偏移" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="probe.x_offset" 
                :min="-100" 
                :max="100"
                :step="0.5"
                :precision="1"
                @change="updateProbe"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                Y偏移 (mm)
                <el-tooltip content="探针相对于喷嘴的Y偏移" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="probe.y_offset" 
                :min="-100" 
                :max="100"
                :step="0.5"
                :precision="1"
                @change="updateProbe"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                Z偏移 (mm)
                <el-tooltip content="探针触发时喷嘴与热床的距离，需要校准" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="probe.z_offset" 
                :min="-5" 
                :max="5"
                :step="0.05"
                :precision="2"
                @change="updateProbe"
                style="width: 100%"
              />
              <div class="param-hint">通过 PROBE_CALIBRATE 命令校准</div>
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><VideoPlay /></el-icon>
          探测参数
        </div>
        
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item>
              <template #label>
                探测速度 (mm/s)
                <el-tooltip content="探针下降速度" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="probe.speed" 
                :min="1" 
                :max="20"
                :step="0.5"
                :precision="1"
                @change="updateProbe"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                采样次数
                <el-tooltip content="每个点探测几次取平均" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="probe.samples" @change="updateProbe">
                <el-option :value="1" label="1次" />
                <el-option :value="2" label="2次" />
                <el-option :value="3" label="3次" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                结果算法
                <el-tooltip content="多次采样的取值方式" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="probe.samples_result" @change="updateProbe">
                <el-option value="average" label="平均值" />
                <el-option value="median" label="中位数" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item>
              <template #label>
                回退距离 (mm)
                <el-tooltip content="探测后回退距离" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="probe.sample_retract_dist" 
                :min="0.5" 
                :max="10"
                :step="0.5"
                :precision="1"
                @change="updateProbe"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><HomeFilled /></el-icon>
          安全Z归位
        </div>
        
        <el-switch 
          v-model="hasSafeZHome" 
          active-text="启用安全Z归位" 
          inactive-text="不使用"
          @change="updateSafeZHome"
        />
        
        <div v-if="hasSafeZHome" style="margin-top: 16px;">
          <el-row :gutter="16">
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  归位位置 (X, Y)
                  <el-tooltip content="Z轴归位时移动到的XY位置" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input 
                  v-model="safeZHomePosition" 
                  placeholder="117, 117"
                  @input="updateSafeZHome"
                />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item>
                <template #label>
                  抬升高度 (mm)
                  <el-tooltip content="归位前先抬升的高度" placement="top">
                    <el-icon class="help-tip"><QuestionFilled /></el-icon>
                  </el-tooltip>
                </template>
                <el-input-number 
                  v-model="safeZHomeZHop" 
                  :min="1" 
                  :max="20"
                  :step="1"
                  @change="updateSafeZHome"
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
  InfoFilled, QuestionFilled, Aim, Connection, Cpu, 
  Position, VideoPlay, HomeFilled, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasProbe = ref(false)
const probeType = ref('probe')
const hasSafeZHome = ref(false)
const safeZHomePosition = ref('117, 117')
const safeZHomeZHop = ref(10)

const defaultProbe = {
  type: 'probe',
  pin: '',
  control_pin: '',
  x_offset: 0,
  y_offset: 0,
  z_offset: 1.0,
  speed: 5.0,
  samples: 1,
  samples_result: 'average',
  sample_retract_dist: 2.0
}

const probe = ref({ ...defaultProbe })

onMounted(() => {
  if (props.config.probe) {
    hasProbe.value = true
    probe.value = { ...defaultProbe, ...props.config.probe }
    probeType.value = props.config.probe.type || 'probe'
  }
  if (props.config.safe_z_home) {
    hasSafeZHome.value = true
    safeZHomePosition.value = props.config.safe_z_home.home_xy_position || '117, 117'
    safeZHomeZHop.value = props.config.safe_z_home.z_hop || 10
  }
})

function onProbeToggle() {
  if (!hasProbe.value) {
    emit('update', { probe: null, safe_z_home: null })
  } else {
    updateProbe()
  }
}

function updateProbe() {
  emit('update', {
    probe: {
      ...probe.value,
      type: probeType.value
    }
  })
}

function updateSafeZHome() {
  if (hasSafeZHome.value) {
    emit('update', {
      safe_z_home: {
        home_xy_position: safeZHomePosition.value,
        z_hop: safeZHomeZHop.value,
        speed: 5.0
      }
    })
  } else {
    emit('update', { safe_z_home: null })
  }
}
</script>

<style scoped>
.probe-type-select {
  display: flex;
  gap: 12px;
}

.probe-option {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.probe-name {
  font-weight: 600;
}

.probe-desc {
  font-size: 11px;
  color: var(--text-secondary);
}

.param-hint {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 4px;
}
</style>
