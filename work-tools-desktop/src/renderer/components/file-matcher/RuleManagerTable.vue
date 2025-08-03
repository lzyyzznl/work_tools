<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { type VxeGridInstance, type VxeGridProps } from "vxe-table";
import { useRuleStore } from "../../stores/ruleStore";
import { useErrorHandler } from "../../composables/useErrorHandler";
import type { Rule, RuleColumn } from "../../types/rule";

const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();

// 表格引用
const gridRef = ref<VxeGridInstance<Rule>>();

// 本地状态
const searchQuery = ref("");
const showAddDialog = ref(false);
const newRuleForm = ref({
	code: "",
	matchRules: "",
	columnValues: {} as Record<string, string>,
});
const formErrors = ref<string[]>([]);

// 计算属性
const filteredRules = computed(() => {
	let rules = [...ruleStore.rules];

	// 搜索过滤
	if (searchQuery.value.trim()) {
		const query = searchQuery.value.toLowerCase();
		rules = rules.filter(
			(rule) =>
				rule.code.toLowerCase().includes(query) ||
				rule.matchRules.some((mr) => mr.toLowerCase().includes(query))
		);
	}

	return rules;
});

// Grid配置 - 配置式表格
const gridOptions = computed<VxeGridProps<Rule>>(() => {
	return {
		border: true,
		height: "auto",
		loading: ruleStore.isLoading,
		keepSource: true,
		rowConfig: {
			keyField: "id",
			isCurrent: true,
			isHover: true,
		},
		columnConfig: {
			resizable: true,
		},
		sortConfig: {
			remote: false,
			trigger: "default",
		},
		checkboxConfig: {
			highlight: true,
			reserve: true,
			range: true,
			trigger: "cell",
		},
		editConfig: {
			trigger: "click",
			mode: "cell",
			showStatus: true,
		},
		exportConfig: {},
		scrollX: {
			enabled: true,
			gt: 0,
		},
		scrollY: {
			enabled: true,
			gt: 100,
		},
		className: "rule-table",
		data: filteredRules.value,
		columns: getColumnsConfig(),
	};
});

// 列配置函数
function getColumnsConfig() {
	const columns: any[] = [];

	// 选择列
	columns.push({
		type: "checkbox",
		width: 50,
		fixed: "left",
	});

	// 序号列
	columns.push({
		field: "index",
		title: "序号",
		width: 80,
		align: "center",
		slots: { default: "index-slot" },
	});

	// 代码列（固定列，不可删除）
	columns.push({
		field: "code",
		title: "规则编码",
		minWidth: 150,
		sortable: true,
		editRender: { name: "input", autoselect: true },
	});

	// 匹配规则列（固定列，不可删除）
	columns.push({
		field: "matchRules",
		title: "匹配规则",
		minWidth: 200,
		sortable: true,
		editRender: { name: "input", autoselect: true },
		slots: { default: "match-rules-slot" },
	});

	// 动态列
	ruleStore.visibleColumns.forEach((column) => {
		const columnConfig: any = {
			field: `columnValues.${column.field}`,
			title: column.name,
			minWidth: 120,
			sortable: true,
		};

		// 根据列类型设置编辑渲染器
		if (column.type === "text") {
			columnConfig.editRender = { name: "input", autoselect: true };
		} else if (column.type === "boolean") {
			columnConfig.editRender = {
				name: "select",
				options: [
					{ label: "是", value: "Y" },
					{ label: "否", value: "N" },
				],
			};
		} else if (column.type === "select" && column.options) {
			// 枚举类型列
			const selectOptions = column.options.map((option) => ({
				label: option,
				value: option,
			}));
			columnConfig.editRender = {
				name: "select",
				options: selectOptions,
			};
		} else {
			// 默认使用文本输入
			columnConfig.editRender = { name: "input", autoselect: true };
		}

		columns.push(columnConfig);
	});

	// 操作列（固定在右侧）
	columns.push({
		title: "操作",
		width: 100,
		fixed: "right",
		align: "center",
		slots: { default: "action-slot" },
	});

	return columns;
}

