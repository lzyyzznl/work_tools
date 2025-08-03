import { ref } from 'vue'
import { useFileStore } from '../stores/fileStore'
import { useFileMatcherStore } from '../stores/fileMatcherStore'
import { useFileRenamerStore } from '../stores/fileRenamerStore'
import { useRenameStore } from '../stores/renameStore'
import { useSettingsStore } from '../stores/settingsStore'
import { useErrorHandler } from './useErrorHandler'
// TODO: 需要创建这些工具函数
// import { exportData, type ExportOptions } from '../utils/exportUtils'
// import { importData, selectImportFile, previewImportData, type ImportOptions } from '../utils/importUtils'

export function useDataManager() {
  // 使用默认的fileStore以保持向后兼容性
  const fileStore = useFileStore()
  const renameStore = useRenameStore()
  const settingsStore = useSettingsStore()
  const { handleError, handleSuccess, handleWarning } = useErrorHandler()

  const isExporting = ref(false)
  const isImporting = ref(false)
  const importPreview = ref<any>(null)
  const showImportPreview = ref(false)

  // 导出数据
  async function exportAllData(options: ExportOptions) {
    if (isExporting.value) return

    isExporting.value = true
    try {
      const files = fileStore.files
      const history = renameStore.history
      const settings = options.includeSettings ? settingsStore.settings : undefined

      exportData(files, history, settings, options)
      
      handleSuccess(
        `数据已成功导出为 ${options.format.toUpperCase()} 格式`,
        '导出完成'
      )
    } catch (error) {
      handleError(error, '导出数据')
    } finally {
      isExporting.value = false
    }
  }

  // 快速导出文件列表
  async function exportFileList(format: 'json' | 'csv' = 'csv', description?: string) {
    const options: ExportOptions = {
      includeFiles: true,
      includeHistory: false,
      includeSettings: false,
      format,
      description: description || '文件列表'
    }
    
    await exportAllData(options)
  }

  // 快速导出完整数据
  async function exportFullData(description?: string) {
    const options: ExportOptions = {
      includeFiles: true,
      includeHistory: true,
      includeSettings: true,
      format: 'json',
      description: description || '完整数据'
    }
    
    await exportAllData(options)
  }

  // 导入数据
  async function importAllData(options: ImportOptions) {
    if (isImporting.value) return

    isImporting.value = true
    try {
      const file = await selectImportFile()
      if (!file) {
        isImporting.value = false
        return
      }

      const result = await importData(file, options)
      
      if (!result.success) {
        handleError(result.errors.join(', '), '导入失败')
        return
      }

      if (result.warnings.length > 0) {
        handleWarning(result.warnings.join(', '), '导入警告')
      }

      if (result.data) {
        // 显示导入预览
        importPreview.value = {
          data: result.data,
          stats: result.stats,
          preview: previewImportData(result.data),
          options
        }
        showImportPreview.value = true
      }

    } catch (error) {
      handleError(error, '导入数据')
    } finally {
      isImporting.value = false
    }
  }

  // 确认导入
  async function confirmImport() {
    if (!importPreview.value) return

    try {
      const { data, options } = importPreview.value

      // 导入文件
      if (data.files.length > 0) {
        if (options.replaceExisting) {
          fileStore.clearFiles()
        }
        fileStore.addFiles(data.files)
      }

      // 导入历史记录
      if (data.renameHistory.length > 0) {
        if (options.mergeHistory) {
          // 合并历史记录
          data.renameHistory.forEach((history: any) => {
            renameStore.addToHistory(history)
          })
        } else {
          // 替换历史记录
          renameStore.clearHistory()
          data.renameHistory.forEach((history: any) => {
            renameStore.addToHistory(history)
          })
        }
      }

      // 导入设置
      if (options.importSettings && data.settings) {
        settingsStore.updateSettings(data.settings)
      }

      handleSuccess(
        `成功导入 ${data.files.length} 个文件和 ${data.renameHistory.length} 条历史记录`,
        '导入完成'
      )

      // 关闭预览
      showImportPreview.value = false
      importPreview.value = null

    } catch (error) {
      handleError(error, '确认导入')
    }
  }

  // 取消导入
  function cancelImport() {
    showImportPreview.value = false
    importPreview.value = null
  }

  // 快速导入
  async function quickImport() {
    const options: ImportOptions = {
      replaceExisting: false,
      mergeHistory: true,
      importSettings: false,
      validateFiles: true
    }
    
    await importAllData(options)
  }

  // 完整导入（替换现有数据）
  async function fullImport() {
    const options: ImportOptions = {
      replaceExisting: true,
      mergeHistory: false,
      importSettings: true,
      validateFiles: true
    }
    
    await importAllData(options)
  }

  // 获取导出统计信息
  function getExportStats() {
    return {
      fileCount: fileStore.files.length,
      historyCount: renameStore.history.length,
      hasSettings: true,
      selectedFiles: fileStore.selectedFiles.length
    }
  }

  // 清空所有数据
  function clearAllData() {
    if (confirm('确定要清空所有数据吗？此操作不可撤销。')) {
      fileStore.clearFiles()
      renameStore.clearHistory()
      handleSuccess('所有数据已清空', '清空完成')
    }
  }

  // 备份当前数据
  async function backupCurrentData() {
    const timestamp = new Date().toISOString().split('T')[0]
    await exportFullData(`backup-${timestamp}`)
  }

  return {
    // 状态
    isExporting,
    isImporting,
    importPreview,
    showImportPreview,

    // 导出方法
    exportAllData,
    exportFileList,
    exportFullData,
    backupCurrentData,

    // 导入方法
    importAllData,
    quickImport,
    fullImport,
    confirmImport,
    cancelImport,

    // 工具方法
    getExportStats,
    clearAllData
  }
}
