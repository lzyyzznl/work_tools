// 重命名相关类型定义

export type RenameOperationType = 'replace' | 'add' | 'number' | 'delete';

export interface ReplaceParams {
  fromStr: string;
  toStr: string;
}

export interface AddParams {
  text: string;
  isPrefix: boolean;
}

export interface NumberParams {
  start: number;
  digits: number;
  step: number;
  separator: string;
  isPrefix: boolean;
}

export interface DeleteParams {
  startPos: number;
  count: number;
  fromLeft: boolean;
}

export interface RenameOperation {
  type: RenameOperationType;
  params: ReplaceParams | AddParams | NumberParams | DeleteParams;
}

export interface RenameHistory {
  id: string;
  timestamp: number;
  operations: Array<{
    oldPath: string;
    newPath: string;
  }>;
}

// Electron 环境下的重命名相关类型
export interface RenamePreview {
  originalName: string;
  newName: string;
  path: string;
  valid: boolean;
  error?: string;
}

export interface BatchRenameResult {
  success: boolean;
  totalFiles: number;
  successCount: number;
  failedCount: number;
  errors: Array<{
    file: string;
    error: string;
  }>;
}
