#!/usr/bin/env python3
"""
批量打印工具 - Nuitka构建脚本
"""

import argparse
from nuitka_builder import NuitkaBuilder


def main():
    parser = argparse.ArgumentParser(description="批量打印工具 - Nuitka构建脚本")
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="调试模式：启用控制台窗口显示错误信息"
    )
    args = parser.parse_args()
    
    # 应用配置
    app_config = {
        "name": "批量打印工具",
        "exe_name": "BatchPrinterTool",
        "entry_point": "apps/batch_printer/gui.py",
        "app_dir": "apps/batch_printer",
        "icon_path": "apps/batch_printer/resources/打印机.ico"
    }
    
    builder = NuitkaBuilder(app_config, debug_mode=args.debug)
    builder.run()


if __name__ == "__main__":
    main() 