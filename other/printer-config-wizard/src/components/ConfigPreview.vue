<template>
  <div class="config-preview-container">
    <div class="preview-header">
      <h3>配置预览</h3>
      <div class="preview-actions">
        <el-button size="small" @click="copyConfig" :icon="CopyDocument">
          复制
        </el-button>
        <el-dropdown @command="handleExport">
          <el-button size="small" type="primary" :icon="Download">
            导出
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="cfg">
                <el-icon><Document /></el-icon>
                导出 .cfg 文件
              </el-dropdown-item>
              <el-dropdown-item command="json">
                <el-icon><Document /></el-icon>
                导出 .json 文件
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="preview-content">
      <pre class="config-code"><code v-html="highlightedConfig"></code></pre>
    </div>
    
    <div class="preview-footer">
      <div class="format-switch">
        <el-radio-group v-model="previewFormat" size="small">
          <el-radio-button label="cfg">CFG</el-radio-button>
          <el-radio-button label="json">JSON</el-radio-button>
        </el-radio-group>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { CopyDocument, Download, Document } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { generateCfg } from '../utils/configGenerator'
import { generateJson } from '../utils/exporter'

const props = defineProps({
  config: {
    type: Object,
    required: true
  }
})

const previewFormat = ref('cfg')

const configText = computed(() => {
  if (previewFormat.value === 'cfg') {
    return generateCfg(props.config)
  } else {
    return generateJson(props.config)
  }
})

const highlightedConfig = computed(() => {
  const text = configText.value
  if (previewFormat.value === 'cfg') {
    return highlightCfg(text)
  } else {
    return highlightJson(text)
  }
})

function highlightCfg(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/(#.*)/g, '<span class="comment">$1</span>')
    .replace(/(\[[\w_]+\])/g, '<span class="section">$1</span>')
    .replace(/^([\w_]+):/gm, '<span class="key">$1</span>:')
    .replace(/:\s*(.+)$/gm, ': <span class="value">$1</span>')
}

function highlightJson(text) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"([^"]+)":/g, '"<span class="key">$1</span>":')
    .replace(/:\s*"([^"]+)"/g, ': "<span class="value">$1</span>"')
    .replace(/:\s*(\d+\.?\d*)/g, ': <span class="value">$1</span>')
    .replace(/:\s*(true|false|null)/g, ': <span class="value">$1</span>')
}

function copyConfig() {
  navigator.clipboard.writeText(configText.value)
  ElMessage.success('配置已复制到剪贴板')
}

function handleExport(format) {
  const content = format === 'cfg' ? generateCfg(props.config) : generateJson(props.config)
  const blob = new Blob([content], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `printer.${format}`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success(`已导出 printer.${format}`)
}
</script>

<style scoped>
.config-preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.preview-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preview-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.preview-actions {
  display: flex;
  gap: 8px;
}

.preview-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  background: #1e1e1e;
}

.config-code {
  margin: 0;
  font-family: 'Fira Code', 'Consolas', 'Monaco', monospace;
  font-size: 12px;
  line-height: 1.6;
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-all;
}

.config-code :deep(.comment) {
  color: #6a9955;
}

.config-code :deep(.section) {
  color: #569cd6;
  font-weight: bold;
}

.config-code :deep(.key) {
  color: #9cdcfe;
}

.config-code :deep(.value) {
  color: #ce9178;
}

.preview-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-color);
  display: flex;
  justify-content: center;
}
</style>
