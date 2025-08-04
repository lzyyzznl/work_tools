import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type { OperationLog } from "../types/common";
import type { ErrorInfo } from "../composables/useErrorHandler";

export const useErrorHandlerStore = defineStore("error-handler", () => {
	// 错误状态
	const errors = ref<ErrorInfo[]>([]);
	const maxErrors = ref(10);
	
	// 操作日志状态
	const operationLogs = ref<OperationLog[]>([]);
	const maxLogs = ref(100);

	// 计算属性
	const errorCount = computed(() => errors.value.length);
	const logCount = computed(() => operationLogs.value.length);

	// 操作日志相关方法
	function addOperationLog(log: Omit<OperationLog, "id" | "timestamp">) {
		const logInfo: OperationLog = {
			...log,
			id: `log_${Date.now()}_${Math.random()}`,
			timestamp: Date.now(),
		};

		operationLogs.value.unshift(logInfo);

		// 限制日志数量
		if (operationLogs.value.length > maxLogs.value) {
			operationLogs.value = operationLogs.value.slice(0, maxLogs.value);
		}

		return logInfo.id;
	}

	function clearOperationLogs() {
		operationLogs.value = [];
	}

	function searchOperationLogs(query: string): OperationLog[] {
		if (!query.trim()) {
			return operationLogs.value;
		}

		const lowerQuery = query.toLowerCase();
		return operationLogs.value.filter(
			(log) =>
				log.message.toLowerCase().includes(lowerQuery) ||
				log.type.toLowerCase().includes(lowerQuery)
		);
	}

	// 错误处理相关方法
	function addError(error: Omit<ErrorInfo, "id" | "timestamp">) {
		const errorInfo: ErrorInfo = {
			...error,
			id: `error_${Date.now()}_${Math.random()}`,
			timestamp: Date.now(),
			duration: error.duration || (error.type === "error" ? 5000 : 3000),
		};

		errors.value.unshift(errorInfo);

		// 限制错误数量
		if (errors.value.length > maxErrors.value) {
			errors.value = errors.value.slice(0, maxErrors.value);
		}

		// 自动移除
		if (errorInfo.duration && errorInfo.duration > 0) {
			setTimeout(() => {
				removeError(errorInfo.id);
			}, errorInfo.duration);
		}

		return errorInfo.id;
	}

	function removeError(id: string) {
		const index = errors.value.findIndex((e) => e.id === id);
		if (index > -1) {
			errors.value.splice(index, 1);
		}
	}

	function clearErrors() {
		errors.value = [];
	}

	return {
		// 状态
		errors,
		maxErrors,
		operationLogs,
		maxLogs,
		
		// 计算属性
		errorCount,
		logCount,
		
		// 操作日志方法
		addOperationLog,
		clearOperationLogs,
		searchOperationLogs,
		
		// 错误处理方法
		addError,
		removeError,
		clearErrors,
	};
});