<script setup lang="ts">
import { computed, ref } from "vue";
import { type VxeGridInstance, type VxeGridProps } from "vxe-table";
import { useFileSystem } from "../../composables/useFileSystem";
import { useFileStore } from "../../stores/fileStore";
import type { FileItem } from "../../types/file";

// Props
interface ColumnConfig {
	field: string;
	title: string;
	width?: number | string;
	minWidth?: number | string;
	sortable?: boolean;
	align?: string;
	editRender?: any;
	slots?: any;
	visible?: boolean;
	[key: string]: any; // 允许其他 vxe-table 列配置属性
}

interface Props {
	showMatchInfo?: boolean;
	showPreview?: boolean;
	showSelection?: boolean;
	fileStore?: any; // 可选的外部store实例
	columns?: ColumnConfig[]; // 动态列配置
}

const props = withDefaults(defineProps<Props>(), {
	showMatchInfo: false,
	showPreview: false,
	showSelection: true,
	fileStore: undefined,
});

// Emits
const emit = defineEmits<{
	(e: "file-selected", file: FileItem): void;
	(e: "selection-changed", selectedFiles: FileItem[]): void;
}>();

// 状态管理
const internalFileStore = useFileStore();
const fileStore = computed(() => props.fileStore || internalFileStore);
const { formatFileSize } = useFileSystem();

// 表格引用
const gridRef = ref<VxeGridInstance<FileItem>>();

// 本地状态
const searchQuery = ref("");

// 计算属性
const filteredFiles = computed(() => {
	let files = [...fileStore.value.files];

	// 搜索过滤
	if (searchQuery.value.trim()) {
		const query = searchQuery.value.toLowerCase();
		files = files.filter(
			(file) =>
				file.name.toLowerCase().includes(query) ||
				file.path.toLowerCase().includes(query) ||
				(file.matchInfo?.matchedRule &&
					file.matchInfo.matchedRule.toLowerCase().includes(query))
		);
	}

	return files;
});

// Grid配置 - 配置式表格
const gridOptions = computed<VxeGridProps<FileItem>>(() => {
	return {
		border: true,
		height: "auto",
		loading: fileStore.value.isLoading,
		keepSource: true, // 添加 keep-source 配置
		rowConfig: {
			keyField: "id", // 添加唯一键字段，解决 row-config.keyField 警告
			isCurrent: true,
			isHover: true,
			drag: true, // 启用行拖拽
			dragSort: true, // 启用行拖拽排序
		},
		columnConfig: {
			resizable: true,
			drag: true, // 启用列拖拽
		},
		sortConfig: {
			remote: false, // 本地排序，让 VXE Table 处理
			trigger: "default",
		},
		checkboxConfig: props.showSelection
			? {
					highlight: true,
					reserve: true,
					range: true,
					trigger: "cell",
			  }
			: undefined,
		editConfig: {
			trigger: "click",
			mode: "cell",
		},
		scrollX: {
			enabled: true,
			gt: 0,
		},
		scrollY: {
			enabled: true,
			gt: 100,
		},
		className: "file-table",
		data: filteredFiles.value,
		columns: getColumnsConfig(),
	};
});

