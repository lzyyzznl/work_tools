<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useErrorHandler } from "../../composables/useErrorHandler";
import { useFileSystem } from "../../composables/useFileSystem";
import { useFileMatcherStore } from "../../stores/fileMatcherStore";
import { useRuleStore } from "../../stores/ruleStore";
import FileTable from "../common/FileTable.vue";
import RuleManager from "./RuleManager.vue";

// 为keep-alive添加组件名称
defineOptions({
	name: "FileMatcherTab"
});
const fileStore = useFileMatcherStore();
const ruleStore = useRuleStore();
const { handleDrop } = useFileSystem();
const { handleError, handleOperation } = useErrorHandler();

const isDragOver = ref(false);
const isMatching = ref(false);
const showRuleManager = ref(false);
const isAutoMatching = ref(false);
const fileTableRef = ref<InstanceType<typeof FileTable> | null>(null);

// 计算属性
const hasFiles = computed(() => fileStore.files.length > 0);
const hasRules = computed(() => ruleStore.rules.length > 0);
const canMatch = computed(() => hasFiles.value && hasRules.value);

// 动态列配置 - 从规则模块读取列配置
const dynamicColumns = computed(() => {
	// 使用规则模块的可见列配置
	return ruleStore.visibleColumns.map((column) => ({
		field: column.field,
		title: column.name,
		width: 120,
		align: "center",
		// 使用默认插槽，具体渲染在FileTable中处理
	}));
});

// 监听文件变化，自动匹配
watch(
	() => fileStore.files.length,
	(newLength, oldLength) => {
		// 只有在文件增加时才自动匹配，避免在文件减少时也触发
		if (newLength > oldLength && hasRules.value && !isAutoMatching.value) {
			isAutoMatching.value = true;
			autoMatch();
		}
	}
);

// 监听规则变化，如果有文件则自动匹配
watch(
	() => ruleStore.rules.length,
	(newLength, oldLength) => {
		if (hasFiles.value && newLength > 0 && !isAutoMatching.value) {
			isAutoMatching.value = true;
			autoMatch();
		}
	}
);

