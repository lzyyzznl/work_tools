<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRuleStore } from "../../stores/ruleStore";
import { useErrorHandler } from "../../composables/useErrorHandler";
import type { RuleColumn } from "../../types/rule";

const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();

// 本地状态
const newColumn = ref({
	name: "",
	type: "text" as "text" | "number" | "date" | "boolean" | "select",
	visible: true,
	options: "",
});

const editingColumnId = ref<string | null>(null);
const editingColumn = ref<Partial<RuleColumn> | null>(null);

// 计算属性
const sortedColumns = computed(() => {
	return [...ruleStore.columns].sort((a, b) => a.order - b.order);
});

// 方法
function addColumn() {
	try {
		if (!newColumn.value.name.trim()) {
			throw new Error("列名不能为空");
		}

		// 检查字段名是否重复（使用列名作为字段名）
		const exists = ruleStore.columns.some(
			(col) => col.field === newColumn.value.name.trim()
		);

		if (exists) {
			throw new Error(`列名 "${newColumn.value.name}" 已存在`);
		}

		// 处理枚举选项
		let options: string[] | undefined;
		if (newColumn.value.type === "select" && newColumn.value.options) {
			options = newColumn.value.options
				.split(",")
				.map((opt) => opt.trim())
				.filter((opt) => opt);
		}

		ruleStore.addColumn({
			name: newColumn.value.name.trim(),
			field: newColumn.value.name.trim(), // 使用列名作为字段名
			type: newColumn.value.type,
			visible: newColumn.value.visible,
			order: ruleStore.columns.length,
			options: options,
		});

		// 重置表单
		newColumn.value = {
			name: "",
			type: "text",
			visible: true,
			options: "",
		};

		handleSuccess("列添加成功");
	} catch (error) {
		handleError(error, "添加列");
	}
}

function startEditColumn(column: RuleColumn) {
	editingColumnId.value = column.id;
	editingColumn.value = {
		...column,
		// 将options数组转换为逗号分隔的字符串
		options: column.options ? column.options.join(",") : "",
		field: column.name, // 编辑时使用列名作为字段名
	};
}

function saveEditColumn() {
	try {
		if (!editingColumn.value || !editingColumnId.value) return;

		if (!editingColumn.value.name?.trim()) {
			throw new Error("列名不能为空");
		}

		// 检查字段名是否重复（使用列名作为字段名，排除当前编辑的列）
		const exists = ruleStore.columns.some(
			(col) =>
				col.field === editingColumn.value?.name?.trim() &&
				col.id !== editingColumnId.value
		);

		if (exists) {
			throw new Error(`列名 "${editingColumn.value.name}" 已存在`);
		}

		// 处理枚举选项
		let options: string[] | undefined;
		if (editingColumn.value.type === "select" && editingColumn.value.options) {
			options = editingColumn.value.options
				.split(",")
				.map((opt) => opt.trim())
				.filter((opt) => opt);
		}

		ruleStore.updateColumn(editingColumnId.value, {
			name: editingColumn.value.name.trim(),
			field: editingColumn.value.name.trim(), // 使用列名作为字段名
			type: editingColumn.value.type,
			visible: editingColumn.value.visible,
			options: options,
		});

		cancelEditColumn();
		handleSuccess("列更新成功");
	} catch (error) {
		handleError(error, "更新列");
	}
}

function cancelEditColumn() {
	editingColumnId.value = null;
	editingColumn.value = null;
}

function deleteColumn(id: string) {
	const column = ruleStore.getColumnById(id);
	if (!column) return;

	// 匹配规则列是隐式固定的（不在列配置中），所以不需要特别检查

	if (confirm(`确定要删除列 "${column.name}" 吗？`)) {
		try {
			ruleStore.deleteColumn(id);
			handleSuccess("列删除成功");
		} catch (error) {
			handleError(error, "删除列");
		}
	}
}

function toggleColumnVisibility(id: string) {
	const column = ruleStore.getColumnById(id);
	if (column) {
		ruleStore.updateColumn(id, { visible: !column.visible });
	}
}

function moveColumnUp(index: number) {
	if (index > 0) {
		const column = sortedColumns.value[index];
		ruleStore.moveColumn(column.id, index - 1);
	}
}

function moveColumnDown(index: number) {
	if (index < sortedColumns.value.length - 1) {
		const column = sortedColumns.value[index];
		ruleStore.moveColumn(column.id, index + 1);
	}
}
</script>