// 格式化匹配规则显示
function formatMatchRules(matchRules: string[] | string): string {
	// 如果是字符串数组，直接连接
	if (Array.isArray(matchRules)) {
		return matchRules.join(", ");
	}
	// 如果是字符串，直接返回
	return matchRules;
}

async function handleEditClosed(params: any) {
	// 编辑关闭时的处理，保存数据
	const { row, column } = params;
	let value = row[column.field];
	if (
		row.columnValues &&
		column.field != "code" &&
		column.field != "matchRules"
	) {
		value = row.columnValues[column.field.replace("columnValues.", "")];
	}
	try {
		// 更新规则
		if (column.field === "code") {
			console.log("更新code字段:", value);
			// 检查代码是否重复
			if (ruleStore.isCodeDuplicate(value, row.id)) {
				throw new Error(`代码 "${value}" 已存在`);
			}
			await ruleStore.updateRule(row.id, { code: value });
		} else if (column.field === "matchRules") {
			console.log("更新matchRules字段:", value);
			// 处理匹配规则更新
			const matchRules = value
				.split(",")
				.map((rule: string) => rule.trim())
				.filter((rule: string) => rule);
			await ruleStore.updateRule(row.id, { matchRules });
		} else if (column.field.startsWith("columnValues.")) {
			console.log("更新columnValues字段:", column.field, value);
			// 处理动态列值更新
			const field = column.field.replace("columnValues.", "");
			const columnValues = { ...row.columnValues, [field]: value };
			await ruleStore.updateRule(row.id, { columnValues });
		}
		console.log("保存成功");
		handleSuccess("规则更新成功");
	} catch (error) {
		console.error("保存失败:", error);
		handleError(error, "更新规则");
		// 恢复旧值
		gridRef.value?.revertData(row);
	}
}

// 表单验证
function validateAddRuleForm(): boolean {
	formErrors.value = [];

	// 验证规则编码
	if (!newRuleForm.value.code || !newRuleForm.value.code.trim()) {
		formErrors.value.push("规则编码不能为空");
	}

	// 验证代码重复
	if (ruleStore.isCodeDuplicate(newRuleForm.value.code.trim())) {
		formErrors.value.push(`规则编码 "${newRuleForm.value.code}" 已存在`);
	}

	// 验证匹配规则
	if (!newRuleForm.value.matchRules || !newRuleForm.value.matchRules.trim()) {
		formErrors.value.push("至少需要一个匹配规则");
	} else {
		const validRules = newRuleForm.value.matchRules
			.split(",")
			.map((rule) => rule.trim())
			.filter((rule) => rule);
		if (validRules.length === 0) {
			formErrors.value.push("至少需要一个有效的匹配规则");
		}
	}

	return formErrors.value.length === 0;
}

// 重置表单
function resetAddRuleForm() {
	newRuleForm.value = {
		code: "",
		matchRules: "",
		columnValues: {},
	};
	formErrors.value = [];
}

// 新增规则
async function addNewRule() {
	resetAddRuleForm();
	showAddDialog.value = true;
}

// 处理弹窗提交
async function handleSubmitAddRule() {
	if (!validateAddRuleForm()) {
		return;
	}

	try {
		const matchRules = newRuleForm.value.matchRules
			.split(",")
			.map((rule) => rule.trim())
			.filter((rule) => rule);

		const ruleData = {
			code: newRuleForm.value.code.trim(),
			matchRules,
			columnValues: newRuleForm.value.columnValues,
		};

		await ruleStore.addRule(ruleData);
		handleSuccess("规则新增成功");
		showAddDialog.value = false;
	} catch (error) {
		handleError(error, "新增规则");
	}
}

// 处理弹窗取消
function handleCancelAddRule() {
	showAddDialog.value = false;
	resetAddRuleForm();
}

