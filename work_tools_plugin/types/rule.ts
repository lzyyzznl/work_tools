// 规则相关类型定义

export interface Rule {
  id: string;
  code: string;
  thirtyD: string;
  matchRules: string[];
  source: 'default' | 'user';
}

export interface RuleConfig {
  version: string;
  settings: {
    autoSave: boolean;
    defaultExportFormat: string;
    theme: string;
  };
  rules: {
    default: Rule[];
    user: Rule[];
  };
}

export interface RuleFormData {
  code: string;
  thirtyD: string;
  matchRules: string[];
}
