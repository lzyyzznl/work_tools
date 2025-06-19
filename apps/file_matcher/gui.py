import datetime
import os
import subprocess
import sys
from pathlib import Path

import pandas as pd
from PySide6.QtCore import  Qt, QUrl
from PySide6.QtGui import (QAction, QColor, QDesktopServices,
                           QIcon)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QCheckBox,
                               QDialog, QFileDialog, QHBoxLayout,
                               QHeaderView, QLabel, QLineEdit, QMainWindow,
                               QMenu, QMessageBox, QPushButton,
                               QSplitter, QStatusBar, QTableWidget,
                               QTableWidgetItem, QToolBar, QVBoxLayout,
                               QWidget)
from rule_manager import RuleManager
from rule_settings import RuleEditDialog, RuleSettingsDialog


class FileMatcherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件名匹配工具 - 增强版")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置窗口图标
        self.set_window_icon()

        # 初始化数据
        self.rule_manager = RuleManager()
        self.files_data = []  # 存储文件信息的列表
        
        # 设置苹果风格
        self.setup_apple_style()
        self.init_ui()
        
        # 启用拖拽
        self.setAcceptDrops(True)

    def set_window_icon(self):
        """设置窗口图标 - 兼容不同的打包方式"""
        icon_files = ["icon.png", "icon.ico"]
        
        # 尝试多种路径查找图标
        search_paths = [
            # Nuitka打包后的资源路径
            "resources",
            # 开发环境路径
            "apps/file_matcher/resources",
            # 相对路径
            os.path.join(os.path.dirname(__file__), "resources"),
            # 绝对路径（开发环境）
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "apps", "file_matcher", "resources")
        ]
        
        for search_path in search_paths:
            for icon_file in icon_files:
                icon_path = os.path.join(search_path, icon_file)
                if os.path.exists(icon_path):
                    try:
                        self.setWindowIcon(QIcon(icon_path))
                        print(f"成功加载图标: {icon_path}")
                        return
                    except Exception as e:
                        print(f"加载图标失败 {icon_path}: {e}")
                        continue
        
        print("未找到合适的图标文件")

    def setup_apple_style(self):
        """设置苹果官网风格的样式和字体"""
        # 设置字体
        from PySide6.QtGui import QFont, QFontDatabase
        
        apple_font_families = [
            "PingFang SC", "SF Pro Display", "SF Pro Text", "system-ui",
            "-apple-system", "BlinkMacSystemFont", "Helvetica Neue",
            "Microsoft YaHei UI", "Segoe UI", "Arial", "sans-serif"
        ]
        
        available_fonts = QFontDatabase.families()
        
        selected_font_family = "Arial"
        for font_family in apple_font_families:
            if font_family in available_fonts:
                selected_font_family = font_family
                break
        
        app_font = QFont(selected_font_family, 14)
        app_font.setWeight(QFont.Normal)
        app_font.setStyleHint(QFont.SansSerif)
        QApplication.instance().setFont(app_font)
        
        # 设置样式表
        self.setStyleSheet(f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(255, 255, 255, 1.0));
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                color: #1d1d1f;
            }}
            
            QToolBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(250, 250, 252, 0.95));
                border: none;
                border-bottom: 1px solid rgba(0, 0, 0, 0.1);
                padding: 8px;
                spacing: 6px;
            }}
            
            QToolBar QToolButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(245, 245, 247, 0.9));
                color: #1d1d1f;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                font-weight: 600;
                min-width: 80px;
                min-height: 20px;
            }}
            
            QToolBar QToolButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(250, 250, 252, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.15);
            }}
            
            QToolBar QToolButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 242, 1.0),
                    stop:1 rgba(235, 235, 237, 1.0));
            }}
            
            QTableWidget {{
                background: white;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                font-size: 13px;
                gridline-color: rgba(0, 0, 0, 0.1);
                selection-background-color: rgba(0, 122, 255, 0.2);
            }}
            
            QHeaderView::section {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(240, 240, 240, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                padding: 8px;
                font-weight: 600;
                color: #1d1d1f;
                font-size: 13px;
            }}
            
            QStatusBar {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.95),
                    stop:1 rgba(250, 250, 252, 0.95));
                border-top: 1px solid rgba(0, 0, 0, 0.1);
                padding: 6px 12px;
                font-size: 12px;
                color: #6e6e73;
            }}
            
            QLabel {{
                color: #1d1d1f;
                font-weight: 500;
                font-size: 14px;
            }}
            
            QCheckBox {{
                font-size: 14px;
                font-weight: 500;
                color: #1d1d1f;
                spacing: 8px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 2px solid rgba(0, 0, 0, 0.2);
                border-radius: 4px;
                background: white;
            }}
            
            QCheckBox::indicator:checked {{
                background: #007AFF;
                border: 2px solid #007AFF;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }}
            
            QGroupBox {{
                font-weight: 600;
                font-size: 16px;
                color: #1d1d1f;
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
            }}
            
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
            }}
        """)

    def init_ui(self):
        """初始化UI界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 创建工具栏
        self.create_toolbar()

        # 创建主要内容区域
        content_splitter = QSplitter(Qt.Vertical)
        
        # 文件管理区域
        file_section = self.create_file_section()
        content_splitter.addWidget(file_section)
        
        # 设置分割比例
        content_splitter.setSizes([600])
        
        main_layout.addWidget(content_splitter)
        
        # 创建状态栏
        self.create_status_bar()

    def create_toolbar(self):
        """创建工具栏"""
        toolbar = QToolBar()
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.addToolBar(toolbar)

        # 添加文件按钮
        add_files_action = QAction("📁 添加文件", self)
        add_files_action.setShortcut("Ctrl+O")
        add_files_action.triggered.connect(self.add_files)
        toolbar.addAction(add_files_action)

        # 添加文件夹按钮
        add_folder_action = QAction("📂 添加文件夹", self)
        add_folder_action.setShortcut("Ctrl+Shift+O")
        add_folder_action.triggered.connect(self.add_folder)
        toolbar.addAction(add_folder_action)

        toolbar.addSeparator()

        # 匹配按钮
        match_action = QAction("🔍 开始匹配", self)
        match_action.setShortcut("Ctrl+M")
        match_action.triggered.connect(self.match_files)
        toolbar.addAction(match_action)

        toolbar.addSeparator()

        # 清空列表按钮
        clear_action = QAction("🗑 清空列表", self)
        clear_action.setShortcut("Ctrl+L")
        clear_action.triggered.connect(self.clear_file_list)
        toolbar.addAction(clear_action)

        toolbar.addSeparator()

        # 导出按钮
        export_action = QAction("💾 导出结果", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_data)
        toolbar.addAction(export_action)

        toolbar.addSeparator()

        # 规则设置按钮
        rules_action = QAction("⚙️ 规则设置", self)
        rules_action.triggered.connect(self.show_rule_settings)
        toolbar.addAction(rules_action)

    def create_file_section(self):
        """创建文件管理区域"""
        section_widget = QWidget()
        layout = QVBoxLayout(section_widget)

        # 文件信息栏
        info_layout = QHBoxLayout()
        
        # 搜索框
        self.search_label = QLabel("搜索:")
        self.search_label.hide()  # 初始隐藏
        info_layout.addWidget(self.search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键字搜索文件...")
        self.search_edit.textChanged.connect(self.filter_files)
        self.search_edit.setFixedWidth(200)
        self.search_edit.hide()  # 初始隐藏
        info_layout.addWidget(self.search_edit)
        
        info_layout.addStretch()

        # 文件统计标签
        self.file_stats_label = QLabel()
        self.file_stats_label.hide()  # 初始隐藏
        info_layout.addWidget(self.file_stats_label)

        layout.addLayout(info_layout)

        # 创建表格
        self.file_table = QTableWidget()
        self.file_table.setColumnCount(8)
        self.file_table.setHorizontalHeaderLabels([
            "选择", "文件名", "路径", "匹配结果", "Code", "30d", "匹配规则", "操作"
        ])

        # 设置表格属性
        self.file_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.file_table.setAlternatingRowColors(True)
        self.file_table.setSortingEnabled(True)
        
        # 设置列宽策略
        header = self.file_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)  # 选择列固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # 文件名自适应
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # 路径自适应
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # 匹配结果
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Code
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # 30d
        header.setSectionResizeMode(6, QHeaderView.Stretch)  # 匹配规则
        header.setSectionResizeMode(7, QHeaderView.Fixed)  # 操作列固定宽度
        
        self.file_table.setColumnWidth(0, 60)  # 选择列宽度
        self.file_table.setColumnWidth(7, 110)  # 操作列宽度

        # 设置右键菜单
        self.file_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.file_table.customContextMenuRequested.connect(self.show_table_context_menu)

        layout.addWidget(self.file_table)

        # 创建空状态提示
        self.empty_state_widget = self.create_empty_state_widget()
        layout.addWidget(self.empty_state_widget)
        
        # 初始状态显示空提示
        self.file_table.hide()
        self.empty_state_widget.show()

        return section_widget

    def create_empty_state_widget(self):
        """创建空状态提示widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        # 图标标签
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)

        # 主提示文本
        main_text = QLabel("暂无文件")
        main_text.setAlignment(Qt.AlignCenter)
        main_text.setStyleSheet("""
            font-size: 24px;
            font-weight: 600;
            color: #1d1d1f;
            margin: 0;
        """)
        layout.addWidget(main_text)

        # 副提示文本
        sub_text = QLabel("拖拽文件或文件夹到此处，或使用工具栏按钮添加文件")
        sub_text.setAlignment(Qt.AlignCenter)
        sub_text.setStyleSheet("""
            font-size: 16px;
            color: #6e6e73;
            margin: 0;
        """)
        layout.addWidget(sub_text)

        # 快速操作按钮
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignCenter)
        button_layout.setSpacing(12)

        add_files_btn = QPushButton("📁 选择文件")
        add_files_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 122, 255, 1.0),
                    stop:1 rgba(0, 100, 220, 1.0));
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 1.0),
                    stop:1 rgba(0, 122, 255, 1.0));
            }
        """)
        add_files_btn.clicked.connect(self.add_files)
        button_layout.addWidget(add_files_btn)

        add_folder_btn = QPushButton("📂 选择文件夹")
        add_folder_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(245, 245, 247, 0.9));
                color: #1d1d1f;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 16px;
                font-weight: 600;
                min-width: 120px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(250, 250, 252, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.15);
            }
        """)
        add_folder_btn.clicked.connect(self.add_folder)
        button_layout.addWidget(add_folder_btn)

        layout.addLayout(button_layout)

        return widget

    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")

        # 版权信息
        copyright_label = QLabel("作者:荔枝鱼  @版权所有,请勿随意传播与商用")
        copyright_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #8e8e93;
                font-style: italic;
            }
        """)
        self.status_bar.addPermanentWidget(copyright_label)

    def dragEnterEvent(self, event):
        """处理拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """处理拖拽放置事件"""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.is_file():
                    self.add_file_to_table(str(path))
                elif path.is_dir():
                    for item in path.iterdir():
                        if item.is_file():
                            self.add_file_to_table(str(item))
        
        self.update_status("通过拖拽添加了文件")
        self.update_file_stats()

    def add_files(self):
        """添加文件对话框"""
        files_paths, _ = QFileDialog.getOpenFileNames(self, "选择文件")
        if files_paths:
            for path in files_paths:
                self.add_file_to_table(path)
            self.update_status(f"添加了 {len(files_paths)} 个文件")
            self.update_file_stats()

    def add_folder(self):
        """添加文件夹对话框"""
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:
            paths = [str(item) for item in Path(folder_path).iterdir() if item.is_file()]
            for path in paths:
                self.add_file_to_table(path)
            self.update_status(f"从文件夹添加了 {len(paths)} 个文件")
            self.update_file_stats()

    def add_file_to_table(self, file_path: str):
        """添加文件到表格"""
        path_obj = Path(file_path)
        
        # 检查是否已经存在
        for file_data in self.files_data:
            if file_data["path"] == file_path:
                return  # 文件已存在，不重复添加
        
        # 添加到数据列表
        file_info = {
            "path": file_path,
            "name": path_obj.name,
            "directory": str(path_obj.parent),
            "size": path_obj.stat().st_size if path_obj.exists() else 0,
            "matched": False,
            "match_info": None
        }
        self.files_data.append(file_info)
        
        # 显示表格，隐藏空状态
        if self.file_table.isHidden():
            self.empty_state_widget.hide()
            self.file_table.show()
        
        # 更新表格显示
        self.refresh_table_display()

    def refresh_table_display(self):
        """刷新表格显示"""
        self.file_table.setRowCount(len(self.files_data))
        
        for row, file_data in enumerate(self.files_data):
            # 选择框
            checkbox = QCheckBox()
            checkbox.setChecked(True)
            self.file_table.setCellWidget(row, 0, checkbox)
            
            # 文件名
            name_item = QTableWidgetItem(file_data["name"])
            name_item.setToolTip(file_data["name"])
            self.file_table.setItem(row, 1, name_item)
            
            # 路径
            path_item = QTableWidgetItem(file_data["directory"])
            path_item.setToolTip(file_data["path"])
            self.file_table.setItem(row, 2, path_item)
            
            # 匹配结果
            if file_data["matched"]:
                match_item = QTableWidgetItem("✅ 匹配")
                match_item.setBackground(QColor(144, 238, 144))  # 淡绿色
                
                info = file_data["match_info"]
                code_item = QTableWidgetItem(str(info["code"]))
                thirty_d_item = QTableWidgetItem(str(info["30d"]))
                rule_item = QTableWidgetItem(info["matched_rule"])
                
                code_item.setBackground(QColor(144, 238, 144))
                thirty_d_item.setBackground(QColor(144, 238, 144))
                rule_item.setBackground(QColor(144, 238, 144))
            else:
                match_item = QTableWidgetItem("❌ 未匹配")
                match_item.setBackground(QColor(255, 182, 193))  # 淡红色
                
                code_item = QTableWidgetItem("")
                thirty_d_item = QTableWidgetItem("")
                rule_item = QTableWidgetItem("")
                
                code_item.setBackground(QColor(255, 182, 193))
                thirty_d_item.setBackground(QColor(255, 182, 193))
                rule_item.setBackground(QColor(255, 182, 193))
            
            self.file_table.setItem(row, 3, match_item)
            self.file_table.setItem(row, 4, code_item)
            self.file_table.setItem(row, 5, thirty_d_item)
            self.file_table.setItem(row, 6, rule_item)
            
            # 操作按钮
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(2, 2, 2, 2)
            action_layout.setSpacing(2)
            
            if file_data["matched"]:
                # 匹配成功时显示编辑规则按钮
                edit_rule_btn = QPushButton("✏️ 修改规则")
                edit_rule_btn.setFixedSize(100, 25)
                edit_rule_btn.setToolTip("修改规则")
                edit_rule_btn.clicked.connect(lambda checked, r=row: self.edit_rule_for_file(r))
                action_layout.addWidget(edit_rule_btn)
            else:
                # 未匹配时显示新增规则按钮
                add_rule_btn = QPushButton("➕ 添加规则")
                add_rule_btn.setFixedSize(100, 25)
                add_rule_btn.setToolTip("添加规则")
                add_rule_btn.clicked.connect(lambda checked, r=row: self.add_rule_for_file(r))
                action_layout.addWidget(add_rule_btn)
            
            action_layout.addStretch()
            self.file_table.setCellWidget(row, 7, action_widget)
        
        # 更新统计信息
        self.update_file_stats()

    def match_files(self):
        """执行文件匹配"""
        if not self.files_data:
            QMessageBox.information(self, "提示", "请先添加文件")
            return
        
        # 重新加载规则
        self.rule_manager.load_rules()
        
        matched_count = 0
        for file_data in self.files_data:
            is_matched, match_info = self.rule_manager.match_filename(file_data["name"])
            file_data["matched"] = is_matched
            file_data["match_info"] = match_info
            if is_matched:
                matched_count += 1
        
        # 刷新显示
        self.refresh_table_display()
        
        total_files = len(self.files_data)
        unmatched_count = total_files - matched_count
        self.update_status(f"匹配完成: 共{total_files}个文件，匹配成功{matched_count}个，未匹配{unmatched_count}个")

    def clear_file_list(self):
        """清空文件列表"""
        reply = QMessageBox.question(
            self, "确认清空", 
            "确定要清空所有文件吗？", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.files_data.clear()
            self.file_table.setRowCount(0)
            
            # 显示空状态
            self.file_table.hide()
            self.empty_state_widget.show()
            
            self.update_status("文件列表已清空")
            self.update_file_stats()

    def show_table_context_menu(self, position):
        """显示表格右键菜单"""
        menu = QMenu(self)
        
        clicked_item = self.file_table.itemAt(position)
        if clicked_item:
            row = clicked_item.row()
            
            # 文件操作
            open_file_action = menu.addAction("📄 打开文件")
            open_file_action.triggered.connect(lambda: self.open_file(row))
            
            open_folder_action = menu.addAction("📂 打开文件夹")
            open_folder_action.triggered.connect(lambda: self.open_file_folder(row))
            
            menu.addSeparator()
            
            # 列表操作
            remove_action = menu.addAction("🗑 从列表移除")
            remove_action.triggered.connect(self.remove_selected_files)
        else:
            # 通用操作
            remove_action = menu.addAction("🗑 移除选中文件")
            remove_action.triggered.connect(self.remove_selected_files)
        
        menu.exec_(self.file_table.mapToGlobal(position))

    def open_file(self, row: int):
        """打开文件"""
        if 0 <= row < len(self.files_data):
            file_path = self.files_data[row]["path"]
            try:
                QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                self.update_status(f"已打开文件: {Path(file_path).name}")
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开文件:\n{str(e)}")

    def open_file_folder(self, row: int):
        """打开文件所在文件夹"""
        if 0 <= row < len(self.files_data):
            file_path = self.files_data[row]["path"]
            try:
                if os.name == "nt":  # Windows
                    subprocess.run(f'explorer /select,"{file_path}"', check=True)
                elif sys.platform == "darwin":  # macOS
                    subprocess.run(["open", "-R", file_path], check=True)
                else:  # Linux
                    subprocess.run(["xdg-open", str(Path(file_path).parent)], check=True)
                self.update_status(f"已打开文件夹: {Path(file_path).parent}")
            except Exception as e:
                QMessageBox.warning(self, "打开失败", f"无法打开文件夹:\n{str(e)}")

    def remove_selected_files(self):
        """移除选中的文件"""
        # 获取选中的行
        selected_rows = set()
        for row in range(self.file_table.rowCount()):
            checkbox = self.file_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_rows.add(row)
        
        if not selected_rows:
            # 如果没有选中，则获取当前行
            current_row = self.file_table.currentRow()
            if current_row >= 0:
                selected_rows.add(current_row)
        
        if not selected_rows:
            QMessageBox.information(self, "提示", "请先选择要移除的文件")
            return
        
        # 按倒序删除，避免索引问题
        for row in sorted(selected_rows, reverse=True):
            if 0 <= row < len(self.files_data):
                del self.files_data[row]
        
        # 刷新显示
        if not self.files_data:
            self.file_table.hide()
            self.empty_state_widget.show()
        else:
            self.refresh_table_display()
        
        self.update_status(f"移除了 {len(selected_rows)} 个文件")
        self.update_file_stats()

    def export_data(self):
        """导出数据"""
        if not self.files_data:
            QMessageBox.information(self, "提示", "没有数据可导出")
            return
        
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"file_match_result_{timestamp}.xlsx"

            file_path, selected_filter = QFileDialog.getSaveFileName(
                self, "导出文件", default_name,
                "Excel Files (*.xlsx);;Excel 97-2003 (*.xls);;CSV Files (*.csv)"
            )

            if not file_path:
                return

            # 准备数据
            data = []
            for file_data in self.files_data:
                if file_data["matched"]:
                    info = file_data["match_info"]
                    data.append([
                        file_data["name"],
                        file_data["directory"],
                        "是",
                        info["code"],
                        info["30d"],
                        info["matched_rule"]
                    ])
                else:
                    data.append([
                        file_data["name"],
                        file_data["directory"],
                        "否",
                        "",
                        "",
                        ""
                    ])

            df = pd.DataFrame(data, columns=[
                "文件名", "文件路径", "是否匹配成功", "Code", "30d", "匹配的规则"
            ])

            # 导出文件
            if selected_filter == "Excel Files (*.xlsx)":
                if not file_path.endswith(".xlsx"):
                    file_path += ".xlsx"
                df.to_excel(file_path, index=False)
            elif selected_filter == "Excel 97-2003 (*.xls)":
                if not file_path.endswith(".xls"):
                    file_path += ".xls"
                df.to_excel(file_path, index=False)
            else:
                if not file_path.endswith(".csv"):
                    file_path += ".csv"
                df.to_csv(file_path, index=False, encoding="utf_8_sig")

            self.update_status(f"已导出到: {file_path}")
            
            # 询问是否打开文件
            reply = QMessageBox.question(
                self, "导出成功", 
                f"文件已成功导出到:\n{file_path}\n\n是否打开文件？",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                try:
                    QDesktopServices.openUrl(QUrl.fromLocalFile(file_path))
                except Exception as e:
                    QMessageBox.warning(self, "打开失败", f"无法打开文件:\n{str(e)}")

        except Exception as e:
            QMessageBox.critical(self, "导出失败", f"导出文件时发生错误:\n{str(e)}")

    def show_rule_settings(self):
        """显示规则设置对话框"""
        dialog = RuleSettingsDialog(self)
        if dialog.exec() == QDialog.Accepted:
            # 重新加载规则
            self.rule_manager.load_rules()
            self.update_status("规则设置已更新")

    def update_status(self, message: str):
        """更新状态栏消息"""
        self.status_bar.showMessage(message)

    def update_file_stats(self):
        """更新文件统计显示"""
        total_count = len(self.files_data)
        
        if total_count == 0:
            # 无数据时隐藏统计信息和搜索框
            self.file_stats_label.hide()
            self.search_label.hide()
            self.search_edit.hide()
            return
        
        # 有数据时显示搜索框
        self.search_label.show()
        self.search_edit.show()
        
        # 统计匹配结果
        matched_count = sum(1 for file_data in self.files_data if file_data["matched"])
        unmatched_count = total_count - matched_count
        
        stats_text = f"总计: {total_count} | 匹配成功: {matched_count} | 未匹配: {unmatched_count}"
        self.file_stats_label.setText(stats_text)
        self.file_stats_label.show()
    
    def filter_files(self, text):
        """根据搜索文本过滤文件表格"""
        text = text.lower()
        for row in range(self.file_table.rowCount()):
            show_row = False
            for col in range(self.file_table.columnCount() - 1):  # 排除操作列
                item = self.file_table.item(row, col)
                if item and text in item.text().lower():
                    show_row = True
                    break
            self.file_table.setRowHidden(row, not show_row)

    def edit_rule_for_file(self, row: int):
        """为匹配的文件编辑规则"""
        if 0 <= row < len(self.files_data):
            file_data = self.files_data[row]
            if file_data["matched"] and file_data["match_info"]:
                # 获取匹配信息中的规则索引
                match_info = file_data["match_info"]
                rule_index = match_info["index"]
                
                # 获取规则数据
                df_rules = self.rule_manager.get_all_rules()
                if rule_index < len(df_rules):
                    rule_data = df_rules.iloc[rule_index].to_dict()
                    
                    # 打开编辑对话框
                    dialog = RuleSettingsDialog(self)
                    dialog.rules_table.selectRow(rule_index)
                    dialog.edit_rule()
                    
                    # 重新匹配文件
                    self.match_files()

    def add_rule_for_file(self, row: int):
        """为未匹配的文件添加规则"""
        if 0 <= row < len(self.files_data):
            file_data = self.files_data[row]
            filename = file_data["name"]
            
            # 打开新增规则对话框，并预填文件名作为匹配规则
            dialog = RuleEditDialog(self, rule_manager=self.rule_manager)
            # 预填match_rule1为文件名的一部分（去掉扩展名）
            if dialog.match_rule_widgets and "match_rule1" in dialog.match_rule_widgets:
                base_name = filename.rsplit('.', 1)[0] if '.' in filename else filename
                dialog.match_rule_widgets["match_rule1"].setText(base_name)
            
            if dialog.exec() == QDialog.Accepted:
                # 重新匹配文件
                self.match_files()


def main():
    """文件名匹配工具主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("文件名匹配工具")
    app.setApplicationVersion("3.0.0")
    app.setOrganizationName("荔枝鱼")
    
    # 创建并显示主窗口
    window = FileMatcherGUI()
    window.show()
    
    # 运行应用程序
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 