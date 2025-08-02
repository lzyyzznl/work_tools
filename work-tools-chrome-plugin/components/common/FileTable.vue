<script setup lang="ts">
import { computed, ref, watch, nextTick } from "vue";
import { useFileStore } from "../../stores/fileStore";
import { useFileSystem } from "../../composables/useFileSystem";
import type { FileItem } from "../../types/file";

// Props
interface Props {
	showMatchInfo?: boolean;
	showPreview?: boolean;
	showSelection?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
	showMatchInfo: false,
	showPreview: false,
	showSelection: true,
});

// 状态管理
const fileStore = useFileStore();
const { formatFileSize } = useFileSystem();

// 本地状态
const sortField = ref<string>("name");
const sortOrder = ref<"asc" | "desc">("asc");
const searchQuery = ref("");
const isVirtualScrollEnabled = ref(false);
const virtualScrollTop = ref(0);
const virtualScrollHeight = ref(400);
const itemHeight = 40; // 每行的高度
const visibleItemCount = ref(10); // 可见项目数量

// 计算属性
const filteredFiles = computed(() => {
	let files = [...fileStore.files];

	// 搜索过滤
	if (searchQuery.value.trim()) {
		const query = searchQuery.value.toLowerCase();
		files = files.filter(
			(file) =>
				file.name.toLowerCase().includes(query) ||
				file.path.toLowerCase().includes(query) ||
				(file.matchInfo?.code &&
					file.matchInfo.code.toLowerCase().includes(query)) ||
				(file.matchInfo?.matchedRule &&
					file.matchInfo.matchedRule.toLowerCase().includes(query))
		);
	}

	return files;
});

const sortedFiles = computed(() => {
	const files = [...filteredFiles.value];

	files.sort((a, b) => {
		let aValue: any = a[sortField.value as keyof FileItem];
		let bValue: any = b[sortField.value as keyof FileItem];

		// 特殊处理不同类型的字段
		if (sortField.value === "size" || sortField.value === "lastModified") {
			aValue = Number(aValue);
			bValue = Number(bValue);
		} else {
			aValue = String(aValue).toLowerCase();
			bValue = String(bValue).toLowerCase();
		}

		if (aValue < bValue) {
			return sortOrder.value === "asc" ? -1 : 1;
		}
		if (aValue > bValue) {
			return sortOrder.value === "asc" ? 1 : -1;
		}
		return 0;
	});

	return files;
});

// 虚拟滚动相关计算属性
const displayedFiles = computed(() => {
	if (!isVirtualScrollEnabled.value || sortedFiles.value.length < 100) {
		return sortedFiles.value;
	}

	const startIndex = Math.floor(virtualScrollTop.value / itemHeight);
	const endIndex = Math.min(
		startIndex + visibleItemCount.value,
		sortedFiles.value.length
	);

	return sortedFiles.value.slice(startIndex, endIndex);
});

// 方法
function handleSort(field: string) {
	if (sortField.value === field) {
		sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
	} else {
		sortField.value = field;
		sortOrder.value = "asc";
	}
}

function handleSelectAll() {
	if (fileStore.selectedFiles.size === fileStore.files.length) {
		fileStore.unselectAllFiles();
	} else {
		fileStore.selectAllFiles();
	}
}

function handleRowClick(file: FileItem) {
	if (props.showSelection) {
		fileStore.toggleFileSelection(file.id);
	}
}

function formatDate(timestamp: number): string {
	return new Date(timestamp).toLocaleString("zh-CN");
}

function getMatchStatusText(file: FileItem): string {
	if (!file.matched) return "未匹配";
	if (file.matchInfo) {
		return `${file.matchInfo.code} (${file.matchInfo.matchedRule})`;
	}
	return "已匹配";
}

function getSortIcon(field: string): string {
	if (sortField.value !== field) return "↕️";
	return sortOrder.value === "asc" ? "↑" : "↓";
}

