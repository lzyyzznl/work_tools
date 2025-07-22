<script setup lang="ts">
import { ref, computed, nextTick } from "vue";
import { useRuleStore } from "../../stores/ruleStore";
import type { Rule } from "../../types/rule";
import RuleEditor from "./RuleEditor.vue";

const ruleStore = useRuleStore();

// 本地状态
const showEditor = ref(false);
const editingRule = ref<Rule | null>(null);
const searchQuery = ref("");
const selectedRuleIds = ref<Set<string>>(new Set());

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

// 方法
function openEditor(rule?: Rule) {
	// 先关闭编辑器，然后重新打开以确保正确的状态
	showEditor.value = false;
	editingRule.value = null;

	// 使用nextTick确保DOM更新完成
	nextTick(() => {
		editingRule.value = rule || null;
		showEditor.value = true;
	});
}

function closeEditor() {
	showEditor.value = false;
	// 延迟清空editingRule，避免组件销毁时的问题
	setTimeout(() => {
		editingRule.value = null;
	}, 100);
}

function handleRuleSaved() {
	closeEditor();
	// 规则已在RuleEditor中保存到store
}

function deleteRule(ruleId: string) {
	if (confirm("确定要删除这个规则吗？")) {
		ruleStore.deleteRule(ruleId);
	}
}

function deleteSelectedRules() {
	if (selectedRules.value.length === 0) return;

	if (confirm(`确定要删除选中的 ${selectedRules.value.length} 个规则吗？`)) {
		selectedRules.value.forEach((rule) => {
			ruleStore.deleteRule(rule.id);
		});
		selectedRuleIds.value.clear();
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
		filteredRules.value.forEach((rule) => selectedRuleIds.value.add(rule.id));
	}
}

function exportRules() {
	const data = ruleStore.exportRules();
	const blob = new Blob([JSON.stringify(data, null, 2)], {
		type: "application/json",
	});
	const url = URL.createObjectURL(blob);
	const a = document.createElement("a");
	a.href = url;
	a.download = `rules-export-${new Date().toISOString().split("T")[0]}.json`;
	a.click();
	URL.revokeObjectURL(url);
}

function importRules() {
	const input = document.createElement("input");
	input.type = "file";
	input.accept = ".json";
	input.onchange = (e) => {
		const file = (e.target as HTMLInputElement).files?.[0];
		if (file) {
			const reader = new FileReader();
			reader.onload = (e) => {
				try {
					const data = JSON.parse(e.target?.result as string);
					ruleStore.importRules(data);
					alert("规则导入成功！");
				} catch (error) {
					alert("导入失败：文件格式不正确");
				}
			};
			reader.readAsText(file);
		}
	};
	input.click();
}

function resetToDefault() {
	if (confirm("确定要重置为默认规则吗？这将删除所有自定义规则。")) {
		ruleStore.resetToDefault();
	}
}
</script>

<template>
	<div class="rule-manager">
		<!-- 工具栏 -->
		<div class="rule-toolbar">
			<div class="toolbar-left">
				<button class="btn btn-primary" @click="openEditor()">
					➕ 添加规则
				</button>
				<button
					class="btn"
					@click="deleteSelectedRules"
					:disabled="selectedRules.length === 0"
				>
					🗑️ 删除选中
				</button>
			</div>

			<div class="toolbar-center">
				<input
					v-model="searchQuery"
					type="text"
					class="input search-input"
					placeholder="搜索规则..."
				/>
			</div>

			<div class="toolbar-right">
				<button class="btn" @click="importRules">📥 导入</button>
				<button class="btn" @click="exportRules">📤 导出</button>
				<button class="btn" @click="resetToDefault">🔄 重置</button>
			</div>
		</div>

		<!-- 规则列表 -->
		<div class="rule-list">
			<div class="rule-header">
				<div class="rule-checkbox">
					<input
						type="checkbox"
						:checked="
							selectedRuleIds.size === filteredRules.length &&
							filteredRules.length > 0
						"
						:indeterminate="
							selectedRuleIds.size > 0 &&
							selectedRuleIds.size < filteredRules.length
						"
						@change="selectAllRules"
					/>
				</div>
				<div class="rule-code">代码</div>
				<div class="rule-thirty-d">30D</div>
				<div class="rule-match-rules">匹配规则</div>
				<div class="rule-source">来源</div>
				<div class="rule-actions">操作</div>
			</div>

			<div class="rule-items">
				<div
					v-for="rule in filteredRules"
					:key="rule.id"
					:class="['rule-item', { selected: selectedRuleIds.has(rule.id) }]"
				>
					<div class="rule-checkbox">
						<input
							type="checkbox"
							:checked="selectedRuleIds.has(rule.id)"
							@change="toggleRuleSelection(rule.id)"
						/>
					</div>
					<div class="rule-code">{{ rule.code }}</div>
					<div class="rule-thirty-d">
						<span
							:class="['thirty-d-badge', rule.thirtyD === 'Y' ? 'yes' : 'no']"
						>
							{{ rule.thirtyD }}
						</span>
					</div>
					<div class="rule-match-rules">
						<div class="match-rules-list">
							<span
								v-for="(matchRule, index) in rule.matchRules"
								:key="index"
								class="match-rule-tag"
							>
								{{ matchRule }}
							</span>
						</div>
					</div>
					<div class="rule-source">
						<span :class="['source-badge', rule.source]">
							{{ rule.source === "default" ? "默认" : "用户" }}
						</span>
					</div>
					<div class="rule-actions">
						<button class="btn btn-sm" @click="openEditor(rule)">
							✏️ 编辑
						</button>
						<button
							class="btn btn-sm"
							@click="deleteRule(rule.id)"
							:disabled="rule.source === 'default'"
						>
							🗑️ 删除
						</button>
					</div>
				</div>
			</div>
		</div>

		<!-- 统计信息 -->
		<div class="rule-stats">
			<div class="stats-item">
				<span class="stats-label">总规则:</span>
				<span class="stats-value">{{ ruleStore.ruleCount }}</span>
			</div>
			<div class="stats-item">
				<span class="stats-label">默认规则:</span>
				<span class="stats-value">{{ ruleStore.systemRules.length }}</span>
			</div>
			<div class="stats-item">
				<span class="stats-label">用户规则:</span>
				<span class="stats-value">{{ ruleStore.userRules.length }}</span>
			</div>
			<div class="stats-item">
				<span class="stats-label">选中:</span>
				<span class="stats-value">{{ selectedRules.length }}</span>
			</div>
		</div>

		<!-- 规则编辑器 -->
		<RuleEditor
			v-if="showEditor"
			:key="editingRule?.id || 'new'"
			:rule="editingRule"
			@save="handleRuleSaved"
			@cancel="closeEditor"
		/>
	</div>
