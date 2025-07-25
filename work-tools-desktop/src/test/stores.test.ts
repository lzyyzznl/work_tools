import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useFileStore, useRuleStore, useRenameStore, useSettingsStore } from '../renderer/stores'
import { createMockFile, createMockFiles, mockRules } from './fixtures/testData'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

describe('Stores', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
  })

  describe('FileStore', () => {
    it('should initialize with empty state', () => {
      const fileStore = useFileStore()
      
      expect(fileStore.files).toHaveLength(0)
      expect(fileStore.selectedFiles.size).toBe(0)
      expect(fileStore.isLoading).toBe(false)
      expect(fileStore.hasFiles).toBe(false)
    })

    it('should add files correctly', () => {
      const fileStore = useFileStore()
      const mockFile = createMockFile('test.txt', 'content')
      
      const id = fileStore.addFile(mockFile)
      
      expect(fileStore.files).toHaveLength(1)
      expect(fileStore.files[0].name).toBe('test.txt')
      expect(fileStore.files[0].id).toBe(id)
      expect(fileStore.hasFiles).toBe(true)
    })

    it('should handle file selection', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      
      const ids = fileStore.addFiles(mockFiles)
      fileStore.selectFile(ids[0])
      fileStore.selectFile(ids[1])
      
      expect(fileStore.selectedFiles.size).toBe(2)
      expect(fileStore.selectedFileItems).toHaveLength(2)
      expect(fileStore.fileStats.selected).toBe(2)
    })

    it('should toggle file selection', () => {
      const fileStore = useFileStore()
      const mockFile = createMockFile('test.txt')
      const id = fileStore.addFile(mockFile)
      
      fileStore.toggleFileSelection(id)
      expect(fileStore.selectedFiles.has(id)).toBe(true)
      
      fileStore.toggleFileSelection(id)
      expect(fileStore.selectedFiles.has(id)).toBe(false)
    })

    it('should select and unselect all files', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)
      
      fileStore.selectAllFiles()
      expect(fileStore.selectedFiles.size).toBe(3)
      
      fileStore.unselectAllFiles()
      expect(fileStore.selectedFiles.size).toBe(0)
    })

    it('should remove files correctly', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      const ids = fileStore.addFiles(mockFiles)
      
      fileStore.selectFile(ids[0])
      fileStore.removeFile(ids[0])
      
      expect(fileStore.files).toHaveLength(2)
      expect(fileStore.selectedFiles.has(ids[0])).toBe(false)
    })

    it('should clear all files', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      const ids = fileStore.addFiles(mockFiles)
      fileStore.selectFile(ids[0])
      
      fileStore.clearFiles()
      
      expect(fileStore.files).toHaveLength(0)
      expect(fileStore.selectedFiles.size).toBe(0)
    })

    it('should update file match results', () => {
      const fileStore = useFileStore()
      const mockFile = createMockFile('test.txt')
      const id = fileStore.addFile(mockFile)
      
      const matchInfo = { code: 'TEST001', thirtyD: 'Y', matchedRule: 'test' }
      fileStore.updateFileMatchResult(id, true, matchInfo)
      
      const file = fileStore.getFileById(id)
      expect(file?.matched).toBe(true)
      expect(file?.matchInfo).toEqual(matchInfo)
    })

    it('should calculate file stats correctly', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(5)
      const ids = fileStore.addFiles(mockFiles)
      
      // 标记一些文件为匹配
      fileStore.updateFileMatchResult(ids[0], true)
      fileStore.updateFileMatchResult(ids[1], true)
      
      // 选择一些文件
      fileStore.selectFile(ids[0])
      fileStore.selectFile(ids[2])
      
      const stats = fileStore.fileStats
      expect(stats.total).toBe(5)
      expect(stats.matched).toBe(2)
      expect(stats.unmatched).toBe(3)
      expect(stats.selected).toBe(2)
    })
  })

  describe('RuleStore', () => {
    it('should initialize with empty rules', () => {
      const ruleStore = useRuleStore()
      
      expect(ruleStore.rules).toHaveLength(0)
      expect(ruleStore.isLoading).toBe(false)
      expect(ruleStore.ruleCount).toBe(0)
    })

    it('should load rules from localStorage', async () => {
      const mockConfig = {
        version: '1.0',
        settings: { autoSave: true, defaultExportFormat: 'xlsx', theme: 'light' },
        rules: { default: mockRules.slice(0, 2), user: mockRules.slice(2, 3) }
      }
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockConfig))

      const ruleStore = useRuleStore()
      await ruleStore.loadRules()

      expect(ruleStore.rules).toHaveLength(3)
      expect(ruleStore.systemRules).toHaveLength(2)
      expect(ruleStore.userRules).toHaveLength(1)
    })

    it('should validate rules correctly', () => {
      const ruleStore = useRuleStore()
      
      // 有效规则
      const validRule = {
        code: 'TEST001',
        thirtyD: 'Y',
        matchRules: ['test', 'example']
      }
      const validResult = ruleStore.validateRule(validRule)
      expect(validResult.isValid).toBe(true)
      expect(validResult.errors).toHaveLength(0)
      
      // 无效规则
      const invalidRule = {
        code: '',
        thirtyD: 'INVALID',
        matchRules: []
      }
      const invalidResult = ruleStore.validateRule(invalidRule)
      expect(invalidResult.isValid).toBe(false)
      expect(invalidResult.errors.length).toBeGreaterThan(0)
    })

    it('should add new rules', () => {
      const ruleStore = useRuleStore()
      
      const newRule = {
        code: 'TEST001',
        thirtyD: 'Y',
        matchRules: ['test']
      }
      
      const id = ruleStore.addRule(newRule)
      
      expect(ruleStore.rules).toHaveLength(1)
      expect(ruleStore.getRuleById(id)?.code).toBe('TEST001')
      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it('should match filenames correctly', () => {
      const ruleStore = useRuleStore()
      ruleStore.addRule({
        code: 'TEST001',
        thirtyD: 'Y',
        matchRules: ['document', 'report']
      })
      
      const result1 = ruleStore.matchFilename('my-document.pdf')
      expect(result1.matched).toBe(true)
      expect(result1.matchInfo?.code).toBe('TEST001')
      
      const result2 = ruleStore.matchFilename('random-file.txt')
      expect(result2.matched).toBe(false)
    })
  })

  describe('RenameStore', () => {
    it('should initialize with default state', () => {
      // 确保 localStorage 返回空值，这样 history 会被初始化为空数组
      localStorageMock.getItem.mockReturnValue(null)

      const renameStore = useRenameStore()

      expect(renameStore.currentMode).toBe('replace')
      expect(renameStore.isPreviewEnabled).toBe(true)
      expect(renameStore.isAutoPreview).toBe(true)
      expect(renameStore.isExecuting).toBe(false)
      expect(renameStore.history).toHaveLength(0)
    })

    it('should update rename parameters', () => {
      const renameStore = useRenameStore()
      
      renameStore.updateReplaceParams({ fromStr: 'old', toStr: 'new' })
      expect(renameStore.replaceParams.fromStr).toBe('old')
      expect(renameStore.replaceParams.toStr).toBe('new')
      
      renameStore.updateAddParams({ text: 'prefix_', isPrefix: true })
      expect(renameStore.addParams.text).toBe('prefix_')
      expect(renameStore.addParams.isPrefix).toBe(true)
    })

    it('should validate parameters correctly', () => {
      const renameStore = useRenameStore()
      
      // Replace mode validation
      renameStore.setMode('replace')
      expect(renameStore.hasValidParams).toBe(false)
      
      renameStore.updateReplaceParams({ fromStr: 'test' })
      expect(renameStore.hasValidParams).toBe(true)
      
      // Add mode validation
      renameStore.setMode('add')
      expect(renameStore.hasValidParams).toBe(false)
      
      renameStore.updateAddParams({ text: 'prefix' })
      expect(renameStore.hasValidParams).toBe(true)
    })

    it('should manage execution state', () => {
      const renameStore = useRenameStore()
      
      renameStore.setExecuting(true)
      expect(renameStore.isExecuting).toBe(true)
      expect(renameStore.executionProgress).toBe(0)
      
      renameStore.updateExecutionProgress(50)
      expect(renameStore.executionProgress).toBe(50)
      
      renameStore.setExecuting(false)
      expect(renameStore.isExecuting).toBe(false)
    })

    it('should manage history', () => {
      const renameStore = useRenameStore()
      
      const operation = {
        id: 'op1',
        timestamp: Date.now(),
        operations: [{ oldPath: 'old.txt', newPath: 'new.txt' }]
      }
      
      renameStore.addToHistory(operation)
      expect(renameStore.history).toHaveLength(1)
      expect(renameStore.canUndo).toBe(true)
      
      renameStore.clearHistory()
      expect(renameStore.history).toHaveLength(0)
      expect(renameStore.canUndo).toBe(false)
    })
  })

  describe('SettingsStore', () => {
    it('should initialize with default settings', () => {
      const settingsStore = useSettingsStore()
      
      expect(settingsStore.settings.theme).toBe('auto')
      expect(settingsStore.settings.language).toBe('zh-CN')
      expect(settingsStore.settings.autoPreview).toBe(true)
      expect(settingsStore.settings.confirmBeforeExecute).toBe(true)
    })

    it('should load settings from localStorage', () => {
      const mockSettings = {
        theme: 'dark',
        language: 'en-US',
        autoPreview: false,
        confirmBeforeExecute: false,
        shortcuts: { 'ctrl+s': 'save' }
      }
      localStorageMock.getItem.mockReturnValue(JSON.stringify(mockSettings))
      
      const settingsStore = useSettingsStore()
      settingsStore.loadSettings()
      
      expect(settingsStore.settings.theme).toBe('dark')
      expect(settingsStore.settings.language).toBe('en-US')
      expect(settingsStore.settings.autoPreview).toBe(false)
    })

    it('should update individual settings', () => {
      const settingsStore = useSettingsStore()
      
      settingsStore.updateSetting('theme', 'dark')
      expect(settingsStore.settings.theme).toBe('dark')
      expect(localStorageMock.setItem).toHaveBeenCalled()
    })

    it('should update multiple settings', () => {
      const settingsStore = useSettingsStore()
      
      settingsStore.updateSettings({
        theme: 'light',
        language: 'en-US',
        autoPreview: false
      })
      
      expect(settingsStore.settings.theme).toBe('light')
      expect(settingsStore.settings.language).toBe('en-US')
      expect(settingsStore.settings.autoPreview).toBe(false)
    })

    it('should export and import settings', () => {
      const settingsStore = useSettingsStore()
      
      settingsStore.updateSetting('theme', 'dark')
      const exported = settingsStore.exportSettings()
      const parsedExported = JSON.parse(exported)
      expect(parsedExported.theme).toBe('dark')
      
      const success = settingsStore.importSettings(exported)
      expect(success).toBe(true)
    })

    it('should reset settings', () => {
      const settingsStore = useSettingsStore()
      
      settingsStore.updateSetting('theme', 'dark')
      settingsStore.resetSettings()
      
      expect(settingsStore.settings.theme).toBe('auto')
    })
  })
})
