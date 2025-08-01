<script setup lang="ts">
import { computed, nextTick, ref, watch } from "vue";
import { type VxeGridInstance, type VxeGridProps } from "vxe-table";
import { useFileSystem } from "../../composables/useFileSystem";
import { useFileStore } from "../../stores/fileStore";
import type { FileItem } from "../../types/file";

// Props
interface Props {
	showMatchInfo?: boolean;
	showPreview?: boolean;
	showSelection?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	showMatchInfo: false,
	showPreview: false,
	showSelection: true,
});

// Emits
const emit = defineEmits<{
	(e: "file-selected", file: FileItem): void;
	(e: "selection-changed", selectedFiles: FileItem[]): void;
	(e: "sort-changed", field: string, order: "asc" | "desc"): void;
	(e: "batch-operation", operation: string, selectedFiles: FileItem[]): void;
}>();

// 状态管理
const fileStore = useFileStore();
const { formatFileSize } = useFileSystem();

// 表格引用
const gridRef = ref<VxeGridInstance<FileItem>>();

// 导出接口实现
async function exportFileApi(body: any) {
	console.log("获取导出参数", body);

	try {
		let blob: Blob;
		let filename =
			body.filename || `file-export-${new Date().toISOString().slice(0, 10)}`;

		// 获取实际的表格数据
		const tableData = sortedFiles.value;
		const fields = body.fields || [];

		console.log("准备导出的数据量:", tableData.length);
		console.log("导出字段:", fields);

		// 根据模式确定导出的数据
		let exportData = tableData;
		if (body.mode.includes("selected") && body.ids && body.ids.length > 0) {
			exportData = tableData.filter((item) => body.ids.includes(item.id));
		}

		console.log("实际导出数据量:", exportData.length);

		if (body.mode.includes("Csv")) {
			// CSV导出
			let csvContent = "";

			// 添加列标题
			if (body.isHeader !== false) {
				csvContent +=
					fields
						.map((field: any) => `"${field.title || field.field}"`)
						.join(",") + "\n";
			}

			// 添加数据行
			exportData.forEach((row: any) => {
				const values = fields.map((field: any) => {
					let value = "";
					if (field.field === "size") {
						value = formatFileSize(row[field.field] || 0);
					} else if (field.field === "lastModified") {
						value = formatDate(row[field.field] || 0);
					} else if (field.field === "matchInfo") {
						value = getMatchStatusText(row);
					} else {
						value = row[field.field] || "";
					}
					// 处理包含逗号、引号或换行符的值
					return `"${String(value).replace(/"/g, '""')}"`;
				});
				csvContent += values.join(",") + "\n";
			});

			blob = new Blob([csvContent], { type: "text/csv;charset=utf-8" });

			if (!filename.endsWith(".csv")) {
				filename += ".csv";
			}
		} else {
			// 默认文本格式 (txt)
			let textContent = "";

			// 添加列标题
			if (body.isHeader !== false) {
				textContent +=
					fields.map((field: any) => field.title || field.field).join("\t") +
					"\n";
			}

			// 添加数据行
			exportData.forEach((row: any) => {
				const values = fields.map((field: any) => {
					let value = "";
					if (field.field === "size") {
						value = formatFileSize(row[field.field] || 0);
					} else if (field.field === "lastModified") {
						value = formatDate(row[field.field] || 0);
					} else if (field.field === "matchInfo") {
						value = getMatchStatusText(row);
					} else {
						value = row[field.field] || "";
					}
					return value;
				});
				textContent += values.join("\t") + "\n";
			});

			blob = new Blob([textContent], { type: "text/plain;charset=utf-8" });

			if (!filename.endsWith(".txt")) {
				filename += ".txt";
			}
		}

		console.log("创建的Blob对象:", blob, "大小:", blob.size);

		// 创建下载链接
		const url = window.URL.createObjectURL(blob);
		const a = document.createElement("a");
		a.href = url;
		a.download = filename;
		document.body.appendChild(a);
		a.click();
		document.body.removeChild(a);
		window.URL.revokeObjectURL(url);

		console.log(`文件导出成功: ${filename}`);
		return Promise.resolve();
	} catch (error) {
		console.error("导出失败:", error);
		throw error;
	}
}

// 处理导出方法
function handleExportMethod({ options }: { options: any }) {
	console.log("导出选项:", options);

	// 处理条件参数，参考官方示例
	const body = {
		filename: options.filename,
		sheetName: options.sheetName,
		isHeader: options.isHeader,
		original: options.original,
		mode: options.mode,
		ids:
			options.mode === "selected"
				? options.data.map((item: any) => item.id)
				: [],
		fields: options.columns.map((column: any) => {
			return {
				field: column.field,
				title: column.title,
			};
		}),
	};

	console.log("处理后的导出参数:", body);

	return exportFileApi(body);
}

// 打开导出对话框
function openExport() {
	const $grid = gridRef.value;
	if ($grid) {
		$grid.openExport();
	}
}

