<script setup lang="ts">
import { computed, watch } from 'vue'
import { useRenameStore } from '../../../stores/renameStore'
import { useRenameEngine } from '../../../composables/useRenameEngine'

const renameStore = useRenameStore()
const { generatePreview } = useRenameEngine()

const startPos = computed({
  get: () => renameStore.deleteParams.startPos,
  set: (value: number) => {
    renameStore.updateDeleteParams({ startPos: Math.max(1, value) })
  }
})

const count = computed({
  get: () => renameStore.deleteParams.count,
  set: (value: number) => {
    renameStore.updateDeleteParams({ count: Math.max(1, value) })
  }
})

const fromLeft = computed({
  get: () => renameStore.deleteParams.fromLeft,
  set: (value: boolean) => {
    renameStore.updateDeleteParams({ fromLeft: value })
  }
})

// 自动预览监听
watch(
  [startPos, count, fromLeft],
  () => {
    if (renameStore.isAutoPreview && renameStore.hasValidParams) {
      generatePreview()
    }
  },
  { immediate: false }
)

function resetParams() {
  startPos.value = 1
  count.value = 1
  fromLeft.value = true
}

function toggleDirection() {
  fromLeft.value = !fromLeft.value
}

// 预设配置
const presets = [
  { label: '删除首字符', config: { startPos: 1, count: 1, fromLeft: true } },
  { label: '删除前3字符', config: { startPos: 1, count: 3, fromLeft: true } },
  { label: '删除末字符', config: { startPos: 1, count: 1, fromLeft: false } },
  { label: '删除后3字符', config: { startPos: 1, count: 3, fromLeft: false } },
  { label: '删除中间字符', config: { startPos: 3, count: 2, fromLeft: true } }
]

function applyPreset(config: any) {
  startPos.value = config.startPos
  count.value = config.count
  fromLeft.value = config.fromLeft
}

// 生成示例预览
function generateExample(originalName: string): string {
  const nameWithoutExt = originalName.includes('.') 
    ? originalName.substring(0, originalName.lastIndexOf('.'))
    : originalName
  const ext = originalName.includes('.') 
    ? originalName.substring(originalName.lastIndexOf('.'))
    : ''
  
  let result = nameWithoutExt
  const startIndex = startPos.value - 1
  
  if (fromLeft.value) {
    // 从左侧删除
    if (startIndex < result.length) {
      const endIndex = Math.min(startIndex + count.value, result.length)
      result = result.slice(0, startIndex) + result.slice(endIndex)
    }
  } else {
    // 从右侧删除
    const rightStartIndex = Math.max(0, result.length - startIndex - count.value + 1)
    const rightEndIndex = Math.max(0, result.length - startIndex + 1)
    result = result.slice(0, rightStartIndex) + result.slice(rightEndIndex)
  }
  
  return result + ext
}
</script>

