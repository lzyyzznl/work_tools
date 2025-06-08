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
from PyQt5.QtCore import Qt, QUrl, QSize, QTimer, QDateTime, QSettings
from PyQt5.QtGui import QDesktopServices, QKeySequence, QIcon, QColor, QCursor, QPixmap
from PyQt5.QtWidgets import QShortcut, QDialog, QFormLayout, QDialogButtonBox, QKeySequenceEdit, QScrollArea
import shutil
import json


class CustomKeySequenceEdit(QKeySequenceEdit):
    """自定义快捷键输入控件，带有特效和提示"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.placeholder_text = "请输入快捷键"
        self.is_focused = False
        self.setup_style()
    
    def setup_style(self):
        """设置样式"""
        self.setStyleSheet("""
            QKeySequenceEdit {
                border: 2px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.9);
                font-size: 14px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 400;
                color: #1d1d1f;
                min-height: 20px;
            }
            QKeySequenceEdit:focus {
                border: 3px solid #007AFF;
                background: rgba(255, 255, 255, 1.0);
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
            }
            QKeySequenceEdit:hover {
                background: rgba(255, 255, 255, 1.0);
                border: 2px solid rgba(0, 0, 0, 0.2);
            }
        """)
    
    def focusInEvent(self, event):
        """获得焦点时的特效"""
        super().focusInEvent(event)
        self.is_focused = True
        self.update()  # 触发重绘来隐藏占位符
        # 添加选中特效动画
        self.setStyleSheet("""
            QKeySequenceEdit {
                border: 3px solid #007AFF;
                border-radius: 8px;
                padding: 12px 16px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(0, 122, 255, 0.1),
                    stop:1 rgba(255, 255, 255, 1.0));
                font-size: 14px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 400;
                color: #1d1d1f;
                min-height: 20px;
                box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.2);
            }
        """)
    
    def focusOutEvent(self, event):
        """失去焦点时恢复样式"""
        super().focusOutEvent(event)
        self.is_focused = False
        self.setup_style()
        self.update()  # 触发重绘来显示占位符
    
    def paintEvent(self, event):
        """自定义绘制，显示占位符文本"""
        super().paintEvent(event)
        
        # 如果没有设置快捷键且没有焦点，显示占位符
        if self.keySequence().isEmpty() and not self.is_focused:
            from PyQt5.QtGui import QPainter, QColor, QFont as QtFont
            from PyQt5.QtCore import Qt
            
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # 设置占位符文本样式
            painter.setPen(QColor(142, 142, 147))  # 灰色文本
            font = QtFont("PingFang SC", 12)
            font.setItalic(True)
            painter.setFont(font)
            
            # 绘制占位符文本
            rect = self.rect()
            rect.setLeft(rect.left() + 16)  # 左边距
            painter.drawText(rect, Qt.AlignLeft | Qt.AlignVCenter, self.placeholder_text)
            
            painter.end()


class ShortcutSettingsDialog(QDialog):
    """快捷键设置对话框"""
    
    def __init__(self, parent=None, current_shortcuts=None):
        super().__init__(parent)
        self.setWindowTitle("快捷键设置")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        # 移除标题栏的问号帮助按钮
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        # 设置苹果风格的样式
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(248, 249, 250, 1.0),
                    stop:1 rgba(255, 255, 255, 1.0));
                border-radius: 12px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QLabel {
                color: #1d1d1f;
                font-weight: 600;
                font-size: 14px;
                border: none;
                background: transparent;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(245, 245, 247, 0.9));
                color: #1d1d1f;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 600;
                min-height: 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(250, 250, 252, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.15);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(240, 240, 242, 1.0),
                    stop:1 rgba(235, 235, 237, 1.0));
            }
            QScrollArea {
                border: none;
                background: transparent;
                border-radius: 8px;
            }
            QScrollArea QWidget {
                background: transparent;
            }
            QScrollBar:vertical {
                background: rgba(0, 0, 0, 0.05);
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: rgba(0, 0, 0, 0.3);
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: rgba(0, 0, 0, 0.5);
            }
        """)
        
        # 默认快捷键配置
        self.default_shortcuts = {
            "添加文件": "Ctrl+O",
            "添加文件夹": "Ctrl+Shift+O", 
            "预览更改": "F6",
            "重置参数": "Ctrl+R",
            "执行重命名": "Ctrl+Return",
            "撤回操作": "Ctrl+Z",
            "清空列表": "Ctrl+Delete",
            "显示帮助": "F1",
            "刷新文件列表": "F5",
            "聚焦所有文件": "Ctrl+A",
            "移除选中文件": "Delete"
        }
        
        # 使用传入的快捷键或默认快捷键
        self.shortcuts = current_shortcuts or self.default_shortcuts.copy()
        
        self.init_ui()
    
    def init_ui(self):
        """初始化用户界面"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 添加标题区域
        title_widget = QWidget()
        title_layout = QVBoxLayout(title_widget)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        title_label = QLabel("快捷键设置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: 700;
                color: #1d1d1f;
                margin-bottom: 8px;
            }
        """)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("自定义您的快捷键，提升工作效率")
        subtitle_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-weight: 400;
                color: #6e6e73;
                margin-bottom: 0px;
            }
        """)
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_widget)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 创建滚动内容widget
        scroll_content = QWidget()
        form_layout = QFormLayout(scroll_content)
        form_layout.setSpacing(15)
        form_layout.setContentsMargins(10, 10, 10, 10)
        
        self.shortcut_editors = {}
        
        for action_name, shortcut in self.shortcuts.items():
            # 创建标签
            label = QLabel(f"{action_name}:")
            label.setStyleSheet("""
                QLabel {
                    font-size: 14px;
                    font-weight: 600;
                    color: #1d1d1f;
                    min-width: 120px;
                }
            """)
            
            # 创建自定义快捷键编辑器
            editor = CustomKeySequenceEdit()
            editor.setKeySequence(QKeySequence(shortcut))
            
            form_layout.addRow(label, editor)
            self.shortcut_editors[action_name] = editor
        
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)
        
        # 添加按钮区域
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        # 恢复默认按钮
        reset_button = QPushButton("🔄 恢复默认")
        reset_button.clicked.connect(self.reset_to_defaults)
        reset_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 149, 0, 0.9),
                    stop:1 rgba(255, 124, 0, 0.9));
                color: white;
                font-weight: 700;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 149, 0, 1.0),
                    stop:1 rgba(255, 124, 0, 1.0));
            }
        """)
        button_layout.addWidget(reset_button)
        
        button_layout.addStretch()
        
        # 标准对话框按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.button(QDialogButtonBox.Ok).setText("确定")
        button_box.button(QDialogButtonBox.Cancel).setText("取消")
        
        # 设置确定按钮为蓝色主题
        ok_button = button_box.button(QDialogButtonBox.Ok)
        ok_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF,
                    stop:1 #0051D5);
                color: white;
                font-weight: 700;
                padding: 10px 24px;
                min-width: 80px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0056CC,
                    stop:1 #003D9F);
            }
        """)
        
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_layout.addWidget(button_box)
        
        layout.addWidget(button_widget)
    
    def reset_to_defaults(self):
        """恢复默认快捷键"""
        reply = QMessageBox.question(self, "确认恢复", 
                                   "确定要恢复所有快捷键到默认设置吗？\n这将覆盖您当前的自定义配置。",
                                   QMessageBox.Yes | QMessageBox.No, 
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            for action_name, default_shortcut in self.default_shortcuts.items():
                if action_name in self.shortcut_editors:
                    self.shortcut_editors[action_name].setKeySequence(QKeySequence(default_shortcut))
    
    def get_shortcuts(self):
        """获取当前设置的快捷键"""
        result = {}
        for action_name, editor in self.shortcut_editors.items():
            sequence = editor.keySequence()
            result[action_name] = sequence.toString() if not sequence.isEmpty() else ""
        return result
    
    def validate_shortcuts(self):
        """验证快捷键是否有冲突"""
        shortcuts = self.get_shortcuts()
        used_shortcuts = {}
        conflicts = []
        
        for action_name, shortcut in shortcuts.items():
            if shortcut and shortcut != "":
                if shortcut in used_shortcuts:
                    conflicts.append(f"'{shortcut}' 在 '{action_name}' 和 '{used_shortcuts[shortcut]}' 中重复")
                else:
                    used_shortcuts[shortcut] = action_name
        
        if conflicts:
            QMessageBox.warning(self, "快捷键冲突", "发现以下快捷键冲突：\n\n" + "\n".join(conflicts))
            return False
        return True
    
    def accept(self):
        """确认设置"""
        if self.validate_shortcuts():
            super().accept()


class QuickTooltipLabel(QLabel):
    """Custom QLabel with faster tooltip display (300ms delay)."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self._show_tooltip)
        self._tooltip_text = ""
    
    def setToolTip(self, text):
        """Set the tooltip text."""
        self._tooltip_text = text
    
    def enterEvent(self, event):
        """Show tooltip with 300ms delay when mouse enters."""
        if self._tooltip_text:
            self.tooltip_timer.start(300)
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Hide tooltip when mouse leaves."""
        self.tooltip_timer.stop()
        from PyQt5.QtWidgets import QToolTip
        QToolTip.hideText()
        super().leaveEvent(event)
    
    def _show_tooltip(self):
        """Show the tooltip at cursor position."""
        if self._tooltip_text:
            from PyQt5.QtWidgets import QToolTip
            from PyQt5.QtGui import QCursor
            QToolTip.showText(QCursor.pos(), self._tooltip_text, self)


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
        
        # 快捷键配置 - 使用用户配置目录
        self.shortcuts_config_file = self.get_config_file_path()
        self.shortcuts = self.load_shortcuts_config()
        
        # 设置苹果风格字体系统
        self.setup_apple_fonts()
        
        # Auto-preview timer - delays preview update by 0.3 seconds after user input
        self.preview_timer = QTimer()
        self.preview_timer.setSingleShot(True)
        self.preview_timer.timeout.connect(self.auto_preview_changes)

        # --- Setup Paths and Icons ---
        try:
            base_path = sys._MEIPASS  # PyInstaller临时目录
        except AttributeError:
            base_path = os.path.dirname(os.path.abspath(__file__)).rsplit(f"{os.sep}src{os.sep}", 1)[0]

        # 修复打包后的资源路径问题
        if hasattr(sys, '_MEIPASS'):
            # 在打包的exe中，资源文件被复制到resource文件夹
            self.resource_path = os.path.join(base_path, "resource")
        else:
            # 在开发环境中，保持原有路径
            self.resource_path = os.path.join(base_path, "src", "resource")
        
        icon_path = os.path.join(self.resource_path, "打印机.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            # 如果PNG图标不存在，尝试加载ICO图标
            ico_path = os.path.join(self.resource_path, "打印机.ico")
            if os.path.exists(ico_path):
                self.setWindowIcon(QIcon(ico_path))
        
        # --- Enable Drag and Drop ---
        self.setAcceptDrops(True)

        self.init_ui()

    def load_shortcuts_config(self):
        """加载快捷键配置"""
        default_shortcuts = {
            "添加文件": "Ctrl+O",
            "添加文件夹": "Ctrl+Shift+O", 
            "预览更改": "F6",
            "重置参数": "Ctrl+R",
            "执行重命名": "Ctrl+Return",
            "撤回操作": "Ctrl+Z",
            "清空列表": "Ctrl+Delete",
            "显示帮助": "F1",
            "刷新文件列表": "F5",
            "聚焦所有文件": "Ctrl+A",
            "移除选中文件": "Delete"
        }
        
        try:
            if os.path.exists(self.shortcuts_config_file):
                with open(self.shortcuts_config_file, 'r', encoding='utf-8') as f:
                    saved_shortcuts = json.load(f)
                    # 确保所有默认快捷键都存在
                    for key, value in default_shortcuts.items():
                        if key not in saved_shortcuts:
                            saved_shortcuts[key] = value
                    return saved_shortcuts
        except Exception as e:
            print(f"Failed to load shortcuts config: {e}")
        
        return default_shortcuts

    def save_shortcuts_config(self):
        """保存快捷键配置"""
        try:
            with open(self.shortcuts_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.shortcuts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存快捷键配置失败：{e}")

    def setup_shortcuts(self):
        """设置快捷键"""
        # 清除现有的快捷键
        if hasattr(self, 'shortcut_objects'):
            for shortcut in self.shortcut_objects:
                shortcut.setParent(None)
        
        self.shortcut_objects = []
        
        # 快捷键与功能的映射
        shortcut_mapping = {
            "聚焦所有文件": (self.file_table, self.select_all_files),
            "移除选中文件": (self.file_table, self.remove_selected_files),
            "刷新文件列表": (self, self.refresh_file_list)
        }
        
        # 为每个快捷键创建QShortcut对象
        for action_name, shortcut_key in self.shortcuts.items():
            if action_name in shortcut_mapping and shortcut_key:
                parent, callback = shortcut_mapping[action_name]
                try:
                    shortcut = QShortcut(QKeySequence(shortcut_key), parent, callback)
                    self.shortcut_objects.append(shortcut)
                except Exception as e:
                    print(f"Failed to create shortcut for {action_name}: {e}")

    def setup_apple_fonts(self):
        """设置苹果官网风格的字体系统"""
        from PyQt5.QtGui import QFont, QFontDatabase
        
        # 苹果字体优先级：PingFang SC > SF Pro > System UI > 备选字体
        apple_font_families = [
            "PingFang SC",           # 苹方字体 (macOS/iOS中文)
            "SF Pro Display",        # 苹果无衬线字体
            "SF Pro Text",           # 苹果文本字体
            "system-ui",             # 系统UI字体
            "-apple-system",         # 苹果系统字体
            "BlinkMacSystemFont",    # Webkit苹果字体
            "Helvetica Neue",        # 苹果经典字体
            "Microsoft YaHei UI",    # 微软雅黑UI (Windows中文)
            "Segoe UI",              # Windows系统字体
            "Arial",                 # 备选字体
            "sans-serif"             # 最终备选
        ]
        
        # 检查可用字体
        font_db = QFontDatabase()
        available_fonts = font_db.families()
        
        selected_font_family = "Arial"  # 默认备选
        for font_family in apple_font_families:
            if font_family in available_fonts:
                selected_font_family = font_family
                break
        
        # 设置全局字体
        app_font = QFont(selected_font_family, 14)
        app_font.setWeight(QFont.Normal)
        app_font.setStyleHint(QFont.SansSerif)
        app_font.setHintingPreference(QFont.PreferFullHinting)
        
        # 应用到整个应用程序
        QApplication.instance().setFont(app_font)
        
        # 设置窗口级别的样式
        self.setStyleSheet(f"""
            QMainWindow {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: #1d1d1f;
            }}
            
            /* 标题级别字体 */
            QLabel {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #1d1d1f;
            }}
            
            /* 按钮字体 */
            QPushButton, QToolButton {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 600;
                color: #1d1d1f;
            }}
            
            /* 输入框字体 */
            QLineEdit, QTextEdit, QPlainTextEdit {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: #1d1d1f;
            }}
            
            /* 表格字体 */
            QTableWidget, QTableView, QHeaderView {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 13px;
                font-weight: 400;
                color: #1d1d1f;
            }}
            
            QHeaderView::section {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 13px;
                font-weight: 600;
                color: #1d1d1f;
            }}
            
            /* 菜单字体 */
            QMenu, QMenuBar {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 400;
                color: #1d1d1f;
            }}
            
            /* 状态栏字体 */
            QStatusBar {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 12px;
                font-weight: 400;
                color: #6e6e73;
            }}
            
            /* 复选框和单选按钮字体 */
            QCheckBox, QRadioButton {{
                font-family: {selected_font_family}, "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 14px;
                font-weight: 500;
                color: #1d1d1f;
            }}
        """)

    def get_config_file_path(self):
        """获取配置文件路径，保存到用户配置目录"""
        import os
        import platform
        
        system = platform.system()
        
        if system == "Windows":
            # Windows: 使用 %APPDATA% 目录
            config_dir = os.path.join(os.environ.get('APPDATA', ''), 'FileRenamerTool')
        elif system == "Darwin":  # macOS
            # macOS: 使用 ~/Library/Application Support/
            home_dir = os.path.expanduser('~')
            config_dir = os.path.join(home_dir, 'Library', 'Application Support', 'FileRenamerTool')
        else:  # Linux and others
            # Linux: 使用 ~/.config/
            home_dir = os.path.expanduser('~')
            config_dir = os.path.join(home_dir, '.config', 'FileRenamerTool')
        
        # 确保配置目录存在
        try:
            os.makedirs(config_dir, exist_ok=True)
        except Exception as e:
            print(f"Failed to create config directory: {e}")
            # 如果创建失败，回退到当前目录
            return "shortcuts_config.json"
        
        return os.path.join(config_dir, 'shortcuts_config.json')

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
        self.setup_shortcuts()

    def create_toolbar(self):
        """Creates the main application toolbar."""
        toolbar = QToolBar("主工具栏")
        toolbar.setIconSize(QSize(28, 28))
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setStyleSheet("""
            QToolBar { 
                padding: 8px; 
                border: none;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QToolButton { 
                padding: 10px; 
                font-size: 14px; 
                font-weight: 600; 
                border-radius: 8px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                color: #1d1d1f;
            }
            QToolButton:hover { 
                background-color: rgba(0, 0, 0, 0.05);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
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

        def get_icon(icon_name):
            """Load custom icon from resource folder, fallback to system icon if not found."""
            icon_path = os.path.join(self.resource_path, f"{icon_name}.png")
            if os.path.exists(icon_path):
                return QIcon(icon_path)
            else:
                # Fallback to system icons
                icon_mapping = {
                    "添加文件": QStyle.SP_FileIcon,
                    "添加文件夹": QStyle.SP_DirIcon,
                    "预览": QStyle.SP_BrowserReload,
                    "重置参数": QStyle.SP_DialogResetButton,
                    "执行": QStyle.SP_DialogApplyButton,
                    "撤回": QStyle.SP_ArrowBack,
                    "清空参数": QStyle.SP_TrashIcon,
                    "使用说明": QStyle.SP_FileDialogDetailedView
                }
                return style.standardIcon(icon_mapping.get(icon_name, QStyle.SP_ComputerIcon))

        # Add actions with custom icons and shortcuts
        add_action(get_icon("添加文件"), "添加文件", self.add_files, self.shortcuts.get("添加文件", "Ctrl+O"))
        add_action(get_icon("添加文件夹"), "添加文件夹", self.add_folder, self.shortcuts.get("添加文件夹", "Ctrl+Shift+O"))
        toolbar.addSeparator()
        add_action(get_icon("预览"), "预览", self.preview_changes, self.shortcuts.get("预览更改", "F6"))
        add_action(get_icon("重置参数"), "重置参数", self.reset_parameters, self.shortcuts.get("重置参数", "Ctrl+R"))
        toolbar.addSeparator()
        
        execute_shortcut = self.shortcuts.get("执行重命名", "Ctrl+Return")
        execute_action = QAction(get_icon("执行"), "执行", self)
        execute_action.triggered.connect(self.execute_rename)
        execute_action.setShortcut(execute_shortcut)
        execute_action.setToolTip(f"执行 ({execute_shortcut})")
        toolbar.addAction(execute_action)
        if (button := toolbar.widgetForAction(execute_action)):
            button.setStyleSheet("font-weight: bold; color: green;")
        
        toolbar.addSeparator()
        
        undo_shortcut = self.shortcuts.get("撤回操作", "Ctrl+Z")
        self.undo_action = QAction(get_icon("撤回"), "撤回", self)
        self.undo_action.triggered.connect(self.undo_last_operation)
        self.undo_action.setEnabled(False)
        self.undo_action.setShortcut(undo_shortcut)
        self.undo_action.setToolTip(f"撤回 ({undo_shortcut})")
        toolbar.addAction(self.undo_action)
        if (button := toolbar.widgetForAction(self.undo_action)):
            button.setStyleSheet("font-weight: bold; color: red;")
        
        toolbar.addSeparator()
        add_action(get_icon("清空参数"), "清空列表", self.clear_file_list, self.shortcuts.get("清空列表", "Ctrl+Delete"))
        add_action(get_icon("使用说明"), "使用说明", self.show_help, self.shortcuts.get("显示帮助", "F1"))
        
        # 添加设置菜单项
        toolbar.addSeparator()
        add_action(get_icon("设置快捷键"), "快捷键设置", self.show_shortcut_settings, "")

    def create_operation_tabs(self):
        """Creates and configures the QTabWidget for renaming operations."""
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            /* 主容器样式 */
            QTabWidget {
                border: none;
                background: transparent;
            }
            
            /* 标签栏样式 */
            QTabBar {
                border: none;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 12px;
                margin: 2px;
            }
            
            /* 标签页基础样式 */
            QTabBar::tab {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.9),
                    stop:1 rgba(245, 245, 247, 0.9));
                color: #1d1d1f;
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 10px;
                padding: 12px 20px;
                margin: 3px 2px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-size: 15px;
                font-weight: 600;
                min-width: 100px;
                text-align: center;
                box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
            }
            
            /* 标签页悬停效果 */
            QTabBar::tab:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 1.0),
                    stop:1 rgba(250, 250, 252, 1.0));
                border: 1px solid rgba(0, 0, 0, 0.15);
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
                transform: translateY(-1px);
            }
            
            /* 选中标签页样式 - 苹果蓝色 */
            QTabBar::tab:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF,
                    stop:1 #0051D5);
                color: white;
                border: 1px solid #0051D5;
                box-shadow: 0 4px 16px rgba(0, 122, 255, 0.3);
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 700;
            }
            
            /* 内容面板样式 */
            QTabWidget::pane {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 12px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 rgba(255, 255, 255, 0.98),
                    stop:1 rgba(250, 250, 252, 0.98));
                margin-top: 2px;
                box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
                backdrop-filter: blur(10px);
            }
            
            /* 内容面板顶部圆角调整 */
            QTabWidget::tab-bar {
                alignment: left;
            }
        """)
        
        # --- Tab 1: Replace String ---
        replace_widget = QWidget()
        replace_widget.setStyleSheet("""
            QWidget { background: transparent; }
            QLabel { 
                color: #1d1d1f; 
                font-weight: 600; 
                font-size: 17px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 400;
                selection-background-color: #007AFF;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
                background: rgba(255, 255, 255, 1.0);
            }
            QLineEdit::placeholder {
                color: #8e8e93;
                font-weight: 400;
            }
        """)
        replace_layout = QHBoxLayout(replace_widget)
        replace_layout.setSpacing(15)
        replace_layout.setContentsMargins(20, 15, 20, 15)
        
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
        add_widget = QWidget()
        add_widget.setStyleSheet("""
            QWidget { background: transparent; }
            QLabel { 
                color: #1d1d1f; 
                font-weight: 600; 
                font-size: 17px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 400;
                selection-background-color: #007AFF;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
                background: rgba(255, 255, 255, 1.0);
            }
            QLineEdit::placeholder {
                color: #8e8e93;
                font-weight: 400;
            }
            QRadioButton {
                color: #1d1d1f;
                font-weight: 500;
                font-size: 16px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                spacing: 8px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid rgba(0, 0, 0, 0.15);
                background: rgba(255, 255, 255, 0.9);
            }
            QRadioButton::indicator:checked {
                background: #007AFF;
                border: 2px solid #007AFF;
            }
            QRadioButton::indicator:hover {
                border: 2px solid rgba(0, 122, 255, 0.5);
            }
        """)
        add_layout = QHBoxLayout(add_widget)
        add_layout.setSpacing(15)
        add_layout.setContentsMargins(20, 15, 20, 15)
        
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
        number_widget = QWidget()
        # 定义苹果风格的通用样式
        apple_tab_style = """
            QWidget { background: transparent; }
            QLabel { 
                color: #1d1d1f; 
                font-weight: 600; 
                font-size: 17px;
                font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
            }
            QLineEdit {
                border: 1px solid rgba(0, 0, 0, 0.1);
                border-radius: 8px;
                padding: 12px 16px;
                background: rgba(255, 255, 255, 0.8);
                font-size: 16px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                font-weight: 400;
                selection-background-color: #007AFF;
                color: #1d1d1f;
            }
            QLineEdit:focus {
                border: 2px solid #007AFF;
                background: rgba(255, 255, 255, 1.0);
            }
            QLineEdit::placeholder {
                color: #8e8e93;
                font-weight: 400;
            }
            QRadioButton {
                color: #1d1d1f;
                font-weight: 500;
                font-size: 16px;
                font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
                spacing: 8px;
                padding: 8px;
            }
            QRadioButton::indicator {
                width: 18px;
                height: 18px;
                border-radius: 9px;
                border: 2px solid rgba(0, 0, 0, 0.15);
                background: rgba(255, 255, 255, 0.9);
            }
            QRadioButton::indicator:checked {
                background: #007AFF;
                border: 2px solid #007AFF;
            }
            QRadioButton::indicator:hover {
                border: 2px solid rgba(0, 122, 255, 0.5);
            }
        """
        number_widget.setStyleSheet(apple_tab_style)
        number_layout = QVBoxLayout(number_widget)
        number_layout.setSpacing(15)
        number_layout.setContentsMargins(20, 15, 20, 15)
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
        delete_widget = QWidget()
        delete_widget.setStyleSheet(apple_tab_style)
        delete_layout = QVBoxLayout(delete_widget)
        delete_layout.setSpacing(15)
        delete_layout.setContentsMargins(20, 15, 20, 15)
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
        title_label.setStyleSheet("""
            font-size: 32px; 
            font-weight: 700; 
            color: #1d1d1f; 
            margin-bottom: 15px; 
            border: none;
            font-family: "PingFang SC", "SF Pro Display", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
        """)
        
        # Subtitle
        subtitle_label = QLabel("或使用上方工具栏的\"添加文件\"、\"添加文件夹\"按钮")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 18px; 
            color: #6e6e73; 
            margin-bottom: 25px; 
            border: none;
            font-weight: 500;
            font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
        """)
        
        # Tips
        tips_label = QLabel("💡 支持的快捷键：Ctrl+O (添加文件)、Ctrl+Shift+O (添加文件夹)")
        tips_label.setAlignment(Qt.AlignCenter)
        tips_label.setStyleSheet("""
            font-size: 14px; 
            color: #8e8e93; 
            border: none;
            font-weight: 400;
            font-family: "PingFang SC", "SF Pro Text", "Helvetica Neue", "Microsoft YaHei UI", "Segoe UI", Arial, sans-serif;
        """)
        
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
        
        # Add help tooltip icon using resource/提示.png with fast tooltip
        help_label = QuickTooltipLabel()
        help_pixmap = QPixmap(os.path.join(self.resource_path, "提示.png"))
        # Scale the icon to larger size (32x32 instead of 16x16)
        scaled_pixmap = help_pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        help_label.setPixmap(scaled_pixmap)
        help_label.setToolTip("只会操作选中的文件，如果一个都不选就处理全部文件")
        help_label.setStyleSheet("margin-left: 2px; padding: 1px;")
        help_label.setCursor(QCursor(Qt.PointingHandCursor))
        select_all_layout.addWidget(help_label)
        select_all_layout.addStretch()
        
        # Add refresh button on the right side
        refresh_button = QPushButton("🔄")
        refresh_shortcut = self.shortcuts.get("刷新文件列表", "F5")
        refresh_button.setToolTip(f"刷新文件列表，更新文件信息并移除已删除的文件 ({refresh_shortcut})")
        refresh_button.clicked.connect(self.refresh_file_list)
        refresh_button.setFixedSize(32, 32)
        refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        select_all_layout.addWidget(refresh_button)
        
        # Updated table structure: "", "当前文件名", "预览", "执行结果", "最后更新时间", "文件大小", "路径"
        table = QTableWidget(columnCount=7)
        table.setHorizontalHeaderLabels(["", "当前文件名", "预览", "执行结果", "最后更新时间", "文件大小", "路径(单击可打开)"])
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setContextMenuPolicy(Qt.CustomContextMenu)
        table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        # Enable sorting
        table.setSortingEnabled(True)
        
        # Connect table item click handler
        table.itemClicked.connect(self.table_item_clicked)
        
        # Connect table item double click handler
        table.itemDoubleClicked.connect(self.table_item_double_clicked)
        
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
        status_bar.addPermanentWidget(QLabel(f"作者:荔枝鱼  v{self.version} @版权所有"))
    
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
            open_file_action = menu.addAction("打开文件")
            open_folder_action = menu.addAction("打开文件所在文件夹")
            menu.addSeparator()
            rename_action = menu.addAction("重命名文件")
            menu.addSeparator()
            refresh_action = menu.addAction("刷新文件列表")
            menu.addSeparator()
            remove_action = menu.addAction("从列表中移除")
            
            action = menu.exec_(self.file_table.mapToGlobal(position))
            
            if action == open_file_action:
                self.open_file(row)
            elif action == rename_action:
                self.rename_single_file(row)
            elif action == open_folder_action:
                self.open_file_folder(row)
            elif action == refresh_action:
                self.refresh_file_list()
            elif action == remove_action:
                self.remove_selected_files()
        else:
            # No item clicked, show general menu
            refresh_action = menu.addAction("刷新文件列表")
            menu.addSeparator()
            remove_action = menu.addAction("从列表中移除选中项")
            
            action = menu.exec_(self.file_table.mapToGlobal(position))
            if action == refresh_action:
                self.refresh_file_list()
            elif action == remove_action:
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

    def show_shortcut_settings(self):
        """显示快捷键设置对话框"""
        dialog = ShortcutSettingsDialog(self, self.shortcuts)
        if dialog.exec_() == QDialog.Accepted:
            # 保存新的快捷键配置
            self.shortcuts = dialog.get_shortcuts()
            self.save_shortcuts_config()
            
            # 重新设置快捷键
            self.setup_shortcuts()
            
            # 重新创建工具栏以更新提示文本
            self.recreate_toolbar()
            
            # 更新刷新按钮的提示文本
            self.update_refresh_button_tooltip()
            
            self.update_status("快捷键设置已保存并生效。")

    def recreate_toolbar(self):
        """重新创建工具栏"""
        # 移除现有工具栏
        for toolbar in self.findChildren(QToolBar):
            self.removeToolBar(toolbar)
        
        # 重新创建工具栏
        self.create_toolbar()

    def update_refresh_button_tooltip(self):
        """更新刷新按钮的工具提示"""
        # 这里需要找到刷新按钮并更新其工具提示
        # 由于刷新按钮在 select_all_layout 中，我们需要重新创建文件表格
        # 或者可以保存刷新按钮的引用
        pass  # 这个方法在重新创建工具栏时会自动更新

    def show_help(self):
        """Shows the help documentation."""
        help_file_path = Path("使用说明.txt")
        
        # Create help file if it doesn't exist
        if not help_file_path.exists() or True:  # Always recreate to show current shortcuts
            # 生成快捷键帮助文本
            shortcuts_help_lines = []
            shortcut_descriptions = {
                "添加文件": "添加文件",
                "添加文件夹": "添加文件夹",
                "预览更改": "预览更改", 
                "重置参数": "重置参数",
                "执行重命名": "执行重命名",
                "撤回操作": "撤回操作",
                "清空列表": "清空列表",
                "显示帮助": "显示此帮助",
                "刷新文件列表": "刷新文件列表",
                "聚焦所有文件": "聚焦所有文件行",
                "移除选中文件": "移除选中的文件"
            }
            
            for action_name, description in shortcut_descriptions.items():
                shortcut = self.shortcuts.get(action_name, "")
                if shortcut:
                    shortcuts_help_lines.append(f"{shortcut:<15} - {description}")
            
            shortcuts_help = "\n".join(shortcuts_help_lines)
            
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

