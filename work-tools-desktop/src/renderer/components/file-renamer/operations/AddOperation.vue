<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";
import type { AddParams } from "../../../types/rename";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

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

// 预设名称输入
const presetName = ref("");

function savePreset() {
	if (!text.value) {
		alert("请输入要保存的文本内容");
		return;
	}

	if (!presetName.value.trim()) {
		alert("请输入预设名称");
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
	<div class="add-operation flex flex-col gap-lg">
		<div class="operation-form flex flex-col gap-md">
			<!-- 位置选择 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label class="form-label text-sm font-medium text-text-primary"
						>添加位置:</label
					>
					<div class="radio-group flex gap-md">
						<label
							class="radio-label flex items-center gap-xs cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="isPrefix"
								@change="isPrefix = true"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary"
								>前缀 (文件名前)</span
							>
						</label>
						<label
							class="radio-label flex items-center gap-xs cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="!isPrefix"
								@change="isPrefix = false"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary"
								>后缀 (扩展名前)</span
							>
						</label>
					</div>
				</div>

				<div class="form-actions flex items-center pb-sm">
					<button
						class="btn btn-sm btn-icon w-36px h-36px flex items-center justify-center text-lg font-bold"
						@click="togglePosition"
						title="切换前缀/后缀"
					>
						⇄
					</button>
				</div>
			</div>

			<!-- 文本输入 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label
						for="add-text"
						class="form-label text-sm font-medium text-text-primary"
					>
						{{ isPrefix ? "前缀" : "后缀" }}文本:
					</label>
					<input
						id="add-text"
						v-model="text"
						type="text"
						class="form-input px-md py-sm border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						:placeholder="`输入要添加的${isPrefix ? '前缀' : '后缀'}文本`"
						autocomplete="off"
					/>
				</div>
			</div>

			<!-- 保存预设 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label class="form-label text-sm font-medium text-text-primary"
						>预设管理:</label
					>
					<div class="flex gap-xs">
						<input
							v-model="presetName"
							type="text"
							class="flex-1 form-input px-md py-sm border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
							placeholder="输入预设名称"
							autocomplete="off"
							style="width: 120px"
						/>
						<select
							v-if="
								renameStore.presets.filter((p) => p.type === 'add').length > 0
							"
							class="form-select px-md py-sm border border-border-primary rounded-md text-sm bg-white"
							@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
						>
							<option value="">选择预设</option>
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
							class="btn btn-sm px-md py-xs text-sm bg-primary text-white rounded-md hover:bg-primary/80"
							@click="savePreset"
							:disabled="!text || !presetName.trim()"
						>
							保存
						</button>
					</div>
				</div>
			</div>
			<div class="form-actions-row flex items-center justify-between gap-md">
				<button
					class="btn btn-sm px-md py-xs text-sm"
					@click="clearParams"
					:disabled="!text"
				>
					🗑️ 清空
				</button>

				<div class="form-tips">
					<span class="tip-text text-xs text-text-tertiary">
						💡
						{{ isPrefix ? "前缀会添加到文件名开头" : "后缀会添加到扩展名之前" }}
					</span>
				</div>
			</div>
		</div>

		<!-- 参数验证提示 -->
		<div
			v-if="!text && renameStore.currentMode === 'add'"
			class="validation-message p-sm pl-md bg-orange-100/10 text-orange-500 border border-orange-200/20 rounded-md text-sm"
		>
			⚠️ 请输入要添加的文本内容
		</div>

		<!-- 预览示例 -->
		<div
			v-if="text"
			class="preview-example p-md bg-background-secondary rounded-md border border-border-secondary"
		>
			<h4
				class="example-title m-0 text-sm font-semibold text-text-primary mb-sm"
			>
				预览示例:
			</h4>
			<div class="example-content flex flex-col gap-xs">
				<div class="example-item flex gap-sm text-sm">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>原文件名:</span
					>
					<span class="example-original text-text-tertiary font-mono"
						>document.txt</span
					>
				</div>
				<div class="example-item flex gap-sm text-sm">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>新文件名:</span
					>
					<span class="example-new text-primary font-mono font-medium">
						{{ isPrefix ? `${text}document.txt` : `document${text}.txt` }}
					</span>
				</div>
			</div>
		</div>
	</div>
</template>
