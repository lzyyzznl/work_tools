# Windows 小工具集合

一个包含三个实用Windows小工具的项目集合：批量打印工具、文件名匹配工具和批量文件重命名工具。

## 📁 项目结构

```
windows_small_tools/
├── apps/                           # 应用程序目录
│   ├── batch_printer/              # 批量打印工具
│   │   ├── src/batch_printer/      # 源代码
│   │   ├── resources/              # 资源文件
│   │   └── run.py                  # 入口脚本
│   ├── file_matcher/               # 文件名匹配工具
│   │   ├── src/file_matcher/       # 源代码
│   │   ├── resources/              # 资源文件
│   │   └── run.py                  # 入口脚本
│   ├── file_renamer/               # 批量文件重命名工具
│   │   ├── src/file_renamer/       # 源代码
│   │   ├── resources/              # 资源文件
│   │   └── run.py                  # 入口脚本
│   └── shared_resources/           # 共享资源文件
├── scripts/                        # 构建脚本
│   ├── nuitka_build_batch_printer.py
│   ├── nuitka_build_file_matcher.py
│   ├── nuitka_build_file_renamer.py
│   ├── nuitka_build_all.py
│   └── README_Nuitka.md
├── dist/                           # 构建输出目录
├── pyproject.toml                  # 项目配置
└── README.md                       # 说明文档
```

## 🛠️ 工具介绍

### 🖨️ 批量打印工具
- **功能**: 批量打印多个文件，支持各种文件格式
- **特色**: 智能打印设置、预览功能、错误处理
- **运行**: `python apps/batch_printer/gui.py`

### 📋 文件名匹配工具  
- **功能**: 根据条件匹配和筛选文件，支持Excel导出
- **特色**: 多种匹配模式、实时预览、数据分析
- **运行**: `python apps/file_matcher/gui.py`

### 🔄 批量文件重命名工具
- **功能**: 批量重命名文件，支持多种重命名模式
- **特色**: 实时预览、撤销功能、智能跳过
- **运行**: `python apps/file_renamer/gui.py`

## 🚀 快速开始

### 环境要求
- Python 3.8+
- PySide6 (原PyQt5已迁移)
- 其他依赖见 `pyproject.toml`

### 安装依赖（使用uv来进行依赖管理）

```bash
# 第一步先安装uv
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# pip安装
pip install uv

#第二步创建环境
uv venv --python 3.12
# 激活环境（windows环境）
.venv\Scripts\activate

# 第三步使用uv安装所有依赖项
# 在根目录下，安装所有依赖
uv pip install -r pyproject.toml  
```


## 📦 打包为可执行文件
### 构建单个工具
```bash
# 构建批量打印工具
python scripts/nuitka_build_batch_printer.py

# 构建文件名匹配工具
python scripts/nuitka_build_file_matcher.py

# 构建批量文件重命名工具
python scripts/nuitka_build_file_renamer.py
```

### 构建所有工具
```bash
# 构建所有工具
python scripts/nuitka_build_all.py all

# 查看可用工具
python scripts/nuitka_build_all.py --list
```

构建完成后，可执行文件位于 `dist/` 目录。

### 为什么选择Nuitka

Nuitka相比PyInstaller有以下优势：
- **更好的性能** - 编译为C++代码，运行速度更快
- **更小的文件** - 通过优化生成更紧凑的可执行文件
- **更好的兼容性** - 对PySide6等复杂库支持更佳

详细构建说明请参考 `scripts/README_Nuitka.md`

## 🎯 特色功能

### 🛡️ 安全特性
- **预览确认** - 所有操作前先预览效果
- **撤销功能** - 支持撤销最近的操作
- **智能跳过** - 自动处理异常情况
- **错误日志** - 详细的错误信息记录

### 🎨 用户界面
- **现代化设计** - 简洁美观的界面
- **拖拽支持** - 支持文件和文件夹拖拽
- **实时反馈** - 操作过程中的实时状态显示
- **颜色标识** - 直观的颜色提示系统

### ⚡ 性能优化
- **多线程处理** - 大量文件处理时保持界面响应
- **内存优化** - 高效的内存使用策略
- **缓存机制** - 智能缓存提升响应速度

## 🔧 开发说明

### 项目组织
每个工具都有独立的目录结构：
- `src/` - 源代码目录
- `resources/` - 资源文件目录  
- `run.py` - 独立的入口脚本

### 资源管理
- 每个工具有独立的资源文件
- 共享资源放在 `apps/shared_resources/`
- 构建时自动包含相应资源


## 📝 更新日志
### v3.1.0 (当前版本)
- 🔄 **重大更新：从PyQt5迁移到PySide6**
- 🚀 提升应用性能和稳定性  
- 🛠️ 更新所有构建脚本支持PySide6
- 📝 更新文档反映迁移变化
- ✅ 保持所有原有功能和UI风格

### v3.0.0  
- ✨ 重新组织项目结构，三个工具完全分离
- 🔄 从PyInstaller迁移到Nuitka构建系统  
- 📁 资源文件与代码文件分离管理
- 🧹 清理无关文件，精简项目结构
- 🚀 优化构建脚本，提升构建效率

### v2.1.0  
- ✨ 完成三个工具的功能开发
- 🎨 统一界面设计风格
- 📦 加入PyInstaller构建支持

## 📄 许可证

本项目仅供学习和个人使用。

## 👨‍💻 作者

**荔枝鱼**  
版本：v3.0.0  
©版权所有
