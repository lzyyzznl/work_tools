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

	// 排序
	files.sort((a, b) => {
		let aValue: any, bValue: any;

		switch (sortField.value) {
			case "name":
				aValue = a.name.toLowerCase();
				bValue = b.name.toLowerCase();
				break;
			case "size":
				aValue = a.size;
				bValue = b.size;
				break;
			case "lastModified":
				aValue = a.lastModified;
				bValue = b.lastModified;
				break;
			case "matched":
				aValue = a.matched ? 1 : 0;
				bValue = b.matched ? 1 : 0;
				break;
			default:
				return 0;
		}

		if (aValue < bValue) return sortOrder.value === "asc" ? -1 : 1;
		if (aValue > bValue) return sortOrder.value === "asc" ? 1 : -1;
		return 0;
	});

	return files;
});

const sortedFiles = computed(() => {
	if (!isVirtualScrollEnabled.value) {
		return filteredFiles.value;
	}

	// 虚拟滚动
	const startIndex = Math.floor(virtualScrollTop.value / itemHeight);
	const endIndex = Math.min(
		startIndex + visibleItemCount.value,
		filteredFiles.value.length
	);

	return filteredFiles.value.slice(startIndex, endIndex);
});

const totalHeight = computed(() => filteredFiles.value.length * itemHeight);
const offsetY = computed(
	() => Math.floor(virtualScrollTop.value / itemHeight) * itemHeight
);

// 方法
function handleSort(field: string) {
	if (sortField.value === field) {
		sortOrder.value = sortOrder.value === "asc" ? "desc" : "asc";
	} else {
		sortField.value = field;
		sortOrder.value = "asc";
	}
}

function handleFileSelect(file: FileItem) {
	if (!props.showSelection) return;
	fileStore.toggleFileSelection(file.id);
}

function handleSelectAll() {
	if (!props.showSelection) return;

	const allSelected = filteredFiles.value.every((file) =>
		fileStore.selectedFiles.has(file.id)
	);

	if (allSelected) {
		filteredFiles.value.forEach((file) => fileStore.unselectFile(file.id));
	} else {
		filteredFiles.value.forEach((file) => fileStore.selectFile(file.id));
	}
}

function formatDate(timestamp: number): string {
	return new Date(timestamp).toLocaleString("zh-CN");
}

function getMatchStatusText(file: FileItem): string {
	if (!file.matched) return "未匹配";
	return file.matchInfo?.code || "已匹配";
}

function getMatchStatusClass(file: FileItem): string {
	return file.matched ? "text-green-600 font-medium" : "text-gray-500";
}

// 虚拟滚动处理
function handleScroll(event: Event) {
	if (!isVirtualScrollEnabled.value) return;

	const target = event.target as HTMLElement;
	virtualScrollTop.value = target.scrollTop;
}

// 监听文件数量变化，决定是否启用虚拟滚动
watch(
	() => filteredFiles.value.length,
	(newLength) => {
		isVirtualScrollEnabled.value = newLength > 100;

		if (isVirtualScrollEnabled.value) {
			nextTick(() => {
				visibleItemCount.value =
					Math.ceil(virtualScrollHeight.value / itemHeight) + 2;
			});
		}
	},
	{ immediate: true }
);

// 计算选中状态
const isAllSelected = computed(() => {
	if (filteredFiles.value.length === 0) return false;
	return filteredFiles.value.every((file) =>
		fileStore.selectedFiles.has(file.id)
	);
});

const isIndeterminate = computed(() => {
	const selectedCount = filteredFiles.value.filter((file) =>
		fileStore.selectedFiles.has(file.id)
	).length;
	return selectedCount > 0 && selectedCount < filteredFiles.value.length;
});

// 计算列数
function getColumnCount() {
	let count = 3; // 基础列：文件名、大小、修改时间
	if (props.showSelection) count++;
	if (props.showMatchInfo) count++;
	if (props.showPreview) count++;
	return count;
}
</script>

