<template>
	<div
		class="app h-screen flex flex-col bg-gray-50 relative overflow-hidden"
		@dragenter="handleGlobalDragEnter"
		@dragover.prevent
		@dragleave="handleGlobalDragLeave"
		@drop="handleGlobalDrop"
	>
		<!-- 导航标签 - 压缩高度 -->
		<div
			class="nav-tabs bg-white border-b border-gray-200 shadow-sm flex-shrink-0"
		>
			<div class="max-w-full mx-auto">
				<div class="flex">
					<button
						@click="switchTab('renamer')"
						class="tab-button flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-center font-medium transition-all duration-200 relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
						:class="
							activeTab === 'renamer'
								? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
								: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
						"
					>
						<div class="flex items-center justify-center gap-1.5 min-w-0">
							<span class="text-sm flex-shrink-0">✏️</span>
							<span class="text-xs sm:text-sm font-medium truncate"
								>文件重命名器</span
							>
							<kbd
								class="hidden lg:inline-flex ml-1.5 px-1.5 py-0.5 text-xs bg-gray-200 text-gray-600 rounded border border-gray-300"
							>
								Ctrl+1
							</kbd>
						</div>
					</button>

					<button
						@click="switchTab('matcher')"
						class="tab-button flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-center font-medium transition-all duration-200 relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
						:class="
							activeTab === 'matcher'
								? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
								: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
						"
					>
						<div class="flex items-center justify-center gap-1.5 min-w-0">
							<span class="text-sm flex-shrink-0">🎯</span>
							<span class="text-xs sm:text-sm font-medium truncate"
								>文件匹配器</span
							>
							<kbd
								class="hidden lg:inline-flex ml-1.5 px-1.5 py-0.5 text-xs bg-gray-200 text-gray-600 rounded border border-gray-300"
							>
								Ctrl+2
							</kbd>
						</div>
					</button>

					<button
						@click="switchTab('log')"
						class="tab-button flex-1 px-3 sm:px-4 py-2 sm:py-2.5 text-center font-medium transition-all duration-200 relative focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-inset"
						:class="
							activeTab === 'log'
								? 'text-blue-600 bg-blue-50 border-b-2 border-blue-600'
								: 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
						"
					>
						<div class="flex items-center justify-center gap-1.5 min-w-0">
							<span class="text-sm flex-shrink-0">📝</span>
							<span class="text-xs sm:text-sm font-medium truncate"
								>操作日志</span
							>
						</div>
					</button>
				</div>
			</div>
		</div>

		<!-- 主要内容区域 - 最大化空间 -->
		<div class="main-content flex-1 min-h-0 overflow-hidden">
			<FileMatcherTab v-if="activeTab === 'matcher'" />
			<FileRenamerTab v-if="activeTab === 'renamer'" />
			<LogPanel v-if="activeTab === 'log'" />
		</div>

		<!-- 全局拖拽覆盖层 -->
		<div
			v-if="isDragOver"
			class="fixed inset-0 z-50 bg-blue-500/20 backdrop-blur-sm flex items-center justify-center pointer-events-none p-4"
		>
			<div
				class="bg-white rounded-2xl shadow-2xl p-6 sm:p-8 text-center max-w-sm w-full border border-blue-200"
			>
				<div class="text-4xl sm:text-6xl mb-4 animate-bounce">📁</div>
				<div class="text-lg sm:text-xl font-semibold text-gray-900 mb-2">
					释放文件到此处
				</div>
				<div class="text-sm text-gray-600">支持拖拽文件或文件夹</div>
				<div class="mt-4 flex justify-center space-x-2">
					<div class="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
					<div
						class="w-2 h-2 bg-blue-400 rounded-full animate-pulse animate-delay-200"
					></div>
					<div
						class="w-2 h-2 bg-blue-400 rounded-full animate-pulse animate-delay-400"
					></div>
				</div>
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
import LogPanel from "./components/common/LogPanel.vue";

const fileStore = useFileStore();
const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();
const { registerShortcut, commonShortcuts } = useKeyboardShortcuts();
const { handleDrop } = useFileSystem();

const activeTab = ref<"matcher" | "renamer" | "log">("renamer");
const isDragOver = ref(false);

// 注册全局快捷键
onMounted(() => {
	// 切换标签页
	registerShortcut({
		key: "1",
		ctrl: true,
		description: "切换到文件重命名器",
		action: () => {
			activeTab.value = "renamer";
		},
	});

	registerShortcut({
		key: "2",
		ctrl: true,
		description: "切换到文件匹配器",
		action: () => {
			activeTab.value = "matcher";
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

function switchTab(tab: "matcher" | "renamer" | "log") {
	activeTab.value = tab;
}

// 全局拖拽处理
function handleGlobalDragEnter(e: DragEvent) {
	e.preventDefault();
	
	// 只有拖拽的是文件才显示拖拽提示
	if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
		isDragOver.value = true;
	}
}

function handleGlobalDragLeave(e: DragEvent) {
	e.preventDefault();
	// 只有当拖拽离开整个应用区域时才设置为false
	if (!e.relatedTarget || !(e.relatedTarget as Element).closest(".app")) {
		isDragOver.value = false;
	}
}

async function handleGlobalDrop(e: DragEvent) {
	e.preventDefault();
	isDragOver.value = false;

	try {
		const files = await handleDrop(e);
		if (files.length > 0) {
			fileStore.addFiles(files);
			handleSuccess(`成功添加 ${files.length} 个文件`);
		}
	} catch (error) {
		handleError(error, "拖拽文件失败");
	}
}
</script>