// 虚拟滚动处理
function handleScroll(event: Event) {
	if (!isVirtualScrollEnabled.value) return;

	const target = event.target as HTMLElement;
	virtualScrollTop.value = target.scrollTop;
}

// 性能优化：监听文件数量变化，自动启用虚拟滚动
watch(
	() => fileStore.files.length,
	(newLength) => {
		isVirtualScrollEnabled.value = newLength > 100;
		if (isVirtualScrollEnabled.value) {
			nextTick(() => {
				// 计算可见项目数量
				const containerHeight = virtualScrollHeight.value;
				visibleItemCount.value = Math.ceil(containerHeight / itemHeight) + 5; // 额外渲染5项
			});
		}
	},
	{ immediate: true }
);

// 搜索防抖处理
let searchTimeout: number | null = null;
function handleSearchInput(event: Event) {
	const target = event.target as HTMLInputElement;

	if (searchTimeout) {
		clearTimeout(searchTimeout);
	}

	searchTimeout = window.setTimeout(() => {
		searchQuery.value = target.value;
	}, 300);
}
</script>

<template>
	<div class="file-table-container">
		<!-- 搜索栏 -->
		<div v-if="fileStore.files.length > 0" class="search-bar">
			<input
				type="text"
				class="search-input"
				placeholder="搜索文件名、路径或匹配信息..."
				@input="handleSearchInput"
			/>
			<div class="search-stats">
				显示 {{ displayedFiles.length }} / {{ fileStore.files.length }} 个文件
			</div>
		</div>

		<div class="table-wrapper" @scroll="handleScroll">
			<table class="file-table">
				<thead>
					<tr>
						<th v-if="showSelection" class="checkbox-col">
							<input
								type="checkbox"
								:checked="
									fileStore.selectedFiles.size === fileStore.files.length &&
									fileStore.files.length > 0
								"
								:indeterminate="
									fileStore.selectedFiles.size > 0 &&
									fileStore.selectedFiles.size < fileStore.files.length
								"
								@change="handleSelectAll"
							/>
						</th>
						<th class="sortable" @click="handleSort('name')">
							文件名 <span class="sort-icon">{{ getSortIcon("name") }}</span>
						</th>
						<th class="sortable" @click="handleSort('size')">
							大小 <span class="sort-icon">{{ getSortIcon("size") }}</span>
						</th>
						<th class="sortable" @click="handleSort('lastModified')">
							修改时间
							<span class="sort-icon">{{ getSortIcon("lastModified") }}</span>
						</th>
						<th v-if="showMatchInfo">匹配状态</th>
						<th v-if="showPreview">预览名称</th>
					</tr>
				</thead>
				<tbody>
					<!-- 虚拟滚动占位符 -->
					<tr
						v-if="
							isVirtualScrollEnabled &&
							sortedFiles.length > displayedFiles.length
						"
						:style="{
							height: `${
								Math.floor(virtualScrollTop.value / itemHeight) * itemHeight
							}px`,
						}"
						class="virtual-spacer"
					></tr>

					<tr
						v-for="file in displayedFiles"
						:key="file.id"
						:class="{
							selected: fileStore.selectedFiles.has(file.id),
							matched: file.matched,
							clickable: showSelection,
						}"
						@click="handleRowClick(file)"
					>
						<td v-if="showSelection" class="checkbox-col">
							<input
								type="checkbox"
								:checked="fileStore.selectedFiles.has(file.id)"
								@click.stop
								@change="fileStore.toggleFileSelection(file.id)"
							/>
						</td>
						<td class="file-name">
							<span class="file-icon">📄</span>
							<span class="name-text" :title="file.name">{{ file.name }}</span>
						</td>
						<td class="file-size">{{ formatFileSize(file.size) }}</td>
						<td class="file-date">{{ formatDate(file.lastModified) }}</td>
						<td
							v-if="showMatchInfo"
							class="match-status"
							:class="{ matched: file.matched }"
						>
							{{ getMatchStatusText(file) }}
						</td>
						<td v-if="showPreview" class="preview-name">
							<span v-if="file.previewName" :title="file.previewName">
								{{ file.previewName }}
							</span>
							<span v-else class="no-preview">-</span>
						</td>
					</tr>
				</tbody>
			</table>
		</div>

		<div v-if="fileStore.files.length === 0" class="empty-state">
			<div class="empty-icon">📁</div>
			<div class="empty-text">暂无文件</div>
			<div class="empty-hint">拖拽文件到此处或点击选择文件</div>
		</div>
	</div>
