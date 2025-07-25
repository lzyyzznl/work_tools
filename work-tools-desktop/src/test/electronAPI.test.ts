import { describe, it, expect, beforeEach } from 'vitest'
import { mockElectronAPI } from './setup'

describe('Electron API Bridge', () => {
  beforeEach(() => {
    // 重置所有 mock
    Object.values(mockElectronAPI.fileSystem).forEach(mock => mock.mockReset())
  })

  describe('fileSystem API', () => {
    it('should have selectFiles method', () => {
      expect(window.electronAPI.fileSystem.selectFiles).toBeDefined()
      expect(typeof window.electronAPI.fileSystem.selectFiles).toBe('function')
    })

    it('should have selectDirectory method', () => {
      expect(window.electronAPI.fileSystem.selectDirectory).toBeDefined()
      expect(typeof window.electronAPI.fileSystem.selectDirectory).toBe('function')
    })

    it('should have readFile method', () => {
      expect(window.electronAPI.fileSystem.readFile).toBeDefined()
      expect(typeof window.electronAPI.fileSystem.readFile).toBe('function')
    })

    it('should have writeFile method', () => {
      expect(window.electronAPI.fileSystem.writeFile).toBeDefined()
      expect(typeof window.electronAPI.fileSystem.writeFile).toBe('function')
    })

    it('should call selectFiles with correct options', async () => {
      const mockFiles = [
        new File(['content'], 'test.txt', { type: 'text/plain' })
      ]
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue(mockFiles)

      const options = { multiple: true, accept: { 'text/*': ['.txt'] } }
      const result = await window.electronAPI.fileSystem.selectFiles(options)

      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalledWith(options)
      expect(result).toEqual(mockFiles)
    })

    it('should handle selectFiles errors', async () => {
      const error = new Error('User cancelled')
      mockElectronAPI.fileSystem.selectFiles.mockRejectedValue(error)

      await expect(
        window.electronAPI.fileSystem.selectFiles({ multiple: true })
      ).rejects.toThrow('User cancelled')
    })

    it('should call selectDirectory and return files', async () => {
      const mockFiles = [
        new File(['content1'], 'file1.txt'),
        new File(['content2'], 'file2.txt')
      ]
      mockElectronAPI.fileSystem.selectDirectory.mockResolvedValue(mockFiles)

      const result = await window.electronAPI.fileSystem.selectDirectory()

      expect(mockElectronAPI.fileSystem.selectDirectory).toHaveBeenCalled()
      expect(result).toEqual(mockFiles)
    })
  })
})
