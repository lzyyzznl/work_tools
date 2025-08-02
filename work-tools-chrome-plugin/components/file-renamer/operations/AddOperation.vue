<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRenameStore } from '../../../stores/renameStore'
import { useRenameEngine } from '../../../composables/useRenameEngine'

const renameStore = useRenameStore()
const { generatePreview } = useRenameEngine()

const text = computed({
  get: () => renameStore.addParams.text,
  set: (value: string) => {
    renameStore.updateAddParams({ text: value })
  }
})

const isPrefix = computed({
  get: () => renameStore.addParams.isPrefix,
  set: (value: boolean) => {
    renameStore.updateAddParams({ isPrefix: value })
  }
})

// 自动预览监听
watch(
  [text, isPrefix],
  () => {
    if (renameStore.isAutoPreview && renameStore.hasValidParams) {
      generatePreview()
    }
  },
  { immediate: false }
)

function clearParams() {
  text.value = ''
}

function togglePosition() {
  isPrefix.value = !isPrefix.value
}

// 常用前缀/后缀预设
const presets = {
  prefix: [
    { label: '日期前缀', value: new Date().toISOString().split('T')[0] + '_' },
    { label: '编号前缀', value: 'No.' },
    { label: '备份前缀', value: 'backup_' },
    { label: '新建前缀', value: 'new_' }
  ],
  suffix: [
    { label: '备份后缀', value: '_backup' },
    { label: '副本后缀', value: '_copy' },
    { label: '编辑后缀', value: '_edited' },
    { label: '最终后缀', value: '_final' }
  ]
}

function applyPreset(value: string) {
  text.value = value
}
</script>

<template>
  <div class="add-operation">
    <div class="operation-header">
      <h3 class="operation-title">
        <span class="operation-icon">➕</span>
        添加前缀/后缀
      </h3>
      <p class="operation-description">
        在文件名的开头或结尾添加指定的文本内容
      </p>
    </div>

    <div class="operation-form">
      <!-- 位置选择 -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">添加位置:</label>
          <div class="radio-group">
            <label class="radio-label">
              <input
                type="radio"
                :checked="isPrefix"
                @change="isPrefix = true"
                class="radio-input"
              />
              <span class="radio-text">前缀 (文件名前)</span>
            </label>
            <label class="radio-label">
              <input
                type="radio"
                :checked="!isPrefix"
                @change="isPrefix = false"
                class="radio-input"
              />
              <span class="radio-text">后缀 (扩展名前)</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-sm btn-icon"
            @click="togglePosition"
            title="切换前缀/后缀"
          >
            ⇄
          </button>
        </div>
      </div>

      <!-- 文本输入 -->
      <div class="form-row">
        <div class="form-group">
          <label for="add-text" class="form-label">
            {{ isPrefix ? '前缀' : '后缀' }}文本:
          </label>
          <input
            id="add-text"
            v-model="text"
            type="text"
            class="form-input"
            :placeholder="`输入要添加的${isPrefix ? '前缀' : '后缀'}文本`"
            autocomplete="off"
          />
        </div>
      </div>

      <!-- 预设选项 -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">常用预设:</label>
          <div class="preset-buttons">
            <button
              v-for="preset in isPrefix ? presets.prefix : presets.suffix"
              :key="preset.label"
              class="btn btn-sm btn-preset"
              @click="applyPreset(preset.value)"
              :title="`应用: ${preset.value}`"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="form-actions-row">
        <button
          class="btn btn-sm"
          @click="clearParams"
          :disabled="!text"
        >
          🗑️ 清空
        </button>

        <div class="form-tips">
          <span class="tip-text">
            💡 {{ isPrefix ? '前缀会添加到文件名开头' : '后缀会添加到扩展名之前' }}
          </span>
        </div>
      </div>
    </div>

    <!-- 参数验证提示 -->
    <div v-if="!text && renameStore.currentMode === 'add'" class="validation-message">
      ⚠️ 请输入要添加的文本内容
    </div>

    <!-- 预览示例 -->
    <div v-if="text" class="preview-example">
      <h4 class="example-title">预览示例:</h4>
      <div class="example-content">
        <div class="example-item">
          <span class="example-label">原文件名:</span>
          <span class="example-original">document.txt</span>
        </div>
        <div class="example-item">
          <span class="example-label">新文件名:</span>
          <span class="example-new">
            {{ isPrefix ? `${text}document.txt` : `document${text}.txt` }}
          </span>
        </div>
      </div>
    </div>

    <!-- 使用示例 -->
    <div class="operation-examples">
      <h4 class="examples-title">使用示例:</h4>
      <div class="examples-list">
        <div class="example-item">
          <span class="example-label">日期前缀:</span>
          <span class="example-content">"2024-01-15_" → 2024-01-15_document.txt</span>
        </div>
        <div class="example-item">
          <span class="example-label">备份后缀:</span>
          <span class="example-content">"_backup" → document_backup.txt</span>
        </div>
        <div class="example-item">
          <span class="example-label">版本标记:</span>
          <span class="example-content">"_v2" → document_v2.txt</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.add-operation {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.operation-header {
  .operation-title {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    margin: 0 0 var(--spacing-xs) 0;
    font-size: var(--font-size-lg);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);

    .operation-icon {
      font-size: var(--font-size-xl);
    }
  }

  .operation-description {
    margin: 0;
    font-size: var(--font-size-sm);
    color: var(--color-text-secondary);
    line-height: 1.4;
  }
}

