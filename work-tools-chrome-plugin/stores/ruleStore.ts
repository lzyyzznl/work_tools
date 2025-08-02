import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Rule, RuleConfig } from "../types/rule";
import { defaultRules } from "../constants/defaultRules";
import { useExcelUtils } from "../composables/useExcelUtils";

export const useRuleStore = defineStore("rule", () => {
	// 状态
	const rules = ref<Rule[]>([]);
	const isLoading = ref(false);

	// Excel工具函数
	const { exportRulesToExcel, importRulesFromExcel, createRuleTemplate } =
		useExcelUtils();

	// 数据验证函数
	function validateRule(rule: Partial<Rule>): {
		isValid: boolean;
		errors: string[];
	} {
		const errors: string[] = [];

		if (!rule.code || !rule.code.trim()) {
			errors.push("代码不能为空");
		}

		if (!rule.matchRules || rule.matchRules.length === 0) {
			errors.push("至少需要一个匹配规则");
		} else {
			const validRules = rule.matchRules.filter((r) => r && r.trim());
			if (validRules.length === 0) {
				errors.push("至少需要一个有效的匹配规则");
			}
		}

		if (rule.thirtyD && !["Y", "N", ""].includes(rule.thirtyD)) {
			errors.push("30D标记只能是Y、N或空");
		}

		return {
			isValid: errors.length === 0,
			errors,
		};
	}

	// 检查规则代码是否重复
	function isCodeDuplicate(
		code: string,
		excludeOptions?: {
			excludeId?: string; // 排除特定ID的规则
			excludeCode?: string; // 排除特定代码的所有规则
			excludeDefaultWithCode?: string; // 排除特定代码的默认规则
		}
	): boolean {
		if (!excludeOptions) {
			// 简单检查：代码是否存在
			return rules.value.some((rule) => rule.code === code);
		}

		return rules.value.some((rule) => {
			// 基本匹配：代码相同
			if (rule.code !== code) return false;

			// 排除特定ID
			if (excludeOptions.excludeId && rule.id === excludeOptions.excludeId) {
				return false;
			}

			// 排除特定代码的所有规则
			if (
				excludeOptions.excludeCode &&
				rule.code === excludeOptions.excludeCode
			) {
				return false;
			}

			// 排除特定代码的默认规则
			if (
				excludeOptions.excludeDefaultWithCode &&
				rule.code === excludeOptions.excludeDefaultWithCode &&
				rule.source === "default"
			) {
				return false;
			}

			return true;
		});
	}

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
		// 验证规则数据
		const validation = validateRule(ruleData);
		if (!validation.isValid) {
			throw new Error(`规则验证失败: ${validation.errors.join(", ")}`);
		}

		// 检查代码重复
		if (isCodeDuplicate(ruleData.code)) {
			throw new Error(`代码 "${ruleData.code}" 已存在`);
		}

		const newRule: Rule = {
			id: `user-${Date.now()}-${Math.random()}`,
			...ruleData,
			code: ruleData.code.trim(),
			matchRules: ruleData.matchRules
				.filter((r) => r.trim())
				.map((r) => r.trim()),
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
		if (index === -1) {
			throw new Error("规则不存在");
		}

		const rule = rules.value[index];
		const updatedData = { ...rule, ...ruleData };

		// 验证更新后的规则数据
		const validation = validateRule(updatedData);
		if (!validation.isValid) {
			throw new Error(`规则验证失败: ${validation.errors.join(", ")}`);
		}

		// 检查代码重复（排除当前规则）
		if (ruleData.code) {
			const excludeOptions =
				rule.source === "default"
					? { excludeDefaultWithCode: rule.code } // 编辑默认规则时，排除同代码的默认规则
					: { excludeId: id }; // 编辑用户规则时，排除当前规则ID

			if (isCodeDuplicate(ruleData.code, excludeOptions)) {
				throw new Error(`代码 "${ruleData.code}" 已存在`);
			}
		}

		// 清理数据
		if (ruleData.code) {
			ruleData.code = ruleData.code.trim();
		}
		if (ruleData.matchRules) {
			ruleData.matchRules = ruleData.matchRules
				.filter((r) => r.trim())
				.map((r) => r.trim());
		}

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

	async function exportRulesToExcelFile() {
		try {
			const result = exportRulesToExcel(rules.value);
			if (result.success) {
				return { success: true, message: `规则已导出到 ${result.filename}` };
			} else {
				return { success: false, message: result.error || "导出失败" };
			}
		} catch (error) {
			console.error("导出规则失败:", error);
			return { success: false, message: "导出失败" };
		}
	}

	async function importRulesFromExcelFile(file: File) {
		try {
			isLoading.value = true;
			const result = await importRulesFromExcel(file);

			if (result.success && result.rules) {
				// 保留默认规则
				const currentDefaultRules = rules.value.filter(
					(r) => r.source === "default"
				);
				const existingUserRules = rules.value.filter(
					(r) => r.source === "user"
				);

				let addedCount = 0;
				let updatedCount = 0;
				let skippedCount = 0;

				// 处理导入的规则：同code更新，不同code新增
				const processedUserRules = [...existingUserRules];

				for (const importedRule of result.rules) {
					// 查找是否存在相同代码的规则
					const existingRuleIndex = processedUserRules.findIndex(
						(r) => r.code === importedRule.code
					);
					const hasDefaultRule = currentDefaultRules.some(
						(r) => r.code === importedRule.code
					);

					if (existingRuleIndex >= 0) {
						// 存在相同代码的用户规则，检查是否需要更新
						const existingRule = processedUserRules[existingRuleIndex];
						const newMatchRules = [...existingRule.matchRules];
						let hasNewRules = false;

						// 检查导入规则中是否有新的匹配规则
						for (const matchRule of importedRule.matchRules) {
							if (!newMatchRules.includes(matchRule)) {
								newMatchRules.push(matchRule);
								hasNewRules = true;
							}
						}

						if (hasNewRules) {
							// 更新现有规则
							processedUserRules[existingRuleIndex] = {
								...existingRule,
								thirtyD: importedRule.thirtyD, // 更新30D标记
								matchRules: newMatchRules,
							};
							updatedCount++;
						} else {
							skippedCount++;
						}
					} else if (hasDefaultRule) {
						// 存在相同代码的默认规则，创建用户规则覆盖
						const defaultRule = currentDefaultRules.find(
							(r) => r.code === importedRule.code
						);
						const newMatchRules = [...(defaultRule?.matchRules || [])];
						let hasNewRules = false;

						// 检查导入规则中是否有新的匹配规则
						for (const matchRule of importedRule.matchRules) {
							if (!newMatchRules.includes(matchRule)) {
								newMatchRules.push(matchRule);
								hasNewRules = true;
							}
						}

						if (hasNewRules || importedRule.thirtyD !== defaultRule?.thirtyD) {
							// 创建新的用户规则
							processedUserRules.push({
								id: `user-${Date.now()}-${Math.random()}`,
								code: importedRule.code,
								thirtyD: importedRule.thirtyD,
								matchRules: newMatchRules,
								source: "user",
							});
							updatedCount++;
						} else {
							skippedCount++;
						}
					} else {
						// 不存在相同代码的规则，直接添加
						processedUserRules.push({
							id: `user-${Date.now()}-${Math.random()}`,
							code: importedRule.code,
							thirtyD: importedRule.thirtyD,
							matchRules: [...importedRule.matchRules],
							source: "user",
						});
						addedCount++;
					}
				}

				rules.value = [...currentDefaultRules, ...processedUserRules];
				await saveRules();

				const totalProcessed = addedCount + updatedCount;
				let message = "";
				if (totalProcessed > 0) {
					const parts = [];
					if (addedCount > 0) parts.push(`新增 ${addedCount} 条`);
					if (updatedCount > 0) parts.push(`更新 ${updatedCount} 条`);
					message = `成功导入：${parts.join("，")}规则`;
					if (skippedCount > 0) {
						message += `，跳过 ${skippedCount} 条重复规则`;
					}
				} else {
					message = "没有新的规则需要导入";
				}

				return {
					success: true,
					message,
					importedCount: totalProcessed,
					skippedCount,
				};
			} else {
				return { success: false, message: result.error || "导入失败" };
			}
		} catch (error) {
			console.error("导入规则失败:", error);
			return { success: false, message: "导入失败" };
		} finally {
			isLoading.value = false;
		}
	}

	function createRuleTemplateFile() {
		try {
			const result = createRuleTemplate();
			if (result.success) {
				return { success: true, message: `模板已创建: ${result.filename}` };
			} else {
				return { success: false, message: result.error || "创建模板失败" };
			}
		} catch (error) {
			console.error("创建模板失败:", error);
			return { success: false, message: "创建模板失败" };
		}
	}

	// 保留原有的JSON导入导出功能作为备用
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

		// Excel导入导出方法
		exportRulesToExcelFile,
		importRulesFromExcelFile,
		createRuleTemplateFile,

		// 保留的JSON导入导出方法
		exportRules,
		importRules,

		// 验证函数
		validateRule,
		isCodeDuplicate,
	};
});
