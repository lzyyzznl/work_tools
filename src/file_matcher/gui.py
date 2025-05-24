import datetime
import os
import subprocess
import sys

import pandas as pd
from PyQt5.QtCore import QMimeData, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QIcon, QKeySequence, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QShortcut,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)


class FileMatcherGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件名匹配工具")
        self.setGeometry(100, 100, 800, 600)
        # 设置窗口图标 - 处理打包和开发两种模式
        try:
            # 打包后模式
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发模式
            base_path = os.path.dirname(os.path.dirname(__file__))

        icon_path = os.path.join(base_path, "resource", "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        # 获取资源文件路径 - 处理打包和开发两种模式
        try:
            # 打包后模式
            base_path = sys._MEIPASS
        except AttributeError:
            # 开发模式
            base_path = os.path.dirname(os.path.dirname(__file__))

        self.csv_path = os.path.join(base_path, "resource", "content.csv")
        if not os.path.exists(self.csv_path):
            QMessageBox.critical(self, "错误", f"找不到规则文件: {self.csv_path}")
            sys.exit(1)
        self.df_rules = pd.read_csv(self.csv_path)
        self.current_folder = None

        self.init_ui()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 设置全局样式
        self.setStyleSheet(
            """
            QWidget {
                font-family: 'Microsoft YaHei';
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton {
                padding: 10px 20px;
                border-radius: 6px;
                min-width: 120px;
                font-size: 16px;
                font-weight: bold;
                background-color: #87CEFA;  /* 天蓝色 */
                color: black;
                border: 1px solid #4682B4;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #6495ED;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
            QLabel {
                font-weight: bold;
                font-size: 16px;
            }
            QTableWidget {
                font-size: 16px;
                font-weight: bold;
            }
            QHeaderView::section {
                padding: 6px;
                font-size: 16px;
                font-weight: bold;
            }
        """
        )

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # 文件夹选择按钮
        self.btn_select = QPushButton("📁 选择文件夹")
        self.btn_select.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #87CEFA;  /* 天蓝色 */
                color: black;
                border: 1px solid #4682B4;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #6495ED;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
        """
        )
        self.btn_select.clicked.connect(self.select_folder)
        layout.addWidget(self.btn_select)

        # 状态标签
        self.lbl_status = QLabel("请选择包含待匹配文件的文件夹")
        self.lbl_status.setStyleSheet(
            """
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 5px;
            }
        """
        )
        layout.addWidget(self.lbl_status)

        # 结果表格
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(
            ["文件名", "匹配结果", "Code", "30d", "命名规则"]
        )
        self.table.setSelectionBehavior(QTableWidget.SelectItems)
        self.table.setSelectionMode(QTableWidget.ContiguousSelection)

        # 表格自动填充窗口
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # 设置列宽策略
        self.table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.Stretch
        )  # 文件名列自动拉伸
        self.table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeToContents
        )  # 匹配结果自适应
        self.table.horizontalHeader().setSectionResizeMode(
            2, QHeaderView.ResizeToContents
        )  # Code自适应
        self.table.horizontalHeader().setSectionResizeMode(
            3, QHeaderView.ResizeToContents
        )  # 30d自适应
        self.table.horizontalHeader().setSectionResizeMode(
            4, QHeaderView.Stretch
        )  # 命名规则自动拉伸

        # 启用排序
        self.table.setSortingEnabled(True)

        layout.addWidget(self.table)

        # 按钮布局
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        # 复制按钮
        self.btn_copy = QPushButton("📋 复制表格内容")
        self.btn_copy.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #87CEFA;  /* 天蓝色 */
                color: black;
                border: 1px solid #4682B4;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #6495ED;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
        """
        )
        self.btn_copy.clicked.connect(self.copy_to_clipboard)
        btn_layout.addWidget(self.btn_copy)

        # 打开文件按钮
        self.btn_open = QPushButton("📂 打开选中行文件")
        self.btn_open.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #87CEFA;  /* 天蓝色 */
                color: black;
                border: 1px solid #4682B4;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #6495ED;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
        """
        )
        self.btn_open.clicked.connect(self.open_file)
        btn_layout.addWidget(self.btn_open)

        # 导出按钮
        self.btn_export = QPushButton("💾 导出文件")
        self.btn_export.setStyleSheet(
            """
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                background-color: #87CEFA;  /* 天蓝色 */
                color: black;
                border: 1px solid #4682B4;
                box-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            QPushButton:hover {
                background-color: #B0E0E6;
            }
            QPushButton:pressed {
                background-color: #6495ED;
                box-shadow: 1px 1px 2px rgba(0,0,0,0.2);
            }
        """
        )
        self.btn_export.clicked.connect(self.export_data)
        btn_layout.addWidget(self.btn_export)

        layout.addLayout(btn_layout)

        # 添加版权信息
        copyright_layout = QHBoxLayout()
        copyright_layout.addStretch()
        copyright_label = QLabel("作者:lizeyu  @版权所有,请勿随意传播与商用")
        copyright_label.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #666;
                font-style: italic;
                padding: 5px;
            }
        """
        )
        copyright_layout.addWidget(copyright_label)
        layout.addLayout(copyright_layout)

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
            matched = False
            filename_item = QTableWidgetItem(filename)
            filename_item.setToolTip(filename)
            self.table.setItem(row, 0, filename_item)

            for _, rule in self.df_rules.iterrows():
                if rule["match_rule"] in filename:
                    matched_item = QTableWidgetItem("是")
                    matched_item.setToolTip("是")
                    self.table.setItem(row, 1, matched_item)

                    code_item = QTableWidgetItem(rule["code"])
                    code_item.setToolTip(rule["code"])
                    self.table.setItem(row, 2, code_item)

                    thirty_d_item = QTableWidgetItem(rule["30d"])
                    thirty_d_item.setToolTip(rule["30d"])
                    self.table.setItem(row, 3, thirty_d_item)

                    detail_item = QTableWidgetItem(rule["match_rule_detail"])
                    detail_item.setToolTip(rule["match_rule_detail"])
                    self.table.setItem(row, 4, detail_item)

                    # 设置匹配成功行背景色(浅绿色)
                    for col in range(self.table.columnCount()):
                        self.table.item(row, col).setBackground(QColor(144, 238, 144))
                    matched = True
                    break

            if not matched:
                matched_item = QTableWidgetItem("否")
                matched_item.setToolTip("否")
                self.table.setItem(row, 1, matched_item)

                empty_item1 = QTableWidgetItem("")
                empty_item1.setToolTip("")
                self.table.setItem(row, 2, empty_item1)

                empty_item2 = QTableWidgetItem("")
                empty_item2.setToolTip("")
                self.table.setItem(row, 3, empty_item2)

                empty_item3 = QTableWidgetItem("")
                empty_item3.setToolTip("")
                self.table.setItem(row, 4, empty_item3)
                # 设置未匹配行背景色(淡红色)
                for col in range(self.table.columnCount()):
                    self.table.item(row, col).setBackground(QColor(255, 182, 193))

    def open_file(self):
        if not self.current_folder:
            QMessageBox.warning(self, "警告", "请先选择文件夹")
            return

        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "警告", "请先选择要打开的文件")
            return

        # 获取选中的第一行的文件名
        row = selected[0].row()
        filename = self.table.item(row, 0).text()
        file_path = os.path.join(self.current_folder, filename)

        try:
            if os.name == "nt":  # Windows
                os.startfile(file_path)
            else:  # Mac and Linux
                opener = "open" if sys.platform == "darwin" else "xdg-open"
                subprocess.call([opener, file_path])
            self.lbl_status.setText(f"已打开文件: {filename}")
        except Exception as e:
            QMessageBox.warning(self, "打开文件失败", f"无法打开文件:\n{str(e)}")
            self.lbl_status.setText("打开文件失败")

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
        self.lbl_status.setText("已复制表格内容到剪贴板")

    def export_data(self):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"file_match_result_{timestamp}.xlsx"

            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "导出文件",
                default_name,
                "Excel Files (*.xlsx);;Excel 97-2003 (*.xls);;CSV Files (*.csv)",
            )

            if not file_path:
                return

            # 确保目录存在
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            data = []
            for row in range(self.table.rowCount()):
                filename = self.table.item(row, 0).text()
                matched = self.table.item(row, 1).text()
                code = self.table.item(row, 2).text() if matched == "是" else ""
                thirty_d = self.table.item(row, 3).text() if matched == "是" else ""
                detail = self.table.item(row, 4).text() if matched == "是" else ""

                if matched == "是":
                    data.append([filename, matched, code, thirty_d, detail])
                else:
                    data.append([filename, matched, "", "", ""])

            df = pd.DataFrame(
                data,
                columns=["文件名", "是否匹配成功", "Code", "30d", "命名规则"],
            )

            try:
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

                self.lbl_status.setText(f"已导出到: {file_path}")

                # 导出成功弹窗
                msg_box = QMessageBox(self)
                msg_box.setWindowTitle("导出成功")
                msg_box.setText(f"文件已成功导出到:\n{file_path}")
                msg_box.setStandardButtons(QMessageBox.Open | QMessageBox.Close)
                msg_box.setDefaultButton(QMessageBox.Close)

                ret = msg_box.exec_()
                if ret == QMessageBox.Open:
                    try:
                        if os.name == "nt":  # Windows
                            os.startfile(file_path)
                        else:  # Mac and Linux
                            opener = "open" if sys.platform == "darwin" else "xdg-open"
                            subprocess.call([opener, file_path])
                    except Exception as e:
                        QMessageBox.warning(
                            self, "打开文件失败", f"无法打开文件:\n{str(e)}"
                        )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "导出失败",
                    f"导出文件时发生错误:\n{str(e)}\n"
                    "请检查文件路径是否有效且具有写入权限",
                )
                self.lbl_status.setText("导出失败")
        except Exception as e:
            QMessageBox.critical(self, "软件产生异常,请联系软件作者解决")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileMatcherGUI()
    window.show()
    sys.exit(app.exec_())
