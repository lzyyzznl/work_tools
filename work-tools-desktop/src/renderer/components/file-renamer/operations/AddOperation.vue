<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";

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

// 常用前缀/后缀预设
const presets = {
	prefix: [
		{ label: "日期前缀", value: new Date().toISOString().split("T")[0] + "_" },
		{ label: "编号前缀", value: "No." },
		{ label: "备份前缀", value: "backup_" },
		{ label: "新建前缀", value: "new_" },
	],
	suffix: [
		{ label: "备份后缀", value: "_backup" },
		{ label: "副本后缀", value: "_copy" },
		{ label: "编辑后缀", value: "_edited" },
		{ label: "最终后缀", value: "_final" },
	],
};

function applyPreset(value: string) {
	text.value = value;
}

// 帮助模态框控制
const showHelp = ref(false);

function toggleHelp() {
	showHelp.value = !showHelp.value;
}
</script>

<template>
	<div class="add-operation flex flex-col gap-lg">
		<div class="operation-header">
			<button
				class="help-button bg-none border-none text-lg cursor-pointer text-text-secondary ml-auto p-xs rounded-md hover:bg-background-secondary hover:text-primary"
				title="查看帮助"
				@click="toggleHelp"
			>
				<span
					class="inline-flex items-center justify-center w-6 h-6 rounded-full bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300"
				>
					?
				</span>
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
					添加前缀/后缀说明
				</h4>
				<p class="m-0 text-sm text-text-secondary leading-1.5 mb-lg">
					在文件名的开头或结尾添加指定的文本内容
				</p>
				<div class="mb-6">
					<h5 class="mb-2 text-sm font-semibold text-text-primary">
						使用示例:
					</h5>
					<ul class="text-sm text-text-secondary space-y-1">
						<li class="flex gap-sm">
							<span
								class="example-label min-w-80px text-text-secondary font-medium"
								>日期前缀:</span
							>
							<span class="example-content text-text-tertiary font-mono"
								>"2024-01-15_" → 2024-01-15_document.txt</span
							>
						</li>
						<li class="flex gap-sm">
							<span
								class="example-label min-w-80px text-text-secondary font-medium"
								>备份后缀:</span
							>
							<span class="example-content text-text-tertiary font-mono"
								>"_backup" → document_backup.txt</span
							>
						</li>
						<li class="flex gap-sm">
							<span
								class="example-label min-w-80px text-text-secondary font-medium"
								>版本标记:</span
							>
							<span class="example-content text-text-tertiary font-mono"
								>"_v2" → document_v2.txt</span
							>
						</li>
					</ul>
				</div>
				<button
					class="close-button absolute top-sm right-sm bg-none border-none text-lg cursor-pointer text-text-secondary w-30px h-30px flex items-center justify-center rounded-md hover:bg-background-secondary hover:text-text-primary"
					@click="toggleHelp"
				>
					✕
				</button>
			</div>
		</div>

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

			<!-- 预设选项 -->
			<div class="form-row flex items-end gap-md">
				<div class="form-group flex-1 flex flex-col gap-xs">
					<label class="form-label text-sm font-medium text-text-primary"
						>常用预设:</label
					>
					<div class="preset-buttons flex flex-wrap gap-xs">
						<button
							v-for="preset in isPrefix ? presets.prefix : presets.suffix"
							:key="preset.label"
							class="btn btn-sm btn-preset text-xs px-xs py-sm bg-background-secondary border border-border-secondary hover:bg-background-tertiary hover:border-primary"
							@click="applyPreset(preset.value)"
							:title="`应用: ${preset.value}`"
						>
							{{ preset.label }}
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
