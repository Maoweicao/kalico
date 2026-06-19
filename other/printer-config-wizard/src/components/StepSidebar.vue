<template>
  <div class="step-sidebar">
    <div class="sidebar-header">
      <h3>{{ t('configPreview') }}</h3>
    </div>
    
    <div class="phase-section">
      <div class="phase-title">
        <el-icon><Setting /></el-icon>
        <span>{{ t('phaseBasic') }}</span>
      </div>
      <div 
        v-for="step in basicSteps" 
        :key="step.id"
        class="step-item"
        :class="{ 
          active: currentStep === step.id,
          completed: currentStep > step.id 
        }"
        @click="$emit('goToStep', step.id)"
      >
        <div class="step-number">
          <el-icon v-if="currentStep > step.id"><Check /></el-icon>
          <span v-else>{{ step.id + 1 }}</span>
        </div>
        <div class="step-info">
          <span class="step-name">{{ step.name }}</span>
        </div>
      </div>
    </div>
    
    <div class="phase-section">
      <div class="phase-title">
        <el-icon><Tools /></el-icon>
        <span>{{ t('phaseAdvanced') }}</span>
      </div>
      <div 
        v-for="step in advancedSteps" 
        :key="step.id"
        class="step-item"
        :class="{ 
          active: currentStep === step.id,
          completed: currentStep > step.id 
        }"
        @click="$emit('goToStep', step.id)"
      >
        <div class="step-number">
          <el-icon v-if="currentStep > step.id"><Check /></el-icon>
          <span v-else>{{ step.id + 1 }}</span>
        </div>
        <div class="step-info">
          <span class="step-name">{{ step.name }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, inject } from 'vue'
import { Setting, Tools, Check } from '@element-plus/icons-vue'

const t = inject('t')

const props = defineProps({
  currentStep: {
    type: Number,
    required: true
  },
  steps: {
    type: Array,
    required: true
  }
})

defineEmits(['goToStep'])

const basicSteps = computed(() => props.steps.filter(s => s.phase === 'basic'))
const advancedSteps = computed(() => props.steps.filter(s => s.phase === 'advanced'))
</script>

<style scoped>
.step-sidebar {
  padding: 16px 0;
  height: 100%;
}

.sidebar-header {
  padding: 0 20px 16px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 16px;
}

.sidebar-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.phase-section {
  margin-bottom: 24px;
}

.phase-title {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 20px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.phase-title .el-icon {
  font-size: 14px;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 20px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
}

.step-item:hover {
  background: #f0f7ff;
}

.step-item.active {
  background: #ecf5ff;
}

.step-item.active::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--primary-color);
  border-radius: 0 2px 2px 0;
}

.step-item.completed .step-number {
  background: var(--success-color);
  color: white;
}

.step-number {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: #e4e7ed;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 600;
  flex-shrink: 0;
  transition: all 0.2s ease;
}

.step-item.active .step-number {
  background: var(--primary-color);
  color: white;
}

.step-info {
  flex: 1;
  min-width: 0;
}

.step-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.step-item.active .step-name {
  color: var(--primary-color);
  font-weight: 600;
}

.step-item.completed .step-name {
  color: var(--success-color);
}
</style>
