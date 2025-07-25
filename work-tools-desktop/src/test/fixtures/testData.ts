// 测试数据文件，用于各种测试场景

export const mockFiles = [
  {
    id: 'file-1',
    name: 'document.pdf',
    path: '/test/documents/document.pdf',
    size: 1024000,
    lastModified: Date.now() - 86400000, // 1天前
    type: 'application/pdf',
    matched: true,
    matchedRules: ['pdf-rule'],
  },
  {
    id: 'file-2', 
    name: 'image.jpg',
    path: '/test/images/image.jpg',
    size: 2048000,
    lastModified: Date.now() - 3600000, // 1小时前
    type: 'image/jpeg',
    matched: false,
    matchedRules: [],
  },
  {
    id: 'file-3',
    name: 'spreadsheet.xlsx',
    path: '/test/data/spreadsheet.xlsx', 
    size: 512000,
    lastModified: Date.now() - 7200000, // 2小时前
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    matched: true,
    matchedRules: ['excel-rule'],
  }
]

export const mockRules = [
  {
    id: 'default-1',
    code: '01.33.06.01',
    thirtyD: 'N',
    matchRules: ['PDF', 'pdf'],
    source: 'default' as const,
  },
  {
    id: 'default-2',
    code: '01.33.06.02',
    thirtyD: 'Y',
    matchRules: ['Excel', 'xlsx'],
    source: 'default' as const,
  },
  {
    id: 'user-1',
    code: '02.01.01',
    thirtyD: 'N',
    matchRules: ['image', 'jpg', 'png'],
    source: 'user' as const,
  }
]

export const mockSettings = {
  theme: 'light' as const,
  language: 'zh-CN' as const,
  autoSave: true,
  showHiddenFiles: false,
  defaultExportFormat: 'xlsx' as const,
  maxFileSize: 100 * 1024 * 1024, // 100MB
}

export const mockRenameOperations = [
  {
    id: 'op-1',
    type: 'prefix' as const,
    value: 'NEW_',
    enabled: true,
  },
  {
    id: 'op-2', 
    type: 'suffix' as const,
    value: '_backup',
    enabled: true,
  },
  {
    id: 'op-3',
    type: 'replace' as const,
    find: 'old',
    replace: 'new',
    enabled: false,
  }
]

// 创建测试用的 File 对象
export function createMockFile(name: string, content: string = 'test content', type: string = 'text/plain'): File {
  const blob = new Blob([content], { type })
  return new File([blob], name, { 
    type,
    lastModified: Date.now()
  })
}

// 创建多个测试文件
export function createMockFiles(count: number = 3): File[] {
  return Array.from({ length: count }, (_, i) => 
    createMockFile(`test-file-${i + 1}.txt`, `Content of file ${i + 1}`)
  )
}
