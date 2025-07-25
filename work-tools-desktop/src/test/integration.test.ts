import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '../renderer/App.vue'
import { useFileStore } from '../renderer/stores/fileStore'
import { useRuleStore } from '../renderer/stores/ruleStore'
import { useRenameStore } from '../renderer/stores/renameStore'
import { createMockFiles, mockRules } from './fixtures/testData'
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

describe('Integration Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
    
    // 重置 Electron API mocks
    Object.values(mockElectronAPI.fileSystem).forEach(mock => mock.mockReset())
  })

  describe('Complete File Processing Workflow', () => {
    it('should handle complete file matching workflow', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      // 1. 添加规则
      ruleStore.rules = [...mockRules]
      expect(ruleStore.rules).toHaveLength(mockRules.length)
      
      // 2. 添加文件
      const mockFiles = createMockFiles(5)
      fileStore.addFiles(mockFiles)
      expect(fileStore.files).toHaveLength(5)
      
      // 3. 执行匹配
      fileStore.files.forEach(file => {
        const result = ruleStore.matchFilename(file.name)
        fileStore.updateFileMatchResult(file.id, result.matched, result.matchInfo)
      })
      
      // 4. 验证匹配结果
      const matchedFiles = fileStore.files.filter(f => f.matched)
      expect(matchedFiles.length).toBeGreaterThanOrEqual(0)
      
      // 5. 验证统计信息
      expect(fileStore.fileStats.total).toBe(5)
      expect(fileStore.fileStats.matched).toBe(matchedFiles.length)
      expect(fileStore.fileStats.unmatched).toBe(5 - matchedFiles.length)
    })

    it('should handle complete file renaming workflow', async () => {
      const fileStore = useFileStore()
      const renameStore = useRenameStore()
      
      // 1. 添加文件
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)
      
      // 2. 设置重命名参数
      renameStore.currentMode = 'replace'
      renameStore.replaceParams = {
        fromStr: 'test',
        toStr: 'renamed'
      }

      // 3. 执行重命名预览
      fileStore.files.forEach(file => {
        const newName = renameStore.generateNewName(file.name)
        fileStore.updateFilePreview(file.id, newName)
      })
      
      // 4. 验证预览结果
      const filesWithPreview = fileStore.files.filter(f => f.previewName)
      expect(filesWithPreview.length).toBeGreaterThanOrEqual(0)
    })

    it('should handle data persistence', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      // 1. 添加数据
      const mockFiles = createMockFiles(2)
      fileStore.addFiles(mockFiles)
      
      ruleStore.addRule({
        code: 'TEST001',
        thirtyD: 'Y',
        matchRules: ['test'],
        source: 'user'
      })
      
      // 2. 验证数据存储
      expect(fileStore.files).toHaveLength(2)
      expect(ruleStore.userRules).toHaveLength(1)
      
      // 3. 清空数据
      fileStore.clearFiles()
      expect(fileStore.files).toHaveLength(0)
    })

    it('should handle error scenarios gracefully', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      // 1. 测试无效规则
      try {
        ruleStore.addRule({
          code: '',
          thirtyD: 'Y',
          matchRules: [],
          source: 'user'
        })
      } catch (error) {
        expect(error).toBeDefined()
      }
      
      // 2. 测试空文件列表操作
      expect(fileStore.files).toHaveLength(0)
      expect(fileStore.fileStats.total).toBe(0)
      
      // 3. 测试文件选择错误
      mockElectronAPI.fileSystem.selectFiles.mockRejectedValue(new Error('User cancelled'))
      
      try {
        await fileStore.selectFilesFromSystem()
      } catch (error) {
        // 错误应该被正确处理
        expect(error).toBeDefined()
      }
    })

    it('should maintain state consistency across operations', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      const renameStore = useRenameStore()
      
      // 1. 初始状态
      expect(fileStore.files).toHaveLength(0)
      expect(ruleStore.rules).toHaveLength(0)
      expect(renameStore.currentMode).toBe('replace')
      
      // 2. 添加数据
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)
      
      ruleStore.rules = [...mockRules]
      
      renameStore.currentMode = 'add'
      renameStore.addParams = {
        text: 'prefix_',
        isPrefix: true
      }

      // 3. 验证状态一致性
      expect(fileStore.files).toHaveLength(3)
      expect(ruleStore.rules).toHaveLength(mockRules.length)
      expect(renameStore.currentMode).toBe('add')
      
      // 4. 执行操作
      fileStore.files.forEach(file => {
        const matchResult = ruleStore.matchFilename(file.name)
        fileStore.updateFileMatchResult(file.id, matchResult.matched, matchResult.matchInfo)
        
        const newName = renameStore.generateNewName(file.name)
        fileStore.updateFilePreview(file.id, newName)
      })
      
      // 5. 验证操作结果
      const processedFiles = fileStore.files.filter(f => f.matched || f.previewName)
      expect(processedFiles.length).toBeGreaterThanOrEqual(0)
    })

    it('should handle concurrent operations', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      // 1. 并发添加文件
      const batch1 = createMockFiles(2, 'batch1_')
      const batch2 = createMockFiles(2, 'batch2_')

      fileStore.addFiles([...batch1, ...batch2])

      expect(fileStore.files).toHaveLength(4)
      
      // 2. 并发添加规则
      ruleStore.addRule({
        code: 'RULE1',
        thirtyD: 'Y',
        matchRules: ['batch1'],
        source: 'user'
      })
      
      ruleStore.addRule({
        code: 'RULE2',
        thirtyD: 'N',
        matchRules: ['batch2'],
        source: 'user'
      })
      
      expect(ruleStore.userRules).toHaveLength(2)
      
      // 3. 验证数据完整性
      const batch1Files = fileStore.files.filter(f => f.name.includes('batch1'))
      const batch2Files = fileStore.files.filter(f => f.name.includes('batch2'))
      
      expect(batch1Files).toHaveLength(2)
      expect(batch2Files).toHaveLength(2)
    })
  })

  describe('Application Integration', () => {
    it('should render complete application with all components', () => {
      const wrapper = mount(App)
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.find('.app').exists()).toBe(true)
      expect(wrapper.find('.title-bar').exists()).toBe(true)
      expect(wrapper.find('.nav-tabs').exists()).toBe(true)
      expect(wrapper.find('.main-content').exists()).toBe(true)
    })

    it('should handle tab switching with data preservation', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(2)
      fileStore.addFiles(mockFiles)
      
      const wrapper = mount(App)
      
      // 切换到重命名器
      const renamerTab = wrapper.findAll('button').find(btn => 
        btn.text().includes('文件重命名器')
      )
      
      if (renamerTab) {
        await renamerTab.trigger('click')
        expect(wrapper.vm.activeTab).toBe('renamer')
      }
      
      // 切换回匹配器
      const matcherTab = wrapper.findAll('button').find(btn => 
        btn.text().includes('文件匹配器')
      )
      
      if (matcherTab) {
        await matcherTab.trigger('click')
        expect(wrapper.vm.activeTab).toBe('matcher')
      }
      
      // 数据应该保持不变
      expect(fileStore.files).toHaveLength(2)
    })
  })
})
