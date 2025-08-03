// 规则相关类型定义

// 规则列定义
export interface RuleColumn {
	id: string;
	name: string; // 列名（用于显示）
	field: string; // 字段名（用于数据映射）
	type: "text" | "boolean" | "select"; // 列类型，仅包含文本、布尔和枚举类型
	visible: boolean; // 是否可见
	order: number; // 显示顺序
	options?: string[]; // 枚举选项，仅在type为select时使用
}

export interface Rule {
	id: string;
	code: string;
	matchRules: string[];
	// 规则列值映射，key为列字段名，value为该规则在该列的值
	columnValues?: Record<string, string>;
}

export interface RuleConfig {
	version: string;
	settings: {
		autoSave: boolean;
		defaultExportFormat: string;
	};
	rules: Rule[];
	columns?: RuleColumn[]; // 规则列配置
}

export interface MatchResult {
	matched: boolean;
	matchInfo?: {
		index: number;
		code: string;
		matchedRule: string;
		columnValues?: Record<string, string>;
	};
}

export interface RuleValidationResult {
	isValid: boolean;
	errors: string[];
}

export interface RuleImportResult {
	success: boolean;
	message: string;
	importedCount?: number;
	skippedCount?: number;
}

export interface RuleExportResult {
	success: boolean;
	message?: string;
	filename?: string;
	error?: string;
}

export interface RuleFormData {
	code: string;
	matchRules: string[];
}
