<template>
  <div class="step-card">
    <h2 class="step-title">MCU 连接配置</h2>
    <p class="step-description">
      MCU (微控制器) 是打印机的主控板。需要配置它与树莓派/电脑的连接方式。
    </p>
    
    <div class="info-box">
      <el-icon><InfoFilled /></el-icon>
      <p>
        <strong>什么是MCU？</strong><br>
        MCU就是打印机的"大脑"，通常是主板上的主芯片（如STM32、ATmega等）。<br>
        它负责控制电机、读取温度、执行G-code指令等。
      </p>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Connection /></el-icon>
        选择连接方式
      </div>
      
      <el-radio-group v-model="connectionType" class="connection-type-select">
        <el-radio-button label="serial">
          <el-icon><Monitor /></el-icon>
          USB 串口
        </el-radio-button>
        <el-radio-button label="canbus">
          <el-icon><Connection /></el-icon>
          CAN 总线
        </el-radio-button>
      </el-radio-group>
    </div>
    
    <div v-if="connectionType === 'serial'" class="form-section">
      <div class="form-section-title">
        <el-icon><Monitor /></el-icon>
        串口配置
      </div>
      
      <div class="info-box">
        <el-icon><InfoFilled /></el-icon>
        <p>
          <strong>如何找到串口路径？</strong><br>
          在树莓派上运行以下命令：<br>
          <code>ls /dev/serial/by-id/*</code><br>
          或者 <code>ls /dev/ttyACM* /dev/ttyUSB*</code>
        </p>
      </div>
      
      <el-form-item label="选择主板（自动填充引脚）">
        <el-select 
          v-model="selectedBoard" 
          placeholder="选择您的主板型号" 
          clearable
          @change="onBoardChange"
          style="width: 100%"
        >
          <el-option-group
            v-for="category in boardCategories"
            :key="category.name"
            :label="category.name"
          >
            <el-option
              v-for="boardId in category.boards"
              :key="boardId"
              :label="boards[boardId].name"
              :value="boardId"
            >
              <div class="board-option-item">
                <span>{{ boards[boardId].name }}</span>
                <span class="board-desc">{{ boards[boardId].desc }}</span>
              </div>
            </el-option>
          </el-option-group>
        </el-select>
      </el-form-item>
      
      <el-form-item>
        <template #label>
          串口路径
          <el-tooltip content="MCU的USB串口设备路径" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-input 
          v-model="serialPath" 
          placeholder="/dev/serial/by-id/usb-Kalico_..."
          @input="updateSerial"
        />
      </el-form-item>
      
      <el-form-item>
        <template #label>
          波特率
          <el-tooltip content="通常保持默认250000即可" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-select v-model="baudRate" style="width: 100%">
          <el-option label="250000 (推荐)" :value="250000" />
          <el-option label="115200" :value="115200" />
          <el-option label="230400" :value="230400" />
          <el-option label="500000" :value="500000" />
        </el-select>
      </el-form-item>
    </div>
    
    <div v-if="connectionType === 'canbus'" class="form-section">
      <div class="form-section-title">
        <el-icon><Connection /></el-icon>
        CAN 总线配置
      </div>
      
      <div class="info-box">
        <el-icon><InfoFilled /></el-icon>
        <p>
          <strong>如何获取CAN UUID？</strong><br>
          运行以下命令查询：<br>
          <code>~/klippy-env/bin/python ~/klipper/scripts/canbus_query.py can0</code>
        </p>
      </div>
      
      <el-form-item>
        <template #label>
          CAN UUID
          <el-tooltip content="MCU的CAN总线唯一标识符" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-input 
          v-model="canbusUuid" 
          placeholder="1234567890abcdef"
          @input="updateCanbus"
        />
      </el-form-item>
      
      <el-form-item>
        <template #label>
          CAN 接口
          <el-tooltip content="CAN总线网络接口名称" placement="top">
            <el-icon class="help-tip"><QuestionFilled /></el-icon>
          </el-tooltip>
        </template>
        <el-input 
          v-model="canbusInterface" 
          placeholder="can0"
          @input="updateCanbus"
        />
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
  InfoFilled, Connection, Monitor, QuestionFilled, 
  ArrowLeft, ArrowRight 
} from '@element-plus/icons-vue'
import { boards, boardCategories } from '../../data/boards'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

const connectionType = ref('serial')
const serialPath = ref('')
const baudRate = ref(250000)
const canbusUuid = ref('')
const canbusInterface = ref('can0')
const selectedBoard = ref('')

onMounted(() => {
  if (props.config.mcu) {
    if (props.config.mcu.canbus_uuid) {
      connectionType.value = 'canbus'
      canbusUuid.value = props.config.mcu.canbus_uuid
      canbusInterface.value = props.config.mcu.canbus_interface || 'can0'
    } else {
      serialPath.value = props.config.mcu.serial || ''
    }
  }
})

function onBoardChange(boardId) {
  if (!boardId) return
  
  const board = boards[boardId]
  if (!board) return
  
  serialPath.value = board.serial
  
  emit('update', {
    mcu: {
      serial: board.serial,
      baud: baudRate.value
    },
    steppers: {
      stepper_x: {
        ...props.config.steppers?.stepper_x,
        step_pin: board.pins.stepper_x?.step_pin || '',
        dir_pin: board.pins.stepper_x?.dir_pin || '',
        enable_pin: board.pins.stepper_x?.enable_pin || '',
        endstop_pin: board.endstops?.x || ''
      },
      stepper_y: {
        ...props.config.steppers?.stepper_y,
        step_pin: board.pins.stepper_y?.step_pin || '',
        dir_pin: board.pins.stepper_y?.dir_pin || '',
        enable_pin: board.pins.stepper_y?.enable_pin || '',
        endstop_pin: board.endstops?.y || ''
      },
      stepper_z: {
        ...props.config.steppers?.stepper_z,
        step_pin: board.pins.stepper_z?.step_pin || '',
        dir_pin: board.pins.stepper_z?.dir_pin || '',
        enable_pin: board.pins.stepper_z?.enable_pin || '',
        endstop_pin: board.endstops?.z || ''
      }
    },
    extruder: {
      ...props.config.extruder,
      step_pin: board.pins.extruder?.step_pin || '',
      dir_pin: board.pins.extruder?.dir_pin || '',
      enable_pin: board.pins.extruder?.enable_pin || '',
      heater_pin: board.pins.extruder?.heater_pin || '',
      sensor_pin: board.thermistors?.extruder || ''
    },
    heater_bed: {
      ...props.config.heater_bed,
      heater_pin: board.pins.heater_bed?.heater_pin || '',
      sensor_pin: board.thermistors?.heater_bed || ''
    },
    fan: {
      ...props.config.fan,
      pin: board.pins.fan?.pin || ''
    },
    tmc: {
      ...props.config.tmc,
      stepper_x: board.pins.tmc2209_x ? {
        driver_type: 'tmc2209',
        uart_pin: board.pins.tmc2209_x.uart_pin,
        run_current: 0.8,
        interpolate: true,
        stealthchop_threshold: 0
      } : props.config.tmc?.stepper_x,
      stepper_y: board.pins.tmc2209_y ? {
        driver_type: 'tmc2209',
        uart_pin: board.pins.tmc2209_y.uart_pin,
        run_current: 0.8,
        interpolate: true,
        stealthchop_threshold: 0
      } : props.config.tmc?.stepper_y,
      stepper_z: board.pins.tmc2209_z ? {
        driver_type: 'tmc2209',
        uart_pin: board.pins.tmc2209_z.uart_pin,
        run_current: 0.8,
        interpolate: true,
        stealthchop_threshold: 0
      } : props.config.tmc?.stepper_z,
      extruder: board.pins.tmc2209_e ? {
        driver_type: 'tmc2209',
        uart_pin: board.pins.tmc2209_e.uart_pin,
        run_current: 0.8,
        interpolate: true,
        stealthchop_threshold: 0
      } : props.config.tmc?.extruder
    }
  })
}

function updateSerial() {
  emit('update', {
    mcu: {
      serial: serialPath.value,
      baud: baudRate.value
    }
  })
}

function updateCanbus() {
  emit('update', {
    mcu: {
      canbus_uuid: canbusUuid.value,
      canbus_interface: canbusInterface.value
    }
  })
}
</script>

<style scoped>
.connection-type-select {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
}

.connection-type-select .el-radio-button {
  flex: 1;
}

.connection-type-select :deep(.el-radio-button__inner) {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.board-option-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.board-option-item .board-desc {
  font-size: 12px;
  color: var(--text-secondary);
}
</style>
