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
	saved: [];
	close: [];
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

// 保存状态
const isSaving = ref(false);
const saveError = ref<string>("");

// 预览状态
const previewMode = ref(false);
const testFileName = ref("");
const testResult = ref<{ matched: boolean; matchedRule?: string } | null>(null);

// 计算属性
const isEditing = computed(() => !!props.rule);
const isEditingDefault = computed(
	() => isEditing.value && props.rule?.source === "default"
);
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

// 监听表单数据变化，自动清除错误
watch(
	() => formData.value,
	() => {
		if (saveError.value) {
			saveError.value = "";
		}
	},
	{ deep: true }
);

function initializeForm() {
	if (props.rule) {
		formData.value = {
			code: props.rule.code || "",
			thirtyD: props.rule.thirtyD || "N",
			matchRules: Array.isArray(props.rule.matchRules)
				? [...props.rule.matchRules]
				: [""],
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
	saveError.value = "";
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
	const matchRules = Array.isArray(formData.value.matchRules)
		? formData.value.matchRules
		: [];
	const validMatchRules = matchRules.filter((rule) => rule && rule.trim());
	if (validMatchRules.length === 0) {
		errors.value.matchRules = "至少需要一个匹配规则";
	}

	// 检查代码是否重复
	if (formData.value.code.trim()) {
		let hasConflict = false;

		if (isEditing.value && props.rule) {
			// 编辑模式：检查是否与其他规则冲突
			if (props.rule.source === "default") {
				// 编辑默认规则：检查是否与其他规则冲突（排除同代码的默认规则）
				hasConflict = ruleStore.rules.some(
					(rule) =>
						rule.code === formData.value.code &&
						!(rule.code === props.rule!.code && rule.source === "default")
				);
			} else {
				// 编辑用户规则：检查是否与其他规则冲突（排除自己）
				hasConflict = ruleStore.rules.some(
					(rule) =>
						rule.code === formData.value.code && rule.id !== props.rule!.id
				);
			}
		} else {
			// 新增模式：检查是否与任何现有规则冲突
			hasConflict = ruleStore.rules.some(
				(rule) => rule.code === formData.value.code
			);
		}

		if (hasConflict) {
			errors.value.code = "代码已存在";
		}
	}

	return Object.keys(errors.value).length === 0;
}

async function handleSave() {
	if (!validateForm()) return;

	// 清除之前的错误
	saveError.value = "";
	isSaving.value = true;

	try {
		// 过滤空的匹配规则
		const matchRules = Array.isArray(formData.value.matchRules)
			? formData.value.matchRules
			: [];
		const cleanMatchRules = matchRules.filter((rule) => rule && rule.trim());

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

		emit("saved");
	} catch (error) {
		// 捕获并显示错误
		saveError.value =
			error instanceof Error ? error.message : "保存失败，请重试";
	} finally {
		isSaving.value = false;
	}
}

function handleCancel() {
	emit("close");
}

// 规则测试功能
function testRule() {
	if (!testFileName.value.trim()) {
		testResult.value = null;
		return;
	}

	const fileName = testFileName.value.trim();
	const matchRules = Array.isArray(formData.value.matchRules)
		? formData.value.matchRules
		: [];
	const validMatchRules = matchRules.filter((rule) => rule && rule.trim());

	for (const matchRule of validMatchRules) {
		if (matchRule && fileName.includes(matchRule)) {
			testResult.value = {
				matched: true,
				matchedRule: matchRule,
			};
			return;
		}
	}

	testResult.value = { matched: false };
}

function togglePreview() {
	previewMode.value = !previewMode.value;
	if (!previewMode.value) {
		testResult.value = null;
		testFileName.value = "";
	}
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
					<!-- 默认规则编辑提示 -->
					<div v-if="isEditingDefault" class="default-rule-notice">
						<div class="notice-content">
							<span class="notice-icon">ℹ️</span>
							<span class="notice-text">
								您正在编辑默认规则，保存后将创建用户规则来覆盖此默认规则。
							</span>
						</div>
					</div>

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

						<!-- 错误信息显示 -->
						<div v-if="saveError" class="form-group">
							<div class="error-banner">
								<span class="error-icon">⚠️</span>
								<span class="error-text">{{ saveError }}</span>
								<button
									type="button"
									class="error-close"
									@click="saveError = ''"
								>
									✕
								</button>
							</div>
						</div>

						<!-- 匹配规则字段 -->
						<div class="form-group">
							<div class="form-label-with-action">
								<label class="form-label">匹配规则 *</label>
								<button
									type="button"
									class="btn btn-sm"
									@click="togglePreview"
									:class="{ active: previewMode }"
								>
									{{ previewMode ? "📝 编辑" : "🔍 测试" }}
								</button>
							</div>

							<div v-if="!previewMode" class="match-rules-container">
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

							<!-- 规则测试区域 -->
							<div v-else class="rule-test-container">
								<div class="test-input-group">
									<label class="test-label">测试文件名:</label>
									<input
										v-model="testFileName"
										type="text"
										class="input"
										placeholder="输入文件名进行测试..."
										@input="testRule"
									/>
								</div>
								<div v-if="testResult" class="test-result">
									<div v-if="testResult.matched" class="result-success">
										✅ 匹配成功！匹配规则: {{ testResult.matchedRule }}
									</div>
									<div v-else class="result-failure">❌ 未匹配到任何规则</div>
								</div>
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
					<button class="btn" @click="handleCancel" :disabled="isSaving">
						取消
					</button>
					<button
						class="btn btn-primary"
						@click="handleSave"
						:disabled="isSaving"
					>
						<span v-if="isSaving">保存中...</span>
						<span v-else>{{ isEditing ? "更新" : "添加" }}</span>
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

.form-label-with-action {
	display: flex;
	justify-content: space-between;
	align-items: center;
	margin-bottom: var(--spacing-sm);

	.btn.active {
		background: var(--color-primary);
		color: white;
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

.rule-test-container {
	.test-input-group {
		margin-bottom: var(--spacing-md);

		.test-label {
			display: block;
			font-size: var(--font-size-sm);
			font-weight: var(--font-weight-medium);
			color: var(--color-text-primary);
			margin-bottom: var(--spacing-xs);
		}
	}

	.test-result {
		padding: var(--spacing-md);
		border-radius: var(--radius-md);
		font-size: var(--font-size-sm);

		.result-success {
			color: var(--color-success);
			background: rgba(34, 197, 94, 0.1);
			padding: var(--spacing-sm);
			border-radius: var(--radius-sm);
		}

		.result-failure {
			color: var(--color-error);
			background: rgba(239, 68, 68, 0.1);
			padding: var(--spacing-sm);
			border-radius: var(--radius-sm);
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

.error-banner {
	display: flex;
	align-items: center;
	gap: var(--spacing-sm);
	padding: var(--spacing-md);
	background: rgba(239, 68, 68, 0.1);
	border: 1px solid rgba(239, 68, 68, 0.2);
	border-radius: var(--radius-md);
	color: var(--color-error);

	.error-icon {
		font-size: var(--font-size-lg);
	}

	.error-text {
		flex: 1;
		font-size: var(--font-size-sm);
		font-weight: var(--font-weight-medium);
	}

	.error-close {
		background: none;
		border: none;
		color: var(--color-error);
		cursor: pointer;
		padding: var(--spacing-xs);
		border-radius: var(--radius-sm);
		font-size: var(--font-size-sm);
		transition: background-color var(--transition-fast);

		&:hover {
			background: rgba(239, 68, 68, 0.1);
		}
	}
}

.default-rule-notice {
	margin-bottom: var(--spacing-lg);

	.notice-content {
		display: flex;
		align-items: center;
		gap: var(--spacing-sm);
		padding: var(--spacing-md);
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid rgba(59, 130, 246, 0.2);
		border-radius: var(--radius-md);
		color: var(--color-primary);

		.notice-icon {
			font-size: var(--font-size-lg);
		}

		.notice-text {
			flex: 1;
			font-size: var(--font-size-sm);
			font-weight: var(--font-weight-medium);
		}
	}
}
</style>
