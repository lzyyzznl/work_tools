import logging
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    pass

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("build.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class FileRenamerBuilder:
    """批量文件重命名工具打包类"""

    def __init__(self):
        self.app_name = "批量文件重命名工具"
        self.entry_point = "src/file_renamer/gui.py"
        self.data_files = [
            ("src/file_renamer", "file_renamer"),
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
        required = ["PyQt5", "PyInstaller"]
        missing = []

        for pkg in required:
            try:
                __import__(pkg)
            except ImportError:
                missing.append(pkg)

        if missing:
            logger.error(f"缺少依赖: {', '.join(missing)}")
            logger.info("请运行: pip install -r requirements.txt")
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

    def convert_icon_to_ico(self):
        """将PNG图标转换为ICO格式"""
        try:
            from PIL import Image

            png_path = "src/resource/icon.png"
            ico_path = "src/resource/icon.ico"

            if not os.path.exists(png_path):
                logger.warning("未找到PNG图标文件")
                return

            img = Image.open(png_path)
            img.save(ico_path)
            logger.info("已转换图标为ICO格式")
        except ImportError:
            logger.warning("未安装Pillow，无法自动转换图标格式")
        except Exception as e:
            logger.error(f"图标转换失败: {e}")

    def build_executable(self):
        """构建可执行文件"""
        # 转换图标格式
        self.convert_icon_to_ico()

        # 获取PyQt5安装路径
        try:
            import PyQt5

            pyqt_path = os.path.dirname(os.path.dirname(PyQt5.__file__))
        except ImportError:
            pyqt_path = ""

        # PyInstaller参数
        args = [
            "pyinstaller",
            f"--name={self.app_name}",
            "--onefile",
            "--windowed",
            "--noconfirm",
            "--add-data=src/file_renamer;file_renamer",
            "--add-data=src/resource;resource",
            "--collect-all",
            "PyQt5",
            "--icon=src/resource/icon.ico",
            "--paths",
            pyqt_path,
            self.entry_point,
        ]

        logger.info("开始构建可执行文件...")
        try:
            subprocess.run(args, check=True)
            logger.info("构建成功完成!")
        except subprocess.CalledProcessError as e:
            logger.error(f"构建失败: {e}")
            sys.exit(1)

    def run(self):
        """执行打包流程"""
        logger.info("=== 开始构建批量文件重命名工具 ===")
        self.check_python_version()
        self.check_dependencies()
        self.clean_build()
        self.build_executable()


if __name__ == "__main__":
    builder = FileRenamerBuilder()
    builder.run()
