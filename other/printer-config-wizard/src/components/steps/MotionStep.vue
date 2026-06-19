<template>
  <div class="step-card">
    <h2 class="step-title">运动参数</h2>
    <p class="step-description">
      设置打印机的尺寸、最大速度和加速度。这些参数决定了打印机的运动性能上限。
    </p>
    
    <div class="warning-box">
      <el-icon><Warning /></el-icon>
      <p>
        <strong>安全提示：</strong>过高的速度和加速度可能导致丢步、振动甚至损坏打印机。<br>
        建议从保守值开始，测试稳定后再逐步提高。
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Grid /></el-icon>
        打印机尺寸 (mm)
      </div>
      
      <el-row :gutter="16">
        <el-col :span="8">
          <el-form-item>
            <template #label>
              X轴行程 (mm)
              <el-tooltip content="X轴最大移动距离，即打印宽度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="sizeX" 
              :min="100" 
              :max="1000" 
              :step="10"
              @change="updateMotion"
              style="width: 100%"
            />
            <div class="param-hint">常见值：220/235/250/300/350</div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              Y轴行程 (mm)
              <el-tooltip content="Y轴最大移动距离，即打印深度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="sizeY" 
              :min="100" 
              :max="1000" 
              :step="10"
              @change="updateMotion"
              style="width: 100%"
            />
            <div class="param-hint">常见值：220/235/250/300/350</div>
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item>
            <template #label>
              Z轴行程 (mm)
              <el-tooltip content="Z轴最大移动距离，即打印高度" placement="top">
                <el-icon class="help-tip"><QuestionFilled /></el-icon>
              </el-tooltip>
            </template>
            <el-input-number 
              v-model="sizeZ" 
              :min="100" 
              :max="1000" 
              :step="10"
              @change="updateMotion"
              style="width: 100%"
            />
            <div class="param-hint">常见值：250/300/350/400</div>
          </el-form-item>
        </el-col>
      </el-row>
      
      <div class="info-box">
        <el-icon><InfoFilled /></el-icon>
        <p>
          <strong>常见打印机尺寸参考：</strong><br>
          • Ender 3: 235 × 235 × 250 mm<br>
          • Ender 5: 220 × 220 × 300 mm<br>
          • Voron 250: 250 × 250 × 250 mm<br>
          • Voron 300: 300 × 300 × 300 mm<br>
          • Voron 350: 350 × 350 × 350 mm
        </p>
      </div>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Odometer /></el-icon>
        XY轴运动参数
      </div>
      
      <el-form-item>
        <template #label>
          最大速度 (mm/s)
          <el-tooltip content="打印机XY轴的最大移动速度" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-slider 
          v-model="maxVelocity" 
          :min="50" 
          :max="600" 
          :step="10"
          show-input
          @change="updateMotion"
        />
        <div class="param-hint">
          推荐值：Cartesian 200-400，CoreXY 300-500
        </div>
      </el-form-item>
      
      <el-form-item>
        <template #label>
          最大加速度 (mm/s²)
          <el-tooltip content="打印机XY轴的最大加速度" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-slider 
          v-model="maxAccel" 
          :min="500" 
          :max="10000" 
          :step="100"
          show-input
          @change="updateMotion"
        />
        <div class="param-hint">
          推荐值：Cartesian 1000-3000，CoreXY 3000-7000
        </div>
      </el-form-item>
      
      <el-form-item>
        <template #label>
          直角速度 (mm/s)
          <el-tooltip content="直角转弯时的最大速度，值越小转角越精确" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-slider 
          v-model="squareCornerVelocity" 
          :min="0" 
          :max="30" 
          :step="0.5"
          show-input
          @change="updateMotion"
        />
        <div class="param-hint">
          默认5.0，降低可提高转角精度
        </div>
      </el-form-item>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Bottom /></el-icon>
        Z轴运动参数
      </div>
      
      <el-form-item>
        <template #label>
          Z轴最大速度 (mm/s)
          <el-tooltip content="Z轴通常使用丝杆，速度较低" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-slider 
          v-model="maxZVelocity" 
          :min="1" 
          :max="50" 
          :step="1"
          show-input
          @change="updateMotion"
        />
        <div class="param-hint">
          普通丝杆：5-15 mm/s，高速丝杆：20-50 mm/s
        </div>
      </el-form-item>
      
      <el-form-item>
        <template #label>
          Z轴最大加速度 (mm/s²)
          <el-tooltip content="Z轴的加速度，通常较低" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-slider 
          v-model="maxZAccel" 
          :min="10" 
          :max="500" 
          :step="10"
          show-input
          @change="updateMotion"
        />
        <div class="param-hint">
          推荐100-300 mm/s²
        </div>
      </el-form-item>
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
  QuestionFilled, Odometer, Bottom, Warning, InfoFilled, Grid,
  ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const sizeX = ref(235)
const sizeY = ref(235)
const sizeZ = ref(250)
const maxVelocity = ref(300)
const maxAccel = ref(3000)
const maxZVelocity = ref(5)
const maxZAccel = ref(100)
const squareCornerVelocity = ref(5.0)

onMounted(() => {
  if (props.config.printer) {
    sizeX.value = props.config.printer.size_x || 235
    sizeY.value = props.config.printer.size_y || 235
    sizeZ.value = props.config.printer.size_z || 250
    maxVelocity.value = props.config.printer.max_velocity || 300
    maxAccel.value = props.config.printer.max_accel || 3000
    maxZVelocity.value = props.config.printer.max_z_velocity || 5
    maxZAccel.value = props.config.printer.max_z_accel || 100
    squareCornerVelocity.value = props.config.printer.square_corner_velocity || 5.0
  }
})

function updateMotion() {
  emit('update', {
    printer: {
      ...props.config.printer,
      size_x: sizeX.value,
      size_y: sizeY.value,
      size_z: sizeZ.value,
      max_velocity: maxVelocity.value,
      max_accel: maxAccel.value,
      max_z_velocity: maxZVelocity.value,
      max_z_accel: maxZAccel.value,
      square_corner_velocity: squareCornerVelocity.value
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

.el-slider {
  --el-slider-main-bg-color: var(--primary-color);
}

:deep(.el-slider__input) {
  width: 80px;
}
</style>
