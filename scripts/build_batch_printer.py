import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("build.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class BatchPrinterBuilder:
    """批量打印工具打包类"""

    def __init__(self):
        self.app_name = "批量打印工具"
        self.entry_point = "src/batch_printer/gui.py"
        self.data_files = [
            ("src/batch_printer", "batch_printer"),
            ("src/resource", "resource"),
        ]

    def check_python_version(self):
        """检查Python版本"""
        if sys.version_info < (3, 8):
            logger.error("需要Python 3.8或更高版本")
            sys.exit(1)
        logger.info(f"Python版本: {platform.python_version()}")

    def check_dependencies(self):
        """检查必要依赖"""
        required = ["PyQt5", "PyInstaller", "win32print", "win32api"]
        missing = []

        for pkg in required:
            try:
                if pkg in ["win32print", "win32api"]:
                    # 这些是pywin32包的子模块
                    __import__(pkg)
                else:
                    __import__(pkg)
            except ImportError:
                if pkg in ["win32print", "win32api"]:
                    missing.append("pywin32")
                else:
                    missing.append(pkg)

        # 去重
        missing = list(set(missing))

        if missing:
            logger.error(f"缺少依赖: {', '.join(missing)}")
            logger.info("请运行: pip install PyQt5 pyinstaller pywin32")
            sys.exit(1)

        logger.info("所有依赖已安装")

    def clean_build(self):
        """清理构建目录"""
        for dir_name in ["build", "dist"]:
            if os.path.exists(dir_name):
                try:
                    shutil.rmtree(dir_name)
                    logger.info(f"已清理目录: {dir_name}")
                except Exception as e:
                    logger.error(f"清理目录 {dir_name} 失败: {e}")
                    sys.exit(1)

    def verify_icon(self):
        """验证图标文件是否存在"""
        ico_path = "src/resource/打印机.ico"
        png_path = "src/resource/打印机.png"
        
        if os.path.exists(ico_path):
            logger.info(f"找到ICO图标文件: {ico_path}")
            return ico_path
        elif os.path.exists(png_path):
            logger.info(f"找到PNG图标文件: {png_path}，尝试转换为ICO格式")
            return self.convert_icon_to_ico()
        else:
            logger.warning("未找到图标文件")
            return None

    def convert_icon_to_ico(self):
        """将PNG图标转换为ICO格式"""
        try:
            from PIL import Image

            png_path = "src/resource/打印机.png"
            ico_path = "src/resource/打印机.ico"

            if not os.path.exists(png_path):
                logger.warning("未找到PNG图标文件")
                return None

            img = Image.open(png_path)
            # 确保图标是正方形，并调整为标准ICO尺寸
            img = img.resize((256, 256), Image.Resampling.LANCZOS)
            img.save(ico_path, format='ICO', sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)])
            logger.info("已转换图标为ICO格式")
            return ico_path
        except ImportError:
            logger.warning("未安装Pillow，无法自动转换图标格式")
            return None
        except Exception as e:
            logger.error(f"图标转换失败: {e}")
            return None

    def build_executable(self):
        """构建可执行文件"""
        # 验证和准备图标文件
        icon_path = self.verify_icon()

        # 获取PyQt5安装路径
        try:
            import PyQt5

            pyqt_path = os.path.dirname(os.path.dirname(PyQt5.__file__))
        except ImportError:
            pyqt_path = ""

        # 优化的PyInstaller参数，确保单文件打包稳定性
        args = [
            "pyinstaller",
            f"--name={self.app_name}",
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--clean",
            "--noupx",  # 禁用UPX压缩避免问题
            "--optimize=2",  # Python字节码优化
        ]
        
        # 只有在图标文件存在时才添加图标参数
        if icon_path and os.path.exists(icon_path):
            args.append(f"--icon={icon_path}")
            logger.info(f"使用图标文件: {icon_path}")
        else:
            logger.warning("未设置图标文件")
        
        # 继续添加其他参数
        args.extend([
            # 基本的Windows API导入
            "--hidden-import=win32print",
            "--hidden-import=win32api",
            "--hidden-import=win32con",
            "--hidden-import=pywintypes",
            "--hidden-import=win32com.client",
            "--hidden-import=pythoncom",
            # PyQt5最小化导入
            "--hidden-import=PyQt5.sip",
            # 排除不需要的大型模块
            "--exclude-module=matplotlib",
            "--exclude-module=numpy", 
            "--exclude-module=scipy",
            "--exclude-module=pandas",
            "--exclude-module=PIL",
            "--exclude-module=tkinter",
            "--exclude-module=sqlite3",
            "--exclude-module=distutils",
            "--exclude-module=email",
            "--exclude-module=http",
            "--exclude-module=urllib3",
            "--exclude-module=xml",
            # 排除PyQt5的3D和Web相关模块
            "--exclude-module=PyQt5.Qt3DAnimation",
            "--exclude-module=PyQt5.Qt3DCore",
            "--exclude-module=PyQt5.Qt3DExtras", 
            "--exclude-module=PyQt5.Qt3DInput",
            "--exclude-module=PyQt5.Qt3DLogic",
            "--exclude-module=PyQt5.Qt3DRender",
            "--exclude-module=PyQt5.QtWebEngine",
            "--exclude-module=PyQt5.QtWebEngineCore",
            "--exclude-module=PyQt5.QtWebEngineWidgets",
            "--exclude-module=PyQt5.QtWebKit",
            "--exclude-module=PyQt5.QtWebKitWidgets",
            "--exclude-module=PyQt5.QtQuick",
            "--exclude-module=PyQt5.QtQuick3D",
            "--exclude-module=PyQt5.QtQml",
            "--exclude-module=PyQt5.QtDesigner",
            "--exclude-module=PyQt5.QtHelp",
            "--exclude-module=PyQt5.QtMultimedia",
            "--exclude-module=PyQt5.QtLocation",
            "--exclude-module=PyQt5.QtPositioning",
        ])

        # 添加数据文件
        for src, dest in self.data_files:
            args.extend(["--add-data", f"{src};{dest}"])

        # 添加其他参数
        args.extend(
            [
                "--paths",
                pyqt_path,
                self.entry_point,
            ]
        )

        logger.info("开始构建可执行文件...")
        logger.info(f"构建命令: {' '.join(args)}")
        
        try:
            subprocess.run(args, check=True)
            logger.info("构建成功完成!")
            
            # 检查生成的文件
            exe_path = f"dist/{self.app_name}.exe"
            if os.path.exists(exe_path):
                size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
                logger.info(f"生成的可执行文件: {exe_path} ({size:.1f} MB)")
            else:
                logger.warning("未找到生成的可执行文件")
                
        except subprocess.CalledProcessError as e:
            logger.error(f"构建失败: {e}")
            sys.exit(1)

    def run(self):
        """执行打包流程"""
        logger.info("=== 开始构建批量打印工具 ===")
        self.check_python_version()
        self.check_dependencies()
        self.clean_build()
        self.build_executable()
        logger.info("=== 构建完成 ===")


if __name__ == "__main__":
    builder = BatchPrinterBuilder()
    builder.run() 