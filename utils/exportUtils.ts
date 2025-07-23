import type { FileItem } from '../types/file'
import type { RenameHistory } from '../types/rename'

export interface ExportData {
  version: string
  timestamp: number
  files: FileItem[]
  renameHistory: RenameHistory[]
  settings?: any
  metadata: {
    totalFiles: number
    exportedBy: string
    description?: string
  }
}

export interface ExportOptions {
  includeFiles: boolean
  includeHistory: boolean
  includeSettings: boolean
  format: 'json' | 'csv'
  description?: string
}

// 导出为JSON格式
export function exportToJSON(data: ExportData): string {
  return JSON.stringify(data, null, 2)
}

// 导出为CSV格式
export function exportToCSV(files: FileItem[]): string {
  const headers = ['原文件名', '新文件名', '文件路径', '文件大小', '修改时间', '状态']
  const rows = [headers.join(',')]
  
  files.forEach(file => {
    const row = [
      `"${file.name}"`,
      `"${file.previewName || file.name}"`,
      `"${file.path}"`,
      file.size?.toString() || '0',
      file.lastModified?.toString() || '',
      file.selected ? '已选中' : '未选中'
    ]
    rows.push(row.join(','))
  })
  
  return rows.join('\n')
}

// 创建并下载文件
export function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  
  URL.revokeObjectURL(url)
}

// 生成导出文件名
export function generateExportFilename(format: 'json' | 'csv', description?: string): string {
  const timestamp = new Date().toISOString().split('T')[0]
  const desc = description ? `-${description.replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '_')}` : ''
  return `work-tools-export${desc}-${timestamp}.${format}`
}

// 主导出函数
export function exportData(
  files: FileItem[],
  history: RenameHistory[],
  settings: any,
  options: ExportOptions
): void {
  try {
    if (options.format === 'csv') {
      // CSV格式只导出文件列表
      const csvContent = exportToCSV(files)
      const filename = generateExportFilename('csv', options.description)
      downloadFile(csvContent, filename, 'text/csv;charset=utf-8')
    } else {
      // JSON格式导出完整数据
      const exportData: ExportData = {
        version: '1.0.0',
        timestamp: Date.now(),
        files: options.includeFiles ? files : [],
        renameHistory: options.includeHistory ? history : [],
        settings: options.includeSettings ? settings : undefined,
        metadata: {
          totalFiles: files.length,
          exportedBy: 'Work Tools Plugin',
          description: options.description
        }
      }
      
      const jsonContent = exportToJSON(exportData)
      const filename = generateExportFilename('json', options.description)
      downloadFile(jsonContent, filename, 'application/json;charset=utf-8')
    }
  } catch (error) {
    console.error('导出失败:', error)
    throw new Error(`导出失败: ${error}`)
  }
}

// 验证导出数据
export function validateExportData(data: any): { isValid: boolean; errors: string[] } {
  const errors: string[] = []
  
  if (!data || typeof data !== 'object') {
    errors.push('无效的数据格式')
    return { isValid: false, errors }
  }
  
  if (!data.version) {
    errors.push('缺少版本信息')
  }
  
  if (!data.timestamp || typeof data.timestamp !== 'number') {
    errors.push('缺少或无效的时间戳')
  }
  
  if (data.files && !Array.isArray(data.files)) {
    errors.push('文件列表格式无效')
  }
  
  if (data.renameHistory && !Array.isArray(data.renameHistory)) {
    errors.push('重命名历史格式无效')
  }
  
  if (!data.metadata || typeof data.metadata !== 'object') {
    errors.push('缺少元数据信息')
  }
  
  return {
    isValid: errors.length === 0,
    errors
  }
}

// 获取导出统计信息
export function getExportStats(data: ExportData): {
  fileCount: number
  historyCount: number
  hasSettings: boolean
  exportSize: string
  exportDate: string
} {
  const jsonString = exportToJSON(data)
  const sizeInBytes = new Blob([jsonString]).size
  const sizeInKB = (sizeInBytes / 1024).toFixed(2)
  
  return {
    fileCount: data.files.length,
    historyCount: data.renameHistory.length,
    hasSettings: !!data.settings,
    exportSize: `${sizeInKB} KB`,
    exportDate: new Date(data.timestamp).toLocaleString()
  }
}
