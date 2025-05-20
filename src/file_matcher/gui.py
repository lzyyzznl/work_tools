import os
import pandas as pd
import datetime
from PyQt5.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QLabel,
    QApplication,
    QShortcut,
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QKeySequence
from fuzzywuzzy import fuzz


class FileMatcherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件匹配工具")
        self.setGeometry(100, 100, 800, 600)

        self.csv_path = "src/resource/content.csv"
        self.df_rules = pd.read_csv(self.csv_path)
        self.current_folder = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()

        # 文件夹选择按钮
        self.btn_select = QPushButton("选择文件夹")
        self.btn_select.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select)

        # 状态标签
        self.lbl_status = QLabel("请选择包含待匹配文件的文件夹")
        layout.addWidget(self.lbl_status)

        # 结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["文件名", "匹配规则", "匹配度"])
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ContiguousSelection)
        layout.addWidget(self.table)

        # 按钮布局
        btn_layout = QHBoxLayout()

        # 复制按钮
        self.btn_copy = QPushButton("复制")
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)

        # 导出按钮
        self.btn_export = QPushButton("导出CSV")
        self.btn_export.clicked.connect(self.export_csv)
        btn_layout.addWidget(self.btn_export)

        layout.addLayout(btn_layout)

        # 添加快捷键Ctrl+C
        shortcut = QShortcut(QKeySequence("Ctrl+C"), self)
        shortcut.activated.connect(self.copy_to_clipboard)

        central_widget.setLayout(layout)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:
            self.current_folder = folder
            self.lbl_status.setText(f"正在扫描: {folder}")
            self.match_files(folder)

    def match_files(self, folder):
        files = [
            f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))
        ]
        self.table.setRowCount(len(files))

        for row, filename in enumerate(files):
            best_match = None
            best_score = 0

            for _, rule in self.df_rules.iterrows():
                pattern = rule["match_rule"]
                # 简单替换占位符为通配符
                pattern = pattern.replace("Study code", "*").replace("Site No", "*")
                score = fuzz.ratio(filename, pattern)

                if score > best_score:
                    best_score = score
                    best_match = rule

            self.table.setItem(row, 0, QTableWidgetItem(filename))
            if best_match is not None:
                self.table.setItem(row, 1, QTableWidgetItem(best_match["match_rule"]))
                self.table.setItem(row, 2, QTableWidgetItem(str(best_score)))

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        csv_text = ""

        # 获取选中的内容
        selected = self.table.selectedItems()

        if not selected:
            # 没有选中时复制全部内容
            for row in range(self.table.rowCount()):
                row_data = []
                for col in range(self.table.columnCount()):
                    item = self.table.item(row, col)
                    row_data.append(item.text() if item else "")
                csv_text += ",".join(row_data) + "\n"
        else:
            # 处理选中的多行内容
            current_row = -1
            for item in selected:
                if item.row() != current_row:
                    if current_row != -1:
                        csv_text += "\n"
                    current_row = item.row()
                    csv_text += item.text()
                else:
                    csv_text += "," + item.text()

        mime_data.setText(csv_text.strip())
        clipboard.setMimeData(mime_data)
        self.lbl_status.setText("已复制内容到剪贴板")

    def export_csv(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"导出结果_{timestamp}.csv"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存CSV文件", default_name, "CSV Files (*.csv)"
        )

        if file_path:
            data = []
            for row in range(self.table.rowCount()):
                filename = self.table.item(row, 0).text()
                rule = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
                score = (
                    self.table.item(row, 2).text() if self.table.item(row, 2) else ""
                )

                # 查找对应的code和30d值
                matched_rule = self.df_rules[self.df_rules["match_rule"] == rule]
                code = matched_rule["code"].values[0] if not matched_rule.empty else ""
                thirty_d = (
                    matched_rule["30d"].values[0] if not matched_rule.empty else ""
                )

                data.append([filename, code, thirty_d])

            df = pd.DataFrame(data, columns=["文件名", "code", "30d"])
            df.to_csv(file_path, index=False, encoding="utf_8_sig")
            self.lbl_status.setText(f"已导出到: {file_path}")


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = FileMatcherGUI()
    window.show()
    sys.exit(app.exec_())
