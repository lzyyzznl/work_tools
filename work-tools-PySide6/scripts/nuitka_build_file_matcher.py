#!/usr/bin/env python3
"""
文件名匹配工具 - Nuitka构建脚本
"""

import argparse
from nuitka_builder import NuitkaBuilder


def main():
    parser = argparse.ArgumentParser(description="文件名匹配工具 - Nuitka构建脚本")
    parser.add_argument(
        "--debug", 
        action="store_true", 
        help="调试模式：启用控制台窗口显示错误信息"
    )
    args = parser.parse_args()
    
    # 应用配置
    app_config = {
        "name": "文件名匹配工具",
        "exe_name": "FileMatcherTool",
        "entry_point": "apps/file_matcher/gui.py",
        "app_dir": "apps/file_matcher",
        "icon_path": "apps/file_matcher/resources/icon.ico"
    }
    
    builder = NuitkaBuilder(app_config, debug_mode=args.debug)
    builder.run()


if __name__ == "__main__":
    main() 