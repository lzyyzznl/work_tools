# FileTable 组件 API 设计文档

## 概述

FileTable 组件是一个基于 vxe-table 的文件列表展示组件，用于显示文件信息、支持搜索、排序、选择等功能。该组件保持与现有 FileTable.vue 组件的接口兼容性，同时利用 vxe-table 的增强功能。

## Props

### showMatchInfo

- **类型**: `boolean`
- **默认值**: `false`
- **描述**: 控制是否显示匹配信息列。当设置为 true 时，将显示文件的匹配状态信息。

### showPreview

- **类型**: `boolean`
- **默认值**: `false`
- **描述**: 控制是否显示预览名称列。当设置为 true 时，将显示文件的预览名称。

### showSelection

- **类型**: `boolean`
- **默认值**: `true`
- **描述**: 控制是否显示选择列。当设置为 true 时，将显示文件选择复选框，允许用户选择文件。

## Events

### file-selected

- **参数**: `(file: FileItem) => void`
- **描述**: 当用户点击文件行时触发。传递被点击的文件对象。

### selection-changed

- **参数**: `(selectedFiles: FileItem[]) => void`
- **描述**: 当文件选择状态改变时触发。传递当前所有选中的文件列表。

### sort-changed

- **参数**: `(field: string, order: 'asc' | 'desc') => void`
- **描述**: 当排序字段或顺序改变时触发。传递当前排序的字段名和排序顺序。

## Slots

### empty

- **作用域插槽参数**: 无
- **描述**: 当文件列表为空时显示的内容。可以用于自定义空状态的显示。

### file-name

- **作用域插槽参数**: `{ file: FileItem }`
- **描述**: 自定义文件名列的显示内容。可以通过该插槽自定义文件名的显示方式。

### file-size

- **作用域插槽参数**: `{ file: FileItem }`
- **描述**: 自定义文件大小列的显示内容。可以通过该插槽自定义文件大小的显示方式。

### last-modified

- **作用域插槽参数**: `{ file: FileItem }`
- **描述**: 自定义最后修改时间列的显示内容。可以通过该插槽自定义修改时间的显示方式。

### match-info

- **作用域插槽参数**: `{ file: FileItem }`
- **描述**: 自定义匹配信息列的显示内容。仅在 showMatchInfo 为 true 时有效。

### preview-name

- **作用域插槽参数**: `{ file: FileItem }`
- **描述**: 自定义预览名称列的显示内容。仅在 showPreview 为 true 时有效。

## 方法

### selectAll()

- **描述**: 选择所有文件。

### unselectAll()

- **描述**: 取消选择所有文件。

### getSelectedFiles()

- **返回值**: `FileItem[]`
- **描述**: 获取当前选中的所有文件。

### setSearchQuery(query: string)

- **参数**: `query: string`
- **描述**: 设置搜索查询字符串，过滤文件列表。

## 类型定义

### FileItem

```typescript
interface FileItem {
	id: string;
	name: string;
	path: string;
	size: number;
	lastModified: number;
	file: File;
	matched?: boolean;
	matchInfo?: MatchInfo;
	previewName?: string;
	selected: boolean;
	executionResult?: string;
}
```

### MatchInfo

```typescript
interface MatchInfo {
	index: number;
	code: string;
	thirtyD: string;
	matchedRule: string;
}
```

## 使用示例

```vue
<template>
	<FileTable
		:show-match-info="true"
		:show-preview="true"
		:show-selection="true"
		@file-selected="handleFileSelected"
		@selection-changed="handleSelectionChanged"
	/>
</template>

<script setup lang="ts">
import { ref } from "vue";
import FileTable from "./FileTable.vue";
import type { FileItem } from "../../types/file";

const handleFileSelected = (file: FileItem) => {
	console.log("选中的文件:", file);
};

const handleSelectionChanged = (selectedFiles: FileItem[]) => {
	console.log("选中的文件列表:", selectedFiles);
};
</script>
```

## vxe-table 增强功能

新的 FileTable 组件基于 vxe-table 实现，具有以下增强功能：

1. **虚拟滚动**: 自动启用虚拟滚动以提高大文件列表的性能
2. **高级排序**: 支持多字段排序和自定义排序函数
3. **筛选功能**: 内置列筛选功能
4. **分页支持**: 可选的分页功能
5. **更好的性能**: 优化的渲染性能和内存使用
6. **丰富的配置选项**: 更多的表格配置选项
7. **主题定制**: 支持主题定制和样式覆盖

## 向后兼容性

新的 FileTable 组件保持与现有组件的接口兼容性：

1. 所有现有的 props 都保持不变
2. 文件选择状态通过相同的机制管理
3. 排序和搜索功能保持相同的接口
4. 组件外观和交互行为保持一致

## 扩展性

新的 API 设计为未来扩展预留了空间：

1. 可以通过插槽自定义各列的显示
2. 提供了丰富的事件用于监听组件状态变化
3. 暴露了常用方法供外部调用
4. 支持通过 props 控制更多 vxe-table 特性
