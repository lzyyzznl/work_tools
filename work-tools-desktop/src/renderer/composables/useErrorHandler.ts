import { useErrorHandlerStore } from "../stores/errorHandlerStore";
import type { OperationLog } from "../types/common";

export interface ErrorInfo {
	id: string;
	type: "error" | "info"; // 简化为只有错误和信息两种类型
	title: string;
	message: string;
	timestamp: number;
	duration?: number;
}

export function useErrorHandler() {
	const store = useErrorHandlerStore();

	function showNativeNotification(
		type: "error" | "info",
		title: string,
		message: string
	) {
		// 使用浏览器的Notification API显示原生通知
		if ("Notification" in window) {
			// 请求通知权限
			if (Notification.permission === "default") {
				Notification.requestPermission();
			}

			// 创建通知
			if (Notification.permission === "granted") {
				const icon =
					type === "error"
						? "❌"
						: "ℹ️";

				new Notification(`${icon} ${title}`, {
					body: message,
					icon: icon,
					silent: false,
					requireInteraction: type === "error", // 错误通知需要用户手动关闭
				});
			}
		}

		// 同时在控制台输出，方便调试
		const logMethod = type === "error" ? "error" : "log";
		console[logMethod](`[${title}] ${message}`);
	}

	// 独立的错误提示函数，只负责显示提示信息，不记录操作日志
	function addError(error: Omit<ErrorInfo, "id" | "timestamp">) {
		const errorInfo: ErrorInfo = {
			...error,
			id: `error_${Date.now()}_${Math.random()}`,
			timestamp: Date.now(),
			duration: error.duration || (error.type === "error" ? 5000 : 3000),
		};

		store.addError(errorInfo);

		// 显示原生通知
		showNativeNotification(error.type, error.title, error.message);

		// 自动移除
		if (errorInfo.duration && errorInfo.duration > 0) {
			setTimeout(() => {
				removeError(errorInfo.id);
			}, errorInfo.duration);
		}

		return errorInfo.id;
	}

	function removeError(id: string) {
		store.removeError(id);
	}

	function clearErrors() {
		store.clearErrors();
	}

	// 独立的操作日志函数，只负责记录操作日志，不显示任何提示
	function addOperationLog(log: Omit<OperationLog, "id" | "timestamp">) {
		return store.addOperationLog(log);
	}

	function clearOperationLogs() {
		store.clearOperationLogs();
	}

	function searchOperationLogs(query: string): OperationLog[] {
		return store.searchOperationLogs(query);
	}

	// 错误处理函数，只处理错误提示
	function handleError(error: any, context?: string) {
		console.error("Error in", context || "unknown context", error);

		let message = "发生未知错误";
		let title = "错误";

		if (error instanceof Error) {
			message = error.message;
			title = error.name || "错误";
		} else if (typeof error === "string") {
			message = error;
		} else if (error && typeof error === "object") {
			message = error.message || error.toString();
			title = error.name || error.type || "错误";
		}

		return addError({
			type: "error",
			title,
			message: context ? `${context}: ${message}` : message,
		});
	}

	// 信息提示函数，只处理信息提示
	function handleSuccess(message: string, title = "成功") {
		return addError({
			type: "info",
			title,
			message,
			duration: 3000,
		});
	}

	// 信息提示函数，只处理信息提示
	function handleWarning(message: string, title = "警告") {
		return addError({
			type: "info",
			title,
			message,
			duration: 3000,
		});
	}

	// 信息提示函数，只处理信息提示
	function handleInfo(message: string, title = "信息") {
		return addError({
			type: "info",
			title,
			message,
			duration: 3000,
		});
	}

	// 操作日志记录函数，只记录操作日志，不显示任何提示
	function logOperation(type: string, message: string, details?: any, fileList?: string[], stats?: { total?: number; success?: number; failed?: number }) {
		// 记录操作日志
		return store.addOperationLog({
			type,
			message,
			level: "info",
			details,
			fileList,
			stats,
		});
	}

	// 保持向后兼容性的函数
	function handleOperation(type: string, message: string, details?: any, fileList?: string[], stats?: { total?: number; success?: number; failed?: number }) {
		// 记录操作日志
		logOperation(type, message, details, fileList, stats);
		
		// 同时显示信息通知
		handleInfo(message, type);
	}
	
	// 增强的操作日志记录函数，支持更详细的日志信息
	function handleDetailedOperation(type: string, message: string, options?: {
		details?: any;
		fileList?: string[];
		stats?: { total?: number; success?: number; failed?: number };
		level?: "info" | "success" | "warning" | "error";
		renameDetails?: Array<{ oldName: string; newName: string }>;
	}) {
		// 记录操作日志
		store.addOperationLog({
			type,
			message,
			level: options?.level || "info",
			details: options?.details,
			fileList: options?.fileList,
			stats: options?.stats,
		});
		
		// 同时显示信息通知
		if (options?.level === "error") {
			handleError(new Error(message), type);
		} else {
			handleInfo(message, type);
		}
	}

	return {
		// 保持原有的响应式属性，但指向 store 中的数据
		errors: store.errors,
		maxErrors: store.maxErrors,
		operationLogs: store.operationLogs,
		maxLogs: store.maxLogs,
		
		// 原有的方法
		addError,
		removeError,
		clearErrors,
		handleError,
		handleSuccess,
		handleWarning,
		handleInfo,
		handleOperation,
		logOperation,
		handleDetailedOperation,
		
		// 保持向后兼容性的方法
		addOperationLog,
		clearOperationLogs,
		searchOperationLogs,
	};
}
