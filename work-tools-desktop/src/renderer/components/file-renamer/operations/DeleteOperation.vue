<script setup lang="ts">
import { computed, watch } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

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

// 预设配置
const presets = [
	{ label: "删除首字符", config: { startPos: 1, count: 1, fromLeft: true } },
	{ label: "删除前3字符", config: { startPos: 1, count: 3, fromLeft: true } },
	{ label: "删除末字符", config: { startPos: 1, count: 1, fromLeft: false } },
	{ label: "删除后3字符", config: { startPos: 1, count: 3, fromLeft: false } },
	{ label: "删除中间字符", config: { startPos: 3, count: 2, fromLeft: true } },
];

function applyPreset(config: any) {
	startPos.value = config.startPos;
	count.value = config.count;
	fromLeft.value = config.fromLeft;
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
	<div class="delete-operation flex flex-col gap-lg">
		<div class="operation-form flex flex-col gap-md">
			<!-- 删除方向 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label class="form-label text-sm font-medium text-text-primary"
						>删除方向:</label
					>
					<div class="radio-group flex gap-md">
						<label
							class="radio-label flex items-center gap-xs cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="fromLeft"
								@change="fromLeft = true"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">从左侧</span>
						</label>
						<label
							class="radio-label flex items-center gap-xs cursor-pointer select-none"
						>
							<input
								type="radio"
								:checked="!fromLeft"
								@change="fromLeft = false"
								class="radio-input m-0"
							/>
							<span class="radio-text text-sm text-text-primary">从右侧</span>
						</label>
					</div>
				</div>

				<div class="form-actions flex items-center pb-sm">
					<button
						class="btn btn-sm btn-icon w-36px h-36px flex items-center justify-center text-lg font-bold"
						@click="toggleDirection"
						title="切换删除方向"
					>
						⇄
					</button>
				</div>
			</div>

			<!-- 删除参数 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label
						for="start-pos"
						class="form-label text-sm font-medium text-text-primary"
					>
						{{ fromLeft ? "开始位置:" : "从右数位置:" }}
					</label>
					<input
						id="start-pos"
						v-model.number="startPos"
						type="number"
						class="form-input px-md py-sm border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						min="1"
						max="50"
						step="1"
					/>
					<span class="form-hint text-xs text-text-tertiary">
						{{ fromLeft ? "第几个字符开始删除" : "从右数第几个位置" }}
					</span>
				</div>

				<div class="form-group flex-1 flex flex-col gap-xs">
					<label
						for="delete-count"
						class="form-label text-sm font-medium text-text-primary"
						>删除字符数:</label
					>
					<input
						id="delete-count"
						v-model.number="count"
						type="number"
						class="form-input px-md py-sm border border-border-primary rounded-md text-sm transition-border-color duration-150 focus:outline-none focus:border-primary focus:shadow-0_0_0_2px_rgba(0,122,255,0.1)"
						min="1"
						max="20"
						step="1"
					/>
					<span class="form-hint text-xs text-text-tertiary"
						>要删除的字符数量</span
					>
				</div>
			</div>

			<!-- 预设配置 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label class="form-label text-sm font-medium text-text-primary"
						>快速配置:</label
					>
					<div class="preset-buttons flex flex-wrap gap-xs">
						<button
							v-for="preset in presets"
							:key="preset.label"
							class="btn btn-sm btn-preset text-xs px-xs py-sm bg-background-secondary border border-border-secondary hover:bg-background-tertiary hover:border-primary"
							@click="applyPreset(preset.config)"
							:title="`应用: ${preset.label}`"
						>
							{{ preset.label }}
						</button>
					</div>
				</div>
			</div>

			<div class="form-actions-row flex items-center justify-between gap-md">
				<button class="btn btn-sm px-md py-xs text-sm" @click="resetParams">
					🔄 重置
				</button>

				<div class="form-tips">
					<span class="tip-text text-xs text-text-tertiary">
						💡
						{{
							fromLeft ? "从左侧计算位置" : "从右侧计算位置"
						}}，只处理文件名部分
					</span>
				</div>
			</div>
		</div>
	</div>
</template>
