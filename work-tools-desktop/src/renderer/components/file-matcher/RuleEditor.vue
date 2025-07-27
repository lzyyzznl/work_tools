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
			class="fixed top-0 left-0 right-0 bottom-0 bg-overlay flex items-center justify-center z-1000 backdrop-blur-4px"
			@click.self="handleCancel"
			@keydown="handleKeydown"
			tabindex="0"
		>
			<div
				class="bg-white rounded-lg shadow-xl w-full max-w-600px max-h-80vh flex flex-col overflow-hidden"
			>
				<!-- 标题栏 -->
				<div
					class="flex items-center justify-between p-4 border-b border-gray-200 bg-gray-50"
				>
					<h3 class="text-lg font-semibold text-gray-900 m-0">
						{{ title }}
					</h3>
					<button
						@click="handleCancel"
						class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors"
					>
						<span class="text-xl">✕</span>
					</button>
				</div>

				<!-- 表单内容 -->
				<div class="flex-1 p-6 overflow-y-auto">
					<!-- 默认规则编辑提示 -->
					<div v-if="isEditingDefault" class="mb-6">
						<div
							class="flex items-center gap-3 p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-800"
						>
							<span class="text-lg">ℹ️</span>
							<span class="flex-1 text-sm font-medium">
								您正在编辑默认规则，保存后将创建用户规则来覆盖此默认规则。
							</span>
						</div>
					</div>

					<form @submit.prevent="handleSave">
						<!-- 代码字段 -->
						<div class="mb-6">
							<label class="block text-sm font-semibold text-gray-700 mb-2"
								>代码 *</label
							>
							<input
								v-model="formData.code"
								type="text"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
								:class="{ 'border-red-500': errors.code }"
								placeholder="例如: 01.33.06.01"
								maxlength="50"
							/>
							<div v-if="errors.code" class="text-xs text-red-600 mt-1">
								{{ errors.code }}
							</div>
						</div>

						<!-- 30D字段 -->
						<div class="mb-6">
							<label class="block text-sm font-semibold text-gray-700 mb-2"
								>30D标记</label
							>
							<select
								v-model="formData.thirtyD"
								class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
							>
								<option value="N">N - 否</option>
								<option value="Y">Y - 是</option>
							</select>
							<div class="text-xs text-gray-500 mt-1">
								标记文件是否需要在30天内处理
							</div>
						</div>

						<!-- 错误信息显示 -->
						<div v-if="saveError" class="mb-6">
							<div
								class="flex items-center gap-3 p-4 bg-red-50 border border-red-200 rounded-lg text-red-800"
							>
								<span class="text-lg">⚠️</span>
								<span class="flex-1 text-sm font-medium">{{ saveError }}</span>
								<button
									type="button"
									@click="saveError = ''"
									class="p-1 text-red-400 hover:text-red-600 hover:bg-red-100 rounded transition-colors"
								>
									<span class="text-lg">✕</span>
								</button>
							</div>
						</div>

						<!-- 匹配规则字段 -->
						<div class="mb-6">
							<div class="flex justify-between items-center mb-2">
								<label class="block text-sm font-semibold text-gray-700"
									>匹配规则 *</label
								>
								<button
									type="button"
									@click="togglePreview"
									class="px-3 py-1 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
									:class="{ 'bg-blue-600 text-white': previewMode }"
								>
									{{ previewMode ? "📝 编辑" : "🔍 测试" }}
								</button>
							</div>

							<div v-if="!previewMode" class="match-rules-container">
								<div
									v-for="(matchRule, index) in formData.matchRules"
									:key="index"
									class="flex gap-3 mb-3 items-center"
								>
									<input
										v-model="formData.matchRules[index]"
										type="text"
										class="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
										:placeholder="`匹配规则 ${index + 1}`"
									/>
									<button
										type="button"
										@click="removeMatchRule(index)"
										:disabled="formData.matchRules.length <= 1"
										class="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
									>
										<span class="text-lg">➖</span>
									</button>
								</div>
								<button
									type="button"
									@click="addMatchRule"
									class="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors"
								>
									➕ 添加规则
								</button>
							</div>

							<!-- 规则测试区域 -->
							<div v-else class="rule-test-container">
								<div class="mb-4">
									<label class="block text-sm font-medium text-gray-700 mb-1"
										>测试文件名:</label
									>
									<input
										v-model="testFileName"
										type="text"
										class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
										placeholder="输入文件名进行测试..."
										@input="testRule"
									/>
								</div>
								<div v-if="testResult" class="p-4 rounded-lg text-sm">
									<div
										v-if="testResult.matched"
										class="text-green-800 bg-green-50 p-3 rounded-lg"
									>
										✅ 匹配成功！匹配规则: {{ testResult.matchedRule }}
									</div>
									<div v-else class="text-red-800 bg-red-50 p-3 rounded-lg">
										❌ 未匹配到任何规则
									</div>
								</div>
							</div>

							<div v-if="errors.matchRules" class="text-xs text-red-600 mt-1">
								{{ errors.matchRules }}
							</div>
							<div class="text-xs text-gray-500 mt-1">
								文件名包含任一规则即可匹配
							</div>
						</div>
					</form>
				</div>

				<!-- 操作按钮 -->
				<div
					class="flex justify-end gap-3 p-6 bg-gray-50 border-t border-gray-200"
				>
					<button
						@click="handleCancel"
						:disabled="isSaving"
						class="px-6 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						取消
					</button>
					<button
						@click="handleSave"
						:disabled="isSaving"
						class="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
					>
						<span v-if="isSaving">保存中...</span>
						<span v-else>{{ isEditing ? "更新" : "添加" }}</span>
					</button>
				</div>
			</div>
		</div>
	</Teleport>
</template>
