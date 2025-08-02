// See the Electron documentation for details on how to use preload scripts:
// https://www.electronjs.org/docs/latest/tutorial/process-model#preload-scripts

import { contextBridge, ipcRenderer, webUtils } from "electron";
import type { FileData } from "../renderer/types/fileSystem";

// 文件系统 API 接口定义
interface FileSelectOptions {
	multiple?: boolean;
	filters?: Array<{ name: string; extensions: string[] }>;
}

interface FileOperationResult {
	success: boolean;
	message?: string;
	error?: string;
}

// 暴露安全的 API 到渲染进程
contextBridge.exposeInMainWorld("electronAPI", {
	fileSystem: {
		selectFiles: async (
			options: FileSelectOptions = {}
		): Promise<FileData[]> => {
			try {
				const fileDataArray: FileData[] = await ipcRenderer.invoke(
					"file-system:select-files",
					options
				);
				return fileDataArray;
			} catch (error) {
				console.error("Error selecting files:", error);
				throw error;
			}
		},

		selectDirectory: async (): Promise<FileData[]> => {
			try {
				const fileDataArray: FileData[] = await ipcRenderer.invoke(
					"file-system:select-directory"
				);
				return fileDataArray;
			} catch (error) {
				console.error("Error selecting directory:", error);
				throw error;
			}
		},

		readFile: async (path: string): Promise<ArrayBuffer> => {
			try {
				return await ipcRenderer.invoke("file-system:read-file", path);
			} catch (error) {
				console.error("Error reading file:", error);
				throw error;
			}
		},

		writeFile: async (
			path: string,
			data: ArrayBuffer
		): Promise<FileOperationResult> => {
			try {
				return await ipcRenderer.invoke("file-system:write-file", path, data);
			} catch (error) {
				console.error("Error writing file:", error);
				throw error;
			}
		},

		renameFile: async (
			oldPath: string,
			newPath: string
		): Promise<FileOperationResult> => {
			try {
				return await ipcRenderer.invoke(
					"file-system:rename-file",
					oldPath,
					newPath
				);
			} catch (error) {
				console.error("Error renaming file:", error);
				throw error;
			}
		},

		checkFileExists: async (filePath: string): Promise<boolean> => {
			try {
				return await ipcRenderer.invoke(
					"file-system:check-file-exists",
					filePath
				);
			} catch (error) {
				console.error("Error checking file existence:", error);
				throw error;
			}
		},

		getFilesFromPath: async (filePath: string): Promise<FileData[]> => {
			try {
				return await ipcRenderer.invoke(
					"file-system:get-files-from-path",
					filePath
				);
			} catch (error) {
				console.error("Error getting files from path:", error);
				throw error;
			}
		},

		getPathForFile: async (file: File): Promise<string> => {
			return webUtils.getPathForFile(file);
		},
	},

	dialog: {
		showSaveDialog: async (options: any) => {
			try {
				return await ipcRenderer.invoke("dialog:show-save-dialog", options);
			} catch (error) {
				console.error("Error showing save dialog:", error);
				throw error;
			}
		},
	},
});
