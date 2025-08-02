import { ref } from 'vue'

export function useFileSystem() {
  const isSupported = ref(false)
  const isLoading = ref(false)

  // 检查浏览器支持
  function checkSupport() {
    // 检查 File System Access API 支持
    if ('showOpenFilePicker' in window) {
      isSupported.value = true
      return 'modern'
    }
    // 回退到传统文件输入
    return 'legacy'
  }

  // 现代文件选择 (File System Access API)
  async function selectFilesModern(options: {
    multiple?: boolean
    accept?: Record<string, string[]>
  } = {}) {
    try {
      isLoading.value = true
      
      const pickerOptions: any = {
        multiple: options.multiple ?? true,
        excludeAcceptAllOption: false
      }

      if (options.accept) {
        pickerOptions.types = Object.entries(options.accept).map(([description, extensions]) => ({
          description,
          accept: { '*/*': extensions }
        }))
      }

      const fileHandles = await (window as any).showOpenFilePicker(pickerOptions)
      const files: File[] = []

      for (const fileHandle of fileHandles) {
        const file = await fileHandle.getFile()
        files.push(file)
      }

      return files
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        // 用户取消选择
        return []
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 传统文件选择 (input[type="file"])
  function selectFilesLegacy(options: {
    multiple?: boolean
    accept?: string
  } = {}): Promise<File[]> {
    return new Promise((resolve) => {
      isLoading.value = true
      
      const input = document.createElement('input')
      input.type = 'file'
      input.multiple = options.multiple ?? true
      
      if (options.accept) {
        input.accept = options.accept
      }

      input.onchange = () => {
        const files = Array.from(input.files || [])
        isLoading.value = false
        resolve(files)
      }

      input.oncancel = () => {
        isLoading.value = false
        resolve([])
      }

      input.click()
    })
  }

  // 统一的文件选择接口
  async function selectFiles(options: {
    multiple?: boolean
    accept?: Record<string, string[]> | string
  } = {}) {
    const supportType = checkSupport()
    
    if (supportType === 'modern' && typeof options.accept === 'object') {
      return await selectFilesModern(options as any)
    } else {
      // 转换 accept 格式
      let acceptString = ''
      if (typeof options.accept === 'object') {
        acceptString = Object.values(options.accept).flat().join(',')
      } else if (typeof options.accept === 'string') {
        acceptString = options.accept
      }
      
      return await selectFilesLegacy({
        multiple: options.multiple,
        accept: acceptString
      })
    }
  }

  // 选择文件夹 (仅现代浏览器支持)
  async function selectDirectory() {
    try {
      isLoading.value = true
      
      if (!('showDirectoryPicker' in window)) {
        throw new Error('Directory picker not supported')
      }

      const dirHandle = await (window as any).showDirectoryPicker()
      const files: File[] = []

      async function processDirectory(dirHandle: any, path = '') {
        for await (const [name, handle] of dirHandle.entries()) {
          if (handle.kind === 'file') {
            const file = await handle.getFile()
            // 添加相对路径信息
            Object.defineProperty(file, 'webkitRelativePath', {
              value: path ? `${path}/${name}` : name,
              writable: false
            })
            files.push(file)
          } else if (handle.kind === 'directory') {
            await processDirectory(handle, path ? `${path}/${name}` : name)
          }
        }
      }

      await processDirectory(dirHandle)
      return files
    } catch (error) {
      if ((error as Error).name === 'AbortError') {
        return []
      }
      throw error
    } finally {
      isLoading.value = false
    }
  }

  // 处理拖拽文件
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

  return {
    isSupported,
    isLoading,
    checkSupport,
    selectFiles,
    selectDirectory,
    handleDrop,
    formatFileSize,
    getFileExtension,
    validateFileType
  }
}
