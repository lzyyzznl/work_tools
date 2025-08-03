<script setup lang="ts">
import { computed } from "vue";
import { useFileRenamerStore } from "../../stores/fileRenamerStore";
import { useRenameStore } from "../../stores/renameStore";
import { useRenameEngine } from "../../composables/useRenameEngine";

const fileStore = useFileRenamerStore();
const renameStore = useRenameStore();
const { checkConflicts, validateParams } = useRenameEngine();

// 计算预览统计信息
const previewStats = computed(() => {
	const files = fileStore.files;
	const totalFiles = files.length;
	const changedFiles = files.filter(
		(file) => file.previewName && file.previewName !== file.name
	).length;
	const unchangedFiles = totalFiles - changedFiles;

	return {
		total: totalFiles,
		changed: changedFiles,
		unchanged: unchangedFiles,
		hasChanges: changedFiles > 0,
	};
});

// 检查冲突和验证
const validationResult = computed(() => validateParams());
const conflictResult = computed(() => checkConflicts());

// 预览文件列表（限制显示数量以提高性能）
const previewFiles = computed(() => {
	return fileStore.files.slice(0, 100); // 只显示前100个文件
});

const hasMoreFiles = computed(() => fileStore.files.length > 100);

// 获取文件状态类
function getFileStatusClass(file: any): string {
	if (!file.previewName) return "no-preview";
	if (file.previewName === file.name) return "unchanged";
	return "changed";
}

// 获取文件状态图标
function getFileStatusIcon(file: any): string {
	if (!file.previewName) return "❓";
	if (file.previewName === file.name) return "➖";
	return "✏️";
}

// 获取文件状态文本
function getFileStatusText(file: any): string {
	if (!file.previewName) return "无预览";
	if (file.previewName === file.name) return "无变化";
	return "已修改";
}
</script>

