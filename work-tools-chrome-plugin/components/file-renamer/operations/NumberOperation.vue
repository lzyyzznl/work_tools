<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRenameStore } from '../../../stores/renameStore'
import { useRenameEngine } from '../../../composables/useRenameEngine'
import { useFileStore } from '../../../stores/fileStore'

const renameStore = useRenameStore()
const fileStore = useFileStore()
const { generatePreview } = useRenameEngine()

const start = computed({
  get: () => renameStore.numberParams.start,
  set: (value: number) => {
    renameStore.updateNumberParams({ start: Math.max(0, value) })
  }
})

const digits = computed({
  get: () => renameStore.numberParams.digits,
  set: (value: number) => {
    renameStore.updateNumberParams({ digits: Math.max(1, Math.min(10, value)) })
  }
})

const step = computed({
  get: () => renameStore.numberParams.step,
  set: (value: number) => {
    renameStore.updateNumberParams({ step: Math.max(1, value) })
  }
})

const separator = computed({
  get: () => renameStore.numberParams.separator,
  set: (value: string) => {
    renameStore.updateNumberParams({ separator: value })
  }
})

const isPrefix = computed({
  get: () => renameStore.numberParams.isPrefix,
  set: (value: boolean) => {
    renameStore.updateNumberParams({ isPrefix: value })
  }
})

// 自动预览监听
watch(
  [start, digits, step, separator, isPrefix],
  () => {
    if (renameStore.isAutoPreview && renameStore.hasValidParams) {
      generatePreview()
    }
  },
  { immediate: false }
)

function resetParams() {
  start.value = 1
  digits.value = 3
  step.value = 1
  separator.value = '_'
  isPrefix.value = true
}

function togglePosition() {
  isPrefix.value = !isPrefix.value
}

// 预设配置
const presets = [
  { label: '标准编号', config: { start: 1, digits: 3, step: 1, separator: '_' } },
  { label: '两位编号', config: { start: 1, digits: 2, step: 1, separator: '_' } },
  { label: '从零开始', config: { start: 0, digits: 3, step: 1, separator: '_' } },
  { label: '间隔编号', config: { start: 10, digits: 2, step: 10, separator: '-' } },
  { label: '无分隔符', config: { start: 1, digits: 4, step: 1, separator: '' } }
]

function applyPreset(config: any) {
  start.value = config.start
  digits.value = config.digits
  step.value = config.step
  separator.value = config.separator
}

// 计算预览范围
const previewNumbers = computed(() => {
  const count = Math.min(fileStore.files.length, 5)
  const numbers = []
  for (let i = 0; i < count; i++) {
    const num = start.value + (i * step.value)
    numbers.push(num.toString().padStart(digits.value, '0'))
  }
  return numbers
})
</script>

