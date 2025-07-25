<script setup lang="ts">
import { ref, computed, nextTick, onMounted } from "vue";
import { useRuleStore } from "../../stores/ruleStore";
import { useErrorHandler } from "../../composables/useErrorHandler";
import type { Rule } from "../../types/rule";
import RuleEditor from "./RuleEditor.vue";

const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();

// 本地状态
const showEditor = ref(false);
const editingRule = ref<Rule | null>(null);
const searchQuery = ref("");
const selectedRuleIds = ref<Set<string>>(new Set());
const showSearchSuggestions = ref(false);
const searchSuggestions = ref<string[]>([]);

// 计算属性
const filteredRules = computed(() => {
	if (!searchQuery.value) return ruleStore.rules;

	const query = searchQuery.value.toLowerCase();
	return ruleStore.rules.filter(
		(rule) =>
			rule.code.toLowerCase().includes(query) ||
			rule.thirtyD.toLowerCase().includes(query) ||
			rule.matchRules.some((mr) => mr.toLowerCase().includes(query))
	);
});

const selectedRules = computed(() => {
	return filteredRules.value.filter((rule) =>
		selectedRuleIds.value.has(rule.id)
	);
});

const ruleStats = computed(() => {
	return {
		total: ruleStore.rules.length,
		user: ruleStore.userRules.length,
		system: ruleStore.systemRules.length,
		filtered: filteredRules.value.length,
		selected: selectedRules.value.length
	};
});

// 方法
function openEditor(rule?: Rule) {
	showEditor.value = false;
	editingRule.value = null;

	nextTick(() => {
		editingRule.value = rule || null;
		showEditor.value = true;
	});
}

function closeEditor() {
	showEditor.value = false;
	editingRule.value = null;
}

function handleRuleSaved() {
	closeEditor();
	handleSuccess("规则保存成功");
}

function deleteRule(rule: Rule) {
	if (confirm(`确定要删除规则 "${rule.code}" 吗？`)) {
		try {
			ruleStore.deleteRule(rule.id);
			selectedRuleIds.value.delete(rule.id);
			handleSuccess("规则删除成功");
		} catch (error) {
			handleError(error, "删除规则失败");
		}
	}
}

function deleteSelectedRules() {
	if (selectedRules.value.length === 0) return;
	
	if (confirm(`确定要删除选中的 ${selectedRules.value.length} 个规则吗？`)) {
		try {
			selectedRules.value.forEach(rule => {
				ruleStore.deleteRule(rule.id);
			});
			selectedRuleIds.value.clear();
			handleSuccess(`成功删除 ${selectedRules.value.length} 个规则`);
		} catch (error) {
			handleError(error, "批量删除规则失败");
		}
	}
}

function toggleRuleSelection(ruleId: string) {
	if (selectedRuleIds.value.has(ruleId)) {
		selectedRuleIds.value.delete(ruleId);
	} else {
		selectedRuleIds.value.add(ruleId);
	}
}

function selectAllRules() {
	if (selectedRuleIds.value.size === filteredRules.value.length) {
		selectedRuleIds.value.clear();
	} else {
		filteredRules.value.forEach(rule => {
			selectedRuleIds.value.add(rule.id);
		});
	}
}

function clearSearch() {
	searchQuery.value = "";
	showSearchSuggestions.value = false;
}

function handleSearchInput() {
	if (searchQuery.value.length > 0) {
		// 简化的搜索建议逻辑
		const suggestions = ruleStore.rules
			.filter(rule => 
				rule.code.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
				rule.matchRules.some(mr => mr.toLowerCase().includes(searchQuery.value.toLowerCase()))
			)
			.slice(0, 5)
			.map(rule => rule.code);
		
		searchSuggestions.value = [...new Set(suggestions)];
		showSearchSuggestions.value = suggestions.length > 0;
	} else {
		showSearchSuggestions.value = false;
	}
}

function selectSearchSuggestion(suggestion: string) {
	searchQuery.value = suggestion;
	showSearchSuggestions.value = false;
}

function resetToDefault() {
	if (confirm("确定要重置为默认规则吗？这将删除所有用户自定义规则。")) {
		try {
			ruleStore.resetToDefault();
			selectedRuleIds.value.clear();
			handleSuccess("已重置为默认规则");
		} catch (error) {
			handleError(error, "重置规则失败");
		}
	}
}

