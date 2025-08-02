import { dialog } from "electron";
import fs from "node:fs/promises";
import path from "node:path";
import type { FileData } from "../renderer/types/fileSystem";

interface FileSelectOptions {
	multiple?: boolean;
	filters?: Array<{ name: string; extensions: string[] }>;
}

interface FileOperationResult {
	success: boolean;
	message?: string;
	error?: string;
}

// 根据文件扩展名获取 MIME 类型
export function getFileType(filePath: string): string {
	const ext = path.extname(filePath).toLowerCase();
	const mimeTypes: Record<string, string> = {
		".txt": "text/plain",
		".pdf": "application/pdf",
		".doc": "application/msword",
		".docx":
			"application/vnd.openxmlformats-officedocument.wordprocessingml.document",
		".xlsx":
			"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		".xls": "application/vnd.ms-excel",
		".csv": "text/csv",
		".jpg": "image/jpeg",
		".jpeg": "image/jpeg",
		".png": "image/png",
		".gif": "image/gif",
		".bmp": "image/bmp",
		".svg": "image/svg+xml",
		".zip": "application/zip",
		".rar": "application/x-rar-compressed",
		".7z": "application/x-7z-compressed",
		".tar": "application/x-tar",
		".gz": "application/gzip",
	};

	return mimeTypes[ext] || "application/octet-stream";
}

// 选择文件
export async function selectFiles(
	options: FileSelectOptions = {}
): Promise<FileData[]> {
	try {
		const result = await dialog.showOpenDialog({
			properties: [
				"openFile",
				...(options.multiple ? ["multiSelections" as const] : []),
			],
			filters: options.filters || [{ name: "All Files", extensions: ["*"] }],
		});

		if (result.canceled) {
			return [];
		}

		const files: FileData[] = [];
		for (const filePath of result.filePaths) {
			try {
				const stats = await fs.stat(filePath);
				const fileBuffer = await fs.readFile(filePath);

				const fileData: FileData = {
					name: path.basename(filePath),
					path: filePath,
					size: stats.size,
					lastModified: stats.mtime.getTime(),
					type: getFileType(filePath),
					arrayBuffer: fileBuffer.buffer.slice(
						fileBuffer.byteOffset,
						fileBuffer.byteOffset + fileBuffer.byteLength
					) as ArrayBuffer,
				};

				files.push(fileData);
			} catch (error) {
				console.error(`Error reading file ${filePath}:`, error);
			}
		}

		return files;
	} catch (error) {
		console.error("Error selecting files:", error);
		throw error;
	}
}

// 选择目录
export async function selectDirectory(): Promise<FileData[]> {
	try {
		const result = await dialog.showOpenDialog({
			properties: ["openDirectory"],
		});

		if (result.canceled) {
			return [];
		}

		const files: FileData[] = [];
		const directoryPath = result.filePaths[0];

		async function readDirectory(dirPath: string) {
			const entries = await fs.readdir(dirPath, { withFileTypes: true });

			for (const entry of entries) {
				const fullPath = path.join(dirPath, entry.name);

				if (entry.isFile()) {
					try {
						const stats = await fs.stat(fullPath);
						const fileBuffer = await fs.readFile(fullPath);

						const fileData: FileData = {
							name: entry.name,
							path: fullPath,
							size: stats.size,
							lastModified: stats.mtime.getTime(),
							type: getFileType(fullPath),
							arrayBuffer: fileBuffer.buffer.slice(
								fileBuffer.byteOffset,
								fileBuffer.byteOffset + fileBuffer.byteLength
							) as ArrayBuffer,
						};

						files.push(fileData);
					} catch (error) {
						console.error(`Error reading file ${fullPath}:`, error);
					}
				} else if (entry.isDirectory()) {
					await readDirectory(fullPath);
				}
			}
		}

		await readDirectory(directoryPath);
		return files;
	} catch (error) {
		console.error("Error selecting directory:", error);
		throw error;
	}
}

// 读取文件
export async function readFile(filePath: string): Promise<ArrayBuffer> {
	try {
		const buffer = await fs.readFile(filePath);
		return buffer.buffer.slice(
			buffer.byteOffset,
			buffer.byteOffset + buffer.byteLength
		) as ArrayBuffer;
	} catch (error) {
		console.error("Error reading file:", error);
		throw error;
	}
}

// 写入文件
export async function writeFile(
	filePath: string,
	data: ArrayBuffer
): Promise<FileOperationResult> {
	try {
		const buffer = Buffer.from(data as ArrayBuffer);
		await fs.writeFile(filePath, buffer);
		return { success: true, message: "File written successfully" };
	} catch (error) {
		console.error("Error writing file:", error);
		return {
			success: false,
			error: error instanceof Error ? error.message : "Unknown error",
		};
	}
}

// 检查文件是否存在
export async function checkFileExists(filePath: string): Promise<boolean> {
	try {
		await fs.access(filePath);
		return true;
	} catch {
		return false;
	}
}

// 重命名文件
export async function renameFile(
	oldPath: string,
	newPath: string
): Promise<FileOperationResult> {
	try {
		// 检查源文件是否存在
		const oldFileExists = await checkFileExists(oldPath);
		if (!oldFileExists) {
			return {
				success: false,
				error: `源文件不存在: ${oldPath}`,
			};
		}

		// 检查目标文件是否已存在
		const newFileExists = await checkFileExists(newPath);
		if (newFileExists) {
			return {
				success: false,
				error: `目标文件已存在: ${newPath}`,
			};
		}

		await fs.rename(oldPath, newPath);
		return { success: true, message: "File renamed successfully" };
	} catch (error) {
		console.error("Error renaming file:", error);
		return {
			success: false,
			error: error instanceof Error ? error.message : "Unknown error",
		};
	}
}
