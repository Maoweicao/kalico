<template>
  <div class="step-card">
    <h2 class="step-title">打印机类型</h2>
    <p class="step-description">
      选择您的打印机机械结构类型。不同的运动学类型决定了XYZ轴的运动方式。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>如何判断打印机类型？</strong><br>
        • 如果XYZ三个轴各自独立运动 → Cartesian（最常见）<br>
        • 如果XY轴通过两条皮带联动形成对角运动 → CoreXY<br>
        • 如果是三角洲/并联结构 → Delta<br>
        • 不确定的话，大多数入门级打印机都是 Cartesian
      </p>
    </div>
    
    <div class="kinematics-select">
      <div 
        v-for="kin in kinematicsTypes" 
        :key="kin.value"
        class="kinematics-option"
        :class="{ active: selected === kin.value }"
        @click="selectKinematics(kin.value)"
      >
        <div class="kin-icon">{{ kin.icon }}</div>
        <div class="kin-name">{{ kin.label }}</div>
        <div class="kin-desc">{{ kin.desc }}</div>
      </div>
    </div>
    
    <div v-if="selected" class="selected-info">
      <el-tag type="success" size="large">
        已选择：{{ kinematicsTypes.find(k => k.value === selected)?.label }}
      </el-tag>
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
import { InfoFilled, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const selected = ref('cartesian')

const kinematicsTypes = [
  { 
    value: 'cartesian', 
    label: 'Cartesian（笛卡尔）', 
    icon: '⬜',
    desc: 'XYZ三轴独立运动，最常见类型。Ender 3、CR-10等。'
  },
  { 
    value: 'corexy', 
    label: 'CoreXY', 
    icon: '◇',
    desc: 'XY轴联动，速度快精度高。Voron、RatRig等。'
  },
  { 
    value: 'corexz', 
    label: 'CoreXZ', 
    icon: '◇',
    desc: 'XZ轴联动，Y轴独立。某些特殊结构打印机。'
  },
  { 
    value: 'delta', 
    label: 'Delta（三角洲）', 
    icon: '△',
    desc: '三臂并联结构，打印高度大。Kossel、Rostock等。'
  },
  { 
    value: 'deltesian', 
    label: 'Deltesian', 
    icon: '▽',
    desc: 'Delta和Cartesian的混合结构。'
  },
  { 
    value: 'polar', 
    label: 'Polar（极坐标）', 
    icon: '◎',
    desc: '使用旋转平台和径向移动。'
  },
  { 
    value: 'rotary_delta', 
    label: 'Rotary Delta', 
    icon: '⟐',
    desc: '旋转式Delta结构。'
  },
  { 
    value: 'winch', 
    label: 'Cable Winch（缆索）', 
    icon: '⟋',
    desc: '使用缆索驱动的并联结构。'
  }
]

onMounted(() => {
  if (props.config.printer?.kinematics) {
    selected.value = props.config.printer.kinematics
  }
})

function selectKinematics(value) {
  selected.value = value
  emit('update', {
    printer: {
      ...props.config.printer,
      kinematics: value
    }
  })
}
</script>

<style scoped>
.selected-info {
  margin-top: 24px;
  text-align: center;
}
</style>
