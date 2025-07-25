// 通用类型定义

export interface AppSettings {
  theme: 'light' | 'dark' | 'auto';
  language: 'zh-CN' | 'en-US';
  shortcuts: Record<string, string>;
  autoPreview: boolean;
  confirmBeforeExecute: boolean;
}

export interface TabItem {
  id: string;
  label: string;
  component: string;
  icon?: string;
}

export interface DialogOptions {
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'confirm';
  confirmText?: string;
  cancelText?: string;
}

export interface ToastMessage {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;
}

export interface ExportOptions {
  format: 'xlsx' | 'csv';
  filename: string;
  includeHeaders: boolean;
}

// Electron 特定的类型定义
export interface ElectronAPI {
  fileSystem: {
    selectFiles: (options: FileSelectOptions) => Promise<File[]>;
    selectDirectory: () => Promise<File[]>;
    readFile: (path: string) => Promise<ArrayBuffer>;
    writeFile: (path: string, data: ArrayBuffer) => Promise<void>;
  };
}

export interface FileSelectOptions {
  multiple?: boolean;
  accept?: Record<string, string[]>;
}

// 扩展 Window 接口以包含 Electron API
declare global {
  interface Window {
    electronAPI: ElectronAPI;
  }
}
