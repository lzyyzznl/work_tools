<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useIndependentRenameEngine } from "../../../composables/useIndependentRenameEngine";
import { useFileRenamerStore } from "../../../stores/fileRenamerStore";
import type { ReplaceParams } from "../../../types/rename";

const renameStore = useRenameStore();
const fileStore = useFileRenamerStore();
const { generatePreview } = useIndependentRenameEngine(fileStore, renameStore);

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
	<div class="replace-operation flex flex-col gap-2">
		<!-- 主要操作行 -->
		<div class="flex flex-col md:flex-row md:items-end gap-2">
			<!-- 主要功能输入区域 -->
			<div class="flex-1 flex flex-col md:flex-row md:items-end gap-2">
				<div class="form-group flex-1 flex flex-col gap-1">
					<input
						id="from-str"
						v-model="fromStr"
						type="text"
						class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						placeholder="查找字符串"
						autocomplete="off"
					/>
				</div>

				<!-- 交换按钮 -->
				<div class="form-actions flex items-center">
					<button
						class="btn btn-sm btn-icon flex items-center justify-center text-lg font-bold px-2 py-1.5 disabled:opacity-50"
						@click="swapParams"
						title="交换查找和替换内容"
						:disabled="!fromStr && !toStr"
					>
						⇄
					</button>
				</div>

				<div class="form-group flex-1 flex flex-col gap-1">
					<input
						id="to-str"
						v-model="toStr"
						type="text"
						class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						placeholder="替换为"
						autocomplete="off"
					/>
				</div>
			</div>

			<!-- 预设管理 -->
			<div class="flex flex-col gap-1 md:w-1/3">
				<div class="flex gap-1">
					<input
						v-model="presetName"
						type="text"
						class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						placeholder="预设名称"
						autocomplete="off"
						style="width: 80px"
					/>
					<select
						v-if="renameStore.presets.filter((p) => p.type === 'replace').length > 0"
						class="form-input px-2 py-2 border border-border-primary rounded-md text-sm bg-white"
						@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
					>
						<option value="">选择</option>
						<option
							v-for="preset in renameStore.presets.filter((p) => p.type === 'replace')"
							:key="preset.id"
							:value="preset.id"
						>
							{{ preset.name }}
						</option>
					</select>
					<button
						class="btn btn-sm px-3 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary/80 disabled:opacity-50"
						@click="savePreset"
						:disabled="!fromStr || !presetName.trim()"
					>
						保存
					</button>
					<button
						class="btn btn-sm px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
						@click="clearParams"
						:disabled="!fromStr && !toStr"
					>
						🗑️ 清空
					</button>
				</div>
			</div>
		</div>

		<!-- 操作按钮行 -->
		<!-- 清空按钮已移至预设管理区域 -->
	</div>
</template>
