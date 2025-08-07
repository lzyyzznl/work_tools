<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useDataManager } from "../../composables/useDataManager";
import { useErrorHandler } from "../../composables/useErrorHandler";
import { useFileSystem } from "../../composables/useFileSystem";
import { useIndependentRenameEngine } from "../../composables/useIndependentRenameEngine";
import { useKeyboardShortcuts } from "../../composables/useKeyboardShortcuts";
import { useFileRenamerStore } from "../../stores/fileRenamerStore";
import { useRenameStore } from "../../stores/renameStore";
import FileTable from "../common/FileTable.vue";
import HelpModal from "../common/HelpModal.vue";
import ImportPreviewModal from "../common/ImportPreviewModal.vue";
import SettingsModal from "../common/SettingsModal.vue";
import RenameOperationTabs from "./RenameOperationTabs.vue";

// 添加对 FileTable 组件的引用类型
import type { ComponentExposed } from "vue-component-type-helpers";

const fileStore = useFileRenamerStore();
const renameStore = useRenameStore();
const { selectFiles, selectDirectory, handleDrop } = useFileSystem();
const {
	generatePreview,
	executeRename,
	undoLastOperation,
	cleanupFileHistory,
} = useIndependentRenameEngine(fileStore, renameStore);
const { handleError, handleSuccess, handleOperation } = useErrorHandler();
const { registerShortcut, commonShortcuts } = useKeyboardShortcuts();
const { confirmImport, cancelImport, showImportPreview, importPreview } =
	useDataManager();

const isDragOver = ref(false);
const isExecuting = ref(false);
const executionMessage = ref("");
const showSettings = ref(false);
const showHelp = ref(false);

// 添加对 FileTable 组件的引用
const fileTableRef = ref<ComponentExposed<typeof FileTable> | null>(null);

async function handleSelectFiles() {
	try {
		const files = await selectFiles({ multiple: true });
		if (files.length > 0) {
			fileStore.addFiles(files);
			// 提供详细的文件列表信息
			const fileNames = files.map((file) => file.name);
			const fileListMessage = `成功添加 ${files.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
			if (renameStore.isAutoPreview) {
				generatePreview();
			}
		}
	} catch (error) {
		handleError(error, "选择文件");
	}
}

async function handleSelectDirectory() {
	try {
		const files = await selectDirectory();
		if (files.length > 0) {
			fileStore.addFiles(files);
			// 提供详细的文件列表信息
			const fileNames = files.map((file) => file.name);
			const fileListMessage = `成功添加 ${files.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
			if (renameStore.isAutoPreview) {
				generatePreview();
			}
		}
	} catch (error) {
		handleError(error, "选择文件夹");
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
			fileStore.addFiles(files);
			// 提供详细的文件列表信息
			const fileNames = files.map((file) => file.name);
			const fileListMessage = `成功添加 ${files.length} 个文件`;
			handleOperation("文件操作", fileListMessage, undefined, fileNames);
			if (renameStore.isAutoPreview) {
				generatePreview();
			}
		}
	} catch (error) {
		handleError(error, "拖拽文件");
	}
}

