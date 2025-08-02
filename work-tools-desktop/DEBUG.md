# 调试指南

## 问题说明

在 Electron + Vite 开发环境中，`useFileSystem.ts` 等 renderer 进程的代码不会编译到 `.vite` 目录中，而是通过 Vite 开发服务器动态提供服务。

## 解决方案

### 1. 调试配置

已在 `.vscode/launch.json` 中添加了两个调试配置：

- **Debug Main Process**: 调试 main 进程代码
- **Debug Renderer Process**: 调试 renderer 进程代码（包括 useFileSystem.ts）

### 2. 使用方法

#### 调试 Renderer 进程（包括 useFileSystem.ts）

1. **启动应用**：
   ```bash
   npm start
   ```

2. **在 VS Code 中设置断点**：
   - 打开 `src/renderer/composables/useFileSystem.ts`
   - 在需要调试的行号左侧点击设置断点

3. **启动调试**：
   - 按 `F5` 或选择 "Run" -> "Start Debugging"
   - 选择 "Debug Renderer Process" 配置
   - 等待调试器连接到端口 9222

4. **开始调试**：
   - 在应用中操作触发断点
   - 可以查看变量、调用栈、执行调试操作

#### 调试 Main 进程

1. **启动调试**：
   - 按 `F5` 或选择 "Run" -> "Start Debugging"
   - 选择 "Debug Main Process" 配置

2. **设置断点**：
   - 在 `src/main/` 目录下的文件中设置断点

### 3. 验证调试端口

应用启动后，可以通过以下命令确认调试端口是否开启：
```bash
netstat -ano | findstr :9222
```

### 4. 注意事项

- 确保没有其他应用占用 9222 端口
- 调试时需要保持开发服务器运行
- 每次修改代码后，热重载会自动生效，断点可能需要重新设置

### 5. 开发环境特点

- **Main 进程**：编译到 `.vite/build/main.js`
- **Preload 脚本**：编译到 `.vite/build/preload.js`
- **Renderer 进程**：通过 Vite 开发服务器（端口 5173）提供服务，支持热重载

这种架构确保了开发时的快速迭代和实时调试能力。