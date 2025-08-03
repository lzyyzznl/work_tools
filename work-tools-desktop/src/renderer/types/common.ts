// 通用类型定义
import type { FileData } from "./fileSystem";

export interface AppSettings {
	shortcuts: Record<string, string>;
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
	type: "info" | "warning" | "error" | "confirm";
	confirmText?: string;
	cancelText?: string;
}

export interface ToastMessage {
	id: string;
	type: "success" | "error" | "warning" | "info";
	message: string;
	duration?: number;
}

export interface ExportOptions {
	format: "xlsx";
	filename: string;
	includeHeaders: boolean;
}

// Electron 特定的类型定义
export interface ElectronAPI {
	fileSystem: {
		selectFiles: (options: FileSelectOptions) => Promise<FileData[]>;
		selectDirectory: () => Promise<FileData[]>;
		readFile: (path: string) => Promise<ArrayBuffer>;
		writeFile: (
			path: string,
			data: ArrayBuffer
		) => Promise<{ success: boolean; error?: string }>;
		renameFile: (
			oldPath: string,
			newPath: string
		) => Promise<{ success: boolean; error?: string }>;
		checkFileExists: (filePath: string) => Promise<boolean>;
		getPathForFile: (filePath: File) => Promise<string>;
		getFilesFromPath: (filePath: string) => Promise<FileData[]>;
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