// 列配置函数
function getColumnsConfig() {
	// 如果传入了动态列配置，则使用动态配置
	const finalConls: any[] = [];
	// 选择列
	if (props.showSelection) {
		finalConls.push({
			type: "checkbox",
			width: 50,
			fixed: "left",
		});
	}

	// 序号列 - 作为第一列，添加拖拽排序配置
	finalConls.push({
		field: "index",
		title: "序号",
		width: 80,
		align: "center",
		dragSort: true, // 启用序号列拖拽排序
		slots: { default: "index-slot" },
	});

	// 文件名列
	finalConls.push({
		field: "name",
		title: "文件名",
		minWidth: 200,
		sortable: true,
		editRender: { name: "input", autoselect: true },
		slots: { default: "name-slot", edit: "name-edit-slot" },
	});

	// 文件大小列
	finalConls.push({
		field: "size",
		title: "大小",
		width: 120,
		sortable: true,
		align: "right",
		slots: { default: "size-slot" },
	});

	// 最后修改时间列
	finalConls.push({
		field: "lastModified",
		title: "修改时间",
		width: 180,
		sortable: true,
		slots: { default: "date-slot" },
	});

	// 匹配信息列
	if (props.showMatchInfo) {
		finalConls.push({
			field: "matchInfo",
			title: "匹配结果",
			width: 150,
			sortable: true,
			slots: { default: "match-slot" },
		});
	}

	// 预览名称列
	if (props.showPreview) {
		finalConls.push({
			field: "previewName",
			title: "预览名称",
			minWidth: 200,
			slots: { default: "preview-slot" },
		});
	}

	if (props.columns && props.columns.length > 0) {
		// 添加动态列配置
		props.columns.forEach((col) => {
			// 为规则动态列添加插槽配置
			const columnConfig = {
				...col,
				slots: { default: `${col.field}-slot` },
			};
			finalConls.push(columnConfig);
		});
	}
	return finalConls;
}

function handleSelectChange() {
	const selectedRecords = gridRef.value?.getCheckboxRecords() || [];
	emit("selection-changed", selectedRecords as FileItem[]);
}

function handleCurrentChange(params: any) {
	const { row } = params;
	if (row) {
		emit("file-selected", row as FileItem);
	}
}

function formatDate(timestamp: number): string {
	return new Date(timestamp).toLocaleString("zh-CN");
}

function getMatchStatusText(file: FileItem): string {
	if (!file.matched) return "未匹配";
	return file.matchInfo?.matchedRule || "已匹配";
}

function getMatchStatusClass(file: FileItem): string {
	return file.matched ? "text-green-600 font-medium" : "text-gray-500";
}

// 编辑相关方法
function handleNameEditComplete(row: FileItem) {
	// 触发表格退出编辑状态
	gridRef.value?.clearEdit();

	// 更新文件存储中的数据
	const fileIndex = fileStore.value.files.findIndex(
		(file: FileItem) => file.id === row.id
	);
	if (fileIndex !== -1) {
		// 创建新的文件数组以触发响应式更新
		const newFiles = [...fileStore.value.files];
		newFiles[fileIndex] = { ...row };
		fileStore.value.files = newFiles;
	}
}

// 拖拽排序相关方法 - 让 VXE Table 自己处理拖拽排序
function handleRowDragStart(params: any) {
	console.log("🔧 [DEBUG] VXE Table 拖拽开始:", params);
}

function handleRowDragEnd(params: any) {
	console.log("🔧 [DEBUG] VXE Table 拖拽结束:", params);
	// VXE Table 会自动更新数据顺序，我们需要同步到 fileStore
	const newData = gridRef.value?.getTableData().fullData || [];
	fileStore.value.files = [...newData];
	console.log(
		"🔧 [DEBUG] 同步拖拽结果到 fileStore，前5个文件:",
		newData.slice(0, 5).map((f: any) => f.name)
	);
}

// 公共方法
function selectAll() {
	if (!props.showSelection) return;
	gridRef.value?.setAllCheckboxRow(true);
	handleSelectChange();
}

function unselectAll() {
	if (!props.showSelection) return;
	gridRef.value?.setAllCheckboxRow(false);
	handleSelectChange();
}

function getSelectedFiles(): FileItem[] {
	return (gridRef.value?.getCheckboxRecords() || []) as FileItem[];
}

function setSearchQuery(query: string) {
	searchQuery.value = query;
}

