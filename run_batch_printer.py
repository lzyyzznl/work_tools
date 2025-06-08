#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量打印工具启动脚本
运行此脚本来启动批量打印工具
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # 测试基本模块导入
    print("正在导入必要的模块...")
    
    import PyQt5
    print("✓ PyQt5 导入成功")
    
    try:
        import win32print
        print("✓ win32print 导入成功")
    except ImportError:
        print("✗ win32print 未找到，部分功能可能受限")
    
    from src.batch_printer.gui import main
    print("✓ 批量打印工具模块导入成功")
    
    if __name__ == "__main__":
        print("启动批量打印工具...")
        main()
        
except ImportError as e:
    print(f"导入错误: {e}")
    print("\n请确保已安装所需的依赖包:")
    print("1. PyQt5: pip install PyQt5")
    print("2. pywin32: pip install pywin32")
    print("\n或者运行: pip install PyQt5 pywin32")
    input("按任意键退出...")
    sys.exit(1)
except Exception as e:
    print(f"启动错误: {e}")
    input("按任意键退出...")
    sys.exit(1) 