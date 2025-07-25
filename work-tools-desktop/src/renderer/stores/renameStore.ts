import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  RenameOperationType,
  ReplaceParams,
  AddParams,
  NumberParams,
  DeleteParams,
  RenameHistory
} from '../types/rename'
import { STORAGE_KEYS } from '../constants/app'

export const useRenameStore = defineStore('rename', () => {
  // 当前重命名模式
  const currentMode = ref<RenameOperationType>('replace')
  
  // 各种重命名参数
  const replaceParams = ref<ReplaceParams>({
    fromStr: '',
    toStr: ''
  })
  
  const addParams = ref<AddParams>({
    text: '',
    isPrefix: true
  })
  
  const numberParams = ref<NumberParams>({
    start: 1,
    digits: 3,
    step: 1,
    separator: '_',
    isPrefix: true
  })
  
  const deleteParams = ref<DeleteParams>({
    startPos: 1,
    count: 1,
    fromLeft: true
  })
  
  // 预览相关状态
  const isPreviewEnabled = ref(true)
  const isAutoPreview = ref(true)
  const previewUpdateTime = ref<number>(0)
  
  // 操作历史
  const history = ref<RenameHistory[]>([])
  const maxHistorySize = ref(50)
  
  // 执行状态
  const isExecuting = ref(false)
  const executionProgress = ref(0)
  const lastExecutionTime = ref<number>(0)
  
  // 计算属性
  const currentParams = computed(() => {
    switch (currentMode.value) {
      case 'replace':
        return replaceParams.value
      case 'add':
        return addParams.value
      case 'number':
        return numberParams.value
      case 'delete':
        return deleteParams.value
      default:
        return replaceParams.value
    }
  })
  
  const canUndo = computed(() => history.value.length > 0)
  
  const hasValidParams = computed(() => {
    switch (currentMode.value) {
      case 'replace':
        return replaceParams.value.fromStr.length > 0
      case 'add':
        return addParams.value.text.length > 0
      case 'number':
        return numberParams.value.start >= 0 && numberParams.value.digits > 0 && numberParams.value.step > 0
      case 'delete':
        return deleteParams.value.startPos > 0 && deleteParams.value.count > 0
      default:
        return false
    }
  })
  
  // 存储操作
  function saveHistory() {
    try {
      localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history.value))
    } catch (error) {
      console.error('保存历史记录失败:', error)
    }
  }
  
  function loadHistory() {
    try {
      const saved = localStorage.getItem(STORAGE_KEYS.HISTORY)
      if (saved) {
        const parsedHistory = JSON.parse(saved)
        history.value = Array.isArray(parsedHistory) ? parsedHistory : []
      } else {
        history.value = []
      }
    } catch (error) {
      console.error('加载历史记录失败:', error)
      history.value = []
    }
  }
  
  // Actions
  function setMode(mode: RenameOperationType) {
    currentMode.value = mode
  }
  
  function updateReplaceParams(params: Partial<ReplaceParams>) {
    replaceParams.value = { ...replaceParams.value, ...params }
  }
  
  function updateAddParams(params: Partial<AddParams>) {
    addParams.value = { ...addParams.value, ...params }
  }
  
  function updateNumberParams(params: Partial<NumberParams>) {
    numberParams.value = { ...numberParams.value, ...params }
  }
  
  function updateDeleteParams(params: Partial<DeleteParams>) {
    deleteParams.value = { ...deleteParams.value, ...params }
  }
  
  function togglePreview() {
    isPreviewEnabled.value = !isPreviewEnabled.value
  }
  
  function toggleAutoPreview() {
    isAutoPreview.value = !isAutoPreview.value
  }
  
  function updatePreviewTime() {
    previewUpdateTime.value = Date.now()
  }
  
  function addToHistory(operation: RenameHistory) {
    history.value.unshift(operation)
    if (history.value.length > maxHistorySize.value) {
      history.value = history.value.slice(0, maxHistorySize.value)
    }
    saveHistory()
  }
  
  function clearHistory() {
    history.value = []
    saveHistory()
  }
  
  function setExecuting(executing: boolean) {
    isExecuting.value = executing
    if (executing) {
      executionProgress.value = 0
    }
  }
  
  function updateExecutionProgress(progress: number) {
    executionProgress.value = Math.max(0, Math.min(100, progress))
  }
  
  function setLastExecutionTime() {
    lastExecutionTime.value = Date.now()
  }
  
  function resetAllParams() {
    replaceParams.value = { fromStr: '', toStr: '' }
    addParams.value = { text: '', isPrefix: true }
    numberParams.value = { start: 1, digits: 3, step: 1, separator: '_', isPrefix: true }
    deleteParams.value = { startPos: 1, count: 1, fromLeft: true }
  }
  
  // 初始化时加载历史记录
  loadHistory()
  
  return {
    // State
    currentMode,
    replaceParams,
    addParams,
    numberParams,
    deleteParams,
    isPreviewEnabled,
    isAutoPreview,
    previewUpdateTime,
    history,
    maxHistorySize,
    isExecuting,
    executionProgress,
    lastExecutionTime,
    
    // Computed
    currentParams,
    canUndo,
    hasValidParams,
    
    // Actions
    setMode,
    updateReplaceParams,
    updateAddParams,
    updateNumberParams,
    updateDeleteParams,
    togglePreview,
    toggleAutoPreview,
    updatePreviewTime,
    addToHistory,
    clearHistory,
    setExecuting,
    updateExecutionProgress,
    setLastExecutionTime,
    resetAllParams,
    
    // Storage actions
    saveHistory,
    loadHistory
  }
})
