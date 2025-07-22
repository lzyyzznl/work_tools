<script setup lang="ts">
import { ref } from 'vue'
import { useFileStore } from '../../stores/fileStore'
import { useFileSystem } from '../../composables/useFileSystem'
import FileTable from '../common/FileTable.vue'

const fileStore = useFileStore()
const { selectFiles, handleDrop } = useFileSystem()

const isDragOver = ref(false)

async function handleSelectFiles() {
  try {
    const files = await selectFiles({ multiple: true })
    if (files.length > 0) {
      fileStore.addFiles(files)
    }
  } catch (error) {
    console.error('选择文件失败:', error)
  }
}

function handleDragEnter(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = true
}

function handleDragLeave(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = false
}

function handleDropFiles(e: DragEvent) {
  e.preventDefault()
  isDragOver.value = false
  
  const files = handleDrop(e)
  if (files.length > 0) {
    fileStore.addFiles(files)
  }
}

function clearFiles() {
  fileStore.clearFiles()
}
</script>

<template>
  <div class="file-matcher-tab">
    <!-- 工具栏 -->
    <div class="toolbar">
      <button class="btn btn-primary" @click="handleSelectFiles">
        📁 选择文件
      </button>
      <button class="btn" @click="clearFiles" :disabled="!fileStore.hasFiles">
        🗑️ 清空
      </button>
      <div class="toolbar-spacer"></div>
      <button class="btn" disabled>
        ⚙️ 规则管理
      </button>
      <button class="btn" disabled>
        📊 导出结果
      </button>
    </div>

    <!-- 拖拽区域 -->
    <div 
      class="drop-zone"
      :class="{ 'drag-over': isDragOver }"
      @dragenter="handleDragEnter"
      @dragover.prevent
      @dragleave="handleDragLeave"
      @drop="handleDropFiles"
    >
      <!-- 文件表格 -->
      <FileTable 
        :show-match-info="true"
        :show-selection="true"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.file-matcher-tab {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-background-secondary);
  border-bottom: 1px solid var(--color-border-primary);

  .toolbar-spacer {
    flex: 1;
  }
}

.drop-zone {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;

  &.drag-over {
    background: rgba(0, 122, 255, 0.05);
    
    &::after {
      content: '拖拽文件到此处';
      position: absolute;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      font-size: var(--font-size-xl);
      font-weight: var(--font-weight-semibold);
      color: var(--color-primary);
      background: var(--color-background-primary);
      padding: var(--spacing-lg) var(--spacing-2xl);
      border-radius: var(--radius-lg);
      border: 2px dashed var(--color-primary);
      z-index: 10;
    }
  }
}
</style>
