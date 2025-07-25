// 文件相关类型定义

export interface FileItem {
  id: string;
  name: string;
  path: string;
  size: number;
  lastModified: number;
  file: File;
  matched?: boolean;
  matchInfo?: MatchInfo;
  previewName?: string;
  selected: boolean;
  executionResult?: string;
}

export interface MatchInfo {
  index: number;
  code: string;
  thirtyD: string;
  matchedRule: string;
}

export interface FileStats {
  total: number;
  matched: number;
  unmatched: number;
  selected: number;
}

// Electron 环境下的文件处理相关类型
export interface ElectronFileHandle {
  path: string;
  name: string;
  size: number;
  lastModified: number;
  type: string;
}

export interface FileOperationResult {
  success: boolean;
  message?: string;
  error?: string;
}

export interface DirectoryInfo {
  path: string;
  name: string;
  isDirectory: boolean;
  children?: DirectoryInfo[];
}
