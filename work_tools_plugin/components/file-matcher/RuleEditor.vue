<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import { useRuleStore } from "../../stores/ruleStore";
import type { Rule } from "../../types/rule";

// Props
interface Props {
	rule?: Rule | null;
}

const props = defineProps<Props>();

// Emits
const emit = defineEmits<{
	save: [];
	cancel: [];
}>();

const ruleStore = useRuleStore();

// 表单数据
const formData = ref({
	code: "",
	thirtyD: "N",
	matchRules: [""],
});

// 验证状态
const errors = ref<Record<string, string>>({});

// 计算属性
const isEditing = computed(() => !!props.rule);
const title = computed(() => (isEditing.value ? "编辑规则" : "添加规则"));

// 组件挂载时初始化
onMounted(() => {
	initializeForm();
});

// 监听props变化
watch(
	() => props.rule,
	() => {
		initializeForm();
	},
	{ immediate: false }
);

function initializeForm() {
	if (props.rule) {
		formData.value = {
			code: props.rule.code,
			thirtyD: props.rule.thirtyD,
			matchRules: [...props.rule.matchRules],
		};
	} else {
		resetForm();
	}
}

// 方法
function resetForm() {
	formData.value = {
		code: "",
		thirtyD: "N",
		matchRules: [""],
	};
	errors.value = {};
}

function addMatchRule() {
	formData.value.matchRules.push("");
}

function removeMatchRule(index: number) {
	if (formData.value.matchRules.length > 1) {
		formData.value.matchRules.splice(index, 1);
	}
}

function validateForm(): boolean {
	errors.value = {};

	// 验证代码
	if (!formData.value.code.trim()) {
		errors.value.code = "代码不能为空";
	}

	// 验证匹配规则
	const validMatchRules = formData.value.matchRules.filter((rule) =>
		rule.trim()
	);
	if (validMatchRules.length === 0) {
		errors.value.matchRules = "至少需要一个匹配规则";
	}

	// 检查代码是否重复
	const existingRule = ruleStore.rules.find(
		(rule) => rule.code === formData.value.code && rule.id !== props.rule?.id
	);
	if (existingRule) {
		errors.value.code = "代码已存在";
	}

	return Object.keys(errors.value).length === 0;
}

function handleSave() {
	if (!validateForm()) return;

	// 过滤空的匹配规则
	const cleanMatchRules = formData.value.matchRules.filter((rule) =>
		rule.trim()
	);

	if (isEditing.value && props.rule) {
		// 更新现有规则
		ruleStore.updateRule(props.rule.id, {
			code: formData.value.code.trim(),
			thirtyD: formData.value.thirtyD,
			matchRules: cleanMatchRules,
		});
	} else {
		// 添加新规则
		ruleStore.addRule({
			code: formData.value.code.trim(),
			thirtyD: formData.value.thirtyD,
			matchRules: cleanMatchRules,
		});
	}

	emit("save");
}

function handleCancel() {
	emit("cancel");
}

// 快捷键处理
function handleKeydown(e: KeyboardEvent) {
	if (e.key === "Escape") {
		handleCancel();
	} else if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
		handleSave();
	}
}
</script>

<template>
	<Teleport to="body">
		<div
			class="rule-editor-overlay"
			@click.self="handleCancel"
			@keydown="handleKeydown"
			tabindex="0"
		>
			<div class="rule-editor">
				<!-- 标题栏 -->
				<div class="editor-header">
					<h3 class="editor-title">{{ title }}</h3>
					<button class="btn btn-sm" @click="handleCancel">✕</button>
				</div>

				<!-- 表单内容 -->
				<div class="editor-content">
					<form @submit.prevent="handleSave">
						<!-- 代码字段 -->
						<div class="form-group">
							<label class="form-label">代码 *</label>
							<input
								v-model="formData.code"
								type="text"
								class="input"
								:class="{ error: errors.code }"
								placeholder="例如: 01.33.06.01"
								maxlength="50"
							/>
							<div v-if="errors.code" class="error-message">
								{{ errors.code }}
							</div>
						</div>

						<!-- 30D字段 -->
						<div class="form-group">
							<label class="form-label">30D标记</label>
							<select v-model="formData.thirtyD" class="input">
								<option value="N">N - 否</option>
								<option value="Y">Y - 是</option>
							</select>
							<div class="form-hint">标记文件是否需要在30天内处理</div>
						</div>

						<!-- 匹配规则字段 -->
						<div class="form-group">
							<label class="form-label">匹配规则 *</label>
							<div class="match-rules-container">
								<div
									v-for="(matchRule, index) in formData.matchRules"
									:key="index"
									class="match-rule-row"
								>
									<input
										v-model="formData.matchRules[index]"
										type="text"
										class="input"
										:placeholder="`匹配规则 ${index + 1}`"
									/>
									<button
										type="button"
										class="btn btn-sm"
										@click="removeMatchRule(index)"
										:disabled="formData.matchRules.length <= 1"
									>
										➖
									</button>
								</div>
								<button type="button" class="btn btn-sm" @click="addMatchRule">
									➕ 添加规则
								</button>
							</div>
							<div v-if="errors.matchRules" class="error-message">
								{{ errors.matchRules }}
							</div>
							<div class="form-hint">文件名包含任一规则即可匹配</div>
						</div>
					</form>
				</div>

				<!-- 操作按钮 -->
				<div class="editor-footer">
					<button class="btn" @click="handleCancel">取消</button>
					<button class="btn btn-primary" @click="handleSave">
						{{ isEditing ? "更新" : "添加" }}
					</button>
				</div>
			</div>
		</div>
	</Teleport>
</template>

<style scoped lang="scss">
.rule-editor-overlay {
	position: fixed;
	top: 0;
	left: 0;
	right: 0;
	bottom: 0;
	background: var(--color-overlay);
	display: flex;
	align-items: center;
	justify-content: center;
	z-index: 1000;
	backdrop-filter: blur(4px);
}

.rule-editor {
	background: var(--color-background-primary);
	border-radius: var(--radius-lg);
	box-shadow: var(--shadow-lg);
	width: 90%;
	max-width: 600px;
	max-height: 80vh;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.editor-header {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: var(--spacing-lg);
	background: var(--color-background-secondary);
	border-bottom: 1px solid var(--color-border-primary);

	.editor-title {
		font-size: var(--font-size-lg);
		font-weight: var(--font-weight-semibold);
		color: var(--color-text-primary);
		margin: 0;
	}
}

.editor-content {
	flex: 1;
	padding: var(--spacing-lg);
	overflow-y: auto;
}

.form-group {
	margin-bottom: var(--spacing-lg);

	.form-label {
		display: block;
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-semibold);
		color: var(--color-text-primary);
		margin-bottom: var(--spacing-sm);
	}

	.input {
		width: 100%;

		&.error {
			border-color: var(--color-error);
		}
	}

	.form-hint {
		font-size: var(--font-size-xs);
		color: var(--color-text-tertiary);
		margin-top: var(--spacing-xs);
	}

	.error-message {
		font-size: var(--font-size-xs);
		color: var(--color-error);
		margin-top: var(--spacing-xs);
	}
}

.match-rules-container {
	.match-rule-row {
		display: flex;
		gap: var(--spacing-sm);
		margin-bottom: var(--spacing-sm);
		align-items: center;

		.input {
			flex: 1;
		}
	}
}

.editor-footer {
	display: flex;
	justify-content: flex-end;
	gap: var(--spacing-md);
	padding: var(--spacing-lg);
	background: var(--color-background-secondary);
	border-top: 1px solid var(--color-border-primary);
}
</style>
