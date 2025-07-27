import { defineStore } from "pinia";
import { ref, watch } from "vue";
import type { AppSettings } from "../types/common";
import { STORAGE_KEYS } from "../constants/app";

const defaultSettings: AppSettings = {
	shortcuts: {},
};

export const useSettingsStore = defineStore("settings", () => {
	const settings = ref<AppSettings>({ ...defaultSettings });
	const isLoading = ref(false);
	const lastSaved = ref<number>(0);

	// 从localStorage加载设置
	function loadSettings() {
		isLoading.value = true;
		try {
			const saved = localStorage.getItem(STORAGE_KEYS.SETTINGS);
			if (saved) {
				const parsedSettings = JSON.parse(saved);
				// 只保留 shortcuts 字段，过滤掉已删除的字段
				settings.value = {
					shortcuts: parsedSettings.shortcuts || defaultSettings.shortcuts,
				};
			}
		} catch (error) {
			console.error("加载设置失败:", error);
			settings.value = { ...defaultSettings };
		} finally {
			isLoading.value = false;
		}
	}

	// 保存设置到localStorage
	function saveSettings() {
		try {
			localStorage.setItem(
				STORAGE_KEYS.SETTINGS,
				JSON.stringify(settings.value)
			);
			lastSaved.value = Date.now();
		} catch (error) {
			console.error("保存设置失败:", error);
			throw new Error("保存设置失败，可能是存储空间不足");
		}
	}

	// 更新单个设置项
	function updateSetting<K extends keyof AppSettings>(
		key: K,
		value: AppSettings[K]
	) {
		settings.value[key] = value;
		saveSettings();
	}

	// 批量更新设置
	function updateSettings(newSettings: Partial<AppSettings>) {
		Object.assign(settings.value, newSettings);
		saveSettings();
	}

	// 重置设置为默认值
	function resetSettings() {
		settings.value = { ...defaultSettings };
		saveSettings();
	}

	// 重置特定分类的设置
	function resetCategory(category: "shortcuts") {
		switch (category) {
			case "shortcuts":
				settings.value.shortcuts = defaultSettings.shortcuts;
				break;
		}

		saveSettings();
	}

	// 导出设置
	function exportSettings(): string {
		return JSON.stringify(settings.value, null, 2);
	}

	// 导入设置
	function importSettings(settingsJson: string): boolean {
		try {
			const importedSettings = JSON.parse(settingsJson);

			// 验证导入的设置格式
			if (typeof importedSettings !== "object" || importedSettings === null) {
				throw new Error("无效的设置格式");
			}

			// 只处理 shortcuts 字段，确保兼容性
			settings.value = {
				shortcuts: importedSettings.shortcuts || defaultSettings.shortcuts,
			};

			saveSettings();

			return true;
		} catch (error) {
			console.error("导入设置失败:", error);
			return false;
		}
	}

	// 获取设置的显示名称
	function getSettingDisplayName(key: keyof AppSettings): string {
		const displayNames: Record<keyof AppSettings, string> = {
			shortcuts: "快捷键",
		};

		return displayNames[key] || key;
	}

	// 监听设置变化，自动保存
	watch(
		settings,
		() => {
			if (!isLoading.value) {
				saveSettings();
			}
		},
		{ deep: true }
	);

	// 初始化时加载设置
	loadSettings();

	return {
		settings,
		isLoading,
		lastSaved,
		loadSettings,
		saveSettings,
		updateSetting,
		updateSettings,
		resetSettings,
		resetCategory,
		exportSettings,
		importSettings,
		getSettingDisplayName,
	};
});