<template>
	<div class="column-manager flex flex-col h-full bg-white">
		<!-- 头部 -->
		<div class="header p-4 border-b border-gray-200 bg-gray-50">
			<h2 class="text-lg font-semibold text-gray-900">规则列管理</h2>
			<p class="text-sm text-gray-600 mt-1">管理规则匹配器中显示的动态列</p>
		</div>

		<!-- 添加新列表单 -->
		<div class="add-column-form p-4 border-b border-gray-200">
			<h3 class="text-md font-medium text-gray-900 mb-3">添加新列</h3>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-3">
				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1"
						>列名</label
					>
					<input
						v-model="newColumn.name"
						type="text"
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						placeholder="显示名称"
					/>
				</div>

				<div>
					<label class="block text-sm font-medium text-gray-700 mb-1"
						>类型</label
					>
					<select
						v-model="newColumn.type"
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						<option value="text">文本</option>
						<option value="number">数字</option>
						<option value="date">日期</option>
						<option value="boolean">布尔值</option>
						<option value="select">枚举</option>
					</select>
				</div>

				<!-- 枚举选项输入框（仅在类型为枚举时显示） -->
				<div v-if="newColumn.type === 'select'">
					<label class="block text-sm font-medium text-gray-700 mb-1"
						>枚举选项</label
					>
					<input
						v-model="newColumn.options"
						type="text"
						class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
						placeholder="选项1,选项2,选项3"
					/>
					<div class="text-xs text-gray-500 mt-1">多个选项请用逗号分隔</div>
				</div>

				<div class="flex items-end">
					<button
						@click="addColumn"
						class="w-full px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
					>
						添加列
					</button>
				</div>
			</div>
		</div>

		<!-- 列列表 -->
		<div class="column-list flex-1 overflow-auto p-4">
			<h3 class="text-md font-medium text-gray-900 mb-3">
				现有列 ({{ sortedColumns.length }})
			</h3>

			<div
				v-if="sortedColumns.length === 0"
				class="text-center py-8 text-gray-500"
			>
				暂无列配置
			</div>

			<div v-else class="space-y-2">
				<div
					v-for="(column, index) in sortedColumns"
					:key="column.id"
					class="flex items-center p-3 border border-gray-200 rounded-md bg-white"
				>
					<!-- 拖拽排序按钮 -->
					<div class="flex flex-col mr-3">
						<button
							@click="moveColumnUp(index)"
							:disabled="index === 0"
							class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
							title="上移"
						>
							↑
						</button>
						<button
							@click="moveColumnDown(index)"
							:disabled="index === sortedColumns.length - 1"
							class="p-1 text-gray-400 hover:text-gray-600 disabled:opacity-30"
							title="下移"
						>
							↓
						</button>
					</div>

					<!-- 列信息 -->
					<div class="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
						<div v-if="editingColumnId === column.id">
							<input
								v-model="editingColumn!.name"
								type="text"
								class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
							/>
						</div>
						<div v-else class="py-1 font-medium">
							{{ column.name }}
						</div>

						<!-- 字段名只读显示 -->
						<div class="py-1 text-gray-600">
							{{ column.field }}
						</div>

						<div v-if="editingColumnId === column.id">
							<select
								v-model="editingColumn!.type"
								class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
							>
								<option value="text">文本</option>
								<option value="number">数字</option>
								<option value="date">日期</option>
								<option value="boolean">布尔值</option>
								<option value="select">枚举</option>
							</select>
						</div>
						<div v-else class="py-1 text-gray-600">
							{{ column.type === "select" ? "枚举" : column.type }}
						</div>

						<div class="flex flex-col">
							<div
								v-if="editingColumnId === column.id"
								class="flex items-center mb-2"
							>
								<input
									v-model="editingColumn!.visible"
									type="checkbox"
									class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
								/>
								<label class="text-sm text-gray-700">可见</label>
							</div>
							<div v-else class="flex items-center mb-2">
								<input
									:checked="column.visible"
									@change="toggleColumnVisibility(column.id)"
									type="checkbox"
									class="mr-2 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
								/>
								<label class="text-sm text-gray-700">
									{{ column.visible ? "可见" : "隐藏" }}
								</label>
							</div>

							<!-- 枚举选项编辑框（仅在类型为枚举时显示） -->
							<div
								v-if="editingColumnId === column.id && editingColumn!.type === 'select'"
							>
								<input
									v-model="editingColumn!.options"
									type="text"
									class="w-full px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500 text-xs"
									placeholder="选项1,选项2,选项3"
								/>
								<div class="text-xs text-gray-500 mt-1">
									多个选项请用逗号分隔
								</div>
							</div>
							<div
								v-else-if="column.type === 'select'"
								class="text-xs text-gray-500"
							>
								选项: {{ column.options?.join(",") || "无" }}
							</div>
						</div>
					</div>

					<!-- 操作按钮 -->
					<div class="ml-3 flex space-x-1">
						<template v-if="editingColumnId === column.id">
							<button
								@click="saveEditColumn"
								class="p-1 text-green-600 hover:text-green-800"
								title="保存"
							>
								✅
							</button>
							<button
								@click="cancelEditColumn"
								class="p-1 text-gray-600 hover:text-gray-800"
								title="取消"
							>
								✕
							</button>
						</template>
						<template v-else>
							<button
								@click="startEditColumn(column)"
								class="p-1 text-blue-600 hover:text-blue-800"
								title="编辑"
							>
								✏️
							</button>
							<button
								@click="deleteColumn(column.id)"
								class="p-1 text-red-600 hover:text-red-800"
								title="删除"
							>
								🗑️
							</button>
						</template>
					</div>
				</div>
			</div>
		</div>

		<!-- 底部说明 -->
		<div
			class="footer p-4 border-t border-gray-200 bg-gray-50 text-sm text-gray-600"
		>
			<p>
				💡
				提示：列配置将影响文件匹配器中动态列的显示，规则创建时可以为每个列设置值。字段名将自动使用列名。
			</p>
		</div>
	</div>
</template>

<style scoped>
/* 使用 UnoCSS 样式，无需额外的 CSS */
</style>
