<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useIndependentRenameEngine } from "../../../composables/useIndependentRenameEngine";
import { useFileRenamerStore } from "../../../stores/fileRenamerStore";

const renameStore = useRenameStore();
const fileStore = useFileRenamerStore();
const { generatePreview } = useIndependentRenameEngine(fileStore, renameStore);

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
	<div class="number-operation flex flex-col gap-2">
		<!-- 主要操作行 -->
		<div class="flex flex-col md:flex-row md:items-end gap-2">
			<!-- 位置选择和数字参数 -->
			<div class="flex-1 flex flex-col md:flex-row md:items-end gap-2">
				<!-- 位置选择 -->
				<div class="form-group flex flex-col gap-1">
					<div class="flex gap-2">
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

				<!-- 数字参数 -->
				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>起始数字：</span
						>
						<input
							id="start-number"
							v-model.number="start"
							type="number"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							min="0"
							max="9999"
							step="1"
							placeholder="起始"
						/>
					</div>
				</div>

				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>位数：</span
						>
						<input
							id="digits"
							v-model.number="digits"
							type="number"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							min="1"
							max="10"
							step="1"
							placeholder="位数"
						/>
					</div>
				</div>

				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>步长：</span
						>
						<input
							id="step"
							v-model.number="step"
							type="number"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							min="1"
							max="100"
							step="1"
							placeholder="步长"
						/>
					</div>
				</div>

				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>分隔符：</span
						>
						<input
							id="separator"
							v-model="separator"
							type="text"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							placeholder="分隔符"
							maxlength="3"
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
						class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						placeholder="预设名称"
						autocomplete="off"
						style="width: 80px"
					/>
					<select
						v-if="
							renameStore.presets.filter((p) => p.type === 'number').length > 0
						"
						class="form-input px-2 py-2 border border-border-primary rounded-md text-sm bg-white"
						@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
					>
						<option value="">选择</option>
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
						class="btn btn-sm px-3 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary/80"
						@click="savePreset"
						:disabled="!renameStore.hasValidParams || !presetName.trim()"
					>
						记忆操作
					</button>
					<button
						class="btn btn-sm px-3 py-2 text-sm bg-red-500 text-white rounded-md hover:bg-red-600"
						@click="resetParams"
					>
						🔄 重置
					</button>
				</div>
			</div>
		</div>

		<!-- 操作按钮行 -->
		<!-- 重置按钮已移至预设管理区域 -->
	</div>
</template>
