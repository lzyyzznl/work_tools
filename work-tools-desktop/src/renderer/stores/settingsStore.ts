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
		try {
			const settingsData = JSON.stringify(settings.value, null, 2);
			// 这里我们将使用在界面层调用处记录日志，因为无法直接访问useErrorHandler
			return settingsData;
		} catch (error) {
			console.error("导出设置失败:", error);
			throw error;
		}
	}

	// 导入设置
	function importSettings(settingsJson: string): { success: boolean; stats?: any; error?: any } {
		try {
			const importedSettings = JSON.parse(settingsJson);			
			// 验证导入的设置格式
			if (typeof importedSettings !== "object" || importedSettings === null) {
				throw new Error("无效的设置格式");
			}

			// 保存导入前的设置快照
			const oldSettings = JSON.stringify(settings.value);
			
			// 统计变更信息
			const stats = {
				oldShortcutsCount: Object.keys(settings.value.shortcuts).length,
				newShortcutsCount: 0,
				addedShortcuts: [],
				modifiedShortcuts: [],
				removedShortcuts: []
			};

			const newShortcuts = importedSettings.shortcuts || {};
			const newKeys = Object.keys(newShortcuts);
			const oldKeys = Object.keys(settings.value.shortcuts);

			// 生成变更统计
			stats.newShortcutsCount = newKeys.length;
			stats.addedShortcuts = newKeys.filter(k => !oldKeys.includes(k));
			stats.removedShortcuts = oldKeys.filter(k => !newKeys.includes(k));
			stats.modifiedShortcuts = newKeys.filter(k => 
				oldKeys.includes(k) && newShortcuts[k] !== settings.value.shortcuts[k]
			);

			// 只处理 shortcuts 字段，确保兼容性
			settings.value = {
				shortcuts: newShortcuts,
			};

			saveSettings();

			return { 
				success: true, 
				stats: {
					...stats,
					totalChanged: stats.addedShortcuts.length + 
									stats.modifiedShortcuts.length + 
									stats.removedShortcuts.length
				}
			};
		} catch (error) {
			console.error("导入设置失败:", error);
			return { success: false, error };
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