<template>
  <div class="number-operation">
    <div class="operation-header">
      <h3 class="operation-title">
        <span class="operation-icon">🔢</span>
        批量添加序号
      </h3>
      <p class="operation-description">
        为文件名添加自动递增的序号，支持自定义起始数字、位数和步长
      </p>
    </div>

    <div class="operation-form">
      <!-- 位置选择 -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">序号位置:</label>
          <div class="radio-group">
            <label class="radio-label">
              <input
                type="radio"
                :checked="isPrefix"
                @change="isPrefix = true"
                class="radio-input"
              />
              <span class="radio-text">前缀</span>
            </label>
            <label class="radio-label">
              <input
                type="radio"
                :checked="!isPrefix"
                @change="isPrefix = false"
                class="radio-input"
              />
              <span class="radio-text">后缀</span>
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

      <!-- 数字参数 -->
      <div class="form-row">
        <div class="form-group">
          <label for="start-number" class="form-label">起始数字:</label>
          <input
            id="start-number"
            v-model.number="start"
            type="number"
            class="form-input"
            min="0"
            max="9999"
            step="1"
          />
        </div>

        <div class="form-group">
          <label for="digits" class="form-label">数字位数:</label>
          <input
            id="digits"
            v-model.number="digits"
            type="number"
            class="form-input"
            min="1"
            max="10"
            step="1"
          />
        </div>

        <div class="form-group">
          <label for="step" class="form-label">步长:</label>
          <input
            id="step"
            v-model.number="step"
            type="number"
            class="form-input"
            min="1"
            max="100"
            step="1"
          />
        </div>

        <div class="form-group">
          <label for="separator" class="form-label">分隔符:</label>
          <input
            id="separator"
            v-model="separator"
            type="text"
            class="form-input"
            placeholder="如: _ - ."
            maxlength="3"
          />
        </div>
      </div>

      <!-- 预设配置 -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">快速配置:</label>
          <div class="preset-buttons">
            <button
              v-for="preset in presets"
              :key="preset.label"
              class="btn btn-sm btn-preset"
              @click="applyPreset(preset.config)"
              :title="`应用: ${preset.label}`"
            >
              {{ preset.label }}
            </button>
          </div>
        </div>
      </div>

      <div class="form-actions-row">
        <button class="btn btn-sm" @click="resetParams">
          🔄 重置
        </button>

        <div class="form-tips">
          <span class="tip-text">
            💡 序号会按文件在列表中的顺序分配
          </span>
        </div>
      </div>
    </div>

    <!-- 序号预览 -->
    <div v-if="previewNumbers.length > 0" class="preview-section">
      <h4 class="preview-title">序号预览:</h4>
      <div class="preview-content">
        <div class="preview-numbers">
          <span
            v-for="(number, index) in previewNumbers"
            :key="index"
            class="preview-number"
          >
            {{ isPrefix ? `${number}${separator}` : `${separator}${number}` }}
          </span>
          <span v-if="fileStore.files.length > 5" class="preview-more">
            ... (共 {{ fileStore.files.length }} 个文件)
          </span>
        </div>
      </div>
    </div>

    <!-- 完整示例 -->
    <div class="preview-example">
      <h4 class="example-title">完整示例:</h4>
      <div class="example-content">
        <div class="example-item">
          <span class="example-label">原文件名:</span>
          <span class="example-original">document.txt</span>
        </div>
        <div class="example-item">
          <span class="example-label">新文件名:</span>
          <span class="example-new">
            {{
              isPrefix
                ? `${start.toString().padStart(digits, '0')}${separator}document.txt`
                : `document${separator}${start.toString().padStart(digits, '0')}.txt`
            }}
          </span>
        </div>
      </div>
    </div>

    <!-- 使用示例 -->
    <div class="operation-examples">
      <h4 class="examples-title">使用示例:</h4>
      <div class="examples-list">
        <div class="example-item">
          <span class="example-label">标准编号:</span>
          <span class="example-content">001_, 002_, 003_ ...</span>
        </div>
        <div class="example-item">
          <span class="example-label">从10开始:</span>
          <span class="example-content">010_, 011_, 012_ ...</span>
        </div>
        <div class="example-item">
          <span class="example-label">步长为5:</span>
          <span class="example-content">001_, 006_, 011_ ...</span>
        </div>
        <div class="example-item">
          <span class="example-label">后缀模式:</span>
          <span class="example-content">_001, _002, _003 ...</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.number-operation {
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

.preview-section {
  padding: var(--spacing-md);
  background: var(--color-background-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-secondary);

  .preview-title {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .preview-content {
    .preview-numbers {
      display: flex;
      flex-wrap: wrap;
      gap: var(--spacing-xs);
      align-items: center;

      .preview-number {
        padding: var(--spacing-xs) var(--spacing-sm);
        background: var(--color-primary);
        color: white;
        border-radius: var(--radius-sm);
        font-family: var(--font-mono);
        font-size: var(--font-size-xs);
        font-weight: var(--font-weight-medium);
      }

      .preview-more {
        color: var(--color-text-tertiary);
        font-size: var(--font-size-xs);
        font-style: italic;
      }
    }
  }
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
