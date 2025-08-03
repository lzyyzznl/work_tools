import { watch } from "vue";
import { useFileSystem } from "./useFileSystem";
import type {
	AddParams,
	DeleteParams,
	NumberParams,
	RenameHistory,
	RenameOperationType,
	ReplaceParams,
} from "../types/rename";

// 为独立store创建的rename engine
export function useIndependentRenameEngine(fileStore: any, renameStore: any) {
	// 生成新文件名的核心函数
	function generateNewName(
		originalName: string,
		mode: RenameOperationType,
		params: any,
		index?: number
	): string {
		const { name: nameWithoutExt, ext } = splitFileName(originalName);

		switch (mode) {
			case "replace":
				return handleReplace(originalName, params as ReplaceParams);
			case "add":
				return handleAdd(nameWithoutExt, ext, params as AddParams);
			case "number":
				return handleNumber(
					nameWithoutExt,
					ext,
					params as NumberParams,
					index || 0
				);
			case "delete":
				return handleDelete(nameWithoutExt, ext, params as DeleteParams);
			default:
				return originalName;
		}
	}

	// 字符串替换处理
	function handleReplace(originalName: string, params: ReplaceParams): string {
		if (!params.fromStr) return originalName;
		return originalName.replace(
			new RegExp(escapeRegExp(params.fromStr), "g"),
			params.toStr
		);
	}

	// 添加前缀/后缀处理
	function handleAdd(
		nameWithoutExt: string,
		ext: string,
		params: AddParams
	): string {
		if (!params.text) return `${nameWithoutExt}${ext}`;

		if (params.isPrefix) {
			return `${params.text}${nameWithoutExt}${ext}`;
		} else {
			return `${nameWithoutExt}${params.text}${ext}`;
		}
	}

	// 添加序号处理
	function handleNumber(
		nameWithoutExt: string,
		ext: string,
		params: NumberParams,
		index: number
	): string {
		const number = params.start + index * params.step;
		const paddedNumber = number.toString().padStart(params.digits, "0");

		if (params.isPrefix) {
			return `${paddedNumber}${params.separator}${nameWithoutExt}${ext}`;
		} else {
			return `${nameWithoutExt}${params.separator}${paddedNumber}${ext}`;
		}
	}

	// 删除字符处理
	function handleDelete(
		nameWithoutExt: string,
		ext: string,
		params: DeleteParams
	): string {
		if (params.count <= 0 || params.startPos <= 0)
			return `${nameWithoutExt}${ext}`;

		let result = nameWithoutExt;
		const startIndex = params.startPos - 1; // 转换为0基索引

		if (params.fromLeft) {
			// 从左侧删除
			if (startIndex < result.length) {
				const endIndex = Math.min(startIndex + params.count, result.length);
				result = result.slice(0, startIndex) + result.slice(endIndex);
			}
		} else {
			// 从右侧删除
			const rightStartIndex = Math.max(
				0,
				result.length - startIndex - params.count + 1
			);
			const rightEndIndex = Math.max(0, result.length - startIndex + 1);
			result = result.slice(0, rightStartIndex) + result.slice(rightEndIndex);
		}

		return `${result}${ext}`;
	}

	// 分离文件名和扩展名
	function splitFileName(fileName: string): { name: string; ext: string } {
		const lastDotIndex = fileName.lastIndexOf(".");
		if (lastDotIndex === -1 || lastDotIndex === 0) {
			return { name: fileName, ext: "" };
		}
		return {
			name: fileName.slice(0, lastDotIndex),
			ext: fileName.slice(lastDotIndex),
		};
	}

	// 转义正则表达式特殊字符
	function escapeRegExp(string: string): string {
		return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
	}

	// 生成所有文件的预览
	function generatePreview() {
		const files = fileStore.files;
		const mode = renameStore.currentMode;
		const params = renameStore.currentParams;

		files.forEach((file, index) => {
			const newName = generateNewName(file.name, mode, params, index);
			fileStore.updateFilePreview(file.id, newName);
		});

		renameStore.updatePreviewTime();
	}

	// 验证重命名参数
	function validateParams(): { isValid: boolean; errors: string[] } {
		const errors: string[] = [];
		const mode = renameStore.currentMode;
		const params = renameStore.currentParams;

		switch (mode) {
			case "replace":
				const replaceParams = params as ReplaceParams;
				if (!replaceParams.fromStr) {
					errors.push("请输入要替换的字符串");
				}
				break;
			case "add":
				const addParams = params as AddParams;
				if (!addParams.text) {
					errors.push("请输入要添加的文本");
				}
				break;
			case "number":
				const numberParams = params as NumberParams;
				if (numberParams.start < 0) {
					errors.push("起始数字不能小于0");
				}
				if (numberParams.digits <= 0) {
					errors.push("数字位数必须大于0");
				}
				if (numberParams.step <= 0) {
					errors.push("步长必须大于0");
				}
				break;
			case "delete":
				const deleteParams = params as DeleteParams;
				if (deleteParams.startPos <= 0) {
					errors.push("开始位置必须大于0");
				}
				if (deleteParams.count <= 0) {
					errors.push("删除字符数必须大于0");
				}
				break;
		}

		return {
			isValid: errors.length === 0,
			errors,
		};
	}

	// 检查重命名冲突
	function checkConflicts(): { hasConflicts: boolean; conflicts: string[] } {
		const files = fileStore.files;
		const newPaths = new Set<string>();
		const conflicts: string[] = [];

		files.forEach((file, index) => {
			const newName = generateNewName(
				file.name,
				renameStore.currentMode,
				renameStore.currentParams,
				index
			);
			const newPath = file.path.replace(file.name, newName);

			if (newPaths.has(newPath)) {
				conflicts.push(newPath);
			} else {
				newPaths.add(newPath);
			}
		});

		return {
			hasConflicts: conflicts.length > 0,
			conflicts,
		};
	}

	// 执行重命名
	async function executeRename(): Promise<{
		success: boolean;
		errors: string[];
	}> {
		const validation = validateParams();
		if (!validation.isValid) {
			return { success: false, errors: validation.errors };
		}

		const conflicts = checkConflicts();
		if (conflicts.hasConflicts) {
			return {
				success: false,
				errors: [`发现重名冲突: ${conflicts.conflicts.join(", ")}`],
			};
		}

		renameStore.setExecuting(true);
		const errors: string[] = [];
		const operations: Array<{ oldPath: string; newPath: string }> = [];

		try {
			const files = fileStore.files;
			const totalFiles = files.length;

			for (let i = 0; i < files.length; i++) {
				const file = files[i];
				const newName = generateNewName(
					file.name,
					renameStore.currentMode,
					renameStore.currentParams,
					i
				);

				if (newName !== file.name) {
					const { renameFile, fileExists } = useFileSystem();
					const newPath = file.path.replace(file.name, newName);

					// 检查源文件是否存在
					const oldFileExists = await fileExists(file.path);
					if (!oldFileExists) {
						errors.push(`源文件不存在: ${file.name}`);
						continue;
					}

					// 检查目标文件是否已存在
					const newFileExists = await fileExists(newPath);
					if (newFileExists) {
						errors.push(`目标文件已存在: ${newName}`);
						continue;
					}

					try {
						await renameFile(file.path, newPath);

						operations.push({
							oldPath: file.path,
							newPath,
						});

						// 更新文件store中的文件信息
						fileStore.updateFileName(file.id, newName);
					} catch (error) {
						errors.push(`重命名文件失败 ${file.name}: ${error}`);
					}
				}

				// 更新进度
				renameStore.updateExecutionProgress(((i + 1) / totalFiles) * 100);
			}

			// 添加到历史记录
			if (operations.length > 0) {
				const historyEntry: RenameHistory = {
					id: `rename_${Date.now()}`,
					timestamp: Date.now(),
					operations,
				};
				renameStore.addToHistory(historyEntry);
			}

			renameStore.setLastExecutionTime();
			return { success: true, errors: [] };
		} catch (error) {
			errors.push(`执行重命名时发生错误: ${error}`);
			return { success: false, errors };
		} finally {
			renameStore.setExecuting(false);
		}
	}

	// 撤回最后一次操作
	async function undoLastOperation(): Promise<{
		success: boolean;
		errors: string[];
	}> {
		if (!renameStore.canUndo) {
			return { success: false, errors: ["没有可撤回的操作"] };
		}

		const lastOperation = renameStore.history[0];
		const errors: string[] = [];

		try {
			const { renameFile } = useFileSystem();
			for (const op of lastOperation.operations) {
				try {
					await renameFile(op.newPath, op.oldPath);

					// 在文件store中找到对应文件并恢复名称
					const fileName = op.oldPath.split("/").pop() || "";
					const newFileName = op.newPath.split("/").pop() || "";
					const file = fileStore.files.find((f) => f.name === newFileName);
					if (file) {
						fileStore.updateFileName(file.id, fileName);
					}
				} catch (error) {
					errors.push(`撤回操作失败 ${op.newPath}: ${error}`);
				}
			}

			// 从历史记录中移除
			renameStore.history.shift();

			return { success: true, errors: [] };
		} catch (error) {
			errors.push(`撤回操作时发生错误: ${error}`);
			return { success: false, errors };
		}
	}

	// 自动预览监听 (只在使用默认store时启用)
	if (renameStore.isAutoPreview) {
		watch(
			[
				() => renameStore.currentMode,
				() => renameStore.currentParams,
				() => fileStore.files.length,
			],
			() => {
				if (renameStore.isPreviewEnabled && fileStore.files.length > 0) {
					generatePreview();
				}
			},
			{ deep: true }
		);
	}

	return {
		generateNewName,
		generatePreview,
		validateParams,
		checkConflicts,
		executeRename,
		undoLastOperation,
		splitFileName,
	};
}