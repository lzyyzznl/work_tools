<script setup lang="ts">
import { ref, computed, onMounted } from "vue";
import { useRuleStore } from "../../stores/ruleStore";
import { useErrorHandler } from "../../composables/useErrorHandler";
import RuleManagerTable from "./RuleManagerTable.vue";
import ColumnManager from "./ColumnManager.vue";

const ruleStore = useRuleStore();
const { handleError, handleSuccess } = useErrorHandler();
const ruleTableRef = ref<InstanceType<typeof RuleManagerTable> | null>(null);

// 本地状态
const searchQuery = ref("");
const activeTab = ref<"rules" | "columns">("rules");

// 计算属性
const ruleStats = computed(() => {
	return {
		total: ruleStore.rules.length
	};
});

// 方法
function resetToDefault() {
	if (confirm("确定要重置为默认规则吗？这将删除所有用户自定义规则。")) {
		try {
			ruleStore.resetToDefault();
			handleSuccess("已重置为默认规则");
		} catch (error) {
			handleError(error, "重置规则失败");
		}
	}
}

async function exportRules() {
	try {
		// 调用子组件的导出方法
		if (ruleTableRef.value) {
			await ruleTableRef.value.exportCSV();
		}
	} catch (error) {
		handleError(error, "导出规则失败");
	}
}

async function importRules(event: Event) {
	// 导入功能已在RuleManagerTable中实现
	const input = event.target as HTMLInputElement;
	input.value = '';
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
		<!-- 标签页导航 -->
		<div class="tab-navigation flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50">
			<div class="tab-buttons flex items-center gap-2">
				<button
					@click="activeTab = 'rules'"
					:active="activeTab === 'rules'"
					class="px-4 py-2 rounded-lg font-medium transition-colors"
					:class="activeTab === 'rules' 
						? 'bg-blue-500 text-white shadow-sm' 
						: 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'"
				>
					<span class="mr-2">📋</span>
					规则管理
				</button>
				<button
					@click="activeTab = 'columns'"
					:active="activeTab === 'columns'"
					class="px-4 py-2 rounded-lg font-medium transition-colors"
					:class="activeTab === 'columns' 
						? 'bg-blue-500 text-white shadow-sm' 
						: 'text-gray-600 hover:bg-gray-200 hover:text-gray-800'"
				>
					<span class="mr-2">📊</span>
					列管理
				</button>
			</div>

			<div class="toolbar-right flex items-center gap-3">
				<!-- 规则管理页面的工具栏按钮 -->
				<template v-if="activeTab === 'rules'">
					<button
						@click="exportRules"
						class="btn-secondary px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors flex items-center"
					>
						<span class="mr-2">📤</span>
						导出CSV
					</button>
					
					<label class="btn-secondary px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors cursor-pointer flex items-center">
						<span class="mr-2">📥</span>
						导入CSV
						<input
							type="file"
							accept=".csv"
							@change="importRules"
							class="hidden"
						/>
					</label>
					
					<button
						@click="resetToDefault"
						class="btn-warning px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors flex items-center"
					>
						<span class="mr-2">🔄</span>
						重置
					</button>
				</template>
			</div>
		</div>

		<!-- 标签页内容 -->
		<div class="tab-content flex-1 overflow-hidden">
			<!-- 规则管理页面 -->
			<div 
				v-if="activeTab === 'rules'"
				class="rules-tab flex flex-col h-full"
			>
				<div class="rule-table-container flex-1 overflow-hidden">
					<RuleManagerTable ref="ruleTableRef" />
				</div>

				<!-- 统计信息 -->
				<div class="rule-stats flex items-center gap-6 p-4 bg-gray-50 border-t border-gray-200 text-sm">
					<div class="stats-item flex items-center gap-2">
						<span class="text-gray-500">总计:</span>
						<span class="font-semibold text-gray-900">{{ ruleStats.total }}</span>
					</div>
				</div>
			</div>

			<!-- 列管理页面 -->
			<div 
				v-else-if="activeTab === 'columns'"
				class="columns-tab flex flex-col h-full"
			>
				<ColumnManager />
			</div>
		</div>
	</div>
</template>