// 删除单行规则
async function deleteRow(row: Rule) {
	if (confirm(`确定要删除规则 "${row.code || "未命名"}" 吗？`)) {
		try {
			await ruleStore.deleteRule(row.id);
			// 从表格中移除行
			const $grid = gridRef.value;
			if ($grid) {
				await $grid.remove(row);
			}
			handleSuccess("规则删除成功");
		} catch (error) {
			handleError(error, "删除规则");
		}
	}
}

// 删除选中规则
async function deleteSelectedRules() {
	const selectedRecords = gridRef.value?.getCheckboxRecords() || [];
	if (selectedRecords.length === 0) return;

	if (confirm(`确定要删除选中的 ${selectedRecords.length} 个规则吗？`)) {
		try {
			for (const rule of selectedRecords) {
				await ruleStore.deleteRule(rule.id);
			}
			handleSuccess(`成功删除 ${selectedRecords.length} 个规则`);
		} catch (error) {
			handleError(error, "删除规则");
		}
	}
}

// 自定义导出 CSV 文件
async function exportCSV() {
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("Grid 引用为空，无法导出");
		return;
	}

	try {
		console.log("开始自定义 CSV 导出");

		// 获取表格数据
		const tableData = $grid.getTableData();
		const { fullData } = tableData;

		console.log("获取到表格数据条数:", fullData.length);

		if (fullData.length === 0) {
			console.warn("没有数据可导出");
			return;
		}

		// 生成 CSV 内容
		const csvContent = generateCSVContent(fullData);
		console.log("CSV 内容生成完成，长度:", csvContent.length);

		// 调用 Electron 文件保存对话框
		const result = await (window as any).electronAPI?.dialog?.showSaveDialog({
			defaultPath: `rules-export-${new Date().toISOString().split("T")[0]}.csv`,
			filters: [
				{ name: "CSV Files", extensions: ["csv"] },
				{ name: "All Files", extensions: ["*"] },
			],
		});

		console.log("文件保存对话框结果:", result);

		if (!result.canceled && result.filePath) {
			// 将 CSV 内容转换为 ArrayBuffer
			const encoder = new TextEncoder();
			const csvBuffer = encoder.encode(csvContent);

			// 写入文件
			const writeResult = await (
				window as any
			).electronAPI?.fileSystem?.writeFile(result.filePath, csvBuffer);

			console.log("文件写入结果:", writeResult);

			if (writeResult?.success) {
				console.log("✅ CSV 导出成功:", result.filePath);
				handleSuccess("规则导出成功");
			} else {
				console.error("❌ CSV 导出失败:", writeResult);
				handleError(new Error("导出失败"), "导出规则");
			}
		}
	} catch (error) {
		console.error("自定义 CSV 导出出错:", error);
		handleError(error, "导出规则");
	}
}

