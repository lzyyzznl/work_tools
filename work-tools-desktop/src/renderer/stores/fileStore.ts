import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { FileItem, FileStats } from "../types/file";

export const useFileStore = defineStore("file", () => {
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
	function addFile(file: File): string {
		const id = `${file.name}-${file.lastModified}-${Math.random()}`;

		// 检查是否已存在相同文件
		const exists = files.value.some(
			(f) =>
				f.name === file.name &&
				f.size === file.size &&
				f.lastModified === file.lastModified
		);

		if (exists) {
			return id;
		}

		const fileItem: FileItem = {
			id,
			name: file.name,
			// 在 Electron 环境中，优先使用 file.path 属性（如果存在）
			path: (file as any).path || file.webkitRelativePath || file.name,
			size: file.size,
			lastModified: file.lastModified,
			file,
			selected: false,
			matched: false,
		};

		files.value.push(fileItem);
		return id;
	}

	function addFiles(fileList: FileList | File[]) {
		const fileArray = Array.from(fileList);
		const addedIds: string[] = [];

		fileArray.forEach((file) => {
			const id = addFile(file);
			addedIds.push(id);
		});

		return addedIds;
	}

	function removeFile(id: string) {
		const index = files.value.findIndex((f) => f.id === id);
		if (index > -1) {
			files.value.splice(index, 1);
			selectedFiles.value.delete(id);
		}
	}

	function removeFiles(ids: string[]) {
		ids.forEach((id) => removeFile(id));
	}

	function clearFiles() {
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
		const file = files.value.find((f) => f.id === id);
		if (file) {
			file.matched = matched;
			file.matchInfo = matchInfo;
		}
	}

	function updateFilePreview(id: string, previewName: string) {
		const file = files.value.find((f) => f.id === id);
		if (file) {
			file.previewName = previewName;
		}
	}

	function updateFileExecutionResult(id: string, result: string) {
		const file = files.value.find((f) => f.id === id);
		if (file) {
			file.executionResult = result;
		}
	}

	function updateFileName(id: string, newName: string) {
		const file = files.value.find((f) => f.id === id);
		if (file) {
			file.name = newName;
			// 在 Electron 环境中，更新完整路径
			const pathParts = file.path.split(/[/\\]/);
			pathParts[pathParts.length - 1] = newName;
			file.path = pathParts.join(process.platform === 'win32' ? '\\' : '/');
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
			const selectedFiles = await window.electronAPI.fileSystem.selectFiles(options);
			const addedIds = addFiles(selectedFiles);
			return addedIds;
		} catch (error) {
			console.error('Error selecting files from system:', error);
			throw error;
		} finally {
			isLoading.value = false;
		}
	}

	async function selectDirectoryFromSystem() {
		try {
			isLoading.value = true;
			const directoryFiles = await window.electronAPI.fileSystem.selectDirectory();
			const addedIds = addFiles(directoryFiles);
			return addedIds;
		} catch (error) {
			console.error('Error selecting directory from system:', error);
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
		updateFilePreview,
		updateFileExecutionResult,
		updateFileName,
		getFileById,
		getFilesToProcess,

		// Electron 特有方法
		selectFilesFromSystem,
		selectDirectoryFromSystem,
	};
});