<template>
	<div
		class="preview-panel flex flex-col gap-md bg-background-primary border border-border-primary rounded-lg p-lg overflow-hidden flex-1"
	>
		<!-- 预览头部 -->
		<div class="preview-header flex items-center justify-between gap-md">
			<h3
				class="preview-title flex items-center gap-sm m-0 text-lg font-semibold text-text-primary"
			>
				<span class="preview-icon text-xl">👁️</span>
				重命名预览
			</h3>

			<!-- 预览统计 -->
			<div class="preview-stats flex gap-md">
				<div class="stat-item flex items-center gap-xs text-sm">
					<span class="stat-label text-text-secondary">总计:</span>
					<span class="stat-value font-semibold text-text-primary">{{
						previewStats.total
					}}</span>
				</div>
				<div class="stat-item flex items-center gap-xs text-sm">
					<span class="stat-label text-text-secondary">将修改:</span>
					<span class="stat-value font-semibold text-success">{{
						previewStats.changed
					}}</span>
				</div>
				<div class="stat-item flex items-center gap-xs text-sm">
					<span class="stat-label text-text-secondary">无变化:</span>
					<span class="stat-value font-semibold text-text-primary">{{
						previewStats.unchanged
					}}</span>
				</div>
			</div>
		</div>

		<!-- 验证和冲突提示 -->
		<div
			v-if="!validationResult.isValid || conflictResult.hasConflicts"
			class="validation-alerts flex flex-col gap-sm"
		>
			<div
				v-if="!validationResult.isValid"
				class="alert flex gap-sm p-sm rounded-md text-sm bg-warning/10 border border-warning/20 text-warning"
			>
				<span class="alert-icon flex-shrink-0 text-base">⚠️</span>
				<div class="alert-content flex-1">
					<div class="alert-title font-semibold mb-xs">参数验证失败</div>
					<ul class="alert-list m-0 pl-md">
						<li
							v-for="error in validationResult.errors"
							:key="error"
							class="mb-xs"
						>
							{{ error }}
						</li>
					</ul>
				</div>
			</div>

			<div
				v-if="conflictResult.hasConflicts"
				class="alert flex gap-sm p-sm rounded-md text-sm bg-error/10 border border-error/20 text-error"
			>
				<span class="alert-icon flex-shrink-0 text-base">❌</span>
				<div class="alert-content flex-1">
					<div class="alert-title font-semibold mb-xs">发现重名冲突</div>
					<ul class="alert-list m-0 pl-md">
						<li
							v-for="conflict in conflictResult.conflicts"
							:key="conflict"
							class="mb-xs"
						>
							{{ conflict }}
						</li>
					</ul>
				</div>
			</div>
		</div>

		<!-- 预览状态 -->
		<div
			v-if="!previewStats.hasChanges && previewStats.total > 0"
			class="no-changes-message flex items-center gap-sm p-md bg-background-secondary rounded-md text-text-secondary text-sm"
		>
			<span class="message-icon text-base">ℹ️</span>
			<span class="message-text">当前设置不会对文件名产生任何更改</span>
		</div>

		<!-- 预览列表 -->
		<div
			v-if="previewStats.hasChanges"
			class="preview-list flex flex-col overflow-hidden flex-1"
		>
			<div
				class="list-header grid gap-sm p-sm bg-background-secondary rounded-t-md text-sm font-semibold text-text-primary"
			>
				<div class="header-item p-xs">状态</div>
				<div class="header-item p-xs">原文件名</div>
				<div class="header-item p-xs">新文件名</div>
			</div>

			<div
				class="list-content flex-1 overflow-y-auto border border-border-secondary border-t-0 rounded-b-md"
			>
				<div
					v-for="file in previewFiles"
					:key="file.id"
					:class="[
						'list-item grid gap-sm p-sm border-b border-border-secondary',
						getFileStatusClass(file),
					]"
				>
					<div class="item-status flex items-center gap-xs">
						<span class="status-icon text-sm">{{
							getFileStatusIcon(file)
						}}</span>
						<span class="status-text text-xs text-text-secondary">{{
							getFileStatusText(file)
						}}</span>
					</div>

					<div class="item-original flex items-center min-w-0">
						<span
							class="file-name overflow-hidden text-ellipsis whitespace-nowrap font-mono"
							:title="file.name"
							>{{ file.name }}</span
						>
					</div>

					<div class="item-preview flex items-center min-w-0">
						<span
							v-if="file.previewName && file.previewName !== file.name"
							class="file-name overflow-hidden text-ellipsis whitespace-nowrap font-mono text-primary font-medium"
							:title="file.previewName"
						>
							{{ file.previewName }}
						</span>
						<span v-else class="no-change text-text-tertiary italic">-</span>
					</div>
				</div>

				<!-- 更多文件提示 -->
				<div
					v-if="hasMoreFiles"
					class="more-files-notice flex items-center gap-sm p-md bg-background-secondary text-text-secondary text-sm text-center border-t border-border-secondary"
				>
					<span class="notice-icon text-base">📄</span>
					<span class="notice-text">
						还有
						{{ fileStore.files.length - 100 }}
						个文件未显示，执行时将处理所有文件
					</span>
				</div>
			</div>
		</div>

		<!-- 空状态 -->
		<div
			v-if="previewStats.total === 0"
			class="empty-state flex flex-col items-center justify-center p-3xl text-center"
		>
			<div class="empty-icon text-48px mb-lg opacity-50">📁</div>
			<div class="empty-text text-lg font-medium text-text-secondary mb-sm">
				暂无文件
			</div>
			<div class="empty-hint text-sm text-text-tertiary">
				请先添加要重命名的文件
			</div>
		</div>

		<!-- 预览操作 -->
		<div
			v-if="previewStats.total > 0"
			class="preview-actions flex items-center justify-between gap-md pt-md border-t border-border-secondary"
		>
			<div class="action-info">
				<span
					v-if="renameStore.previewUpdateTime"
					class="update-time text-xs text-text-tertiary"
				>
					上次更新:
					{{ new Date(renameStore.previewUpdateTime).toLocaleTimeString() }}
				</span>
			</div>

			<div class="action-buttons flex gap-sm">
				<button
					class="btn btn-sm btn-secondary"
					@click="$emit('refresh-preview')"
					:disabled="!renameStore.hasValidParams"
				>
					🔄 刷新预览
				</button>

				<button
					class="btn btn-sm btn-primary"
					@click="$emit('execute-rename')"
					:disabled="
						!previewStats.hasChanges ||
						!validationResult.isValid ||
						conflictResult.hasConflicts
					"
				>
					✅ 执行重命名
				</button>
			</div>
		</div>
	</div>
</template>