// 生成 CSV 内容
function generateCSVContent(data: Rule[]): string {
	console.log("开始生成CSV内容");

	// 获取当前表格的实时列配置
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("Grid引用为空");
		return "";
	}

	// 获取当前显示的列配置
	const tableColumns = $grid.getColumns();
	console.log(
		"当前表格列配置:",
		tableColumns.map((col) => ({
			field: col.field,
			title: col.title,
			type: col.type,
			visible: col.visible,
		}))
	);

	// 根据实时列配置生成表头
	const headers: string[] = [];
	const validColumns = tableColumns.filter(
		(col) => col.visible !== false && col.type !== "checkbox" && col.title
	);

	console.log(
		"有效导出列:",
		validColumns.map((col) => ({
			field: col.field,
			title: col.title,
		}))
	);

	validColumns.forEach((col) => {
		headers.push(col.title || col.field || "");
	});

	console.log("实时生成的表头:", headers);

	// 转义 CSV 字段
	const escapeCSVField = (field: string): string => {
		if (field.includes(",") || field.includes('"') || field.includes("\n")) {
			return `"${field.replace(/"/g, '""')}"`;
		}
		return field;
	};

	// 生成 CSV 行
	const csvRows = [headers.map(escapeCSVField).join(",")];

	data.forEach((rule, index) => {
		console.log("处理规则:", rule.code, "索引:", index);

		// 根据实时列配置生成数据行
		const row: string[] = [];

		validColumns.forEach((col) => {
			let cellValue = "";

			switch (col.field) {
				case "index":
					cellValue = (index + 1).toString();
					break;
				case "code":
					cellValue = escapeCSVField(rule.code);
					break;
				case "matchRules":
					cellValue = escapeCSVField(formatMatchRules(rule.matchRules));
					break;
				default:
					// 处理动态列
					if (col.field.startsWith("columnValues.")) {
						const field = col.field.replace("columnValues.", "");
						cellValue = escapeCSVField(rule.columnValues?.[field] || "");
					} else {
						cellValue = "";
					}
			}

			row.push(cellValue);
		});

		console.log("生成的数据行:", row);
		csvRows.push(row.join(","));
	});

	return csvRows.join("\n");
}

// 导入CSV文件
async function importCSV(event: Event) {
	const input = event.target as HTMLInputElement;
	const file = input.files?.[0];
	if (!file) return;

	try {
		const text = await file.text();
		await parseCSVAndImport(text);
		handleSuccess("规则导入成功");
	} catch (error) {
		handleError(error, "导入规则");
	} finally {
		input.value = "";
	}
}

// 解析CSV并导入
async function parseCSVAndImport(csvContent: string) {
	const lines = csvContent.split("\n");
	if (lines.length < 2) {
		throw new Error("CSV文件格式不正确");
	}

	// 解析表头
	const headers = lines[0]
		.split(",")
		.map((h) => h.trim().replace(/^"(.*)"$/, "$1"));
	console.log("CSV表头:", headers);

	// 获取现有的列配置
	const existingColumns = [...ruleStore.columns];

	// 固定列映射
	const codeIndex = headers.findIndex(
		(h) => h === "规则编码" || h === "规则编码" || h === "code" || h === "Code"
	);
	const matchRulesIndex = headers.findIndex(
		(h) =>
			h === "匹配规则" ||
			h === "matchRules" ||
			h === "Match Rules" ||
			h === "规则"
	);

	if (codeIndex === -1) {
		throw new Error(
			"CSV文件中未找到规则编码列，请确保包含'规则编码'、'规则编码'或'code'列"
		);
	}
	if (matchRulesIndex === -1) {
		throw new Error(
			"CSV文件中未找到匹配规则列，请确保包含'匹配规则'、'matchRules'或'规则'列"
		);
	}

	// 查找动态列并添加新列
	const newColumnsToAdd: Array<Omit<RuleColumn, "id">> = [];
	headers.forEach((header, index) => {
		// 跳过固定列
		if (index === codeIndex || index === matchRulesIndex) {
			return;
		}

		// 检查是否已存在该列（按名称匹配）
		const existingColumn = existingColumns.find(
			(col) => col.name === header || col.field === header
		);
		if (!existingColumn) {
			// 添加新列到待添加列表，直接使用表头作为字段名
			const newColumn: Omit<RuleColumn, "id"> = {
				name: header,
				field: header, // 直接使用表头作为字段名
				type: "text", // 默认为文本类型
				visible: true,
				order: existingColumns.length + newColumnsToAdd.length,
			};
			newColumnsToAdd.push(newColumn);
		}
	});

	// 批量添加新列
	for (const newColumn of newColumnsToAdd) {
		ruleStore.addColumn(newColumn);
	}

	// 解析数据行并导入规则
	for (let i = 1; i < lines.length; i++) {
		const line = lines[i].trim();
		if (!line) continue;

		const values = line
			.split(",")
			.map((v) => v.trim().replace(/^"(.*)"$/, "$1"));
		if (values.length !== headers.length) {
			console.warn(`第${i + 1}行数据列数不匹配，跳过`);
			continue;
		}

		// 构造规则对象
		const ruleData: any = {
			code: values[codeIndex] || "",
			matchRules: values[matchRulesIndex]
				? values[matchRulesIndex]
						.split(",")
						.map((r) => r.trim())
						.filter((r) => r)
				: [],
			columnValues: {},
		};

		// 处理动态列值 - 直接使用表头作为字段名
		headers.forEach((header, index) => {
			// 跳过固定列
			if (index === codeIndex || index === matchRulesIndex) {
				return;
			}

			// 直接使用表头作为字段名映射
			ruleData.columnValues[header] = values[index] || "";
		});

		// 检查是否已存在相同代码的规则
		if (ruleStore.isCodeDuplicate(ruleData.code)) {
			// 更新现有规则
			const existingRule = ruleStore.rules.find(
				(r) => r.code === ruleData.code
			);
			if (existingRule) {
				await ruleStore.updateRule(existingRule.id, ruleData);
			}
		} else {
			// 添加新规则
			await ruleStore.addRule(ruleData);
		}
	}
}

