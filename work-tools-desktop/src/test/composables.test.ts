import { describe, it, expect, beforeEach, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useFileSystem, useErrorHandler, useExcelUtils, useKeyboardShortcuts } from '../renderer/composables'
import { createMockFile, createMockFiles } from './fixtures/testData'
import { mockElectronAPI } from './setup'

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

describe('Composables', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
    
    // 重置 Electron API mocks
    Object.values(mockElectronAPI.fileSystem).forEach(mock => mock.mockReset())
  })

  describe('useFileSystem', () => {
    it('should initialize with correct state', () => {
      const { isSupported, isLoading, checkSupport } = useFileSystem()
      
      expect(isSupported.value).toBe(true)
      expect(isLoading.value).toBe(false)
      expect(checkSupport()).toBe('electron')
    })

    it('should select files using Electron API', async () => {
      const { selectFiles } = useFileSystem()
      const mockFiles = createMockFiles(2)
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue(mockFiles)

      const options = { multiple: true, accept: { 'Text Files': ['.txt'] } }
      const result = await selectFiles(options)

      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalledWith({
        multiple: true,
        filters: [{ name: 'Text Files', extensions: ['txt'] }]
      })
      expect(result).toEqual(mockFiles)
    })

    it('should select directory using Electron API', async () => {
      const { selectDirectory } = useFileSystem()
      const mockFiles = createMockFiles(3)
      mockElectronAPI.fileSystem.selectDirectory.mockResolvedValue(mockFiles)

      const result = await selectDirectory()

      expect(mockElectronAPI.fileSystem.selectDirectory).toHaveBeenCalled()
      expect(result).toEqual(mockFiles)
    })

    it('should handle file selection errors', async () => {
      const { selectFiles } = useFileSystem()
      const error = new Error('User cancelled')
      mockElectronAPI.fileSystem.selectFiles.mockRejectedValue(error)

      const result = await selectFiles()

      expect(result).toEqual([])
    })

    it('should format file size correctly', () => {
      const { formatFileSize } = useFileSystem()
      
      expect(formatFileSize(0)).toBe('0 B')
      expect(formatFileSize(1024)).toBe('1 KB')
      expect(formatFileSize(1048576)).toBe('1 MB')
      expect(formatFileSize(1073741824)).toBe('1 GB')
    })

    it('should get file extension correctly', () => {
      const { getFileExtension } = useFileSystem()
      
      expect(getFileExtension('test.txt')).toBe('txt')
      expect(getFileExtension('document.pdf')).toBe('pdf')
      expect(getFileExtension('archive.tar.gz')).toBe('gz')
      expect(getFileExtension('noextension')).toBe('')
    })

    it('should validate file types correctly', () => {
      const { validateFileType } = useFileSystem()
      const txtFile = createMockFile('test.txt')
      const pdfFile = createMockFile('document.pdf')
      
      expect(validateFileType(txtFile, ['txt', 'doc'])).toBe(true)
      expect(validateFileType(pdfFile, ['txt', 'doc'])).toBe(false)
      expect(validateFileType(pdfFile, ['*'])).toBe(true)
    })

    it('should get file info correctly', () => {
      const { getFileInfo } = useFileSystem()
      const mockFile = createMockFile('test.txt', 'content', 'text/plain')
      
      const info = getFileInfo(mockFile)
      
      expect(info.name).toBe('test.txt')
      expect(info.extension).toBe('txt')
      expect(info.type).toBe('text/plain')
      expect(typeof info.formattedSize).toBe('string')
    })

    it('should handle drag and drop files', () => {
      const { handleDrop } = useFileSystem()
      const mockFile = createMockFile('dropped.txt')
      
      const mockEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          files: [mockFile]
        }
      } as any
      
      const result = handleDrop(mockEvent)
      
      expect(mockEvent.preventDefault).toHaveBeenCalled()
      expect(result).toHaveLength(1)
      expect(result[0]).toBe(mockFile)
    })
  })

  describe('useErrorHandler', () => {
    it('should initialize with empty errors', () => {
      const { errors, maxErrors } = useErrorHandler()
      
      expect(errors.value).toHaveLength(0)
      expect(maxErrors.value).toBe(10)
    })

    it('should add errors correctly', () => {
      const { errors, addError } = useErrorHandler()
      
      const errorId = addError({
        type: 'error',
        title: '测试错误',
        message: '这是一个测试错误'
      })
      
      expect(errors.value).toHaveLength(1)
      expect(errors.value[0].id).toBe(errorId)
      expect(errors.value[0].type).toBe('error')
      expect(errors.value[0].title).toBe('测试错误')
    })

    it('should remove errors correctly', () => {
      const { errors, addError, removeError } = useErrorHandler()
      
      const errorId = addError({
        type: 'info',
        title: '测试',
        message: '测试消息'
      })
      
      expect(errors.value).toHaveLength(1)
      
      removeError(errorId)
      expect(errors.value).toHaveLength(0)
    })

    it('should handle different error types', () => {
      const { handleError, handleSuccess, handleWarning, handleInfo } = useErrorHandler()
      
      const errorId = handleError(new Error('测试错误'))
      const successId = handleSuccess('操作成功')
      const warningId = handleWarning('警告信息')
      const infoId = handleInfo('信息提示')
      
      expect(typeof errorId).toBe('string')
      expect(typeof successId).toBe('string')
      expect(typeof warningId).toBe('string')
      expect(typeof infoId).toBe('string')
    })

    it('should limit error count', () => {
      const { errors, addError, maxErrors } = useErrorHandler()
      maxErrors.value = 3
      
      // 添加超过限制的错误
      for (let i = 0; i < 5; i++) {
        addError({
          type: 'error',
          title: `错误 ${i}`,
          message: `消息 ${i}`
        })
      }
      
      expect(errors.value).toHaveLength(3)
    })
  })

  describe('useExcelUtils', () => {
    it('should export rules to Excel format', () => {
      const { exportRulesToExcel } = useExcelUtils()
      const mockRules = [
        {
          id: 'rule1',
          code: 'TEST001',
          thirtyD: 'Y',
          matchRules: ['test', 'example'],
          source: 'user' as const
        }
      ]
      
      const result = exportRulesToExcel(mockRules, 'test.xlsx')
      
      expect(result.success).toBe(true)
      expect(result.filename).toBe('test.xlsx')
    })

    it('should handle export errors', () => {
      const { exportRulesToExcel } = useExcelUtils()
      
      // 传入无效数据来触发错误
      const result = exportRulesToExcel(null as any)
      
      expect(result.success).toBe(false)
      expect(result.error).toBeDefined()
    })

    it('should create rule template', () => {
      const { createRuleTemplate } = useExcelUtils()
      
      const result = createRuleTemplate()
      
      expect(result.success).toBe(true)
      expect(result.filename).toBe('rule-template.xlsx')
    })
  })

  describe('useKeyboardShortcuts', () => {
    it('should initialize with correct state', () => {
      const { shortcuts, isEnabled } = useKeyboardShortcuts()
      
      expect(shortcuts.value.size).toBe(0)
      expect(isEnabled.value).toBe(true)
    })

    it('should register shortcuts correctly', () => {
      const { shortcuts, registerShortcut } = useKeyboardShortcuts()
      const action = vi.fn()
      
      const id = registerShortcut({
        key: 's',
        ctrl: true,
        description: '保存',
        action
      })
      
      expect(shortcuts.value.size).toBe(1)
      expect(shortcuts.value.has(id)).toBe(true)
      expect(id).toBe('ctrl+s')
    })

    it('should unregister shortcuts correctly', () => {
      const { shortcuts, registerShortcut, unregisterShortcut } = useKeyboardShortcuts()
      
      const id = registerShortcut({
        key: 'o',
        ctrl: true,
        description: '打开',
        action: vi.fn()
      })
      
      expect(shortcuts.value.size).toBe(1)
      
      unregisterShortcut(id)
      expect(shortcuts.value.size).toBe(0)
    })

    it('should generate correct shortcut display text', () => {
      const { getShortcutDisplayText } = useKeyboardShortcuts()
      
      const config1 = {
        key: 's',
        ctrl: true,
        description: '保存',
        action: vi.fn()
      }
      
      const config2 = {
        key: 'F1',
        description: '帮助',
        action: vi.fn()
      }
      
      expect(getShortcutDisplayText(config1)).toBe('Ctrl + S')
      expect(getShortcutDisplayText(config2)).toBe('F1')
    })

    it('should provide common shortcuts', () => {
      const { commonShortcuts } = useKeyboardShortcuts()
      const action = vi.fn()
      
      const selectFilesShortcut = commonShortcuts.selectFiles(action)
      const saveShortcut = commonShortcuts.selectAll(action)
      
      expect(selectFilesShortcut.key).toBe('o')
      expect(selectFilesShortcut.ctrl).toBe(true)
      expect(saveShortcut.key).toBe('a')
      expect(saveShortcut.ctrl).toBe(true)
    })
  })
})
