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
	updateSetting,
	resetCategory,
	resetAllSettings,
	exportSettingsToFile,
	importSettingsFromFile,
	getSettingDescription,
	getSettingDisplayName,
	validateSetting,
} = useSettings();

const { handleError, handleSuccess, handleWarning } = useErrorHandler();

const activeTab = ref("interface");
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
		handleSuccess(`${getGroupTitle(category)}已重置为默认值`, "重置成功");
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
		handleSuccess("所有设置已重置为默认值", "重置成功");
	} catch (error) {
		handleError(error, "重置所有设置");
	} finally {
		isResetting.value = false;
	}
}

async function handleExport() {
	try {
		exportSettingsToFile();
		handleSuccess("设置已导出到文件", "导出成功");
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
			handleSuccess("设置已成功导入", "导入成功");
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

function handleSettingChange(key: string, value: any) {
	if (!validateSetting(key, value)) {
		handleWarning(
			`设置值无效: ${getSettingDisplayName(key as any)}`,
			"设置错误"
		);
		return;
	}

	updateSetting(key as any, value);
}
</script>

<template>
	<div
		v-if="isVisible"
		class="fixed top-0 left-0 right-0 bottom-0 bg-black bg-opacity-50 flex items-center justify-center z-1000 p-spacing-lg"
		@click="closeModal"
	>
		<div
			class="bg-background-primary rounded-radius-lg shadow-2xl w-full max-w-800px max-h-90vh flex flex-col overflow-hidden"
		>
			<!-- 模态框头部 -->
			<div
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-b-1px border-b-border-primary bg-background-secondary"
			>
				<h2
					class="flex items-center gap-spacing-sm m-0 text-xl font-semibold text-text-primary"
				>
					<span class="text-2xl">⚙️</span>
					设置
				</h2>
				<button
					class="w-32px h-32px border-none bg-none text-text-secondary text-xl cursor-pointer rounded-50% flex items-center justify-center transition-fast hover:bg-background-tertiary hover:text-text-primary"
					@click="closeModal"
				>
					×
				</button>
			</div>

			<!-- 模态框内容 -->
			<div class="flex-1 flex overflow-hidden">
				<!-- 标签页导航 -->
				<div
					class="w-200px bg-background-secondary border-r-1px border-r-border-primary p-spacing-md overflow-y-auto"
				>
					<button
						v-for="group in settingGroups"
						:key="group.key"
						class="w-full flex items-center gap-spacing-sm p-spacing-sm p-x-spacing-md border-none bg-none text-text-secondary text-left cursor-pointer rounded-radius-md transition-fast m-b-spacing-xs hover:bg-background-tertiary hover:text-text-primary"
						:class="{ 'bg-primary text-white': activeTab === group.key }"
						@click="switchTab(group.key)"
					>
						<span class="text-base">{{ group.icon }}</span>
						<span class="text-sm font-medium">{{ group.title }}</span>
					</button>
				</div>

				<!-- 标签页内容 -->
				<div class="flex-1 overflow-y-auto p-spacing-lg">
					<div
						v-for="group in settingGroups"
						:key="group.key"
						v-show="activeTab === group.key"
						class="tab-panel"
					>
						<div>
							<div class="flex items-center justify-between m-b-spacing-lg">
								<h3
									class="flex items-center gap-spacing-sm m-0 text-lg font-semibold text-text-primary"
								>
									<span class="text-xl">{{ group.icon }}</span>
									{{ group.title }}
								</h3>
								<button
									class="btn btn-sm"
									@click="handleResetCategory(group.key)"
									:disabled="isResetting"
								>
									🔄 重置
								</button>
							</div>

							<div class="flex flex-col gap-spacing-lg">
								<div
									v-for="setting in group.settings"
									:key="setting.key"
									class="flex items-start justify-between gap-spacing-lg p-spacing-md border-1px border-border-secondary rounded-radius-md bg-background-primary"
								>
									<div class="flex-1 min-w-0">
										<label
											class="block text-sm font-semibold text-text-primary m-b-spacing-xs"
										>
											{{ getSettingDisplayName(setting.key as any) }}
										</label>
										<p class="m-0 text-xs text-text-secondary leading-1.4">
											{{ getSettingDescription(setting.key) }}
										</p>
									</div>

									<div class="flex items-center gap-spacing-sm flex-shrink-0">
										<!-- 布尔值设置 -->
										<label
											v-if="setting.type === 'boolean'"
											class="relative inline-block w-44px h-24px cursor-pointer"
										>
											<input
												type="checkbox"
												:checked="settings[setting.key as keyof typeof settings]"
												@change="
													handleSettingChange(
														setting.key,
														($event.target as HTMLInputElement).checked
													)
												"
												class="opacity-0 w-0 h-0"
											/>
											<span
												class="absolute top-0 left-0 right-0 bottom-0 bg-border-primary transition-fast rounded-24px before:absoute before:content-empty before:h-18px before:w-18px before:left-3px before:bottom-3px before:bg-white before:transition-fast before:rounded-50% checked:bg-primary checked:before:translate-x-20px"
											></span>
										</label>

										<!-- 数字设置 -->
										<input
											v-else-if="setting.type === 'number'"
											type="number"
											:value="settings[setting.key as keyof typeof settings]"
											@input="
												handleSettingChange(
													setting.key,
													parseInt(($event.target as HTMLInputElement).value)
												)
											"
											:min="setting.min"
											:max="setting.max"
											class="min-w-120px p-spacing-xs p-x-spacing-sm border-1px border-border-primary rounded-radius-sm text-sm bg-background-primary text-text-primary focus:outline-none focus:border-primary focus:shadow-0-0-0-2px-rgba-0-122-255-0.1"
										/>

										<!-- 选择设置 -->
										<select
											v-else-if="setting.type === 'select'"
											:value="settings[setting.key as keyof typeof settings]"
											@change="
												handleSettingChange(
													setting.key,
													($event.target as HTMLSelectElement).value
												)
											"
											class="min-w-120px p-spacing-xs p-x-spacing-sm border-1px border-border-primary rounded-radius-sm text-sm bg-background-primary text-text-primary focus:outline-none focus:border-primary focus:shadow-0-0-0-2px-rgba-0-122-255-0.1"
										>
											<option
												v-for="option in setting.options"
												:key="option.value"
												:value="option.value"
											>
												{{ option.label }}
											</option>
										</select>

										<!-- 后缀文本 -->
										<span
											v-if="setting.suffix"
											class="text-sm text-text-secondary"
										>
											{{ setting.suffix }}
										</span>
									</div>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>

			<!-- 模态框底部 -->
			<div
				class="flex items-center justify-between p-spacing-lg p-x-spacing-xl border-t-1px border-t-border-primary bg-background-secondary"
			>
				<div class="flex gap-spacing-sm">
					<button class="btn" @click="handleImport" :disabled="isImporting">
						📥 导入设置
					</button>
					<button class="btn" @click="handleExport">📤 导出设置</button>
				</div>

				<div class="flex gap-spacing-sm">
					<button
						class="btn btn-danger"
						@click="handleResetAll"
						:disabled="isResetting"
					>
						🔄 重置所有
					</button>
					<button class="btn btn-primary" @click="closeModal">完成</button>
				</div>
			</div>
		</div>
	</div>
</template>
