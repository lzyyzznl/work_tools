import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import App from '../renderer/App.vue'
import { useFileStore } from '../renderer/stores/fileStore'
import { useRuleStore } from '../renderer/stores/ruleStore'

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

describe('App', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorageMock.getItem.mockClear()
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    localStorageMock.clear.mockClear()
  })

  it('should render main application', () => {
    const wrapper = mount(App)
    
    expect(wrapper.exists()).toBe(true)
    expect(wrapper.find('.app').exists()).toBe(true)
    expect(wrapper.text()).toContain('工作工具')
  })

  it('should show navigation tabs', () => {
    const wrapper = mount(App)
    
    expect(wrapper.text()).toContain('文件匹配器')
    expect(wrapper.text()).toContain('文件重命名器')
  })

  it('should switch between tabs', async () => {
    const wrapper = mount(App)
    
    // 默认应该显示文件匹配器
    expect(wrapper.vm.activeTab).toBe('matcher')
    
    // 点击重命名器标签
    const renamerTab = wrapper.findAll('button').find(btn => 
      btn.text().includes('文件重命名器')
    )
    
    if (renamerTab) {
      await renamerTab.trigger('click')
      expect(wrapper.vm.activeTab).toBe('renamer')
    }
  })

  it('should display file and rule statistics', () => {
    const fileStore = useFileStore()
    const ruleStore = useRuleStore()
    
    const wrapper = mount(App)
    
    expect(wrapper.text()).toContain('文件:')
    expect(wrapper.text()).toContain('规则:')
    expect(wrapper.text()).toContain(fileStore.fileStats.total.toString())
    expect(wrapper.text()).toContain(ruleStore.ruleCount.toString())
  })

  it('should show keyboard shortcuts', () => {
    const wrapper = mount(App)
    
    expect(wrapper.text()).toContain('Ctrl+1')
    expect(wrapper.text()).toContain('Ctrl+2')
  })

  it('should render notification container', () => {
    const wrapper = mount(App)
    
    expect(wrapper.findComponent({ name: 'NotificationContainer' }).exists()).toBe(true)
  })
})
