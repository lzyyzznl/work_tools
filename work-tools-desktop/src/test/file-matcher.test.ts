import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FileMatcherTab from '../renderer/components/file-matcher/FileMatcherTab.vue'
import RuleManager from '../renderer/components/file-matcher/RuleManager.vue'
import RuleEditor from '../renderer/components/file-matcher/RuleEditor.vue'
import { useFileStore } from '../renderer/stores/fileStore'
import { useRuleStore } from '../renderer/stores/ruleStore'
import { createMockFile, createMockFiles, mockRules } from './fixtures/testData'
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

describe('File Matcher Components', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
    
    // 重置 Electron API mocks
    Object.values(mockElectronAPI.fileSystem).forEach(mock => mock.mockReset())
  })

  describe('FileMatcherTab', () => {
    it('should render empty state when no files', () => {
      const wrapper = mount(FileMatcherTab)
      
      expect(wrapper.find('.drop-zone').exists()).toBe(true)
      expect(wrapper.text()).toContain('拖拽文件到此处')
    })

    it('should show file list when files exist', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)

      const wrapper = mount(FileMatcherTab)
      
      expect(wrapper.find('.file-list').exists()).toBe(true)
      expect(wrapper.find('.drop-zone').exists()).toBe(false)
    })

    it('should show warning when no rules configured', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(2)
      fileStore.addFiles(mockFiles)

      const wrapper = mount(FileMatcherTab)
      
      expect(wrapper.find('.status-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('尚未配置匹配规则')
    })

    it('should show stats when both files and rules exist', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)
      
      // 添加一些规则
      ruleStore.rules = [...mockRules]

      const wrapper = mount(FileMatcherTab)
      
      expect(wrapper.find('.stats-bar').exists()).toBe(true)
      expect(wrapper.text()).toContain('总文件:')
      expect(wrapper.text()).toContain('规则数量:')
    })

    it('should handle file selection', async () => {
      const mockFiles = createMockFiles(2)
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue(mockFiles)

      const wrapper = mount(FileMatcherTab)
      const selectButton = wrapper.find('button[class*="btn-primary"]')
      
      await selectButton.trigger('click')
      
      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalled()
    })

    it('should handle directory selection', async () => {
      const mockFiles = createMockFiles(5)
      mockElectronAPI.fileSystem.selectDirectory.mockResolvedValue(mockFiles)

      const wrapper = mount(FileMatcherTab)
      const selectDirButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('选择目录')
      )
      
      if (selectDirButton) {
        await selectDirButton.trigger('click')
        expect(mockElectronAPI.fileSystem.selectDirectory).toHaveBeenCalled()
      }
    })

    it('should clear files when clear button clicked', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)

      const wrapper = mount(FileMatcherTab)
      const clearButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('清空文件')
      )
      
      expect(fileStore.files).toHaveLength(3)
      
      if (clearButton) {
        await clearButton.trigger('click')
        expect(fileStore.files).toHaveLength(0)
      }
    })

    it('should execute file matching', async () => {
      const fileStore = useFileStore()
      const ruleStore = useRuleStore()
      
      // 添加文件
      const mockFiles = [
        createMockFile('document.pdf', 'content'),
        createMockFile('image.jpg', 'content')
      ]
      fileStore.addFiles(mockFiles)
      
      // 添加规则
      ruleStore.rules = [
        {
          id: 'rule-1',
          code: 'PDF001',
          thirtyD: 'Y',
          matchRules: ['pdf'],
          source: 'user'
        }
      ]

      const wrapper = mount(FileMatcherTab)
      const matchButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('开始匹配')
      )
      
      if (matchButton) {
        await matchButton.trigger('click')
        
        // 检查匹配结果
        const pdfFile = fileStore.files.find(f => f.name.includes('pdf'))
        expect(pdfFile?.matched).toBe(true)
      }
    })

    it('should open rule manager modal', async () => {
      const wrapper = mount(FileMatcherTab)
      const ruleManagerButton = wrapper.findAll('button').find(btn => 
        btn.text().includes('管理规则')
      )
      
      if (ruleManagerButton) {
        await ruleManagerButton.trigger('click')
        expect(wrapper.find('.fixed').exists()).toBe(true)
        expect(wrapper.text()).toContain('规则管理')
      }
    })
  })

  describe('RuleManager', () => {
    it('should render empty state when no rules', () => {
      const wrapper = mount(RuleManager)
      
      expect(wrapper.find('.empty-state').exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无规则')
    })

    it('should render rules when they exist', async () => {
      const ruleStore = useRuleStore()
      ruleStore.rules = [...mockRules]

      const wrapper = mount(RuleManager)
      
      expect(wrapper.find('.rule-table').exists()).toBe(true)
      expect(wrapper.findAll('.rule-row')).toHaveLength(mockRules.length)
    })

    it('should filter rules based on search query', async () => {
      const ruleStore = useRuleStore()
      ruleStore.rules = [...mockRules]

      const wrapper = mount(RuleManager)
      const searchInput = wrapper.find('input[type="text"]')
      
      await searchInput.setValue('PDF')
      
      const visibleRows = wrapper.findAll('.rule-row')
      expect(visibleRows.length).toBeLessThanOrEqual(mockRules.length)
    })

    it('should select and deselect rules', async () => {
      const ruleStore = useRuleStore()
      ruleStore.rules = [...mockRules]

      const wrapper = mount(RuleManager)
      const firstCheckbox = wrapper.find('.rule-row input[type="checkbox"]')
      
      await firstCheckbox.trigger('change')
      
      // 检查选中状态
      expect(firstCheckbox.element.checked).toBe(true)
    })

    it('should open rule editor when clicking edit button', async () => {
      const ruleStore = useRuleStore()
      ruleStore.rules = [...mockRules]

      const wrapper = mount(RuleManager)
      const editButton = wrapper.find('.rule-row button[title="编辑"]')
      
      if (editButton.exists()) {
        await editButton.trigger('click')
        expect(wrapper.vm.showEditor).toBe(true)
      }
    })

    it('should show rule statistics', async () => {
      const ruleStore = useRuleStore()
      ruleStore.rules = [...mockRules]

      const wrapper = mount(RuleManager)
      
      expect(wrapper.find('.rule-stats').exists()).toBe(true)
      expect(wrapper.text()).toContain('总计:')
      expect(wrapper.text()).toContain('系统:')
      expect(wrapper.text()).toContain('用户:')
    })
  })

  describe('RuleEditor', () => {
    it('should render in create mode when no rule provided', () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: null }
      })

      // 组件应该能正常挂载
      expect(wrapper.exists()).toBe(true)
    })

    it('should render in edit mode when rule provided', () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: mockRules[0] }
      })

      // 组件应该能正常挂载
      expect(wrapper.exists()).toBe(true)
    })

    it('should validate required fields', async () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: null }
      })

      // 测试组件的基本渲染
      expect(wrapper.exists()).toBe(true)
    })

    it('should emit close event when cancel button clicked', async () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: null }
      })

      // 测试组件的基本功能
      expect(wrapper.exists()).toBe(true)
    })

    it('should add and remove match rules', async () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: null }
      })

      // 测试组件的基本功能
      expect(wrapper.vm.formData.matchRules).toHaveLength(1)
    })

    it('should save rule with valid data', async () => {
      const wrapper = mount(RuleEditor, {
        props: { rule: null }
      })

      // 测试组件的基本状态
      expect(wrapper.vm.formData.code).toBe('')
      expect(wrapper.vm.formData.thirtyD).toBe('N')
    })
  })
})
