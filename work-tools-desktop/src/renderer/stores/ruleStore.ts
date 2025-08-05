import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { Rule, RuleConfig, RuleColumn } from "../types/rule";
import { defaultRules } from "../constants/defaultRules";
import { STORAGE_KEYS } from "../constants/app";

export const useRuleStore = defineStore("rule", () => {
	// 状态
	const rules = ref<Rule[]>([]);
	const columns = ref<RuleColumn[]>([]); // 规则列配置
	const isLoading = ref(false);

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

		return {
			isValid: errors.length === 0,
			errors,
		};
	}

	// 检查规则编码是否重复
	function isCodeDuplicate(code: string, excludeId?: string): boolean {
		return rules.value.some(
			(rule) => rule.code === code && rule.id !== excludeId
		);
	}

	// 计算属性
	const ruleCount = computed(() => rules.value.length);
	const visibleColumns = computed(() =>
		columns.value.filter((col) => col.visible).sort((a, b) => a.order - b.order)
	);

	// Electron 环境下的存储操作
	async function loadRules() {
		isLoading.value = true;
		try {
			// 从 localStorage 加载规则（Electron 环境）
			const storedConfig = localStorage.getItem(STORAGE_KEYS.RULES);
			const config: RuleConfig = storedConfig
				? JSON.parse(storedConfig)
				: {
						version: "1.0",
						settings: {
							autoSave: true,
							defaultExportFormat: "xlsx",
						},
						rules: defaultRules,
						columns: [], // 默认空的列配置
				  };

			// 直接使用规则
			rules.value = config.rules;

			// 加载列配置
			if (config.columns && config.columns.length > 0) {
				columns.value = config.columns;
			} else {
				// 如果没有列配置，初始化默认列配置
				initializeDefaultColumns();
			}

			// 如果是首次加载，保存默认配置
			if (!storedConfig) {
				await saveRules();
			}
		} catch (error) {
			console.error("Failed to load rules:", error);
			// 使用默认规则
			rules.value = [...defaultRules];
			// 初始化默认列配置
			initializeDefaultColumns();
		} finally {
			isLoading.value = false;
		}
	}

	// 初始化默认列配置
	function initializeDefaultColumns() {
		// 默认创建一个空的列
		columns.value = [];
	}

	// 列管理方法
	function addColumn(columnData: Omit<RuleColumn, "id">) {
		const newColumn: RuleColumn = {
			id: `col-${Date.now()}-${Math.random()}`,
			...columnData,
		};
		columns.value.push(newColumn);
		saveRules();
		return newColumn.id;
	}

	function updateColumn(
		id: string,
		columnData: Partial<Omit<RuleColumn, "id">>
	) {
		const index = columns.value.findIndex((col) => col.id === id);
		if (index === -1) {
			throw new Error("列不存在");
		}

		Object.assign(columns.value[index], columnData);
		saveRules();
	}

	function deleteColumn(id: string) {
		const index = columns.value.findIndex((col) => col.id === id);
		if (index > -1) {
			columns.value.splice(index, 1);
			saveRules();
		}
	}

	function getColumnById(id: string) {
		return columns.value.find((col) => col.id === id);
	}

	function moveColumn(id: string, newIndex: number) {
		const index = columns.value.findIndex((col) => col.id === id);
		if (index === -1) {
			throw new Error("列不存在");
		}

		const [movedColumn] = columns.value.splice(index, 1);
		columns.value.splice(newIndex, 0, movedColumn);

		// 更新所有列的order属性
		columns.value.forEach((col, i) => {
			col.order = i;
		});

		saveRules();
	}

	async function saveRules() {
		try {
			const config: RuleConfig = {
				version: "1.0",
				settings: {
					autoSave: true,
					defaultExportFormat: "xlsx",
				},
				rules: rules.value,
				columns: columns.value, // 保存列配置
			};

			// 保存到 localStorage（Electron 环境）
			localStorage.setItem(STORAGE_KEYS.RULES, JSON.stringify(config));
		} catch (error) {
			console.error("Failed to save rules:", error);
			throw error;
		}
	}

	function addRule(ruleData: Omit<Rule, "id">) {
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
		};

		rules.value.push(newRule);
		saveRules();
		return newRule.id;
	}

	function updateRule(id: string, ruleData: Partial<Omit<Rule, "id">>) {
		const index = rules.value.findIndex((r) => r.id === id);
		if (index === -1) {
			throw new Error("规则不存在");
		}

		const rule = rules.value[index];

		// 处理 columnValues 的合并
		let finalRuleData = { ...ruleData };
		if (ruleData.columnValues) {
			// 确保 columnValues 对象存在
			if (!rule.columnValues) {
				rule.columnValues = {};
			}
			// 合并 columnValues
			finalRuleData.columnValues = {
				...rule.columnValues,
				...ruleData.columnValues,
			};
		}

		const updatedData = { ...rule, ...finalRuleData };

		// 验证更新后的规则数据
		const validation = validateRule(updatedData);
		if (!validation.isValid) {
			throw new Error(`规则验证失败: ${validation.errors.join(", ")}`);
		}

		// 检查代码重复（排除当前规则）
		if (ruleData.code && isCodeDuplicate(ruleData.code, id)) {
			throw new Error(`代码 "${ruleData.code}" 已存在`);
		}

		// 清理数据
		if (ruleData.code) {
			finalRuleData.code = ruleData.code.trim();
		}
		if (ruleData.matchRules) {
			finalRuleData.matchRules = ruleData.matchRules
				.filter((r) => r.trim())
				.map((r) => r.trim());
		}

		// 直接更新规则
		Object.assign(rule, finalRuleData);

		saveRules();
	}

	function deleteRule(id: string) {
		const index = rules.value.findIndex((r) => r.id === id);
		if (index > -1) {
			// 直接删除规则
			rules.value.splice(index, 1);
			saveRules();
		}
	}

	function getRuleById(id: string) {
		return rules.value.find((r) => r.id === id);
	}

	function matchFilename(filename: string) {
		// 转换为小写以实现不区分大小写的匹配
		const lowerFilename = filename.toLowerCase();

		for (let i = 0; i < rules.value.length; i++) {
			const rule = rules.value[i];

			// 跳过被删除的规则
			if (rule.matchRules.length === 0) continue;

			for (const matchRule of rule.matchRules) {
				if (matchRule && lowerFilename.includes(matchRule.toLowerCase())) {
					return {
						matched: true,
						matchInfo: {
							index: i,
							code: rule.code,
							matchedRule: matchRule,
							// 添加规则的列值信息
							columnValues: rule.columnValues || {},
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

	function resetColumnsToDefault() {
		initializeDefaultColumns();
		saveRules();
	}

	// 保留原有的JSON导入导出功能
	function exportRules() {
		return {
			version: "1.0",
			exportTime: new Date().toISOString(),
			rules: rules.value,
		};
	}

	function importRules(data: any) {
		if (data.rules && Array.isArray(data.rules)) {
			// 直接导入所有规则
			rules.value = [...data.rules];
			saveRules();
		}
	}

	return {
		// 状态
		rules,
		columns,
		isLoading,

		// 计算属性
		ruleCount,
		visibleColumns,

		// 方法
		loadRules,
		saveRules,
		addRule,
		updateRule,
		deleteRule,
		getRuleById,
		matchFilename,
		resetToDefault,

		// 列管理方法
		addColumn,
		updateColumn,
		deleteColumn,
		getColumnById,
		moveColumn,
		resetColumnsToDefault,

		// JSON导入导出方法
		exportRules,
		importRules,

		// 验证函数
		validateRule,
		isCodeDuplicate,
	};
});
