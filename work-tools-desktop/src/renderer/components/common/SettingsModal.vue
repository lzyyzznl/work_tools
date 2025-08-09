<script setup lang="ts">
import { ref, computed } from "vue";
import { useSettings } from "../../composables/useSettings";
import { useErrorHandler } from "../../composables/useErrorHandler";

interface Props {
	modelValue: boolean;
}

interface Emits {
	(e: "update:modelValue", value: boolean): void;
}

const props = defineProps<Props>();
const emit = defineEmits<Emits>();

const {
	settings,
	settingGroups,
	resetCategory,
	resetAllSettings,
	exportSettingsToFile,
	importSettingsFromFile,
	getSettingDescription,
	getSettingDisplayName,
} = useSettings();

const { handleError, handleSuccess, handleWarning } = useErrorHandler();

const activeTab = ref("shortcuts");
const isResetting = ref(false);
const isImporting = ref(false);

const isVisible = computed({
	get: () => props.modelValue,
	set: (value: boolean) => emit("update:modelValue", value),
});

function closeModal() {
	isVisible.value = false;
}

function switchTab(tabKey: string) {
	activeTab.value = tabKey;
}

async function handleResetCategory(category: string) {
	if (isResetting.value) return;

	isResetting.value = true;
	try {
		resetCategory(category as any);
		handleSuccess(`${getGroupTitle(category)}已重置为默认值`, "重置成功"); // 显示通知
	} catch (error) {
		handleError(error, "重置设置");
	} finally {
		isResetting.value = false;
	}
}

async function handleResetAll() {
	if (isResetting.value) return;

	if (!confirm("确定要重置所有设置为默认值吗？此操作不可撤销。")) {
		return;
	}

	isResetting.value = true;
	try {
		resetAllSettings();
		handleSuccess("所有设置已重置为默认值", "重置成功"); // 显示通知
	} catch (error) {
		handleError(error, "重置所有设置");
	} finally {
		isResetting.value = false;
	}
}

async function handleExport() {
	try {
		exportSettingsToFile();
		handleSuccess("设置已导出到文件", "导出成功", true); // 显示通知
	} catch (error) {
		handleError(error, "导出设置");
	}
}

async function handleImport() {
	if (isImporting.value) return;

	isImporting.value = true;
	try {
		const success = await importSettingsFromFile();
		if (success) {
			handleSuccess("设置已成功导入", "导入成功", true); // 显示通知
		} else {
			handleWarning("导入失败，请检查文件格式", "导入失败");
		}
	} catch (error) {
		handleError(error, "导入设置");
	} finally {
		isImporting.value = false;
	}
}

function getGroupTitle(key: string): string {
	const group = settingGroups.value.find((g) => g.key === key);
	return group?.title || key;
}
</script>

<template>
	<div
		v-if="isVisible"
		class="fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-1000 p-spacing-lg"
		@click="closeModal"
	>
		<div
			class="bg-white rounded-lg shadow-xl w-full max-w-800px max-h-90vh flex flex-col overflow-hidden"
		>
			<!-- 模态框头部 -->
			<div
				class="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-white"
			>
				<h2 class="flex items-center gap-3 m-0 text-xl font-bold text-gray-900">
					<span class="text-2xl">⚙️</span>
					设置
				</h2>
				<button
					class="w-8 h-8 border-none bg-none text-gray-500 text-xl cursor-pointer rounded-full flex items-center justify-center transition-colors hover:bg-gray-100 hover:text-gray-700"
					@click="closeModal"
				>
					×
				</button>
			</div>

			<!-- 模态框内容 -->
			<div class="flex-1 flex overflow-hidden">
				<!-- 标签页导航 -->
				<div class="w-50 bg-white border-r border-gray-200 p-3 overflow-y-auto">
					<button
						v-for="group in settingGroups"
						:key="group.key"
						class="w-full flex items-center gap-3 px-4 py-3 border-none bg-none text-gray-600 text-left cursor-pointer rounded-md transition-colors mb-1 hover:bg-gray-100 hover:text-gray-900"
						:class="{
							'bg-blue-50 text-blue-600 font-medium': activeTab === group.key,
						}"
						@click.stop="switchTab(group.key)"
					>
						<span class="text-base">{{ group.icon }}</span>
						<span class="text-sm">{{ group.title }}</span>
					</button>
				</div>

				<!-- 标签页内容 -->
				<div class="flex-1 overflow-y-auto p-6">
					<div
						v-for="group in settingGroups"
						:key="group.key"
						v-show="activeTab === group.key"
						class="tab-panel"
					>
						<div>
							<div class="flex items-center justify-between mb-6">
								<h3
									class="flex items-center gap-3 m-0 text-lg font-semibold text-gray-900"
								>
									<span class="text-xl">{{ group.icon }}</span>
									{{ group.title }}
								</h3>
								<button
									class="px-3 py-1.5 text-sm bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
									@click="handleResetCategory(group.key)"
									:disabled="isResetting"
								>
									🔄 重置
								</button>
							</div>

							<div class="flex flex-col gap-5">
								<div
									v-for="setting in group.settings"
									:key="setting.key"
									class="flex items-start justify-between gap-5 p-4 border border-gray-200 rounded-md bg-white"
									@click.stop
								>
									<div class="flex-1 min-w-0">
										<label class="block text-sm font-medium text-gray-900 mb-1">
											{{ getSettingDisplayName(setting.key as any) }}
										</label>
										<p class="m-0 text-xs text-gray-500 leading-1.4">
											{{ getSettingDescription(setting.key) }}
										</p>
									</div>

									<div class="flex items-center gap-spacing-sm flex-shrink-0">
										<!-- 快捷键设置特殊处理 -->
										<div v-if="setting.key === 'shortcuts'">
											<button
												class="px-3 py-1.5 text-sm bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
												@click="
													() => {
														/* 打开快捷键设置对话框 */
													}
												"
											>
												设置快捷键
											</button>
										</div>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- 模态框底部 -->
			<div
				class="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-white"
			>
				<div class="flex gap-2">
					<button
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
						@click="handleImport"
						:disabled="isImporting"
					>
						📥 导入设置
					</button>
					<button
						class="px-4 py-2 bg-gray-100 text-gray-700 rounded-md hover:bg-gray-200 transition-colors"
						@click="handleExport"
					>
						📤 导出设置
					</button>
				</div>

				<div class="flex gap-2">
					<button
						class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition-colors disabled:opacity-50"
						@click="handleResetAll"
						:disabled="isResetting"
					>
						🔄 重置所有
					</button>
					<button
						class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
						@click="closeModal"
					>
						完成
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