// 文件操作
async function handleSelectFiles() {
	try {
		const fileIds = await fileStore.selectFilesFromSystem({ multiple: true });
		if (fileIds.length > 0) {
			// 获取添加的文件信息
			const addedFiles = fileStore.files.filter((file) =>
				fileIds.includes(file.id)
			);
			const fileNames = addedFiles.map((file) => file.name);
			const fileListMessage = `成功添加 ${fileIds.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
		}
	} catch (error) {
		handleError(error, "选择文件失败");
	}
}

async function handleSelectDirectory() {
	try {
		const fileIds = await fileStore.selectDirectoryFromSystem();
		if (fileIds.length > 0) {
			// 获取添加的文件信息
			const addedFiles = fileStore.files.filter((file) =>
				fileIds.includes(file.id)
			);
			const fileNames = addedFiles.map((file) => file.name);
			const fileListMessage = `成功添加 ${fileIds.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
		}
	} catch (error) {
		handleError(error, "选择目录失败");
	}
}

function handleDragEnter(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = true;
}

function handleDragLeave(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = false;
}

async function handleDropFiles(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = false;

	try {
		const files = await handleDrop(e);
		if (files.length > 0) {
			const fileIds = fileStore.addFiles(files);
			// 提供详细的文件列表信息
			const fileNames = files.map((file) => file.name);
			const fileListMessage = `成功添加 ${files.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
		}
	} catch (error) {
		handleError(error, "拖拽文件失败");
	}
}

function clearFiles() {
	fileStore.clearFiles();
	handleOperation("文件操作", "已清空文件列表");
}

// 批量移除选中文件
function handleRemoveSelectedFiles() {
	const selectedFiles = fileTableRef.value?.getSelectedFiles() || [];
	if (selectedFiles.length === 0) return;

	// 确认对话框防止误操作
	if (confirm(`确定要移除选中的 ${selectedFiles.length} 个文件吗？`)) {
		const fileIds = selectedFiles.map((file) => file.id);
		fileStore.removeFiles(fileIds);
		// 清除表格中的选中状态
		fileTableRef.value?.unselectAll();
		handleOperation("文件操作", `已移除 ${selectedFiles.length} 个文件`);
	}
}

// 自动匹配函数
async function autoMatch() {
	if (!canMatch.value) {
		isAutoMatching.value = false;
		return;
	}

	try {
		let matchedCount = 0;

		// 只匹配新增的文件（未匹配过的文件）
		const newFiles = fileStore.files.filter(
			(file) => !file.matched && !file.matchInfo
		);
		newFiles.forEach((file) => {
			const result = ruleStore.matchFilename(file.name);
			fileStore.updateFileMatchResult(
				file.id,
				result.matched,
				result.matchInfo
			);
			if (result.matched) {
				matchedCount++;
			}
		});

		if (newFiles.length > 0) {
			handleOperation(
				"匹配操作",
				`自动匹配完成，共匹配 ${matchedCount} 个文件`
			);
		}
	} catch (error) {
		handleError(error, "文件自动匹配失败");
	} finally {
		isAutoMatching.value = false;
	}
}

// 匹配操作（手动触发，匹配所有文件）
async function executeMatch() {
	if (!canMatch.value) return;

	isMatching.value = true;
	try {
		let matchedCount = 0;

		// 匹配所有文件
		fileStore.files.forEach((file) => {
			const result = ruleStore.matchFilename(file.name);
			fileStore.updateFileMatchResult(
				file.id,
				result.matched,
				result.matchInfo
			);
			if (result.matched) {
				matchedCount++;
			}
		});

		// 提供详细的统计信息
		const stats = {
			total: fileStore.files.length,
			success: matchedCount,
			failed: fileStore.files.length - matchedCount,
		};
		const message = `匹配完成，总共: ${stats.total}, 匹配成功: ${stats.success}, 匹配失败: ${stats.failed}`;
		handleOperation("匹配操作", message, undefined, undefined, stats);
	} catch (error) {
		handleError(error, "文件匹配失败");
	} finally {
		isMatching.value = false;
	}
}

function clearMatchResults() {
	fileStore.files.forEach((file) => {
		fileStore.updateFileMatchResult(file.id, false);
	});
	handleOperation("匹配操作", "已清除匹配结果");
}

// 规则管理
function openRuleManager() {
	showRuleManager.value = true;
}

function closeRuleManager() {
	showRuleManager.value = false;
}

// 导出功能
function handleExport() {
	if (!fileTableRef.value) return;
	fileTableRef.value.exportExcel();
	// handleOperation("导出操作", "已触发导出功能"); // 将在 onExport 中处理日志
}

// 监听导出事件
function onExport(event: {
	success: boolean;
	message: string;
	fileCount?: number;
	filePath?: string;
	fileNames?: string[];
	error?: any;
}) {
	handleOperation("导出操作", event.message, {
		fileCount: event.fileCount,
		filePath: event.filePath,
		fileNames: event.fileNames,
		error: event.error,
	});
}

// 监听选择变化事件
function onSelectionChanged(selectedFiles: any[]) {
	// 重置选中状态
	fileStore.unselectAllFiles();

	// 更新选中状态
	selectedFiles.forEach((file) => {
		fileStore.selectFile(file.id);
	});
}
</script>

<template>
	<div class="file-matcher-tab flex flex-col h-full bg-gray-50">
		<!-- 工具栏 - 压缩高度 -->
		<div
			class="toolbar bg-white border-b border-gray-200 shadow-sm flex-shrink-0"
		>
			<div class="max-w-full mx-auto px-3 py-2">
				<div
					class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2"
				>
					<!-- 左侧按钮组 -->
					<div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
						<button
							@click="handleSelectFiles"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
						>
							<span class="text-sm">📁</span>
							<span class="hidden sm:inline">选择文件</span>
							<span class="sm:hidden">文件</span>
						</button>

						<button
							@click="handleSelectDirectory"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
						>
							<span class="text-sm">📂</span>
							<span class="hidden sm:inline">选择目录</span>
							<span class="sm:hidden">目录</span>
						</button>

						<button
							v-if="hasFiles"
							@click="clearFiles"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-red-600 text-white hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
						>
							<span class="text-sm">🗑️</span>
							<span class="hidden sm:inline">清空文件</span>
							<span class="sm:hidden">清空</span>
						</button>

						<button
							v-if="hasFiles && fileStore.fileStats.selected > 0"
							@click="handleRemoveSelectedFiles"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-orange-500 text-white hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
						>
							<span class="text-sm">❌</span>
							<span class="hidden sm:inline">移除选中</span>
							<span class="sm:hidden">移除</span>
							<span class="hidden sm:inline"
								>({{ fileStore.fileStats.selected }})</span
							>
						</button>
					</div>

					<!-- 右侧按钮组 -->
					<div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
						<button
							v-if="hasFiles"
							@click="handleExport"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
						>
							<span class="text-sm">📤</span>
							<span class="hidden sm:inline">导出</span>
						</button>

						<button
							@click="openRuleManager"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
						>
							<span class="text-sm">⚙️</span>
							<span class="hidden sm:inline">管理规则</span>
							<span class="sm:hidden">规则</span>
						</button>

						<button
							@click="executeMatch"
							:disabled="!canMatch || isMatching"
							class="inline-flex items-center gap-1.5 px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-green-600 text-white hover:bg-green-700 focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:hover:bg-green-600"
						>
							<span v-if="isMatching" class="text-sm">⏳</span>
							<span v-else class="text-sm">🎯</span>
							<span class="hidden sm:inline">{{
								isMatching ? "匹配中..." : "开始匹配"
							}}</span>
							<span class="sm:hidden">{{
								isMatching ? "匹配中" : "匹配"
							}}</span>
						</button>

						<button
							v-if="hasFiles"
							@click="clearMatchResults"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-orange-500 text-white hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
						>
							<span class="text-sm">🔄</span>
							<span class="hidden sm:inline">清除结果</span>
							<span class="sm:hidden">清除</span>
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- 主内容区域 - 最大化表格空间 -->
		<div class="flex-1 flex flex-col min-h-0 bg-gray-50">
			<div class="flex-1 p-2 sm:p-3">
				<div
					class="drop-zone h-full flex flex-col relative overflow-hidden border-2 border-dashed rounded-xl transition-all duration-300 bg-white"
					:class="{
						'border-blue-400 bg-blue-50 shadow-lg': isDragOver,
						'border-gray-300 hover:border-gray-400': !isDragOver,
					}"
					@dragenter="handleDragEnter"
					@dragover.prevent
					@dragleave="handleDragLeave"
					@drop="handleDropFiles"
				>
					<!-- 文件表格 - 占据最大空间 -->
					<div
						class="file-table-wrapper flex-1 min-h-0 rounded-xl overflow-hidden"
					>
						<FileTable
							ref="fileTableRef"
							:show-match-info="true"
							:show-selection="true"
							:show-preview="false"
							:file-store="fileStore"
							:columns="dynamicColumns"
							@export="onExport"
							@selection-changed="onSelectionChanged"
						/>
					</div>

					<!-- 拖拽提示 -->
					<div
						v-if="isDragOver"
						class="absolute inset-0 flex items-center justify-center pointer-events-none bg-blue-50/90 backdrop-blur-sm"
					>
						<div class="text-center p-6">
							<div class="text-3xl sm:text-5xl mb-3 animate-bounce">📁</div>
							<div class="text-lg sm:text-xl font-semibold text-blue-600 mb-2">
								拖拽文件到此处
							</div>
							<div class="text-xs sm:text-sm text-blue-500">
								支持文件和文件夹
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 状态提示 - 压缩高度 -->
		<div
			v-if="hasFiles && !hasRules"
			class="status-bar bg-yellow-50 border-t border-yellow-200 flex-shrink-0"
		>
			<div class="max-w-full mx-auto px-3 py-2">
				<div
					class="flex flex-col sm:flex-row sm:items-center gap-2 text-yellow-800"
				>
					<div class="flex items-start gap-2 flex-1">
						<span class="text-lg flex-shrink-0">⚠️</span>
						<div class="min-w-0">
							<div class="font-medium text-xs sm:text-sm">尚未配置匹配规则</div>
							<div class="text-xs text-yellow-700">
								请先添加匹配规则才能进行文件匹配
							</div>
						</div>
					</div>
					<button
						@click="openRuleManager"
						class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg transition-all duration-200 bg-yellow-600 text-white hover:bg-yellow-700 focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 flex-shrink-0"
					>
						<span class="text-sm">➕</span>
						添加规则
					</button>
				</div>
			</div>
		</div>

		<!-- 匹配统计 - 压缩高度 -->
		<div
			v-if="hasFiles && hasRules"
			class="stats-bar bg-white border-t border-gray-200 flex-shrink-0 mb-4"
		>
			<div class="max-w-full mx-auto px-3 py-2">
				<div
					class="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-2"
				>
					<!-- 统计数据 -->
					<div
						class="grid grid-cols-2 sm:grid-cols-4 gap-2 lg:flex lg:items-center lg:gap-4"
					>
						<div class="flex items-center gap-1.5 min-w-0">
							<span class="text-xs text-gray-500 flex-shrink-0">总文件:</span>
							<span class="font-semibold text-gray-900 text-xs truncate">{{
								fileStore.fileStats.total
							}}</span>
						</div>
						<div class="flex items-center gap-1.5 min-w-0">
							<span class="text-xs text-gray-500 flex-shrink-0">已匹配:</span>
							<span class="font-semibold text-green-600 text-xs truncate">{{
								fileStore.fileStats.matched
							}}</span>
						</div>
						<div class="flex items-center gap-1.5 min-w-0">
							<span class="text-xs text-gray-500 flex-shrink-0">未匹配:</span>
							<span class="font-semibold text-red-600 text-xs truncate">{{
								fileStore.fileStats.unmatched
							}}</span>
						</div>
						<div class="flex items-center gap-1.5 min-w-0">
							<span class="text-xs text-gray-500 flex-shrink-0">已选中:</span>
							<span class="font-semibold text-blue-600 text-xs truncate">{{
								fileStore.fileStats.selected
							}}</span>
						</div>
					</div>

					<!-- 规则数量 -->
					<div class="flex items-center gap-1.5 lg:flex-shrink-0">
						<span class="text-xs text-gray-500">规则数量:</span>
						<span class="font-semibold text-purple-600 text-xs">{{
							ruleStore.ruleCount
						}}</span>
					</div>
				</div>
			</div>
		</div>

		<!-- 规则管理器模态框 -->
		<div
			v-if="showRuleManager"
			class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4"
			@click.self="closeRuleManager"
		>
			<div
				class="bg-white rounded-xl shadow-2xl w-full max-w-6xl h-full max-h-[90vh] flex flex-col overflow-hidden"
			>
				<!-- 模态框头部 -->
				<div
					class="flex items-center justify-between p-3 sm:p-4 border-b border-gray-200 bg-gray-50 flex-shrink-0"
				>
					<h2 class="text-base sm:text-lg font-semibold text-gray-900">
						规则管理
					</h2>
					<button
						@click="closeRuleManager"
						class="inline-flex items-center justify-center w-8 h-8 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-all duration-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
					>
						<span class="text-lg">✕</span>
						<span class="sr-only">关闭</span>
					</button>
				</div>

				<!-- 模态框内容 -->
				<div class="flex-1 overflow-hidden bg-white">
					<RuleManager />
				</div>
			</div>
		</div>
	</div>
</template>
