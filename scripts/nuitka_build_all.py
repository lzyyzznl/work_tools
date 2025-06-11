#!/usr/bin/env python3
"""
统一的Nuitka构建脚本 - 适应新的项目结构
用于一次性构建所有工具的可执行文件
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


class NuitkaAllBuilder:
    """统一的Nuitka构建管理器"""

    def __init__(self):
        self.tools = {
            "batch_printer": {
                "name": "批量打印工具",
                "entry": "apps/batch_printer/gui.py",
                "icon": "apps/batch_printer/resources/打印机.ico"
            },
            "file_matcher": {
                "name": "文件名匹配工具", 
                "entry": "apps/file_matcher/gui.py",
                "icon": "apps/file_matcher/resources/icon.ico"
            },
            "file_renamer": {
                "name": "批量文件重命名工具",
                "entry": "apps/file_renamer/gui.py", 
                "icon": "apps/file_renamer/resources/icon.ico"
            }
        }
        self.output_dir = "dist"

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

    def build_single(self, tool_key):
        """构建单个应用"""
        if tool_key not in self.tools:
            logger.error(f"未知的应用: {tool_key}")
            logger.info(f"可用的应用: {', '.join(self.tools.keys())}")
            return False

        tool = self.tools[tool_key]
        logger.info(f"开始构建 {tool['name']}...")
        
        # 检查入口文件是否存在
        if not os.path.exists(tool['entry']):
            logger.error(f"入口文件不存在: {tool['entry']}")
            return False

        # 构建基本命令
        cmd = [
            sys.executable, "-m", "nuitka",
            "--onefile",                    # 单文件模式
            "--standalone",                 # 独立模式
            "--enable-plugin=pyqt5",        # PyQt5插件
            f"--output-filename={tool['name']}.exe",
            f"--output-dir={self.output_dir}",
            "--remove-output",              # 清理旧输出
        ]

        # Windows特定设置
        if os.name == "nt":
            cmd.append("--windows-console-mode=disable")  # 禁用控制台
            
            # 如果图标文件存在，添加图标
            if os.path.exists(tool['icon']):
                cmd.append(f"--windows-icon-from-ico={tool['icon']}")
                logger.info(f"使用图标: {tool['icon']}")
            else:
                logger.warning(f"图标文件不存在: {tool['icon']}")

        # 添加入口点
        cmd.append(tool['entry'])

        logger.info(f"执行命令: {' '.join(cmd)}")

        try:
            # 执行构建
            result = subprocess.run(cmd, cwd=".", check=False)
            
            if result.returncode == 0:
                exe_path = f"{self.output_dir}/{tool['name']}.exe"
                if os.path.exists(exe_path):
                    size = os.path.getsize(exe_path) / 1024 / 1024  # MB
                    logger.info(f"✅ {tool['name']} 构建成功: {exe_path} ({size:.1f} MB)")
                    return True
                else:
                    logger.error(f"❌ 构建完成但未找到输出文件: {exe_path}")
                    return False
            else:
                logger.error(f"❌ {tool['name']} 构建失败，返回码: {result.returncode}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 构建 {tool['name']} 过程异常: {e}")
            return False

    def build_all(self):
        """构建所有应用"""
        logger.info("=== 开始构建所有应用 ===")
        
        success_count = 0
        total_count = len(self.tools)
        
        for tool_key in self.tools:
            if self.build_single(tool_key):
                success_count += 1
            logger.info("-" * 60)

        logger.info(f"=== 构建完成: {success_count}/{total_count} 成功 ===")
        
        if success_count == total_count:
            logger.info("✅ 所有应用构建成功!")
        else:
            logger.warning(f"⚠️ 有 {total_count - success_count} 个应用构建失败")
        
        return success_count == total_count

    def list_apps(self):
        """列出所有可用的应用"""
        logger.info("可用的应用:")
        for key, tool in self.tools.items():
            logger.info(f"  {key}: {tool['name']}")


def main():
    parser = argparse.ArgumentParser(description="Nuitka统一构建工具 - 新项目结构")
    parser.add_argument(
        "app", 
        nargs="?", 
        choices=list(NuitkaAllBuilder().tools.keys()) + ["all"],
        help="要构建的应用名称，或使用 'all' 构建所有应用"
    )
    parser.add_argument(
        "--list", 
        action="store_true", 
        help="列出所有可用的应用"
    )

    args = parser.parse_args()
    builder = NuitkaAllBuilder()

    # 检查Nuitka
    if not args.list and not builder.check_nuitka():
        logger.error("请先安装Nuitka: pip install nuitka")
        sys.exit(1)

    if args.list:
        builder.list_apps()
        return

    if not args.app:
        logger.info("请指定要构建的应用，或使用 --help 查看帮助")
        builder.list_apps()
        return

    if args.app == "all":
        success = builder.build_all()
    else:
        success = builder.build_single(args.app)
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main() 