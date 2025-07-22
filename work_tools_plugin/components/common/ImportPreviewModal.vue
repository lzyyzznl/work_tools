<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  modelValue: boolean
  previewData: any
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'confirm'): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const isVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

const preview = computed(() => props.previewData?.preview)
const stats = computed(() => props.previewData?.stats)

function handleConfirm() {
  emit('confirm')
}

function handleCancel() {
  emit('cancel')
}
</script>

<template>
  <div v-if="isVisible" class="modal-overlay" @click="handleCancel">
    <div class="modal-container" @click.stop>
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <span class="modal-icon">📥</span>
          导入数据预览
        </h2>
        <button class="modal-close" @click="handleCancel">×</button>
      </div>

      <!-- 模态框内容 -->
      <div class="modal-content">
        <div v-if="preview && stats" class="preview-content">
          <!-- 导入统计 -->
          <div class="import-stats">
            <h3>导入统计</h3>
            <div class="stats-grid">
              <div class="stat-item">
                <span class="stat-label">版本:</span>
                <span class="stat-value">{{ stats.version }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">文件数量:</span>
                <span class="stat-value">{{ stats.fileCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">历史记录:</span>
                <span class="stat-value">{{ stats.historyCount }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">包含设置:</span>
                <span class="stat-value">{{ stats.hasSettings ? '是' : '否' }}</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">导入时间:</span>
                <span class="stat-value">{{ stats.importDate }}</span>
              </div>
            </div>
          </div>

          <!-- 数据摘要 -->
          <div class="data-summary">
            <h3>数据摘要</h3>
            <pre class="summary-text">{{ preview.summary }}</pre>
          </div>

          <!-- 文件预览 -->
          <div v-if="preview.filePreview.length > 0" class="data-preview">
            <h3>文件预览 (前5个)</h3>
            <ul class="preview-list">
              <li v-for="file in preview.filePreview" :key="file" class="preview-item">
                {{ file }}
              </li>
            </ul>
            <p v-if="stats.fileCount > 5" class="more-info">
              还有 {{ stats.fileCount - 5 }} 个文件...
            </p>
          </div>

          <!-- 历史记录预览 -->
          <div v-if="preview.historyPreview.length > 0" class="data-preview">
            <h3>历史记录预览 (前3个)</h3>
            <ul class="preview-list">
              <li v-for="history in preview.historyPreview" :key="history" class="preview-item">
                {{ history }}
              </li>
            </ul>
            <p v-if="stats.historyCount > 3" class="more-info">
              还有 {{ stats.historyCount - 3 }} 条历史记录...
            </p>
          </div>

          <!-- 设置预览 -->
          <div v-if="preview.settingsPreview.length > 0" class="data-preview">
            <h3>设置预览</h3>
            <ul class="preview-list">
              <li v-for="setting in preview.settingsPreview" :key="setting" class="preview-item">
                {{ setting }}
              </li>
            </ul>
          </div>

          <!-- 导入选项提醒 -->
          <div class="import-options">
            <h3>导入选项</h3>
            <div class="options-info">
              <div class="option-item">
                <span class="option-label">替换现有文件:</span>
                <span class="option-value">{{ previewData?.options?.replaceExisting ? '是' : '否' }}</span>
              </div>
              <div class="option-item">
                <span class="option-label">合并历史记录:</span>
                <span class="option-value">{{ previewData?.options?.mergeHistory ? '是' : '否' }}</span>
              </div>
              <div class="option-item">
                <span class="option-label">导入设置:</span>
                <span class="option-value">{{ previewData?.options?.importSettings ? '是' : '否' }}</span>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="no-preview">
          <div class="no-preview-icon">📄</div>
          <p>无法预览导入数据</p>
        </div>
      </div>

      <!-- 模态框底部 -->
      <div class="modal-footer">
        <div class="footer-warning">
          <span class="warning-icon">⚠️</span>
          <span class="warning-text">请仔细检查导入数据，确认无误后再执行导入操作</span>
        </div>
        
        <div class="footer-actions">
          <button class="btn" @click="handleCancel">
            取消
          </button>
          <button class="btn btn-primary" @click="handleConfirm">
            确认导入
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: var(--spacing-lg);
}

.modal-container {
  background: var(--color-background-primary);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-primary);
  background: var(--color-background-secondary);

  .modal-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin: 0;
    font-size: var(--font-size-xl);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);

    .modal-icon {
      font-size: var(--font-size-2xl);
    }
  }

  .modal-close {
    width: 32px;
    height: 32px;
    border: none;
    background: none;
    color: var(--color-text-secondary);
    font-size: var(--font-size-xl);
    cursor: pointer;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all var(--transition-fast);

    &:hover {
      background: var(--color-background-tertiary);
      color: var(--color-text-primary);
    }
  }
}

.modal-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.preview-content {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);

  h3 {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-base);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }
}

.import-stats {
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--spacing-sm);

    .stat-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-sm);
      background: var(--color-background-secondary);
      border-radius: var(--radius-sm);

      .stat-label {
        color: var(--color-text-secondary);
        font-size: var(--font-size-sm);
      }

      .stat-value {
        color: var(--color-text-primary);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
      }
    }
  }
}

.data-summary {
  .summary-text {
    background: var(--color-background-secondary);
    padding: var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    white-space: pre-line;
    margin: 0;
    font-family: var(--font-mono);
  }
}

.data-preview {
  .preview-list {
    margin: 0;
    padding: 0;
    list-style: none;

    .preview-item {
      padding: var(--spacing-xs) var(--spacing-sm);
      background: var(--color-background-secondary);
      border-radius: var(--radius-sm);
      margin-bottom: var(--spacing-xs);
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
      font-family: var(--font-mono);
    }
  }

  .more-info {
    margin: var(--spacing-sm) 0 0 0;
    font-size: var(--font-size-sm);
    color: var(--color-text-tertiary);
    font-style: italic;
  }
}

.import-options {
  .options-info {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    .option-item {
      display: flex;
      justify-content: space-between;
      padding: var(--spacing-sm);
      background: var(--color-background-secondary);
      border-radius: var(--radius-sm);

      .option-label {
        color: var(--color-text-secondary);
        font-size: var(--font-size-sm);
      }

      .option-value {
        color: var(--color-text-primary);
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
      }
    }
  }
}

.no-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3xl);
  text-align: center;

  .no-preview-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-lg);
    opacity: 0.5;
  }

  p {
    margin: 0;
    color: var(--color-text-secondary);
    font-size: var(--font-size-base);
  }
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid var(--color-border-primary);
  background: var(--color-background-secondary);

  .footer-warning {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);

    .warning-icon {
      color: #ff9500;
    }

    .warning-text {
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
    }
  }

  .footer-actions {
    display: flex;
    gap: var(--spacing-sm);
  }
}
</style>
