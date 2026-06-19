<template>
  <div class="step-card">
    <h2 class="step-title">热床网格调平</h2>
    <p class="step-description">
      热床网格调平通过探测多个点来补偿热床不平整。需要先配置探针。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>什么是热床网格？</strong><br>
        打印机会在热床表面探测多个点，建立一个高度图。<br>
        打印时自动补偿热床的不平整，提高第一层附着力。
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Grid /></el-icon>
        是否启用
      </div>
      
      <el-switch 
        v-model="hasBedMesh" 
        active-text="启用热床网格" 
        inactive-text="不使用"
        @change="onToggle"
      />
    </div>
    
    <div v-if="hasBedMesh">
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Position /></el-icon>
          探测范围
        </div>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                网格最小坐标 (X, Y)
                <el-tooltip content="网格左下角坐标，需考虑探针偏移" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="meshMin" 
                placeholder="30, 30"
                @input="update"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <template #label>
                网格最大坐标 (X, Y)
                <el-tooltip content="网格右上角坐标，需考虑探针偏移" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="meshMax" 
                placeholder="200, 200"
                @input="update"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><Grid /></el-icon>
          网格参数
        </div>
        
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item>
              <template #label>
                探测点数 (X, Y)
                <el-tooltip content="网格的探测点数量，建议奇数" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input 
                v-model="probeCount" 
                placeholder="5, 5"
                @input="update"
              />
              <div class="param-hint">推荐 3,3 到 7,7</div>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                插值算法
                <el-tooltip content="双三次插值更平滑" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-select v-model="algorithm" @change="update">
                <el-option value="lagrange" label="拉格朗日" />
                <el-option value="bicubic" label="双三次 (推荐)" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item>
              <template #label>
                移动高度 (mm)
                <el-tooltip content="探测时的Z高度" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="horizontalMoveZ" 
                :min="2" 
                :max="20"
                :step="1"
                @change="update"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
        </el-row>
      </div>
      
      <div class="form-section">
        <div class="form-section-title">
          <el-icon><TrendCharts /></el-icon>
          淡出设置
        </div>
        
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item>
              <template #label>
                淡出起始高度 (mm)
                <el-tooltip content="开始淡出补偿的高度" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="fadeStart" 
                :min="0" 
                :max="5"
                :step="0.5"
                :precision="1"
                @change="update"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item>
              <template #label>
                淡出结束高度 (mm)
                <el-tooltip content="完全淡出补偿的高度" placement="top">
                  <el-icon class="help-tip"><QuestionFilled /></el-icon>
                </el-tooltip>
              </template>
              <el-input-number 
                v-model="fadeEnd" 
                :min="1" 
                :max="20"
                :step="1"
                @change="update"
                style="width: 100%"
              />
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
  InfoFilled, QuestionFilled, Grid, Position, 
  TrendCharts, ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const hasBedMesh = ref(false)
const meshMin = ref('30, 30')
const meshMax = ref('200, 200')
const probeCount = ref('5, 5')
const algorithm = ref('bicubic')
const horizontalMoveZ = ref(5)
const fadeStart = ref(0)
const fadeEnd = ref(10)

onMounted(() => {
  if (props.config.bed_mesh) {
    hasBedMesh.value = true
    meshMin.value = props.config.bed_mesh.mesh_min || '30, 30'
    meshMax.value = props.config.bed_mesh.mesh_max || '200, 200'
    probeCount.value = props.config.bed_mesh.probe_count || '5, 5'
    algorithm.value = props.config.bed_mesh.algorithm || 'bicubic'
    horizontalMoveZ.value = props.config.bed_mesh.horizontal_move_z || 5
    fadeStart.value = props.config.bed_mesh.fade_start || 0
    fadeEnd.value = props.config.bed_mesh.fade_end || 10
  }
})

function onToggle() {
  if (!hasBedMesh.value) {
    emit('update', { bed_mesh: null })
  } else {
    update()
  }
}

function update() {
  emit('update', {
    bed_mesh: {
      mesh_min: meshMin.value,
      mesh_max: meshMax.value,
      probe_count: probeCount.value,
      algorithm: algorithm.value,
      horizontal_move_z: horizontalMoveZ.value,
      fade_start: fadeStart.value,
      fade_end: fadeEnd.value
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
</style>
