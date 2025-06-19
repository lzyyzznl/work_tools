from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLineEdit, QComboBox, QLabel, QMessageBox, QHeaderView,
    QMenu, QInputDialog, QFormLayout, QDialogButtonBox, QGroupBox,
    QScrollArea, QWidget, QSplitter
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QCursor
import sys
import os
from rule_manager import RuleManager


class RuleEditDialog(QDialog):
    """规则编辑对话框"""
    
    def __init__(self, parent=None, rule_data=None, rule_manager=None):
        super().__init__(parent)
        self.rule_manager = rule_manager
        self.rule_data = rule_data or {}
        self.match_rule_widgets = []  # 改为列表存储匹配规则控件
        self.is_editing = rule_data is not None
        
        self.setWindowTitle("编辑规则" if rule_data else "添加规则")
        self.setModal(True)
        # 设置窗口标志：对话框，带有标题栏、系统菜单、最小化和关闭按钮，但不显示帮助按钮
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.setup_ui()
        self.setup_apple_style()
        
        if rule_data:
            self.load_rule_data()
        else:
            # 只有新增时才添加默认的匹配规则
            self.add_match_rule_widget()
    
    def setup_ui(self):
        """设置界面"""
        self.setFixedSize(600, 500)
        layout = QVBoxLayout(self)
        
        # 基本信息组
        basic_group = QGroupBox("基本信息")
        basic_layout = QFormLayout(basic_group)
        
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("输入代码，如：01.33.06.01")
        basic_layout.addRow("Code:", self.code_edit)
        
        self.thirty_d_combo = QComboBox()
        self.thirty_d_combo.addItems(["Y", "N"])
        basic_layout.addRow("30d:", self.thirty_d_combo)
        
        layout.addWidget(basic_group)
        
        # 匹配规则组
        rules_group = QGroupBox("匹配规则")
        rules_layout = QVBoxLayout(rules_group)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        self.rules_form_layout = QFormLayout(scroll_widget)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        rules_layout.addWidget(scroll_area)
        
        # 添加规则按钮
        add_rule_btn = QPushButton("➕ 添加更多匹配规则")
        add_rule_btn.clicked.connect(self.add_new_match_rule)
        rules_layout.addWidget(add_rule_btn)
        
        layout.addWidget(rules_group)
        
        # 按钮组
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        button_box.accepted.connect(self.accept_rule)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def add_match_rule_widget(self, value=""):
        """添加匹配规则输入控件"""
        rule_widget = QWidget()
        rule_layout = QHBoxLayout(rule_widget)
        rule_layout.setContentsMargins(0, 0, 0, 0)
        
        rule_edit = QLineEdit()
        rule_edit.setText(value)
        rule_edit.setPlaceholderText("输入匹配关键字")
        
        remove_btn = QPushButton("🗑")
        remove_btn.setFixedSize(30, 30)
        remove_btn.clicked.connect(lambda widget=rule_widget, edit=rule_edit: self.remove_match_rule(widget, edit))
        
        rule_layout.addWidget(rule_edit)
        rule_layout.addWidget(remove_btn)
        
        self.match_rule_widgets.append(rule_edit)
        self.rules_form_layout.addRow(f"匹配规则 {len(self.match_rule_widgets)}:", rule_widget)
    
    def add_new_match_rule(self):
        """添加新的匹配规则"""
        self.add_match_rule_widget()
    
    def remove_match_rule(self, widget, edit):
        """移除匹配规则"""
        if edit in self.match_rule_widgets:
            # 从列表中移除
            self.match_rule_widgets.remove(edit)
            
            # 找到并移除对应的行
            for i in range(self.rules_form_layout.rowCount()):
                field_item = self.rules_form_layout.itemAt(i, QFormLayout.FieldRole)
                if field_item and field_item.widget() == widget:
                    self.rules_form_layout.removeRow(i)
                    break
            
            # 更新标签
            self.update_rule_labels()
    
    def update_rule_labels(self):
        """更新规则标签"""
        for i in range(self.rules_form_layout.rowCount()):
            label_item = self.rules_form_layout.itemAt(i, QFormLayout.LabelRole)
            if label_item and label_item.widget():
                label_item.widget().setText(f"匹配规则 {i + 1}:")

    def load_rule_data(self):
        """加载规则数据到界面"""
        self.code_edit.setText(str(self.rule_data.get('code', '')))
        thirty_d = str(self.rule_data.get('30d', 'N'))
        index = self.thirty_d_combo.findText(thirty_d)
        if index >= 0:
            self.thirty_d_combo.setCurrentIndex(index)
        
        # 清除现有的匹配规则控件
        self.match_rule_widgets.clear()
        # 清除表单中的所有行
        while self.rules_form_layout.rowCount() > 0:
            self.rules_form_layout.removeRow(0)
        
        # 加载匹配规则
        match_rules = self.rule_data.get('match_rules', [])
        if match_rules:
            for rule_value in match_rules:
                if rule_value and str(rule_value).strip():
                    self.add_match_rule_widget(str(rule_value).strip())
        
        # 如果没有匹配规则，至少添加一个空的
        if not self.match_rule_widgets:
            self.add_match_rule_widget()
    
    def accept_rule(self):
        """确认规则"""
        code = self.code_edit.text().strip()
        if not code:
            QMessageBox.warning(self, "警告", "请输入Code")
            return
        
        thirty_d = self.thirty_d_combo.currentText()
        
        # 收集匹配规则
        match_rules = []
        for widget in self.match_rule_widgets:
            value = widget.text().strip()
            if value:  # 只保存非空的规则
                match_rules.append(value)
        
        if not match_rules:
            QMessageBox.warning(self, "警告", "请至少输入一个匹配规则")
            return
        
        self.result_data = {
            'code': code,
            '30d': thirty_d,
            'match_rules': match_rules
        }
        
        self.accept()
    
    def setup_apple_style(self):
        """设置苹果风格样式"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(255, 255, 255, 1.0));
                border-radius: 12px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QGroupBox {
                font-weight: 600;
                font-size: 16px;
                color: #1d1d1f;
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
            }
            QLineEdit {
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                color: #1d1d1f;
                min-height: 20px;
            }
            QLineEdit:focus {
                border: 3px solid #007AFF;
                background: rgba(255, 255, 255, 1.0);
            }
            QComboBox {
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                color: #1d1d1f;
                min-height: 20px;
                min-width: 80px;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 122, 255, 1.0),
                    stop:1 rgba(0, 100, 220, 1.0));
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 1.0),
                    stop:1 rgba(0, 122, 255, 1.0));
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 100, 220, 1.0),
                    stop:1 rgba(0, 80, 200, 1.0));
            }
        """)