<template>
  <div class="delete-operation">
    <div class="operation-header">
      <h3 class="operation-title">
        <span class="operation-icon">✂️</span>
        删除字符
      </h3>
      <p class="operation-description">
        从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除
      </p>
    </div>

    <div class="operation-form">
      <!-- 删除方向 -->
      <div class="form-row">
        <div class="form-group">
          <label class="form-label">删除方向:</label>
          <div class="radio-group">
            <label class="radio-label">
              <input
                type="radio"
                :checked="fromLeft"
                @change="fromLeft = true"
                class="radio-input"
              />
              <span class="radio-text">从左侧</span>
            </label>
            <label class="radio-label">
              <input
                type="radio"
                :checked="!fromLeft"
                @change="fromLeft = false"
                class="radio-input"
              />
              <span class="radio-text">从右侧</span>
            </label>
          </div>
        </div>

        <div class="form-actions">
          <button
            class="btn btn-sm btn-icon"
            @click="toggleDirection"
            title="切换删除方向"
          >
            ⇄
          </button>
        </div>
      </div>

      <!-- 删除参数 -->
      <div class="form-row">
        <div class="form-group">
          <label for="start-pos" class="form-label">
            {{ fromLeft ? '开始位置:' : '从右数位置:' }}
          </label>
          <input
            id="start-pos"
            v-model.number="startPos"
            type="number"
            class="form-input"
            min="1"
            max="50"
            step="1"
          />
          <span class="form-hint">
            {{ fromLeft ? '第几个字符开始删除' : '从右数第几个位置' }}
          </span>
        </div>

        <div class="form-group">
          <label for="delete-count" class="form-label">删除字符数:</label>
          <input
            id="delete-count"
            v-model.number="count"
            type="number"
            class="form-input"
            min="1"
            max="20"
            step="1"
          />
          <span class="form-hint">要删除的字符数量</span>
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
            💡 {{ fromLeft ? '从左侧计算位置' : '从右侧计算位置' }}，只处理文件名部分
          </span>
        </div>
      </div>
    </div>

    <!-- 删除示例 -->
    <div class="preview-example">
      <h4 class="example-title">删除示例:</h4>
      <div class="example-content">
        <div class="example-item">
          <span class="example-label">原文件名:</span>
          <span class="example-original">IMG_20240115_document.txt</span>
        </div>
        <div class="example-item">
          <span class="example-label">新文件名:</span>
          <span class="example-new">
            {{ generateExample('IMG_20240115_document.txt') }}
          </span>
        </div>
        <div class="example-item">
          <span class="example-label">删除说明:</span>
          <span class="example-description">
            {{ fromLeft 
              ? `从第${startPos}个字符开始删除${count}个字符` 
              : `从右数第${startPos}个位置删除${count}个字符` 
            }}
          </span>
        </div>
      </div>
    </div>

    <!-- 位置指示器 -->
    <div class="position-indicator">
      <h4 class="indicator-title">位置指示 (以 "IMG_20240115_document" 为例):</h4>
      <div class="indicator-content">
        <div class="char-positions">
          <div class="char-row">
            <span class="char-label">字符:</span>
            <div class="chars">
              <span v-for="(char, index) in 'IMG_20240115_document'.split('')" 
                    :key="index" 
                    class="char"
                    :class="{ 
                      highlight: fromLeft 
                        ? (index >= startPos - 1 && index < startPos - 1 + count)
                        : (index >= 'IMG_20240115_document'.length - startPos - count + 1 && 
                           index < 'IMG_20240115_document'.length - startPos + 1)
                    }"
              >
                {{ char }}
              </span>
            </div>
          </div>
          <div class="position-row">
            <span class="char-label">位置:</span>
            <div class="positions">
              <span v-for="(char, index) in 'IMG_20240115_document'.split('')" 
                    :key="index" 
                    class="position"
                    :class="{ 
                      highlight: fromLeft 
                        ? (index >= startPos - 1 && index < startPos - 1 + count)
                        : (index >= 'IMG_20240115_document'.length - startPos - count + 1 && 
                           index < 'IMG_20240115_document'.length - startPos + 1)
                    }"
              >
                {{ fromLeft ? index + 1 : 'IMG_20240115_document'.length - index }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 使用示例 -->
    <div class="operation-examples">
      <h4 class="examples-title">使用示例:</h4>
      <div class="examples-list">
        <div class="example-item">
          <span class="example-label">删除前缀:</span>
          <span class="example-content">位置1，删除4个 → "IMG_" 被删除</span>
        </div>
        <div class="example-item">
          <span class="example-label">删除后缀:</span>
          <span class="example-content">从右数位置1，删除3个 → 删除末尾字符</span>
        </div>
        <div class="example-item">
          <span class="example-label">删除中间:</span>
          <span class="example-content">位置5，删除8个 → 删除日期部分</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.delete-operation {
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
      }

      .form-hint {
        font-size: var(--font-size-xs);
        color: var(--color-text-tertiary);
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

      .example-description {
        color: var(--color-text-secondary);
        font-style: italic;
      }
    }
  }
}

.position-indicator {
  padding: var(--spacing-md);
  background: var(--color-background-secondary);
  border-radius: var(--radius-md);
  border: 1px solid var(--color-border-secondary);

  .indicator-title {
    margin: 0 0 var(--spacing-sm) 0;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
  }

  .indicator-content {
    .char-positions {
      display: flex;
      flex-direction: column;
      gap: var(--spacing-xs);

      .char-row, .position-row {
        display: flex;
        align-items: center;
        gap: var(--spacing-sm);

        .char-label {
          min-width: 40px;
          font-size: var(--font-size-xs);
          color: var(--color-text-secondary);
          font-weight: var(--font-weight-medium);
        }

        .chars, .positions {
          display: flex;
          gap: 1px;

          .char, .position {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 20px;
            height: 24px;
            font-family: var(--font-mono);
            font-size: var(--font-size-xs);
            background: var(--color-background-primary);
            border: 1px solid var(--color-border-secondary);

            &.highlight {
              background: var(--color-error);
              color: white;
              font-weight: var(--font-weight-semibold);
            }
          }
        }
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
