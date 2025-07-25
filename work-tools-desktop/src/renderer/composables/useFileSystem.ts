import { ref } from 'vue'

export function useFileSystem() {
  const isSupported = ref(true) // Electron 环境总是支持文件系统操作
  const isLoading = ref(false)

  // 在 Electron 环境中，我们总是使用 electronAPI
  function checkSupport() {
    return window.electronAPI ? 'electron' : 'unsupported'
  }

  // 使用 Electron API 选择文件
  async function selectFiles(options: {
    multiple?: boolean
    accept?: Record<string, string[]>
  } = {}) {
    try {
      isLoading.value = true
      
      // 转换 accept 格式为 Electron 的 filters 格式
      let filters: Array<{ name: string; extensions: string[] }> = []
      
      if (options.accept) {
        filters = Object.entries(options.accept).map(([name, extensions]) => ({
          name,
          extensions: extensions.map(ext => ext.replace(/^\./, '')) // 移除前导点
        }))
      }

      const electronOptions = {
        multiple: options.multiple ?? true,
        filters: filters.length > 0 ? filters : undefined
      }

      const files = await window.electronAPI.fileSystem.selectFiles(electronOptions)
      return files
    } catch (error) {
      console.error('Error selecting files:', error)
      if ((error as Error).message.includes('cancelled') || (error as Error).message.includes('canceled')) {
        // 用户取消选择
        return []
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 使用 Electron API 选择目录
  async function selectDirectory() {
    try {
      isLoading.value = true
      
      const files = await window.electronAPI.fileSystem.selectDirectory()
      return files
    } catch (error) {
      console.error('Error selecting directory:', error)
      if ((error as Error).message.includes('cancelled') || (error as Error).message.includes('canceled')) {
        return []
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 读取文件内容
  async function readFile(path: string): Promise<ArrayBuffer> {
    try {
      isLoading.value = true
      return await window.electronAPI.fileSystem.readFile(path)
    } catch (error) {
      console.error('Error reading file:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 写入文件
  async function writeFile(path: string, data: ArrayBuffer) {
    try {
      isLoading.value = true
      const result = await window.electronAPI.fileSystem.writeFile(path, data)
      if (!result.success) {
        throw new Error(result.error || 'Failed to write file')
      }
      return result
    } catch (error) {
      console.error('Error writing file:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 处理拖拽文件 (在 Electron 中仍然可用)
  function handleDrop(event: DragEvent): File[] {
    event.preventDefault()
    const files: File[] = []
    
    if (event.dataTransfer?.items) {
      // 使用 DataTransferItemList 接口
      for (let i = 0; i < event.dataTransfer.items.length; i++) {
        const item = event.dataTransfer.items[i]
        if (item.kind === 'file') {
          const file = item.getAsFile()
          if (file) {
            files.push(file)
          }
        }
      }
    } else if (event.dataTransfer?.files) {
      // 回退到 FileList 接口
      files.push(...Array.from(event.dataTransfer.files))
    }
    
    return files
  }

  // 格式化文件大小
  function formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 B'
    
    const k = 1024
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  // 获取文件扩展名
  function getFileExtension(filename: string): string {
    const lastDot = filename.lastIndexOf('.')
    return lastDot > 0 ? filename.substring(lastDot + 1).toLowerCase() : ''
  }

  // 验证文件类型
  function validateFileType(file: File, allowedTypes: string[]): boolean {
    const extension = getFileExtension(file.name)
    return allowedTypes.includes(extension) || allowedTypes.includes('*')
  }

  // 获取文件路径 (Electron 特有)
  function getFilePath(file: File): string {
    // 在 Electron 环境中，File 对象可能有 path 属性
    return (file as any).path || file.webkitRelativePath || file.name
  }

  // 检查文件是否存在 (Electron 特有)
  async function fileExists(path: string): Promise<boolean> {
    try {
      await readFile(path)
      return true
    } catch {
      return false
    }
  }

  // 获取文件信息
  function getFileInfo(file: File) {
    return {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      extension: getFileExtension(file.name),
      formattedSize: formatFileSize(file.size),
      path: getFilePath(file)
    }
  }

  // 批量处理文件
  async function processFiles(
    files: File[], 
    processor: (file: File, index: number) => Promise<any>,
    onProgress?: (current: number, total: number) => void
  ) {
    const results = []
    
    for (let i = 0; i < files.length; i++) {
      try {
        const result = await processor(files[i], i)
        results.push({ success: true, result, file: files[i] })
      } catch (error) {
        results.push({ success: false, error, file: files[i] })
      }
      
      if (onProgress) {
        onProgress(i + 1, files.length)
      }
    }
    
    return results
  }

  return {
    isSupported,
    isLoading,
    checkSupport,
    selectFiles,
    selectDirectory,
    readFile,
    writeFile,
    handleDrop,
    formatFileSize,
    getFileExtension,
    validateFileType,
    getFilePath,
    fileExists,
    getFileInfo,
    processFiles
  }
}
