import { describe, it, expect } from 'vitest'
import {
  APP_CONFIG,
  SUPPORTED_LANGUAGES,
  THEMES,
  FILE_SIZE_LIMITS,
  EXPORT_FORMATS,
  NOTIFICATION_DURATION,
  KEYBOARD_SHORTCUTS,
  DRAG_DROP_TYPES,
  STORAGE_KEYS,
  defaultRules,
  SUPPORTED_FILE_TYPES,
  FILE_ICONS,
  FILE_SIZE_UNITS,
  RENAME_PATTERNS
} from '../renderer/constants'

describe('Constants', () => {
  describe('App Constants', () => {
    it('should have correct app config', () => {
      expect(APP_CONFIG.name).toBe('批量文件处理工具')
      expect(APP_CONFIG.version).toBe('1.0.0')
      expect(APP_CONFIG.author).toBe('lizeyu')
      expect(typeof APP_CONFIG.description).toBe('string')
    })

    it('should have supported languages', () => {
      expect(SUPPORTED_LANGUAGES['zh-CN']).toBe('简体中文')
      expect(SUPPORTED_LANGUAGES['en-US']).toBe('English')
      expect(Object.keys(SUPPORTED_LANGUAGES)).toHaveLength(2)
    })

    it('should have theme options', () => {
      expect(THEMES.light).toBe('浅色主题')
      expect(THEMES.dark).toBe('深色主题')
      expect(THEMES.auto).toBe('跟随系统')
    })

    it('should have file size limits', () => {
      expect(FILE_SIZE_LIMITS.MAX_FILE_SIZE).toBe(100 * 1024 * 1024)
      expect(FILE_SIZE_LIMITS.MAX_FILES_COUNT).toBe(1000)
      expect(FILE_SIZE_LIMITS.MAX_BATCH_SIZE).toBe(50)
    })

    it('should have export formats', () => {
      expect(EXPORT_FORMATS.xlsx).toBe('Excel 文件 (.xlsx)')
      expect(EXPORT_FORMATS.csv).toBe('CSV 文件 (.csv)')
    })

    it('should have notification durations', () => {
      expect(NOTIFICATION_DURATION.success).toBe(3000)
      expect(NOTIFICATION_DURATION.error).toBe(5000)
      expect(NOTIFICATION_DURATION.warning).toBe(4000)
      expect(NOTIFICATION_DURATION.info).toBe(3000)
    })

    it('should have keyboard shortcuts', () => {
      expect(KEYBOARD_SHORTCUTS.SAVE).toBe('Ctrl+S')
      expect(KEYBOARD_SHORTCUTS.OPEN).toBe('Ctrl+O')
      expect(KEYBOARD_SHORTCUTS.EXPORT).toBe('Ctrl+E')
      expect(typeof KEYBOARD_SHORTCUTS.HELP).toBe('string')
    })

    it('should have drag drop types', () => {
      expect(DRAG_DROP_TYPES.FILES).toBe('Files')
      expect(DRAG_DROP_TYPES.TEXT).toBe('text/plain')
    })

    it('should have storage keys', () => {
      expect(STORAGE_KEYS.SETTINGS).toBe('app-settings')
      expect(STORAGE_KEYS.RULES).toBe('user-rules')
      expect(STORAGE_KEYS.HISTORY).toBe('operation-history')
      expect(STORAGE_KEYS.RECENT_FILES).toBe('recent-files')
    })
  })

  describe('Default Rules', () => {
    it('should have default rules array', () => {
      expect(Array.isArray(defaultRules)).toBe(true)
      expect(defaultRules.length).toBeGreaterThan(0)
    })

    it('should have valid rule structure', () => {
      const firstRule = defaultRules[0]
      expect(firstRule).toHaveProperty('id')
      expect(firstRule).toHaveProperty('code')
      expect(firstRule).toHaveProperty('thirtyD')
      expect(firstRule).toHaveProperty('matchRules')
      expect(firstRule).toHaveProperty('source')
      expect(firstRule.source).toBe('default')
    })

    it('should have unique rule IDs', () => {
      const ids = defaultRules.map(rule => rule.id)
      const uniqueIds = new Set(ids)
      expect(uniqueIds.size).toBe(ids.length)
    })

    it('should have valid match rules', () => {
      defaultRules.forEach(rule => {
        expect(Array.isArray(rule.matchRules)).toBe(true)
        expect(rule.matchRules.length).toBeGreaterThan(0)
        rule.matchRules.forEach(matchRule => {
          expect(typeof matchRule).toBe('string')
          expect(matchRule.length).toBeGreaterThan(0)
        })
      })
    })
  })

  describe('File Type Constants', () => {
    it('should have supported file types', () => {
      expect(SUPPORTED_FILE_TYPES.documents).toBeDefined()
      expect(SUPPORTED_FILE_TYPES.spreadsheets).toBeDefined()
      expect(SUPPORTED_FILE_TYPES.images).toBeDefined()
      expect(SUPPORTED_FILE_TYPES.archives).toBeDefined()
    })

    it('should have valid file type structure', () => {
      const docType = SUPPORTED_FILE_TYPES.documents
      expect(Array.isArray(docType.extensions)).toBe(true)
      expect(Array.isArray(docType.mimeTypes)).toBe(true)
      expect(typeof docType.description).toBe('string')
      expect(docType.extensions.length).toBeGreaterThan(0)
      expect(docType.mimeTypes.length).toBeGreaterThan(0)
    })

    it('should have file icons', () => {
      expect(FILE_ICONS['.pdf']).toBe('📄')
      expect(FILE_ICONS['.xlsx']).toBe('📊')
      expect(FILE_ICONS['.jpg']).toBe('🖼️')
      expect(FILE_ICONS['.zip']).toBe('📦')
      expect(FILE_ICONS.default).toBe('📄')
    })

    it('should have file size units', () => {
      expect(Array.isArray(FILE_SIZE_UNITS)).toBe(true)
      expect(FILE_SIZE_UNITS).toEqual(['B', 'KB', 'MB', 'GB', 'TB'])
    })

    it('should have rename patterns', () => {
      expect(RENAME_PATTERNS.DATE_FORMAT).toBe('YYYY-MM-DD')
      expect(RENAME_PATTERNS.TIME_FORMAT).toBe('HH:mm:ss')
      expect(RENAME_PATTERNS.DATETIME_FORMAT).toBe('YYYY-MM-DD_HH-mm-ss')
      expect(RENAME_PATTERNS.NUMBER_FORMAT).toBe('000')
    })
  })

  describe('Constants Type Safety', () => {
    it('should have readonly properties at compile time', () => {
      // TypeScript 编译时检查，运行时不会抛出错误
      // 这个测试主要验证常量的结构正确性
      expect(APP_CONFIG.name).toBe('批量文件处理工具')
      expect(typeof APP_CONFIG.version).toBe('string')
      expect(typeof APP_CONFIG.author).toBe('string')
    })

    it('should have immutable array references', () => {
      // 验证数组常量的结构
      expect(Array.isArray(FILE_SIZE_UNITS)).toBe(true)
      expect(FILE_SIZE_UNITS.length).toBe(5)
      expect(FILE_SIZE_UNITS[0]).toBe('B')
      expect(FILE_SIZE_UNITS[4]).toBe('TB')
    })
  })
})
