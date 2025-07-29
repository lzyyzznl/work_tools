<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRenameStore } from "../../stores/renameStore";
import { useRenameEngine } from "../../composables/useRenameEngine";
import ReplaceOperation from "./operations/ReplaceOperation.vue";
import AddOperation from "./operations/AddOperation.vue";
import NumberOperation from "./operations/NumberOperation.vue";
import DeleteOperation from "./operations/DeleteOperation.vue";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

// 帮助模态框控制
const showHelp = ref({
	replace: false,
	add: false,
	number: false,
	delete: false,
});

function toggleHelp(tabKey: string) {
	showHelp.value[tabKey as keyof typeof showHelp.value] =
		!showHelp.value[tabKey as keyof typeof showHelp.value];
}

const operationTabs = [
	{
		key: "replace",
		label: "字符串替换",
		icon: "🔄",
		component: ReplaceOperation,
		helpTitle: "字符串替换说明",
		helpContent:
			"将文件名中的指定字符串替换为新的字符串。支持精确匹配，区分大小写。",
		helpExamples: [
			{ label: "删除前缀", content: '查找 "IMG_" → 替换为 ""' },
			{ label: "替换分隔符", content: '查找 "_" → 替换为 "-"' },
			{ label: "修改扩展名", content: '查找 ".txt" → 替换为 ".md"' },
		],
	},
	{
		key: "add",
		label: "添加前缀/后缀",
		icon: "➕",
		component: AddOperation,
		helpTitle: "添加前缀/后缀说明",
		helpContent: "在文件名的开头或扩展名之前添加指定的文本内容。",
		helpExamples: [
			{ label: "日期前缀", content: '"2024-01-15_" → 2024-01-15_document.txt' },
			{ label: "备份后缀", content: '"_backup" → document_backup.txt' },
			{ label: "版本标记", content: '"_v2" → document_v2.txt' },
		],
	},
	{
		key: "number",
		label: "批量添加序号",
		icon: "🔢",
		component: NumberOperation,
		helpTitle: "批量添加序号说明",
		helpContent:
			"为文件名添加自动递增的序号，支持自定义起始数字、位数、步长和分隔符。",
		helpExamples: [
			{
				label: "标准编号",
				content:
					'起始数字1，3位数，步长1，分隔符"_" → "001_document.txt", "002_document.txt", "003_document.txt"',
			},
			{
				label: "从10开始",
				content:
					'起始数字10，2位数，步长1，分隔符"_" → "10_document.txt", "11_document.txt", "12_document.txt"',
			},
			{
				label: "步长为5",
				content:
					'起始数字1，3位数，步长5，分隔符"_" → "001_document.txt", "006_document.txt", "011_document.txt"',
			},
			{
				label: "后缀模式",
				content:
					'起始数字1，3位数，步长1，分隔符"_"，后缀模式 → "document_001.txt", "document_002.txt", "document_003.txt"',
			},
		],
	},
	{
		key: "delete",
		label: "删除字符",
		icon: "✂️",
		component: DeleteOperation,
		helpTitle: "删除字符说明",
		helpContent: "从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除。",
		helpExamples: [
			{ label: "删除前缀", content: '位置1，删除4个 → "IMG_" 被删除' },
			{ label: "删除后缀", content: "从右数位置1，删除3个 → 删除末尾字符" },
			{ label: "删除中间", content: "位置5，删除8个 → 删除日期部分" },
		],
	},
];

const currentTab = computed({
	get: () => renameStore.currentMode,
	set: (value) => {
		renameStore.setMode(value);
		if (renameStore.isAutoPreview) {
			generatePreview();
		}
	},
});

const currentComponent = computed(() => {
	const tab = operationTabs.find((t) => t.key === currentTab.value);
	return tab?.component || ReplaceOperation;
});
</script>

<template>
	<div
		class="rename-operation-tabs flex flex-col bg-background-tertiary border-b border-border-primary"
	>
		<!-- 标签页导航 -->
		<div class="tab-nav flex px-lg pt-sm gap-xs overflow-x-auto">
			<button
				v-for="tab in operationTabs"
				:key="tab.key"
				:class="[
					'tab-button flex items-center gap-xs px-md py-sm border-none rounded-t-md text-sm font-medium transition-all duration-150 whitespace-nowrap',
					currentTab === tab.key
						? 'bg-primary text-white font-semibold'
						: 'bg-background-secondary text-text-secondary hover:bg-background-primary hover:text-text-primary',
				]"
				@click="currentTab = tab.key as any"
			>
				<span class="tab-icon text-base">{{ tab.icon }}</span>
				<span class="tab-label text-sm">{{ tab.label }}</span>
			</button>
		</div>

		<!-- 标签页内容 -->
		<div class="tab-content bg-background-primary p-lg min-h-120px">
			<component :is="currentComponent" />
		</div>

		<!-- 预览控制 -->
		<div
			class="preview-controls flex items-center gap-md px-lg py-sm bg-background-secondary border-t border-border-secondary text-sm"
		>
			<label
				class="checkbox-label flex items-center gap-xs cursor-pointer select-none"
			>
				<input
					type="checkbox"
					v-model="renameStore.isAutoPreview"
					class="checkbox m-0 rounded border-border-primary text-primary focus:ring-primary"
				/>
				<span class="checkbox-text text-text-primary font-medium"
					>自动预览</span
				>
			</label>

			<button
				v-if="!renameStore.isAutoPreview"
				class="btn btn-sm btn-secondary px-md py-xs text-sm"
				@click="generatePreview"
				:disabled="!renameStore.hasValidParams"
			>
				🔄 手动预览
			</button>

			<div class="preview-info ml-auto">
				<span
					v-if="renameStore.previewUpdateTime"
					class="preview-time text-text-tertiary text-xs"
				>
					上次预览:
					{{ new Date(renameStore.previewUpdateTime).toLocaleTimeString() }}
				</span>
			</div>
		</div>
	</div>
</template>