function clearFiles() {
	// 清理所有文件的历史记录
	renameStore.clearHistory();
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

async function handleExecuteRename() {
	isExecuting.value = true;
	executionMessage.value = "正在执行重命名...";

	try {
		const result = await executeRename();
		if (result.success) {
			// 提供详细的成功信息
			const message = `重命名操作完成！成功: ${
				result.stats?.success || 0
			}, 失败: ${result.stats?.failed || 0}`;
			handleOperation(
				"重命名操作",
				message,
				{ renameDetails: result.renameDetails },
				undefined,
				{
					total: result.stats?.total,
					success: result.stats?.success,
					failed: result.stats?.failed,
				}
			);
			executionMessage.value = "";
		} else {
			handleError(result.errors.join(", "), "重命名失败");
			executionMessage.value = "";
		}
	} catch (error) {
		handleError(error, "重命名执行");
		executionMessage.value = "";
	} finally {
		isExecuting.value = false;
	}
}

async function handleUndoRename() {
	try {
		const result = await undoLastOperation();
		if (result.success) {
			handleOperation("撤回操作", "撤回操作完成！", {
				undoDetails: result.undoDetails,
			});
		} else {
			handleError(result.errors.join(", "), "撤回失败");
		}
	} catch (error) {
		handleError(error, "撤回操作");
	}
}

function handlePreview() {
	generatePreview();
	handleOperation("预览操作", "已生成预览");
}

function openSettings() {
	showSettings.value = true;
}

function openHelp() {
	showHelp.value = true;
}

// 添加导出方法
function handleExport() {
	if (fileTableRef.value) {
		fileTableRef.value.exportExcel();
	}
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

onMounted(() => {
	// 注册快捷键
	registerShortcut(commonShortcuts.selectFiles(handleSelectFiles));
	registerShortcut(
		commonShortcuts.clearFiles(() => {
			if (fileStore.hasFiles) {
				clearFiles();
			}
		})
	);
	registerShortcut(
		commonShortcuts.executeRename(() => {
			if (
				fileStore.hasFiles &&
				renameStore.hasValidParams &&
				!isExecuting.value
			) {
				handleExecuteRename();
			}
		})
	);
	registerShortcut(
		commonShortcuts.undoRename(() => {
			if (renameStore.canUndo) {
				handleUndoRename();
			}
		})
	);
	registerShortcut(
		commonShortcuts.preview(() => {
			if (fileStore.hasFiles && renameStore.hasValidParams) {
				handlePreview();
			}
		})
	);
	registerShortcut(
		commonShortcuts.switchToReplace(() => {
			renameStore.setMode("replace");
		})
	);
	registerShortcut(
		commonShortcuts.switchToAdd(() => {
			renameStore.setMode("add");
		})
	);
	registerShortcut(
		commonShortcuts.switchToNumber(() => {
			renameStore.setMode("number");
		})
	);
	registerShortcut(
		commonShortcuts.switchToDelete(() => {
			renameStore.setMode("delete");
		})
	);
	registerShortcut(
		commonShortcuts.toggleAutoPreview(() => {
			renameStore.toggleAutoPreview();
			handleOperation(
				"设置更新",
				`自动预览已${renameStore.isAutoPreview ? "开启" : "关闭"}`
			);
		})
	);
	registerShortcut(
		commonShortcuts.selectAll(() => {
			if (fileStore.hasFiles) {
				fileStore.selectAllFiles();
			}
		})
	);
	registerShortcut(
		commonShortcuts.deselectAll(() => {
			if (fileStore.hasFiles) {
				fileStore.unselectAllFiles();
			}
		})
	);
	registerShortcut(commonShortcuts.openSettings(openSettings));
	registerShortcut(commonShortcuts.openHelp(openHelp));
});
</script>

<template>
	<div class="file-renamer-tab flex flex-col h-full bg-gray-50">
		<!-- 工具栏 - 压缩高度 -->
		<div
			class="toolbar bg-white border-b border-gray-200 shadow-sm flex-shrink-0"
		>
			<div class="max-w-full mx-auto px-3 py-2">
				<div class="flex flex-wrap items-center gap-1.5 sm:gap-2">
					<!-- 按钮组 -->
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
							<span class="hidden sm:inline">选择文件夹</span>
							<span class="sm:hidden">文件夹</span>
						</button>

						<button
							@click="clearFiles"
							:disabled="!fileStore.hasFiles"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-red-600 text-white hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-red-600"
						>
							<span class="text-sm">🗑️</span>
							<span class="hidden sm:inline">清空</span>
						</button>

						<button
							v-if="fileStore.hasFiles && fileStore.fileStats.selected > 0"
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

						<button
							:disabled="!fileStore.hasFiles"
							@click="handleExport"
							title="导出当前文件列表"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-100"
						>
							<span class="text-sm">📤</span>
							<span class="hidden sm:inline">导出</span>
						</button>
						<button
							@click="handlePreview"
							:disabled="!fileStore.hasFiles || !renameStore.hasValidParams"
							title="生成重命名预览 (Ctrl+P)"
							class="inline-flex items-center gap-1.5 px-2.5 sm:px-3 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-100"
						>
							<span class="text-sm">👁️</span>
							<span class="hidden sm:inline">预览</span>
						</button>

						<button
							@click="handleExecuteRename"
							:disabled="
								!fileStore.hasFiles ||
								!renameStore.hasValidParams ||
								isExecuting
							"
							title="执行批量重命名 (Ctrl+Enter)"
							class="inline-flex items-center gap-1.5 px-3 sm:px-4 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed bg-blue-600 text-white hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:hover:bg-blue-600"
						>
							<span v-if="isExecuting" class="flex items-center gap-1.5">
								<span class="text-sm">⏳</span>
								<span class="hidden sm:inline">执行中...</span>
								<span class="sm:hidden">执行中</span>
								<span
									v-if="renameStore.executionProgress > 0"
									class="text-xs opacity-80 ml-1"
								>
									({{ Math.round(renameStore.executionProgress) }}%)
								</span>
							</span>
							<span v-else class="flex items-center gap-1.5">
								<span class="text-sm">✅</span>
								<span class="hidden sm:inline">执行重命名</span>
								<span class="sm:hidden">执行</span>
							</span>
						</button>

						<div class="flex items-center gap-1.5">
							<button
								@click="handleUndoRename"
								:disabled="!renameStore.canUndo"
								class="inline-flex items-center gap-1.5 px-2 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-gray-100"
							>
								<span class="text-sm">↩️</span>
								<span class="sr-only">撤回</span>
							</button>
							<!-- TODO 后面再做
							<button
								@click="openSettings"
								title="设置 (Ctrl+,)"
								class="inline-flex items-center gap-1.5 px-2 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
							>
								<span class="text-sm">⚙️</span>
								<span class="sr-only">设置</span>
							</button> -->

							<button
								@click="openHelp"
								title="帮助 (F1)"
								class="inline-flex items-center gap-1.5 px-2 py-1.5 text-xs sm:text-sm font-medium rounded-lg transition-all duration-200 bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
							>
								<span class="text-sm">❓</span>
								<span class="sr-only">帮助</span>
							</button>
						</div>
					</div>
				</div>
			</div>

			<!-- 执行状态消息 - 压缩高度 -->
			<div
				v-if="executionMessage"
				class="execution-message px-3 py-2 text-center text-xs sm:text-sm font-medium flex-shrink-0 border-b"
				:class="{
					'bg-green-50 text-green-800 border-green-200':
						executionMessage.includes('完成') ||
						executionMessage.includes('成功'),
					'bg-red-50 text-red-800 border-red-200':
						executionMessage.includes('失败'),
					'bg-blue-50 text-blue-800 border-blue-200':
						!executionMessage.includes('完成') &&
						!executionMessage.includes('成功') &&
						!executionMessage.includes('失败'),
				}"
			>
				<div class="max-w-4xl mx-auto">
					{{ executionMessage }}
				</div>
			</div>

			<!-- 重命名操作配置 - 压缩高度 -->
			<div
				class="rename-operation-container bg-white border-b border-gray-200 flex-shrink-0"
			>
				<div class="max-w-full mx-auto">
					<RenameOperationTabs />
				</div>
			</div>
		</div>
		<!-- 主内容区域 - 最大化表格空间 -->
		<div class="flex-1 flex flex-col min-h-0 bg-gray-50 mb-4">
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
							:show-preview="true"
							:show-selection="true"
							:show-execution-result="true"
							:file-store="fileStore"
							@export="onExport"
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

		<!-- 模态框 -->
		<SettingsModal v-model="showSettings" />
		<HelpModal v-model="showHelp" />
		<ImportPreviewModal
			v-model="showImportPreview"
			:preview-data="importPreview"
			@confirm="confirmImport"
			@cancel="cancelImport"
		/>
	</div>
</template>
