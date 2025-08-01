<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useFileStore } from "../../stores/fileStore";
import { useRenameStore } from "../../stores/renameStore";
import { useFileSystem } from "../../composables/useFileSystem";
import { useRenameEngine } from "../../composables/useRenameEngine";
import { useErrorHandler } from "../../composables/useErrorHandler";
import { useKeyboardShortcuts } from "../../composables/useKeyboardShortcuts";
import { useDataManager } from "../../composables/useDataManager";
import FileTable from "../common/FileTable.vue";
import RenameOperationTabs from "./RenameOperationTabs.vue";
import NotificationContainer from "../common/NotificationContainer.vue";
import SettingsModal from "../common/SettingsModal.vue";
import HelpModal from "../common/HelpModal.vue";
import ImportPreviewModal from "../common/ImportPreviewModal.vue";

// 添加对 FileTable 组件的引用类型
import type { ComponentExposed } from "vue-component-type-helpers";

const fileStore = useFileStore();
const renameStore = useRenameStore();
const { selectFiles, selectDirectory, handleDrop } = useFileSystem();
const { generatePreview, executeRename, undoLastOperation } = useRenameEngine();
const { handleError, handleSuccess, handleWarning } = useErrorHandler();
const { registerShortcut, commonShortcuts, getShortcutDisplayText } =
	useKeyboardShortcuts();
const {
	exportFileList,
	exportFullData,
	fullImport,
	confirmImport,
	cancelImport,
	showImportPreview,
	importPreview,
	isExporting,
} = useDataManager();

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

function handleDropFiles(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = false;

	const files = handleDrop(e);
	if (files.length > 0) {
		fileStore.addFiles(files);
		if (renameStore.isAutoPreview) {
			generatePreview();
		}
	}
}

function clearFiles() {
	fileStore.clearFiles();
}

async function handleExecuteRename() {
	isExecuting.value = true;
	executionMessage.value = "正在执行重命名...";

	try {
		const result = await executeRename();
		if (result.success) {
			handleSuccess("重命名操作完成！", "成功");
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
			handleSuccess("撤回操作完成！", "成功");
		} else {
			handleError(result.errors.join(", "), "撤回失败");
		}
	} catch (error) {
		handleError(error, "撤回操作");
	}
}

function handlePreview() {
	generatePreview();
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
		fileTableRef.value.exportCSV();
	}
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
			handleSuccess(
				`自动预览已${renameStore.isAutoPreview ? "开启" : "关闭"}`,
				"设置更新"
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
	<div class="file-renamer-tab flex flex-col h-full">
		<!-- 工具栏 -->
		<div
			class="toolbar flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50"
		>
			<div class="toolbar-left flex items-center gap-3">
				<button
					@click="handleSelectFiles"
					class="px-4 py-2 rounded-lg transition-colors bg-blue-600 text-white hover:bg-blue-700"
				>
					📁 选择文件
				</button>
				<button
					@click="handleSelectDirectory"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
				>
					📂 选择文件夹
				</button>
				<button
					@click="clearFiles"
					:disabled="!fileStore.hasFiles"
					class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					🗑️ 清空
				</button>
				<button
					:disabled="!fileStore.hasFiles"
					@click="handleExport"
					title="导出当前文件列表"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					<span>📤</span>
					导出
				</button>
			</div>

			<div class="toolbar-right flex items-center gap-3">
				<button
					@click="handlePreview"
					:disabled="!fileStore.hasFiles || !renameStore.hasValidParams"
					title="生成重命名预览 (Ctrl+P)"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					👁️ 预览
				</button>
				<button
					@click="handleExecuteRename"
					:disabled="
						!fileStore.hasFiles || !renameStore.hasValidParams || isExecuting
					"
					title="执行批量重命名 (Ctrl+Enter)"
					class="px-6 py-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed bg-blue-600 text-white hover:bg-blue-700"
				>
					<span v-if="isExecuting">
						⏳ 执行中...
						<span
							v-if="renameStore.executionProgress > 0"
							class="ml-2 text-xs opacity-80"
						>
							({{ Math.round(renameStore.executionProgress) }}%)
						</span>
					</span>
					<span v-else>✅ 执行重命名</span>
				</button>
				<button
					@click="handleUndoRename"
					:disabled="!renameStore.canUndo"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
				>
					↩️ 撤回
				</button>
				<button
					@click="openSettings"
					title="设置 (Ctrl+,)"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
				>
					⚙️ 设置
				</button>
				<button
					@click="openHelp"
					title="帮助 (F1)"
					class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
				>
					❓ 帮助
				</button>
			</div>
		</div>

		<!-- 执行状态消息 -->
		<div
			v-if="executionMessage"
			class="execution-message p-3 text-center text-sm font-medium"
			:class="{
				'bg-green-100 text-green-800 border-b border-green-200':
					executionMessage.includes('完成') ||
					executionMessage.includes('成功'),
				'bg-red-100 text-red-800 border-b border-red-200':
					executionMessage.includes('失败'),
				'bg-blue-100 text-blue-800 border-b border-blue-200':
					!executionMessage.includes('完成') &&
					!executionMessage.includes('成功') &&
					!executionMessage.includes('失败'),
			}"
		>
			{{ executionMessage }}
		</div>

		<!-- 重命名操作配置 -->
		<RenameOperationTabs />

		<!-- 拖拽区域 -->
		<div
			class="drop-zone flex-1 flex flex-col relative overflow-hidden border-2 border-dashed border-gray-300 m-4 rounded-lg transition-colors"
			:class="{ 'border-blue-500 bg-blue-50': isDragOver }"
			@dragenter="handleDragEnter"
			@dragover.prevent
			@dragleave="handleDragLeave"
			@drop="handleDropFiles"
		>
			<!-- 文件表格 -->
			<FileTable
				ref="fileTableRef"
				:show-preview="true"
				:show-selection="true"
			/>

			<!-- 拖拽提示 -->
			<div
				v-if="isDragOver"
				class="absolute inset-0 flex items-center justify-center pointer-events-none"
			>
				<div
					class="text-2xl font-semibold text-blue-600 bg-white px-6 py-4 rounded-lg border-2 border-blue-500"
				>
					拖拽文件到此处
				</div>
			</div>
		</div>

		<!-- 通知容器 -->
		<NotificationContainer />

		<!-- 设置模态框 -->
		<SettingsModal v-model="showSettings" />

		<!-- 帮助模态框 -->
		<HelpModal v-model="showHelp" />

		<!-- 导入预览模态框 -->
		<ImportPreviewModal
			v-model="showImportPreview"
			:preview-data="importPreview"
			@confirm="confirmImport"
			@cancel="cancelImport"
		/>
	</div>
</template>
