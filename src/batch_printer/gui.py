import os
import sys
import csv
import subprocess
import win32print
import win32api
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QGroupBox, QCheckBox, QRadioButton, QButtonGroup,
    QProgressBar, QStatusBar, QHeaderView, QAbstractItemView,
    QMessageBox, QSplitter, QFrame, QLineEdit, QSpinBox
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt5.QtGui import QIcon, QColor, QFont, QPixmap


class PrintWorker(QThread):
    """打印工作线程"""
    progress_updated = pyqtSignal(int, str, str)  # row, status, message
    finished = pyqtSignal()
    log_print_result = pyqtSignal(str, str, bool, int, str, str, str)  # file_name, printer, duplex, copies, result, page_range, orientation
    
    def __init__(self, print_queue, printer_name, print_settings):
        super().__init__()
        self.print_queue = print_queue
        self.printer_name = printer_name
        self.print_settings = print_settings
        self.is_paused = False
        self.is_stopped = False
    
    def run(self):
        """执行打印任务"""
        for queue_index, (original_index, file_info) in enumerate(self.print_queue):
            if self.is_stopped:
                break
                
            # 检查是否暂停
            while self.is_paused and not self.is_stopped:
                time.sleep(0.1)
            
            if self.is_stopped:
                break
            
            try:
                self.progress_updated.emit(original_index, "正在打印", "正在处理...")
                
                # 打印文件，使用文件的独立设置
                self.print_file_with_settings(file_info)
                
                # 更新完成状态
                complete_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.progress_updated.emit(original_index, "打印完成", complete_time)
                
                # 发出日志记录信号
                self.log_print_result.emit(
                    file_info['name'], 
                    self.printer_name,
                    file_info['duplex'],
                    file_info['copies'],
                    "成功",
                    file_info['page_range'],
                    file_info['orientation']
                )
                
            except Exception as e:
                self.progress_updated.emit(original_index, "打印失败", str(e))
                # 发出日志记录信号
                self.log_print_result.emit(
                    file_info['name'], 
                    self.printer_name,
                    file_info['duplex'],
                    file_info['copies'],
                    "失败",
                    file_info['page_range'],
                    file_info['orientation']
                )
        
        self.finished.emit()
    
    def print_file_with_settings(self, file_info):
        """使用文件独立设置打印文件"""
        file_path = file_info['path']
        duplex = file_info['duplex']
        copies = file_info['copies']
        page_range = file_info.get('page_range', '')
        orientation = file_info.get('orientation', 'portrait')
        
        # 使用新的打印方法，传递所有参数
        self.print_file_with_devmode(file_path, duplex, copies, page_range, orientation)
    
    def print_file(self, file_path):
        """实际打印文件的方法"""
        try:
            import subprocess
            import os
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 首先尝试设置指定的打印机为默认打印机（临时）
            original_printer = None
            try:
                # 获取当前默认打印机
                original_printer = win32print.GetDefaultPrinter()
                
                # 如果指定了打印机且不是当前默认的，则临时设置为默认
                if self.printer_name and self.printer_name != original_printer:
                    win32print.SetDefaultPrinter(self.printer_name)
                    time.sleep(0.5)  # 等待设置生效
                    
            except Exception as printer_error:
                print(f"设置打印机时出错: {printer_error}")
            
            # 尝试打印文件
            success = False
            
            # 方法1: 使用ShellExecute进行打印
            try:
                result = win32api.ShellExecute(
                    0,                    # hwnd (父窗口句柄)
                    "print",              # 操作类型
                    file_path,           # 要打印的文件
                    None,                # 参数
                    ".",                 # 工作目录
                    0                    # 显示方式 (0=隐藏窗口)
                )
                
                # ShellExecute返回值大于32表示成功
                if result > 32:
                    success = True
                    time.sleep(2)  # 等待打印作业处理
                else:
                    raise Exception(f"ShellExecute错误代码: {result}")
                    
            except Exception as shell_error:
                print(f"ShellExecute失败: {shell_error}")
                
                # 方法2: 使用PowerShell打印
                try:
                    if file_path.lower().endswith('.pdf'):
                        # PDF文件特殊处理
                        cmd = f'Start-Process -FilePath "{file_path}" -Verb Print -WindowStyle Hidden -Wait'
                    else:
                        # 其他文件类型
                        cmd = f'Start-Process -FilePath "{file_path}" -Verb Print -WindowStyle Hidden'
                    
                    subprocess.run([
                        'powershell', '-ExecutionPolicy', 'Bypass', '-Command', cmd
                    ], check=True, timeout=60, capture_output=True)
                    
                    success = True
                    time.sleep(2)
                    
                except subprocess.TimeoutExpired:
                    # 超时也认为可能成功了
                    success = True
                    time.sleep(1)
                    
                except Exception as ps_error:
                    print(f"PowerShell打印失败: {ps_error}")
                    
                    # 方法3: 使用关联程序的默认操作
                    try:
                        os.startfile(file_path, "print")
                        success = True
                        time.sleep(3)  # 等待更长时间
                        
                    except Exception as startfile_error:
                        print(f"startfile打印失败: {startfile_error}")
                        raise Exception(f"所有打印方法都失败了")
            
            # 恢复原始默认打印机
            try:
                if original_printer and self.printer_name and self.printer_name != original_printer:
                    win32print.SetDefaultPrinter(original_printer)
            except Exception as restore_error:
                print(f"恢复打印机设置时出错: {restore_error}")
            
            if not success:
                raise Exception("打印失败，未知错误")
                
        except Exception as e:
            raise Exception(f"打印失败: {str(e)}")
    
    def print_file_with_devmode(self, file_path, duplex, copies, page_range, orientation):
        """使用DEVMODE结构设置打印参数进行打印"""
        try:
            import win32con
            import pywintypes
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                raise Exception(f"文件不存在: {file_path}")
            
            # 获取打印机句柄
            hprinter = win32print.OpenPrinter(self.printer_name)
            
            try:
                # 获取打印机的默认DEVMODE
                devmode = win32print.GetPrinter(hprinter, 2)['pDevMode']
                if devmode is None:
                    # 如果无法获取DEVMODE，创建一个新的
                    devmode = pywintypes.DEVMODEType()
                    devmode.DeviceName = self.printer_name
                
                # 设置打印参数
                devmode.Fields = 0
                
                # 设置份数
                if copies > 1:
                    devmode.Copies = copies
                    devmode.Fields |= win32con.DM_COPIES
                
                # 设置双面打印
                if duplex:
                    devmode.Duplex = win32con.DMDUP_VERTICAL  # 长边翻转
                    devmode.Fields |= win32con.DM_DUPLEX
                else:
                    devmode.Duplex = win32con.DMDUP_SIMPLEX  # 单面
                    devmode.Fields |= win32con.DM_DUPLEX
                
                # 设置页面方向
                if orientation == 'landscape':
                    devmode.Orientation = win32con.DMORIENT_LANDSCAPE
                else:
                    devmode.Orientation = win32con.DMORIENT_PORTRAIT
                devmode.Fields |= win32con.DM_ORIENTATION
                
                # 使用修改后的DEVMODE设置打印机
                win32print.DocumentProperties(0, hprinter, self.printer_name, devmode, devmode, win32con.DM_IN_BUFFER | win32con.DM_OUT_BUFFER)
                
                # 执行打印
                success = self.execute_print_with_settings(file_path, devmode)
                
                if not success:
                    raise Exception("打印失败")
                
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            # 如果使用DEVMODE失败，回退到简单方法
            print(f"DEVMODE打印失败，回退到简单方法: {e}")
            self.print_file_simple_with_settings(file_path, duplex, copies, page_range, orientation)
    
    def execute_print_with_settings(self, file_path, devmode):
        """执行带设置的打印"""
        try:
            # 方法1: 尝试使用Word COM对象进行打印（如果是Word文档）
            if file_path.lower().endswith(('.doc', '.docx')):
                return self.print_with_word_com(file_path, devmode)
            
            # 方法2: 尝试使用Excel COM对象进行打印（如果是Excel文档）
            elif file_path.lower().endswith(('.xls', '.xlsx')):
                return self.print_with_excel_com(file_path, devmode)
            
            # 方法3: 尝试使用Adobe Reader COM对象进行打印（如果是PDF文档）
            elif file_path.lower().endswith('.pdf'):
                return self.print_with_adobe_reader(file_path, devmode)
            
            # 方法4: 对于其他文件类型，使用系统关联程序
            else:
                return self.print_with_system_association(file_path, devmode)
                
        except Exception as e:
            print(f"带设置打印失败: {e}")
            return False
    
    def print_with_word_com(self, file_path, devmode):
        """使用Word COM对象进行打印"""
        try:
            import win32com.client
            
            word = win32com.client.Dispatch("Word.Application")
            word.Visible = False
            
            try:
                doc = word.Documents.Open(file_path, ReadOnly=True)
                
                # 设置打印机
                word.ActivePrinter = self.printer_name
                
                # 打印文档
                doc.PrintOut(
                    Copies=devmode.Copies if hasattr(devmode, 'Copies') else 1,
                    ManualDuplexPrint=not devmode.Duplex if hasattr(devmode, 'Duplex') else False
                )
                
                doc.Close(False)
                return True
                
            finally:
                word.Quit()
                
        except Exception as e:
            print(f"Word COM打印失败: {e}")
            return False
    
    def print_with_excel_com(self, file_path, devmode):
        """使用Excel COM对象进行打印"""
        try:
            import win32com.client
            
            excel = win32com.client.Dispatch("Excel.Application")
            excel.Visible = False
            excel.DisplayAlerts = False
            
            try:
                workbook = excel.Workbooks.Open(file_path, ReadOnly=True)
                worksheet = workbook.ActiveSheet
                
                # 设置打印机
                excel.ActivePrinter = self.printer_name
                
                # 打印工作表
                worksheet.PrintOut(
                    Copies=devmode.Copies if hasattr(devmode, 'Copies') else 1
                )
                
                workbook.Close(False)
                return True
                
            finally:
                excel.Quit()
                
        except Exception as e:
            print(f"Excel COM打印失败: {e}")
            return False
    
    def print_with_adobe_reader(self, file_path, devmode):
        """使用Adobe Reader进行PDF打印"""
        try:
            # 尝试多种方法打印PDF
            
            # 方法1: 使用Adobe Reader命令行
            try:
                import subprocess
                
                # 查找Adobe Reader可执行文件
                adobe_paths = [
                    r"C:\Program Files\Adobe\Acrobat DC\Acrobat\Acrobat.exe",
                    r"C:\Program Files (x86)\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe",
                    r"C:\Program Files\Adobe\Acrobat Reader DC\Reader\AcroRd32.exe"
                ]
                
                adobe_exe = None
                for path in adobe_paths:
                    if os.path.exists(path):
                        adobe_exe = path
                        break
                
                if adobe_exe:
                    # 构建命令行参数
                    cmd = [
                        adobe_exe,
                        "/t",  # 打印文档
                        file_path,
                        self.printer_name
                    ]
                    
                    subprocess.run(cmd, timeout=30)
                    time.sleep(2)  # 等待打印作业开始
                    return True
                    
            except Exception as e:
                print(f"Adobe Reader命令行打印失败: {e}")
            
            # 方法2: 使用SumatraPDF（如果可用）
            try:
                sumatra_paths = [
                    r"C:\Program Files\SumatraPDF\SumatraPDF.exe",
                    r"C:\Program Files (x86)\SumatraPDF\SumatraPDF.exe"
                ]
                
                sumatra_exe = None
                for path in sumatra_paths:
                    if os.path.exists(path):
                        sumatra_exe = path
                        break
                
                if sumatra_exe:
                    cmd = [
                        sumatra_exe,
                        "-print-to",
                        self.printer_name,
                        file_path
                    ]
                    
                    subprocess.run(cmd, timeout=30)
                    time.sleep(2)
                    return True
                    
            except Exception as e:
                print(f"SumatraPDF打印失败: {e}")
            
            # 方法3: 回退到系统关联程序
            return self.print_with_system_association(file_path, devmode)
            
        except Exception as e:
            print(f"PDF打印失败: {e}")
            return False
    
    def print_with_system_association(self, file_path, devmode):
        """使用系统关联程序打印"""
        try:
            # 临时设置打印机为默认打印机
            original_printer = None
            try:
                original_printer = win32print.GetDefaultPrinter()
                if self.printer_name != original_printer:
                    win32print.SetDefaultPrinter(self.printer_name)
                    time.sleep(0.5)
            except:
                pass
            
            # 使用ShellExecute打印
            result = win32api.ShellExecute(
                0, "print", file_path, None, ".", 0
            )
            
            # 恢复原始默认打印机
            if original_printer and self.printer_name != original_printer:
                try:
                    win32print.SetDefaultPrinter(original_printer)
                except:
                    pass
            
            return result > 32
            
        except Exception as e:
            print(f"系统关联程序打印失败: {e}")
            return False
    
    def print_file_simple_with_settings(self, file_path, duplex, copies, page_range, orientation):
        """简单方法打印文件（回退方案）"""
        try:
            # 如果需要多份，重复打印
            for copy_num in range(copies):
                self.print_file(file_path)
                if copies > 1:
                    time.sleep(2)  # 多份之间延迟
            
        except Exception as e:
            raise Exception(f"简单打印失败: {str(e)}")
    
    def pause(self):
        """暂停打印"""
        self.is_paused = True
    
    def resume(self):
        """恢复打印"""
        self.is_paused = False
    
    def stop(self):
        """停止打印"""
        self.is_stopped = True


class BatchPrinterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("批量打印工具")
        self.setGeometry(100, 100, 1500, 1500)
        
        # 设置窗口图标
        self.setup_icon()
        
        # 初始化数据
        self.file_list = []  # 存储待打印文件列表
        self.print_worker = None  # 打印工作线程
        self.settings = QSettings("BatchPrinter", "Settings")  # 设置存储
        self.print_history = []  # 打印历史记录
        
        # 支持的文件类型
        self.supported_extensions = {
            '.pdf', '.doc', '.docx', '.txt', '.rtf', '.xls', '.xlsx', 
            '.ppt', '.pptx', '.jpg', '.jpeg', '.png', '.bmp', '.tiff'
        }
        
        self.init_ui()
        self.load_settings()
    
    def setup_icon(self):
        """设置窗口图标"""
        try:
            # 处理打包和开发两种模式
            base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.dirname(__file__)))
            icon_path = os.path.join(base_path, "resource", "打印机.png")
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))
        except Exception:
            pass
    
    def init_ui(self):
        """初始化用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 设置样式
        self.setup_styles()
        
        # 先创建状态栏（在其他组件之前）
        self.create_status_bar()
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 第一排：文件选择区域
        file_selection_area = self.create_file_selection_area()
        main_layout.addWidget(file_selection_area)
        
        # 第二排：合并的设置参数区域
        settings_area = self.create_unified_settings_area()
        main_layout.addWidget(settings_area)
        
        # 第三排：打印控制区域
        control_area = self.create_print_control_area()
        main_layout.addWidget(control_area)
        
        # 第四排：文件列表和日志区域
        content_area = self.create_content_area()
        main_layout.addWidget(content_area)
        
        central_widget.setLayout(main_layout)
        
        # 启用拖拽
        self.setAcceptDrops(True)
    
    def setup_styles(self):
        """设置界面样式"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                color: #333333;
            }
            
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background-color: #1976D2;
            }
            
            QPushButton:pressed {
                background-color: #1565C0;
            }
            
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
                background-color: white;
                min-width: 150px;
            }
            
            QComboBox:focus {
                border-color: #4CAF50;
            }
            
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f9f9f9;
                selection-background-color: #1976D2;
                selection-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            
            QTableWidget::item {
                padding: 5px;
                border: none;
            }
            
            QTableWidget::item:selected {
                background-color: #1976D2;
                color: white;
            }
            
            QTableWidget::item:focus {
                background-color: #1976D2;
                color: white;
                outline: none;
            }
            
            QHeaderView::section {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
                padding: 8px;
                font-weight: bold;
            }
            
            QLabel {
                color: #333333;
                font-size: 14px;
            }
            
            QCheckBox, QRadioButton {
                font-size: 14px;
                color: #333333;
            }
            
            QProgressBar {
                border: 2px solid #ddd;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
    
    def create_file_selection_area(self):
        """创建文件选择区域（第一排）"""
        file_group = QGroupBox("文件选择")
        file_layout = QHBoxLayout()
        
        self.btn_add_files = QPushButton("📁 添加文件")
        self.btn_add_files.clicked.connect(self.add_files)
        
        self.btn_add_folder = QPushButton("📂 添加文件夹")
        self.btn_add_folder.clicked.connect(self.add_folder)
        
        self.btn_clear_list = QPushButton("🗑️ 清空列表")
        self.btn_clear_list.clicked.connect(self.clear_file_list)
        self.btn_clear_list.setStyleSheet("QPushButton { background-color: #f44336; }")
        
        file_layout.addWidget(self.btn_add_files)
        file_layout.addWidget(self.btn_add_folder)
        file_layout.addWidget(self.btn_clear_list)
        file_layout.addStretch()
        
        file_group.setLayout(file_layout)
        return file_group
    
    def create_unified_settings_area(self):
        """创建统一的设置参数区域（第二排）"""
        settings_group = QGroupBox("打印设置参数")
        main_settings_layout = QVBoxLayout()
        
        # 第一行：打印机选择
        printer_layout = QHBoxLayout()
        
        # 创建字体
        param_font = QFont()
        param_font.setPointSize(10)  # 增大字体
        
        label_printer = QLabel("打印机:")
        label_printer.setFont(param_font)
        printer_layout.addWidget(label_printer)
        
        self.combo_printer = QComboBox()
        self.combo_printer.setFont(param_font)
        self.load_printers()
        printer_layout.addWidget(self.combo_printer)
        
        self.btn_refresh_printers = QPushButton("🔄 刷新")
        self.btn_refresh_printers.setFont(param_font)
        self.btn_refresh_printers.clicked.connect(self.load_printers)
        self.btn_refresh_printers.setMaximumWidth(80)
        printer_layout.addWidget(self.btn_refresh_printers)
        printer_layout.addStretch()
        
        # 第二行：打印参数设置
        params_layout = QHBoxLayout()
        
        # 创建字体
        param_font = QFont()
        param_font.setPointSize(10)  # 增大字体
        
        # 打印方式
        label_duplex = QLabel("打印方式:")
        label_duplex.setFont(param_font)
        params_layout.addWidget(label_duplex)
        
        self.radio_simplex = QRadioButton("单面")
        self.radio_simplex.setFont(param_font)
        self.radio_duplex = QRadioButton("双面")
        self.radio_duplex.setFont(param_font)
        self.radio_simplex.setChecked(True)
        
        self.duplex_group = QButtonGroup()
        self.duplex_group.addButton(self.radio_simplex, 0)
        self.duplex_group.addButton(self.radio_duplex, 1)
        
        params_layout.addWidget(self.radio_simplex)
        params_layout.addWidget(self.radio_duplex)
        
        # 分隔线
        separator1 = QLabel("|")
        separator1.setFont(param_font)
        params_layout.addWidget(separator1)
        
        # 份数
        label_copies = QLabel("份数:")
        label_copies.setFont(param_font)
        params_layout.addWidget(label_copies)
        
        self.spin_copies = QSpinBox()
        self.spin_copies.setFont(param_font)
        self.spin_copies.setMinimum(1)
        self.spin_copies.setMaximum(99)
        self.spin_copies.setValue(1)
        self.spin_copies.setMaximumWidth(80)
        params_layout.addWidget(self.spin_copies)
        
        # 分隔线
        separator2 = QLabel("|")
        separator2.setFont(param_font)
        params_layout.addWidget(separator2)
        
        # 页码范围
        label_page = QLabel("页码:")
        label_page.setFont(param_font)
        params_layout.addWidget(label_page)
        
        self.edit_page_range = QLineEdit()
        self.edit_page_range.setFont(param_font)
        self.edit_page_range.setPlaceholderText("如: 1-5 或 2,4,6")
        self.edit_page_range.setMaximumWidth(120)
        params_layout.addWidget(self.edit_page_range)
        
        # 分隔线
        separator3 = QLabel("|")
        separator3.setFont(param_font)
        params_layout.addWidget(separator3)
        
        # 页面方向
        label_orientation = QLabel("方向:")
        label_orientation.setFont(param_font)
        params_layout.addWidget(label_orientation)
        
        self.combo_orientation = QComboBox()
        self.combo_orientation.setFont(param_font)
        self.combo_orientation.addItems(["纵向", "横向"])
        self.combo_orientation.setMaximumWidth(20)
        params_layout.addWidget(self.combo_orientation)
        
        # 分隔线
        separator4 = QLabel("|")
        separator4.setFont(param_font)
        params_layout.addWidget(separator4)
        
        # 批量应用按钮
        self.btn_apply_to_all = QPushButton("应用所有文件")
        self.btn_apply_to_all.setFont(param_font)
        self.btn_apply_to_all.setMaximumWidth(100)
        self.btn_apply_to_all.clicked.connect(self.apply_settings_to_all)
        params_layout.addWidget(self.btn_apply_to_all)
        
        params_layout.addStretch()
        
        # 第三行：应用模式选择
        mode_layout = QHBoxLayout()
        self.chk_apply_all = QCheckBox("应用所有文件 (统一使用上述设置)")
        self.chk_apply_all.setFont(param_font)
        self.chk_apply_all.stateChanged.connect(self.on_apply_all_changed)
        mode_layout.addWidget(self.chk_apply_all)
        
        mode_layout.addStretch()
        
        # 添加到主布局
        main_settings_layout.addLayout(printer_layout)
        main_settings_layout.addLayout(params_layout)
        main_settings_layout.addLayout(mode_layout)
        
        settings_group.setLayout(main_settings_layout)
        return settings_group
    
    def create_print_control_area(self):
        """创建打印控制区域（第三排）"""
        control_group = QGroupBox("打印控制")
        control_layout = QHBoxLayout()
        
        self.btn_start_print = QPushButton("▶️ 开始打印")
        self.btn_start_print.clicked.connect(self.start_printing)
        self.btn_start_print.setEnabled(False)
        # 设置开始打印按钮为绿色
        self.btn_start_print.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50 !important;
                color: white !important;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover:enabled {
                background-color: #45a049 !important;
            }
            QPushButton:pressed:enabled {
                background-color: #3d8b40 !important;
            }
            QPushButton:disabled {
                background-color: #A8D8A8 !important;
                color: #6B9B6B !important;
                border: 2px solid #cccccc;
            }
        """)
        
        self.btn_pause_print = QPushButton("⏸️ 暂停打印")
        self.btn_pause_print.clicked.connect(self.pause_printing)
        self.btn_pause_print.setEnabled(False)
        
        self.btn_stop_print = QPushButton("⏹️ 停止打印")
        self.btn_stop_print.clicked.connect(self.stop_printing)
        self.btn_stop_print.setEnabled(False)
        self.btn_stop_print.setStyleSheet("""
            QPushButton {
                background-color: #f44336 !important;
                color: white !important;
                font-weight: bold;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover:enabled {
                background-color: #d32f2f !important;
            }
            QPushButton:pressed:enabled {
                background-color: #b71c1c !important;
            }
            QPushButton:disabled {
                background-color: #ffcccc !important;
                color: #999999 !important;
                border: 2px solid #cccccc;
            }
        """)
        
        control_layout.addWidget(self.btn_start_print)
        control_layout.addWidget(self.btn_pause_print)
        control_layout.addWidget(self.btn_stop_print)
        control_layout.addStretch()
        
        control_group.setLayout(control_layout)
        return control_group
    
    def create_content_area(self):
        """创建内容区域（第四排）- 文件列表和日志"""
        return self.create_right_area()  # 重用现有的方法
    

    
    def create_right_area(self):
        """创建右侧区域（文件列表 + 日志区域）"""
        right_frame = QFrame()
        right_layout = QVBoxLayout()
        
        # 创建分隔器
        splitter = QSplitter(Qt.Vertical)
        
        # 创建文件列表区域
        file_area = self.create_file_area()
        
        # 创建日志区域
        log_area = self.create_log_area()
        
        # 添加到分隔器
        splitter.addWidget(file_area)
        splitter.addWidget(log_area)
        splitter.setSizes([400, 200])  # 文件列表400，日志200
        
        right_layout.addWidget(splitter)
        right_frame.setLayout(right_layout)
        
        return right_frame
    
    def create_file_area(self):
        """创建文件列表区域"""
        file_frame = QFrame()
        file_layout = QVBoxLayout()
        
                # 先创建表头全选复选框
        self.header_checkbox = QCheckBox()
        self.header_checkbox.stateChanged.connect(self.on_header_checkbox_changed)
        
        # 文件列表标题和控制
        title_layout = QHBoxLayout()
        self.lbl_file_count = QLabel("文件列表 (0 个文件)")
        self.lbl_file_count.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        title_layout.addWidget(self.lbl_file_count)
        
        # 全选控制
        title_layout.addWidget(QLabel("全选:"))
        title_layout.addWidget(self.header_checkbox)
        
        title_layout.addStretch()
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        title_layout.addWidget(self.progress_bar)
        
        file_layout.addLayout(title_layout)
        

        
        # 文件表格
        self.table_files = QTableWidget()
        self.table_files.setColumnCount(10)
        self.table_files.setHorizontalHeaderLabels([
            "", "文件名", "文件路径", "文件大小", "打印方式", "份数", "页码范围", "页面方向", "打印状态", "操作"
        ])

        
        # 设置表格属性
        self.table_files.setAlternatingRowColors(True)
        self.table_files.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_files.setSelectionMode(QAbstractItemView.SingleSelection)
        
        # 设置列宽
        header = self.table_files.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)           # 选择
        header.setSectionResizeMode(1, QHeaderView.Interactive)       # 文件名
        header.setSectionResizeMode(2, QHeaderView.Stretch)          # 文件路径
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # 文件大小
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # 打印方式
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # 份数
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # 页码范围
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # 页面方向
        header.setSectionResizeMode(8, QHeaderView.ResizeToContents) # 打印状态
        header.setSectionResizeMode(9, QHeaderView.ResizeToContents) # 操作
        
        # 设置初始列宽
        self.table_files.setColumnWidth(0, 50)
        self.table_files.setColumnWidth(1, 150)
        
        file_layout.addWidget(self.table_files)
        file_frame.setLayout(file_layout)
        
        return file_frame
    
    def create_log_area(self):
        """创建日志区域"""
        log_frame = QFrame()
        log_layout = QVBoxLayout()
        
        # 日志标题
        log_title = QLabel("打印日志")
        log_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        log_layout.addWidget(log_title)
        
        # 日志表格
        self.table_log = QTableWidget()
        self.table_log.setColumnCount(8)
        self.table_log.setHorizontalHeaderLabels([
            "时间", "文件名", "打印机", "打印方式", "份数", "页码范围", "页面方向", "结果"
        ])
        
        # 设置表格属性
        self.table_log.setAlternatingRowColors(True)
        self.table_log.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table_log.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table_log.setSortingEnabled(True)
        
        # 设置列宽
        log_header = self.table_log.horizontalHeader()
        log_header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # 时间
        log_header.setSectionResizeMode(1, QHeaderView.Stretch)          # 文件名
        log_header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # 打印机
        log_header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # 打印方式
        log_header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # 份数
        log_header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # 页码范围
        log_header.setSectionResizeMode(6, QHeaderView.ResizeToContents) # 页面方向
        log_header.setSectionResizeMode(7, QHeaderView.ResizeToContents) # 结果
        
        log_layout.addWidget(self.table_log)
        
        # 日志操作按钮
        log_btn_layout = QHBoxLayout()
        self.btn_clear_log = QPushButton("清空日志")
        self.btn_clear_log.clicked.connect(self.clear_log)
        self.btn_export_log = QPushButton("导出日志")
        self.btn_export_log.clicked.connect(self.export_log)
        
        log_btn_layout.addStretch()
        log_btn_layout.addWidget(self.btn_clear_log)
        log_btn_layout.addWidget(self.btn_export_log)
        
        log_layout.addLayout(log_btn_layout)
        log_frame.setLayout(log_layout)
        
        return log_frame
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪 - 请添加要打印的文件")
    
    def load_printers(self):
        """加载系统打印机列表"""
        try:
            self.combo_printer.clear()
            
            # 获取系统打印机列表
            printers = [printer[2] for printer in win32print.EnumPrinters(2)]
            
            # 获取默认打印机
            try:
                default_printer = win32print.GetDefaultPrinter()
            except:
                default_printer = None
            
            # 添加打印机到下拉列表
            for printer in printers:
                self.combo_printer.addItem(printer)
                
            # 设置默认打印机为选中项
            if default_printer and default_printer in printers:
                index = printers.index(default_printer)
                self.combo_printer.setCurrentIndex(index)
            
            # 连接打印机选择变化事件（延迟连接，等UI初始化完成）
            QTimer.singleShot(100, lambda: self.setup_printer_connection())
                
            self.status_bar.showMessage(f"找到 {len(printers)} 台打印机")
            
        except Exception as e:
            QMessageBox.warning(self, "警告", f"无法获取打印机列表: {str(e)}")
            self.status_bar.showMessage("无法获取打印机列表")
    
    def setup_printer_connection(self):
        """设置打印机连接（延迟执行，确保UI初始化完成）"""
        # 连接打印机选择变化事件
        self.combo_printer.currentTextChanged.connect(self.on_printer_changed)
        
        # 如果有打印机，检查当前选中的打印机能力
        if self.combo_printer.count() > 0:
            self.on_printer_changed(self.combo_printer.currentText())
    
    def on_printer_changed(self, printer_name):
        """打印机选择改变时检查打印机能力"""
        if not printer_name:
            return
            
        try:
            # 获取打印机能力
            capabilities = self.get_printer_capabilities(printer_name)
            
            # 更新UI根据打印机能力
            self.update_ui_based_on_printer_capabilities(capabilities)
            
            # 显示打印机信息
            duplex_support = "支持" if capabilities.get('duplex_support', False) else "不支持"
            self.status_bar.showMessage(f"打印机: {printer_name} | 双面打印: {duplex_support}")
            
        except Exception as e:
            print(f"检查打印机能力时出错: {e}")
            self.status_bar.showMessage(f"无法获取打印机 {printer_name} 的能力信息")
    
    def get_printer_capabilities(self, printer_name):
        """获取打印机能力"""
        capabilities = {
            'duplex_support': False,
            'duplex_modes': [],
            'paper_sizes': [],
            'orientations': ['portrait', 'landscape'],
            'resolutions': []
        }
        
        try:
            import win32con
            
            # 获取打印机句柄
            hprinter = win32print.OpenPrinter(printer_name)
            
            try:
                # 获取设备能力
                # 检查是否支持双面打印
                duplex_caps = win32print.DeviceCapabilities(
                    printer_name, None, win32con.DC_DUPLEX
                )
                
                if duplex_caps and duplex_caps != 0:
                    capabilities['duplex_support'] = True
                    capabilities['duplex_modes'] = ['单面', '双面长边翻转', '双面短边翻转']
                else:
                    capabilities['duplex_support'] = False
                    capabilities['duplex_modes'] = ['单面']
                
                # 获取支持的纸张大小
                try:
                    paper_sizes = win32print.DeviceCapabilities(
                        printer_name, None, win32con.DC_PAPERS
                    )
                    if paper_sizes:
                        capabilities['paper_sizes'] = paper_sizes
                except:
                    pass
                
                # 获取打印分辨率
                try:
                    resolutions = win32print.DeviceCapabilities(
                        printer_name, None, win32con.DC_ENUMRESOLUTIONS
                    )
                    if resolutions:
                        capabilities['resolutions'] = resolutions
                except:
                    pass
                    
            finally:
                win32print.ClosePrinter(hprinter)
                
        except Exception as e:
            print(f"获取打印机能力失败: {e}")
            # 如果无法获取具体能力，设置默认值
            capabilities['duplex_support'] = True  # 假设支持双面打印
            capabilities['duplex_modes'] = ['单面', '双面']
        
        return capabilities
    
    def update_ui_based_on_printer_capabilities(self, capabilities):
        """根据打印机能力更新UI"""
        # 更新双面打印选项
        duplex_support = capabilities.get('duplex_support', False)
        
        # 启用或禁用双面打印选项
        self.radio_duplex.setEnabled(duplex_support)
        
        if not duplex_support:
            # 如果不支持双面打印，强制选择单面
            self.radio_simplex.setChecked(True)
            self.radio_duplex.setChecked(False)
            self.radio_duplex.setToolTip("当前打印机不支持双面打印")
        else:
            self.radio_duplex.setToolTip("双面打印（长边翻转）")
            
        # 更新已有文件的双面打印控件
        for row in range(self.table_files.rowCount()):
            duplex_combo = self.table_files.cellWidget(row, 4)
            if duplex_combo:
                duplex_combo.setEnabled(duplex_support)
                if not duplex_support:
                    duplex_combo.setCurrentText("单面")
    
    def add_files(self):
        """添加文件到打印列表"""
        file_filter = "所有支持的文件 (*.pdf *.doc *.docx *.txt *.rtf *.xls *.xlsx *.ppt *.pptx *.jpg *.jpeg *.png *.bmp *.tiff);;PDF文件 (*.pdf);;Word文档 (*.doc *.docx);;Excel文件 (*.xls *.xlsx);;PowerPoint文件 (*.ppt *.pptx);;图片文件 (*.jpg *.jpeg *.png *.bmp *.tiff);;文本文件 (*.txt *.rtf);;所有文件 (*.*)"
        
        files, _ = QFileDialog.getOpenFileNames(
            self, "选择要打印的文件", "", file_filter
        )
        
        if files:
            # 检查文件数量限制
            current_count = len(self.file_list)
            new_files_count = len(files)
            total_count = current_count + new_files_count
            
            if total_count > 50:
                QMessageBox.warning(
                    self, "文件数量限制", 
                    f"不能添加 {new_files_count} 个文件！\n\n"
                    f"当前列表已有 {current_count} 个文件，\n"
                    f"添加后将有 {total_count} 个文件，\n"
                    f"超过了最大限制 50 个文件。\n\n"
                    f"请减少选择的文件数量或先清空部分文件。"
                )
                return
            
            added_count = 0
            for file_path in files:
                if self.add_file_to_list(file_path):
                    added_count += 1
            
            self.update_file_count()
            self.status_bar.showMessage(f"成功添加 {added_count} 个文件")
    
    def add_folder(self):
        """添加文件夹中的所有支持文件"""
        folder = QFileDialog.getExistingDirectory(self, "选择包含待打印文件的文件夹")
        
        if folder:
            current_count = len(self.file_list)
            folder_path = Path(folder)
            
            # 先收集文件夹中的所有支持文件
            found_files = []
            for file_path in folder_path.rglob("*"):
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    # 检查文件是否已存在
                    file_str = str(file_path)
                    if not any(existing['path'] == file_str for existing in self.file_list):
                        found_files.append(file_str)
            
            if not found_files:
                QMessageBox.information(self, "提示", "文件夹中没有找到新的支持文件")
                return
            
            # 检查文件数量限制
            new_files_count = len(found_files)
            total_count = current_count + new_files_count
            
            if total_count > 50:
                QMessageBox.warning(
                    self, "文件数量限制", 
                    f"不能添加文件夹中的 {new_files_count} 个文件！\n\n"
                    f"当前列表已有 {current_count} 个文件，\n"
                    f"添加后将有 {total_count} 个文件，\n"
                    f"超过了最大限制 50 个文件。\n\n"
                    f"请先清空部分文件后再添加文件夹。"
                )
                return
            
            # 添加文件
            added_count = 0
            for file_path in found_files:
                if self.add_file_to_list(file_path):
                    added_count += 1
            
            self.update_file_count()
            self.status_bar.showMessage(f"从文件夹中添加了 {added_count} 个文件")
    
    def add_file_to_list(self, file_path):
        """添加单个文件到列表"""
        # 检查文件是否已存在
        for existing_file in self.file_list:
            if existing_file['path'] == file_path:
                return False
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return False
        
        # 获取文件信息
        file_info = {
            'path': file_path,
            'name': os.path.basename(file_path),
            'size': os.path.getsize(file_path),
            'status': '未打印',
            'selected': True,  # 默认选中
            'duplex': self.radio_duplex.isChecked(),  # 从全局设置获取
            'copies': self.spin_copies.value(),  # 从全局设置获取
            'page_range': '',  # 页码范围，空表示全部页
            'orientation': 'portrait',  # 页面方向，portrait=纵向，landscape=横向
            'complete_time': ''
        }
        
        self.file_list.append(file_info)
        self.add_file_to_table(file_info)
        
        # 更新开始打印按钮状态
        self.btn_start_print.setEnabled(len(self.file_list) > 0)
        
        return True
    
    def add_file_to_table(self, file_info):
        """添加文件到表格显示"""
        row = self.table_files.rowCount()
        self.table_files.insertRow(row)
        
        # 1. 选择复选框
        checkbox = QCheckBox()
        checkbox.setChecked(file_info['selected'])
        checkbox.stateChanged.connect(lambda state, r=row: self.on_file_selection_changed(r, state))
        self.table_files.setCellWidget(row, 0, checkbox)
        
        # 2. 文件名
        name_item = QTableWidgetItem(file_info['name'])
        name_item.setToolTip(file_info['path'])
        self.table_files.setItem(row, 1, name_item)
        
        # 3. 文件路径
        path_item = QTableWidgetItem(file_info['path'])
        self.table_files.setItem(row, 2, path_item)
        
        # 4. 文件大小
        size_item = QTableWidgetItem(self.format_file_size(file_info['size']))
        size_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.table_files.setItem(row, 3, size_item)
        
        # 5. 打印方式下拉框
        duplex_combo = QComboBox()
        duplex_combo.addItems(["单面", "双面"])
        duplex_combo.setCurrentText("双面" if file_info['duplex'] else "单面")
        duplex_combo.currentTextChanged.connect(lambda text, r=row: self.on_duplex_changed(r, text))
        # 如果应用所有文件，则禁用
        if hasattr(self, 'chk_apply_all') and self.chk_apply_all.isChecked():
            duplex_combo.setEnabled(False)
        self.table_files.setCellWidget(row, 4, duplex_combo)
        
        # 6. 份数输入框
        copies_spin = QSpinBox()
        copies_spin.setMinimum(1)
        copies_spin.setMaximum(99)
        copies_spin.setValue(file_info['copies'])
        copies_spin.valueChanged.connect(lambda value, r=row: self.on_copies_changed(r, value))
        # 如果应用所有文件，则禁用
        if hasattr(self, 'chk_apply_all') and self.chk_apply_all.isChecked():
            copies_spin.setEnabled(False)
        self.table_files.setCellWidget(row, 5, copies_spin)
        
        # 7. 页码范围输入框
        page_range_edit = QLineEdit()
        page_range_edit.setText(file_info['page_range'])
        page_range_edit.setPlaceholderText("全部页")
        page_range_edit.textChanged.connect(lambda text, r=row: self.on_page_range_changed(r, text))
        # 如果应用所有文件，则禁用
        if hasattr(self, 'chk_apply_all') and self.chk_apply_all.isChecked():
            page_range_edit.setEnabled(False)
        self.table_files.setCellWidget(row, 6, page_range_edit)
        
        # 8. 页面方向下拉框
        orientation_combo = QComboBox()
        orientation_combo.addItems(["纵向", "横向"])
        orientation_combo.setCurrentText("纵向" if file_info['orientation'] == 'portrait' else "横向")
        orientation_combo.currentTextChanged.connect(lambda text, r=row: self.on_orientation_changed(r, text))
        # 如果应用所有文件，则禁用
        if hasattr(self, 'chk_apply_all') and self.chk_apply_all.isChecked():
            orientation_combo.setEnabled(False)
        self.table_files.setCellWidget(row, 7, orientation_combo)
        
        # 9. 打印状态
        status_item = QTableWidgetItem(file_info['status'])
        status_item.setTextAlignment(Qt.AlignCenter)
        self.table_files.setItem(row, 8, status_item)
        
        # 10. 操作按钮
        delete_btn = QPushButton("删除")
        delete_btn.setMaximumWidth(60)
        delete_btn.setStyleSheet("QPushButton { background-color: #f44336; color: white; }")
        delete_btn.clicked.connect(lambda checked, r=row: self.delete_file(r))
        self.table_files.setCellWidget(row, 9, delete_btn)
        
        # 设置状态颜色
        self.update_row_status_color(row, file_info['status'])
    
    def clear_file_list(self):
        """清空文件列表"""
        if self.file_list:
            reply = QMessageBox.question(
                self, "确认清空", 
                f"确定要清空列表中的 {len(self.file_list)} 个文件吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.file_list.clear()
                self.table_files.setRowCount(0)
                self.update_file_count()
                self.btn_start_print.setEnabled(False)
                self.status_bar.showMessage("文件列表已清空")
    
    def update_file_count(self):
        """更新文件数量显示"""
        count = len(self.file_list)
        self.lbl_file_count.setText(f"文件列表 ({count}/50 个文件)")
        
        # 如果接近限制，改变颜色提醒
        if count >= 45:
            self.lbl_file_count.setStyleSheet("QLabel { color: red; font-weight: bold; }")
        elif count >= 35:
            self.lbl_file_count.setStyleSheet("QLabel { color: orange; font-weight: bold; }")
        else:
            self.lbl_file_count.setStyleSheet("QLabel { color: #333333; font-size: 12px; font-weight: bold; }")
        
        # 更新表头复选框状态
        if hasattr(self, 'header_checkbox'):
            self.update_header_checkbox_state()
        
        # 更新开始打印按钮状态
        if hasattr(self, 'btn_start_print'):
            self.update_start_button_state()
    
    def format_file_size(self, size_bytes):
        """格式化文件大小显示"""
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        
        return f"{size_bytes:.1f} {size_names[i]}"
    
    def update_row_status_color(self, row, status):
        """更新行的状态颜色"""
        colors = {
            '未打印': QColor(240, 240, 240),
            '正在打印': QColor(255, 248, 220),
            '打印完成': QColor(220, 255, 220),
            '打印失败': QColor(255, 220, 220)
        }
        
        color = colors.get(status, QColor(255, 255, 255))
        
        # 只更新有QTableWidgetItem的列（不是widget的列）
        text_columns = [1, 2, 3, 8]  # 文件名、路径、大小、状态
        for col in text_columns:
            item = self.table_files.item(row, col)
            if item:
                item.setBackground(color)
    
    def start_printing(self):
        """开始打印任务"""
        if not self.file_list:
            QMessageBox.warning(self, "警告", "请先添加要打印的文件")
            return
        
        if self.combo_printer.currentText() == "":
            QMessageBox.warning(self, "警告", "请选择打印机")
            return
        
        # 获取选中的文件
        selected_files = self.get_selected_files()
        if not selected_files:
            # 如果没有选中任何文件，则打印全部
            selected_files = [(i, file_info) for i, file_info in enumerate(self.file_list)]
            QMessageBox.information(self, "提示", "未选择文件，将打印全部文件")
        
        # 重置选中文件的状态
        for i, file_info in selected_files:
            file_info['status'] = '未打印'
            self.update_table_row_status(i, '未打印', '')
        
        # 创建并启动打印线程
        self.print_worker = PrintWorker(
            selected_files, 
            self.combo_printer.currentText(),
            None  # 不使用全局设置，每个文件有自己的设置
        )
        self.print_worker.progress_updated.connect(self.on_print_progress)
        self.print_worker.finished.connect(self.on_print_finished)
        self.print_worker.log_print_result.connect(self.add_to_log)
        
        # 更新UI状态
        self.btn_start_print.setEnabled(False)
        self.btn_pause_print.setEnabled(True)
        self.btn_stop_print.setEnabled(True)
        
        # 显示进度条
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(selected_files))
        self.progress_bar.setValue(0)
        
        # 启动打印
        self.print_worker.start()
        self.status_bar.showMessage(f"正在打印 {len(selected_files)} 个文件...")
    
    def on_header_checkbox_changed(self, state):
        """表头复选框状态改变"""
        checked = state == Qt.Checked
        for row in range(self.table_files.rowCount()):
            checkbox = self.table_files.cellWidget(row, 0)
            if checkbox:
                # 临时断开信号避免递归
                checkbox.blockSignals(True)
                checkbox.setChecked(checked)
                # 更新数据
                if row < len(self.file_list):
                    self.file_list[row]['selected'] = checked
                checkbox.blockSignals(False)
        
        # 更新开始打印按钮状态
        self.update_start_button_state()
        
        # 更新状态栏
        if checked:
            self.status_bar.showMessage(f"已全选 {self.table_files.rowCount()} 个文件")
        else:
            self.status_bar.showMessage("已取消选择所有文件")
    
    def select_all_files(self):
        """全选文件"""
        self.header_checkbox.setChecked(True)
    
    def select_none_files(self):
        """取消全选"""
        self.header_checkbox.setChecked(False)
    
    def update_start_button_state(self):
        """更新开始打印按钮的状态"""
        has_selected = any(
            self.file_list[i]['selected'] 
            for i in range(min(len(self.file_list), self.table_files.rowCount()))
        )
        has_printer = self.combo_printer.count() > 0
        self.btn_start_print.setEnabled(has_selected and has_printer)
    
    def on_file_selection_changed(self, row, state):
        """文件选择状态改变"""
        if row < len(self.file_list):
            self.file_list[row]['selected'] = (state == Qt.Checked)
            
            # 更新表头复选框状态
            self.update_header_checkbox_state()
            
            # 更新开始打印按钮状态
            self.update_start_button_state()
    
    def update_header_checkbox_state(self):
        """更新表头复选框状态"""
        if self.table_files.rowCount() == 0:
            self.header_checkbox.setChecked(False)
            return
        
        selected_count = 0
        total_count = self.table_files.rowCount()
        
        for row in range(total_count):
            checkbox = self.table_files.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                selected_count += 1
        
        # 临时断开信号避免递归
        self.header_checkbox.blockSignals(True)
        
        if selected_count == 0:
            self.header_checkbox.setChecked(False)
        elif selected_count == total_count:
            self.header_checkbox.setChecked(True)
        else:
            # 部分选中状态，设为未选中但可以添加视觉提示
            self.header_checkbox.setChecked(False)
        
        self.header_checkbox.blockSignals(False)
    
    def on_duplex_changed(self, row, text):
        """打印方式改变"""
        if row < len(self.file_list):
            self.file_list[row]['duplex'] = (text == "双面")
    
    def on_copies_changed(self, row, value):
        """份数改变"""
        if row < len(self.file_list):
            self.file_list[row]['copies'] = value
    
    def on_page_range_changed(self, row, text):
        """页码范围改变"""
        if row < len(self.file_list):
            self.file_list[row]['page_range'] = text
    
    def on_orientation_changed(self, row, text):
        """页面方向改变"""
        if row < len(self.file_list):
            self.file_list[row]['orientation'] = 'portrait' if text == '纵向' else 'landscape'
    
    def on_apply_all_changed(self, state):
        """应用所有文件设置改变"""
        apply_all = (state == Qt.Checked)
        
        # 更新表格中所有文件的设置控件状态
        for row in range(self.table_files.rowCount()):
            # 获取打印方式下拉框
            duplex_combo = self.table_files.cellWidget(row, 4)
            if duplex_combo:
                duplex_combo.setEnabled(not apply_all)
                if apply_all:
                    # 应用全局设置
                    global_duplex = "双面" if self.radio_duplex.isChecked() else "单面"
                    duplex_combo.setCurrentText(global_duplex)
                    if row < len(self.file_list):
                        self.file_list[row]['duplex'] = self.radio_duplex.isChecked()
            
            # 获取份数输入框
            copies_spin = self.table_files.cellWidget(row, 5)
            if copies_spin:
                copies_spin.setEnabled(not apply_all)
                if apply_all:
                    # 应用全局设置
                    copies_spin.setValue(self.spin_copies.value())
                    if row < len(self.file_list):
                        self.file_list[row]['copies'] = self.spin_copies.value()
            
            # 获取页码范围输入框
            page_range_edit = self.table_files.cellWidget(row, 6)
            if page_range_edit:
                page_range_edit.setEnabled(not apply_all)
            
            # 获取页面方向下拉框
            orientation_combo = self.table_files.cellWidget(row, 7)
            if orientation_combo:
                orientation_combo.setEnabled(not apply_all)
        

        
        # 当应用全部时，监听全局设置的改变
        if apply_all:
            self.radio_simplex.toggled.connect(self.update_all_files_settings)
            self.radio_duplex.toggled.connect(self.update_all_files_settings)
            self.spin_copies.valueChanged.connect(self.update_all_files_settings)
        else:
            # 断开连接
            try:
                self.radio_simplex.toggled.disconnect(self.update_all_files_settings)
                self.radio_duplex.toggled.disconnect(self.update_all_files_settings)
                self.spin_copies.valueChanged.disconnect(self.update_all_files_settings)
            except:
                pass
    
    def update_all_files_settings(self):
        """更新所有文件的设置（当应用全部时）"""
        if not self.chk_apply_all.isChecked():
            return
        
        global_duplex_text = "双面" if self.radio_duplex.isChecked() else "单面"
        global_duplex_bool = self.radio_duplex.isChecked()
        global_copies = self.spin_copies.value()
        
        for row in range(self.table_files.rowCount()):
            # 更新打印方式下拉框
            duplex_combo = self.table_files.cellWidget(row, 4)
            if duplex_combo:
                duplex_combo.setCurrentText(global_duplex_text)
            
            # 更新份数输入框
            copies_spin = self.table_files.cellWidget(row, 5)
            if copies_spin:
                copies_spin.setValue(global_copies)
            
            # 更新数据
            if row < len(self.file_list):
                self.file_list[row]['duplex'] = global_duplex_bool
                self.file_list[row]['copies'] = global_copies
    
    def delete_file(self, row):
        """删除文件"""
        if row >= len(self.file_list):
            return
        
        # 检查是否正在打印
        if self.file_list[row]['status'] == '正在打印':
            QMessageBox.warning(self, "警告", "无法删除正在打印的文件")
            return
        
        file_name = self.file_list[row]['name']
        reply = QMessageBox.question(
            self, "确认删除", 
            f"确定要删除文件 '{file_name}' 吗？",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 从列表中删除
            del self.file_list[row]
            
            # 从表格中删除
            self.table_files.removeRow(row)
            
            # 更新文件计数
            self.update_file_count()
            
            # 更新按钮状态
            self.btn_start_print.setEnabled(len(self.file_list) > 0)
            
            self.status_bar.showMessage(f"已删除文件: {file_name}")
    
    def get_selected_files(self):
        """获取选中的文件列表"""
        selected_files = []
        for i, file_info in enumerate(self.file_list):
            if file_info['selected']:
                selected_files.append((i, file_info))
        return selected_files
    
    def add_to_log(self, file_name, printer, duplex, copies, result, page_range="", orientation="portrait"):
        """添加到日志"""
        
        log_entry = {
            'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'file_name': file_name,
            'printer': printer,
            'duplex': "双面" if duplex else "单面",
            'copies': copies,
            'page_range': page_range or "全部页",
            'orientation': "纵向" if orientation == 'portrait' else "横向",
            'result': result
        }
        
        self.print_history.append(log_entry)
        
        # 添加到日志表格
        row = self.table_log.rowCount()
        self.table_log.insertRow(row)
        
        self.table_log.setItem(row, 0, QTableWidgetItem(log_entry['time']))
        self.table_log.setItem(row, 1, QTableWidgetItem(log_entry['file_name']))
        self.table_log.setItem(row, 2, QTableWidgetItem(log_entry['printer']))
        self.table_log.setItem(row, 3, QTableWidgetItem(log_entry['duplex']))
        self.table_log.setItem(row, 4, QTableWidgetItem(str(log_entry['copies'])))
        self.table_log.setItem(row, 5, QTableWidgetItem(log_entry['page_range']))
        self.table_log.setItem(row, 6, QTableWidgetItem(log_entry['orientation']))
        
        result_item = QTableWidgetItem(log_entry['result'])
        if result == "成功":
            result_item.setBackground(QColor(220, 255, 220))
        elif result == "失败":
            result_item.setBackground(QColor(255, 220, 220))
        self.table_log.setItem(row, 7, result_item)
        
        # 滚动到最新记录
        self.table_log.scrollToBottom()
    
    def clear_log(self):
        """清空日志"""
        if self.print_history:
            reply = QMessageBox.question(
                self, "确认清空", 
                f"确定要清空 {len(self.print_history)} 条日志记录吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.print_history.clear()
                self.table_log.setRowCount(0)
                self.status_bar.showMessage("日志已清空")
    
    def export_log(self):
        """导出日志"""
        if not self.print_history:
            QMessageBox.information(self, "提示", "没有日志记录可以导出")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出日志", 
            f"打印日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "CSV 文件 (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['时间', '文件名', '打印机', '打印方式', '份数', '页码范围', '页面方向', '结果'])
                    
                    for log in self.print_history:
                        writer.writerow([
                            log['time'], log['file_name'], log['printer'],
                            log['duplex'], log['copies'], log['page_range'], 
                            log['orientation'], log['result']
                        ])
                
                QMessageBox.information(self, "成功", f"日志已导出到: {file_path}")
                self.status_bar.showMessage(f"日志已导出: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"导出日志失败: {str(e)}")
    
    def pause_printing(self):
        """暂停/恢复打印"""
        if self.print_worker:
            if self.print_worker.is_paused:
                self.print_worker.resume()
                self.btn_pause_print.setText("⏸️ 暂停打印")
                self.status_bar.showMessage("正在打印...")
            else:
                self.print_worker.pause()
                self.btn_pause_print.setText("▶️ 恢复打印")
                self.status_bar.showMessage("打印已暂停")
    
    def stop_printing(self):
        """停止打印"""
        if self.print_worker:
            self.print_worker.stop()
            self.print_worker.wait()  # 等待线程结束
            self.on_print_finished()
            self.status_bar.showMessage("打印已停止")
    
    def on_print_progress(self, row, status, message):
        """处理打印进度更新"""
        if row < len(self.file_list):
            self.file_list[row]['status'] = status
            if status == '打印完成':
                self.file_list[row]['complete_time'] = message
                self.progress_bar.setValue(self.progress_bar.value() + 1)
            
            self.update_table_row_status(row, status, message)
    
    def update_table_row_status(self, row, status, message):
        """更新表格行状态"""
        # 更新状态列（现在是第8列）
        status_item = self.table_files.item(row, 8)
        if status_item:
            status_item.setText(status)
        
        # 更新行颜色
        self.update_row_status_color(row, status)
        
        # 如果正在打印，禁用删除按钮
        delete_btn = self.table_files.cellWidget(row, 9)
        if delete_btn:
            delete_btn.setEnabled(status != '正在打印')
    
    def on_print_finished(self):
        """打印完成处理"""
        # 更新UI状态
        self.btn_start_print.setEnabled(True)
        self.btn_pause_print.setEnabled(False)
        self.btn_pause_print.setText("⏸️ 暂停打印")
        self.btn_stop_print.setEnabled(False)
        
        # 隐藏进度条
        self.progress_bar.setVisible(False)
        
        # 统计打印结果
        completed = sum(1 for f in self.file_list if f['status'] == '打印完成')
        failed = sum(1 for f in self.file_list if f['status'] == '打印失败')
        
        self.status_bar.showMessage(f"打印完成 - 成功: {completed}, 失败: {failed}")
        
        # 清理打印线程
        self.print_worker = None
    
    def load_settings(self):
        """加载设置"""
        try:
            # 加载打印设置
            duplex = self.settings.value("print/duplex", False, type=bool)
            copies = self.settings.value("print/copies", 1, type=int)
            apply_all = self.settings.value("print/apply_all", False, type=bool)
            
            self.radio_duplex.setChecked(duplex)
            self.radio_simplex.setChecked(not duplex)
            self.spin_copies.setValue(copies)
            self.chk_apply_all.setChecked(apply_all)
            
        except Exception as e:
            print(f"加载设置失败: {e}")
    
    def save_settings(self):
        """保存设置"""
        try:
            self.settings.setValue("print/duplex", self.radio_duplex.isChecked())
            self.settings.setValue("print/copies", self.spin_copies.value())
            self.settings.setValue("print/apply_all", self.chk_apply_all.isChecked())
            
        except Exception as e:
            print(f"保存设置失败: {e}")
    
    def dragEnterEvent(self, event):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()
    
    def dropEvent(self, event):
        """拖拽放下事件"""
        current_count = len(self.file_list)
        files = []
        
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if os.path.isfile(file_path):
                # 检查文件是否已存在和是否支持
                if (file_path not in [f['path'] for f in self.file_list] and 
                    Path(file_path).suffix.lower() in self.supported_extensions):
                    files.append(file_path)
            elif os.path.isdir(file_path):
                # 如果是文件夹，递归添加支持的文件
                folder_path = Path(file_path)
                for file in folder_path.rglob("*"):
                    if (file.is_file() and 
                        file.suffix.lower() in self.supported_extensions and
                        str(file) not in [f['path'] for f in self.file_list]):
                        files.append(str(file))
        
        if not files:
            self.status_bar.showMessage("没有找到新的支持文件")
            return
        
        # 检查文件数量限制
        new_files_count = len(files)
        total_count = current_count + new_files_count
        
        if total_count > 50:
            QMessageBox.warning(
                self, "文件数量限制", 
                f"不能添加拖拽的 {new_files_count} 个文件！\n\n"
                f"当前列表已有 {current_count} 个文件，\n"
                f"添加后将有 {total_count} 个文件，\n"
                f"超过了最大限制 50 个文件。\n\n"
                f"请先清空部分文件后再拖拽添加。"
            )
            return
        
        # 添加文件
        added_count = 0
        for file_path in files:
            if self.add_file_to_list(file_path):
                added_count += 1
        
        if added_count > 0:
            self.update_file_count()
            self.status_bar.showMessage(f"通过拖拽添加了 {added_count} 个文件")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止打印任务
        if self.print_worker and self.print_worker.isRunning():
            self.stop_printing()
        
        # 保存设置
        self.save_settings()
        
        event.accept()

    def apply_settings_to_all(self):
        """应用设置到所有文件"""
        if not self.file_list:
            QMessageBox.information(self, "提示", "文件列表为空")
            return
        
        # 获取统一设置区域的设置
        duplex_bool = self.radio_duplex.isChecked()
        duplex_text = "双面" if duplex_bool else "单面"
        copies = self.spin_copies.value()
        page_range = self.edit_page_range.text().strip()
        orientation_text = self.combo_orientation.currentText()
        orientation_value = 'portrait' if orientation_text == '纵向' else 'landscape'
        
        applied_count = 0
        for row in range(self.table_files.rowCount()):
            if row < len(self.file_list):
                # 更新数据
                self.file_list[row]['duplex'] = duplex_bool
                self.file_list[row]['copies'] = copies
                self.file_list[row]['page_range'] = page_range
                self.file_list[row]['orientation'] = orientation_value
                
                # 更新UI控件
                # 打印方式下拉框
                duplex_combo = self.table_files.cellWidget(row, 4)
                if duplex_combo:
                    duplex_combo.setCurrentText(duplex_text)
                
                # 份数输入框
                copies_spin = self.table_files.cellWidget(row, 5)
                if copies_spin:
                    copies_spin.setValue(copies)
                
                # 页码范围输入框
                page_range_edit = self.table_files.cellWidget(row, 6)
                if page_range_edit:
                    page_range_edit.setText(page_range)
                
                # 页面方向下拉框
                orientation_combo = self.table_files.cellWidget(row, 7)
                if orientation_combo:
                    orientation_combo.setCurrentText(orientation_text)
                
                applied_count += 1
        
        self.status_bar.showMessage(f"已将设置应用到 {applied_count} 个文件")
        QMessageBox.information(self, "应用成功", 
                               f"已将以下设置应用到所有 {applied_count} 个文件:\n"
                               f"打印方式: {duplex_text}\n"
                               f"份数: {copies}\n"
                               f"页码范围: {page_range if page_range else '全部'}\n"
                               f"页面方向: {orientation_text}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    app.setApplicationName("批量打印工具")
    app.setApplicationVersion("1.0.0")
    
    # 创建主窗口
    window = BatchPrinterGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main() 