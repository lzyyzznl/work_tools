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
)
from PyQt5.QtCore import Qt


class FilePrefixAdder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件名处理工具")
        self.setFixedSize(700, 600)

        # 主控件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 布局
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # 标题
        title = QLabel("文件名处理工具")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 文件夹选择
        folder_layout = QHBoxLayout()
        folder_label = QLabel("目标文件夹:")
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText("请选择文件夹...")
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
        self.add_radio.setChecked(True)

        operation_layout.addWidget(self.replace_radio)
        operation_layout.addWidget(self.add_radio)
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

        # 输出区域
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        layout.addWidget(self.output_area)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.folder_input.setText(folder)

    def process_files(self, directory):
        """处理目录下的文件"""
        directory = Path(directory)
        if not directory.is_dir():
            self.output_area.append(f"错误：{directory} 不是有效目录")
            return

        self.output_area.append(f"开始处理: {directory}")

        # 根据选择的操作类型进行处理
        if self.replace_radio.isChecked():
            # 替换字符串模式
            old_str = self.replace_from.text().strip()
            new_str = self.replace_to.text().strip()

            if not old_str:
                self.output_area.append("错误：原字符串不能为空")
                return

            self._replace_in_filenames(directory, old_str, new_str)
        else:
            # 添加前缀/后缀模式
            text = self.add_text.text().strip()
            if not text:
                self.output_area.append("错误：要添加的文本不能为空")
                return

            is_prefix = self.position_group.checkedId() == 0
            self._add_to_filenames(directory, text, is_prefix)

    def _replace_in_filenames(self, directory, old_str, new_str):
        """替换文件名中的字符串"""
        for root, _, files in (
            os.walk(directory)
            if self.recursive_check.isChecked()
            else [(directory, [], os.listdir(directory))]
        ):
            for filename in files:
                if old_str in filename:
                    new_name = filename.replace(old_str, new_str)
                    self._rename_file(root, filename, new_name)

    def _add_to_filenames(self, directory, text, is_prefix):
        """添加前缀或后缀"""
        for root, _, files in (
            os.walk(directory)
            if self.recursive_check.isChecked()
            else [(directory, [], os.listdir(directory))]
        ):
            for filename in files:
                name, ext = os.path.splitext(filename)
                new_name = (text + name + ext) if is_prefix else (name + text + ext)
                self._rename_file(root, filename, new_name)

    def _rename_file(self, root, old_name, new_name):
        """执行文件重命名"""
        old_path = Path(root) / old_name
        new_path = Path(root) / new_name

        try:
            old_path.rename(new_path)
            self.output_area.append(f"已重命名: {old_name} -> {new_name}")
        except Exception as e:
            self.output_area.append(f"重命名 {old_name} 失败: {e}")

    def execute(self):
        folder = self.folder_input.text().strip()
        if not folder:
            self.output_area.append("错误：文件夹路径不能为空")
            return

        self.process_files(folder)
        self.output_area.append("操作完成！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FilePrefixAdder()
    window.show()
    sys.exit(app.exec_())
