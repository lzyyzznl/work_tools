#!/usr/bin/env python3
"""
批量打印工具 - Nuitka构建脚本
适应新的项目结构
"""

import logging
import os
import subprocess
import sys

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


class BatchPrinterBuilder:
    """批量打印工具构建器"""

    def __init__(self):
        self.app_name = "批量打印工具"
        self.entry_point = "apps/batch_printer/gui.py"
        self.output_dir = "dist"
        self.icon_path = "apps/batch_printer/resources/打印机.ico"

    def check_nuitka(self):
        """检查Nuitka是否可用"""
        try:
            result = subprocess.run([sys.executable, "-m", "nuitka", "--version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info(f"Nuitka版本: {result.stdout.strip()}")
                return True
            else:
                logger.error(f"Nuitka不可用: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"检查Nuitka失败: {e}")
            return False

    def check_entry_point(self):
        """检查入口文件是否存在"""
        if not os.path.exists(self.entry_point):
            logger.error(f"入口文件不存在: {self.entry_point}")
            return False
        logger.info(f"入口文件: {self.entry_point}")
        return True

    def build_executable(self):
        """构建可执行文件"""
        logger.info(f"开始构建 {self.app_name}...")

        # 构建基本命令
        cmd = [
            sys.executable, "-m", "nuitka",
            "--onefile",                    # 单文件模式
            "--standalone",                 # 独立模式
            "--enable-plugin=pyqt5",        # PyQt5插件
            f"--output-filename={self.app_name}.exe",
            f"--output-dir={self.output_dir}",
            "--remove-output",              # 清理旧输出
            "--include-data-dir=apps/batch_printer/resources=resources",  # 包含资源文件
        ]

        # Windows特定设置
        if os.name == "nt":
            cmd.append("--windows-console-mode=disable")  # 禁用控制台
            
            # 如果图标文件存在，添加图标
            if os.path.exists(self.icon_path):
                cmd.append(f"--windows-icon-from-ico={self.icon_path}")
                logger.info(f"使用图标: {self.icon_path}")
            else:
                logger.warning(f"图标文件不存在: {self.icon_path}")

        # 添加入口点
        cmd.append(self.entry_point)

        logger.info(f"执行命令: {' '.join(cmd)}")

        try:
            # 执行构建
            result = subprocess.run(cmd, cwd=".", check=False)
            
            if result.returncode == 0:
                exe_path = f"{self.output_dir}/{self.app_name}.exe"
                if os.path.exists(exe_path):
                    size = os.path.getsize(exe_path) / 1024 / 1024  # MB
                    logger.info(f"✅ 构建成功: {exe_path} ({size:.1f} MB)")
                    return True
                else:
                    logger.error(f"❌ 构建完成但未找到输出文件: {exe_path}")
                    return False
            else:
                logger.error(f"❌ 构建失败，返回码: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 构建过程异常: {e}")
            return False

    def run(self):
        """执行构建流程"""
        logger.info(f"=== 开始构建 {self.app_name} ===")
        
        # 检查Nuitka
        if not self.check_nuitka():
            logger.error("请先安装Nuitka: pip install nuitka")
            sys.exit(1)
        
        # 检查入口文件
        if not self.check_entry_point():
            sys.exit(1)
        
        # 构建
        if self.build_executable():
            logger.info(f"=== {self.app_name} 构建完成 ===")
        else:
            logger.error(f"=== {self.app_name} 构建失败 ===")
            sys.exit(1)


if __name__ == "__main__":
    builder = BatchPrinterBuilder()
    builder.run() 