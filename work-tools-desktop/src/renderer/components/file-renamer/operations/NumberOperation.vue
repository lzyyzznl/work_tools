<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";
import { useFileStore } from "../../../stores/fileStore";

const renameStore = useRenameStore();
const fileStore = useFileStore();
const { generatePreview } = useRenameEngine();

const start = computed({
	get: () => renameStore.numberParams.start,
	set: (value: number) => {
		renameStore.updateNumberParams({ start: Math.max(0, value) });
	},
});

const digits = computed({
	get: () => renameStore.numberParams.digits,
	set: (value: number) => {
		renameStore.updateNumberParams({
			digits: Math.max(1, Math.min(10, value)),
		});
	},
});

const step = computed({
	get: () => renameStore.numberParams.step,
	set: (value: number) => {
		renameStore.updateNumberParams({ step: Math.max(1, value) });
	},
});

const separator = computed({
	get: () => renameStore.numberParams.separator,
	set: (value: string) => {
		renameStore.updateNumberParams({ separator: value });
	},
});

const isPrefix = computed({
	get: () => renameStore.numberParams.isPrefix,
	set: (value: boolean) => {
		renameStore.updateNumberParams({ isPrefix: value });
	},
});

// 自动预览监听
watch(
	[start, digits, step, separator, isPrefix],
	() => {
		if (renameStore.isAutoPreview && renameStore.hasValidParams) {
			generatePreview();
		}
	},
	{ immediate: false }
);

function resetParams() {
	start.value = 1;
	digits.value = 3;
	step.value = 1;
	separator.value = "_";
	isPrefix.value = true;
}

function togglePosition() {
	isPrefix.value = !isPrefix.value;
}

// 预设名称输入
const presetName = ref("");

function savePreset() {
	if (!presetName.value.trim()) {
		alert("请输入预设名称");
		return;
	}

	renameStore.addPreset({
		name: presetName.value.trim(),
		type: "number",
		params: {
			start: start.value,
			digits: digits.value,
			step: step.value,
			separator: separator.value,
			isPrefix: isPrefix.value,
		},
	});

	// 保存后清空输入框
	presetName.value = "";
}

// 计算预览范围
const previewNumbers = computed(() => {
	const count = Math.min(fileStore.files.length, 5);
	const numbers = [];
	for (let i = 0; i < count; i++) {
		const num = start.value + i * step.value;
		numbers.push(num.toString().padStart(digits.value, "0"));
	}
	return numbers;
});
</script>

<template>
	<div class="flex flex-col gap-4">
		<div class="flex flex-col gap-3">
			<!-- 位置选择 -->
			<div class="flex items-end gap-3">
				<div class="flex-1 flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>序号位置:</label
					>
					<div class="flex gap-3">
						<label class="flex items-center gap-1 cursor-pointer select-none">
							<input
								type="radio"
								:checked="isPrefix"
								@change="isPrefix = true"
								class="m-0"
							/>
							<span class="text-sm text-gray-800 dark:text-gray-200">前缀</span>
						</label>
						<label class="flex items-center gap-1 cursor-pointer select-none">
							<input
								type="radio"
								:checked="!isPrefix"
								@change="isPrefix = false"
								class="m-0"
							/>
							<span class="text-sm text-gray-800 dark:text-gray-200">后缀</span>
						</label>
					</div>
				</div>

				<div class="flex items-center pb-2">
					<button
						class="w-9 h-9 flex items-center justify-center text-lg font-bold"
						@click="togglePosition"
						title="切换前缀/后缀"
					>
						⇄
					</button>
				</div>
			</div>

			<!-- 数字参数 -->
			<div class="flex items-end gap-3">
				<div class="flex-1 flex flex-col gap-1">
					<label
						for="start-number"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>起始数字:</label
					>
					<input
						id="start-number"
						v-model.number="start"
						type="number"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						min="0"
						max="9999"
						step="1"
					/>
				</div>

				<div class="flex-1 flex flex-col gap-1">
					<label
						for="digits"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>数字位数:</label
					>
					<input
						id="digits"
						v-model.number="digits"
						type="number"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						min="1"
						max="10"
						step="1"
					/>
				</div>

				<div class="flex-1 flex flex-col gap-1">
					<label
						for="step"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>步长:</label
					>
					<input
						id="step"
						v-model.number="step"
						type="number"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						min="1"
						max="100"
						step="1"
					/>
				</div>

				<div class="flex-1 flex flex-col gap-1">
					<label
						for="separator"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>分隔符:</label
					>
					<input
						id="separator"
						v-model="separator"
						type="text"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						placeholder="如: _ - ."
						maxlength="3"
					/>
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
								renameStore.presets.filter((p) => p.type === 'number').length >
								0
							"
							class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm bg-white"
							@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
						>
							<option value="">选择预设</option>
							<option
								v-for="preset in renameStore.presets.filter(
									(p) => p.type === 'number'
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
							:disabled="!presetName.trim()"
						>
							保存
						</button>
					</div>
				</div>
			</div>

			<div class="flex items-center justify-between gap-3">
				<button class="text-sm py-1 px-2" @click="resetParams">🔄 重置</button>

				<div>
					<span class="text-xs text-gray-400 dark:text-gray-500">
						💡 序号会按文件在列表中的顺序分配
					</span>
				</div>
			</div>
		</div>

		<!-- 序号预览 -->
		<div
			v-if="previewNumbers.length > 0"
			class="p-3 bg-gray-100 dark:bg-gray-700 rounded-md border border-gray-300 dark:border-gray-600"
		>
			<h4 class="mb-1 text-sm font-semibold text-gray-800 dark:text-gray-200">
				序号预览:
			</h4>
			<div>
				<div class="flex flex-wrap gap-1 items-center">
					<span
						v-for="(number, index) in previewNumbers"
						:key="index"
						class="py-1 px-2 bg-blue-500 text-white rounded-sm font-mono text-xs font-medium"
					>
						{{ isPrefix ? `${number}${separator}` : `${separator}${number}` }}
					</span>
					<span
						v-if="fileStore.files.length > 5"
						class="text-gray-400 dark:text-gray-500 text-xs italic"
					>
						... (共 {{ fileStore.files.length }} 个文件)
					</span>
				</div>
			</div>
		</div>
	</div>
</template>
