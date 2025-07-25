<script setup lang="ts">
import { computed } from 'vue'
import { useFileStore } from '../../stores/fileStore'
import { useRenameStore } from '../../stores/renameStore'
import { useRenameEngine } from '../../composables/useRenameEngine'

const fileStore = useFileStore()
const renameStore = useRenameStore()
const { checkConflicts, validateParams } = useRenameEngine()

// 计算预览统计信息
const previewStats = computed(() => {
  const files = fileStore.files
  const totalFiles = files.length
  const changedFiles = files.filter(file => file.previewName && file.previewName !== file.name).length
  const unchangedFiles = totalFiles - changedFiles
  
  return {
    total: totalFiles,
    changed: changedFiles,
    unchanged: unchangedFiles,
    hasChanges: changedFiles > 0
  }
})

// 检查冲突和验证
const validationResult = computed(() => validateParams())
const conflictResult = computed(() => checkConflicts())

// 预览文件列表（限制显示数量以提高性能）
const previewFiles = computed(() => {
  return fileStore.files.slice(0, 100) // 只显示前100个文件
})

const hasMoreFiles = computed(() => fileStore.files.length > 100)

// 获取文件状态类
function getFileStatusClass(file: any): string {
  if (!file.previewName) return 'no-preview'
  if (file.previewName === file.name) return 'unchanged'
  return 'changed'
}

// 获取文件状态图标
function getFileStatusIcon(file: any): string {
  if (!file.previewName) return '❓'
  if (file.previewName === file.name) return '➖'
  return '✏️'
}

// 获取文件状态文本
function getFileStatusText(file: any): string {
  if (!file.previewName) return '无预览'
  if (file.previewName === file.name) return '无变化'
  return '已修改'
}
</script>

<template>
  <div class="preview-panel">
    <!-- 预览头部 -->
    <div class="preview-header">
      <h3 class="preview-title">
        <span class="preview-icon">👁️</span>
        重命名预览
      </h3>
      
      <!-- 预览统计 -->
      <div class="preview-stats">
        <div class="stat-item">
          <span class="stat-label">总计:</span>
          <span class="stat-value">{{ previewStats.total }}</span>
        </div>
        <div class="stat-item success">
          <span class="stat-label">将修改:</span>
          <span class="stat-value">{{ previewStats.changed }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">无变化:</span>
          <span class="stat-value">{{ previewStats.unchanged }}</span>
        </div>
      </div>
    </div>

    <!-- 验证和冲突提示 -->
    <div v-if="!validationResult.isValid || conflictResult.hasConflicts" class="validation-alerts">
      <div v-if="!validationResult.isValid" class="alert alert-warning">
        <span class="alert-icon">⚠️</span>
        <div class="alert-content">
          <div class="alert-title">参数验证失败</div>
          <ul class="alert-list">
            <li v-for="error in validationResult.errors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>

      <div v-if="conflictResult.hasConflicts" class="alert alert-error">
        <span class="alert-icon">❌</span>
        <div class="alert-content">
          <div class="alert-title">发现重名冲突</div>
          <ul class="alert-list">
            <li v-for="conflict in conflictResult.conflicts" :key="conflict">{{ conflict }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- 预览状态 -->
    <div v-if="!previewStats.hasChanges && previewStats.total > 0" class="no-changes-message">
      <span class="message-icon">ℹ️</span>
      <span class="message-text">当前设置不会对文件名产生任何更改</span>
    </div>

    <!-- 预览列表 -->
    <div v-if="previewStats.hasChanges" class="preview-list">
      <div class="list-header">
        <div class="header-item">状态</div>
        <div class="header-item">原文件名</div>
        <div class="header-item">新文件名</div>
      </div>

      <div class="list-content">
        <div
          v-for="file in previewFiles"
          :key="file.id"
          :class="['list-item', getFileStatusClass(file)]"
        >
          <div class="item-status">
            <span class="status-icon">{{ getFileStatusIcon(file) }}</span>
            <span class="status-text">{{ getFileStatusText(file) }}</span>
          </div>
          
          <div class="item-original">
            <span class="file-name" :title="file.name">{{ file.name }}</span>
          </div>
          
          <div class="item-preview">
            <span 
              v-if="file.previewName && file.previewName !== file.name"
              class="file-name preview" 
              :title="file.previewName"
            >
              {{ file.previewName }}
            </span>
            <span v-else class="no-change">-</span>
          </div>
        </div>

        <!-- 更多文件提示 -->
        <div v-if="hasMoreFiles" class="more-files-notice">
          <span class="notice-icon">📄</span>
          <span class="notice-text">
            还有 {{ fileStore.files.length - 100 }} 个文件未显示，执行时将处理所有文件
          </span>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-if="previewStats.total === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <div class="empty-text">暂无文件</div>
      <div class="empty-hint">请先添加要重命名的文件</div>
    </div>

    <!-- 预览操作 -->
    <div v-if="previewStats.total > 0" class="preview-actions">
      <div class="action-info">
        <span v-if="renameStore.previewUpdateTime" class="update-time">
          上次更新: {{ new Date(renameStore.previewUpdateTime).toLocaleTimeString() }}
        </span>
      </div>
      
      <div class="action-buttons">
        <button
          class="btn btn-sm"
          @click="$emit('refresh-preview')"
          :disabled="!renameStore.hasValidParams"
        >
          🔄 刷新预览
        </button>
        
        <button
          class="btn btn-sm btn-primary"
          @click="$emit('execute-rename')"
          :disabled="!previewStats.hasChanges || !validationResult.isValid || conflictResult.hasConflicts"
        >
          ✅ 执行重命名
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.preview-panel {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  background: var(--color-background-primary);
  border: 1px solid var(--color-border-primary);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  max-height: 600px;
  overflow: hidden;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);

  .preview-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin: 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);

    .preview-icon {
      font-size: var(--font-size-xl);
    }
  }

  .preview-stats {
    display: flex;
    gap: var(--spacing-md);

    .stat-item {
      display: flex;
      align-items: center;
      gap: var(--spacing-xs);
      font-size: var(--font-size-sm);

      .stat-label {
        color: var(--color-text-secondary);
      }

      .stat-value {
        font-weight: var(--font-weight-semibold);
        color: var(--color-text-primary);
      }

      &.success .stat-value {
        color: var(--color-success);
      }
    }
  }
}

