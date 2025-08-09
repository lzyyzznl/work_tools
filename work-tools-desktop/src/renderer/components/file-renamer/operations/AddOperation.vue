<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useIndependentRenameEngine } from "../../../composables/useIndependentRenameEngine";
import { useFileRenamerStore } from "../../../stores/fileRenamerStore";
import type { AddParams } from "../../../types/rename";

const renameStore = useRenameStore();
const fileStore = useFileRenamerStore();
const { generatePreview } = useIndependentRenameEngine(fileStore, renameStore);

const text = computed({
	get: () => renameStore.addParams.text,
	set: (value: string) => {
		renameStore.updateAddParams({ text: value });
	},
});

const isPrefix = computed({
	get: () => renameStore.addParams.isPrefix,
	set: (value: boolean) => {
		renameStore.updateAddParams({ isPrefix: value });
	},
});

// 自动预览监听
watch(
	[text, isPrefix],
	() => {
		if (renameStore.isAutoPreview && renameStore.hasValidParams) {
			generatePreview();
		}
	},
	{ immediate: false }
);

function clearParams() {
	text.value = "";
}

function togglePosition() {
	isPrefix.value = !isPrefix.value;
}

// 记忆操作名称输入
const presetName = ref("");

function savePreset() {
	if (!text.value) {
		alert("请输入要保存的文本内容");
		return;
	}

	if (!presetName.value.trim()) {
		alert("请输入记忆操作名称");
		return;
	}

	renameStore.addPreset({
		name: presetName.value.trim(),
		type: "add",
		params: {
			text: text.value,
			isPrefix: isPrefix.value,
		},
	});

	// 保存后清空输入框
	presetName.value = "";
}
</script>

<template>
	<div class="add-operation flex flex-col gap-2">
		<!-- 主要操作行 -->
		<div class="flex flex-col md:flex-row md:items-end gap-2">
			<!-- 位置选择和文本输入 -->
			<div class="flex-1 flex flex-col md:flex-row md:items-end gap-2">
				<!-- 位置选择 -->
				<div class="form-group flex flex-col gap-1">
					<div class="radio-group flex gap-2">
						<label
							class="radio-label flex items-center gap-1 cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="isPrefix"
								@change="isPrefix = true"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">前缀</span>
						</label>
						<label
							class="radio-label flex items-center gap-1 cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="!isPrefix"
								@change="isPrefix = false"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">后缀</span>
						</label>
					</div>
				</div>

				<!-- 切换按钮 -->
				<div class="form-actions flex items-center">
					<button
						class="btn btn-sm btn-icon flex items-center justify-center text-lg font-bold px-2 py-1.5"
						@click="togglePosition"
						title="切换前缀/后缀"
					>
						⇄
					</button>
				</div>

				<!-- 文本输入 -->
				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>添加内容：</span
						>
						<input
							id="add-text"
							v-model="text"
							type="text"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							:placeholder="`输入${isPrefix ? '前缀' : '后缀'}文本`"
							autocomplete="off"
						/>
					</div>
				</div>
			</div>

			<!-- 预设管理 -->
			<div class="flex flex-col gap-1 md:w-1/3">
				<div class="flex gap-1">
					<input
						v-model="presetName"
						type="text"
						class="flex-1 form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						placeholder="操作名称"
						autocomplete="off"
						style="width: 80px"
					/>
					<select
						v-if="
							renameStore.presets.filter((p) => p.type === 'add').length > 0
						"
						class="form-select px-2 py-2 border border-border-primary rounded-md text-sm bg-white"
						@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
					>
						<option value="">选择操作</option>
						<option
							v-for="preset in renameStore.presets.filter(
								(p) => p.type === 'add'
							)"
							:key="preset.id"
							:value="preset.id"
						>
							{{ preset.name }}
						</option>
					</select>
					<button
						class="btn btn-sm px-3 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary/80"
						@click="savePreset"
						:disabled="!renameStore.hasValidParams || !presetName.trim()"
					>
						记忆操作
					</button>
					<button
						class="btn btn-sm px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
						@click="clearParams"
						:disabled="!text"
					>
						🗑️ 重置
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
