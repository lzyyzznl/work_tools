import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { FileItem, FileStats } from "../types/file";
import type { FileData } from "../types/fileSystem";

export const useFileMatcherStore = defineStore("file-matcher", () => {
	// 状态
	const files = ref<FileItem[]>([]);
	const selectedFiles = ref<Set<string>>(new Set());
	const isLoading = ref(false);

	// 计算属性
	const fileStats = computed<FileStats>(() => {
		const total = files.value.length;
		const matched = files.value.filter((f) => f.matched).length;
		const unmatched = total - matched;
		const selected = selectedFiles.value.size;

		return { total, matched, unmatched, selected };
	});

	const selectedFileItems = computed(() => {
		return files.value.filter((f) => selectedFiles.value.has(f.id));
	});

	const hasFiles = computed(() => files.value.length > 0);

	// 操作方法
	function addFile(fileData: FileData): string {
		const id = `${fileData.name}-${fileData.lastModified}-${Math.random()}`;

		// 检查是否已存在相同文件
		const exists = files.value.some(
			(f) =>
				f.name === fileData.name &&
				f.size === fileData.size &&
				f.lastModified === fileData.lastModified
		);

		if (exists) {
			return id;
		}

		const fileItem: FileItem = {
			id,
			name: fileData.name,
			path: fileData.path,
			size: fileData.size,
			lastModified: fileData.lastModified,
			fileData,
			selected: false,
			matched: false,
		};

		// 使用展开运算符创建新数组，确保Vue的响应式系统能够检测到变化
		files.value = [...files.value, fileItem];
		return id;
	}

	function addFiles(fileDataArray: FileData[]) {
		const addedIds: string[] = [];

		fileDataArray.forEach((fileData) => {
			const id = addFile(fileData);
			addedIds.push(id);
		});

		return addedIds;
	}

	function removeFile(id: string) {
		const index = files.value.findIndex((f) => f.id === id);
		if (index > -1) {
			// 使用filter创建新数组，确保Vue的响应式系统能够检测到变化
			files.value = files.value.filter((f) => f.id !== id);
			selectedFiles.value.delete(id);
		}
	}

	function removeFiles(ids: string[]) {
		ids.forEach((id) => removeFile(id));
	}

	function clearFiles() {
		// 创建新数组，确保Vue的响应式系统能够检测到变化
		files.value = [];
		selectedFiles.value.clear();
	}

	function selectFile(id: string) {
		selectedFiles.value.add(id);
	}

	function unselectFile(id: string) {
		selectedFiles.value.delete(id);
	}

	function toggleFileSelection(id: string) {
		if (selectedFiles.value.has(id)) {
			unselectFile(id);
		} else {
			selectFile(id);
		}
	}

	function selectAllFiles() {
		files.value.forEach((f) => selectedFiles.value.add(f.id));
	}

	function unselectAllFiles() {
		selectedFiles.value.clear();
	}

	function updateFileMatchResult(
		id: string,
		matched: boolean,
		matchInfo?: any
	) {
		const index = files.value.findIndex((f) => f.id === id);
		if (index > -1) {
			// 使用展开运算符创建新对象，确保Vue的响应式系统能够检测到变化
			files.value[index] = {
				...files.value[index],
				matched,
				matchInfo,
			};
		}
	}

	function getFileById(id: string) {
		return files.value.find((f) => f.id === id);
	}

	function getFilesToProcess() {
		// 如果有选中的文件，返回选中的；否则返回全部
		return selectedFiles.value.size > 0 ? selectedFileItems.value : files.value;
	}

	// Electron 特有的方法
	async function selectFilesFromSystem(options: { multiple?: boolean } = {}) {
		try {
			isLoading.value = true;
			const selectedFileData = await window.electronAPI.fileSystem.selectFiles(
				options
			);
			const addedIds = addFiles(selectedFileData);
			return addedIds;
		} catch (error) {
			console.error("Error selecting files from system:", error);
			throw error;
		} finally {
			isLoading.value = false;
		}
	}

	async function selectDirectoryFromSystem() {
		try {
			isLoading.value = true;
			const directoryFileData =
				await window.electronAPI.fileSystem.selectDirectory();
			const addedIds = addFiles(directoryFileData);
			return addedIds;
		} catch (error) {
			console.error("Error selecting directory from system:", error);
			throw error;
		} finally {
			isLoading.value = false;
		}
	}

	return {
		// 状态
		files,
		selectedFiles,
		isLoading,

		// 计算属性
		fileStats,
		selectedFileItems,
		hasFiles,

		// 方法
		addFile,
		addFiles,
		removeFile,
		removeFiles,
		clearFiles,
		selectFile,
		unselectFile,
		toggleFileSelection,
		selectAllFiles,
		unselectAllFiles,
		updateFileMatchResult,
		getFileById,
		getFilesToProcess,

		// Electron 特有方法
		selectFilesFromSystem,
		selectDirectoryFromSystem,
	};
});