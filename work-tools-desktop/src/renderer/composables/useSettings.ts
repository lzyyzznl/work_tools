import { computed } from "vue";
import { useSettingsStore } from "../stores/settingsStore";
import { useKeyboardShortcuts } from "./useKeyboardShortcuts";

export function useSettings() {
	const settingsStore = useSettingsStore();
	const { setEnabled: setShortcutsEnabled } = useKeyboardShortcuts();

	// 应用设置到各个系统
	function applySettings() {
		// 应用快捷键设置
		setShortcutsEnabled(true); // 默认启用快捷键
	}

	// 验证设置值
	function validateSetting(key: string, value: any): boolean {
		// 目前没有针对快捷键的特殊验证规则
		return true;
	}

	// 获取设置分组
	const settingGroups = computed(() => [
		{
			key: "shortcuts",
			title: "快捷键设置",
			icon: "⌨️",
			settings: [
				{
					key: "shortcuts",
				},
			],
		},
	]);

	// 获取设置项的描述
	function getSettingDescription(key: string): string {
		const descriptions: Record<string, string> = {
			shortcuts: "自定义键盘快捷键",
		};

		return descriptions[key] || "";
	}

	// 重置所有设置
	function resetAllSettings() {
		settingsStore.resetSettings();
		applySettings();
	}

	// 导出设置到文件
	function exportSettingsToFile() {
		const settings = settingsStore.exportSettings();
		const blob = new Blob([settings], { type: "application/json" });
		const url = URL.createObjectURL(blob);

		const a = document.createElement("a");
		a.href = url;
		a.download = `work-tools-settings-${
			new Date().toISOString().split("T")[0]
		}.json`;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);

		URL.revokeObjectURL(url);
	}

	// 从文件导入设置
	function importSettingsFromFile(): Promise<boolean> {
		return new Promise((resolve) => {
			const input = document.createElement("input");
			input.type = "file";
			input.accept = ".json";

			input.onchange = (e) => {
				const file = (e.target as HTMLInputElement).files?.[0];
				if (!file) {
					resolve(false);
					return;
				}

				const reader = new FileReader();
				reader.onload = (e) => {
					const content = e.target?.result as string;
					const success = settingsStore.importSettings(content);
					if (success) {
						applySettings();
					}
					resolve(success);
				};
				reader.onerror = () => resolve(false);
				reader.readAsText(file);
			};

			input.click();
		});
	}

	return {
		settings: settingsStore.settings,
		isLoading: settingsStore.isLoading,
		lastSaved: settingsStore.lastSaved,
		settingGroups,
		applySettings,
		validateSetting,
		getSettingDescription,
		updateSetting: settingsStore.updateSetting,
		updateSettings: settingsStore.updateSettings,
		resetSettings: settingsStore.resetSettings,
		resetCategory: settingsStore.resetCategory,
		resetAllSettings,
		exportSettingsToFile,
		importSettingsFromFile,
		getSettingDisplayName: settingsStore.getSettingDisplayName,
	};
}
