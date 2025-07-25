# 工作工具 - 开发文档

## 🏗️ 项目架构

### 技术栈
- **前端**: Vue 3 + TypeScript + UnoCSS
- **桌面**: Electron + Electron Forge
- **状态管理**: Pinia
- **构建工具**: Vite
- **测试**: Vitest + Vue Test Utils

### 目录结构
```
work-tools-desktop/
├── src/
│   ├── main/                    # Electron 主进程
│   │   ├── main.ts             # 主进程入口
│   │   ├── preload.ts          # 预加载脚本
│   │   └── handlers/           # IPC 处理器
│   │       └── fileSystemHandler.ts
│   └── renderer/               # 渲染进程 (Vue 应用)
│       ├── App.vue             # 根组件
│       ├── renderer.ts         # 渲染进程入口
│       ├── components/         # Vue 组件
│       │   ├── common/         # 通用组件
│       │   ├── file-matcher/   # 文件匹配器组件
│       │   └── file-renamer/   # 文件重命名器组件
│       ├── composables/        # 组合式函数
│       ├── stores/             # Pinia 状态管理
│       ├── types/              # TypeScript 类型
│       └── constants/          # 常量定义
├── assets/                     # 静态资源
├── tests/                      # 测试文件
├── docs/                       # 文档
└── forge.config.ts            # Electron Forge 配置
```

## 🔧 开发环境设置

### 环境要求
- Node.js >= 18.0.0
- npm >= 9.0.0
- Git

### 初始化项目
```bash
# 克隆项目
git clone <repository-url>
cd work-tools-desktop

# 安装依赖
npm install

# 启动开发服务器
npm start
```

### 开发命令
```bash
# 开发模式
npm start

# 运行测试
npm test
npm run test:run
npm run test:ui

# 代码检查
npm run lint

# 构建应用
npm run package
npm run make
```

## 🏛️ 架构设计

### 主进程 (Main Process)
负责应用生命周期管理和系统级操作：

```typescript
// src/main/main.ts
import { app, BrowserWindow } from 'electron'
import { setupFileSystemHandlers } from './handlers/fileSystemHandler'

// 创建主窗口
function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    }
  })
}

// 设置 IPC 处理器
setupFileSystemHandlers()
```

### 预加载脚本 (Preload)
提供安全的 API 桥接：

```typescript
// src/main/preload.ts
import { contextBridge, ipcRenderer } from 'electron'

contextBridge.exposeInMainWorld('electronAPI', {
  fileSystem: {
    selectFiles: (options) => ipcRenderer.invoke('file-system:select-files', options),
    selectDirectory: () => ipcRenderer.invoke('file-system:select-directory')
  }
})
```

### 渲染进程 (Renderer)
Vue 3 应用，包含所有 UI 逻辑：

```typescript
// src/renderer/App.vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useFileStore } from './stores/fileStore'
import FileMatcherTab from './components/file-matcher/FileMatcherTab.vue'

const activeTab = ref<'matcher' | 'renamer'>('matcher')
const fileStore = useFileStore()
</script>
```

## 📦 状态管理

### Pinia Stores
使用 Pinia 进行状态管理：

```typescript
// src/renderer/stores/fileStore.ts
export const useFileStore = defineStore('file', () => {
  const files = ref<FileItem[]>([])
  const selectedFiles = ref<Set<string>>(new Set())

  function addFiles(newFiles: File[]) {
    // 添加文件逻辑
  }

  return { files, selectedFiles, addFiles }
})
```

### 主要 Stores
- `fileStore`: 文件管理
- `ruleStore`: 规则管理
- `renameStore`: 重命名操作
- `settingsStore`: 应用设置

## 🧩 组件设计

### 组件层次结构
```
App.vue
├── FileMatcherTab.vue
│   ├── FileTable.vue
│   └── RuleManager.vue
│       └── RuleEditor.vue
├── FileRenamerTab.vue
│   ├── PreviewPanel.vue
│   └── RenameOperationTabs.vue
└── NotificationContainer.vue
```

