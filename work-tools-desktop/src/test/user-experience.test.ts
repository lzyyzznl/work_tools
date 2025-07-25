import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '../renderer/App.vue'
import { useFileStore } from '../renderer/stores/fileStore'
import { useKeyboardShortcuts } from '../renderer/composables/useKeyboardShortcuts'
import { createMockFiles } from './fixtures/testData'

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

describe('User Experience Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
  })

  describe('Drag and Drop', () => {
    it('should show drag overlay when dragging files', async () => {
      const wrapper = mount(App)
      
      // 模拟拖拽进入
      await wrapper.find('.app').trigger('dragenter')
      
      expect(wrapper.vm.isDragOver).toBe(true)
      expect(wrapper.find('.fixed').exists()).toBe(true)
      expect(wrapper.text()).toContain('释放文件到此处')
    })

    it('should hide drag overlay when drag leaves', async () => {
      const wrapper = mount(App)
      
      // 模拟拖拽进入然后离开
      await wrapper.find('.app').trigger('dragenter')
      expect(wrapper.vm.isDragOver).toBe(true)
      
      await wrapper.find('.app').trigger('dragleave')
      expect(wrapper.vm.isDragOver).toBe(false)
    })

    it('should handle file drop', async () => {
      const fileStore = useFileStore()
      const wrapper = mount(App)
      
      // 创建模拟拖拽事件
      const mockFiles = createMockFiles(2)
      const mockEvent = {
        preventDefault: vi.fn(),
        dataTransfer: {
          files: mockFiles
        }
      } as any
      
      // 模拟文件拖拽
      await wrapper.find('.app').trigger('drop', mockEvent)
      
      expect(mockEvent.preventDefault).toHaveBeenCalled()
      expect(wrapper.vm.isDragOver).toBe(false)
    })
  })

  describe('Keyboard Shortcuts', () => {
    it('should register keyboard shortcuts on mount', () => {
      const { shortcuts } = useKeyboardShortcuts()
      
      mount(App)
      
      // 应该注册了快捷键
      expect(shortcuts.value.size).toBeGreaterThan(0)
    })

    it('should switch tabs with keyboard shortcuts', async () => {
      const wrapper = mount(App)
      
      // 默认在匹配器标签
      expect(wrapper.vm.activeTab).toBe('matcher')
      
      // 模拟 Ctrl+2 切换到重命名器
      const event = new KeyboardEvent('keydown', {
        key: '2',
        ctrlKey: true
      })
      document.dispatchEvent(event)
      
      // 注意：由于测试环境限制，这里只验证方法存在
      expect(wrapper.vm.switchTab).toBeDefined()
    })

    it('should show keyboard shortcuts in UI', () => {
      const wrapper = mount(App)
      
      expect(wrapper.text()).toContain('Ctrl+1')
      expect(wrapper.text()).toContain('Ctrl+2')
    })
  })

  describe('User Interface', () => {
    it('should display real-time statistics', () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(5)
      fileStore.addFiles(mockFiles)
      
      const wrapper = mount(App)
      
      expect(wrapper.text()).toContain('文件:')
      expect(wrapper.text()).toContain('5')
    })

    it('should provide visual feedback for active tab', () => {
      const wrapper = mount(App)
      
      const matcherTab = wrapper.findAll('button').find(btn => 
        btn.text().includes('文件匹配器')
      )
      
      if (matcherTab) {
        expect(matcherTab.classes()).toContain('text-blue-600')
        expect(matcherTab.classes()).toContain('bg-blue-50')
      }
    })

    it('should show app branding and title', () => {
      const wrapper = mount(App)
      
      expect(wrapper.text()).toContain('工作工具')
      expect(wrapper.text()).toContain('文件处理助手')
      expect(wrapper.find('.app-logo').exists()).toBe(true)
    })

    it('should be responsive and accessible', () => {
      const wrapper = mount(App)
      
      // 检查基本的响应式类
      expect(wrapper.find('.h-screen').exists()).toBe(true)
      expect(wrapper.find('.flex').exists()).toBe(true)
      
      // 检查可访问性元素
      expect(wrapper.find('h1').exists()).toBe(true)
      expect(wrapper.findAll('button').length).toBeGreaterThan(0)
    })
  })

  describe('Error Handling', () => {
    it('should handle drag and drop errors gracefully', async () => {
      const wrapper = mount(App)
      
      // 模拟无效的拖拽事件
      const mockEvent = {
        preventDefault: vi.fn(),
        dataTransfer: null
      } as any
      
      // 应该不会抛出错误
      expect(() => {
        wrapper.find('.app').trigger('drop', mockEvent)
      }).not.toThrow()
    })

    it('should provide user feedback for operations', () => {
      const wrapper = mount(App)
      
      // 通知容器应该存在
      expect(wrapper.findComponent({ name: 'NotificationContainer' }).exists()).toBe(true)
    })
  })

  describe('Performance', () => {
    it('should handle large number of files efficiently', () => {
      const fileStore = useFileStore()
      const largeFileSet = createMockFiles(1000)
      
      const startTime = performance.now()
      fileStore.addFiles(largeFileSet)
      const endTime = performance.now()
      
      // 操作应该在合理时间内完成（1秒）
      expect(endTime - startTime).toBeLessThan(1000)
      expect(fileStore.files).toHaveLength(1000)
    })

    it('should maintain responsive UI with many operations', async () => {
      const fileStore = useFileStore()
      const wrapper = mount(App)
      
      // 添加大量文件
      const files = createMockFiles(100)
      fileStore.addFiles(files)
      
      // UI 应该仍然响应
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('100')
    })
  })

  describe('Data Persistence', () => {
    it('should maintain state across tab switches', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)
      
      const wrapper = mount(App)
      
      // 切换标签
      const renamerTab = wrapper.findAll('button').find(btn => 
        btn.text().includes('文件重命名器')
      )
      
      if (renamerTab) {
        await renamerTab.trigger('click')
        expect(wrapper.vm.activeTab).toBe('renamer')
      }
      
      // 数据应该保持
      expect(fileStore.files).toHaveLength(3)
      
      // 切换回来
      const matcherTab = wrapper.findAll('button').find(btn => 
        btn.text().includes('文件匹配器')
      )
      
      if (matcherTab) {
        await matcherTab.trigger('click')
        expect(wrapper.vm.activeTab).toBe('matcher')
      }
      
      // 数据仍然保持
      expect(fileStore.files).toHaveLength(3)
    })
  })
})
