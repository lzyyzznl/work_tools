<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";
import type { ReplaceParams } from "../../../types/rename";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

const fromStr = computed({
	get: () => renameStore.replaceParams.fromStr,
	set: (value: string) => {
		renameStore.updateReplaceParams({ fromStr: value });
	},
});

const toStr = computed({
	get: () => renameStore.replaceParams.toStr,
	set: (value: string) => {
		renameStore.updateReplaceParams({ toStr: value });
	},
});

// 自动预览监听
watch(
	[fromStr, toStr],
	() => {
		if (renameStore.isAutoPreview && renameStore.hasValidParams) {
			generatePreview();
		}
	},
	{ immediate: false }
);

function clearParams() {
	fromStr.value = "";
	toStr.value = "";
}

function swapParams() {
	const temp = fromStr.value;
	fromStr.value = toStr.value;
	toStr.value = temp;
}

// 预设名称输入
const presetName = ref("");

function savePreset() {
	if (!fromStr.value) {
		alert("请输入要查找的字符串");
		return;
	}

	if (!presetName.value.trim()) {
		alert("请输入预设名称");
		return;
	}

	renameStore.addPreset({
		name: presetName.value.trim(),
		type: "replace",
		params: {
			fromStr: fromStr.value,
			toStr: toStr.value,
		},
	});

	// 保存后清空输入框
	presetName.value = "";
}
</script>

<template>
	<div class="flex flex-col gap-4">
		<div class="flex flex-col gap-3">
			<div class="flex items-end gap-3">
				<div class="flex-1 flex flex-col gap-1">
					<label
						for="from-str"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>查找字符串:</label
					>
					<input
						id="from-str"
						v-model="fromStr"
						type="text"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						placeholder="要替换的字符串"
						autocomplete="off"
					/>
				</div>

				<div class="flex items-center pb-2">
					<button
						class="w-9 h-9 flex items-center justify-center text-lg font-bold disabled:opacity-50"
						@click="swapParams"
						title="交换查找和替换内容"
						:disabled="!fromStr && !toStr"
					>
						⇄
					</button>
				</div>

				<div class="flex-1 flex flex-col gap-1">
					<label
						for="to-str"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>替换为:</label
					>
					<input
						id="to-str"
						v-model="toStr"
						type="text"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						placeholder="新的字符串（留空表示删除）"
						autocomplete="off"
					/>
				</div>
			</div>

			<div class="flex items-center justify-between gap-3">
				<button
					class="text-sm py-1 px-2 disabled:opacity-50"
					@click="clearParams"
					:disabled="!fromStr && !toStr"
				>
					🗑️ 清空
				</button>

				<div>
					<span class="text-xs text-gray-400 dark:text-gray-500">
						💡 支持精确匹配，区分大小写
					</span>
				</div>
			</div>

			<!-- 保存预设 -->
			<div class="flex items-end gap-3 mt-3">
				<div class="flex-1 flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>预设管理:</label
					>
					<div class="flex gap-2">
						<input
							v-model="presetName"
							type="text"
							class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
							placeholder="输入预设名称"
							autocomplete="off"
							style="width: 120px"
						/>
						<select
							v-if="
								renameStore.presets.filter((p) => p.type === 'replace').length >
								0
							"
							class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white"
							@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
						>
							<option value="">选择预设</option>
							<option
								v-for="preset in renameStore.presets.filter(
									(p) => p.type === 'replace'
								)"
								:key="preset.id"
								:value="preset.id"
							>
								{{ preset.name }}
							</option>
						</select>
						<button
							class="text-sm py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50"
							@click="savePreset"
							:disabled="!fromStr || !presetName.trim()"
						>
							保存
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- 参数验证提示 -->
		<div
			v-if="fromStr && !renameStore.hasValidParams"
			class="py-2 px-3 bg-orange-100 dark:bg-orange-900 bg-opacity-10 text-orange-500 border border-orange-200 dark:border-orange-800 border-opacity-20 rounded-md text-sm"
		>
			⚠️ 请输入要查找的字符串
		</div>
	</div>
</template>
