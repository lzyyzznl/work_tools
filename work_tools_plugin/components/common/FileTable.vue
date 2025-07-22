<script setup lang="ts">
import { computed, ref } from 'vue'
import { useFileStore } from '../../stores/fileStore'
import { useFileSystem } from '../../composables/useFileSystem'
import type { FileItem } from '../../types/file'

// Props
interface Props {
  showMatchInfo?: boolean
  showPreview?: boolean
  showSelection?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showMatchInfo: false,
  showPreview: false,
  showSelection: true
})

// 状态管理
const fileStore = useFileStore()
const { formatFileSize } = useFileSystem()

// 本地状态
const sortField = ref<string>('name')
const sortOrder = ref<'asc' | 'desc'>('asc')

// 计算属性
const sortedFiles = computed(() => {
  const files = [...fileStore.files]
  
  files.sort((a, b) => {
    let aValue: any = a[sortField.value as keyof FileItem]
    let bValue: any = b[sortField.value as keyof FileItem]
    
    // 特殊处理不同类型的字段
    if (sortField.value === 'size' || sortField.value === 'lastModified') {
      aValue = Number(aValue)
      bValue = Number(bValue)
    } else {
      aValue = String(aValue).toLowerCase()
      bValue = String(bValue).toLowerCase()
    }
    
    if (aValue < bValue) {
      return sortOrder.value === 'asc' ? -1 : 1
    }
    if (aValue > bValue) {
      return sortOrder.value === 'asc' ? 1 : -1
    }
    return 0
  })
  
  return files
})

// 方法
function handleSort(field: string) {
  if (sortField.value === field) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortField.value = field
    sortOrder.value = 'asc'
  }
}

function handleSelectAll() {
  if (fileStore.selectedFiles.size === fileStore.files.length) {
    fileStore.unselectAllFiles()
  } else {
    fileStore.selectAllFiles()
  }
}

function handleRowClick(file: FileItem) {
  if (props.showSelection) {
    fileStore.toggleFileSelection(file.id)
  }
}

function formatDate(timestamp: number): string {
  return new Date(timestamp).toLocaleString('zh-CN')
}

function getMatchStatusText(file: FileItem): string {
  if (!file.matched) return '未匹配'
  if (file.matchInfo) {
    return `${file.matchInfo.code} (${file.matchInfo.matchedRule})`
  }
  return '已匹配'
}

function getSortIcon(field: string): string {
  if (sortField.value !== field) return '↕️'
  return sortOrder.value === 'asc' ? '↑' : '↓'
}
</script>

<template>
  <div class="file-table-container">
    <div class="table-wrapper">
      <table class="file-table">
        <thead>
          <tr>
            <th v-if="showSelection" class="checkbox-col">
              <input
                type="checkbox"
                :checked="fileStore.selectedFiles.size === fileStore.files.length && fileStore.files.length > 0"
                :indeterminate="fileStore.selectedFiles.size > 0 && fileStore.selectedFiles.size < fileStore.files.length"
                @change="handleSelectAll"
              />
            </th>
            <th class="sortable" @click="handleSort('name')">
              文件名 <span class="sort-icon">{{ getSortIcon('name') }}</span>
            </th>
            <th class="sortable" @click="handleSort('size')">
              大小 <span class="sort-icon">{{ getSortIcon('size') }}</span>
            </th>
            <th class="sortable" @click="handleSort('lastModified')">
              修改时间 <span class="sort-icon">{{ getSortIcon('lastModified') }}</span>
            </th>
            <th v-if="showMatchInfo">匹配状态</th>
            <th v-if="showPreview">预览名称</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="file in sortedFiles"
            :key="file.id"
            :class="{ 
              selected: fileStore.selectedFiles.has(file.id),
              matched: file.matched,
              clickable: showSelection
            }"
            @click="handleRowClick(file)"
          >
            <td v-if="showSelection" class="checkbox-col">
              <input
                type="checkbox"
                :checked="fileStore.selectedFiles.has(file.id)"
                @click.stop
                @change="fileStore.toggleFileSelection(file.id)"
              />
            </td>
            <td class="file-name">
              <span class="file-icon">📄</span>
              <span class="name-text" :title="file.name">{{ file.name }}</span>
            </td>
            <td class="file-size">{{ formatFileSize(file.size) }}</td>
            <td class="file-date">{{ formatDate(file.lastModified) }}</td>
            <td v-if="showMatchInfo" class="match-status" :class="{ matched: file.matched }">
              {{ getMatchStatusText(file) }}
            </td>
            <td v-if="showPreview" class="preview-name">
              <span v-if="file.previewName" :title="file.previewName">
                {{ file.previewName }}
              </span>
              <span v-else class="no-preview">-</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    
    <div v-if="fileStore.files.length === 0" class="empty-state">
      <div class="empty-icon">📁</div>
      <div class="empty-text">暂无文件</div>
      <div class="empty-hint">拖拽文件到此处或点击选择文件</div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.file-table-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.table-wrapper {
  flex: 1;
  overflow: auto;
}

.file-table {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--font-size-sm);

  th, td {
    padding: var(--spacing-sm) var(--spacing-md);
    text-align: left;
    border-bottom: 1px solid var(--color-border-secondary);
  }

  th {
    background: var(--color-background-secondary);
    font-weight: var(--font-weight-semibold);
    color: var(--color-text-primary);
    position: sticky;
    top: 0;
    z-index: 1;

    &.sortable {
      cursor: pointer;
      user-select: none;
      
      &:hover {
        background: var(--color-background-tertiary);
      }
    }
  }

  tr {
    &:hover {
      background: var(--color-background-secondary);
    }

    &.selected {
      background: rgba(0, 122, 255, 0.1);
    }

    &.clickable {
      cursor: pointer;
    }
  }

  .checkbox-col {
    width: 40px;
    text-align: center;
  }

  .file-name {
    display: flex;
    align-items: center;
    gap: var(--spacing-xs);
    min-width: 0;

    .file-icon {
      flex-shrink: 0;
    }

    .name-text {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }

  .file-size {
    width: 80px;
    text-align: right;
    color: var(--color-text-secondary);
  }

  .file-date {
    width: 140px;
    color: var(--color-text-secondary);
  }

  .match-status {
    width: 120px;
    color: var(--color-text-secondary);

    &.matched {
      color: var(--color-success);
      font-weight: var(--font-weight-medium);
    }
  }

  .preview-name {
    color: var(--color-text-secondary);
    font-style: italic;

    .no-preview {
      color: var(--color-text-tertiary);
    }
  }

  .sort-icon {
    font-size: var(--font-size-xs);
    margin-left: var(--spacing-xs);
    opacity: 0.6;
  }
}

.empty-state {
  flex: 1;
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
</style>
