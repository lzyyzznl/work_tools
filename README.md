# 文件名前缀添加工具

## 功能
递归地为指定文件夹及其子文件夹下所有文件添加统一前缀

## 环境初始化
1. 确保已安装Python 3.8+和uv
2. 安装依赖：
   ```bash
   uv pip install -e .
   ```
3. 安装打包工具：
   ```bash
   uv pip install pyinstaller
   ```

## 打包为Windows可执行文件
```bash
python build_exe.py
```
生成的exe文件位于dist目录下

## 使用方式
### 图形界面(GUI)版本
运行dist/FilePrefixAdderGUI.exe

### 命令行版本
```bash
prefix-adder
```

### 作为Python模块
```bash
python -m file_prefix_adder.main
```

## 开发
1. 安装开发依赖：
   ```bash
   uv pip install -e ".[dev]"
   ```
2. 运行测试：
   ```bash
   pytest
   ```

## 注意事项
- 程序会修改原文件名，请先备份重要文件
- 不支持撤销操作
- 遇到重名文件时会跳过并报错
- 支持中文路径和文件名

## 示例
### GUI版本
1. 运行FilePrefixAdderGUI.exe
2. 点击"浏览"选择目标文件夹
3. 输入要添加的前缀
4. 点击"执行"按钮

### 命令行版本
```bash
prefix-adder
```
然后输入：
```
请输入目标文件夹路径: D:/test
请输入要添加的前缀: 2025_
```
将把D:/test目录下所有文件改为"2025_原文件名"的形式
