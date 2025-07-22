<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useFileStore } from "../../stores/fileStore";
import { useRuleStore } from "../../stores/ruleStore";
import { useFileSystem } from "../../composables/useFileSystem";
import FileTable from "../../components/common/FileTable.vue";
import RuleManager from "../../components/file-matcher/RuleManager.vue";

const fileStore = useFileStore();
const ruleStore = useRuleStore();
const { selectFiles, selectDirectory, handleDrop } = useFileSystem();

// 状态管理
const isDragOver = ref(false);
const showRuleManager = ref(false);
const currentView = ref<"files" | "rules">("files");

async function handleSelectFiles() {
	try {
		const files = await selectFiles({ multiple: true });
		if (files.length > 0) {
			fileStore.addFiles(files);
			// 自动执行匹配
			await performMatching();
		}
	} catch (error) {
		console.error("选择文件失败:", error);
	}
}

async function handleSelectDirectory() {
	try {
		const files = await selectDirectory();
		if (files.length > 0) {
			fileStore.addFiles(files);
			// 自动执行匹配
			await performMatching();
		}
	} catch (error) {
		console.error("选择文件夹失败:", error);
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
		// 自动执行匹配
		performMatching();
	}
}

async function performMatching() {
	for (const file of fileStore.files) {
		const result = ruleStore.matchFilename(file.name);
		fileStore.updateFileMatchResult(file.id, result.matched, result.matchInfo);
	}
}

function clearFiles() {
	fileStore.clearFiles();
}

function exportResults() {
	const matchedFiles = fileStore.files.filter((f) => f.matched);
	if (matchedFiles.length === 0) {
		alert("没有匹配的文件可以导出");
		return;
	}

	// 准备导出数据
	const exportData = matchedFiles.map((file) => ({
		文件名: file.name,
		文件路径: file.path,
		文件大小: formatFileSize(file.size),
		修改时间: new Date(file.lastModified).toLocaleString("zh-CN"),
		匹配代码: file.matchInfo?.code || "",
		"30D标记": file.matchInfo?.thirtyD || "",
		匹配规则: file.matchInfo?.matchedRule || "",
	}));

	// 创建CSV内容
	const headers = Object.keys(exportData[0]);
	const csvContent = [
		headers.join(","),
		...exportData.map((row) =>
			headers.map((header) => `"${row[header as keyof typeof row]}"`).join(",")
		),
	].join("\n");

	// 下载文件
	const blob = new Blob(["\uFEFF" + csvContent], {
		type: "text/csv;charset=utf-8;",
	});
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `file-match-results-${
		new Date().toISOString().split("T")[0]
	}.csv`;
	a.click();
	URL.revokeObjectURL(url);
}

function openRuleManager() {
	currentView.value = "rules";
}

function switchToFilesView() {
	currentView.value = "files";
}

// 导入formatFileSize函数
const { formatFileSize } = useFileSystem();

// 组件挂载时初始化
onMounted(async () => {
	await ruleStore.loadRules();
});
</script>

<template>
	<div class="page-container">
		<!-- 页面头部 -->
		<header class="page-header">
			<div class="header-content">
				<h1 class="page-title">
					<span class="page-icon">🔍</span>
					文件匹配工具
				</h1>
				<p class="page-description">
					根据预定义规则匹配文件名，支持批量处理和自定义规则
				</p>
			</div>
		</header>

		<!-- 工具栏 -->
		<div class="page-toolbar">
			<div class="toolbar-section">
				<!-- 视图切换 -->
				<div class="view-tabs">
					<button
						:class="['view-tab', { active: currentView === 'files' }]"
						@click="switchToFilesView"
					>
						📄 文件列表
					</button>
					<button
						:class="['view-tab', { active: currentView === 'rules' }]"
						@click="openRuleManager"
					>
						⚙️ 规则管理
					</button>
				</div>
			</div>

			<div class="toolbar-spacer"></div>

			<div class="toolbar-section" v-if="currentView === 'files'">
				<button class="btn btn-primary" @click="handleSelectFiles">
					📁 选择文件
				</button>
				<button class="btn" @click="handleSelectDirectory">
					📂 选择文件夹
				</button>
				<div class="toolbar-divider"></div>
				<button class="btn" @click="clearFiles" :disabled="!fileStore.hasFiles">
					🗑️ 清空文件
				</button>
				<button
					class="btn"
					@click="performMatching"
					:disabled="!fileStore.hasFiles"
				>
					🔄 重新匹配
				</button>
				<button
					class="btn"
					@click="exportResults"
					:disabled="!fileStore.hasFiles"
				>
					📊 导出结果
				</button>
			</div>
		</div>

		<!-- 主内容区域 -->
		<main
			class="page-main"
			:class="{ 'drag-over': isDragOver && currentView === 'files' }"
			@dragenter="currentView === 'files' ? handleDragEnter : null"
			@dragover.prevent
			@dragleave="currentView === 'files' ? handleDragLeave : null"
			@drop="currentView === 'files' ? handleDropFiles : null"
		>
			<div class="page-content">
				<!-- 文件列表视图 -->
				<FileTable
					v-if="currentView === 'files'"
					:show-match-info="true"
					:show-selection="true"
				/>

				<!-- 规则管理视图 -->
				<RuleManager v-if="currentView === 'rules'" />
			</div>
		</main>

		<!-- 状态栏 -->
		<footer class="page-footer">
			<div class="footer-info">
				<div class="info-item">
					<span class="info-label">文件:</span>
					<span class="info-value">{{ fileStore.fileStats.total }}</span>
				</div>
				<div class="info-item">
					<span class="info-label">匹配:</span>
					<span class="info-value">{{ fileStore.fileStats.matched }}</span>
				</div>
				<div class="info-item">
					<span class="info-label">未匹配:</span>
					<span class="info-value">{{ fileStore.fileStats.unmatched }}</span>
				</div>
				<div class="info-item">
					<span class="info-label">选中:</span>
					<span class="info-value">{{ fileStore.fileStats.selected }}</span>
				</div>
			</div>
			<div class="footer-actions">
				<div class="action-item highlight">规则: {{ ruleStore.ruleCount }}</div>
				<div class="action-item">v1.0.0</div>
			</div>
		</footer>
	</div>
</template>

<style scoped lang="scss">
/* 文件匹配页面特定样式 */

.view-tabs {
	display: flex;
	gap: var(--spacing-xs);

	.view-tab {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		padding: var(--spacing-sm) var(--spacing-lg);
		border: 1px solid var(--color-border-primary);
		border-radius: var(--radius-md);
		background: var(--color-background-primary);
		color: var(--color-text-secondary);
		font-family: var(--font-family-primary);
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-medium);
		cursor: pointer;
		transition: all var(--transition-fast);

		&:hover {
			color: var(--color-text-primary);
			border-color: var(--color-primary);
		}

		&.active {
			background: var(--color-primary);
			color: white;
			border-color: var(--color-primary);
		}
	}
}
</style>
