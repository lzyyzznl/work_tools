<script setup lang="ts">
import { computed } from "vue";
import { useRenameStore } from "../../stores/renameStore";
import { useRenameEngine } from "../../composables/useRenameEngine";
import ReplaceOperation from "./operations/ReplaceOperation.vue";
import AddOperation from "./operations/AddOperation.vue";
import NumberOperation from "./operations/NumberOperation.vue";
import DeleteOperation from "./operations/DeleteOperation.vue";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

const operationTabs = [
	{
		key: "replace",
		label: "字符串替换",
		icon: "🔄",
		component: ReplaceOperation,
	},
	{
		key: "add",
		label: "添加前缀/后缀",
		icon: "➕",
		component: AddOperation,
	},
	{
		key: "number",
		label: "批量添加序号",
		icon: "🔢",
		component: NumberOperation,
	},
	{
		key: "delete",
		label: "删除字符",
		icon: "✂️",
		component: DeleteOperation,
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
