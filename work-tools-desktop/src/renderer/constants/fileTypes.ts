// 文件类型相关常量

export const SUPPORTED_FILE_TYPES = {
  // 文档类型
  documents: {
    extensions: ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
    mimeTypes: [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'text/plain',
      'application/rtf'
    ],
    description: '文档文件'
  },
  
  // 表格类型
  spreadsheets: {
    extensions: ['.xlsx', '.xls', '.csv'],
    mimeTypes: [
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel',
      'text/csv'
    ],
    description: '表格文件'
  },
  
  // 图片类型
  images: {
    extensions: ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg'],
    mimeTypes: [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/bmp',
      'image/svg+xml'
    ],
    description: '图片文件'
  },
  
  // 压缩文件
  archives: {
    extensions: ['.zip', '.rar', '.7z', '.tar', '.gz'],
    mimeTypes: [
      'application/zip',
      'application/x-rar-compressed',
      'application/x-7z-compressed',
      'application/x-tar',
      'application/gzip'
    ],
    description: '压缩文件'
  }
} as const;

export const FILE_ICONS = {
  // 文档图标
  '.pdf': '📄',
  '.doc': '📝',
  '.docx': '📝',
  '.txt': '📄',
  '.rtf': '📄',
  
  // 表格图标
  '.xlsx': '📊',
  '.xls': '📊',
  '.csv': '📊',
  
  // 图片图标
  '.jpg': '🖼️',
  '.jpeg': '🖼️',
  '.png': '🖼️',
  '.gif': '🖼️',
  '.bmp': '🖼️',
  '.svg': '🖼️',
  
  // 压缩文件图标
  '.zip': '📦',
  '.rar': '📦',
  '.7z': '📦',
  '.tar': '📦',
  '.gz': '📦',
  
  // 默认图标
  default: '📄'
} as const;

export const FILE_SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'] as const;

export const RENAME_PATTERNS = {
  DATE_FORMAT: 'YYYY-MM-DD',
  TIME_FORMAT: 'HH:mm:ss',
  DATETIME_FORMAT: 'YYYY-MM-DD_HH-mm-ss',
  NUMBER_FORMAT: '000',
} as const;
