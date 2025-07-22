<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useFileStore } from "../../stores/fileStore";
import { useRenameStore } from "../../stores/renameStore";
import { useFileSystem } from "../../composables/useFileSystem";
import { useRenameEngine } from "../../composables/useRenameEngine";
import FileRenamerTab from "../../components/file-renamer/FileRenamerTab.vue";
import NotificationContainer from "../../components/common/NotificationContainer.vue";

const fileStore = useFileStore();
const renameStore = useRenameStore();
const { selectFiles, selectDirectory, handleDrop } = useFileSystem();
const { generatePreview, executeRename, undoLastOperation } = useRenameEngine();

// 简化的App组件，主要功能都在FileRenamerTab中实现

// 组件挂载时初始化
onMounted(() => {
	// 初始化逻辑
});
</script>

<template>
	<div class="app-container">
		<!-- 页面头部 -->
		<header class="app-header">
			<div class="header-content">
				<h1 class="app-title">
					<span class="app-icon">✏️</span>
					文件重命名工具
				</h1>
				<p class="app-description">
					批量重命名文件，支持多种重命名模式和实时预览
				</p>
			</div>
		</header>

		<!-- 主要内容 -->
		<main class="app-main">
			<FileRenamerTab />
		</main>

		<!-- 状态栏 -->
		<footer class="app-footer">
			<div class="footer-info">
				<div class="info-item">
					<span class="info-label">文件:</span>
					<span class="info-value">{{ fileStore.fileStats.total }}</span>
				</div>
				<div class="info-item">
					<span class="info-label">选中:</span>
					<span class="info-value">{{ fileStore.fileStats.selected }}</span>
				</div>
			</div>
			<div class="footer-actions">
				<div class="action-item highlight">
					模式: {{ renameStore.currentMode }}
				</div>
				<div class="action-item">v1.0.0</div>
			</div>
		</footer>

		<!-- 全局通知容器 -->
		<NotificationContainer />
	</div>
</template>

<style scoped lang="scss">
.app-container {
	display: flex;
	flex-direction: column;
	height: 100vh;
	background: var(--color-background-primary);
}

.app-header {
	padding: var(--spacing-lg) var(--spacing-2xl);
	background: var(--color-background-secondary);
	border-bottom: 1px solid var(--color-border-primary);

	.header-content {
		max-width: 1200px;
		margin: 0 auto;

		.app-title {
			display: flex;
			align-items: center;
			gap: var(--spacing-sm);
			margin: 0 0 var(--spacing-xs) 0;
			font-size: var(--font-size-2xl);
			font-weight: var(--font-weight-bold);
			color: var(--color-text-primary);

			.app-icon {
				font-size: var(--font-size-3xl);
			}
		}

		.app-description {
			margin: 0;
			font-size: var(--font-size-base);
			color: var(--color-text-secondary);
			line-height: 1.5;
		}
	}
}

.app-main {
	flex: 1;
	overflow: hidden;
	max-width: 1200px;
	margin: 0 auto;
	width: 100%;
	padding: var(--spacing-lg);
}

.app-footer {
	display: flex;
	align-items: center;
	justify-content: space-between;
	padding: var(--spacing-sm) var(--spacing-2xl);
	background: var(--color-background-secondary);
	border-top: 1px solid var(--color-border-primary);
	font-size: var(--font-size-sm);

	.footer-info {
		display: flex;
		gap: var(--spacing-lg);

		.info-item {
			display: flex;
			align-items: center;
			gap: var(--spacing-xs);

			.info-label {
				color: var(--color-text-secondary);
			}

			.info-value {
				font-weight: var(--font-weight-semibold);
				color: var(--color-text-primary);
			}
		}
	}

	.footer-actions {
		display: flex;
		gap: var(--spacing-md);

		.action-item {
			color: var(--color-text-secondary);

			&.highlight {
				color: var(--color-primary);
				font-weight: var(--font-weight-semibold);
			}
		}
	}
}
</style>
