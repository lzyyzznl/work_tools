import math
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
    QTabWidget,
    QToolBar,
    QStyle,
    QInputDialog,
)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QDateTime
from PyQt5.QtGui import QDesktopServices, QKeySequence, QIcon, QColor, QCursor
from PyQt5.QtWidgets import QShortcut
import shutil


class FileRenamer(QMainWindow):
    """
    The main application window for the batch file renaming tool.
    It orchestrates the UI components and handles the main application logic.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量文件重命名工具")
        self.setMinimumSize(900, 700)
        self.resize(1400, 900)
        self.version = "2.0.0"
        self.files_data = []
        self.history = []
        
        # Auto-preview timer - delays preview update by 0.3 seconds after user input
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.auto_preview_changes)

        # --- Setup Paths and Icons ---
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(f"{os.sep}src{os.sep}", 1)[0]

        self.resource_path = os.path.join(base_path, "src", "resource")
        
        icon_path = os.path.join(self.resource_path, "icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        # --- Enable Drag and Drop ---
        self.setAcceptDrops(True)

        self.init_ui()

    # ----------------------------------------------------------------------
    # UI Creation Methods
    # ----------------------------------------------------------------------

    def init_ui(self):
        """Initializes and lays out all UI components."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.main_layout = QVBoxLayout(central_widget)

        self.create_toolbar()
        
        splitter = QSplitter(Qt.Vertical)
        
        self.tabs = self.create_operation_tabs()
        
        table_container = QWidget()
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create select all layout first (always at top)
        self.file_table, self.select_all_layout = self.create_file_table()
        
        # Create a widget to hold the select all layout so we can hide/show it easily
        self.select_all_widget = QWidget()
        select_all_container_layout = QVBoxLayout(self.select_all_widget)
        select_all_container_layout.setContentsMargins(0, 0, 0, 0)
        select_all_container_layout.addLayout(self.select_all_layout)
        
        table_layout.addWidget(self.select_all_widget)
        
        # Create content area that will switch between empty state and table
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create empty state widget
        self.empty_state_widget = self.create_empty_state_widget()
        content_layout.addWidget(self.empty_state_widget)
        content_layout.addWidget(self.file_table)
        
        table_layout.addWidget(content_area)
        
        # Initially hide the table and select all widget, show empty state
        self.file_table.hide()
        self.select_all_widget.hide()
        self.empty_state_widget.show()

        splitter.addWidget(self.tabs)
        splitter.addWidget(table_container)
        splitter.setSizes([160, 600])

        self.main_layout.addWidget(splitter)
        self.create_status_bar()

        # Setup keyboard shortcuts
        QShortcut(QKeySequence.Delete, self.file_table, self.remove_selected_files)
        QShortcut(QKeySequence.SelectAll, self.file_table, self.select_all_files)

    def create_toolbar(self):
        """Creates the main application toolbar."""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(28, 28))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar { padding: 8px; border: none; }
            QToolButton { padding: 10px; font-size: 14px; font-weight: bold; border-radius: 5px; }
            QToolButton:hover { background-color: #e8e8e8; }
        """)
        self.addToolBar(toolbar)
        style = self.style()

        def add_action(icon, text, callback, shortcut=None):
            action = QAction(icon, text, self)
            action.triggered.connect(callback)
            if shortcut:
                action.setShortcut(shortcut)
                action.setToolTip(f"{text} ({shortcut})")
            toolbar.addAction(action)
            return action

        # Add actions with shortcuts
        add_action(style.standardIcon(QStyle.SP_FileIcon), "添加文件", self.add_files, "Ctrl+O")
        add_action(style.standardIcon(QStyle.SP_DirIcon), "添加文件夹", self.add_folder, "Ctrl+Shift+O")
        toolbar.addSeparator()
        add_action(style.standardIcon(QStyle.SP_BrowserReload), "预览", self.preview_changes, "F5")
        add_action(style.standardIcon(QStyle.SP_DialogResetButton), "重置参数", self.reset_parameters, "Ctrl+R")
        toolbar.addSeparator()
        
        execute_action = QAction(style.standardIcon(QStyle.SP_DialogApplyButton), "执行", self)
        execute_action.triggered.connect(self.execute_rename)
        execute_action.setShortcut("Ctrl+Enter")
        execute_action.setToolTip("执行 (Ctrl+Enter)")
        toolbar.addAction(execute_action)
        if (button := toolbar.widgetForAction(execute_action)):
            button.setStyleSheet("font-weight: bold; color: green;")
        
        toolbar.addSeparator()
        
        self.undo_action = QAction(style.standardIcon(QStyle.SP_ArrowBack), "撤回", self)
        self.undo_action.triggered.connect(self.undo_last_operation)
        self.undo_action.setEnabled(False)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setToolTip("撤回 (Ctrl+Z)")
        toolbar.addAction(self.undo_action)
        if (button := toolbar.widgetForAction(self.undo_action)):
            button.setStyleSheet("font-weight: bold; color: red;")
        
        toolbar.addSeparator()
        add_action(style.standardIcon(QStyle.SP_TrashIcon), "清空列表", self.clear_file_list, "Ctrl+Delete")
        add_action(style.standardIcon(QStyle.SP_FileDialogDetailedView), "使用说明", self.show_help, "F1")

    def create_operation_tabs(self):
        """Creates and configures the QTabWidget for renaming operations."""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabBar::tab { font-size: 14px; font-weight: bold; padding: 10px 18px; }
            QTabWidget::pane { border: 1px solid #CCC; border-top: none; }
            QTabBar::tab:selected { background-color: #f0f0f0; border: 1px solid #999; border-bottom: none; }
        """)
        
        # --- Tab 1: Replace String ---
        replace_widget = QWidget(); replace_layout = QHBoxLayout(replace_widget)
        self.replace_from = QLineEdit(placeholderText="查找的字符串")
        self.replace_to = QLineEdit(placeholderText="替换为的字符串")
        # Add auto-preview listeners
        self.replace_from.textChanged.connect(self.start_preview_timer)
        self.replace_to.textChanged.connect(self.start_preview_timer)
        replace_layout.addWidget(QLabel("将:")); replace_layout.addWidget(self.replace_from)
        replace_layout.addWidget(QLabel("替换为:")); replace_layout.addWidget(self.replace_to)
        replace_layout.addStretch()
        tabs.addTab(replace_widget, "替换字符串")

        # --- Tab 2: Add Prefix/Suffix ---
        add_widget = QWidget(); add_layout = QHBoxLayout(add_widget)
        self.add_text = QLineEdit(placeholderText="要添加的文本")
        self.add_text.textChanged.connect(self.start_preview_timer)
        self.position_group = QButtonGroup()
        prefix_radio = QRadioButton("添加为前缀"); prefix_radio.setChecked(True)
        suffix_radio = QRadioButton("添加为后缀")
        self.position_group.addButton(prefix_radio, 0); self.position_group.addButton(suffix_radio, 1)
        self.position_group.buttonClicked.connect(self.start_preview_timer)
        add_layout.addWidget(prefix_radio); add_layout.addWidget(suffix_radio)
        add_layout.addWidget(self.add_text); add_layout.addStretch()
        tabs.addTab(add_widget, "添加前缀/后缀")

        # --- Tab 3: Add Sequential Numbers ---
        number_widget = QWidget(); number_layout = QVBoxLayout(number_widget)
        row1_layout = QHBoxLayout()
        self.number_position_group = QButtonGroup()
        num_prefix_radio = QRadioButton("前缀"); num_prefix_radio.setChecked(True)
        num_suffix_radio = QRadioButton("后缀")
        self.number_position_group.addButton(num_prefix_radio, 0); self.number_position_group.addButton(num_suffix_radio, 1)
        self.number_position_group.buttonClicked.connect(self.start_preview_timer)
        row1_layout.addWidget(QLabel("序号位置:")); row1_layout.addWidget(num_prefix_radio); row1_layout.addWidget(num_suffix_radio)
        row1_layout.addSpacing(20)
        self.separator_input = QLineEdit("_"); self.separator_input.setFixedWidth(50)
        self.separator_input.textChanged.connect(self.start_preview_timer)
        row1_layout.addWidget(QLabel("连接符:")); row1_layout.addWidget(self.separator_input)
        row1_layout.addStretch()
        
        row2_layout = QHBoxLayout()
        self.start_number = QLineEdit("1"); self.start_number.setFixedWidth(80)
        self.number_digits = QLineEdit("2"); self.number_digits.setFixedWidth(80)
        self.number_step = QLineEdit("1"); self.number_step.setFixedWidth(80)
        # Add auto-preview listeners
        self.start_number.textChanged.connect(self.start_preview_timer)
        self.number_digits.textChanged.connect(self.start_preview_timer)
        self.number_step.textChanged.connect(self.start_preview_timer)
        row2_layout.addWidget(QLabel("起始数字:")); row2_layout.addWidget(self.start_number)
        row2_layout.addSpacing(20)
        row2_layout.addWidget(QLabel("数字位数(不足补0):")); row2_layout.addWidget(self.number_digits)
        row2_layout.addSpacing(20)
        row2_layout.addWidget(QLabel("步长:")); row2_layout.addWidget(self.number_step)
        row2_layout.addStretch()
        
        number_layout.addLayout(row1_layout); number_layout.addLayout(row2_layout)
        tabs.addTab(number_widget, "批量添加序号")
        
        # --- Tab 4: Delete Characters ---
        delete_widget = QWidget(); delete_layout = QVBoxLayout(delete_widget)
        row1_layout = QHBoxLayout()
        self.delete_direction_group = QButtonGroup()
        left_radio = QRadioButton("从左开始"); left_radio.setChecked(True)
        right_radio = QRadioButton("从右开始")
        self.delete_direction_group.addButton(left_radio, 0); self.delete_direction_group.addButton(right_radio, 1)
        self.delete_direction_group.buttonClicked.connect(self.start_preview_timer)
        row1_layout.addWidget(QLabel("删除方向:")); row1_layout.addWidget(left_radio); row1_layout.addWidget(right_radio)
        row1_layout.addStretch()
        
        row2_layout = QHBoxLayout()
        self.delete_start_pos = QLineEdit("1"); self.delete_start_pos.setFixedWidth(80)
        self.delete_count = QLineEdit("1"); self.delete_count.setFixedWidth(80)
        self.delete_start_pos.textChanged.connect(self.start_preview_timer)
        self.delete_count.textChanged.connect(self.start_preview_timer)
        row2_layout.addWidget(QLabel("开始位置:")); row2_layout.addWidget(self.delete_start_pos)
        row2_layout.addSpacing(20)
        row2_layout.addWidget(QLabel("删除字符数:")); row2_layout.addWidget(self.delete_count)
        row2_layout.addStretch()
        
        delete_layout.addLayout(row1_layout); delete_layout.addLayout(row2_layout)
        tabs.addTab(delete_widget, "删除字符")
        return tabs

    def create_empty_state_widget(self):
        """Creates the empty state widget displayed when no files are loaded."""
        empty_widget = QWidget()
        empty_widget.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border: 2px dashed #dee2e6;
                border-radius: 10px;
            }
        """)
        
        empty_layout = QVBoxLayout(empty_widget)
        empty_layout.setAlignment(Qt.AlignCenter)
        
        # Large icon
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 80px; margin-bottom: 30px; border: none;")
        
        # Main message
        title_label = QLabel("拖拽文件或文件夹到此处")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 32px; font-weight: bold; color: #495057; margin-bottom: 15px; border: none;")
        
        # Subtitle
        subtitle_label = QLabel("或使用上方工具栏的\"添加文件\"、\"添加文件夹\"按钮")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 20px; color: #6c757d; margin-bottom: 25px; border: none;")
        
        # Tips
        tips_label = QLabel("💡 支持的快捷键：Ctrl+O (添加文件)、Ctrl+Shift+O (添加文件夹)")
        tips_label.setAlignment(Qt.AlignCenter)
        tips_label.setStyleSheet("font-size: 16px; color: #868e96; border: none;")
        
        empty_layout.addWidget(icon_label)
        empty_layout.addWidget(title_label)
        empty_layout.addWidget(subtitle_label)
        empty_layout.addWidget(tips_label)
        
        return empty_widget

    def create_file_table(self):
        """Creates the file table widget and its 'select all' checkbox layout."""
        select_all_layout = QHBoxLayout()
        self.header_checkbox = QCheckBox("全选/全不选"); self.header_checkbox.setChecked(False)
        self.header_checkbox.stateChanged.connect(lambda s: self.toggle_all_checkboxes(Qt.CheckState(s)))
        select_all_layout.addWidget(self.header_checkbox)
        
        # Add help tooltip icon
        help_label = QLabel("❓")
        help_label.setToolTip("只会操作选中的文件，如果一个都不选就处理全部文件")
        help_label.setStyleSheet("color: #666; font-size: 16px; margin-left: 5px;")
        select_all_layout.addWidget(help_label)
        select_all_layout.addStretch()
        
        # Updated table structure: "", "当前文件名", "预览", "执行结果", "最后更新时间", "文件大小", "路径"
        table = QTableWidget(columnCount=7)
        table.setHorizontalHeaderLabels(["", "当前文件名", "预览", "执行结果", "最后更新时间", "文件大小", "路径"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        # Connect table item click handler
        table.itemClicked.connect(self.table_item_clicked)
        
        header = table.horizontalHeader()
        resize_modes = [
            QHeaderView.ResizeToContents,  # 选择框
            QHeaderView.Stretch,           # 当前文件名
            QHeaderView.Stretch,           # 预览
            QHeaderView.ResizeToContents,  # 执行结果
            QHeaderView.ResizeToContents,  # 最后更新时间
            QHeaderView.ResizeToContents,  # 文件大小
            QHeaderView.Stretch            # 路径
        ]
        for i, size_mode in enumerate(resize_modes):
            header.setSectionResizeMode(i, size_mode)
        
        return table, select_all_layout

    def create_status_bar(self):
        """Creates the application's status bar."""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        status_bar.addPermanentWidget(QLabel(f"作者:lizeyu  v{self.version} @版权所有"))
    
    # ----------------------------------------------------------------------
    # Event Handling Methods
    # ----------------------------------------------------------------------

    def dragEnterEvent(self, event):
        """Handles drag enter events to accept file URLs."""
        if event.mimeData().hasUrls(): event.acceptProposedAction()

    def dropEvent(self, event):
        """Handles drop events to add files and folders."""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = Path(url.toLocalFile())
                if path.is_file(): self.add_file_to_table(str(path))
                elif path.is_dir():
                    for item in path.iterdir():
                        if item.is_file(): self.add_file_to_table(str(item))
        self.update_status("通过拖拽添加了文件。")

    def show_table_context_menu(self, position):
        """Shows a context menu for the file table."""
        menu = QMenu()
        
        # Get the clicked row
        clicked_item = self.file_table.itemAt(position)
        if clicked_item:
            row = clicked_item.row()
            
            # Add context menu actions
            rename_action = menu.addAction("重命名文件")
            open_folder_action = menu.addAction("打开文件所在文件夹")
            menu.addSeparator()
            remove_action = menu.addAction("从列表中移除")
            
            action = menu.exec_(self.file_table.mapToGlobal(position))
            
            if action == rename_action:
                self.rename_single_file(row)
            elif action == open_folder_action:
                self.open_file_folder(row)
            elif action == remove_action:
                self.remove_selected_files()
        else:
            # No item clicked, show general menu
            remove_action = menu.addAction("从列表中移除选中项")
            if menu.exec_(self.file_table.mapToGlobal(position)) == remove_action:
                self.remove_selected_files()

    # ----------------------------------------------------------------------
    # Core Slots (Actions Triggered by UI)
    # ----------------------------------------------------------------------

    def add_files(self):
        """Opens a dialog to add multiple files."""
        if files_paths := QFileDialog.getOpenFileNames(self, "选择文件")[0]:
            for path in files_paths: self.add_file_to_table(path)
            self.update_status(f"添加了 {len(files_paths)} 个文件。")

    def add_folder(self):
        """Opens a dialog to add a folder's contents."""
        if folder_path := QFileDialog.getExistingDirectory(self, "选择文件夹"):
            paths = [str(item) for item in Path(folder_path).iterdir() if item.is_file()]
            for path in paths: self.add_file_to_table(path)
            self.update_status(f"从文件夹添加了 {len(paths)} 个文件。")

    def clear_file_list(self):
        """Clears all files from the list."""
        self.file_table.setRowCount(0)
        self.files_data.clear()
        self.history.clear()
        self.undo_action.setEnabled(False)
        
        # Show empty state and hide table and select all widget
        self.file_table.hide()
        self.select_all_widget.hide()
        self.empty_state_widget.show()
        
        self.update_status("文件列表已清空。")

    def remove_selected_files(self):
        """Removes selected files from the list."""
        selected_rows = sorted({idx.row() for idx in self.file_table.selectedIndexes()}, reverse=True)
        if not selected_rows: return

        for row in selected_rows:
            del self.files_data[row]
            self.file_table.removeRow(row)
        
        # Show empty state and hide table and select all widget if no files left
        if len(self.files_data) == 0:
            self.file_table.hide()
            self.select_all_widget.hide()
            self.empty_state_widget.show()
            
        self.update_status(f"移除了 {len(selected_rows)} 个文件。")

    def start_preview_timer(self):
        """Starts the 0.3 second delay timer for auto-preview."""
        self.preview_timer.stop()  # Stop any existing timer
        self.preview_timer.start(300)  # Start 300ms timer

    def auto_preview_changes(self):
        """Automatically generates previews when called by timer."""
        if self.file_table.rowCount() > 0:
            self.preview_changes()

    def reset_parameters(self):
        """Resets all operation parameters to their default values."""
        # Reset Replace tab
        self.replace_from.clear()
        self.replace_to.clear()
        
        # Reset Add Prefix/Suffix tab
        self.add_text.clear()
        self.position_group.button(0).setChecked(True)  # Set to prefix
        
        # Reset Add Number tab
        self.start_number.setText("1")
        self.number_digits.setText("2")
        self.number_step.setText("1")
        self.separator_input.setText("_")
        self.number_position_group.button(0).setChecked(True)  # Set to prefix
        
        # Reset Delete Characters tab
        self.delete_start_pos.setText("1")
        self.delete_count.setText("1")
        self.delete_direction_group.button(0).setChecked(True)  # Set to from left
        
        # Switch to the first tab
        self.tabs.setCurrentIndex(0)
        
        # Clear all previews and reset to show original filenames
        for row in range(self.file_table.rowCount()):
            original_name = self.files_data[row]["path_obj"].name
            preview_item = QTableWidgetItem(original_name)
            preview_item.setForeground(QColor("black"))
            self.file_table.setItem(row, 2, preview_item)
            self.files_data[row]['preview_name'] = ""
            
            # Clear result column (now at column 3)
            result_item = self.file_table.item(row, 3)
            if result_item:
                result_item.setText("")
        
        self.update_status("已重置所有参数到默认值。")

    def preview_changes(self):
        """Generates and displays filename previews based on current operation."""
        params = self._get_operation_params()
        if not params: return

        rows_to_process = self.get_rows_to_process()
        
        # First, clear all previous previews from the UI and data model
        for row in range(self.file_table.rowCount()):
            self.file_table.setItem(row, 2, QTableWidgetItem(""))
            # Safely clear the result column (now at column 3)
            result_item = self.file_table.item(row, 3)
            if result_item:
                result_item.setText("")
            else:
                self.file_table.setItem(row, 3, QTableWidgetItem(""))
            self.files_data[row]['preview_name'] = ""

        # Generate previews for ALL rows that need processing
        for i, row in enumerate(rows_to_process):
            file_info = self.files_data[row]
            path_obj = file_info["path_obj"]
            original_name = path_obj.name
            
            # Get the real stem (filename without the last extension only)
            # This handles files with multiple dots correctly
            if '.' in original_name:
                original_stem = original_name.rsplit('.', 1)[0]  # Split from the right, only once
                file_suffix = '.' + original_name.rsplit('.', 1)[1]
            else:
                original_stem = original_name
                file_suffix = ''
            
            # Calculate the new stem using the operation parameters
            new_stem = self._calculate_new_stem(original_stem, params, i)
            
            # Always show a preview for processed files
            if new_stem and new_stem != original_stem:
                # File will be changed - show new name in red
                final_name = new_stem + file_suffix
                file_info["preview_name"] = final_name
                
                preview_item = QTableWidgetItem(final_name)
                preview_item.setForeground(QColor("red"))
                self.file_table.setItem(row, 2, preview_item)
            else:
                # File will not be changed - show original name in normal color
                file_info["preview_name"] = ""  # No change, so no preview_name for execution
                
                preview_item = QTableWidgetItem(original_name)
                preview_item.setForeground(QColor("black"))  # Normal color
                self.file_table.setItem(row, 2, preview_item)
        
        changed_count = sum(1 for row in rows_to_process if self.files_data[row]["preview_name"])
        self.update_status(f"已为 {len(rows_to_process)} 个文件生成预览，其中 {changed_count} 个将被重命名。")

    def execute_rename(self):
        """Executes the file renaming operation for rows with a valid preview."""
        rows_to_rename = [row for row in self.get_rows_to_process() if self.files_data[row]["preview_name"]]
        if not rows_to_rename:
            QMessageBox.information(self, "无操作", "没有可供重命名的文件。请先生成预览。")
            return
        
        if QMessageBox.question(self, "确认操作", f"即将重命名 {len(rows_to_rename)} 个文件。是否继续？",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            self.update_status("重命名操作已取消。")
            return

        current_batch_history, success, fail = [], 0, 0
        for row in rows_to_rename:
            file_data = self.files_data[row]
            old_path = file_data["path_obj"]
            new_path = old_path.with_name(file_data["preview_name"])

            try:
                if new_path.exists(): raise OSError("目标文件名已存在")
                os.rename(old_path, new_path)
                
                current_batch_history.append((str(old_path), str(new_path)))
                file_data.update(path_obj=new_path, original_name=new_path.name, preview_name="")
                
                self.file_table.item(row, 1).setText(new_path.name)
                self.file_table.item(row, 2).setText("")
                self.file_table.setItem(row, 3, QTableWidgetItem("✅ 成功"))
                success += 1
            except OSError as e:
                self.file_table.setItem(row, 3, QTableWidgetItem(f"❌ 失败: {e}"))
                fail += 1
        
        if current_batch_history:
            self.history.append(current_batch_history)
            self.undo_action.setEnabled(True)
        self.update_status(f"重命名完成：{success} 成功，{fail} 失败。")

    def undo_last_operation(self):
        """Reverts the last renaming operation."""
        if not self.history: return
        
        last_batch = self.history[-1]
        if QMessageBox.question(self, "确认撤回", f"即将撤回 {len(last_batch)} 个文件的命名。是否继续？",
                                QMessageBox.Yes | QMessageBox.No, QMessageBox.No) == QMessageBox.No:
            self.update_status("撤回操作已取消。")
            return

        self.history.pop()
        success, fail = 0, 0
        for old_path_str, new_path_str in reversed(last_batch):
            try:
                os.rename(new_path_str, old_path_str)
                # Find the corresponding file in files_data and update it
                for file_data in self.files_data:
                    if str(file_data["path_obj"]) == new_path_str:
                        file_data.update(path_obj=Path(old_path_str), original_name=Path(old_path_str).name, preview_name="")
                        break
                success += 1
            except OSError: fail += 1
        
        self.refresh_table_display()
        self.undo_action.setEnabled(bool(self.history))
        self.update_status(f"撤回完成：{success} 成功，{fail} 失败。")

    # ----------------------------------------------------------------------
    # Helper & Utility Methods
    # ----------------------------------------------------------------------

    def _get_operation_params(self):
        """Extracts and returns parameters from the current UI tab."""
        params = {"type": None}
        current_tab_index = self.tabs.currentIndex()
        if current_tab_index == 0:
            params.update(type="replace", from_str=self.replace_from.text(), to_str=self.replace_to.text())
        elif current_tab_index == 1:
            params.update(type="add", text=self.add_text.text(), is_prefix=self.position_group.checkedId() == 0)
        elif current_tab_index == 2:
            try:
                params.update(
                    type="number", start=int(self.start_number.text()), digits=int(self.number_digits.text()),
                    step=int(self.number_step.text()), separator=self.separator_input.text(),
                    is_prefix=self.number_position_group.checkedId() == 0)
            except ValueError:
                QMessageBox.warning(self, "输入错误", "序号设置中的数字、位数、步长必须为有效整数。")
                return None
        elif current_tab_index == 3:
            try:
                params.update(
                    type="delete", start_pos=int(self.delete_start_pos.text()), 
                    count=int(self.delete_count.text()),
                    from_left=self.delete_direction_group.checkedId() == 0)
            except ValueError:
                QMessageBox.warning(self, "输入错误", "删除设置中的开始位置和删除字符数必须为有效整数。")
                return None
        return params

    def _calculate_new_stem(self, original_stem, params, index):
        """Calculates a new filename stem based on operation parameters."""
        op_type = params.get("type")
        
        if op_type == "replace":
            from_str = params.get("from_str", "")
            to_str = params.get("to_str", "")
            # Only perform replacement if from_str is not empty and exists in the filename
            if from_str and from_str in original_stem:
                return original_stem.replace(from_str, to_str)
            else:
                return original_stem  # No change if from_str is empty or not found
                
        elif op_type == "add":
            text = params.get("text", "")
            # Only add prefix/suffix if text is not empty
            if text:
                if params.get("is_prefix"):
                    return f"{text}{original_stem}"
                else:
                    return f"{original_stem}{text}"
            else:
                return original_stem  # No change if text is empty
                
        elif op_type == "number":
            # Number operation always applies (assuming valid parameters)
            num_str = f"{params['start'] + (index * params['step']):0{params['digits']}d}"
            separator = params.get("separator", "_")
            if params.get("is_prefix"):
                return f"{num_str}{separator}{original_stem}"
            else:
                return f"{original_stem}{separator}{num_str}"
                
        elif op_type == "delete":
            # Delete characters from the specified position
            start_pos = params.get("start_pos", 1)
            count = params.get("count", 1)
            from_left = params.get("from_left", True)
            
            if start_pos < 1 or count < 1:
                return original_stem  # Invalid parameters, no change
            
            stem_length = len(original_stem)
            if stem_length == 0:
                return original_stem  # Empty string, no change
            
            if from_left:
                # Delete from left: convert 1-based to 0-based index
                start_index = start_pos - 1
                if start_index >= stem_length:
                    return original_stem  # Start position beyond string length
                end_index = min(start_index + count, stem_length)
                return original_stem[:start_index] + original_stem[end_index:]
            else:
                # Delete from right: convert 1-based to 0-based index from the end
                start_index = stem_length - start_pos
                if start_index < 0:
                    return original_stem  # Start position beyond string length
                end_index = max(start_index - count + 1, 0)
                return original_stem[:end_index] + original_stem[start_index + 1:]
        
        # Default: return original stem unchanged
        return original_stem

    def add_file_to_table(self, file_path):
        """Adds a file to the internal data list and the UI table."""
        path_obj = Path(file_path)
        if path_obj.resolve() in (item['path_obj'].resolve() for item in self.files_data): return

        # Show table and select all widget, hide empty state if this is the first file
        if len(self.files_data) == 0:
            self.empty_state_widget.hide()
            self.file_table.show()
            self.select_all_widget.show()

        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        self.files_data.append({"path_obj": path_obj, "preview_name": "", "original_name": path_obj.name})

        # Get file stats
        file_stat = path_obj.stat()
        
        # Create table items
        chk_box = QTableWidgetItem()
        chk_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
        chk_box.setCheckState(Qt.Unchecked)
        
        # Set default preview to show original filename in normal color
        preview_item = QTableWidgetItem(path_obj.name)
        preview_item.setForeground(QColor("black"))
        
        # Format last modified time
        last_modified = QDateTime.fromSecsSinceEpoch(int(file_stat.st_mtime)).toString("yyyy-MM-dd hh:mm:ss")
        time_item = QTableWidgetItem(last_modified)
        time_item.setTextAlignment(Qt.AlignCenter)
        
        # Format file size
        size_item = QTableWidgetItem(self.format_file_size(file_stat.st_size))
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # Create clickable path item
        path_item = QTableWidgetItem(str(path_obj.parent))
        path_item.setForeground(QColor("blue"))
        path_item.setToolTip("点击打开文件夹")
        
        # Set items to table: "", "当前文件名", "预览", "执行结果", "最后更新时间", "文件大小", "路径"
        self.file_table.setItem(row, 0, chk_box)                                    # 选择框
        self.file_table.setItem(row, 1, QTableWidgetItem(path_obj.name))          # 当前文件名
        self.file_table.setItem(row, 2, preview_item)                             # 预览
        self.file_table.setItem(row, 3, QTableWidgetItem(""))                     # 执行结果
        self.file_table.setItem(row, 4, time_item)                                # 最后更新时间
        self.file_table.setItem(row, 5, size_item)                                # 文件大小
        self.file_table.setItem(row, 6, path_item)                                # 路径

    def get_rows_to_process(self):
        """Returns a list of row indices to be processed (checked, or all if none checked)."""
        checked_rows = [i for i in range(self.file_table.rowCount()) if self.file_table.item(i, 0).checkState() == Qt.Checked]
        return checked_rows if checked_rows else range(self.file_table.rowCount())

    def refresh_table_display(self):
        """Fully re-populates the table from the files_data list. Used after undo."""
        temp_data = list(self.files_data)
        self.clear_file_list() # This also clears history, which might be undesirable. Let's do it manually.
        self.file_table.setRowCount(0)
        self.files_data.clear()
        
        for item in temp_data: self.add_file_to_table(str(item["path_obj"]))

    def toggle_all_checkboxes(self, state):
        """Toggles the checked state of all file items in the table."""
        for i in range(self.file_table.rowCount()):
            if item := self.file_table.item(i, 0): item.setCheckState(state)

    def update_status(self, message):
        """Shows a temporary message in the status bar."""
        self.statusBar().showMessage(message, 5000)

    def show_help(self):
        """Shows the help documentation."""
        help_file_path = Path("使用说明.txt")
        
        # Create help file if it doesn't exist
        if not help_file_path.exists():
            help_content = """批量文件重命名工具 - 使用说明

=== 主要功能 ===

1. 【字符串替换】
   - 将文件名中的指定文本替换为新文本
   - 支持空字符替换（删除文本）
   - 只替换匹配的字符串

2. 【添加前缀/后缀】
   - 在文件名前或后添加指定文本
   - 可选择前缀或后缀位置

3. 【批量添加序号】
   - 为文件添加递增序号
   - 可设置起始数字、位数、步长
   - 可选择前缀或后缀位置
   - 可自定义分隔符

4. 【删除字符】
   - 从指定位置删除指定数量的字符
   - 支持从左或从右开始删除
   - 可设置开始位置和删除字符数

=== 快捷键 ===

Ctrl+O        - 添加文件
Ctrl+Shift+O  - 添加文件夹
F5            - 预览更改
Ctrl+R        - 重置参数
Ctrl+Enter    - 执行重命名
Ctrl+Z        - 撤回操作
Ctrl+Delete   - 清空列表
F1            - 显示此帮助
Ctrl+A        - 选中所有文件
Delete        - 移除选中的文件

=== 操作说明 ===

1. 添加文件：使用"添加文件"或"添加文件夹"按钮，或直接拖拽文件到窗口
2. 选择操作：在上方标签页中选择重命名方式
3. 设置参数：根据选择的操作设置相关参数
4. 预览更改：红色文件名表示将被更改，黑色表示不变
5. 选择文件：勾选要处理的文件，不选择任何文件将处理全部
6. 执行操作：点击"执行"按钮进行重命名
7. 撤回操作：如需撤回，点击"撤回"按钮

=== 右键菜单 ===

在文件列表中右键点击可以：
- 重命名文件：直接编辑单个文件名
- 打开文件所在文件夹：在资源管理器中打开
- 从列表中移除：移除不需要的文件

=== 表格功能 ===

- 点击列标题可以排序
- 点击蓝色路径可以打开文件夹
- 执行结果显示操作成功/失败状态
- 显示文件最后更新时间和大小

=== 安全提示 ===

- 重命名前会显示预览
- 支持撤回最近的操作
- 同名文件会显示错误提示
- 只处理选中的文件，提高安全性

版本：v2.0.0
作者：lizeyu
"""
            try:
                with open(help_file_path, 'w', encoding='utf-8') as f:
                    f.write(help_content)
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法创建帮助文件：{e}")
                return
        
        # Open help file
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(help_file_path.absolute())))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开帮助文件：{e}")

    def select_all_files(self):
        """Selects all files in the table."""
        for row in range(self.file_table.rowCount()):
            checkbox_item = self.file_table.item(row, 0)
            if checkbox_item:
                checkbox_item.setCheckState(Qt.Checked)
        self.update_status("已选中所有文件。")

    def rename_single_file(self, row):
        """Renames a single file through a dialog."""
        if row >= len(self.files_data):
            return
            
        file_data = self.files_data[row]
        old_path = file_data["path_obj"]
        old_name = old_path.name
        
        new_name, ok = QInputDialog.getText(self, "重命名文件", f"新文件名:", text=old_name)
        if not ok or not new_name.strip() or new_name == old_name:
            return
            
        new_path = old_path.with_name(new_name.strip())
        
        try:
            if new_path.exists():
                QMessageBox.warning(self, "错误", "目标文件名已存在！")
                return
                
            os.rename(old_path, new_path)
            
            # Update data
            file_data.update(path_obj=new_path, original_name=new_path.name, preview_name="")
            
            # Update table display
            self.file_table.item(row, 1).setText(new_path.name)
            self.file_table.item(row, 2).setText("")
            self.file_table.setItem(row, 3, QTableWidgetItem("✅ 重命名成功"))
            
            # Add to history for undo
            self.history.append([(str(old_path), str(new_path))])
            self.undo_action.setEnabled(True)
            
            self.update_status(f"文件 '{old_name}' 已重命名为 '{new_name}'。")
            
        except OSError as e:
            QMessageBox.warning(self, "错误", f"重命名失败：{e}")

    def open_file_folder(self, row):
        """Opens the folder containing the file."""
        if row >= len(self.files_data):
            return
            
        file_path = self.files_data[row]["path_obj"]
        folder_path = file_path.parent
        
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件夹：{e}")

    def table_item_clicked(self, item):
        """Handles table item click events."""
        row = item.row()
        column = item.column()
        
        # If clicked on path column (column 6), open the folder
        if column == 6:
            self.open_file_folder(row)

    @staticmethod
    def format_file_size(size_bytes):
        """Formats a file size in bytes into a human-readable string (KB, MB, etc.)."""
        if size_bytes == 0: return "0 B"
        size_name = ("B", "KB", "MB", "GB", "TB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_name[i]}"


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileRenamer()
    window.show()
    sys.exit(app.exec_())
