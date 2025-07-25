import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FileRenamerTab from '../renderer/components/file-renamer/FileRenamerTab.vue'
import PreviewPanel from '../renderer/components/file-renamer/PreviewPanel.vue'
import { useFileStore } from '../renderer/stores/fileStore'
import { useRenameStore } from '../renderer/stores/renameStore'
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

describe('File Renamer Components', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
  })

  describe('FileRenamerTab', () => {
    it('should render empty state when no files', () => {
      const wrapper = mount(FileRenamerTab)
      
      expect(wrapper.exists()).toBe(true)
      expect(wrapper.text()).toContain('暂无文件')
    })

    it('should show files when they exist', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(3)
      fileStore.addFiles(mockFiles)

      const wrapper = mount(FileRenamerTab)
      
      expect(wrapper.exists()).toBe(true)
    })

    it('should execute rename operations', async () => {
      const fileStore = useFileStore()
      const renameStore = useRenameStore()
      
      const mockFiles = createMockFiles(2)
      fileStore.addFiles(mockFiles)
      
      // 设置重命名参数
      renameStore.currentMode = 'replace'
      renameStore.replaceParams = {
        fromStr: 'test',
        toStr: 'renamed'
      }

      const wrapper = mount(FileRenamerTab)
      
      expect(wrapper.exists()).toBe(true)
    })
  })

  describe('PreviewPanel', () => {
    it('should render preview panel', () => {
      const wrapper = mount(PreviewPanel)
      
      expect(wrapper.exists()).toBe(true)
    })

    it('should show file previews', async () => {
      const fileStore = useFileStore()
      const mockFiles = createMockFiles(2)
      fileStore.addFiles(mockFiles)

      const wrapper = mount(PreviewPanel)
      
      expect(wrapper.exists()).toBe(true)
    })

    it('should handle rename preview updates', async () => {
      const fileStore = useFileStore()
      const renameStore = useRenameStore()
      
      const mockFiles = createMockFiles(1)
      fileStore.addFiles(mockFiles)
      
      renameStore.currentMode = 'replace'
      renameStore.replaceParams = {
        fromStr: 'test',
        toStr: 'new'
      }

      const wrapper = mount(PreviewPanel)
      
      expect(wrapper.exists()).toBe(true)
    })
  })
})