### 组件通信
- **Props**: 父子组件数据传递
- **Emits**: 子组件向父组件发送事件
- **Pinia**: 跨组件状态共享
- **Provide/Inject**: 深层组件通信

## 🎨 样式系统

### UnoCSS 配置
```typescript
// uno.config.ts
export default defineConfig({
  presets: [
    presetUno(),
    presetAttributify(),
    presetIcons()
  ],
  theme: {
    colors: {
      primary: '#3B82F6',
      secondary: '#6B7280'
    }
  }
})
```

### 样式规范
- 使用原子化 CSS 类
- 遵循设计系统规范
- 保持响应式设计
- 支持深色模式

## 🧪 测试策略

### 测试类型
1. **单元测试**: 组件、函数、工具类
2. **集成测试**: 组件间交互
3. **端到端测试**: 完整用户流程

### 测试工具
- **Vitest**: 测试运行器
- **Vue Test Utils**: Vue 组件测试
- **Testing Library**: 用户行为测试

### 测试示例
```typescript
// tests/components/FileTable.test.ts
import { mount } from '@vue/test-utils'
import FileTable from '@/components/common/FileTable.vue'

describe('FileTable', () => {
  it('should render file list', () => {
    const wrapper = mount(FileTable, {
      props: { files: mockFiles }
    })
    expect(wrapper.findAll('.file-row')).toHaveLength(2)
  })
})
```

## 🔄 构建和部署

### 开发构建
```bash
# 启动开发服务器
npm start

# 热重载和调试工具自动启用
```

### 生产构建
```bash
# 打包应用
npm run package

# 创建安装程序
npm run make
```

### 构建配置
```typescript
// forge.config.ts
export default {
  packagerConfig: {
    name: '工作工具',
    icon: './assets/icon',
    asar: true
  },
  makers: [
    new MakerSquirrel({}),
    new MakerZIP({}, ['darwin']),
    new MakerDeb({}),
    new MakerRpm({})
  ]
}
```

## 🐛 调试指南

### 开发工具
- **Vue DevTools**: Vue 组件调试
- **Electron DevTools**: 主进程调试
- **Vite DevTools**: 构建过程调试

### 常见问题
1. **IPC 通信失败**: 检查预加载脚本配置
2. **样式不生效**: 确认 UnoCSS 配置
3. **热重载失败**: 重启开发服务器

### 日志记录
```typescript
// 使用统一的日志系统
import { logger } from '@/utils/logger'

logger.info('操作成功', { fileCount: 10 })
logger.error('操作失败', error)
```

## 📋 代码规范

### TypeScript 规范
- 严格类型检查
- 使用接口定义数据结构
- 避免 any 类型

### Vue 规范
- 使用 Composition API
- 组件名使用 PascalCase
- Props 定义类型

### 提交规范
```
feat: 添加新功能
fix: 修复问题
docs: 更新文档
style: 代码格式调整
refactor: 代码重构
test: 测试相关
chore: 构建工具相关
```

## 🚀 性能优化

### 渲染优化
- 虚拟滚动处理大列表
- 组件懒加载
- 图片懒加载

### 内存优化
- 及时清理事件监听器
- 避免内存泄漏
- 合理使用缓存

### 构建优化
- 代码分割
- Tree Shaking
- 资源压缩

## 🔐 安全考虑

### Electron 安全
- 禁用 Node.js 集成
- 启用上下文隔离
- 验证 IPC 消息

### 数据安全
- 输入验证
- 文件路径检查
- 权限控制

## 📚 扩展开发

### 添加新功能
1. 创建相应的类型定义
2. 实现业务逻辑
3. 创建 UI 组件
4. 编写测试
5. 更新文档

### 插件系统
- 支持第三方插件
- 提供插件 API
- 插件生命周期管理

---

这份开发文档将帮助开发者快速了解项目结构和开发流程。如有疑问，请参考代码注释或联系开发团队。
