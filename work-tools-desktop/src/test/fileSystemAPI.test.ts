import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mockElectronAPI } from './setup'
import { createMockFile, createMockFiles } from './fixtures/testData'

describe('File System API Integration', () => {
  beforeEach(() => {
    // 重置所有 mock
    Object.values(mockElectronAPI.fileSystem).forEach(mock => mock.mockReset())
  })

  describe('selectFiles', () => {
    it('should select single file', async () => {
      const mockFile = createMockFile('test.txt', 'test content')
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue([mockFile])

      const result = await window.electronAPI.fileSystem.selectFiles({ multiple: false })

      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalledWith({ multiple: false })
      expect(result).toHaveLength(1)
      expect(result[0].name).toBe('test.txt')
    })

    it('should select multiple files', async () => {
      const mockFiles = createMockFiles(3)
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue(mockFiles)

      const result = await window.electronAPI.fileSystem.selectFiles({ multiple: true })

      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalledWith({ multiple: true })
      expect(result).toHaveLength(3)
      result.forEach((file, index) => {
        expect(file.name).toBe(`test-file-${index + 1}.txt`)
      })
    })

    it('should handle file selection with filters', async () => {
      const mockFile = createMockFile('document.pdf', 'pdf content', 'application/pdf')
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue([mockFile])

      const options = {
        multiple: false,
        filters: [
          { name: 'PDF Files', extensions: ['pdf'] }
        ]
      }

      const result = await window.electronAPI.fileSystem.selectFiles(options)

      expect(mockElectronAPI.fileSystem.selectFiles).toHaveBeenCalledWith(options)
      expect(result).toHaveLength(1)
      expect(result[0].name).toBe('document.pdf')
      expect(result[0].type).toBe('application/pdf')
    })

    it('should handle empty selection', async () => {
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue([])

      const result = await window.electronAPI.fileSystem.selectFiles()

      expect(result).toHaveLength(0)
    })

    it('should handle selection errors', async () => {
      const error = new Error('File selection failed')
      mockElectronAPI.fileSystem.selectFiles.mockRejectedValue(error)

      await expect(
        window.electronAPI.fileSystem.selectFiles()
      ).rejects.toThrow('File selection failed')
    })
  })

  describe('selectDirectory', () => {
    it('should select directory and return files', async () => {
      const mockFiles = [
        createMockFile('file1.txt', 'content1'),
        createMockFile('file2.txt', 'content2'),
        createMockFile('file3.pdf', 'pdf content', 'application/pdf')
      ]
      mockElectronAPI.fileSystem.selectDirectory.mockResolvedValue(mockFiles)

      const result = await window.electronAPI.fileSystem.selectDirectory()

      expect(mockElectronAPI.fileSystem.selectDirectory).toHaveBeenCalled()
      expect(result).toHaveLength(3)
      expect(result[0].name).toBe('file1.txt')
      expect(result[1].name).toBe('file2.txt')
      expect(result[2].name).toBe('file3.pdf')
      expect(result[2].type).toBe('application/pdf')
    })

    it('should handle empty directory', async () => {
      mockElectronAPI.fileSystem.selectDirectory.mockResolvedValue([])

      const result = await window.electronAPI.fileSystem.selectDirectory()

      expect(result).toHaveLength(0)
    })

    it('should handle directory selection errors', async () => {
      const error = new Error('Directory access denied')
      mockElectronAPI.fileSystem.selectDirectory.mockRejectedValue(error)

      await expect(
        window.electronAPI.fileSystem.selectDirectory()
      ).rejects.toThrow('Directory access denied')
    })
  })

  describe('readFile', () => {
    it('should read file content', async () => {
      const mockContent = new ArrayBuffer(10)
      const view = new Uint8Array(mockContent)
      view.set([72, 101, 108, 108, 111]) // "Hello"
      
      mockElectronAPI.fileSystem.readFile.mockResolvedValue(mockContent)

      const result = await window.electronAPI.fileSystem.readFile('/path/to/file.txt')

      expect(mockElectronAPI.fileSystem.readFile).toHaveBeenCalledWith('/path/to/file.txt')
      expect(result).toBeInstanceOf(ArrayBuffer)
      expect(result.byteLength).toBe(10)
    })

    it('should handle file read errors', async () => {
      const error = new Error('File not found')
      mockElectronAPI.fileSystem.readFile.mockRejectedValue(error)

      await expect(
        window.electronAPI.fileSystem.readFile('/nonexistent/file.txt')
      ).rejects.toThrow('File not found')
    })
  })

  describe('writeFile', () => {
    it('should write file successfully', async () => {
      const mockResult = { success: true, message: 'File written successfully' }
      mockElectronAPI.fileSystem.writeFile.mockResolvedValue(mockResult)

      const data = new ArrayBuffer(5)
      const view = new Uint8Array(data)
      view.set([72, 101, 108, 108, 111]) // "Hello"

      const result = await window.electronAPI.fileSystem.writeFile('/path/to/output.txt', data)

      expect(mockElectronAPI.fileSystem.writeFile).toHaveBeenCalledWith('/path/to/output.txt', data)
      expect(result.success).toBe(true)
      expect(result.message).toBe('File written successfully')
    })

    it('should handle file write errors', async () => {
      const mockResult = { success: false, error: 'Permission denied' }
      mockElectronAPI.fileSystem.writeFile.mockResolvedValue(mockResult)

      const data = new ArrayBuffer(5)
      const result = await window.electronAPI.fileSystem.writeFile('/readonly/file.txt', data)

      expect(result.success).toBe(false)
      expect(result.error).toBe('Permission denied')
    })

    it('should handle write operation exceptions', async () => {
      const error = new Error('Disk full')
      mockElectronAPI.fileSystem.writeFile.mockRejectedValue(error)

      const data = new ArrayBuffer(5)

      await expect(
        window.electronAPI.fileSystem.writeFile('/path/to/file.txt', data)
      ).rejects.toThrow('Disk full')
    })
  })

  describe('File object properties', () => {
    it('should create proper File objects with correct properties', async () => {
      const mockFile = createMockFile('test.txt', 'test content', 'text/plain')
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue([mockFile])

      const result = await window.electronAPI.fileSystem.selectFiles()
      const file = result[0]

      expect(file).toBeInstanceOf(File)
      expect(file.name).toBe('test.txt')
      expect(file.type).toBe('text/plain')
      expect(file.size).toBeGreaterThan(0)
      expect(typeof file.lastModified).toBe('number')
    })

    it('should handle different file types correctly', async () => {
      const mockFiles = [
        createMockFile('document.pdf', 'pdf content', 'application/pdf'),
        createMockFile('image.jpg', 'image data', 'image/jpeg'),
        createMockFile('data.xlsx', 'excel data', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
      ]
      mockElectronAPI.fileSystem.selectFiles.mockResolvedValue(mockFiles)

      const result = await window.electronAPI.fileSystem.selectFiles({ multiple: true })

      expect(result[0].type).toBe('application/pdf')
      expect(result[1].type).toBe('image/jpeg')
      expect(result[2].type).toBe('application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    })
  })
})
