# Windows 小工具集合

一个包含三个实用Windows小工具的项目集合：批量打印工具、文件名匹配工具和批量文件重命名工具。

## 📁 项目结构

```
windows_small_tools/
├── apps/                           # 应用程序目录
│   ├── batch_printer/              # 批量打印工具
│   │   ├── gui.py                 # 主程序入口
│   │   └── resources/              # 资源文件
│   ├── file_matcher/               # 文件名匹配工具
│   │   ├── gui.py                 # 主程序入口
│   │   ├── resources/              # 资源文件
│   │   ├── rule_manager.py        # 规则管理器
│   │   └── rule_settings.py       # 规则设置
│   └── file_renamer/              # 批量文件重命名工具
│       ├── gui.py                # 主程序入口
│       └── resources/             # 资源文件
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
- **特色**: 
  - 打印队列管理，支持暂停/停止
  - 多线程处理，保持界面响应
  - 打印状态实时反馈
  - 支持多种打印选项设置
  - 错误处理和日志记录
- **运行**: `python apps/batch_printer/gui.py`

### 📋 文件名匹配工具  
- **功能**: 根据条件匹配和筛选文件，支持Excel导出
- **特色**: 
  - 规则管理，支持自定义匹配规则
  - 实时预览匹配结果
  - 支持批量导出到Excel
  - 拖拽文件支持
  - 多种匹配模式可选
- **运行**: `python apps/file_matcher/gui.py`

### 🔄 批量文件重命名工具
- **功能**: 批量重命名文件，支持多种重命名模式
- **特色**: 
  - 自定义重命名规则
  - 实时预览重命名效果
  - 支持撤销操作
  - 快捷键支持
  - 拖拽文件支持
  - 智能跳过已处理文件
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
- **现代化设计** - 基于PySide6的现代化界面
- **拖拽支持** - 支持文件和文件夹拖拽
- **实时反馈** - 操作过程中的实时状态显示
- **颜色标识** - 直观的颜色提示系统
- **统一风格** - 所有工具采用统一的设计语言

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
### v1.0.0 (当前版本)
- 🛠️ 使用PySide6构建现代化界面
- 📦 使用Nuitka进行高效打包
- 📁 清晰的项目结构和资源管理
- 🚀 优化的构建和分发流程
- ✅ 四个实用工具的完整实现

### v0.1.0  
- ✨ 初始版本发布
- 📁 基础项目结构搭建
- 🛠️ 核心功能开发完成
- 📝 初始文档编写完成

### v2.1.0  
- ✨ 完成三个工具的功能开发
- 🎨 统一界面设计风格
- 📦 加入PyInstaller构建支持

## 📄 许可证

本项目采用MIT许可证，详情请参阅LICENSE文件。

## 👨‍💻 作者

**荔枝鱼**  
版本：v1.0.0  
©版权所有

## 📝 联系方式

- 邮箱：632795136@qq.com
- GitHub：https://github.com/qq632795136/work_tools
