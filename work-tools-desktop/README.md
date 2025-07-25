# 工作工具 (Work Tools Desktop)

一个基于 Electron + Vue 3 + UnoCSS 的批量文件处理桌面应用程序，专为文件匹配和重命名操作而设计。

## 🚀 功能特性

### 📁 文件匹配器
- **智能文件匹配**: 基于自定义规则匹配文件名
- **规则管理**: 支持用户自定义规则和系统预设规则
- **批量处理**: 一次性处理大量文件
- **匹配结果预览**: 实时显示匹配状态和结果
- **规则导入导出**: 支持规则的备份和分享

### ✏️ 文件重命名器
- **多种重命名模式**: 替换、添加、删除、编号等
- **实时预览**: 重命名前预览新文件名
- **批量重命名**: 支持批量文件重命名操作
- **撤销功能**: 支持重命名操作的撤销
- **历史记录**: 保存重命名历史便于回溯

### 🎯 用户体验
- **拖拽支持**: 支持拖拽文件和文件夹到应用
- **键盘快捷键**: 丰富的快捷键支持提高效率
- **响应式界面**: 现代化的用户界面设计
- **实时统计**: 显示文件数量、匹配状态等统计信息
- **错误处理**: 友好的错误提示和处理机制

## 🛠️ 技术栈

- **前端框架**: Vue 3 (Composition API)
- **桌面框架**: Electron
- **样式系统**: UnoCSS
- **状态管理**: Pinia
- **构建工具**: Vite
- **测试框架**: Vitest
- **打包工具**: Electron Forge

## 📦 安装和使用

### 开发环境要求
- Node.js >= 18
- npm >= 9

### 安装依赖
```bash
cd work-tools-desktop
npm install
```

### 开发模式
```bash
npm start
```

### 运行测试
```bash
# 运行所有测试
npm run test:run

# 交互式测试
npm test

# 测试 UI
npm run test:ui
```

### 构建应用
```bash
# 打包应用
npm run package

# 构建安装程序
npm run make
```

## 🎮 使用指南

### 文件匹配器
1. **添加文件**: 点击"选择文件"或"选择目录"，或直接拖拽文件到应用
2. **管理规则**: 点击"管理规则"添加或编辑匹配规则
3. **执行匹配**: 点击"开始匹配"执行文件匹配
4. **查看结果**: 在文件列表中查看匹配状态和结果

### 文件重命名器
1. **添加文件**: 选择需要重命名的文件
2. **设置操作**: 选择重命名模式并配置参数
3. **预览结果**: 查看重命名预览效果
4. **执行重命名**: 确认无误后执行重命名操作

### 快捷键
- `Ctrl + 1`: 切换到文件匹配器
- `Ctrl + 2`: 切换到文件重命名器
- `Ctrl + O`: 选择文件
- `Ctrl + A`: 全选文件

## 🏗️ 项目结构

```
work-tools-desktop/
├── src/
│   ├── main/                 # 主进程
│   │   ├── main.ts          # 主进程入口
│   │   ├── preload.ts       # 预加载脚本
│   │   └── handlers/        # IPC 处理器
│   └── renderer/            # 渲染进程
│       ├── App.vue          # 主应用组件
│       ├── components/      # Vue 组件
│       │   ├── common/      # 通用组件
│       │   ├── file-matcher/ # 文件匹配器组件
│       │   └── file-renamer/ # 文件重命名器组件
│       ├── composables/     # 组合式函数
│       ├── stores/          # Pinia 状态管理
│       ├── types/           # TypeScript 类型定义
│       └── constants/       # 常量定义
├── assets/                  # 静态资源
├── tests/                   # 测试文件
└── docs/                    # 文档
```

## 🧪 测试

项目包含全面的测试覆盖：

- **单元测试**: 组件、存储、组合式函数测试
- **集成测试**: 端到端功能测试
- **用户体验测试**: 交互和性能测试

测试统计：
- 总测试数: 182+
- 测试覆盖率: 90%+
- 组件测试: 40+
- 功能测试: 60+

## 📋 开发规范

### 代码风格
- 使用 TypeScript 进行类型安全
- 遵循 Vue 3 Composition API 最佳实践
- 使用 UnoCSS 原子化 CSS 类
- 保持组件单一职责原则

### 提交规范
- feat: 新功能
- fix: 修复问题
- docs: 文档更新
- style: 样式调整
- refactor: 代码重构
- test: 测试相关
- chore: 构建/工具相关

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [Electron](https://electronjs.org/) - 跨平台桌面应用框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [UnoCSS](https://unocss.dev/) - 即时原子化 CSS 引擎
- [Vite](https://vitejs.dev/) - 下一代前端构建工具

## 📞 支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/FAQ.md)
2. 搜索现有的 [Issues](https://github.com/work-tools/desktop/issues)
3. 创建新的 Issue 描述问题
4. 联系开发团队: team@work-tools.com

---

**工作工具** - 让文件处理更简单、更高效！ 🚀