// 自定义导出 CSV 文件 - 适配 Electron 环境
async function exportCSV() {
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("🔧 [DEBUG] Grid 引用为空，无法导出");
		return;
	}

	try {
		console.log("🔧 [DEBUG] 开始自定义 CSV 导出");

		// 获取表格数据
		const tableData = $grid.getTableData();
		const { fullData } = tableData;

		console.log("🔧 [DEBUG] 获取到表格数据条数:", fullData.length);

		if (fullData.length === 0) {
			console.warn("🔧 [DEBUG] 没有数据可导出");
			return;
		}

		// 生成 CSV 内容
		const csvContent = generateCSVContent(fullData);
		console.log("🔧 [DEBUG] CSV 内容生成完成，长度:", csvContent.length);

		// 调用 Electron 文件保存对话框
		const result = await (window as any).electronAPI?.dialog?.showSaveDialog({
			defaultPath: "file_table_export.csv",
			filters: [
				{ name: "CSV Files", extensions: ["csv"] },
				{ name: "All Files", extensions: ["*"] },
			],
		});

		console.log("🔧 [DEBUG] 文件保存对话框结果:", result);

		if (!result.canceled && result.filePath) {
			// 将 CSV 内容转换为 ArrayBuffer
			const encoder = new TextEncoder();
			const csvBuffer = encoder.encode(csvContent);

			// 写入文件
			const writeResult = await (
				window as any
			).electronAPI?.fileSystem?.writeFile(result.filePath, csvBuffer);

			console.log("🔧 [DEBUG] 文件写入结果:", writeResult);

			if (writeResult?.success) {
				console.log("✅ CSV 导出成功:", result.filePath);
			} else {
				console.error("❌ CSV 导出失败:", writeResult);
			}
		}
	} catch (error) {
		console.error("🔧 [DEBUG] 自定义 CSV 导出出错:", error);
	}
}

// 生成 CSV 内容
function generateCSVContent(data: FileItem[]): string {
	console.log("🔧 [DEBUG] 开始生成CSV内容");

	// 获取当前表格的实时列配置
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("🔧 [DEBUG] Grid引用为空");
		return "";
	}

	// 获取当前显示的列配置（考虑拖拽排序）
	const tableColumns = $grid.getColumns();
	console.log(
		"🔧 [DEBUG] 当前表格列配置:",
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
		"🔧 [DEBUG] 有效导出列:",
		validColumns.map((col) => ({
			field: col.field,
			title: col.title,
		}))
	);

	validColumns.forEach((col) => {
		headers.push(col.title || col.field || "");
	});

	console.log("🔧 [DEBUG] 实时生成的表头:", headers);

	// 转义 CSV 字段
	const escapeCSVField = (field: string): string => {
		if (field.includes(",") || field.includes('"') || field.includes("\n")) {
			return `"${field.replace(/"/g, '""')}"`;
		}
		return field;
	};

	// 生成 CSV 行
	const csvRows = [headers.map(escapeCSVField).join(",")];

	data.forEach((file, index) => {
		console.log("🔧 [DEBUG] 处理文件:", file.name, "索引:", index);

		// 根据实时列配置生成数据行
		const row: string[] = [];

		validColumns.forEach((col) => {
			let cellValue = "";

			switch (col.field) {
				case "index":
					cellValue = (index + 1).toString();
					break;
				case "name":
					cellValue = escapeCSVField(file.name);
					break;
				case "size":
					cellValue = formatFileSize(file.size);
					break;
				case "lastModified":
					cellValue = formatDate(file.lastModified);
					break;
				case "matchInfo":
					cellValue = escapeCSVField(getMatchStatusText(file));
					break;
				case "previewName":
					cellValue = escapeCSVField(file.previewName || "");
					break;
				default:
					// 处理动态列 - 从 matchInfo.columnValues 中获取值
					if (file.matched && file.matchInfo?.columnValues?.[col.field]) {
						cellValue = escapeCSVField(file.matchInfo.columnValues[col.field]);
					} else {
						cellValue = "-";
					}
					break;
			}

			row.push(cellValue);
		});

		console.log("🔧 [DEBUG] 生成的数据行:", row);
		csvRows.push(row.join(","));
	});

	return csvRows.join("\n");
}

