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
