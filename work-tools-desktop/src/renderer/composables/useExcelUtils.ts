import * as XLSX from "xlsx";
import type { Rule } from "../types/rule";

export interface ExcelRule {
	code: string;
	match_rules: string;
}

export interface ExcelMatchResult {
	文件名: string;
	文件路径: string;
	文件大小: string;
	修改时间: string;
	是否匹配成功: string;
	匹配代码: string;
	匹配规则: string;
}

export function useExcelUtils() {
	/**
	 * 导出规则到Excel文件
	 */
	function exportRulesToExcel(rules: Rule[], filename?: string) {
		try {
			// 转换规则数据格式
			const excelData: ExcelRule[] = rules.map((rule) => ({
				code: rule.code,
				match_rules: rule.matchRules.join("; "),
			}));

			// 创建工作簿
			const wb = XLSX.utils.book_new();
			const ws = XLSX.utils.json_to_sheet(excelData);

			// 设置列宽
			ws["!cols"] = [
				{ width: 15 }, // code
				{ width: 8 }, // 30d
				{ width: 50 }, // match_rules
			];

			// 添加工作表
			XLSX.utils.book_append_sheet(wb, ws, "规则列表");

			// 生成文件名
			const defaultFilename = `rules-export-${
				new Date().toISOString().split("T")[0]
			}.xlsx`;
			const finalFilename = filename || defaultFilename;

			// 导出文件
			XLSX.writeFile(wb, finalFilename);

			return { success: true, filename: finalFilename };
		} catch (error) {
			console.error("导出规则失败:", error);
			return {
				success: false,
				error: error instanceof Error ? error.message : "未知错误",
			};
		}
	}

	/**
	 * 从Excel文件导入规则
	 */
	function importRulesFromExcel(
		file: File
	): Promise<{ success: boolean; rules?: Rule[]; error?: string }> {
		return new Promise((resolve) => {
			const reader = new FileReader();

			reader.onload = (e) => {
				try {
					const data = new Uint8Array(e.target?.result as ArrayBuffer);
					const workbook = XLSX.read(data, { type: "array" });

					// 获取第一个工作表
					const firstSheetName = workbook.SheetNames[0];
					const worksheet = workbook.Sheets[firstSheetName];

					// 转换为JSON
					const jsonData = XLSX.utils.sheet_to_json<ExcelRule>(worksheet);

					// 验证和转换数据
					const rules: Rule[] = [];
					const errors: string[] = [];

					jsonData.forEach((row, index) => {
						try {
							// 验证必填字段
							if (!row.code || !row.code.trim()) {
								errors.push(`第${index + 2}行：代码不能为空`);
								return;
							}

							if (!row.match_rules || !row.match_rules.trim()) {
								errors.push(`第${index + 2}行：匹配规则不能为空`);
								return;
							}

							// 转换数据格式
							const rule: Rule = {
								id: `imported-${Date.now()}-${Math.random()}`,
								code: row.code.trim(),
								matchRules: row.match_rules
									.split(";")
									.map((r) => r.trim())
									.filter((r) => r),
							};

							rules.push(rule);
						} catch (error) {
							errors.push(`第${index + 2}行：数据格式错误`);
						}
					});

					if (errors.length > 0) {
						resolve({
							success: false,
							error: `导入失败：\n${errors.join("\n")}`,
						});
						return;
					}

					if (rules.length === 0) {
						resolve({
							success: false,
							error: "文件中没有有效的规则数据",
						});
						return;
					}

					resolve({ success: true, rules });
				} catch (error) {
					resolve({
						success: false,
						error: error instanceof Error ? error.message : "文件解析失败",
					});
				}
			};

			reader.onerror = () => {
				resolve({ success: false, error: "文件读取失败" });
			};

			reader.readAsArrayBuffer(file);
		});
	}

	/**
	 * 导出匹配结果到Excel文件
	 */
	function exportMatchResultsToExcel(
		results: ExcelMatchResult[],
		filename?: string
	) {
		try {
			// 创建工作簿
			const wb = XLSX.utils.book_new();
			const ws = XLSX.utils.json_to_sheet(results);

			// 设置列宽
			ws["!cols"] = [
				{ width: 30 }, // 文件名
				{ width: 40 }, // 文件路径
				{ width: 12 }, // 文件大小
				{ width: 20 }, // 修改时间
				{ width: 12 }, // 是否匹配成功
				{ width: 15 }, // 匹配代码
				{ width: 10 }, // 30D标记
				{ width: 30 }, // 匹配规则
			];

			// 添加工作表
			XLSX.utils.book_append_sheet(wb, ws, "匹配结果");

			// 生成文件名
			const defaultFilename = `file-match-results-${
				new Date().toISOString().split("T")[0]
			}.xlsx`;
			const finalFilename = filename || defaultFilename;

			// 导出文件
			XLSX.writeFile(wb, finalFilename);

			return { success: true, filename: finalFilename };
		} catch (error) {
			console.error("导出匹配结果失败:", error);
			return {
				success: false,
				error: error instanceof Error ? error.message : "未知错误",
			};
		}
	}

	/**
	 * 创建规则导入模板
	 */
	function createRuleTemplate() {
		const templateData: ExcelRule[] = [
			{
				code: "01.33.06.01",
				match_rules: "Confidential Disclosure Agreements; CDA; confidential",
			},
			{
				code: "01.33.06.02",
				match_rules: "one way letter; oneway; one-way",
			},
		];

		return exportRulesToExcel(
			templateData.map((item) => ({
				id: `template-${Math.random()}`,
				code: item.code,
				matchRules: item.match_rules.split("; "),
			})),
			"rule-template.xlsx"
		);
	}

	return {
		exportRulesToExcel,
		importRulesFromExcel,
		exportMatchResultsToExcel,
		createRuleTemplate,
	};
}
