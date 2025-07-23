<script setup lang="ts">
import { ref, computed } from 'vue'
import { useSettings } from '../../composables/useSettings'
import { useErrorHandler } from '../../composables/useErrorHandler'

interface Props {
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const {
  settings,
  settingGroups,
  updateSetting,
  resetCategory,
  resetAllSettings,
  exportSettingsToFile,
  importSettingsFromFile,
  getSettingDescription,
  getSettingDisplayName,
  validateSetting
} = useSettings()

const { handleError, handleSuccess, handleWarning } = useErrorHandler()

const activeTab = ref('interface')
const isResetting = ref(false)
const isImporting = ref(false)

const isVisible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value)
})

function closeModal() {
  isVisible.value = false
}

function switchTab(tabKey: string) {
  activeTab.value = tabKey
}

async function handleResetCategory(category: string) {
  if (isResetting.value) return
  
  isResetting.value = true
  try {
    resetCategory(category as any)
    handleSuccess(`${getGroupTitle(category)}已重置为默认值`, '重置成功')
  } catch (error) {
    handleError(error, '重置设置')
  } finally {
    isResetting.value = false
  }
}

async function handleResetAll() {
  if (isResetting.value) return
  
  if (!confirm('确定要重置所有设置为默认值吗？此操作不可撤销。')) {
    return
  }
  
  isResetting.value = true
  try {
    resetAllSettings()
    handleSuccess('所有设置已重置为默认值', '重置成功')
  } catch (error) {
    handleError(error, '重置所有设置')
  } finally {
    isResetting.value = false
  }
}

async function handleExport() {
  try {
    exportSettingsToFile()
    handleSuccess('设置已导出到文件', '导出成功')
  } catch (error) {
    handleError(error, '导出设置')
  }
}

async function handleImport() {
  if (isImporting.value) return
  
  isImporting.value = true
  try {
    const success = await importSettingsFromFile()
    if (success) {
      handleSuccess('设置已成功导入', '导入成功')
    } else {
      handleWarning('导入失败，请检查文件格式', '导入失败')
    }
  } catch (error) {
    handleError(error, '导入设置')
  } finally {
    isImporting.value = false
  }
}

function getGroupTitle(key: string): string {
  const group = settingGroups.value.find(g => g.key === key)
  return group?.title || key
}

function handleSettingChange(key: string, value: any) {
  if (!validateSetting(key, value)) {
    handleWarning(`设置值无效: ${getSettingDisplayName(key as any)}`, '设置错误')
    return
  }
  
  updateSetting(key as any, value)
}
</script>

<template>
  <div v-if="isVisible" class="modal-overlay" @click="closeModal">
    <div class="modal-container" @click.stop>
      <!-- 模态框头部 -->
      <div class="modal-header">
        <h2 class="modal-title">
          <span class="modal-icon">⚙️</span>
          设置
        </h2>
        <button class="modal-close" @click="closeModal">×</button>
      </div>

      <!-- 模态框内容 -->
      <div class="modal-content">
        <!-- 标签页导航 -->
        <div class="tabs-nav">
          <button
            v-for="group in settingGroups"
            :key="group.key"
            :class="['tab-button', { active: activeTab === group.key }]"
            @click="switchTab(group.key)"
          >
            <span class="tab-icon">{{ group.icon }}</span>
            <span class="tab-label">{{ group.title }}</span>
          </button>
        </div>

        <!-- 标签页内容 -->
        <div class="tabs-content">
          <div
            v-for="group in settingGroups"
            :key="group.key"
            v-show="activeTab === group.key"
            class="tab-panel"
          >
            <div class="settings-group">
              <div class="group-header">
                <h3 class="group-title">
                  <span class="group-icon">{{ group.icon }}</span>
                  {{ group.title }}
                </h3>
                <button
                  class="btn btn-sm"
                  @click="handleResetCategory(group.key)"
                  :disabled="isResetting"
                >
                  🔄 重置
                </button>
              </div>

              <div class="settings-list">
                <div
                  v-for="setting in group.settings"
                  :key="setting.key"
                  class="setting-item"
                >
                  <div class="setting-info">
                    <label class="setting-label">
                      {{ getSettingDisplayName(setting.key as any) }}
                    </label>
                    <p class="setting-description">
                      {{ getSettingDescription(setting.key) }}
                    </p>
                  </div>

                  <div class="setting-control">
                    <!-- 布尔值设置 -->
                    <label
                      v-if="setting.type === 'boolean'"
                      class="switch-label"
                    >
                      <input
                        type="checkbox"
                        :checked="settings[setting.key as keyof typeof settings]"
                        @change="handleSettingChange(setting.key, ($event.target as HTMLInputElement).checked)"
                        class="switch-input"
                      />
                      <span class="switch-slider"></span>
                    </label>

                    <!-- 数字设置 -->
                    <input
                      v-else-if="setting.type === 'number'"
                      type="number"
                      :value="settings[setting.key as keyof typeof settings]"
                      @input="handleSettingChange(setting.key, parseInt(($event.target as HTMLInputElement).value))"
                      :min="setting.min"
                      :max="setting.max"
                      class="number-input"
                    />

                    <!-- 选择设置 -->
                    <select
                      v-else-if="setting.type === 'select'"
                      :value="settings[setting.key as keyof typeof settings]"
                      @change="handleSettingChange(setting.key, ($event.target as HTMLSelectElement).value)"
                      class="select-input"
                    >
                      <option
                        v-for="option in setting.options"
                        :key="option.value"
                        :value="option.value"
                      >
                        {{ option.label }}
                      </option>
                    </select>

                    <!-- 后缀文本 -->
                    <span v-if="setting.suffix" class="setting-suffix">
                      {{ setting.suffix }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模态框底部 -->
      <div class="modal-footer">
        <div class="footer-left">
          <button class="btn" @click="handleImport" :disabled="isImporting">
            📥 导入设置
          </button>
          <button class="btn" @click="handleExport">
            📤 导出设置
          </button>
        </div>
        
        <div class="footer-right">
          <button
            class="btn btn-danger"
            @click="handleResetAll"
            :disabled="isResetting"
          >
            🔄 重置所有
          </button>
          <button class="btn btn-primary" @click="closeModal">
            完成
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
  max-width: 800px;
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
  display: flex;
  overflow: hidden;
}

