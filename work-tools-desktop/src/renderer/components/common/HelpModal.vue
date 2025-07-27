<script setup lang="ts">
import { ref, computed } from "vue";
import { useKeyboardShortcuts } from "../../composables/useKeyboardShortcuts";

interface Props {
	modelValue: boolean;
}

interface Emits {
	(e: "update:modelValue", value: boolean): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const { getShortcuts, getShortcutDisplayText } = useKeyboardShortcuts();

const activeTab = ref("overview");

const isVisible = computed({
	get: () => props.modelValue,
	set: (value: boolean) => emit("update:modelValue", value),
});

const shortcuts = computed(() => getShortcuts());

function closeModal() {
	isVisible.value = false;
}

function switchTab(tabKey: string) {
	activeTab.value = tabKey;
}

const helpSections = [
	{
		key: "overview",
		title: "概述",
		icon: "📖",
	},
	{
		key: "features",
		title: "功能介绍",
		icon: "✨",
	},
	{
		key: "shortcuts",
		title: "快捷键",
		icon: "⌨️",
	},
	{
		key: "tips",
		title: "使用技巧",
		icon: "💡",
	},
	{
		key: "faq",
		title: "常见问题",
		icon: "❓",
	},
];
</script>

<template>
	<div
		v-if="isVisible"
		class="fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-1000 p-spacing-lg"
		@click="closeModal"
	>
		<div
			class="bg-white rounded-lg shadow-xl w-full max-w-900px max-h-90vh flex flex-col overflow-hidden"
		>
			<!-- 模态框头部 -->
			<div
				class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white"
			>
				<h2 class="flex items-center gap-3 m-0 text-xl font-bold text-gray-900">
					<span class="text-2xl">📚</span>
					帮助文档
				</h2>
				<button
					class="w-8 h-8 border-none bg-none text-gray-500 text-xl cursor-pointer rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 hover:text-gray-700"
					@click="closeModal"
				>
					×
				</button>
			</div>