// 本地状态
const searchQuery = ref("");
const sortField = ref<string>("name");
const sortOrder = ref<"asc" | "desc">("asc");

// 计算属性
const filteredFiles = computed(() => {
	let files = [...fileStore.files];

	// 搜索过滤
	if (searchQuery.value.trim()) {
		const query = searchQuery.value.toLowerCase();
		files = files.filter(
			(file) =>
				file.name.toLowerCase().includes(query) ||
				file.path.toLowerCase().includes(query) ||
				(file.matchInfo?.code &&
					file.matchInfo.code.toLowerCase().includes(query)) ||
				(file.matchInfo?.matchedRule &&
					file.matchInfo.matchedRule.toLowerCase().includes(query))
		);
	}

	return files;
});

const sortedFiles = computed(() => {
	return [...filteredFiles.value].sort((a, b) => {
		let aValue: any, bValue: any;

		switch (sortField.value) {
			case "name":
				aValue = a.name.toLowerCase();
				bValue = b.name.toLowerCase();
				break;
			case "size":
				aValue = a.size;
				bValue = b.size;
				break;
			case "lastModified":
				aValue = a.lastModified;
				bValue = b.lastModified;
				break;
			case "matched":
				aValue = a.matched ? 1 : 0;
				bValue = b.matched ? 1 : 0;
				break;
			default:
				return 0;
		}

		if (aValue < bValue) return sortOrder.value === "asc" ? -1 : 1;
		if (aValue > bValue) return sortOrder.value === "asc" ? 1 : -1;
		return 0;
	});
});

