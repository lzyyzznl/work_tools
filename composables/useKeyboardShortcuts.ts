import { onMounted, onUnmounted, ref } from 'vue'

export interface ShortcutConfig {
  key: string
  ctrl?: boolean
  alt?: boolean
  shift?: boolean
  meta?: boolean
  description: string
  action: () => void | Promise<void>
}

export function useKeyboardShortcuts() {
  const shortcuts = ref<Map<string, ShortcutConfig>>(new Map())
  const isEnabled = ref(true)

  // 生成快捷键的唯一标识符
  function generateShortcutId(config: ShortcutConfig): string {
    const modifiers = []
    if (config.ctrl) modifiers.push('ctrl')
    if (config.alt) modifiers.push('alt')
    if (config.shift) modifiers.push('shift')
    if (config.meta) modifiers.push('meta')
    
    return `${modifiers.join('+')}${modifiers.length > 0 ? '+' : ''}${config.key.toLowerCase()}`
  }

  // 检查按键事件是否匹配快捷键配置
  function matchesShortcut(event: KeyboardEvent, config: ShortcutConfig): boolean {
    const keyMatches = event.key.toLowerCase() === config.key.toLowerCase()
    const ctrlMatches = !!event.ctrlKey === !!config.ctrl
    const altMatches = !!event.altKey === !!config.alt
    const shiftMatches = !!event.shiftKey === !!config.shift
    const metaMatches = !!event.metaKey === !!config.meta

    return keyMatches && ctrlMatches && altMatches && shiftMatches && metaMatches
  }

  // 处理键盘事件
  async function handleKeyDown(event: KeyboardEvent) {
    if (!isEnabled.value) return

    // 如果焦点在输入框中，跳过某些快捷键
    const activeElement = document.activeElement
    const isInputFocused = activeElement && (
      activeElement.tagName === 'INPUT' ||
      activeElement.tagName === 'TEXTAREA' ||
      activeElement.contentEditable === 'true'
    )

    for (const [id, config] of shortcuts.value) {
      if (matchesShortcut(event, config)) {
        // 对于某些快捷键，即使在输入框中也要执行
        const allowInInput = ['escape', 'f1', 'f2', 'f3', 'f4', 'f5'].includes(config.key.toLowerCase())
        
        if (isInputFocused && !allowInInput) {
          continue
        }

        event.preventDefault()
        event.stopPropagation()

        try {
          await config.action()
        } catch (error) {
          console.error(`快捷键 ${id} 执行失败:`, error)
        }
        break
      }
    }
  }

  // 注册快捷键
  function registerShortcut(config: ShortcutConfig): string {
    const id = generateShortcutId(config)
    shortcuts.value.set(id, config)
    return id
  }

  // 注销快捷键
  function unregisterShortcut(id: string) {
    shortcuts.value.delete(id)
  }

  // 清空所有快捷键
  function clearShortcuts() {
    shortcuts.value.clear()
  }

  // 启用/禁用快捷键系统
  function setEnabled(enabled: boolean) {
    isEnabled.value = enabled
  }

  // 获取所有已注册的快捷键
  function getShortcuts(): ShortcutConfig[] {
    return Array.from(shortcuts.value.values())
  }

  // 获取快捷键的显示文本
  function getShortcutDisplayText(config: ShortcutConfig): string {
    const modifiers = []
    if (config.ctrl) modifiers.push('Ctrl')
    if (config.alt) modifiers.push('Alt')
    if (config.shift) modifiers.push('Shift')
    if (config.meta) modifiers.push('Cmd')
    
    const key = config.key.length === 1 ? config.key.toUpperCase() : config.key
    return [...modifiers, key].join(' + ')
  }

  // 预定义的常用快捷键配置
  const commonShortcuts = {
    // 文件操作
    selectFiles: (action: () => void) => ({
      key: 'o',
      ctrl: true,
      description: '选择文件',
      action
    }),
    
    clearFiles: (action: () => void) => ({
      key: 'Delete',
      shift: true,
      description: '清空文件',
      action
    }),

    // 重命名操作
    executeRename: (action: () => void) => ({
      key: 'Enter',
      ctrl: true,
      description: '执行重命名',
      action
    }),

    undoRename: (action: () => void) => ({
      key: 'z',
      ctrl: true,
      description: '撤回重命名',
      action
    }),

    preview: (action: () => void) => ({
      key: 'p',
      ctrl: true,
      description: '预览重命名',
      action
    }),

    // 模式切换
    switchToReplace: (action: () => void) => ({
      key: '1',
      ctrl: true,
      description: '切换到字符串替换',
      action
    }),

    switchToAdd: (action: () => void) => ({
      key: '2',
      ctrl: true,
      description: '切换到添加前缀/后缀',
      action
    }),

    switchToNumber: (action: () => void) => ({
      key: '3',
      ctrl: true,
      description: '切换到批量序号',
      action
    }),

    switchToDelete: (action: () => void) => ({
      key: '4',
      ctrl: true,
      description: '切换到删除字符',
      action
    }),

    // 界面操作
    toggleAutoPreview: (action: () => void) => ({
      key: 'a',
      ctrl: true,
      alt: true,
      description: '切换自动预览',
      action
    }),

    openSettings: (action: () => void) => ({
      key: ',',
      ctrl: true,
      description: '打开设置',
      action
    }),

    openHelp: (action: () => void) => ({
      key: 'F1',
      description: '打开帮助',
      action
    }),

    // 选择操作
    selectAll: (action: () => void) => ({
      key: 'a',
      ctrl: true,
      description: '全选文件',
      action
    }),

    deselectAll: (action: () => void) => ({
      key: 'd',
      ctrl: true,
      description: '取消全选',
      action
    }),

    // 其他
    escape: (action: () => void) => ({
      key: 'Escape',
      description: '取消/关闭',
      action
    })
  }

  // 组件挂载时添加事件监听
  onMounted(() => {
    document.addEventListener('keydown', handleKeyDown)
  })

  // 组件卸载时移除事件监听
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeyDown)
    clearShortcuts()
  })

  return {
    shortcuts,
    isEnabled,
    registerShortcut,
    unregisterShortcut,
    clearShortcuts,
    setEnabled,
    getShortcuts,
    getShortcutDisplayText,
    commonShortcuts
  }
}
