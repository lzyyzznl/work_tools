<script setup lang="ts">
import { ref, computed } from 'vue'
import { useFileStore } from '../../stores/fileStore'
import { useRuleStore } from '../../stores/ruleStore'
import { useFileSystem } from '../../composables/useFileSystem'
import { useErrorHandler } from '../../composables/useErrorHandler'
import FileTable from '../common/FileTable.vue'
import RuleManager from './RuleManager.vue'

const fileStore = useFileStore()
const ruleStore = useRuleStore()
const { selectFiles, selectDirectory, handleDrop } = useFileSystem()
const { handleError, handleSuccess } = useErrorHandler()

const isDragOver = ref(false)
const isMatching = ref(false)
const showRuleManager = ref(false)

// 计算属性
const hasFiles = computed(() => fileStore.files.length > 0)
const hasRules = computed(() => ruleStore.rules.length > 0)
const canMatch = computed(() => hasFiles.value && hasRules.value)

// 文件操作
async function handleSelectFiles() {
  try {
    const files = await fileStore.selectFilesFromSystem({ multiple: true })
    if (files.length > 0) {
      handleSuccess(`成功添加 ${files.length} 个文件`)
    }
  } catch (error) {
    handleError(error, '选择文件失败')
  }
}

async function handleSelectDirectory() {
  try {
    const files = await fileStore.selectDirectoryFromSystem()
    if (files.length > 0) {
      handleSuccess(`成功添加 ${files.length} 个文件`)
    }
  } catch (error) {
    handleError(error, '选择目录失败')
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
  
  try {
    const files = handleDrop(e)
    if (files.length > 0) {
      fileStore.addFiles(files)
      handleSuccess(`成功添加 ${files.length} 个文件`)
    }
  } catch (error) {
    handleError(error, '拖拽文件失败')
  }
}

function clearFiles() {
  fileStore.clearFiles()
  handleSuccess('已清空文件列表')
}

// 匹配操作
async function executeMatch() {
  if (!canMatch.value) return
  
  isMatching.value = true
  try {
    let matchedCount = 0
    
    fileStore.files.forEach(file => {
      const result = ruleStore.matchFilename(file.name)
      fileStore.updateFileMatchResult(file.id, result.matched, result.matchInfo)
      if (result.matched) {
        matchedCount++
      }
    })
    
    handleSuccess(`匹配完成，共匹配 ${matchedCount} 个文件`)
  } catch (error) {
    handleError(error, '文件匹配失败')
  } finally {
    isMatching.value = false
  }
}

function clearMatchResults() {
  fileStore.files.forEach(file => {
    fileStore.updateFileMatchResult(file.id, false)
  })
  handleSuccess('已清除匹配结果')
}

// 规则管理
function openRuleManager() {
  showRuleManager.value = true
}

function closeRuleManager() {
  showRuleManager.value = false
}
</script>

<template>
  <div class="file-matcher-tab flex flex-col h-full bg-white">
    <!-- 工具栏 -->
    <div class="toolbar flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
      <div class="toolbar-left flex items-center gap-3">
        <button
          @click="handleSelectFiles"
          class="btn-primary px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
        >
          <span class="mr-2">📁</span>
          选择文件
        </button>
        
        <button
          @click="handleSelectDirectory"
          class="btn-secondary px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
        >
          <span class="mr-2">📂</span>
          选择目录
        </button>
        
        <button
          v-if="hasFiles"
          @click="clearFiles"
          class="btn-danger px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
        >
          <span class="mr-2">🗑️</span>
          清空文件
        </button>
      </div>

      <div class="toolbar-right flex items-center gap-3">
        <button
          @click="openRuleManager"
          class="btn-secondary px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
        >
          <span class="mr-2">⚙️</span>
          管理规则
        </button>
        
        <button
          @click="executeMatch"
          :disabled="!canMatch || isMatching"
          class="btn-primary px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <span v-if="isMatching" class="mr-2">⏳</span>
          <span v-else class="mr-2">🎯</span>
          {{ isMatching ? '匹配中...' : '开始匹配' }}
        </button>
        
        <button
          v-if="hasFiles"
          @click="clearMatchResults"
          class="btn-warning px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors"
        >
          <span class="mr-2">🔄</span>
          清除结果
        </button>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="main-content flex-1 flex flex-col">
      <!-- 拖拽区域 -->
      <div
        v-if="!hasFiles"
        @dragenter="handleDragEnter"
        @dragover.prevent
        @dragleave="handleDragLeave"
        @drop="handleDropFiles"
        class="drop-zone flex-1 flex flex-col items-center justify-center p-12 border-2 border-dashed border-gray-300 m-4 rounded-lg transition-colors"
        :class="{ 'border-blue-500 bg-blue-50': isDragOver }"
      >
        <div class="text-6xl mb-6 opacity-50">📁</div>
        <div class="text-xl font-medium text-gray-600 mb-4">
          {{ isDragOver ? '释放文件到此处' : '拖拽文件到此处' }}
        </div>
        <div class="text-sm text-gray-400 mb-6 text-center">
          支持单个文件或整个文件夹<br>
          也可以点击下方按钮选择文件
        </div>
        <div class="flex gap-4">
          <button
            @click="handleSelectFiles"
            class="btn-primary px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            选择文件
          </button>
          <button
            @click="handleSelectDirectory"
            class="btn-secondary px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
          >
            选择目录
          </button>
        </div>
      </div>

      <!-- 文件列表 -->
      <div v-else class="file-list flex-1">
        <FileTable
          :show-match-info="true"
          :show-selection="true"
          :show-preview="false"
        />
      </div>

      <!-- 状态提示 -->
      <div v-if="hasFiles && !hasRules" class="status-bar p-4 bg-yellow-50 border-t border-yellow-200">
        <div class="flex items-center gap-3 text-yellow-800">
          <span class="text-xl">⚠️</span>
          <div>
            <div class="font-medium">尚未配置匹配规则</div>
            <div class="text-sm">请先添加匹配规则才能进行文件匹配</div>
          </div>
          <button
            @click="openRuleManager"
            class="ml-auto px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 transition-colors"
          >
            添加规则
          </button>
        </div>
      </div>

      <!-- 匹配统计 -->
      <div v-if="hasFiles && hasRules" class="stats-bar p-4 bg-gray-50 border-t border-gray-200">
        <div class="flex items-center justify-between text-sm">
          <div class="flex items-center gap-6">
            <div class="flex items-center gap-2">
              <span class="text-gray-500">总文件:</span>
              <span class="font-semibold text-gray-900">{{ fileStore.fileStats.total }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-500">已匹配:</span>
              <span class="font-semibold text-green-600">{{ fileStore.fileStats.matched }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-500">未匹配:</span>
              <span class="font-semibold text-red-600">{{ fileStore.fileStats.unmatched }}</span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-gray-500">已选中:</span>
              <span class="font-semibold text-blue-600">{{ fileStore.fileStats.selected }}</span>
            </div>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-gray-500">规则数量:</span>
            <span class="font-semibold text-purple-600">{{ ruleStore.ruleCount }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 规则管理器模态框 -->
    <div
      v-if="showRuleManager"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
      @click.self="closeRuleManager"
    >
      <div class="bg-white rounded-lg shadow-xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col">
        <div class="flex items-center justify-between p-4 border-b border-gray-200">
          <h2 class="text-lg font-semibold text-gray-900">规则管理</h2>
          <button
            @click="closeRuleManager"
            class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <span class="text-xl">✕</span>
          </button>
        </div>
        <div class="flex-1 overflow-hidden">
          <RuleManager />
        </div>
      </div>
    </div>
  </div>
</template>
