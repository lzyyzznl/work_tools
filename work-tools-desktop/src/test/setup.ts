import { vi } from 'vitest'
import 'uno.css'

// Mock Electron APIs
const mockElectronAPI = {
  fileSystem: {
    selectFiles: vi.fn(),
    selectDirectory: vi.fn(),
    readFile: vi.fn(),
    writeFile: vi.fn(),
  },
}

// 模拟 window.electronAPI
Object.defineProperty(window, 'electronAPI', {
  value: mockElectronAPI,
  writable: true,
})

// 导出 mock 对象供测试使用
export { mockElectronAPI }
