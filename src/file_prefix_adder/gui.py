import os
import sys
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QFileDialog,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
    QCheckBox,
    QGroupBox,
    QStatusBar,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMenu,
    QAction,
    QMessageBox,
    QAbstractItemView,
)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QKeySequence
from PyQt5.QtWidgets import QShortcut
import shutil


class FilePrefixAdder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件名处理工具")
        self.setMinimumSize(800, 600)
        self.resize(1500, 1000)
        self.version = "1.0.0"
        self.current_directory = ""

        # 创建状态栏
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.addPermanentWidget(
            QLabel(f"author:lizeyu  v{self.version} @版权所有，禁止商用")
        )

        # 主控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 文件夹选择
        folder_layout = QHBoxLayout()
        folder_label = QLabel("目标文件夹:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("请选择文件夹...")
        self.folder_input.editingFinished.connect(self.on_folder_input_changed)  # 添加失焦事件
        browse_btn = QPushButton("浏览")
        browse_btn.clicked.connect(self.browse_folder)

        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_input)
        folder_layout.addWidget(browse_btn)
        layout.addLayout(folder_layout)

        # 操作类型选择
        operation_group = QGroupBox("操作类型")
        operation_layout = QVBoxLayout()

        self.replace_radio = QRadioButton("替换字符串")
        self.add_radio = QRadioButton("添加前缀/后缀")
        self.number_radio = QRadioButton("批量添加序号")
        self.add_radio.setChecked(True)

        operation_layout.addWidget(self.replace_radio)
        operation_layout.addWidget(self.add_radio)
        operation_layout.addWidget(self.number_radio)
        operation_group.setLayout(operation_layout)
        layout.addWidget(operation_group)

        # 替换字符串输入
        self.replace_layout = QHBoxLayout()
        replace_label = QLabel("替换字符串:")
        self.replace_from = QLineEdit()
        self.replace_from.setPlaceholderText("原字符串")
        self.replace_to = QLineEdit()
        self.replace_to.setPlaceholderText("新字符串")

        self.replace_layout.addWidget(replace_label)
        self.replace_layout.addWidget(self.replace_from)
        self.replace_layout.addWidget(self.replace_to)
        layout.addLayout(self.replace_layout)

        # 前缀/后缀输入
        self.add_layout = QHBoxLayout()
        self.position_group = QButtonGroup()

        prefix_radio = QRadioButton("前缀")
        suffix_radio = QRadioButton("后缀")
        prefix_radio.setChecked(True)

        self.position_group.addButton(prefix_radio, 0)
        self.position_group.addButton(suffix_radio, 1)

        self.add_text = QLineEdit()
        self.add_text.setPlaceholderText("要添加的文本")

        self.add_layout.addWidget(prefix_radio)
        self.add_layout.addWidget(suffix_radio)
        self.add_layout.addWidget(self.add_text)
        layout.addLayout(self.add_layout)

        # 序号功能输入 - 重新设计布局
        self.number_layout = QHBoxLayout()
        
        # 序号位置组
        position_group_widget = QWidget()
        position_layout = QHBoxLayout()
        position_layout.setContentsMargins(0, 0, 0, 0)
        position_layout.setSpacing(2)  # 减少内部间距
        
        number_pos_label = QLabel("位置:")
        self.number_position_group = QButtonGroup()
        
        number_prefix_radio = QRadioButton("前缀")
        number_suffix_radio = QRadioButton("后缀")
        number_position_radio = QRadioButton("指定位置")
        number_prefix_radio.setChecked(True)
        
        self.number_position_group.addButton(number_prefix_radio, 0)
        self.number_position_group.addButton(number_suffix_radio, 1)
        self.number_position_group.addButton(number_position_radio, 2)
        
        # 指定位置的输入框
        self.position_input = QLineEdit()
        self.position_input.setText("2")
        self.position_input.setMaximumWidth(40)
        self.position_input.setEnabled(False)  # 默认禁用
        self.position_input.setToolTip("从第几位开始插入序号")
        
        # 连接信号，当选择指定位置时启用输入框
        number_position_radio.toggled.connect(lambda checked: self.position_input.setEnabled(checked))
        
        position_layout.addWidget(number_pos_label)
        position_layout.addWidget(number_prefix_radio)
        position_layout.addWidget(number_suffix_radio)
        position_layout.addWidget(number_position_radio)
        position_layout.addWidget(self.position_input)
        # 不在这里添加弹性空间，保持组内紧凑
        position_group_widget.setLayout(position_layout)
        
        # 起始和位数组（使用固定容器确保标签和输入框紧贴）
        number_params_widget = QWidget()
        number_params_layout = QHBoxLayout()
        number_params_layout.setContentsMargins(0, 0, 0, 0)
        number_params_layout.setSpacing(0)  # 容器间无间距
        
        # 起始容器
        start_container = QWidget()
        start_container.setFixedWidth(80)  # 固定容器宽度
        start_layout = QHBoxLayout()
        start_layout.setContentsMargins(0, 0, 0, 0)
        start_layout.setSpacing(1)
        start_label = QLabel("起始:")
        self.start_number = QLineEdit()
        self.start_number.setText("1")
        self.start_number.setMaximumWidth(50)
        start_layout.addWidget(start_label)
        start_layout.addWidget(self.start_number)
        start_container.setLayout(start_layout)
        
        # 位数容器
        digits_container = QWidget()
        digits_container.setFixedWidth(80)  # 固定容器宽度
        digits_layout = QHBoxLayout()
        digits_layout.setContentsMargins(0, 0, 0, 0)
        digits_layout.setSpacing(2)
        digits_label = QLabel("位数:")
        self.number_digits = QLineEdit()
        self.number_digits.setText("1")
        self.number_digits.setMaximumWidth(50)
        digits_layout.addWidget(digits_label)
        digits_layout.addWidget(self.number_digits)
        digits_container.setLayout(digits_layout)
        
        # 步长容器
        step_container = QWidget()
        step_container.setFixedWidth(80)  # 固定容器宽度
        step_layout = QHBoxLayout()
        step_layout.setContentsMargins(0, 0, 0, 0)
        step_layout.setSpacing(2)
        step_label = QLabel("步长:")
        self.number_step = QLineEdit()
        self.number_step.setText("1")
        self.number_step.setMaximumWidth(50)
        self.number_step.setToolTip("支持小数，如0.1, 0.5等")
        step_layout.addWidget(step_label)
        step_layout.addWidget(self.number_step)
        step_container.setLayout(step_layout)
        
        number_params_layout.addWidget(start_container)
        number_params_layout.addWidget(digits_container)
        number_params_layout.addWidget(step_container)
        number_params_widget.setLayout(number_params_layout)
        
        # 递增/递减组
        direction_group_widget = QWidget()
        direction_layout = QHBoxLayout()
        direction_layout.setContentsMargins(0, 0, 0, 0)
        direction_layout.setSpacing(2)  # 减少内部间距
        
        direction_label = QLabel("方向:")
        self.number_direction_group = QButtonGroup()
        
        increase_radio = QRadioButton("递增")
        decrease_radio = QRadioButton("递减")
        increase_radio.setChecked(True)
        
        self.number_direction_group.addButton(increase_radio, 0)
        self.number_direction_group.addButton(decrease_radio, 1)
        
        direction_layout.addWidget(direction_label)
        direction_layout.addWidget(increase_radio)
        direction_layout.addWidget(decrease_radio)
        # 不在这里添加弹性空间，保持紧凑
        direction_group_widget.setLayout(direction_layout)
        
        # 连接符号组（使用固定容器）
        separator_group_widget = QWidget()
        separator_group_widget.setFixedWidth(100)  # 固定容器宽度
        separator_layout = QHBoxLayout()
        separator_layout.setContentsMargins(0, 0, 0, 0)
        separator_layout.setSpacing(5)  # 标签和输入框间距
        
        separator_label = QLabel("连接符:")
        self.separator_input = QLineEdit()
        self.separator_input.setText(".")
        self.separator_input.setMaximumWidth(30)
        self.separator_input.setToolTip("序号和文件名之间的连接符号")
        
        separator_layout.addWidget(separator_label)
        separator_layout.addWidget(self.separator_input)
        separator_group_widget.setLayout(separator_layout)
        
        # 添加到主布局，组之间使用固定间距，右侧用弹性空间
        self.number_layout.addWidget(position_group_widget)
        self.number_layout.addSpacing(20)  # 组之间的固定间距
        self.number_layout.addWidget(number_params_widget)
        self.number_layout.addSpacing(20)  # 组之间的固定间距
        self.number_layout.addWidget(direction_group_widget)
        self.number_layout.addSpacing(20)  # 组之间的固定间距
        self.number_layout.addWidget(separator_group_widget)
        self.number_layout.addStretch()  # 右侧弹性空间，窗口变大时只增加这里的距离
        
        layout.addLayout(self.number_layout)

        # 递归处理选项
        self.recursive_check = QCheckBox("是否需要处理子级文件夹")
        self.recursive_check.setChecked(True)
        layout.addWidget(self.recursive_check)

        # 按钮
        btn_layout = QHBoxLayout()
        self.execute_btn = QPushButton("执行")
        self.execute_btn.clicked.connect(self.execute)
        quit_btn = QPushButton("退出")
        quit_btn.clicked.connect(self.close)

        btn_layout.addWidget(self.execute_btn)
        btn_layout.addWidget(quit_btn)
        layout.addLayout(btn_layout)

        # 输出区域 - 分割为文件列表和日志区域（上下布局）
        splitter = QSplitter(Qt.Vertical)
        
        # 文件列表区域的容器
        file_list_container = QWidget()
        file_list_layout = QVBoxLayout()
        file_list_container.setLayout(file_list_layout)
        
        # 文件列表区域标题和操作按钮
        header_layout = QHBoxLayout()
        
        # 全选复选框
        self.header_checkbox = QCheckBox("全选")
        self.header_checkbox.clicked.connect(self.on_header_checkbox_clicked)
        
        header_label = QLabel("文件列表")
        header_label.setStyleSheet("font-weight: bold;")
        
        # 返回上一级按钮
        back_btn = QPushButton("返回上一级")
        back_btn.setMinimumWidth(100)
        back_btn.setMaximumWidth(120)
        back_btn.clicked.connect(self.go_to_parent_directory)
        
        refresh_btn = QPushButton("刷新")
        refresh_btn.setMaximumWidth(60)
        refresh_btn.clicked.connect(self.load_file_list)
        
        header_layout.addWidget(self.header_checkbox)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(back_btn)
        header_layout.addWidget(refresh_btn)
        file_list_layout.addLayout(header_layout)
        
        # 文件列表表格
        self.file_list_table = QTableWidget()
        self.file_list_table.setColumnCount(5)
        self.file_list_table.setHorizontalHeaderLabels(["选择", "文件名", "类型", "大小", "修改时间"])
        self.file_list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_list_table.setColumnWidth(0, 50)  # 复选框列宽度
        self.file_list_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_list_table.setAlternatingRowColors(True)
        
        # 启用表头排序
        self.file_list_table.setSortingEnabled(True)
        
        # 设置表头
        self.file_list_table.setHorizontalHeaderLabels(["选择", "文件名", "类型", "大小", "修改时间"])
        self.file_list_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_list_table.setColumnWidth(0, 50)  # 复选框列宽度
        
        # 设置双击事件
        self.file_list_table.itemDoubleClicked.connect(self.on_item_double_clicked)
        
        # 设置右键菜单
        self.file_list_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_list_table.customContextMenuRequested.connect(self.show_context_menu)
        
        file_list_layout.addWidget(self.file_list_table)
        
        # 下方日志区域
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setMaximumHeight(150)
        
        splitter.addWidget(file_list_container)
        splitter.addWidget(self.log_area)
        splitter.setSizes([400, 150])
        
        layout.addWidget(splitter)
        
        # 设置快捷键
        self.setup_shortcuts()
        
        # 存储剪贴板数据
        self.clipboard_data = []
        self.clipboard_operation = None  # 'copy' or 'cut'
        
        # 设置按钮样式
        self.setup_button_styles()

    def setup_button_styles(self):
        """设置按钮样式为深色"""
        button_style = """
        QPushButton {
            background-color: #3c3c3c;
            color: white;
            border: 1px solid #555555;
            border-radius: 4px;
            padding: 6px 12px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #4a4a4a;
            border-color: #777777;
        }
        QPushButton:pressed {
            background-color: #2a2a2a;
            border-color: #333333;
        }
        QPushButton:disabled {
            background-color: #2a2a2a;
            color: #666666;
            border-color: #333333;
        }
        """
        
        # 找到所有QPushButton并应用样式
        for button in self.findChildren(QPushButton):
            button.setStyleSheet(button_style)

    def setup_shortcuts(self):
        """设置快捷键"""
        # Ctrl+A 全选
        select_all_shortcut = QShortcut(QKeySequence("Ctrl+A"), self)
        select_all_shortcut.activated.connect(self.select_all_files)
        
        # Ctrl+C 复制
        copy_shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        copy_shortcut.activated.connect(self.copy_selected_files)
        
        # Ctrl+X 剪切
        cut_shortcut = QShortcut(QKeySequence("Ctrl+X"), self)
        cut_shortcut.activated.connect(self.cut_selected_files)
        
        # Ctrl+V 粘贴
        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        paste_shortcut.activated.connect(self.paste_files)
        
        # Delete 删除
        delete_shortcut = QShortcut(QKeySequence("Delete"), self)
        delete_shortcut.activated.connect(self.delete_selected_files)

    def on_folder_input_changed(self):
        """处理文件夹路径输入框失焦事件"""
        folder_path = self.folder_input.text().strip()
        if not folder_path:
            return
            
        # 检查路径是否存在
        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            # 路径有效，更新当前目录并加载文件列表
            self.current_directory = folder_path
            self.load_file_list()
            self.log_area.append(f"已切换到目录: {folder_path}")
        else:
            # 路径无效，提示用户
            QMessageBox.warning(self, "路径错误", f"指定的路径不存在或不是有效的文件夹:\n{folder_path}")
            self.log_area.append(f"错误：无效的文件夹路径: {folder_path}")
            # 恢复到之前的有效路径
            if self.current_directory:
                self.folder_input.setText(self.current_directory)
            else:
                self.folder_input.clear()

    def go_to_parent_directory(self):
        """返回上一级目录"""
        if not self.current_directory:
            return
            
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:  # 确保不是根目录
            self.current_directory = parent_dir
            self.folder_input.setText(self.current_directory)
            self.load_file_list()
            self.log_area.append(f"已返回上一级目录: {parent_dir}")
        else:
            self.log_area.append("已在根目录，无法继续返回上一级")

    def browse_folder(self):
        # 使用自定义的文件夹选择对话框
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)  # 显示文件和文件夹
        dialog.setOption(QFileDialog.DontUseNativeDialog, True)  # 使用Qt对话框而不是系统原生对话框
        dialog.setOption(QFileDialog.DontConfirmOverwrite, True)  # 允许选择当前目录
        dialog.setAcceptMode(QFileDialog.AcceptOpen)
        dialog.setWindowTitle("选择文件夹（可以看到文件但只能选择文件夹）")
        
        # 设置初始目录
        if self.current_directory and os.path.isdir(self.current_directory):
            dialog.setDirectory(self.current_directory)
        
        if dialog.exec_():
            # 获取选择的目录（无论是否选中具体项目）
            selected_dir = dialog.directory().absolutePath()
            if selected_dir and os.path.isdir(selected_dir):
                self.folder_input.setText(selected_dir)
                self.current_directory = selected_dir
                self.load_file_list()
    
    def load_file_list(self):
        """加载文件列表到表格"""
        if not self.current_directory or not os.path.isdir(self.current_directory):
            return
            
        self.file_list_table.setRowCount(0)
        
        # 重置表头复选框 - 添加安全检查
        if hasattr(self, 'header_checkbox') and self.header_checkbox:
            self.header_checkbox.setChecked(False)
        
        try:
            items = []
            # 获取当前目录下的所有项目
            for item_name in os.listdir(self.current_directory):
                item_path = os.path.join(self.current_directory, item_name)
                if os.path.isdir(item_path):
                    item_type = "文件夹"
                    item_size = ""
                else:
                    item_type = "文件"
                    try:
                        size = os.path.getsize(item_path)
                        item_size = self.format_file_size(size)
                    except:
                        item_size = "未知"
                
                try:
                    mtime = os.path.getmtime(item_path)
                    import datetime
                    mod_time = datetime.datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")
                except:
                    mod_time = "未知"
                
                items.append((item_name, item_type, item_size, mod_time))
            
            # 排序：文件夹在前，然后按名称排序
            items.sort(key=lambda x: (x[1] != "文件夹", x[0].lower()))
            
            # 添加到表格
            for i, (name, type_, size, mtime) in enumerate(items):
                self.file_list_table.insertRow(i)
                
                # 复选框列
                checkbox = QCheckBox()
                self.file_list_table.setCellWidget(i, 0, checkbox)
                
                # 其他列
                self.file_list_table.setItem(i, 1, QTableWidgetItem(name))
                self.file_list_table.setItem(i, 2, QTableWidgetItem(type_))
                self.file_list_table.setItem(i, 3, QTableWidgetItem(size))
                self.file_list_table.setItem(i, 4, QTableWidgetItem(mtime))
                
        except Exception as e:
            self.log_area.append(f"加载文件列表出错: {e}")
    
    def format_file_size(self, size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def on_item_double_clicked(self, item):
        """处理双击事件"""
        if item is None or item.column() != 1:  # 只处理文件名列的双击（现在是第1列）
            return
            
        row = item.row()
        
        # 安全检查：确保表格项不为空
        filename_item = self.file_list_table.item(row, 1)
        file_type_item = self.file_list_table.item(row, 2)
        
        if filename_item is None or file_type_item is None:
            self.log_area.append("错误：无法获取文件信息")
            return
            
        filename = filename_item.text()
        file_type = file_type_item.text()
        
        if file_type == "文件夹":
            # 进入子文件夹
            new_dir = os.path.join(self.current_directory, filename)
            if os.path.isdir(new_dir):
                self.current_directory = new_dir
                self.folder_input.setText(self.current_directory)
                self.load_file_list()
        else:
            # 打开文件
            file_path = os.path.join(self.current_directory, filename)
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                self.log_area.append(f"已打开文件: {filename}")
            except Exception as e:
                self.log_area.append(f"打开文件失败: {filename} - {e}")
    
    def show_context_menu(self, position):
        """显示右键菜单"""
        item = self.file_list_table.itemAt(position)
        if item is None:
            return
            
        menu = QMenu(self)
        row = item.row()
        
        # 安全检查：确保表格项不为空
        filename_item = self.file_list_table.item(row, 1)
        if filename_item is None:
            return
            
        filename = filename_item.text()
        
        # 显示文件操作菜单
        # 复制操作
        copy_action = QAction("复制 (Ctrl+C)", self)
        copy_action.triggered.connect(self.copy_selected_files)
        menu.addAction(copy_action)
        
        # 剪切操作
        cut_action = QAction("剪切 (Ctrl+X)", self)
        cut_action.triggered.connect(self.cut_selected_files)
        menu.addAction(cut_action)
        
        # 删除操作
        delete_action = QAction("删除 (Delete)", self)
        delete_action.triggered.connect(self.delete_selected_files)
        menu.addAction(delete_action)
        
        menu.addSeparator()
        
        # 重命名操作
        rename_action = QAction("重命名", self)
        rename_action.triggered.connect(lambda: self.rename_selected_item(row))
        menu.addAction(rename_action)
        
        menu.addSeparator()
        
        # 粘贴操作（如果剪贴板有内容）
        if self.clipboard_data:
            paste_action = QAction("粘贴 (Ctrl+V)", self)
            paste_action.triggered.connect(self.paste_files)
            menu.addAction(paste_action)
            menu.addSeparator()
        
        # 刷新操作
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.load_file_list)
        menu.addAction(refresh_action)
        
        menu.exec_(self.file_list_table.mapToGlobal(position))
    
    def rename_selected_item(self, row):
        """重命名选中的项目"""
        filename_item = self.file_list_table.item(row, 1)  # 文件名现在在第1列
        if filename_item is None:
            self.log_area.append("错误：无法获取文件信息")
            return
            
        old_name = filename_item.text()
        
        from PyQt5.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(self, "重命名", "新文件名:", text=old_name)
        
        if ok and new_name and new_name != old_name:
            old_path = os.path.join(self.current_directory, old_name)
            new_path = os.path.join(self.current_directory, new_name)
            
            try:
                os.rename(old_path, new_path)
                self.log_area.append(f"重命名成功: {old_name} -> {new_name}")
                self.load_file_list()  # 刷新列表
            except Exception as e:
                self.log_area.append(f"重命名失败: {old_name} - {e}")
                QMessageBox.warning(self, "重命名失败", f"重命名失败: {e}")

    def select_all_files(self):
        """全选所有文件"""
        for row in range(self.file_list_table.rowCount()):
            checkbox = self.file_list_table.cellWidget(row, 0)
            if checkbox and checkbox.isEnabled():  # 只选择可用的复选框
                checkbox.setChecked(True)
        self.log_area.append("已全选所有文件")

    def unselect_all_files(self):
        """取消全选"""
        for row in range(self.file_list_table.rowCount()):
            checkbox = self.file_list_table.cellWidget(row, 0)
            if checkbox:
                checkbox.setChecked(False)
        self.log_area.append("已取消全选")

    def invert_selection(self):
        """反选"""
        for row in range(self.file_list_table.rowCount()):
            checkbox = self.file_list_table.cellWidget(row, 0)
            if checkbox and checkbox.isEnabled():  # 只操作可用的复选框
                checkbox.setChecked(not checkbox.isChecked())
        self.log_area.append("已反选文件")

    def on_header_checkbox_clicked(self):
        """处理表头复选框点击事件"""
        checked = self.header_checkbox.isChecked()
        
        if checked:
            # 全选
            self.select_all_files()
        else:
            # 反选逻辑：如果当前有选中的，就取消全选；如果没有选中的，就全选
            has_selected = any(
                self.file_list_table.cellWidget(row, 0).isChecked()
                for row in range(self.file_list_table.rowCount())
                if self.file_list_table.cellWidget(row, 0) and self.file_list_table.cellWidget(row, 0).isEnabled()
            )
            
            if has_selected:
                self.unselect_all_files()
                self.header_checkbox.setChecked(False)
            else:
                self.invert_selection()

    def copy_selected_files(self):
        """复制选中的文件"""
        selected_files = self.get_selected_files()
        if not selected_files:
            self.log_area.append("没有选中任何文件")
            return
        
        self.clipboard_data = []
        for filename in selected_files:
            file_path = os.path.join(self.current_directory, filename)
            self.clipboard_data.append(file_path)
        
        self.clipboard_operation = 'copy'
        self.log_area.append(f"已复制 {len(selected_files)} 个文件到剪贴板")

    def cut_selected_files(self):
        """剪切选中的文件"""
        selected_files = self.get_selected_files()
        if not selected_files:
            self.log_area.append("没有选中任何文件")
            return
        
        self.clipboard_data = []
        for filename in selected_files:
            file_path = os.path.join(self.current_directory, filename)
            self.clipboard_data.append(file_path)
        
        self.clipboard_operation = 'cut'
        self.log_area.append(f"已剪切 {len(selected_files)} 个文件到剪贴板")

    def paste_files(self):
        """粘贴文件"""
        if not self.clipboard_data:
            self.log_area.append("剪贴板为空")
            return
        
        success_count = 0
        error_count = 0
        
        for source_path in self.clipboard_data:
            if not os.path.exists(source_path):
                self.log_area.append(f"源文件不存在: {source_path}")
                error_count += 1
                continue
            
            filename = os.path.basename(source_path)
            target_path = os.path.join(self.current_directory, filename)
            
            # 如果目标文件已存在，生成新文件名
            if os.path.exists(target_path):
                name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(target_path):
                    new_filename = f"{name}_副本{counter}{ext}"
                    target_path = os.path.join(self.current_directory, new_filename)
                    counter += 1
            
            try:
                if self.clipboard_operation == 'copy':
                    if os.path.isdir(source_path):
                        shutil.copytree(source_path, target_path)
                    else:
                        shutil.copy2(source_path, target_path)
                elif self.clipboard_operation == 'cut':
                    shutil.move(source_path, target_path)
                
                success_count += 1
            except Exception as e:
                self.log_area.append(f"粘贴失败 {filename}: {e}")
                error_count += 1
        
        if self.clipboard_operation == 'cut':
            # 剪切完成后清空剪贴板
            self.clipboard_data = []
            self.clipboard_operation = None
        
        self.log_area.append(f"粘贴完成: 成功 {success_count} 个，失败 {error_count} 个")
        self.load_file_list()  # 刷新文件列表

    def delete_selected_files(self):
        """删除选中的文件"""
        selected_files = self.get_selected_files()
        if not selected_files:
            self.log_area.append("没有选中任何文件")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除选中的 {len(selected_files)} 个文件吗？\n此操作不可撤销！",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        success_count = 0
        error_count = 0
        
        for filename in selected_files:
            file_path = os.path.join(self.current_directory, filename)
            try:
                if os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                else:
                    os.remove(file_path)
                success_count += 1
            except Exception as e:
                self.log_area.append(f"删除失败 {filename}: {e}")
                error_count += 1
        
        self.log_area.append(f"删除完成: 成功 {success_count} 个，失败 {error_count} 个")
        self.load_file_list()  # 刷新文件列表

    def get_selected_files(self):
        """获取选中的文件列表"""
        selected_files = []
        for row in range(self.file_list_table.rowCount()):
            checkbox = self.file_list_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                filename_item = self.file_list_table.item(row, 1)
                if filename_item is None:
                    continue  # 跳过空项
                filename = filename_item.text()
                selected_files.append(filename)
        return selected_files

    def process_files(self, directory):
        """处理目录下的文件"""
        directory = Path(directory)
        if not directory.is_dir():
            self.log_area.append(f"错误：{directory} 不是有效目录")
            return

        # 获取选中的文件
        selected_files = self.get_selected_files()
        
        if selected_files:
            self.log_area.append(f"开始处理选中的 {len(selected_files)} 个项目: {directory}")
        else:
            self.log_area.append(f"未选择任何项目，将处理所有文件: {directory}")

        # 根据选择的操作类型进行处理
        if self.replace_radio.isChecked():
            # 替换字符串模式
            old_str = self.replace_from.text()
            new_str = self.replace_to.text()

            if not old_str:
                self.log_area.append("错误：原字符串不能为空")
                return

            self._replace_in_filenames(directory, old_str, new_str, selected_files)
        elif self.add_radio.isChecked():
            # 添加前缀/后缀模式
            text = self.add_text.text()
            if not text:
                self.log_area.append("错误：要添加的文本不能为空")
                return

            is_prefix = self.position_group.checkedId() == 0
            self._add_to_filenames(directory, text, is_prefix, selected_files)
        else:
            # 批量添加序号模式
            try:
                start_num = float(self.start_number.text())
                digits = int(self.number_digits.text())
                step = float(self.number_step.text())
            except ValueError:
                self.log_area.append("错误：起始数字、位数和步长必须是有效数字")
                return
                
            if digits < 1:
                self.log_area.append("错误：位数必须大于0")
                return
                
            position_mode = self.number_position_group.checkedId()  # 0=前缀, 1=后缀, 2=指定位置
            is_increase = self.number_direction_group.checkedId() == 0
            separator = self.separator_input.text()
            
            # 如果是指定位置模式，获取位置值
            insert_position = None
            if position_mode == 2:  # 指定位置
                try:
                    insert_position = int(self.position_input.text())
                    if insert_position < 1:
                        self.log_area.append("错误：指定位置必须大于等于1")
                        return
                except ValueError:
                    self.log_area.append("错误：指定位置必须是有效整数")
                    return
                    
            self._add_numbers_to_filenames(directory, start_num, digits, step, position_mode, insert_position, separator, is_increase, selected_files)

    def _replace_in_filenames(self, directory, old_str, new_str, selected_files=None):
        """替换文件名中的字符串"""
        for root, _, files in (
            os.walk(directory)
            if self.recursive_check.isChecked()
            else [(directory, [], os.listdir(directory))]
        ):
            for filename in files:
                # 如果有选中文件列表，只处理选中的文件
                if selected_files and filename not in selected_files:
                    continue
                    
                if old_str in filename:
                    new_name = filename.replace(old_str, new_str)
                    self._rename_file(root, filename, new_name)

    def _add_to_filenames(self, directory, text, is_prefix, selected_files=None):
        """添加前缀或后缀"""
        for root, _, files in (
            os.walk(directory)
            if self.recursive_check.isChecked()
            else [(directory, [], os.listdir(directory))]
        ):
            for filename in files:
                # 如果有选中文件列表，只处理选中的文件
                if selected_files and filename not in selected_files:
                    continue
                    
                name, ext = os.path.splitext(filename)
                new_name = (text + name + ext) if is_prefix else (name + text + ext)
                self._rename_file(root, filename, new_name)

    def _add_numbers_to_filenames(self, directory, start_num, digits, step, position_mode, insert_position, separator, is_increase, selected_files=None):
        """添加序号到文件名"""
        # 收集要处理的文件
        files_to_process = []
        for root, _, files in (
            os.walk(directory)
            if self.recursive_check.isChecked()
            else [(directory, [], os.listdir(directory))]
        ):
            for filename in files:
                # 如果有选中文件列表，只处理选中的文件
                if selected_files and filename not in selected_files:
                    continue
                files_to_process.append((root, filename))
        
        # 排序确保处理顺序一致
        files_to_process.sort(key=lambda x: x[1].lower())
        
        # 如果是递减，反转列表
        if not is_increase:
            files_to_process.reverse()
        
        # 处理每个文件
        for i, (root, filename) in enumerate(files_to_process):
            current_num = start_num + (i * step if is_increase else -i * step)
            
            # 格式化数字：如果是整数就不显示小数点，否则显示小数
            if current_num == int(current_num):
                number_str = str(int(current_num)).zfill(digits)
            else:
                # 小数情况，保留必要的小数位
                number_str = f"{current_num:.10g}".zfill(digits)
            
            name, ext = os.path.splitext(filename)
            
            if position_mode == 0:  # 前缀
                new_name = f"{number_str}{separator}{name}{ext}"
            elif position_mode == 1:  # 后缀
                new_name = f"{name}{separator}{number_str}{ext}"
            else:  # 指定位置
                # 在指定位置插入序号
                if insert_position <= len(name):
                    before = name[:insert_position-1]
                    after = name[insert_position-1:]
                    new_name = f"{before}{number_str}{separator}{after}{ext}"
                else:
                    # 如果指定位置超出文件名长度，则添加到末尾
                    new_name = f"{name}{separator}{number_str}{ext}"
            
            self._rename_file(root, filename, new_name)

    def _rename_file(self, root, old_name, new_name):
        """执行文件重命名"""
        old_path = Path(root) / old_name
        new_path = Path(root) / new_name

        try:
            old_path.rename(new_path)
            self.log_area.append(f"已重命名: {old_name} -> {new_name}")
        except Exception as e:
            self.log_area.append(f"重命名 {old_name} 失败: {e}")

    def execute(self):
        folder = self.folder_input.text()
        if not folder:
            self.log_area.append("错误：文件夹路径不能为空")
            return

        # 使用当前目录作为处理目录
        if self.current_directory:
            folder = self.current_directory
            
        self.process_files(folder)
        self.log_area.append("操作完成！")
        
        # 刷新文件列表
        if self.current_directory:
            self.load_file_list()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilePrefixAdder()
    window.show()
    sys.exit(app.exec_())
