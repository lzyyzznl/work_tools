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


def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        logger.error("需要Python 3.8或更高版本")
        sys.exit(1)
    logger.info(f"Python版本: {platform.python_version()}")


def check_dependencies():
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


def clean_build():
    """清理构建目录"""
    for dir_name in ["build", "dist"]:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                logger.info(f"已清理目录: {dir_name}")
            except Exception as e:
                logger.error(f"清理目录 {dir_name} 失败: {e}")
                sys.exit(1)


def build_executable():
    """构建可执行文件"""
    # 获取PyQt5安装路径
    try:
        import PyQt5

        pyqt_path = os.path.dirname(os.path.dirname(PyQt5.__file__))
    except ImportError:
        pyqt_path = ""

    # PyInstaller参数
    args = [
        "pyinstaller",
        "--name=FilePrefixAdderGUI",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data=src/file_prefix_adder;file_prefix_adder",
        "--paths",
        pyqt_path,
        "--hidden-import",
        "PyQt5.QtCore",
        "--hidden-import",
        "PyQt5.QtGui",
        "--hidden-import",
        "PyQt5.QtWidgets",
        "src/file_prefix_adder/gui_qt.py",
    ]

    logger.info("开始构建可执行文件...")
    try:
        subprocess.run(args, check=True)
        logger.info("构建成功完成!")
    except subprocess.CalledProcessError as e:
        logger.error(f"构建失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    logger.info("=== 开始构建过程 ===")
    check_python_version()
    check_dependencies()
    clean_build()
    build_executable()


if __name__ == "__main__":
    main()