<template>
	<div class="file-table-container flex flex-col h-full">
		<!-- 搜索栏 -->
		<div class="search-bar p-4 border-b border-gray-200">
			<div class="relative">
				<input
					v-model="searchQuery"
					type="text"
					placeholder="搜索文件名、路径或匹配信息..."
					class="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
				/>
				<div
					class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
				>
					<span class="text-gray-400">🔍</span>
				</div>
				<div
					v-if="searchQuery"
					class="absolute inset-y-0 right-0 pr-3 flex items-center"
				>
					<button
						@click="searchQuery = ''"
						class="text-gray-400 hover:text-gray-600 focus:outline-none"
					>
						<span>✕</span>
					</button>
				</div>
			</div>
		</div>

		<!-- 文件表格 -->
		<div
			v-if="filteredFiles.length > 0"
			class="table-container flex-1 overflow-auto"
			:style="{
				height: isVirtualScrollEnabled ? `${virtualScrollHeight}px` : 'auto',
			}"
			@scroll="handleScroll"
		>
			<table class="w-full">
				<thead class="bg-gray-50 sticky top-0 z-10">
					<tr>
						<th v-if="props.showSelection" class="w-12 px-4 py-3 text-left">
							<input
								type="checkbox"
								:checked="isAllSelected"
								:indeterminate="isIndeterminate"
								@change="handleSelectAll"
								class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							/>
						</th>
						<th
							class="px-4 py-3 text-left font-medium text-gray-900 cursor-pointer hover:bg-gray-100"
							@click="handleSort('name')"
						>
							文件名
							<span v-if="sortField === 'name'" class="ml-1 text-xs opacity-60">
								{{ sortOrder === "asc" ? "↑" : "↓" }}
							</span>
						</th>
						<th
							class="w-20 px-4 py-3 text-right font-medium text-gray-900 cursor-pointer hover:bg-gray-100"
							@click="handleSort('size')"
						>
							大小
							<span v-if="sortField === 'size'" class="ml-1 text-xs opacity-60">
								{{ sortOrder === "asc" ? "↑" : "↓" }}
							</span>
						</th>
						<th
							class="w-35 px-4 py-3 text-left font-medium text-gray-900 cursor-pointer hover:bg-gray-100"
							@click="handleSort('lastModified')"
						>
							修改时间
							<span
								v-if="sortField === 'lastModified'"
								class="ml-1 text-xs opacity-60"
							>
								{{ sortOrder === "asc" ? "↑" : "↓" }}
							</span>
						</th>
						<th
							v-if="props.showMatchInfo"
							class="w-30 px-4 py-3 text-left font-medium text-gray-900 cursor-pointer hover:bg-gray-100"
							@click="handleSort('matched')"
						>
							匹配状态
							<span
								v-if="sortField === 'matched'"
								class="ml-1 text-xs opacity-60"
							>
								{{ sortOrder === "asc" ? "↑" : "↓" }}
							</span>
						</th>
						<th
							v-if="props.showPreview"
							class="px-4 py-3 text-left font-medium text-gray-900"
						>
							预览名称
						</th>
					</tr>
				</thead>
				<tbody>
					<!-- 虚拟滚动占位符 -->
					<tr
						v-if="isVirtualScrollEnabled && offsetY > 0"
						class="virtual-spacer"
					>
						<td
							:colspan="getColumnCount()"
							:style="{ height: `${offsetY}px` }"
						></td>
					</tr>

					<!-- 文件行 -->
					<tr
						v-for="file in sortedFiles"
						:key="file.id"
						class="border-b border-gray-100 hover:bg-gray-50 cursor-pointer"
						:class="{ 'bg-blue-50': fileStore.selectedFiles.has(file.id) }"
						@click="handleFileSelect(file)"
					>
						<td v-if="props.showSelection" class="px-4 py-3">
							<input
								type="checkbox"
								:checked="fileStore.selectedFiles.has(file.id)"
								@click.stop
								@change="fileStore.toggleFileSelection(file.id)"
								class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
							/>
						</td>
						<td class="px-4 py-3">
							<div class="flex items-center">
								<span class="mr-2">📄</span>
								<span
									class="truncate font-medium text-gray-900"
									:title="file.name"
								>
									{{ file.name }}
								</span>
							</div>
						</td>
						<td class="px-4 py-3 text-right text-gray-500">
							{{ formatFileSize(file.size) }}
						</td>
						<td class="px-4 py-3 text-gray-500">
							{{ formatDate(file.lastModified) }}
						</td>
						<td
							v-if="props.showMatchInfo"
							class="px-4 py-3"
							:class="getMatchStatusClass(file)"
						>
							{{ getMatchStatusText(file) }}
						</td>
						<td v-if="props.showPreview" class="px-4 py-3 text-gray-500 italic">
							<span v-if="file.previewName" :title="file.previewName">
								{{ file.previewName }}
							</span>
							<span v-else class="text-gray-400">无预览</span>
						</td>
					</tr>

					<!-- 虚拟滚动底部占位符 -->
					<tr v-if="isVirtualScrollEnabled" class="virtual-spacer">
						<td
							:colspan="getColumnCount()"
							:style="{
								height: `${
									totalHeight - offsetY - sortedFiles.length * itemHeight
								}px`,
							}"
						></td>
					</tr>
				</tbody>
			</table>
		</div>

		<!-- 空状态 -->
		<div
			v-else
			class="empty-state flex-1 flex flex-col items-center justify-center p-12 text-center"
		>
			<div class="text-6xl mb-6 opacity-50">📁</div>
			<div class="text-lg font-medium text-gray-600 mb-2">
				{{ searchQuery ? "未找到匹配的文件" : "暂无文件" }}
			</div>
			<div class="text-sm text-gray-400">
				{{ searchQuery ? "尝试调整搜索条件" : "请选择文件或拖拽文件到此处" }}
			</div>
		</div>
	</div>
</template>

<!-- 移除额外的 script 标签，将方法合并到 setup script 中 -->