class RuleSettingsDialog(QDialog):
    """规则设置主对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rule_manager = RuleManager()
        self.setWindowTitle("匹配规则设置")
        self.setModal(True)
        # 设置窗口标志：对话框，带有标题栏、系统菜单、最小化和关闭按钮，但不显示帮助按钮
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint | Qt.WindowSystemMenuHint | 
                           Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint)
        self.resize(800, 600)
        
        self.setup_ui()
        self.setup_apple_style()
        self.load_rules()
    
    def setup_ui(self):
        """设置界面"""
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ 添加规则")
        add_btn.clicked.connect(self.add_rule)
        toolbar_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ 编辑规则")
        edit_btn.clicked.connect(self.edit_rule)
        toolbar_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑 删除规则")
        delete_btn.clicked.connect(self.delete_rule)
        toolbar_layout.addWidget(delete_btn)
        
        reset_btn = QPushButton("🔄 重置规则")
        reset_btn.clicked.connect(self.reset_rules)
        toolbar_layout.addWidget(reset_btn)
        
        toolbar_layout.addStretch()
        
        # 搜索框
        search_label = QLabel("搜索:")
        toolbar_layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入关键字搜索...")
        self.search_edit.textChanged.connect(self.filter_table)
        self.search_edit.setFixedWidth(200)
        toolbar_layout.addWidget(self.search_edit)
        
        layout.addLayout(toolbar_layout)
        
        # 规则表格
        self.rules_table = QTableWidget()
        self.rules_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rules_table.customContextMenuRequested.connect(self.show_context_menu)
        self.rules_table.itemDoubleClicked.connect(self.edit_rule)
        self.rules_table.setSortingEnabled(True)  # 启用排序
        
        layout.addWidget(self.rules_table)
        
        # 按钮组
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def setup_apple_style(self):
        """设置苹果风格样式"""
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(255, 255, 255, 1.0));
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QTableWidget {
                background: white;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                font-size: 14px;
                gridline-color: rgba(0, 0, 0, 0.1);
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(240, 240, 240, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 4px;
                padding: 8px;
                font-weight: 600;
                color: #1d1d1f;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 122, 255, 1.0),
                    stop:1 rgba(0, 100, 220, 1.0));
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(30, 144, 255, 1.0),
                    stop:1 rgba(0, 122, 255, 1.0));
            }
        """)
    
    def load_rules(self):
        """加载规则到表格"""
        self.rule_manager.load_rules()
        rules = self.rule_manager.get_all_rules()
        
        # 设置表格列
        self.rules_table.setColumnCount(3)
        self.rules_table.setHorizontalHeaderLabels(["Code", "30d", "匹配规则"])
        
        if not rules:
            self.rules_table.setRowCount(0)
            return
        
        # 设置表格行数
        self.rules_table.setRowCount(len(rules))
        
        # 填充数据
        for row, rule in enumerate(rules):
            # Code列
            self.rules_table.setItem(row, 0, QTableWidgetItem(str(rule.get('code', ''))))
            # 30d列
            self.rules_table.setItem(row, 1, QTableWidgetItem(str(rule.get('30d', ''))))
            
            # 合并所有匹配规则到一列，用|分割
            match_rules = rule.get('match_rules', [])
            combined_rules = ' | '.join(match_rules) if match_rules else ''
            self.rules_table.setItem(row, 2, QTableWidgetItem(combined_rules))
        
        # 调整列宽
        self.rules_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.rules_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
    
    def filter_table(self, text):
        """根据搜索文本过滤表格"""
        text = text.lower()
        for row in range(self.rules_table.rowCount()):
            show_row = False
            for col in range(self.rules_table.columnCount()):
                item = self.rules_table.item(row, col)
                if item and text in item.text().lower():
                    show_row = True
                    break
            self.rules_table.setRowHidden(row, not show_row)
    
    def add_rule(self):
        """添加新规则"""
        dialog = RuleEditDialog(self, rule_manager=self.rule_manager)
        if dialog.exec() == QDialog.Accepted:
            result = dialog.result_data
            if self.rule_manager.add_rule(
                result['code'], 
                result['30d'], 
                result['match_rules']
            ):
                self.load_rules()  # 自动刷新
                QMessageBox.information(self, "成功", "规则添加成功")
            else:
                QMessageBox.critical(self, "错误", "规则添加失败")
    
    def edit_rule(self):
        """编辑选中的规则"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要编辑的规则")
            return
        
        # 获取当前行的数据
        rules = self.rule_manager.get_all_rules()
        if current_row >= len(rules):
            return
        
        rule_data = rules[current_row]
        
        dialog = RuleEditDialog(self, rule_data, self.rule_manager)
        if dialog.exec() == QDialog.Accepted:
            result = dialog.result_data
            if self.rule_manager.update_rule(
                current_row,
                result['code'],
                result['30d'],
                result['match_rules']
            ):
                self.load_rules()  # 自动刷新
                QMessageBox.information(self, "成功", "规则更新成功")
            else:
                QMessageBox.critical(self, "错误", "规则更新失败")
    
    def delete_rule(self):
        """删除选中的规则"""
        current_row = self.rules_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "警告", "请选择要删除的规则")
            return
        
        reply = QMessageBox.question(
            self, "确认删除", 
            "确定要删除选中的规则吗？", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.rule_manager.delete_rule(current_row):
                self.load_rules()  # 自动刷新
                QMessageBox.information(self, "成功", "规则删除成功")
            else:
                QMessageBox.critical(self, "错误", "规则删除失败")
    
    def reset_rules(self):
        """重置规则为默认配置"""
        reply = QMessageBox.question(
            self, "确认重置",
            "确定要重置所有规则为默认配置吗？这将清除所有自定义规则！\n\n这个操作不可撤销。",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.rule_manager.reset_to_default():
                self.load_rules()  # 自动刷新
                QMessageBox.information(self, "成功", "规则已重置为默认配置")
            else:
                QMessageBox.critical(self, "错误", "重置规则失败")

    def show_context_menu(self, position):
        """显示右键菜单"""
        menu = QMenu(self)
        
        add_action = menu.addAction("添加规则")
        add_action.triggered.connect(self.add_rule)
        
        if self.rules_table.itemAt(position):
            edit_action = menu.addAction("编辑规则")
            edit_action.triggered.connect(self.edit_rule)
            
            delete_action = menu.addAction("删除规则")
            delete_action.triggered.connect(self.delete_rule)
        
        menu.exec_(self.rules_table.mapToGlobal(position)) 