			<!-- 模态框内容 -->
			<div class="flex-1 flex overflow-hidden">
				<!-- 标签页导航 -->
				<div class="w-45 bg-white border-r border-gray-200 p-3 overflow-y-auto">
					<button
						v-for="section in helpSections"
						:key="section.key"
						class="w-full flex items-center gap-3 px-4 py-3 border-none bg-none text-gray-600 text-left cursor-pointer rounded-md transition-colors mb-1 hover:bg-gray-100 hover:text-gray-900"
						:class="{
							'bg-blue-50 text-blue-600 font-medium': activeTab === section.key,
						}"
						@click.stop="switchTab(section.key)"
					>
						<span class="text-base">{{ section.icon }}</span>
						<span class="text-sm">{{ section.title }}</span>
					</button>
				</div>

				<!-- 标签页内容 -->
				<div class="flex-1 overflow-y-auto p-6">
					<!-- 概述 -->
					<div v-show="activeTab === 'overview'" class="tab-panel">
						<div class="help-section">
							<h3 class="m-0 mb-4 text-lg font-semibold text-gray-900">
								欢迎使用文件重命名工具
							</h3>
							<p class="m-0 mb-4 leading-6 text-gray-600">
								这是一个强大的批量文件重命名工具，支持多种重命名模式和实时预览功能。
							</p>

							<h4 class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900">
								主要特性
							</h4>
							<ul class="m-0 mb-4 pl-5 text-gray-600">
								<li class="mb-1 leading-6">
									🔄 字符串替换 - 查找并替换文件名中的指定文本
								</li>
								<li class="m-b-spacing-xs leading-6">
									➕ 添加前缀/后缀 - 在文件名前后添加文本
								</li>
								<li class="m-b-spacing-xs leading-6">
									🔢 批量添加序号 - 为文件添加自动递增的序号
								</li>
								<li class="m-b-spacing-xs leading-6">
									✂️ 删除字符 - 从文件名中删除指定位置的字符
								</li>
								<li class="m-b-spacing-xs leading-6">
									👁️ 实时预览 - 修改参数时自动显示重命名效果
								</li>
								<li class="m-b-spacing-xs leading-6">
									↩️ 撤回功能 - 支持撤回最近的重命名操作
								</li>
								<li class="m-b-spacing-xs leading-6">
									⌨️ 快捷键支持 - 提供丰富的键盘快捷键
								</li>
							</ul>

							<h4 class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900">
								使用流程
							</h4>
							<ol class="m-0 mb-4 pl-5 text-gray-600">
								<li class="mb-1 leading-6">选择要重命名的文件或文件夹</li>
								<li class="m-b-spacing-xs leading-6">
									选择重命名模式（替换、添加、序号、删除）
								</li>
								<li class="m-b-spacing-xs leading-6">配置重命名参数</li>
								<li class="m-b-spacing-xs leading-6">查看预览效果</li>
								<li class="m-b-spacing-xs leading-6">执行重命名操作</li>
							</ol>
						</div>
					</div>

					<!-- 功能介绍 -->
					<div v-show="activeTab === 'features'" class="tab-panel">
						<div class="help-section">
							<h3
								class="m-0 m-b-spacing-md text-lg font-semibold text-text-primary"
							>
								功能详细介绍
							</h3>

							<div class="mb-8 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									🔄 字符串替换
								</h4>
								<p class="m-0 mb-4 leading-6 text-gray-600">
									查找文件名中的指定字符串并替换为新的字符串。支持精确匹配，区分大小写。
								</p>
								<div
									class="mt-2 p-3 bg-gray-50 rounded-sm text-sm font-mono text-gray-600"
								>
									<strong>示例：</strong>将 "IMG_20240115_001.jpg" 中的 "IMG_"
									替换为 "Photo_"<br />
									<strong>结果：</strong>"Photo_20240115_001.jpg"
								</div>
							</div>

							<div class="mb-8 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									➕ 添加前缀/后缀
								</h4>
								<p class="m-0 mb-4 leading-6 text-gray-600">
									在文件名的开头或扩展名之前添加指定的文本内容。
								</p>
								<div
									class="mt-2 p-3 bg-gray-50 rounded-sm text-sm font-mono text-gray-600"
								>
									<strong>前缀示例：</strong>为 "document.txt" 添加前缀
									"backup_"<br />
									<strong>结果：</strong>"backup_document.txt"<br />
									<strong>后缀示例：</strong>为 "document.txt" 添加后缀 "_v2"<br />
									<strong>结果：</strong>"document_v2.txt"
								</div>
							</div>

							<div class="mb-8 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									🔢 批量添加序号
								</h4>
								<p class="m-0 mb-4 leading-6 text-gray-600">
									为文件添加自动递增的序号，支持自定义起始数字、位数、步长和分隔符。
								</p>
								<div
									class="mt-2 p-3 bg-gray-50 rounded-sm text-sm font-mono text-gray-600"
								>
									<strong>示例：</strong
									>起始数字1，3位数，步长1，分隔符"_"<br />
									<strong>结果：</strong>"001_document.txt", "002_document.txt",
									"003_document.txt"
								</div>
							</div>

							<div class="mb-8 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									✂️ 删除字符
								</h4>
								<p class="m-0 mb-4 leading-6 text-gray-600">
									从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除。
								</p>
								<div
									class="mt-2 p-3 bg-gray-50 rounded-sm text-sm font-mono text-gray-600"
								>
									<strong>示例：</strong>从左侧第1个位置删除4个字符<br />
									<strong>原文件：</strong>"IMG_document.txt"<br />
									<strong>结果：</strong>"document.txt"
								</div>
							</div>
						</div>
					</div>

					<!-- 快捷键 -->
					<div v-show="activeTab === 'shortcuts'" class="tab-panel">
						<div class="help-section">
							<h3 class="m-0 mb-4 text-lg font-semibold text-gray-900">
								键盘快捷键
							</h3>
							<p class="m-0 mb-4 leading-6 text-gray-600">
								使用快捷键可以大大提高操作效率。以下是所有可用的快捷键：
							</p>

							<div class="flex flex-col gap-2 mb-6">
								<div
									v-for="shortcut in shortcuts"
									:key="shortcut.description"
									class="flex items-center justify-between px-4 py-3 border border-gray-200 rounded-sm bg-white"
								>
									<div
										class="font-mono text-sm font-semibold text-blue-600 bg-gray-50 px-3 py-1 rounded-sm"
									>
										{{ getShortcutDisplayText(shortcut) }}
									</div>
									<div class="text-sm text-gray-600">
										{{ shortcut.description }}
									</div>
								</div>
							</div>

							<div
								class="p-4 bg-blue-50 rounded-md border-l-4 border-l-blue-500"
							>
								<p class="m-0 mb-2 font-semibold text-blue-700">
									<strong>注意：</strong>
								</p>
								<ul class="m-0 text-gray-600">
									<li class="mb-1 leading-6">
										快捷键在输入框获得焦点时可能不会生效
									</li>
									<li class="m-b-spacing-xs leading-6">
										可以在设置中禁用快捷键功能
									</li>
									<li class="m-b-spacing-xs leading-6">
										Escape键可以取消当前操作或关闭对话框
									</li>
								</ul>
							</div>
						</div>
					</div>

					<!-- 使用技巧 -->
					<div v-show="activeTab === 'tips'" class="tab-panel">
						<div class="help-section">
							<h3 class="m-0 mb-4 text-lg font-semibold text-gray-900">
								使用技巧
							</h3>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									💡 批量处理技巧
								</h4>
								<ul class="m-0 mb-4 pl-5 text-gray-600">
									<li class="mb-1 leading-6">使用拖拽功能可以快速添加文件</li>
									<li class="m-b-spacing-xs leading-6">
										支持同时选择文件和文件夹
									</li>
									<li class="m-b-spacing-xs leading-6">
										可以使用Ctrl+A全选所有文件
									</li>
									<li class="m-b-spacing-xs leading-6">
										建议在执行前先预览效果
									</li>
								</ul>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									🎯 重命名策略
								</h4>
								<ul class="m-0 mb-4 pl-5 text-gray-600">
									<li class="mb-1 leading-6">对于大量文件，建议使用序号模式</li>
									<li class="m-b-spacing-xs leading-6">
										替换模式适合统一修改文件名格式
									</li>
									<li class="m-b-spacing-xs leading-6">
										删除模式可以快速清理文件名前缀
									</li>
									<li class="m-b-spacing-xs leading-6">
										组合使用多种模式可以实现复杂的重命名需求
									</li>
								</ul>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									⚡ 性能优化
								</h4>
								<ul class="m-0 mb-4 pl-5 text-gray-600">
									<li class="mb-1 leading-6">处理大量文件时可以关闭自动预览</li>
									<li class="m-b-spacing-xs leading-6">
										在设置中调整每页显示的文件数量
									</li>
									<li class="m-b-spacing-xs leading-6">
										使用虚拟滚动处理超大文件列表
									</li>
									<li class="m-b-spacing-xs leading-6">定期清理操作历史记录</li>
								</ul>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4
									class="m-6 m-t-0 mb-2 text-base font-semibold text-gray-900"
								>
									🔒 安全建议
								</h4>
								<ul class="m-0 mb-4 pl-5 text-gray-600">
									<li class="mb-1 leading-6">重要文件建议先备份</li>
									<li class="m-b-spacing-xs leading-6">
										使用预览功能确认重命名效果
									</li>
									<li class="m-b-spacing-xs leading-6">
										利用撤回功能恢复误操作
									</li>
									<li class="m-b-spacing-xs leading-6">避免使用系统保留字符</li>
								</ul>
							</div>
						</div>
					</div>

					<!-- 常见问题 -->
					<div v-show="activeTab === 'faq'" class="tab-panel">
						<div class="help-section">
							<h3 class="m-0 mb-4 text-lg font-semibold text-gray-900">
								常见问题
							</h3>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">
									Q: 为什么有些文件无法重命名？
								</h4>
								<p class="m-0 text-gray-600">
									A:
									可能的原因包括：文件正在被其他程序使用、没有足够的权限、文件名包含非法字符、或者文件被系统保护。
								</p>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">Q: 如何撤回重命名操作？</h4>
								<p class="m-0 text-gray-600">
									A:
									点击工具栏中的"撤回"按钮，或使用快捷键Ctrl+Z。注意撤回功能只能恢复最近的操作。
								</p>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">
									Q: 预览显示的结果和实际重命名结果不一致？
								</h4>
								<p class="m-0 text-gray-600">
									A:
									这可能是由于文件系统限制或文件名冲突导致的。建议检查文件名是否包含非法字符或与现有文件重名。
								</p>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">
									Q: 如何处理大量文件时的性能问题？
								</h4>
								<p class="m-0 text-gray-600">
									A:
									可以在设置中关闭自动预览、启用虚拟滚动、或减少每页显示的文件数量来提高性能。
								</p>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">Q: 支持哪些文件格式？</h4>
								<p class="m-0 text-gray-600">
									A:
									工具支持所有类型的文件和文件夹，重命名操作只修改文件名，不会影响文件内容。
								</p>
							</div>

							<div class="mb-6 p-4 border border-gray-200 rounded-md bg-white">
								<h4 class="m-0 mb-2 text-blue-700">Q: 如何备份和恢复设置？</h4>
								<p class="m-0 text-gray-600">
									A:
									在设置页面中可以导出当前设置到JSON文件，也可以从文件导入之前保存的设置。
								</p>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- 模态框底部 -->
			<div
				class="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-white"
			>
				<div>
					<span class="text-sm text-gray-400">版本 1.0.0</span>
				</div>
				<div class="flex gap-2">
					<button
						class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
						@click="closeModal"
					>
						关闭
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