{shortcuts_help}

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
- 打开文件：直接打开选中的文件
- 打开文件所在文件夹：在资源管理器中打开文件夹
- 重命名文件：直接编辑单个文件名
- 刷新文件列表：更新文件信息，移除已删除的文件
- 从列表中移除：移除不需要的文件

=== 表格功能 ===

- 点击列标题可以排序
- 双击文件名或预览列可以直接打开文件
- 点击蓝色路径可以打开文件夹
- 执行结果显示操作成功/失败状态
- 显示文件最后更新时间和大小
- 只会操作选中的文件，如果一个都不选就处理全部文件
- 表头右侧的刷新按钮可以更新文件信息

=== 安全提示 ===

- 重命名前会显示预览
- 支持撤回最近的操作
- 同名文件会显示错误提示
- 只处理选中的文件，提高安全性

版本：v2.0.0
作者：荔枝鱼

注意：快捷键可以在工具栏的"快捷键设置"中自定义
""".format(shortcuts_help=shortcuts_help)
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
        """Selects all rows in the table (focus, not checkbox)."""
        self.file_table.selectAll()
        self.update_status("已聚焦所有文件行。")

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

    def open_file(self, row):
        """Opens the file directly."""
        if row >= len(self.files_data):
            return
            
        file_path = self.files_data[row]["path_obj"]
        
        try:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(file_path)))
            self.update_status(f"已打开文件：{file_path.name}")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法打开文件：{e}")

    def refresh_file_list(self):
        """Refreshes the file list by checking if files still exist and updating their information."""
        if not self.files_data:
            self.update_status("没有文件需要刷新。")
            return
        
        refreshed_count = 0
        missing_files = []
        
        for row in range(len(self.files_data) - 1, -1, -1):  # Iterate backwards to safely remove items
            file_data = self.files_data[row]
            file_path = file_data["path_obj"]
            
            # Check if file still exists
            if not file_path.exists():
                missing_files.append(file_path.name)
                # Remove from data and table
                del self.files_data[row]
                self.file_table.removeRow(row)
            else:
                # Update file information
                try:
                    stat_result = file_path.stat()
                    modification_time = QDateTime.fromSecsSinceEpoch(int(stat_result.st_mtime))
                    size_bytes = stat_result.st_size
                    
                    # Update table display
                    self.file_table.item(row, 4).setText(modification_time.toString("yyyy-MM-dd hh:mm:ss"))
                    self.file_table.item(row, 5).setText(self.format_file_size(size_bytes))
                    refreshed_count += 1
                except Exception as e:
                    print(f"Error refreshing {file_path}: {e}")
        
        # Show empty state if no files left
        if len(self.files_data) == 0:
            self.file_table.hide()
            self.select_all_widget.hide()
            self.empty_state_widget.show()
        
        # Update status message
        if missing_files:
            self.update_status(f"刷新完成。更新了 {refreshed_count} 个文件，移除了 {len(missing_files)} 个不存在的文件。")
        else:
            self.update_status(f"刷新完成。更新了 {refreshed_count} 个文件信息。")

    def table_item_clicked(self, item):
        """Handles table item click events."""
        row = item.row()
        column = item.column()
        
        # If clicked on path column (column 6), open the folder
        if column == 6:
            self.open_file_folder(row)

    def table_item_double_clicked(self, item):
        """Handles table item double click events."""
        row = item.row()
        column = item.column()
        
        # If double clicked on filename column (column 1) or preview column (column 2), open the file
        if column == 1 or column == 2:
            self.open_file(row)

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
