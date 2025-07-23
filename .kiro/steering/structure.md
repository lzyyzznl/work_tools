# 项目结构

## 根目录组织

```
work_tools_plugin/
├── components/          # 组件目录
├── composables/         # 可复用组合函数
├── stores/              # 状态管理存储
├── types/               # 类型定义文件
├── utils/               # 工具函数
├── entrypoints/         # 扩展入口点
├── constants/           # 应用常量
├── assets/              # 静态资源
└── public/              # 公共资源
```

## 组件架构

### `/components/`

- **common/**：跨功能共享的界面组件
- **file-matcher/**：文件匹配功能专用组件
- **file-renamer/**：文件重命名功能专用组件
- **HelloWorld.vue**：示例模板组件

### 组件命名规范

- 使用大驼峰命名法命名组件文件
- 使用反映功能的描述性名称
- 在功能文件夹中分组相关组件

## 组合式函数模式

### `/composables/`

提取为可复用函数的核心业务逻辑：

- **useDataManager.ts**：数据导入导出操作
- **useErrorHandler.ts**：错误处理和用户反馈
- **useExcelUtils.ts**：表格文件处理工具
- **useFileSystem.ts**：文件系统操作
- **useKeyboardShortcuts.ts**：键盘快捷键管理
- **useRenameEngine.ts**：核心重命名逻辑引擎
- **useSearchHistory.ts**：搜索历史管理
- **useSettings.ts**：应用设置管理

### 组合式函数命名规范

- 以 `use` 开头加描述性名称
- 导出为命名函数
- 返回包含方法和响应式状态的对象

## 状态管理

### `/stores/`

集中式状态的存储：

- **fileStore.ts**：文件列表和选择管理
- **renameStore.ts**：重命名操作状态
- **ruleStore.ts**：匹配规则管理
- **settingsStore.ts**：应用设置

### 存储命名规范

- 以 `Store` 结尾（如 `fileStore`）
- 使用带字符串标识符的 `defineStore`
- 导出为 `useXxxStore` 函数

## 类型定义

### `/types/`

类型脚本接口和类型：

- **common.ts**：应用间共享类型
- **file.ts**：文件相关类型定义
- **rename.ts**：重命名操作类型
- **rule.ts**：规则系统类型

### 类型命名规范

- 接口使用大驼峰命名法
- 使用反映数据结构的描述性名称
- 在同一文件中分组相关类型

## 扩展入口点

### `/entrypoints/`

浏览器扩展特定入口点：

- **background.ts**：后台脚本
- **content.ts**：内容脚本
- **popup/**：扩展弹窗界面
- **file-matcher/**：文件匹配独立页面
- **file-renamer/**：文件重命名独立页面
- **common/**：共享入口点工具

### 入口点结构

- 每个主要功能都有自己的入口点
- 独立页面使用网页文件
- 脚本入口点使用类型脚本文件

## 工具函数

### `/utils/`

辅助函数和工具：

- **exportUtils.ts**：数据导出功能
- **importUtils.ts**：数据导入功能

## 文件命名规范

- **组件**：大驼峰命名法（如 `FileList.vue`）
- **组合式函数**：小驼峰命名法加 `use` 前缀（如 `useFileManager.ts`）
- **存储**：小驼峰命名法加 `Store` 后缀（如 `fileStore.ts`）
- **类型**：小驼峰命名法（如 `fileTypes.ts`）
- **工具**：小驼峰命名法（如 `stringUtils.ts`）

## 导入导出模式

- 工具和组合式函数使用命名导出
- 组件使用默认导出
- 一致的导入顺序：外部库、内部模块、类型