// 自定义导出功能 - 适配 Electron 环境，支持CSV和TXT格式
async function exportData(type: "csv" | "txt" = "csv") {
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("🔧 [DEBUG] Grid 引用为空，无法导出");
		return;
	}

	try {
		console.log(`🔧 [DEBUG] 开始自定义 ${type.toUpperCase()} 导出`);

		// 获取表格数据
		const tableData = $grid.getTableData();
		const { fullData } = tableData;

		if (fullData.length === 0) {
			console.warn("🔧 [DEBUG] 没有数据可导出");
			return;
		}

		// 根据类型生成不同格式的内容
		let content: string;
		let extension: string;
		let filterName: string;

		switch (type) {
			case "csv":
				content = generateCSVContent(fullData);
				extension = "csv";
				filterName = "CSV Files";
				break;
			case "txt":
				content = generateTXTContent(fullData);
				extension = "txt";
				filterName = "Text Files";
				break;
			default:
				content = generateCSVContent(fullData);
				extension = "csv";
				filterName = "CSV Files";
		}

		// 调用 Electron 文件保存对话框
		const result = await (window as any).electronAPI?.dialog?.showSaveDialog({
			defaultPath: `file_table_export.${extension}`,
			filters: [
				{ name: filterName, extensions: [extension] },
				{ name: "All Files", extensions: ["*"] },
			],
		});

		if (!result.canceled && result.filePath) {
			// 将内容转换为 ArrayBuffer
			const encoder = new TextEncoder();
			const buffer = encoder.encode(content);

			// 写入文件
			const writeResult = await (
				window as any
			).electronAPI?.fileSystem?.writeFile(result.filePath, buffer);

			if (writeResult?.success) {
				console.log(`✅ ${type.toUpperCase()} 导出成功:`, result.filePath);
			} else {
				console.error(`❌ ${type.toUpperCase()} 导出失败:`, writeResult);
			}
		}
	} catch (error) {
		console.error(`🔧 [DEBUG] 自定义 ${type.toUpperCase()} 导出出错:`, error);
	}
}

