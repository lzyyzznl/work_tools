# FileTable 组件文档

## 概述

FileTable 组件是一个基于 vxe-table 的文件列表展示组件，用于显示文件信息、支持搜索、排序、选择等功能。该组件提供了丰富的功能，包括文件展示、搜索、排序、选择等，并保持与现有 FileTable.vue 组件的接口兼容性，同时利用 vxe-table 的增强功能。

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

### 基本使用

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

### 在文件重命名组件中使用

```vue
<template>
	<!-- 文件表格 -->
	<FileTable :show-preview="true" :show-selection="true" />
</template>

<script setup lang="ts">
import FileTable from "../common/FileTable.vue";
</script>
```

### 在文件匹配组件中使用

```vue
<template>
	<!-- 文件表格 -->
	<FileTable
		:show-match-info="true"
		:show-selection="true"
		:show-preview="false"
	/>
</template>

<script setup lang="ts">
import FileTable from "../common/FileTable.vue";
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

## 与旧组件的差异和优势

### 功能增强

1. **性能提升**: 使用 vxe-table 替代原生实现，大幅提升大文件列表的渲染性能
2. **虚拟滚动**: 自动启用虚拟滚动，即使处理数万个文件也能保持流畅
3. **增强的交互**: 提供更丰富的用户交互功能，如列宽调整、表头固定等
4. **更好的可扩展性**: 基于成熟的 vxe-table 组件，便于后续功能扩展

### 兼容性保证

1. **接口兼容**: 保持与现有组件完全一致的接口，无需修改现有代码
2. **样式一致**: 保持与原组件相同的外观和交互行为
3. **无缝迁移**: 现有代码可以无缝迁移到新组件，无需额外适配

### 新增特性

1. **增强的搜索功能**: 支持在文件名、路径、匹配信息等多个字段中搜索
2. **更灵活的排序**: 支持多字段排序和自定义排序函数
3. **丰富的配置选项**: 提供更多表格配置选项，满足不同场景需求

## 常见问题解答和故障排除指南

### 1. 文件表格显示为空

**问题**: 文件表格没有显示任何文件。

**解决方案**:

- 检查是否正确添加了文件到 fileStore
- 确认 FileTable 组件是否正确引入和使用
- 检查是否有搜索条件过滤了所有文件

### 2. 选择功能不工作

**问题**: 无法选择文件或选择事件没有触发。

**解决方案**:

- 确认 `showSelection` 属性是否设置为 `true`
- 检查 `selection-changed` 事件监听器是否正确绑定
- 确认组件是否正确暴露了选择相关方法

### 3. 排序功能异常

**问题**: 点击列头无法正确排序。

**解决方案**:

- 检查 `sort-changed` 事件监听器是否正确实现
- 确认排序字段和顺序是否正确传递给后端或状态管理

### 4. 搜索功能不生效

**问题**: 输入搜索关键词后，文件列表没有过滤。

**解决方案**:

- 检查搜索框是否正确绑定到 `searchQuery` 状态
- 确认搜索过滤逻辑是否正确实现
- 检查搜索关键词是否正确传递给过滤函数

### 5. 匹配信息列不显示

**问题**: 设置 `showMatchInfo` 为 `true` 后，匹配信息列仍然不显示。

**解决方案**:

- 确认 `showMatchInfo` 属性是否正确传递给组件
- 检查文件对象是否包含 `matchInfo` 字段
- 确认文件是否已正确匹配并更新了匹配信息

### 6. 预览名称列不显示

**问题**: 设置 `showPreview` 为 `true` 后，预览名称列仍然不显示。

**解决方案**:

- 确认 `showPreview` 属性是否正确传递给组件
- 检查文件对象是否包含 `previewName` 字段
- 确认重命名预览是否已正确生成

### 7. 性能问题

**问题**: 在处理大量文件时，表格响应缓慢。

**解决方案**:

- 确认是否正确启用了虚拟滚动
- 检查是否有不必要的重复渲染
- 确认是否正确使用了 vxe-table 的性能优化选项

### 8. 样式问题

**问题**: 表格样式不符合预期。

**解决方案**:

- 确认是否正确引入了 vxe-table 的样式文件
- 检查 UnoCSS 样式是否正确应用
- 确认是否正确配置了 vxe-table 的主题

## 最佳实践

### 1. 性能优化

- 对于大量文件的场景，建议启用虚拟滚动以提升性能
- 避免在表格渲染函数中执行复杂计算，应预先计算好数据

### 2. 状态管理

- 使用 Vuex 或 Pinia 等状态管理工具统一管理文件列表状态
- 通过事件机制实现组件间通信，避免直接操作组件内部状态

### 3. 错误处理

- 为所有异步操作添加适当的错误处理机制
- 提供友好的错误提示信息，帮助用户理解问题原因

### 4. 用户体验

- 提供清晰的空状态提示，引导用户添加文件
- 在加载数据时显示加载状态，提升用户体验
- 合理使用搜索和筛选功能，帮助用户快速找到所需文件

## 扩展性

新的 API 设计为未来扩展预留了空间：

1. 可以通过插槽自定义各列的显示
2. 提供了丰富的事件用于监听组件状态变化
3. 暴露了常用方法供外部调用
4. 支持通过 props 控制更多 vxe-table 特性