// Grid配置 - 配置式表格
const gridOptions = computed<VxeGridProps<FileItem>>(() => ({
	border: true,
	height: "auto",
	loading: fileStore.isLoading,
	rowConfig: {
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
		remote: true,
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
		showStatus: true,
	},
	exportConfig: {
		remote: true,
		modes: [
			{ label: "导出全部数据为 TXT", value: "allTxt" },
			{ label: "导出全部数据为 CSV", value: "allCsv" },
			{ label: "导出选中数据为 TXT", value: "selectedTxt" },
			{ label: "导出选中数据为 CSV", value: "selectedCsv" },
		],
		exportMethod: handleExportMethod,
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
	data: sortedFiles.value,
	columns: getColumnsConfig(),
}));

// 列配置函数
function getColumnsConfig() {
	const cols: any[] = [];

	// 选择列
	if (props.showSelection) {
		cols.push({
			type: "checkbox",
			width: 50,
			fixed: "left",
		});
	}

	// 序号列 - 作为第一列，添加拖拽排序配置
	cols.push({
		field: "index",
		title: "序号",
		width: 80,
		align: "center",
		dragSort: true, // 启用序号列拖拽排序
		slots: { default: "index-slot" },
	});

	// 文件名列
	cols.push({
		field: "name",
		title: "文件名",
		minWidth: 200,
		sortable: true,
		editRender: { name: "input", autoselect: true },
		slots: { default: "name-slot", edit: "name-edit-slot" },
	});

	// 文件大小列
	cols.push({
		field: "size",
		title: "大小",
		width: 120,
		sortable: true,
		align: "right",
		slots: { default: "size-slot" },
	});

	// 最后修改时间列
	cols.push({
		field: "lastModified",
		title: "修改时间",
		width: 180,
		sortable: true,
		slots: { default: "date-slot" },
	});

	// 匹配信息列
	if (props.showMatchInfo) {
		cols.push({
			field: "matchInfo",
			title: "匹配状态",
			width: 150,
			sortable: true,
			slots: { default: "match-slot" },
		});
	}

	// 预览名称列
	if (props.showPreview) {
		cols.push({
			field: "previewName",
			title: "预览名称",
			minWidth: 200,
			slots: { default: "preview-slot" },
		});
	}

	return cols;
}

// 方法
function handleSortChange(params: any) {
	const { property, order } = params;
	if (property) {
		sortField.value = property;
		sortOrder.value = order === "asc" ? "asc" : "desc";
		emit("sort-changed", property, sortOrder.value);
	}
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
	return file.matchInfo?.code || "已匹配";
}

function getMatchStatusClass(file: FileItem): string {
	return file.matched ? "text-green-600 font-medium" : "text-gray-500";
}

// 编辑相关方法
function handleNameEditComplete(row: FileItem) {
	// 触发表格退出编辑状态
	gridRef.value?.clearEdit();

	// 更新文件存储中的数据
	const fileIndex = fileStore.files.findIndex((file) => file.id === row.id);
	if (fileIndex !== -1) {
		// 创建新的文件数组以触发响应式更新
		const newFiles = [...fileStore.files];
		newFiles[fileIndex] = { ...row };
		fileStore.files = newFiles;
	}
}

// 拖拽排序相关方法
function handleRowDragStart(params: any) {
	console.log("🔧 [DEBUG] Row drag start:", params);
}

function handleRowDragEnd(params: any) {
	console.log("🔧 [DEBUG] Row drag end:", params);
	const { dragRow, targetRow, currRow, nextRow } = params;

	// 更新文件存储中的文件顺序
	const newFiles = [...fileStore.files];
	const dragIndex = newFiles.findIndex((file) => file.id === dragRow.id);

	console.log(
		"🔧 [DEBUG] Drag index:",
		dragIndex,
		"Total files:",
		newFiles.length
	);

	if (dragIndex !== -1) {
		// 从原位置移除
		const [removedFile] = newFiles.splice(dragIndex, 1);

		// 计算新位置
		let newIndex = newFiles.length; // 默认放到最后
		if (targetRow) {
			const targetIndex = newFiles.findIndex(
				(file) => file.id === targetRow.id
			);
			if (targetIndex !== -1) {
				// 根据currRow和nextRow确定插入位置
				if (currRow && currRow.id === targetRow.id) {
					// 插入到目标行之后
					newIndex = targetIndex + 1;
				} else {
					// 插入到目标行之前
					newIndex = targetIndex;
				}
			}
		}

		console.log("🔧 [DEBUG] Moving file from", dragIndex, "to", newIndex);

		// 插入到新位置
		newFiles.splice(newIndex, 0, removedFile);

		// 更新文件存储
		fileStore.files = newFiles;
		console.log("🔧 [DEBUG] Files updated successfully");
	}
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

// 批量操作方法
function executeBatchOperation(operation: string) {
	if (!props.showSelection) return;
	const selectedFiles = getSelectedFiles();
	if (selectedFiles.length > 0) {
		emit("batch-operation", operation, selectedFiles);
	}
}

// 导出相关方法
async function exportData(options: {
	type: "xlsx" | "csv";
	mode: "current" | "selected";
	columns?: string[];
	filename?: string;
}) {
	if (!gridRef.value) return;

	try {
		// 设置默认文件名
		const defaultFilename =
			options.filename ||
			`file-export-${new Date().toISOString().slice(0, 10)}`;

		// 根据导出类型设置文件扩展名
		const extension = options.type === "xlsx" ? ".xlsx" : ".csv";
		const filename = defaultFilename.endsWith(extension)
			? defaultFilename
			: `${defaultFilename}${extension}`;

		// 准备导出选项
		const exportOptions = {
			type: options.type,
			mode: options.mode,
			filename: filename,
			// 自定义导出字段映射
			columnFilterMethod: ({ column }: { column: any }) => {
				// 过滤掉不需要导出的列，如操作列
				return column.property !== "actions";
			},
			// 自定义数据处理
			dataFilterMethod: ({ row }: { row: any }) => {
				// 可以在这里对导出的数据进行处理
				return row;
			},
		};

		// 执行导出
		await gridRef.value.exportData(exportOptions);

		// 导出完成回调
		console.log(`数据导出完成: ${filename}`);
	} catch (error) {
		console.error("导出失败:", error);
		// 可以在这里添加错误处理逻辑，比如显示错误消息
	}
}

// 导出全部数据
function exportAllData(type: "xlsx" | "csv" = "xlsx", filename?: string) {
	const $grid = gridRef.value;
	if ($grid) {
		const mode = type === "xlsx" ? "allXlsx" : "allCsv";
		$grid.exportData({
			mode,
			filename,
		});
	}
}

// 导出选中数据
function exportSelectedData(type: "xlsx" | "csv" = "xlsx", filename?: string) {
	const $grid = gridRef.value;
	if ($grid) {
		const mode = type === "xlsx" ? "selectedXlsx" : "selectedCsv";
		$grid.exportData({
			mode,
			filename,
		});
	}
}

// 暴露方法给父组件
defineExpose({
	selectAll,
	unselectAll,
	getSelectedFiles,
	setSearchQuery,
	executeBatchOperation,
	exportAllData,
	exportSelectedData,
	openExport,
});

// 监听文件选择变化
watch(
	() => fileStore.selectedFiles,
	(newSelected) => {
		nextTick(() => {
			// 更新表格选中状态
			if (gridRef.value) {
				// 清除当前选中状态
				gridRef.value.setAllCheckboxRow(false);
				// 重新设置选中状态
				const selectedIds = Array.from(newSelected);
				const selectedFiles = sortedFiles.value.filter((file) =>
					selectedIds.includes(file.id)
				);
				gridRef.value.setCheckboxRow(selectedFiles, true);
			}
		});
	},
	{ deep: true }
);

// 监听文件列表变化
watch(
	() => sortedFiles.value,
	() => {
		nextTick(() => {
			// 更新表格数据
			gridRef.value?.reloadData(sortedFiles.value);
		});
	},
	{ deep: true }
);
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
			v-if="sortedFiles.length > 0"
			class="table-container flex-1 overflow-hidden"
		>
			<vxe-grid
				ref="gridRef"
				v-bind="gridOptions"
				@sort-change="handleSortChange"
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
