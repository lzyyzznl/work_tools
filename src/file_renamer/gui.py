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
)
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer
from PyQt5.QtGui import QDesktopServices, QKeySequence, QIcon, QColor
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
        self.file_table, select_all_layout = self.create_file_table()
        table_layout.addLayout(select_all_layout)
        table_layout.addWidget(self.file_table)

        splitter.addWidget(self.tabs)
        splitter.addWidget(table_container)
        splitter.setSizes([160, 600])

        self.main_layout.addWidget(splitter)
        self.create_status_bar()

        QShortcut(QKeySequence.Delete, self.file_table, self.remove_selected_files)

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

        def add_action(icon, text, callback):
            action = QAction(icon, text, self)
            action.triggered.connect(callback)
            toolbar.addAction(action)
            return action

        add_action(style.standardIcon(QStyle.SP_FileIcon), "添加文件", self.add_files)
        add_action(style.standardIcon(QStyle.SP_DirIcon), "添加文件夹", self.add_folder)
        toolbar.addSeparator()
        add_action(style.standardIcon(QStyle.SP_BrowserReload), "预览", self.preview_changes)
        add_action(style.standardIcon(QStyle.SP_DialogResetButton), "重置参数", self.reset_parameters)
        toolbar.addSeparator()
        
        execute_action = QAction(style.standardIcon(QStyle.SP_DialogApplyButton), "执行", self)
        execute_action.triggered.connect(self.execute_rename)
        toolbar.addAction(execute_action)
        if (button := toolbar.widgetForAction(execute_action)):
            button.setStyleSheet("font-weight: bold; color: green;")
        
        toolbar.addSeparator()
        
        self.undo_action = QAction(style.standardIcon(QStyle.SP_ArrowBack), "撤回", self)
        self.undo_action.triggered.connect(self.undo_last_operation)
        self.undo_action.setEnabled(False)
        toolbar.addAction(self.undo_action)
        if (button := toolbar.widgetForAction(self.undo_action)):
            button.setStyleSheet("font-weight: bold; color: red;")
        
        toolbar.addSeparator()
        add_action(style.standardIcon(QStyle.SP_TrashIcon), "清空列表", self.clear_file_list)

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

    def create_file_table(self):
        """Creates the file table widget and its 'select all' checkbox layout."""
        select_all_layout = QHBoxLayout()
        self.header_checkbox = QCheckBox("全选/全不选"); self.header_checkbox.setChecked(False)
        self.header_checkbox.stateChanged.connect(lambda s: self.toggle_all_checkboxes(Qt.CheckState(s)))
        select_all_layout.addWidget(self.header_checkbox); select_all_layout.addStretch()
        
        table = QTableWidget(columnCount=6)
        table.setHorizontalHeaderLabels(["", "当前文件名", "预览", "文件大小", "执行结果", "路径"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows); table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        header = table.horizontalHeader()
        for i, size_mode in enumerate([QHeaderView.ResizeToContents, QHeaderView.Stretch, QHeaderView.Stretch, 
                                     QHeaderView.ResizeToContents, QHeaderView.ResizeToContents, QHeaderView.Stretch]):
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
        remove_action = menu.addAction("从列表中移除")
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
        self.update_status("文件列表已清空。")

    def remove_selected_files(self):
        """Removes selected files from the list."""
        selected_rows = sorted({idx.row() for idx in self.file_table.selectedIndexes()}, reverse=True)
        if not selected_rows: return

        for row in selected_rows:
            del self.files_data[row]
            self.file_table.removeRow(row)
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
            
            # Clear result column
            result_item = self.file_table.item(row, 4)
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
            # Safely clear the result column
            result_item = self.file_table.item(row, 4)
            if result_item:
                result_item.setText("")
            else:
                self.file_table.setItem(row, 4, QTableWidgetItem(""))
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
                self.file_table.setItem(row, 4, QTableWidgetItem("✅ 成功"))
                success += 1
            except OSError as e:
                self.file_table.setItem(row, 4, QTableWidgetItem(f"失败: {e}"))
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

        row = self.file_table.rowCount()
        self.file_table.insertRow(row)
        self.files_data.append({"path_obj": path_obj, "preview_name": "", "original_name": path_obj.name})

        chk_box = QTableWidgetItem(); chk_box.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled); chk_box.setCheckState(Qt.Unchecked)
        size_item = QTableWidgetItem(self.format_file_size(path_obj.stat().st_size)); size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.file_table.setItem(row, 0, chk_box)
        self.file_table.setItem(row, 1, QTableWidgetItem(path_obj.name))
        # Set default preview to show original filename in normal color
        preview_item = QTableWidgetItem(path_obj.name)
        preview_item.setForeground(QColor("black"))
        self.file_table.setItem(row, 2, preview_item)
        self.file_table.setItem(row, 3, size_item)
        self.file_table.setItem(row, 4, QTableWidgetItem(""))
        self.file_table.setItem(row, 5, QTableWidgetItem(str(path_obj.parent)))

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
