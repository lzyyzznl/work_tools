#!/usr/bin/env python3
"""
文件名匹配工具 - Nuitka构建脚本
适应新的项目结构
"""

import argparse
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


class FileMatcherBuilder:
    """文件名匹配工具构建器"""

    def __init__(self, debug_mode=False):
        self.app_name = "文件名匹配工具"
        self.entry_point = "apps/file_matcher/gui.py"
        self.output_dir = "dist"
        self.icon_path = "apps/file_matcher/resources/icon.ico"
        self.debug_mode = debug_mode

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
        logger.info(f"调试模式: {'开启' if self.debug_mode else '关闭'}")

        # 构建基本命令
        cmd = [
            sys.executable, "-m", "nuitka",
            "--onefile",                    # 单文件模式
            "--standalone",                 # 独立模式
            "--enable-plugin=pyside6",       # PySide6插件
            f"--output-filename={self.app_name}.exe",
            f"--output-dir={self.output_dir}",
            "--remove-output",              # 清理旧输出
            "--include-data-dir=apps/file_matcher/resources=resources",  # 包含资源文件
            "--assume-yes-for-downloads",   # 自动下载依赖
        ]

        # Windows特定设置
        if os.name == "nt":
            if self.debug_mode:
                # 调试模式：保留控制台窗口，显示错误信息
                cmd.append("--windows-console-mode=force")
                logger.info("调试模式：启用控制台窗口")
            else:
                # 发布模式：禁用控制台
                cmd.append("--windows-console-mode=disable")
                logger.info("发布模式：禁用控制台窗口")
            
            # 如果图标文件存在，添加图标
            if os.path.exists(self.icon_path):
                cmd.append(f"--windows-icon-from-ico={self.icon_path}")
                logger.info(f"使用图标: {self.icon_path}")
            else:
                logger.warning(f"图标文件不存在: {self.icon_path}")

        # 优化选项
        if not self.debug_mode:
            cmd.extend([
                "--lto=yes",                    # 链接时优化
                "--enable-plugin=upx",          # UPX压缩（如果可用）
            ])

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
                    
                    if self.debug_mode:
                        logger.info("🐛 调试模式构建完成，exe运行时会显示控制台窗口用于调试")
                    else:
                        logger.info("🚀 发布模式构建完成，如果运行有问题请用调试模式重新构建")
                    
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
            if self.debug_mode:
                print("\n📋 下一步：")
                print("1. 运行生成的exe文件")
                print("2. 查看控制台输出的错误信息")
                print("3. 根据错误信息修复问题")
                print("4. 修复后用正常模式重新构建: python scripts/nuitka_build_file_matcher.py")
        else:
            logger.error(f"=== {self.app_name} 构建失败 ===")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="文件名匹配工具 - Nuitka构建脚本")
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="调试模式：启用控制台窗口显示错误信息"
    )
    args = parser.parse_args()
    
    builder = FileMatcherBuilder(debug_mode=args.debug)
    builder.run()


if __name__ == "__main__":
    main() 