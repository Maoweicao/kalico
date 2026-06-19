<template>
  <div class="step-card">
    <h2 class="step-title">导出配置</h2>
    <p class="step-description">
      恭喜！您已完成所有配置。现在可以导出您的打印机配置文件了。
    </p>
    
    <div class="export-section">
      <div class="export-card">
        <div class="export-icon">
          <el-icon :size="48" color="#409eff"><Document /></el-icon>
        </div>
        <h3>CFG 格式</h3>
        <p>Kalico/Klipper 原生配置格式</p>
        <el-button type="primary" size="large" @click="exportCfg">
          <el-icon class="el-icon--left"><Download /></el-icon>
          导出 printer.cfg
        </el-button>
      </div>
      
      <div class="export-card">
        <div class="export-icon">
          <el-icon :size="48" color="#67c23a"><Document /></el-icon>
        </div>
        <h3>JSON 格式</h3>
        <p>结构化数据格式，便于程序处理</p>
        <el-button type="success" size="large" @click="exportJson">
          <el-icon class="el-icon--left"><Download /></el-icon>
          导出 printer.json
        </el-button>
      </div>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><CopyDocument /></el-icon>
        复制配置
      </div>
      
      <div class="copy-actions">
        <el-button @click="copyCfg">
          <el-icon class="el-icon--left"><CopyDocument /></el-icon>
          复制 CFG 格式
        </el-button>
        <el-button @click="copyJson">
          <el-icon class="el-icon--left"><CopyDocument /></el-icon>
          复制 JSON 格式
        </el-button>
      </div>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><InfoFilled /></el-icon>
        下一步操作
      </div>
      
      <div class="info-box">
        <el-icon><InfoFilled /></el-icon>
        <p>
          <strong>使用配置文件：</strong><br>
          1. 将 <code>printer.cfg</code> 复制到树莓派的 <code>~/printer_data/config/</code> 目录<br>
          2. 根据实际情况修改串口路径和引脚<br>
          3. 重启 Kalico 服务：<code>sudo service kalico restart</code><br>
          4. 通过 Web 界面检查配置是否正确<br>
          5. 运行 <code>PID_CALIBRATE</code> 校准温度控制<br>
          6. 运行 <code>SHAPER_CALIBRATE</code> 校准输入整形
        </p>
      </div>
    </div>
    
    <div class="form-section">
      <div class="form-section-title">
        <el-icon><Warning /></el-icon>
        注意事项
      </div>
      
      <div class="warning-box">
        <el-icon><Warning /></el-icon>
        <p>
          <strong>安全提示：</strong><br>
          • 首次使用前请仔细检查所有引脚配置<br>
          • 确保温度限制设置合理<br>
          • 建议先在断电状态下检查配置<br>
          • 首次加热时请监控温度变化
        </p>
      </div>
    </div>
    
    <div class="step-actions">
      <el-button @click="$emit('prev')">
        <el-icon class="el-icon--left"><ArrowLeft /></el-icon>
        上一步
      </el-button>
      <el-button type="success" @click="exportCfg">
        <el-icon class="el-icon--left"><Download /></el-icon>
        导出配置
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { 
  Document, Download, CopyDocument, InfoFilled, 
  Warning, ArrowLeft 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { generateCfg } from '../../utils/configGenerator'
import { generateJson } from '../../utils/exporter'

const props = defineProps({
  config: Object
})

const emit = defineEmits(['update', 'next', 'prev'])

function exportCfg() {
  downloadFile(generateCfg(props.config), 'printer.cfg', 'text/plain')
  ElMessage.success('已导出 printer.cfg')
}

function exportJson() {
  downloadFile(generateJson(props.config), 'printer.json', 'application/json')
  ElMessage.success('已导出 printer.json')
}

function copyCfg() {
  navigator.clipboard.writeText(generateCfg(props.config))
  ElMessage.success('CFG 配置已复制到剪贴板')
}

function copyJson() {
  navigator.clipboard.writeText(generateJson(props.config))
  ElMessage.success('JSON 配置已复制到剪贴板')
}

function downloadFile(content, filename, type) {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.export-section {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.export-card {
  text-align: center;
  padding: 32px;
  background: var(--bg-color);
  border-radius: var(--radius-large);
  border: 2px solid var(--border-color);
  transition: all 0.2s ease;
}

.export-card:hover {
  border-color: var(--primary-light);
  transform: translateY(-4px);
  box-shadow: var(--shadow-medium);
}

.export-icon {
  margin-bottom: 16px;
}

.export-card h3 {
  font-size: 18px;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.export-card p {
  font-size: 14px;
  color: var(--text-secondary);
  margin-bottom: 20px;
}

.copy-actions {
  display: flex;
  gap: 12px;
}

code {
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Fira Code', 'Consolas', monospace;
  font-size: 12px;
}

@media (max-width: 768px) {
  .export-section {
    grid-template-columns: 1fr;
  }
}
</style>
