# Nuitka 构建工具使用说明

本目录包含使用 Nuitka 打包工具的脚本，用于将 Python 应用程序编译为高性能的可执行文件。

## 为什么选择 Nuitka

Nuitka 相比 PyInstaller 有以下优势：

1. **更好的性能** - Nuitka 将 Python 代码编译为 C++，运行速度更快
2. **更小的文件尺寸** - 通过精确的依赖分析，生成的可执行文件通常更小
3. **更好的兼容性** - 对复杂的 Python 特性支持更好
4. **更强的优化** - 支持多种编译优化选项

## 安装依赖

在使用构建脚本之前，请确保安装了必要的依赖：

```bash
pip install nuitka PyQt5 pywin32 pandas
```

对于图标转换功能，还需要安装：
```bash
pip install Pillow
```

## 可用的构建脚本

### 单独构建脚本

1. **`nuitka_build_batch_printer.py`** - 构建批量打印工具（简化版）
2. **`nuitka_build_file_matcher.py`** - 构建文件名匹配工具（简化版）
3. **`nuitka_build_file_renamer.py`** - 构建批量文件重命名工具（简化版）

### 统一构建脚本

- **`nuitka_build_all.py`** - 统一管理所有构建任务（简化版）
- **`build_with_nuitka.py`** - 原型简化构建脚本

## 使用方法

### 构建单个应用

```bash
# 构建批量打印工具
python scripts/nuitka_build_batch_printer.py

# 构建文件名匹配工具
python scripts/nuitka_build_file_matcher.py

# 构建批量文件重命名工具
python scripts/nuitka_build_file_renamer.py
```

### 使用统一构建脚本

```bash
# 查看所有可用的应用
python scripts/nuitka_build_all.py --list

# 构建特定应用
python scripts/nuitka_build_all.py batch_printer
python scripts/nuitka_build_all.py file_matcher
python scripts/nuitka_build_all.py file_renamer

# 构建所有应用
python scripts/nuitka_build_all.py all
```

## 输出文件

构建完成后，可执行文件将位于：
- **输出目录**: `dist/`
- **日志文件**: `nuitka_build.log` 或 `nuitka_build_all.log`

## Nuitka 参数说明

构建脚本使用了以下主要的 Nuitka 参数：

- `--onefile` - 生成单个可执行文件
- `--standalone` - 独立模式，包含所有依赖
- `--windows-console-mode=disable` - 禁用控制台窗口（GUI应用）
- `--windows-icon-from-ico` - 设置应用图标
- `--include-package` - 包含特定Python包
- `--include-data-dir` - 包含数据文件目录
- `--noinclude-custom-mode` - 排除不需要的模块以减小文件大小

## 优化特性

脚本包含以下优化：

1. **模块排除** - 自动排除不必要的大型模块（如 matplotlib, scipy 等）
2. **图标处理** - 自动检测和转换图标格式
3. **依赖检查** - 构建前检查所有必要依赖
4. **清理功能** - 自动清理旧的构建文件
5. **错误处理** - 详细的错误报告和日志记录

## 故障排除

### 常见问题

1. **缺少依赖**
   ```
   错误: 缺少依赖: nuitka
   解决: pip install nuitka
   ```

2. **图标转换失败**
   ```
   警告: 未安装Pillow，无法自动转换图标格式
   解决: pip install Pillow
   ```

3. **构建失败**
   - 检查 Python 版本（需要 3.8+）
   - 查看日志文件获取详细错误信息
   - 确保所有源文件存在

### 性能优化建议

- 使用 SSD 硬盘可显著提升构建速度
- 关闭杀毒软件的实时监控（构建期间）
- 确保有足够的内存和磁盘空间

## 与 PyInstaller 的区别

| 特性 | Nuitka | PyInstaller |
|------|---------|-------------|
| 执行速度 | 更快（编译优化） | 普通 |
| 文件大小 | 通常更小 | 较大 |
| 构建时间 | 较长 | 较短 |
| 兼容性 | 优秀 | 良好 |
| 调试支持 | 较复杂 | 简单 |

## 升级说明

如果您之前使用 PyInstaller 构建脚本，现在可以：

1. 使用新的 Nuitka 脚本进行构建
2. 旧的 PyInstaller 脚本已被标记为弃用
3. 推荐使用 Nuitka 以获得更好的性能和更小的文件大小 