// 生成 TXT 内容
function generateTXTContent(data: FileItem[]): string {
	console.log("🔧 [DEBUG] 开始生成TXT内容");

	// 获取当前表格的实时列配置
	const $grid = gridRef.value;
	if (!$grid) {
		console.error("🔧 [DEBUG] Grid引用为空");
		return "";
	}

	// 获取当前显示的列配置（考虑拖拽排序）
	const tableColumns = $grid.getColumns();
	console.log(
		"🔧 [DEBUG] TXT导出-当前表格列配置:",
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

	validColumns.forEach((col) => {
		headers.push(col.title || col.field || "");
	});

	console.log("🔧 [DEBUG] TXT导出-实时生成的表头:", headers);

	let txt = headers.join("\t") + "\n";
	txt += headers.map(() => "---").join("\t") + "\n";

	data.forEach((file, index) => {
		console.log("🔧 [DEBUG] TXT导出-处理文件:", file.name, "索引:", index);

		// 根据实时列配置生成数据行
		const cells: string[] = [];

		validColumns.forEach((col) => {
			let cellValue = "";

			switch (col.field) {
				case "index":
					cellValue = (index + 1).toString();
					break;
				case "name":
					cellValue = file.name;
					break;
				case "size":
					cellValue = formatFileSize(file.size);
					break;
				case "lastModified":
					cellValue = formatDate(file.lastModified);
					break;
				case "matchInfo":
					cellValue = getMatchStatusText(file);
					break;
				case "previewName":
					cellValue = file.previewName || "";
					break;
				default:
					// 处理动态列 - 从 matchInfo.columnValues 中获取值
					if (file.matched && file.matchInfo?.columnValues?.[col.field]) {
						cellValue = file.matchInfo.columnValues[col.field];
					} else {
						cellValue = "-";
					}
					break;
			}

			cells.push(cellValue);
		});

		console.log("🔧 [DEBUG] TXT导出-生成的数据行:", cells);
		txt += cells.join("\t") + "\n";
	});

	return txt;
}

// 暴露方法给父组件
defineExpose({
	selectAll,
	unselectAll,
	getSelectedFiles,
	setSearchQuery,
	exportCSV,
	exportData,
});

// VXE Table 通过配置自动处理数据响应，无需手动监听
</script>

<template>
	<div class="file-table-container flex flex-col h-full">
		<!-- 搜索栏 -->
		<div
			class="search-bar p-lg border-b border-border-primary bg-background-secondary"
		>
			<div class="relative">
				<input
					v-model="searchQuery"
					type="text"
					placeholder="搜索文件名、路径或匹配信息..."
					class="input-base w-full pl-10 pr-4"
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

		<!-- 文件表格 -->
		<div
			v-if="filteredFiles.length > 0"
			class="table-container flex-1 overflow-hidden"
		>
			<vxe-grid
				ref="gridRef"
				v-bind="gridOptions"
				@checkbox-change="handleSelectChange"
				@checkbox-all="handleSelectChange"
				@current-change="handleCurrentChange"
				@row-dragstart="handleRowDragStart"
				@row-dragend="handleRowDragEnd"
			>
				<!-- 自定义插槽 -->
				<template #index-slot="{ rowIndex }">
					<span class="text-text-secondary font-medium">
						{{ rowIndex + 1 }}
					</span>
				</template>

				<template #name-slot="{ row }">
					<div class="flex items-center">
						<span class="mr-2">📄</span>
						<span
							class="truncate font-medium text-text-primary"
							:title="row.name"
						>
							{{ row.name }}
						</span>
					</div>
				</template>

				<template #name-edit-slot="{ row }">
					<input
						v-model="row.name"
						type="text"
						class="input-base w-full"
						@blur="handleNameEditComplete(row)"
						@keydown.enter="handleNameEditComplete(row)"
					/>
				</template>

				<template #size-slot="{ row }">
					<span class="text-text-secondary">
						{{ formatFileSize(row.size) }}
					</span>
				</template>

				<template #date-slot="{ row }">
					<span class="text-text-secondary">
						{{ formatDate(row.lastModified) }}
					</span>
				</template>

				<template #match-slot="{ row }">
					<span :class="getMatchStatusClass(row)">
						{{ getMatchStatusText(row) }}
					</span>
				</template>

				<template #preview-slot="{ row }">
					<span
						v-if="row.previewName"
						class="text-text-secondary italic"
						:title="row.previewName"
					>
						{{ row.previewName }}
					</span>
					<span v-else class="text-text-tertiary italic"> 无预览 </span>
				</template>

				<!-- 动态生成的规则列插槽 -->
				<template
					v-for="column in props.columns"
					:key="column.field"
					#[`${column.field}-slot`]="{ row }"
				>
					<span
						v-if="row.matched && row.matchInfo?.columnValues?.[column.field]"
					>
						{{ row.matchInfo.columnValues[column.field] }}
					</span>
					<span v-else class="text-text-tertiary">-</span>
				</template>
			</vxe-grid>
		</div>

		<!-- 空状态 -->
		<div
			v-else
			class="empty-state flex-1 flex flex-col items-center justify-center p-12 text-center"
		>
			<div class="text-6xl mb-6 opacity-50">📁</div>
			<div class="text-lg font-medium text-text-secondary mb-2">
				{{ searchQuery ? "未找到匹配的文件" : "暂无文件" }}
			</div>
			<div class="text-sm text-text-tertiary">
				{{ searchQuery ? "尝试调整搜索条件" : "请选择文件或拖拽文件到此处" }}
			</div>
			<slot name="empty"></slot>
		</div>
	</div>
</template>

<style scoped>
/* 使用 UnoCSS 样式，无需额外的 CSS */
</style>