function exportRules() {
	try {
		const data = ruleStore.exportRules();
		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = document.createElement('a');
		a.href = url;
		a.download = `rules-export-${new Date().toISOString().split('T')[0]}.json`;
		a.click();
		URL.revokeObjectURL(url);
		handleSuccess("规则导出成功");
	} catch (error) {
		handleError(error, "导出规则失败");
	}
}

async function importRules(event: Event) {
	const input = event.target as HTMLInputElement;
	const file = input.files?.[0];
	if (!file) return;

	try {
		const text = await file.text();
		const data = JSON.parse(text);
		ruleStore.importRules(data);
		handleSuccess("规则导入成功");
	} catch (error) {
		handleError(error, "导入规则失败");
	} finally {
		input.value = '';
	}
}

// 生命周期
onMounted(async () => {
	try {
		await ruleStore.loadRules();
	} catch (error) {
		handleError(error, "加载规则失败");
	}
});
</script>

<template>
	<div class="rule-manager flex flex-col h-full bg-white">
		<!-- 工具栏 -->
		<div class="toolbar flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
			<div class="toolbar-left flex items-center gap-3">
				<button
					@click="openEditor()"
					class="btn-primary px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
				>
					<span class="mr-2">➕</span>
					新建规则
				</button>
				
				<button
					v-if="selectedRules.length > 0"
					@click="deleteSelectedRules"
					class="btn-danger px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors"
				>
					<span class="mr-2">🗑️</span>
					删除选中 ({{ selectedRules.length }})
				</button>
			</div>

			<div class="toolbar-right flex items-center gap-3">
				<button
					@click="exportRules"
					class="btn-secondary px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
				>
					<span class="mr-2">📤</span>
					导出
				</button>
				
				<label class="btn-secondary px-3 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors cursor-pointer">
					<span class="mr-2">📥</span>
					导入
					<input
						type="file"
						accept=".json"
						@change="importRules"
						class="hidden"
					/>
				</label>
				
				<button
					@click="resetToDefault"
					class="btn-warning px-3 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors"
				>
					<span class="mr-2">🔄</span>
					重置
				</button>
			</div>
		</div>

		<!-- 搜索栏 -->
		<div class="search-bar p-4 border-b border-gray-200 relative">
			<div class="relative">
				<input
					v-model="searchQuery"
					@input="handleSearchInput"
					@focus="handleSearchInput"
					@blur="setTimeout(() => showSearchSuggestions = false, 200)"
					type="text"
					placeholder="搜索规则代码、30D标记或匹配规则..."
					class="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
				<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
					<span class="text-gray-400">🔍</span>
				</div>
				<div v-if="searchQuery" class="absolute inset-y-0 right-0 pr-3 flex items-center">
					<button
						@click="clearSearch"
						class="text-gray-400 hover:text-gray-600 focus:outline-none"
					>
						<span>✕</span>
					</button>
				</div>
			</div>

			<!-- 搜索建议 -->
			<div
				v-if="showSearchSuggestions && searchSuggestions.length > 0"
				class="absolute top-full left-4 right-4 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 max-h-48 overflow-y-auto"
			>
				<div
					v-for="suggestion in searchSuggestions"
					:key="suggestion"
					@click="selectSearchSuggestion(suggestion)"
					class="px-4 py-2 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0"
				>
					{{ suggestion }}
				</div>
			</div>
		</div>

		<!-- 规则列表 -->
		<div class="rule-list flex-1 overflow-auto">
			<div v-if="filteredRules.length === 0" class="empty-state flex flex-col items-center justify-center h-full p-12 text-center">
				<div class="text-6xl mb-6 opacity-50">📋</div>
				<div class="text-lg font-medium text-gray-600 mb-2">
					{{ searchQuery ? '未找到匹配的规则' : '暂无规则' }}
				</div>
				<div class="text-sm text-gray-400 mb-4">
					{{ searchQuery ? '尝试调整搜索条件' : '点击"新建规则"开始添加规则' }}
				</div>
				<button
					v-if="!searchQuery"
					@click="openEditor()"
					class="btn-primary px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
				>
					新建第一个规则
				</button>
			</div>

			<div v-else class="rule-table">
				<!-- 表头 -->
				<div class="table-header flex items-center p-4 bg-gray-50 border-b border-gray-200 font-medium text-gray-700">
					<div class="w-12 flex items-center justify-center">
						<input
							type="checkbox"
							:checked="selectedRuleIds.size === filteredRules.length && filteredRules.length > 0"
							:indeterminate="selectedRuleIds.size > 0 && selectedRuleIds.size < filteredRules.length"
							@change="selectAllRules"
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						/>
					</div>
					<div class="flex-1 min-w-0 px-4">规则代码</div>
					<div class="w-20 px-4 text-center">30D</div>
					<div class="flex-1 min-w-0 px-4">匹配规则</div>
					<div class="w-20 px-4 text-center">来源</div>
					<div class="w-32 px-4 text-center">操作</div>
				</div>

				<!-- 规则行 -->
				<div
					v-for="rule in filteredRules"
					:key="rule.id"
					class="rule-row flex items-center p-4 border-b border-gray-100 hover:bg-gray-50 transition-colors"
					:class="{ 'bg-blue-50': selectedRuleIds.has(rule.id) }"
				>
					<div class="w-12 flex items-center justify-center">
						<input
							type="checkbox"
							:checked="selectedRuleIds.has(rule.id)"
							@change="toggleRuleSelection(rule.id)"
							class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
						/>
					</div>
					<div class="flex-1 min-w-0 px-4">
						<div class="font-medium text-gray-900 truncate">{{ rule.code }}</div>
					</div>
					<div class="w-20 px-4 text-center">
						<span
							class="inline-block px-2 py-1 text-xs font-medium rounded-full"
							:class="rule.thirtyD === 'Y' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'"
						>
							{{ rule.thirtyD || 'N' }}
						</span>
					</div>
					<div class="flex-1 min-w-0 px-4">
						<div class="flex flex-wrap gap-1">
							<span
								v-for="(matchRule, index) in rule.matchRules.slice(0, 3)"
								:key="index"
								class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded"
							>
								{{ matchRule }}
							</span>
							<span
								v-if="rule.matchRules.length > 3"
								class="inline-block px-2 py-1 text-xs bg-gray-100 text-gray-500 rounded"
							>
								+{{ rule.matchRules.length - 3 }}
							</span>
						</div>
					</div>
					<div class="w-20 px-4 text-center">
						<span
							class="inline-block px-2 py-1 text-xs font-medium rounded-full"
							:class="rule.source === 'user' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'"
						>
							{{ rule.source === 'user' ? '用户' : '系统' }}
						</span>
					</div>
					<div class="w-32 px-4 flex items-center justify-center gap-2">
						<button
							@click="openEditor(rule)"
							class="p-1 text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
							title="编辑"
						>
							✏️
						</button>
						<button
							@click="deleteRule(rule)"
							class="p-1 text-red-600 hover:text-red-800 hover:bg-red-50 rounded transition-colors"
							title="删除"
						>
							🗑️
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- 统计信息 -->
		<div class="rule-stats flex items-center gap-6 p-4 bg-gray-50 border-t border-gray-200 text-sm">
			<div class="stats-item flex items-center gap-2">
				<span class="text-gray-500">总计:</span>
				<span class="font-semibold text-gray-900">{{ ruleStats.total }}</span>
			</div>
			<div class="stats-item flex items-center gap-2">
				<span class="text-gray-500">系统:</span>
				<span class="font-semibold text-gray-900">{{ ruleStats.system }}</span>
			</div>
			<div class="stats-item flex items-center gap-2">
				<span class="text-gray-500">用户:</span>
				<span class="font-semibold text-blue-600">{{ ruleStats.user }}</span>
			</div>
			<div v-if="searchQuery" class="stats-item flex items-center gap-2">
				<span class="text-gray-500">筛选:</span>
				<span class="font-semibold text-green-600">{{ ruleStats.filtered }}</span>
			</div>
			<div v-if="selectedRules.length > 0" class="stats-item flex items-center gap-2">
				<span class="text-gray-500">选中:</span>
				<span class="font-semibold text-orange-600">{{ ruleStats.selected }}</span>
			</div>
		</div>

		<!-- 规则编辑器模态框 -->
		<RuleEditor
			v-if="showEditor"
			:rule="editingRule"
			@close="closeEditor"
			@saved="handleRuleSaved"
		/>
	</div>
</template>
