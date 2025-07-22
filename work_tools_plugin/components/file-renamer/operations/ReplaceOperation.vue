<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRenameStore } from '../../../stores/renameStore'
import { useRenameEngine } from '../../../composables/useRenameEngine'

const renameStore = useRenameStore()
const { generatePreview } = useRenameEngine()

const fromStr = computed({
  get: () => renameStore.replaceParams.fromStr,
  set: (value: string) => {
    renameStore.updateReplaceParams({ fromStr: value })
  }
})

const toStr = computed({
  get: () => renameStore.replaceParams.toStr,
  set: (value: string) => {
    renameStore.updateReplaceParams({ toStr: value })
  }
})

// 自动预览监听
watch(
  [fromStr, toStr],
  () => {
    if (renameStore.isAutoPreview && renameStore.hasValidParams) {
      generatePreview()
    }
  },
  { immediate: false }
)

function clearParams() {
  fromStr.value = ''
  toStr.value = ''
}

function swapParams() {
  const temp = fromStr.value
  fromStr.value = toStr.value
  toStr.value = temp
}
</script>

<template>
  <div class="replace-operation">
    <div class="operation-header">
      <h3 class="operation-title">
        <span class="operation-icon">🔄</span>
        字符串替换
      </h3>
      <p class="operation-description">
        将文件名中的指定字符串替换为新的字符串
      </p>
    </div>

    <div class="operation-form">
      <div class="form-row">
        <div class="form-group">
          <label for="from-str" class="form-label">查找字符串:</label>
          <input
            id="from-str"
            v-model="fromStr"
            type="text"
            class="form-input"
            placeholder="要替换的字符串"
            autocomplete="off"
          />
        </div>

        <div class="form-actions">
          <button
            class="btn btn-sm btn-icon"
            @click="swapParams"
            title="交换查找和替换内容"
            :disabled="!fromStr && !toStr"
          >
            ⇄
          </button>
        </div>

        <div class="form-group">
          <label for="to-str" class="form-label">替换为:</label>
          <input
            id="to-str"
            v-model="toStr"
            type="text"
            class="form-input"
            placeholder="新的字符串（留空表示删除）"
            autocomplete="off"
          />
        </div>
      </div>

      <div class="form-actions-row">
        <button
          class="btn btn-sm"
          @click="clearParams"
          :disabled="!fromStr && !toStr"
        >
          🗑️ 清空
        </button>

        <div class="form-tips">
          <span class="tip-text">
            💡 支持精确匹配，区分大小写
          </span>
        </div>
      </div>
    </div>

    <!-- 参数验证提示 -->
    <div v-if="fromStr && !renameStore.hasValidParams" class="validation-message">
      ⚠️ 请输入要查找的字符串
    </div>

    <!-- 使用示例 -->
    <div class="operation-examples">
      <h4 class="examples-title">使用示例:</h4>
      <div class="examples-list">
        <div class="example-item">
          <span class="example-label">删除前缀:</span>
          <span class="example-content">查找 "IMG_" → 替换为 ""</span>
        </div>
        <div class="example-item">
          <span class="example-label">替换分隔符:</span>
          <span class="example-content">查找 "_" → 替换为 "-"</span>
        </div>
        <div class="example-item">
          <span class="example-label">修改扩展名:</span>
          <span class="example-content">查找 ".txt" → 替换为 ".md"</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.replace-operation {
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