.operation-form {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);

  .form-row {
    display: flex;
    align-items: end;
    gap: var(--spacing-md);

    .form-group {
      flex: 1;
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);

      .form-label {
        font-size: var(--font-size-sm);
        font-weight: var(--font-weight-medium);
        color: var(--color-text-primary);
      }

      .form-input {
        padding: var(--spacing-sm) var(--spacing-md);
        border: 1px solid var(--color-border-primary);
        border-radius: var(--radius-md);
        font-size: var(--font-size-sm);
        transition: border-color var(--transition-fast);

        &:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
        }

        &::placeholder {
          color: var(--color-text-tertiary);
        }
      }

      .radio-group {
        display: flex;
        gap: var(--spacing-md);

        .radio-label {
          display: flex;
          align-items: center;
          gap: var(--spacing-xs);
          cursor: pointer;
          user-select: none;

          .radio-input {
            margin: 0;
          }

          .radio-text {
            font-size: var(--font-size-sm);
            color: var(--color-text-primary);
          }
        }
      }

      .preset-buttons {
        display: flex;
        flex-wrap: wrap;
        gap: var(--spacing-xs);

        .btn-preset {
          font-size: var(--font-size-xs);
          padding: var(--spacing-xs) var(--spacing-sm);
          background: var(--color-background-secondary);
          border: 1px solid var(--color-border-secondary);

          &:hover {
            background: var(--color-background-tertiary);
            border-color: var(--color-primary);
          }
        }
      }
    }

    .form-actions {
      display: flex;
      align-items: center;
      padding-bottom: var(--spacing-sm);

      .btn-icon {
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: var(--font-size-lg);
        font-weight: bold;
      }
    }
  }

  .form-actions-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: var(--spacing-md);

    .form-tips {
      .tip-text {
        font-size: var(--font-size-xs);
        color: var(--color-text-tertiary);
      }
    }
  }
}

.validation-message {
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(255, 149, 0, 0.1);
  color: #ff9500;
  border: 1px solid rgba(255, 149, 0, 0.2);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
}

.preview-example {
  padding: var(--spacing-md);
  background: var(--color-background-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-secondary);

  .example-title {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .example-content {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    .example-item {
      display: flex;
      gap: var(--spacing-sm);
      font-size: var(--font-size-sm);

      .example-label {
        min-width: 80px;
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
      }

      .example-original {
        color: var(--color-text-tertiary);
        font-family: var(--font-mono);
      }

      .example-new {
        color: var(--color-primary);
        font-family: var(--font-mono);
        font-weight: var(--font-weight-medium);
      }
    }
  }
}

.operation-examples {
  .examples-title {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .examples-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-xs);

    .example-item {
      display: flex;
      gap: var(--spacing-sm);
      font-size: var(--font-size-xs);

      .example-label {
        min-width: 80px;
        color: var(--color-text-secondary);
        font-weight: var(--font-weight-medium);
      }

      .example-content {
        color: var(--color-text-tertiary);
        font-family: var(--font-mono);
      }
    }
  }
}
</style>
