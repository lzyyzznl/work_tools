import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Rule, RuleConfig } from "../types/rule";

export const useRuleStore = defineStore("rule", () => {
	// 状态
	const rules = ref<Rule[]>([]);
	const isLoading = ref(false);

	// 默认规则配置 - 从原Python程序迁移
	const defaultRules: Rule[] = [
		{
			id: "default-1",
			code: "01.33.06.01",
			thirtyD: "N",
			matchRules: [
				"Confidential Disclosure Agreements",
				"CDA",
				"confidential",
				"disclosure",
			],
			source: "default",
		},
		{
			id: "default-2",
			code: "01.33.06.02",
			thirtyD: "N",
			matchRules: ["one way letter", "oneway", "one-way"],
			source: "default",
		},
		{
			id: "default-3",
			code: "01.33.10.02",
			thirtyD: "N",
			matchRules: ["Privacy notice", "PN", "privacy", "notice"],
			source: "default",
		},
		{
			id: "default-4",
			code: "02.02.03",
			thirtyD: "N",
			matchRules: ["FDC", "financial", "disclosure"],
			source: "default",
		},
		{
			id: "default-5",
			code: "02.03.03",
			thirtyD: "Y",
			matchRules: ["Local Destruction", "493847", "destruction", "local"],
			source: "default",
		},
		{
			id: "default-6",
			code: "03.01.01",
			thirtyD: "N",
			matchRules: ["contract", "agreement", "CONTRACT", "AGREEMENT"],
			source: "default",
		},
		{
			id: "default-7",
			code: "03.02.01",
			thirtyD: "Y",
			matchRules: ["invoice", "bill", "payment", "INVOICE"],
			source: "default",
		},
		{
			id: "default-8",
			code: "04.01.01",
			thirtyD: "N",
			matchRules: ["report", "analysis", "REPORT", "summary"],
			source: "default",
		},
		{
			id: "default-9",
			code: "05.01.01",
			thirtyD: "N",
			matchRules: ["email", "correspondence", "letter", "EMAIL"],
			source: "default",
		},
		{
			id: "default-10",
			code: "06.01.01",
			thirtyD: "Y",
			matchRules: ["temp", "temporary", "draft", "TEMP", "DRAFT"],
			source: "default",
		},
	];

	// 计算属性
	const userRules = computed(() =>
		rules.value.filter((r) => r.source === "user")
	);
	const systemRules = computed(() =>
		rules.value.filter((r) => r.source === "default")
	);
	const ruleCount = computed(() => rules.value.length);

	// 操作方法
	async function loadRules() {
		isLoading.value = true;
		try {
			// 从 chrome.storage 加载规则
			const result = await chrome.storage.local.get(["ruleConfig"]);
			const config: RuleConfig = result.ruleConfig || {
				version: "1.0",
				settings: {
					autoSave: true,
					defaultExportFormat: "xlsx",
					theme: "light",
				},
				rules: {
					default: defaultRules,
					user: [],
				},
			};

			// 合并默认规则和用户规则
			const mergedRules = [...config.rules.default, ...config.rules.user];
			rules.value = mergedRules;

			// 如果是首次加载，保存默认配置
			if (!result.ruleConfig) {
				await saveRules();
			}
		} catch (error) {
			console.error("Failed to load rules:", error);
			// 使用默认规则
			rules.value = [...defaultRules];
		} finally {
			isLoading.value = false;
		}
	}

	async function saveRules() {
		try {
			const config: RuleConfig = {
				version: "1.0",
				settings: {
					autoSave: true,
					defaultExportFormat: "xlsx",
					theme: "light",
				},
				rules: {
					default: systemRules.value,
					user: userRules.value,
				},
			};

			await chrome.storage.local.set({ ruleConfig: config });
		} catch (error) {
			console.error("Failed to save rules:", error);
			throw error;
		}
	}

	function addRule(ruleData: Omit<Rule, "id" | "source">) {
		const newRule: Rule = {
			id: `user-${Date.now()}-${Math.random()}`,
			...ruleData,
			source: "user",
		};

		rules.value.push(newRule);
		saveRules();
		return newRule.id;
	}

	function updateRule(
		id: string,
		ruleData: Partial<Omit<Rule, "id" | "source">>
	) {
		const index = rules.value.findIndex((r) => r.id === id);
		if (index > -1) {
			const rule = rules.value[index];

			// 如果是默认规则，创建用户规则覆盖
			if (rule.source === "default") {
				const newRule: Rule = {
					...rule,
					...ruleData,
					id: `user-${Date.now()}-${Math.random()}`,
					source: "user",
				};
				rules.value.push(newRule);

				// 移除原默认规则
				rules.value.splice(index, 1);
			} else {
				// 直接更新用户规则
				Object.assign(rule, ruleData);
			}

			saveRules();
		}
	}

	function deleteRule(id: string) {
		const index = rules.value.findIndex((r) => r.id === id);
		if (index > -1) {
			const rule = rules.value[index];

			if (rule.source === "default") {
				// 对于默认规则，标记为删除而不是真正删除
				rule.matchRules = [];
			} else {
				// 直接删除用户规则
				rules.value.splice(index, 1);
			}

			saveRules();
		}
	}

	function getRuleById(id: string) {
		return rules.value.find((r) => r.id === id);
	}

	function matchFilename(filename: string) {
		for (let i = 0; i < rules.value.length; i++) {
			const rule = rules.value[i];

			// 跳过被删除的规则
			if (rule.matchRules.length === 0) continue;

			for (const matchRule of rule.matchRules) {
				if (matchRule && filename.includes(matchRule)) {
					return {
						matched: true,
						matchInfo: {
							index: i,
							code: rule.code,
							thirtyD: rule.thirtyD,
							matchedRule: matchRule,
						},
					};
				}
			}
		}

		return { matched: false, matchInfo: null };
	}

	function resetToDefault() {
		rules.value = [...defaultRules];
		saveRules();
	}

	function exportRules() {
		return {
			version: "1.0",
			exportTime: new Date().toISOString(),
			rules: rules.value,
		};
	}

	function importRules(data: any) {
		if (data.rules && Array.isArray(data.rules)) {
			// 保留默认规则，只导入用户规则
			const importedUserRules = data.rules.filter(
				(r: Rule) => r.source === "user"
			);
			const currentDefaultRules = rules.value.filter(
				(r) => r.source === "default"
			);

			rules.value = [...currentDefaultRules, ...importedUserRules];
			saveRules();
		}
	}

	return {
		// 状态
		rules,
		isLoading,

		// 计算属性
		userRules,
		systemRules,
		ruleCount,

		// 方法
		loadRules,
		saveRules,
		addRule,
		updateRule,
		deleteRule,
		getRuleById,
		matchFilename,
		resetToDefault,
		exportRules,
		importRules,
	};
});
