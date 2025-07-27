<script setup lang="ts">
import { ref, computed, watch } from "vue";
import { useRenameStore } from "../../../stores/renameStore";
import { useRenameEngine } from "../../../composables/useRenameEngine";

const renameStore = useRenameStore();
const { generatePreview } = useRenameEngine();

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

// 帮助模态框控制
const showHelp = ref(false);

function toggleHelp() {
	showHelp.value = !showHelp.value;
}
</script>

<template>
	<div class="flex flex-col gap-4">
		<div>
			<button
				class="bg-none border-none text-lg cursor-pointer text-gray-500 dark:text-gray-400 ml-auto py-1 px-2 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-blue-500"
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
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-1000"
			@click.self="toggleHelp"
		>
			<div
				class="bg-white dark:bg-gray-800 p-6 rounded-xl shadow-lg max-w-[500px] w-[90%] relative"
			>
				<h4 class="mb-4 text-lg font-semibold text-gray-800 dark:text-gray-200">
					字符串替换说明
				</h4>
				<p class="mb-6 text-sm text-gray-500 dark:text-gray-400 leading-normal">
					将文件名中的指定字符串替换为新的字符串
				</p>
				<div class="mb-6">
					<h5
						class="mb-2 text-sm font-semibold text-gray-800 dark:text-gray-200"
					>
						使用示例:
					</h5>
					<ul class="text-sm text-gray-500 dark:text-gray-400 space-y-1">
						<li class="flex gap-2">
							<span
								class="min-w-[80px] text-gray-500 dark:text-gray-400 font-medium"
								>删除前缀:</span
							>
							<span class="text-gray-400 dark:text-gray-500 font-mono"
								>查找 "IMG_" → 替换为 ""</span
							>
						</li>
						<li class="flex gap-2">
							<span
								class="min-w-[80px] text-gray-500 dark:text-gray-400 font-medium"
								>替换分隔符:</span
							>
							<span class="text-gray-400 dark:text-gray-500 font-mono"
								>查找 "_" → 替换为 "-"</span
							>
						</li>
						<li class="flex gap-2">
							<span
								class="min-w-[80px] text-gray-500 dark:text-gray-400 font-medium"
								>修改扩展名:</span
							>
							<span class="text-gray-400 dark:text-gray-500 font-mono"
								>查找 ".txt" → 替换为 ".md"</span
							>
						</li>
					</ul>
				</div>
				<button
					class="absolute top-2 right-2 bg-none border-none text-lg cursor-pointer text-gray-500 dark:text-gray-400 w-8 h-8 flex items-center justify-center rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 hover:text-gray-800 dark:hover:text-gray-200"
					@click="toggleHelp"
				>
					✕
				</button>
			</div>
		</div>

		<div class="flex flex-col gap-3">
			<div class="flex items-end gap-3">
				<div class="flex-1 flex flex-col gap-1">
					<label
						for="from-str"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>查找字符串:</label
					>
					<input
						id="from-str"
						v-model="fromStr"
						type="text"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						placeholder="要替换的字符串"
						autocomplete="off"
					/>
				</div>

				<div class="flex items-center pb-2">
					<button
						class="w-9 h-9 flex items-center justify-center text-lg font-bold disabled:opacity-50"
						@click="swapParams"
						title="交换查找和替换内容"
						:disabled="!fromStr && !toStr"
					>
						⇄
					</button>
				</div>

				<div class="flex-1 flex flex-col gap-1">
					<label
						for="to-str"
						class="text-sm font-medium text-gray-800 dark:text-gray-200"
						>替换为:</label
					>
					<input
						id="to-str"
						v-model="toStr"
						type="text"
						class="py-2 px-3 border border-gray-300 dark:border-gray-600 rounded-md text-sm transition-colors duration-150 focus:outline-none focus:border-blue-500 focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] dark:focus:shadow-[0_0_0_2px_rgba(0,122,255,0.1)] placeholder:text-gray-400 dark:placeholder:text-gray-500"
						placeholder="新的字符串（留空表示删除）"
						autocomplete="off"
					/>
				</div>
			</div>

			<div class="flex items-center justify-between gap-3">
				<button
					class="text-sm py-1 px-2 disabled:opacity-50"
					@click="clearParams"
					:disabled="!fromStr && !toStr"
				>
					🗑️ 清空
				</button>

				<div>
					<span class="text-xs text-gray-400 dark:text-gray-500">
						💡 支持精确匹配，区分大小写
					</span>
				</div>
			</div>
		</div>

		<!-- 参数验证提示 -->
		<div
			v-if="fromStr && !renameStore.hasValidParams"
			class="py-2 px-3 bg-orange-100 dark:bg-orange-900 bg-opacity-10 text-orange-500 border border-orange-200 dark:border-orange-800 border-opacity-20 rounded-md text-sm"
		>
			⚠️ 请输入要查找的字符串
		</div>
	</div>
</template>