</template>

<style scoped lang="scss">
.file-table-container {
	flex: 1;
	display: flex;
	flex-direction: column;
	overflow: hidden;
}

.search-bar {
	display: flex;
	align-items: center;
	gap: var(--spacing-md);
	padding: var(--spacing-md);
	background: var(--color-background-secondary);
	border-bottom: 1px solid var(--color-border-primary);

	.search-input {
		flex: 1;
		padding: var(--spacing-sm) var(--spacing-md);
		border: 1px solid var(--color-border-primary);
		border-radius: var(--radius-md);
		font-size: var(--font-size-sm);
		background: var(--color-background-primary);
		color: var(--color-text-primary);

		&:focus {
			outline: none;
			border-color: var(--color-primary);
			box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2);
		}

		&::placeholder {
			color: var(--color-text-tertiary);
		}
	}

	.search-stats {
		font-size: var(--font-size-xs);
		color: var(--color-text-secondary);
		white-space: nowrap;
	}
}

.table-wrapper {
	flex: 1;
	overflow: auto;
}

.file-table {
	width: 100%;
	border-collapse: collapse;
	font-size: var(--font-size-sm);

	th,
	td {
		padding: var(--spacing-sm) var(--spacing-md);
		text-align: left;
		border-bottom: 1px solid var(--color-border-secondary);
	}

	th {
		background: var(--color-background-secondary);
		font-weight: var(--font-weight-semibold);
		color: var(--color-text-primary);
		position: sticky;
		top: 0;
		z-index: 1;

		&.sortable {
			cursor: pointer;
			user-select: none;

			&:hover {
				background: var(--color-background-tertiary);
			}
		}
	}

	tr {
		&:hover {
			background: var(--color-background-secondary);
		}

		&.selected {
			background: rgba(0, 122, 255, 0.1);
		}

		&.clickable {
			cursor: pointer;
		}
	}

	.checkbox-col {
		width: 40px;
		text-align: center;
	}

	.file-name {
		display: flex;
		align-items: center;
		gap: var(--spacing-xs);
		min-width: 0;

		.file-icon {
			flex-shrink: 0;
		}

		.name-text {
			flex: 1;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
	}

	.file-size {
		width: 80px;
		text-align: right;
		color: var(--color-text-secondary);
	}

	.file-date {
		width: 140px;
		color: var(--color-text-secondary);
	}

	.match-status {
		width: 120px;
		color: var(--color-text-secondary);

		&.matched {
			color: var(--color-success);
			font-weight: var(--font-weight-medium);
		}
	}

	.preview-name {
		color: var(--color-text-secondary);
		font-style: italic;

		.no-preview {
			color: var(--color-text-tertiary);
		}
	}

	.sort-icon {
		font-size: var(--font-size-xs);
		margin-left: var(--spacing-xs);
		opacity: 0.6;
	}

	.virtual-spacer {
		pointer-events: none;

		td {
			padding: 0;
			border: none;
		}
	}
}

.empty-state {
	flex: 1;
	display: flex;
	flex-direction: column;
	align-items: center;
	justify-content: center;
	padding: var(--spacing-3xl);
	text-align: center;

	.empty-icon {
		font-size: 48px;
		margin-bottom: var(--spacing-lg);
		opacity: 0.5;
	}

	.empty-text {
		font-size: var(--font-size-lg);
		font-weight: var(--font-weight-medium);
		color: var(--color-text-secondary);
		margin-bottom: var(--spacing-sm);
	}

	.empty-hint {
		font-size: var(--font-size-sm);
		color: var(--color-text-tertiary);
	}
}
</style>
