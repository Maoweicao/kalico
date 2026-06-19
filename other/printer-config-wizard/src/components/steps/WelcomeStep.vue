<template>
  <div class="step-card welcome-step">
    <div class="welcome-header">
      <div class="welcome-icon">
        <el-icon :size="48" color="#409eff"><Setting /></el-icon>
      </div>
      <h1 class="step-title">{{ t('welcomeTitle') }}</h1>
      <p class="step-description" v-html="t('welcomeDesc').replace('\n', '<br>')"></p>
    </div>
    
    <div class="welcome-features">
      <div class="feature-card">
        <el-icon :size="32" color="#67c23a"><CircleCheck /></el-icon>
        <h3>{{ t('featureEasy') }}</h3>
        <p>{{ t('featureEasyDesc') }}</p>
      </div>
      <div class="feature-card">
        <el-icon :size="32" color="#e6a23c"><MagicStick /></el-icon>
        <h3>{{ t('featureSmart') }}</h3>
        <p>{{ t('featureSmartDesc') }}</p>
      </div>
      <div class="feature-card">
        <el-icon :size="32" color="#409eff"><Download /></el-icon>
        <h3>{{ t('featureExport') }}</h3>
        <p>{{ t('featureExportDesc') }}</p>
      </div>
    </div>
    
    <div class="welcome-guide">
      <h3>{{ locale === 'zh' ? '配置流程概览' : 'Configuration Overview' }}</h3>
      <div class="guide-steps">
        <div class="guide-phase">
          <div class="phase-badge basic">{{ t('phaseBasic') }}</div>
          <div class="phase-items">
            <span>{{ t('stepMcu') }}</span>
            <span>{{ t('stepKinematics') }}</span>
            <span>{{ t('stepMotion') }}</span>
            <span>{{ t('stepStepperX') }}/{{ t('stepStepperY') }}/{{ t('stepStepperZ') }}</span>
            <span>{{ t('stepExtruder') }}</span>
            <span>{{ t('stepHeaterBed') }}</span>
            <span>{{ t('stepFan') }}</span>
          </div>
        </div>
        <div class="guide-phase">
          <div class="phase-badge advanced">{{ t('phaseAdvanced') }}</div>
          <div class="phase-items">
            <span>{{ t('stepTmc') }}</span>
            <span>{{ t('stepToolboard') }}</span>
            <span>{{ t('stepProbe') }}</span>
            <span>{{ t('stepBedMesh') }}</span>
            <span>{{ t('stepInputShaper') }}</span>
            <span>{{ t('stepDisplay') }}</span>
            <span>{{ t('stepTempSensor') }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <div class="welcome-tip">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>{{ locale === 'zh' ? '提示：' : 'Tip: ' }}</strong>
        {{ locale === 'zh' ? '您可以随时点击左侧步骤跳转，也可以使用底部按钮前进/后退。' : 'You can click steps on the left sidebar or use buttons at the bottom to navigate.' }}<br>
        {{ locale === 'zh' ? '右侧实时预览生成的配置文件。' : 'The right panel shows real-time config preview.' }}
      </p>
    </div>
    
    <div class="step-actions">
      <el-button type="primary" size="large" @click="$emit('next')">
        {{ t('startConfig') }}
        <el-icon class="el-icon--right"><ArrowRight /></el-icon>
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'
import { Setting, CircleCheck, MagicStick, Download, InfoFilled, ArrowRight } from '@element-plus/icons-vue'

const t = inject('t')
const locale = inject('locale')

defineProps({
  config: Object
})

defineEmits(['update', 'next', 'prev'])
</script>

<style scoped>
.welcome-step {
  max-width: 800px;
  margin: 0 auto;
}

.welcome-header {
  text-align: center;
  margin-bottom: 40px;
}

.welcome-icon {
  margin-bottom: 16px;
}

.welcome-header .step-title {
  font-size: 28px;
  margin-bottom: 12px;
}

.welcome-header .step-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.welcome-features {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 32px;
}

.feature-card {
  text-align: center;
  padding: 24px 16px;
  background: var(--bg-color);
  border-radius: var(--radius-medium);
  transition: transform 0.2s ease;
}

.feature-card:hover {
  transform: translateY(-4px);
}

.feature-card h3 {
  font-size: 16px;
  margin: 12px 0 8px;
  color: var(--text-primary);
}

.feature-card p {
  font-size: 13px;
  color: var(--text-secondary);
}

.welcome-guide {
  background: var(--bg-color);
  border-radius: var(--radius-medium);
  padding: 24px;
  margin-bottom: 24px;
}

.welcome-guide h3 {
  font-size: 16px;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.guide-steps {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.guide-phase {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.phase-badge {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.phase-badge.basic {
  background: #ecf5ff;
  color: #409eff;
}

.phase-badge.advanced {
  background: #fdf6ec;
  color: #e6a23c;
}

.phase-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.phase-items span {
  background: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 13px;
  color: var(--text-regular);
  border: 1px solid var(--border-color);
}

.welcome-tip {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  background: #f0f9ff;
  border: 1px solid #b3d8ff;
  border-radius: var(--radius-medium);
  padding: 16px;
  margin-bottom: 32px;
}

.welcome-tip .el-icon {
  color: var(--primary-color);
  margin-top: 2px;
  flex-shrink: 0;
}

.welcome-tip p {
  font-size: 13px;
  color: var(--text-regular);
  line-height: 1.6;
  margin: 0;
}

.step-actions {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .welcome-features {
    grid-template-columns: 1fr;
  }
  
  .guide-phase {
    flex-direction: column;
  }
}
</style>