.tabs-nav {
  width: 200px;
  background: var(--color-background-secondary);
  border-right: 1px solid var(--color-border-primary);
  padding: var(--spacing-md);
  overflow-y: auto;

  .tab-button {
    width: 100%;
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    background: none;
    color: var(--color-text-secondary);
    text-align: left;
    cursor: pointer;
    border-radius: var(--radius-md);
    transition: all var(--transition-fast);
    margin-bottom: var(--spacing-xs);

    &:hover {
      background: var(--color-background-tertiary);
      color: var(--color-text-primary);
    }

    &.active {
      background: var(--color-primary);
      color: white;
    }

    .tab-icon {
      font-size: var(--font-size-base);
    }

    .tab-label {
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-medium);
    }
  }
}

.tabs-content {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
}

.settings-group {
  .group-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: var(--spacing-lg);

    .group-title {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      margin: 0;
      font-size: var(--font-size-lg);
      font-weight: var(--font-weight-semibold);
      color: var(--color-text-primary);

      .group-icon {
        font-size: var(--font-size-xl);
      }
    }
  }

  .settings-list {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-lg);
  }
}

.setting-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--spacing-lg);
  padding: var(--spacing-md);
  border: 1px solid var(--color-border-secondary);
  border-radius: var(--radius-md);
  background: var(--color-background-primary);

  .setting-info {
    flex: 1;
    min-width: 0;

    .setting-label {
      display: block;
      font-size: var(--font-size-sm);
      font-weight: var(--font-weight-semibold);
      color: var(--color-text-primary);
      margin-bottom: var(--spacing-xs);
    }

    .setting-description {
      margin: 0;
      font-size: var(--font-size-xs);
      color: var(--color-text-secondary);
      line-height: 1.4;
    }
  }

  .setting-control {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    flex-shrink: 0;

    .switch-label {
      position: relative;
      display: inline-block;
      width: 44px;
      height: 24px;
      cursor: pointer;

      .switch-input {
        opacity: 0;
        width: 0;
        height: 0;

        &:checked + .switch-slider {
          background-color: var(--color-primary);

          &:before {
            transform: translateX(20px);
          }
        }
      }

      .switch-slider {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-color: var(--color-border-primary);
        transition: var(--transition-fast);
        border-radius: 24px;

        &:before {
          position: absolute;
          content: "";
          height: 18px;
          width: 18px;
          left: 3px;
          bottom: 3px;
          background-color: white;
          transition: var(--transition-fast);
          border-radius: 50%;
        }
      }
    }

    .number-input,
    .select-input {
      min-width: 120px;
      padding: var(--spacing-xs) var(--spacing-sm);
      border: 1px solid var(--color-border-primary);
      border-radius: var(--radius-sm);
      font-size: var(--font-size-sm);
      background: var(--color-background-primary);
      color: var(--color-text-primary);

      &:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.1);
      }
    }

    .setting-suffix {
      font-size: var(--font-size-sm);
      color: var(--color-text-secondary);
    }
  }
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-lg) var(--spacing-xl);
  border-top: 1px solid var(--color-border-primary);
  background: var(--color-background-secondary);

  .footer-left,
  .footer-right {
    display: flex;
    gap: var(--spacing-sm);
  }
}
</style>
