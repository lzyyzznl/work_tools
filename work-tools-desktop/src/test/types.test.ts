import { describe, it, expect } from 'vitest'
import type {
  AppSettings,
  TabItem,
  DialogOptions,
  ToastMessage,
  ExportOptions,
  ElectronAPI,
  FileSelectOptions,
  FileItem,
  MatchInfo,
  FileStats,
  ElectronFileHandle,
  FileOperationResult,
  DirectoryInfo,
  Rule,
  RuleConfig,
  MatchResult,
  RuleValidationResult,
  RuleImportResult,
  RuleExportResult,
  RuleFormData,
  RenameOperationType,
  ReplaceParams,
  AddParams,
  NumberParams,
  DeleteParams,
  RenameOperation,
  RenameHistory,
  RenamePreview,
  BatchRenameResult
} from '../renderer/types'

describe('Type Definitions', () => {
  describe('Common Types', () => {
    it('should validate AppSettings type', () => {
      const settings: AppSettings = {
        theme: 'light',
        language: 'zh-CN',
        shortcuts: { 'ctrl+s': 'save' },
        autoPreview: true,
        confirmBeforeExecute: false
      }
      
      expect(settings.theme).toBe('light')
      expect(settings.language).toBe('zh-CN')
      expect(settings.shortcuts).toEqual({ 'ctrl+s': 'save' })
      expect(settings.autoPreview).toBe(true)
      expect(settings.confirmBeforeExecute).toBe(false)
    })

    it('should validate TabItem type', () => {
      const tab: TabItem = {
        id: 'tab-1',
        label: '文件匹配',
        component: 'FileMatcherTab',
        icon: '📁'
      }
      
      expect(tab.id).toBe('tab-1')
      expect(tab.label).toBe('文件匹配')
      expect(tab.component).toBe('FileMatcherTab')
      expect(tab.icon).toBe('📁')
    })

    it('should validate DialogOptions type', () => {
      const dialog: DialogOptions = {
        title: '确认删除',
        message: '确定要删除这些文件吗？',
        type: 'confirm',
        confirmText: '确定',
        cancelText: '取消'
      }
      
      expect(dialog.type).toBe('confirm')
      expect(dialog.title).toBe('确认删除')
    })

    it('should validate ToastMessage type', () => {
      const toast: ToastMessage = {
        id: 'toast-1',
        type: 'success',
        message: '操作成功',
        duration: 3000
      }
      
      expect(toast.type).toBe('success')
      expect(toast.duration).toBe(3000)
    })

    it('should validate ExportOptions type', () => {
      const options: ExportOptions = {
        format: 'xlsx',
        filename: 'export.xlsx',
        includeHeaders: true
      }
      
      expect(options.format).toBe('xlsx')
      expect(options.includeHeaders).toBe(true)
    })
  })

  describe('File Types', () => {
    it('should validate FileItem type', () => {
      const mockFile = new File(['content'], 'test.txt')
      const fileItem: FileItem = {
        id: 'file-1',
        name: 'test.txt',
        path: '/path/to/test.txt',
        size: 1024,
        lastModified: Date.now(),
        file: mockFile,
        matched: true,
        selected: false
      }
      
      expect(fileItem.name).toBe('test.txt')
      expect(fileItem.matched).toBe(true)
      expect(fileItem.selected).toBe(false)
    })

    it('should validate FileStats type', () => {
      const stats: FileStats = {
        total: 10,
        matched: 7,
        unmatched: 3,
        selected: 2
      }
      
      expect(stats.total).toBe(10)
      expect(stats.matched + stats.unmatched).toBe(stats.total)
    })

    it('should validate ElectronFileHandle type', () => {
      const handle: ElectronFileHandle = {
        path: '/path/to/file.txt',
        name: 'file.txt',
        size: 2048,
        lastModified: Date.now(),
        type: 'text/plain'
      }
      
      expect(handle.name).toBe('file.txt')
      expect(handle.type).toBe('text/plain')
    })
  })

  describe('Rule Types', () => {
    it('should validate Rule type', () => {
      const rule: Rule = {
        id: 'rule-1',
        code: 'TEST001',
        thirtyD: '测试规则',
        matchRules: ['*.txt', '*.doc'],
        source: 'user'
      }
      
      expect(rule.source).toBe('user')
      expect(rule.matchRules).toHaveLength(2)
    })

    it('should validate MatchResult type', () => {
      const result: MatchResult = {
        matched: true,
        matchInfo: {
          code: 'TEST001',
          thirtyD: '测试规则',
          matchedRule: '*.txt'
        }
      }
      
      expect(result.matched).toBe(true)
      expect(result.matchInfo?.code).toBe('TEST001')
    })
  })

  describe('Rename Types', () => {
    it('should validate RenameOperationType', () => {
      const types: RenameOperationType[] = ['replace', 'add', 'number', 'delete']
      
      types.forEach(type => {
        expect(['replace', 'add', 'number', 'delete']).toContain(type)
      })
    })

    it('should validate ReplaceParams type', () => {
      const params: ReplaceParams = {
        fromStr: 'old',
        toStr: 'new'
      }
      
      expect(params.fromStr).toBe('old')
      expect(params.toStr).toBe('new')
    })

    it('should validate RenameOperation type', () => {
      const operation: RenameOperation = {
        type: 'replace',
        params: {
          fromStr: 'test',
          toStr: 'demo'
        } as ReplaceParams
      }
      
      expect(operation.type).toBe('replace')
      expect((operation.params as ReplaceParams).fromStr).toBe('test')
    })

    it('should validate BatchRenameResult type', () => {
      const result: BatchRenameResult = {
        success: true,
        totalFiles: 5,
        successCount: 4,
        failedCount: 1,
        errors: [
          {
            file: 'error.txt',
            error: 'Permission denied'
          }
        ]
      }
      
      expect(result.success).toBe(true)
      expect(result.successCount + result.failedCount).toBe(result.totalFiles)
      expect(result.errors).toHaveLength(1)
    })
  })
})
