<template>
	<div
		class="app h-screen flex flex-col bg-gray-100 relative"
		@dragenter="handleGlobalDragEnter"
		@dragover.prevent
		@dragleave="handleGlobalDragLeave"
		@drop="handleGlobalDrop"
	>
		<!-- 导航标签 -->
		<div class="nav-tabs flex bg-white border-b border-gray-200">
			<button
				@click="switchTab('matcher')"
				class="tab-button flex-1 px-6 py-4 text-center font-medium transition-colors relative after:content-empty after:absolute after:bottom-0 after:left-0 after:right-0 after:h-2px after:bg-transparent after:transition-bg-color after:duration-200 hover:after:bg-blue-500/30"
				:class="
					activeTab === 'matcher'
						? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600 after:bg-blue-600'
						: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
				"
			>
				<div class="flex items-center justify-center gap-2">
					<span>🎯</span>
					<span>文件匹配器</span>
					<kbd class="ml-2 px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded"
						>Ctrl+1</kbd
					>
				</div>
			</button>

			<button
				@click="switchTab('renamer')"
				class="tab-button flex-1 px-6 py-4 text-center font-medium transition-colors relative after:content-empty after:absolute after:bottom-0 after:left-0 after:right-0 after:h-2px after:bg-transparent after:transition-bg-color after:duration-200 hover:after:bg-blue-500/30"
				:class="
					activeTab === 'renamer'
						? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600 after:bg-blue-600'
						: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
				"
			>
				<div class="flex items-center justify-center gap-2">
					<span>✏️</span>
					<span>文件重命名器</span>
					<kbd class="ml-2 px-2 py-1 text-xs bg-gray-200 text-gray-600 rounded"
						>Ctrl+2</kbd
					>
				</div>
			</button>
		</div>

		<!-- 主要内容区域 -->
		<div class="main-content flex-1 overflow-hidden">
			<FileMatcherTab v-if="activeTab === 'matcher'" />
			<FileRenamerTab v-if="activeTab === 'renamer'" />
		</div>

		<!-- 通知容器 -->
		<NotificationContainer />

		<!-- 全局拖拽覆盖层 -->
		<div
			v-if="isDragOver"
			class="fixed inset-0 z-50 bg-blue-500 bg-opacity-20 flex items-center justify-center pointer-events-none"
		>
			<div class="bg-white rounded-lg shadow-xl p-8 text-center">
				<div class="text-6xl mb-4">📁</div>
				<div class="text-xl font-semibold text-gray-900 mb-2">
					释放文件到此处
				</div>
				<div class="text-sm text-gray-600">支持拖拽文件或文件夹</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useFileStore } from "./stores/fileStore";
import { useRuleStore } from "./stores/ruleStore";
import { useErrorHandler } from "./composables/useErrorHandler";
import { useKeyboardShortcuts } from "./composables/useKeyboardShortcuts";
import { useFileSystem } from "./composables/useFileSystem";
import FileMatcherTab from "./components/file-matcher/FileMatcherTab.vue";
import FileRenamerTab from "./components/file-renamer/FileRenamerTab.vue";
import NotificationContainer from "./components/common/NotificationContainer.vue";

const fileStore = useFileStore();
const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();
const { registerShortcut, commonShortcuts } = useKeyboardShortcuts();
const { handleDrop } = useFileSystem();

const activeTab = ref<"matcher" | "renamer">("matcher");
const isDragOver = ref(false);

// 注册全局快捷键
onMounted(() => {
	// 切换标签页
	registerShortcut({
		key: "1",
		ctrl: true,
		description: "切换到文件匹配器",
		action: () => {
			activeTab.value = "matcher";
		},
	});

	registerShortcut({
		key: "2",
		ctrl: true,
		description: "切换到文件重命名器",
		action: () => {
			activeTab.value = "renamer";
		},
	});

	// 文件操作快捷键
	registerShortcut(
		commonShortcuts.selectFiles(async () => {
			try {
				await fileStore.selectFilesFromSystem({ multiple: true });
			} catch (error) {
				handleError(error, "选择文件失败");
			}
		})
	);

	// 初始化数据
	initializeApp();
});

async function initializeApp() {
	try {
		await ruleStore.loadRules();
	} catch (error) {
		handleError(error, "初始化应用失败");
	}
}

function switchTab(tab: "matcher" | "renamer") {
	activeTab.value = tab;
}

// 全局拖拽处理
function handleGlobalDragEnter(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = true;
}

function handleGlobalDragLeave(e: DragEvent) {
	e.preventDefault();
	// 只有当拖拽离开整个应用区域时才设置为false
	if (!e.relatedTarget || !(e.relatedTarget as Element).closest(".app")) {
		isDragOver.value = false;
	}
}

function handleGlobalDrop(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = false;

	try {
		const files = handleDrop(e);
		if (files.length > 0) {
			fileStore.addFiles(files);
			handleSuccess(`成功添加 ${files.length} 个文件`);
		}
	} catch (error) {
		handleError(error, "拖拽文件失败");
	}
}
</script>
