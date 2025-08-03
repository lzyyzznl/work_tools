import type { Rule } from "../types/rule";

// 从Python版本迁移的完整默认规则数据
export const defaultRules: Rule[] = [
	{
		id: "default-1",
		code: "unique_code",
		matchRules: ["规则1", "规则2", "规则N"],
	},
];
