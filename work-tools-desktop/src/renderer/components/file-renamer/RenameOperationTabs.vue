<script setup lang="ts">
import { computed } from 'vue'
import { useRenameStore } from '../../stores/renameStore'
import { useRenameEngine } from '../../composables/useRenameEngine'
import ReplaceOperation from './operations/ReplaceOperation.vue'
import AddOperation from './operations/AddOperation.vue'
import NumberOperation from './operations/NumberOperation.vue'
import DeleteOperation from './operations/DeleteOperation.vue'

const renameStore = useRenameStore()
const { generatePreview } = useRenameEngine()

const operationTabs = [
  {
    key: 'replace',
    label: '字符串替换',
    icon: '🔄',
    component: ReplaceOperation
  },
  {
    key: 'add',
    label: '添加前缀/后缀',
    icon: '➕',
    component: AddOperation
  },
  {
    key: 'number',
    label: '批量添加序号',
    icon: '🔢',
    component: NumberOperation
  },
  {
    key: 'delete',
    label: '删除字符',
    icon: '✂️',
    component: DeleteOperation
  }
]

const currentTab = computed({
  get: () => renameStore.currentMode,
  set: (value) => {
    renameStore.setMode(value)
    if (renameStore.isAutoPreview) {
      generatePreview()
    }
  }
})

const currentComponent = computed(() => {
  const tab = operationTabs.find(t => t.key === currentTab.value)
  return tab?.component || ReplaceOperation
})
</script>

<template>
  <div class="rename-operation-tabs">
    <!-- 标签页导航 -->
    <div class="tab-nav">
      <button
        v-for="tab in operationTabs"
        :key="tab.key"
        :class="['tab-button', { active: currentTab === tab.key }]"
        @click="currentTab = tab.key"
      >
        <span class="tab-icon">{{ tab.icon }}</span>
        <span class="tab-label">{{ tab.label }}</span>
      </button>
    </div>

    <!-- 标签页内容 -->
    <div class="tab-content">
      <component :is="currentComponent" />
    </div>

    <!-- 预览控制 -->
    <div class="preview-controls">
      <label class="checkbox-label">
        <input
          type="checkbox"
          v-model="renameStore.isAutoPreview"
          class="checkbox"
        />
        <span class="checkbox-text">自动预览</span>
      </label>
      
      <button
        v-if="!renameStore.isAutoPreview"
        class="btn btn-sm"
        @click="generatePreview"
        :disabled="!renameStore.hasValidParams"
      >
        🔄 手动预览
      </button>
      
      <div class="preview-info">
        <span v-if="renameStore.previewUpdateTime" class="preview-time">
          上次预览: {{ new Date(renameStore.previewUpdateTime).toLocaleTimeString() }}
        </span>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.rename-operation-tabs {
  background: var(--color-background-tertiary);
  border-bottom: 1px solid var(--color-border-primary);
}

.tab-nav {
  display: flex;
  padding: var(--spacing-sm) var(--spacing-lg) 0;
  gap: var(--spacing-xs);
  overflow-x: auto;

  .tab-button {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    padding: var(--spacing-sm) var(--spacing-md);
    border: none;
    border-radius: var(--radius-md) var(--radius-md) 0 0;
    background: var(--color-background-secondary);
    color: var(--color-text-secondary);
    cursor: pointer;
    transition: all var(--transition-fast);
    white-space: nowrap;
    font-size: var(--font-size-sm);
    font-weight: var(--font-weight-medium);

    &:hover {
      background: var(--color-background-primary);
      color: var(--color-text-primary);
    }

    &.active {
      background: var(--color-primary);
      color: white;
      font-weight: var(--font-weight-semibold);
    }

    .tab-icon {
      font-size: var(--font-size-base);
    }

    .tab-label {
      font-size: var(--font-size-sm);
    }
  }
}

.tab-content {
  background: var(--color-background-primary);
  padding: var(--spacing-lg);
  min-height: 120px;
}

.preview-controls {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-background-secondary);
  border-top: 1px solid var(--color-border-secondary);
  font-size: var(--font-size-sm);

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    cursor: pointer;
    user-select: none;

    .checkbox {
      margin: 0;
    }

    .checkbox-text {
      color: var(--color-text-primary);
      font-weight: var(--font-weight-medium);
    }
  }

  .preview-info {
    margin-left: auto;

    .preview-time {
      color: var(--color-text-tertiary);
      font-size: var(--font-size-xs);
    }
  }
}
</style>
