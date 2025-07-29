<script setup lang="ts">
import { computed, watch } from "vue";
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

// 预设配置
const presets = [
	{
		label: "标准编号",
		config: { start: 1, digits: 3, step: 1, separator: "_" },
	},
	{
		label: "两位编号",
		config: { start: 1, digits: 2, step: 1, separator: "_" },
	},
	{
		label: "从零开始",
		config: { start: 0, digits: 3, step: 1, separator: "_" },
	},
	{
		label: "间隔编号",
		config: { start: 10, digits: 2, step: 10, separator: "-" },
	},
	{
		label: "无分隔符",
		config: { start: 1, digits: 4, step: 1, separator: "" },
	},
];

function applyPreset(config: any) {
	start.value = config.start;
	digits.value = config.digits;
	step.value = config.step;
	separator.value = config.separator;
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

			<!-- 预设配置 -->
			<div class="flex items-end gap-3">
				<div class="flex-1 flex flex-col gap-1">
					<label class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>快速配置:</label
					>
					<div class="flex flex-wrap gap-1">
						<button
							v-for="preset in presets"
							:key="preset.label"
							class="text-xs py-1 px-2 bg-gray-100 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600 hover:border-blue-500"
							@click="applyPreset(preset.config)"
							:title="`应用: ${preset.label}`"
						>
							{{ preset.label }}
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
