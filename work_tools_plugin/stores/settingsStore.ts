import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export interface AppSettings {
  // 界面设置
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  
  // 重命名设置
  autoPreview: boolean
  confirmBeforeExecute: boolean
  showPreviewPanel: boolean
  maxHistorySize: number
  
  // 性能设置
  maxFilesPerPage: number
  enableVirtualScrolling: boolean
  
  // 快捷键设置
  enableKeyboardShortcuts: boolean
  customShortcuts: Record<string, string>
  
  // 文件处理设置
  includeHiddenFiles: boolean
  followSymlinks: boolean
  maxFileSize: number // MB
  
  // 导入导出设置
  exportFormat: 'json' | 'csv'
  includeSettings: boolean
  
  // 其他设置
  showWelcomeDialog: boolean
  enableAnalytics: boolean
  autoSave: boolean
}

const defaultSettings: AppSettings = {
  // 界面设置
  theme: 'auto',
  language: 'zh-CN',
  
  // 重命名设置
  autoPreview: true,
  confirmBeforeExecute: true,
  showPreviewPanel: true,
  maxHistorySize: 50,
  
  // 性能设置
  maxFilesPerPage: 100,
  enableVirtualScrolling: false,
  
  // 快捷键设置
  enableKeyboardShortcuts: true,
  customShortcuts: {},
  
  // 文件处理设置
  includeHiddenFiles: false,
  followSymlinks: false,
  maxFileSize: 100, // 100MB
  
  // 导入导出设置
  exportFormat: 'json',
  includeSettings: true,
  
  // 其他设置
  showWelcomeDialog: true,
  enableAnalytics: false,
  autoSave: true
}

export const useSettingsStore = defineStore('settings', () => {
  const settings = ref<AppSettings>({ ...defaultSettings })
  const isLoading = ref(false)
  const lastSaved = ref<number>(0)

  // 从localStorage加载设置
  function loadSettings() {
    isLoading.value = true
    try {
      const saved = localStorage.getItem('work-tools-settings')
      if (saved) {
        const parsedSettings = JSON.parse(saved)
        // 合并默认设置和保存的设置，确保新增的设置项有默认值
        settings.value = { ...defaultSettings, ...parsedSettings }
      }
    } catch (error) {
      console.error('加载设置失败:', error)
      settings.value = { ...defaultSettings }
    } finally {
      isLoading.value = false
    }
  }

  // 保存设置到localStorage
  function saveSettings() {
    try {
      localStorage.setItem('work-tools-settings', JSON.stringify(settings.value))
      lastSaved.value = Date.now()
    } catch (error) {
      console.error('保存设置失败:', error)
      throw new Error('保存设置失败，可能是存储空间不足')
    }
  }

  // 更新单个设置项
  function updateSetting<K extends keyof AppSettings>(key: K, value: AppSettings[K]) {
    settings.value[key] = value
    if (settings.value.autoSave) {
      saveSettings()
    }
  }

  // 批量更新设置
  function updateSettings(newSettings: Partial<AppSettings>) {
    Object.assign(settings.value, newSettings)
    if (settings.value.autoSave) {
      saveSettings()
    }
  }

  // 重置设置为默认值
  function resetSettings() {
    settings.value = { ...defaultSettings }
    if (settings.value.autoSave) {
      saveSettings()
    }
  }

  // 重置特定分类的设置
  function resetCategory(category: 'interface' | 'rename' | 'performance' | 'shortcuts' | 'files' | 'export' | 'other') {
    switch (category) {
      case 'interface':
        settings.value.theme = defaultSettings.theme
        settings.value.language = defaultSettings.language
        break
      case 'rename':
        settings.value.autoPreview = defaultSettings.autoPreview
        settings.value.confirmBeforeExecute = defaultSettings.confirmBeforeExecute
        settings.value.showPreviewPanel = defaultSettings.showPreviewPanel
        settings.value.maxHistorySize = defaultSettings.maxHistorySize
        break
      case 'performance':
        settings.value.maxFilesPerPage = defaultSettings.maxFilesPerPage
        settings.value.enableVirtualScrolling = defaultSettings.enableVirtualScrolling
        break
      case 'shortcuts':
        settings.value.enableKeyboardShortcuts = defaultSettings.enableKeyboardShortcuts
        settings.value.customShortcuts = { ...defaultSettings.customShortcuts }
        break
      case 'files':
        settings.value.includeHiddenFiles = defaultSettings.includeHiddenFiles
        settings.value.followSymlinks = defaultSettings.followSymlinks
        settings.value.maxFileSize = defaultSettings.maxFileSize
        break
      case 'export':
        settings.value.exportFormat = defaultSettings.exportFormat
        settings.value.includeSettings = defaultSettings.includeSettings
        break
      case 'other':
        settings.value.showWelcomeDialog = defaultSettings.showWelcomeDialog
        settings.value.enableAnalytics = defaultSettings.enableAnalytics
        settings.value.autoSave = defaultSettings.autoSave
        break
    }
    
    if (settings.value.autoSave) {
      saveSettings()
    }
  }

  // 导出设置
  function exportSettings(): string {
    return JSON.stringify(settings.value, null, 2)
  }

  // 导入设置
  function importSettings(settingsJson: string): boolean {
    try {
      const importedSettings = JSON.parse(settingsJson)
      
      // 验证导入的设置格式
      if (typeof importedSettings !== 'object' || importedSettings === null) {
        throw new Error('无效的设置格式')
      }

      // 合并设置，保留当前设置中新增的项
      const mergedSettings = { ...settings.value, ...importedSettings }
      settings.value = mergedSettings
      
      if (settings.value.autoSave) {
        saveSettings()
      }
      
      return true
    } catch (error) {
      console.error('导入设置失败:', error)
      return false
    }
  }

  // 获取设置的显示名称
  function getSettingDisplayName(key: keyof AppSettings): string {
    const displayNames: Record<keyof AppSettings, string> = {
      theme: '主题',
      language: '语言',
      autoPreview: '自动预览',
      confirmBeforeExecute: '执行前确认',
      showPreviewPanel: '显示预览面板',
      maxHistorySize: '历史记录数量',
      maxFilesPerPage: '每页文件数',
      enableVirtualScrolling: '虚拟滚动',
      enableKeyboardShortcuts: '快捷键',
      customShortcuts: '自定义快捷键',
      includeHiddenFiles: '包含隐藏文件',
      followSymlinks: '跟随符号链接',
      maxFileSize: '最大文件大小',
      exportFormat: '导出格式',
      includeSettings: '包含设置',
      showWelcomeDialog: '显示欢迎对话框',
      enableAnalytics: '启用分析',
      autoSave: '自动保存'
    }
    
    return displayNames[key] || key
  }

  // 监听设置变化，自动保存
  watch(
    settings,
    () => {
      if (settings.value.autoSave && !isLoading.value) {
        saveSettings()
      }
    },
    { deep: true }
  )

  // 初始化时加载设置
  loadSettings()

  return {
    settings,
    isLoading,
    lastSaved,
    loadSettings,
    saveSettings,
    updateSetting,
    updateSettings,
    resetSettings,
    resetCategory,
    exportSettings,
    importSettings,
    getSettingDisplayName
  }
})
