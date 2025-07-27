// 规则相关类型定义

export interface Rule {
	id: string;
	code: string;
	thirtyD: string;
	matchRules: string[];
	source: "default" | "user";
}

export interface RuleConfig {
	version: string;
	settings: {
		autoSave: boolean;
		defaultExportFormat: string;
	};
	rules: {
		default: Rule[];
		user: Rule[];
	};
}

export interface MatchResult {
	matched: boolean;
	matchInfo?: {
		code: string;
		thirtyD: string;
		matchedRule: string;
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
	thirtyD: string;
	matchRules: string[];
}
