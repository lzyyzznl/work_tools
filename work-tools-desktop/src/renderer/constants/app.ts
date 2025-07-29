// 应用程序常量定义

export const APP_CONFIG = {
	name: "批量文件处理工具",
	version: "1.0.0",
	description: "文件匹配和重命名桌面应用",
	author: "lizeyu",
	homepage: "https://github.com/lizeyu/work-tools-desktop",
} as const;

export const SUPPORTED_LANGUAGES = {
	"zh-CN": "简体中文",
	"en-US": "English",
} as const;

export const THEMES = {
	light: "浅色主题",
	dark: "深色主题",
	auto: "跟随系统",
} as const;

export const FILE_SIZE_LIMITS = {
	MAX_FILE_SIZE: 100 * 1024 * 1024, // 100MB
	MAX_FILES_COUNT: 1000,
	MAX_BATCH_SIZE: 50,
} as const;

export const EXPORT_FORMATS = {
	xlsx: "Excel 文件 (.xlsx)",
	csv: "CSV 文件 (.csv)",
} as const;

export const NOTIFICATION_DURATION = {
	success: 3000,
	error: 5000,
	warning: 4000,
	info: 3000,
} as const;

export const KEYBOARD_SHORTCUTS = {
	SAVE: "Ctrl+S",
	OPEN: "Ctrl+O",
	EXPORT: "Ctrl+E",
	CLEAR: "Ctrl+Delete",
	SELECT_ALL: "Ctrl+A",
	REFRESH: "F5",
	HELP: "F1",
} as const;

export const DRAG_DROP_TYPES = {
	FILES: "Files",
	TEXT: "text/plain",
} as const;

export const STORAGE_KEYS = {
	SETTINGS: "app-settings",
	RULES: "user-rules",
	HISTORY: "operation-history",
	RECENT_FILES: "recent-files",
	PRESETS: "rename-presets",
} as const;
