<script setup lang="ts">
import { ref, computed, watch } from "vue";
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

// 帮助模态框控制
const showHelp = ref(false);

function toggleHelp() {
	showHelp.value = !showHelp.value;
}
</script>
<template>
	<div class="delete-operation flex flex-col gap-lg">
		<div class="operation-header">
			<h3
				class="operation-title flex items-center gap-sm m-0 text-lg font-semibold text-text-primary"
			>
				<span class="operation-icon text-xl">✂️</span>
				删除字符
			</h3>
			<button
				class="help-button bg-none border-none text-lg cursor-pointer text-text-secondary ml-auto p-xs rounded-md hover:bg-background-secondary hover:text-primary"
				title="查看帮助"
				@click="toggleHelp"
			>
				❓
			</button>
		</div>

		<!-- 帮助模态框 -->
		<div
			v-if="showHelp"
			class="help-modal fixed inset-0 bg-black/50 flex items-center justify-center z-1000"
			@click.self="toggleHelp"
		>
			<div
				class="help-content bg-background-primary p-lg rounded-lg shadow-lg max-w-500px w-90% relative"
			>
				<h4 class="m-0 text-lg font-semibold text-text-primary mb-md">
					删除字符说明
				</h4>
				<p class="m-0 text-sm text-text-secondary leading-1.5 mb-lg">
					从文件名中删除指定位置和数量的字符，支持从左侧或右侧删除
				</p>
				<button
					class="close-button absolute top-sm right-sm bg-none border-none text-lg cursor-pointer text-text-secondary w-30px h-30px flex items-center justify-center rounded-md hover:bg-background-secondary hover:text-text-primary"
					@click="toggleHelp"
				>
					✕
				</button>
			</div>
		</div>

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

		<!-- 删除示例 -->
		<div
			class="preview-example p-md bg-background-secondary rounded-md border border-border-secondary"
		>
			<h4
				class="example-title m-0 text-sm font-semibold text-text-primary mb-sm"
			>
				删除示例:
			</h4>
			<div class="example-content flex flex-col gap-xs">
				<div class="example-item flex gap-sm text-sm">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>原文件名:</span
					>
					<span class="example-original text-text-tertiary font-mono"
						>IMG_20240115_document.txt</span
					>
				</div>
				<div class="example-item flex gap-sm text-sm">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>新文件名:</span
					>
					<span class="example-new text-primary font-mono font-medium">
						{{ generateExample("IMG_20240115_document.txt") }}
					</span>
				</div>
				<div class="example-item flex gap-sm text-sm">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>删除说明:</span
					>
					<span class="example-description text-text-secondary italic">
						{{
							fromLeft
								? `从第${startPos}个字符开始删除${count}个字符`
								: `从右数第${startPos}个位置删除${count}个字符`
						}}
					</span>
				</div>
			</div>
		</div>

		<!-- 位置指示器 -->
		<div
			class="position-indicator p-md bg-background-secondary rounded-md border border-border-secondary"
		>
			<h4
				class="indicator-title m-0 text-sm font-semibold text-text-primary mb-sm"
			>
				位置指示 (以 "IMG_20240115_document" 为例):
			</h4>
			<div class="indicator-content">
				<div class="char-positions flex flex-col gap-xs">
					<div class="char-row flex items-center gap-sm">
						<span
							class="char-label min-w-40px text-xs text-text-secondary font-medium"
							>字符:</span
						>
						<div class="chars flex gap-1px">
							<span
								v-for="(char, index) in 'IMG_20240115_document'.split('')"
								:key="index"
								class="char flex items-center justify-center w-20px h-24px font-mono text-xs bg-background-primary border border-border-secondary"
								:class="{
									'highlight bg-error text-white font-semibold': fromLeft
										? index >= startPos - 1 && index < startPos - 1 + count
										: index >=
												'IMG_20240115_document'.length - startPos - count + 1 &&
										  index < 'IMG_20240115_document'.length - startPos + 1,
								}"
							>
								{{ char }}
							</span>
						</div>
					</div>
					<div class="position-row flex items-center gap-sm">
						<span
							class="char-label min-w-40px text-xs text-text-secondary font-medium"
							>位置:</span
						>
						<div class="positions flex gap-1px">
							<span
								v-for="(char, index) in 'IMG_20240115_document'.split('')"
								:key="index"
								class="position flex items-center justify-center w-20px h-24px font-mono text-xs bg-background-primary border border-border-secondary"
								:class="{
									'highlight bg-error text-white font-semibold': fromLeft
										? index >= startPos - 1 && index < startPos - 1 + count
										: index >=
												'IMG_20240115_document'.length - startPos - count + 1 &&
										  index < 'IMG_20240115_document'.length - startPos + 1,
								}"
							>
								{{
									fromLeft ? index + 1 : "IMG_20240115_document".length - index
								}}
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>

		<!-- 使用示例 -->
		<div class="operation-examples">
			<h4
				class="examples-title m-0 text-sm font-semibold text-text-primary mb-sm"
			>
				使用示例:
			</h4>
			<div class="examples-list flex flex-col gap-xs">
				<div class="example-item flex gap-sm text-xs">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>删除前缀:</span
					>
					<span class="example-content text-text-tertiary font-mono"
						>位置1，删除4个 → "IMG_" 被删除</span
					>
				</div>
				<div class="example-item flex gap-sm text-xs">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>删除后缀:</span
					>
					<span class="example-content text-text-tertiary font-mono"
						>从右数位置1，删除3个 → 删除末尾字符</span
					>
				</div>
				<div class="example-item flex gap-sm text-xs">
					<span class="example-label min-w-80px text-text-secondary font-medium"
						>删除中间:</span
					>
					<span class="example-content text-text-tertiary font-mono"
						>位置5，删除8个 → 删除日期部分</span
					>
				</div>
			</div>
		</div>
	</div>
</template>