</template>

<style scoped lang="scss">
.rule-manager {
	display: flex;
	flex-direction: column;
	height: 100%;
	background: var(--color-background-primary);
}

.rule-toolbar {
	display: flex;
	align-items: center;
	gap: var(--spacing-lg);
	padding: var(--spacing-lg);
	background: var(--color-background-secondary);
	border-bottom: 1px solid var(--color-border-primary);

	.toolbar-left,
	.toolbar-right {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
	}

	.toolbar-center {
		flex: 1;
		display: flex;
		justify-content: center;

		.search-input {
			width: 300px;
		}
	}
}

.rule-list {
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.rule-header {
	display: grid;
	grid-template-columns: 40px 120px 60px 1fr 80px 120px;
	gap: var(--spacing-md);
	padding: var(--spacing-md) var(--spacing-lg);
	background: var(--color-background-tertiary);
	border-bottom: 1px solid var(--color-border-primary);
	font-weight: var(--font-weight-semibold);
	font-size: var(--font-size-sm);
	color: var(--color-text-primary);
}

.rule-items {
	flex: 1;
	overflow-y: auto;
}

.rule-item {
	display: grid;
	grid-template-columns: 40px 120px 60px 1fr 80px 120px;
	gap: var(--spacing-md);
	padding: var(--spacing-md) var(--spacing-lg);
	border-bottom: 1px solid var(--color-border-secondary);
	transition: all var(--transition-fast);

	&:hover {
		background: var(--color-background-secondary);
	}

	&.selected {
		background: rgba(0, 122, 255, 0.1);
	}

	.rule-code {
		font-family: var(--font-family-mono);
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-medium);
	}

	.thirty-d-badge {
		display: inline-block;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-xs);
		font-weight: var(--font-weight-bold);

		&.yes {
			background: var(--color-warning);
			color: white;
		}

		&.no {
			background: var(--color-success);
			color: white;
		}
	}

	.match-rules-list {
		display: flex;
		flex-wrap: wrap;
		gap: var(--spacing-xs);

		.match-rule-tag {
			display: inline-block;
			padding: 2px 6px;
			background: var(--color-background-tertiary);
			border-radius: var(--radius-sm);
			font-size: var(--font-size-xs);
			color: var(--color-text-secondary);
		}
	}

	.source-badge {
		display: inline-block;
		padding: 2px 6px;
		border-radius: var(--radius-sm);
		font-size: var(--font-size-xs);
		font-weight: var(--font-weight-medium);

		&.default {
			background: var(--color-background-tertiary);
			color: var(--color-text-secondary);
		}

		&.user {
			background: var(--color-primary);
			color: white;
		}
	}

	.rule-actions {
		display: flex;
		gap: var(--spacing-xs);
	}
}

.rule-stats {
	display: flex;
	align-items: center;
	gap: var(--spacing-xl);
	padding: var(--spacing-md) var(--spacing-lg);
	background: var(--color-background-secondary);
	border-top: 1px solid var(--color-border-primary);
	font-size: var(--font-size-sm);

	.stats-item {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);

		.stats-label {
			color: var(--color-text-secondary);
		}

		.stats-value {
			color: var(--color-text-primary);
			font-weight: var(--font-weight-semibold);
		}
	}
}
</style>
