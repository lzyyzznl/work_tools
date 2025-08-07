<template>
	<div class="log-panel flex flex-col h-full">
		<!-- 面板标题和控制按钮 -->
		<div
			class="log-header flex flex-col sm:flex-row sm:items-center justify-between p-3 border-b border-gray-200 bg-gray-50 flex-shrink-0 gap-2"
		>
			<h3 class="text-sm font-medium text-gray-900">操作日志</h3>
			<div class="flex flex-wrap items-center gap-2">
				<!-- 日志级别过滤 -->
				<div class="flex items-center gap-1">
					<label class="text-xs text-gray-600">级别:</label>
					<select
						v-model="filterLevel"
						class="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
					>
						<option value="">全部</option>
						<option value="info">信息</option>
						<option value="success">成功</option>
						<option value="warning">警告</option>
						<option value="error">错误</option>
					</select>
				</div>
				
				<input
					v-model="searchQuery"
					type="text"
					placeholder="搜索日志..."
					class="px-2 py-1 text-xs border border-gray-300 rounded focus:outline-none focus:ring-1 focus:ring-blue-500"
				/>
				<button
					@click="clearLogs"
					class="px-2 py-1 text-xs bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
					title="清空日志"
				>
					清空
				</button>
				<button
					@click="toggleExpand"
					class="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors"
					:title="isExpanded ? '收起' : '展开'"
				>
					{{ isExpanded ? "收起" : "展开" }}
				</button>
			</div>
		</div>

		<!-- 日志列表 -->
		<div
			v-if="isExpanded"
			class="log-content flex-1 overflow-y-auto bg-white"
			:class="isExpanded ? 'max-h-full' : 'max-h-6'"
		>
			<div
				v-for="log in filteredLogs"
				:key="log.id"
				class="log-item border-b border-gray-100 hover:bg-gray-50 transition-colors"
				:class="{
					'bg-red-50': log.level === 'error',
					'bg-green-50': log.level === 'success',
					'bg-yellow-50': log.level === 'warning',
					'bg-blue-50': log.level === 'info',
				}"
			>
				<div class="px-3 py-2 text-xs">
					<div class="flex items-center justify-between">
						<span
							class="font-medium flex items-center"
							:class="{
								'text-red-700': log.level === 'error',
								'text-green-700': log.level === 'success',
								'text-yellow-700': log.level === 'warning',
								'text-blue-700': log.level === 'info',
							}"
						>
							<!-- 日志级别图标 -->
							<span class="mr-1">
								<span v-if="log.level === 'error'">❌</span>
								<span v-else-if="log.level === 'success'">✅</span>
								<span v-else-if="log.level === 'warning'">⚠️</span>
								<span v-else>ℹ️</span>
							</span>
							{{ log.type }}
						</span>
						<span class="text-gray-500">
							{{ formatTime(log.timestamp) }}
						</span>
					</div>
					<div class="mt-1 text-gray-800 break-words">
						{{ log.message }}
					</div>
					<!-- 显示文件列表 -->
					<div
						v-if="log.fileList && log.fileList.length > 0"
						class="mt-1 text-gray-600"
					>
						<div class="font-medium text-xs flex items-center">
							<span>文件列表 ({{ log.fileList.length }} 个文件):</span>
						</div>
						<ul class="list-disc list-inside text-xs pl-2">
							<li v-for="(file, index) in log.fileList" :key="index">
								{{ file }}
							</li>
						</ul>
					</div>
					<!-- 显示统计信息 -->
					<div v-if="log.stats" class="mt-1 text-gray-600">
						<div class="font-medium text-xs">操作统计:</div>
						<div class="text-xs pl-2">
							<span v-if="log.stats.total !== undefined"
								>总计: {{ log.stats.total }}</span
							>
							<span v-if="log.stats.success !== undefined" class="ml-2"
								>成功: {{ log.stats.success }}</span
							>
							<span v-if="log.stats.failed !== undefined" class="ml-2"
								>失败: {{ log.stats.failed }}</span
							>
						</div>
					</div>
					<!-- 显示重命名详情 -->
					<div
						v-if="log.details && log.details.renameDetails"
						class="mt-1 text-gray-600"
					>
						<div class="font-medium text-xs">重命名详情:</div>
						<ul class="list-disc list-inside text-xs pl-2">
							<li
								v-for="(detail, index) in log.details.renameDetails"
								:key="index"
							>
								{{ detail.oldName }} → {{ detail.newName }}
							</li>
						</ul>
					</div>
				</div>
			</div>

			<!-- 空状态 -->
			<div
				v-if="filteredLogs.length === 0"
				class="p-4 text-center text-gray-500 text-sm"
			>
				暂无操作日志
			</div>
		</div>

		<!-- 收起状态下的简要信息 -->
		<div
			v-else
			class="log-summary px-3 py-2 text-xs bg-white border-b border-gray-200 flex-shrink-0"
		>
			<span class="text-gray-600"> {{ operationLogs.length }} 条日志 </span>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref, computed } from "vue";
import { useErrorHandlerStore } from "../../stores/errorHandlerStore";
import type { OperationLog } from "../../types/common";

const store = useErrorHandlerStore();
const { clearOperationLogs, searchOperationLogs, operationLogs } = store;

const isExpanded = ref(true);
const searchQuery = ref("");
const filterLevel = ref("");

const filteredLogs = computed(() => {
	let logs = searchOperationLogs(searchQuery.value);
	
	// 应用级别过滤
	if (filterLevel.value) {
		logs = logs.filter(log => log.level === filterLevel.value);
	}
	
	return logs;
});

function formatTime(timestamp: number): string {
	return new Date(timestamp).toLocaleTimeString("zh-CN", {
		hour12: false,
		hour: "2-digit",
		minute: "2-digit",
		second: "2-digit",
	});
}

function clearLogs() {
	clearOperationLogs();
}

function toggleExpand() {
	isExpanded.value = !isExpanded.value;
}
</script>

<style scoped>
.log-panel {
	font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas,
		"Liberation Mono", monospace;
}
</style>
