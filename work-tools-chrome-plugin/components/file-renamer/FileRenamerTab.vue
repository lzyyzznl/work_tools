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
	quickImport,
	fullImport,
	confirmImport,
	cancelImport,
	showImportPreview,
	importPreview,
	isExporting,
	isImporting,
} = useDataManager();

const isDragOver = ref(false);
const isExecuting = ref(false);
const executionMessage = ref("");
const showSettings = ref(false);
const showHelp = ref(false);

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
	<div class="file-renamer-tab">
		<!-- 工具栏 -->
		<div class="toolbar">
			<div class="toolbar-section">
				<button class="btn btn-primary" @click="handleSelectFiles">
					📁 选择文件
				</button>
				<button class="btn" @click="handleSelectDirectory">
					📂 选择文件夹
				</button>
				<button class="btn" @click="clearFiles" :disabled="!fileStore.hasFiles">
					🗑️ 清空
				</button>
				<button
					class="btn"
					@click="quickImport"
					:disabled="isImporting"
					title="导入文件列表和历史记录"
				>
					<span v-if="isImporting">⏳</span>
					<span v-else>📥</span>
					导入
				</button>
				<button
					class="btn"
					@click="() => exportFileList('csv')"
					:disabled="!fileStore.hasFiles || isExporting"
					title="导出当前文件列表为CSV格式"
				>
					<span v-if="isExporting">⏳</span>
					<span v-else>📤</span>
					导出
				</button>
			</div>

			<div class="toolbar-spacer"></div>

			<div class="toolbar-section">
				<button
					class="btn"
					@click="handlePreview"
					:disabled="!fileStore.hasFiles || !renameStore.hasValidParams"
					title="生成重命名预览 (Ctrl+P)"
				>
					👁️ 预览
				</button>
				<button
					class="btn btn-primary"
					@click="handleExecuteRename"
					:disabled="
						!fileStore.hasFiles || !renameStore.hasValidParams || isExecuting
					"
					title="执行批量重命名 (Ctrl+Enter)"
				>
					<span v-if="isExecuting">
						⏳ 执行中...
						<span
							v-if="renameStore.executionProgress > 0"
							class="progress-text"
						>
							({{ Math.round(renameStore.executionProgress) }}%)
						</span>
					</span>
					<span v-else>✅ 执行重命名</span>
				</button>
				<button
					class="btn"
					@click="handleUndoRename"
					:disabled="!renameStore.canUndo"
				>
					↩️ 撤回
				</button>
				<button class="btn" @click="openSettings" title="设置 (Ctrl+,)">
					⚙️ 设置
				</button>
				<button class="btn" @click="openHelp" title="帮助 (F1)">❓ 帮助</button>
			</div>
		</div>

		<!-- 执行状态消息 -->
		<div
			v-if="executionMessage"
			class="execution-message"
			:class="{
				success:
					executionMessage.includes('完成') ||
					executionMessage.includes('成功'),
				error: executionMessage.includes('失败'),
			}"
		>
			{{ executionMessage }}
		</div>

		<!-- 重命名操作配置 -->
		<RenameOperationTabs />

		<!-- 拖拽区域 -->
		<div
			class="drop-zone"
			:class="{ 'drag-over': isDragOver }"
			@dragenter="handleDragEnter"
			@dragover.prevent
			@dragleave="handleDragLeave"
			@drop="handleDropFiles"
		>
			<!-- 文件表格 -->
			<FileTable :show-preview="true" :show-selection="true" />
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

<style scoped lang="scss">
.file-renamer-tab {
	display: flex;
	flex-direction: column;
	height: 100%;
}

.toolbar {
	display: flex;
	align-items: center;
	padding: var(--spacing-md) var(--spacing-lg);
	background: var(--color-background-secondary);
	border-bottom: 1px solid var(--color-border-primary);

	.toolbar-section {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.toolbar-spacer {
		flex: 1;
	}
}

.execution-message {
	padding: var(--spacing-sm) var(--spacing-lg);
	font-size: var(--font-size-sm);
	font-weight: var(--font-weight-medium);
	text-align: center;

	&.success {
		background: rgba(52, 199, 89, 0.1);
		color: var(--color-success);
		border-bottom: 1px solid rgba(52, 199, 89, 0.2);
	}

	&.error {
		background: rgba(255, 59, 48, 0.1);
		color: var(--color-error);
		border-bottom: 1px solid rgba(255, 59, 48, 0.2);
	}

	&:not(.success):not(.error) {
		background: rgba(0, 122, 255, 0.1);
		color: var(--color-primary);
		border-bottom: 1px solid rgba(0, 122, 255, 0.2);
	}
}

.progress-text {
	font-size: var(--font-size-xs);
	opacity: 0.8;
	margin-left: var(--spacing-xs);
}

.btn {
	position: relative;
	overflow: hidden;

	&:disabled {
		opacity: 0.6;
		cursor: not-allowed;
	}

	&:not(:disabled):hover {
		transform: translateY(-1px);
		box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
	}

	&:not(:disabled):active {
		transform: translateY(0);
	}
}

.drop-zone {
	flex: 1;
	display: flex;
	flex-direction: column;
	position: relative;
	overflow: hidden;

	&.drag-over {
		background: rgba(0, 122, 255, 0.05);

		&::after {
			content: "拖拽文件到此处";
			position: absolute;
			top: 50%;
			left: 50%;
			transform: translate(-50%, -50%);
			font-size: var(--font-size-xl);
			font-weight: var(--font-weight-semibold);
			color: var(--color-primary);
			background: var(--color-background-primary);
			padding: var(--spacing-lg) var(--spacing-2xl);
			border-radius: var(--radius-lg);
			border: 2px dashed var(--color-primary);
			z-index: 10;
		}
	}
}
</style>
