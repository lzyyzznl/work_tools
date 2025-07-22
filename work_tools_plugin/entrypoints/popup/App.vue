<script setup lang="ts">
import { onMounted } from "vue";
import { useRuleStore } from "../../stores/ruleStore";

// 状态管理
const ruleStore = useRuleStore();

// 功能按钮配置
const features = [
	{
		id: "file-matcher",
		title: "文件匹配工具",
		description: "根据预定义规则匹配文件名",
		icon: "🔍",
		url: "/file-matcher.html",
	},
	{
		id: "file-renamer",
		title: "文件重命名工具",
		description: "批量重命名文件，支持多种模式",
		icon: "✏️",
		url: "/file-renamer.html",
	},
];

// 打开功能页面
function openFeature(feature: (typeof features)[0]) {
	chrome.tabs.create({
		url: chrome.runtime.getURL(feature.url),
	});
}

// 组件挂载时初始化
onMounted(async () => {
	await ruleStore.loadRules();
});
</script>

<template>
	<div class="popup">
		<!-- 标题栏 -->
		<header class="popup-header">
			<h1 class="popup-title">
				<span class="popup-icon">🛠️</span>
				批量文件处理工具
			</h1>
			<p class="popup-subtitle">选择要使用的功能</p>
		</header>

		<!-- 功能按钮 -->
		<main class="popup-content">
			<div class="feature-grid">
				<button
					v-for="feature in features"
					:key="feature.id"
					class="feature-card"
					@click="openFeature(feature)"
				>
					<div class="feature-icon">{{ feature.icon }}</div>
					<div class="feature-info">
						<h3 class="feature-title">{{ feature.title }}</h3>
						<p class="feature-description">{{ feature.description }}</p>
					</div>
					<div class="feature-arrow">→</div>
				</button>
			</div>
		</main>

		<!-- 底部信息 -->
		<footer class="popup-footer">
			<div class="popup-info">v1.0.0 by 荔枝鱼</div>
		</footer>
	</div>
</template>

<style scoped lang="scss">
.popup {
	width: 320px;
	max-height: 400px;
	background: var(--color-background-primary);
	display: flex;
	flex-direction: column;
}

.popup-header {
	padding: var(--spacing-lg);
	background: linear-gradient(
		to bottom,
		rgba(248, 249, 250, 1),
		rgba(255, 255, 255, 1)
	);
	border-bottom: 1px solid var(--color-border-primary);
	text-align: center;

	.popup-title {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: var(--spacing-sm);
		font-size: var(--font-size-lg);
		font-weight: var(--font-weight-bold);
		color: var(--color-text-primary);
		margin: 0 0 var(--spacing-xs) 0;

		.popup-icon {
			font-size: var(--font-size-xl);
		}
	}

	.popup-subtitle {
		font-size: var(--font-size-sm);
		color: var(--color-text-secondary);
		margin: 0;
	}
}

.popup-content {
	padding: var(--spacing-lg);
}

.feature-grid {
	display: flex;
	flex-direction: column;
	gap: var(--spacing-md);
}

.feature-card {
	display: flex;
	align-items: center;
	gap: var(--spacing-md);
	padding: var(--spacing-lg);
	border: 1px solid var(--color-border-primary);
	border-radius: var(--radius-lg);
	background: linear-gradient(
		to bottom,
		rgba(255, 255, 255, 0.9),
		rgba(245, 245, 247, 0.9)
	);
	cursor: pointer;
	transition: all var(--transition-fast);
	text-align: left;

	&:hover {
		background: linear-gradient(
			to bottom,
			rgba(255, 255, 255, 1),
			rgba(250, 250, 252, 1)
		);
		border-color: var(--color-primary);
		transform: translateY(-1px);
		box-shadow: var(--shadow-md);
	}

	&:active {
		transform: translateY(0);
		background: linear-gradient(
			to bottom,
			rgba(240, 240, 242, 1),
			rgba(235, 235, 237, 1)
		);
	}

	.feature-icon {
		font-size: 32px;
		flex-shrink: 0;
	}

	.feature-info {
		flex: 1;
		min-width: 0;

		.feature-title {
			font-size: var(--font-size-base);
			font-weight: var(--font-weight-semibold);
			color: var(--color-text-primary);
			margin: 0 0 var(--spacing-xs) 0;
		}

		.feature-description {
			font-size: var(--font-size-sm);
			color: var(--color-text-secondary);
			margin: 0;
			line-height: 1.4;
		}
	}

	.feature-arrow {
		font-size: var(--font-size-lg);
		color: var(--color-text-tertiary);
		flex-shrink: 0;
		transition: all var(--transition-fast);
	}

	&:hover .feature-arrow {
		color: var(--color-primary);
		transform: translateX(2px);
	}
}

.popup-footer {
	padding: var(--spacing-md) var(--spacing-lg);
	background: var(--color-background-secondary);
	border-top: 1px solid var(--color-border-primary);
	text-align: center;

	.popup-info {
		font-size: var(--font-size-xs);
		color: var(--color-text-tertiary);
		font-style: italic;
	}
}
</style>