// 暴露方法给父组件
defineExpose({
	exportCSV,
});

// 组件挂载时加载规则
onMounted(async () => {
	try {
		await ruleStore.loadRules();
	} catch (error) {
		handleError(error, "加载规则");
	}
});
</script>

<template>
	<div class="rule-manager-table flex flex-col h-full">
		<!-- 搜索栏 -->
		<div class="search-bar p-4 border-b border-gray-200">
			<div class="relative">
				<input
					v-model="searchQuery"
					type="text"
					placeholder="搜索规则编码或匹配规则..."
					class="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
				<div
					class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
				>
					<span class="text-gray-400">🔍</span>
				</div>
				<div
					v-if="searchQuery"
					class="absolute inset-y-0 right-0 pr-3 flex items-center"
				>
					<button
						@click="searchQuery = ''"
						class="text-gray-400 hover:text-gray-600 focus:outline-none"
					>
						<span>✕</span>
					</button>
				</div>
			</div>
		</div>

		<!-- 工具栏 -->
		<div class="toolbar p-4 border-b border-gray-200 flex gap-2">
			<button
				@click="addNewRule"
				class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
			>
				新增规则
			</button>
			<button
				@click="deleteSelectedRules"
				class="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
			>
				删除选中
			</button>
		</div>

		<!-- 规则表格 -->
		<div class="table-container flex-1 overflow-hidden">
			<vxe-grid
				ref="gridRef"
				v-bind="gridOptions"
				@edit-closed="handleEditClosed"
			>
				<!-- 自定义插槽 -->
				<template #index-slot="{ rowIndex }">
					<span class="text-gray-500">
						{{ rowIndex + 1 }}
					</span>
				</template>

				<template #match-rules-slot="{ row }">
					<span class="text-gray-700">
						{{ formatMatchRules(row.matchRules) }}
					</span>
				</template>

				<template #action-slot="{ row }">
					<button
						@click="deleteRow(row)"
						class="text-red-500 hover:text-red-700 focus:outline-none"
						title="删除"
					>
						删除
					</button>
				</template>
			</vxe-grid>
		</div>

		<!-- 新增规则弹窗 -->
		<div
			v-if="showAddDialog"
			class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
		>
			<div
				class="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-hidden"
			>
				<!-- 弹窗头部 -->
				<div
					class="flex items-center justify-between p-4 border-b border-gray-200"
				>
					<h3 class="text-lg font-medium text-gray-900">新增规则</h3>
					<button
						@click="handleCancelAddRule"
						class="text-gray-400 hover:text-gray-600 focus:outline-none"
					>
						<span class="text-xl">×</span>
					</button>
				</div>

				<!-- 弹窗内容 -->
				<div class="p-4 overflow-y-auto max-h-[calc(90vh-120px)]">
					<!-- 错误提示 -->
					<div
						v-if="formErrors.length > 0"
						class="mb-4 p-3 bg-red-50 border border-red-200 rounded-md"
					>
						<div class="text-sm text-red-600">
							<div v-for="error in formErrors" :key="error" class="mb-1">
								{{ error }}
							</div>
						</div>
					</div>

					<!-- 表单字段 -->
					<div class="space-y-4">
						<!-- 规则编码 -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								规则编码 <span class="text-red-500">*</span>
							</label>
							<input
								v-model="newRuleForm.code"
								type="text"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="请输入规则编码"
							/>
						</div>

						<!-- 匹配规则 -->
						<div>
							<label class="block text-sm font-medium text-gray-700 mb-1">
								匹配规则 <span class="text-red-500">*</span>
							</label>
							<input
								v-model="newRuleForm.matchRules"
								type="text"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								placeholder="请输入匹配规则，多个规则用逗号分隔"
							/>
							<div class="text-xs text-gray-500 mt-1">
								多个匹配规则请用逗号分隔，例如：*.jpg,*.png
							</div>
						</div>

						<!-- 动态列 -->
						<div v-for="column in ruleStore.visibleColumns" :key="column.id">
							<label class="block text-sm font-medium text-gray-700 mb-1">
								{{ column.name }}
							</label>
							<!-- 文本类型 -->
							<input
								v-if="column.type === 'text'"
								v-model="newRuleForm.columnValues[column.field]"
								type="text"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								:placeholder="`请输入${column.name}`"
							/>
							<!-- 布尔类型 -->
							<select
								v-else-if="column.type === 'boolean'"
								v-model="newRuleForm.columnValues[column.field]"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							>
								<option value="">请选择</option>
								<option value="Y">是</option>
								<option value="N">否</option>
							</select>
							<!-- 枚举类型 -->
							<select
								v-else-if="column.type === 'select' && column.options"
								v-model="newRuleForm.columnValues[column.field]"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							>
								<option value="">请选择</option>
								<option
									v-for="option in column.options"
									:key="option"
									:value="option"
								>
									{{ option }}
								</option>
							</select>
							<!-- 默认文本类型 -->
							<input
								v-else
								v-model="newRuleForm.columnValues[column.field]"
								type="text"
								class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								:placeholder="`请输入${column.name}`"
							/>
						</div>
					</div>
				</div>

				<!-- 弹窗底部 -->
				<div class="flex justify-end gap-2 p-4 border-t border-gray-200">
					<button
						@click="handleCancelAddRule"
						class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
					>
						取消
					</button>
					<button
						@click="handleSubmitAddRule"
						class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
					>
						确定
					</button>
				</div>
			</div>
		</div>
	</div>
</template>

<style scoped>
/* 弹窗样式优化 */
.rule-manager-table {
	position: relative;
}

/* 弹窗动画效果 */
.fixed {
	backdrop-filter: blur(2px);
}

/* 弹窗内容滚动条样式 */
.overflow-y-auto::-webkit-scrollbar {
	width: 6px;
}

.overflow-y-auto::-webkit-scrollbar-track {
	background: #f1f1f1;
	border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb {
	background: #c1c1c1;
	border-radius: 3px;
}

.overflow-y-auto::-webkit-scrollbar-thumb:hover {
	background: #a8a8a8;
}

/* 表单输入框焦点样式 */
input:focus,
select:focus {
	outline: none;
	box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* 按钮悬停效果 */
button {
	transition: all 0.2s ease;
}

/* 错误提示动画 */
.bg-red-50 {
	animation: slideIn 0.3s ease-out;
}

@keyframes slideIn {
	from {
		opacity: 0;
		transform: translateY(-10px);
	}
	to {
		opacity: 1;
		transform: translateY(0);
	}
}
</style>
