import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import { defineComponent } from 'vue'

// 测试组件，用于验证 UnoCSS 类的应用
const TestComponent = defineComponent({
  template: `
    <div class="page-container">
      <button class="btn-primary">主要按钮</button>
      <button class="btn-secondary">次要按钮</button>
      <input class="input-base" placeholder="测试输入框" />
      <div class="text-primary">主要文本</div>
      <div class="text-secondary">次要文本</div>
    </div>
  `
})

describe('UnoCSS Configuration', () => {
  it('should apply page-container styles correctly', () => {
    const wrapper = mount(TestComponent)
    const container = wrapper.find('.page-container')
    
    expect(container.exists()).toBe(true)
    expect(container.classes()).toContain('page-container')
  })

  it('should apply button styles correctly', () => {
    const wrapper = mount(TestComponent)
    
    const primaryBtn = wrapper.find('.btn-primary')
    const secondaryBtn = wrapper.find('.btn-secondary')
    
    expect(primaryBtn.exists()).toBe(true)
    expect(secondaryBtn.exists()).toBe(true)
    expect(primaryBtn.classes()).toContain('btn-primary')
    expect(secondaryBtn.classes()).toContain('btn-secondary')
  })

  it('should apply input styles correctly', () => {
    const wrapper = mount(TestComponent)
    const input = wrapper.find('.input-base')
    
    expect(input.exists()).toBe(true)
    expect(input.classes()).toContain('input-base')
    expect(input.attributes('placeholder')).toBe('测试输入框')
  })

  it('should apply text color classes correctly', () => {
    const wrapper = mount(TestComponent)
    
    const primaryText = wrapper.find('.text-primary')
    const secondaryText = wrapper.find('.text-secondary')
    
    expect(primaryText.exists()).toBe(true)
    expect(secondaryText.exists()).toBe(true)
    expect(primaryText.text()).toBe('主要文本')
    expect(secondaryText.text()).toBe('次要文本')
  })

  it('should render component without errors', () => {
    expect(() => {
      mount(TestComponent)
    }).not.toThrow()
  })
})