.validation-alerts {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);

  .alert {
    display: flex;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border-radius: var(--radius-md);
    font-size: var(--font-size-sm);

    &.alert-warning {
      background: rgba(255, 149, 0, 0.1);
      border: 1px solid rgba(255, 149, 0, 0.2);
      color: #ff9500;
    }

    &.alert-error {
      background: rgba(255, 59, 48, 0.1);
      border: 1px solid rgba(255, 59, 48, 0.2);
      color: var(--color-error);
    }

    .alert-icon {
      flex-shrink: 0;
      font-size: var(--font-size-base);
    }

    .alert-content {
      flex: 1;

      .alert-title {
        font-weight: var(--font-weight-semibold);
        margin-bottom: var(--spacing-xs);
      }

      .alert-list {
        margin: 0;
        padding-left: var(--spacing-md);

        li {
          margin-bottom: var(--spacing-xs);
        }
      }
    }
  }
}

.no-changes-message {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md);
  background: var(--color-background-secondary);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);

  .message-icon {
    font-size: var(--font-size-base);
  }
}

.preview-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;

  .list-header {
    display: grid;
    grid-template-columns: 100px 1fr 1fr;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    background: var(--color-background-secondary);
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);

    .header-item {
      padding: var(--spacing-xs) 0;
    }
  }

  .list-content {
    flex: 1;
    overflow-y: auto;
    border: 1px solid var(--color-border-secondary);
    border-top: none;
    border-radius: 0 0 var(--radius-md) var(--radius-md);

    .list-item {
      display: grid;
      grid-template-columns: 100px 1fr 1fr;
      gap: var(--spacing-sm);
      padding: var(--spacing-sm) var(--spacing-md);
      border-bottom: 1px solid var(--color-border-secondary);
      font-size: var(--font-size-sm);

      &:last-child {
        border-bottom: none;
      }

      &.changed {
        background: rgba(52, 199, 89, 0.05);
      }

      &.unchanged {
        background: var(--color-background-primary);
        opacity: 0.7;
      }

      &.no-preview {
        background: rgba(255, 149, 0, 0.05);
      }

      .item-status {
        display: flex;
        align-items: center;
        gap: var(--spacing-xs);

        .status-icon {
          font-size: var(--font-size-sm);
        }

        .status-text {
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
        }
      }

      .item-original,
      .item-preview {
        display: flex;
        align-items: center;
        min-width: 0;

        .file-name {
          overflow: hidden;
          text-overflow: ellipsis;
          white-space: nowrap;
          font-family: var(--font-mono);

          &.preview {
            color: var(--color-primary);
            font-weight: var(--font-weight-medium);
          }
        }

        .no-change {
          color: var(--color-text-tertiary);
          font-style: italic;
        }
      }
    }

    .more-files-notice {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      padding: var(--spacing-md);
      background: var(--color-background-secondary);
      color: var(--color-text-secondary);
      font-size: var(--font-size-sm);
      text-align: center;
      border-top: 1px solid var(--color-border-secondary);

      .notice-icon {
        font-size: var(--font-size-base);
      }
    }
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-3xl);
  text-align: center;

  .empty-icon {
    font-size: 48px;
    margin-bottom: var(--spacing-lg);
    opacity: 0.5;
  }

  .empty-text {
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-medium);
    color: var(--color-text-secondary);
    margin-bottom: var(--spacing-sm);
  }

  .empty-hint {
    font-size: var(--font-size-sm);
    color: var(--color-text-tertiary);
  }
}

.preview-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--spacing-md);
  padding-top: var(--spacing-md);
  border-top: 1px solid var(--color-border-secondary);

  .action-info {
    .update-time {
      font-size: var(--font-size-xs);
      color: var(--color-text-tertiary);
    }
  }

  .action-buttons {
    display: flex;
    gap: var(--spacing-sm);
  }
}
</style>
