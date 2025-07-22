import type { FileItem } from '../types/file'
import type { RenameHistory } from '../types/rename'
import type { ExportData } from './exportUtils'

export interface ImportResult {
  success: boolean
  data?: ExportData
  errors: string[]
  warnings: string[]
  stats: {
    fileCount: number
    historyCount: number
    hasSettings: boolean
    version: string
    importDate: string
  }
}

export interface ImportOptions {
  replaceExisting: boolean
  mergeHistory: boolean
  importSettings: boolean
  validateFiles: boolean
}

// 从文件读取内容
export function readFileContent(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = (e) => {
      const content = e.target?.result as string
      resolve(content)
    }
    
    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }
    
    reader.readAsText(file, 'utf-8')
  })
}

// 解析JSON数据
export function parseImportData(content: string): { data: any; errors: string[] } {
  const errors: string[] = []
  let data: any = null
  
  try {
    data = JSON.parse(content)
  } catch (error) {
    errors.push('JSON格式无效')
    return { data: null, errors }
  }
  
  return { data, errors }
}

// 验证导入数据
export function validateImportData(data: any): { isValid: boolean; errors: string[]; warnings: string[] } {
  const errors: string[] = []
  const warnings: string[] = []
  
  // 基本结构验证
  if (!data || typeof data !== 'object') {
    errors.push('数据格式无效')
    return { isValid: false, errors, warnings }
  }
  
  // 版本检查
  if (!data.version) {
    warnings.push('缺少版本信息，可能是旧版本的导出文件')
  } else if (data.version !== '1.0.0') {
    warnings.push(`版本不匹配，当前支持版本: 1.0.0，文件版本: ${data.version}`)
  }
  
  // 时间戳验证
  if (!data.timestamp || typeof data.timestamp !== 'number') {
    warnings.push('缺少或无效的时间戳')
  }
  
  // 文件列表验证
  if (data.files) {
    if (!Array.isArray(data.files)) {
      errors.push('文件列表格式无效')
    } else {
      // 验证文件项
      data.files.forEach((file: any, index: number) => {
        if (!file.id || !file.name || !file.path) {
          warnings.push(`文件项 ${index + 1} 缺少必要字段`)
        }
      })
    }
  }
  
  // 历史记录验证
  if (data.renameHistory) {
    if (!Array.isArray(data.renameHistory)) {
      errors.push('重命名历史格式无效')
    } else {
      data.renameHistory.forEach((history: any, index: number) => {
        if (!history.id || !history.timestamp || !history.operations) {
          warnings.push(`历史记录 ${index + 1} 格式不完整`)
        }
      })
    }
  }
  
  // 设置验证
  if (data.settings && typeof data.settings !== 'object') {
    warnings.push('设置数据格式可能无效')
  }
  
  // 元数据验证
  if (!data.metadata) {
    warnings.push('缺少元数据信息')
  }
  
  return {
    isValid: errors.length === 0,
    errors,
    warnings
  }
}

// 转换导入的文件数据
export function convertImportedFiles(importedFiles: any[]): FileItem[] {
  return importedFiles.map((file: any) => ({
    id: file.id || `imported_${Date.now()}_${Math.random()}`,
    name: file.name || 'unknown',
    path: file.path || '',
    size: file.size || 0,
    lastModified: file.lastModified || Date.now(),
    type: file.type || 'file',
    selected: false, // 导入的文件默认不选中
    previewName: file.previewName || undefined,
    matchResult: undefined,
    executionResult: undefined
  }))
}

// 转换导入的历史记录
export function convertImportedHistory(importedHistory: any[]): RenameHistory[] {
  return importedHistory.map((history: any) => ({
    id: history.id || `imported_history_${Date.now()}_${Math.random()}`,
    timestamp: history.timestamp || Date.now(),
    operations: history.operations || []
  }))
}

// 主导入函数
export async function importData(
  file: File,
  options: ImportOptions
): Promise<ImportResult> {
  const result: ImportResult = {
    success: false,
    errors: [],
    warnings: [],
    stats: {
      fileCount: 0,
      historyCount: 0,
      hasSettings: false,
      version: 'unknown',
      importDate: new Date().toLocaleString()
    }
  }
  
  try {
    // 读取文件内容
    const content = await readFileContent(file)
    
    // 解析JSON
    const { data, errors: parseErrors } = parseImportData(content)
    if (parseErrors.length > 0) {
      result.errors.push(...parseErrors)
      return result
    }
    
    // 验证数据
    const { isValid, errors: validationErrors, warnings } = validateImportData(data)
    result.warnings.push(...warnings)
    
    if (!isValid) {
      result.errors.push(...validationErrors)
      return result
    }
    
    // 转换数据
    const convertedData: ExportData = {
      version: data.version || '1.0.0',
      timestamp: data.timestamp || Date.now(),
      files: data.files ? convertImportedFiles(data.files) : [],
      renameHistory: data.renameHistory ? convertImportedHistory(data.renameHistory) : [],
      settings: options.importSettings ? data.settings : undefined,
      metadata: data.metadata || {
        totalFiles: data.files?.length || 0,
        exportedBy: 'Unknown',
        description: '导入的数据'
      }
    }
    
    // 更新统计信息
    result.stats = {
      fileCount: convertedData.files.length,
      historyCount: convertedData.renameHistory.length,
      hasSettings: !!convertedData.settings,
      version: convertedData.version,
      importDate: new Date().toLocaleString()
    }
    
    result.data = convertedData
    result.success = true
    
  } catch (error) {
    result.errors.push(`导入失败: ${error}`)
  }
  
  return result
}

// 选择导入文件
export function selectImportFile(): Promise<File | null> {
  return new Promise((resolve) => {
    const input = document.createElement('input')
    input.type = 'file'
    input.accept = '.json'
    
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      resolve(file || null)
    }
    
    input.oncancel = () => {
      resolve(null)
    }
    
    input.click()
  })
}

// 预览导入数据
export function previewImportData(data: ExportData): {
  summary: string
  filePreview: string[]
  historyPreview: string[]
  settingsPreview: string[]
} {
  const summary = `
版本: ${data.version}
导出时间: ${new Date(data.timestamp).toLocaleString()}
文件数量: ${data.files.length}
历史记录: ${data.renameHistory.length}
包含设置: ${data.settings ? '是' : '否'}
  `.trim()
  
  const filePreview = data.files.slice(0, 5).map(file => 
    `${file.name} (${file.path})`
  )
  
  const historyPreview = data.renameHistory.slice(0, 3).map(history => 
    `${new Date(history.timestamp).toLocaleString()} - ${history.operations.length} 个操作`
  )
  
  const settingsPreview = data.settings ? 
    Object.keys(data.settings).slice(0, 5) : []
  
  return {
    summary,
    filePreview,
    historyPreview,
    settingsPreview
  }
}
