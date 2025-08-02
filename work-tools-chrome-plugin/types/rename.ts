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
