<script setup lang="ts">
import { computed } from "vue";

interface Props {
	modelValue: boolean;
	previewData: any;
}

interface Emits {
	(e: "update:modelValue", value: boolean): void;
	(e: "confirm"): void;
	(e: "cancel"): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const isVisible = computed({
	get: () => props.modelValue,
	set: (value: boolean) => emit("update:modelValue", value),
});

const preview = computed(() => props.previewData?.preview);
const stats = computed(() => props.previewData?.stats);

function handleConfirm() {
	emit("confirm");
}

function handleCancel() {
	emit("cancel");
}
</script>

<template>
	<div
		v-if="isVisible"
		class="fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-1000 p-spacing-lg"
		@click="handleCancel"
	>
		<div
			class="bg-background-primary rounded-radius-lg shadow-2xl w-full max-w-700px max-h-90vh flex flex-col overflow-hidden"
		>
			<!-- 模态框头部 -->
			<div
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-b-1px border-b-border-primary bg-background-secondary"
			>
				<h2
					class="flex items-center gap-spacing-sm m-0 text-xl font-semibold text-text-primary"
				>
					<span class="text-2xl">📥</span>
					导入数据预览
				</h2>
				<button
					class="w-32px h-32px border-none bg-none text-text-secondary text-xl cursor-pointer rounded-50% flex items-center justify-center transition-fast hover:bg-background-tertiary hover:text-text-primary"
					@click="handleCancel"
				>
					×
				</button>
			</div>

			<!-- 模态框内容 -->
			<div class="flex-1 overflow-y-auto p-spacing-lg">
				<div v-if="preview && stats" class="flex flex-col gap-spacing-lg">
					<!-- 导入统计 -->
					<div>
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							导入统计
						</h3>
						<div
							class="grid grid-cols-auto-fit-minmax-200px-1fr gap-spacing-sm"
						>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">版本:</span>
								<span class="text-text-primary text-sm font-medium">{{
									stats.version
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">文件数量:</span>
								<span class="text-text-primary text-sm font-medium">{{
									stats.fileCount
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">历史记录:</span>
								<span class="text-text-primary text-sm font-medium">{{
									stats.historyCount
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">包含设置:</span>
								<span class="text-text-primary text-sm font-medium">{{
									stats.hasSettings ? "是" : "否"
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">导入时间:</span>
								<span class="text-text-primary text-sm font-medium">{{
									stats.importDate
								}}</span>
							</div>
						</div>
					</div>

					<!-- 数据摘要 -->
					<div>
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							数据摘要
						</h3>
						<pre
							class="bg-background-secondary p-spacing-md rounded-radius-md text-sm text-text-secondary whitespace-pre-line m-0 font-mono"
							>{{ preview.summary }}</pre
						>
					</div>

					<!-- 文件预览 -->
					<div v-if="preview.filePreview.length > 0">
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							文件预览 (前5个)
						</h3>
						<ul class="m-0 p-0 list-none">
							<li
								v-for="file in preview.filePreview"
								:key="file"
								class="p-spacing-xs p-x-spacing-sm bg-background-secondary rounded-radius-sm m-b-spacing-xs text-sm text-text-secondary font-mono"
							>
								{{ file }}
							</li>
						</ul>
						<p
							v-if="stats.fileCount > 5"
							class="m-spacing-sm m-t-0 m-b-0 text-sm text-text-tertiary italic"
						>
							还有 {{ stats.fileCount - 5 }} 个文件...
						</p>
					</div>

					<!-- 历史记录预览 -->
					<div v-if="preview.historyPreview.length > 0">
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							历史记录预览 (前3个)
						</h3>
						<ul class="m-0 p-0 list-none">
							<li
								v-for="history in preview.historyPreview"
								:key="history"
								class="p-spacing-xs p-x-spacing-sm bg-background-secondary rounded-radius-sm m-b-spacing-xs text-sm text-text-secondary font-mono"
							>
								{{ history }}
							</li>
						</ul>
						<p
							v-if="stats.historyCount > 3"
							class="m-spacing-sm m-t-0 m-b-0 text-sm text-text-tertiary italic"
						>
							还有 {{ stats.historyCount - 3 }} 条历史记录...
						</p>
					</div>

					<!-- 设置预览 -->
					<div v-if="preview.settingsPreview.length > 0">
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							设置预览
						</h3>
						<ul class="m-0 p-0 list-none">
							<li
								v-for="setting in preview.settingsPreview"
								:key="setting"
								class="p-spacing-xs p-x-spacing-sm bg-background-secondary rounded-radius-sm m-b-spacing-xs text-sm text-text-secondary font-mono"
							>
								{{ setting }}
							</li>
						</ul>
					</div>

					<!-- 导入选项提醒 -->
					<div>
						<h3
							class="m-0 m-b-spacing-sm text-base font-semibold text-text-primary"
						>
							导入选项
						</h3>
						<div class="flex flex-col gap-spacing-xs">
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">替换现有文件:</span>
								<span class="text-text-primary text-sm font-medium">{{
									previewData?.options?.replaceExisting ? "是" : "否"
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">合并历史记录:</span>
								<span class="text-text-primary text-sm font-medium">{{
									previewData?.options?.mergeHistory ? "是" : "否"
								}}</span>
							</div>
							<div
								class="flex justify-between p-spacing-sm bg-background-secondary rounded-radius-sm"
							>
								<span class="text-text-secondary text-sm">导入设置:</span>
								<span class="text-text-primary text-sm font-medium">{{
									previewData?.options?.importSettings ? "是" : "否"
								}}</span>
							</div>
						</div>
					</div>
				</div>

				<div
					v-else
					class="flex flex-col items-center justify-center p-spacing-3xl text-center"
				>
					<div class="text-48px m-b-spacing-lg opacity-50">📄</div>
					<p class="m-0 text-text-secondary text-base">无法预览导入数据</p>
				</div>
			</div>

			<!-- 模态框底部 -->
			<div
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-t-1px border-t-border-primary bg-background-secondary"
			>
				<div class="flex items-center gap-spacing-xs">
					<span class="text-orange-500">⚠️</span>
					<span class="text-sm text-text-secondary"
						>请仔细检查导入数据，确认无误后再执行导入操作</span
					>
				</div>

				<div class="flex gap-spacing-sm">
					<button class="btn" @click="handleCancel">取消</button>
					<button class="btn btn-primary" @click="handleConfirm">
						确认导入
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
