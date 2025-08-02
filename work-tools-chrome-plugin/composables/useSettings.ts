import { computed } from 'vue'
import { useSettingsStore } from '../stores/settingsStore'
import { useRenameStore } from '../stores/renameStore'
import { useKeyboardShortcuts } from './useKeyboardShortcuts'

export function useSettings() {
  const settingsStore = useSettingsStore()
  const renameStore = useRenameStore()
  const { setEnabled: setShortcutsEnabled } = useKeyboardShortcuts()

  // 应用设置到各个系统
  function applySettings() {
    // 应用重命名设置
    renameStore.isAutoPreview = settingsStore.settings.autoPreview
    renameStore.maxHistorySize = settingsStore.settings.maxHistorySize

    // 应用快捷键设置
    setShortcutsEnabled(settingsStore.settings.enableKeyboardShortcuts)

    // 应用主题设置
    applyTheme(settingsStore.settings.theme)
  }

  // 应用主题
  function applyTheme(theme: 'light' | 'dark' | 'auto') {
    const root = document.documentElement
    
    if (theme === 'auto') {
      // 根据系统主题自动切换
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      root.setAttribute('data-theme', prefersDark ? 'dark' : 'light')
    } else {
      root.setAttribute('data-theme', theme)
    }
  }

  // 监听系统主题变化
  function setupThemeListener() {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    
    const handleThemeChange = () => {
      if (settingsStore.settings.theme === 'auto') {
        applyTheme('auto')
      }
    }

    mediaQuery.addEventListener('change', handleThemeChange)
    
    // 返回清理函数
    return () => {
      mediaQuery.removeEventListener('change', handleThemeChange)
    }
  }

  // 验证设置值
  function validateSetting(key: string, value: any): boolean {
    switch (key) {
      case 'maxHistorySize':
        return typeof value === 'number' && value >= 1 && value <= 1000
      case 'maxFilesPerPage':
        return typeof value === 'number' && value >= 10 && value <= 1000
      case 'maxFileSize':
        return typeof value === 'number' && value >= 1 && value <= 1000
      case 'theme':
        return ['light', 'dark', 'auto'].includes(value)
      case 'language':
        return ['zh-CN', 'en-US'].includes(value)
      case 'exportFormat':
        return ['json', 'csv'].includes(value)
      default:
        return true
    }
  }

  // 获取设置分组
  const settingGroups = computed(() => [
    {
      key: 'interface',
      title: '界面设置',
      icon: '🎨',
      settings: [
        { key: 'theme', type: 'select', options: [
          { value: 'light', label: '浅色' },
          { value: 'dark', label: '深色' },
          { value: 'auto', label: '跟随系统' }
        ]},
        { key: 'language', type: 'select', options: [
          { value: 'zh-CN', label: '简体中文' },
          { value: 'en-US', label: 'English' }
        ]}
      ]
    },
    {
      key: 'rename',
      title: '重命名设置',
      icon: '✏️',
      settings: [
        { key: 'autoPreview', type: 'boolean' },
        { key: 'confirmBeforeExecute', type: 'boolean' },
        { key: 'showPreviewPanel', type: 'boolean' },
        { key: 'maxHistorySize', type: 'number', min: 1, max: 1000 }
      ]
    },
    {
      key: 'performance',
      title: '性能设置',
      icon: '⚡',
      settings: [
        { key: 'maxFilesPerPage', type: 'number', min: 10, max: 1000 },
        { key: 'enableVirtualScrolling', type: 'boolean' }
      ]
    },
    {
      key: 'shortcuts',
      title: '快捷键设置',
      icon: '⌨️',
      settings: [
        { key: 'enableKeyboardShortcuts', type: 'boolean' }
      ]
    },
    {
      key: 'files',
      title: '文件处理',
      icon: '📁',
      settings: [
        { key: 'includeHiddenFiles', type: 'boolean' },
        { key: 'followSymlinks', type: 'boolean' },
        { key: 'maxFileSize', type: 'number', min: 1, max: 1000, suffix: 'MB' }
      ]
    },
    {
      key: 'export',
      title: '导入导出',
      icon: '📤',
      settings: [
        { key: 'exportFormat', type: 'select', options: [
          { value: 'json', label: 'JSON' },
          { value: 'csv', label: 'CSV' }
        ]},
        { key: 'includeSettings', type: 'boolean' }
      ]
    },
    {
      key: 'other',
      title: '其他设置',
      icon: '⚙️',
      settings: [
        { key: 'showWelcomeDialog', type: 'boolean' },
        { key: 'enableAnalytics', type: 'boolean' },
        { key: 'autoSave', type: 'boolean' }
      ]
    }
  ])

  // 获取设置项的描述
  function getSettingDescription(key: string): string {
    const descriptions: Record<string, string> = {
      theme: '选择应用的外观主题',
      language: '选择界面显示语言',
      autoPreview: '修改参数时自动生成预览',
      confirmBeforeExecute: '执行重命名前显示确认对话框',
      showPreviewPanel: '显示重命名预览面板',
      maxHistorySize: '保留的操作历史记录数量',
      maxFilesPerPage: '文件列表每页显示的最大文件数',
      enableVirtualScrolling: '大量文件时启用虚拟滚动提升性能',
      enableKeyboardShortcuts: '启用键盘快捷键操作',
      includeHiddenFiles: '处理时包含隐藏文件',
      followSymlinks: '跟随符号链接处理目标文件',
      maxFileSize: '处理文件的最大大小限制',
      exportFormat: '导出数据时使用的文件格式',
      includeSettings: '导出时包含应用设置',
      showWelcomeDialog: '首次使用时显示欢迎对话框',
      enableAnalytics: '启用匿名使用统计',
      autoSave: '修改设置时自动保存'
    }
    
    return descriptions[key] || ''
  }

  // 重置所有设置
  function resetAllSettings() {
    settingsStore.resetSettings()
    applySettings()
  }

  // 导出设置到文件
  function exportSettingsToFile() {
    const settings = settingsStore.exportSettings()
    const blob = new Blob([settings], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    
    const a = document.createElement('a')
    a.href = url
    a.download = `work-tools-settings-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    
    URL.revokeObjectURL(url)
  }

  // 从文件导入设置
  function importSettingsFromFile(): Promise<boolean> {
    return new Promise((resolve) => {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = '.json'
      
      input.onchange = (e) => {
        const file = (e.target as HTMLInputElement).files?.[0]
        if (!file) {
          resolve(false)
          return
        }
        
        const reader = new FileReader()
        reader.onload = (e) => {
          const content = e.target?.result as string
          const success = settingsStore.importSettings(content)
          if (success) {
            applySettings()
          }
          resolve(success)
        }
        reader.onerror = () => resolve(false)
        reader.readAsText(file)
      }
      
      input.click()
    })
  }

  return {
    settings: settingsStore.settings,
    isLoading: settingsStore.isLoading,
    lastSaved: settingsStore.lastSaved,
    settingGroups,
    applySettings,
    applyTheme,
    setupThemeListener,
    validateSetting,
    getSettingDescription,
    updateSetting: settingsStore.updateSetting,
    updateSettings: settingsStore.updateSettings,
    resetSettings: settingsStore.resetSettings,
    resetCategory: settingsStore.resetCategory,
    resetAllSettings,
    exportSettingsToFile,
    importSettingsFromFile,
    getSettingDisplayName: settingsStore.getSettingDisplayName
  }
}
