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
