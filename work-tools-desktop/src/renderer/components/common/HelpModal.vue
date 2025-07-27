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
			class="bg-background-primary rounded-radius-lg shadow-2xl w-full max-w-900px max-h-90vh flex flex-col overflow-hidden"
		>
			<!-- 模态框头部 -->
			<div
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-b-1px border-b-border-primary bg-background-secondary"
			>
				<h2
					class="flex items-center gap-spacing-sm m-0 text-xl font-semibold text-text-primary"
				>
					<span class="text-2xl">📚</span>
					帮助文档
				</h2>
				<button
					class="w-32px h-32px border-none bg-none text-text-secondary text-xl cursor-pointer rounded-50% flex items-center justify-center transition-fast hover:bg-background-tertiary hover:text-text-primary"
					@click="closeModal"
				>
					×
				</button>
			</div>

			<!-- 模态框内容 -->
			<div class="flex-1 flex overflow-hidden">
				<!-- 标签页导航 -->
				<div
					class="w-180px bg-background-secondary border-r-1px border-r-border-primary p-spacing-md overflow-y-auto"
				>
					<button
						v-for="section in helpSections"
						:key="section.key"
						class="w-full flex items-center gap-spacing-sm p-spacing-sm p-x-spacing-md border-none bg-none text-text-secondary text-left cursor-pointer rounded-radius-md transition-fast mb-spacing-xs hover:bg-background-tertiary hover:text-text-primary"
						:class="{ 'bg-primary text-white': activeTab === section.key }"
						@click="switchTab(section.key)"
					>
						<span class="text-base">{{ section.icon }}</span>
						<span class="text-sm font-medium">{{ section.title }}</span>
					</button>
				</div>

				<!-- 标签页内容 -->
				<div class="flex-1 overflow-y-auto p-spacing-lg">
					<!-- 概述 -->
					<div v-show="activeTab === 'overview'" class="tab-panel">
						<div class="help-section">
							<h3
								class="m-0 m-b-spacing-md text-lg font-semibold text-text-primary"
							>
								欢迎使用文件重命名工具
							</h3>
							<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
								这是一个强大的批量文件重命名工具，支持多种重命名模式和实时预览功能。
							</p>

							<h4
								class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
							>
								主要特性
							</h4>
							<ul class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary">
								<li class="m-b-spacing-xs leading-1.5">
									🔄 字符串替换 - 查找并替换文件名中的指定文本
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									➕ 添加前缀/后缀 - 在文件名前后添加文本
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									🔢 批量添加序号 - 为文件添加自动递增的序号
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									✂️ 删除字符 - 从文件名中删除指定位置的字符
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									👁️ 实时预览 - 修改参数时自动显示重命名效果
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									↩️ 撤回功能 - 支持撤回最近的重命名操作
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									⌨️ 快捷键支持 - 提供丰富的键盘快捷键
								</li>
							</ul>

							<h4
								class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
							>
								使用流程
							</h4>
							<ol class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary">
								<li class="m-b-spacing-xs leading-1.5">
									选择要重命名的文件或文件夹
								</li>
								<li class="m-b-spacing-xs leading-1.5">
									选择重命名模式（替换、添加、序号、删除）
								</li>
								<li class="m-b-spacing-xs leading-1.5">配置重命名参数</li>
								<li class="m-b-spacing-xs leading-1.5">查看预览效果</li>
								<li class="m-b-spacing-xs leading-1.5">执行重命名操作</li>
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

							<div
								class="m-b-spacing-xl p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									🔄 字符串替换
								</h4>
								<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
									查找文件名中的指定字符串并替换为新的字符串。支持精确匹配，区分大小写。
								</p>
								<div
									class="m-t-spacing-sm p-spacing-sm bg-background-secondary rounded-radius-sm text-sm font-mono text-text-secondary"
								>
									<strong>示例：</strong>将 "IMG_20240115_001.jpg" 中的 "IMG_"
									替换为 "Photo_"<br />
									<strong>结果：</strong>"Photo_20240115_001.jpg"
								</div>
							</div>

							<div
								class="m-b-spacing-xl p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									➕ 添加前缀/后缀
								</h4>
								<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
									在文件名的开头或扩展名之前添加指定的文本内容。
								</p>
								<div
									class="m-t-spacing-sm p-spacing-sm bg-background-secondary rounded-radius-sm text-sm font-mono text-text-secondary"
								>
									<strong>前缀示例：</strong>为 "document.txt" 添加前缀
									"backup_"<br />
									<strong>结果：</strong>"backup_document.txt"<br />
									<strong>后缀示例：</strong>为 "document.txt" 添加后缀 "_v2"<br />
									<strong>结果：</strong>"document_v2.txt"
								</div>
							</div>

							<div
								class="m-b-spacing-xl p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									🔢 批量添加序号
								</h4>
								<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
									为文件添加自动递增的序号，支持自定义起始数字、位数、步长和分隔符。
								</p>
								<div
									class="m-t-spacing-sm p-spacing-sm bg-background-secondary rounded-radius-sm text-sm font-mono text-text-secondary"
								>
									<strong>示例：</strong
									>起始数字1，3位数，步长1，分隔符"_"<br />
									<strong>结果：</strong>"001_document.txt", "002_document.txt",
									"003_document.txt"
								</div>
							</div>

							<div
								class="m-b-spacing-xl p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									✂️ 删除字符
								</h4>
								<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
									从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除。
								</p>
								<div
									class="m-t-spacing-sm p-spacing-sm bg-background-secondary rounded-radius-sm text-sm font-mono text-text-secondary"
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
							<h3
								class="m-0 m-b-spacing-md text-lg font-semibold text-text-primary"
							>
								键盘快捷键
							</h3>
							<p class="m-0 m-b-spacing-md leading-1.6 text-text-secondary">
								使用快捷键可以大大提高操作效率。以下是所有可用的快捷键：
							</p>

							<div class="flex flex-col gap-spacing-sm m-b-spacing-lg">
								<div
									v-for="shortcut in shortcuts"
									:key="shortcut.description"
									class="flex items-center justify-between p-spacing-sm p-x-spacing-md border-1px border-border-secondary rounded-radius-sm bg-background-primary"
								>
									<div
										class="font-mono text-sm font-semibold text-primary bg-background-secondary p-spacing-xs p-x-spacing-sm rounded-radius-sm"
									>
										{{ getShortcutDisplayText(shortcut) }}
									</div>
									<div class="text-sm text-text-secondary">
										{{ shortcut.description }}
									</div>
								</div>
							</div>

							<div
								class="p-spacing-md bg-blue-100 rounded-radius-md border-l-4px border-l-primary"
							>
								<p class="m-0 m-b-spacing-sm font-semibold text-primary">
									<strong>注意：</strong>
								</p>
								<ul class="m-0 text-text-secondary">
									<li class="m-b-spacing-xs leading-1.5">
										快捷键在输入框获得焦点时可能不会生效
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										可以在设置中禁用快捷键功能
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										Escape键可以取消当前操作或关闭对话框
									</li>
								</ul>
							</div>
						</div>
					</div>

					<!-- 使用技巧 -->
					<div v-show="activeTab === 'tips'" class="tab-panel">
						<div class="help-section">
							<h3
								class="m-0 m-b-spacing-md text-lg font-semibold text-text-primary"
							>
								使用技巧
							</h3>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									💡 批量处理技巧
								</h4>
								<ul
									class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary"
								>
									<li class="m-b-spacing-xs leading-1.5">
										使用拖拽功能可以快速添加文件
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										支持同时选择文件和文件夹
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										可以使用Ctrl+A全选所有文件
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										建议在执行前先预览效果
									</li>
								</ul>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									🎯 重命名策略
								</h4>
								<ul
									class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary"
								>
									<li class="m-b-spacing-xs leading-1.5">
										对于大量文件，建议使用序号模式
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										替换模式适合统一修改文件名格式
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										删除模式可以快速清理文件名前缀
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										组合使用多种模式可以实现复杂的重命名需求
									</li>
								</ul>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									⚡ 性能优化
								</h4>
								<ul
									class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary"
								>
									<li class="m-b-spacing-xs leading-1.5">
										处理大量文件时可以关闭自动预览
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										在设置中调整每页显示的文件数量
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										使用虚拟滚动处理超大文件列表
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										定期清理操作历史记录
									</li>
								</ul>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4
									class="m-spacing-lg m-t-0 m-b-spacing-sm text-base font-semibold text-text-primary"
								>
									🔒 安全建议
								</h4>
								<ul
									class="m-0 m-b-spacing-md p-l-spacing-lg text-text-secondary"
								>
									<li class="m-b-spacing-xs leading-1.5">重要文件建议先备份</li>
									<li class="m-b-spacing-xs leading-1.5">
										使用预览功能确认重命名效果
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										利用撤回功能恢复误操作
									</li>
									<li class="m-b-spacing-xs leading-1.5">
										避免使用系统保留字符
									</li>
								</ul>
							</div>
						</div>
					</div>

					<!-- 常见问题 -->
					<div v-show="activeTab === 'faq'" class="tab-panel">
						<div class="help-section">
							<h3
								class="m-0 m-b-spacing-md text-lg font-semibold text-text-primary"
							>
								常见问题
							</h3>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 为什么有些文件无法重命名？
								</h4>
								<p class="m-0 text-text-secondary">
									A:
									可能的原因包括：文件正在被其他程序使用、没有足够的权限、文件名包含非法字符、或者文件被系统保护。
								</p>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 如何撤回重命名操作？
								</h4>
								<p class="m-0 text-text-secondary">
									A:
									点击工具栏中的"撤回"按钮，或使用快捷键Ctrl+Z。注意撤回功能只能恢复最近的操作。
								</p>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 预览显示的结果和实际重命名结果不一致？
								</h4>
								<p class="m-0 text-text-secondary">
									A:
									这可能是由于文件系统限制或文件名冲突导致的。建议检查文件名是否包含非法字符或与现有文件重名。
								</p>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 如何处理大量文件时的性能问题？
								</h4>
								<p class="m-0 text-text-secondary">
									A:
									可以在设置中关闭自动预览、启用虚拟滚动、或减少每页显示的文件数量来提高性能。
								</p>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 支持哪些文件格式？
								</h4>
								<p class="m-0 text-text-secondary">
									A:
									工具支持所有类型的文件和文件夹，重命名操作只修改文件名，不会影响文件内容。
								</p>
							</div>

							<div
								class="m-b-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
							>
								<h4 class="m-0 m-b-spacing-sm text-primary">
									Q: 如何备份和恢复设置？
								</h4>
								<p class="m-0 text-text-secondary">
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
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-t-1px border-t-border-primary bg-background-secondary"
			>
				<div>
					<span class="text-sm text-text-tertiary">版本 1.0.0</span>
				</div>
				<div class="flex gap-spacing-sm">
					<button class="btn btn-primary" @click="closeModal">关闭</button>
				</div>
			</div>
		</div>
	</div>
</template>
