<script setup lang="ts">
import { computed, watch, ref } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useIndependentRenameEngine } from "../../../composables/useIndependentRenameEngine";
import { useFileRenamerStore } from "../../../stores/fileRenamerStore";

const renameStore = useRenameStore();
const fileStore = useFileRenamerStore();
const { generatePreview } = useIndependentRenameEngine(fileStore, renameStore);

const startPos = computed({
	get: () => renameStore.deleteParams.startPos,
	set: (value: number) => {
		renameStore.updateDeleteParams({ startPos: Math.max(1, value) });
	},
});

const count = computed({
	get: () => renameStore.deleteParams.count,
	set: (value: number) => {
		renameStore.updateDeleteParams({ count: Math.max(1, value) });
	},
});

const fromLeft = computed({
	get: () => renameStore.deleteParams.fromLeft,
	set: (value: boolean) => {
		renameStore.updateDeleteParams({ fromLeft: value });
	},
});

// 自动预览监听
watch(
	[startPos, count, fromLeft],
	() => {
		if (renameStore.isAutoPreview && renameStore.hasValidParams) {
			generatePreview();
		}
	},
	{ immediate: false }
);

function resetParams() {
	startPos.value = 1;
	count.value = 1;
	fromLeft.value = true;
}

function toggleDirection() {
	fromLeft.value = !fromLeft.value;
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
		type: "delete",
		params: {
			startPos: startPos.value,
			count: count.value,
			fromLeft: fromLeft.value,
		},
	});

	// 保存后清空输入框
	presetName.value = "";
}

// 生成示例预览
function generateExample(originalName: string): string {
	const nameWithoutExt = originalName.includes(".")
		? originalName.substring(0, originalName.lastIndexOf("."))
		: originalName;
	const ext = originalName.includes(".")
		? originalName.substring(originalName.lastIndexOf("."))
		: "";

	let result = nameWithoutExt;
	const startIndex = startPos.value - 1;

	if (fromLeft.value) {
		// 从左侧删除
		if (startIndex < result.length) {
			const endIndex = Math.min(startIndex + count.value, result.length);
			result = result.slice(0, startIndex) + result.slice(endIndex);
		}
	} else {
		// 从右侧删除
		const rightStartIndex = Math.max(
			0,
			result.length - startIndex - count.value + 1
		);
		const rightEndIndex = Math.max(0, result.length - startIndex + 1);
		result = result.slice(0, rightStartIndex) + result.slice(rightEndIndex);
	}

	return result + ext;
}
</script>
<template>
	<div class="delete-operation flex flex-col gap-2">
		<!-- 主要操作行 -->
		<div class="flex flex-col md:flex-row md:items-end gap-2">
			<!-- 删除方向和删除参数 -->
			<div class="flex-1 flex flex-col md:flex-row md:items-end gap-2">
				<!-- 删除方向 -->
				<div class="form-group flex flex-col gap-1">
					<div class="radio-group flex gap-2">
						<label
							class="radio-label flex items-center gap-1 cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="fromLeft"
								@change="fromLeft = true"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">左侧</span>
						</label>
						<label
							class="radio-label flex items-center gap-1 cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="!fromLeft"
								@change="fromLeft = false"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">右侧</span>
						</label>
					</div>
				</div>

				<!-- 切换按钮 -->
				<div class="form-actions flex items-center">
					<button
						class="btn btn-sm btn-icon flex items-center justify-center text-lg font-bold px-2 py-1.5"
						@click="toggleDirection"
						title="切换删除方向"
					>
						⇄
					</button>
				</div>

				<!-- 删除参数 -->
				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>起始位置：</span
						>
						<input
							id="start-pos"
							v-model.number="startPos"
							type="number"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							min="1"
							max="50"
							step="1"
							:placeholder="fromLeft ? '开始位置' : '从右数位置'"
						/>
					</div>
				</div>

				<div class="form-group flex-1 flex flex-col gap-1">
					<div class="flex items-center gap-2">
						<span
							class="text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap"
							>删除字符数：</span
						>
						<input
							id="delete-count"
							v-model.number="count"
							type="number"
							class="form-input px-3 py-2 border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1) flex-1"
							min="1"
							max="20"
							step="1"
							placeholder="删除字符数"
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
							renameStore.presets.filter((p) => p.type === 'delete').length > 0
						"
						class="form-input px-2 py-2 border border-border-primary rounded-md text-sm bg-white"
						@change="e => renameStore.applyPreset((e.target as HTMLSelectElement).value)"
					>
						<option value="">选择</option>
						<option
							v-for="preset in renameStore.presets.filter(
								(p) => p.type === 'delete'
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
