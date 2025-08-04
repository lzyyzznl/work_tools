import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
	RenameOperationType,
	ReplaceParams,
	AddParams,
	NumberParams,
	DeleteParams,
	RenameHistory,
	Preset,
} from "../types/rename";
import { STORAGE_KEYS } from "../constants/app";

export const useRenameStore = defineStore("rename", () => {
	// 当前重命名模式
	const currentMode = ref<RenameOperationType>("replace");

	// 各种重命名参数
	const replaceParams = ref<ReplaceParams>({
		fromStr: "",
		toStr: "",
	});

	const addParams = ref<AddParams>({
		text: "",
		isPrefix: true,
	});

	const numberParams = ref<NumberParams>({
		start: 1,
		digits: 3,
		step: 1,
		separator: "_",
		isPrefix: true,
	});

	const deleteParams = ref<DeleteParams>({
		startPos: 1,
		count: 1,
		fromLeft: true,
	});

	// 预览相关状态
	const isPreviewEnabled = ref(true);
	const isAutoPreview = ref(true);
	const previewUpdateTime = ref<number>(0);

	// 操作历史
	const history = ref<RenameHistory[]>([]);
	const maxHistorySize = ref(50);

	// 预设管理
	const presets = ref<Preset[]>([]);

	// 执行状态
	const isExecuting = ref(false);
	const executionProgress = ref(0);
	const lastExecutionTime = ref<number>(0);

	// 计算属性
	const currentParams = computed(() => {
		switch (currentMode.value) {
			case "replace":
				return replaceParams.value;
			case "add":
				return addParams.value;
			case "number":
				return numberParams.value;
			case "delete":
				return deleteParams.value;
			default:
				return replaceParams.value;
		}
	});

	const canUndo = computed(() => history.value.length > 0);

	const hasValidParams = computed(() => {
		switch (currentMode.value) {
			case "replace":
				return replaceParams.value.fromStr.length > 0;
			case "add":
				return addParams.value.text.length > 0;
			case "number":
				return (
					numberParams.value.start >= 0 &&
					numberParams.value.digits > 0 &&
					numberParams.value.step > 0
				);
			case "delete":
				return deleteParams.value.startPos > 0 && deleteParams.value.count > 0;
			default:
				return false;
		}
	});

	// 存储操作
	function saveHistory() {
		try {
			localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history.value));
		} catch (error) {
			console.error("保存历史记录失败:", error);
		}
	}

	function loadHistory() {
		try {
			const saved = localStorage.getItem(STORAGE_KEYS.HISTORY);
			if (saved) {
				const parsedHistory = JSON.parse(saved);
				history.value = Array.isArray(parsedHistory) ? parsedHistory : [];
			} else {
				history.value = [];
			}
		} catch (error) {
			console.error("加载历史记录失败:", error);
			history.value = [];
		}
	}

	// 预设存储操作
	function savePresets() {
		try {
			localStorage.setItem(STORAGE_KEYS.PRESETS, JSON.stringify(presets.value));
		} catch (error) {
			console.error("保存预设失败:", error);
		}
	}

	function loadPresets() {
		try {
			const saved = localStorage.getItem(STORAGE_KEYS.PRESETS);
			if (saved) {
				const parsedPresets = JSON.parse(saved);
				presets.value = Array.isArray(parsedPresets) ? parsedPresets : [];
			} else {
				presets.value = [];
			}
		} catch (error) {
			console.error("加载预设失败:", error);
			presets.value = [];
		}
	}

	// Actions
	function setMode(mode: RenameOperationType) {
		currentMode.value = mode;
	}

	function updateReplaceParams(params: Partial<ReplaceParams>) {
		replaceParams.value = { ...replaceParams.value, ...params };
	}

	function updateAddParams(params: Partial<AddParams>) {
		addParams.value = { ...addParams.value, ...params };
	}

	function updateNumberParams(params: Partial<NumberParams>) {
		numberParams.value = { ...numberParams.value, ...params };
	}

	function updateDeleteParams(params: Partial<DeleteParams>) {
		deleteParams.value = { ...deleteParams.value, ...params };
	}

	function togglePreview() {
		isPreviewEnabled.value = !isPreviewEnabled.value;
	}

	function toggleAutoPreview() {
		isAutoPreview.value = !isAutoPreview.value;
	}

	function updatePreviewTime() {
		previewUpdateTime.value = Date.now();
	}

	function addToHistory(operation: RenameHistory) {
		history.value.unshift(operation);
		if (history.value.length > maxHistorySize.value) {
			history.value = history.value.slice(0, maxHistorySize.value);
		}
		saveHistory();
	}

	function clearHistory() {
		history.value = [];
		saveHistory();
	}
	
	function removeFileHistory(filePath: string) {
		// 从历史记录中移除与指定文件相关的操作
		history.value = history.value.map(historyEntry => {
			const filteredOperations = historyEntry.operations.filter(
				op => op.oldPath !== filePath && op.newPath !== filePath
			);
			return {
				...historyEntry,
				operations: filteredOperations
			};
		}).filter(historyEntry => historyEntry.operations.length > 0); // 移除空的操作记录
		
		saveHistory();
	}

	function setExecuting(executing: boolean) {
		isExecuting.value = executing;
		if (executing) {
			executionProgress.value = 0;
		}
	}

	function updateExecutionProgress(progress: number) {
		executionProgress.value = Math.max(0, Math.min(100, progress));
	}

	function setLastExecutionTime() {
		lastExecutionTime.value = Date.now();
	}

	function resetAllParams() {
		replaceParams.value = { fromStr: "", toStr: "" };
		addParams.value = { text: "", isPrefix: true };
		numberParams.value = {
			start: 1,
			digits: 3,
			step: 1,
			separator: "_",
			isPrefix: true,
		};
		deleteParams.value = { startPos: 1, count: 1, fromLeft: true };
	}

	// 预设管理 actions
	function addPreset(preset: Omit<Preset, "id" | "createdAt" | "updatedAt">) {
		const newPreset: Preset = {
			id: Date.now().toString(),
			...preset,
			createdAt: Date.now(),
			updatedAt: Date.now(),
		};
		presets.value.push(newPreset);
		savePresets();
	}

	function removePreset(id: string) {
		presets.value = presets.value.filter((preset) => preset.id !== id);
		savePresets();
	}

	function updatePreset(
		id: string,
		updates: Partial<Omit<Preset, "id" | "createdAt" | "updatedAt">>
	) {
		const index = presets.value.findIndex((preset) => preset.id === id);
		if (index !== -1) {
			presets.value[index] = {
				...presets.value[index],
				...updates,
				updatedAt: Date.now(),
			};
			savePresets();
		}
	}

	function applyPreset(id: string) {
		const preset = presets.value.find((p) => p.id === id);
		if (preset) {
			setMode(preset.type);
			switch (preset.type) {
				case "replace":
					updateReplaceParams(preset.params as ReplaceParams);
					break;
				case "add":
					updateAddParams(preset.params as AddParams);
					break;
				case "number":
					updateNumberParams(preset.params as NumberParams);
					break;
				case "delete":
					updateDeleteParams(preset.params as DeleteParams);
					break;
			}
		}
	}

	// 初始化时加载历史记录和预设
	loadHistory();
	loadPresets();

	return {
		// State
		currentMode,
		replaceParams,
		addParams,
		numberParams,
		deleteParams,
		isPreviewEnabled,
		isAutoPreview,
		previewUpdateTime,
		history,
		maxHistorySize,
		isExecuting,
		executionProgress,
		lastExecutionTime,

		// Computed
		currentParams,
		canUndo,
		hasValidParams,

		// Actions
		setMode,
		updateReplaceParams,
		updateAddParams,
		updateNumberParams,
		updateDeleteParams,
		togglePreview,
		toggleAutoPreview,
		updatePreviewTime,
		addToHistory,
		clearHistory,
		setExecuting,
		updateExecutionProgress,
		setLastExecutionTime,
		resetAllParams,

		// Storage actions
		saveHistory,
		loadHistory,

		// Preset actions
		addPreset,
		removePreset,
		updatePreset,
		applyPreset,

		// Preset storage actions
		savePresets,
		loadPresets,

		// Preset state
		presets,
	};
});
